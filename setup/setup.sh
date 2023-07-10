#!/bin/bash

set -e

source utils/bigprint.sh

# install dependencies
pip3 install -q -r ../requirements.txt

bigprint Creating Accounts

# create accounts
./create-accounts.sh

bigprint Creating Asset

# create asset with creator account
./create-asset.sh

bigprint Optin Asset

./optin.sh

bigprint Setting up contract
# deploy & setup contract
./setup-contract.sh


coophair=$(jq -r .addr config/accounts/coophair.keys.json)
coophold=$(jq -r .addr config/accounts/coophold.keys.json)
app_addr=$(jq -r .app_addr config/deploy.json)

bigprint rekeying holding addresses to contract $app_addr

python3 ../clients/rekey.py $coophair $app_addr yes
python3 ../clients/rekey.py $coophold $app_addr yes

python3 ../clients/call_unfreeze.py "" $coophold

bigprint setup.sh success
