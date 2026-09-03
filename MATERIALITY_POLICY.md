# Materiality and Completeness Policy

The Book must preserve institutional accountability without becoming a duplicate data lake.

## Two proof modes

### Individual material receipt

Use an individual Big Book receipt when a fact materially changes or establishes authority, capital intent, governance, execution, ownership, obligation, entitlement, outcome, model qualification, or another fact whose exact causal position must be traversable directly.

Typical Epinnox examples:

- qualified ZLJ intelligence actually used by Benjamin;
- material ZLJ model qualification/demotion or data-quality incident;
- final Benjamin `ENTER`, `HOLD`, `REDUCE`, `EXIT`, or material `NO_TRADE` decision;
- Watchman authorization/block/revocation;
- Hand action/execution/fill/settlement/reconciliation;
- material outcome/evaluation records.

### Journal commitment

Use a journal commitment when the producer must prove a complete high-volume history without turning every record into an individual ledger entry.

Typical examples:

- all ZLJ predictions generated during a qualification window;
- all Benjamin decisions, including abstentions, during a benchmark window;
- other complete producer journals where omission/cherry-picking would distort evaluation.

The producer retains the complete ordered journal in governed storage, computes a leaf from each `record_id + payload_digest`, seals the ordered leaves into a Merkle root, and emits `ZLJ.JOURNAL_COMMITMENT` or `BENJAMIN.JOURNAL_COMMITMENT` to the Big Book.

## Anti-cherry-picking invariant

> A material-case receipt proves a consequential event. A journal commitment proves the surrounding population was not silently rewritten to show only favorable cases.

A committed record can later be disclosed to an authorized verifier with a Merkle inclusion proof without revealing neighboring records.

## Journal ordering

Journal v1 uses `PRODUCER_SEQUENCE`. The source journal must preserve the exact order used to calculate its commitment.

## Source retention

The journal itself remains in The Vault or another governed producer store according to retention policy. The Big Book stores the commitment payload and evidence envelope, not every journal row.

## No automatic public disclosure

A private journal commitment is not automatically projected to the Little Book. Public anchoring or testimony requires explicit disclosure policy.
