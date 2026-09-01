from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EvidenceClass(str, Enum):
    CONSTITUTIONAL = "CONSTITUTIONAL"
    ECONOMIC = "ECONOMIC"
    ANALYTICAL = "ANALYTICAL"


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


def _require_digest(value: str) -> None:
    if len(value) != 64:
        raise ValueError("payload_digest must be a 64-character SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("payload_digest must be hexadecimal") from exc


@dataclass(frozen=True, slots=True)
class EvidenceEnvelope:
    schema_version: str
    receipt_id: str
    producer: str
    producer_key_id: str
    event_type: str
    evidence_class: EvidenceClass
    subject_id: str
    occurred_at: datetime
    payload_digest: str
    payload_ref: str | None
    correlation_id: str | None
    causation_receipt_id: str | None
    signature: str

    def __post_init__(self) -> None:
        for name in ("schema_version", "receipt_id", "producer", "producer_key_id", "event_type", "subject_id"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        _require_aware(self.occurred_at, "occurred_at")
        _require_digest(self.payload_digest)
        if not self.signature:
            raise ValueError("signature is required")

    def signing_body(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "receipt_id": self.receipt_id,
            "producer": self.producer,
            "producer_key_id": self.producer_key_id,
            "event_type": self.event_type,
            "evidence_class": self.evidence_class.value,
            "subject_id": self.subject_id,
            "occurred_at": self.occurred_at.isoformat(),
            "payload_digest": self.payload_digest,
            "payload_ref": self.payload_ref,
            "correlation_id": self.correlation_id,
            "causation_receipt_id": self.causation_receipt_id,
        }

    def wire(self) -> dict[str, object]:
        return {**self.signing_body(), "signature": self.signature}


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    sequence: int
    envelope: EvidenceEnvelope
    recorded_at: datetime
    previous_hash: str
    entry_hash: str

    def chain_body(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "envelope": self.envelope.wire(),
            "recorded_at": self.recorded_at.isoformat(),
            "previous_hash": self.previous_hash,
        }
