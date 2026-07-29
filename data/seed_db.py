# data/seed_db.py
"""
Creates all tables and inserts a small, realistic sample dataset.
Run this once (or anytime you want to reset your local DB).
"""

import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import (
    Base, engine, SessionLocal,
    Supplier, SupplierComponent, Component,
    Product, BOMItem, Factory, FactoryProduct,
    Customer, PurchaseOrder, Inventory,
)


def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # -------------------------
    # Suppliers
    # -------------------------
    supplier_a = Supplier(
        name="Acme Electronics",
        region="Taiwan",
        reliability_score=0.95
    )

    supplier_b = Supplier(
        name="Backup Components Co",
        region="Vietnam",
        reliability_score=0.80
    )

    session.add_all([supplier_a, supplier_b])
    session.flush()

    # -------------------------
    # Components
    # -------------------------
    chip = Component(
        name="Microcontroller Chip",
        category="electronics"
    )

    battery = Component(
        name="Li-ion Battery",
        category="electronics"
    )

    session.add_all([chip, battery])
    session.flush()

    # -------------------------
    # Supplier ↔ Component Links
    # -------------------------
    session.add_all([
        SupplierComponent(
            supplier_id=supplier_a.id,
            component_id=chip.id,
            lead_time_days=7,
            unit_cost=4.5
        ),
        SupplierComponent(
            supplier_id=supplier_b.id,
            component_id=chip.id,
            lead_time_days=15,
            unit_cost=3.9
        ),
        SupplierComponent(
            supplier_id=supplier_a.id,
            component_id=battery.id,
            lead_time_days=10,
            unit_cost=8.0
        ),
    ])

    # -------------------------
    # Product
    # -------------------------
    smart_device = Product(
        name="Smart Sensor Device",
        sku="SSD-1000",
        unit_price=45.0
    )

    session.add(smart_device)
    session.flush()

    # -------------------------
    # Bill of Materials (BOM)
    # -------------------------
    session.add_all([
        BOMItem(
            product_id=smart_device.id,
            component_id=chip.id,
            quantity_required=1
        ),
        BOMItem(
            product_id=smart_device.id,
            component_id=battery.id,
            quantity_required=1
        ),
    ])

    # -------------------------
    # Factory
    # -------------------------
    factory_1 = Factory(
        name="Pune Assembly Plant",
        location="Pune, India"
    )

    session.add(factory_1)
    session.flush()

    session.add(
        FactoryProduct(
            factory_id=factory_1.id,
            product_id=smart_device.id,
            production_rate_per_day=200
        )
    )

    # -------------------------
    # Customer
    # -------------------------
    customer = Customer(
        name="RetailChain Corp",
        priority_tier=1
    )

    session.add(customer)
    session.flush()

    # -------------------------
    # Purchase Order
    # -------------------------
    session.add(
        PurchaseOrder(
            customer_id=customer.id,
            product_id=smart_device.id,
            quantity=5000,
            due_date=date(2026, 9, 1),
            status="open"
        )
    )

    # -------------------------
    # Inventory
    # -------------------------
    session.add(
        Inventory(
            item_type="component",
            item_id=chip.id,
            factory_id=factory_1.id,
            quantity_on_hand=1200
        )
    )

    session.commit()
    session.close()

    print("Database seeded successfully.")


if __name__ == "__main__":
    seed()