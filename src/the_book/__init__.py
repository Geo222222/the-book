"""The Book: private proof history plus public testimony."""

from .anchor import AnchorReceipt, DisabledAnchor, LiveAnchoringDisabled, merkle_root
from .canonical import canonical_json, sha256_hex
from .domain import EvidenceClass, EvidenceEnvelope, LedgerEntry, PrivacyClass
from .identity import AuthorityRegistry, Ed25519ProducerSigner, IdentityError, sign_evidence
from .ledger import (
    BigBook,
    DuplicateReceipt,
    EvidenceLedger,
    EvidenceLedgerError,
    InvalidCausation,
    PayloadDigestMismatch,
    SecretPayloadRejected,
    SignatureRejected,
)
from .little_book import (
    DisclosurePolicy,
    DisclosureRejected,
    DuplicatePublicRecord,
    LittleBook,
    LittleBookError,
    PublicAttestation,
    StateCommitment,
    verify_public_record,
)
from .privacy import AccessDenied, can_view, require_view
from .scoped import sign_scoped_evidence

__all__ = [
    "AccessDenied",
    "AnchorReceipt",
    "AuthorityRegistry",
    "BigBook",
    "DisabledAnchor",
    "DisclosurePolicy",
    "DisclosureRejected",
    "DuplicatePublicRecord",
    "DuplicateReceipt",
    "Ed25519ProducerSigner",
    "EvidenceClass",
    "EvidenceEnvelope",
    "EvidenceLedger",
    "EvidenceLedgerError",
    "IdentityError",
    "InvalidCausation",
    "LedgerEntry",
    "LittleBook",
    "LittleBookError",
    "LiveAnchoringDisabled",
    "PayloadDigestMismatch",
    "PrivacyClass",
    "PublicAttestation",
    "SecretPayloadRejected",
    "SignatureRejected",
    "StateCommitment",
    "can_view",
    "canonical_json",
    "merkle_root",
    "require_view",
    "sha256_hex",
    "sign_evidence",
    "sign_scoped_evidence",
    "verify_public_record",
]
