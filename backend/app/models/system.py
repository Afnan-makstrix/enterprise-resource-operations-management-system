"""
System Audit Logging, Notifications & Global Settings
"""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(String(60), nullable=False, index=True)
    record_id = Column(String(50), nullable=False, index=True)
    action = Column(String(10), nullable=False, index=True)
    old_data = Column(JSONB, nullable=True)
    new_data = Column(JSONB, nullable=True)
    changed_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    changer = relationship("Employee")

class SystemNotification(Base):
    __tablename__ = "system_notifications"

    notification_id = Column(BigInteger, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(30), nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    action_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    recipient = relationship("Employee")

class CompanySetting(Base):
    __tablename__ = "company_settings"

    setting_id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(80), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    category = Column(String(50), default="GENERAL", nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
