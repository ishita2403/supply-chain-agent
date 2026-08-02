# tests/scenarios/scenario_seed_data.py

from datetime import date
from supply_chain_agent.models import (
    Supplier, SupplierComponent, Component, Product, BOMItem,
    Factory, FactoryProduct, Customer, PurchaseOrder, Inventory,
)


def build_rich_seed(session):
    """
    A deliberately richer seed dataset than Phase 1's original, specifically
    designed to make EVERY recovery strategy's feasibility precondition
    satisfiable at least once (Section 2.2) -- most notably split_production,
    which the original single-factory seed data could never trigger.
    """
    # --- Suppliers: TWO per component, enabling alternate_supplier ---
    acme = Supplier(name="Acme Electronics", region="Taiwan", reliability_score=0.95)
    backup = Supplier(name="Backup Components Co", region="Vietnam", reliability_score=0.80)
    sole_source = Supplier(name="Sole Source Casings Ltd", region="Germany", reliability_score=0.60)
    session.add_all([acme, backup, sole_source])
    session.flush()

    chip = Component(name="Microcontroller Chip", category="electronics")
    battery = Component(name="Li-ion Battery", category="electronics")
    casing = Component(name="Custom Casing", category="mechanical")  # deliberately single-sourced
    session.add_all([chip, battery, casing])
    session.flush()

    session.add_all([
        SupplierComponent(supplier_id=acme.id, component_id=chip.id, lead_time_days=7, unit_cost=4.5),
        SupplierComponent(supplier_id=backup.id, component_id=chip.id, lead_time_days=15, unit_cost=3.9),
        SupplierComponent(supplier_id=acme.id, component_id=battery.id, lead_time_days=10, unit_cost=8.0),
        # casing has ONLY one supplier -- deliberately, to test the "no
        # alternate available" feasibility-gating path (Scenario 3).
        SupplierComponent(supplier_id=sole_source.id, component_id=casing.id, lead_time_days=20, unit_cost=12.0),
    ])

    # --- Products ---
    smart_device = Product(name="Smart Sensor Device", sku="SSD-1000", unit_price=45.0)
    rugged_device = Product(name="Rugged Field Sensor", sku="RFS-2000", unit_price=120.0)
    session.add_all([smart_device, rugged_device])
    session.flush()

    session.add_all([
        BOMItem(product_id=smart_device.id, component_id=chip.id, quantity_required=1),
        BOMItem(product_id=smart_device.id, component_id=battery.id, quantity_required=1),
        BOMItem(product_id=rugged_device.id, component_id=chip.id, quantity_required=1),
        BOMItem(product_id=rugged_device.id, component_id=casing.id, quantity_required=1),
    ])

    # --- Factories: TWO make the smart_device, enabling split_production ---
    pune = Factory(name="Pune Assembly Plant", location="Pune, India")
    chennai = Factory(name="Chennai Assembly Plant", location="Chennai, India")
    session.add_all([pune, chennai])
    session.flush()

    session.add_all([
        FactoryProduct(factory_id=pune.id, product_id=smart_device.id, production_rate_per_day=200),
        FactoryProduct(factory_id=chennai.id, product_id=smart_device.id, production_rate_per_day=150),
        FactoryProduct(factory_id=pune.id, product_id=rugged_device.id, production_rate_per_day=50),
        # rugged_device is deliberately single-factory -- no split_production
        # option should ever appear for it.
    ])

    # --- Customers across multiple priority tiers, enabling delay_low_priority ---
    key_account = Customer(name="RetailChain Corp", priority_tier=1)
    mid_tier = Customer(name="RegionalDistributor Inc", priority_tier=2)
    low_tier = Customer(name="SmallShop LLC", priority_tier=3)
    session.add_all([key_account, mid_tier, low_tier])
    session.flush()

    # --- Purchase Orders: mix of sizes, including one deliberately LARGE
    #     order that will push cost above the guardrail ceiling ---
    session.add_all([
        PurchaseOrder(customer_id=key_account.id, product_id=smart_device.id,
                       quantity=5000, due_date=date(2026, 9, 1), status="open"),
        PurchaseOrder(customer_id=mid_tier.id, product_id=smart_device.id,
                       quantity=1200, due_date=date(2026, 9, 5), status="open"),
        PurchaseOrder(customer_id=low_tier.id, product_id=smart_device.id,
                       quantity=300, due_date=date(2026, 9, 10), status="open"),
        # A deliberately huge order -- will push alternate_supplier/air_freight
        # cost well past the $25,000 guardrail ceiling from Phase 9.
        PurchaseOrder(customer_id=key_account.id, product_id=rugged_device.id,
                       quantity=8000, due_date=date(2026, 9, 3), status="open"),
    ])

    # --- Some finished-goods inventory, enabling allocate_inventory ---
    session.add(Inventory(item_type="product", item_id=smart_device.id,
                           factory_id=pune.id, quantity_on_hand=800))

    session.commit()