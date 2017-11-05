#!/usr/bin/env python

import sys, os, time, curses

def main(stdscr):
    curses.use_default_colors()
    stdscr.nodelay(1)

    min_lve = 500
    interval = 5
    sort_pri = 'out'
    sort_sec = 'in'
    oldvals = {}
    filled = False

    def bytes_to_human(num):
        for unit in ['KiB', 'MiB']:
            num /= 1024.0
            if abs(num) < 1024.0:
                return "%.2f %s/s" % (num, unit)
        return "%.2f %s/s" % (num, 'GiB')

    def sort_func(item):
        return bandwidth[item][sort_pri], bandwidth[item][sort_sec], item * -1

    while True:
        while True:
            c = stdscr.getch()
            if c == -1:
                break
            elif c == ord('i'):
                sort_pri = 'in'
                sort_sec = 'out'
            elif c == ord('o'):
                sort_pri = 'out'
                sort_sec = 'in'
            elif c == ord('q'):
                return
        bandwidth = {}
        stdscr.clear()
        stdscr.addstr('   LVE ID             IN            OUT', curses.A_REVERSE)
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
            if not lve_id in oldvals:
                oldvals[lve_id] = { 'in': 0, 'out': 0 }
            bandwidth[lve_id] = {
                'in': (traf_in - oldvals[lve_id]['in']) / float(interval),
                'out': (traf_out - oldvals[lve_id]['out']) / float(interval)
            }
            oldvals[lve_id] = { 'in': traf_in, 'out': traf_out }
        for lve_id in oldvals:
            if not lve_id in bandwidth:
                oldvals[lve_id] = { 'in': 0, 'out': 0 }
        if filled:
            lines = 0
            for lve_id in sorted(bandwidth, key = sort_func, reverse = True):
                if bandwidth[lve_id]['in'] == 0 and bandwidth[lve_id]['out'] == 0:
                    continue
                lines += 1
                stdscr.addstr('\n%9s' % (lve_id) + '%15s' % (bytes_to_human(bandwidth[lve_id]['in'])) + '%15s' % (bytes_to_human(bandwidth[lve_id]['out'])));
                if lines == stdscr.getmaxyx()[0]-1:
                    break
        else:
            filled = True
        stdscr.move(0, 0)
        stdscr.refresh()
        time.sleep(interval)

if __name__ == '__main__':
    curses.wrapper(main)
