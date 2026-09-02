# The Book

> **The Big Book carries the private history. The Little Book carries deliberate public testimony.**

Within Epinnox:

> **ZLJ sees. Benjamin decides. Watchman governs. The Hand executes. The Book remembers and proves.**

The Book is the institution's **authoritative evidence, memory-lineage, and proof infrastructure**. It does not exist to make every fact public or permanent, and it does not become the decision-maker merely because every organ eventually writes evidence into it.

Its governing principle remains:

> **Everything material must be provable. Only minimum necessary evidence should be preserved or exposed.**

Legitimacy comes from provable authority, contracts, accounting, governance, reproducible records, and evidence of actions. Blockchain is one integrity mechanism, not the source of legitimacy.

## Role inside Epinnox

The Book connects the organs without absorbing their truth:

```text
MARKET / WORLD
      |
      v
     ZLJ
perception / models / predictions
      |
      v
   BENJAMIN
decision intelligence
      |
      v
   WATCHMAN
governance / authorization
      |
      v
   THE HAND
external financial action
      |
      v
     WORLD
      |
      v
   THE BOOK
authoritative lineage / outcome proof
      |
      +------> Benjamin learning
      `------> ZLJ calibration
```

The Book may receive material evidence throughout the lifecycle rather than only after execution. Its job is to preserve which qualified evidence existed, which decision was made, which governance result applied, what external action occurred, and what later outcome became known.

## Three storage/trust surfaces

### The Vault

Encrypted, access-controlled source evidence: contracts, statements, identity documents, valuations, private research, model artifacts, selected datasets, banking records, correspondence, and other sensitive material.

The Vault holds secrets and policy-governed source evidence.

### The Big Book

The authoritative **private proof and institutional lineage history** for Epinnox and other institutional domains.

The Big Book may preserve signed event evidence, evidence digests, governed references, actor/authority identity, privacy class, visibility scope, causal lineage, and append-only integrity commitments.

It does not need to store every raw feature vector, prompt, model input, order-book event, private document, or secret itself.

A production Big Book may use a permissioned blockchain or another replicated tamper-evident backend. No chain vendor is constitutional.

### The Little Book

The **public verification surface**. It is not a second copy of the Big Book and cannot generically export or reconstruct it.

The Little Book contains only deliberately public testimony such as:

- institutional genesis proofs;
- public keys;
- charter/version commitments;
- periodic Big Book state commitments;
- public authority credentials;
- public attestations;
- revocations/superseding credentials;
- intentionally disclosed asset or institutional claims.

## Epinnox domain truth versus Book proof truth

- **ZLJ holds perception/model truth** — what was observed, derived, predicted, and how qualified the producer was.
- **Benjamin holds decision truth** — what Epinnox decided about capital and why.
- **Watchman holds governance/authorization truth** — what was permitted or blocked under governing rules.
- **The Hand holds execution/capability truth** — what external action was attempted/performed and what the provider/venue returned.
- **The Vault holds underlying governed source evidence.**
- **The Big Book holds authoritative private lineage/proofs of material institutional events.**
- **The Little Book holds deliberate public testimony.**

The Book therefore proves and connects domain facts without becoming the domain itself.

## Benjamin memory relationship

Benjamin requires semantic, episodic, and procedural cognitive memory.

The Book does not need to implement all cognition or retrieval itself. Instead, it provides authoritative lineage and durable evidence references so Benjamin can reconstruct material cases without rewriting history.

For v1 short-horizon trading, a useful learning lineage is:

```text
Market evidence
      |
      v
ZLJ intelligence / prediction
      |
      v
Benjamin decision
      |
      v
Watchman authorization or block
      |
      v
Hand action / no action
      |
      v
Outcome
      |
      v
Evaluation
```

This supports three practical case views:

- **market memory** — what the market/evidence looked like;
- **decision memory** — what Benjamin believed and decided;
- **outcome memory** — what actually happened.

The Book preserves the authoritative lineage among these views. Benjamin owns their cognitive interpretation; ZLJ owns prediction/model evaluation; The Hand owns execution facts.

## Privacy classes

| Class | Purpose | Typical audience |
| --- | --- | --- |
| `PUBLIC_PROOF` | intentionally public proof | anyone |
| `PARTICIPANT_PROOF` | contributions, rights, votes, entitlements | named participants / authorized roles |
| `CONFIDENTIAL_EVIDENCE` | contracts, portfolio matters, decisions, model/performance evidence, deliberations | selected roles and matters |
| `SECRET_REGULATED` | SSNs, banking credentials, identity documents, keys, regulated/private data | extremely restricted systems |

`SECRET_REGULATED` source material is never accepted as raw bytes by the Big Book kernel and is never directly published by the Little Book.

## Constitutional non-reconstruction rule

> **The Little Book must never be sufficient to reconstruct the Big Book.**

A public observer should not be able to derive private wealth, portfolio composition, trading history, strategies, model stack, distributions, private relationships, acquisition targets, exact confidential transaction amounts, or confidential agreements unless the institution intentionally publishes that specific claim.

## Bridge principle

Every future bridge should identify:

- producer organ;
- event/object type;
- authority owned by that producer;
- causal parent(s);
- evidence digest/reference;
- time/sequence semantics;
- privacy/visibility;
- version/schema;
- correction/supersession behavior.

The Book verifies those claims under policy. It does not invent missing domain truth to make a lineage complete.

## Current code status

Current milestone remains a privacy/disclosure and proof foundation. The repository contains signed evidence envelopes, privacy classes, least-privilege reads, append-only lineage, evidence digest verification, deterministic commitments, Little Book state commitments, and explicit public-attestation policy.

Existing event namespaces may predate the final Epinnox bridge ownership described above. Future migration should preserve historical meaning rather than silently reinterpret old `BENJAMIN.*`, `HAND.*`, or other records.

**No production permissioned chain, public chain, tokenized fund ownership contract, or production key-management system is selected merely by this documentation.**

See `PRIVACY_MODEL.md`, `ARCHITECTURE.md`, and `COVENANT.md`.
