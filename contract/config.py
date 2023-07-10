import os
from pyteal import Addr, Int
from json import loads
from sys import argv

reldir=os.path.dirname(os.path.realpath(__file__))
os.chdir(reldir)
config=os.path.abspath("../setup/config")
os.chdir(config)

with open("./accounts/operator.keys.json", "r") as f:
    config = loads(f.read())
    OPERATOR=Addr(config["addr"])

with open("./accounts/coophair.keys.json", "r") as f:
    config = loads(f.read())
    UNCIRCULATING=Addr(config["addr"])

with open("./accounts/coophold.keys.json", "r") as f:
    config2 = loads(f.read())
    UNCLAIMED=Addr(config2["addr"])

with open("./aid.txt", "r") as f:
    AID=Int(int(f.read()))

os.chdir(reldir)

