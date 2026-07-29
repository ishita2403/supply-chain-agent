# src/supply_chain_agent/models/component.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)  # e.g. "electronics", "mechanical"

    suppliers = relationship("SupplierComponent", back_populates="component")
    bom_items = relationship("BOMItem", back_populates="component")