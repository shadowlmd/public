#!/usr/bin/env python

import os

min_lve = 500

for lve_id in os.listdir('/proc/lve/per-lve/'):
  if lve_id.isdigit() and int(lve_id) >= min_lve and os.path.isfile(os.path.join('/proc/lve/per-lve', lve_id, 'net_stat')):
    print(lve_id)
