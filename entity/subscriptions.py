from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base, AuditMixin

class Subscription(Base, AuditMixin):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(String(50))

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")

class SubscriptionCreateUpdate(BaseModel):
    user_id: int
    plan_id: int
    status: str

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str