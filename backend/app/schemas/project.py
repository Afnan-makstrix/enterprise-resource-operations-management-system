"""
Project and Task Management Pydantic Schemas
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    project_code: str
    name: str
    description: Optional[str] = None
    client_id: Optional[int] = None
    project_manager_id: int
    start_date: date
    target_end_date: date
    budget: float = Field(0.0, ge=0)
    status: str = "PLANNING"
    priority: str = "MEDIUM"

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    project_id: int
    client_name: Optional[str] = None
    project_manager_name: Optional[str] = None
    cost_to_date: float
    total_tasks: Optional[int] = 0
    completed_tasks: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    task_code: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: str = "MEDIUM"
    status: str = "TODO"
    estimated_hours: float = 0.0
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[date] = None

class TaskOut(TaskBase):
    task_id: int
    project_id: int
    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: int
    reporter_name: Optional[str] = None
    actual_hours: float
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
