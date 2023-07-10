# CRV Power Distributor

## Overview

This contract manages an asset with default-freeze and clawback. The intended use case is managing the Coop CRV donor voting power token:

CRV Donor voting power was decided to be proportional to donation USD value (fixed at time of donation.)

As rewards are distributed from the CRV, voting power will dilute.

Donation values will be calculated off-chain and added by an admin with allocate_vp. If the receiver is opted in to the token, the tokens will be transfered immediately. Otherwise, the voting power amount will be added to a box per user and will be claimable as ASA tokens via claim_vp.

The contract will have 2 escrow addresses - the token manager (coophair) which will hold non-circulating supply, and a "claimable" escrow address that will hold the tokens available to be claimed by donors (coophold).

Dilution of distributed tokens happens via clawback in the dilute_claimed method. Unclaimed tokens will also dilute via the dilute_unclaimed method.

The user-callable methods are claim_vp (to claim the tokens after opting in), and a set of user-facing unfreeze/freeze functions that facilitate burning voting power, or donating it to another holder. The intent of for user addresses to be frozen at all times, and these functions to facilitate moving tokens between existing holders, but not smart contracts/atomic swaps/other monetization methods.

## Global Storage
- UNCLAIMED (coophold balance)
- CIRCULATING uint64 (unclaimed+circulating)

These are meant as a sanity check but I am not sure that they are actually necessary. The token is default-frozen but holders can still close out balance to the creator account, which would throw the storage values off. I will leave them in for now but can be removed moving forward.

- CAN_ALLOCATE uint64 : 0 | 1

This locks the allocation function, meant to be used while voting on something is in progress. New voting power allocations will happen after voting has concluded.

## Box Storage
[address]: [claimable amt] (8 bytes)

## App accts

- "UNCIRCULATING" - COOPHAIR.. - manager+freeze+clawback address of token. Holds undistributed/non-circulating supply
- "UNCLAIMED" - ??? - holds allocated but unclaimed 

These are meant to be rekeyed to the contract's app address. The contract expects both of them to be unfrozed. See end of setup/setup.sh

## Methods - user - implemented

### claim_vp()

Check box $addr for val

Send $val VP tokens from coophold to $addr

delete box $addr

### user_freeze/user_unfreeze

These facilitate donations to other (non-zero) holders or burning (back to uncirculating/manager acct)

Group txn structure is:

- user_unfreeze app call
- send back to [addr with nonzero balance]
- user_freeze app call

## Methods - admin or operator - implemented

### allocate_vp(amt, addr)

If addr not opted in: store in box

- Move hair->hold $amt

- Create or update box $addr val += $amt

Else if addr opted in: send $amt to addr

### dilute_unclaimed(perm, addr1, ...)

Dilute box storage claimable amts by per-mille %% $perm

### dilute_claimed(num, note)

Dilute distributed voting power by clawback

Iterate foreign accts and clawback num%% of their balance

### update_state_int / delete_state_int

update or delete a global storage value

### freeze / unfreeze: explicitly freeze or unfreeze an address

### unrekey(addr)

rekey address to itself

## Setup & usage

requirements: pip jq (and node for js-clients)

custom requirement: a `sandbox` command in your PATH. Template in setup/sandbox.template

```
# init setup
cd setup
./setup.sh
# sets up 131 accounts (creator + 2 escrow addrs + 128 players)
# sets up token
# opts in all accounts to token
# deploys contract
```

Example usage:

```
# allocate some voting power to all 128 accounts
cd ../clients
bash mass_allocate.sh

# claim it from 64 accounts
bash mass_claim.sh

# dilute 50% of unclaimed voting power
python3 call_dilute_unclaimed.py "" 500

# dilute 50% of claimed voting power
cd ../js-clients
npm i
node call-dilute-claimed.js 500 "note"
```

The first arg to the python client scripts is app ID, which defaults to "last deployed" if `""` is provided.

You can use `setup/keep-redeploying.sh` for a CI style redeployer.

## Future/TODO

Drafts from here on

- recalc_circulating?
(Used if VP tokens are closed out?)
Check if storages line up with balances for hair/hold
Update circulating If not
will likely remove the global storage values anyway, so prob no need for this.

- claim_vp with extra Txn.accounts: for admin/operator to drop to other users when they opt in


## Box storage MBR

we have 93 donors currently, but let's accomodate 400 

(2500 per box) + (400 * (box size + key size))

keysize=32
boxsize=8
boxes=400

400 * (2500 + (400 * (8 + 32))) = 7.4 ALGO

## License

This software is released under GPLv3. Details in the [LICENSE](LICENSE) file.

Explanation of the GPLv3 can be found [here](https://www.gnu.org/licenses/quick-guide-gplv3.html).
