# Evidence Protocol v1.1

The Book accepts signed proof envelopes from independent domain producers. It is designed around **minimum necessary evidence**, private authoritative history, and explicit public disclosure.

## Proof envelope

A v1.1 `EvidenceEnvelope` cryptographically binds:

- producer and signing key;
- event type;
- evidence class;
- **privacy class**;
- **visibility scope**;
- subject identifier;
- occurrence time;
- source-evidence digest;
- optional governed evidence reference;
- lifecycle correlation;
- causal parent; and
- producer signature.

Privacy and visibility are part of the signed body. They are not mutable access-control labels that can be silently changed after the producer signs the event.

## Four privacy classes

- `PUBLIC_PROOF`
- `PARTICIPANT_PROOF`
- `CONFIDENTIAL_EVIDENCE`
- `SECRET_REGULATED`

`PUBLIC_PROOF` must explicitly include `PUBLIC` visibility. Non-public classes cannot include `PUBLIC` visibility.

## Source evidence handling

The producer fixes the exact source artifact, computes its SHA-256 digest, stores the source artifact in The Vault or another governed store, and signs a proof envelope containing the digest and optional durable reference.

For ordinary non-secret evidence, the Big Book ingestion service may receive source bytes transiently to verify the digest. Those bytes are not persisted in the ledger entry merely because verification occurred.

For `SECRET_REGULATED` material, raw source bytes are prohibited from the Big Book ingestion API. The restricted system must compute the digest before the proof reaches The Book.

## Big Book

The Big Book is the private authoritative proof history.

It verifies producer identity, namespace authority, signatures, privacy fields, source digests where permitted, causal lineage, and append-only integrity.

Read access is least-privilege. A receipt may exist in the Big Book without being visible to every institutional participant.

## Lineage

- `correlation_id` groups proofs belonging to one lifecycle.
- `causation_receipt_id` names the specific prior proof that caused the current event.
- Causation must point backward to a receipt already accepted by the Big Book.

Example:

```text
EPINNOX.RECOMMENDATION
  -> BENJAMIN.DECISION
  -> BENJAMIN.RISK
  -> BENJAMIN.AUTHORIZATION
  -> HAND.EXECUTION
  -> future BENJAMIN.RECONCILIATION
```

The causal graph proves how an action came to exist without requiring every source artifact in that lifecycle to be exposed to every reader.

## Little Book

The Little Book is a separate public testimony surface. There is intentionally no generic Big Book export operation.

Public records are created only through explicit disclosure policy and may include:

- Big Book state/Merkle commitments;
- institutional genesis and charter commitments;
- public keys and revocations;
- public authority credentials;
- intentionally public attestations or asset claims.

The Little Book must not be sufficient to reconstruct the private Big Book.

## Blockchain adapters

The Big Book may later use a permissioned/private blockchain or another replicated tamper-evident backend. The Little Book may later use a public blockchain or another public append-only timestamp/verification medium.

The protocol contract does not assume Ethereum, Solana, Hyperledger, or any other chain. Blockchain is replaceable proof infrastructure.

## Ownership

Fund, enterprise, or participant ownership may later use blockchain-native state where legal and operational analysis shows value. Ownership smart contracts are not part of Evidence Protocol v1.1 and are not required for the Big Book/Little Book proof model.
