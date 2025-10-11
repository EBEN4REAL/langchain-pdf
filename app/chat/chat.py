from langchain_openai import ChatOpenAI 
from app.chat.models import ChatArgs
from app.chat.vector_stores.pinecone import build_retriever
from app.chat.llms.chatopenai import build_llm 
from app.chat.memories.sql_memory import build_memory
from app.chat.models import ChatArgs
from app.chat.vector_stores.pinecone import build_retriever
from app.chat.llms.chatopenai import build_llm 
from app.chat.memories.sql_memory import build_memory
# from langchain.chains import ConversationalRetrievalChain
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain

def build_chat(chat_args: ChatArgs):
    """
    Build a conversational retrieval chain for PDF Q&A.
    
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: A ConversationalRetrievalChain

    Example Usage:
        chat_args = ChatArgs(
            conversation_id="conv_123",
            pdf_id="pdf_456",
            streaming=True
        )
        chain = build_chat(chat_args)
        response = chain({"question": "What is this about?"})
    """
    retriever = build_retriever(chat_args)
    llm = build_llm(chat_args)
    condense_question_llm = ChatOpenAI(streaming=False)
    memory = build_memory(chat_args)

    return StreamingConversationalRetrievalChain.from_llm(
        llm=llm,
        condense_question_llm=condense_question_llm,
        retriever=retriever,
        memory=memory,
    )