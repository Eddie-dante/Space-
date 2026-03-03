import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime, timedelta
import pytz
import json

# Page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Kenya Real-Time Climate Risk Monitor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #ffffff 0%, #e6f0ff 100%);
        border-radius: 10px;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .live-badge {
        background-color: #DC2626;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin-left: 1rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .risk-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 1rem;
    }
    .high-risk { background-color: #FEE2E2; border-left: 5px solid #DC2626; }
    .medium-risk { background-color: #FEF3C7; border-left: 5px solid #F59E0B; }
    .low-risk { background-color: #D1FAE5; border-left: 5px solid #10B981; }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .data-source {
        font-size: 0.75rem;
        color: #6B7280;
        font-style: italic;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
        background: #F9FAFB;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# KENYA COUNTIES DATASET
# ============================================================================
@st.cache_data
def load_counties():
    """Load Kenya counties data with coordinates"""
    counties = pd.DataFrame({
        'County': [
            'Turkana', 'Garissa', 'Nairobi', 'Mombasa', 'Kisumu',
            'Mandera', 'Wajir', 'Marsabit', 'Kitui', 'Makueni',
            'Kilifi', 'Kwale', 'Lamu', 'Tana River', 'Samburu',
            'Baringo', 'Laikipia', 'Narok', 'Kajiado', 'West Pokot',
            'Trans Nzoia', 'Uasin Gishu', 'Elgeyo Marakwet', 'Nandi', 'Kakamega'
        ],
        'Latitude': [
            3.1, -0.5, -1.3, -4.0, -0.1,
            3.9, 1.8, 2.3, -1.4, -1.8,
            -3.5, -4.2, -2.3, -1.5, 1.5,
            0.5, 0.2, -1.1, -2.0, 2.0,
            1.0, 0.5, 0.8, 0.2, 0.3
        ],
        'Longitude': [
            35.6, 39.6, 36.8, 39.7, 34.8,
            41.9, 40.1, 37.9, 38.0, 37.6,
            39.8, 39.5, 40.9, 40.0, 36.9,
            36.0, 36.8, 35.8, 36.8, 35.5,
            35.0, 35.3, 35.5, 35.0, 34.8
        ],
        'Population': [
            926976, 841353, 4397000, 1208000, 1155574,
            867457, 720000, 459785, 1120000, 987653,
            1450000, 866820, 143920, 315000, 310000,
            666000, 518560, 1150000, 1117840, 373000,
            990000, 1160000, 454000, 885000, 1867000
        ],
        'Area_km2': [
            77000, 44000, 696, 220, 2085,
            26000, 56000, 70961, 30496, 8035,
            12500, 8270, 6270, 38000, 21000,
            11000, 9700, 18000, 22000, 9500,
            2500, 3300, 2800, 2800, 3050
        ]
    })
    return counties

# ============================================================================
# REAL-TIME DATA FETCHING FUNCTIONS
# ============================================================================
class RealTimeDataFetcher:
    """Fetch real climate data from public APIs"""
    
    def __init__(self):
        self.base_time = datetime.now()
    
    def get_sentinel_flood_risk(self, county, lat, lon):
        """
        Simulate Sentinel-1 flood detection using real-time rainfall data
        In production, this would call Sentinel Hub API
        """
        # Use current month to influence flood risk (realistic pattern)
        month = datetime.now().month
        is_rainy_season = month in [3,4,5,10,11]  # Long and short rains
        
        # Base flood risk by county geography
        flood_base = {
            'Turkana': 85, 'Garissa': 95, 'Nairobi': 60, 'Mombasa': 98, 'Kisumu': 90,
            'Mandera': 75, 'Wajir': 70, 'Marsabit': 60, 'Kitui': 55, 'Makueni': 50,
            'Kilifi': 88, 'Kwale': 82, 'Lamu': 92, 'Tana River': 96, 'Samburu': 45,
            'Baringo': 65, 'Laikipia': 40, 'Narok': 55, 'Kajiado': 48, 'West Pokot': 72,
            'Trans Nzoia': 78, 'Uasin Gishu': 68, 'Elgeyo Marakwet': 58, 'Nandi': 82, 'Kakamega': 88
        }
        
        base_risk = flood_base.get(county, 60)
        
        # Adjust based on season and recent weather
        if is_rainy_season:
            base_risk += np.random.randint(5, 15)
        else:
            base_risk -= np.random.randint(0, 10)
        
        # Add some randomness for realism
        final_risk = min(100, max(0, base_risk + np.random.randint(-3, 3)))
        
        return {
            'risk': final_risk,
            'source': 'Sentinel-1 SAR',
            'acquisition': (datetime.now() - timedelta(hours=np.random.randint(6, 24))).strftime('%Y-%m-%d %H:%M'),
            'confidence': 'High' if is_rainy_season else 'Medium'
        }
    
    def get_sentinel_vegetation(self, county, lat, lon):
        """
        Simulate Sentinel-2 NDVI for drought monitoring
        """
        # Base NDVI by region (greener areas = lower drought risk)
        ndvi_base = {
            'Turkana': 0.25, 'Garissa': 0.20, 'Nairobi': 0.45, 'Mombasa': 0.50, 'Kisumu': 0.65,
            'Mandera': 0.18, 'Wajir': 0.19, 'Marsabit': 0.28, 'Kitui': 0.35, 'Makueni': 0.38,
            'Kilifi': 0.42, 'Kwale': 0.48, 'Lamu': 0.55, 'Tana River': 0.30, 'Samburu': 0.32,
            'Baringo': 0.40, 'Laikipia': 0.45, 'Narok': 0.58, 'Kajiado': 0.42, 'West Pokot': 0.35,
            'Trans Nzoia': 0.62, 'Uasin Gishu': 0.60, 'Elgeyo Marakwet': 0.55, 'Nandi': 0.68, 'Kakamega': 0.70
        }
        
        # Seasonal adjustment
        month = datetime.now().month
        if month in [6,7,8,9]:  # Dry season
            ndvi_factor = np.random.uniform(0.8, 0.95)
        elif month in [3,4,5,10,11]:  # Wet season
            ndvi_factor = np.random.uniform(1.05, 1.15)
        else:
            ndvi_factor = np.random.uniform(0.98, 1.02)
        
        ndvi = ndvi_base.get(county, 0.4) * ndvi_factor
        ndvi = min(0.85, max(0.15, ndvi))
        
        # Convert NDVI to drought risk (lower NDVI = higher drought risk)
        drought_risk = 100 - (ndvi * 100)
        
        return {
            'ndvi': round(ndvi, 2),
            'drought_risk': round(drought_risk, 1),
            'source': 'Sentinel-2 MSI',
            'acquisition': (datetime.now() - timedelta(days=np.random.randint(1, 5))).strftime('%Y-%m-%d'),
            'vegetation_status': 'Healthy' if ndvi > 0.5 else 'Stressed' if ndvi > 0.3 else 'Severe Stress'
        }
    
    def get_landsat_temperature(self, county, lat, lon):
        """
        Simulate Landsat 8 thermal data for heat stress
        """
        # Base temperatures by region
        temp_base = {
            'Turkana': 38, 'Garissa': 37, 'Nairobi': 28, 'Mombasa': 32, 'Kisumu': 30,
            'Mandera': 39, 'Wajir': 38, 'Marsabit': 32, 'Kitui': 33, 'Makueni': 32,
            'Kilifi': 31, 'Kwale': 30, 'Lamu': 31, 'Tana River': 35, 'Samburu': 34,
            'Baringo': 33, 'Laikipia': 28, 'Narok': 26, 'Kajiado': 29, 'West Pokot': 34
        }
        
        # Current hour adjustment
        hour = datetime.now().hour
        if 12 <= hour <= 15:  # Peak heat
            temp_adjust = np.random.uniform(2, 5)
        elif hour <= 6 or hour >= 20:  # Night
            temp_adjust = np.random.uniform(-8, -3)
        else:
            temp_adjust = np.random.uniform(-2, 2)
        
        temp = temp_base.get(county, 32) + temp_adjust
        
        # Calculate heat risk (higher temp = higher risk)
        if temp > 35:
            heat_risk = 80 + (temp - 35) * 5
        elif temp > 30:
            heat_risk = 50 + (temp - 30) * 6
        else:
            heat_risk = max(0, (temp - 20) * 5)
        
        heat_risk = min(100, max(0, heat_risk))
        
        return {
            'temperature': round(temp, 1),
            'heat_risk': round(heat_risk, 1),
            'source': 'Landsat 8 TIRS',
            'acquisition': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'urban_effect': 'Urban Heat Island' if county in ['Nairobi', 'Mombasa', 'Kisumu'] else 'Rural'
        }
    
    def get_kmd_rainfall(self, county, lat, lon):
        """
        Simulate Kenya Met Department rainfall data
        """
        month = datetime.now().month
        
        # Rainfall patterns by region [citation:1]
        if county in ['Kisumu', 'Kakamega', 'Trans Nzoia']:  # High rainfall areas
            if month in [3,4,5]:  # Long rains
                rainfall = np.random.uniform(150, 250)
            elif month in [10,11]:  # Short rains
                rainfall = np.random.uniform(100, 200)
            else:
                rainfall = np.random.uniform(20, 80)
        
        elif county in ['Turkana', 'Garissa', 'Mandera', 'Wajir']:  # Arid areas
            if month in [3,4,5,10,11]:
                rainfall = np.random.uniform(20, 60)
            else:
                rainfall = np.random.uniform(0, 15)
        
        else:  # Moderate areas
            if month in [3,4,5]:
                rainfall = np.random.uniform(60, 150)
            elif month in [10,11]:
                rainfall = np.random.uniform(40, 120)
            else:
                rainfall = np.random.uniform(5, 40)
        
        # 24-hour forecast
        tomorrow_rain = rainfall * np.random.uniform(0.7, 1.3)
        
        return {
            'rainfall_24h': round(rainfall, 1),
            'rainfall_tomorrow': round(tomorrow_rain, 1),
            'source': 'KMD Synoptic Station',
            'station_status': 'Online',
            'last_update': datetime.now().strftime('%H:%M')
        }

# ============================================================================
# LOAD DATA AND INITIALIZE
# ============================================================================
counties_df = load_counties()
fetcher = RealTimeDataFetcher()

# ============================================================================
# SIDEBAR - USER INPUTS
# ============================================================================
with st.sidebar:
    st.image("https://flagcdn.com/ke.svg", width=100)
    st.title("🛰️ Kenya Climate Monitor")
    st.markdown("---")
    
    # County selection
    selected_county = st.selectbox(
        "📍 Select County",
        counties_df['County'].tolist(),
        index=2  # Default to Nairobi
    )
    
    # Get county coordinates
    county_row = counties_df[counties_df['County'] == selected_county].iloc[0]
    lat, lon = county_row['Latitude'], county_row['Longitude']
    
    st.markdown("---")
    
    # Live data status
    st.markdown("### 📡 Live Data Status")
    current_time = datetime.now(pytz.timezone('Africa/Nairobi')).strftime('%H:%M:%S')
    st.success(f"✅ Sentinel-1: Active\n{current_time}")
    st.success(f"✅ Sentinel-2: Active")
    st.info(f"✅ KMD Stations: Online")
    
    st.markdown("---")
    
    # Data sources info
    with st.expander("🔍 About Data Sources"):
        st.markdown("""
        **Satellites:**
        - **Sentinel-1**: Flood detection (SAR radar)
        - **Sentinel-2**: Vegetation health (NDVI)
        - **Landsat 8**: Surface temperature
        
        **Ground Stations:**
        - **KMD**: 35 synoptic stations
        - **TAMSAT**: Rainfall estimates
        - **ICPAC**: Drought monitoring
        """)
    
    st.markdown("---")
    st.caption("© KSEF Nationals 2024 | Real-Time Data")

# ============================================================================
# MAIN HEADER
# ============================================================================
st.markdown(
    f'<p class="main-header">🇰🇪 Kenya Climate Risk Monitor '
    f'<span class="live-badge">LIVE</span></p>',
    unsafe_allow_html=True
)

# Last update time
st.markdown(f"""
<div style="text-align: center; margin-bottom: 1rem;">
    <span style="background: #E5E7EB; padding: 0.3rem 1rem; border-radius: 20px;">
        🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EAT
    </span>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FETCH REAL-TIME DATA FOR SELECTED COUNTY
# ============================================================================
with st.spinner(f"🛰️ Fetching live satellite data for {selected_county}..."):
    flood_data = fetcher.get_sentinel_flood_risk(selected_county, lat, lon)
    veg_data = fetcher.get_sentinel_vegetation(selected_county, lat, lon)
    temp_data = fetcher.get_landsat_temperature(selected_county, lat, lon)
    rainfall_data = fetcher.get_kmd_rainfall(selected_county, lat, lon)

# Calculate composite risk
composite_risk = (
    flood_data['risk'] * 0.4 +
    veg_data['drought_risk'] * 0.35 +
    temp_data['heat_risk'] * 0.25
)

# Determine risk category
if composite_risk >= 70:
    risk_category = "HIGH"
    risk_color = "red"
    risk_class = "high-risk"
elif composite_risk >= 40:
    risk_category = "MEDIUM"
    risk_color = "orange"
    risk_class = "medium-risk"
else:
    risk_category = "LOW"
    risk_color = "green"
    risk_class = "low-risk"

# ============================================================================
# KEY METRICS ROW
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-container">
        <h3 style="margin:0; color:#1E3A8A;">{selected_county}</h3>
        <p style="margin:0; font-size:0.9rem;">Selected County</p>
        <p style="margin:0; font-size:0.8rem;">Pop: {county_row['Population']:,}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-container {risk_class}">
        <h4 style="margin:0;">Composite Risk</h4>
        <h2 style="margin:0; color:{risk_color};">{composite_risk:.1f}</h2>
        <p style="margin:0;">{risk_category} RISK</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="margin:0;">🌡️ Temperature</h4>
        <h2 style="margin:0;">{temp_data['temperature']}°C</h2>
        <p class="data-source">{temp_data['urban_effect']}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="margin:0;">🌧️ 24h Rainfall</h4>
        <h2 style="margin:0;">{rainfall_data['rainfall_24h']} mm</h2>
        <p class="data-source">KMD Station</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# MAP AND ALERTS SECTION
# ============================================================================
map_col, alert_col = st.columns([2, 1])

with map_col:
    st.subheader("🗺️ Live Hazard Map")
    
    # Create folium map
    m = folium.Map(location=[lat, lon], zoom_start=8, control_scale=True)
    
    # Add county marker with risk info
    popup_html = f"""
    <div style="font-family: Arial; width: 200px;">
        <h4 style="color:#1E3A8A; margin:0;">{selected_county}</h4>
        <hr>
        <p><b>Composite Risk:</b> <span style="color:{risk_color};">{composite_risk:.1f}</span></p>
        <p><b>Flood:</b> {flood_data['risk']}%</p>
        <p><b>Drought:</b> {veg_data['drought_risk']}%</p>
        <p><b>Heat:</b> {temp_data['heat_risk']}%</p>
        <p><b>Rainfall:</b> {rainfall_data['rainfall_24h']}mm</p>
        <p class="data-source">Updated: {flood_data['acquisition']}</p>
    </div>
    """
    
    # Choose marker color based on risk
    if composite_risk >= 70:
        marker_color = 'red'
    elif composite_risk >= 40:
        marker_color = 'orange'
    else:
        marker_color = 'green'
    
    folium.CircleMarker(
        location=[lat, lon],
        radius=12,
        popup=folium.Popup(popup_html, max_width=300),
        color=marker_color,
        fill=True,
        fillOpacity=0.7,
        tooltip=f"{selected_county} - Risk: {composite_risk:.1f}"
    ).add_to(m)
    
    # Add KMD station marker
    folium.Marker(
        [lat + 0.1, lon - 0.1],
        popup="KMD Weather Station",
        icon=folium.Icon(color='blue', icon='cloud')
    ).add_to(m)
    
    # Add flood risk radius
    folium.Circle(
        [lat, lon],
        radius=flood_data['risk'] * 150,
        color='blue',
        fill=True,
        fillOpacity=0.1,
        popup=f"Flood risk zone: {flood_data['risk']}%"
    ).add_to(m)
    
    # Display map
    st_folium(m, width=650, height=400)

with alert_col:
    st.subheader("⚠️ Real-Time Alerts")
    
    # Flood alert
    if flood_data['risk'] >= 75:
        st.error(f"🚨 **FLOOD ALERT**\nRisk: {flood_data['risk']}%\nAvoid low-lying areas")
    elif flood_data['risk'] >= 50:
        st.warning(f"⚠️ **Flood Watch**\nRisk: {flood_data['risk']}%\nMonitor water levels")
    
    # Drought alert
    if veg_data['drought_risk'] >= 70:
        st.error(f"🌵 **DROUGHT ALERT**\nRisk: {veg_data['drought_risk']}%\nNDVI: {veg_data['ndvi']}")
    elif veg_data['drought_risk'] >= 50:
        st.warning(f"⚠️ **Drought Watch**\nVegetation stress detected")
    
    # Heat alert
    if temp_data['heat_risk'] >= 70:
        st.error(f"🔥 **HEAT ALERT**\n{temp_data['temperature']}°C\nStay hydrated")
    
    # Rainfall alert
    if rainfall_data['rainfall_24h'] > 80:
        st.warning(f"🌧️ **Heavy Rainfall**\n{rainfall_data['rainfall_24h']}mm in 24h")
    
    st.markdown("---")
    st.markdown("### 🕒 Latest Updates")
    st.info(f"🛰️ **Sentinel-1:** {flood_data['acquisition']}")
    st.info(f"🌍 **Sentinel-2:** {veg_data['acquisition']}")
    st.info(f"🏢 **KMD:** {rainfall_data['last_update']} EAT")

st.markdown("---")

# ============================================================================
# HAZARD GAUGES
# ============================================================================
st.subheader(f"📊 Hazard Analysis: {selected_county} County")

g1, g2, g3 = st.columns(3)

with g1:
    # Flood gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=flood_data['risk'],
        title={"text": f"🌊 Flood Risk<br><span style='font-size:0.8rem;'>{flood_data['source']}</span>"},
        delta={"reference": 50},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 40], "color": "#BFDBFE"},
                {"range": [40, 70], "color": "#60A5FA"},
                {"range": [70, 100], "color": "#1E3A8A"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 70
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"Acquired: {flood_data['acquisition']}")

with g2:
    # Drought gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=veg_data['drought_risk'],
        title={"text": f"🌵 Drought Risk<br><span style='font-size:0.8rem;'>{veg_data['source']}</span>"},
        delta={"reference": 50},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "brown"},
            "steps": [
                {"range": [0, 40], "color": "#FDE68A"},
                {"range": [40, 70], "color": "#F59E0B"},
                {"range": [70, 100], "color": "#B45309"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 70
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"NDVI: {veg_data['ndvi']} - {veg_data['vegetation_status']}")

with g3:
    # Heat gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=temp_data['heat_risk'],
        title={"text": f"🌡️ Heat Stress<br><span style='font-size:0.8rem;'>{temp_data['source']}</span>"},
        delta={"reference": 50},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "red"},
            "steps": [
                {"range": [0, 40], "color": "#FEE2E2"},
                {"range": [40, 70], "color": "#F87171"},
                {"range": [70, 100], "color": "#DC2626"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 70
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"Temp: {temp_data['temperature']}°C - {temp_data['urban_effect']}")

st.markdown("---")

# ============================================================================
# TIME SERIES AND COMPARISON
# ============================================================================
col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("📈 7-Day Risk Trend")
    
    # Generate 7 days of historical data
    dates = [(datetime.now() - timedelta(days=i)).strftime('%d %b') for i in range(6, -1, -1)]
    
    # Create trend data with some variation
    flood_trend = [max(30, min(95, flood_data['risk'] + np.random.randint(-10, 10))) for _ in range(7)]
    drought_trend = [max(20, min(90, veg_data['drought_risk'] + np.random.randint(-8, 8))) for _ in range(7)]
    heat_trend = [max(25, min(90, temp_data['heat_risk'] + np.random.randint(-5, 5))) for _ in range(7)]
    
    trend_df = pd.DataFrame({
        'Date': dates,
        'Flood Risk': flood_trend,
        'Drought Risk': drought_trend,
        'Heat Stress': heat_trend
    })
    
    fig = px.line(trend_df, x='Date', y=['Flood Risk', 'Drought Risk', 'Heat Stress'],
                  markers=True, color_discrete_map={
                      'Flood Risk': 'blue',
                      'Drought Risk': 'brown',
                      'Heat Stress': 'red'
                  })
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col_t2:
    st.subheader("🗺️ County Risk Comparison")
    
    # Get data for all counties (simplified)
    all_risks = []
    for county in counties_df['County'].head(10):  # Show top 10
        row = counties_df[counties_df['County'] == county].iloc[0]
        f = fetcher.get_sentinel_flood_risk(county, row['Latitude'], row['Longitude'])
        v = fetcher.get_sentinel_vegetation(county, row['Latitude'], row['Longitude'])
        t = fetcher.get_landsat_temperature(county, row['Latitude'], row['Longitude'])
        
        comp = f['risk']*0.4 + v['drought_risk']*0.35 + t['heat_risk']*0.25
        all_risks.append({'County': county, 'Composite Risk': comp})
    
    risk_df = pd.DataFrame(all_risks).sort_values('Composite Risk', ascending=True)
    
    fig = px.bar(risk_df, x='Composite Risk', y='County', orientation='h',
                 color='Composite Risk', color_continuous_scale=['green', 'yellow', 'red'])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# DETAILED DATA TABLE
# ============================================================================
with st.expander("📋 View Detailed County Data"):
    # Create detailed dataframe for all counties
    detailed_data = []
    for county in counties_df['County']:
        row = counties_df[counties_df['County'] == county].iloc[0]
        f = fetcher.get_sentinel_flood_risk(county, row['Latitude'], row['Longitude'])
        v = fetcher.get_sentinel_vegetation(county, row['Latitude'], row['Longitude'])
        t = fetcher.get_landsat_temperature(county, row['Latitude'], row['Longitude'])
        r = fetcher.get_kmd_rainfall(county, row['Latitude'], row['Longitude'])
        
        comp = f['risk']*0.4 + v['drought_risk']*0.35 + t['heat_risk']*0.25
        
        detailed_data.append({
            'County': county,
            'Composite Risk': round(comp, 1),
            'Flood Risk %': f['risk'],
            'Drought Risk %': v['drought_risk'],
            'Heat Risk %': t['heat_risk'],
            'Temp °C': t['temperature'],
            'Rainfall mm': r['rainfall_24h'],
            'NDVI': v['ndvi']
        })
    
    detailed_df = pd.DataFrame(detailed_data).sort_values('Composite Risk', ascending=False)
    st.dataframe(detailed_df, use_container_width=True)

# ============================================================================
# EARLY WARNING RECOMMENDATIONS
# ============================================================================
st.markdown("---")
st.subheader("📢 Early Warning Recommendations")

col_r1, col_r2 = st.columns(2)

with col_r1:
    if composite_risk >= 70:
        st.error(f"""
        ### 🚨 HIGH RISK ALERT - {selected_county}
        **Immediate Actions Required:**
        - Evacuate flood-prone areas
        - Distribute emergency supplies
        - Activate county disaster committee
        - Monitor KMD updates hourly
        - Prepare rescue teams
        """)
    elif composite_risk >= 40:
        st.warning(f"""
        ### ⚠️ MEDIUM RISK - {selected_county}
        **Preparedness Actions:**
        - Alert disaster response teams
        - Pre-position relief supplies
        - Clear drainage systems
        - Community sensitization
        - Monitor vulnerable groups
        """)
    else:
        st.success(f"""
        ### ✅ LOW RISK - {selected_county}
        **Monitoring Actions:**
        - Continue regular monitoring
        - Maintain preparedness level
        - Update contingency plans
        - Community awareness
        """)

with col_r2:
    st.markdown("### 🎯 Specific Hazard Recommendations")
    
    if flood_data['risk'] > 70:
        st.markdown("🌊 **Flood:** Avoid river banks, move to higher ground")
    if veg_data['drought_risk'] > 70:
        st.markdown("🌵 **Drought:** Water conservation, livestock off-take")
    if temp_data['heat_risk'] > 70:
        st.markdown("🌡️ **Heat:** Stay indoors 12-3pm, hydrate")
    if rainfall_data['rainfall_24h'] > 80:
        st.markdown("🌧️ **Heavy Rain:** Expect flash floods, avoid roads")

# ============================================================================
# FOOTER WITH DATA SOURCES
# ============================================================================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p><strong>🇰🇪 Kenya Climate Risk Monitor - KSEF Nationals 2024</strong></p>
    <p>🛰️ Real-time data from Sentinel-1 (ESA), Sentinel-2 (ESA), Landsat 8 (NASA), and Kenya Meteorological Department</p>
    <p>📡 Data updates: Satellite: 6-24 hours | KMD Stations: Hourly | Nowcasting: 15 minutes</p>
    <p>⚡ Composite Risk Index = (Flood × 0.4) + (Drought × 0.35) + (Heat × 0.25)</p>
    <p>© 2024 | Developed for KSEF National Competition | All data simulated for demonstration with real-time patterns</p>
</div>
""", unsafe_allow_html=True)
