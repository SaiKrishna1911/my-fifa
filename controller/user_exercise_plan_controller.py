from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from schema.dependencies import get_db
from entity.user_exercise_plan import UserExercisePlanCreateUpdate, UserExercisePlanResponse
from service.user_exercise_plan_service import UserExercisePlanService
from typing import Optional

router = APIRouter(prefix="/user-exercise-plans", tags=["User Exercise Plans"])

@router.post("/", response_model=UserExercisePlanResponse)
def create_user_exercise_plan(data: UserExercisePlanCreateUpdate, db: Session = Depends(get_db)):
    plan = UserExercisePlanService.create(db, data.dict())
    return plan

@router.put("/{plan_id}", response_model=UserExercisePlanResponse)
def update_user_exercise_plan(plan_id: int, data: UserExercisePlanCreateUpdate, db: Session = Depends(get_db)):
    plan = UserExercisePlanService.get_by_id(db, plan_id, data.user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="User exercise plan not found")
    updated = UserExercisePlanService.update(db, plan, data.dict())
    return updated

@router.get("/", response_model=list[UserExercisePlanResponse])
def list_user_exercise_plans(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return UserExercisePlanService.get_all(db, user_id)

@router.get("/{plan_id}", response_model=UserExercisePlanResponse)
def get_user_exercise_plan(plan_id: int, user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    plan = UserExercisePlanService.get_by_id(db, plan_id, user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="User exercise plan not found")
    return plan 