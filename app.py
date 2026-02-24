import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt

st.set_page_config(page_title="CIRS - Climate & Disaster System", layout="wide")
st.title("🌍 Climate & Disaster Resilience System (CIRS)")

# Load dataset
data = pd.read_csv("data/climate_data.csv")

# ----------------------
# Flood Model
# ----------------------
data['Flood'] = np.where(data['Rainfall_mm']>40,1,0)
flood_X = data[['Rainfall_mm','Soil_Moisture','NDVI']]
flood_y = data['Flood']
flood_model = LogisticRegression()
flood_model.fit(flood_X, flood_y)

def predict_flood(rainfall, soil, ndvi):
    return flood_model.predict_proba([[rainfall, soil, ndvi]])[0][1]

# ----------------------
# Drought Model
# ----------------------
data['Drought'] = np.where((data['Rainfall_mm']<5) & (data['Soil_Moisture']<25),1,0)
drought_X = data[['Rainfall_mm','Temperature_C','Soil_Moisture']]
drought_y = data['Drought']
drought_model = LogisticRegression()
drought_model.fit(drought_X, drought_y)

def predict_drought(rainfall, temp, soil):
    return drought_model.predict_proba([[rainfall, temp, soil]])[0][1]

# ----------------------
# Quick Water Advice
# ----------------------
def water_advice(soil_moisture):
    if soil_moisture < 25:
        return "Water immediately"
    elif soil_moisture < 40:
        return "Irrigation recommended soon"
    else:
        return "Water level adequate"

# ----------------------
# Streamlit Dashboard
# ----------------------
menu = st.sidebar.selectbox(
    "Select Module",
    ["Flood Prediction","Drought Prediction","Climate Trends","Water Advice"]
)

if menu=="Flood Prediction":
    st.header("🌧 Flood Risk Assessment")
    rainfall = st.number_input("Rainfall (mm)", 0.0, 500.0)
    soil = st.number_input("Soil Moisture (%)", 0.0, 100.0)
    ndvi = st.number_input("NDVI", 0.0, 1.0)
    if st.button("Predict Flood Risk"):
        risk = predict_flood(rainfall, soil, ndvi)*100
        st.success(f"Flood Risk: {risk:.2f}%")
        if risk > 50:
            st.warning("⚠️ High flood risk! Take precautions.")
        else:
            st.info("Low flood risk.")

elif menu=="Drought Prediction":
    st.header("🌵 Drought Risk Assessment")
    rainfall = st.number_input("Rainfall (mm)", 0.0, 500.0, key="drought_rain")
    temp = st.number_input("Temperature (°C)", 0.0, 50.0)
    soil = st.number_input("Soil Moisture (%)", 0.0, 100.0, key="drought_soil")
    if st.button("Predict Drought Risk"):
        risk = predict_drought(rainfall, temp, soil)*100
        st.success(f"Drought Risk: {risk:.2f}%")
        if risk > 50:
            st.warning("⚠️ High drought risk! Manage water resources.")
        else:
            st.info("Low drought risk.")

elif menu=="Climate Trends":
    st.header("📊 Climate Data Visualization")
    st.line_chart(data[['Rainfall_mm','Temperature_C','Soil_Moisture']])

elif menu=="Water Advice":
    st.header("💧 Quick Water Advice")
    soil = st.number_input("Soil Moisture (%)", 0.0, 100.0, key="water_soil")
    advice = water_advice(soil)
    st.info(f"Recommendation: {advice}")
