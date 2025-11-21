#!/usr/bin/env python

import curses
import time
from pathlib import Path

KILO = 1024.0


def main(stdscr: curses.window) -> None:
    curses.use_default_colors()
    stdscr.nodelay(yes=True)

    min_lve = 500
    interval = 3
    sleep_cycles = interval * 10
    sort_pri = "out"
    sort_sec = "in"
    oldvals = {}
    filled = False
    refresh = True

    def bytes_to_human(num: float) -> str:
        for unit in ["KiB", "MiB"]:
            num /= KILO
            if abs(num) < KILO:
                return f"{num:.2f} {unit}/s"
        return f"{num:.2f} GiB/s"

    def sort_func(item: int) -> tuple:
        return bandwidth[item][sort_pri], bandwidth[item][sort_sec], item * -1

    with Path("/etc/login.defs").open("r") as file:
        for line in file:
            entry = line.split()
            if not entry:
                continue
            if entry[0] == "UID_MIN":
                min_lve = int(entry[1])
                break

    while True:
        while True:
            c = stdscr.getch()
            if c == -1:
                break
            if c == ord("i"):
                sort_pri = "in"
                sort_sec = "out"
                refresh = True
            elif c == ord("o"):
                sort_pri = "out"
                sort_sec = "in"
                refresh = True
            elif c == ord("q"):
                return
        if not refresh:
            time.sleep(0.1)
            sleep_cycles -= 1
            if sleep_cycles == 0 or not filled:
                refresh = True
                filled = True
            continue
        bandwidth: dict[int, dict[str, int]] = {}
        stdscr.clear()
        stdscr.addstr("   LVE ID             IN            OUT", curses.A_REVERSE)
        for lve in Path("/proc/lve/per-lve").iterdir():
            if not lve.name.isdigit():
                continue
            lve_net_stat = lve / "net_stat"
            lve_id = int(lve.name)
            if lve_id < min_lve or not lve_net_stat.is_file():
                continue
            for line in lve_net_stat.open("r"):
                dummy, _, _, traf_out, traf_in = line.split()
                if dummy.startswith("traf"):
                    break
            traf_in = int(traf_in)
            traf_out = int(traf_out)
            if traf_in == 0 and traf_out == 0:
                continue
            if not filled:
                bandwidth[lve_id] = {"in": 0, "out": 0}
            else:
                sleep_time = (interval / 0.1) - sleep_cycles
                bandwidth[lve_id] = {"in": (traf_in - oldvals[lve_id]["in"]) * 10 / sleep_time, "out": (traf_out - oldvals[lve_id]["out"]) * 10 / sleep_time}
            oldvals[lve_id] = {"in": traf_in, "out": traf_out}
        for lve_id in oldvals:
            if lve_id not in bandwidth:
                oldvals[lve_id] = {"in": 0, "out": 0}
        lines = 0
        for lve_id in sorted(bandwidth, key=sort_func, reverse=True):
            if bandwidth[lve_id]["in"] == 0 and bandwidth[lve_id]["out"] == 0:
                continue
            lines += 1
            stdscr.addstr(f"\n{lve_id:>9}{bytes_to_human(bandwidth[lve_id]['in']):>15}{bytes_to_human(bandwidth[lve_id]['out']):>15}")
            if lines == stdscr.getmaxyx()[0] - 1:
                break
        stdscr.move(0, 0)
        stdscr.refresh()
        refresh = False
        sleep_cycles = interval * 10


if __name__ == "__main__":
    curses.wrapper(main)
