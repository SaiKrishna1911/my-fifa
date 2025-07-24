from sqlalchemy.orm import Session
from entity.meal_plan import MealPlan, MealPlanCreateUpdate
from typing import List, Optional

class MealPlanService:
    @staticmethod
    def create(db: Session, data: MealPlanCreateUpdate) -> MealPlan:
        plan = MealPlan(**data)
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def update(db: Session, plan: MealPlan, data: MealPlanCreateUpdate) -> MealPlan:
        for field, value in data.items():
            setattr(plan, field, value)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def get_by_id(db: Session, plan_id: int, user_id: Optional[int] = None) -> Optional[MealPlan]:
        query = db.query(MealPlan).filter(MealPlan.id == plan_id)
        if user_id is not None:
            query = query.filter(MealPlan.user_id == user_id)
        return query.first()

    @staticmethod
    def get_all(db: Session, user_id: Optional[int] = None) -> List[MealPlan]:
        query = db.query(MealPlan)
        if user_id is not None:
            query = query.filter(MealPlan.user_id == user_id)
        return query.all() 