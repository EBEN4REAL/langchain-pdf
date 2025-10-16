from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from queue import Queue
from typing import Any
import threading
import os
from dotenv import load_dotenv

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""
    
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue
        print("StreamingHandler initialized")

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM started")
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print(f"Token: {repr(token)}")
        self.queue.put(token)

    def on_llm_end(self, response, **kwargs):
        print("LLM ended")
        self.queue.put(None)

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        print(f"LLM error: {error}")
        self.queue.put(None)

def test_streaming():
    queue = Queue()
    handler = StreamingHandler(queue)
    
    # Create LLM with streaming enabled
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        streaming=True,  # CRITICAL!
        callbacks=[handler]
    )
    
    def run_llm():
        try:
            print("\n=== Starting LLM invocation ===")
            response = llm.invoke("Say 'Hello, World!' and then count to 5")
            print(f"\n=== Final response: {response} ===")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            queue.put(None)
    
    thread = threading.Thread(target=run_llm)
    thread.start()
    
    print("\n=== Streaming tokens: ===")
    token_count = 0
    while True:
        token = queue.get()
        if token is None:
            break
        token_count += 1
        print(token, end="", flush=True)
    
    thread.join()
    print(f"\n\n=== Test complete! Received {token_count} tokens ===")

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables!")
        print("Please set it in your .env file")
        exit(1)
    
    test_streaming()