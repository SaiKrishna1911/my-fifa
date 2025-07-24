from openai import BaseModel
from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from entity.base import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    room_status = Column(String(15), default="active")

    user = relationship("User")
    chats = relationship("Chat", back_populates="room")

class ChatRoomCreate(BaseModel):
    user_id: int
    room_status: Optional[str] = "active"

class ChatRoomResponse(ChatRoomCreate):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_context = Column(Text)
    system_context = Column(Text)
    is_exit_msg = Column(Boolean, default=False)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    room = relationship("ChatRoom", back_populates="chats")

class ChatCreateUpdate(BaseModel):
    user_id: int
    user_context: str = None
    system_context: str = None
    is_exit_msg: bool = False
    room_id: Optional[int] = None
    created_at: Optional[datetime] = None

class ChatResponse(BaseModel):
    id: int
    user_id: int
    user_context: str = None
    system_context: str = None
    is_exit_msg: bool = False
    room_id: Optional[int] = None
    created_at: Optional[datetime] = None