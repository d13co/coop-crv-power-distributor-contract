from sys import argv
from common import *

addr=argv[2]

private_key = get_private_key_for_address(addr)

# call application
def call_app():
    # get sender address
    sender = account.address_from_private_key(private_key)
    print("claiming for", addr)

    # create a Signer object 
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    sp.flat_fee = True
    sp.fee = 4000

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()

    b_addr = encoding.decode_address(addr)

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("claim_vp"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[],
        accounts=[UNCLAIMED, UNCIRCULATING, sender],
        foreign_apps=[],
        foreign_assets=[AID],
        boxes=[
            (app_id, b_addr)
        ],
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))

call_app()
