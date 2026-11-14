# 加密市場隨身版 (Crypto Market Pocket)

A phone-first crypto market app for BTC, ETH and SOL, in Cantonese: prices, moving averages, derivatives, spot ETF flows and on-chain data, in five tabs.

**Open it:** https://raymondchan2046.github.io/crypto-pocket/

On a phone, choose "Add to Home Screen" in the browser menu to open it full screen like an app.

## What is live and what is a snapshot

**Live**, loaded from [CoinGecko](https://www.coingecko.com/)'s public API each time the page opens and about once a minute while it stays open (no account or API key needed):

- price, 24-hour, 7-day and 30-day change, 24-hour high and low, market cap, distance from all-time high
- total crypto market cap and each coin's share of it

**Snapshot** taken on 13 November 2026 (Hong Kong time) and stored inside `index.html`:

- daily closes and moving averages (Kraken)
- Fear & Greed Index (alternative.me)
- open interest and funding rates (CoinGecko derivatives, OKX)
- liquidations (OKX)
- spot ETF net flows (CoinMarketCap)
- on-chain data (Coin Metrics, DefiLlama, mempool.space)

Every section is labelled 即時 (live) or 快照 (snapshot) with its time. If CoinGecko cannot be reached, the live numbers fall back to the snapshot and the page says so.

## Files

- `index.html` is the whole app, with the snapshot data inside it. To update the app, upload a new `index.html`; the link stays the same.
- `manifest.webmanifest` and the `icon-*.png` files are what "Add to Home Screen" uses.

For information only, not financial advice.
