"""
Chat service that handles converstation with LLM.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.models.chat_model import ChatState, Message
from app.common.utils import apply_windowing

from langchain_openrouter.chat_models import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ContextAwareChatApp:
    """A chat application with intelligent context management."""

    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant.",
        context_budget: int = 8000
    ):
        """
        Initialize the chat app.

        Args:
            system_prompt: The system message defining assistant behavior
            context_budget: Maximum tokens for conversation history
        """
        self.llm = ChatOpenRouter(model=os.getenv("MODEL_NAME", "openai/gpt-oss-120b:free"), temperature=0.7)
        self.state = ChatState(max_tokens=context_budget)

        # Add system message
        self.state.messages.append(Message(role="system", content=system_prompt))

    def _manage_context(self):
        """Apply the selected context management strategy."""
        self.state = apply_windowing(self.state, window_size=5)


    def _build_messages(self) -> list:
        """Build the message list for the LLM."""
        messages = []

        # Add all current messages
        for msg in self.state.messages:
            if msg.role == "system":
                messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        return messages

    def chat(self, user_input: str) -> str:
        """
        Process a user message and return the assistant's response.
        """
        # Add user message
        self.state.messages.append(Message(role="user", content=user_input))

        # Manage context before calling LLM
        self._manage_context()

        # Build messages and get response
        messages = self._build_messages()
        response = self.llm.invoke(messages)

        # Add assistant response to state
        self.state.messages.append(Message(role="assistant", content=response.content))

        return response.content

    def get_stats(self) -> dict:
        """Return current context statistics."""
        return {
            "message_count": len(self.state.messages),
            "total_tokens": self.state.total_tokens(),
            "budget_remaining": self.state.max_tokens - self.state.total_tokens(),
        }

    def get_message_history(self) -> dict:
        """Return Message History."""
        return {
            "message_count": len(self.state.messages),
            "messages": self.state.messages
        }