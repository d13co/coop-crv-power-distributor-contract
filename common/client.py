from algosdk.v2client import algod
from algosdk import mnemonic, account
from json import loads

with open("client.json", "r") as f:
    config=loads(f.read())
    token=config["token"]
    uri=config["uri"]

def get_client():
    return algod.AlgodClient(token, uri)
