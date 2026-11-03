-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- PRODUCTION RELATIONAL DATABASE SCHEMA (PostgreSQL 16+)
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

-- Ensure pgcrypto extension for UUID generation and hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. UTILITY FUNCTIONS & COMMON DOMAINS
-- ============================================================================

-- Generic trigger function to auto-update 'updated_at' timestamps
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 2. ROLE & PERMISSION MANAGEMENT (RBAC MODULE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_code VARCHAR(100) NOT NULL UNIQUE,
    module_name VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INT NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id INT NOT NULL REFERENCES permissions(permission_id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- ============================================================================
-- 3. DEPARTMENT MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS departments (
    department_id SERIAL PRIMARY KEY,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    manager_id INT, -- Circular reference resolved via ALTER TABLE below
    budget NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (budget >= 0),
    location VARCHAR(100) DEFAULT 'Headquarters',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. EMPLOYEE MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    employee_number VARCHAR(30) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30),
    job_title VARCHAR(100) NOT NULL,
    department_id INT NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
    manager_id INT REFERENCES employees(employee_id) ON DELETE SET NULL, -- Self-referencing org hierarchy
    role_id INT NOT NULL REFERENCES roles(role_id) ON DELETE RESTRICT,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    salary NUMERIC(12, 2) NOT NULL CHECK (salary > 0),
    employment_type VARCHAR(20) NOT NULL DEFAULT 'FULL_TIME' 
        CHECK (employment_type IN ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERN')),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE', 'ON_LEAVE', 'PROBATION', 'TERMINATED', 'RESIGNED')),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Complete circular FK for department manager
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_departments_manager'
    ) THEN
        ALTER TABLE departments 
        ADD CONSTRAINT fk_departments_manager 
        FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS user_credentials (
    credential_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE REFERENCES employees(employee_id) ON DELETE CASCADE,
    username VARCHAR(60) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    failed_login_attempts INT NOT NULL DEFAULT 0 CHECK (failed_login_attempts >= 0),
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_profiles (
    profile_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE REFERENCES employees(employee_id) ON DELETE CASCADE,
    national_id VARCHAR(50) UNIQUE,
    date_of_birth DATE CHECK (date_of_birth < CURRENT_DATE - INTERVAL '16 years'),
    gender VARCHAR(20) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY')),
    blood_group VARCHAR(10),
    marital_status VARCHAR(20) DEFAULT 'SINGLE',
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'United States',
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(30),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 5. LEAVE MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS leave_types (
    leave_type_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    annual_allowance INT NOT NULL CHECK (annual_allowance >= 0),
    is_paid BOOLEAN NOT NULL DEFAULT TRUE,
    carry_forward BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leave_balances (
    balance_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    leave_type_id INT NOT NULL REFERENCES leave_types(leave_type_id) ON DELETE RESTRICT,
    year INT NOT NULL CHECK (year >= 2000),
    total_allocated NUMERIC(5, 2) NOT NULL CHECK (total_allocated >= 0),
    used_days NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (used_days >= 0),
    pending_days NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (pending_days >= 0),
    remaining_days NUMERIC(5, 2) GENERATED ALWAYS AS (total_allocated - used_days) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_employee_leave_type_year UNIQUE (employee_id, leave_type_id, year)
);

CREATE TABLE IF NOT EXISTS leave_requests (
    leave_request_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    leave_type_id INT NOT NULL REFERENCES leave_types(leave_type_id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days NUMERIC(4, 1) NOT NULL CHECK (total_days > 0),
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')),
    approved_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_leave_dates CHECK (end_date >= start_date)
);

-- ============================================================================
-- 6. ATTENDANCE MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS attendance_records (
    attendance_id BIGSERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    check_in TIMESTAMPTZ,
    check_out TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'PRESENT'
        CHECK (status IN ('PRESENT', 'ABSENT', 'LATE', 'HALF_DAY', 'ON_LEAVE', 'REMOTE', 'HOLIDAY')),
    hours_worked NUMERIC(5, 2) DEFAULT 0.00 CHECK (hours_worked >= 0 AND hours_worked <= 24),
    overtime_hours NUMERIC(5, 2) DEFAULT 0.00 CHECK (overtime_hours >= 0 AND overtime_hours <= 16),
    ip_address VARCHAR(45),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_employee_work_date UNIQUE (employee_id, work_date)
);

-- ============================================================================
-- 7. PAYROLL MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS salary_structures (
    structure_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE REFERENCES employees(employee_id) ON DELETE CASCADE,
    base_salary NUMERIC(12, 2) NOT NULL CHECK (base_salary > 0),
    house_rent_allowance NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (house_rent_allowance >= 0),
    transport_allowance NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (transport_allowance >= 0),
    medical_allowance NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (medical_allowance >= 0),
    tax_deduction_pct NUMERIC(5, 2) NOT NULL DEFAULT 10.00 CHECK (tax_deduction_pct >= 0 AND tax_deduction_pct <= 100),
    provident_fund_pct NUMERIC(5, 2) NOT NULL DEFAULT 5.00 CHECK (provident_fund_pct >= 0 AND provident_fund_pct <= 100),
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payrolls (
    payroll_id BIGSERIAL PRIMARY KEY,
    payroll_number VARCHAR(30) NOT NULL UNIQUE,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    pay_date DATE NOT NULL,
    base_salary NUMERIC(12, 2) NOT NULL CHECK (base_salary >= 0),
    total_allowances NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (total_allowances >= 0),
    gross_salary NUMERIC(12, 2) NOT NULL CHECK (gross_salary >= 0),
    tax_deduction NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (tax_deduction >= 0),
    provident_fund NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (provident_fund >= 0),
    other_deductions NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (other_deductions >= 0),
    net_salary NUMERIC(12, 2) NOT NULL CHECK (net_salary >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'APPROVED', 'PROCESSED', 'PAID', 'CANCELLED')),
    payment_method VARCHAR(30) DEFAULT 'DIRECT_DEPOSIT'
        CHECK (payment_method IN ('DIRECT_DEPOSIT', 'CHECK', 'WIRE_TRANSFER', 'CASH')),
    processed_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_payroll_period CHECK (pay_period_end >= pay_period_start),
    CONSTRAINT uq_employee_pay_period UNIQUE (employee_id, pay_period_start, pay_period_end)
);

-- ============================================================================
-- 8. CLIENT & CUSTOMER MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS clients (
    client_id SERIAL PRIMARY KEY,
    client_code VARCHAR(30) NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30),
    billing_address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'United States',
    credit_limit NUMERIC(15, 2) NOT NULL DEFAULT 50000.00 CHECK (credit_limit >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 9. SUPPLIER MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_code VARCHAR(30) NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30),
    tax_identification_number VARCHAR(50) UNIQUE,
    payment_terms VARCHAR(50) DEFAULT 'NET_30',
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'United States',
    rating NUMERIC(3, 2) DEFAULT 5.00 CHECK (rating >= 1.00 AND rating <= 5.00),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'BLACKLISTED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 10. INVENTORY & WAREHOUSE MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS product_categories (
    category_id SERIAL PRIMARY KEY,
    category_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INT REFERENCES product_categories(category_id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_items (
    item_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    category_id INT NOT NULL REFERENCES product_categories(category_id) ON DELETE RESTRICT,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'UNIT',
    cost_price NUMERIC(12, 2) NOT NULL CHECK (cost_price >= 0),
    selling_price NUMERIC(12, 2) NOT NULL CHECK (selling_price >= cost_price),
    total_quantity_on_hand INT NOT NULL DEFAULT 0 CHECK (total_quantity_on_hand >= 0),
    reorder_level INT NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
    reorder_quantity INT NOT NULL DEFAULT 50 CHECK (reorder_quantity > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    manager_id INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse_stocks (
    stock_id SERIAL PRIMARY KEY,
    warehouse_id INT NOT NULL REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    item_id INT NOT NULL REFERENCES inventory_items(item_id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    bin_location VARCHAR(50),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_warehouse_item UNIQUE (warehouse_id, item_id)
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL 
        CHECK (transaction_type IN ('PURCHASE_RECEIPT', 'SALE_DISPATCH', 'TRANSFER', 'ADJUSTMENT', 'RETURN')),
    item_id INT NOT NULL REFERENCES inventory_items(item_id) ON DELETE RESTRICT,
    warehouse_id INT NOT NULL REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    destination_warehouse_id INT REFERENCES warehouses(warehouse_id) ON DELETE SET NULL,
    quantity INT NOT NULL CHECK (quantity != 0), -- Positive for receipt/return, negative for dispatch
    unit_cost NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (unit_cost >= 0),
    reference_type VARCHAR(50) NOT NULL, -- 'PURCHASE_ORDER', 'SALES_INVOICE', 'MANUAL_AUDIT'
    reference_id VARCHAR(50),
    notes TEXT,
    created_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    transaction_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 11. PURCHASE ORDER MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id SERIAL PRIMARY KEY,
    po_number VARCHAR(30) NOT NULL UNIQUE,
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id) ON DELETE RESTRICT,
    warehouse_id INT NOT NULL REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    requested_by INT NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    subtotal NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (subtotal >= 0),
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    shipping_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_fee >= 0),
    total_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'SUBMITTED', 'APPROVED', 'ORDERED', 'RECEIVED', 'PARTIALLY_RECEIVED', 'CANCELLED')),
    approved_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id SERIAL PRIMARY KEY,
    po_id INT NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    item_id INT NOT NULL REFERENCES inventory_items(item_id) ON DELETE RESTRICT,
    quantity_ordered INT NOT NULL CHECK (quantity_ordered > 0),
    quantity_received INT NOT NULL DEFAULT 0 CHECK (quantity_received >= 0 AND quantity_received <= quantity_ordered),
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0),
    subtotal NUMERIC(15, 2) GENERATED ALWAYS AS (quantity_ordered * unit_cost) STORED,
    CONSTRAINT uq_po_item UNIQUE (po_id, item_id)
);

-- ============================================================================
-- 12. PROJECT & TASK MANAGEMENT MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    project_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    client_id INT REFERENCES clients(client_id) ON DELETE SET NULL,
    project_manager_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    target_end_date DATE NOT NULL,
    actual_end_date DATE,
    budget NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (budget >= 0),
    cost_to_date NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (cost_to_date >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'PLANNING'
        CHECK (status IN ('PLANNING', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED')),
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_project_dates CHECK (target_end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS project_members (
    project_member_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    role_in_project VARCHAR(50) NOT NULL DEFAULT 'CONTRIBUTOR',
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_project_employee UNIQUE (project_id, employee_id)
);

CREATE TABLE IF NOT EXISTS project_tasks (
    task_id BIGSERIAL PRIMARY KEY,
    task_code VARCHAR(40) NOT NULL UNIQUE,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    assigned_to INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    reporter_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    parent_task_id BIGINT REFERENCES project_tasks(task_id) ON DELETE SET NULL, -- Self-referencing subtasks
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    status VARCHAR(20) NOT NULL DEFAULT 'TODO'
        CHECK (status IN ('BACKLOG', 'TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'CANCELLED')),
    estimated_hours NUMERIC(6, 2) DEFAULT 0.00 CHECK (estimated_hours >= 0),
    actual_hours NUMERIC(6, 2) DEFAULT 0.00 CHECK (actual_hours >= 0),
    due_date DATE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_time_logs (
    log_id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL REFERENCES project_tasks(task_id) ON DELETE CASCADE,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    log_date DATE NOT NULL DEFAULT CURRENT_DATE,
    hours_logged NUMERIC(5, 2) NOT NULL CHECK (hours_logged > 0 AND hours_logged <= 24),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 13. SALES & INVOICING MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sales_invoices (
    invoice_id BIGSERIAL PRIMARY KEY,
    invoice_number VARCHAR(35) NOT NULL UNIQUE,
    client_id INT NOT NULL REFERENCES clients(client_id) ON DELETE RESTRICT,
    project_id INT REFERENCES projects(project_id) ON DELETE SET NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    subtotal NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (subtotal >= 0),
    tax_rate NUMERIC(5, 2) NOT NULL DEFAULT 10.00 CHECK (tax_rate >= 0),
    tax_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    total_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    paid_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (paid_amount >= 0),
    balance_due NUMERIC(15, 2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'UNPAID'
        CHECK (payment_status IN ('UNPAID', 'PARTIALLY_PAID', 'PAID', 'OVERDUE', 'VOID')),
    notes TEXT,
    created_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_invoice_dates CHECK (due_date >= issue_date)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    invoice_item_id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL REFERENCES sales_invoices(invoice_id) ON DELETE CASCADE,
    item_id INT REFERENCES inventory_items(item_id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    line_total NUMERIC(15, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- ============================================================================
-- 14. FINANCIAL PAYMENTS & TRANSACTIONS MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS financial_payments (
    payment_id BIGSERIAL PRIMARY KEY,
    payment_number VARCHAR(35) NOT NULL UNIQUE,
    payment_type VARCHAR(20) NOT NULL 
        CHECK (payment_type IN ('CUSTOMER_RECEIPT', 'VENDOR_DISBURSEMENT', 'PAYROLL_DISBURSEMENT')),
    invoice_id BIGINT REFERENCES sales_invoices(invoice_id) ON DELETE SET NULL,
    po_id INT REFERENCES purchase_orders(po_id) ON DELETE SET NULL,
    payroll_id BIGINT REFERENCES payrolls(payroll_id) ON DELETE SET NULL,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(30) NOT NULL 
        CHECK (payment_method IN ('BANK_TRANSFER', 'CREDIT_CARD', 'CHECK', 'CASH', 'AUTOMATED_CLEARING')),
    transaction_reference VARCHAR(100) UNIQUE,
    payment_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    processed_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 15. AUDIT LOGGING MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(60) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_by INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 16. NOTIFICATIONS & SYSTEM SETTINGS MODULE
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_notifications (
    notification_id BIGSERIAL PRIMARY KEY,
    recipient_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(30) NOT NULL 
        CHECK (notification_type IN ('LEAVE_STATUS', 'PO_APPROVAL', 'INVOICE_ALERT', 'TASK_ASSIGNED', 'PAYROLL_READY', 'SYSTEM')),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    action_url VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS company_settings (
    setting_id SERIAL PRIMARY KEY,
    setting_key VARCHAR(80) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    description TEXT,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 17. AUTOMATIC TIMESTAMP TRIGGERS
-- ============================================================================

CREATE TRIGGER trg_roles_timestamp BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_departments_timestamp BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_employees_timestamp BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_user_credentials_timestamp BEFORE UPDATE ON user_credentials
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_employee_profiles_timestamp BEFORE UPDATE ON employee_profiles
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_leave_balances_timestamp BEFORE UPDATE ON leave_balances
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_leave_requests_timestamp BEFORE UPDATE ON leave_requests
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_salary_structures_timestamp BEFORE UPDATE ON salary_structures
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_payrolls_timestamp BEFORE UPDATE ON payrolls
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_clients_timestamp BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_suppliers_timestamp BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_inventory_items_timestamp BEFORE UPDATE ON inventory_items
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_warehouses_timestamp BEFORE UPDATE ON warehouses
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_purchase_orders_timestamp BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_projects_timestamp BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_project_tasks_timestamp BEFORE UPDATE ON project_tasks
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_sales_invoices_timestamp BEFORE UPDATE ON sales_invoices
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER trg_company_settings_timestamp BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
