"""Self-test of the collection "Password managers, security keys, routers, VPNs and home cameras (manuals)"
(manuals/privacy_manuals.py), with no downloads.

It checks that the category is listed under its own key and heading, says the safety notice first (download from the
maker, spare key, default passwords, how to report scams with the Elder Fraud Hotline), searches the Internet Archive
with its own words (none that another collection already searches), lists every maker as link-only (nothing read from
their sites) with its reason, marks only openly licensed guides "full", and links the guidance pages.

Run it from the repository's folder:   python3 -m pytest manuals/test_privacy_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import privacy_manuals as P  # noqa: E402


def test_category():
    cat = C.CATEGORIES["privacy_security"]
    assert cat is P.CATEGORY and cat["kind"] == "manuals" and cat["name"].endswith("(manuals)")
    for words in ("maker's own site", "spare security key", "default password", "ReportFraud.ftc.gov",
                  "1-833-372-8311"):
        assert words in cat["notice"], words
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "privacy_security" for w in c.get("ia") or []}
    assert not set(cat["ia"]) & taken and len(cat["ia"]) == len(set(cat["ia"]))
    urls = " ".join(g["url"] for g in cat["guidance"])
    for host in ("cisa.gov", "nist.gov", "ncsc.gov.uk", "reportfraud.ftc.gov", "ic3.gov"):
        assert host in urls, host


def test_makers_are_link_only():
    names = " ".join(m["maker"] for m in P.MAKERS)
    for brand in ("Bitwarden", "1Password", "Yubico", "Mullvad", "eero", "Ring"):
        assert brand in names, brand
    for m in P.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "privacy_security"
    keys = [m["key"] for m in P.MAKERS]
    assert len(keys) == len(set(keys))


def test_only_open_documents_are_full():
    for doc in P.DOCUMENTS:
        assert doc["access"] == "full" and "GPL" in doc["rights"] and doc["reason"], doc["key"]
        assert doc["url"].startswith("https://keepassxc.org/docs/")
