# The Book Covenant

The Book exists to preserve evidence across institutions and generations. Its job is memory, provenance, and proof — not authority over capital.

## B0 invariants

1. **Producer sovereignty** — Epinnox, Benjamin, The Hand, and future organs sign only their own evidence.
2. **No impersonation** — a valid key is still rejected when it claims an event namespace it is not authorized to produce.
3. **No private-key custody** — The Book registry contains public verification material only.
4. **Append only** — accepted ledger entries are never edited or deleted by the domain API.
5. **Corrections append** — a correction is a new signed envelope that causally references earlier evidence.
6. **Digest before trust** — supplied source payloads must hash to the envelope's declared digest.
7. **Lineage before chronology** — a causation reference must point to evidence already present in The Book.
8. **Raw secrets stay out** — PII, credentials, signing private keys, and large private datasets are not written to blockchain payloads.
9. **Blockchain is a proof rail** — The Book domain remains valid if the underlying chain technology changes.
10. **No live anchor in B0** — B0 computes anchor roots but cannot publish them to a live chain.
11. **No token ownership in B0** — fund-unit mint, burn, transfer restriction, and holder registry contracts are future milestones.
12. **Verification is replayable** — The Book can re-verify signatures and the complete local hash chain from genesis.

## Producer namespaces

Initial event namespace ownership is:

```text
EPINNOX.*   -> Epinnox / The Eyes
BENJAMIN.*  -> Benjamin / Mind, Guard, Treasury, Portfolio
HAND.*      -> The Hand / execution
BOOK.*      -> The Book's own anchor and verification attestations only
```

Granting a producer another namespace is an explicit authority-registry change and itself must become constitutional evidence in a later persistent implementation.
