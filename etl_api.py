# etl_api.py
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DGI_API_KEY = os.getenv("DGI_API_KEY")
DB_PATH = 'sqlite:///samarth.db'
ENGINE = create_engine(DB_PATH)

AGRICULTURE_RESOURCE_ID = "35be999b-0208-4354-b557-f6ca9a5355de"
RAINFALL_RESOURCE_ID = "440dbca7-86ce-4bf6-b1af-83af2855757e"

BASE_API_URL = "https://api.data.gov.in/resource/"


def fetch_dgi_data(resource_id: str, limit: int = 10000) -> pd.DataFrame:  # Increased limit
    """Fetches data from a specific Data.gov.in resource ID."""
    url = f"{BASE_API_URL}{resource_id}?api-key={DGI_API_KEY}&format=json&limit={limit}"

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        if 'records' not in data or not data['records']:
            print(f"Error: No records found for ID {resource_id}")
            return pd.DataFrame()

        df = pd.DataFrame(data['records'])
        df['original_source_id'] = resource_id
        return df

    except requests.exceptions.RequestException as e:
        print(f"API Fetch Error for {resource_id}: {e}")
        return pd.DataFrame()


def run_etl():
    """Fetches and loads data into SQLite DB."""
    print("\n--- Starting ETL Process ---")

    # Fetch Agriculture Data
    df_agri = fetch_dgi_data(AGRICULTURE_RESOURCE_ID, limit=10000)
    if not df_agri.empty:
        # Clean column names
        df_agri.columns = df_agri.columns.str.lower().str.replace(' ', '_')

        # Rename columns
        df_agri.rename(columns={
            'state_name': 'state_name',
            'district_name': 'district_name',
            'crop_year': 'year',
            'season': 'season',
            'crop': 'crop',
            'area_': 'area_hectares',
            'production_': 'production_tonnes'
        }, inplace=True)

        # Convert to numeric
        df_agri['production_tonnes'] = pd.to_numeric(df_agri['production_tonnes'], errors='coerce')
        df_agri['area_hectares'] = pd.to_numeric(df_agri['area_hectares'], errors='coerce')

        # Remove rows with invalid production
        df_agri = df_agri.dropna(subset=['production_tonnes'])

        print(f"✅ Loaded {len(df_agri)} agriculture rows")
        print(f"Available states: {sorted(df_agri['state_name'].unique())}")

        df_agri.to_sql('agri_data', ENGINE, if_exists='replace', index=False)

    # Fetch Climate Data
    df_climate = fetch_dgi_data(RAINFALL_RESOURCE_ID, limit=10000)
    if not df_climate.empty:
        df_climate.columns = df_climate.columns.str.lower().str.replace(' ', '_')

        df_climate.rename(columns={
            'subdivision': 'region',
            'year': 'year',
            'annual': 'annual_rainfall_mm'
        }, inplace=True)

        # Convert to numeric
        df_climate['year'] = pd.to_numeric(df_climate['year'], errors='coerce')
        df_climate['annual_rainfall_mm'] = pd.to_numeric(df_climate['annual_rainfall_mm'], errors='coerce')

        df_climate = df_climate.dropna(subset=['year', 'annual_rainfall_mm'])

        print(f"✅ Loaded {len(df_climate)} climate rows")
        print(f"Available regions: {sorted(df_climate['region'].unique())}")

        df_climate.to_sql('climate_data', ENGINE, if_exists='replace', index=False)


if __name__ == "__main__":
    run_etl()