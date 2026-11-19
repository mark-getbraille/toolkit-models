"""Self-test of manuals.json's kept versions (build_manuals.merge_catalogue), with made-up manifests only."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as M  # noqa: E402


def manifest(built, content, entries=10):
    """A made-up manifest of the category "cars"."""
    return {"key": "cars", "file": f"manuals-cars.{built}.json.gz", "size": 100, "sha256": "s" + built,
            "built": built, "entries": entries, "content_sha256": content, "files": [f"manuals-cars.{built}.json.gz"]}


def test_versions_kept():
    """A changed index is a new version and the old one stays listed; the same entries add nothing; an index built
    before versions existed becomes the first old version."""
    first = M.merge_catalogue([manifest("2026-11-01", "a")])["collections"]["cars"]
    assert first["versions"][0]["change_note"] == "First version"
    same = M.merge_catalogue([manifest("2026-11-08", "a")], {"collections": {"cars": first}})["collections"]["cars"]
    assert same == first
    new = M.merge_catalogue([manifest("2026-11-15", "b", 12)], {"collections": {"cars": first}})["collections"]["cars"]
    assert new["file"] == "manuals-cars.2026-11-15.json.gz" and [v["built"] for v in new["versions"]] == [
        "2026-11-15", "2026-11-01"]
    assert new["versions"][0]["url"].endswith("/manuals/manuals-cars.2026-11-15.json.gz")
    legacy = {"key": "cars", "file": "manuals-cars.json.gz", "size": 90, "sha256": "x", "built": "2026-10-01"}
    up = M.merge_catalogue([manifest("2026-11-15", "b")], {"collections": {"cars": legacy}})["collections"]["cars"]
    assert [v["file"] for v in up["versions"]] == ["manuals-cars.2026-11-15.json.gz", "manuals-cars.json.gz"]
