from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from .anchor import merkle_root_hashes
from .canonical import canonical_json, sha256_hex


class JournalError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class JournalLeaf:
    record_id: str
    payload_digest: str
    leaf_hash: str


@dataclass(frozen=True, slots=True)
class MerkleProofNode:
    side: str
    hash: str


@dataclass(frozen=True, slots=True)
class JournalCommitment:
    schema_version: str
    journal_id: str
    record_type: str
    ordering: str
    first_record_id: str
    last_record_id: str
    record_count: int
    merkle_root: str
    period_start: datetime
    period_end: datetime
    sealed_at: datetime
    source_ref: str

    def wire(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "journal_id": self.journal_id,
            "record_type": self.record_type,
            "ordering": self.ordering,
            "first_record_id": self.first_record_id,
            "last_record_id": self.last_record_id,
            "record_count": self.record_count,
            "merkle_root": self.merkle_root,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "sealed_at": self.sealed_at.isoformat(),
            "source_ref": self.source_ref,
        }

    def payload_bytes(self) -> bytes:
        return canonical_json(self.wire())


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise JournalError(f"{field} must be timezone-aware")


def _leaf_hash(record_id: str, payload_digest: str) -> str:
    if not record_id:
        raise JournalError("record_id is required")
    if len(payload_digest) != 64:
        raise JournalError("payload_digest must be SHA-256 hex")
    try:
        int(payload_digest, 16)
    except ValueError as exc:
        raise JournalError("payload_digest must be SHA-256 hex") from exc
    return sha256_hex(canonical_json({"record_id": record_id, "payload_digest": payload_digest.lower()}))


def journal_leaf(record_id: str, payload: bytes) -> JournalLeaf:
    payload_digest = sha256_hex(payload)
    return JournalLeaf(record_id, payload_digest, _leaf_hash(record_id, payload_digest))


def seal_journal(
    *,
    journal_id: str,
    record_type: str,
    records: Sequence[tuple[str, bytes]],
    period_start: datetime,
    period_end: datetime,
    sealed_at: datetime,
    source_ref: str,
) -> tuple[JournalCommitment, tuple[JournalLeaf, ...]]:
    if not journal_id or not record_type or not source_ref:
        raise JournalError("journal_id, record_type, and source_ref are required")
    if not records:
        raise JournalError("journal requires at least one record")
    _require_aware(period_start, "period_start")
    _require_aware(period_end, "period_end")
    _require_aware(sealed_at, "sealed_at")
    if period_end < period_start:
        raise JournalError("period_end cannot be before period_start")
    if sealed_at < period_end:
        raise JournalError("sealed_at cannot be before period_end")
    record_ids = [record_id for record_id, _ in records]
    if any(not record_id for record_id in record_ids):
        raise JournalError("record ids must be non-empty")
    if len(set(record_ids)) != len(record_ids):
        raise JournalError("journal record ids must be unique")

    leaves = tuple(journal_leaf(record_id, payload) for record_id, payload in records)
    commitment = JournalCommitment(
        schema_version="1.0",
        journal_id=journal_id,
        record_type=record_type,
        ordering="PRODUCER_SEQUENCE",
        first_record_id=leaves[0].record_id,
        last_record_id=leaves[-1].record_id,
        record_count=len(leaves),
        merkle_root=merkle_root_hashes([leaf.leaf_hash for leaf in leaves]),
        period_start=period_start,
        period_end=period_end,
        sealed_at=sealed_at,
        source_ref=source_ref,
    )
    return commitment, leaves


def journal_merkle_proof(leaves: Sequence[JournalLeaf], index: int) -> tuple[MerkleProofNode, ...]:
    if not leaves:
        raise JournalError("proof requires at least one leaf")
    if index < 0 or index >= len(leaves):
        raise JournalError("proof index out of range")

    layer = [leaf.leaf_hash for leaf in leaves]
    position = index
    proof: list[MerkleProofNode] = []
    while len(layer) > 1:
        working = list(layer)
        if len(working) % 2:
            working.append(working[-1])
        sibling = position - 1 if position % 2 else position + 1
        side = "LEFT" if sibling < position else "RIGHT"
        proof.append(MerkleProofNode(side=side, hash=working[sibling]))
        next_layer = []
        for offset in range(0, len(working), 2):
            left = bytes.fromhex(working[offset])
            right = bytes.fromhex(working[offset + 1])
            next_layer.append(sha256_hex(left + right))
        position //= 2
        layer = next_layer
    return tuple(proof)


def verify_journal_inclusion(
    *,
    record_id: str,
    payload: bytes,
    proof: Sequence[MerkleProofNode],
    expected_root: str,
) -> bool:
    current = bytes.fromhex(journal_leaf(record_id, payload).leaf_hash)
    try:
        for node in proof:
            sibling = bytes.fromhex(node.hash)
            if node.side == "LEFT":
                current = bytes.fromhex(sha256_hex(sibling + current))
            elif node.side == "RIGHT":
                current = bytes.fromhex(sha256_hex(current + sibling))
            else:
                return False
    except ValueError:
        return False
    return current.hex() == expected_root.lower()
