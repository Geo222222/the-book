from datetime import datetime, timezone

import pytest

from the_book import (
    AuthorityRegistry,
    BigBook,
    DuplicateReceipt,
    Ed25519ProducerSigner,
    EvidenceClass,
    sha256_hex,
    sign_evidence,
)


NOW = datetime(2026, 9, 2, 19, 0, tzinfo=timezone.utc)


def setup_book():
    signer = Ed25519ProducerSigner.generate("LegacyProducer", "legacy-k1")
    registry = AuthorityRegistry()
    registry.register(
        producer="LegacyProducer",
        key_id="legacy-k1",
        public_key=signer.public_key_bytes,
        allowed_event_prefixes=("LEGACY.",),
    )
    return signer, BigBook(registry)


def test_exact_replay_returns_original_acceptance_receipt() -> None:
    signer, book = setup_book()
    payload = b"same"
    envelope = sign_evidence(
        signer,
        receipt_id="R-1",
        event_type="LEGACY.EVENT",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="S-1",
        occurred_at=NOW,
        payload_digest=sha256_hex(payload),
    )
    first = book.append_idempotent(envelope, payload=payload, recorded_at=NOW)
    replay = book.append_idempotent(envelope, payload=payload, recorded_at=NOW)

    assert first.sequence == replay.sequence == 0
    assert first.entry_hash == replay.entry_hash
    assert first.duplicate_replay is False
    assert replay.duplicate_replay is True
    assert book.entry_count == 1


def test_receipt_id_reuse_with_changed_evidence_is_rejected() -> None:
    signer, book = setup_book()
    first_payload = b"one"
    first = sign_evidence(
        signer,
        receipt_id="R-1",
        event_type="LEGACY.EVENT",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="S-1",
        occurred_at=NOW,
        payload_digest=sha256_hex(first_payload),
    )
    book.append_idempotent(first, payload=first_payload, recorded_at=NOW)

    second_payload = b"two"
    changed = sign_evidence(
        signer,
        receipt_id="R-1",
        event_type="LEGACY.EVENT",
        evidence_class=EvidenceClass.ANALYTICAL,
        subject_id="S-2",
        occurred_at=NOW,
        payload_digest=sha256_hex(second_payload),
    )
    with pytest.raises(DuplicateReceipt):
        book.append_idempotent(changed, payload=second_payload, recorded_at=NOW)
