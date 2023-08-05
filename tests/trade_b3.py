import asyncio
import json
import sys
import uuid
from malala.sockets import UnixSocket, Transport

# Usage:
# Create order: python -m test.trade_b3 create_order
# Cancel order: python -m test.trade_b3 cancel_order order_id


async def unix_client(r):
    path = "/tmp/gateway_out_socket"
    reader, writer = await UnixSocket.open_conn(path)
    await Transport.send_json(r, writer)

    # while True:
    #     msg = await Transport.recv_str(reader)
    #     print(msg)


async def main():
    # get service
    service = sys.argv[1]

    if service == "new":
        r = {
            "exchange": "b3",
            "service": "sendNewOrderSingle",
            "clordid": str(uuid.uuid4()),
            "account": "11536670",
            "price": "4600",
            "quote": "wdou23",
            "qtd": 1,
            "market": "XBMF",
            "type": "limited",
            "side": "buy",
            "sourceaddress": "#",
        }

    elif service == "cancel":
        orderid = sys.argv[2]

        r = {
            "exchange": "b3",
            "service": "cancelOrder",
            "origclordid": orderid,
            "clordid": orderid + ":cancel",
            "account": "11536670",
            "quote": "wdoq23",
            "qtd": 1,
            "market": "XBMF",
            "side": "buy",
            "sourceaddress": "#",
        }

    else:
        raise Exception("Invalid service")

    # send request
    print(json.dumps(r, indent=4))
    await unix_client(r)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt")
