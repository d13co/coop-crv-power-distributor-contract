import os
from json import loads
from algosdk import mnemonic, account

accounts={}

for filename in os.listdir("../setup/config/accounts"):
    if filename[-5:] == ".json":
        key=filename[0:-10]
        with open("../setup/config/accounts/"+filename, "r") as f:
            accounts[key] = loads(f.read())

def get_private_key(name):
    return mnemonic.to_private_key(accounts[name]["key"])

def get_private_key_for_address(addr):
    for i in accounts:
        if accounts[i]['addr'] == addr:
            return mnemonic.to_private_key(accounts[i]['key'])
    raise ValueError("no key found")
##

def get_creator_private_key():
    return get_private_key('creator')

def get_operator_private_key():
    return get_private_key('operator')

def get_coophair_private_key():
    return get_private_key('coophair')

def get_player1_private_key():
    return get_private_key('player1')

def get_player2_private_key():
    return get_private_key('player2')
