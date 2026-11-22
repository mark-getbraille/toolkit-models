"""Tests of the historical newspaper source (kit/sources_newspapers.py), its full-corpus command
(kit/build_newspapers.py) and the resumable download (fetch.Fetcher.download). Every newspaper, article, year file
and file list here is made up; no network is used (a fake "site" answers the requests)."""

import gzip
import hashlib
import io
import json
import os
import sys
import tarfile
import urllib.error

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import build_dataset  # noqa: E402
import build_newspapers  # noqa: E402
import fetch  # noqa: E402
import sources_newspapers as sn  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402


@pytest.fixture(autouse=True)
def short_waits(monkeypatch):
    """The tests do not need the real 3-second wait between requests."""
    monkeypatch.setattr(fetch, "DEFAULT_DELAY", 0.0)


# ====================================================================== made-up year files

NEWS = ("The new bridge over Willow Creek was opened on Tuesday afternoon before a large crowd of citizens. The\n"
        "mayor spoke briefly and the band played several airs while the first wagons crossed the river.")
EDITORIAL = ("It seems to us that the council has acted in haste. We believe that the people of this town deserve a\n"
             "fuller account of the money spent upon the new road, and we shall say so again.")
AD = ("Just received at our store a fine assortment of dry goods, boots and shoes. Prices reduced. Calico 8 cents\n"
      "per yard. Call at the corner of Main and Elm streets.")
LETTER = ("Mr. Editor: Allow me a few lines in your valuable paper to speak of the condition of the roads in the\n"
          "north end of the county, which are a disgrace to us all. Yours truly, A Farmer.")
NOTICE = ("Notice is hereby given that the undersigned has been appointed administrator of the estate of Silas\n"
          "Brindle, deceased, late of Hollow County. All persons having claims will present them.")
SERIAL = ("CHAPTER IV. The rain had not stopped for three days when Martha at last opened the old trunk in the\n"
          "attic and found the letters her father had hidden there. (To be continued.)")
POEM = ("The autumn leaves are falling fast\nUpon the quiet hill,\nThe summer days are gone at last\nAnd all the "
        "woods are still.\nO let us gather round the fire\nAnd sing the songs of old,\nUntil the evening stars "
        "retire\nAnd morning turns to gold.")
JUNK = "Tbe 1t wns AbriI3 tbs7wki@ nnd tlie qx zzv rrn ccx"


def scan(regions, articles, title="The Riverbend gazette. [volume] (Riverbend, Ohio) 1850-1890", state="Ohio"):
    """One made-up scan JSON (as American Stories gives it)."""
    return {"lccn": {"title": title, "state": state, "lccn": "sn00000001"}, "page_number": 1,
            "bboxes": regions, "full articles": articles, "edition": {"date": "1865-04-03"}}


def article(n, text, headline="", byline="", ids=None):
    return {"full_article_id": n, "headline": headline, "byline": byline, "article": text,
            "object_ids": ids if ids is not None else [n]}


def year_file(year=1865, scans=None):
    """A made-up faro_<year>.tar.gz (bytes) with the given {member name: scan dict}."""
    if scans is None:
        regions = [{"id": i, "class": "article", "legibility": "Legible"} for i in range(9)]
        regions[7]["legibility"] = "Questionable"
        regions[8]["legibility"] = "Illegible"
        scans = {f"{year}-04-03_p2_sn00000001_00000000001_{year}040301_0007.json": scan(regions, [
            article(0, NEWS, "BRIDGE OPENED\n\nA Great Day for Willow Creek", "By Our Reporter"),
            article(1, EDITORIAL, "THE COUNCIL AND THE ROAD"),
            article(2, AD, "NEW GOODS"),
            article(3, LETTER, "COMMUNICATED"),
            article(4, NOTICE, "ADMINISTRATOR'S NOTICE"),
            article(5, SERIAL, "THE HIDDEN LETTERS"),
            article(6, POEM, ""),
            article(7, JUNK, "", ids=[7, 8]),
            article(8, "   ", "EMPTY"),
        ])}
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        folder = tarfile.TarInfo(f"faro_{year}")
        folder.type = tarfile.DIRTYPE
        tar.addfile(folder)
        for name, data in scans.items():
            raw = json.dumps(data).encode("utf-8")
            info = tarfile.TarInfo(f"faro_{year}/{name}")
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    return buf.getvalue()


def records(year=1865):
    return list(sn.records_from_stream(io.BytesIO(year_file(year))))


# ====================================================================== the source, the styles and the rules

def test_source_styles_and_not_used_are_registered():
    source = writing_sources.by_key()[sn.SOURCE_KEY]
    assert source.licence == "CC BY 4.0" and source.licence_class == writing_sources.OPEN
    assert "Melissa Dell" in source.credit and "2308.12477" in source.notes
    assert sn.SOURCE_KEY in build_dataset.OPT_IN                       # not in the ordinary build
    for style in sn.STYLES:
        assert style in styles.STYLES
    assert any("Chronicling America bulk OCR" in name for name, _ in writing_sources.NOT_USED)


def test_each_style_rule():
    assert sn.classify("BRIDGE OPENED", NEWS) == ("newspaper_news_historical", "default (news)")
    assert sn.classify("THE COUNCIL", EDITORIAL)[0] == "newspaper_editorial_historical"
    assert sn.classify("Editorial Notes", NEWS)[0] == "newspaper_editorial_historical"
    assert sn.classify("NEW GOODS", AD)[0] == "newspaper_ad_historical"
    assert sn.classify("FOR SALE", "A good farm horse, $40. Inquire of the owner.")[0] == "newspaper_ad_historical"
    assert sn.classify("", LETTER)[0] == "newspaper_letter_historical"
    assert sn.classify("To the Editor", NEWS)[0] == "newspaper_letter_historical"
    assert sn.classify("", NOTICE)[0] == "newspaper_notice_historical"
    assert sn.classify("SHERIFF'S SALE", NEWS)[0] == "newspaper_notice_historical"
    assert sn.classify("", SERIAL) == ("newspaper_fiction_poetry_historical", "serial story words")
    assert sn.classify("", POEM) == ("newspaper_fiction_poetry_historical", "poem")
    assert sn.classify("Lines Written in Spring", NEWS)[0] == "newspaper_fiction_poetry_historical"


def test_prose_in_narrow_columns_is_not_a_poem_and_capitalised_ads_are_not_poems():
    prose = ("the meeting was held at the\nschool house on friday last and\nwas well attended by the people\n"
             "of the district who came from\nfar and near to hear the speakers\nand to take part in the business")
    assert not sn.looks_like_poem(prose)
    ad_lines = "Our New Stock\nOf Goods Has Arrived\nCalico 8 cents per yard\nShoes $1.50\nCall At\nThe Corner Store"
    assert sn.classify("", ad_lines)[0] == "newspaper_ad_historical"


def test_ocr_quality_scores_but_never_drops():
    assert sn.ocr_quality(NEWS) > 0.9
    assert sn.ocr_quality(JUNK) < 0.3
    assert sn.ocr_quality("Silas Brindle of Hollow") == 1.0           # names count neither way
    assert sn.ocr_quality("") == 0.0
    recs = records()
    junk = [r for r in recs if r["extra"]["article_id"].startswith("7_")]
    assert junk and junk[0]["extra"]["ocr_quality"] < 0.3              # kept, with its score
    assert len(recs) == 8                                              # every article with text; only the empty one


def test_legibility_from_the_regions():
    recs = {r["extra"]["article_id"].split("_")[0]: r for r in records()}
    assert recs["0"]["extra"]["legibility"] == 1.0
    assert recs["7"]["extra"]["legibility"] == 0.25                   # Questionable (0.5) and Illegible (0)
    assert sn.legibility({"object_ids": [1]}, {1: {"class": "article"}}) is None


def test_scan_names_newspaper_names_and_dates():
    info = sn.scan_info("faro_1910/1910-07-16_p7_sn00000002_00000000009_1910071601_0677.json")
    assert info["date"] == "1910-07-16" and info["page"] == "7" and info["lccn"] == "sn00000002"
    assert info["edition"] == "01" and info["seq"] == "0677"
    assert sn.scan_info("1955-11-23_pna_sn00000003_0000000000A_1955112301_0672.json")["page"] == ""
    assert sn.newspaper_name("The Riverbend gazette. [volume] (Riverbend, Ohio) 1850-1890") == \
        "The Riverbend gazette (Riverbend, Ohio)"
    assert sn.date_words("1865-04-03") == "3 April 1865"


def test_record_text_is_as_printed_with_columns_joined_and_poem_lines_kept():
    recs = {r["extra"]["article_id"].split("_")[0]: r for r in records()}
    news = recs["0"]
    assert news["response"] == " ".join(NEWS.split())                  # same words, same order
    assert "BRIDGE OPENED / A Great Day for Willow Creek" in news["instruction"]
    assert "By Our Reporter" in news["instruction"] and "3 April 1865" in news["instruction"]
    assert "1860s" in news["instruction"] and "The Riverbend gazette (Riverbend, Ohio)" in news["instruction"]
    poem = recs["6"]
    assert poem["response"] == POEM and poem["instruction"].startswith("Write a poem")
    assert recs["7"]["response"] == JUNK                                # OCR mistakes never corrected


def test_rows_are_never_scrubbed():
    """The owner's decision: this source's text stays exactly as printed, under either privacy setting."""
    text = "Account No. 4417-2290-1135 and 123-45-6789 were read aloud; the password: tulip9 was printed."
    art = {"article_id": "1_x", "year": 1901, "decade": "1900s", "date": "1901-02-03", "page": "1",
           "edition": "01", "lccn": "sn00000001", "newspaper_title": "The Test", "newspaper": "The Test",
           "state": "Ohio", "headline": "", "byline": "", "text": text, "legibility": None}
    record = sn.article_record(art)
    assert record["unchanged"] is True and sn.SOURCE_UNCHANGED
    source = writing_sources.by_key()[sn.SOURCE_KEY]
    for privacy in (build_dataset.OWNER, build_dataset.STRICT):
        row = build_dataset.examples_from_record(record, source, privacy)[0][0]
        assert row["response"] == text


def test_row_format():
    source = writing_sources.by_key()[sn.SOURCE_KEY]
    record = records()[1]
    row = build_dataset.examples_from_record(record, source)[0][0]
    row["style"], row["register"] = styles.label(row, source.key, record)
    assert row["style"] == "newspaper_editorial_historical" and row["register"] == "formal"
    for field in ("id", "instruction", "response", "messages", "source", "licence", "credit", "year", "decade",
                  "date", "newspaper", "state", "lccn", "page", "headline", "byline", "ocr_quality", "legibility",
                  "style_rule"):
        assert field in row, field
    assert row["decade"] == "1860s" and row["year"] == 1865 and row["licence"] == "CC BY 4.0"
    assert row["messages"][1]["content"] == row["response"]


# ====================================================================== choosing years

TREE = [{"type": "file", "path": "README.md", "size": 10},
        {"type": "file", "path": "faro_1866.tar.gz", "size": 300, "lfs": {"oid": "b" * 64, "size": 3_000_000_000}},
        {"type": "file", "path": "faro_1865.tar.gz", "size": 200, "lfs": {"oid": "a" * 64, "size": 2_000_000_000}},
        {"type": "file", "path": "faro_1910.tar.gz", "size": 700, "lfs": {"oid": "c" * 64, "size": 7_000_000_000}}]


def test_year_files_parse_years_and_cap():
    files = sn.year_files(json.dumps(TREE))
    assert [f["year"] for f in files] == [1865, 1866, 1910]
    assert files[0]["size"] == 2_000_000_000 and files[0]["sha256"] == "a" * 64
    assert files[0]["url"].endswith("/resolve/main/faro_1865.tar.gz")
    assert [f["year"] for f in sn.choose(files)[0]] == [1865, 1866, 1910]          # default: every year
    assert [f["year"] for f in sn.choose(files, "1860s")[0]] == [1865, 1866]
    assert [f["year"] for f in sn.choose(files, "1866, 1900-")[0]] == [1866, 1910]
    chosen, left = sn.choose(files, "", max_gb=5.5)
    assert [f["year"] for f in chosen] == [1865, 1866] and [f["year"] for f in left] == [1910]
    with pytest.raises(ValueError):
        sn.parse_years("eighteen sixty")
    assert "hours" in sn.hours_text(340_400_000_000, 100)


# ====================================================================== the resumable download

class Site:
    """A fake web site holding one file. It honours Range requests (unless ignore_range), can cut a download off
    after cut_after bytes (once), and answers robots.txt with 404 (no rules)."""

    def __init__(self, data, cut_after=None, ignore_range=False):
        self.data, self.cut_after, self.ignore_range, self.ranges = data, cut_after, ignore_range, []

    def open(self, req, timeout=None):
        if req.full_url.endswith("/robots.txt"):
            raise urllib.error.HTTPError(req.full_url, 404, "not found", {}, None)
        rng = req.get_header("Range")
        self.ranges.append(rng)
        start = int(rng.split("=")[1].rstrip("-")) if rng and not self.ignore_range else 0
        body = self.data[start:]
        site = self

        class Resp(io.BytesIO):
            status = 206 if start else 200

            def read(self, n=-1):
                if site.cut_after is not None and self.tell() + start >= site.cut_after:
                    site.cut_after = None
                    raise ConnectionResetError("the connection was cut off")
                return super().read(n if site.cut_after is None else min(n, site.cut_after - start - self.tell()))
        return Resp(body)


DATA = bytes(range(256)) * 400                    # 102,400 made-up bytes
SHA = hashlib.sha256(DATA).hexdigest()
URL = "https://files.example.com/faro_1865.tar.gz"


def fetcher(site, lines=None):
    return fetch.Fetcher(say=(lines.append if lines is not None else lambda _: None), opener=site)


def test_download_resumes_after_a_cut_off(tmp_path):
    site, lines = Site(DATA, cut_after=40_000), []
    dest = str(tmp_path / "faro_1865.tar.gz")
    how = fetcher(site).download(URL, dest, size=len(DATA), sha256=SHA, say=lines.append, chunk=8192,
                                 report_every=30_000, sleep=lambda s: None)
    assert how == "downloaded" and open(dest, "rb").read() == DATA
    assert site.ranges[0] is None and site.ranges[1].startswith("bytes=4")   # the second request asks for the rest
    assert any("resuming" in line for line in lines) and any("%" in line for line in lines)
    assert not os.path.exists(dest + ".part")


def test_download_resumes_a_part_file_left_by_an_earlier_run(tmp_path):
    dest = str(tmp_path / "faro_1865.tar.gz")
    with open(dest + ".part", "wb") as f:
        f.write(DATA[:5000])
    site = Site(DATA)
    fetcher(site).download(URL, dest, size=len(DATA), sha256=SHA, sleep=lambda s: None)
    assert site.ranges == ["bytes=5000-"] and open(dest, "rb").read() == DATA


def test_download_starts_again_when_the_site_ignores_range(tmp_path):
    dest = str(tmp_path / "faro_1865.tar.gz")
    with open(dest + ".part", "wb") as f:
        f.write(DATA[:5000])
    fetcher(Site(DATA, ignore_range=True)).download(URL, dest, size=len(DATA), sha256=SHA, sleep=lambda s: None)
    assert open(dest, "rb").read() == DATA


def test_download_skips_a_finished_file_and_rejects_a_bad_checksum(tmp_path):
    dest = str(tmp_path / "faro_1865.tar.gz")
    with open(dest, "wb") as f:
        f.write(DATA)
    site = Site(DATA)
    assert fetcher(site).download(URL, dest, size=len(DATA)) == "already" and site.ranges == []
    other = str(tmp_path / "faro_1866.tar.gz")
    with pytest.raises(ValueError):
        fetcher(Site(DATA)).download(URL, other, size=len(DATA), sha256="0" * 64, sleep=lambda s: None)
    assert not os.path.exists(other) and not os.path.exists(other + ".part")


class FakeFetcher:
    """Stands in for fetch.Fetcher in download_years: 'downloads' by writing made-up bytes of the right size."""

    def __init__(self, fail=()):
        self.fail, self.asked = set(fail), []

    def download(self, url, dest, size=None, sha256=None, say=None):
        self.asked.append(url)
        if os.path.exists(dest) and os.path.getsize(dest) == size:
            return "already"
        if any(url.endswith(name) for name in self.fail):
            raise OSError("cut off")
        with open(dest, "wb") as f:
            f.write(b"x" * size)
        return "downloaded"


def small_files():
    return [{"year": y, "name": f"faro_{y}.tar.gz", "size": s, "sha256": "", "url": f"{URL[:-16]}faro_{y}.tar.gz"}
            for y, s in ((1865, 1000), (1866, 2000), (1867, 3000))]


def test_download_years_running_total_resume_and_disk_space(tmp_path):
    lines = []
    folder = str(tmp_path / "papers")
    results = sn.download_years(FakeFetcher(fail={"faro_1866.tar.gz"}), folder, small_files(), lines.append,
                                free_bytes=10 ** 9)
    assert [how for _, how in results] == ["downloaded", "cut off", "downloaded"]
    assert any("file 1 of 3" in line for line in lines) and any("Running total" in line for line in lines)
    again = sn.download_years(FakeFetcher(), folder, small_files(), lines.append, free_bytes=10 ** 9)
    assert [how for _, how in again] == ["already", "downloaded", "already"]
    lines.clear()
    stopped = sn.download_years(FakeFetcher(), str(tmp_path / "other"), small_files(), lines.append,
                                free_bytes=2500)
    assert stopped[-1] == (1866, "not enough disk space") and "STOPPED" in lines[-1]
    assert [y for y, _ in sn.local_year_files(folder, "1866-")] == [1866, 1867]


# ====================================================================== building

def test_build_year_writes_style_files_and_resumes(tmp_path):
    path = tmp_path / "faro_1865.tar.gz"
    path.write_bytes(year_file(1865))
    out = str(tmp_path / "out")
    result = build_newspapers.build_year(1865, str(path), out, say=lambda _: None)
    assert result["articles"] == 8 and result["examples"] == 8
    folder = tmp_path / "out" / "newspapers" / "1860s" / "1865"
    assert (folder / "DONE.txt").exists() and not (tmp_path / "out" / "newspapers" / "1860s" / "1865.part").exists()
    rows = []
    for name in os.listdir(folder):
        if name.endswith(".jsonl.gz"):
            with gzip.open(folder / name, "rt", encoding="utf-8") as f:
                rows += [json.loads(line) for line in f]
    assert len(rows) == 8 and {r["style"] for r in rows} == set(sn.STYLES)
    path.write_bytes(b"not a tar file")                                # a finished year is not read again
    assert build_newspapers.build_year(1865, str(path), out, say=lambda _: None) == result
    build_newspapers.write_summary(out, [result], say=lambda _: None)
    report = (tmp_path / "out" / "newspapers" / "NEWSPAPERS-REPORT.txt").read_text(encoding="utf-8")
    assert "1860s: 8 articles, 8 examples." in report
    assert "2308.12477" in (tmp_path / "out" / "newspapers" / "ATTRIBUTION.txt").read_text(encoding="utf-8")


def test_build_only_command_with_a_chosen_style(tmp_path):
    folder = tmp_path / "papers"
    folder.mkdir()
    (folder / "faro_1865.tar.gz").write_bytes(year_file(1865))
    out = tmp_path / "out"
    assert build_newspapers.main(["--build-only", "--folder", str(folder), "--out", str(out), "--workers", "1",
                                  "--styles", "newspaper_notice_historical"]) == 0
    names = os.listdir(out / "newspapers" / "1860s" / "1865")
    assert [n for n in names if n.endswith(".gz")] == ["newspaper_notice_historical-train.jsonl.gz"] or \
        [n for n in names if n.endswith(".gz")] == ["newspaper_notice_historical-validation.jsonl.gz"]


def test_sample_build_through_the_ordinary_builder(tmp_path):
    folder = tmp_path / "papers"
    folder.mkdir()
    (folder / "faro_1865.tar.gz").write_bytes(year_file(1865))
    out = tmp_path / "out"
    assert build_dataset.main(["--out", str(out), "--sources", sn.SOURCE_KEY, "--newspaper-folder", str(folder)]) == 0
    rows = [json.loads(line) for name in ("train.jsonl", "validation.jsonl")
            for line in (out / name).read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 8 and all(r["source"] == sn.SOURCE_KEY and r["decade"] == "1860s" for r in rows)
    assert (out / "newspaper_notice_historical").is_dir()


def test_sample_streams_the_start_of_sample_years_when_nothing_is_downloaded(tmp_path):
    class Streamer:
        def __init__(self):
            self.asked = []

        def open_stream(self, url):
            self.asked.append(url)
            return io.BytesIO(year_file(int(url[-11:-7])))
    streamer = Streamer()
    got = list(sn.read_american_stories(streamer, say=lambda _: None, newspaper_folder=str(tmp_path / "none"),
                                        newspaper_years="1860-1890", per_year=3))
    assert [u[-16:] for u in streamer.asked] == ["faro_1865.tar.gz", "faro_1885.tar.gz"]
    assert len(got) == 6
