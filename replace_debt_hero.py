"""
replace_debt_hero.py
====================
Applies feature-steps-container (animated, ITC-style) to all 26 debt
management lesson pages:

  NEW-STYLE files (24) — div.lesson-container, no globe-hero:
    1. Insert feature-steps-container after div.lesson-page-header
    2. Add css/feature-steps.css after css/globe-hero.css in <head>
    3. Add js/feature-steps.js + FeatureSteps initialiser after
       js/globe-hero.js at bottom of <body>

  LEGACY files (2) — div.inner-box, globe-hero present:
    1. Remove div.globe-hero from div.inner-box
    2. Insert feature-steps-container before div.lower-content
    3. Same CSS/JS injection as above

Run once:  python replace_debt_hero.py
"""

import os
from bs4 import BeautifulSoup, NavigableString

FOLDER = r"C:/Users/Uncle Taps/Desktop/CGT LEFT HTML"

# ── Image URLs (same Unsplash images as ITC/VAT lessons) ──────────────────────
IMG_CONTEXT     = "https://images.unsplash.com/photo-1723958929247-ef054b525153?q=80&w=2070&auto=format&fit=crop"
IMG_LEGISLATION = "https://images.unsplash.com/photo-1723931464622-b7df7c71e380?q=80&w=2070&auto=format&fit=crop"
IMG_CONCEPTS    = "https://images.unsplash.com/photo-1725961476494-efa87ae3106a?q=80&w=2070&auto=format&fit=crop"

# ── CSS / JS anchors ──────────────────────────────────────────────────────────
FEATURE_CSS = "css/feature-steps.css"
GLOBE_CSS   = "css/globe-hero.css"
GLOBE_JS    = "js/globe-hero.js"
FEATURE_JS  = "js/feature-steps.js"

INIT_SCRIPT = (
    "\n\t\tdocument.addEventListener('DOMContentLoaded', () => {\n"
    "\t\t\tnew FeatureSteps('lesson-overview-steps', {\n"
    "\t\t\t\tfeatures: [\n"
    "\t\t\t\t\t{ title: 'Context' },\n"
    "\t\t\t\t\t{ title: 'Legislation' },\n"
    "\t\t\t\t\t{ title: 'Concepts' }\n"
    "\t\t\t\t],\n"
    "\t\t\t\tautoPlayInterval: 4000\n"
    "\t\t\t});\n"
    "\t\t});\n"
    "\t"
)

# ── Lesson step content: (context_text, legislation_text, concepts_text) ──────
LESSON_STEPS = {
    "debtintroduction.html": (
        "Tax debt management is the process by which ZIMRA identifies, assesses, and recovers unpaid tax obligations owed by individuals, businesses, and other entities.",
        "Governed by the Income Tax Act [Chapter 23:06], the VAT Act [Chapter 23:12], the ZIMRA Act [Chapter 23:11], and the Finance Act 2025, which collectively define ZIMRA's collection mandate.",
        "This lesson covers the nature of tax debt, ZIMRA's statutory debt collection mandate, the debt management lifecycle, and the importance of proactive compliance by taxpayers.",
    ),
    "debtcreation.html": (
        "Tax debt arises when a taxpayer fails to pay assessed or self-assessed tax within the prescribed due dates, triggering legal obligations and enforcement rights for ZIMRA.",
        "Creation of debt is governed by the payment and assessment provisions of the Income Tax Act [Chapter 23:06] and VAT Act [Chapter 23:12], including self-assessment obligations under Finance Act amendments.",
        "This lesson examines how tax liability crystallises into enforceable debt, covering due dates, self-assessment obligations, default mechanisms, and the legal character of tax debt.",
    ),
    "debtassessments.html": (
        "A tax assessment is ZIMRA's formal determination of a taxpayer's liability, serving as the legal foundation for debt collection action and enforcement proceedings.",
        "Assessment powers are conferred by sections of the Income Tax Act [Chapter 23:06] and VAT Act [Chapter 23:12], empowering ZIMRA to issue original, estimated, additional, and revised assessments.",
        "This lesson examines types of assessments, the assessment period, how assessments crystallise legally enforceable debt, objection rights, and the link between assessment and collection.",
    ),
    "debtidentification.html": (
        "Effective debt management begins with accurately identifying and classifying outstanding tax obligations across all tax types — a prerequisite for targeted and proportionate collection action.",
        "ZIMRA's TARMS system and relevant provisions of the Income Tax Act [Chapter 23:06] govern debt identification, account maintenance, and the categorisation of outstanding obligations by age and type.",
        "This lesson covers debt segmentation by tax type, age and collectibility; risk-based classification; the distinction between active and dormant debt; and how ZIMRA prioritises its collection portfolio.",
    ),
    "debttaxpayeraccount.html": (
        "Maintaining accurate taxpayer accounts is fundamental to computing correct debt balances, issuing accurate statements, and directing proportionate collection action to the right taxpayer.",
        "Account management is governed by record-keeping and administrative provisions of the Income Tax Act [Chapter 23:06], VAT Act [Chapter 23:12], and TARMS operational guidelines.",
        "This lesson covers taxpayer account reconciliation, statement of account interpretation, how credits and debits are applied, interest and penalty accumulation on accounts, and account correction procedures.",
    ),
    "debtclearance.html": (
        "Tax clearance certificates are official confirmations of a taxpayer's good standing, frequently required for participation in government tenders, business registration renewals, and corporate transactions.",
        "The issuance and withdrawal of clearance certificates is governed by sections of the Finance Act, the Procurement and Disposal of Public Assets Act, and ZIMRA's administrative procedures.",
        "This lesson examines the criteria for obtaining clearance, the impact of outstanding debt on certificate eligibility, strategic compliance to maintain clearance status, and the use of clearance certificates in commerce.",
    ),
    "debtinterestpenalties.html": (
        "Late payment of tax attracts both statutory interest and administrative penalties, which compound over time and can significantly inflate the total amount a taxpayer owes to ZIMRA.",
        "Interest and penalty provisions are contained in the Income Tax Act [Chapter 23:06], VAT Act [Chapter 23:12], and the Finance Act 2025, which prescribes current rates and grounds for waiver.",
        "This lesson covers the calculation of interest on overdue tax, fixed and percentage-based administrative penalties, the compounding effect of long-standing arrears, and the procedures for seeking remission or waiver.",
    ),
    "debtpaymentliabilities.html": (
        "Understanding precisely when and how tax liabilities must be paid is essential to preventing the creation of debt and avoiding the penalties and enforcement action that follow non-payment.",
        "Payment due dates and methods are prescribed by the Income Tax Act [Chapter 23:06], the VAT Act [Chapter 23:12], PAYE regulations, and provisional tax provisions of the Finance Act 2025.",
        "This lesson covers self-assessment payment deadlines, provisional tax instalments, methods of payment accepted by ZIMRA, the legal effect of late payment, and strategies for managing payment obligations.",
    ),
    "debtcollection.html": (
        "ZIMRA employs a structured continuum of strategies to recover outstanding tax debt, ranging from informal reminders and voluntary arrangements through to compelled recovery and enforcement.",
        "Collection powers are grounded in the Income Tax Act [Chapter 23:06], the VAT Act [Chapter 23:12], and enforcement frameworks introduced or strengthened by the Finance Act 2025.",
        "This lesson covers the debt collection continuum from reminder notices to enforcement; segmented collection strategies based on risk and taxpayer profile; and how ZIMRA prioritises its collection portfolio.",
    ),
    "debtpaymentplans.html": (
        "Where taxpayers face genuine financial difficulty and cannot discharge their full tax obligations immediately, ZIMRA may approve structured payment arrangements as an alternative to compelled enforcement.",
        "Instalment agreements and deferred payment are authorised under provisions of the Income Tax Act [Chapter 23:06] and ZIMRA's administrative guidelines, with conditions set by the Commissioner.",
        "This lesson covers the application process for payment plans, the terms and conditions imposed, monitoring and compliance obligations, default consequences, and the strategic use of instalment arrangements by taxpayers.",
    ),
    "debtenforcement.html": (
        "When voluntary collection methods fail, ZIMRA has broad statutory powers to compel payment — including seizure of assets, restriction of business operations, and third-party collection orders.",
        "Enforcement powers are derived from the Income Tax Act [Chapter 23:06], the VAT Act [Chapter 23:12], and enhanced provisions introduced by the Finance Act 2025 and the Finance Bill 2026.",
        "This lesson covers ZIMRA's full spectrum of enforcement tools, the principles of proportionality and escalation, taxpayer rights during enforcement, and how to respond to enforcement notices.",
    ),
    "debtgarnishee.html": (
        "A garnishee order directs a third party — such as a bank, employer, or trade debtor — holding funds belonging to a taxpayer to pay those funds directly to ZIMRA in satisfaction of the debt.",
        "Third-party collection and garnishee procedures are governed by agent appointment provisions of the Income Tax Act [Chapter 23:06] and analogous VAT Act provisions for third-party liability.",
        "This lesson covers the mechanics of the garnishee process, the obligations and rights of the garnishee, priority among competing claimants, consequences of non-compliance, and how taxpayers can challenge improper garnishees.",
    ),
    "debtattachment.html": (
        "ZIMRA has the power to attach and sell a taxpayer's movable or immovable property to recover unpaid tax debt, making asset seizure one of the most coercive tools in its enforcement arsenal.",
        "The attachment and sale process is authorised by distress provisions in the Income Tax Act [Chapter 23:06], supplemented by relevant provisions of the Magistrates Court Act [Chapter 7:10] for enforcement of tax warrants.",
        "This lesson covers the attachment procedure from warrant to sale, categories of attachable property and exempt assets, the public auction process, the taxpayer's right of redemption, and ZIMRA's power to bid in.",
    ),
    "debtcivilrecovery.html": (
        "ZIMRA may institute civil proceedings to have a tax liability recognised as a civil judgment, enabling it to employ the full range of court-ordered enforcement and execution remedies.",
        "Civil recovery is authorised by the Income Tax Act [Chapter 23:06], the High Court Act [Chapter 7:06], and the Magistrates Court Act [Chapter 7:10], which together define the court-based collection framework.",
        "This lesson covers the process of issuing summons, obtaining and registering civil judgment, methods of judgment enforcement, the prescription and revival of tax debts, and the cost implications of civil proceedings.",
    ),
    "debtinsolvency.html": (
        "When a taxpayer is sequestrated or a company is wound up, the ranking of ZIMRA's claim among competing creditors critically determines how much of the outstanding tax debt is ultimately recovered.",
        "Tax debt priority in insolvency is governed by the Income Tax Act [Chapter 23:06], the Insolvency Act [Chapter 6:04], and the Companies and Other Business Entities Act (COBEA) [Chapter 24:31].",
        "This lesson covers ZIMRA's status as a preferred creditor, the ranking of different tax obligations in sequestration and liquidation, proofs of debt in insolvency proceedings, and post-insolvency obligations of the insolvent taxpayer.",
    ),
    "debtbusinessclosure.html": (
        "The closure or deregistration of a business does not extinguish outstanding tax obligations; ZIMRA may pursue directors, members, or shareholders personally for unpaid company tax debt.",
        "Director and officer liability for company tax obligations is grounded in provisions of the Income Tax Act [Chapter 23:06], the VAT Act [Chapter 23:12], and COBEA [Chapter 24:31].",
        "This lesson covers the personal liability of directors for company tax arrears, final tax compliance obligations on closure, the requirement for tax clearance before deregistration, and the implications of voluntary versus compulsory winding-up.",
    ),
    "debtdisputes.html": (
        "A taxpayer who disputes an assessment must carefully navigate the intersection of the objection and appeal process with ongoing debt collection, as debt does not automatically halt upon lodging a dispute.",
        "Dispute procedures are governed by the objection and appeal provisions of the Income Tax Act [Chapter 23:06], the Special Court for Income Tax Appeals rules, and suspension-of-collection provisions.",
        "This lesson covers the effect of an objection on enforcement; when collection may be suspended pending appeal; the risks of ignoring debt while disputing; penalties for frivolous objections; and strategy for managing the dispute-debt interface.",
    ),
    "debtwriteoffs.html": (
        "ZIMRA has authority to write off or remit tax debt that is demonstrably irrecoverable, uncollectable by any reasonable means, or where pursuit would cause disproportionate hardship relative to the amount recoverable.",
        "The Commissioner's remission and write-off powers are contained in the Income Tax Act [Chapter 23:06] and are governed by policy criteria published pursuant to the Finance Act 2025.",
        "This lesson covers the legal distinction between write-off and remission, the criteria for irrecoverability, the formal application procedure, conditionality attached to remission, and the circumstances under which written-off debt may be revived.",
    ),
    "debtengagement.html": (
        "Proactive taxpayer engagement — through education, outreach, and voluntary disclosure — is central to ZIMRA's modern approach to debt prevention and early-stage compliance management.",
        "ZIMRA's engagement mandate flows from the ZIMRA Act [Chapter 23:11] and voluntary disclosure provisions of the Income Tax Act [Chapter 23:06], supported by Finance Act 2025 incentives for early settlement.",
        "This lesson covers the voluntary disclosure programme, compliance improvement agreements, behavioural segmentation of taxpayers for tailored engagement, and the comparative cost-benefit of voluntary settlement versus enforcement.",
    ),
    "debttechnology.html": (
        "Digital systems and data-driven platforms have fundamentally transformed how ZIMRA identifies outstanding obligations, prioritises collection action, and communicates with taxpayers at scale.",
        "ZIMRA's technology framework is grounded in its TARMS operational architecture and electronic communications provisions introduced by the Finance Act 2025 and related statutory instruments.",
        "This lesson covers TARMS's debt management module, automated risk profiling and scoring, electronic notices and correspondence, online payment portals, and the use of data analytics in prioritising debt collection.",
    ),
    "debtspecialsituations.html": (
        "Certain categories of taxpayers — including non-residents, mining entities, deceased estates, and corporate groups — require specialised debt management approaches beyond standard collection procedures.",
        "Special taxpayer provisions are distributed across the Income Tax Act [Chapter 23:06], the Finance Act 2025, applicable double taxation agreements, and the Deceased Estates Succession Act.",
        "This lesson covers debt recovery from deceased estates, non-resident debt collection and treaty-based assistance, group company obligations and set-off, cross-border enforcement mechanisms, and intra-group tax debt allocation.",
    ),
    "debtethics.html": (
        "Tax practitioners and ZIMRA officers involved in debt management must uphold rigorous ethical and professional standards, balancing the imperative to collect revenue with the obligation to respect taxpayer rights.",
        "Professional conduct obligations arise from the ZIMRA Act [Chapter 23:11], the registered tax practitioners framework, professional body codes of ethics, and Zimbabwe's anti-corruption and public integrity legislation.",
        "This lesson covers the duty of confidentiality in debt proceedings, prohibition on inducements and conflicts of interest, the proper and proportionate use of enforcement powers, taxpayer rights during collection, and whistleblowing protections.",
    ),
    "debtcasestudies.html": (
        "Practical case studies illustrate how debt management principles are applied across diverse real-world taxpayer situations, bridging the gap between statutory knowledge and professional practice in Zimbabwe.",
        "Each case study draws on the Income Tax Act [Chapter 23:06], VAT Act [Chapter 23:12], and Finance Act 2025 as applied in illustrated scenarios involving individuals, SMEs, corporates, and special-category taxpayers.",
        "This lesson applies collection strategy selection, enforcement escalation decisions, payment plan negotiations, and the management of the dispute-debt interface through worked examples drawn from common Zimbabwean practice.",
    ),
    "debttoolkit.html": (
        "This practitioner toolkit provides structured reference materials, templates, checklists, and worked guides for managing tax debt engagements efficiently and in compliance with Zimbabwean law.",
        "All toolkit resources are anchored to provisions of the Income Tax Act [Chapter 23:06], VAT Act [Chapter 23:12], Finance Act 2025, and ZIMRA administrative guidance.",
        "The toolkit includes debt management workflow templates, objection and appeal checklists, instalment application guides, enforcement response strategies, ethical compliance reminders, and quick-reference calculation aids.",
    ),
    "debtmanagementadministration.html": (
        "ZIMRA's internal administrative framework determines how debt management functions are organised, authorised, escalated, and measured across regional offices and national headquarters.",
        "Administrative governance is grounded in the ZIMRA Act [Chapter 23:11] and delegated authority provisions of the Income Tax Act [Chapter 23:06], which empower officers at various levels to perform collection functions.",
        "This lesson covers ZIMRA's organisational structure for debt management, delegation of collection authority, case escalation procedures for large or complex debts, performance metrics, and internal governance of the debt function.",
    ),
    "debtpaye.html": (
        "PAYE debt arises when employers fail to remit withheld employee income tax to ZIMRA, creating a high-priority category of tax debt given that the funds are held in trust on behalf of employees.",
        "Employer PAYE obligations and the deemed trust nature of withheld amounts are established by the Income Tax Act [Chapter 23:06], Section 72 agent provisions, and PAYE regulations under the Finance Act 2025.",
        "This lesson covers the employer's role as collecting agent, the trust character of withheld PAYE, personal director liability for PAYE arrears, ZIMRA's priority enforcement approach, and compliance strategies for employers managing PAYE obligations.",
    ),
}


# ── HTML builder ──────────────────────────────────────────────────────────────
def build_feature_steps_html(ctx: str, leg: str, con: str) -> str:
    return f"""<section class="feature-steps-container" id="lesson-overview-steps">
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


def inject_css_js(soup, changes):
    """Add feature-steps.css and feature-steps.js + initialiser to the page."""
    # ── CSS ──────────────────────────────────────────────────────────────────
    if not soup.find("link", href=FEATURE_CSS):
        anchor_css = soup.find("link", href=GLOBE_CSS)
        if anchor_css:
            new_link = soup.new_tag("link", href=FEATURE_CSS, rel="stylesheet")
            anchor_css.insert_after(new_link)
            changes.append("added feature-steps.css")
        else:
            changes.append("WARN: globe-hero.css not found — feature-steps.css not added")

    # ── JS ───────────────────────────────────────────────────────────────────
    if not soup.find("script", src=FEATURE_JS):
        anchor_js = soup.find("script", src=GLOBE_JS)
        if anchor_js:
            init_tag = soup.new_tag("script")
            init_tag.string = INIT_SCRIPT
            fs_tag = soup.new_tag("script", src=FEATURE_JS)
            anchor_js.insert_after(init_tag)
            anchor_js.insert_after(fs_tag)
            changes.append("added feature-steps.js + initialiser")
        else:
            changes.append("WARN: globe-hero.js not found — feature-steps.js not added")


def process(filepath, ctx, leg, con):
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    soup = BeautifulSoup(raw, "html.parser")
    changes = []

    # Skip if already processed
    if soup.find(class_="feature-steps-container"):
        changes.append("skipped — feature-steps-container already present")
        return changes

    steps_html = build_feature_steps_html(ctx, leg, con)
    steps_tag = BeautifulSoup(steps_html, "html.parser")

    # ── Detect layout type ───────────────────────────────────────────────────
    globe = soup.find(class_="globe-hero")

    if globe:
        # LEGACY: inner-box → globe-hero → lower-content
        inner = soup.find(class_="inner-box")
        lower = inner.find(class_="lower-content") if inner else None
        globe.decompose()
        changes.append("removed globe-hero")
        if lower:
            lower.insert_before(steps_tag)
            changes.append("inserted feature-steps-container before lower-content")
        elif inner:
            inner.insert(0, steps_tag)
            changes.append("inserted feature-steps-container at top of inner-box")
        else:
            changes.append("WARN: no inner-box found for legacy file")
    else:
        # NEW-STYLE: lesson-container → lesson-page-header → section.lesson-section
        container = soup.find(class_="lesson-container")
        if container:
            header = container.find(class_="lesson-page-header")
            if header:
                header.insert_after(steps_tag)
                changes.append("inserted feature-steps-container after lesson-page-header")
            else:
                changes.append("WARN: lesson-page-header not found")
        else:
            changes.append("WARN: no lesson-container found")

    # ── CSS / JS ─────────────────────────────────────────────────────────────
    inject_css_js(soup, changes)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

    return changes


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    all_ok = True
    for fname, (ctx, leg, con) in LESSON_STEPS.items():
        path = os.path.join(FOLDER, fname)
        if not os.path.exists(path):
            print(f"  MISSING  {fname}")
            all_ok = False
            continue
        result = process(path, ctx, leg, con)
        has_warn = any(r.startswith("WARN") for r in result)
        status = "WARN" if has_warn else "  OK "
        print(f"  {status}  {fname}")
        for r in result:
            print(f"         {r}")
    print("=" * 60)
    if all_ok:
        print("All debt lesson pages updated successfully.")
