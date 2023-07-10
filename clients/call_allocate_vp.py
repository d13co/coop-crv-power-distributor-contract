from sys import argv
from common import *

amount=int(argv[2])
addr=argv[3]

private_key = get_operator_private_key()

# call application
def call_app():
    # get sender address
    sender = account.address_from_private_key(private_key)
    print("allocating", amount, "to", addr, "from operator", sender)

    # create a Signer object 
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    sp.flat_fee = True
    sp.fee = 4000 # could be 2000 if receiver not opted in. w/e ?

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()

    b_addr = encoding.decode_address(addr)

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("allocate_vp"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[amount, b_addr],
        accounts=[UNCLAIMED, UNCIRCULATING, addr],
        foreign_apps=[],
        foreign_assets=[AID],
        boxes=[
            (app_id, b_addr)
        ],
        note='crvdao/v1:{"type":"allocate","rcv":"7X4O5K6JBDWLSXYGGAG6LSTXNGKWXVO3PP4W5YVOSJMOQLGJJ5ZJFF65DA","d_tx_id":"DED7CGC2HICRMRNGTVUCYH5SZO55XRAGPFQS7FGFVRFBJQCW3LJQ","d_ts":1687387165,"d_aid":796425061,"d_amt":5000000000,"d_unit_usd":0.02950552362,"amt":147527618}'.encode()
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))

call_app()
