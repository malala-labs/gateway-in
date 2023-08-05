import asyncio
import json
import sys

from malala.sockets import UnixSocket, Transport


async def unix_client(r) -> None:
    path = "/tmp/gateway_in_socket"
    reader, writer = await UnixSocket.open_conn(path)

    uri = "wss://stream.binance.com/ws/btcusdt@depth@100ms"
    r = {"exchange": "binance", "uri": uri}
    await Transport.send_json(r, writer)
    writer.write_eof()

    try:
        async for msg in Transport.recv_bytes(reader):
            print(msg)
    except Exception:
        await UnixSocket.close_conn(writer)


async def main(service) -> None:
    if service == "book":
        r = {
            "exchange": "binance",
            "service": "subscribe_book",
            "symbol": "btcusdt:spot",
        }

    elif service == "orders":
        r = {
            "exchange": "binance",
            "service": "subscribe_orders",
        }

    else:
        raise ValueError("Invalid service")

    print(json.dumps(r, indent=4))
    await unix_client(r)


if __name__ == "__main__":
    try:
        service = sys.argv[1]
        asyncio.run(main(service))
    except KeyboardInterrupt as e:
        print(e)
