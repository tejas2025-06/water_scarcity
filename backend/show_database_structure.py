"""
DATABASE STRUCTURE VISUALIZATION
Shows the complete database schema and data flow for REAL TIME WATER SCARCITY PREDICTION
"""

from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

def show_database_structure():
    """Display complete database structure"""
    
    print("=" * 80)
    print("🗄️  REAL TIME WATER SCARCITY PREDICTION DATABASE STRUCTURE")
    print("=" * 80)
    print()
    
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    # Get database info
    with engine.connect() as conn:
        # Check tables
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        tables = conn.execute(tables_query).fetchall()
        
        print(f"📊 DATABASE: water_db (PostgreSQL + PostGIS)")
        print(f"📍 Location: localhost:5432")
        print(f"📋 Tables: {len(tables)}")
        print()
        
        for table in tables:
            table_name = table[0]
            print(f"{'='*80}")
            print(f"📁 TABLE: {table_name}")
            print(f"{'='*80}")
            
            # Get column information
            columns_query = text(f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = conn.execute(columns_query).fetchall()
            
            print(f"\n📋 COLUMNS ({len(columns)} total):")
            print(f"{'Column Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
            print("-" * 80)
            
            for col in columns:
                col_name, data_type, nullable, default = col
                default_str = str(default)[:20] if default else "-"
                print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default_str}")
            
            # Get row count
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            count = conn.execute(count_query).scalar()
            print(f"\n📊 TOTAL RECORDS: {count:,}")
            
            # Show sample data
            if count > 0:
                sample_query = text(f"SELECT * FROM {table_name} LIMIT 3")
                sample = pd.read_sql(sample_query, conn)
                print(f"\n📝 SAMPLE DATA (first 3 rows):")
                print(sample.to_string(index=False))
            
            print()

def show_data_sources():
    """Show where each database column gets its data"""
    
    print("=" * 80)
    print("🔄 DATA SOURCES FOR EACH DATABASE COLUMN")
    print("=" * 80)
    print()
    
    data_sources = {
        "zones table": {
            "zone_id": "Auto-generated (SERIAL PRIMARY KEY)",
            "zone_name": "Manually defined (53 Indian cities/districts)",
            "geometry": "Real coordinates from Google Maps/OpenStreetMap"
        },
        "water_data table": {
            "zone_id": "Foreign key reference to zones table",
            "timestamp": "Date range: 2021-01-01 to 2024-12-31",
            "rainfall_mm": "NASA POWER API (PRECTOTCORR parameter)",
            "avg_temp_celsius": "NASA POWER API (T2M parameter)",
            "humidity": "NASA POWER API (RH2M parameter)",
            "wind_speed": "NASA POWER API (WS2M parameter)",
            "solar_radiation": "NASA POWER API (ALLSKY_SFC_SW_DWN parameter)",
            "population": "Census of India 2011 + annual growth projections",
            "literacy_rate": "Census of India 2011",
            "urban_density": "Urban Development Ministry reports",
            "gdp_per_capita": "Ministry of Statistics & Programme Implementation",
            "industrial_demand": "Calculated: GDP per capita × 0.002",
            "agricultural_demand": "Calculated: 8 + (latitude - 10) × 0.5",
            "infrastructure_score": "NITI Aayog Composite Water Management Index",
            "water_recycling_rate": "Calculated: literacy_rate × 0.3",
            "groundwater_level": "Central Ground Water Board (simulated)",
            "monsoon_dependency": "Calculated: Geographic analysis (lat/lon)",
            "drought_risk_index": "Calculated: Multi-factor (temp, rain, humidity)",
            "water_consumption_mld": "Calculated: Multi-factor consumption model"
        }
    }
    
    for table, columns in data_sources.items():
        print(f"📁 {table.upper()}")
        print("-" * 80)
        for column, source in columns.items():
            print(f"  {column:<25} → {source}")
        print()

def show_data_flow():
    """Show how data flows through the system"""
    
    print("=" * 80)
    print("🔄 DATA FLOW DIAGRAM")
    print("=" * 80)
    print()
    
    flow = """
    ┌─────────────────────────────────────────────────────────────────┐
    │                    DATA COLLECTION PHASE                        │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ NASA POWER   │ │ Census India │ │ NITI Aayog   │
            │ Weather API  │ │ Demographics │ │ Water Index  │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │   setup_and_train.py          │
                    │   - Fetch weather data        │
                    │   - Add demographic data      │
                    │   - Calculate factors         │
                    │   - Insert into database      │
                    └───────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    DATABASE STORAGE                             │
    │  ┌──────────────┐              ┌──────────────────────────┐    │
    │  │ zones        │              │ water_data               │    │
    │  │ - 53 zones   │◄─────────────│ - 77,433 records         │    │
    │  │ - Coordinates│  Foreign Key │ - 19 columns             │    │
    │  └──────────────┘              │ - 4 years daily data     │    │
    │                                 └──────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   ML MODEL TRAINING           │
                    │   - Read all historical data  │
                    │   - Train Random Forest       │
                    │   - Save model (98.8% R²)     │
                    └───────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    PREDICTION PHASE                             │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ Get Latest   │ │ Get Weather  │ │ Calculate    │
            │ Zone Data    │ │ Forecast     │ │ Factors      │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │   main.py (FastAPI)           │
                    │   - Load trained model        │
                    │   - Prepare input features    │
                    │   - Make prediction           │
                    │   - Return risk level         │
                    └───────────────────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │ API Response  │
                            │ - Water (MLD) │
                            │ - Risk Level  │
                            └───────────────┘
    """
    
    print(flow)

def show_statistics():
    """Show database statistics"""
    
    print("=" * 80)
    print("📊 DATABASE STATISTICS")
    print("=" * 80)
    print()
    
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    with engine.connect() as conn:
        # Overall stats
        stats_query = text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT zone_id) as unique_zones,
                MIN(timestamp) as earliest_date,
                MAX(timestamp) as latest_date,
                AVG(water_consumption_mld) as avg_consumption,
                MIN(water_consumption_mld) as min_consumption,
                MAX(water_consumption_mld) as max_consumption,
                AVG(population) as avg_population,
                AVG(gdp_per_capita) as avg_gdp,
                AVG(infrastructure_score) as avg_infrastructure,
                AVG(drought_risk_index) as avg_drought_risk
            FROM water_data
        """)
        
        stats = conn.execute(stats_query).fetchone()
        
        print("📈 OVERALL STATISTICS:")
        print(f"  Total Records: {stats[0]:,}")
        print(f"  Unique Zones: {stats[1]}")
        print(f"  Date Range: {stats[2]} to {stats[3]}")
        print(f"  Avg Water Consumption: {stats[4]:.2f} MLD")
        print(f"  Min/Max Consumption: {stats[5]:.2f} / {stats[6]:.2f} MLD")
        print(f"  Avg Population: {stats[7]:,.0f}")
        print(f"  Avg GDP per capita: ₹{stats[8]:,.0f}")
        print(f"  Avg Infrastructure Score: {stats[9]:.1f}/10")
        print(f"  Avg Drought Risk: {stats[10]:.1f}/10")
        print()
        
        # Top zones by consumption
        top_zones_query = text("""
            SELECT z.zone_name, AVG(wd.water_consumption_mld) as avg_consumption
            FROM zones z
            JOIN water_data wd ON z.zone_id = wd.zone_id
            GROUP BY z.zone_name
            ORDER BY avg_consumption DESC
            LIMIT 10
        """)
        
        top_zones = conn.execute(top_zones_query).fetchall()
        
        print("🏆 TOP 10 ZONES BY WATER CONSUMPTION:")
        for i, (zone_name, avg_consumption) in enumerate(top_zones, 1):
            print(f"  {i:2d}. {zone_name:<20} {avg_consumption:>6.2f} MLD")

if __name__ == "__main__":
    show_database_structure()
    print()
    show_data_sources()
    print()
    show_data_flow()
    print()
    show_statistics()
    
    print()
    print("=" * 80)
    print("✅ DATABASE OVERVIEW COMPLETE")
    print("=" * 80)