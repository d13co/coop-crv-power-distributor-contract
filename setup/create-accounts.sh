#!/bin/bash

set -e

cd config/accounts

keys=$(ls  *.keys.json | sed 's/.keys.json//g')

cd ../..

echo Start: creating keys

for destination in $keys; do
  rm config/accounts/$destination.keys.json
  ./utils/create-account.sh config/accounts/$destination.keys.json &
done

wait

echo Start: funding

for file in config/accounts/*.keys.json; do
  addr=$(jq -r .addr $file)
  ./utils/fund.sh $addr &
  echo Started fund $addr
done

wait

echo Create accounts done
