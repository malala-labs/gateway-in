import asyncio

from malala.sockets import WebSocket
from .base import BaseExchange
from locksmith import fetch_credentials

import pdb


class BinanceSpot(BaseExchange):
    def __init__(self, session, channels):
        self.session = session
        self.channels = channels
        self._streams = dict()

    async def exchange_auth(self) -> None:
        r = {"exchange": "binance"}
        self._api_key = fetch_credentials(r).get("apiKey")

    async def _start_stream(self, id) -> None:
        # symbol = r.pop("symbol").split(":")[0].lower()
        # endpoint = r.pop("endpoint")
        # payload = {
        #     "id": id,
        #     "method": "SUBSCRIBE",
        #     "params": [f"{symbol}{endpoint}"],
        # }
        headers = {"X-MBX-APIKEY": self._api_key}

        uri = "https://api.binance.com/api/v1/userDataStream"
        async with self.session.post(uri, headers=headers, data={}) as resp:
            msg = await resp.json()
            self._streams[id] = msg["listenKey"]

    async def _listen_stream(self, id, r) -> None:
        symbol = r.pop("symbol").split(":")[0].lower()
        endpoint = r.pop("endpoint")
        payload = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol}{endpoint}"],
            "id": 2,
        }

        # _endpoint = f"{symbol}{endpoint}"
        # pdb.set_trace()
        uri = f"wss://stream.binance.com:9443/ws/{self._streams[id]}"
        print(uri)
        # pdb.set_trace()

        # async with self.session.ws_connect(uri) as ws:
        #     # resp = await ws.send_json(payload)
        #     # print(resp)
        #     # pdb.set_trace()

        #     async for msg in ws:
        #         print(msg)
        #         pdb.set_trace()

        await WebSocket.send_json(self.session, uri, payload)
        async for msg in WebSocket.recv_str(self.session, uri):
            pdb.set_trace()
            print(msg)

            await self.channels[id].put(msg)

    async def spawn_stream(self, id, r) -> set:
        tasks = set()
        if id not in self._streams:
            await self._start_stream(id)

        await self._listen_stream(id, r)

        tasks.add(asyncio.create_task(self._listen_stream(id, r)))
        return tasks
