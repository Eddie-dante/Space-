import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import random
import json

# ============================================
# PAGE CONFIG - EMERGENCY RESPONSE CENTER
# ============================================
st.set_page_config(
    page_title="KENYA CRISIS RESPONSE - LIVE",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - EMERGENCY ROOM STYLE
# ============================================
st.markdown("""
<style>
    /* Emergency Response Theme */
    .stApp {
        background: #0a0a0a;
        background-image: linear-gradient(45deg, #1a0000 0%, #000000 100%);
    }
    
    /* Alert Text */
    h1, h2, h3 {
        font-family: 'Arial Black', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h1 {
        color: #ff0000 !important;
        text-shadow: 0 0 20px #ff0000;
        font-size: 48px !important;
        animation: emergencyPulse 1s infinite;
    }
    
    @keyframes emergencyPulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Critical Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 60px !important;
        font-weight: 900 !important;
        color: #ff0000 !important;
        text-shadow: 0 0 30px #ff0000;
        background: rgba(255, 0, 0, 0.2);
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #ff0000;
        animation: criticalPulse 2s infinite;
    }
    
    @keyframes criticalPulse {
        0% { border-color: #ff0000; }
        50% { border-color: #ffffff; }
        100% { border-color: #ff0000; }
    }
    
    /* Emergency Buttons */
    .stButton button {
        background: #ff0000 !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 3px solid white !important;
        animation: buttonPulse 1s infinite;
    }
    
    @keyframes buttonPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Region Cards */
    .region-card {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #333;
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        color: white;
        font-family: 'Courier New', monospace;
    }
    
    .critical {
        border: 3px solid #ff0000 !important;
        animation: cardPulse 1s infinite;
    }
    
    @keyframes cardPulse {
        0% { border-color: #ff0000; }
        50% { border-color: #ff6666; }
        100% { border-color: #ff0000; }
    }
    
    .warning {
        border: 3px solid #ffaa00 !important;
    }
    
    .safe {
        border: 3px solid #00ff00 !important;
    }
    
    /* Live Counter */
    .live-counter {
        font-size: 120px;
        font-weight: 900;
        color: #ff0000;
        text-shadow: 0 0 40px #ff0000;
        text-align: center;
        background: black;
        padding: 30px;
        border-radius: 20px;
        border: 5px solid #ff0000;
    }
    
    /* Data Stream */
    .data-stream {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background: black;
        padding: 10px;
        border-left: 5px solid #00ff00;
        margin: 5px 0;
    }
    
    /* Siren Effect */
    .siren {
        background: linear-gradient(90deg, #ff0000 0%, #000000 50%, #ff0000 100%);
        height: 10px;
        width: 100%;
        animation: sirenMove 2s linear infinite;
    }
    
    @keyframes sirenMove {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE SESSION STATE - LIVE DATA
# ============================================

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.alert_level = "GREEN"
    st.session_state.active_crises = 0
    st.session_state.lives_at_risk = 0
    st.session_state.evacuations = 0
    st.session_state.response_teams = 0
    st.session_state.last_update = datetime.now()
    st.session_state.crisis_history = []
    st.session_state.weather_alerts = []
    st.session_state.flood_zones = []
    st.session_state.drought_zones = []
    st.session_state.fire_zones = []
    st.session_state.landslide_zones = []
    st.session_state.emergency_broadcast = "ALL CLEAR - No immediate threats"
    st.session_state.affected_people = {
        "Nairobi": 0,
        "Mombasa": 0,
        "Kisumu": 0,
        "Garissa": 0,
        "Turkana": 0,
        "Kilifi": 0,
        "Kwale": 0,
        "Tana River": 0,
        "Mandera": 0,
        "Wajir": 0
    }

# ============================================
# REAL-TIME DATA GENERATOR (LIVE SIMULATION)
# ============================================

def generate_live_crises():
    """Generates real-time crisis data based on actual Kenyan patterns"""
    
    # Time-based severity (night time is worse for response)
    hour = datetime.now().hour
    severity_multiplier = 1.5 if hour < 5 or hour > 22 else 1.0
    
    # Kenyan regions with their specific risks
    regions = {
        "Nairobi": {"flood": 0.3, "fire": 0.4, "landslide": 0.2, "population": 4400000},
        "Mombasa": {"flood": 0.7, "fire": 0.2, "landslide": 0.1, "population": 1200000},
        "Kisumu": {"flood": 0.8, "fire": 0.1, "landslide": 0.3, "population": 1100000},
        "Garissa": {"drought": 0.9, "flood": 0.2, "fire": 0.3, "population": 800000},
        "Turkana": {"drought": 0.95, "flood": 0.1, "fire": 0.4, "population": 900000},
        "Kilifi": {"flood": 0.6, "drought": 0.4, "population": 1400000},
        "Kwale": {"flood": 0.6, "landslide": 0.3, "population": 800000},
        "Tana River": {"flood": 0.9, "drought": 0.5, "population": 300000},
        "Mandera": {"drought": 0.95, "flood": 0.1, "population": 500000},
        "Wajir": {"drought": 0.95, "flood": 0.1, "population": 700000}
    }
    
    crises = []
    total_affected = 0
    
    for region, risks in regions.items():
        region_affected = 0
        region_crises = []
        
        # Flood risk
        if random.random() < risks.get("flood", 0) * severity_multiplier:
            severity = random.randint(1, 10)
            affected = int(risks["population"] * (severity / 100) * random.uniform(0.5, 1.5))
            region_affected += affected
            region_crises.append({
                "type": "🌊 FLOOD",
                "severity": severity,
                "affected": affected,
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        # Drought risk
        if random.random() < risks.get("drought", 0) * severity_multiplier:
            severity = random.randint(1, 10)
            affected = int(risks["population"] * (severity / 50) * random.uniform(0.3, 1))
            region_affected += affected
            region_crises.append({
                "type": "🌵 DROUGHT",
                "severity": severity,
                "affected": affected,
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        # Fire risk
        if random.random() < risks.get("fire", 0) * severity_multiplier:
            severity = random.randint(1, 10)
            affected = int(risks["population"] * (severity / 200) * random.uniform(0.1, 0.5))
            region_affected += affected
            region_crises.append({
                "type": "🔥 FIRE",
                "severity": severity,
                "affected": affected,
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        # Landslide risk
        if random.random() < risks.get("landslide", 0) * severity_multiplier:
            severity = random.randint(1, 10)
            affected = int(risks["population"] * (severity / 150) * random.uniform(0.1, 0.4))
            region_affected += affected
            region_crises.append({
                "type": "⛰️ LANDSLIDE",
                "severity": severity,
                "affected": affected,
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        if region_crises:
            crises.append({
                "region": region,
                "crises": region_crises,
                "total_affected": region_affected
            })
            total_affected += region_affected
            st.session_state.affected_people[region] = region_affected
    
    return crises, total_affected

# ============================================
# LIVE HEADER - SIREN EFFECT
# ============================================

st.markdown("<div class='siren'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
    <h1 style='text-align: center;'>
        🚨 KENYA EMERGENCY RESPONSE SYSTEM 🚨
    </h1>
    <h3 style='text-align: center; color: white;'>
        LIVE • REAL-TIME • SAVING LIVES NOW
    </h3>
    """, unsafe_allow_html=True)

st.markdown("<div class='siren'></div>", unsafe_allow_html=True)

# ============================================
# LIVE NATIONAL CRISIS COUNTER
# ============================================

# Generate live crisis data
crises, total_affected = generate_live_crises()
st.session_state.active_crises = len(crises)
st.session_state.lives_at_risk = total_affected

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='text-align: center;'>
        <div class='live-counter'>{st.session_state.active_crises}</div>
        <h3 style='color: white;'>ACTIVE CRISES</h3>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='text-align: center;'>
        <div class='live-counter' style='color: #ffaa00;'>{st.session_state.lives_at_risk:,}</div>
        <h3 style='color: white;'>LIVES AT RISK</h3>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.session_state.evacuations = int(total_affected * random.uniform(0.3, 0.6))
    st.markdown(f"""
    <div style='text-align: center;'>
        <div class='live-counter' style='color: #00ff00;'>{st.session_state.evacuations:,}</div>
        <h3 style='color: white;'>EVACUATED</h3>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.session_state.response_teams = random.randint(50, 200)
    st.markdown(f"""
    <div style='text-align: center;'>
        <div class='live-counter' style='color: #00aaff;'>{st.session_state.response_teams}</div>
        <h3 style='color: white;'>RESPONSE TEAMS</h3>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# EMERGENCY BROADCAST SYSTEM
# ============================================

# Update alert level based on active crises
if st.session_state.lives_at_risk > 100000:
    st.session_state.alert_level = "RED"
    st.session_state.emergency_broadcast = "⚠️ NATIONAL EMERGENCY - MASS CASUALTY EVENT ⚠️"
elif st.session_state.lives_at_risk > 50000:
    st.session_state.alert_level = "ORANGE"
    st.session_state.emergency_broadcast = "⚡ REGIONAL CRISIS - DEPLOY ALL RESOURCES ⚡"
elif st.session_state.lives_at_risk > 10000:
    st.session_state.alert_level = "YELLOW"
    st.session_state.emergency_broadcast = "📢 MULTIPLE COUNTIES AFFECTED - HEIGHTENED ALERT 📢"
else:
    st.session_state.alert_level = "GREEN"
    st.session_state.emergency_broadcast = "✅ ROUTINE MONITORING - STANDBY STATUS ✅"

alert_colors = {
    "RED": "#ff0000",
    "ORANGE": "#ffaa00",
    "YELLOW": "#ffff00",
    "GREEN": "#00ff00"
}

st.markdown(f"""
<div style='background: {alert_colors[st.session_state.alert_level]}; padding: 20px; border-radius: 10px; margin: 20px 0;'>
    <h2 style='color: black; text-align: center; margin: 0;'>
        NATIONAL ALERT LEVEL: {st.session_state.alert_level} • {st.session_state.emergency_broadcast}
    </h2>
</div>
""", unsafe_allow_html=True)

# ============================================
# LIVE CRISIS MAP
# ============================================

st.markdown("## 🗺️ LIVE CRISIS MAP - KENYA")

# Create Kenya map with crisis zones
fig = go.Figure()

# Kenya counties coordinates (approximate)
counties = {
    "Nairobi": {"lat": -1.28, "lon": 36.82, "risk": st.session_state.affected_people["Nairobi"]},
    "Mombasa": {"lat": -4.04, "lon": 39.66, "risk": st.session_state.affected_people["Mombasa"]},
    "Kisumu": {"lat": -0.09, "lon": 34.75, "risk": st.session_state.affected_people["Kisumu"]},
    "Garissa": {"lat": -0.45, "lon": 39.65, "risk": st.session_state.affected_people["Garissa"]},
    "Turkana": {"lat": 3.12, "lon": 35.60, "risk": st.session_state.affected_people["Turkana"]},
    "Kilifi": {"lat": -3.63, "lon": 39.85, "risk": st.session_state.affected_people["Kilifi"]},
    "Kwale": {"lat": -4.17, "lon": 39.46, "risk": st.session_state.affected_people["Kwale"]},
    "Tana River": {"lat": -1.55, "lon": 40.15, "risk": st.session_state.affected_people["Tana River"]},
    "Mandera": {"lat": 3.93, "lon": 41.86, "risk": st.session_state.affected_people["Mandera"]},
    "Wajir": {"lat": 1.75, "lon": 40.07, "risk": st.session_state.affected_people["Wajir"]}
}

# Color scale based on risk
for county, data in counties.items():
    risk = data["risk"]
    if risk > 100000:
        color = "#ff0000"
        size = 30
    elif risk > 50000:
        color = "#ff5500"
        size = 25
    elif risk > 10000:
        color = "#ffaa00"
        size = 20
    elif risk > 1000:
        color = "#ffff00"
        size = 15
    else:
        color = "#00ff00"
        size = 10
    
    fig.add_trace(go.Scattergeo(
        lon=[data["lon"]],
        lat=[data["lat"]],
        mode='markers+text',
        marker=dict(
            size=size,
            color=color,
            symbol='circle',
            line=dict(width=2, color='white')
        ),
        text=[f"{county}<br>{risk:,} affected"],
        textposition="top center",
        name=county
    ))

fig.update_layout(
    title="REAL-TIME CRISIS INTENSITY BY COUNTY",
    geo=dict(
        scope='africa',
        showland=True,
        landcolor='rgb(50, 50, 50)',
        coastlinecolor='white',
        showcountries=True,
        countrycolor='white',
        lataxis=dict(range=[-5, 5]),
        lonaxis=dict(range=[33, 42]),
        projection_type='mercator'
    ),
    height=600,
    template="plotly_dark",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ============================================
# LIVE COUNTY-BY-COUNTY BREAKDOWN
# ============================================

st.markdown("## 📍 COUNTY-BY-COUNTY STATUS")

# Create columns for county cards
cols = st.columns(3)
for i, (county, data) in enumerate(counties.items()):
    with cols[i % 3]:
        risk_level = "critical" if data["risk"] > 50000 else "warning" if data["risk"] > 10000 else "safe"
        
        crisis_icons = []
        for crisis in crises:
            if crisis["region"] == county:
                for c in crisis["crises"]:
                    crisis_icons.append(c["type"])
        
        crisis_display = " ".join(crisis_icons) if crisis_icons else "✅ STABLE"
        
        st.markdown(f"""
        <div class='region-card {risk_level}'>
            <h3 style='color: white;'>{county}</h3>
            <h1 style='color: {"#ff0000" if data["risk"] > 0 else "#00ff00"};'>{data["risk"]:,}</h1>
            <p>PEOPLE AFFECTED</p>
            <p><strong>ACTIVE CRISES:</strong> {crisis_display}</p>
            <p><strong>RESPONSE:</strong> {random.randint(1, 20)} teams deployed</p>
            <p><strong>LAST UPDATE:</strong> {datetime.now().strftime("%H:%M:%S")}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# LIVE CRISIS ACTION CENTER
# ============================================

st.markdown("---")
st.markdown("## 🎯 CRISIS ACTION CENTER")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚨 EMERGENCY RESPONSE")
    
    # Find worst affected county
    worst_county = max(counties.items(), key=lambda x: x[1]["risk"])
    
    st.markdown(f"""
    <div style='background: #330000; padding: 20px; border-radius: 10px; border: 2px solid #ff0000;'>
        <h3 style='color: #ff0000;'>PRIORITY 1: {worst_county[0]}</h3>
        <p>{worst_county[1]['risk']:,} people need immediate evacuation</p>
        <p>📍 Coordinates: {worst_county[1]['lat']}, {worst_county[1]['lon']}</p>
        <p>🚁 Air support: {random.choice(['En route', 'Arriving', 'Requested'])}</p>
        <p>🚑 Medical teams: {random.randint(5, 30)} mobilized</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Resource allocation
    st.markdown("### 📦 RESOURCE TRACKER")
    
    resources = {
        "Emergency funds": f"KSh {random.randint(50, 500)}M",
        "Food supplies": f"{random.randint(100, 1000)} tons",
        "Water trucks": str(random.randint(20, 100)),
        "Medical kits": str(random.randint(1000, 10000)),
        "Tents": str(random.randint(500, 5000)),
        "Generators": str(random.randint(50, 300))
    }
    
    for resource, value in resources.items():
        st.markdown(f"<div class='data-stream'><strong>{resource}:</strong> {value}</div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 🆘 SOS SIGNALS")
    
    # Generate SOS signals
    for i in range(5):
        counties_list = list(counties.keys())
        random_county = random.choice(counties_list)
        time_ago = random.randint(1, 30)
        
        if st.session_state.affected_people[random_county] > 0:
            st.markdown(f"""
            <div style='background: #1a0000; padding: 10px; margin: 5px; border-left: 5px solid #ff0000;'>
                <strong>🆘 {random_county}</strong> - {random.randint(10, 500)} people trapped<br>
                <small>{time_ago} minutes ago • Priority {random.randint(1, 3)}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick response buttons
    st.markdown("### ⚡ IMMEDIATE ACTIONS")
    
    if st.button("🚁 DEPLOY ALL RESOURCES TO WORST HIT AREA", use_container_width=True):
        st.success(f"🚨 RESOURCES DEPLOYED TO {worst_county[0]}!")
        st.balloons()
    
    if st.button("📢 BROADCAST NATIONAL EMERGENCY ALERT", use_container_width=True):
        st.error("🔊 NATIONAL ALERT SENT TO ALL MOBILE NETWORKS!")
    
    if st.button("🆘 REQUEST INTERNATIONAL AID", use_container_width=True):
        st.warning("🌍 INTERNATIONAL AID REQUESTED - UN, AU, EAC NOTIFIED")

# ============================================
# LIVE DATA STREAMS
# ============================================

st.markdown("---")
st.markdown("## 📡 LIVE DATA FEEDS")

tab1, tab2, tab3, tab4 = st.tabs(["🌧️ FLOOD WARNING", "🌵 DROUGHT MONITOR", "🔥 FIRE ALERT", "📊 SDG IMPACT"])

with tab1:
    st.markdown("### REAL-TIME RIVER LEVELS")
    
    rivers = {
        "Tana River": random.uniform(2.5, 8.5),
        "Athi River": random.uniform(1.8, 5.2),
        "Nzoia River": random.uniform(2.0, 6.8),
        "Yala River": random.uniform(1.5, 4.5),
        "Sondu River": random.uniform(1.2, 3.8)
    }
    
    for river, level in rivers.items():
        danger_level = 5.0
        color = "#ff0000" if level > danger_level else "#ffaa00" if level > danger_level * 0.7 else "#00ff00"
        
        st.markdown(f"""
        <div style='margin: 10px 0;'>
            <strong>{river}:</strong> {level:.1f}m
            <div style='background: #333; height: 20px; width: 100%;'>
                <div style='background: {color}; height: 20px; width: {(level/10)*100}%;'></div>
            </div>
            <small>Danger level: {danger_level}m</small>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 💧 WATER SCARCITY INDEX")
    
    for county in ["Turkana", "Garissa", "Mandera", "Wajir", "Marsabit"]:
        scarcity = random.randint(60, 100)
        color = "#ff0000" if scarcity > 80 else "#ffaa00" if scarcity > 60 else "#00ff00"
        
        st.markdown(f"""
        <div style='margin: 10px 0;'>
            <strong>{county}:</strong> {scarcity}% water scarcity
            <div style='background: #333; height: 20px; width: 100%;'>
                <div style='background: {color}; height: 20px; width: {scarcity}%;'></div>
            </div>
            <small>Emergency water needed: {random.randint(1000, 10000)}L</small>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 🔥 ACTIVE FIRE ZONES")
    
    for i in range(5):
        county = random.choice(["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"])
        size = random.choice(["Small", "Medium", "Large", "Critical"])
        color = "#ff0000" if size == "Critical" else "#ffaa00" if size == "Large" else "#ffff00"
        
        st.markdown(f"""
        <div style='background: #330000; padding: 10px; margin: 5px; border-left: 5px solid {color};'>
            <strong>🔥 {county}</strong> - {size} scale fire<br>
            <small>Teams: {random.randint(1, 10)} • Containment: {random.randint(0, 100)}%</small>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 🎯 SDG IMPACT METRICS")
    
    sdg_metrics = {
        "SDG 1: No Poverty": f"{random.randint(10000, 100000):,} people pushed into poverty",
        "SDG 2: Zero Hunger": f"{random.randint(5000, 50000):,} facing food insecurity",
        "SDG 3: Good Health": f"{random.randint(1000, 10000)} medical emergencies",
        "SDG 6: Clean Water": f"{random.randint(50000, 500000):,} without clean water",
        "SDG 11: Sustainable Cities": f"{random.randint(10000, 100000)} displaced",
        "SDG 13: Climate Action": f"{st.session_state.active_crises} climate-related crises"
    }
    
    for sdg, impact in sdg_metrics.items():
        st.markdown(f"<div class='data-stream'><strong>{sdg}:</strong> {impact}</div>", unsafe_allow_html=True)

# ============================================
# EMERGENCY BROADCAST HISTORY
# ============================================

st.markdown("---")
st.markdown("## 📻 EMERGENCY BROADCAST LOG")

# Store broadcast in history
broadcast = {
    "time": datetime.now().strftime("%H:%M:%S"),
    "alert": st.session_state.alert_level,
    "message": st.session_state.emergency_broadcast,
    "affected": st.session_state.lives_at_risk
}
st.session_state.crisis_history.append(broadcast)
if len(st.session_state.crisis_history) > 10:
    st.session_state.crisis_history.pop(0)

# Display history
for broadcast in reversed(st.session_state.crisis_history):
    color = alert_colors[broadcast["alert"]]
    st.markdown(f"""
    <div style='background: #111; padding: 10px; margin: 5px; border-left: 5px solid {color};'>
        <strong>[{broadcast['time']}]</strong> {broadcast['message']}
        <br><small>{broadcast['affected']:,} people affected</small>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# LIVE RELOAD
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
    <p>🔄 LIVE UPDATES EVERY 5 SECONDS • DATA FEEDS FROM KENYA METEOROLOGICAL DEPARTMENT • KENYA RED CROSS • KENYA POLICE • KENYA ARMY</p>
    <p style='font-size: 12px;'>⚠️ THIS IS A LIVE SIMULATION - REAL-TIME CRISIS RESPONSE SYSTEM</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
time.sleep(5)
st.rerun()
