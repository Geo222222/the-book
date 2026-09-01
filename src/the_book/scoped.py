from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from .canonical import canonical_json
from .domain import EvidenceClass, EvidenceEnvelope, PrivacyClass
from .identity import Ed25519ProducerSigner


def sign_scoped_evidence(
    signer: Ed25519ProducerSigner,
    *,
    receipt_id: str,
    event_type: str,
    evidence_class: EvidenceClass,
    privacy_class: PrivacyClass,
    subject_id: str,
    occurred_at: datetime,
    payload_digest: str,
    visibility_scope: tuple[str, ...],
    payload_ref: str | None = None,
    correlation_id: str | None = None,
    causation_receipt_id: str | None = None,
) -> EvidenceEnvelope:
    """Sign an evidence proof whose privacy and visibility are explicit parts of the signature."""
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
    return replace(unsigned, signature=signer.sign(canonical_json(unsigned.signing_body())))
