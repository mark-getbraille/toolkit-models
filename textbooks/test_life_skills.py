"""Self-test of the life-skills reference modules (car_care.py, gardening.py, first_aid.py, home_health.py,
dental_care.py, eye_care.py, eyecare_products.py, midwifery.py, instrument_care.py), with MADE-UP data only: nothing
is downloaded.

It checks that each module is registered under its request word with its group, that every request stays at 256 jobs
or fewer, that every web guide and PDF has a licence the toolkit may repackage, a notice, a description, a licence
page and line and a working page pattern; that every home health book's notice carries its emergency note (911) and
says it is not a diagnosis or not medical training; that the NHS books are marked as UK sources with the practice
note; that the old books are checked to be from before 1931 and say they are out of date; that every NOT_INCLUDED row
says where to find the source; and that the eye care products book quotes only a label given in the eye, names the
library book of its whole label, and lists device records from made-up openFDA answers.

Run it from the repository's folder:   python3 -m pytest textbooks/test_life_skills.py
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

WORDS = {"car_care": "car-care", "gardening": "gardening", "first_aid": "first-aid", "home_health": "home-health",
         "dental_care": "dental-care", "eye_care": "eye-care", "eyecare_products": "eyecare-products",
         "midwifery": "midwifery", "instrument_care": "instrument-care"}
HEALTH = ("first_aid", "home_health", "dental_care", "eye_care", "eyecare_products", "midwifery")


def modules():
    """The life-skills modules that exist."""
    return [m for m in more_refs.modules() if m.__name__ in WORDS]


def test_all_registered():
    assert {m.__name__ for m in modules()} == set(WORDS)
    assert sources.GROUPS["homehealth"] == "Reference, home health care and first aid"
    assert sources.GROUPS["carcare"] and sources.GROUPS["garden"] and sources.GROUPS["instruments"]
    total = sum(len(sources.expand_keys([w])) for w in WORDS.values())
    assert total <= 256


@pytest.mark.parametrize("m", modules(), ids=lambda m: m.__name__)
def test_books(m):
    c = m.COLLECTION
    word = WORDS[m.__name__]
    keys = sources.expand_keys([word])
    assert keys == c.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"{c.prefix}:{n}" for n in list(c.guides) + list(c.pdfs) + list(c.makers)}
    for g in list(c.guides.values()) + list(c.pdfs.values()):
        whole = bool(g.get("unchanged"))
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, whole), g["name"]
        assert g["notice"] and g["description"] and g["group"] == c.group, g["name"]
        if not g.get("old_public_domain"):
            assert g["licence_page"] and g["licence_text"], g["name"]
        else:
            assert g["archive"] and int(g["published"]) < 1931 and "out of date" in g["notice"], g["name"]
        if g["name"] in c.guides:
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url if isinstance(url, str) else url[0]), (g["name"], url)
            for start, _depth in g.get("crawl") or []:
                assert start.startswith("https://"), g["name"]
        if m.__name__ in HEALTH:
            assert "911" in g["notice"], g["name"]
            assert re.search(r"not (medical training|medical advice|a diagnosis)|or a diagnosis", g["notice"]), \
                g["name"]
        if g.get("country", "United States") == "United Kingdom":
            assert "A UK source" in g["notice"] and g["licence"] == "OGL-UK-3.0", g["name"]
            assert "999" in sources.practice_note("United Kingdom", g["subject"], g["title"]), g["name"]
    assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in m.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_cdc_books_whole_with_conditions():
    import first_aid as F
    import parenting as P
    cdc = [g for m in modules() for g in m.COLLECTION.guides.values() if g["publisher"] == P.CDC_PUBLISHER]
    assert len(cdc) >= 10
    for g in cdc:
        assert g["unchanged"] and g["licence_page"] == P.CDC_TERMS and "Source: CDC" in g["notice"], g["name"]
        pattern = re.compile(g["pages"])
        site = g["crawl"][0][0].rsplit("/", 1)[0]
        assert pattern.match(site + "/index.html") and not pattern.match(site + "/es/index.html")
    assert "1-800-222-1222" in F.EMERGENCY


def test_nhs_page_patterns():
    import first_aid as F
    g = F.nhs_book("homehealth", "x", "T", "First aid (UK)", ["conditions/frostbite", "symptoms/cough"], "d")
    assert re.match(g["pages"], "https://www.nhs.uk/conditions/frostbite/")
    assert not re.match(g["pages"], "https://www.nhs.uk/conditions/frostbite-other/")
    assert g["urls"] == ["https://www.nhs.uk/conditions/frostbite/", "https://www.nhs.uk/symptoms/cough/"]


def test_midwifery_notes_and_no_repeats():
    import midwifery as W
    assert "1-833-852-6262" in W.NOTE and "988" in W.NOTE
    built = {g["name"] for m in modules() for g in m.COLLECTION.guides.values()}
    assert not built & {"nhs_pregnancy_baby", "cdc_pregnancy", "safe_to_sleep"}
    for row in W.NOT_INCLUDED[:2]:
        assert "Link-only" in row[1]


class FakeLabel:
    """A made-up medications.Label with only the fields eyecare_products reads."""

    def __init__(self, route, doc_code="34390-5", generic="TETRAHYDROZOLINE HYDROCHLORIDE"):
        self.products = [{"name": "Made-up Drops", "generic": generic, "form": "SOLUTION/ DROPS", "route": route,
                          "actives": [("TETRAHYDROZOLINE", "0.5 mg in 1 mL")], "inactives": []}]
        self.doc_code, self.setid, self.version, self.date, self.company = doc_code, "abc", "3", "2026-01-02", "Co"
        self.sections, self.highlights = [], []


def test_eye_label_only_given_in_the_eye(monkeypatch):
    import eyecare_products as P
    import medications as M
    monkeypatch.setattr(P, "search_labels", lambda name, cache=None: [("s1", 1, "NASAL SPRAY"), ("s2", 1, "EYE")])
    monkeypatch.setattr(M, "spl_xml", lambda setid, version, cache=None: setid)
    monkeypatch.setattr(M, "read_label", lambda xml: FakeLabel("NASAL" if xml == "s1" else "OPHTHALMIC"))
    label = P.eye_label("tetrahydrozoline")
    assert label.products[0]["route"] == "OPHTHALMIC"
    book, page = P.library_book("tetrahydrozoline", label)
    assert book == "med:otc:t-z" and page.lower().startswith("tetrahydrozoline")
    html = P.label_parts_html(label)
    assert html.count(M.NONE_SAID) == 4 and "the label's own words" in html
    monkeypatch.setattr(M, "read_label", lambda xml: FakeLabel("NASAL"))
    assert P.eye_label("tetrahydrozoline") is None
    assert all(len(g) == 3 and g[2] for g in P.EYE_GROUPS)
    assert "eye doctor" in P.NOTICE and "911" in P.NOTICE


def test_eye_care_devices_book(monkeypatch):
    import eyecare_products as P
    import fda_recalls
    import home_tests as H
    monkeypatch.setattr(fda_recalls, "licence_still_open", lambda probe: True)
    monkeypatch.setattr(H, "api", lambda path, params: {})
    monkeypatch.setattr(H, "decisions", lambda code: [("510(k)", "K000001", "Made-up Lens Case", "Co", "2020-01-01",
                                                       "SESE")])

    def fake_paged(path, search, limit=None):
        if path == "device/classification":
            return [{"product_code": "LRX", "device_name": "Case, Contact Lens", "device_class": "2",
                     "regulation_number": "886.5928", "definition": "A case for lenses."},
                    {"product_code": "NYK", "device_name": "Ophthalmodynamometer, Diagnostic Contact Lens"}], {}
        return [{"brand_name": "MadeUpCase", "version_or_model_number": "M1", "device_description": "Lens case",
                 "company_name": "Made-up Vision", "identifiers": [{"id": "00012345678905"}], "is_otc": "true"}], \
            {"last_updated": "2026-11-01"}
    monkeypatch.setattr(H, "paged", fake_paged)
    book = P.eye_care_devices_book("eye_care_devices", "/tmp/none")
    assert [p.title for p in book.pages] == ["Case, Contact Lens (product code LRX)"]     # diagnostic left out
    assert "00012345678905" in book.pages[0].body and "K000001" in book.pages[0].body
    assert book.published == "2026-11-01" and "tap water" in book.notice
