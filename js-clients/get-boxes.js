import algosdk from 'algosdk';
import { die } from './util.js';
import { APP_ID, algod } from './common.js';

export async function getAllUnclaimed(appId = APP_ID) {
  const { boxes } = await algod.getApplicationBoxes(appId).do();

  const unclaimed = {};

  for(const { name } of boxes) {
    const box = await algod.getApplicationBoxByName(appId, name).do();
    const addr = algosdk.encodeAddress(name);
    unclaimed[addr] = algosdk.decodeUint64(box.value) / 1_000_000;
  }

  return unclaimed;
}

export async function getUserUnclaimed(addr, appId = APP_ID) {
  const { publicKey: name } = algosdk.decodeAddress(addr);
  try {
    const box = await algod.getApplicationBoxByName(appId, name).do();
    return algosdk.decodeUint64(box.value) / 1_000_000;
  } catch(e) {
    if (e.message.includes('box not found')) {
      return 0;
    } else {
      throw e;
    }
  }
}

console.log(await getUserUnclaimed('YLHXVDC5TKYPMF5GN6UV4LD3HL6N22KCZ7OEWNT345ZQPXBA77LZKY6VGU'));
