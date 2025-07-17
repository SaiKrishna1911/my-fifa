import json
from typing import Optional

from fastapi import APIRouter, HTTPException, File, UploadFile, Form

from constants.system_promt import SYSTEM_PROMPT
from schema.chat_schema import ChatTurn
from utils.utils import run_with_tools, is_exit_message

router = APIRouter()

@router.post("/coach/chat")
def chat_turn(
    messages: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    try:
        messages_list = json.loads(messages)
        for msg in messages_list:
            if isinstance(msg.get("content"), dict):
                # Flatten content dictionary into a plain string with note appended
                text = msg["content"].get("text", "")
                note = msg["content"].get("note", "")
                msg["content"] = f"{text}\n\nNote: {note}" if note else text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid messages format: {str(e)}")

    convo = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_list
    if file:
        convo.append({"role": "user", "content": f"[User uploaded file: {file.filename}]"})
    final_result = run_with_tools(convo, file)

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