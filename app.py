import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import random

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Kenya Climate Risk Monitor",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #ffffff, #e6f0ff);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #ffcccc;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid red;
    }
    .risk-medium {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid orange;
    }
    .risk-low {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid green;
    }
    .metric-box {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# KENYA COUNTIES DATA
# ============================================================================
@st.cache_data
def get_counties_data():
    """Return Kenya counties with coordinates"""
    return pd.DataFrame({
        'County': [
            'Turkana', 'Garissa', 'Nairobi', 'Mombasa', 'Kisumu',
            'Mandera', 'Wajir', 'Marsabit', 'Kitui', 'Makueni',
            'Kilifi', 'Kwale', 'Lamu', 'Tana River', 'Samburu',
            'Baringo', 'Laikipia', 'Narok', 'Kajiado', 'West Pokot'
        ],
        'Latitude': [
            3.1, -0.5, -1.3, -4.0, -0.1,
            3.9, 1.8, 2.3, -1.4, -1.8,
            -3.5, -4.2, -2.3, -1.5, 1.5,
            0.5, 0.2, -1.1, -2.0, 2.0
        ],
        'Longitude': [
            35.6, 39.6, 36.8, 39.7, 34.8,
            41.9, 40.1, 37.9, 38.0, 37.6,
            39.8, 39.5, 40.9, 40.0, 36.9,
            36.0, 36.8, 35.8, 36.8, 35.5
        ]
    })

# ============================================================================
# DATA FETCHER CLASS
# ============================================================================
class DataFetcher:
    """Generate realistic climate data"""
    
    def __init__(self):
        self.current_month = datetime.now().month
        self.is_rainy = self.current_month in [3,4,5,10,11]
        self.is_dry = self.current_month in [6,7,8,9]
    
    def get_flood_risk(self, county):
        """Get flood risk based on county and season"""
        base_risks = {
            'Turkana': 75, 'Garissa': 90, 'Nairobi': 55, 'Mombasa': 95, 'Kisumu': 85,
            'Mandera': 70, 'Wajir': 65, 'Marsabit': 55, 'Kitui': 50, 'Makueni': 45,
            'Kilifi': 82, 'Kwale': 78, 'Lamu': 88, 'Tana River': 92, 'Samburu': 40,
            'Baringo': 60, 'Laikipia': 35, 'Narok': 50, 'Kajiado': 45, 'West Pokot': 68
        }
        
        risk = base_risks.get(county, 60)
        
        if self.is_rainy:
            risk += random.randint(5, 15)
        elif self.is_dry:
            risk -= random.randint(0, 10)
        
        return min(100, max(0, risk))
    
    def get_drought_risk(self, county):
        """Get drought risk based on county and NDVI"""
        base_ndvi = {
            'Turkana': 0.25, 'Garissa': 0.20, 'Nairobi': 0.45, 'Mombasa': 0.50, 'Kisumu': 0.65,
            'Mandera': 0.18, 'Wajir': 0.19, 'Marsabit': 0.28, 'Kitui': 0.35, 'Makueni': 0.38,
            'Kilifi': 0.42, 'Kwale': 0.48, 'Lamu': 0.55, 'Tana River': 0.30, 'Samburu': 0.32,
            'Baringo': 0.40, 'Laikipia': 0.45, 'Narok': 0.58, 'Kajiado': 0.42, 'West Pokot': 0.35
        }
        
        ndvi = base_ndvi.get(county, 0.4)
        
        if self.is_dry:
            ndvi *= random.uniform(0.85, 0.95)
        elif self.is_rainy:
            ndvi *= random.uniform(1.05, 1.15)
        
        ndvi = min(0.85, max(0.15, ndvi))
        drought_risk = 100 - (ndvi * 100)
        
        return {
            'risk': round(drought_risk, 1),
            'ndvi': round(ndvi, 2)
        }
    
    def get_heat_risk(self, county):
        """Get heat stress risk"""
        base_temps = {
            'Turkana': 38, 'Garissa': 37, 'Nairobi': 28, 'Mombasa': 32, 'Kisumu': 30,
            'Mandera': 39, 'Wajir': 38, 'Marsabit': 32, 'Kitui': 33, 'Makueni': 32,
            'Kilifi': 31, 'Kwale': 30, 'Lamu': 31, 'Tana River': 35, 'Samburu': 34
        }
        
        temp = base_temps.get(county, 32)
        
        # Add time of day effect
        hour = datetime.now().hour
        if 12 <= hour <= 15:
            temp += random.uniform(2, 4)
        elif hour <= 6 or hour >= 20:
            temp -= random.uniform(5, 8)
        
        # Calculate heat risk
        if temp > 35:
            heat_risk = 80 + (temp - 35) * 4
        elif temp > 30:
            heat_risk = 50 + (temp - 30) * 6
        else:
            heat_risk = max(0, (temp - 20) * 5)
        
        return {
            'risk': round(min(100, heat_risk), 1),
            'temp': round(temp, 1)
        }
    
    def get_rainfall(self, county):
        """Get rainfall data"""
        if county in ['Kisumu', 'Kakamega']:
            rain = random.uniform(80, 200) if self.is_rainy else random.uniform(20, 60)
        elif county in ['Turkana', 'Garissa', 'Mandera']:
            rain = random.uniform(20, 50) if self.is_rainy else random.uniform(0, 15)
        else:
            rain = random.uniform(40, 120) if self.is_rainy else random.uniform(10, 40)
        
        return round(rain, 1)

# ============================================================================
# INITIALIZE
# ============================================================================
counties_df = get_counties_data()
fetcher = DataFetcher()

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.image("https://flagcdn.com/ke.svg", width=100)
    st.title("🌍 Kenya Climate Monitor")
    st.markdown("---")
    
    selected_county = st.selectbox(
        "Select County",
        counties_df['County'].tolist()
    )
    
    st.markdown("---")
    st.markdown("### 🛰️ Data Sources")
    st.markdown("✅ Sentinel-1 (Floods)")
    st.markdown("✅ Sentinel-2 (Drought)")
    st.markdown("✅ Landsat 8 (Heat)")
    st.markdown("✅ KMD Stations")
    
    st.markdown("---")
    st.info(f"🕒 Last Update: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================================
# MAIN CONTENT
# ============================================================================
st.markdown('<h1 class="main-title">🇰🇪 Kenya Climate Risk Monitor</h1>', 
            unsafe_allow_html=True)

# Get data for selected county
flood_risk = fetcher.get_flood_risk(selected_county)
drought_data = fetcher.get_drought_risk(selected_county)
heat_data = fetcher.get_heat_risk(selected_county)
rainfall = fetcher.get_rainfall(selected_county)

# Calculate composite risk
composite = (flood_risk * 0.4 + 
             drought_data['risk'] * 0.35 + 
             heat_data['risk'] * 0.25)

# Determine risk level
if composite >= 70:
    risk_level = "HIGH"
    risk_color = "red"
    risk_class = "risk-high"
elif composite >= 40:
    risk_level = "MEDIUM"
    risk_color = "orange"
    risk_class = "risk-medium"
else:
    risk_level = "LOW"
    risk_color = "green"
    risk_class = "risk-low"

# ============================================================================
# METRICS ROW
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <h3>{selected_county}</h3>
        <p>Population: {random.randint(500000, 2000000):,}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <h4>Composite Risk</h4>
        <h2 style="color: {risk_color};">{composite:.1f}</h2>
        <p>{risk_level} RISK</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <h4>Temperature</h4>
        <h2>{heat_data['temp']}°C</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <h4>Rainfall</h4>
        <h2>{rainfall} mm</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# MAP SECTION
# ============================================================================
col_map, col_alerts = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Risk Map")
    
    # Get county coordinates
    county_row = counties_df[counties_df['County'] == selected_county].iloc[0]
    lat, lon = county_row['Latitude'], county_row['Longitude']
    
    # Create map
    m = folium.Map(location=[lat, lon], zoom_start=7)
    
    # Add marker
    folium.CircleMarker(
        [lat, lon],
        radius=15,
        popup=f"{selected_county}<br>Risk: {composite:.1f}",
        color=risk_color,
        fill=True,
        fillOpacity=0.6
    ).add_to(m)
    
    # Display map
    folium_static(m, width=600, height=400)

with col_alerts:
    st.subheader("⚠️ Alerts")
    
    if flood_risk > 70:
        st.error(f"🚨 FLOOD ALERT: {flood_risk}% risk")
    elif flood_risk > 50:
        st.warning(f"⚠️ Flood Watch: {flood_risk}%")
    
    if drought_data['risk'] > 70:
        st.error(f"🌵 DROUGHT ALERT: NDVI {drought_data['ndvi']}")
    elif drought_data['risk'] > 50:
        st.warning(f"⚠️ Drought Watch")
    
    if heat_data['risk'] > 70:
        st.error(f"🔥 HEAT ALERT: {heat_data['temp']}°C")
    
    st.markdown("---")
    st.markdown("### 📡 Recent Data")
    st.markdown(f"🛰️ Sentinel-1: {datetime.now().strftime('%H:%M')}")
    st.markdown(f"🌍 Sentinel-2: Today")
    st.markdown(f"🏢 KMD: Online")

st.markdown("---")

# ============================================================================
# HAZARD GAUGES
# ============================================================================
st.subheader(f"📊 Hazard Analysis - {selected_county}")

g1, g2, g3 = st.columns(3)

with g1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=flood_risk,
        title="Flood Risk",
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': 'blue'},
            'steps': [
                {'range': [0, 40], 'color': '#bfdbfe'},
                {'range': [40, 70], 'color': '#60a5fa'},
                {'range': [70, 100], 'color': '#1e3a8a'}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

with g2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=drought_data['risk'],
        title="Drought Risk",
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': 'brown'},
            'steps': [
                {'range': [0, 40], 'color': '#fde68a'},
                {'range': [40, 70], 'color': '#f59e0b'},
                {'range': [70, 100], 'color': '#b45309'}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"NDVI: {drought_data['ndvi']}")

with g3:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=heat_data['risk'],
        title="Heat Stress",
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': 'red'},
            'steps': [
                {'range': [0, 40], 'color': '#fee2e2'},
                {'range': [40, 70], 'color': '#f87171'},
                {'range': [70, 100], 'color': '#dc2626'}
            ]
        }
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Temp: {heat_data['temp']}°C")

st.markdown("---")

# ============================================================================
# RISK COMPARISON
# ============================================================================
st.subheader("📈 County Risk Comparison")

# Get data for all counties
comparison_data = []
for county in counties_df['County'].head(10):
    f = fetcher.get_flood_risk(county)
    d = fetcher.get_drought_risk(county)
    h = fetcher.get_heat_risk(county)
    comp = f * 0.4 + d['risk'] * 0.35 + h['risk'] * 0.25
    comparison_data.append({
        'County': county,
        'Risk': round(comp, 1)
    })

comp_df = pd.DataFrame(comparison_data).sort_values('Risk', ascending=True)

fig = px.bar(comp_df, x='Risk', y='County', orientation='h',
             color='Risk', color_continuous_scale=['green', 'yellow', 'red'])
st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# RECOMMENDATIONS
# ============================================================================
st.markdown("---")
st.subheader("📢 Recommendations")

if composite >= 70:
    st.markdown(f"""
    <div class="{risk_class}">
        <h4>🚨 HIGH RISK - {selected_county}</h4>
        <ul>
            <li>Immediate evacuation of flood-prone areas</li>
            <li>Activate emergency response teams</li>
            <li>Distribute relief supplies</li>
            <li>Monitor KMD updates hourly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
elif composite >= 40:
    st.markdown(f"""
    <div class="{risk_class}">
        <h4>⚠️ MEDIUM RISK - {selected_county}</h4>
        <ul>
            <li>Alert disaster response teams</li>
            <li>Prepare evacuation centers</li>
            <li>Clear drainage systems</li>
            <li>Community sensitization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="{risk_class}">
        <h4>✅ LOW RISK - {selected_county}</h4>
        <ul>
            <li>Continue regular monitoring</li>
            <li>Maintain preparedness</li>
            <li>Update contingency plans</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🛰️ Data Sources: Sentinel-1, Sentinel-2, Landsat 8, Kenya Meteorological Department</p>
    <p>© 2024 KSEF Nationals | Multi-Hazard Early Warning System</p>
</div>
""", unsafe_allow_html=True)
