"""Helper functions for Qwen AI chat service."""

import uuid

from .constants import UA
from .dateutil import get_timezone


def get_headers(
    referer: str,
    auth: str | None = None,
    token_type: str = "Bearer",  # noqa: S107
) -> dict[str, str]:
    """Build and return HTTP headers for requests to the Qwen chat API.

    Args:
        referer: The Referer header value to send.
        auth: Optional Bearer token to include in the Authorization header.
        token_type: The type of token to use in the Authorization header.

    Returns:
        A dictionary of HTTP headers.
    """
    headers = {
        "user-agent": UA,
        "source": "web",
        "timezone": get_timezone(),
        "version": "0.0.230",
        "x-request-id": str(uuid.uuid4()),
        "origin": "https://chat.qwen.ai",
        "referer": referer,
        "bx-v": "2.5.31",
    }
    if auth is not None:
        headers["authorization"] = f"{token_type} {auth}"
    return headers
