from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends

from schema.dependencies import get_db
from service.food_vision_service import estimate_nutrition_from_image
from sqlalchemy.orm import Session
from datetime import date as dt_date
import json
from service.daily_plan_tracking_service import DailyPlanTrackingService

router = APIRouter()

@router.post("/analyze-food-image")
async def analyze_food_image(
    file: UploadFile = File(...),
    goal: Optional[str] = Form(None),
    user_id: int = Form(...),
    confirm: bool = Form(False),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    result = estimate_nutrition_from_image(contents, goal)
    # Try to parse calories and summary from result
    try:
        parsed = json.loads(result) if isinstance(result, str) else result
        calories = parsed.get("calories") or parsed.get("calories_kcal") or 0
        summary = parsed.get("text") or str(parsed)
    except Exception:
        calories = 0
        summary = str(result)
    today = dt_date.today().isoformat()
    if confirm:
        DailyPlanTrackingService.log_food_event(db, user_id, today, summary, calories)
    return {"result": result}