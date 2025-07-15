import json

from fastapi import APIRouter, HTTPException

from constants.system_promt import SYSTEM_PROMPT
from schema.chat_schema import ChatTurn
from utils.utils import run_with_tools, is_exit_message

router = APIRouter()

@router.post("/coach/chat")
def chat_turn(body: ChatTurn):
    convo = [{"role": "system", "content": SYSTEM_PROMPT}] + body.messages
    final_result = run_with_tools(convo)

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

    return {
        "role": "system",
        "content": content_obj,
        "is_exit": is_exit
    }