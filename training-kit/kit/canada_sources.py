"""CANADA picture collections for the Picture Model Training Kit (the Canadian equivalents of us_sources.py and
us_modern_sources.py) that cannot be ready-made packs because of their licence: share-alike, non-commercial or
research use. The open ones (Commons CC0, public domain and CC BY Canadian houses, streets, cars, money, road signs,
shops, holidays, eating out, getting around, public places and archive photos, and iNaturalist CC0 and CC BY photos
by province) are packs in packs/canada_packs.py.

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link and the exact terms line are in each entry).

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA, ODbL and GFDL: only with the share-alike choice (--with-wikipedia).
  "noncommercial"  CC BY-NC and other non-commercial terms, such as the Government of Canada's "you may reproduce
                   the materials in whole or in part for non-commercial purposes": personal use only
                   (--personal-noncommercial).
  "research"       terms that allow copying but leave other uses to the owners: personal use only
                   (--personal-research with --accept-research-terms).

Answers are fixed sentences from each source's own records (a Commons category's name, a product's name, brand and
size as people typed them into Open Food Facts, an iNaturalist community identification, a recall notice's product,
photo text and issue, a form's own title, an archive's own caption), never written by an AI model. Nobody is named.
Canadian labels and signs are bilingual: the answers are in English, and a product whose label is in English and
French says so. The City of Montréal's archive captions are only in French: those rows are in French ("language":
"fr"), as other French collections in extra_sources.py are.

Safety (packs/SOURCE-RULES.md): no sexual content (files and records whose words name nudity, underwear, swimwear or
sexual products are left out); children only in everyday clothed scenes, and every row whose words name a child is
marked "child". Recall photos of children's clothing and sleepwear are left out, and so are recalls of drugs, medical
devices, cannabis and vehicles (only consumer products and food are taken).

The collections (CANADA_SOURCES):
  share-alike
    commons_ca_sa          Wikimedia Commons: the Canadian house, room, street, road-sign, shop, holiday, eating-out,
                           transit and public-place categories of the open packs, files under CC BY-SA or GFDL.
    openfacts_ca           Open Food Facts (photos CC BY-SA 3.0, data ODbL 1.0;
                           https://world.openfoodfacts.org/terms-of-use): front photos of products sold in Canada
                           (countries_tags en:canada) with a North American or GS1 Canada barcode (GS1 prefixes 000 to
                           139, or 754 and 755), with the name, brand and size people typed in. Read through
                           off_dump.py (the product database on Hugging Face, the photos on AWS Open Data), never
                           Open Food Facts' websites, which block AI crawlers. Open Beauty Facts and Open Products
                           Facts (which gave "What languages is the label in?" from their records) are no longer read:
                           same block, no open photo route (ca_site_items is kept, and stops at once).
                           Supplements, vitamins, cough drops and throat lozenges are skipped (med_vet_sources.
                           openfacts_supplements takes them).
    inaturalist_ca_sa      iNaturalist research-grade observations in each province and territory, photos CC BY-SA
                           (through GBIF and the iNaturalist Open Dataset, inat_gbif.py; such photos are few).
  noncommercial
    inaturalist_ca_nc      The same, photos under CC BY-NC, BY-NC-SA or BY-NC-ND.
    montreal_archives      Archives de la Ville de Montréal, "Archives photographiques (sélection)" (donnees.montreal.ca,
                           CC BY-NC-SA 4.0: "Ces données sont accessibles à toutes et tous sous licence CC BY-NC-SA 4.0
                           ... Certaines restrictions d'usages s'appliquent sur les fichiers numérisés (usage non
                           commercial uniquement)"): 110 old photographs of Montreal streets, parks and buildings with
                           the archive's French title and description. "Que montre cette photographie ?" (French) and
                           "Where was this photo taken?" -> "It was taken in Montreal, Quebec, Canada."
    cra_forms              Blank Canada Revenue Agency forms (TD1, T2201 Disability Tax Credit Certificate, T1213,
                           RC151, RC66 and others), each form's English PDF found on its canada.ca page and its first
                           pages drawn as pictures (needs pypdfium2: pip install pypdfium2). "What is this form?",
                           "What does it say at the top?", "Is this form filled in?". The Government of Canada's terms
                           (https://www.canada.ca/en/transparency/terms.html): "Unless otherwise specified you may
                           reproduce the materials in whole or in part for non-commercial purposes, and in any format,
                           without charge or further permission" and "you may not reproduce materials on this site, in
                           whole or in part, for the purposes of commercial redistribution without prior written
                           permission". So: non-commercial. (canada.ca did not answer the machine this was written
                           on; the page and PDF readers are tested with made-up data only.)
  research
    ca_recalls             Health Canada's Recalls and Safety Alerts (recalls-rappels.canada.ca): the list is open data
                           under the Open Government Licence - Canada (open.canada.ca dataset d38de914-...), but it has
                           no pictures; the photos are on each recall's page (robots.txt allows those pages and their
                           pictures), under the canada.ca terms above, and many are the recalling companies' own
                           product photos ("Some of the content on this site may be subject to the copyright of another
                           party"). So, as the US CPSC recall photos: research, personal use only. "What product is
                           this?" from the photo's own alt text and the notice's product, "Why was this product
                           recalled?" from the notice's issue.

Needing sign-up (CANADA_SIGN_UP has the links), looked at and not included (CANADA_NOT_INCLUDED, with the reason of
each) and the owners to ask for permission (CANADA_PERMISSION_CANDIDATES: the organisation, what they have, their
terms line and contact page; nothing here downloads from them).

CANADA_PICTURE_MAKING_OK holds the collections without people: openfacts_ca and cra_forms. Not the Commons entry
(street and holiday photos), iNaturalist (hands), the recall photos (children's products in use) or the Montréal
archive photos (street scenes with people).

    python kit/canada_sources.py montreal_archives --cap 8     (a quick check; prints a few rows)
"""

import csv
import html
import io
import json
import os
import random
import re
import time
import unicodedata

from extra_sources import USER_AGENT, get_json, off_name, per_label, research, save, say
from home_sources import commons_sa_items, facts_image, kind_rows, FACT_SITES, FACTS_FIELDS, FACTS_CREDIT
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import Source, clean
from us_sources import off_us_front, INAT_GROUPS, INAT_LICENCES

WHAT_Q = "What is this?"
HOUSE_Q = "What kind of house is this?"
ROOM_Q = "What room is this?"
PLACE_Q = "What kind of place is this?"
HAPPENING_Q = "What is happening here?"
SIGN_Q = "What does this road sign mean?"
PRODUCT_Q = "What product is this?"
LANGUAGES_Q = "What languages is the label in?"
RECALL_Q = "Why was this product recalled?"
FORM_Q = "What is this form?"
TOP_Q = "What does it say at the top?"
FILLED_Q = "Is this form filled in?"
WHERE_Q = "Where was this photo taken?"
FRENCH_Q = "Que montre cette photographie ?"
CANADA = "Canada"
# Words that leave a record out: nudity, underwear, swimwear and sexual products, evidence photos (the safety rules).
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|bathing suits?|underwear|lingerie|bras?|briefs|nude|naked|topless|"
                       r"sexy|sexual\w*|erotic\w*|adult toys?|vibrators?|condoms?|lubricants?|crime scenes?|"
                       r"evidence photo\w*|mug ?shots?)\b", re.I)
CHILD_CLOTHES = re.compile(r"\b(sleepwear|pajamas|pyjamas|nightgowns?|robes?|garments?|clothing|onesies?|"
                           r"bodysuits?|hoodies?|sweatshirts?|jackets?|dresses|costumes?)\b", re.I)
PROVINCES = ["Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia",
             "New Brunswick", "Prince Edward Island", "Newfoundland and Labrador", "Yukon", "Northwest Territories",
             "Nunavut"]


def folded(text):
    """Text without accents, in lower case ("Québec" -> "quebec")."""
    return "".join(c for c in unicodedata.normalize("NFD", text or "") if unicodedata.category(c) != "Mn").lower()


# ----------------------------------------------------------------- share-alike: Commons Canadian categories

# The categories of packs/canada_packs.py (not the cars: their answers come from each file's model category).
CA_SA = (
    [(f"Houses in {p}" if p != "Northwest Territories" else "Houses in the Northwest Territories", WHAT_Q,
      f"This is a house in {p}, Canada.", True) for p in PROVINCES]
    + [("Farmhouses in Canada", HOUSE_Q, "It is a farmhouse.", True),
       ("Log houses in Canada", HOUSE_Q, "It is a log house.", True),
       ("Cottages in Canada", HOUSE_Q, "It is a cottage.", True),
       ("Row houses in Canada", HOUSE_Q, "It is a row house.", True),
       ("Semi-detached houses in Canada", HOUSE_Q, "It is a semi-detached house.", True),
       ("Kitchens in Canada", ROOM_Q, "This is a kitchen.", True),
       ("Living rooms in Canada", ROOM_Q, "This is a living room.", True),
       ("Bedrooms in Canada", ROOM_Q, "This is a bedroom.", True),
       ("Streets in Toronto", PLACE_Q, "This is a street in Toronto, Canada.", True),
       ("Streets in Montreal", PLACE_Q, "This is a street in Montreal, Canada.", True),
       ("Streets in Vancouver", PLACE_Q, "This is a street in Vancouver, Canada.", True),
       ("Streets in Calgary", PLACE_Q, "This is a street in Calgary, Canada.", True),
       ("Streets in Ottawa", PLACE_Q, "This is a street in Ottawa, Canada.", True),
       ("Streets in Halifax, Nova Scotia", PLACE_Q, "This is a street in Halifax, Canada.", True),
       ("Stop signs in Canada", SIGN_Q, "It is a stop sign (in Quebec it says ARRÊT).", True),
       ("Bilingual road signs in Canada", SIGN_Q, "It is a bilingual road sign, in English and French.", True),
       ("Supermarkets in Canada", PLACE_Q, "This is a supermarket in Canada.", True),
       ("Dépanneurs", PLACE_Q, "This is a dépanneur, a Quebec corner store.", True),
       ("Canada Day", HAPPENING_Q, "This is Canada Day (1 July).", True),
       ("Remembrance Day in Canada", HAPPENING_Q, "This is Remembrance Day in Canada (11 November).", True),
       ("Thanksgiving in Canada", HAPPENING_Q, "This is Thanksgiving in Canada (October).", True),
       ("National Holiday (Quebec)", HAPPENING_Q, "This is the Fête nationale du Québec (24 June).", True),
       ("Winterlude", HAPPENING_Q, "This is Winterlude, Ottawa's winter festival.", True),
       ("Tim Hortons", PLACE_Q, "This is a Tim Hortons coffee and doughnut shop.", True),
       ("Poutine", WHAT_Q, "This is poutine: fries with cheese curds and gravy.", True),
       ("Toronto subway", PLACE_Q, "This is the Toronto subway (TTC).", True),
       ("Montreal Metro stations", PLACE_Q, "This is a Montreal Metro station.", True),
       ("TransLink (British Columbia)", PLACE_Q, "This is TransLink, Vancouver's public transit.", True),
       ("GO Transit", PLACE_Q, "This is GO Transit, the Toronto region's commuter trains and buses.", True),
       ("Toronto Pearson International Airport", PLACE_Q, "This is Toronto Pearson International Airport.", True),
       ("Post offices in Canada", PLACE_Q, "This is a post office in Canada.", True),
       ("Shoppers Drug Mart", PLACE_Q, "This is a Shoppers Drug Mart pharmacy.", True),
       ("Libraries in Canada", PLACE_Q, "This is a library in Canada.", True),
       ("Winter in Canada", HAPPENING_Q, "This is winter in Canada.", True),
       ("Pond hockey", HAPPENING_Q, "This is pond hockey, ice hockey played outdoors.", True),
       ("Rideau Canal Skateway", HAPPENING_Q, "This is skating on the Rideau Canal Skateway in Ottawa.", False),
       ("Ice fishing in Canada", HAPPENING_Q, "This is ice fishing in Canada.", True),
       ("Canoeing in Canada", HAPPENING_Q, "This is canoeing in Canada.", True)])


def prepare_commons_ca_sa(source, data_dir, work, cap):
    """Wikimedia Commons Canadian categories, files under CC BY-SA or GFDL (home_sources.commons_sa_items: the
    categories share the cap; rows whose words name a child are marked "child"; files whose words name nudity are
    left out). Files whose words name swimwear, underwear or evidence photos are left out too."""
    items = commons_sa_items(CA_SA, cap, source.test, "ca-sa")
    left_out = {i[0] for i in items if NOT_SHOWN.search(f"{i[0]} {i[2]['answer']}")}    # every row of that file
    items = [(n, u, dict(r, place=CANADA)) for n, u, r in items if n not in left_out]
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: Open ... Facts, sold in Canada

CA_FOOD_CATEGORIES = ("breakfast-cereals", "cookies", "crackers", "chips-and-fries", "candies", "chocolates",
                      "peanut-butters", "jams", "maple-syrups", "sodas", "fruit-juices", "coffees", "teas", "pastas",
                      "pasta-sauces", "soups", "canned-vegetables", "rices", "breads", "cheeses", "yogurts", "milks",
                      "plant-based-milks", "ice-creams", "frozen-pizzas", "frozen-meals", "condiments", "snack-bars",
                      "nuts", "flours", "baby-foods", "waters")
CA_FACTS_CREDIT = "Open Food Facts contributors, product {code}: photos CC BY-SA 3.0, data ODbL 1.0, " \
                  "https://world.openfoodfacts.org/product/{code}"


# Supplements, vitamins, cough drops and throat lozenges: taken by med_vet_sources.openfacts_supplements (US and
# Canada), so they are skipped here and the two entries do not repeat each other.
SUPPLEMENT_TAGS = {"en:dietary-supplements", "en:vitamins", "en:cough-drops", "en:throat-lozenges"}


def is_supplement(hit):
    """True when a product's categories name a supplement, vitamin, cough drop or throat lozenge."""
    return bool(SUPPLEMENT_TAGS & set(hit.get("categories_tags") or []))


def ca_barcode(code):
    """True when a product's barcode is one sold on Canadian shelves: a North American UPC (GS1 prefixes 000 to 139,
    which GS1 Canada also gives out) or a GS1 Canada EAN (754 and 755); so a European product also sold in Canada is
    left out, as us_sources.us_barcode does for the USA."""
    code = str(code or "")
    if not code.isdigit() or len(code) not in (12, 13):
        return False
    prefix = code.zfill(13)[:3]
    return prefix <= "139" or prefix in ("754", "755")


def bilingual_row(hit, extra):
    """ "What languages is the label in?" -> "The label is in English and French." when the product's record gives
    both languages (Open Food Facts' languages_codes); None otherwise (a label is not guessed)."""
    codes = hit.get("languages_codes") or {}
    if "en" in codes and "fr" in codes:
        return dict(extra, question=LANGUAGES_Q, answer="The label is in English and French.")
    return None


def ca_food_items(work, want):
    """[(file name, address, row)] for Open Food Facts products sold in Canada with a Canadian shelf barcode, the
    most scanned of each grocery category first, an even share of each. Read from the product database's slim copy
    (off_dump), never from Open Food Facts' websites."""
    import off_dump
    per = per_label(want, len(CA_FOOD_CATEGORIES))
    wanted = {f"en:{c}": c for c in CA_FOOD_CATEGORIES}

    def labels(hit):
        """The grocery categories of a product sold in Canada with a Canadian shelf barcode, an English front photo
        and a name that is not left out; never a supplement."""
        if "en:canada" not in hit["countries_tags"] or not ca_barcode(hit["code"]) or is_supplement(hit) \
                or not off_us_front(hit["code"], hit["images"]):
            return ()
        answer = off_name(hit)
        if not answer or NOT_SHOWN.search(answer):
            return ()
        return [wanted[t] for t in hit["categories_tags"] if t in wanted]

    best = off_dump.top_by_label(work, labels, per)
    items = []
    for category in CA_FOOD_CATEGORIES:
        hits = best.get(category, [])
        for hit in hits:
            extra = {"split": "", "credit": CA_FACTS_CREDIT.format(code=hit["code"]), "place": CANADA,
                     "place_kind": "market"}
            items.append((f"off-front-{hit['code']}.jpg", off_us_front(hit["code"], hit["images"]),
                          dict(extra, question=PRODUCT_Q, answer=off_name(hit))))
        say(f"  Open Food Facts (Canada) {category}: {len(hits)} products")
    return items


def ca_site_items(site, want):
    """[(file name, address, row)] for Open Beauty Facts or Open Products Facts products sold in Canada. Not used:
    those sites block AI crawlers (off_dump.NOT_BUILT), so this stops at once; the code is kept."""
    import off_dump
    off_dump.refuse(f"Open {site.capitalize()} Facts (Canada)")
    base, _, name, _ = FACT_SITES[site]
    hits, page = [], 1
    while len(hits) < want * 2 and page <= 10:
        try:
            data = get_json(f"{base}/api/v2/search", {"countries_tags_en": "canada", "page_size": 100, "page": page,
                                                      "sort_by": "unique_scans_n",
                                                      "fields": FACTS_FIELDS + ",languages_codes"})
        except RuntimeError:
            break
        batch = data.get("products") or []
        hits += batch
        time.sleep(1)
        if len(batch) < 100:
            break
        page += 1
    items = []
    for hit in hits:
        if len({i[0] for i in items}) >= want:
            break
        url = facts_image(site, hit.get("code") or "", hit.get("images") or {}, "front", "en") \
            if ca_barcode(hit.get("code")) and not is_supplement(hit) else ""
        answer = off_name(hit)
        if not url or not answer or NOT_SHOWN.search(answer):
            continue
        extra = {"credit": FACTS_CREDIT.format(site=name, code=hit["code"], base=base), "split": "",
                 "place": CANADA, "place_kind": "market"}
        file_name = f"{site}-front-{hit['code']}.jpg"
        items.append((file_name, url, dict(extra, question=PRODUCT_Q, answer=answer)))
        items += [(file_name, url, dict(extra, **row)) for row in kind_rows(site, hit)]
        row = bilingual_row(hit, extra)
        if row:
            items.append((file_name, url, row))
    say(f"  {name} (Canada): {len({i[0] for i in items})} products")
    return items


def prepare_openfacts_ca(source, data_dir, work, cap):
    """Front photos of Open Food Facts products sold in Canada, with their name, brand and size; Canada as the place
    of sale. Open Beauty Facts and Open Products Facts (ca_site_items) used to give a quarter: they block AI crawlers
    and have no open bulk route for their photos, so the food products now fill the entry."""
    want = int((cap + source.test) * 1.15)
    items = ca_food_items(work, want)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- iNaturalist, provinces, other licences

def inat_ca_rows(source, data_dir, licences, prefix):
    """Rows for iNaturalist research-grade observations in each province and territory whose photo's own licence is
    one of licences: the provinces and groups take turns, one page each. The province is the place. The records
    come from GBIF and the photos from the iNaturalist Open Dataset (inat_gbif.py); iNaturalist's website and API are
    never read."""
    import inat_gbif
    want = int((source.cap + source.test) * 1.1)
    provinces = inat_gbif.regions("CA", PROVINCES)
    items = inat_gbif.region_items("CA", provinces, INAT_GROUPS, licences, want, prefix, lambda p: f"{p}, Canada")
    say(f"  iNaturalist on GBIF (Canada, {', '.join(INAT_LICENCES[x] for x in licences)}): {len(items) // 2} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


def prepare_inaturalist_ca_sa(source, data_dir, work, cap):
    """iNaturalist Canadian photos under CC BY-SA."""
    return inat_ca_rows(source, data_dir, ("cc-by-sa",), "inatca-sa")


def prepare_inaturalist_ca_nc(source, data_dir, work, cap):
    """iNaturalist Canadian photos under CC BY-NC, BY-NC-SA or BY-NC-ND."""
    return inat_ca_rows(source, data_dir, ("cc-by-nc", "cc-by-nc-sa", "cc-by-nc-nd"), "inatca-nc")


# ----------------------------------------------------------------- non-commercial: Archives de la Ville de Montréal

MTL_CSV = ("https://donnees.montreal.ca/dataset/cc3fbf3d-f93c-479d-a807-9ae042721aba/resource/"
           "41f0cec9-2110-452e-a93d-8f29190ee2ae/download/photothequearchives.csv")
MTL_PAGE = "https://donnees.montreal.ca/dataset/phototheque-archives"
MTL_PLACE = "Montreal, Quebec, Canada"


def montreal_rows(text):
    """[(file name, address, row)] from the archive's CSV: "Que montre cette photographie ?" with its French title
    and description ("S/O", none, is left out), and "Where was this photo taken?" in English. The credit is the one
    the archive asks for ("Archives de la Ville de Montréal")."""
    items = []
    for rec in csv.DictReader(io.StringIO(text)):
        title, words = clean(rec.get("Titre")).strip(" ."), clean(rec.get("Description"))
        url = clean(rec.get("Fichier jpg - 200 dpi")).replace("http://", "https://")
        if not title or not url:
            continue
        answer = f"{title}." + (f" {words}" if words and words.upper() not in ("S/O", "S.O.") else "")
        if not answer.endswith((".", "!", "?")):
            answer += "."
        when = clean(str(rec.get("Date") or ""))
        credit = (f"{clean(rec.get('Mention de crédits')) or 'Archives de la Ville de Montréal'}, "
                  f"{clean(rec.get('Cote'))}, CC BY-NC-SA 4.0, {MTL_PAGE}")
        name = "mtl-" + re.sub(r"[^\w-]+", "_", url.rsplit("/", 1)[-1].rsplit(".", 1)[0]) + ".jpg"
        base = {"split": "", "credit": credit, "place": MTL_PLACE, **({"facts": {"date": when}} if when else {})}
        child = {"child": True} if CHILD_WORDS.search(answer) or re.search(r"\benfants?\b", answer, re.I) else {}
        items.append((name, url, dict(base, question=FRENCH_Q, answer=answer, language="fr", **child)))
        items.append((name, url, dict(base, question=WHERE_Q, answer=f"It was taken in {MTL_PLACE}.", **child)))
    return items


def prepare_montreal_archives(source, data_dir, work, cap):
    """The City of Montréal's selection of archive photographs (110), with their French captions."""
    import requests
    r = requests.get(MTL_CSV, timeout=120, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    text = r.content.decode("utf-8-sig", errors="replace")
    items = montreal_rows(text)
    names = list(dict.fromkeys(n for n, _, _ in items))[:cap + source.test]
    items = [i for i in items if i[0] in set(names)]
    say(f"  Archives de la Ville de Montréal: {len(names)} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- non-commercial: blank CRA forms

CRA_FORMS = "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/{slug}.html"
CANADA_TERMS = "https://www.canada.ca/en/transparency/terms.html"
# The forms (their canada.ca page names): personal tax credits, disability tax credit, benefits and common requests.
CRA_SLUGS = ("td1", "td1on", "td1bc", "td1ab", "td1x", "t2201", "t1213", "rc151", "rc66", "rc65", "t1135", "t2125",
             "t777", "rc4288", "t1158", "t1-adj", "t1013", "rc4649", "t2091-ind", "rc199", "t1032", "t1-m", "t778",
             "rc72", "t1198", "rc376", "rc381")
H1 = re.compile(r"<h1[^>]*>(?P<title>.*?)</h1>", re.I | re.S)
PAGES_PER_FORM = 2
PAGE_SIDE = 1700


def form_page_links(page_html, base="https://www.canada.ca"):
    """(the form's title, the address of its English PDF) from its canada.ca page: the page's heading, and the first
    link to an English PDF ("...-26e.pdf", not the fillable "-fill-" copy when a plain one is there); ("", "")."""
    heading = H1.search(page_html)
    title = clean(html.unescape(re.sub(r"<[^>]+>", " ", heading.group("title")))) if heading else ""
    links = re.findall(r'href="([^"]+\.pdf)"', page_html, re.I)
    english = [h for h in links if re.search(r"e\.pdf$", h, re.I) and "/formspubs/" in h]
    plain = [h for h in english if "-fill-" not in h] or english
    if not plain:
        return title, ""
    href = html.unescape(plain[0])
    return title, href if href.startswith("http") else base + href


def top_words(text, most=25):
    """The words printed at the top of a page as one line (at most about most words); "" when fewer than three."""
    lines = [clean(x) for x in re.split(r"[\r\n]+", text or "") if clean(x)]
    out = []
    for line in lines:
        if len(" ".join(out + [line]).split()) > most:
            break
        out.append(line)
    words = " ".join(out)
    return words if len(words.split()) >= 3 else ""


def form_pictures(data, title, url, page_url):
    """[(base name, JPEG bytes, [rows])] for the first pages of one blank CRA form PDF (pypdfium2): page 1 with "What
    is this form?", "Is this form filled in?" and the words at its top; the next page with "What is this?"."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(data)
    meta = doc.get_metadata_dict()
    name = title or clean(meta.get("Title")) or url.rsplit("/", 1)[-1]
    credit = (f"{name}, Canada Revenue Agency, {page_url or url}; reproduced for non-commercial use under the "
              f"Government of Canada's terms ({CANADA_TERMS})")
    base = re.sub(r"\W+", "_", url.rsplit("/", 1)[-1].rsplit(".", 1)[0])[:60]
    out, pages = [], len(doc)
    place = {"place": CANADA, "place_kind": "origin"}
    for n in range(min(pages, PAGES_PER_FORM)):
        page = doc[n]
        w, h = page.get_size()
        top = top_words(page.get_textpage().get_text_bounded(left=0, bottom=h * 0.85, right=w, top=h))
        bitmap = page.render(scale=PAGE_SIDE / max(w, h)).to_pil().convert("RGB")
        jpeg = io.BytesIO()
        bitmap.save(jpeg, "JPEG", quality=88)
        if n == 0:
            rows = [{"question": FORM_Q, "answer": f"This is {name}, a Canada Revenue Agency form."
                     + (f" It has {pages} pages." if pages > 1 else ""), "split": "", "credit": credit, **place},
                    {"question": FILLED_Q, "answer": "No: it is a blank form, with empty boxes and lines to fill in.",
                     "split": "", "credit": credit, **place}]
        else:
            rows = [{"question": WHAT_Q, "answer": f"This is page {n + 1} of {pages} of {name}.", "split": "",
                     "credit": credit, **place}]
        if top:
            rows.append({"question": TOP_Q, "answer": f"At the top it says: {top}", "split": "", "credit": credit,
                         **place})
        out.append((f"cra-{base}-p{n + 1}", jpeg.getvalue(), rows))
    doc.close()
    return out


def prepare_cra_forms(source, data_dir, work, cap):
    """Blank CRA forms: each form's canada.ca page read for its title and English PDF, the PDF's first pages drawn
    as pictures (pypdfium2), gently, one form at a time."""
    try:
        import pypdfium2  # noqa: F401 - only checked here
    except ImportError:
        say("  The CRA forms need pypdfium2 (pip install pypdfium2): left out.")
        return []
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    folder = os.path.join(data_dir, source.key)
    rows = []
    for slug in CRA_SLUGS:
        if len(rows) >= (cap + source.test) * 3:
            break
        page_url = CRA_FORMS.format(slug=slug)
        try:
            page = s.get(page_url, timeout=60)
            title, pdf = form_page_links(page.text) if page.status_code == 200 else ("", "")
            if not pdf:
                say(f"  CRA {slug}: no English PDF found on its page")
                continue
            r = s.get(pdf, timeout=120)
            if r.status_code != 200 or not r.content.startswith(b"%PDF"):
                continue
            for name, data, form_rows in form_pictures(r.content, title, pdf, page_url):
                path = save(name, data, folder)
                if path:
                    rows += [dict(row, picture=path) for row in form_rows]
        except Exception as e:  # noqa: BLE001 - that form is left out
            say(f"  CRA {slug}: left out ({type(e).__name__})")
        time.sleep(2)
    say(f"  CRA forms: {len({r['picture'] for r in rows})} pages")
    return rows


# ----------------------------------------------------------------- research: Health Canada recall photos

RECALLS_JSON = "https://recalls-rappels.canada.ca/sites/default/files/opendata-donneesouvertes/HCRSAMOpenData.json"
RECALLS_SITE = "https://recalls-rappels.canada.ca"
RECALLS_DATASET = "https://open.canada.ca/data/en/dataset/d38de914-c94c-429b-8ab1-8776c31643e3"
# The recall categories taken: consumer products and food (not drugs, medical devices, cannabis or vehicles).
RECALL_KINDS = re.compile(r"^(Household items|Toys and games|Sports and fitness|Electronics|Tools and accessories|"
                          r"Appliances|Outdoor living|Furniture and furnishings|Kitchenware and tableware|"
                          r"Hobby and craft items|Jewellery|Beauty and personal care|Clothing and accessories|Food|"
                          r"Candy, confectionary, snacks and sweeteners|Nuts, grains, and seeds|Dairy|Frozen|Processed|"
                          r"Condiments|Grain products|Fish and seafood|Fruits and vegetables|Meat and poultry|"
                          r"Non-alcoholic|Bread|Beverages|Multiple food items|Pet Care/Food|Consumer products)\b")
RECALL_PICTURE = re.compile(r"/sites/default/files/(styles/[\w-]+/public/)?alert/recall/\d+/[^\"'?]+\.(jpe?g|png)",
                            re.I)
# Photo texts that show only a label, a code or a part, not the product.
RECALL_DETAIL = re.compile(r"\b(label|lot|code|upc|barcode|serial|date|location|tag|stamp|close-?up|detail|back of|"
                           r"bottom of|underside|inside of|warning|instructions?)\b", re.I)


def recall_pictures(page_html):
    """[(picture address, its alt text)] of the product photos on one recall page (the lazy-loaded data-src or the
    src of each <img> under /sites/default/files/.../alert/recall/), each once."""
    out, seen = [], set()
    for tag in re.findall(r"<img\b[^>]*>", page_html, re.I):
        attrs = dict((k.lower(), html.unescape(v)) for k, v in re.findall(r'([\w-]+)="([^"]*)"', tag))
        src = attrs.get("data-src") or attrs.get("src") or ""
        m = RECALL_PICTURE.search(src)
        if not m or m.group(0) in seen:
            continue
        seen.add(m.group(0))
        out.append((RECALLS_SITE + src if src.startswith("/") else src, clean(attrs.get("alt"))))
    return out


# Parts of a recall photo's alt text that are not the product's name: which side is shown, and sizes.
ALT_SIDE = re.compile(r"^((front|back|side|top|bottom)( view| panel)?( of (the )?(recalled )?(products?|package|"
                      r"packaging))?|product|recalled product|package|packaging)$", re.I)
ALT_SIZE = re.compile(r"^\d+([.,]\d+)?\s*(g|kg|mg|ml|l|oz|lb|lbs|units?|pack|count|ct)\b.*$", re.I)


def recall_product(alt, record):
    """The product's name from a photo's alt text ("Front of product - FTVN Series Boiler" -> "the FTVN Series
    Boiler"; "Tahineh - 800 g - Front" -> "the Tahineh"), else the notice's product field (its first sentence);
    ""."""
    text = html.unescape(clean(alt))
    parts = [p.strip(" .") for p in re.split(r"\s+[-–]\s+", text) if p.strip(" .")]
    parts = [p for p in parts if not ALT_SIDE.match(p) and not ALT_SIZE.match(p)]
    text = ", ".join(parts)
    text = re.sub(r"\s+(front|back|side|top)( view)?$", "", text, flags=re.I)
    text = re.sub(r"^(the )?recalled\s+", "", text, flags=re.I).strip(" .")
    if not text or len(text.split()) > 14:
        text = re.split(r"(?<=[.;])\s", html.unescape(clean(record.get("Product"))))[0].strip(" .;")
    if not text or len(text.split()) > 14:
        return ""
    return text if text.lower().startswith(("the ", "a ", "an ")) else f"the {text}"


def recall_rows(record, pictures):
    """[(file name, address, row)] for one recall notice's photos: "What product is this?" and, when the notice
    names its issue, "Why was this product recalled?"; [] for children's clothing, sleepwear and anything in
    NOT_SHOWN."""
    words = " ".join(clean(record.get(k)) for k in ("Title", "Product", "Issue"))
    if NOT_SHOWN.search(words):
        return []
    child = bool(CHILD_WORDS.search(words))
    if child and CHILD_CLOTHES.search(words):
        return []
    issue = clean(record.get("Issue"))
    credit = f"Health Canada, Recalls and Safety Alerts: {clean(record.get('Title'))[:120]}, {record.get('URL')}"
    items = []
    for n, (url, alt) in enumerate(pictures[:3]):
        product = recall_product(alt, record)
        if not product or RECALL_DETAIL.search(alt) or NOT_SHOWN.search(alt):
            continue
        base = {"split": "", "credit": credit, "place": CANADA, "place_kind": "market",
                **({"child": True} if child else {})}
        name = f"carecall-{record.get('NID')}-{n}.jpg"
        items.append((name, url, dict(base, question=PRODUCT_Q, answer=f"This is {product}.")))
        if issue:
            items.append((name, url, dict(base, question=RECALL_Q,
                                          answer=f"It was recalled in Canada for this reason: {issue}.")))
    return items


def prepare_ca_recalls(source, data_dir, work, cap):
    """Health Canada recall photos: the open list (OGL) read once, consumer-product and food recalls chosen at
    random, each recall's page read (gently, two seconds apart) for its product photos."""
    import requests
    want = int((cap + source.test) * 1.2)
    records = [r for r in get_json(RECALLS_JSON) if RECALL_KINDS.match(r.get("Category") or "")
               and "/alert-recall/" in (r.get("URL") or "")]
    random.Random("ca-recalls").shuffle(records)
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    items = []
    for record in records:
        if len({i[0] for i in items}) >= want:
            break
        try:
            page = s.get(record["URL"], timeout=60)
        except Exception:  # noqa: BLE001 - that recall is left out
            continue
        if page.status_code == 200:
            items += recall_rows(record, recall_pictures(page.text))
        time.sleep(2)
    say(f"  Health Canada recalls: {len({i[0] for i in items})} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

CANADA_SOURCES = [
    # ---- share-alike
    Source("commons_ca_sa", "Wikimedia Commons: Canadian houses, streets, signs, shops, holidays, transit and public "
                            "places, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2500, 25, prepare_commons_ca_sa, "about 350 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("openfacts_ca", "Open Food Facts: products sold in Canada, their name, brand and size (share-alike)",
           "Photos CC BY-SA 3.0, database ODbL 1.0 (https://world.openfoodfacts.org/terms-of-use)",
           "Open Food Facts contributors, photos CC BY-SA 3.0, data ODbL 1.0, each product credited in its row, "
           "https://world.openfoodfacts.org", "share-alike", 2500, 25,
           prepare_openfacts_ca, "about 450 MB of product records (read once, shared by the Open Food Facts "
           "entries) and 1 GB of photos", terms="https://world.openfoodfacts.org/terms-of-use",
           terms_summary="CC BY-SA 3.0 photos and an ODbL database: use with credit, and anything made from them "
                         "keeps the same licence."),
    Source("inaturalist_ca_sa", "iNaturalist: wild plants and animals in each Canadian province and territory, "
                                "photos under CC BY-SA (share-alike)",
           "Each photo CC BY-SA (its observation page; https://www.inaturalist.org/pages/terms)",
           "iNaturalist contributors, CC BY-SA, each credited in its row, https://www.inaturalist.org",
           "share-alike", 800, 10, prepare_inaturalist_ca_sa, "about 120 MB",
           terms="https://www.inaturalist.org/pages/terms",
           terms_summary="CC BY-SA: use with credit, and anything made from it keeps the same licence."),
    # ---- non-commercial
    Source("inaturalist_ca_nc", "iNaturalist: wild plants and animals in each Canadian province and territory, "
                                "photos under CC BY-NC (personal use)",
           "Each photo CC BY-NC, BY-NC-SA or BY-NC-ND (its observation page)",
           "iNaturalist contributors, CC BY-NC (and NC-SA, NC-ND), each credited in its row, "
           "https://www.inaturalist.org", "noncommercial", 4000, 30, prepare_inaturalist_ca_nc, "about 550 MB",
           terms="https://www.inaturalist.org/pages/terms",
           terms_summary="CC BY-NC: use with credit, not for commercial purposes."),
    Source("montreal_archives", "Old photographs of Montreal with French captions (Archives de la Ville de Montréal, "
                                "personal use)",
           f"CC BY-NC-SA 4.0 ({MTL_PAGE}); credit 'Archives de la Ville de Montréal'",
           "Archives de la Ville de Montréal, Archives photographiques (sélection), CC BY-NC-SA 4.0, " + MTL_PAGE,
           "noncommercial", 110, 5, prepare_montreal_archives, "about 30 MB",
           terms="https://creativecommons.org/licenses/by-nc-sa/4.0/",
           terms_summary="CC BY-NC-SA 4.0: use with credit ('Archives de la Ville de Montréal'), not for commercial "
                         "purposes, and anything made from it keeps the same licence."),
    Source("cra_forms", "Blank Canada Revenue Agency forms: TD1, T2201 and others (personal use)",
           f"Government of Canada terms: non-commercial reproduction allowed without permission ({CANADA_TERMS})",
           "Canada Revenue Agency forms, https://www.canada.ca/en/revenue-agency/services/forms-publications.html, "
           "reproduced for non-commercial use", "noncommercial", 60, 4, prepare_cra_forms,
           "about 20 MB (needs pypdfium2)", terms=CANADA_TERMS,
           terms_summary="Government of Canada: 'you may reproduce the materials in whole or in part for "
                         "non-commercial purposes ... without charge or further permission'; commercial "
                         "redistribution needs written permission."),
    # ---- research
    Source("ca_recalls", "Canadian product and food recall photos (Health Canada Recalls and Safety Alerts): which "
                         "product, and why it was recalled (personal use)",
           f"The list is open data (Open Government Licence - Canada, {RECALLS_DATASET}); the photos are on canada.ca "
           f"pages (non-commercial reproduction, {CANADA_TERMS}) and many belong to the recalling companies",
           "Health Canada and the Canadian Food Inspection Agency, Recalls and Safety Alerts, "
           "https://recalls-rappels.canada.ca, each recall credited in its row", "research", 2000, 20,
           prepare_ca_recalls, "about 300 MB", terms=CANADA_TERMS,
           terms_summary=research("Government of Canada: non-commercial reproduction allowed; 'Some of the content "
                                  "on this site may be subject to the copyright of another party' (recall photos "
                                  "often come from the companies).")),
]

# The collections a picture-making model may learn from: product photos and blank forms, without people.
CANADA_PICTURE_MAKING_OK = {"openfacts_ca", "cra_forms"}

CANADA_SIGN_UP = {
    "Canadian Armed Forces imagery (Combat Camera) on DVIDS":
        "https://www.dvidshub.net (search 'Canadian Armed Forces Combat Camera'): DVIDS's API needs a free key (as "
        "archive_packs.py notes). The pictures are Crown copyright of National Defence, which allows 'personal or "
        "public non-commercial use' (https://www.canada.ca/en/department-national-defence/corporate/intellectual-"
        "property/crown-copyright.html): a non-commercial entry once a key is in the repository secrets "
        "(DVIDS_API_KEY).",
    "Bank of Canada bank-note image gallery":
        "https://www.bankofcanada.ca/banknotes/using-bank-note-images/bank-notes-multimedia/ : 'For non-commercial "
        "uses of this nature, we provide a gallery of images that can be reproduced without obtaining the Bank's "
        "permission' if 'The images are reproduced accurately and without alterations' and the source is cited "
        "('Source: Bank of Canada'). A few dozen images on a web page with no list a program can read: download "
        "them yourself into the own-pictures folder (personal use).",
    "Flickr: Government of Canada, provinces and cities (Parks Canada, Canadian Heritage, Archives of Ontario, "
    "City of Vancouver Archives' Flickr copies)":
        "Flickr's API terms forbid storing the photos (as us_modern_sources.py explains); not built.",
    "Roboflow Universe Canadian sets (Canadian coins, Canadian road signs, Canadian banknotes)":
        "https://universe.roboflow.com (search 'canadian coins', 'canadian road signs'): a free Roboflow account and "
        "API key; check each set's licence and where its photos came from.",
}

CANADA_NOT_INCLUDED = {
    "Library and Archives Canada Collection Search (recherche-collection-search.bac-lac.gc.ca)":
        "refused this machine (403) in November 2026; LAC's photos come from their Commons copies instead "
        "(packs/canada_packs.py commons_ca_archives). LAC gives rights item by item (many 'Copyright: Expired').",
    "Canadian Register of Historic Places (historicplaces.ca) and Parks Canada's Federal Heritage Buildings Review "
    "Office (the HABS equivalent)":
        "historicplaces.ca's photos are supplied by the provinces, territories and towns, each with its own "
        "copyright, and the site states no open licence or list for programs; Parks Canada's photos are Crown "
        "copyright under the canada.ca terms (non-commercial), not the Open Government Licence (as "
        "documentary_packs.py notes). Canadian houses come from Commons (commons_ca_homes).",
    "NRC Archives Photographs (National Research Council, 12,944 photos, open.canada.ca dataset 2a097b38-...)":
        "the dataset is listed under the Open Government Licence - Canada, but each photo's own page says 'To "
        "request a license to reproduce the work on this website for commercial purposes, please contact the NRC "
        "Archives' (so non-commercial at most), and the records give only titles ('Space Research Facility "
        "Equipment 013'), not descriptions. In CANADA_PERMISSION_CANDIDATES.",
    "Natural Resources Canada, Geological Survey of Canada photo collections (the USGS equivalent)":
        "open.canada.ca lists NRCan's maps, air photos (the National Air Photo Library: vertical aerial photos with "
        "no description) and geoscience data under the OGL, but no captioned ground-photo collection; "
        "natural-resources.canada.ca has no list a program can read.",
    "Health Canada Drug Product Database (the C3PI equivalent)":
        "open data (OGL) with every drug's name, strength and maker, but no pictures of pills or packages; the "
        "makers' product monographs are PDFs without pill photos.",
    "Transport Canada Vehicle Recalls Database (OGL)": "recall data only, no photos.",
    "City of Vancouver Archives (searcharchives.vancouver.ca)": "refused this machine (403) in November 2026.",
    "City of Toronto open data, Ville de Montréal aerial photo sets": "Toronto's portal has no photo collection; "
                                                                     "Montréal's aerial photos are vertical survey "
                                                                     "pictures without descriptions.",
    "ISED Radio Equipment List (sms-sgs.ic.gc.ca)":
        "its robots.txt says 'User-agent: * Disallow: /', and it has no open data download or API; not for "
        "pictures in any case (see the toolkit proposal in the report).",
    "Loblaw (PC Express), Sobeys (Voilà), Metro, Walmart.ca, Canadian Tire, Amazon.ca (product photos)":
        "their terms forbid scraping and copying, and the photos are the makers' or shops' copyright; in "
        "CANADA_PERMISSION_CANDIDATES.",
    "Realtor.ca (CREA), Centris, Zillow Canada (house listings)":
        "their terms forbid scraping, the listing photos belong to agents and photographers, and the interiors are "
        "private homes.",
    "Alberta, Ontario and British Columbia government forms":
        "their sites allow non-commercial copies of unaltered forms only (Alberta's forms site: commercial "
        "redistribution 'is prohibited without written permission'), like the federal forms; the federal CRA forms "
        "are the cra_forms entry.",
    "Ingenium (Canada Science and Technology Museum) artifact pictures":
        "CC BY-NC-ND (the OGL covers only its records), as extra_sources.py notes; NoDerivatives pictures cannot "
        "be given new descriptions.",
}

CANADA_NOT_INCLUDED.update({
    "Archives of Ontario images beyond its own Commons upload (data.ontario.ca 'Archives of Ontario photographs and "
    "maps')":
        "the open-data record is under the Open Government Licence - Ontario but says 'The dataset does not include "
        "actual digitized images ... Please note that the actual images are not published under the Open "
        "Government Licence.' Only the files the Archives itself released on Commons under OGL-ON are used "
        "(packs/canada_packs.py commons_ca_provincial).",
    "Provincial open-data portals (data.ontario.ca, catalogue.data.gov.bc.ca, open.alberta.ca, donneesquebec.ca)":
        "searched for photo collections in November 2026: only aerial and orthophoto imagery (vertical survey "
        "pictures with no description), highway-camera data without a licence ('notspecified') and Montréal's "
        "archive selection (the montreal_archives entry). No provincial ministry (transportation, parks, agriculture, "
        "health, emergency management) publishes a captioned photo gallery under its open licence there; their "
        "Flickr streams cannot be used (Flickr's API terms).",
    "Indigenous community life":
        "the owner's rule: only from community-approved or openly licensed sources, and nothing sacred or "
        "ceremonial unless the source says it may be shared. No Indigenous community's or organisation's own "
        "archive with an open licence and sharing permission was found; Commons' 'Indigenous peoples in Canada' "
        "is openly licensed but not community-approved and mixes ceremonies, regalia and named people, so it is not "
        "taken (the daily-life pack also leaves out sacred and ceremonial words). Candidates to ask are in "
        "CANADA_PERMISSION_CANDIDATES.",
})

CANADA_PERMISSION_CANDIDATES = {
    "Indigenous community archives and media (for example the Inuit Heritage Trust, the Shingwauk Residential "
    "Schools Centre, APTN, Indigenous Services Canada's photo library)":
        "Have: photographs of everyday community life chosen by the communities. Ask each first, saying what is "
        "wanted (everyday scenes only, described for blind people, credited) and asking which pictures may be "
        "shared; nothing sacred or ceremonial unless they say so. (Contacts not checked from this machine.)",
    "Provincial ministries with Crown-copyright photo libraries (BC Parks, Ontario Parks, provincial transportation "
    "and ferry services)":
        "Have: photos of parks, roads, ferries and services. Terms: Crown copyright of the province unless a page "
        "says otherwise (not checked page by page from this machine). Ask each ministry's communications office "
        "for release under its province's Open Government Licence.",
    "Library and Archives Canada":
        "Has: millions of photographs of Canadian life with captions (rights item by item). Ask (bulk access for "
        "describing pictures for blind people): https://library-archives.canada.ca/eng/services/public/"
        "consult-copy/pages/default.aspx (copy and reproduction services) or the general contact page "
        "https://library-archives.canada.ca/eng/corporate/contact-us/pages/contact-us.aspx.",
    "Health Canada (Recalls and Safety Alerts)":
        "Has: the recall photos of consumer products and food (the kit's ca_recalls entry, research only). Terms: "
        "canada.ca, non-commercial; third-party photos. Ask: https://recalls-rappels.canada.ca/en/contact-us.",
    "Canada Revenue Agency (Crown copyright of its forms)":
        "Has: every federal tax form. Terms: canada.ca, non-commercial reproduction only. Ask for an open licence "
        "for the blank forms: https://www.canada.ca/en/revenue-agency/corporate/contact-information.html.",
    "Bank of Canada and the Royal Canadian Mint":
        "Have: images of every current bank note and coin. Terms: 'The Bank of Canada is the registered copyright "
        "owner of all design elements of Canadian bank notes' and 'Commercial users must obtain the Bank's "
        "permission'; it 'will also consider giving permission ... for educational, archival, museum, numismatic "
        "or related purposes' (https://www.bankofcanada.ca/banknotes/using-bank-note-images/). Ask: "
        "https://www.bankofcanada.ca/banknotes/using-bank-note-images/submit-a-bank-note-image-reproduction-"
        "request/ ; the Mint: https://www.mint.ca/en/contact-us.",
    "National Research Council Canada (NRC Archives Photographs)":
        "Has: 12,944 historic photographs (see CANADA_NOT_INCLUDED). Ask: NRC.DR-DN.CNRC@nrc-cnrc.gc.ca (the "
        "address on each photo's page).",
    "Loblaw Companies, Sobeys, Metro (grocers) and Canadian Tire":
        "Have: product photos with names, brands and sizes, and bilingual labels. Terms: their sites forbid "
        "scraping. Ask their media or accessibility contacts (Loblaw: https://www.loblaw.ca/en/contact-us).",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one Canada collection.")
    parser.add_argument("key", choices=[s.key for s in CANADA_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in CANADA_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="canada-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
