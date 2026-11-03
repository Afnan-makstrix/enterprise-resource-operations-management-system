"""
Audit Logs and System Notifications API Router
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.core.pagination import PaginationParams, PaginatedResponse
from backend.app.models.system import AuditLog, SystemNotification
from backend.app.models.employee import Employee

router = APIRouter(prefix="/audit", tags=["Audit Logs & System Notifications"])

@router.get("/logs")
def list_audit_logs(
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    action: Optional[str] = Query(None, description="INSERT, UPDATE, DELETE"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin"]))
):
    """Retrieves immutable audit trail history."""
    query = db.query(AuditLog)
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    if action:
        query = query.filter(AuditLog.action == action)

    total = query.count()
    logs = query.order_by(desc(AuditLog.changed_at)).offset(params.offset).limit(params.page_size).all()

    items = [
        {
            "audit_id": l.audit_id,
            "table_name": l.table_name,
            "record_id": l.record_id,
            "action": l.action,
            "changed_by": l.changed_by,
            "changed_at": l.changed_at,
            "old_data": l.old_data,
            "new_data": l.new_data
        }
        for l in logs
    ]

    return PaginatedResponse.create(items, total, params)

@router.get("/notifications")
def list_user_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Fetches alerts for authenticated user."""
    query = db.query(SystemNotification).filter(SystemNotification.recipient_id == current_user.employee_id)
    if unread_only:
        query = query.filter(SystemNotification.is_read == False)

    notifs = query.order_by(desc(SystemNotification.created_at)).limit(50).all()
    return [
        {
            "notification_id": n.notification_id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at,
            "action_url": n.action_url
        }
        for n in notifs
    ]

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Marks a notification as read."""
    notif = db.query(SystemNotification).filter(
        SystemNotification.notification_id == notification_id,
        SystemNotification.recipient_id == current_user.employee_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Notification marked as read"}
