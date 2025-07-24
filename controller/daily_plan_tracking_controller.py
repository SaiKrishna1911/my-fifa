from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schema.dependencies import get_db
from entity.daily_plan_tracking import DailyPlanTrackingCreateUpdate, DailyPlanTrackingResponse
from service.daily_plan_tracking_service import DailyPlanTrackingService

router = APIRouter(prefix="/users/{user_id}/daily-plan-tracking", tags=["Daily Plan Tracking"])

@router.post("/", response_model=DailyPlanTrackingResponse)
def create_daily_plan_tracking(user_id: int, data: DailyPlanTrackingCreateUpdate, db: Session = Depends(get_db)):
    data_dict = data.dict()
    data_dict['user_id'] = user_id
    tracking = DailyPlanTrackingService.create(db, data_dict)
    return tracking

@router.put("/{tracking_id}", response_model=DailyPlanTrackingResponse)
def update_daily_plan_tracking(user_id: int, tracking_id: int, data: DailyPlanTrackingCreateUpdate, db: Session = Depends(get_db)):
    tracking = DailyPlanTrackingService.get_by_id(db, tracking_id, user_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Daily plan tracking not found")
    updated = DailyPlanTrackingService.update(db, tracking, data.dict())
    return updated

@router.get("/", response_model=list[DailyPlanTrackingResponse])
def list_daily_plan_tracking(user_id: int, db: Session = Depends(get_db)):
    return DailyPlanTrackingService.get_all(db, user_id)

@router.get("/{tracking_id}", response_model=DailyPlanTrackingResponse)
def get_daily_plan_tracking(user_id: int, tracking_id: int, db: Session = Depends(get_db)):
    tracking = DailyPlanTrackingService.get_by_id(db, tracking_id, user_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Daily plan tracking not found")
    return tracking 