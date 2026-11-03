"""
Inventory, Warehouse & Supply Chain Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class InventoryItemBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: int
    unit_of_measure: str = "UNIT"
    cost_price: float = Field(..., ge=0)
    selling_price: float = Field(..., ge=0)
    total_quantity_on_hand: int = Field(0, ge=0)
    reorder_level: int = Field(10, ge=0)
    reorder_quantity: int = Field(50, gt=0)
    is_active: bool = True

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemOut(InventoryItemBase):
    item_id: int
    category_name: Optional[str] = None
    stock_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class WarehouseOut(BaseModel):
    warehouse_id: int
    warehouse_code: str
    name: str
    location: str
    capacity: int
    manager_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class InventoryTransactionOut(BaseModel):
    transaction_id: int
    transaction_type: str
    item_id: int
    item_name: Optional[str] = None
    sku: Optional[str] = None
    warehouse_name: Optional[str] = None
    quantity: int
    unit_cost: float
    reference_type: str
    reference_id: Optional[str] = None
    transaction_date: datetime

    class Config:
        from_attributes = True
