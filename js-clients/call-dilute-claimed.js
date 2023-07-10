import algosdk from 'algosdk';
import { die } from './util.js';
import { APP_ID, AID, RESERVES, UNCIRCULATING, contract, creator, algod } from './common.js';
import { getHolders } from './indexer.js';
import chunk from 'lodash/chunk.js';

const perm = process.argv[2] ? Number(process.argv[2]) : 0;

if (!perm) {
  die(`Expected non-zero per-mille dillution, e.g. "10" for 1%, "1000" = 100%`);
}

let holders = await getHolders(AID);

holders = Object.keys(holders)
  .filter(addr => !RESERVES.includes(addr));

const { addr, sk } = algosdk.mnemonicToSecretKey(creator.key);

const params = await algod.getTransactionParams().do();

const method = 'dilute_claimed';
const methodConf = contract.methods.find(({name}) => name === method);

console.log('holders.length', holders.length);

async function dilute48(holders) {
  try {
    const gtxns = chunk(holders, 3).map(holders => {
      const suggestedParams = {
        ...params,
        flatFee: true,
        fee: 1000 + (1000 * holders.length),
      };
      // could use atomic transaction composer but I'm in a bit of a rush
      // and had this code lying around already. welp
      const args = {
        from: addr,
        appIndex: APP_ID,
        suggestedParams,
        appArgs: [
          methodConf.getSelector(),
          algosdk.encodeUint64(perm),
          new Uint8Array(Buffer.from(process.argv[3])),
        ],
        foreignAssets: [AID],
        accounts: [UNCIRCULATING, ...holders],
      };
      console.log(args);
      return algosdk.makeApplicationNoOpTxnFromObject(args);
    });
    algosdk.assignGroupID(gtxns);
    const signed = gtxns.map(txn => algosdk.signTransaction(txn, sk).blob);
    await algod.sendRawTransaction(signed).do();
    console.log("https://app.dappflow.org/explorer/transaction/" + gtxns[0].txID());
  } catch(e) {
    console.error(e);
  }
}

const chunks = chunk(holders, 48);

await Promise.all(chunks.map(chunk => dilute48(chunk)));

