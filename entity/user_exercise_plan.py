from sqlalchemy import Column, Integer, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import enum
from typing import Optional
from datetime import date
from entity.base import Base

class UserExercisePlanStatus(enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class UserExercisePlan(Base):
    __tablename__ = "user_exercise_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_plan_id = Column(Integer, ForeignKey("exercise_plans.id"), nullable=False)
    start_date = Column(Date)
    status = Column(Enum(UserExercisePlanStatus), default=UserExercisePlanStatus.active)

    user = relationship("User", back_populates="user_exercise_plans")
    exercise_plan = relationship("ExercisePlan", back_populates="user_exercise_plans")

class UserExercisePlanCreateUpdate(BaseModel):
    user_id: int
    exercise_plan_id: int
    start_date: date
    status: Optional[str] = "active"

class UserExercisePlanResponse(UserExercisePlanCreateUpdate):
    id: int
    class Config:
        orm_mode = True 