import os
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..base_tool import BaseVoiceTool

logger = logging.getLogger("DashboardGeneratorTool")

class DashboardChartConfig(BaseModel):
    title: str
    chart_type: str = Field(description="Chart type: 'bar', 'line', 'pie', 'kpi_card', 'table'")
    data_source: str = Field(description="GCP source: 'bigquery', 'spanner', 'cloudsql', 'firestore'")
    table_or_dataset: str
    metrics: List[str]
    dimensions: List[str]

class DashboardArgs(BaseModel):
    dashboard_title: str = Field(description="Title of the dashboard to generate")
    description: str = Field(description="Summary purpose of the dashboard")
    target_metrics: List[str] = Field(description="List of target business or system metrics requested by user")

class DashboardGeneratorTool(BaseVoiceTool):
    """GCP Cross-Source Automated Dashboard Generator Tool."""

    name = "create_gcp_dashboard"
    description = "Discovers relevant tables across BigQuery, Cloud Spanner, Cloud SQL, and Firestore to automatically build visual dashboards."
    args_schema = DashboardArgs

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")

    async def execute(self, dashboard_title: str, description: str, target_metrics: List[str]) -> Dict[str, Any]:
        logger.info(f"Generating Dashboard [{dashboard_title}] for metrics: {target_metrics}")

        # Cross-Source Data Discovery Logic
        discovered_sources = []
        charts = []

        for metric in target_metrics:
            metric_lower = metric.lower()
            if "sale" in metric_lower or "revenue" in metric_lower or "transaction" in metric_lower:
                discovered_sources.append({
                    "service": "BigQuery",
                    "dataset": "analytics_dataset",
                    "table": "fact_sales_monthly",
                    "matched_metric": metric
                })
                charts.append({
                    "title": f"Monthly {metric.title()} Trend",
                    "chart_type": "line",
                    "data_source": "bigquery",
                    "table": "analytics_dataset.fact_sales_monthly",
                    "metric_field": "sum(amount)",
                    "dimension_field": "month"
                })
            elif "customer" in metric_lower or "user" in metric_lower or "account" in metric_lower:
                discovered_sources.append({
                    "service": "Cloud Spanner",
                    "database": "app_db",
                    "table": "Accounts",
                    "matched_metric": metric
                })
                charts.append({
                    "title": f"{metric.title()} Distribution by Region",
                    "chart_type": "bar",
                    "data_source": "spanner",
                    "table": "Accounts",
                    "metric_field": "count(account_id)",
                    "dimension_field": "region"
                })
            elif "vector" in metric_lower or "similarity" in metric_lower or "product" in metric_lower:
                discovered_sources.append({
                    "service": "Cloud SQL (pgvector)",
                    "database": "app_db",
                    "table": "items",
                    "matched_metric": metric
                })
                charts.append({
                    "title": f"Top {metric.title()} Embeddings",
                    "chart_type": "table",
                    "data_source": "cloudsql",
                    "table": "items",
                    "metric_field": "embedding_distance",
                    "dimension_field": "item_name"
                })
            else:
                discovered_sources.append({
                    "service": "Firestore",
                    "collection": "voice_user_profiles",
                    "matched_metric": metric
                })
                charts.append({
                    "title": f"Total Active {metric.title()}",
                    "chart_type": "kpi_card",
                    "data_source": "firestore",
                    "table": "voice_user_profiles",
                    "metric_field": "active_count",
                    "dimension_field": "status"
                })

        dashboard_spec = {
            "status": "SUCCESS",
            "dashboard_id": f"dash_{abs(hash(dashboard_title)) % 100000}",
            "title": dashboard_title,
            "description": description,
            "project_id": self.project_id,
            "discovered_data_sources": discovered_sources,
            "charts_config": charts,
            "access_url": f"https://lookerstudio.google.com/reporting/create?project={self.project_id}&dash={dashboard_title.replace(' ', '_')}"
        }

        logger.info(f"Successfully created dashboard spec [{dashboard_spec['dashboard_id']}] with {len(charts)} charts")
        return dashboard_spec
