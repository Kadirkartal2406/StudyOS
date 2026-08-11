"""CORS config — wildcard yok; localhost Flutter Web portları."""

from __future__ import annotations

import re

from starlette.middleware.cors import CORSMiddleware

from app.core.config import (
    LOCALHOST_ORIGIN_REGEX,
    build_cors_middleware_kwargs,
)


def test_build_cors_never_uses_wildcard():
    kwargs = build_cors_middleware_kwargs(["*"], allow_localhost=True)
    assert "*" not in kwargs["allow_origins"]
    assert kwargs["allow_credentials"] is True
    assert kwargs["allow_origin_regex"] == LOCALHOST_ORIGIN_REGEX


def test_build_cors_keeps_production_origins():
    kwargs = build_cors_middleware_kwargs(
        ["https://app.studyos.com", "https://admin.example.com", "*"],
        allow_localhost=True,
    )
    assert kwargs["allow_origins"] == [
        "https://app.studyos.com",
        "https://admin.example.com",
    ]


def test_localhost_regex_matches_flutter_web_ports():
    rx = re.compile(LOCALHOST_ORIGIN_REGEX)
    assert rx.fullmatch("http://localhost:57780")
    assert rx.fullmatch("http://127.0.0.1:57780")
    assert rx.fullmatch("http://localhost:8080")
    assert not rx.fullmatch("https://evil.example.com")
    assert not rx.fullmatch("https://studyos-api-ghl2.onrender.com")


def test_cors_middleware_allows_localhost_origin():
    kwargs = build_cors_middleware_kwargs(
        ["https://app.studyos.com"],
        allow_localhost=True,
    )
    mw = CORSMiddleware(app=lambda scope, receive, send: None, **kwargs)
    assert mw.is_allowed_origin("http://localhost:57780")
    assert mw.is_allowed_origin("https://app.studyos.com")
    assert not mw.is_allowed_origin("https://evil.example.com")


def test_cors_localhost_can_be_disabled():
    kwargs = build_cors_middleware_kwargs(
        ["https://app.studyos.com"],
        allow_localhost=False,
    )
    assert "allow_origin_regex" not in kwargs
    mw = CORSMiddleware(app=lambda scope, receive, send: None, **kwargs)
    assert not mw.is_allowed_origin("http://localhost:57780")
    assert mw.is_allowed_origin("https://app.studyos.com")
