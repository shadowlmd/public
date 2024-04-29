#!/bin/bash

N=0

for F in /sys/devices/system/cpu/vulnerabilities/*; do
	S=${F##*/}
	I=${#S}
	[[ $I -gt $N ]] && N=$I
done

((N++))

for F in /sys/devices/system/cpu/vulnerabilities/*; do
	printf "%-${N}s: " "${F##*/}"
	cat "$F"
done
