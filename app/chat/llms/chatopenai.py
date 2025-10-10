from langchain_openai import ChatOpenAI

def build_llm(chat_args) -> ChatOpenAI:
    """
    Build a ChatOpenAI instance with specified parameters.

    Args:
        chat_args: Object containing temperature and streaming flag

    Returns:
        ChatOpenAI: Configured ChatOpenAI instance
    """
    return ChatOpenAI()