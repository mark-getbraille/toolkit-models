"""A self-test of the disability, veterans and immigration picture packs (packs/people_packs.py) and the kit's
collections (training-kit/kit/people_sources.py), with made-up rows only: nothing is downloaded from the internet.

It checks that:
  - the notes say what the owner asked (the ADA and ADA.gov, 711 relay, the Veterans Crisis Line's 988 then 1, USCIS
    and no notarios, and the not-legal-advice line), with the same words in the packs and the kit;
  - every answer is "This is ...", ends with its pack's note where the pack needs one (every veterans and
    immigration answer), and uses no pitying words about disabled people;
  - no Commons category of these packs is named by another pack file or the kit's other files, nor twice here, and
    the kit's share-alike entry only uses the packs' own categories with the same answers;
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflows' known list and limit lines, in the
    kit's sources (packs "permissive", prepare_pack), never for picture-making, in the machines or documents topic
    (veterans in none), and the guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_people.py
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import people_packs as P  # noqa: E402

REPO = os.path.dirname(HERE)
NOTES = ("LEGAL", "ACCESS_NOTE", "HEARING_NOTE", "VETERAN_NOTE", "IMMIGRATION_NOTE")
PITY = re.compile(r"\b(suffer\w*|confined|wheelchair-bound|bound to|victim|handicapped|afflicted|stricken|"
                  r"crippled|invalid)\b", re.I)


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    assert P.LEGAL == ("General information, not legal advice; check the current rules or ask an accredited "
                       "representative or lawyer.")
    assert "ADA.gov" in P.ACCESS_NOTE and "800-514-0301" in P.ACCESS_NOTE
    assert "711" in P.HEARING_NOTE and "audiologist" in P.HEARING_NOTE
    assert "988 then press 1" in P.VETERAN_NOTE and "VA.gov" in P.VETERAN_NOTE
    assert "USCIS" in P.IMMIGRATION_NOTE and "notario" in P.IMMIGRATION_NOTE
    assert P.IMMIGRATION_NOTE.endswith(P.LEGAL)


def test_every_answer():
    for category, answer in answers(P.specs()):
        assert answer.startswith("This is ") and answer.endswith("."), category
        assert not PITY.search(answer), category
    for category, answer in answers(P.VETERANS):
        assert answer.endswith(P.VETERAN_NOTE), category
    for category, answer in answers(P.IMMIGRATION_DOCUMENTS):
        assert answer.endswith(P.IMMIGRATION_NOTE), category
    for category, answer in answers(P.HEARING_COMMUNICATION):
        if re.search(r"hearing|audio|TTY|videophone", category + answer.split(".")[0], re.I):
            assert P.HEARING_NOTE in answer or P.ACCESS_NOTE in answer, category
    # nothing made up: no number of degrees, sizes or prices outside the notes
    for _category, answer in answers(P.specs()):
        rest = answer
        for name in NOTES:
            rest = rest.replace(getattr(P, name), "")
        assert not re.search(r"\$\d|\d+\s*(cm|mm|inches|pounds|kg)\b", rest), answer


def test_no_commons_category_is_used_elsewhere():
    """No category of these packs is named (in quotes) by another pack file or kit file, nor twice here."""
    others = ""
    files = glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(REPO, "training-kit", "kit", "*.py"))
    for path in files:
        name = os.path.basename(path)
        if name in ("people_packs.py", "people_sources.py") or name.startswith("test_"):
            continue
        with open(path, encoding="utf-8") as f:
            others += f.read()
    names = [spec[0] for spec in P.specs()]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_matches():
    import sources  # noqa: F401 - loaded first: it loads people_sources at its end
    import people_sources as k
    for name in NOTES:
        assert getattr(k, name) == getattr(P, name), name
    pack_answers = {spec[0]: spec[2][0][1] for spec in P.specs()}
    for category, _q, answer, _deeper in k.PEOPLE_SA:
        assert pack_answers.get(category) == answer, category
    assert all(reason for reason in k.PEOPLE_NOT_INCLUDED.values())
    assert not k.PEOPLE_PICTURE_MAKING_OK


def test_wiring():
    keys = set(P.PEOPLE_PACKS)
    assert keys == set(P.PEOPLE_LIMITS) and len(keys) == 4
    assert keys <= set(build_packs.PACKS)
    assert set(P.PEOPLE_COMMONS_KEYS) == keys and keys <= build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in P.PEOPLE_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import people_sources") == 2
    import sources
    import topics
    import people_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    machines, documents = set(topics.find("machines").keys), set(topics.find("documents").keys)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert key in no_making, key
    assert "commons_mobility_aids" in machines and "people_commons_sa" in machines
    assert {"commons_hearing_communication", "commons_immigration_documents"} <= documents
    assert not any("commons_veterans" in t.keys for t in topics.TOPICS)
    for s in k.PEOPLE_SOURCES:
        assert s.key in listed and s.key in no_making, s.key
        assert s.key in keys or s.group != "permissive", s.key
    assert listed["people_commons_sa"].group == "share-alike"
