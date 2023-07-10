from os import chdir
from sys import argv, path
from algosdk import transaction

path.insert(1, '../common')
chdir('../common')

from client import *
from accounts import get_private_key_for_address

rekey=argv[1]
to=argv[2]

print("algod client", uri)
print("rekey", rekey, "to", to)
private_key=get_private_key_for_address(rekey)

if len(argv) < 4 or argv[3] != "yes":
    print("Press any to proceed")
    input()

client=get_client()

# define sender as creator
sender = account.address_from_private_key(private_key)

# get node suggested parameters
params = client.suggested_params()
params.flat_fee = True
params.fee = 1000

# create unsigned transaction
txn = transaction.PaymentTxn(sender, params, sender, 0, rekey_to=to)

print(txn)

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
