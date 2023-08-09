import abc


class BaseExchange(abc.ABC):
    @abc.abstractmethod
    async def exchange_auth(self) -> set:
        raise NotImplementedError

    @abc.abstractmethod
    async def spawn_stream(self, id, payload) -> set:
        raise NotImplementedError
