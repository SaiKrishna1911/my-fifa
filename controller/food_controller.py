from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from service.food_vision_service import estimate_nutrition_from_image

router = APIRouter()

@router.post("/analyze-food-image")
async def analyze_food_image(file: UploadFile = File(...), goal: Optional[str] = Form(None)):
    contents = await file.read()
    result = estimate_nutrition_from_image(contents, goal)
    return {"result": result}