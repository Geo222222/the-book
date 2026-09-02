from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from .anchor import merkle_root
from .canonical import canonical_json, sha256_hex
from .domain import EvidenceEnvelope, LedgerEntry, PrivacyClass
from .identity import AuthorityRegistry
from .payload_contracts import DomainPayloadError, validate_target_payload
from .privacy import can_view, require_view


class EvidenceLedgerError(RuntimeError):
    pass


class SignatureRejected(EvidenceLedgerError):
    pass


class DuplicateReceipt(EvidenceLedgerError):
    pass


class InvalidCausation(EvidenceLedgerError):
    pass


class InvalidEvidenceDependency(EvidenceLedgerError):
    pass


class InvalidRecordingTime(EvidenceLedgerError):
    pass


class InvalidDomainPayload(EvidenceLedgerError):
    pass


class PayloadDigestMismatch(EvidenceLedgerError):
    pass


class SecretPayloadRejected(EvidenceLedgerError):
    pass


@dataclass(frozen=True, slots=True)
class BookReceipt:
    receipt_id: str
    sequence: int
    entry_hash: str
    recorded_at: datetime
    accepted: bool
    duplicate_replay: bool

    def wire(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "sequence": self.sequence,
            "entry_hash": self.entry_hash,
            "recorded_at": self.recorded_at.isoformat(),
            "accepted": self.accepted,
            "duplicate_replay": self.duplicate_replay,
        }


class BigBook:
    """Private authoritative proof history.

    The in-process kernel models proof semantics. Production authorization must
    additionally be enforced at the service/storage boundary; callers are not
    given a generic API that enumerates every private envelope.
    """

    def __init__(self, registry: AuthorityRegistry) -> None:
        self._registry = registry
        self._entries: list[LedgerEntry] = []
        self._receipt_ids: set[str] = set()
        self._receipt_index: dict[str, LedgerEntry] = {}

    @property
    def entry_count(self) -> int:
        """Operational metadata for the trusted Big Book service, not Little Book output."""
        return len(self._entries)

    def _validate_payload(self, envelope: EvidenceEnvelope, payload: bytes | None) -> None:
        if envelope.privacy_class is PrivacyClass.SECRET_REGULATED and payload is not None:
            raise SecretPayloadRejected(
                "SECRET_REGULATED source material must be hashed in its restricted system; raw bytes may not enter The Book"
            )
        if payload is not None:
            if sha256_hex(payload) != envelope.payload_digest:
                raise PayloadDigestMismatch("payload does not match declared digest")
            try:
                validate_target_payload(envelope, payload)
            except DomainPayloadError as exc:
                raise InvalidDomainPayload(str(exc)) from exc

    def _validate_typed_causation(self, envelope: EvidenceEnvelope) -> None:
        """Enforce causal organ boundaries that require ledger context."""
        if envelope.event_type in {"WATCHMAN.AUTHORIZATION", "WATCHMAN.BLOCK"}:
            if envelope.causation_receipt_id is None:
                raise InvalidCausation("Watchman governance requires a Benjamin decision causation receipt")
            parent = self._receipt_index.get(envelope.causation_receipt_id)
            if parent is None or parent.envelope.event_type != "BENJAMIN.DECISION":
                raise InvalidCausation(
                    "Watchman governance must causally reference an existing BENJAMIN.DECISION receipt"
                )
        if envelope.event_type == "HAND.EXECUTION":
            if envelope.causation_receipt_id is None:
                raise InvalidCausation("Hand execution requires a Watchman authorization causation receipt")
            parent = self._receipt_index.get(envelope.causation_receipt_id)
            if parent is None or parent.envelope.event_type != "WATCHMAN.AUTHORIZATION":
                raise InvalidCausation(
                    "HAND.EXECUTION must causally reference an existing WATCHMAN.AUTHORIZATION receipt"
                )

    def append(
        self,
        envelope: EvidenceEnvelope,
        *,
        payload: bytes | None = None,
        recorded_at: datetime | None = None,
    ) -> LedgerEntry:
        if envelope.receipt_id in self._receipt_ids:
            raise DuplicateReceipt(envelope.receipt_id)
        if not self._registry.verify(envelope):
            raise SignatureRejected("producer signature, identity, or event namespace was rejected")
        self._validate_payload(envelope, payload)
        if envelope.causation_receipt_id and envelope.causation_receipt_id not in self._receipt_ids:
            raise InvalidCausation("causation receipt must already exist in the Big Book")
        self._validate_typed_causation(envelope)
        missing_dependencies = [
            receipt_id
            for receipt_id in envelope.evidence_receipt_ids
            if receipt_id not in self._receipt_ids
        ]
        if missing_dependencies:
            raise InvalidEvidenceDependency(
                "evidence dependencies must already exist in the Big Book: "
                + ", ".join(missing_dependencies)
            )

        timestamp = recorded_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise EvidenceLedgerError("recorded_at must be timezone-aware")
        if envelope.schema_version == "2.0" and envelope.produced_at is not None and timestamp < envelope.produced_at:
            raise InvalidRecordingTime("recorded_at cannot be before v2 produced_at")
        previous_hash = self._entries[-1].entry_hash if self._entries else "GENESIS"
        chain_body = {
            "sequence": len(self._entries),
            "envelope": envelope.wire(),
            "recorded_at": timestamp.isoformat(),
            "previous_hash": previous_hash,
        }
        entry_hash = sha256_hex(canonical_json(chain_body))
        entry = LedgerEntry(
            sequence=len(self._entries),
            envelope=envelope,
            recorded_at=timestamp,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )
        self._entries.append(entry)
        self._receipt_ids.add(envelope.receipt_id)
        self._receipt_index[envelope.receipt_id] = entry
        return entry

    def append_idempotent(
        self,
        envelope: EvidenceEnvelope,
        *,
        payload: bytes | None = None,
        recorded_at: datetime | None = None,
    ) -> BookReceipt:
        """Append once, or acknowledge an exact replay after a lost response.

        Reusing a receipt id for different signed evidence remains a hard error.
        """
        existing = self._receipt_index.get(envelope.receipt_id)
        if existing is not None:
            if existing.envelope != envelope:
                raise DuplicateReceipt(
                    f"receipt id {envelope.receipt_id!r} already belongs to different evidence"
                )
            self._validate_payload(envelope, payload)
            self._validate_typed_causation(envelope)
            return BookReceipt(
                receipt_id=existing.envelope.receipt_id,
                sequence=existing.sequence,
                entry_hash=existing.entry_hash,
                recorded_at=existing.recorded_at,
                accepted=True,
                duplicate_replay=True,
            )

        entry = self.append(envelope, payload=payload, recorded_at=recorded_at)
        return BookReceipt(
            receipt_id=entry.envelope.receipt_id,
            sequence=entry.sequence,
            entry_hash=entry.entry_hash,
            recorded_at=entry.recorded_at,
            accepted=True,
            duplicate_replay=False,
        )

    def visible_entries(
        self,
        *,
        principal: str,
        authorities: Iterable[str] = (),
    ) -> tuple[LedgerEntry, ...]:
        return tuple(
            entry
            for entry in self._entries
            if can_view(entry.envelope, principal=principal, authorities=authorities)
        )

    def get(
        self,
        receipt_id: str,
        *,
        principal: str,
        authorities: Iterable[str] = (),
    ) -> LedgerEntry:
        entry = self._receipt_index[receipt_id]
        require_view(entry.envelope, principal=principal, authorities=authorities)
        return entry

    def state_root(self) -> str:
        """Return only the current cryptographic commitment, never private envelopes."""
        if not self._entries:
            raise EvidenceLedgerError("cannot commit an empty Big Book")
        return merkle_root(tuple(self._entries))

    def verify_integrity(self) -> bool:
        seen: set[str] = set()
        for sequence, entry in enumerate(self._entries):
            if entry.sequence != sequence:
                return False
            expected_previous = self._entries[sequence - 1].entry_hash if sequence else "GENESIS"
            if entry.previous_hash != expected_previous:
                return False
            if entry.envelope.receipt_id in seen:
                return False
            if entry.envelope.causation_receipt_id and entry.envelope.causation_receipt_id not in seen:
                return False
            if entry.envelope.event_type in {"WATCHMAN.AUTHORIZATION", "WATCHMAN.BLOCK"}:
                parent_id = entry.envelope.causation_receipt_id
                parent = self._receipt_index.get(parent_id) if parent_id else None
                if parent is None or parent.envelope.event_type != "BENJAMIN.DECISION":
                    return False
            if entry.envelope.event_type == "HAND.EXECUTION":
                parent_id = entry.envelope.causation_receipt_id
                parent = self._receipt_index.get(parent_id) if parent_id else None
                if parent is None or parent.envelope.event_type != "WATCHMAN.AUTHORIZATION":
                    return False
            if any(receipt_id not in seen for receipt_id in entry.envelope.evidence_receipt_ids):
                return False
            if entry.envelope.schema_version == "2.0" and entry.envelope.produced_at is not None:
                if entry.recorded_at < entry.envelope.produced_at:
                    return False
            if not self._registry.verify(entry.envelope):
                return False
            if sha256_hex(canonical_json(entry.chain_body())) != entry.entry_hash:
                return False
            seen.add(entry.envelope.receipt_id)
        return True


# Backward-compatible type name for B0 callers. New code should use BigBook.
EvidenceLedger = BigBook
