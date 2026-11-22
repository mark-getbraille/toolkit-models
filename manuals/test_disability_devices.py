"""Self-test of the manual collections for disabilities other than blindness (manuals/disability_devices.py):
hearing_communication_devices and wheelchairs_mobility_vehicles, with MADE-UP data only: nothing is downloaded.

It checks that both collections are listed in categories.py with their name, description, index licence and notice
(professionals fit the devices; button batteries; weight limits; qualified installers); that their Internet Archive
words are their own (no word another collection already searches, such as "hearing aid" or "wheelchair"); that every
maker is link-only with its reason and an https home page, and no maker key is used twice in its collection; that the
US government guides are "full" only where the site lets programs read them (the FCC and NHTSA are links); and that
the hand-entered pages become index entries without any download.

Run it from the repository's folder:   python3 -m pytest manuals/test_disability_devices.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import disability_devices as DD  # noqa: E402

KEYS = ("hearing_communication_devices", "wheelchairs_mobility_vehicles")


def test_listed_with_notice():
    for key in KEYS:
        cat = C.CATEGORIES[key]
        assert cat is DD.CATEGORIES[key] and cat["kind"] == "manuals", key
        assert cat["name"] and cat["description"] and cat["licence"].startswith("CC0"), key
    assert "audiologist" in DD.HEARING_NOTICE and "button batteries" in DD.HEARING_NOTICE
    assert "1-800-222-1222" in DD.HEARING_NOTICE
    assert "weight limit" in DD.MOBILITY_NOTICE and "qualified mobility equipment dealer" in DD.MOBILITY_NOTICE


def test_internet_archive_words_are_new():
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k not in KEYS for w in c.get("ia") or []}
    for key in KEYS:
        words = [w.lower() for w in C.CATEGORIES[key]["ia"]]
        assert len(words) == len(set(words)), key
        assert not set(words) & taken, (key, set(words) & taken)
    assert "hearing aid" in taken and "wheelchair" in taken      # the other collections search those


def test_makers_link_only():
    for key, makers in (("hearing_communication_devices", DD.HEARING_MAKERS),
                        ("wheelchairs_mobility_vehicles", DD.MOBILITY_MAKERS)):
        keys = [m["key"] for m in makers]
        assert len(keys) == len(set(keys)), key
        for m in makers:
            assert m["access"] == "link" and m["reason"] and m["category"] == key, m["key"]
            assert m["library"].startswith("https://") and m["library"].count("/") == 3, m["key"]
    names = " ".join(m["maker"] for m in DD.HEARING_MAKERS + DD.MOBILITY_MAKERS)
    for brand in ("Phonak", "Cochlear", "Tobii Dynavox", "CapTel", "Permobil", "BraunAbility"):
        assert brand in names, brand


def test_government_guides():
    docs = {d["key"]: d for d in DD.HEARING_DOCUMENTS + DD.MOBILITY_DOCUMENTS}
    for key in ("fda-hearing-aids", "fda-cochlear-implants", "nidcd-assistive-devices", "va-prosthetics"):
        assert docs[key]["access"] == "full" and "public domain" in docs[key]["rights"], key
    for key in ("fcc-relay-services", "fcc-hearing-aid-compatibility", "nhtsa-adapted-vehicles"):
        assert docs[key]["access"] == "link" and "403" in docs[key]["reason"], key
    for d in docs.values():
        assert d["url"].startswith("https://") and d["title"] and d["by"] and d["document"], d["key"]
    entries, notes = B.document_entries(None, DD.HEARING_DOCUMENTS, "hearing_communication_devices")
    assert not notes and len(entries) == len(DD.HEARING_DOCUMENTS)
    assert all(e["id"].startswith("doc-hearing_communication_devices-") for e in entries)
    linked = [e for e in entries if e["access"] == "link"]
    assert linked and all(e["manuals"][0].get("link_only") for e in linked)
