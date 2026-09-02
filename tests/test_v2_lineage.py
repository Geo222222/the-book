from datetime import datetime, timezone

import pytest

from the_book import (
    AuthorityRegistry,
    BigBook,
    Ed25519ProducerSigner,
    EvidenceClass,
    InvalidEvidenceDependency,
    sha256_hex,
    sign_evidence,
    sign_evidence_v2,
)


NOW = datetime(2026, 9, 2, 18, 0, tzinfo=timezone.utc)


def register(registry: AuthorityRegistry, signer: Ed25519ProducerSigner, prefix: str) -> None:
    registry.register(
        producer=signer.producer,
        key_id=signer.key_id,
        public_key=signer.public_key_bytes,
        allowed_event_prefixes=(prefix,),
    )


def append_zlj(ledger: BigBook, signer: Ed25519ProducerSigner, receipt_id: str) -> None:
    payload = receipt_id.encode()
    envelope = sign_evidence_v2(
        signer,
        receipt_id=receipt_id,
        event_type="ZLJ.INTELLIGENCE",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id=f"INTEL-{receipt_id}",
        occurred_at=NOW,
        payload_digest=sha256_hex(payload),
        payload_ref=f"vault://zlj/{receipt_id}",
        correlation_id="CASE-001",
    )
    ledger.append(envelope, payload=payload, recorded_at=NOW)


def test_v2_decision_can_bind_primary_cause_and_multiple_evidence_dependencies() -> None:
    registry = AuthorityRegistry()
    zlj = Ed25519ProducerSigner.generate("ZLJ", "zlj-k1")
    benjamin = Ed25519ProducerSigner.generate("Benjamin", "benjamin-k1")
    register(registry, zlj, "ZLJ.")
    register(registry, benjamin, "BENJAMIN.")
    ledger = BigBook(registry)

    append_zlj(ledger, zlj, "ZLJ-R1")
    append_zlj(ledger, zlj, "ZLJ-R2")

    payload = b'{"decision":"NO_TRADE"}'
    decision = sign_evidence_v2(
        benjamin,
        receipt_id="BEN-R1",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-001",
        occurred_at=NOW,
        payload_digest=sha256_hex(payload),
        payload_ref="vault://benjamin/DEC-001",
        correlation_id="CASE-001",
        causation_receipt_id="ZLJ-R1",
        evidence_receipt_ids=("ZLJ-R2",),
    )

    entry = ledger.append(decision, payload=payload, recorded_at=NOW)
    assert entry.envelope.causation_receipt_id == "ZLJ-R1"
    assert entry.envelope.evidence_receipt_ids == ("ZLJ-R2",)
    assert ledger.verify_integrity() is True


def test_v2_rejects_missing_evidence_dependency() -> None:
    registry = AuthorityRegistry()
    benjamin = Ed25519ProducerSigner.generate("Benjamin", "benjamin-k1")
    register(registry, benjamin, "BENJAMIN.")
    ledger = BigBook(registry)
    payload = b"decision"
    decision = sign_evidence_v2(
        benjamin,
        receipt_id="BEN-R1",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-001",
        occurred_at=NOW,
        payload_digest=sha256_hex(payload),
        evidence_receipt_ids=("MISSING-R1",),
    )

    with pytest.raises(InvalidEvidenceDependency):
        ledger.append(decision, payload=payload, recorded_at=NOW)


def test_v1_1_signing_shape_remains_legacy_compatible() -> None:
    signer = Ed25519ProducerSigner.generate("Benjamin", "benjamin-k1")
    legacy = sign_evidence(
        signer,
        receipt_id="LEGACY-R1",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-LEGACY",
        occurred_at=NOW,
        payload_digest=sha256_hex(b"legacy"),
    )
    assert legacy.schema_version == "1.1"
    assert "evidence_receipt_ids" not in legacy.signing_body()
