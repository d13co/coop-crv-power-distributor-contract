import algosdk from 'algosdk';
import { die, parseJSONFile } from './util.js';
import { APP_ID, AID, UNCIRCULATING, contract, creator, algod } from './common.js';
import { send } from './common-send.js';

const senderFile = process.argv[2];

const amount = Number(process.argv[3]);

if (!process.argv[3]) {
  die('Expected: <sender file> <amount>');
}

const { addr, key } = parseJSONFile(senderFile);

const sender = algosdk.mnemonicToSecretKey(key);

await send(sender, UNCIRCULATING, amount, algod);
