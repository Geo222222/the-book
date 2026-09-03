from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from .domain import EvidenceClass, EvidenceEnvelope, PrivacyClass
from .ledger import BigBook, BookReceipt


class WireEnvelopeError(ValueError):
    pass


def _timestamp(value: Any, field: str, *, nullable: bool = False) -> datetime | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value:
        raise WireEnvelopeError(f"{field} must be an ISO-8601 timestamp string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WireEnvelopeError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise WireEnvelopeError(f"{field} must be timezone-aware")
    return parsed


def evidence_envelope_from_wire(value: Mapping[str, Any]) -> EvidenceEnvelope:
    try:
        schema_version = str(value["schema_version"])
        occurred_at = _timestamp(value["occurred_at"], "occurred_at")
        assert occurred_at is not None
        return EvidenceEnvelope(
            schema_version=schema_version,
            receipt_id=str(value["receipt_id"]),
            producer=str(value["producer"]),
            producer_key_id=str(value["producer_key_id"]),
            event_type=str(value["event_type"]),
            evidence_class=EvidenceClass(str(value["evidence_class"])),
            subject_id=str(value["subject_id"]),
            occurred_at=occurred_at,
            payload_digest=str(value["payload_digest"]),
            payload_ref=value.get("payload_ref"),
            correlation_id=value.get("correlation_id"),
            causation_receipt_id=value.get("causation_receipt_id"),
            signature=str(value["signature"]),
            privacy_class=PrivacyClass(str(value.get("privacy_class", "CONFIDENTIAL_EVIDENCE"))),
            visibility_scope=tuple(str(item) for item in value.get("visibility_scope", ("INSTITUTION",))),
            evidence_receipt_ids=tuple(str(item) for item in value.get("evidence_receipt_ids", ())),
            source_event_at=_timestamp(value.get("source_event_at"), "source_event_at", nullable=True),
            known_at=_timestamp(value.get("known_at"), "known_at", nullable=True),
            produced_at=_timestamp(value.get("produced_at"), "produced_at", nullable=True),
            valid_from=_timestamp(value.get("valid_from"), "valid_from", nullable=True),
            valid_until=_timestamp(value.get("valid_until"), "valid_until", nullable=True),
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, WireEnvelopeError):
            raise
        raise WireEnvelopeError(f"invalid evidence envelope: {exc}") from exc


class BookIngestService:
    """Wire boundary used by producer outboxes.

    A production deployment can put authentication, transport encryption, rate
    limits, and durable storage around this boundary without changing the signed
    evidence contract.
    """

    def __init__(self, book: BigBook) -> None:
        self.book = book

    def append_idempotent(self, *, envelope: Mapping[str, Any], payload: bytes) -> dict[str, object]:
        parsed = evidence_envelope_from_wire(envelope)
        receipt: BookReceipt = self.book.append_idempotent(parsed, payload=payload)
        return receipt.wire()
