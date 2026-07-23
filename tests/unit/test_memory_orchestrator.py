import sys
import os
import pytest
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.memory.state_memory_orchestrator import UnifiedStateAndMemoryOrchestrator
from src.core.session_manager import VoiceSessionManager

@pytest.mark.asyncio
async def test_unified_state_and_memory_orchestrator():
    orchestrator = UnifiedStateAndMemoryOrchestrator(session_id="mem-test-001", user_id="user_test_999")
    state = await orchestrator.initialize_session()
    
    assert state["session_id"] == "mem-test-001"
    assert state["user_id"] == "user_test_999"
    assert state["workflow_step"] == "INIT"
    
    # Update transient state
    orchestrator.update_session_state("workflow_step", "ACCOUNT_VERIFIED")
    assert orchestrator.state_store["workflow_step"] == "ACCOUNT_VERIFIED"

    # Simulate multi-turn conversation triggering context compaction
    for i in range(7):
        orchestrator.record_turn(role="user" if i % 2 == 0 else "agent", text=f"Turn message {i}")
        
    context_prompt = orchestrator.get_full_context_prompt_injection()
    assert "ACCOUNT_VERIFIED" in context_prompt
    assert "Context Summary" in context_prompt

    # Finalize session
    res = await orchestrator.finalize_session()
    assert res is True

@pytest.mark.asyncio
async def test_voice_session_manager_memory_integration():
    manager = VoiceSessionManager(session_id="session-mem-002", user_id="user_888")
    await manager.initialize()
    
    client = manager.create_client(provider_type="vertex")
    assert "user_888" in client.system_instruction
    assert "INIT" in client.system_instruction

    closed = await manager.close_session()
    assert closed is True

if __name__ == "__main__":
    pytest.main([__file__])
