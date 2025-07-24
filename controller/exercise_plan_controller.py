from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schema.dependencies import get_db
from entity.exercise_plan import ExercisePlanCreateUpdate, ExercisePlanResponse
from service.exercise_plan_service import ExercisePlanService

router = APIRouter(prefix="/exercise-plans", tags=["Exercise Plans"])

@router.post("/", response_model=ExercisePlanResponse)
def create_exercise_plan(plan_data: ExercisePlanCreateUpdate, db: Session = Depends(get_db)):
    plan = ExercisePlanService.create(db, plan_data.dict())
    return plan

@router.put("/{plan_id}", response_model=ExercisePlanResponse)
def update_exercise_plan(plan_id: int, plan_data: ExercisePlanCreateUpdate, db: Session = Depends(get_db)):
    plan = ExercisePlanService.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Exercise plan not found")
    updated = ExercisePlanService.update(db, plan, plan_data.dict())
    return updated

@router.get("/", response_model=list[ExercisePlanResponse])
def list_exercise_plans(db: Session = Depends(get_db)):
    return ExercisePlanService.get_all(db)

@router.get("/{plan_id}", response_model=ExercisePlanResponse)
def get_exercise_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = ExercisePlanService.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Exercise plan not found")
    return plan 