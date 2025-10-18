"""Date and time utility functions for Qwen."""

import datetime
from datetime import timezone as tz


def get_timezone() -> str:
    """Get the timezone string in the required format.

    Returns:
        The formatted timezone string.
    """
    now = datetime.datetime.now(tz=tz.utc)
    return now.strftime("%a %b %d %Y %H:%M:%S GMT+0000")


def get_timestamp(*, ms: bool = True) -> int:
    """Return the current UTC timestamp in milliseconds as an integer."""
    now = datetime.datetime.now(tz=tz.utc)
    return int(now.timestamp() * (1000 if ms else 1))


def auth_ttl_days(expires_at: int) -> float:
    """Get the number of days until expiration from a given timestamp.

    Returns:
        Amount of days until expiration as a float.
    """
    now = get_timestamp(ms=False)
    return round((expires_at - now) / 86400.0, 3)
