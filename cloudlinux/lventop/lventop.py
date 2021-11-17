#!/usr/bin/env python

import sys
import os
import time
import curses


def main(stdscr):
    curses.use_default_colors()
    stdscr.nodelay(1)

    min_lve = 500
    interval = 3
    sleep_cycles = interval * 10
    sort_pri = 'out'
    sort_sec = 'in'
    oldvals = {}
    filled = False
    refresh = True

    def bytes_to_human(num):
        for unit in ['KiB', 'MiB']:
            num /= 1024.0
            if abs(num) < 1024.0:
                return "%.2f %s/s" % (num, unit)
        return "%.2f %s/s" % (num, 'GiB')

    def sort_func(item):
        return bandwidth[item][sort_pri], bandwidth[item][sort_sec], item * -1

    for line in open('/etc/login.defs', 'r'):
        entry = line.split()
        if not entry:
            continue
        if entry[0] == 'UID_MIN':
            min_lve = int(entry[1])
            break

    while True:
        while True:
            c = stdscr.getch()
            if c == -1:
                break
            elif c == ord('i'):
                sort_pri = 'in'
                sort_sec = 'out'
                refresh = True
            elif c == ord('o'):
                sort_pri = 'out'
                sort_sec = 'in'
                refresh = True
            elif c == ord('q'):
                return
        if not refresh:
            time.sleep(0.1)
            sleep_cycles -= 1
            if sleep_cycles == 0 or not filled:
                refresh = True
                filled = True
            continue
        bandwidth = {}
        stdscr.clear()
        stdscr.addstr('   LVE ID             IN            OUT',
                      curses.A_REVERSE)
        for lve_id in os.listdir('/proc/lve/per-lve/'):
            fname = os.path.join('/proc/lve/per-lve', lve_id, 'net_stat')
            if not lve_id.isdigit():
                continue
            lve_id = int(lve_id)
            if lve_id < min_lve or not os.path.isfile(fname):
                continue
            for line in open(fname, 'r'):
                dummy, lim_out, lim_in, traf_out, traf_in = line.split()
                if dummy == 'traf:':
                    break
            traf_in = int(traf_in)
            traf_out = int(traf_out)
            if traf_in == 0 and traf_out == 0:
                continue
            if not filled:
                bandwidth[lve_id] = {'in': 0, 'out': 0}
            else:
                sleep_time = (interval / 0.1) - sleep_cycles
                bandwidth[lve_id] = {
                    'in': (traf_in - oldvals[lve_id]['in']) * 10 / sleep_time,
                    'out': (traf_out - oldvals[lve_id]['out']) * 10 / sleep_time
                }
            oldvals[lve_id] = {'in': traf_in, 'out': traf_out}
        for lve_id in oldvals:
            if not lve_id in bandwidth:
                oldvals[lve_id] = {'in': 0, 'out': 0}
        lines = 0
        for lve_id in sorted(bandwidth, key=sort_func, reverse=True):
            if bandwidth[lve_id]['in'] == 0 and bandwidth[lve_id]['out'] == 0:
                continue
            lines += 1
            stdscr.addstr('\n%9s' % (lve_id) + '%15s' % (bytes_to_human(
                bandwidth[lve_id]['in'])) + '%15s' % (bytes_to_human(bandwidth[lve_id]['out'])))
            if lines == stdscr.getmaxyx()[0]-1:
                break
        stdscr.move(0, 0)
        stdscr.refresh()
        refresh = False
        sleep_cycles = interval * 10


if __name__ == '__main__':
    curses.wrapper(main)
