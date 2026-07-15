"""
StudyOS — Güvenlik Yardımcıları Birim Testleri
bcrypt hash/verify ve JWT access token üretme/doğrulama.
"""

import uuid

import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_hash_password_produces_different_hash_than_plain_text():
    hashed = hash_password("GucluSifre123!")
    assert hashed != "GucluSifre123!"
    assert hashed.startswith("$2b$")


def test_verify_password_succeeds_with_correct_password():
    hashed = hash_password("GucluSifre123!")
    assert verify_password("GucluSifre123!", hashed) is True


def test_verify_password_fails_with_wrong_password():
    hashed = hash_password("GucluSifre123!")
    assert verify_password("YanlisSifre", hashed) is False


def test_create_and_decode_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "student")

    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "student"
    assert payload["type"] == "access"


def test_decode_access_token_rejects_invalid_token():
    with pytest.raises(AuthenticationError):
        decode_access_token("gecersiz.jwt.token")


def test_generate_refresh_token_is_unique_each_call():
    first = generate_refresh_token()
    second = generate_refresh_token()
    assert first != second
    assert len(first) > 32


def test_hash_token_is_deterministic():
    token = generate_refresh_token()
    assert hash_token(token) == hash_token(token)
    assert hash_token(token) != token
