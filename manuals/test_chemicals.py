"""Self-test of the household and garage chemical collections (manuals/chemicals.py, manuals/chemical_labels.py and
their use by build_manuals.py), with MADE-UP files and pages only: nothing is downloaded from the internet.

It checks that:
  - the EPA's fixed-column bulk files are read right: only ACTIVE products, the registration number as a label prints
    it ("3-1"), the restricted-use flag, the product types and use sites, the registrant, and the NEWEST label PDF of
    each product from the sitemaps;
  - a category's spec picks the right products (pool sanitisers for the pool category, household disinfectants for
    cleaners, every product for pesticide_labels), with label files first;
  - Health Canada's extract keeps current products only, home-use (DOMESTIC) products first, and links the
    registry's product page;
  - the NIOSH Pocket Guide index gives each chemical once, with its CAS number and links to CAMEO and PubChem;
  - every chemical category is listed with its makers, every maker is a "link" maker with a reason, a unique key and
    an https address, and the builder never fetches a link maker's site;
  - build() writes an index holding the EPA, Health Canada and NIOSH entries, the guidance and the credit lines, and a
    source that fails leaves a note while the others go on.

Run it from the repository's folder:   python3 -m pytest manuals/test_chemicals.py
"""

import gzip
import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import chemical_labels as L  # noqa: E402
import chemicals as CH  # noqa: E402


def product_line(reg, name, cancelled=False, rup="F"):
    """A made-up PRODUCT.TXT line: REG_NR 1-11, FORM 12-13, TOX 14, APPR_DATE 15-22, CAN_DATE 23-30, CT_CODE 31-32,
    PROD_NAME 33-102, RUP_FLAG 103."""
    can, ct = ("20200101", "C ") if cancelled else ("00000000", "  ")
    return f"{reg}163" + "19900101" + can + ct + f"{name:<70}" + rup + "  N"


PRODUCTS = "\n".join([
    product_line("00000300001", "EXAMPLE POOL SHOCK 73%"),
    product_line("00000300002", "EXAMPLE OLD CLEANER", cancelled=True),
    product_line("00001200007", "EXAMPLE DISINFECTANT RTU"),
    product_line("00001200008", "EXAMPLE FARM FLY KILLER", rup="T"),
])
TYPES = "00000300001" + "20\n00000300001" + "59\n00001200007" + "20\n00001200008" + "43\n"
TYPENAMES = "20DISINFECTANT\n43INSECTICIDE\n59ALGAECIDE\n"
SITES = "00000300001650116101\n00001200007630000009\n00001200008520030000\n"
SITENAMES = "650116101SWIMMING POOL WATER\n630000009HOUSEHOLD (UNSPECIFIED)\n520030000CATTLE (ALL OR UNSPECIFIED)\n"
COMPANIES = "000003" + f"{'EXAMPLE POOL COMPANY LLC':<60}" + "\n000012" + f"{'THE EXAMPLE CHEMICAL CO.':<60}" + "\n"
SITEMAP = """<urlset><url><loc>https://www3.epa.gov/pesticides/chem_search/ppls/000003-00001-20100101.pdf</loc></url>
<url><loc>https://www3.epa.gov/pesticides/chem_search/ppls/000003-00001-20240315.pdf</loc></url>
<url><loc>https://www3.epa.gov/pesticides/chem_search/ppls/000012-00007-20190707.pdf</loc></url>
<url><loc>https://www3.epa.gov/pesticides/chem_search/help/index-ppls.html</loc></url></urlset>"""
PMRA_CSV = ('Registration number,Product name - English,Product name - French,Registration Status,Expiry date,'
            'Marketing type,Date first registered,Exclusive period start date,Active ingredients - English,'
            'Active ingredients - French,Product Type,Registrant name,Use Site Category,Sites of Use,Pests,'
            'Current / Historical,Active ingredient concentration,CAS number\n'
            '30001,EXAMPLE POOL CHLORINE,,Full Registration,2030-12-31,COMMERCIAL,2000-01-01,2000-01-01,'
            'TRICHLOROISOCYANURIC ACID,,SWIMMING POOL BACTERICIDE,EXAMPLE POOLS INC.*,29-SWIMMING POOLS,'
            'SWIMMING POOL WATER,,Current,90 %,87-90-1\n'
            '30002,EXAMPLE HOME POOL TABS,,Full Registration,2030-12-31,DOMESTIC,2000-01-01,2000-01-01,'
            'TRICHLOROISOCYANURIC ACID,,SWIMMING POOL BACTERICIDE,EXAMPLE POOLS INC.*,29-SWIMMING POOLS,'
            'SWIMMING POOL WATER,,Current,90 %,87-90-1\n'
            '1596,"""OLD"" INSECT POWDER",,,,NOT AVAILABLE,1945-07-01,1927-07-01,N/A,N/A,INSECTICIDE,,,,,Historical,'
            '%,N/A\n')
NIOSH_HTML = ("<table><tr><td>67-64-1</td><td><a href='npgd0004.html'>Acetone</a></td></tr>"
              "<tr><td>7681-52-9</td><td><a href='npgd0560.html'>Sodium hypochlorite</a></td></tr>"
              "<tr><td>107-21-1</td><td><a href='npgd0272.html'>Ethylene glycol</a></td></tr>"
              "<tr><td>9999-99-9</td><td><a href='npgd0004.html'>Acetone (another number)</a></td></tr></table>")


def zipped(text):
    """A one-file zip of text, as the EPA publishes each PPIS file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("file.txt", text)
    return buf.getvalue()


class FakeFetch:
    """Answers from made-up files; records every address asked."""

    def __init__(self, broken=()):
        self.asked, self.requests, self.broken = [], 0, set(broken)
        files = {"product.zip": PRODUCTS, "prodtype.zip": TYPES, "company.zip": COMPANIES, "prodsite.zip": SITES,
                 "typename.zip": TYPENAMES, "sitename.zip": SITENAMES}
        self.files = {L.PPIS + k: zipped(v) for k, v in files.items()}
        self.pages = {L.EPA_SITEMAP.format(0): SITEMAP, L.PMRA_CSV: PMRA_CSV, L.NIOSH_INDEX: NIOSH_HTML}

    def raw(self, url, headers=None, cache=True, max_bytes=0):
        self.asked.append(url)
        if url in self.broken or url not in self.files:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.files[url]

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        if url in self.broken or url not in self.pages:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.pages[url]

    def size(self, url):
        self.asked.append(url)
        return 0

    def json(self, url, headers=None, cache=True):
        # The Internet Archive (chemical_safety also lists the Lanco safety data sheets collection): not answered.
        self.asked.append(url)
        raise RuntimeError(f"{url}: HTTP 404")


def test_epa_files_are_read_right():
    """Active products only; the label's own number; the newest label; restricted use; registrant names."""
    products = L.parse_epa_products(PRODUCTS)
    assert set(products) == {"00000300001", "00001200007", "00001200008"}
    assert products["00001200008"] == ("EXAMPLE FARM FLY KILLER", True)
    assert L.epa_reg("00000300001") == "3-1" and L.epa_reg("00001200007") == "12-7"
    labels = L.epa_label_urls([SITEMAP])
    assert labels["00000300001"] == ("20240315", "https://www3.epa.gov/pesticides/chem_search/ppls/"
                                                 "000003-00001-20240315.pdf")
    assert L.parse_epa_companies(COMPANIES)["000012"] == "THE EXAMPLE CHEMICAL CO."
    assert L.company_name("THE EXAMPLE CHEMICAL CO.") == "The Example Chemical Co."
    assert L.company_name("EXAMPLE POOL COMPANY LLC") == "Example Pool Company LLC"
    assert L.product_name("EXAMPLE DISINFECTANT RTU") == "Example Disinfectant RTU"
    assert L.product_name("TERRO ANT KILLER II") == "Terro Ant Killer II"


def test_epa_categories_pick_their_products():
    """The pool spec takes the pool sanitiser, the household spec the disinfectant, pesticide_labels everything; a
    product with a label file comes first and links its newest PDF; one without links the EPA's product page."""
    data = L.EpaData(FakeFetch(), say=lambda *_: None)
    pool = data.entries(CH.CHEMICAL_CATEGORIES["pool_spa_chemicals"]["epa"], "pool_spa_chemicals", 50)
    assert [e["model"] for e in pool] == ["EPA Reg. No. 3-1"]
    e = pool[0]
    assert e["brand"] == "Example Pool Company LLC" and e["name"] == "Example Pool Shock 73% (EPA Reg. No. 3-1)"
    assert e["manuals"][0]["url"].endswith("000003-00001-20240315.pdf") and e["manuals"][0]["kind"] == "pdf"
    assert e["manuals"][0]["document"] == "pesticide label" and e["category"] == "pool_spa_chemicals"
    assert e["type"] == "algaecide" or e["type"] == "disinfectant"
    home = data.entries(CH.CHEMICAL_CATEGORIES["household_cleaners"]["epa"], "household_cleaners", 50)
    assert [x["model"] for x in home] == ["EPA Reg. No. 12-7"]
    every = data.entries(CH.CHEMICAL_CATEGORIES["pesticide_labels"]["epa"], "pesticide_labels", 50)
    assert [x["model"] for x in every] == ["EPA Reg. No. 3-1", "EPA Reg. No. 12-7", "EPA Reg. No. 12-8"]
    farm = every[2]
    assert farm["restricted_use"] and any("Restricted Use" in f for f in farm["facts"])
    assert farm["manuals"][0]["kind"] == "page" and "P102_REG_NUM:12-8" in farm["manuals"][0]["url"]
    assert data.entries({"sites": r"CATTLE"}, "farm_chemicals", 1)[0]["model"] == "EPA Reg. No. 12-8"
    assert not L.epa_selected({}, ["INSECTICIDE"], [], "X")          # an empty spec takes nothing


def test_health_canada():
    """Current products only, home-use first, the registry's page as the link."""
    products = L.parse_pmra(PMRA_CSV)
    assert [p["reg"] for p in products] == ["30001", "30002"]
    assert products[0]["site_categories"] == ["SWIMMING POOLS"]
    got = L.pmra_entries(products, CH.CHEMICAL_CATEGORIES["pool_spa_chemicals"]["pmra"], "pool_spa_chemicals", 10)
    assert [e["id"] for e in got] == ["pmra-30002", "pmra-30001"]
    assert got[0]["manuals"][0]["url"] == L.PMRA_PAGE.format("30002")
    assert "sold for home use (domestic class)" in got[0]["facts"]
    assert got[0]["brand"] == "Example Pools Inc." and got[0]["name"].startswith("Example Home Pool Tabs")
    assert L.pmra_entries(products, {"domestic": True}, "x", 10)[0]["id"] == "pmra-30002"


def test_niosh():
    """Each Pocket Guide page once, with CAMEO and PubChem links (never read)."""
    got = L.niosh_entries(NIOSH_HTML, "chemical_safety", 10)
    assert [e["name"] for e in got] == ["Acetone (CAS 67-64-1)", "Sodium hypochlorite (CAS 7681-52-9)",
                                        "Ethylene glycol (CAS 107-21-1)"]
    links = [m["url"] for m in got[0]["manuals"]]
    assert links == ["https://www.cdc.gov/niosh/npg/npgd0004.html",
                     "https://cameochemicals.noaa.gov/search/simple?st=chemicals&na=67-64-1",
                     "https://pubchem.ncbi.nlm.nih.gov/compound/67-64-1"]


def test_every_category_and_maker_is_sound():
    """Every chemical category is in CATEGORIES; every maker is linked only, with a reason, a unique key, an https
    address and its category; the owner's categories are all there."""
    wanted = {"household_cleaners", "pool_spa_chemicals", "lawn_garden_chemicals", "paints_coatings",
              "lubricants_oils", "wood_finishes", "automotive_fluids", "adhesives_sealants", "solvents_thinners",
              "pest_control", "batteries", "fuels_propane", "fire_extinguishers", "personal_care", "baby_care",
              "water_treatment", "aquarium_chemicals", "photo_chemicals", "art_craft_supplies", "concrete_masonry",
              "roofing_insulation", "welding_gases", "marine_products", "farm_chemicals", "pesticide_labels",
              "chemical_safety"}
    assert wanted == set(CH.CHEMICAL_CATEGORIES) and wanted <= set(C.CATEGORIES)
    keys = [m["key"] for m in CH.MAKERS]
    assert len(keys) == len(set(keys)) and len(keys) >= 150
    for m in CH.MAKERS:
        assert m["access"] == "link" and m["reason"].startswith("linked only") and m["library"].startswith("https://")
        assert m["category"] in CH.CHEMICAL_CATEGORIES and m["prefix"] == "ch"
    for key, cat in CH.CHEMICAL_CATEGORIES.items():
        assert cat["kind"] == "manuals" and cat["guidance"], key
        assert cat.get("makers") or key in ("pesticide_labels", "chemical_safety"), key
        assert all(g["url"].startswith("https://") for g in cat["guidance"])
    assert {"clorox", "pg", "sc-johnson", "scotts", "sherwin-williams", "wd-40", "prestone", "3m"} <= set(keys)


def test_link_makers_are_never_fetched():
    """The builder lists a link maker's address and reads nothing of it."""
    fetch = FakeFetch()
    entries, notes = B.maker_entries(fetch, CH.CHEMICAL_CATEGORIES["household_cleaners"]["makers"],
                                     CH.CHEMICAL_EXCLUDE, sizes=False)
    assert fetch.asked == [] and notes == []
    assert all(e["manuals"][0]["kind"] == "library" and e["category"] == "household_cleaners" for e in entries)
    assert entries[0]["id"].startswith("ch-") and "safety data sheets" in entries[0]["name"]


def test_build_writes_the_sources_and_a_failure_leaves_a_note(tmp_path, monkeypatch):
    """build() of a category with EPA, Health Canada and makers writes them all; a broken NIOSH index leaves a note."""
    monkeypatch.setattr(B, "_EPA", {})
    monkeypatch.setattr(B, "_PMRA", {})
    fetch = FakeFetch(broken={L.NIOSH_INDEX})
    B.build("pool_spa_chemicals", str(tmp_path), 50, fetch)
    name = json.load(open(tmp_path / "manifest-pool_spa_chemicals.json"))["file"]
    index = json.loads(gzip.decompress((tmp_path / name).read_bytes()))
    ids = [e["id"] for e in index["entries"]]
    assert "epa-3-1" in ids and "pmra-30002" in ids and any(i.startswith("ch-hth") for i in ids)
    assert "US EPA" in index["credit"] and "Open Government Licence - Canada" in index["credit"]
    assert any(g["url"] == "https://poisonhelp.hrsa.gov/" for g in index["guidance"])
    B.build("chemical_safety", str(tmp_path), 50, fetch)
    name = json.load(open(tmp_path / "manifest-chemical_safety.json"))["file"]
    index = json.loads(gzip.decompress((tmp_path / name).read_bytes()))
    assert any("NIOSH Pocket Guide failed" in n for n in index["notes"]) and index["entries"] == []
