#!/bin/bash

set -o xtrace

for player in ../setup/config/accounts/player*.keys.json; do
# for player in $(ls ../setup/config/accounts/player*.keys.json | head -n 64); do
  node ../js-clients/call-claim.js $player
done

wait
