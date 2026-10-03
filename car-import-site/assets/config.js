// Site-wide settings. Edit these values to brand the site as your own.
window.SITE_CONFIG = {
  brandName: "Your Brand Motors",
  tagline: "Japanese vehicles, sourced at auction and delivered to your door",
  whatsappNumber: "263770000000", // international format, no "+" or spaces
  phoneDisplay: "+263 77 000 0000",
  email: "sales@example.com",
  enquiryFormUrl: "", // optional: link to a Google Form or similar; leave blank to use the built-in form
  currency: "USD",

  // Illustrative import charges used by the landed-cost estimator.
  // These are placeholders only: confirm current rates with ZIMRA / your clearing agent
  // before quoting a client, and update them whenever the Finance Act changes.
  duties: {
    customsDutyRate: 0.40,   // applied to the customs (CIF) value
    vatRate: 0.155,          // applied to CIF + customs duty
    surtaxRate: 0.35,        // applied to CIF on vehicles at or above surtaxAgeYears
    surtaxAgeYears: 5,
    clearingAgentFee: 350,   // flat fee
    registrationAndPlates: 250,
    carbonTaxByCc: [         // flat amounts by engine size band
      { maxCc: 1500, amount: 100 },
      { maxCc: 2000, amount: 150 },
      { maxCc: 3000, amount: 250 },
      { maxCc: Infinity, amount: 400 }
    ]
  }
};
