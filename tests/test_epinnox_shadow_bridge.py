import json
from datetime import datetime, timedelta, timezone

from the_book import (
    AuthorityRegistry,
    BigBook,
    BookIngestService,
    Ed25519ProducerSigner,
    EvidenceClass,
    canonical_json,
    sha256_hex,
    sign_evidence_v2,
)


T0 = datetime(2026, 9, 2, 19, 10, tzinfo=timezone.utc)


def zlj_payload() -> bytes:
    return canonical_json(
        {
            "schema_version": "1.0",
            "intelligence_id": "ZLJ-INTEL-001",
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
            "code_version": "zlj-shadow-commit-001",
            "feature_version": "features-v1",
            "invalidation_conditions": ["order-flow reversal", "liquidity deterioration"],
            "known_at": T0.isoformat(),
            "valid_until": (T0 + timedelta(seconds=30)).isoformat(),
        }
    )


def benjamin_payload() -> bytes:
    expires = T0 + timedelta(seconds=20)
    return canonical_json(
        {
            "schema_version": "1.0",
            "decision_id": "BEN-DEC-001",
            "instrument": "BTC-USD",
            "action": "ENTER",
            "side": "BUY",
            "horizon_ms": 120_000,
            "intended_size": {"value": 0.01, "unit": "BASE"},
            "expected_edge_before_costs_bps": 8.4,
            "expected_edge_after_costs_bps": 4.1,
            "confidence": 0.67,
            "thesis_ref": "vault://benjamin/theses/BEN-DEC-001",
            "invalidation_ref": "vault://benjamin/invalidation/BEN-DEC-001",
            "capital_state_ref": "capital://snapshot/CAP-001",
            "position_state_ref": "position://snapshot/POS-001",
            "reasoner_version": "benjamin-v1-shadow-001",
            "evidence_receipt_ids": ["BOOK-ZLJ-001"],
            "expires_at": expires.isoformat(),
        }
    )


def test_complete_zlj_to_benjamin_shadow_case_is_causally_provable() -> None:
    zlj = Ed25519ProducerSigner.generate("ZLJ", "zlj-shadow-k1")
    benjamin = Ed25519ProducerSigner.generate("Benjamin", "benjamin-shadow-k1")
    registry = AuthorityRegistry()
    registry.register(
        producer="ZLJ",
        key_id="zlj-shadow-k1",
        public_key=zlj.public_key_bytes,
        allowed_event_prefixes=("ZLJ.",),
    )
    registry.register(
        producer="Benjamin",
        key_id="benjamin-shadow-k1",
        public_key=benjamin.public_key_bytes,
        allowed_event_prefixes=("BENJAMIN.",),
    )
    book = BigBook(registry)
    ingest = BookIngestService(book)

    intel_payload = zlj_payload()
    intel_envelope = sign_evidence_v2(
        zlj,
        receipt_id="BOOK-ZLJ-001",
        event_type="ZLJ.INTELLIGENCE",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="ZLJ-INTEL-001",
        occurred_at=T0,
        source_event_at=T0 - timedelta(milliseconds=40),
        known_at=T0,
        produced_at=T0,
        valid_from=T0,
        valid_until=T0 + timedelta(seconds=30),
        payload_digest=sha256_hex(intel_payload),
        payload_ref="vault://zlj/intelligence/ZLJ-INTEL-001",
        correlation_id="EPX-SHADOW-001",
    )
    intel_receipt = ingest.append_idempotent(envelope=intel_envelope.wire(), payload=intel_payload)
    assert intel_receipt["accepted"] is True
    assert intel_receipt["sequence"] == 0

    decision_time = T0 + timedelta(milliseconds=25)
    decision_payload = benjamin_payload()
    decision_envelope = sign_evidence_v2(
        benjamin,
        receipt_id="BOOK-BEN-001",
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        subject_id="BEN-DEC-001",
        occurred_at=decision_time,
        known_at=decision_time,
        produced_at=decision_time,
        valid_from=decision_time,
        valid_until=T0 + timedelta(seconds=20),
        payload_digest=sha256_hex(decision_payload),
        payload_ref="vault://benjamin/decisions/BEN-DEC-001",
        correlation_id="EPX-SHADOW-001",
        causation_receipt_id="BOOK-ZLJ-001",
    )
    decision_receipt = ingest.append_idempotent(
        envelope=decision_envelope.wire(),
        payload=decision_payload,
    )

    assert decision_receipt["accepted"] is True
    assert decision_receipt["sequence"] == 1
    assert book.entry_count == 2
    assert book.verify_integrity() is True

    replay = ingest.append_idempotent(envelope=decision_envelope.wire(), payload=decision_payload)
    assert replay["sequence"] == 1
    assert replay["entry_hash"] == decision_receipt["entry_hash"]
    assert replay["duplicate_replay"] is True
