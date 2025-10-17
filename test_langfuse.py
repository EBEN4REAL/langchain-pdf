# test_langfuse.py
import os
from dotenv import load_dotenv
load_dotenv()

from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("UPLOAD_URL", "https://prod-upload-langchain.fly.dev"),
)

# Create a test trace
trace = langfuse.trace(name="test-trace")
print(f"Test trace created: {trace.id}")

# Flush to send immediately
langfuse.flush()
print("Data flushed to Langfuse")