from __future__ import annotations

from datetime import datetime, timezone

from .canonical import canonical_json, sha256_hex
from .domain import EvidenceEnvelope, LedgerEntry
from .identity import AuthorityRegistry


class EvidenceLedgerError(RuntimeError):
    pass


class SignatureRejected(EvidenceLedgerError):
    pass


class DuplicateReceipt(EvidenceLedgerError):
    pass


class InvalidCausation(EvidenceLedgerError):
    pass


class PayloadDigestMismatch(EvidenceLedgerError):
    pass


class EvidenceLedger:
    """B0 in-memory append-only ledger with signature and lineage verification."""

    def __init__(self, registry: AuthorityRegistry) -> None:
        self._registry = registry
        self._entries: list[LedgerEntry] = []
        self._receipt_ids: set[str] = set()

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries)

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
        if payload is not None and sha256_hex(payload) != envelope.payload_digest:
            raise PayloadDigestMismatch("payload does not match declared digest")
        if envelope.causation_receipt_id and envelope.causation_receipt_id not in self._receipt_ids:
            raise InvalidCausation("causation receipt must already exist in The Book")

        timestamp = recorded_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise EvidenceLedgerError("recorded_at must be timezone-aware")
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
        return entry

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
            if not self._registry.verify(entry.envelope):
                return False
            if sha256_hex(canonical_json(entry.chain_body())) != entry.entry_hash:
                return False
            seen.add(entry.envelope.receipt_id)
        return True
