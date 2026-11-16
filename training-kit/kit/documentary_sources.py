"""Documentary photo collections for the Picture Model Training Kit whose licence keeps them out of the open packs
("National Geographic and similar": nature, places, cultures and people around the world, with good captions).
The open ones (Library of Congress, National Park Service, NASA Earth Observatory, ESO, USGS and Commons Valued
images) are ready-made packs: packs/documentary_packs.py.

National Geographic itself is a commercial, copyrighted publisher with no open dataset or licence, so nothing of it
is used; nor are commercial picture agencies (Getty, AP, Reuters, BBC). Nothing here is scraped from them.

Nothing here is in a ready-made pack or re-shared by the kit's makers. Each collection is downloaded by the kit on the
user's own computer, straight from its makers, only when the user ticks the matching choice. Groups (Source.group,
as in sources.py and extra_sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with
                   them is CC BY-SA.
  "research"       research or personal terms, or terms that forbid passing the data on: personal use only
                   (--personal-research with --accept-research-terms).

The collections (DOCUMENTARY_SOURCES):
  share-alike
    commons_documentary_sa  Wikimedia Commons Featured pictures, Quality images and Valued images whose licence is
                            CC BY-SA or GFDL (the CC0, public domain and CC BY ones are in the open "commons" and
                            "commons_valued" packs), with the file's English caption or the start of its English
                            description.
  research
    unsplash_lite           Unsplash Lite Dataset: 25,000 photos (nature, places, people, cities) with the
                            photographer's own description and, where given, the city and country. Unsplash's
                            dataset terms allow training but forbid passing the data on, so personal use only. Its
                            AI-written descriptions ("ai_description") are never used.

Every picture gets "Describe this picture." with the caption, tidied and at least 6 words long; a picture whose record
gives the place also gets "Where was this photo taken?" ("It was taken in Paris, France."), and its rows carry
"place". Rows whose words name a child carry "child": True, so picture-making leaves them out; nothing sexual is
kept (extra_sources.NUDE).

Needing sign-up or a request (cannot be downloaded automatically; DOCUMENTARY_SIGN_UP has the links): Geograph
Britain and Ireland, Geograph Deutschland and Geograph Channel Islands (CC BY-SA; bulk image sets by request form or on
Kaggle), and the Flickr collections (US Forest Service, Bureau of Land Management, USDA, NOAA, Natural England, New
Zealand's Department of Conservation, Flickr Commons members such as the National Library of Ireland and the State
Library of New South Wales, and the Biodiversity Heritage Library), which need a free API key.

Looked at and not included: DOCUMENTARY_NOT_INCLUDED.

    python kit/documentary_sources.py unsplash_lite --data <empty folder> --cap 8     (a quick check)
"""

import csv
import io
import os
import random
import re
import time

import sources
from extra_sources import NUDE, commons_file_name, commons_get, commons_sa_entries, commons_session
from more_sources import fetch_shared, sentence
from personal_sources import CHILD_WORDS, first_sentences, remote_zip
from sources import NARRATE, Source, clean, fetch_pictures

ASK_WHERE = "Where was this photo taken?"
# Catalogue words and file notes that are not a description ("DSC_0123", "IMG 4567", "File:").
NOT_A_CAPTION = re.compile(r"^(file:|image:|dsc|img|p\d{6})|\b(DSC|IMG|DSCF|DSCN)[_ ]?\d+", re.I)


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def caption(text, words=6, most=70):
    """A caption as an answer: tidied, its first sentences (at most about most words), a capital first letter and a
    full stop; "" when it is shorter than words words, looks like a file name or says something sexual."""
    text = re.sub(r"\{\{\s*w\s*\|[^|}]*\|([^}]*)\}\}", r"\1", clean(text))   # {{w|Å, Moskenes|Å}} -> Å
    text = re.sub(r"\{\{\s*w\s*\|([^}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{[^}]*\}\}|[\[\]]", "", text)
    text = re.sub(r"\s*#\w+", "", text).strip(" .,")                  # hashtags ("#cherry #tree")
    text = first_sentences(text, most)
    if len(text.split()) < words or NOT_A_CAPTION.search(text) or NUDE.search(text):
        return ""
    return sentence(text)


def short_credit(credit):
    """A Commons credit ("File:... by <author>, <licence>, <page>") with a long author text (some authors write a
    paragraph of wishes there) cut to about 80 characters, and no e-mail addresses."""
    credit = re.sub(r"\S+@\S+\.\w+", "", credit)
    m = re.match(r"(.*?) by (.*), ([^,]+), (https://\S+)$", credit)
    if not m or len(m.group(2)) <= 80:
        return " ".join(credit.split())
    author = m.group(2)[:77].rsplit(" ", 1)[0] + "..."
    return " ".join(f"{m.group(1)} by {author}, {m.group(3)}, {m.group(4)}".split())


def where_row(row, place):
    """The "Where was this photo taken?" twin of a row, for a picture whose record gives its place."""
    return dict(row, question=ASK_WHERE, answer=f"It was taken in {sources.place_words(place)}.",
                **sources.place_fields({"place": place}))


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

COMMONS_DOCUMENTARY = ("Featured pictures on Wikimedia Commons", "Quality images",
                       "Valued images sorted by promotion date")


def commons_titles(s, category, most):
    """Up to most file titles of a Commons category, newest additions first, 500 a request."""
    titles, params = [], {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                          "cmtype": "file", "cmlimit": 500, "cmsort": "timestamp", "cmdir": "desc"}
    while len(titles) < most:
        data = commons_get(s, params)
        titles += [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])]
        if "continue" not in data:
            break
        params.update(data["continue"])
        time.sleep(1)
    return titles[:most]


def prepare_commons_documentary_sa(source, data_dir, work, cap):
    """Wikimedia Commons Featured pictures, Quality images and Valued images under CC BY-SA or GFDL (never NC or
    ND): the file's English caption, or else the start of its English description, as "Describe this picture."
    About a third of each category is read (newest first), then a random pick."""
    s = commons_session()
    want = int((cap + source.test) * 1.2)
    titles = []
    for category in COMMONS_DOCUMENTARY:
        titles += commons_titles(s, category, want * 4 // len(COMMONS_DOCUMENTARY) + 200)
    titles = list(dict.fromkeys(titles))
    random.Random(401).shuffle(titles)
    items = []
    for start in range(0, len(titles), 500):
        for title, url, credit, text in commons_sa_entries(s, titles[start:start + 500]):
            answer = caption(text)
            if answer:
                items.append((commons_file_name("cdsa", title), url,
                              {"question": NARRATE, "answer": answer, "split": "", "credit": short_credit(credit),
                               "child": bool(CHILD_WORDS.search(answer))}))
        if len(items) >= want:
            break
    say(f"  Fetching {len(items[:want])} Commons Featured, Quality and Valued pictures (share-alike).")
    return fetch_pictures(items[:want], os.path.join(data_dir, source.key), workers=4, pause=0.2)


# ----------------------------------------------------------------- research: Unsplash Lite

UNSPLASH_LITE = "https://unsplash-datasets.s3.amazonaws.com/lite/latest/unsplash-research-dataset-lite-latest.zip"
UNSPLASH_TERMS = "https://github.com/unsplash/datasets/blob/master/TERMS.md"


def unsplash_place(r):
    """The place of an Unsplash photo from its city and country fields ("Paris, France"), or ""."""
    city, country = clean(r.get("photo_location_city")), clean(r.get("photo_location_country"))
    if not country:
        return ""
    return f"{city}, {country}" if city and city.lower() != country.lower() else country


def prepare_unsplash_lite(source, data_dir, work, cap):
    """Unsplash Lite Dataset (Unsplash's dataset terms; personal use here): its photos.tsv000 (about 4 MB inside a
    320 MB zip, read piece by piece without downloading the rest), the photographer's own description of 6 words or
    more as "Describe this picture.", and the city and country as "Where was this photo taken?". The photos come
    from Unsplash's picture server at 1,600 pixels."""
    archive = remote_zip(UNSPLASH_LITE)
    name = next(n for n in archive.namelist() if n.startswith("photos.tsv"))
    with archive.open(name) as f:
        table = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    found = []
    for r in table:
        answer = caption(r.get("photo_description"))
        url = clean(r.get("photo_image_url"))
        if not answer or not url.startswith("https://"):
            continue
        who = " ".join(p for p in (clean(r.get("photographer_first_name")), clean(r.get("photographer_last_name")))
                       if p) or clean(r.get("photographer_username")) or "an Unsplash photographer"
        credit = f"Photo by {who} on Unsplash ({clean(r.get('photo_url'))}), Unsplash Lite Dataset, {UNSPLASH_TERMS}"
        row = {"question": NARRATE, "answer": answer, "split": "", "credit": credit,
               "child": bool(CHILD_WORDS.search(answer))}
        photo_id = re.sub(r"[^\w-]", "_", r.get("photo_id") or str(len(found)))
        found.append((f"unsplash-{photo_id}.jpg", f"{url}?w=1600&q=85&fm=jpg", row, unsplash_place(r)))
    random.Random(403).shuffle(found)
    found = found[:int((cap + source.test) * 1.1)]
    items = []
    for file_name, url, row, place in found:
        if place:
            row = dict(row, **sources.place_fields({"place": place}))
        items.append((file_name, url, row))
        if place:
            items.append((file_name, url, where_row(row, place)))
    say(f"  Fetching {len(found)} Unsplash Lite photos ({sum(1 for f in found if f[3])} with a place).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- needing sign-up, and not included

DOCUMENTARY_SIGN_UP = {
    "Geograph Britain and Ireland (CC BY-SA 2.0; about 7 million geolocated photos with titles and descriptions)":
        "https://data.geograph.org.uk/datasets.html : the project asks that its live site and API are not used for "
        "bulk or training downloads. The metadata (titles, descriptions, places) is in its CC BY-SA dumps at "
        "https://data.geograph.org.uk/dumps/ ; the pictures come as prepared datasets by its request form or from "
        "its Kaggle datasets (a Kaggle account is needed).",
    "Geograph Deutschland and Geograph Channel Islands (CC BY-SA)":
        "https://geo.hlipp.de and https://www.geograph.org.gg/dumps/ : the same project rules; ask the projects.",
    "Flickr collections: US Forest Service, Bureau of Land Management, USDA, NOAA Photo Library, Natural England, "
    "New Zealand Department of Conservation (mostly public domain or CC BY), Flickr Commons members such as the "
    "National Library of Ireland and the State Library of New South Wales (no known copyright restrictions), and the "
    "Biodiversity Heritage Library":
        "https://www.flickr.com/services/api/misc.api_keys.html : a free Flickr API key is needed to list and "
        "download them (BHL's own API, https://www.biodiversitylibrary.org/docs/api3.html , needs a key too). Check "
        "each photo's licence on its page.",
}

DOCUMENTARY_NOT_INCLUDED = {
    "National Geographic, Getty Images, AP, Reuters, BBC": "commercial and copyrighted, with no open licence or "
                                                           "dataset; not scraped.",
    "NOAA Photo Library": "public domain, but photolib.noaa.gov forwards to www.noaa.gov/digital-library, which "
                          "refused the machine these entries were made on (403); its Flickr copy needs a key.",
    "USFWS National Digital Library": "public domain, but the old site forwards to fws.gov/search/images, whose "
                                      "search service is not public.",
    "European Space Agency (CC BY-SA 3.0 IGO)": "its multimedia gallery forwarded every request to the home page, so "
                                                "no listing of pictures could be read.",
    "Australian Antarctic Division image library": "images.aad.gov.au did not answer.",
    "Parks Canada": "its photos are Crown copyright, with no open licence.",
}


# ----------------------------------------------------------------- the table

DOCUMENTARY_SOURCES = [
    Source("commons_documentary_sa", "Wikimedia Commons Featured, Quality and Valued pictures with captions "
                                     "(share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page); captions CC0",
           "Wikimedia Commons contributors, Featured pictures, Quality images and Valued images, each file under "
           "CC BY-SA or GFDL with its author named, https://commons.wikimedia.org/wiki/Commons:Featured_pictures",
           "share-alike", 2500, 20, prepare_commons_documentary_sa, "about 1 GB of pictures"),
    Source("unsplash_lite", "Unsplash Lite: nature, places and people described by their photographers "
                            "(personal use)",
           "Unsplash Dataset Terms (github.com/unsplash/datasets/blob/master/TERMS.md): training allowed, no "
           "redistribution",
           "Unsplash Lite Dataset, Unsplash Inc., https://unsplash.com/data ; photos by Unsplash photographers, "
           "credited per photo", "research", 3000, 20, prepare_unsplash_lite,
           "about 4 MB of data and 1.5 GB of photos",
           terms=UNSPLASH_TERMS,
           terms_summary="Unsplash's dataset terms: you may download the Lite photos and use them to train models "
                         "for your own internal use; you must not publish, share or redistribute any of the data. "
                         "Personal, non-commercial use only."),
]

# The collections a picture-making model may learn from: none of these (both show people, including children).
DOCUMENTARY_PICTURE_MAKING_OK = set()


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try one documentary collection.")
    parser.add_argument("key", choices=[s.key for s in DOCUMENTARY_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in DOCUMENTARY_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="documentary-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
