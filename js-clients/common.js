import algosdk from 'algosdk';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import { parseJSONFile } from './util.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const configPath = join(__dirname, '../setup/config');

export const AID = Number(readFileSync(join(configPath, 'aid.txt')).toString());

export const UNCIRCULATING = parseJSONFile(join(configPath, 'accounts/coophair.keys.json')).addr;
export const UNCLAIMED = parseJSONFile(join(configPath, 'accounts/coophold.keys.json')).addr;

export const RESERVES = [UNCIRCULATING, UNCLAIMED];

const deploy = parseJSONFile(join(configPath, 'deploy.json'));

export const APP_ID = deploy.app_id;
export const APP_ADDR = deploy.app_addr;

export const contract = new algosdk.ABIContract(parseJSONFile(join(configPath, '../../contract/contract.json')));

export const creator = parseJSONFile(join(configPath, 'accounts/creator.keys.json'));

const { uri, port, token } = parseJSONFile(join(__dirname, '../common/client.json'));

export const algod = new algosdk.Algodv2(token, uri, port);
