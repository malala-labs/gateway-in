import asyncio
import json
import sys

from malala.sockets import UnixSocket, Transport


async def unix_client(r):
    path = "/tmp/gateway_in_socket"
    reader, writer = await UnixSocket.open_conn(path)
    await Transport.send_json(r, writer)

    while True:
        msg = await Transport.recv_str(reader)
        print(msg)


async def main(service):
    if service == "book":
        r = {
            "exchange": "b3",
            "module": "quotes",
            "service": "aggregatedBook",
            "parameterGet": "wdou23",
            "parameters": {
                "subsbribetype": "1",
                "delay": "10",
            },
        }

    elif service == "orders":
        r = {
            "exchange": "b3",
            "module": "negotiation",
            "service": "dailyOrder",
            "parameters": {
                "account": "11536670",
                "market": "XBMF",
                "dispatch": "true",
                "history": "true",
            },
        }

    else:
        raise Exception("Invalid service", service)

    print(json.dumps(r, indent=4))
    await unix_client(r)


if __name__ == "__main__":
    try:
        service = sys.argv[1]
        asyncio.run(main(service))

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        print(e)
