#!/bin/bash

set -e

creator=$(jq -r .addr config/accounts/coophair.keys.json)
name="CRV DAO Voting Power"
unit="CRVPower"

output=$(sandbox goal asset create --creator $creator --name "$name" --unitname "$unit" --decimals 6 --total 1000000000000000 --defaultfrozen)

aid=$(echo -e "$output" | grep "Created asset with asset index" | grep -oE '[0-9]+')

echo -n $aid > config/aid.txt

echo Asset creation done $aid
