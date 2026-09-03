import json
from datetime import datetime, timedelta, timezone

import pytest

from the_book import (
    AuthorityRegistry,
    BigBook,
    Ed25519ProducerSigner,
    EvidenceClass,
    InvalidDomainPayload,
    InvalidEvidenceDependency,
    InvalidRecordingTime,
    sha256_hex,
    sign_evidence,
    sign_evidence_v2,
)


NOW = datetime(2026, 9, 2, 18, 0, tzinfo=timezone.utc)


def encode(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def zlj_payload(intelligence_id: str, *, valid_until: datetime | None = None) -> bytes:
    return encode(
        {
            "schema_version": "1.0",
            "intelligence_id": intelligence_id,
            "instrument": "BTC-USD",
            "horizon_ms": 30_000,
            "proposition": "price_up >= 8bps",
            "probability": 0.71,
            "expected_move_bps": 11.4,
            "market_state": "liquid_directional",
            "regime": "directional_liquid",
            "model_ids": ["microstructure_model_04"],
            "qualification_state": "QUALIFIED",
            "competence_refs": ["zlj://competence/microstructure_model_04"],
            "evidence_refs": ["zlj://observation/OBS-001"],
            "code_version": "commit-zlj-001",
            "feature_version": "features-v1",
            "invalidation_conditions": ["order-flow reversal"],
            "known_at": NOW.isoformat(),
            "valid_until": valid_until.isoformat() if valid_until else None,
        }
    )


def benjamin_payload(
    *,
    evidence_receipt_ids: list[str],
    expires_at: datetime,
    action: str = "NO_TRADE",
) -> bytes:
    return encode(
        {
            "schema_version": "1.0",
            "decision_id": "DEC-001",
            "instrument": "BTC-USD",
            "action": action,
            "side": "NONE" if action in {"NO_TRADE", "HOLD"} else "BUY",
            "horizon_ms": 120_000,
            "intended_size": {"value": 0.0 if action == "NO_TRADE" else 0.01, "unit": "BASE"},
            "expected_edge_before_costs_bps": 8.4,
            "expected_edge_after_costs_bps": 4.1,
            "confidence": 0.67,
            "thesis_ref": "vault://benjamin/theses/DEC-001",
            "invalidation_ref": "vault://benjamin/invalidation/DEC-001",
            "capital_state_ref": "capital://snapshot/CAP-001",
            "position_state_ref": "position://snapshot/POS-001",
            "reasoner_version": "benjamin-v1-shadow-001",
            "evidence_receipt_ids": evidence_receipt_ids,
            "expires_at": expires_at.isoformat(),
        }
    )


def register(registry: AuthorityRegistry, signer: Ed25519ProducerSigner, prefix: str) -> None:
    registry.register(
        producer=signer.producer,
        key_id=signer.key_id,
        public_key=signer.public_key_bytes,
        allowed_event_prefixes=(prefix,),
    )


def append_zlj(ledger: BigBook, signer: Ed25519ProducerSigner, receipt_id: str) -> None:
    subject_id = f"INTEL-{receipt_id}"
    payload = zlj_payload(subject_id)
    envelope = sign_evidence_v2(
        signer,
        receipt_id=receipt_id,
        event_type="ZLJ.INTELLIGENCE",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id=subject_id,
        occurred_at=NOW,
        known_at=NOW,
        produced_at=NOW,
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

    expires_at = NOW + timedelta(seconds=30)
    payload = benjamin_payload(evidence_receipt_ids=["ZLJ-R1", "ZLJ-R2"], expires_at=expires_at)
    decision = sign_evidence_v2(
        benjamin,
        receipt_id="BEN-R1",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-001",
        occurred_at=NOW,
        known_at=NOW,
        produced_at=NOW,
        valid_until=expires_at,
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
    expires_at = NOW + timedelta(seconds=30)
    payload = benjamin_payload(evidence_receipt_ids=["MISSING-R1"], expires_at=expires_at)
    decision = sign_evidence_v2(
        benjamin,
        receipt_id="BEN-R1",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-001",
        occurred_at=NOW,
        known_at=NOW,
        produced_at=NOW,
        valid_until=expires_at,
        payload_digest=sha256_hex(payload),
        evidence_receipt_ids=("MISSING-R1",),
    )

    with pytest.raises(InvalidEvidenceDependency):
        ledger.append(decision, payload=payload, recorded_at=NOW)


def test_v2_rejects_payload_lineage_that_disagrees_with_envelope() -> None:
    registry = AuthorityRegistry()
    zlj = Ed25519ProducerSigner.generate("ZLJ", "zlj-k1")
    benjamin = Ed25519ProducerSigner.generate("Benjamin", "benjamin-k1")
    register(registry, zlj, "ZLJ.")
    register(registry, benjamin, "BENJAMIN.")
    ledger = BigBook(registry)
    append_zlj(ledger, zlj, "ZLJ-R1")
    expires_at = NOW + timedelta(seconds=30)
    payload = benjamin_payload(evidence_receipt_ids=[], expires_at=expires_at)
    decision = sign_evidence_v2(
        benjamin,
        receipt_id="BEN-R1",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-001",
        occurred_at=NOW,
        known_at=NOW,
        produced_at=NOW,
        valid_until=expires_at,
        payload_digest=sha256_hex(payload),
        causation_receipt_id="ZLJ-R1",
    )

    with pytest.raises(InvalidDomainPayload):
        ledger.append(decision, payload=payload, recorded_at=NOW)


def test_v2_rejects_recording_before_production() -> None:
    registry = AuthorityRegistry()
    zlj = Ed25519ProducerSigner.generate("ZLJ", "zlj-k1")
    register(registry, zlj, "ZLJ.")
    ledger = BigBook(registry)
    produced_at = NOW + timedelta(seconds=1)
    payload = zlj_payload("PRED-001")
    prediction = sign_evidence_v2(
        zlj,
        receipt_id="ZLJ-R1",
        event_type="ZLJ.PREDICTION",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="PRED-001",
        occurred_at=NOW,
        known_at=NOW,
        produced_at=produced_at,
        payload_digest=sha256_hex(payload),
    )

    with pytest.raises(InvalidRecordingTime):
        ledger.append(prediction, payload=payload, recorded_at=NOW)


def test_v2_signing_body_binds_knowability_and_validity() -> None:
    signer = Ed25519ProducerSigner.generate("ZLJ", "zlj-k1")
    valid_until = NOW + timedelta(seconds=30)
    payload = zlj_payload("PRED-001", valid_until=valid_until)
    envelope = sign_evidence_v2(
        signer,
        receipt_id="ZLJ-R1",
        event_type="ZLJ.PREDICTION",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="PRED-001",
        occurred_at=NOW,
        source_event_at=NOW - timedelta(milliseconds=50),
        known_at=NOW,
        produced_at=NOW,
        valid_from=NOW,
        valid_until=valid_until,
        payload_digest=sha256_hex(payload),
    )
    body = envelope.signing_body()
    assert body["known_at"] == NOW.isoformat()
    assert body["produced_at"] == NOW.isoformat()
    assert body["valid_until"] == valid_until.isoformat()


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
    assert "known_at" not in legacy.signing_body()
