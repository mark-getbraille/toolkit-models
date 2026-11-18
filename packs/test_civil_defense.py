"""A self-test of the civil defence parsers (packs/civil_defense_packs.py, training-kit/kit/civil_defense_figures.py
and training-kit/kit/civil_defense_sources.py), with made-up records and made-up pictures only: nothing is downloaded.

It checks that:
  - titles lose their form codes and years, and years are read from the record;
  - a booklet is used only when every maker is a US federal body (not a state office, a contractor or a university),
    it is dated 1950 to 1985, the Archive does not only lend it and no uploader put NC or ND on it;
  - a film is used only with a public-domain mark or a US federal agency as its maker, and never when its record
    names Hiroshima or the dead, or it is not about civil defense;
  - a film's sentence names its year, maker and sponsor from the record; its description is quoted only when long
    enough;
  - on a made-up page, a drawing is found and running text is not, a "Figure 3" caption is read, a separate short
    line under a drawing is a caption, and a block of words is never a picture;
  - stills that are black, white, blank, title cards or blurred are recognised, and an ordinary scene is not;
  - a burned-in logo near an edge and frame lines are found, and a clean film has none;
  - a booklet picture's rows: caption, cover, graphic, medical and child marks, and no rows without a caption;
  - the builders (with made-up downloads) set aside the pictures without a caption or film description;
  - the tables agree (every pack has a limit; the kit's groups and lists; the record is whole).

Run it from the repository's folder:   python3 -m pytest packs/test_civil_defense.py
"""

import io
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import civil_defense_packs as m  # noqa: E402
import civil_defense_figures as f  # noqa: E402


def meta(**fields):
    """A made-up Internet Archive item record."""
    base = {"title": "The Family fallout shelter", "creator": "United States. Office of Civil and Defense "
            "Mobilization", "date": "1959", "collection": ["prelinger_library", "americana"]}
    base.update(fields)
    return base


# ----------------------------------------------------------------- words and records

def test_titles_and_years():
    assert m.tidy_title("H-7 Family Shelter Designs 1962") == "Family Shelter Designs"
    assert m.tidy_title("IG-3-2 Basic Course For Civil Defense 1955") == "Basic Course For Civil Defense"
    assert m.tidy_title("Fallout protection : what to know and do about nuclear attack") == "Fallout protection"
    assert m.tidy_title("Operation Cue (1964 revision)") == "Operation Cue"
    assert m.tidy_title("Family Shelter Series PSD F-61-3 Basement Concrete Block Shelter") == \
        "Basement Concrete Block Shelter"
    assert m.year_of({"date": "1961-05"}) == 1961 and m.year_of({}, "Emergency Mass Feeding Course 1953") == 1953
    assert m.year_of({}) == 0
    assert m.doc_kind("Handbook For Fallout Shelter Management") == "handbook" and m.doc_kind("Ten for survival") == \
        "booklet"


def test_booklet_ok():
    assert m.booklet_ok(meta()) == ""
    assert m.booklet_ok(meta(creator=["United States. Office of Civil Defense", "United States. Extension "
                                      "Service"])) == ""
    assert "not a US federal civil defense" in m.booklet_ok(meta(creator="Wilding Picture Productions"))
    assert "not shown to be a US federal" in m.booklet_ok(meta(creator="Minnesota. Office of Civil Defense"))
    assert "not shown to be a US federal" in m.booklet_ok(meta(creator=["United States. Office of Civil Defense",
                                                                       "Rice University. Dept. of Architecture"]))
    assert "1987" in m.booklet_ok(meta(date="1987"))
    assert "lends" in m.booklet_ok(meta(collection=["internetarchivebooks", "inlibrary", "printdisabled"]))
    assert "uploader" in m.booklet_ok(meta(licenseurl="https://creativecommons.org/licenses/by-nc-nd/4.0/"))
    assert "without pictures" in m.booklet_ok(meta(title="Stockpile report to the Congress"))
    assert "childbirth" in m.booklet_ok(meta(title="Emergency childbirth"))


def test_film_ok_and_lead():
    duck = {"title": "Duck and Cover", "year": "1951", "creator": "Archer Productions, Inc.",
            "sponsor": "U.S. Federal Civil Defense Administration",
            "licenseurl": "http://creativecommons.org/licenses/publicdomain/",
            "subject": "Atomic-nuclear: Civil defense",
            "description": "Famous Civil Defense film for children in which Bert the Turtle shows what to do in case "
                           "of atomic attack."}
    why, licence = m.film_ok(duck)
    assert why == "" and "public domain" in licence
    assert m.film_lead(duck) == ("A still from the 1951 US civil defense film 'Duck and Cover', made by Archer "
                                 "Productions, Inc. for the U.S. Federal Civil Defense Administration.")
    assert m.film_description(duck).startswith("Famous Civil Defense film")
    assert m.film_description(dict(duck, description="Civil defense.")) == ""
    army = dict(duck, licenseurl="", creator="U.S. Army Pictorial Service", title="Occupying a Public Shelter")
    assert m.film_ok(army)[0] == "" and "17 U.S.C. 105" in m.film_ok(army)[1]
    studio = dict(duck, licenseurl="")
    assert "DO NOT ASSUME" in m.film_ok(studio)[0]
    assert "Hiroshima" in m.film_ok(dict(duck, description="Scenes of Hiroshima after the bomb."))[0]
    assert "not a civil defense film" in m.film_ok(dict(duck, title="The Armor Soldier on the Nuclear Battlefield"))[0]
    nc = dict(duck, licenseurl="https://creativecommons.org/licenses/by-nc-nd/4.0/")
    assert "non-commercial" in m.film_ok(nc)[0]


# ----------------------------------------------------------------- pages

def page_image():
    """A made-up scanned page (850 x 1100, grey array) with running text at the top, a drawing in the middle, and a
    block of small print near the bottom; and its OCR lines (pixels)."""
    import numpy as np
    from PIL import Image, ImageDraw
    img = Image.new("L", (850, 1100), 245)
    d = ImageDraw.Draw(img)
    lines = []
    for k in range(6):                                            # running text: dark bars where the words are
        y = 80 + k * 26
        d.rectangle((90, y, 760, y + 12), fill=40)
        lines.append({"box": (90, y, 760, y + 12), "text": "The shelter walls are built of solid concrete blocks "
                                                           "set in mortar", "body": True})
    d.rectangle((200, 300, 650, 620), outline=20, width=4)       # the drawing: a box with a roof and lines
    d.line((200, 300, 425, 230, 650, 300), fill=20, width=4)
    for x in range(230, 640, 40):
        d.line((x, 320, x, 600), fill=60, width=2)
    lines.append({"box": (330, 640, 520, 656), "text": "Figure 3. Basement concrete-block shelter", "body": False})
    for k in range(8):                                            # small print: a list, not a picture
        y = 850 + k * 22
        d.rectangle((150, y, 420, y + 10), fill=50)
        lines.append({"box": (150, y, 420, y + 10), "text": "Water for two weeks and canned food", "body": False})
    return np.asarray(img), lines


def test_regions_and_captions():
    gray, lines = page_image()
    blanked = [ln["box"] for ln in lines if ln["body"] or f.figure_match(ln["text"])]
    regions = f.find_regions(gray, blanked)
    drawing = [b for b in regions if b[1] < 330 and b[3] > 590]
    assert len(drawing) == 1
    assert f.caption_for(drawing[0], lines, gray.shape[0]) == ("3", "Basement concrete-block shelter")
    listed = [b for b in regions if b[1] > 800]
    assert all(f.words_cover(b, lines) > f.MOST_WORDS for b in listed)       # the list is words, not a picture
    plain = [dict(ln) for ln in lines if not ln["text"].startswith("Figure")]
    plain.append({"box": (300, 640, 560, 656), "text": "An outdoor concrete shelter", "body": False})
    plain.sort(key=lambda ln: ln["box"][1])
    assert f.caption_for(drawing[0], plain, gray.shape[0]) == ("", "An outdoor concrete shelter")
    noisy = [ln for ln in plain if ln["text"] != "An outdoor concrete shelter"]
    noisy.append({"box": (300, 640, 560, 656), "text": "E L E V A T o N", "body": False})
    noisy.sort(key=lambda ln: ln["box"][1])
    assert f.caption_for(drawing[0], noisy, gray.shape[0]) == ("", "")


def test_caption_words():
    assert f.figure_match("Figur-e 3").group(1) == "3"
    assert f.figure_match("Fig. 9.-Double-wall shelter").group(2) == "Double-wall shelter"
    assert f.tidy_caption("ABOVEGROUND DOUBLE-WALL SHELTER") == "Aboveground double-wall shelter"
    assert f.tidy_caption("a con- crete shelter.") == "a concrete shelter"
    assert not f.caption_ok("II. The Shelters") and not f.caption_ok("BILL OF MATIIRIAiS (T O MATIIRIAiS")
    assert not f.caption_ok("General information", strict=True)
    assert f.word_share("I. Fallout shelter is needed everywhere . . . . . . 3") == 1.0


def test_picture_kind():
    import numpy as np
    rng = np.random.default_rng(1)
    lines = np.full((200, 200), 245, dtype=np.uint8)
    lines[50:52, :] = 10
    assert f.picture_kind(lines) == "drawing"
    halftone = rng.integers(60, 200, size=(200, 200)).astype(np.uint8)
    assert f.picture_kind(halftone) == "photograph"


# ----------------------------------------------------------------- stills

def still(kind, seed=0):
    """A made-up 320 x 240 grey still: "scene" (shapes of many shades), "black", "white", "blank", "card" (lettering
    on a plain grey ground) or "blurred"."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    rng = random.Random(seed)
    if kind in ("black", "white", "blank"):
        return np.full((240, 320), {"black": 8, "white": 250, "blank": 128}[kind], dtype=np.uint8)
    img = Image.new("L", (320, 240), 110 if kind == "card" else 150)
    d = ImageDraw.Draw(img)
    if kind == "card":
        for row in range(5):
            for col in range(18):
                d.rectangle((40 + col * 14, 60 + row * 26, 42 + col * 14, 74 + row * 26), fill=235)
        return np.asarray(img)
    for _ in range(40):
        x, y = rng.randrange(320), rng.randrange(240)
        d.rectangle((x, y, x + rng.randrange(10, 80), y + rng.randrange(10, 60)), fill=rng.randrange(0, 255))
    if kind == "blurred":
        img = img.filter(ImageFilter.GaussianBlur(8))
    return np.asarray(img)


def test_still_problems():
    assert f.still_problem(still("scene")) == ""
    assert f.still_problem(still("black")) == "too dark"
    assert f.still_problem(still("white")) == "a white frame"
    assert f.still_problem(still("blank")) == "a blank frame"
    assert f.still_problem(still("card")) == "a title card"
    assert f.still_problem(still("blurred"), sharp_floor=200) == "blurred"


def test_fixed_marks():
    import numpy as np
    frames = [np.asarray(__import__("PIL.Image", fromlist=["Image"]).fromarray(still("scene", seed=s))
                         .resize((128, 96))) for s in range(20)]
    assert f.fixed_marks(frames) == (0.0, 0.0, 0.0, 0.0)
    marked = []
    for g in frames:
        g = g.copy()
        g[4:12, 104:124] = 250                                     # a white logo in the top right corner ...
        g[6:10, 108:120] = 0                                       # ... with dark lettering
        marked.append(g)
    cut = f.fixed_marks(marked)
    assert cut[0] > 0.05 or cut[3] > 0.05
    assert f.fixed_marks(frames[:5]) == (0.0, 0.0, 0.0, 0.0)       # too few stills to tell


# ----------------------------------------------------------------- rows and builders

def figure(caption="", label="", share=0.4, kind="drawing", labels=""):
    """A made-up picture found on a page."""
    return {"jpeg": jpeg(), "box": (0, 0, 10, 10), "label": label, "caption": caption, "labels": labels,
            "kind": kind, "share": share}


def jpeg(shade=90):
    """A made-up 200 x 150 JPEG."""
    from PIL import Image
    buffer = io.BytesIO()
    Image.new("RGB", (200, 150), (shade, shade, shade)).save(buffer, "JPEG")
    return buffer.getvalue()


def test_booklet_rows():
    rows, source, marks = m.booklet_rows(meta(), 3, 0, figure("Aboveground double-wall shelter", "9"), "credit")
    assert rows[0]["answer"] == ("This is a drawing from a 1959 US civil defense booklet, 'The Family fallout "
                                 "shelter': figure 9, aboveground double-wall shelter.")
    assert rows[1]["question"] == m.FROM_Q and rows[1]["answer"] == source
    assert source.endswith("published by the Office of Civil and Defense Mobilization.") and marks == {}
    rows, _, _ = m.booklet_rows(meta(), 0, 0, figure(share=0.6), "credit")
    assert rows[0]["answer"] == "It is the cover of a 1959 US civil defense booklet, 'The Family fallout shelter'."
    rows, _, _ = m.booklet_rows(meta(), 0, 1, figure(share=0.6), "credit")
    assert rows is None                                            # only the biggest picture is the cover
    rows, _, marks = m.booklet_rows(meta(), 4, 0, figure("Fallout areas at 1 hour after detonation", "1"), "c")
    assert marks == {"content": "graphic"} and rows[0]["content"] == "graphic"
    rows, _, marks = m.booklet_rows(meta(title="Civil defense in schools"), 4, 0, figure("Pupils at their desks"), "c")
    assert marks.get("child") is True
    rows, _, marks = m.booklet_rows(meta(title="Family guide emergency health care"), 4, 0,
                                    figure("Applying a splint to the arm"), "c")
    assert marks.get("content") == "medical"
    rows, _, _ = m.booklet_rows(meta(), 4, 0, figure(), "c")
    assert rows is None
    rows, _, _ = m.booklet_rows(meta(), 6, 0, figure(label="4"), "c", said="The posts (marked A in fig. 4) hold the "
                                                                           "roof beams in place.")
    assert "The booklet's text about it says" in rows[0]["answer"]


def test_booklet_builder(monkeypatch):
    """The booklet builder keeps the captioned pictures and sets aside the others (made-up item, PDF and pages)."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument.new()
    for _ in range(3):
        doc.new_page(612, 792)
    buffer = io.BytesIO()
    doc.save(buffer)
    pdf = buffer.getvalue()
    data = {"metadata": meta(), "files": [{"name": "booklet.pdf", "format": "Text PDF", "size": str(len(pdf))}]}
    pages = {0: [figure(share=0.6)], 1: [figure("Basement shelter", "2"), figure(labels="concrete block")],
             2: [figure("Pupils under their desks")]}
    monkeypatch.setattr(m, "item", lambda s, identifier: data)

    def fake_download(s, url, path, most_bytes):
        """Write the made-up PDF."""
        with open(path, "wb") as out:
            out.write(pdf)
        return True
    monkeypatch.setattr(m, "download", fake_download)
    calls = iter(range(10))
    monkeypatch.setattr(m.figures, "page_figures", lambda page: pages[next(calls)])
    build_packs.reset_needs()
    out = m.build_cd_booklets(10, ["familyfalloutshe00unitrich"])
    pictures = [(name, row) for name, data, row in out if data]
    assert len(pictures) == 3 and len(out) == 6                    # cover, figure 2, the pupils; two rows each
    assert any(row.get("child") for _, row in pictures)
    assert [n["reason"] for n in build_packs.NEEDS] == ["it has no printed caption"]
    assert build_packs.NEEDS[0]["hints"]["text"] == "concrete block"
    assert build_packs.NEEDS[0]["content"] == "graphic"           # a fallout booklet's uncaptioned picture
    build_packs.reset_needs()


def test_film_builder(monkeypatch, tmp_path):
    """The film builder keeps good stills with the fixed sentence, and sets aside every still of a film without a
    description (made-up items and stills)."""
    from PIL import Image
    paths = []
    for k in range(16):
        p = tmp_path / f"{k:05d}.jpg"
        Image.fromarray(still("scene", seed=k)).convert("RGB").save(p, "JPEG", quality=92)
        paths.append((30.0 + k * 10, str(p)))
    black = tmp_path / "black.jpg"
    Image.fromarray(still("black")).convert("RGB").save(black)
    paths.append((200.0, str(black)))
    films = {"DuckandC1951": {"title": "Duck and Cover", "year": "1951", "creator": "Archer Productions, Inc.",
                              "licenseurl": "http://creativecommons.org/licenses/publicdomain/",
                              "description": "Famous Civil Defense film for children in which Bert the Turtle shows "
                                             "what to do in case of atomic attack."},
             "Radiolog1961": {"title": "Radiological Defense", "year": "1961", "creator": "U.S. Office of Civil "
                              "Defense", "licenseurl": "http://creativecommons.org/licenses/publicdomain/",
                              "description": "Civil defense."}}
    monkeypatch.setattr(m, "item", lambda s, i: {"metadata": films[i], "files": [{"name": "f_512kb.mp4", "format":
                                                                                  "512Kb MPEG4", "size": "1000"}]})
    monkeypatch.setattr(m, "download", lambda s, url, path, most: True)
    monkeypatch.setattr(m, "ffmpeg_stills", lambda video, folder: (paths, 260.0))
    build_packs.reset_needs()
    out = m.build_cd_films(40, ["DuckandC1951", "Radiolog1961"])
    assert out and all(data for _, data, _ in out)
    row = out[0][2]
    assert row["question"] == m.FROM_Q and row["answer"].startswith("A still from the 1951 US civil defense film "
                                                                     "'Duck and Cover'")
    assert row["content"] == "graphic" and row["child"] is True
    assert len(out) <= 16                                          # the black frame is left out
    assert build_packs.NEEDS and all(n["reason"] == "the film's record has no description" for n in build_packs.NEEDS)
    build_packs.reset_needs()


def test_tables():
    """Every pack has a builder, a credit and a limit; the kit's groups and lists agree; the record is whole."""
    assert set(m.CIVIL_DEFENSE_PACKS) == set(m.CIVIL_DEFENSE_LIMITS) == {"cd_booklets", "cd_films"}
    assert all(callable(b) and "public domain" in c for b, c in m.CIVIL_DEFENSE_PACKS.values())
    assert set(m.FILMS_LEFT_OUT) <= set(m.FILMS) | {"MedicalA1950"}
    import civil_defense_sources as k
    groups = {s.key: s.group for s in k.CIVIL_DEFENSE_SOURCES}
    assert groups == {"cd_uk_booklets_research": "research", "cd_uk_films_research": "research",
                      "cd_canada_nc": "noncommercial", "cd_aus_nz_research": "research"}
    assert k.CIVIL_DEFENSE_PICTURE_MAKING_OK == set()
    assert all(s.terms.startswith("https://") and s.terms_summary for s in k.CIVIL_DEFENSE_SOURCES)
    keys = ("source", "offers", "terms", "terms_url", "robots", "result")
    assert all(set(e) == set(keys) and all(e[x] for x in keys) for e in k.CIVIL_DEFENSE_RECORD)
    results = " ".join(e["result"] for e in k.CIVIL_DEFENSE_RECORD)
    assert all(key in results for key in list(groups) + ["cd_booklets", "cd_films"])
    assert not set(k.UK_BOOKLETS) & set(k.CANADA_BOOKLETS)


def test_kit_rows():
    import civil_defense_sources as k
    rows = k.booklet_rows(figure("Fig. 4 An inner refuge"[7:], "4"), 5, 0, "Protect and Survive", 1980, "booklet",
                          "UK Home Office", "credit")
    assert rows[0]["answer"] == "It is a drawing from a 1980 UK Home Office civil defence booklet, 'Protect and " \
                                "Survive'."
    assert rows[1]["answer"].endswith("figure 4, an inner refuge.")
    rows = k.booklet_rows(figure(), 5, 0, "Your Basement Fallout Shelter", 0, "pamphlet", "Canadian", "credit")
    assert len(rows) == 1 and rows[0]["answer"].startswith("It is a drawing from a Canadian civil defence pamphlet")
    assert k.marks_for("Protect and Survive: Casualties") == {"content": "graphic"}
