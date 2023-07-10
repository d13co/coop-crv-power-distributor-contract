from sys import argv
from common import *
from pyteal import Addr

amount=int(argv[2])
note=argv[3]
addrs=argv[4:]
addr_empty='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ'
b_addr_empty = encoding.decode_address(addr_empty)

private_key = get_creator_private_key()

# call application
def call_app(addrs):
    # addrs max: 16 x 4 = 64

    # get sender address
    sender = account.address_from_private_key(private_key)
    print("Dilluting", amount/10, "% from claimed power of", addrs)

    # create a Signer object 
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()

    addrs4 = chunker(addrs, 4)

    for addrs4 in chunker(addrs, 4):

        sp.flat_fee = True
        sp.fee = 1000 + (3000 * len(addrs4))

        accounts = [UNCIRCULATING] + addrs4
        print("fa", accounts)

        atc.add_method_call(
            app_id=app_id,
            method=contract.get_method_by_name("dilute_claimed"),
            sender=sender,
            sp=sp,
            signer=signer,
            method_args=[amount, encoding.encode_as_bytes("test")],
            accounts=accounts,
            foreign_apps=[],
            foreign_assets=[AID],
        )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("https://app.dappflow.org/explorer/transaction/"+results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))

chunks = chunker(addrs, 64)

for chunk in chunks:
    call_app(chunk)
