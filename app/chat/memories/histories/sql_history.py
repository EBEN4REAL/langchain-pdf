from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import List

from app.web.api import (
    get_messages_by_conversation_id,
    add_message_to_conversation
)

class SqlMessageHistory(BaseChatMessageHistory):
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Return messages as a list"""
        msgs = get_messages_by_conversation_id(self.conversation_id)
        return list(msgs) if msgs else []
    
    def add_message(self, message: BaseMessage) -> None:
        add_message_to_conversation(
            conversation_id=self.conversation_id,
            role=message.type,
            content=message.content
        )

    def clear(self) -> None:
        pass