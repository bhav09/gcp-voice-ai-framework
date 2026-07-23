import pytest
from src.tools.gcp_connectors.dashboard_tool import DashboardGeneratorTool
from src.tools.gcp_connectors.insights_tool import CrossSourceInsightsTool
from src.security.guardrails import VoiceGuardrailsEngine

@pytest.mark.asyncio
async def test_dashboard_generator_tool():
    tool = DashboardGeneratorTool()
    res = await tool.execute(
        dashboard_title="Executive Sales & Churn Dashboard",
        description="Tracks monthly revenue and customer retention metrics across BigQuery and Cloud Spanner",
        target_metrics=["Monthly Revenue", "Customer Churn Rate", "Product Embeddings"]
    )
    
    assert res["status"] == "SUCCESS"
    assert res["title"] == "Executive Sales & Churn Dashboard"
    assert len(res["discovered_data_sources"]) == 3
    assert len(res["charts_config"]) == 3
    assert "lookerstudio.google.com" in res["access_url"]

@pytest.mark.asyncio
async def test_cross_source_insights_tool():
    tool = CrossSourceInsightsTool()
    res = await tool.execute(
        topic="Customer Account Growth",
        target_data_sources=["bigquery", "spanner", "vertex_rag"]
    )
    
    assert res["status"] == "SUCCESS"
    assert res["topic"] == "Customer Account Growth"
    assert res["queried_sources_count"] == 3
    assert len(res["discovered_findings"]) == 3
    assert len(res["executive_summary_takeaways"]) > 0

def test_nsfw_and_off_topic_guardrails():
    guardrails = VoiceGuardrailsEngine()
    
    # 1. Test NSFW language rejection
    nsfw_check = guardrails.validate_input_transcript("Tell me a vulgar explicit story with profane words")
    assert nsfw_check["is_safe"] is False
    assert nsfw_check["violation_type"] == "NSFW_LANGUAGE"
    assert "professional" in nsfw_check["polite_response"]

    # 2. Test Off-topic conversation redirection
    off_topic_check = guardrails.validate_input_transcript("who won the football match yesterday")
    assert off_topic_check["is_safe"] is False
    assert off_topic_check["violation_type"] == "OFF_TOPIC"
    assert "specialize exclusively in GCP" in off_topic_check["polite_response"]

    # 3. Test Valid enterprise analytics topic
    valid_check = guardrails.validate_input_transcript("Create a dashboard with Q3 sales and customer retention metrics")
    assert valid_check["is_safe"] is True
    assert valid_check["polite_response"] is None
