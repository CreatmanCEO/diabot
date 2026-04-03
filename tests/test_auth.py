"""Tests for auth service."""

import pytest
from unittest.mock import AsyncMock
from services.auth import AuthService


@pytest.fixture
def auth():
    db = AsyncMock()
    return AuthService(
        db=db, admin_ids={100, 200}, rate_limit_requests=3, rate_limit_window=60
    )


def test_admin_is_always_allowed(auth):
    assert auth.is_admin(100) is True
    assert auth.is_admin(999) is False


@pytest.mark.asyncio
async def test_allowed_user(auth):
    auth.db.is_user_allowed = AsyncMock(return_value=True)
    assert await auth.is_allowed(300) is True


@pytest.mark.asyncio
async def test_admin_always_allowed_no_db_call(auth):
    assert await auth.is_allowed(100) is True
    auth.db.is_user_allowed.assert_not_called()


@pytest.mark.asyncio
async def test_unknown_user_denied(auth):
    auth.db.is_user_allowed = AsyncMock(return_value=False)
    assert await auth.is_allowed(999) is False


def test_rate_limiting(auth):
    for _ in range(3):
        allowed, _ = auth.check_rate_limit(300)
        assert allowed is True
    allowed, wait = auth.check_rate_limit(300)
    assert allowed is False
    assert wait > 0


def test_rate_limit_per_user(auth):
    for _ in range(3):
        auth.check_rate_limit(300)
    # Different user should not be limited
    allowed, _ = auth.check_rate_limit(400)
    assert allowed is True


def test_admin_not_exempt_from_rate_limit(auth):
    """Admins are subject to rate limits too."""
    for _ in range(3):
        auth.check_rate_limit(100)
    allowed, _ = auth.check_rate_limit(100)
    assert allowed is False
