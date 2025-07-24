from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from schema.dependencies import get_db
from entity.meal_plan import MealPlanCreateUpdate, MealPlanResponse
from service.meal_plan_service import MealPlanService
from typing import Optional

router = APIRouter(prefix="/meal-plans", tags=["Meal Plans"])

@router.post("/", response_model=MealPlanResponse)
def create_meal_plan(data: MealPlanCreateUpdate, db: Session = Depends(get_db)):
    plan = MealPlanService.create(db, data.dict())
    return plan

@router.put("/{plan_id}", response_model=MealPlanResponse)
def update_meal_plan(plan_id: int, data: MealPlanCreateUpdate, db: Session = Depends(get_db)):
    plan = MealPlanService.get_by_id(db, plan_id, data.user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    updated = MealPlanService.update(db, plan, data.dict())
    return updated

@router.get("/", response_model=list[MealPlanResponse])
def list_meal_plans(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return MealPlanService.get_all(db, user_id)

@router.get("/{plan_id}", response_model=MealPlanResponse)
def get_meal_plan(plan_id: int, user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    plan = MealPlanService.get_by_id(db, plan_id, user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan 