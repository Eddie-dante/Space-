import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Kenya Climate Risk Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .risk-card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .high-risk {
        background-color: #FEE2E2;
        border-left: 5px solid #DC2626;
    }
    .medium-risk {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
    }
    .low-risk {
        background-color: #D1FAE5;
        border-left: 5px solid #10B981;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/county_data.csv')
    # Calculate composite risk
    df['Composite_Risk'] = (
        df['Flood_Risk'] * 0.4 +
        df['Drought_Risk'] * 0.3 +
        df['Heat_Risk'] * 0.3
    ).round(1)
   
    # Add risk category
    def categorize_risk(score):
        if score >= 70:
            return 'High Risk 🔴'
        elif score >= 40:
            return 'Medium Risk 🟡'
        else:
            return 'Low Risk 🟢'
   
    df['Risk_Category'] = df['Composite_Risk'].apply(categorize_risk)
    return df

df = load_data()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/45/Flag_of_Kenya.svg", width=100)
    st.title("🌍 Kenya Climate Risk Monitor")
    st.markdown("---")
   
    # County selector
    selected_county = st.selectbox(
        "Select County",
        df['County'].tolist()
    )
   
    # Year selector (for future expansion)
    year = st.slider("Select Year", 2020, 2025, 2024)
   
    st.markdown("---")
    st.markdown("### 🛰️ Satellites Used")
    st.markdown("✅ Sentinel-1 (Floods)")
    st.markdown("✅ Sentinel-2 (Drought)")
    st.markdown("✅ Landsat 8 (Heat)")
   
    st.markdown("---")
    st.caption("Data Source: ESA, NASA | Analysis: 2024")

# Main content
st.markdown('<p class="main-header">🇰🇪 Kenya Climate Risk Monitor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Hazard Satellite-Based Early Warning System</p>', unsafe_allow_html=True)

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Counties Analyzed",
        value=len(df),
        delta="10"
    )

with col2:
    high_risk_count = len(df[df['Composite_Risk'] >= 70])
    st.metric(
        label="High Risk Counties",
        value=high_risk_count,
        delta=f"{high_risk_count/len(df)*100:.0f}% of total",
        delta_color="inverse"
    )

with col3:
    avg_risk = df['Composite_Risk'].mean()
    st.metric(
        label="National Avg Risk",
        value=f"{avg_risk:.1f}",
        delta="Moderate"
    )

with col4:
    most_vulnerable = df.loc[df['Composite_Risk'].idxmax(), 'County']
    st.metric(
        label="Most Vulnerable",
        value=most_vulnerable,
        delta="High Risk"
    )

st.markdown("---")

# Two columns for map and data
map_col, data_col = st.columns([2, 1])

with map_col:
    st.subheader("🗺️ Climate Risk Map of Kenya")
   
    # Create base map
    m = folium.Map(location=[0.5, 38.0], zoom_start=6)
   
    # Add county markers
    for idx, row in df.iterrows():
        # Determine color based on risk
        if row['Composite_Risk'] >= 70:
            color = 'red'
        elif row['Composite_Risk'] >= 40:
            color = 'orange'
        else:
            color = 'green'
       
        # Create popup HTML
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin:0; color:#1E3A8A;">{row['County']} County</h4>
            <hr>
            <p><b>Composite Risk:</b> {row['Composite_Risk']}</p>
            <p><b>Flood Risk:</b> {row['Flood_Risk']}%</p>
            <p><b>Drought Risk:</b> {row['Drought_Risk']}%</p>
            <p><b>Heat Risk:</b> {row['Heat_Risk']}%</p>
            <p><b>Population:</b> {row['Population']:,}</p>
        </div>
        """
       
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillOpacity=0.7
        ).add_to(m)
   
    # Display map
    folium_static(m, width=700, height=500)

with data_col:
    st.subheader("📊 Risk Rankings")
   
    # Show top 5 highest risk counties
    st.markdown("**Top 5 High Risk Counties**")
    top_5 = df.nlargest(5, 'Composite_Risk')[['County', 'Composite_Risk', 'Risk_Category']]
   
    for i, row in top_5.iterrows():
        if 'High' in row['Risk_Category']:
            st.markdown(f"🔴 **{row['County']}** - {row['Composite_Risk']}")
        elif 'Medium' in row['Risk_Category']:
            st.markdown(f"🟡 **{row['County']}** - {row['Composite_Risk']}")
   
    st.markdown("---")
   
    # Show selected county details
    county_data = df[df['County'] == selected_county].iloc[0]
   
    st.markdown(f"### 📍 {selected_county} County Details")
   
    # Risk gauge for composite risk
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = county_data['Composite_Risk'],
        title = {'text': "Composite Risk Score"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightgreen"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "red"}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Detailed risk breakdown
st.subheader(f"📈 Detailed Risk Analysis: {selected_county} County")

# Three columns for hazard breakdown
haz1, haz2, haz3 = st.columns(3)

with haz1:
    flood_val = county_data['Flood_Risk']
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = flood_val,
        title = {'text': "Flood Risk"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2563EB"},
            'steps': [
                {'range': [0, 40], 'color': "#BFDBFE"},
                {'range': [40, 70], 'color': "#60A5FA"},
                {'range': [70, 100], 'color': "#1E3A8A"}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with haz2:
    drought_val = county_data['Drought_Risk']
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = drought_val,
        title = {'text': "Drought Risk"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#B45309"},
            'steps': [
                {'range': [0, 40], 'color': "#FDE68A"},
                {'range': [40, 70], 'color': "#F59E0B"},
                {'range': [70, 100], 'color': "#B45309"}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with haz3:
    heat_val = county_data['Heat_Risk']
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = heat_val,
        title = {'text': "Heat Stress"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#DC2626"},
            'steps': [
                {'range': [0, 40], 'color': "#FEE2E2"},
                {'range': [40, 70], 'color': "#F87171"},
                {'range': [70, 100], 'color': "#DC2626"}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

# Radar chart for comparison
st.subheader("🔄 Multi-Hazard Comparison")

# Prepare data for radar chart
categories = ['Flood Risk', 'Drought Risk', 'Heat Risk', 'Forest Loss']
selected_values = [
    county_data['Flood_Risk'],
    county_data['Drought_Risk'],
    county_data['Heat_Risk'],
    county_data['Forest_Loss']
]

# Add national average for comparison
avg_values = [
    df['Flood_Risk'].mean(),
    df['Drought_Risk'].mean(),
    df['Heat_Risk'].mean(),
    df['Forest_Loss'].mean()
]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=selected_values,
    theta=categories,
    fill='toself',
    name=selected_county,
    line_color='blue'
))
fig.add_trace(go.Scatterpolar(
    r=avg_values,
    theta=categories,
    fill='toself',
    name='National Average',
    line_color='gray',
    opacity=0.5
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )),
    showlegend=True,
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("### 📢 Early Warning Recommendations")

if county_data['Composite_Risk'] >= 70:
    st.error(f"⚠️ **HIGH RISK ALERT**: {selected_county} County requires immediate attention. Multiple hazards detected at critical levels.")
elif county_data['Composite_Risk'] >= 40:
    st.warning(f"⚠️ **MEDIUM RISK**: {selected_county} County shows moderate vulnerability. Preparedness measures recommended.")
else:
    st.success(f"✅ **LOW RISK**: {selected_county} County currently shows low climate vulnerability. Continue monitoring.")

st.markdown("---")
st.caption("© 2024 Kenya Climate Risk Monitor | Data from Sentinel-1, Sentinel-2, and Landsat 8")
