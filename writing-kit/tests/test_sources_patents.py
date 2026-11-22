"""Tests of the patent sources (kit/sources_patents.py) and their full-corpus command (kit/build_patents.py). Every
patent, application, year file, weekly file and portal answer here is made up; no network is used."""

import gzip
import io
import json
import os
import sys
import tarfile
import urllib.error
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import build_dataset  # noqa: E402
import build_patents as bp  # noqa: E402
import sources_patents as sp  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402

APPLICATION = {"application_number": "12345678", "publication_number": "US20160000001A1",
               "title": "MADE-UP TACTILE READER", "decision": "ACCEPTED", "filing_date": "2016-01-05",
               "main_cpc_label": "G09B21/004", "patent_number": "9999999",
               "abstract": "A made-up reader turns printed letters into raised dots under the fingers.",
               "claims": "1. A made-up reader comprising a camera and a pin array.\n2. The reader of claim 1, wherein "
                         "the pins are round.",
               "background": "Made-up background.", "summary": "Made-up summary.",
               "full_description": "BACKGROUND\n\nPeople who are blind read made-up braille.\n\nDETAILED DESCRIPTION"
                                   "\n\nThe camera sees the page and the pins rise in made-up patterns."}


def hupd_year(year=2016, apps=None):
    """A made-up HUPD year file (bytes)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for i, app in enumerate(apps if apps is not None else [APPLICATION]):
            raw = json.dumps(app).encode("utf-8")
            info = tarfile.TarInfo(f"{year}/{app.get('application_number', i)}.json")
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    return buf.getvalue()


V4 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE us-patent-grant SYSTEM "us-patent-grant-v47-2022-02-17.dtd" [ ]>
<us-patent-grant><us-bibliographic-data-grant>
<publication-reference><document-id><country>US</country><doc-number>11111111</doc-number><kind>B2</kind>
<date>20300105</date></document-id></publication-reference>
<application-reference appl-type="utility"><document-id><country>US</country><doc-number>17000001</doc-number>
<date>20280301</date></document-id></application-reference>
<classifications-cpc><main-cpc><classification-cpc><section>A</section><class>47</class><subclass>J</subclass>
<main-group>31</main-group><subgroup>44</subgroup></classification-cpc></main-cpc></classifications-cpc>
<invention-title id="d2e1">Made-up coffee maker</invention-title></us-bibliographic-data-grant>
<abstract id="abstract"><p id="p-0001">A made-up coffee maker heats water &amp; pours it.</p></abstract>
<description id="description"><heading id="h-1">BACKGROUND</heading><p id="p-0002">Made-up words about coffee.</p>
</description><claims id="claims"><claim id="CLM-1" num="00001"><claim-text>1. A made-up coffee maker comprising a
heater.</claim-text></claim></claims></us-patent-grant>
"""
V25 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE PATDOC SYSTEM "ST32-US-Grant-025xml.dtd" [ ]>
<PATDOC><SDOBI><B100><B110><DNUM><PDAT>06500000</PDAT></DNUM></B110><B140><DATE><PDAT>20030107</PDAT></DATE></B140>
</B100><B200><B210><DNUM><PDAT>09000001</PDAT></DNUM></B210><B220><DATE><PDAT>20010202</PDAT></DATE></B220></B200>
<B500><B540><STEXT><PDAT>Made-up washing machine</PDAT></STEXT></B540></B500></SDOBI>
<SDOAB><BTEXT><PARA ID="P-00001"><PTEXT><PDAT>A made-up washer spins clothes.</PDAT></PTEXT></PARA></BTEXT></SDOAB>
<SDODE><BTEXT><H LVL="1"><STEXT><PDAT>BACKGROUND</PDAT></STEXT></H><PARA ID="P-00002"><PTEXT><PDAT>Made-up washing
words.</PDAT></PTEXT></PARA></BTEXT></SDODE>
<SDOCL><CL><CLM ID="CLM-00001"><PARA ID="P-00003"><PTEXT><PDAT>1. A made-up washer comprising a drum.</PDAT></PTEXT>
</PARA></CLM></CL></SDOCL></PATDOC>
"""
APS = """HHHHHT APS1      ISSUE  760106
PATN
WKU  039300014
APN  0545678
APD  19750115
TTL  Made-up refrigerator door
ISD  19760106
INVT
NAM  Example; Ann
ABST
PAL  A made-up door keeps the cold inside the made-up
     refrigerator box.
BSUM
PAC  BACKGROUND
PAR  Made-up words about cold.
CLMS
NUM  1.
PAR  A made-up refrigerator door comprising a seal.
NUM  2.
PAR  The door of claim 1, wherein the seal is rubber.
PATN
WKU  039300022
TTL  Second made-up patent
ISD  19760106
ABST
PAL  A second made-up abstract with enough words in it.
"""


def weekly_zip(name, text):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, text)
    return buf.getvalue()


# ====================================================================== the sources and the examples

def test_sources_and_styles_are_registered():
    known = writing_sources.by_key()
    assert known[sp.HUPD_KEY].licence_class == writing_sources.SHARE_ALIKE and known[sp.HUPD_KEY].licence == \
        "CC BY-SA 4.0"
    assert known[sp.USPTO_KEY].licence_class == writing_sources.OPEN
    assert {sp.HUPD_KEY, sp.USPTO_KEY} <= build_dataset.OPT_IN
    for style in sp.STYLES:
        assert style in styles.STYLES and style in styles.FORMAL_STYLES
    assert not any("USPTO patent full texts" == name for name, _ in writing_sources.NOT_USED)


def test_three_styles_from_one_application():
    records = list(sp.hupd_records(io.BytesIO(hupd_year())))
    assert [r["style_label"] for r in records] == ["patent_abstract", "patent_claims", "patent_description"]
    abstract = records[0]
    assert abstract["instruction"] == ('Write the abstract of a US patent application titled "Made-up tactile reader", '
                                       "filed 2016-01-05 (main CPC class G09B21/004). Write it in the formal, precise "
                                       "style of a US patent.")
    assert abstract["response"] == APPLICATION["abstract"]
    assert records[1]["response"].startswith("1. A made-up reader comprising") and "\n2. The reader" not in \
        records[1]["response"]      # one paragraph: lines joined, words unchanged
    assert "pins rise in made-up patterns" in records[2]["response"]
    extra = records[2]["extra"]
    assert extra["year"] == 2016 and extra["decade"] == "2010s" and extra["section"] == "description"
    assert extra["decision"] == "ACCEPTED" and extra["application_number"] == "12345678"


def test_copyright_notice_leaves_a_patent_out():
    marked = dict(APPLICATION, full_description="A portion of the disclosure of this patent document contains "
                                                "material which is subject to copyright protection.")
    assert list(sp.hupd_records(io.BytesIO(hupd_year(apps=[marked])))) == []
    assert sp.patent_records(sp.hupd_patent(dict(APPLICATION, abstract="(c) 2015 Made-Up Corp.")), sp.HUPD_KEY) == []


def test_hupd_year_list():
    listing = [{"type": "file", "path": "data/2016.tar.gz", "size": 1, "lfs": {"size": 5571700238, "oid": "ab"}},
               {"type": "file", "path": "data/2004.tar.gz", "size": 1, "lfs": {"size": 2590424725, "oid": "cd"}},
               {"type": "file", "path": "data/all-years.tar", "size": 9},
               {"type": "file", "path": "data/sample-jan-2016.tar.gz", "size": 9}]
    files = sp.hupd_year_files(json.dumps(listing))
    assert [f["year"] for f in files] == [2004, 2016] and files[1]["size"] == 5571700238
    assert files[0]["url"] == "https://huggingface.co/datasets/HUPD/hupd/resolve/main/data/2004.tar.gz"


def test_grant_formats():
    v4 = list(sp.grant_docs(V4))[0]
    assert v4["patent_number"] == "11111111" and v4["grant_date"] == "2030-01-05" and v4["filing_date"] == "2028-03-01"
    assert v4["main_cpc"] == "A47J31/44" and v4["abstract"] == "A made-up coffee maker heats water & pours it."
    assert v4["claims"].startswith("1. A made-up coffee maker") and v4["description"].startswith("BACKGROUND")
    v25 = list(sp.grant_docs(V25))[0]
    assert v25["title"] == "Made-up washing machine" and v25["patent_number"] == "6500000"
    assert v25["grant_date"] == "2003-01-07" and v25["abstract"] == "A made-up washer spins clothes."
    aps = list(sp.aps_docs(APS))
    assert [a["title"] for a in aps] == ["Made-up refrigerator door", "Second made-up patent"]
    first = aps[0]
    assert first["patent_number"] == "3930001" and first["grant_date"] == "1976-01-06"
    assert first["abstract"] == "A made-up door keeps the cold inside the made-up refrigerator box."
    assert first["claims"] == ("1. A made-up refrigerator door comprising a seal.\n\n2. The door of claim 1, wherein "
                               "the seal is rubber.")
    assert first["description"] == "BACKGROUND\n\nMade-up words about cold."


def test_weekly_files_read_document_by_document():
    xml = list(sp.weekly_records(weekly_zip("ipg300105.xml", V4 + V25)))
    assert [r["extra"]["patent_number"] for r in xml if r["style_label"] == "patent_abstract"] == ["11111111",
                                                                                                    "6500000"]
    assert xml[0]["instruction"].startswith('Write the abstract of a US patent titled "Made-up coffee maker", '
                                            "granted 2030-01-05")
    aps = list(sp.weekly_records(weekly_zip("pftaps19760106_wk01.txt", APS)))
    assert {r["extra"]["title"] for r in aps} == {"Made-up refrigerator door", "Second made-up patent"}
    assert len(list(sp.weekly_records(weekly_zip("x.xml", V4 + V25), limit=1))) == 3


def test_portal_lists_are_read_tolerantly():
    search = {"bulkDataProductBag": [{"productIdentifier": "MADEUPXML", "productTitleText": "Patent Grant Full-Text "
                                      "Data (No Images) - XML"},
                                     {"productIdentifier": "MADEUPIMG", "productTitleText": "Patent Grant Full-Text "
                                      "Data with Embedded TIFF Images"},
                                     {"productIdentifier": "OTHER", "productTitleText": "Trademark daily"}]}
    assert sp.grant_products(json.dumps(search)) == ["MADEUPXML"]
    product = {"bulkDataProductBag": [{"productIdentifier": "MADEUPXML", "productFileBag": {"count": 3, "fileDataBag": [
        {"fileName": "ipg300105.zip", "fileSize": 120, "fileDataFromDate": "2030-01-05",
         "fileDownloadURI": sp.ODP + "datasets/products/MADEUPXML/files/ipg300105.zip"},
        {"fileName": "ipg291231.zip", "fileSize": 110},
        {"fileName": "notes.pdf", "fileSize": 1}]}}]}
    files = sp.odp_files(json.dumps(product), 2030)
    assert [f["name"] for f in files] == ["ipg300105.zip"] and files[0]["size"] == 120
    assert [f["name"] for f in sp.odp_files(product, 2029)] == ["ipg291231.zip"]
    flat = {"productIdentifier": "OLD", "productFileBag": [{"fileName": "pftaps19760106_wk01.zip", "fileSize": 7}]}
    assert sp.odp_files(flat, 1976)[0]["url"].endswith("/datasets/products/OLD/files/pftaps19760106_wk01.zip")


# ====================================================================== the command

class FakeOpener:
    """Answers like the Open Data Portal: one address sends the file itself, another redirects to a file store."""

    def __init__(self):
        self.seen = []

    def open(self, req, timeout=None):
        self.seen.append((req.full_url, req.get_header("X-api-key")))
        if "redirect" in req.full_url:
            raise urllib.error.HTTPError(req.full_url, 302, "Found", {"Location": "https://files.example/w.zip"}, None)
        return io.BytesIO(b"")


def test_the_key_never_follows_a_redirect():
    opener = FakeOpener()
    assert bp.resolve("made-up-key", sp.ODP + "x/redirect.zip", opener) == ("https://files.example/w.zip", False)
    assert bp.resolve("made-up-key", sp.ODP + "x/direct.zip", opener) == (sp.ODP + "x/direct.zip", True)
    assert bp.resolve("made-up-key", "https://files.example/other.zip", opener) == \
        ("https://files.example/other.zip", False)
    assert all(key == "made-up-key" for url, key in opener.seen) and len(opener.seen) == 2
    with pytest.raises(ValueError):
        bp.odp_json("made-up-key", "https://example.org/not-the-portal")


def test_uspto_needs_the_key(monkeypatch, capsys):
    monkeypatch.delenv(sp.USPTO_KEY_ENV, raising=False)
    assert bp.main(["--source", "uspto", "--folder", "nowhere"]) == 1
    assert sp.USPTO_KEY_ENV in capsys.readouterr().out
    assert list(sp.read_uspto_grants(None, say=lambda text: None)) == []


def test_uspto_download_marks_finished_years(tmp_path, monkeypatch):
    class FakeFetcher:
        def __init__(self, name):
            self.name, self.got = name, []

        def download(self, url, dest, size=None, say=None):
            self.got.append(url)
            if "broken" in url:
                raise OSError("cut off")
            with open(dest, "wb") as f:
                f.write(b"x" * (size or 1))
            return "downloaded"
    monkeypatch.setattr(bp, "resolve", lambda key, url: (url, url.startswith(sp.ODP)))
    plain, keyed = FakeFetcher("plain"), FakeFetcher("keyed")
    chosen = [{"year": 1976, "size": 4, "files": [{"name": "a.zip", "size": 2, "url": sp.ODP + "a.zip"},
                                                   {"name": "b.zip", "size": 2, "url": "https://files.example/b.zip"}]},
              {"year": 1977, "size": 2, "files": [{"name": "c.zip", "size": 2, "url": "https://files.example/broken"}]}]
    results = bp.download_uspto("made-up-key", str(tmp_path), chosen, say=lambda text: None, fetcher=plain,
                                key_fetcher=keyed)
    assert results == [(1976, "downloaded"), (1977, "cut off")]
    assert keyed.got == [sp.ODP + "a.zip"] and plain.got[0] == "https://files.example/b.zip"
    assert os.path.exists(tmp_path / "1976" / bp.DOWNLOADED) and not os.path.exists(tmp_path / "1977" / bp.DOWNLOADED)


def test_build_year_and_build_only_command(tmp_path):
    folder = tmp_path / "patents" / sp.HUPD_KEY
    folder.mkdir(parents=True)
    (folder / "2016.tar.gz").write_bytes(hupd_year())
    out = str(tmp_path / "out")
    assert bp.main(["--build-only", "--folder", str(tmp_path / "patents"), "--out", out, "--workers", "1"]) == 0
    year = os.path.join(out, "patents", sp.HUPD_KEY, "2010s", "2016")
    names = sorted(os.listdir(year))
    assert "DONE.txt" in names and any(n.startswith("patent_claims-") for n in names)
    rows = []
    for n in names:
        if n.endswith(".jsonl.gz"):
            with gzip.open(os.path.join(year, n), "rt", encoding="utf-8") as f:
                rows += [json.loads(x) for x in f]
    assert sorted(r["style"] for r in rows) == ["patent_abstract", "patent_claims", "patent_description"]
    assert all(r["licence"] == "CC BY-SA 4.0" and r["register"] == "formal" for r in rows)
    report = open(os.path.join(out, "patents", "PATENTS-REPORT.txt"), encoding="utf-8").read()
    assert "hupd_patents 2016: 3 examples" in report
    done = bp.build_year(sp.HUPD_KEY, 2016, str(folder / "2016.tar.gz"), out, say=lambda text: None)
    assert done["examples"] == 3                                   # read back from DONE.txt
    weekly = tmp_path / "patents" / sp.USPTO_KEY / "2030"
    weekly.mkdir(parents=True)
    (weekly / "ipg300105.zip").write_bytes(weekly_zip("ipg300105.xml", V4))
    assert bp.main(["--source", "uspto", "--build-only", "--folder", str(tmp_path / "patents"), "--out", out,
                    "--workers", "1"]) == 1                        # not marked as fully downloaded yet
    (weekly / bp.DOWNLOADED).write_text("[]")
    assert bp.main(["--source", "uspto", "--build-only", "--folder", str(tmp_path / "patents"), "--out", out,
                    "--workers", "1", "--styles", "patent_claims"]) == 0
    got = os.listdir(os.path.join(out, "patents", sp.USPTO_KEY, "2030s", "2030"))
    assert [n for n in got if n.endswith(".gz")][0].startswith("patent_claims-")


def test_sample_reads_downloaded_year_files(tmp_path):
    folder = tmp_path / "patents" / sp.HUPD_KEY
    folder.mkdir(parents=True)
    (folder / "2016.tar.gz").write_bytes(hupd_year())
    records = list(sp.read_hupd(None, say=lambda text: None, patent_folder=str(tmp_path / "patents")))
    assert len(records) == 3 and records[0]["extra"]["title"] == "Made-up tactile reader"
