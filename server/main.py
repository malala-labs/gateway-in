import asyncio
import json
import aiohttp

from malala.sockets import UnixSocket, Transport
from malala.tasks import TaskManager
from client.b3 import B3
from client.binance import BinanceSpot

import pdb


class ExchangeConnector:
    def __init__(self):
        self.exchanges = dict()
        self.active_users = dict()
        self.channels = dict()
        self.tasks = dict()

    async def _start_exchanges(self) -> None:
        self.session = aiohttp.ClientSession()

        self.exchanges["b3"] = B3(
            self.session,
            self.channels,
        )
        self.exchanges["binance"] = BinanceSpot(
            self.session,
            self.channels,
        )
        for exchange in self.exchanges:
            await self.exchanges[exchange].exchange_auth()

    async def _start_server(self) -> None:
        path = "/tmp/gateway_in_socket"
        server = await UnixSocket.start_server(self._handle_client, path)

        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader, writer) -> None:
        fd = writer.get_extra_info("socket").fileno()
        print(f"Serving conn -- fd: #{fd}")

        async for msg in Transport.recv_json(reader):
            id, r = abs(hash(json.dumps(msg))), msg

        try:
            await self._subscribe(id, r)
            while True:
                msg = await self.channels[id].get()
                await Transport.send_str(msg, writer)

        except Exception:
            # -- housekeeping --------
            await self._unsubscribe(id)
            await UnixSocket.close_conn(writer)
            print(f"Closed conn -- fd: #{fd}")

    async def _subscribe(self, id, r) -> None:
        exchange = r.pop("exchange")

        if id not in self.active_users:
            # start new service
            self.active_users[id] = 0
            self.channels[id] = asyncio.Queue()
            self.tasks[id] = set()

            # creates a strong reference to running services
            self.tasks[id].update(
                await self.exchanges[exchange].spawn_stream(id, r),
            )

        self.active_users[id] += 1

    async def _unsubscribe(self, id) -> None:
        # update active users
        self.active_users[id] -= 1

        # terminate service
        if self.active_users[id] <= 0:
            await TaskManager.cancel_tasks(self.tasks[id])
            await self.channels[id].put(None)

            del self.active_users[id]
            del self.channels[id]
            del self.tasks[id]

    async def _monitor_event_loop(self) -> None:
        event_loop = asyncio.get_event_loop()
        await TaskManager.monitor_event_loop(event_loop, timeout=60)

    async def main(self) -> None:
        await self._monitor_event_loop()
        await self._start_exchanges()
        await self._start_server()


if __name__ == "__main__":
    try:
        asyncio.run(ExchangeConnector().main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
