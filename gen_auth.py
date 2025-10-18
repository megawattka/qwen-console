"""Generate authentication token for Qwen AI chat service."""

import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import httpx
from httpx import HTTPError

from qwen import QwenError, auth_ttl_days, get_headers

load_dotenv()
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main(args: argparse.Namespace) -> None:
    """Main function to generate authentication token.

    Args:
        args: Command-line arguments.

    Raises:
        QwenError: If the authentication fails.
    """
    client = httpx.Client(http2=True)
    auth_f = Path(args.output)
    if auth_f.exists() and not args.force:
        infos = json.load(fp=auth_f.open("r", encoding="u8"))
        ttl_d = auth_ttl_days(infos["expires_at"])
        log.info("Found existing auth file with %s days until expiration.", ttl_d)  # noqa: E501
        if ttl_d < 0.0:
            log.info("Token expired. Regenerating...")
        else:
            log.info("Use --force to force regeneration.")
            sys.exit(0)

    password = os.environ["QWEN_PASSWORD"]
    payload = {
        "email": os.environ["QWEN_EMAIL"],
        "password": hashlib.sha256(password.encode()).hexdigest(),
    }
    url = "https://chat.qwen.ai/api/v1/auths/signin"

    headers = get_headers(referer="https://chat.qwen.ai/auth?action=signin")
    resp = client.post(url, json=payload, headers=headers)

    log.info("Auth request completed with status: %s", resp.status_code)
    try:
        resp.raise_for_status()
        infos = resp.json()
        del infos["profile_image_url"]
        json.dump(
            infos,
            fp=auth_f.open("w", encoding="u8"),
            indent=4,
            ensure_ascii=False,
        )
        log.info("Token saved to %s", args.output)
    except (Exception, HTTPError) as e:
        log.info("resp.text: %s", resp.text)
        log.info("exc: %s", e)
        log.info("status: %s", resp.status_code)
        raise QwenError from e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Qwen AI chat authentication token.",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="force token regeneration.",
    )
    parser.add_argument(
        "-o", "--output",
        help="output file for the authentication token.",
        default="auth.json",
    )
    args = parser.parse_args()
    main(args)
