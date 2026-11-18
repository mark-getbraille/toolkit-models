"""A self-test of the top-up passes in build_packs.py, with a made-up pack builder and a made-up "published" pack in
a temporary folder: nothing is downloaded from the internet and no real pack is touched.

It checks that a top-up pass:
  - keeps every row and picture of the published pack, unchanged;
  - adds only new pictures, leaving out one with an address already in the pack, one whose picture content is
    already in the pack, and the extra rows of pictures that were left out;
  - renames a new picture that only happens to share an old picture's file name;
  - merges CREDITS.txt and considered-<key>.jsonl without repeats, counts the pass, and names its files
    <key>.pass2.zip so the published files are not overwritten;
  - writes nothing to publish (so the workflow keeps the old pack) when it adds nothing, when the pack already has
    its limit, and when the published pack did not download whole;
  - builds from the start when the pack is not published yet;
  - shuffles exactly as before on a normal build and differently on a top-up pass (pass_random).

Run it from the repository's folder:   python3 packs/test_top_up.py      (or: python3 -m pytest packs/test_top_up.py)
"""

import io
import json
import os
import random
import shutil
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_packs  # noqa: E402

KEY = "selftest_topup"
SAY = []                      # what the builder said (instead of printing it)


def picture(shade):
    """A small made-up JPEG picture, one colour (shade, 0-255), so each shade gives different picture content."""
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (80, 80), (shade, 255 - shade, (shade * 7) % 256)).save(out, "JPEG", quality=90)
    return out.getvalue()


# What the made-up builder brings on its next run: [(file name, address, picture shade, extra rows)].
PLAN = []


def fake_builder(limit):
    """A made-up pack builder: it "downloads" the pictures in PLAN (noting each address, as fetch_all does) and
    returns them as pack entries, with any extra rows pointing at the same picture (as food_packs.with_twins)."""
    entries = []
    for name, url, shade, extra in PLAN[:limit + 5]:
        build_packs.considered(name, url, "")
        build_packs.note_source(name, url)
        entries.append((name, picture(shade), {"question": "Describe this picture.", "answer": f"Shade {shade}.",
                                               "credit": f"Made-up picture {name}, CC0"}))
        entries += [(None, None, {"question": q, "answer": a, "credit": f"Made-up picture {name}, CC0",
                                  "file": f"pictures/{name}"}) for q, a in extra]
    return entries


def reset():
    """Put build_packs back as it is when a build starts (each check below is a separate build)."""
    build_packs.PASS, build_packs.TOP_UP = 1, None
    build_packs.SOURCES.clear()
    build_packs.CONSIDERED.clear()
    os.environ.pop("PACK_PASS", None)
    build_packs.PACKS[KEY] = (fake_builder, "Made-up self-test pictures, CC0.")


def publish(out, published):
    """Copy a built pack (its parts and manifest) into the made-up release folder and write its packs.json there,
    as the workflow's upload and manifest jobs do."""
    with open(os.path.join(out, f"manifest-{KEY}.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    os.makedirs(published, exist_ok=True)
    for name in manifest["files"]:
        shutil.copyfile(os.path.join(out, name), os.path.join(published, name))
    with open(os.path.join(published, "packs.json"), "w", encoding="utf-8") as f:
        json.dump({KEY: manifest}, f)
    return manifest


def read_pack(folder, manifest):
    """(rows, {picture name: bytes}, CREDITS text, considered notes) of a pack whose files are in folder."""
    data = b"".join(open(os.path.join(folder, name), "rb").read() for name in manifest["files"])
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        rows = [json.loads(line) for line in z.read("rows.jsonl").decode().splitlines()]
        pictures = {n[len("pictures/"):]: z.read(n) for n in z.namelist() if n.startswith("pictures/")}
        notes = [json.loads(line) for line in z.read(f"considered-{KEY}.jsonl").decode().splitlines()] \
            if f"considered-{KEY}.jsonl" in z.namelist() else []
        return rows, pictures, z.read("CREDITS.txt").decode(), notes


def first_pack(scratch):
    """Build and "publish" the first pass of the made-up pack: three pictures, one with a second row. Returns (the
    release folder, its manifest)."""
    reset()
    PLAN[:] = [("a.jpg", "https://example.org/a", 10, [("What colour is it?", "Dark.")]),
               ("b.jpg", "https://example.org/b", 60, []),
               ("c.jpg", "https://example.org/c", 110, [])]
    out, published = os.path.join(scratch, "first"), os.path.join(scratch, "release")
    assert build_packs.main([KEY, "--out", out, "--limit", "3"]) == 0
    return published, publish(out, published)


def test_top_up_adds_only_new_pictures():
    """A top-up pass keeps the old pack, drops repeats, renames a clash and merges credits and notes."""
    with tempfile.TemporaryDirectory() as scratch:
        published, old = first_pack(scratch)
        old_rows, old_pictures, _, _ = read_pack(published, old)
        reset()
        PLAN[:] = [("a-again.jpg", "https://example.org/a", 200, [("Twin?", "Should be left out.")]),  # same address
                   ("b-copy.jpg", "https://example.org/b-copy", 60, []),     # same picture content as b.jpg
                   ("c.jpg", "https://example.org/c-new", 150, []),          # same name, another picture: renamed
                   ("d.jpg", "https://example.org/d", 170, [("Is it bright?", "Yes.")]),
                   ("e.jpg", "https://example.org/e", 190, []),
                   ("f.jpg", "https://example.org/f", 230, [])]              # over the limit of 6
        out = os.path.join(scratch, "second")
        assert build_packs.main([KEY, "--out", out, "--limit", "6", "--top-up", "--published", published]) == 0
        manifest = json.load(open(os.path.join(out, f"manifest-{KEY}.json")))
        assert manifest["passes"] == 2 and manifest["files"] == [f"{KEY}.pass2.zip"], manifest
        rows, pictures, credits, notes = read_pack(out, manifest)
        assert rows[:len(old_rows)] == old_rows, "the old rows must come first, unchanged"
        for name, data in old_pictures.items():
            assert pictures[name] == data, f"old picture {name} changed"
        assert sorted(pictures) == ["a.jpg", "b.jpg", "c-p2.jpg", "c.jpg", "d.jpg", "e.jpg"], sorted(pictures)
        new_rows = rows[len(old_rows):]
        assert [r.get("file") for r in new_rows] == ["pictures/c-p2.jpg", "pictures/d.jpg", "pictures/d.jpg",
                                                     "pictures/e.jpg"], new_rows
        assert not any(r["answer"] == "Should be left out." for r in rows)
        assert new_rows[0]["source"] == "https://example.org/c-new", "a new picture keeps its address as source"
        assert all(r.get("source") for r in old_rows if r["question"] == "Describe this picture.")
        credit_lines = credits.split("\n\n", 1)[1].splitlines()
        assert len(credit_lines) == len(set(credit_lines)), "each credit line once"
        assert set(credit_lines) == {f"{r['file']}: {r['credit']}" for r in rows}, credits
        assert manifest["rows"] == len(rows) and manifest["pictures"] == len(rows)
        used = {n["url"] for n in notes if n["used"]}
        assert {"https://example.org/a", "https://example.org/c-new", "https://example.org/e"} <= used, notes
        assert len({n["url"] for n in notes}) == len(notes), "each candidate once in considered"
        assert not os.path.exists(os.path.join(out, "published", f"{KEY}-published.zip")), "download removed"

        # A third pass over the merged pack: the pass number keeps counting and the "source" fields are used.
        publish(out, published)
        reset()
        PLAN[:] = [("c.jpg", "https://example.org/c-new", 150, []), ("g.jpg", "https://example.org/g", 250, [])]
        out3 = os.path.join(scratch, "third")
        assert build_packs.main([KEY, "--out", out3, "--limit", "9", "--top-up", "--published", published]) == 0
        manifest3 = json.load(open(os.path.join(out3, f"manifest-{KEY}.json")))
        _, pictures3, _, _ = read_pack(out3, manifest3)
        assert manifest3["passes"] == 3 and sorted(set(pictures3) - set(pictures)) == ["g.jpg"], sorted(pictures3)


def test_nothing_new_keeps_the_old_pack():
    """A pass that finds only pictures already in the pack, or a pack that is full, publishes nothing."""
    with tempfile.TemporaryDirectory() as scratch:
        published, old = first_pack(scratch)
        before = {n: open(os.path.join(published, n), "rb").read() for n in os.listdir(published)}
        reset()
        PLAN[:] = [("a.jpg", "https://example.org/a", 10, []), ("b2.jpg", "https://example.org/b2", 60, [])]
        out = os.path.join(scratch, "again")
        assert build_packs.main([KEY, "--out", out, "--limit", "6", "--top-up", "--published", published]) == 0
        assert not os.path.exists(os.path.join(out, f"manifest-{KEY}.json")), "nothing new: nothing to publish"
        reset()
        full = os.path.join(scratch, "full")
        assert build_packs.main([KEY, "--out", full, "--limit", "3", "--top-up", "--published", published]) == 0
        assert not os.path.exists(os.path.join(full, f"manifest-{KEY}.json")), "a full pack is left as it is"
        after = {n: open(os.path.join(published, n), "rb").read() for n in os.listdir(published)}
        assert before == after, "the published pack must not change"


def test_damaged_download_stops_without_publishing():
    """A published pack that does not match packs.json's SHA-256 stops the top-up with an error."""
    with tempfile.TemporaryDirectory() as scratch:
        published, old = first_pack(scratch)
        with open(os.path.join(published, old["files"][0]), "r+b") as f:
            f.seek(40)
            f.write(b"XX")
        reset()
        out = os.path.join(scratch, "damaged")
        try:
            build_packs.main([KEY, "--out", out, "--limit", "6", "--top-up", "--published", published])
        except SystemExit as e:
            assert "did not download whole" in str(e)
        else:
            raise AssertionError("a damaged download must stop the top-up")
        assert not os.path.exists(os.path.join(out, f"manifest-{KEY}.json"))


def test_not_published_builds_from_the_start():
    """--top-up of a pack that is not published yet is an ordinary first build."""
    with tempfile.TemporaryDirectory() as scratch:
        reset()
        PLAN[:] = [("a.jpg", "https://example.org/a", 10, [])]
        out = os.path.join(scratch, "new")
        assert build_packs.main([KEY, "--out", out, "--limit", "3", "--top-up", "--published",
                                 os.path.join(scratch, "empty-release")]) == 0
        manifest = json.load(open(os.path.join(out, f"manifest-{KEY}.json")))
        assert manifest["passes"] == 1 and manifest["files"] == [f"{KEY}.zip"]


def test_pass_random():
    """pass_random is random.Random on a normal build and shuffles differently on a top-up pass."""
    reset()
    order = list(range(50))
    first, plain = order[:], order[:]
    build_packs.pass_random(7919).shuffle(first)
    random.Random(7919).shuffle(plain)
    assert first == plain, "a normal build must shuffle exactly as before"
    build_packs.PASS = 2
    second = order[:]
    build_packs.pass_random(7919).shuffle(second)
    assert second != first, "a top-up pass must look at the candidates in another order"
    reset()


def test_new_only():
    """new_only (used by the shared helpers before they cut the list to the limit) skips what the pack has."""
    with tempfile.TemporaryDirectory() as scratch:
        published, _ = first_pack(scratch)
        reset()
        build_packs.start_top_up(KEY, 10, os.path.join(scratch, "x"), published)
        items = [("a.jpg", "https://example.org/zzz", None),      # name in the pack, its address differs: kept
                 ("q.jpg", "https://example.org/b", None),        # address in the pack: skipped
                 ("n.jpg", "https://example.org/n", None)]
        assert [i[0] for i in build_packs.new_only(items)] == ["a.jpg", "n.jpg"]
        reset()
        assert build_packs.new_only(items) == items, "a normal build skips nothing"


if __name__ == "__main__":
    import contextlib
    checks = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for check in checks:
        with contextlib.redirect_stdout(io.StringIO()):
            check()
        print(f"passed: {check.__name__}")
    print(f"All {len(checks)} top-up checks passed.")
