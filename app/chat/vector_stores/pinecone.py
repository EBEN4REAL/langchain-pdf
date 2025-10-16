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

def build_retriever(chat_args, k) -> PineconeVectorStore:
    """
    Build a retriever from Pinecone vector store filtered by PDF ID.
    
    Args:
        chat_args: Object containing pdf_id and other chat parameters
    
    Returns:
        Retriever: Configured Pinecone retriever
    """
    return vector_store.as_retriever(
        search_kwargs={
            "filter": {"pdf_id": chat_args.pdf_id},
            "k": k
        }
    )