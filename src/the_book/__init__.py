"""The Book: private proof history plus public testimony."""

from .anchor import AnchorReceipt, DisabledAnchor, LiveAnchoringDisabled, merkle_root
from .canonical import canonical_json, sha256_hex
from .domain import EvidenceClass, EvidenceEnvelope, LedgerEntry, PrivacyClass
from .identity import AuthorityRegistry, Ed25519ProducerSigner, IdentityError, sign_evidence, sign_evidence_v2
from .ledger import (
    BigBook,
    DuplicateReceipt,
    EvidenceLedger,
    EvidenceLedgerError,
    InvalidCausation,
    InvalidEvidenceDependency,
    InvalidRecordingTime,
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
from .namespaces import NamespaceAuthority, NamespaceAuthorityError, V2_NAMESPACE_AUTHORITIES
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
    "InvalidEvidenceDependency",
    "InvalidRecordingTime",
    "LedgerEntry",
    "LittleBook",
    "LittleBookError",
    "LiveAnchoringDisabled",
    "NamespaceAuthority",
    "NamespaceAuthorityError",
    "PayloadDigestMismatch",
    "PrivacyClass",
    "PublicAttestation",
    "SecretPayloadRejected",
    "SignatureRejected",
    "StateCommitment",
    "V2_NAMESPACE_AUTHORITIES",
    "can_view",
    "canonical_json",
    "merkle_root",
    "require_view",
    "sha256_hex",
    "sign_evidence",
    "sign_evidence_v2",
    "sign_scoped_evidence",
    "verify_public_record",
]
