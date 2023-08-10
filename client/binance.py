import asyncio

from malala.sockets import WebSocket
from malala.constants import TEN_MIN
from .base import BaseExchange
from locksmith import fetch_credentials

import pdb
import json
import time


class BinanceSpot(BaseExchange):
    def __init__(self, session, channels):
        self.session = session
        self.channels = channels
        self._streams = dict()

        self._base_uri = {
            "ws": "wss://stream.binance.com:9443/ws",
            "rest": "https://api.binance.com/api/v3",
        }

    async def exchange_auth(self) -> None:
        r = {"exchange": "binance"}
        self._api_key = fetch_credentials(r).get("apiKey")

    async def _start_stream(self, id) -> None:
        headers = {"X-MBX-APIKEY": self._api_key}
        uri = f"{self._base_uri['rest']}/userDataStream"

        async with self.session.post(uri, headers=headers, data={}) as resp:
            _json = await resp.json()
            self._streams[id] = _json["listenKey"]

    async def _listen_stream(self, id, r) -> None:
        symbol = r.get("symbol").split(":")[0].lower()
        endpoint = r.get("endpoint")
        payload = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol}{endpoint}"],
            "id": id,
        }
        uri = f"{self._base_uri['ws']}/{self._streams[id]}"

        async with self.session.ws_connect(uri, heartbeat=TEN_MIN) as ws:
            await ws.send_json(payload)
            _json = await ws.receive_json()
            assert _json.get("result") == None

            async for msg in ws:
                print(msg.data)
                await self.channels[id].put(msg.data)

    async def spawn_stream(self, id, r) -> set:
        tasks = set()

        if id not in self._streams:
            await self._start_stream(id)

        # await self._listen_stream(id, r)

        tasks.add(asyncio.create_task(self._listen_stream(id, r)))
        return tasks
