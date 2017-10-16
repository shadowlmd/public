#!/usr/bin/env python

import sys, os, time, curses

def main(stdscr):
    curses.use_default_colors()
    stdscr.nodelay(1)

    min_lve = 500
    sort_pri = 'out'
    sort_sec = 'in'
    oldvals = {}

    def bytes_to_human(num):
        for unit in ['KiB', 'MiB']:
            num /= 1024.0
            if abs(num) < 1024.0:
                return "%.2f %s/s" % (num, unit)
        return "%.2f %s/s" % (num, 'GiB')

    def sort_func(item):
        return bandwidth[item][sort_pri], bandwidth[item][sort_sec], item * -1

    def compare_func(x, y):
        for index in range(0, len(x)):
            cmp_r = x[index] - y[index]
            if cmp_r != 0:
                return cmp_r

    while True:
        c = stdscr.getch()
        if c == ord('i'):
            sort_pri = 'in'
            sort_sec = 'out'
        elif c == ord('o'):
            sort_pri = 'out'
            sort_sec = 'in'
        elif c == ord('q'):
            break
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
            with open(fname, 'r') as in_file:
                for line in in_file:
                    dummy, lim_out, lim_in, traf_out, traf_in = line.split()
                    if dummy == 'traf:':
                        break
            traf_in = int(traf_in)
            traf_out = int(traf_out)
            if not lve_id in oldvals:
                oldvals[lve_id] = { 'in': 0, 'out': 0 }
            bandwidth[lve_id] = { 'in': traf_in - oldvals[lve_id]['in'], 'out': traf_out - oldvals[lve_id]['out'] }
            oldvals[lve_id] = { 'in': traf_in, 'out': traf_out }
        for lve_id in oldvals:
            if not lve_id in bandwidth:
                del oldvals[lve_id]
        lines = 0
        for lve_id in sorted(bandwidth, key = sort_func, cmp = compare_func, reverse = True):
            lines += 1
            stdscr.addstr('\n%9s' % (lve_id) + '%15s' % (bytes_to_human(bandwidth[lve_id]['in'])) + '%15s' % (bytes_to_human(bandwidth[lve_id]['out'])));
            if lines == stdscr.getmaxyx()[0]-1:
                break
        stdscr.move(0, 0)
        stdscr.refresh()
        time.sleep(1)

if __name__ == '__main__':
    curses.wrapper(main)
