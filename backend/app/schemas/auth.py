"""
Authentication Pydantic Schemas
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    role: str
    employee_id: int
    full_name: str

class UserProfileOut(BaseModel):
    employee_id: int
    employee_number: str
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr
    job_title: str
    department_name: Optional[str]
    role_name: str
    employment_type: str
    status: str
    salary: float

    class Config:
        from_attributes = True
