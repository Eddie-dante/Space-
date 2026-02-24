import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import folium
from streamlit_folium import folium_static
from folium import plugins
import geopandas as gpd
from shapely.geometry import Point, Polygon
import json

# ============================================
# PAGE CONFIG - Professional Space Agency Look
# ============================================
st.set_page_config(
    page_title="SATGUARD-KE | Kenya Space Science",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for space theme with enhanced map styling
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
    /* Map container styling */
    .map-container {
        border: 2px solid #00FF00;
        border-radius: 10px;
        padding: 5px;
        background: rgba(0,0,0,0.3);
    }
    /* Layer control styling */
    .layer-control {
        background: rgba(0,0,0,0.8);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00FF00;
        margin: 10px 0;
    }
    /* Water body animation */
    @keyframes waterPulse {
        0% { opacity: 0.7; }
        50% { opacity: 0.9; }
        100% { opacity: 0.7; }
    }
    .water-body {
        animation: waterPulse 3s infinite;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ENHANCED GEOGRAPHIC DATA GENERATION
# ============================================

class GeographicDataGenerator:
    """Generates realistic geographic and satellite data for any location"""
    
    def __init__(self):
        self.continents = {
            "Africa": {
                "countries": {
                    "Kenya": {"lat": -1.28, "lon": 36.82, "zoom": 6},
                    "Tanzania": {"lat": -6.37, "lon": 34.89, "zoom": 6},
                    "Uganda": {"lat": 1.37, "lon": 32.29, "zoom": 7},
                    "Ethiopia": {"lat": 9.15, "lon": 40.49, "zoom": 6},
                    "South Africa": {"lat": -30.56, "lon": 22.94, "zoom": 5},
                    "Egypt": {"lat": 26.82, "lon": 30.80, "zoom": 6},
                    "Nigeria": {"lat": 9.08, "lon": 8.68, "zoom": 6},
                    "Morocco": {"lat": 31.79, "lon": -7.09, "zoom": 6},
                    "Ghana": {"lat": 7.95, "lon": -1.02, "zoom": 7},
                    "Rwanda": {"lat": -1.94, "lon": 29.87, "zoom": 8}
                }
            },
            "Asia": {
                "countries": {
                    "India": {"lat": 20.59, "lon": 78.96, "zoom": 5},
                    "China": {"lat": 35.86, "lon": 104.19, "zoom": 4},
                    "Japan": {"lat": 36.20, "lon": 138.25, "zoom": 6},
                    "Indonesia": {"lat": -0.79, "lon": 113.92, "zoom": 5}
                }
            },
            "Europe": {
                "countries": {
                    "UK": {"lat": 55.38, "lon": -3.44, "zoom": 6},
                    "Germany": {"lat": 51.17, "lon": 10.45, "zoom": 6},
                    "France": {"lat": 46.23, "lon": 2.21, "zoom": 6},
                    "Italy": {"lat": 41.87, "lon": 12.57, "zoom": 6}
                }
            },
            "North America": {
                "countries": {
                    "USA": {"lat": 37.09, "lon": -95.71, "zoom": 4},
                    "Canada": {"lat": 56.13, "lon": -106.35, "zoom": 4},
                    "Mexico": {"lat": 23.63, "lon": -102.55, "zoom": 5}
                }
            },
            "South America": {
                "countries": {
                    "Brazil": {"lat": -14.24, "lon": -51.93, "zoom": 5},
                    "Argentina": {"lat": -38.42, "lon": -63.62, "zoom": 5},
                    "Peru": {"lat": -9.19, "lon": -75.02, "zoom": 6}
                }
            },
            "Australia": {
                "countries": {
                    "Australia": {"lat": -25.27, "lon": 133.78, "zoom": 4},
                    "New Zealand": {"lat": -40.90, "lon": 174.89, "zoom": 6}
                }
            }
        }
        
    def generate_water_bodies(self, center_lat, center_lon, radius_km=100):
        """Generate realistic water bodies (lakes, rivers, dams) for any location"""
        water_bodies = []
        
        # Major lakes
        num_lakes = random.randint(3, 8)
        for i in range(num_lakes):
            lake_size = random.uniform(2, 15)  # km radius
            water_bodies.append({
                'type': 'lake',
                'name': f"Lake {chr(65+i)}",
                'lat': center_lat + random.uniform(-2, 2),
                'lon': center_lon + random.uniform(-2, 2),
                'radius_km': lake_size,
                'depth_m': random.uniform(5, 200),
                'water_quality': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                'surface_temp_c': random.uniform(18, 30),
                'chlorophyll_mgm3': round(random.uniform(0.1, 10), 2)
            })
        
        # Rivers (as line features)
        num_rivers = random.randint(5, 15)
        for i in range(num_rivers):
            points = []
            start_lat = center_lat + random.uniform(-3, 3)
            start_lon = center_lon + random.uniform(-3, 3)
            
            # Create meandering river
            for j in range(random.randint(5, 15)):
                points.append([
                    start_lat + j * random.uniform(-0.2, 0.2),
                    start_lon + j * random.uniform(-0.2, 0.2) + np.sin(j) * 0.1
                ])
            
            water_bodies.append({
                'type': 'river',
                'name': f"{chr(65+i)} River",
                'coordinates': points,
                'length_km': random.uniform(10, 500),
                'width_m': random.uniform(10, 500),
                'flow_rate_m3s': random.uniform(10, 1000)
            })
        
        # Small water bodies (ponds, reservoirs)
        num_small = random.randint(20, 50)
        for i in range(num_small):
            water_bodies.append({
                'type': 'small_water',
                'name': f"Pond/Reservoir {i+1}",
                'lat': center_lat + random.uniform(-5, 5),
                'lon': center_lon + random.uniform(-5, 5),
                'area_ha': random.uniform(0.1, 50),
                'purpose': random.choice(['Irrigation', 'Drinking', 'Livestock', 'Recreation'])
            })
        
        return water_bodies
    
    def generate_vegetation(self, center_lat, center_lon, radius_km=100):
        """Generate vegetation data with various indices"""
        vegetation_data = []
        
        # Grid of vegetation points
        grid_size = 20
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center_lat - 2 + (i * 4 / grid_size)
                lon = center_lon - 2 + (j * 4 / grid_size)
                
                # Calculate NDVI (Normalized Difference Vegetation Index)
                ndvi = random.uniform(-0.2, 0.9)
                evi = random.uniform(-0.1, 1.0)  # Enhanced Vegetation Index
                
                vegetation_data.append({
                    'lat': lat,
                    'lon': lon,
                    'ndvi': round(ndvi, 3),
                    'evi': round(evi, 3),
                    'savi': round(random.uniform(-0.3, 1.2), 3),  # Soil Adjusted VI
                    'vegetation_type': self.classify_vegetation(ndvi, evi),
                    'biomass_tons': round(random.uniform(0, 500), 1),
                    'health': random.choice(['Excellent', 'Good', 'Fair', 'Poor', 'Drought'])
                })
        
        return vegetation_data
    
    def classify_vegetation(self, ndvi, evi):
        """Classify vegetation type based on indices"""
        if ndvi > 0.6 and evi > 0.5:
            return 'Dense Forest'
        elif ndvi > 0.4 and evi > 0.3:
            return 'Moderate Forest'
        elif ndvi > 0.2 and evi > 0.1:
            return 'Grassland/Shrub'
        elif ndvi > 0.1:
            return 'Sparse Vegetation'
        elif ndvi > -0.1:
            return 'Barren/Urban'
        else:
            return 'Water/Snow'
    
    def generate_traffic_data(self, center_lat, center_lon):
        """Generate traffic and infrastructure data"""
        traffic_data = []
        
        # Major roads
        road_types = ['Highway', 'Primary Road', 'Secondary Road', 'Local Road']
        for i in range(random.randint(10, 20)):
            points = []
            start_lat = center_lat + random.uniform(-2, 2)
            start_lon = center_lon + random.uniform(-2, 2)
            
            for j in range(random.randint(3, 8)):
                points.append([
                    start_lat + j * random.uniform(-0.1, 0.1),
                    start_lon + j * random.uniform(-0.1, 0.1)
                ])
            
            traffic_data.append({
                'type': 'road',
                'name': f"Road {i+1}",
                'road_type': random.choice(road_types),
                'coordinates': points,
                'length_km': random.uniform(2, 50),
                'traffic_density': random.choice(['Low', 'Moderate', 'High', 'Very High']),
                'speed_limit_kmh': random.randint(30, 120),
                'lanes': random.randint(1, 4)
            })
        
        # Urban areas/cities
        num_cities = random.randint(5, 15)
        for i in range(num_cities):
            traffic_data.append({
                'type': 'urban',
                'name': f"City/Town {i+1}",
                'lat': center_lat + random.uniform(-2, 2),
                'lon': center_lon + random.uniform(-2, 2),
                'population': random.randint(1000, 5000000),
                'area_km2': random.uniform(5, 500),
                'night_lights_intensity': random.uniform(0, 100),
                'heat_island_effect_c': round(random.uniform(1, 5), 1)
            })
        
        # Air traffic
        num_flights = random.randint(5, 20)
        for i in range(num_flights):
            traffic_data.append({
                'type': 'aircraft',
                'flight_id': f"FL{random.randint(100, 999)}",
                'lat': center_lat + random.uniform(-3, 3),
                'lon': center_lon + random.uniform(-3, 3),
                'altitude_ft': random.randint(25000, 40000),
                'speed_knots': random.randint(400, 550),
                'heading': random.randint(0, 360),
                'aircraft_type': random.choice(['B737', 'A320', 'B787', 'A380', 'C172'])
            })
        
        return traffic_data
    
    def generate_urban_heat_islands(self, center_lat, center_lon):
        """Generate urban heat island data"""
        heat_islands = []
        
        for i in range(random.randint(3, 8)):
            heat_islands.append({
                'lat': center_lat + random.uniform(-1, 1),
                'lon': center_lon + random.uniform(-1, 1),
                'temperature_anomaly_c': round(random.uniform(2, 8), 1),
                'area_km2': random.uniform(1, 50),
                'building_density': random.choice(['Low', 'Medium', 'High']),
                'green_space_percent': random.randint(5, 40)
            })
        
        return heat_islands

# ============================================
# ENHANCED MAP CREATION
# ============================================

def create_interactive_map(center_lat, center_lon, zoom_start, selected_layers):
    """Create folium map with multiple layers"""
    
    # Base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='CartoDB dark_matter',  # Dark theme for space agency look
        attr='SATGUARD-KE'
    )
    
    # Add different tile layers
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     attr='Esri', name='Satellite Imagery').add_to(m)
    
    # Initialize data generator
    generator = GeographicDataGenerator()
    
    # ============================================
    # LAYER 1: WATER BODIES (Most detailed)
    # ============================================
    if 'water' in selected_layers:
        water_layer = folium.FeatureGroup(name='💧 Water Bodies', show=True)
        
        water_bodies = generator.generate_water_bodies(center_lat, center_lon)
        
        for water in water_bodies:
            if water['type'] == 'lake':
                # Lakes as circles with gradient
                folium.Circle(
                    location=[water['lat'], water['lon']],
                    radius=water['radius_km'] * 1000,  # Convert to meters
                    popup=folium.Popup(
                        f"<b>{water['name']}</b><br>"
                        f"Type: Lake<br>"
                        f"Depth: {water['depth_m']}m<br>"
                        f"Water Quality: {water['water_quality']}<br>"
                        f"Surface Temp: {water['surface_temp_c']}°C<br>"
                        f"Chlorophyll: {water['chlorophyll_mgm3']} mg/m³",
                        max_width=300
                    ),
                    tooltip=water['name'],
                    color='#00FFFF',
                    weight=1,
                    fill=True,
                    fillColor='#0066CC',
                    fillOpacity=0.6,
                    className='water-body'
                ).add_to(water_layer)
                
            elif water['type'] == 'river':
                # Rivers as polylines
                folium.PolyLine(
                    locations=water['coordinates'],
                    popup=folium.Popup(
                        f"<b>{water['name']}</b><br>"
                        f"Length: {water['length_km']} km<br>"
                        f"Width: {water['width_m']} m<br>"
                        f"Flow Rate: {water['flow_rate_m3s']} m³/s",
                        max_width=300
                    ),
                    tooltip=water['name'],
                    color='#0099FF',
                    weight=3,
                    opacity=0.8
                ).add_to(water_layer)
                
            elif water['type'] == 'small_water':
                # Small water bodies as smaller markers
                folium.CircleMarker(
                    location=[water['lat'], water['lon']],
                    radius=3,
                    popup=folium.Popup(
                        f"<b>{water['name']}</b><br>"
                        f"Area: {water['area_ha']} ha<br>"
                        f"Purpose: {water['purpose']}",
                        max_width=200
                    ),
                    tooltip=water['name'],
                    color='#33CCFF',
                    weight=1,
                    fill=True,
                    fillColor='#33CCFF',
                    fillOpacity=0.8
                ).add_to(water_layer)
        
        water_layer.add_to(m)
    
    # ============================================
    # LAYER 2: VEGETATION
    # ============================================
    if 'vegetation' in selected_layers:
        veg_layer = folium.FeatureGroup(name='🌿 Vegetation Index', show=True)
        
        vegetation = generator.generate_vegetation(center_lat, center_lon)
        
        # Color map for NDVI
        for veg in vegetation:
            # Color based on NDVI
            if veg['ndvi'] > 0.6:
                color = '#006400'  # Dark green - dense forest
            elif veg['ndvi'] > 0.4:
                color = '#228B22'  # Forest green
            elif veg['ndvi'] > 0.2:
                color = '#32CD32'  # Lime green - grassland
            elif veg['ndvi'] > 0.1:
                color = '#ADFF2F'  # Light green - sparse
            elif veg['ndvi'] > -0.1:
                color = '#8B7355'  # Brown - barren
            else:
                color = '#4169E1'  # Blue - water
                
            folium.CircleMarker(
                location=[veg['lat'], veg['lon']],
                radius=5,
                popup=folium.Popup(
                    f"<b>Vegetation Analysis</b><br>"
                    f"NDVI: {veg['ndvi']}<br>"
                    f"EVI: {veg['evi']}<br>"
                    f"SAVI: {veg['savi']}<br>"
                    f"Type: {veg['vegetation_type']}<br>"
                    f"Biomass: {veg['biomass_tons']} tons<br>"
                    f"Health: {veg['health']}",
                    max_width=250
                ),
                tooltip=f"NDVI: {veg['ndvi']}",
                color=color,
                weight=1,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(veg_layer)
        
        veg_layer.add_to(m)
    
    # ============================================
    # LAYER 3: TRAFFIC & INFRASTRUCTURE
    # ============================================
    if 'traffic' in selected_layers:
        traffic_layer = folium.FeatureGroup(name='🚦 Traffic & Infrastructure', show=True)
        
        traffic_data = generator.generate_traffic_data(center_lat, center_lon)
        
        for item in traffic_data:
            if item['type'] == 'road':
                # Color by traffic density
                if item['traffic_density'] == 'Very High':
                    color = '#FF0000'  # Red
                elif item['traffic_density'] == 'High':
                    color = '#FF4500'  # Orange-Red
                elif item['traffic_density'] == 'Moderate':
                    color = '#FFA500'  # Orange
                else:
                    color = '#FFFF00'  # Yellow
                
                folium.PolyLine(
                    locations=item['coordinates'],
                    popup=folium.Popup(
                        f"<b>{item['name']}</b><br>"
                        f"Type: {item['road_type']}<br>"
                        f"Length: {item['length_km']} km<br>"
                        f"Traffic: {item['traffic_density']}<br>"
                        f"Speed Limit: {item['speed_limit_kmh']} km/h<br>"
                        f"Lanes: {item['lanes']}",
                        max_width=250
                    ),
                    tooltip=f"{item['name']} - {item['traffic_density']} traffic",
                    color=color,
                    weight=4,
                    opacity=0.8
                ).add_to(traffic_layer)
                
            elif item['type'] == 'urban':
                # Urban areas as larger circles
                size = np.log10(item['population']) * 2
                folium.Circle(
                    location=[item['lat'], item['lon']],
                    radius=size * 500,
                    popup=folium.Popup(
                        f"<b>{item['name']}</b><br>"
                        f"Population: {item['population']:,}<br>"
                        f"Area: {item['area_km2']} km²<br>"
                        f"Night Lights Intensity: {item['night_lights_intensity']}<br>"
                        f"Heat Island Effect: +{item['heat_island_effect_c']}°C",
                        max_width=250
                    ),
                    tooltip=item['name'],
                    color='#FFD700',
                    weight=1,
                    fill=True,
                    fillColor='#FFD700',
                    fillOpacity=0.3
                ).add_to(traffic_layer)
                
            elif item['type'] == 'aircraft':
                # Aircraft as plane icons
                folium.Marker(
                    location=[item['lat'], item['lon']],
                    popup=folium.Popup(
                        f"<b>Flight {item['flight_id']}</b><br>"
                        f"Aircraft: {item['aircraft_type']}<br>"
                        f"Altitude: {item['altitude_ft']:,} ft<br>"
                        f"Speed: {item['speed_knots']} knots<br>"
                        f"Heading: {item['heading']}°",
                        max_width=200
                    ),
                    tooltip=f"Flight {item['flight_id']}",
                    icon=folium.Icon(icon='plane', color='blue', prefix='fa')
                ).add_to(traffic_layer)
        
        traffic_layer.add_to(m)
    
    # ============================================
    # LAYER 4: URBAN HEAT ISLANDS
    # ============================================
    if 'heat' in selected_layers:
        heat_layer = folium.FeatureGroup(name='🌡️ Urban Heat Islands', show=True)
        
        heat_islands = generator.generate_urban_heat_islands(center_lat, center_lon)
        
        for heat in heat_islands:
            # Color based on temperature anomaly
            if heat['temperature_anomaly_c'] > 6:
                color = '#8B0000'  # Dark red
            elif heat['temperature_anomaly_c'] > 4:
                color = '#FF0000'  # Red
            elif heat['temperature_anomaly_c'] > 2:
                color = '#FF4500'  # Orange-Red
            else:
                color = '#FFA500'  # Orange
            
            folium.Circle(
                location=[heat['lat'], heat['lon']],
                radius=heat['area_km2'] * 200,
                popup=folium.Popup(
                    f"<b>Urban Heat Island</b><br>"
                    f"Temperature Anomaly: +{heat['temperature_anomaly_c']}°C<br>"
                    f"Area: {heat['area_km2']} km²<br>"
                    f"Building Density: {heat['building_density']}<br>"
                    f"Green Space: {heat['green_space_percent']}%",
                    max_width=200
                ),
                tooltip=f"Heat Island: +{heat['temperature_anomaly_c']}°C",
                color=color,
                weight=1,
                fill=True,
                fillColor=color,
                fillOpacity=0.4
            ).add_to(heat_layer)
        
        heat_layer.add_to(m)
    
    # ============================================
    # LAYER 5: SATELLITE COVERAGE
    # ============================================
    if 'satellite' in selected_layers:
        sat_layer = folium.FeatureGroup(name='🛰️ Satellite Coverage', show=True)
        
        # Simulate satellite swaths
        for i in range(5):
            swath_center_lat = center_lat + random.uniform(-5, 5)
            swath_center_lon = center_lon + random.uniform(-5, 5)
            
            # Create swath polygon
            swath_points = [
                [swath_center_lat - 1, swath_center_lon - 2],
                [swath_center_lat - 1, swath_center_lon + 2],
                [swath_center_lat + 1, swath_center_lon + 2],
                [swath_center_lat + 1, swath_center_lon - 2],
                [swath_center_lat - 1, swath_center_lon - 2]
            ]
            
            folium.Polygon(
                locations=swath_points,
                popup=f"Satellite Swath {i+1}<br>Coverage width: 400km",
                tooltip=f"Satellite Pass {i+1}",
                color='#00FF00',
                weight=1,
                fill=True,
                fillColor='#00FF00',
                fillOpacity=0.1
            ).add_to(sat_layer)
        
        sat_layer.add_to(m)
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    # Add mouse position
    plugins.MousePosition().add_to(m)
    
    # Add measure tool
    plugins.MeasureControl(position='topleft').add_to(m)
    
    return m

# ============================================
# SPACE SCIENCE DATA GENERATION (Existing)
# ============================================
@st.cache_data(ttl=3600)
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
    
    # Space weather data
    space_weather = {
        "solar_wind_speed": round(random.uniform(350, 750), 1),
        "solar_wind_density": round(random.uniform(1, 20), 2),
        "bt": round(random.uniform(0, 30), 1),
        "bz": round(random.uniform(-20, 20), 1),
        "kp_index": round(random.uniform(0, 9), 1),
        "xray_flux": f"{random.uniform(1e-9, 1e-5):.2e}",
        "proton_flux": round(random.uniform(0.1, 100), 2),
        "electron_flux": round(random.uniform(100, 10000), 2),
        "radiation_belt": round(random.uniform(0.1, 5), 2),
        "aurora_oval": random.choice(["Quiet", "Active", "Storm"]),
    }
    
    # Debris tracking
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
    
    solar_wind = [random.uniform(350, 750) for _ in range(24)]
    kp_values = [random.uniform(0, 9) for _ in range(24)]
    radiation = [random.uniform(0.1, 5) for _ in range(24)]
    
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
    """Simulates satellite pass predictions for any location"""
    passes = []
    now = datetime.now()
    
    for i in range(3):
        pass_time = now + timedelta(hours=random.randint(1, 12))
        duration = random.randint(5, 15)
        max_elevation = random.randint(15, 85)
        
        passes.append({
            "satellite": sat_name,
            "aos": pass_time.strftime("%H:%M:%S"),
            "los": (pass_time + timedelta(minutes=duration)).strftime("%H:%M:%S"),
            "duration": duration,
            "max_elevation": max_elevation,
            "frequency": random.choice(['UHF', 'VHF', 'S-Band', 'X-Band']),
            "data_rate": f"{random.randint(100, 1200)} kbps"
        })
    
    return passes

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
# MAIN DASHBOARD
# ============================================
st.title("🛰️ **SATGUARD-KE**")
st.markdown("### *Kenya's Satellite-Based Space Weather & Early Warning System*")
st.markdown("### *Enhanced Geographic Intelligence Platform*")
st.markdown("---")

# Initialize data generator
geo_generator = GeographicDataGenerator()

# Get space data
space_data = generate_space_data()
historical_data = generate_historical_space_data()

# ============================================
# ENHANCED SIDEBAR - Geographic Selection
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=80)
    st.markdown("## **MISSION CONTROL**")
    st.markdown(f"**Last Update:** {space_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
    st.markdown("---")
    
    # Geographic Selection
    st.markdown("### 🌍 **Geographic Selection**")
    
    # Continent selection
    selected_continent = st.selectbox(
        "Select Continent",
        list(geo_generator.continents.keys())
    )
    
    # Country selection based on continent
    if selected_continent:
        countries = geo_generator.continents[selected_continent]["countries"]
        selected_country = st.selectbox(
            "Select Country",
            list(countries.keys())
        )
        
        # Location details
        country_data = countries[selected_country]
        st.markdown(f"**Capital/Coordinates:** {country_data['lat']:.2f}°, {country_data['lon']:.2f}°")
        
        # Custom location option
        st.markdown("---")
        st.markdown("### 🎯 **Custom Location**")
        use_custom = st.checkbox("Enter custom coordinates")
        
        if use_custom:
            custom_lat = st.number_input("Latitude", value=country_data['lat'], format="%.4f")
            custom_lon = st.number_input("Longitude", value=country_data['lon'], format="%.4f")
            zoom_level = st.slider("Zoom Level", min_value=3, max_value=18, value=country_data['zoom'])
        else:
            custom_lat = country_data['lat']
            custom_lon = country_data['lon']
            zoom_level = country_data['zoom']
    
    st.markdown("---")
    
    # Layer Selection
    st.markdown("### 🗺️ **Map Layers**")
    
    selected_layers = []
    
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("💧 Water Bodies", value=True):
            selected_layers.append('water')
        if st.checkbox("🌿 Vegetation", value=True):
            selected_layers.append('vegetation')
        if st.checkbox("🚦 Traffic", value=True):
            selected_layers.append('traffic')
    with col2:
        if st.checkbox("🌡️ Heat Islands", value=True):
            selected_layers.append('heat')
        if st.checkbox("🛰️ Satellite", value=True):
            selected_layers.append('satellite')
        if st.checkbox("🏭 Industrial", value=False):
            selected_layers.append('industrial')
    
    st.markdown("---")
    
    # Main menu selection
    menu = st.radio(
        "**SELECT MISSION**",
        ["🗺️ Geographic Intelligence",
         "🛰️ Space Weather", 
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
# PAGE 1: ENHANCED GEOGRAPHIC INTELLIGENCE
# ============================================
if menu == "🗺️ Geographic Intelligence":
    st.header("🗺️ **GEOGRAPHIC INTELLIGENCE PLATFORM**")
    st.markdown("*Multi-layer satellite-derived geographic analysis*")
    
    # Create tabs for different views
    map_tab, analysis_tab, stats_tab = st.tabs(["🗺️ Interactive Map", "📊 Analysis Tools", "📈 Statistics"])
    
    with map_tab:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        
        # Create and display the interactive map
        m = create_interactive_map(custom_lat, custom_lon, zoom_level, selected_layers)
        folium_static(m, width=1200, height=600)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Map Legend
        with st.expander("🗺️ Map Legend", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**💧 Water Bodies**")
                st.markdown("• 🟦 Lakes (Blue circles)")
                st.markdown("• 🔷 Rivers (Blue lines)")
                st.markdown("• 🔹 Ponds (Small blue dots)")
            
            with col2:
                st.markdown("**🌿 Vegetation**")
                st.markdown("• 🟢 Dense Forest (Dark green)")
                st.markdown("• 🟢 Forest (Green)")
                st.markdown("• 🟡 Grassland (Light green)")
                st.markdown("• 🟤 Barren (Brown)")
            
            with col3:
                st.markdown("**🚦 Traffic**")
                st.markdown("• 🔴 Very High Traffic")
                st.markdown("• 🟠 High Traffic")
                st.markdown("• 🟡 Moderate Traffic")
                st.markdown("• 🟢 Low Traffic")
                st.markdown("• ✈️ Aircraft")
            
            with col4:
                st.markdown("**🌡️ Heat Islands**")
                st.markdown("• 🔴 Extreme (+6°C+)")
                st.markdown("• 🔴 High (+4-6°C)")
                st.markdown("• 🟠 Moderate (+2-4°C)")
                st.markdown("• 🟡 Low (+0-2°C)")
    
    with analysis_tab:
        st.subheader("📊 Geographic Analysis Tools")
        
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Water Resource Assessment", "Vegetation Health Index", "Urban Development Analysis", 
             "Climate Impact Study", "Infrastructure Planning", "Disaster Risk Assessment"]
        )
        
        if analysis_type == "Water Resource Assessment":
            st.markdown("### 💧 Water Resource Assessment")
            
            # Generate water quality metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Water Bodies", random.randint(50, 200))
                st.metric("Total Water Area", f"{random.randint(1000, 5000)} km²")
            
            with col2:
                st.metric("Water Quality Index", random.randint(60, 95), 
                         f"{random.randint(-5, 5)} points")
                st.metric("Drinking Water Suitability", 
                         random.choice(["Excellent", "Good", "Fair", "Poor"]))
            
            with col3:
                st.metric("Irrigation Potential", f"{random.randint(40, 90)}%")
                st.metric("Flood Risk", random.choice(["Low", "Moderate", "High", "Severe"]))
            
            # Water quality chart
            water_params = pd.DataFrame({
                'Parameter': ['pH', 'Turbidity', 'Dissolved O2', 'Nitrates', 'Phosphates', 'Bacteria'],
                'Value': [random.uniform(6.5, 8.5), random.uniform(1, 10), 
                         random.uniform(5, 12), random.uniform(0.1, 5),
                         random.uniform(0.01, 1), random.uniform(0, 100)],
                'Unit': ['', 'NTU', 'mg/L', 'mg/L', 'mg/L', 'CFU/100mL']
            })
            
            st.dataframe(water_params, use_container_width=True)
            
        elif analysis_type == "Vegetation Health Index":
            st.markdown("### 🌿 Vegetation Health Analysis")
            
            # Generate vegetation metrics grid
            veg_data = []
            for i in range(10):
                for j in range(10):
                    veg_data.append({
                        'Grid': f"{chr(65+i)}{j+1}",
                        'NDVI': round(random.uniform(0.1, 0.9), 2),
                        'EVI': round(random.uniform(0.1, 1.0), 2),
                        'SAVI': round(random.uniform(0.1, 0.8), 2),
                        'Health': random.choice(['Excellent', 'Good', 'Fair', 'Poor'])
                    })
            
            veg_df = pd.DataFrame(veg_data)
            
            # Heatmap of NDVI
            fig = px.density_heatmap(
                veg_df, x='Grid', y='NDVI', z='NDVI',
                title="Vegetation Health Index Heatmap",
                color_continuous_scale="Greens"
            )
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
    with stats_tab:
        st.subheader("📈 Geographic Statistics")
        
        # Generate statistics for the selected area
        stats = {
            "Land Cover Distribution": {
                "Forest": random.randint(15, 40),
                "Grassland": random.randint(10, 30),
                "Agriculture": random.randint(10, 35),
                "Urban": random.randint(5, 25),
                "Water": random.randint(2, 15),
                "Barren": random.randint(5, 20)
            },
            "Climate Data": {
                "Avg Temperature": f"{random.uniform(15, 35):.1f}°C",
                "Annual Rainfall": f"{random.randint(500, 2000)} mm",
                "Humidity": f"{random.randint(40, 90)}%",
                "Solar Radiation": f"{random.randint(4, 8)} kWh/m²/day"
            },
            "Population Metrics": {
                "Population Density": f"{random.randint(10, 500)}/km²",
                "Urban Population": f"{random.randint(20, 80)}%",
                "Growth Rate": f"{random.uniform(0.5, 3.5):.1f}%"
            }
        }
        
        # Display statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌳 Land Cover")
            land_cover_df = pd.DataFrame(
                list(stats["Land Cover Distribution"].items()),
                columns=['Type', 'Percentage']
            )
            
            fig = px.pie(land_cover_df, values='Percentage', names='Type',
                        title="Land Cover Distribution",
                        color_discrete_sequence=px.colors.sequential.Greens)
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 🌡️ Climate Data")
            for key, value in stats["Climate Data"].items():
                st.metric(key, value)
        
        with col2:
            st.markdown("### 👥 Population Metrics")
            for key, value in stats["Population Metrics"].items():
                st.metric(key, value)
            
            # Time series of changes
            years = list(range(2015, 2026))
            urban_growth = [random.randint(20, 60) + i*0.5 for i in range(11)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years,
                y=urban_growth,
                mode='lines+markers',
                name='Urbanization Trend',
                line=dict(color='#FFD700', width=3)
            ))
            fig.update_layout(
                title="Urbanization Trend (2015-2026)",
                xaxis_title="Year",
                yaxis_title="Urban Population %",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 2: SPACE WEATHER (Enhanced with location context)
# ============================================
elif menu == "🛰️ Space Weather":
    st.header("🛰️ **SPACE WEATHER MONITORING**")
    st.markdown(f"*Real-time solar activity and cosmic radiation data for {selected_country}*")
    
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
        
        # Local impact
        st.subheader(f"📡 Impact on {selected_country}")
        local_impact = satellite_risk_assessment(
            space_data['weather']['radiation_belt'],
            space_data['weather']['solar_wind_speed'],
            space_data['weather']['kp_index']
        )
        st.metric("Local Satellite Risk", local_impact[0], f"{local_impact[1]}%")
    
    with col2:
        st.subheader("📈 24-Hour Space Weather Trends")
        
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

# ============================================
# PAGE 3: SATELLITE OPERATIONS (Enhanced)
# ============================================
elif menu == "📡 Satellite Operations":
    st.header("📡 **SATELLITE OPERATIONS CENTER**")
    st.markdown(f"*Real-time satellite tracking for {selected_country}*")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🛰️ Active Satellites")
        for sat in space_data['satellites']:
            with st.expander(f"**{sat['name']}**"):
                st.write(f"**Type:** {sat['type']}")
                st.write(f"**Altitude:** {sat['altitude']} km")
                st.write(f"**Inclination:** {sat['inclination']}°")
                st.write(f"**Status:** 🟢 Operational")
                
                # Next pass for selected location
                passes = calculate_satellite_pass(sat['name'], custom_lat, custom_lon)
                st.write(f"**Next Passes ({selected_country}):**")
                for p in passes:
                    st.write(f"  • {p['aos']} - {p['los']} ({p['duration']} min, {p['max_elevation']}° elev)")
    
    with col2:
        st.subheader("🚨 Space Debris Monitoring")
        
        st.metric("Total Tracked Debris", f"{space_data['debris']['total']:,}", 
                  f"+{random.randint(50, 200)}/day")
        st.metric("Near Misses (24h)", space_data['debris']['near_misses_24h'])
        st.metric("Critical Objects", space_data['debris']['critical_tracking'])
        
        risk_color = "red" if space_data['debris']['risk_level'] == "HIGH" else "orange" if space_data['debris']['risk_level'] == "MODERATE" else "green"
        st.markdown(f"**Collision Risk Level:** :{risk_color}[{space_data['debris']['risk_level']}]")
        
        if space_data['debris']['risk_level'] == "HIGH":
            st.error("⚠️ Multiple collision risks detected. Maneuvers recommended.")
        
        # Local impact
        st.subheader(f"📍 Impact on {selected_country}")
        local_debris_risk = random.choice(["Low", "Moderate", "High"])
        st.metric("Local Debris Risk", local_debris_risk)

# ============================================
# PAGE 4: KENYA MONITORING (Enhanced)
# ============================================
elif menu == "🌍 Kenya Monitoring":
    st.header("🌍 **KENYA FROM SPACE**")
    st.markdown("*Satellite-derived environmental data for Kenya*")
    
    # Generate Kenya-specific data
    def analyze_kenya_region():
        regions = {
            "Nairobi": {"lat": -1.28, "lon": 36.82, "risk": "Moderate", "population": 4.4e6},
            "Mombasa": {"lat": -4.04, "lon": 39.66, "risk": "High-Flood", "population": 1.2e6},
            "Kisumu": {"lat": -0.09, "lon": 34.75, "risk": "High-Flood", "population": 1.1e6},
            "Garissa": {"lat": -0.45, "lon": 39.65, "risk": "High-Drought", "population": 0.8e6},
            "Turkana": {"lat": 3.12, "lon": 35.60, "risk": "Extreme-Drought", "population": 0.9e6},
            "Mt Kenya": {"lat": -0.15, "lon": 37.30, "risk": "Low", "population": 0.1e6}
        }
        
        for region in regions:
            regions[region]["ndvi"] = round(random.uniform(0.2, 0.8), 2)
            regions[region]["soil_moisture"] = round(random.uniform(10, 80), 1)
            regions[region]["temperature"] = round(random.uniform(22, 38), 1)
            regions[region]["rainfall_7day"] = round(random.uniform(0, 60), 1)
            # Add water bodies
            regions[region]["water_bodies"] = random.randint(1, 20)
            regions[region]["water_quality"] = random.choice(["Good", "Fair", "Poor"])
        
        return regions
    
    kenya_regions = analyze_kenya_region()
    
    # Kenya map
    kenya_map = folium.Map(location=[-1.28, 36.82], zoom_start=6, 
                          tiles='CartoDB dark_matter')
    
    # Add regions
    for region, data in kenya_regions.items():
        # Color based on risk
        if "Extreme" in data["risk"] or "High" in data["risk"]:
            color = "red"
        elif "Moderate" in data["risk"]:
            color = "orange"
        else:
            color = "green"
        
        folium.Marker(
            [data["lat"], data["lon"]],
            popup=folium.Popup(
                f"<b>{region}</b><br>"
                f"Population: {data['population']:,.0f}<br>"
                f"NDVI: {data['ndvi']}<br>"
                f"Water Bodies: {data['water_bodies']}<br>"
                f"Water Quality: {data['water_quality']}<br>"
                f"Risk: {data['risk']}",
                max_width=300
            ),
            tooltip=region,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(kenya_map)
    
    # Add major water bodies (Lake Victoria, etc.)
    folium.Circle(
        location=[-1.0, 33.0],
        radius=50000,
        popup="Lake Victoria",
        tooltip="Lake Victoria",
        color='#00FFFF',
        fill=True,
        fillColor='#0066CC',
        fillOpacity=0.4
    ).add_to(kenya_map)
    
    st.subheader("🗺️ Kenya Regional Map")
    folium_static(kenya_map, width=1200, height=500)
    
    # Regional analysis
    st.subheader("📊 Regional Analysis")
    
    regions_df = pd.DataFrame([
        {
            "Region": region,
            "NDVI": data["ndvi"],
            "Soil Moisture %": data["soil_moisture"],
            "Temp °C": data["temperature"],
            "Rainfall (7d) mm": data["rainfall_7day"],
            "Water Bodies": data["water_bodies"],
            "Water Quality": data["water_quality"],
            "Risk Level": data["risk"]
        }
        for region, data in kenya_regions.items()
    ])
    
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

# ============================================
# PAGE 5: EARLY WARNING
# ============================================
elif menu == "🚨 Early Warning":
    st.header("🚨 **EARLY WARNING SYSTEM**")
    st.markdown(f"*Space-based disaster prediction for {selected_country}*")
    
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
        
        hf_quality = max(0, 100 - space_data['weather']['kp_index'] * 12)
        st.metric("HF Radio Quality", f"{hf_quality:.0f}%", 
                  "Degraded" if hf_quality < 60 else "Good")
        
        comms_quality = max(0, 100 - satellite_risk_assessment(
            space_data['weather']['radiation_belt'],
            space_data['weather']['solar_wind_speed'],
            space_data['weather']['kp_index']
        )[1]/2)
        st.metric("Satellite Communications", f"{comms_quality:.0f}%", 
                  "Signal degradation possible" if comms_quality < 70 else "Normal")
    
    st.markdown("---")
    st.subheader(f"⚠️ Active Warnings for {selected_country}")
    
    # Generate warnings based on location
    warnings = []
    
    if space_data['weather']['kp_index'] > 6:
        warnings.append(("🔴 SPACE WEATHER", "Severe geomagnetic storm - Possible communication blackouts"))
    
    if space_data['debris']['near_misses_24h'] > 3:
        warnings.append(("🟠 DEBRIS ALERT", "High collision risk for LEO satellites"))
    
    # Local warnings based on geographic data
    local_flood_risk = random.choice([True, False])
    local_drought_risk = random.choice([True, False])
    
    if local_flood_risk:
        warnings.append(("🌧 FLOOD RISK", "Heavy rainfall predicted in low-lying areas"))
    if local_drought_risk:
        warnings.append(("🌵 DROUGHT WATCH", "Below-average rainfall expected"))
    
    for warning in warnings[:5]:
        st.markdown(f"**{warning[0]}** - {warning[1]}")
    
    if not warnings:
        st.success("✅ No active warnings - Conditions normal")

# ============================================
# PAGE 6: RESEARCH DATA
# ============================================
elif menu == "📊 Research Data":
    st.header("📊 **SPACE SCIENCE RESEARCH**")
    st.markdown("*Data for scientific analysis and publication*")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Solar Activity", "Satellite Telemetry", 
                                      "Geographic Data", "Research Papers"])
    
    with tab1:
        st.subheader("Solar Cycle Analysis")
        
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
    
    with tab2:
        st.subheader("Satellite Telemetry Archive")
        
        telemetry = pd.DataFrame({
            'Timestamp': pd.date_range(start='2026-02-01', periods=10, freq='6H'),
            'Satellite': random.choices(['KENYA-SAT-1', 'CBMSAT-1', 'KSA-MONITOR'], k=10),
            'Temperature_C': [random.uniform(15, 35) for _ in range(10)],
            'Battery_V': [random.uniform(24, 29) for _ in range(10)],
            'Data_Rate_kbps': [random.randint(100, 1000) for _ in range(10)],
            'Errors_Count': [random.randint(0, 10) for _ in range(10)]
        })
        
        st.dataframe(telemetry, use_container_width=True)
        
        csv = telemetry.to_csv(index=False)
        st.download_button(
            label="📥 Download Telemetry Data (CSV)",
            data=csv,
            file_name="satellite_telemetry.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader(f"Geographic Data - {selected_country}")
        
        # Generate geographic research data
        geo_data = pd.DataFrame({
            'Parameter': ['Total Area', 'Water Bodies Count', 'Water Area', 'Forest Cover',
                         'Urban Area', 'Agricultural Land', 'Protected Areas'],
            'Value': [f"{random.randint(10000, 1000000)} km²",
                     str(random.randint(50, 500)),
                     f"{random.randint(100, 10000)} km²",
                     f"{random.randint(10, 60)}%",
                     f"{random.randint(5, 30)}%",
                     f"{random.randint(20, 70)}%",
                     f"{random.randint(5, 25)}%"]
        })
        
        st.dataframe(geo_data, use_container_width=True)
    
    with tab4:
        st.subheader("Research Publications")
        
        papers = [
            ("Space Weather Effects on Equatorial Satellites", "Journal of African Space Science, 2025"),
            ("Kenya's First Satellite: Lessons Learned", "African Journal of Science, 2024"),
            ("Debris Mitigation Strategies for Developing Space Nations", "Space Policy, 2024"),
            ("Machine Learning for Space Weather Prediction", "AI in Aerospace, 2025"),
            ("Water Resource Mapping Using Satellite Data", "Remote Sensing, 2025"),
            ("Urban Heat Islands in African Cities", "Urban Climate, 2024")
        ]
        
        for title, journal in papers:
            st.markdown(f"**📄 {title}**")
            st.markdown(f"*{journal}*")
            st.markdown("---")

# ============================================
# PAGE 7: INTERNATIONAL IMPACT
# ============================================
else:
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
    
    1. **SDG 6:** Clean Water and Sanitation (Water body mapping)
    2. **SDG 9:** Industry, Innovation and Infrastructure
    3. **SDG 11:** Sustainable Cities and Communities
    4. **SDG 13:** Climate Action
    5. **SDG 15:** Life on Land
    
    ### Scientific Contributions:
    - Real-time space weather monitoring for East Africa
    - High-resolution water body mapping
    - Urban heat island tracking
    - Vegetation health monitoring
    - Satellite-based early warning system
    
    ### Future Development:
    - Integration with actual satellite ground stations
    - Machine learning for improved predictions
    - Regional space weather center for East Africa
    - STEM education outreach program
    - Real-time water quality monitoring
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
    <p style='font-size: 12px;'>🌍 Interactive Geographic Intelligence Platform with Multi-Layer Analysis</p>
</div>
""", unsafe_allow_html=True)