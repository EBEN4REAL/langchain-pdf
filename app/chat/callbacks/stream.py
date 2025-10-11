from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from queue import Queue
from typing import Any, Dict, List
import threading
from dotenv import load_dotenv
import os

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""
    
    def __init__(self, queue: Queue):
        self.queue = queue

    def on_chat_model_start(self, serialized, messages, run_id, **kwargs):
        if serialized["kwargs"]["streaming"]:
            self.streaming_run_ids.add(run_id)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.queue.put(token)

    def on_llm_end(self, response, run_id, **kwargs):
        if run_id in self.streaming_run_ids:
            self.queue.put(None)
            self.streaming_run_ids.remove(run_id)

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when LLM errors."""
        self.queue.put(None)