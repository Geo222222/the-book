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


T0 = datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc)


def zlj_payload() -> bytes:
    return canonical_json(
        {
            "schema_version": "1.0",
            "intelligence_id": "ZLJ-HAND-001",
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
            "evidence_refs": ["zlj://observation/OBS-HAND-001"],
            "code_version": "zlj-shadow-001",
            "feature_version": "features-v1",
            "invalidation_conditions": ["liquidity deterioration"],
            "known_at": T0.isoformat(),
            "valid_until": (T0 + timedelta(seconds=30)).isoformat(),
        }
    )


def decision_payload(expires_at) -> bytes:
    return canonical_json(
        {
            "schema_version": "1.0",
            "decision_id": "DEC-HAND-001",
            "instrument": "BTC-USD",
            "action": "ENTER",
            "side": "BUY",
            "horizon_ms": 120_000,
            "intended_size": {"value": 0.01, "unit": "BASE"},
            "expected_edge_before_costs_bps": 8.0,
            "expected_edge_after_costs_bps": 4.0,
            "confidence": 0.65,
            "thesis_ref": "vault://benjamin/theses/DEC-HAND-001",
            "invalidation_ref": "vault://benjamin/invalidation/DEC-HAND-001",
            "capital_state_ref": "capital://snapshot/CAP-001",
            "position_state_ref": "position://snapshot/POS-001",
            "reasoner_version": "benjamin-v1-shadow-001",
            "evidence_receipt_ids": ["BOOK-ZLJ-HAND-001"],
            "expires_at": expires_at.isoformat(),
        }
    )


def watchman_payload(*, result: str, evaluated_at, expires_at=None) -> bytes:
    authorized = result == "AUTHORIZE"
    return canonical_json(
        {
            "schema_version": "1.0",
            "governance_id": "RSK-HAND-001" if authorized else "RSK-HAND-BLOCK-001",
            "decision_receipt_id": "BOOK-BEN-HAND-001",
            "decision_id": "DEC-HAND-001",
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
                    "idempotency_key": "a" * 64,
                }
                if authorized
                else None
            ),
            "evaluated_at": evaluated_at.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at is not None else None,
        }
    )


def hand_payload(*, authorization_receipt_id: str, governance_id: str, executed_at) -> bytes:
    return canonical_json(
        {
            "schema_version": "2.0",
            "receipt_id": "EXE-HAND-001",
            "authorization_book_receipt_id": authorization_receipt_id,
            "governance_id": governance_id,
            "capability": "ORDER_EXECUTION",
            "idempotency_key": "a" * 64,
            "instrument": "BTC-USD",
            "side": "BUY",
            "requested_quantity": "0.01",
            "status": "DRY_RUN",
            "venue_order_id": None,
            "executed_quantity": None,
            "average_price": None,
            "executed_at": executed_at.isoformat(),
            "message": "dry-run accepted exact instruction BUY 0.01 BTC-USD",
        }
    )


def setup_book():
    zlj = Ed25519ProducerSigner.generate("ZLJ", "zlj-hand-k1")
    benjamin = Ed25519ProducerSigner.generate("Benjamin", "benjamin-hand-k1")
    watchman = Ed25519ProducerSigner.generate("Watchman", "watchman-hand-k1")
    hand = Ed25519ProducerSigner.generate("The Hand", "hand-k1")
    registry = AuthorityRegistry()
    for producer, signer, prefix in (
        ("ZLJ", zlj, "ZLJ."),
        ("Benjamin", benjamin, "BENJAMIN."),
        ("Watchman", watchman, "WATCHMAN."),
        ("The Hand", hand, "HAND."),
    ):
        registry.register(
            producer=producer,
            key_id=signer.key_id,
            public_key=signer.public_key_bytes,
            allowed_event_prefixes=(prefix,),
        )
    book = BigBook(registry)
    ingest = BookIngestService(book)

    intel = zlj_payload()
    intel_envelope = sign_evidence_v2(
        zlj,
        receipt_id="BOOK-ZLJ-HAND-001",
        event_type="ZLJ.INTELLIGENCE",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="ZLJ-HAND-001",
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
    decision = decision_payload(decision_expiry)
    decision_envelope = sign_evidence_v2(
        benjamin,
        receipt_id="BOOK-BEN-HAND-001",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="DEC-HAND-001",
        occurred_at=decision_time,
        known_at=decision_time,
        produced_at=decision_time,
        valid_from=decision_time,
        valid_until=decision_expiry,
        payload_digest=sha256_hex(decision),
        causation_receipt_id="BOOK-ZLJ-HAND-001",
    )
    ingest.append_idempotent(envelope=decision_envelope.wire(), payload=decision)
    return book, ingest, watchman, hand


def append_watchman_authorization(ingest, watchman):
    evaluated_at = T0 + timedelta(milliseconds=20)
    expires_at = evaluated_at + timedelta(minutes=5)
    payload = watchman_payload(result="AUTHORIZE", evaluated_at=evaluated_at, expires_at=expires_at)
    envelope = sign_evidence_v2(
        watchman,
        receipt_id="BOOK-WATCH-HAND-001",
        event_type="WATCHMAN.AUTHORIZATION",
        evidence_class=EvidenceClass.CONSTITUTIONAL,
        subject_id="RSK-HAND-001",
        occurred_at=evaluated_at,
        known_at=evaluated_at,
        produced_at=evaluated_at,
        source_event_at=T0 + timedelta(milliseconds=10),
        valid_from=evaluated_at,
        valid_until=expires_at,
        payload_digest=sha256_hex(payload),
        causation_receipt_id="BOOK-BEN-HAND-001",
    )
    ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
    return evaluated_at


def test_full_zlj_benjamin_watchman_hand_chain_is_provable() -> None:
    book, ingest, watchman, hand = setup_book()
    evaluated_at = append_watchman_authorization(ingest, watchman)
    executed_at = evaluated_at + timedelta(milliseconds=5)
    payload = hand_payload(
        authorization_receipt_id="BOOK-WATCH-HAND-001",
        governance_id="RSK-HAND-001",
        executed_at=executed_at,
    )
    envelope = sign_evidence_v2(
        hand,
        receipt_id="BOOK-EXE-HAND-001",
        event_type="HAND.EXECUTION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="EXE-HAND-001",
        occurred_at=executed_at,
        known_at=executed_at,
        produced_at=executed_at,
        source_event_at=evaluated_at,
        payload_digest=sha256_hex(payload),
        causation_receipt_id="BOOK-WATCH-HAND-001",
        evidence_receipt_ids=("BOOK-BEN-HAND-001",),
    )

    receipt = ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
    assert receipt["accepted"] is True
    assert receipt["sequence"] == 3
    assert book.entry_count == 4
    assert book.verify_integrity() is True

    replay = ingest.append_idempotent(envelope=envelope.wire(), payload=payload)
    assert replay["sequence"] == 3
    assert replay["entry_hash"] == receipt["entry_hash"]
    assert replay["duplicate_replay"] is True


def test_hand_cannot_bypass_watchman_and_cause_from_benjamin_directly() -> None:
    _, ingest, _, hand = setup_book()
    executed_at = T0 + timedelta(milliseconds=30)
    payload = hand_payload(
        authorization_receipt_id="BOOK-BEN-HAND-001",
        governance_id="RSK-HAND-001",
        executed_at=executed_at,
    )
    envelope = sign_evidence_v2(
        hand,
        receipt_id="BOOK-EXE-HAND-001",
        event_type="HAND.EXECUTION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="EXE-HAND-001",
        occurred_at=executed_at,
        known_at=executed_at,
        produced_at=executed_at,
        payload_digest=sha256_hex(payload),
        causation_receipt_id="BOOK-BEN-HAND-001",
    )
    with pytest.raises(InvalidCausation, match="WATCHMAN.AUTHORIZATION"):
        ingest.append_idempotent(envelope=envelope.wire(), payload=payload)


def test_watchman_block_cannot_be_used_as_hand_execution_authority() -> None:
    _, ingest, watchman, hand = setup_book()
    evaluated_at = T0 + timedelta(milliseconds=20)
    block = watchman_payload(result="BLOCK", evaluated_at=evaluated_at)
    block_envelope = sign_evidence_v2(
        watchman,
        receipt_id="BOOK-WATCH-BLOCK-HAND-001",
        event_type="WATCHMAN.BLOCK",
        evidence_class=EvidenceClass.CONSTITUTIONAL,
        subject_id="RSK-HAND-BLOCK-001",
        occurred_at=evaluated_at,
        known_at=evaluated_at,
        produced_at=evaluated_at,
        payload_digest=sha256_hex(block),
        causation_receipt_id="BOOK-BEN-HAND-001",
    )
    ingest.append_idempotent(envelope=block_envelope.wire(), payload=block)

    executed_at = evaluated_at + timedelta(milliseconds=5)
    execution = hand_payload(
        authorization_receipt_id="BOOK-WATCH-BLOCK-HAND-001",
        governance_id="RSK-HAND-BLOCK-001",
        executed_at=executed_at,
    )
    hand_envelope = sign_evidence_v2(
        hand,
        receipt_id="BOOK-EXE-HAND-001",
        event_type="HAND.EXECUTION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="EXE-HAND-001",
        occurred_at=executed_at,
        known_at=executed_at,
        produced_at=executed_at,
        payload_digest=sha256_hex(execution),
        causation_receipt_id="BOOK-WATCH-BLOCK-HAND-001",
    )
    with pytest.raises(InvalidCausation, match="WATCHMAN.AUTHORIZATION"):
        ingest.append_idempotent(envelope=hand_envelope.wire(), payload=execution)
