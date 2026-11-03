-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- ROW-LEVEL SECURITY (RLS) & GRANULAR ACCESS CONTROL POLICIES
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

-- ============================================================================
-- 1. ENABLE ROW LEVEL SECURITY ON SENSITIVE TABLES
-- ============================================================================
ALTER TABLE payrolls ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE leave_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Note: In PostgreSQL, table owners/superusers bypass RLS by default.
-- FORCE ROW LEVEL SECURITY ensures even table owners are evaluated by RLS policies when testing.
ALTER TABLE payrolls FORCE ROW LEVEL SECURITY;
ALTER TABLE attendance_records FORCE ROW LEVEL SECURITY;
ALTER TABLE leave_requests FORCE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. HELPER FUNCTIONS FOR SESSION CONTEXT
-- Reads session settings set by backend connection pool:
-- SET LOCAL app.current_user_id = '42';
-- SET LOCAL app.current_user_role = 'Admin';
-- ============================================================================
CREATE OR REPLACE FUNCTION current_app_user_id() 
RETURNS INT AS $$
BEGIN
    RETURN NULLIF(CURRENT_SETTING('app.current_user_id', TRUE), '')::INT;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION current_app_user_role() 
RETURNS TEXT AS $$
BEGIN
    RETURN COALESCE(NULLIF(CURRENT_SETTING('app.current_user_role', TRUE), ''), 'ANONYMOUS');
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'ANONYMOUS';
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 3. RLS POLICIES FOR PAYROLLS
-- Sensitive salary data: only the employee themselves, or HR/Super Admin can view
-- ============================================================================
DROP POLICY IF EXISTS rls_payroll_access_policy ON payrolls;
CREATE POLICY rls_payroll_access_policy ON payrolls
    FOR ALL
    USING (
        -- Admins and HR have full visibility
        current_app_user_role() IN ('Super Admin', 'Admin', 'HR Manager', 'Finance Manager')
        OR
        -- Employee can only read their own compensation
        (employee_id = current_app_user_id())
        OR
        -- Internal background maintenance fallback
        (current_app_user_id() IS NULL)
    );

-- ============================================================================
-- 4. RLS POLICIES FOR LEAVE REQUESTS
-- Employees see their own; Department Managers see their team's requests
-- ============================================================================
DROP POLICY IF EXISTS rls_leave_requests_policy ON leave_requests;
CREATE POLICY rls_leave_requests_policy ON leave_requests
    FOR ALL
    USING (
        current_app_user_role() IN ('Super Admin', 'Admin', 'HR Manager')
        OR
        employee_id = current_app_user_id()
        OR
        -- Direct manager access
        EXISTS (
            SELECT 1 FROM employees e 
            WHERE e.employee_id = leave_requests.employee_id 
              AND e.manager_id = current_app_user_id()
        )
        OR
        current_app_user_id() IS NULL
    );

-- ============================================================================
-- 5. RLS POLICIES FOR ATTENDANCE
-- Employees log/view own attendance; Managers view department attendance
-- ============================================================================
DROP POLICY IF EXISTS rls_attendance_policy ON attendance_records;
CREATE POLICY rls_attendance_policy ON attendance_records
    FOR ALL
    USING (
        current_app_user_role() IN ('Super Admin', 'Admin', 'HR Manager')
        OR
        employee_id = current_app_user_id()
        OR
        EXISTS (
            SELECT 1 FROM employees e 
            WHERE e.employee_id = attendance_records.employee_id 
              AND e.manager_id = current_app_user_id()
        )
        OR
        current_app_user_id() IS NULL
    );

-- ============================================================================
-- 6. RLS POLICIES FOR AUDIT LOGS
-- Audit logs are strictly immutable and only readable by Security & Super Admin
-- ============================================================================
DROP POLICY IF EXISTS rls_audit_logs_read_only ON audit_logs;
CREATE POLICY rls_audit_logs_read_only ON audit_logs
    FOR SELECT
    USING (
        current_app_user_role() IN ('Super Admin', 'Admin', 'Security Auditor')
        OR
        current_app_user_id() IS NULL
    );

-- Prevent unauthorized UPDATE/DELETE on audit_logs completely
DROP POLICY IF EXISTS rls_audit_logs_prevent_tampering ON audit_logs;
CREATE POLICY rls_audit_logs_prevent_tampering ON audit_logs
    FOR UPDATE
    USING (FALSE);
