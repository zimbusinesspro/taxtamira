"""
replace_vat_hero.py
===================
For every VAT lesson page:
  1. Removes the <div class="globe-hero"> block from inside .inner-box
  2. Inserts a <section class="feature-steps-container"> (matching the
     itcfoundations.html style) before <div class="lower-content">

Run once:  python replace_vat_hero.py
"""

import os
from bs4 import BeautifulSoup, NavigableString

FOLDER = r"C:/Users/Uncle Taps/Desktop/CGT LEFT HTML"

# ── Confirmed-working Unsplash images (same 3 used in itcfoundations.html) ──
IMG_CONTEXT     = "https://images.unsplash.com/photo-1723958929247-ef054b525153?q=80&w=2070&auto=format&fit=crop"
IMG_LEGISLATION = "https://images.unsplash.com/photo-1723931464622-b7df7c71e380?q=80&w=2070&auto=format&fit=crop"
IMG_CONCEPTS    = "https://images.unsplash.com/photo-1725961476494-efa87ae3106a?q=80&w=2070&auto=format&fit=crop"

# ── Step content per lesson: (context_text, legislation_text, concepts_text) ─
LESSON_STEPS = {
    "vatfoundations.html": (
        "VAT is a consumption tax levied on value added at each stage of production "
        "and distribution. In Zimbabwe, it replaced Sales Tax in 2004 and forms a "
        "cornerstone of the indirect tax system.",
        "The primary legislation is the VAT Act [Chapter 23:12], supported by the "
        "Finance Act, ZIMRA practice notes, and statutory instruments governing "
        "rates, exemptions, and administration.",
        "This lesson establishes the conceptual foundations of VAT — the invoice "
        "credit method, the destination principle, and how VAT compares to other "
        "indirect taxes operating in Zimbabwe.",
    ),
    "vatdefinitions.html": (
        "Precise legal definitions are the gateway to correct VAT compliance. "
        "Misunderstanding terms such as 'taxable supply' or 'registered operator' "
        "is one of the most common sources of VAT error in practice.",
        "Interpretation of the VAT Act [Chapter 23:12] begins with Section 2, "
        "which defines the principal terms. The Interpretation Act supplements "
        "the Act's construction rules where needed.",
        "Key definitions examined include 'taxable supply', 'exempt supply', "
        "'zero-rated supply', 'registered operator', 'enterprise', 'consideration', "
        "and 'services' — each carrying specific legal significance.",
    ),
    "vatimposition.html": (
        "Understanding the scope of VAT determines whether any transaction is "
        "taxable at all. Knowing the boundaries of the charge prevents both "
        "under-collection and costly over-collection by a business.",
        "Section 6 of the VAT Act imposes VAT on the supply of taxable goods or "
        "services in Zimbabwe, on importation of goods, and on imported services. "
        "Schedule 1 (exempt) and Schedule 2 (zero-rated) define the outer limits.",
        "This lesson covers the territorial scope of VAT, the meaning of 'supply "
        "in Zimbabwe', the charge on imported services, and the distinction between "
        "taxable, exempt, and out-of-scope supplies.",
    ),
    "vatrates.html": (
        "VAT does not apply at a single rate to all supplies. Zimbabwe's VAT system "
        "operates a multi-rate structure where the applicable rate depends on the "
        "nature of the supply, giving rise to both planning opportunities and "
        "compliance obligations.",
        "The standard rate is prescribed under Section 6(1) of the VAT Act. "
        "Schedule 1 identifies exempt supplies while Schedule 2 lists zero-rated "
        "supplies. Finance Act amendments periodically adjust which items fall "
        "in each category.",
        "This lesson covers the standard rate, zero-rated and exempt supplies, "
        "the policy rationale for differential rating, the practical impact on "
        "input tax recovery, and the VAT treatment of mixed supplies.",
    ),
    "vattimeofsupply.html": (
        "The timing of a supply determines when VAT is due, which return period "
        "it falls into, and when the tax point triggers the obligation to account "
        "for VAT. Getting this wrong affects cash flow and can trigger penalties.",
        "Section 9 of the VAT Act sets out the time of supply rules. The basic "
        "tax point is the earlier of invoice date or payment date. Specific "
        "provisions address continuous supplies, lay-by agreements, and deposits.",
        "This lesson covers the basic and special tax points, continuous and "
        "periodic supplies, the treatment of advances and deposits, goods supplied "
        "on approval, and interaction with the chosen accounting basis.",
    ),
    "vatvalueofsupply.html": (
        "The value of supply is the amount on which VAT is calculated. An "
        "understated value leads to under-payment of VAT; an overstated value "
        "inflates the supplier's output tax liability unnecessarily.",
        "Section 10 of the VAT Act governs the value of supply. The general rule "
        "is the total consideration received. Additional provisions apply to "
        "connected parties, non-monetary consideration, and imported services.",
        "Topics include the consideration rule, open market value for related-party "
        "supplies, the treatment of discounts and rebates, and the special "
        "valuation rule for barter and non-cash transactions.",
    ),
    "vatimportexport.html": (
        "Cross-border transactions are among the most complex areas of VAT law. "
        "The distinction between goods exported at zero rate and services subject "
        "to reverse charge demands careful analysis in every international deal.",
        "Zero-rating of exports is provided under Schedule 2 of the VAT Act. "
        "Section 6(1)(a) imposes VAT on imported goods at the port of entry. "
        "Imported services are governed by the reverse charge in Section 6(1)(b).",
        "This lesson covers zero-rating conditions for exports, VAT at importation, "
        "the reverse charge on imported services, customs duty interaction, and "
        "documentation requirements for zero-rating claims.",
    ),
    "vatspeciallevies.html": (
        "Beyond the standard VAT rate, certain transactions attract additional "
        "statutory levies that co-exist with VAT. Operators in tourism, hospitality, "
        "and other designated sectors must account for these charges accurately.",
        "Special levies are imposed under sector-specific legislation alongside "
        "the VAT Act. The Tourism Levy Act, Finance Acts, and applicable statutory "
        "instruments prescribe the rates and remittance procedures.",
        "Topics include the nature and purpose of special VAT charges, the tourism "
        "levy, AIDS levy interaction with VAT obligations, sector-specific "
        "surcharges, and the compliance implications for affected operators.",
    ),
    "vatregistration.html": (
        "VAT registration is the threshold between being an unregistered business "
        "and a VAT-collecting agent of the state. Understanding the rules determines "
        "when a business must register and the consequences of failing to do so.",
        "Section 23 of the VAT Act governs compulsory registration. Section 24 "
        "provides for voluntary registration. ZIMRA's registration process is "
        "supplemented by practice notes and TaRMS system procedures.",
        "Topics covered include the registration threshold, the rolling 12-month "
        "turnover test, voluntary registration, group and branch registration, "
        "registration effective dates, and deregistration procedures.",
    ),
    "vataccountingbasis.html": (
        "The VAT accounting basis determines when output tax is declared and input "
        "tax is claimed. Choosing the wrong basis or misunderstanding the switching "
        "rules causes cash-flow mismatches and triggers compliance failures.",
        "Section 15 of the VAT Act prescribes the invoice basis as the default. "
        "Section 16 allows qualifying taxpayers to use the payments (cash) basis. "
        "Switching between bases requires prior ZIMRA approval.",
        "This lesson examines the invoice basis, the payments basis, eligibility "
        "criteria for each, the practical impact on working capital management, "
        "and the documentary requirements for both methods.",
    ),
    "vatinputtax.html": (
        "The ability to deduct input tax is the mechanism that makes VAT a tax on "
        "value added rather than a cascading turnover tax. Understanding the "
        "conditions and restrictions is critical for every registered operator.",
        "Section 15 of the VAT Act governs input tax deductions. The Seventh "
        "Schedule lists blocked input tax items. ZIMRA practice notes provide "
        "guidance on the apportionment methodology for partially taxable businesses.",
        "Topics include conditions for a valid deduction, blocked input tax (motor "
        "vehicles, entertainment), the apportionment formula for mixed-use "
        "businesses, and documentary requirements for claims.",
    ),
    "vatadjustments.html": (
        "VAT amounts previously declared are not always final. Credits, debts "
        "written off, and changes in the use of assets all require VAT adjustments "
        "in subsequent returns — inaccuracy here distorts the entire VAT account.",
        "Change-in-use adjustments are governed by Sections 15(2)(d) and 16(3) "
        "of the VAT Act. Credit and debit notes are addressed in Sections 21 and "
        "22. Section 20 governs bad-debt relief for unpaid consideration.",
        "This lesson covers change-in-use adjustments, credit and debit notes, "
        "bad-debt relief conditions and recovery, error correction procedures, "
        "and adjustments on cessation of a taxable activity.",
    ),
    "vatdocumentation.html": (
        "The right to claim input tax and the validity of output tax declarations "
        "both depend on holding and issuing correct documentation. A poorly issued "
        "tax invoice can result in denial of a deduction and trigger audit penalties.",
        "Section 20 of the VAT Act prescribes the mandatory requirements for a "
        "valid tax invoice. Sections 21 and 22 cover credit and debit notes. "
        "ZIMRA's practice notes address electronic invoicing and fiscal devices.",
        "Topics include mandatory elements of a tax invoice, simplified invoices "
        "for small supplies, credit and debit note requirements, record-retention "
        "periods, fiscal device obligations, and export zero-rating documentation.",
    ),
    "vatcompliance.html": (
        "Submitting accurate VAT returns on time and settling the VAT account "
        "promptly are the cornerstones of compliance. Non-compliance exposes the "
        "operator to interest, penalties, and escalating ZIMRA enforcement action.",
        "Section 28 of the VAT Act governs return submission. Sections 30–33 "
        "address penalties and interest for late filing and late payment. ZIMRA's "
        "TaRMS is now the mandatory platform for VAT return submission.",
        "Topics include the VAT return filing cycle, calculating net VAT payable, "
        "payment due dates, the interest and penalty regime, voluntary disclosure, "
        "and best practice for reconciling the VAT account to underlying records.",
    ),
    "vatrefunds.html": (
        "When input tax credits exceed output tax in a period, the registered "
        "operator is entitled to a refund. Understanding the refund process — and "
        "the reasons ZIMRA may delay or withhold — is vital for cash-flow management.",
        "Section 29 of the VAT Act entitles registered operators to a refund of "
        "excess input tax. The Finance Act 2025 introduced changes to the "
        "accelerated refund scheme for qualifying exporters.",
        "Topics include when a refund arises, the standard refund process, the "
        "accelerated scheme for exporters, set-off against other tax liabilities, "
        "audit triggers from refund claims, and how to challenge a delayed refund.",
    ),
    "vatassessments.html": (
        "ZIMRA's power to assess VAT is a key enforcement tool. Taxpayers need "
        "to understand both the self-assessment system and ZIMRA's power to raise "
        "its own assessments where returns are absent or deficient.",
        "Section 31 of the VAT Act empowers the Commissioner to raise additional "
        "assessments. Section 32 prescribes the assessment prescription period. "
        "Section 33 governs self-assessment under the modern compliance framework.",
        "This lesson covers the self-assessment system, additional and revised "
        "assessments, the prescription period, estimated assessments where no "
        "return is filed, onus of proof, and the taxpayer's right to object.",
    ),
    "vatobjections.html": (
        "A VAT assessment that is disputed does not have to be accepted. The VAT "
        "Act provides a structured objections and appeals process that allows "
        "taxpayers to challenge ZIMRA's findings through administrative and "
        "judicial channels.",
        "Sections 35–38 of the VAT Act govern the objections and appeals process. "
        "The Fiscal Appeals Court provides the first judicial tier of appeal. "
        "Appeals to the High Court lie on questions of law.",
        "Topics include grounds for objection, the 30-day procedural deadline, "
        "drafting a valid objection, paying disputed tax pending resolution, "
        "escalation to the Fiscal Appeals Court, and High Court appeals.",
    ),
    "vataudits.html": (
        "ZIMRA has broad powers to audit and inspect registered operators. "
        "Understanding how an audit unfolds — and the rights available to the "
        "taxpayer — is essential for both proactive preparation and risk management.",
        "Sections 40–44 of the VAT Act empower the Commissioner to conduct "
        "audits, access premises and records, and issue production notices. "
        "Obstruction of a ZIMRA officer is a criminal offence under the Act.",
        "Topics include types of ZIMRA audit (desk, field, comprehensive), the "
        "audit process and taxpayer rights, responding to audit findings, onus "
        "of proof during audit, and the link between audit outcomes and assessments.",
    ),
    "vatdigital.html": (
        "Zimbabwe's drive toward electronic compliance — through fiscal devices, "
        "TaRMS, and new rules for digital services — is reshaping how operators "
        "discharge their VAT obligations. Staying current is non-negotiable.",
        "Fiscal device obligations are prescribed under statutory instruments "
        "issued pursuant to the VAT Act. The Finance Act 2025 introduced provisions "
        "governing imported electronic services and digital marketplace facilitation.",
        "Topics include fiscalisation requirements, electronic VAT invoicing, "
        "the VAT treatment of digital services and e-commerce, marketplace "
        "facilitator obligations, and ZIMRA's data-matching compliance initiatives.",
    ),
    "vatrepresentative.html": (
        "Not every VAT obligation falls on the principal taxpayer. The concept "
        "of representative persons and withholding agents distributes compliance "
        "responsibilities to agents and intermediaries who become personally liable.",
        "Section 48 of the VAT Act defines and imposes obligations on "
        "representative persons. Section 49 provides for VAT withholding agents. "
        "Finance Acts have periodically expanded the categories of designated agent.",
        "Topics include who qualifies as a representative person, their personal "
        "liability for the principal's VAT, withholding agent obligations, "
        "and the interaction with cross-border service payment rules.",
    ),
    "vatindustryrules.html": (
        "Several industries in Zimbabwe are subject to special VAT provisions "
        "that depart from the general rules. Practitioners advising in financial "
        "services, mining, agriculture, or real estate must understand these "
        "sector-specific modifications.",
        "The VAT Act's special provisions are supplemented by sector instruments: "
        "the Banking Act for financial services, the Mines and Minerals Act for "
        "mining, and statutory instruments for agriculture and real estate.",
        "Topics include the VAT treatment of financial services (exempt, input "
        "tax denied), farming and agro-processing special rules, real estate "
        "provisions, mining input tax recovery, and professional services.",
    ),
    "vatantiavoidance.html": (
        "VAT avoidance — structuring transactions artificially to avoid, reduce, "
        "or defer the VAT charge — is countered by the Commissioner's general "
        "anti-avoidance powers and statutory provisions targeting sham arrangements.",
        "Section 45 of the VAT Act empowers the Commissioner-General to disregard "
        "transactions designed to avoid VAT. Connected-party supply rules under "
        "Section 10 address under-valued related-party transactions.",
        "Topics include the general anti-avoidance rule, artificial splitting of "
        "transactions, the connected-party valuation override, VAT fraud criminal "
        "penalties, and ZIMRA's enforcement approach to avoidance schemes.",
    ),
    "vatpractical.html": (
        "Theory becomes meaningful when applied to real transactions. This lesson "
        "tests VAT knowledge against practical business scenarios — from a small "
        "retail trader to a large manufacturer — in the Zimbabwean context.",
        "All provisions of the VAT Act [Chapter 23:12] are potentially applicable "
        "here, with emphasis on Sections 6, 9, 10, 15 and 16 governing the charge, "
        "time, value, deductions, and filing obligations.",
        "Topics include end-to-end VAT compliance for a business cycle, computing "
        "net VAT payable, completing a VAT return, identifying VAT errors in a set "
        "of accounts, and applying the rules to complex multi-supply scenarios.",
    ),
    "vattoolkit.html": (
        "The VAT practitioner toolkit is a consolidated reference for exam "
        "candidates and practitioners, bringing together key rules, common pitfalls, "
        "quick-reference decision trees, and worked examples for efficient revision.",
        "This toolkit covers the entire VAT Act [Chapter 23:12] in a condensed "
        "format. Priority is given to Sections 2, 6, 9, 10, 15, 16, 20, 23, 28, "
        "29 and 35, and both Schedules 1 and 2.",
        "Topics include VAT calculation checklists, the most common VAT mistakes, "
        "decision trees for registration, rate classification, time/value of supply, "
        "and exam-style worked examples across the full range of VAT scenarios.",
    ),
}


def build_feature_steps_html(ctx, leg, con):
    """Return the feature-steps-container HTML string for a lesson."""
    return f"""<!-- New Feature Steps Section -->
<section class="feature-steps-container" id="lesson-overview-steps">
<div class="feature-steps-wrapper">
<div class="feature-steps-grid">
<div class="steps-list">
<!-- Step 1 -->
<div class="step-item" data-index="0">
<div class="step-number-wrap">1</div>
<div class="step-content">
<h3>Context</h3>
<p>{ctx}</p>
<div class="step-progress-container">
<div class="step-progress-bar"></div>
</div>
</div>
</div>
<!-- Step 2 -->
<div class="step-item" data-index="1">
<div class="step-number-wrap">2</div>
<div class="step-content">
<h3>Legislation</h3>
<p>{leg}</p>
<div class="step-progress-container">
<div class="step-progress-bar"></div>
</div>
</div>
</div>
<!-- Step 3 -->
<div class="step-item" data-index="2">
<div class="step-number-wrap">3</div>
<div class="step-content">
<h3>Concepts</h3>
<p>{con}</p>
<div class="step-progress-container">
<div class="step-progress-bar"></div>
</div>
</div>
</div>
</div>
<div class="feature-image-side">
<div class="feature-image-item active">
<img alt="Context" src="{IMG_CONTEXT}"/>
<div class="image-overlay"></div>
</div>
<div class="feature-image-item">
<img alt="Legislation" src="{IMG_LEGISLATION}"/>
<div class="image-overlay"></div>
</div>
<div class="feature-image-item">
<img alt="Concepts" src="{IMG_CONCEPTS}"/>
<div class="image-overlay"></div>
</div>
</div>
</div>
</div>
</section>"""


def process_file(filepath, ctx, leg, con):
    fname = os.path.basename(filepath)
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    soup = BeautifulSoup(raw, "html.parser")

    inner = soup.find("div", class_="inner-box")
    if not inner:
        return "no-inner-box"

    # ── 1. Remove globe-hero ──────────────────────────────────────────────
    globe = inner.find("div", class_="globe-hero")
    if globe:
        globe.decompose()
    else:
        return "no-globe-hero"

    # ── 2. Insert feature-steps-container before lower-content ───────────
    lower = inner.find("div", class_="lower-content")
    if not lower:
        return "no-lower-content"

    steps_soup = BeautifulSoup(build_feature_steps_html(ctx, leg, con), "html.parser")
    steps_tag  = steps_soup.find("section", class_="feature-steps-container")

    lower.insert_before(steps_tag)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))
    return "updated"


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    updated, issues = [], []

    for fname, (ctx, leg, con) in LESSON_STEPS.items():
        path = os.path.join(FOLDER, fname)
        if not os.path.exists(path):
            issues.append((fname, "FILE NOT FOUND"))
            continue
        result = process_file(path, ctx, leg, con)
        if result == "updated":
            updated.append(fname)
        else:
            issues.append((fname, result))

    print("=" * 60)
    print(f"UPDATED  ({len(updated)})")
    for f in updated:
        print("  +", f)
    if issues:
        print()
        print(f"ISSUES  ({len(issues)})")
        for f, reason in issues:
            print(f"  ! {f}  ({reason})")
    print("=" * 60)
