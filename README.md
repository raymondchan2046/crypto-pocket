# 加密市場隨身版 (Crypto Market Pocket)

A phone-first crypto market app for BTC, ETH and SOL, in Cantonese: prices, moving averages, derivatives, spot ETF flows and on-chain data, in five tabs.

**Open it:** https://raymondchan2046.github.io/crypto-pocket/

On a phone, choose "Add to Home Screen" in the browser menu to open it full screen like an app.

## What is live and what is a snapshot

**Live**, loaded straight from each source's public API (no account or API key needed). Prices refresh about once a minute; the rest load when you open their tab:

| Section | Source |
|---|---|
| Price, changes, 24-hour high and low, market cap, total market cap, market share | [CoinGecko](https://www.coingecko.com/) |
| Daily closes, sparklines and moving averages | Kraken |
| Fear & Greed Index | alternative.me |
| Open interest and funding rate across ten exchanges | CoinGecko derivatives |
| Funding-rate history | OKX |
| Liquidations, last 24 hours | OKX |
| Active addresses, transactions, MVRV | Coin Metrics community data |
| Chain fees, TVL, stablecoin supply, DEX volume | DefiLlama |
| Bitcoin network | mempool.space |
| Hourly leverage and flow chart, OKX open-interest history | OKX statistics, collected every hour by this repository (see below) |

**Snapshot** taken on 13 November 2026 (Hong Kong time) and stored inside `index.html`, because its source does not allow calls from a web page:

- spot ETF net flows (CoinMarketCap)

Every section is labelled 即時 (live) or 快照 (snapshot) with its time. If a source cannot be reached, that section falls back to the snapshot and its label says so.

Opening the 衍生品 tab downloads about 2 MB (CoinGecko's full derivatives list) and pages through a day of OKX liquidation orders, so it takes longer than the other tabs.

## Meanings and readings

Every section has two extra parts:

- **每項數據嘅含意** (what each figure means): a closed list under the section explaining each number in plain words.
- **數字解讀** (reading of the numbers): a few sentences worked out from the figures on screen each time they load, such as how far the price is from its moving averages, whether funding is above or below the usual 0.01%, or which side most liquidations came from. They describe the data and never advise buying or selling.

## Hourly leverage and flow (每小時槓桿同資金流)

The 衍生品 tab has a chart of five panels on one hourly axis, for the last 24 hours, 3 days or 7 days: price, open interest across OKX contracts, net taker buying, the long/short account ratio and liquidations of the USDT-margined perpetual. Touching any panel shows every figure for that hour.

OKX does not let a web page read these statistics, and keeps only about a day of liquidation orders. So `.github/workflows/okx-data.yml` runs `scripts/update_okx.py` every hour at about 17 minutes past. It merges the new hours into `okx.json` and publishes it on the `data` branch as a single commit that each run replaces, so the branch never grows. The page reads that file from `raw.githubusercontent.com`. Liquidations are kept from 15 November 2026 onward, for seven days; hours that a missed run left incomplete are shaded grey.

To run it by hand: Actions → Update OKX hourly data → Run workflow. GitHub pauses scheduled workflows in a public repository after 60 days without activity; if that happens, the same page offers to turn it back on.

## Files

- `index.html` is the whole app, with the snapshot data inside it. To update the app, upload a new `index.html`; the link stays the same.
- `manifest.webmanifest` and the `icon-*.png` files are what "Add to Home Screen" uses.
- `scripts/update_okx.py` and `.github/workflows/okx-data.yml` collect the hourly OKX data.

For information only, not financial advice.
