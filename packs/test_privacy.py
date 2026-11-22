"""A self-test of the privacy, security and digital safety packs (packs/privacy_packs.py and
packs/synthetic_scams_packs.py) and the kit's collections (training-kit/kit/privacy_sources.py), with made-up records
only: nothing is downloaded from the internet (the scam examples are drawn here, from the generator's fixed seed).

It checks that:
  - the notes say what the owner asked: report to the FTC (ReportFraud.ftc.gov), 7726 and the FBI (ic3.gov), the
    Elder Fraud Hotline 1-833-372-8311, gift cards, codes, pop-ups, padlocks and voice cloning, and the kit uses the
    same words;
  - every computer-made example is DEFENSIVE and unmistakably made up: the EXAMPLE banner and "made-up example" in
    its answers, web addresses only under ".example", phone numbers only in the 555-01xx range (besides the real
    reporting lines in the notes), no real bank, courier or agency name, and its scam answer names warning signs;
  - the generator gives the same pictures and rows from the same seed, and every kind can be drawn;
  - every Commons answer starts "This is" and carries its note where it should, and no Commons category is named by
    another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows (never the scam examples or screenshots), in the privacy topic, and the guarded kit
    module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_privacy.py
"""

import glob
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import privacy_packs as p  # noqa: E402
import synthetic_scams_packs as s  # noqa: E402

REPO = os.path.dirname(HERE)
KEYS = set(p.PRIVACY_PACKS) | set(s.SYNTHETIC_SCAMS_PACKS)
LIMITS = dict(p.PRIVACY_LIMITS, **s.SYNTHETIC_SCAMS_LIMITS)
# The real reporting lines the notes name; every other number in an example must be a 555-01xx one.
REAL_LINES = ("1-833-372-8311", "7726")
REAL_NAMES = re.compile(r"\b(IRS|Social Security Administration|Medicare|FedEx|UPS|USPS|DHL|Amazon|PayPal|Apple|"
                        r"Microsoft|Google|Chase|Wells Fargo|Bank of America|Venmo|Zelle|Cash App|Norton|McAfee|"
                        r"Geek Squad|Walmart|Target|Best Buy)\b")


def test_notes_say_what_the_owner_asked():
    assert "ReportFraud.ftc.gov" in s.REPORT_NOTE and "7726" in s.REPORT_NOTE and "ic3.gov" in s.REPORT_NOTE
    assert "1-833-372-8311" in s.ELDER_NOTE
    assert "gift card" in s.GIFT_NOTE and "cryptocurrency" in s.GIFT_NOTE
    assert "never ask you to call a phone number" in s.POPUP_NOTE
    assert "does not prove the site is honest" in s.PADLOCK_NOTE
    assert "code word" in s.VOICE_NOTE and "AI" in s.VOICE_NOTE
    assert "WPA3" in p.ROUTER_NOTE and "default admin password" in p.ROUTER_NOTE
    assert "do not pay" in p.RANSOM_NOTE and "3-2-1" in p.RANSOM_NOTE
    assert "audio" in p.CAPTCHA_NOTE


def every_kind():
    """One made-up example of every kind, from a fixed seed (the facts only, nothing drawn)."""
    out = []
    for i, kind in enumerate(s.KINDS):
        d = s.template(random.Random(f"test-{i}"), kind)
        d["rng"] = random.Random(i)
        out.append(d)
    return out


def test_examples_are_made_up_and_defensive():
    for d in every_kind():
        rows = s.example_rows(d)
        said = " ".join(r["answer"] for r in rows)
        assert all(r["synthetic"] and r["example"] for r in rows), d["kind"]
        assert rows[0]["answer"].startswith("This is a made-up example of") and "EXAMPLE" in rows[0]["answer"]
        assert s.BANNER in rows[1]["answer"], d["kind"]
        text = " ".join([d["sender"], d["subject"]] + d["lines"])
        hosts = re.sub(r"[\w.+-]+@", "", text.lower())           # an email address's host only
        for host in re.findall(r"([a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,})\b", hosts):
            assert host.endswith(".example"), (d["kind"], host)
        notes = " ".join(s.NOTES)
        for number in re.findall(r"\d[\d-]{6,}\d", text + " " + said.replace(notes, "")):
            if number not in REAL_LINES and not re.fullmatch(r"\d{6}", number):
                assert "555-01" in number, (d["kind"], number)
        assert not REAL_NAMES.search(text), (d["kind"], REAL_NAMES.search(text))
        if d["verdict"] == "scam":
            assert rows[2]["answer"].startswith("Yes, this made-up example shows the warning signs of a scam: ")
            assert len(d["signs"]) >= 2 and d["steps"], d["kind"]
        else:
            assert rows[2]["answer"].startswith(("This made-up example shows none", "No, this is not a scam")), \
                d["kind"]
        assert rows[3]["answer"].strip(), d["kind"]


def test_scam_kinds_carry_their_notes():
    by_kind = {d["kind"]: d for d in every_kind()}
    for kind in ("grandparent_text", "boss_email", "agency_letter"):
        assert s.GIFT_NOTE in by_kind[kind]["notes"], kind
    assert s.ELDER_NOTE in by_kind["grandparent_text"]["notes"]
    assert s.VOICE_NOTE in by_kind["new_number_text"]["notes"]
    assert s.POPUP_NOTE in by_kind["tech_popup"]["notes"] and s.PADLOCK_NOTE in by_kind["fake_login"]["notes"]
    assert s.CODE_NOTE in by_kind["code_request_text"]["notes"]
    for kind in s.SCAM_KINDS:
        assert s.REPORT_NOTE in by_kind[kind]["notes"], kind
    assert set(s.KINDS) == set(by_kind) and not set(s.SCAM_KINDS) & set(s.SAFE_KINDS)


def test_generator_is_fixed_and_draws_every_frame():
    first = s.make_example(7)
    again = s.make_example(7)
    assert first[0] == again[0] and first[1] == again[1] and first[2] == again[2]
    frames = set()
    for d in every_kind():
        page = s.draw_example(d)
        assert page.width >= 700 and page.height >= 800, d["kind"]
        frames.add(d["frame"])
    assert frames == {"text", "chat", "email", "letter", "popup", "browser", "sign", "app", "warning", "notice"}
    entries = s.build_synthetic_scam_examples(3)
    assert sum(1 for _n, data, _r in entries if data) == 3 and len(entries) == 12


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_commons_answers():
    for category, answer in answers(p.PRIVACY_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
    said = dict(answers(p.PRIVACY_SPECS))
    assert p.ROUTER_NOTE in said["Wi-Fi routers and access points"]
    assert s.REPORT_NOTE in said["Phishing"] and p.RANSOM_NOTE in said["Ransomware"]
    assert p.KEY_NOTE in said["YubiKey"] and p.CAPTCHA_NOTE in said["ReCAPTCHA"]
    phishing = next(x for x in p.SCREENS if x[0] == "Phishing")
    assert phishing[3].search("Phishing email screenshot") and not phishing[3].search("Anti-Phishing Working Group "
                                                                                     "logo")


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    others = ""
    mine = {os.path.abspath(p.__file__), os.path.abspath(s.__file__)}
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) not in mine and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in p.PRIVACY_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads privacy_sources at its end
    import privacy_sources as k
    for name in ("VERIFY_NOTE", "REPORT_NOTE", "CODE_NOTE"):
        assert getattr(k, name) == getattr(s, name), name
    for name in ("KEY_NOTE", "ROUTER_NOTE", "CAMERA_NOTE", "BIO_NOTE", "SKIM_NOTE"):
        assert getattr(k, name) == getattr(p, name), name
    pack_answers = dict(answers(p.SECURITY_THINGS))
    for category, _q, answer, _deeper in k.PRIVACY_SA:
        assert answer == pack_answers[category], category
    assert all(reason for reason in k.PRIVACY_NOT_INCLUDED.values())


def test_wiring():
    assert set(LIMITS) == KEYS and len(KEYS) == 3
    assert KEYS <= set(build_packs.PACKS)
    assert set(p.PRIVACY_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (KEYS - set(p.PRIVACY_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import privacy_sources") == 2
    import sources
    import topics
    import privacy_sources as k
    listed = {x.key: x for x in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    topic = set(topics.find("privacy").keys)
    for key in KEYS:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert key in topic, key
        assert (key in no_making) == (key not in k.PRIVACY_PICTURE_MAKING_OK), key
    for x in k.PRIVACY_SOURCES:
        assert x.key in listed and x.key in topic, x.key
        assert x.key in KEYS or x.group != "permissive", x.key
    assert listed["privacy_commons_sa"].group == "share-alike"
    assert "synthetic_scam_examples" in no_making and "commons_privacy_screens" in no_making
    assert "commons_privacy_security" not in no_making
    order = [t.id for t in topics.TOPICS]
    assert order.index("privacy") == order.index("radio" if "radio" in order else "home") + 1
