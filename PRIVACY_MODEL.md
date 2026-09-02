# The Book Privacy Model

## Governing doctrine

> **Everything material must be provable. Not everything that happens must be permanently exposed.**

Within Epinnox:

> **ZLJ sees. Benjamin decides. Watchman governs. The Hand executes. The Book remembers and proves.**

The Book exists to preserve authoritative evidence/proof lineage about institutional history. It is not a dumping ground for raw evidence, personal data, strategy, credentials, private correspondence, model internals, or regulated identifiers, and it does not become the owner of another organ's domain truth merely because it stores proof of it.

Legitimacy comes from provable authority, contracts, accounting, governance, reproducible records, and evidence of actions. Blockchain is a possible integrity mechanism; it is not the source of legitimacy.

## The three storage/trust systems

### The Vault

The Vault holds underlying evidence that requires access controls or retention policy: contracts, statements, identity documents, valuations, deliberations, banking records, selected source datasets, model artifacts, correspondence, and other sensitive material.

The Vault is not a blockchain. Objects may be amended, superseded, archived, encrypted, access-scoped, or deleted according to law and policy. The Book records which exact object version was relied upon by digest and durable reference where necessary.

### The Big Book

The Big Book is the institution's authoritative **private proof/evidence history**. Its production deployment may use a permissioned blockchain or another replicated tamper-evident backend, but the domain contract does not depend on a specific chain implementation.

The Big Book stores or references signed event evidence, evidence digests, causal lineage, producing authority, visibility scope, schema/version, and governed references to underlying evidence.

The Big Book answers:

> **What material fact was asserted, by which organ under what authority, from what evidence, and what caused it?**

### The Little Book

The Little Book is the public verification surface. It is not a copy, mirror, export, or readable projection of the Big Book.

It contains only deliberately public records such as institutional genesis, public keys, charter/version commitments, state commitments, public attestations, revocations, public authority credentials, and intentionally disclosed claims.

The Little Book answers:

> **Can the institution prove this approved public claim without revealing its private history?**

## Epinnox producer ownership

Privacy controls must preserve which organ owns each truth:

- **ZLJ** — observations, market state, model/prediction provenance, qualification, calibration, drift, and competence evidence.
- **Benjamin** — capital decisions, thesis/invalidation, confidence, decision-context references, and later decision evaluation.
- **Watchman** — governance, policy/risk evaluation, authorization, block, expiry, and capability constraints.
- **The Hand** — capability invocation, provider/venue action, execution result, transfer/settlement result, failure, and reconciliation truth.
- **The Book** — authoritative evidence/proof lineage connecting those records.

A consumer's access to a proof does not give that consumer ownership of the producer's truth.

## Privacy classes

| Class | Meaning | Typical audience | Persistence rule |
| --- | --- | --- | --- |
| `PUBLIC_PROOF` | Deliberately public proof or attestation | Anyone | Durable |
| `PARTICIPANT_PROOF` | Rights, contributions, votes, entitlements, scoped authority | Named participants / authorized roles | Durable |
| `CONFIDENTIAL_EVIDENCE` | Contracts, financials, portfolio/trading matters, model evidence, decisions, governance, execution, deliberations | Selected roles and matters | Policy-governed |
| `SECRET_REGULATED` | SSNs, bank credentials, identity documents, private keys, regulated/private data | Extremely restricted systems | Never directly written as a public or raw immutable proof payload |

Privacy class and visibility are independent of evidence class. A capital or model event can be economically material while remaining confidential.

## Minimum necessary evidence

A proof record should preserve only what is required to establish the institutional fact.

Example:

```text
Event: BENJAMIN.DECISION
Subject: decision:DEC-381
Producer: Benjamin
Evidence refs:
  - zlj:intelligence:INT-9921
  - capital-state:STATE-118
Digest: 981b...
Visibility:
  - BENJAMIN_DECISION
  - WATCHMAN_GOVERNANCE
  - AUTHORIZED_AUDITOR
```

The underlying raw market stream, full feature vectors, private reasoning, unrelated positions, credentials, and source artifacts remain outside The Book unless a separate governed rule requires protected evidence about them.

A later Watchman authorization, Hand action, or outcome is a separate causally linked record rather than a field silently appended to the original decision as though it existed earlier.

## Time and hindsight privacy/integrity

For Benjamin v1, privacy does not excuse timing ambiguity.

Where material to reconstructing a decision, the evidence model should preserve or reference enough source-time, ingestion-time, `known_at`, horizon, sequence, and outcome-availability semantics to establish what was actually knowable at the time.

Later outcomes may create evaluation/calibration records. They must not rewrite earlier prediction/decision evidence.

## Cognitive memory versus proof history

Benjamin may maintain semantic, episodic, and procedural memory optimized for cognition. ZLJ may maintain research/model memory optimized for experimentation, model serving, and calibration.

The Book is not required to store those cognitive systems wholesale.

It preserves the minimum authoritative lineage needed to reconstruct material cases, prove producer/version/evidence relationships, and support later authorized audit or learning.

## Non-reconstruction rule

> **The Little Book must never be sufficient to reconstruct the Big Book.**

A full download of the Little Book must not reveal or permit reliable derivation of private net worth, portfolio composition, trading history, strategy, model stack, distributions, private relationships, exact confidential transaction amounts, confidential contracts, credentials, or secret/regulated data unless the institution intentionally disclosed that specific claim.

Public state commitments may prove that a private history existed and has not been rewritten without disclosing the records inside that history.

## Internal least privilege

Membership in the institution is not blanket permission to inspect the Big Book. Access is scoped by:

- role;
- domain;
- matter;
- participant rights;
- delegated authority;
- legal or fiduciary need;
- retention and disclosure policy.

Examples:

- ZLJ may receive the outcome/calibration feedback needed to evaluate its prediction without receiving Benjamin's entire private thesis history.
- The Hand may receive the exact Watchman authorization needed for execution without receiving unrelated ZLJ models or portfolio history.
- Benjamin may retrieve relevant historical case evidence without receiving secret custody credentials.

## Transitional event names

Existing Book/Benjamin/Hand code may contain legacy event names such as `BENJAMIN.RISK` or `BENJAMIN.AUTHORIZATION`.

Those records retain their historical semantics and privacy. Future schemas may move target governance/authorization ownership to explicit Watchman event families, but migration must not silently reinterpret already-issued proofs.

## Immutability rule

The system distinguishes **immutable event history** from **immutable personal/source data**.

Corrections, reversals, superseding decisions, authorization revocations, reconciliation updates, and model/outcome evaluations are new events. Sensitive source data remains in governed storage and is referenced by cryptographic digest where appropriate.

A bad secret, false statement, incorrect prediction, or accidentally exposed identifier must never become immortal merely because a ledger can make something immutable.

## Core privacy invariant

> **Preserve enough private evidence to prove and reconstruct material institutional lineage; expose no more than the legitimate consumer needs.**
