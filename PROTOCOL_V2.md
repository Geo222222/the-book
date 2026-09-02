# Book Evidence Protocol v2

Protocol v2 freezes cross-organ producer ownership before expanding the evidence envelope itself.

> **ZLJ sees. Benjamin decides. Watchman governs. The Hand executes. The Book remembers and proves.**

## Purpose

Protocol v2 establishes the target namespace and authority model for new evidence while preserving all accepted v1.1/B1 receipts under the exact semantics they had when issued.

The Book transports, verifies, preserves, and connects domain truth. It does not acquire the authority of the producer whose proof it stores.

## Reserved producer namespaces

| Namespace | Constitutional producer | Domain truth |
| --- | --- | --- |
| `ZLJ.*` | ZLJ | market perception, models, prediction, calibration, model/data-quality evidence |
| `BENJAMIN.*` | Benjamin | capital decisions, decision evaluation, Benjamin competence/procedure evidence |
| `WATCHMAN.*` | Watchman | governance, policy, risk/limits, authorization, block, revocation, capability constraints |
| `HAND.*` | The Hand | capability invocation, execution, provider result, settlement, reconciliation |
| `INSTITUTION.*` | Institution | institution-wide authority, capital/accounting, ownership, disclosure, governed institutional facts |
| `MARTIANS.*` | The Martians | stewardship, contribution, entitlement, covenant, family-network facts |

A producer key registered for one reserved namespace cannot be registered as the owner of another reserved namespace.

## Target event families

### ZLJ

- `ZLJ.INTELLIGENCE`
- `ZLJ.PREDICTION`
- `ZLJ.MODEL_QUALIFICATION`
- `ZLJ.CALIBRATION`
- `ZLJ.DATA_QUALITY_INCIDENT`
- `ZLJ.EVALUATION`
- `ZLJ.JOURNAL_COMMITMENT`

### Benjamin

- `BENJAMIN.DECISION`
- `BENJAMIN.DECISION_SUPERSEDED`
- `BENJAMIN.DECISION_EVALUATION`
- `BENJAMIN.COMPETENCE_CHANGE`
- `BENJAMIN.PROCEDURE_VERSION`
- `BENJAMIN.JOURNAL_COMMITMENT`

### Watchman

- `WATCHMAN.AUTHORIZATION`
- `WATCHMAN.BLOCK`
- `WATCHMAN.REVOCATION`
- `WATCHMAN.POLICY_COMMITMENT`

### The Hand

- `HAND.ACTION_ACCEPTED`
- `HAND.ACTION_REJECTED`
- `HAND.EXECUTION`
- `HAND.FILL`
- `HAND.SETTLEMENT`
- `HAND.RECONCILIATION`

### Institution

- `INSTITUTION.CAPITAL_STATE`
- `INSTITUTION.ACCOUNTING`
- `INSTITUTION.OWNERSHIP`
- `INSTITUTION.AUTHORITY`
- `INSTITUTION.DISCLOSURE`

These are target bridge event families, not permission for The Book to originate the underlying facts.

## Legacy compatibility

The following accepted historical names are not rewritten:

- `BENJAMIN.RISK` remains a B1 record whose historical semantics include the then-embedded Watchman-role evaluation.
- `BENJAMIN.AUTHORIZATION` remains a B1 authorization-stage record and does not grant Benjamin target ownership of final governance.
- `EPINNOX.RECOMMENDATION` retains the producer meaning it had when issued and is not automatically reclassified as ZLJ evidence.

New target bridges should emit explicit producer-owned namespaces. Migration occurs by new causally linked records, not by mutation of accepted history.

## Versioning rule

Protocol v2 is introduced in layers:

1. **v2 ownership contract** — this milestone: reserved namespaces and producer authority.
2. **v2 lineage contract** — multiple evidence dependencies while preserving a primary causal trigger.
3. **v2 timing contract** — explicit knowability, production, validity, and recording semantics.
4. **v2 domain payload contracts** — typed ZLJ and Benjamin payload schemas.
5. **v2 completeness contract** — individual material receipts plus journal/state commitments.

Until the later layers are implemented and qualified, existing `EvidenceEnvelope` v1.1 remains readable and valid. No accepted receipt is silently upgraded.

## Core invariant

> **A valid signature proves what the authorized producer signed. It does not give that producer authority over another organ's namespace.**
