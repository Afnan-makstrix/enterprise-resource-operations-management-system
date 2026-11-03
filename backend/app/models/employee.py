"""
Department and Employee Domain Models
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, index=True)
    department_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    budget = Column(Numeric(15, 2), default=0.00, nullable=False)
    location = Column(String(100), default="Headquarters")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String(30), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    job_title = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id", ondelete="RESTRICT"), nullable=False, index=True)
    manager_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False, index=True)
    hire_date = Column(Date, default=date.today, nullable=False)
    salary = Column(Numeric(12, 2), nullable=False)
    employment_type = Column(String(20), default="FULL_TIME", nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    manager = relationship("Employee", remote_side=[employee_id], backref="direct_reports")
    role = relationship("Role", back_populates="employees")
    credential = relationship("UserCredential", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    profile = relationship("EmployeeProfile", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    salary_structure = relationship("SalaryStructure", back_populates="employee", uselist=False, cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class UserCredential(Base):
    __tablename__ = "user_credentials"

    credential_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), unique=True, nullable=False)
    username = Column(String(60), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="credential")

class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), unique=True, nullable=False)
    national_id = Column(String(50), unique=True, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    marital_status = Column(String(20), default="SINGLE")
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    country = Column(String(50), default="United States")
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="profile")
