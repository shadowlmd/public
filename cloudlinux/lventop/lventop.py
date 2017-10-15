#!/usr/bin/env python3

import os  
for lveid in os.listdir('/proc/lve/per-lve/'):
  if os.path.isfile(os.path.join('/proc/lve/per-lve', lveid, 'net_stat')):
    print(fn)
