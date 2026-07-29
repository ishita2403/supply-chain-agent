# src/supply_chain_agent/models/supplier.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String)
    # A score from 0-1 representing historical reliability.
    # Used later by the Recovery Plan Generator and Scoring Engine.
    reliability_score = Column(Float, default=0.9)

    # "components" gives us supplier.components -> list of SupplierComponent
    # rows, letting us navigate from a Supplier to what it supplies.
    components = relationship("SupplierComponent", back_populates="supplier")


class SupplierComponent(Base):
    """
    Association table: which suppliers can provide which components,
    and at what cost/lead time. This is what enables 'alternate supplier'
    recovery plans later.
    """
    __tablename__ = "supplier_components"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)

    supplier = relationship("Supplier", back_populates="components")
    component = relationship("Component", back_populates="suppliers")