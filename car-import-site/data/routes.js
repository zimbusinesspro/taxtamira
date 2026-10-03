// Shipping and inland routes from Japan to Zimbabwe. All costs are illustrative USD figures;
// replace them with your shipping line, transporter and agent quotes.
//   freight   - Japan port to destination port (RoRo), per vehicle
//   insurance - marine insurance as a share of FOB
//   portFees  - destination port handling, wharfage and agency
//   transit   - road transit to the Zimbabwe border (fuel, driver/carrier, transit bond)
//   borderFees- border-post charges excluding duty
window.ROUTES = [
  {
    id: "durban-beitbridge",
    name: "Durban (SA) → Beitbridge → Harare",
    days: "35–45",
    freight: 1250, insurance: 0.015, portFees: 420, transit: 650, borderFees: 120,
    notes: "Most frequent sailings; road transit through South Africa under bond."
  },
  {
    id: "beira-forbes",
    name: "Beira (MZ) → Forbes/Mutare → Harare",
    days: "40–50",
    freight: 1400, insurance: 0.015, portFees: 380, transit: 380, borderFees: 110,
    notes: "Shortest road leg to eastern Zimbabwe."
  },
  {
    id: "dar-chirundu",
    name: "Dar es Salaam (TZ) → Chirundu → Harare",
    days: "40–55",
    freight: 1150, insurance: 0.015, portFees: 450, transit: 900, borderFees: 130,
    notes: "Lower freight, longer road leg through Zambia."
  },
  {
    id: "walvis-kazungula",
    name: "Walvis Bay (NA) → Kazungula → Bulawayo",
    days: "45–60",
    freight: 1300, insurance: 0.015, portFees: 400, transit: 850, borderFees: 120,
    notes: "Suits western Zimbabwe; fewer sailings."
  }
];
