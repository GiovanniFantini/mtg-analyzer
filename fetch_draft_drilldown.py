"""Fetch separate, auditable 17Lands contexts without overwriting prior snapshots."""
import concurrent.futures
import datetime
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
PAIRS = ['WU','UB','BR','RG','WG','WB','BG','UG','UR','WR']


def fetch(key, endpoint, params):
    url = 'https://www.17lands.com' + endpoint + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'MTG-Draft-Research/1.0'})
    with urllib.request.urlopen(req, timeout=40) as response:
        value = json.load(response)
    return key, {'url': url, 'params': params, 'value': value}


def main():
    requests = []
    for period in ['ALL_TIME', 'LAST_WEEK']:
        base = dict(expansion='FRA', event_type='PremierDraft', time_period=period)
        for pair in ['all'] + PAIRS:
            requests.append((period + ':' + pair, '/api/card_data', {**base, **({'colors':pair} if pair != 'all' else {})}))
        requests.append((period + ':colors', '/color_ratings/data', {**base, 'combine_splash':'false'}))
    for mode in ['TradDraft', 'QuickDraft']:
        requests.append((mode + ':all', '/api/card_data', dict(expansion='FRA', event_type=mode, time_period='ALL_TIME')))
        requests.append((mode + ':colors', '/color_ratings/data', dict(expansion='FRA', event_type=mode, time_period='ALL_TIME', combine_splash='false')))
    result = {'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'contexts':{}, 'errors':{}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        pending = {executor.submit(fetch, *args):args[0] for args in requests}
        for future in concurrent.futures.as_completed(pending):
            key = pending[future]
            try:
                key, record = future.result()
                result['contexts'][key] = record
            except Exception as error:
                result['errors'][key] = str(error)
    path = ROOT / 'draft-drilldown-20261016.json'
    if path.exists():
        raise FileExistsError('Snapshot already exists; retain it and choose a new snapshot name.')
    path.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'contexts':len(result['contexts']), 'errors':result['errors'], 'path':str(path)}))


if __name__ == '__main__':
    main()
