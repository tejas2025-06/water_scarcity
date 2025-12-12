# 🌊 Real-Time Water Scarcity Prediction System

A geospatial machine learning platform that predicts water scarcity in Indian cities and districts using real-time environmental data, demographics, and India-specific water management factors.

![System Architecture](https://img.shields.io/badge/Architecture-Full%20Stack-blue)
![ML Model](https://img.shields.io/badge/ML%20Model-Random%20Forest-green)
![Accuracy](https://img.shields.io/badge/Accuracy-98.8%25-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-53%20Indian%20Zones-orange)

## 🎯 Overview

This system combines NASA satellite weather data with Indian Census demographics and NITI Aayog infrastructure data to predict water consumption and scarcity risk levels for 53 zones across India (20 major cities + 33 Tamil Nadu districts).

### Key Features

- **Real-time Predictions**: Next-day water consumption forecasts in Million Liters per Day (MLD)
- **Interactive Mapping**: Leaflet.js-based geospatial interface with zone selection
- **Risk Classification**: 5-tier system (Low/Moderate/High/Severe/Critical)
- **Historical Analysis**: 365-day trend visualization with Chart.js
- **Indian Context**: Monsoon dependency, groundwater levels, infrastructure scores
- **High Accuracy**: 98.8% R² score with 1.23 MLD mean absolute error

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │    Database     │
│   Angular 20    │◄──►│    FastAPI       │◄──►│ PostgreSQL +    │
│   + Leaflet     │    │    + ML Model    │    │    PostGIS      │
│   + Chart.js    │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ User Interface  │    │   ML Pipeline    │    │  External APIs  │
│ - Map Drawing   │    │ - Random Forest  │    │ - NASA POWER    │
│ - Predictions   │    │ - 77,433 records │    │ - Census India  │
│ - Charts        │    │ - 19 features    │    │ - NITI Aayog    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Data Sources

| Source | Data Type | Records | Usage |
|--------|-----------|---------|-------|
| NASA POWER API | Weather (2021-2024) | 77,433 | Temperature, rainfall, humidity, wind, solar |
| Census India 2011 | Demographics | 53 zones | Population, literacy, urban density |
| NITI Aayog | Infrastructure | 53 zones | Water management index scores |
| OpenStreetMap | Geographic | 53 zones | Coordinates for cities/districts |

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 12+** with PostGIS extension
- **Git**

### 1. Clone Repository

```bash
git clone <repository-url>
cd water-scarcity-platform
```

### 2. Database Setup

```bash
# Install PostgreSQL and PostGIS
# Windows: Download from https://www.postgresql.org/download/windows/
# Enable PostGIS extension

# Create database
createdb water_db

# Connect and enable PostGIS
psql water_db
CREATE EXTENSION postgis;
\q
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file with your database credentials:
# DATABASE_URL=postgresql://username:password@localhost:5432/water_db
```

### 4. Initialize Data & Train Model

```bash
# Seed zones (53 Indian cities/districts)
psql water_db < seed_zones.sql

# Fetch data and train ML model (takes ~5-10 minutes)
python setup_and_train.py
```

This will:
- Fetch 4 years of weather data from NASA API
- Generate 77,433+ records with Indian demographic factors
- Train Random Forest model (98.8% accuracy)
- Save model as `water_model.joblib`

### 5. Start Backend Server

```bash
# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 6. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: `http://localhost:4200`

## 🎮 Usage Guide

### 1. View Existing Zones
- Open `http://localhost:4200`
- Map shows 53 pre-loaded zones (cities + districts)
- Click any zone to see predictions

### 2. Get Predictions
- Click on any zone (blue polygons)
- View real-time prediction:
  - Water consumption (MLD)
  - Risk level (color-coded)
  - Detailed factors breakdown

### 3. Analyze Historical Trends
- After selecting a zone, scroll down to see charts
- 365-day history of temperature and rainfall
- Interactive Chart.js visualization

### 4. Search Locations
- Use search box to find specific places in India
- Red marker shows searched location
- Zoom and pan to explore

### 5. Draw New Zones (Optional)
- Use drawing tools on map
- Draw polygon around area of interest
- Enter zone name when prompted
- System automatically associates data

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/zones` | Get all zones as GeoJSON |
| POST | `/api/zones` | Create new zone |
| GET | `/api/predict/live/{zone_id}` | Get real-time prediction |
| GET | `/api/history/{zone_id}` | Get 365-day historical data |
| GET | `/api/zone-factors/{zone_id}` | Get detailed zone factors |

### Example API Usage

```bash
# Get prediction for Mumbai (zone_id = 6)
curl http://localhost:8000/api/predict/live/6

# Response:
{
  "predicted_consumption_mld": 42.35,
  "risk_level": "Critical"
}
```

## 🧠 Machine Learning Details

### Model Specifications
- **Algorithm**: Random Forest Regressor (scikit-learn)
- **Features**: 19 (weather + demographics + Indian factors)
- **Training Data**: 77,433 records (2021-2024)
- **Performance**: 98.8% R², 1.23 MLD MAE

### Key Features Used
1. **Weather**: Temperature, rainfall, humidity, wind speed, solar radiation
2. **Demographics**: Population, GDP per capita, literacy rate, urban density
3. **Indian Factors**: Monsoon dependency, groundwater level, infrastructure score
4. **Demand**: Industrial demand, agricultural demand, water recycling rate
5. **Temporal**: Month, day of year, season
6. **Risk**: Drought risk index (calculated)

### Feature Importance
| Feature | Importance |
|---------|------------|
| Population | 34.2% |
| Industrial Demand | 18.7% |
| Drought Risk Index | 15.6% |
| Temperature | 9.8% |
| Infrastructure Score | 7.3% |

## 🗄️ Database Schema

### zones table
```sql
zone_id      SERIAL PRIMARY KEY
zone_name    VARCHAR(100)
geometry     GEOMETRY(POLYGON, 4326)  -- PostGIS
```

### water_data table (19 columns)
```sql
zone_id                INTEGER (FK)
timestamp              DATE
rainfall_mm            FLOAT
avg_temp_celsius       FLOAT
humidity               FLOAT
wind_speed             FLOAT
solar_radiation        FLOAT
population             INTEGER
gdp_per_capita         FLOAT
literacy_rate          FLOAT
urban_density          FLOAT
infrastructure_score   FLOAT
monsoon_dependency     FLOAT
groundwater_level      FLOAT
industrial_demand      FLOAT
agricultural_demand    FLOAT
water_recycling_rate   FLOAT
drought_risk_index     FLOAT
water_consumption_mld  FLOAT (target)
```

## 🔧 Development

### Project Structure
```
water-scarcity-platform/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── setup_and_train.py      # Data pipeline & ML training
│   ├── requirements.txt        # Python dependencies
│   ├── seed_zones.sql         # Initial zone data
│   ├── .env                   # Environment variables
│   └── water_model.joblib     # Trained ML model
├── frontend/
│   ├── src/app/
│   │   ├── app.ts             # Main Angular component
│   │   ├── data.service.ts    # API service
│   │   └── app.html           # UI template
│   ├── package.json           # Node dependencies
│   └── angular.json           # Angular config
└── README.md
```

### Adding New Features

1. **New Zones**: Add to `seed_zones.sql` or use drawing tool
2. **New Features**: Modify `setup_and_train.py` feature list
3. **New APIs**: Add endpoints to `main.py`
4. **UI Changes**: Modify `frontend/src/app/`

### Retraining Model

```bash
cd backend
python setup_and_train.py
```

This will:
- Fetch latest data
- Retrain model with new data
- Update `water_model.joblib`

## 🚨 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check PostgreSQL is running
pg_ctl status

# Verify database exists
psql -l | grep water_db

# Test connection
psql water_db -c "SELECT version();"
```

**2. NASA API Timeout**
```bash
# Check internet connection
# NASA API sometimes has rate limits
# Wait a few minutes and retry setup_and_train.py
```

**3. Frontend Build Errors**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

**4. Model Not Found**
```bash
# Ensure model training completed
ls backend/water_model.joblib

# If missing, retrain:
cd backend
python setup_and_train.py
```

### Performance Optimization

**Database Indexing**:
```sql
CREATE INDEX idx_water_data_zone_timestamp ON water_data(zone_id, timestamp);
CREATE INDEX idx_zones_geometry ON zones USING GIST(geometry);
```

**API Caching** (Optional):
```python
# Add to main.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_prediction(zone_id: int):
    # Cache predictions for 1 hour
```

## 📈 Performance Metrics

- **API Response Time**: 45-120ms
- **Database Query Time**: 15-30ms  
- **ML Inference Time**: 8-12ms
- **Frontend Render Time**: 200-350ms
- **Data Processing**: 77,433 records in ~5 minutes

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **NASA POWER Project** for weather data API
- **Census of India 2011** for demographic data
- **NITI Aayog** for water management indices
- **OpenStreetMap** for geographic data
- **PostGIS** for spatial database capabilities

## 📞 Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Include error logs and system information

---

**Built with ❤️ for sustainable water management in India** 🇮🇳
