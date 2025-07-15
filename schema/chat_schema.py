# schemas/chat_schema.py
from pydantic import BaseModel
from typing import List, Dict

class ChatTurn(BaseModel):
    messages: List[Dict[str, str]]