"""A self-test of the pictures set aside for a description (build_packs.needs_description, write_needs and the
"needs only" mode), with made-up pictures and a made-up "published" release in a temporary folder: nothing is
downloaded from the internet and no real pack is touched.

It checks that:
  - needs_description refuses a NoDerivatives licence, an unknown licence category, words about nudity or sex, a
    repeat and anything over the cap, and keeps the marks ("child" found in the words, "content", never for
    picture-making);
  - in a real builder (NPGallery, with its web answers made up), a picture dropped only for its missing alt text is
    set aside, but one with a copyrighted licence or with nudity in its words is not, and the archive and graphic
    packs' own safety checks refuse torture, slurs and a dead child before anything is set aside;
  - needs-<key>.v1.zip has needs.jsonl (one row per picture with every field), the pictures, README.txt,
    CREDITS.txt and a describing.json that the training kit opens as a review collection, every picture "new";
  - a "needs only" run writes only the needs zip (no pack manifest, the published pack unchanged), never sets aside
    a picture already in the pack, and a second run keeps the first needs zip and adds only new pictures (v2);
  - a top-up pass adds to the published needs zip too.

Run it from the repository's folder:   python3 packs/test_needs.py      (or: python3 -m pytest packs/test_needs.py)
"""

import io
import json
import os
import shutil
import sys
import tempfile
import types
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_packs  # noqa: E402

KEY = "selftest_needs"
PLAN = []          # what the made-up builder sees: [(name, address, shade, description or "", licence)]


def picture(shade):
    """A small made-up JPEG picture of one colour."""
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (90, 70), (shade, 255 - shade, (shade * 5) % 256)).save(out, "JPEG", quality=90)
    return out.getvalue()


def fake_builder(limit):
    """A made-up builder: a picture with a description of four words or more goes into the pack; one without is set
    aside (its bytes given, as a builder reading a zip does); one with a copyrighted licence is dropped for that."""
    entries = []
    for name, url, shade, text, licence in PLAN:
        if licence == "copyrighted":
            continue                                         # a licence drop: never set aside
        if len(text.split()) < 4:
            build_packs.needs_description(name, url, f"Made-up {name}, {licence}", licence, text=text,
                                          title=f"Title of {name}", page_url=url + "/page",
                                          reason="its caption is under four words", data=picture(shade),
                                          extra={"tags": ["made", "up"]})
            continue
        if build_packs.NEEDS_ONLY:
            continue                                         # (as fetch_all: nothing is downloaded)
        build_packs.note_source(name, url)
        entries.append((name, picture(shade), {"question": "Describe this picture.", "answer": text,
                                               "credit": f"Made-up {name}, {licence}"}))
    return entries[:limit]


def reset():
    """Put build_packs back as it is when a build starts."""
    build_packs.PASS, build_packs.TOP_UP = 1, None
    build_packs.SOURCES.clear()
    build_packs.CONSIDERED.clear()
    build_packs.reset_needs()
    os.environ.pop("PACK_PASS", None)
    build_packs.PACKS[KEY] = (fake_builder, "Made-up self-test pictures, CC0.")


def publish(out, published):
    """Copy what a build wrote into the made-up release folder, as the workflow does: the pack (with packs.json)
    when there is one, and the needs zip with needs-manifest.json."""
    os.makedirs(published, exist_ok=True)
    pack = os.path.join(out, f"manifest-{KEY}.json")
    if os.path.exists(pack):
        manifest = json.load(open(pack, encoding="utf-8"))
        for name in manifest["files"]:
            shutil.copyfile(os.path.join(out, name), os.path.join(published, name))
        json.dump({KEY: manifest}, open(os.path.join(published, "packs.json"), "w", encoding="utf-8"))
    needs = os.path.join(out, f"needs-manifest-{KEY}.json")
    if os.path.exists(needs):
        manifest = json.load(open(needs, encoding="utf-8"))
        shutil.copyfile(os.path.join(out, manifest["file"]), os.path.join(published, manifest["file"]))
        json.dump({KEY: manifest}, open(os.path.join(published, "needs-manifest.json"), "w", encoding="utf-8"))


def read_needs(folder, manifest):
    """(rows, {picture name: bytes}, describing.json, README text) of a needs zip."""
    with zipfile.ZipFile(os.path.join(folder, manifest["file"])) as z:
        rows = [json.loads(line) for line in z.read("needs.jsonl").decode().splitlines()]
        pictures = {n[len("pictures/"):]: z.read(n) for n in z.namelist() if n.startswith("pictures/")}
        return rows, pictures, json.loads(z.read("describing.json")), z.read("README.txt").decode()


def test_needs_description_rules():
    """The refusals and the marks kept."""
    reset()
    build_packs.NEEDS_LIMIT = 3
    data = picture(40)
    nd = build_packs.needs_description("a.jpg", "https://example.org/a", "x", "CC BY-ND 4.0", data=data)
    nc_nd = build_packs.needs_description("a2.jpg", "https://example.org/a2", "x", "CC BY-NC-ND 2.0", data=data)
    words = build_packs.needs_description("b.jpg", "https://example.org/b", "x", "CC0", title="A nude study")
    odd = build_packs.needs_description("c.jpg", "https://example.org/c", "x", "CC0", category="mystery")
    assert not (nd or nc_nd or words or odd), "ND, nudity and an unknown category are never set aside"
    assert build_packs.needs_description("d.jpg", "https://example.org/d", "x", "CC0", title="Two boys on a pier")
    assert build_packs.needs_description("e.jpg", "https://example.org/e", "x", "public domain",
                                         extra={"content": "graphic", "date": "1944"})
    assert not build_packs.needs_description("d2.jpg", "https://example.org/d", "x", "CC0"), "a repeat address"
    assert build_packs.needs_description("f.jpg", "https://example.org/f", "x", "CC BY 4.0", category="noncommercial")
    assert not build_packs.needs_description("g.jpg", "https://example.org/g", "x", "CC0"), "over the cap of 3"
    d, e, f = build_packs.NEEDS
    assert d["child"] and d["not_for_picture_making"], "a child in the words is marked, never for picture-making"
    assert e["content"] == "graphic" and e["not_for_picture_making"] and e["hints"] == {"date": "1944"}
    assert not f["child"] and not f["not_for_picture_making"] and f["category"] == "noncommercial"
    reset()


def fake_npgallery_answers(results):
    """A stand-in for documentary_packs.get_json: NPGallery's search answers with results for the first word only."""
    calls = []

    def get_json(s, url, params=None, tries=4, pause=5):
        calls.append(params)
        return {"Results": results} if len(calls) == 1 else {"Results": []}
    return get_json


def test_builder_sets_aside_only_description_drops():
    """build_npgallery (its web answers made up): only the public-domain photo whose alt text is too short is set
    aside; a copyrighted one and one whose words are about nudity are not."""
    import documentary_packs as dp
    reset()
    build_packs.NEEDS_ONLY = True            # nothing is downloaded
    asset = lambda key, alt, rights="Public domain", title="A view": {"Asset": {   # noqa: E731
        "AssetID": key, "PrimaryType": "image", "AltText": alt, "Title": title,
        "ConstraintsInformation": {"Constraint": rights}, "NPSUnits": [{"Name": "Wind Cave National Park"}]}}
    results = [asset("good", "Bison grazing on a grassy hill under a wide blue sky"),
               asset("short", "Bison"),
               asset("copyrighted", "Bison", rights="Copyright"),
               asset("nude", "A naked hiker", title="Hiker")]
    saved = dp.get_json, dp.time
    dp.get_json = fake_npgallery_answers(results)
    dp.time = types.SimpleNamespace(sleep=lambda seconds: None, time=__import__("time").time)
    try:
        dp.build_npgallery(10)
    finally:
        dp.get_json, dp.time = saved
    names = [n["name"] for n in build_packs.NEEDS]
    assert names == ["npgallery-short.jpg"], names
    item = build_packs.NEEDS[0]
    assert item["page_url"].endswith("AssetDetail/short") and item["licence"] == "public domain", item
    assert item["hints"]["text"] == "Bison" and item["place"] == "Wind Cave National Park, USA", item
    reset()


def test_safety_checks_come_first():
    """The archive and graphic packs' own safety checks refuse a picture before it is set aside."""
    import archive_packs
    import graphic_packs
    reset()
    assert not archive_packs.set_aside("t.jpg", "https://example.org/t", "x", "public domain", text="Torture camp")
    assert not archive_packs.set_aside("s.jpg", "https://example.org/s", "x", "public domain", text="Japs landing")
    assert not graphic_packs.graphic_aside("k.jpg", "https://example.org/k", "x", "public domain",
                                           text="Dead child", title="")
    assert archive_packs.set_aside("w.jpg", "https://example.org/w", "x", "public domain", text="Wounded soldiers")
    assert graphic_packs.graphic_aside("r.jpg", "https://example.org/r", "x", "public domain", text="Ruins")
    marks = [(n["name"], n["content"]) for n in build_packs.NEEDS]
    assert marks == [("w.jpg", "graphic"), ("r.jpg", "graphic")], marks
    reset()


def test_needs_zip_format():
    """A normal build writes the pack and needs-<key>.v1.zip with every field; the describing.json in it opens in
    the training kit as a review collection with every picture new."""
    with tempfile.TemporaryDirectory() as scratch:
        reset()
        PLAN[:] = [("a.jpg", "https://example.org/a", 10, "A red square on a plain table", "CC0"),
                   ("b.jpg", "https://example.org/b", 60, "Short", "CC0"),
                   ("c.jpg", "https://example.org/c", 110, "", "CC BY 4.0"),
                   ("x.jpg", "https://example.org/x", 160, "", "copyrighted")]
        out = os.path.join(scratch, "out")
        assert build_packs.main([KEY, "--out", out, "--limit", "5", "--published", os.path.join(scratch, "rel")]) == 0
        manifest = json.load(open(os.path.join(out, f"needs-manifest-{KEY}.json")))
        assert manifest["file"] == f"needs-{KEY}.v1.zip" and manifest["count"] == 2 and manifest["version"] == 1
        assert manifest["category"] == "open" and manifest["sha256"] and manifest["date"]
        rows, pictures, meta, readme = read_needs(out, manifest)
        assert sorted(pictures) == ["b.jpg", "c.jpg"], sorted(pictures)
        row = rows[0]
        for field in ("file", "url", "page_url", "credit", "licence", "category", "source", "hints", "reason",
                      "place", "place_kind", "content", "child", "not_for_picture_making", "added"):
            assert field in row, field
        assert row["source"] == KEY and row["hints"]["text"] == "Short" and row["hints"]["tags"] == ["made", "up"]
        assert row["page_url"] == "https://example.org/b/page" and row["file"] == "pictures/b.jpg"
        assert meta["review_only"] is True and meta["never_for_picture_making"] is True
        assert meta["review_category"] == "open" and meta["review_source"] == f"needs-{KEY}"
        assert all(e["status"] == "new" for e in meta["pictures"].values())
        assert "Short" in meta["pictures"]["b.jpg"]["notes"] and meta["pictures"]["b.jpg"]["hint"]
        assert "Nothing here is ever used for training" in readme
        pack = json.load(open(os.path.join(out, f"manifest-{KEY}.json")))
        assert pack["pictures"] == 1, "only the described picture is in the pack"
        kit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "training-kit", "kit")
        sys.path.insert(0, kit)
        import describe_package
        space = os.path.join(scratch, "space")
        summary = describe_package.import_package(space, os.path.join(out, manifest["file"]))
        assert "2 new pictures" in summary, summary
        workspace = describe_package.open_workspace(space)
        assert describe_package.is_review(workspace)
        assert {workspace.entry(n)["status"] for n in workspace.pictures} == {"new"}
        assert workspace.entry("b.jpg")["page_url"] == "https://example.org/b/page"
        reset()


def test_needs_only_leaves_the_pack_alone():
    """A needs-only run writes only the needs zip; a second one adds to it without repeats; nothing in the pack is
    set aside; a top-up pass adds to the needs zip too."""
    with tempfile.TemporaryDirectory() as scratch:
        published = os.path.join(scratch, "release")
        reset()
        PLAN[:] = [("a.jpg", "https://example.org/a", 10, "A red square on a plain table", "CC0"),
                   ("b.jpg", "https://example.org/b", 60, "A green square on a plain table", "CC0")]
        first = os.path.join(scratch, "first")
        assert build_packs.main([KEY, "--out", first, "--limit", "5", "--published", published]) == 0
        publish(first, published)
        assert not os.path.exists(os.path.join(published, "needs-manifest.json")), "nothing set aside yet"
        before = {n: open(os.path.join(published, n), "rb").read() for n in os.listdir(published)}

        # The collection now gives b.jpg no description (it is in the pack: never set aside) and has c and d new.
        reset()
        PLAN[:] = [("a.jpg", "https://example.org/a", 10, "A red square on a plain table", "CC0"),
                   ("b.jpg", "https://example.org/b", 60, "", "CC0"),
                   ("c.jpg", "https://example.org/c", 110, "", "CC0"),
                   ("d.jpg", "https://example.org/d", 150, "Blue", "CC BY 4.0")]
        second = os.path.join(scratch, "second")
        assert build_packs.main([KEY, "--out", second, "--limit", "5", "--needs-only", "--published", published]) == 0
        assert not os.path.exists(os.path.join(second, f"manifest-{KEY}.json")), "no pack is written"
        assert not any(n.endswith(".zip") and not n.startswith("needs-") for n in os.listdir(second))
        manifest = json.load(open(os.path.join(second, f"needs-manifest-{KEY}.json")))
        rows, pictures, _, _ = read_needs(second, manifest)
        assert sorted(pictures) == ["c.jpg", "d.jpg"], sorted(pictures)
        publish(second, published)
        after = {n: open(os.path.join(published, n), "rb").read() for n in before}
        assert after == before, "the published pack is unchanged"

        # A second needs-only run: the first needs zip is kept, only e.jpg is new.
        reset()
        PLAN.append(("e.jpg", "https://example.org/e", 200, "", "CC0"))
        third = os.path.join(scratch, "third")
        assert build_packs.main([KEY, "--out", third, "--limit", "5", "--needs-only", "--published", published]) == 0
        manifest3 = json.load(open(os.path.join(third, f"needs-manifest-{KEY}.json")))
        rows3, pictures3, meta3, _ = read_needs(third, manifest3)
        assert manifest3["version"] == 2 and manifest3["file"] == f"needs-{KEY}.v2.zip"
        assert sorted(pictures3) == ["c.jpg", "d.jpg", "e.jpg"] and rows3[:2] == rows, sorted(pictures3)
        assert sorted(meta3["pictures"]) == ["c.jpg", "d.jpg", "e.jpg"]
        publish(third, published)

        # Nothing new: no needs manifest is written (the published one stays).
        reset()
        fourth = os.path.join(scratch, "fourth")
        assert build_packs.main([KEY, "--out", fourth, "--limit", "5", "--needs-only", "--published", published]) == 0
        assert not os.path.exists(os.path.join(fourth, f"needs-manifest-{KEY}.json"))

        # A top-up pass of the pack sets aside f.jpg and adds it to the published needs zip.
        reset()
        PLAN[:] = PLAN + [("f.jpg", "https://example.org/f", 220, "", "CC0"),
                          ("g.jpg", "https://example.org/g", 240, "A yellow square on a plain table", "CC0")]
        fifth = os.path.join(scratch, "fifth")
        assert build_packs.main([KEY, "--out", fifth, "--limit", "5", "--top-up", "--published", published]) == 0
        manifest5 = json.load(open(os.path.join(fifth, f"needs-manifest-{KEY}.json")))
        _, pictures5, _, _ = read_needs(fifth, manifest5)
        assert sorted(pictures5) == ["c.jpg", "d.jpg", "e.jpg", "f.jpg"] and manifest5["version"] == 3
        assert os.path.exists(os.path.join(fifth, f"manifest-{KEY}.json")), "the pack itself got g.jpg"
        reset()


def test_url_only_rows():
    """A source whose terms do not allow copying pictures gives a row with the address only, no picture file."""
    with tempfile.TemporaryDirectory() as scratch:
        reset()
        build_packs.NEEDS_LIMIT = 5
        assert build_packs.needs_description("u.jpg", "https://example.org/u", "Photo, CC BY 2.0", "CC BY 2.0",
                                             url_only=True, data=picture(9))
        manifest = build_packs.write_needs(KEY, scratch, seconds=1)
        rows, pictures, meta, _ = read_needs(scratch, manifest)
        assert pictures == {} and rows[0]["url_only"] and "file" not in rows[0] and meta["pictures"] == {}
        reset()


if __name__ == "__main__":
    import contextlib
    checks = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for check in checks:
        with contextlib.redirect_stdout(io.StringIO()):
            check()
        print(f"passed: {check.__name__}")
    print(f"All {len(checks)} needs checks passed.")


def test_picture_names_stay_plain():
    """Picture names from other sites become plain file names that cannot leave the pack's folder when unpacked;
    names that are already plain stay exactly as they were."""
    for good in ("met-12345.jpg", "nara-mil-9.jpg", "europeana-2048_x.jpg", "pack_key"):
        assert build_packs.plain_name(good) == good
    for bad, plain in (("../../evil.jpg", "evil.jpg"), ("..\\..\\x.jpg", "x.jpg"), ("C:x y.jpg", "C_x_y.jpg"),
                       (".hidden.jpg", "hidden.jpg"), ("a..b.jpg", "a.b.jpg"), ("", "picture")):
        assert build_packs.plain_name(bad) == plain, bad
    assert build_packs.plain_file("pictures/../x.jpg") == "pictures/x.jpg"
    try:
        build_packs.write_pack("../evil", [], tempfile.mkdtemp())
        raise AssertionError("a pack key with a path was accepted")
    except ValueError:
        pass
