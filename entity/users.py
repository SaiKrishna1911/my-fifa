from typing import Optional

from openai import BaseModel
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from entity.base import AuditMixin, Base


class User(Base, AuditMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    status = Column(String(50))
    height_cm = Column(Float)
    weight_kg = Column(Float)
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

    conversations = relationship("Conversation", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    meals = relationship("Meal", back_populates="user")

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    height_cm: float
    weight_kg: float
    status: str
    allergies: Optional[list[str]] = []

    class Config:
        orm_mode = True