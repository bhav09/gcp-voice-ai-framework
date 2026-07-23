import os
import time
import logging
from typing import Dict, Any, List, Optional
from .working_memory import ShortTermWorkingMemory
from .episodic_memory import EpisodicMemoryManager

logger = logging.getLogger("UnifiedMemoryOrchestrator")

class UnifiedStateAndMemoryOrchestrator:
    """Unified State & Common Memory Orchestrator for Voice AI Agent sessions.
    
    Manages:
    1. Transient Session State (Active workflow step, user intent, auth level).
    2. Short-Term Working Memory (Real-time dialogue turns & audio transcript buffer).
    3. Context Summarization Engine (Compacts dialogue context when threshold is reached).
    4. Long-Term Episodic Memory (Firestore user profile & cross-session memory).
    """

    def __init__(self, session_id: str, user_id: Optional[str] = None, project_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id or f"anon_user_{session_id[:8]}"
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
        
        # State & Memory Components
        self.state_store: Dict[str, Any] = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": time.time(),
            "active_intent": None,
            "workflow_step": "INIT",
            "is_authenticated": False
        }
        
        self.working_memory = ShortTermWorkingMemory(max_turns=6)
        self.episodic_memory = EpisodicMemoryManager(project_id=self.project_id)
        self.compacted_summary: str = ""

    async def initialize_session(self) -> Dict[str, Any]:
        """Loads long-term user profile & preferences from Firestore upon voice call connection."""
        logger.info(f"Initializing Unified State & Memory for Session [{self.session_id}], User [{self.user_id}]")
        user_profile = await self.episodic_memory.get_user_profile(self.user_id)
        if user_profile:
            self.state_store["user_profile"] = user_profile
            logger.info(f"Loaded persistent episodic memory for user [{self.user_id}]: {list(user_profile.keys())}")
        return self.state_store

    def record_turn(self, role: str, text: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> None:
        """Record dialogue turn into short-term working memory and check context compactor thresholds."""
        self.working_memory.add_turn(role=role, text=text)
        
        # Automatic Context Compaction / Summarization Check
        turns = self.working_memory.get_context_turns()
        if len(turns) >= self.working_memory.max_turns:
            # Compact the oldest 3 turns into a summary, then remove them
            old_turns = turns[:3]
            self._compact_context(old_turns)
            self.working_memory.remove_oldest(3)

    def _compact_context(self, old_turns: List[Dict[str, Any]]) -> None:
        """Compacts early dialogue turns into a persistent summary string."""
        summary_snippets = [f"{t['role']}: {t['text']}" for t in old_turns]
        new_summary = " | ".join(summary_snippets)
        if self.compacted_summary:
            self.compacted_summary += f" -> {new_summary}"
        else:
            self.compacted_summary = f"Prior Conversation Summary: {new_summary}"
        logger.info(f"Compacted working context into summary: {self.compacted_summary[:80]}...")

    def update_session_state(self, key: str, value: Any) -> None:
        """Update transient session state variable."""
        self.state_store[key] = value
        logger.debug(f"Updated session state [{key}] = {value}")

    def get_full_context_prompt_injection(self) -> str:
        """Generates dynamic system prompt context injection combining state, summary, and user profile."""
        profile_str = str(self.state_store.get("user_profile", {}))
        return (
            f"\n[ACTIVE SESSION STATE]\n"
            f"- User ID: {self.user_id}\n"
            f"- Workflow Step: {self.state_store.get('workflow_step')}\n"
            f"- User Profile Context: {profile_str}\n"
            f"- Context Summary: {self.compacted_summary or 'None'}\n"
        )

    async def finalize_session(self) -> bool:
        """Persists extracted user profile attributes and session summary to Firestore at call end."""
        logger.info(f"Finalizing session [{self.session_id}]. Persisting episodic memory to Firestore.")
        session_summary_data = {
            "last_session_id": self.session_id,
            "last_active": time.time(),
            "summary": self.compacted_summary,
            "workflow_step": self.state_store.get("workflow_step")
        }
        return await self.episodic_memory.update_user_profile(self.user_id, session_summary_data)
