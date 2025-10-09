import os
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from app.chat.embeddings.openai import embeddings

load_dotenv()

index_name = os.getenv("PINECONE_INDEX_NAME")
vector_store = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings,
    pinecone_api_key=os.getenv("PINECONE_API_KEY")
)