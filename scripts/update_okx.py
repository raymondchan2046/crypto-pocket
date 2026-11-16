#!/usr/bin/env python3
"""Collects hourly OKX statistics for BTC, ETH and SOL into one JSON file.

The app's web page cannot read these OKX endpoints itself (they send no CORS
headers), so a GitHub Action runs this every hour and publishes the file on
the repository's `data` branch, where the page reads it.

Usage: python3 scripts/update_okx.py PATH_TO_JSON
The file at PATH_TO_JSON is read if it exists and updated in place: new hours
are merged into the old ones and anything older than seven days is dropped.
OKX keeps only about a day of liquidation orders, so they are summed into the
file as they arrive; an hour that a missed run left incomplete is marked.
"""
import json, os, sys, time, datetime, urllib.request, urllib.error

API = 'https://www.okx.com/api/v5/'
COINS = ['BTC', 'ETH', 'SOL']
H = 3600_000
KEEP_HOURS = 168
KEEP_DAYS = 180
HK = datetime.timezone(datetime.timedelta(hours=8))


def get(path, tries=4):
    """GET an OKX endpoint and return its `data`, pausing between calls to stay inside OKX's rate limits."""
    for attempt in range(tries):
        time.sleep(0.45)
        try:
            req = urllib.request.Request(API + path, headers={'User-Agent': 'crypto-pocket-data/1.0', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.load(r)
            if body.get('code') == '0':
                return body.get('data') or []
            if body.get('code') == '50011' and attempt < tries - 1:      # too many requests
                time.sleep(2 * (attempt + 1)); continue
            raise RuntimeError(f"OKX {path.split('?')[0]}: {body.get('code')} {body.get('msg')}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt == tries - 1:
                raise RuntimeError(f"OKX {path.split('?')[0]}: {e}") from e
            time.sleep(2 * (attempt + 1))
    return []


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v == v and v not in (float('inf'), float('-inf')) else None


def rnd(v, places):
    return None if v is None else round(v, places)


def update_coin(coin, old, now_ms):
    rows = {r['t']: r for r in old.get('hourly', [])}
    row = lambda t: rows.setdefault(t, {'t': t})
    hour = lambda ms: ms // H * H
    price_places = 2 if coin == 'SOL' else 1

    # Price: OKX spot candles, stamped with the START of their hour. Two pages cover more than a week.
    after = ''
    for _ in range(2):
        page = get(f'market/history-candles?instId={coin}-USDT&bar=1H&limit=100' + (f'&after={after}' if after else ''))
        if not page:
            break
        for c in page:
            r = row(int(c[0]))
            r.update(o=rnd(num(c[1]), price_places), h=rnd(num(c[2]), price_places), l=rnd(num(c[3]), price_places), c=rnd(num(c[4]), price_places))
        after = page[-1][0]

    # OKX statistics are stamped with the END of their hour: the row at T describes T-1h..T,
    # so each is stored on the hour that starts at T-1h. OI and the long/short ratio are the values at T.
    for ts, oi, vol in get(f'rubik/stat/contracts/open-interest-volume?ccy={coin}&period=1H'):
        r = row(int(ts) - H); r['oi'] = rnd(num(oi), 0); r['vol'] = rnd(num(vol), 0)
    for ts, sell, buy in get(f'rubik/stat/taker-volume?ccy={coin}&instType=CONTRACTS&period=1H'):
        r = row(int(ts) - H); r['tk_sell'] = rnd(num(sell), 0); r['tk_buy'] = rnd(num(buy), 0)
    for ts, ratio in get(f'rubik/stat/contracts/long-short-account-ratio?ccy={coin}&period=1H'):
        row(int(ts) - H)['ls'] = rnd(num(ratio), 3)

    # Liquidations of the USDT-margined perpetual, in USD, summed per hour. Only orders newer than the
    # last run's cursor are added, so a re-run never counts an order twice.
    spec = [i for i in get(f'public/instruments?instType=SWAP&instFamily={coin}-USDT') if i.get('instId') == f'{coin}-USDT-SWAP']
    ct_val = num(spec[0]['ctVal']) if spec else None
    cursor = old.get('liq_cursor') or 0
    gaps = [g for g in old.get('liq_gaps', [])]
    liq_from = old.get('liq_from')
    fresh, oldest, reached, after, pages = [], None, False, '', 0
    while ct_val and pages < 300:
        page = get(f'public/liquidation-orders?instType=SWAP&uly={coin}-USDT&state=filled&limit=100' + (f'&after={after}' if after else ''))
        details = (page[0].get('details') if page else None) or []
        if not details:
            break
        pages += 1
        for d in details:
            ts = int(d['ts'])
            oldest = ts if oldest is None else min(oldest, ts)
            if ts <= cursor:
                reached = True
                continue
            usd = (num(d.get('sz')) or 0) * ct_val * (num(d.get('bkPx')) or 0)
            fresh.append((ts, 'long' if d.get('posSide') == 'long' or (d.get('posSide') not in ('long', 'short') and d.get('side') == 'sell') else 'short', usd))
        if reached:
            break
        after = details[-1]['ts']
    if fresh:
        for ts, side, usd in fresh:
            r = row(hour(ts))
            r['liq_long'] = r.get('liq_long') or 0
            r['liq_short'] = r.get('liq_short') or 0
            r['liq_' + side] = round(r['liq_' + side] + usd)
            r['liq_n'] = (r.get('liq_n') or 0) + 1
        new_cursor = max(ts for ts, _, _ in fresh)
    else:
        new_cursor = cursor
    if liq_from is None:
        # First run: OKX's oldest order starts the record; that first hour is only partly covered.
        start = oldest if oldest is not None else now_ms
        liq_from = hour(start) + H
    elif cursor and not reached and oldest is not None and oldest > cursor:
        # A run was missed for longer than OKX keeps orders: the hours in between are incomplete.
        gaps.append([hour(cursor), hour(oldest)])

    # Hours inside the record and outside any gap count liquidations, with zero where none happened.
    window_start = hour(now_ms) - (KEEP_HOURS - 1) * H
    gaps = [g for g in gaps if g[1] >= window_start]
    in_gap = lambda t: any(a <= t <= b for a, b in gaps)
    out = []
    for t in sorted(rows):
        if t < window_start or t > hour(now_ms):
            continue
        r = rows[t]
        if t >= liq_from and not in_gap(t):
            r.setdefault('liq_long', 0); r.setdefault('liq_short', 0); r.setdefault('liq_n', 0)
            r.pop('liq_gap', None)
        elif t >= liq_from - H:
            r['liq_gap'] = True
        out.append(r)

    # Daily open interest for the 180-day chart, dated by the Hong Kong day of its timestamp.
    daily = [{'date': datetime.datetime.fromtimestamp(int(ts) / 1000, HK).strftime('%Y-%m-%d'), 'oi_usd': rnd(num(oi), 0)}
             for ts, oi, _ in get(f'rubik/stat/contracts/open-interest-volume?ccy={coin}&period=1D')]
    daily = sorted([d for d in daily if d['oi_usd'] is not None], key=lambda d: d['date'])[-KEEP_DAYS:] or old.get('oi_daily', [])

    return {'hourly': out, 'oi_daily': daily, 'liq_cursor': new_cursor, 'liq_from': liq_from, 'liq_gaps': gaps}


def main():
    path = sys.argv[1]
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    now_ms = int(time.time() * 1000)
    coins = data.get('coins', {})
    failed = []
    for coin in COINS:
        try:
            coins[coin] = update_coin(coin, coins.get(coin, {}), now_ms)
        except Exception as e:                      # keep the other coins and the old data for this one
            failed.append(f'{coin}: {e}')
            print(f'warning: {coin} not updated: {e}', file=sys.stderr)
    if len(failed) == len(COINS):
        sys.exit('no coin could be updated:\n' + '\n'.join(failed))
    data = {
        'updated': datetime.datetime.fromtimestamp(now_ms / 1000, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'OKX public API (spot candles, contract statistics, USDT-margined swap liquidations)',
        'hours': KEEP_HOURS,
        'failed': failed,
        'coins': coins,
    }
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))
    os.replace(tmp, path)
    for coin in COINS:
        c = coins.get(coin, {})
        h = c.get('hourly', [])
        print(f"{coin}: {len(h)} hours, {sum(1 for r in h if 'liq_long' in r)} with liquidations, {len(c.get('oi_daily', []))} days of OI")


if __name__ == '__main__':
    main()
