# The Book Architecture

## Constitutional hierarchy

```text
REAL WORLD
    |
    v
DOMAIN SYSTEMS
Benjamin / The Martians / The Hand / Epinnox
    |
    | signed minimum-necessary proofs
    v
BIG BOOK
private authoritative proof history
    |
    +---- private verification for authorized participants
    |
    +---- selected state commitments / attestations
             |
             v
        LITTLE BOOK
        public testimony
             |
             v
          THE WORLD
```

The Book is one product with two trust surfaces.

## Big Book

The Big Book is private and permissioned. It is the authoritative proof history shared by institutional domains. A production deployment may use a permissioned blockchain or other replicated tamper-evident infrastructure. The code must not assume a specific ledger vendor or chain.

The Big Book records:

- event type and subject reference;
- evidence class and privacy class;
- actor/signing identity;
- cryptographic digest of the evidence relied upon;
- governed reference to the evidence in The Vault when applicable;
- correlation and causal lineage;
- visibility scope;
- append-only sequence and chain commitment.

It does not need to store the contract, statement, private key, identity document, strategy artifact, or other underlying source material.

## Little Book

The Little Book is a public verification surface. It is deliberately information-poor.

It may publish:

- institutional genesis proofs;
- public keys;
- charter/version commitments;
- Big Book Merkle/state commitments;
- intentionally public authority credentials;
- public attestations;
- revocations/superseding credentials;
- intentionally public asset claims.

It never automatically projects Big Book records.

A Little Book proof is created from a cryptographic commitment plus an explicit disclosure decision. There is no generic `export_big_book()` operation.

## The Vault

The Vault is separate governed storage. It is responsible for confidentiality, retention, access control, encryption, deletion where lawful, and durable object versioning. The Book stores a digest and reference proving which object version was relied upon.

## Domain separation

### Benjamin

Benjamin owns capital truth: portfolios, treasury, opportunities, allocations, risk state, decisions, and distributions. It emits proofs of material decisions and actions to the Big Book.

### The Martians

The Martians owns stewardship truth: family-network identity, scoped relationships, contribution, authority, governance, succession, agreements, and entitlements. It emits only necessary proofs to the Big Book.

### The Hand

The Hand owns execution truth. It proves what instruction it received, what action it performed, and what outcome it observed. It does not decide what becomes publicly disclosed.

### Epinnox

Epinnox owns analytical truth: observations, models, research, and recommendations. Sensitive strategy and opportunity details remain private; the Big Book records the minimum proof necessary to reconstruct decision provenance.

## Public commitment model

A Big Book range can be reduced to a Merkle root:

```text
BIG_BOOK_STATE_COMMITMENT
range: 88400-89117
merkle_root: 7bf41957214...
issuer: institution
```

The Little Book may publish that root. Years later, an authorized party can reveal one Big Book record plus its Merkle proof and establish that the record existed inside the committed history without revealing neighboring private records.

## Non-reconstruction requirement

The Little Book must remain safe even under total public download, indefinite retention, and sophisticated analysis. Public records must not encode enough metadata to infer private portfolio composition, wealth, family disputes, private relationships, distribution amounts, acquisition targets, or confidential agreements unless the institution deliberately elects to disclose that specific fact.
