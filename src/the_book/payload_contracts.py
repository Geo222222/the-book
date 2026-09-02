from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Mapping

from .domain import EvidenceEnvelope


class DomainPayloadError(ValueError):
    pass


BENJAMIN_ACTIONS = {"ENTER", "HOLD", "REDUCE", "EXIT", "NO_TRADE"}
BENJAMIN_SIDES = {"BUY", "SELL", "NONE"}
SIZE_UNITS = {"BASE", "QUOTE", "PERCENT_EQUITY", "RISK_FRACTION"}
ZLJ_QUALIFICATION_STATES = {"QUALIFIED", "DEGRADED", "BLOCKED"}


def _object(payload: bytes) -> Mapping[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DomainPayloadError("domain payload must be UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise DomainPayloadError("domain payload must be a JSON object")
    return value


def _require_string(value: Mapping[str, Any], field: str, *, nullable: bool = False) -> str | None:
    item = value.get(field)
    if item is None and nullable:
        return None
    if not isinstance(item, str) or not item:
        raise DomainPayloadError(f"{field} must be a non-empty string")
    return item


def _require_string_list(value: Mapping[str, Any], field: str) -> tuple[str, ...]:
    item = value.get(field)
    if not isinstance(item, list) or any(not isinstance(entry, str) or not entry for entry in item):
        raise DomainPayloadError(f"{field} must be an array of non-empty strings")
    if len(set(item)) != len(item):
        raise DomainPayloadError(f"{field} must not contain duplicates")
    return tuple(item)


def _require_probability(value: Mapping[str, Any], field: str, *, nullable: bool = False) -> float | None:
    item = value.get(field)
    if item is None and nullable:
        return None
    if isinstance(item, bool) or not isinstance(item, (int, float)):
        raise DomainPayloadError(f"{field} must be numeric")
    result = float(item)
    if result < 0.0 or result > 1.0:
        raise DomainPayloadError(f"{field} must be between 0 and 1")
    return result


def _require_number(value: Mapping[str, Any], field: str, *, nullable: bool = False) -> float | None:
    item = value.get(field)
    if item is None and nullable:
        return None
    if isinstance(item, bool) or not isinstance(item, (int, float)):
        raise DomainPayloadError(f"{field} must be numeric")
    return float(item)


def _require_positive_int(value: Mapping[str, Any], field: str) -> int:
    item = value.get(field)
    if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
        raise DomainPayloadError(f"{field} must be a positive integer")
    return item


def _parse_timestamp(value: Mapping[str, Any], field: str, *, nullable: bool = False) -> datetime | None:
    item = value.get(field)
    if item is None and nullable:
        return None
    if not isinstance(item, str) or not item:
        raise DomainPayloadError(f"{field} must be an ISO-8601 timestamp string")
    try:
        parsed = datetime.fromisoformat(item.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DomainPayloadError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DomainPayloadError(f"{field} must be timezone-aware")
    return parsed


def validate_zlj_intelligence(payload: bytes) -> Mapping[str, Any]:
    value = _object(payload)
    if value.get("schema_version") != "1.0":
        raise DomainPayloadError("ZLJ intelligence schema_version must be 1.0")
    _require_string(value, "intelligence_id")
    _require_string(value, "instrument")
    _require_positive_int(value, "horizon_ms")
    _require_string(value, "proposition")
    _require_probability(value, "probability", nullable=True)
    _require_number(value, "expected_move_bps", nullable=True)
    _require_string(value, "market_state", nullable=True)
    _require_string(value, "regime", nullable=True)
    _require_string_list(value, "model_ids")
    qualification = _require_string(value, "qualification_state")
    if qualification not in ZLJ_QUALIFICATION_STATES:
        raise DomainPayloadError("qualification_state is invalid")
    _require_string_list(value, "competence_refs")
    _require_string_list(value, "evidence_refs")
    _require_string(value, "code_version", nullable=True)
    _require_string(value, "feature_version", nullable=True)
    _require_string_list(value, "invalidation_conditions")
    known_at = _parse_timestamp(value, "known_at")
    valid_until = _parse_timestamp(value, "valid_until", nullable=True)
    if valid_until is not None and known_at is not None and valid_until < known_at:
        raise DomainPayloadError("valid_until cannot be before known_at")
    return value


def validate_benjamin_decision(payload: bytes) -> Mapping[str, Any]:
    value = _object(payload)
    if value.get("schema_version") != "1.0":
        raise DomainPayloadError("Benjamin decision schema_version must be 1.0")
    _require_string(value, "decision_id")
    _require_string(value, "instrument")
    action = _require_string(value, "action")
    if action not in BENJAMIN_ACTIONS:
        raise DomainPayloadError("action is invalid")
    side = _require_string(value, "side")
    if side not in BENJAMIN_SIDES:
        raise DomainPayloadError("side is invalid")
    _require_positive_int(value, "horizon_ms")
    size = value.get("intended_size")
    if not isinstance(size, dict):
        raise DomainPayloadError("intended_size must be an object")
    unit = size.get("unit")
    amount = size.get("value")
    if unit not in SIZE_UNITS:
        raise DomainPayloadError("intended_size.unit is invalid")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or float(amount) < 0:
        raise DomainPayloadError("intended_size.value must be non-negative")
    if action == "NO_TRADE" and float(amount) != 0.0:
        raise DomainPayloadError("NO_TRADE intended_size.value must be zero")
    _require_number(value, "expected_edge_before_costs_bps", nullable=True)
    _require_number(value, "expected_edge_after_costs_bps", nullable=True)
    _require_probability(value, "confidence")
    _require_string(value, "thesis_ref", nullable=True)
    _require_string(value, "invalidation_ref", nullable=True)
    _require_string(value, "capital_state_ref")
    _require_string(value, "position_state_ref")
    _require_string(value, "reasoner_version")
    _require_string_list(value, "evidence_receipt_ids")
    _parse_timestamp(value, "expires_at")
    return value


def validate_target_payload(envelope: EvidenceEnvelope, payload: bytes) -> Mapping[str, Any] | None:
    """Validate target v2 payloads without deciding their economic truth."""
    if envelope.schema_version != "2.0":
        return None
    if envelope.event_type in {"ZLJ.INTELLIGENCE", "ZLJ.PREDICTION"}:
        value = validate_zlj_intelligence(payload)
        if value["intelligence_id"] != envelope.subject_id:
            raise DomainPayloadError("ZLJ intelligence_id must equal envelope subject_id")
        if value["known_at"] != envelope.known_at.isoformat():
            raise DomainPayloadError("ZLJ payload known_at must equal envelope known_at")
        return value
    if envelope.event_type == "BENJAMIN.DECISION":
        value = validate_benjamin_decision(payload)
        if value["decision_id"] != envelope.subject_id:
            raise DomainPayloadError("Benjamin decision_id must equal envelope subject_id")
        lineage_ids = set(envelope.evidence_receipt_ids)
        if envelope.causation_receipt_id is not None:
            lineage_ids.add(envelope.causation_receipt_id)
        if set(value["evidence_receipt_ids"]) != lineage_ids:
            raise DomainPayloadError("Benjamin decision evidence_receipt_ids must equal Book lineage dependencies")
        return value
    return None
