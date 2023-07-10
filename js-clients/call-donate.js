import algosdk from 'algosdk';
import { die, parseJSONFile } from './util.js';
import { APP_ID, AID, UNCIRCULATING, contract, creator, algod } from './common.js';
import { send } from './common-send.js';

const senderFile = process.argv[2];

const receiver = process.argv[3];

const amount = Number(process.argv[4]);

if (!process.argv[4]) {
  die('Expected: <sender file> <receiver address> <amount>');
}

const { addr, key } = parseJSONFile(senderFile);

const sender = algosdk.mnemonicToSecretKey(key);

await send(sender, receiver, amount, algod);
