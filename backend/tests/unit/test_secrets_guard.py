"""RC2 M22.5 — Production secret guard unit tests."""

import pytest

from app.core.secrets_guard import (
    is_production_like,
    validate_production_secrets,
)


def test_dev_env_skips_validation():
    errs = validate_production_secrets(
        app_env="development",
        jwt_secret="change-me-in-production",
        app_secret="change-me",
        cookie_secret="x",
        raise_on_fail=False,
    )
    assert errs == []


def test_production_rejects_weak_jwt():
    errs = validate_production_secrets(
        app_env="production",
        jwt_secret="change-me-in-production",
        app_secret="a" * 32,
        cookie_secret="b" * 32,
        raise_on_fail=False,
    )
    assert any("JWT_SECRET" in e for e in errs)


def test_beta_rejects_short_secrets():
    errs = validate_production_secrets(
        app_env="beta",
        jwt_secret="short",
        app_secret="also-short",
        cookie_secret="c" * 32,
        raise_on_fail=False,
    )
    assert len(errs) >= 2


def test_production_accepts_strong_secrets():
    errs = validate_production_secrets(
        app_env="production",
        jwt_secret="x" * 32,
        app_secret="y" * 32,
        cookie_secret="z" * 32,
        raise_on_fail=False,
    )
    assert errs == []


def test_production_raise_exits():
    with pytest.raises(SystemExit):
        validate_production_secrets(
            app_env="prod",
            jwt_secret="change-me",
            raise_on_fail=True,
        )


def test_is_production_like():
    assert is_production_like("production")
    assert is_production_like("BETA")
    assert not is_production_like("development")
