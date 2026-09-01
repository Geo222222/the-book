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


class DisabledAnchor:
    def anchor(self, *, root_hash: str, start_sequence: int, end_sequence: int) -> AnchorReceipt:
        raise LiveAnchoringDisabled("B0 has no live blockchain anchor adapter")


def merkle_root(entries: Sequence[LedgerEntry]) -> str:
    if not entries:
        raise ValueError("at least one ledger entry is required")
    layer = [bytes.fromhex(entry.entry_hash) for entry in entries]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [bytes.fromhex(sha256_hex(layer[i] + layer[i + 1])) for i in range(0, len(layer), 2)]
    return layer[0].hex()
