from dataclasses import replace
from datetime import datetime, timezone

import pytest

from the_book import (
    AuthorityRegistry,
    DisabledAnchor,
    DuplicateReceipt,
    Ed25519ProducerSigner,
    EvidenceClass,
    EvidenceLedger,
    InvalidCausation,
    LiveAnchoringDisabled,
    PayloadDigestMismatch,
    SignatureRejected,
    sha256_hex,
    sign_evidence,
)


NOW = datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc)


def setup_identity(producer: str = "Benjamin", key_id: str = "benjamin-k1", prefix: str = "BENJAMIN."):
    signer = Ed25519ProducerSigner.generate(producer, key_id)
    registry = AuthorityRegistry()
    registry.register(
        producer=producer,
        key_id=key_id,
        public_key=signer.public_key_bytes,
        allowed_event_prefixes=(prefix,),
    )
    return signer, registry


def envelope(signer, payload: bytes, **updates):
    args = {
        "receipt_id": "RCP-001",
        "event_type": "BENJAMIN.DECISION",
        "evidence_class": EvidenceClass.ECONOMIC,
        "subject_id": "DEC-001",
        "occurred_at": NOW,
        "payload_digest": sha256_hex(payload),
        "payload_ref": "vault://decisions/DEC-001",
        "correlation_id": "LIFE-001",
    }
    args.update(updates)
    return sign_evidence(signer, **args)


def test_signed_evidence_is_accepted_without_storing_raw_payload() -> None:
    signer, registry = setup_identity()
    payload = b'{"status":"APPROVED"}'
    ledger = EvidenceLedger(registry)
    entry = ledger.append(envelope(signer, payload), payload=payload, recorded_at=NOW)

    assert entry.envelope.payload_digest == sha256_hex(payload)
    assert not hasattr(entry, "payload")
    assert ledger.verify_integrity() is True


def test_tampered_envelope_signature_is_rejected() -> None:
    signer, registry = setup_identity()
    payload = b"original"
    signed = envelope(signer, payload)
    tampered = replace(signed, subject_id="DEC-TAMPERED")
    with pytest.raises(SignatureRejected):
        EvidenceLedger(registry).append(tampered, payload=payload, recorded_at=NOW)


def test_valid_key_cannot_impersonate_another_namespace() -> None:
    signer, registry = setup_identity()
    payload = b"execution"
    forged = envelope(signer, payload, event_type="HAND.EXECUTION")
    with pytest.raises(SignatureRejected):
        EvidenceLedger(registry).append(forged, payload=payload, recorded_at=NOW)


def test_payload_digest_must_match_source_evidence() -> None:
    signer, registry = setup_identity()
    signed = envelope(signer, b"expected")
    with pytest.raises(PayloadDigestMismatch):
        EvidenceLedger(registry).append(signed, payload=b"different", recorded_at=NOW)


def test_duplicate_receipt_is_rejected() -> None:
    signer, registry = setup_identity()
    payload = b"same"
    signed = envelope(signer, payload)
    ledger = EvidenceLedger(registry)
    ledger.append(signed, payload=payload, recorded_at=NOW)
    with pytest.raises(DuplicateReceipt):
        ledger.append(signed, payload=payload, recorded_at=NOW)


def test_correction_is_new_signed_evidence_with_backward_lineage() -> None:
    signer, registry = setup_identity()
    ledger = EvidenceLedger(registry)
    original_payload = b"approved"
    original = envelope(signer, original_payload)
    ledger.append(original, payload=original_payload, recorded_at=NOW)

    correction_payload = b"rejected due to operator correction"
    correction = envelope(
        signer,
        correction_payload,
        receipt_id="RCP-002",
        event_type="BENJAMIN.CORRECTION",
        subject_id="DEC-001",
        payload_digest=sha256_hex(correction_payload),
        causation_receipt_id="RCP-001",
    )
    ledger.append(correction, payload=correction_payload, recorded_at=NOW)

    visible = ledger.visible_entries(principal="INSTITUTION")
    assert len(visible) == 2
    assert visible[0].envelope == original
    assert visible[1].envelope.causation_receipt_id == "RCP-001"
    assert ledger.verify_integrity() is True


def test_unknown_causation_is_rejected() -> None:
    signer, registry = setup_identity()
    payload = b"child"
    signed = envelope(signer, payload, causation_receipt_id="MISSING")
    with pytest.raises(InvalidCausation):
        EvidenceLedger(registry).append(signed, payload=payload, recorded_at=NOW)


def test_chain_tampering_is_detected() -> None:
    signer, registry = setup_identity()
    ledger = EvidenceLedger(registry)
    payload = b"one"
    ledger.append(envelope(signer, payload), payload=payload, recorded_at=NOW)
    ledger._entries[0] = replace(ledger._entries[0], previous_hash="FAKE")
    assert ledger.verify_integrity() is False


def test_state_root_is_deterministic_and_live_anchor_is_disabled() -> None:
    signer, registry = setup_identity()
    ledger = EvidenceLedger(registry)
    payload = b"one"
    ledger.append(envelope(signer, payload), payload=payload, recorded_at=NOW)
    first = ledger.state_root()
    second = ledger.state_root()
    assert first == second
    assert len(first) == 64
    with pytest.raises(LiveAnchoringDisabled):
        DisabledAnchor().anchor(root_hash=first, start_sequence=0, end_sequence=0)
