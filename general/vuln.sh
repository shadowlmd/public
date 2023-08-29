#!/bin/bash

for F in /sys/devices/system/cpu/vulnerabilities/*; do
    printf "%-21s: " "${F##*/}"
    cat "$F"
done
