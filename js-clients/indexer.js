import algosdk from 'algosdk';
import { lookup } from './util.js';

// const token = "";
// const server = "https://mainnet-idx.algonode.cloud";
// const port = 443;

const token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const server = "http://localhost";
const port = 8980;

export const indexer = new algosdk.Indexer(token, server, port);

export function getRawHolders(aid) {
  const query = indexer.lookupAssetBalances(aid);
  return lookup({ query });
}

export async function getHolders(aid, opts = { includeZero: false }) {
  const data = await getRawHolders(aid);

  const output = {}
  for(const holder of data) {
    const { amount, address } = holder;
    if (amount || opts?.includeZero) {
      output[address] = amount;
    }
  }

  return output;
}

export async function getHolderDetails(aid, opts = { includeZero: false }) {
  const data = await getRawHolders(aid);

  const output = {}
  for(const holder of data) {
    const { amount, address, "is-frozen": frozen } = holder;
    if (amount || opts?.includeZero) {
      output[address] = { amount, frozen };
    }
  }

  return output;
}
