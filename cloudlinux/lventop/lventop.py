#!/usr/bin/env python

import os
for lve_id in os.listdir('/proc/lve/per-lve/'):
  if os.path.isfile(os.path.join('/proc/lve/per-lve', lve_id, 'net_stat')):
    print(lve_id)
