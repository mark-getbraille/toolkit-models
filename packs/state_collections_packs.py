"""Pack builders for US STATE DIGITAL LIBRARIES and the NEWBERRY LIBRARY: everyday pictures of earlier decades and
of today from state libraries, state archives, regional universities, small colleges, historical societies and public
libraries, and the Newberry's postcards, photographs, prints and maps. Landscapes, townscapes, main streets, buildings,
farms, factories, tools, clothing, people at work and daily life, maps and nature. Used by build_packs.py in the same
way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a
row is {"question", "answer", "credit"}, plus "place" where the record names one, "facts" (the holding library, the
collection, the year, the subjects), and "child": true where the words of a picture name a child. A picture with
more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file" names the same
picture (food_packs.with_twins). The limit counts pictures.

WHICH PICTURES. Only items whose OWN rights statement is open: rightsstatements.org "No Copyright - United States"
(NoC-US) or "No Known Copyright" (NKC), the Public Domain Mark, CC0 or CC BY (never share-alike, non-commercial or
no-derivatives), or the same in words ("No Copyright - United States", "No known copyright restrictions", "Public
domain"). An item whose rights statement is open but whose own rights text also restricts use ("Online access is
provided for research purposes only", "permission must be granted by ...", "protected by copyright") is NOT taken:
when the two disagree, the stricter one wins (rights_of). Items with no rights statement at all are never in these
packs; they are the kit's personal-use entry (training-kit/kit/state_collections_personal_sources.py).

THE READERS (reusable for any state library):
  ContentDM   the official CONTENTdm server API (/digital/bl/dmwebservices/index.php, documented by OCLC), which
              every CONTENTdm site's robots.txt allows (they disallow /oai/, /digital/search/ and /utils/, which are
              never used here). Each collection's field list says which fields hold the title, description, rights,
              type, place and date (the Dublin Core mapping); its records are read 100 at a time, paced by the
              site's Crawl-Delay (1 second). Pictures come from the site's IIIF image server (/iiif/2/...).
  oai_records an OAI-PMH reader (ListRecords with resumption tokens, oai_dc), for sites that offer OAI-PMH and do
              not forbid it in robots.txt; its records are made into the same plain fields as ContentDM's, so the
              same rights and safety rules apply (rights_of reads rightsstatements.org addresses and words alike).
  dlg_records the Digital Library of Georgia's documented JSON API (dlg.usg.edu/about/api), filtered by its rights
              facet (NoC-US, NKC, CC BY).
  newberry    the Newberry Library's Orange Logic search API (collections.newberry.org/API/search/v3.0, answering
              anonymous readers; its robots.txt asks 5 seconds between requests and forbids only /Share/), filtered
              by "Rights Status: No Copyright - United States".
Every host's robots.txt is read before it is used (RobotsGuard): a host that blocks AI crawlers (ClaudeBot, GPTBot,
CCBot, anthropic-ai) or says "ai-train=no" is not read, an address its robots forbid is not fetched, and its
Crawl-Delay is kept.

Every answer is the library's own words: "Describe this picture." with the record's title and description (catalogue
fields, web addresses, credit lines and the collection's boilerplate sentences taken out: a sentence shared by many
records of a collection is about the collection, not the picture), and "Where was this photo taken?" for a photograph
whose record names a US place. Nothing is written by an AI model and nothing is guessed. A picture that passes every
check but has only a title, or words too short to describe it, is set aside for a description
(build_packs.needs_description), keeping its marks.

Safety (packs/SOURCE-RULES.md), the museum packs' screens: no nudity, swimwear or sexual content (an item whose words
name nudity is never in these packs; the Newberry's public-domain nudes in art go to museum_art_nudes through
adult_art_packs.newberry_nudes and its own rules); no crime, arrests, prisons, executions or victims; no violence or
atrocity pictures (the dead or injured, lynchings, massacres, riots, the Klan: left out, not marked); no portraits,
yearbooks, team or class photos of named people (privacy); no camps, youth programmes or school pupils whose age the
record does not give; no official events; no old slurs; and no American Indian or Indigenous material, whose cultural
restrictions (Traditional Knowledge labels) an open rights statement does not settle. Every row whose words name a
child is marked "child". All four packs show people and are never used for picture-making (the kit's
PEOPLE_AND_BODILY_PACK_KEYS).

The packs (all open; every source checked at the source on 19 November 2026):
  newberry_library        The Newberry Library, Chicago: postcards (with item-by-item picture descriptions), photographs,
                          prints, drawings, posters and maps whose Rights Status is "No Copyright - United States"
                          (the Newberry's open-access policy: "any lawful purpose, commercial or non-commercial").
  state_libraries_midwest Ohio Memory (Ohio History Connection and Ohio libraries), Ball State University's Digital
                          Media Repository (Indiana), the Illinois Digital Archives (Illinois State Library), Ohio
                          University Libraries, UW-Milwaukee Libraries and Digital Horizons (North Dakota and
                          Minnesota): their open collections, found by the reader.
  state_libraries_south   The Digital Library of Georgia (GALILEO: Georgia's colleges, archives and libraries), the
                          Kentucky Digital Library, Auburn University Libraries, the Alabama Department of Archives
                          and History, and Digital Maryland (Enoch Pratt Free Library and Maryland's libraries).
  state_libraries_west    Washington State University Libraries, the University of New Mexico's New Mexico Digital
                          Collections and Northern Arizona University's Colorado Plateau Digital Archives (their
                          non-Indigenous open collections).

Looked at and NOT made into packs (the reasons are in training-kit/kit/state_collections_personal_sources.py,
STATE_COLLECTIONS_NOT_INCLUDED): the Indianapolis Museum of Art at Newfields, the Denver Art Museum, the Dallas Museum
of Art, the Saint Louis Art Museum and the Hammer Museum (CC0 or public-domain images, but no official API, IIIF
listing or bulk data: only their websites' own search, which Denver's robots.txt forbids); DigitalNC, the Connecticut
Digital Archive and FIU dPanther (bot challenges); Montana Memory (answers every request with 429); the Mountain
West Digital Library (a Primo portal with no open API; its members' own sites are read where they allow it); UF
Digital Collections (its old OAI-PMH address now serves the new website; no API reached); Utah State University (moved
to Preservica); the CONTENTdm sites OCLC hosts (*.contentdm.oclc.org: New York Heritage, the Tennessee Virtual
Archive, Missouri Digital Heritage), which answered with a Cloudflare challenge on 19 November 2026 (the reader stops
at a site that refuses three requests in a row). The Library of Congress, NARA, NYPL, Digital Commonwealth and DPLA are other packs' sources.

    python packs/state_collections_packs.py newberry_library --limit 8      (prints a few rows: a quick check)
"""

import collections
import json
import re
import sys
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from build_packs import fetch_all, new_only, USER_AGENT
from food_packs import with_twins, count_pictures, sentence
from expression_packs import CHILD
from university_packs import left_out_because, marked, long_enough, record_text, iiif_image
from us_modern_packs import GRAPHIC
from us_packs import DESCRIBE_Q
from places import where, place_name

WHERE_Q = "Where was this photo taken?"
OPEN_CATEGORY = "open"

# ----------------------------------------------------------------- rights

# The rights addresses that make an item open, and the names said in its credit.
OPEN_URI = re.compile(r"(rightsstatements\.org/(vocab|page)/(NoC-US|NKC)/|creativecommons\.org/publicdomain/"
                      r"(mark|zero)/|creativecommons\.org/licenses/by/\d)", re.I)
# Rights addresses that are not open (in copyright, other restrictions, share-alike, non-commercial, no-derivatives).
CLOSED_URI = re.compile(r"(rightsstatements\.org/(vocab|page)/(InC|NoC-CR|NoC-NC|NoC-OKLR|CNE|UND)|"
                        r"creativecommons\.org/licenses/by-(sa|nc|nd))", re.I)
# Open statements in words (a rights field with no address).
OPEN_TEXT = re.compile(r"\b(no copyright\W+united states|no known copyright( restrictions)?|"
                       r"(is|are|in) (in )?the public domain|^\W*public domain\b|copyright is in public domain|"
                       r"\bcc0\b|public domain mark)", re.I)
# Words of a rights text that restrict use: they win over an open address on the same item.
RESTRICTED = re.compile(r"(research purposes only|for (research|study|scholarly|educational) (use|purposes)|"
                        r"private study|personal use|non-?commercial|educational use only|"
                        r"(?<!no )permission (is |must be )?(required|needed|granted)|permission (to|for) "
                        r"(publish|reproduce|use|publication)|requests? for permission|written permission|"
                        r"must be (granted|obtained)|protected by copyright|\bin copyright\b|all rights reserved|"
                        r"copyright (is )?(held|owned|retained) by|may not be (used|reproduced|published|copied)|"
                        r"©|\(c\) ?\d{4})", re.I)
# The restrictions that still allow research and private study (the kit's personal-use "research" group).
RESEARCH_ONLY = re.compile(r"(research purposes only|for (research|study|scholarly|educational) (use|purposes)|"
                           r"research, teaching,? and private study|private study|educational use only)", re.I)
RIGHTS_NAMES = (("NoC-US", "No Copyright - United States (rightsstatements.org)"),
                ("NKC", "No Known Copyright (rightsstatements.org)"),
                ("publicdomain/mark", "Public Domain Mark"), ("publicdomain/zero", "CC0"))


def rights_name(text):
    """The open statement of an item in words, for its credit ("No Copyright - United States (rightsstatements.org)",
    "CC BY 4.0", "Public domain" ...)."""
    for part, name in RIGHTS_NAMES:
        if part.lower() in text.lower():
            return name
    m = re.search(r"licenses/by/(\d\.\d)", text)
    if m:
        return f"CC BY {m.group(1)}"
    m = OPEN_TEXT.search(text)
    if m:
        words = m.group(0).strip(" .").lower()
        if "no copyright" in words:
            return "No Copyright - United States"
        if "no known" in words:
            return "No known copyright restrictions"
        return "Public domain"
    return text[:80]


def rights_of(values):
    """(kind, name, reason) of an item's rights fields (addresses and words alike). kind is "open" (the item may go
    into a pack: name says its statement), "none" (no rights statement at all), "research" (its words allow research
    or private study only: the kit's personal-use group) or "closed" (in copyright, permission needed, or not open).
    An open address with restricting words on the same item is not open: the stricter wins."""
    texts = [clean(v) for v in values if clean(v)]
    joined = " | ".join(texts)
    if not texts:
        return "none", "", "no rights statement"
    if CLOSED_URI.search(joined):
        return "closed", "", f"its rights statement is not open ({CLOSED_URI.search(joined).group(0)})"
    restricted = RESTRICTED.search(joined)
    if restricted:
        if RESEARCH_ONLY.search(joined) and not re.search(r"protected by copyright|\bin copyright\b|all rights "
                                                          r"reserved|must be (granted|obtained)|written permission",
                                                          joined, re.I):
            return "research", "", f"its rights text allows research or study only ({restricted.group(0)})"
        return "closed", "", f"its rights text restricts use ({restricted.group(0)})"
    if OPEN_URI.search(joined) or OPEN_TEXT.search(joined):
        return OPEN_CATEGORY, rights_name(joined), ""
    return "closed", "", f"its rights statement is not an open one ({joined[:80]})"


# ----------------------------------------------------------------- safety and description

# Violence and atrocity: never in these packs (left out, not marked), beyond university_packs' own screens.
VIOLENCE = re.compile(r"\b(lynch\w*|massacre\w*|atrocit\w*|riots?|rioters?|mobs?|ku klux|klans?\w*|kkk|"
                      r"hanged|hangings?|gallows|executions?|executed|scaffold|murder\w*|slain|assassinat\w*|"
                      r"battlefield dead|wreck victims?|disaster victims?|torture\w*|beaten|beating)\b", re.I)
# American Indian and Indigenous material: left out (cultural restrictions, Traditional Knowledge labels).
INDIGENOUS = re.compile(r"\b(american indians?|native americans?|indigenous|first nations?|tribes?|tribal|"
                        r"indian (reservations?|agency|schools?|territory|tribes?|chiefs?|dances?|villages?|camps?)|"
                        r"pueblos?|navajo|din[eé]|hopi|zuni|apache|lakota|dakota (sioux|people)|sioux|ojibwe?|"
                        r"chippewa|cherokee|choctaw|chickasaw|creek indians|muscogee|seminole|shawnee|miami indians|"
                        r"potawatomi|ho-chunk|winnebago|menominee|oneida|mohawk|seneca|onondaga|iroquois|"
                        r"haudenosaunee|blackfeet|crow indians|cheyenne|arapaho|nez perce|yakama|salish|"
                        r"kootenai|shoshone|paiute|ute indians|osage|kiowa|comanche|pawnee|omaha indians|"
                        r"mandan|hidatsa|arikara|assiniboine|aleut|inupiat|yupik|tlingit|ayer collection)\b", re.I)
# Records that are not pictures (documents, pages of books and newspapers, recordings).
NOT_A_PICTURE = re.compile(r"\b(text|texts|newspapers?|letters?|correspondence|ledgers?|deeds?|minutes|"
                           r"typescripts?|manuscripts?|pamphlets?|books?|periodicals?|journals?|diar(y|ies)|"
                           r"yearbooks?|directories|directory|catalogs?|catalogues?|programs?|programmes?|"
                           r"transcripts?|oral histor\w*|sound|audio|moving ?image|video|film|reports?|"
                           r"certificates?|documents?|records|forms?|receipts?|invoices?|bills?|tickets?)\b", re.I)
# A record whose title or description says it is a document (a letter, an article, a menu ...), even when the site
# files it as a still image: a scan of text is not a picture to describe.
DOCUMENT = re.compile(r"(^\W*(letters?|telegrams?|memo(randum|s)?|newspapers?|(newspaper )?articles?|clippings?|"
                      r"menus?|programs?|receipts?|minutes|reports?|invoices?|certificates?|deeds?|ledgers?|"
                      r"typescripts?|manuscripts?|transcripts?|lists?|forms?|pages?|diar(y|ies)|notes|"
                      r"press releases?|statements?|speech(es)?|announcements?|resolutions?|petitions?)\b|"
                      r"\b(letters? (to|from|written)|newspaper articles?|(breakfast|dinner|supper) menus?|"
                      r"press releases?)\b)", re.I)
PHOTO_WORDS = re.compile(r"\b(photo\w*|postcards?|post cards?|negatives?|slides?|glass plates?|snapshots?|"
                         r"stereographs?|lantern slides?|prints?, photographic|gelatin silver|albumen|cyanotype)\b",
                         re.I)
# A collection whose name says it is not about pictures (newspapers, yearbooks, oral histories ...), or about
# American Indian or Indigenous peoples: its records are not read at all.
SKIP_COLLECTION = re.compile(r"\b(newspapers?|gazette|herald|courier|times|tribune|journal|yearbooks?|annuals?|"
                             r"oral histor\w*|minutes|directories|directory|catalogs?|bulletins?|newsletters?|"
                             r"theses|dissertations?|obituar\w*|sandbox|test|census|deeds?|ledgers?|"
                             r"scrapbooks?|interviews?|recordings?|audio|video|sound)\b", re.I)


def why_left_out(words, year=0):
    """Why an item is left out by its words ("" when it may be taken): university_packs' screens (nudity,
    swimwear, crime, privacy, minors, official events, slurs), violence and atrocity (VIOLENCE, us_modern_packs.GRAPHIC:
    the dead and injured are left out here, not marked), and American Indian or Indigenous material (INDIGENOUS)."""
    reason = left_out_because(words, year, modern=False)
    if reason:
        return reason
    if VIOLENCE.search(words) or GRAPHIC.search(words):
        return "its words are about violence, death or injury (no atrocity pictures)"
    if INDIGENOUS.search(words):
        return "American Indian or Indigenous material (cultural restrictions; left out)"
    return ""


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n\s*\n|\s{3,}")


def sentences(text):
    """The sentences of a text (paragraph breaks and wide gaps count as sentence ends)."""
    return [" ".join(s.split()) for s in SENTENCE_SPLIT.split(str(text or "")) if s and s.strip()]


def shared_sentences(texts, least=3, share=0.2):
    """The sentences that many texts of one collection have in common (at least least of them and share of all):
    they describe the collection, not the picture ("The Ewing Collection consists of 5,055 glass plate negatives.")."""
    texts = [t for t in texts if t]
    counts = collections.Counter(s for t in texts for s in set(sentences(t)))
    return {s for s, n in counts.items() if n >= least and n >= share * len(texts)}


# Catalogue notes that are not about what the picture shows: the back of a postcard, postmarks, dating notes,
# transcriptions and digitization notes.
NOT_THE_PICTURE = re.compile(r"^(addressed\b|postmark|postmarked|date (from|approximated|taken)|dated from|"
                             r"transcri(bed|ption)|note:|notes?:|this item was digitized|digitized\b|digitization|"
                             r"written on (the )?(back|verso)|on (the )?(back|verso)\b|verso\b|message on|"
                             r"stamp(ed)? on|publisher'?s? (number|no)|card (number|no)|caption reads|"
                             r"\"?photo only copyrighted|detached from|uniform title|at head of title|scale\b|"
                             r"\W*(1|one) maps?\b|pt\. \d)|\b\d+(\.\d+)? ?x ?\d+(\.\d+)? ?(cm|in)\b|\bhand col\b",
                             re.I)


def own_words(text, shared):
    """A description without its collection's shared sentences and without notes about the back of the item, its
    dating or its digitization (NOT_THE_PICTURE)."""
    return " ".join(s for s in sentences(text) if s not in shared and not NOT_THE_PICTURE.search(s)
                    and re.search(r"[A-Za-z]{3,}", s))          # not a leftover "Pt." or "2, no."


def year_of(*values):
    """The first year (1800-2099) in a record's date fields; 0 when none."""
    for v in values:
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", str(v or ""))
        if m:
            return int(m.group(1))
    return 0


STATES = ("Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
          "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
          "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
          "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
          "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
          "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
          "District of Columbia")
# The abbreviations library catalogues use for the states ("Athens (Ga.)", "Washington, N.C.").
STATE_ABBREVIATIONS = {
    "ala": "Alabama", "ariz": "Arizona", "ark": "Arkansas", "calif": "California", "colo": "Colorado",
    "conn": "Connecticut", "del": "Delaware", "d.c": "District of Columbia", "fla": "Florida", "ga": "Georgia",
    "ill": "Illinois", "ind": "Indiana", "kan": "Kansas", "kans": "Kansas", "ky": "Kentucky", "la": "Louisiana",
    "me": "Maine", "md": "Maryland", "mass": "Massachusetts", "mich": "Michigan", "minn": "Minnesota",
    "miss": "Mississippi", "mo": "Missouri", "mont": "Montana", "neb": "Nebraska", "nebr": "Nebraska",
    "nev": "Nevada", "n.h": "New Hampshire", "n.j": "New Jersey", "n.m": "New Mexico", "n. mex": "New Mexico",
    "n.y": "New York", "n.c": "North Carolina", "n.d": "North Dakota", "n. dak": "North Dakota", "okla": "Oklahoma",
    "or": "Oregon", "oreg": "Oregon", "pa": "Pennsylvania", "r.i": "Rhode Island", "s.c": "South Carolina",
    "s.d": "South Dakota", "s. dak": "South Dakota", "tenn": "Tennessee", "tex": "Texas", "vt": "Vermont",
    "va": "Virginia", "wash": "Washington", "w. va": "West Virginia", "w.va": "West Virginia", "wis": "Wisconsin",
    "wisc": "Wisconsin", "wyo": "Wyoming"}
US_STATE = re.compile(r"\b(" + "|".join(STATES) + r")\b")
NOT_A_TOWN = re.compile(r"\b(county|counties|region|river|creek|mountains|street|avenue|road|"
                        r"united states|north america|u\.s|usa)\b|^\d|^-?\d+(\.\d+)?$", re.I)


def state_named(part):
    """The state a place part names in full or as a catalogue abbreviation ("N.C.", "Ga", "Ohio"), else ""."""
    part = " ".join(part.split()).strip(" .()")
    if part in STATES:
        return part
    return STATE_ABBREVIATIONS.get(part.lower().rstrip("."), "")


def us_place(*values):
    """A US place from a record's PLACE fields, in the forms catalogues write them: "Athens (Ohio)", "Washington,
    N.C.", "United States, Georgia, Clarke County, Athens, 33.96, -83.37", "Bismarck, North Dakota", or a subject
    heading "Streets--North Carolina--Washington": "Athens, Ohio, USA". The town is the part next to the state (before
    it, or after it in a subject heading), never a county, river or street; "" when no US state is named."""
    pieces = []
    for value in values:
        for text in (value if isinstance(value, list) else [value]):
            text = str(text or "")
            pieces += text.split(";")
    for text in pieces:
            text = clean(text)
            if not text or "." in text.split(",")[0] and "Models" in text:
                continue                                  # software noise ("DigitalOai.Models.GenericLabelNode")
            m = re.match(r"^(.*?)\s*\(([^()]+)\)\s*$", text)        # "Athens (Ga.)", "X (Emmitsburg, Md.)"
            if m:
                outer, inner = m.group(1).strip(), [p.strip() for p in m.group(2).split(",")]
                if inner == ["State"] and state_named(outer):
                    return place_name(state_named(outer), "USA")             # "Washington (State)"
                if state_named(inner[-1]):
                    town = inner[-2] if len(inner) > 1 else outer
                    town = "" if not town or NOT_A_TOWN.search(town) or state_named(town) else town
                    return place_name(town, state_named(inner[-1]), "USA")
            if "--" in text:                                                   # a subject heading
                parts = [re.sub(r"\s*\(State\)$", "", p.strip(" .")) for p in text.split("--")]
                for i, p in enumerate(parts):
                    if state_named(p):
                        town = parts[i + 1] if i + 1 < len(parts) else ""
                        town = "" if NOT_A_TOWN.search(town) or not town[:1].isupper() else town
                        return place_name(town, state_named(p), "USA")
                continue
            parts = [p.strip(" ()") for p in re.split(r"[;,]", text) if p.strip(" .()")]
            for i, p in enumerate(parts):
                state = state_named(p)
                if not state:
                    continue
                if state == "Washington" and i + 1 < len(parts) and state_named(parts[i + 1]):
                    continue                                                   # "Washington, N.C.": the town
                before = parts[i - 1] if i > 0 else ""
                after = parts[i + 1] if i + 1 < len(parts) else ""
                town = before if before and not NOT_A_TOWN.search(before) and \
                    (not state_named(before) or before == "Washington") else ""
                if not town and re.search(r"united states|usa", " ".join(parts[:i]), re.I):
                    later = [q for q in parts[i + 1:] if not NOT_A_TOWN.search(q) and not state_named(q)]
                    town = later[0] if later else ""                          # "United States, Georgia, ..., Athens"
                return place_name(town, state, "USA")
    return ""


def item_rows(item):
    """The rows of one picture: "Describe this picture." with its library's words, and "Where was this photo
    taken?" for a photograph whose record names a US place. Marked "child" where its words name a child."""
    facts = {"holding_library": item.get("library"), "collection": item.get("collection"),
             "year": item.get("year") or None, "subjects": item.get("subjects") or None}
    facts = {k: v for k, v in facts.items() if v}
    place = item.get("place", "")
    rows = [{"question": DESCRIBE_Q, "answer": item["answer"], "credit": item["credit"], "facts": facts,
             **where(place)}]
    if place and item.get("photo"):
        rows.append({"question": WHERE_Q, "answer": f"It was taken in {place}.", "credit": item["credit"],
                     **where(place)})
    return marked(rows, item["words"])


def judge(item, rights_values, items, answers, key):
    """Decide one candidate (a dict with name, url, title, description, words, year, ...): left out with its reason
    (considered), set aside for a description (needs_description), or added to items as (name, url, rows). Returns
    "taken", "needs" or the reason it was left out. rights_values: the item's rights fields."""
    kind, name, reason = rights_of(rights_values)
    if kind != OPEN_CATEGORY:
        considered(item["name"], item["page"], reason)
        return reason
    item["licence"] = name
    reason = why_left_out(item["words"], item.get("year", 0))
    if reason:
        considered(item["name"], item["page"], reason)
        return reason
    if DOCUMENT.search(item["title"]) or DOCUMENT.search(item.get("description", "")[:200]):
        considered(item["name"], item["page"], "a document (a letter, an article, a menu ...), not a picture")
        return "a document"
    if not item.get("url"):
        considered(item["name"], item["page"], "no picture address (a document or a multi-page item)")
        return "no picture"
    item["credit"] = item["credit"].replace("{licence}", name)
    answer = record_text(item["title"], [item["description"]] if item.get("description") else [])
    item["answer"] = answer
    if not long_enough(answer, item["title"], name_ok=True) or answer in answers or \
            not item.get("description") or len(item["description"].split()) < 4:
        needs_description(item["name"], item["url"], item["credit"], name, category=OPEN_CATEGORY,
                          text=item.get("description", ""), title=item["title"], place=item.get("place", ""),
                          reason="only a title, or words too short to describe the picture",
                          page_url=item["page"],
                          extra={"subjects": item.get("subjects"), "year": item.get("year"),
                                 "holding_library": item.get("library"), "collection": item.get("collection"),
                                 "child": bool(CHILD.search(item["words"])), "not_for_picture_making": True})
        return "needs"
    answers.add(answer)
    items.append((item["name"], item["url"], item_rows(item)))
    return "taken"


# ----------------------------------------------------------------- robots.txt

AI_CRAWLERS = re.compile(r"^(claudebot|claude-web|anthropic-ai|gptbot|ccbot|google-extended)$", re.I)
OUR_AGENT = re.compile(r"^picturemodeltrainingkit", re.I)


def robots_groups(text):
    """The groups of a robots.txt: [(user agents in lower case, [(rule, path)])], with "crawl-delay" kept as a rule.
    Several User-agent lines in a row share one group (RFC 9309)."""
    groups, agents, rules = [], [], []
    for line in str(text or "").splitlines():
        key, _, value = line.split("#")[0].partition(":")
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif key in ("allow", "disallow", "crawl-delay") and agents:
            rules.append((key, value))
    if agents:
        groups.append((agents, rules))
    return groups


def robots_rule_matches(rule, path):
    """Whether a robots.txt path rule matches a path with its query ("/records.json?page=2"), as RFC 9309 says: a
    prefix match, "*" for any characters and "$" for the end. (Python's urllib.robotparser drops a trailing "?" from
    a rule, so "Disallow: /records?" there wrongly forbids "/records.json"; this does not.)"""
    pattern = "".join(".*" if c == "*" else re.escape(c) for c in rule.rstrip("$"))
    return bool(re.match(pattern + ("$" if rule.endswith("$") else ""), path))


def robots_verdict(groups, path):
    """(allowed, crawl delay) of a path for this kit: the group naming our agent, else the "*" group; the longest
    matching rule wins, Allow winning a tie; no matching rule allows."""
    mine = [g for g in groups if any(OUR_AGENT.match(a) for a in g[0])] or [g for g in groups if "*" in g[0]]
    rules = [r for g in mine for r in g[1]]
    best, allowed = -1, True
    for key, value in rules:
        if key in ("allow", "disallow") and value and robots_rule_matches(value, path):
            if len(value) > best or (len(value) == best and key == "allow"):
                best, allowed = len(value), key == "allow"
    delays = [float(v) for k, v in rules if k == "crawl-delay" and re.fullmatch(r"\d+(\.\d+)?", v)]
    return allowed, max(delays) if delays else 0.0


class RobotsGuard:
    """Reads each host's robots.txt once (through the build's session) and answers whether an address may be
    fetched: not when robots.txt forbids it for this kit (or for all agents), not on a host that blocks AI crawlers
    or says "ai-train=no", and not when the robots.txt could not be read (refused or a server error). delay() is the
    host's Crawl-Delay (at least the given least). A host with no robots.txt (404) may be read."""

    def __init__(self, s=None, fetch=None):
        """s: a requests session; fetch: a function host -> robots text, "" for none, or None (for the tests)."""
        self.s, self.fetch, self.hosts, self.lock = s, fetch, {}, threading.Lock()

    def _text(self, host):
        """The robots.txt of host ("" when there is none; None when it could not be read)."""
        if self.fetch:
            return self.fetch(host)
        try:
            r = (self.s or session()).get(f"https://{host}/robots.txt", timeout=30)
        except Exception:  # noqa: BLE001 - not readable: not read (as a server error)
            return None
        if r.status_code in (401, 403, 429) or r.status_code >= 500:
            return None
        if r.status_code != 200 or "<html" in r.text[:300].lower():
            return ""
        return r.text

    def _host(self, host):
        """(groups or None, blocked reason) of one host, read once."""
        with self.lock:
            if host not in self.hosts:
                text = self._text(host)
                if text is None:
                    self.hosts[host] = (None, "its robots.txt could not be read (refused or a server error)")
                else:
                    groups = robots_groups(text)
                    blocked = ""
                    if re.search(r"ai-train\s*=\s*no", text, re.I):
                        blocked = "its robots.txt says ai-train=no"
                    elif any(any(AI_CRAWLERS.match(a) for a in agents) and ("disallow", "/") in rules
                             for agents, rules in groups):
                        blocked = "its robots.txt blocks AI crawlers"
                    self.hosts[host] = (groups, blocked)
            return self.hosts[host]

    def allowed(self, url):
        """("", delay) when url may be fetched, else (the reason, 0)."""
        parts = urllib.parse.urlparse(url)
        groups, blocked = self._host(parts.netloc)
        if groups is None or blocked:
            return blocked or "its robots.txt could not be read", 0
        ok, delay = robots_verdict(groups, (parts.path or "/") + (f"?{parts.query}" if parts.query else ""))
        return ("", delay) if ok else ("its robots.txt forbids this address", 0)

    def delay(self, url, least=0.0):
        """The Crawl-Delay of url's host, at least least seconds."""
        groups, _ = self._host(urllib.parse.urlparse(url).netloc)
        return max(least, robots_verdict(groups or [], "/")[1])


class Pacer:
    """Waits so that requests to one host are at least pause seconds apart (several threads may share it)."""

    def __init__(self, pause):
        """pause: the seconds between requests."""
        self.pause, self.last, self.lock = pause, 0.0, threading.Lock()

    def wait(self):
        """Sleep until the next request may be made."""
        with self.lock:
            wait = self.last + self.pause - time.time()
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()


def get_json(s, url, pacer=None, tries=3, params=None):
    """The JSON at url (paced), trying again on a busy server (429, 5xx) or a dropped connection; None when it never
    came."""
    for attempt in range(tries):
        if pacer:
            pacer.wait()
        try:
            r = s.get(url, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (400, 401, 403, 404, 410):
                return None
            after = r.headers.get("Retry-After", "")
            time.sleep(min(int(after), 120) if after.isdigit() else 5 * (attempt + 1))
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(5 * (attempt + 1))
    return None


# ----------------------------------------------------------------- CONTENTdm

IMAGE_FILES = ("jp2", "jpg", "jpeg", "tif", "tiff", "png", "gif")


def field_roles(fields):
    """{role: [field nicknames]} of a CONTENTdm collection's field list (dmGetCollectionFieldInfo), by the Dublin
    Core each field is mapped to and its name: title, description, rights (every field mapped to rights or named
    "Rights ..."), type, format, subject, place, date, creator, contributor, publisher."""
    roles = collections.defaultdict(list)
    for f in fields or []:
        nick, dc, name = str(f.get("nick") or ""), str(f.get("dc") or ""), str(f.get("name") or "").lower()
        if not nick:
            continue
        if dc == "rights" or "right" in name:
            roles["rights"].append(nick)
        elif dc == "title" and not roles["title"]:
            roles["title"].append(nick)
        elif dc == "descri" or (dc == "BLANK" and name in ("description", "caption", "summary")):
            roles["description"].append(nick)
        elif dc == "type":
            roles["type"].append(nick)
        elif dc.startswith("format") or name in ("format", "medium", "genre"):
            roles["format"].append(nick)
        elif dc == "subjec":
            roles["subject"].append(nick)
        elif dc in ("coveraa", "covera") or re.search(r"\b(place|location|spatial|geographic)", name):
            roles["place"].append(nick)
        elif dc in ("date", "coverab") and "date" in name:
            roles["date"].append(nick)
        elif dc == "creato":
            roles["creator"].append(nick)
        elif dc in ("contri", "publis") or re.search(r"(contributing|holding|repository|institution)", name):
            roles["library"].append(nick)
    return roles


class ContentDM:
    """The official CONTENTdm server API of one site (https://<host>/digital/bl/dmwebservices/index.php), paced by its
    Crawl-Delay (at least pause seconds). name: the site's name in credits ("Ohio Memory")."""

    def __init__(self, host, name, s=None, pause=1.0, robots=None, prefix=""):
        """host: "ohiomemory.org"; name: its name; s: a requests session; robots: a RobotsGuard."""
        self.host, self.name, self.s = host, name, s or session()
        self.robots = robots or RobotsGuard(self.s)
        self.base = f"https://{host}/digital/bl/dmwebservices/index.php"
        self.pacer = Pacer(self.robots.delay(self.base, pause))
        self.prefix = prefix or re.sub(r"[^a-z0-9]+", "", host.split(".")[0].lower())[:12]
        self.failures = 0               # API calls in a row that came to nothing

    def api(self, query):
        """One API call ("dmGetCollectionList", "dmQuery/..."): its JSON, or None."""
        why, _ = self.robots.allowed(self.base)
        if why or self.failures >= 3:
            return None
        got = get_json(self.s, f"{self.base}?q={query}/json", self.pacer)
        self.failures = 0 if got is not None else self.failures + 1
        if self.failures == 3:          # refused three times running (a bot challenge, a block): stop reading it
            say(f"{self.name}: three requests in a row refused or unanswered; this site is not read further")
        return got

    def collections(self):
        """[(alias, name)] of the site's collections (aliases without the slash)."""
        return [(str(c.get("alias") or "").strip("/"), clean(c.get("name")))
                for c in self.api("dmGetCollectionList") or [] if c.get("alias")]

    def roles(self, alias):
        """The field roles of a collection (field_roles)."""
        return field_roles(self.api(f"dmGetCollectionFieldInfo/{alias}") or [])

    def records(self, alias, roles, start=1, count=100):
        """(records, total) of a collection from record start (1-based): each record a dict of its fields, with
        "pointer" and "filetype"."""
        nicks = list(dict.fromkeys(n for r in ("title", "description", "rights", "type", "format", "subject",
                                               "place", "date", "creator", "library") for n in roles.get(r, [])[:3]))
        fields = "!".join(nicks[:20]) or "title"
        data = self.api(f"dmQuery/{alias}/0/{fields}/nosort/{count}/{start}/0/0/0/0/0/0") or {}
        total = int((data.get("pager") or {}).get("total") or 0)
        return data.get("records") or [], total

    def picture(self, alias, pointer):
        """The IIIF address of a single-picture record, at most 2048 pixels."""
        return f"https://{self.host}/iiif/2/{alias}:{pointer}/full/!2048,2048/0/default.jpg"

    def page(self, alias, pointer):
        """The record's web page."""
        return f"https://{self.host}/digital/collection/{alias}/id/{pointer}"


def cdm_value(record, roles, role):
    """A record's text for one role (its fields joined; CONTENTdm gives an empty dict for an empty field)."""
    out = []
    for nick in roles.get(role, []):
        v = record.get(nick)
        if isinstance(v, str) and v.strip():
            out.append(v.strip())
    return "; ".join(out)


def cdm_candidate(site, alias, collection, roles, record, shared):
    """The candidate dict of one CONTENTdm record (see judge), and its rights values."""
    pointer = record.get("pointer")
    title = clean(cdm_value(record, roles, "title"))
    description = clean(own_words(cdm_value(record, roles, "description"), shared))
    kind = clean(" ".join([cdm_value(record, roles, "type"), cdm_value(record, roles, "format")]))
    subjects = [s.strip() for s in re.split(r";", cdm_value(record, roles, "subject")) if s.strip()][:10]
    place = us_place(cdm_value(record, roles, "place"), cdm_value(record, roles, "subject"))
    library = re.sub(r",\s*\d+\s.*$", "", clean(cdm_value(record, roles, "library")).split(";")[0])[:120] or site.name
    single = str(record.get("filetype") or "").lower() in IMAGE_FILES
    picture_ok = single and not (NOT_A_PICTURE.search(kind) and not PHOTO_WORDS.search(kind)
                                 and "image" not in kind.lower())
    page = site.page(alias, pointer)
    credit = (f"{title[:150]}, {library}" + (f", via {site.name}" if site.name not in library else "") +
              f", {{licence}}, {page}")
    item = {"name": f"{site.prefix}-{re.sub(r'[^A-Za-z0-9_-]+', '', alias)[:30]}-{pointer}.jpg",
            "url": site.picture(alias, pointer) if picture_ok else "", "page": page, "title": title,
            "description": description, "words": " ".join([title, description, kind, " ".join(subjects),
                                                           collection]),
            "year": year_of(cdm_value(record, roles, "date"), title), "place": place, "library": library,
            "collection": collection, "subjects": subjects, "credit": credit,
            "photo": bool(PHOTO_WORDS.search(f"{kind} {title}"))}
    rights = [record.get(n) for n in roles.get("rights", []) if isinstance(record.get(n), str)]
    return item, rights


def cdm_site_items(site, want, rng, key, answers, mode=OPEN_CATEGORY, per_collection=0, sample=100):
    """(name, url, rows) items of one CONTENTdm site: its collections in a shuffled order; the first sample records
    of each are read, a collection with no item of the wanted rights kind is passed over, and a collection that has
    them is read further (random pages) for up to per_collection items. mode "open" makes pack items (judge);
    "none" or "research" gives (name, url, candidate) for the kit's personal-use entry instead."""
    out, chosen = [], collections.Counter()
    per_collection = per_collection or max(30, want // 6)
    cols = [(a, n) for a, n in site.collections() if not SKIP_COLLECTION.search(n) and not INDIGENOUS.search(n)]
    rng.shuffle(cols)
    say(f"{site.name}: {len(cols)} collections to look at")
    for alias, name in cols:
        if len(out) >= want or listing_out_of_time():
            break
        roles = site.roles(alias)
        if not roles.get("title"):
            continue
        recs, total = site.records(alias, roles, 1, sample)
        kinds = collections.Counter(rights_of([r.get(n) for n in roles.get("rights", [])
                                               if isinstance(r.get(n), str)])[0] for r in recs)
        if not kinds.get(mode):
            continue
        later = list(range(sample + 1, total + 1, sample))
        rng.shuffle(later)
        for start in [1] + later:
            if chosen[alias] >= per_collection or len(out) >= want or listing_out_of_time():
                break
            if start != 1:
                recs, _ = site.records(alias, roles, start, sample)
            shared = shared_sentences([cdm_value(r, roles, "description") for r in recs])
            for r in recs:
                if chosen[alias] >= per_collection or len(out) >= want:
                    break
                item, rights = cdm_candidate(site, alias, name, roles, r, shared)
                if mode != OPEN_CATEGORY:
                    if rights_of(rights)[0] == mode and item["url"] and not why_left_out(item["words"],
                                                                                         item["year"]):
                        out.append((item["name"], item["url"], item))
                        chosen[alias] += 1
                    continue
                if judge(item, rights, out, answers, key) == "taken":
                    chosen[alias] += 1
        if chosen[alias]:
            say(f"  {site.name} / {name}: {chosen[alias]} taken")
    return out


# ----------------------------------------------------------------- OAI-PMH

OAI_NS = {"oai": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/"}
DC_FIELDS = ("title", "description", "rights", "type", "format", "subject", "coverage", "date", "identifier",
             "relation", "publisher", "contributor", "creator", "source")


def oai_parse(xml_text):
    """(records, resumption token) of one OAI-PMH ListRecords answer in oai_dc: each record {"id", "deleted",
    <Dublin Core element>: [values]}."""
    root = ET.fromstring(xml_text)
    out = []
    for rec in root.iter(f"{{{OAI_NS['oai']}}}record"):
        header = rec.find("oai:header", OAI_NS)
        one = {"id": (header.findtext("oai:identifier", "", OAI_NS) if header is not None else ""),
               "deleted": header is not None and header.get("status") == "deleted"}
        for f in DC_FIELDS:
            one[f] = [clean(e.text) for e in rec.iter(f"{{{OAI_NS['dc']}}}{f}") if e.text and clean(e.text)]
        out.append(one)
    token = root.find(".//oai:resumptionToken", OAI_NS)
    return out, (token.text.strip() if token is not None and token.text else "")


def oai_records(s, base, set_spec="", most=1000, pacer=None, robots=None):
    """Up to most records of an OAI-PMH endpoint (oai_dc; one set when set_spec is given), following resumption
    tokens; nothing when robots.txt forbids the address."""
    robots = robots or RobotsGuard(s)
    why, _ = robots.allowed(base)
    if why:
        say(f"OAI-PMH {base}: not read ({why})")
        return []
    pacer = pacer or Pacer(robots.delay(base, 1.0))
    params = {"verb": "ListRecords", "metadataPrefix": "oai_dc", **({"set": set_spec} if set_spec else {})}
    out = []
    while len(out) < most and not listing_out_of_time():
        pacer.wait()
        try:
            r = s.get(base, params=params, timeout=120)
            if r.status_code != 200:
                break
            recs, token = oai_parse(r.content)
        except Exception as error:  # noqa: BLE001 - stop here with what was read
            say(f"OAI-PMH {base}: stopped ({type(error).__name__})")
            break
        out += [x for x in recs if not x["deleted"]]
        if not token:
            break
        params = {"verb": "ListRecords", "resumptionToken": token}
    return out[:most]


IMAGE_ADDRESS = re.compile(r"\.(jpe?g|png|gif|tiff?)(\?|$)|/iiif/|/full/", re.I)
CDM_REF = re.compile(r"^(https?://[^/]+)/(?:cdm/ref/collection|digital/collection)/([^/]+)/id/(\d+)", re.I)


def oai_picture(record):
    """The picture address of an OAI record: an image address among its identifiers and relations, else the CONTENTdm
    IIIF address made from a CONTENTdm record address; "" when none."""
    for value in record.get("identifier", []) + record.get("relation", []):
        if value.startswith("http") and IMAGE_ADDRESS.search(value):
            return value
    for value in record.get("identifier", []):
        m = CDM_REF.match(value)
        if m:
            return f"{m.group(1)}/iiif/2/{m.group(2)}:{m.group(3)}/full/!2048,2048/0/default.jpg"
    return ""


def oai_candidate(record, site_name, prefix, shared=()):
    """The candidate dict of one OAI record (see judge), and its rights values."""
    title = clean((record.get("title") or [""])[0])
    description = clean(own_words(" ".join(record.get("description", [])[:2]), set(shared)))
    kind = " ".join(record.get("type", []) + record.get("format", []))
    page = next((v for v in record.get("identifier", []) if v.startswith("http") and not IMAGE_ADDRESS.search(v)),
                record.get("id", ""))
    library = clean((record.get("publisher") or record.get("contributor") or [site_name])[0])[:120]
    url = oai_picture(record)
    if NOT_A_PICTURE.search(kind) and not PHOTO_WORDS.search(kind) and "image" not in kind.lower():
        url = ""
    item = {"name": f"{prefix}-{re.sub(r'[^A-Za-z0-9_-]+', '_', record.get('id', ''))[-60:]}.jpg", "url": url,
            "page": page, "title": title, "description": description,
            "words": " ".join([title, description, kind, " ".join(record.get("subject", []))]),
            "year": year_of(*record.get("date", [])), "place": us_place(record.get("coverage", []),
                                                                         record.get("subject", [])),
            "library": library, "collection": site_name, "subjects": record.get("subject", [])[:10],
            "credit": f"{title[:150]}, {library}" + (f", via {site_name}" if site_name not in library else "") +
                      f", {{licence}}, {page}",
            "photo": bool(PHOTO_WORDS.search(f"{kind} {title}"))}
    return item, record.get("rights", [])


# ----------------------------------------------------------------- the Digital Library of Georgia

DLG = "https://dlg.usg.edu/records.json"
DLG_API_DOCS = "https://dlg.usg.edu/about/api"
DLG_OPEN_RIGHTS = ("http://rightsstatements.org/vocab/NoC-US/1.0/", "http://rightsstatements.org/vocab/NKC/1.0/",
                   "https://creativecommons.org/licenses/by/4.0/")


def dlg_picture(doc):
    """The picture address of a DLG record: its edm_is_shown_by when that is a picture, else the first picture of
    its IIIF manifest (read later: returned as "manifest:<address>"), else the CONTENTdm IIIF address made from a
    CONTENTdm record address; "" when none."""
    for v in doc.get("edm_is_shown_by") or []:
        if isinstance(v, str) and IMAGE_ADDRESS.search(v):
            return v
    manifest = doc.get("iiif_manifest_url_ss")
    if isinstance(manifest, list):
        manifest = manifest[0] if manifest else ""
    if manifest:
        return "manifest:" + manifest
    for v in doc.get("edm_is_shown_at") or []:
        m = CDM_REF.match(str(v))
        if m:
            return f"{m.group(1)}/iiif/2/{m.group(2)}:{m.group(3)}/full/!2048,2048/0/default.jpg"
    return ""


def dlg_candidate(doc, shared=()):
    """The candidate dict of one DLG record (see judge), and its rights values (dc_right and dlg_local_right: the
    stricter wins)."""
    def first(field):
        """The first value of a DLG field."""
        v = doc.get(field) or []
        return clean(v[0] if isinstance(v, list) and v else v)
    title = first("dcterms_title") or clean(doc.get("title"))
    description = clean(own_words(" ".join((doc.get("dcterms_description") or [])[:1]), set(shared)))
    kind = " ".join((doc.get("dcterms_type") or []) + (doc.get("dcterms_medium") or []))
    page = f"https://dlg.usg.edu/record/{doc.get('id')}"
    library = first("dcterms_provenance") or "Digital Library of Georgia"
    subjects = [clean(s) for s in (doc.get("dcterms_subject") or [])][:10]
    item = {"name": f"dlg-{re.sub(r'[^A-Za-z0-9_-]+', '_', str(doc.get('id')))[:80]}.jpg",
            "url": dlg_picture(doc), "page": page, "title": title, "description": description,
            "words": " ".join([title, description, kind, " ".join(subjects), clean(doc.get("collection_title"))]),
            "year": year_of(*(doc.get("dc_date") or [])), "place": us_place(doc.get("dcterms_spatial") or []),
            "library": library, "collection": clean(doc.get("collection_title")), "subjects": subjects,
            "credit": f"{title[:150]}, {library}, via the Digital Library of Georgia, {{licence}}, {page}",
            "photo": bool(PHOTO_WORDS.search(f"{kind} {title}"))}
    rights = list(doc.get("dc_right") or []) + list(doc.get("dlg_local_right") or [])
    return item, rights


def dlg_items(want, rng, answers, robots, s=None):
    """(name, url, rows) items of the Digital Library of Georgia: still images under each open rights statement,
    random pages of 100. A picture on a host whose robots.txt forbids it is left out; a IIIF manifest is read for
    its first picture."""
    s = s or session()
    pacer = Pacer(robots.delay(DLG, 1.0))
    why, _ = robots.allowed(DLG)
    if why:
        say(f"Digital Library of Georgia: not read ({why})")
        return []
    out = []
    for rights in DLG_OPEN_RIGHTS:
        params = {"per_page": 100, "f[class_name][]": "Item", "f[type_facet][]": "StillImage",
                  "f[rights_facet][]": rights}
        first = get_json(s, DLG, pacer, params=dict(params, page=1)) or {}
        pages = int(((first.get("response") or {}).get("pages") or {}).get("total_pages") or 0)
        order = list(range(1, pages + 1))
        rng.shuffle(order)
        share = want * (0.8 if "NoC-US" in rights else 0.1)
        got = 0
        for page in order[:60]:
            if got >= share or len(out) >= want or listing_out_of_time():
                break
            data = first if page == 1 else get_json(s, DLG, pacer, params=dict(params, page=page)) or {}
            docs = (data.get("response") or {}).get("docs") or []
            shared = shared_sentences([" ".join(d.get("dcterms_description") or []) for d in docs])
            for doc in docs:
                item, rights_values = dlg_candidate(doc, shared)
                if item["url"].startswith("manifest:"):
                    if rights_of(rights_values)[0] != OPEN_CATEGORY or why_left_out(item["words"], item["year"]):
                        considered(item["name"], item["page"], "not open, or left out by its words")
                        continue
                    manifest = item["url"][len("manifest:"):]
                    item["url"] = "" if robots.allowed(manifest)[0] else iiif_image(
                        get_json(s, manifest, pacer) or {})
                if item["url"] and robots.allowed(item["url"])[0]:
                    considered(item["name"], item["page"], f"its picture's host forbids it "
                                                           f"({robots.allowed(item['url'])[0]})")
                    continue
                if judge(item, rights_values, out, answers, "dlg") == "taken":
                    got += 1
        say(f"Digital Library of Georgia ({rights.split('/')[-3] if 'rightsstatements' in rights else 'CC BY'}): "
            f"{got} taken")
    return out


# ----------------------------------------------------------------- the Newberry Library

NEWBERRY = "https://collections.newberry.org/API/search/v3.0/search"
NEWBERRY_POLICY = "https://www.newberry.org/policies#open-access"
NEWBERRY_PAUSE = 5.0          # its robots.txt: Crawl-delay: 5
NEWBERRY_FIELDS = ("CoreField.Identifier", "CoreField.Title", "CoreField.CaptionLong", "new.Subject", "new.Format",
                   "new.Summary-Long", "new.Rights-Status", "new.Contributing-Institution",
                   "new.Archival-Collection-Title", "Path_TR1", "MediaType", "CoreField.Purpose")
# The kinds of picture read, each its own search (the Newberry's Format field), and its share of the pack.
NEWBERRY_FORMATS = (("Postcards", 0.45), ("Photographs", 0.2), ("Prints", 0.1), ("Maps", 0.1),
                    ("Drawings", 0.05), ("Posters", 0.05), ("Lantern slides", 0.05))
NEWBERRY_RIGHTS = 'new.Rights-Status:"No Copyright - United States"'


def newberry_search(s, query, page, pacer, per_page=100):
    """One page of the Newberry's search API: (items, total)."""
    params = {"query": query, "fields": ",".join(NEWBERRY_FIELDS), "format": "json", "countperpage": per_page,
              "pagenumber": page}
    data = get_json(s, NEWBERRY, pacer, params=params) or {}
    resp = data.get("APIResponse") or {}
    return resp.get("Items") or [], int((resp.get("GlobalInfo") or {}).get("TotalCount") or 0)


def newberry_candidate(it, shared=()):
    """The candidate dict of one Newberry asset (see judge), and its rights values. The description is the asset's
    own caption (CaptionLong), not the collection's summary: a caption equal to the summary, or shared by many assets
    of a page, describes the collection and is not used."""
    ident = clean(it.get("CoreField.Identifier"))
    title = clean(it.get("CoreField.Title"))
    caption = clean(it.get("CoreField.CaptionLong"))
    summary = clean(it.get("new.Summary-Long"))
    if caption and (caption == summary or caption in shared):
        caption = ""
    kind = clean(it.get("new.Format")).replace(",", ", ")
    subjects = [s.strip() for s in clean(it.get("new.Subject")).split(",") if s.strip()][:10]
    picture = (it.get("Path_TR1") or {}).get("URI", "") if isinstance(it.get("Path_TR1"), dict) else ""
    library = clean(it.get("new.Contributing-Institution")) or "Newberry Library"
    collection = clean(it.get("new.Archival-Collection-Title"))
    page = f"https://collections.newberry.org/asset-management/{ident}"
    item = {"name": f"newberry-{re.sub(r'[^A-Za-z0-9]+', '', ident)}.jpg",
            "url": picture if it.get("MediaType") in ("Image", None, "") else "", "page": page, "title": title,
            "description": caption, "words": " ".join([title, caption, kind, " ".join(subjects), collection]),
            "year": year_of(title), "place": us_place(subjects, title), "library": library,
            "collection": collection, "subjects": subjects,
            "credit": f"{title[:150]}, {library}" + (f" ({collection})" if collection else "") +
                      f", {{licence}}, {page} (From the Newberry Library)",
            "photo": bool(PHOTO_WORDS.search(f"{kind} {title}"))}
    return item, [clean(it.get("new.Rights-Status"))]


def newberry_items(want, rng, answers, robots, s=None, formats=NEWBERRY_FORMATS):
    """(name, url, rows) items of the Newberry Library: each format's No-Copyright assets, random pages of 100."""
    s = s or session()
    why, _ = robots.allowed(NEWBERRY)
    if why:
        say(f"Newberry Library: not read ({why})")
        return []
    pacer = Pacer(robots.delay(NEWBERRY, NEWBERRY_PAUSE))
    out = []
    for fmt, share in formats:
        query = f'{NEWBERRY_RIGHTS} AND new.Format:"{fmt}" AND MediaType:Image'
        items, total = newberry_search(s, query, 1, pacer)
        pages = list(range(1, min(total // 100 + 1, 2000) + 1))
        rng.shuffle(pages)
        got = 0
        for done, page in enumerate(pages[:40]):
            if got >= want * share * 1.2 or listing_out_of_time() or (done >= 10 and not got):
                break                     # enough, or ten pages with no described picture: the next format
            batch = items if page == 1 else newberry_search(s, query, page, pacer)[0]
            captions = collections.Counter(clean(it.get("CoreField.CaptionLong")) for it in batch)
            shared = {c for c, n in captions.items() if c and n >= 3}
            for it in batch:
                item, rights = newberry_candidate(it, shared)
                if any(n == item["name"] for n, _, _ in out):
                    continue
                if judge(item, rights, out, answers, "newberry_library") == "taken":
                    got += 1
        say(f"Newberry Library ({fmt}): {got} taken of about {total}")
    return out


# The Newberry's public-domain nudes in art, for museum_art_nudes (adult_art_packs.newberry_nudes uses these).
NEWBERRY_NUDE_QUERIES = ("nude", "naked", "bathers", "academy figure")


def newberry_nude_records(want, s=None):
    """[(name, picture, title, credit, kind, text)] of Newberry prints, drawings and paintings whose Rights Status is
    "No Copyright - United States" and whose words name nudity (never photographs; adult_art_packs applies the
    museum_art_nudes rules)."""
    s = s or session()
    robots = RobotsGuard(s)
    if robots.allowed(NEWBERRY)[0]:
        return []
    pacer = Pacer(robots.delay(NEWBERRY, NEWBERRY_PAUSE))
    out, seen = [], set()
    for word in NEWBERRY_NUDE_QUERIES:
        items, _ = newberry_search(s, f'{NEWBERRY_RIGHTS} AND MediaType:Image AND "{word}"', 1, pacer)
        for it in items:
            item, rights = newberry_candidate(it)
            if item["name"] in seen or not item["url"] or rights_of(rights)[0] != OPEN_CATEGORY:
                continue
            seen.add(item["name"])
            if PHOTO_WORDS.search(clean(it.get("new.Format"))):
                continue
            credit = item["credit"].replace("{licence}", "No Copyright - United States")
            out.append((item["name"], item["url"], item["title"], credit, clean(it.get("new.Format")),
                        item["description"]))
        if len(out) >= want:
            break
    return out[:want]


# ----------------------------------------------------------------- the packs

# CONTENTdm sites: (host, name in credits, file-name prefix).
MIDWEST_SITES = [("ohiomemory.org", "Ohio Memory", "ohmem"), ("dmr.bsu.edu", "Ball State University Digital Media "
                                                                           "Repository", "bsu"),
                 ("idaillinois.org", "Illinois Digital Archives", "ida"),
                 ("media.library.ohio.edu", "Ohio University Libraries", "ohiou"),
                 ("collections.lib.uwm.edu", "UW-Milwaukee Libraries", "uwm"),
                 ("digitalhorizonsonline.org", "Digital Horizons", "dh")]
SOUTH_SITES = [("kdl.kyvl.org", "Kentucky Digital Library", "kdl"),
               ("content.lib.auburn.edu", "Auburn University Libraries", "auburn"),
               ("digital.archives.alabama.gov", "Alabama Department of Archives and History", "adah"),
               ("collections.digitalmaryland.org", "Digital Maryland", "dmd")]
WEST_SITES = [("content.libraries.wsu.edu", "Washington State University Libraries", "wsu"),
              ("econtent.unm.edu", "New Mexico Digital Collections (University of New Mexico)", "unm"),
              ("archive.library.nau.edu", "Colorado Plateau Digital Archives (Northern Arizona University)", "nau")]


def sites_pack(key, sites, limit, extra=None):
    """A pack from CONTENTdm sites (and extra: a function (want, rng, answers, robots) -> items, for a non-CONTENTdm
    source): the sites are read at the same time, each in its own thread with its own pace, each for an even share;
    the pictures are fetched two at a time per pack, one second apart."""
    import concurrent.futures
    s, rng, answers = session(), pass_random(key), set()
    robots = RobotsGuard(s)
    sources = len(sites) + (1 if extra else 0)
    want = int(limit * 1.3 / max(1, sources)) + 4

    def one(site):
        """The items of one site (none when it cannot be read)."""
        host, name, prefix = site
        try:
            return cdm_site_items(ContentDM(host, name, s=session(), robots=robots, prefix=prefix), want,
                                  pass_random(f"{key}/{host}"), key, answers)
        except Exception as error:  # noqa: BLE001 - one site down does not stop the pack
            say(f"{name}: left out ({type(error).__name__}: {error})")
            return []

    items = []
    with concurrent.futures.ThreadPoolExecutor(max(1, len(sites))) as pool:
        jobs = [pool.submit(one, site) for site in sites]
        if extra:
            try:
                items += extra(want, rng, answers, robots)
            except Exception as error:  # noqa: BLE001 - that source down: the sites still count
                say(f"{key}: the extra source is left out ({type(error).__name__}: {error})")
        for job in jobs:
            items += job.result()
    rng.shuffle(items)
    items = new_only(items)
    fetched = fetch_all(items[:int(limit * 1.2) + 2], workers=3, pause=1.0)[:limit]
    say(f"{key}: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if r[0].get('child'))} marked child")
    return with_twins(fetched)


def build_newberry_library(limit):
    """The Newberry Library pack (newberry_items)."""
    s, rng, answers = session(), pass_random("newberry_library"), set()
    items = newberry_items(int(limit * 1.3) + 4, rng, answers, RobotsGuard(s), s)
    rng.shuffle(items)                    # the formats and series mixed, not the first series read
    items = new_only(items)
    fetched = fetch_all(items[:int(limit * 1.2) + 2], workers=3, pause=0.5)[:limit]
    say(f"newberry_library: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if r[0].get('child'))} marked "
        f"child")
    return with_twins(fetched)


def build_state_libraries_midwest(limit):
    """Ohio, Indiana, Illinois, Wisconsin and North Dakota state digital libraries (MIDWEST_SITES)."""
    return sites_pack("state_libraries_midwest", MIDWEST_SITES, limit)


def build_state_libraries_south(limit):
    """The Digital Library of Georgia (dlg_items) and the Kentucky, Alabama and Maryland sites (SOUTH_SITES)."""
    return sites_pack("state_libraries_south", SOUTH_SITES, limit,
                      extra=lambda want, rng, answers, robots: dlg_items(want * 2, rng, answers, robots))


def build_state_libraries_west(limit):
    """Washington State University, New Mexico and Northern Arizona (WEST_SITES)."""
    return sites_pack("state_libraries_west", WEST_SITES, limit)


STATE_COLLECTIONS_CREDIT = ("{what}: only items whose own rights statement is No Copyright - United States, No Known "
                            "Copyright, the Public Domain Mark, CC0 or CC BY (each item's statement, holding library "
                            "and record page below); descriptions are the libraries' own words.")
STATE_COLLECTIONS_PACKS = {
    "newberry_library": (build_newberry_library,
                         "The Newberry Library, Chicago (https://collections.newberry.org): postcards, photographs, "
                         "prints, drawings, posters and maps whose Rights Status is No Copyright - United States, "
                         "\"available for any lawful purpose, commercial or non-commercial\" (the Newberry's open "
                         "access policy, https://www.newberry.org/policies#open-access). From the Newberry Library; "
                         "each item and its record page below."),
    "state_libraries_midwest": (build_state_libraries_midwest, STATE_COLLECTIONS_CREDIT.format(
        what="Ohio Memory, Ball State University Digital Media Repository, Illinois Digital Archives, "
             "Ohio University Libraries, UW-Milwaukee Libraries and Digital Horizons (CONTENTdm "
             "API)")),
    "state_libraries_south": (build_state_libraries_south, STATE_COLLECTIONS_CREDIT.format(
        what="The Digital Library of Georgia (its API, https://dlg.usg.edu/about/api), the Kentucky Digital Library, "
             "Auburn University Libraries, the Alabama Department of Archives and History and Digital Maryland "
             "(CONTENTdm API)")),
    "state_libraries_west": (build_state_libraries_west, STATE_COLLECTIONS_CREDIT.format(
        what="Washington State University Libraries, New Mexico Digital Collections (University of New Mexico) and "
             "the Colorado Plateau Digital Archives (Northern Arizona University) (CONTENTdm API)")),
}
STATE_COLLECTIONS_LIMITS = {
    "newberry_library": 4000,          # of about 190,000 open postcards and 60,000 photographs (many need words)
    "state_libraries_midwest": 3000,   # open collections are a minority on these sites (survey, November 2026)
    "state_libraries_south": 3000,     # the DLG has about 23,000 open still images with descriptions
    "state_libraries_west": 2500,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one state-collections pack builder.")
    parser.add_argument("key", choices=sorted(STATE_COLLECTIONS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--rows", type=int, default=0, help="print only this many rows (0: all)")
    args = parser.parse_args(argv)
    entries = STATE_COLLECTIONS_PACKS[args.key][0](args.limit)
    for name, data, row in entries[:args.rows or None]:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child, "
        f"{len(build_packs.NEEDS)} set aside for a description")
    return 0


if __name__ == "__main__":
    sys.exit(main())
