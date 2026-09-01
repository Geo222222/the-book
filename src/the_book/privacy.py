from __future__ import annotations

from collections.abc import Iterable

from .domain import EvidenceEnvelope, PrivacyClass


class AccessDenied(PermissionError):
    pass


def can_view(
    envelope: EvidenceEnvelope,
    *,
    principal: str,
    authorities: Iterable[str] = (),
) -> bool:
    """Evaluate Big Book read visibility without expanding the stored evidence."""
    if envelope.privacy_class is PrivacyClass.PUBLIC_PROOF:
        return True

    granted = {principal, *authorities}
    return bool(granted.intersection(envelope.visibility_scope))


def require_view(
    envelope: EvidenceEnvelope,
    *,
    principal: str,
    authorities: Iterable[str] = (),
) -> None:
    if not can_view(envelope, principal=principal, authorities=authorities):
        raise AccessDenied("principal is not authorized to view this Big Book proof")
