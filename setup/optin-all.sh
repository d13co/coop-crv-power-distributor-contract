#!/bin/bash

aid=$(cat config/aid.txt)

for addr in $(jq -r .addr config/accounts/coop*.json config/accounts/player*.keys.json); do
  sandbox goal asset optin --assetid $aid -a $addr &
done

wait
