from sqlalchemy import Column, Integer, Float, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import date
from entity.base import Base

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    energy = Column(Float)
    calories = Column(Float)
    fats = Column(Float)
    proteins = Column(Float)
    carbs = Column(Float)
    meals_json = Column(JSON)

    user = relationship("User", back_populates="meal_plans")

class MealPlanCreateUpdate(BaseModel):
    user_id: Optional[int]
    date: date
    energy: Optional[float]
    calories: Optional[float]
    fats: Optional[float]
    proteins: Optional[float]
    carbs: Optional[float]
    meals_json: Optional[dict]

class MealPlanResponse(MealPlanCreateUpdate):
    id: int
    class Config:
        orm_mode = True 