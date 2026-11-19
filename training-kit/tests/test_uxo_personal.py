"""Tests of the personal-use UXO and small-arms recognition collections (kit/uxo_personal_sources.py), with made-up
text and made-up PDFs only: nothing is downloaded and no real manual is used.

It checks that:
  - only Distribution Statement A (or a stated open licence) is kept, in its usual and shifted-font forms, and that
    every restricted marking refuses a document, even beside Distribution A;
  - the section filter drops render-safe, disposal, demolition, fuze-functioning and charge sections (UXO) and
    firing, cycle-of-function, maintenance, modification and ammunition sections (small arms), records each dropped
    title, keeps "clearing" only inside the safety section, and leaves out a document that is mostly procedure;
  - figure captions are kept only from kept sections, with the safety line, and small-arms figures only when they
    show the weapon or its parts;
  - with pypdfium2 (and the field-manual figure finder) installed: a made-up manual is checked, cut down to its kept
    pages, its figure is cut, and the review workspace and the personal folder (README "personal use; not for
    redistribution") are made, with every picture "needs another look", content "graphic".

    xvfb-run -a python3.12 -m pytest -q training-kit/tests -p no:cacheprovider
"""

import ctypes
import io
import json
import os
import sys

import pytest

KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit")
if KIT not in sys.path:
    sys.path.insert(0, KIT)

import uxo_personal_sources as ux  # noqa: E402

A_LINE = "DISTRIBUTION RESTRICTION: Approved for public release; distribution is unlimited."


# ----------------------------------------------------------------- the release check

def test_distribution_a_kept_and_restricted_refused():
    """Distribution A in its usual forms is kept; B to F, FOUO, CUI, NOFORN and export control are refused, also
    beside Distribution A; a document saying nothing is refused."""
    for text in (A_LINE, "Approved for public release, distribution unlimited", "Distribution Unlimited; Approved "
                 "for Public Release", "DISTRIBUTION STATEMENT A: Approved for public release; distribution is "
                 "unlimited."):
        ok, line = ux.release_check("Field Manual " + text)
        assert ok, text
        assert "Distribution Statement A" in line
    for text in ("DISTRIBUTION STATEMENT B: Distribution authorized to U.S. Government agencies only.",
                 "DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government agencies and their "
                 "contractors.", "Distribution Statement D.", "DISTRIBUTION STATEMENT E", "Distribution F: further "
                 "dissemination only as directed", "FOR OFFICIAL USE ONLY", "CUI", "NOFORN",
                 "This document contains export-controlled technical data."):
        ok, why = ux.release_check(text)
        assert not ok and "restricted" in why, text
        ok, why = ux.release_check(A_LINE + " " + text)
        assert not ok and "restricted" in why, text
    ok, why = ux.release_check("To be distributed in accordance with DA Form 12-40.")
    assert not ok and "does not say" in why


def test_shifted_font_cover_is_read():
    """A cover printed in a font whose letters come out 29 places early is read (the 2024 ATP 4-32.2 does this)."""
    shifted = "".join(chr(ord(c) - 29) if "!" <= c <= "z" else c for c in
                      "DISTRIBUTION STATEMENT A Approvedforpublicrelease distributionisunlimited")
    assert ux.unshifted(shifted).startswith("DISTRIBUTION")
    assert ux.release_check("COVER " + shifted)[0]
    bad = "".join(chr(ord(c) - 29) if "!" <= c <= "z" else c for c in "DISTRIBUTION STATEMENT C: authorized")
    assert not ux.release_check(A_LINE + " " + bad)[0]


def test_licence_basis():
    """A humanitarian body's document is kept only when its stated open licence is printed in it."""
    licence = r"Creative Commons Attribution[- ]4\.0|CC BY 4\.0"
    assert ux.release_check("Published under CC BY 4.0 by a humanitarian body.", "licence", licence)[0]
    assert not ux.release_check("All rights reserved.", "licence", licence)[0]
    assert not ux.release_check("CC BY 4.0. For official use only.", "licence", licence)[0]


# ----------------------------------------------------------------- the section filter

def page(*lines):
    """A made-up page's text from its lines (with enough words to count as a page of text)."""
    return "\n".join(lines + ("This page has running text about the subject so that it counts as a page with "
                              "words on it for the share of pages that are left out.",))


def test_uxo_filter_drops_render_safe_and_disposal_sections():
    """Bookmarked render-safe and disposal sections are dropped and recorded; recognition, marking and reporting
    are kept; a printed demolition heading stays dropped to the end of its chapter."""
    pages = [page(A_LINE), page("Chapter 1 Recognizing UXO", "DROPPED ORDNANCE"), page("PROJECTED ORDNANCE"),
             page("THROWN ORDNANCE"), page("PLACED ORDNANCE"), page("SEA MINES"), page("SUBMUNITIONS"),
             page("Chapter 2 Render-Safe Procedures"), page("more about it"),                    # 7, 8
             page("Appendix A Disposal Techniques"), page("Appendix B Reporting UXO"),          # 9, 10
             page("Appendix C Marking and Protective Measures", "DEMOLITION PROCEDURES"),       # 11
             page("STEP ONE"), page("Appendix D Safe Distances")]                               # 12, 13
    marks = [(0, "Chapter 1 Recognizing UXO", 1), (0, "Chapter 2 Render-Safe Procedures", 7),
             (0, "Appendix A Disposal Techniques", 9), (0, "Appendix B Reporting UXO", 10),
             (0, "Appendix C Marking and Protective Measures", 11), (0, "Appendix D Safe Distances", 13)]
    result = ux.filter_pages(pages, marks, "uxo")
    assert result["leave_out"] == ""
    kept = set(result["kept"])
    assert {0, 1, 2, 3, 4, 5, 6, 10, 13} <= kept
    assert not {7, 8, 9, 11, 12} & kept
    assert "Chapter 2 Render-Safe Procedures" in result["dropped"]
    assert "Appendix A Disposal Techniques" in result["dropped"]
    assert result["dropped"]["DEMOLITION PROCEDURES"] == [12, 13]         # page numbers counted from 1
    assert "operational EOD procedure" in result["reasons"]["Chapter 2 Render-Safe Procedures"]
    for title in ("Fuze Functioning", "Charge Calculation", "Blow-in-Place", "Disarming the Mine",
                  "Manufacturing Improvised Explosive Devices", "Employment of Mines", "Defuzing"):
        assert ux.title_reason(title, "uxo"), title
    for title in ("Identifying UXO", "Projected Ordnance", "Reporting UXO", "Marking UXO", "Protective Measures",
                  "UXO Hazards", "Evacuation Distances"):
        assert ux.title_reason(title, "uxo") == "", title


def test_uxo_document_mostly_procedure_is_left_out():
    """A document whose pages are mostly render-safe and disposal procedure is left out entirely."""
    pages = [page(A_LINE), page("Chapter 1 Identifying UXO")] + [page("CHAPTER 2 RENDER SAFE PROCEDURES")] + \
        [page("STEP") for _ in range(6)]
    result = ux.filter_pages(pages, [], "uxo")
    assert "mostly operational EOD procedure" in result["leave_out"]


def test_body_text_full_of_procedure_words_is_dropped():
    """A page that is not under a dropped heading but uses procedure words many times is dropped."""
    pages = [page("Chapter 1 Recognizing UXO"), page("Use the blasting cap and detonating cord; render-safe the "
                                                     "fuze; then blow-in-place.")]
    result = ux.filter_pages(pages, [], "uxo")
    assert result["kept"] == [0] and any("procedure words" in t for t in result["dropped"])


def test_small_arms_filter():
    """Safety and description are kept; clearing is kept inside the safety section only; the cycle of function
    (and the smaller headings under it), marksmanship, maintenance, modification and ammunition are dropped; table
    fragments such as "TO FIRE" are not headings."""
    pages = [page(A_LINE),
             page("Chapter 1 Safety", "SAFE WEAPONS HANDLING", "RULES OF FIREARMS SAFETY", "TO FIRE"),
             page("CLEARING THE PISTOL"),
             page("Chapter 2 Description", "MAJOR COMPONENTS"), page("CYCLE OF FUNCTION"), page("FEEDING"),
             page("BOLT GROUP"),
             page("Chapter 3 Operation", "CLEARING THE PISTOL"), page("Chapter 4 Marksmanship"),
             page("Chapter 5 Maintenance", "DISASSEMBLY"), page("Chapter 6 Modifications and Conversions"),
             page("Appendix A Ammunition"), page("Appendix B Characteristics of the M9 Pistol")]
    result = ux.filter_pages(pages, [], "small_arms")
    kept = set(result["kept"])
    assert {0, 1, 2, 3, 12} <= kept
    assert not {4, 5, 6, 7, 8, 9, 10, 11} & kept
    assert result["dropped"]["CYCLE OF FUNCTION"] == [5, 6] and result["dropped"]["FEEDING"] == [6, 7]
    assert "clearing outside" in result["reasons"]["CLEARING THE PISTOL"]
    assert ux.heading_of("TO FIRE") is None and ux.heading_of("SAFE WEAPONS HANDLING") == (5, "SAFE WEAPONS "
                                                                                              "HANDLING")
    assert ux.heading_of("Chapter 2 provides the general characteristics, description, major components, and") \
        is None
    for title in ("Select-Fire Conversion", "Installing a Suppressor", "Trigger Replacement", "Reloading Ammunition",
                  "Zeroing", "Firing Positions", "Immediate Action", "Armorer Procedures", "Lubrication"):
        assert ux.title_reason(title, "small_arms"), title
    for title in ("Description", "Major Components", "Rules of Firearms Safety", "Flash Suppressor"):
        assert ux.title_reason(title, "small_arms") == "", title


def test_small_arms_manual_with_nothing_left_is_left_out():
    """A manual that is nearly all operation and maintenance is left out."""
    pages = [page("Chapter 1 Operating Instructions")] + [page("STEP") for _ in range(5)]
    assert ux.filter_pages(pages, [], "small_arms")["leave_out"]


# ----------------------------------------------------------------- captions

def test_captions_kept_only_from_kept_sections():
    """Captions on kept pages become answers with the safety line; captions on dropped pages, render-safe captions
    and small-arms captions that are not exterior views are not used."""
    doc = {"short": "FM 99-1 (made up)"}
    captions = {1: [("1-1", "Examples of Projected Ordnance"), ("1-2", "Render-safe procedure for a fuze")],
                3: [("2-1", "Rocket")]}
    used, left = ux.figure_rows(doc, [0, 1], captions, "uxo")
    assert [u[1] for u in used] == ["1-1"]
    assert used[0][3] == ("This is a figure from FM 99-1 (made up) (approved for public release): figure 1-1, "
                          "examples of projected ordnance. " + ux.UXO_LINE)
    reasons = {label: why for label, _c, why in left}
    assert "operational EOD procedure" in reasons["1-2"] and "left out" in reasons["2-1"]

    captions = {1: [("2-1", "M9 Pistol, Right Side"), ("2-2", "Prone firing position"), ("2-3", "Feeding"),
                    ("2-4", "Weapon safety status"), ("2-5", "Accuracy and consistency")]}
    used, left = ux.figure_rows({"short": "TC 9-9 (made up)"}, [1], captions, "small_arms")
    assert [u[1] for u in used] == ["2-1"]
    assert used[0][3].endswith("figure 2-1, M9 pistol, right side. " + ux.GUN_LINE)
    assert len(left) == 4


def test_tables_are_personal_review_only():
    """Both collections are personal, review-only, never published, never for picture-making, content "graphic";
    every document is checked for Distribution Statement A on the Internet Archive."""
    import sources
    assert {s["topic"] for s in ux.UXO_PERSONAL_SOURCES} == set(ux.TOPICS)
    for s in ux.UXO_PERSONAL_SOURCES:
        assert s["review_only"] and s["personal_only"] and s["never_publish"] and s["never_for_picture_making"]
        assert s["content"] == "graphic" and s["content"] in sources.PICTURE_MAKING_NEVER
        assert s["category"] == "research" and callable(s["fetch"])
    assert ux.UXO_PICTURE_MAKING_OK == set()
    for docs in ux.DOCUMENTS.values():
        for d in docs:
            assert d["basis"] == "statement" and d["page"].startswith("https://archive.org/details/")
    assert ux.PERSONAL_LINE == "PERSONAL USE; NOT FOR REDISTRIBUTION."
    assert ux.personal_folder("uxo").endswith(os.path.join("Picture Model Training personal files",
                                                           "UXO recognition"))


# ----------------------------------------------------------------- made-up PDFs (pypdfium2)

def made_up_pdf(pages):
    """PDF bytes from pages [(lines [(text, y)], rectangles [(left, bottom, width, height)])] (US Letter)."""
    pdfium = pytest.importorskip("pypdfium2")
    import pypdfium2.raw as raw
    doc = pdfium.PdfDocument.new()
    font = raw.FPDFText_LoadStandardFont(doc, b"Helvetica")
    for lines, rects in pages:
        pg = doc.new_page(612, 792)
        for text, y in lines:
            obj = raw.FPDFPageObj_CreateTextObj(doc, font, 11)
            buf = (text + "\x00").encode("utf-16-le")
            raw.FPDFText_SetText(obj, ctypes.cast(ctypes.c_char_p(buf), ctypes.POINTER(raw.FPDF_WCHAR)))
            raw.FPDFPageObj_Transform(obj, 1, 0, 0, 1, 72, y)
            raw.FPDFPage_InsertObject(pg, obj)
        for left, bottom, width, height in rects:
            rect = raw.FPDFPageObj_CreateNewRect(left, bottom, width, height)
            raw.FPDFPageObj_SetStrokeColor(rect, 0, 0, 0, 255)
            raw.FPDFPath_SetDrawMode(rect, 0, True)
            raw.FPDFPage_InsertObject(pg, rect)
        raw.FPDFPage_GenerateContent(pg)
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


BODY = [("This made-up page has running text so that it counts as a page of words for the filter.", 120)]


def made_up_manual(statement=A_LINE):
    """A made-up four-page UXO manual: cover, a recognition chapter with a figure, a render-safe chapter with a
    figure, and a reporting appendix."""
    return made_up_pdf([
        ([("FM 99-1 (made up) Unexploded Ordnance", 700), (statement, 660)] + BODY, []),
        ([("Chapter 1 Recognizing UXO", 700), ("Figure 1-1. Examples of projected ordnance", 380)] + BODY,
         [(150, 400, 250, 200)]),
        ([("Chapter 2 Render-Safe Procedures", 700), ("Figure 2-1. Rocket", 380)] + BODY, [(150, 400, 250, 200)]),
        ([("Appendix A Reporting UXO", 700)] + BODY, []),
    ])


def test_made_up_pdf_distribution_check():
    """A made-up PDF with Distribution A passes; one with Distribution C is refused."""
    doc = {"id": "fm-99-1", "short": "FM 99-1 (made up)", "title": "Made-up UXO manual", "year": 2026}
    assert ux.process_document(doc, made_up_manual(), "uxo")["ok"]
    refused = ux.process_document(doc, made_up_manual("DISTRIBUTION STATEMENT C: authorized to DoD only."), "uxo")
    assert not refused["ok"] and "restricted" in refused["reason"]


def test_made_up_pdf_end_to_end(tmp_path):
    """The made-up manual is filtered (the render-safe chapter dropped and recorded), saved with only its kept
    pages under a README that says personal use; its recognition figure goes to the review workspace as "needs
    another look", content "graphic"; the render-safe figure does not."""
    fm = ux.figure_tools()
    if fm is None:
        pytest.skip("packs/field_manual_packs.py is not here")
    import pypdfium2 as pdfium
    doc = ux.archive_doc("fm-99-1", "FM 99-1 (made up)", "Made-up UXO manual", "Nobody", 2026, "uxo")
    data = made_up_manual()
    result = ux.process_document(doc, data, "uxo", fm)
    assert result["ok"] and list(result["filter"]["dropped"]) == ["Chapter 2 Render-Safe Procedures"]
    assert len(pdfium.PdfDocument(result["pdf"])) == 3          # the cover, chapter 1 and the reporting appendix
    assert [f[3] for f in result["figures"]] == ["1-1"]

    old = ux.DOCUMENTS["uxo"]
    ux.DOCUMENTS["uxo"] = [doc]
    try:
        summary = ux.fetch_topic("uxo", str(tmp_path / "ws"), 10, documents_base=str(tmp_path / "Docs"),
                                 download=lambda d: (data, d["page"]), fm=fm)
    finally:
        ux.DOCUMENTS["uxo"] = old
    folder = tmp_path / "Docs" / "UXO recognition"
    readme = (folder / "README.txt").read_text(encoding="utf-8")
    assert readme.startswith(ux.PERSONAL_LINE) and "Chapter 2 Render-Safe Procedures" in readme
    assert (folder / "Made-up UXO manual (2026) (recognition and safety pages only).pdf").is_file()
    data = json.loads((tmp_path / "ws" / "describing.json").read_text(encoding="utf-8"))
    assert data["review_only"] and data["personal_only"] and data["never_publish"]
    assert data["never_for_picture_making"] and data["content"] == "graphic"
    entries = list(data["pictures"].values())
    assert len(entries) == 1 and entries[0]["status"] == "needs another look" and entries[0]["content"] == "graphic"
    text = (tmp_path / "ws" / (os.path.splitext(next(iter(data["pictures"])))[0] + ".txt")).read_text("utf-8")
    assert "figure 1-1, examples of projected ordnance" in text and ux.UXO_LINE in text
    assert "1 new figures added for review" in summary
