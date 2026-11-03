"""
Project, Task & Workflow Management API Router
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.core.pagination import PaginationParams, PaginatedResponse
from backend.app.models.project import Project, ProjectMember, ProjectTask, TaskTimeLog
from backend.app.models.employee import Employee
from backend.app.schemas.project import ProjectCreate, ProjectOut, TaskBase, TaskCreate, TaskUpdate, TaskOut

router = APIRouter(prefix="/projects", tags=["Project & Workflow Management"])

@router.get("/", response_model=PaginatedResponse[ProjectOut])
def list_projects(
    status: Optional[str] = Query(None, description="Filter by status (PLANNING, IN_PROGRESS, COMPLETED, ON_HOLD)"),
    priority: Optional[str] = Query(None, description="Filter by priority (LOW, MEDIUM, HIGH, CRITICAL)"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists projects with dynamic search, filter, and task progress tracking."""
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)
    if priority:
        query = query.filter(Project.priority == priority)

    if params.search:
        term = f"%{params.search}%"
        query = query.filter(
            or_(
                Project.name.ilike(term),
                Project.project_code.ilike(term),
                Project.description.ilike(term)
            )
        )

    total = query.count()
    projects = query.order_by(desc(Project.created_at)).offset(params.offset).limit(params.page_size).all()

    items = []
    for p in projects:
        t_total = db.query(func.count(ProjectTask.task_id)).filter(ProjectTask.project_id == p.project_id).scalar() or 0
        t_done = db.query(func.count(ProjectTask.task_id)).filter(
            ProjectTask.project_id == p.project_id,
            ProjectTask.status == "DONE"
        ).scalar() or 0

        items.append(ProjectOut(
            project_id=p.project_id,
            project_code=p.project_code,
            name=p.name,
            description=p.description,
            client_id=p.client_id,
            client_name=p.client.company_name if p.client else None,
            project_manager_id=p.project_manager_id,
            project_manager_name=p.manager.full_name if p.manager else None,
            start_date=p.start_date,
            target_end_date=p.target_end_date,
            budget=float(p.budget),
            cost_to_date=float(p.cost_to_date),
            status=p.status,
            priority=p.priority,
            total_tasks=t_total,
            completed_tasks=t_done,
            created_at=p.created_at
        ))

    return PaginatedResponse.create(items, total, params)

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Retrieves full project details."""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    t_total = db.query(func.count(ProjectTask.task_id)).filter(ProjectTask.project_id == p.project_id).scalar() or 0
    t_done = db.query(func.count(ProjectTask.task_id)).filter(
        ProjectTask.project_id == p.project_id,
        ProjectTask.status == "DONE"
    ).scalar() or 0

    return ProjectOut(
        project_id=p.project_id,
        project_code=p.project_code,
        name=p.name,
        description=p.description,
        client_id=p.client_id,
        client_name=p.client.company_name if p.client else None,
        project_manager_id=p.project_manager_id,
        project_manager_name=p.manager.full_name if p.manager else None,
        start_date=p.start_date,
        target_end_date=p.target_end_date,
        budget=float(p.budget),
        cost_to_date=float(p.cost_to_date),
        status=p.status,
        priority=p.priority,
        total_tasks=t_total,
        completed_tasks=t_done,
        created_at=p.created_at
    )

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin", "Project Manager"]))
):
    """Creates a new enterprise project."""
    if db.query(Project).filter(Project.project_code == payload.project_code).first():
        raise HTTPException(status_code=400, detail="Project code already exists")

    proj = Project(
        project_code=payload.project_code,
        name=payload.name,
        description=payload.description,
        client_id=payload.client_id,
        project_manager_id=payload.project_manager_id,
        start_date=payload.start_date,
        target_end_date=payload.target_end_date,
        budget=payload.budget,
        cost_to_date=0.00,
        status=payload.status,
        priority=payload.priority
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return get_project(proj.project_id, db, current_user)

@router.get("/{project_id}/tasks", response_model=List[TaskOut])
def list_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists all work breakdown tasks for a given project."""
    tasks = db.query(ProjectTask).filter(ProjectTask.project_id == project_id).order_by(ProjectTask.created_at).all()
    return [
        TaskOut(
            task_id=t.task_id,
            task_code=t.task_code,
            project_id=t.project_id,
            project_name=t.project.name if t.project else None,
            title=t.title,
            description=t.description,
            assigned_to=t.assigned_to,
            assignee_name=t.assignee.full_name if t.assignee else None,
            reporter_id=t.reporter_id,
            reporter_name=t.reporter.full_name if t.reporter else None,
            priority=t.priority,
            status=t.status,
            estimated_hours=float(t.estimated_hours or 0.0),
            actual_hours=float(t.actual_hours or 0.0),
            due_date=t.due_date,
            completed_at=t.completed_at,
            created_at=t.created_at
        )
        for t in tasks
    ]

@router.post("/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_project_task(
    project_id: int,
    payload: TaskBase,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Adds a task to a project."""
    if db.query(ProjectTask).filter(ProjectTask.task_code == payload.task_code).first():
        raise HTTPException(status_code=400, detail="Task code already exists")

    task = ProjectTask(
        task_code=payload.task_code,
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        assigned_to=payload.assigned_to,
        reporter_id=current_user.employee_id,
        priority=payload.priority,
        status=payload.status,
        estimated_hours=payload.estimated_hours,
        actual_hours=0.00,
        due_date=payload.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskOut(
        task_id=task.task_id,
        task_code=task.task_code,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        assignee_name=task.assignee.full_name if task.assignee else None,
        reporter_id=task.reporter_id,
        reporter_name=current_user.full_name,
        priority=task.priority,
        status=task.status,
        estimated_hours=float(task.estimated_hours or 0.0),
        actual_hours=0.0,
        due_date=task.due_date,
        completed_at=None,
        created_at=task.created_at
    )

@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Updates task status, hours, or assignment."""
    task = db.query(ProjectTask).filter(ProjectTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(task, field, val)

    if payload.status == "DONE" and not task.completed_at:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return TaskOut(
        task_id=task.task_id,
        task_code=task.task_code,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        assignee_name=task.assignee.full_name if task.assignee else None,
        reporter_id=task.reporter_id,
        reporter_name=task.reporter.full_name if task.reporter else None,
        priority=task.priority,
        status=task.status,
        estimated_hours=float(task.estimated_hours or 0.0),
        actual_hours=float(task.actual_hours or 0.0),
        due_date=task.due_date,
        completed_at=task.completed_at,
        created_at=task.created_at
    )
