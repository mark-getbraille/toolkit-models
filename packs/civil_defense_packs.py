"""Pack builders for OLD US CIVIL DEFENSE BOOKLETS AND FILMS (the 1950s to the 1980s): the drawings and photographs
printed in the booklets of the Federal Civil Defense Administration, the Office of Civil and Defense Mobilization, the
Office of Civil Defense and the Defense Civil Preparedness Agency, and still pictures from civil defense films (the
Prelinger Archives and the US government films on the Internet Archive). The owner suggested them: home shelters,
emergency supplies, fallout, first aid, rescue, fire fighting and warning signals were drawn and filmed to teach
ordinary people, so the pictures are clear teaching pictures. Used by build_packs.py in the same way as its own PACKS:
each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question",
"answer", "credit"}, plus "content" ("graphic" or "medical") and "child": True where they apply. A picture with two
questions comes once with its JPEG and then as (None, None, row) with "file" naming the same picture
(food_packs.with_twins). The limit counts pictures.

  cd_booklets   Pictures from US civil defense booklets, 1950 to 1985, found on each scanned page by
                training-kit/kit/civil_defense_figures.py (the shared method: the page is drawn, the running text is
                blanked out, and what is left that is inked and big enough is a picture). A picture whose own caption
                is printed next to it ("Figure 9. Aboveground double-wall shelter") gets "What does this picture
                show?" with "This is a drawing from a 1959 US civil defense booklet, 'The Family Fallout Shelter':
                figure 9, aboveground double-wall shelter." and "Where is this picture from?"; a picture whose
                caption is only "Figure 5" gets the sentence of the booklet's own text that names figure 5, quoted;
                a booklet's cover gets "It is the cover of ...". A picture with no caption is set aside for a person
                to describe
                (build_packs.needs_description), with the booklet's sentence and the words printed in the picture as
                hints. Nothing is guessed from the picture itself.
  cd_films      Still pictures from US civil defense films ("Duck and Cover", 1951; "Survival Under Atomic Attack",
                1951; "About Fallout", 1963 ...). Each film is downloaded once (the Internet Archive's smallest MP4
                copy) and ffmpeg takes a still at each change of scene, and at least one every 12 seconds. Stills in
                the first 25 and the last 20 seconds (titles and credits), black, white and blank frames, title
                cards, blurred stills and repeats are left out (civil_defense_figures.still_problem, with the
                kit's video_frames.py numbers); black bars, burned-in logos or time codes and the frame lines of
                full-frame film scans near the edges are cropped off (a film that would lose more than 30 percent
                of its picture that way is left out).
                Each still gets "Where is this picture from?" with a fixed sentence from the film's own record:
                "A still from the 1951 US civil defense film 'Duck and Cover', made by Archer Productions, Inc. for
                the U.S. Federal Civil Defense Administration." and the record's own short description of the film,
                quoted. Nothing in the answer is about what the still shows, so nothing is guessed. A film whose
                record has no description (under 8 words) gives no rows: its stills are set aside for a person to
                describe.

WHERE THEY COME FROM. The Internet Archive (archive.org): its advanced search and metadata APIs (documented at
https://archive.org/developers/) and its download addresses; its robots.txt (https://archive.org/robots.txt) disallows
only /control/ and /report/. One request at a time, with build_packs.USER_AGENT.
  Booklets: items whose creator is a US federal civil defense agency (CD_AGENCY: Federal Civil Defense
    Administration, Office of Civil and Defense Mobilization, Office of Civil Defense, Defense Civil Preparedness
    Agency, early FEMA), and every other creator named is a US federal body (no contractor, university or state
    office), dated 1950 to 1985. US government works are not protected by copyright (17 U.S.C. 105), whatever a
    copy's uploader wrote; an item whose uploader put a non-commercial or no-derivatives licence on it is left out
    all the same. Items the Archive only lends (inlibrary, printdisabled) and microfiche scans are not used.
  Films: the Prelinger Archives' own advice (https://www.panix.com/~footage/prelarch.html, May 2026): "DO NOT ASSUME
    that all Prelinger Archives films are in the public domain"; "Many Prelinger films carry a Creative Commons Public
    Domain Dedication ... this Public Domain dedication still governs films to which it has been affixed." So a film
    is used only when its item carries a public-domain mark (licenseurl: the Public Domain Dedication, the Public
    Domain Mark or CC0), or when its maker (creator) is itself a US federal agency (a US government work, 17 U.S.C.
    105). Films made for the government by private studios are used only with the mark.

SAFETY (packs/SOURCE-RULES.md). Pictures and stills whose words, or whose booklet or film, are about bombs, blasts,
explosions, attack damage, casualties, injuries or burns carry "content": "graphic" (the kit's graphic choice, never for
picture-making); a film about nuclear attack is graphic in all its stills, since a still cannot be checked by its
words. First-aid and home-nursing pictures without those words carry "content": "medical". Films whose record names
Hiroshima, Nagasaki, victims or the dead, booklets about childbirth, and anything whose words are about nudity or sex
are left out. Many films and booklets show schoolchildren (school drills, "Duck and Cover"): every row whose film or
booklet names children, pupils or schools carries "child": True (everyday scenes only, never for picture-making). Both
packs show people, so neither is ever used for picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS).

The UK, Canadian, Australian and New Zealand civil defence booklets and films are not open (Crown copyright, or
restored in the United States) and are kit entries: training-kit/kit/civil_defense_sources.py.

Needs: pypdfium2 (cd_booklets) and the ffmpeg program (cd_films; on GitHub's machines "sudo apt-get install -y
ffmpeg").

    python packs/civil_defense_packs.py cd_booklets --limit 6 --items familyfalloutshe00unitrich
    python packs/civil_defense_packs.py cd_films --limit 4 --items DuckandC1951
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote

import build_packs  # noqa: F401 - loaded first, as the other pack modules do
from build_packs import session, say, considered, needs_description, pass_random, listing_out_of_time, \
    out_of_time, clean
from food_packs import with_twins, count_pictures

# The shared page and still method lives with the kit (training-kit/kit/civil_defense_figures.py), which uses it too.
KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "training-kit", "kit")
if KIT not in sys.path:
    sys.path.append(KIT)
import civil_defense_figures as figures  # noqa: E402

ARCHIVE = "https://archive.org/"
SEARCH = ARCHIVE + "advancedsearch.php"
DRAWING_Q = "What does this picture show?"
FROM_Q = "Where is this picture from?"
PD_US = "a US government work, not subject to copyright in the United States (17 U.S.C. 105)"

# ----------------------------------------------------------------- words

# The US federal civil defense agencies, as library records name them.
CD_AGENCY = re.compile(r"Federal Civil Defense Administration|Office of Civil and Defense Mobilization|Office of "
                       r"Civil Defense|Defense Civil Preparedness Agency|Federal Emergency Management Agency|"
                       r"Office of Defense Mobilization|National Security Resources Board", re.I)
# Every creator of a booklet must be one of these (a US federal body).
FEDERAL = re.compile(r"^\W*(United States|U\.\s?S\.|US\b|Federal|Office of Civil|Defense Civil|Department of "
                     r"Defense|Executive Office of the President|National Security Resources Board|Office of Defense "
                     r"Mobilization)", re.I)
# A state, territory or city civil defense office, or a contractor ("Minnesota. Office of Civil Defense").
NOT_FEDERAL = re.compile(r"\b(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|"
                         r"Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|"
                         r"Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New "
                         r"Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|"
                         r"Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|"
                         r"Virginia|Washington|West Virginia|Wisconsin|Wyoming|Guam|Puerto Rico|Philippines?|"
                         r"county|city of|university|college|institute|inc\b|incorporated|corporation|company|"
                         r"associates|laboratory|research)\b", re.I)
# The shared words (training-kit/kit/civil_defense_figures.py): what makes a row graphic, medical or a child's, and
# what is never used.
GRAPHIC, MEDICAL, CHILD, LEAVE_OUT = figures.GRAPHIC, figures.MEDICAL, figures.CHILD, figures.LEAVE_OUT
# Titles of items with no pictures to find (reports, lists, newsletters): not downloaded.
TEXT_ONLY = re.compile(r"\b(report to (the )?congress|annual report|appropriation|hearings?|bibliograph\w*|"
                       r"newsletter|minutes|catalog of courses|directory|statistic\w*|stockpile report)\b", re.I)
# What a civil defense film is about (one of these in its title, description or subjects).
CD_TOPIC = re.compile(r"civil defen[cs]e|fallout|shelters?|atomic attack|nuclear attack|duck and cover|conelrad|"
                      r"radiological|survival|emergency|air raid|home protection|evacuat\w*|disaster|warning", re.I)
# Films about soldiers in battle or weapons rather than civilians' protection.
NOT_CD_FILM = re.compile(r"\b(battlefield|combat|soldier\w*|infantry|armor|tank crews?|missile crews?|"
                         r"anti-?aircraft|radar defense|december 7th|pearl harbor|beaches|victory garden\w*|"
                         r"gardens of victory)\b", re.I)
PD_MARK = re.compile(r"creativecommons\.org/(licenses/publicdomain|publicdomain/(mark|zero))", re.I)
NC_ND = re.compile(r"licenses/[a-z-]*(nc|nd)[a-z-]*/", re.I)


def text_of(value):
    """A metadata field (text or a list of texts) as plain text."""
    if isinstance(value, list):
        value = " ".join(str(v) for v in value)
    return clean(value)


def listed(value):
    """A metadata field as a list of plain texts."""
    if value is None:
        return []
    return [clean(v) for v in (value if isinstance(value, list) else [value]) if clean(v)]


def year_of(meta, title=""):
    """The four-digit year of an item (its year or date field, or a year in its title), or 0."""
    for value in (meta.get("year"), meta.get("date"), title):
        m = re.search(r"\b(19[3-9]\d|20[0-2]\d)\b", text_of(value))
        if m:
            return int(m.group(1))
    return 0


def a_or_an(word):
    """"a" or "an" for the word that follows."""
    return "an" if re.match(r"[aeiou]|1[18]\d\d\b|8", str(word), re.I) else "a"


def tidy_title(title):
    """A booklet's or film's title as said in an answer: without a leading form code ("H-7", "IG-3-2", "CPG 1-19",
    "MP-15"), a trailing year or "(1966 revision)", a bracketed note, or its subtitle after " : "."""
    t = clean(title)
    t = re.sub(r"\[[^\]]*\]?", "", t)
    t = re.sub(r"^(?:[A-Z]{1,4}[- ]?\d+(?:[-.]\d+)*[A-Z]?\s+|Family Shelter Series PSD F-\d+-\d+\s+)", "", t)
    t = re.split(r"\s+:\s+|\s*;\s+", t)[0]
    t = re.sub(r"\s*\(?(19[3-9]\d)(?: revision)?\)?\s*$", "", t)
    t = re.sub(r"\s+(?:\d{4}\s+)?[A-Z]-\d+\s*\(\s*Revised\s*\)\s*$", "", t)
    t = t.strip(" .,:;-")
    if t.isupper():
        t = t.title()
    return t[:1].upper() + t[1:]


def doc_kind(title):
    """"handbook", "manual", "guide" or "booklet", as the title says."""
    for word in ("handbook", "manual", "guide"):
        if re.search(rf"\b{word}\b", title, re.I):
            return word
    return "booklet"


AGENCY_NAMES = {name.lower(): name for name in (
    "Federal Civil Defense Administration", "Office of Civil and Defense Mobilization", "Office of Civil Defense",
    "Defense Civil Preparedness Agency", "Federal Emergency Management Agency", "Office of Defense Mobilization",
    "National Security Resources Board")}


def agency_of(creators):
    """The civil defense agency among an item's creators, in its usual spelling ("Office of Civil Defense"), or ""."""
    for c in creators:
        m = CD_AGENCY.search(c)
        if m:
            return AGENCY_NAMES.get(m.group(0).lower(), m.group(0))
    return ""


# ----------------------------------------------------------------- the Internet Archive

def search(s, query, fields=("identifier",), rows=500):
    """The documents of an Internet Archive advanced search (at most rows), [] when it does not answer."""
    try:
        r = s.get(SEARCH, params={"q": query, "fl[]": list(fields), "rows": str(rows), "output": "json"},
                  timeout=90)
        return (r.json().get("response") or {}).get("docs", []) if r.status_code == 200 else []
    except Exception:  # noqa: BLE001 - no answer: nothing found
        return []


def item(s, identifier):
    """An Internet Archive item's metadata and files ({"metadata": {...}, "files": [...]}), {} when not found."""
    try:
        r = s.get(f"{ARCHIVE}metadata/{quote(identifier)}", timeout=90)
        return r.json() if r.status_code == 200 else {}
    except Exception:  # noqa: BLE001 - not found
        return {}


def download(s, url, path, most_bytes):
    """Download url into path (in pieces); False when it fails, is over most_bytes, or the time is up."""
    try:
        with s.get(url, stream=True, timeout=120) as r:
            if r.status_code != 200:
                return False
            size = 0
            with open(path, "wb") as f:
                for block in r.iter_content(1 << 20):
                    size += len(block)
                    if size > most_bytes or out_of_time():
                        return False
                    f.write(block)
        return size > 0
    except Exception:  # noqa: BLE001 - left out
        return False


# ----------------------------------------------------------------- booklets

BOOKLET_QUERY = ('mediatype:texts AND creator:("Federal Civil Defense Administration" OR "Office of Civil Defense" OR '
                 '"Office of Civil and Defense Mobilization" OR "Defense Civil Preparedness Agency" OR "Federal '
                 'Emergency Management Agency") AND NOT collection:(inlibrary OR printdisabled OR lendinglibrary OR '
                 'microfiche)')
# Booklets checked by hand (November 2026), tried first: US government works with a PDF on the Internet Archive.
BOOKLETS = ["familyfalloutshe00unitrich", "h-7-family-shelter-designs-1962", "falloutprotectio00unitrich",
            "falloutprotectio1966unitrich", "familyfalloutshelter", "home-protection-exercises",
            "in-time-of-emergency-1968", "intimeofemergenc00unit_0", "civildefenseinsc00unitrich",
            "interimcivildefe1951unitrich", "family-shelter-series-psd-f-61-3-basement-concrete-block-shelter",
            "family-shelter-series-psd-f-61-4-outside-semimounded-plywood-box",
            "family-shelter-series-psd-f-61-5-belowground-corrugated-steel-culvert",
            "family-shelter-series-psd-f-61-6-outside-semimounded-steel-igloo",
            "family-shelter-series-psd-f-61-7-aboveground-earth-covered-lumber",
            "family-shelter-series-psd-f-61-8-belowground-new-construction-clay",
            "fallout-protection-for-homes-with-basements-may-1967", "h-6-fallout-protection-what-to-know-and-do-"
            "about-nuclear-attack", "emergency-mass-feeding-course-1953", "ig-3-2-basic-course-for-civil-defense-1955",
            "h-16-shelter-management-handbook-1978", "HandbookForFalloutShelterManagement", "churchcivildefen00unit",
            "clergyincivildef00unitrich", "familyguideemerg00unit_0", "CAT31305662", "CAT31108232"]
BOOKLET_MOST_PAGES = 200
BOOKLET_MOST_BYTES = 150_000_000
BOOKLET_MOST_PICTURES = 40         # at most this many pictures from one booklet, so the pack spreads over many


def booklet_ok(meta):
    """"" when an Internet Archive item may be used as a US civil defense booklet (see the module docstring), else the
    reason it is not."""
    creators = listed(meta.get("creator"))
    title = text_of(meta.get("title"))
    words = " ".join([title, text_of(meta.get("description")), text_of(meta.get("subject"))])
    year = year_of(meta, title)
    if not creators or not agency_of(creators):
        return "its creator is not a US federal civil defense agency"
    bad = next((c for c in creators if NOT_FEDERAL.search(c) or not (FEDERAL.search(c) or CD_AGENCY.search(c))), "")
    if bad:
        return f"one of its makers is not shown to be a US federal body ({bad})"
    if year and not 1950 <= year <= 1985:
        return f"it is from {year} (only 1950 to 1985 are used)"
    if not year and re.search(r"Federal Emergency Management", " ".join(creators), re.I):
        return "an undated FEMA item (only 1950 to 1985 are used)"
    if NC_ND.search(text_of(meta.get("licenseurl"))):
        return "its uploader put a non-commercial or no-derivatives licence on the copy"
    collections = {c.lower() for c in listed(meta.get("collection"))}
    if collections & {"inlibrary", "printdisabled", "lendinglibrary", "microfiche", "eric-microfiche"}:
        return "the Internet Archive only lends it, or it is a microfiche scan"
    if TEXT_ONLY.search(title):
        return "a report or list without pictures"
    if LEAVE_OUT.search(words):
        return "its words are about childbirth, nudity or the dead"
    return ""


def booklet_pdf(data):
    """The (name, size) of an item's PDF with words in it: its "Text PDF" first, then any PDF; ("", 0) if none."""
    pdfs = [f for f in data.get("files", []) if str(f.get("name", "")).lower().endswith(".pdf")]
    order = {"Text PDF": 0, "Additional Text PDF": 1}
    pdfs.sort(key=lambda f: (order.get(f.get("format"), 2), int(f.get("size") or 0)))
    return (pdfs[0]["name"], int(pdfs[0].get("size") or 0)) if pdfs else ("", 0)


def booklet_rows(meta, page, number, fig, credit, said=""):
    """The rows of one picture from a booklet (page and number count from 0; number 0 is the page's biggest
    picture), or None when it has no caption (it is then set aside). said: the sentence of the booklet's own text that
    names the picture's figure number ("The roof beams (marked "C" in fig. 5) are installed ..."), used when the
    caption is only "Figure 5". Also returns the sentence saying where it is from and its marks: (rows or None,
    sentence, marks)."""
    title = tidy_title(text_of(meta.get("title")))
    year = year_of(meta, text_of(meta.get("title")))
    creators = listed(meta.get("creator"))
    agency = agency_of(creators)
    kind = fig["kind"]
    made = f"{a_or_an(year or 'US')} {year} US" if year else "a US"
    lead = f"{a_or_an(kind)} {kind} from {made} civil defense {doc_kind(title)}, '{title}'"
    source = f"It is {lead}" + (f", published by the {agency}" if agency else "") + "."
    caption = fig["caption"]
    words = " ".join([caption, fig["labels"], text_of(meta.get("title"))])
    marks = {}
    booklet_words = " ".join([text_of(meta.get("title")), text_of(meta.get("subject"))])
    if GRAPHIC.search(caption) or re.search(r"\beffects?\b|attack environment|damage", booklet_words, re.I):
        marks["content"] = "graphic"
    elif MEDICAL.search(caption) or re.search(r"first aid|health care|nursing|medical", booklet_words, re.I):
        marks["content"] = "medical"
    if CHILD.search(words) or CHILD.search(booklet_words):
        marks["child"] = True
    if page == 0 and number == 0 and fig["share"] >= 0.3 and not caption:
        answer = f"It is the cover of {made} civil defense {doc_kind(title)}, '{title}'."
    elif caption and figures.caption_ok(caption) and not LEAVE_OUT.search(caption):
        text = caption[:1].lower() + caption[1:] if re.match(r"[A-Z][a-z]", caption) else caption
        answer = (f"This is {lead}: figure {fig['label']}, {text}." if fig["label"] else f"This is {lead}: {text}.")
    elif fig["label"] and said:
        answer = f"This is {lead}: figure {fig['label']}. The booklet's text about it says: \"{said}\""
        if GRAPHIC.search(said) and "content" not in marks:
            marks["content"] = "graphic"
    else:
        return None, source, marks
    rows = [dict({"question": DRAWING_Q, "answer": answer, "credit": credit}, **marks),
            dict({"question": FROM_Q, "answer": source, "credit": credit}, **marks)]
    return rows, source, marks


def figure_sentence(doc, n, label, words=45):
    """The first sentence of the booklet's own text, on page n or the pages just before and after it, that names
    figure label ("... marked "B" in fig. 5 ..."), tidied; "" when there is none or it is not clean text."""
    mention = re.compile(rf"\bfig(?:ure|s)?\.?\s*{re.escape(label)}\b", re.I)
    for k in (n, n - 1, n + 1):
        if not 0 <= k < len(doc):
            continue
        text = " ".join(doc[k].get_textpage().get_text_range().split())
        text = re.sub(r"(\w)- (\w)", r"\1\2", text)
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text):
            if mention.search(sentence) and not figures.FIGURE.match(sentence) and \
                    6 <= len(sentence.split()) <= words and figures.word_share(sentence) >= 0.85:
                return sentence.strip()
    return ""


def booklet_pictures(data, meta, identifier, pdf_url, page_url, most):
    """[(file name, JPEG bytes, rows)] of one booklet's PDF bytes (at most most), and set aside the pictures
    without a caption."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(data)
    if len(doc) > BOOKLET_MOST_PAGES:
        considered(identifier, pdf_url, f"too long ({len(doc)} pages; at most {BOOKLET_MOST_PAGES})")
        return []
    title = text_of(meta.get("title"))
    year = year_of(meta, title)
    agency = agency_of(listed(meta.get("creator"))) or "US government"
    base = re.sub(r"[^a-z0-9]+", "_", identifier.lower()).strip("_")[:40]
    out = []
    pages = list(range(len(doc)))
    for n in pages:
        if len(out) >= most or out_of_time():
            break
        try:
            found = figures.page_figures(doc[n])
        except Exception as e:  # noqa: BLE001 - a page that cannot be read is skipped
            considered(f"{base}_p{n + 1}", pdf_url, f"the page could not be read ({type(e).__name__})")
            continue
        for i, fig in enumerate(found[:4]):
            name = f"cd_{base}_p{n + 1:03d}_{i}.jpg"
            at = f"{page_url}/page/n{n}"
            credit = (f"{agency}, '{tidy_title(title)}'" + (f" ({year})" if year else "") + f", page {n + 1}; "
                      f"{PD_US}; Internet Archive copy {page_url}")
            said = figure_sentence(doc, n, fig["label"]) if fig["label"] and not fig["caption"] else ""
            rows, source, marks = booklet_rows(meta, n, i, fig, credit, said)
            if rows is None:
                hint = {"lead": source, "page": n + 1, **marks}
                if re.search(r"nuclear|atomic|attack|fallout|blast|bomb|radiolog|radiation|war\b",
                             title, re.I) and "content" not in marks:
                    hint["content"] = "graphic"        # a booklet about attack: its uncaptioned pictures may show it
                needs_description(name, f"{pdf_url}#page={n + 1}&picture={i + 1}", credit,
                                  "Public domain (US government work, 17 U.S.C. 105)", "open",
                                  text=fig["labels"], title=tidy_title(title),
                                  reason="it has no printed caption" if not fig["caption"]
                                  else "its caption is too short or unreadable", extra=hint, page_url=at,
                                  data=fig["jpeg"])
                considered(name, pdf_url, "no caption (set aside for a description)")
                continue
            considered(name, pdf_url, "")
            out.append((name, fig["jpeg"], rows))
    doc.close()
    return out[:most]


def booklet_candidates(s, items=None):
    """The identifiers of the booklets to read: items when given, else BOOKLETS first and then the Archive's search
    (shuffled, so a top-up pass reads others first)."""
    if items:
        return list(items)
    found = [d["identifier"] for d in search(s, BOOKLET_QUERY) if d.get("identifier")]
    pass_random(1950).shuffle(found)
    return list(dict.fromkeys(BOOKLETS + found))


def build_cd_booklets(limit, items=None):
    """Pictures from US civil defense booklets (see the module docstring), at most limit."""
    s, fetched = session(), []
    for identifier in booklet_candidates(s, items):
        if len(fetched) >= limit or listing_out_of_time():
            break
        data = item(s, identifier)
        meta = data.get("metadata") or {}
        page_url = f"{ARCHIVE}details/{identifier}"
        why = booklet_ok(meta) if meta else "not found on the Internet Archive"
        name, size = booklet_pdf(data)
        if not why and not name:
            why = "the item has no PDF"
        if not why and size > BOOKLET_MOST_BYTES:
            why = f"its PDF is too big ({size // 1_000_000} MB)"
        if why:
            considered(identifier, page_url, why)
            say(f"  {identifier}: left out, {why}")
            continue
        pdf_url = f"{ARCHIVE}download/{quote(identifier)}/{quote(name)}"
        folder = tempfile.mkdtemp(prefix="cd-booklet-")
        path = os.path.join(folder, "booklet.pdf")
        try:
            if not download(s, pdf_url, path, BOOKLET_MOST_BYTES):
                considered(identifier, pdf_url, "the PDF could not be downloaded")
                continue
            with open(path, "rb") as f:
                got = booklet_pictures(f.read(), meta, identifier, pdf_url, page_url,
                                       min(BOOKLET_MOST_PICTURES, limit - len(fetched)))
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        say(f"  {identifier}: {len(got)} pictures with captions")
        fetched += got
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- films

FILM_QUERY = ('mediatype:movies AND (collection:prelinger OR collection:FedFlix) AND (subject:"civil defense" OR '
              'title:"civil defense" OR subject:fallout OR title:fallout OR title:shelter OR title:"atomic attack" '
              'OR description:"civil defense")')
# Films checked by hand (November 2026), tried first. Each has a public-domain mark on its item or was made by a US
# federal agency; the builder checks again.
# Films looked at by eye and left out (November 2026), with the reason.
FILMS_LEFT_OUT = {
    "MedicalA1950": "'Medical Aspects of Nuclear Radiation' (1950): shows the ruins of Hiroshima and a newspaper "
                    "headline about sterility and impotence; made for the Air Force's Special Weapons Project, not a "
                    "civil defense film for the public",
}
FILMS = ["DuckandC1951", "Survival1951", "AboutFal1955", "AboutFal1963", "Radiolog1961", "Operatio1964",
         "YourChan1972", "OurCitie1951", "AtomicAl1951", "202269_Occupying_a_Public_Shelter",
         "202267_Planning_Emergence_From_Public_Shelters", "WhattoDo1943", "DayCalle1955", "DayCalle1955_2",
         "gov.ntis.ava11109vnb1"]
FILM_FORMATS = ("512Kb MPEG4", "MPEG4", "h.264", "h.264 IA", "Ogg Video")
FILM_MOST_BYTES = 450_000_000
FILM_MOST_STILLS = 40              # at most this many stills from one film
SKIP_START, SKIP_END = 25.0, 20.0  # seconds of titles and credits at each end
EVERY = 12                         # a still at least every this many seconds, besides each change of scene
SETTLE = 1.0                       # each still is taken this long after its change of scene (at most)
SCENE = 0.25                       # ffmpeg's scene-change score that counts as a new scene
FIXED_MARK_MOST = 0.30             # a film whose burned-in marks or frame lines would cut off more is left out


def film_ok(meta):
    """("" or the reason a film is not used, how it is free): see the module docstring."""
    title = text_of(meta.get("title"))
    words = " ".join([title, text_of(meta.get("description")), text_of(meta.get("subject"))])
    creators = listed(meta.get("creator"))
    licence = text_of(meta.get("licenseurl"))
    if LEAVE_OUT.search(words):
        return "its record names the dead, victims, Hiroshima or Nagasaki, nudity or sex", ""
    if not CD_TOPIC.search(words) or NOT_CD_FILM.search(title):
        return "it is not a civil defense film", ""
    if PD_MARK.search(licence):
        return "", f"public domain (the item's mark: {licence})"
    if NC_ND.search(licence):
        return f"its licence is non-commercial or no-derivatives ({licence})", ""
    if any(FEDERAL.search(c) and not NOT_FEDERAL.search(c) for c in creators):
        return "", f"public domain: made by {creators[0]}, {PD_US}"
    return "no public-domain mark and not made by a US federal agency (Prelinger: 'DO NOT ASSUME')", ""


def film_file(data):
    """(name, size) of a film's video copy to read: the smallest of FILM_FORMATS under FILM_MOST_BYTES."""
    files = [f for f in data.get("files", []) if f.get("format") in FILM_FORMATS
             and 0 < int(f.get("size") or 0) <= FILM_MOST_BYTES]
    files.sort(key=lambda f: (FILM_FORMATS.index(f["format"]), int(f.get("size") or 0)))
    return (files[0]["name"], int(files[0]["size"])) if files else ("", 0)


def film_description(meta):
    """The first sentences (at most 40 words) of a film's own record, or "" when it has fewer than 8 words."""
    text = clean(text_of(meta.get("description")))
    text = re.sub(r"Selected for the \d{4} National Film Registry[^.]*\.\s*", "", text)
    out = build_packs.first_sentences(text, words=40).replace('"', "'")
    return out if len(out.split()) >= 8 else ""


def film_lead(meta):
    """The fixed sentence of a film's stills, from its record: "A still from the 1951 US civil defense film 'Duck and
    Cover', made by Archer Productions, Inc. for the U.S. Federal Civil Defense Administration."."""
    title = tidy_title(text_of(meta.get("title")))
    year = year_of(meta, text_of(meta.get("title")))
    maker = next(iter(listed(meta.get("creator"))), "")
    sponsor = next((x for x in listed(meta.get("sponsor")) if FEDERAL.search(x) or CD_AGENCY.search(x)), "")
    made = ""
    if maker and maker.lower() not in ("none", "unknown"):
        the = "the " if FEDERAL.search(maker) and not maker.lower().startswith("the ") else ""
        made = f", made by {the}{maker}" + (f" for the {sponsor}" if sponsor and sponsor != maker else "")
    elif sponsor:
        made = f", made for the {sponsor}"
    return f"A still from the {str(year) + ' ' if year else ''}US civil defense film '{title}'{made}."


def ffmpeg_stills(video, folder):
    """Stills of a video with ffmpeg, as ([(seconds, path)], the video's length in seconds): first the moments
    where a scene changes (and at least one every EVERY seconds) are found, then each still is taken a little after
    that moment (up to SETTLE seconds, and never past half-way to the next one), so a dissolve from one scene to the
    next is not caught half-way. ([], 0.0) when ffmpeg is missing or fails."""
    if not shutil.which("ffmpeg"):
        say("  ffmpeg is not installed: no film stills (sudo apt-get install -y ffmpeg)")
        return [], 0.0
    chooser = f"select='isnan(prev_selected_t)+gt(scene\\,{SCENE})+gte(t-prev_selected_t\\,{EVERY})',showinfo"
    try:
        done = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info", "-i", video, "-vf", chooser,
                               "-f", "null", "-"], capture_output=True, text=True, timeout=1800)
    except Exception as e:  # noqa: BLE001 - no stills
        say(f"  ffmpeg failed ({type(e).__name__})")
        return [], 0.0
    times = [float(t) for t in re.findall(r"pts_time:\s*([0-9.]+)", done.stderr)]
    length = re.search(r"Duration:\s*(\d+):(\d+):([0-9.]+)", done.stderr)
    length = (int(length.group(1)) * 3600 + int(length.group(2)) * 60 + float(length.group(3))) if length else \
        (times[-1] if times else 0.0)
    out = []
    for i, t in enumerate(times):
        following = times[i + 1] if i + 1 < len(times) else length
        at = t + min(SETTLE, max(0.0, (following - t) / 2))
        path = os.path.join(folder, f"{i:05d}.jpg")
        try:
            subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-ss", f"{at:.2f}", "-i",
                            video, "-frames:v", "1", "-q:v", "3", path], capture_output=True, timeout=120)
        except Exception:  # noqa: BLE001 - that still is skipped
            continue
        if os.path.exists(path):
            out.append((at, path))
    return out, length


def good_stills(stills, length, most):
    """The stills worth keeping: [(seconds, JPEG bytes)] from [(seconds, path)] of a film length seconds long, at most
    most, spread over the film; and what was left out, {reason: count}. A film with a burned-in mark near its edges
    gives none."""
    import numpy as np
    from PIL import Image
    if not stills:
        return [], {}
    looked, left = [], {}
    for t, path in stills:
        if t < SKIP_START or t > length - SKIP_END:
            left["titles and credits"] = left.get("titles and credits", 0) + 1
            continue
        img = Image.open(path).convert("RGB")
        looked.append((t, img))
    if not looked:
        return [], left
    small = [np.asarray(img.convert("L").resize((128, 96))) for _, img in looked]
    top, bottom, side_l, side_r = figures.black_borders(small)
    inner = [g[top:96 - bottom or None, side_l:128 - side_r or None] for g in small]
    cut = figures.fixed_marks(inner)                 # burned-in marks and frame lines near the edges: cut off
    kept_share = (1 - cut[0] - cut[1]) * (1 - cut[2] - cut[3])
    if kept_share < 1 - FIXED_MARK_MOST:
        return [], {"burned-in marks near the edges that cannot be cut off": len(looked)}
    inner_h, inner_w = 96 - top - bottom, 128 - side_l - side_r
    top, bottom = top + round(cut[0] * inner_h), bottom + round(cut[1] * inner_h)
    side_l, side_r = side_l + round(cut[2] * inner_w), side_r + round(cut[3] * inner_w)
    sharp = sorted(figures.sharpness(np.asarray(img.convert("L").resize((320, 240)))) for _, img in looked)
    floor = max(figures.SHARP_LEAST, 0.35 * sharp[len(sharp) // 2])
    kept, prints = [], []
    for t, img in looked:
        w, h = img.size
        crop = img.crop((side_l * w // 128, top * h // 96, w - side_r * w // 128, h - bottom * h // 96))
        gray = np.asarray(crop.convert("L").resize((320, max(2, 320 * crop.size[1] // max(1, crop.size[0])))))
        problem = figures.still_problem(gray, floor)
        if not problem:
            mark = figures.fingerprint(gray)
            if any(figures.distance(mark, p) <= 10 for p in prints):
                problem = "a repeat"
            else:
                prints.append(mark)
        if problem:
            left[problem] = left.get(problem, 0) + 1
            continue
        kept.append((t, crop))
    if len(kept) > most:                                   # spread evenly over the film
        step = len(kept) / most
        kept = [kept[int(i * step)] for i in range(most)]
    out = []
    for t, crop in kept:
        import io
        buffer = io.BytesIO()
        crop.save(buffer, "JPEG", quality=90)
        out.append((t, buffer.getvalue()))
    return out, left


def film_candidates(s, items=None):
    """The identifiers of the films to read: items when given, else FILMS first and then the Archive's search."""
    if items:
        return list(items)
    found = [d["identifier"] for d in search(s, FILM_QUERY) if d.get("identifier")]
    pass_random(1951).shuffle(found)
    return list(dict.fromkeys(FILMS + found))


def build_cd_films(limit, items=None):
    """Stills from US civil defense films (see the module docstring), at most limit pictures."""
    s, fetched, seen_titles = session(), [], set()
    for identifier in film_candidates(s, items):
        if len(fetched) >= limit or listing_out_of_time():
            break
        data = item(s, identifier)
        meta = data.get("metadata") or {}
        page_url = f"{ARCHIVE}details/{identifier}"
        why, licence = film_ok(meta) if meta else ("not found on the Internet Archive", "")
        why = FILMS_LEFT_OUT.get(identifier, why)
        title_key = (tidy_title(text_of(meta.get("title"))).lower(), year_of(meta))
        if not why and title_key in seen_titles:
            why = "another copy of a film already used"
        name, _ = film_file(data)
        if not why and not name:
            why = "no video copy small enough"
        if why:
            considered(identifier, page_url, why)
            say(f"  {identifier}: left out, {why}")
            continue
        seen_titles.add(title_key)
        folder = tempfile.mkdtemp(prefix="cd-film-")
        try:
            video = os.path.join(folder, "film" + os.path.splitext(name)[1])
            url = f"{ARCHIVE}download/{quote(identifier)}/{quote(name)}"
            if not download(s, url, video, FILM_MOST_BYTES):
                considered(identifier, url, "the film could not be downloaded")
                continue
            stills_folder = os.path.join(folder, "stills")
            os.makedirs(stills_folder)
            stills, length = ffmpeg_stills(video, stills_folder)
            kept, left = good_stills(stills, length, min(FILM_MOST_STILLS, limit - len(fetched)))
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        lead, about = film_lead(meta), film_description(meta)
        words = " ".join([text_of(meta.get("title")), text_of(meta.get("description")), text_of(meta.get("subject"))])
        marks = {}
        if GRAPHIC.search(words):
            marks["content"] = "graphic"
        elif MEDICAL.search(words):
            marks["content"] = "medical"
        if CHILD.search(words):
            marks["child"] = True
        credit = f"{tidy_title(text_of(meta.get('title')))}, Internet Archive {page_url}; {licence}"
        base = re.sub(r"[^a-z0-9]+", "_", identifier.lower()).strip("_")[:40]
        answer = lead + (f" The film's catalogue record describes it: \"{about}\"" if about else "")
        for t, jpeg in kept:
            still = f"cdfilm_{base}_{t:07.1f}.jpg"
            if not about:
                needs_description(still, url, credit, licence, "open", title=tidy_title(text_of(meta.get("title"))),
                                  reason="the film's record has no description", extra={"lead": lead,
                                  "seconds": round(t, 1), **marks}, page_url=f"{page_url}?start={int(t)}", data=jpeg)
                continue
            considered(still, url, "")
            fetched.append((still, jpeg, [dict({"question": FROM_Q, "answer": answer, "credit": credit}, **marks)]))
        say(f"  {identifier}: {len(kept)} stills" + (" (set aside: no description)" if not about else "") +
            (f"; left out: {', '.join(f'{v} {k}' for k, v in left.items())}" if left else ""))
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- the packs

CIVIL_DEFENSE_PACKS = {
    "cd_booklets": (build_cd_booklets,
                    "Drawings and photographs from US civil defense booklets, 1950 to 1985 (Federal Civil Defense "
                    "Administration, Office of Civil and Defense Mobilization, Office of Civil Defense, Defense Civil "
                    "Preparedness Agency), with their printed captions; US government works, public domain "
                    "(17 U.S.C. 105). Copies from the Internet Archive, https://archive.org"),
    "cd_films": (build_cd_films,
                 "Stills from US civil defense films, 1950s to 1970s (Prelinger Archives and US government films on "
                 "the Internet Archive), each film public domain by its item's public-domain mark or as a US "
                 "government work (17 U.S.C. 105); answers from each film's own record. https://archive.org"),
}
# How many pictures a full build takes: about 25 booklets with 5 to 40 captioned pictures each, and about 25 films of
# up to 40 stills each.
CIVIL_DEFENSE_LIMITS = {"cd_booklets": 1200, "cd_films": 1200}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one civil defense pack builder.")
    parser.add_argument("key", choices=sorted(CIVIL_DEFENSE_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--items", default="", help="only these Internet Archive identifiers, separated by commas")
    args = parser.parse_args(argv)
    items = [i.strip() for i in args.items.split(",") if i.strip()] or None
    entries = CIVIL_DEFENSE_PACKS[args.key][0](args.limit, items)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    if build_packs.NEEDS:
        say(f"{len(build_packs.NEEDS)} pictures set aside for a description; the first: "
            + json.dumps({k: build_packs.NEEDS[0][k] for k in ("name", "reason", "hints", "content", "child")},
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
