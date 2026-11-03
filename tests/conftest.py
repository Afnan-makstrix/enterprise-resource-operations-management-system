"""
Pytest Fixtures and Test Setup for EROMS
Configures a dedicated PostgreSQL test database: eroms_test_db
Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.config import settings
from backend.app.models.employee import Department, Employee, UserCredential
from backend.app.models.rbac import Role
from backend.app.core.security import get_password_hash, create_access_token

TEST_DATABASE_URL = "postgresql+psycopg2://eroms_admin:eroms_secure_password_2026@127.0.0.1:5432/eroms_test_db"

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Seeds essential baseline reference data in the test database."""
    db = TestingSessionLocal()
    
    # 1. Super Admin role
    admin_role = db.query(Role).filter(Role.role_name == "Super Admin").first()
    if not admin_role:
        admin_role = Role(role_name="Super Admin", description="Full system access", is_system=True)
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    # 2. Staff role
    staff_role = db.query(Role).filter(Role.role_name == "Staff").first()
    if not staff_role:
        staff_role = Role(role_name="Staff", description="Standard staff", is_system=False)
        db.add(staff_role)
        db.commit()
        db.refresh(staff_role)

    # 3. Test Department
    test_dept = db.query(Department).filter(Department.department_code == "TEST_DEPT").first()
    if not test_dept:
        test_dept = Department(
            department_code="TEST_DEPT",
            name="Test Engineering Department",
            description="Department used exclusively for automated test cases",
            budget=1000000.00,
            location="Test Lab"
        )
        db.add(test_dept)
        db.commit()
        db.refresh(test_dept)

    # 4. Test Admin Employee
    admin_emp = db.query(Employee).filter(Employee.email == "admin.tester@eroms-test.com").first()
    if not admin_emp:
        admin_emp = Employee(
            employee_number="EMP-TEST-001",
            first_name="Admin",
            last_name="Tester",
            email="admin.tester@eroms-test.com",
            job_title="Lead Quality Architect",
            department_id=test_dept.department_id,
            role_id=admin_role.role_id,
            salary=125000.00,
            employment_type="FULL_TIME",
            status="ACTIVE"
        )
        db.add(admin_emp)
        db.commit()
        db.refresh(admin_emp)

    # 5. Test Admin UserCredential
    cred = db.query(UserCredential).filter(UserCredential.username == "admin_tester").first()
    if not cred:
        cred = UserCredential(
            employee_id=admin_emp.employee_id,
            username="admin_tester",
            password_hash=get_password_hash("TestPassword123!")
        )
        db.add(cred)
        db.commit()
    else:
        cred.password_hash = get_password_hash("TestPassword123!")
        db.commit()

    db.close()
    yield

@pytest.fixture
def db_session():
    """Provides an isolated database session per test function."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token():
    """Generates a valid JWT token for the test admin user."""
    db = TestingSessionLocal()
    admin_emp = db.query(Employee).filter(Employee.email == "admin.tester@eroms-test.com").first()
    token = create_access_token(
        data={"sub": "admin_tester", "emp_id": admin_emp.employee_id, "role": "Super Admin"}
    )
    db.close()
    return token

@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
