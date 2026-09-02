from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Sequence

from .canonical import sha256_hex
from .domain import LedgerEntry


class LiveAnchoringDisabled(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AnchorReceipt:
    root_hash: str
    start_sequence: int
    end_sequence: int
    chain_id: str
    transaction_id: str
    anchored_at: datetime


class AnchorAdapter(Protocol):
    def anchor(self, *, root_hash: str, start_sequence: int, end_sequence: int) -> AnchorReceipt: ...


def merkle_root_hashes(hashes: Sequence[str]) -> str:
    if not hashes:
        raise ValueError("at least one hash is required")
    try:
        layer = [bytes.fromhex(value) for value in hashes]
    except ValueError as exc:
        raise ValueError("Merkle leaves must be hexadecimal hashes") from exc
    if any(len(value) != 32 for value in layer):
        raise ValueError("Merkle leaves must be 32-byte SHA-256 hashes")
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [bytes.fromhex(sha256_hex(layer[i] + layer[i + 1])) for i in range(0, len(layer), 2)]
    return layer[0].hex()


def merkle_root(entries: Sequence[LedgerEntry]) -> str:
    if not entries:
        raise ValueError("at least one ledger entry is required")
    return merkle_root_hashes([entry.entry_hash for entry in entries])
