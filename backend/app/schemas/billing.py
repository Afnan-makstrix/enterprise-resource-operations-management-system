"""
Sales Invoicing, Financial Payments & Billing Schemas
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class InvoiceItemCreate(BaseModel):
    item_id: Optional[int] = None
    description: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)

class InvoiceCreate(BaseModel):
    client_id: int
    project_id: Optional[int] = None
    issue_date: Optional[date] = None
    due_date: date
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]

class InvoiceItemOut(BaseModel):
    invoice_item_id: int
    item_id: Optional[int]
    description: str
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True

class InvoiceOut(BaseModel):
    invoice_id: int
    invoice_number: str
    client_id: int
    client_name: Optional[str] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    issue_date: date
    due_date: date
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    balance_due: float
    payment_status: str
    created_at: datetime
    items: List[InvoiceItemOut] = []

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    invoice_id: Optional[int] = None
    po_id: Optional[int] = None
    payment_type: str = "CUSTOMER_RECEIPT"
    amount: float = Field(..., gt=0)
    payment_method: str = "BANK_TRANSFER"
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentOut(BaseModel):
    payment_id: int
    payment_number: str
    payment_type: str
    invoice_id: Optional[int]
    amount: float
    payment_method: str
    transaction_reference: Optional[str]
    payment_date: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True
