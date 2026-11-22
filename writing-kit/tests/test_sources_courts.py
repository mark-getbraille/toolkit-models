"""Tests of the court opinions source (kit/sources_courts.py) and its full-corpus command (kit/build_court_opinions.py).
Every court, case, opinion and bulk file here is made up; no network is used."""

import bz2
import gzip
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import build_court_opinions as bco  # noqa: E402
import build_dataset  # noqa: E402
import sources_courts as sc  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402


def q(value):
    """One value as PostgreSQL's COPY writes it (FORCE_QUOTE, backslash before a quote or backslash); None is NULL."""
    if value is None:
        return ""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def csv_bz2(path, head, rows):
    """A made-up bulk CSV file, bzip2-compressed."""
    lines = [",".join(head)] + [",".join(q(r.get(h)) for h in head) for r in rows]
    with bz2.open(path, "wt", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines) + "\n")


OPINION_HEAD = ["id", "type", "author_str", "per_curiam", "plain_text", "html", "html_with_citations", "xml_harvard",
                "cluster_id"]
OPINIONS = [
    {"id": 1, "type": "020lead", "author_str": "Judge Made-Up", "per_curiam": "f", "cluster_id": 10,
     "plain_text": "The made-up judgment is affirmed. The tenant said \"no\" and paid 100 dollars.\nSo ordered."},
    {"id": 2, "type": "040dissent", "author_str": "Judge Other", "per_curiam": "f", "cluster_id": 10,
     "html": "<p>I respectfully dissent.</p><p>The record shows SSN 123-45-6789 and card 4111 1111 1111 1111.</p>"},
    {"id": 3, "type": "010combined", "author_str": None, "per_curiam": "t", "cluster_id": 20,
     "xml_harvard": "<opinion><p>Per curiam. The made-up appeal is dismissed &amp; costs are taxed.</p></opinion>"},
    {"id": 4, "type": "030concurrence", "author_str": "Judge Third", "per_curiam": "f", "cluster_id": 10,
     "plain_text": "I concur in the made-up judgment, for a different reason."},
    {"id": 5, "type": "020lead", "author_str": "", "per_curiam": "f", "cluster_id": 30, "plain_text": "   "},
    {"id": 6, "type": "070rehearing", "author_str": "Judge Fourth", "per_curiam": "f", "cluster_id": 30,
     "plain_text": "Rehearing denied in this made-up state case."},
]


def made_up_export(folder, date="2030-03-31"):
    """The five made-up bulk files of one export in folder/<date>/; returns {table: path}."""
    base = os.path.join(folder, date)
    os.makedirs(base, exist_ok=True)
    paths = {t: os.path.join(base, f"{t}-{date}.csv.bz2") for t in sc.TABLES}
    csv_bz2(paths["courts"], ["id", "full_name", "short_name", "jurisdiction"],
            [{"id": "scotus", "full_name": "Supreme Court of the United States", "short_name": "Supreme Court",
              "jurisdiction": "F"}, {"id": "madeup", "full_name": "Supreme Court of Made-Up State",
                                     "short_name": "Made-Up", "jurisdiction": "S"}])
    csv_bz2(paths["dockets"], ["id", "court_id", "docket_number", "case_name"],
            [{"id": 100, "court_id": "scotus", "docket_number": "99-1", "case_name": "Doe v. Town"},
             {"id": 200, "court_id": "madeup", "docket_number": "A-7", "case_name": "Roe v. Shop"},
             {"id": 300, "court_id": "madeup", "docket_number": "B-8", "case_name": "Poe v. City"}])
    csv_bz2(paths["opinion-clusters"], ["id", "docket_id", "date_filed", "case_name", "precedential_status"],
            [{"id": 10, "docket_id": 100, "date_filed": "1954-05-17", "case_name": "Doe v. Made-Up Town",
              "precedential_status": "Published"},
             {"id": 20, "docket_id": 200, "date_filed": "1899-01-02", "case_name": "Roe v. Shop",
              "precedential_status": "Published"},
             {"id": 30, "docket_id": 300, "date_filed": "2021-07-08", "case_name": "Poe v. City",
              "precedential_status": "Unpublished"}])
    csv_bz2(paths["citations"], ["id", "volume", "reporter", "page", "type", "cluster_id"],
            [{"id": 1, "volume": "999", "reporter": "U.S.", "page": "1", "type": 1, "cluster_id": 10}])
    csv_bz2(paths["opinions"], OPINION_HEAD, OPINIONS)
    return paths


# ====================================================================== the source and the rules

def test_source_styles_and_not_used_are_registered():
    source = writing_sources.by_key()[sc.SOURCE_KEY]
    assert source.licence_class == writing_sources.OPEN and "Public Domain Mark" in source.licence
    assert sc.SOURCE_KEY in build_dataset.OPT_IN
    for style in sc.STYLES:
        assert style in styles.STYLES and style in styles.FORMAL_STYLES
    names = " ".join(name for name, _ in writing_sources.NOT_USED)
    assert "CourtListener's website" in names and "Caselaw Access Project" in names and "COLD Cases" in names


def test_styles_come_from_the_data_types():
    assert sc.style_for("020lead") == ("court_opinion_majority", "type 020lead")
    assert sc.style_for("015unamimous")[0] == "court_opinion_majority"
    assert sc.style_for("035concurrenceinpart")[0] == "court_opinion_concurrence"
    assert sc.style_for("040dissent")[0] == "court_opinion_dissent"
    assert sc.style_for("010combined")[0] == "court_opinion_combined"
    assert sc.style_for("010combined", per_curiam=True)[0] == "court_opinion_majority"
    assert sc.style_for("060remittitur")[0] == "court_opinion_other" and sc.style_for("")[0] == "court_opinion_other"


def test_bucket_listing_picks_the_newest_complete_export():
    def item(name, size):
        return f"<Contents><Key>bulk-data/{name}</Key><LastModified>x</LastModified><Size>{size}</Size></Contents>"
    page = "".join(item(f"{t}-2030-03-31.csv.bz2", 1000 + i) for i, t in enumerate(sc.TABLES))
    page += "".join(item(f"{t}-2030-06-30.csv.bz2", 5000) for t in sc.TABLES[:3])          # half-finished
    page += item("people-db-people-2030-06-30.csv.bz2", 9) + item("opinions-2030-06-30.csv.bz2", 14)
    files = sc.bucket_files([page])
    date, chosen = sc.latest_complete(files)
    assert date == "2030-03-31" and [f["table"] for f in chosen] == list(sc.TABLES)
    assert chosen[-1]["url"] == f"{sc.BUCKET}/bulk-data/opinions-2030-03-31.csv.bz2" and chosen[0]["size"] == 1000
    assert sc.parse_filter(" scotus, CA9 ,") == {"scotus", "ca9"} and sc.parse_filter("") == set()


def test_csv_rows_read_copy_escapes(tmp_path):
    path = tmp_path / "o.csv.bz2"
    csv_bz2(path, OPINION_HEAD, OPINIONS[:2])
    with open(path, "rb") as f:
        rows = list(sc.csv_rows(f))
    assert rows[0]["plain_text"].startswith('The made-up judgment is affirmed. The tenant said "no"')
    assert "\nSo ordered." in rows[0]["plain_text"] and rows[0]["author_str"] == "Judge Made-Up"
    assert rows[1]["plain_text"] == "" and rows[1]["html"].startswith("<p>I respectfully dissent.")


def test_text_from_html_and_xml():
    text, field = sc.opinion_text({"html": "<p>One.</p><p>Two &amp; three.</p>"})
    assert (text, field) == ("One.\n\nTwo & three.", "html")
    assert sc.opinion_text({"plain_text": "  ", "xml_harvard": "<opinion><p>Made up.</p></opinion>"})[1] == \
        "xml_harvard"
    assert sc.opinion_text({"plain_text": "   "}) == ("", "")


def test_record_instruction_and_fields():
    info = {"court": "scotus", "court_name": "Supreme Court of the United States", "court_type": "F",
            "case_name": "Doe v. Made-Up Town", "date_filed": "1954-05-17", "docket_number": "99-1",
            "citation": "999 U.S. 1", "precedential_status": "Published"}
    record = sc.opinion_record(OPINIONS[1], info)
    assert record["style_label"] == "court_opinion_dissent"
    assert record["instruction"] == ("Write a dissenting opinion of the Supreme Court of the United States in Doe v. "
                                     "Made-Up Town (999 U.S. 1), decided 17 May 1954, written by Judge Other (docket "
                                     "number 99-1). Write it in the formal style of an American judicial opinion.")
    extra = record["extra"]
    assert extra["court_type"] == "federal court of appeals" and extra["decade"] == "1950s" and extra["year"] == 1954
    assert extra["text_from"] == "html" and extra["opinion_type"] == "040dissent"
    assert sc.opinion_record(OPINIONS[4], info) is None
    plain = sc.opinion_record(OPINIONS[2], {})
    assert "issued per curiam" in plain["instruction"] and "an American court" in plain["instruction"]


def test_identity_numbers_are_masked_under_both_settings():
    source = writing_sources.by_key()[sc.SOURCE_KEY]
    record = sc.opinion_record(OPINIONS[1], {"court": "madeup"})
    for privacy in (build_dataset.OWNER, build_dataset.STRICT):
        row = build_dataset.examples_from_record(record, source, privacy)[0][0]
        assert "123-45-6789" not in row["response"] and "4111 1111 1111 1111" not in row["response"]
        assert "respectfully dissent" in row["response"]


# ====================================================================== the database and the build

def test_index_joins_cases_to_courts(tmp_path):
    paths = made_up_export(str(tmp_path / "court_opinions"))
    index = bco.Index(str(tmp_path / "index.sqlite"))
    assert not index.finished()
    index.make(paths, say=lambda text: None)
    assert index.finished()
    case = index.case("10")
    assert case == {"date_filed": "1954-05-17", "case_name": "Doe v. Made-Up Town", "precedential_status": "Published",
                    "court": "scotus", "docket_number": "99-1", "court_name": "Supreme Court of the United States",
                    "court_type": "F", "citation": "999 U.S. 1"}
    assert index.case("999") == {} and index.case("not a number") == {}
    index.make(paths, say=lambda text: (_ for _ in ()).throw(AssertionError("made twice")))


def lines(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(x) for x in f]


def all_rows(base):
    out = []
    for root, _dirs, files in os.walk(base):
        for name in files:
            if name.endswith(".jsonl.gz"):
                out += lines(os.path.join(root, name))
    return sorted(out, key=lambda r: r["opinion_id"])


def test_build_writes_by_court_and_year_and_filters(tmp_path):
    paths = made_up_export(str(tmp_path / "court_opinions"))
    index = bco.Index(str(tmp_path / "index.sqlite"))
    index.make(paths, say=lambda text: None)
    out = str(tmp_path / "out")
    counts = bco.build(paths["opinions"], index, out, say=lambda text: None)
    assert counts["opinions"] == 5 and counts["no text"] == 1 and counts["examples"] == 5
    base = os.path.join(out, "court_opinions")
    rows = all_rows(base)
    assert [r["style"] for r in rows] == ["court_opinion_majority", "court_opinion_dissent", "court_opinion_majority",
                                          "court_opinion_concurrence", "court_opinion_other"]
    assert rows[0]["court"] == "scotus" and rows[0]["citation"] == "999 U.S. 1" and rows[0]["register"] == "formal"
    assert os.path.isdir(os.path.join(base, "scotus", "1950s", "1954"))
    assert os.path.isdir(os.path.join(base, "madeup", "1890s", "1899"))
    again = bco.build(paths["opinions"], index, out, say=lambda text: None)       # built before: read back
    assert again["examples"] == 5
    chosen = bco.build(paths["opinions"], index, str(tmp_path / "out2"), courts={"madeup"}, years="2000-",
                       say=lambda text: None)
    assert chosen["examples"] == 1 and chosen["not one of the chosen courts"] == 3
    assert chosen["not one of the chosen years"] == 1


def test_build_resumes_after_a_stop(tmp_path, monkeypatch):
    paths = made_up_export(str(tmp_path / "court_opinions"))
    index = bco.Index(str(tmp_path / "index.sqlite"))
    index.make(paths, say=lambda text: None)
    clean = str(tmp_path / "clean")
    bco.build(paths["opinions"], index, clean, checkpoint=2, say=lambda text: None)
    real = sc.opinion_record
    calls = {"n": 0}

    def stops_at_the_fifth(row, info):
        calls["n"] += 1
        if calls["n"] == 5:
            raise KeyboardInterrupt("the window was closed")
        return real(row, info)
    monkeypatch.setattr(sc, "opinion_record", stops_at_the_fifth)
    out = str(tmp_path / "out")
    with pytest.raises(KeyboardInterrupt):
        bco.build(paths["opinions"], index, out, checkpoint=2, say=lambda text: None)
    progress = json.load(open(os.path.join(out, "court_opinions", "PROGRESS.json")))
    assert progress["rows"] == 4
    monkeypatch.setattr(sc, "opinion_record", real)
    said = []
    bco.build(paths["opinions"], index, out, checkpoint=2, say=said.append)
    assert any("Carrying on after 4 opinions" in s for s in said)
    assert [r["id"] for r in all_rows(os.path.join(out, "court_opinions"))] == \
        [r["id"] for r in all_rows(os.path.join(clean, "court_opinions"))]


def test_writer_closes_old_files_and_adds_to_them(tmp_path, monkeypatch):
    monkeypatch.setattr(bco, "OPEN_FILES", 2)
    w = bco.Writer(str(tmp_path))
    for i in range(3):
        w.write(f"c{i}/x.jsonl.gz", '{"n": %d}\n' % i)
    w.write("c0/x.jsonl.gz", '{"n": 9}\n')                # opened again for adding
    w.close()
    assert [r["n"] for r in lines(tmp_path / "c0" / "x.jsonl.gz")] == [0, 9]
    sizes = w.sizes()
    with gzip.open(tmp_path / "c1" / "x.jsonl.gz", "at") as f:
        f.write('{"n": 5}\n')
    os.makedirs(tmp_path / "c5")
    with gzip.open(tmp_path / "c5" / "x.jsonl.gz", "wt") as f:
        f.write('{"n": 6}\n')
    bco.restore(str(tmp_path), sizes)
    assert [r["n"] for r in lines(tmp_path / "c1" / "x.jsonl.gz")] == [1]
    assert not os.path.exists(tmp_path / "c5" / "x.jsonl.gz")


def test_build_only_command_and_summary(tmp_path, monkeypatch):
    folder = str(tmp_path / "court_opinions")
    made_up_export(folder)
    out = str(tmp_path / "out")
    assert bco.main(["--build-only", "--folder", folder, "--out", out, "--styles", "court_opinion_dissent"]) == 0
    base = os.path.join(out, "court_opinions")
    assert [r["style"] for r in all_rows(base)] == ["court_opinion_dissent"]
    report = open(os.path.join(base, "COURT-OPINIONS-REPORT.txt"), encoding="utf-8").read()
    assert "court_opinion_dissent: 1" in report and "scotus: 1" in report
    assert "Public Domain Mark" in open(os.path.join(base, "ATTRIBUTION.txt"), encoding="utf-8").read()
    assert bco.main(["--build-only", "--folder", str(tmp_path / "none"), "--out", out]) == 1


def test_sample_reads_the_local_files(tmp_path):
    folder = str(tmp_path / "court_opinions")
    paths = made_up_export(folder)
    bco.Index(os.path.join(os.path.dirname(paths["opinions"]), "index.sqlite")).make(paths, say=lambda text: None)
    records = list(sc.read_court_opinions(None, say=lambda text: None, court_folder=folder, sample_rows=3))
    assert len(records) == 3 and records[0]["extra"]["court"] == "scotus"
    assert "Doe v. Made-Up Town" in records[0]["instruction"]
