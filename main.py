"""The entrypoint of this project."""

import asyncio
import logging

from dotenv import load_dotenv

from qwen import Qwen

load_dotenv()
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def main() -> None:
    """Entrypoint."""
    qwen = Qwen.from_auth_file("auth.json")
    me = await qwen.get_me()
    log.info("Authenticated as: %s", me["name"])

    logging.getLogger("httpx").setLevel(logging.WARNING)
    chat_id = await qwen.create_chat(temporary=True)
    parent_id = None
    while True:
        message = input(">>> ")  # noqa: ASYNC250
        kwargs = {"message": message, "parent_id": parent_id}
        output = ""
        async for chunk in qwen.create_completion(chat_id, **kwargs):
            if isinstance(chunk, dict):
                parent_id = chunk["response.created"]["response_id"]
                continue
            if isinstance(chunk, str):
                output += chunk
                print(chunk, end="", flush=True)  # noqa: T201
        print("\n")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
