import logging
from typing import Dict, Any, Optional
from ..tools.gcp_connectors.firestore_tool import FirestoreTool

logger = logging.getLogger("EpisodicMemory")

class EpisodicMemoryManager:
    """Long-term episodic user profile & dialogue persistence manager backed by Firestore."""

    def __init__(self, project_id: Optional[str] = None, collection: str = "voice_user_profiles"):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
        self.firestore_tool = FirestoreTool(project_id=self.project_id)
        self.collection = collection

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch cross-session preferences and persistent state for user."""
        res = await self.firestore_tool.execute(collection=self.collection, document_id=user_id, action="read")
        return res.get("data", {})

    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update episodic user attributes in long-term memory."""
        res = await self.firestore_tool.execute(collection=self.collection, document_id=user_id, action="write", payload=updates)
        return res.get("status") in ["success", "mock_success"]
