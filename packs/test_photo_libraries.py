"""A self-test of the NASA Image and Video Library packs (packs/nasa_library_packs.py), the themed NPGallery packs
(packs/nps_library_packs.py) and the kit's entries for them (training-kit/kit/photo_library_sources.py), with
made-up records only: nothing is downloaded from the internet.

It checks that:
  - only NASA's own pictures are kept: a NASA centre, a NASA photographer (or none), NASA/JPL/STScI/USGS credits,
    and no copyright, courtesy or licence words; company, other-agency, university and amateur credits are left out;
  - NASA answers are the record's own plain description (catalogue prefix, credit lines, web addresses and "for
    more" sentences taken out, nothing added) and too-short captions give no answer;
  - each record gets one theme, graphics none, and pictures with people never go to the planets or Earth packs;
  - only public-domain NPGallery photos credited to the Park Service are kept; the wildlife and landscape themes skip
    the general npgallery pack's words, and no search word of the themed packs is one of its words;
  - a builder with made-up search pages keeps only its own theme's free records, each picture once;
  - every pack is wired: in build_packs.PACKS (and not in the Commons lane), in the workflows' known list and limit
    lines, in the kit's sources (group "permissive", prepare_pack), picture-making only for the keys the kit module
    allows, the people packs in PEOPLE_AND_BODILY_PACK_KEYS, in the topics the module docstring names, and the
    guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_photo_libraries.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import documentary_packs  # noqa: E402
import nasa_library_packs as n  # noqa: E402
import nps_library_packs as p  # noqa: E402

REPO = os.path.dirname(HERE)


def record(**fields):
    """A made-up NASA library record with a NASA centre, a title and a caption, changed by fields."""
    info = {"center": "KSC", "nasa_id": "KSC-20990101-PH-TEST01", "media_type": "image",
            "title": "Made-up test record", "description": "A made-up caption that is long enough to be a description.",
            "keywords": []}
    info.update(fields)
    return info


# ----------------------------------------------------------------- NASA: copyright

def test_nasa_free_keeps_nasa_pictures():
    assert n.nasa_free(record())
    assert n.nasa_free(record(photographer="NASA/Jane Doe"))
    assert n.nasa_free(record(photographer="NASA JSC"))
    assert n.nasa_free(record(center="JPL", secondary_creator="NASA/JPL-Caltech"))
    assert n.nasa_free(record(center="GSFC", secondary_creator="NASA, STScI"))
    assert n.nasa_free(record(description="A made-up crater on a made-up moon. Image credit: NASA/JPL-Caltech/USGS"))


def test_nasa_free_leaves_out_others():
    assert not n.nasa_free(record(center=""))
    assert not n.nasa_free(record(center="ESA"))
    assert not n.nasa_free(record(photographer="Rocket Lab"))
    assert not n.nasa_free(record(photographer="SpaceX"))
    assert not n.nasa_free(record(photographer="Jane Doe"))
    assert not n.nasa_free(record(center="JPL", secondary_creator="NASA/JPL-Caltech/MSSS"))
    assert not n.nasa_free(record(center="JPL", secondary_creator="NASA/ESA/Made-up University"))
    assert not n.nasa_free(record(description="A made-up launch photo. Photo courtesy of a made-up company."))
    assert not n.nasa_free(record(description="A made-up comet over a made-up hill. Copyright Jane Doe."))
    assert not n.nasa_free(record(secondary_creator="Enhanced image by Jane Doe (CC BY-NC-SA)"))
    assert not n.nasa_free(record(description="A made-up galaxy. Image credit: NASA, ESA and J. Doe (Made-up U.)"))


# ----------------------------------------------------------------- NASA: answers

def test_nasa_answer_is_the_plain_description():
    info = record(title="Made-up shuttle view",
                  description="S99-12345 (8 Feb. 2099) --- A made-up overhead view of a made-up shuttle cargo bay "
                              "with its doors open. Photo credit: NASA/Jane Doe. For more information, visit "
                              "https://www.nasa.gov/made-up.")
    assert n.nasa_answer(info) == "A made-up overhead view of a made-up shuttle cargo bay with its doors open."
    long = record(description=" ".join(f"Sentence number {i} has exactly seven words here." for i in range(20)))
    answer = n.nasa_answer(long)
    assert len(answer.split()) <= 70 and answer.endswith(".")
    assert n.nasa_answer(record(description="Made-up short caption.")) == ""
    assert n.nasa_answer(record(title="A made-up title of seven words here",
                                description="A made-up title of seven words here.")) == ""


# ----------------------------------------------------------------- NASA: themes

def test_theme_of():
    assert n.theme_of(record(title="Made-up Jupiter clouds", description="Made-up storms on Jupiter seen by Juno.")) \
        == "nasa_planets_telescopes"
    assert n.theme_of(record(title="Made-up coast as seen from the International Space Station",
                             description="A made-up coastline photographed by the crew from orbit.")) \
        == "nasa_earth_from_space"
    assert n.theme_of(record(title="Made-up ER-2 in flight", description="A made-up research aircraft.")) \
        == "nasa_aircraft"
    assert n.theme_of(record(title="Made-up STS-999 launch",
                             description="Astronauts aboard a made-up shuttle lift off from Pad 39A.")) \
        == "nasa_rockets_launch"
    assert n.theme_of(record(title="Made-up spacewalk", description="A made-up astronaut works outside a station.")) \
        == "nasa_space_astronauts"
    assert n.theme_of(record(title="Made-up clean room work",
                             description="Made-up technicians fit a panel to a made-up spacecraft.")) \
        == "nasa_people_at_work"
    # people never go to the planets or Earth packs
    assert n.theme_of(record(title="Made-up Hubble training",
                             description="Astronauts practise made-up Hubble repairs in a pool.")) \
        != "nasa_planets_telescopes"
    assert n.theme_of(record(title="Made-up Mars rover test",
                             description="Engineers drive a made-up Mars rover in a test yard.")) \
        == "nasa_people_at_work"
    # graphics have no theme; a record with no theme words has none
    assert n.theme_of(record(title="Made-up Mars base (Illustration)", description="An illustration of a base.")) == ""
    assert n.theme_of(record(title="Made-up artist's concept", description="A made-up planet.")) == ""
    assert n.theme_of(record(title="Made-up award", description="A made-up plaque on a made-up wall.")) == ""


def test_picture_link_takes_the_largest_that_fits():
    item = {"links": [{"href": "https://example.invalid/a~orig.jpg", "render": "image", "width": 6000, "height": 4000},
                      {"href": "https://example.invalid/a~large.jpg", "render": "image", "width": 1920, "height": 1280},
                      {"href": "https://example.invalid/a~medium.jpg", "render": "image", "width": 1280, "height": 853},
                      {"href": "https://example.invalid/a.srt", "render": "caption", "width": 0, "height": 0}]}
    assert n.picture_link(item) == "https://example.invalid/a~large.jpg"
    assert n.picture_link({"links": []}) == ""


def test_keys_and_searches():
    assert sorted(n.NASA_LIBRARY_KEYS) == sorted(k for k, _w, _p in n.THEMES)
    assert set(n.SEARCHES) == set(n.NASA_LIBRARY_KEYS) == set(n.NASA_LIBRARY_LIMITS) == set(n.NASA_LIBRARY_PACKS)
    for key, searches in n.SEARCHES.items():
        assert len(searches) == len(set(searches)), key


def fake_get_json(pages):
    """A stand-in for documentary_packs.get_json that answers from made-up pages {(query, page): data}."""
    def get(_s, _url, params=None, **_kw):
        return pages.get((params.get("q") or params.get("keyword"), params.get("page")))
    return get


def quiet(monkeypatch, module):
    """No waiting, no set-aside pictures and no published pack, for a builder run on made-up pages."""
    set_aside = []
    monkeypatch.setattr(module.time, "sleep", lambda _s: None)
    monkeypatch.setattr(module, "listing_out_of_time", lambda: False)
    monkeypatch.setattr(module, "already_in_pack", lambda *a, **k: False)
    monkeypatch.setattr(module, "needs_description", lambda name, *a, **k: set_aside.append(name) or True)
    return set_aside


def test_library_items_keeps_only_its_theme(monkeypatch):
    set_aside = quiet(monkeypatch, n)
    link = [{"href": "https://example.invalid/x~large.jpg", "render": "image", "width": 1920, "height": 1080}]

    def item(**fields):
        """A made-up search result."""
        return {"data": [record(**fields)], "links": link}
    found = [item(nasa_id="A1", title="Made-up ER-2 in flight", description="A made-up research aircraft over a "
                                                                              "made-up desert at dawn."),
             item(nasa_id="A1", title="Made-up ER-2 in flight", description="The same record found twice here."),
             item(nasa_id="A2", title="Made-up X-99 on a runway", photographer="A made-up company",
                  description="A made-up aircraft photo by a company, not NASA."),
             item(nasa_id="A3", title="Made-up Saturn rings", description="Made-up rings of Saturn's moons seen "
                                                                            "by Cassini."),
             item(nasa_id="A4", title="Made-up glider", description="Glider.")]
    pages = {(q, 1): {"collection": {"metadata": {"total_hits": len(found)}, "items": found}}
             for q in n.SEARCHES["nasa_aircraft"]}
    monkeypatch.setattr(n, "get_json", fake_get_json(pages))
    items = n.library_items("nasa_aircraft", 10, s=object())
    assert [name for name, _u, _r in items] == ["nasa-A1.jpg"]
    rows = items[0][2]
    assert rows[0]["question"] == "Describe this picture." and rows[0]["answer"].startswith("A made-up research")
    assert "images.nasa.gov/details/A1" in rows[0]["credit"] and "not under copyright" in rows[0]["credit"]
    assert set_aside == ["nasa-A4.jpg"]


# ----------------------------------------------------------------- NPGallery

def asset(**fields):
    """A made-up NPGallery record: a public-domain photo with alt text, changed by fields."""
    info = {"AssetID": "00000000-0000-0000-0000-000000000001", "PrimaryType": "image",
            "ConstraintsInformation": {"Constraint": "Public domain"}, "PhotoCredit": "NPS Photo",
            "Title": "Made-up accessible trail", "Keywords": ["accessible trail", "made-up park"],
            "AltText": "A made-up paved path with a gentle slope runs between low railings.",
            "Description": "A made-up description of the made-up path.",
            "NPSUnits": [{"Name": "Made-up National Park"}]}
    info.update(fields)
    return info


def test_nps_free():
    assert p.nps_free(asset())
    assert p.nps_free(asset(PhotoCredit=""))
    assert p.nps_free(asset(PhotoCredit="NPS / Jane Doe"))
    assert p.nps_free(asset(PhotoCredit="National Park Service"))
    assert not p.nps_free(asset(PhotoCredit="Jane Doe"))
    assert not p.nps_free(asset(PhotoCredit="Courtesy of a made-up society"))
    assert not p.nps_free(asset(ConstraintsInformation={"Constraint": "Copyright"}))
    assert not p.nps_free(asset(Description="A made-up photo. Copyright Jane Doe."))


def test_nps_theme_of():
    assert p.theme_of(asset()) == "npgallery_accessibility"
    assert p.theme_of(asset(Title="Made-up visitor center desk", Keywords=["visitor center"],
                            AltText="A made-up desk in a made-up lobby.")) == "npgallery_facilities"
    assert p.theme_of(asset(Title="Made-up homestead cabin", Keywords=["cabin"])) == "npgallery_historic_buildings"
    assert p.theme_of(asset(Title="Made-up moose", Keywords=["moose"])) == "npgallery_wildlife_more"
    assert p.theme_of(asset(Title="Made-up sand dunes", Keywords=["dunes"])) == "npgallery_landscapes_more"
    # the general pack's words: a moose by a river or dunes under a mountain are its subject
    assert p.theme_of(asset(Title="Made-up moose by a river", Keywords=["moose"])) == ""
    assert p.theme_of(asset(Title="Made-up dunes", Keywords=["dunes", "mountain"])) == ""
    assert p.theme_of(asset(Title="Made-up park map", Keywords=["accessible"])) == ""
    assert p.theme_of(asset(Title="Made-up thing", Keywords=["thing"], AltText="A made-up thing.")) == ""


def test_nps_searches_are_not_the_general_packs_words():
    general = {w.lower() for w in documentary_packs.NPG_WORDS}
    for key, words in p.SEARCHES.items():
        assert not {w.lower() for w in words} & general, key
        assert len(words) == len(set(words)), key
    assert set(p.SEARCHES) == set(p.NPS_LIBRARY_KEYS) == set(p.NPS_LIBRARY_LIMITS) == set(p.NPS_LIBRARY_PACKS)


def test_gallery_items_keeps_only_its_theme(monkeypatch):
    set_aside = quiet(monkeypatch, p)
    results = [{"Asset": asset(AssetID="a1")}, {"Asset": asset(AssetID="a1")},
               {"Asset": asset(AssetID="a2", PhotoCredit="Jane Doe")},
               {"Asset": asset(AssetID="a3", Title="Made-up moose", Keywords=["moose"])},
               {"Asset": asset(AssetID="a4", AltText="Short alt text.")},
               {"Asset": asset(AssetID="a5", PrimaryType="document")}]
    pages = {(w, page): {"Results": results} for w in p.SEARCHES["npgallery_accessibility"] for page in range(1, 60)}
    monkeypatch.setattr(p, "get_json", fake_get_json(pages))
    items = p.gallery_items("npgallery_accessibility", 10, s=object())
    assert [name for name, _u, _r in items] == ["npgallery-a1.jpg"]
    name, url, rows = items[0]
    assert url.endswith("GetAsset/a1/proxyhires.jpg")
    assert rows[0]["answer"].startswith("A made-up paved path") and "public domain" in rows[0]["credit"]
    assert rows[1]["question"] == "Where was this photo taken?"
    assert rows[1]["answer"] == "It was taken in Made-up National Park, USA."
    assert set_aside == ["npgallery-a4.jpg"]


# ----------------------------------------------------------------- wiring

def test_wiring():
    limits = {**n.NASA_LIBRARY_LIMITS, **p.NPS_LIBRARY_LIMITS}
    keys = set(limits)
    assert len(keys) == 11
    for key in keys:
        assert key in build_packs.PACKS and key not in build_packs.COMMONS_KEYS, key
    for key in n.NASA_LIBRARY_PACKS:
        assert build_packs.PACKS[key] is n.NASA_LIBRARY_PACKS[key], key
    for key in p.NPS_LIBRARY_PACKS:
        assert build_packs.PACKS[key] is p.NPS_LIBRARY_PACKS[key], key
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in limits.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import photo_library_sources") == 2
    import sources
    import topics
    import photo_library_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    assert {s.key for s in k.PHOTO_LIBRARY_SOURCES} == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert (key in no_making) == (key not in k.PHOTO_LIBRARY_PICTURE_MAKING_OK), key
        assert listed[key].cap <= limits[key], key
    for key in k.PHOTO_LIBRARY_BODILY_KEYS:
        assert key in sources.PEOPLE_AND_BODILY_PACK_KEYS and key not in k.PHOTO_LIBRARY_PICTURE_MAKING_OK, key
    in_topic = {
        "machines": {"nasa_aircraft", "nasa_rockets_launch"},
        "nature": {"nasa_earth_from_space", "nasa_planets_telescopes", "npgallery_wildlife_more",
                   "npgallery_landscapes_more"},
        "documents": {"npgallery_facilities"},
        "vision": {"npgallery_accessibility"},
    }
    for topic_id, wanted in in_topic.items():
        assert wanted <= set(topics.find(topic_id).keys), topic_id
    no_topic = {"nasa_space_astronauts", "nasa_people_at_work", "npgallery_historic_buildings"}
    for topic in topics.TOPICS:
        assert not no_topic & set(topic.keys), topic.id
    assert all(reason for reason in k.PHOTO_LIBRARY_NOT_INCLUDED.values())
    assert all(link.startswith("https://") for link in k.PHOTO_LIBRARY_SIGN_UP.values())


def test_nps_accessibility_needs_its_own_words():
    """Accessibility only from the title or keywords, and not from a person's name or a park interpreter."""
    assert p.theme_of(asset(Title="Made-up house repairs", Keywords=["made-up house"],
                            AltText="Project notes: a fully accessible path will be built.")) \
        == "npgallery_historic_buildings"
    assert p.theme_of(asset(Title="Made-up ranger talk by Ada Doe", Keywords=["interpreter"],
                            AltText="A made-up ranger speaks to a made-up group.")) == ""
    assert p.theme_of(asset(Title="Made-up ADA ramp", Keywords=["ramp"])) == "npgallery_accessibility"
