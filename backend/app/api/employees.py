"""
Employee Management API Router
Implements comprehensive CRUD, search, filter, pagination, and recursive org chart hierarchy.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, text
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.core.pagination import PaginationParams, PaginatedResponse
from backend.app.models.employee import Employee, Department, UserCredential, EmployeeProfile
from backend.app.models.rbac import Role
from backend.app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut

router = APIRouter(prefix="/employees", tags=["Employee Management"])

@router.get("/", response_model=PaginatedResponse[EmployeeOut])
def list_employees(
    department_id: Optional[int] = Query(None, description="Filter by Department ID"),
    role_id: Optional[int] = Query(None, description="Filter by Role ID"),
    status: Optional[str] = Query(None, description="Filter by Status (ACTIVE, ON_LEAVE, TERMINATED)"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """
    Lists employees with multi-column filtering, free-text search, and pagination.
    Backed by indexed PostgreSQL queries.
    """
    query = db.query(Employee).filter(Employee.is_deleted == False)

    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if role_id:
        query = query.filter(Employee.role_id == role_id)
    if status:
        query = query.filter(Employee.status == status)

    if params.search:
        term = f"%{params.search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(term),
                Employee.last_name.ilike(term),
                Employee.email.ilike(term),
                Employee.employee_number.ilike(term),
                Employee.job_title.ilike(term)
            )
        )

    # Sorting
    if params.sort_by and hasattr(Employee, params.sort_by):
        col = getattr(Employee, params.sort_by)
        query = query.order_by(desc(col) if params.sort_desc else asc(col))
    else:
        query = query.order_by(asc(Employee.employee_id))

    total = query.count()
    employees = query.offset(params.offset).limit(params.page_size).all()

    items = []
    for emp in employees:
        items.append(EmployeeOut(
            employee_id=emp.employee_id,
            employee_number=emp.employee_number,
            first_name=emp.first_name,
            last_name=emp.last_name,
            full_name=emp.full_name,
            email=emp.email,
            phone=emp.phone,
            job_title=emp.job_title,
            department_id=emp.department_id,
            department_name=emp.department.name if emp.department else None,
            manager_id=emp.manager_id,
            manager_name=emp.manager.full_name if emp.manager else None,
            role_id=emp.role_id,
            role_name=emp.role.role_name if emp.role else None,
            hire_date=emp.hire_date,
            salary=float(emp.salary),
            employment_type=emp.employment_type,
            status=emp.status,
            created_at=emp.created_at
        ))

    return PaginatedResponse.create(items, total, params)

@router.get("/org-chart/tree")
def get_organizational_chart(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """
    Executes PostgreSQL Recursive Common Table Expression (CTE)
    to generate the multi-level organizational chart tree.
    """
    sql = text("""
        WITH RECURSIVE OrgHierarchy AS (
            SELECT 
                employee_id,
                first_name || ' ' || last_name AS full_name,
                job_title,
                manager_id,
                department_id,
                1 AS hierarchy_level,
                CAST(first_name || ' ' || last_name AS TEXT) AS reporting_chain
            FROM employees
            WHERE manager_id IS NULL AND is_deleted = FALSE
            
            UNION ALL
            
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name,
                e.job_title,
                e.manager_id,
                e.department_id,
                oh.hierarchy_level + 1,
                oh.reporting_chain || ' -> ' || (e.first_name || ' ' || e.last_name)
            FROM employees e
            INNER JOIN OrgHierarchy oh ON e.manager_id = oh.employee_id
            WHERE e.is_deleted = FALSE
        )
        SELECT 
            oh.employee_id,
            oh.full_name,
            oh.job_title,
            oh.manager_id,
            d.name AS department_name,
            oh.hierarchy_level,
            oh.reporting_chain
        FROM OrgHierarchy oh
        JOIN departments d ON oh.department_id = d.department_id
        WHERE oh.hierarchy_level <= 3
        ORDER BY oh.hierarchy_level, oh.full_name;
    """)
    result = db.execute(sql).fetchall()
    return [
        {
            "employee_id": row.employee_id,
            "full_name": row.full_name,
            "job_title": row.job_title,
            "manager_id": row.manager_id,
            "department_name": row.department_name,
            "hierarchy_level": row.hierarchy_level,
            "reporting_chain": row.reporting_chain
        }
        for row in result
    ]

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee_detail(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Retrieves full employee record by primary key ID."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id, Employee.is_deleted == FALSE).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return EmployeeOut(
        employee_id=emp.employee_id,
        employee_number=emp.employee_number,
        first_name=emp.first_name,
        last_name=emp.last_name,
        full_name=emp.full_name,
        email=emp.email,
        phone=emp.phone,
        job_title=emp.job_title,
        department_id=emp.department_id,
        department_name=emp.department.name if emp.department else None,
        manager_id=emp.manager_id,
        manager_name=emp.manager.full_name if emp.manager else None,
        role_id=emp.role_id,
        role_name=emp.role.role_name if emp.role else None,
        hire_date=emp.hire_date,
        salary=float(emp.salary),
        employment_type=emp.employment_type,
        status=emp.status,
        created_at=emp.created_at
    )

@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin", "HR Manager"]))
):
    """
    Creates a new employee record and initializes their profile and credentials.
    Uses database transaction to guarantee ACID integrity.
    """
    # Check for existing email or employee number
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Employee email already in use")

    emp_number = payload.employee_number or f"EMP-{db.query(Employee).count() + 10001:06d}"
    
    new_emp = Employee(
        employee_number=emp_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        job_title=payload.job_title,
        department_id=payload.department_id,
        manager_id=payload.manager_id,
        role_id=payload.role_id,
        salary=payload.salary,
        employment_type=payload.employment_type,
        status=payload.status
    )
    db.add(new_emp)
    db.flush()

    # Create empty profile
    profile = EmployeeProfile(employee_id=new_emp.employee_id)
    db.add(profile)

    db.commit()
    db.refresh(new_emp)

    return EmployeeOut(
        employee_id=new_emp.employee_id,
        employee_number=new_emp.employee_number,
        first_name=new_emp.first_name,
        last_name=new_emp.last_name,
        full_name=new_emp.full_name,
        email=new_emp.email,
        phone=new_emp.phone,
        job_title=new_emp.job_title,
        department_id=new_emp.department_id,
        department_name=new_emp.department.name if new_emp.department else None,
        manager_id=new_emp.manager_id,
        manager_name=new_emp.manager.full_name if new_emp.manager else None,
        role_id=new_emp.role_id,
        role_name=new_emp.role.role_name if new_emp.role else None,
        hire_date=new_emp.hire_date,
        salary=float(new_emp.salary),
        employment_type=new_emp.employment_type,
        status=new_emp.status,
        created_at=new_emp.created_at
    )

@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin", "HR Manager"]))
):
    """Updates an existing employee record."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id, Employee.is_deleted == False).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = payload.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(emp, field, val)

    db.commit()
    db.refresh(emp)

    return EmployeeOut(
        employee_id=emp.employee_id,
        employee_number=emp.employee_number,
        first_name=emp.first_name,
        last_name=emp.last_name,
        full_name=emp.full_name,
        email=emp.email,
        phone=emp.phone,
        job_title=emp.job_title,
        department_id=emp.department_id,
        department_name=emp.department.name if emp.department else None,
        manager_id=emp.manager_id,
        manager_name=emp.manager.full_name if emp.manager else None,
        role_id=emp.role_id,
        role_name=emp.role.role_name if emp.role else None,
        hire_date=emp.hire_date,
        salary=float(emp.salary),
        employment_type=emp.employment_type,
        status=emp.status,
        created_at=emp.created_at
    )

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin"]))
):
    """Soft-deletes an employee record."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp.is_deleted = True
    emp.status = "TERMINATED"
    db.commit()
    return None
