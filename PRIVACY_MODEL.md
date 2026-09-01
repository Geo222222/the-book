# The Book Privacy Model

## Governing doctrine

> **Everything material must be provable. Not everything that happens must be permanently exposed.**

The Book exists to preserve proofs about evidence and institutional history. It is not a dumping ground for raw evidence, personal data, strategy, credentials, private correspondence, or regulated identifiers.

Legitimacy comes from provable authority, contracts, accounting, governance, reproducible records, and evidence of actions. Blockchain is a possible integrity mechanism; it is not the source of legitimacy.

## The three systems

### The Vault

The Vault holds underlying evidence that requires access controls or retention policy: contracts, statements, identity documents, valuations, deliberations, banking records, source datasets, correspondence, and other sensitive material.

The Vault is not a blockchain. Objects may be amended, superseded, archived, encrypted, access-scoped, or deleted according to law and policy. The Book records which exact object version was relied upon by digest and durable reference.

### The Big Book

The Big Book is the institution's authoritative **private proof history**. Its production deployment may use a permissioned blockchain or another replicated tamper-evident backend, but the domain contract does not depend on a specific chain implementation.

The Big Book stores signed event proofs, evidence digests, lineage, authority, visibility scope, and references to underlying evidence. It does not need to store the underlying evidence itself.

The Big Book answers:

> **What happened, under whose authority, and what exact evidence was relied upon?**

### The Little Book

The Little Book is the public verification surface. It is not a copy, mirror, export, or readable projection of the Big Book.

It contains only deliberately public records such as institutional genesis, public keys, charter/version commitments, state commitments, public attestations, revocations, public authority credentials, and intentionally disclosed asset claims.

The Little Book answers:

> **Can the institution prove this claim without revealing its private history?**

## Privacy classes

| Class | Meaning | Typical audience | Persistence rule |
| --- | --- | --- | --- |
| `PUBLIC_PROOF` | Deliberately public proof or attestation | Anyone | Durable |
| `PARTICIPANT_PROOF` | Rights, contributions, votes, entitlements, scoped authority | Named participants / authorized roles | Durable |
| `CONFIDENTIAL_EVIDENCE` | Contracts, valuations, financials, deliberations, portfolio and family matters | Selected roles and matters | Policy-governed |
| `SECRET_REGULATED` | SSNs, bank credentials, identity documents, private keys, regulated/private family data | Extremely restricted systems | Never directly written to a blockchain or public proof surface |

Privacy class and visibility are independent of evidence class. A capital event can be economically material while remaining confidential.

## Minimum necessary evidence

A proof record should preserve only what is required to establish the institutional fact.

Example:

```text
Event: CAPITAL_CONTRIBUTION_ACCEPTED
Subject: participant:9271
Authority: agreement:AG-229
Evidence digest: 981b...
Evidence location: vault://agreements/AG-229/v3
Visibility: BENJAMIN_STEWARD, participant:9271
```

The underlying agreement, address, bank account, identity document, correspondence, and private reasoning stay outside The Book unless a separate rule specifically requires a protected proof about them.

## Non-reconstruction rule

> **The Little Book must never be sufficient to reconstruct the Big Book.**

A full download of the Little Book must not reveal or permit reliable derivation of private net worth, private distributions, investment strategy, acquisition targets, family disputes, private relationships, exact confidential transaction amounts, confidential contracts, or secret/regulated data.

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

No participant receives more information than is necessary to exercise rights, perform authority, or verify a legitimate claim.

## Immutability rule

The system distinguishes **immutable event history** from **immutable personal data**.

Corrections and reversals are new events. Sensitive source data remains in governed storage and is referenced by cryptographic digest. A bad secret, false statement, or accidentally exposed identifier must never become immortal merely because a ledger can make it immutable.
