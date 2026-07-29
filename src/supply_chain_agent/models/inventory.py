# src/supply_chain_agent/models/inventory.py

from sqlalchemy import Column, Integer, String
from .base import Base


class Inventory(Base):
    """
    Tracks on-hand stock. item_type distinguishes whether item_id
    refers to a Component or a Product, since both can sit in inventory.
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    item_type = Column(String, nullable=False)   # "component" or "product"
    item_id = Column(Integer, nullable=False)
    factory_id = Column(Integer, nullable=False)
    quantity_on_hand = Column(Integer, nullable=False, default=0)