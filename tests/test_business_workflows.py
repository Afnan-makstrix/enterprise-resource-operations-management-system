"""
End-to-End Enterprise Business Workflow Tests
Tests real multi-step operational workflows and business rules.
"""
import uuid
import pytest
from datetime import date, timedelta
from fastapi import status
from backend.app.models.employee import Department, Employee
from backend.app.models.finance import SalesInvoice, FinancialPayment
from backend.app.models.inventory_purchasing import Client

def test_employee_creation_and_listing_workflow(client, auth_headers, db_session):
    """
    Workflow 1:
    Admin creates new employee -> Assigned to department -> Appears in search & pagination.
    """
    dept = db_session.query(Department).first()
    uid = uuid.uuid4().hex[:6]
    new_email = f"workflow.{uid}@eroms-test.com"
    emp_num = f"EMP-WF-{uid}"

    payload = {
        "employee_number": emp_num,
        "first_name": "Workflow",
        "last_name": "Candidate",
        "email": new_email,
        "phone": "+1-555-0199",
        "job_title": "Full Stack Architect",
        "department_id": dept.department_id,
        "role_id": 1,
        "salary": 95000.00,
        "employment_type": "FULL_TIME",
        "status": "ACTIVE"
    }

    create_resp = client.post("/api/v1/employees/", json=payload, headers=auth_headers)
    assert create_resp.status_code == status.HTTP_201_CREATED
    created_data = create_resp.json()
    emp_id = created_data["employee_id"]

    # Verify search finds the new employee
    search_resp = client.get(f"/api/v1/employees/?search={uid}", headers=auth_headers)
    assert search_resp.status_code == status.HTTP_200_OK
    search_data = search_resp.json()
    assert search_data["total"] >= 1
    assert any(e["employee_id"] == emp_id for e in search_data["items"])

def test_invoice_creation_and_payment_status_workflow(client, auth_headers, db_session):
    """
    Workflow 2:
    Invoice generated ($10,000) -> Status is UNPAID
    Payment recorded ($4,000) -> Status becomes PARTIALLY_PAID
    Payment recorded ($6,000) -> Status becomes PAID, balance_due becomes 0.
    """
    uid = uuid.uuid4().hex[:6]
    test_client = Client(
        client_code=f"CLI-TEST-{uid}",
        company_name=f"Apex Global Technologies {uid}",
        contact_person="Sarah Connor",
        email=f"billing.{uid}@apex-tech.com",
        credit_limit=100000.00
    )
    db_session.add(test_client)
    db_session.commit()
    db_session.refresh(test_client)

    # 1. Create Sales Invoice
    inv = SalesInvoice(
        invoice_number=f"INV-WF-{uid}",
        client_id=test_client.client_id,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        subtotal=10000.00,
        tax_rate=0.00,
        tax_amount=0.00,
        discount_amount=0.00,
        total_amount=10000.00,
        paid_amount=0.00,
        payment_status="UNPAID"
    )
    db_session.add(inv)
    db_session.commit()
    db_session.refresh(inv)

    assert inv.payment_status == "UNPAID"
    assert float(inv.total_amount) == 10000.00

    # 2. Apply Partial Payment via Stored Procedure API
    pay_payload1 = {
        "amount": 4000.00,
        "payment_method": "BANK_TRANSFER",
        "transaction_reference": f"TXN-WF1-{uid}",
        "notes": "First milestone payment"
    }
    pay_resp1 = client.post(
        f"/api/v1/billing/invoices/{inv.invoice_id}/payments",
        json=pay_payload1,
        headers=auth_headers
    )
    assert pay_resp1.status_code == status.HTTP_201_CREATED

    # Verify status changed to PARTIALLY_PAID
    inv_check1 = client.get(f"/api/v1/billing/invoices/{inv.invoice_id}", headers=auth_headers).json()
    assert inv_check1["payment_status"] == "PARTIALLY_PAID"
    assert inv_check1["paid_amount"] == 4000.00
    assert inv_check1["balance_due"] == 6000.00

    # 3. Apply Final Remaining Payment ($6,000)
    pay_payload2 = {
        "amount": 6000.00,
        "payment_method": "BANK_TRANSFER",
        "transaction_reference": f"TXN-WF2-{uid}",
        "notes": "Final settlement"
    }
    pay_resp2 = client.post(
        f"/api/v1/billing/invoices/{inv.invoice_id}/payments",
        json=pay_payload2,
        headers=auth_headers
    )
    assert pay_resp2.status_code == status.HTTP_201_CREATED

    # Verify status changed to PAID and balance is 0
    inv_check2 = client.get(f"/api/v1/billing/invoices/{inv.invoice_id}", headers=auth_headers).json()
    assert inv_check2["payment_status"] == "PAID"
    assert inv_check2["paid_amount"] == 10000.00
    assert inv_check2["balance_due"] == 0.00
