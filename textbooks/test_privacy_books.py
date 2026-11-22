"""Self-test of the privacy, security and digital safety books (privacy_books.py), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once with its own group and request words (at most 256 jobs each) and
reaches sources.py; that every web guide and PDF has a licence the toolkit may repackage, a description, a licence
page and line, and a notice that ends with the safety words (ReportFraud.ftc.gov, 7726, ic3.gov, the Elder Fraud
Hotline); that the share-alike books are share-alike and the Canadian one personal use only; that non-US books say
where they apply; that page patterns match their own addresses (and not other languages); that fixed-list guides are
read in the order listed; that the privacy law books reach sources.LAWS in this group; and that every row of
NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_privacy_books.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import privacy_books as P  # noqa: E402

BOOKS = list(P.COLLECTION.guides.values()) + list(P.COLLECTION.pdfs.values())


def test_registered():
    assert P in more_refs.modules() and more_refs.MODULES.count("privacy_books") == 1
    assert sources.GROUPS[P.GROUP] == "Reference, privacy, security and digital safety"
    keys = sources.expand_keys(["privacy"])
    assert keys == P.COLLECTION.expand_keys(["privacy"]) and len(keys) == len(set(keys)) <= 256
    own = {f"privacy:{n}" for n in list(P.COLLECTION.guides) + list(P.COLLECTION.pdfs)}
    assert set(keys) == own | {f"law:{n}" for n in P.LAW_NAMES}
    for word in ("privacy-scams", "privacy-ai"):
        part = sources.expand_keys([word])
        assert part and set(part) <= own and len(part) <= 256, word
    assert set(P.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in P.NOT_INCLUDED)


def test_safety_notice_says_what_the_owner_asked():
    for words in ("ReportFraud.ftc.gov", "7726", "ic3.gov", "1-833-372-8311"):
        assert words in P.SAFETY, words


def test_every_book():
    for g in BOOKS:
        assert g["group"] == P.GROUP, g["name"]
        whole = bool(g.get("unchanged"))
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, whole), (g["name"], short)
        assert g["notice"].endswith(P.SAFETY) and g["description"], g["name"]
        assert g["licence_page"] and g["licence_text"] and g["country"], g["name"]
        if g["name"] in P.COLLECTION.guides:
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
        else:
            assert g.get("pdf") or g.get("archive"), g["name"]
            assert g["version"], g["name"]


def test_licence_kinds():
    kind = {g["name"]: B.licence_kind(B.licence_short(g["licence"]) if g["licence"] not in sources.NO_CHANGES
                                      else g["licence"]) for g in BOOKS}
    for name in ("security_in_a_box", "privacy_guides", "owasp_cheat_sheets", "gnupg_manual"):
        assert kind[name] == "share-alike", name
    for name in ("eff_ssd_glossary_playlists", "tor_manual", "cisa_secure_our_world", "nist_csf_2",
                 "ncsc_individuals_families", "intl_ai_safety_interim_report"):
        assert kind[name] == "open", name
    canada = P.COLLECTION.guides["canada_get_cyber_safe"]
    assert canada["personal_use"] and "personal use only" in canada["notice"] and kind["canada_get_cyber_safe"]


def test_non_us_books_say_where_they_apply():
    for g in BOOKS:
        if g["country"] in ("United Kingdom", "Canada"):
            assert re.search(r"UK|Canad", g["notice"]), g["name"]
    for subject in ("Online safety (United Kingdom)", "Online safety (Canada)", "Data protection (UK)"):
        assert sources.practice_note("United Kingdom" if "Canada" not in subject else "Canada", subject), subject


def test_page_patterns():
    tor = re.compile(P.COLLECTION.guides["tor_manual"]["pages"])
    assert tor.match("https://tb-manual.torproject.org/tor-browser/getting-started/downloading/")
    assert not tor.match("https://tb-manual.torproject.org/ru/about/")
    siab = re.compile(P.COLLECTION.guides["security_in_a_box"]["pages"])
    assert siab.match("https://securityinabox.org/en/passwords/password-managers")
    assert not siab.match("https://securityinabox.org/en/blog/2025-09-detentions")
    pg = re.compile(P.COLLECTION.guides["privacy_guides"]["pages"])
    assert pg.match("https://www.privacyguides.org/en/basics/threat-modeling/")
    assert not pg.match("https://www.privacyguides.org/en/articles/2025/01/01/news/")
    eff = re.compile(P.COLLECTION.guides["eff_ssd_glossary_playlists"]["pages"])
    assert eff.match("https://ssd.eff.org/glossary/end-end-encryption") and \
        not eff.match("https://ssd.eff.org/module/creating-strong-passwords")      # already in the library


def test_pages_read_in_order(monkeypatch):
    """A fixed-list guide is read in the order listed, its first page first, and nothing else is fetched."""
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    cisa = P.COLLECTION.guides["cisa_secure_our_world"]
    found = [u for u, _unit in D.crawl(cisa, None)]
    assert found == P.CISA_PAGES
    assert [unit for _u, unit in D.crawl(cisa, None)][-1] == "For small businesses"
    owasp = P.COLLECTION.guides["owasp_cheat_sheets"]
    assert [u for u, _unit in D.crawl(owasp, None)] == owasp["urls"]


def test_laws():
    laws = {law["name"]: law for law in sources.LAWS if law["name"] in P.LAW_NAMES}
    assert set(laws) == set(P.LAW_NAMES)
    for law in laws.values():
        assert law["group"] == P.GROUP and law["description"], law["name"]
    assert laws["uk_gdpr"]["country"] == "United Kingdom" and laws["canada_pipeda"]["country"] == "Canada"
    assert laws["cfr_45_164_hipaa_privacy_security"]["cfr"]["part"] == 164


def test_not_included():
    for row in P.NOT_INCLUDED:
        assert "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in P.NOT_INCLUDED)
    for words in ("FTC", "FCC", "HIPAA", "CFPB", "ENISA", "EU AI Act", "OECD", "International AI Safety Report",
                  "AI Security Institute", "Apple", "Meta"):
        assert words in names, words
