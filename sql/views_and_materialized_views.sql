-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- ADVANCED DATABASE VIEWS & MATERIALIZED VIEWS
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

-- ============================================================================
-- 1. VIEW: COMPREHENSIVE EMPLOYEE DIRECTORY & ORG DETAILS
-- ============================================================================
CREATE OR REPLACE VIEW vw_employee_directory AS
SELECT 
    e.employee_id,
    e.employee_number,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.phone,
    e.job_title,
    d.department_code,
    d.name AS department_name,
    m.first_name || ' ' || m.last_name AS manager_name,
    r.role_name,
    e.employment_type,
    e.status,
    e.hire_date,
    ROUND((CURRENT_DATE - e.hire_date)::NUMERIC / 365.25, 1) AS tenure_years,
    e.salary,
    uc.username,
    uc.last_login_at,
    ep.city,
    ep.country
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN roles r ON e.role_id = r.role_id
LEFT JOIN employees m ON e.manager_id = m.employee_id
LEFT JOIN user_credentials uc ON e.employee_id = uc.employee_id
LEFT JOIN employee_profiles ep ON e.employee_id = ep.employee_id
WHERE e.is_deleted = FALSE;

-- ============================================================================
-- 2. VIEW: DEPARTMENT BUDGET UTILIZATION & PAYROLL BURDEN
-- ============================================================================
CREATE OR REPLACE VIEW vw_department_budget_utilization AS
SELECT 
    d.department_id,
    d.department_code,
    d.name AS department_name,
    d.location,
    mgr.first_name || ' ' || mgr.last_name AS department_head,
    COUNT(e.employee_id) AS total_headcount,
    COALESCE(SUM(e.salary), 0.00) AS total_annual_salary_expense,
    d.budget AS annual_allocated_budget,
    ROUND(d.budget - COALESCE(SUM(e.salary), 0.00), 2) AS remaining_budget_variance,
    CASE 
        WHEN d.budget > 0 THEN ROUND((COALESCE(SUM(e.salary), 0.00) / d.budget) * 100.0, 2)
        ELSE 0.00 
    END AS budget_utilization_pct,
    CASE 
        WHEN COALESCE(SUM(e.salary), 0.00) > d.budget THEN 'OVER_BUDGET'
        WHEN COALESCE(SUM(e.salary), 0.00) >= (d.budget * 0.90) THEN 'WARNING_NEAR_LIMIT'
        ELSE 'HEALTHY'
    END AS budget_health_status
FROM departments d
LEFT JOIN employees mgr ON d.manager_id = mgr.employee_id
LEFT JOIN employees e ON d.department_id = e.department_id AND e.is_deleted = FALSE AND e.status = 'ACTIVE'
GROUP BY d.department_id, d.department_code, d.name, d.location, mgr.first_name, mgr.last_name, d.budget;

-- ============================================================================
-- 3. VIEW: PROJECT FINANCIAL HEALTH & PROFITABILITY
-- ============================================================================
CREATE OR REPLACE VIEW vw_project_financial_health AS
SELECT 
    p.project_id,
    p.project_code,
    p.name AS project_name,
    c.company_name AS client_name,
    pm.first_name || ' ' || pm.last_name AS project_manager,
    p.status AS project_status,
    p.budget AS allocated_budget,
    COALESCE(task_summary.total_logged_hours, 0) AS total_logged_hours,
    COALESCE(task_summary.actual_labor_cost, 0.00) AS actual_labor_cost,
    COALESCE(inv_summary.total_invoiced, 0.00) AS total_invoiced,
    COALESCE(inv_summary.total_collected, 0.00) AS total_collected,
    ROUND(COALESCE(inv_summary.total_invoiced, 0.00) - COALESCE(task_summary.actual_labor_cost, 0.00), 2) AS gross_profit,
    CASE 
        WHEN COALESCE(inv_summary.total_invoiced, 0.00) > 0 THEN
            ROUND(((COALESCE(inv_summary.total_invoiced, 0.00) - COALESCE(task_summary.actual_labor_cost, 0.00)) / inv_summary.total_invoiced) * 100.0, 2)
        ELSE 0.00
    END AS profit_margin_pct
FROM projects p
LEFT JOIN clients c ON p.client_id = c.client_id
LEFT JOIN employees pm ON p.project_manager_id = pm.employee_id
LEFT JOIN (
    SELECT 
        pt.project_id,
        SUM(ttl.hours_logged) AS total_logged_hours,
        SUM(ttl.hours_logged * (e.salary / 2080.0 * 1.5)) AS actual_labor_cost
    FROM project_tasks pt
    JOIN task_time_logs ttl ON pt.task_id = ttl.task_id
    JOIN employees e ON ttl.employee_id = e.employee_id
    GROUP BY pt.project_id
) task_summary ON p.project_id = task_summary.project_id
LEFT JOIN (
    SELECT 
        si.project_id,
        SUM(si.total_amount) AS total_invoiced,
        SUM(si.paid_amount) AS total_collected
    FROM sales_invoices si
    WHERE si.project_id IS NOT NULL
    GROUP BY si.project_id
) inv_summary ON p.project_id = inv_summary.project_id;

-- ============================================================================
-- 4. VIEW: INVENTORY VALUATION & REORDER INTELLIGENCE
-- ============================================================================
CREATE OR REPLACE VIEW vw_inventory_valuation_and_reorder AS
SELECT 
    i.item_id,
    i.sku,
    i.name AS item_name,
    c.name AS category_name,
    i.unit_of_measure,
    i.cost_price,
    i.selling_price,
    i.total_quantity_on_hand,
    i.reorder_level,
    i.reorder_quantity,
    ROUND(i.total_quantity_on_hand * i.cost_price, 2) AS total_inventory_valuation_cost,
    ROUND(i.total_quantity_on_hand * i.selling_price, 2) AS potential_retail_valuation,
    ROUND((i.selling_price - i.cost_price), 2) AS unit_markup,
    CASE 
        WHEN i.cost_price > 0 THEN ROUND(((i.selling_price - i.cost_price) / i.cost_price) * 100.0, 2)
        ELSE 0.00
    END AS markup_percentage,
    CASE 
        WHEN i.total_quantity_on_hand = 0 THEN 'OUT_OF_STOCK'
        WHEN i.total_quantity_on_hand <= (i.reorder_level * 0.5) THEN 'CRITICAL'
        WHEN i.total_quantity_on_hand <= i.reorder_level THEN 'REORDER_REQUIRED'
        ELSE 'OPTIMAL'
    END AS stock_health_status
FROM inventory_items i
JOIN product_categories c ON i.category_id = c.category_id
WHERE i.is_active = TRUE;

-- ============================================================================
-- 5. VIEW: ACCOUNTS RECEIVABLE AGING ANALYSIS
-- ============================================================================
CREATE OR REPLACE VIEW vw_accounts_receivable_aging AS
SELECT 
    si.invoice_id,
    si.invoice_number,
    c.client_code,
    c.company_name AS client_name,
    c.email AS client_email,
    si.issue_date,
    si.due_date,
    CURRENT_DATE - si.due_date AS days_past_due,
    si.total_amount,
    si.paid_amount,
    si.balance_due,
    si.payment_status,
    CASE 
        WHEN CURRENT_DATE <= si.due_date THEN 'CURRENT'
        WHEN CURRENT_DATE - si.due_date BETWEEN 1 AND 30 THEN '1_TO_30_DAYS'
        WHEN CURRENT_DATE - si.due_date BETWEEN 31 AND 60 THEN '31_TO_60_DAYS'
        WHEN CURRENT_DATE - si.due_date BETWEEN 61 AND 90 THEN '61_TO_90_DAYS'
        ELSE 'OVER_90_DAYS_CRITICAL'
    END AS aging_bracket
FROM sales_invoices si
JOIN clients c ON si.client_id = c.client_id
WHERE si.payment_status != 'PAID';

-- ============================================================================
-- 6. MATERIALIZED VIEW: MONTHLY FINANCIAL CASH FLOW SUMMARY
-- Aggregates revenue, vendor disbursements, and payroll payouts
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_monthly_financial_summary;
CREATE MATERIALIZED VIEW mv_monthly_financial_summary AS
WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', payment_date) AS month_date,
        SUM(amount) AS total_revenue,
        COUNT(payment_id) AS receipt_count
    FROM financial_payments
    WHERE payment_type = 'CUSTOMER_RECEIPT'
    GROUP BY DATE_TRUNC('month', payment_date)
),
monthly_vendor_expenses AS (
    SELECT 
        DATE_TRUNC('month', payment_date) AS month_date,
        SUM(amount) AS total_vendor_disbursements,
        COUNT(payment_id) AS disbursement_count
    FROM financial_payments
    WHERE payment_type = 'VENDOR_DISBURSEMENT'
    GROUP BY DATE_TRUNC('month', payment_date)
),
monthly_payroll_expenses AS (
    SELECT 
        DATE_TRUNC('month', pay_date) AS month_date,
        SUM(net_salary) AS total_net_payroll,
        SUM(gross_salary) AS total_gross_payroll,
        COUNT(payroll_id) AS payroll_headcount
    FROM payrolls
    WHERE status IN ('PAID', 'PROCESSED')
    GROUP BY DATE_TRUNC('month', pay_date)
)
SELECT 
    COALESCE(r.month_date, v.month_date, p.month_date) AS period_month,
    TO_CHAR(COALESCE(r.month_date, v.month_date, p.month_date), 'Mon YYYY') AS period_label,
    COALESCE(r.total_revenue, 0.00) AS gross_revenue,
    COALESCE(v.total_vendor_disbursements, 0.00) AS vendor_expenses,
    COALESCE(p.total_net_payroll, 0.00) AS payroll_expenses,
    ROUND(COALESCE(v.total_vendor_disbursements, 0.00) + COALESCE(p.total_net_payroll, 0.00), 2) AS total_operational_expenses,
    ROUND(COALESCE(r.total_revenue, 0.00) - (COALESCE(v.total_vendor_disbursements, 0.00) + COALESCE(p.total_net_payroll, 0.00)), 2) AS net_cash_flow,
    COALESCE(r.receipt_count, 0) AS total_receipts,
    COALESCE(p.payroll_headcount, 0) AS total_payroll_disbursed
FROM monthly_revenue r
FULL OUTER JOIN monthly_vendor_expenses v ON r.month_date = v.month_date
FULL OUTER JOIN monthly_payroll_expenses p ON COALESCE(r.month_date, v.month_date) = p.month_date
ORDER BY period_month DESC;

-- Unique index for concurrent refresh
CREATE UNIQUE INDEX IF NOT EXISTS uq_idx_mv_monthly_financial_period 
ON mv_monthly_financial_summary (period_month);

-- ============================================================================
-- 7. MATERIALIZED VIEW: DEPARTMENT PERFORMANCE KPI SUMMARY
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_department_kpi_summary;
CREATE MATERIALIZED VIEW mv_department_kpi_summary AS
SELECT 
    d.department_id,
    d.department_code,
    d.name AS department_name,
    COUNT(DISTINCT e.employee_id) AS total_employees,
    ROUND(AVG(COALESCE(att.monthly_attendance_pct, 100.0)), 2) AS avg_attendance_rate_pct,
    COUNT(DISTINCT pt.task_id) AS total_assigned_tasks,
    COUNT(DISTINCT CASE WHEN pt.status = 'DONE' THEN pt.task_id END) AS completed_tasks,
    CASE 
        WHEN COUNT(DISTINCT pt.task_id) > 0 THEN 
            ROUND((COUNT(DISTINCT CASE WHEN pt.status = 'DONE' THEN pt.task_id END)::NUMERIC / COUNT(DISTINCT pt.task_id)) * 100.0, 2)
        ELSE 100.00 
    END AS task_completion_rate_pct,
    COUNT(DISTINCT CASE WHEN lr.status = 'PENDING' THEN lr.leave_request_id END) AS pending_leave_requests
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id AND e.is_deleted = FALSE
LEFT JOIN (
    SELECT 
        employee_id,
        ROUND((COUNT(CASE WHEN status IN ('PRESENT', 'HALF_DAY', 'ON_LEAVE') THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)) * 100.0, 2) AS monthly_attendance_pct
    FROM attendance_records
    WHERE work_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY employee_id
) att ON e.employee_id = att.employee_id
LEFT JOIN project_tasks pt ON e.employee_id = pt.assigned_to
LEFT JOIN leave_requests lr ON e.employee_id = lr.employee_id
GROUP BY d.department_id, d.department_code, d.name;

CREATE UNIQUE INDEX IF NOT EXISTS uq_idx_mv_dept_kpi_id 
ON mv_department_kpi_summary (department_id);
