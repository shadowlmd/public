#!/bin/bash

declare -A V
C=0
N=0
SKIP_NOT_AFFECTED=""
SKIP_FULLY_MITIGATED=""

shopt -s nocasematch

for F in /sys/devices/system/cpu/vulnerabilities/*; do
	S=${F##*/}
	I=${#S}
	[[ $I -gt $N ]] && N=$I
	V[$S]=$(<$F)
done

((N++))

for K in "${!V[@]}"; do
	if [[ ${V[$K]} == "Not affected" ]]; then
		NOT_AFFECTED="y"
	elif [[ ! ${V[$K]} =~ (Vulnerable|unknown) ]]; then
		FULLY_MITIGATED="y"
	fi
	if ! [[ $SKIP_NOT_AFFECTED == "y" && $NOT_AFFECTED == "y" ]] && ! [[ $SKIP_FULLY_MITIGATED == "y" && $FULLY_MITIGATED == "y" ]]; then
		printf "%-${N}s: %s\n" "$K" "${V[$K]}"
		((C++))
	fi
	if [[ $C -eq 0 ]]; then
		echo "No matching vulnerabilities."
	fi
done
