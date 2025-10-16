from langchain_openai import ChatOpenAI

def build_llm(chat_args, model_name) -> ChatOpenAI:
    """
    Build a ChatOpenAI instance with specified parameters.

    Args:
        chat_args: Object containing temperature and streaming flag

    Returns:
        ChatOpenAI: Configured ChatOpenAI instance
    """
    print(f"Building LLM with model: {model_name}, streaming: {chat_args.streaming}")
    return ChatOpenAI(
        # streaming=chat_args.streaming,
        streaming=True,
        model_name=model_name,
    )