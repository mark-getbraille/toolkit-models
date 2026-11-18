"""Self-tests of the textbooks builder with a made-up book only (sample_book.py): nothing is downloaded.

Run it from the repository's folder:   python3 -m pytest textbooks/test_textbooks.py
"""

import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import mathtext  # noqa: E402
from sample_book import make_sample_repo  # noqa: E402


def test_math_as_text():
    """Formulas become linear text a screen reader and liblouis can read."""
    assert mathtext.latex_text(r"\frac{1 + \sqrt{5}}{2}") == "(1 + sqrt(5))/2"
    assert mathtext.latex_text(r"x^{2} - 4 \ne 0") == "x^2 − 4 ≠ 0"
    assert mathtext.latex_text(r"\text{0,}\dot{3}") == "0,3 recurring"


def test_licences():
    """Licences are read from words and addresses; NoDerivatives is never allowed."""
    assert B.licence_short("Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International") == \
        "CC BY-NC-SA 4.0"
    assert B.licence_short("", "http://creativecommons.org/licenses/by/4.0/") == "CC BY 4.0"
    assert B.licence_short("CC BY NC SA 3.0 IGO") == "CC BY-NC-SA 3.0 IGO"
    assert B.licence_kind("CC BY-ND 4.0") == "" and B.licence_kind("CC BY 4.0") == "open"
    assert B.licence_words("CC BY-NC-SA 4.0") == "CC BY-NC-SA 4.0, not for commercial use"


def test_sample_book(tmp_path):
    """The made-up book becomes a ZIM file with chapter and section pages, numbered figures, text math, no teacher
    notes, an index page, and a manifest entry with size and SHA-256."""
    repo = make_sample_repo(str(tmp_path / "repo"))
    out = str(tmp_path / "out")
    manifests = B.build([], out, local_osbooks=repo)
    entry = list(manifests.values())[0]["books"][0]
    assert entry["licence"] == "CC BY 4.0" and entry["credit"] == "OpenStax, Rice University"
    path = os.path.join(out, entry["file"])
    assert entry["size"] == os.path.getsize(path) and len(entry["sha256"]) == 64
    with open(path, "rb") as f:
        assert struct.unpack("<I", f.read(4))[0] == 72173914
    book = B.osbooks_books(repo)[0]
    titles = [p.title for p in book.pages]
    assert titles == ["Preface", "Chapter 1: The Urinary System", "1.1 The Kidney", "Chapter 2: The Heart",
                      "2.1 The Heart"]
    kidney = book.pages[2].body
    assert "Figure 1.1" in kidney and "A bean-shaped organ" in kidney and "v = d/t" in kidney and "H₂O" in kidney
    assert "SECRET TEACHER TEXT" not in kidney and "Everyday Connection" in kidney
    assert "Table 1.1" in kidney and "Question 1" in kidney and "The nephron." in kidney
    assert 'href="1-1-the-kidney#fig-kidney">Figure 1.1' in book.pages[4].body
    data = B.merge([os.path.join(out, n) for n in os.listdir(out) if n.startswith("manifest-")])
    assert data["books"][0]["name"] == "openstax_tiny_science" and data["not_included"]
    json.dumps(data)
