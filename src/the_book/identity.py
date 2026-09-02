from __future__ import annotations

import base64
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .canonical import canonical_json
from .domain import EvidenceClass, EvidenceEnvelope, PrivacyClass
from .namespaces import require_v2_namespace_authority


class IdentityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PublicIdentity:
    producer: str
    key_id: str
    public_key: bytes
    allowed_event_prefixes: tuple[str, ...]


class Ed25519ProducerSigner:
    """Producer-side signer. Private key material must not be persisted by The Book."""

    def __init__(self, producer: str, key_id: str, private_key: Ed25519PrivateKey) -> None:
        if not producer or not key_id:
            raise IdentityError("producer and key_id are required")
        self.producer = producer
        self.key_id = key_id
        self._private_key = private_key

    @classmethod
    def generate(cls, producer: str, key_id: str) -> "Ed25519ProducerSigner":
        return cls(producer, key_id, Ed25519PrivateKey.generate())

    @property
    def public_key_bytes(self) -> bytes:
        return self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def sign(self, message: bytes) -> str:
        return base64.b64encode(self._private_key.sign(message)).decode("ascii")


class AuthorityRegistry:
    """Public verification registry. It intentionally stores no private signing keys."""

    def __init__(self) -> None:
        self._identities: dict[str, PublicIdentity] = {}

    def register(
        self,
        *,
        producer: str,
        key_id: str,
        public_key: bytes,
        allowed_event_prefixes: Iterable[str],
    ) -> None:
        prefixes = tuple(allowed_event_prefixes)
        if not prefixes or any(not prefix for prefix in prefixes):
            raise IdentityError("at least one event prefix is required")
        if key_id in self._identities:
            raise IdentityError("key_id is already registered")
        require_v2_namespace_authority(producer=producer, prefixes=prefixes)
        self._identities[key_id] = PublicIdentity(producer, key_id, bytes(public_key), prefixes)

    def verify(self, envelope: EvidenceEnvelope) -> bool:
        identity = self._identities.get(envelope.producer_key_id)
        if identity is None or identity.producer != envelope.producer:
            return False
        if not any(envelope.event_type.startswith(prefix) for prefix in identity.allowed_event_prefixes):
            return False
        try:
            signature = base64.b64decode(envelope.signature, validate=True)
            Ed25519PublicKey.from_public_bytes(identity.public_key).verify(
                signature,
                canonical_json(envelope.signing_body()),
            )
        except (ValueError, InvalidSignature):
            return False
        return True


def sign_evidence(
    signer: Ed25519ProducerSigner,
    *,
    receipt_id: str,
    event_type: str,
    evidence_class: EvidenceClass,
    subject_id: str,
    occurred_at: datetime,
    payload_digest: str,
    privacy_class: PrivacyClass = PrivacyClass.CONFIDENTIAL_EVIDENCE,
    visibility_scope: tuple[str, ...] = ("INSTITUTION",),
    payload_ref: str | None = None,
    correlation_id: str | None = None,
    causation_receipt_id: str | None = None,
) -> EvidenceEnvelope:
    """Sign a v1.1 proof envelope, including privacy and visibility in the signature."""
    unsigned = EvidenceEnvelope(
        schema_version="1.1",
        receipt_id=receipt_id,
        producer=signer.producer,
        producer_key_id=signer.key_id,
        event_type=event_type,
        evidence_class=evidence_class,
        subject_id=subject_id,
        occurred_at=occurred_at,
        payload_digest=payload_digest,
        payload_ref=payload_ref,
        correlation_id=correlation_id,
        causation_receipt_id=causation_receipt_id,
        signature="PENDING",
        privacy_class=privacy_class,
        visibility_scope=visibility_scope,
    )
    signature = signer.sign(canonical_json(unsigned.signing_body()))
    return replace(unsigned, signature=signature)
