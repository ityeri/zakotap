import io
import json
from collections.abc import Callable
from typing import Any
import httpx
import asyncio

import websockets
from httpx import Response

from .api import WS_ENDPOINT, HTTP_ENDPOINT


class ZakoClient:
    def __init__(self, token: str, name: str, client: httpx.AsyncClient=None):
        self.token: str = token
        self.name: str = name
        self.client: httpx.AsyncClient = client

        if not self.client:
            self.client = httpx.AsyncClient()

        self.audio_func: Callable[[str], io.BytesIO] | None = None


    def run(self):
        asyncio.run(self.start())


    async def start(self):
        try:
            async with websockets.connect(WS_ENDPOINT + "/gateway", ping_timeout=None, ping_interval=None) as socket:
                data = {
                    "name": self.name,
                    "token": self.token
                }

                await socket.send(json.dumps(data))

                response = await socket.recv()
                response_data = json.loads(response)

                if not response_data["ok"]:
                    raise ConnectionError("핸드쉐이킹에 실패했습니다. 잘못된 name 이나 token 이 전달되었을수 있습니다")

                while True:
                    response = await socket.recv()
                    response_data = json.loads(response)

                    id = response_data["id"]
                    is_ping = response_data["ping"]
                    content = response_data["data"]
                    kwargs: dict[str, Any] = response_data["parameters"]

                    if is_ping:
                        await self.client.post(HTTP_ENDPOINT + f"/data/{id}/ok")

                    else:
                        try:
                            audio_data = self.audio_func(content)
                            await self.audio_response(id, True, audio_data)
                        except Exception as e:
                            await self.audio_response(id, False, err=str(e))
        finally:
            await self.client.aclose()


    async def audio_response(
            self,
            id: str,
            ok: bool,
            audio_data: io.BytesIO | None=None,
            err: str | None = None) -> Response | None:

        if ok:
            response = await self.client.post(
                HTTP_ENDPOINT + f"/data/{id}/ok",
                data=audio_data.getvalue(),
                headers={"Content-Type": "application/octet-stream"}
            )
            return response

        else:
            await self.client.post(
                HTTP_ENDPOINT + f"/data/{id}/err",
                json={"message": err}
            )
            return None


    def on_receive(self, func: Callable[[str], io.BytesIO]):
        self.audio_func = func