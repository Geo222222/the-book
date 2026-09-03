from datetime import datetime, timedelta, timezone

import pytest

from the_book import (
    AuthorityRegistry,
    BigBook,
    BookIngestService,
    Ed25519ProducerSigner,
    EvidenceClass,
    InvalidCausation,
    canonical_json,
    sha256_hex,
    sign_evidence_v2,
)


T0 = datetime(2026, 9, 2, 18, 0, tzinfo=timezone.utc)


def zlj_payload() -> bytes:
    return canonical_json(
        {
            "schema_version": "1.0",
            "intelligence_id": "ZLJ-WATCH-001",
            "instrument": "BTC-USD",
            "horizon_ms": 30_000,
            "proposition": "qualified market evidence",
            "probability": 0.7,
            "expected_move_bps": 10.0,
            "market_state": "liquid_directional",
            "regime": "directional_liquid",
            "model_ids": ["microstructure_model_04"],
            "qualification_state": "QUALIFIED",
            "competence_refs": ["zlj://competence/microstructure_model_04"],
            "evidence_refs": ["zlj://observation/OBS-WATCH-001"],
            "code_version": "zlj-shadow-001",
            "feature_version": "features-v1",
            "invalidation_conditions": ["liquidity deterioration"],
            "known_at": T0.isoformat(),
            "valid_until": (T0 + timedelta(seconds=30)).isoformat(),
        }
    )


def benjamin_payload(*, decision_id: str, evidence_receipt_id: str, expires_at) -> bytes:
    return canonical_json(
        {
            "schema_version": "1.0",
            "decision_id": decision_id,
            "instrument": "BTC-USD",
            "action": "ENTER",
            "side": "BUY",
            "horizon_ms": 120_000,
            "intended_size": {"value": 0.01, "unit": "BASE"},
            "expected_edge_before_costs_bps": 8.0,
            "expected_edge_after_costs_bps": 4.0,
            "confidence": 0.65,
            "thesis_ref": "vault://benjamin/theses/DEC-WATCH-001",
            "invalidation_ref": "vault://benjamin/invalidation/DEC-WATCH-001",
            "capital_state_ref": "capital://snapshot/CAP-001",
            "position_state_ref": "position://snapshot/POS-001",
            "reasoner_version": "benjamin-v1-shadow-001",
            "evidence_receipt_ids": [evidence_receipt_id],
            "expires_at": expires_at.isoformat(),
        }
    )


def watchman_payload(
    *,
    governance_id: str,
    decision_receipt_id: str,
    decision_id: str,
    result: str,
    evaluated_at,
    expires_at=None,
) -> bytes:
    authorized = result == "AUTHORIZE"
    return canonical_json(
        {
            "schema_version": "1.0",
            "governance_id": governance_id,
            "decision_receipt_id": decision_receipt_id,
            "decision_id": decision_id,
            "result": result,
            "policy_version": "watchman-b0-v1",
            "checks": [
                {
                    "check_id": "B0_POLICY_PASS" if authorized else "ORDER_QUANTITY_LIMIT_EXCEEDED",
                    "status": "PASS" if authorized else "BLOCK",
                    "reason": "B0_POLICY_PASS" if authorized else "ORDER_QUANTITY_LIMIT_EXCEEDED",
                }
            ],
            "capability_constraints": (
                {
                    "capability": "ORDER_EXECUTION",
                    "instrument": "BTC-USD",
                    "side": "BUY",
                    "quantity": "0.01",
                    "idempotency_key": "idem-watch-001",
                }
                if authorized
                else None
            ),
            "evaluated_at": evaluated_at.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at is not None else None,
        }
    )


def setup_chain():
    zlj = Ed25519ProducerSigner.generate("ZLJ", "zlj-watch-k1")
    benjamin = Ed25519ProducerSigner.generate("Benjamin", "benjamin-watch-k1")
    watchman = Ed25519ProducerSigner.generate("Watchman", "watchman-k1")
    registry = AuthorityRegistry()
    registry.register(
        producer="ZLJ",
        key_id=zlj.key_id,
        public_key=zlj.public_key_bytes,
        allowed_event_prefixes=("ZLJ.",),
    )
    registry.register(
        producer="Benjamin",
        key_id=benjamin.key_id,
        public_key=benjamin.public_key_bytes,
        allowed_event_prefixes=("BENJAMIN.",),
    )
    registry.register(
        producer="Watchman",
        key_id=watchman.key_id,
        public_key=watchman.public_key_bytes,
        allowed_event_prefixes=("WATCHMAN.",),
    )
    book = BigBook(registry)
    ingest = BookIngestService(book)

    intel = zlj_payload()
    intel_envelope = sign_evidence_v2(
        zlj,
        receipt_id="BOOK-ZLJ-WATCH-001",
        event_type="ZLJ.INTELLIGENCE",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="ZLJ-WATCH-001",
        occurred_at=T0,
        known_at=T0,
        produced_at=T0,
        valid_from=T0,
        valid_until=T0 + timedelta(seconds=30),
        payload_digest=sha256_hex(intel),
    )
    ingest.append_idempotent(envelope=intel_envelope.wire(), payload=intel)

    decision_time = T0 + timedelta(milliseconds=10)
    decision_expiry = T0 + timedelta(seconds=20)
    decision = benjamin_payload(
        decision_id="DEC-WATCH-001",
        evidence_receipt_id="BOOK-ZLJ-WATCH-001",
        expires_at=decision_expiry,
    )
    decision_envelope = sign_evidence_v2(
        benjamin,
        receipt_id="BOOK-BEN-WATCH-001",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-WATCH-001",
        occurred_at=decision_time,
        known_at=decision_time,
        produced_at=decision_time,
        valid_from=decision_time,
        valid_until=decision_expiry,
        payload_digest=sha256_hex(decision),
        causation_receipt_id="BOOK-ZLJ-WATCH-001",
    )
    ingest.append_idempotent(envelope=decision_envelope.wire(), payload=decision)
    return book, ingest, zlj, benjamin, watchman


def test_benjamin_decision_to_watchman_authorization_is_causally_provable() -> None:
    book, ingest, _, _, watchman = setup_chain()
    evaluated_at = T0 + timedelta(milliseconds=20)
    expires_at = evaluated_at + timedelta(minutes=5)
    payload = watchman_payload(
        governance_id="RSK-WATCH-AUTH-001",
        decision_receipt_id="BOOK-BEN-WATCH-001",
        decision_id="DEC-WATCH-001",
        result="AUTHORIZE",
        evaluated_at=evaluated_at,
        expires_at=expires_at,
    )
    envelope = sign_evidence_v2(
        watchman,
        receipt_id="BOOK-WATCH-AUTH-001",
        event_type="WATCHMAN.AUTHORIZATION",
        evidence_class=EvidenceClass.CONSTITUTIONAL,
        subject_id="RSK-WATCH-AUTH-001",
        occurred_at=evaluated_at,
        known_at=evaluated_at,
        produced_at=evaluated_at,
        source_event_at=T0 + timedelta(milliseconds=10),
        valid_from=evaluated_at,
        valid_until=expires_at,
        payload_digest=sha256_hex(payload),
        causation_receipt_id="BOOK-BEN-WATCH-001",
    )

    receipt = ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
    assert receipt["accepted"] is True
    assert receipt["sequence"] == 2
    assert book.entry_count == 3
    assert book.verify_integrity() is True

    replay = ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
    assert replay["sequence"] == 2
    assert replay["entry_hash"] == receipt["entry_hash"]
    assert replay["duplicate_replay"] is True


def test_benjamin_decision_to_watchman_block_is_provable_without_capability() -> None:
    book, ingest, _, _, watchman = setup_chain()
    evaluated_at = T0 + timedelta(milliseconds=20)
    payload = watchman_payload(
        governance_id="RSK-WATCH-BLOCK-001",
        decision_receipt_id="BOOK-BEN-WATCH-001",
        decision_id="DEC-WATCH-001",
        result="BLOCK",
        evaluated_at=evaluated_at,
    )
    envelope = sign_evidence_v2(
        watchman,
        receipt_id="BOOK-WATCH-BLOCK-001",
        event_type="WATCHMAN.BLOCK",
        evidence_class=EvidenceClass.CONSTITUTIONAL,
        subject_id="RSK-WATCH-BLOCK-001",
        occurred_at=evaluated_at,
        known_at=evaluated_at,
        produced_at=evaluated_at,
        source_event_at=T0 + timedelta(milliseconds=10),
        payload_digest=sha256_hex(payload),
        causation_receipt_id="BOOK-BEN-WATCH-001",
    )

    receipt = ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
    assert receipt["accepted"] is True
    assert receipt["sequence"] == 2
    assert book.verify_integrity() is True


def test_watchman_cannot_claim_zlj_receipt_as_its_benjamin_decision_parent() -> None:
    _, ingest, _, _, watchman = setup_chain()
    evaluated_at = T0 + timedelta(milliseconds=20)
    payload = watchman_payload(
        governance_id="RSK-WATCH-FORGED-PARENT",
        decision_receipt_id="BOOK-ZLJ-WATCH-001",
        decision_id="DEC-WATCH-001",
        result="BLOCK",
        evaluated_at=evaluated_at,
    )
    envelope = sign_evidence_v2(
        watchman,
        receipt_id="BOOK-WATCH-FORGED-PARENT",
        event_type="WATCHMAN.BLOCK",
        evidence_class=EvidenceClass.CONSTITUTIONAL,
        subject_id="RSK-WATCH-FORGED-PARENT",
        occurred_at=evaluated_at,
        known_at=evaluated_at,
        produced_at=evaluated_at,
        payload_digest=sha256_hex(payload),
        causation_receipt_id="BOOK-ZLJ-WATCH-001",
    )

    with pytest.raises(InvalidCausation, match="BENJAMIN.DECISION"):
        ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
