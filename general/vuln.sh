#!/bin/bash

SKIP_NOT_AFFECTED="y"
SKIP_FULLY_MITIGATED="n"

print_help() {
	cat <<-'EOF'
		Usage: check-vulns.sh [options]

		Options:
		  -a   show all entries (don't skip "Not affected")
		  -s   skip entries considered fully mitigated
		  -h   show this help and exit
	EOF
}

while getopts ":ash" OPT; do
	case "$OPT" in
	a) SKIP_NOT_AFFECTED="n" ;;
	s) SKIP_FULLY_MITIGATED="y" ;;
	h)
		print_help
		exit 0
		;;
	\?)
		echo "Unknown option: -$OPTARG" >&2
		exit 2
		;;
	esac
done

declare -a VULN_K VULN_V

shopt -s nocasematch

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
