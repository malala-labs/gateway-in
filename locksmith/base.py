import abc


class BaseParser(abc.ABC):
    @abc.abstractmethod
    def parse_credentials(self, cred) -> dict[str, str]:
        raise NotImplementedError
