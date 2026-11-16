"""Pack builders for pictures of the human body, used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"} (a second row about the same picture has no bytes and names the picture in "file").

Why: blind users meet nude figures in art and bodies in medical pictures, and a describing model should say what
is there plainly and factually, as a museum's alt text does ("a marble statue of a standing nude man, his weight on
one leg"), instead of refusing or being vague.

Hard rules kept by every builder here:
  - No sexual content and no sexual acts: records whose title, subject tags or description mention erotic art,
    sexual acts, or stories told for their sexual content (SEXUAL below) are left out.
  - No minors: records whose title, tags or description mention children, babies, putti, cupids, youths, the
    Madonna and Child and the like, in English, French, Italian, Spanish, German, Dutch, Latin or Japanese (MINOR
    below), are left out. The filter is deliberately wide: when a word could mean a young person, the record goes.
  - Licence: CC0, public domain, or CC BY with the author credited; never share-alike, NC or ND.
  - Answers are plain and factual: the medium, the pose and what is shown, from the museum's or book's own text.

The packs (BODY_PACKS):
  art_nudes  Non-sexual nudes in art from five open-access museums: the Metropolitan Museum of Art ("Female Nudes"
             and "Male Nudes" subject tags, public-domain works), the Art Institute of Chicago (public-domain works
             with the subject "nudes" or "nude" in the title; its alt text written for screen readers), the
             Cleveland Museum of Art (CC0 works with "nude" or "naked" in the title or description), the National
             Gallery of Art, Washington (open-access works with a "nude" keyword; its alt text) and the Smithsonian
             American Art Museum and Hirshhorn (CC0 pictures with the topic "nude"). Asked "Describe this picture."
             and "Is there nudity in this picture?".
  anatomy    Anatomy figures: OpenStax "Anatomy and Physiology" (first edition, CC BY 4.0; the second edition is
             now CC BY-NC-SA and is not used), only figures OpenStax drew itself or took from US government
             sources, with their alt text and caption; and the public-domain plates of Gray's Anatomy (1918) on
             Wikimedia Commons, with their caption.

    python packs/body_packs.py art_nudes --limit 8      (prints a few rows: a quick check of one builder)

A folder named by the environment variable BODY_PACKS_CACHE, when set, keeps the National Gallery of Art's large
open-data tables (about 200 MB) between test runs; without it they are downloaded into a temporary folder.
"""

import concurrent.futures
import csv
import io
import json
import os
import random
import re
import sys
import tempfile
import time

from build_packs import session, clean, smaller, fetch_all, first_sentences, say, article, LONG_SIDE  # noqa: F401
from food_packs import commons_get, commons_members, commons_entries, with_twins, sentence

DESCRIBE = "Describe this picture."
IS_NUDE = "Is there nudity in this picture?"
NUDE_YES = "Yes: it shows a nude figure, in a non-sexual artistic way."
FIGURE_SHOWS = "What does this figure show?"


# ----------------------------------------------------------------- the safety filters

# Words that may name or describe a young person, in the languages the collections use. Wide on purpose: a record
# that mentions any of them is left out, even when the word is used about an adult ("young woman", "student").
MINOR = re.compile(
    r"\b(child\w*|kids?|boy\w*|girl\w*|infan\w*|bab(y|ies|es?)|toddler\w*|newborn\w*|neonat\w*|teen\w*|juvenile\w*|"
    r"youth\w*|young\w*|adolesc\w*|minors?|lads?|maiden\w*|schoolboy\w*|schoolgirl\w*|school\w*|students?|"
    r"sons?|daughters?|mothers?|motherhood|maternity|famil(y|ies)|nativity|innocents|madonna\w*|virgin\w*|"
    r"holy family|christ child|bambino|bambin\w*|put(to|ti|ten)|amor\w*|amoretti|amorini|cupids?|cherub\w*|eros|"
    r"angel\w*|genius|genii|psyche|ganymede|narcissus|icarus|hyacinth\w*|kouros|kouroi|kore|korai|ephebe\w*|"
    r"david|romulus|remus|charity|caritas|fetus|fetal|foetus|foetal|embryo\w*|"
    r"enfant\w*|filles?|fillettes?|gar[cç]on\w*|petite?s?|jeune\w*|jeunesse|fanciull\w*|ragazz\w*|bimb\w*|"
    r"ni[nñ][oa]s?|muchach\w*|chic[oa]s?|kinder\w*|kindje\w*|kindheit|knabe\w*|m[aä]dchen|j[uü]ngling\w*|"
    r"junge\w*|jongen\w*|meisje\w*|puer\w*|puella\w*|infans)\b|子供|子ども|こども|童|少年|少女|乳児|幼|赤ん坊|娘|息子",
    re.I)

# Words that mark sexual content, sexual acts, or stories whose pictures are about sex or sexual violence. Also wide.
SEXUAL = re.compile(
    r"\b(erotic\w*|shunga|makura|porn\w*|sex\w*|intercourse|coitus|copulat\w*|phall\w*|ithyphall\w*|priap\w*|"
    r"penis|vulva|vagina\w*|genital\w*|erection\w*|erectile|arous\w*|orgasm\w*|masturbat\w*|satyrs?|satyresses?|"
    r"nymphs?|brothel\w*|bordello|prostitut\w*|courtesans?|harem\w*|concubine\w*|odalisques?|rap(e|es|ed|ing)|ravish\w*|"
    r"abduct\w*|seduc\w*|lust\w*|lovers?|love-?making|kiss\w*|embrac\w*|caress\w*|bacchanal\w*|orgy|orgies|"
    r"voyeur\w*|leda|dana[eë]|antiope|susanna|bathsheba|jupiter|zeus|pasiphae|salmacis|hermaphrodit\w*|"
    r"bondage|fetish\w*|pin-?ups?|burlesque|striptease|stripper\w*)\b|春画|枕絵|艶|秘画", re.I)

# What each builder left out and why, for the quick check (source, title, the word that excluded it).
EXCLUDED = []


def left_out(source, title, *texts):
    """True when a record must be left out because its title, tags or text mention a young person or sexual
    content; the reason is noted in EXCLUDED."""
    text = " ".join(clean(t) for t in (title, *texts) if t)
    for kind, pattern in (("minor", MINOR), ("sexual", SEXUAL)):
        found = pattern.search(text)
        if found:
            EXCLUDED.append((source, clean(title)[:90], f"{kind}: {found.group(0)}"))
            return True
    return False


# ----------------------------------------------------------------- shared helpers

NUDITY_WORDS = re.compile(r"\b(nude\w*|naked|nudity|unclothed|undressed)\b", re.I)


def nudity_kind(*texts):
    """("female", "male", both or neither) from a record's subject tags: which nudity the museum names."""
    text = " ".join(clean(t).lower() for t in texts if t)
    female = bool(re.search(r"female nude|nude female|female\\nude|female\s*-\s*nude|nude wom[ae]n|female figure|"
                            r"\bwom[ae]n\b|\bfemale\b", text))
    male = bool(re.search(r"male nude|nude male|(?<!fe)male\\nude|(?<!fe)male\s*-\s*nude|nude m[ae]n|male figure|"
                          r"\bm[ae]n\b|(?<!fe)\bmale\b", text))
    return female, male


def nudity_sentence(female, male):
    """A plain sentence about the nudity the record names."""
    if female and male:
        return "The work includes male and female nudity."
    if female:
        return "The work includes female nudity."
    if male:
        return "The work includes male nudity."
    return "The work includes nudity."


def lead(title, kind="", artist="", date="", medium=""):
    """The opening sentence of an answer from the record: "Seated Male Nude: a drawing by Baccio Bandinelli,
    c. 1516-20, in red chalk." (only what the record gives)."""
    kind, medium = clean(kind).lower(), clean(medium)
    if not kind and medium and len(medium.split()) <= 2:     # "drawing", "oil on canvas" said once, as the kind
        kind, medium = medium.lower(), ""
    out = clean(title).rstrip(".")
    bits = []
    if kind:
        bits.append(f"{article(kind)} {kind}" + (f" by {clean(artist)}" if artist else ""))
    elif artist:
        bits.append(f"by {clean(artist)}")
    if date:
        bits.append(clean(date))
    if medium and len(medium) <= 80 and medium.lower() != kind:
        bits.append("in " + medium[0].lower() + medium[1:])
    if bits:
        out += ": " + ", ".join(bits)
    return sentence(out)


def art_rows(answer_text, credit, title, kind, artist, date, medium, female, male):
    """The two rows of an art_nudes picture: "Describe this picture." (the record's opening sentence, the museum's
    own description, and a sentence naming the nudity when the description does not) and "Is there nudity ...?"."""
    answer = lead(title, kind, artist, date, medium)
    text = first_sentences(answer_text, 110) if answer_text else ""
    if text:
        answer += " " + sentence(text)
    if not NUDITY_WORDS.search(answer):
        answer += " " + nudity_sentence(female, male)
    return [{"question": DESCRIBE, "answer": answer, "credit": credit},
            {"question": IS_NUDE, "answer": NUDE_YES, "credit": credit}]


def safe_name(text):
    """A file-name-safe version of a record identifier."""
    return re.sub(r"[^\w.-]+", "_", str(text))[:80]


def on_white(data):
    """JPEG bytes like build_packs.smaller(), but with a transparent picture (a PNG diagram) put on white paper
    first, so its black labels do not vanish on a black background; None when unreadable or tiny."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            paper = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(paper, img)
        img = img.convert("RGB")
    except Exception:  # noqa: BLE001 - left out
        return None
    if min(img.size) < 64:
        return None
    img.thumbnail((LONG_SIDE, LONG_SIDE))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=90)
    return out.getvalue()


def fetch_diagrams(items, workers=4, pause=0.2):
    """build_packs.fetch_all() for diagrams: items are (name, address, rows); returns [(name, JPEG, rows)], each
    picture put on white (see on_white)."""
    s = session()

    def one(item):
        """One picture, or None."""
        name, url, rows = item
        time.sleep(pause)
        for _ in range(3):
            try:
                r = s.get(url, timeout=60)
                if r.status_code == 200:
                    data = on_white(r.content)
                    return (name, data, rows) if data else None
                if r.status_code in (403, 404, 410):
                    return None
                time.sleep(int(r.headers.get("Retry-After", "5")) if r.status_code == 429 else 2)
            except Exception:  # noqa: BLE001 - tried again, then left out
                time.sleep(2)
        return None

    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        return [r for r in pool.map(one, items) if r]


# ----------------------------------------------------------------- The Metropolitan Museum of Art

MET = "https://collectionapi.metmuseum.org/public/collection/v1"
MET_TAGS = ("Female Nudes", "Male Nudes")      # the Met's subject tags (Getty AAT) for nudes


def met_items(want):
    """(name, picture address, rows) for public-domain Met works tagged "Female Nudes" or "Male Nudes" (the
    v1.1 search pages through the tag's objects; each object's record gives the tags, title and picture)."""
    s, ids = session(), []
    for tag in MET_TAGS:
        offset = 0
        while True:
            try:
                page = s.get(MET + ".1/search", params={"q": tag, "tags": "true", "hasImages": "true",
                                                         "offset": offset, "limit": 500}, timeout=60).json()
            except Exception:  # noqa: BLE001 - the next tag
                break
            found = page.get("objectIDs") or []
            ids += found
            offset += len(found)
            if not found or offset >= (page.get("total") or 0):
                break
            time.sleep(0.5)
    ids = list(dict.fromkeys(ids))
    say(f"Met: {len(ids)} works tagged as nudes")
    random.Random(51).shuffle(ids)

    def one(object_id):
        """One object's record, or None."""
        time.sleep(0.1)
        try:
            return s.get(f"{MET}/objects/{object_id}", timeout=60).json()
        except Exception:  # noqa: BLE001 - left out
            return None

    items = []
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for start in range(0, len(ids), 200):
            for o in pool.map(one, ids[start:start + 200]):
                if not o or not o.get("isPublicDomain") or not o.get("primaryImageSmall"):
                    continue
                tags = [t.get("term", "") for t in o.get("tags") or []]
                title = clean(o.get("title"))
                if not title or left_out("Met", title, " ".join(tags), o.get("objectName"), o.get("medium")):
                    continue
                female, male = "Female Nudes" in tags, "Male Nudes" in tags
                others = [t.lower() for t in tags if t not in MET_TAGS and len(t) < 30][:5]
                shown = ("The museum lists these subjects too: " + ", ".join(others) + ".") if others else ""
                artist = clean(o.get("artistDisplayName"))
                date = clean(o.get("objectDate"))
                credit = f"The Metropolitan Museum of Art, public domain (CC0): {title}" + \
                    (f", {artist}" if artist else "") + f", {o.get('objectURL', '')}"
                rows = art_rows(shown, credit, title, o.get("objectName"), artist, date, o.get("medium"),
                                female, male)
                items.append((f"met-{o['objectID']}.jpg", o["primaryImageSmall"], rows))
            if len(items) >= want:
                break
    say(f"Met: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- Art Institute of Chicago

AIC = "https://api.artic.edu/api/v1/artworks/search"
AIC_FIELDS = ["id", "title", "subject_titles", "term_titles", "description", "short_description", "thumbnail",
              "image_id", "artist_display", "date_display", "medium_display", "classification_title"]


def aic_items(want):
    """(name, picture address, rows) for public-domain Art Institute works with the subject "nudes" or "nude" or
    "naked" in the title; the answer uses the museum's alt text (written for screen readers) or its short
    description."""
    s = session()
    s.headers["AIC-User-Agent"] = s.headers["User-Agent"]
    query = {"query": {"bool": {"must": [
        {"term": {"is_public_domain": True}}, {"exists": {"field": "image_id"}},
        {"bool": {"should": [{"match": {"subject_titles": "nudes"}}, {"match": {"term_titles": "nudes"}},
                             {"match": {"title": "nude"}}, {"match": {"title": "naked"}}]}}]}},
        "fields": AIC_FIELDS}
    items, page = [], 1
    while len(items) < want:
        try:
            data = s.post(AIC, params={"limit": 100, "page": page}, json=query, timeout=60).json()
        except Exception:  # noqa: BLE001 - stop here
            break
        records = data.get("data") or []
        for a in records:
            title = clean(a.get("title"))
            terms = " ".join((a.get("subject_titles") or []) + (a.get("term_titles") or []))
            alt = clean((a.get("thumbnail") or {}).get("alt_text"))
            text = alt if len(alt.split()) >= 8 else clean(a.get("short_description"))
            if not title or not a.get("image_id") or not (NUDITY_WORDS.search(f"{title} {terms} {alt}")):
                continue
            if left_out("AIC", title, terms, text, a.get("description")):
                continue
            female, male = nudity_kind(terms, title, text)
            artist = clean(a.get("artist_display")).split("\n")[0]
            credit = f"Art Institute of Chicago, CC0 (public domain): {title}, {artist}, " \
                     f"https://www.artic.edu/artworks/{a['id']}"
            rows = art_rows(text, credit, title, a.get("classification_title"), re.sub(r"\s*\(.*", "", artist),
                            a.get("date_display"), a.get("medium_display"), female, male)
            url = f"https://www.artic.edu/iiif/2/{a['image_id']}/full/1686,/0/default.jpg"
            items.append((f"aic-{a['id']}.jpg", url, rows))
        if page >= ((data.get("pagination") or {}).get("total_pages") or 0) or not records:
            break
        page += 1
        time.sleep(1)
    say(f"Art Institute of Chicago: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- Cleveland Museum of Art

CMA = "https://openaccess-api.clevelandart.org/api/artworks/"


def cma_items(want):
    """(name, picture address, rows) for CC0 Cleveland works whose title or description says nude or naked; the
    answer uses the museum's description (its "digital description" or alt text when there is one)."""
    s, items, seen = session(), [], set()
    for word in ("nude", "naked"):
        skip = 0
        while len(items) < want:
            try:
                data = s.get(CMA, params={"q": word, "cc0": 1, "has_image": 1, "limit": 200, "skip": skip},
                             timeout=60).json()
            except Exception:  # noqa: BLE001 - the next word
                break
            records = data.get("data") or []
            for a in records:
                if a["id"] in seen or a.get("share_license_status") != "CC0":
                    continue
                seen.add(a["id"])
                title = clean(a.get("title"))
                text = next((clean(a.get(k)) for k in ("alt_text", "digital_description", "description",
                                                       "wall_description") if len(clean(a.get(k)).split()) >= 8), "")
                if not title or not NUDITY_WORDS.search(f"{title} {text}"):
                    continue
                if left_out("Cleveland", title, text, a.get("type"), a.get("technique")):
                    continue
                images = a.get("images") or {}
                url = (images.get("print") or images.get("web") or {}).get("url")
                if not url:
                    continue
                creator = (a.get("creators") or [{}])[0].get("description") or ""
                female, male = nudity_kind(title, text)
                credit = f"Cleveland Museum of Art, CC0: {title}, {creator}, {a.get('url', '')}"
                rows = art_rows(text, credit, title, a.get("type"), re.sub(r"\s*\(.*", "", creator),
                                a.get("creation_date"), a.get("technique"), female, male)
                items.append((f"cma-{a['id']}.jpg", url, rows))
            skip += len(records)
            if not records or skip >= ((data.get("info") or {}).get("total") or 0):
                break
            time.sleep(0.5)
    say(f"Cleveland Museum of Art: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- National Gallery of Art, Washington

NGA_DATA = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data/"
NGA_FILES = ("objects_terms.csv", "published_images.csv", "objects.csv")


def nga_tables(folder):
    """The paths of the National Gallery's open-data tables, downloaded into folder unless already there."""
    s, paths = session(), []
    for name in NGA_FILES:
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            say(f"National Gallery of Art: downloading {name}")
            with s.get(NGA_DATA + name, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(path + ".part", "wb") as f:
                    for block in r.iter_content(1 << 20):
                        f.write(block)
            os.replace(path + ".part", path)
        paths.append(path)
    return paths


def nga_items(want):
    """(name, picture address, rows) for open-access National Gallery works with a "nude" keyword (Nude, Female
    nude, Male nude, Standing female nude ...); the answer uses the gallery's alt text ("assistive text")."""
    csv.field_size_limit(1 << 30)
    cache = os.environ.get("BODY_PACKS_CACHE")
    with tempfile.TemporaryDirectory() as temp:
        folder = cache or temp
        os.makedirs(folder, exist_ok=True)
        terms_path, images_path, objects_path = nga_tables(folder)
        terms = {}
        for r in csv.DictReader(open(terms_path, encoding="utf-8")):
            terms.setdefault(r["objectid"], []).append(r["term"])
        nude = {k for k, v in terms.items() if any("nude" in t.lower() for t in v)}
        images = {}
        for r in csv.DictReader(open(images_path, encoding="utf-8")):
            if r["depictstmsobjectid"] in nude and r["viewtype"] == "primary" and r["openaccess"] == "1":
                images[r["depictstmsobjectid"]] = r
        objects = {r["objectid"]: r for r in csv.DictReader(open(objects_path, encoding="utf-8"))
                   if r["objectid"] in images}
    say(f"National Gallery of Art: {len(nude)} works with a nude keyword, {len(images)} with an open-access picture")
    keys = sorted(images)
    random.Random(52).shuffle(keys)
    items = []
    for k in keys:
        o, image = objects.get(k), images[k]
        if not o:
            continue
        title, alt = clean(o["title"]), clean(image["assistivetext"])
        words = " ".join(terms[k])
        if left_out("NGA", title, words, alt):
            continue
        female, male = nudity_kind(words)
        credit = f"National Gallery of Art, Washington, CC0: {title}, {clean(o['attribution'])}, " \
                 f"https://www.nga.gov/collection/art-object-page.{k}.html"
        rows = art_rows(alt, credit, title, o["classification"], o["attribution"], o["displaydate"], o["medium"],
                        female, male)
        items.append((f"nga-{k}.jpg", f"{image['iiifurl']}/full/!{LONG_SIDE},{LONG_SIDE}/0/default.jpg", rows))
        if len(items) >= want:
            break
    say(f"National Gallery of Art: {len(items)} usable")
    return items


# ----------------------------------------------------------------- Smithsonian (American Art Museum, Hirshhorn)

SI_NUDE_UNITS = ("saam", "hmsg")


def si_items(want):
    """(name, picture address, rows) for Smithsonian American Art Museum and Hirshhorn records whose topics say
    nude (or "Nudity") and whose picture is CC0; the answer uses the accessibility text or gallery label when there
    is one (build_packs.si_row), otherwise the record's title, artist, date and medium."""
    from build_packs import si_keys, si_row, SI_BUCKET
    s, items = session(), []
    per_unit = want // len(SI_NUDE_UNITS) + 1
    for unit in SI_NUDE_UNITS:
        keys = si_keys(unit)
        random.Random(unit + "-nude").shuffle(keys)
        found = 0
        for key in keys:
            if found >= per_unit:
                break
            try:
                lines = s.get(f"{SI_BUCKET}/{key}", timeout=120).text.splitlines()
            except Exception:  # noqa: BLE001 - the next file
                continue
            for line in lines:
                if "nud" not in line.lower():
                    continue
                record = json.loads(line)
                content = record.get("content", {})
                freetext = content.get("freetext", {})
                topics = [t.get("content", "") for t in freetext.get("topic", [])] + \
                    list(content.get("indexedStructured", {}).get("topic", []))
                if not any(re.search(r"nud", t, re.I) for t in topics):
                    continue
                media = (content.get("descriptiveNonRepeating", {}).get("online_media") or {}).get("media", [])
                picture = next((m for m in media if (m.get("usage") or {}).get("access") == "CC0"
                                and m.get("type") == "Images" and m.get("content")), None)
                title = clean(record.get("title"))
                if not picture or not title:
                    continue
                got = si_row(record)
                text = got[1]["answer"] if got else ""
                if left_out("Smithsonian", title, " ".join(topics), text):
                    continue

                def field(name, label):
                    """The first value of a freetext field with this label."""
                    return next((clean(x.get("content")) for x in freetext.get(name, []) if x.get("label") == label),
                                "")
                artist = re.sub(r",\s*born.*", "", field("name", "Artist"))
                female, male = nudity_kind(" ".join(topics))
                credit = f"{record.get('unitCode', unit.upper())}, Smithsonian Institution, CC0: {title}" + \
                    (f", {artist}" if artist else "")
                rows = art_rows(text, credit, title, "", artist, field("date", "Date"),
                                field("physicalDescription", "Medium"), female, male)
                items.append((f"si-{safe_name(record.get('id', title))}.jpg", picture["content"] + "&max=2048", rows))
                found += 1
                if found >= per_unit:
                    break
            time.sleep(0.2)
        say(f"Smithsonian {unit}: {found} usable")
    return items[:want]


# ----------------------------------------------------------------- art_nudes

# Each museum's share of the pack (the National Gallery and the Met have the most tagged nudes).
ART_SHARES = (("nga", nga_items, 0.35), ("met", met_items, 0.35), ("si", si_items, 0.12),
              ("cma", cma_items, 0.09), ("aic", aic_items, 0.09))


def build_art_nudes(limit):
    """The art_nudes pack's pictures: [(name, JPEG, row)], two rows per picture ("Describe this picture." and
    "Is there nudity in this picture?"). Each museum gives its share of the limit (a museum with fewer gives what
    it has)."""
    items = []
    for key, collect, share in ART_SHARES:
        try:
            items += collect(max(2, round(limit * share * 1.2)))
        except Exception as error:  # noqa: BLE001 - one museum down does not stop the pack
            say(f"{key}: left out ({error})")
    random.Random(50).shuffle(items)
    fetched = fetch_all(items, workers=4, pause=0.2)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- OpenStax Anatomy and Physiology (1st edition)

OPENSTAX = "https://openstax.org/apps/archive/20260604.144757"
OPENSTAX_BOOK = "14fb4ad7-39a1-4eee-ab6e-3ef2482e3e22@ccce780"    # Anatomy and Physiology (2013), CC BY 4.0
# Credits that are free to copy: US government sources (public domain). A figure crediting anyone else (a
# photographer, a university, Wikimedia, Flickr, a ©) is left out, as its licence may not be CC BY.
OPENSTAX_FREE_CREDIT = re.compile(r"\b(NIH|National Institutes? of Health|NCI|National Cancer Institute|CDC|Centers "
                                  r"for Disease Control|NIAID|NHLBI|NIGMS|NASA|NOAA|USDA|FDA|U\.?S\.? Department|"
                                  r"public domain)\b", re.I)
OPENSTAX_NOT_FREE = re.compile(r"©|\(c\)|regents|universit|wikimedia|flickr|copyright|courtesy|by-sa|nc", re.I)


def openstax_credit_free(credit):
    """True when a figure has no third-party credit, or every part of it names a public-domain source."""
    if not credit:
        return True
    parts = [p for p in re.split(r";", credit) if p.strip()]
    return all(OPENSTAX_FREE_CREDIT.search(p) and not OPENSTAX_NOT_FREE.search(p) for p in parts)


def openstax_figures(page_html):
    """[(number, title, caption, credit, alt text, picture address)] for the one-picture figures of a page."""
    out = []
    for block in re.findall(r'<div class="os-figure">(.*?)</div>\s*</div>', page_html, re.S):
        sources = re.findall(r'<img[^>]*\ssrc="([^"]+)"', block)
        if len(sources) != 1:
            continue
        alt = re.search(r'<img[^>]*\salt="([^"]*)"', block)
        number = re.search(r'class="os-number">([^<]*)<', block)
        title = re.search(r'class="os-title"[^>]*>(.*?)</span>', block, re.S)
        caption = re.search(r'class="os-caption">(.*?)</span>\s*$', block, re.S)
        caption = clean(caption.group(1)) if caption else ""
        credit = ""
        cut = re.search(r"\(\s*(image\s+)?credits?\b", caption, re.I)
        if cut:
            caption, credit = caption[:cut.start()].strip(), caption[cut.start():].strip(" ()")
        url = OPENSTAX + "/resources/" + sources[0].rsplit("/", 1)[-1]
        out.append((clean(number.group(1)) if number else "", clean(title.group(1)) if title else "", caption,
                    credit, clean(alt.group(1)) if alt else "", url))
    return out


def openstax_items(want):
    """(name, picture address, rows) for OpenStax Anatomy and Physiology (1st edition) figures that OpenStax made
    or took from US government sources: "Describe this picture." answered with the figure's alt text (written for
    screen-reader users), and "What does this figure show?" with its title and caption."""
    s = session()
    book = s.get(f"{OPENSTAX}/contents/{OPENSTAX_BOOK}.json", timeout=60).json()
    if "by/4.0" not in ((book.get("license") or {}).get("url") or ""):
        raise RuntimeError("OpenStax Anatomy and Physiology is no longer listed as CC BY 4.0")

    def pages(tree):
        """The book's page ids, in order."""
        out = []
        for c in tree.get("contents", []):
            out += pages(c) if "contents" in c else [c["id"].rstrip("@")]
        return out

    items = []
    for page_id in pages(book["tree"]):
        try:
            page = s.get(f"{OPENSTAX}/contents/{OPENSTAX_BOOK}:{page_id}.json", timeout=60).json()
        except Exception:  # noqa: BLE001 - the next page
            continue
        for number, title, caption, credit, alt, url in openstax_figures(page.get("content", "")):
            if not openstax_credit_free(credit) or left_out("OpenStax", f"Figure {number} {title}", caption, alt):
                continue
            source = f"OpenStax, Anatomy and Physiology (2013), figure {number}, CC BY 4.0, " \
                     f"https://openstax.org/details/books/anatomy-and-physiology" + (f"; {credit}" if credit else "")
            rows = []
            if len(alt.split()) >= 8:
                rows.append({"question": DESCRIBE, "answer": sentence(alt), "credit": source})
            if len(caption.split()) >= 5:
                shows = sentence(f"{title}: {caption}" if title else caption)
                rows.append({"question": FIGURE_SHOWS if rows else DESCRIBE, "answer": shows, "credit": source})
            if rows:
                items.append((f"openstax-ap-{safe_name(number or url.rsplit('/', 1)[-1])}.jpg", url, rows))
        time.sleep(0.2)
    say(f"OpenStax Anatomy and Physiology: {len(items)} usable figures")
    random.Random(53).shuffle(items)
    return items[:want]


# ----------------------------------------------------------------- Gray's Anatomy plates (Wikimedia Commons)

GRAYS_CATEGORY = "Gray's Anatomy plates"


def grays_items(want):
    """(name, picture address, rows) for the plates of Gray's Anatomy (1918, public domain) on Wikimedia Commons
    (the category and its subcategories, two levels down), answered with the file's caption or the plate's
    description. Commons may ask this machine to slow down (429): commons_get waits and tries again."""
    s = session()
    titles, categories, done = [], [GRAYS_CATEGORY], set()
    for _ in range(3):
        deeper = []
        for category in categories:
            if category in done:
                continue
            done.add(category)
            titles += commons_members(s, category, "file")
            deeper += [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
        categories = deeper
    titles = list(dict.fromkeys(titles))
    say(f"Gray's Anatomy: {len(titles)} files")
    random.Random(54).shuffle(titles)
    items = []
    for title, url, credit, text in commons_entries(s, titles[:int(want * 1.5) + 10]):
        if not text or left_out("Gray's", title, text):
            continue
        rows = [{"question": DESCRIBE, "answer": text, "credit": credit + "; Henry Gray, Anatomy of the Human "
                                                                          "Body (1918), public domain"}]
        items.append((f"grays-{safe_name(title.split(':', 1)[-1].rsplit('.', 1)[0])}.jpg", url, rows))
        if len(items) >= want:
            break
    say(f"Gray's Anatomy: {len(items)} usable")
    return items


def build_anatomy(limit):
    """The anatomy pack's pictures: [(name, JPEG, row)]: OpenStax figures first (about two thirds), Gray's plates
    for the rest (Commons may be unreachable from some machines; then the pack has OpenStax only)."""
    items = openstax_items(int(limit * 0.7) + 2)
    try:
        items += grays_items(limit - min(len(items), int(limit * 0.7)) + 2)
    except Exception as error:  # noqa: BLE001 - Commons refused: OpenStax only
        say(f"Gray's Anatomy: left out ({error})")
    random.Random(55).shuffle(items)
    fetched = fetch_diagrams(items, workers=3, pause=0.3)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- the packs

BODY_PACKS = {
    "art_nudes": (build_art_nudes, "Non-sexual nudes in art, from open-access museum collections, each work "
                                   "credited below: The Metropolitan Museum of Art (public-domain works, CC0, "
                                   "https://www.metmuseum.org/about-the-met/policies-and-documents/open-access); "
                                   "Art Institute of Chicago (public-domain works and data CC0, "
                                   "https://www.artic.edu/open-access/open-access-images); Cleveland Museum of Art "
                                   "(CC0, https://www.clevelandart.org/open-access); National Gallery of Art, "
                                   "Washington (CC0, https://github.com/NationalGalleryOfArt/opendata); Smithsonian "
                                   "Institution Open Access (CC0, https://www.si.edu/openaccess). Records mentioning "
                                   "children or young people, or sexual content, were left out."),
    "anatomy": (build_anatomy, "OpenStax, Anatomy and Physiology (2013, first edition), Rice University, CC BY 4.0, "
                               "https://openstax.org/details/books/anatomy-and-physiology (download for free at "
                               "openstax.org); only figures without a third-party credit or credited to US "
                               "government sources. Henry Gray, Anatomy of the Human Body (1918), illustrations by "
                               "Henry Vandyke Carter and others, public domain, via Wikimedia Commons, each file "
                               "credited below."),
}

# How many pictures a full build takes from each collection (about what each offers after the licence and
# safety checks).
BODY_LIMITS = {
    "art_nudes": 4000,
    "anatomy": 1500,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows and a few records the safety filter left out (a
    quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one body pack builder.")
    parser.add_argument("key", choices=sorted(BODY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = BODY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    say(f"Left out by the safety filter: {len(EXCLUDED)}, for example:")
    for source, title, reason in random.Random(1).sample(EXCLUDED, min(15, len(EXCLUDED))):
        say(f"  {source}: {title}  ({reason})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
