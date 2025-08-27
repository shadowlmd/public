#!/bin/bash

SPACESTR="          "
FILENAME="$1"
OLDSPACES=${2:-2}
NEWSPACES=${3:-4}

die() {
	echo "$*" 1>&2
	exit 1
}

usage() {
	die "Usage: ${0##*/} filename [oldspaces [newspaces]]"
}

[[ -n $FILENAME ]] || usage
[[ -w $FILENAME ]] || die "File '$FILENAME' is not writable"
[[ $OLDSPACES =~ ^[1-9]$ && $NEWSPACES =~ ^[1-9]$ && $OLDSPACES != $NEWSPACES ]] || usage
[[ -e "${FILENAME}.backup" ]] && die "File '${FILENAME}.backup' already exists, can't proceed"

cp -a "$FILENAME" "${FILENAME}.backup"

while true; do
	sed -r 's/(^|\t+)'"${SPACESTR:0:OLDSPACES}"'/\1\t/g' "$FILENAME" >"${FILENAME}.2to4tmp"
	cmp -s "$FILENAME" "${FILENAME}.2to4tmp" && break
	cp "${FILENAME}.2to4tmp" "$FILENAME"
done

while true; do
	sed -r 's/(^|\s+)\t/\1'"${SPACESTR:0:NEWSPACES}"'/g' "$FILENAME" >"${FILENAME}.2to4tmp"
	cmp -s "$FILENAME" "${FILENAME}.2to4tmp" && break
	cp "${FILENAME}.2to4tmp" "$FILENAME"
done

rm -f "${FILENAME}.2to4tmp"
