from openai import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base, AuditMixin

class Conversation(Base, AuditMixin):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50))

    user = relationship("User", back_populates="conversations")
    chats = relationship("Chat", back_populates="conversation")

class ConversationCreateUpdate(BaseModel):
    user_id: int
    status: str

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    status: str