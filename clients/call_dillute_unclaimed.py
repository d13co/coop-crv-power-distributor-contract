from sys import argv
from common import *
from pyteal import Addr

amount=int(argv[2])
addrs=argv[3:]
addr_empty='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ'
b_addr_empty = encoding.decode_address(addr_empty)

private_key = get_creator_private_key()

if len(addrs) == 0:
    boxen = get_app_boxes(client, app_id)

    for b in boxen:
        print(b, get_user_boxes(client, app_id, b)[0])

    print("Dilute all these by ", amount/10, "%")
    input()
    addrs = boxen

def pad(arr, num, pad_elem):
    while len(arr) < num:
        arr.append(pad_elem)
    return arr

# call application
def call_app(addrs):
    # addrs max: 16 x 4 = 64

    # get sender address
    sender = account.address_from_private_key(private_key)
    print("Dilluting", amount/10, "% from unclaimed power of", addrs)

    # create a Signer object 
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()

    addrs4 = chunker(addrs, 4)

    for addrs4 in chunker(addrs, 4):

        sp.flat_fee = True
        sp.fee = 1000 + (1000 * len(addrs4))

        addrs4 = pad(addrs4, 4, addr_empty)
        b_addrs4 = list(map(lambda addr: encoding.decode_address(addr), addrs4))

        method_args = [amount] + b_addrs4
        boxes = list(map(lambda b_addr: (app_id, b_addr), b_addrs4))

        atc.add_method_call(
            app_id=app_id,
            method=contract.get_method_by_name("dilute_unclaimed"),
            sender=sender,
            sp=sp,
            signer=signer,
            method_args=method_args,
            accounts=[UNCLAIMED, UNCIRCULATING],
            foreign_apps=[],
            foreign_assets=[AID],
            boxes=boxes,
        )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))

chunks = chunker(addrs, 64)

for chunk in chunks:
    call_app(chunk)
