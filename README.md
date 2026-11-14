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

**Snapshot** taken on 13 November 2026 (Hong Kong time) and stored inside `index.html`, because these two sources do not allow calls from a web page:

- OKX open-interest history chart
- spot ETF net flows (CoinMarketCap)

Every section is labelled 即時 (live) or 快照 (snapshot) with its time. If a source cannot be reached, that section falls back to the snapshot and its label says so.

Opening the 衍生品 tab downloads about 2 MB (CoinGecko's full derivatives list) and pages through a day of OKX liquidation orders, so it takes longer than the other tabs.

## Meanings and readings

Every section has two extra parts:

- **每項數據嘅含意** (what each figure means): a closed list under the section explaining each number in plain words.
- **數字解讀** (reading of the numbers): a few sentences worked out from the figures on screen each time they load, such as how far the price is from its moving averages, whether funding is above or below the usual 0.01%, or which side most liquidations came from. They describe the data and never advise buying or selling.

## Files

- `index.html` is the whole app, with the snapshot data inside it. To update the app, upload a new `index.html`; the link stays the same.
- `manifest.webmanifest` and the `icon-*.png` files are what "Add to Home Screen" uses.

For information only, not financial advice.
