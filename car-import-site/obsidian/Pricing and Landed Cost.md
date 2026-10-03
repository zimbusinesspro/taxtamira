---
tags: [car-import, pricing, tax]
---
# Pricing and Landed Cost
Back to [[Car Import Business - Map]] · Related: [[Routes to Zimbabwe]]

**FOB** (vehicle price in Japan) + freight + insurance = **CIF** (the customs value).

Landed cost = CIF + port fees + road transit + border fees + duties and taxes + clearing agent + registration.

Duties and taxes (rates set in `assets/config.js`; **all placeholders, so verify with ZIMRA or a clearing agent**):
- Customs duty: a percentage of CIF
- Surtax: applies to vehicles above an age threshold
- VAT on importation: charged on CIF + customs duty
- Carbon tax: a flat amount that depends on engine size

> [!warning] Before going live
> Confirm every rate against the current Customs and Excise Tariff and Finance Act, then update `config.js`.
