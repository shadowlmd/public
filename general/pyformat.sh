#! /bin/bash

[[ $1 =~ \.py$ ]] || exit 1

echo "Formatting $1 with isort and autopep8.."

isort -l 150 "$1"
autopep8 --aggressive -i --max-line-length 150 "$1"
