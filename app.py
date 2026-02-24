import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="CIRS - Climate & Disaster System", layout="wide")
st.title("🌍 Climate & Disaster Resilience System (CIRS)")
st.caption("Satellite-Based Early Warning System for Kenya | SDG 11, 13, 6, 2")

# ======================
# GENERATE SAMPLE DATA (No external files needed!)
# ======================
@st.cache_data
def generate_sample_data():
    """Creates realistic climate data for demonstration"""
    dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30, 0, -1)]
    
    np.random.seed(42)  # For reproducible results
    rainfall = np.random.gamma(2, 10, 30).round(1)
    temperature = np.random.normal(28, 3, 30).round(1)
    soil_moisture = (50 + 20 * np.sin(np.linspace(0, 3*np.pi, 30)) + np.random.normal(0, 5, 30)).round(1)
    ndvi = (0.5 + 0.2 * np.sin(np.linspace(0, 2*np.pi, 30)) + np.random.normal(0, 0.05, 30)).round(2)
    
    # Clip values to realistic ranges
    soil_moisture = np.clip(soil_moisture, 10, 90)
    ndvi = np.clip(ndvi, 0.1, 0.9)
    
    df = pd.DataFrame({
        'Date': dates,
        'Rainfall_mm': rainfall,
        'Temperature_C': temperature,
        'Soil_Moisture': soil_moisture,
        'NDVI': ndvi
    })
    return df

# Load the data
data = generate_sample_data()

# ======================
# FLOOD PREDICTION MODEL
# ======================
# Define flood risk based on rainfall and soil moisture
data['Flood_Risk'] = ((data['Rainfall_mm'] > 40) | 
                      ((data['Rainfall_mm'] > 25) & (data['Soil_Moisture'] > 60))).astype(int)

# Train flood model
flood_features = ['Rainfall_mm', 'Soil_Moisture', 'NDVI']
X_flood = data[flood_features]
y_flood = data['Flood_Risk']

try:
    flood_model = LogisticRegression()
    flood_model.fit(X_flood, y_flood)
    model_ready = True
except:
    model_ready = False
    st.warning("⚠️ Using rule-based predictions (model training failed)")

def predict_flood(rainfall, soil, ndvi):
    """Flood risk prediction"""
    if model_ready:
        prob = flood_model.predict_proba([[rainfall, soil, ndvi]])[0][1]
        return prob * 100
    else:
        # Fallback rule-based prediction
        risk = 0
        if rainfall > 40:
            risk += 60
        elif rainfall > 25:
            risk += 30
        
        if soil > 70:
            risk += 30
        elif soil > 50:
            risk += 15
            
        if ndvi < 0.3:
            risk += 10
            
        return min(risk, 98)

# ======================
# DROUGHT PREDICTION MODEL
# ======================
data['Drought_Risk'] = ((data['Rainfall_mm'] < 5) & 
                        (data['Soil_Moisture'] < 25) & 
                        (data['Temperature_C'] > 30)).astype(int)

def predict_drought(rainfall, temp, soil):
    """Drought risk prediction"""
    risk = 0
    if rainfall < 5:
        risk += 50
    elif rainfall < 15:
        risk += 25
        
    if soil < 20:
        risk += 30
    elif soil < 35:
        risk += 15
        
    if temp > 32:
        risk += 20
    elif temp > 28:
        risk += 10
        
    return min(risk, 95)

# ======================
# DISASTER SEVERITY INDEX (NEW!)
# ======================
def calculate_disaster_index(rainfall, temp, soil, ndvi):
    """Combines multiple factors into one risk score"""
    flood_score = predict_flood(rainfall, soil, ndvi) / 100
    drought_score = predict_drought(rainfall, temp, soil) / 100
    
    # Weighted combination
    combined = (flood_score * 0.5 + drought_score * 0.5) * 100
    
    if combined > 70:
        return "🔴 SEVERE", combined
    elif combined > 40:
        return "🟡 MODERATE", combined
    else:
        return "🟢 LOW", combined

# ======================
# WATER RESOURCE ADVICE
# ======================
def water_management_advice(soil_moisture, rainfall, region_type="urban"):
    """Provides water management recommendations"""
    if soil_moisture < 20:
        if region_type == "urban":
            return "🏙️ Water rationing recommended. Harvest rainwater when available."
        else:
            return "🌾 Irrigation critical. Consider drought-resistant crops."
    elif soil_moisture < 40:
        return "💧 Monitor water levels. Plan for potential shortage."
    elif soil_moisture > 80 and rainfall > 30:
        return "⚠️ Excess water. Check drainage systems for flooding."
    else:
        return "✅ Water levels adequate."

# ======================
# STREAMLIT UI
# ======================
st.sidebar.image("https://img.icons8.com/fluency/96/earth-planet.png", width=80)
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Select Module",
    ["🏠 Dashboard", "🌧 Flood Prediction", "🌵 Drought Prediction", 
     "💧 Water Resources", "📊 Climate Trends", "🚨 Disaster Risk Map"]
)

region_type = st.sidebar.selectbox("Region Type", ["urban", "rural"])

# ======================
# DASHBOARD HOME
# ======================
if menu == "🏠 Dashboard":
    st.header("🚨 Real-Time Climate Intelligence")
    
    col1, col2, col3, col4 = st.columns(4)
    
    latest = data.iloc[-1]
    
    with col1:
        st.metric("Current Rainfall", f"{latest['Rainfall_mm']} mm", 
                  delta=f"{latest['Rainfall_mm'] - data['Rainfall_mm'].iloc[-2]:.1f}")
    with col2:
        st.metric("Temperature", f"{latest['Temperature_C']}°C")
    with col3:
        st.metric("Soil Moisture", f"{latest['Soil_Moisture']}%")
    with col4:
        st.metric("Vegetation Index", f"{latest['NDVI']}")
    
    st.subheader("📡 Satellite Data Feed (Last 30 Days)")
    st.line_chart(data.set_index('Date')[['Rainfall_mm', 'Temperature_C', 'Soil_Moisture']])
    
    # Quick risk assessment
    severity, score = calculate_disaster_index(
        latest['Rainfall_mm'], 
        latest['Temperature_C'], 
        latest['Soil_Moisture'], 
        latest['NDVI']
    )
    
    st.subheader(f"Current Disaster Risk: {severity} ({score:.1f}%)")
    
    if score > 50:
        st.warning("⚠️ Take precautionary measures immediately!")
    
    st.info("""
    **About CIRS:**
    - Uses satellite data for climate monitoring
    - Supports SDG 11 (Cities), 13 (Climate), 6 (Water), 2 (Zero Hunger)
    - AI-powered early warning system
    """)

# ======================
# FLOOD PREDICTION
# ======================
elif menu == "🌧 Flood Prediction":
    st.header("🌧 Flood Risk Assessment")
    st.caption("Predicts flood probability using rainfall, soil moisture, and vegetation data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rainfall = st.slider("Rainfall (mm)", 0.0, 200.0, 25.0)
        soil = st.slider("Soil Moisture (%)", 0.0, 100.0, 45.0)
        ndvi = st.slider("NDVI (Vegetation Index)", 0.0, 1.0, 0.5)
    
    with col2:
        st.subheader("Risk Analysis")
        risk = predict_flood(rainfall, soil, ndvi)
        
        # Visual indicator
        if risk > 70:
            st.error(f"🔴 HIGH FLOOD RISK: {risk:.1f}%")
            st.markdown("""
            **Immediate Actions:**
            - Evacuate low-lying areas
            - Move livestock to higher ground
            - Prepare emergency kits
            """)
        elif risk > 40:
            st.warning(f"🟡 MODERATE FLOOD RISK: {risk:.1f}%")
            st.markdown("""
            **Precautionary Measures:**
            - Monitor water levels
            - Clear drainage systems
            - Stay tuned for updates
            """)
        else:
            st.success(f"🟢 LOW FLOOD RISK: {risk:.1f}%")
        
        # Gauge chart
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.barh([0], [risk], color=['red' if risk>70 else 'orange' if risk>40 else 'green'])
        ax.set_xlim(0, 100)
        ax.set_yticks([])
        ax.set_xlabel("Risk Percentage")
        st.pyplot(fig)

# ======================
# DROUGHT PREDICTION
# ======================
elif menu == "🌵 Drought Prediction":
    st.header("🌵 Drought Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rainfall = st.slider("Rainfall (mm)", 0.0, 200.0, 10.0, key="d_rain")
        temp = st.slider("Temperature (°C)", 15.0, 45.0, 32.0)
        soil = st.slider("Soil Moisture (%)", 0.0, 100.0, 20.0, key="d_soil")
    
    with col2:
        risk = predict_drought(rainfall, temp, soil)
        
        if risk > 70:
            st.error(f"🔴 SEVERE DROUGHT RISK: {risk:.1f}%")
            st.markdown("""
            **Critical Actions:**
            - Emergency water distribution
            - Livestock feed intervention
            - Water trucking activation
            """)
        elif risk > 40:
            st.warning(f"🟡 MODERATE DROUGHT RISK: {risk:.1f}%")
            st.markdown("""
            **Preparedness:**
            - Water conservation
            - Early planting of drought-resistant crops
            - Rainwater harvesting
            """)
        else:
            st.success(f"🟢 LOW DROUGHT RISK: {risk:.1f}%")

# ======================
# WATER RESOURCES
# ======================
elif menu == "💧 Water Resources":
    st.header("💧 Water Resource Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        soil = st.slider("Current Soil Moisture (%)", 0.0, 100.0, 35.0)
        rainfall = st.slider("Recent Rainfall (mm)", 0.0, 200.0, 15.0)
        
    with col2:
        advice = water_management_advice(soil, rainfall, region_type)
        st.info(advice)
        
        # Water availability index
        availability = min(100, (soil / 50) * 70 + (rainfall / 100) * 30)
        
        if availability < 30:
            st.error(f"Water Scarcity Index: {availability:.1f}% - CRITICAL")
        elif availability < 60:
            st.warning(f"Water Scarcity Index: {availability:.1f}% - MODERATE")
        else:
            st.success(f"Water Availability: {availability:.1f}% - ADEQUATE")
    
    st.subheader("Rainwater Harvesting Potential")
    roof_area = st.number_input("Roof Area (m²)", 50, 1000, 100)
    monthly_rainfall = data['Rainfall_mm'].mean()
    
    harvest_potential = (roof_area * monthly_rainfall / 1000) * 1000  # liters
    st.metric("Monthly Harvest Potential", f"{harvest_potential:.0f} liters")

# ======================
# CLIMATE TRENDS
# ======================
elif menu == "📊 Climate Trends":
    st.header("📊 Historical Climate Data")
    
    metric = st.selectbox("Select Metric", ["Rainfall_mm", "Temperature_C", "Soil_Moisture", "NDVI"])
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data['Date'], data[metric], marker='o', linestyle='-')
    ax.set_xlabel("Date")
    ax.set_ylabel(metric)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average", f"{data[metric].mean():.1f}")
    with col2:
        st.metric("Maximum", f"{data[metric].max():.1f}")
    with col3:
        st.metric("Minimum", f"{data[metric].min():.1f}")

# ======================
# DISASTER RISK MAP
# ======================
elif menu == "🚨 Disaster Risk Map":
    st.header("🚨 Regional Disaster Risk Assessment")
    
    regions = ["Nairobi", "Mombasa", "Kisumu", "Garissa", "Turkana"]
    risks = []
    
    for region in regions:
        # Simulate different risks per region
        if region in ["Garissa", "Turkana"]:
            risk = np.random.uniform(60, 90)  # High drought risk
        elif region in ["Kisumu", "Mombasa"]:
            risk = np.random.uniform(50, 85)  # High flood risk
        else:
            risk = np.random.uniform(20, 50)  # Moderate risk
            
        risks.append(risk)
    
    risk_df = pd.DataFrame({
        "Region": regions,
        "Risk Level": risks
    })
    
    # Color code
    def color_risk(val):
        if val > 70:
            return 'background-color: red'
        elif val > 40:
            return 'background-color: orange'
        else:
            return 'background-color: green'
    
    st.dataframe(risk_df.style.applymap(color_risk, subset=['Risk Level']))
    
    st.subheader("Priority Actions by Region")
    for i, region in enumerate(regions):
        if risks[i] > 70:
            st.error(f"{region}: IMMEDIATE INTERVENTION NEEDED")
        elif risks[i] > 40:
            st.warning(f"{region}: Prepare response teams")
        else:
            st.success(f"{region}: Monitor regularly")
