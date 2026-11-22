"""World geography and countries for the reference library, in its own group "Reference, world geography" (the owner's
request of 2026-11-22). Keys: geography (every book), geo:<name>.

What this module builds, in plain words:
  - geo:factbook, the CIA World Factbook IN FULL: every country's, territory's and ocean's page (introduction,
    geography, people and society, environment, government, economy, energy, communications, transport, military and
    security (kept, as the Factbook printed it), space, terrorism and transnational issues), with a short "map in
    words" at the top of each page made only from the Factbook's own words (where the country is, its coordinates,
    the map it is on, its area compared with a US state, its borders and neighbours, coastline, terrain, highest and
    lowest points, and the capital). The book opens with an index by continent (the Factbook's own regions under
    their continent), one page per continent, so a reader can go Africa, Asia, Europe ... and then to a country.
    The CIA retired the Factbook on 4 February 2026 and its pages on cia.gov now forward to a farewell story; its
    downloadable archives (factbook-2025.zip and earlier) forward there too, and the Wayback Machine cannot be
    reached by the builder. So the Factbook is read from factbook.json (github.com/factbook/factbook.json), a
    faithful JSON copy of every Factbook page taken from cia.gov until the end, pinned to one commit so every build
    reads the same edition. The Factbook is a work of the US government (public domain; the CIA said so on its
    site), and the factbook.json project dedicates its files to the public domain (CC0 1.0); both lines are checked
    at every build. Photos and flag pictures are not used (none are in the JSON); maps are described in words.
  - geo:index, a guide to geography in the library: the Factbook by continent, maps and land navigation, travel and
    phrasebooks, holidays around the world, and the sources that are links only.

Not built (NOT_INCLUDED, link-only): the State Department's country Background Notes and its "U.S. Relations With"
fact sheets (state.gov and its 2009-2017 archive refuse programs), the 7 GB Kiwix copies of the Factbook with photos
(too large; the text is built here), the USGS GNIS and NGA GNS place-name gazetteers (lookup databases of millions of
names, not books; the picture packs already turn coordinates into countries with Natural Earth), and the Census
Bureau's gazetteer files.

Run from the repository's folder:
  python3 textbooks/geography.py geo:factbook --out build/textbooks --limit 5
  python3 textbooks/geography.py --list geography
"""

import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker shared by the reference modules

GROUP = "geography"
GROUPS = {GROUP: "Reference, world geography"}

# The factbook.json commit read (the last state of the copy; every build reads this same edition).
FB_COMMIT = "144d6977b2b01ac1cbd220de754c0a005616760b"
FB_DATE = "2026-09-11"
FB_RAW = f"https://raw.githubusercontent.com/factbook/factbook.json/{FB_COMMIT}"
FB_REPO = "https://github.com/factbook/factbook.json"
# The two licence lines checked at every build: the project's read-me (the Factbook is public domain) and its
# licence file (CC0 for the project's own files).
FB_README_TEXT = r"in the public domain"
FB_LICENSE_TEXT = r"CC0 1\.0 Universal"
FAREWELL = "https://www.cia.gov/stories/story/spotlighting-the-world-factbook-as-we-bid-a-fond-farewell/"
FB_NOTICE = ("The World Factbook, by the Central Intelligence Agency (CIA): a work of the US government, in the public "
             "domain. The CIA retired the Factbook on 4 February 2026; this is its last edition as copied from cia.gov "
             "by the factbook.json project (github.com/factbook/factbook.json, CC0 1.0). Facts are as the CIA last "
             "published them and some will be out of date. The \"map in words\" at the top of each page is made "
             "only from the Factbook's own entries; no pictures are included. Use of this copy does not imply the "
             "CIA's endorsement.")

# The Factbook's regions (the folders of factbook.json), each with its continent for the index, in index order.
REGIONS = [
    ("africa", "Africa", "Africa"),
    ("antarctica", "Antarctica", "Antarctica"),
    ("central-asia", "Central Asia", "Asia"),
    ("east-n-southeast-asia", "East and Southeast Asia", "Asia"),
    ("middle-east", "Middle East", "Asia"),
    ("south-asia", "South Asia", "Asia"),
    ("australia-oceania", "Australia and Oceania", "Australia and Oceania"),
    ("europe", "Europe", "Europe"),
    ("north-america", "North America", "North America"),
    ("central-america-n-caribbean", "Central America and the Caribbean", "North America"),
    ("south-america", "South America", "South America"),
    ("oceans", "Oceans", "Oceans and the world"),
    ("world", "The world", "Oceans and the world"),
]
CONTINENTS = list(dict.fromkeys(c for _f, _r, c in REGIONS))

# Every page of factbook.json at FB_COMMIT: {region folder: {GEC code: name}} (the codes are the Factbook's own
# two-letter GEC codes, not ISO codes; the names are those of the project's summary list).
REGION_CODES = {
    "africa": {"ag": "Algeria", "ao": "Angola", "bn": "Benin", "bc": "Botswana", "uv": "Burkina Faso",
        "by": "Burundi", "cm": "Cameroon", "cv": "Cape Verde", "ct": "Central African Republic", "cd": "Chad",
        "cn": "Comoros", "cf": "Congo", "cg": "Congo DR", "iv": "Cote d'Ivoire", "dj": "Djibouti", "eg": "Egypt",
        "ek": "Equatorial Guinea", "er": "Eritrea", "et": "Ethiopia", "gb": "Gabon", "gh": "Ghana", "gv": "Guinea",
        "pu": "Guinea-Bissau", "ke": "Kenya", "lt": "Lesotho", "li": "Liberia", "ly": "Libya", "ma": "Madagascar",
        "mi": "Malawi", "ml": "Mali", "mr": "Mauritania", "mp": "Mauritius", "mo": "Morocco", "mz": "Mozambique",
        "wa": "Namibia", "ng": "Niger", "ni": "Nigeria", "rw": "Rwanda", "sh": "Saint Helena",
        "tp": "Sao Tome and Principe", "sg": "Senegal", "se": "Seychelles", "sl": "Sierra Leone", "so": "Somalia",
        "sf": "South Africa", "od": "South Sudan", "su": "Sudan", "wz": "Swaziland", "tz": "Tanzania",
        "ga": "The Gambia", "to": "Togo", "ts": "Tunisia", "ug": "Uganda", "wi": "Western Sahara", "za": "Zambia",
        "zi": "Zimbabwe"},
    "antarctica": {"ay": "Antarctica", "bv": "Bouvet Island", "fs": "French Southern and Antarctic Lands",
        "hm": "Heard Island and McDonald Islands"},
    "australia-oceania": {"aq": "American Samoa", "at": "Ashmore and Cartier Islands", "as": "Australia",
        "kt": "Christmas Island", "ck": "Cocos (Keeling) Islands", "cw": "Cook Islands", "cr": "Coral Sea Islands",
        "fj": "Fiji", "fp": "French Polynesia", "gq": "Guam", "kr": "Kiribati", "rm": "Marshall Islands",
        "fm": "Micronesia", "nr": "Nauru", "nc": "New Caledonia", "nz": "New Zealand", "ne": "Niue",
        "nf": "Norfolk Island", "cq": "Northern Mariana Islands", "ps": "Palau", "pc": "Pitcairn Islands",
        "ws": "Samoa", "bp": "Solomon Islands", "tl": "Tokelau", "tn": "Tonga", "tv": "Tuvalu",
        "um": "US Pacific Island Wildlife Refuges", "nh": "Vanuatu", "wq": "Wake Island", "wf": "Wallis and Futuna"},
    "central-america-n-caribbean": {"av": "Anguilla", "ac": "Antigua and Barbuda", "aa": "Aruba", "bb": "Barbados",
        "bh": "Belize", "vi": "British Virgin Islands", "cj": "Cayman Islands", "cs": "Costa Rica", "cu": "Cuba",
        "uc": "Curacao", "do": "Dominica", "dr": "Dominican Republic", "es": "El Salvador", "gj": "Grenada",
        "gt": "Guatemala", "ha": "Haiti", "ho": "Honduras", "jm": "Jamaica", "mh": "Montserrat",
        "bq": "Navassa Island", "nu": "Nicaragua", "pm": "Panama", "rq": "Puerto Rico", "tb": "Saint Barthelemy",
        "sc": "Saint Kitts and Nevis", "st": "Saint Lucia", "rn": "Saint Martin",
        "vc": "Saint Vincent and the Grenadines", "nn": "Sint Maarten", "bf": "The Bahamas",
        "td": "Trinidad and Tobago", "tk": "Turks and Caicos Islands", "vq": "US Virgin Islands"},
    "central-asia": {"am": "Armenia", "aj": "Azerbaijan", "gg": "Georgia", "kz": "Kazakhstan", "kg": "Kyrgyzstan",
        "rs": "Russia", "ti": "Tajikistan", "tx": "Turkmenistan", "uz": "Uzbekistan"},
    "east-n-southeast-asia": {"bx": "Brunei", "bm": "Burma", "cb": "Cambodia", "ch": "China", "hk": "Hong Kong",
        "id": "Indonesia", "ja": "Japan", "la": "Laos", "mc": "Macau", "my": "Malaysia", "mg": "Mongolia",
        "kn": "North Korea", "pp": "Papua New Guinea", "pf": "Paracel Islands", "rp": "Philippines",
        "sn": "Singapore", "ks": "South Korea", "pg": "Spratly Islands", "tw": "Taiwan", "th": "Thailand",
        "tt": "Timor-Leste", "vm": "Vietnam"},
    "europe": {"ax": "Akrotiri (Sovereign Base)", "al": "Albania", "an": "Andorra", "au": "Austria", "bo": "Belarus",
        "be": "Belgium", "bk": "Bosnia and Herzegovina", "bu": "Bulgaria", "hr": "Croatia", "cy": "Cyprus",
        "ez": "Czech Republic", "da": "Denmark", "dx": "Dhekelia (Sovereign Base)", "en": "Estonia",
        "ee": "European Union", "fo": "Faroe Islands", "fi": "Finland", "fr": "France", "gm": "Germany",
        "gi": "Gibraltar", "gr": "Greece", "gk": "Guernsey", "hu": "Hungary", "ic": "Iceland", "ei": "Ireland",
        "im": "Isle of Man", "it": "Italy", "jn": "Jan Mayen", "je": "Jersey", "kv": "Kosovo", "lg": "Latvia",
        "ls": "Liechtenstein", "lh": "Lithuania", "lu": "Luxembourg", "mk": "Macedonia", "mt": "Malta",
        "md": "Moldova", "mn": "Monaco", "mj": "Montenegro", "nl": "Netherlands", "no": "Norway", "pl": "Poland",
        "po": "Portugal", "ro": "Romania", "sm": "San Marino", "ri": "Serbia", "lo": "Slovakia", "si": "Slovenia",
        "sp": "Spain", "sv": "Svalbard", "sw": "Sweden", "sz": "Switzerland", "up": "Ukraine", "uk": "United Kingdom",
        "vt": "Vatican City (Holy See)"},
    "middle-east": {"ba": "Bahrain", "gz": "Gaza Strip", "ir": "Iran", "iz": "Iraq", "is": "Israel", "jo": "Jordan",
        "ku": "Kuwait", "le": "Lebanon", "mu": "Oman", "qa": "Qatar", "sa": "Saudi Arabia", "sy": "Syria",
        "tu": "Turkey", "ae": "United Arab Emirates", "we": "West Bank", "ym": "Yemen"},
    "north-america": {"bd": "Bermuda", "ca": "Canada", "ip": "Clipperton Island", "gl": "Greenland", "mx": "Mexico",
        "sb": "Saint Pierre and Miquelon", "us": "United States"},
    "oceans": {"xq": "Arctic Ocean", "zh": "Atlantic Ocean", "xo": "Indian Ocean", "zn": "Pacific Ocean",
        "oo": "Southern Ocean"},
    "south-america": {"ar": "Argentina", "bl": "Bolivia", "br": "Brazil", "ci": "Chile", "co": "Colombia",
        "ec": "Ecuador", "fk": "Falkland Islands", "gy": "Guyana", "pa": "Paraguay", "pe": "Peru",
        "sx": "South Georgia and the South Sandwich Islands", "ns": "Suriname", "uy": "Uruguay", "ve": "Venezuela"},
    "south-asia": {"af": "Afghanistan", "bg": "Bangladesh", "bt": "Bhutan", "io": "British Indian Ocean Territory",
        "in": "India", "mv": "Maldives", "np": "Nepal", "pk": "Pakistan", "ce": "Sri Lanka"},
    "world": {"xx": "World"},
}

# The Factbook entries that make the "map in words": (section, field, label).
MAP_FIELDS = [("Geography", "Location", "Where it is"), ("Geography", "Geographic coordinates", "Coordinates"),
              ("Geography", "Map references", "On the map of"), ("Geography", "Area", "Area"),
              ("Geography", "Area - comparative", "Size compared"), ("Geography", "Land boundaries", "Borders"),
              ("Geography", "Coastline", "Coastline"), ("Geography", "Terrain", "Terrain"),
              ("Geography", "Elevation", "Highest and lowest points"), ("Government", "Capital", "Capital")]
# Tags kept from the Factbook's own text (all others are taken out, their words kept).
KEEP_TAGS = r"(?:strong|em|b|i|br|p|ul|ol|li)"


def clean(text):
    """The Factbook's text as safe HTML: only simple tags kept (bold, italics, line breaks, paragraphs, lists); its
    entities (such as &eacute;) are kept as they are."""
    text = re.sub(rf"<(?!/?{KEEP_TAGS}\b)[^>]*>", "", str(text or ""))
    return re.sub(r"<(/?)(\w+)[^>]*?(/?)>", lambda m: f"<{m.group(1)}{m.group(2).lower()}{m.group(3)}>", text)


def plain(text):
    """The Factbook's text as plain words (tags taken out, entities read)."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", str(text or ""))).split())


def field_html(value, level):
    """One Factbook entry as HTML: {"text": ...} becomes a paragraph; an entry with parts (such as "total" and
    "land") becomes a heading per part one level down; a "note" is a paragraph of its own."""
    if isinstance(value, str):
        return f"<p>{clean(value)}</p>"
    if not isinstance(value, dict):
        return ""
    out = []
    if "text" in value:
        out.append(f"<p>{clean(value['text'])}</p>")
    for key, part in value.items():
        if key == "text":
            continue
        if key == "note":
            out.append(f"<p>{clean(part)}</p>")
        elif isinstance(part, dict) and set(part) == {"text"}:
            out.append(f"<p><strong>{html.escape(key.strip())}:</strong> {clean(part['text'])}</p>")
        else:
            out.append(f"<h{min(level, 6)}>{html.escape(key.strip())}</h{min(level, 6)}>{field_html(part, level + 1)}")
    return "".join(out)


def map_in_words(data):
    """The short "map in words" of a page: the Factbook's own entries on where the place is, as a list."""
    items = []
    for section, name, label in MAP_FIELDS:
        value = (data.get(section) or {}).get(name)
        if not value:
            continue
        if isinstance(value, dict) and "text" not in value:
            parts = [f"{k.strip()}: {plain(v.get('text') if isinstance(v, dict) else v)}" for k, v in value.items()
                     if k != "note" and (not isinstance(v, dict) or "text" in v)]
            words = "; ".join(p for p in parts if p.split(": ", 1)[1])
        else:
            words = plain(value.get("text") if isinstance(value, dict) else value)
        if words:
            items.append(f"<li><strong>{html.escape(label)}:</strong> {html.escape(words)}</li>")
    if not items:
        return ""
    return ("<h2>The map in words</h2><p>Made only from the Factbook's own entries below.</p><ul>" + "".join(items) +
            "</ul>")


def country_name(data, code, region):
    """The page's name: the Factbook's conventional short form where it has one, else the summary list's name."""
    short = (((data.get("Government") or {}).get("Country name") or {}).get("conventional short form") or {})
    words = plain(short.get("text") if isinstance(short, dict) else "")
    return words if words and words.lower() != "none" else REGION_CODES[region][code]


def country_body(data):
    """The whole page of one country: the map in words, then every section of the Factbook with every entry."""
    out = [map_in_words(data)]
    for section, fields in data.items():
        if not isinstance(fields, dict) or not fields:
            continue
        out.append(f"<h2>{html.escape(section)}</h2>")
        for name, value in fields.items():
            out.append(f"<h3>{html.escape(name.strip())}</h3>{field_html(value, 4)}")
    return "".join(out)


def page_path(region, code, name):
    """The address of a country's page in the book ("europe-fr-france")."""
    import build_textbooks as B
    return f"{region}-{code}-{B.slug(name, 40)}"


def index_pages(names):
    """The index by continent: one page per continent listing its Factbook regions and their places, each linked
    to its page. names: {(region, code): page name}."""
    import build_textbooks as B
    pages = []
    for continent in CONTINENTS:
        body = [f"<p>The places of the World Factbook in {html.escape(continent)}, by the Factbook's own regions. "
                f"Choose a name to open its page.</p>"]
        for folder, region, cont in REGIONS:
            if cont != continent:
                continue
            links = sorted(((n, page_path(folder, code, n)) for (f, code), n in names.items() if f == folder),
                           key=lambda x: x[0].lower())
            if links:
                body.append(f"<h2>{html.escape(region)}</h2><ul>" +
                            "".join(f'<li><a href="{p}">{html.escape(n)}</a></li>' for n, p in links) + "</ul>")
        if len(body) == 1:                   # no place of this continent was read (a small test build)
            continue
        pages.append(B.Page(f"index-{B.slug(continent, 40)}", f"Index: {continent}", "".join(body), 0,
                            "Index by continent"))
    return pages


def factbook_licence_ok(get, left_out):
    """True when the project's read-me still says the Factbook is public domain and its licence file is still CC0;
    otherwise the reason goes in left_out."""
    try:
        readme, licence = get(f"{FB_RAW}/README.md"), get(f"{FB_RAW}/LICENSE.md")
    except Exception as e:  # noqa: BLE001 - said in left_out
        left_out.append({"title": "The World Factbook", "reason": f"Its licence could not be checked ({e})."})
        return False
    if not re.search(FB_README_TEXT, readme) or not re.search(FB_LICENSE_TEXT, licence):
        left_out.append({"title": "The World Factbook", "reason": "factbook.json no longer says the Factbook is in "
                         "the public domain, or its licence file is no longer CC0: not built."})
        return False
    return True


def factbook_book(name, work, cache=None, left_out=None, limit=None, fetch=None):
    """The World Factbook book: the index by continent, then every place's page, region by region. fetch: a
    function(url) -> text (the builder's fetch by default; the self-test passes a made-up one)."""
    import json
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    get = fetch or (lambda url: B.fetch(url, cache) if K.readable(url, cache) else "")
    if not factbook_licence_ok(get, left_out):
        return None
    book = K.new_book("geo_factbook", "The World Factbook: every country, territory and ocean (CIA, last edition)",
                      "Countries of the world", GROUP, "Central Intelligence Agency (CIA)", K.US_GOV, K.US_GOV_URL,
                      FB_REPO, "The CIA World Factbook in full, one page per country, territory and ocean, with an "
                      "index by continent: introduction and background, geography (with the map in words), people "
                      "and society, environment, government, economy, energy, communications, transport, military "
                      "and security, space, terrorism and transnational issues.", FB_NOTICE, country="International",
                      changes="the Factbook's JSON pages made into web pages; a short \"map in words\" made from its "
                              "own entries; an index by continent added")
    names, pages = {}, []
    for number, (folder, region, _continent) in enumerate(REGIONS, 1):
        for code in REGION_CODES[folder]:
            if limit and len(pages) >= limit:
                break
            url = f"{FB_RAW}/{folder}/{code}.json"
            try:
                data = json.loads(get(url) or "{}")
            except (ValueError, OSError) as e:
                left_out.append({"title": REGION_CODES[folder][code], "reason": f"Its page could not be read ({e})."})
                continue
            if not data:
                left_out.append({"title": REGION_CODES[folder][code], "reason": "Its page could not be read."})
                continue
            title = country_name(data, code, folder)
            names[(folder, code)] = title
            pages.append(B.Page(page_path(folder, code, title), title, country_body(data), number, region))
            book.originals.append({"url": url, "kind": "json"})
    book.pages = index_pages(names) + pages if pages else []
    book.published = "2026-02"
    book.version = f"factbook.json commit {FB_COMMIT[:7]} ({FB_DATE}), the Factbook's last edition"
    return book


def factbook_sign(name):
    """The weekly sign of the Factbook book: the pinned commit and the page list (the Factbook no longer changes)."""
    return K.sha(FB_COMMIT, REGION_CODES)


# ====================================================================== the index

SECTIONS = [
    ("Countries by continent", "The World Factbook has a page for every country, territory and ocean, with an index "
     "by continent at its start: Africa, Antarctica, Asia (Central Asia, East and Southeast Asia, the Middle East and "
     "South Asia), Australia and Oceania, Europe, North America (with Central America and the Caribbean), South "
     "America, and the oceans and the world.", [
         ("key", "geo:factbook", "The World Factbook (CIA, last edition): every country's page, with the map in "
                                 "words, and the index by continent")]),
    ("Maps and finding your way", "Reading maps, coordinates and compass directions.", [
        ("key", "pdf:army_fm_3_25_26_map_reading", "Map Reading and Land Navigation (FM 3-25.26): grid references, "
                                                   "latitude and longitude, contour lines"),
        ("key", "science:usgs_earthquakes_for_everyone", "Earthquakes for everyone (USGS)"),
        ("key", "science:noaa_ocean_facts", "Ocean facts (NOAA)")]),
    ("Travel and languages", "Visiting other countries: travel rules, phrasebooks and language courses.", [
        ("word", "travel", "Travel books: USA.gov travel pages, FAA PackSafe, national park passes"),
        ("key", "lang:wikivoyage_phrasebooks", "Wikivoyage phrasebooks"),
        ("word", "languages", "Language courses (FSI, Peace Corps) and example sentences"),
        ("word", "holidays", "Holidays and observances, with other countries' public holidays")]),
    ("Links only", "Sources the builder cannot read, or that are not books.", [
        ("link", "State Department country pages (U.S. Relations With ... fact sheets)",
         "https://www.state.gov/countries-and-areas-list/", "state.gov refuses programs; open it in a browser"),
        ("link", "State Department Background Notes (archived, to about 2012)",
         "https://2009-2017.state.gov/r/pa/ei/bgn/index.htm", "the archive refuses programs; open it in a browser"),
        ("link", "USGS Geographic Names Information System (GNIS): US place names",
         "https://www.usgs.gov/tools/geographic-names-information-system-gnis",
         "a lookup database of about a million names, not a book"),
        ("link", "NGA GEOnet Names Server (GNS): foreign place names", "https://geonames.nga.mil/geon-ags/",
         "a lookup database of millions of names, not a book"),
        ("link", "Census Bureau gazetteer files (counties and places, with area and coordinates)",
         "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html",
         "data tables for a spreadsheet, not a book")]),
]
INDEX = X.index_maker("geo", GROUP, "World geography: a guide to the library", "World geography",
                      "A guide to world geography in the library: the World Factbook by continent, maps and finding "
                      "your way, travel and languages, and the sources that are links only.", SECTIONS,
                      country="International")
MAKERS = {"factbook": (factbook_book, factbook_sign), "index": INDEX}

COLLECTION = K.Collection("geo", GROUP, makers=MAKERS, words={"geography": lambda: ["geo:index", "geo:factbook"]})

LICENCE_LINES = {
    "geo_factbook": "The World Factbook: a work of the US government (17 U.S.C. 105); the CIA's site said it was in "
                    "the public domain until the Factbook was retired on 4 February 2026 (cia.gov now forwards every "
                    "Factbook address, the archives included, to its farewell story, checked 2026-11-22). Read from "
                    "factbook.json at commit 144d697, whose read-me (\"in the public domain\") and CC0 1.0 licence "
                    "file are checked at every build; raw.githubusercontent.com has no robots.txt rules.",
    "geo_index": "The index (geo:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("State Department Background Notes and \"U.S. Relations With\" country fact sheets", "Public domain, but "
     "www.state.gov answers programs \"403\" and its 2009-2017 archive (where the last Background Notes are) answers "
     "\"forbidden\" (checked 2026-11-22); the GPO's printed Background Notes on the Internet Archive are from "
     "1989-1990 and too old. The World Factbook covers the same facts. Link-only. Index: "
     "https://2009-2017.state.gov/r/pa/ei/bgn/index.htm"),
    ("The World Factbook as Kiwix ZIM files with photos (Internet Archive theworldfactbook_en_all_2024-05, 7 GB)",
     "The same text with the CIA's photos, too large for this library; the text is built from the last edition "
     "(geo:factbook). Index: https://archive.org/details/theworldfactbook_en_all_2024-05"),
    ("The CIA's own downloadable Factbook archives (factbook-2025.zip and earlier)", "Their addresses on cia.gov now "
     "forward to the farewell story, and the Wayback Machine cannot be reached by the builder (checked 2026-11-22). "
     "Index: " + FAREWELL),
    ("USGS GNIS and NGA GNS place-name gazetteers", "Public domain, but they are lookup databases of millions of names "
     "(features, populated places, coordinates), not books; the picture packs already turn coordinates into countries "
     "with Natural Earth (packs/places.py). Link-only. Index: "
     "https://www.usgs.gov/tools/geographic-names-information-system-gnis and https://geonames.nga.mil/geon-ags/"),
    ("Census Bureau gazetteer files", "Public domain data tables (counties, places, ZIP code areas with land area "
     "and coordinates), better opened in a spreadsheet than read as a book. Index: "
     "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
