#!/bin/bash

[[ -n "$2" ]] || exit 1

openssl s_client -quiet -connect $1:$2
