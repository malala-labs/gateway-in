import asyncio

from malala.sockets import WebSocket
from malala.constants import ONE_MIN, TEN_MIN
from .base import BaseExchange
from locksmith import fetch_credentials

import pdb


class Binance(BaseExchange):
    def __init__(self, channels, session):
        # global variables
        self.channels = channels
        self.session = session

        # local variables
        self._book = dict()
        self._last_update_id = 0

        # uris
        self._uri_http = dict()
        self._uri_http["spot"] = "https://api.binance.com/api/v3"
        self._uri_http["fut"] = "https://fapi.binance.com/fapi/v1"

        self._uri_ws = dict()
        self._uri_ws["spot"] = "wss://stream.binance.com/ws"
        self._uri_ws["fut"] = "wss://fstream.binance.com/ws"

    async def exchange_auth(self) -> set:
        api_key = fetch_credentials({"exchange": "binance"}).get("apiKey")

        # instance self._listen_key
        await self._acquire_listen_key(api_key)
        task = asyncio.create_task(self._keepalive_listen_key(api_key))
        return {task}

    async def _acquire_listen_key(self, api_key) -> None:
        uri = "https://api.binance.com/api/v1/userDataStream"
        headers = {"X-MBX-APIKEY": api_key}
        async with self.session.post(uri, headers=headers) as resp:
            data = await resp.json()
            self._listen_key = data["listenKey"]

    async def _keepalive_listen_key(self, api_key) -> None:
        uri = "https://api.binance.com/api/v1/userDataStream"
        headers = {"X-MBX-APIKEY": api_key}
        params = {"listenKey": self._listen_key}
        while True:
            async with self.session.put(uri, headers=headers, params=params) as resp:
                if resp.status == 200:
                    print(f"\nListen key refreshed: {self._listen_key}\n")
                    await asyncio.sleep(60 * 1)
                else:
                    print(f"Error: {resp.status}. Reconnecting...")
                    await asyncio.sleep(1)

    async def _exchange_client(self, id, r) -> None:
        uri = r.pop("uri")
        async for msg in WebSocket.recv_str(self.session, uri):
            await self.channels[id].put(msg)

    async def spawn_service(self, id, r) -> set:
        task = asyncio.create_task(self._exchange_client(id, r))
        return {task}
