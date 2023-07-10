from sys import argv
from common import *

key=argv[2]

private_key = get_operator_private_key()

# call application
def call_app():
    # get sender address
    sender = account.address_from_private_key(private_key)
    print("deleting global",key)

    # create a Signer object 
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    sp.flat_fee = True
    sp.fee = 1000

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("delete_state_int"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[key.encode()],
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))

call_app()
