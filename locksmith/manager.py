from pathlib import Path
import yaml

from .parsers import B3Parser, BinanceParser


class PswManager:
    def __init__(self):
        self._cred = self._load_credentials()

    def _load_credentials(self):
        dir = Path(__file__).resolve().parent
        file = f"{dir}/credentials.yml"

        with open(file, "r") as stream:
            return yaml.safe_load(stream)


# --------------------------------------------
def fetch_credentials(r):
    exchange = r.get("exchange")
    cred = PswManager()._cred.get(exchange)

    match exchange:
        case "b3":
            return B3Parser().parse_credentials(cred)

        case "binance":
            return BinanceParser().parse_credentials(cred)
