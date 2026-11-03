"""
Analytics, KPI Metrics and Executive Dashboard Schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ExecutiveKPIs(BaseModel):
    total_employees: int
    active_projects: int
    inventory_items_count: int
    low_stock_alerts: int
    total_revenue_collected: float
    total_outstanding_receivables: float
    total_monthly_payroll: float
    attendance_rate_today: float

class MonthlyTrendPoint(BaseModel):
    month_label: str
    gross_revenue: float
    vendor_expenses: float
    payroll_expenses: float
    net_cash_flow: float

class DepartmentMetric(BaseModel):
    department_id: int
    department_code: str
    name: str
    headcount: int
    budget: float
    total_salary: float
    utilization_pct: float

class ProjectHealthMetric(BaseModel):
    project_id: int
    project_code: str
    name: str
    client_name: str
    budget: float
    total_invoiced: float
    total_collected: float
    labor_cost: float
    profit_margin_pct: float

class DashboardOverviewOut(BaseModel):
    kpis: ExecutiveKPIs
    monthly_trends: List[MonthlyTrendPoint]
    department_metrics: List[DepartmentMetric]
    top_projects: List[ProjectHealthMetric]
