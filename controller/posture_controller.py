from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from schema.dependencies import get_db
from service.posture_validator import validate_posture
import base64
from datetime import date as dt_date
from service.daily_plan_tracking_service import DailyPlanTrackingService
import json
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter()

@router.post("/posture/validate")
async def validate_posture_api(
    video_file: UploadFile = File(...),
    exercise: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not (video_file.content_type.startswith("video/") or video_file.content_type == "image/gif"):
        raise HTTPException(status_code=400, detail="Only video or GIF files are accepted.")

    video_bytes = await video_file.read()
    video_b64 = base64.b64encode(video_bytes).decode("utf-8")

    result = validate_posture(exercise=exercise, video_b64=video_b64)
    # Try to parse calories burned, reps, and summary from result
    try:
        parsed = result if isinstance(result, dict) else json.loads(result)
        calories_burned = parsed.get("calories_burned") or 0
        reps = parsed.get("repetitions") or parsed.get("reps") or 0
        summary = parsed.get("summary") or parsed.get("text") or str(parsed)
    except Exception:
        calories_burned = 0
        reps = 0
        summary = str(result)
    today = dt_date.today().isoformat()
    DailyPlanTrackingService.log_exercise_event(db, user_id, today, summary, calories_burned, reps)
    return result