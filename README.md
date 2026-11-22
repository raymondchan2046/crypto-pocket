# 加密市場隨身版 (Crypto Market Pocket)

A phone-first crypto market app for BTC, ETH and SOL, in Cantonese: prices, a rebound check, moving averages, derivatives, spot ETF flows and on-chain data, in five tabs.

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
| Hourly leverage and flow chart, OKX open-interest history | OKX statistics, collected by this repository's job (see below) |
| Spot ETF daily net flows | CoinMarketCap, collected by the same job, because CoinMarketCap does not let a web page read it |

Every section is labelled with its time. If a source cannot be reached, that section falls back to a **snapshot** stored inside `index.html`, taken on 22 November 2026 (Hong Kong time), and its label says 快照 (snapshot).

Opening the 衍生品 tab reads the first two pages of CoinGecko's derivatives list (500 contracts, busiest first, which hold more than 99% of these coins' open interest on the ten exchanges) and pages through a day of OKX liquidation orders, so it takes longer than the other tabs.

## Meanings and readings

Every section has two extra parts:

- **每項數據嘅含意** (what each figure means): a closed list under the section explaining each number in plain words.
- **數字解讀** (reading of the numbers): a few sentences worked out from the figures on screen each time they load, such as how far the price is from its moving averages, whether funding is above or below the usual 0.01%, or which side most liquidations came from. They describe the data and never advise buying or selling.

## Rebound check (反彈訊號檢查)

At the top of the 市場 tab, for the coin you pick, the app checks seven conditions often cited before a rebound and shows which ones hold right now. It recalculates whenever new data loads, so it stays current while the page is open.

| Group | Condition |
|---|---|
| Oversold and deleveraged (超賣同去槓桿) | Fear & Greed Index 25 or below |
| | Daily RSI(14) 30 or below |
| | OKX open interest, counted in coins, down 3% or more in 24 hours |
| | Long positions are 65% or more of OKX liquidations in 24 hours |
| | OKX funding rate negative |
| Signs of a turn (轉勢跡象) | Price 2% or more above its 24-hour low, set at least 2 hours ago |
| | More aggressive buying than selling on OKX contracts over the last 4 hours |

The badge reads:

- 條件齊: at least 3 of the first group and both of the second.
- 留意: at least 3 of the first group without both signs of a turn, or both signs with 2 of the first group.
- 未見訊號: otherwise.
- 數據唔夠: missing data could change the answer.

Snapshot data, and OKX hourly data more than two and a half hours old, is never counted.

**This is a description of the data, not a forecast.** The conditions and thresholds are common rules of thumb, not a tested model. Under the badge, the card replays a daily version of the check over the past year: extreme fear and an oversold RSI, then a close 2% above the recent low. It shows how often the price was higher 7 days later, next to how often that was true on any day. When this check was added (16 November 2026), the replay had come out worse than a coin flip for all three coins: BTC was higher 7 days later 2 times out of 6, ETH 2 out of 6 and SOL 2 out of 5.

## Hourly leverage and flow (每小時槓桿同資金流)

The 衍生品 tab has a chart of five panels on one hourly axis, for the last 24 hours, 3 days or 7 days: price, open interest across OKX contracts, net taker buying, the long/short account ratio and liquidations of the USDT-margined perpetual. Touching any panel shows every figure for that hour.

OKX does not let a web page read these statistics, and keeps only about a day of liquidation orders. So `.github/workflows/okx-data.yml` runs `scripts/update_okx.py` every hour at about 23 minutes past (GitHub often starts it a few minutes late). It merges the new hours into `okx.json` and publishes it on the `data` branch as a single commit that each run replaces, so the branch never grows. The page reads that file from `raw.githubusercontent.com`. Liquidations are kept from 15 November 2026 onward, for seven days; hours that a missed run left incomplete are shaded grey.

The same job also collects the last 90 days of US spot ETF net flows for the three coins from CoinMarketCap.

GitHub starts scheduled jobs on a best-effort basis, and in its first days it started this one only every 6 to 11 hours, not every hour. Between runs, the chart and the rebound check's hourly conditions show the time of the last update. After two and a half hours the rebound check stops counting them.

To run it by hand: Actions → Update OKX hourly data → Run workflow. GitHub pauses scheduled workflows in a public repository after 60 days without activity; if that happens, the same page offers to turn it back on.

## Files

- `index.html` is the whole app, with the snapshot data inside it. To update the app, upload a new `index.html`; the link stays the same.
- `manifest.webmanifest` and the `icon-*.png` files are what "Add to Home Screen" uses.
- `scripts/update_okx.py` and `.github/workflows/okx-data.yml` collect the hourly OKX data.

For information only, not financial advice.
