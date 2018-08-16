#!/bin/bash

for F in /sys/devices/system/cpu/vulnerabilities/*; do
    printf "%-18s: " "${F##*/}"
    cat "$F"
done
