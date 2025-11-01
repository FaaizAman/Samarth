# data_access.py
import pandas as pd
from sqlalchemy import create_engine
from typing import Tuple
from query_schema import QueryPlan

DB_PATH = 'sqlite:///samarth.db'
ENGINE = create_engine(DB_PATH)


def execute_comparison(plan: QueryPlan) -> Tuple[pd.DataFrame, list]:
    requested_district = plan.regions[0] if plan.regions else get_available_districts()[0]
    actual_district = find_actual_district_name(requested_district)

    if not actual_district:
        return pd.DataFrame(), ["35be999b-0208-4354-b557-f6ca9a5355de"]

    if plan.action == "top_crops":
        sql_query = f"""
        SELECT 
            crop as Crop,
            SUM(production_tonnes) as Total_Production,
            AVG(production_tonnes) as Avg_Production,
            COUNT(DISTINCT year) as Years_Available
        FROM agri_data 
        WHERE district_name = '{actual_district}'
        AND year IN (SELECT DISTINCT year FROM agri_data ORDER BY year DESC LIMIT {plan.time_period_years})
        GROUP BY crop
        HAVING Years_Available > 0
        ORDER BY Total_Production DESC
        LIMIT {plan.top_n}
        """

    elif plan.action == "rainfall_only":
        climate_region = map_district_to_climate_region(actual_district)

        sql_query = f"""
        SELECT 
            region as Region,
            year as Year,
            annual_rainfall_mm as Rainfall
        FROM climate_data 
        WHERE region = '{climate_region}'
        AND year IN (SELECT DISTINCT year FROM climate_data ORDER BY year DESC LIMIT {plan.time_period_years})
        ORDER BY year DESC
        """

    elif plan.action == "compare_states" and len(plan.regions) >= 2:
        district1 = find_actual_district_name(plan.regions[0])
        district2 = find_actual_district_name(plan.regions[1])

        if not district1 or not district2:
            return pd.DataFrame(), ["35be999b-0208-4354-b557-f6ca9a5355de"]

        sql_query = f"""
        SELECT 
            district_name as District,
            AVG(production_tonnes) as Avg_Production,
            COUNT(DISTINCT crop) as Crop_Count,
            COUNT(DISTINCT year) as Years_Available
        FROM agri_data 
        WHERE district_name IN ('{district1}', '{district2}')
        AND year IN (SELECT DISTINCT year FROM agri_data ORDER BY year DESC LIMIT {plan.time_period_years})
        GROUP BY district_name
        """

    else:
        sql_query = f"""
        SELECT 
            district_name as District,
            year as Year,
            crop as Crop,
            production_tonnes as Production
        FROM agri_data 
        WHERE district_name = '{actual_district}'
        AND year IN (SELECT DISTINCT year FROM agri_data ORDER BY year DESC LIMIT {plan.time_period_years})
        ORDER BY year DESC
        LIMIT 50
        """

    try:
        df_result = pd.read_sql(sql_query, ENGINE)
        sources = ["35be999b-0208-4354-b557-f6ca9a5355de", "440dbca7-86ce-4bf6-b1af-83af2855757e"]
        return df_result, sources
    except Exception as e:
        return pd.DataFrame(), ["35be999b-0208-4354-b557-f6ca9a5355de"]


def find_actual_district_name(requested_district):
    try:
        all_districts = get_available_districts()
        requested_lower = requested_district.lower().strip()

        for district in all_districts:
            if district.lower().strip() == requested_lower:
                return district

        for district in all_districts:
            if requested_lower in district.lower():
                return district

        return None
    except:
        return requested_district


def map_district_to_climate_region(district):
    district_upper = district.upper()

    if 'ANDHRA' in district_upper:
        return 'COASTAL ANDHRA PRADESH'
    elif 'ANDAMAN' in district_upper or 'NICOBAR' in district_upper:
        return 'ANDAMAN & NICOBAR ISLANDS'
    elif 'TAMIL' in district_upper or 'NADU' in district_upper:
        return 'TAMIL NADU'
    elif 'KARNATAKA' in district_upper:
        return 'COASTAL KARNATAKA'
    else:
        return 'COASTAL ANDHRA PRADESH'


def generate_narrative_summary(df_result: pd.DataFrame, sources: list, plan: QueryPlan) -> str:
    if df_result.empty:
        available_dists = get_available_districts()[:6]
        return f"No data found for '{plan.regions[0]}'\n\nAvailable districts: {', '.join(available_dists)}\n\nTry questions about these districts."

    if plan.action == "top_crops":
        district = plan.regions[0]
        answer = f"Top {plan.top_n} Most Produced Crops in {district} District\n\n"

        for i, (_, row) in enumerate(df_result.iterrows(), 1):
            answer += f"{i}. {row['Crop']}\n"
            answer += f"   Total Production: {row['Total_Production']:,.0f} tonnes\n"
            answer += f"   Average Annual: {row['Avg_Production']:,.0f} tonnes\n\n"

        if 'Total_Production' in df_result.columns:
            total = df_result['Total_Production'].sum()
            answer += f"Total production of top {plan.top_n} crops: {total:,.0f} tonnes\n\n"

    elif plan.action == "rainfall_only":
        avg_rainfall = df_result['Rainfall'].mean()
        answer = f"Rainfall Analysis\n\n"
        answer += f"Average Rainfall: {avg_rainfall:,.0f} mm\n\n"
        answer += f"Based on {len(df_result)} years of regional data\n\n"

    elif plan.action == "compare_states":
        answer = f"District Comparison: {' vs '.join(plan.regions)}\n\n"
        for _, row in df_result.iterrows():
            answer += f"{row['District']}\n"
            answer += f"   Average Production: {row['Avg_Production']:,.0f} tonnes\n"
            answer += f"   Crops Grown: {row['Crop_Count']} types\n\n"

    else:
        district = plan.regions[0]
        if 'Production' in df_result.columns:
            avg_production = df_result['Production'].mean()
            answer = f"Agriculture Production in {district} District\n\n"
            answer += f"Average Production: {avg_production:,.0f} tonnes\n\n"
        else:
            answer = f"Data Summary for {district} District\n\n"
            answer += f"Found {len(df_result)} records of agricultural data.\n\n"

    answer += "Data sourced from Government of India datasets"
    return answer


def get_available_districts():
    try:
        districts = pd.read_sql("SELECT DISTINCT district_name FROM agri_data WHERE district_name IS NOT NULL", ENGINE)
        return districts['district_name'].tolist()
    except:
        return ['ANANTAPUR', 'CHITTOOR', 'GUNTUR', 'EAST GODAVARI']