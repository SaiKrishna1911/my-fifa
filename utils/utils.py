from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from openai import OpenAI
import os
import json

from schema.tool_schema import TOOL_SCHEMAS
from service.exercise_service import find_exercise
from service.meal_service import suggest_meals
from utils.clients import sync_client


def gpt_call(msgs: List[Dict[str, Any]]):
    resp = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=msgs,
        tools=TOOL_SCHEMAS,
        stream=False,
    )
    return resp.choices[0].message

def run_with_tools(messages: List[Dict[str, Any]], max_iters: int = 3):
    for _ in range(max_iters):
        assistant_msg = gpt_call(messages)
        msg: Dict[str, Any] = {"role": "assistant"}
        if assistant_msg.content:
            msg["content"] = assistant_msg.content
        if assistant_msg.tool_calls:
            msg["tool_calls"] = [tc.model_dump() for tc in assistant_msg.tool_calls]
        messages.append(msg)

        if not assistant_msg.tool_calls:
            return assistant_msg

        for call in assistant_msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            if name == "find_exercise":
                result = find_exercise(**args)
            elif name == "suggest_meals":
                result = suggest_meals(**args)
            # elif name == "validate_posture":
            #     result = PostureValidator.analyse_clip(**args)
            messages.append({
                "role": "tool",
                "name": name,
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
    raise HTTPException(500, "GPT never returned a final message")

def is_exit_message(message: str) -> str:
    response = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that determines whether a user wants to end the conversation.\n"
                    "If the message clearly sounds like an ending (e.g. 'thanks', 'bye', 'peace', 'cool got it', "
                    "'that's all for now', 'no further questions', etc.), then respond with a friendly, light-hearted "
                    "goodbye message. Be casual, appreciative, and avoid being cringe no coffee mug jokes.\n\n"
                    "If it's not an ending message, respond with just 'continue'."
                )
            },
            {
                "role": "user",
                "content": f"Does this message mean the user wants to end the conversation?\n\n\"{message}\""
            }
        ],
        temperature=0
    )
    reply = response.choices[0].message.content.strip()
    return reply