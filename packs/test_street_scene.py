"""A self-test of the US and Canadian street scene parsers (packs/street_scene_packs.py and
training-kit/kit/street_scene_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - a category's place is read right ("... in Georgia (U.S. state)" -> "Georgia, USA", "... in Ontario" -> "Ontario,
    Canada"), and a photo of a worldwide category is kept only when something says it is in the USA or Canada;
  - the category rules give the right questions, and a traffic light filed under two colours, or a crosswalk under
    two styles, gets no answer to that question (never a guess);
  - a pedestrian signal's state is read only from plain words ("showing the walking person", "countdown at 8"),
    never from words that name both walk and don't walk, a sign or a symbol, or numbers that are not seconds;
  - crash, injury and protest words leave a file out; a file with no answer has none (it is set aside);
  - the FHWA gallery's state comes from its file name, and Flickr captions that are not road scenes are left out;
  - the Bosch traffic light answers say only the makers' labels, and frames with a hidden light are skipped;
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflow's known list and limit lines, in the
    kit's sources and never for picture-making; the kit's share-alike entry drops a file filed under two colours.

Run it from the repository's folder:   python3 -m pytest packs/test_street_scene.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import street_scene_packs as d  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"
REPO = os.path.dirname(HERE)


def test_category_places():
    """Places from category names, in the US and Canada."""
    assert d.category_place("Pedestrian signals in Georgia (U.S. state)", "USA") == "Georgia, USA"
    assert d.category_place("Pedestrian signals in New York (state)", "USA") == "New York, USA"
    assert d.category_place("Continental crosswalks in Ontario", "Canada") == "Ontario, Canada"
    assert d.category_place("Traffic lights at red state in Toronto", "Canada") == "Toronto, Canada"
    assert d.category_place("Crosswalks in the United States by city", "USA") == "USA"
    assert d.category_place("Pedestrian crossings in Washington, D.C. by style", "USA") == "Washington, D.C., USA"
    assert d.category_place("Tactile paving in train stations in the United States", "") == "USA"
    assert d.category_place("Street signs in New York City", "USA") == "New York City, New York, USA"
    assert d.category_place("Raised pedestrian crossings", "") == ""


def test_worldwide_categories_kept_only_in_north_america(monkeypatch):
    """A file of a worldwide category is kept only when a category or the camera says the USA or Canada."""
    monkeypatch.setattr(d, "PLACES", {"File:B.jpg": "Netherlands", "File:C.jpg": "USA", "File:D.jpg": "Mexico"})
    assert d.file_place("File:A.jpg", "Raised pedestrian crossings", ["Raised pedestrian crossings in Canada"], "") \
        == "Canada"
    assert d.file_place("File:A.jpg", "Raised pedestrian crossings", ["Speed humps in Ohio"], "") == "Ohio, USA"
    assert d.file_place("File:B.jpg", "Raised pedestrian crossings", [], "") == ""
    assert d.file_place("File:C.jpg", "Raised pedestrian crossings", [], "") == "USA"
    # A US topic whose photo's camera says Mexico: not kept.
    assert not d.in_north_america(d.file_place("File:D.jpg", "HAWK beacons", [], "USA"))
    t = d.topic("Raised pedestrian crossings", 0, "", d.CROSSWALK_KIND_Q)
    rows, _ = d.file_rows("File:B.jpg", "u", CREDIT, "", "", "Raised pedestrian crossings", [], t)
    assert rows is None


def test_rule_rows():
    """Category rules: crosswalk styles and colours; two colours or two styles give no answer to that question."""
    rows = d.rule_rows(["Continental crosswalks in Ohio", "Curb cuts in California"], d.CROSSWALK_KIND_Q)
    assert [r["question"] for r in rows] == [d.CROSSWALK_KIND_Q, d.CROSSWALK_Q, d.CURB_Q]
    assert rows[0]["answer"].startswith("It is a continental crosswalk")
    rows = d.rule_rows(["Traffic lights at red state in Ohio"], d.LIGHT_Q)
    assert rows == [{"question": d.LIGHT_Q, "answer": d.LIGHT_STATES["red"]}]
    rows = d.rule_rows(["Traffic lights at red state in Ohio", "Traffic lights at green state in Ohio"])
    assert all(r["question"] != d.LIGHT_Q for r in rows)
    rows = d.rule_rows(["Continental crosswalks in Ohio", "Ladder crosswalks in Ohio"])
    assert [r["question"] for r in rows] == [d.CROSSWALK_Q]
    # Signs about crossings are not crosswalks; the dark state says how drivers must treat it.
    assert d.rule_rows(["Pedestrian crossing signs in the United States"]) == []
    assert "all-way stop" in d.rule_rows(["Traffic lights at dark state in the United States"])[0]["answer"]
    assert d.rule_rows(["Pedestrian signal push buttons in Maryland"])[0]["question"] == d.BUTTON_Q
    assert "ticks" in d.rule_rows(["Audible traffic signals"])[0]["answer"]
    assert d.rule_rows(["Roundabouts in Michigan"])[0]["question"] == d.PLACE_Q
    assert d.rule_rows(["Interchange ramps in the United States"])[0]["answer"].startswith("This is a highway ramp")


def test_pedestrian_signal_state_never_guessed():
    """Only plain words give a state."""
    walk = d.ped_signal_state("Pedestrian signal showing the walking person, Main St.")
    assert walk.startswith("The pedestrian signal shows the walking person")
    assert d.ped_signal_state('Crosswalk signal displaying "WALK"').startswith("The pedestrian signal shows the walk")
    assert d.ped_signal_state("Pedestrian signal showing a red hand").startswith("The pedestrian signal shows the "
                                                                                 "raised hand")
    assert d.ped_signal_state("The orange hand is lit at the crosswalk").startswith("The pedestrian signal shows the "
                                                                                    "raised hand")
    count = d.ped_signal_state("Pedestrian countdown at 8 seconds")
    assert count.startswith("The pedestrian countdown shows 8: about 8 seconds are left")
    assert d.ped_signal_state("Pedestrian countdown signal reads 1.").startswith("The pedestrian countdown shows 1: "
                                                                                "about 1 second is left")
    for text in ("Walk and don't walk signals", "A sign showing walk symbol", "Countdown at 3 intersections on Main",
                 "Pedestrian countdown signals at 5th Avenue", "Countdown of 25 years",
                 "Pedestrian signal, countdown showing 12, walking person lit",
                 "Signal showing either the walking person or the hand", "Traffic light showing red", ""):
        assert d.ped_signal_state(text) == "", text


def test_file_rows():
    """A file's rows: the rules, the state from its own words (only for a signal or crossing), its caption."""
    t = d.topic("Pedestrian signals in the United States", 1, "USA", d.PED_SIGNAL_Q)
    rows, place = d.file_rows("File:Ped signal showing the walking person.jpg", "u", CREDIT,
                              "A pedestrian signal on Market Street at noon.", "",
                              "Pedestrian signals in California", ["Pedestrian signals in California"], t)
    assert place == "California, USA"
    assert [r["question"] for r in rows] == [d.PED_SIGNAL_Q, d.PED_STATE_Q, d.DESCRIBE_Q]
    assert all(r["place"] == "California, USA" and r["credit"] == CREDIT for r in rows)
    # A street sign file whose title says "showing walk" gets no signal state (no signal row to go with it).
    t = d.topic("Street signs in the United States by state", 1, "USA", d.SIGN_Q)
    rows, _ = d.file_rows("File:Sign showing the walking person.jpg", "u", CREDIT, "", "",
                          "Street signs in Ohio", [], t)
    assert [r["question"] for r in rows] == [d.SIGN_Q]
    # No rule and a camera-record caption: no rows (the builder sets it aside for a description).
    t = d.topic("Sidewalk obstructions", 1, "", d.WHAT_Q)
    rows, _ = d.file_rows("File:IMG_1234.jpg", "u", CREDIT, "Camera model Canon EOS", "", "Things in Ohio", [], t)
    assert rows == []


def test_harm_words():
    """Crashes, injuries and protests are left out of these everyday packs; plain street words are not."""
    for words in ("Car crash at intersection", "Ghost bike memorial", "Protest march on Main Street",
                  "Pedestrian injured in crosswalk"):
        assert d.HARM.search(words), words
    for words in ("Continental crosswalk at Main and 5th", "Traffic light at red", "Bus stop in winter"):
        assert not d.HARM.search(words), words


def test_fhwa():
    """The gallery's state from its file name; Flickr captions must be road scenes, not bridge parts or events."""
    assert d.gallery_place("File:GA 6 I20 I75 FHWA 1966 124.jpg") == "Georgia, USA"
    assert d.gallery_place("File:WS 5 I94 FHWA 1967 782.jpg") == "Wisconsin, USA"
    assert d.gallery_place("File:US 1 GEN FHWA 48 734.jpg") == "USA"
    caption = ("An aerial view of the interchange in Atlanta between Interstate Routes 20 and 75, with the skyline "
               "behind.")
    rows = d.fhwa_row("File:GA 6 I20 I75 FHWA 1966 124.jpg", caption, CREDIT, "Georgia, USA", True)
    assert [r["question"] for r in rows] == [d.DESCRIBE_Q, d.WHERE_Q] and rows[0]["answer"] == caption
    assert d.fhwa_row("File:Dowel Pocket FL (8451838010).jpg", "Dowel pocket in the bridge deck on a highway.",
                      CREDIT, "USA", False) == []
    assert d.fhwa_row("File:X.jpg", "The Administrator speaks at a press conference about highway safety.", CREDIT,
                      "USA", False) == []
    rows = d.fhwa_row("File:X.jpg", "A new high-visibility crosswalk and curb ramps at a busy intersection.", CREDIT,
                      "USA", False)
    assert [r["question"] for r in rows] == [d.DESCRIBE_Q]
    assert d.fhwa_row("File:X.jpg", "Bridge.", CREDIT, "USA", True) == []


def test_bosch_answers():
    """Bosch frames: labels only; a frame with a hidden light is skipped."""
    import sources  # noqa: F401 - the kit's table first, as the kit loads it (it then loads street_scene_sources)
    import street_scene_sources as k
    text = ("- boxes: []\n  path: ./rgb/train/a/1.png\n"
            "- boxes:\n  - {label: Red, occluded: false, x_max: 636.6, x_min: 632.2, y_max: 365.3, y_min: 346.3}\n"
            "  - {label: Red, occluded: false, x_max: 653.8, x_min: 649.2, y_max: 374.8,\n    y_min: 353.5}\n"
            "  - {label: RedLeft, occluded: false, x_max: 613.6, x_min: 608.8, y_max: 374.7, y_min: 354.0}\n"
            "  path: ./rgb/train/a/2.png\n"
            "- boxes:\n  - {label: Green, occluded: true, x_max: 615.7, x_min: 610.6, y_max: 358.6, y_min: 351.5}\n"
            "  path: ./rgb/train/a/3.png\n"
            "- boxes:\n  - {label: Yellow, occluded: false, x_max: 615.7, x_min: 610.6, y_max: 368.6, y_min: 351.5}\n"
            "  path: ./rgb/train/a/4.png\n")
    frames = k.bosch_frames(text)
    assert [f[0] for f in frames] == ["dataset_train_rgb/rgb/train/a/2.png", "dataset_train_rgb/rgb/train/a/4.png"]
    assert k.bosch_answer(frames[0][1]) == ("There are three traffic lights ahead: two show red and one shows a red "
                                            "left arrow.")
    assert k.bosch_answer(frames[1][1]) == "There is one traffic light ahead in the distance, and it shows yellow."
    assert k.bosch_answer([("Green", 0.5, 24), ("Green", 0.6, 30)]) == ("There are two traffic lights ahead: both "
                                                                        "show green.")
    assert k.bosch_answer([("off", 0.5, 40)]) == "There is one traffic light ahead, and it is switched off (dark)."


def test_wiring(monkeypatch):
    """Every pack is in PACKS and COMMONS_KEYS, the workflows know them, the kit lists them and never uses them for
    picture-making; the kit's share-alike entry drops a file under two colours."""
    keys = set(d.STREET_SCENE_PACKS)
    assert keys <= set(build_packs.PACKS)
    assert keys <= build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in d.STREET_SCENE_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import street_scene_sources") == 2
    import sources
    import street_scene_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed) and {"street_scene_commons_sa", "bosch_traffic_lights"} <= set(listed)
    assert listed["bosch_traffic_lights"].group == "noncommercial"
    assert listed["street_scene_commons_sa"].group == "share-alike"
    assert all(listed[key].group == "permissive" for key in keys)
    assert keys | {"street_scene_commons_sa", "bosch_traffic_lights"} <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert keys <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS)
    assert k.STREET_SCENE_PICTURE_MAKING_OK == set()
    made_up = [("street-sa-A.jpg", "u", {"question": k.LIGHT_Q, "answer": "The traffic light is red: traffic facing "
                                                                          "it must stop."}),
               ("street-sa-A.jpg", "u", {"question": k.LIGHT_Q, "answer": "The traffic light is green: ..."}),
               ("street-sa-B.jpg", "u", {"question": k.LIGHT_Q, "answer": "The traffic light is red: traffic facing "
                                                                          "it must stop."}),
               ("street-sa-Car_crash.jpg", "u", {"question": "Is there a crosswalk here?", "answer": "Yes."})]
    monkeypatch.setattr(k, "commons_sa_items", lambda *a, **kw: list(made_up))
    assert [i[0] for i in k.sa_items([], 10, 0, "street-sa")] == ["street-sa-B.jpg"]
