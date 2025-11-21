#!/bin/bash

RUFF_LINE_LENGTH=160
RUFF_SELECT=ALL
RUFF_IGNORE=BLE001,D100,D101,D103,D107,D203,D213,EM101,RUF001,S110,T201

[[ $1 =~ \.py$ ]] || exit 1

echo "Formatting $1 with ruff.."
ruff --isolated --config "line-length = $RUFF_LINE_LENGTH" format --no-cache "$1"

echo "Checking and fixing $1 with ruff.."
ruff --isolated --config "line-length = $RUFF_LINE_LENGTH" check --select $RUFF_SELECT --ignore $RUFF_IGNORE --no-cache --fix "$1"
