# 🌍 Kenya Climate Risk Monitor

### Multi-Hazard Satellite-Based Early Warning System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## 🎯 Overview

The Kenya Climate Risk Monitor is an integrated satellite-based system that monitors multiple environmental hazards simultaneously:

- 🌊 **Flood risk** (using Sentinel-1 radar data)
- 🌵 **Drought severity** (using Sentinel-2 vegetation indices)
- 🌡️ **Urban heat islands** (using Landsat 8 thermal data)
- 🌳 **Deforestation trends** (using multi-temporal analysis)

## 🛰️ Satellites Used

| Satellite | Hazard Monitored | Technology |
|-----------|------------------|------------|
| Sentinel-1 | Floods | Synthetic Aperture Radar (SAR) |
| Sentinel-2 | Drought, Deforestation | Multispectral (NDVI) |
| Landsat 8 | Urban Heat | Thermal Infrared |

## 🧠 How It Works

1. **Data Acquisition**: Download free satellite imagery from ESA and NASA
2. **Processing**: Calculate indices (NDVI, LST, flood extent)
3. **Integration**: Combine hazards into Composite Climate Risk Index
4. **Visualization**: Interactive dashboard for decision makers

## 📊 Climate Risk Index Formula
