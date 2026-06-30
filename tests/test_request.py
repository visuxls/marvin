import json

from starlette.datastructures import Headers
from starlette.requests import Request

from web.request import read_json_body, request_with_cached_body


async def test_read_json_body():
    body = json.dumps({"hello": "world"}).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": Headers({"content-type": "application/json"}).raw,
    }
    request = Request(scope, receive)
    replayable, payload = await read_json_body(request)
    assert payload == {"hello": "world"}
    assert await replayable.body() == body


def test_request_with_cached_body():
    body = b"cached"
    scope = {"type": "http", "method": "POST", "path": "/", "headers": []}
    request = Request(scope)
    replayable = request_with_cached_body(request, body)
    import asyncio

    async def receive_body():
        return await replayable.receive()

    received = asyncio.run(receive_body())
    assert received["body"] == body
