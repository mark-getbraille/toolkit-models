"""Pack builders for documentary photographs of nature, places, cultures and people around the world, with the
captions their makers wrote ("National Geographic and similar"), used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}, plus "place" when the record says where the photo was taken (see places.py) and
"child": True when the caption mentions a child (expression_packs.CHILD). The limit counts pictures.

Every picture gets "Describe this picture." with its maker's own caption, tidied (catalogue codes, square brackets
and file notes taken out), at least 6 words long. A picture whose record names the place also gets "Where was this
photo taken?" ("It was taken in Indianapolis, Indiana, USA."), as a second row for the same picture (food_packs.
with_twins), so the zip holds the picture once. Nothing is written by an AI model.

National Geographic itself is a commercial, copyrighted publisher with no open dataset or licence, so nothing of
it is used; nor are commercial picture agencies (Getty, AP, Reuters, BBC). These are the open alternatives:

  loc_highsmith      Library of Congress, Carol M. Highsmith Archive: about 70,000 colour photographs of every US
                     state (1980s to 2020s), landscapes, towns, people at work and festivals, with long titles written
                     from the photographer's notes. She gave the photographs to the public: "No known restrictions on
                     publication." Place from the record ("Indianapolis, Indiana, USA").
  loc_fsa            Library of Congress, Farm Security Administration / Office of War Information photographs
                     (1935-1945; Dorothea Lange, Walker Evans, Gordon Parks, Marion Post Wolcott and others): rural and
                     town life in the USA, with the agency's captions. US government work, "No known restrictions".
                     Black-and-white (about 171,000) and colour (about 1,600) collections.
  loc_world          Library of Congress, photographs of places and peoples around the world with no known
                     restrictions: the Photochrom prints (about 7,500 colour views of Europe, the Middle East and North
                     Africa, 1890s-1900s) and the G. Eric and Edith Matson collection (about 22,000 photographs of the
                     Middle East, 1898-1946; its Bible-verse slide titles are left out).
  npgallery          US National Park Service, NPGallery: photographs from the national parks (wildlife, landscapes,
                     historic places, people), each with the park's accessibility alt text and its description. Only
                     items marked "Public domain". Place: the park ("Wind Cave National Park, USA").
  earth_observatory  NASA Earth Observatory, Image of the Day (now on science.nasa.gov): satellite and astronaut
                     pictures of the Earth with the alt text NASA's writers gave each picture. NASA's own pictures are
                     not under copyright; pictures whose article names a commercial maker (Planet, Maxar, Airbus and
                     the like) or a copyright are left out.
  eso                European Southern Observatory: photographs of the Atacama Desert observatories in Chile (Paranal,
                     La Silla, Chajnantor), their landscapes, night skies and people, with ESO's captions. CC BY 4.0
                     (https://www.eso.org/public/copyright/). Deep-space pictures are left out (only pictures whose
                     record gives an Earth, sky, observatory or people type). Place from the record's category.
  usgs               US Geological Survey multimedia gallery: photographs of volcanoes, rivers, coasts, glaciers,
                     wildlife and scientists at work, with USGS's captions. Public domain (only pages saying "Public
                     Domain"); maps, charts and diagrams are left out.
  commons_valued     Wikimedia Commons Valued images (the best picture of each subject, chosen by reviewers): files
                     with an English caption (captions are CC0) whose picture is CC0, public domain or CC BY. Place
                     from the camera's coordinates. (Featured pictures and Quality images under these licences are
                     already in the "commons" pack; their CC BY-SA files are a share-alike kit entry, see
                     training-kit/kit/documentary_sources.py.)

Looked at and not used here (checked at the source in November 2026), with the reason:
  National Geographic, Getty, AP, Reuters, BBC    Commercial and copyrighted; no open licence. Not scraped.
  NOAA Photo Library             Public domain, but photolib.noaa.gov now forwards to www.noaa.gov/digital-library,
                                 which refused this machine (CloudFront 403); its Flickr copy needs a Flickr API key.
  USFWS National Digital Library Public domain, but the old CONTENTdm site forwards to fws.gov/search/images, whose
                                 search service is not public (its address is built inside the page's script).
  US Forest Service, BLM, USDA, Natural England, NZ Department of Conservation, Flickr Commons (National Library of
  Ireland, State Library NSW and others), Biodiversity Heritage Library    Their photos are on Flickr (or, for BHL,
                                 its API), which needs a free API key: sign-up (listed in documentary_sources.py).
  Geograph Britain and Ireland, Geograph Deutschland, Geograph Channel Islands    CC BY-SA (share-alike), and the
                                 project asks that its live site and API are not used for bulk or training downloads;
                                 its bulk image sets come by request form or Kaggle (sign-up, see
                                 documentary_sources.py).
  Unsplash Lite                  Unsplash's own dataset terms (no redistribution): a personal-use kit entry.
  European Space Agency          CC BY-SA 3.0 IGO for some pictures, but its multimedia gallery forwarded this machine
                                 to the home page; no listing could be read.
  Australian Antarctic Division  images.aad.gov.au did not answer from this machine.
  Parks Canada                   Its photos are Crown copyright, not under an open licence.
  NASA Image and Video Library   Already in the kit (training-kit/kit/sources.py "nasa").

    python packs/documentary_packs.py npgallery --limit 8      (prints a few rows: a quick check of one builder)
"""

import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, fetch_all, say, LONG_SIDE, COMMONS_API, COMMONS_FREE
from build_packs import pass_random, new_only, already_in_pack  # top-up passes (see build_packs)
from build_packs import listing_out_of_time, out_of_time
from build_packs import needs_description  # pictures set aside for a description (see build_packs)
from food_packs import with_twins, count_pictures
from expression_packs import CHILD
from world_packs import capped_words, full_stop
from places import country_at, country_named, place_name, where

ASK_DESCRIBE = "Describe this picture."
ASK_WHERE = "Where was this photo taken?"
# Country names said with "the" ("taken in the USA"), as in the kit's sources.THE_COUNTRIES.
THE_COUNTRIES = {"usa", "uk", "netherlands", "philippines", "united arab emirates", "czechia", "bahamas", "gambia",
                 "maldives", "vatican city", "west bank", "gaza strip"}
# Words that a description must not have (nothing sexual, as SOURCE-RULES.md says).
NOT_SHOWN = re.compile(r"\b(nud\w*|naked|nudity|topless|erotic\w*|sex\w*|porn\w*|lingerie|undress\w*)\b", re.I)
# Catalogue codes and file notes in captions: "LC-USF34-012345-D", "(LOT 1234)", "digital file from original",
# "1 photograph : digital, tiff file, color", call numbers and negative numbers.
CATALOGUE = re.compile(r"\s*\((?:LOT|LC|Neg\.?|No\.?)\s*[\w\s.:-]*\)|\bLC-[A-Z0-9]+-[\w-]+\b|"
                       r"\bdigital file from [^.;]*|"
                       r"\b1 photograph\s*:[^.;]*|\b(?:neg(?:ative)?|no)\.?\s*\d[\w-]*\b|\[\s*(?:graphic|picture)\s*\]",
                       re.I)


def tidy(text):
    """A caption as an answer: HTML and square brackets taken out (the Library of Congress puts titles it wrote
    itself in brackets), catalogue codes removed, spaces tidied, a capital first letter and a full stop."""
    text = clean(text)
    text = CATALOGUE.sub("", text)
    text = re.sub(r"[\[\]]", "", text)
    text = re.sub(r"\s+([,.;:])", r"\1", " ".join(text.split())).strip(" ,;:-")
    text = re.sub(r"[,;:]\s*$", "", text)
    return full_stop(text[:1].upper() + text[1:]) if text else ""


def usable(answer, words=6):
    """True when an answer is at least words words long and says nothing sexual."""
    return len(answer.split()) >= words and not NOT_SHOWN.search(answer)


def place_words(place):
    """A place as it is said in a sentence: "the USA", "Paris, France", "Kyoto, Japan"."""
    return ("the " + place) if place.lower() in THE_COUNTRIES else place


def picture_rows(answer, credit, place="", texts=()):
    """The rows of one picture: "Describe this picture." with answer and, when the record gives a place, "Where was
    this photo taken?"; all marked "child" when the answer or any of texts mentions a child."""
    rows = [{"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **where(place)}]
    if place:
        rows.append({"question": ASK_WHERE, "answer": f"It was taken in {place_words(place)}.", "credit": credit,
                     **where(place)})
    if any(CHILD.search(t or "") for t in (answer, *texts)):
        rows = [dict(r, child=True) for r in rows]
    return rows


def get_json(s, url, params=None, tries=4, pause=5):
    """The JSON at url, waiting and trying again when the server is busy (429 or 5xx); None when it never came."""
    for attempt in range(tries):
        if out_of_time():                  # no waiting and trying again once the time is up
            return None
        try:
            r = s.get(url, params=params, timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (403, 404):
                return None
            after = r.headers.get("Retry-After", "")
            time.sleep(int(after) if after.isdigit() else pause * (attempt + 1))
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(pause * (attempt + 1))
    return None


def finish(key, items, limit, workers=4, pause=0.2):
    """Shuffle (name, address, rows) items, download the pictures and return the pack entries (at most limit
    pictures), saying how many came and how many are marked child. On a top-up pass the pictures already in the
    published pack are left out first (new_only), so the places go to new ones."""
    items = new_only(items)
    pass_random(len(key) * 7919).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.2) + 2], workers=workers, pause=pause)[:limit]
    say(f"{key}: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if len(r) > 1)} with a place, "
        f"{sum(1 for _, _, r in fetched if r[0].get('child'))} marked child")
    return with_twins(fetched)


# ----------------------------------------------------------------- Library of Congress

LOC = "https://www.loc.gov/"
# Matson slide titles that are Bible verses ("Mark 1:13. And He was there in the wilderness ..."), not descriptions.
BIBLE_VERSE = re.compile(r"^\W*(?:[123] )?[A-Z][a-z]+\.? \d+:\d+")
LOC_NOT_A_PHOTO = re.compile(r"\b(map|maps|plan|plans|drawing|diagram|title card|caption card|untitled)\b", re.I)
LOC_SETS = {
    # key: [(search address, extra parameters, number of records, name in the credit)]
    "loc_highsmith": [("collections/carol-m-highsmith/", {}, 70000,
                       "Carol M. Highsmith Archive, Library of Congress, Prints and Photographs Division")],
    "loc_fsa": [("collections/fsa-owi-black-and-white-negatives/", {}, 171000,
                 "U.S. Farm Security Administration/Office of War Information Black & White Photographs, Library of "
                 "Congress, Prints and Photographs Division"),
                ("collections/fsa-owi-color-photographs/", {}, 1600,
                 "U.S. Farm Security Administration/Office of War Information Color Photographs, Library of Congress, "
                 "Prints and Photographs Division")],
    "loc_world": [("collections/photochrom-prints/", {}, 7500,
                   "Photochrom Prints, Library of Congress, Prints and Photographs Division"),
                  ("photos/", {"fa": "partof:matson (g. eric and edith) photograph collection|online-format:image"},
                   22000, "G. Eric and Edith Matson Photograph Collection, Library of Congress, Prints and "
                          "Photographs Division")],
}


def loc_picture(record):
    """The address of a record's picture: the largest of the Library's ready-made sizes that is at most about
    LONG_SIDE pixels, or ""."""
    best, best_side = "", 0
    for url in record.get("image_url") or []:
        m = re.search(r"#h=(\d+)&w=(\d+)", url)
        side = max(int(m.group(1)), int(m.group(2))) if m else 0
        if side <= LONG_SIDE * 1.1 and side > best_side:
            best, best_side = url.split("#")[0], side
    return best


def loc_place(record):
    """Where a Library of Congress photo was taken, from its record: the first "place" heading ("Indiana--Marion
    County--Indianapolis", "Ireland--County Cork") with the record's country, most specific first and at most three
    parts ("Indianapolis, Indiana, USA"); "" when the record names no country."""
    item = record.get("item") or {}
    heading = clean(((item.get("place") or [{}])[0] or {}).get("title"))
    heading = re.sub(r"\s*\((county|state|region|province|municipality|district|parish)\)", "", heading, flags=re.I)
    parts = [p.strip(" .") for p in heading.split("--") if p.strip(" .")]
    listed_country = country_named((record.get("location_country") or [""])[0])
    first_country = country_named(parts[0]) if parts else ""
    country = listed_country or first_country
    if not country:                    # no heading: a country among the record's location words ("switzerland")
        return next((c for c in map(country_named, record.get("location") or []) if c), "")
    rest = parts[1:] if parts and first_country == country else parts
    rest = [p for p in rest if not re.search(r"\b(county|parish|states|region|municipality|borough)$", p, re.I)]
    return place_name(*list(reversed(rest))[:2], country)


def loc_free(record):
    """True when the Library says the photo has no known restrictions on publication (and it is online)."""
    advisory = clean((record.get("item") or {}).get("rights_advisory"))
    return not record.get("access_restricted") and advisory.lower().startswith("no known restrictions")


def loc_items(s, path, extra, total, name, want, rng):
    """[(name, picture address, rows)] from random result pages of one Library of Congress collection or search,
    a few from each page and each caption once, until want pictures are found (or 60 pages are read). The Library
    asks programs to keep to about one request a second on its search pages, so each page waits."""
    pages = list(range(1, max(2, total // 100) + 1))
    rng.shuffle(pages)
    items, answers = [], set()
    per_page = max(3, want // 25)          # a few from each page: a page holds one place or one photographer's day
    for page in pages[:60]:
        if listing_out_of_time():          # leave the rest of the time for fetching what was found
            say(f"  {name.split(',')[0]}: stopped looking at half the time limit")
            break
        taken = 0
        time.sleep(2)
        data = get_json(s, LOC + path, {"fo": "json", "c": 100, "sp": page, "at": "results", **extra}, pause=15)
        for record in (data or {}).get("results") or []:
            title = clean(record.get("title"))
            answer = tidy(title)
            picture = loc_picture(record)
            if already_in_pack(url=picture):   # in the published pack already (a top-up pass): not counted
                continue
            if not loc_free(record) or not picture or LOC_NOT_A_PHOTO.search(title) or taken >= per_page:
                continue
            item = record.get("item") or {}
            link = re.sub(r"^(https?:)?//", "https://", item.get("link") or record.get("id") or "")
            credit = f"{title[:150]}, {name}, no known restrictions on publication, {link}"
            if (not usable(answer) and not NOT_SHOWN.search(answer)) or BIBLE_VERSE.match(title):
                # Free, a photo, its caption too short or a Bible verse: set aside for a description.
                control = re.sub(r"\W", "", str(item.get("control_number") or item.get("id") or ""))
                needs_description(f"loc-{control or len(items)}.jpg", picture, credit,
                                  "no known restrictions on publication", title=title, page_url=link,
                                  place=loc_place(record),
                                  reason="its title is a Bible verse" if BIBLE_VERSE.match(title) else
                                  "its caption is under six words",
                                  extra={"summary": clean(item.get("summary")), "collection": name.split(",")[0],
                                         "date": clean(record.get("date")),
                                         "subjects": [clean(x) for x in (record.get("subject") or [])][:12]})
                continue
            if not usable(answer) or answer in answers:
                continue
            answers.add(answer)
            taken += 1
            control = re.sub(r"\W", "", str(item.get("control_number") or item.get("id") or len(items)))
            items.append((f"loc-{control}.jpg", picture, picture_rows(answer, credit, loc_place(record),
                                                                        [clean(item.get("summary"))])))
        if len(items) >= want:
            break
    say(f"  {name.split(',')[0]}: {len(items)} usable records")
    return items


def build_loc(key, limit):
    """A Library of Congress pack: records from each of its collections (in proportion to their size, at least a
    quarter each), their titles as answers."""
    s, rng, items = session(), pass_random(sum(map(ord, key))), []
    sets = LOC_SETS[key]
    total = sum(n for _, _, n, _ in sets)
    for path, extra, n, name in sets:
        if listing_out_of_time():
            break
        share = max(0.25, n / total) if len(sets) > 1 else 1.0
        items += loc_items(s, path, extra, n, name, int(limit * share * 1.3) + 4, rng)
    return finish(key, items, limit, workers=3, pause=0.5)


def build_loc_highsmith(limit):
    """The Carol M. Highsmith pack (see the module docstring)."""
    return build_loc("loc_highsmith", limit)


def build_loc_fsa(limit):
    """The FSA/OWI pack (see the module docstring)."""
    return build_loc("loc_fsa", limit)


def build_loc_world(limit):
    """The Photochrom and Matson pack (see the module docstring)."""
    return build_loc("loc_world", limit)


# ----------------------------------------------------------------- National Park Service, NPGallery

NPG = "https://npgallery.nps.gov/"
# Search words, so the pack spreads over many kinds of photos (NPGallery's search finds them in titles, keywords
# and descriptions).
NPG_WORDS = ("wildlife", "bison", "bear", "elk", "birds", "wildflowers", "landscape", "canyon", "mountain", "waterfall",
             "geyser", "glacier", "volcano", "desert", "forest", "coast", "beach", "cave", "river", "lake", "snow",
             "sunset", "night sky", "trail", "historic house", "lighthouse", "fort", "battlefield", "ranger",
             "visitors", "festival", "dance", "craft", "boat", "farm", "ruins", "petroglyph", "bridge", "garden")
NPG_NOT_A_PHOTO = re.compile(r"\b(brochure|map|maps|logo|poster|chart|diagram|graphic|illustration|drawing|sign "
                             r"design|infographic|newsletter|cover|plan)\b", re.I)


def npg_answer(asset):
    """An NPGallery photo's answer: its accessibility alt text and the first sentences of its description (at most
    about 70 words), or ""."""
    alt = tidy(asset.get("AltText"))
    if not usable(alt):
        return ""
    description = capped_words(clean(asset.get("Description")), 40)
    if description and description.lower()[:40] not in alt.lower() and not re.search(r"https?://|@", description):
        return capped_words(f"{alt} {tidy(description)}", 70)
    return alt


def npg_credit(asset):
    """The credit NPGallery asks for, with the photo's title and page."""
    statement = clean(asset.get("Copyright"))
    asked = re.search(r"credit:\s*'?([^']+)'?", statement)
    who = clean(asked.group(1)).rstrip(".") if asked else clean(asset.get("Publisher")) or "National Park Service"
    return (f"{clean(asset.get('Title'))[:120].rstrip('.')}, {who}; public domain (U.S. National Park Service), "
            f"{NPG}AssetDetail/{asset.get('AssetID')}")


def build_npgallery(limit):
    """The NPGallery pack: public-domain photos found with NPG_WORDS, the alt text and description as the answer,
    the park as the place. NPGallery's own 2,600-pixel copy ("proxyhires") is fetched, not the original (up to
    15 MB)."""
    s, items, seen = session(), [], set()
    rng = pass_random(71)
    per_word = int(limit * 1.3 / len(NPG_WORDS)) + 2
    for word in NPG_WORDS:
        found = 0
        for page in range(1, 30):
            time.sleep(0.5)
            data = get_json(s, NPG + "api/search", {"keyword": word, "page": page})
            results = (data or {}).get("Results") or []
            for result in results:
                asset = result.get("Asset") or {}
                key = asset.get("AssetID")
                constraint = clean((asset.get("ConstraintsInformation") or {}).get("Constraint")).lower()
                if not key or key in seen or asset.get("PrimaryType") != "image" or constraint != "public domain" \
                        or NPG_NOT_A_PHOTO.search(clean(asset.get("Title"))):
                    continue
                answer = npg_answer(asset)
                units = [clean(u.get("Name")) for u in asset.get("NPSUnits") or [] if clean(u.get("Name"))]
                place = place_name(units[0], "USA") if len(units) == 1 else ""
                if not answer:              # public domain, a photo, but no alt text of six words: set aside
                    if not NOT_SHOWN.search(clean(asset.get("AltText"))):
                        seen.add(key)
                        needs_description(f"npgallery-{key}.jpg", f"{NPG}GetAsset/{key}/proxyhires.jpg",
                                          npg_credit(asset), "public domain", text=clean(asset.get("AltText")),
                                          title=clean(asset.get("Title")), place=place,
                                          page_url=f"{NPG}AssetDetail/{key}",
                                          reason="no accessibility alt text of six words or more",
                                          extra={"description": capped_words(clean(asset.get("Description")), 80),
                                                 "keywords": clean(asset.get("Keywords"))[:300]})
                    continue
                seen.add(key)
                items.append((f"npgallery-{key}.jpg", f"{NPG}GetAsset/{key}/proxyhires.jpg",
                              picture_rows(answer, npg_credit(asset), place, [clean(asset.get("Title"))])))
                found += 1
            if found >= per_word or len(results) < 48:
                break
    rng.shuffle(items)
    say(f"NPGallery: {len(items)} usable photos")
    return finish("npgallery", items, limit, workers=4, pause=0.3)


# ----------------------------------------------------------------- NASA Earth Observatory

SCIENCE = "https://science.nasa.gov/wp-json/wp/v2/"
EO_IMAGE_OF_THE_DAY = 22453            # the "science-org" term of Earth Observatory's Image of the Day
# Pictures not made by NASA or another open source (commercial satellite companies) or naming a copyright.
EO_NOT_NASA = re.compile(r"Planet Labs|PlanetScope|SkySat|Maxar|DigitalGlobe|WorldView|Airbus|Pl[ée]iades|SPOT \d|"
                         r"Satellogic|BlackSky|Capella|ICEYE|Umbra|©|\(c\)|copyright", re.I)
EO_DATE_ONLY = re.compile(r"^\s*\d{4}-\d{2}-\d{2}")
# Maps, charts and data plots (Earth Observatory has many): only pictures of the Earth itself are kept.
EO_NOT_A_PHOTO = re.compile(r"\b(maps?|charts?|graphs?|plots?|diagrams?|colou?r (scale|bar|key)|legend|"
                            r"animation|data visuali[sz]ation|model(led)? (output|data))\b", re.I)


def eo_picture(source_url):
    """A large copy of an Earth Observatory picture: its 720-pixel thumbnail's address without "_th", sized by the
    asset server to at most LONG_SIDE pixels."""
    base = source_url.split("?")[0]
    return re.sub(r"_th(\.\w+)$", r"\1", base) + f"?w={LONG_SIDE}&h={LONG_SIDE}&fit=clip"


def build_earth_observatory(limit):
    """The Earth Observatory pack: Image of the Day posts (random pages of the 9,000 or so), each post's featured
    picture with its alt text (written by NASA's writers; older posts, whose alt text is only a date or the
    title, are left out), after reading the post's article to leave out pictures made by commercial companies."""
    s, items = session(), []
    head = s.get(SCIENCE + "posts", params={"science-org": EO_IMAGE_OF_THE_DAY, "per_page": 50, "_fields": "id"},
                 timeout=60)
    total = int(head.headers.get("X-WP-TotalPages", "1") or 1)
    for page in range(1, total + 1):                  # newest first: older posts mostly have no real alt text
        if len(items) >= limit * 1.3:
            break
        posts = get_json(s, SCIENCE + "posts", {"science-org": EO_IMAGE_OF_THE_DAY, "per_page": 50, "page": page,
                                                "_fields": "id,link,title,featured_media"}) or []
        ids = [str(p["featured_media"]) for p in posts if p.get("featured_media")]
        media = {m["id"]: m for m in get_json(s, SCIENCE + "media", {"include": ",".join(ids), "per_page": 50,
                                                                     "_fields": "id,alt_text,source_url"}) or []}
        good, poor = [], []
        for post in posts:
            m = media.get(post.get("featured_media")) or {}
            alt = tidy(m.get("alt_text"))
            title = clean((post.get("title") or {}).get("rendered")).lower().rstrip(".")
            if not m.get("source_url") or EO_NOT_A_PHOTO.search(alt) or EO_NOT_A_PHOTO.search(title):
                continue
            if usable(alt, 10) and not EO_DATE_ONLY.match(alt) \
                    and title[:30] not in alt.lower():          # migrated posts often repeat the title as alt text
                good.append((post, m, alt))
            elif not NOT_SHOWN.search(alt):
                poor.append((post, m, alt))     # only a date or the title as alt text: set aside (checked below)
        if not good and not poor:
            continue
        articles = get_json(s, SCIENCE + "posts", {"include": ",".join(str(p["id"]) for p, _, _ in good + poor),
                                                   "per_page": 50, "_fields": "id,content"}) or []
        text = {a["id"]: clean((a.get("content") or {}).get("rendered")) for a in articles}
        for post, m, alt in poor:               # the same copyright check as the pack's pictures, first
            if post["id"] not in text or EO_NOT_NASA.search(text[post["id"]]):
                continue
            title = clean((post.get("title") or {}).get("rendered"))
            needs_description(f"earth-observatory-{post['id']}.jpg", eo_picture(m["source_url"]),
                              f"{title}, NASA Earth Observatory, {post.get('link')} (NASA images are not under "
                              "copyright)", "NASA, not under copyright", text=alt, title=title,
                              page_url=post.get("link") or "", reason="its alt text is only a date or the title",
                              extra={"article": capped_words(text[post["id"]], 120)})
        for post, m, alt in good:
            if post["id"] not in text or EO_NOT_NASA.search(text[post["id"]]):
                continue
            title = clean((post.get("title") or {}).get("rendered"))
            credit = f"{title}, NASA Earth Observatory, {post.get('link')} (NASA images are not under copyright)"
            items.append((f"earth-observatory-{post['id']}.jpg", eo_picture(m["source_url"]),
                          picture_rows(capped_words(alt, 90), credit)))
        time.sleep(0.5)
    say(f"Earth Observatory: {len(items)} usable posts")
    return finish("earth_observatory", items, limit, workers=4, pause=0.2)


# ----------------------------------------------------------------- European Southern Observatory

ESO = "https://www.eso.org/public/images/"
# ESO's picture categories in Chile, with the place each one is.
ESO_CATEGORIES = {"paranal": "Paranal Observatory, Chile", "lasilla": "La Silla Observatory, Chile",
                  "alma": "Chajnantor Plateau, Chile", "apex": "Chajnantor Plateau, Chile"}
# (The ELT category is left out: most of its pictures are renderings of the telescope being built.)
# Record types of documentary photos (the Earth and its sky, observatories, people), not deep-space pictures.
ESO_NOT_A_PHOTO = re.compile(r"\b(render\w*|artist['’]s (impression|view|rendering)|illustration|animation|"
                             r"computer[- ]generated|simulat\w*|mock-?up|diagram|infographic|drawing)\b", re.I)
ESO_DOCUMENTARY = re.compile(r"Local Universe : Earth|Unspecified : (Technology|People)|Observatory|Facility|"
                             r"Night Sky|Landscape|Atmosphere", re.I)


def eso_page(s, image_id):
    """(description, credit, type) of an ESO picture from its page, or None."""
    try:
        page = s.get(f"{ESO}{image_id}/", timeout=60).text
    except Exception:  # noqa: BLE001 - left out
        return None
    start, stop = page.find("<h1"), page.find('class="credit"')
    if start < 0 or stop < 0:
        return None
    body = page[start:stop]
    paragraphs = [clean(p) for p in re.findall(r"<p>(.*?)</p>", body, re.S) if len(clean(p).split()) > 3]
    credit = clean(re.sub(r"Usage of ESO images.*", "", clean(page[stop:stop + 800].split(">", 1)[-1]),
                          flags=re.S))
    kind = " ".join(clean(t) for t in re.findall(r"Type:</td>\s*<td[^>]*>(.*?)</td>", page, re.S))
    return (paragraphs[0] if paragraphs else "", credit, kind)


def build_eso(limit):
    """The ESO pack: pictures from ESO's Chilean observatory categories whose type is documentary (ESO_DOCUMENTARY),
    the first paragraph of ESO's caption (at most about 70 words) as the answer and the category's place."""
    s, items, seen = session(), [], set()
    per_category = int(limit * 1.4 / len(ESO_CATEGORIES)) + 3
    for category, place in ESO_CATEGORIES.items():
        listed = []
        for page in range(1, 40):
            try:
                text = s.get(f"{ESO}archive/category/{category}/list/{page}/", timeout=60).text
            except Exception:  # noqa: BLE001 - stop this category
                break
            found = re.findall(r"id: '([\w-]+)',\s*title: '((?:[^'\\]|\\.)*)'", text)
            listed += [i for i, _ in found if i not in seen]
            if not found or len(listed) >= per_category * 6:
                break
            time.sleep(0.5)
        pass_random(74).shuffle(listed)
        found = 0
        for image_id in listed:
            if found >= per_category:
                break
            time.sleep(0.5)
            info = eso_page(s, image_id)
            if not info or not ESO_DOCUMENTARY.search(info[2]) or ESO_NOT_A_PHOTO.search(info[0]):
                continue
            answer = tidy(capped_words(info[0], 70))
            credit = f"{info[1] or 'ESO'}, CC BY 4.0, {ESO}{image_id}/"
            if not usable(answer):
                if not NOT_SHOWN.search(answer) and needs_description(
                        f"eso-{image_id}.jpg", f"https://cdn.eso.org/images/large/{image_id}.jpg", credit, "CC BY 4.0",
                        text=answer, place=place, page_url=f"{ESO}{image_id}/",
                        reason="its caption is under six words", extra={"type": info[2]}):
                    seen.add(image_id)
                continue
            seen.add(image_id)
            items.append((f"eso-{image_id}.jpg", f"https://cdn.eso.org/images/large/{image_id}.jpg",
                          picture_rows(answer, credit, place)))
            found += 1
        say(f"  ESO {category}: {found} usable pictures")
    return finish("eso", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- US Geological Survey

USGS = "https://www.usgs.gov"
USGS_GALLERY = USGS + "/products/multimedia-gallery/images"
USGS_NOT_A_PHOTO = re.compile(r"\b(map|maps|chart|graph|graphic|diagram|figure|logo|organizational|poster|"
                              r"infographic|illustration|plot|table|screenshot|cover|flyer|schematic|model "
                              r"output|cross[- ]section|photomicrographs?|micrographs?|necropsy|histolog\w*|stain|"
                              r"lesions?|tissue|organs?|microscop\w*|carcass\w*|found dead)\b", re.I)


def usgs_page(s, path):
    """(title, caption, picture address) of a USGS image page whose page says Public Domain, or None."""
    try:
        page = s.get(USGS + path, timeout=60).text
    except Exception:  # noqa: BLE001 - left out
        return None
    if "Public Domain" not in page:
        return None
    meta = dict(re.findall(r'<meta (?:property|name)="(og:[a-z:]+)" content="([^"]*)"', page))
    pictures = re.findall(r'(?:src|href)="(https://[^"]+/s3fs-public/styles/full_width/public/thumbnails/image/[^"]+)"',
                          page)
    if not pictures:
        return None
    return clean(meta.get("og:title")), clean(meta.get("og:description")), pictures[0].replace("&amp;", "&")


def build_usgs(limit):
    """The USGS pack: image pages from random pages of the multimedia gallery (about 1,000 pages of 20), the
    caption (its first sentences, at most about 60 words) as the answer. Maps, charts, diagrams and wildlife-health
    laboratory pictures (necropsies, micrographs) are left out."""
    s, items = session(), []
    try:
        first = s.get(USGS_GALLERY, timeout=60).text
        last = max([int(n) for n in re.findall(r"[?&]page=(\d+)", first)] + [1])
    except Exception:  # noqa: BLE001 - nothing to read
        return []
    pages = list(range(0, last + 1))
    pass_random(75).shuffle(pages)
    for page in pages:
        if len(items) >= limit * 1.3 or listing_out_of_time():
            break
        time.sleep(1)
        try:
            text = s.get(USGS_GALLERY, params={"page": page}, timeout=60).text
        except Exception:  # noqa: BLE001 - next page
            continue
        for path in sorted(set(re.findall(r'href="(/media/images/[\w-]+)"', text))):
            if USGS_NOT_A_PHOTO.search(path.replace("-", " ")):
                continue
            time.sleep(0.5)
            info = usgs_page(s, path)
            if not info or USGS_NOT_A_PHOTO.search(info[0]) or USGS_NOT_A_PHOTO.search(info[1]):
                continue
            answer = tidy(capped_words(info[1], 60))
            credit = f"{info[0]}, U.S. Geological Survey, public domain, {USGS}{path}"
            if not usable(answer):
                if not NOT_SHOWN.search(answer):
                    needs_description(f"usgs-{path.rsplit('/', 1)[-1][:80]}.jpg", info[2], credit, "public domain",
                                      text=answer, title=info[0], page_url=USGS + path,
                                      reason="its caption is under six words")
                continue
            items.append((f"usgs-{path.rsplit('/', 1)[-1][:80]}.jpg", info[2], picture_rows(answer, credit)))
    say(f"USGS: {len(items)} usable photos")
    return finish("usgs", items, limit, workers=4, pause=0.3)


# ----------------------------------------------------------------- Wikimedia Commons Valued images

VALUED = "Category:Valued images sorted by promotion date"


def commons_get(s, params, tries=8):
    """A Commons API answer, waiting politely when the server asks to slow down (maxlag or 429), each request at
    least build_packs.COMMONS_PAUSE seconds after this build's last Commons request (build_packs.commons_pace)."""
    wait = 5
    for _ in range(tries):
        try:
            build_packs.commons_pace()
            r = s.get(COMMONS_API, params=dict(params, format="json", maxlag=5), timeout=60)
            if r.status_code == 200:
                data = r.json()
                if (data.get("error") or {}).get("code") != "maxlag":
                    return data
            after = r.headers.get("Retry-After", "")
            time.sleep(min(int(after) if after.isdigit() else wait, 120))
        except Exception:  # noqa: BLE001 - wait and try again
            time.sleep(wait)
        wait = min(wait * 2, 120)
    return {}


def build_commons_valued(limit):
    """The Commons Valued images pack: files of the category (about 56,000, read 50 at a time) with an English
    caption of 6 words or more whose licence is CC0, public domain or CC BY (never SA, NC or ND), the camera's
    coordinates as the place. Only about one file in twelve has such a caption."""
    s, items, seen = session(), [], set()
    params = {"action": "query", "generator": "categorymembers", "gcmtitle": VALUED, "gcmtype": "file",
              "gcmlimit": 50, "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": LONG_SIDE,
              "iiextmetadatafilter": "LicenseShortName|Artist|GPSLatitude|GPSLongitude"}
    while len(items) < limit * 1.3:
        data = commons_get(s, params)
        pages = [p for p in ((data.get("query") or {}).get("pages") or {}).values() if p.get("pageid")]
        if not pages:
            break
        entities = commons_get(s, {"action": "wbgetentities", "ids": "|".join(f"M{p['pageid']}" for p in pages),
                                   "props": "labels", "languages": "en"}).get("entities", {})
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            caption = tidy((((entities.get(f"M{p['pageid']}") or {}).get("labels") or {}).get("en") or {})
                           .get("value"))
            if p["pageid"] in seen or re.search(r"\b(SA|NC|ND)\b", licence.upper()) \
                    or not COMMONS_FREE.match(licence) or info.get("mime") not in ("image/jpeg", "image/png") \
                    or not info.get("thumburl"):
                continue
            seen.add(p["pageid"])
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            credit = f"{p['title']} by {artist}, {licence}, {page}"
            place = country_at(clean((meta.get("GPSLatitude") or {}).get("value")),
                               clean((meta.get("GPSLongitude") or {}).get("value")))
            if not usable(caption):             # free, a photo, no English caption of six words: set aside
                if not NOT_SHOWN.search(caption):
                    needs_description(f"commons-valued-{p['pageid']}.jpg", info["thumburl"], credit, licence,
                                      text=caption, title=p["title"], place=place, page_url=page,
                                      reason="no English caption of six words or more")
                continue
            items.append((f"commons-valued-{p['pageid']}.jpg", info["thumburl"], picture_rows(caption, credit, place)))
        if "continue" not in data:
            break
        params.update(data["continue"])
        time.sleep(1)
    say(f"Commons Valued images: {len(items)} captioned free files")
    return finish("commons_valued", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- the packs

LOC_TERMS = "https://www.loc.gov/legal/ (Prints and Photographs Division rights statements)"

DOCUMENTARY_PACKS = {
    "loc_highsmith": (build_loc_highsmith, "Carol M. Highsmith Archive, Library of Congress, Prints and Photographs "
                                           "Division, https://www.loc.gov/collections/carol-m-highsmith/ : 'No known "
                                           "restrictions on publication' (Highsmith gave the rights to the public). "
                                           f"Titles from the Library's records. {LOC_TERMS}"),
    "loc_fsa": (build_loc_fsa, "U.S. Farm Security Administration/Office of War Information photographs, 1935-1945, "
                               "Library of Congress, Prints and Photographs Division, "
                               "https://www.loc.gov/pictures/collection/fsa/ : US government work, 'No known "
                               f"restrictions'. Captions from the agency's records. {LOC_TERMS}"),
    "loc_world": (build_loc_world, "Photochrom Prints and the G. Eric and Edith Matson Photograph Collection, Library "
                                   "of Congress, Prints and Photographs Division, https://www.loc.gov/pictures/ : 'No "
                                   "known restrictions on publication'. Titles from the Library's records. "
                                   + LOC_TERMS),
    "npgallery": (build_npgallery, "U.S. National Park Service, NPGallery, https://npgallery.nps.gov : photos marked "
                                   "'Public domain', each with the credit the park asks for, below. Alt text and "
                                   "descriptions by the parks."),
    "earth_observatory": (build_earth_observatory, "NASA Earth Observatory, Image of the Day, "
                                                   "https://science.nasa.gov/earth/earth-observatory/ : NASA images "
                                                   "and text are not under copyright "
                                                   "(https://www.nasa.gov/nasa-brand-center/images-and-media/); "
                                                   "pictures naming a commercial maker or a copyright are left out. "
                                                   "Alt text by NASA's writers."),
    "eso": (build_eso, "European Southern Observatory (ESO), https://www.eso.org/public/images/ : pictures and "
                       "captions CC BY 4.0 (https://www.eso.org/public/copyright/), each with its full credit line "
                       "below."),
    "usgs": (build_usgs, "U.S. Geological Survey multimedia gallery, https://www.usgs.gov/products/multimedia-gallery "
                         ": public domain (US government work; only pages saying 'Public Domain'), "
                         "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits"),
    "commons_valued": (build_commons_valued, "Wikimedia Commons Valued images, "
                                             "https://commons.wikimedia.org/wiki/Commons:Valued_images : captions CC0; "
                                             "pictures CC0, public domain or CC BY, each with its author below."),
}

# How many pictures a full build takes from each collection.
DOCUMENTARY_LIMITS = {
    "loc_highsmith": 6000,            # of about 70,000; titles of 6 words or more are most of them
    "loc_fsa": 6000,                  # of about 173,000; many short captions ("Kempton, West Virginia.") are left out
    "loc_world": 4000,                # Photochrom (7,500) and Matson (22,000, Bible-verse slides left out)
    "npgallery": 6000,                # of hundreds of thousands; those with alt text of 6 words or more
    "earth_observatory": 3000,        # of about 9,500 posts; those with real alt text (mostly 2020 onwards)
    "eso": 1200,                      # documentary pictures in the Chilean categories (about 7,000 pictures in all)
    "usgs": 4000,                     # of about 20,000 gallery pages
    "commons_valued": 2500,           # of about 56,000 Valued images; those with an English caption and a free licence
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one documentary pack builder.")
    parser.add_argument("key", choices=sorted(DOCUMENTARY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = DOCUMENTARY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
