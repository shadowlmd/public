#!/usr/bin/env python3

import asyncio

import websockets


def die(msg: str, code: int = 0):
    print(msg)
    exit(code)


async def main():
    try:
        websocket = await asyncio.wait_for(websockets.connect("wss://bbs.bsrealm.net:8803"), 5)
    except asyncio.exceptions.TimeoutError:
        die("Connection timed out", 1)
    except BaseException as e:
        die(repr(e), 1)

    resp = b""
    while b"EMSI_IRQ8E08" not in resp:
        try:
            r = await asyncio.wait_for(websocket.recv(), 20)
            resp += bytes(r)
        except BaseException:
            break

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
