from sqlalchemy import Column, Integer, String, DECIMAL, Text, Boolean
from sqlalchemy.orm import relationship
from entity.base import Base, AuditMixin
from pydantic import BaseModel
from typing import Optional


class Plan(Base, AuditMixin):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2))
    goal = Column(Text)
    duration_days = Column(Integer)
    deleted = Column(Boolean, default=False)

    subscriptions = relationship("Subscription", back_populates="plan")



class PlanCreateUpdate(BaseModel):
    name: str
    price: float
    goal: Optional[str] = None
    duration_days: int

class PlanResponse(PlanCreateUpdate):
    id: int
    deleted: bool

    class Config:
        orm_mode = True