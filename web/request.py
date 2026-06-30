import json
from typing import Any

from fastapi import Request


def request_with_cached_body(request: Request, body: bytes) -> Request:
    """
    Return a request whose body can be read again by downstream handlers.

    Args:
        request: Original incoming request.
        body: Raw request body bytes.

    Returns:
        Request wrapper that replays the cached body.
    """

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(request.scope, receive)


async def read_json_body(request: Request) -> tuple[Request, dict[str, Any]]:
    """
    Read a JSON request body once and make it available for reuse.

    Args:
        request: Incoming HTTP request.

    Returns:
        Tuple of a replayable request and the parsed JSON body.
    """
    body = await request.body()
    payload = json.loads(body)
    return request_with_cached_body(request, body), payload
