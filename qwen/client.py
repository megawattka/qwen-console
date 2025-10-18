"""Qwen main module."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from httpx import AsyncClient, HTTPStatusError, QueryParams, Response

from .dateutil import auth_ttl_days, get_timestamp
from .exceptions import QwenError
from .helpers import get_headers

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from .typings import xJsonT

log = logging.getLogger(__name__)


class Qwen:
    """Main Qwen class."""

    def __init__(
        self,
        token: str,
        client: AsyncClient,
    ) -> None:
        self._auth_token = token
        self._http = client

    @staticmethod
    def read_auth_file(filename: str = "auth.json") -> str:
        """Read authentication token from a file.

        Args:
            filename: Path to the authentication file.

        Returns:
            The authentication token as a string.

        Raises:
            QwenError: Invalid or Non-existent token.
        """
        auth_p = Path(filename)
        if not auth_p.exists():
            raise QwenError("Auth file not found. Use gen_auth.py")

        infos = json.load(fp=auth_p.open("r", encoding="u8"))
        eat = infos["expires_at"]
        einfo = auth_ttl_days(eat)
        if einfo <= 0.0:
            raise QwenError("Auth token expired. Expiration: %s days", einfo)

        log.info("Found token. It'll expire in %s days", auth_ttl_days(eat))
        return infos["token"]

    @classmethod
    def from_auth_file(cls, filename: str = "auth.json") -> Qwen:
        """Create a Qwen instance using an authentication file.

        Args:
            filename: Path to the authentication file.

        Returns:
            An instance of Qwen.
        """
        token = cls.read_auth_file(filename=filename)
        client = AsyncClient(http2=True)
        return cls(token=token, client=client)

    async def request(
        self,
        method: str,
        url: str,
        referer: str = "https://chat.qwen.ai/",
        json: xJsonT | None = None,
        params: QueryParams | None = None,
    ) -> Response:
        """Make an HTTP request to Qwen API.

        Returns:
            The HTTP response.
        """
        headers = get_headers(referer=referer, auth=self._auth_token)
        return await self._http.request(
            method, url,
            headers=headers,
            params=params,
            json=json,
        )

    async def get_chats(self) -> xJsonT:
        """Return the list of chats for the authenticated user."""
        url = "https://chat.qwen.ai/api/v2/chats/?page=1"
        resp = await self.request(url=url, method="GET")
        resp.raise_for_status()
        return resp.json()["data"]

    async def get_me(self) -> xJsonT:
        """Return the auth info about current token.

        Raises:
            QwenError: If the authentication token is invalid.
        """
        url = "https://chat.qwen.ai/api/v1/auths/"
        resp = await self.request(url=url, method="GET")
        try:
            resp.raise_for_status()
        except HTTPStatusError as e:
            raise QwenError from e
        return resp.json()

    async def get_models(self) -> xJsonT:
        """Return the list of available models for the authenticated user."""
        url = "https://chat.qwen.ai/api/models"
        resp = await self.request(url=url, method="GET")
        resp.raise_for_status()
        return resp.json()["data"]

    async def create_chat(
        self,
        *,
        temporary: bool = False,
        model: str = "qwen3-max",
        title: str = "New chat",
    ) -> str:
        """Create a new chat.

        Returns:
            The created chat id.
        """
        url = "https://chat.qwen.ai/api/v2/chats/new"
        payload = {
            "title": title,
            "models": [model],
            "chat_mode": "normal" if not temporary else "local",
            "chat_type": "t2t",
            "timestamp": get_timestamp(),
        }
        resp = await self.request(url=url, method="POST", json=payload)
        resp.raise_for_status()
        return resp.json()["data"]["id"]

    @staticmethod
    def _clear_line(line: str) -> xJsonT | None:
        if not line:
            return None
        return json.loads(line.replace("data: ", "").strip())

    async def create_completion(
        self,
        chat_id: str,
        message: str,
        referer: str = "https://chat.qwen.ai/",
        *,
        temporary_chat: bool = False,
        model: str = "qwen3-max",
        parent_id: str | None = None,
        thinking_enabled: bool = False,
    ) -> AsyncGenerator[xJsonT | str | None, None]:
        """Create a streaming chat completion and asynchronously yield parsed events.

        This coroutine opens a streaming HTTP connection to the completions
        endpoint and yields either parsed JSON chunks (xJsonT), string content
        fragments, or None for empty lines. The generator finishes when the
        stream signals the finished status.

        Parameters:
            chat_id: The chat identifier.
            message: The message content to send.
            referer: The referer header value.
            temporary_chat: Whether to use a temporary/local chat mode.
            model: Model name to use.
            parent_id: Optional parent message id.

        Yields:
            xJsonT | str | None: Parsed JSON chunks, text content, or None.
        """  # noqa: E501
        url = "https://chat.qwen.ai/api/v2/chat/completions"
        params = QueryParams(chat_id=chat_id)
        headers = get_headers(referer=referer, auth=self._auth_token)
        payload = {
            "chat_id": chat_id,
            "chat_mode": "local" if temporary_chat else "normal",
            "incremental_output": True,
            "model": model,
            "parent_id": parent_id,
            "stream": True,
            "timestamp": get_timestamp(ms=False),
            "messages": [{
                "chat_type": "t2t",
                "content": message,
                "feature_config": {
                    "output_schema": "phase",
                    "thinking_enabled": thinking_enabled,
                },
                "files": [],
                "models": [model],
                "role": "user",
                "sub_chat_type": "t2t",
                "timestamp": get_timestamp(ms=False),
                "user_action": "chat",
            }],
        }
        stream = self._http.stream(
            method="POST",
            url=url,
            params=params,
            headers=headers,
            json=payload,
        )
        async with stream as r:
            lineiter = r.aiter_lines()
            yield self._clear_line(await anext(lineiter))
            async for line in lineiter:
                cleared = self._clear_line(line)
                if cleared is not None:
                    if cleared["choices"][0]["delta"]["status"] == "finished":
                        break
                    yield cleared["choices"][0]["delta"]["content"]
