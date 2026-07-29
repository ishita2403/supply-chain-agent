# tests/test_models.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal, Product, Supplier


def test_product_has_bom_items():
    session = SessionLocal()
    product = session.query(Product).filter_by(sku="SSD-1000").first()
    assert product is not None
    assert len(product.bom_items) == 2
    session.close()


def test_component_has_multiple_suppliers():
    session = SessionLocal()
    # find the chip via any BOM item's component
    product = session.query(Product).filter_by(sku="SSD-1000").first()
    chip_bom = [b for b in product.bom_items if b.component.name == "Microcontroller Chip"][0]
    assert len(chip_bom.component.suppliers) == 2  # Acme + Backup
    session.close()