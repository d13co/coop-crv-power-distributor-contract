import algosdk from 'algosdk';
import { die, parseJSONFile } from './util.js';
import { APP_ID, AID, RESERVES, contract, creator, algod } from './common.js';
import { getHolders } from './indexer.js';
import chunk from 'lodash/chunk.js';

const senderFile = process.argv[2];

const { addr, key } = parseJSONFile(senderFile);

const { sk } = algosdk.mnemonicToSecretKey(key);

const params = await algod.getTransactionParams().do();

const method = 'claim_vp';
const methodConf = contract.methods.find(({name}) => name === method);

async function isOptedIn(addr, aid) {
  const info = await algod.accountInformation(addr).do();
  return info?.assets?.some(({"asset-id": _aid}) => _aid === aid);
}

async function claim() {
  try {
    const optedIn = await isOptedIn(addr, AID);

    const txns = [];

    if (!optedIn) {
      console.error('Not opted in, adding optin to', AID);
      txns.push(algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        from: addr,
        to: addr,
        amount: 0,
        assetIndex: AID,
        suggestedParams: { ...params },
      }));
    }

    const suggestedParams = {
      ...params,
      flatFee: true,
      fee: 4000, // 1 outer app, 1 unfreeze, 1 atxn, 1 freeze
    };

    debugger;
    const args = {
      from: addr,
      appIndex: APP_ID,
      suggestedParams,
      appArgs: [
        methodConf.getSelector(),
      ],
      foreignAssets: [AID],
      accounts: [...RESERVES, addr],
      boxes: [{appIndex: APP_ID, name: algosdk.decodeAddress(addr).publicKey}],
    };

    const txn = algosdk.makeApplicationNoOpTxnFromObject(args);
    txns.push(txn);

    algosdk.assignGroupID(txns);
    const signed = txns.map(txn => algosdk.signTransaction(txn, sk).blob);
    await algod.sendRawTransaction(signed).do();
    console.log("https://app.dappflow.org/explorer/transaction/" + txn.txID());
  } catch(e) {
    console.error(e);
  }
}

claim();
