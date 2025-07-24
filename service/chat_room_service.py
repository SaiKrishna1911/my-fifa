from sqlalchemy.orm import Session
from entity.chats import ChatRoom, ChatRoomCreate
from typing import Optional

class ChatRoomService:
    @staticmethod
    def create(db: Session, data: dict) -> ChatRoom:
        room = ChatRoom(**data)
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def get_active_for_user(db: Session, user_id: int) -> Optional[ChatRoom]:
        return db.query(ChatRoom).filter(ChatRoom.user_id == user_id, ChatRoom.room_status == "active").order_by(ChatRoom.created_at.desc()).first()

    @staticmethod
    def set_inactive(db: Session, room: ChatRoom):
        room.room_status = "inactive"
        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def get_by_id(db: Session, room_id: int) -> Optional[ChatRoom]:
        return db.query(ChatRoom).filter(ChatRoom.id == room_id).first() 