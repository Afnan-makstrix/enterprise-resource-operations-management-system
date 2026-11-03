"""
Authentication and Identity Router
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.config import settings
from backend.app.core.security import verify_password, create_access_token
from backend.app.core.dependencies import get_current_user
from backend.app.models.employee import UserCredential, Employee
from backend.app.schemas.auth import LoginRequest, TokenResponse, UserProfileOut

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login.
    Validates username and password against PostgreSQL credentials.
    """
    credential = db.query(UserCredential).filter(UserCredential.username == form_data.username).first()
    if not credential or not verify_password(form_data.password, credential.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employee = db.query(Employee).filter(Employee.employee_id == credential.employee_id).first()
    if not employee or employee.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee profile inactive or suspended"
        )

    role_name = employee.role.role_name if employee.role else "Employee"
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": credential.username,
            "emp_id": employee.employee_id,
            "role": role_name
        },
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=credential.credential_id,
        username=credential.username,
        role=role_name,
        employee_id=employee.employee_id,
        full_name=employee.full_name
    )

@router.post("/json-login", response_model=TokenResponse)
def json_login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    """JSON body login endpoint for single-page React frontend clients."""
    credential = db.query(UserCredential).filter(UserCredential.username == payload.username).first()
    if not credential or not verify_password(payload.password, credential.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    employee = db.query(Employee).filter(Employee.employee_id == credential.employee_id).first()
    if not employee or employee.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee account inactive"
        )

    role_name = employee.role.role_name if employee.role else "Employee"
    access_token = create_access_token(
        data={"sub": credential.username, "emp_id": employee.employee_id, "role": role_name}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=credential.credential_id,
        username=credential.username,
        role=role_name,
        employee_id=employee.employee_id,
        full_name=employee.full_name
    )

@router.get("/me", response_model=UserProfileOut)
def read_current_user_profile(
    current_user: Employee = Depends(get_current_user)
):
    """Fetches currently authenticated user profile and permissions."""
    return UserProfileOut(
        employee_id=current_user.employee_id,
        employee_number=current_user.employee_number,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        email=current_user.email,
        job_title=current_user.job_title,
        department_name=current_user.department.name if current_user.department else None,
        role_name=current_user.role.role_name if current_user.role else "Employee",
        employment_type=current_user.employment_type,
        status=current_user.status,
        salary=float(current_user.salary)
    )
