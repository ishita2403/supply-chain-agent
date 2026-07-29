# src/supply_chain_agent/models/customer.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # 1 = highest priority. Used in Phase 6 for "delay low priority customers".
    priority_tier = Column(Integer, default=3)

    purchase_orders = relationship("PurchaseOrder", back_populates="customer")