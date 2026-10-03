(function () {
  const cfg = window.SITE_CONFIG;
  const vehicles = window.VEHICLES;
  const routes = window.ROUTES;
  const $ = (sel) => document.querySelector(sel);
  const money = (n) => new Intl.NumberFormat("en-US", { style: "currency", currency: cfg.currency, maximumFractionDigits: 0 }).format(n);
  const label = (v) => `${v.year} ${v.make} ${v.model}`;
  const waLink = (text) => `https://wa.me/${cfg.whatsappNumber}${text ? "?text=" + encodeURIComponent(text) : ""}`;

  // Branding and contact details
  document.title = `${cfg.brandName} | Japanese Vehicle Imports`;
  document.querySelectorAll("[data-brand]").forEach((el) => (el.textContent = cfg.brandName));
  document.querySelectorAll("[data-tagline]").forEach((el) => (el.textContent = cfg.tagline));
  document.querySelectorAll("[data-phone]").forEach((el) => (el.textContent = cfg.phoneDisplay));
  document.querySelectorAll("[data-email]").forEach((el) => { el.textContent = cfg.email; el.href = "mailto:" + cfg.email; });
  document.querySelectorAll("[data-wa]").forEach((el) => (el.href = waLink("Hello, I'd like to import a vehicle from Japan.")));
  if (cfg.enquiryFormUrl) { const a = $("#external-form"); a.href = cfg.enquiryFormUrl; a.hidden = false; }

  // ---- Price search ----
  const fill = (sel, values) => values.forEach((v) => sel.add(new Option(v, v)));
  const uniq = (key) => [...new Set(vehicles.map((v) => v[key]))].sort();
  fill($("#f-make"), uniq("make"));
  fill($("#f-body"), uniq("body"));
  fill($("#f-fuel"), uniq("fuel"));

  function renderPrices() {
    const make = $("#f-make").value, body = $("#f-body").value, fuel = $("#f-fuel").value;
    const budget = parseFloat($("#f-budget").value) || Infinity;
    const q = $("#f-q").value.trim().toLowerCase();
    const rows = vehicles
      .map((v, i) => ({ v, i }))
      .filter(({ v }) => (!make || v.make === make) && (!body || v.body === body) && (!fuel || v.fuel === fuel)
        && v.maxPrice <= budget && (!q || `${v.make} ${v.model}`.toLowerCase().includes(q)))
      .sort((a, b) => a.v.maxPrice - b.v.maxPrice);
    $("#result-count").textContent = `${rows.length} vehicle${rows.length === 1 ? "" : "s"} found`;
    $("#price-rows").innerHTML = rows.map(({ v, i }) => `
      <tr>
        <td>${v.make}</td><td>${v.model}</td><td>${v.year}</td><td>${v.cc} cc</td>
        <td>${v.body}</td><td>${v.fuel}</td><td class="num">${money(v.maxPrice)}</td>
        <td><button class="link-btn" data-pick="${i}">Calculate →</button></td>
      </tr>`).join("");
  }
  ["#f-make", "#f-body", "#f-fuel", "#f-budget", "#f-q"].forEach((s) => $(s).addEventListener("input", renderPrices));
  $("#price-rows").addEventListener("click", (e) => {
    const i = e.target.dataset.pick;
    if (i === undefined) return;
    $("#c-vehicle").value = i;
    loadVehicle(+i);
    $("#calculator").scrollIntoView();
  });

  // ---- Landed-cost calculator ----
  vehicles.forEach((v, i) => $("#c-vehicle").add(new Option(`${label(v)} (max ${money(v.maxPrice)})`, i)));
  routes.forEach((r) => $("#e-route").add(new Option(r.name, r.name)));

  function loadVehicle(i) {
    const v = vehicles[i];
    $("#c-fob").value = v.maxPrice;
    $("#c-year").value = v.year;
    $("#c-cc").value = v.cc;
    $("#e-vehicle").value = label(v);
    renderRoutes();
  }

  function duties(cif, year, cc) {
    const d = cfg.duties;
    const age = new Date().getFullYear() - year;
    const customs = cif * d.customsDutyRate;
    const surtax = age >= d.surtaxAgeYears ? cif * d.surtaxRate : 0;
    const vat = (cif + customs) * d.vatRate;
    const carbon = d.carbonTaxByCc.find((b) => cc <= b.maxCc).amount;
    return { customs, surtax, vat, carbon, clearing: d.clearingAgentFee, reg: d.registrationAndPlates };
  }

  function costRoute(r, fob, year, cc, withDuty) {
    const insurance = fob * r.insurance;
    const cif = fob + r.freight + insurance;
    const lines = [
      ["Vehicle (FOB)", fob],
      ["Ocean freight", r.freight],
      ["Marine insurance", insurance],
      ["Port & agency fees", r.portFees],
      ["Road transit", r.transit],
      ["Border fees", r.borderFees]
    ];
    if (withDuty) {
      const t = duties(cif, year, cc);
      lines.push(["Customs duty", t.customs], ["Surtax (older vehicles)", t.surtax], ["VAT on import", t.vat],
        ["Carbon tax", t.carbon], ["Clearing agent", t.clearing], ["Registration & plates", t.reg]);
    }
    return { lines, total: lines.reduce((s, [, n]) => s + n, 0) };
  }

  function renderRoutes() {
    const fob = parseFloat($("#c-fob").value) || 0;
    const year = parseInt($("#c-year").value, 10) || new Date().getFullYear();
    const cc = parseInt($("#c-cc").value, 10) || 1500;
    const withDuty = $("#c-duty").checked;
    const results = routes.map((r) => ({ r, ...costRoute(r, fob, year, cc, withDuty) }));
    const best = Math.min(...results.map((x) => x.total));
    $("#route-cards").innerHTML = results.map(({ r, lines, total }) => `
      <article class="route-card${total === best ? " best" : ""}">
        <h3>${r.name}${total === best ? '<span class="badge">Lowest</span>' : ""}</h3>
        <p class="days">${r.days} days · ${r.notes}</p>
        <dl>${lines.filter(([, n]) => n > 0).map(([k, n]) => `<dt>${k}</dt><dd>${money(n)}</dd>`).join("")}</dl>
        <div class="total"><span>Estimated total</span><span>${money(total)}</span></div>
      </article>`).join("");
  }
  $("#c-vehicle").addEventListener("change", (e) => loadVehicle(+e.target.value));
  ["#c-fob", "#c-year", "#c-cc", "#c-duty"].forEach((s) => $(s).addEventListener("input", renderRoutes));

  // ---- Enquiry via WhatsApp ----
  $("#enquiry").addEventListener("submit", (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    const text = [
      `Vehicle enquiry from ${f.get("name")} (${f.get("phone")})`,
      f.get("vehicle") && `Vehicle: ${f.get("vehicle")}`,
      f.get("route") && `Route: ${f.get("route")}`,
      f.get("message")
    ].filter(Boolean).join("\n");
    window.open(waLink(text), "_blank", "noopener");
  });

  renderPrices();
  loadVehicle(0);
})();
