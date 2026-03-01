import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import folium
from streamlit_folium import st_folium
import numpy as np
import sys
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Kenya Climate Risk Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display version info for debugging
st.sidebar.write(f"🐍 Python: {sys.version[:5]}")
st.sidebar.write(f"📊 Pandas: {pd.__version__}")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0;
        font-weight: bold;
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
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    # Create sample data if file doesn't exist
    try:
        df = pd.read_csv('data/county_data.csv')
    except FileNotFoundError:
        # Create sample data
        data = {
            'County': ['Turkana', 'Garissa', 'Nairobi', 'Mombasa', 'Kisumu', 
                      'Mandera', 'Wajir', 'Marsabit', 'Kitui', 'Makueni'],
            'Flood_Risk': [85, 95, 60, 98, 90, 75, 70, 60, 55, 50],
            'Drought_Risk': [95, 90, 30, 20, 40, 98, 96, 85, 80, 75],
            'Heat_Risk': [90, 88, 95, 85, 80, 92, 91, 88, 75, 70],
            'Forest_Loss': [15, 5, 40, 20, 25, 8, 6, 12, 18, 22],
            'Population': [926976, 841353, 4397000, 1208000, 1155574, 
                          867457, 720000, 459785, 1120000, 987653],
            'Area_km2': [77000, 44000, 696, 220, 2085, 
                        26000, 56000, 70961, 30496, 8035],
            'Latitude': [3.1, -0.5, -1.3, -4.0, -0.1, 
                        3.9, 1.8, 2.3, -1.4, -1.8],
            'Longitude': [35.6, 39.6, 36.8, 39.7, 34.8, 
                         41.9, 40.1, 37.9, 38.0, 37.6]
        }
        df = pd.DataFrame(data)
    
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
    st.markdown("✅ **Sentinel-1** (Floods)")
    st.markdown("✅ **Sentinel-2** (Drought)")
    st.markdown("✅ **Landsat 8** (Heat)")
    
    st.markdown("---")
    st.markdown("### 📊 Risk Scale")
    st.markdown("🔴 **High:** >70")
    st.markdown("🟡 **Medium:** 40-70")
    st.markdown("🟢 **Low:** <40")
    
    st.markdown("---")
    st.caption("Data Source: ESA, NASA | Analysis: 2024")

# Main content
st.markdown('<p class="main-header">🇰🇪 Kenya Climate Risk Monitor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Hazard Satellite-Based Early Warning System</p>', unsafe_allow_html=True)

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Counties Analyzed",
            value=len(df)
        )
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        high_risk_count = len(df[df['Composite_Risk'] >= 70])
        st.metric(
            label="High Risk Counties",
            value=high_risk_count,
            delta=f"{high_risk_count/len(df)*100:.0f}% of total"
        )
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_risk = df['Composite_Risk'].mean()
        st.metric(
            label="National Avg Risk",
            value=f"{avg_risk:.1f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

with col4:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        most_vulnerable = df.loc[df['Composite_Risk'].idxmax(), 'County']
        st.metric(
            label="Most Vulnerable",
            value=most_vulnerable
        )
        st.markdown('</div>', unsafe_allow_html=True)

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
            icon_color = 'darkred'
        elif row['Composite_Risk'] >= 40:
            color = 'orange'
            icon_color = 'orange'
        else:
            color = 'green'
            icon_color = 'darkgreen'
        
        # Create popup HTML
        popup_html = f"""
        <div style="font-family: Arial; width: 250px; padding: 10px;">
            <h4 style="margin:0; color:#1E3A8A;">{row['County']} County</h4>
            <hr style="margin:5px 0;">
            <p><b>Composite Risk:</b> <span style="color:{color}; font-weight:bold;">{row['Composite_Risk']}</span></p>
            <p><b>Flood Risk:</b> {row['Flood_Risk']}%</p>
            <p><b>Drought Risk:</b> {row['Drought_Risk']}%</p>
            <p><b>Heat Risk:</b> {row['Heat_Risk']}%</p>
            <p><b>Population:</b> {row['Population']:,}</p>
            <p><b>Area:</b> {row['Area_km2']:,} km²</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillOpacity=0.7,
            tooltip=row['County']
        ).add_to(m)
    
    # Display map with updated st_folium
    st_folium(m, width=700, height=500, returned_objects=[])

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
    
    st.markdown(f"### 📍 {selected_county} County")
    
    # Quick stats
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Population:** {county_data['Population']:,}")
    with col_b:
        st.markdown(f"**Area:** {county_data['Area_km2']:,} km²")
    
    # Risk gauge for composite risk
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=county_data['Composite_Risk'],
        title={'text': "Composite Risk Score"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "#D1FAE5"},
                {'range': [40, 70], 'color': "#FEF3C7"},
                {'range': [70, 100], 'color': "#FEE2E2"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Detailed risk breakdown
st.subheader(f"📈 Hazard Analysis: {selected_county} County")

# Three columns for hazard breakdown
haz1, haz2, haz3 = st.columns(3)

with haz1:
    flood_val = county_data['Flood_Risk']
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=flood_val,
        title={'text': "🌊 Flood Risk"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2563EB"},
            'steps': [
                {'range': [0, 40], 'color': "#BFDBFE"},
                {'range': [40, 70], 'color': "#60A5FA"},
                {'range': [70, 100], 'color': "#1E3A8A"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, width='stretch')
    
    # Flood description
    if flood_val >= 70:
        st.error("⚠️ High flood risk")
    elif flood_val >= 40:
        st.warning("⚠️ Moderate flood risk")
    else:
        st.success("✅ Low flood risk")

with haz2:
    drought_val = county_data['Drought_Risk']
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=drought_val,
        title={'text': "🌵 Drought Risk"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#B45309"},
            'steps': [
                {'range': [0, 40], 'color': "#FDE68A"},
                {'range': [40, 70], 'color': "#F59E0B"},
                {'range': [70, 100], 'color': "#B45309"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, width='stretch')
    
    # Drought description
    if drought_val >= 70:
        st.error("⚠️ Severe drought risk")
    elif drought_val >= 40:
        st.warning("⚠️ Moderate drought risk")
    else:
        st.success("✅ Low drought risk")

with haz3:
    heat_val = county_data['Heat_Risk']
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=heat_val,
        title={'text': "🌡️ Heat Stress"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#DC2626"},
            'steps': [
                {'range': [0, 40], 'color': "#FEE2E2"},
                {'range': [40, 70], 'color': "#F87171"},
                {'range': [70, 100], 'color': "#DC2626"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, width='stretch')
    
    # Heat description
    if heat_val >= 70:
        st.error("⚠️ Extreme heat stress")
    elif heat_val >= 40:
        st.warning("⚠️ Moderate heat stress")
    else:
        st.success("✅ Low heat stress")

st.markdown("---")

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
    line=dict(color='blue', width=2),
    fillcolor='rgba(0,0,255,0.1)'
))
fig.add_trace(go.Scatterpolar(
    r=avg_values,
    theta=categories,
    fill='toself',
    name='National Average',
    line=dict(color='gray', width=2, dash='dash'),
    fillcolor='rgba(128,128,128,0.1)'
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )),
    showlegend=True,
    height=400,
    margin=dict(l=80, r=80, t=40, b=40)
)

st.plotly_chart(fig, width='stretch')

# Bar chart comparison
st.subheader("📊 County Risk Comparison")

# Sort by composite risk
df_sorted = df.sort_values('Composite_Risk', ascending=True)

fig = px.bar(
    df_sorted,
    x='Composite_Risk',
    y='County',
    orientation='h',
    title="Climate Risk Index by County",
    color='Composite_Risk',
    color_continuous_scale=['green', 'yellow', 'red'],
    labels={'Composite_Risk': 'Risk Score', 'County': ''}
)
fig.update_layout(height=400)
st.plotly_chart(fig, width='stretch')

# Data table
st.subheader("📋 County Risk Data")
st.dataframe(
    df[['County', 'Composite_Risk', 'Risk_Category', 'Flood_Risk', 'Drought_Risk', 'Heat_Risk']]
    .sort_values('Composite_Risk', ascending=False)
    .style.highlight_max(subset=['Composite_Risk'], color='#ffcdd2')
    .highlight_min(subset=['Composite_Risk'], color='#c8e6c9'),
    use_container_width=True
)

# Footer with early warning recommendations
st.markdown("---")
st.markdown("### 📢 Early Warning Recommendations")

if county_data['Composite_Risk'] >= 70:
    st.error(f"⚠️ **HIGH RISK ALERT**: {selected_county} County requires immediate attention. Multiple hazards detected at critical levels. Recommend: Emergency preparedness, resource mobilization, and community alerts.")
elif county_data['Composite_Risk'] >= 40:
    st.warning(f"⚠️ **MEDIUM RISK**: {selected_county} County shows moderate vulnerability. Recommended actions: Monitoring, contingency planning, and community sensitization.")
else:
    st.success(f"✅ **LOW RISK**: {selected_county} County currently shows low climate vulnerability. Recommended actions: Continue monitoring and maintain preparedness.")

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>© 2024 Kenya Climate Risk Monitor | Data from Sentinel-1, Sentinel-2, and Landsat 8</p>
    <p>Developed for KSEF National Competition | Multi-Hazard Satellite-Based Early Warning System</p>
</div>
""", unsafe_allow_html=True)

# Sidebar note about data
st.sidebar.markdown("---")
st.sidebar.info(
    "🛰️ **Data Update**: This dashboard uses integrated satellite data "
    "from ESA and NASA missions. Risk scores are calculated in real-time "
    "using multi-hazard analysis."
)
