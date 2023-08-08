import asyncio
import aiohttp
import glob
import yaml

from client.b3 import B3
from client.binance import Binance
from utils.io import load_yaml


import pdb


class ExchangeConnector:
    def __init__(self):
        self.exchanges = dict()
        self.channels = dict()
        self.tasks = dict()

    async def _start_exchanges(self) -> None:
        self.session = aiohttp.ClientSession()

        self.exchanges["b3"] = B3(
            self.channels,
            self.session,
        )
        self.exchanges["binance"] = Binance(
            self.channels,
            self.session,
        )
        # for exchange in self.exchanges:
        #     self.tasks[0].update(
        #         await self.exchanges[exchange].exchange_auth(),
        #     )

    async def _start_books(self) -> None:
        files = glob.glob("config/*.yaml")
        for file in files:
            config = load_yaml(file)
        pdb.set_trace()

    async def _start_server(self) -> None:
        pass

    async def main(self) -> None:
        await self._start_exchanges()
        await self._start_books()


if __name__ == "__main__":
    try:
        asyncio.run(ExchangeConnector().main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
