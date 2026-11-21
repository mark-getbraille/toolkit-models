"""The official label and safety-sheet sources of the chemical collections (manuals/chemicals.py), read by
manuals/build_manuals.py. Each gives index entries in the same shape as the other sources (brand, model, name, type,
category, the addresses of the documents): facts and links only, never the documents themselves.

  EPA pesticide labels    the US EPA's Pesticide Product Information System bulk files (PPIS,
      https://www.epa.gov/ingredients-used-pesticide-products/ppis-download-product-information-data): every
      registered pesticide product (weed killers, insect killers, rodent baits, disinfectants and sanitisers, pool
      and spa sanitisers and algaecides, wood preservatives, antifouling paints, insect repellents ...), with its
      EPA registration number, name, registrant, product types, use sites and whether it is a Restricted Use
      Pesticide; and the address of its newest official label PDF in the Pesticide Product Label System (PPLS),
      read from the www3.epa.gov sitemaps that list every label file. US government data (public domain). The
      www3.epa.gov robots.txt allows these files (it asks for a crawl delay of 1 second, kept: build_manuals.GAPS).
      NOT used: the PPLS search service on ordspub.epa.gov, whose robots.txt disallows every program.
  Health Canada pesticide labels    the Pesticide Product Information Database extract of Health Canada's Pest
      Management Regulatory Agency (open.canada.ca dataset e10b0d6e-04ac-4014-a64a-666c3874bbe0, CSV from
      pest-control.canada.ca/pesticide-registry-api/api/extract/product), under the Open Government Licence -
      Canada: every product registered in Canada, current ones only, with its registration number, name, registrant,
      product type, marketing class (DOMESTIC: sold for home use) and use sites; the link is the registry's own
      product page, which lists the product's label files. (pest-control.canada.ca publishes no robots.txt.)
  NIOSH Pocket Guide    the US National Institute for Occupational Safety and Health's Pocket Guide to Chemical
      Hazards (public domain, a US government work): its index by CAS number (www.cdc.gov/niosh/npg/npgdcas.html,
      allowed by robots.txt) gives about 680 chemicals with their Pocket Guide page. Each entry also links the same
      chemical in NOAA's CAMEO Chemicals (public domain; a link for the person to open: its search is disallowed to
      programs, so the builder never reads it) and in PubChem (the US National Library of Medicine; its compound
      page by CAS number, again a link only: PubChem's robots.txt disallows its PUG REST service, so the builder
      does not call it).

Nothing here is downloaded for publishing: the labels, guides and data sheets stay at their official addresses and
the toolkit fetches each for the owner's own use.
"""

import csv
import html
import io
import re
import urllib.parse
import zipfile

PPIS = "https://www3.epa.gov/pesticides/PPISdata/"
PPIS_FILES = {"product": "product.zip", "type": "prodtype.zip", "company": "company.zip", "site": "prodsite.zip",
              "typename": "typename.zip", "sitename": "sitename.zip"}
EPA_SITEMAP = "https://www3.epa.gov/sitemaps/pesticides_{}.xml"
EPA_SITEMAPS = 40                 # pesticides_0.xml ... (the builder stops at the first that is missing)
EPA_PRODUCT_PAGE = "https://ordspub.epa.gov/ords/pesticides/f?p=PPLS:102:::NO::P102_REG_NUM:{}"
EPA_LABEL = re.compile(r"https://www3\.epa\.gov/pesticides/chem_search/ppls/(\d{6})-(\d{5})-(\d{8})\.pdf")
EPA_SOURCE = ("the US EPA's Pesticide Product Information System and Pesticide Product Label System (US "
              "government data, public domain)")
EPA_RIGHTS = "an official label approved by the US EPA, published by the EPA for the public"

PMRA_CSV = "https://pest-control.canada.ca/pesticide-registry-api/api/extract/product"
PMRA_PAGE = "https://pest-control.canada.ca/pesticide-registry/en/product-details.html?regNum={}"
PMRA_SOURCE = ("Health Canada's Pesticide Product Information Database. Contains information licensed under the "
               "Open Government Licence - Canada")
PMRA_RIGHTS = "an official label registered by Health Canada; the registry's page lists its label files"

NIOSH_INDEX = "https://www.cdc.gov/niosh/npg/npgdcas.html"
NIOSH_BASE = "https://www.cdc.gov/niosh/npg/"
CAMEO_SEARCH = "https://cameochemicals.noaa.gov/search/simple?st=chemicals&na={}"
PUBCHEM_PAGE = "https://pubchem.ncbi.nlm.nih.gov/compound/{}"
NIOSH_SOURCE = "the NIOSH Pocket Guide to Chemical Hazards (US government work, public domain)"


# ------------------------------------------------------------------------------------------------- EPA (PPIS)

def zip_text(data):
    """The text of the one file in a PPIS zip (they are plain ASCII, read as Latin-1 so no byte fails)."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name = [n for n in z.namelist() if not n.endswith("/")][0]
        return z.read(name).decode("latin-1")


def epa_reg(reg_nr):
    """The EPA registration number as a label prints it: "00000300001" -> "3-1"; a distributor's or supplemental
    number has more parts, but the PPIS files hold only company-product numbers."""
    reg_nr = reg_nr.strip().zfill(11)
    return f"{int(reg_nr[:6])}-{int(reg_nr[6:11])}"


def parse_epa_products(text):
    """{11-digit registration number: (product name, restricted use)} of the ACTIVE products in PRODUCT.TXT (fixed
    columns: REG_NR 1-11, CAN_DATE 23-30 "00000000" and CT_CODE 31-32 blank for an active product, PROD_NAME
    33-102, RUP_FLAG 103 "T" for a Restricted Use Pesticide)."""
    out = {}
    for line in text.splitlines():
        if len(line) < 103 or not line[:11].strip().isdigit():
            continue
        if line[22:30] != "00000000" or line[30:32].strip():
            continue
        name = " ".join(line[32:102].split())
        if name:
            out[line[:11]] = (name, line[102:103] == "T")
    return out


def parse_epa_pairs(text, width):
    """{registration number: [codes]} of a PPIS file of registration number (11 digits) and code (width digits):
    PRODTYPE.TXT (2) and PRODSITE.TXT (9)."""
    out = {}
    for line in text.splitlines():
        if len(line) >= 11 + width and line[:11].isdigit():
            out.setdefault(line[:11], []).append(line[11:11 + width])
    return out


def parse_epa_names(text, width):
    """{code: description} of a PPIS vocabulary file: TYPENAME.TXT (2-digit codes) and SITENAME.TXT (9)."""
    out = {}
    for line in text.splitlines():
        code, desc = line[:width], " ".join(line[width:].split())
        if code.strip().isdigit() and desc:
            out[code] = desc
    return out


def parse_epa_companies(text):
    """{6-digit company number: its name} from COMPANY.TXT (CO_NR 1-6, CO_NAME 7-66)."""
    out = {}
    for line in text.splitlines():
        if len(line) > 7 and line[:6].isdigit():
            name = " ".join(line[6:66].split())
            if name:
                out[line[:6]] = name
    return out


def epa_label_urls(sitemap_texts):
    """{11-digit registration number: (date, the address of its newest label PDF)} from the www3.epa.gov sitemaps,
    which list every label file of the PPLS as chem_search/ppls/<company 6>-<product 5>-<yyyymmdd>.pdf."""
    out = {}
    for text in sitemap_texts:
        for m in EPA_LABEL.finditer(text):
            reg, date = m.group(1) + m.group(2), m.group(3)
            if reg not in out or date > out[reg][0]:
                out[reg] = (date, m.group(0))
    return out


def company_name(name):
    """A registrant's name in ordinary capitals: "THE SCOTTS COMPANY LLC" -> "The Scotts Company LLC"."""
    small = {"and", "of", "the", "for", "a", "an", "dba", "d/b/a"}
    keep = {"LLC", "LP", "LLP", "USA", "US", "PLC", "AG", "SA", "NV", "BV", "GMBH", "II", "III", "INC.", "CO.",
            "LTD.", "CORP.", "NA", "N.A.", "DBA"}
    words = []
    for i, w in enumerate(name.replace("*", "").split()):
        if w.upper() in keep and w.upper() not in ("INC.", "CO.", "LTD.", "CORP.", "DBA"):
            words.append(w.upper())
        elif i and w.lower() in small:
            words.append(w.lower())
        else:
            words.append(w[:1].upper() + w[1:].lower() if not re.search(r"\d", w) else w)
    return " ".join(words)


def product_name(name):
    """A product's name in ordinary capitals, keeping short codes ("ROUNDUP WEED & GRASS KILLER III" -> "Roundup
    Weed & Grass Killer III"; "HTH 3" CHLORINATING TABLETS" keeps its inch mark)."""
    out = []
    for w in name.split():
        core = re.sub(r"[^A-Za-z0-9]", "", w)
        letters = re.sub(r"[^A-Za-z]", "", w)
        if (re.fullmatch(r"[IVX]+|[A-Z]*\d[A-Z\d-]*", core) or (len(letters) <= 3 and letters.isupper()
                                                               and letters not in COMMON_WORDS)):
            out.append(w)
        else:
            out.append(w[:1].upper() + w[1:].lower())
    return " ".join(out)


# Short words of product names that are ordinary words, written in ordinary capitals ("ANT" -> "Ant"); other words of
# three letters or fewer are kept as printed ("WSP", "RTU", "EC", "DF").
COMMON_WORDS = {"OF", "IN", "ON", "TO", "AN", "OR", "AT", "BY", "A", "THE", "AND", "FOR", "ANT", "ANTS", "BUG", "OFF",
                "ALL", "PRO", "MAX", "ONE", "TWO", "OIL", "WET", "DRY", "HOT", "NEW", "FLY", "RAT", "GEL", "BAY", "TOP",
                "BIG", "RED", "SUN", "AIR", "NO", "GO", "UP", "OUT", "BEE", "TIC", "MIX", "PET", "DOG", "CAT", "ROW",
                "LOT", "SET", "KIT", "BAR", "CAN", "JET", "ICE", "SEA", "DEW", "LAB", "AID", "FOG", "GUN", "DUO", "PAK",
                "PAC", "TAB", "EZ", "WAY", "DAY", "LOW", "OLD", "OAK", "ELM", "MUD", "BIO", "ECO", "TEC", "TEK"}


def epa_entry(reg, name, restricted, company, types, sites, label, category, kind):
    """One index entry of an EPA-registered pesticide product (its newest label PDF, or the PPLS page when no label
    file is listed)."""
    number = epa_reg(reg)
    brand = company_name(company) if company else ""
    title = f"{product_name(name)} (EPA Reg. No. {number})"
    facts = [f"EPA Reg. No. {number}"]
    if types:
        facts.append("product type: " + ", ".join(t.lower() for t in types[:4]))
    if restricted:
        facts.append("a Restricted Use Pesticide: for sale to and use by certified applicators only")
    page = EPA_PRODUCT_PAGE.format(number)
    manual = {"title": f"Official label: {product_name(name)}", "url": label[1] if label else "", "page": page,
              "kind": "pdf" if label else "page", "size": 0, "document": "pesticide label",
              "label_date": f"{label[0][:4]}-{label[0][4:6]}-{label[0][6:]}" if label else "",
              "rights": EPA_RIGHTS, "source": "US EPA"}
    if not label:
        manual["url"] = page
    return {"id": f"epa-{number}", "brand": brand, "model": f"EPA Reg. No. {number}", "name": title,
            "type": kind, "category": category, "barcodes": [], "fcc_ids": [], "ic_ids": [], "source": EPA_SOURCE,
            "page": page, "facts": facts, "restricted_use": bool(restricted),
            "use_sites": sites[:12], "manuals": [manual]}


def epa_selected(spec, types, sites, name):
    """True when an EPA product belongs to a category: spec {"types": product type words (any), "sites": a
    regular expression on use-site names (any), "names": a regular expression on the product's name, "all": every
    product}; a product passes when every rule given matches (types and sites and names), or "all"."""
    if spec.get("all"):
        return True
    if spec.get("types") and not any(t in spec["types"] for t in types):
        return False
    if spec.get("sites") and not any(re.search(spec["sites"], s, re.I) for s in sites):
        return False
    if spec.get("names") and not re.search(spec["names"], name, re.I):
        return False
    return bool(spec.get("types") or spec.get("sites") or spec.get("names"))


def epa_kind(types):
    """The plain kind of an EPA product from its first known type: "weed killer", "insect killer" ..."""
    plain = [("HERBICIDE", "weed killer (herbicide)"), ("RODENTICIDE", "rodent poison (rodenticide)"),
             ("TERMITICIDE", "termite killer"), ("INSECTICIDE", "insect killer (insecticide)"),
             ("MITICIDE", "mite killer"), ("REPELLENT", "repellent"), ("ALGAECIDE", "algaecide"),
             ("ALGICIDE", "algaecide"), ("FUNGICIDE", "fungicide"), ("DISINFECTANT", "disinfectant"),
             ("SANITIZER", "sanitiser"), ("VIRUCIDE", "disinfectant"), ("ANTIFOUL", "antifouling product"),
             ("WATER PURIFIER", "water purifier"), ("MOLLUSCICIDE", "slug and snail killer"),
             ("PLANT GROWTH", "plant growth regulator"), ("ANTIMICROBIAL", "antimicrobial"),
             ("BACTERI", "antibacterial"), ("FUMIGANT", "fumigant")]
    for word, kind in plain:
        if any(word in t for t in types):
            return kind
    return "pesticide"


class EpaData:
    """The PPIS files and the label addresses, read once per build and shared by every category."""

    def __init__(self, fetch, say=print):
        self.fetch, self.say, self.loaded = fetch, say, False

    def load(self):
        """Read the six PPIS files and the sitemaps (about 10 MB of zips and 30 sitemaps)."""
        if self.loaded:
            return
        f = {k: zip_text(self.fetch.raw(PPIS + v, max_bytes=30_000_000)) for k, v in PPIS_FILES.items()}
        self.products = parse_epa_products(f["product"])
        self.types = parse_epa_pairs(f["type"], 2)
        self.sites = parse_epa_pairs(f["site"], 9)
        self.type_names = parse_epa_names(f["typename"], 2)
        self.site_names = parse_epa_names(f["sitename"], 9)
        self.companies = parse_epa_companies(f["company"])
        texts = []
        for n in range(EPA_SITEMAPS):
            try:
                texts.append(self.fetch.text(EPA_SITEMAP.format(n)))
            except RuntimeError:
                break
        self.labels = epa_label_urls(texts)
        self.loaded = True
        self.say(f"EPA: {len(self.products)} active products, {len(self.labels)} with a label file listed")

    def entries(self, spec, category, limit):
        """The entries of the products a category's spec selects (each with its newest label), up to limit (the
        products with a label file first, then by registration number)."""
        self.load()
        picked = []
        for reg, (name, restricted) in self.products.items():
            types = [self.type_names.get(c, "") for c in self.types.get(reg, [])]
            types = [t for t in dict.fromkeys(types) if t]
            sites = [self.site_names.get(c, "") for c in self.sites.get(reg, [])]
            sites = [s for s in dict.fromkeys(sites) if s]
            if not epa_selected(spec, types, sites, name):
                continue
            picked.append((reg not in self.labels, reg, name, restricted, types, sites))
        picked.sort()
        out = []
        for _, reg, name, restricted, types, sites in picked[:limit]:
            out.append(epa_entry(reg, name, restricted, self.companies.get(reg[:6], ""), types, sites,
                                 self.labels.get(reg), category, epa_kind(types)))
        return out


# ------------------------------------------------------------------------------------------------- Health Canada

def parse_pmra(text):
    """The CURRENT products of the Health Canada extract: [{reg, name, registrant, type, marketing, sites, site
    categories, active ingredients}]."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        if (r.get("Current / Historical") or "").strip() != "Current":
            continue
        reg = (r.get("Registration number") or "").strip()
        name = " ".join((r.get("Product name - English") or "").split())
        if not reg or not name:
            continue
        cats = [re.sub(r"^\d+-", "", c.strip()) for c in re.split(r",\s*(?=\d+-)", r.get("Use Site Category") or "")
                if c.strip()]
        out.append({"reg": reg, "name": name, "registrant": (r.get("Registrant name") or "").strip(),
                    "type": (r.get("Product Type") or "").strip(), "marketing": (r.get("Marketing type") or "").strip(),
                    "sites": (r.get("Sites of Use") or "").strip(), "site_categories": cats,
                    "actives": (r.get("Active ingredients - English") or "").strip()})
    return out


def pmra_selected(spec, p):
    """True when a Canadian product belongs to a category: spec {"types": a regular expression on its product
    type, "sites": on its use-site categories and sites, "names": on its name, "domestic": only products sold for
    home use (marketing class DOMESTIC), "all": every current product}; every rule given must match."""
    if spec.get("domestic") and p["marketing"] != "DOMESTIC":
        return False
    if spec.get("all"):
        return True
    if spec.get("types") and not re.search(spec["types"], p["type"], re.I):
        return False
    if spec.get("sites") and not re.search(spec["sites"], " ".join(p["site_categories"]) + " " + p["sites"], re.I):
        return False
    if spec.get("names") and not re.search(spec["names"], p["name"], re.I):
        return False
    return bool(spec.get("types") or spec.get("sites") or spec.get("names") or spec.get("domestic"))


def pmra_entry(p, category):
    """One index entry of a product registered in Canada (the registry's product page, which lists its labels)."""
    page = PMRA_PAGE.format(urllib.parse.quote(p["reg"]))
    name = product_name(p["name"])
    facts = [f"Canadian pest control product registration number {p['reg']} (PCP Act)"]
    if p["type"]:
        facts.append("product type: " + p["type"].lower())
    if p["marketing"] == "DOMESTIC":
        facts.append("sold for home use (domestic class)")
    elif p["marketing"]:
        facts.append("class: " + p["marketing"].lower())
    if p["actives"]:
        facts.append("active ingredients: " + p["actives"].lower()[:200])
    return {"id": f"pmra-{p['reg']}", "brand": company_name(p["registrant"]),
            "model": f"Reg. No. {p['reg']} PCP Act", "name": f"{name} (Reg. No. {p['reg']}, PCP Act)",
            "type": (p["type"].split(",")[0].strip().lower() or "pesticide"), "category": category,
            "barcodes": [], "fcc_ids": [], "ic_ids": [], "source": PMRA_SOURCE, "page": page, "facts": facts,
            "manuals": [{"title": f"Official labels: {name}", "url": page, "page": page, "kind": "page", "size": 0,
                         "document": "pesticide label", "rights": PMRA_RIGHTS, "source": "Health Canada"}]}


def pmra_entries(products, spec, category, limit):
    """The entries of the Canadian products a category's spec selects (home-use products first), up to limit."""
    picked = [p for p in products if pmra_selected(spec, p)]
    picked.sort(key=lambda p: (p["marketing"] != "DOMESTIC", p["name"]))
    return [pmra_entry(p, category) for p in picked[:limit]]


# ------------------------------------------------------------------------------------------------- NIOSH

NIOSH_ROW = re.compile(r"<td>\s*([0-9]{2,7}-[0-9]{2}-[0-9])\s*</td>\s*<td>\s*<a href=['\"](npgd\d{4}\.html)['\"]>"
                       r"([^<]+)</a>", re.I)


def parse_niosh(text):
    """[(CAS number, the Pocket Guide page's address, the chemical's name)] from the Pocket Guide's CAS index, each
    page once (a chemical with several CAS numbers keeps its first)."""
    out, seen = [], set()
    for cas, page, name in NIOSH_ROW.findall(text):
        if page in seen:
            continue
        seen.add(page)
        out.append((cas, NIOSH_BASE + page, " ".join(html.unescape(name).split())))
    return out


def niosh_entry(cas, page, name, category):
    """One index entry of a chemical: its NIOSH Pocket Guide page, and links to the same chemical in CAMEO
    Chemicals and PubChem (for the person to open; the builder reads neither)."""
    key = page.rsplit("/", 1)[-1].split(".")[0]
    return {"id": f"niosh-{key}", "brand": "", "model": f"CAS {cas}", "name": f"{name} (CAS {cas})",
            "type": "chemical", "category": category, "barcodes": [], "fcc_ids": [], "ic_ids": [],
            "source": NIOSH_SOURCE, "page": page, "cas": cas,
            "manuals": [{"title": f"NIOSH Pocket Guide: {name}", "url": page, "page": page, "kind": "page", "size": 0,
                         "document": "chemical hazard guide", "rights": "a US government work (public domain)",
                         "source": "NIOSH (CDC)"},
                        {"title": f"CAMEO Chemicals: {name}", "url": CAMEO_SEARCH.format(urllib.parse.quote(cas)),
                         "page": CAMEO_SEARCH.format(urllib.parse.quote(cas)), "kind": "page", "size": 0,
                         "document": "chemical datasheet", "rights": "NOAA, a US government work (public domain)",
                         "source": "NOAA"},
                        {"title": f"PubChem: {name}", "url": PUBCHEM_PAGE.format(cas), "page": PUBCHEM_PAGE.format(cas),
                         "kind": "page", "size": 0, "document": "chemical safety summary",
                         "rights": "the US National Library of Medicine; each source's data keeps its own terms",
                         "source": "PubChem"}]}


def niosh_entries(text, category, limit):
    """The entries of the Pocket Guide's chemicals, up to limit."""
    return [niosh_entry(cas, page, name, category) for cas, page, name in parse_niosh(text)[:limit]]
