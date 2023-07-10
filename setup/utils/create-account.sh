#!/bin/bash

set -e

addr=$(sandbox goal account new | grep -o 'address.*$' | awk '{print $2}')

key=$(sandbox goal account export -a $addr | cut -d'"' -f2)

jq --null-input --arg addr $addr --arg key "$key" '{ addr: $addr, key: $key }' | tee $1
