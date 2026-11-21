"""Medicines: the official labels of human and veterinary medicines as ZIM books, for looking up a medicine offline.

The textbooks builder (build_textbooks.py) makes the books; this module adds one more kind of reference book: the
labels of medicines sold in the United States, the "package inserts" and patient leaflets that come with them. A
blind person can look up a medicine by its generic name or a brand name and read, in a plain order, what it is for,
how to take it, its warnings (the boxed warning first), side effects, interactions, storage, pregnancy and
breastfeeding, and the patient leaflet (Medication Guide or patient package insert), in the label's own words.

Where the text comes from (every source checked by hand on 2026-11-21; the lines quoted are in LICENCE_LINES):
  DailyMed (dailymed.nlm.nih.gov, National Library of Medicine)   the labels themselves, in the FDA's Structured
          Product Labeling (SPL) XML, read one by one through DailyMed's official web services (v2): prescription
          and over-the-counter human labels (with the Medication Guides, patient package inserts, instructions for
          use and the Drug Facts panels, which are parts of the label) and animal (veterinary) labels. DailyMed's
          bulk files are 3 GB each (19 GB for prescription labels, 38 GB for over-the-counter ones), far more than
          a build machine holds, so only its small mapping files are downloaded whole: "rxnorm_mappings.zip" (which
          label is which generic medicine, strength, form and brand) and "dm_spl_zip_files_meta_data.zip" (each
          label's title, company and date). The same labels are published by openFDA in the public domain (CC0).
  Drugs@FDA (www.fda.gov, the FDA's data file, public domain)      each human label's FDA application: its number,
          the company that holds it, and the date it was first approved.
  Health Canada Drug Product Database (its official API, Open Government Licence - Canada)   the brand names the
          same medicine is sold under in Canada (marketed products only), human and veterinary.
What was looked at and not used, and why, is in NOT_INCLUDED (LactMed and LiverTox, the CDC's vaccine information
statements, the Green Book, the USDA's vaccine labels, Health Canada's product monographs, MedlinePlus, ...).

How the books are organised (each a ZIM file of its own, so nobody has to download all of them):
  Prescription medicines (US labels), 14 books by first letter: med:rx:a, med:rx:b, ... med:rx:u-z
  Over-the-counter medicines (US Drug Facts labels), 7 books: med:otc:a-b, med:otc:c, ... med:otc:t-z
  Pet and horse medicines, and Farm animal medicines (US animal drug labels): both from the one key med:animal
One page per medicine, named by its generic name ("Ibuprofen"; a combination: "Acetaminophen and codeine
phosphate"). Each brand name (US, and Canadian from Health Canada) is a title of its own that leads to the page, and
every book has a "Brand names A to Z" page. A medicine sold in several forms (tablets, an injection, a cream) has
one label per form on its page, each label in this order:
  Quick facts   (prescription or over the counter, brand names, forms, whether it has a boxed warning, and what
                it is for in the label's own first sentence: a short summary drawn only from the label)
  Highlights    (the label's own summary, "Highlights of prescribing information", when it has one)
  What it is for, How to take it (animals: How to give it), Warnings (the boxed warning first), Side effects,
  Interactions, Storage, Pregnancy and breastfeeding, Information for patients (the Medication Guide, patient
  package insert, instructions for use; animals: information for owners), Other parts of the label.
A part the label does not have says so ("The label has no separate section on this."), so every page reads the
same way. The label's own text is kept: its headings, paragraphs, lists and tables; pictures become their
description ("Picture: Chemical structure") or are left out when they have none. Every page and every book says
"Information, not medical advice: ask a pharmacist or doctor" (animals: "ask a veterinarian").

Which label is chosen when many companies sell the same medicine (metformin has about 500 labels, most of them from
repackagers): for each generic medicine and each form, the label of a brand when there is one, else not a
repackager's, then one by a company that holds an FDA application (Drugs@FDA: the maker, not a pharmacy), then one
with a name of its own, then the newest year (DailyMed's upload date) and the most revised (its version number).
Homeopathic products are left out (their "ingredients" are dilutions, not medicines), and so are kits of unrelated
medicines (first-aid kits).

Versions: every build is a new file (<name>.<YYYY-MM-DD>.zim) and the old ones stay (updates.py keeps them in
textbooks.json "versions"); a rebuild whose text did not change adds no version. The weekly check (updates.py)
rebuilds the books when DailyMed publishes its next monthly release (sign()).

Keys:
  medicines            every book (all the keys below)
  med:human, med:rx, med:otc   every human, prescription or over-the-counter book
  med:rx:<letters>, med:otc:<letters>, med:animal   one book (two for med:animal)

Use from the command line (the textbooks workflow calls it through build_textbooks.py):
  python textbooks/medications.py med:rx:a --out build/textbooks --cache build/textbooks-cache
  python textbooks/medications.py med:rx:i med:otc:i-m med:animal --only ibuprofen,metformin,carprofen,apoquel
      (a small test build: only those medicines, generic or brand names, in books named "..._sample")
"""

import argparse
import datetime
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402

DAILYMED = "https://dailymed.nlm.nih.gov/dailymed"
DM_SERVICES = DAILYMED + "/services/v2"
DM_DATA = "https://dailymed-data.nlm.nih.gov/public-release-files"
DM_DOWNLOADS = DAILYMED + "/spl-resources-all-drug-labels.cfm"
DRUGS_AT_FDA = "https://www.fda.gov/media/89850/download"          # the Drugs@FDA data file (zip, weekly)
FDA_POLICY = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_POLICY_TEXT = r"They are in the public domain and may be republished, reprinted and otherwise used freely"
OPENFDA_META = "https://api.fda.gov/drug/label.json?limit=1"
OPENFDA_LICENSE = "https://open.fda.gov/license/"
DPD_API = "https://health-products.canada.ca/api/drug"
DPD_DATASET = "https://open.canada.ca/data/api/action/package_show?id=bf55e42a-63cb-4556-bfd8-44f26e5a36fe"
OGL_CANADA = "https://open.canada.ca/en/open-government-licence-canada"
OGL_CANADA_NOTICE = "Contains information licensed under the Open Government Licence – Canada."

RELEASE = "medicines"            # the GitHub release the medicine books are published in
LICENCE = "Public domain (US drug labeling)"   # sources.ALLOWED: "open"
GROUP_HUMAN = "medicines"
GROUP_VET = "vet_medicines"
N = "{urn:hl7-org:v3}"           # the SPL XML namespace

# The DailyMed document types (LOINC codes) of each kind of label.
RX_TYPES = {"34391-3": "prescription", "53404-0": "vaccine", "60683-0": "plasma derivative",
            "60684-8": "cellular therapy"}
OTC_TYPE = "34390-5"
ANIMAL_TYPES = {"50578-4": "prescription animal", "50577-6": "over-the-counter animal",
                "50576-8": "medicated feed (Type A medicated article)"}

RX_PIECES = ["a", "b", "c", "d", "e-f", "g-h", "i-l", "m", "n-o", "p", "q-r", "s", "t", "u-z"]
OTC_PIECES = ["a-b", "c", "d-h", "i-m", "n-r", "s", "t-z"]
MAX_FORMS = 6                    # the most labels (forms) on one medicine's page
MAX_TRIES = 3                    # labels read in turn when the chosen one turns out to be another kind

HUMAN_NOTICE = "Information, not medical advice: ask a pharmacist or doctor."
VET_NOTICE = "Information, not veterinary advice: ask a veterinarian."
LABEL_NOTICE = ("Drug labels are written by the companies that make the medicines and are approved or listed by "
                "the US Food and Drug Administration (FDA). Source: National Library of Medicine (DailyMed). The "
                "same labels are published by openFDA in the public domain (CC0 1.0). Brand names are trademarks "
                "of their owners.")
FDA_CREDIT = "FDA applications: Drugs@FDA, US Food and Drug Administration (public domain)."

# ====================================================================== what was checked (shown in textbooks.json)

# The notes the toolkit shows with each collection (textbooks.json "group_notes").
GROUP_NOTES = {GROUP_HUMAN: HUMAN_NOTICE + " Labels change: each book is rebuilt monthly and older versions are "
                            "kept.",
               GROUP_VET: VET_NOTICE + " Labels change: each book is rebuilt monthly and older versions are kept."}

LICENCE_LINES = {
    "dailymed": "NLM web policies (www.nlm.nih.gov/web_policies.html): \"Works produced by the U.S. government are "
                "not subject to copyright protection in the United States. Any such works found on National "
                "Library of Medicine (NLM) Web sites may be freely used or reproduced without permission in the "
                "U.S. Please acknowledge NLM as the source\" (credited on every book: \"Source: National Library of "
                "Medicine (DailyMed)\"). The labels are written by the drug companies; the same labels are "
                "published by openFDA (open.fda.gov/license/): \"unless otherwise noted, the content, data, "
                "documentation, code, and related materials on openFDA is public domain and made available with a "
                "Creative Commons CC0 1.0 Universal dedication\"; its drug label data carries no \"not in the public "
                "domain\" warning. Every build checks that openFDA's drug label API still names that licence. "
                "dailymed.nlm.nih.gov has no robots.txt (it redirects to the home page) and "
                "dailymed-data.nlm.nih.gov has none (404); the labels are read through DailyMed's web services, "
                "one request at a time.",
    "drugs_at_fda": "FDA website policies (www.fda.gov/about-fda/about-website/website-policies): \"Unless otherwise "
                    "noted, the contents of the FDA website (www.fda.gov) — both text and graphics — are not "
                    "copyrighted. They are in the public domain and may be republished, reprinted and otherwise "
                    "used freely by anyone\" (checked again at every build). www.fda.gov's robots.txt allows "
                    "/media/ and asks a 30-second crawl delay; the data file is one request per build.",
    "health_canada_dpd": "open.canada.ca dataset \"Drug Product Database - All Files\" (its resources include the "
                         "API health-products.canada.ca/api/drug/): licence \"Open Government Licence - Canada\" "
                         "(checked again at every build); attribution: \"Contains information licensed under the "
                         "Open Government Licence – Canada.\" health-products.canada.ca has no robots.txt (404).",
}

NOT_INCLUDED = [
    ("NIH LactMed (Drugs and Lactation Database) and LiverTox (NCBI Bookshelf)", "Public domain, but NCBI answers "
     "this builder's requests with a reCAPTCHA browser check (\"Checking your browser\"), and the robots.txt of its "
     "bulk download site (ftp.ncbi.nlm.nih.gov) and of its E-utilities API (eutils.ncbi.nlm.nih.gov) both say "
     "\"User-agent: * Disallow: /\". The pregnancy and breastfeeding part of each entry comes from the label's own "
     "sections (Pregnancy, Lactation, Nursing mothers; the Drug Facts \"If pregnant or breast-feeding\")."),
    ("openFDA drug labels (bulk JSON download)", "Public domain (CC0), the same labels as DailyMed's, but with every "
     "section flattened to plain text (tables and lists lost) and without the animal labels; its download host's "
     "robots.txt answers 403, which this builder reads as \"no\". DailyMed's SPL XML keeps the headings, lists and "
     "tables; openFDA's API is used only to check the licence."),
    ("FDA Medication Guides page (accessdata.fda.gov)", "The Medication Guides are part of each label in DailyMed "
     "(its \"Medication Guide\" section) and are included from there; accessdata.fda.gov asks robots to visit only "
     "at night, 30 seconds apart."),
    ("CDC Vaccine Information Statements", "Public domain, but www.cdc.gov refuses automated requests (403, its "
     "robots.txt included). Vaccine package inserts are included from DailyMed (prescription books)."),
    ("Health Canada product monographs (Drug Product Database PDFs)", "The monographs are written by the drug "
     "companies and are not government information under the Open Government Licence – Canada (it does not cover "
     "third-party material). Only the database's own facts are used: the Canadian brand names."),
    ("Health Canada veterinary drug labels", "No veterinary label text is published in the Drug Product Database; "
     "the Canadian brand names of veterinary medicines are included."),
    ("FDA CVM Green Book (Animal Drugs @ FDA)", "Public domain, but reachable only through an undocumented web-app "
     "interface (no official API or bulk download). Each animal label's own FDA approval number (NADA or ANADA) is "
     "shown instead."),
    ("USDA Center for Veterinary Biologics product information (animal vaccines)", "www.aphis.usda.gov refuses "
     "automated requests (403, its robots.txt included)."),
    ("MedlinePlus drug information", "Its drug monographs are AHFS Consumer Medication Information, copyrighted by "
     "the American Society of Health-System Pharmacists (not reusable); MedlinePlus's own health topics are already "
     "in the Kiwix library."),
    ("Drugs.com", "Copyrighted; not used."),
    ("EPA pesticide labels (flea and tick products)", "Handled by another part of the library (pesticide labels)."),
    ("Homeopathic products", "Left out of the medicine books: their labels list dilutions, not medicines."),
]

# ====================================================================== the pieces

def expand_keys(words):
    """The one-book keys ("med:rx:a", "med:animal") of a list of words ("medicines", "med:human", "med:rx",
    "med:otc", "med:animal" or a one-book key); unknown words give nothing."""
    out = []
    for w in words:
        if w in ("medicines", "med:all"):
            out += [f"med:rx:{p}" for p in RX_PIECES] + [f"med:otc:{p}" for p in OTC_PIECES] + ["med:animal"]
        elif w == "med:human":
            out += [f"med:rx:{p}" for p in RX_PIECES] + [f"med:otc:{p}" for p in OTC_PIECES]
        elif w == "med:rx":
            out += [f"med:rx:{p}" for p in RX_PIECES]
        elif w == "med:otc":
            out += [f"med:otc:{p}" for p in OTC_PIECES]
        elif w == "med:animal" or (w.startswith("med:rx:") and w[7:] in RX_PIECES) or \
                (w.startswith("med:otc:") and w[8:] in OTC_PIECES):
            out.append(w)
    return list(dict.fromkeys(out))


def in_piece(name, piece, pieces):
    """True when a medicine's name belongs to the book of letters `piece` ("e-f": names starting with e or f).
    Names that start with no letter (a number) go to the last book."""
    first = (name[:1] or "~").lower()
    if not ("a" <= first <= "z"):
        return piece == pieces[-1]
    low, _, high = piece.partition("-")
    return low <= first <= (high or low)


# ====================================================================== names, strengths and forms

SALTS = {"hydrochloride", "hcl", "hydrobromide", "sulfate", "sulphate", "maleate", "mesylate", "besylate",
         "tartrate", "bitartrate", "citrate", "succinate", "fumarate", "acetate", "phosphate", "sodium", "potassium",
         "calcium", "magnesium", "trihydrate", "monohydrate", "dihydrate", "hyclate", "disodium", "dipropionate",
         "propionate", "valerate", "hemihydrate", "anhydrous", "lysine", "tromethamine", "hydrate", "dihydrochloride",
         "monosodium", "meglumine", "bromide", "chloride", "nitrate", "lactate", "gluconate", "malate", "oxalate",
         "pamoate", "napsylate", "estolate", "stearate", "ethylsuccinate", "hexahydrate", "sesquihydrate"}


def base_name(name):
    """A medicine's name without its salt, for matching ("METFORMIN HYDROCHLORIDE" -> "metformin", "ibuprofen
    sodium" -> "ibuprofen", "AMOXICILLIN (AMOXICILLIN TRIHYDRATE)" -> "amoxicillin"); a name that is only salt words
    ("sodium chloride", "calcium carbonate") keeps its first word."""
    words = re.sub(r"\(.*?\)", " ", (name or "").lower()).replace(",", " ").split()
    while len(words) > 1 and words[-1] in SALTS:
        words.pop()
    return " ".join(words)


def combo_key(names):
    """The key of a medicine (one ingredient or a combination): its base names, sorted, joined with " + "."""
    return " + ".join(sorted({base_name(n) for n in names if base_name(n)}))


def display_name(names):
    """A medicine's page title from its ingredients: "Ibuprofen", "Acetaminophen and codeine phosphate",
    "Acetaminophen, dextromethorphan hydrobromide and guaifenesin"."""
    names = sorted({" ".join(n.lower().split()) for n in names if n.strip()})
    text = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return text[:1].upper() + text[1:]


def parse_rxnorm(name):
    """(ingredient names, dose form) of an RxNorm clinical drug name ("ibuprofen 200 MG Oral Tablet" ->
    (["ibuprofen"], "Oral Tablet"); "24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet" ->
    (["metformin hydrochloride"], "Extended Release Oral Tablet"); "5 ML lidocaine hydrochloride 10 MG/ML Injection"
    -> (["lidocaine hydrochloride"], "Injection"))."""
    s = re.sub(r"^[\d.]+ [A-Z]+ ", "", name.strip())
    names, form = [], ""
    parts = s.split(" / ")
    for i, part in enumerate(parts):
        toks = part.split(" ")
        j = next((k for k, t in enumerate(toks) if re.match(r"^\d", t)), len(toks))
        if " ".join(toks[:j]).strip():
            names.append(" ".join(toks[:j]))
        if i == len(parts) - 1:
            rest = toks[j + 1:]
            k = next((k for k, t in enumerate(rest) if re.match(r"^[A-Z][a-z]", t)), len(rest))
            form = " ".join(rest[k:])
    return names, form


def form_family(form):
    """The way a medicine is used, from its dose form ("Oral Tablet" -> "by mouth", "Extended Release Oral Tablet"
    -> "by mouth, extended release", "Injectable Solution" -> "injection", "Topical Cream" -> "on the skin")."""
    f = (form or "").lower()
    rules = [(r"ophthalmic|\beye\b", "in the eye"), (r"\botic\b|\bear\b", "in the ear"), (r"nasal", "in the nose"),
             (r"inhal|nebuli", "breathed in"),
             (r"inject|syringe|cartridge|auto-injector|infusion|intravenous|implant", "injection"),
             (r"vaginal", "vaginal"), (r"rectal|enema|suppositor", "rectal"),
             (r"toothpaste|mouthwash|dental|oral gel|rinse|mucosal|mucous membrane|oral paste|oral spray",
              "in the mouth"),
             (r"topical|transdermal|patch|\bpad\b|soap|shampoo|cream|ointment|lotion|foam|stick|\bgel\b|\boil\b|"
              r"cloth|swab|spray|tape|dressing|\bpaste\b|\bbar\b|powder(?! for)", "on the skin"),
             (r"extended release", "by mouth, extended release"),
             (r"syrup|elixir|suspension|solution|oral liquid|drops", "by mouth, liquid"),
             (r"oral|tablet|capsule|chewable|lozenge|sublingual|buccal|granule|pellet|gum|film|strip|wafer",
              "by mouth")]
    for pattern, family in rules:
        if re.search(pattern, f):
            return family
    return "other forms"


ANIMAL_FORM = re.compile(r"\b(TABLET|CAPSULE|INJECTION|INJECTABLE|SOLUTION|SUSPENSION|POWDER|GRANULE|PASTE|GEL|"
                         r"OINTMENT|CREAM|SHAMPOO|SPRAY|COLLAR|LIQUID|EMULSION|LOTION|PELLET|BOLUS|IMPLANT|AEROSOL|"
                         r"CONCENTRATE|DROPS?|KIT|PATCH|STRIP|BAR|CHEW|SOFT CHEW|PREMIX|CRUMBLE|MEAL|FEED|TINCTURE|"
                         r"FOAM|WIPES?|GAS|SUPPOSITORY|INSERT|DIP|POUR-ON|PELLETED|TOPICAL)\b")


TITLE_FORM = re.compile(r"\b(soft chewables?|chewables?|soft chews?|chews?|tablets?|caplets?|capsules?|injection|"
                        r"injectable|sterile|flavou?red|oral|topical)\b", re.I)


def parse_title(title):
    """(brand, generic names, form, company) of a DailyMed listing title: "QUELLIN (CARPROFEN) TABLET, CHEWABLE
    [ELANCO US INC.]" -> ("QUELLIN", ["CARPROFEN"], "TABLET, CHEWABLE", "ELANCO US INC."); "CARPROFEN TABLET
    [ZYVET]" -> ("", ["CARPROFEN"], "TABLET", "ZYVET")."""
    t = html.unescape(title or "").strip()
    m = re.search(r"\s*\[([^\]]*)\]\s*$", t)
    company = m.group(1) if m else ""
    t = t[:m.start()] if m else t
    m = re.match(r"^(.*?)\s*\(((?:[^()]|\([^()]*\))*)\)\s*(.*)$", t)   # the first product of the title
    if m and m.group(2).strip():
        brand, inner, form = m.group(1).strip(), m.group(2), m.group(3).strip()
        generics = [re.sub(r"^\s*and\s+", "", TITLE_FORM.sub(" ", g), flags=re.I).strip()
                    for g in re.split(r",\s*(?![^()]*\))", inner)]
        generics = [" ".join(g.split()) for g in generics if g]
        if not brand_words(brand, combo_key(generics)):     # "AMOXICILLIN CAPSULES (AMOXICILLIN)": no brand
            brand = ""
        return brand, generics, form, company
    m = ANIMAL_FORM.search(t)
    name, form = (t[:m.start()].strip(), t[m.start():].strip()) if m else (t, "")
    return "", [x.strip() for x in re.split(r",| AND ", name) if x.strip()], form, company


REPACKAGERS = re.compile(r"REPACK|PREPACK|MEDICATION SOLUTIONS|PD-RX|PROFICIENT RX|DIRECT RX|DIRECT_RX|NUCARE|"
                         r"QUALITY CARE|AIDAREX|PREFERRED PHARMACEUTICAL|BRYANT RANCH|ASCLEMED|HENRY SCHEIN|MEDSOURCE|"
                         r"NORTHWIND|LAKE ERIE|COUPLER|QPHARMA|UNIT DOSE SERVICES|AMERICAN HEALTH PACKAGING|"
                         r"CARDINAL HEALTH|MAJOR PHARMACEUTICALS|AVKARE|AVPAK|GOLDEN STATE MEDICAL|ST\. MARY'S MEDICAL|"
                         r"RXCHANGE|NUCARE|DENTON PHARMA|MCKESSON|PRECISION DOSE|SAFECOR|ATLANTIC BIOLOGICALS|"
                         r"MEDVANTX|READYMEDS|STAT RX|RX PAK|PHARMEDIX|PACKAGING", re.I)


def rank(candidate):
    """How good a label is as the one shown for its medicine and form (higher first): a brand's label that RxNorm
    knows, then not a repackager's, by a company that holds an FDA application (the maker), with a name of its own
    in its title (a brand, or a shop's own brand), uploaded in the newest year, the most revised (a label kept up to
    date for years), the newest."""
    return (bool(candidate.get("sbd")), not REPACKAGERS.search(candidate.get("company", "")),
            bool(candidate.get("maker")), bool(candidate.get("brand")), candidate.get("date", "")[:4],
            int(candidate.get("version") or 0), candidate.get("date", ""))


def first_word(company):
    """The first real word of a company's name, for matching ("AUROBINDO PHARMA LTD" -> "aurobindo")."""
    words = [w for w in re.findall(r"[a-z0-9]+", (company or "").lower()) if len(w) > 2 and w != "the"]
    return words[0] if words else ""


def makers(fda):
    """The first words of the companies that hold an FDA application (Drugs@FDA): a label by one of them is the
    maker's own, not a repackager's or a pharmacy's."""
    return {first_word(v.get("sponsor", "")) for v in (fda or {}).values()} - {""}


# ====================================================================== downloads (DailyMed, Drugs@FDA, Health Canada)

_READ = {}                       # what was read fresh in this run (the listings and mapping files), by address


def _fresh(url, cache=None, binary=False):
    """The body of url read fresh today: kept in the cache folder for the rest of the day only (the listings and
    mapping files change every day; a test build run twice in one day reads them once)."""
    if not cache:
        return B.fetch(url, None, binary=binary)
    return _day_cached(url, cache, binary)


def _day_cached(url, cache, binary):
    """The body of url, from today's copy in the cache folder or read now (see _fresh)."""
    import hashlib
    path = os.path.join(cache, "dailymed-today", datetime.date.today().isoformat(),
                        hashlib.sha256(url.encode()).hexdigest()[:40])
    if not os.path.exists(path):
        data = B.fetch(url, None, binary=True)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    with open(path, "rb") as f:
        data = f.read()
    return data if binary else data.decode("utf-8", "replace")


def _zip_text(url, suffix, cache=None):
    """The text of the member ending with `suffix` of the zip file at url (read once per run, fresh each day)."""
    if (url, suffix) not in _READ:
        data = _fresh(url, cache, binary=True)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(suffix.lower()))
            _READ[(url, suffix)] = z.read(name).decode("utf-8", "replace")
    return _READ[(url, suffix)]


def _dm_date(text):
    """"10/09/2010" or "Oct 29, 2026" as "2010-10-09" ("" when not a date)."""
    m = re.match(r"(\d\d)/(\d\d)/(\d{4})", text or "")
    return f"{m.group(3)}-{m.group(1)}-{m.group(2)}" if m else B.iso_date(text or "")


PREP = {"isopropyl alcohol", "povidone-iodine", "ethanol", "benzalkonium", "chlorhexidine", "inert ingredients",
        "sodium"}                # the swabs and placebo tablets that come with a medicine in a kit or pack


def rxnorm_records(text, kits=None):
    """{setid: {"names": [ingredient names], "forms": {family: dose form}, "brands": {brand names}, "version"}} from
    DailyMed's rxnorm_mappings.txt (SETID|SPL_VERSION|RXCUI|RXSTRING|RXTTY): its clinical drugs (SCD) give the
    ingredients and forms, its branded drugs (SBD, BPCK) the brand names in brackets. A label for several products:
    a pack (a birth control pack with its placebo tablets, an injection kit with its alcohol swab) counts as its
    medicine; a pack of several medicines (an H. pylori pack) as their combination; a kit of unrelated medicines (a
    first-aid kit, an allergen mixture without a pack) is left out, and its set id added to kits."""
    found = {}
    for line in text.splitlines()[1:]:
        p = line.split("|")
        if len(p) < 5:
            continue
        setid, version, _cui, name, tty = p[:5]
        rec = found.setdefault(setid, {"combos": {}, "forms": {}, "brands": set(), "version": version, "pack": False})
        if tty == "SCD":
            names, form = parse_rxnorm(name)
            if names:
                rec["combos"].setdefault(combo_key(names), set()).update(names)
                rec["forms"].setdefault(combo_key(names), {}).setdefault(form_family(form), form)
        elif tty in ("SBD", "BPCK"):
            rec["brands"].update(b.strip() for b in re.findall(r"\[([^\]]+)\]\s*(?:Pack)?$", name))
        if tty in ("GPCK", "BPCK"):
            rec["pack"] = True
    out = {}
    for setid, rec in found.items():
        combos = rec["combos"]
        real = [k for k in combos if k not in PREP] or list(combos)
        if not real:
            continue
        if len(real) > 1 and not rec["pack"]:
            if kits is not None:
                kits.add(setid)
            continue
        names = set().union(*(combos[k] for k in real))
        forms = {}
        for k in real:
            for family, form in rec["forms"][k].items():
                forms.setdefault(family, form)
        out[setid] = {"names": names, "forms": forms, "brands": rec["brands"], "version": rec["version"]}
    return out


def meta_records(text):
    """{setid: (title, upload date "YYYY-MM-DD", version)} from dm_spl_zip_files_meta_data.txt
    (SETID|ZIP_FILE_NAME|UPLOAD_DATE|SPL_VERSION|TITLE)."""
    out = {}
    for line in text.splitlines()[1:]:
        p = line.split("|", 4)
        if len(p) == 5:
            out[p[0]] = (p[4], _dm_date(p[2]), p[3])
    return out


def dailymed_listing(doctypes, cache=None):
    """{setid: {"title", "version", "date"}} of every label of these DailyMed document types (its web service
    spls.json, 100 a page), read fresh once per run and each day (labels change)."""
    if ("listing", tuple(doctypes)) in _READ:
        return _READ[("listing", tuple(doctypes))]
    out = {}
    for doctype in doctypes:
        page = 1
        while True:
            data = json.loads(_fresh(f"{DM_SERVICES}/spls.json?doctype={doctype}&pagesize=100&page={page}", cache))
            for row in data.get("data", []):
                out[row["setid"]] = {"title": row.get("title", ""), "version": row.get("spl_version", 0),
                                     "date": _dm_date(row.get("published_date", "")), "doctype": doctype}
            meta = data.get("metadata", {})
            if page >= int(meta.get("total_pages") or 0) or not data.get("data"):
                break
            page += 1
    _READ[("listing", tuple(doctypes))] = out
    return out


def spl_xml(setid, version, cache=None):
    """The SPL XML of one label (DailyMed's web service), kept in the cache folder under its set id and version
    (a new version of the label is read again)."""
    url = f"{DM_SERVICES}/spls/{setid}.xml"
    if cache:
        path = os.path.join(cache, "dailymed-spl", f"{setid}.{version}.xml")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
        text = B.fetch(url, None)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return text
    return B.fetch(url, None)


def drugs_at_fda(cache=None):
    """{"NDA020402": {"sponsor", "approved"}} from the Drugs@FDA data file: each application's company and the date
    it was first approved; {} when FDA's policy page no longer says its contents are public domain, or the file
    cannot be read. Read once per run."""
    if "drugs@fda" in _READ:
        return _READ["drugs@fda"]
    _READ["drugs@fda"] = {}
    try:
        if not (B.allowed_by_robots(FDA_POLICY, cache) and B.allowed_by_robots(DRUGS_AT_FDA, cache)):
            return {}
        words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", B.fetch(FDA_POLICY, None))).split())
        if not re.search(FDA_POLICY_TEXT, words):
            return {}
        data = B.fetch(DRUGS_AT_FDA, None, binary=True)                 # read fresh: it changes weekly
    except (urllib.error.URLError, OSError, ValueError):
        return {}
    out = {}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        def rows(suffix):
            """The rows of one tab-separated member, as dicts."""
            name = next((n for n in z.namelist() if n.lower().endswith(suffix)), None)
            if not name:
                return []
            lines = z.read(name).decode("latin-1").splitlines()
            head = lines[0].split("\t") if lines else []
            return [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]
        for r in rows("applications.txt"):
            out[f"{r.get('ApplType', '').strip()}{r.get('ApplNo', '').strip()}"] = {
                "sponsor": r.get("SponsorName", "").strip(), "approved": ""}
        by_no = {k[-6:]: k for k in out}
        for r in rows("submissions.txt"):
            if r.get("SubmissionType") == "ORIG" and r.get("SubmissionStatus") == "AP":
                key = by_no.get(r.get("ApplNo", "").strip().zfill(6))
                if key:
                    out[key]["approved"] = B.iso_date(r.get("SubmissionStatusDate", ""))
    _READ["drugs@fda"] = out
    return out


GENERIC_WORDS = re.compile(r"\b(tablets?|tabs?|caplets?|capsules?|caps|liquid|gels?|gel caps|liqui-gels|mini|"
                           r"suspension|"
                           r"oral|solution|syrup|drops|injection|cream|ointment|extra|strength|regular|er|xr|sr|cr|"
                           r"dr|fc|bp|usp|film coated|chewables?|soft|chews?|sterile|injectable|flavou?red|"
                           r"for|and|with|mg|ml|mcg|g|%|"
                           r"\d[\d.,/]*\s*(mg|ml|mcg|g)?)\b",
                           re.I)


def brand_words(brand, key):
    """A brand name as shown ("CHILDREN'S MOTRIN" -> "Children's Motrin"), or "" when it is only the generic name
    with forms and strengths ("IBUPROFEN TABLETS 200 MG", "Metformin ER"): that is no brand to look up."""
    brand = re.sub(r"(^|[\s\-/(&+])([a-z])", lambda m: m.group(1) + m.group(2).upper(),
                   " ".join((brand or "").split()).lower())
    rest = brand.lower()
    for name in key.split(" + "):
        rest = re.sub(rf"\b{re.escape(name)}\w*", " ", rest)
    rest = " ".join(w for w in rest.split() if w not in SALTS)
    rest = GENERIC_WORDS.sub(" ", rest)
    return brand if re.search(r"[a-z]{2,}", re.sub(r"[^a-z' ]", " ", rest)) else ""


CANADA_KIND = {"NON-PRESCRIPTION DRUGS": "otc", "ETHICAL": "otc", "HOMEOPATHIC": ""}


def canadian_brands(cache=None):
    """{(kind, combo key): {brand names}} of the products marketed in Canada (Health Canada's Drug Product
    Database API): kind "rx" for prescription (and narcotic and controlled) products, "otc" for non-prescription
    ones, "animal" for veterinary ones; homeopathic products and names that are only the generic name are left
    out. {} when the dataset's licence is no longer the Open Government Licence - Canada or the API cannot be read.
    Read once per run."""
    if "dpd" in _READ:
        return _READ["dpd"]
    _READ["dpd"] = {}
    try:
        if B.allowed_by_robots(DPD_DATASET, cache):
            meta = json.loads(B.fetch(DPD_DATASET, None))
            if "open government licence - canada" not in (meta.get("result", {}).get("license_title") or "").lower():
                return {}
        products = json.loads(B.fetch(f"{DPD_API}/drugproduct/?lang=en&type=json&status=2", None))
        ingredients = json.loads(B.fetch(f"{DPD_API}/activeingredient/?lang=en&type=json", None))
        schedules = json.loads(B.fetch(f"{DPD_API}/schedule/?lang=en&type=json", None))
    except (urllib.error.URLError, OSError, ValueError):
        return {}
    names, kinds = {}, {}
    for i in ingredients:
        names.setdefault(i.get("drug_code"), []).append(i.get("ingredient_name", ""))
    for sch in schedules:
        kinds.setdefault(sch.get("drug_code"), set()).add(CANADA_KIND.get(sch.get("schedule_name", ""), "rx"))
    out = {}
    for p in products:
        key = combo_key(names.get(p.get("drug_code"), []))
        if p.get("class_name") == "Veterinary":
            found = {"animal"}
        elif p.get("class_name") == "Human":
            found = kinds.get(p.get("drug_code"), {"rx"})
            found = {"rx"} if "rx" in found else found - {""}
        else:
            continue
        brand = brand_words(p.get("brand_name", ""), key)
        for kind in found:
            if key and brand:
                out.setdefault((kind, key), set()).add(brand)
    _READ["dpd"] = out
    return out


def licence_still_open():
    """True when openFDA's drug label API still names its public-domain licence page (the same labels)."""
    try:
        meta = json.loads(B.fetch(OPENFDA_META, None)).get("meta", {})
    except (urllib.error.URLError, OSError, ValueError):
        return False
    return meta.get("license", "").rstrip("/") == OPENFDA_LICENSE.rstrip("/")


# ====================================================================== the label (SPL XML) as HTML

def _t(el):
    """The words of an element, spaces tidied."""
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def _code(el):
    """The LOINC code of a section ("34067-9"), "" when it has none."""
    c = el.find(N + "code")
    return c.get("code", "") if c is not None else ""


class SplHtml:
    """Turns the narrative text of an SPL label (its <text> elements) into the plain HTML of the books: paragraphs,
    lists, tables with their captions, bold and italic words, superscripts; a picture becomes "Picture: " and its
    description (the label's alt text), or is left out when it has none; links inside the label keep their words."""

    def __init__(self, root):
        self.media = {}
        for m in root.iter(N + "observationMedia"):
            self.media[m.get("ID", "")] = _t(m.find(N + "text"))

    def inner(self, el):
        """The HTML of an element's content: its text, its children, their tails."""
        out = [html.escape(el.text or "")]
        for child in el:
            out.append(self.convert(child))
            out.append(html.escape(child.tail or ""))
        return "".join(out)

    def convert(self, el):
        """The HTML of one element of the label's narrative text."""
        tag = el.tag.replace(N, "")
        if tag == "paragraph":
            return f"<p>{self.inner(el)}</p>"
        if tag == "list":
            kind = "ol" if el.get("listType") == "ordered" else "ul"
            caption = el.find(N + "caption")
            head = f"<p><strong>{html.escape(_t(caption))}</strong></p>" if caption is not None else ""
            items = "".join(f"<li>{self.inner(i)}</li>" for i in el.findall(N + "item"))
            return f"{head}<{kind}>{items}</{kind}>"
        if tag == "item":
            return f"<li>{self.inner(el)}</li>"
        if tag == "caption":
            return ""                             # written by its list or table
        if tag == "table":
            caption = el.find(N + "caption")
            cap = f"<caption>{self.inner(caption)}</caption>" if caption is not None else ""
            rows = "".join(self.convert(c) for c in el if c.tag.replace(N, "") in ("thead", "tbody", "tfoot", "tr"))
            return f"<table>{cap}{rows}</table>"
        if tag in ("thead", "tbody", "tfoot"):
            return f"<{tag}>{''.join(self.convert(c) for c in el if c.tag == N + 'tr')}</{tag}>"
        if tag == "tr":
            return f"<tr>{''.join(self.convert(c) for c in el if c.tag in (N + 'td', N + 'th'))}</tr>"
        if tag in ("td", "th"):
            span = "".join(f' {a}="{html.escape(el.get(a))}"' for a in ("colspan", "rowspan") if el.get(a))
            return f"<{tag}{span}>{self.inner(el)}</{tag}>"
        if tag in ("col", "colgroup", "footnoteRef"):
            return ""
        if tag == "content":
            style = (el.get("styleCode") or "").lower()
            text = self.inner(el)
            if "bold" in style:
                text = f"<strong>{text}</strong>"
            if "italics" in style:
                text = f"<em>{text}</em>"
            return text
        if tag in ("sup", "sub"):
            return f"<{tag}>{self.inner(el)}</{tag}>"
        if tag == "br":
            return "<br>"
        if tag == "linkHtml":
            href = el.get("href", "")
            if href.startswith(("http://", "https://")):
                return f'<a href="{html.escape(href)}">{self.inner(el)}</a>'
            return self.inner(el)
        if tag == "renderMultiMedia":
            alt = self.media.get(el.get("referencedObject", ""), "")
            return f"<p>Picture: {html.escape(alt)}</p>" if alt else ""
        if tag == "footnote":
            return f" (Footnote: {self.inner(el)})"
        return self.inner(el)

    def text(self, section):
        """The HTML of a section's own <text> ("" when it has none)."""
        t = section.find(N + "text")
        return self.convert(t) if t is not None else ""


@dataclass
class Section:
    """One section of a label: its LOINC code, its title as printed, its own HTML, its subsections."""
    code: str
    title: str
    body: str
    children: list = field(default_factory=list)


@dataclass
class Label:
    """One label read from its SPL XML (see read_label)."""
    setid: str
    version: str
    doc_code: str
    doc_name: str
    title: str
    date: str
    company: str
    products: list
    approval: str
    approval_kind: str
    schedule: str
    sections: list
    highlights: list
    homeopathic: bool = False
    brand: str = ""

    @property
    def animal(self):
        """True for an animal (veterinary) label."""
        return self.doc_code in ANIMAL_TYPES

    @property
    def kind(self):
        """"rx", "otc" or "animal" (or "" for any other document)."""
        if self.animal:
            return "animal"
        return "rx" if self.doc_code in RX_TYPES else ("otc" if self.doc_code == OTC_TYPE else "")


def read_label(xml_text):
    """The Label of an SPL XML document: its kind, company, date, products (name, generic names, form, route,
    active ingredients with strengths, inactive ingredients), FDA approval, controlled-substance schedule, sections
    (the product data section left out: its facts are in "Ingredients"), and the label's own Highlights."""
    root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    conv = SplHtml(root)
    code = root.find(N + "code")
    eff = root.find(N + "effectiveTime")
    org = root.find(f"{N}author/{N}assignedEntity/{N}representedOrganization/{N}name")
    products, approval, approval_kind, schedule, homeopathic = [], "", "", "", False
    for mp in root.iter(N + "manufacturedProduct"):
        inner = mp.find(N + "manufacturedProduct")
        if inner is None:
            inner = mp.find(N + "manufacturedMedicine")
        if inner is None:
            continue
        actives, inactives = [], []
        for ing in inner.findall(N + "ingredient"):
            sub = _t(ing.find(f"{N}ingredientSubstance/{N}name"))
            num = ing.find(f"{N}quantity/{N}numerator")
            den = ing.find(f"{N}quantity/{N}denominator")
            if ing.get("classCode", "").startswith("ACT"):
                strength = ""
                if num is not None and num.get("value"):
                    unit = num.get("unit", "")
                    homeopathic |= unit.startswith("[hp_")
                    strength = f"{num.get('value')} {unit if unit != '1' else ''}".strip()
                    if den is not None and den.get("value") and (den.get("value"), den.get("unit")) != ("1", "1"):
                        strength += f" in {den.get('value')} {den.get('unit') if den.get('unit') != '1' else ''}"
                actives.append((sub, strength.strip()))
            elif ing.get("classCode") == "IACT" and sub:
                inactives.append(sub)
        form = inner.find(N + "formCode")
        route = mp.find(f".//{N}routeCode")
        products.append({"name": _t(inner.find(N + "name")),
                         "generic": _t(inner.find(f"{N}asEntityWithGeneric/{N}genericMedicine/{N}name")),
                         "form": form.get("displayName", "") if form is not None else "",
                         "route": route.get("displayName", "") if route is not None else "",
                         "actives": actives, "inactives": inactives})
        ap = mp.find(f".//{N}approval")
        if ap is not None and not approval:
            i, c = ap.find(N + "id"), ap.find(N + "code")
            approval = (i.get("extension", "") if i is not None else "") or ""
            approval_kind = c.get("displayName", "") if c is not None else ""
        for pol in mp.iter(N + "policy"):
            if pol.get("classCode") == "DEADrugSchedule":
                pc = pol.find(N + "code")
                schedule = pc.get("displayName", "") if pc is not None else ""
    sections, highlights = [], []

    def section(el):
        """A Section and its subsections."""
        kids = [section(c.find(N + "section")) for c in el.findall(N + "component")
                if c.find(N + "section") is not None]
        return Section(_code(el), _t(el.find(N + "title")), conv.text(el), kids)
    body = root.find(f"{N}component/{N}structuredBody")
    for comp in (body.findall(N + "component") if body is not None else []):
        el = comp.find(N + "section")
        if el is None or _code(el) == "48780-1":
            continue
        sections.append(section(el))
        for hl in el.iter(N + "highlight"):
            t = hl.find(N + "text")
            if t is not None and _t(t):
                title = re.sub(r"^\s*\d+(\.\d+)*\s+", "", _t(el.find(N + "title"))) or \
                    {"34066-1": "Boxed warning", "43683-2": "Recent major changes"}.get(_code(el), "")
                highlights.append((_code(el), title, conv.convert(t)))
    highlights.sort(key=lambda h: h[0] != "34066-1")          # the boxed warning first
    return Label(setid=(root.find(N + "setId").get("root", "") if root.find(N + "setId") is not None else ""),
                 version=(root.find(N + "versionNumber").get("value", "")
                          if root.find(N + "versionNumber") is not None else ""),
                 doc_code=code.get("code", "") if code is not None else "",
                 doc_name=code.get("displayName", "") if code is not None else "",
                 title=_t(root.find(N + "title")), date=B.iso_date(eff.get("value", "") if eff is not None else ""),
                 company=_t(org), products=products, approval=approval, approval_kind=approval_kind,
                 schedule=schedule, sections=sections, highlights=highlights, homeopathic=homeopathic)


# The parts of an entry, in the plain order of every page, and the label sections (LOINC codes) that go in each.
PARTS = [
    ("uses", "What it is for", "What it is for"),
    ("dosing", "How to take it", "How to give it"),
    ("warnings", "Warnings", "Warnings"),
    ("side_effects", "Side effects", "Side effects"),
    ("interactions", "Interactions", "Interactions"),
    ("storage", "Storage", "Storage"),
    ("pregnancy", "Pregnancy and breastfeeding", "Pregnancy, breeding and nursing"),
    ("patients", "Information for patients", "Information for owners"),
    ("other", "Other parts of the label", "Other parts of the label"),
]
PART_OF = {
    "34067-9": "uses", "55105-1": "uses", "55106-9": "uses",
    "34068-7": "dosing", "43678-2": "dosing",
    "34066-1": "warnings", "34070-3": "warnings", "43685-7": "warnings", "34071-1": "warnings", "42232-9": "warnings",
    "50570-1": "warnings", "50569-3": "warnings", "50568-5": "warnings", "50567-7": "warnings", "50566-9": "warnings",
    "50565-1": "warnings", "34088-5": "warnings", "50741-8": "warnings", "34072-9": "warnings", "60562-6": "warnings",
    "34084-4": "side_effects",
    "34073-7": "interactions", "34074-5": "interactions",
    "44425-7": "storage", "34069-5": "storage", "60561-8": "storage",
    "42228-7": "pregnancy", "34077-8": "pregnancy", "34078-6": "pregnancy", "34079-4": "pregnancy",
    "34080-2": "pregnancy", "77290-5": "pregnancy", "77291-3": "pregnancy", "53414-9": "pregnancy",
    "42231-1": "patients", "42230-3": "patients", "34076-0": "patients", "59845-8": "patients", "50744-2": "patients",
    "88436-1": "patients",
}
MOVED = {"pregnancy", "interactions", "patients", "side_effects"}   # pulled out of a parent of another part
NONE_SAID = "The label has no separate section on this."


def part_of(sec, title_hint=True):
    """The part a section belongs to: by its LOINC code, or (for an unclassified section) by the words of its title
    ("Other information" of a Drug Facts label is storage; "Inactive ingredients" stays with the other parts)."""
    part = PART_OF.get(sec.code)
    if part:
        return part
    t = sec.title.lower()
    if title_hint and sec.code == "42229-5":
        if re.match(r"^\s*other information", t):
            return "storage"
        if re.search(r"\bstorage\b|\bstore\b", t):
            return "storage"
    return "other"


def sort_sections(sections):
    """{part: [(Section, depth note)]}: every top-level section in its part, in the label's order, with the
    subsections of other parts pulled out of their parent (the Pregnancy and Nursing mothers subsections of "Use in
    specific populations" or "Precautions", the "If pregnant or breast-feeding" of a Drug Facts "Warnings"), and the
    package label (the carton's text) last among the other parts."""
    parts = {p[0]: [] for p in PARTS}
    panels = []

    def pull(sec, parent_part):
        """Take out of sec the subsections that belong to another part (MOVED), anywhere below it."""
        kept = []
        for child in sec.children:
            cp = part_of(child, title_hint=False)
            if cp in MOVED and cp != parent_part:
                parts[cp].append(child)
            else:
                pull(child, parent_part)
                kept.append(child)
        sec.children = kept
    for sec in sections:
        part = part_of(sec)
        pull(sec, part)
        if sec.code == "51945-4":
            panels.append(sec)
        elif sec.code == "34066-1":
            parts["warnings"].insert(0, sec)          # the boxed warning first
        else:
            parts[part].append(sec)
    parts["other"] += panels
    return parts


def section_html(sec, level, fallback=""):
    """The HTML of a section: its title as a heading of `level` (at most 6), its text, its subsections."""
    title = sec.title or fallback
    head = f"<h{min(level, 6)}>{html.escape(title)}</h{min(level, 6)}>" if title else ""
    return head + sec.body + "".join(section_html(c, level + 1) for c in sec.children)


SECTION_NAMES = {"34066-1": "Boxed warning", "34067-9": "Uses", "34068-7": "Directions", "34071-1": "Warnings",
                 "42230-3": "Patient package insert", "42231-1": "Medication Guide", "51945-4": "Package label",
                 "34069-5": "How supplied", "44425-7": "Storage and handling"}


def first_sentence(sections_html, limit=320):
    """The first sentence of some HTML (for "what it is for" in the label's own words), at most `limit` letters."""
    words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", sections_html)).split())
    words = re.sub(r"^\s*(\d+(\.\d+)*\s+)?INDICATIONS?\s*(AND|&)\s*USAGE\s*:?\s*", "", words, flags=re.I)
    words = re.sub(r"^(INDICATIONS?|USES?)\s*:?\s*", "", words, flags=re.I)
    sentences = [m.group(1) for m in re.finditer(r"(.{20,}?[.;])(?=\s|$)", words)] or [words]
    # The label's own words on what it treats, not the class's opening caution ("Carefully consider the
    # potential benefits and risks ...").
    text = next((x.strip() for x in sentences if re.search(r"\b(indicated|used|treat\w*|reliev\w*|relief|"
                                                             r"prevent\w*|control\w*|reduc\w*)\b", x, re.I)
                 and not re.match(r"\s*carefully consider", x, re.I)), sentences[0].strip())
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def ingredients_html(label):
    """The products of a label and their ingredients (active with strength, inactive), as a list."""
    out, seen = [], set()
    for p in label.products:
        actives = "; ".join(f"{a} {s}".strip() for a, s in p["actives"])
        key = (p["name"], p["form"], actives)
        if key in seen or not (p["name"] or actives):
            continue
        seen.add(key)
        line = f"<strong>{html.escape(p['name'].strip() or p['generic'])}</strong>"
        line += f", {html.escape(p['form'].lower())}" if p["form"] else ""
        line += f" ({html.escape(p['route'].lower())})" if p["route"] else ""
        line += f". Active: {html.escape(actives)}" if actives else ""
        line += f". Inactive: {html.escape(', '.join(p['inactives']).lower())}" if p["inactives"] else ""
        out.append(f"<li>{line}.</li>")
    return f"<ul>{''.join(out)}</ul>" if out else ""


def approval_words(label, fda):
    """"FDA application: NDA 020402, held by PFIZER, first approved 1995-04-20." from the label's approval and
    Drugs@FDA (the company that holds the application now);
    "OTC monograph M013" for an over-the-counter monograph product; "" when the label names none."""
    a = label.approval
    if not a:
        return ""
    m = re.match(r"^(NDA|ANDA|BLA|NADA|ANADA|BN|CNDA)(\d+)$", a)
    if not m:
        kind = label.approval_kind or "Marketing category"
        return f"Marketing category: {kind} {a}."
    words = f"FDA application: {m.group(1)} {m.group(2)}"
    info = fda.get(a) or fda.get(f"{m.group(1)}{m.group(2).zfill(6)}")
    if info:
        words += f", held by {info['sponsor']}" if info.get("sponsor") else ""
        words += f", first approved {info['approved']}" if info.get("approved") else ""
    return words + "."


def label_html(label, heading, fda, level=2):
    """The HTML of one label on a medicine's page: its heading, where it comes from, its ingredients, the label's
    own highlights, then every part in the plain order (a part the label lacks says so)."""
    vet = label.animal
    original = f"{DAILYMED}/drugInfo.cfm?setid={label.setid}"
    out = [f"<h{level}>{html.escape(heading)}</h{level}>"]
    facts = [f"Label by {html.escape(label.company)}" if label.company else "Label",
             f"version {html.escape(label.version)}" if label.version else "",
             f"dated {html.escape(label.date)}" if label.date else ""]
    line = ", ".join(x for x in facts if x) + "."
    approval = approval_words(label, fda)
    if approval:
        line += " " + html.escape(approval)
    if label.schedule:
        line += f" Controlled substance, schedule {html.escape(label.schedule)}."
    out.append(f'<p>{line} Original: <a href="{html.escape(original)}">{html.escape(original)}</a>.</p>')
    ingredients = ingredients_html(label)
    if ingredients:
        out.append(f"<h{level + 1}>Ingredients</h{level + 1}>{ingredients}")
    if label.highlights:
        out.append(f"<h{level + 1}>Highlights (the label's own summary)</h{level + 1}>")
        for _code_, title, body in label.highlights:
            out.append((f"<h{level + 2}>{html.escape(title)}</h{level + 2}>" if title else "") + body)
    parts = sort_sections(read_label_copy(label))
    for key, human, animal in PARTS:
        out.append(f"<h{level + 1}>{animal if vet else human}</h{level + 1}>")
        if parts[key]:
            out += [section_html(s, level + 2, SECTION_NAMES.get(s.code, "")) for s in parts[key]]
        else:
            out.append(f"<p>{NONE_SAID}</p>")
    return "\n".join(out)


def uses_sentence(label):
    """What the medicine is for, in the label's own first sentence (its Highlights' indications, else its
    Indications or Uses, or its Purpose)."""
    for code, _title, body in label.highlights:
        if code == "34067-9" and first_sentence(body):
            return first_sentence(body)
    parts = sort_sections(read_label_copy(label))
    for code in ("34067-9", "55105-1"):
        for sec in parts["uses"]:
            if sec.code == code:
                text = first_sentence(section_html(sec, 4))
                if text:
                    return text
    return ""


def read_label_copy(label):
    """A copy of a label's sections (sort_sections changes the sections it is given)."""
    def copy(s):
        """A copy of one section."""
        return Section(s.code, s.title, s.body, [copy(c) for c in s.children])
    return [copy(s) for s in label.sections]


# ====================================================================== species (animal labels)

PETS = re.compile(r"\b(dogs?|puppy|puppies|canines?|cats?|kittens?|felines?|horses?|equine|foals?|ponies|pony|"
                  r"ferrets?|rabbits?|pet|pets|companion animals?|mares?|stallions?|geldings?)\b", re.I)
FARM = re.compile(r"\b(cattle|cows?|calf|calves|heifers?|steers?|bulls?|beef|dairy|swine|pigs?|hogs?|sows?|"
                  r"piglets?|gilts?|boars?|chickens?|broilers?|layers?|turkeys?|poultry|sheep|lambs?|ewes?|goats?|"
                  r"kids|fish|catfish|salmonids?|trout|honey ?bees?|ducks?|quail|pheasants?|livestock|bison)\b", re.I)


def species(label):
    """{"pets", "farm"}: the books an animal label belongs in, from the words of its title, uses and directions
    (dogs, cats, horses: "pets"; cattle, pigs, poultry, sheep, goats, fish, bees: "farm"); a label that names
    neither goes with the pets."""
    parts = sort_sections(read_label_copy(label))
    words = label.title + " " + " ".join(re.sub(r"<[^>]+>", " ", section_html(s, 4))
                                         for s in parts["uses"] + parts["dosing"])
    found = set()
    if PETS.search(words):
        found.add("pets")
    if FARM.search(words):
        found.add("farm")
    return found or {"pets"}


# ====================================================================== the books

@dataclass
class Medicine:
    """One medicine (one ingredient or a combination) of one kind: its key, ingredient names, brand names (US and
    Canadian), and its chosen labels with the form each stands for."""
    key: str
    names: set
    kind: str
    brands: set = field(default_factory=set)
    canada: set = field(default_factory=set)
    labels: list = field(default_factory=list)       # [(form words, Label)]


BOOKS = {
    "rx": dict(title="Prescription medicines {letters} (US drug labels)", group=GROUP_HUMAN,
               subject="Medicines (prescription)", notice=HUMAN_NOTICE,
               description="The official US labels (package inserts) of prescription medicines whose generic name "
                           "starts with {letters}, with their Medication Guides and patient leaflets: what each is "
                           "for, how to take it, warnings (the boxed warning first), side effects, interactions, "
                           "storage, pregnancy and breastfeeding. Brand names lead to their medicine. "),
    "otc": dict(title="Over-the-counter medicines {letters} (US Drug Facts)", group=GROUP_HUMAN,
                subject="Medicines (over the counter)", notice=HUMAN_NOTICE,
                description="The official US Drug Facts labels of medicines sold without a prescription whose "
                            "generic name starts with {letters}: uses, directions, warnings, when to ask a doctor, "
                            "storage, pregnancy and breastfeeding. Brand names lead to their medicine. "),
    "pets": dict(title="Pet and horse medicines (US animal drug labels)", group=GROUP_VET,
                 subject="Veterinary medicines (pets and horses)", notice=VET_NOTICE,
                 description="The official US labels of medicines for dogs, cats, horses and other pets, with their "
                             "information for owners: what each is for, how to give it, warnings, side effects, "
                             "storage and use in breeding animals. Brand names lead to their medicine. "),
    "farm": dict(title="Farm animal medicines (US animal drug labels)", group=GROUP_VET,
                 subject="Veterinary medicines (farm animals)", notice=VET_NOTICE,
                 description="The official US labels of medicines and medicated feeds for cattle, pigs, poultry, "
                             "sheep, goats, fish and bees: what each is for, how to give it, warnings (including "
                             "withdrawal times before meat, milk or eggs are used), side effects and storage. Brand "
                             "names lead to their medicine. "),
}


def letters_words(piece):
    """"e-f" -> "E to F", "a" -> "A", "u-z" -> "U to Z"."""
    low, _, high = piece.partition("-")
    return f"{low.upper()} to {high.upper()}" if high else low.upper()


def about_page(kind, vet):
    """The book's first page: what it holds, how a page reads, where the text comes from, and the notice."""
    notice = VET_NOTICE if vet else HUMAN_NOTICE
    ask = "a veterinarian" if vet else "a pharmacist or doctor"
    order = ", ".join(p[2] if vet else p[1] for p in PARTS)
    return (f"<p><strong>{notice}</strong> These are the medicines' official labels, as the companies that make "
            f"them wrote them and the FDA approved or listed them. A label is not a substitute for {ask}, who knows "
            "the person or animal it is for.</p>"
            "<h2>How a page reads</h2><p>One page per medicine, named by its generic name; a brand name leads to its "
            "medicine, and the page Brand names A to Z lists them all. A medicine sold in several forms (tablets, an "
            "injection, a cream) has one label for each form. Every label starts with where it comes from and its "
            "ingredients, then its own Highlights when it has them, then always the same parts in this order: "
            f"{order}. A part the label does not have says \"{NONE_SAID}\"</p>"
            "<h2>Which label is shown</h2><p>Many companies sell the same medicine with nearly the same label. For "
            "each medicine and form the book shows one: the brand's label when there is one, otherwise one that is "
            "not a repackager's, the newest. The address of the original label in DailyMed is on each label; "
            "DailyMed also has every other company's label.</p>"
            f"<h2>Where the text comes from</h2><p>{html.escape(LABEL_NOTICE)} {html.escape(FDA_CREDIT)} Canadian "
            f"brand names: Health Canada's Drug Product Database. {html.escape(OGL_CANADA_NOTICE)}</p>")


def medicine_page(med, fda):
    """(page path, title, body HTML) of one medicine: the notice, its quick facts, then each of its labels."""
    vet = med.kind == "animal"
    name = display_name(med.names)
    kind = {"rx": "prescription medicine (US)", "otc": "over-the-counter medicine (US)"}.get(med.kind,
                                                                                         "animal medicine (US)")
    facts = [f"<li>Kind: {kind}.</li>"]
    brands = sorted(med.brands, key=str.casefold)
    if brands:
        shown = ", ".join(brands[:80]) + (f", and {len(brands) - 80} more" if len(brands) > 80 else "")
        facts.append(f"<li>Brand names (US): {html.escape(shown)}.</li>")
    canada = sorted(med.canada - set(brands), key=str.casefold)
    if canada:
        shown = ", ".join(canada[:60]) + (f", and {len(canada) - 60} more" if len(canada) > 60 else "")
        facts.append(f"<li>Brand names in Canada (Health Canada): {html.escape(shown)}.</li>")
    facts.append("<li>Forms on this page: " + html.escape("; ".join(f for f, _ in med.labels)) + ".</li>")
    boxed = [f for f, lab in med.labels if any(s.code == "34066-1" for s in lab.sections)]
    if boxed:
        facts.append("<li>Boxed warning (the FDA's strongest warning): yes"
                     + (f" ({html.escape('; '.join(boxed))})" if len(med.labels) > 1 else "")
                     + ". It is the first thing under Warnings.</li>")
    uses = next((u for u in (uses_sentence(lab) for _f, lab in med.labels) if u), "")
    if uses:
        facts.append(f"<li>What it is for, in the label's words: “{html.escape(uses)}”</li>")
    out = [f"<p><strong>{VET_NOTICE if vet else HUMAN_NOTICE}</strong></p>", "<h2>Quick facts</h2>",
           f"<ul>{''.join(facts)}</ul>"]
    for form, lab in med.labels:
        brand = brand_words(lab.brand, med.key) or lab.company or lab.title
        heading = f"{name}, {form}: label of {brand}"
        out.append(label_html(lab, heading, fda))
    return B.slug(name, 80), name, "\n".join(out)


def make_book(kind, piece, medicines, fda, only=False):
    """The Book of medicines of one kind ("rx", "otc", "pets", "farm"), with its about page, its brand index and
    one page per medicine (in name order, grouped by first letter); brand names become titles of their own
    (redirects to the medicine's page)."""
    spec = BOOKS[kind]
    letters = letters_words(piece) if piece else ""
    vet = kind in ("pets", "farm")
    name = {"rx": f"medicines_us_prescription_{piece.replace('-', '_')}",
            "otc": f"medicines_us_otc_{piece.replace('-', '_')}",
            "pets": "medicines_us_pets", "farm": "medicines_us_farm_animals"}[kind] + ("_sample" if only else "")
    book = B.Book(name=name, title=spec["title"].format(letters=letters) + (" (sample)" if only else ""),
                  subject=spec["subject"], level="reference", group=spec["group"],
                  publisher="US National Library of Medicine (DailyMed) and the companies whose labels they are",
                  country="United States", licence=LICENCE, licence_url=OPENFDA_LICENSE, source=DAILYMED + "/",
                  description=spec["description"].format(letters=letters) + spec["notice"],
                  notice=f"{spec['notice']} {LABEL_NOTICE} {FDA_CREDIT} {OGL_CANADA_NOTICE}",
                  changes="made into web pages, one page per medicine, the label's sections put in a plain order "
                          "(nothing reworded); pictures left out (their descriptions kept)")
    book.redirects = []
    pages, brand_rows, dates = [], [], []
    used = {"index", "about-this-book", "brand-names-a-to-z", "style-css"}
    for med in sorted(medicines, key=lambda m: display_name(m.names).casefold()):
        path, title, body = medicine_page(med, fda)
        while path in used:
            path += "-2"
        used.add(path)
        letter = title[:1].upper() if title[:1].isalpha() else "0-9"
        pages.append(B.Page(path, title, body, 0, letter))
        dates += [lab.date for _f, lab in med.labels]
        # Each label's official SPL XML file (what the page was made from) is one of the book's originals.
        book.originals += [{"url": f"{DM_SERVICES}/spls/{lab.setid}.xml", "kind": "xml"} for _f, lab in med.labels
                           if lab.setid]
        for brand in sorted(med.brands | med.canada, key=str.casefold):
            brand_rows.append((brand, title, path))
    if not pages:
        return book
    rows = sorted(brand_rows, key=lambda r: (r[0].casefold(), r[1].casefold()))
    seen = set()
    for brand, title, path in rows:
        rpath = "brand/" + B.slug(brand, 70)
        if rpath not in seen and B.slug(brand, 70) != path:
            seen.add(rpath)
            book.redirects.append((rpath, f"{brand} ({title})", path))
    index = "".join(f'<li>{html.escape(b)}: <a href="{html.escape(p)}">{html.escape(t)}</a></li>' for b, t, p in rows)
    book.pages = [B.Page("about-this-book", "About this book", about_page(kind, vet)),
                  B.Page("brand-names-a-to-z", "Brand names A to Z",
                         f"<p>Each brand name and the medicine it is.</p><ul>{index}</ul>" if rows else
                         "<p>No brand names in this book.</p>")] + pages
    book.published = B.newest_date(dates)
    return book


# ====================================================================== collecting the medicines of a piece

def _only_match(only, key, names, brands):
    """True when a medicine is one of the --only names (its generic name, salt or not, or one of its brands)."""
    if not only:
        return True
    words = {base_name(o) for o in only} | {o.lower() for o in only}
    return key in words or any(b.lower() in words for b in brands)


def human_medicines(kind, piece, cache=None, left_out=None, only=None, fda=None):
    """The Medicines of one human piece ("rx" or "otc", letters "a" or "e-f"): DailyMed's mapping files group the
    labels by generic medicine and form; the prescription listing says which are prescription; the best label of
    each medicine and form is read (another one when it turns out to be of another kind or homeopathic)."""
    left_out = left_out if left_out is not None else []
    rx = dailymed_listing(list(RX_TYPES), cache)
    kits, maker_words = set(), makers(fda)
    records = rxnorm_records(_zip_text(f"{DM_DATA}/rxnorm_mappings.zip", "rxnorm_mappings.txt", cache), kits)
    meta = meta_records(_zip_text(f"{DM_DATA}/dm_spl_zip_files_meta_data.zip", "meta_data.txt", cache))
    groups = {}
    for setid, rec in records.items():
        is_rx = setid in rx
        if (kind == "rx") != is_rx:
            continue
        key = combo_key(rec["names"])
        title, date, version = meta.get(setid, (rx.get(setid, {}).get("title", ""), "", rec["version"]))
        brand, _generics, _form, company = parse_title(title)
        g = groups.setdefault(key, {"names": {}, "brands": set(), "forms": {}})
        for n in rec["names"]:
            g["names"][n.lower()] = g["names"].get(n.lower(), 0) + 1
        g["brands"] |= rec["brands"]
        for family in rec["forms"]:
            g["forms"].setdefault(family, []).append({"setid": setid, "sbd": bool(rec["brands"]), "brand": bool(brand),
                                                      "maker": first_word(company) in maker_words,
                                                      "company": company, "date": date, "version": version})
    medicines = []
    for key, g in groups.items():
        names = choose_names(g["names"])
        if not in_piece(display_name(names), piece, RX_PIECES if kind == "rx" else OTC_PIECES) and not only:
            continue
        if not _only_match(only, key, names, g["brands"]):
            continue
        med = Medicine(key=key, names=set(names), kind=kind,
                       brands={b for b in (brand_words(x, key) for x in g["brands"]) if b})
        for family in sorted(g["forms"], key=lambda f: (-len(g["forms"][f]), f))[:MAX_FORMS]:
            for cand in sorted(g["forms"][family], key=rank, reverse=True)[:MAX_TRIES]:
                try:
                    label = read_label(spl_xml(cand["setid"], cand["version"], cache))
                except (urllib.error.URLError, OSError, ET.ParseError, ValueError) as e:
                    left_out.append({"title": f"DailyMed label {cand['setid']}", "reason": f"Not read ({e})."})
                    continue
                if label.kind != kind or label.homeopathic:
                    continue
                label.brand = next((b for b in sorted(records[cand["setid"]]["brands"])), "") or \
                    parse_title(meta.get(cand["setid"], ("",))[0])[0]
                med.labels.append((family, label))
                break
        if med.labels:
            medicines.append(med)
    if kits and not only:
        left_out.append({"title": "Kits of several medicines", "reason": f"{len(kits)} labels of kits (first-aid kits, "
                         "allergen mixtures, kits of unrelated medicines) left out; each medicine is in the books from "
                         "its own label."})
    return medicines


def choose_names(counts):
    """The ingredient names a medicine is shown by: of the names that share a base name ("metformin hydrochloride",
    "metformin"), the one most labels use."""
    best = {}
    for n, c in counts.items():
        b = base_name(n)
        if b not in best or c > best[b][1]:
            best[b] = (n, c)
    return [n for n, _c in best.values()]


def animal_medicines(cache=None, left_out=None, only=None):
    """The Medicines of the animal books: DailyMed's listing of animal labels, grouped by the generic names and form
    of their titles; the best label of each medicine and form is read; homeopathic products are left out."""
    left_out = left_out if left_out is not None else []
    listing = dailymed_listing(list(ANIMAL_TYPES), cache)
    groups, homeopathic = {}, 0
    for setid, row in listing.items():
        brand, generics, form, company = parse_title(row["title"])
        if len(generics) > 5:                     # homeopathic mixtures (checked again in each label read)
            homeopathic += 1
            continue
        key = combo_key(generics)
        if not key:
            continue
        g = groups.setdefault(key, {"brands": set(), "forms": {}, "names": {}})
        for n in generics:
            g["names"][n.lower()] = g["names"].get(n.lower(), 0) + 1
        if brand_words(brand, key):
            g["brands"].add(brand_words(brand, key))
        family = (form.split(",")[0].strip().lower() or "other forms")
        g["forms"].setdefault(family, []).append({"setid": setid, "brand": bool(brand), "company": company,
                                                  "date": row["date"], "version": row["version"]})
    medicines = []
    for key, g in groups.items():
        names = choose_names(g["names"])
        if not _only_match(only, key, names, g["brands"]):
            continue
        med = Medicine(key=key, names=set(names), kind="animal", brands=set(g["brands"]))
        for family in sorted(g["forms"], key=lambda f: (-len(g["forms"][f]), f))[:MAX_FORMS]:
            for cand in sorted(g["forms"][family], key=rank, reverse=True)[:MAX_TRIES]:
                try:
                    label = read_label(spl_xml(cand["setid"], cand["version"], cache))
                except (urllib.error.URLError, OSError, ET.ParseError, ValueError) as e:
                    left_out.append({"title": f"DailyMed label {cand['setid']}", "reason": f"Not read ({e})."})
                    continue
                if not label.animal or label.homeopathic:
                    homeopathic += label.homeopathic
                    continue
                label.brand = parse_title(listing[cand["setid"]]["title"])[0]
                med.labels.append((family, label))
                break
        if med.labels:
            medicines.append(med)
    if homeopathic:
        left_out.append({"title": "Homeopathic animal products", "reason": f"{homeopathic} labels left out: their "
                         "labels list dilutions, not medicines."})
    return regroup(medicines)


def label_names(label):
    """The active ingredients a label itself names (its product data), without repeats; [] when it names none."""
    names = {}
    for p in label.products:
        for name, _strength in p["actives"]:
            if name.strip():
                names.setdefault(base_name(name), name.strip())
    return list(names.values())


def regroup(medicines):
    """The animal Medicines grouped again by the active ingredients their labels name (a title such as "3% IODINE
    TEAT DIP" or "A PALATABLE FORMULA FOR CATS" says the product, not its medicine): medicines whose labels name
    the same ingredients become one, with all their brands and at most MAX_FORMS labels (one per form)."""
    out = {}
    for med in medicines:
        names = label_names(med.labels[0][1]) or sorted(med.names)
        key = combo_key(names) or med.key
        if key not in out:
            out[key] = Medicine(key=key, names=set(choose_names({n.lower(): 1 for n in names})), kind=med.kind)
        target = out[key]
        target.brands |= med.brands
        for family, label in med.labels:
            if family not in {f for f, _l in target.labels} and len(target.labels) < MAX_FORMS:
                target.labels.append((family, label))
    return list(out.values())


def books_for_key(key, cache=None, left_out=None, only=None):
    """The Books of one key ("med:rx:a", "med:otc:c", "med:animal"), or [] when the labels' licence can no longer
    be confirmed (said in left_out)."""
    left_out = left_out if left_out is not None else []
    if not licence_still_open():
        left_out.append({"title": key, "reason": "openFDA's drug label API no longer names its public-domain "
                         "licence, so the labels' status could not be confirmed."})
        return []
    for url in (DM_SERVICES + "/spls.json", DM_DATA + "/rxnorm_mappings.zip"):
        if not B.allowed_by_robots(url, cache):
            left_out.append({"title": key, "reason": f"robots.txt does not allow {url}."})
            return []
    fda = drugs_at_fda(cache)
    canada = canadian_brands(cache)
    parts = key.split(":")
    if parts[1] in ("rx", "otc"):
        meds = human_medicines(parts[1], parts[2], cache, left_out, only, fda)
        for m in meds:
            m.canada = canada.get((parts[1], m.key), set())
        return [make_book(parts[1], parts[2], meds, fda, bool(only))]
    meds = animal_medicines(cache, left_out, only)
    books = []
    for kind in ("pets", "farm"):
        chosen = []
        for m in meds:
            labels = [(f, lab) for f, lab in m.labels if kind in species(lab)]
            if labels:
                chosen.append(Medicine(key=m.key, names=m.names, kind="animal", brands=m.brands,
                                       canada=canada.get(("animal", m.key), set()), labels=labels))
        books.append(make_book(kind, "", chosen, fda, bool(only)))
    return books


# ====================================================================== the weekly check and the build

def sign(key):
    """The sign of change of a medicine key (updates.py): the name of DailyMed's newest monthly update file
    ("dm_spl_monthly_update_oct2026.zip"), so the books are built again once a month, after DailyMed's monthly
    release ("" when the downloads page cannot be read: then nothing is rebuilt)."""
    try:
        found = re.findall(r"dm_spl_monthly_update_([a-z]{3})(\d{4})\.zip", B.fetch(DM_DOWNLOADS, None))
    except (urllib.error.URLError, OSError):
        return ""
    if not found:
        return ""
    newest = max(found, key=lambda m: (m[1], B.MONTHS.get(m[0], 0)))
    return f"dailymed-{newest[1]}-{B.MONTHS.get(newest[0], 0):02d}"


def release_url():
    """The download address of the medicines' release."""
    return f"{B.RELEASE.rsplit('/', 1)[0]}/{RELEASE}"


def build_medicines(keys, out_dir, cache=None, date=None, only=None):
    """Build the books of keys (see expand_keys) into out_dir, write manifest-<key>.json for each key (as
    build_textbooks.build does) and return {key: manifest}. Every book is kept as a new version (versioned file
    names); only: build just these medicines (a test build; the books are named "..._sample")."""
    manifests = {}
    os.makedirs(out_dir, exist_ok=True)
    for key in expand_keys(keys):
        left_out, entries = [], []
        try:
            books = books_for_key(key, cache, left_out, only)
        except Exception as e:  # noqa: BLE001 - one key's failure does not stop the others; said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            books = []
        fingerprint = sign(key) if not only else ""
        for book in books:
            if not book.pages:
                left_out.append({"title": book.title, "reason": "No labels could be read."})
                continue
            entry = B.write_book(book, out_dir, date, versioned=True)
            entry.update({"key": key, "fingerprint": fingerprint, "release": RELEASE,
                          "url": f"{release_url()}/{entry['file']}", "items": len(book.pages) - 2,
                          "group_name": {GROUP_HUMAN: "Reference, medicines",
                                         GROUP_VET: "Reference, animal medicines"}[book.group],
                          "note": VET_NOTICE if book.group == GROUP_VET else HUMAN_NOTICE})
            print(f"{entry['file']}: {entry['items']} medicines, {entry['size']:,} bytes")
            entries.append(entry)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": RELEASE, "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if only else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["medicines"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--only", default="", help="build only these medicines (generic or brand names, commas)")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    only = [x.strip() for x in a.only.split(",") if x.strip()] or None
    build_medicines(a.keys, a.out, a.cache, only=only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
