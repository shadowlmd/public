#!/usr/bin/env python

from __future__ import print_function
import os, time

min_lve = 500
sort_type = 'o'
oldstats = {}
newstats = {}

while True:
    for lve_id in os.listdir('/proc/lve/per-lve/'):
        fname = os.path.join('/proc/lve/per-lve', lve_id, 'net_stat')
        if lve_id.isdigit() and int(lve_id) >= min_lve and os.path.isfile(fname):
            with open(fname, 'r') as in_file:
                for line in in_file:
                    dummy, lim_out, lim_in, traf_out, traf_in = line.split()
                    if dummy == 'traf:':
                        break
            if not lve_id in oldstats:
                oldstats[lve_id] = { 'in': 0, 'out': 0 }
            newstats[lve_id] = { 'in': traf_in - oldstats[lve_id]['in'], 'out': traf_out - oldstats[lve_id]['out'] }
            oldstats[lve_id] = { 'in': traf_in, 'out': traf_out }
    for lve_id in oldstats:
        if not lve_id in newstats:
            del oldstats[lve_id]
    for lve_id in newstats:
        print(lve_id, ' ', newstats[lve_id]['in'], ' ', newstats[lve_id]['out']);
    time.sleep(1)