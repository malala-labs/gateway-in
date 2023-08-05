import asyncio

from malala.sockets import WebSocket
from locksmith import fetch_credentials
from providers.cedro import WsAuth
from .base import BaseExchange


class B3(BaseExchange):
    def __init__(self, channels, session):
        self.channels = channels
        self.session = session
        self._base_uri = "wss://wfxp.cedrotech.com/ws"

    async def exchange_auth(self) -> set:
        cred = fetch_credentials({"exchange": "b3"})
        self._payload_auth = WsAuth(cred).to_json()
        return set()

    async def _acquire_token(self) -> str:
        async with self.session.ws_connect(self._base_uri) as ws:
            await ws.send_json(self._payload_auth)
            data = await ws.receive_json()
            return data["token"]

    async def _exchange_client(self, id, payload) -> None:
        token = await self._acquire_token()
        uri = self._base_uri + f"?reconnect={token}"
        payload.update({"token": token})

        await WebSocket.send_json(self.session, uri, payload)
        async for msg in WebSocket.recv_str(self.session, uri):
            await self.channels[id].put(msg)

    async def spawn_service(self, id, payload) -> set:
        task = asyncio.create_task(self._exchange_client(id, payload))
        return {task}
