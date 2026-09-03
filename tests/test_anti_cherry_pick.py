from datetime import datetime, timezone

from the_book import journal_merkle_proof, seal_journal, verify_journal_inclusion


NOW = datetime(2026, 9, 2, 19, 20, tzinfo=timezone.utc)


def test_omitting_losing_prediction_changes_committed_history() -> None:
    complete_records = [
        ("PRED-001-WIN", b'{"prediction":"UP","outcome":"WIN"}'),
        ("PRED-002-LOSS", b'{"prediction":"UP","outcome":"LOSS"}'),
        ("PRED-003-WIN", b'{"prediction":"DOWN","outcome":"WIN"}'),
    ]
    complete, complete_leaves = seal_journal(
        journal_id="ZLJ-PRED-WINDOW-001",
        record_type="ZLJ.PREDICTION",
        records=complete_records,
        period_start=NOW,
        period_end=NOW,
        sealed_at=NOW,
        source_ref="vault://zlj/journals/window-001",
    )

    cherry_picked, _ = seal_journal(
        journal_id="ZLJ-PRED-WINDOW-001-CHERRY-PICKED",
        record_type="ZLJ.PREDICTION",
        records=[complete_records[0], complete_records[2]],
        period_start=NOW,
        period_end=NOW,
        sealed_at=NOW,
        source_ref="vault://zlj/journals/window-001-tampered",
    )

    assert complete.record_count == 3
    assert cherry_picked.record_count == 2
    assert complete.merkle_root != cherry_picked.merkle_root

    loss_proof = journal_merkle_proof(complete_leaves, 1)
    assert verify_journal_inclusion(
        record_id="PRED-002-LOSS",
        payload=complete_records[1][1],
        proof=loss_proof,
        expected_root=complete.merkle_root,
    )
    assert not verify_journal_inclusion(
        record_id="PRED-002-LOSS",
        payload=b'{"prediction":"UP","outcome":"WIN"}',
        proof=loss_proof,
        expected_root=complete.merkle_root,
    )


def test_benjamin_abstention_is_part_of_complete_decision_population() -> None:
    decisions = [
        ("DEC-001-ENTER", b'{"action":"ENTER"}'),
        ("DEC-002-NO-TRADE", b'{"action":"NO_TRADE"}'),
        ("DEC-003-EXIT", b'{"action":"EXIT"}'),
    ]
    complete, leaves = seal_journal(
        journal_id="BEN-DEC-WINDOW-001",
        record_type="BENJAMIN.DECISION",
        records=decisions,
        period_start=NOW,
        period_end=NOW,
        sealed_at=NOW,
        source_ref="vault://benjamin/journals/window-001",
    )
    proof = journal_merkle_proof(leaves, 1)

    assert complete.record_count == 3
    assert verify_journal_inclusion(
        record_id="DEC-002-NO-TRADE",
        payload=decisions[1][1],
        proof=proof,
        expected_root=complete.merkle_root,
    )
