from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EvidenceClass(str, Enum):
    CONSTITUTIONAL = "CONSTITUTIONAL"
    ECONOMIC = "ECONOMIC"
    ANALYTICAL = "ANALYTICAL"


class PrivacyClass(str, Enum):
    PUBLIC_PROOF = "PUBLIC_PROOF"
    PARTICIPANT_PROOF = "PARTICIPANT_PROOF"
    CONFIDENTIAL_EVIDENCE = "CONFIDENTIAL_EVIDENCE"
    SECRET_REGULATED = "SECRET_REGULATED"


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


def _require_digest(value: str, field: str = "payload_digest") -> None:
    if len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc


def _require_visibility(privacy_class: PrivacyClass, visibility_scope: tuple[str, ...]) -> None:
    if not visibility_scope or any(not item for item in visibility_scope):
        raise ValueError("visibility_scope must contain at least one non-empty scope")
    if len(set(visibility_scope)) != len(visibility_scope):
        raise ValueError("visibility_scope must not contain duplicates")
    if privacy_class is PrivacyClass.PUBLIC_PROOF:
        if "PUBLIC" not in visibility_scope:
            raise ValueError("PUBLIC_PROOF must include PUBLIC visibility")
    elif "PUBLIC" in visibility_scope:
        raise ValueError("non-public evidence cannot include PUBLIC visibility")


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
    privacy_class: PrivacyClass = PrivacyClass.CONFIDENTIAL_EVIDENCE
    visibility_scope: tuple[str, ...] = ("INSTITUTION",)

    def __post_init__(self) -> None:
        for name in ("schema_version", "receipt_id", "producer", "producer_key_id", "event_type", "subject_id"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        _require_aware(self.occurred_at, "occurred_at")
        _require_digest(self.payload_digest)
        _require_visibility(self.privacy_class, self.visibility_scope)
        if self.privacy_class is PrivacyClass.SECRET_REGULATED and self.payload_ref is not None:
            if not self.payload_ref.startswith(("vault://", "secure://", "kms://")):
                raise ValueError("SECRET_REGULATED evidence must reference restricted storage")
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
            "privacy_class": self.privacy_class.value,
            "visibility_scope": list(self.visibility_scope),
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
