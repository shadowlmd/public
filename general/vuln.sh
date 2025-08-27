#!/bin/bash

declare -A V
C=0
N=0
SKIP_NOT_AFFECTED="y"
SKIP_FULLY_MITIGATED="n"

shopt -s nocasematch

if [[ $1 == "--all" ]]; then
	SKIP_NOT_AFFECTED="n"
elif [[ $1 == "--skip-mitigated" ]]; then
	SKIP_FULLY_MITIGATED="y"
fi

for F in /sys/devices/system/cpu/vulnerabilities/*; do
	S=${F##*/}
	I=${#S}
	[[ $I -gt $N ]] && N=$I
	V[$S]=$(<$F)
done

((N++))

for K in "${!V[@]}"; do
	unset NOT_AFFECTED
	unset FULLY_MITIGATED
	if [[ ${V[$K]} == "Not affected" ]]; then
		NOT_AFFECTED="y"
	elif [[ ! ${V[$K]} =~ (Vulnerable|unknown) ]]; then
		FULLY_MITIGATED="y"
	fi
	[[ $SKIP_NOT_AFFECTED == "y" && $NOT_AFFECTED == "y" ]] && continue
	[[ $SKIP_FULLY_MITIGATED == "y" && $FULLY_MITIGATED == "y" ]] && continue
	printf "%-${N}s: %s\n" "$K" "${V[$K]}"
	((C++))
done

if [[ $C -eq 0 ]]; then
	echo "No matching vulnerabilities."
fi
