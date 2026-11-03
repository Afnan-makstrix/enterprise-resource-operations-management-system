"""
FastAPI Security & Authentication Dependencies
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.employee import UserCredential, Employee
from backend.app.models.rbac import Role, Permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Employee:
    """Validates JWT access token and returns authenticated Employee instance."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    credential = db.query(UserCredential).filter(UserCredential.username == username).first()
    if credential is None or credential.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account does not exist or has been locked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employee = db.query(Employee).filter(
        Employee.employee_id == credential.employee_id,
        Employee.is_deleted == False
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee profile not found or has been deactivated"
        )

    # Set PostgreSQL session variables for Row Level Security (RLS) policies
    try:
        role_name = employee.role.role_name if employee.role else "Employee"
        db.execute(text(f"SET LOCAL app.current_user_id = '{employee.employee_id}';"))
        db.execute(text(f"SET LOCAL app.current_user_role = '{role_name}';"))
    except Exception:
        pass

    return employee

def require_role(allowed_roles: List[str]):
    """Role-Based Access Control dependency factory."""
    def role_checker(current_user: Employee = Depends(get_current_user)) -> Employee:
        user_role = current_user.role.role_name if current_user.role else ""
        if user_role not in allowed_roles and user_role != "Super Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
