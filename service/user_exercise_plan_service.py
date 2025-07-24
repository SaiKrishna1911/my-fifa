from sqlalchemy.orm import Session
from entity.user_exercise_plan import UserExercisePlan, UserExercisePlanCreateUpdate
from typing import List, Optional

class UserExercisePlanService:
    @staticmethod
    def create(db: Session, data: UserExercisePlanCreateUpdate) -> UserExercisePlan:
        plan = UserExercisePlan(**data)
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def update(db: Session, plan: UserExercisePlan, data: UserExercisePlanCreateUpdate) -> UserExercisePlan:
        for field, value in data.items():
            setattr(plan, field, value)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def get_by_id(db: Session, plan_id: int, user_id: Optional[int] = None) -> Optional[UserExercisePlan]:
        query = db.query(UserExercisePlan).filter(UserExercisePlan.id == plan_id)
        if user_id is not None:
            query = query.filter(UserExercisePlan.user_id == user_id)
        return query.first()

    @staticmethod
    def get_all(db: Session, user_id: Optional[int] = None) -> List[UserExercisePlan]:
        query = db.query(UserExercisePlan)
        if user_id is not None:
            query = query.filter(UserExercisePlan.user_id == user_id)
        return query.all() 