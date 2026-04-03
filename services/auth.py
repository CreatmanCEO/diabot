"""Authentication, authorization and rate limiting service."""

from __future__ import annotations

from collections import defaultdict
from time import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.database import Database


class AuthService:
    """Manages user access control and rate limiting."""

    def __init__(
        self,
        db: Database,
        admin_ids: set[int],
        rate_limit_requests: int = 30,
        rate_limit_window: int = 3600,
    ) -> None:
        self.db = db
        self.admin_ids = admin_ids
        self._rate_limit_requests = rate_limit_requests
        self._rate_limit_window = rate_limit_window
        self._requests: dict[int, list[float]] = defaultdict(list)

    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in self.admin_ids

    async def is_allowed(self, user_id: int) -> bool:
        """Check if user has access to the bot.

        Admins always have access. Other users must be in allowed_users table.
        """
        if self.is_admin(user_id):
            return True
        return await self.db.is_user_allowed(user_id)

    def check_rate_limit(self, user_id: int) -> tuple[bool, int]:
        """Check if user is within rate limits.

        Returns:
            Tuple of (allowed, seconds_until_reset).
            If allowed is True, seconds_until_reset is 0.
        """
        now = time()
        cutoff = now - self._rate_limit_window
        # Clean old entries
        self._requests[user_id] = [
            t for t in self._requests[user_id] if t > cutoff
        ]
        if len(self._requests[user_id]) >= self._rate_limit_requests:
            oldest = self._requests[user_id][0]
            wait = int(oldest + self._rate_limit_window - now) + 1
            return False, wait
        self._requests[user_id].append(now)
        return True, 0
