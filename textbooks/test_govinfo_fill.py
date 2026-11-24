"""Self-test of the official copies for the thin reference sections (textbooks/govinfo_fill.py, keys gpo:), with
MADE-UP data only: nothing is downloaded.

It checks that:
  - the module is registered once in more_refs.MODULES, its request words (govinfo-fill and one per section) reach
    sources.expand_keys, each stays at 256 jobs or fewer, and together they cover every key exactly once;
  - every book sits in its section's existing group (the car care, driving, motorcycles, pools, recycling,
    emergency, mental health, aging, veterans, genealogy and relationships modules' own), and its notice ends with
    that section's safety or help note;
  - every book has a licence the toolkit may repackage, a description, a notice that says whose work it is and where
    the copy comes from, and the licence page and line checked at build time; GovInfo books read GovInfo's own PDF
    address; EPA books are personal use under the EPA's terms; military manuals are judged by the release rule with
    the explosives parts left out; no book repeats a PDF or Internet Archive item already in the library;
  - the licence lines and left-out rows reach sources.py, each row with an address;
  - the sign-up books: without the owner's key nothing is fetched and the build says where to sign up; with a key
    the key goes only in a request header (never in an address or a page), made-up search results become pages
    with links, and a refused key is said plainly.

Run it from the repository's folder:   python3 -m pytest textbooks/test_govinfo_fill.py
"""

import io
import json
import os
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import thin_topics  # noqa: E402
import govinfo_fill as G  # noqa: E402
import aging_end_of_life  # noqa: E402
import car_care  # noqa: E402
import disaster_ready  # noqa: E402
import driving  # noqa: E402
import genealogy  # noqa: E402
import mental_health  # noqa: E402
import motorcycles_rvs  # noqa: E402
import pools_spas  # noqa: E402
import recycling  # noqa: E402
import relationships  # noqa: E402
import veterans  # noqa: E402

# section: the existing module whose group its books join
OWNERS = {"car": car_care, "drive": driving, "motor": motorcycles_rvs, "pools": pools_spas, "recycle": recycling,
          "ready": disaster_ready, "mind": mental_health, "aging": aging_end_of_life, "veterans": veterans,
          "gen": genealogy, "relate": relationships}


def test_registered_once_with_words_under_256():
    assert more_refs.MODULES.count("govinfo_fill") == 1 and G in more_refs.modules()
    every = G.COLLECTION.expand_keys(["govinfo-fill"])
    assert sources.expand_keys(["govinfo-fill"]) == every
    assert len(every) == len(set(every)) <= 256
    assert set(every) == set(G.COLLECTION.own_keys())
    seen = []
    for word in G.WORDS:
        keys = sources.expand_keys([word])
        assert keys == G.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
        assert all(k.startswith("gpo:") for k in keys), word
        if word != "govinfo-fill":
            seen += keys
    assert sorted(seen) == sorted(every)                 # the section words share the keys out exactly once
    assert G.COLLECTION.expand_keys(["gpo:new"]) == [f"gpo:new:{a}" for a in G.NEW_AREAS]
    for word in ("gpo-car", "gpo-motor", "gpo-pools", "gpo-recycling", "gpo-ready", "gpo-mind", "gpo-aging",
                 "gpo-veterans", "gpo-genealogy", "gpo-relate"):
        assert word in G.WORDS and G.WORDS[word](), word


def test_books_join_the_existing_groups_with_their_notes():
    assert set(G.BOOKS) == set(OWNERS) == set(G.AREAS)
    for area, books in G.BOOKS.items():
        assert books, area
        group = OWNERS[area].COLLECTION.group
        assert G.group_of(area) == group and group in sources.GROUPS, area
        for b in books:
            assert b["group"] == group and b["area"] == area, b["name"]
            assert b["notice"].rstrip().endswith(" ".join(G.note_of(area).split())), b["name"]
    assert G.GROUPS == {}                                # no new group: every book sits beside its section's own


def test_every_book_is_truthfully_licensed_and_described():
    names = [b["name"] for b in G.PDFS]
    assert len(names) == len(set(names))
    for b in G.PDFS:
        short = b["licence"] if b["licence"] in sources.NO_CHANGES else B.licence_short(b["licence"])
        assert B.licence_kind(short, False), (b["name"], b["licence"])
        assert b["description"] and b["notice"] and b["title"] and b["publisher"], b["name"]
        assert b["licence_page"] and b["licence_text"], b["name"]
        assert b.get("pdf") or b.get("archive"), b["name"]
        if b.get("pdf", "").startswith(G.GOVINFO):
            package = b["pdf"].rsplit("/", 1)[1][:-4]
            assert b["pdf"] == f"{G.GOVINFO}/content/pkg/{package}/pdf/{package}.pdf", b["name"]
            assert package in b["notice"] and "GovInfo" in b["notice"], b["name"]
        if b.get("personal_use"):                         # the EPA's terms, as recycling.py keeps them
            assert b["licence"] == recycling.X.EPA_TERMS and "Personal use only" in b["notice"], b["name"]
            assert b["area"] == "recycle", b["name"]
        else:
            assert b["licence"] == sources.US_GOV, b["name"]
            if not b.get("distribution_a"):
                assert "public domain" in b["notice"].lower(), b["name"]
        if b.get("distribution_a"):                       # a military manual: the release rule and the cut
            assert b.get("archive") and b["work"].startswith("a work of the US armed forces"), b["name"]
            assert "Internet Archive" in b["notice"], b["name"]
    assert any(b.get("distribution_a") for b in G.CAR) and any(b.get("distribution_a") for b in G.MOTOR)


def test_nothing_already_in_the_library_is_repeated():
    have = set()
    for m in more_refs.modules():
        if m is G:
            continue
        for e in m.COLLECTION.pdfs.values():
            have |= {e.get("pdf") or "", e.get("archive") or ""}
    for e in list(sources.PDF_DOCS) + list(thin_topics.PDF_DOCS):
        have |= {e.get("pdf") or "", e.get("archive") or ""}
    have.discard("")
    mine = [b.get("pdf") or b.get("archive") for b in G.PDFS]
    assert len(mine) == len(set(mine))
    assert not [m for m in mine if m in have]


def test_records_reach_sources():
    assert set(G.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert G.NOT_INCLUDED
    for row in G.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    said = " ".join(r[0] + r[1] for r in G.NOT_INCLUDED)
    for words in ("catalog.gpo.gov", "permanent.fdlp.gov", "NCBI Bookshelf", "nepis.epa.gov", "American Red Cross",
                  "Model Aquatic Health Code", "Federal Benefits for Veterans", "lending-library"):
        assert words.lower() in said.lower(), words
    assert "GOVINFO_API_KEY" in G.LICENCE_LINES["govinfo_fill_signup"]


def test_sign_up_book_without_a_key_fetches_nothing(monkeypatch):
    monkeypatch.delenv(G.KEY_ENV, raising=False)
    monkeypatch.setattr(G, "api_search", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    left = []
    assert G.new_book("new:ready", "work", None, left) is None
    assert left and left[0]["fetch_yourself"] and left[0]["url"] == G.SIGNUP and G.KEY_ENV in left[0]["reason"]
    assert G.new_sign("new:ready") == ""
    assert G.COLLECTION.sign("gpo:new:ready") == ""


def test_sign_up_book_with_a_key(monkeypatch):
    key = "MADE-UP-KEY-0000"
    monkeypatch.setenv(G.KEY_ENV, key)
    rows = [{"title": "Made-Up Flood Guide", "packageId": "GOVPUB-HS5_100-PURL-gpo000001",
             "dateIssued": "2026-01-01", "governmentAuthor": ["Homeland Security", "FEMA"]}]
    asked = []
    monkeypatch.setattr(G, "api_search", lambda k, docclass, size=100: asked.append((k, docclass)) or rows)
    left = []
    book = G.new_book("new:ready", "work", None, left)
    assert book is not None and not left
    assert [d for _k, d in asked] == G.AREAS["ready"][4] and all(k == key for k, _d in asked)
    assert book.group == disaster_ready.COLLECTION.group and len(book.pages) == len(G.AREAS["ready"][4])
    html = book.pages[0].body
    assert "Made-Up Flood Guide" in html and "/content/pkg/GOVPUB-HS5_100-PURL-gpo000001/pdf/" in html
    assert key not in json.dumps([p.body for p in book.pages]) + book.notice + book.description
    assert G.new_sign("new:ready")


def test_refused_key_is_said(monkeypatch):
    monkeypatch.setenv(G.KEY_ENV, "MADE-UP-BAD-KEY")

    def refuse(*a, **k):
        raise urllib.error.HTTPError(G.API, 403, "Forbidden", {}, io.BytesIO(b""))
    monkeypatch.setattr(G, "api_search", refuse)
    left = []
    assert G.new_book("new:mind", "work", None, left) is None
    assert "refused the key" in left[0]["reason"]


def test_the_key_goes_in_a_header_only(monkeypatch):
    seen = {}

    class Answer(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_open(url, secret_headers, data=None, headers=None, method=None, timeout=None):
        """A made-up build_textbooks.keyed_urlopen: records what would be sent (the key in its own headers)."""
        seen["url"], seen["headers"], seen["body"] = url, dict(secret_headers), data
        return Answer(json.dumps({"results": [{"packageId": "X"}]}).encode())
    import build_textbooks
    monkeypatch.setattr(build_textbooks, "keyed_urlopen", fake_open)
    out = G.api_search("MADE-UP-KEY-1234", "TD8")
    assert out == [{"packageId": "X"}]
    assert seen["url"] == G.API and "MADE-UP-KEY-1234" not in seen["url"]
    assert seen["headers"] == {"X-Api-Key": "MADE-UP-KEY-1234"}
    body = json.loads(seen["body"])
    assert body["query"] == "collection:GOVPUB AND docclass:TD8" and "MADE-UP-KEY-1234" not in seen["body"].decode()
