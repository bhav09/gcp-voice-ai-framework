from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from src.tools.dispatcher import ToolDispatcher
from src.tools.gcp_connectors.bigquery_tool import BigQueryTool
from src.tools.gcp_connectors.firestore_tool import FirestoreTool
from src.tools.gcp_connectors.pubsub_tool import PubSubTool
from src.tools.gcp_connectors.rag_vertex import VertexRAGTool
from src.tools.gcp_connectors.spanner_tool import SpannerTool
from src.tools.gcp_connectors.spanner_graph_tool import SpannerGraphTool
from src.tools.gcp_connectors.cloudsql_tool import CloudSQLTool
from src.tools.gcp_connectors.dashboard_tool import DashboardGeneratorTool
from src.tools.gcp_connectors.insights_tool import CrossSourceInsightsTool

router = APIRouter(prefix="/api/v1/tools", tags=["Tools Execution API"])

# Global Tool Dispatcher instance
dispatcher = ToolDispatcher()
dispatcher.register_tool(BigQueryTool())
dispatcher.register_tool(FirestoreTool())
dispatcher.register_tool(PubSubTool())
dispatcher.register_tool(VertexRAGTool())
dispatcher.register_tool(SpannerTool())
dispatcher.register_tool(SpannerGraphTool())
dispatcher.register_tool(CloudSQLTool())
dispatcher.register_tool(DashboardGeneratorTool())
dispatcher.register_tool(CrossSourceInsightsTool())

class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(description="Registered tool name")
    arguments: Dict[str, Any] = Field(description="Arguments payload")

@router.get("/declarations")
async def get_tool_declarations() -> List[Dict[str, Any]]:
    """Return Gemini OpenAPI function declarations for all registered GCP connector tools."""
    return dispatcher.get_tool_declarations()

@router.post("/execute")
async def execute_tool_api(request: ToolExecuteRequest) -> Dict[str, Any]:
    """Execute registered GCP tool asynchronously via REST API."""
    result = await dispatcher.execute_tool(request.tool_name, request.arguments)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
