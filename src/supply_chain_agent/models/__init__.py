# src/supply_chain_agent/models/__init__.py
from .base import Base, engine, SessionLocal
from .supplier import Supplier, SupplierComponent
from .component import Component
from .product import Product, BOMItem
from .factory import Factory, FactoryProduct
from .customer import Customer
from .purchase_order import PurchaseOrder
from .inventory import Inventory

__all__ = [
    "Base", "engine", "SessionLocal",
    "Supplier", "SupplierComponent", "Component",
    "Product", "BOMItem", "Factory", "FactoryProduct",
    "Customer", "PurchaseOrder", "Inventory",
]

# add to src/supply_chain_agent/models/__init__.py
from .event import Event
__all__.append("Event")