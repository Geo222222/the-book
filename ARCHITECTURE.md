# The Book Architecture

## Constitutional hierarchy

```text
REAL WORLD / MARKETS
        |
        v
       ZLJ
perception / models / predictions
        |
        v
     BENJAMIN
 capital decision intelligence
        |
        v
     WATCHMAN
 governance / authorization
        |
        v
      THE HAND
 authorized external capability
        |
        v
   EXTERNAL WORLD
        |
        v
     OUTCOMES

Material lineage from every stage
        |
        v
     BIG BOOK
private authoritative evidence/proof history
        |
        +---- private verification for authorized roles
        |
        +---- selected state commitments / attestations
                 |
                 v
            LITTLE BOOK
            public testimony
```

The Book is one product with two trust surfaces plus governed source-evidence references. It connects institutional history without becoming the market observer, decision-maker, governor, or executor.

## Big Book

The Big Book is private and permissioned. It is the authoritative proof/evidence history shared by institutional domains.

A production deployment may use a permissioned blockchain or other replicated tamper-evident infrastructure. The code must not assume a specific ledger vendor or chain.

The Big Book records or references, where material:

- event/object type and subject reference;
- producing organ and signing identity;
- evidence class and privacy class;
- cryptographic digest of evidence relied upon;
- governed source-evidence reference when applicable;
- correlation and causal lineage;
- timestamps/sequence/availability semantics where required;
- visibility scope;
- schema/version identity;
- append-only sequence and integrity commitment.

It does not need to store every contract, private key, identity document, market tick, feature vector, model input, prompt, strategy artifact, or other underlying source object.

## Little Book

The Little Book is a public verification surface. It is deliberately information-poor.

It may publish:

- institutional genesis proofs;
- public keys;
- charter/version commitments;
- Big Book state commitments;
- intentionally public authority credentials;
- public attestations;
- revocations/superseding credentials;
- intentionally public asset/institutional claims.

It never automatically projects Big Book records.

A Little Book proof is created from a cryptographic commitment plus an explicit disclosure decision. There is no generic `export_big_book()` operation.

## The Vault

The Vault is separate governed storage responsible for confidentiality, retention, access control, encryption, deletion where lawful, and durable object versioning.

The Book may store a digest/reference proving which exact object version was relied upon without forcing the source object itself into immutable history.

## Epinnox domain separation

### ZLJ

ZLJ owns perception/model truth:

- market observations;
- derived measurements/features;
- market state/regime;
- model identity/qualification;
- predictions;
- calibration/drift/competence evidence;
- opportunity evidence.

ZLJ may emit minimum-necessary material evidence/provenance to the Big Book. The Book does not decide whether a forecast is economically actionable.

### Benjamin

Benjamin owns capital decision truth:

- decision context references;
- trade/no-trade judgment;
- thesis/invalidation;
- intended size/position change;
- confidence;
- decision procedure/reasoner identity;
- later decision evaluation.

Benjamin does not own final external-action authorization and does not place the action itself.

### Watchman

Watchman owns governance/authorization truth:

- policy/mandate evaluation;
- risk/limit results;
- compliance/jurisdiction checks;
- authority validation;
- `AUTHORIZE` or `BLOCK`;
- exact capability/action constraints and expiry.

The Book preserves this result; it does not infer a pass because Benjamin wanted the trade.

### The Hand

The Hand owns execution/capability truth:

- which authorized capability/adapter was invoked;
- which external provider/venue/account was used;
- exact bounded parameters;
- accepted/rejected/partial/filled/transferred/settled state;
- external identifiers;
- failures/retries/idempotency;
- reconciliation observations.

The Hand does not decide what becomes publicly disclosed.

### Other domains

Other institutional systems, including The Martians, retain their own truth and may publish only necessary proofs into the same Book infrastructure. Epinnox's organ model does not make The Book exclusive to one domain.

## Target Epinnox event lineage

A target v1 short-horizon case may look like:

```text
ZLJ.OBSERVATION / ZLJ.PREDICTION
          |
          v
BENJAMIN.DECISION
          |
          v
WATCHMAN.AUTHORIZATION | WATCHMAN.BLOCK
          |
          v
HAND.ACTION / HAND.EXECUTION   (only if authorized)
          |
          v
OUTCOME / RECONCILIATION
          |
          v
EVALUATION / CALIBRATION / LEARNING EVIDENCE
```

Exact event names are bridge-contract concerns. Existing namespaces may use legacy labels. Historical records must retain their original semantics rather than being rewritten to match later naming.

## Cognitive memory relationship

The Book does not replace Benjamin's cognitive memory services.

Benjamin may maintain semantic, episodic, and procedural memory optimized for retrieval/reasoning. The Big Book provides the authoritative material lineage needed to reconstruct cases and prove what happened.

For short-horizon learning, a case may reference:

```text
Market memory   -> ZLJ state/predictions available at the time
Decision memory -> Benjamin thesis/decision/confidence
Outcome memory  -> Hand/external result + later market outcome
```

The Book connects these records while preserving producer ownership.

## Correction and supersession

No domain silently rewrites accepted Book history.

If a prediction is later evaluated, a decision is reversed, a Watchman authorization is revoked/superseded, or an execution is corrected/reconciled, the later truth is represented by a new causally linked event.

This preserves both what was believed/authorized at the time and what was learned later.

## Public commitment model

A Big Book range can be reduced to a commitment such as a Merkle root:

```text
BIG_BOOK_STATE_COMMITMENT
range: 88400-89117
merkle_root: 7bf41957214...
issuer: institution
```

The Little Book may publish that root. Later, an authorized party can reveal one Big Book record plus its proof and establish inclusion without revealing neighboring private records.

## Non-reconstruction requirement

The Little Book must remain safe even under total public download, indefinite retention, and sophisticated analysis.

Public records must not encode enough metadata to infer private portfolio composition, trading history, wealth, model stack, distributions, private relationships, acquisition targets, or confidential agreements unless the institution deliberately elects to disclose that specific fact.

## Core boundary

> **The Book remembers and proves what each organ truthfully produced; it does not become the organ that should have produced it.**
