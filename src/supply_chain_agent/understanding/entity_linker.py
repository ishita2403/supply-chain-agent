# src/supply_chain_agent/understanding/entity_linker.py

from dataclasses import dataclass
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from ..models import Supplier, Component, Factory

FUZZY_MATCH_THRESHOLD = 75  # 0-100 scale; below this, we don't trust the match


@dataclass
class EntityLinkResult:
    supplier_id: int | None
    supplier_match_score: float
    component_id: int | None
    component_match_score: float
    factory_id: int | None
    factory_match_score: float


def _best_fuzzy_match(text: str, candidates: dict[str, int]) -> tuple[int | None, float]:
    """
    candidates: {name: id} for every known entity of one type (e.g. all suppliers).
    Uses token_set_ratio, which is robust to word order and partial overlap —
    e.g. "Acme Electronics" scores highly against "...Acme Electronics reports...".
    """
    if not candidates:
        return None, 0.0

    match = process.extractOne(
        text, candidates.keys(), scorer=fuzz.token_set_ratio
    )
    if match is None:
        return None, 0.0

    matched_name, score, _ = match
    if score < FUZZY_MATCH_THRESHOLD:
        return None, score
    return candidates[matched_name], score


def link_entities(session: Session, raw_text: str) -> EntityLinkResult:
    suppliers = {s.name: s.id for s in session.query(Supplier).all()}
    components = {c.name: c.id for c in session.query(Component).all()}
    factories = {f.name: f.id for f in session.query(Factory).all()}

    supplier_id, supplier_score = _best_fuzzy_match(raw_text, suppliers)
    component_id, component_score = _best_fuzzy_match(raw_text, components)
    factory_id, factory_score = _best_fuzzy_match(raw_text, factories)

    return EntityLinkResult(
        supplier_id=supplier_id, supplier_match_score=supplier_score,
        component_id=component_id, component_match_score=component_score,
        factory_id=factory_id, factory_match_score=factory_score,
    )