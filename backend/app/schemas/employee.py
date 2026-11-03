"""
Employee Domain Pydantic Schemas
"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

class EmployeeBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    job_title: str = Field(..., max_length=100)
    department_id: int
    manager_id: Optional[int] = None
    role_id: int
    salary: float = Field(..., gt=0)
    employment_type: str = "FULL_TIME"
    status: str = "ACTIVE"

class EmployeeCreate(EmployeeBase):
    employee_number: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    role_id: Optional[int] = None
    salary: Optional[float] = Field(None, gt=0)
    employment_type: Optional[str] = None
    status: Optional[str] = None

class EmployeeOut(BaseModel):
    employee_id: int
    employee_number: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: Optional[str]
    job_title: str
    department_id: int
    department_name: Optional[str] = None
    manager_id: Optional[int]
    manager_name: Optional[str] = None
    role_id: int
    role_name: Optional[str] = None
    hire_date: date
    salary: float
    employment_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
