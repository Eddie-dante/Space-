import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt

st.set_page_config(page_title="CIRS - Climate Intelligence System", layout="wide")
st.title("🌍 Climate Intelligence & Resilience System (CIRS)")

# Load dataset
data = pd.read_csv("data/climate_data.csv")

# ----------------------
# Build Flood Model
# ----------------------
data['Flood'] = np.where(data['Rainfall_mm']>40,1,0)
X_flood = data[['Rainfall_mm','Soil_Moisture','NDVI']]
y_flood = data['Flood']
flood_model = LogisticRegression()
flood_model.fit(X_flood,y_flood)

def predict_flood(rainfall, soil, ndvi):
    return flood_model.predict_proba([[rainfall, soil, ndvi]])[0][1]

# ----------------------
# Build Drought Model
# ----------------------
data['Drought'] = np.where((data['Rainfall_mm']<5) & (data['Soil_Moisture']<25),1,0)
X_drought = data[['Rainfall_mm','Temperature_C','Soil_Moisture']]
y_drought = data['Drought']
drought_model = LogisticRegression()
drought_model.fit(X_drought,y_drought)

def predict_drought(rainfall, temp, soil):
    return drought_model.predict_proba([[rainfall, temp, soil]])[0][1]

# ----------------------
# Smart Farming Functions
# ----------------------
def recommend_crop(soil_moisture, rainfall):
    if soil_moisture>50 and rainfall>30:
        return "Maize or Rice"
    elif soil_moisture>30 and rainfall>10:
        return "Beans or Sorghum"
    else:
        return "Drought-resistant crops like Millet or Cassava"

def irrigation_advice(soil_moisture):
    if soil_moisture<25:
        return "Irrigation required immediately"
    elif soil_moisture<40:
        return "Irrigation recommended soon"
    else:
        return "Soil moisture adequate"

# ----------------------
# Streamlit Dashboard
# ----------------------
menu = st.sidebar.selectbox(
    "Select Module",
    ["Flood Prediction","Drought Prediction","Smart Farming","Climate Trends"]
)

if menu=="Flood Prediction":
    st.header("🌧 Flood Risk Assessment")
    rainfall = st.number_input("Enter Rainfall (mm)",0.0,500.0)
    soil = st.number_input("Enter Soil Moisture (%)",0.0,100.0)
    ndvi = st.number_input("Enter NDVI",0.0,1.0)
    if st.button("Predict Flood Risk"):
        risk = predict_flood(rainfall,soil,ndvi)*100
        st.success(f"Flood Risk Probability: {risk:.2f}%")
        if risk>50:
            st.warning("⚠️ High Flood Risk! Take preventive measures.")
        else:
            st.info("Low Flood Risk.")

elif menu=="Drought Prediction":
    st.header("🌵 Drought Risk Assessment")
    rainfall = st.number_input("Enter Rainfall (mm)",0.0,500.0,key="drought_rain")
    temp = st.number_input("Enter Temperature (C)",0.0,50.0)
    soil = st.number_input("Enter Soil Moisture (%)",0.0,100.0,key="drought_soil")
    if st.button("Predict Drought Risk"):
        risk = predict_drought(rainfall,temp,soil)*100
        st.success(f"Drought Risk Probability: {risk:.2f}%")
        if risk>50:
            st.warning("⚠️ High Drought Risk! Plan water usage accordingly.")
        else:
            st.info("Low Drought Risk.")

elif menu=="Smart Farming":
    st.header("🌾 AI Farming Advisor")
    soil = st.number_input("Enter Soil Moisture (%)",0.0,100.0,key="farm_soil")
    rainfall = st.number_input("Enter Rainfall (mm)",0.0,500.0,key="farm_rain")
    if st.button("Get Recommendations"):
        crop = recommend_crop(soil,rainfall)
        irrigation = irrigation_advice(soil)
        st.success(f"Recommended Crop: {crop}")
        st.info(f"Irrigation Advice: {irrigation}")

elif menu=="Climate Trends":
    st.header("📊 Climate Data Visualization")
    st.line_chart(data[['Rainfall_mm','Temperature_C','Soil_Moisture']])
