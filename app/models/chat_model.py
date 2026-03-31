"""
Models containing the fundamental classes holding the chats with LLM
"""

from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime

@dataclass
class Message:
    """A single message in the conversation."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    token_estimate: int = 0

    def __post_init__(self):
        # Estimate tokens: ~4 characters per token
        self.token_estimate = len(self.content) // 4

@dataclass
class ChatState:
    """The complete state of a conversation."""

    messages: list[Message] = field(default_factory=list)
    max_tokens: int = 8000  # Context budget for history

    def total_tokens(self) -> int:
        """Calculate total tokens in current context."""
        message_tokens = sum(m.token_estimate for m in self.messages)
        return message_tokens