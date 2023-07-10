#!/bin/bash

set -o xtrace

for player in $(ls ../setup/config/accounts/player*.keys.json); do
  python3 call_allocate_vp.py "" 100000000 $(jq -r .addr $player) &
done

wait
