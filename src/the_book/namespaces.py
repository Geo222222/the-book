from __future__ import annotations

from dataclasses import dataclass


class NamespaceAuthorityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class NamespaceAuthority:
    prefix: str
    producer: str
    authority: str


V2_NAMESPACE_AUTHORITIES: tuple[NamespaceAuthority, ...] = (
    NamespaceAuthority(
        "ZLJ.",
        "ZLJ",
        "market perception, model production, prediction, calibration, and model/data-quality evidence",
    ),
    NamespaceAuthority(
        "BENJAMIN.",
        "Benjamin",
        "capital decision intelligence, decision evaluation, and Benjamin-owned competence/procedure evidence",
    ),
    NamespaceAuthority(
        "WATCHMAN.",
        "Watchman",
        "governance, policy, risk/limit evaluation, authorization, block, revocation, and capability constraints",
    ),
    NamespaceAuthority(
        "HAND.",
        "The Hand",
        "authorized capability invocation, external execution, provider response, settlement, and reconciliation evidence",
    ),
    NamespaceAuthority(
        "INSTITUTION.",
        "Institution",
        "institution-wide authority, capital/accounting, ownership, disclosure, and explicitly governed institutional facts",
    ),
    NamespaceAuthority(
        "MARTIANS.",
        "The Martians",
        "stewardship, contribution, entitlement, covenant, and family-network domain facts",
    ),
)


LEGACY_EVENT_OWNERSHIP: dict[str, str] = {
    "BENJAMIN.RISK": "B1 historical semantics; target governance owner is Watchman",
    "BENJAMIN.AUTHORIZATION": "B1 historical semantics; target authorization owner is Watchman",
    "EPINNOX.RECOMMENDATION": "legacy producer semantics must be preserved and not automatically reinterpreted",
}


def authority_for_prefix(prefix: str) -> NamespaceAuthority | None:
    return next((item for item in V2_NAMESPACE_AUTHORITIES if item.prefix == prefix), None)


def require_v2_namespace_authority(*, producer: str, prefixes: tuple[str, ...]) -> None:
    """Require a producer to own every registered v2 namespace prefix.

    Unknown prefixes are intentionally left available for legacy/custom v1.1 identities.
    Once a prefix is reserved by Protocol v2, only its constitutional producer may
    register it.
    """

    for prefix in prefixes:
        authority = authority_for_prefix(prefix)
        if authority is not None and authority.producer != producer:
            raise NamespaceAuthorityError(
                f"producer {producer!r} cannot register reserved namespace {prefix!r}; "
                f"owner is {authority.producer!r}"
            )
