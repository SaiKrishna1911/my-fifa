from sqlalchemy import Column, Integer, Date, Boolean, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from entity.base import Base
from datetime import date

class DailyPlanTracking(Base):
    __tablename__ = "daily_plan_tracking"
    __table_args__ = (UniqueConstraint('user_id', 'date', name='unique_user_date'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    exercise_done = Column(Boolean, default=False)
    exercise_summary = Column(Text)
    meals_logged = Column(Boolean, default=False)
    meal_summary = Column(Text)
    calories_burned = Column(Float)
    calories_intake = Column(Float)
    reps_done = Column(Integer)
    form_score = Column(Float)
    journal_notes = Column(Text)
    protein = Column(Float)
    carbohydrates = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)

    user = relationship("User", back_populates="daily_plan_trackings")

class DailyPlanTrackingCreateUpdate(BaseModel):
    user_id: int
    date: str
    exercise_done: Optional[bool] = False
    exercise_summary: Optional[str]
    meals_logged: Optional[bool] = False
    meal_summary: Optional[str]
    calories_burned: Optional[float]
    calories_intake: Optional[float]
    reps_done: Optional[int]
    form_score: Optional[float]
    journal_notes: Optional[str]
    protein: Optional[float]
    carbohydrates: Optional[float]
    fat: Optional[float]
    fiber: Optional[float]

class DailyPlanTrackingResponse(DailyPlanTrackingCreateUpdate):
    id: int
    date: date  # Change type from str to date
    class Config:
        orm_mode = True 