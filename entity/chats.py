from openai import BaseModel
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base, AuditMixin

class Chat(Base, AuditMixin):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    conversation = relationship("Conversation", back_populates="chats")

class ChatCreateUpdate(BaseModel):
    conversation_id: int
    user_query: str
    ai_response: str

class ChatResponse(BaseModel):
    id: int
    conversation_id: int
    user_query: str