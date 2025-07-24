from sqlalchemy.orm import Session
from entity.chats import Chat, ChatCreateUpdate
from typing import List, Optional

class ChatService:
    @staticmethod
    def create(db: Session, data: dict) -> Chat:
        chat = Chat(**data)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def get_by_id(db: Session, chat_id: int, user_id: Optional[int] = None) -> Optional[Chat]:
        query = db.query(Chat).filter(Chat.id == chat_id)
        if user_id is not None:
            query = query.filter(Chat.user_id == user_id)
        return query.first()

    @staticmethod
    def get_all(db: Session, user_id: Optional[int] = None) -> List[Chat]:
        query = db.query(Chat)
        if user_id is not None:
            query = query.filter(Chat.user_id == user_id)
        return query.all()

    @staticmethod
    def get_by_room(db: Session, room_id: int) -> List[Chat]:
        return db.query(Chat).filter(Chat.room_id == room_id).order_by(Chat.id).all()

    @staticmethod
    def get_latest_by_room(db: Session, user_id: int, room_id: int) -> Optional[Chat]:
        return db.query(Chat).filter(Chat.user_id == user_id, Chat.room_id == room_id).order_by(Chat.id.desc()).first()

    @staticmethod
    def get_all_chats_for_user(db: Session, user_id: int) -> List[Chat]:
        return db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at).all()

    @staticmethod
    def get_chats_for_user_on_date(db: Session, user_id: int, date) -> List[Chat]:
        from sqlalchemy import func
        return db.query(Chat).filter(
            Chat.user_id == user_id,
            func.date(Chat.created_at) == date
        ).order_by(Chat.created_at).all()

    @staticmethod
    def handle_coach_chat(user_id: int, messages: str, file, db: Session):
        from service.chat_room_service import ChatRoomService
        from entity.chats import ChatCreateUpdate
        from constants.system_promt import SYSTEM_PROMPT
        from utils.utils import run_with_tools, is_exit_message
        import json
        from datetime import datetime
        from service.daily_plan_tracking_service import DailyPlanTrackingService

        # 1. Parse user messages
        try:
            messages_list = json.loads(messages)
        except Exception as e:
            raise ValueError(f"Invalid messages format: {str(e)}")

        # 2. Detect special requests
        user_query_text = " ".join([msg.get("content", "") if isinstance(msg.get("content"), str) else str(msg.get("content")) for msg in messages_list])
        is_past_convo_request = any(x in user_query_text.lower() for x in ["past conversation", "previous chat", "history", "old conversation", "old chat", "previous conversation"])
        is_journal_request = any(x in user_query_text.lower() for x in ["journal", "summary of the day", "today's progress", "daily journal", "fitness journal"])

        convo = []
        context = {}

        if is_past_convo_request:
            # Gather all chats for the user (all rooms)
            chat_history = ChatService.get_all_chats_for_user(db, user_id)
            for chat in chat_history:
                convo.append({"role": "user", "content": chat.user_context})
                convo.append({"role": "system", "content": chat.system_context})
            context["type"] = "past_conversations"
        elif is_journal_request:
            # Try to extract date from user query, fallback to today
            import re
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", user_query_text)
            if date_match:
                journal_date = date_match.group(1)
            else:
                journal_date = datetime.utcnow().date().isoformat()
            # Gather daily plan for the day
            daily_plan = None
            daily_plans = DailyPlanTrackingService.get_all(db, user_id)
            for plan in daily_plans:
                if str(plan.date) == journal_date:
                    daily_plan = plan
                    break
            # Gather all chats for the user on that date
            chats_on_date = ChatService.get_chats_for_user_on_date(db, user_id, journal_date)
            for chat in chats_on_date:
                convo.append({"role": "user", "content": chat.user_context})
                convo.append({"role": "system", "content": chat.system_context})
            context["type"] = "journal"
            context["journal_date"] = journal_date
            context["daily_plan"] = daily_plan.dict() if daily_plan else None
        else:
            # Default: use active room context
            room = ChatRoomService.get_active_for_user(db, user_id)
            if not room:
                room = ChatRoomService.create(db, {"user_id": user_id, "room_status": "active"})
            chat_history = ChatService.get_by_room(db, room.id)
            for chat in chat_history:
                convo.append({"role": "user", "content": chat.user_context})
                convo.append({"role": "system", "content": chat.system_context})
            context["type"] = "default"

        # 3. Add new user message
        convo += messages_list
        if file:
            convo.append({"role": "user", "content": f"[User uploaded file: {file.filename}]"})
        # 4. Add context to system prompt
        system_prompt = SYSTEM_PROMPT.replace("{context}", json.dumps(context, default=str))
        convo = [{"role": "system", "content": system_prompt}] + convo
        final_result = run_with_tools(convo, file, db=db, user_id=user_id)

        if isinstance(final_result, dict) and "structured" in final_result:
            content_obj = final_result["structured"]
            content_for_exit = json.dumps(content_obj, ensure_ascii=False)
        elif isinstance(final_result, dict) and "text" in final_result:
            content_obj = final_result["text"]
            content_for_exit = content_obj
        else:
            content_obj = getattr(final_result, "content", "").strip()
            content_for_exit = content_obj

        exit_flag = is_exit_message(content_for_exit)
        is_exit = exit_flag.lower() != "continue"

        # 5. Log chat turn with room_id (use active room for logging)
        room = ChatRoomService.get_active_for_user(db, user_id)
        if not room:
            room = ChatRoomService.create(db, {"user_id": user_id, "room_status": "active"})
        chat_data = ChatCreateUpdate(
            user_id=user_id,
            user_context=messages,
            system_context=json.dumps(content_obj, ensure_ascii=False) if isinstance(content_obj, (dict, list)) else str(content_obj),
            is_exit_msg=is_exit,
            room_id=room.id
        )
        ChatService.create(db, chat_data.dict())

        # 6. If exit, set room inactive
        if is_exit:
            ChatRoomService.set_inactive(db, room)

        return {
            "role": "system",
            "content": content_obj,
            "is_exit": is_exit,
            "room_id": room.id
        } 