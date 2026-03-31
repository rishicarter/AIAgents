"""
Utils offer helper functions as Service
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

from app.models.chat_model import ChatState

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def apply_windowing(state: ChatState, window_size: int = 5) -> ChatState:
    """
    Windowing — Keep Only N Recent Messages

    args
    ---
    window_size: int -> Determines the recent N messages in history.
    actual_window_size will be window_size + system messages if present.
    returns
    ---
    ChatState -> State with recent N messages
    """
    curr_message_len = len(state.messages)
    if curr_message_len <= window_size:
        return ChatState

    pruned_messages = []
    msg_count = 0

    # Iterate from older messages to maintain windows size and keep system message
    for i in range(curr_message_len-1, -1, -1):
        if state.messages[i].role == "system":
            pruned_messages.append(state.messages[i])
            continue
        if msg_count<=window_size:
            pruned_messages.append(state.messages[i])
            msg_count+=1
            continue
    ## Reverse the messages to maintain the order
    state.messages = pruned_messages[::-1]
    return state
    
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"batch_size": 64, "normalize_embeddings": True}
    )

def load_vectorstore(embedding_model):
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embedding_model
    )