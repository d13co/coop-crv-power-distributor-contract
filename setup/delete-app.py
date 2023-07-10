import base64

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from sys import path, argv
from os import chdir
from json import loads, dumps
from algosdk.logic import get_application_address

path.insert(1, '../common')
chdir('../common')
from client import *
from accounts import get_creator_private_key

path.insert(1, '../setup')
chdir('../setup')

default_last_app_id=0
with open("config/deploy.json", "r") as f:
    default_last_app_id=loads(f.read())["app_id"]

app_id=int(argv[1]) if len(argv) > 1 else default_last_app_id

def main() :
    # initialize an algodClient
    algod_client = get_client()

    # get node suggested parameters
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 2000

    # define private keys
    creator_private_key = get_creator_private_key()

    # creator address
    sender = account.address_from_private_key(creator_private_key)

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, app_id)

    # sign transaction
    signed_txn = txn.sign(creator_private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    algod_client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(algod_client, tx_id, 6)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))
    except Exception as err:
        print(err)
        return

main()
