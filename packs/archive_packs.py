"""Pack builders for more documentary, archive, museum and news photographs with the captions their makers wrote,
filling gaps left by documentary_packs.py (US government archives beyond the Library of Congress, big public
libraries, art museums with written descriptions, a Danish museum, Dutch press photos and open government news
photos). They are used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and
returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" when the
record says where the photo was taken (see places.py; museum objects say where they were made, place_kind "origin")
and "child": True when the caption mentions a child. The limit counts pictures.

Graphic pictures (the dead, wounds, disaster casualties: war archives such as the Australian War Memorial have many)
are kept by the owner's rule, with the record's own plain caption, and every row of such a picture carries
"content": "graphic" (GRIM finds them; each builder's log says how many). Still left out: anything sexual, sexual
violence, torture or execution scenes, and pictures whose caption names both a child and death or injury (a dead or
injured child).

Every picture gets "Describe this picture." with its maker's own caption, tidied (catalogue codes, exhibition notes
and file notes taken out), at least 6 words long. A picture whose record names the place also gets "Where was this
photo taken?" as a second row for the same picture (food_packs.with_twins). Nothing is written by an AI model.
Captions written all in capital letters (DOCUMERICA, the Australian War Memorial) are put in ordinary sentence case:
place names from the record, US states, months and words in quotation marks keep their capitals.

  nara                US National Archives catalogue (catalog.archives.gov), three photo series with long captions:
                      DOCUMERICA (the Environmental Protection Agency's 1971-1977 survey of American life and the
                      environment, about 15,900 photos), the War Relocation Authority's photographs of Japanese
                      American incarceration (1942-1945, about 4,000, full captions by the WRA photographers, Dorothea
                      Lange among them) and Ansel Adams's photographs of national parks (about 220). US government work,
                      public domain; only records marked "Unrestricted" for use. Place from the record's place
                      headings ("Honolulu (Hawaii)" -> "Honolulu, Hawaii, USA") or, for the WRA, the caption's opening
                      words ("Heart Mountain Relocation Center, Heart Mountain, Wyoming."). Captions with wartime
                      slurs are left out.
  nypl                The New York Public Library's public-domain items (photographs, stereoviews, postcards and
                      prints; maps, menus and book pages left out), from the Library's bulk metadata release on GitHub
                      (github.com/NYPL-publicdomain/data-and-utilities, metadata CC0, items "no known US copyright
                      restrictions"). Titles of 6 words or more, with the description where there is one. Place from
                      the geographic subject.
  getty_museum        The J. Paul Getty Museum, Los Angeles, Open Content: objects whose record says "No Copyright",
                      with the museum's own description (metadata CC0, https://www.getty.edu/legal/image_request/ ).
                      Found with the museum's SPARQL service (data.getty.edu); place made as "origin".
  digital_commonwealth  Digital Commonwealth (Massachusetts libraries, archives and museums, including the Boston
                      Public Library): photographs marked "No known copyright restrictions" (reuse "no restrictions").
                      Titles of 6 words or more, with the abstract where there is one; place from the record. (Its
                      photos under CC BY-NC-ND are a non-commercial kit entry: training-kit/kit/archive_sources.py.)
  smk                 Statens Museum for Kunst (National Gallery of Denmark): public-domain works (CC0 / Public Domain
                      Mark, https://open.smk.dk) whose title is a description of 6 words or more. SMK writes these in
                      Danish ("En ung mand og en grædende ung pige med kysehat"); English titles, where SMK wrote them,
                      are used as they are and marked "twinned". ARCHIVE_TRANSLATE names the Danish model
                      (opus-mt-tc-big-gmq-en, CC BY 4.0, already used for Swedish and Norwegian), so the build adds
                      English translation twins as for the other languages.
  anefo               Nationaal Archief (the Netherlands) photographs, mostly the Anefo press agency (1945-1989): about
                      430,000 photos with their Dutch captions, CC0 or public domain (both scan and metadata,
                      https://www.nationaalarchief.nl/onderzoeken/open-data/fotos). The Archive's own API is
                      "temporarily unavailable", so the files come from the copy the Archive put on Wikimedia Commons
                      ("Images from Nationaal Archief"), with the Dutch caption ("Beschrijving") and place ("Locatie",
                      or the Netherlands when the file is filed under "Netherlands photographs taken on ...").
                      Many show public figures and events. Dutch translation twins with the model already used for
                      Rijksmuseum texts; captions in English are marked "twinned".
  kremlin             Photographs on the Russian President's English website (en.kremlin.ru), with their captions and
                      the place each gallery gives. "All content on this site is licensed under Creative Commons
                      Attribution 4.0 International" (the site's footer). Most show meetings and ceremonies; the place
                      is kept only when the gallery names a Russian place or a country.
  awm                 Australian War Memorial: photographs whose record says "Copyright expired - public domain",
                      with the Memorial's caption (mostly the First and Second World Wars) and the place from the
                      record.

Looked at and not used here (checked at the source in November 2026), with the reason; the ones under a licence
that is not open are kit entries in training-kit/kit/archive_sources.py:
  NARA catalogue API v2         Needs an API key (sign-up); the catalogue's own public search (used above) does not.
  DVIDS (US military photos)    Public domain, but its API refuses every request without a key (sign-up).
  FEMA photo library            Public domain, but www.fema.gov/multimedia-library refused this machine (Akamai 403).
  Voice of America photos       VOA's own photos are public domain, but most photos on its pages are AP, Reuters or AFP
                                wire photos (commercial agencies, not used); there is no list of VOA's own photos.
  White House, State Department, NIH Image Gallery, US Army, UK National Archives, Chilean and Argentine government
  photos, Biodiversity Heritage Library    On Flickr, which needs a free API key (sign-up).
  Naval History and Heritage Command   Public domain, but www.history.navy.mil sends an incomplete certificate chain,
                                so no secure connection could be made from this machine.
  NYPL Digital Collections API  Needs a token (sign-up); the bulk CC0 metadata release (used above) does not.
  State Library of New South Wales, State Library Victoria, Library and Archives Canada, Danish Royal Library
                                Their sites refused this machine (Cloudflare checks, proxy errors or a broken API).
  Paris Musées                  CC0, but its API needs a token (sign-up) and answered "service unavailable".
  Harvard Art Museums           Needs an API key (sign-up).
  Yale Center for British Art, Finnish National Gallery, Nationalmuseum Sweden, Belvedere, British Museum, Imperial
  War Museums, Science Museum Group    Their collection sites refused this machine (Cloudflare checks) or their API
                                answered with an error; listed with their licences in archive_sources.py.
  Natural History Museum London, Naturalis, Museum für Naturkunde    Their specimen photos have names, not written
                                descriptions; named specimens from these museums already reach the kit through GBIF
                                (the gbif_species pack).
  Wikinews                      Its captions are CC BY 2.5, but Wikinews's API refused this machine (too many
                                requests); its photos are Commons files, many already in the commons packs.
  Agência Brasil                Its reproduction policy now allows journalistic use with credit only (commercial use
                                needs permission): a personal-use kit entry, not an open pack.

    python packs/archive_packs.py nara --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, LONG_SIDE
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from build_packs import listing_out_of_time  # noqa: E402
from food_packs import count_pictures
from expression_packs import CHILD
from world_packs import capped_words, full_stop
from places import country_named, place_name, place_from_text
from documentary_packs import tidy, usable, picture_rows, get_json, finish, commons_get, NOT_SHOWN

# Words that mean a photo shows the dead, wounds, disaster casualties or other graphic scenes (war archives have
# many). By the owner's rule such photos are kept, described plainly from the record, and their rows carry
# "content": "graphic" (so the kit can leave them out of picture-making and show them only when chosen).
GRIM = re.compile(r"\b(dead(?! sea\b| end\b)|corpses?|bod(y|ies) of|killed|wounded|wounds?|casualt\w*|injur\w*|"
                  r"bleeding|blood|"
                  r"grave|graves|burial|buried|massacre|atrocit\w*|skeleton\w*|remains of|mutilat\w*|amputat\w*|"
                  r"lijk\w*|doden|dode|gewond\w*|gesneuveld\w*|slachtoffers?|døde?|lig|såret)\b", re.I)
# Still left out whatever the record says: sexual violence, and torture or execution scenes (and their propaganda).
NEVER_SHOWN = re.compile(r"\b(rape[ds]?|raping|sexual(ly)? (assault\w*|abuse\w*|violence)|molest\w*|verkracht\w*|"
                         r"voldtægt\w*|tortur\w*|execut\w*|beheading|hanged|hanging bodies|lynch\w*|firing squad|"
                         r"marteling\w*|gemarteld|executie\w*|terechtgesteld|henrettelse\w*)\b", re.I)
# Words for children in Danish and Dutch that expression_packs.CHILD does not have.
CHILD_MORE = re.compile(r"\b(kinderen|kindje|børn|barn|barnet|drenge?|drengen|piger?|pigen|spædbarn|kleuters?|"
                        r"peuters?|"
                        r"scholieren|scholier|schoolkinderen|zuigeling\w*|jeugd)\b", re.I)
# Words for nudes in Danish and Dutch (documentary_packs.NOT_SHOWN has the English ones).
NUDE_MORE = re.compile(r"\b(nøgen|nøgne|halvnøgen|akt|aktstudie|aktmodel|afklædt|draperet|half[- ]draped|naakt\w*|"
                       r"bloot|ontkleed|ontbloot\w*|badende|bathers?|bathing)\b", re.I)
# Old slurs found in some 1940s captions: such captions are left out rather than repeated.
SLURS = re.compile(r"\b(japs?|nips?|niggers?|negroes|coloreds?|squaws?|redskins?)\b", re.I)

US_STATES = ("Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
             "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
             "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
             "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
             "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
             "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",
             "Wyoming", "District of Columbia", "Puerto Rico")
# The Library of Congress's short forms of US states in place headings ("Nucla (Colo.)").
LC_STATES = {"Ala.": "Alabama", "Ariz.": "Arizona", "Ark.": "Arkansas", "Calif.": "California", "Colo.": "Colorado",
             "Conn.": "Connecticut", "Del.": "Delaware", "D.C.": "District of Columbia", "Fla.": "Florida",
             "Ga.": "Georgia", "Ill.": "Illinois", "Ind.": "Indiana", "Kan.": "Kansas", "Kans.": "Kansas",
             "Ky.": "Kentucky", "La.": "Louisiana", "Md.": "Maryland", "Mass.": "Massachusetts", "Mich.": "Michigan",
             "Minn.": "Minnesota", "Miss.": "Mississippi", "Mo.": "Missouri", "Mont.": "Montana", "Neb.": "Nebraska",
             "Nebr.": "Nebraska", "Nev.": "Nevada", "N.H.": "New Hampshire", "N.J.": "New Jersey",
             "N.M.": "New Mexico", "N.Mex.": "New Mexico", "N.Y.": "New York", "N.C.": "North Carolina",
             "N.D.": "North Dakota", "N.Dak.": "North Dakota", "Okla.": "Oklahoma", "Or.": "Oregon",
             "Ore.": "Oregon", "Pa.": "Pennsylvania", "R.I.": "Rhode Island", "S.C.": "South Carolina",
             "S.D.": "South Dakota", "S.Dak.": "South Dakota", "Tenn.": "Tennessee", "Tex.": "Texas", "Vt.": "Vermont",
             "Va.": "Virginia", "Wash.": "Washington", "W.Va.": "West Virginia", "W. Va.": "West Virginia",
             "Wis.": "Wisconsin", "Wyo.": "Wyoming", "P.R.": "Puerto Rico"}
for _state in US_STATES:
    LC_STATES.setdefault(_state, _state)
# Words that keep their capital letter when an all-capitals caption is put in sentence case.
CAPITALS = {w.lower(): w for w in (
    "I", "US", "U.S.", "USA", "EPA", "UN", "NASA", "TVA", "WPA", "CCC", "WRA", "RAAF", "AIF", "RAN", "HMAS", "HMS",
    "USS", "RAF", "WW", "II", "III", "IV", "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday", "Sunday", "American", "Americans", "Indian", "Indians", "Mexican", "Hawaiian", "Japanese", "Chinese",
    "English", "Spanish", "Navajo", "Hopi", "Christmas", "Easter", "Australia", "Australian", "Australians",
    "British", "German", "Germans", "Japan", "Guinea", "Papua", "Borneo", "France", "Egypt", "Palestine",
    "Gallipoli", "Europe", "Pacific", "Atlantic", "Mississippi", "Missouri", "Ohio", "Hudson", "Colorado",
    "Sydney", "Melbourne", "Brisbane", "Adelaide", "Perth", "Darwin", "Canberra", "Victoria", "Queensland",
    "Tasmania", "Wales", "London")}
for _state in US_STATES:                 # one-word states; "New", "North" and the like only from the record's places
    if " " not in _state:
        CAPITALS[_state.lower()] = _state


def mostly_capitals(text):
    """True when at least four in five of a text's letters are capitals (a caption typed in capitals)."""
    letters = [c for c in text if c.isalpha()]
    return len(letters) > 10 and sum(c.isupper() for c in letters) >= 0.8 * len(letters)


def sentence_case(text, names=()):
    """An all-capitals caption in sentence case: lower case, a capital at the start of each sentence, and capitals
    kept for CAPITALS, the words of names (place names from the record), words in quotation marks and short
    letter-and-number codes ("H-1", "B-17"). A caption not in capitals comes back as it is."""
    if not mostly_capitals(text):
        return text
    keep = dict(CAPITALS)
    for name in names:
        for word in re.findall(r"[A-Za-z][\w'’-]*", name or ""):
            keep[word.lower()] = word[:1].upper() + word[1:]
    quoted = {w.lower() for q in re.findall(r"[\"“]([^\"”]+)[\"”]", text) for w in q.split()}

    def one(m):
        """One word, in lower case unless it is kept."""
        whole = m.group(0)
        if re.search(r"\d", whole):                   # codes stay ("H-1", "B-17"); "105TH" -> "105th"
            return whole.lower() if re.match(r"^\d+(ST|ND|RD|TH)\.?$", whole) else whole
        word = whole.rstrip(".")                      # "BRITAIN." -> "BRITAIN" and "."; "U.S." stays
        if word.lower() + "." in keep:
            word = whole
        tail = whole[len(word):]
        low = word.lower()
        if low in keep:
            return keep[low] + tail
        if low.strip("\"“”") in quoted:
            return low[:1].upper() + low[1:] + tail
        return low + tail

    out = re.sub(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", one, text)
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)


def lc_place(heading):
    """A US place heading in the Library of Congress form ("Honolulu (Hawaii)", "Nucla (Colo.)", "Wisconsin",
    "Calaveras County (Calif.)") as a row's place ("Honolulu, Hawaii, USA"); a heading naming another country
    ("Paris (France)") gives "Paris, France"; "" when it is not understood."""
    heading = clean(heading).strip(" .")
    m = re.match(r"^(.+?)\s*\(([^()]+)\)$", heading)
    if m:
        town, region = m.group(1).strip(), m.group(2).strip()
        if region in LC_STATES:
            if re.search(r"\b(county|parish)$", town, re.I):
                return place_name(LC_STATES[region], "USA")
            return place_name(town, LC_STATES[region], "USA")
        country = country_named(region)
        return place_name(town, country) if country else ""
    if heading in LC_STATES:
        return place_name(LC_STATES[heading], "USA")
    return place_from_text(heading)


def child_rows(rows, *texts):
    """Rows marked "child" also when any of texts names a child in Danish or Dutch (CHILD_MORE)."""
    if any(CHILD_MORE.search(t or "") for t in texts):
        return [dict(r, child=True) for r in rows]
    return rows


def not_shown(*texts):
    """True when any text says something sexual (in English, Danish or Dutch), names sexual violence, torture or an
    execution, holds an old slur, or shows a dead or injured child (graphic words and child words together): such
    a picture is left out. Other graphic pictures are kept and marked (graphic_rows)."""
    joined = " ".join(t for t in texts if t)
    if GRIM.search(joined) and (CHILD.search(joined) or CHILD_MORE.search(joined)):
        return True
    return bool(joined) and bool(NOT_SHOWN.search(joined) or NUDE_MORE.search(joined) or NEVER_SHOWN.search(joined)
                                 or SLURS.search(joined))


def graphic_rows(rows):
    """Rows marked "content": "graphic" when their picture's caption names the dead, wounds or casualties."""
    if any(GRIM.search(r.get("answer", "")) for r in rows):
        return [dict(r, content="graphic") for r in rows]
    return rows


def finish_marked(key, items, limit, workers=4, pause=0.2):
    """documentary_packs.finish, after marking the graphic pictures among items (name, address, rows) and leaving
    out any that not_shown refuses; says how many are graphic."""
    items = [(n, u, graphic_rows(rows)) for n, u, rows in items if not not_shown(*(r["answer"] for r in rows))]
    entries = finish(key, items, limit, workers=workers, pause=pause)
    say(f"{key}: {sum(1 for _, d, r in entries if d is not None and r.get('content') == 'graphic')} pictures marked "
        "graphic")
    return entries


# ----------------------------------------------------------------- US National Archives

NARA = "https://catalog.archives.gov/"
NARA_SEARCH = NARA + "proxy/records/search"           # the catalogue's own public search (the v2 API needs a key)
# The series: (catalogue id, number of online items, name in the credit).
NARA_SERIES = [
    (542493, 15900, "DOCUMERICA: The Environmental Protection Agency's Program to Photographically Document Subjects "
                    "of Environmental Concern, 1972-1977, Records of the Environmental Protection Agency (412-DA)"),
    (536000, 4000, "Central Photographic File of the War Relocation Authority, 1942-1945, Records of the War "
                   "Relocation Authority (210-G)"),
    (519830, 220, "Ansel Adams Photographs of National Parks and Monuments, 1941-1942, Records of the National Park "
                  "Service (79-AA)"),
]
# Notes in DOCUMERICA titles that are not a description.
NARA_NOTES = re.compile(r"\s*\((?:FROM THE [^)]*|SEQUENCE|VERTICAL[^)]*|HORIZONTAL[^)]*|NOTE:[^)]*|[^)]*FICHE[^)]*)\)|"
                        r"\s*\b\d{1,2}/\d{4}\b|\s*\.\s*\.\s*\.\s*$|^\s*Photograph of\s+", re.I)
WRA_FULL = re.compile(r"^\s*The full caption for this photograph reads:\s*", re.I)
NARA_MOST_BYTES = 4_000_000         # larger files (20 MB scans) are left out


def nara_picture(record):
    """The address of a record's smallest usable picture (a JPEG, GIF or small TIFF under NARA_MOST_BYTES), or ""."""
    best, best_rank = "", 9
    for obj in record.get("digitalObjects") or []:
        kind, url = obj.get("objectType") or "", obj.get("objectUrl") or ""
        size = int(obj.get("objectFileSize") or 0)
        if not url or not size or size > NARA_MOST_BYTES:
            continue
        rank = 0 if "JPG" in kind or "JPEG" in kind else 1 if "GIF" in kind else 2 if "TIFF" in kind else 9
        if rank < best_rank:
            best, best_rank = url, rank
    return best


def nara_caption(record):
    """(caption, place words) of a NARA record: the WRA's full caption (its scope note) or the title, without
    exhibition notes, fiche numbers and dates, in sentence case when typed in capitals."""
    title = clean(record.get("title"))
    note = clean(record.get("scopeAndContentNote"))
    text = WRA_FULL.sub("", note) if WRA_FULL.match(note) else title
    text = re.sub(r"\s*--\s*", ", ", NARA_NOTES.sub("", text)).strip(" .")
    places = [clean(s.get("heading")) for s in record.get("subjects") or []
              if s.get("authorityType") == "geographicPlaceName"]
    return sentence_case(text, places), places


def wra_place(caption):
    """The place a WRA caption opens with ("Heart Mountain Relocation Center, Heart Mountain, Wyoming. ...") as
    "Heart Mountain, Wyoming, USA"; "" when its first sentence does not end with a US state."""
    first = re.split(r"(?<=[a-z])\.\s", caption, maxsplit=1)[0]
    parts = [p.strip(" .\"'") for p in first.split(",")]
    if len(parts) >= 2 and parts[-1] in US_STATES:
        return place_name(parts[-2], parts[-1], "USA")
    last = caption.rstrip(" .").rsplit(",", 1)                  # Ansel Adams: "..., Yosemite," California.
    if len(last) == 2 and last[1].strip(" .\"'") in US_STATES:
        return place_name(last[1].strip(" .\"'"), "USA")
    return ""


def nara_items(s, naid, total, name, want, rng):
    """[(name, picture address, rows)] from random result pages of one NARA series (the search reaches its first
    10,000 records), a few from each page and each caption once."""
    pages = list(range(1, max(2, min(total, 10000) // 100) + 1))
    rng.shuffle(pages)
    items, answers = [], set()
    per_page = max(3, want // 20)
    for page in pages[:60]:
        if listing_out_of_time():          # leave the rest of the time for fetching
            break
        time.sleep(1)
        data = get_json(s, NARA_SEARCH, {"ancestorNaId": naid, "availableOnline": "true", "limit": 100,
                                         "page": page}, pause=10)
        hits = (((data or {}).get("body") or {}).get("hits") or {}).get("hits") or []
        taken = 0
        for hit in hits:
            record = (hit.get("_source") or {}).get("record") or {}
            if (record.get("useRestriction") or {}).get("status") != "Unrestricted" or taken >= per_page:
                continue
            caption, places = nara_caption(record)
            answer = tidy(capped_words(caption, 80))
            picture = nara_picture(record)
            if not picture or not usable(answer) or answer in answers or not_shown(answer):
                continue
            answers.add(answer)
            taken += 1
            place = next((p for p in map(lc_place, places) if p), "") or wra_place(caption)
            who = next((clean(c.get("heading")) for c in record.get("contributors") or []
                        if c.get("contributorType") == "Photographer"), "")
            who = re.sub(r",\s*\d{4}-(\d{4})?$", "", who)
            credit = (f"{clean(record.get('title'))[:150]}" + (f", photographer {who}" if who else "")
                      + f", {name}, U.S. National Archives and Records Administration, public domain (US government "
                        f"work), {NARA}id/{record.get('naId')}")
            items.append((f"nara-{record.get('naId')}.jpg", picture, picture_rows(answer, credit, place)))
        if len(items) >= want:
            break
    say(f"  NARA {name.split(':')[0].split(',')[0]}: {len(items)} usable records")
    return items


def build_nara(limit):
    """The NARA pack: records from each series in NARA_SERIES, in proportion to their size (at least a sixth of the
    pack each, or the whole series when it is smaller)."""
    s, rng, items = session(), pass_random(301), []
    total = sum(n for _, n, _ in NARA_SERIES)
    for naid, n, name in NARA_SERIES:
        share = max(1 / 6, n / total)
        items += nara_items(s, naid, n, name, int(limit * share * 1.3) + 3, rng)
    return finish_marked("nara", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- New York Public Library

NYPL_ITEMS = ("https://raw.githubusercontent.com/NYPL-publicdomain/data-and-utilities/master/items/pd_items_1.csv",
              "https://raw.githubusercontent.com/NYPL-publicdomain/data-and-utilities/master/items/pd_items_2.csv")
# Kinds of item that are not photographs or pictures of the world: left out.
NYPL_NOT_A_PHOTO = re.compile(r"\b(maps?|menus?|atlases|charts?|plans?|sheet music|scores?|manuscripts?|letters?|"
                              r"broadsides?|book ?plates?|title pages?|text|newspapers?|periodicals?|"
                              r"specimens?|ornaments?|patterns?|diagrams?|playbills?|programs?|tickets?|"
                              r"trade cards?|portrait prints?)\b", re.I)
NYPL_PHOTO = re.compile(r"photograph|stereoscopic|postcard|lantern slide|albumen|gelatin|glass negative|"
                        r"cyanotype|platinum print", re.I)
# Titles, subjects and collections of maps and charts (some are typed "still image").
NYPL_MAP = re.compile(r"\b(maps?|map of|chart of|charts|atlas\w*|plan of|plans|nautical|cartograph\w*|"
                      r"geographical|bird's-eye view|panoramic view)\b|--\s*Maps", re.I)
NYPL_GENRES = re.compile(r"photograph|stereoscopic|postcard|lantern slide|albumen|gelatin|glass negative|"
                         r"lithograph|engraving|etching|watercolor|drawing|chromolithograph|woodcut|print", re.I)


def nypl_rows(want, small):
    """Candidate rows of the NYPL item tables, read as they download; when small is True (a quick check) reading
    stops early, otherwise both tables (about 150 MB) are read and a random sample kept."""
    import requests
    csv.field_size_limit(10 ** 8)
    rng, kept, seen = pass_random(302), [], 0
    for url in NYPL_ITEMS:
        with requests.get(url, stream=True, timeout=300, headers={"User-Agent": build_packs.USER_AGENT}) as r:
            r.raw.decode_content = True
            reader = csv.DictReader(io.TextIOWrapper(r.raw, encoding="utf-8", errors="replace", newline=""))
            try:
                for row in reader:
                    kinds = row.get("Resource Type") or ""
                    if "still image" not in kinds or "cartographic" in kinds or not row.get("First Image") \
                            or NYPL_MAP.search(" ".join(row.get(k) or "" for k in ("Title", "Subject Topical",
                                                                                   "Collection Title"))):
                        continue
                    genre = row.get("Genre") or ""
                    if NYPL_NOT_A_PHOTO.search(genre + " " + (row.get("Physical Description Form") or "")) \
                            or (genre and not NYPL_GENRES.search(genre)):
                        continue
                    seen += 1
                    if len(kept) < want:
                        kept.append(row)
                    else:                                  # a random sample of everything read
                        j = rng.randrange(seen)
                        if j < want:
                            kept[j] = row
                    if small and seen >= want * 12:
                        return kept
            except (csv.Error, Exception) as e:  # noqa: BLE001 - a cut-off download ends the table
                say(f"  NYPL table ended early: {e}")
    return kept


def nypl_place(row):
    """The place of an NYPL item from its first geographic subject ("Calaveras County (Calif.)", "New York (N.Y.)",
    "California", "Egypt"), or ""."""
    for heading in (row.get("Subject Geographic") or "").split("|"):
        heading = heading.split("--")[0].strip()
        place = lc_place(heading)
        if place:
            return place
    return ""


def build_nypl(limit):
    """The NYPL pack: public-domain still images whose title (with the description, where there is one) is 6 words
    or more; the Library's 1,600-pixel copy of the first image."""
    rows = nypl_rows(int(limit * 4) + 40, small=limit < 300)
    items, answers = [], set()
    for row in rows:
        title = tidy(row.get("Title"))
        description = clean(row.get("Description"))
        answer = title
        if description and description.lower()[:30] not in title.lower():
            answer = tidy(capped_words(f"{full_stop(title)} {description}", 70)) if title else tidy(description)
        if not usable(answer) or answer in answers or not_shown(answer, row.get("Subject Topical")):
            continue
        answers.add(answer)
        # "w" is the Library's large copy that every item has (its 1,600-pixel "q" copy is missing for many).
        picture = re.sub(r"&t=\w+$", "&t=w", row["First Image"].replace("http://", "https://"))
        link = (row.get("Digital Collections URL") or "").replace("http://", "https://")
        collection = clean(row.get("Collection Title"))
        credit = (f"{clean(row.get('Title'))[:150]}, The New York Public Library"
                  + (f", {collection}" if collection else "") + f", no known US copyright restrictions, {link}")
        place = nypl_place(row)
        if NYPL_PHOTO.search(row.get("Genre") or ""):          # a photograph: where it was taken
            rows = picture_rows(answer, credit, place, [row.get("Subject Topical")])
        else:                                                    # a print or drawing: the place it shows
            rows = picture_rows(answer, credit, "", [row.get("Subject Topical")])
            rows = [dict(r, place=place, place_kind="depicted") for r in rows] if place else rows
        items.append((f"nypl-{row.get('UUID') or len(items)}.jpg", picture, rows))
    say(f"NYPL: {len(items)} usable items")
    return finish_marked("nypl", items, limit, workers=4, pause=0.3)


# ----------------------------------------------------------------- J. Paul Getty Museum

GETTY_SPARQL = "https://data.getty.edu/museum/collection/sparql"
GETTY_DESCRIPTION = "http://vocab.getty.edu/aat/300080091"
GETTY_QUERY = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
SELECT DISTINCT ?o WHERE {{ ?o a crm:E22_Human-Made_Object ; crm:P138i_has_representation ?r ;
  crm:P67i_is_referred_to_by ?s . ?s crm:P2_has_type <{description}> . }} ORDER BY ?o LIMIT {limit} OFFSET {offset}"""
GETTY_TOTAL = 62000                 # objects with a picture and a description (counted in November 2026)


def getty_text(record, label):
    """The plain text (not the HTML copy) of a Getty record's statement whose types include label, or ""."""
    for statement in record.get("referred_to_by") or []:
        labels = [c.get("_label") for c in statement.get("classified_as") or []]
        content = statement.get("content") or ""
        if label in labels and "<" not in content:
            return clean(content)
    for statement in record.get("referred_to_by") or []:
        if label in [c.get("_label") for c in statement.get("classified_as") or []]:
            return clean(statement.get("content"))
    return ""


def getty_object(s, uri):
    """(name, picture address, rows) of one Getty object whose record says "No Copyright" and has a description of
    6 words or more, or None."""
    record = get_json(s, uri, tries=2)
    if not record or getty_text(record, "Rights Statement") != "No Copyright":
        return None
    answer = tidy(capped_words(getty_text(record, "Description"), 80))
    title = re.sub(r"\s*\([^()]*\)$", "", clean(record.get("_label")))
    pictures = [r.get("id") for r in record.get("representation") or [] if "/iiif/image/" in (r.get("id") or "")]
    if not pictures or not usable(answer) or not_shown(answer, title):
        return None
    picture = re.sub(r"/full/full/0/default\.jpg$", f"/full/!{LONG_SIDE},{LONG_SIDE}/0/default.jpg", pictures[0])
    maker = clean(((record.get("produced_by") or {}).get("_label") or "").replace("Production of Artwork by", ""))
    page = next((p.get("id") for p in record.get("subject_of") or []
                 if "/art/collection/object/" in (p.get("id") or "")), uri)
    credit = (f"{title}" + (f", {maker}" if maker and maker.lower() != "unknown" else "")
              + f", The J. Paul Getty Museum, Los Angeles, Open Content (no copyright; metadata CC0), {page}")
    place = place_from_text(getty_text(record, "Creation Place Description"))
    rows = picture_rows(answer, credit)
    if place:                         # where the object was made, not where a photo was taken: no "where" question
        rows = [dict(r, place=place, place_kind="origin") for r in rows]
    return f"getty-{uri.rsplit('/', 1)[-1]}.jpg", picture, rows


def build_getty_museum(limit):
    """The Getty pack: objects found with the museum's SPARQL service (random pages of the about 62,000 with a
    picture and a description), each record read to keep only "No Copyright" ones."""
    s, rng, items = session(), pass_random(303), []
    offsets = list(range(0, GETTY_TOTAL, 200))
    rng.shuffle(offsets)
    for offset in offsets:
        if len(items) >= limit * 1.3:
            break
        try:
            r = s.post(GETTY_SPARQL, data={"query": GETTY_QUERY.format(description=GETTY_DESCRIPTION, limit=200,
                                                                         offset=offset)},
                       headers={"Accept": "application/sparql-results+json"}, timeout=180)
            uris = [b["o"]["value"] for b in r.json()["results"]["bindings"]]
        except Exception:  # noqa: BLE001 - next page
            continue
        rng.shuffle(uris)
        for uri in uris[:max(4, int(limit * 1.5 / 20) + 2)]:
            item = getty_object(s, uri)
            time.sleep(0.2)
            if item:
                items.append(item)
    say(f"Getty Museum: {len(items)} usable objects")
    return finish_marked("getty_museum", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- Digital Commonwealth (Massachusetts)

DC = "https://www.digitalcommonwealth.org/"
DC_IIIF = "https://iiif.digitalcommonwealth.org/iiif/2/{}/full/!{},{}/0/default.jpg"


def dc_place(a):
    """The place of a Digital Commonwealth record from its place hierarchy ("Needham, Massachusetts, USA"), or ""."""
    for text in a.get("subject_hiergeo_geojson_ssm") or []:
        try:
            p = json.loads(text).get("properties") or {}
        except ValueError:
            continue
        country = country_named(p.get("country"))
        if not country:
            continue
        town = p.get("city") or p.get("city_section") or p.get("area") or ""
        state = p.get("state") or p.get("region") or ""
        return place_name(town, state, country)
    return ""


def described(answer, most=3):
    """True when a title says what is in the picture, not only names and dates: at least most words in lower case
    ("Mary E. Archer, barn, Enfield, Mass., May 25, 1928." has one: a property list, not a description)."""
    return len([w for w in re.findall(r"[A-Za-z]+", answer) if w.islower() and len(w) > 2]) >= most


def dc_items(s, reuse, want, rng, genre="Photographs"):
    """[(name, picture address, row text, record)] of random result pages of Digital Commonwealth photographs with
    one reuse value ("no restrictions" or "creative commons"); each record's title (and abstract) of 6 words or
    more."""
    params = {"per_page": 100, "f[genre_basic_ssim][]": genre, "f[reuse_allowed_ssi][]": reuse}
    first = get_json(s, DC + "search.json", dict(params, page=1)) or {}
    pages = list(range(1, int(((first.get("meta") or {}).get("pages") or {}).get("total_pages") or 1) + 1))
    rng.shuffle(pages)
    found, answers = [], set()
    per_page = max(2, want // 25)          # a page holds one series (pages are in title order): a few from each
    for page in pages[:120]:
        if listing_out_of_time():          # leave the rest of the time for fetching
            break
        time.sleep(1)
        data = get_json(s, DC + "search.json", dict(params, page=page)) or {}
        taken = 0
        for x in data.get("data") or []:
            a = x.get("attributes") or {}
            title = clean(a.get("title_info_primary_tsi"))
            abstract = clean(a.get("abstract_tsi"))
            text = title
            if abstract and abstract.lower()[:30] not in title.lower():
                text = f"{full_stop(title)} {abstract}"
            answer = tidy(capped_words(text, 70))
            if not a.get("exemplary_image_ssi") or not usable(answer) or not described(answer) \
                    or answer in answers or not_shown(answer) or taken >= per_page:
                continue
            answers.add(answer)
            taken += 1
            found.append((answer, a))
        if len(found) >= want:
            break
    return found


def build_digital_commonwealth(limit):
    """The Digital Commonwealth pack: photographs marked "No known copyright restrictions"."""
    s, rng, items = session(), pass_random(304), []
    for answer, a in dc_items(s, "no restrictions", int(limit * 1.3) + 4, rng):
        ark = a.get("identifier_uri_ss") or DC + "search/" + a["id"]
        who = clean(a.get("institution_name_ssi")) or "Digital Commonwealth"
        credit = (f"{clean(a.get('title_info_primary_tsi'))[:150]}, {who}, via Digital Commonwealth, "
                  f"{clean(a.get('rights_ss')) or 'No known copyright restrictions.'} {ark}")
        picture = DC_IIIF.format(a["exemplary_image_ssi"], LONG_SIDE, LONG_SIDE)
        items.append((f"dc-{a['id'].split(':')[-1]}.jpg", picture, picture_rows(answer, credit, dc_place(a))))
    say(f"Digital Commonwealth: {len(items)} usable photographs")
    return finish_marked("digital_commonwealth", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- Statens Museum for Kunst (Denmark)

SMK = "https://api.smk.dk/api/v1/art/search/"
SMK_TOTAL = 39500                   # public-domain works with a picture (November 2026)


def smk_titles(item):
    """(English title, Danish title) of an SMK work: the first title of 6 words or more in each language."""
    english = danish = ""
    for t in item.get("titles") or []:
        text = tidy(t.get("title"))
        if not usable(text):
            continue
        language = (t.get("language") or "").lower()
        if language.startswith("eng") and not english:
            english = text
        elif language.startswith(("dan", "dansk")) and not danish:
            danish = text
    return english, danish


def build_smk(limit):
    """The SMK pack: public-domain works with a descriptive title (random pages of the about 39,500), SMK's
    1,024-pixel copy. English titles are marked "twinned" (not translated again)."""
    s, rng, items = session(), pass_random(305), []
    offsets = list(range(0, SMK_TOTAL, 100))
    rng.shuffle(offsets)
    for offset in offsets[:200]:
        if len(items) >= limit * 1.3:
            break
        time.sleep(0.5)
        data = get_json(s, SMK, {"keys": "*", "offset": offset, "rows": 100, "lang": "en",
                                 "filters": "[has_image:true],[public_domain:true]"}) or {}
        taken = 0
        for item in data.get("items") or []:
            english, danish = smk_titles(item)
            answer = english or danish
            rights = item.get("rights") or ""
            picture = item.get("image_thumbnail") or ""
            if not answer or not picture or not item.get("public_domain") or not_shown(answer) \
                    or not described(answer) or not re.search(r"publicdomain/(zero|mark)", rights) \
                    or taken >= max(2, limit // 25):         # a page holds one artist: a few from each
                continue
            taken += 1
            artist = ", ".join(clean(p.get("creator")) for p in (item.get("production") or [])[:2]
                               if clean(p.get("creator")))
            credit = (f"{answer[:150].rstrip('.')}" + (f", {artist}" if artist else "")
                      + f", Statens Museum for Kunst (SMK), public domain ({rights}), {item.get('frontend_url', '')}")
            rows = child_rows(picture_rows(answer, credit), answer)
            if english:
                rows = [dict(r, twinned=True) for r in rows]
            items.append((f"smk-{re.sub(r'[^\w-]', '_', item.get('object_number') or item['id'])}.jpg", picture,
                          rows))
    say(f"SMK: {len(items)} usable works")
    return finish_marked("smk", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- Nationaal Archief (Anefo), via Commons

ANEFO_CATEGORY = "Category:Images from Nationaal Archief"
def wiki_param(text, name):
    """The value of a template parameter (|name = value) in wikitext, or ""."""
    m = re.search(r"\|\s*" + re.escape(name) + r"\s*=\s*(.*?)(?=\n\s*\||\n\}\})", text, re.S | re.I)
    return m.group(1).strip() if m else ""


def anefo_fields(wikitext):
    """{field: value} of a Nationaal Archief file's description on Commons, which copies the Archive's record line
    by line ("Beschrijving : Kaagweek 1959, Regenbogen in actie<br>", "Datum : 19 juli 1959<br>", "Locatie : ...")."""
    description = wiki_param(wikitext, "description")
    description = re.sub(r"^\{\{\s*nl\s*\|\s*(?:1\s*=\s*)?", "", description)
    description = re.sub(r"\{\{\s*w\s*\|[^|}]*\|([^}]*)\}\}", r"\1", description)   # {{w|link|text}} -> text
    description = re.sub(r"\{\{\s*w\s*\|([^}]*)\}\}", r"\1", description)           # {{w|name}} -> name
    description = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", description)       # [[link|text]] -> text
    fields = {}
    for line in re.split(r"<br\s*/?>|\n", description):
        m = re.match(r"^\s*([A-Za-zÀ-ÿ /]+?)\s*:\s*(.*?)\s*(\}\})?\s*$", line)
        if m:
            fields.setdefault(m.group(1).strip().lower(), clean(m.group(2)))
    return fields


def english(text):
    """True when a caption is in English rather than Dutch (more common English little words than Dutch ones)."""
    words = re.findall(r"[a-z]+", text.lower())
    return sum(w in ("the", "and", "of", "with", "to", "is", "has", "at", "on") for w in words) > \
        sum(w in ("de", "het", "een", "en", "van", "met", "op", "bij", "te", "tijdens") for w in words)


def anefo_place(fields, wikitext):
    """The place of a Nationaal Archief photo from its record: the "Locatie" field (a Dutch town, or a place naming
    its country) and, when the file is in a "Netherlands photographs taken on ..." category, the Netherlands; ""
    when the record says nothing."""
    dutch = bool(re.search(r"\[\[Category:Netherlands photographs taken on", wikitext))
    location = re.sub(r"\[\s*onbekend\s*\]", "", fields.get("locatie", "")).strip(" ,;")
    parts = [p.strip() for p in re.split(r"[,;]", location) if p.strip()]
    if parts:
        country = country_named(parts[-1])
        if country:
            return place_name(*parts[:-1][:2], country)
        if dutch and len(parts[0]) < 40:
            return place_name(parts[0], "Netherlands")
    return "Netherlands" if dutch else ""


def build_anefo(limit):
    """The Nationaal Archief pack: files of the Commons category (about 430,000), read 50 at a time from random
    starting letters, whose licence is CC0 or public domain and whose Dutch caption is 6 words or more."""
    s, rng, items, seen = session(), pass_random(306), [], set()
    starts = [a + b for a in "ABCDEFGHIJKLMNOPRSTVWZ" for b in "aeiou"]
    rng.shuffle(starts)
    for start in starts:
        if len(items) >= limit * 1.3:
            break
        data = commons_get(s, {"action": "query", "generator": "categorymembers", "gcmtitle": ANEFO_CATEGORY,
                               "gcmtype": "file", "gcmlimit": 50, "gcmstartsortkeyprefix": start,
                               "prop": "imageinfo|revisions", "rvprop": "content", "rvslots": "main",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 1600,
                               "iiextmetadatafilter": "LicenseShortName|Artist"})
        pages = [p for p in ((data.get("query") or {}).get("pages") or {}).values() if p.get("pageid")]
        taken = 0
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            licence = clean(((info.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value"))
            wikitext = (((p.get("revisions") or [{}])[0].get("slots") or {}).get("main") or {}).get("*", "")
            fields = anefo_fields(wikitext)
            answer = tidy(capped_words(fields.get("beschrijving", ""), 70))
            if p["pageid"] in seen or not re.match(r"^(cc0|cc-zero|public domain|pd)", licence, re.I) \
                    or not usable(answer) or not_shown(answer) or info.get("mime") != "image/jpeg" \
                    or not info.get("thumburl") or taken >= max(3, limit // 15):
                continue
            seen.add(p["pageid"])
            taken += 1
            artist = fields.get("fotograaf") or clean(((info.get("extmetadata") or {}).get("Artist") or {})
                                                       .get("value")) or "unknown"
            collection = fields.get("collectie / archief", "")
            credit = (f"{answer[:120]} Foto: {artist[:80]}, Nationaal Archief"
                      + (f" / {collection}" if collection else "") + f", {licence} "
                      f"(https://www.nationaalarchief.nl/onderzoeken/open-data/fotos), copy on Wikimedia Commons: "
                      f"https://commons.wikimedia.org/wiki/{p['title'].replace(' ', '_')}")
            rows = child_rows(picture_rows(answer, credit, anefo_place(fields, wikitext)), answer)
            if english(answer):                 # some captions (mostly from British agencies) are in English
                rows = [dict(r, twinned=True) for r in rows]
            items.append((f"anefo-{p['pageid']}.jpg", info["thumburl"], rows))
        time.sleep(1)
    say(f"Nationaal Archief: {len(items)} usable photos")
    return finish_marked("anefo", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- Kremlin (en.kremlin.ru)

KREMLIN = "http://en.kremlin.ru"
KREMLIN_PAGES = 2400                 # pages of the photo index (about 20 galleries each, 2000 onwards)
# Places in Russia that galleries name without the country.
RUSSIAN_PLACES = re.compile(r"\b(Kremlin|Moscow|Novo-Ogaryovo|St Petersburg|Saint Petersburg|Sochi|Kazan|Bocharov "
                            r"Ruchei|Valdai|Vladivostok|Novosibirsk|Yekaterinburg|Kaliningrad|Nizhny Novgorod|"
                            r"Sevastopol|Crimea|Region|Territory|Republic of [A-Z]\w+)\b")


def kremlin_place(text):
    """A gallery's place as a row's place: "The Kremlin, Moscow" -> "The Kremlin, Moscow, Russia"; a place whose
    last part is a country keeps that country; "" otherwise (a city abroad named alone is not guessed)."""
    text = clean(text).strip(" .")
    if not text:
        return ""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    country = country_named(parts[-1])
    if country:
        return place_name(*parts[:-1][-2:], country)
    if RUSSIAN_PLACES.search(text) and not re.search(r"\bCrimea|Sevastopol", text):
        return place_name(*parts[-2:], "Russia")
    return ""


def kremlin_gallery(s, path):
    """[(name, picture address, rows)] of one photo gallery: each photo's caption (data-text) and place."""
    try:
        page = s.get(KREMLIN + path, timeout=60).text
    except Exception:  # noqa: BLE001 - left out
        return []
    title = clean((re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S) or [None, ""])[1])
    out = []
    for big, text, where_text in re.findall(r'<a class="photo photoset_a" href="([^"]+)"[^>]*>\s*<img[^>]*?'
                                            r'data-text="([^"]*)"\s*data-place="([^"]*)"', page, re.S):
        answer = tidy(text)
        if not usable(answer) or not_shown(answer):
            continue
        credit = (f"{title[:120]}: {answer[:150]} Presidential Executive Office of Russia, kremlin.ru, CC BY 4.0 "
                  f"(http://creativecommons.org/licenses/by/4.0/), {KREMLIN}{path}")
        name = "kremlin-" + re.sub(r"\W", "", big.rsplit("/", 1)[-1].split(".")[0])[:40] + ".jpg"
        out.append((name, big, picture_rows(answer, credit, kremlin_place(where_text))))   # its picture server: http
    return out


def build_kremlin(limit):
    """The Kremlin pack: galleries from random pages of the photo index, at most a few photos from each gallery."""
    s, rng, items, answers = session(), pass_random(307), [], set()
    s.headers["User-Agent"] = "Mozilla/5.0 (compatible; " + build_packs.USER_AGENT + ")"
    pages = list(range(1, KREMLIN_PAGES + 1))
    rng.shuffle(pages)
    for number in pages[:300]:
        if len(items) >= limit * 1.3:
            break
        time.sleep(1)
        try:
            index = s.get(f"{KREMLIN}/multimedia/photo/page/{number}", timeout=60).text
        except Exception:  # noqa: BLE001 - next page
            continue
        galleries = sorted(set(re.findall(r'href="(/events/[a-z]+/[a-z]+/\d+/photos)"', index)))
        rng.shuffle(galleries)
        for path in galleries[:3]:
            time.sleep(1)
            photos = [p for p in kremlin_gallery(s, path) if p[2][0]["answer"] not in answers]
            rng.shuffle(photos)
            for photo in photos[:3]:
                answers.add(photo[2][0]["answer"])
                items.append(photo)
    say(f"Kremlin: {len(items)} usable photos")
    return finish_marked("kremlin", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- Australian War Memorial

AWM = "https://www.awm.gov.au"


def awm_record(s, path):
    """(name, picture address, rows) of one AWM photograph whose page says "Copyright expired - public domain",
    or None."""
    try:
        page = s.get(AWM + path, timeout=60).text
    except Exception:  # noqa: BLE001 - left out
        return None
    if "public domain" not in page.lower():
        return None
    meta = dict(re.findall(r'<meta (?:property|name)="([^"]+)" content="([^"]*)"', page))
    picture = meta.get("og:image") or ""
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", re.sub(r"<script.*?</script>", "", page, flags=re.S)))
    copyright_ok = re.search(r"Copyright expired - public domain|This item is in the Public Domain", text)
    m = re.search(r"\|\s*Description\s*\|[|\s]*([^|]{20,})", text)
    place_m = re.search(r'<a href="/collection/PL\d+">([^<]+)</a>', page)     # "Europe: France, Somme, Pozieres"
    if not copyright_ok or not m or not picture.startswith("http"):
        return None
    words = clean(place_m.group(1)) if place_m else ""
    caption = clean(m.group(1))
    caption = re.sub(r"^([A-Z ,.'-]+\.\s*)?\d{4}-\d{2}-\d{2}\.\s*", lambda mm: mm.group(1) or "", caption)
    caption = re.sub(r"\bNo\.? ?(\d)", r"Number \1", caption)      # "No 7 Squadron" (tidy drops "No 7" as a code)
    answer = tidy(capped_words(sentence_case(caption, re.split(r"[:,]", words)), 80))
    if not usable(answer) or not_shown(answer):
        return None
    parts = [p.strip() for p in re.split(r"[:,]", words) if p.strip()]
    at = next((i for i, p in enumerate(parts) if country_named(p)), -1)        # the first part that is a country
    place = place_name(*list(reversed(parts[at + 1:]))[:2], country_named(parts[at])) if at >= 0 else ""
    credit = (f"{caption[:150]}, Australian War Memorial, {path.rsplit('/', 1)[-1]}, copyright expired - public "
              f"domain, {AWM}{path}")
    return (f"awm-{path.rsplit('/', 1)[-1]}.jpg", picture, picture_rows(answer, credit, place))


def build_awm(limit):
    """The AWM pack: photographs from random pages of the Memorial's collection search (photographs only), each
    record's page read for its copyright, caption, place and picture."""
    s, rng, items = session(), pass_random(308), []
    s.headers["User-Agent"] = "Mozilla/5.0 (compatible; " + build_packs.USER_AGENT + ")"
    pages = list(range(1, 2000))
    rng.shuffle(pages)
    for number in pages[:120]:
        if len(items) >= limit * 1.3:
            break
        time.sleep(1)
        try:
            listing = s.get(AWM + "/advanced-search", params={"query": "", "collection": "true",
                                                             "facet_type": "Photograph", "page": number},
                            timeout=60).text
        except Exception:  # noqa: BLE001 - next page
            continue
        paths = sorted(set(re.findall(r'href="(/collection/[A-Z]\d+)"', listing)))
        rng.shuffle(paths)
        for path in paths[:max(3, limit // 10)]:
            time.sleep(0.5)
            item = awm_record(s, path)
            if item:
                items.append(item)
    say(f"Australian War Memorial: {len(items)} usable photos")
    return finish_marked("awm", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- the packs

ARCHIVE_PACKS = {
    "nara": (build_nara, "U.S. National Archives and Records Administration, https://catalog.archives.gov : "
                         "DOCUMERICA (412-DA), War Relocation Authority photographs (210-G) and Ansel Adams "
                         "photographs of national parks (79-AA). US government work, public domain; only records "
                         "marked 'Unrestricted' for use. Captions from the Archives' records."),
    "nypl": (build_nypl, "The New York Public Library, public-domain items: metadata CC0 "
                         "(https://github.com/NYPL-publicdomain/data-and-utilities), items with 'no known US copyright "
                         "restrictions' (https://www.nypl.org/research/resources/public-domain-collections). Titles "
                         "and descriptions from the Library's records."),
    "getty_museum": (build_getty_museum, "The J. Paul Getty Museum, Los Angeles, Open Content Program "
                                         "(https://www.getty.edu/projects/open-content-program/): objects with 'No "
                                         "Copyright'; metadata and descriptions CC0 (https://data.getty.edu)."),
    "digital_commonwealth": (build_digital_commonwealth, "Digital Commonwealth, Massachusetts "
                                                         "(https://www.digitalcommonwealth.org): photographs marked "
                                                         "'No known copyright restrictions', each with its holding "
                                                         "library or museum below."),
    "smk": (build_smk, "Statens Museum for Kunst (National Gallery of Denmark), https://open.smk.dk : public-domain "
                       "works (CC0 / Public Domain Mark), titles from SMK's records (Danish, or English where SMK "
                       "wrote it)."),
    "anefo": (build_anefo, "Nationaal Archief, The Hague (mostly the Anefo collection), CC0 or public domain for scan "
                           "and metadata (https://www.nationaalarchief.nl/onderzoeken/open-data/fotos); the copy on "
                           "Wikimedia Commons, Category:Images from Nationaal Archief. Photographers named below."),
    "kremlin": (build_kremlin, "Presidential Executive Office of Russia, http://en.kremlin.ru : 'All content on this "
                               "site is licensed under Creative Commons Attribution 4.0 International' "
                               "(http://creativecommons.org/licenses/by/4.0/). Captions from the site."),
    "awm": (build_awm, "Australian War Memorial, https://www.awm.gov.au/collection : photographs whose record says "
                       "'Copyright expired - public domain' (https://www.awm.gov.au/copyright). Captions from the "
                       "Memorial's records."),
}

# How many pictures a full build takes from each collection.
ARCHIVE_LIMITS = {
    "nara": 5000,                     # DOCUMERICA ~15,900 (search reaches 10,000), WRA ~4,000, Ansel Adams ~220
    "nypl": 6000,                     # of about 180,000 public-domain still images; titles of 6 words or more
    "getty_museum": 4000,             # of about 62,000 described objects; those with "No Copyright"
    "digital_commonwealth": 3000,     # of about 115,000 unrestricted photographs; many titles are too short
    "smk": 3000,                      # of about 39,500 public-domain works; those with a descriptive title
    "anefo": 6000,                    # of about 430,000 files; Dutch captions of 6 words or more
    "kremlin": 3000,                  # of tens of thousands of photos since 2000
    "awm": 3000,                      # of hundreds of thousands of photographs; those in the public domain
}

# Packs in another language: (language, Helsinki-NLP model, revision), as world_portal_packs.PORTAL_TRANSLATE, for
# build_packs to add to its TRANSLATE and MT_MODELS (Danish uses the North Germanic model already used for Swedish
# and Norwegian; Dutch the model already used for the Rijksmuseum).
ARCHIVE_TRANSLATE = {
    "smk": ("da", "Helsinki-NLP/opus-mt-tc-big-gmq-en", "b243b46fc9e1eaf068ae0d8ae896ac1acd7d2380"),
    "anefo": ("nl", "Helsinki-NLP/opus-mt-tc-bible-big-gmw-en", "5af4b912a33023bc682ee6f27456dab65dbeaa73"),
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one archive pack builder.")
    parser.add_argument("key", choices=sorted(ARCHIVE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--rows", type=int, default=0, help="print only this many rows (0: all)")
    args = parser.parse_args(argv)
    entries = ARCHIVE_PACKS[args.key][0](args.limit)
    for name, data, row in entries[:args.rows or None]:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child, "
        f"{sum(1 for _, _, r in entries if r.get('content') == 'graphic')} rows marked graphic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
