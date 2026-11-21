"""A guard: no code in this repository fetches iNaturalist's website or API.

Why: iNaturalist's website (www.inaturalist.org) says "ai-train=no", and the robots.txt of its API
(api.inaturalist.org) turns every program away. iNaturalist's research-grade observations are read instead from GBIF
(api.gbif.org, the dataset iNaturalist publishes there), with the photos from the iNaturalist Open Dataset on Amazon's
open-data programme (inaturalist-open-data.s3.amazonaws.com): packs/na_animal_packs.py ("iNaturalist through GBIF")
for the ready-made packs and kit/inat_gbif.py for the kit's own downloads.

It checks that:
  - no Python file of the repository (packs, the kit, tools, scripts) has an address on api.inaturalist.org or
    static.inaturalist.org in its code (comments and docstrings may name them, to explain why they are not used);
  - the only www.inaturalist.org addresses in code are the two that are shown to people and never fetched: the
    site's home page in a credit line and its terms page. Test files (test_*.py) are not looked at: they hold
    made-up records and addresses to show that iNaturalist's own addresses are refused, and never download;
  - no workflow, command or shell script names iNaturalist's API;
  - the kit reader refuses photos kept on iNaturalist's own website, turns GBIF's Open Dataset addresses into the
    "large" copy and checks each photo's own licence (packs/test_na_animals.py checks the packs' reader the same way).

Run it from the training-kit folder:   xvfb-run -a python3 -m pytest -q tests/test_no_inaturalist_site.py
"""

import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit")
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, KIT)
import inat_gbif  # noqa: E402

FORBIDDEN = re.compile(r"(api|static)\.inaturalist\.org", re.I)
SITE = re.compile(r"https?://([a-z0-9-]+\.)*inaturalist\.org\S*", re.I)
# The www.inaturalist.org addresses code may hold: shown to people (a credit, a terms link), never fetched.
SHOWN = {"https://www.inaturalist.org", "https://www.inaturalist.org/pages/terms"}


def python_files():
    """Every Python file of the repository except the tests (test_*.py) and anything under .git or a __pycache__
    folder."""
    for top, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for f in files:
            if f.endswith(".py") and not f.startswith("test_"):
                yield os.path.join(top, f)


def code_strings(path):
    """[(line, text)] of the string constants in a Python file's code, leaving out docstrings (which may explain
    why iNaturalist's site is not read). The pieces of an f-string are included."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body \
                and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            docs.add(id(node.body[0].value))
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs]


def test_no_code_fetches_inaturalist():
    """No address on iNaturalist's API or photo server in code; www.inaturalist.org only in credits and terms."""
    problems = []
    for path in python_files():
        for line, text in code_strings(path):
            where = f"{os.path.relpath(path, REPO)}:{line}"
            if FORBIDDEN.search(text):
                problems.append(f"{where}: {text[:100]!r}")
            for m in SITE.finditer(text):
                address = m.group(0).rstrip(".,;:)'\"")
                if address not in SHOWN:
                    problems.append(f"{where}: {address}")
    assert not problems, "Code that could fetch iNaturalist's website or API:\n" + "\n".join(problems)


def test_no_script_names_the_api():
    """No workflow, Windows command or shell script names iNaturalist's API or photo server."""
    problems = []
    for top, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for f in files:
            if f.endswith((".yml", ".yaml", ".cmd", ".bat", ".sh", ".ps1")):
                path = os.path.join(top, f)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    if FORBIDDEN.search(fh.read()):
                        problems.append(os.path.relpath(path, REPO))
    assert not problems, problems


def test_kit_reader_uses_the_open_dataset_only():
    """The kit reader takes photos only from the iNaturalist Open Dataset, as their "large" copy, and only under
    the licences asked for (each photo's own)."""
    s3 = "https://inaturalist-open-data.s3.amazonaws.com/photos/604606400/original.jpg"
    assert inat_gbif.open_data_photo(s3) == "https://inaturalist-open-data.s3.amazonaws.com/photos/604606400/large.jpg"
    assert inat_gbif.open_data_photo("https://static.inaturalist.org/photos/1/original.jpg") == ""
    assert inat_gbif.open_data_photo("https://example.org/photos/1/original.jpg") == ""
    assert inat_gbif.on_inaturalist_site("https://api.inaturalist.org/v1/observations")
    assert inat_gbif.on_inaturalist_site("https://www.inaturalist.org/")
    assert not inat_gbif.on_inaturalist_site(s3)
    assert inat_gbif.licence_code("http://creativecommons.org/licenses/by-nc-sa/4.0/") == "cc-by-nc-sa"
    assert inat_gbif.licence_code("http://creativecommons.org/publicdomain/zero/1.0/") == "cc0"
    record = {"key": 11, "references": "https://www.inaturalist.org/observations/5", "media": [
        {"type": "StillImage", "license": "http://creativecommons.org/licenses/by-sa/4.0/", "creator": "someone",
         "identifier": "https://static.inaturalist.org/photos/7/original.jpg"},
        {"type": "StillImage", "license": "http://creativecommons.org/licenses/by/4.0/", "creator": "someone",
         "identifier": "https://inaturalist-open-data.s3.amazonaws.com/photos/8/original.jpeg"},
        {"type": "StillImage", "license": "http://creativecommons.org/licenses/by-sa/4.0/", "creator": "someone",
         "identifier": "https://inaturalist-open-data.s3.amazonaws.com/photos/9/original.jpg"}]}
    media, code, url = inat_gbif.photo(record, ("cc-by-sa",))
    assert code == "cc-by-sa" and url.endswith("/photos/9/large.jpg") and inat_gbif.photo_id(url) == "9"
    assert inat_gbif.photo(record, ("cc-by-nc",)) == (None, "", "")
    assert inat_gbif.credit(record, media, code) == ("Photo by someone on iNaturalist, CC BY-SA, "
                                                     "https://www.inaturalist.org/observations/5 (via GBIF, "
                                                     "https://www.gbif.org/occurrence/11)")
    assert inat_gbif.evidence({"dynamicProperties": '{"evidenceOfPresence":"scat"}'}) == {"scat"}
    assert inat_gbif.latin({"taxonRank": "GENUS", "species": ""}) == ""

