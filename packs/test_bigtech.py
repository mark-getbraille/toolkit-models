"""A self-test of the big-company parsers (packs/bigtech_packs.py and training-kit/kit/bigtech_sources.py), with
made-up records only: nothing is downloaded from the internet.

It checks that:
  - a Google Scanned Objects model is named from the first real line of its description (not "Test"), only a CC BY 4.0
    model is used, and every answer says the picture is computer-made, not a photo;
  - an Open Images Extended photo with a confirmed person or body-part label is left out, vague labels (colours,
    "Product") are not said, the giver's own tag comes first, "a" is put only before countable things, and "Is there
    ...?" is answered yes and no from confirmed and rejected labels;
  - a PubTabNet table is read row by row from its structure and cells (headings marked, blanks said, bullets said as a
    list), and tables that do not match, are too big or mostly blank are left out; an article is used only under
    CC BY or CC0 (never CC BY-NC), and is credited with its title and at most three authors;
  - the kit's ScreenQA answer is what most people wrote, or "That is not shown on this screen."; a PixMo transcript
    loses "um", repeated words and a leading "So", is refused when it names anything sexual or is short; stock-photo
    sites are refused; a PixMo count question is made only from a plain name of a thing; FinTabNet's file names give
    the company's stock symbol and year; and the kit reads a table exactly as the pack does.

Run it from the repository's folder:   python3 -m pytest packs/test_bigtech.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import bigtech_packs as b  # noqa: E402
import bigtech_sources as k  # noqa: E402

CC_BY = "Creative Commons Attribution 4.0 International"


# ----------------------------------------------------------------- Google Scanned Objects

def test_gso_name_and_rows():
    """The product's name comes from the description's first real line; other licences are refused."""
    model = {"name": "Weisshai_Great_White_Shark", "description": "Weisshai Great White Shark\nTest",
             "license_name": CC_BY, "categories": ["Toys"]}
    assert b.gso_name(model) == "Weisshai Great White Shark"
    assert b.gso_name({"name": "Some_Mug", "description": "Test"}) == "Some Mug"
    assert b.gso_name({"name": "Some_Mug", "description": ""}) == "Some Mug"
    row = b.gso_rows(model)
    assert row["question"] == "What is this?"
    assert row["answer"].startswith("This is a computer-made picture of a 3D scan of a real product, not a photo.")
    assert "The product is: Weisshai Great White Shark. It is a toy." in row["answer"]
    assert "CC BY 4.0" in row["credit"] and row["credit"].endswith("/Weisshai_Great_White_Shark")
    assert b.gso_rows(dict(model, license_name="Creative Commons Attribution-NonCommercial 4.0")) is None
    plain = b.gso_rows(dict(model, categories=["Consumer Goods"]))
    assert plain["answer"].endswith("The product is: Weisshai Great White Shark.")


# ----------------------------------------------------------------- Open Images Extended (crowdsourced)

NAMES = {"/m/1": "Pressure cooker", "/m/2": "Kitchen", "/m/3": "Product", "/m/4": "Human hand", "/m/5": "Glitter",
         "/m/6": "Slow cooker", "/m/7": "Pastel (Art)", "/m/8": "Taj Mahal", "/m/9": "Silver", "/m/10": "Woman"}


class FixedRandom:
    """A stand-in for random.Random whose choice() always takes the first item, so the rows are known."""

    def choice(self, items):
        """The first item."""
        return list(items)[0]


def test_oie_people_and_vague_labels():
    """A confirmed person or body part leaves the photo out; only vague labels leave it out too."""
    assert b.oie_rows({"/m/1": ("tag-verification", 1), "/m/4": ("verification", 1)}, NAMES, FixedRandom()) == []
    assert b.oie_rows({"/m/1": ("tag-verification", 1), "/m/10": ("verification", 1)}, NAMES, FixedRandom()) == []
    assert b.oie_rows({"/m/3": ("tag-verification", 1), "/m/9": ("verification", 1)}, NAMES, FixedRandom()) == []
    # A REJECTED person label does not leave the photo out.
    assert b.oie_rows({"/m/1": ("tag-verification", 1), "/m/10": ("verification", 0)}, NAMES, FixedRandom())


def test_oie_rows():
    """The giver's tag first, vague labels not said, yes and no questions only about countable things."""
    labels = {"/m/2": ("verification", 1), "/m/1": ("tag-verification", 1), "/m/3": ("verification", 1),
              "/m/5": ("verification", 1), "/m/6": ("verification", 0)}
    rows = b.oie_rows(labels, NAMES, FixedRandom())
    assert rows[0] == {"question": "What is in this picture?",
                       "answer": "In this photo: pressure cooker, glitter and kitchen."}
    assert rows[1] == {"question": "Is there a pressure cooker in this picture?",
                       "answer": "Yes, there is a pressure cooker in this picture."}
    assert rows[2] == {"question": "Is there a slow cooker in this picture?",
                       "answer": "No, I can't see a slow cooker in this picture."}


def test_oie_words():
    """Qualifiers are dropped, names keep their capitals, stuff and plurals get no "a"."""
    assert b.oie_said("Pastel (Art)") == "pastel"
    assert b.oie_said("Taj Mahal") == "Taj Mahal"
    assert b.oie_said("TV stand") == "TV stand"
    assert b.oie_countable("Pressure cooker")
    assert not b.oie_countable("Glitter")
    assert not b.oie_countable("Lighting")
    assert not b.oie_countable("Scissors")
    assert not b.oie_countable("Taj Mahal")
    rows = b.oie_rows({"/m/5": ("tag-verification", 1)}, NAMES, FixedRandom())
    assert rows == [{"question": "What is in this picture?", "answer": "In this photo: glitter."}]


# ----------------------------------------------------------------- PubTabNet and FinTabNet tables

def cell(text):
    """A made-up PubTabNet cell: its characters as tokens."""
    return {"tokens": list(text), "bbox": [0, 0, 1, 1]}


HTML = ["<thead>", "<tr>", "<td>", "</td>", "<td>", "</td>", "<td>", "</td>", "</tr>", "</thead>",
        "<tbody>", "<tr>", "<td>", "</td>", "<td>", "</td>", "<td>", "</td>", "</tr>",
        "<tr>", "<td", ' colspan="2"', ">", "</td>", "<td>", "</td>", "</tr>", "</tbody>"]
CELLS = [[cell("<b>Group</b>"), cell("Week 1"), cell("Week 2"), cell("A"), {"tokens": []}, cell("3.5"),
          cell("Total•All"), cell("7")]]


def test_ptn_grid():
    """Rows from the tokens: headings marked, the OTSL nesting undone, bold taken out, bullets said as a list."""
    grid = b.ptn_grid(HTML, CELLS)
    assert grid == [(True, ["Group", "Week 1", "Week 2"]), (False, ["A", "", "3.5"]), (False, ["Total, All", "7"])]
    assert b.ptn_grid(HTML, [CELLS[0][:-1]]) == []          # one cell short: the two do not match


def test_ptn_rows():
    """The table read out, and its size; too big or mostly blank tables are left out."""
    rows = b.ptn_rows(b.ptn_grid(HTML, CELLS), 3)
    assert rows[0]["question"] == "Read this table to me."
    assert rows[0]["answer"] == ("This table has 3 rows and 3 columns. Row 1 (headings): Group; Week 1; Week 2. "
                                 "Row 2: A; blank; 3.5. Row 3: Total, All; 7.")
    assert rows[1] == {"question": "How many rows and columns does this table have?",
                       "answer": "It has 3 rows and 3 columns; the first row holds the headings."}
    assert b.ptn_rows(b.ptn_grid(HTML, CELLS), 7) == []      # too many columns
    blank = [(False, ["x", "", ""]), (False, ["", "", ""])]
    assert b.ptn_rows(blank, 3) == []
    assert b.ptn_rows([(False, ["a", "b"])] * 16, 2) == []   # too many rows


def test_ptn_articles():
    """The PMC id from a file name, at most three authors, and only CC BY or CC0 articles."""
    assert b.ptn_pmcid("PMC5755158_010_01.png") == "PMC5755158"
    assert b.ptn_pmcid("page.png") == ""
    assert b.ptn_authors("Lu D, Tiezzi F, Schillebeeckx C, McNulty NP.") == "Lu D, Tiezzi F, Schillebeeckx C and others"
    assert b.ptn_authors("Lu D.") == "Lu D"

    class Answer:
        """A made-up Europe PMC answer."""

        def json(self):
            """Three articles: CC BY, CC BY-NC (refused) and CC0."""
            return {"resultList": {"result": [
                {"pmcid": "PMC1", "license": "cc by", "title": "A study.", "authorString": "A A, B B.",
                 "journalInfo": {"journal": {"title": "J One"}}, "pubYear": "2017"},
                {"pmcid": "PMC2", "license": "cc by-nc", "title": "B", "authorString": "C C."},
                {"pmcid": "PMC3", "license": "cc0", "title": "C", "authorString": "", "journalTitle": "J Three"}]}}

    class Session:
        """A made-up session that answers every request with Answer."""

        def get(self, *args, **kwargs):
            """The made-up answer."""
            return Answer()

    free = b.ptn_free_articles(Session(), ["PMC1", "PMC2", "PMC3"])
    assert sorted(free) == ["PMC1", "PMC3"]
    assert free["PMC1"] == {"licence": "CC BY", "title": "A study", "authors": "A A, B B", "journal": "J One",
                            "year": "2017"}
    assert free["PMC3"]["licence"] == "CC0" and free["PMC3"]["authors"] == "its authors"
    credit = b.PTN_CREDIT.format(pmcid="PMC1", **free["PMC1"])
    assert credit.startswith('Table from "A study" by A A, B B, J One (2017), CC BY, '
                             "https://europepmc.org/article/PMC/PMC1;")


def test_kit_reads_tables_as_the_pack():
    """The kit's FinTabNet reader gives the same rows as the pack's PubTabNet reader."""
    grid = k.table_grid(HTML, CELLS)
    assert grid == b.ptn_grid(HTML, CELLS)
    assert k.table_rows(grid, 3) == b.ptn_rows(grid, 3)
    assert k.fintab_report("DFS.2012.page_94.pdf_81952.png") == ("DFS", "2012")
    assert k.fintab_report("BRK.B.2015.page_5.pdf_1.png") == ("BRK.B", "2015")
    assert k.fintab_report("odd.png") == ("not given", "unknown")


# ----------------------------------------------------------------- ScreenQA and PixMo (the kit)

def test_screenqa_answer():
    """The answer most people wrote; "not shown" when most found none."""
    agree = [{"full_answer": "The rating is 4.6 stars."}, {"full_answer": "The rating is 4.6."},
             {"full_answer": "The rating is 4.6 stars."}]
    assert k.screenqa_answer(agree) == "The rating is 4.6 stars."
    none = [{"full_answer": "<no answer>"}, {"full_answer": "<no answer>"}, {"full_answer": "It is red."}]
    assert k.screenqa_answer(none) == k.NOT_SHOWN
    assert k.screenqa_answer([{"full_answer": "it is red"}, {"full_answer": "<no answer>"}]) == "It is red."
    assert k.screenqa_answer([]) == ""


SPOKEN = ("So this is a picture of a a kitchen, um, with a white fridge on the left. There's There's a wooden table "
          "in the middle with four chairs around it, uh, and a bowl of apples on it. The floor is grey tile and the "
          "walls are painted a pale yellow colour. Above the sink there is a window with blue curtains, and the light "
          "coming in is bright, so it looks like it is daytime.")


def test_spoken_text():
    """Fillers and repeated words out, the leading "So" dropped, a full stop at the end."""
    text = k.spoken_text(SPOKEN)
    assert text.startswith("This is a picture of a kitchen, with a white fridge on the left. There's a wooden table")
    assert " um" not in text and " uh" not in text and text.endswith(".")
    assert k.spoken_text("A short one.") == ""
    assert k.spoken_text(SPOKEN + " She is wearing lingerie.") == ""
    assert len(k.spoken_text(" ".join([SPOKEN] * 10)).split()) <= k.PIXMO_MOST_WORDS
    assert k.best_transcript(["Too short.", SPOKEN]) == text
    assert k.best_transcript([]) == ""


def test_pixmo_urls_and_names():
    """Stock-photo sites are refused; names are made from the address."""
    assert k.pixmo_url_ok("https://i.redd.it/abc.jpg")
    assert not k.pixmo_url_ok("https://image.shutterstock.com/x.jpg")
    assert not k.pixmo_url_ok("https://thumbs.dreamstime.com/x.jpg")
    assert not k.pixmo_url_ok("ftp://example.org/x.jpg")
    assert k.pixmo_name("pixmo-cap", "https://a/b.jpg") == k.pixmo_name("pixmo-cap", "https://a/b.jpg")
    assert k.pixmo_name("pixmo-cap", "https://a/b.jpg").startswith("pixmo-cap-")


def test_count_rows():
    """Plain names only; none, one and many said in words up to ten."""
    assert k.count_rows("Book", 21) == {"question": "How many books are there in this picture?",
                                        "answer": "There are 21 books."}
    assert k.count_rows("red vehicle", 9)["answer"] == "There are nine red vehicles."
    assert k.count_rows("Cup", 1)["answer"] == "There is one cup."
    assert k.count_rows("Person", 0)["answer"] == "There are no people in this picture."
    assert k.count_rows("Glasses", 2)["question"] == "How many glasses are there in this picture?"
    assert k.count_rows("Book on right bookshelf", 4) is None
    assert k.count_rows("Bird", 31) is None
    assert k.count_rows("Bikini", 2) is None


def test_child_mark():
    """A transcript that names a child marks its row."""
    assert k.with_child({"answer": "x"}, "A boy rides a bike.")["child"] is True
    assert "child" not in k.with_child({"answer": "x"}, "A red bike.")


def test_every_pack_has_a_limit():
    """Every open pack has a full-build limit, and every kit entry is research with terms."""
    assert set(b.BIGTECH_PACKS) == set(b.BIGTECH_LIMITS)
    assert all(s.group == "research" and s.terms and s.terms_summary for s in k.BIGTECH_SOURCES)
    assert k.BIGTECH_PICTURE_MAKING_OK <= {s.key for s in k.BIGTECH_SOURCES}
