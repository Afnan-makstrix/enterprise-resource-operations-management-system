"""
Database Integrity & Constraint Validation Tests
Tests foreign keys, unique constraints, check constraints, and ACID rollback behavior.
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from backend.app.models.employee import Department, Employee
from backend.app.models.attendance_leave import LeaveRequest, LeaveType
from backend.app.models.finance import SalesInvoice
from backend.app.models.inventory_purchasing import Client

def test_foreign_key_constraint_enforcement(db_session):
    """Attempting to create an employee with a non-existent department_id must raise IntegrityError."""
    invalid_dept_id = 999999
    emp = Employee(
        employee_number="EMP-INV-FK",
        first_name="Invalid",
        last_name="Dept",
        email="invalid.fk@test.com",
        job_title="Engineer",
        department_id=invalid_dept_id,
        role_id=1,
        salary=50000.00
    )
    db_session.add(emp)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "foreign key" in str(exc_info.value).lower()

def test_unique_constraint_enforcement(db_session):
    """Duplicate employee_number or email must be rejected by PostgreSQL unique constraint."""
    dept = db_session.query(Department).first()
    
    emp1 = Employee(
        employee_number="EMP-UQ-001",
        first_name="Unique",
        last_name="One",
        email="unique.test@example.com",
        job_title="Analyst",
        department_id=dept.department_id,
        role_id=1,
        salary=60000.00
    )
    db_session.add(emp1)
    db_session.flush()

    # Attempt to insert identical email and employee_number
    emp2 = Employee(
        employee_number="EMP-UQ-001",
        first_name="Unique",
        last_name="Two",
        email="unique.test@example.com",
        job_title="Analyst",
        department_id=dept.department_id,
        role_id=1,
        salary=65000.00
    )
    db_session.add(emp2)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "unique" in str(exc_info.value).lower()

def test_check_constraint_salary_positive(db_session):
    """PostgreSQL CHECK constraint 'salary > 0' must prevent negative or zero salaries."""
    dept = db_session.query(Department).first()
    emp = Employee(
        employee_number="EMP-NEG-SAL",
        first_name="Negative",
        last_name="Salary",
        email="negative.sal@example.com",
        job_title="Tester",
        department_id=dept.department_id,
        role_id=1,
        salary=-500.00  # Violates CHECK (salary > 0)
    )
    db_session.add(emp)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "check" in str(exc_info.value).lower()

def test_acid_transaction_rollback(db_session):
    """
    ACID Rollback Test: When a multi-statement transaction encounters an error halfway,
    all previous modifications must roll back without partial data corruption.
    """
    dept = db_session.query(Department).first()
    initial_count = db_session.query(Employee).count()

    try:
        # Step 1: Valid Employee Insert
        emp_valid = Employee(
            employee_number="EMP-ROLLBACK-01",
            first_name="Valid",
            last_name="Record",
            email="valid.rollback@example.com",
            job_title="Engineer",
            department_id=dept.department_id,
            role_id=1,
            salary=70000.00
        )
        db_session.add(emp_valid)
        db_session.flush()

        # Step 2: Invalid Employee Insert (violates salary constraint)
        emp_invalid = Employee(
            employee_number="EMP-ROLLBACK-02",
            first_name="Invalid",
            last_name="Record",
            email="invalid.rollback@example.com",
            job_title="Engineer",
            department_id=dept.department_id,
            role_id=1,
            salary=-100.00  # Will fail!
        )
        db_session.add(emp_invalid)
        db_session.flush()

    except IntegrityError:
        db_session.rollback()

    # Verify that Step 1 was also rolled back completely!
    final_count = db_session.query(Employee).count()
    assert final_count == initial_count, "Rollback failed: partial insert persisted!"
    assert db_session.query(Employee).filter(Employee.employee_number == "EMP-ROLLBACK-01").first() is None
