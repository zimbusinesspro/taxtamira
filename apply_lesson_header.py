"""
apply_lesson_header.py
======================
Replaces the old two-part lesson heading (pink .service-title-box + plain
feature-steps-title h2) with a single amber .lesson-page-header block on
every lesson HTML page.

Strategy per file type
----------------------
A) Both service-title-box AND feature-steps-title h2 present (30 files)
   - lesson number  : grey <span> inside feature-steps-title h2
   - lesson name    : service-title-box <h2> text  (more descriptive)
   - excerpt        : service-title-box <p> text   (may be empty)
   - Action: remove service-title-box, replace feature-steps-title h2
             with new .lesson-page-header

B) service-title-box only (no feature-steps-title h2) (56 files)
   - lesson name    : service-title-box <h2> text
   - excerpt        : service-title-box <p> text   (may be empty)
   - lesson number  : derived from hero-label or left blank
   - Action: replace service-title-box in-place with .lesson-page-header

C) feature-steps-title only (no service-title-box) (1 file)
   - lesson number  : grey <span> inside h2
   - lesson name    : h2 main text
   - excerpt        : empty
   - Action: replace feature-steps-title h2 with .lesson-page-header

D) lesson-section based (debt module files, no box/steps)
   - lesson number  : parsed from first h2 (e.g. "Lesson Three:", "Lesson 13:")
   - lesson name    : remainder of that h2 after colon
   - excerpt        : first prose paragraph from first non-empty section
   - Action: insert lesson-page-header at top of .inner-box, optionally
             remove the now-redundant empty title section

Skip list (non-lesson pages)
"""

import os, glob, re
from bs4 import BeautifulSoup, NavigableString, Tag

FOLDER = r"C:/Users/Uncle Taps/Desktop/CGT LEFT HTML"

# Pages that are menus, landing pages or templates — skip completely
SKIP_FILENAMES = {
    "index.html",
    "about.html",
    "contact.html",
    "taxnews.html",
    "taxinsights.html",
    "itcmenu.html",
    "vatmenu.html",
    "cgtmenu.html",
    "debtmenu.html",
    "lessonstemplate.html",
    "vatlessonstemplate.html",
}


def clean_text(tag):
    """Return plain text from a tag, collapsing whitespace."""
    if tag is None:
        return ""
    return re.sub(r"\s+", " ", tag.get_text(separator=" ", strip=True))


def build_header_html(lesson_number, lesson_name, excerpt):
    """Return the HTML string for the new .lesson-page-header block."""
    num_html  = f'\n    <span class="lesson-number">{lesson_number}</span>' if lesson_number else ""
    name_html = f'\n    <span class="lesson-name">{lesson_name}</span>'
    exc_html  = f'\n    <span class="lesson-excerpt">{excerpt}</span>' if excerpt else ""
    return f'<div class="lesson-page-header">{num_html}{name_html}{exc_html}\n</div>'


ORDINAL_TO_NUM = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20",
}

# Pattern: "Lesson (Three|13|...) [Deep Research Report|Lesson Plan]:" or
#           "Lesson (Three|13|...) Title" (no colon)
_LESSON_RE = re.compile(
    r"^Lesson\s+(\w+)(?:\s+(?:Deep\s+Research\s+Report|Lesson\s+Plan))?[:\s]\s*(.*)",
    re.IGNORECASE,
)


def parse_debt_h2(text):
    """Return (lesson_number_str, lesson_name) from a debt-module h2 string."""
    m = _LESSON_RE.match(text.strip())
    if not m:
        return "", text.strip()
    raw_num, rest = m.group(1), m.group(2).strip()
    # normalise ordinals → digits
    num = ORDINAL_TO_NUM.get(raw_num.lower(), raw_num)
    lesson_number = "Debt Lesson {}".format(num)
    # rest might start with " - " leftover
    lesson_name = rest.lstrip(" -").strip()
    if not lesson_name:
        lesson_name = text.strip()
    return lesson_number, lesson_name


def get_debt_excerpt(inner_box):
    """Return first prose paragraph from the first non-empty lesson-section."""
    for section in inner_box.find_all("section", class_="lesson-section"):
        content = section.find("div", class_="section-content")
        if not content:
            continue
        txt = clean_text(content)
        if txt:
            # truncate to ~200 chars at a sentence boundary
            if len(txt) > 220:
                idx = txt.rfind(". ", 0, 220)
                txt = txt[:idx + 1] if idx > 60 else txt[:220] + "…"
            return txt
    return ""


def process_file(filepath):
    fname = os.path.basename(filepath)
    if fname in SKIP_FILENAMES:
        return "skipped"

    with open(filepath, encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    # Already converted
    if "lesson-page-header" in raw:
        return "already-done"

    has_box   = "service-title-box" in raw
    has_steps = "feature-steps-title" in raw

    soup = BeautifulSoup(raw, "html.parser")

    # ── Cases A / B / C  (service-title-box or feature-steps-title) ───────
    if has_box or has_steps:
        box        = soup.find("div", class_="service-title-box")
        steps_h2   = soup.find("h2",  class_="feature-steps-title")

        box_h2_tag = box.find("h2")  if box else None
        box_p_tag  = box.find("p")   if box else None
        grey_span  = steps_h2.find("span") if steps_h2 else None

        lesson_number = clean_text(grey_span).rstrip(" -").strip() if grey_span else ""
        lesson_name   = clean_text(box_h2_tag) if box_h2_tag else ""
        excerpt       = clean_text(box_p_tag)  if box_p_tag  else ""

        # steps-only: derive name from h2 main text
        if not lesson_name and steps_h2:
            full_text = clean_text(steps_h2)
            lesson_name = full_text.replace(lesson_number, "").strip(" -").strip()

        # box-only: try hero-label for lesson number
        if not lesson_number:
            hero_label = soup.find(class_="hero-label")
            if hero_label:
                lesson_number = clean_text(hero_label)

        if not lesson_name:
            return "skipped"

        new_header = BeautifulSoup(build_header_html(lesson_number, lesson_name, excerpt), "html.parser")
        header_tag = new_header.find("div", class_="lesson-page-header")

        if box:
            box.replace_with(header_tag)
        if steps_h2:
            if box:
                steps_h2.decompose()
            else:
                steps_h2.replace_with(header_tag)

    # ── Case D: lesson-section based (debt module without box/steps) ───────
    else:
        # Debt-module files use .lesson-container directly (no .inner-box wrapper)
        lc = (soup.find("div", class_="inner-box") or
              soup.find("div", class_="lesson-container"))
        if not lc:
            return "skipped"

        first_section = lc.find("section", class_="lesson-section")
        if not first_section:
            return "skipped"

        first_h2 = first_section.find("h2")
        if not first_h2:
            return "skipped"

        h2_text = clean_text(first_h2)

        # Skip if it looks like a generic section (Executive summary, etc.)
        if h2_text.lower().startswith("executive") or h2_text.lower().startswith("context"):
            # Try to find a real lesson title h2 anywhere on the page
            page_h1 = soup.find("h1")
            h2_text = clean_text(page_h1) if page_h1 else h2_text

        lesson_number, lesson_name = parse_debt_h2(h2_text)
        excerpt = get_debt_excerpt(lc)

        if not lesson_name:
            return "skipped"

        new_header = BeautifulSoup(build_header_html(lesson_number, lesson_name, excerpt), "html.parser")
        header_tag = new_header.find("div", class_="lesson-page-header")

        # Insert at the very top of the container (before all sections)
        lc.insert(0, header_tag)

        # If the first section was purely a title (empty content), remove it
        first_content = first_section.find("div", class_="section-content")
        if first_content and not first_content.get_text(strip=True):
            first_section.decompose()

    # ── Write out ──────────────────────────────────────────────────────────
    html_out = str(soup)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_out)
    return "updated"


# ── Main ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = {"updated": [], "already-done": [], "skipped": []}
    for path in sorted(glob.glob(os.path.join(FOLDER, "*.html"))):
        status = process_file(path)
        results[status].append(os.path.basename(path))

    print("=" * 60)
    print("UPDATED  ({})".format(len(results["updated"])))
    for f in results["updated"]:
        print("  +", f)
    print()
    print("ALREADY DONE  ({})".format(len(results["already-done"])))
    for f in results["already-done"]:
        print("  =", f)
    print()
    print("SKIPPED  ({})".format(len(results["skipped"])))
    for f in results["skipped"]:
        print("  -", f)
    print("=" * 60)
