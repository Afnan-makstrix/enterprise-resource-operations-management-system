"""
Finance, Payroll, Invoicing & Financial Payment Models
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Date, Numeric, Text, ForeignKey, UniqueConstraint
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from backend.app.database import Base

class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    structure_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), unique=True, nullable=False)
    base_salary = Column(Numeric(12, 2), nullable=False)
    house_rent_allowance = Column(Numeric(10, 2), default=0.00, nullable=False)
    transport_allowance = Column(Numeric(10, 2), default=0.00, nullable=False)
    medical_allowance = Column(Numeric(10, 2), default=0.00, nullable=False)
    tax_deduction_pct = Column(Numeric(5, 2), default=10.00, nullable=False)
    provident_fund_pct = Column(Numeric(5, 2), default=5.00, nullable=False)
    effective_from = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="salary_structure")

class Payroll(Base):
    __tablename__ = "payrolls"

    payroll_id = Column(BigInteger, primary_key=True, index=True)
    payroll_number = Column(String(30), unique=True, nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False, index=True)
    base_salary = Column(Numeric(12, 2), nullable=False)
    total_allowances = Column(Numeric(10, 2), default=0.00, nullable=False)
    gross_salary = Column(Numeric(12, 2), nullable=False)
    tax_deduction = Column(Numeric(10, 2), default=0.00, nullable=False)
    provident_fund = Column(Numeric(10, 2), default=0.00, nullable=False)
    other_deductions = Column(Numeric(10, 2), default=0.00, nullable=False)
    net_salary = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default="DRAFT", nullable=False, index=True)
    payment_method = Column(String(30), default="DIRECT_DEPOSIT")
    processed_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    processor = relationship("Employee", foreign_keys=[processed_by])

class SalesInvoice(Base):
    __tablename__ = "sales_invoices"

    invoice_id = Column(BigInteger, primary_key=True, index=True)
    invoice_number = Column(String(35), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="RESTRICT"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="SET NULL"), nullable=True, index=True)
    issue_date = Column(Date, default=date.today, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    subtotal = Column(Numeric(15, 2), default=0.00, nullable=False)
    tax_rate = Column(Numeric(5, 2), default=10.00, nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    balance_due = Column(Numeric(15, 2), server_default=FetchedValue()) # Generated stored column
    payment_status = Column(String(20), default="UNPAID", nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    client = relationship("Client")
    project = relationship("Project")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("FinancialPayment", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    invoice_item_id = Column(BigInteger, primary_key=True, index=True)
    invoice_id = Column(BigInteger, ForeignKey("sales_invoices.invoice_id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.item_id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(15, 2), server_default=FetchedValue()) # Generated stored column

    invoice = relationship("SalesInvoice", back_populates="items")
    item = relationship("InventoryItem")

class FinancialPayment(Base):
    __tablename__ = "financial_payments"

    payment_id = Column(BigInteger, primary_key=True, index=True)
    payment_number = Column(String(35), unique=True, nullable=False, index=True)
    payment_type = Column(String(20), nullable=False, index=True)
    invoice_id = Column(BigInteger, ForeignKey("sales_invoices.invoice_id", ondelete="SET NULL"), nullable=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.po_id", ondelete="SET NULL"), nullable=True, index=True)
    payroll_id = Column(BigInteger, ForeignKey("payrolls.payroll_id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)
    transaction_reference = Column(String(100), unique=True, nullable=True)
    payment_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    processed_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    invoice = relationship("SalesInvoice", back_populates="payments")
