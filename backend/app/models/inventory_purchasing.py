"""
Client, Supplier, Inventory & Purchasing Models
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, index=True)
    client_code = Column(String(30), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    billing_address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    country = Column(String(50), default="United States")
    credit_limit = Column(Numeric(15, 2), default=50000.00, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String(30), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    tax_identification_number = Column(String(50), unique=True, nullable=True)
    payment_terms = Column(String(50), default="NET_30")
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    country = Column(String(50), default="United States")
    rating = Column(Numeric(3, 2), default=5.00)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class ProductCategory(Base):
    __tablename__ = "product_categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_category_id = Column(Integer, ForeignKey("product_categories.category_id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    parent = relationship("ProductCategory", remote_side=[category_id])

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    item_id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.category_id", ondelete="RESTRICT"), nullable=False, index=True)
    unit_of_measure = Column(String(20), default="UNIT")
    cost_price = Column(Numeric(12, 2), nullable=False)
    selling_price = Column(Numeric(12, 2), nullable=False)
    total_quantity_on_hand = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)
    reorder_quantity = Column(Integer, default=50, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    category = relationship("ProductCategory")
    stocks = relationship("WarehouseStock", back_populates="item", cascade="all, delete-orphan")

class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, index=True)
    warehouse_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False)
    capacity = Column(Integer, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    manager = relationship("Employee")
    stocks = relationship("WarehouseStock", back_populates="warehouse", cascade="all, delete-orphan")

class WarehouseStock(Base):
    __tablename__ = "warehouse_stocks"

    stock_id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id", ondelete="RESTRICT"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.item_id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, default=0, nullable=False)
    bin_location = Column(String(50), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    warehouse = relationship("Warehouse", back_populates="stocks")
    item = relationship("InventoryItem", back_populates="stocks")

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    transaction_id = Column(BigInteger, primary_key=True, index=True)
    transaction_type = Column(String(20), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.item_id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id", ondelete="RESTRICT"), nullable=False, index=True)
    destination_warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(12, 2), default=0.00)
    reference_type = Column(String(50), nullable=False)
    reference_id = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    transaction_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    item = relationship("InventoryItem")
    warehouse = relationship("Warehouse", foreign_keys=[warehouse_id])

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(30), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id", ondelete="RESTRICT"), nullable=False, index=True)
    requested_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False)
    order_date = Column(Date, default=date.today, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    subtotal = Column(Numeric(15, 2), default=0.00, nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    shipping_fee = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    status = Column(String(20), default="DRAFT", nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    supplier = relationship("Supplier")
    warehouse = relationship("Warehouse")
    requester = relationship("Employee", foreign_keys=[requested_by])
    approver = relationship("Employee", foreign_keys=[approved_by])
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    po_item_id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.po_id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.item_id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0, nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(15, 2), server_default=FetchedValue())

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("InventoryItem")
