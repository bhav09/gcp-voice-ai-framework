import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.api.fastapi_app import app

client = TestClient(app)

def test_fastapi_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["project_id"] is not None

def test_fastapi_tool_declarations_endpoint():
    response = client.get("/api/v1/tools/declarations")
    assert response.status_code == 200
    declarations = response.json()
    assert len(declarations) >= 7
    tool_names = [d["name"] for d in declarations]
    assert "query_spanner_graph" in tool_names
    assert "query_cloudsql_database" in tool_names

def test_fastapi_tool_execute_endpoint():
    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool_name": "query_cloudsql_database",
            "arguments": {"sql_query": "SELECT 1"}
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"

def test_fastapi_session_lifecycle_endpoints():
    # Start Session
    start_resp = client.post(
        "/api/v1/sessions/start",
        json={"user_id": "fastapi_test_user", "provider_type": "vertex"}
    )
    assert start_resp.status_code == 200
    session_data = start_resp.json()
    session_id = session_data["session_id"]
    assert session_data["status"] == "ACTIVE"

    # Get State
    state_resp = client.get(f"/api/v1/sessions/{session_id}/state")
    assert state_resp.status_code == 200
    assert state_resp.json()["session_id"] == session_id

    # End Session
    end_resp = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_resp.status_code == 200
    assert end_resp.json()["status"] == "CLOSED"

def test_fastapi_websocket_voice_stream():
    with client.websocket_connect("/ws/voice?session_id=test_ws_001") as websocket:
        # Send binary PCM frame
        pcm_bytes = b"\x00\x10\x00\x20" * 128
        websocket.send_bytes(pcm_bytes)
        data = websocket.receive_json()
        assert data["event"] == "audio_received"
        assert data["bytes_len"] == len(pcm_bytes)

if __name__ == "__main__":
    pytest.main([__file__])
