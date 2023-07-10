from sys import argv
from common import *

addr=argv[2]

private_key = get_creator_private_key()

# call application
def call_app():
    # get sender address
    sender = account.address_from_private_key(private_key)
    print("Unrekeying", addr, "from app", app_id, "to sender", sender)

    # create a Signer object 
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    sp.flat_fee = True
    sp.fee = 2000

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("unrekey"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[encoding.decode_address(addr)],
        accounts=[addr],
        foreign_apps=[]
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))

call_app()
