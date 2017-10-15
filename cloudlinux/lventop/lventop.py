#!/usr/bin/env python

import sys, os, time, curses

def size_fmt(num):
    for unit in ['KiB', 'MiB']:
        num /= 1024.0
        if abs(num) < 1024.0:
            return "%.2f %s/s" % (num, unit)
    return "%.2f %s/s" % (num, 'GiB')

def main(stdscr):
    stdscr.nodelay(1)

    min_lve = 500
    sort_by = 'out'
    oldvals = {}
    bandwidth = {}

    while True:
        c = stdscr.getch()
        if c == 105:
            sort_by = 'in'
        elif c == 111:
            sort_by = 'out'
        elif c == 113:
            break
        stdscr.clear()
        stdscr.addstr('   LVE ID             IN            OUT\n')
        for lve_id in os.listdir('/proc/lve/per-lve/'):
            fname = os.path.join('/proc/lve/per-lve', lve_id, 'net_stat')
            if lve_id.isdigit() and int(lve_id) >= min_lve and os.path.isfile(fname):
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
        for lve_id in sorted(bandwidth, key = lambda item: bandwidth[item][sort_by], reverse = True):
            lines += 1
            stdscr.addstr('%9s' % (lve_id) + '%15s' % (size_fmt(bandwidth[lve_id]['in'])) + '%15s' % (size_fmt(bandwidth[lve_id]['out'])) + '\n');
            if lines == 10:
                break
        stdscr.move(0, 0)
        stdscr.refresh()
        time.sleep(1)

if __name__ == '__main__':
    curses.wrapper(main)
