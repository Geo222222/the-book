"""The Book: shared evidence, provenance, and integrity infrastructure."""

from .anchor import AnchorReceipt, DisabledAnchor, LiveAnchoringDisabled, merkle_root
from .canonical import canonical_json, sha256_hex
from .domain import EvidenceClass, EvidenceEnvelope, LedgerEntry
from .identity import AuthorityRegistry, Ed25519ProducerSigner, IdentityError, sign_evidence
from .ledger import (
    DuplicateReceipt,
    EvidenceLedger,
    EvidenceLedgerError,
    InvalidCausation,
    PayloadDigestMismatch,
    SignatureRejected,
)

__all__ = [
    "AnchorReceipt",
    "AuthorityRegistry",
    "DisabledAnchor",
    "DuplicateReceipt",
    "Ed25519ProducerSigner",
    "EvidenceClass",
    "EvidenceEnvelope",
    "EvidenceLedger",
    "EvidenceLedgerError",
    "IdentityError",
    "InvalidCausation",
    "LedgerEntry",
    "LiveAnchoringDisabled",
    "PayloadDigestMismatch",
    "SignatureRejected",
    "canonical_json",
    "merkle_root",
    "sha256_hex",
    "sign_evidence",
]
