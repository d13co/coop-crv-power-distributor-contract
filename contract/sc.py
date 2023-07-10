from pyteal import *
from config import AID, UNCIRCULATING, UNCLAIMED, OPERATOR

bytes_empty = Bytes("")
bytes_unclaimed = Bytes("UNCLAIMED")
bytes_circulating = Bytes("CIRCULATING")
bytes_can_allocate = Bytes("CAN_ALLOCATE")
bytes_numbers=Bytes("0123456789")
bytes_abi_user_freeze=Bytes("base64", "80PpvA==")

len_min_allocate_note_length_required=Int(160)

str_crvdao_note_prefix='crvdao/v1:'
bytes_crvdao_note_prefix=Bytes(str_crvdao_note_prefix)
len_bytes_crvdao_note_prefix=Int(len(str_crvdao_note_prefix))

str_allocate_note_prefix='crvdao/v1:{"type":"allocate",'
bytes_allocate_note_prefix=Bytes(str_allocate_note_prefix)
len_bytes_allocate_note_prefix=Int(len(str_allocate_note_prefix))

bytes_d_tx_id=Bytes("d_tx_id")

bytes_allocate_generic_note=Bytes("CRV DAO voting power allocation for your donation")
bytes_allocate_specific_note=Bytes("CRV DAO voting power allocation for your donation with txn ID ")

err_unauthorized = "ERR UNAUTHORIZED"
err_not_opted_in_to_asset = "ERR NOT OPTED IN TO ASSET"
err_no_asset_balance = "ERR NO ASSET BALANCE"
err_cannot_allocate = "ERR ALLOCATIONS LOCKED"
err_expected_group_of_3 = "ERR EXPECTED GROUP OF 3"
err_expected_same_caller = "ERR EXPECTED SAME CALLER IN GROUP"
err_expected_unfreeze_first = "ERR EXPECTED UNFREEZE AS 1 OF 3"
err_expected_axfer_as_second = "ERR EXPECTED ASSET TRANSFER AS 2 OF 3"
err_expected_freeze_as_third = "ERR EXPECTED FREEZE AS 3 OF 3"
err_invalid_destination = "ERR INVALID DESTINATION"
err_receiver_has_zero_balance = "ERR RECEIVER MUST HAVE NON-ZERO BALANCE"

# lifted from pyteal-utils
@Subroutine(TealType.bytes)
def int_to_ascii(arg):
    """int_to_ascii converts an integer to the ascii byte that represents it"""
    return Extract(bytes_numbers, arg, Int(1))

@Subroutine(TealType.bytes)
def itoa(i):
    """itoa converts an integer to the ascii byte string it represents"""
    return If(
        i == Int(0),
        Bytes("0"),
        Concat(
            If(i / Int(10) > Int(0), itoa(i / Int(10)), Bytes("")),
            int_to_ascii(i % Int(10)),
        ),
    )

def custom_assert(cond, str):
    """assert that fails with an error string attached"""
    return If(Not(cond)).Then(Assert(Bytes('') == Bytes(str)))

def fail_if(cond, str):
    """assert that fails with an error string attached"""
    return If(cond).Then(Assert(Bytes('') == Bytes(str)))

def fail(str):
    """fail intentionally with readable error string"""
    return Assert(bytes_empty == Bytes(str))

def app_global_decr(key, val):
    """Decrement uint global at $key by $val"""
    return App.globalPut(key, App.globalGet(key) - val)

def app_global_incr(key, val):
    """Increment uint global at $key by $val"""
    return App.globalPut(key, App.globalGet(key) + val)

# create app, init storages
@Subroutine(TealType.none)
def create_app():
    """Initialize global storage"""
    return Seq(
        App.globalPut(bytes_unclaimed, Int(0)),
        App.globalPut(bytes_circulating, Int(0)),
        App.globalPut(bytes_can_allocate, Int(1)),
    )

@Subroutine(TealType.none)
def admin_only():
    """fails if the caller is not the contract creator/admin"""
    return If(Gtxn[0].sender() != Global.creator_address()).Then(fail(err_unauthorized))

def admin_or_operator_only():
    """fails if the caller is not the contract creator/admin or the designated operator"""
    return fail_if(
        And(Gtxn[0].sender() != Global.creator_address(), Gtxn[0].sender() != OPERATOR),
        err_unauthorized
    )

def is_reserve(addr):
    return Or(addr == UNCIRCULATING, addr == UNCLAIMED)

def can_allocate():
    """fails if global storage can_allocate is not zero"""
    return fail_if(App.globalGet(bytes_can_allocate) == Int(0), err_cannot_allocate)

# Main router class
router = Router(
    # Name of the contract
    "CRV Power Distributor",
    # What to do for each on-complete type when no arguments are passed (bare call)
    BareCallActions(
        no_op=OnCompleteAction.create_only(create_app),
        # Always let creator update/delete
        update_application=OnCompleteAction.call_only(admin_only),
        delete_application=OnCompleteAction.call_only(admin_only),
    ),
    clear_state=Approve() # attempt to send NFTs before clearing state (won't fail)
)

# admin method to change global state (8x)
@router.method
def update_state_int(key: abi.DynamicBytes, val: abi.Uint64):
    return Seq(
        admin_or_operator_only(),
        App.globalPut(key.get(), val.get()),
    )

# admin method to change global state (8x)
@router.method
def delete_state_int(key: abi.DynamicBytes):
    return Seq(
        admin_or_operator_only(),
        App.globalDel(key.get()),
    )

@router.method
def unrekey(addr: abi.Address):
    """[admin] undo rekeying of escrowed address back to itself"""
    return Seq(
        # admin only
        admin_only(),
        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: addr.get(),
            TxnField.receiver: addr.get(),
            TxnField.amount: Int(0),
            TxnField.rekey_to: addr.get(),
            TxnField.fee: Int(0),
        })
    )

def _unfreeze(acct, frozen=Int(0)):
    """[mixed] common method to unfreeze (default) or freeze an account"""
    return InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.AssetFreeze,
            TxnField.freeze_asset: AID,
            TxnField.sender: UNCIRCULATING,
            TxnField.freeze_asset_account: acct,
            TxnField.freeze_asset_frozen: frozen,
            TxnField.fee: Int(0),
        })

def _freeze(acct):
    """[mixed] common method to freeze an account"""
    return _unfreeze(acct, Int(1))

@router.method
def unfreeze(addr: abi.Address):
    """[admin] method to unfreeze an account"""
    return Seq(
        # admin only
        admin_only(),
        _unfreeze(addr.get())
    )

@router.method
def freeze(addr: abi.Address):
    """[admin] method to freeze an account"""
    return Seq(
        # admin only
        admin_only(),
        _freeze(addr.get()),
    )

def send_vp(receiver, amount, sender, note=bytes_empty):
    """[admin|op] send token from sender to receiver"""
    return Seq(
        _unfreeze(receiver),
        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: AID,
            TxnField.sender: sender,
            TxnField.asset_receiver: receiver,
            TxnField.asset_amount: amount,
            TxnField.fee: Int(0),
            TxnField.note: note,
        }),
        _freeze(receiver),
    )

@router.method
def claim_vp():
    """[user] claim voting power tokens"""
    amount = ScratchVar(TealType.uint64)
    return Seq(
        length := App.box_length(Txn.sender()),
        If(Not(length.hasValue())).Then(Seq(
            fail("NO VOTING POWER TO CLAIM"),
        )),
        amount.store(Btoi(
            App.box_extract(Txn.sender(), Int(0), Int(8)),
        )),
        send_vp(Txn.sender(), amount.load(), UNCLAIMED),
        Pop(App.box_delete(Txn.sender())),
        app_global_decr(bytes_unclaimed, amount.load()),
    )

# app call note should have a structure like this:
# crvdao/v1:{"type":"allocate","rcv":"7X4O5K6JBDWLSXYGGAG6LSTXNGKWXVO3PP4W5YVOSJMOQLGJJ5ZJFF65DA","d_tx_id":"DED7CGC2HICRMRNGTVUCYH5SZO55XRAGPFQS7FGFVRFBJQCW3LJQ","d_ts":1687387165,"d_aid":796425061,"d_amt":5000000000,"d_unit_usd":0.02950552362,"amt":147527618}

Subroutine(TealType.bytes)
def extract_note():
    """Extract reference txn id (d_tx_id) from app call note.
    validates the note prefix before attempting to parse JSON (incl. type: allocate
    Will fail if the prefix is set but either: 1/ Invalid JSON, or 2/ no d_tx_id field."""
    return Cond(
        [Len(Txn.note()) < len_min_allocate_note_length_required, bytes_allocate_generic_note],
        [Extract(Txn.note(), Int(0), len_bytes_allocate_note_prefix) != bytes_allocate_note_prefix, bytes_allocate_generic_note],
        [Int(1), Concat(
            bytes_allocate_specific_note,
            # this is fairly expensive opcode-wise but should still be under budget
            # ~100 opcode for a 250 byte json string
            JsonRef.as_string(
                # cut out the crvdao/v1: prefix, parse the rest
                Substring(Txn.note(), len_bytes_crvdao_note_prefix, Len(Txn.note())),
                # looking for .d_tx_id field
                bytes_d_tx_id,
            ),
        )],
    )

@router.method
def allocate_vp(amount: abi.Uint64, addr: abi.Address):
    """[admin|op] allocate voting power. sends if account opted in, otherwise allocates a box for later claim"""
    prev_amt = ScratchVar(TealType.uint64)
    note = ScratchVar(TealType.bytes)
    return Seq(
        # admin or operator access only
        admin_or_operator_only(),
        # allocating new power will be disabled during voting sessions
        can_allocate(),
        # allocating to one of the reserves is disallowed
        fail_if(is_reserve(addr.get()), err_invalid_destination),
        balance := AssetHolding.balance(addr.get(), AID),
        # If opted in, send directly
        If(balance.hasValue()).Then(Seq(
            send_vp(addr.get(), amount.get(), UNCIRCULATING, extract_note()),
        )).Else(Seq( # else allocate in box for later claim
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: AID,
                TxnField.sender: UNCIRCULATING,
                TxnField.asset_receiver: UNCLAIMED,
                TxnField.asset_amount: amount.get(),
                TxnField.fee: Int(0),
            }),
            length := App.box_length(addr.get()),
            If(Not(length.hasValue())).Then(Seq(
                Pop(App.box_create(addr.get(), Int(8))),
                prev_amt.store(Int(0)),
            )).Else(Seq(
                prev_amt.store(Btoi(
                    App.box_extract(addr.get(), Int(0), Int(8)),
                )),
            )),
            App.box_put(addr.get(), Itob(prev_amt.load() + amount.get())),
            app_global_incr(bytes_unclaimed, amount.get()),
        )),
        app_global_incr(bytes_circulating, amount.get()),
    )

@Subroutine(TealType.none)
def _dilute_unclaimed(permille, addr):
    """[admin|op] dilute unclaimed voting power, move back funds to non-circulating wallet, decrease global storage"""
    initial_amount = ScratchVar(TealType.uint64)
    amount = ScratchVar(TealType.uint64)
    return Seq(
        length := App.box_length(addr),
        # check box exists (user has voting power)
        If(Not(length.hasValue())).Then(Seq(
            fail("NO VOTING POWER TO DILUTE"),
        )),
        # initial amount of user
        initial_amount.store(Btoi(
            App.box_extract(addr, Int(0), Int(8)),
        )),
        # amount to subtract
        amount.store(
            permille * initial_amount.load() / Int(1000),
        ),
        # if there is anything left to subtract
        If (amount.load() > Int(0)).Then(Seq(
            # transfer funds from UNCLAIMED wallet back to UNCIRCULATING wallet
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: AID,
                TxnField.sender: UNCLAIMED,
                TxnField.asset_receiver: UNCIRCULATING,
                TxnField.asset_amount: amount.load(),
                TxnField.fee: Int(0),
            }),
            app_global_decr(bytes_circulating, amount.load()),
            app_global_decr(bytes_unclaimed, amount.load()),
            # final amount of user after dillution
            amount.store(initial_amount.load() - amount.load()),
            # if there is a final amount remaining, save it, otherwise delete
            If(amount.load() > Int(0)).Then(
                App.box_put(addr, Itob(amount.load()))
            ).Else(
                Pop(App.box_delete(addr)),
            ),
        ))
    )

@router.method
def dilute_unclaimed(permille: abi.Uint64, addr1: abi.Address, addr2: abi.Address, addr3: abi.Address, addr4: abi.Address):
    """[admin|op] Dilute unclaimed voting power of up to 4 accounts"""
    return Seq(
        # admin or operator access only
        admin_or_operator_only(),
        If(addr1.get() != Global.zero_address()).Then(
            _dilute_unclaimed(permille.get(), addr1.get())
        ),
        If(addr2.get() != Global.zero_address()).Then(
            _dilute_unclaimed(permille.get(), addr2.get())
        ),
        If(addr3.get() != Global.zero_address()).Then(
            _dilute_unclaimed(permille.get(), addr3.get())
        ),
        If(addr4.get() != Global.zero_address()).Then(
            _dilute_unclaimed(permille.get(), addr4.get())
        ),
    )

@Subroutine(TealType.none)
def _dilute_claimed(permille, addr, note):
    """[admin|op] dilute claimed voting power via clawback, move back funds to non-circulating wallet, decrease global storage"""
    initial_amount = ScratchVar(TealType.uint64)
    amount = ScratchVar(TealType.uint64)
    return Seq(
        # get initial user balance
        balance := AssetHolding.balance(
            addr,
            AID,
        ),
        # fail if the receiver is not opted in
        custom_assert(balance.hasValue(), err_not_opted_in_to_asset),
        # fail if the receiver has zero balance
        fail_if(balance.value() == Int(0), err_no_asset_balance),
        # initial amount of user
        initial_amount.store(balance.value()),
        # amount to subtract
        amount.store(
            permille * initial_amount.load() / Int(1000),
        ),
        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: AID,
            TxnField.sender: UNCIRCULATING,
            TxnField.asset_sender: addr,
            TxnField.asset_receiver: UNCIRCULATING,
            TxnField.asset_amount: amount.load(),
            TxnField.fee: Int(0),
        }),
        app_global_decr(bytes_circulating, amount.load()),
    )

@router.method
def dilute_claimed(permille: abi.Uint64, note: abi.DynamicBytes):
    """[admin|op] Dilute all foreign accounts by $permille %%"""
    i = ScratchVar(TealType.uint64)
    return Seq(
        # admin or operator access only
        admin_or_operator_only(),
        Log(itoa(Txn.accounts.length())),
        # Txn.accounts[0] is the caller (!) - ignore it & start at 1
        For(i.store(Int(1)), i.load() <= Txn.accounts.length(),  i.store(i.load() + Int(1))).Do(Seq(
            # ignore reserve accounts
            If(Not(is_reserve( Txn.accounts[i.load()]))).Then(
              _dilute_claimed(permille.get(), Txn.accounts[i.load()], note.get())
            )
        ))
    )

# The following facilitates donations to other non-zero holders or burning (back to uncirculating/manager acct)
# txn structure is:
# - user_unfreeze app call
# - send back to [addr with nonzero balance]
# - user_freeze app call

@router.method
def user_unfreeze():
    """[user] method to unfreeze. must be 1/3 and:
    2/3: Axfer to an account with a nonzero balance (and the unclaimed account)
    3/3: freeze of same account"""
    return Seq(
        # expect group of 3
        custom_assert(Global.group_size() == Int(3), err_expected_group_of_3),
        # expect sender is same in the group
        custom_assert(Gtxn[0].sender() == Gtxn[1].sender(), err_expected_same_caller),
        custom_assert(Gtxn[2].sender() == Gtxn[1].sender(), err_expected_same_caller),
        # expect this (unfreeze) is the first in the group
        custom_assert(Txn.group_index() == Int(0), err_expected_unfreeze_first),
        # expect second txn in group is an axter
        custom_assert(Gtxn[1].type_enum() == TxnType.AssetTransfer, err_expected_axfer_as_second),
        # ...AND the receiver is not UNCLAIMED addr
        custom_assert(Gtxn[1].asset_receiver() != UNCLAIMED, err_invalid_destination),
        # ...AND the receiver has a nonzero balance already
        balance := AssetHolding.balance(Gtxn[1].asset_receiver(), AID),
        fail_if(balance.value() == Int(0), err_receiver_has_zero_balance),
        # expect final/third txn is a freeze
        custom_assert(Gtxn[2].type_enum() == TxnType.ApplicationCall, err_expected_freeze_as_third),
        # mathcing first app arg - hardcoded to user_freeze abi encoding
        custom_assert(Gtxn[2].application_args[0] == bytes_abi_user_freeze, err_expected_freeze_as_third),
        # all good: we can unfreeze both sender and receiver
        _unfreeze(Txn.sender()),
        _unfreeze(Gtxn[1].asset_receiver()),
        # update storage int value if burning
        If(Gtxn[1].asset_receiver() == UNCIRCULATING).Then(app_global_decr(bytes_circulating, Gtxn[1].asset_amount())),
    )

@router.method
def user_freeze():
    """[user] pair of user_unfreeze, called as 3rd in group to freeze both accounts"""
    return Seq(
        _freeze(Txn.sender()),
        # user_unfreeze/freeze is also used to burn tokens (back to UNCIRCULATING)
        # if we are burning then do NOT freeze receiver
        # otherwise freeze them
        If(Gtxn[1].asset_receiver() != UNCIRCULATING).Then(
            _freeze(Gtxn[1].asset_receiver())
        )
    )

def get_contracts():
    return router.compile_program(version=8)
