-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- ADVANCED DATABASE INDEXING STRATEGIES
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

-- ============================================================================
-- 1. B-TREE INDEXES ON FOREIGN KEYS & JOIN COLUMNS
-- Reduces sequential scans on high-cardinality relational joins
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager_id ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_employees_role_id ON employees(role_id);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date);

CREATE INDEX IF NOT EXISTS idx_attendance_employee_id ON attendance_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_work_date ON attendance_records(work_date);

CREATE INDEX IF NOT EXISTS idx_leave_requests_employee_id ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);
CREATE INDEX IF NOT EXISTS idx_leave_balances_emp_type ON leave_balances(employee_id, leave_type_id);

CREATE INDEX IF NOT EXISTS idx_payrolls_employee_id ON payrolls(employee_id);
CREATE INDEX IF NOT EXISTS idx_payrolls_pay_date ON payrolls(pay_date);
CREATE INDEX IF NOT EXISTS idx_payrolls_status ON payrolls(status);

CREATE INDEX IF NOT EXISTS idx_inventory_items_category_id ON inventory_items(category_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_stocks_warehouse_id ON warehouse_stocks(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_stocks_item_id ON warehouse_stocks(item_id);

CREATE INDEX IF NOT EXISTS idx_inv_trans_item_id ON inventory_transactions(item_id);
CREATE INDEX IF NOT EXISTS idx_inv_trans_warehouse_id ON inventory_transactions(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_inv_trans_date ON inventory_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_po_supplier_id ON purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_po_warehouse_id ON purchase_orders(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_po_items_po_id ON purchase_order_items(po_id);
CREATE INDEX IF NOT EXISTS idx_po_items_item_id ON purchase_order_items(item_id);

CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_pm_id ON projects(project_manager_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON project_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_task_time_logs_task_id ON task_time_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_time_logs_emp_id ON task_time_logs(employee_id);

CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON sales_invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_project_id ON sales_invoices(project_id);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON sales_invoices(due_date);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);

CREATE INDEX IF NOT EXISTS idx_payments_invoice_id ON financial_payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payments_po_id ON financial_payments(po_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON financial_payments(payment_date);

-- ============================================================================
-- 2. COMPOSITE INDEXES FOR HIGH-TRAFFIC MULTI-COLUMN FILTERING
-- Optimizes query planner for WHERE colA = x AND colB = y patterns
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_comp_employees_dept_status 
ON employees(department_id, status);

CREATE INDEX IF NOT EXISTS idx_comp_attendance_emp_date 
ON attendance_records(employee_id, work_date DESC);

CREATE INDEX IF NOT EXISTS idx_comp_tasks_proj_status_prio 
ON project_tasks(project_id, status, priority);

CREATE INDEX IF NOT EXISTS idx_comp_invoices_client_status 
ON sales_invoices(client_id, payment_status, due_date);

CREATE INDEX IF NOT EXISTS idx_comp_inv_trans_type_date 
ON inventory_transactions(transaction_type, transaction_date DESC);

CREATE INDEX IF NOT EXISTS idx_comp_leave_req_emp_status 
ON leave_requests(employee_id, status, start_date);

-- ============================================================================
-- 3. PARTIAL INDEXES (HIGH-VALUE FILTERED SUBSETS)
-- Significantly smaller index size, blazing fast scans for active workloads
-- ============================================================================

-- Active, non-deleted employees only (ignores retired/terminated records)
CREATE INDEX IF NOT EXISTS idx_partial_active_employees 
ON employees(employee_id, department_id, salary) 
WHERE is_deleted = FALSE AND status = 'ACTIVE';

-- Unpaid / delinquent invoices only (ignores millions of archived paid invoices)
CREATE INDEX IF NOT EXISTS idx_partial_unpaid_invoices 
ON sales_invoices(invoice_id, client_id, due_date, balance_due) 
WHERE payment_status != 'PAID';

-- Active / in-flight project tasks only
CREATE INDEX IF NOT EXISTS idx_partial_open_tasks 
ON project_tasks(task_id, project_id, assigned_to, due_date) 
WHERE status NOT IN ('DONE', 'CANCELLED');

-- Unread notifications only (instant user dashboard alert bell queries)
CREATE INDEX IF NOT EXISTS idx_partial_unread_notifications 
ON system_notifications(recipient_id, created_at DESC) 
WHERE is_read = FALSE;

-- Low stock inventory reorder alerts
CREATE INDEX IF NOT EXISTS idx_partial_low_stock_items 
ON inventory_items(item_id, sku, total_quantity_on_hand, reorder_level) 
WHERE total_quantity_on_hand <= reorder_level AND is_active = TRUE;

-- ============================================================================
-- 4. FUNCTIONAL / EXPRESSION INDEXES
-- Eliminates table scans on case-insensitive lookups and date aggregations
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_expr_employees_email_lower 
ON employees(LOWER(email));

CREATE INDEX IF NOT EXISTS idx_expr_clients_name_lower 
ON clients(LOWER(company_name));

CREATE INDEX IF NOT EXISTS idx_expr_suppliers_name_lower 
ON suppliers(LOWER(company_name));

CREATE INDEX IF NOT EXISTS idx_expr_attendance_year_month 
ON attendance_records(EXTRACT(YEAR FROM work_date), EXTRACT(MONTH FROM work_date));

-- ============================================================================
-- 5. GIN (GENERALIZED INVERTED) INDEXES FOR JSONB AUDIT LOGS
-- Accelerates arbitrary key/value JSON search inside audit history
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_gin_audit_logs_old_data 
ON audit_logs USING GIN (old_data);

CREATE INDEX IF NOT EXISTS idx_gin_audit_logs_new_data 
ON audit_logs USING GIN (new_data);

CREATE INDEX IF NOT EXISTS idx_gin_audit_table_action 
ON audit_logs(table_name, action, changed_at DESC);
