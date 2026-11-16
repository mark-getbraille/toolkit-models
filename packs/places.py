"""Where in the world a pack's pictures are from: the optional "place" of a pack row, used by every pack file.

A row may carry:
  "place"       a short plain place name, most specific first, ending with the country in English: "Shoreditch,
                London, UK", "Kyoto, Japan", "Kenya" (or a region where the source gives no country: "West Asia").
  "place_kind"  "photo" (where the photo was taken; the same as leaving it out), "origin" (where an object was made:
                museum objects) or "depicted" (the place a picture shows: a painting of a town, a map).

A place is only ever taken from the source's own records (its metadata, coordinates or the place its authors say all
their photos were taken), never guessed from the picture. Coordinates are turned into a country here, on the building
machine, with Natural Earth's country borders (public domain, naturalearthdata.com; the 1:50 million file, about
3 MB, downloaded once per build from the project's GitHub release tag). Nothing else is looked up anywhere.

    python packs/places.py 51.52 -0.08        (prints the country at a latitude and longitude: a quick check)
"""

import json
import re
import sys

NE_COUNTRIES = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/"
                "ne_50m_admin_0_countries.geojson")
# Short everyday English names where Natural Earth's own (its ADMIN field) is long or formal, by ISO code.
SHORT_NAMES = {"US": "USA", "GB": "UK", "HK": "Hong Kong", "MO": "Macao", "RS": "Serbia", "TZ": "Tanzania",
               "BS": "Bahamas", "SZ": "Eswatini", "AX": "Åland", "CZ": "Czechia", "TL": "East Timor",
               "VA": "Vatican City", "FM": "Micronesia", "KR": "South Korea", "KP": "North Korea"}
# Other spellings sources use for a country, in lower case, and the name a row uses.
OTHER_NAMES = {"united states": "USA", "united states of america": "USA", "u.s.a.": "USA", "us": "USA",
               "america": "USA", "united kingdom": "UK", "great britain": "UK", "britain": "UK",
               "united kingdom of great britain and northern ireland": "UK", "the netherlands": "Netherlands",
               "holland": "Netherlands", "korea": "South Korea", "republic of korea": "South Korea",
               "korea, republic of": "South Korea", "russian federation": "Russia", "viet nam": "Vietnam",
               "people's republic of china": "China", "prc": "China", "lao": "Laos", "lao pdr": "Laos",
               "czech republic": "Czechia", "turkiye": "Turkey", "türkiye": "Turkey", "ivory coast": "Ivory Coast",
               "côte d'ivoire": "Ivory Coast", "cote d'ivoire": "Ivory Coast", "the gambia": "Gambia",
               "the bahamas": "Bahamas", "republic of serbia": "Serbia", "united republic of tanzania": "Tanzania",
               "taiwan, province of china": "Taiwan", "hong kong sar": "Hong Kong", "hong kong s.a.r.": "Hong Kong",
               "iran, islamic republic of": "Iran", "england": "England", "scotland": "Scotland", "wales": "Wales",
               "northern ireland": "Northern Ireland"}
_COUNTRIES = None          # [(name, ISO code, (west, south, east, north), [rings])], read once
_NAMES = None              # {name in another language or spelling, lower case: English name}


def _polygons(geometry):
    """The outer rings of a GeoJSON Polygon or MultiPolygon, each a list of (longitude, latitude), with the holes
    (lakes, enclaves) as [(outer ring, [hole rings])]."""
    if geometry["type"] == "Polygon":
        return [(geometry["coordinates"][0], geometry["coordinates"][1:])]
    return [(p[0], p[1:]) for p in geometry["coordinates"]]


def _load():
    """Read Natural Earth's countries once (downloaded on the building machine)."""
    global _COUNTRIES, _NAMES
    if _COUNTRIES is not None:
        return
    from build_packs import session
    data = json.loads(session().get(NE_COUNTRIES, timeout=300).content)
    _COUNTRIES, _NAMES = [], {}
    for feature in data["features"]:
        p = feature["properties"]
        code = p.get("ISO_A2_EH") or p.get("ISO_A2") or ""
        name = SHORT_NAMES.get(code) or p["ADMIN"]
        polygons = []
        for outer, holes in _polygons(feature["geometry"]):
            xs, ys = [x for x, _ in outer], [y for _, y in outer]
            polygons.append(((min(xs), min(ys), max(xs), max(ys)), outer, holes))
        _COUNTRIES.append((name, code, polygons))
        for key in ("ADMIN", "NAME", "NAME_LONG", "NAME_EN", "NAME_SV", "NAME_NL", "NAME_JA", "NAME_ZH", "NAME_DE",
                    "NAME_FR", "NAME_ES", "NAME_KO"):
            if p.get(key):
                _NAMES.setdefault(str(p[key]).strip().lower(), name)


def _inside(x, y, ring):
    """Whether the point (x, y) is inside a ring of (x, y) corners (the even-odd rule)."""
    inside, j = False, len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def country_at(latitude, longitude, near=0.1):
    """The country at a latitude and longitude (degrees), or "" (at sea, in Antarctica, or not a number). A point
    just off a coast, within near degrees (about 10 km) of a country's border line, counts as that country: the
    50 million border file smooths coasts, so beaches and harbours can fall just outside."""
    try:
        y, x = float(latitude), float(longitude)
    except (TypeError, ValueError):
        return ""
    if not (-90 <= y <= 90 and -180 <= x <= 180) or (x == 0 and y == 0):
        return ""
    _load()
    for name, _, polygons in _COUNTRIES:
        for (west, south, east, north), outer, holes in polygons:
            if west <= x <= east and south <= y <= north and _inside(x, y, outer) \
                    and not any(_inside(x, y, h) for h in holes):
                return "" if name == "Antarctica" else name
    best, best_name = near * near, ""
    for name, _, polygons in _COUNTRIES:
        for (west, south, east, north), outer, _ in polygons:
            if west - near <= x <= east + near and south - near <= y <= north + near:
                for px, py in outer:
                    d = (px - x) ** 2 + (py - y) ** 2
                    if d < best:
                        best, best_name = d, name
    return "" if best_name == "Antarctica" else best_name


def country_named(name_or_code):
    """A country's everyday English name from an ISO 3166 two-letter code ("GB"), an English name in another form
    ("United Kingdom of Great Britain and Northern Ireland") or a name in Swedish, Dutch, Japanese, Chinese, German,
    French, Spanish or Korean ("Sverige", "Nederland", "日本"); "" when unknown."""
    text = " ".join(str(name_or_code or "").replace("_", " ").split()).strip(" .")
    if not text:
        return ""
    if text.lower() in OTHER_NAMES:
        return OTHER_NAMES[text.lower()]
    _load()
    if len(text) == 2 and text.isalpha() and text.isupper():
        return next((name for name, code, _ in _COUNTRIES if code == text), "")
    return _NAMES.get(text.lower(), "")


def place_name(*parts):
    """A place from its parts, most specific first ("Kyoto", "Japan" -> "Kyoto, Japan"), leaving out empty parts
    and a part repeated ("Singapore", "Singapore" -> "Singapore")."""
    out = []
    for part in parts:
        part = " ".join(str(part or "").split()).strip(" ,.")
        if part and part.lower() not in (p.lower() for p in out):
            out.append(part)
    return ", ".join(out)


CONTINENTS = re.compile(r"^(north and central america|north america|central america|south america|latin america|"
                        r"europe|asia|africa|oceania|australia and oceania|antarctica|middle east|caribbean)$", re.I)


def place_from_text(text, most=3):
    """A row's place from a museum's place text, in the forms museums write it: "United States: Massachusetts,
    Cambridge", "Cleveland, Cuyahoga County, Ohio, United States, North and Central America", "Dannevirke (New
    Zealand)" or "Japan" -> "Cambridge, Massachusetts, USA", "Cleveland, Ohio, USA", "Dannevirke, New Zealand",
    "Japan". At most most parts are kept (the country and the most specific ones); "" when the text names no
    country this file knows (the country must be recognised, so an unclear text gives no place)."""
    text = " ".join(str(text or "").split()).strip(" .;")
    if not text:
        return ""
    m = re.match(r"^(.+?)\s*\(([^()]+)\)$", text)                  # "Dannevirke (New Zealand)"
    if m:
        parts = [m.group(1), m.group(2)]
    elif ":" in text:                                               # "United States: Massachusetts, Cambridge"
        country, rest = text.split(":", 1)
        parts = [p for p in reversed(rest.split(",")) if p.strip()] + [country]
    else:                                                           # most specific first already
        parts = text.split(",")
    parts = [p.strip() for p in parts if p.strip() and not CONTINENTS.match(p.strip())
             and not re.search(r"\b(county|province|prefecture|parish|district)$", p.strip(), re.I)]
    if not parts:
        return ""
    country = country_named(parts[-1])
    if not country:
        return ""
    inner = list(dict.fromkeys(p for p in parts[:-1] if country_named(p) != country))[:most - 1]
    return place_name(*inner, country)


def where(place, kind=None):
    """The place fields to add to a row: {"place": ..., "place_kind": ...}, or {} when there is no place, so a
    builder can write {**row, **where(place)}."""
    if not place:
        return {}
    return {"place": place, "place_kind": kind} if kind and kind != "photo" else {"place": place}


def with_place(entries, place, kind=None):
    """Pack entries [(name, JPEG or None, row)] with every row given the same place (a collection whose authors took
    all its photos in one city or country), keeping a row's own place when it already has one."""
    if not place:
        return entries
    return [(name, data, row if row.get("place") else {**row, **where(place, kind)}) for name, data, row in entries]


def main(argv=None):
    """Print the country at a latitude and longitude, or the English name of a country name or code."""
    argv = sys.argv[1:] if argv is None else argv
    print(country_at(argv[0], argv[1]) if len(argv) == 2 else country_named(" ".join(argv)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
