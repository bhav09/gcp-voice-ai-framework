import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("WorkingMemory")

class ShortTermWorkingMemory:
    """In-memory sliding ring buffer holding recent turn history and context summarization triggers."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._turns: List[Dict[str, Any]] = []

    def add_turn(self, role: str, text: str, audio_duration_sec: Optional[float] = None) -> None:
        """Add dialogue turn to short-term memory buffer."""
        self._turns.append({
            "role": role,
            "text": text,
            "audio_duration_sec": audio_duration_sec
        })
        if len(self._turns) > self.max_turns:
            compacted_turn = self._turns.pop(0)
            logger.debug(f"Evicted oldest turn from working memory: {compacted_turn['role']}")

    def get_context_turns(self) -> List[Dict[str, Any]]:
        """Return active working context turns."""
        return list(self._turns)

    def remove_oldest(self, count: int) -> List[Dict[str, Any]]:
        """Remove and return the oldest N turns from working memory."""
        actual_count = min(count, len(self._turns))
        removed = self._turns[:actual_count]
        del self._turns[:actual_count]
        return removed

    def clear(self) -> None:
        """Clear memory buffer."""
        self._turns.clear()
