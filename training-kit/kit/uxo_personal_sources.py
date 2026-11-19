"""PERSONAL-USE recognition collections: unexploded ordnance (UXO) and small arms, from military manuals that are
approved for public release. For the owner's own computer only; NOTHING HERE IS EVER PUBLISHED by the kit's makers
(no ready-made pack, no release asset, no add-on that is shared).

WHY. The owner is blind and is building a safety tool that helps people recognise suspected unexploded ordnance, so
that they stay away from it and report it (the kit already has the open landmine and munition picture packs:
amlid_landmines, commons_uxo, commons_munition_models in sources.py, and safety_rites_sources.py). A blind person
cannot see what a pictured object is, so the private, local describer should be able to say "this looks like a
mortar round: do not touch it; move back and report it", and, for a pictured firearm, what kind of gun it is. The
public military manuals hold the best plain identification drawings and safety rules for both. They are used here
for RECOGNITION and SAFETY only.

STRICT SCOPE (enforced in code, not only promised):
  1. PUBLIC RELEASE ONLY (release_check). A document is used only when its own front matter (first FRONT_PAGES
     pages) says "Approved for public release; distribution is unlimited" (Distribution Statement A), or, for a
     humanitarian body's document, shows the open licence named in its entry (basis "licence"). Any restricted
     marking (Distribution B to F, "distribution authorized to", FOUO, CUI, NOFORN, export-controlled) refuses it,
     even when Distribution A is also printed. Some Army PDFs print the statement in a font whose letters come out
     moved by 29 places (",675,%87,21" for "DISTRIBUTION"); the check also reads that form (unshifted), so the
     statement is checked, never assumed.
  2. RECOGNITION AND SAFETY SECTIONS ONLY (filter_pages). Each page's section titles are found from the PDF's
     bookmarks and from the headings printed on the page (chapter and appendix lines, and short capital-letter
     headings, carried on to the following pages until the next heading). A page is left out when any of its titles
     names something outside the scope:
       UXO: render-safe procedures, disposal or demolition techniques, destruction in place, disarming, defuzing,
            fuze functioning or arming in detail, charge calculations, priming and firing systems, manufacturing,
            modifying, arming or employing munitions, laying mines, booby-trap setting, breaching, EOD tools and
            techniques (UXO_DROP), and anything about making or modifying explosives or devices (COMMON_DROP).
       Small arms: marksmanship, firing and firing positions, aiming and aiming devices, zeroing, employment,
            engagements, tactics, stability and recoil control, drills and qualification, the cycle of function
            (feeding, chambering, locking, firing, unlocking, extracting, ejecting, cocking), operating instructions,
            loading and unloading, malfunctions and stoppages, disassembly and assembly, maintenance, cleaning,
            lubrication, inspection, troubleshooting and repair, parts lists and tools, armorer-level work,
            modifications and conversions of any kind (select-fire, barrels, suppressors, triggers), mountable
            equipment and accessories, ammunition, reloading and ballistics (SA_DROP), and COMMON_DROP. "Clearing"
            is kept only on a page that is part of the manual's own safety section (SA_CLEARING, SA_SAFETY).
     A page whose text uses procedure words many times (BODY_OPS, at least BODY_OPS_LEAST times) is left out too.
     Every title that caused pages to be left out is recorded, with its pages, in the folder's README.
  3. A UXO document whose pages are mostly left out (more than MOSTLY of its pages: mostly operational EOD
     procedure) is left out entirely; a small-arms manual is kept for its identification and safety pages only, and
     left out when fewer than SA_LEAST_PAGES pages remain.
  4. Pictures: figure crops with their printed captions, only from pages that were kept, only when the caption
     itself passes the same checks (and, for small arms, names an exterior view, a weapon type or its parts:
     SA_FIGURE_OK). UXO answers always end with UXO_LINE ("Do not touch it or go closer ..."), small-arms answers
     with GUN_LINE ("Treat every gun as loaded ...").

OUTPUT, on the owner's own computer:
  (a) The documents, in a local folder (personal_folder): "Documents\\Picture Model Training personal files\\UXO
      recognition" and "...\\Small arms recognition", each with README.txt ("PERSONAL USE; NOT FOR
      REDISTRIBUTION", every document with its release line and address, every section left out and why, every
      document refused and why). A document with no section left out is saved as the original PDF; a document with
      sections left out is saved as a copy holding only the kept pages ("... (recognition and safety pages
      only).pdf"), so nothing outside the scope is in the folder that the toolkit's "Your own documents" reads.
  (b) For the picture describer: a review workspace (<library>\\Review\\<key>, made by run_review.py like the other
      review collections) with the figure crops, each with a draft answer such as "This is a figure from ATP 4-32.2
      (approved for public release): figure 13, examples of general purpose bombs. Do not touch it or go closer.
      ..." Every picture arrives with the status "needs another look" (never "described" or "checked"); the owner
      (with a sighted helper where needed) checks each one (REVIEW_INSTRUCTIONS). Content "graphic", so it is used
      only with the graphic-scenes choice, and never for picture-making (sources.PICTURE_MAKING_NEVER);
      describing.json also says personal_only, never_publish and never_for_picture_making.

The figure method is the field-manual pack builder's (packs/field_manual_packs.py: captions, graphic_boxes,
text_lines, figure_box, crop), imported, not copied (figure_tools). It is there when the kit runs from a copy of the
repository (or when PICTURE_KIT_PACKS names the packs folder); without it, the documents are still saved and the
summary says that no figures could be cut. Scanned pages (one picture per page) give no figures, as in that builder.
The PDFs are read with pypdfium2 (Apache/BSD), as in that builder.

How to use (for the kit's own code):
  UXO_PERSONAL_SOURCES  a list of plain dicts like review_sources.REVIEW_SOURCES (key, name, category "research",
                        licence, terms, terms_summary, credit, content "graphic", cap, download, fetch,
                        review_only True) plus personal_only, never_publish and never_for_picture_making (all True).
                        fetch(folder, cap, say) fills the review workspace and the personal documents folder.
  UXO_DOCUMENTS, SMALL_ARMS_DOCUMENTS   the documents (checked by hand in November 2026; checked again in code).
  UXO_NOT_INCLUDED, SMALL_ARMS_NOT_INCLUDED, OWNER_DECISION   looked at and left out, with the reason.

    python uxo_personal_sources.py uxo <workspace folder> [cap]          (a quick run of one collection)
    python uxo_personal_sources.py check <PDF file> uxo|small_arms        (what the filters keep, offline)

Nothing is sent anywhere except the downloads from the Internet Archive (its documented metadata and download
addresses; its robots.txt allows them).
"""

import io
import os
import re
import shutil
import sys
import time

TOPICS = ("uxo", "small_arms")
FRONT_PAGES = 20          # the release statement must be on one of the first pages
MOSTLY = 0.5              # a UXO document with more than this share of its pages left out is left out entirely
SA_LEAST_PAGES = 3        # a small-arms manual with fewer kept pages than this is left out
BODY_OPS_LEAST = 3        # a page using procedure words at least this often is left out
FOLDER_ROOT = "Picture Model Training personal files"
FOLDER_NAMES = {"uxo": "UXO recognition", "small_arms": "Small arms recognition"}
README = "README.txt"
REVIEW_FILE = "REVIEW-INSTRUCTIONS.txt"
CREDITS_FILE = "CREDITS.txt"
USER_AGENT = "PictureModelTrainingKit/2 (https://github.com/mark-getbraille/toolkit-models)"
PERSONAL_LINE = "PERSONAL USE; NOT FOR REDISTRIBUTION."

UXO_LINE = ("Do not touch it or go closer. Move back carefully the way you came, warn others, and report it to the "
            "police, military or a mine-action organisation.")        # the same words as safety_rites_sources
GUN_LINE = "Treat every gun as loaded, and keep your fingers away from the trigger."
PD = "a US government work, not subject to copyright (17 U.S.C. 105)"
ARCHIVE = "https://archive.org"


def say_nothing(text):
    """The default say: nothing."""


# ----------------------------------------------------------------- 1. the release check

DISTRIBUTION_A = re.compile(r"approved\s*for\s*public\s*release\s*[;:,.]?\s*(and\s*)?distribution\s*(is\s*)?"
                            r"unlimited|distribution\s*(is\s*)?unlimited\s*[;:,.]?\s*approved\s*for\s*public\s*"
                            r"release|distribution\s+statement\s+a\s*[:.]\s*approved", re.I)
RESTRICTED = re.compile(r"distribution\s*(statement\s*)?[B-F]\s*[:.\-–—]|distribution\s+statement\s+[B-F]\b|"
                        r"distribution\s*authorized\s*to|authorized\s+to\s+U\.?\s?S\.?\s+Government\s+agencies|"
                        r"for\s*official\s*use\s*only|\bFOUO\b|controlled\s*unclassified|\bCUI\b|\bNOFORN\b|"
                        r"export[- ]?controlled|\bITAR\b|not\s+releasable\s+to", re.I)


def unshifted(text):
    """The text with every character moved 29 places on: some Army PDFs print the cover in a font whose letters come
    out 29 places early (",675,%87,21" is "DISTRIBUTION"). Only used for the release check."""
    return "".join(chr(ord(c) + 29) if 3 < ord(c) < 94 and c not in " \t\n\r" else c for c in text)


def release_check(front_text, basis="statement", licence=None):
    """(True, the line found) when the document's front matter shows it is publicly released, else (False, the
    reason). basis "statement": Distribution Statement A ("Approved for public release; distribution is
    unlimited"); basis "licence": licence (a regular expression for the open licence its publisher states). A
    restricted marking always refuses, in either form of the text."""
    text = " ".join((front_text or "").split())
    for form in (text, unshifted(text)):
        bad = RESTRICTED.search(form)
        if bad:
            return False, f"its front matter shows a restricted marking ({' '.join(bad.group(0).split())})"
    if basis == "licence":
        found = re.search(licence, text, re.I) if licence else None
        if found:
            return True, " ".join(found.group(0).split())
        return False, "its front matter does not show the open licence it should be published under"
    for form in (text, unshifted(text)):
        found = DISTRIBUTION_A.search(form)
        if found:
            return True, "Approved for public release; distribution is unlimited (Distribution Statement A)"
    return False, "its front matter does not say it is approved for public release (Distribution Statement A)"


# ----------------------------------------------------------------- 2. the section filter

# Never in scope, for both topics: making, changing or improvising explosives, devices or weapons.
COMMON_DROP = re.compile(
    r"manufactur\w*|fabricat\w*|home[- ]?made|improvis\w*\s+(explosive|device|weapon|munition)s?\s+(construction|"
    r"making|manufacture)|construct\w*\s+(of\s+)?(an?\s+)?(ieds?|devices?|bombs?|explosives?)|making\s+(explosives?|"
    r"bombs?|devices?|ammunition)|modif(y|ying|ication|ications)\s+(of\s+)?(munitions?|ordnance|weapons?|firearms?)|"
    r"conversions?|reloading|handload\w*", re.I)

UXO_DROP = re.compile(
    r"render[- ]?safe|\bRSPs?\b|disposal\s+(procedures?|operations?|techniques?|methods?|actions?)|"
    r"(procedures?|techniques?|methods?)\s+(of|for)\s+disposal|demolition\s+(procedures?|techniques?|operations?|"
    r"charges?|methods?|of)|destruction\s+(procedures?|in\s+place|techniques?|methods?)|destroy(ing)?\s+in\s+place|"
    r"blow[- ]in[- ]place|\bBIP\b|disarm\w*|defuz\w*|de-fuz\w*|neutrali[sz]\w*|fuz(e|ing)\s+function\w*|"
    r"function(ing)?\s+of\s+(the\s+)?fuz\w*|fuzing\b|arming\s+(sequence|mechanism|procedures?|systems?)|"
    r"charge\s+calculation|calculat\w*\s+(the\s+)?charges?|explosive\s+charges?|priming|initiation\s+(systems?|"
    r"procedures?|sets?)|firing\s+(circuits?|systems?|devices?\s+installation)|detonating\s+cord|blasting\s+caps?|"
    r"employ(ing|ment)\s+(of\s+)?(munitions?|mines?|ordnance|explosives?)|emplac\w*|laying\s+(of\s+)?(mines?|"
    r"minefields?)|mine[- ]?laying|booby[- ]?traps?\s+(setting|emplacement|construction|installation)|"
    r"setting\s+booby|breach\w*|eod\s+(procedures?|techniques?|tools?|equipment)|tools?\s+and\s+equipment|"
    r"remote\s+(movement|procedures?|handling)|access\s+procedures?|removal\s+procedures?|recovery\s+procedures?|"
    r"exploitation|post[- ]blast", re.I)

SA_DROP = re.compile(
    r"marksmanship|firing|\bfire\s+(control|commands?|distribution|team|and\s+maneuver)|modes?\s+of\s+fire|"
    r"\baim(s|ing)?\b|aiming\s+devices?|sight\s+(picture|alignment|adjustments?)|zero(ing)?\b|employment|"
    r"engagements?|tactic\w*|combat|stability|recoil\s+management|\bcontrol\b(?!\s+status\s+description)|"
    r"weapons?\s+control\s+status|overmatch|movement|carry\s+positions?|drills?|qualification|ballistic\w*|"
    r"machine\s+gun\s+theory|cycle\s+of\s+(function|operation)|feeding|chambering|\blocking\b|unlocking|"
    r"extracting|ejecting|cocking|operating\s+(instructions|procedures)|operation\s+under|\bloading\b|"
    r"unloading|reload\w*|malfunctions?|stoppages?|immediate\s+action|remedial\s+action|disassembl\w*|"
    r"reassembl\w*|\bassembly\s+(procedures?|instructions)|field\s+strip\w*|maintenance|\bPMCS\b|cleaning|"
    r"lubricat\w*|inspection|troubleshoot\w*|repair\w*|replac\w*|parts\s+lists?|special\s+tools|armou?rer|"
    r"modif\w*|conversion|select[- ]?fire\s+(conversion|modification|kits?)|(?<!flash\s)suppressors?|"
    r"silencers?|barrel\s+(change|replacement|exchange)|"
    r"trigger\s+(job|work|replacement|modification)|mount(ing|able)|accessor\w*|holsters?|ammunition|"
    r"cartridges?|rounds?\s+of|complex", re.I)
SA_SAFETY = re.compile(r"\bsafe(ty)?\b|safe\s+weapons?\s+handling|rules\s+of\s+firearms?\s+safety|warning", re.I)
SA_CLEARING = re.compile(r"clear(ing)?\s+(the\s+)?(weapon|pistol|rifle|carbine|machine\s*gun|firearm)|"
                         r"\bclearing\b|safety\s+check", re.I)
# Procedure words in running text: a page that uses them BODY_OPS_LEAST times or more is left out.
BODY_OPS = {
    "uxo": re.compile(r"render[- ]safe|blow[- ]in[- ]place|disarm\w*|defuz\w*|neutrali[sz]\w*|priming|detonating "
                      r"cord|blasting caps?|charge calculation|initiation system|demolition charge|remote "
                      r"(movement|pull)|hook[- ]and[- ]line", re.I),
    "small_arms": re.compile(r"squeeze the trigger|trigger squeeze|sight picture|point of aim|zero(ing)?\b|"
                             r"disassembl\w*|lubricat\w*|convert\w* to (select|full)[- ]?(fire|auto)\w*|"
                             r"(?<!flash )suppressor|silencer|firing position|shot process|"
                             r"engage(ment|s)? (the )?targets?", re.I),
}

CHAPTER_LINE = re.compile(r"^\s*(chapter|appendix|annex|part|section)\s+([0-9IVXL]{1,5}|[A-Z])\b\.?\s*[-–—:.]?\s*"
                          r"(.*)$", re.I)
CONTENTS_LINE = re.compile(r"(\.\s?){3,}|\s\d{1,3}(-\d{1,3})?\s*$")
STOP_START = re.compile(r"^(to|of|and|or|the|a|an|in|on|for|with|at|by|if|do|not|no|never)\b", re.I)
RUNNING_HEAD = re.compile(r"\b(TC|FM|ATP|TM|MCRP|NTTP|AFTTP|MCWP|NWP)\s?\d", re.I)
CAPTION_START = re.compile(r"^\s*(figure|fig\.|table|plate)\s", re.I)


def heading_of(line):
    """(level, title) when a printed line is a heading, else None: level 0 for a chapter, appendix, annex, part or
    section line ("Chapter II Recognizing Explosive Ordnance"), level 5 for a short line in capital letters
    ("CYCLE OF FUNCTION"). Lines of a contents list, running heads, captions and table fragments ("TO FIRE") are not
    headings."""
    text = " ".join(line.split())
    if not text or len(text) > 90 or CAPTION_START.match(text) or RUNNING_HEAD.search(text):
        return None
    m = CHAPTER_LINE.match(text)
    if m:
        rest = m.group(3)
        if rest and (CONTENTS_LINE.search(text) or rest[0].islower() or len(text) > 70
                     or re.search(r"\b(and|or|the|of|to|in|with|a)$|[,;]$", rest)):
            return None                                # a contents line or a sentence ("Chapter 2 provides ...")
        return 0, text
    letters = [c for c in text if c.isalpha()]
    words = text.split()
    if len(letters) >= 4 and text == text.upper() and 1 <= len(words) <= 9 and not STOP_START.match(text) \
            and not text.endswith((".", ",", ";")) and not CONTENTS_LINE.search(text):
        return 5, text
    return None


def starts_with_chapter(text, first=4):
    """True when one of the first lines of a page's text is a chapter, appendix, annex, part or section line."""
    lines = [line for line in (text or "").replace("\r", "").split("\n") if line.strip()][:first]
    return any((heading_of(line) or (None,))[0] == 0 for line in lines)


def page_titles(pages, bookmarks=()):
    """For each page, the list of section titles it belongs to: [(level, title, where)], where is "bookmark" or
    "heading". pages: each page's text (lines separated by new lines); bookmarks: [(level, title, page index)].

    A bookmark covers its page up to and INCLUDING the page where the next bookmark of the same or a higher level
    starts (a section can end part-way down a page), unless that page begins with a chapter line. A printed heading covers the rest of its page and the following
    pages until the next heading of the same or a higher level (a chapter line ends the capital-letter headings). A
    page with three or more chapter lines is a contents page: its headings are not used."""
    count = len(pages)
    out = [[] for _ in range(count)]
    marks = sorted((p, lvl, " ".join(str(t).split())) for lvl, t, p in bookmarks
                   if p is not None and 0 <= p < count and str(t).strip())
    top = [starts_with_chapter(text) for text in pages]
    for i, (start, level, title) in enumerate(marks):
        end = next((p for p, lvl, _t in marks[i + 1:] if lvl <= level and p > start), None)
        last = count - 1 if end is None else end - 1 if top[end] else end
        for n in range(start, max(start, last) + 1):
            out[n].append((level, title, "bookmark"))
    current = {}                                       # level -> title, carried from page to page
    for n, text in enumerate(pages):
        lines = [line for line in (text or "").replace("\r", "").split("\n") if line.strip()]
        found = [(i, h) for i, h in ((i, heading_of(line)) for i, line in enumerate(lines)) if h]
        if sum(1 for _i, (lvl, _t) in found if lvl == 0) >= 3:
            found = []                                 # a contents page
        if starts_with_chapter(text):
            current = {}                               # a chapter starts at the top: nothing is carried onto it
        found = [h for _i, h in found]
        titles = [(lvl, t, "heading") for lvl, t in sorted(current.items())]
        for level, title in found:
            for deeper in [k for k in current if k >= level]:
                del current[deeper]
            current[level] = title
            titles.append((level, title, "heading"))
        seen = set()
        for item in titles:
            if item[1] not in seen:
                seen.add(item[1])
                out[n].append(item)
    return out


def title_reason(title, topic, others=()):
    """"" when a section title is in scope for topic ("uxo" or "small_arms"), else the reason it is left out. others:
    the other titles of the same page (for small arms, "clearing" is kept only beside the safety section)."""
    found = COMMON_DROP.search(title)
    if found:
        return f"making or modifying explosives, devices or weapons ({found.group(0)})"
    if topic == "uxo":
        found = UXO_DROP.search(title)
        return f"operational EOD procedure ({found.group(0)})" if found else ""
    if SA_CLEARING.search(title):
        if any(SA_SAFETY.search(t) and not SA_DROP.search(t) for t in others if t != title) or \
                (SA_SAFETY.search(title) and not SA_DROP.search(title)):
            return ""
        return "clearing outside the manual's own safety section"
    if SA_SAFETY.search(title) and not SA_DROP.search(title):
        return ""
    found = SA_DROP.search(title)
    return f"operation, firing, maintenance or modification ({found.group(0)})" if found else ""


def filter_pages(pages, bookmarks, topic):
    """What the section filter keeps of one document: {"kept": [page indexes], "dropped": {title: [page numbers,
    counted from 1]}, "reasons": {title: reason}, "share_dropped": the share of pages with text that were left out,
    "leave_out": "" or why the whole document is left out}."""
    titles = page_titles(pages, bookmarks)
    kept, dropped, reasons, with_text, dropped_text = [], {}, {}, 0, 0
    ops = BODY_OPS[topic]
    # A capital-letter heading that is left out stays left out for the rest of its chapter (the last chapter title
    # of its page), because the smaller headings under it ("CYCLE OF FUNCTION", then "FEEDING", "BELT FEED SLIDE")
    # look the same; with no chapter titles at all, to the end of the document. sticky: (title, reason, chapter).
    sticky = None
    for n, page in enumerate(titles):
        names = [t for _lvl, t, _w in page]
        chapters = [t for lvl, t, _w in page if lvl == 0]
        bad = [(t, title_reason(t, topic, names)) for t in names]
        bad = [(t, why) for t, why in bad if why]
        if sticky and (sticky[2] is None or sticky[2] == (chapters[-1] if chapters else None)):
            bad.append(sticky[:2])
        else:
            sticky = None
        bad = list(dict(bad).items())
        for lvl, t, where in page:
            if lvl == 5 and where == "heading" and t in dict(bad) and not (sticky and sticky[0] == t):
                sticky = (t, dict(bad)[t], chapters[-1] if chapters else None)
        hits = ops.findall(pages[n] or "")
        if len(hits) >= BODY_OPS_LEAST:
            label = f"page {n + 1}: procedure words in the text"
            bad.append((label, f"procedure words used {len(hits)} times"))
        has_text = len((pages[n] or "").split()) >= 20
        with_text += has_text
        if bad:
            dropped_text += has_text
            for t, why in bad:
                dropped.setdefault(t, []).append(n + 1)
                reasons[t] = why
        else:
            kept.append(n)
    share = dropped_text / with_text if with_text else 0.0
    leave_out = ""
    if topic == "uxo" and share > MOSTLY:
        leave_out = f"mostly operational EOD procedure ({round(share * 100)} percent of its pages are out of scope)"
    if topic == "small_arms" and sum(1 for n in kept if len((pages[n] or "").split()) >= 20) < SA_LEAST_PAGES:
        leave_out = "almost nothing in it is identification or safety"
    return {"kept": kept, "dropped": dropped, "reasons": reasons, "share_dropped": share, "leave_out": leave_out}


# ----------------------------------------------------------------- 3. captions and answers

SA_FIGURE_OK = re.compile(r"\b(view|side|exterior|external|outside|components?|parts?|nomenclature|controls?|"
                          r"features?|characteristics|pistols?|rifles?|carbines?|machine\s*guns?|revolvers?|"
                          r"shotguns?|handguns?|receivers?|safet(y|ies)|selectors?|magazines?|sights?|"
                          r"slides?|barrels?|stocks?|grips?|muzzle|bipod|M\d{1,3}[A-Z]?\d?)\b", re.I)
SA_FIGURE_NOT = re.compile(r"\b(firing|fire|fired|aim\w*|stance|positions?|posture|squeez\w*|engag\w*|targets?|"
                           r"zero\w*|group(ing)?s?|shots?|range|trajector\w*|ballistic\w*|disassembl\w*|"
                           r"reassembl\w*|clean\w*|lubric\w*|malfunction\w*|stoppage\w*|immediate|remedial|"
                           r"load\w*|draw(ing)?|holster\w*|carry\w*|mount\w*|qualif\w*|drills?|cycle|feeding|"
                           r"chamber\w*|extract\w*|eject\w*|cock\w*|lock\w*|unlock\w*|modif\w*|conver\w*|"
                           r"(?<!flash\s)suppress\w*|wound\w*|casualt\w*|soldiers?|marines?|shooter\w*|gunner\w*|"
                           r"example|status|commands?|procedures?|steps?)\b",
                           re.I)
CAPTION_TOO_LITTLE = re.compile(r"^\(?(continued|cont\.?|example|examples|sample|figure|\d+)\)?\.?$", re.I)


def caption_reason(caption, topic):
    """"" when a figure's caption may be used for topic, else the reason it is not."""
    words = " ".join((caption or "").split()).rstrip(".")
    if len(words.split()) < 2 or CAPTION_TOO_LITTLE.match(words):
        return "its caption says too little"
    why = title_reason(words, topic)
    if why and not (topic == "small_arms" and SA_FIGURE_OK.search(words) and not SA_FIGURE_NOT.search(words)
                    and not COMMON_DROP.search(words) and not re.search(r"firing|maintenance|modif|conver|"
                                                                        r"ammunition|cartridge", words, re.I)):
        return why
    if topic == "small_arms":
        if SA_FIGURE_NOT.search(words):
            return f"not an exterior view or a part ({SA_FIGURE_NOT.search(words).group(0)})"
        if not SA_FIGURE_OK.search(words):
            return "the caption does not name a weapon, a view or its parts"
    return ""


# Words a caption's capital letters are kept for (the other capitalised words of a Title Case caption are lowered:
# "Examples of General Purpose Bombs" -> "examples of general purpose bombs").
PROPER = {"Soviet", "Russian", "Chinese", "American", "British", "German", "French", "Italian", "Iraqi", "Afghan",
          "Korean", "Vietnamese", "Yugoslav", "Belgian", "Israeli", "Iranian", "Ukrainian", "Warsaw", "Browning",
          "Beretta", "Sig", "Glock", "Colt", "Mark", "Model", "Navy", "Army", "Marine", "Corps", "Air", "Force"}


def figure_answer(document, label, caption, topic):
    """The draft answer for one figure: where it is from, its number and caption, then the safety line."""
    words = " ".join(caption.split()).rstrip(".")
    words = " ".join(w.lower() if re.fullmatch(r"\(?[A-Z][a-z]+(-[A-Za-z][a-z]+)*[,;:)]?", w)
                     and w.strip("(),;:").split("-")[0] not in PROPER else w for w in words.split())
    line = UXO_LINE if topic == "uxo" else GUN_LINE
    return f"This is a figure from {document['short']} (approved for public release): figure {label}, {words}. {line}"


def figure_rows(document, kept_pages, page_captions, topic):
    """The figures that may be used: [(page index, label, caption, answer)] from page_captions {page index: [(label,
    caption)]}, only on kept pages and only with a usable caption. Also [(label, caption, reason)] of those left
    out."""
    kept, used, left = set(kept_pages), [], []
    for n in sorted(page_captions):
        for label, caption in page_captions[n]:
            if n not in kept:
                left.append((label, caption, "its page is in a section that is left out"))
                continue
            why = caption_reason(caption, topic)
            if why:
                left.append((label, caption, why))
                continue
            used.append((n, label, caption, figure_answer(document, label, caption, topic)))
    return used, left


# ----------------------------------------------------------------- 4. the documents

def archive_doc(identifier, short, title, publisher, year, topic, note=""):
    """One document on the Internet Archive (its "Text PDF" is read), checked for Distribution Statement A."""
    return {"id": identifier, "source": "archive", "short": short, "title": title, "publisher": publisher,
            "year": year, "topic": topic, "basis": "statement", "licence": None, "note": note,
            "page": f"{ARCHIVE}/details/{identifier}"}


# Checked by hand in November 2026 (front matter, contents and figures); every check is made again in code.
UXO_DOCUMENTS = [
    archive_doc("atp-4-32.2-multiservice-tactics-techniques-and-procedures-for-explosive-ordnance-2024",
                "ATP 4-32.2 (2024)", "ATP 4-32.2 / MCRP 10-10D.1 / NTTP 3-02.4.1 / AFTTP 3-2.12, Multi-Service "
                "Tactics, Techniques, and Procedures for Explosive Ordnance", "US Army, Marine Corps, Navy and Air "
                "Force (ALSA Center)", 2024, "uxo",
                "Recognizing, reacting to and reporting explosive ordnance; about 37 figures (dropped, projected, "
                "placed and thrown ordnance, markers, barricades). Its cover statement is in a shifted font."),
    archive_doc("DTIC_ADA458030", "FM 3-100.38 (2005)", "FM 3-100.38 / MCRP 3-17.2B / NTTP 3-02.4.1 / AFTTP(I) "
                "3-2.12, UXO Multi-Service Tactics, Techniques, and Procedures for Unexploded Explosive Ordnance "
                "Operations", "US Army, Marine Corps, Navy and Air Force (ALSA Center); DTIC copy", 2005, "uxo",
                "UXO hazards; identifying, marking and reporting UXO; protective measures."),
    archive_doc("DTIC_ADA404336", "FM 3-100.38 (2001)", "FM 3-100.38 / MCRP 3-17.2B / NTTP 3-02.4.1 / AFTTP(I) "
                "3-2.12, UXO Multiservice Procedures for Unexploded Explosive Ordnance Operations",
                "US Army, Marine Corps, Navy and Air Force (ALSA Center); DTIC copy", 2001, "uxo",
                "Appendix A identifies dropped, projected, thrown and placed ordnance and sea mines."),
    archive_doc("FM_100_38_M_P_O_U_O_E_1996", "FM 100-38 (1996)", "FM 100-38 / MCRP 4-5.1 / NWP TP 3-02.4.1, "
                "Multiservice Procedures for Operations in an Unexploded Ordnance Environment",
                "US Army, Marine Corps, Navy and Air Force", 1996, "uxo", "A scanned copy: text only, no figures."),
    archive_doc("DTIC_ADA340928", "the UXO Reference Manual (1996)", "Unexploded Ordnance (UXO) Reference Manual",
                "Federal Advisory Committee for the Development of Innovative Technologies, with the DoD "
                "Explosives Safety Board and the Naval EOD Technology Division; DTIC copy", 1996, "uxo",
                "Types of UXO with drawings (projectiles, mortars, rockets, bombs, submunitions)."),
    archive_doc("DTIC_ADA422504", "Unexploded Ordnance (UXO): An Overview (1996)", "Unexploded Ordnance (UXO): An "
                "Overview", "Naval Explosive Ordnance Disposal Technology Division (UXO Center of Excellence); "
                "DTIC copy", 1996, "uxo", "A short overview with pictures of UXO types."),
]

SMALL_ARMS_DOCUMENTS = [
    archive_doc("tc-3-23.35-pistol-2017", "TC 3-23.35, Pistol (2017)", "TC 3-23.35, Pistol",
                "Headquarters, Department of the Army", 2017, "small_arms",
                "Kept: its overview (safe weapons handling, rules of firearms safety, weapon safety status) and the "
                "description and major components of the M9, M11 and M17 pistols."),
    archive_doc("tc-3-22.9-rifle-and-carbine-2016", "TC 3-22.9, Rifle and Carbine (2016)", "TC 3-22.9, Rifle and "
                "Carbine (with changes)", "Headquarters, Department of the Army", 2016, "small_arms",
                "Kept: safety and the description of the M16 rifle and M4 carbine (upper and lower receiver)."),
    archive_doc("tc-3-22.249-light-machine-gun-m-249-series-2017", "TC 3-22.249, Light Machine Gun M249 Series "
                "(2017)", "TC 3-22.249, Light Machine Gun M249 Series", "Headquarters, Department of the Army",
                2017, "small_arms", "Kept: overview, safety and the weapon's description."),
    archive_doc("medium-machine-gun-tc-3-22.240", "TC 3-22.240, Medium Machine Gun (2017)", "TC 3-22.240, Medium "
                "Machine Gun (M240 series)", "Headquarters, Department of the Army", 2017, "small_arms",
                "Kept: overview, safety and the weapon's description."),
    archive_doc("heavy-machine-gun-m-2-series-tc-3-22.50", "TC 3-22.50, Heavy Machine Gun M2 Series (2017)",
                "TC 3-22.50, Heavy Machine Gun M2 Series", "Headquarters, Department of the Army", 2017,
                "small_arms", "Kept: overview, safety and the weapon's description."),
]

DOCUMENTS = {"uxo": UXO_DOCUMENTS, "small_arms": SMALL_ARMS_DOCUMENTS}

UXO_NOT_INCLUDED = {
    "FM 21-16, Unexploded Ordnance (UXO) Procedures (1994), archive.org Unexploded_Ordinance_Procedures_FM_21-16":
        "the only copy found is scanned without readable text, so its release statement cannot be checked by the "
        "program; FM 3-100.38 and ATP 4-32.2 replaced it and are included.",
    "GICHD Explosive Ordnance Guide for Ukraine (2nd edition, 2022)":
        "a very good recognition guide, but '© GICHD' with no open licence; the GICHD terms of use reserve all "
        "rights and forbid changes (https://www.gichd.org/terms-of-use/), and its fuze and anti-disturbance "
        "chapters would have to be cut out. The owner may download it himself from gichd.org for personal reading.",
    "IMAS (International Mine Action Standards), mineactionstandards.org":
        "copyright of the United Nations (UNMAS); no open licence; mostly management standards, not recognition.",
    "UNMAS and UN mine-action material": "UN copyright; use beyond credited journalism needs the UN's licence.",
    "NATO EOD and ordnance-recognition publications (AEODP and others)":
        "no NATO recognition document marked releasable to the public was found as a downloadable copy.",
    "Military Munitions and Explosives of Concern: A Handbook for Federal Land Managers (BLM and FWS, 2006), "
    "archive.org militarymunition00unit":
        "a public US civilian-agency handbook, but it carries no Distribution Statement A line, which the owner's "
        "rule requires (see OWNER_DECISION).",
    "Afghanistan Ordnance Identification Guide, Volume 1 (Naval EOD Technology Division, 2004), archive.org "
    "afghanistan-ordnance-identification-guide-volume-1":
        "Distribution Statement A and written for people who are not EOD technicians, but it is a 472-page scan "
        "(no figures can be cut) and the section filter leaves out 91 percent of it (its fuzing-systems section "
        "explains how fuzes work, and its item pages could not be told apart by headings), so the mostly-out-of-scope "
        "rule leaves it out. The owner may look at it himself.",
    "Unexploded Ordnance (UXO), DTIC ADA389383 (1999)": "only a 6-page cover record; nothing to recognise.",
    "ATP 4-32.2's and FM 3-100.38's EOD sections": "kept documents; any render-safe or disposal section in them is "
                                                  "cut by the section filter, and recorded in README.txt.",
    "DTIC research reports on UXO detection (sensors, radar, magnetometry)":
        "public, but about detection equipment, not recognition by people.",
    "FM 9-40, Unexploded Bombs: Organization and Operation for Disposal (1943-44)": "about disposal: out of scope.",
}

SMALL_ARMS_NOT_INCLUDED = {
    "TM 9-1005-313-10, M240 machine gun operator's manual": "Distribution Statement C (US Government agencies and "
                                                           "their contractors only): refused.",
    "TM 9-1005-201-10, M249 machine gun operator's manual (1991)": "Distribution Statement C: refused.",
    "TM 9-1005-317-10, M9 pistol operator's manual": "no Distribution Statement A in the copies found ('to be "
                                                    "distributed in accordance with DA Form 12-40E'); TC 3-23.35 "
                                                    "covers the M9 with Distribution A.",
    "TM 9-1005-249-10 (M16, M16A1) and TM 9-1005-319-10 (M16A2)": "no Distribution Statement A in the copies "
                                                                 "found; TC 3-22.9 covers the rifle.",
    "TM 9-1005-211-12 (M1911A1, 1968), TM 9-1005-222-12 (M1 rifle, 1969), TM 9-1005-223-20 (M14, 1967), "
    "TM 9-1005-213-10 (M2, 1973)":
        "printed before distribution statements; no Distribution Statement A on them, and mostly maintenance.",
    "FSTC-CS-07-35-66, Small Arms Identification and Operation Guide, Eurasian Communist Countries (1967)":
        "no Distribution Statement A; and half of it is operation.",
    "DIA Small-Caliber Ammunition Identification Guide (DTIC ADA165896)": "ammunition, not the firearm itself; "
                                                                         "its release line cannot be read.",
    "State hunter-education manuals": "copyrighted (most are published by a private company for the states); no "
                                      "open licence found.",
    "TC 3-22.9 and the other training circulars' marksmanship chapters": "kept documents; the chapters on aiming, "
                                                                        "firing, employment, drills, zeroing and "
                                                                        "ammunition are cut by the section filter.",
}

# Material that is clearly meant for the public but lacks the line the owner's rule asks for: not downloaded; the
# owner can decide.
OWNER_DECISION = {
    "DoD 3Rs Explosives Safety Education Program (US Army Corps of Engineers): safety guides, pocket cards and fact "
    "sheets, https://www.denix.osd.mil/uxo/educational-resources/":
        "public safety education from the Department of Defense (US government works), made to be handed out, but "
        "the PDFs carry no 'Distribution Statement A' line and no licence statement. Not downloaded under the "
        "strict rule; adding them would need the owner's rule to accept 'published by DoD for public education'.",
    "Military Munitions and Explosives of Concern handbook (BLM and FWS, 2006)":
        "the same: a US civilian-agency work with no Distribution Statement A line.",
}


# ----------------------------------------------------------------- 5. reading the PDFs (pypdfium2)

def bookmarks_of(doc):
    """[(level, title, page index)] of a PDF's bookmarks (pypdfium2 4 and 5 differ; both are read)."""
    out = []
    try:
        for item in doc.get_toc(max_depth=4):
            title = item.get_title() if hasattr(item, "get_title") else getattr(item, "title", "")
            if hasattr(item, "get_dest"):
                dest = item.get_dest()
                page = dest.get_index() if dest is not None else None
            else:
                page = getattr(item, "page_index", None)
            out.append((getattr(item, "level", 0), title or "", page))
    except Exception:  # noqa: BLE001 - a PDF without bookmarks (or with broken ones)
        return []
    return out


def page_texts(doc):
    """Each page's text, lines separated by new lines."""
    out = []
    for n in range(len(doc)):
        try:
            out.append(doc[n].get_textpage().get_text_range().replace("\r", ""))
        except Exception:  # noqa: BLE001 - a page whose text cannot be read
            out.append("")
    return out


def figure_tools():
    """packs/field_manual_packs.py (the figure finder of the field-manual pack builder), imported, or None when it
    is not on this computer. Looked for beside the kit in a copy of the repository, or in the folder named by
    PICTURE_KIT_PACKS."""
    import importlib
    here = os.path.dirname(os.path.abspath(__file__))
    for folder in ("", os.environ.get("PICTURE_KIT_PACKS", ""), os.path.join(here, "..", "..", "packs")):
        if folder:
            if not os.path.isfile(os.path.join(folder, "field_manual_packs.py")):
                continue
            folder = os.path.abspath(folder)
            if folder not in sys.path:
                sys.path.append(folder)                 # appended, so it never hides the kit's own modules
        try:
            importlib.import_module("build_packs")      # loaded first, as the pack modules expect
            return importlib.import_module("field_manual_packs")
        except ImportError:
            continue
        except Exception:  # noqa: BLE001 - there, but not usable here
            return None
    return None


def page_captions_of(doc, fm, pages=None):
    """{page index: [(label, caption, box)]} of the printed figure captions (fm.captions), on pages (all when
    None)."""
    out = {}
    for n in (range(len(doc)) if pages is None else pages):
        try:
            found = fm.captions(doc[n])
        except Exception:  # noqa: BLE001 - a page that cannot be read
            found = []
        if found:
            out[n] = found
    return out


def cut_figures(doc, fm, document, kept, topic):
    """[(file name, JPEG bytes, answer, label, caption)] of the usable figures on the kept pages, cut as the
    field-manual builder cuts them, and [(label, caption, reason)] of those left out."""
    with_boxes = page_captions_of(doc, fm)
    plain = {n: [(label, caption) for label, caption, _box in found] for n, found in with_boxes.items()}
    used, left = figure_rows(document, kept, plain, topic)
    base = re.sub(r"[^a-z0-9]+", "_", document["id"].lower()).strip("_")[:40]
    out, seen = [], set()
    for n, label, caption, answer in used:
        page = doc[n]
        boxes = fm.graphic_boxes(page)
        if boxes is None:
            left.append((label, caption, "a scanned page: the drawing cannot be told from the text"))
            continue
        lines = fm.text_lines(page)
        height = page.get_size()[1]
        ordered = sorted(with_boxes[n], key=lambda c: -c[2][3])
        i = next(k for k, c in enumerate(ordered) if c[0] == label and c[1] == caption)
        above = ordered[i - 1][2][1] if i else height * 0.93
        below = ordered[i + 1][2][3] if i + 1 < len(ordered) else height * 0.07
        where = fm.figure_box(ordered[i][2], boxes, above, below, lines)
        jpeg = fm.crop(page, where) if where else None
        name = f"{base}_fig_{re.sub(r'[^A-Za-z0-9]+', '-', label)}.jpg"
        if not jpeg or name in seen:
            left.append((label, caption, "no drawing was found next to the caption"))
            continue
        seen.add(name)
        out.append((name, jpeg, answer, label, caption))
    return out, left


def kept_copy(doc, kept):
    """PDF bytes holding only the kept pages of doc."""
    import pypdfium2 as pdfium
    new = pdfium.PdfDocument.new()
    new.import_pages(doc, pages=list(kept))
    out = io.BytesIO()
    new.save(out)
    return out.getvalue()


def safe_file_name(text):
    """A file name made of text (no characters Windows forbids)."""
    return re.sub(r"\s+", " ", re.sub(r'[\\/:*?"<>|]+', " ", text)).strip()[:150]


def process_document(document, data, topic, fm=None):
    """Check and filter one document's PDF bytes. Returns {"ok", "reason", "release", "filter", "file_name",
    "pdf" (bytes to save: the original, or only the kept pages), "figures" (from cut_figures, when fm is given),
    "figures_left"}."""
    import pypdfium2 as pdfium
    result = {"ok": False, "reason": "", "release": "", "filter": None, "file_name": "", "pdf": b"",
              "figures": [], "figures_left": []}
    try:
        doc = pdfium.PdfDocument(data)
    except Exception as e:  # noqa: BLE001 - said plainly
        result["reason"] = f"the PDF cannot be read ({str(e)[:80]})"
        return result
    pages = page_texts(doc)
    ok, line = release_check(" ".join(pages[:FRONT_PAGES]), document.get("basis", "statement"),
                             document.get("licence"))
    if not ok:
        result["reason"] = line
        return result
    result["release"] = line
    kept = filter_pages(pages, bookmarks_of(doc), topic)
    result["filter"] = kept
    if kept["leave_out"]:
        result["reason"] = kept["leave_out"]
        return result
    result["ok"] = True
    title = safe_file_name(f"{document['title']} ({document.get('year', '')})".replace(" ()", ""))
    if kept["dropped"]:
        result["file_name"] = f"{title} (recognition and safety pages only).pdf"
        result["pdf"] = kept_copy(doc, kept["kept"])
    else:
        result["file_name"] = f"{title}.pdf"
        result["pdf"] = bytes(data)
    if fm is not None:
        result["figures"], result["figures_left"] = cut_figures(doc, fm, document, kept["kept"], topic)
    return result


# ----------------------------------------------------------------- 6. the personal folder

def personal_folder(topic, base=None):
    """The local folder for topic's documents: <Documents>\\Picture Model Training personal files\\<UXO
    recognition | Small arms recognition> (Documents under OneDrive when that is where Windows keeps it), or
    base\\<that name> when base is given."""
    if not base:
        home = os.path.expanduser("~")
        documents = os.path.join(home, "Documents")
        onedrive = os.path.join(home, "OneDrive", "Documents")
        if not os.path.isdir(documents) and os.path.isdir(onedrive):
            documents = onedrive
        base = os.path.join(documents, FOLDER_ROOT)
    return os.path.join(base, FOLDER_NAMES[topic])


def readme_text(topic, results):
    """README.txt for the personal folder: the personal-use rule, every document kept (release line, address, the
    sections left out and why), and every document refused (and why)."""
    what = "unexploded ordnance (UXO) recognition" if topic == "uxo" else "small arms recognition"
    lines = [PERSONAL_LINE, "",
             f"These documents are for {what}: what such things look like, their hazards in plain words, safe "
             "distances, marking and reporting" + ("" if topic == "uxo" else ", the names of a firearm's outside "
                                                   "parts and basic firearm safety") + ".",
             "They were downloaded on this computer for the owner's personal use only. Do not share, upload or "
             "redistribute them, and do not put them in anything that is published.",
             "Each one says in its own front matter that it is approved for public release (Distribution "
             "Statement A); the program checked this before keeping it.",
             "Sections outside recognition and safety (" + ("render-safe, disposal, demolition, fuze functioning, "
                                                            "charges, manufacturing, modifying, arming or "
                                                            "employing munitions" if topic == "uxo" else
                                                            "firing, marksmanship, tactics, operation, "
                                                            "disassembly, maintenance, modification and "
                                                            "ammunition") +
             ") were left out: a document with such sections is saved with only its kept pages.",
             "You can add this folder to the toolkit's \"Your own documents\".", "", "DOCUMENTS KEPT", ""]
    for document, result in results:
        if not result.get("ok"):
            continue
        lines += [f"{result['file_name']}", f"  {document['title']}, {document['publisher']}, {document['year']}.",
                  f"  Release: {result['release']}.", f"  Copy used: {document['page']}"]
        dropped = result["filter"]["dropped"] if result.get("filter") else {}
        if dropped:
            lines.append("  Left out (title: pages: reason):")
            for title, pages in dropped.items():
                lines.append(f"    {title}: {page_ranges(pages)}: {result['filter']['reasons'][title]}")
        else:
            lines.append("  Nothing left out.")
        lines.append("")
    lines += ["DOCUMENTS LEFT OUT", ""]
    for document, result in results:
        if not result.get("ok"):
            lines += [f"{document['title']} ({document['page']}): {result.get('reason') or 'not read'}."]
            dropped = result["filter"]["dropped"] if result.get("filter") else {}
            for title, pages in list(dropped.items())[:40]:
                lines.append(f"    {title}: {page_ranges(pages)}: {result['filter']['reasons'][title]}")
    not_included = UXO_NOT_INCLUDED if topic == "uxo" else SMALL_ARMS_NOT_INCLUDED
    lines += ["", "LOOKED AT AND NOT DOWNLOADED", ""] + [f"{k}: {v}" for k, v in not_included.items()]
    return "\r\n".join(lines) + "\r\n"


def page_ranges(pages):
    """Page numbers as short ranges: [1, 2, 3, 7] -> "pages 1-3, 7"."""
    pages = sorted(set(pages))
    parts, start = [], None
    for i, p in enumerate(pages):
        if start is None:
            start = p
        if i + 1 == len(pages) or pages[i + 1] != p + 1:
            parts.append(f"{start}" if start == p else f"{start}-{p}")
            start = None
    return ("page " if len(pages) == 1 else "pages ") + ", ".join(parts)


# ----------------------------------------------------------------- 7. the review workspace and fetch

REVIEW_INSTRUCTIONS = """PERSONAL-USE REVIEW COLLECTION: {name}

PERSONAL USE; NOT FOR REDISTRIBUTION. These pictures were cut from military manuals that are approved for public
release, on this computer, for the owner's private describer only. They are never shared, never put in a published
model and never used to make pictures.

They are for RECOGNITION AND SAFETY: what {what} looks like, with its printed caption, so that the describer can
say what a pictured object is{safety}.

For every picture (with a sighted helper where needed):
1. DELETE the picture when it shows how to take something apart, disarm, defuze, destroy, fire, aim, load, modify
   or repair anything, or a person being hurt.
2. DELETE it when the picture does not match its caption (the cut can catch the wrong part of a page).
3. Read the draft description. It is made from the manual's own caption and always ends with the safety line. Keep
   the safety line. Correct anything that is wrong.
4. Mark the picture "checked" only when it is right. Only checked pictures are ever trained on.

The documents themselves are in the personal folder named in each picture's notes, with README.txt.
Source: {credit}
Licence or terms: {licence}
"""


def make_review_workspace(folder, source, say):
    """A review_sources.ReviewWorkspace with this collection's instructions and flags (content "graphic",
    personal_only, never_publish, never_for_picture_making), whose pictures arrive as "needs another look"."""
    import describe_package as dp
    import review_sources as rs

    class RecognitionWorkspace(rs.ReviewWorkspace):
        """ReviewWorkspace for the personal recognition collections (its own notes and CREDITS.txt columns)."""

        def flush(self):
            """Add the queued pictures as "needs another look", with credit and source in notes and CREDITS.txt."""
            if not self.waiting:
                self.save_tried()
                return
            dp.add_pictures(self.workspace, [os.path.join(self.staging, n) for n, *_ in self.waiting], person="")
            lines = []
            for item in self.waiting:
                name, credit, licence, page, content, note = item[:6]
                if self.workspace.pictures.get(name) is None:
                    continue
                entry = self.workspace.entry(name)
                entry.update(status=dp.LOOK, described_by="", described_at="", checked_by="", checked_at="",
                             changed_at=dp.now(), content=content, review="review-only",
                             notes=rs.clean(f"PERSONAL USE; NOT FOR REDISTRIBUTION. Draft description from the "
                                            f"manual's own caption; check it (see {REVIEW_FILE}). {note} Credit: "
                                            f"{credit}. Licence: {licence}. Source: {page}"))
                lines.append("\t".join([name, credit, licence, page]))
                self.added += 1
            self.workspace.save()
            with open(os.path.join(self.folder, CREDITS_FILE), "a", encoding="utf-8", newline="\r\n") as f:
                if f.tell() == 0:
                    f.write(f"Credits for {self.source['name']} ({PERSONAL_LINE})\nfile\tcredit\tlicence\tsource\n")
                f.write("\n".join(lines) + ("\n" if lines else ""))
            shutil.rmtree(self.staging, ignore_errors=True)
            self.waiting = []
            self.save_tried()
            self.say(f"{self.source['name']}: {len(self.workspace.pictures)} pictures in the review workspace.")

    ws = RecognitionWorkspace(folder, source, say)
    ws.workspace.data.update(content="graphic", review_only=True, personal_only=True, never_publish=True,
                             never_for_picture_making=True, needs_explicit_choice=True)
    ws.workspace.save()
    uxo = source["topic"] == "uxo"
    with open(os.path.join(ws.folder, REVIEW_FILE), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(REVIEW_INSTRUCTIONS.format(
            name=source["name"], credit=source["credit"], licence=f"{source['licence']} ({source['terms_summary']})",
            what="a kind of unexploded ordnance" if uxo else "a kind of firearm and its outside parts",
            safety=", and then tell the person not to touch it, to move back and to report it" if uxo else
            ", with the reminder to treat every gun as loaded"))
    return ws


def download_pdf(identifier, session=None):
    """(PDF bytes, address) of an Internet Archive item's PDF (its "Text PDF" first), or (None, reason)."""
    import requests
    from urllib.parse import quote
    s = session or requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    meta = s.get(f"{ARCHIVE}/metadata/{identifier}", timeout=60).json()
    files = [f for f in meta.get("files", []) if f.get("name", "").lower().endswith(".pdf")]
    if not files:
        return None, "the Internet Archive item has no PDF"
    files.sort(key=lambda f: (f.get("format") != "Text PDF", -int(f.get("size") or 0)))
    url = f"{ARCHIVE}/download/{identifier}/{quote(files[0]['name'])}"
    for attempt in range(3):
        r = s.get(url, timeout=600)
        if r.status_code == 200 and r.content[:5] == b"%PDF-":
            return r.content, url
        time.sleep(5 * (attempt + 1))
    return None, f"could not be downloaded from {url}"


def fetch_topic(topic, folder, cap, say=say_nothing, documents_base=None, download=None, fm="find"):
    """Fill topic's review workspace (folder) with figure crops and its personal folder with the documents (see the
    module docstring); returns a plain summary. download(document) -> (bytes, address) replaces the Internet
    Archive download (for tests); fm: the figure tools (field_manual_packs), "find" to look for them, None for
    none."""
    source = next(s for s in UXO_PERSONAL_SOURCES if s["topic"] == topic)
    try:
        import pypdfium2  # noqa: F401 - only checked here, used by process_document
    except ImportError:
        raise RuntimeError("the PDF reader pypdfium2 is not installed in the kit's Python, so the manuals cannot "
                           "be checked; nothing was downloaded") from None
    out_folder = personal_folder(topic, documents_base)
    os.makedirs(out_folder, exist_ok=True)
    ws = make_review_workspace(folder, source, say)
    if fm == "find":
        fm = figure_tools()
    if fm is None:
        say("The figure finder (packs/field_manual_packs.py) is not on this computer, so no figures are cut; the "
            "documents are still saved.")
    results, refused, figures_left = [], 0, 0
    for document in DOCUMENTS[topic]:
        say(f"  {document['title']} ...")
        try:
            data, where = download(document) if download else download_pdf(document["id"])
        except Exception as e:  # noqa: BLE001 - said plainly; the others go on
            data, where = None, f"could not be downloaded now ({str(e)[:100]})"
        if data is None:
            results.append((document, {"ok": False, "reason": where}))
            refused += 1
            say(f"    left out: {where}")
            continue
        result = process_document(document, data, topic, fm)
        results.append((document, result))
        if not result["ok"]:
            refused += 1
            say(f"    left out: {result['reason']}")
            continue
        with open(os.path.join(out_folder, result["file_name"]), "wb") as f:
            f.write(result["pdf"])
        dropped = result["filter"]["dropped"]
        say(f"    kept {len(result['filter']['kept'])} pages; {len(dropped)} section titles left out; "
            f"{len(result['figures'])} figures.")
        figures_left += len(result["figures_left"])
        credit = f"{document['title']}, {document['publisher']}, {document['year']}; {PD}; {result['release']}; " \
                 f"copy at {document['page']}"
        for name, jpeg, answer, label, caption in result["figures"]:
            if ws.full(cap):
                break
            if ws.done(name):
                continue
            ws.add(name, jpeg, answer, credit, "Public domain (US government work); Distribution Statement A",
                   document["page"], content="graphic",
                   note=f"Figure {label} ({caption}). The document is in {out_folder}.")
    with open(os.path.join(out_folder, README), "w", encoding="utf-8", newline="") as f:
        f.write(readme_text(topic, results))
    kept = sum(1 for _d, r in results if r.get("ok"))
    ws.flush()
    summary = (f"{source['name']}: {kept} of {len(results)} documents kept in {out_folder} ({refused} left out; "
               f"the reasons and every section left out are in {README}); {ws.added} new figures added for review "
               f"({len(ws.workspace.pictures)} in the workspace), {figures_left} figures not used. Every figure "
               f"needs a check before it can be used (see {REVIEW_FILE}). {PERSONAL_LINE}")
    say(summary)
    return summary


def fetch_uxo_recognition(folder, cap, say=say_nothing):
    """The UXO recognition collection (fetch_topic "uxo")."""
    return fetch_topic("uxo", folder, cap, say)


def fetch_small_arms_recognition(folder, cap, say=say_nothing):
    """The small arms recognition collection (fetch_topic "small_arms")."""
    return fetch_topic("small_arms", folder, cap, say)


# ----------------------------------------------------------------- the table

TERMS_SUMMARY = ("US government works approved for public release (Distribution Statement A); kept for personal "
                 "use only by the owner's rule: never shared, never published, never used to make pictures.")

UXO_PERSONAL_SOURCES = [
    dict(key="uxo_recognition_personal", topic="uxo",
         name="Unexploded ordnance recognition: figures from public military manuals (personal use, review)",
         category="research", licence="Public domain (US government works), each with Distribution Statement A "
                                      "checked in its own front matter",
         terms="https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/523024p.pdf",
         terms_summary=TERMS_SUMMARY,
         credit="US Army, Marine Corps, Navy and Air Force multi-service publications and the Naval EOD Technology "
                "Division, copies on the Internet Archive (https://archive.org), credited per picture",
         content="graphic", cap=300, download="about 150 MB of PDFs", fetch=fetch_uxo_recognition,
         review_only=True, personal_only=True, never_publish=True, never_for_picture_making=True),
    dict(key="small_arms_recognition_personal", topic="small_arms",
         name="Small arms recognition: exterior views from public Army training circulars (personal use, review)",
         category="research", licence="Public domain (US government works), each with Distribution Statement A "
                                      "checked in its own front matter",
         terms="https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/523024p.pdf",
         terms_summary=TERMS_SUMMARY,
         credit="Headquarters, Department of the Army training circulars, copies on the Internet Archive "
                "(https://archive.org), credited per picture",
         content="graphic", cap=100, download="about 120 MB of PDFs", fetch=fetch_small_arms_recognition,
         review_only=True, personal_only=True, never_publish=True, never_for_picture_making=True),
]
# Neither collection may be used for picture-making.
UXO_PICTURE_MAKING_OK = set()


def check_file(path, topic):
    """Print what the release check and the section filter make of one local PDF (nothing is downloaded)."""
    with open(path, "rb") as f:
        data = f.read()
    document = {"id": os.path.basename(path), "short": os.path.basename(path), "title": os.path.basename(path),
                "basis": "statement", "licence": None}
    result = process_document(document, data, topic, figure_tools())
    print(f"kept: {result['ok']} ({result['release'] or result['reason']})")
    if result.get("filter"):
        print(f"pages kept: {len(result['filter']['kept'])}; share left out: "
              f"{round(result['filter']['share_dropped'] * 100)} percent")
        for title, pages in result["filter"]["dropped"].items():
            print(f"  left out: {title}: {page_ranges(pages)}: {result['filter']['reasons'][title]}")
    for name, _jpeg, answer, _label, _caption in result.get("figures", []):
        print(f"  figure {name}: {answer}")
    for label, caption, why in result.get("figures_left", [])[:60]:
        print(f"  figure not used: {label} {caption}: {why}")


def main(argv=None):
    """uxo|small_arms <workspace folder> [cap], or check <PDF> uxo|small_arms (see the module docstring)."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) >= 3 and argv[0] == "check":
        check_file(argv[1], argv[2])
        return 0
    if len(argv) >= 2 and argv[0] in TOPICS:
        fetch_topic(argv[0], argv[1], int(argv[2]) if len(argv) > 2 else 20, print)      # says its own summary
        return 0
    print(__doc__.split("\n\n")[0])
    print("python uxo_personal_sources.py uxo|small_arms <workspace folder> [cap]\n"
          "python uxo_personal_sources.py check <PDF> uxo|small_arms")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
