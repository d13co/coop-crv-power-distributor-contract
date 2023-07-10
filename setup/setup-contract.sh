#!/bin/bash

set -e

source ./utils/bigprint.sh

# deploy
bigprint Deploying

python3 deploy.py

app_addr=$(jq -r .app_addr config/deploy.json)

# fund app addr
bigprint Funding app addr

utils/fund.sh $app_addr

bigprint Finished setting up contract
