"""
Billing, Invoicing & Financial Transactions API Router
"""
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, text
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.core.pagination import PaginationParams, PaginatedResponse
from backend.app.models.finance import SalesInvoice, InvoiceItem, FinancialPayment
from backend.app.models.employee import Employee
from backend.app.schemas.billing import (
    InvoiceCreate, InvoiceOut, InvoiceItemOut, PaymentCreate, PaymentOut
)

router = APIRouter(prefix="/billing", tags=["Billing & Financial Transactions"])

@router.get("/invoices", response_model=PaginatedResponse[InvoiceOut])
def list_invoices(
    payment_status: Optional[str] = Query(None, description="Filter by status (UNPAID, PARTIALLY_PAID, PAID)"),
    client_id: Optional[int] = Query(None, description="Filter by Client ID"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists sales invoices with customer accounts and payment balances."""
    query = db.query(SalesInvoice)

    if payment_status:
        query = query.filter(SalesInvoice.payment_status == payment_status)
    if client_id:
        query = query.filter(SalesInvoice.client_id == client_id)

    if params.search:
        term = f"%{params.search}%"
        query = query.filter(SalesInvoice.invoice_number.ilike(term))

    total = query.count()
    invoices = query.order_by(desc(SalesInvoice.issue_date)).offset(params.offset).limit(params.page_size).all()

    items = []
    for inv in invoices:
        items.append(InvoiceOut(
            invoice_id=inv.invoice_id,
            invoice_number=inv.invoice_number,
            client_id=inv.client_id,
            client_name=inv.client.company_name if inv.client else None,
            project_id=inv.project_id,
            project_name=inv.project.name if inv.project else None,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            subtotal=float(inv.subtotal),
            tax_amount=float(inv.tax_amount),
            discount_amount=float(inv.discount_amount),
            total_amount=float(inv.total_amount),
            paid_amount=float(inv.paid_amount),
            balance_due=float(inv.total_amount - inv.paid_amount),
            payment_status=inv.payment_status,
            created_at=inv.created_at,
            items=[]
        ))

    return PaginatedResponse.create(items, total, params)

@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice_detail(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Retrieves full invoice with line items."""
    inv = db.query(SalesInvoice).filter(SalesInvoice.invoice_id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    items_out = [
        InvoiceItemOut(
            invoice_item_id=it.invoice_item_id,
            item_id=it.item_id,
            description=it.description,
            quantity=it.quantity,
            unit_price=float(it.unit_price),
            line_total=float(it.quantity * it.unit_price)
        )
        for it in inv.items
    ]

    return InvoiceOut(
        invoice_id=inv.invoice_id,
        invoice_number=inv.invoice_number,
        client_id=inv.client_id,
        client_name=inv.client.company_name if inv.client else None,
        project_id=inv.project_id,
        project_name=inv.project.name if inv.project else None,
        issue_date=inv.issue_date,
        due_date=inv.due_date,
        subtotal=float(inv.subtotal),
        tax_amount=float(inv.tax_amount),
        discount_amount=float(inv.discount_amount),
        total_amount=float(inv.total_amount),
        paid_amount=float(inv.paid_amount),
        balance_due=float(inv.total_amount - inv.paid_amount),
        payment_status=inv.payment_status,
        created_at=inv.created_at,
        items=items_out
    )

@router.post("/invoices/{invoice_id}/payments", status_code=status.HTTP_201_CREATED)
def record_invoice_payment(
    invoice_id: int,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(["Super Admin", "Admin", "Finance Manager"]))
):
    """
    Executes PostgreSQL Stored Procedure sp_record_invoice_payment
    to apply payment and update balances atomically.
    """
    try:
        # Call the PostgreSQL stored procedure
        sql = text("""
            CALL sp_record_invoice_payment(
                :inv_id, :amt, :meth, :ref, :proc_by, :notes
            );
        """)
        db.execute(sql, {
            "inv_id": invoice_id,
            "amt": payload.amount,
            "meth": payload.payment_method,
            "ref": payload.transaction_reference or f"TXN-WEB-{date.today()}",
            "proc_by": current_user.employee_id,
            "notes": payload.notes or "Payment recorded via EROMS portal"
        })
        db.commit()
        return {"status": "success", "message": "Payment recorded and balance reconciled successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payments", response_model=PaginatedResponse[PaymentOut])
def list_payments(
    payment_type: Optional[str] = Query(None, description="CUSTOMER_RECEIPT, VENDOR_DISBURSEMENT, PAYROLL_DISBURSEMENT"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists financial transactions and payment disbursements."""
    query = db.query(FinancialPayment)

    if payment_type:
        query = query.filter(FinancialPayment.payment_type == payment_type)

    total = query.count()
    payments = query.order_by(desc(FinancialPayment.payment_date)).offset(params.offset).limit(params.page_size).all()

    items = [
        PaymentOut(
            payment_id=p.payment_id,
            payment_number=p.payment_number,
            payment_type=p.payment_type,
            invoice_id=p.invoice_id,
            amount=float(p.amount),
            payment_method=p.payment_method,
            transaction_reference=p.transaction_reference,
            payment_date=p.payment_date,
            notes=p.notes
        )
        for p in payments
    ]

    return PaginatedResponse.create(items, total, params)

@router.get("/aging-report")
def get_ar_aging_report(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """
    Queries the database view vw_accounts_receivable_aging
    for overdue debt aging buckets.
    """
    sql = text("""
        SELECT 
            aging_bracket,
            COUNT(invoice_id) AS invoice_count,
            SUM(balance_due) AS total_overdue_balance
        FROM vw_accounts_receivable_aging
        GROUP BY aging_bracket
        ORDER BY total_overdue_balance DESC;
    """)
    result = db.execute(sql).fetchall()
    return [
        {
            "aging_bracket": row.aging_bracket,
            "invoice_count": row.invoice_count,
            "total_overdue_balance": float(row.total_overdue_balance or 0.0)
        }
        for row in result
    ]
