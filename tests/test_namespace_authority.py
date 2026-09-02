from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import pytest

from the_book.identity import AuthorityRegistry
from the_book.namespaces import NamespaceAuthorityError


def public_key_bytes() -> bytes:
    return Ed25519PrivateKey.generate().public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def test_reserved_namespace_accepts_constitutional_owner() -> None:
    registry = AuthorityRegistry()
    registry.register(
        producer="ZLJ",
        key_id="zlj-k1",
        public_key=public_key_bytes(),
        allowed_event_prefixes=("ZLJ.",),
    )


def test_reserved_namespace_rejects_wrong_producer() -> None:
    registry = AuthorityRegistry()
    with pytest.raises(NamespaceAuthorityError):
        registry.register(
            producer="Benjamin",
            key_id="benjamin-impersonates-zlj",
            public_key=public_key_bytes(),
            allowed_event_prefixes=("ZLJ.",),
        )


def test_unknown_legacy_prefix_remains_registerable() -> None:
    registry = AuthorityRegistry()
    registry.register(
        producer="LegacyProducer",
        key_id="legacy-k1",
        public_key=public_key_bytes(),
        allowed_event_prefixes=("LEGACY.",),
    )
