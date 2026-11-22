"""Pack builder for the DRAWINGS IN US MILITARY FIELD MANUALS AND NAVY COURSES: the numbered figures of survival,
first-aid, map-reading, knots and rigging, field-sanitation, cold-weather and mountaineering manuals, and of the US
Navy's nonresident training courses (the NEETS electricity and electronics modules, Basic Machines, Culinary
Specialist, Hospital Corpsman), each with its own printed caption
("Figure 8-12. Square knot"). Line drawings of knots, shelters, compasses, map symbols, splints and bandages are
good teaching pictures for a describer, and their captions are the publisher's own words. Used by build_packs.py in
the same way as its own PACKS: build_field_manual_figures(limit) returns [(file name, JPEG bytes, row)], where a row
is {"question", "answer", "credit"}, plus "content": "medical" for first-aid and medical drawings. The limit counts
pictures.

WHERE THE MANUALS COME FROM. The manuals are works of the US government (17 U.S.C. 105: not subject to copyright).
The builder reads each PDF's front pages and judges it with the repository's release rule (military_release.py,
the owner's decision of 22 November 2026): a manual whose copy comes from the Internet Archive or a government or
museum site is used whether or not it prints Distribution Statement A, and each row's credit says truthfully which
(the statement when printed; otherwise "published openly by <the host>; its front pages print no distribution
statement"). A manual that prints a restricted marking (Distribution B to F, FOUO, CUI, NOFORN, export control) is
used only when the government itself publishes it openly at the address it was read from; this pack is published
openly and has no personal-use route, so an Internet Archive copy of such a manual is left out (its reason says
"personal use only, fetch it yourself"). A classified marking leaves it out unless it was declassified and released
(military_release.py says how that is shown). The official site
(armypubs.army.mil) shuts out automated readers in its robots.txt, and marines.mil, the Coast Guard's and FEMA's
sites refuse automated requests, so the copies on the Internet Archive are used (its robots.txt allows them); each
row names that copy. The same manuals are in the toolkit's offline library as text (textbooks/sources.py PDF_DOCS,
"Reference, field manuals").

HOW A FIGURE IS FOUND (pypdfium2, Apache/BSD, as us_modern_packs.form_pages uses): on each page, every caption line
"Figure 4-12. <title>" (not the list of figures, whose lines end in dot leaders and page numbers) is located; the
drawing is the drawn shapes and pictures on the page just above the caption, up to the caption above it, the
nearest line of body text (a text line wider than 45 percent of the page) or the top of the page (or, when there is
nothing above, just below it, down to the next caption or body text); the running heads and footers, the page's
thin rules and link underlines are not counted, and the cut stops at the caption, which is not in the picture. The page is drawn at 180 dots per inch and cut to that box. A
page that is one scanned picture (an old manual scanned whole) is left out: its drawing cannot be told from its text.

What is asked: "What does this picture show?" with "It is a figure from <manual>: figure 4-12, <caption>." (most are
line drawings, a few are photos or maps, so the answer says "figure", as the manual does). A figure
whose caption says too little (fewer than two words, or only "continued", "example" or a number) is set aside for a
description (build_packs.needs_description).

Safety (packs/SOURCE-RULES.md and the owner's rule for field manuals): only survival, first aid, map reading, knots
and rigging, hygiene, cold-weather and mountain safety are chosen; any figure whose caption names weapons, firing,
ammunition, explosives, mines, tactics, combat or harm (NOT_SAFE) is left out, and so is every figure of a chapter
about them (NOT_SAFE_PAGES: the pages of such a chapter in the manual's bookmarks). Drawings from the first-aid
manual and the survival-medicine chapter, and any whose caption names a wound, injury, fracture, bleeding, burn or
casualty, are marked "content": "medical" (used only with the kit's medical choice, never for picture-making).
Many drawings show soldiers at work, so the pack is not for picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS).
No sexual content can come from these manuals.

    python packs/field_manual_packs.py --limit 10      (prints a few rows: a quick check)
"""

import io
import json
import re
import sys

import build_packs  # noqa: F401 - loaded first, as the other pack modules do
import military_release
from build_packs import session, say, considered, needs_description, pass_random, listing_out_of_time

DRAWING_Q = "What does this picture show?"
PD_CREDIT = "a US government work, not subject to copyright (17 U.S.C. 105)"     # the release line follows it

# The manuals (Internet Archive item, title as said in an answer, publisher, medical: every drawing is medical).
# Checked by hand on 2026-11-18: each front page reads "DISTRIBUTION RESTRICTION: Approved for public release;
# distribution is unlimited." (the builder checks each PDF again with military_release.release_rule).
MANUALS = [
    ("survival-atp-3-50-21", "the US Army's survival manual (ATP 3-50.21, 2018)", False),
    ("FM4-25x11", "the US armed forces' first-aid manual (FM 4-25.11, 2002)", True),
    ("FM3-25x26", "the US Army's map reading and land navigation manual (FM 3-25.26, 2001)", False),
    ("FM4-25x12", "the US Army's field sanitation manual (FM 4-25.12, 2002)", False),
    ("fm-5-125-rigging-techniques-procedures-and-applications-1995",
     "the US Army's rigging manual (FM 5-125, 1995)", False),
    ("military-mountaineering-tc-3-97.61-november-2025", "the US Army's mountaineering manual (TC 3-97.61, 2025)",
     False),
    ("soldiers-handbook-for-individual-operations-and-survival-in-cold-weather-areas-tc-21-3",
     "the US Army's cold-weather handbook (TC 21-3, 1986)", False),
    # US Navy nonresident training courses (NAVEDTRA), the same Distribution Statement A.
    ("navedtra-14037-basic-machines-1994", "the US Navy's course Basic Machines (NAVEDTRA 14037, 1994)", False),
    ("navedtra-15008-culinary-specialist-2010", "the US Navy's course Culinary Specialist (NAVEDTRA 15008, 2010)",
     False),
    ("hospital-corpsman-nonresident-training-course-navedtra-14295",
     "the US Navy's course Hospital Corpsman (NAVEDTRA 14295, 2000)", True),
] + [(f"NEETSModule{n:02d}", f"the US Navy's electricity and electronics course NEETS module {n} ({words})", False)
     for n, words in ((1, "matter, energy and direct current"), (2, "alternating current and transformers"),
                      (3, "circuit protection, control and measurement"), (4, "conductors, wiring and schematics"),
                      (5, "generators and motors"), (6, "electron tubes and power supplies"),
                      (7, "solid-state devices"), (8, "amplifiers"), (9, "wave generation and shaping"),
                      (10, "wave propagation, transmission lines and antennas"), (13, "number systems and logic"),
                      (14, "microelectronics"), (16, "test equipment"), (19, "the technician's handbook"),
                      (22, "digital computers"), (24, "fiber optics"))]

# Added under the release rule of 22 November 2026 (military_release.py): Internet Archive copies that print no
# Distribution Statement A (read on 2026-11-22), so each row's credit says "its front pages print no distribution
# statement". A page that is one scanned picture gives no figures, as for every manual here. Kept apart for merges.
MANUALS_RELEASE_RULE = [
    ("fm-4-25-10-field-hygiene-and-sanitation-2004", "the US Army's field hygiene manual (FM 4-25.10, 2004)", False),
    ("MCRP_3-02F_FM_21-76_Survival", "the US Army and Marine Corps survival manual (FM 21-76, 1992)", False),
    ("Afr64-4352-481Survivalmanual", "the US Air Force's survival training manual (AFR 64-4, 1985)", False),
    ("milmanual-st-31-91b--us-army-special-forces-medical-handbook",
     "the US Army's Special Forces medical handbook (ST 31-91B, 1982)", True),
]
MANUALS += MANUALS_RELEASE_RULE

# The release markings, from the shared rule (military_release.py), kept under these names for the tests.
DISTRIBUTION_A = military_release.DISTRIBUTION_A
RESTRICTED = military_release.RESTRICTED
NOT_SAFE = re.compile(r"\b(weapons?|rifles?|pistols?|guns?|firing|fire\s+team|marksmanship|ammunition|rounds?\s+of|"
                      r"bayonets?|knife\s+fighting|explosives?|demolitions?|mines?|grenades?|booby|traps?\s+for\s+"
                      r"(people|enemy)|ambush\w*|tactic\w*|combat\s+operations?|enemy|sniper|kill\w*|evasion|"
                      r"interrogation|captiv\w*|corpses?|dead\s+bod\w*|nude|naked)\b", re.I)
MEDICAL = re.compile(r"\b(wounds?|injur\w*|fractur\w*|bleed\w*|tourniquet|splint\w*|bandag\w*|dressings?|burns?|"
                     r"casualt\w*|resuscitat\w*|airway|CPR|frostbite|hypothermia|blisters?|bites?|stings?|medic\w*|"
                     r"pulse|shock|skin|eye|eyes|teeth|tooth|anatomy|lungs?|heart)\b", re.I)
CAPTION = re.compile(r"^\s*Figure\s+([A-Z]?-?\d+(?:-\d+)?[a-z]?)(?:\.?\s*[\u2014\u2013]\s*|\.?\s+)(.{2,200}?)\s*$")
# A sentence that only mentions a figure ("Figure 1-15 shows you ...") is not its caption.
SENTENCE = re.compile(r"^(shows?|illustrates?|is|are|was|gives|lists|depicts|presents|contains|compares|and|or|in|on"
                      r"|of|as|for|to|with|from|at|by|above|below)\b", re.I)
LIST_LINE = re.compile(r"\.{4,}|\s\d+-\d+\s*$|\s[ivx]+\s*$")
TOO_LITTLE = re.compile(r"^\(?(continued|cont\.?|example|examples|sample|figure|\d+)\)?\.?$", re.I)
DPI = 180


def manual_pdf(identifier, s):
    """(PDF address, item page) of an Internet Archive item: its "Text PDF" (the one with words) first."""
    meta = s.get(f"https://archive.org/metadata/{identifier}", timeout=60).json()
    files = [f for f in meta.get("files", []) if f.get("name", "").lower().endswith(".pdf")]
    if not files:
        return "", ""
    files.sort(key=lambda f: (f.get("format") != "Text PDF", -int(f.get("size") or 0)))
    from urllib.parse import quote
    return (f"https://archive.org/download/{identifier}/{quote(files[0]['name'])}",
            f"https://archive.org/details/{identifier}")


def distribution_ok(doc, source="https://archive.org/", pages=12):
    """(reason, release line) for a manual's PDF: reason is "" when this open pack may use it, else why it is left
    out. The words of its first pages are judged by the shared release rule (military_release.release_rule) with
    the address its copy was read from (source). This pack has no personal-use route, so a "personal" verdict (a
    restricted marking on a copy the government does not publish itself) leaves it out too. The release line is
    the truthful line for the credit."""
    words = " ".join(" ".join(doc[n].get_textpage().get_text_range().split()) for n in range(min(pages, len(doc))))
    rule = military_release.release_rule(words, source)
    if rule.verdict != "public":
        return f"its front matter {rule.reason}", ""
    return "", rule.release


def unsafe_pages(doc):
    """The page indexes of chapters whose bookmark title names weapons, tactics or harm (NOT_SAFE)."""
    marks = []
    try:
        for item in doc.get_toc(max_depth=1):
            # pypdfium2 5 reads a bookmark with get_title() and get_dest().get_index(); version 4 had .title and
            # .page_index. Both are read, so a version change can never silently stop the weapons check.
            title = item.get_title() if hasattr(item, "get_title") else getattr(item, "title", "")
            if hasattr(item, "get_dest"):
                dest = item.get_dest()
                page = dest.get_index() if dest is not None else None
            else:
                page = getattr(item, "page_index", None)
            marks.append((title or "", page if page is not None else -1))
    except Exception:  # noqa: BLE001 - a manual without bookmarks
        return set()
    marks = sorted((p, t) for t, p in marks if p >= 0)
    out = set()
    for i, (start, title) in enumerate(marks):
        if NOT_SAFE.search(title):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(doc)
            out.update(range(start, end))
    return out


def captions(page):
    """[(label, caption, (left, bottom, right, top))] of the figure captions printed on a page (PDF points), or []
    for a list-of-figures page."""
    textpage = page.get_textpage()
    lines = textpage.get_text_range().replace("\r", "").split("\n")
    found = [CAPTION.match(line) for line in lines]
    found = [(m, line) for m, line in zip(found, lines) if m]
    if sum(1 for _, line in found if LIST_LINE.search(line)) >= 2:
        return []                                       # the list of figures
    out = []
    for m, line in found:
        if LIST_LINE.search(line) or SENTENCE.match(m.group(2)):
            continue
        caption = " ".join(m.group(2).split())
        searcher = textpage.search(f"Figure {m.group(1)}", match_case=True, match_whole_word=False)
        while True:                                  # the caption itself, not a sentence that mentions the figure
            hit = searcher.get_next()
            if not hit:
                break
            after = " ".join(textpage.get_text_range(hit[0], hit[1] + len(caption) + 8).split())
            if caption[:12] in after:
                out.append((m.group(1), caption, textpage.get_charbox(hit[0])))
                break
    return out


def graphic_boxes(page):
    """The boxes (left, bottom, right, top) of the drawn shapes and pictures on a page, without its running heads
    and footers (the top and bottom 7 percent) and its thin full-width rules; None when the page is one scanned
    picture."""
    import pypdfium2.raw as pdfium_c
    width, height = page.get_size()
    boxes = []
    for obj in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_PATH, pdfium_c.FPDF_PAGEOBJ_IMAGE], max_depth=3):
        try:
            left, bottom, right, top = obj.get_bounds() if hasattr(obj, "get_bounds") else obj.get_pos()
        except Exception:  # noqa: BLE001 - an object without a position
            continue
        if obj.type == pdfium_c.FPDF_PAGEOBJ_IMAGE and (right - left) * (top - bottom) > 0.8 * width * height:
            return None
        if top > height * 0.93 or bottom < height * 0.07:
            continue
        if obj.type == pdfium_c.FPDF_PAGEOBJ_PATH and top - bottom < 1.5:
            continue                                    # rules and link underlines
        boxes.append((left, bottom, right, top))
    return boxes


def text_lines(page):
    """The boxes (left, bottom, right, top) of the body-text lines of a page: text runs wider than 45 percent of the
    page (a drawing's labels are narrower)."""
    width = page.get_size()[0]
    textpage = page.get_textpage()
    out = []
    for i in range(textpage.count_rects()):
        left, bottom, right, top = textpage.get_rect(i)
        if right - left > width * 0.45:
            out.append((left, bottom, right, top))
    return out


def figure_box(cap_box, boxes, above_limit, below_limit, lines=()):
    """The box of the drawing that belongs to a caption: the shapes between the caption and above_limit (the caption
    above it, or the top of the page), stopping at the nearest body-text line (lines); when there are none, those
    between the caption and below_limit. The box never reaches into the caption. None when the caption has no
    drawing."""
    top_of_caption, bottom_of_caption = cap_box[3], cap_box[1]
    text_above = [ln[1] for ln in lines if ln[1] > top_of_caption + 1 and ln[1] < above_limit]
    upper = min([above_limit] + text_above)
    above = [b for b in boxes if b[1] >= top_of_caption - 2 and b[3] <= upper + 1]
    if above:
        box = (min(b[0] for b in above), min(b[1] for b in above), max(b[2] for b in above), max(b[3] for b in above))
        return (box[0], max(box[1], top_of_caption + 1), box[2], box[3])
    text_below = [ln[3] for ln in lines if ln[3] < bottom_of_caption - 1 and ln[3] > below_limit]
    lower = max([below_limit] + text_below)
    below = [b for b in boxes if b[3] <= bottom_of_caption + 2 and b[1] >= lower - 1]
    if not below:
        return None
    box = (min(b[0] for b in below), min(b[1] for b in below), max(b[2] for b in below), max(b[3] for b in below))
    return (box[0], box[1], box[2], min(box[3], bottom_of_caption - 1))


def crop(page, box):
    """JPEG bytes of the drawing in box (PDF points), drawn at DPI, with a small margin at the sides and top (none at
    the bottom, where the caption is); None when it is too small."""
    width, height = page.get_size()
    scale = DPI / 72
    left, bottom, right, top = box
    pad = 6
    image = page.render(scale=scale).to_pil().convert("RGB")
    px = (max(0, (left - pad) * scale), max(0, (height - top - pad) * scale),
          min(image.width, (right + pad) * scale), min(image.height, (height - bottom) * scale))
    if px[2] - px[0] < 120 or px[3] - px[1] < 120:
        return None
    out = io.BytesIO()
    image.crop(tuple(int(v) for v in px)).save(out, "JPEG", quality=90)
    return out.getvalue()


def manual_figures(data, identifier, manual, medical, pdf_url, page_url):
    """[(file name, JPEG bytes, row)] of the figures of one manual's PDF bytes (see the module docstring); figures
    with too little caption are set aside (needs_description)."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(data)
    why, release = distribution_ok(doc, pdf_url)
    if why:
        considered(identifier, pdf_url, why)
        return []
    skip = unsafe_pages(doc)
    who = ("the US Navy" if "Navy" in manual else "Headquarters, US Air Force" if "Air Force" in manual
           else "Headquarters, Department of the Army")
    credit = f"Figure from {manual}, {who}; {PD_CREDIT}; {release.rstrip(".")}; copy at {page_url}"
    base = re.sub(r"[^a-z0-9]+", "_", identifier.lower()).strip("_")[:40]
    out, seen = [], set()
    for n in range(len(doc)):
        page = doc[n]
        found = captions(page)
        if not found:
            continue
        boxes = graphic_boxes(page)
        lines = text_lines(page)
        width, height = page.get_size()
        for i, (label, caption, box) in enumerate(sorted(found, key=lambda c: -c[2][3])):
            name = f"{base}_fig_{re.sub(r'[^A-Za-z0-9]+', '-', label)}.jpg"
            if name in seen:
                continue
            seen.add(name)
            if n in skip or NOT_SAFE.search(caption):
                considered(name, pdf_url, "the figure is about weapons, tactics or harm")
                continue
            if boxes is None:
                considered(name, pdf_url, "a scanned page: the drawing cannot be told from the text")
                continue
            ordered = sorted(found, key=lambda c: -c[2][3])
            above_limit = ordered[i - 1][2][1] if i else height * 0.93
            below_limit = ordered[i + 1][2][3] if i + 1 < len(ordered) else height * 0.07
            where = figure_box(box, boxes, above_limit, below_limit, lines)
            jpeg = crop(page, where) if where else None
            if not jpeg:
                considered(name, pdf_url, "no drawing was found next to the caption")
                continue
            words = caption.rstrip(".")
            is_medical = medical or bool(MEDICAL.search(words))
            row = {"question": DRAWING_Q, "credit": credit}
            if is_medical:
                row["content"] = "medical"
            if len(words.split()) < 2 or TOO_LITTLE.match(words):
                needs_description(name, pdf_url, credit, "Public domain (US government work)", "open", text=words,
                                  title=f"Figure {label}", reason="its caption is too short to describe the drawing",
                                  extra={"content": "medical"} if is_medical else None, page_url=page_url, data=jpeg)
                considered(name, pdf_url, "its caption is too short (set aside for a description)")
                continue
            words = words[0].upper() + words[1:]
            row["answer"] = f"It is a figure from {manual}: figure {label}, {words}."
            considered(name, pdf_url, "")
            out.append((name, jpeg, row))
    return out


def build_field_manual_figures(limit):
    """The figures of the MANUALS (see the module docstring), the manuals in a shuffled order, at most limit."""
    s, out = session(), []
    manuals = list(MANUALS)
    pass_random(76).shuffle(manuals)
    for identifier, manual, medical in manuals:
        if len(out) >= limit or listing_out_of_time():
            break
        # The session tries a dropped connection again (build_packs.session, also on the file server archive.org
        # redirects to); a manual that still cannot be read is left out, so it never fails the whole pack.
        try:
            pdf_url, page_url = manual_pdf(identifier, s)
        except Exception as e:  # noqa: BLE001 - the item's details could not be read: this manual is left out
            considered(identifier, f"https://archive.org/details/{identifier}",
                       f"its Internet Archive details could not be read ({type(e).__name__})")
            continue
        if not pdf_url:
            considered(identifier, page_url, "the Internet Archive item has no PDF")
            continue
        try:
            r = s.get(pdf_url, timeout=600)
        except Exception as e:  # noqa: BLE001 - tried again by the session already: this manual is left out
            say(f"  {manual}: could not be downloaded ({type(e).__name__})")
            considered(identifier, pdf_url, f"could not be downloaded ({type(e).__name__}, after several tries)")
            continue
        if r.status_code != 200:
            considered(identifier, pdf_url, f"could not be downloaded (the server answered {r.status_code})")
            continue
        got = manual_figures(r.content, identifier, manual, medical, pdf_url, page_url)
        say(f"  {manual}: {len(got)} figures")
        out += got
    return out[:limit]


FIELD_MANUAL_PACKS = {
    "field_manual_figures": (build_field_manual_figures,
                             "Drawings from US military field manuals and Navy training courses published openly "
                             "(Distribution Statement A, or openly published by a government site or the Internet "
                             "Archive; each credit says which): survival, first aid, map reading, rigging, "
                             "field sanitation, cold weather, mountaineering, electricity and electronics, machines, "
                             "cooking and hospital care; US government works, public domain (17 U.S.C. 105). "
                             "Copies from the Internet Archive, https://archive.org"),
}
FIELD_MANUAL_LIMITS = {"field_manual_figures": 2500}     # about 700 in the Army manuals, 1,500 or more in the Navy courses


def main(argv=None):
    """Run the builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try the field-manual figures pack builder.")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    entries = build_field_manual_figures(args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} figures, {sum(1 for _, _, r in entries if r.get('content') == 'medical')} medical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
