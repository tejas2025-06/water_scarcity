import os
import joblib
import pandas as pd
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

# --- App, DB, and Model Setup ---
app = FastAPI(title="REAL TIME WATER SCARCITY PREDICTION")
engine = create_engine(os.getenv("DATABASE_URL"))
model = joblib.load("water_model.joblib")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ZoneInput(BaseModel):
    name: str
    geometry: dict

class PredictionOutput(BaseModel):
    predicted_consumption_mld: float
    risk_level: str

# --- API Endpoints ---
@app.get("/api/zones")
def get_zones():
    with engine.connect() as conn:
        query = text("SELECT json_build_object('type','FeatureCollection','features',json_agg(json_build_object('type','Feature','id',zone_id,'properties',json_build_object('name',zone_name),'geometry',ST_AsGeoJSON(geometry)::json))) FROM zones;")
        result = conn.execute(query).scalar_one_or_none()
        return result or {"type": "FeatureCollection", "features": []}

@app.post("/api/zones", status_code=201)
def create_zone(zone: ZoneInput):
    geometry_geojson = json.dumps(zone.geometry)
    with engine.connect() as conn:
        try:
            query = text("INSERT INTO zones (zone_name, geometry) VALUES (:name, ST_GeomFromGeoJSON(:geom))")
            conn.execute(query, {"name": zone.name, "geom": geometry_geojson})
            conn.commit()
            return {"message": f"Zone '{zone.name}' created successfully."}
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))

# --- NEW: Endpoint to get historical data for charts ---
@app.get("/api/history/{zone_id}")
def get_history(zone_id: int):
    with engine.connect() as conn:
        # Get the last 365 days of data for the specified zone
        query = text("""
            SELECT "timestamp", rainfall_mm, avg_temp_celsius
            FROM water_data
            WHERE zone_id = :z_id
            ORDER BY "timestamp" DESC
            LIMIT 365;
        """)
        result = conn.execute(query, {"z_id": zone_id})
        # Fetch all rows and convert them into a list of dictionaries
        history = [{"timestamp": row[0], "rainfall": row[1], "temperature": row[2]} for row in result.fetchall()]
        return history

@app.get("/api/zone-factors/{zone_id}")
def get_zone_factors(zone_id: int):
    """Get detailed Indian water scarcity factors for a zone"""
    with engine.connect() as conn:
        query = text("""
            SELECT zone_name, 
                   AVG(population) as avg_population,
                   AVG(gdp_per_capita) as avg_gdp_per_capita,
                   AVG(literacy_rate) as avg_literacy_rate,
                   AVG(urban_density) as avg_urban_density,
                   AVG(infrastructure_score) as avg_infrastructure_score,
                   AVG(monsoon_dependency) as avg_monsoon_dependency,
                   AVG(groundwater_level) as avg_groundwater_level,
                   AVG(industrial_demand) as avg_industrial_demand,
                   AVG(agricultural_demand) as avg_agricultural_demand,
                   AVG(water_recycling_rate) as avg_water_recycling_rate,
                   AVG(drought_risk_index) as avg_drought_risk_index
            FROM water_data wd
            JOIN zones z ON wd.zone_id = z.zone_id
            WHERE wd.zone_id = :z_id
            GROUP BY zone_name
        """)
        result = conn.execute(query, {"z_id": zone_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Zone not found")
        
        return {
            "zone_name": result[0],
            "demographics": {
                "population": int(result[1]) if result[1] else 0,
                "gdp_per_capita": round(result[2], 0) if result[2] else 0,
                "literacy_rate": round(result[3], 1) if result[3] else 0,
                "urban_density": round(result[4], 0) if result[4] else 0
            },
            "infrastructure": {
                "infrastructure_score": round(result[5], 1) if result[5] else 0,
                "water_recycling_rate": round(result[10], 1) if result[10] else 0
            },
            "environmental": {
                "monsoon_dependency": round(result[6], 2) if result[6] else 0,
                "groundwater_level": round(result[7], 1) if result[7] else 0,
                "drought_risk_index": round(result[11], 1) if result[11] else 0
            },
            "demand_factors": {
                "industrial_demand_mld": round(result[8], 1) if result[8] else 0,
                "agricultural_demand_mld": round(result[9], 1) if result[9] else 0
            }
        }

@app.get("/api/predict/live/{zone_id}", response_model=PredictionOutput)
def predict_live(zone_id: int):
    """Enhanced prediction with real Indian factors"""
    tomorrow = pd.to_datetime('today') + pd.Timedelta(days=1)
    
    # Get real weather forecast (placeholder - in production use weather API)
    forecast_temp = 35.0 
    forecast_rain = 0.5
    forecast_humidity = 65.0
    forecast_wind = 3.2
    forecast_solar = 18.5
    
    # Get latest data for this zone
    with engine.connect() as conn:
        latest_query = text("""
            SELECT population, gdp_per_capita, literacy_rate, urban_density, 
                   infrastructure_score, monsoon_dependency, groundwater_level,
                   industrial_demand, agricultural_demand, water_recycling_rate
            FROM water_data 
            WHERE zone_id = :z_id 
            ORDER BY timestamp DESC LIMIT 1
        """)
        latest_data = conn.execute(latest_query, {"z_id": zone_id}).fetchone()
        
        if not latest_data:
            # Fallback defaults
            latest_data = (55000, 2500, 75.0, 4000, 5.5, 0.65, 15.0, 5.0, 8.0, 20.0)

    # Calculate drought risk index
    drought_risk = max(0, min(10, 
        (forecast_temp - 25) * 0.1 +
        (40 - forecast_rain) * 0.02 +
        latest_data[5] * 2 +  # monsoon_dependency
        (100 - forecast_humidity) * 0.01
    ))

    # Prepare enhanced input data
    input_data = {
        'zone_id': zone_id,
        'rainfall_mm': forecast_rain,
        'avg_temp_celsius': forecast_temp,
        'population': latest_data[0],
        'month': tomorrow.month,
        'day_of_year': tomorrow.dayofyear,
        'season': {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3}[tomorrow.month],
        'gdp_per_capita': latest_data[1],
        'literacy_rate': latest_data[2],
        'urban_density': latest_data[3],
        'infrastructure_score': latest_data[4],
        'monsoon_dependency': latest_data[5],
        'groundwater_level': latest_data[6],
        'industrial_demand': latest_data[7],
        'agricultural_demand': latest_data[8],
        'water_recycling_rate': latest_data[9],
        'drought_risk_index': drought_risk,
        'humidity': forecast_humidity,
        'wind_speed': forecast_wind,
        'solar_radiation': forecast_solar
    }
    
    # Load feature order
    try:
        features_order = joblib.load("model_features.joblib")
    except:
        # Fallback to basic features if enhanced model not available
        features_order = ['zone_id', 'rainfall_mm', 'avg_temp_celsius', 'population', 'month', 'day_of_year']
    
    # Create DataFrame with available features
    df = pd.DataFrame([input_data])
    available_features = [f for f in features_order if f in df.columns]
    df = df[available_features]
    
    prediction = model.predict(df)[0]
    
    # Enhanced risk assessment based on Indian water scarcity thresholds
    risk = "Low"
    if prediction > 18: risk = "Moderate"
    if prediction > 25: risk = "High" 
    if prediction > 35: risk = "Severe"
    if prediction > 50: risk = "Critical"
    
    return {"predicted_consumption_mld": round(prediction, 2), "risk_level": risk}

