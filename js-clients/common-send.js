import algosdk from 'algosdk';
import { APP_ID, AID, UNCIRCULATING, contract } from './common.js';

const unfreezeMethod = contract.methods.find(({name}) => name === 'user_unfreeze');
const freezeMethod = contract.methods.find(({name}) => name === 'user_freeze');

export async function send(sender, receiver, amount, algod) {
  const { addr, sk } = sender;
  const params = await algod.getTransactionParams().do();

  try {
    const suggestedParams = {
      ...params,
      flatFee: true,
      fee: 3000, // 1 outer app, 2 unfreeze
    };

    const txns = [];

    txns.push(algosdk.makeApplicationNoOpTxnFromObject({
      from: addr,
      appIndex: APP_ID,
      suggestedParams,
      appArgs: [
        unfreezeMethod.getSelector(),
      ],
      foreignAssets: [AID],
      accounts: [UNCIRCULATING, addr, receiver],
    }));

    txns.push(algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
      from: addr,
      to: receiver,
      amount,
      assetIndex: AID,
      suggestedParams: { ...params },
    }));
      
    txns.push(algosdk.makeApplicationNoOpTxnFromObject({
      from: addr,
      appIndex: APP_ID,
      suggestedParams,
      appArgs: [
        freezeMethod.getSelector(),
      ],
      foreignAssets: [AID],
      accounts: [UNCIRCULATING, receiver],
    }));

    algosdk.assignGroupID(txns);
    const signed = txns.map(txn => algosdk.signTransaction(txn, sk).blob);
    await algod.sendRawTransaction(signed).do();
    const txID = txns[0].txID();
    await algosdk.waitForConfirmation(algod, txID, 10);
    console.log("https://app.dappflow.org/explorer/transaction/" + txID);
  } catch(e) {
    console.error(e);
  }
}
