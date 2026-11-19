"""A self-test of the drug, paraphernalia and firearm parsers (packs/drug_firearm_packs.py and
training-kit/kit/drug_firearm_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - a drug or paraphernalia file is left out when its words name someone using a drug, an overdose, a child, harm,
    a drawing or chart, or (in these things-only packs) a person; "smoking pipe" and "vaping device" are things, not
    someone smoking or vaping;
  - drug answers end with the drug line, gun answers with the gun line, accessory answers with no line, and a
    caption that reads like instructions or names making a suppressor is not learnt;
  - CBP titles become "This is a US Customs and Border Protection photo of a drug seizure: ...", without the Flickr
    number; titles about arrests, smugglers, money or tunnels are left out;
  - maker categories become "This looks like a Smith & Wesson revolver."; names that are not a maker's are skipped;
  - gun files are left out for firing, pointing at someone, people, toys and conversion parts;
  - PHIL records must be public domain and show a drug, not a patient or a laboratory;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS, in the workflow's known list and
    limit lines, in the kit's sources and never for picture-making; the kit's share-alike filter drops the same
    words.

Run it from the repository's folder:   python3 -m pytest packs/test_drug_firearm.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import drug_firearm_packs as d  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"
REPO = os.path.dirname(HERE)


def made_up(title, caption="", cats=""):
    """A made-up Commons file as service_packs.commons_files gives it."""
    return {"title": title, "url": "https://upload.wikimedia.org/x.jpg", "credit": CREDIT, "caption": caption,
            "year": 0, "place": "", "cats": cats}


def test_drug_files_left_out_by_their_words():
    """Use, overdose, children, harm, drawings and people leave a drug file out; plain photos are kept."""
    kept = [made_up("File:Ecstasy pills seized.jpg", "Ecstasy tablets with a logo.", "Ecstasy tablets"),
            made_up("File:Briar smoking pipe.jpg", "A briar smoking pipe on a table.", "Smoking pipes"),
            made_up("File:Vaping device.jpg", "A refillable vaping device.", "Electronic cigarettes; Vaping")]
    for f in kept:
        assert d.drug_left_out(f) == "", f["title"]
    dropped = [made_up("File:Man smoking a joint.jpg"), made_up("File:Heroin injection.jpg"),
               made_up("File:Fentanyl overdose.jpg"), made_up("File:Children and vapes.jpg"),
               made_up("File:Cocaine chemical structure.png"), made_up("File:Bong.jpg", "A woman holds a bong."),
               made_up("File:Pipe.jpg", "Pipe smoker at a cafe.")]
    for f in dropped:
        assert d.drug_left_out(f), f["title"]
    # People are allowed only where a pack says so (and use words still leave the file out).
    assert d.drug_left_out(made_up("File:Officers with seized cocaine.jpg"), people_ok=True) == ""
    assert d.drug_left_out(made_up("File:Officers with seized cocaine.jpg"))


def test_rows_and_lines():
    """Drug rows end with DRUG_LINE, gun rows with GUN_LINE; instructions and making captions are not learnt."""
    f = made_up("File:Ecstasy tablets.jpg", "Pink ecstasy tablets stamped with a crown.")
    rows = d.drug_rows(f, *[d.DRUG_CATEGORIES["Ecstasy tablets"][i] for i in (0, 1, 3)])
    assert [r["question"] for r in rows] == [d.ASK_WHAT, d.ASK_DESCRIBE]
    assert all(r["answer"].endswith(d.DRUG_LINE) for r in rows)
    assert rows[0]["answer"].startswith("These look like ecstasy tablets")
    f = made_up("File:Speedloader.jpg", "How to load a speedloader, step by step.")
    rows = d.accessory_rows(f, *[d.ACCESSORIES["Speedloaders"][i] for i in (0, 1, 3)])
    assert len(rows) == 1 and rows[0]["answer"].endswith("at once.")
    f = made_up("File:Suppressor.jpg", "A suppressor next to a solvent trap kit.")
    assert d.accessory_rows(f, *[d.ACCESSORIES["Firearm silencers"][i] for i in (0, 1, 3)]) == []
    f = made_up("File:Colt Python revolver.jpg", "A Colt Python revolver with a six-inch barrel.", "Revolvers")
    rows = d.gun_rows(f, *[d.KINDS["Revolvers"][i] for i in (0, 1, 3)])
    assert len(rows) == 2 and all(r["answer"].endswith(d.GUN_LINE) for r in rows)


def test_gun_files_left_out():
    """Firing, pointing at people, people, toys and conversion parts leave a gun file out."""
    for title, caption in (("File:Firing a revolver.jpg", ""), ("File:Revolver.jpg", "Pointing a gun at a man."),
                           ("File:Police officer with pistol.jpg", ""), ("File:Toy revolver.jpg", ""),
                           ("File:Glock with auto sear.jpg", ""), ("File:Shotgun.jpg", "A hunter with his shotgun."),
                           ("File:Rifle at crime scene.jpg", "")):
        assert d.gun_left_out(made_up(title, caption)), title
    assert d.gun_left_out(made_up("File:Smith & Wesson Model 10.jpg", "A Smith & Wesson Model 10 revolver.")) == ""
    assert d.accessory_left_out(made_up("File:Gun cleaning kit.jpg", "A gun cleaning kit with rods and brushes.")) \
        == ""
    assert d.accessory_left_out(made_up("File:Holster.jpg", "A soldier wearing a holster."))


def test_cbp_titles():
    """CBP titles name a drug seizure; arrests, smugglers, money and tunnels are left out; the answer is the title."""
    titles = ["File:Douglas CBP Officers Seize 176 Pounds of Marijuana (15355631991).jpg",
              "File:San Luis CBP Nabs Smuggler with $67K of Meth (14241725992).jpg",
              "File:Otay Drug Tunnel Discovery (26264254626).jpg",
              "File:Dulles CBP Seizes $150k in Unreported Currency (36664075374).jpg",
              "File:2014 East Coast Trade Symposium (13080753345).jpg",
              "File:CBP Officers Seize 95 lbs of Liquid Methamphetamine at Eagle Pass (23837059332).jpg"]
    assert d.cbp_titles(titles) == [titles[0], titles[5]]
    rows = d.cbp_rows(made_up(titles[5], "CBP officers found liquid methamphetamine in a car's fuel tank."))
    assert rows[0]["answer"] == ("This is a US Customs and Border Protection photo of a drug seizure: CBP Officers "
                                 "Seize 95 lbs of Liquid Methamphetamine at Eagle Pass.")
    assert rows[0]["place"] == "USA" and rows[1]["question"] == d.ASK_DESCRIBE
    assert d.cbp_rows(made_up(titles[0], "A child was in the car.")) == []


def test_maker_answers():
    """Maker categories become a maker and kind; names that are not a maker's are skipped."""
    assert d.maker_answer("Smith & Wesson revolvers", "revolver") == "This looks like a Smith & Wesson revolver."
    assert d.maker_answer("Glock", "pistol") == "This looks like a Glock pistol."
    assert d.maker_answer("Harrington & Richardson Firearms", "revolver") == \
        "This looks like a Harrington & Richardson revolver."
    assert d.maker_answer("Izh shotguns", "shotgun") == "This looks like an Izh shotgun."
    for name in ("Eusebio Zuloaga's gunshot", "Revolvers made by Manufacture d'Armes de Saint-Étienne (France)",
                 "Nagant wz. NG 30", "Joslyn Army revolver"):
        assert d.maker_answer(name, "revolver") == "", name


def test_phil_records():
    """PHIL records: public domain, a drug named, not a patient, laboratory or chart, nobody using."""
    good = {"public": True, "caption": "This image depicts a still life of drug paraphernalia, including a pipe."}
    assert d.phil_drug_left_out(good) == ""
    for r in ({"public": False, "caption": good["caption"]},
              {"public": True, "caption": "Lesions on a patient's forearm caused by injecting heroin."},
              {"public": True, "caption": "A laboratory technician pipetting e-cigarette liquid."},
              {"public": True, "caption": "A view of a cigarette beetle larva."}):
        assert d.phil_drug_left_out(r), r["caption"]


def test_wiring():
    """Every pack is in PACKS, the Commons ones in COMMONS_KEYS, the workflows know them, the kit lists them and never
    uses them for picture-making."""
    keys = set(d.DRUG_FIREARM_PACKS)
    assert keys <= set(build_packs.PACKS)
    assert keys - {"cdc_phil_drugs"} <= build_packs.COMMONS_KEYS
    assert "cdc_phil_drugs" not in build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in d.DRUG_FIREARM_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import drug_firearm_sources") == 2
    import sources
    import drug_firearm_sources as k
    listed = {s.key for s in sources.SOURCES}
    assert keys <= listed and "drug_firearm_commons_sa" in listed
    assert keys | {"drug_firearm_commons_sa"} <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert {"commons_cbp_seizures", "cdc_phil_drugs"} <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS)
    assert k.DRUG_FIREARM_PICTURE_MAKING_OK == set()
    assert not k.left_out("drugfire-sa-Briar smoking pipe This looks like a smoking pipe.")
    assert k.left_out("drugfire-sa-Man smoking a joint This looks like a joint.")
    assert k.left_out("drugfire-sa-Solvent trap kit This looks like a suppressor (a silencer).")
