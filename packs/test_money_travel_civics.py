"""A self-test of the money and work, travel, and citizenship and civics packs (packs/money_work_packs.py,
packs/travel_packs.py, packs/civics_packs.py and their helpers in packs/synthetic_documents.py) and the kit's
collections (training-kit/kit/money_work_sources.py, travel_sources.py, civics_sources.py). Only computer-made
documents are drawn (a few, small); nothing is downloaded from the internet.

It checks that:
  - every synthetic document can never pass for a real one: its rows say SPECIMEN and not real, its people are from
    the made-up name lists, Social Security numbers begin 000 and employer numbers 00 (never issued), passports are
    of the made-up country Utopia with numbers containing "SPC", airlines are made up, phone numbers are in the
    555-01xx range and web addresses end ".example";
  - every answer agrees with the facts the generator drew (net pay is gross pay less the deductions, boarding is
    before departure, the passport expires after it was issued);
  - tax and legal answers end with the not-advice line;
  - the AIGA sign specs name each sign from its file's own name and never mix plain and hotel information or
    parking and no parking; no Commons category of these packs is named by another pack file;
  - every pack is wired: in build_packs.PACKS, the Commons one in COMMONS_KEYS (and only it), in the workflows' known
    list and limit lines, in the kit's sources (group "permissive", prepare_pack), in the documents topic, never
    for picture-making, and the three kit files listed twice as hidden imports.

Run it from the repository's folder:   python3 -m pytest packs/test_money_travel_civics.py
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import civics_packs as cv  # noqa: E402
import money_work_packs as mw  # noqa: E402
import synthetic_bills_packs as bills  # noqa: E402
import synthetic_documents as sd  # noqa: E402
import travel_packs as tr  # noqa: E402

REPO = os.path.dirname(HERE)
NOT_ADVICE = "General information, not tax or legal advice; check the current rules or ask a professional."
ALL_PACKS = {**mw.MONEY_WORK_PACKS, **tr.TRAVEL_PACKS, **cv.CIVICS_PACKS}
ALL_LIMITS = {**mw.MONEY_WORK_LIMITS, **tr.TRAVEL_LIMITS, **cv.CIVICS_LIMITS}
SYNTHETIC = ("synthetic_pay_documents", "synthetic_travel_documents", "synthetic_civic_documents")


def test_impossible_numbers():
    for n in range(40):
        rng = sd.seeded(1, n)
        assert re.fullmatch(r"000-\d\d-\d{4}", sd.impossible_ssn(rng))
        assert re.fullmatch(r"00-\d{7}", sd.impossible_ein(rng))
        assert re.fullmatch(r"\(555\) 555-01\d\d", sd.fiction_phone(rng))
        first, last = sd.made_up_person(rng)
        assert first in bills.FIRST and last in bills.LAST


def rows_of(make, n):
    """The rows of the n-th document of a maker (the picture is drawn but not kept)."""
    _name, data, rows = make(n)
    assert data[:2] == b"\xff\xd8"                  # a JPEG
    return rows


def check_common(rows, credit):
    """Every row is synthetic and credited; one says the document is not real and marked SPECIMEN."""
    assert all(r["synthetic"] and r["credit"] == credit for r in rows)
    not_real = [r for r in rows if r["question"] == sd.NOT_REAL_Q]
    assert len(not_real) == 1 and not_real[0]["answer"].startswith("No. It is marked SPECIMEN")
    assert "SPECIMEN" in rows[0]["answer"] and "made-up" in rows[0]["answer"]


def test_pay_documents():
    for n in range(6):
        rows = rows_of(mw.make_document, n)
        check_common(rows, mw.CREDIT)
        said = {r["question"]: r["answer"] for r in rows}
        if n % 3 == 2:
            assert re.search(r"Box a shows 000-\d\d-\d{4}", said["What Social Security number is printed?"])
            assert said["How much federal tax was withheld?"].endswith(NOT_ADVICE)
        else:
            assert said["What was taken out?"].endswith(NOT_ADVICE)
    rng = sd.seeded(mw.SEED, 0)
    d = mw.stub_details(rng)
    assert d["net"] == d["gross"] - sum(c for _t, c in d["deductions"]) and d["net"] > 0
    assert d["start"] < d["end"] < d["paid"]
    w = mw.w2_details(sd.seeded(mw.SEED, 2))
    assert w["ssn"].startswith("000-") and w["ein"].startswith("00-") and w["box1"] <= w["box3"]


def test_travel_documents():
    for n in range(4):
        rows = rows_of(tr.make_document, n)
        check_common(rows, tr.CREDIT)
    p = tr.passport_details(0, sd.seeded(tr.SEED, 0))
    assert p["number"].startswith("SPC") and p["issued"] < p["expires"]
    b = tr.boarding_details(1, sd.seeded(tr.SEED, 1))
    assert b["flight"][:2] in {code for _n, code in tr.AIRLINES} and b["board"] < b["depart"]
    assert {code for _n, code in tr.AIRLINES} <= {"ZZ", "ZY", "ZX"}
    rows = tr.passport_rows(p)
    assert any("Utopia" in r["answer"] for r in rows)


def test_civic_documents():
    for n in range(4):
        rows = rows_of(cv.make_document, n)
        check_common(rows, cv.CREDIT)
    s = cv.summons_details(sd.seeded(cv.SEED, 1))
    assert s["web"].endswith(".example") and s["phone"].startswith("(555) 555-01")
    rows = cv.summons_rows(s)
    said = {r["question"]: r["answer"] for r in rows}
    assert said["When and where do I report?"].endswith(NOT_ADVICE)
    ballot = cv.ballot_details(sd.seeded(cv.SEED, 0))
    assert all(len(people) >= 2 for _o, _m, people in ballot["contests"])
    assert all(c in cv.COUNTIES for c in [ballot["county"]])


def test_specimen_marks_drawn():
    from PIL import Image
    page = Image.new("RGB", (600, 400), (255, 255, 255))
    marked = sd.specimen_marks(page)
    assert marked.size == page.size and marked.getbbox() and marked.tobytes() != page.tobytes()


def test_aiga_signs():
    specs = tr.aiga_specs()
    assert len(specs) == len(tr.AIGA_SIGNS) and all(s[0] == tr.AIGA for s in specs)

    def meaning(file_title):
        hits = [s[2][0][1] for s in specs if s[3].search(file_title)]
        return hits
    assert len(meaning("File:AIGA information.svg")) == 1 and "where you can ask" in meaning("File:AIGA information.svg")[0]
    assert len(meaning("File:Aiga hotelinformation.svg")) == 1 and "hotel" in meaning("File:Aiga hotelinformation.svg")[0]
    assert len(meaning("File:Aiga noparking.svg")) == 1 and "no parking" in meaning("File:Aiga noparking.svg")[0]
    assert len(meaning("File:Aiga parking.svg")) == 1 and "for parking" in meaning("File:Aiga parking.svg")[0]
    assert meaning("File:Aiga toiletsq men.svg") == [] and meaning("File:BSicon PASSPORT.svg") == []
    assert not tr.CHANGE_WORDS.search("File:2013 Boston Marathon-48.jpg") and tr.TAXI_WORDS.search("taxi rank")
    for _c, _d, rows, _p in specs:
        assert rows[0][1].startswith("It is the symbol sign for ") and rows[0][1].endswith(tr.AIGA_NOTE)


def test_no_commons_category_is_used_by_another_pack():
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.basename(path) != "travel_packs.py" and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in tr.TRAVEL_SPECS] + [tr.AIGA]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_wiring():
    keys = set(ALL_PACKS)
    assert keys == set(ALL_LIMITS) and len(keys) == 4
    assert keys <= set(build_packs.PACKS)
    assert set(tr.TRAVEL_COMMONS_KEYS) == {"commons_travel_signs"} <= build_packs.COMMONS_KEYS
    assert not set(SYNTHETIC) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in ALL_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    for name in ("money_work_sources", "travel_sources", "civics_sources"):
        assert kit_yml.count(f"--hidden-import {name} ") == 2, name
    import sources
    import topics
    import civics_sources
    import money_work_sources
    import travel_sources
    listed = {s.key: s for s in sources.SOURCES}
    # pay and civic papers in money, travel documents and signs in transport (the signs also in documents)
    placed = set(topics.find("money").keys) | set(topics.find("transport").keys)
    kit = money_work_sources.MONEY_WORK_SOURCES + travel_sources.TRAVEL_SOURCES + civics_sources.CIVICS_SOURCES
    assert {s.key for s in kit} == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert key in placed, key
        assert key in sources.NOT_FOR_PICTURE_MAKING and key not in sources.PERSONAL_PICTURE_MAKING_OK, key
        assert listed[key].cap == ALL_LIMITS[key], key
    assert "commons_travel_signs" in topics.find("documents").keys
    for mod in (money_work_sources, travel_sources, civics_sources):
        not_included = [v for k, v in vars(mod).items() if k.endswith("_NOT_INCLUDED")][0]
        assert not_included and all(not_included.values())
