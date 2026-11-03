"""
Department Pydantic Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class DepartmentBase(BaseModel):
    department_code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    budget: float = Field(0.0, ge=0)
    location: Optional[str] = "Headquarters"
    is_active: bool = True

class DepartmentCreate(DepartmentBase):
    manager_id: Optional[int] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[int] = None
    budget: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    is_active: Optional[bool] = None

class DepartmentOut(DepartmentBase):
    department_id: int
    manager_id: Optional[int] = None
    manager_name: Optional[str] = None
    headcount: Optional[int] = 0
    total_payroll: Optional[float] = 0.0
    created_at: datetime

    class Config:
        from_attributes = True
