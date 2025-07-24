from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from entity.base import Base

class ExercisePlan(Base):
    __tablename__ = "exercise_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    duration_days = Column(Integer)
    description = Column(Text)
    level = Column(String(50))
    is_active = Column(Boolean, default=True)

    user_exercise_plans = relationship("UserExercisePlan", back_populates="exercise_plan")

class ExercisePlanCreateUpdate(BaseModel):
    name: str
    duration_days: Optional[int] = None
    description: Optional[str] = None
    level: Optional[str] = None
    is_active: Optional[bool] = True

class ExercisePlanResponse(ExercisePlanCreateUpdate):
    id: int
    class Config:
        orm_mode = True 