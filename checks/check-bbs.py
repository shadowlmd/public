#!/usr/bin/env python3

import asyncio
import sys

from websockets.client import connect


def die(msg: str, code: int = 0) -> None:
    print(msg)
    sys.exit(code)


async def main() -> None:
    try:
        websocket = await asyncio.wait_for(connect("wss://home.bsrealm.net:8803"), 5)
    except asyncio.exceptions.TimeoutError:
        die("Connection timed out", 1)
    except Exception as e:
        die(repr(e), 1)

    resp = b""
    try:
        while b"EMSI_IRQ8E08" not in resp:
            r = await asyncio.wait_for(websocket.recv(), 20)
            if isinstance(r, bytes):
                resp += r
            elif isinstance(r, str):
                resp += r.encode(encoding="latin1")
    except asyncio.exceptions.TimeoutError:
        pass

    websocket.close_timeout = 1
    await websocket.close()

    if b"EMSI_IRQ8E08" in resp:
        die("Got valid response", 0)
    elif len(resp.strip()) == 0:
        die("Got empty response", 1)
    else:
        resp = resp.decode(encoding="CP866")
        die(f"Got invalid response:\n\n{resp}", 1)


if __name__ == "__main__":
    asyncio.run(main())
