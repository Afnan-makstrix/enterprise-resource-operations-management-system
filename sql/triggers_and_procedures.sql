-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- ADVANCED DATABASE PROCEDURES, FUNCTIONS & TRIGGERS (PL/pgSQL)
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

-- ============================================================================
-- 1. STORED PROCEDURE: EMPLOYEE ONBOARDING TRANSACTION
-- Atomically creates employee, profile, user credentials, and leave allocations
-- Demonstrates: ACID transactions, SAVEPOINT, exception rollback, strict data integrity
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_onboard_employee(
    p_employee_number VARCHAR(30),
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50),
    p_email VARCHAR(120),
    p_phone VARCHAR(30),
    p_job_title VARCHAR(100),
    p_department_code VARCHAR(20),
    p_role_name VARCHAR(50),
    p_salary NUMERIC(12, 2),
    p_manager_email VARCHAR(120) DEFAULT NULL,
    p_username VARCHAR(60) DEFAULT NULL,
    p_password_hash VARCHAR(255) DEFAULT NULL,
    p_employment_type VARCHAR(20) DEFAULT 'FULL_TIME'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_department_id INT;
    v_role_id INT;
    v_manager_id INT := NULL;
    v_new_emp_id INT;
    v_current_year INT := EXTRACT(YEAR FROM CURRENT_DATE);
    v_leave_rec RECORD;
BEGIN
    -- 1. Validate Department
    SELECT department_id INTO v_department_id 
    FROM departments 
    WHERE department_code = p_department_code AND is_active = TRUE;
    
    IF v_department_id IS NULL THEN
        RAISE EXCEPTION 'Department code % not found or inactive.', p_department_code;
    END IF;

    -- 2. Validate Role
    SELECT role_id INTO v_role_id 
    FROM roles 
    WHERE role_name = p_role_name;
    
    IF v_role_id IS NULL THEN
        RAISE EXCEPTION 'Role % does not exist.', p_role_name;
    END IF;

    -- 3. Resolve Manager if specified
    IF p_manager_email IS NOT NULL THEN
        SELECT employee_id INTO v_manager_id 
        FROM employees 
        WHERE email = p_manager_email AND is_deleted = FALSE;
        
        IF v_manager_id IS NULL THEN
            RAISE NOTICE 'Manager email % not found. Defaulting to NULL.', p_manager_email;
        END IF;
    END IF;

    -- 4. Insert Employee Record
    INSERT INTO employees (
        employee_number, first_name, last_name, email, phone, job_title,
        department_id, manager_id, role_id, salary, employment_type, status, hire_date
    ) VALUES (
        p_employee_number, p_first_name, p_last_name, p_email, p_phone, p_job_title,
        v_department_id, v_manager_id, v_role_id, p_salary, p_employment_type, 'ACTIVE', CURRENT_DATE
    ) RETURNING employee_id INTO v_new_emp_id;

    -- 5. Insert Default Profile
    INSERT INTO employee_profiles (employee_id, country)
    VALUES (v_new_emp_id, 'United States');

    -- 6. Insert User Credentials if credentials supplied
    IF p_username IS NOT NULL AND p_password_hash IS NOT NULL THEN
        INSERT INTO user_credentials (employee_id, username, password_hash)
        VALUES (v_new_emp_id, p_username, p_password_hash);
    END IF;

    -- 7. Initialize Default Annual Leave Balances for all active leave types
    FOR v_leave_rec IN SELECT leave_type_id, annual_allowance FROM leave_types LOOP
        INSERT INTO leave_balances (
            employee_id, leave_type_id, year, total_allocated, used_days, pending_days
        ) VALUES (
            v_new_emp_id, v_leave_rec.leave_type_id, v_current_year, v_leave_rec.annual_allowance, 0, 0
        ) ON CONFLICT (employee_id, leave_type_id, year) DO NOTHING;
    END LOOP;

    -- 8. Initialize Default Salary Structure
    INSERT INTO salary_structures (
        employee_id, base_salary, house_rent_allowance, transport_allowance, medical_allowance
    ) VALUES (
        v_new_emp_id, p_salary * 0.70, p_salary * 0.15, p_salary * 0.08, p_salary * 0.07
    );

    -- 9. Insert Audit Log
    INSERT INTO audit_logs (table_name, record_id, action, new_data)
    VALUES ('employees', v_new_emp_id::TEXT, 'INSERT', jsonb_build_object(
        'employee_number', p_employee_number,
        'email', p_email,
        'department_id', v_department_id,
        'salary', p_salary
    ));

    RAISE NOTICE 'Employee % (%) onboarded successfully with ID %.', p_employee_number, p_email, v_new_emp_id;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to onboard employee: % (SQLSTATE: %)', SQLERRM, SQLSTATE;
END;
$$;

-- ============================================================================
-- 2. STORED PROCEDURE: LEAVE APPROVAL & BALANCE ADJUSTMENT
-- Atomically validates balance, approves leave, updates used days, logs audit
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_process_leave_approval(
    p_leave_request_id INT,
    p_approver_id INT,
    p_decision VARCHAR(20), -- 'APPROVED' or 'REJECTED'
    p_rejection_reason TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_req RECORD;
    v_balance RECORD;
    v_year INT;
BEGIN
    -- 1. Fetch and Lock Leave Request
    SELECT * INTO v_req
    FROM leave_requests
    WHERE leave_request_id = p_leave_request_id
    FOR UPDATE;

    IF v_req IS NULL THEN
        RAISE EXCEPTION 'Leave request % does not exist.', p_leave_request_id;
    END IF;

    IF v_req.status != 'PENDING' THEN
        RAISE EXCEPTION 'Leave request % has already been %.', p_leave_request_id, v_req.status;
    END IF;

    v_year := EXTRACT(YEAR FROM v_req.start_date);

    IF p_decision = 'APPROVED' THEN
        -- Check and Lock Leave Balance
        SELECT * INTO v_balance
        FROM leave_balances
        WHERE employee_id = v_req.employee_id AND leave_type_id = v_req.leave_type_id AND year = v_year
        FOR UPDATE;

        IF v_balance IS NULL THEN
            RAISE EXCEPTION 'No leave balance record found for employee % in year %.', v_req.employee_id, v_year;
        END IF;

        IF v_balance.remaining_days < v_req.total_days THEN
            RAISE EXCEPTION 'Insufficient leave balance. Requested: %, Available: %', v_req.total_days, v_balance.remaining_days;
        END IF;

        -- Update Leave Balance: increment used_days
        UPDATE leave_balances
        SET used_days = used_days + v_req.total_days
        WHERE balance_id = v_balance.balance_id;

        -- Update Request Status
        UPDATE leave_requests
        SET status = 'APPROVED',
            approved_by = p_approver_id,
            approved_at = CURRENT_TIMESTAMP
        WHERE leave_request_id = p_leave_request_id;

        -- Insert System Notification for Employee
        INSERT INTO system_notifications (recipient_id, title, message, notification_type)
        VALUES (
            v_req.employee_id,
            'Leave Request Approved',
            FORMAT('Your leave request for %s days starting %s has been APPROVED.', v_req.total_days, v_req.start_date),
            'LEAVE_STATUS'
        );

    ELSIF p_decision = 'REJECTED' THEN
        UPDATE leave_requests
        SET status = 'REJECTED',
            approved_by = p_approver_id,
            approved_at = CURRENT_TIMESTAMP,
            rejection_reason = p_rejection_reason
        WHERE leave_request_id = p_leave_request_id;

        INSERT INTO system_notifications (recipient_id, title, message, notification_type)
        VALUES (
            v_req.employee_id,
            'Leave Request Rejected',
            FORMAT('Your leave request from %s has been REJECTED. Reason: %s', v_req.start_date, COALESCE(p_rejection_reason, 'No reason specified')),
            'LEAVE_STATUS'
        );
    ELSE
        RAISE EXCEPTION 'Invalid decision: %. Must be APPROVED or REJECTED.', p_decision;
    END IF;

    -- Audit Log Entry
    INSERT INTO audit_logs (table_name, record_id, action, changed_by, new_data)
    VALUES ('leave_requests', p_leave_request_id::TEXT, 'UPDATE', p_approver_id, jsonb_build_object(
        'status', p_decision,
        'approved_by', p_approver_id,
        'days', v_req.total_days
    ));
END;
$$;

-- ============================================================================
-- 3. STORED PROCEDURE: PURCHASE ORDER RECEIPT & INVENTORY FULFILLMENT
-- Updates warehouse stock, records inventory transaction, updates PO status
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_receive_purchase_order(
    p_po_id INT,
    p_receiver_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_po RECORD;
    v_item RECORD;
BEGIN
    -- Fetch and lock PO
    SELECT * INTO v_po 
    FROM purchase_orders 
    WHERE po_id = p_po_id 
    FOR UPDATE;

    IF v_po IS NULL THEN
        RAISE EXCEPTION 'Purchase order % not found.', p_po_id;
    END IF;

    IF v_po.status NOT IN ('APPROVED', 'ORDERED', 'PARTIALLY_RECEIVED') THEN
        RAISE EXCEPTION 'Purchase order % cannot be received because status is %.', p_po_id, v_po.status;
    END IF;

    -- Process each PO line item
    FOR v_item IN SELECT * FROM purchase_order_items WHERE po_id = p_po_id LOOP
        -- Update PO item received quantity
        UPDATE purchase_order_items
        SET quantity_received = quantity_ordered,
            received_at = CURRENT_TIMESTAMP
        WHERE po_item_id = v_item.po_item_id;

        -- Update or Insert into warehouse_stocks
        INSERT INTO warehouse_stocks (warehouse_id, item_id, quantity)
        VALUES (v_po.warehouse_id, v_item.item_id, v_item.quantity_ordered)
        ON CONFLICT (warehouse_id, item_id)
        DO UPDATE SET quantity = warehouse_stocks.quantity + EXCLUDED.quantity,
                      updated_at = CURRENT_TIMESTAMP;

        -- Update master inventory item total quantity
        UPDATE inventory_items
        SET total_quantity_on_hand = total_quantity_on_hand + v_item.quantity_ordered,
            updated_at = CURRENT_TIMESTAMP
        WHERE item_id = v_item.item_id;

        -- Record Inventory Transaction ledger entry
        INSERT INTO inventory_transactions (
            transaction_type, item_id, warehouse_id, quantity, unit_cost,
            reference_type, reference_id, created_by, notes
        ) VALUES (
            'PURCHASE_RECEIPT', v_item.item_id, v_po.warehouse_id, v_item.quantity_ordered,
            v_item.unit_cost, 'PURCHASE_ORDER', v_po.po_number, p_receiver_id,
            FORMAT('Received via PO #%s', v_po.po_number)
        );
    END LOOP;

    -- Mark PO as RECEIVED
    UPDATE purchase_orders
    SET status = 'RECEIVED',
        updated_at = CURRENT_TIMESTAMP
    WHERE po_id = p_po_id;

    -- Audit log
    INSERT INTO audit_logs (table_name, record_id, action, changed_by, new_data)
    VALUES ('purchase_orders', p_po_id::TEXT, 'UPDATE', p_receiver_id, jsonb_build_object(
        'status', 'RECEIVED',
        'po_number', v_po.po_number
    ));
END;
$$;

-- ============================================================================
-- 4. STORED PROCEDURE: RECORD INVOICE PAYMENT & AUTO-BALANCE
-- Records payment, recalculates balance, updates payment status
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_record_invoice_payment(
    p_invoice_id BIGINT,
    p_amount NUMERIC(15, 2),
    p_payment_method VARCHAR(30),
    p_transaction_reference VARCHAR(100),
    p_processed_by INT,
    p_notes TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_inv RECORD;
    v_new_paid NUMERIC(15, 2);
    v_payment_num VARCHAR(35);
BEGIN
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Payment amount must be greater than zero.';
    END IF;

    -- Lock Invoice
    SELECT * INTO v_inv
    FROM sales_invoices
    WHERE invoice_id = p_invoice_id
    FOR UPDATE;

    IF v_inv IS NULL THEN
        RAISE EXCEPTION 'Invoice % does not exist.', p_invoice_id;
    END IF;

    IF v_inv.payment_status = 'PAID' THEN
        RAISE EXCEPTION 'Invoice % is already fully paid.', v_inv.invoice_number;
    END IF;

    IF p_amount > v_inv.balance_due THEN
        RAISE EXCEPTION 'Payment of % exceeds remaining balance of % on invoice %.', 
            p_amount, v_inv.balance_due, v_inv.invoice_number;
    END IF;

    -- Generate payment number
    v_payment_num := 'PAY-' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD-HH24MISS') || '-' || SUBSTRING(gen_random_uuid()::TEXT, 1, 4);

    -- Insert into financial_payments
    INSERT INTO financial_payments (
        payment_number, payment_type, invoice_id, amount, payment_method,
        transaction_reference, notes, processed_by
    ) VALUES (
        v_payment_num, 'CUSTOMER_RECEIPT', p_invoice_id, p_amount, p_payment_method,
        p_transaction_reference, p_notes, p_processed_by
    );

    -- Update sales invoice paid_amount
    v_new_paid := v_inv.paid_amount + p_amount;
    
    UPDATE sales_invoices
    SET paid_amount = v_new_paid,
        payment_status = CASE 
            WHEN v_new_paid >= total_amount THEN 'PAID'
            ELSE 'PARTIALLY_PAID'
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE invoice_id = p_invoice_id;

    -- Audit Log
    INSERT INTO audit_logs (table_name, record_id, action, changed_by, new_data)
    VALUES ('sales_invoices', p_invoice_id::TEXT, 'UPDATE', p_processed_by, jsonb_build_object(
        'payment_number', v_payment_num,
        'amount_paid', p_amount,
        'new_total_paid', v_new_paid,
        'status', CASE WHEN v_new_paid >= v_inv.total_amount THEN 'PAID' ELSE 'PARTIALLY_PAID' END
    ));
END;
$$;

-- ============================================================================
-- 5. FUNCTION & TRIGGER: LOW STOCK AUTOMATIC ALERT
-- Fires after UPDATE on inventory_items; dispatches alert when stock <= reorder_level
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_check_inventory_reorder()
RETURNS TRIGGER AS $$
DECLARE
    v_admin_id INT;
BEGIN
    IF NEW.total_quantity_on_hand <= NEW.reorder_level AND 
       (OLD.total_quantity_on_hand > NEW.reorder_level OR TG_OP = 'INSERT') THEN
        
        -- Find Procurement / Admin employee
        SELECT employee_id INTO v_admin_id 
        FROM employees e
        JOIN roles r ON e.role_id = r.role_id
        WHERE r.role_name IN ('Super Admin', 'Admin', 'Procurement Manager', 'Inventory Manager')
        LIMIT 1;

        IF v_admin_id IS NOT NULL THEN
            INSERT INTO system_notifications (recipient_id, title, message, notification_type, action_url)
            VALUES (
                v_admin_id,
                'LOW STOCK ALERT: ' || NEW.name,
                FORMAT('Item %s (SKU: %s) is at %s units, which is at or below reorder level (%s). Recommended reorder quantity: %s.',
                    NEW.name, NEW.sku, NEW.total_quantity_on_hand, NEW.reorder_level, NEW.reorder_quantity),
                'SYSTEM',
                '/inventory'
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_inventory_reorder_alert ON inventory_items;
CREATE TRIGGER trg_inventory_reorder_alert
AFTER INSERT OR UPDATE OF total_quantity_on_hand ON inventory_items
FOR EACH ROW EXECUTE FUNCTION fn_trg_check_inventory_reorder();

-- ============================================================================
-- 6. FUNCTION & TRIGGER: AUDIT LOGGING FOR EMPLOYEE RECORD CHANGES
-- Automatically captures before/after JSONB snapshots into audit_logs
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_audit_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data)
        VALUES (
            'employees',
            NEW.employee_id::TEXT,
            'UPDATE',
            to_jsonb(OLD),
            to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data)
        VALUES (
            'employees',
            OLD.employee_id::TEXT,
            'DELETE',
            to_jsonb(OLD)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_employees ON employees;
CREATE TRIGGER trg_audit_employees
AFTER UPDATE OR DELETE ON employees
FOR EACH ROW EXECUTE FUNCTION fn_trg_audit_employee_changes();

-- ============================================================================
-- 7. FUNCTION: CALCULATE EMPLOYEE PAYROLL ACCRUAL
-- PL/pgSQL function to compute net pay based on attendance, allowances, and tax tiers
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_calculate_employee_payroll(
    p_employee_id INT,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    base_salary NUMERIC(12, 2),
    allowances NUMERIC(10, 2),
    gross_salary NUMERIC(12, 2),
    tax NUMERIC(10, 2),
    provident_fund NUMERIC(10, 2),
    net_salary NUMERIC(12, 2),
    attendance_ratio NUMERIC(5, 2)
) AS $$
DECLARE
    v_structure RECORD;
    v_workdays INT := 22; -- Standard monthly workdays
    v_present_days NUMERIC(5, 2) := 0;
    v_ratio NUMERIC(5, 2) := 1.00;
    v_gross NUMERIC(12, 2);
    v_tax NUMERIC(10, 2);
    v_pf NUMERIC(10, 2);
    v_net NUMERIC(12, 2);
BEGIN
    -- Fetch salary structure
    SELECT * INTO v_structure 
    FROM salary_structures 
    WHERE employee_id = p_employee_id;

    IF v_structure IS NULL THEN
        -- Fallback to employee base salary
        SELECT salary, 0.00, 0.00, 0.00, 10.00, 5.00
        INTO v_structure
        FROM employees WHERE employee_id = p_employee_id;
    END IF;

    -- Count attendance
    SELECT COALESCE(SUM(
        CASE 
            WHEN status = 'PRESENT' THEN 1.0
            WHEN status = 'HALF_DAY' THEN 0.5
            WHEN status = 'ON_LEAVE' THEN 1.0
            ELSE 0.0
        END
    ), 22)
    INTO v_present_days
    FROM attendance_records
    WHERE employee_id = p_employee_id 
      AND work_date BETWEEN p_start_date AND p_end_date;

    IF v_present_days > 0 AND v_present_days < v_workdays THEN
        v_ratio := ROUND(v_present_days / v_workdays, 2);
    ELSE
        v_ratio := 1.00;
    END IF;

    base_salary := ROUND(v_structure.base_salary * v_ratio, 2);
    allowances := ROUND((v_structure.house_rent_allowance + v_structure.transport_allowance + v_structure.medical_allowance) * v_ratio, 2);
    gross_salary := base_salary + allowances;
    
    -- Tax calculation (progressive rate simulation)
    tax := ROUND(gross_salary * (v_structure.tax_deduction_pct / 100.0), 2);
    provident_fund := ROUND(base_salary * (v_structure.provident_fund_pct / 100.0), 2);
    net_salary := gross_salary - tax - provident_fund;
    attendance_ratio := v_ratio;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;
