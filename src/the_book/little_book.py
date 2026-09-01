from __future__ import annotations

import base64
from dataclasses import dataclass, replace
from datetime import datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import canonical_json
from .identity import Ed25519ProducerSigner


class LittleBookError(RuntimeError):
    pass


class DisclosureRejected(LittleBookError):
    pass


class DuplicatePublicRecord(LittleBookError):
    pass


@dataclass(frozen=True, slots=True)
class DisclosurePolicy:
    allowed_claim_types: frozenset[str]
    allow_named_subjects: bool = False

    def __post_init__(self) -> None:
        if not self.allowed_claim_types:
            raise ValueError("allowed_claim_types cannot be empty")


@dataclass(frozen=True, slots=True)
class StateCommitment:
    schema_version: str
    commitment_id: str
    issuer: str
    issuer_key_id: str
    state_epoch: str
    merkle_root: str
    issued_at: datetime
    signature: str

    def signing_body(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "commitment_id": self.commitment_id,
            "issuer": self.issuer,
            "issuer_key_id": self.issuer_key_id,
            "state_epoch": self.state_epoch,
            "merkle_root": self.merkle_root,
            "issued_at": self.issued_at.isoformat(),
        }

    def wire(self) -> dict[str, object]:
        return {**self.signing_body(), "signature": self.signature}


@dataclass(frozen=True, slots=True)
class PublicAttestation:
    schema_version: str
    attestation_id: str
    issuer: str
    issuer_key_id: str
    claim_type: str
    claim: str
    evidence_commitment: str
    big_book_root: str
    issued_at: datetime
    public_subject: str | None
    expires_at: datetime | None
    supersedes_attestation_id: str | None
    signature: str

    def signing_body(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "attestation_id": self.attestation_id,
            "issuer": self.issuer,
            "issuer_key_id": self.issuer_key_id,
            "claim_type": self.claim_type,
            "claim": self.claim,
            "evidence_commitment": self.evidence_commitment,
            "big_book_root": self.big_book_root,
            "issued_at": self.issued_at.isoformat(),
            "public_subject": self.public_subject,
            "expires_at": None if self.expires_at is None else self.expires_at.isoformat(),
            "supersedes_attestation_id": self.supersedes_attestation_id,
        }

    def wire(self) -> dict[str, object]:
        return {**self.signing_body(), "signature": self.signature}


PublicRecord = StateCommitment | PublicAttestation


class LittleBook:
    """Public testimony surface.

    It accepts only explicit public records. There is intentionally no generic
    Big Book export or projection API, and state commitment publication accepts a
    root rather than private entries.
    """

    def __init__(self, policy: DisclosurePolicy) -> None:
        self._policy = policy
        self._records: list[PublicRecord] = []
        self._ids: set[str] = set()

    @property
    def records(self) -> tuple[PublicRecord, ...]:
        return tuple(self._records)

    def publish_state_commitment(
        self,
        *,
        signer: Ed25519ProducerSigner,
        commitment_id: str,
        state_epoch: str,
        merkle_root: str,
        issued_at: datetime,
    ) -> StateCommitment:
        if commitment_id in self._ids:
            raise DuplicatePublicRecord(commitment_id)
        if not state_epoch or len(state_epoch) > 128:
            raise DisclosureRejected("state_epoch must be concise and non-empty")
        if len(merkle_root) != 64:
            raise DisclosureRejected("merkle_root must be a SHA-256 commitment")
        try:
            int(merkle_root, 16)
        except ValueError as exc:
            raise DisclosureRejected("merkle_root must be hexadecimal") from exc
        if issued_at.tzinfo is None or issued_at.utcoffset() is None:
            raise DisclosureRejected("issued_at must be timezone-aware")

        unsigned = StateCommitment(
            schema_version="1.1",
            commitment_id=commitment_id,
            issuer=signer.producer,
            issuer_key_id=signer.key_id,
            state_epoch=state_epoch,
            merkle_root=merkle_root,
            issued_at=issued_at,
            signature="PENDING",
        )
        record = replace(unsigned, signature=signer.sign(canonical_json(unsigned.signing_body())))
        self._records.append(record)
        self._ids.add(commitment_id)
        return record

    def publish_attestation(
        self,
        *,
        signer: Ed25519ProducerSigner,
        attestation_id: str,
        claim_type: str,
        claim: str,
        evidence_commitment: str,
        big_book_root: str,
        issued_at: datetime,
        public_subject: str | None = None,
        expires_at: datetime | None = None,
        supersedes_attestation_id: str | None = None,
    ) -> PublicAttestation:
        if attestation_id in self._ids:
            raise DuplicatePublicRecord(attestation_id)
        if claim_type not in self._policy.allowed_claim_types:
            raise DisclosureRejected("claim type is not approved for public disclosure")
        if public_subject is not None and not self._policy.allow_named_subjects:
            raise DisclosureRejected("policy does not permit named public subjects")
        if not claim or len(claim) > 512:
            raise DisclosureRejected("public claim must be concise and non-empty")
        for name, value in (("evidence_commitment", evidence_commitment), ("big_book_root", big_book_root)):
            if len(value) != 64:
                raise DisclosureRejected(f"{name} must be a SHA-256 commitment")
            try:
                int(value, 16)
            except ValueError as exc:
                raise DisclosureRejected(f"{name} must be hexadecimal") from exc
        if issued_at.tzinfo is None or issued_at.utcoffset() is None:
            raise DisclosureRejected("issued_at must be timezone-aware")
        if expires_at is not None:
            if expires_at.tzinfo is None or expires_at.utcoffset() is None:
                raise DisclosureRejected("expires_at must be timezone-aware")
            if expires_at <= issued_at:
                raise DisclosureRejected("expires_at must be after issued_at")

        unsigned = PublicAttestation(
            schema_version="1.1",
            attestation_id=attestation_id,
            issuer=signer.producer,
            issuer_key_id=signer.key_id,
            claim_type=claim_type,
            claim=claim,
            evidence_commitment=evidence_commitment,
            big_book_root=big_book_root,
            issued_at=issued_at,
            public_subject=public_subject,
            expires_at=expires_at,
            supersedes_attestation_id=supersedes_attestation_id,
            signature="PENDING",
        )
        record = replace(unsigned, signature=signer.sign(canonical_json(unsigned.signing_body())))
        self._records.append(record)
        self._ids.add(attestation_id)
        return record


def verify_public_record(record: PublicRecord, public_key: bytes) -> bool:
    try:
        signature = base64.b64decode(record.signature, validate=True)
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, canonical_json(record.signing_body()))
    except (ValueError, InvalidSignature):
        return False
    return True
