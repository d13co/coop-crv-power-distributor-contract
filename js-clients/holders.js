import { getHolderDetails } from './indexer.js';

console.log(await getHolderDetails(Number(process.argv[2])));
