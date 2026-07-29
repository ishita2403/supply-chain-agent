# src/supply_chain_agent/models/factory.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Factory(Base):
    __tablename__ = "factories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)

    product_links = relationship("FactoryProduct", back_populates="factory")


class FactoryProduct(Base):
    """Which factories can produce which products, and at what rate."""
    __tablename__ = "factory_products"

    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    production_rate_per_day = Column(Integer, nullable=False)

    factory = relationship("Factory", back_populates="product_links")
    product = relationship("Product", back_populates="factory_links")