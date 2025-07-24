from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from openai import OpenAI
import os
import json

from schema.tool_schema import TOOL_SCHEMAS
from service.exercise_service import find_exercise
from service.food_vision_service import estimate_nutrition_from_image
from service.meal_service import suggest_meals
from service.posture_validator import validate_posture
from utils.clients import sync_client


def gpt_call(msgs: List[Dict[str, Any]], file: Optional[Any] = None):
    messages = msgs
    if file:
        file_context = (
            f"User uploaded a file named {file.filename}. "
            "If it's an image (jpg/png/jpeg), it’s likely a food photo — assume the user wants a nutrition analysis. "
            "If it's a video (mp4/mov/gif/webm/gif), assume it’s a workout form video — decide based on user query whether to analyze posture. "
            "Do not ask for reconfirmation — infer intent based on filename and user prompt like 'analyze this for me'."
            "If the user says he did an exercise, or any kind of physical activity, log it as an exercise event into journal. call log_exercise_event "
        )
        messages = [{"role": "system", "content": file_context}] + msgs
    resp = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
        stream=False,
    )
    return resp.choices[0].message

def run_with_tools(messages: List[Dict[str, Any]], file: Optional[Any] = None, max_iters: int = 3, db=None, user_id=None):
    from datetime import date as dt_date
    from service.daily_plan_tracking_service import DailyPlanTrackingService
    today = dt_date.today().isoformat()
    for _ in range(max_iters):
        assistant_msg = gpt_call(messages, file=file)
        msg: Dict[str, Any] = {"role": "assistant"}
        if assistant_msg.content:
            msg["content"] = assistant_msg.content
        if assistant_msg.tool_calls:
            msg["tool_calls"] = [tc.model_dump() for tc in assistant_msg.tool_calls]
        messages.append(msg)
        if not assistant_msg.tool_calls:
            try:
                structured = json.loads(assistant_msg.content.strip())
                return {"structured": structured}
            except json.JSONDecodeError:
                return {"text": assistant_msg.content.strip()}

        print(assistant_msg.tool_calls)
        for call in assistant_msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            # Try to get user_id from args or fallback
            uid = args.get("user_id") or user_id
            if name == "find_exercise":
                result = find_exercise(**args)
            elif name == "suggest_meals":
                result = suggest_meals(**args)
            elif name == "validate_posture":
                if "video_b64" in args and file:
                    import base64
                    file_content = base64.b64encode(file.file.read()).decode()
                    file.file.seek(0)
                    args["video_b64"] = file_content
                result = validate_posture(**args)
                # Log exercise event
                if db and uid:
                    try:
                        calories_burned = result.get("calories_burned") or 0
                        reps = result.get("repetitions") or result.get("reps") or 0
                        summary = result.get("summary") or result.get("text") or str(result)
                        protein = result.get("protein") or 0
                        carbohydrates = result.get("carbohydrates") or 0
                        fat = result.get("fat") or 0
                        fiber = result.get("fiber") or 0
                        DailyPlanTrackingService.log_exercise_event(
                            db, uid, today, summary, calories_burned, reps,
                            protein=protein,
                            carbohydrates=carbohydrates,
                            fat=fat,
                            fiber=fiber
                        )
                    except Exception:
                        pass
            elif name == "estimate_nutrition_from_image":
                if "image_b64" in args and file:
                    import base64
                    image_content = base64.b64encode(file.file.read()).decode()
                    file.file.seek(0)  # Reset stream just in case
                    args["image_b64"] = image_content
                    args["confirm"] = True
                    args["user_id"] = uid
                    args["db"] = db
                result = estimate_nutrition_from_image(**args)
            elif name == "log_exercise_event":
                if db and uid:
                    try:
                        print("ARGS", args)
                        DailyPlanTrackingService.log_exercise_event(
                            db=db,
                            user_id=uid,
                            date=args.get("date"),
                            exercise_summary=args.get("summary", "Exercise"),
                            calories_burned=args.get("calories_burned", 0),
                            reps=args.get("reps_done")
                        )
                    except Exception as e:
                        print(f"[ERROR] Failed to log exercise event: {e}")
            result = {}
            messages.append({
                "role": "tool",
                "name": name,
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
        else:
            # fallback: handle structured exercise data from GPT response
            try:
                structured = json.loads(assistant_msg.content.strip())
                if db and uid and "calories_burned" in structured:
                    DailyPlanTrackingService.log_exercise_event(
                        db=db,
                        user_id=uid,
                        date=today,
                        exercise_summary=structured.get("exercise", "Unspecified exercise"),
                        calories_burned=structured.get("calories_burned", 0),
                        reps=None,
                        protein=structured.get("protein", 0),
                        carbohydrates=structured.get("carbohydrates", 0),
                        fat=structured.get("fats", 0),  # Match to DB field `fat`
                        fiber=structured.get("fiber", 0),
                    )
            except Exception:
                pass

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