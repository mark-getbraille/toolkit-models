"""More archive, museum and news-photo collections for the Picture Model Training Kit whose licence keeps them out of
the open packs. The open ones found in the same search (US National Archives, New York Public Library, Getty Museum,
Digital Commonwealth's unrestricted photos, Statens Museum for Kunst, Nationaal Archief, kremlin.ru and the Australian
War Memorial) are ready-made packs: packs/archive_packs.py.

Nothing here is in a ready-made pack or re-shared by the kit's makers. Each collection is downloaded by the kit on the
user's own computer, straight from its makers, only when the user ticks the matching choice. Groups (Source.group,
as in sources.py and extra_sources.py, and packs/SOURCE-RULES.md):
  "noncommercial"  non-commercial licences or terms: personal-use box (Alt+Q); the result is personal use only.
  "research"       narrower terms (here: journalistic use only): personal-use box (Alt+Z) after agreeing to the
                   terms; personal use only.

The collections (ARCHIVE_SOURCES):
  noncommercial
    vam                     Victoria and Albert Museum, London: objects with a picture and the museum's own summary,
                            physical or brief description, through the V&A's public collections API
                            (api.vam.ac.uk, no key). The V&A's pictures may be used for non-commercial purposes
                            (https://www.vam.ac.uk/info/va-websites-terms-conditions). Pictures the V&A flags as
                            sensitive are left out. Place made as "origin".
    digital_commonwealth_nc Digital Commonwealth (Massachusetts libraries and museums, mostly the Boston Public
                            Library and the Nantucket Historical Association): photographs whose record gives the
                            licence CC BY-NC-ND 4.0, with their titles and abstracts (6 words or more, more than
                            names and dates) and the place from the record. (Its unrestricted photos are the open
                            "digital_commonwealth" pack.) CC BY-NC-ND: the pictures are not changed or shared; the
                            kit only makes its own training copies on the user's computer.
  research
    agencia_brasil          Agência Brasil (Brazil's public news agency, EBC): news photos with the photographer's
                            Portuguese caption and the place and date it opens with ("Campo Grande/ MS - 28.03.2026 -
                            ..."). Its reproduction policy (https://agenciabrasil.ebc.com.br/sobre) allows
                            reproduction "for journalistic purposes, with the source named"; commercial use needs
                            permission. Only photos credited to Agência Brasil's own photographers are used (not wire
                            or partner photos). Captions stay in Portuguese.

Every picture gets "Describe this picture." with the caption, tidied and at least 6 words long; a picture whose record
gives the place also gets "Where was this photo taken?" and its rows carry "place". Rows whose words name a child
carry "child": True; nothing sexual is kept (extra_sources.NUDE). Graphic pictures (the dead, wounds, casualties) are
kept by the owner's rule and their rows carry "content": "graphic"; sexual violence, torture and execution scenes,
and pictures naming a dead or injured child, are left out.

Needing sign-up (cannot be downloaded automatically; ARCHIVE_SIGN_UP has the links): the NARA catalogue API v2 key,
DVIDS (US military photos), the NYPL Digital Collections API, Harvard Art Museums, Paris Musées, the Flickr
collections (White House, State Department, NIH Image Gallery, UK National Archives, US Army, Chilean and Argentine
government photos, Biodiversity Heritage Library), the Imperial War Museums' non-commercial licence downloads and the
State Library of New South Wales API.

Looked at and not included: ARCHIVE_NOT_INCLUDED.

    python kit/archive_sources.py vam --data <empty folder> --cap 8     (a quick check)
"""

import json
import os
import random
import re
import time

import sources
from documentary_sources import caption, where_row
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import NARRATE, Source, clean

# Words that mean a picture shows the dead, wounds or casualties: kept, with "content": "graphic" on its rows.
GRAPHIC = re.compile(r"\b(dead(?! sea\b| end\b)|corpses?|bod(y|ies) of|killed|wounded|wounds?|casualt\w*|injur\w*|"
                     r"bleeding|massacre|atrocit\w*|mortos?|mortas?|feridos?|feridas?|v[íi]timas?|cad[áa]ver\w*)\b",
                     re.I)
# Never kept: sexual violence, torture and executions.
NEVER = re.compile(r"\b(rape[ds]?|raping|sexual(ly)? (assault\w*|abuse\w*|violence)|molest\w*|estupr\w*|tortur\w*|"
                   r"execut\w*|beheading|lynch\w*|firing squad)\b", re.I)
# Portuguese words for children that personal_sources.CHILD_WORDS does not have.
CHILD_PT = re.compile(r"\b(crian[çc]as?|menin[oa]s?|beb[êe]s?|adolescentes?|alunos?|alunas?|estudantes?|filh[oa]s?)\b",
                      re.I)


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def session():
    """A requests session with the kit's name."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = sources.USER_AGENT
    return s


def get_json(s, url, params=None, tries=3):
    """The JSON at url, trying again when the server is busy; None when it never came."""
    for attempt in range(tries):
        try:
            r = s.get(url, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (403, 404):
                return None
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(5 * (attempt + 1))
    return None


def make_rows(file_name, url, answer, credit, place="", kind=None):
    """The kit rows of one picture: "Describe this picture." and, for a photo whose record gives where it was taken,
    "Where was this photo taken?"; "child" when the answer names a child, "content": "graphic" when it names the
    dead or injuries. [] when the answer names a dead or injured child or something never kept."""
    child = bool(CHILD_WORDS.search(answer) or CHILD_PT.search(answer))
    graphic = bool(GRAPHIC.search(answer))
    if NEVER.search(answer) or (child and graphic):
        return []
    row = {"question": NARRATE, "answer": answer, "split": "", "credit": credit, "child": child}
    if graphic:
        row["content"] = "graphic"
    if place:
        row.update(sources.place_fields({"place": place, "place_kind": kind or "photo"}))
    rows = [(file_name, url, row)]
    if place and (kind or "photo") == "photo":
        rows.append((file_name, url, where_row(row, place)))
    return rows


# ----------------------------------------------------------------- noncommercial: Victoria and Albert Museum

VAM = "https://api.vam.ac.uk/v2/"
VAM_TERMS = "https://www.vam.ac.uk/info/va-websites-terms-conditions"
# Kinds of object whose description is about a pattern or a page, not something to see in a photo.
VAM_LEFT_OUT = re.compile(r"\b(textile design|design for|pattern|sample|fragment|negative|book|manuscript|"
                          r"letter|ticket|programme|playbill|print(ed)? ephemera)\b", re.I)


def vam_object(s, record):
    """(file name, picture address, rows) of one V&A object with a description of 6 words or more, or None."""
    images = record.get("_images") or {}
    base = images.get("_iiif_image_base_url") or ""
    if not base or VAM_LEFT_OUT.search(record.get("objectType") or ""):
        return None
    data = get_json(s, VAM + "object/" + record["systemNumber"]) or {}
    full = data.get("record") or {}
    meta = (data.get("meta") or {}).get("images") or {}
    if any(m.get("sensitiveImage") for m in meta.get("_images_meta") or []):
        return None
    text = full.get("summaryDescription") or full.get("physicalDescription") or full.get("briefDescription") or ""
    answer = caption(re.sub(r"\s*\(\d+[:\d\s,to]*\)", "", text))
    if not answer:
        return None
    title = clean(record.get("_primaryTitle")) or clean(record.get("objectType"))
    maker = clean((record.get("_primaryMaker") or {}).get("name"))
    place = clean(record.get("_primaryPlace"))
    credit = (f"{title}" + (f", {maker}" if maker else "") + f", © Victoria and Albert Museum, London, "
              f"https://collections.vam.ac.uk/item/{record['systemNumber']}/ , non-commercial use ({VAM_TERMS})")
    return (f"vam-{record['systemNumber']}.jpg", base + "full/!1600,1600/0/default.jpg", answer, credit, place)


def prepare_vam(source, data_dir, work, cap):
    """V&A objects with pictures from random pages of the API's search (about 750,000 records with pictures), each
    object's own record read for its description."""
    s, rng = session(), random.Random(501)
    want = int((cap + source.test) * 1.2)
    pages = list(range(1, 7500))
    rng.shuffle(pages)
    items = []
    for page in pages:
        if len(items) >= want * 1.4:
            break
        data = get_json(s, VAM + "objects/search", {"q": "", "images_exist": 1, "page_size": 100, "page": page,
                                                    "order_sort": "asc"}) or {}
        records = data.get("records") or []
        rng.shuffle(records)
        for record in records[:max(3, want // 40)]:
            found = vam_object(s, record)
            time.sleep(0.2)
            if found:
                name, url, answer, credit, place = found
                items += make_rows(name, url, answer, credit, place, "origin")
    pictures = list(dict.fromkeys(name for name, _, _ in items))[:want]
    items = [i for i in items if i[0] in set(pictures)]
    say(f"  Fetching {len(pictures)} V&A pictures (non-commercial).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- noncommercial: Digital Commonwealth CC BY-NC-ND

DC = "https://www.digitalcommonwealth.org/"


def dc_place(a):
    """The place of a Digital Commonwealth record from its place hierarchy ("Nantucket, Massachusetts, United
    States"), or ""."""
    for text in a.get("subject_hiergeo_geojson_ssm") or []:
        try:
            p = json.loads(text).get("properties") or {}
        except ValueError:
            continue
        if p.get("country"):
            parts = [p.get("city") or p.get("city_section") or p.get("area") or "", p.get("state") or "",
                     "USA" if p["country"] == "United States" else p["country"]]
            return ", ".join(dict.fromkeys(x for x in parts if x))
    return ""


def prepare_digital_commonwealth_nc(source, data_dir, work, cap):
    """Digital Commonwealth photographs under CC BY-NC-ND 4.0 (about 119,000): random result pages, a few from
    each (pages are in title order), titles with their abstract that say more than names and dates."""
    s, rng = session(), random.Random(502)
    want = int((cap + source.test) * 1.2)
    params = {"per_page": 100, "f[genre_basic_ssim][]": "Photographs", "f[reuse_allowed_ssi][]": "creative commons"}
    first = get_json(s, DC + "search.json", dict(params, page=1)) or {}
    pages = list(range(1, int(((first.get("meta") or {}).get("pages") or {}).get("total_pages") or 1) + 1))
    rng.shuffle(pages)
    items, answers, pictures = [], set(), 0
    for page in pages[:400]:
        if pictures >= want:
            break
        time.sleep(1)
        taken = 0
        for x in (get_json(s, DC + "search.json", dict(params, page=page)) or {}).get("data") or []:
            a = x.get("attributes") or {}
            if "by-nc-nd" not in (a.get("license_uri_ss") or "") or not a.get("exemplary_image_ssi") \
                    or taken >= max(2, want // 30):
                continue
            title, abstract = clean(a.get("title_info_primary_tsi")), clean(a.get("abstract_tsi"))
            answer = caption(f"{title}. {abstract}" if abstract and abstract[:30].lower() not in title.lower()
                             else title)
            lower_words = [w for w in re.findall(r"[A-Za-z]+", answer) if w.islower() and len(w) > 2]
            if not answer or answer in answers or len(lower_words) < 3:
                continue
            answers.add(answer)
            ark = a.get("identifier_uri_ss") or DC + "search/" + a["id"]
            credit = (f"{title[:150]}, {clean(a.get('institution_name_ssi')) or 'Digital Commonwealth'}, via Digital "
                      f"Commonwealth, CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/), {ark}")
            url = (f"https://iiif.digitalcommonwealth.org/iiif/2/{a['exemplary_image_ssi']}/full/!1600,1600/0/"
                   "default.jpg")
            rows = make_rows(f"dcnc-{a['id'].split(':')[-1]}.jpg", url, answer, credit, dc_place(a))
            if rows:
                taken += 1
                pictures += 1
                items += rows
    say(f"  Fetching {pictures} Digital Commonwealth photographs (CC BY-NC-ND, non-commercial).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=3)


# ----------------------------------------------------------------- research: Agência Brasil

AB = "https://agenciabrasil.ebc.com.br"
AB_TERMS = "https://agenciabrasil.ebc.com.br/sobre"
AB_PAGES = 16000                     # pages of its photo list (November 2026)
# Brazil's state abbreviations, for the place a caption opens with ("Campo Grande/ MS").
BR_STATES = {"AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
             "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
             "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
             "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
             "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
             "SE": "Sergipe", "TO": "Tocantins"}


def ab_caption(text):
    """(caption, place, photographer) of an Agência Brasil photo description ("Campo Grande/ MS - 28.03.2026 - O
    presidente da COP15 ... Foto: Rafa Neddermeyer/ Agência Brasil"); the place only for a Brazilian city and
    state."""
    text = clean(text)
    m = re.search(r"\s*Fotos?:\s*(.+)$", text)
    who = clean(m.group(1)) if m else ""
    text = text[:m.start()] if m else text
    place = ""
    head = re.match(r"^\s*([^-–]{2,60}?)\s*[-–]\s*\d{1,2}[./]\d{1,2}[./]\d{2,4}\s*[-–]\s*", text)
    if head:
        text = text[head.end():]
        city = re.match(r"^(.+?)\s*/\s*([A-Z]{2})$", head.group(1).strip())
        if city and city.group(2) in BR_STATES:
            place = f"{city.group(1).strip()}, {BR_STATES[city.group(2)]}, Brazil"
        elif head.group(1).strip() in ("Brasília", "Brasilia"):
            place = "Brasília, Brazil"
    return text.strip(), place, who


def prepare_agencia_brasil(source, data_dir, work, cap):
    """Agência Brasil photos from random pages of its photo list: each photo page's description (the caption) and
    its 754-pixel copy; only photos credited "Agência Brasil"."""
    s, rng = session(), random.Random(503)
    s.headers["User-Agent"] = "Mozilla/5.0 (compatible; " + sources.USER_AGENT + ")"
    want = int((cap + source.test) * 1.2)
    pages = list(range(1, AB_PAGES))
    rng.shuffle(pages)
    items, answers, pictures = [], set(), 0
    for number in pages[:300]:
        if pictures >= want:
            break
        time.sleep(1)
        try:
            listing = s.get(AB + "/fotos", params={"page": number}, timeout=60).text
        except Exception:  # noqa: BLE001 - next page
            continue
        links = sorted(set(re.findall(r'href="(https://agenciabrasil\.ebc\.com\.br/foto/[^"]+)"', listing)))
        rng.shuffle(links)
        for link in links[:max(2, want // 40)]:
            time.sleep(0.5)
            try:
                page = s.get(link, timeout=60).text
            except Exception:  # noqa: BLE001 - next photo
                continue
            meta = dict(re.findall(r'<meta (?:property|name)="([^"]+)" content="([^"]*)"', page))
            text, place, who = ab_caption(meta.get("og:description") or meta.get("description") or "")
            url = (meta.get("twitter:image") or "").replace("&amp;", "&")
            answer = caption(text)
            if not answer or answer in answers or not url or "Agência Brasil" not in who:
                continue
            answers.add(answer)
            credit = f"Foto: {who}, {link} , reproduction for journalistic purposes with the source named ({AB_TERMS})"
            rows = make_rows("agbr-" + re.sub(r"[^\w-]", "_", link.rsplit("/", 1)[-1])[:80] + ".jpg", url,
                             answer, credit, place)
            if rows:
                pictures += 1
                items += rows
    say(f"  Fetching {pictures} Agência Brasil photos (personal use).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=3)


# ----------------------------------------------------------------- needing sign-up, and not included

ARCHIVE_SIGN_UP = {
    "US National Archives catalogue API v2 (public domain)":
        "https://www.archives.gov/research/catalog/help/api : an API key by e-mail request. (The open 'nara' pack "
        "uses the catalogue's own public search instead.)",
    "DVIDS, US Defense Visual Information Distribution Service (public domain military photos with captions)":
        "https://api.dvidshub.net : a free API key (sign-up); every request without one is refused.",
    "NYPL Digital Collections API (public-domain items, updated records)":
        "https://api.repo.nypl.org : a free token (sign-up). The open 'nypl' pack uses the bulk CC0 release instead.",
    "Harvard Art Museums (images: non-commercial; metadata open)":
        "https://harvardartmuseums.org/collections/api : a free API key (sign-up).",
    "Paris Musées (about 300,000 works, CC0 pictures, French descriptions)":
        "https://parismuseescollections.paris.fr/fr/se-connecter : an account and API token; its API answered "
        "'service unavailable' in November 2026.",
    "Flickr collections: The White House, US State Department, NIH Image Gallery, US Army, UK National Archives, "
    "Chilean government (Gobierno de Chile), Argentine government (Casa Rosada), Biodiversity Heritage Library":
        "https://www.flickr.com/services/api/misc.api_keys.html : a free Flickr API key. Most are public domain, "
        "CC BY or 'no known copyright restrictions' (check each photo's licence on its page).",
    "Imperial War Museums (IWM Non Commercial Licence)":
        "https://www.iwm.org.uk/corporate/policies/non-commercial-licence : downloads after accepting the licence on "
        "each item page; its collection search refused automated access (Cloudflare check).",
    "State Library of New South Wales collection API (many photos 'no known copyright restrictions')":
        "https://collection.sl.nsw.gov.au : an API key (sign-up); the API host did not answer from the machine "
        "these entries were made on.",
}

ARCHIVE_NOT_INCLUDED = {
    "Getty Images, AP, Reuters, National Geographic, BBC": "commercial and copyrighted; not scraped.",
    "FEMA photo library (public domain)": "www.fema.gov/multimedia-library refused the machine (Akamai 403).",
    "Voice of America photos": "VOA's own photos are public domain, but most photos on its pages are AP, Reuters or "
                               "AFP wire photos, and there is no list of VOA's own.",
    "Naval History and Heritage Command (public domain)": "www.history.navy.mil sends an incomplete certificate "
                                                          "chain; no secure connection could be made.",
    "US Army Center of Military History": "mostly paintings and posters with short titles; its photos are on Flickr "
                                          "(sign-up).",
    "British Museum (CC BY-NC-SA 4.0)": "its collection site refused automated access (Cloudflare check) and it has "
                                        "no public API; a noncommercial entry can be added if a data release appears.",
    "Science Museum Group (pictures CC BY-NC-SA 4.0)": "collection.sciencemuseumgroup.org.uk refused the machine "
                                                       "(CloudFront 403).",
    "Belvedere, Vienna (CC BY-SA 4.0 pictures)": "sammlung.belvedere.at refused the machine (403); a share-alike "
                                                 "entry can be added when it answers.",
    "Yale Center for British Art (public domain)": "its collection site refused automated access (Cloudflare check); "
                                                   "the LUX API answered with empty replies.",
    "Finnish National Gallery": "its open-data API needs registration; its works also reach the kit through the "
                                "europeana_fi pack.",
    "Nationalmuseum Sweden (public domain)": "its API answered with server errors; its works are also in K-samsök "
                                             "(the ksamsok pack).",
    "State Library Victoria, Library and Archives Canada, Danish Royal Library": "their sites refused the machine "
                                                                                "(proxy errors, a security check, "
                                                                                "or a broken API).",
    "Beeldbank WO2 (NIOD)": "licences differ per photo and are not given in a form a program can read.",
    "European Parliament Multimedia Centre": "its home page answered, but its photo search is built by the page's "
                                             "script with no public listing, and the photo licence could not be "
                                             "confirmed; to be checked again.",
    "Natural History Museum London, Naturalis, Museum für Naturkunde": "specimen photos have names, not written "
                                                                       "descriptions; named specimens reach the kit "
                                                                       "through GBIF.",
    "Wikinews (captions CC BY 2.5)": "its API refused the machine (too many requests); its photos are Commons files.",
}


# ----------------------------------------------------------------- the table

ARCHIVE_SOURCES = [
    Source("vam", "Victoria and Albert Museum objects with the museum's descriptions (non-commercial)",
           f"V&A terms: pictures and text for non-commercial use ({VAM_TERMS})",
           "Victoria and Albert Museum, London, collections API (https://api.vam.ac.uk), each object credited "
           "'© Victoria and Albert Museum, London'", "noncommercial", 3000, 20, prepare_vam,
           "about 1 GB of pictures", terms=VAM_TERMS,
           terms_summary="The V&A allows its pictures and texts to be used for non-commercial purposes such as "
                         "private study and teaching; no commercial use. Personal use only."),
    Source("digital_commonwealth_nc", "Digital Commonwealth photographs of Massachusetts and beyond, CC BY-NC-ND "
                                      "(non-commercial)",
           "CC BY-NC-ND 4.0 (each record's licence, https://creativecommons.org/licenses/by-nc-nd/4.0/)",
           "Digital Commonwealth (https://www.digitalcommonwealth.org), Boston Public Library and other Massachusetts "
           "institutions, CC BY-NC-ND 4.0, each photo credited", "noncommercial", 2500, 20,
           prepare_digital_commonwealth_nc, "about 800 MB of pictures",
           terms="https://creativecommons.org/licenses/by-nc-nd/4.0/",
           terms_summary="CC BY-NC-ND 4.0: non-commercial use with credit, and the pictures themselves are not "
                         "changed or shared. Personal use only."),
    Source("agencia_brasil", "Agência Brasil news photos with Portuguese captions (personal use)",
           f"Agência Brasil reproduction policy: journalistic use with the source named; commercial use needs "
           f"permission ({AB_TERMS})",
           "Agência Brasil, Empresa Brasil de Comunicação (EBC), https://agenciabrasil.ebc.com.br , each photo "
           "credited to its photographer", "research", 2000, 20, prepare_agencia_brasil,
           "about 300 MB of pictures", terms=AB_TERMS,
           terms_summary="Agência Brasil allows its texts and photos to be reproduced by news media for journalistic "
                         "purposes with the source named; other and commercial uses need its permission. Personal "
                         "use only."),
]

# The collections a picture-making model may learn from: only those without people (V&A objects are museum objects,
# but some show people and children in paintings and photographs, so none is marked).
ARCHIVE_PICTURE_MAKING_OK = set()


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one archive collection.")
    parser.add_argument("key", choices=[s.key for s in ARCHIVE_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in ARCHIVE_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="archive-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, "
          f"{sum(1 for r in rows if r.get('content') == 'graphic')} rows marked graphic, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
