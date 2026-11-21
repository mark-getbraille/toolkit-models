"""A self-test of the picture category gap packs (packs/gaps_oi_packs.py, packs/gaps_collection_packs.py and
training-kit/kit/gaps_sources.py), with made-up labels and records only: nothing is downloaded from the internet.

It checks that:
  - Open Images rows say only what the labels say: "I can see a urinal and a hand dryer." for confirmed labels, a
    "No, I can't see ..." only for a label people checked and found absent, the seafood allergy note, child rows
    marked, nudity left out, swimwear with a child left out;
  - the cards pack answers only what kind of card it is, and never asks about a real person's identity papers (only
    a photo whose own title says "specimen" or "sample");
  - no Open Images label of these packs is asked by another pack already;
  - museum records give "Tell me about this museum object." from the record only; nudes and erotica and works the
    kit's art_institute collection already has are left out; Cleveland needs CC0;
  - WordPress photos need alt text of six words or more; Library of Congress maps must be from 1930 or before or by
    the US government; Europeana records must be English and CC0, PDM or CC BY; PHIL records must be public domain,
    name the topic and show no patient or microscope picture;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS, in the workflows' known list and
    limit lines, in the kit's sources (open ones "permissive"), the people packs never for picture-making, the
    guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_gaps.py
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import gaps_collection_packs as c  # noqa: E402

REPO = os.path.dirname(HERE)


def rows_of(labels, groups, title=""):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1), title)


# ----------------------------------------------------------------- Open Images rows

def test_confirmed_labels_are_named():
    rows = rows_of({"Urinal": 1, "Hand dryer": 1, "Bidet": 0}, g.PUBLIC_HOME)
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What washroom fixtures are in this picture?"] == "I can see a urinal and a hand dryer."
    assert said["Is there a bidet in this picture?"] == "No, I can't see a bidet in this picture."
    assert any(a.startswith("Yes, there is a") for a in said.values())


def test_nothing_without_a_confirmed_label():
    assert rows_of({"Bidet": 0, "Urinal": None}, g.PUBLIC_HOME) == []
    assert rows_of({"Person": 1}, g.PUBLIC_HOME) == []


def test_plural_and_mass_words_read_well():
    rows = rows_of({"Pancake": 0, "Bagel": 1}, g.FOOD_MORE)
    no = [r for r in rows if r["answer"].startswith("No")][0]
    assert no["question"] == "Are there any pancakes in this picture?"
    assert no["answer"] == "No, I can't see any pancakes in this picture."
    assert g.a_thing("luggage") == "any luggage" and g.a_thing("a urinal") == "a urinal"
    assert g.is_there("octopus") == "Is there any octopus in this picture?"


def test_seafood_note_and_child_marks():
    rows = rows_of({"Lobster": 1, "Crab": 1, "Girl": 1}, g.FOOD_MORE)
    first = rows[0]
    assert first["answer"] == f"I can see lobster and crab. {g.SEAFOOD_NOTE}"
    assert all(r.get("child") for r in rows)


def test_left_out_labels():
    assert rows_of({"Swimming pool": 1, "Nudity": 1}, g.PUBLIC_HOME) == []
    assert rows_of({"Swimming pool": 1, "Swimwear": 1, "Boy": 1}, g.PUBLIC_HOME) == []
    assert rows_of({"Swimming pool": 1, "Swimwear": 1}, g.PUBLIC_HOME)


def test_cards_only_say_the_kind():
    rows = rows_of({"Business card": 1}, g.CARDS)
    assert rows[0]["answer"] == "It looks like a business card. I can only say what kind it is, not what it says."
    # A real person's papers: never asked about; a specimen is.
    assert rows_of({"Passport": 1}, g.CARDS, "My new passport") == []
    assert rows_of({"Identity document": 1}, g.CARDS, "Specimen ID card")[0]["answer"].startswith(
        "It looks like an identity document (a sample)")
    assert not any("Is there a passport" in r["question"] for r in rows_of({"Passport": 1}, g.CARDS, "sample"))
    assert not any("identity" in r["question"] for r in rows_of({"Postcard": 1, "Identity document": 0}, g.CARDS))


def test_no_label_is_asked_twice():
    """Every label of the gap packs is new: no other Open Images pack asks about it, and no two gap packs share one."""
    import everyday_packs
    import home_packs
    import food_packs
    import culture_packs
    elsewhere = set(everyday_packs.OI_HOME) | set(food_packs.OI_FOOD) | set(culture_packs.OI_CULTURE)
    for group in home_packs.OI_GROUP_QUESTIONS:
        elsewhere |= set(group[0])
    import things_packs, packaged_goods_packs, med_vet_packs, people_activity_packs, disability_packs  # noqa: E401
    import world_life_packs, street_scene_packs  # noqa: E401
    for mod in (things_packs, packaged_goods_packs, med_vet_packs, people_activity_packs, disability_packs,
                world_life_packs, street_scene_packs):
        for name, value in vars(mod).items():
            if name.startswith("OI_") and isinstance(value, dict):
                elsewhere |= set(value)
    packs = [g.PUBLIC_HOME, g.OUTINGS, g.FOOD_MORE, g.CARDS]
    for groups in packs:
        assert not g.gap_labels(groups) & elsewhere, g.gap_labels(groups) & elsewhere
        for group in groups:
            assert group["question"].endswith("?") and all(w and w == w.strip() for w in group["things"].values())
    for i, a in enumerate(packs):
        for b in packs[i + 1:]:
            assert not g.gap_labels(a) & g.gap_labels(b)


# ----------------------------------------------------------------- museums

def test_aic_records():
    record = {"id": 7, "title": "Teapot", "is_public_domain": True, "image_id": "abc", "artwork_type_title": "Vessel",
              "artist_display": "Paul Revere (American, 1735-1818)", "date_display": "1782", "medium_display": "Silver",
              "subject_titles": ["tea", "drinking vessels"], "thumbnail": {"alt_text": "A work made of silver."},
              "place_of_origin": "Boston"}
    name, picture, rows, described = c.aic_item(record)
    assert name == "aicg-7.jpg" and picture.endswith("/abc/full/843,/0/default.jpg") and described
    assert rows[0]["answer"] == ("Teapot: a vessel by Paul Revere, 1782, in silver. The museum lists these subjects: "
                                 "tea, drinking vessels.")
    assert len(rows) == 1                       # the stock alt text is not used
    assert c.aic_item(dict(record, thumbnail={"alt_text": "Silver teapot with a curved spout and a wooden handle."})) \
        is None                                 # real alt text: the kit's art_institute collection has it
    assert c.aic_item(dict(record, is_public_domain=False)) is None
    assert c.aic_item(dict(record, title="Reclining Nude")) is None
    assert c.aic_item(dict(record, subject_titles=[]))[3] is False
    with_text = c.aic_item(dict(record, subject_titles=[], description="<p>Revere made this teapot for a merchant.</p>"))
    assert with_text[2][0]["answer"].endswith("Revere made this teapot for a merchant.") and with_text[3]
    assert "description CC BY 4.0" in with_text[2][0]["credit"]


def test_cleveland_records():
    record = {"id": 9, "title": "Lace Towel End", "share_license_status": "CC0", "type": "Embroidery",
              "creation_date": "c. 1700s", "culture": ["Russia, Nizhny-Novgorod province"], "technique": "linen",
              "description": "This Russian lace panel was likely used to embellish the end of a bathing towel.",
              "url": "https://clevelandart.org/art/1931.110", "images": {"web": {"url": "https://x/web.jpg"}}}
    name, picture, rows, described = c.cma_item(record)
    assert name == "cmag-9.jpg" and picture == "https://x/web.jpg" and described
    assert rows[0]["answer"] == ("Lace Towel End: an embroidery, c. 1700s, in linen. It is from Russia. This Russian "
                                 "lace panel was likely used to embellish the end of a bathing towel.")
    assert c.cma_item(dict(record, share_license_status="Copyrighted")) is None
    assert c.cma_item(dict(record, description="An erotic print.")) is None


# ----------------------------------------------------------------- WordPress, maps, Europeana, PHIL

def test_wordpress_photos():
    photo = {"id": 3, "link": "https://wordpress.org/photos/photo/x/",
             "content": {"rendered": "<p>A small, round pomegranate with brown blemishes hanging from a branch.</p>"},
             "_links": {"author": [{"href": "https://wordpress.org/photos/wp-json/wporg/v1/users/someone"}]},
             "class_list": ["photo_category-food-drink"],
             "_embedded": {"wp:featuredmedia": [{"media_details": {"sizes": {"large": {"source_url": "https://pd/l.jpg"}}}}]}}
    name, picture, rows = c.wp_item(photo)
    assert (name, picture) == ("wpphoto-3.jpg", "https://pd/l.jpg")
    assert rows[0]["answer"] == "A small, round pomegranate with brown blemishes hanging from a branch."
    assert rows[0]["credit"].startswith("Photo by WordPress.org user someone, WordPress Photo Directory, CC0")
    assert c.wp_item(dict(photo, content={"rendered": "<p>Pomegranate.</p>"})) is None


def test_maps_must_be_public_domain():
    old = {"date": "1920-10", "item": {"created_published": "Sanborn Map Company, Oct 1920"}, "title": "Sanborn Map"}
    assert c.map_free(old) == (True, "published in 1920")
    usgs = {"date": "1976", "item": {"created_published": ["Reston, Va. : U.S. Geological Survey, 1980."]}}
    assert c.map_free(usgs) == (True, "made by the US government")
    dated = c.map_rows({"title": "Map of a cavalry engagement", "date": "1862", "item": {"created_published": "1862."}}, "c")
    assert dated[0]["answer"] == "This is a map: Map of a cavalry engagement. The Library of Congress dates it 1862."
    unknown = c.map_rows({"title": "Map of El Paso", "date": "1893", "item": {"created_published": "[S.l. : s.n., 1893-4]."}}, "c")
    assert "Published" not in unknown[0]["answer"]
    assert c.map_free({"date": "1985", "item": {"created_published": "Rand McNally"}})[0] is False
    rows = c.map_rows(dict(old, title="Sanborn Fire Insurance Map from Nashua, Valley County, Montana."), "credit")
    assert rows[0]["answer"] == ("This is a map: Sanborn Fire Insurance Map from Nashua, Valley County, Montana. The "
                                 "Library of Congress dates it 1920-10. Published by Sanborn Map Company, Oct 1920.")


def test_europeana_records():
    record = {"id": "/1/abc", "rights": ["http://creativecommons.org/publicdomain/zero/1.0/"], "language": ["en"],
              "title": ["Design Sketch, Coat Dress"], "edmIsShownBy": ["https://x/1.jpg"], "dataProvider": ["Museum"],
              "dcDescription": ["Sketch on board. A full-length, long-sleeved double-breasted coat-dress."]}
    name, picture, rows = c.europeana_item(record, "fashion")
    assert rows[0]["answer"].startswith("Design Sketch, Coat Dress. Sketch on board.")
    assert c.europeana_item(dict(record, language=["nl"]), "fashion") is None
    assert c.europeana_item(dict(record, rights=["http://creativecommons.org/licenses/by-sa/4.0/"]), "fashion") is None


def test_phil_records():
    good = {"public": True, "caption": "This photograph depicts a woman washing her hands with soap and water."}
    assert c.phil_kept(good, c.PHIL_BEHAVIOUR_WORDS) == ""
    assert c.phil_kept(dict(good, public=False), c.PHIL_BEHAVIOUR_WORDS)
    assert c.phil_kept({"public": True, "caption": "Lesions on a patient's hands."}, c.PHIL_BEHAVIOUR_WORDS)
    assert c.phil_kept({"public": True, "caption": "Marijuana and smoking implements."}, c.PHIL_BEHAVIOUR_WORDS)
    assert c.phil_kept({"public": True, "caption": "A view of a lake with a harmful algal bloom."},
                       c.PHIL_ALGAE_WORDS) == ""
    assert c.phil_kept({"public": True, "caption": "A micrograph of a cyanobacteria bloom."}, c.PHIL_ALGAE_WORDS)
    assert c.phil_kept({"public": True, "caption": "Illustration of algae blooming, Plate 4."}, c.PHIL_ALGAE_WORDS)


# ----------------------------------------------------------------- wiring

def test_wiring():
    keys = set(g.OI_GAPS_PACKS) | set(c.GAP_COLLECTION_PACKS)
    limits = dict(g.OI_GAPS_LIMITS, **c.GAP_COLLECTION_LIMITS)
    assert keys == set(limits) and len(keys) == 13
    assert keys <= set(build_packs.PACKS)
    assert set(c.GAP_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(c.GAP_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in limits.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import gaps_sources") == 2
    import sources
    import topics
    import gaps_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed) and all(listed[key].group == "permissive" for key in keys)
    assert listed["gaps_rocks_commons_sa"].group == "share-alike"
    people = set(c.GAP_PEOPLE_PACKS) | set(g.OI_GAPS_PACKS)
    assert people <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS) and people <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert not {"loc_maps", "cdc_phil_algae", "commons_rocks_fossils", "commons_nara_aerial"} & \
        set(sources.NOT_FOR_PICTURE_MAKING)
    assert k.GAPS_PICTURE_MAKING_OK == {"gaps_rocks_commons_sa"}
    in_topics = {key for t in topics.TOPICS for key in t.keys}
    assert {"open_images_food_more", "aic_collection", "cleveland_collection", "open_images_cards_documents",
            "loc_maps", "commons_rocks_fossils"} <= in_topics
    assert "Nappy (nappy.co, CC0 photos of Black and brown people)" in k.GAPS_NOT_INCLUDED
