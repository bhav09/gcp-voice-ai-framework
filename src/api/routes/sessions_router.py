from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from src.core.session_manager import VoiceSessionManager

router = APIRouter(prefix="/api/v1/sessions", tags=["Session Lifecycle API"])

# Active session store
active_sessions: Dict[str, VoiceSessionManager] = {}

class SessionStartRequest(BaseModel):
    user_id: Optional[str] = Field(default=None, description="Optional persistent user identifier")
    provider_type: str = Field(default="vertex", description="'vertex' or 'aistudio'")

class SessionStartResponse(BaseModel):
    session_id: str
    user_id: str
    status: str

@router.post("/start", response_model=SessionStartResponse)
async def start_session_api(request: SessionStartRequest):
    """Initialize new Voice AI session, loading Firestore episodic memory."""
    manager = VoiceSessionManager(user_id=request.user_id)
    await manager.initialize()
    manager.create_client(provider_type=request.provider_type)
    
    active_sessions[manager.session_id] = manager
    return SessionStartResponse(
        session_id=manager.session_id,
        user_id=manager.memory_orchestrator.user_id,
        status="ACTIVE"
    )

@router.get("/{session_id}/state")
async def get_session_state_api(session_id: str) -> Dict[str, Any]:
    """Retrieve active session state & context memory summary."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session [{session_id}] not found.")
    
    manager = active_sessions[session_id]
    return {
        "session_id": session_id,
        "state": manager.memory_orchestrator.state_store,
        "summary": manager.memory_orchestrator.compacted_summary
    }

@router.post("/{session_id}/end")
async def end_session_api(session_id: str) -> Dict[str, Any]:
    """Terminate session and persist state to Firestore."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session [{session_id}] not found.")
    
    manager = active_sessions.pop(session_id)
    persisted = await manager.close_session()
    return {"session_id": session_id, "status": "CLOSED", "memory_persisted": persisted}
