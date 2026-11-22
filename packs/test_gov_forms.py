"""A self-test of the filled-in government forms pack (packs/gov_forms_packs.py) and the kit's collection
(training-kit/kit/gov_forms_sources.py). Only computer-made forms are drawn (a few, small); nothing is downloaded.

It checks that every form can never pass for a real one (its title says SPECIMEN and not an IRS or SSA form, its
rows say not real, people are from the made-up name lists, Social Security numbers begin 000 and employer numbers
00), that every answer agrees with the facts the generator drew, that tax answers end with the not-advice line, and
that the pack is wired: in build_packs.PACKS (not a Commons pack), the workflows' known list and limit line, the
kit's sources (group "permissive", prepare_pack), the documents topic, never for picture-making, and the kit file
listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_gov_forms.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gov_forms_packs as gf  # noqa: E402
import synthetic_bills_packs as bills  # noqa: E402
import synthetic_documents as sd  # noqa: E402

REPO = os.path.dirname(HERE)


def test_every_kind_is_specimen_and_exact():
    seen = set()
    for n in range(8):
        rng = sd.seeded(gf.SEED, n)
        d = gf.details(gf.KINDS[n % len(gf.KINDS)], rng)
        seen.add(d["kind"])
        assert d["first"] in bills.FIRST and d["last"] in bills.LAST
        assert re.fullmatch(r"000-\d\d-\d{4}", d["ssn"])
        for key in ("ein", "payer_ein"):
            if d.get(key):
                assert re.fullmatch(r"00-\d{7}", d[key])
        assert "SPECIMEN, not an" in gf.TITLES[d["kind"]]
        rows = gf.form_rows(d)
        assert all(r["synthetic"] and r["credit"] == gf.CREDIT for r in rows)
        assert "SPECIMEN" in rows[0]["answer"] and "made-up" in rows[0]["answer"]
        not_real = [r for r in rows if r["question"] == sd.NOT_REAL_Q]
        assert len(not_real) == 1 and not_real[0]["answer"].startswith("No. It is marked SPECIMEN")
        values = " ".join(v for _label, v in gf.field_list(d))
        assert d["ssn"] in values and f"{d['first']} {d['last']}" in values
        if d["kind"] == "w4":
            assert d["dependents"] == d["children"] * 220000 + d["others"] * 50000
        if d["kind"] in ("w4", "w9", "nec"):
            assert any(r["answer"].endswith(gf.NOT_ADVICE) for r in rows)
    assert seen == set(gf.KINDS)
    name, data, rows = gf.make_form(0)
    assert data[:2] == b"\xff\xd8" and name.startswith("govform-w4-")


def test_wiring():
    keys = set(gf.GOV_FORMS_PACKS)
    assert keys == set(gf.GOV_FORMS_LIMITS) == {"synthetic_gov_forms"}
    assert keys <= set(build_packs.PACKS) and not keys & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in gf.GOV_FORMS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import gov_forms_sources ") == 2
    import sources                     # first: it loads gov_forms_sources itself
    import topics
    import gov_forms_sources
    listed = {s.key: s for s in sources.SOURCES}
    assert {s.key for s in gov_forms_sources.GOV_FORMS_SOURCES} == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack
        assert key in topics.find("documents").keys
        assert key in sources.NOT_FOR_PICTURE_MAKING and key not in sources.PERSONAL_PICTURE_MAKING_OK
        assert listed[key].cap == gf.GOV_FORMS_LIMITS[key]
    assert all(gov_forms_sources.GOV_FORMS_NOT_INCLUDED.values())
