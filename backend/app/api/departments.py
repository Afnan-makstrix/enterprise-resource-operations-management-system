"""
Department Management API Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.employee import Department, Employee
from backend.app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["Department Management"])

@router.get("/", response_model=List[DepartmentOut])
def list_departments(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists all active corporate departments with aggregated headcount and payroll figures."""
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    
    # Aggregate headcounts and payroll
    stats = db.query(
        Employee.department_id,
        func.count(Employee.employee_id).label("headcount"),
        func.sum(Employee.salary).label("total_payroll")
    ).filter(
        Employee.is_deleted == False,
        Employee.status == "ACTIVE"
    ).group_by(Employee.department_id).all()

    stats_map = {s.department_id: (s.headcount, float(s.total_payroll or 0.0)) for s in stats}

    results = []
    for d in departments:
        hc, pr = stats_map.get(d.department_id, (0, 0.0))
        results.append(DepartmentOut(
            department_id=d.department_id,
            department_code=d.department_code,
            name=d.name,
            description=d.description,
            manager_id=d.manager_id,
            manager_name=d.manager.full_name if d.manager else None,
            budget=float(d.budget),
            location=d.location,
            is_active=d.is_active,
            headcount=hc,
            total_payroll=pr,
            created_at=d.created_at
        ))
    return results

@router.get("/{department_id}", response_model=DepartmentOut)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Retrieves department details by ID."""
    d = db.query(Department).filter(Department.department_id == department_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Department not found")

    hc = db.query(func.count(Employee.employee_id)).filter(
        Employee.department_id == d.department_id,
        Employee.is_deleted == False
    ).scalar() or 0

    pr = db.query(func.sum(Employee.salary)).filter(
        Employee.department_id == d.department_id,
        Employee.is_deleted == False
    ).scalar() or 0.0

    return DepartmentOut(
        department_id=d.department_id,
        department_code=d.department_code,
        name=d.name,
        description=d.description,
        manager_id=d.manager_id,
        manager_name=d.manager.full_name if d.manager else None,
        budget=float(d.budget),
        location=d.location,
        is_active=d.is_active,
        headcount=hc,
        total_payroll=float(pr),
        created_at=d.created_at
    )

@router.post("/", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin"]))
):
    """Creates a new corporate department."""
    if db.query(Department).filter(Department.department_code == payload.department_code).first():
        raise HTTPException(status_code=400, detail="Department code already exists")

    dept = Department(
        department_code=payload.department_code,
        name=payload.name,
        description=payload.description,
        budget=payload.budget,
        location=payload.location,
        manager_id=payload.manager_id,
        is_active=payload.is_active
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)

    return DepartmentOut(
        department_id=dept.department_id,
        department_code=dept.department_code,
        name=dept.name,
        description=dept.description,
        manager_id=dept.manager_id,
        manager_name=dept.manager.full_name if dept.manager else None,
        budget=float(dept.budget),
        location=dept.location,
        is_active=dept.is_active,
        headcount=0,
        total_payroll=0.0,
        created_at=dept.created_at
    )

@router.put("/{department_id}", response_model=DepartmentOut)
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin"]))
):
    """Updates department budget, manager, or details."""
    dept = db.query(Department).filter(Department.department_id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    update_data = payload.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(dept, field, val)

    db.commit()
    db.refresh(dept)
    return get_department(department_id, db, current_user)
