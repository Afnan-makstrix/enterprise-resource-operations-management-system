"""
Attendance and Leave Management Models
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, UniqueConstraint
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from backend.app.database import Base

class LeaveType(Base):
    __tablename__ = "leave_types"

    leave_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    annual_allowance = Column(Integer, nullable=False)
    is_paid = Column(Boolean, default=True, nullable=False)
    carry_forward = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    balance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id", ondelete="RESTRICT"), nullable=False)
    year = Column(Integer, nullable=False)
    total_allocated = Column(Numeric(5, 2), nullable=False)
    used_days = Column(Numeric(5, 2), default=0.00, nullable=False)
    pending_days = Column(Numeric(5, 2), default=0.00, nullable=False)
    remaining_days = Column(Numeric(5, 2), server_default=FetchedValue()) # Generated column in PostgreSQL
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee")
    leave_type = relationship("LeaveType")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    leave_request_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id", ondelete="RESTRICT"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Numeric(4, 1), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType")
    approver = relationship("Employee", foreign_keys=[approved_by])

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    attendance_id = Column(BigInteger, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    work_date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="PRESENT", nullable=False, index=True)
    hours_worked = Column(Numeric(5, 2), default=0.00)
    overtime_hours = Column(Numeric(5, 2), default=0.00)
    ip_address = Column(String(45), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee")
