# src/supply_chain_agent/models/product.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy import Float


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)

    bom_items = relationship("BOMItem", back_populates="product")
    factory_links = relationship("FactoryProduct", back_populates="product")
    purchase_orders = relationship("PurchaseOrder", back_populates="product")
    unit_price = Column(Float, nullable=False, default=0.0)


class BOMItem(Base):
    """
    Bill of Materials line item: 'Product X needs Y units of Component Z.'
    This is the single most important table for dependency-graph
    construction in Phase 4 — it's the Product<->Component edge.
    """
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    quantity_required = Column(Integer, nullable=False, default=1)

    product = relationship("Product", back_populates="bom_items")
    component = relationship("Component", back_populates="bom_items")