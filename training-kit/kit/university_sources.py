"""COLLEGE AND UNIVERSITY photo collections of the United States and Canada for the Picture Model Training Kit: the
collections that cannot be ready-made packs because of their licence, and the ones that need a sign-up or permission
or were looked at and left out. The open ones are packs in packs/university_packs.py: dpla_campus (DPLA items from
college and university libraries under No Copyright - United States, the Public Domain Mark, CC0 or CC BY),
commons_college_streams (colleges' own photo streams copied to Wikimedia Commons, public domain or CC BY) and
commons_university_archives (university libraries' digitized photographs with no known copyright restrictions).

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link and the terms line are in each entry; where a page
refused this machine, the entry says so and what is not verified).

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA: only with the share-alike choice (--with-wikipedia); an add-on trained with them is
                   CC BY-SA.
  "noncommercial"  CC BY-NC and CC BY-NC-SA (never NoDerivatives): the personal-use box (Alt+Q); the result is for
                   personal use only.

The collections (UNIVERSITY_SOURCES):
  share-alike
    dpla_campus_sa   DPLA items from college and university libraries whose rights URI is CC BY-SA (any version),
                     image items found by the same everyday words as the open dpla_campus pack.
  noncommercial
    dpla_campus_nc   The same for CC BY-NC and CC BY-NC-SA (CC BY-NC-ND and BY-ND are never taken).
Both need a free DPLA API key in the environment variable DPLA_API_KEY on the trainer's computer (asked for at
https://pro.dp.la/developers/api-basics: DPLA e-mails a 32-character key); without it they say so and add nothing.

Answers are the institution's own words (the record's title and description), never written by an AI model.

Safety and privacy (packs/SOURCE-RULES.md, as university_packs.py): nothing sexual, no swimwear or beauty contests,
no crime, prisons, evidence or victims, no portraits, yearbooks, team or class photos or student records, no camps,
youth programmes or school pupils (minors whose age is not given), no official events; "child" and "content":
"graphic" marked from the words (archive_sources.make_rows; a dead or injured child is left out). Both entries show
people and are never used for picture-making (UNIVERSITY_PICTURE_MAKING_OK is empty).

Needing sign-up (UNIVERSITY_SIGN_UP), needing permission (UNIVERSITY_PERMISSION) and looked at but not included
(UNIVERSITY_NOT_INCLUDED), each with the terms line. UNIVERSITY_SUMMARY has one line per institution: what it offers
and where it went. UNIVERSITY_SEXUALITY_NOTES records the owner's question about university sexuality and
sex-education archives (report only: nothing is built or downloaded from them).

    python -c "import sources, university_sources"      (from the kit folder: checks the file loads)
"""

import math
import os
import random
import re
import time

from archive_sources import session, get_json, make_rows
from extra_sources import say
from more_sources import fetch_shared
from sources import Source, clean

DPLA = "https://api.dp.la/v2/items"
DPLA_TERMS = "https://dp.la/about/terms-conditions"
# The rights URIs of each entry (DPLA's "rights" field, as the item's institution gave it). Never NoDerivatives.
SA_RIGHTS = re.compile(r"^https?://creativecommons\.org/licenses/by-sa/", re.I)
NC_RIGHTS = re.compile(r"^https?://creativecommons\.org/licenses/by-nc(-sa)?/", re.I)
# A data provider that is a college or university (as packs/university_packs.py).
UNIVERSITY = re.compile(r"\b(universit(y|ies|é)|college|institute of technology|polytechnic|school of mines|"
                        r"seminary)\b", re.I)
NOT_UNIVERSITY = re.compile(r"\b(state (library|archives)|public library|historical society|museum)\b", re.I)
TOPICS = ["campus", "college students", "university students", "dormitory", "student union", "dining hall",
          "library interior", "laboratory", "classroom", "commencement", "homecoming", "football game",
          "basketball game", "marching band", "stadium", "agricultural experiment station", "cooperative extension",
          "farm", "greenhouse", "main street", "downtown", "street scene", "parade", "county fair", "park", "forest",
          "lake", "river", "snow", "construction", "festival", "concert"]
# As university_packs.left_out_because: words that leave a record out.
LEFT_OUT = re.compile(r"\b(nud\w*|naked|topless|underwear|lingerie|swim\w*|bikini\w*|bathing suits?|beauty "
                      r"(contest|pageant|queen)s?|pageants?|sex\w*|erotic\w*|porn\w*|arrest\w*|suspects?|inmates?|"
                      r"prisons?|prisoners?|jail\w*|crimes?|criminal|murder\w*|shootings?|victims?|mug ?shots?|"
                      r"evidence|lynch\w*|execut\w*|portraits?|head ?shots?|yearbooks?|class (photo|picture)s?|"
                      r"team (photo|picture)s?|group (photo|portrait)s?|rosters?|transcripts?|student records?|"
                      r"camps?|campers?|youth|high schools?|middle schools?|elementary|junior high|4-h|scouts?|"
                      r"preschool\w*|day ?care|orphan\w*|trustees?|regents?|donors?|gala|banquet|luncheon|"
                      r"ribbon[- ]cutting|groundbreaking|inaugurat\w*|senator|governor|mayor|candidates?|"
                      r"japs?|niggers?|negro(es)?|squaws?|redskins?|savages?)\b", re.I)
CONTENTDM_THUMB = re.compile(r"^(https?://[^/]+)/(?:digital/api/singleitem/collection/([^/]+)/id/(\d+)/thumbnail|"
                             r"utils/getthumbnail/collection/([^/]+)/id/(\d+))")


def as_list(value):
    """A DPLA field as a list."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def dpla_picture(doc):
    """The full-size picture of a DPLA item: its "mediaMaster", else the CONTENTdm IIIF address made from a
    CONTENTdm thumbnail's address; "" when there is only a small thumbnail."""
    for url in as_list(doc.get("mediaMaster")):
        if isinstance(url, str) and url.startswith("http"):
            return url
    m = CONTENTDM_THUMB.match(str(doc.get("object") or ""))
    if m:
        host, alias, pointer = m.group(1), m.group(2) or m.group(4), m.group(3) or m.group(5)
        return f"{host}/iiif/2/{alias}:{pointer}/full/!1600,1600/0/default.jpg"
    return ""


def dpla_place(src):
    """The place of a DPLA item from its first spatial entry with a US state or Canadian province, or ""."""
    for sp in as_list(src.get("spatial")):
        if not isinstance(sp, dict):
            continue
        country = clean(sp.get("country"))
        country = "USA" if country in ("United States", "USA", "") and sp.get("state") else country
        if country not in ("USA", "Canada"):
            continue
        return ", ".join(dict.fromkeys(x for x in (clean(sp.get("city")), clean(sp.get("state")), country) if x))
    return ""


def dpla_answer(src):
    """The record's title and its first description when that says more, at most about 70 words; "" when it is under
    six words."""
    title = re.sub(r"[\[\]]", "", clean(" ".join(as_list(src.get("title"))[:1]))).strip(" .")
    text = title
    for d in as_list(src.get("description")):
        d = clean(d)
        if d and d.lower()[:40] not in title.lower():
            text = f"{title}. {d}" if title else d
            break
    text = re.sub(r"https?://\S+", "", text)
    words = text.split()
    if len(words) < 6:
        return ""
    text = " ".join(words[:70])
    return text if text.endswith((".", "!", "?")) else text + "."


def dpla_entry_items(key, rights_ok, cap, test, prefix, seed):
    """[(file name, picture address, row)] of DPLA college and university image items whose rights URI matches
    rights_ok, found by TOPICS (each topic's rights facet first, then a few random pages of each matching URI)."""
    s, rng = session(), random.Random(seed)
    want = int((cap + test) * 1.25) + 2
    topics = list(TOPICS)
    rng.shuffle(topics)
    share = max(3, math.ceil(want / len(topics)))
    items, seen, pictures = [], set(), 0
    for topic in topics:
        if pictures >= want:
            break
        facets = get_json(s, DPLA, {"api_key": key, "q": topic, "facets": "rights", "facet_size": 100,
                                    "page_size": 0}) or {}
        terms = ((facets.get("facets") or {}).get("rights") or {}).get("terms") or []
        got = 0
        for term in terms:
            uri, count = str(term.get("term") or ""), int(term.get("count") or 0)
            if not rights_ok.match(uri) or re.search(r"-nd\b|/by-nd|nc-nd", uri, re.I):
                continue
            pages = list(range(1, min(100, math.ceil(count / 100)) + 1))
            rng.shuffle(pages)
            for page in pages[:4]:
                if got >= share:
                    break
                time.sleep(0.5)
                data = get_json(s, DPLA, {"api_key": key, "q": topic, "rights": uri, "exact_field_match": "true",
                                          "page_size": 100, "page": page}) or {}
                for doc in data.get("docs") or []:
                    if got >= share:
                        break
                    src = doc.get("sourceResource") or {}
                    dp = doc.get("dataProvider")
                    provider = clean(dp.get("name") if isinstance(dp, dict) else " ".join(as_list(dp)[:1]))
                    name = f"{prefix}-{doc.get('id')}.jpg"
                    if name in seen or "image" not in [str(t).lower() for t in as_list(src.get("type"))] \
                            or not UNIVERSITY.search(provider) or NOT_UNIVERSITY.search(provider):
                        continue
                    seen.add(name)
                    words = " ".join(str(x) for x in (*as_list(src.get("title")), *as_list(src.get("description")),
                                                      *[s_.get("name") if isinstance(s_, dict) else s_
                                                        for s_ in as_list(src.get("subject"))]))
                    answer, url = dpla_answer(src), dpla_picture(doc)
                    if LEFT_OUT.search(words) or not answer or not url:
                        continue
                    link = doc.get("isShownAt") or f"https://dp.la/item/{doc.get('id')}"
                    credit = (f"{answer[:150]} {provider}, via the Digital Public Library of America, rights {uri}, "
                              f"{link}")
                    rows = make_rows(name, url, answer, credit, dpla_place(src))
                    if rows:
                        items += rows
                        got += 1
                        pictures += 1
        say(f"  DPLA '{topic}': {got} items")
    return items


def prepare_dpla(source, data_dir, rights_ok, prefix, seed):
    """One DPLA entry: the key from DPLA_API_KEY, the items (dpla_entry_items), the pictures fetched."""
    key = os.environ.get("DPLA_API_KEY", "").strip()
    if not key:
        say(f"  {source.key}: no DPLA API key. Ask for a free one at https://pro.dp.la/developers/api-basics and set "
            "the environment variable DPLA_API_KEY to it. Nothing added.")
        return []
    items = dpla_entry_items(key, rights_ok, source.cap, source.test, prefix, seed)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=3)


def prepare_dpla_campus_sa(source, data_dir, work, cap):
    """DPLA college and university items under CC BY-SA."""
    return prepare_dpla(source, data_dir, SA_RIGHTS, "dplasa", 611)


def prepare_dpla_campus_nc(source, data_dir, work, cap):
    """DPLA college and university items under CC BY-NC or CC BY-NC-SA."""
    return prepare_dpla(source, data_dir, NC_RIGHTS, "dplanc", 612)


UNIVERSITY_SOURCES = [
    Source("dpla_campus_sa", "Campus life, college towns and farms from US college and university libraries, items "
                             "under CC BY-SA (Digital Public Library of America, share-alike; needs a free DPLA key)",
           "Each item CC BY-SA (its rights URI in DPLA); DPLA metadata CC0 (https://dp.la/about/terms-conditions)",
           "US college and university libraries via the Digital Public Library of America, CC BY-SA, each credited "
           "in its row, https://dp.la", "share-alike", 1500, 20, prepare_dpla_campus_sa,
           "up to about 400 MB of pictures", terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA: use with credit, and anything made from it keeps the same licence."),
    Source("dpla_campus_nc", "Campus life, college towns and farms from US college and university libraries, items "
                             "under CC BY-NC or BY-NC-SA (Digital Public Library of America, personal use; needs a "
                             "free DPLA key)",
           "Each item CC BY-NC or CC BY-NC-SA (its rights URI in DPLA); DPLA metadata CC0",
           "US college and university libraries via the Digital Public Library of America, CC BY-NC or BY-NC-SA, "
           "each credited in its row, https://dp.la", "noncommercial", 1500, 20, prepare_dpla_campus_nc,
           "up to about 400 MB of pictures", terms="https://creativecommons.org/licenses/by-nc/4.0/",
           terms_summary="CC BY-NC (or BY-NC-SA): use with credit, never for money; the result is for personal "
                         "use only."),
]

# Both entries show people (students, crowds, townspeople): never for picture-making.
UNIVERSITY_PICTURE_MAKING_OK = set()

UNIVERSITY_SIGN_UP = {
    "Digital Public Library of America (DPLA) API":
        "A free key by e-mail (https://pro.dp.la/developers/api-basics; DPLA e-mails a 32-character key). Used by "
        "the open pack dpla_campus (GitHub secret DPLA_API_KEY) and by dpla_campus_sa and dpla_campus_nc here "
        "(environment variable DPLA_API_KEY on the trainer's computer). DPLA's terms: 'all Metadata has been "
        "dedicated to the public pursuant to Creative Commons' CC0 public domain dedication' "
        "(https://dp.la/about/terms-conditions); each item's picture keeps its institution's rights statement. "
        "pro.dp.la's developer policy pages refused this machine (CloudFront 403), so DPLA's API rate limits were "
        "not read; the builders pause between requests.",
    "UBC Open Collections API (University of British Columbia)":
        "A free key (https://open.library.ubc.ca/docs: 'Open Collections API Keys are valid for all three of our "
        "APIs'). Not used: the UBC Archives photographs say 'Images provided for research and reference use only. "
        "Permission to publish, copy or otherwise use these images must be obtained from the UBC Archives' (see "
        "UNIVERSITY_PERMISSION), and open.library.ubc.ca blocked this machine ('Your request was blocked because our "
        "system detected unusual activity').",
    "Calisphere (University of California)":
        "Its Solr API needed a token on request, but 'as of February 2024, any API keys that have been assigned "
        "will no longer be able to access data through the legacy Solr API' "
        "(https://help.oac.cdlib.org/support/solutions/articles/9000101639); calisphere.org answers robots with an "
        "AWS WAF challenge. 'Calisphere ... shares Calisphere data with the Digital Public Library of America', so "
        "its open items (UC campuses, USC and other California libraries) reach dpla_campus.",
    "Universities' own Flickr streams":
        "A free Flickr API key, but Flickr's API terms (https://www.flickr.com/services/api/tos/) forbid storing "
        "photos, which a training pack does. Not used; the Commons copies of the streams are used instead "
        "(commons_college_streams; state universities' streams are in state_packs.py).",
}

UNIVERSITY_PERMISSION = {
    "Canadiana (Canadian Research Knowledge Network, CRKN)":
        "https://www.canadiana.ca/terms : 'You may not use spiders, robots, data mining techniques or other "
        "automated devices or programs to catalog, download or otherwise reproduce, store or distribute any items "
        "in the Collection without prior written permission from CRKN'; the site is for 'personal, non-commercial "
        "use'. Ask CRKN (info@crkn.ca) for permission; much of it is printed matter, not photographs.",
    "UBC Archives Photograph Collection (University of British Columbia)":
        "'Images provided for research and reference use only. Permission to publish, copy or otherwise use these "
        "images must be obtained from the UBC Archives' (each record, open.library.ubc.ca/collections/arphotos). "
        "Campus life from the 1900s to today: a good candidate for a written request to UBC Archives.",
    "The Portal to Texas History (University of North Texas), searched directly":
        "https://texashistory.unt.edu/terms-of-use/ : 'made publicly available by the collection-holding partners "
        "for use in research, teaching, and private study' and 'the reproduction of some materials may be restricted "
        "by terms of gift or purchase agreements'. Its items marked open in DPLA (the Portal is a DPLA hub) are "
        "taken by dpla_campus; the rest need the holding partner's permission.",
    "University of Alberta Library digitized collections (Peel's Prairie Provinces)":
        "https://library.ualberta.ca/digital-initiatives/digital-collections/rights : each item's own rights; where "
        "none applies, 'Identify and contact the copyright owner(s) directly, to request permission'. The postcards "
        "the Library put on Commons as public domain are taken by commons_university_archives; the collection is "
        "moving to the Internet Archive (check each item's licence there).",
    "Yale University Library digital collections":
        "Yale's open-access policy gives 'license- and royalty-free access to digital images of public domain "
        "materials' (2011), but the Library's permission page says 'Yale University provides access to these "
        "materials for educational and research purposes only', and collections.library.yale.edu/robots.txt "
        "disallows /manifests/ for every robot and /iiif/ for GPTBot (a sign against AI training). Not used without "
        "Yale's written agreement; its public-domain photos are mostly before 1929.",
}

UNIVERSITY_NOT_INCLUDED = {
    "University of Minnesota UMedia": "umedia.lib.umn.edu answered this machine with an Azure WAF JavaScript "
                                      "challenge (403). Its items reach DPLA through the Minnesota Digital Library "
                                      "hub; the open ones are taken by dpla_campus.",
    "University of Michigan Digital Collections (quod.lib.umich.edu)": "Cloudflare challenge (403). Michigan items "
                                                                       "reach DPLA through the Michigan Service Hub.",
    "University of Illinois Digital Collections": "digital.library.illinois.edu refused this machine (403). Illinois "
                                                  "items reach DPLA through the Illinois Digital Heritage Hub.",
    "University of Utah Marriott Library": "collections.lib.utah.edu answered 418 (a robot block). Utah items reach "
                                           "DPLA through the Mountain West Digital Library.",
    "Harvard Library (LibraryCloud API)": "api.lib.harvard.edu refused this machine (403). Harvard's art museums are "
                                          "covered elsewhere (archive_sources.py: a key, images non-commercial).",
    "University of North Carolina (dc.lib.unc.edu)": "offline in November 2026 ('This website is currently offline "
                                                     "as we work to address a security issue'). UNC items reach DPLA "
                                                     "through the North Carolina Digital Heritage Center.",
    "Cornell, UT Austin (digital.lib.utexas.edu), Oregon Digital, Memorial University (collections.mun.ca)":
        "did not answer this machine (time-outs). Oregon State and University of Oregon items reach DPLA through "
        "Northwest Digital Heritage; Texas items through the Portal to Texas History. Cornell's and Memorial's "
        "terms were not read.",
    "McGill Library digital collections": "digital.library.mcgill.ca refused this machine (403); terms not read.",
    "Mountain West Digital Library, Ohio Memory, Texas Digital Library (aggregators)":
        "reachable, but they are DPLA hubs (or feed one): their open college and university items are taken by "
        "dpla_campus. Ohio Memory is run by the Ohio History Connection and the State Library of Ohio (state "
        "bodies: left to state_packs.py).",
    "Princeton (DPUL), Indiana, Penn State, Wisconsin (UWDC), Washington's own site, Simon Fraser, Toronto, "
    "Calgary, Dalhousie, Laval, Montréal": "not examined one by one in this pass. The US ones that are DPLA "
                                           "contributors reach dpla_campus when an item's rights are open; the "
                                           "Canadian ones (and Québec's BAnQ, which is provincial: canada_packs.py) "
                                           "remain to be checked.",
    "Commons copies of colleges' streams under CC BY-SA":
        "The Accent (Austin Community College's student newspaper, about 1,300 files, CC BY-SA 2.0) and a few UDC "
        "Law files: share-alike, a possible later Commons share-alike entry; the open files of the other streams "
        "are in commons_college_streams.",
    "Texas Tech student housing, Texas A&M (Memorial Student Center and university pictures), Colorado School of "
    "Mines and Oregon State University streams on Commons": "in state_packs.commons_state_community (state "
                                                            "universities); not repeated.",
    "Texas Army ROTC stream on Commons (about 13,900 files)": "military training: service_packs.py covers uniformed "
                                                              "services; not campus everyday life.",
    "University computer-vision datasets of everyday scenes":
        "Already in the kit: GeoDE (Princeton), Visual Genome (Stanford), MINC (Cornell), COCO-Text (Cornell Tech), "
        "Fashionpedia (Cornell), VizWiz, Cityscapes, Places365, SUN397, ADE20K (mentioned in other source files). "
        "Not added (licences as generally published, not re-checked here: unverified): BDD100K (Berkeley, its own "
        "licence for non-commercial research), CADC (Waterloo, CC BY-NC 4.0, driving in snow), NYU Depth V2 and "
        "SUN RGB-D (no stated licence: research), ScanNet and Matterport3D (signed terms of use: sign-up).",
}

# One line per institution: what it offers and where it went (the report's table).
UNIVERSITY_SUMMARY = {
    "DPLA (aggregator of US libraries)": "open: dpla_campus pack (NoC-US, PDM, CC0, CC BY); CC BY-SA and BY-NC: kit "
                                         "entries dpla_campus_sa and dpla_campus_nc; key DPLA_API_KEY",
    "College of DuPage, Germanna CC, Community College of Vermont, Texas A&M-Commerce, Roanoke, Union, Louisville, "
    "Michigan SEAS, UDC Law": "open: commons_college_streams (Commons copies of their Flickr streams, CC BY / PD)",
    "University of Washington, Miami University, University of Alberta, SMU": "open: commons_university_archives "
                                                                              "(no known copyright / PD)",
    "Calisphere (UC)": "via DPLA (legacy API closed)",
    "Portal to Texas History (UNT)": "via DPLA; direct: research, teaching and private study (permission)",
    "Mountain West DL, Ohio Memory, Texas DL, Minnesota UMedia, Michigan, Illinois, Utah, UNC, Oregon": "via DPLA "
                                                                                                     "hubs",
    "Canadiana / CRKN": "permission (robots and downloads forbidden without written permission)",
    "UBC Open Collections": "permission (research and reference use only); API key sign-up",
    "Yale": "permission (robots.txt and 'educational and research purposes only')",
    "Harvard, McGill, Cornell, UT Austin, Memorial": "not included (refused or did not answer this machine)",
    "Princeton, Indiana, Penn State, Wisconsin, SFU, Toronto, Calgary, Dalhousie, Laval, Montréal": "not examined "
                                                                                                   "in this pass",
}

# The owner's question (report only; nothing built, nothing downloaded): university and college sexuality and
# sex-education archives. Each: what it offers, its terms line, adults-only certainty, and whether it would fit the
# review-only adult collections of adult_review_sources.py (adults only, consent, no violence, reviewed by a trusted
# sighted adult, never for picture-making, never published).
UNIVERSITY_SEXUALITY_NOTES = {
    "The Kinsey Institute (Indiana University)":
        "Books, art, photographs and film on sex and gender research. 'Access to materials in our collections "
        "requires an appointment' (visitors 18 or over, registered); 'To make an inquiry or request licensing for "
        "your project, please contact our collections staff' (libknsy@iu.edu); no open licence and no online image "
        "collection (https://kinseyinstitute.org/collections/index.html). Adults-only certainty: not stated per "
        "item. Fit: only as a permission (contract) candidate, as adult_review_sources.py already says.",
    "Digital Transgender Archive (Northeastern University and partners)":
        "Digitized trans history (periodicals, photographs). Its policy: rights are secured 'to digitize materials "
        "and make them available online for noncommercial educational and research purposes'; item rights such as "
        "'Copyright undetermined' (https://www.digitaltransgenderarchive.net/about/policies; the page refused this "
        "machine, read through a search engine). Not open; mostly documents, not instructional pictures; ages not "
        "stated. Fit: no (not open; would need permission).",
    "ONE National Gay & Lesbian Archives (USC Libraries)":
        "Photographs and graphics in the USC Digital Library carry 'Image is displayed for education and personal "
        "research only. Reuse requires signed permission' (from ONE Archives and the copyright holder); its "
        "reproduction guidelines say images are not to be used 'without the expressed written permission from ONE "
        "Archives' (2012 forms). Fit: permission only.",
    "The ArQuives (Canada's LGBTQ2+ Archives, Toronto)":
        "A fee schedule for reproductions (May 2025, queeries@arquives.ca); no open licence found. Fit: permission "
        "only.",
    "OpenStax Anatomy and Physiology (Rice University)":
        "The FIRST edition (2013) is CC BY 4.0 and is already used (body_packs anatomy). The SECOND edition is NOT: "
        "'Anatomy and Physiology 2e is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
        "(CC BY-NC-SA) license', and its art without other credit is 'Copyright Rice University, OpenStax, under CC "
        "BY-NC-SA 4.0'; some figures are third-party ('Regents of University of Michigan Medical School © 2012') "
        "(https://openstax.org/books/anatomy-and-physiology-2e/pages/preface). adult_review_sources.py's reason "
        "holds: reproductive anatomy diagrams, no sexual activity; per figure the licence differs, so any reuse "
        "must check each figure's credit. Fit: anatomy, not the adult review collections.",
    "BCcampus, eCampusOntario, Open Oregon State and other university open textbooks":
        "Reproductive-system chapters adapted from OpenStax (Open Oregon State 'Anatomy & Physiology': 'Images, from "
        "Anatomy & Physiology by OpenStax, are licensed under CC BY except where otherwise noted'; eCampusOntario "
        "medical-terminology books); BCcampus lists 'Human Reproduction: A Clinical Perspective' as CC BY-NC. No "
        "CC BY sex-education book with its own drawings of sexual health was found. Each figure's credit must be "
        "checked (as adult_review_sources.py notes for LibreTexts and Lumen). Fit: anatomy diagrams only.",
    "University health services' safer-sex posters and pamphlets":
        "No open-licensed university collection found; such posters are usually all rights reserved. The Commons "
        "'Safer sex' and 'Condoms' categories are already read by adult_review_sources.py.",
    "DPLA and Calisphere items under 'Sex instruction', 'Safe sex in AIDS prevention', 'Condoms'":
        "Not searched: DPLA needs the API key (none on this machine) and Calisphere answers robots with a "
        "challenge. Likely contents: AIDS-era posters and pamphlets (1980s-1990s) from university special "
        "collections (UCSF, USC ONE Archives, Cornell's Human Sexuality Collection), mostly 'In Copyright' or "
        "'Copyright Not Evaluated'; NoC-US items would be few (US government CDC/NIH material). Unverified. Fit: "
        "only items under NoC-US, PDM, CC0 or CC BY with adults only by their words, reviewed as the existing "
        "review-only collections are; a search with the DPLA key could list them for the owner's decision.",
}
