from fastapi import APIRouter, HTTPException

from constants.system_promt import SYSTEM_PROMPT
from schema.chat_schema import ChatTurn
from utils.utils import run_with_tools, is_exit_message

router = APIRouter()

@router.post("/coach/chat")
def chat_turn(body: ChatTurn):
    convo = [{"role": "system", "content": SYSTEM_PROMPT}] + body.messages
    final_message = run_with_tools(convo)

    content = final_message.content.strip()
    if not content:
        raise HTTPException(500, "Empty response")

    exit_flag = is_exit_message(content)
    is_exit = exit_flag.lower() != "continue"

    return {
        "response": content,
        "is_exit": is_exit
    }