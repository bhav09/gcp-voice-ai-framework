import sys
import os
import pytest
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.tools.gcp_connectors.bigquery_tool import BigQueryTool
from src.tools.gcp_connectors.firestore_tool import FirestoreTool
from src.tools.gcp_connectors.pubsub_tool import PubSubTool
from src.tools.gcp_connectors.rag_vertex import VertexRAGTool
from src.tools.gcp_connectors.spanner_tool import SpannerTool
from src.tools.gcp_connectors.spanner_graph_tool import SpannerGraphTool
from src.tools.gcp_connectors.cloudsql_tool import CloudSQLTool
from src.memory.episodic_memory import EpisodicMemoryManager

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")

@pytest.mark.asyncio
async def test_bigquery_read_only_tool():
    tool = BigQueryTool(project_id=PROJECT_ID)
    # Test valid query schema
    res = await tool.execute(query="SELECT 1 as test_val")
    assert "row_count" in res or "notice" in res

@pytest.mark.asyncio
async def test_bigquery_mutation_guardrail():
    tool = BigQueryTool(project_id=PROJECT_ID)
    # Mutation queries must be blocked by safety guardrail
    res = await tool.execute(query="DELETE FROM dataset.table WHERE 1=1")
    assert "error" in res
    assert "restricted" in res["error"].lower()

@pytest.mark.asyncio
async def test_firestore_read_write_connector():
    tool = FirestoreTool(project_id=PROJECT_ID)
    # Non-destructive transient document test
    res_write = await tool.execute(
        collection="test_voice_sessions",
        document_id="test_doc_001",
        action="write",
        payload={"session_status": "active", "test_flag": True}
    )
    assert res_write.get("status") in ["success", "mock_success"]

@pytest.mark.asyncio
async def test_pubsub_event_publisher():
    tool = PubSubTool(project_id=PROJECT_ID)
    res = await tool.execute(
        topic_id="test-voice-events",
        event_data={"event": "session_started", "user_id": "test_user_123"}
    )
    assert res.get("status") in ["published", "mock_published"]

@pytest.mark.asyncio
async def test_vertex_rag_search():
    tool = VertexRAGTool(project_id=PROJECT_ID)
    res = await tool.execute(query="What is Gemini Live PCM streaming?")
    assert "results" in res
    assert len(res["results"]) > 0

@pytest.mark.asyncio
async def test_spanner_database_query():
    tool = SpannerTool(project_id=PROJECT_ID)
    res = await tool.execute(sql_query="SELECT 1 as id")
    assert "rows" in res or "notice" in res

@pytest.mark.asyncio
async def test_spanner_mutation_guardrail():
    tool = SpannerTool(project_id=PROJECT_ID)
    res = await tool.execute(sql_query="DELETE FROM accounts WHERE 1=1")
    assert "error" in res

@pytest.mark.asyncio
async def test_spanner_graph_gql_query():
    tool = SpannerGraphTool(project_id=PROJECT_ID)
    res = await tool.execute(gql_query="GRAPH FinGraph MATCH (a:Account)-[e:TRANSFERRED]->(b:Account) RETURN a, e, b")
    assert "graph_paths" in res or "notice" in res

@pytest.mark.asyncio
async def test_cloudsql_database_query():
    tool = CloudSQLTool(project_id=PROJECT_ID)
    res = await tool.execute(sql_query="SELECT * FROM items ORDER BY embedding <-> '[0.1, 0.2]' LIMIT 5")
    assert res.get("status") == "success"
    assert "rows" in res


if __name__ == "__main__":
    pytest.main([__file__])
