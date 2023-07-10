import base64

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from sys import path
from os import chdir
from json import loads, dumps
from algosdk.logic import get_application_address

path.insert(1, '../common')
chdir('../common')
from client import *
from accounts import get_creator_private_key

path.insert(1, '../setup')
chdir('../setup')

from deploy_core import deploy_app

def main() :
    # initialize an algodClient
    algod_client = get_client()

    # define private keys
    creator_private_key = get_creator_private_key()

    # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 4
    global_bytes = 2
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    print("-----------------------------------------------")
    print("\tDeploying new CRV Power Distibutor contract")
    print("-----------------------------------------------")

    # create new application
    app_id = deploy_app(algod_client, 0, creator_private_key, global_schema, local_schema)

    print("App ID:", app_id)
    print("App address:", get_application_address(app_id))

    with open("config/deploy.json", "r") as f:
        existing = loads(f.read())
        f.close()

    existing["app_id"] = app_id
    existing["app_addr"] = get_application_address(app_id)

    with open("config/deploy.json", "w") as f:
        f.write(dumps(existing))
    
main()
