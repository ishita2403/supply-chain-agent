# src/supply_chain_agent/models/purchase_order.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="open")  # open, delayed, fulfilled, cancelled

    customer = relationship("Customer", back_populates="purchase_orders")
    product = relationship("Product", back_populates="purchase_orders")# src/supply_chain_agent/models/purchase_order.py

