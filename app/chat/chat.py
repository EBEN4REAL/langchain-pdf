
from langchain_openai import ChatOpenAI 
from langchain.prompts import PromptTemplate
from app.chat.models import ChatArgs
from app.chat.vector_stores import retriever_map
from app.chat.llms import llm_map
from app.chat.memories import memory_map
from app.chat.memories.sql_memory import build_memory
from app.chat.models import ChatArgs
import random
from app.chat.vector_stores.pinecone import build_retriever
from app.chat.llms.chatopenai import build_llm 
from app.chat.memories.sql_memory import build_memory
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain
from app.web.api import (
    set_conversation_components,
    get_conversation_components
)

def select_component(
    component_type, component_map, chat_args
):
    components = get_conversation_components(
        chat_args.conversation_id
    )
    previous_component = components[component_type]

    if previous_component:
        builder = component_map[previous_component]
        return previous_component, builder(chat_args)
    else:
        random_name = random.choice(list(component_map.keys()))
        builder = component_map[random_name]
        return random_name, builder(chat_args)

def build_chat(chat_args: ChatArgs):
    retriever_name, retriever = select_component(
        "retriever",
        retriever_map,
        chat_args
    )
    llm_name, llm = select_component(
        "llm",
        llm_map,
        chat_args
    )
    memory_name, memory = select_component(
        "memory",
        memory_map,
        chat_args
    )

    print(f"Running chain with - LLM: {llm_name}, Retriever: {retriever_name}, Memory: {memory_name}")
    print(f"Streaming enabled: {chat_args.streaming}")
    
    set_conversation_components(
        chat_args.conversation_id,
        llm=llm_name,
        retriever=retriever_name,
        memory=memory_name
    )
    
    # Improved condense question prompt - this is critical!
    condense_question_prompt = PromptTemplate.from_template(
        """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
If the follow up question is already standalone and doesn't reference the chat history, return it exactly as provided.

IMPORTANT: Preserve the original meaning and intent of the question. Do not change what is being asked.

Chat History:
{chat_history}

Follow Up Question: {question}

Standalone Question:"""
    )
    
    # Use non-streaming for question condensation, with temperature=0 for consistency
    condense_question_llm = ChatOpenAI(
        streaming=False,
        temperature=0,
        model="gpt-3.5-turbo"
    )

    # Improved QA prompt
    qa_prompt = PromptTemplate.from_template(
        """You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context provided, just say that you don't have enough information to answer. Don't make up an answer.

Context:
{context}

Question: {question}

Answer: Let me help you with that."""
    )

    chain = StreamingConversationalRetrievalChain.from_llm(
        llm=llm,
        condense_question_llm=condense_question_llm,
        condense_question_prompt=condense_question_prompt,
        retriever=retriever,
        memory=memory,
        verbose=True,
        return_source_documents=False,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
    )
    
    return chain
