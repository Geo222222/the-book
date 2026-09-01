# The Book

> **The Book remembers. No organ writes history for another.**

The Book is the shared evidence and provenance system for Epinnox, Benjamin, The Hand, and future House systems. It is not owned by Benjamin and it does not make investment decisions, perform risk approval, execute trades, or originate economic facts.

The Book verifies signed evidence, preserves append-only lineage, and can anchor cryptographic commitments to a blockchain without forcing private or bulky source material on-chain.

## Constitutional role

```text
Epinnox (Eyes) -------- signed analytical evidence ----\
Benjamin (Mind/Guard) -- signed authority evidence -----+--> THE BOOK --> anchor roots / ownership state
The Hand --------------- signed execution evidence ----/
```

Every producer signs only its own claims. The Book verifies those claims and records them in an append-only hash chain.

## Evidence classes

1. **CONSTITUTIONAL** — covenant, authority, policy, fund formation, ownership, succession.
2. **ECONOMIC** — decisions, risk results, authorizations, executions, fills, NAV, subscriptions, redemptions, distributions.
3. **ANALYTICAL** — market observations, model runs, datasets, backtests, research, recommendations.

Raw private evidence is normally stored off-chain. The Book records canonical digests and durable references. Blockchain anchoring proves integrity; it is not a substitute for secure source storage.

## B0 — Sovereign Evidence Kernel

B0 establishes:

- canonical JSON hashing;
- signed `EvidenceEnvelope` records;
- Ed25519 producer identities;
- authority registry with event-type permissions;
- append-only hash-chained ledger entries;
- corrections as new evidence, never destructive edits;
- payload digest verification;
- blockchain anchor interface with no live chain selected;
- tests for tampering, impersonation, duplicate receipts, lineage corruption, and unauthorized event claims.

## Hard boundaries

- The Book cannot fabricate producer evidence.
- A producer cannot sign as another producer.
- The Book stores no producer private keys.
- Historical entries are never edited or deleted by the domain API.
- Raw PII, credentials, private keys, and large evidence payloads are not blockchain payloads.
- A blockchain implementation may be replaced without changing The Book domain contract.
- B0 contains no live public-chain writer and no tokenized fund ownership contract.

## Status

**FOUNDATION ONLY — NO LIVE BLOCKCHAIN, NO FUND TOKENS, NO PRODUCTION KEY MANAGEMENT.**
