import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Kenya Climate Risk Monitor",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; text-align: center; }
    .risk-high { color: red; font-weight: bold; }
    .risk-medium { color: orange; font-weight: bold; }
    .risk-low { color: green; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# CREATE DATA DIRECTLY IN THE APP (NO FILE NEEDED)
@st.cache_data
def create_data():
    data = {
        'County': ['Turkana', 'Garissa', 'Nairobi', 'Mombasa', 'Kisumu', 
                  'Mandera', 'Wajir', 'Marsabit', 'Kitui', 'Makueni',
                  'Kilifi', 'Kwale', 'Lamu', 'Tana River', 'Samburu'],
        'Flood_Risk': [85, 95, 60, 98, 90, 75, 70, 60, 55, 50, 88, 82, 92, 96, 45],
        'Drought_Risk': [95, 90, 30, 20, 40, 98, 96, 85, 80, 75, 35, 40, 25, 60, 88],
        'Heat_Risk': [90, 88, 95, 85, 80, 92, 91, 88, 75, 70, 82, 78, 72, 75, 84],
        'Latitude': [3.1, -0.5, -1.3, -4.0, -0.1, 3.9, 1.8, 2.3, -1.4, -1.8, 
                    -3.5, -4.2, -2.3, -1.5, 1.5],
        'Longitude': [35.6, 39.6, 36.8, 39.7, 34.8, 41.9, 40.1, 37.9, 38.0, 37.6,
                     39.8, 39.5, 40.9, 40.0, 36.9]
    }
    df = pd.DataFrame(data)
    
    # Calculate composite risk
    df['Composite_Risk'] = (
        df['Flood_Risk'] * 0.4 + 
        df['Drought_Risk'] * 0.3 + 
        df['Heat_Risk'] * 0.3
    ).round(1)
    
    # Add risk category
    df['Risk_Category'] = df['Composite_Risk'].apply(
        lambda x: 'HIGH' if x >= 70 else ('MEDIUM' if x >= 40 else 'LOW')
    )
    
    return df

# Load data
df = create_data()

# Sidebar
with st.sidebar:
    st.image("https://flagcdn.com/ke.svg", width=100)
    st.title("🌍 Climate Risk Monitor")
    st.markdown("---")
    
    selected_county = st.selectbox("Select County", df['County'].tolist())
    
    st.markdown("### 🛰️ Satellites")
    st.info("Sentinel-1 (Floods)\n\nSentinel-2 (Drought)\n\nLandsat 8 (Heat)")
    
    st.markdown("---")
    st.caption("© 2024 KSEF Project")

# Main content
st.markdown('<p class="main-header">🇰🇪 KENYA CLIMATE RISK MONITOR</p>', 
            unsafe_allow_html=True)
st.markdown("### Multi-Hazard Satellite-Based Early Warning System")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Counties", len(df))
with col2:
    high_risk = len(df[df['Composite_Risk'] >= 70])
    st.metric("High Risk", high_risk)
with col3:
    st.metric("National Avg Risk", f"{df['Composite_Risk'].mean():.1f}")
with col4:
    most_vuln = df.loc[df['Composite_Risk'].idxmax(), 'County']
    st.metric("Most Vulnerable", most_vuln)

st.markdown("---")

# Map and data side by side
col_map, col_data = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Risk Map")
    
    # Create map
    m = folium.Map(location=[0.5, 38.0], zoom_start=5.5)
    
    for _, row in df.iterrows():
        if row['Composite_Risk'] >= 70:
            color = 'red'
        elif row['Composite_Risk'] >= 40:
            color = 'orange'
        else:
            color = 'green'
            
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            popup=f"{row['County']}: {row['Composite_Risk']}",
            color=color,
            fill=True,
            fillOpacity=0.7
        ).add_to(m)
    
    st_folium(m, width=600, height=400)

with col_data:
    st.subheader("📊 Risk Rankings")
    top_5 = df.nlargest(5, 'Composite_Risk')[['County', 'Composite_Risk']]
    for _, row in top_5.iterrows():
        st.write(f"• **{row['County']}**: {row['Composite_Risk']}")

# Selected county details
st.markdown("---")
st.subheader(f"📍 {selected_county} County Analysis")

county_data = df[df['County'] == selected_county].iloc[0]

# Three gauges
g1, g2, g3 = st.columns(3)

with g1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=county_data['Flood_Risk'],
        title="Flood Risk",
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': 'blue'}}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with g2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=county_data['Drought_Risk'],
        title="Drought Risk",
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': 'brown'}}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with g3:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=county_data['Heat_Risk'],
        title="Heat Risk",
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': 'red'}}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

# Risk summary
st.markdown("---")
col_risk, col_rec = st.columns(2)

with col_risk:
    st.subheader("🎯 Composite Risk")
    risk = county_data['Composite_Risk']
    if risk >= 70:
        st.error(f"**HIGH RISK**: {risk}")
    elif risk >= 40:
        st.warning(f"**MEDIUM RISK**: {risk}")
    else:
        st.success(f"**LOW RISK**: {risk}")

with col_rec:
    st.subheader("📢 Recommendations")
    if risk >= 70:
        st.error("Immediate action required! Multiple hazards detected.")
    elif risk >= 40:
        st.warning("Prepare mitigation measures. Monitor closely.")
    else:
        st.success("Continue monitoring. Low vulnerability.")

# Bar chart
st.markdown("---")
st.subheader("📈 County Comparison")
fig = px.bar(df.sort_values('Composite_Risk'), 
             x='County', y='Composite_Risk',
             color='Composite_Risk',
             color_continuous_scale=['green', 'yellow', 'red'])
st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Data: Sentinel-1, Sentinel-2, Landsat 8 | KSEF Nationals 2024")
