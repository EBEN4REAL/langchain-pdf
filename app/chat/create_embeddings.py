from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os

from app.chat.vector_stores.pinecone import vector_store

def create_embeddings_for_pdf(pdf_id: str, pdf_path: str):
    """
    Generate and store embeddings for the given pdf

    1. Extract text from the specified PDF.
    2. Divide the extracted text into manageable chunks.
    3. Generate an embedding for each chunk.
    4. Persist the generated embeddings.

    :param pdf_id: The unique identifier for the PDF.
    :param pdf_path: The file path to the PDF.

    Example Usage:

    create_embeddings_for_pdf('123456', '/path/to/pdf')
    """

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    loader = PyPDFLoader(pdf_path)
    docs = loader.load_and_split(text_splitter)
    
    for i, doc in enumerate(docs, start=1):
        # Safely set the page number from metadata or fallback
        doc.metadata["page"] = doc.metadata.get("page", i)
        doc.metadata["pdf_id"] = pdf_id
        doc.metadata["text"] = doc.page_content

    
    vector_store.add_documents(docs)
    print(f"Loaded {len(docs)} documents from the PDF.")