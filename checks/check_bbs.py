#!/usr/bin/env python3

import asyncio
import websockets


async def read_from_bbs():
    async with websockets.connect("wss://bbs.bsrealm.net:8803") as websocket:
        resp = b""
        while True:
            try:
                r = await asyncio.wait_for(websocket.recv(), 10)
                resp += bytes(r)
                if b"EMSI_IRQ8E08" in resp:
                    break
            except BaseException:
                break
        return resp


def die(msg: str, code: int = 0):
    print(msg)
    exit(code)


def main():
    try:
        r = asyncio.run(asyncio.wait_for(read_from_bbs(), 15))
    except asyncio.exceptions.TimeoutError:
        die("Check timed out", 1)
    except BaseException as e:
        die(repr(e), 1)

    if b"EMSI_IRQ8E08" in r:
        die("Got valid response", 0)
    elif len(r.strip()) == 0:
        die("Got empty response", 1)
    else:
        r = r.decode(encoding="CP866")
        die(f"Got invalid response:\n\n{r}", 1)


if __name__ == "__main__":
    main()
