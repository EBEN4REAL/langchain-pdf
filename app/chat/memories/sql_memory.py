from typing import List
from pydantic import BaseModel
from langchain.memory import ConversationBufferMemory       
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.web.api import (
    get_messages_by_conversation_id,
    add_message_to_conversation
)


class SqlMessageHistory(BaseChatMessageHistory):
    """Custom chat history that stores messages in your database."""
    
    conversation_id: str
    
    def __init__(self, conversation_id: str):
        super().__init__()
        self.conversation_id = conversation_id
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from database."""
        db_messages = get_messages_by_conversation_id(self.conversation_id)
        
        langchain_messages = []
        for msg in db_messages:
            if msg.type == "human":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                langchain_messages.append(AIMessage(content=msg.content))
        
        return langchain_messages
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the database."""
        message_type = "human" if isinstance(message, HumanMessage) else "ai"
        add_message_to_conversation(
            conversation_id=self.conversation_id,
            content=message.content,
            role=message.type
        )
    
    def clear(self) -> None:
        """Clear conversation history (optional)."""
        pass

def build_memory(chat_args) -> ConversationBufferMemory:
    """
    Build conversation memory from database using chat_args.
    
    Args:
        chat_args: Object containing conversation_id
    
    Returns:
        ConversationBufferMemory: Memory object with database backend
    """
    chat_history = SqlMessageHistory(
        conversation_id=chat_args.conversation_id
    )
    
    return ConversationBufferMemory(
        chat_memory=chat_history,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )