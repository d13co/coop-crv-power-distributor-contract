import os
import json
from sys import argv, path
from algosdk import encoding
from base64 import b64decode

reldir=os.path.dirname(__file__)
if reldir != '':
    os.chdir(reldir)

from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic

with open("../setup/config/accounts/coophair.keys.json", "r") as f:
    config = json.loads(f.read())
    UNCIRCULATING=config["addr"]

with open("../setup/config/accounts/coophold.keys.json", "r") as f:
    config = json.loads(f.read())
    UNCLAIMED=config["addr"]

with open("../setup/config/aid.txt", "r") as f:
    AID=int(f.read())

path.insert(1, '../common')
os.chdir('../common')

from client import *
from accounts import get_creator_private_key, get_operator_private_key, get_player1_private_key, get_player2_private_key, get_private_key, accounts, get_private_key_for_address

path.insert(1, '../contract')
os.chdir('../contract')
from sc import get_contracts

path.insert(1, '../clients')
os.chdir('../clients')

default_last_app_id=0
with open("../setup/config/deploy.json", "r") as f:
    deploy_json=loads(f.read())
    default_last_app_id=deploy_json["app_id"]
    app_addr=deploy_json["app_addr"]

app_id=int(argv[1]) if len(argv) > 1 and argv[1] != "" else default_last_app_id

_, _, contract = get_contracts()

client = get_client()

def chunker(iter, size):
    chunks = [];
    if size < 1:
        raise ValueError('Chunk size must be greater than 0.')
    for i in range(0, len(iter), size):
        chunks.append(iter[i:(i+size)])
    return chunks


# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            if formatted_key == 'voted':
                formatted_value = base64.b64decode(value['bytes']).decode('utf-8')
            else:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted

# helper function to read app global state
def read_global_state(client, app_id):
    app = client.application_info(app_id)
    global_state = app['params']['global-state'] if "global-state" in app['params'] else []
    return format_state(global_state)

def get_asset_balances(client, addr):
    assets={}
    asset_state=client.account_info(app_addr)
    for elem in asset_state["assets"]:
        key=elem["asset-id"]
        value=elem["amount"]
        assets[key]=value
    return assets

def get_user_boxes(client, app_id, address):
    box_name_bytes=encoding.decode_address(address)
    chunk_size = 8
    out_data=[]
    box_data=b64decode(client.application_box_by_name(app_id, box_name_bytes).get('value'))
    for aid_bytes in chunker(box_data, chunk_size):
        aid_int = int.from_bytes(aid_bytes, byteorder='big', signed=False)
        out_data.append(aid_int)
    return out_data

def get_app_boxes(client, app_id, decode_address=True):
    app_boxes=[]
    data=client.application_boxes(app_id).get('boxes')
    for elem in data:
        name = base64.b64decode(elem['name'])
        if decode_address and len(name) == 32:
            app_boxes.append(encoding.encode_address(name))
        else:
            app_boxes.append(name.decode('utf-8'))
    return app_boxes

def pad(arr, num, pad_elem):
    while len(arr) < num:
        arr.append(pad_elem)
    return arr
