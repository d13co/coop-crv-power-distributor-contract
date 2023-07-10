import { readFileSync } from 'fs';

export async function lookup({ query, attempts = 1, callback, old_err, nn, limit }) {
  if (nn)
    query = query.nextToken(nn);
  let res;
  const start = Date.now();
  try {
    res = await query.do();
  } catch(e) {
    const message = e.response?.body?.message ?? e.response?.body ?? e.message;
    console.error(message);
    const sleepfor = Math.pow(attempts, 2) * 2000;
    console.error('sleeping for', sleepfor/1000);
    await sleep(sleepfor);
    if (attempts > 4 && e.message == old_err) {
      console.error('too many errors, quiting');
      return;
    }
    return lookup({ query, attempts: attempts+1, old_err: e.message, nn, callback, limit });
  }
  const elapsed = Math.floor((Date.now() - start) / 1000);
  if (callback)
    callback(res.balances);
  let round1, round2;
  console.error(res['next-token'], res.balances?.length, round1, round2, `${elapsed}s.`);
  res.balances = res.balances ?? [];
  if (res['next-token'] && (!limit || res.balances.length < limit)) {
    nn = res['next-token'];
    await sleep(1500);
    const next = await lookup({ query, attempts: 1, callback, nn });
    return [...res.balances, ...next];
  }
  return res.balances;
}

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const parseJSONFile = (filename) => {
  return JSON.parse(readFileSync(filename));
}

export const die = (...args) => {
  console.error(...args);
  process.exit(1);
}
