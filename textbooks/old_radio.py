"""Old-time radio scripts for the reference library (the owner's request of 2026-11-22), in their own group
"Reference, old-time radio". TEXT ONLY: no recordings and no speech models. Keys: old-radio (every book),
otr:<name>.

Most scripts of radio's golden age (about 1930 to 1960) are NOT in the public domain. Under the US Copyright Act of
1909 a broadcast was not a "publication", so an unpublished script got federal copyright on 1 January 1978, lasting
at least until the end of 2002 and usually for the writer's life plus 70 years; published scripts of 1931 to 1963 are
free only when their copyright was not renewed, which has to be shown work by work. So this module builds only
scripts that are public domain for a reason that can be checked:
  - works of the US government (17 U.S.C. 105), written and published by federal agencies;
  - and it links to the rest.

What it builds, in plain words:
  - otr:usda_consumer_time: "Consumer Time", the US Department of Agriculture's dramatized consumer programme on NBC
    (1941 to 1947; during the war under the War Food Administration): every script the National Agricultural Library
    put on the Internet Archive (collection usda-consumertime, about 240 scripts), each one page with its title, date,
    network and station line, writers named on the script, and its whole machine-read text. Each item's record must
    name a US government agency as its maker or publisher, and its rights line must say it is not in copyright;
  - otr:usda_farm_home_hour: talks and dramatized features of the National Farm and Home Hour (NBC, 1929 to 1945),
    the USDA's part of it (collection usda-nationalfarmhomehour), one book per piece of years (PIECES), checked the
    same way;
  - otr:wartime_food_radio: the War Food Administration's "Food Makes a Difference" radio scripts (1944 and 1945);
  - otr:owi_radio_war_guide: the Office of War Information's Radio War Guide (July 1943), the government's guide for
    wartime radio programmes (marked public domain on the Internet Archive);
  - otr:americans_all_immigrants_all: the US Office of Education's guide to its twenty-six dramatic broadcasts
    "Americans All, Immigrants All" (CBS, 1938 to 1939);
  - otr:index, "Old-time radio scripts: a guide" (facts and links, CC0): what is built and why, the copyright rules in
    plain words, Voice of America scripts already in the library, and the famous collections as links only: the
    Generic Radio Workshop (it says the scripts "remain ... the copyright of their respective owners"), the Library
    of Congress's radio collections (NBC, the Federal Theatre Project's radio division), the Internet Archive's
    scripts of commercial series, and the published anthologies (such as The Treasury Star Parade, 1942).

Every script was machine-read from typed, mimeographed pages: the text has the scanner's mistakes (OCR_NOTE). The
Consumer Time scripts say on their first page that the script "may not be broadcast without special permission" and
that its title is restricted to network broadcast: that is about broadcasting, not reading; the notice repeats it.
Old scripts also carry the language and views of their time.

Licences: the Internet Archive records (archive.org/metadata/<item>) give the maker, publisher and the National
Agricultural Library's rights line ("The contributing institution believes that this item is not in copyright.");
they are read at every build. The OWI guide carries the Public Domain Mark on the Internet Archive.
archive.org's robots.txt allows the files and its metadata API; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/old_radio.py otr:index --out build/textbooks
  python3 textbooks/old_radio.py otr:usda_consumer_time --out build/textbooks --limit 3
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "oldradio"
GROUPS = {GROUP: "Reference, old-time radio"}

IA = "https://archive.org"
OCR_NOTE = ("Machine-read from typed and mimeographed pages: the text has the scanner's mistakes (wrong letters, "
            "broken lines, speaker names out of place). The scan at the Internet Archive address is the true record. "
            "Old scripts carry the language and views of their time.")
GOV_NOTE = ("A work of the US government (17 U.S.C. 105): public domain in the United States. The contributing "
            "library (the National Agricultural Library) says it believes the item is not in copyright.")
BROADCAST_NOTE = ("The scripts say on their first page that they may not be broadcast without special permission "
                  "and that the title is restricted to network broadcast: that concerns broadcasting, not reading.")
GOV_RIGHTS = r"not in copyright|public domain|no known copyright"
GOV_MAKER = r"United States|U\. ?S\. Department|War Food Administration|Office of War Information"

# The collections read through the Internet Archive's search: name -> (search, title, description, extra notice).
SERIES = {
    "usda_consumer_time": (
        "collection:usda-consumertime AND mediatype:texts",
        "Consumer Time: USDA radio scripts (NBC, 1941 to 1947)",
        "The US Department of Agriculture's weekly dramatized consumer programme on NBC: short plays and talks on "
        "buying, cooking and keeping food, rationing and the Victory Garden in wartime, clothing, household equipment "
        "and the home, each script with its date, network, station and writers.",
        BROADCAST_NOTE),
    "usda_farm_home_hour": (
        "collection:usda-nationalfarmhomehour AND mediatype:texts",
        "The National Farm and Home Hour: USDA radio scripts",
        "The US Department of Agriculture's part of the National Farm and Home Hour on NBC: talks, interviews and "
        "dramatized features for farm families on crops, livestock, plant disease, homemaking and the farm economy.",
        ""),
    "wartime_food_radio": (
        "collection:usda-warfoodadministration AND mediatype:texts AND title:(\"radio script\")",
        "Food Makes a Difference: War Food Administration radio scripts (1944 to 1945)",
        "The War Food Administration's wartime radio scripts \"Food Makes a Difference\", on food, nutrition and "
        "rationing in the Second World War.", ""),
}
# The National Farm and Home Hour in pieces of years (about 530 scripts in all), so no build job runs long.
FARM_PIECES = {"1928-1931": (1928, 1931), "1932-1934": (1932, 1934), "1935-1937": (1935, 1937),
               "1938-1945": (1938, 1945)}
PIECES = {"usda_farm_home_hour": lambda: list(FARM_PIECES)}


def ia_search(query, cache=None, rows=1000):
    """[{identifier, title, date}] of an Internet Archive search, oldest first."""
    import build_textbooks as B
    url = (f"{IA}/advancedsearch.php?q={urllib.parse.quote(query)}&fl[]=identifier&fl[]=title&fl[]=date"
           f"&rows={rows}&output=json&sort[]=date+asc")
    return json.loads(B.fetch(url, cache))["response"]["docs"]


def text_of(meta):
    """A field of an Internet Archive record as one line of text (lists joined)."""
    return "; ".join(meta) if isinstance(meta, list) else str(meta or "")


def government_item(meta):
    """True when an Internet Archive record names a US government agency as maker or publisher and its rights line
    (or licence) says public domain or not in copyright."""
    who = text_of(meta.get("creator")) + " " + text_of(meta.get("publisher"))
    rights = text_of(meta.get("rights")) + " " + text_of(meta.get("possible-copyright-status")) + " " + \
        text_of(meta.get("licenseurl")).replace("publicdomain", "public domain")
    return bool(re.search(GOV_MAKER, who)) and bool(re.search(GOV_RIGHTS, rights, re.I))


def series_book(name, work, cache=None, left_out=None, limit=None):
    """One Internet Archive collection of government radio scripts as a book: one page per script (see the module
    docstring). name may hold a piece of years ("usda_farm_home_hour:1932-1934")."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    base, _, part = name.partition(":")
    query, title, description, extra = SERIES[base]
    if part:
        first, last = FARM_PIECES[part]
        query += f" AND date:[{first}-01-01 TO {last}-12-31]"
        title += f", {part}"
    book = K.new_book(f"otr_{base}" + (f"_{part.replace('-', '_')}" if part else ""), title, "Old-time radio scripts",
                      GROUP, "US Department of Agriculture (scans by the National Agricultural Library)",
                      "Public domain (US government work)", K.US_GOV_URL, f"{IA}/search?query="
                      + urllib.parse.quote(query), description, " ".join(x for x in (GOV_NOTE, extra, OCR_NOTE) if x),
                      changes="each script's machine-read text made into a web page")
    for doc in ia_search(query, cache):
        if limit and len(book.pages) >= limit:
            break
        ident = doc["identifier"]
        try:
            meta = json.loads(B.fetch(f"{IA}/metadata/{ident}", cache))
        except (urllib.error.URLError, OSError, ValueError):
            left_out.append({"title": ident, "reason": "Its record could not be read."})
            continue
        m = meta.get("metadata", {})
        if not government_item(m):
            left_out.append({"title": text_of(m.get("title")) or ident, "reason": "Its record does not show a US "
                             "government maker and a public-domain or not-in-copyright rights line."})
            continue
        txt = next((f["name"] for f in meta.get("files", []) if f["name"].endswith("_djvu.txt")), "")
        if not txt:
            left_out.append({"title": text_of(m.get("title")) or ident, "reason": "No machine-read text."})
            continue
        try:
            text = B.fetch(f"{IA}/download/{ident}/{urllib.parse.quote(txt)}", cache)
        except (urllib.error.URLError, OSError):
            left_out.append({"title": text_of(m.get("title")) or ident, "reason": "Its text could not be read."})
            continue
        head = K.dl([("Title", text_of(m.get("title"))), ("Date", text_of(m.get("date"))),
                     ("Made by", text_of(m.get("creator"))), ("Published by", text_of(m.get("publisher"))),
                     ("Notes", text_of(m.get("description"))), ("Rights", text_of(m.get("rights"))),
                     ("Scan", f"{IA}/details/{ident}")])
        page_title = f"{text_of(m.get('date'))[:10]} {text_of(m.get('title'))}".strip()
        book.pages.append(B.Page(B.slug(f"{page_title} {ident}", 80), page_title, head + K.text_html(text), 0,
                                 text_of(m.get("date"))[:4]))
        book.originals.append({"url": f"{IA}/details/{ident}", "kind": "page"})
    book.published = ""
    return book


def series_sign(name):
    """The weekly sign: the list of the collection's items (a new scan changes it)."""
    base, _, part = name.partition(":")
    query = SERIES[base][0]
    if part:
        first, last = FARM_PIECES[part]
        query += f" AND date:[{first}-01-01 TO {last}-12-31]"
    return K.sha([d["identifier"] for d in ia_search(query)])


def gov_pdf(name, title, archive, year, publisher, description, licence_note):
    """A US government radio document of the Internet Archive as a PDF entry (read whole by pdfdoc_book)."""
    return K.us_pdf(GROUP, name=name, title=title, subject="Old-time radio (government radio)", publisher=publisher,
                    archive=archive, published=str(year), version=f"{year} (Internet Archive item {archive})",
                    description=description, notice=f"{licence_note} {OCR_NOTE}",
                    changes="its scanned pages' machine-read text made into web pages")


PDFS = [
    gov_pdf("owi_radio_war_guide", "Radio War Guide (Office of War Information, July 1943)", "RadioWarGuide", 1943,
            "Office of War Information (and the Office of Facts and Figures), US government",
            "The government's guide for radio stations in the Second World War: the war messages and campaigns "
            "(war news, fighting inflation and more) that stations were asked to work into their programmes.",
            "A work of the US government (17 U.S.C. 105), marked public domain (Public Domain Mark 1.0) on the "
            "Internet Archive."),
    gov_pdf("americans_all_immigrants_all", "Americans All, Immigrants All: the programmes (US Office of Education, "
            "1939)", "americansallimmi00unit", 1939,
            "US Department of the Interior, Office of Education",
            "The Office of Education's guide to its twenty-six dramatic radio broadcasts \"Americans All, Immigrants "
            "All\" (CBS, 1938 to 1939, with the Service Bureau for Intercultural Education and the WPA): each "
            "broadcast's subject (opening frontiers, the English, Hispanic, Black, Irish, German, Jewish and many more "
            "peoples' parts in American life) and books to read.",
            "A work of the US government (17 U.S.C. 105); the US Holocaust Memorial Museum, which scanned it, is "
            "unaware of any copyright restrictions. Its reading lists name books of the 1930s; their words and some "
            "of its own reflect their time."),
]

SECTIONS = [
    ("What is built, and why", "Government radio scripts are public domain in the United States (works of the US "
     "government). Most commercial radio scripts of 1930 to 1960 are still in copyright: a broadcast was not a "
     "publication under the old law, so unpublished scripts got copyright in 1978, usually for the writer's life "
     "plus 70 years; published ones of 1931 to 1963 are free only when their copyright was not renewed.", [
         ("key", "otr:usda_consumer_time", "Consumer Time: USDA dramatized consumer programme (NBC, 1941 to 1947)"),
         ("key", "otr:usda_farm_home_hour:1928-1931", "The National Farm and Home Hour, 1928 to 1931"),
         ("key", "otr:usda_farm_home_hour:1932-1934", "The National Farm and Home Hour, 1932 to 1934"),
         ("key", "otr:usda_farm_home_hour:1935-1937", "The National Farm and Home Hour, 1935 to 1937"),
         ("key", "otr:usda_farm_home_hour:1938-1945", "The National Farm and Home Hour, 1938 to 1945"),
         ("key", "otr:wartime_food_radio", "Food Makes a Difference: War Food Administration scripts"),
         ("key", "otr:owi_radio_war_guide", "Radio War Guide (Office of War Information, 1943)"),
         ("key", "otr:americans_all_immigrants_all", "Americans All, Immigrants All (Office of Education, 1939)")]),
    ("Voice of America", "VOA radio scripts (public domain, US government) are already in the library.", [
        ("word", "pub:voa_history", "Voice of America radio scripts of the 1970s, one book per month")]),
    ("Famous series (links only)", "These collections hold scripts of the commercial series (Suspense, Lux Radio "
     "Theatre, The Shadow, Dragnet, Gunsmoke ...). Their scripts are in copyright unless shown otherwise, so they are "
     "links only: read them on the sites.", [
         ("link", "The Generic Radio Workshop script library", "https://www.genericradio.com/",
          "it says the scripts \"remain ... the copyright of their respective owners\": link only"),
         ("link", "Internet Archive: old-time radio scripts", "https://archive.org/search?query=subject%3A%22radio+"
          "scripts%22", "scripts of commercial series uploaded by collectors (such as the Joe Hehn Memorial "
          "Collection): copyright of their owners unless shown otherwise; link only"),
         ("link", "Library of Congress Recorded Sound Section: radio collections (NBC and others)",
          "https://www.loc.gov/research-centers/recorded-sound/", "scripts kept for research, mostly not online; "
          "copyright of the networks and writers"),
         ("link", "Federal Theatre Project collection (Library of Congress), with its radio division",
          "https://www.loc.gov/collections/federal-theatre-project-1935-to-1939/", "playscripts and programmes of "
          "the WPA's Federal Theatre Project; check each item's rights statement"),
         ("link", "The Treasury Star Parade (1942 anthology)", "https://archive.org/details/treasurystarpara0000will",
          "a commercially published anthology of the Treasury Department's wartime radio scripts; lending-library "
          "copy, copyright status not shown: link only")]),
]
INDEX = X.index_maker("otr", GROUP, "Old-time radio scripts: a guide", "Old-time radio scripts",
                      "A guide to the old-time radio scripts in the library (government radio of the 1920s to 1940s), "
                      "the copyright rules in plain words, and the famous script collections as links.", SECTIONS)
MAKERS = {"index": INDEX, **{name: (series_book, series_sign) for name in SERIES}}

COLLECTION = K.Collection("otr", GROUP, pdfs=PDFS, makers=MAKERS, pieces=PIECES, words={
    "old-radio": lambda: ["otr:index", "otr:usda_consumer_time", "otr:wartime_food_radio"]
    + [f"otr:usda_farm_home_hour:{p}" for p in FARM_PIECES] + [f"otr:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "otr_usda": "Internet Archive records of the National Agricultural Library's USDA radio scripts "
                "(collections usda-consumertime, usda-nationalfarmhomehour, usda-warfoodadministration; read at every "
                "build): creator or publisher \"United States. Department of Agriculture\" (or the War Food "
                "Administration), rights \"The contributing institution believes that this item is not in "
                "copyright.\" US government works (17 U.S.C. 105). archive.org robots.txt allows the files and "
                "metadata; no AI rules (checked 2026-11-22).",
    "otr_owi": "archive.org/metadata/RadioWarGuide: creator Office of Facts and Figures and Office of War "
               "Information, licenseurl Public Domain Mark 1.0 (checked 2026-11-22).",
    "otr_americans_all": "archive.org/metadata/americansallimmi00unit: creator United States Office of Education, "
                         "\"The USHMM is unaware of any copyright restrictions for this item.\" (checked 2026-11-22).",
    "otr_index": "The guide (otr:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Generic Radio Workshop script library (genericradio.com)", "Its home page says: \"We make no claims to ownership "
     "of these materials; they remain, as they should, the copyright of their respective owners\" and \"Individual "
     "scripts may be copyrighted by their owners\"; link-only from otr:index. Index: https://www.genericradio.com/"),
    ("Scripts of commercial radio series (Suspense, Lux Radio Theatre, The Shadow, Li'l Abner, Sky King ...)",
     "Unpublished broadcast scripts got federal copyright in 1978 (usually the writer's life plus 70 years), and "
     "published ones of 1931 to 1963 are free only with evidence of no renewal, which was not found for these; "
     "link-only. Index: https://archive.org/search?query=subject%3A%22radio+scripts%22"),
    ("The Treasury Star Parade (Farrar and Rinehart, 1942) and other anthologies", "Commercially published in 1942 "
     "(copyright renewal not checked) and held only as lending-library scans; link-only. Index: "
     "https://archive.org/details/treasurystarpara0000will"),
    ("Library of Congress radio script collections (NBC collection, Recorded Sound Section)", "Mostly not online, and "
     "the scripts are the networks' and writers' copyright; link-only. Index: "
     "https://www.loc.gov/research-centers/recorded-sound/"),
    ("USDA Radio Service talks (collection usda-usdaradioservice, about 750 items)", "Talks and news letters rather "
     "than radio programmes; not built now (they can be added as another series). Index: "
     "https://archive.org/details/usda-usdaradioservice"),
    ("Recordings of old-time radio", "Text only by the owner's choice (no audio, no speech models). Index: "
     "https://archive.org/details/oldtimeradio"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
