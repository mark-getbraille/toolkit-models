"""MODERN PACKAGED GOODS for the Picture Model Training Kit: the collections that cannot be ready-made packs because of
their terms, and the ones that need a sign-up, need permission, or were looked at and left out. The open ones (Amazon
Berkeley Objects catalogue photos of packaged goods, and Open Images photos with a packaging label) are packs in
packs/packaged_goods_packs.py (abo_packaged_goods, open_images_packaged_goods).

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link and the terms line are in each entry).

Groups (Source.group, as in sources.py):
  "research"  personal, non-commercial use only (the personal-use box, Alt+Z, after agreeing to the terms).

The collections (PACKAGED_GOODS_SOURCES):
  research
    fda_recall_photos  US Food and Drug Administration recall notices (fda.gov, "Recalls, Market Withdrawals, & Safety
                       Alerts"): the product photos of food, drink, dietary supplement, medicine, cosmetic and pet
                       food recalls, with the photo's own alt text, which usually reads the package's printed name,
                       size and dates ("Priano Protein Carbonara Tortelloni, Net Wt. 9 oz, Best if used by
                       12/18/2026"), the notice's brand, and why it was recalled. FDA's website policy says its own
                       text and graphics are public domain "unless otherwise noted", but each notice is marked
                       "COMPANY ANNOUNCEMENT ... FDA posts the company's announcement as a public service": the photos
                       are the recalling firms' own, so (as the CPSC and Health Canada recall photos in us_sources.py
                       and canada_sources.py) they are for personal use only until the firms agree. fda.gov's
                       robots.txt asks robots to wait 30 seconds between pages, so this reader is slow on purpose.

Answers are fixed sentences from each notice's own words, never written by an AI model. Answers about a medicine or a
dietary supplement end with pill_packs' line "Check the packaging or ask a pharmacist to be sure." Recalls of medical
devices, biologics and tobacco are left out, and so is anything whose words name sexual products. None of these
collections is used for picture-making (PACKAGED_GOODS_PICTURE_MAKING_OK is empty).

Needing sign-up or a manual download (PACKAGED_GOODS_SIGN_UP), permission candidates
(PACKAGED_GOODS_PERMISSION_CANDIDATES), and looked at but not included (PACKAGED_GOODS_NOT_INCLUDED, with the
reason).

    python kit/packaged_goods_sources.py fda_recall_photos --cap 4      (from the kit folder: a quick check)
"""

import html
import os
import random
import re
import time

from extra_sources import USER_AGENT, research, say
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import Source, clean

PRODUCT_Q = "What product is this?"
RECALL_Q = "Why was this product recalled?"
SAFETY = "Check the packaging or ask a pharmacist to be sure."

# ----------------------------------------------------------------- research: FDA recall photos

FDA_SITE = "https://www.fda.gov"
FDA_LIST = FDA_SITE + "/datatables/views/ajax"
FDA_LIST_PARAMS = {"search_api_fulltext": "", "field_regulated_product_field": "All", "draw": "1",
                   "view_name": "recall_solr_index", "view_display_id": "recall_datatable_block_1"}
FDA_TERMS = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_PAUSE = 30           # fda.gov's robots.txt: "Crawl-Delay: 30"
# The recall kinds taken (the listing's "product type" words): packaged goods, not devices, biologics or tobacco.
FDA_KINDS = re.compile(r"\b(Food & Beverages|Dietary Supplements|Drugs|Cosmetics|Animal & Veterinary|Pet Food)\b")
FDA_NOT_KINDS = re.compile(r"\b(Medical Devices|Biologics|Tobacco)\b")
FDA_MEDICINE = re.compile(r"\b(Drugs|Dietary Supplements)\b")
# The product photos on a notice's page (each <img> of the "recall_image" styles), and their alt text.
FDA_PICTURE = re.compile(r"/files/styles/recall_image_\w+/public/([^\"'?]+\.(?:jpe?g|png))", re.I)
# Alt texts that are not about the product as a whole: a code, a lot number, a side, or nothing.
FDA_DETAIL = re.compile(r"^(image|photo|picture|product (image|photo|label)|label|front|back|side|top|bottom|"
                        r"lot( code| number)?s?|upc|barcode)\b[\s\d:.-]*$|^\s*$", re.I)
NOT_SHOWN = re.compile(r"\b(condoms?|lubricants?|sexual\w*|sexy|erotic\w*|male enhancement|enhancement pills?|"
                       r"sildenafil|tadalafil|vardenafil|libido|aphrodisiac\w*|vibrators?|nude|naked)\b", re.I)


def text_of(cell):
    """The plain text of one HTML cell of the listing (tags removed, entities read, spaces tidied)."""
    return clean(html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(str(cell or "")))))


def fda_listing(rows):
    """The FDA recall listing's rows (lists of HTML cells) as dicts: {"url", "brand", "product", "kinds", "reason",
    "company", "date"}; rows that name no page are left out."""
    out = []
    for cells in rows:
        cells = list(cells) + [""] * 8
        link = re.search(r'href="([^"]+)"', html.unescape(cells[1] or ""))
        if not link:
            continue
        url = link.group(1) if link.group(1).startswith("http") else FDA_SITE + link.group(1)
        date = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', html.unescape(cells[0] or ""))
        out.append({"url": url, "brand": text_of(cells[1]), "product": text_of(cells[2]), "kinds": text_of(cells[3]),
                    "reason": text_of(cells[4]), "company": text_of(cells[5]), "date": date.group(1) if date else ""})
    return out


def fda_wanted(record):
    """True for a recall of packaged goods (food, drink, supplements, medicines, cosmetics, pet food) whose words
    name nothing left out."""
    words = " ".join(record.get(k, "") for k in ("brand", "product", "reason"))
    return bool(FDA_KINDS.search(record.get("kinds", ""))) and not FDA_NOT_KINDS.search(record.get("kinds", "")) \
        and not NOT_SHOWN.search(words)


def fda_pictures(page_html):
    """[(picture address, its alt text)] of the product photos on one notice's page, each once, at full size
    (/files/<name> rather than the small style)."""
    out, seen = [], set()
    for tag in re.findall(r"<img\b[^>]*>", page_html, re.I):
        m = FDA_PICTURE.search(tag)
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        alt = re.search(r'\balt="([^"]*)"', tag)
        out.append((f"{FDA_SITE}/files/{m.group(1)}", html.unescape(clean(alt.group(1) if alt else ""))))
    return out


def fda_product(alt, record):
    """What the answer names: the photo's own alt text (it usually reads the label: name, size, dates) when it says
    more than a side or a code, else the notice's brand and product; "" when neither says anything."""
    text = re.sub(r"^(an? |the )?(image|photo|picture)( of)?\s+", "", clean(alt), flags=re.I)
    text = re.sub(r"^(the )?recalled\s+", "", text, flags=re.I).strip(" .")
    if text and not FDA_DETAIL.match(text) and len(text.split()) <= 40:
        return text
    named = " ".join(w for w in (record.get("brand", ""), record.get("product", "")) if w).strip(" .")
    return named if named and len(named.split()) <= 30 else ""


def fda_rows(record, pictures):
    """[(file name, address, row)] for one notice's photos: "What product is this?" and, when the notice gives a
    reason, "Why was this product recalled?"; [] for a recall this collection does not take."""
    if not fda_wanted(record):
        return []
    words = " ".join(record.get(k, "") for k in ("brand", "product"))
    child = bool(CHILD_WORDS.search(words))
    medicine = bool(FDA_MEDICINE.search(record.get("kinds", "")))
    slug = re.sub(r"[^a-z0-9]+", "-", record["url"].rsplit("/", 1)[-1].lower())[:60].strip("-")
    credit = (f"US Food and Drug Administration, recall notice (company announcement) of {record.get('company') or 'the firm'}"
              f", {record.get('date', '')}: {record['url']}")
    reason = record.get("reason", "").strip(" .")
    items = []
    for n, (url, alt) in enumerate(pictures[:4]):
        if NOT_SHOWN.search(alt):
            continue
        product = fda_product(alt, record)
        if not product:
            continue
        brand = record.get("brand", "")
        answer = f"This is the recalled product: {product}."
        if brand and brand.lower() not in product.lower():
            answer += f" Brand: {brand}."
        if medicine:
            answer += f" {SAFETY}"
        base = {"split": "", "credit": credit, "place": "United States", "place_kind": "market",
                **({"child": True} if child else {})}
        name = f"fda-{slug}-{n}.jpg"
        items.append((name, url, dict(base, question=PRODUCT_Q, answer=answer)))
        if reason:
            items.append((name, url, dict(base, question=RECALL_Q,
                                          answer=f"It was recalled in the USA for this reason: {reason}.")))
    return items


def fda_records(s, most=2000):
    """The FDA recall listing (about 1,100 notices of the last years), read 500 at a time."""
    records, start = [], 0
    while start < most:
        r = s.get(FDA_LIST, params=dict(FDA_LIST_PARAMS, start=str(start), length="500"), timeout=120)
        r.raise_for_status()
        data = r.json()
        rows = data.get("data") or []
        records += fda_listing(rows)
        start += len(rows)
        if not rows or start >= int(data.get("recordsFiltered") or 0):
            break
        time.sleep(FDA_PAUSE)
    return records


def prepare_fda_recall_photos(source, data_dir, work, cap):
    """FDA recall photos: the listing read once, packaged-goods recalls chosen at random, each notice's page read
    30 seconds apart (fda.gov's robots.txt asks for that) for its product photos."""
    import requests
    want = int((cap + source.test) * 1.2)
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    try:
        records = [r for r in fda_records(s) if fda_wanted(r)]
    except Exception as e:  # noqa: BLE001 - said, and the collection is left out this time
        say(f"  FDA recalls: the listing could not be read ({type(e).__name__}); left out this time.")
        return []
    random.Random("fda-recalls").shuffle(records)
    say(f"  FDA recalls: {len(records)} packaged-goods notices; reading their pages, one every {FDA_PAUSE} seconds "
        f"(this is slow on purpose).")
    items = []
    for record in records:
        if len({i[0] for i in items}) >= want:
            break
        time.sleep(FDA_PAUSE)
        try:
            page = s.get(record["url"], timeout=60)
        except Exception:  # noqa: BLE001 - that notice is left out
            continue
        if page.status_code == 200:
            items += fda_rows(record, fda_pictures(page.text))
    say(f"  FDA recalls: {len({i[0] for i in items})} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=1)


# ----------------------------------------------------------------- the table

PACKAGED_GOODS_SOURCES = [
    Source("fda_recall_photos", "US food, drink, supplement, medicine and pet food recall photos (Food and Drug "
                                "Administration): the label, the brand, and why it was recalled (personal use)",
           "FDA text is public domain, but each notice is the recalling company's announcement, posted by FDA 'as a "
           "public service'; its photos are the company's (fda.gov website policies)",
           "US Food and Drug Administration recall notices (company announcements), each recall credited in its row, "
           "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts", "research", 300, 10,
           prepare_fda_recall_photos, "about 100 MB (slow: one page every 30 seconds)", terms=FDA_TERMS,
           terms_summary=research("fda.gov: its own text and graphics are public domain 'unless otherwise noted'; "
                                  "recall notices are 'COMPANY ANNOUNCEMENT ... FDA posts the company's "
                                  "announcement as a public service', so the photos belong to the recalling "
                                  "companies.")),
]

# None of these is used for picture-making.
PACKAGED_GOODS_PICTURE_MAKING_OK = set()

PACKAGED_GOODS_SIGN_UP = {
    "Smithsonian Open Access API (api.si.edu, NMAH packaging and product items, CC0)":
        "https://api.data.gov/signup/ : a free api.data.gov key. Not needed: the same CC0 records are in the "
        "key-free bulk files (smithsonian-open-access on AWS), which a full scan in November 2026 found to hold "
        "1,227 packaging-like CC0 records, only 5 of them from 1950 or later (the rest are 1700s-1800s apothecary "
        "jars and bottles). Not built.",
    "Holoselecta (Fuchs, Grundmann and Fleisch, ETH Zurich Auto-ID Labs, 2019; CC BY 4.0)":
        "https://github.com/tobiagru/ObjectDetectionGroceryProducts : 295 photos of Swiss vending machines with "
        "10,035 boxes of 109 products named by GTIN. Open (CC BY 4.0), but published only as a Google Drive folder "
        "(https://drive.google.com/open?id=1OofnsREqF1QNfUqZPZgcXu2VkWr2JUMA) whose listing a program cannot read "
        "in full. The owner can download it by hand and add it through the own-pictures folder.",
    "Retail-786k (Lamm and Keuper, 2023; Zenodo 7970567, CC BY-NC-ND 4.0)":
        "https://zenodo.org/records/7970567 : 786,000 cut-out product pictures from German retail leaflets, "
        "labelled only by product number. Non-commercial and NoDerivatives; no product names to learn from. Not "
        "built.",
    "MVTec D2S (CC BY-NC-SA 4.0)":
        "https://www.mvtec.com/company/research/datasets/mvtec-d2s : a download form; supermarket products on a "
        "turntable, labelled with 60 product classes. Personal use allowed once the owner fills the form: built as "
        "the local-file sign-up entry signup_sources.mvtec_d2s.",
    "Unitail, Locount, RP2K, Kaggle RPC": "request forms, e-mail or a Kaggle login; already in "
                                          "signup_sources.SIGNUP_NOT_INCLUDED.",
}

PACKAGED_GOODS_NOT_INCLUDED = {
    "USDA FSIS recall label images (fsis.usda.gov)":
        "fsis.usda.gov refused this machine (403) for its pages and its robots.txt. The label pictures FSIS posts are "
        "the establishments' own product labels (company artwork), so they would be personal use only even when "
        "reachable, like the CPSC and FDA recall photos. Not built; try from the owner's computer.",
    "CPSC recall photos (saferproducts.gov Recalls API)":
        "already the personal-use entry us_sources.cpsc_recalls: CPSC allows copying recall notices, but 'any "
        "other use of photographs ... may require permission from a copyright holder'.",
    "Health Canada recall photos (recalls-rappels.canada.ca)":
        "already the personal-use entry canada_sources.ca_recalls: the list is under the Open Government Licence - "
        "Canada, but the photos on each page are mostly the recalling firms' (the OGL leaves out third-party "
        "material).",
    "openFDA enforcement reports (api.fda.gov)":
        "public domain, but text only (no product photos); the photos are on the company announcements "
        "(fda_recall_photos).",
    "Smithsonian NMAH packaging (CC0)":
        "the CC0 open-access records hold almost no modern packaging (5 of 1,227 packaging-like records are from "
        "1950 or later; the rest are apothecary jars and 1800s bottles). Not built.",
    "Cooper Hewitt, Smithsonian Design Museum": "already the open cooper_hewitt entry (CC0 accessibility "
                                                "descriptions); its packaging is part of it.",
    "Te Papa (Museum of New Zealand) packaging":
        "of about 1,100 'packaging' records, the pictures are CC BY-NC-ND 4.0 (140), all rights reserved (321) or "
        "have none; only 7 are 'No Known Copyright Restrictions' (1800s). NoDerivatives and not modern: not built.",
    "Museums Victoria (Australia)":
        "its collections API refused this machine again (403); already the non-commercial kit entry "
        "signup_sources.museums_victoria, which reads it from the owner's computer.",
    "Powerhouse Museum (Sydney)":
        "api.maas.museum did not answer; the collection site's robots.txt says 'Disallow: /'. As in "
        "signup_sources.SIGNUP_NOT_INCLUDED.",
    "Ingenium (Canada Science and Technology Museum)":
        "robots.txt 'Content-Signal: ... ai-train=no'; pictures CC BY-NC-ND. Stays out.",
    "Science Museum Group (UK)":
        "robots.txt disallows /api/, /iiif/ and every address with '?'; pictures CC BY-NC-SA. Stays out.",
    "RISD Museum (Rhode Island School of Design)":
        "robots.txt 'Content-Signal: search=yes,ai-train=no,use=reference': an express reservation against AI "
        "training. Stays out.",
    "Hagley Museum and Library digital archives (trade catalogues)":
        "digital.hagley.org answers robots with a challenge page (even for robots.txt); the trade catalogues are "
        "mostly before 1960 and permission is asked for publication. Not built.",
    "Pratt, Parsons (The New School), ArtCenter archives":
        "not looked at one by one in this pass: no API, bulk download or open licence for their packaging "
        "collections is known (design-school archives are usually for research and reference, with permission "
        "needed for reproduction). Not built; worth a look from the owner's computer.",
    "Open Images V7 training set":
        "the human-checked training labels are a 2.7 GB list (and the image list another 2.7 GB) for a few "
        "thousand more generic photos ('a tin can'); the validation and test photos are the open "
        "open_images_packaged_goods pack.",
    "Products-10K (JD.com)":
        "research use only, and labelled by product number only (no names); already left out in "
        "personal_sources.REJECTED and signup_sources.SIGNUP_NOT_INCLUDED.",
    "SKU-110K, RPC, the Grocery Store Dataset, the Freiburg Groceries Dataset":
        "already covered (SKU-110K and RPC in the sign-up and rejected lists; grocery_store an open pack; "
        "freiburg_groceries a personal-use entry).",
    "GroZi-120 and GroZi-3.2k":
        "no licence stated (grozi.calit2.net does not answer; GroZi-3.2k is a Google Drive file with no terms); "
        "low-resolution shelf video frames labelled only by product number. Not built.",
    "Grocery Products dataset (Tonioni and Di Stefano, 2017)":
        "no licence stated; studio product pictures of an Italian shop labelled by category and product number "
        "only. Not built.",
    "Open Food, Beauty, Products and Pet Food Facts": "Open Food Facts is already the share-alike entries "
                                                      "openfacts_us and openfacts_ca (and openfoodfacts), read "
                                                      "through its bulk routes (off_dump.py); Open Beauty, Products "
                                                      "and Pet Food Facts are not built: the source blocks AI "
                                                      "crawlers.",
    "Walmart, Target, Kroger, Costco, Amazon.com product pages":
        "their terms forbid copying or scraping; already in us_sources.US_NOT_INCLUDED and "
        "US_PERMISSION_CANDIDATES. (Amazon's own open set is ABO, used.)",
}

PACKAGED_GOODS_PERMISSION_CANDIDATES = {
    "US Food and Drug Administration (recall photos)":
        "what: product photos of about 1,100 recall notices a year (food, supplements, medicines, pet food). Terms: "
        "the photos are the recalling companies' (company announcements). Ask: FDA's web team "
        "(https://www.fda.gov/about-fda/contact-fda) whether the photos may be used to train a picture describer "
        "for blind people, or the companies themselves.",
    "USDA Food Safety and Inspection Service (recall label images)":
        "what: the labels of every meat, poultry and egg product recall. Terms: the labels are the companies'. "
        "Ask: FSIS (https://www.fsis.usda.gov/contact-us).",
    "Te Papa (Museum of New Zealand)":
        "what: about 1,000 packaging objects, CC BY-NC-ND. Ask: Te Papa's collections online team "
        "(https://www.tepapa.govt.nz/about/contact-us) about using the pictures for an accessibility describer.",
}


def main(argv=None):
    """A quick check of one collection: python kit/packaged_goods_sources.py fda_recall_photos --cap 4"""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try one packaged-goods collection.")
    parser.add_argument("key", choices=[s.key for s in PACKAGED_GOODS_SOURCES])
    parser.add_argument("--cap", type=int, default=4)
    args = parser.parse_args(argv)
    source = next(s for s in PACKAGED_GOODS_SOURCES if s.key == args.key)
    with tempfile.TemporaryDirectory() as folder:
        rows = source.prepare(source, folder, folder, args.cap)
        for row in rows:
            print(json.dumps({k: v for k, v in row.items() if k != "picture"}, ensure_ascii=False))
    print(f"{len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
