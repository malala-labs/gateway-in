import asyncio

from malala.sockets import WebSocket
from malala.constants import ONE_MIN, TEN_MIN
from .base import BaseExchange
from locksmith import fetch_credentials

from utils.io import load_yaml

import pdb


class BinanceSpot(BaseExchange):
    def __init__(self, channels, session):
        self.channels = channels
        self.session = session
        self._streams = dict()

    async def exchange_auth(self) -> None:
        r = {"exchange": "binance"}
        self._api_key = fetch_credentials(r).get("apiKey")

    async def _start_stream(self, id, r) -> None:
        symbol = r.pop("symbol").split(":")[0].lower()
        endpoint = r.pop("endpoint")
        payload = {
            "id": id,
            "method": "SUBSCRIBE",
            "params": [f"{symbol}{endpoint}"],
        }
        headers = {"X-MBX-APIKEY": self._api_key}

        uri = "https://api.binance.com/api/v3/userDataStream"
        async with self.session.post(uri, headers=headers, data=payload) as resp:
            self._streams[id] = resp.json()["listenKey"]

    async def _listen_stream(self, id) -> None:
        uri = f"wss://stream.binance.com:9443/ws/{self._streams[id]}"
        async for msg in WebSocket.recv_str(self.session, uri):
            await self.channels[id].put(msg)

    async def _fetch_snapshot(self, id, r) -> None:
        symbol = r.pop("symbol").split(":")[0].upper()
        params = {"symbol": symbol, "limit": 1000}

        uri = f"https://api.binance.com/api/v3/depth"
        while True:
            async with self.session.post(uri, data=params) as resp:
                await self.channels[id].put(resp.data)
                await asyncio.sleep(TEN_MIN)

    async def spawn_service(self, id, r) -> set:
        tasks = set()
        if id not in self._streams:
            await self._start_stream(id, r)

        tasks.add(asyncio.create_task(self._fetch_snapshot(id, r)))
        tasks.add(asyncio.create_task(self._listen_stream(id)))
        return tasks
