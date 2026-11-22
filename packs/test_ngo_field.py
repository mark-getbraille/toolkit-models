"""A self-test of the non-profit and field-manual pack builders (packs/ngo_packs.py, packs/field_manual_packs.py)
and the kit's notes about non-profit collections (training-kit/kit/ngo_sources.py), with made-up records only:
nothing is downloaded from the internet.

It checks that:
  - an Our World in Data chart's rows say its kind, title, subtitle (links reduced to their words) and places, and
    its citation; unpublished charts and table-only charts are left out;
  - a field manual follows the release rule (military_release.py; a made-up PDF made with pypdfium2 when it is
    installed): an Internet Archive copy is kept with or without Distribution Statement A, with a truthful release
    line; a restricted marking leaves it out of this open pack unless a government site publishes that copy; a
    classified marking leaves it out unless declassified and released; a third-party copy still needs the
    statement;
  - figure captions are read, list-of-figures lines are not, unsafe captions are recognised, first-aid words make a
    row "medical", and the box of a drawing stops at body text and never reaches into its caption;
  - the kit's non-profit notes load, with no collection used for picture-making.

Run it from the repository's folder:   python3 -m pytest packs/test_ngo_field.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import ngo_packs as ngo  # noqa: E402
import field_manual_packs as fm  # noqa: E402


def test_owid_chart_rows():
    """A line chart's answer has its title, subtitle without link marks, and its places; the source row its
    citation."""
    config = {"title": "Life expectancy", "subtitle": "The [period life expectancy](#dod:life-expectancy) at birth.",
              "selectedEntityNames": ["World", "Africa", "Europe"], "isPublished": True}
    metadata = {"chart": {"citation": "UN WPP (2024)"}}
    rows, why = ngo.chart_rows("life-expectancy", config, metadata)
    assert why == "" and len(rows) == 2
    assert rows[0]["answer"] == ('This is a line chart from Our World in Data titled "Life expectancy". The period '
                                 'life expectancy at birth. It shows World, Africa and Europe.')
    assert rows[1]["question"] == ngo.SOURCE_Q and "UN WPP (2024)" in rows[1]["answer"]
    assert rows[0]["credit"] == "Our World in Data, CC BY 4.0, https://ourworldindata.org/grapher/life-expectancy"


def test_owid_kinds_and_left_out():
    """Maps, bar charts and the left-out charts."""
    assert ngo.chart_kind({"tab": "map", "hasMapTab": True}) == "world map"
    assert ngo.chart_kind({"chartTypes": ["DiscreteBar"]}) == "bar chart"
    assert ngo.chart_kind({}) == "line chart" and ngo.chart_kind({"tab": "table"}) == ""
    rows, _ = ngo.chart_rows("m", {"title": "Map", "tab": "map", "hasMapTab": True}, {})
    assert "Each country is coloured" in rows[0]["answer"] and len(rows) == 1
    assert ngo.chart_rows("x", {"title": "X", "isPublished": False}, {})[0] is None
    assert ngo.chart_rows("x", {"title": "X", "tab": "table"}, {})[0] is None
    assert ngo.place_list([str(i) for i in range(10)]).endswith("7 and 2 more")


def test_field_manual_words():
    """Captions, list lines, unsafe captions and medical words."""
    m = fm.CAPTION.match("Figure 8-12. Square knot")
    assert m and m.group(1) == "8-12" and m.group(2) == "Square knot"
    assert fm.CAPTION.match("Figure A-3. Bowline") and fm.CAPTION.match("Figure 2-1 Jaw Thrust Method")
    assert fm.CAPTION.match("Figure 1-4.\u2014Magnetic field around a conductor.").group(2).startswith("Magnetic")
    assert fm.SENTENCE.match("shows you a couple of people lifting") and not fm.SENTENCE.match("Square knot")
    assert fm.LIST_LINE.search("Figure 2-1. Jaw thrust method ............ 2-6")
    assert fm.NOT_SAFE.search("Firing positions") and fm.NOT_SAFE.search("Improvised weapons")
    assert not fm.NOT_SAFE.search("Lean-to shelter") and not fm.NOT_SAFE.search("Snare for small game")
    assert fm.MEDICAL.search("Applying a tourniquet") and not fm.MEDICAL.search("Clove hitch")
    assert fm.TOO_LITTLE.match("(continued)") and not fm.TOO_LITTLE.match("Square knot")
    assert fm.RESTRICTED.search("DISTRIBUTION STATEMENT B") and fm.DISTRIBUTION_A.search(
        "Approved for public release; distribution is unlimited")


def test_figure_box():
    """The drawing above a caption, stopping at the body text above it and at the caption; else the one below."""
    caption = (100, 300, 300, 310)                       # left, bottom, right, top (PDF points)
    shapes = [(120, 320, 400, 500), (130, 340, 200, 520), (100, 600, 500, 610), (110, 100, 300, 280)]
    lines = [(72, 560, 540, 570)]                        # a line of body text above the drawing
    box = fm.figure_box(caption, shapes, 740, 50, lines)
    assert box == (120, 320, 400, 520)                   # the shape above the body text is not taken
    below = fm.figure_box(caption, [(110, 100, 300, 301)], 740, 50, [])
    assert below == (110, 100, 300, 299)                 # cut at the caption's bottom
    assert fm.figure_box(caption, [], 740, 50, lines) is None


def test_distribution_check_on_a_made_up_pdf():
    """The release rule on made-up PDFs (only when pypdfium2 is installed): Distribution Statement A passes, a missing
    statement passes from the Internet Archive with a truthful line, a restricted marking passes only from a
    government site, classified never, and a third-party copy needs the statement."""
    try:
        import pypdfium2 as pdfium
        import pypdfium2.raw as pdfium_c
    except ImportError:
        return

    def pdf(words):
        """A one-page PDF with words on it."""
        doc = pdfium.PdfDocument.new()
        page = doc.new_page(612, 792)
        font = pdfium_c.FPDFText_LoadStandardFont(doc, b"Helvetica")
        text = pdfium_c.FPDFPageObj_CreateTextObj(doc, font, 12)
        import ctypes
        buf = (words + "\x00").encode("utf-16-le")
        pdfium_c.FPDFText_SetText(text, ctypes.cast(ctypes.c_char_p(buf), ctypes.POINTER(pdfium_c.FPDF_WCHAR)))
        pdfium_c.FPDFPageObj_Transform(text, 1, 0, 0, 1, 72, 700)
        pdfium_c.FPDFPage_InsertObject(page, text)
        pdfium_c.FPDFPage_GenerateContent(page)
        import io
        out = io.BytesIO()
        doc.save(out)
        return pdfium.PdfDocument(out.getvalue())
    ia = "https://archive.org/download/x/x.pdf"
    why, line = fm.distribution_ok(pdf("Approved for public release; distribution is unlimited."), ia)
    assert why == "" and line.startswith("Distribution Statement A")
    why, line = fm.distribution_ok(pdf("Survival manual."), ia)
    assert why == "" and "print no distribution statement" in line and "approved for public release" not in line
    why, line = fm.distribution_ok(pdf("DISTRIBUTION STATEMENT C: authorized to DOD only."), ia)
    assert "restricted" in why and "personal use only" in why and line == ""
    why, line = fm.distribution_ok(pdf("DISTRIBUTION STATEMENT C: authorized to DOD only."),
                                   "https://armypubs.army.mil/epubs/x.pdf")
    assert why == "" and "publishes it openly at https://armypubs.army.mil/epubs/x.pdf" in line
    assert "classified" in fm.distribution_ok(pdf("SECRET"), ia)[0]           # live marking, no release shown
    why, line = fm.distribution_ok(pdf("SECRET DECLASSIFIED by made-up authority"), ia)
    assert why == "" and "Originally classified SECRET; declassified" in line
    assert fm.distribution_ok(pdf("Survival manual."), "https://example.com/x.pdf")[0]
    assert fm.distribution_ok(pdf("Approved for public release; distribution is unlimited."),
                              "https://example.com/x.pdf")[0] == ""


def test_tables_and_kit_notes():
    """Every pack has a limit and a credit; the kit's non-profit notes load and use nothing for picture-making."""
    assert set(ngo.NGO_PACKS) == set(ngo.NGO_LIMITS) and set(fm.FIELD_MANUAL_PACKS) == set(fm.FIELD_MANUAL_LIMITS)
    assert all(credit for _, credit in list(ngo.NGO_PACKS.values()) + list(fm.FIELD_MANUAL_PACKS.values()))
    assert len({m[0] for m in fm.MANUALS}) == len(fm.MANUALS)
    import ngo_sources
    assert ngo_sources.NGO_SOURCES == [] and ngo_sources.NGO_PICTURE_MAKING_OK == ()
    assert ngo_sources.NGO_NOT_INCLUDED and ngo_sources.NGO_PERMISSION_CANDIDATES


def test_unsafe_pages_reads_pypdfium2_5_bookmarks():
    """unsafe_pages reads bookmarks the way pypdfium2 5 gives them (get_title, get_dest().get_index()) and the
    older way (title, page_index), so a weapons chapter is always skipped."""
    import field_manual_packs as fm

    class Dest:
        def __init__(self, i):
            self.i = i

        def get_index(self):
            return self.i

    class New:
        def __init__(self, t, i):
            self.t, self.i = t, i

        def get_title(self):
            return self.t

        def get_dest(self):
            return Dest(self.i)

    class Old:
        def __init__(self, t, i):
            self.title, self.page_index = t, i

    class Doc:
        def __init__(self, items):
            self.items = items

        def get_toc(self, max_depth=1):
            return iter(self.items)

        def __len__(self):
            return 30

    for kind in (New, Old):
        doc = Doc([kind("Chapter 1. Shelters", 0), kind("Chapter 2. Weapons", 10), kind("Chapter 3. Knots", 20)])
        assert fm.unsafe_pages(doc) == set(range(10, 20)), kind


def test_field_manual_release_rule_additions():
    """The manuals added under the release rule of 22 November 2026 are in the pack's list once each."""
    ids = [m[0] for m in fm.MANUALS]
    assert len(ids) == len(set(ids)) and all(m in fm.MANUALS for m in fm.MANUALS_RELEASE_RULE)
    assert ("milmanual-st-31-91b--us-army-special-forces-medical-handbook" in ids and
            dict((m[0], m[2]) for m in fm.MANUALS)["milmanual-st-31-91b--us-army-special-forces-medical-handbook"])
