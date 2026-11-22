"""Self-test of the collection "Home health tests (instructions for use)" (manuals/home_health_tests.py), with no
downloads.

It checks that the category is listed under its key, says the safety notice first, searches the Internet Archive
and the FDA's device identifiers with its own words, lists every maker the owner named as link-only (nothing read
from their sites) with its reason, and links the FDA's and CDC's guidance pages.

Run it from the repository's folder:   python3 -m pytest manuals/test_home_health_tests.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import home_health_tests as H  # noqa: E402


def test_category():
    cat = C.CATEGORIES["home_health_tests"]
    assert cat is H.CATEGORY and cat["notice"] == ("Follow the test's own instructions; faint lines can be hard to "
                                                   "read; contact a doctor or pharmacist about any result.")
    assert "pregnancy test" in cat["ia"] and '"SARS-CoV-2"' in cat["udi"]
    assert any("fda.gov" in g["url"] for g in cat["guidance"]) and any("cdc.gov" in g["url"] for g in cat["guidance"])


def test_makers_are_link_only():
    names = " ".join(m["maker"] for m in H.MAKERS)
    for brand in ("First Response", "Clearblue", "BinaxNOW", "iHealth", "Flowflex", "Lucira", "OraQuick",
                  "Accu-Chek", "OneTouch", "FreeStyle", "Contour", "Everlywell", "LetsGetChecked"):
        assert brand in names, brand
    for m in H.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "home_health_tests"
    keys = [m["key"] for m in H.MAKERS]
    assert len(keys) == len(set(keys))
