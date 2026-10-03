#!/usr/bin/env python3
"""Make a type 2+ packet (FTS-0001, FSC-0039) with one message.

Field lengths are not checked: the tool makes broken packets for pktsan.
"""

import argparse
import datetime
import os
import re
import struct
import time
from pathlib import Path


def address(s: str) -> tuple[int, ...]:
    m = re.fullmatch(r"(\d+):(\d+)/(\d+)(?:\.(\d+))?", s)
    if not m:
        msg = f"not zone:net/node[.point]: {s!r}"
        raise argparse.ArgumentTypeError(msg)
    return tuple(int(x or 0) for x in m.groups())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text_file", help="message text file (LF or CRLF line ends)")
    ap.add_argument("-f", "--from", dest="orig", type=address, required=True, help="origin address zone:net/node[.point]")
    ap.add_argument("-t", "--to", dest="dest", type=address, required=True, help="destination address zone:net/node[.point]")
    ap.add_argument("-a", "--area", help="echo area tag; netmail if not given")
    ap.add_argument("--from-name", default="Sysop", help="default: %(default)s")
    ap.add_argument("--to-name", default="All", help="default: %(default)s")
    ap.add_argument("-s", "--subject", default="", help="default: empty")
    ap.add_argument("--origin", default="mkpkt", help="origin line text, default: %(default)s")
    ap.add_argument("-p", "--password", default="", help="packet password")
    ap.add_argument(
        "-d",
        "--date",
        type=datetime.datetime.fromisoformat,
        default=datetime.datetime.now().astimezone().replace(microsecond=0),
        help="YYYY-MM-DD HH:MM:SS, default: now",
    )
    ap.add_argument(
        "--attr",
        type=lambda s: int(s, 0),
        default=None,
        help="message attribute: a bit mask (FTS-0001), e.g. 0x83 = private (1) + crash (2) + kill/sent (0x80); "
        "decimal, 0x hex or 0b binary; default: 0 for echomail, 1 (private) for netmail",
    )
    ap.add_argument("-o", "--output", help="output packet, default: XXXXXXXX.pkt from the time")
    a = ap.parse_args()

    oz, onet, onode, opt = a.orig
    dz, dnet, dnode, dpt = a.dest
    d = a.date
    enc = os.fsencode

    hdr = struct.pack(
        "<12H BB 8s HH HHBBH HHHH 4s",
        onode,
        dnode,
        d.year,
        d.month - 1,
        d.day,
        d.hour,
        d.minute,
        d.second,
        0,
        2,
        onet,
        dnet,
        0xFE,
        0,
        enc(a.password),
        oz,
        dz,
        0,
        0x0100,
        0,
        0,
        0x0001,
        oz,
        dz,
        opt,
        dpt,
        b"",
    )

    lines = Path(a.text_file).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r").split(b"\r")
    if lines[-1] == b"":
        lines.pop()

    # SEEN-BY, ^APATH, ^AVia etc. at the end stay after the origin line
    n = len(lines)
    while n and lines[n - 1].startswith((b"SEEN-BY:", b"\x01")):
        n -= 1
    body, tail = lines[:n], lines[n:]

    orig = b"%d:%d/%d" % (oz, onet, onode) + (b".%d" % opt if opt else b"")
    if a.area is not None:
        head = [b"AREA:" + enc(a.area)]
        tail = [b"SEEN-BY: %d/%d" % (onet, onode), *tail, b"\x01PATH: %d/%d" % (onet, onode)]
        attr = 0
    else:
        head = [b"\x01INTL %d:%d/%d %d:%d/%d" % (dz, dnet, dnode, oz, onet, onode)]
        if opt:
            head.append(b"\x01FMPT %d" % opt)
        if dpt:
            head.append(b"\x01TOPT %d" % dpt)
        attr = 1
    # serial: 1/34 s ticks within a 4-year cycle, 1461 * 86400 * 34 < 2^32
    serial = int(time.time() * 34) % (1461 * 86400 * 34)
    head.append(b"\x01MSGID: %s %08x" % (orig, serial))
    origin = b" * Origin: " + enc(a.origin) + b" (" + orig + b")"
    text = b"".join(line + b"\r" for line in [*head, *body, origin, *tail])
    if a.attr is not None:
        attr = a.attr

    msg = (
        struct.pack("<7H", 2, onode, dnode, onet, dnet, attr, 0)
        + struct.pack("20s", d.strftime("%d %b %y  %H:%M:%S").encode())
        + enc(a.to_name)
        + b"\0"
        + enc(a.from_name)
        + b"\0"
        + enc(a.subject)
        + b"\0"
        + text
        + b"\0"
    )

    out = a.output or "%08x.pkt" % (int(time.time()) & 0xFFFFFFFF)
    with Path(out).open("xb") as fh:
        fh.write(hdr + msg + b"\0\0")
    print(out)


if __name__ == "__main__":
    main()
