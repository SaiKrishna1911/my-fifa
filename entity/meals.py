from openai import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from entity.base import Base, AuditMixin

class Meal(Base, AuditMixin):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    suggested_meal = Column(JSON, nullable=False)

    user = relationship("User", back_populates="meals")

class MealCreateUpdate(BaseModel):
    user_id: int
    suggested_meal: dict

class MealResponse(BaseModel):
    id: int
    user_id: int
    suggested_meal: dict

    class Config:
        orm_mode = True