"""
Inventory and Supply Chain API Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.core.pagination import PaginationParams, PaginatedResponse
from backend.app.models.inventory_purchasing import (
    InventoryItem, Warehouse, WarehouseStock, InventoryTransaction, ProductCategory
)
from backend.app.models.employee import Employee
from backend.app.schemas.inventory import (
    InventoryItemCreate, InventoryItemOut, WarehouseOut, InventoryTransactionOut
)

router = APIRouter(prefix="/inventory", tags=["Inventory & Warehouse Management"])

@router.get("/items", response_model=PaginatedResponse[InventoryItemOut])
def list_inventory_items(
    category_id: Optional[int] = Query(None, description="Filter by Category ID"),
    low_stock_only: bool = Query(False, description="Filter items at or below reorder level"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists inventory items with stock status calculations and category lookup."""
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)

    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    if low_stock_only:
        query = query.filter(InventoryItem.total_quantity_on_hand <= InventoryItem.reorder_level)

    if params.search:
        term = f"%{params.search}%"
        query = query.filter(
            or_(
                InventoryItem.name.ilike(term),
                InventoryItem.sku.ilike(term),
                InventoryItem.description.ilike(term)
            )
        )

    total = query.count()
    items = query.order_by(asc(InventoryItem.name)).offset(params.offset).limit(params.page_size).all()

    output_items = []
    for it in items:
        # Determine status
        if it.total_quantity_on_hand == 0:
            st = "OUT_OF_STOCK"
        elif it.total_quantity_on_hand <= it.reorder_level:
            st = "LOW_STOCK"
        else:
            st = "OPTIMAL"

        output_items.append(InventoryItemOut(
            item_id=it.item_id,
            sku=it.sku,
            name=it.name,
            description=it.description,
            category_id=it.category_id,
            category_name=it.category.name if it.category else None,
            unit_of_measure=it.unit_of_measure,
            cost_price=float(it.cost_price),
            selling_price=float(it.selling_price),
            total_quantity_on_hand=it.total_quantity_on_hand,
            reorder_level=it.reorder_level,
            reorder_quantity=it.reorder_quantity,
            stock_status=st,
            is_active=it.is_active,
            created_at=it.created_at
        ))

    return PaginatedResponse.create(output_items, total, params)

@router.get("/warehouses", response_model=List[WarehouseOut])
def list_warehouses(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists all regional warehouses."""
    whs = db.query(Warehouse).filter(Warehouse.is_active == True).all()
    return [
        WarehouseOut(
            warehouse_id=w.warehouse_id,
            warehouse_code=w.warehouse_code,
            name=w.name,
            location=w.location,
            capacity=w.capacity,
            manager_name=w.manager.full_name if w.manager else None,
            is_active=w.is_active
        )
        for w in whs
    ]

@router.get("/transactions", response_model=PaginatedResponse[InventoryTransactionOut])
def list_inventory_transactions(
    transaction_type: Optional[str] = Query(None, description="Filter by type (PURCHASE_RECEIPT, SALE_DISPATCH, etc.)"),
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Lists historical stock movement audit records."""
    query = db.query(InventoryTransaction)

    if transaction_type:
        query = query.filter(InventoryTransaction.transaction_type == transaction_type)

    total = query.count()
    txns = query.order_by(desc(InventoryTransaction.transaction_date)).offset(params.offset).limit(params.page_size).all()

    items = [
        InventoryTransactionOut(
            transaction_id=t.transaction_id,
            transaction_type=t.transaction_type,
            item_id=t.item_id,
            item_name=t.item.name if t.item else None,
            sku=t.item.sku if t.item else None,
            warehouse_name=t.warehouse.name if t.warehouse else None,
            quantity=t.quantity,
            unit_cost=float(t.unit_cost or 0.0),
            reference_type=t.reference_type,
            reference_id=t.reference_id,
            transaction_date=t.transaction_date
        )
        for t in txns
    ]

    return PaginatedResponse.create(items, total, params)
