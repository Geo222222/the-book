# Blockchain Adapters

Blockchain is an implementation mechanism beneath The Book, not its constitutional source of truth.

## Big Book backend

The production Big Book may use a **permissioned/private blockchain** when multiple independent institutional parties need to agree on history without trusting one operator completely.

Potential node operators include the institution, Benjamin, The Martians, an independent trustee, auditor, custodian, or future trust. Running several nodes under one person's control is replication, not meaningful decentralized trust.

Requirements for a future Big Book adapter:

- permissioned consensus;
- scoped read/write authority;
- private transaction/data capability or proof-only records;
- durable identity and key rotation;
- correction/supersession semantics;
- auditable node membership;
- exportable cryptographic proofs;
- no raw `SECRET_REGULATED` payloads.

## Little Book backend

The Little Book may use a public blockchain or other publicly timestamped append-only medium.

It publishes only deliberately public proof artifacts such as:

- Big Book state/Merkle commitments;
- public keys and key revocations;
- genesis/charter commitments;
- public authority credentials;
- public attestations;
- intentionally disclosed asset claims.

The Little Book is never a public replica of the Big Book.

## Current status

No permissioned chain, public chain, consensus implementation, smart-contract platform, or token standard is selected. The domain kernel remains backend-neutral until trust participants, privacy requirements, cost, legal retention, disaster recovery, and governance requirements are defined.
