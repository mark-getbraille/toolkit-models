"""A self-test of the North American animal packs (packs/na_animal_packs.py), with made-up records only: nothing is
downloaded from the internet.

It checks that:
  - a GBIF record that is dead, shows tracks or bones in a species pack, is captive, is a person or a domestic animal,
    or whose words name a kill, a catch, roadkill or an injury is left out; a signs group keeps only the sign it asks
    for; only a photo whose OWN licence is open is used;
  - sex and age are said only when the record states them ("a doe", "a fawn", "a caterpillar"), never guessed;
  - venomous and dangerous animals get their safety note, and signs get their own sentence;
  - English names: the preferred name most checklists give, then ITIS, then the commonest;
  - the species are visited commonest first, with priority species every third place, and caps shrink together;
  - a whole wild pack runs on a made-up GBIF (the photos are not fetched);
  - Commons breed categories are matched to the wanted breeds by name; domestic rows mark children but not the young
    of animals ("goat kids");
  - NOAA pictures are kept only when NOAA's own credit is on them and their description names the species;
  - every pack is wired: in build_packs.PACKS (na_domestic_animals in COMMONS_KEYS, the GBIF and NOAA packs not), in
    the workflow's known list and limit lines, in the kit's sources and its nature topic, and the packs that show
    people never used for picture-making.

Run it from the repository's folder:   python3 -m pytest packs/test_na_animals.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import na_animal_packs as n  # noqa: E402

REPO = os.path.dirname(HERE)
CC_BY = "http://creativecommons.org/licenses/by/4.0/"
CC_BY_NC = "http://creativecommons.org/licenses/by-nc/4.0/"


def media(licence=CC_BY, url="https://inaturalist-open-data.s3.amazonaws.com/photos/1/original.jpg"):
    """A made-up GBIF media entry."""
    return {"type": "StillImage", "identifier": url, "license": licence, "creator": "A. Person"}


def record(**extra):
    """A made-up GBIF record of a white-tailed deer."""
    r = {"key": 11, "species": "Odocoileus virginianus", "speciesKey": 2440965, "genus": "Odocoileus",
         "family": "Cervidae", "order": "Artiodactyla", "taxonRank": "SPECIES", "countryCode": "US",
         "gadm": {"level1": {"name": "Pennsylvania"}}, "datasetKey": "d", "datasetName": "iNaturalist research-grade "
         "observations", "recordedBy": "A. Person", "media": [media()], "vitality": "alive",
         "dynamicProperties": '{"evidenceOfPresence":"organism"}',
         "references": "https://www.inaturalist.org/observations/1"}
    r.update(extra)
    return r


def test_records_left_out():
    """Dead, signs in a species pack, captive, people and domestic animals, and harm words are left out."""
    m = media()
    assert n.record_problem(record(), m) == ""
    assert "dead" in n.record_problem(record(vitality="dead"), m)
    assert n.record_problem(record(dynamicProperties='{"evidenceOfPresence":"track"}'), m)
    assert n.record_problem(record(dynamicProperties='{"evidenceOfPresence":"bone"}'), m, "track")
    assert n.record_problem(record(**{"http://unknown.org/captive_cultivated": "captive"}), m)
    assert n.record_problem(record(species="Felis catus"), m)
    assert n.record_problem(record(species="Homo sapiens"), m)
    for words in ("Roadkill on route 9", "hit by a car", "harvested by my uncle", "caught this bass",
                  "injured leg", "mounted specimen", "eating a squirrel", "entangled in a net"):
        assert n.record_problem(record(occurrenceRemarks=words), m), words
    assert n.record_problem(record(), dict(m, title="Dead deer"))
    # A signs group keeps only the sign it asks for, and a record showing it with eggs is fine for "egg".
    assert n.record_problem(record(dynamicProperties='{"evidenceOfPresence":"track"}'), m, "track") == ""
    assert n.record_problem(record(dynamicProperties='{"evidenceOfPresence":["construction","egg"]}'), m, "egg") \
        == "it shows construction, egg, not what this pack asks about"
    assert n.record_problem(record(dynamicProperties='{"evidenceOfPresence":"scat"}'), m, "track")


def test_only_open_photo_licences():
    """The photo's own licence decides: a CC BY-NC photo on a CC BY record is not used."""
    assert n.free_media(record(media=[media(CC_BY_NC)])) is None
    assert n.free_media(record(media=[media(CC_BY_NC), media(CC_BY)]))["license"] == CC_BY
    assert n.photo_url("https://inaturalist-open-data.s3.amazonaws.com/photos/9/original.jpg").endswith(
        "/9/large.jpg")


def test_inaturalist_through_gbif():
    """The shared iNaturalist reader takes photos only from the iNaturalist Open Dataset (never iNaturalist's own
    website), as their "large" copy, each photo's own licence open; regions are matched without accents."""
    static = media(url="https://static.inaturalist.org/photos/1/original.jpg")
    assert n.free_media({"media": [static]}) is None
    assert n.inat_photo({"media": [static]}) == (None, "")
    s3 = dict(static, identifier="https://inaturalist-open-data.s3.amazonaws.com/photos/2/original.png")
    nc = dict(s3, license=CC_BY_NC)
    assert n.inat_photo({"media": [static, nc, s3]}) == (s3, "CC BY 4.0")
    assert n.inat_photo_id(s3) == "2" and n.photo_url(s3["identifier"]).endswith("/photos/2/large.png")
    assert n.on_inaturalist_site("https://api.inaturalist.org/v1/observations")
    assert not n.on_inaturalist_site(s3["identifier"])
    rec = record(media=[nc, s3], taxonRank="SPECIES", speciesKey=None)
    name, url, rows = n.inat_region_item(None, rec, "What animal is this?", "Ontario, Canada", "inatca", {})
    assert name == "inatca-2.jpg" and url.endswith("/photos/2/large.png")
    assert rows[0]["answer"] == "This is Odocoileus virginianus." and rows[0]["place"] == "Ontario, Canada"
    assert rows[0]["credit"].startswith("Photo by A. Person on iNaturalist, CC BY 4.0, "
                                        "https://www.inaturalist.org/observations/1 (via GBIF")
    assert rows[1]["answer"] == "It was taken in Ontario, Canada."
    assert n.inat_region_item(None, record(media=[nc]), "Q?", "Ontario, Canada", "inatca", {}) is None
    assert n.inat_region_item(None, record(taxonRank="GENUS"), "Q?", "Ontario, Canada", "inatca", {}) is None

    class Answer:
        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    class FakeGbif:
        def get(self, url, params=None, timeout=None):
            assert "inaturalist.org" not in url
            return Answer({"facets": [{"counts": [{"name": "Ontario"}, {"name": "Québec"}]}]})
    from canada_packs import folded
    assert n.inat_regions(FakeGbif(), "CA", ["Quebec", "Yukon"], folded) == {"Quebec": "Québec"}


def test_sex_and_age_only_when_stated():
    """A doe, a buck, a fawn, a male bird, a caterpillar; nothing when nothing is stated."""
    assert n.wild_answer("White-tailed Deer", "Odocoileus virginianus", record(sex="Female")) == \
        "This is a White-tailed Deer (Odocoileus virginianus), a doe."
    assert n.wild_answer("White-tailed Deer", "Odocoileus virginianus", record(sex="Male")).endswith("a buck.")
    assert n.wild_answer("White-tailed Deer", "Odocoileus virginianus", record(lifeStage="Juvenile")).endswith(
        "a fawn.")
    assert n.wild_answer("White-tailed Deer", "Odocoileus virginianus", record()) == \
        "This is a White-tailed Deer (Odocoileus virginianus)."
    assert n.wild_answer("White-tailed Deer", "Odocoileus virginianus", record(sex="Indeterminate")) == \
        "This is a White-tailed Deer (Odocoileus virginianus)."
    bird = {"genus": "Cardinalis", "family": "Cardinalidae", "order": "Passeriformes", "species": "Cardinalis "
            "cardinalis", "sex": "Male", "lifeStage": "Adult"}
    assert n.wild_answer("Northern Cardinal", "Cardinalis cardinalis", bird).endswith("an adult male.")
    moth = {"order": "Lepidoptera", "genus": "Malacosoma", "lifeStage": "Larva", "species": "Malacosoma americana"}
    assert "a caterpillar" in n.wild_answer("Eastern Tent Caterpillar Moth", "Malacosoma americana", moth)
    assert n.wild_answer("", "Sorex cinereus", {"species": "Sorex cinereus"}) == "This is Sorex cinereus."


def test_safety_notes_and_signs():
    """Venomous and dangerous animals get a caution; signs get their sentence."""
    snake = {"genus": "Crotalus", "species": "Crotalus horridus"}
    assert "Caution: it is a rattlesnake, venomous" in n.wild_answer("Timber Rattlesnake", "Crotalus horridus", snake)
    assert "venomous" in n.wild_answer("Eastern Copperhead", "Agkistrodon contortrix",
                                       {"genus": "Agkistrodon", "species": "Agkistrodon contortrix"})
    assert "brown recluse" in n.wild_answer("Brown Recluse", "Loxosceles reclusa", {"genus": "Loxosceles"})
    assert "widow" in n.wild_answer("Southern Black Widow", "Latrodectus mactans", {"genus": "Latrodectus"})
    assert "Lyme" in n.wild_answer("Blacklegged Tick", "Ixodes scapularis", {"genus": "Ixodes"})
    assert "Caution" not in n.wild_answer("Eastern Gray Squirrel", "Sciurus carolinensis", {"genus": "Sciurus"})
    assert n.wild_answer("Raccoon", "Procyon lotor", {"genus": "Procyon"}, "tracks") == \
        "These are tracks of a Raccoon (Procyon lotor)."
    assert n.wild_answer("Raccoon", "Procyon lotor", {"genus": "Procyon"}, "scat").startswith("This is scat")
    assert all(p.startswith(n.ARACHNID_GENERA) for p in n.ARACHNID_PESTS)
    assert "Cimex lectularius" in n.INSECT_PESTS and "Ixodes scapularis" in n.ARACHNID_PESTS


def test_english_names():
    """The preferred name most checklists give; else ITIS; else the commonest; diseases are not names."""
    itis = n.ITIS + " (ITIS)"
    assert n.english_name([{"language": "eng", "vernacularName": "American Deer", "source": "Catalogue of Life"},
                           {"language": "eng", "vernacularName": "White-tailed Deer", "source": itis}]) == \
        "White-tailed Deer"
    assert n.english_name([{"language": "eng", "vernacularName": "Gray squirrel", "source": "a"},
                           {"language": "eng", "vernacularName": "Eastern Gray Squirrel", "source": "b"},
                           {"language": "eng", "vernacularName": "Eastern gray squirrel", "source": "c"},
                           {"language": "fra", "vernacularName": "Écureuil gris", "source": "d"}]) == \
        "Eastern Gray Squirrel"
    assert n.english_name([{"language": "eng", "vernacularName": "firefish", "source": itis},
                           {"language": "eng", "vernacularName": "Red Lionfish", "source": "a", "preferred": True},
                           {"language": "eng", "vernacularName": "Red lionfish", "source": "b", "preferred": True}]) \
        == "Red Lionfish"
    assert n.english_name([{"language": "eng", "vernacularName": "Leaf spot", "source": itis}]) == ""
    assert n.english_name([]) == ""


def test_visit_order():
    """Commonest first, a priority species every third place, caps by rank, all caps shrinking together."""
    ranked = [(k, 1000 - k) for k in range(1, 501)]
    order = n.visit_order([(9999, 50), (3, 997)], ranked, 10, 10 ** 6)
    assert [k for k, _, _ in order[:4]] == [1, 2, 9999, 3]            # species 3 is ranked high already
    caps = {k: c for k, _, c in order}
    assert caps[1] == 20 and caps[100] == 10 and caps[450] == 5 and caps[9999] == 10
    small = n.visit_order([], ranked, 10, 100)
    assert len(small) == 500 and all(c >= 1 for _, _, c in small) and sum(c for _, _, c in small) < 700


class FakeResponse:
    """A made-up HTTP answer."""

    def __init__(self, data):
        self.data = data

    def json(self):
        """The made-up JSON."""
        return self.data


class FakeGBIF:
    """A made-up GBIF API: two mammal species, the commoner with a dead record and a CC BY-NC photo."""

    def get(self, url, params=None, timeout=None):
        """The answer to one request."""
        params = params or {}
        if url.endswith("/vernacularNames"):
            name = "White-tailed Deer" if "/2440965/" in url else "Raccoon"
            return FakeResponse({"results": [{"language": "eng", "vernacularName": name, "source": n.ITIS}]})
        if url.endswith("species/match"):
            return FakeResponse({})                      # no priority species found
        if params.get("facet"):
            return FakeResponse({"facets": [{"counts": [{"name": "2440965", "count": 40},
                                                        {"name": "5218786", "count": 20}]}]})
        if params.get("speciesKey") == 2440965:
            return FakeResponse({"results": [record(key=1, sex="Female"), record(key=2, vitality="dead"),
                                             record(key=3, media=[media(CC_BY_NC)])]})
        return FakeResponse({"results": [record(key=4, species="Procyon lotor", speciesKey=5218786, genus="Procyon",
                                                family="Procyonidae", recordedBy="B. Person",
                                                gadm={"level1": {"name": "Ontario"}}, countryCode="CA")]})


def test_wild_pack_offline(monkeypatch):
    """A whole wild pack on a made-up GBIF: the dead record and the CC BY-NC photo are left out."""
    fetched = []
    monkeypatch.setattr(n, "session", lambda: FakeGBIF())
    monkeypatch.setattr(n.time, "sleep", lambda s: None)
    monkeypatch.setattr(n, "fetch_all", lambda items, **kw: fetched.extend(items) or
                        [(name, b"jpeg", rows) for name, url, rows in items])
    entries = n.build_na_wild_mammals(10)
    answers = sorted(r["answer"] for _, _, r in entries if r["question"] == "What animal is this?")
    assert answers == ["This is a Raccoon (Procyon lotor).",
                       "This is a White-tailed Deer (Odocoileus virginianus), a doe."]
    places = {r["place"] for _, _, r in entries if r.get("place")}
    assert places == {"Pennsylvania, USA", "Ontario, Canada"}
    assert all("gbif.org/occurrence/" in r["credit"] and "CC BY 4.0" in r["credit"] for _, _, r in entries)
    assert all(url.endswith("/large.jpg") for _, url, _ in fetched)


def test_breed_matching():
    """Commons breed categories are matched by name, whatever their brackets or animal word."""
    cats = ["Category:Boxer (dog)", "Category:Labrador Retriever", "Category:Dogs by breed group",
            "Category:Bichon Frisé", "Category:Unknown breed X"]
    found = n.wanted_breeds(cats, "dog", n.DOG_BREEDS)
    assert found["Category:Boxer (dog)"][0] == "Boxer"
    assert "Category:Labrador Retriever" in found and "Category:Unknown breed X" not in found
    assert len([c for c in found if "Bichon" in c]) == 1
    cows = n.wanted_breeds(["Category:Jersey cattle", "Category:Holstein Friesian cattle"], "cattle", n.CATTLE_BREEDS)
    assert n.breed_answer(*cows["Category:Jersey cattle"], "cattle") == "This is a Jersey, a breed of dairy cattle."
    chickens = n.wanted_breeds(["Category:Rhode Island Red"], "chicken", n.CHICKEN_BREEDS)
    assert n.breed_answer(*chickens["Category:Rhode Island Red"], "chicken") == \
        "This is a Rhode Island Red, a breed of chicken."


def test_domestic_rows_and_harm():
    """The young of animals are not children; a child named in the words is marked; butchery is left out."""
    rows = n.domestic_rows("File:Goat kids playing.jpg", "c", "Two goat kids playing in a field of goats.",
                           "What breed of goat is this?", "This is a Boer, a breed of goat.", "Boer goat")
    assert not any(r.get("child") for r in rows)
    rows = n.domestic_rows("File:Pony.jpg", "c", "A girl leading her Shetland pony at a county fair.",
                           "What breed of horse is this?", "This is a Shetland pony, a breed of horse.", "Shetland")
    assert all(r.get("child") for r in rows)
    assert rows[1]["question"] == n.DESCRIBE_Q
    for words in ("Pig slaughter in a village", "Lamb meat at a market", "Dead calf", "Dog statue"):
        assert n.DOMESTIC_HARM.search(words), words
    assert not n.DOMESTIC_HARM.search("A Jersey cow grazing")
    assert n.SKIP_CAT.search("Labrador Retrievers in art") and not n.SKIP_CAT.search("Labrador Retriever puppies")


NOAA_PAGE = """<h2 class="species-overview__header-name">\n<span>Humpback Whale</span>\n</h2>
<p class="species-overview__header-subname">Megaptera novaeangliae</p>
<img class="dam-image img-responsive" src="/s3/a.jpg?itok=1" alt="Humpback whale breaching. Credit: NOAA Fisheries."/>
<figcaption>Credit: NOAA Fisheries</figcaption>
<img class="dam-image" src="/s3/b.jpg" alt="A close up of a humpback whale tail fluke."/>
<figcaption>Credit: Val Shore/Eagle Wing Tours.</figcaption>
<img class="dam-image" src="/s3/c.jpg" alt="Three melon-headed whales swim together."/>
<figcaption>Credit: NOAA Fisheries/Mary Applegate</figcaption>
<img class="dam-image" src="/s3/d.jpg" alt="Researchers tagging a humpback whale from a boat."/>
<figcaption>Credit: NOAA Fisheries</figcaption>"""


def test_noaa_images():
    """Only NOAA-credited pictures that name the species, without people, tagging or boats."""
    common, latin, images = n.noaa_images(NOAA_PAGE)
    assert (common, latin) == ("Humpback Whale", "Megaptera novaeangliae")
    assert images == [("https://www.fisheries.noaa.gov/s3/a.jpg?itok=1", "Humpback whale breaching.",
                       "NOAA Fisheries")]


def test_wiring():
    """Every pack is wired into the builder, the workflows and the kit."""
    keys = set(n.NA_ANIMAL_PACKS)
    assert keys <= set(build_packs.PACKS)
    assert keys & build_packs.COMMONS_KEYS == {"na_domestic_animals"}
    assert set(n.NA_ANIMAL_LIMITS) == keys
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    for key, limit in n.NA_ANIMAL_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    import sources
    import topics
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed)
    assert all(listed[k].group == "permissive" for k in keys)
    people = {"na_herps_fish", "noaa_fisheries_species", "na_domestic_animals"}
    assert people <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS) and people <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert keys <= set(topics.find("nature").keys)
