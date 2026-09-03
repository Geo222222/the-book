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


def _require_optional_aware(value: datetime | None, field: str) -> None:
    if value is not None:
        _require_aware(value, field)


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


def _require_dependencies(
    *,
    receipt_id: str,
    causation_receipt_id: str | None,
    evidence_receipt_ids: tuple[str, ...],
) -> None:
    if any(not item for item in evidence_receipt_ids):
        raise ValueError("evidence_receipt_ids must contain only non-empty receipt ids")
    if len(set(evidence_receipt_ids)) != len(evidence_receipt_ids):
        raise ValueError("evidence_receipt_ids must not contain duplicates")
    if receipt_id in evidence_receipt_ids:
        raise ValueError("an evidence envelope cannot depend on itself")
    if causation_receipt_id == receipt_id:
        raise ValueError("an evidence envelope cannot cause itself")
    if causation_receipt_id is not None and causation_receipt_id in evidence_receipt_ids:
        raise ValueError("primary causation must not be duplicated in evidence_receipt_ids")


def _require_v2_timing(
    *,
    occurred_at: datetime,
    source_event_at: datetime | None,
    known_at: datetime | None,
    produced_at: datetime | None,
    valid_from: datetime | None,
    valid_until: datetime | None,
) -> None:
    for value, field in (
        (source_event_at, "source_event_at"),
        (known_at, "known_at"),
        (produced_at, "produced_at"),
        (valid_from, "valid_from"),
        (valid_until, "valid_until"),
    ):
        _require_optional_aware(value, field)
    if known_at is None or produced_at is None:
        raise ValueError("v2 envelopes require known_at and produced_at")
    if occurred_at > produced_at:
        raise ValueError("occurred_at cannot be after produced_at")
    if known_at > produced_at:
        raise ValueError("known_at cannot be after produced_at")
    if valid_from is not None and valid_until is not None and valid_until < valid_from:
        raise ValueError("valid_until cannot be before valid_from")


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
    evidence_receipt_ids: tuple[str, ...] = ()
    source_event_at: datetime | None = None
    known_at: datetime | None = None
    produced_at: datetime | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("schema_version", "receipt_id", "producer", "producer_key_id", "event_type", "subject_id"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        if self.schema_version not in {"1.1", "2.0"}:
            raise ValueError("schema_version must be 1.1 or 2.0")
        _require_aware(self.occurred_at, "occurred_at")
        if self.schema_version == "1.1":
            if self.evidence_receipt_ids:
                raise ValueError("v1.1 envelopes cannot carry v2 evidence dependencies")
            if any(
                value is not None
                for value in (
                    self.source_event_at,
                    self.known_at,
                    self.produced_at,
                    self.valid_from,
                    self.valid_until,
                )
            ):
                raise ValueError("v1.1 envelopes cannot carry v2 timing fields")
        else:
            _require_v2_timing(
                occurred_at=self.occurred_at,
                source_event_at=self.source_event_at,
                known_at=self.known_at,
                produced_at=self.produced_at,
                valid_from=self.valid_from,
                valid_until=self.valid_until,
            )
        _require_digest(self.payload_digest)
        _require_visibility(self.privacy_class, self.visibility_scope)
        _require_dependencies(
            receipt_id=self.receipt_id,
            causation_receipt_id=self.causation_receipt_id,
            evidence_receipt_ids=self.evidence_receipt_ids,
        )
        if self.privacy_class is PrivacyClass.SECRET_REGULATED and self.payload_ref is not None:
            if not self.payload_ref.startswith(("vault://", "secure://", "kms://")):
                raise ValueError("SECRET_REGULATED evidence must reference restricted storage")
        if not self.signature:
            raise ValueError("signature is required")

    def signing_body(self) -> dict[str, object]:
        body: dict[str, object] = {
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
        if self.schema_version == "2.0":
            body.update(
                {
                    "evidence_receipt_ids": list(self.evidence_receipt_ids),
                    "source_event_at": self.source_event_at.isoformat() if self.source_event_at else None,
                    "known_at": self.known_at.isoformat() if self.known_at else None,
                    "produced_at": self.produced_at.isoformat() if self.produced_at else None,
                    "valid_from": self.valid_from.isoformat() if self.valid_from else None,
                    "valid_until": self.valid_until.isoformat() if self.valid_until else None,
                }
            )
        return body

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
