from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, DECIMAL
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class AuditMixin:
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), default="system")
    updated_by = Column(String(100), default="system")