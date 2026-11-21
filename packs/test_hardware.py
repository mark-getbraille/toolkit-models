"""A self-test of the hardware, tools and shop equipment parsers (packs/hardware_packs.py and
training-kit/kit/hardware_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - a part's kind comes from its most specific Commons category ("Carriage bolts" -> a carriage bolt, not a bolt;
    "Wing nuts" -> a wing nut), and its features (head, drive, thread, material, finish) from its category names and
    title; a feature given two different values is not said (never a guess);
  - a size is said only where the title states it in a standard form, never from a camera's lens size;
  - head, drive and thread are said only of screw-like parts, never of a hinge or a tool;
  - singular and plural answers read right ("These are wood screws ... They have"), and safety equipment and ladders
    carry their safety line;
  - every kind table's patterns compile, and categories that are not about the part (climbing bolts, ice screws,
    medical screws, art, firearms) are skipped;
  - ABO listings: the finish, material, sizes and pack count come from the listing's own name and fields, the kind
    from its name, and no listing is in both abo_hardware and things_packs abo_products;
  - the Smithsonian records give the object's own name, maker, place, date and materials, and prints, toys and
    weapons are left out;
  - every pack is wired: in build_packs.PACKS (and COMMONS_KEYS for the Commons packs), the workflows' known list and
    limit lines, the kit's sources and hidden imports, and the picture-making rules.

Run it from the repository's folder:   python3 -m pytest packs/test_hardware.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import hardware_packs as h  # noqa: E402

REPO = os.path.dirname(HERE)
ALL = ("head", "drive", "thread", "material", "finish", "size")


def kind_of(kinds, found_in, cats=(), title="File:X.jpg"):
    rule = h.file_kind(kinds, found_in, list(cats), title)
    return rule and rule[1]


def test_kinds_are_the_most_specific():
    assert kind_of(h.FASTENER_KINDS, "Carriage bolts", ["Bolts"]) == "a carriage bolt"
    assert kind_of(h.FASTENER_KINDS, "Wing nuts", ["Nuts (hardware)"]) == "a wing nut"
    assert kind_of(h.FASTENER_KINDS, "Nyloc nuts") == "a lock nut"
    assert kind_of(h.FASTENER_KINDS, "Roofing nails", ["Metal nails"]) == "roofing nails"
    assert kind_of(h.FASTENER_KINDS, "Confirmat") == "a confirmat screw"
    assert kind_of(h.FASTENER_KINDS, "Toggle bolts") == "a toggle bolt"
    assert kind_of(h.FASTENER_KINDS, "Thread pitch gauges", ["Screws"]) == "a thread pitch gauge"
    assert kind_of(h.FASTENER_KINDS, "Countersunk screws") == "screws"
    assert kind_of(h.DOOR_KINDS, "Concealed hinges", ["Hinges"]) == "a concealed (European) cabinet hinge"
    assert kind_of(h.DOOR_KINDS, "Padlocks", ["Locks (security devices)"]) == "a padlock"
    assert kind_of(h.DOOR_KINDS, "Drawer slides") == "a drawer slide"
    assert kind_of(h.BUILDING_KINDS, "Joist hangers", ["Mounting brackets"]) == "a joist hanger"
    assert kind_of(h.PLUMBING_KINDS, "Twist-on wire connectors") == "a wire nut (twist-on connector)"
    assert kind_of(h.PLUMBING_KINDS, "NEMA 14-50") == "a NEMA 14-50 plug or outlet"
    assert kind_of(h.PLUMBING_KINDS, "P-traps") == "a P-trap"
    assert kind_of(h.MATERIAL_KINDS, "Oriented strand board") == "OSB (oriented strand board)"
    assert kind_of(h.MATERIAL_KINDS, "PTFE tape") == "PTFE thread tape (plumber's tape)"
    assert kind_of(h.HAND_TOOL_KINDS, "Locking pliers", ["Pliers"]) == "locking pliers"
    assert kind_of(h.HAND_TOOL_KINDS, "Jack stands") == "a jack stand"
    assert kind_of(h.POWER_KINDS, "Impact drivers", ["Power tools"]) == "an impact driver"
    assert kind_of(h.SHOP_KINDS, "Jointers") == "a jointer"
    assert kind_of(h.SHOP_KINDS, "TIG welding", ["Welding"]) == "a TIG welder"
    assert kind_of(h.PPE_KINDS, "N95 respirators", ["Respirators"]) == "an N95 respirator"
    assert kind_of(h.SEWING_FOOD_KINDS, "Sergers") == "a serger (overlock machine)"
    assert kind_of(h.FASTENER_KINDS, "Something else entirely") is None


def test_features_from_categories_and_title():
    f = h.file_features(["Countersunk screws", "Torx", "Stainless steel screws"], "File:Screw zinc-plated.jpg")
    assert f == {"head": "a countersunk (flat) head, which sits flush with the surface",
                 "drive": "a Torx (six-point star) screwdriver or bit", "material": "stainless steel",
                 "finish": "zinc-plated"}
    two = h.file_features(["Phillips screws", "Torx"], "File:Mixed screws.jpg")
    assert "drive" not in two                                   # two drives: not said
    cap = h.file_features(["Socket Head Cap Screw", "Hex socket"], "File:x.jpg")
    assert cap["head"] == "a socket cap head: a tall round head" and "hex key" in cap["drive"]
    assert h.file_features(["Rusty bolts"], "File:Old.jpg")["finish"] == "rusty (corroded)"


def test_sizes_only_from_the_title():
    assert h.title_size("File:Screw M6x20 stainless.jpg") == "M6x20"
    assert h.title_size("File:Bolt M12.JPG") == "M12"
    assert h.title_size("File:16d common nails.jpg") == "16d"
    assert h.title_size('File:#8 x 1-1/4" wood screw.jpg') == "#8"
    assert h.title_size("File:Canon EF 50mm lens.jpg") == ""
    assert h.title_size("File:Mercedes M5 engine.jpg") == ""
    assert h.title_size("File:Screws.jpg") == ""


def test_rows_and_feature_limits():
    rule = h.file_kind(h.FASTENER_KINDS, "Wood screws", [], "File:x.jpg")
    feats = h.keep_features(h.file_features(["Wood screws", "Pozidriv", "Countersunk screws"], "File:x.jpg"), rule,
                            ALL)
    rows = h.part_rows(rule, feats, "4x40 mm", "")
    assert rows[0]["answer"].startswith("These are wood screws: screws with a sharp point")
    assert "They have a countersunk (flat) head" in rows[0]["answer"] and "take a Pozidriv" in rows[0]["answer"]
    assert "The file's title gives the size: 4x40 mm." in rows[0]["answer"]
    assert {r["question"] for r in rows} == {h.WHAT_Q, h.HEAD_Q, h.DRIVE_Q, h.SIZE_Q}
    hinge = h.file_kind(h.DOOR_KINDS, "Butt hinges", [], "File:x.jpg")
    feats = h.keep_features(h.file_features(["Butt hinges", "Brass", "Phillips screws"], "File:x.jpg"), hinge,
                            ("material", "finish"))
    assert feats == {"material": "brass"}                       # no screw drive said of a hinge
    rows = h.part_rows(hinge, feats, "", "A brass butt hinge on an old door.")
    assert rows[0]["answer"].startswith("This is a butt hinge") and "Material: brass." in rows[0]["answer"]
    assert rows[-1] == {"question": h.DESCRIBE_Q, "answer": "A brass butt hinge on an old door."}
    nut = h.file_kind(h.FASTENER_KINDS, "Wing nuts", [], "File:x.jpg")
    assert "head" not in h.keep_features({"head": "a pan head", "material": "brass"}, nut, ALL)
    ppe = h.file_kind(h.PPE_KINDS, "Earplugs", [], "File:x.jpg")
    assert h.part_rows(ppe, {}, "", "")[0]["answer"].endswith(h.PPE_LINE)
    ladder = h.file_kind(h.HAND_TOOL_KINDS, "Stepladders", [], "File:x.jpg")
    first = h.part_rows(ladder, {}, "", "")[0]
    assert first["question"] == h.TOOL_Q and first["answer"].endswith(h.LADDER_LINE)


def test_tables_and_skips():
    for name in dir(h):
        if name.endswith("_KINDS") and name != "ABO_KINDS":
            for rule in getattr(h, name):
                assert rule[0].pattern and rule[1] and rule[3] in (h.WHAT_Q, h.TOOL_Q), (name, rule[1])
        if name.endswith("_TOPICS"):
            assert all(isinstance(r, str) and isinstance(d, int) for r, d in getattr(h, name)), name
    for skipped in ("Bolts (climbing)", "Ice screws", "Medical screws", "Screws in art", "Drawings of screws",
                    "Bolt action (firearms)", "Wheel bolts", "Lug nuts", "Screw-shaped food", "Netsuke"):
        assert h.SKIP.search(skipped), skipped
    for kept in ("Carriage bolts", "Wood screws", "Hinges", "Wing nuts", "Table saws", "Respirators"):
        assert not h.SKIP.search(kept), kept
    assert "Wood screws" in h.EXISTING and "Rivets" in h.EXISTING          # asked by commons_tools and machine parts
    assert h.HARM.search("Hand injury from a nail gun") and not h.HARM.search("Galvanised roofing nails")


def listing(name, code="HARDWARE_HANDLE", **more):
    return {"item_id": "B0TEST", "country": "US", "domain_name": "amazon.com", "main_image_id": "img1",
            "product_type": [{"value": code}], "item_name": [{"language_tag": "en_US", "value": name}],
            "brand": [{"language_tag": "en_US", "value": "AmazonBasics"}], **more}


def test_abo_rows():
    rows = h.abo_hw_rows(listing("AmazonBasics Flat Round Cabinet Knob, 1.44\" Diameter, Satin Nickel, 25-Pack",
                                 finish_type=[{"language_tag": "en_US", "value": "Satin Nickel"}]))
    answer = rows[0]["answer"]
    assert answer.startswith("This is a cabinet knob by AmazonBasics. Its listing calls it: AmazonBasics Flat Round")
    assert "Finish: satin nickel." in answer and "A pack of 25." in answer
    assert 'Size (from its listing): 1.44" Diameter.' in answer
    assert {r["question"] for r in rows} == {h.WHAT_Q, h.FINISH_Q, h.SIZE_Q}
    rows = h.abo_hw_rows(listing("AmazonBasics Rounded 3.5 Inch x 3.5 Inch Door Hinges, 18 Pack, Oil Rubbed Bronze",
                                 "HARDWARE_HINGE", material=[{"language_tag": "en_US", "value": "Steel"}]))
    assert rows[0]["answer"].startswith("This is a door hinge by AmazonBasics.")
    assert "Finish: oil rubbed bronze." in rows[0]["answer"] and "Material: steel." in rows[0]["answer"]
    rows = h.abo_hw_rows(listing("AmazonBasics Deadbolt - Single Cylinder - Matte Black", "LOCK"))
    assert rows[0]["answer"].startswith("This is a deadbolt by AmazonBasics: a door lock with a solid bolt")
    assert h.abo_hw_rows(listing("A kettle", "ELECTRIC_WATER_BOILER")) == []
    assert h.abo_hw_rows(listing("", "LOCK")) == []
    import things_packs
    assert set(h.ABO_HW_TYPES) == set(things_packs.ABO_HARDWARE_TYPES)
    assert things_packs.abo_rows(listing("AmazonBasics Deadbolt", "LOCK")) == []    # not in abo_products any more


def nmah(title, object_name, **free):
    return {"title": title, "content": {
        "freetext": {"objectType": [{"label": "Object Name", "content": object_name}], **free},
        "descriptiveNonRepeating": {"record_ID": "nmah_1", "guid": "https://n2t.net/ark:/1",
                                    "online_media": {"media": [{"type": "Images", "content": "https://ids.si.edu/x",
                                                                "usage": {"access": "CC0"}}]}}}}


def test_nmah_rows():
    url, rows = h.nmah_row(nmah("Padlock", "padlock", name=[{"label": "maker", "content": "Yale & Towne"}],
                                place=[{"label": "place made", "content": "United States: Connecticut, Stamford"}],
                                date=[{"label": "date made", "content": "ca 1890"}],
                                physicalDescription=[{"label": "Physical Description",
                                                      "content": "brass (overall material)"}]))
    assert url == "https://ids.si.edu/x&max=2048"
    assert rows[0]["answer"] == ("This is a padlock, made by Yale & Towne in Connecticut, Stamford, ca 1890. Its "
                                 "record gives its materials: brass.")
    assert rows[1]["question"] == "What is it made of?" and "CC0" in rows[0]["credit"]
    assert h.nmah_row(nmah("Lock", "photograph")) is None
    assert h.nmah_row(nmah("Toy hammer", "toy")) is None
    assert h.nmah_row(nmah("Rifle bolt", "rifle")) is None
    assert h.nmah_row(nmah("Suit", "suit, 2 piece")) is None
    assert h.nmah_row(nmah("Smoothing plane", "plane, smoothing"))[1][0]["answer"].startswith("This is a wood plane")


def test_wiring():
    keys = set(h.HARDWARE_PACKS)
    assert keys == set(h.HARDWARE_LIMITS)
    assert keys <= set(build_packs.PACKS)
    commons = {k for k in keys if k.startswith("commons_")}
    assert commons <= build_packs.COMMONS_KEYS and not {"abo_hardware", "nmah_hardware_tools"} & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in h.HARDWARE_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import hardware_sources") == 2
    import sources
    import hardware_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed) and "hardware_commons_sa" in listed
    assert listed["hardware_commons_sa"].group == "share-alike"
    assert all(listed[key].group == "permissive" for key in keys)
    people = {"commons_hand_tools_trades", "commons_power_tools", "commons_shop_machines", "commons_ppe",
              "commons_sewing_food_equipment"}
    assert people <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS) and people <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert "hardware_commons_sa" in sources.NOT_FOR_PICTURE_MAKING and k.HARDWARE_PICTURE_MAKING_OK == set()
    assert "commons_fasteners" not in sources.NOT_FOR_PICTURE_MAKING        # parts alone, no people
    assert all(len(s) == 4 for s in k.HARDWARE_SA)
