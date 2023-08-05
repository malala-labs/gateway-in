from .base import BaseParser


class B3Parser(BaseParser):
    def __init__(self):
        super().__init__()

    def parse_credentials(self, cred) -> dict[str, str]:
        cedro = cred.get("cedro")
        oms = cred.get("oms")

        auth = {
            "usr_cedro": cedro.get("key"),
            "psw_cedro": cedro.get("secret"),
            "usr_oms": oms.get("key"),
            "psw_oms": oms.get("secret"),
        }
        return auth


class BinanceParser(BaseParser):
    def __init__(self):
        super().__init__()

    def parse_credentials(self, cred) -> dict[str, str]:
        auth = {
            "apiKey": cred.get("key"),
            "secret": cred.get("secret"),
        }
        return auth
