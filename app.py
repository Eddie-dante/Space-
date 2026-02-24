import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import random

# ============================================
# PAGE CONFIG - SPACE MISSION CONTROL THEME
# ============================================
st.set_page_config(
    page_title="KENYA MARS MISSION",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS - REAL MISSION CONTROL LOOK
st.markdown("""
<style>
    /* Mission Control Theme */
    .stApp {
        background: #0a0f1e;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.15) 2px, transparent 2px),
            radial-gradient(white, rgba(255,255,255,.1) 1px, transparent 1px);
        background-size: 50px 50px, 10px 10px;
    }
    
    /* Terminal-style text */
    h1, h2, h3, .stMarkdown {
        font-family: 'Courier New', monospace !important;
        color: #00ff9d !important;
        text-shadow: 0 0 10px #00ff9d;
    }
    
    /* Mission Control Panels */
    div[data-testid="stMetricValue"] {
        font-size: 60px !important;
        color: #00ff9d !important;
        font-family: 'Digital', 'Courier New', monospace !important;
        text-shadow: 0 0 20px #00ff9d;
        background: rgba(0, 255, 157, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #00ff9d;
    }
    
    /* Alert Panels */
    .stAlert {
        background: rgba(255, 0, 0, 0.2) !important;
        border: 3px solid #ff0000 !important;
        color: #ff0000 !important;
        font-weight: bold;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Glowing buttons */
    .stButton button {
        background: transparent !important;
        color: #00ff9d !important;
        border: 2px solid #00ff9d !important;
        font-family: 'Courier New', monospace !important;
        font-size: 20px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        animation: glow 2s infinite;
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px #00ff9d; }
        50% { box-shadow: 0 0 20px #00ff9d; }
        100% { box-shadow: 0 0 5px #00ff9d; }
    }
    
    /* Mission timer */
    .mission-timer {
        font-size: 48px;
        font-family: 'Digital', 'Courier New', monospace;
        color: #ffaa00;
        text-shadow: 0 0 20px #ffaa00;
        background: black;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #ffaa00;
        text-align: center;
    }
    
    /* Data streams */
    .data-stream {
        font-family: 'Courier New', monospace;
        color: #00ff9d;
        background: rgba(0, 255, 157, 0.05);
        padding: 10px;
        border-left: 3px solid #00ff9d;
        margin: 5px 0;
        animation: blink 5s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        95% { opacity: 1; }
        100% { opacity: 0.8; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# MISSION STATE - REAL-TIME SIMULATION
# ============================================

if 'mission_time' not in st.session_state:
    st.session_state.mission_time = datetime.now()
    st.session_state.mission_phase = "LAUNCH"
    st.session_state.distance_earth = 0  # km
    st.session_state.distance_mars = 546000000  # km to Mars
    st.session_state.velocity = 0  # km/s
    st.session_state.fuel = 100  # percentage
    st.session_state.oxygen = 100
    st.session_state.power = 100
    st.session_state.comm_delay = 0  # seconds
    st.session_state.anomalies = []
    st.session_state.rover_deployed = False
    st.session_state.mars_landing = False
    st.session_state.countdown = 10
    st.session_state.emergency = False
    st.session_state.telemetry_history = []

# ============================================
# MISSION HEADER - LIVE COUNTDOWN
# ============================================

st.markdown("""
<div style='text-align: center;'>
    <h1>🚀 KENYA SPACE AGENCY - MARS MISSION 2026 🚀</h1>
    <h2 style='color: #ffaa00;'>"TAARIFA ZA BONDE LA UFA"</h2>
</div>
""", unsafe_allow_html=True)

# Mission timer
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='mission-timer'>MISSION TIME<br>{st.session_state.mission_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='mission-timer'>PHASE<br>{st.session_state.mission_phase}</div>", unsafe_allow_html=True)
with col3:
    status_color = "#00ff00" if not st.session_state.emergency else "#ff0000"
    st.markdown(f"<div class='mission-timer' style='color: {status_color};'>STATUS<br>{'NOMINAL' if not st.session_state.emergency else 'EMERGENCY'}</div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='mission-timer'>CREW<br>AI-CONTROL</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# MAIN MISSION CONTROL INTERFACE
# ============================================

# Mission Control Buttons
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🚀 LAUNCH"):
        st.session_state.mission_phase = "ASCENT"
        st.session_state.velocity = 8
        st.balloons()
with col2:
    if st.button("🛸 COURSE CORRECTION"):
        st.session_state.anomalies.append("Course correction executed")
with col3:
    if st.button("🔴 MARS ORBIT"):
        st.session_state.mission_phase = "MARS ORBIT"
        st.session_state.distance_mars = 20000
with col4:
    if st.button("🦾 DEPLOY ROVER"):
        if st.session_state.mission_phase == "MARS ORBIT":
            st.session_state.rover_deployed = True
            st.session_state.mission_phase = "ROVER DEPLOYED"
with col5:
    if st.button("⚠️ EMERGENCY PROTOCOL"):
        st.session_state.emergency = not st.session_state.emergency

st.markdown("---")

# ============================================
# LIVE TELEMETRY - SPACECRAFT STATUS
# ============================================

st.markdown("## 📡 LIVE TELEMETRY STREAM")

# Update telemetry based on mission phase
if st.session_state.mission_phase == "ASCENT":
    st.session_state.distance_earth += st.session_state.velocity * 10
    st.session_state.fuel = max(0, st.session_state.fuel - 0.1)
    st.session_state.oxygen = max(0, st.session_state.oxygen - 0.05)
    st.session_state.power = max(0, st.session_state.power - 0.08)
    st.session_state.comm_delay = st.session_state.distance_earth / 300000  # light delay

elif st.session_state.mission_phase == "MARS ORBIT":
    st.session_state.distance_mars = max(0, st.session_state.distance_mars - 100)
    st.session_state.power -= 0.02
    st.session_state.comm_delay = (546000000 - st.session_state.distance_mars) / 300000

# Random anomalies (keep it exciting!)
if random.random() < 0.01:  # 1% chance per update
    anomalies = [
        "🔥 Temperature spike in engine bay",
        "⚠️ Communication glitch detected",
        "🔋 Solar panel efficiency dropping",
        "📡 Signal interference",
        "🌡️ Coolant pressure fluctuation",
        "⚡ Power surge in navigation system"
    ]
    st.session_state.anomalies.append(random.choice(anomalies))
    if len(st.session_state.anomalies) > 5:
        st.session_state.anomalies.pop(0)

# Display telemetry in mission control style
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='data-stream'>
        🌍 DISTANCE FROM EARTH: {st.session_state.distance_earth:,.0f} km<br>
        🔴 DISTANCE TO MARS: {st.session_state.distance_mars:,.0f} km<br>
        🚀 VELOCITY: {st.session_state.velocity:.1f} km/s<br>
        ⏱️ COMMUNICATION DELAY: {st.session_state.comm_delay:.1f} seconds
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Fuel gauge
    fuel_color = "#00ff00" if st.session_state.fuel > 50 else "#ffaa00" if st.session_state.fuel > 20 else "#ff0000"
    st.markdown(f"""
    <div class='data-stream'>
        ⛽ FUEL: <span style='color: {fuel_color};'>{st.session_state.fuel:.1f}%</span><br>
        💨 OXYGEN: <span style='color: {"#00ff00" if st.session_state.oxygen > 50 else "#ffaa00" if st.session_state.oxygen > 20 else "#ff0000"};'>{st.session_state.oxygen:.1f}%</span><br>
        ⚡ POWER: <span style='color: {"#00ff00" if st.session_state.power > 50 else "#ffaa00" if st.session_state.power > 20 else "#ff0000"};'>{st.session_state.power:.1f}%</span><br>
        🛰️ SYSTEMS: {'🟢 ONLINE' if not st.session_state.emergency else '🔴 EMERGENCY'}
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='data-stream'>
        🎯 MISSION PHASE: {st.session_state.mission_phase}<br>
        🤖 ROVER STATUS: {'🟢 DEPLOYED' if st.session_state.rover_deployed else '⚪ STOWED'}<br>
        📊 DATA RATE: {random.randint(100, 500)} kbps<br>
        🌡️ TEMPERATURE: {random.randint(-50, 30)}°C
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 3D SPACE VISUALIZATION
# ============================================

st.markdown("## 🪐 SOLAR SYSTEM POSITION")

# Create 3D visualization
fig = go.Figure()

# Sun
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers',
    marker=dict(size=20, color='yellow'),
    name='Sun'
))

# Earth orbit
earth_angle = time.time() * 0.1
earth_x = 150 * np.cos(earth_angle)
earth_y = 150 * np.sin(earth_angle)
earth_z = 0

# Mars orbit
mars_angle = time.time() * 0.05
mars_x = 228 * np.cos(mars_angle)
mars_y = 228 * np.sin(mars_angle)
mars_z = 10

# Spacecraft position (between Earth and Mars)
if st.session_state.mission_phase in ["ASCENT", "CRUISE"]:
    progress = 1 - (st.session_state.distance_mars / 546000000)
    craft_x = earth_x + (mars_x - earth_x) * progress
    craft_y = earth_y + (mars_y - earth_y) * progress
    craft_z = earth_z + (mars_z - earth_z) * progress
else:
    craft_x, craft_y, craft_z = mars_x, mars_y, mars_z

# Plot Earth
fig.add_trace(go.Scatter3d(
    x=[earth_x], y=[earth_y], z=[earth_z],
    mode='markers+text',
    marker=dict(size=15, color='blue'),
    text=['🌍 EARTH'],
    textposition="top center",
    name='Earth'
))

# Plot Mars
fig.add_trace(go.Scatter3d(
    x=[mars_x], y=[mars_y], z=[mars_z],
    mode='markers+text',
    marker=dict(size=12, color='red'),
    text=['🔴 MARS'],
    textposition="top center",
    name='Mars'
))

# Plot Spacecraft
fig.add_trace(go.Scatter3d(
    x=[craft_x], y=[craft_y], z=[craft_z],
    mode='markers+text',
    marker=dict(size=8, color='green', symbol='diamond'),
    text=['🚀 KENYA-1'],
    textposition="top center",
    name='Spacecraft'
))

# Orbit paths
orbit_angles = np.linspace(0, 2*np.pi, 100)
earth_orbit_x = 150 * np.cos(orbit_angles)
earth_orbit_y = 150 * np.sin(orbit_angles)
mars_orbit_x = 228 * np.cos(orbit_angles)
mars_orbit_y = 228 * np.sin(orbit_angles)

fig.add_trace(go.Scatter3d(
    x=earth_orbit_x, y=earth_orbit_y, z=np.zeros(100),
    mode='lines',
    line=dict(color='blue', width=1, dash='dot'),
    name='Earth Orbit'
))

fig.add_trace(go.Scatter3d(
    x=mars_orbit_x, y=mars_orbit_y, z=np.ones(100)*10,
    mode='lines',
    line=dict(color='red', width=1, dash='dot'),
    name='Mars Orbit'
))

fig.update_layout(
    title="REAL-TIME MISSION TRAJECTORY",
    scene=dict(
        xaxis_title="X (million km)",
        yaxis_title="Y (million km)",
        zaxis_title="Z (million km)",
        bgcolor='rgba(0,0,0,0)'
    ),
    height=600,
    showlegend=True,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================
# MISSION LOG & ANOMALIES
# ============================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📋 MISSION LOG")
    
    # Generate mission events
    if st.session_state.mission_phase == "ASCENT":
        st.markdown("🟢 T+ 00:01:23 - Stage 1 separation confirmed")
        st.markdown("🟢 T+ 00:02:45 - Fairing jettisoned")
        st.markdown("🟢 T+ 00:05:12 - Earth orbit insertion")
    
    elif st.session_state.mission_phase == "MARS ORBIT":
        st.markdown("🟢 T+ 180:15:33 - Mars orbit insertion burn")
        st.markdown("🟢 T+ 180:22:18 - Orbital parameters nominal")
        st.markdown("🟡 T+ 181:03:47 - Preparing for landing sequence")
    
    if st.session_state.rover_deployed:
        st.markdown("🟢 T+ 185:45:12 - ROVER DEPLOYED SUCCESSFULLY!")
        st.markdown("🟢 T+ 185:46:30 - First image received from surface")
        st.markdown("🎉 HISTORIC MOMENT: First Kenyan rover on Mars!")

with col2:
    st.markdown("## ⚠️ ACTIVE ANOMALIES")
    
    if st.session_state.anomalies:
        for anomaly in st.session_state.anomalies[-3:]:  # Show last 3
            st.markdown(f"🔴 {anomaly}")
    else:
        st.markdown("✅ All systems nominal")
    
    # Emergency override
    if st.session_state.emergency:
        st.error("🚨 MISSION EMERGENCY - OVERRIDE PROTOCOLS ACTIVE")
        
        if st.button("🛑 ABORT MISSION"):
            st.session_state.mission_phase = "ABORTED"
            st.error("MISSION ABORTED - RETURNING TO EARTH")

# ============================================
# MARS SURFACE EXPLORATION
# ============================================

if st.session_state.rover_deployed:
    st.markdown("---")
    st.markdown("## 🦾 MARS ROVER FEED")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📸 Rover Camera View")
        
        # Generate random Mars landscape
        img_data = np.random.rand(20, 30)
        
        fig = go.Figure(data=go.Heatmap(
            z=img_data,
            colorscale='Hot',
            showscale=False
        ))
        fig.update_layout(
            title="MARS SURFACE - KENYA ROVER CAMERA",
            height=400,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔬 Science Instruments")
        
        # Soil analysis
        st.markdown(f"""
        <div class='data-stream'>
            🪨 Soil Composition:<br>
            - Silicon: {random.randint(20, 30)}%<br>
            - Iron: {random.randint(10, 20)}%<br>
            - Magnesium: {random.randint(5, 15)}%<br>
            - Sulfur: {random.randint(3, 8)}%<br>
            <br>
            💧 Water Ice Detection: {'✅ POSITIVE' if random.random() > 0.7 else '❌ NEGATIVE'}<br>
            🌡️ Surface Temperature: {random.randint(-100, 20)}°C<br>
            💨 Atmospheric Pressure: {random.randint(4, 10)} mb
        </div>
        """, unsafe_allow_html=True)
        
        # Sample collection
        if st.button("🧪 COLLECT SOIL SAMPLE"):
            st.balloons()
            st.success(f"Sample #{random.randint(1000, 9999)} collected and analyzed!")

# ============================================
# MISSION SUMMARY & ACHIEVEMENTS
# ============================================

st.markdown("---")
st.markdown("## 🏆 MISSION ACHIEVEMENTS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.distance_earth > 100000:
        st.markdown("✅ **EARTH ESCAPE**")
    else:
        st.markdown("⬜ Earth escape")
        
with col2:
    if st.session_state.mission_phase in ["MARS ORBIT", "ROVER DEPLOYED"]:
        st.markdown("✅ **MARS ORBIT INSERTION**")
    else:
        st.markdown("⬜ Mars orbit")
        
with col3:
    if st.session_state.rover_deployed:
        st.markdown("✅ **ROVER DEPLOYMENT**")
    else:
        st.markdown("⬜ Rover deployment")
        
with col4:
    if st.session_state.rover_deployed and st.session_state.mission_phase == "ROVER DEPLOYED":
        st.markdown("✅ **MARS LANDING**")
    else:
        st.markdown("⬜ Mars landing")

# Final mission status
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 50px;'>
    <h1 style='color: #00ff9d; font-size: 72px;'>🇰🇪</h1>
    <h2>"Kenya reaching for the stars"</h2>
    <p style='color: #888;'>KSEF Space Science Division • Mission Control Center • 2026</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 2 seconds for real-time effect
time.sleep(2)
st.rerun()