"""MEDICINES, MEDICAL TOOLS AND SUPPLIES, and VETERINARY MEDICINES (the United States and Canada first) for the
Picture Model Training Kit: the collections that cannot be ready-made packs because of their licence, and the ones
that need a sign-up, need permission, or were looked at and left out. The open ones (Commons supplies, surgical
instruments, medicines and veterinary categories, the CC BY dental instrument photos, Open Images medical labels and
CDC PHIL supply photos) are packs in packs/med_vet_packs.py.

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link and the exact terms line are in each entry).

THE OWNER'S RULE: CURRENT ITEMS ONLY. Medical instruments, supplies and pills, human and veterinary, must be things in
use today: rows whose words suggest something old (a year before 2000, a decade before the 2000s, a century,
"antique", "historic", "vintage", "museum", "accession", "obsolete", "replica", "exhibit", "World War") or a
medicine the source says is discontinued or withdrawn are left out (OLD). DailyMed holds only the labels in use now
(its own words: "the most recent submitted labeling ... currently in use"). No museum medical collections at all.

Groups (Source.group, as in sources.py):
  "share-alike"  CC BY-SA, GFDL and ODbL: only with the share-alike choice (--with-wikipedia); an add-on trained with
                 them is CC BY-SA.
  "research"     personal use only, after agreeing to the terms (the personal-use box, Alt+Z).

Answers are fixed sentences from each source's own words (a Commons category's name, the product name people typed
into Open Food Facts, a DailyMed label's title), never written by an AI model. A medicine's answer always says "This
looks like ..." and ends with the safety line ("Check the packaging or ask a pharmacist to be sure."; for animals "...
ask a vet or pharmacist ..."): a model must never sound sure about a medicine. "What does the label say?" is not
asked: no source here gives a label's exact text.

Safety (packs/SOURCE-RULES.md): no sexual content (files and products whose words name nudity, condoms or personal
lubricants are left out); no patients, injuries, blood, operations or drug misuse; files whose words name a child are
left out; in the Commons entry, files whose words name a person are left out too, so every entry here shows the
things themselves and may be used for picture-making.

The collections (MED_VET_SOURCES):
  share-alike
    med_vet_commons_sa     Wikimedia Commons files under CC BY-SA or GFDL of the categories of the open Commons
                           packs (bandages, syringes, inhalers, first-aid kits, stethoscopes, surgical instruments,
                           pills, blister packs, pill bottles, vitamins, veterinary drugs). Captions CC0.
    openfacts_supplements  Open Food Facts: dietary supplements, vitamins, cough drops and throat lozenges sold in the
                           USA or Canada (a North American barcode), their name, brand and size; protein powders and
                           sports nutrition left out. Photos CC BY-SA 3.0, data ODbL 1.0
                           (https://world.openfoodfacts.org/terms-of-use). Read through off_dump.py (the product
                           database on Hugging Face, the photos on AWS Open Data), never the websites, which block
                           AI crawlers. Not in canada_sources.openfacts_ca or
                           us_sources (neither reads these categories; see the filter proposed in the report).
  research
    dailymed_human_labels  DailyMed (US National Library of Medicine): the package and label pictures of human
                           over-the-counter and prescription medicines as their makers submitted them to the FDA.
    dailymed_vet_labels    The same for animal drugs (over-the-counter and prescription veterinary labels): pet and
                           livestock dewormers, flea and tick products, antibiotics.
                           NLM's copyright page (https://www.nlm.nih.gov/web_policies.html): "Works produced by the
                           U.S. government are not subject to copyright protection", but "you may encounter documents,
                           illustrations, photographs, or other content contributed by or licensed from private
                           individuals, companies, or organizations that may be protected by U.S. and international
                           copyright laws", and "Transmission or reproduction of copyrighted items (beyond that
                           allowed by fair use ...) requires the written permission of the copyright holders". The
                           label pictures are the drug makers' own artwork: research, personal use only.

Needing sign-up (MED_VET_SIGN_UP), permission candidates (MED_VET_PERMISSION_CANDIDATES), and looked at but not
included (MED_VET_NOT_INCLUDED, with the reason and the terms line of each, including every public-media
organisation checked: NPR, PBS, GBH/WGBH and the American Archive of Public Broadcasting, CBC/Radio-Canada, TVO,
Knowledge Network, Télé-Québec, member stations and Voice of America).

MED_VET_PICTURE_MAKING_OK: every entry (no people by their words; packages and products only).

    python kit/med_vet_sources.py dailymed_vet_labels --cap 8      (from the kit folder: a quick check)
"""

import json
import os
import random
import re
import time

from extra_sources import get_json, off_name, per_label, research, say
from home_sources import commons_sa_items
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import Source, clean
from us_sources import off_us_front

WHAT_Q = "What is this?"
MEDICINE_Q = "What is this medicine?"
INSTRUMENT_Q = "What is this instrument?"
PRODUCT_Q = "What product is this?"
KIND_Q = "What kind of product is this?"
SAFETY = "Check the packaging or ask a pharmacist to be sure."
VET_SAFETY = "Check the packaging or ask a vet or pharmacist to be sure."

# ----------------------------------------------------------------- words that leave a picture out

# The owner's rule: current items only (as packs/med_vet_packs.OLD; a dose such as "1000 mg" is not a year).
DOSE = r"(?!\s?(mg|mcg|µg|ml|mL|g|iu|IU|units?|tablets?|capsules?|caplets?|count|ct|pieces|x)\b)"
OLD = re.compile(r"\b(1[0-8]\d\d|19\d\d)s?\b" + DOSE + r"|\b(19)?[1-9]0s\b|\b\d{1,2}(st|nd|rd|th)[- ]century\b|"
                 r"\b(antiques?|historic(al|ally)?|history of|vintage|museums?|accession\w*|catalogue (no|number)|"
                 r"circa|c\. ?1[5-9]\d\d|obsolete|old[- ]fashioned|replicas?|exhibit(s|ed|ion)?|world war|WWI+|"
                 r"civil war|victorian|edwardian|wellcome|smithsonian|army medical museum|discontinued|withdrawn|"
                 r"no longer (sold|made|available|marketed))\b|"
                 # museum accession numbers: "(AM 2017.92.14-13)", "1992.3.4", "inv. no. 123"
                 r"\b[A-Z]{1,4}\s?\d{2,4}\.\d{1,4}\.\d{1,4}|\b\d{4}\.\d{1,4}\.\d{1,4}\b|\binv(entory)?\.? ?no\b",
                 re.I)
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|underwear|lingerie|nude|naked|nudity|topless|sexy|sexual\w*|"
                       r"erotic\w*|porn\w*|condoms?|personal lubricants?|lubricating jelly)\b", re.I)
HARM = re.compile(r"\b(injur\w*|wounds?|wounded|blood(?![- ](glucose|sugar|pressure))\w*|bleed\w*|dead|deaths?|"
                  r"died|killed|corpses?|cadavers?|autops\w*|amputat\w*|patients?|surgery in progress|during "
                  r"(an? |the )?(surgery|operation)|operating (room|theat(er|re)|table)|incisions?|"
                  r"drug (abuse|users?)|illicit|heroin|fentanyl|cocaine|euthanas\w*)\b", re.I)
PERSON = re.compile(r"\b(man|men|woman|women|person|people|boy|boys|girl|girls|users?|workers?|selfie|portraits?|"
                    r"wearing|holding|he|she|his|her|him|they are|family|crowd\w*|dr|mr|mrs|ms|nurses?|doctors?|"
                    r"physicians?|paramedics?|surgeons?|dentists?|pharmacists?|veterinarians?|volunteers?|"
                    r"soldiers?|hands|fingers|faces)\b", re.I)


def left_out(words, people_ok=False):
    """True when a picture's words name nudity or sexual products, harm, a patient or misuse, a child, something
    old or discontinued (the owner's rule), or (unless people_ok) a person."""
    return bool(NOT_SHOWN.search(words) or HARM.search(words) or OLD.search(words) or CHILD_WORDS.search(words)
                or (not people_ok and PERSON.search(words)))


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

# (category, question, answer, also its subcategories): the categories of packs/med_vet_packs.py.
MED_VET_SA = [
    ("Bandages", WHAT_Q, "This is a bandage.", True),
    ("Adhesive bandages", WHAT_Q, "This is an adhesive bandage (a sticking plaster).", True),
    ("Medical tape", WHAT_Q, "This is medical tape.", True),
    ("Splints", WHAT_Q, "This is a splint.", False),
    ("Syringes", WHAT_Q, "This is a syringe.", True),
    ("Insulin pens", WHAT_Q, "This is an insulin pen.", False),
    ("Inhalers", WHAT_Q, "This is an inhaler.", True),
    ("Nebulizers", WHAT_Q, "This is a nebulizer.", True),
    ("Pill organizers", WHAT_Q, "This is a pill organizer.", False),
    ("First aid kits", WHAT_Q, "This is a first-aid kit.", True),
    ("Stethoscopes", WHAT_Q, "This is a stethoscope.", True),
    ("Pulse oximeters", WHAT_Q, "This is a pulse oximeter.", False),
    ("Hospital beds", WHAT_Q, "This is a hospital bed.", True),
    ("Automated external defibrillators", WHAT_Q, "This is an AED (automated external defibrillator).", True),
    ("Surgical masks", WHAT_Q, "This is a surgical mask.", True),
    ("Medical gloves", WHAT_Q, "These are medical gloves.", True),
    ("Scalpels", INSTRUMENT_Q, "This is a scalpel.", True),
    ("Surgical forceps", INSTRUMENT_Q, "This is a pair of surgical forceps.", True),
    ("Surgical scissors", INSTRUMENT_Q, "This is a pair of surgical scissors.", False),
    ("Needle holders", INSTRUMENT_Q, "This is a needle holder.", False),
    ("Pills", WHAT_Q, "These are pills.", True),
    ("Tablets (pharmacy)", WHAT_Q, "These are tablets.", True),
    ("Capsules (pharmacy)", WHAT_Q, "These are capsules.", True),
    ("Blister packs", WHAT_Q, "This is a blister pack of pills.", True),
    ("Pill bottles", WHAT_Q, "This is a pill bottle.", True),
    ("Medicine bottles", WHAT_Q, "This is a medicine bottle.", True),
    ("Vials", WHAT_Q, "This is a vial of medicine.", True),
    ("Vitamins", WHAT_Q, "These are vitamins.", True),
    ("Dietary supplements", WHAT_Q, "This is a dietary supplement.", True),
    ("Ibuprofen", MEDICINE_Q, f"This looks like ibuprofen, a medicine for pain, fever and swelling. {SAFETY}", True),
    ("Paracetamol", MEDICINE_Q, f"This looks like acetaminophen (paracetamol), a medicine for pain and fever. "
                                f"{SAFETY}", True),
    ("Aspirin", MEDICINE_Q, f"This looks like aspirin, a medicine for pain and fever. {SAFETY}", True),
    ("Veterinary drugs", MEDICINE_Q, f"This looks like a veterinary medicine, made for animals. {VET_SAFETY}", True),
    ("Veterinary instruments", INSTRUMENT_Q, "This is a veterinary instrument.", True),
]


def sa_items(specs, cap, test, prefix):
    """home_sources.commons_sa_items (files under CC BY-SA or GFDL, the categories sharing the cap, children left
    out), without the files whose words name nudity, harm or a patient, something old, or a person: every row of
    such a file goes."""
    items = commons_sa_items(specs, cap, test, prefix, adults_only=True)
    bad = {name for name, _, row in items if left_out(f"{name} {row['answer']}")}
    if bad:
        say(f"  {len(bad)} files left out by their words")
    return [i for i in items if i[0] not in bad]


def prepare_med_vet_commons_sa(source, data_dir, work, cap):
    """Commons medical supply, instrument, medicine and veterinary categories, files under CC BY-SA or GFDL."""
    items = sa_items(MED_VET_SA, cap, source.test, "medvet-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: Open Food Facts supplements

# (Open Food Facts category tag, the plain words for "What kind of product is this?").
SUPPLEMENT_KINDS = [("dietary-supplements", "a dietary supplement"), ("vitamins", "vitamins"),
                    ("cough-drops", "cough drops"), ("throat-lozenges", "throat lozenges")]
NOT_SUPPLEMENTS = re.compile(r"\b(protein|whey|creatine|pre-?workout|mass gainer|bcaa|sports? nutrition|energy "
                             r"drink|bars?|hydration|electrolytes?|sports drinks?)\b", re.I)
COUNTRIES = (("united-states", "USA"), ("canada", "Canada"))
SUPPLEMENT_CREDIT = "Open Food Facts contributors, product {code}: photos CC BY-SA 3.0, data ODbL 1.0, " \
                    "https://world.openfoodfacts.org/product/{code}"


def north_american_barcode(code):
    """True for a barcode sold on US and Canadian shelves: a UPC (GS1 prefixes 000 to 139) or a GS1 Canada EAN
    (754, 755)."""
    code = str(code or "")
    if not code.isdigit() or len(code) not in (12, 13):
        return False
    prefix = code.zfill(13)[:3]
    return prefix <= "139" or prefix in ("754", "755")


def supplement_rows(hit, kind, country):
    """[(file name, address, row)] for one Open Food Facts product: "What product is this?" (its name, brand and
    size) and "What kind of product is this?"; [] for a product without a North American barcode, an English front
    photo or a name, for protein powders and sports nutrition, and for words that leave it out."""
    code = hit.get("code") or ""
    url = off_us_front(code, hit.get("images")) if north_american_barcode(code) else ""
    answer = off_name(hit)
    tags = " ".join(hit.get("categories_tags") or [])
    if not url or not answer or NOT_SUPPLEMENTS.search(f"{answer} {tags}") or left_out(answer, people_ok=True):
        return []
    extra = {"split": "", "credit": SUPPLEMENT_CREDIT.format(code=code), "place": country, "place_kind": "market"}
    name = f"off-supplement-{code}.jpg"
    return [(name, url, dict(extra, question=PRODUCT_Q, answer=answer)),
            (name, url, dict(extra, question=KIND_Q, answer=f"It is {kind}."))]


def prepare_openfacts_supplements(source, data_dir, work, cap):
    """Open Food Facts supplements, vitamins, cough drops and lozenges sold in the USA and in Canada, the most
    scanned first, an even share of each kind and country. Read from the product database's slim copy (off_dump:
    the database on Hugging Face, the photos on AWS Open Data), never from Open Food Facts' websites, which block AI
    crawlers. A product is taken once, for the first kind and country it is picked for."""
    import off_dump
    per = per_label(int((cap + source.test) * 1.2), len(SUPPLEMENT_KINDS) * len(COUNTRIES))

    def labels(hit):
        """The (kind, country) pairs a product counts for: its supplement categories and its countries of sale,
        when supplement_rows takes it."""
        tags, countries = set(hit["categories_tags"]), set(hit["countries_tags"])
        return [(tag, country) for tag, kind in SUPPLEMENT_KINDS for country_tag, country in COUNTRIES
                if f"en:{tag}" in tags and f"en:{country_tag}" in countries and supplement_rows(hit, kind, country)]

    best = off_dump.top_by_label(work, labels, per * 2)
    items, seen = [], set()
    for tag, kind in SUPPLEMENT_KINDS:
        for _, country in COUNTRIES:
            got = 0
            for hit in best.get((tag, country), []):
                if got < per and hit["code"] not in seen:
                    seen.add(hit["code"])
                    items += supplement_rows(hit, kind, country)
                    got += 1
            say(f"  Open Food Facts {tag} ({country}): {got} products")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- research: DailyMed package labels

DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/services/v2/"
DAILYMED_TERMS = "https://www.nlm.nih.gov/web_policies.html"
# DailyMed's document types (LOINC codes): human over-the-counter and prescription labels, animal ones.
HUMAN_DOCTYPES = (("34390-5", "an over-the-counter medicine"), ("34391-3", "a prescription medicine"))
ANIMAL_DOCTYPES = (("50577-6", "an over-the-counter animal medicine"), ("50578-4", "a prescription animal medicine"))
# Media whose names show a package or a label; and those that show a chemical structure, a chart or a table.
PACKAGE_PICTURE = re.compile(r"(label|carton|package|packaging|pdp|principal|display|box|bottle|container|blister|"
                             r"pouch|tube|vial|front|panel|bag|jar|can|pack|sachet|syringe|applicator|tub)", re.I)
NOT_PACKAGE = re.compile(r"(structure|struct|chem|formula|figure|fig\d|graph|chart|table|diagram|curve|plot|"
                         r"molecule|image\d{2,}|logo)", re.I)
# Kinds of over-the-counter product that would otherwise fill the entry (thousands of hand sanitizers and
# sunscreens were listed from 2020): at most one in ten.
CROWDED = re.compile(r"\b(hand sanitizer|sanitizing|antiseptic hand|alcohol (gel|wipes?)|sunscreen|spf ?\d+)\b",
                     re.I)
# Cosmetics and toiletries that the FDA lists as over-the-counter drugs (hair dyes, lotions, toothpastes, soaps,
# make-up with sunscreen): not medicines as people mean the word, so left out.
COSMETIC = re.compile(r"\b(hair|cosmetics?|make-?up|foundation|lipsticks?|lip (balm|gloss)|toothpaste|mouthwash|"
                      r"mouth rinse|soaps?|body (wash|care|lotion)|moisturi[sz]\w*|beauty|skin ?care|serum|bb cream|"
                      r"cushion|concealer|primer|whitening|tooth|dental|deodorant|antiperspirant|perfume|"
                      r"fragrance|shaving|bath)\b", re.I)
UNITS = {"MG": "mg", "MCG": "mcg", "ML": "ml", "G": "g", "IU": "IU", "KG": "kg", "HCL": "HCl", "USP": "USP",
         "NF": "NF", "LLC": "LLC", "INC": "Inc", "LTD": "Ltd", "CO": "Co", "SPF": "SPF", "OTC": "OTC", "II": "II"}


def readable(text):
    """A DailyMed title's capitals in readable case ("FAST SOLD LLC" -> "Fast Sold LLC", "10 MG" -> "10 mg")."""
    words = []
    for word in clean(text).split():
        core = word.strip(".,;:()")
        fixed = UNITS.get(core.upper()) or "".join(
            part if part in "-/" or (any(c.isdigit() for c in part) and len(part) < 6) else part.capitalize()
            for part in re.split(r"([-/])", core))
        words.append(word.replace(core, fixed) if core else word)
    return " ".join(words)


def dailymed_title(title):
    """(product, generic name, form, maker) from a DailyMed title: "OZIPCO BROAD SPECTRUM DEWORMER (FENBENDAZOLE)
    POWDER [FAST SOLD LLC]" -> ("Ozipco Broad Spectrum Dewormer", "fenbendazole", "powder", "Fast Sold LLC");
    "METOPROLOL TARTRATE TABLET, FILM COATED [PD-RX PHARMACEUTICALS, INC.]" -> ("Metoprolol Tartrate", "",
    "tablet, film coated", "PD-Rx Pharmaceuticals, Inc."); None when it cannot be read."""
    m = re.match(r"^(?P<name>.+?)\s*\[(?P<maker>[^\]]+)\]\s*$", clean(title))
    if not m:
        return None
    name, maker = m.group("name"), m.group("maker")
    generic = ""
    g = re.search(r"\(([^()]+)\)\s*(?P<rest>[^()]*)$", name)
    if g:
        generic, form = g.group(1), g.group("rest")
        name = name[:g.start()].strip()
    else:
        f = re.search(r"\b(TABLETS?|CAPSULES?|INJECTION|SOLUTION|SUSPENSION|POWDER|CREAM|OINTMENT|GEL|LOTION|SPRAY|"
                      r"LIQUID|SYRUP|PATCH|GRANULES?|PASTE|AEROSOL|SHAMPOO|LOZENGE|KIT|STRIP|SOAP)\b.*$", name)
        form = f.group(0) if f else ""
        name = name[:f.start()].strip() if f else name
    if not name:
        return None
    return readable(name), clean(generic).lower(), clean(form).lower().strip(" ,"), readable(maker)


def dailymed_answer(title, kind, vet):
    """The careful answer for a label picture: "This looks like the package or label of Ozipco Broad Spectrum
    Dewormer (fenbendazole), a powder, an over-the-counter animal medicine from Fast Sold LLC." and the safety line;
    "" when the title cannot be read."""
    parts = dailymed_title(title)
    if not parts:
        return ""
    name, generic, form, maker = parts
    what = name + (f" ({generic})" if generic and generic.lower() not in name.lower() else "")
    form = f", {form}" if form else ""
    return (f"This looks like the package or label of {what}{form}: {kind} from {maker.rstrip('.')}. "
            f"{VET_SAFETY if vet else SAFETY}")


def label_picture(media):
    """The first package or label picture of a DailyMed label's media list, or None."""
    for item in media:
        name = item.get("name") or ""
        if item.get("mime_type") == "image/jpeg" and PACKAGE_PICTURE.search(name) and not NOT_PACKAGE.search(name):
            return item
    return None


def prepare_dailymed(source, data_dir, cap, doctypes, prefix, vet):
    """DailyMed labels: for each document type, random pages of the label list (100 a page), each label's media
    list read (gently, a third of a second apart) for one package or label picture; an even share of each type."""
    want = int((cap + source.test) * 1.15)
    per = per_label(want, len(doctypes))
    rng = random.Random(prefix)
    items = []
    for doctype, kind in doctypes:
        try:
            first = get_json(DAILYMED + "spls.json", {"doctype": doctype, "pagesize": 100, "page": 1})
        except RuntimeError:
            continue
        pages = list(range(1, int(first["metadata"].get("total_pages") or 1) + 1))
        rng.shuffle(pages)
        got, crowded = 0, 0
        for page in pages:
            if got >= per:
                break
            try:
                data = get_json(DAILYMED + "spls.json", {"doctype": doctype, "pagesize": 100, "page": page})
            except RuntimeError:
                continue
            for spl in data.get("data") or []:
                if got >= per:
                    break
                title = spl.get("title") or ""
                if left_out(title, people_ok=True) or COSMETIC.search(title):
                    continue
                if CROWDED.search(title):
                    if crowded >= max(1, per // 10):
                        continue
                answer = dailymed_answer(title, kind, vet)
                if not answer:
                    continue
                try:
                    media = get_json(f"{DAILYMED}spls/{spl['setid']}/media.json").get("data", {}).get("media") or []
                except RuntimeError:
                    continue
                time.sleep(0.3)
                picture = label_picture(media)
                if not picture:
                    continue
                crowded += 1 if CROWDED.search(title) else 0
                credit = (f"DailyMed, US National Library of Medicine: label of {clean(title)}, setid {spl['setid']}; "
                          f"label artwork by its maker, https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
                          f"{spl['setid']}")
                items.append((f"{prefix}-{spl['setid']}.jpg", picture["url"],
                              {"question": MEDICINE_Q, "answer": answer, "split": "", "credit": credit,
                               "place": "USA", "place_kind": "market"}))
                got += 1
        say(f"  DailyMed {kind}: {got} labels")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_dailymed_human_labels(source, data_dir, work, cap):
    """DailyMed human medicine labels (over the counter and prescription)."""
    return prepare_dailymed(source, data_dir, cap, HUMAN_DOCTYPES, "dailymed", vet=False)


def prepare_dailymed_vet_labels(source, data_dir, work, cap):
    """DailyMed animal medicine labels (over the counter and prescription)."""
    return prepare_dailymed(source, data_dir, cap, ANIMAL_DOCTYPES, "dailymed-vet", vet=True)


# ----------------------------------------------------------------- the table

SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
DAILYMED_SUMMARY = research("NLM: label pictures are 'content contributed by or licensed from private individuals, "
                            "companies, or organizations that may be protected by U.S. and international copyright "
                            "laws' (the drug makers' artwork).")
MED_VET_SOURCES = [
    # ---- share-alike
    Source("med_vet_commons_sa", "Wikimedia Commons: bandages, syringes, inhalers, stethoscopes, surgical "
                                 "instruments, pills, pill bottles, vitamins and veterinary drugs, files under CC "
                                 "BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 20, prepare_med_vet_commons_sa, "about 250 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("openfacts_supplements", "Open Food Facts: vitamins, dietary supplements, cough drops and throat "
                                    "lozenges sold in the USA and Canada, their name, brand and size (share-alike)",
           "Photos CC BY-SA 3.0, database ODbL 1.0 (https://world.openfoodfacts.org/terms-of-use)",
           "Open Food Facts contributors, photos CC BY-SA 3.0, data ODbL 1.0, each product credited in its row, "
           "https://world.openfoodfacts.org", "share-alike", 1200, 20, prepare_openfacts_supplements,
           "about 450 MB of product records (read once, shared by the Open Food Facts entries) and 500 MB of photos", terms="https://world.openfoodfacts.org/terms-of-use",
           terms_summary="Photos CC BY-SA 3.0 and data ODbL 1.0: use with credit; anything made from them keeps the "
                         "same licence."),
    # ---- research
    Source("dailymed_human_labels", "US medicine packages and labels, over the counter and prescription: which "
                                    "medicine (DailyMed, NLM; personal use)",
           "NLM web policies: government works are public domain, but label pictures are the makers' artwork and "
           f"'may be protected' ({DAILYMED_TERMS})",
           "DailyMed, US National Library of Medicine, https://dailymed.nlm.nih.gov; label artwork by each maker, "
           "credited in its row", "research", 3000, 30, prepare_dailymed_human_labels,
           "about 600 MB (pictures fetched one by one)", terms=DAILYMED_TERMS, terms_summary=DAILYMED_SUMMARY),
    Source("dailymed_vet_labels", "US animal medicine packages and labels: dewormers, flea and tick products, "
                                  "antibiotics for pets and livestock (DailyMed, NLM; personal use)",
           "NLM web policies: government works are public domain, but label pictures are the makers' artwork and "
           f"'may be protected' ({DAILYMED_TERMS})",
           "DailyMed, US National Library of Medicine, https://dailymed.nlm.nih.gov; label artwork by each maker, "
           "credited in its row", "research", 2000, 20, prepare_dailymed_vet_labels,
           "about 400 MB (pictures fetched one by one)", terms=DAILYMED_TERMS, terms_summary=DAILYMED_SUMMARY),
]

# The collections a picture-making model may learn from: all of them (no people by their words; packages,
# products and things only).
MED_VET_PICTURE_MAKING_OK = {"med_vet_commons_sa", "openfacts_supplements", "dailymed_human_labels",
                             "dailymed_vet_labels"}

MED_VET_SIGN_UP = {
    "Roboflow Universe surgical-instrument sets (e.g. 'Surgical Tools' by Mahmudul Hasan Ratul, CC BY 4.0: needle "
    "holders, scalpels, forceps and scissors)":
        "https://universe.roboflow.com/mahmudul-hasan-ratul/surgical-tools-v1ozl : a free Roboflow account and API "
        "key (it would come from a GitHub secret such as ROBOFLOW_API_KEY) to export; check each set's licence on "
        "its page and where its photos came from (many Roboflow sets are scraped from the web). The CC BY 4.0 "
        "dental instrument photos are already a pack (dental_instruments), taken from Mendeley Data, which needs no "
        "account.",
    "Kaggle surgical-instrument, pill and medicine-package sets":
        "https://www.kaggle.com : a free Kaggle account and API token (KAGGLE_USERNAME and KAGGLE_KEY secrets); "
        "check each set's licence one by one ('Other', 'Unknown' and web-scraped sets are not usable).",
    "Flickr: hospitals', public-health agencies' and public-media stations' photostreams":
        "https://www.flickr.com/services/apps/create/ : a free API key (FLICKR_API_KEY), but Flickr's API terms "
        "(https://www.flickr.com/services/api/tos/) say you shall not 'Cache or store any Flickr user photos other "
        "than for reasonable periods in order to provide the service you are providing to Flickr users'. Not "
        "built; Commons copies of CC-licensed Flickr photos are used instead, each file's licence checked.",
}

MED_VET_PERMISSION_CANDIDATES = {
    "SURGICAL TOOLS (Mendeley Data cyghvmjrt3, Amrita Vishwa Vidyapeetham, Chennai)":
        "Has: 6,000 photos of forceps, hemostats, scalpels, mayo scissors, syringes, bandage scissors, episiotomy "
        "scissors, surgical gloves and medical cotton. Licence: 'CC BY-ND 4.0' ('copy and distribute the material "
        "in any medium or format in unadapted form only'), so the photos cannot be given new descriptions or made "
        "smaller for a pack; and about 1,000 of them were 'sourced from various online platforms' (other people's "
        "copyright). Ask the authors (contact on https://data.mendeley.com/datasets/cyghvmjrt3/1) whether their "
        "own 5,000 photos may be used under CC BY.",
    "US National Library of Medicine (DailyMed label pictures)":
        "Has: package and label pictures of about 150,000 human and 3,500 animal drug labels (the research entries "
        "above). Ask whether NLM can say which label pictures may be used for training (they belong to the drug "
        "makers): https://support.nlm.nih.gov.",
    "Health Canada (Drug Product Database, Veterinary Drugs Directorate)":
        "Has: every drug sold in Canada (human, veterinary, disinfectant) with its DIN, brand, ingredients and "
        "packaging sizes, under the Open Government Licence - Canada, but no pictures. Ask whether label or "
        "package images submitted with applications could be published openly: "
        "https://www.canada.ca/en/health-canada/corporate/contact-us.html.",
    "NPR, PBS, GBH and CBC/Radio-Canada (photo libraries)":
        "Have: captioned news and programme photographs. Their terms forbid copying and (NPR) AI training without "
        "written consent (see MED_VET_NOT_INCLUDED). Ask: NPR's permissions page "
        "(https://www.npr.org/about-npr/179881519/rights-and-permissions-information), PBS "
        "(https://www.pbs.org/about/contact-information/), GBH Archives (through https://openvault.wgbh.org), "
        "CBC/Radio-Canada (https://cbchelp.cbc.ca, 'How do I ... obtain permission to use "
        "CBC or Radio-Canada material').",
}

MED_VET_NOT_INCLUDED = {
    # ---- Canadian medicines
    "Health Canada Drug Product Database (the Canadian counterpart of NLM's C3PI pill photos)":
        "open data, 'Open Government Licence - Canada' (open.canada.ca dataset 'Drug Product Database - All "
        "Files'), with every drug's name, strength, form, maker and package size, but no images: its extract has "
        "no image field (QRYM_DRUG_PRODUCT, QRYM_PACKAGING ...), and the API's packaging list "
        "(health-products.canada.ca/api/drug/packaging) has its UPC field empty in all 58,464 records (checked "
        "November 2026), so it cannot even be matched to Open Food Facts barcodes. The product monographs and "
        "veterinary labels it links to are the makers' PDFs. No Canadian pill-identification image set with an "
        "open licence was found (vigilance.ca's RxPhotos is a commercial service).",
    "Open Food, Beauty and Products Facts medicine categories":
        "almost nothing sold in Canada or the USA is filed as a medicine (en:medicines: 0 in Canada, 8 on Open "
        "Products Facts in the USA; en:pet-medicines, en:dewormers, en:flea-and-tick-treatments: 0 on Open Pet "
        "Food Facts and Open Products Facts, November 2026). The supplements, vitamins and lozenges are the "
        "openfacts_supplements entry.",
    # ---- veterinary
    "FDA Green Book and Animal Drugs @ FDA": "lists of approved animal drugs (names, sponsors, active ingredients), "
                                             "no pictures; the labels themselves are in DailyMed "
                                             "(dailymed_vet_labels).",
    "Health Canada Veterinary Drugs Directorate": "veterinary products are in the Drug Product Database (no "
                                                  "pictures, see above).",
    "USDA APHIS photos": "the Commons category 'Animal and Plant Health Inspection Service' has 32 files of its own "
                         "(130 with subcategories), mostly wildlife work at airports, border inspections and "
                         "officials, not animal medicines (a sample of its file names was read, November 2026); "
                         "APHIS's own photo stream is on Flickr (not used, see MED_VET_SIGN_UP).",
    "Veterinary pill-identification image sets": "none with an open licence was found.",
    # ---- the owner's rule: current items only
    "Wellcome Collection, Smithsonian NMAH medicine and science, Science Museum Group, Army Medical Museum "
    "(National Museum of Health and Medicine), old catalogue drawings":
        "left out by the owner's rule for this collection: only medical instruments, supplies and medicines in "
        "use today, nothing historical.",
    "3D-COSI (Zenodo 7635562, 103 3D-scanned medical instruments)": "3D models, not photos, and 'CC BY-NC 4.0'.",
    # ---- already used elsewhere
    "Commons categories already used by other packs":
        "Medical thermometers, Digital thermometers, Glucose meters, Sphygmomanometers in home_packs "
        "(commons_appliances; Sphygmomanometers is asked here too, only at its own level); Wheelchairs, Electric "
        "wheelchairs, Rollators, Crutches, Forearm crutches, Walking sticks, Mobility scooters, Hearing aids in "
        "disability_packs; Personal protective equipment in events_safety_packs; Pharmacies in Canada and the "
        "United States in canada_packs and us_modern_packs. Not repeated.",
    "Commons categories with no files (November 2026)":
        "Gauze, Elastic bandages, Arm slings, Walkers (mobility), Zimmer frames, Quad canes, Blood glucose test "
        "strips, Continuous glucose monitors, Metered-dose inhalers, Spacers (inhalers), Hemostats, IV poles, N95 "
        "respirators, Nitrile gloves, Surgical gowns, Epinephrine autoinjectors, EpiPen, Sharps containers, "
        "Medicines in Canada, Over-the-counter drugs, Flea collars, Pet medication, "
        "Dewormers, Heartworm medication, Pet care products, Livestock medicine (the spellings 'Hot-water bottles', "
        "'Pregnancy test' and 'Autoinjectors' do have files and are used).",
    # ---- public media (photos), checked November 2026
    "NPR (npr.org)":
        "Terms of Use: 'You may not reproduce, distribute, republish, upload ... or use for commercial purposes "
        "any copyrighted material on the NPR Services without the prior written consent of NPR' and 'You may not "
        "use, or enable others to use, any content, information, or other material on NPR Services to build or "
        "train large language models, machine learning tools, or artificial intelligence (AI) systems without the "
        "prior written consent of NPR' (https://www.npr.org/about-npr/179876898/terms-of-use). Its robots.txt "
        "also disallows GPTBot and CCBot. Most NPR photos are Getty, AP or Reuters in any case. No open photos.",
    "PBS (pbs.org) and PBS member stations":
        "Terms of Use: 'You shall not post, publish, transmit, reproduce, distribute or in any way use or exploit "
        "any Information for commercial purposes', and copyright law 'generally prohibit[s] the unauthorized "
        "reproduction ... of all text, photographic and graphic ... images' (https://www.pbs.org/about/policies/"
        "terms-of-use/). Member stations (WNYC, KQED, NHPR, WFAE, WBEZ ...) publish their own terms of use; none "
        "found states an open licence for its photos (only their titles were seen in a search, not read in full: "
        "unverified). No open photo collection found.",
    "GBH (WGBH) Open Vault and the American Archive of Public Broadcasting (AAPB)":
        "GBH terms: 'This Site and the Content therein may be used for bona fide personal, non-commercial "
        "purposes only' and 'You may not remove, copy, alter, reproduce, ... download, transmit, distribute, "
        "license or commercially exploit ... the Content' (https://americanarchive.org/legal/tou); AAPB Online "
        "Reading Room rules: 'you agree not to ... infringe any copyright' and 'The nature of ORR content often "
        "makes it difficult to determine the content's copyright status' (https://americanarchive.org/legal/"
        "orr-rules). Video and audio, streamed for research in the USA only; no open photo set.",
    "CBC/Radio-Canada (cbc.ca, ici.radio-canada.ca)":
        "the terms page refused this machine (403); CBC's help page sends reuse requests through permissions "
        "('How do I search for content or obtain permission to use CBC or Radio-Canada material'), and its "
        "robots.txt disallows AI crawlers (GPTBot, ChatGPT-User, OAI-SearchBot: 'Disallow: /'). No open licence "
        "found; in MED_VET_PERMISSION_CANDIDATES.",
    "Commons categories about the stations (National Public Radio, WGBH, WNYC, KQED, Canadian Broadcasting "
    "Corporation, Télé-Québec)":
        "53, 26, 40, 21, 53 and 11 files of their own (November 2026): logos, buildings, presenters at awards "
        "and archive photos by others (a sample of file names was read), not photos released by the stations "
        "under an open licence. No pack.",
    "TVO, Knowledge Network, Télé-Québec":
        "their sites state no open licence for photos (TVO's terms elsewhere allow use 'solely for informational, "
        "personal, non-commercial purposes'); their terms pages are rendered by scripts and could not be read in "
        "full from this machine. No open photo collection found.",
    "Voice of America (voanews.com)":
        "Copyright Statement: 'All text, audio and video material produced exclusively by the Voice of America "
        "is in the public domain', but 'voanews.com content may also contain text, video, audio, images, "
        "graphics, and other copyrighted material that is licensed for use in VOA programming only' and AFP, AP "
        "and Reuters material 'may not be stored in a computer except for personal and non-commercial use' "
        "(https://www.voanews.com/p/5338.html). VOA's site gives no list of its own photos (as archive_packs.py "
        "notes), so the site itself is not read; VOA's own files copied to Commons ('Images from Voice of "
        "America', 1,084 files) ARE used: the open pack voa_commons_photos in packs/med_vet_packs.py, each file's "
        "licence checked and wire-agency files left out.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one medicine, medical supply or veterinary collection.")
    parser.add_argument("key", choices=[s.key for s in MED_VET_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in MED_VET_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="med-vet-")
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
