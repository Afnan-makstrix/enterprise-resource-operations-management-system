-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- 30 ADVANCED BUSINESS OPERATIONS & ANALYTICAL SQL QUERIES
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

-- ============================================================================
-- MODULE 1: COMPLEX JOINS (Q01 - Q05)
-- ============================================================================

-- Q01: Employee Compensation Breakdown with Department and Manager Details
-- Concept: Multi-table INNER JOIN, self-referencing LEFT JOIN (Manager), LEFT JOIN on Profile
SELECT 
    e.employee_number,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    d.name AS department_name,
    d.location AS department_location,
    COALESCE(m.first_name || ' ' || m.last_name, 'None (Executive)') AS reports_to,
    r.role_name,
    e.salary,
    ss.house_rent_allowance,
    ss.transport_allowance,
    ss.medical_allowance,
    ROUND(e.salary + COALESCE(ss.house_rent_allowance + ss.transport_allowance + ss.medical_allowance, 0), 2) AS total_annual_compensation,
    ep.city,
    ep.country
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
INNER JOIN roles r ON e.role_id = r.role_id
LEFT JOIN employees m ON e.manager_id = m.employee_id
LEFT JOIN salary_structures ss ON e.employee_id = ss.employee_id
LEFT JOIN employee_profiles ep ON e.employee_id = ep.employee_id
WHERE e.is_deleted = FALSE
ORDER BY d.name, e.salary DESC;

-- Q02: Cross-Department Project Task Velocity & Member Utilization
-- Concept: INNER JOIN across 4 tables with conditional aggregation
SELECT 
    p.project_code,
    p.name AS project_name,
    d.name AS lead_department,
    COUNT(DISTINCT pm.employee_id) AS total_assigned_team_size,
    COUNT(pt.task_id) AS total_project_tasks,
    COUNT(CASE WHEN pt.status = 'DONE' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN pt.status = 'IN_PROGRESS' THEN 1 END) AS active_tasks,
    COALESCE(SUM(pt.estimated_hours), 0.00) AS total_estimated_hours,
    COALESCE(SUM(pt.actual_hours), 0.00) AS total_actual_hours,
    ROUND(COALESCE(SUM(pt.actual_hours), 0.00) - COALESCE(SUM(pt.estimated_hours), 0.00), 2) AS hour_variance
FROM projects p
INNER JOIN employees mgr ON p.project_manager_id = mgr.employee_id
INNER JOIN departments d ON mgr.department_id = d.department_id
LEFT JOIN project_members pm ON p.project_id = pm.project_id AND pm.is_active = TRUE
LEFT JOIN project_tasks pt ON p.project_id = pt.project_id
GROUP BY p.project_code, p.name, d.name
ORDER BY total_project_tasks DESC;

-- Q03: Supplier Reliability & Purchase Order Fulfillment
-- Concept: RIGHT JOIN to ensure suppliers without any purchase orders are identified
SELECT 
    s.supplier_code,
    s.company_name AS supplier_name,
    s.rating,
    s.status AS supplier_status,
    COUNT(po.po_id) AS total_orders_placed,
    COALESCE(SUM(po.total_amount), 0.00) AS total_purchased_volume,
    COUNT(CASE WHEN po.status = 'RECEIVED' THEN 1 END) AS fulfilled_orders,
    COUNT(CASE WHEN po.status = 'CANCELLED' THEN 1 END) AS cancelled_orders,
    CASE 
        WHEN COUNT(po.po_id) > 0 THEN 
            ROUND((COUNT(CASE WHEN po.status = 'RECEIVED' THEN 1 END)::NUMERIC / COUNT(po.po_id)) * 100.0, 2)
        ELSE 0.00 
    END AS fulfillment_rate_pct
FROM purchase_orders po
RIGHT JOIN suppliers s ON po.supplier_id = s.supplier_id
GROUP BY s.supplier_id, s.supplier_code, s.company_name, s.rating, s.status
ORDER BY total_purchased_volume DESC;

-- Q04: FULL OUTER JOIN for Budget Variance vs Total Payroll Expense
-- Concept: FULL OUTER JOIN reconciling allocated department budgets with executed payroll
SELECT 
    COALESCE(d.department_code, 'UNASSIGNED') AS department_code,
    COALESCE(d.name, 'Unassigned / Global') AS department_name,
    COALESCE(d.budget, 0.00) AS annual_budget,
    COALESCE(p_summary.total_payroll_paid, 0.00) AS ytd_payroll_paid,
    ROUND(COALESCE(d.budget, 0.00) - COALESCE(p_summary.total_payroll_paid, 0.00), 2) AS remaining_budget,
    CASE 
        WHEN d.department_id IS NULL THEN 'PAYROLL_WITHOUT_DEPARTMENT'
        WHEN p_summary.department_id IS NULL THEN 'BUDGET_WITHOUT_PAYROLL'
        ELSE 'MATCHED'
    END AS reconciliation_status
FROM departments d
FULL OUTER JOIN (
    SELECT 
        e.department_id,
        SUM(p.net_salary) AS total_payroll_paid
    FROM payrolls p
    JOIN employees e ON p.employee_id = e.employee_id
    WHERE p.status = 'PAID'
    GROUP BY e.department_id
) p_summary ON d.department_id = p_summary.department_id
ORDER BY annual_budget DESC;

-- Q05: LATERAL JOIN - Top 2 Highest Paid Employees for Each Department
-- Concept: PostgreSQL LATERAL subquery executing a parameterized correlated ranking
SELECT 
    d.department_code,
    d.name AS department_name,
    top_emp.employee_number,
    top_emp.employee_name,
    top_emp.job_title,
    top_emp.salary
FROM departments d
CROSS JOIN LATERAL (
    SELECT 
        e.employee_number,
        e.first_name || ' ' || e.last_name AS employee_name,
        e.job_title,
        e.salary
    FROM employees e
    WHERE e.department_id = d.department_id AND e.is_deleted = FALSE
    ORDER BY e.salary DESC
    LIMIT 2
) top_emp
WHERE d.is_active = TRUE
ORDER BY d.name, top_emp.salary DESC;

-- ============================================================================
-- MODULE 2: SUBQUERIES & CORRELATED SUBQUERIES (Q06 - Q10)
-- ============================================================================

-- Q06: Correlated Subquery: Employees Earning More than Their Department Average
-- Concept: Correlated scalar subquery comparing individual salary against departmental mean
SELECT 
    e.employee_number,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    d.name AS department_name,
    e.salary,
    ROUND((
        SELECT AVG(e2.salary) 
        FROM employees e2 
        WHERE e2.department_id = e.department_id AND e2.is_deleted = FALSE
    ), 2) AS dept_average_salary,
    ROUND(e.salary - (
        SELECT AVG(e2.salary) 
        FROM employees e2 
        WHERE e2.department_id = e.department_id AND e2.is_deleted = FALSE
    ), 2) AS premium_above_dept_avg
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.is_deleted = FALSE
  AND e.salary > (
      SELECT AVG(e2.salary) 
      FROM employees e2 
      WHERE e2.department_id = e.department_id AND e2.is_deleted = FALSE
  )
ORDER BY premium_above_dept_avg DESC;

-- Q07: Scalar Subquery: Clients Whose Unpaid Balance Exceeds 60% of Credit Limit
-- Concept: Subquery in WHERE clause evaluating customer exposure risk
SELECT 
    c.client_code,
    c.company_name,
    c.credit_limit,
    COALESCE((
        SELECT SUM(si.balance_due)
        FROM sales_invoices si
        WHERE si.client_id = c.client_id AND si.payment_status != 'PAID'
    ), 0.00) AS total_outstanding_debt,
    ROUND((COALESCE((
        SELECT SUM(si.balance_due)
        FROM sales_invoices si
        WHERE si.client_id = c.client_id AND si.payment_status != 'PAID'
    ), 0.00) / NULLIF(c.credit_limit, 0)) * 100.0, 2) AS credit_utilization_pct
FROM clients c
WHERE COALESCE((
    SELECT SUM(si.balance_due)
    FROM sales_invoices si
    WHERE si.client_id = c.client_id AND si.payment_status != 'PAID'
), 0.00) >= (c.credit_limit * 0.60)
ORDER BY credit_utilization_pct DESC;

-- Q08: EXISTS Subquery: Projects That Have Completed All Assigned Tasks
-- Concept: EXISTS and NOT EXISTS subquery for lifecycle workflow validation
SELECT 
    p.project_code,
    p.name AS project_name,
    p.status AS current_status,
    c.company_name AS client_name,
    p.target_end_date
FROM projects p
JOIN clients c ON p.client_id = c.client_id
WHERE p.status = 'IN_PROGRESS'
  AND EXISTS (
      SELECT 1 FROM project_tasks pt WHERE pt.project_id = p.project_id
  )
  AND NOT EXISTS (
      SELECT 1 FROM project_tasks pt 
      WHERE pt.project_id = p.project_id AND pt.status != 'DONE'
  );

-- Q09: NOT EXISTS Subquery: Dead Stock Inventory (No Movement in Last 90 Days)
-- Concept: NOT EXISTS correlated subquery across ledger tables
SELECT 
    i.sku,
    i.name AS item_name,
    cat.name AS category_name,
    i.total_quantity_on_hand,
    i.cost_price,
    ROUND(i.total_quantity_on_hand * i.cost_price, 2) AS trapped_capital
FROM inventory_items i
JOIN product_categories cat ON i.category_id = cat.category_id
WHERE i.total_quantity_on_hand > 0
  AND NOT EXISTS (
      SELECT 1 
      FROM inventory_transactions it
      WHERE it.item_id = i.item_id 
        AND it.transaction_date >= CURRENT_TIMESTAMP - INTERVAL '90 days'
  )
ORDER BY trapped_capital DESC;

-- Q10: Subquery with ALL / ANY: Top Suppliers Outperforming Category Average
-- Concept: Greater than ALL / ANY comparison operator
SELECT 
    s.company_name,
    s.rating,
    s.city,
    po.po_number,
    po.total_amount
FROM purchase_orders po
JOIN suppliers s ON po.supplier_id = s.supplier_id
WHERE po.total_amount > ALL (
    SELECT AVG(sub_po.total_amount)
    FROM purchase_orders sub_po
    WHERE sub_po.status = 'RECEIVED'
)
ORDER BY po.total_amount DESC;

-- ============================================================================
-- MODULE 3: COMMON TABLE EXPRESSIONS (CTEs) & RECURSIVE CTEs (Q11 - Q15)
-- ============================================================================

-- Q11: Recursive CTE: Complete Corporate Organization Chart & Hierarchy
-- Concept: RECURSIVE CTE establishing employee management tree with hierarchy level and path
WITH RECURSIVE OrgHierarchy AS (
    -- Anchor Member: Top executives (no manager)
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        job_title,
        manager_id,
        1 AS hierarchy_level,
        CAST(first_name || ' ' || last_name AS TEXT) AS reporting_chain
    FROM employees
    WHERE manager_id IS NULL AND is_deleted = FALSE

    UNION ALL

    -- Recursive Member: Subordinates
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.job_title,
        e.manager_id,
        oh.hierarchy_level + 1,
        oh.reporting_chain || ' -> ' || (e.first_name || ' ' || e.last_name)
    FROM employees e
    INNER JOIN OrgHierarchy oh ON e.manager_id = oh.employee_id
    WHERE e.is_deleted = FALSE
)
SELECT 
    hierarchy_level,
    REPEAT('  ', hierarchy_level - 1) || employee_name AS indented_org_chart,
    job_title,
    reporting_chain
FROM OrgHierarchy
ORDER BY hierarchy_level, employee_name;

-- Q12: Recursive CTE: Multi-Level Product Category Rollup
-- Concept: RECURSIVE CTE traversing self-referencing category taxonomy
WITH RECURSIVE CategoryTree AS (
    SELECT 
        category_id,
        category_code,
        name,
        parent_category_id,
        1 AS depth_level,
        CAST(name AS TEXT) AS category_path
    FROM product_categories
    WHERE parent_category_id IS NULL

    UNION ALL

    SELECT 
        c.category_id,
        c.category_code,
        c.name,
        c.parent_category_id,
        ct.depth_level + 1,
        ct.category_path || ' > ' || c.name
    FROM product_categories c
    INNER JOIN CategoryTree ct ON c.parent_category_id = ct.category_id
)
SELECT 
    depth_level,
    category_path,
    COUNT(i.item_id) AS total_products_in_category,
    COALESCE(SUM(i.total_quantity_on_hand), 0) AS total_units_in_stock
FROM CategoryTree ct
LEFT JOIN inventory_items i ON ct.category_id = i.category_id
GROUP BY depth_level, category_path, ct.category_id
ORDER BY category_path;

-- Q13: Recursive CTE: Project Task Dependency Tree & WBS Breakdown
-- Concept: RECURSIVE CTE finding subtask relationships and aggregate rollups
WITH RECURSIVE TaskWBS AS (
    SELECT 
        task_id,
        task_code,
        title,
        project_id,
        parent_task_id,
        status,
        priority,
        estimated_hours,
        actual_hours,
        1 AS wbs_level,
        CAST(task_code AS TEXT) AS task_hierarchy
    FROM project_tasks
    WHERE parent_task_id IS NULL

    UNION ALL

    SELECT 
        pt.task_id,
        pt.task_code,
        pt.title,
        pt.project_id,
        pt.parent_task_id,
        pt.status,
        pt.priority,
        pt.estimated_hours,
        pt.actual_hours,
        wbs.wbs_level + 1,
        wbs.task_hierarchy || '.' || pt.task_code
    FROM project_tasks pt
    INNER JOIN TaskWBS wbs ON pt.parent_task_id = wbs.task_id
)
SELECT 
    p.name AS project_name,
    wbs.wbs_level,
    wbs.task_hierarchy,
    wbs.title AS task_title,
    wbs.status,
    wbs.priority,
    wbs.estimated_hours,
    wbs.actual_hours
FROM TaskWBS wbs
JOIN projects p ON wbs.project_id = p.project_id
ORDER BY p.name, wbs.task_hierarchy;

-- Q14: Multi-Step CTE: Comprehensive Client Account Profitability
-- Concept: Multi-CTE pipeline joining invoices, project costs, and payment receipts
WITH ClientRevenue AS (
    SELECT 
        client_id,
        SUM(total_amount) AS total_invoiced,
        SUM(paid_amount) AS total_collected,
        SUM(balance_due) AS total_unpaid
    FROM sales_invoices
    GROUP BY client_id
),
ClientProjectCosts AS (
    SELECT 
        p.client_id,
        SUM(ttl.hours_logged * (e.salary / 2080.0 * 1.5)) AS direct_labor_cost
    FROM projects p
    JOIN project_tasks pt ON p.project_id = pt.project_id
    JOIN task_time_logs ttl ON pt.task_id = ttl.task_id
    JOIN employees e ON ttl.employee_id = e.employee_id
    GROUP BY p.client_id
)
SELECT 
    c.client_code,
    c.company_name,
    COALESCE(cr.total_invoiced, 0.00) AS total_invoiced,
    COALESCE(cr.total_collected, 0.00) AS total_collected,
    COALESCE(cr.total_unpaid, 0.00) AS total_unpaid,
    ROUND(COALESCE(cpc.direct_labor_cost, 0.00), 2) AS estimated_labor_cost,
    ROUND(COALESCE(cr.total_collected, 0.00) - COALESCE(cpc.direct_labor_cost, 0.00), 2) AS net_realized_margin,
    CASE 
        WHEN COALESCE(cr.total_collected, 0.00) > 0 THEN 
            ROUND(((COALESCE(cr.total_collected, 0.00) - COALESCE(cpc.direct_labor_cost, 0.00)) / cr.total_collected) * 100.0, 2)
        ELSE 0.00 
    END AS realized_margin_pct
FROM clients c
LEFT JOIN ClientRevenue cr ON c.client_id = cr.client_id
LEFT JOIN ClientProjectCosts cpc ON c.client_id = cpc.client_id
ORDER BY net_realized_margin DESC;

-- Q15: CTE with Window Aggregation: Employee Attendance Deficit Tracking
-- Concept: Common Table Expression analyzing work-hour compliance
WITH MonthlyAttendanceAudit AS (
    SELECT 
        employee_id,
        EXTRACT(MONTH FROM work_date) AS audit_month,
        COUNT(*) AS recorded_days,
        SUM(hours_worked) AS total_hours_worked,
        SUM(overtime_hours) AS total_overtime_hours,
        COUNT(CASE WHEN status = 'LATE' THEN 1 END) AS late_occurrences,
        COUNT(CASE WHEN status = 'ABSENT' THEN 1 END) AS unexcused_absences
    FROM attendance_records
    WHERE work_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY employee_id, EXTRACT(MONTH FROM work_date)
)
SELECT 
    e.employee_number,
    e.first_name || ' ' || e.last_name AS employee_name,
    d.name AS department_name,
    maa.recorded_days,
    maa.total_hours_worked,
    maa.total_overtime_hours,
    maa.late_occurrences,
    maa.unexcused_absences,
    ROUND((maa.recorded_days * 8.0) - maa.total_hours_worked, 2) AS hours_deficit
FROM MonthlyAttendanceAudit maa
JOIN employees e ON maa.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
WHERE (maa.recorded_days * 8.0) > maa.total_hours_worked
ORDER BY hours_deficit DESC;

-- ============================================================================
-- MODULE 4: WINDOW FUNCTIONS (Q16 - Q20)
-- ============================================================================

-- Q16: Window Functions: ROW_NUMBER, RANK, DENSE_RANK on Employee Salaries
-- Concept: Departmental and Organization-wide comparative ranking
SELECT 
    d.name AS department_name,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    e.salary,
    ROW_NUMBER() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_row_num,
    RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_salary_rank,
    DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_dense_rank,
    DENSE_RANK() OVER (ORDER BY e.salary DESC) AS company_wide_rank
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.is_deleted = FALSE;

-- Q17: Window Function NTILE(4): Quartile Distribution of Client Billing Volume
-- Concept: NTILE(4) statistical segmentation for enterprise customer accounts
SELECT 
    c.client_code,
    c.company_name,
    COALESCE(SUM(si.total_amount), 0.00) AS total_billed_amount,
    NTILE(4) OVER (ORDER BY COALESCE(SUM(si.total_amount), 0.00) DESC) AS revenue_quartile,
    CASE NTILE(4) OVER (ORDER BY COALESCE(SUM(si.total_amount), 0.00) DESC)
        WHEN 1 THEN 'TIER_1_PLATINUM'
        WHEN 2 THEN 'TIER_2_GOLD'
        WHEN 3 THEN 'TIER_3_SILVER'
        WHEN 4 THEN 'TIER_4_BRONZE'
    END AS customer_tier
FROM clients c
LEFT JOIN sales_invoices si ON c.client_id = si.client_id
GROUP BY c.client_id, c.client_code, c.company_name
ORDER BY revenue_quartile, total_billed_amount DESC;

-- Q18: Window Functions LAG & LEAD: Month-over-Month (MoM) Invoice Revenue Trend
-- Concept: LAG and LEAD to calculate previous and next month revenue deltas
WITH MonthlyInvoiceTotals AS (
    SELECT 
        DATE_TRUNC('month', issue_date) AS invoice_month,
        SUM(total_amount) AS monthly_invoiced_total
    FROM sales_invoices
    GROUP BY DATE_TRUNC('month', issue_date)
)
SELECT 
    TO_CHAR(invoice_month, 'YYYY-MM') AS month_label,
    monthly_invoiced_total,
    LAG(monthly_invoiced_total, 1) OVER (ORDER BY invoice_month) AS prior_month_revenue,
    ROUND(monthly_invoiced_total - LAG(monthly_invoiced_total, 1) OVER (ORDER BY invoice_month), 2) AS mom_dollar_change,
    ROUND((
        (monthly_invoiced_total - LAG(monthly_invoiced_total, 1) OVER (ORDER BY invoice_month)) / 
        NULLIF(LAG(monthly_invoiced_total, 1) OVER (ORDER BY invoice_month), 0)
    ) * 100.0, 2) AS mom_growth_pct,
    LEAD(monthly_invoiced_total, 1) OVER (ORDER BY invoice_month) AS following_month_revenue
FROM MonthlyInvoiceTotals
ORDER BY invoice_month;

-- Q19: Running Cumulative Total (SUM OVER) & Contribution Percentage
-- Concept: Cumulative summation over an ordered partition window
SELECT 
    si.invoice_number,
    c.company_name AS client_name,
    si.issue_date,
    si.total_amount,
    SUM(si.total_amount) OVER (
        PARTITION BY EXTRACT(YEAR FROM si.issue_date) 
        ORDER BY si.issue_date, si.invoice_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS ytd_cumulative_revenue,
    ROUND((
        si.total_amount / 
        SUM(si.total_amount) OVER (PARTITION BY EXTRACT(YEAR FROM si.issue_date))
    ) * 100.0, 2) AS pct_of_annual_total
FROM sales_invoices si
JOIN clients c ON si.client_id = c.client_id
ORDER BY si.issue_date;

-- Q20: Moving Window Average (AVG OVER): 7-Day Moving Average of Daily Work Hours
-- Concept: ROWS BETWEEN 6 PRECEDING AND CURRENT ROW for moving trend smoothing
SELECT 
    work_date,
    SUM(hours_worked) AS daily_total_company_hours,
    ROUND(AVG(SUM(hours_worked)) OVER (
        ORDER BY work_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS seven_day_moving_avg_hours
FROM attendance_records
GROUP BY work_date
ORDER BY work_date DESC;

-- ============================================================================
-- MODULE 5: ADVANCED AGGREGATIONS & GROUPING SETS (Q21 - Q25)
-- ============================================================================

-- Q21: GROUP BY with HAVING: High-Impact Department Salary & Headcount Filter
-- Concept: Aggregate filtering with multiple conditions in HAVING clause
SELECT 
    d.department_code,
    d.name AS department_name,
    COUNT(e.employee_id) AS total_headcount,
    ROUND(AVG(e.salary), 2) AS avg_employee_salary,
    MIN(e.salary) AS min_salary,
    MAX(e.salary) AS max_salary,
    SUM(e.salary) AS total_dept_payroll
FROM departments d
JOIN employees e ON d.department_id = e.department_id
WHERE e.is_deleted = FALSE
GROUP BY d.department_code, d.name
HAVING COUNT(e.employee_id) >= 2 
   AND AVG(e.salary) > 50000.00
ORDER BY total_dept_payroll DESC;

-- Q22: Hierarchical ROLLUP: Sales Invoiced by Year, Quarter, and Overall Total
-- Concept: ROLLUP generating multi-level sub-totals and grand totals
SELECT 
    EXTRACT(YEAR FROM issue_date)::TEXT AS invoice_year,
    'Q' || EXTRACT(QUARTER FROM issue_date)::TEXT AS invoice_quarter,
    COUNT(invoice_id) AS total_invoices,
    SUM(total_amount) AS gross_invoiced_amount,
    SUM(paid_amount) AS total_collected_amount,
    SUM(balance_due) AS total_outstanding_amount
FROM sales_invoices
GROUP BY ROLLUP (EXTRACT(YEAR FROM issue_date)::TEXT, 'Q' || EXTRACT(QUARTER FROM issue_date)::TEXT)
ORDER BY invoice_year NULLS LAST, invoice_quarter NULLS LAST;

-- Q23: Multi-Dimensional CUBE: Inventory Stock Distribution by Warehouse & Category
-- Concept: CUBE calculating cross-tabulation totals across all dimension combinations
SELECT 
    COALESCE(w.name, 'ALL WAREHOUSES') AS warehouse_name,
    COALESCE(cat.name, 'ALL CATEGORIES') AS category_name,
    COUNT(DISTINCT ws.item_id) AS distinct_item_count,
    SUM(ws.quantity) AS total_units_stored,
    ROUND(SUM(ws.quantity * i.cost_price), 2) AS total_valuation
FROM warehouse_stocks ws
JOIN warehouses w ON ws.warehouse_id = w.warehouse_id
JOIN inventory_items i ON ws.item_id = i.item_id
JOIN product_categories cat ON i.category_id = cat.category_id
GROUP BY CUBE (w.name, cat.name)
ORDER BY warehouse_name, category_name;

-- Q24: GROUPING SETS: Flexible Multi-Perspective Financial Payment Analysis
-- Concept: GROUPING SETS aggregating by payment_type, payment_method, and overall
SELECT 
    payment_type,
    payment_method,
    COUNT(payment_id) AS transaction_count,
    SUM(amount) AS total_transacted_volume,
    ROUND(AVG(amount), 2) AS avg_transaction_size
FROM financial_payments
GROUP BY GROUPING SETS (
    (payment_type, payment_method),
    (payment_type),
    (payment_method),
    ()
)
ORDER BY payment_type NULLS LAST, payment_method NULLS LAST;

-- Q25: FILTER Clause inside Aggregation Functions (PostgreSQL Specific)
-- Concept: Clean SQL standard FILTER (WHERE ...) inside aggregate functions
SELECT 
    d.name AS department_name,
    COUNT(e.employee_id) AS total_headcount,
    COUNT(e.employee_id) FILTER (WHERE e.status = 'ACTIVE') AS active_count,
    COUNT(e.employee_id) FILTER (WHERE e.status = 'ON_LEAVE') AS on_leave_count,
    COUNT(e.employee_id) FILTER (WHERE e.status = 'TERMINATED') AS terminated_count,
    ROUND(AVG(e.salary) FILTER (WHERE e.employment_type = 'FULL_TIME'), 2) AS avg_fulltime_salary,
    ROUND(AVG(e.salary) FILTER (WHERE e.employment_type = 'CONTRACT'), 2) AS avg_contract_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.name
ORDER BY total_headcount DESC;

-- ============================================================================
-- MODULE 6: ENTERPRISE ANALYTICAL REPORTS & FORENSICS (Q26 - Q30)
-- ============================================================================

-- Q26: Employee Annual Cohort Retention Analysis
-- Concept: Calculating annual cohort retention and attrition rates
SELECT 
    EXTRACT(YEAR FROM hire_date) AS hire_cohort_year,
    COUNT(employee_id) AS total_hired,
    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) AS currently_active,
    COUNT(CASE WHEN status = 'TERMINATED' OR status = 'RESIGNED' THEN 1 END) AS departed,
    ROUND((COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END)::NUMERIC / COUNT(employee_id)) * 100.0, 2) AS retention_rate_pct,
    ROUND(AVG(salary), 2) AS avg_cohort_salary
FROM employees
GROUP BY EXTRACT(YEAR FROM hire_date)
ORDER BY hire_cohort_year DESC;

-- Q27: Supplier Lead Time & Delivery Deviation Analysis
-- Concept: Date arithmetic measuring expected vs actual delivery deviations
SELECT 
    s.company_name AS supplier_name,
    po.po_number,
    po.order_date,
    po.expected_delivery_date,
    MAX(poi.received_at)::DATE AS actual_fulfillment_date,
    MAX(poi.received_at)::DATE - po.order_date AS total_lead_days,
    MAX(poi.received_at)::DATE - po.expected_delivery_date AS days_deviation_from_promise,
    CASE 
        WHEN MAX(poi.received_at)::DATE <= po.expected_delivery_date THEN 'ON_TIME_OR_EARLY'
        ELSE 'LATE_DELIVERY'
    END AS delivery_performance
FROM purchase_orders po
JOIN suppliers s ON po.supplier_id = s.supplier_id
JOIN purchase_order_items poi ON po.po_id = poi.po_id
WHERE po.status = 'RECEIVED' AND poi.received_at IS NOT NULL
GROUP BY s.company_name, po.po_number, po.order_date, po.expected_delivery_date
ORDER BY days_deviation_from_promise DESC;

-- Q28: Attendance Anomaly & Tardiness Detection Report
-- Concept: Multi-metric behavioral analysis flagging attendance compliance risks
SELECT 
    e.employee_number,
    e.first_name || ' ' || e.last_name AS employee_name,
    d.name AS department_name,
    COUNT(ar.attendance_id) AS total_tracked_days,
    COUNT(CASE WHEN ar.status = 'LATE' THEN 1 END) AS times_late,
    COUNT(CASE WHEN ar.status = 'HALF_DAY' THEN 1 END) AS half_days,
    COUNT(CASE WHEN ar.status = 'ABSENT' THEN 1 END) AS absences,
    ROUND((COUNT(CASE WHEN ar.status = 'LATE' THEN 1 END)::NUMERIC / NULLIF(COUNT(ar.attendance_id), 0)) * 100.0, 2) AS tardiness_ratio_pct
FROM attendance_records ar
JOIN employees e ON ar.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
WHERE ar.work_date >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY e.employee_id, e.employee_number, e.first_name, e.last_name, d.name
HAVING COUNT(CASE WHEN ar.status = 'LATE' THEN 1 END) >= 1
ORDER BY tardiness_ratio_pct DESC;

-- Q29: Cash Flow Runway & Liquid Coverage Ratio Forecast
-- Concept: Cross-module treasury analysis (liquid receipts vs obligations)
WITH TotalReceipts AS (
    SELECT COALESCE(SUM(amount), 0.00) AS total_collected 
    FROM financial_payments 
    WHERE payment_type = 'CUSTOMER_RECEIPT'
),
TotalVendorBills AS (
    SELECT COALESCE(SUM(total_amount - subtotal), 0.00) AS pending_po_commitments 
    FROM purchase_orders 
    WHERE status IN ('APPROVED', 'ORDERED')
),
MonthlyPayrollObligation AS (
    SELECT COALESCE(SUM(salary) / 12.0, 0.00) AS estimated_monthly_payroll 
    FROM employees 
    WHERE status = 'ACTIVE' AND is_deleted = FALSE
),
OutstandingReceivables AS (
    SELECT COALESCE(SUM(balance_due), 0.00) AS total_uncollected_invoices 
    FROM sales_invoices 
    WHERE payment_status != 'PAID'
)
SELECT 
    tr.total_collected AS historical_cash_collected,
    ori.total_uncollected_invoices AS immediate_receivables,
    ROUND(mpo.estimated_monthly_payroll, 2) AS monthly_payroll_burn,
    ROUND(tvb.pending_po_commitments, 2) AS open_po_commitments,
    ROUND((tr.total_collected + ori.total_uncollected_invoices) / NULLIF(mpo.estimated_monthly_payroll, 0), 1) AS runway_months_coverage
FROM TotalReceipts tr
CROSS JOIN TotalVendorBills tvb
CROSS JOIN MonthlyPayrollObligation mpo
CROSS JOIN OutstandingReceivables ori;

-- Q30: Audit Trail Forensics: Salary Modification Tracking via JSONB Diffs
-- Concept: Querying JSONB operators (->>, ?, -) to detect data mutations
SELECT 
    al.audit_id,
    al.changed_at,
    COALESCE(e.first_name || ' ' || e.last_name, 'System') AS modified_by,
    al.record_id AS target_employee_id,
    al.old_data->>'salary' AS old_salary,
    al.new_data->>'salary' AS new_salary,
    ROUND((al.new_data->>'salary')::NUMERIC - (al.old_data->>'salary')::NUMERIC, 2) AS salary_increase_amount,
    ROUND((
        ((al.new_data->>'salary')::NUMERIC - (al.old_data->>'salary')::NUMERIC) / 
        NULLIF((al.old_data->>'salary')::NUMERIC, 0)
    ) * 100.0, 2) AS pct_change
FROM audit_logs al
LEFT JOIN employees e ON al.changed_by = e.employee_id
WHERE al.table_name = 'employees' 
  AND al.action = 'UPDATE'
  AND al.new_data ? 'salary'
  AND al.old_data ? 'salary'
ORDER BY al.changed_at DESC;
