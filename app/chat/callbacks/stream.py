
from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from queue import Queue
from typing import Any, Dict, List, Set
import threading
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""
    
    def __init__(self, queue: Queue):
        super().__init__()  # Call parent constructor
        self.queue = queue
        self.streaming_run_ids: Set[uuid.UUID] = set()  # Initialize this!

    def on_chat_model_start(self, serialized, messages, run_id, **kwargs):
        # Safely check for streaming flag
        try:
            if serialized.get("kwargs", {}).get("streaming", False):
                self.streaming_run_ids.add(run_id)
        except (KeyError, TypeError):
            # If structure is different, assume streaming
            self.streaming_run_ids.add(run_id)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.queue.put(token)

    def on_llm_end(self, response, run_id, **kwargs):
        if run_id in self.streaming_run_ids:
            self.streaming_run_ids.discard(run_id)  # Use discard instead of remove
        self.queue.put(None)  # Always signal end

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when LLM errors."""
        self.queue.put(None)