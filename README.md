# The Book

> **The Big Book carries the history. The Little Book carries the testimony.**

The Book is the institution's proof infrastructure. It does **not** exist to make every fact public or permanent. Its governing principle is:

> **Everything material must be provable. Only minimum necessary evidence should be preserved or exposed.**

Legitimacy comes from provable authority, contracts, accounting, governance, reproducible records, and evidence of actions. Blockchain is one integrity mechanism, not the source of legitimacy.

## Three storage/trust surfaces

### The Vault

Encrypted, access-controlled source evidence: contracts, statements, identity documents, valuations, deliberations, banking records, correspondence, datasets, and other sensitive material.

The Vault holds secrets and policy-governed evidence.

### The Big Book

The authoritative **private proof history** for Benjamin, The Martians, The Hand, Epinnox, and future institutional domains.

The Big Book stores signed event proofs, evidence digests, evidence references, authority, privacy class, visibility scope, causal lineage, and append-only integrity commitments. It does not need to store the underlying evidence itself.

A production Big Book may use a permissioned blockchain or another replicated tamper-evident backend. No chain vendor is constitutional.

### The Little Book

The **public verification surface**. It is not a second copy of the Big Book and cannot generically export or reconstruct it.

The Little Book contains only deliberately public testimony such as:

- institutional genesis proofs;
- public keys;
- charter/version commitments;
- periodic Big Book Merkle/state commitments;
- public authority credentials;
- public attestations;
- revocations/superseding credentials;
- intentionally disclosed asset claims.

## Privacy classes

| Class | Purpose | Typical audience |
| --- | --- | --- |
| `PUBLIC_PROOF` | intentionally public proof | anyone |
| `PARTICIPANT_PROOF` | contributions, rights, votes, entitlements | named participants / authorized roles |
| `CONFIDENTIAL_EVIDENCE` | contracts, valuations, portfolio/family matters, deliberations | selected roles and matters |
| `SECRET_REGULATED` | SSNs, banking credentials, identity documents, keys, regulated/private family data | extremely restricted systems |

`SECRET_REGULATED` source material is never accepted as raw bytes by the Big Book kernel and is never directly published by the Little Book.

## Domain truth versus proof truth

- **Benjamin holds capital truth.**
- **The Martians holds stewardship truth.**
- **The Hand holds execution truth.**
- **Epinnox holds analytical truth.**
- **The Vault holds underlying evidence.**
- **The Big Book holds private institutional proofs.**
- **The Little Book holds public testimony.**

The Book therefore proves domain facts without becoming the domain itself.

## Constitutional non-reconstruction rule

> **The Little Book must never be sufficient to reconstruct the Big Book.**

A public observer should not be able to derive private wealth, portfolio composition, distributions, family disputes, private relationships, acquisition targets, exact confidential transaction amounts, or confidential agreements unless the institution intentionally publishes that specific claim.

## Code status

Current milestone: **B1 — Privacy & Disclosure Constitution**.

The repository contains:

- signed evidence envelopes;
- four privacy classes;
- Big Book least-privilege reads;
- append-only proof lineage;
- source-evidence digest verification;
- rejection of raw secret/regulated payloads;
- deterministic Merkle roots;
- Little Book state commitments;
- explicit public-attestation policy;
- no generic Big Book-to-Little Book export path.

**No production permissioned chain, public chain, tokenized fund ownership contract, or production key-management system is selected yet.**

See `PRIVACY_MODEL.md` and `ARCHITECTURE.md`.
