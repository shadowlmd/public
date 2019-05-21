#!/bin/bash

## use https://ipwhois.cf service from console ##

if ! which w3m 1>/dev/null 2>&1; then
    echo "Please install w3m first"
    exit 1
fi


if [[ -z "$1" ]]; then
  echo "Usage: ${0##*/} ip_address [as]"
  exit 1
fi

URL="https://ipwhois.bsrealm.net/?query=$1"
[[ "${2,,}" == "as" ]] && URL="${URL}&as=on"

w3m -dump "$URL" | tail -n +2 | head -n -1 | awk 'BEGIN { P = 0 }; { if (P == 0) { if (NF != 0) { P = 1 } }; if (P != 0) { print } }' | tac | awk 'BEGIN { P = 0 }; { if (P == 0) { if (NF != 0) { P = 1 } }; if (P != 0) { print } }' | tac
