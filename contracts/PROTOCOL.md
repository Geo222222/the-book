# Evidence Protocol v1.0

The Book accepts signed `EvidenceEnvelope` records from independent producers.

## Payload handling

The producer fixes the exact source artifact, computes its SHA-256 digest, stores the source artifact in an appropriate private evidence store, and signs an envelope containing the digest and optional durable `payload_ref`.

The Book may receive the source payload during ingestion to verify the digest, but the B0 ledger stores only the envelope — not the raw payload.

## Lineage

- `correlation_id` groups receipts that belong to one lifecycle, such as one investment thesis through execution and reconciliation.
- `causation_receipt_id` names the specific prior receipt that caused the current event.
- Causation must point backward to a receipt already accepted by The Book.

Example:

```text
EPINNOX.RECOMMENDATION
  -> BENJAMIN.DECISION
  -> BENJAMIN.RISK
  -> BENJAMIN.AUTHORIZATION
  -> HAND.EXECUTION
  -> future BENJAMIN.RECONCILIATION
```

## Blockchain anchoring

The Book batches accepted ledger entry hashes into deterministic Merkle roots. A future blockchain adapter publishes roots and returns an `AnchorReceipt` containing chain and transaction identifiers. The domain contract does not assume Ethereum, Solana, Hyperledger, or any other specific chain.

Fund ownership may later become blockchain-native, but ownership contracts are not part of B0.
