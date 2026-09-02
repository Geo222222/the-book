from datetime import datetime, timezone

from the_book import (
    AuthorityRegistry,
    BigBook,
    Ed25519ProducerSigner,
    EvidenceClass,
    journal_merkle_proof,
    seal_journal,
    sha256_hex,
    sign_evidence_v2,
    verify_journal_inclusion,
)


NOW = datetime(2026, 9, 2, 18, 30, tzinfo=timezone.utc)


def test_journal_commitment_proves_inclusion_without_exposing_neighbors() -> None:
    records = [("PRED-001", b"one"), ("PRED-002", b"two"), ("PRED-003", b"three")]
    commitment, leaves = seal_journal(
        journal_id="ZLJ-PRED-20260902-01",
        record_type="ZLJ.PREDICTION",
        records=records,
        period_start=NOW,
        period_end=NOW,
        sealed_at=NOW,
        source_ref="vault://zlj/journals/20260902-01",
    )
    proof = journal_merkle_proof(leaves, 1)

    assert verify_journal_inclusion(
        record_id="PRED-002",
        payload=b"two",
        proof=proof,
        expected_root=commitment.merkle_root,
    )
    assert not verify_journal_inclusion(
        record_id="PRED-002",
        payload=b"tampered",
        proof=proof,
        expected_root=commitment.merkle_root,
    )


def test_zlj_journal_commitment_is_a_valid_book_event() -> None:
    records = [("PRED-001", b"one"), ("PRED-002", b"two")]
    commitment, _ = seal_journal(
        journal_id="ZLJ-PRED-20260902-01",
        record_type="ZLJ.PREDICTION",
        records=records,
        period_start=NOW,
        period_end=NOW,
        sealed_at=NOW,
        source_ref="vault://zlj/journals/20260902-01",
    )
    payload = commitment.payload_bytes()

    signer = Ed25519ProducerSigner.generate("ZLJ", "zlj-k1")
    registry = AuthorityRegistry()
    registry.register(
        producer="ZLJ",
        key_id="zlj-k1",
        public_key=signer.public_key_bytes,
        allowed_event_prefixes=("ZLJ.",),
    )
    envelope = sign_evidence_v2(
        signer,
        receipt_id="BOOK-ZLJ-JOURNAL-001",
        event_type="ZLJ.JOURNAL_COMMITMENT",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id=commitment.journal_id,
        occurred_at=NOW,
        known_at=NOW,
        produced_at=NOW,
        payload_digest=sha256_hex(payload),
        payload_ref="vault://book/commitments/ZLJ-PRED-20260902-01",
    )
    ledger = BigBook(registry)
    ledger.append(envelope, payload=payload, recorded_at=NOW)

    assert ledger.entry_count == 1
    assert ledger.verify_integrity()
