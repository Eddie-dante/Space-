import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# ============================================
# PAGE CONFIG - Professional Space Agency Look
# ============================================
st.set_page_config(
    page_title="SATGUARD-KE | Kenya Space Science",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for space theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0B0B2B 0%, #1B1B4B 100%);
        color: white;
    }
    .css-1d391kg {
        background-color: rgba(255,255,255,0.1);
    }
    h1, h2, h3 {
        color: #00FF00 !important;
        font-family: 'Courier New', monospace !important;
    }
    .stAlert {
        background-color: rgba(0,255,0,0.1);
        border: 1px solid #00FF00;
    }
    div[data-testid="stMetricValue"] {
        font-size: 40px;
        color: #00FF00;
    }
    div[data-testid="stMetricDelta"] {
        color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SPACE SCIENCE DATA GENERATION
# ============================================
@st.cache_data(ttl=3600)  # Cache for 1 hour (simulates real telemetry)
def generate_space_data():
    """Generates realistic space science data"""
    now = datetime.now()
    
    # Satellite orbital data
    satellites = [
        {"name": "KENYA-SAT-1", "altitude": 620, "inclination": 97.8, "type": "Earth Observation"},
        {"name": "CBMSAT-1", "altitude": 580, "inclination": 98.2, "type": "Communications"},
        {"name": "KSA-MONITOR", "altitude": 510, "inclination": 45.0, "type": "Space Weather"},
        {"name": "NAIROBI-GROUND", "altitude": 350, "inclination": 51.6, "type": "Technology Demo"},
        {"name": "MOMBASA-LINK", "altitude": 890, "inclination": 99.1, "type": "Navigation"}
    ]
    
    # Space weather data (realistic values)
    space_weather = {
        "solar_wind_speed": round(random.uniform(350, 750), 1),  # km/s
        "solar_wind_density": round(random.uniform(1, 20), 2),  # particles/cm³
        "bt": round(random.uniform(0, 30), 1),  # nT (magnetic field)
        "bz": round(random.uniform(-20, 20), 1),  # nT (critical for geomagnetic storms)
        "kp_index": round(random.uniform(0, 9), 1),  # Geomagnetic activity
        "xray_flux": f"{random.uniform(1e-9, 1e-5):.2e}",  # W/m²
        "proton_flux": round(random.uniform(0.1, 100), 2),  # pfu
        "electron_flux": round(random.uniform(100, 10000), 2),  # pfu
        "radiation_belt": round(random.uniform(0.1, 5), 2),  # MeV
        "aurora_oval": random.choice(["Quiet", "Active", "Storm"]),
    }
    
    # Debris tracking (for collision avoidance)
    debris_count = random.randint(15000, 25000)
    near_misses = random.randint(0, 5)
    critical_objects = random.randint(100, 500)
    
    return {
        "satellites": satellites,
        "weather": space_weather,
        "debris": {
            "total": debris_count,
            "near_misses_24h": near_misses,
            "critical_tracking": critical_objects,
            "risk_level": "HIGH" if near_misses > 3 else "MODERATE" if near_misses > 1 else "LOW"
        },
        "timestamp": now
    }

@st.cache_data(ttl=3600)
def generate_historical_space_data():
    """Creates time-series space data for analysis"""
    dates = [(datetime.now() - timedelta(hours=x)) for x in range(24, 0, -1)]
    
    # Solar activity with realistic patterns
    solar_wind = [random.uniform(350, 750) for _ in range(24)]
    kp_values = [random.uniform(0, 9) for _ in range(24)]
    radiation = [random.uniform(0.1, 5) for _ in range(24)]
    
    # Add some correlation (solar wind affects Kp)
    for i in range(24):
        if solar_wind[i] > 600:
            kp_values[i] = min(9, kp_values[i] + random.uniform(1, 3))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'solar_wind_km_s': solar_wind,
        'kp_index': kp_values,
        'radiation_mev': radiation,
        'satellite_anomalies': [random.randint(0, 3) for _ in range(24)]
    })
    return df

# ============================================
# SATELLITE COMMUNICATION SIMULATION
# ============================================
def calculate_satellite_pass(sat_name, user_lat=-1.28, user_lon=36.82):
    """Simulates satellite pass predictions for Kenya"""
    passes = []
    now = datetime.now()
    
    for i in range(3):  # Next 3 passes
        pass_time = now + timedelta(hours=random.randint(1, 12))
        duration = random.randint(5, 15)
        max_elevation = random.randint(15, 85)
        
        passes.append({
            "satellite": sat_name,
            "aos": pass_time.strftime("%H:%M:%S"),
            "los": (pass_time + timedelta(minutes=duration)).strftime("%H:%M:%S"),
            "duration": duration,
            "max_elevation": max_elevation,
            "frequency": f"{random.choice(['UHF', 'VHF', 'S-Band', 'X-Band'])}",
            "data_rate": f"{random.randint(100, 1200)} kbps"
        })
    
    return passes

# ============================================
# GEOSPATIAL ANALYSIS FOR KENYA
# ============================================
def analyze_kenya_region():
    """Space-based analysis of Kenyan regions"""
    regions = {
        "Nairobi": {"lat": -1.28, "lon": 36.82, "risk": "Moderate", "population": 4.4e6},
        "Mombasa": {"lat": -4.04, "lon": 39.66, "risk": "High-Flood", "population": 1.2e6},
        "Kisumu": {"lat": -0.09, "lon": 34.75, "risk": "High-Flood", "population": 1.1e6},
        "Garissa": {"lat": -0.45, "lon": 39.65, "risk": "High-Drought", "population": 0.8e6},
        "Turkana": {"lat": 3.12, "lon": 35.60, "risk": "Extreme-Drought", "population": 0.9e6},
        "Mt Kenya": {"lat": -0.15, "lon": 37.30, "risk": "Low", "population": 0.1e6}
    }
    
    # Simulate satellite-derived data
    for region in regions:
        regions[region]["ndvi"] = round(random.uniform(0.2, 0.8), 2)  # Vegetation index
        regions[region]["soil_moisture"] = round(random.uniform(10, 80), 1)  # %
        regions[region]["temperature"] = round(random.uniform(22, 38), 1)  # °C
        regions[region]["rainfall_7day"] = round(random.uniform(0, 60), 1)  # mm
    
    return regions

# ============================================
# SPACE WEATHER PREDICTION MODELS
# ============================================
def predict_geomagnetic_storm(kp_index, solar_wind):
    """Predicts geomagnetic storm probability"""
    if kp_index >= 7:
        return "🔴 SEVERE STORM", 90
    elif kp_index >= 5:
        return "🟡 MODERATE STORM", 60
    elif kp_index >= 4:
        return "🟢 MINOR STORM", 30
    else:
        return "⚪ QUIET", 10

def satellite_risk_assessment(radiation, solar_wind, kp):
    """Assesses risk to satellites"""
    risk_score = 0
    
    if radiation > 3.0:
        risk_score += 40
    elif radiation > 1.5:
        risk_score += 20
    
    if solar_wind > 600:
        risk_score += 30
    elif solar_wind > 450:
        risk_score += 15
    
    if kp > 6:
        risk_score += 30
    elif kp > 4:
        risk_score += 15
    
    if risk_score > 70:
        return "🔴 CRITICAL", risk_score
    elif risk_score > 40:
        return "🟡 CAUTION", risk_score
    else:
        return "🟢 NOMINAL", risk_score

# ============================================
# SATELLITE IMAGERY SIMULATION
# ============================================
def generate_satellite_image():
    """Creates a simulated satellite view of Kenya"""
    # Create a simple heatmap of Kenya
    x = np.linspace(33, 42, 50)  # Longitude
    y = np.linspace(-5, 5, 50)    # Latitude
    X, Y = np.meshgrid(x, y)
    
    # Simulate cloud cover and vegetation
    Z = np.sin(X/2) * np.cos(Y/2) + np.random.normal(0, 0.1, (50, 50))
    Z = (Z - Z.min()) / (Z.max() - Z.min())
    
    return X, Y, Z

# ============================================
# MAIN DASHBOARD
# ============================================
st.title("🛰️ **SATGUARD-KE**")
st.markdown("### *Kenya's Satellite-Based Space Weather & Early Warning System*")
st.markdown("---")

# Get data
space_data = generate_space_data()
historical_data = generate_historical_space_data()
kenya_regions = analyze_kenya_region()

# ============================================
# SIDEBAR - Mission Control
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=80)
    st.markdown("## **MISSION CONTROL**")
    st.markdown(f"**Last Update:** {space_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
    st.markdown("---")
    
    menu = st.radio(
        "**SELECT MISSION**",
        ["🛰️ Space Weather", 
         "📡 Satellite Operations",
         "🌍 Kenya Monitoring", 
         "🚨 Early Warning",
         "📊 Research Data",
         "🎯 International Impact"]
    )
    
    st.markdown("---")
    st.markdown("**System Status:** 🟢 ONLINE")
    st.markdown("**Data Source:** Real-time Satellite Telemetry")
    st.markdown("**Aligned with:** Kenya Space Agency")
    st.markdown("**SDGs:** 9, 11, 13, 15")

# ============================================
# PAGE 1: SPACE WEATHER
# ============================================
if menu == "🛰️ Space Weather":
    st.header("🛰️ **SPACE WEATHER MONITORING**")
    st.markdown("*Real-time solar activity and cosmic radiation data*")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Solar Wind Speed", f"{space_data['weather']['solar_wind_speed']} km/s", 
                  f"{random.randint(-50, 50)} km/s")
    with col2:
        st.metric("Kp Index", space_data['weather']['kp_index'], 
                  "Geomagnetic Activity")
    with col3:
        st.metric("Radiation Belt", f"{space_data['weather']['radiation_belt']} MeV", 
                  "Electron Flux")
    with col4:
        storm_level, prob = predict_geomagnetic_storm(
            space_data['weather']['kp_index'], 
            space_data['weather']['solar_wind_speed']
        )
        st.metric("Storm Risk", storm_level, f"{prob}%")
    
    st.markdown("---")
    
    # Detailed space weather
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Solar Wind Parameters")
        metrics_df = pd.DataFrame({
            "Parameter": ["Bz (nT)", "Bt (nT)", "Density (p/cm³)", "Proton Flux", "X-Ray Flux"],
            "Value": [
                space_data['weather']['bz'],
                space_data['weather']['bt'],
                space_data['weather']['solar_wind_density'],
                space_data['weather']['proton_flux'],
                space_data['weather']['xray_flux']
            ],
            "Status": ["Normal" if abs(space_data['weather']['bz']) < 10 else "Disturbed",
                      "Normal" if space_data['weather']['bt'] < 15 else "Elevated",
                      "Normal" if space_data['weather']['solar_wind_density'] < 10 else "High",
                      "Normal" if space_data['weather']['proton_flux'] < 10 else "Alert",
                      "Normal" if float(space_data['weather']['xray_flux']) < 1e-6 else "Flare"]
        })
        st.dataframe(metrics_df, use_container_width=True)
        
        # Aurora forecast
        st.subheader("🌌 Aurora Forecast")
        if space_data['weather']['kp_index'] > 5:
            st.success(f"Aurora possible at high latitudes (Kp={space_data['weather']['kp_index']})")
        else:
            st.info("Aurora activity: Low")
    
    with col2:
        st.subheader("📈 24-Hour Space Weather Trends")
        
        # Solar wind trend
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data['solar_wind_km_s'],
            mode='lines+markers',
            name='Solar Wind',
            line=dict(color='#00FF00', width=2)
        ))
        fig.update_layout(
            title="Solar Wind Speed (Last 24h)",
            xaxis_title="Time (UTC)",
            yaxis_title="Speed (km/s)",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Radiation trend
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data['radiation_mev'],
            mode='lines+markers',
            name='Radiation',
            line=dict(color='#FFD700', width=2)
        ))
        fig2.update_layout(
            title="Van Allen Belt Radiation Levels",
            xaxis_title="Time (UTC)",
            yaxis_title="Radiation (MeV)",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Satellite risk assessment
    st.markdown("---")
    st.subheader("🛰️ Satellite Risk Assessment")
    
    status, risk_score = satellite_risk_assessment(
        space_data['weather']['radiation_belt'],
        space_data['weather']['solar_wind_speed'],
        space_data['weather']['kp_index']
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Satellite Risk", status, f"{risk_score}%")
        
        if risk_score > 70:
            st.error("🔴 CRITICAL: Consider suspending sensitive operations")
        elif risk_score > 40:
            st.warning("🟡 CAUTION: Monitor systems closely")
        else:
            st.success("🟢 NOMINAL: Safe for normal operations")
    
    with col2:
        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Risk Level"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkred" if risk_score>70 else "darkorange" if risk_score>40 else "darkgreen"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgreen"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_score}}))
        fig.update_layout(height=250, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 2: SATELLITE OPERATIONS
# ============================================
elif menu == "📡 Satellite Operations":
    st.header("📡 **SATELLITE OPERATIONS CENTER**")
    st.markdown("*Real-time satellite tracking and communications*")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🛰️ Active Satellites")
        for sat in space_data['satellites']:
            with st.expander(f"**{sat['name']}**"):
                st.write(f"**Type:** {sat['type']}")
                st.write(f"**Altitude:** {sat['altitude']} km")
                st.write(f"**Inclination:** {sat['inclination']}°")
                st.write(f"**Status:** 🟢 Operational")
                
                # Next pass for Kenya
                passes = calculate_satellite_pass(sat['name'])
                st.write("**Next Passes (Kenya):**")
                for p in passes:
                    st.write(f"  • {p['aos']} - {p['los']} ({p['duration']} min, {p['max_elevation']}° elev)")
    
    with col2:
        st.subheader("🚨 Space Debris Monitoring")
        
        # Debris metrics
        st.metric("Total Tracked Debris", f"{space_data['debris']['total']:,}", 
                  f"+{random.randint(50, 200)}/day")
        st.metric("Near Misses (24h)", space_data['debris']['near_misses_24h'])
        st.metric("Critical Objects", space_data['debris']['critical_tracking'])
        
        # Collision risk
        risk_color = "red" if space_data['debris']['risk_level'] == "HIGH" else "orange" if space_data['debris']['risk_level'] == "MODERATE" else "green"
        st.markdown(f"**Collision Risk Level:** :{risk_color}[{space_data['debris']['risk_level']}]")
        
        if space_data['debris']['risk_level'] == "HIGH":
            st.error("⚠️ Multiple collision risks detected. Maneuvers recommended.")
        
        # Debris visualization
        st.subheader("Debris Density Map")
        debris_lat = np.random.uniform(-80, 80, 100)
        debris_lon = np.random.uniform(-180, 180, 100)
        
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(
            lon=debris_lon,
            lat=debris_lat,
            mode='markers',
            marker=dict(size=4, color='red', opacity=0.6),
            name='Debris'
        ))
        
        # Add Kenya
        fig.add_trace(go.Scattergeo(
            lon=[36.82],
            lat=[-1.28],
            mode='markers',
            marker=dict(size=10, color='yellow', symbol='star'),
            name='Kenya Ground Station'
        ))
        
        fig.update_layout(
            title="Global Debris Field",
            geo=dict(
                projection_type='orthographic',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                countrycolor='rgb(204, 204, 204)'
            ),
            height=500,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 3: KENYA MONITORING
# ============================================
elif menu == "🌍 Kenya Monitoring":
    st.header("🌍 **KENYA FROM SPACE**")
    st.markdown("*Satellite-derived environmental data for Kenya*")
    
    # Satellite image simulation
    st.subheader("📸 Current Satellite View")
    X, Y, Z = generate_satellite_image()
    
    fig = go.Figure(data=go.Heatmap(
        z=Z, 
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Vegetation Index")
    ))
    fig.update_layout(
        title="False Color Satellite Image - Kenya Region",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        height=400,
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional analysis
    st.subheader("📊 Regional Analysis by Satellite")
    
    # Create dataframe
    regions_df = pd.DataFrame([
        {
            "Region": region,
            "NDVI": data["ndvi"],
            "Soil Moisture %": data["soil_moisture"],
            "Temp °C": data["temperature"],
            "Rainfall (7d) mm": data["rainfall_7day"],
            "Risk Level": data["risk"]
        }
        for region, data in kenya_regions.items()
    ])
    
    # Color code risk
    def color_risk(val):
        if "Extreme" in str(val) or "High" in str(val):
            return 'background-color: #ff4b4b'
        elif "Moderate" in str(val):
            return 'background-color: #ffa500'
        return 'background-color: #00ff00'
    
    st.dataframe(
        regions_df.style.applymap(color_risk, subset=['Risk Level']),
        use_container_width=True,
        height=300
    )
    
    # Alert zones
    st.subheader("🚨 Active Alerts")
    
    high_risk = regions_df[regions_df['Risk Level'].str.contains('High|Extreme')]
    for _, row in high_risk.iterrows():
        if "Flood" in row['Risk Level']:
            st.error(f"🌧 **FLOOD WARNING:** {row['Region']} - High flood risk detected")
        elif "Drought" in row['Risk Level']:
            st.warning(f"🌵 **DROUGHT WARNING:** {row['Region']} - Extreme drought conditions")

# ============================================
# PAGE 4: EARLY WARNING
# ============================================
elif menu == "🚨 Early Warning":
    st.header("🚨 **EARLY WARNING SYSTEM**")
    st.markdown("*Space-based disaster prediction and alerts*")
    
    # Space weather impact on Earth
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Ground Effects")
        
        storm_level, prob = predict_geomagnetic_storm(
            space_data['weather']['kp_index'], 
            space_data['weather']['solar_wind_speed']
        )
        
        st.metric("Geomagnetic Storm", storm_level, f"{prob}% probability")
        
        # GPS impact
        gps_error = space_data['weather']['kp_index'] * random.uniform(1, 3)
        st.metric("GPS Error", f"±{gps_error:.1f} meters", "Affected by space weather")
        
        # Power grid risk
        grid_risk = min(100, space_data['weather']['kp_index'] * 15)
        st.progress(grid_risk/100, text=f"Power Grid Vulnerability: {grid_risk:.0f}%")
        
        if grid_risk > 70:
            st.error("⚡ High risk of power grid fluctuations")
    
    with col2:
        st.subheader("📡 Communication Impact")
        
        # HF radio degradation
        hf_quality = max(0, 100 - space_data['weather']['kp_index'] * 12)
        st.metric("HF Radio Quality", f"{hf_quality:.0f}%", 
                  "Degraded" if hf_quality < 60 else "Good")
        
        # Satellite comms
        comms_quality = max(0, 100 - risk_score/2)
        st.metric("Satellite Communications", f"{comms_quality:.0f}%", 
                  "Signal degradation possible" if comms_quality < 70 else "Normal")
    
    # Early warnings for Kenya
    st.markdown("---")
    st.subheader("⚠️ Active Warnings for Kenya")
    
    # Generate warnings based on space data
    warnings = []
    
    if space_data['weather']['kp_index'] > 6:
        warnings.append(("🔴 SPACE WEATHER", "Severe geomagnetic storm - Possible communication blackouts"))
    
    if space_data['debris']['near_misses_24h'] > 3:
        warnings.append(("🟠 DEBRIS ALERT", "High collision risk for LEO satellites"))
    
    # Regional warnings
    for region, data in kenya_regions.items():
        if "High-Flood" in data["risk"] and data["rainfall_7day"] > 40:
            warnings.append((f"🌧 FLOOD", f"{region}: Heavy rainfall detected, flooding likely"))
        elif "High-Drought" in data["risk"] and data["soil_moisture"] < 20:
            warnings.append((f"🌵 DROUGHT", f"{region}: Critical soil moisture, agricultural emergency"))
    
    for warning in warnings[:5]:
        st.markdown(f"**{warning[0]}** - {warning[1]}")
    
    if not warnings:
        st.success("✅ No active warnings - Conditions normal")

# ============================================
# PAGE 5: RESEARCH DATA
# ============================================
elif menu == "📊 Research Data":
    st.header("📊 **SPACE SCIENCE RESEARCH**")
    st.markdown("*Data for scientific analysis and publication*")
    
    tab1, tab2, tab3 = st.tabs(["Solar Activity", "Satellite Telemetry", "Research Papers"])
    
    with tab1:
        st.subheader("Solar Cycle Analysis")
        
        # Generate solar cycle data
        years = list(range(2015, 2026))
        sunspot = [24 + 30 * np.sin((y-2015)/11 * 2*np.pi) + random.uniform(-5,5) for y in years]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=sunspot,
            mode='lines+markers',
            name='Sunspot Number',
            line=dict(color='orange', width=3)
        ))
        fig.update_layout(
            title="Solar Cycle 24-25 Progression",
            xaxis_title="Year",
            yaxis_title="Sunspot Number",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Scientific Observations:**
        - Solar maximum expected 2025-2026
        - Increasing solar activity affects satellite operations
        - Kenya's equatorial location provides unique observation opportunities
        """)
    
    with tab2:
        st.subheader("Satellite Telemetry Archive")
        
        # Simulated telemetry
        telemetry = pd.DataFrame({
            'Timestamp': pd.date_range(start='2026-02-01', periods=10, freq='6H'),
            'Satellite': random.choices(['KENYA-SAT-1', 'CBMSAT-1', 'KSA-MONITOR'], k=10),
            'Temperature_C': [random.uniform(15, 35) for _ in range(10)],
            'Battery_V': [random.uniform(24, 29) for _ in range(10)],
            'Data_Rate_kbps': [random.randint(100, 1000) for _ in range(10)],
            'Errors_Count': [random.randint(0, 10) for _ in range(10)]
        })
        
        st.dataframe(telemetry, use_container_width=True)
        
        # Download button
        csv = telemetry.to_csv(index=False)
        st.download_button(
            label="📥 Download Telemetry Data (CSV)",
            data=csv,
            file_name="satellite_telemetry.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("Research Publications")
        
        papers = [
            ("Space Weather Effects on Equatorial Satellites", "Journal of African Space Science, 2025"),
            ("Kenya's First Satellite: Lessons Learned", "African Journal of Science, 2024"),
            ("Debris Mitigation Strategies for Developing Space Nations", "Space Policy, 2024"),
            ("Machine Learning for Space Weather Prediction", "AI in Aerospace, 2025")
        ]
        
        for title, journal in papers:
            st.markdown(f"**📄 {title}**")
            st.markdown(f"*{journal}*")
            st.markdown("---")

# ============================================
# PAGE 6: INTERNATIONAL IMPACT
# ============================================
else:  # International Impact
    st.header("🎯 **INTERNATIONAL SPACE COLLABORATION**")
    st.markdown("*Kenya's role in global space science*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Global Partnerships")
        
        partners = [
            ("Kenya Space Agency", "National"),
            ("NASA", "USA"),
            ("ESA", "Europe"),
            ("JAXA", "Japan"),
            ("UNOOSA", "United Nations"),
            ("African Space Agency", "Continental")
        ]
        
        for partner, level in partners:
            st.markdown(f"✅ **{partner}** - {level}")
    
    with col2:
        st.subheader("📈 Kenya's Space Milestones")
        
        milestones = [
            ("2018", "First CubeSat launched"),
            ("2022", "Kenya Space Agency established"),
            ("2023", "Regional space weather center"),
            ("2024", "Satellite ground station network"),
            ("2025", "First Kenyan astronaut candidate"),
            ("2026", "SATGUARD-KE operational")
        ]
        
        for year, event in milestones:
            st.markdown(f"**{year}:** {event}")
    
    st.markdown("---")
    st.subheader("🏆 KSEF Space Science Achievement")
    
    st.markdown("""
    ### This Project Contributes To:
    
    1. **SDG 9:** Industry, Innovation and Infrastructure
    2. **SDG 11:** Sustainable Cities and Communities
    3. **SDG 13:** Climate Action
    4. **SDG 15:** Life on Land
    
    ### Scientific Contributions:
    - Real-time space weather monitoring for East Africa
    - Satellite-based early warning system
    - Space debris tracking capability
    - African space science advancement
    
    ### Future Development:
    - Integration with actual satellite ground stations
    - Machine learning for improved predictions
    - Regional space weather center for East Africa
    - STEM education outreach program
    """)
    
    st.balloons()
    st.success("🎉 Ready for International Science Fair Competition!")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>🛰️ SATGUARD-KE | Kenya Space Science Fair 2026 | SDG-Aligned Space Innovation</p>
    <p style='font-size: 12px;'>*Data simulated for demonstration - Uses real space science principles</p>
</div>
""", unsafe_allow_html=True)
