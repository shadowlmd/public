#!/bin/bash

SKIP_NOT_AFFECTED="y"
SKIP_FULLY_MITIGATED="n"

declare -a VULN_K VULN_V

shopt -s nocasematch

if [[ $1 == "--all" ]]; then
	SKIP_NOT_AFFECTED="n"
elif [[ $1 == "--skip-mitigated" ]]; then
	SKIP_FULLY_MITIGATED="y"
fi

C=0
N=0
for F in /sys/devices/system/cpu/vulnerabilities/*; do
	S=${F##*/}
	I=${#S}
	[[ $I -gt $N ]] && N=$I
	VULN_K[$C]=$S
	VULN_V[$C]=$(<$F)
	((C++))
done

((N++))

F=0
for ((I = 0; I < C; I++)); do
	unset NOT_AFFECTED
	unset FULLY_MITIGATED
	if [[ ${VULN_V[$I]} == "Not affected" ]]; then
		NOT_AFFECTED="y"
	elif [[ ! ${VULN_V[$I]} =~ (Vulnerable|unknown) ]]; then
		FULLY_MITIGATED="y"
	fi
	[[ $SKIP_NOT_AFFECTED == "y" && $NOT_AFFECTED == "y" ]] && continue
	[[ $SKIP_FULLY_MITIGATED == "y" && $FULLY_MITIGATED == "y" ]] && continue
	printf "%-${N}s: %s\n" "${VULN_K[$I]}" "${VULN_V[$I]}"
	((F++))
done

if [[ $F -eq 0 ]]; then
	echo "No matching vulnerabilities."
fi
