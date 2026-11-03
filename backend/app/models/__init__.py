"""
Model Package Registry
Exports all SQLAlchemy models for EROMS application and Alembic migrations.
"""
from backend.app.database import Base
from backend.app.models.rbac import Role, Permission, RolePermission
from backend.app.models.employee import Department, Employee, UserCredential, EmployeeProfile
from backend.app.models.attendance_leave import LeaveType, LeaveBalance, LeaveRequest, AttendanceRecord
from backend.app.models.finance import SalaryStructure, Payroll, SalesInvoice, InvoiceItem, FinancialPayment
from backend.app.models.inventory_purchasing import (
    Client, Supplier, ProductCategory, InventoryItem, Warehouse,
    WarehouseStock, InventoryTransaction, PurchaseOrder, PurchaseOrderItem
)
from backend.app.models.project import Project, ProjectMember, ProjectTask, TaskTimeLog
from backend.app.models.system import AuditLog, SystemNotification, CompanySetting

__all__ = [
    "Base",
    "Role", "Permission", "RolePermission",
    "Department", "Employee", "UserCredential", "EmployeeProfile",
    "LeaveType", "LeaveBalance", "LeaveRequest", "AttendanceRecord",
    "SalaryStructure", "Payroll", "SalesInvoice", "InvoiceItem", "FinancialPayment",
    "Client", "Supplier", "ProductCategory", "InventoryItem", "Warehouse",
    "WarehouseStock", "InventoryTransaction", "PurchaseOrder", "PurchaseOrderItem",
    "Project", "ProjectMember", "ProjectTask", "TaskTimeLog",
    "AuditLog", "SystemNotification", "CompanySetting"
]
