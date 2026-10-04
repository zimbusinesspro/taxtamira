---
tags: [car-import, sourcing]
---
# Vehicle Sourcing
Back to [[Car Import Business - Map]] · Related: [[Website Features]], [[Next Steps]]

**Current state:** the site's prices come from `data/vehicles.js`, which holds sample rows typed in by hand. Nothing is pulled from Japan yet.

## Ways to get real cars and prices
1. **Auctions through a Japan-based agent or exporter.** The big auction groups (USS, TAA, JU, HAA, CAA, Aucnet) are dealer-only. A licensed exporter bids for you for a fee. Your site shows a *maximum* price per model and the agent bids up to it. This is what the "max price, may decrease if won lower" wording points to.
2. **Exporter stock partnerships.** Large exporters with ready stock in Japan (and some with stock already in Durban or Dar) run dealer, agent or affiliate programmes. Some provide a stock feed or API you can display on your site.
3. **A manual price list.** You agree a max-price list with your agent each month and update `data/vehicles.js`. This is the simplest way to launch.

> [!warning] Don't scrape
> Don't copy listings or photos from another company's site without written permission. It breaks their terms and can create copyright problems.

## Questions to ask a Japan agent
- Auction access and fee per car won
- Inspection, auction-sheet translation and photos
- Deposit terms and what happens if a bid fails
- Shipping lines and sailings to Durban, Beira, Dar es Salaam and Walvis Bay
- Whether they provide a stock feed or API
