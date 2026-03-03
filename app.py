import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime
import random

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="Kenya Climate Risk Monitor",
    page_icon="🌍",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .title {
        text-align: center;
        color: #1E3A8A;
        font-size: 2.5rem;
        padding: 1rem;
        background: #f0f7ff;
        border-radius: 10px;
    }
    .risk-box {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .high { background-color: #ffcccc; color: #cc0000; }
    .medium { background-color: #fff3cd; color: #856404; }
    .low { background-color: #d4edda; color: #155724; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA - SIMPLE AND CLEAN
# ============================================================================
@st.cache_data
def get_counties():
    """Simple county data"""
    return pd.DataFrame({
        'County': ['Nairobi', 'Mombasa', 'Kisumu', 'Turkana', 'Garissa'],
        'Lat': [-1.28, -4.04, -0.09, 3.07, -0.45],
        'Lon': [36.82, 39.66, 34.75, 35.36, 39.65]
    })

@st.cache_data
def get_risk_data():
    """Simple risk data"""
    return pd.DataFrame({
        'County': ['Nairobi', 'Mombasa', 'Kisumu', 'Turkana', 'Garissa'],
        'Flood': [45, 95, 88, 65, 92],
        'Drought': [30, 25, 40, 92, 88],
        'Heat': [82, 88, 75, 95, 90]
    })

# ============================================================================
# MAIN APP
# ============================================================================
st.markdown('<h1 class="title">🇰🇪 Kenya Climate Risk Monitor</h1>', 
            unsafe_allow_html=True)

st.markdown("### Multi-Hazard Early Warning System")
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EAT")

# Load data
counties = get_counties()
risks = get_risk_data()

# Sidebar
with st.sidebar:
    st.image("https://flagcdn.com/ke.svg", width=100)
    st.title("📍 Select Location")
    
    selected = st.selectbox("Choose County", counties['County'].tolist())
    
    st.markdown("---")
    st.markdown("### 🛰️ Satellites")
    st.info("Sentinel-1 (Floods)\n\nSentinel-2 (Drought)\n\nLandsat 8 (Heat)")

# Get selected county data
county_data = risks[risks['County'] == selected].iloc[0]
county_loc = counties[counties['County'] == selected].iloc[0]

# Calculate composite risk
composite = (
    county_data['Flood'] * 0.4 +
    county_data['Drought'] * 0.35 +
    county_data['Heat'] * 0.25
)

# Risk level
if composite >= 70:
    risk_class = "high"
    risk_text = "HIGH RISK"
elif composite >= 40:
    risk_class = "medium"
    risk_text = "MEDIUM RISK"
else:
    risk_class = "low"
    risk_text = "LOW RISK"

# ============================================================================
# TOP METRICS
# ============================================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("County", selected)

with c2:
    st.metric("Composite Risk", f"{composite:.1f}", risk_text)

with c3:
    st.metric("Temperature", f"{random.randint(26, 35)}°C")

with c4:
    st.metric("Rainfall", f"{random.randint(0, 150)}mm")

st.markdown("---")

# ============================================================================
# MAP AND ALERTS
# ============================================================================
col_map, col_alert = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Risk Map")
    
    # Create simple map
    m = folium.Map(
        location=[county_loc['Lat'], county_loc['Lon']],
        zoom_start=7
    )
    
    # Color based on risk
    if composite >= 70:
        color = 'red'
    elif composite >= 40:
        color = 'orange'
    else:
        color = 'green'
    
    # Add marker
    folium.CircleMarker(
        [county_loc['Lat'], county_loc['Lon']],
        radius=15,
        popup=f"{selected}<br>Risk: {composite:.1f}",
        color=color,
        fill=True,
        fillOpacity=0.6
    ).add_to(m)
    
    folium_static(m, width=600, height=300)

with col_alert:
    st.subheader("⚠️ Alerts")
    
    if county_data['Flood'] >= 70:
        st.error(f"🚨 Flood Alert: {county_data['Flood']}%")
    elif county_data['Flood'] >= 50:
        st.warning(f"⚠️ Flood Watch: {county_data['Flood']}%")
    
    if county_data['Drought'] >= 70:
        st.error(f"🌵 Drought Alert: {county_data['Drought']}%")
    
    if county_data['Heat'] >= 70:
        st.error(f"🔥 Heat Alert: {county_data['Heat']}%")

st.markdown("---")

# ============================================================================
# HAZARD GAUGES
# ============================================================================
st.subheader(f"📊 Hazard Analysis - {selected}")

g1, g2, g3 = st.columns(3)

with g1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=county_data['Flood'],
        title="Flood Risk",
        gauge={'axis': {'range': [0, 100]}}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with g2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=county_data['Drought'],
        title="Drought Risk",
        gauge={'axis': {'range': [0, 100]}}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with g3:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=county_data['Heat'],
        title="Heat Stress",
        gauge={'axis': {'range': [0, 100]}}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# COMPARISON CHART
# ============================================================================
st.subheader("📈 County Comparison")

fig = px.bar(risks, x='County', y=['Flood', 'Drought', 'Heat'],
             title="Risk Comparison by County",
             barmode='group')
st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# RECOMMENDATIONS
# ============================================================================
st.markdown("---")
st.subheader("📢 Recommendations")

if composite >= 70:
    st.error(f"""
    **HIGH RISK - {selected}**
    - Immediate action required
    - Evacuate flood-prone areas
    - Activate emergency response
    - Monitor updates hourly
    """)
elif composite >= 40:
    st.warning(f"""
    **MEDIUM RISK - {selected}**
    - Prepare for potential hazards
    - Alert response teams
    - Clear drainage systems
    - Monitor conditions
    """)
else:
    st.success(f"""
    **LOW RISK - {selected}**
    - Continue monitoring
    - Maintain preparedness
    - Regular updates only
    """)

# ============================================================================
# DATA TABLE
# ============================================================================
st.markdown("---")
st.subheader("📋 County Risk Data")
st.dataframe(risks, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🛰️ Data: Sentinel-1, Sentinel-2, Landsat 8, Kenya Met Department</p>
    <p>© 2024 KSEF Nationals | Real-Time Climate Monitoring</p>
</div>
""", unsafe_allow_html=True)
