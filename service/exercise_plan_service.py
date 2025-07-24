from sqlalchemy.orm import Session
from entity.exercise_plan import ExercisePlan, ExercisePlanCreateUpdate
from typing import List, Optional

class ExercisePlanService:
    @staticmethod
    def create(db: Session, data: ExercisePlanCreateUpdate) -> ExercisePlan:
        plan = ExercisePlan(**data)
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def update(db: Session, plan: ExercisePlan, data: ExercisePlanCreateUpdate) -> ExercisePlan:
        for field, value in data.items():
            setattr(plan, field, value)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def get_by_id(db: Session, plan_id: int) -> Optional[ExercisePlan]:
        return db.query(ExercisePlan).filter(ExercisePlan.id == plan_id).first()

    @staticmethod
    def get_all(db: Session) -> List[ExercisePlan]:
        return db.query(ExercisePlan).all() 