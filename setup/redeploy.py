import base64

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from sys import argv, path
from os import chdir

path.insert(1, '../common')
chdir('../common')
from client import *
from accounts import get_creator_private_key

path.insert(1, '../setup')
chdir('../setup')

from deploy_core import deploy_app

default_last_app_id=0
with open("config/deploy.json", "r") as f:
    default_last_app_id=loads(f.read())["app_id"]

app_id=int(argv[1]) if len(argv) > 1 else default_last_app_id

client = get_client()

# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])

# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn) :
    private_key = mnemonic.to_private_key(mn)
    return private_key

# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            if formatted_key == 'voted':
                formatted_value = base64.b64decode(value['bytes']).decode('utf-8')
            else:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted

# helper function to read app global state
def read_global_state(client, app_id):
    app = client.application_info(app_id)
    global_state = app['params']['global-state'] if "global-state" in app['params'] else []
    return format_state(global_state)


# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationUpdateTxn(sender, params, app_id, approval_program, clear_program)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 4)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))

    except Exception as err:
        print(err)
        return

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    # app_id = transaction_response['application-index']
    # print("app_id=", app_id, sep="")

    return


def main() :
    # initialize an algodClient
    algod_client = get_client()

    creator_private_key = get_creator_private_key()

    print("-----------------------------------------------")
    print("Redeploying contract", app_id)
    print("-----------------------------------------------")

    # redeploy application
    deploy_app(algod_client, app_id, creator_private_key)

    print("Redeployed to App ID:", app_id)

main()
