from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schema.dependencies import get_db
from entity.plans import Plan, PlanCreateUpdate, PlanResponse

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.post("/", response_model=PlanResponse)
def create_plan(plan_data: PlanCreateUpdate, db: Session = Depends(get_db)):
    plan = Plan(**plan_data.dict())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, plan_data: PlanCreateUpdate, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for field, value in plan_data.dict().items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/{plan_id}", response_model=dict)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.deleted = True
    db.commit()
    return {"message": f"Plan {plan_id} marked as deleted"}