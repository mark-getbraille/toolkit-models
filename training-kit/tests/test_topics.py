"""Tests of topic add-ons (kit/topics.py, and how kit/train.py and kit/make_toolkit_addon.py use them): every topic's
collections exist, the everyday ("replay") share, the label and its licence rules (sensitive and personal-use
propagation), and the label in the result zip. Nothing here downloads anything or needs a graphics card; every
picture and row is made up."""

import json
import os
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit")
sys.path.insert(0, KIT)
sys.path.insert(0, HERE)
import sources  # noqa: E402
import topics  # noqa: E402

REPO_4B = "huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated"
REVISION_4B = "ce72a7c22aacb493fb94478de3bfbe834c61844a"
LABEL_KEYS = ["format", "topic_id", "title", "description", "base_model", "base_model_version", "licence_class",
              "sensitive", "picture_making", "kit_version", "trained"]
KNOWN = {s.key: s for s in sources.SOURCES}


# ----------------------------------------------------------------- the topics and their collections

def test_the_owners_ten_topics_are_there():
    assert [t.id for t in topics.TOPICS] == ["medicines", "drugs", "firearms", "food", "machines", "art",
                                             "documents", "nature", "nudity", "sexual"]
    for topic in topics.TOPICS:
        assert topic.title and topic.description.endswith(".") and len(topic.description) < 300
        assert topics.find(topic.id.upper()) is topic
    assert topics.find("nope") is None


def test_every_topic_key_is_a_collection_of_the_kit():
    """Every key a topic names is a collection in sources.py (no typing mistakes), named once."""
    for topic in topics.TOPICS:
        assert topic.keys, topic.id
        assert len(set(topic.keys)) == len(topic.keys), f"{topic.id} names a collection twice"
        missing = [k for k in topic.keys if k not in KNOWN]
        assert not missing, f"{topic.id}: {missing} are not collections of the kit"


def test_every_topic_has_open_collections():
    """Each topic can be trained with no box ticked (its open collections), except sexual content, which needs the
    content choices it turns on by itself."""
    for topic in topics.TOPICS:
        used, _left_out, missing = topics.topic_sources(topic, sources)
        assert used and not missing, topic.id
        assert all(s.group == "permissive" for s in used)


def test_topic_collections_fit_their_topic():
    """The packs land where they belong: pills in medicines, drug and firearm packs apart, nudes and erotic art only
    in the sensitive topics, and no medical-picture, graphic or sexual collection in an everyday topic."""
    by_id = {t.id: set(t.keys) for t in topics.TOPICS}
    assert {"taiwan_pills", "pharmassist", "c3pi_pills", "dailymed_human_labels"} <= by_id["medicines"]
    assert set(sources.DRUG_FIREARM_PACK_KEYS) <= by_id["drugs"] | by_id["firearms"]
    assert "commons_drugs" in by_id["drugs"] and "wikidata_firearms" in by_id["firearms"]
    assert by_id["sexual"] == {"erotic_art"}
    assert set(sources.ADULT_ART_PACK_KEYS) <= by_id["nudity"] | by_id["sexual"]
    for topic in topics.TOPICS:
        if topic.id in ("nudity", "sexual"):
            continue
        for key in topic.keys:
            assert KNOWN[key].content == "", (topic.id, key)


def test_only_the_sensitive_topics_are_sensitive():
    assert [t.id for t in topics.TOPICS if t.sensitive] == ["nudity", "sexual"]
    assert [t.id for t in topics.TOPICS if t.personal_only] == ["sexual"]
    assert topics.find("nudity").needs == ("nudity",)
    assert set(topics.find("sexual").needs) == {"nudity", "sexual"}


def test_a_topic_turns_on_the_content_it_needs():
    """Training the nudity topic chooses art with nudity by itself; sexual content also adult sexual content."""
    used, _l, _m = topics.topic_sources(topics.find("nudity"), sources)
    assert {s.key for s in used} == {"art_nudes", "museum_art_nudes", "nude_photo_studies"}
    used, _l, _m = topics.topic_sources(topics.find("sexual"), sources)
    assert [s.key for s in used] == ["erotic_art"]
    assert topics.content_choices(topics.find("food"), {"with_medical": True}) == {
        "with_nudity": False, "with_medical": True, "with_sexual": False, "with_graphic": False,
        "with_noncommercial": False, "with_research": False}


def test_personal_use_collections_need_their_boxes():
    """A topic's share-alike, non-commercial and research-only collections are left out until their box is ticked."""
    food = topics.find("food")
    used, left_out, _m = topics.topic_sources(food, sources)
    assert "openfoodfacts" in {s.key for s in left_out} and "food101" in {s.key for s in left_out}
    used, left_out, _m = topics.topic_sources(food, sources, with_wikipedia=True, choices={"with_research": True})
    assert {"openfoodfacts", "food101"} <= {s.key for s in used} and not left_out


def test_the_everyday_mix_is_open_everyday_photos():
    for key in topics.EVERYDAY_KEYS:
        assert KNOWN[key].group == "permissive" and KNOWN[key].content == "", key
    documents = topics.find("documents")
    assert "textvqa" not in topics.everyday_keys(documents, sources)        # never the topic's own collections
    assert "docci" in topics.everyday_keys(documents, sources)


# ----------------------------------------------------------------- the everyday ("replay") share

def test_the_replay_share_and_its_limits():
    assert topics.REPLAY_DEFAULT == 0.15
    assert topics.check_replay(0.15) == 0.15 and topics.check_replay(15) == 0.15
    assert topics.check_replay(0) == 0.0 and topics.check_replay(40) == 0.4 and topics.check_replay("0.4") == 0.4
    for wrong in (0.41, 41, -1, "a lot", None):
        with pytest.raises(ValueError, match="0 to 40 percent|from 0 to 40"):
            topics.check_replay(wrong)


def test_the_replay_share_is_its_share_of_the_whole_mix():
    topic_rows = [{"picture": f"t{i}.jpg", "source": "eggs"} for i in range(850)]
    everyday = [{"picture": f"e{i}.jpg", "source": "docci"} for i in range(1000)]
    rows, added = topics.mix(topic_rows, everyday, 0.15)
    assert added == 150 and len(rows) == 1000
    assert sum(1 for r in rows if r.get("replay")) / len(rows) == pytest.approx(0.15)
    assert not any(r.get("replay") for r in rows if r["source"] == "eggs")
    assert topics.mix(topic_rows, everyday, 0.15) == (rows, added)          # the same every time (a restart)
    rows, added = topics.mix(topic_rows, everyday, 0.40)
    assert added / len(rows) == pytest.approx(0.40, abs=0.001)
    assert topics.mix(topic_rows, everyday, 0) == (topics.mix(topic_rows, [], 0)[0], 0)
    rows, added = topics.mix(topic_rows, everyday[:20], 0.15)                # not enough everyday pictures
    assert added == 20 and len(rows) == 870


def test_topic_rows_holds_back_the_test_pictures(tmp_path, monkeypatch):
    """train.topic_rows: the topic's training pictures with the everyday share, the topic's test pictures marked
    "topic" and the everyday ones (at most 100) marked "everyday"; nothing kept back is trained on."""
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import train
    monkeypatch.setattr(train, "LOG", str(tmp_path / "log.txt"))
    calls = []

    def fake_prepare(work, state, size, with_wikipedia, keys=None, name=None, **content):
        """Made-up rows for each collection asked for: 50 for training and 5 for the test."""
        calls.append((name, sorted(keys), content))
        rows = [{"picture": f"{k}-{i}.jpg", "source": k, "question": "q", "answer": "a"} for k in sorted(keys)
                for i in range(55)]
        return [r for r in rows if not r["picture"].endswith(("-50.jpg", "-51.jpg", "-52.jpg", "-53.jpg",
                                                              "-54.jpg"))], \
            [r for r in rows if r["picture"].endswith(("-50.jpg", "-51.jpg", "-52.jpg", "-53.jpg", "-54.jpg"))]
    monkeypatch.setattr(train, "prepare_data", fake_prepare)
    topic = topics.find("drugs")
    content = topics.content_choices(topic)
    rows, test, added = train.topic_rows(str(tmp_path), None, topic, "normal", False, 0.15, content)
    assert calls[0][0] == "topic-drugs" and calls[0][1] == sorted(
        ["commons_drugs", "commons_drug_paraphernalia", "commons_cbp_seizures", "cdc_phil_drugs"])
    assert calls[1][0] == "everyday" and "docci" in calls[1][1]
    assert len(rows) - added == 200 and added == round(200 * 0.15 / 0.85)
    assert {r["topic_part"] for r in test} == {"topic", "everyday"}
    assert sum(1 for r in test if r["topic_part"] == "topic") == 20
    assert sum(1 for r in test if r["topic_part"] == "everyday") == 50
    assert not {r["picture"] for r in rows} & {r["picture"] for r in test}
    calls.clear()
    rows, test, added = train.topic_rows(str(tmp_path), None, topic, "normal", False, 0.0, content)
    assert added == 0 and len(calls) == 1 and {r["topic_part"] for r in test} == {"topic"}


def importable_train():
    """True when train.py can be imported here (it needs psutil for its computer-use lines)."""
    import importlib.util
    return importlib.util.find_spec("psutil") is not None


# ----------------------------------------------------------------- the label and its licence

def test_licence_is_open_for_open_collections():
    food = topics.find("food")
    assert topics.licence_class(food, ["eggs", "beef", "docci"], sources) == "open"
    assert topics.licence_class(food, ["eggs", "openfoodfacts"], sources) == "open"     # share-alike is open


@pytest.mark.parametrize("change", [
    {"collections": ["eggs", "food101"]},                     # a research-only collection learned from
    {"collections": ["eggs", "inaturalist_us_nc"]},           # a non-commercial one
    {"personal_choice": True},                                # a personal-use box ticked
    {"review_used": True},                                    # checked review pictures
    {"own_used": True},                                       # the person's own pictures
    {"sexual_used": True},                                    # adult sexual content
])
def test_personal_use_propagates_to_the_label(change):
    food = topics.find("food")
    collections = change.pop("collections", ["eggs"])
    assert topics.licence_class(food, collections, sources, **change) == "personal use only"


def test_sexual_content_is_always_personal_and_sensitive():
    sexual = topics.find("sexual")
    assert topics.licence_class(sexual, ["erotic_art"], sources) == "personal use only"
    assert topics.is_sensitive(sexual) and topics.is_sensitive(topics.find("nudity"))
    assert topics.licence_class(topics.find("nudity"), ["art_nudes"], sources) == "open"
    assert topics.licence_class(topics.find("nudity"), ["art_nudes", "princeton_art_personal"], sources) == \
        "personal use only"


def test_sensitive_content_propagates_to_the_label():
    food = topics.find("food")
    assert not topics.is_sensitive(food) and not topics.is_sensitive(food, {"", "medical"})
    for tag in ("nudity", "intimate", "sexual", "graphic"):
        assert topics.is_sensitive(food, {"", tag})


def test_the_label_has_the_agreed_fields(tmp_path):
    import datetime
    label = topics.make_label(topics.find("firearms"), REPO_4B, REVISION_4B, "open", False,
                              datetime.date(2026, 11, 20))
    assert list(label) == LABEL_KEYS
    assert label["topic_id"] == "firearms" and label["title"] == "Firearms and accessories"
    assert label["base_model"] == REPO_4B and label["base_model_version"] == REVISION_4B
    assert label["licence_class"] == "open" and label["sensitive"] is False and label["picture_making"] is False
    assert label["kit_version"] == topics.KIT_VERSION and label["trained"] == "2026-11-20"
    path = tmp_path / topics.LABEL_FILE
    topics.write_label(str(path), label)
    assert json.loads(path.read_text(encoding="utf-8")) == label
    with pytest.raises(ValueError):
        topics.make_label(topics.find("food"), REPO_4B, REVISION_4B, "free for all", False)


def test_the_label_format_is_documented():
    """The toolkit reads the label, so every field is described in TOPIC ADD-ON LABEL FORMAT.txt."""
    path = os.path.join(os.path.dirname(KIT), "TOPIC ADD-ON LABEL FORMAT.txt")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for key in LABEL_KEYS:
        assert f'"{key}"' in text, key
    assert '"personal use only"' in text and '"open"' in text and topics.LABEL_FILE in text
    for topic in topics.TOPICS:
        assert topic.id in text


def test_the_score_is_said_in_plain_words():
    before = [{"topic_part": "topic", "score": 0.2}] * 10 + [{"topic_part": "everyday", "score": 0.3}] * 4
    after = [{"topic_part": "topic", "score": 0.3}] * 10 + [{"topic_part": "everyday", "score": 0.25}] * 4
    lines = topics.score_lines(topics.find("food"), topics.score_summary(before, after))
    text = "\n".join(lines)
    assert lines[0] == "Topic add-on: Food and packaged goods"
    assert "10 test pictures kept back" in text and "it got better at this topic" in text
    assert "everyday description got worse; next time raise the everyday share" in text


# ----------------------------------------------------------------- the label in the result zip

def test_the_label_goes_into_the_zip_and_its_toolkit_folder(tmp_path, monkeypatch):
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import make_toolkit_addon as mta
    import train
    from test_toolkit_addon import GOOD_SETTINGS, good_tensors, make_kit, write_gguf
    monkeypatch.setattr(train, "HERE", str(tmp_path))
    monkeypatch.setattr(train, "LOG", str(tmp_path / "training-log.txt"))
    (tmp_path / "training-log.txt").write_text("log\n")
    final = tmp_path / "work" / "adapter-4b-topic-sexual" / "final"
    final.mkdir(parents=True)
    (final / "adapter_config.json").write_text("{}")
    report = tmp_path / "report.txt"
    report.write_text("report")
    monkeypatch.setattr(mta, "add_to_zip", lambda *a, **k: (_ for _ in ()).throw(mta.AddonError("later")))
    label = topics.make_label(topics.find("sexual"), REPO_4B, REVISION_4B, "personal use only", True)
    info = {"model": REPO_4B, "revision": REVISION_4B, "run": "4b-topic-sexual", "collections": ["erotic_art"],
            "share_alike": False, "topic": "sexual", "label": label, "sexual_used": True}
    path = train.package("4b", str(final), str(report), info, "-topic-sexual")
    with zipfile.ZipFile(path) as z:
        assert json.loads(z.read("addon-label.json")) == label
        assert "PERSONAL-USE-ONLY.txt" in z.namelist()
    # make_toolkit_addon copies the label beside the toolkit's own file.
    kit, result = make_kit(tmp_path / "kit")
    with zipfile.ZipFile(result, "a") as z:
        z.writestr("addon-label.json", topics.label_text(label))
    gguf = tmp_path / "made.gguf"
    write_gguf(gguf, GOOD_SETTINGS, good_tensors())
    monkeypatch.undo()
    mta.add_to_zip(result, str(kit / "work"), gguf=str(gguf))
    with zipfile.ZipFile(result) as z:
        assert json.loads(z.read("toolkit/addon-label.json")) == label
        assert json.loads(z.read("addon-label.json")) == label


@pytest.mark.parametrize("argv, words", [
    (["--topic", "cooking"], "There is no topic called cooking"),
    (["--topic", "food", "--continue"], "never as a follow-up"),
    (["--topic", "food", "--topic-replay", "0.5"], "0 to 40 percent"),
])
def test_wrong_topic_choices_stop_in_plain_words(tmp_path, monkeypatch, argv, words):
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import train
    monkeypatch.setattr(train, "LOG", str(tmp_path / "training-log.txt"))
    with pytest.raises(SystemExit):
        train.main(argv)
    assert words in (tmp_path / "training-log.txt").read_text(encoding="utf-8")


def test_topic_list(capsys):
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import train
    assert train.main(["--topic", "list"]) == 0
    out = capsys.readouterr().out
    assert "food: Food and packaged goods" in out and "sexual: Sexual content (sensitive)" in out
