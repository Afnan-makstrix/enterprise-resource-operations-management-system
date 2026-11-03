"""
Base model and common mixins for SQLAlchemy ORM models.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from backend.app.database import Base

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
