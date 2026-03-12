#!/usr/bin/env python3
"""
readability_enhancer.py
=======================
TaxTami Lesson Readability Enhancer
------------------------------------
Scans every lesson HTML file in the project and injects two types of
inline highlight spans into lesson-body text:

  <span class="leg-ref">…</span>
      ─ All legislative references:
        • Section / s numbers with sub-sections  (Section 8(1)(a), s.8(1))
        • Act names                               (Income Tax Act [Chapter 23:06])
        • Schedule references                     (Thirteenth Schedule, Schedule 4)
        • Statutory Instruments                   (SI 12/2019)
        • Finance Acts / Finance Bills

  <span class="key-term">…</span>
      ─ Core Zimbabwean tax concepts / defined terms:
        gross income, taxable supply, assessed loss, PAYE, ZIMRA, etc.

Safety rules
────────────
• Skips content inside: <script>, <style>, <code>, <pre>, <a>, <h1>–<h6>
  header/nav/footer, <select>, <button>, <input>, <title>
• Never re-processes a file that already contains class="leg-ref"
  (idempotent — safe to run multiple times)
• Only writes a file back when changes were actually made
• Processes ONLY files that contain lesson content markers
  (.section-content / .lesson-section / .lesson-details)

Usage
─────
  python readability_enhancer.py            # process all lesson files
  python readability_enhancer.py --test     # dry-run (no writes)
  python readability_enhancer.py itcgrossincome.html   # single file

Requires: beautifulsoup4  (pip install beautifulsoup4)
"""

import os
import re
import sys
import glob
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — project directory
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "CGT LEFT HTML")

# HTML files that are NOT lesson pages (menus, landing pages, templates, etc.)
SKIP_FILENAMES = {
    "index.html", "about.html", "contact.html", "taxtami.html",
    "itcmenu.html", "vatmenu.html", "cgtmenu.html", "debtmenu.html",
    "dtmenu.html", "taxnews.html", "taxinsights.html",
    "legislationbank.html", "lessonstemplate.html",
    "itclessonstemplate.html", "vatlessonstemplate.html",
    "2022_notes_memory_bank.html",
    "digital-services-tax-2026.html",
    "vat-rate-change-2026.html",
    "paye-reconciliation-2025.html",
    "default.php", "mail.php",
}

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN A — Legislative References  →  class="leg-ref"
# ═══════════════════════════════════════════════════════════════════════════════

_ACT_NAMES = [
    r"Income Tax Act(?:\s*\[Chapter\s+23:06\])?",
    r"Value Added Tax Act(?:\s*\[Chapter\s+23:12\])?",
    r"\bVAT Act(?:\s*\[Chapter\s+23:12\])?",
    r"Capital Gains Tax Act(?:\s*\[Chapter\s+23:01\])?",
    r"Public Debt Management Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Finance Act\s*(?:No\.\s*\d+\s+of\s+)?\d{4}",
    r"Finance Bill\s*\d{4}",
    r"Companies and Other Business Entities Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Companies Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Exchange Control Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Indigenisation and Economic Empowerment Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Mines and Minerals Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Customs and Excise Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Stamp Duties Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Special Economic Zones Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Reserve Bank of Zimbabwe Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Labour Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"Pension and Provident Funds Act(?:\s*\[Chapter\s+\d+:\d+\])?",
    r"\[Chapter\s+\d+:\d+\]",
]

_SECTION_PATTERNS = [
    # "Section 8(1)(a)" / "Sections 8, 9 and 10" / "Section 8(1)(a) and (b)"
    (r"\b[Ss]ections?\s+"
     r"\d+[A-Z]?(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*"
     r"(?:\s*(?:and|,|to)\s+\d+[A-Z]?(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*)*"),

    # "subsection (1)" / "subsection (1)(a)"
    (r"\b[Ss]ubsections?\s+\(\s*[0-9a-zA-Z]+\s*\)"
     r"(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*"),

    # "paragraph (a)" / "paragraph (a)(i)"
    (r"\b[Pp]aragraphs?\s+\([a-zA-Z0-9]+\)"
     r"(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*"),

    # "First Schedule" / "Thirteenth Schedule" / "Schedule 4" / "13th Schedule"
    (r"\b(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|"
     r"Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth)\s+Schedule\b"),
    r"\b[Ss]chedule\s+\d{1,2}[A-Z]?\b",
    r"\b\d{1,2}(?:st|nd|rd|th)\s+[Ss]chedule\b",

    # "Regulation 3(1)"
    r"\b[Rr]egulations?\s+\d+[A-Z]?(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*",

    # "SI 12/2019" / "Statutory Instrument 12 of 2019"
    r"\bSI\s+\d+\s*/\s*\d{2,4}\b",
    r"\bStatutory Instrument\s+(?:No\.)?\s*\d+\s+of\s+\d{4}\b",

    # "s.8(1)" — short section notation
    r"\bs\s*\.\s*\d+[A-Z]?(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*",
]

_ALL_LEG = _ACT_NAMES + _SECTION_PATTERNS
LEG_PATTERN = re.compile("(" + "|".join(_ALL_LEG) + ")")

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN B — Key Tax Concepts / Defined Terms  →  class="key-term"
# ═══════════════════════════════════════════════════════════════════════════════

_KEY_TERMS_RAW = [
    # Core income tax
    "gross income", "taxable income", "chargeable income",
    "assessed loss", "assessed deficit",
    "source of income", "Zimbabwe source", "deemed source",
    "year of assessment", "tax year", "tax period",
    "resident", "non-resident", "ordinarily resident",

    # Capital / revenue distinction
    "capital gain", "capital loss", "capital gains tax",
    "capital receipt", "revenue receipt",
    "capital expenditure", "revenue expenditure",
    "capital asset", "fixed capital", "floating capital",
    "trading stock",

    # Deductions
    "general deduction", "specific deduction",
    "capital allowance", "capital allowances",
    "wear and tear", "wear-and-tear",
    "special initial allowance",
    "commercial building allowance",
    "recoupment", "scrapping allowance",
    "assessed loss", "ring-fencing",
    "deductible expenditure", "non-deductible",
    "bad debts", "bad debt", "doubtful debt", "doubtful debts",

    # Employment / PAYE
    "pay as you earn", "PAYE",
    "fringe benefit", "fringe benefits",
    "employment income", "emoluments",
    "deemed remuneration",
    "employer", "employee",

    # Withholding taxes
    "withholding tax", "final withholding tax",
    "withholding agent",
    "non-residents tax on interest",
    "non-residents tax on fees",
    "non-residents tax on royalties",

    # VAT terms
    "taxable supply", "taxable supplies",
    "exempt supply", "exempt supplies",
    "zero-rated supply", "zero-rated supplies",
    "zero-rated",
    "input tax credit", "input tax",
    "output tax",
    "registered operator",
    "tax invoice", "fiscal tax invoice",
    "credit note", "debit note",
    "time of supply", "value of supply",
    "deemed supply",
    "open market value",
    "consideration",

    # CGT terms
    "specified asset", "specified assets",
    "marketable security", "marketable securities",
    "real property",
    "disposal",
    "notional vendor",
    "rollover relief", "rollover",
    "deferral",
    "principal private residence",
    "suspensive sale",
    "deemed sale",

    # Anti-avoidance / compliance
    "tax avoidance", "tax evasion", "tax planning",
    "anti-avoidance",
    "substance over form",
    "general anti-avoidance",
    "arm's length", "arm's length principle",
    "related party", "connected person", "associated enterprise",
    "transfer pricing",
    "beneficial owner", "beneficial ownership",
    "permanent establishment",

    # Administration
    "ZIMRA", "Zimbabwe Revenue Authority",
    "self-assessment",
    "presumptive tax",
    "tax clearance certificate", "tax clearance",
    "objection", "appeal",
    "default assessment", "estimated assessment",
    "representative taxpayer",
    "penalty", "additional tax", "interest",
    "garnishee order", "civil execution",

    # Exempt income
    "exempt income", "exempt from income tax",
    "dividend", "dividends",
    "interest income",
]

# Sort longest-first to prevent partial-match shadowing
_KEY_TERMS_SORTED = sorted(set(_KEY_TERMS_RAW), key=len, reverse=True)

TERM_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in _KEY_TERMS_SORTED) + r")\b",
    re.IGNORECASE,
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAGS TO SKIP during text-node processing
# ═══════════════════════════════════════════════════════════════════════════════

# Never descend into these tags' text content
SKIP_ANCESTOR_TAGS = {
    "script", "style", "code", "pre", "head", "title",
    "a", "button", "select", "option", "input", "textarea",
    "header", "nav", "footer",
    "h1", "h2", "h3", "h4", "h5", "h6",
}

# Span classes that mean the text is already highlighted — do not re-process
PROTECTED_SPAN_CLASSES = {
    "leg-ref", "key-term",
    "case-name", "case-citation",
    "section-letter",
    "pitfall-title",
}


# ═══════════════════════════════════════════════════════════════════════════════
# CORE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _should_skip(text_node: NavigableString) -> bool:
    """Return True if this text node must not be processed."""
    if not isinstance(text_node, NavigableString):
        return True
    if isinstance(text_node, Comment):
        return True
    if not str(text_node).strip():
        return True

    # Walk up the DOM tree checking ancestors
    parent = text_node.parent
    while parent and isinstance(parent, Tag):
        tag_name = parent.name
        if tag_name in SKIP_ANCESTOR_TAGS:
            return True
        if tag_name == "span":
            classes = set(parent.get("class") or [])
            if classes & PROTECTED_SPAN_CLASSES:
                return True
        parent = parent.parent
    return False


def _apply_pattern(soup: BeautifulSoup,
                   text_node: NavigableString,
                   pattern: re.Pattern,
                   css_class: str) -> bool:
    """
    Scan *text_node* for *pattern* matches.
    Replace each match with <span class="css_class">matched text</span>.
    Plain text segments between / around matches become new NavigableStrings.
    Returns True if the node was modified.
    """
    raw = str(text_node)
    matches = list(pattern.finditer(raw))
    if not matches:
        return False

    # Build replacement fragments
    fragments = []
    last_end = 0
    for m in matches:
        start, end = m.start(), m.end()
        if start > last_end:
            fragments.append(NavigableString(raw[last_end:start]))
        span = soup.new_tag("span", **{"class": css_class})
        span.string = m.group(0)
        fragments.append(span)
        last_end = end
    if last_end < len(raw):
        fragments.append(NavigableString(raw[last_end:]))

    # Insert fragments immediately after text_node, then remove it.
    # Inserting in REVERSE order keeps correct document order because each
    # new node is placed directly after text_node (before the previously
    # inserted nodes).
    for frag in reversed(fragments):
        text_node.insert_after(frag)
    text_node.extract()
    return True


def _process_area(soup: BeautifulSoup, area: Tag) -> None:
    """
    Two-pass processing on a single lesson content area:
      Pass 1 — legislative references  (more specific; do first)
      Pass 2 — key tax terms           (skip anything already inside a span)
    """
    # ── Pass 1: legislative references ──────────────────────────────────────
    for tn in list(area.find_all(string=True)):
        if _should_skip(tn):
            continue
        _apply_pattern(soup, tn, LEG_PATTERN, "leg-ref")

    # ── Pass 2: key terms ────────────────────────────────────────────────────
    # After pass-1, new NavigableStrings exist inside <span class="leg-ref">.
    # _should_skip() will block those from being re-processed here.
    for tn in list(area.find_all(string=True)):
        if _should_skip(tn):
            continue
        _apply_pattern(soup, tn, TERM_PATTERN, "key-term")


# ═══════════════════════════════════════════════════════════════════════════════
# FILE PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

LESSON_MARKERS = ("section-content", "lesson-section", "lesson-details")


def process_file(filepath, dry_run=False):
    """
    Process one HTML file.
    Returns the filename if changes were made (or would be), else None.
    """
    fname = os.path.basename(filepath)

    if fname in SKIP_FILENAMES:
        return None

    # Read
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
            raw_html = fh.read()
    except OSError as exc:
        print(f"  ✗ Cannot read {fname}: {exc}")
        return None

    # Quick content check — does the file have lesson content?
    if not any(marker in raw_html for marker in LESSON_MARKERS):
        return None

    # Idempotency check — skip if already processed
    if 'class="leg-ref"' in raw_html or "class='leg-ref'" in raw_html:
        print(f"  ↷ Already processed, skipping: {fname}")
        return None

    # Parse
    soup = BeautifulSoup(raw_html, "html.parser")

    # Find lesson content areas (all three layout types A / B / C)
    content_areas = (
        soup.select(".section-content")
        + soup.select(".lesson-section")
        + soup.select(".lesson-container")
    )
    if not content_areas:
        return None

    for area in content_areas:
        _process_area(soup, area)

    new_html = str(soup)

    # Only write if something actually changed
    if new_html == raw_html:
        return None

    if not dry_run:
        try:
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(new_html)
        except OSError as exc:
            print(f"  ✗ Cannot write {fname}: {exc}")
            return None

    return fname


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]
    dry_run = "--test" in args
    specific_files = [a for a in args if not a.startswith("--")]

    if dry_run:
        print("DRY-RUN MODE - files will NOT be modified.\n")

    if specific_files:
        # Single-file mode
        filepaths = [
            os.path.join(PROJECT_DIR, f) if not os.path.isabs(f) else f
            for f in specific_files
        ]
    else:
        # Process all HTML files in the project directory
        filepaths = sorted(
            glob.glob(os.path.join(PROJECT_DIR, "*.html"))
            + glob.glob(os.path.join(PROJECT_DIR, "*.php"))
        )

    print("Scanning {} files in: {}\n".format(len(filepaths), PROJECT_DIR))

    processed, skipped, errors = [], [], []

    for fp in filepaths:
        try:
            result = process_file(fp, dry_run=dry_run)
            if result:
                processed.append(result)
                action = "Would process" if dry_run else "[OK] Processed"
                print("  {}: {}".format(action, result))
            else:
                skipped.append(os.path.basename(fp))
        except Exception as exc:
            errors.append(os.path.basename(fp))
            print("  [ERR] {} : {}".format(os.path.basename(fp), exc))

    sep = "=" * 55
    print("\n{}".format(sep))
    print("  {}: {} files".format("Would process" if dry_run else "Processed", len(processed)))
    print("  Skipped (no change / already done / non-lesson): {} files".format(len(skipped)))
    if errors:
        print("  Errors: {} files - {}".format(len(errors), errors))
    print("{}\n".format(sep))


if __name__ == "__main__":
    main()
