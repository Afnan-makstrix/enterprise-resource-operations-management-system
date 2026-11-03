"""
Project, Task & Work Breakdown Management Models
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="SET NULL"), nullable=True, index=True)
    project_manager_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False, index=True)
    start_date = Column(Date, default=date.today, nullable=False)
    target_end_date = Column(Date, nullable=False)
    actual_end_date = Column(Date, nullable=True)
    budget = Column(Numeric(15, 2), default=0.00, nullable=False)
    cost_to_date = Column(Numeric(15, 2), default=0.00, nullable=False)
    status = Column(String(20), default="PLANNING", nullable=False, index=True)
    priority = Column(String(20), default="MEDIUM", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    client = relationship("Client")
    manager = relationship("Employee")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"

    project_member_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_project = Column(String(50), default="CONTRIBUTOR", nullable=False)
    assigned_date = Column(Date, default=date.today, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    project = relationship("Project", back_populates="members")
    employee = relationship("Employee")

class ProjectTask(Base):
    __tablename__ = "project_tasks"

    task_id = Column(BigInteger, primary_key=True, index=True)
    task_code = Column(String(40), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True, index=True)
    reporter_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False)
    parent_task_id = Column(BigInteger, ForeignKey("project_tasks.task_id", ondelete="SET NULL"), nullable=True)
    priority = Column(String(20), default="MEDIUM", nullable=False)
    status = Column(String(20), default="TODO", nullable=False, index=True)
    estimated_hours = Column(Numeric(6, 2), default=0.00)
    actual_hours = Column(Numeric(6, 2), default=0.00)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("Employee", foreign_keys=[assigned_to])
    reporter = relationship("Employee", foreign_keys=[reporter_id])
    subtasks = relationship("ProjectTask", remote_side=[parent_task_id])
    time_logs = relationship("TaskTimeLog", back_populates="task", cascade="all, delete-orphan")

class TaskTimeLog(Base):
    __tablename__ = "task_time_logs"

    log_id = Column(BigInteger, primary_key=True, index=True)
    task_id = Column(BigInteger, ForeignKey("project_tasks.task_id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = Column(Date, default=date.today, nullable=False)
    hours_logged = Column(Numeric(5, 2), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    task = relationship("ProjectTask", back_populates="time_logs")
    employee = relationship("Employee")
