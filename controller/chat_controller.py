import json
from typing import Optional, List

from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends, Query
from sqlalchemy.orm import Session
from schema.dependencies import get_db
from entity.chats import ChatCreateUpdate, ChatResponse
from service.chat_service import ChatService

from constants.system_promt import SYSTEM_PROMPT
from schema.chat_schema import ChatTurn
from utils.utils import run_with_tools, is_exit_message

router = APIRouter()

@router.post("/chats/", response_model=ChatResponse)
def create_chat(data: ChatCreateUpdate, db: Session = Depends(get_db)):
    chat = ChatService.create(db, data.dict())
    return chat

@router.get("/chats/", response_model=List[ChatResponse])
def list_chats(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return ChatService.get_all(db, user_id)

@router.get("/chats/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int, user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    chat = ChatService.get_by_id(db, chat_id, user_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/coach/chat")
def chat_turn(
    user_id: int = Form(...),
    messages: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        result = ChatService.handle_coach_chat(user_id=user_id, messages=messages, file=file, db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result