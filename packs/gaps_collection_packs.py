"""Collection packs for the GAPS the picture category inventory found (November 2026): two general museums, everyday
photos with alt text people wrote, old maps, dated fashion and archaeology, public health behaviours and algae blooms,
rocks, minerals and fossils, and aerial photographs. Used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one
question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

Every answer is the source's own words (a museum's alt text, label or description, a photographer's alt text, a
library's title and date, the CDC's caption, a Commons category's name), never a guess. The content rules of the open
packs apply (service_packs.safety: nothing sexual, no torture or execution, no dead or injured child; graphic pictures
marked; child rows marked).

The packs (GAP_COLLECTION_PACKS):
  aic_collection        The Art Institute of Chicago: public-domain works (is_public_domain) of every department,
                        the same number from each (AIC_DEPARTMENTS), "Tell me about this museum object." from the
                        record (title, kind, maker, date, medium), its short description (CC0) or else its longer
                        description (CC BY 4.0, credited) and its subjects. Works with the museum's own alt text
                        are left out: the kit's art_institute collection has every one of them. Works tagged or
                        worded as nudes or erotica are left out (museum_art_nudes and erotic_art have them).
  cleveland_collection  The Cleveland Museum of Art Open Access: CC0 works (share_license_status) of every department,
                        the same number from each, "Tell me about this museum object." from the record and the
                        curators' description. Nudes and erotica left out as above.
  wordpress_photos      The WordPress Photo Directory (wordpress.org/photos): CC0 photos, each with the alt text its
                        contributor wrote and the directory's volunteer moderators checked, as "Write a short
                        description ...". Photos of every kind (people, animals, food, places, things).
  loc_maps              Library of Congress Geography and Map Division: maps from its online collections (general
                        maps, battles, cities and towns, cultural landscapes, Civil War, county landownership,
                        Sanborn fire insurance maps), only those published in 1930 or before or made by the US
                        government (public domain in the US), "What is this map?" from the Library's title, date and
                        publisher.
  europeana_fashion_archaeology  Europeana's fashion and archaeology themes: English records whose own rights are
                        CC0, the Public Domain Mark or CC BY, "Describe this picture." from the title and description.
  cdc_phil_health_behaviour  CDC Public Health Image Library: public-domain photos of health behaviours (hand
                        washing, masks, smoking and tobacco, exercise, seat belts, helmets, sunscreen, insect
                        repellent), "Describe this picture." from the CDC's caption; no patients, lesions or
                        microscope pictures.
  cdc_phil_algae        CDC PHIL: public-domain photos of harmful algal blooms and cyanobacteria in lakes and rivers,
                        the CDC's caption and a short safety note (stay out, keep dogs out).
  commons_rocks_fossils Wikimedia Commons categories of minerals, gemstones, meteorites, rocks and fossils (CC0, public
                        domain or CC BY files only), "What is this?" from the category's name. (Smithsonian NMNH's own
                        pictures could not be used: its picture server, ids.si.edu, disallows all robots.)
  commons_nara_aerial   US National Archives aerial photographs as copied to Wikimedia Commons (public domain, each
                        file's licence checked), "Describe this picture." from the file's own caption. (NARA's
                        catalogue itself blocks this program's robots, so its Commons copies are used.)

    python packs/gaps_collection_packs.py wordpress_photos --limit 8      (prints a few rows: a quick check)
"""

import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, needs_description, pass_random, first_sentences, ALT_TEXT
from body_packs import lead, made_in, NUDITY_WORDS, MINOR
from places import place_from_text
from service_packs import safety
from museum_general_packs import MUSEUM_QUESTION, EMPTY_TAGS, NOT_HERE, get_json
from food_packs import with_twins, sentence
from drug_firearm_packs import PHIL_DRUG_WORDS

ASK_DESCRIBE = "Describe this picture."
ASK_MAP = "What is this map?"
ASK_WHAT = "What is this?"
YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")


def shared_finish(key, items, limit, workers=4, pause=0.2):
    """archive_packs.finish_marked: the graphic pictures marked, refused ones left out, pictures fetched."""
    from archive_packs import finish_marked
    return finish_marked(key, items, limit, workers=workers, pause=pause)


def marked_rows(rows, *texts):
    """rows with the safety marks of their words ("graphic", "child"), or [] when safety() refuses them."""
    keep, marks = safety([r["answer"] for r in rows] + [t for t in texts if t])
    if not keep:
        return []
    if MINOR.search(" ".join(r["answer"] for r in rows)):
        marks["child"] = True             # the wide young-person words (putti, Madonna and Child ...)
    return [dict(r, **marks) for r in rows]


def nude_or_erotic(*texts):
    """True when a museum record's words name a nude or erotica (their own packs have those)."""
    words = " ".join(clean(t) for t in texts if t)
    return bool(NOT_HERE.search(words) or NUDITY_WORDS.search(words))


def museum_rows(credit, title, kind, artist, date, medium, text="", subjects=(), alt="", culture=""):
    """(rows, described) of one museum object: "Tell me about this museum object." from the record, its short text
    and subjects; "Write a short description ..." from the museum's own alt text. described is False when the
    record only names the object (no text, alt text or subjects)."""
    answer = lead(title, kind, artist, date, medium)
    culture = clean(culture)
    if culture and culture.lower() not in answer.lower():
        answer += f" It is from {culture}."
    text = first_sentences(clean(text), 70)
    if text:
        answer += " " + sentence(text)
    subjects = [t for t in subjects if t and not EMPTY_TAGS.match(t)]
    if subjects and not text:
        answer += " The museum lists these subjects: " + ", ".join(t.lower() for t in subjects[:8]) + "."
    rows = [{"question": MUSEUM_QUESTION, "answer": answer, "credit": credit}]
    alt = clean(alt)
    if len(alt.split()) >= 6:
        rows.append({"question": ALT_TEXT, "answer": sentence(alt), "credit": credit})
    return rows, bool(text or subjects or len(alt.split()) >= 6)


# ----------------------------------------------------------------- aic_collection

AIC = "https://api.artic.edu/api/v1/artworks/search"
AIC_DEPARTMENTS = {"PC-13": "Prints and Drawings", "PC-7": "Arts of Asia", "PC-14": "Textiles",
                   "PC-9": "Applied Arts of Europe", "PC-12": "Photography and Media", "PC-3": "Arts of the Americas",
                   "PC-4": "Arts of Greece, Rome, and Byzantium", "PC-10": "Painting and Sculpture of Europe",
                   "PC-1": "Arts of Africa", "PC-5": "Architecture and Design"}
AIC_TOP_ID, AIC_WINDOW = 270000, 3000      # record numbers run to about 260,000
AIC_FIELDS = ["id", "title", "department_title", "artwork_type_title", "thumbnail", "short_description", "description",
              "image_id",
              "artist_display", "date_display", "medium_display", "place_of_origin", "subject_titles",
              "classification_titles", "term_titles", "is_public_domain"]


def aic_post(s, body):
    """One search request (the API asks for at most 60 a minute, so each waits a second), or {}."""
    for attempt in range(3):
        time.sleep(1.1)
        try:
            r = s.post(AIC, json=body, timeout=60)
            if r.status_code == 200:
                return r.json()
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(5 * (attempt + 1))
    return {}


def aic_item(a):
    """(name, picture address, rows, described) for one Art Institute record, or None when it is not for this pack
    (not public domain, no picture, a nude or erotica, refused by the safety rules)."""
    title = clean(a.get("title"))
    if not a.get("is_public_domain") or not a.get("image_id") or not title:
        return None
    alt = clean((a.get("thumbnail") or {}).get("alt_text"))
    if len(alt.split()) >= 4 and not alt.startswith("A work made of"):
        return None                       # the kit's art_institute collection has every work with real alt text
    alt = ""                              # the museum's stock text ("A work made of ...") says only the material
    subjects = a.get("subject_titles") or []
    if nude_or_erotic(title, alt, a.get("short_description"), " ".join(subjects),
                      " ".join(a.get("term_titles") or [])):
        return None
    artist = re.sub(r"\s*\(.*", "", clean(a.get("artist_display")).split("\n")[0])
    page = f"https://www.artic.edu/artworks/{a['id']}"
    text, licence = clean(a.get("short_description")), "CC0 (public domain)"
    if not text and clean(a.get("description")):
        text, licence = clean(a.get("description")), "CC0 (public domain); description CC BY 4.0, Art Institute of Chicago"
    credit = f"Art Institute of Chicago, {licence}: {title}" + (f", {artist}" if artist else "") + f", {page}"
    rows, described = museum_rows(credit, title, a.get("artwork_type_title"), artist, a.get("date_display"),
                                  a.get("medium_display"), text, subjects, alt)
    rows = made_in(rows, place_from_text(a.get("place_of_origin")))
    rows = marked_rows(rows, title, alt)
    if not rows:
        return None
    picture = f"https://www.artic.edu/iiif/2/{a['image_id']}/full/843,/0/default.jpg"      # the museum's own size
    return f"aicg-{a['id']}.jpg", picture, rows, described


def aic_items(want, s=None):
    """(name, picture address, rows) for aic_collection: the same number from each department, from random windows
    of record numbers among the public-domain works with a picture."""
    s = s or session()
    s.headers["AIC-User-Agent"] = s.headers["User-Agent"]
    rng = pass_random(5101)
    per = max(2, want // len(AIC_DEPARTMENTS) + 1)
    items = []
    for department, name in AIC_DEPARTMENTS.items():
        base = [{"term": {"is_public_domain": True}}, {"term": {"department_id": department}},
                {"exists": {"field": "image_id"}}]
        total = (aic_post(s, {"query": {"bool": {"filter": base}}, "limit": 0}).get("pagination") or {}).get("total") \
            or 0
        # The search gives at most 1,000 results a query, so it is asked about random windows of record numbers.
        windows = list(range(0, AIC_TOP_ID, AIC_WINDOW))
        rng.shuffle(windows)
        found = 0
        for start in windows:
            if found >= per or build_packs.listing_out_of_time():
                break
            query = {"bool": {"filter": base + [{"range": {"id": {"gte": start, "lt": start + AIC_WINDOW}}}]}}
            data = aic_post(s, {"query": query, "fields": AIC_FIELDS, "limit": 100})
            records = data.get("data") or []
            rng.shuffle(records)
            for a in records[:max(10, per // 4)]:
                got = aic_item(a)
                if not got or found >= per:
                    continue
                file, picture, rows, described = got
                if not described:
                    needs_description(file, picture, rows[0]["credit"], "CC0", "open", text=rows[0]["answer"],
                                      title=clean(a.get("title")), reason="its record names the object but does not "
                                      "say what it shows", page_url=f"https://www.artic.edu/artworks/{a['id']}",
                                      extra={"department": name})
                    continue
                items.append((file, picture, rows))
                found += 1
        say(f"  Art Institute of Chicago {name}: {found} usable of {total}")
    return items


def aic_fetch(items, workers=3):
    """Download Art Institute pictures (items are (name, address, rows)) with the AIC-User-Agent header the museum
    asks programs to send (its picture server refuses requests without it); [(name, JPEG, rows)] for those that
    came, each tried up to three times."""
    import concurrent.futures
    from build_packs import smaller, considered, note_source
    s = session()
    s.headers["AIC-User-Agent"] = s.headers["User-Agent"]

    def one(item):
        """One picture, or None."""
        name, url, rows = item
        for attempt in range(3):
            time.sleep(0.5)
            try:
                r = s.get(url, timeout=60)
            except Exception:  # noqa: BLE001 - tried again
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code == 200:
                data = smaller(r.content)
                considered(name, url, "" if data else "the picture could not be read")
                if data:
                    note_source(name, url)
                return (name, data, rows) if data else None
            if r.status_code in (403, 404, 410):
                considered(name, url, f"could not be downloaded (the server answered {r.status_code})")
                return None
            time.sleep(10 * (attempt + 1))
        considered(name, url, "could not be downloaded after three tries")
        return None

    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        return [x for x in pool.map(one, items) if x]


def build_aic_collection(limit):
    """The aic_collection pack (see the module docstring): graphic pictures marked and refused ones left out
    (archive_packs), then the pictures fetched with the museum's header."""
    from archive_packs import graphic_rows, not_shown
    from build_packs import new_only
    items = [(n, u, graphic_rows(rows)) for n, u, rows in aic_items(int(limit * 1.2) + 2)
             if not not_shown(*(r["answer"] for r in rows))]
    items = new_only(items)                      # (a top-up pass: only pictures not in the pack yet)
    pass_random(5106).shuffle(items)
    if build_packs.NEEDS_ONLY:
        return []
    fetched = aic_fetch(items[:int(limit * 1.2) + 2])[:limit]
    say(f"aic_collection: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if r[0].get('child'))} marked child")
    return with_twins(fetched)


# ----------------------------------------------------------------- cleveland_collection

CMA = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_DEPARTMENTS = ("African Art", "American Painting and Sculpture", "Art of the Americas", "Chinese Art",
                   "Decorative Art and Design", "Drawings", "Egyptian and Ancient Near Eastern Art",
                   "European Painting and Sculpture", "Greek and Roman Art", "Islamic Art", "Japanese Art",
                   "Korean Art", "Medieval Art", "Modern European Painting and Sculpture", "Oceania", "Photography",
                   "Prints", "Textiles", "Indian and Southeast Asian Art")


def cma_item(a):
    """(name, picture address, rows, described) for one Cleveland record, or None (not CC0, no picture, a nude or
    erotica, refused by the safety rules)."""
    title = clean(a.get("title"))
    images = a.get("images") or {}
    web = ((images.get("print") or images.get("web") or {}) or {}).get("url")
    if a.get("share_license_status") != "CC0" or not web or not title:
        return None
    text = clean(a.get("digital_description") or a.get("wall_description") or a.get("description"))
    if nude_or_erotic(title, text, a.get("type"), a.get("technique")):
        return None
    maker = re.sub(r"\s*\(.*", "", clean(((a.get("creators") or [{}])[0] or {}).get("description")))
    culture = str((a.get("culture") or [""])[0]).split(",")[0]
    credit = f"Cleveland Museum of Art, CC0: {title}" + (f", {maker}" if maker else "") + f", {a.get('url', '')}"
    technique = clean(a.get("technique"))
    rows, described = museum_rows(credit, title, a.get("type"), maker, a.get("creation_date"),
                                  technique if len(technique) <= 80 else "", text, culture=culture)
    rows = made_in(rows, place_from_text(culture))
    rows = marked_rows(rows, title)
    if not rows:
        return None
    return f"cmag-{a['id']}.jpg", web, rows, described


def cma_items(want, s=None):
    """(name, picture address, rows) for cleveland_collection: the same number from each department, from random
    places in each department's CC0 works with a picture."""
    s = s or session()
    rng = pass_random(5102)
    per = max(2, want // len(CMA_DEPARTMENTS) + 1)
    items = []
    for department in CMA_DEPARTMENTS:
        first = get_json(s, CMA, params={"cc0": 1, "has_image": 1, "limit": 1, "department": department}) or {}
        total = (first.get("info") or {}).get("total") or 0
        starts = list(range(0, max(1, total), 100))
        rng.shuffle(starts)
        found = 0
        for skip in starts[:30]:
            if found >= per or build_packs.listing_out_of_time():
                break
            time.sleep(1)
            data = get_json(s, CMA, params={"cc0": 1, "has_image": 1, "limit": 100, "skip": skip,
                                            "department": department}) or {}
            records = data.get("data") or []
            rng.shuffle(records)
            for a in records[:max(5, per // 3)]:
                got = cma_item(a)
                if not got or found >= per:
                    continue
                file, picture, rows, described = got
                if not described:
                    needs_description(file, picture, rows[0]["credit"], "CC0", "open", text=rows[0]["answer"],
                                      title=clean(a.get("title")), reason="its record names the object but does not "
                                      "say what it shows", page_url=a.get("url", ""), extra={"department": department})
                    continue
                items.append((file, picture, rows))
                found += 1
        say(f"  Cleveland {department}: {found} usable of {total}")
    return items


def build_cleveland_collection(limit):
    """The cleveland_collection pack (see the module docstring)."""
    return shared_finish("cleveland_collection", cma_items(int(limit * 1.2) + 2), limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- wordpress_photos

WP = "https://wordpress.org/photos/wp-json/wp/v2/photos"
WP_FIELDS = "id,content,link,class_list,_links,_embedded"


def wp_alt(html_text):
    """The alt text of a WordPress photo from its rendered content (a paragraph), or ""."""
    return clean(re.sub(r"<[^>]+>", " ", html_text or ""))


def wp_item(p):
    """(name, picture address, rows) for one WordPress Photo Directory photo, or None (no alt text of at least six
    words, no picture, refused by the safety rules)."""
    alt = wp_alt((p.get("content") or {}).get("rendered"))
    media = ((p.get("_embedded") or {}).get("wp:featuredmedia") or [{}])[0] or {}
    sizes = (media.get("media_details") or {}).get("sizes") or {}
    picture = (sizes.get("large") or sizes.get("1536x1536") or {}).get("source_url") or media.get("source_url")
    if len(alt.split()) < 6 or not picture:
        return None
    author = (((p.get("_links") or {}).get("author") or [{}])[0].get("href") or "").rstrip("/").rsplit("/", 1)[-1]
    credit = f"Photo by WordPress.org user {author or 'unknown'}, WordPress Photo Directory, CC0, {p.get('link', '')}"
    categories = [c.split("photo_category-", 1)[1] for c in p.get("class_list") or [] if "photo_category-" in c]
    rows = marked_rows([{"question": ALT_TEXT, "answer": sentence(alt), "credit": credit}])
    if not rows:
        return None
    if "people" in categories:            # people photos: the whole pack is never used for picture-making
        rows = [dict(r, facts={"category": "people"}) for r in rows]
    return f"wpphoto-{p['id']}.jpg", picture, rows


def wp_items(want, s=None):
    """(name, picture address, rows) from random pages of the directory (100 photos a page, a second between
    requests)."""
    s = s or session()
    rng = pass_random(5103)
    first = s.get(WP, params={"per_page": 1, "_fields": "id"}, timeout=60)
    pages = int(first.headers.get("X-WP-TotalPages", "1") or 1) // 100 + 1
    order = list(range(1, pages + 1))
    rng.shuffle(order)
    items, seen = [], set()
    for page in order:
        if len(items) >= want or build_packs.listing_out_of_time():
            break
        time.sleep(1)
        data = get_json(s, WP, params={"per_page": 100, "page": page, "_embed": "wp:featuredmedia",
                                       "_fields": WP_FIELDS}) or []
        for p in data if isinstance(data, list) else []:
            got = wp_item(p)
            if got and got[0] not in seen:
                seen.add(got[0])
                items.append(got)
    say(f"  WordPress Photo Directory: {len(items)} photos with alt text")
    return items[:want]


def build_wordpress_photos(limit):
    """The wordpress_photos pack (see the module docstring)."""
    return shared_finish("wordpress_photos", wp_items(int(limit * 1.2) + 2), limit, workers=4, pause=0.2)


# ----------------------------------------------------------------- loc_maps

LOC_MAPS = "https://www.loc.gov/maps/"
LOC_MAP_SETS = ("general maps", "military battles and campaigns", "cities and towns", "cultural landscapes",
                "civil war maps", "county landownership maps", "sanborn maps")
US_GOVERNMENT = re.compile(r"\b(U\.\s?S\.|United States|Geological Survey|Coast and Geodetic|Army|Corps of Engineers|"
                           r"Department of|Bureau of|Census|National Park Service|USDA|Soil Conservation|"
                           r"Government Printing Office|Forest Service|Tennessee Valley Authority|Central Intelligence "
                           r"Agency)\b", re.I)


def map_year(record):
    """The earliest year a map record gives (its date), or 0."""
    years = [int(y) for y in YEAR.findall(str(record.get("date") or ""))]
    return min(years) if years else 0


def map_free(record):
    """(free, why): public domain in the US when published in 1930 or before, or made by the US government (its
    publisher field names a federal body); online and not restricted."""
    item = record.get("item") or {}
    publisher = clean(" ".join(item.get("created_published") or []) if isinstance(item.get("created_published"), list)
                      else item.get("created_published"))
    if record.get("access_restricted"):
        return False, ""
    year = map_year(record)
    if 0 < year <= 1930:
        return True, f"published in {year}"
    if US_GOVERNMENT.search(publisher):
        return True, "made by the US government"
    return False, ""


def map_rows(record, credit):
    """"What is this map?" from the Library's title, date and publisher (only what the record says)."""
    item = record.get("item") or {}
    title = clean(record.get("title")).rstrip(".")
    publisher = item.get("created_published")
    publisher = clean(publisher[0] if isinstance(publisher, list) and publisher else publisher)
    answer = f"This is a map: {title}."
    date = clean(record.get("date"))
    if date and date not in title:
        answer += f" The Library of Congress dates it {date}."
    publisher = re.sub(r"[\[\]]|\bS\.\s?l\.\s*:?|\bs\.\s?n\.,?", "", publisher).strip(" ,:;.")
    if not re.search(r"[A-Za-z]{3}", YEAR.sub("", publisher)):
        publisher = ""                    # only a date, or "place and publisher unknown"
    if publisher and publisher.lower() not in title.lower():
        answer += f" Published by {publisher.rstrip('.')}."
    return [{"question": ASK_MAP, "answer": answer, "credit": credit}]


def loc_map_items(want, s=None):
    """(name, picture address, rows) for loc_maps: the same number from each of LOC_MAP_SETS, from random result
    pages (the Library asks programs to wait between requests: five seconds here)."""
    from documentary_packs import loc_picture
    s = s or session()
    rng = pass_random(5104)
    per = max(2, want // len(LOC_MAP_SETS) + 1)
    items, seen = [], set()
    for part in LOC_MAP_SETS:
        found, pages = 0, list(range(1, 60))
        rng.shuffle(pages)
        for page in pages[:15]:
            if found >= per or build_packs.listing_out_of_time():
                break
            time.sleep(5)
            data = get_json(s, LOC_MAPS, params={"fo": "json", "c": 100, "sp": page, "at": "results",
                                                 "fa": f"partof:{part}|online-format:image"}) or {}
            for record in data.get("results") or []:
                free, why = map_free(record)
                picture = loc_picture(record)
                link = re.sub(r"^(https?:)?//", "https://", str(record.get("id") or ""))
                if not free or not picture or link in seen or found >= per:
                    continue
                seen.add(link)
                title = clean(record.get("title"))
                credit = f"{title[:150]}, Library of Congress, Geography and Map Division, public domain ({why}), " \
                         f"{link}"
                name = "locmap-" + re.sub(r"\W+", "_", link.rstrip("/").rsplit("/", 1)[-1])[:60] + ".jpg"
                items.append((name, picture, map_rows(record, credit)))
                found += 1
        say(f"  Library of Congress maps, {part}: {found} usable")
    return items


def build_loc_maps(limit):
    """The loc_maps pack (see the module docstring)."""
    return shared_finish("loc_maps", loc_map_items(int(limit * 1.2) + 2), limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- europeana_fashion_archaeology

EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EUROPEANA_FREE = re.compile(r"creativecommons\.org/(publicdomain/(zero|mark)/|licenses/by/\d)", re.I)
EUROPEANA_THEMES = {"fashion": "Europeana fashion theme", "archaeology": "Europeana archaeology theme"}


def europeana_item(record, theme):
    """(name, picture address, rows) for one Europeana record, or None (not English, not free, no picture, too short
    a text, refused by the safety rules)."""
    from medical_packs import tidy_record_text
    from documentary_packs import tidy, usable
    rights = " ".join(record.get("rights") or [])
    picture = (record.get("edmIsShownBy") or [""])[0]
    title = clean((record.get("title") or [""])[0])
    if not EUROPEANA_FREE.search(rights) or re.search(r"by-(sa|nc|nd)", rights) or not picture or not title \
            or (record.get("language") or []) != ["en"]:
        return None
    description = tidy_record_text(first_sentences(clean((record.get("dcDescription") or [""])[0]), 60))
    text = title if not description or description.lower() in title.lower() else f"{title.rstrip('.')}. {description}"
    answer = tidy(text)
    if not usable(answer):
        return None
    provider = clean((record.get("dataProvider") or ["Europeana"])[0])
    credit = f"{provider} via Europeana ({EUROPEANA_THEMES[theme]}), \"{title[:150]}\", {rights}, " \
             f"https://www.europeana.eu/item{record['id']}"
    rows = marked_rows([{"question": ASK_DESCRIBE, "answer": answer, "credit": credit}], title)
    if not rows:
        return None
    return "europeana-" + re.sub(r"\W+", "_", record["id"]).strip("_")[:80] + ".jpg", picture, rows


def europeana_items(want, s=None):
    """(name, picture address, rows) from the fashion and archaeology themes, English records only, free rights."""
    import os
    s = s or session()
    rng = pass_random(5105)
    key = os.environ.get("EUROPEANA_KEY") or "api2demo"     # Europeana's public test key unless the build has one
    items = []
    for theme in EUROPEANA_THEMES:
        cursor, found = "*", 0
        while cursor and found < want and not build_packs.listing_out_of_time():
            time.sleep(0.5)
            data = get_json(s, EUROPEANA, params={"wskey": key, "query": "*", "theme": theme, "cursor": cursor,
                                                  "qf": ["TYPE:IMAGE", "LANGUAGE:en"], "reusability": "open",
                                                  "rows": 100, "profile": "rich"}) or {}
            for record in data.get("items") or []:
                got = europeana_item(record, theme)
                if got:
                    items.append(got)
                    found += 1
            cursor = data.get("nextCursor")
        say(f"  Europeana {theme}: {found} usable")
    rng.shuffle(items)
    return items[:want]


def build_europeana_fashion_archaeology(limit):
    """The europeana_fashion_archaeology pack (see the module docstring)."""
    return shared_finish("europeana_fashion_archaeology", europeana_items(int(limit * 1.2) + 2), limit, workers=4,
                         pause=0.2)


# ----------------------------------------------------------------- CDC PHIL: health behaviours and algae blooms

PHIL_BEHAVIOUR_KEYWORDS = ("hand washing", "handwashing", "hand hygiene", "face mask", "smoking", "tobacco",
                           "cigarette", "physical activity", "exercise", "seat belt", "bicycle helmet", "sunscreen",
                           "insect repellent", "condom", "cough etiquette")
PHIL_BEHAVIOUR_WORDS = re.compile(r"\b(hand ?washing|wash\w* (his|her|their|the) hands|hand hygiene|hand sanitiz\w*|"
                                  r"masks?|respirators?|smok\w*|tobacco|cigarettes?|cigars?|e-cigarettes?|vap\w*|"
                                  r"physical activity|exercis\w*|walking|jogging|bicycl\w*|seat ?belts?|helmets?|"
                                  r"sunscreen|repellent|condoms?|cough\w*|sneez\w*)\b", re.I)
PHIL_ALGAE_KEYWORDS = ("harmful algal bloom", "algal bloom", "cyanobacteria", "blue-green algae", "algae")
PHIL_ALGAE_WORDS = re.compile(r"\b(blooms?|blooming|scum|spilled paint|discolou?red water)\b", re.I)
# Drawings from old manuals and microscope plates are not photos of a bloom in the water.
PHIL_NOT_A_BLOOM = re.compile(r"\b(illustrat\w*|plates?|morpholog\w*|drawings?|diagrams?|manual|wastewater|"
                              r"oxidation ponds?|lagoons?)\b", re.I)
PHIL_NOT_HERE = re.compile(r"\b(patients?|lesions?|ulcer\w*|rash\w*|abscess\w*|wounds?|autops\w*|cadaver|necro\w*|"
                           r"micrograph\w*|microscop\w*|magnifi\w*|stain\w*|agar|culture plates?|petri|specimens?|"
                           r"x-ray|radiograph\w*|tumou?rs?|cancer of|surgery|surgical)\b", re.I)
ALGAE_NOTE = ("Water with a bloom like this can make people and pets ill: stay out of it, keep dogs out, and do not "
              "drink it.")


def phil_kept(r, words):
    """Why a PHIL record is left out ("" when kept): not public domain, the topic's words not in its caption, or a
    patient, lesion, laboratory or microscope picture."""
    caption = r.get("caption") or ""
    if not r.get("public"):
        return "not marked public domain"
    if not words.search(caption):
        return "its caption does not name the topic"
    if PHIL_NOT_HERE.search(caption):
        return "a patient, lesion, laboratory or microscope picture"
    if words is PHIL_BEHAVIOUR_WORDS and PHIL_DRUG_WORDS.search(caption):
        return "a drug photo (cdc_phil_drugs has those)"
    if words is PHIL_ALGAE_WORDS and PHIL_NOT_A_BLOOM.search(caption):
        return "a drawing, a manual's plate or a treatment pond, not a bloom in open water"
    return ""


def phil_topic_items(key, keywords, words, want, note=""):
    """(name, picture address, rows) for one PHIL topic: the CDC's caption as "Describe this picture." (with note)."""
    from medical_packs import phil_records, phil_credit
    from med_vet_packs import phil_caption
    items = []
    for r in phil_records(keywords):
        if phil_kept(r, words):
            continue
        caption = phil_caption(r["caption"])
        if not caption:
            continue
        rows = marked_rows([{"question": ASK_DESCRIBE, "answer": caption + (f" {note}" if note else ""),
                             "credit": phil_credit(r), "facts": {"phil_id": r["pid"]}}])
        if rows:
            items.append((f"phil-{r['pid']}.jpg", r["picture"], rows))
        if len(items) >= want:
            break
    say(f"CDC PHIL {key}: {len(items)} usable")
    return items


def build_cdc_phil_health_behaviour(limit):
    """The cdc_phil_health_behaviour pack (see the module docstring)."""
    items = phil_topic_items("cdc_phil_health_behaviour", PHIL_BEHAVIOUR_KEYWORDS, PHIL_BEHAVIOUR_WORDS,
                             int(limit * 1.1) + 2)
    return shared_finish("cdc_phil_health_behaviour", items, limit, workers=3, pause=0.3)


def build_cdc_phil_algae(limit):
    """The cdc_phil_algae pack (see the module docstring)."""
    items = phil_topic_items("cdc_phil_algae", PHIL_ALGAE_KEYWORDS, PHIL_ALGAE_WORDS, int(limit * 1.1) + 2,
                             ALGAE_NOTE)
    return shared_finish("cdc_phil_algae", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- Wikimedia Commons: rocks, minerals, fossils

def rock(category, thing, about="", deeper=True):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, rows)."""
    rows = [(ASK_WHAT, f"This is {thing}." + (f" {about}" if about else ""))]
    return (category, deeper, rows)


ROCKS_FOSSILS = [
    rock("Quartz", "quartz, a common mineral", "It is hard enough to scratch glass."),
    rock("Amethyst", "amethyst, a purple kind of quartz"),
    rock("Pyrite", "pyrite (fool's gold), a brassy yellow mineral"),
    rock("Calcite", "calcite, a common mineral that fizzes in acid"),
    rock("Fluorite", "fluorite, a mineral that grows in cubes"),
    rock("Malachite", "malachite, a green copper mineral"),
    rock("Gypsum", "gypsum, a soft mineral you can scratch with a fingernail"),
    rock("Mica", "mica, a mineral that splits into thin sheets"),
    rock("Feldspar", "feldspar, the most common mineral group in the Earth's crust"),
    rock("Halite", "halite (rock salt)"),
    rock("Gemstones", "a gemstone"),
    rock("Meteorites", "a meteorite, a rock that fell from space"),
    rock("Granite", "granite, an igneous rock"),
    rock("Basalt", "basalt, a dark volcanic rock"),
    rock("Obsidian", "obsidian, natural volcanic glass", "Its broken edges can be very sharp."),
    rock("Pumice", "pumice, a light volcanic rock full of holes that can float"),
    rock("Sandstone", "sandstone, a sedimentary rock made of sand grains"),
    rock("Limestone", "limestone, a sedimentary rock"),
    rock("Marble (rock)", "marble, a metamorphic rock"),
    rock("Slate", "slate, a metamorphic rock that splits into flat sheets"),
    rock("Geodes", "a geode: a hollow rock lined with crystals"),
    rock("Fossils", "a fossil"),
    rock("Ammonite fossils", "an ammonite fossil, the coiled shell of an extinct sea animal"),
    rock("Trilobite fossils", "a trilobite fossil, an extinct sea animal"),
    rock("Dinosaur fossils", "a dinosaur fossil"),
    rock("Fossil leaves", "a fossil leaf"),
    rock("Petrified wood", "petrified wood: wood turned to stone"),
    rock("Amber", "amber, fossil tree resin"),
    rock("Shark teeth fossils", "a fossil shark tooth"),
]


def build_commons_rocks_fossils(limit):
    """The commons_rocks_fossils pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(ROCKS_FOSSILS, limit, "rocks")


# ----------------------------------------------------------------- Wikimedia Commons: NARA aerial photographs

AERIAL = "This is an aerial photograph: a view of the ground from above, taken from an aircraft."
AERIAL_WORDS = re.compile(r"\b(aerial|air view|from the air|bird'?s[- ]eye|overhead view|airscape)\b", re.I)
NARA_AERIAL = [
    ("Aerial photographs from the National Archives and Records Administration", True, [(ASK_WHAT, AERIAL)],
     AERIAL_WORDS),
    ("Aerial photographs of the United States by the United States Department of Agriculture", True,
     [(ASK_WHAT, AERIAL)], AERIAL_WORDS),
    ("Aerial photographs of the United States by the United States Geological Survey", True, [(ASK_WHAT, AERIAL)],
     AERIAL_WORDS),
]


def build_commons_nara_aerial(limit):
    """The commons_nara_aerial pack: NARA's (and USDA's and USGS's) aerial photographs on Commons, only files whose
    words say the photo is aerial; "What is this?" from the category, and the file's own caption as "Write a short
    description ..." where it is a real one (home_packs.build_commons_topic adds it)."""
    from home_packs import build_commons_topic
    return build_commons_topic(NARA_AERIAL, limit, "aerial")


# ----------------------------------------------------------------- the packs

GAP_COLLECTION_PACKS = {
    "aic_collection": (build_aic_collection,
                       "The Art Institute of Chicago, public API (https://api.artic.edu/docs/): public-domain works "
                       "(CC0) of every department, each credited below; alt text and short descriptions CC0."),
    "cleveland_collection": (build_cleveland_collection,
                             "The Cleveland Museum of Art Open Access (CC0, https://openaccess-api.clevelandart.org): "
                             "CC0 works of every department, each credited below."),
    "wordpress_photos": (build_wordpress_photos,
                         "The WordPress Photo Directory (https://wordpress.org/photos/license/): every photo CC0, "
                         "with the alt text its contributor wrote; each credited below."),
    "loc_maps": (build_loc_maps,
                 "Library of Congress, Geography and Map Division (https://www.loc.gov/maps/): maps published in 1930 "
                 "or before, or made by the US government (public domain in the US), each credited below."),
    "europeana_fashion_archaeology": (build_europeana_fashion_archaeology,
                                      "Europeana (https://www.europeana.eu), fashion and archaeology themes: records "
                                      "whose own rights are CC0, the Public Domain Mark or CC BY, each credited "
                                      "below."),
    "cdc_phil_health_behaviour": (build_cdc_phil_health_behaviour,
                                  "CDC Public Health Image Library (https://phil.cdc.gov): public-domain photos of "
                                  "health behaviours, each item's public-domain field checked."),
    "cdc_phil_algae": (build_cdc_phil_algae,
                       "CDC Public Health Image Library (https://phil.cdc.gov): public-domain photos of harmful "
                       "algal blooms, each item's public-domain field checked."),
    "commons_rocks_fossils": (build_commons_rocks_fossils,
                              "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY "
                              "(credited below) of mineral, gemstone, meteorite, rock and fossil categories."),
    "commons_nara_aerial": (build_commons_nara_aerial,
                            "Wikimedia Commons copies of US National Archives, USDA and USGS aerial photographs "
                            "(public domain, works of the US government; each file's licence checked)."),
}
GAP_COLLECTION_LIMITS = {
    "aic_collection": 4000,                 # 10 departments, the same number from each (about 59,000 open works)
    "cleveland_collection": 4000,           # 19 departments (about 38,000 CC0 works with a picture)
    "wordpress_photos": 6000,               # about 47,000 CC0 photos with alt text
    "loc_maps": 1400,                       # 7 map collections, 1930 or before or US government
    "europeana_fashion_archaeology": 1500,  # about 4,600 English open records in the two themes
    "cdc_phil_health_behaviour": 300,       # PHIL keyword searches; many captions name patients
    "cdc_phil_algae": 60,                   # a few dozen PHIL bloom photos
    "commons_rocks_fossils": 1500,          # 29 categories, an even share each
    "commons_nara_aerial": 800,             # aerial files with their own caption
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
GAP_COMMONS_KEYS = ("commons_rocks_fossils", "commons_nara_aerial")
# The packs with people in them: never used for picture-making (training-kit PEOPLE_AND_BODILY_PACK_KEYS).
GAP_PEOPLE_PACKS = ("wordpress_photos", "europeana_fashion_archaeology", "cdc_phil_health_behaviour",
                    "aic_collection", "cleveland_collection")


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a gap collection pack builder.")
    parser.add_argument("key", choices=sorted(GAP_COLLECTION_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = GAP_COLLECTION_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
