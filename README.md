# Project Samarth

Intelligent Q&A system for Indian agriculture and climate data integration.

## Overview
This system provides natural language interface to query and correlate agriculture production data with climate patterns using live data from data.gov.in.

## Features
- Natural language question answering
- Cross-domain data integration (Agriculture + Climate)
- District-level analysis
- Source traceability
- Real-time data processing

## Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Run ETL: `python etl_api.py`
5. Launch app: `streamlit run main.py`

## Data Sources
- Agriculture: Ministry of Agriculture & Farmers Welfare
- Climate: India Meteorological Department
- Portal: data.gov.in