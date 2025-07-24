from typing import Optional

from openai import BaseModel
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from entity.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    status = Column(String(50))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    goal = Column(String(100), nullable=True)
    _allergies = Column("allergies", Text)

    def __init__(self, **kwargs):
        allergies = kwargs.pop("allergies", None)
        super().__init__(**kwargs)
        if allergies is not None:
            self.allergies = allergies

    @hybrid_property
    def allergies(self) -> list[str]:
        return self._allergies.split(",") if self._allergies else []

    @allergies.setter
    def allergies(self, value: list[str]):
        self._allergies = ",".join(value) if value else ""

    meal_plans = relationship("MealPlan", back_populates="user")
    user_exercise_plans = relationship("UserExercisePlan", back_populates="user")
    daily_plan_trackings = relationship("DailyPlanTracking", back_populates="user")

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    height_cm: float
    weight_kg: float
    status: str
    allergies: Optional[list[str]] = []
    goal: Optional[str] = None

    class Config:
        orm_mode = True