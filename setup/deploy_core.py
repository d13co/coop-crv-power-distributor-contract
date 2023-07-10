import base64

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from sys import path
from os import chdir
from accounts import get_creator_private_key
from json import loads, dumps

path.insert(1, '../common')
chdir('../common')
from client import *

path.insert(1, '../contract')
chdir('../contract')
from sc import get_contracts

path.insert(1, '../setup')
chdir('../setup')

# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])

# create new application
def deploy_app(client, app_id, private_key, global_schema="", local_schema=""):
    approval_program, clear_program, contract = get_contracts()

    # compile program to binary
    approval_program_compiled = compile_program(client, approval_program)

    # compile program to binary
    clear_program_compiled = compile_program(client, clear_program)

    chdir('../contract')
    # compile program to TEAL assembly
    with open("./approval.teal", "w") as f:
        f.write(approval_program)

    # compile program to TEAL assembly
    with open("./clear.teal", "w") as f:
        f.write(clear_program)

    with open("./contract.json", "w") as f:
        import json
        f.write(json.dumps(contract.dictify()))

    chdir('../setup')

    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    if app_id == 0:
        # create unsigned transaction
        txn = transaction.ApplicationCreateTxn(sender, params, on_complete, approval_program_compiled, clear_program_compiled, global_schema, local_schema, extra_pages=3)
    else:
        txn = transaction.ApplicationUpdateTxn(sender, params, app_id, approval_program_compiled, clear_program_compiled)

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

    if app_id == 0:
        app_id = transaction_response['application-index']
        return app_id
