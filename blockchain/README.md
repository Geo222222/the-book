# Blockchain Boundary

B0 intentionally contains **no live chain integration**.

The Book currently computes deterministic Merkle roots over accepted ledger entries. A later adapter may anchor those roots to a chosen blockchain.

A production anchor must provide:

- explicit network/chain identity;
- transaction receipt and finality semantics;
- retry/idempotency behavior;
- reorg/finality handling where applicable;
- fee controls;
- key isolation;
- independent verification from the chain;
- migration/export strategy.

Tokenized Firstfruits ownership is a separate future milestone. It must not be conflated with evidence anchoring.
