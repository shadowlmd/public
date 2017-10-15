#!/usr/bin/env python

from __future__ import print_function
import sys, os, time

min_lve = 500
sort_type = 'o'
oldstats = {}
newstats = {}

def size_fmt(num):
    for unit in ['KiB', 'MiB']:
        num /= 1024.0
        if abs(num) < 1024.0:
            return "%.2f %s/s" % (num, unit)
    return "%.2f %s/s" % (num, 'GiB')

while True:
    sys.stderr.write("\x1b[2J\x1b[H")
    print('   LVE ID          IN         OUT')
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
            if not lve_id in oldstats:
                oldstats[lve_id] = { 'in': 0, 'out': 0 }
            newstats[lve_id] = { 'in': traf_in - oldstats[lve_id]['in'], 'out': traf_out - oldstats[lve_id]['out'] }
            oldstats[lve_id] = { 'in': traf_in, 'out': traf_out }
    for lve_id in oldstats:
        if not lve_id in newstats:
            del oldstats[lve_id]
    for lve_id in newstats:
        print('%9s' % lve_id + '%12s' % size_fmt(newstats[lve_id]['in']) + '%12s' % size_fmt(newstats[lve_id]['out']));
    time.sleep(1)
