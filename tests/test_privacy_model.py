from datetime import datetime, timedelta, timezone

import pytest

from the_book import (
    AccessDenied,
    AuthorityRegistry,
    BigBook,
    DisclosurePolicy,
    DisclosureRejected,
    Ed25519ProducerSigner,
    EvidenceClass,
    LittleBook,
    PrivacyClass,
    SecretPayloadRejected,
    sha256_hex,
    sign_scoped_evidence,
    verify_public_record,
)


NOW = datetime(2026, 9, 1, 13, 30, tzinfo=timezone.utc)


def setup_book():
    signer = Ed25519ProducerSigner.generate("Benjamin", "benjamin-k1")
    registry = AuthorityRegistry()
    registry.register(
        producer="Benjamin",
        key_id="benjamin-k1",
        public_key=signer.public_key_bytes,
        allowed_event_prefixes=("BENJAMIN.",),
    )
    return signer, BigBook(registry)


def proof(
    signer,
    *,
    receipt_id="RCP-1",
    privacy_class=PrivacyClass.CONFIDENTIAL_EVIDENCE,
    visibility_scope=("BENJAMIN_STEWARD",),
    payload_ref="vault://decisions/DEC-1",
):
    payload = b'{"decision":"APPROVED","private_amount":"25000"}'
    return sign_scoped_evidence(
        signer,
        receipt_id=receipt_id,
        event_type="BENJAMIN.DECISION",
        evidence_class=EvidenceClass.ECONOMIC,
        privacy_class=privacy_class,
        subject_id="DEC-1",
        occurred_at=NOW,
        payload_digest=sha256_hex(payload),
        payload_ref=payload_ref,
        visibility_scope=visibility_scope,
        correlation_id="MATTER-1",
    ), payload


def test_big_book_enforces_internal_least_privilege() -> None:
    signer, book = setup_book()
    envelope, payload = proof(signer)
    entry = book.append(envelope, payload=payload, recorded_at=NOW)

    assert book.get(entry.envelope.receipt_id, principal="BENJAMIN_STEWARD") == entry
    with pytest.raises(AccessDenied):
        book.get(entry.envelope.receipt_id, principal="UNRELATED_FAMILY_MEMBER")


def test_big_book_has_no_unrestricted_entry_enumeration_api() -> None:
    _, book = setup_book()
    assert not hasattr(book, "entries")


def test_participant_proof_can_be_scoped_to_named_participant() -> None:
    signer, book = setup_book()
    envelope, payload = proof(
        signer,
        privacy_class=PrivacyClass.PARTICIPANT_PROOF,
        visibility_scope=("BENJAMIN_STEWARD", "participant:9271"),
    )
    entry = book.append(envelope, payload=payload, recorded_at=NOW)

    assert book.get(entry.envelope.receipt_id, principal="participant:9271") == entry
    with pytest.raises(AccessDenied):
        book.get(entry.envelope.receipt_id, principal="participant:OTHER")


def test_secret_regulated_raw_source_bytes_never_enter_big_book() -> None:
    signer, book = setup_book()
    envelope, payload = proof(
        signer,
        privacy_class=PrivacyClass.SECRET_REGULATED,
        visibility_scope=("IDENTITY_VAULT",),
        payload_ref="vault://identity/DOC-1",
    )
    with pytest.raises(SecretPayloadRejected):
        book.append(envelope, payload=payload, recorded_at=NOW)

    entry = book.append(envelope, recorded_at=NOW)
    assert entry.envelope.payload_digest == sha256_hex(payload)
    assert not hasattr(entry, "payload")


def test_secret_regulated_cannot_reference_public_storage() -> None:
    signer, _ = setup_book()
    with pytest.raises(ValueError):
        proof(
            signer,
            privacy_class=PrivacyClass.SECRET_REGULATED,
            visibility_scope=("IDENTITY_VAULT",),
            payload_ref="https://example.com/identity.pdf",
        )


def state_commitment(signer, book, little):
    return little.publish_state_commitment(
        signer=signer,
        commitment_id="STATE-1",
        state_epoch="2026-09-01",
        merkle_root=book.state_root(),
        issued_at=NOW,
    )


def test_little_book_state_commitment_receives_root_not_private_entries() -> None:
    signer, book = setup_book()
    envelope, payload = proof(signer)
    book.append(envelope, payload=payload, recorded_at=NOW)

    little = LittleBook(DisclosurePolicy(allowed_claim_types=frozenset({"AUTHORITY_VALID"})))
    commitment = state_commitment(signer, book, little)

    wire = commitment.wire()
    assert wire["merkle_root"] == book.state_root()
    assert wire["state_epoch"] == "2026-09-01"
    assert "start_sequence" not in wire
    assert "end_sequence" not in wire
    assert "payload_ref" not in wire
    assert "subject_id" not in wire
    assert "private_amount" not in str(wire)
    assert verify_public_record(commitment, signer.public_key_bytes) is True


def test_little_book_requires_explicit_approved_public_claim() -> None:
    signer, book = setup_book()
    envelope, payload = proof(signer)
    book.append(envelope, payload=payload, recorded_at=NOW)

    little = LittleBook(DisclosurePolicy(allowed_claim_types=frozenset({"AUTHORITY_VALID"})))
    state = state_commitment(signer, book, little)

    with pytest.raises(DisclosureRejected):
        little.publish_attestation(
            signer=signer,
            attestation_id="PUB-1",
            claim_type="PRIVATE_PORTFOLIO_EXPORT",
            claim="publish everything",
            evidence_commitment=envelope.payload_digest,
            big_book_root=state.merkle_root,
            issued_at=NOW,
        )


def test_little_book_named_subjects_are_opt_in() -> None:
    signer, book = setup_book()
    envelope, payload = proof(signer)
    book.append(envelope, payload=payload, recorded_at=NOW)
    little = LittleBook(DisclosurePolicy(allowed_claim_types=frozenset({"AUTHORITY_VALID"})))
    state = state_commitment(signer, book, little)

    with pytest.raises(DisclosureRejected):
        little.publish_attestation(
            signer=signer,
            attestation_id="PUB-1",
            claim_type="AUTHORITY_VALID",
            claim="Treasury signatory authority is valid",
            public_subject="person:123",
            evidence_commitment=envelope.payload_digest,
            big_book_root=state.merkle_root,
            issued_at=NOW,
            expires_at=NOW + timedelta(days=365),
        )


def test_explicit_public_attestation_contains_testimony_not_big_book_evidence() -> None:
    signer, book = setup_book()
    envelope, payload = proof(signer)
    book.append(envelope, payload=payload, recorded_at=NOW)
    little = LittleBook(
        DisclosurePolicy(
            allowed_claim_types=frozenset({"AUTHORITY_VALID"}),
            allow_named_subjects=True,
        )
    )
    state = state_commitment(signer, book, little)
    attestation = little.publish_attestation(
        signer=signer,
        attestation_id="PUB-1",
        claim_type="AUTHORITY_VALID",
        claim="Treasury signatory authority is valid",
        public_subject="person:123",
        evidence_commitment=envelope.payload_digest,
        big_book_root=state.merkle_root,
        issued_at=NOW,
        expires_at=NOW + timedelta(days=365),
    )

    wire = attestation.wire()
    assert wire["public_subject"] == "person:123"
    assert "payload_ref" not in wire
    assert "correlation_id" not in wire
    assert "causation_receipt_id" not in wire
    assert "private_amount" not in str(wire)
    assert verify_public_record(attestation, signer.public_key_bytes) is True
