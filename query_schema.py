# query_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class QueryPlan(BaseModel):
    action: str = Field(description="Database action")
    regions: list[str] = Field(description="States/regions to analyze")
    time_period_years: int = Field(description="Number of years to analyze")
    agri_metric: str = Field(description="Agriculture metric")
    climate_metric: str = Field(description="Climate metric")
    top_n: Optional[int] = Field(default=5, description="Number of top items to show")

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_data_query",
        "description": "Generate query plan for agriculture and climate data",
        "parameters": QueryPlan.model_json_schema()
    }
}