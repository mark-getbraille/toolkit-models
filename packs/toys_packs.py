"""Picture packs for TOYS AND CHILDREN'S PRODUCTS (the owner's request of 2026-11-22): toys by type (blocks,
dolls, stuffed animals, puzzles, vehicles, puppets, educational and mechanical toys), ride-on toys and outdoor play
equipment, nursery items the baby products pack does not have, and old toys in museums: as PRODUCTS only, never a
child in the photo. Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and
returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes once with its JPEG and
then as (None, None, row) rows naming the same picture. The limit counts pictures.

Why: the owner is blind and wants the picture describer to say what a toy is (a shape sorter, a pull toy, a
kaleidoscope, a pedal car) and the US Consumer Product Safety Commission's safety notes that go with it (choking on
small parts, magnets, button batteries, ride-ons, playgrounds and baby walkers), for buying, sorting and checking
toys for a child.

No children: every Commons file whose words name a child (home_packs adults_only: child, kid, boy, girl, baby,
toddler and their other-language words) or say someone is playing (NO_PLAYING) is left out, and the nursery items
are read through NO_CHILD (a baby product's own name, "baby walker", is allowed; a baby is not). Open Images photos
with a confirmed child, person or face are left out (NO_PEOPLE_LABELS). Answers say only what the category, label
or museum record says.

The safety notes (the same words in the kit's toys_sources.py) are the CPSC's published advice, said as such
(cpsc.gov itself refuses programs, so its pages are links only; the reference library's CPSC child safety book
parent:cpsc_child_safety and the recall books recalls:* hold the rest):
  SMALL_PARTS_NOTE  toys with small parts are not for children under 3; small balls, marbles and balloons choke.
  MAGNET_NOTE       swallowed strong magnets can join up inside the body: get emergency care at once (said by
                    the toys book and the kit; no picture category here is about magnets).
  BATTERY_NOTE      button and coin batteries: keep battery doors screwed shut; one swallowed can burn the throat
                    in two hours: go to the emergency room at once.
  RIDE_NOTE         a helmet for riding toys; keep riding toys away from cars, stairs and pools.
  PLAYGROUND_NOTE   soft surfacing (wood chips, sand, rubber) under and around play equipment; watch children.
  WALKER_NOTE       baby walkers can roll down stairs: block stairs, or choose a stationary activity centre.
  RECALL_NOTE       check recalls at SaferProducts.gov and register the product with its maker.

The packs (TOYS_PACKS):
  commons_toys_by_type        Wikimedia Commons (CC0, public domain or CC BY files only): toy vehicles, trucks,
                              boats, aircraft and robots, toy blocks and wooden blocks, rag dolls, Barbie dolls and
                              dollhouses, plush and soft toys, Beanie Babies, tin, wind-up and mechanical toys, toy
                              soldiers, kaleidoscopes, Slinky, Play-Doh and Plasticine, hand and finger puppets,
                              toy pianos, rattles, rubber ducks, pinwheels, water guns, toy kitchens and
                              telephones, Hot Wheels, Playmobil, Duplo, K'Nex, Meccano, Kapla, Tinkertoy, Lincoln
                              Logs, Etch A Sketch, View-Master, wooden puzzles, pull toys, educational toys and shape
                              sorters.
  commons_ride_ons_playgrounds  Commons: rocking and hobby horses, tricycles, ride-on toys, toy wagons, pedal cars,
                              playground equipment, slides, swings, seesaws, jungle gyms, sandboxes, roundabouts and
                              playhouses.
  commons_nursery_more        Commons: baby walkers, changing tables, cradles, diapers, diaper bags and toy chests.
  commons_museum_toys         Commons: antique toys and toys in museums (mostly museum photos).
  met_toys                    The Metropolitan Museum of Art (CC0): dolls, toys, rattles, tops, marbles and toy
                              figures named so in the object's own record (MET_WORDS).
  open_images_toys            Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                              LEGO and construction sets, toy vehicles, action and animal figures, Barbie and
                              Japanese dolls, plush toys, baby and bath toys, puppets, dollhouses, educational
                              toys, marbles, kaleidoscopes, pinwheels, yo-yos and more, nursery furniture. No label
                              is asked twice (packs/test_gaps_pictures.py checks).

Not repeated here (other packs have them): commons_toys_sports_music (teddy bears, stuffed toys, dolls, action
figures, toy trains, LEGO, building blocks, jigsaws, Rubik's Cubes, yo-yos, kites, tops, board games, dice,
dominoes), the games packs (board, card and puzzle games, fidget toys), commons_baby_products and
open_images_baby_products (bottles, car seats, cribs, high chairs, playpens, monitors, pacifiers, teethers, gates,
strollers), wikidata_toys_games, the kit's cpsc_recalls, and the Open Images labels other packs ask (Toy, Doll,
Teddy bear, Stuffed toy, Toy block, Jigsaw puzzle, Kite, Playground, Playground slide, Tricycle, Kick scooter, Baby
rattle, Infant bed, Diaper and others). Sports equipment is another helper's collection. What was looked at and
left out (the Smithsonian, the Strong Museum, the V&A Museum of Childhood) is in the kit's toys_sources.py.

    python packs/toys_packs.py commons_toys_by_type --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from outdoor_cooking_packs import with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

SMALL_PARTS_NOTE = ("Choking (CPSC): toys with small parts are not for children under 3; follow the age on the "
                    "label, and keep small balls, marbles and balloons away from young children.")
MAGNET_NOTE = ("Magnets (CPSC): strong magnets that are swallowed can pull together inside the body and cause "
               "serious harm: get emergency medical care at once.")
BATTERY_NOTE = ("Button batteries (CPSC): keep battery doors screwed shut and spare batteries out of reach; a "
                "swallowed button or coin battery can burn the throat in as little as two hours: go to the emergency "
                "room at once.")
RIDE_NOTE = ("Riding toys (CPSC): wear a helmet, and keep riding toys away from cars, streets, stairs and swimming "
             "pools.")
PLAYGROUND_NOTE = ("Playground safety (CPSC): look for soft surfacing such as wood chips, sand or rubber under and "
                   "around the equipment, check for broken parts and sharp edges, and watch children at play.")
WALKER_NOTE = ("Baby walkers (CPSC): walkers can roll down stairs; block every stairway, or choose a stationary "
               "activity centre instead.")
RECALL_NOTE = "Recalls: check SaferProducts.gov for recalls, and register the product with its maker."
SLEEP_NOTE = ("Safe sleep (CPSC): a baby sleeps on its back on a firm, flat surface with nothing else in the "
              "cradle or crib.")

ASK_WHAT = "What is this?"
TOY_NOTES = f"{SMALL_PARTS_NOTE} {RECALL_NOTE}"

# Files whose words say someone is playing (the photo then shows children, even when it does not say so).
NO_PLAYING = re.compile(r"^(?!.*\b(play(ing|s|ed)? (with|on|in|at)|playing|plays|riding|rides|swinging|sliding|"
                        r"people|persons?|family|families|wom[ae]n|m[ae]n|mother|father|parents?)\b)", re.I | re.S)
# The nursery items: a baby product's own name ("baby walker") is allowed, any other child word leaves a file out.
NO_CHILD = re.compile(r"^(?!.*(\b(child\w*|kids?|boys?|girls?|toddlers?|infants?|newborns?|sons?|daughters?|"
                      r"enfants?|kinder|ni[nñ][oa]s?|bambin[oi]|people|wom[ae]n|m[ae]n|mother|father|parents?)\b|"
                      r"\bbab(y|ies)\b(?!['’]?s? ?(walkers?|changing|cradles?|diapers?|nappies|bags?|chests?|"
                      r"furniture|products?)\b)))", re.I | re.S)


def thing(category, words, notes=TOY_NOTES, deeper=False, pattern=NO_PLAYING):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)], pattern): only files whose words the pattern accepts are taken."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))], pattern)


# ----------------------------------------------------------------- Commons: toys by type

BATTERY_TOY = f"{SMALL_PARTS_NOTE} {BATTERY_NOTE} {RECALL_NOTE}"
TOYS = [
    thing("Toy vehicles", "a toy vehicle", deeper=True),
    thing("Toy trucks", "a toy truck"),
    thing("Toy boats", "a toy boat", deeper=True),
    thing("Toy aircraft", "a toy aircraft", deeper=True),
    thing("Toy robots", "a toy robot", BATTERY_TOY, True),
    thing("Toy blocks", "toy blocks", deeper=True),
    thing("Wooden blocks", "wooden blocks", deeper=True),
    thing("Rag dolls", "a rag doll (a cloth doll)", deeper=True),
    thing("Barbie dolls", "a Barbie doll", deeper=True),
    thing("Dollhouses", "a dollhouse", deeper=True),
    thing("Plush toys", "a plush toy (a soft toy)", deeper=True),
    thing("Soft toys", "a soft toy", deeper=True),
    thing("Beanie Babies", "a Beanie Baby, a small bean-filled soft toy"),
    thing("Tin toys", "a tin toy (a toy made of metal sheet)", deeper=True),
    thing("Wind-up toys", "a wind-up toy (a clockwork toy)", deeper=True),
    thing("Mechanical toys", "a mechanical toy", deeper=True),
    thing("Toy soldiers", "toy soldiers"),
    thing("Kaleidoscopes", "a kaleidoscope: you look through it and turn it to see coloured patterns", deeper=True),
    thing("Slinky", "a Slinky, a toy spring that walks down stairs", deeper=True),
    thing("Play-Doh", "Play-Doh modelling dough", "Play-Doh is not food; keep it away from children who may eat it."),
    thing("Plasticine", "Plasticine (modelling clay)", deeper=True),
    thing("Hand puppets", "a hand puppet", deeper=True),
    thing("Finger puppets", "finger puppets"),
    thing("Toy pianos", "a toy piano", deeper=True),
    thing("Rattles", "a rattle", deeper=True),
    thing("Rubber ducks", "a rubber duck (a bath toy)", deeper=True),
    thing("Pinwheels", "a pinwheel (a toy windmill on a stick)", deeper=True),
    thing("Water guns", "a water gun (a squirt gun)", deeper=True),
    thing("Toy kitchens", "a toy kitchen", deeper=True),
    thing("Toy telephones", "a toy telephone", deeper=True),
    thing("Hot Wheels", "Hot Wheels toy cars", deeper=True),
    thing("Playmobil", "Playmobil toy figures and sets", deeper=True),
    thing("Duplo", "LEGO Duplo, large toy bricks for young children", deeper=True),
    thing("K'Nex", "K'Nex, a construction toy of rods and connectors"),
    thing("Meccano", "Meccano, a construction toy of metal strips, nuts and bolts", deeper=True),
    thing("Kapla", "Kapla, thin wooden planks for building", deeper=True),
    thing("Tinkertoy", "Tinkertoy, a construction toy of wooden spools and sticks"),
    thing("Lincoln Logs", "Lincoln Logs, toy notched logs for building cabins"),
    thing("Etch A Sketch", "an Etch A Sketch drawing toy, worked with two knobs", deeper=True),
    thing("View-Master", "a View-Master, a toy viewer for picture reels", deeper=True),
    thing("Wooden puzzles", "a wooden puzzle", deeper=True),
    thing("Pull toys", "a pull toy, pulled along on a string", deeper=True),
    thing("Educational toys", "an educational toy", deeper=True),
    thing("Shape sorters", "a shape sorter: blocks go through holes of the same shape"),
]

# ----------------------------------------------------------------- Commons: ride-ons and playgrounds

RIDE_NOTES = f"{RIDE_NOTE} {RECALL_NOTE}"
PLAY_NOTES = PLAYGROUND_NOTE
RIDE_ONS = [
    thing("Rocking horses", "a rocking horse", RECALL_NOTE, True),
    thing("Hobby horses", "a hobby horse (a horse's head on a stick)", RECALL_NOTE, True),
    thing("Tricycles", "a tricycle", RIDE_NOTES, True),
    thing("Ride-on toys", "a ride-on toy", RIDE_NOTES, True),
    thing("Toy wagons", "a toy wagon (a pull-along cart)", RIDE_NOTES, True),
    thing("Pedal cars", "a pedal car", RIDE_NOTES, True),
    thing("Playground equipment", "playground equipment", PLAY_NOTES, True),
    thing("Playground slides", "a playground slide", PLAY_NOTES, True),
    thing("Swings", "a swing", PLAY_NOTES, True),
    thing("Seesaws", "a seesaw", PLAY_NOTES, True),
    thing("Jungle gyms", "a jungle gym (a climbing frame)", PLAY_NOTES, True),
    thing("Sandboxes", "a sandbox (a sandpit)", "Cover a sandbox when it is not in use.", True),
    thing("Playground roundabouts", "a playground roundabout (merry-go-round)", PLAY_NOTES, True),
    thing("Playhouses", "a playhouse", PLAY_NOTES, True),
]

# ----------------------------------------------------------------- Commons: nursery items and museum toys

NURSERY = [
    thing("Baby walkers", "a baby walker", f"{WALKER_NOTE} {RECALL_NOTE}", True, NO_CHILD),
    thing("Changing tables", "a changing table", "Keep one hand on the baby, and use the safety strap.", True,
          NO_CHILD),
    thing("Cradles", "a cradle", f"{SLEEP_NOTE} {RECALL_NOTE}", True, NO_CHILD),
    thing("Diapers", "a diaper (nappy)", "", True, NO_CHILD),
    thing("Diaper bags", "a diaper bag (a changing bag)", "", False, NO_CHILD),
    thing("Toy chests", "a toy chest", "Toy chests (CPSC): choose one with no lid or a lid that stays open and does "
                                       "not slam, with air holes.", False, NO_CHILD),
]
MUSEUM_TOYS = [
    thing("Antique toys", "an antique toy", "", True),
    thing("Toys in museums", "a toy in a museum", "", True),
]


def build_commons_toys_by_type(limit):
    """The commons_toys_by_type pack (see the module docstring); no file whose words name a child."""
    from home_packs import build_commons_topic
    return build_commons_topic(TOYS, limit, "toytype", adults_only=True)


def build_commons_ride_ons_playgrounds(limit):
    """The commons_ride_ons_playgrounds pack (see the module docstring); no file whose words name a child."""
    from home_packs import build_commons_topic
    return build_commons_topic(RIDE_ONS, limit, "rideplay", adults_only=True)


def build_commons_nursery_more(limit):
    """The commons_nursery_more pack (see the module docstring): NO_CHILD instead of adults_only, so a product's own
    name ("baby walker") does not leave its picture out."""
    from home_packs import build_commons_topic
    return build_commons_topic(NURSERY, limit, "nursery")


def build_commons_museum_toys(limit):
    """The commons_museum_toys pack (see the module docstring); no file whose words name a child."""
    from home_packs import build_commons_topic
    return build_commons_topic(MUSEUM_TOYS, limit, "museumtoy", adults_only=True)


# ----------------------------------------------------------------- the Met (CC0)

MET_SEARCHES = ("doll", "toy", "rattle", "spinning top", "marbles", "whistle toy")
MET_WORDS = re.compile(r"\b(dolls?|toys?|rattles?|tops?|marbles?|dollhouse|doll's house|puppets?|marionettes?)\b",
                       re.I)


def met_themed(o):
    """True when a Met object belongs to met_toys (museum_general_packs leaves it to this pack)."""
    return bool(MET_WORDS.search(o.get("objectName") or ""))


def build_met_toys(limit):
    """The met_toys pack (see the module docstring)."""
    from archive_packs import finish_marked
    from personal_care_packs import met_search_items
    items = met_search_items(MET_SEARCHES, met_themed, int(limit * 1.2) + 2, "met-toys")
    return finish_marked("met_toys", items, limit, workers=4, pause=0.2)


# ----------------------------------------------------------------- Open Images

NO_PEOPLE_LABELS = ("Person", "Human face", "Woman", "Man", "Human head", "Human body", "Human hand")
TOYS_OI = [
    group("What toys are in this picture?",
          {"Lego": "LEGO bricks", "Construction set toy": "a construction set", "Interlocking block":
           "interlocking blocks", "Toy vehicle": "a toy vehicle", "Action figure": "an action figure",
           "Animal figure": "an animal figure", "Barbie": "a Barbie doll", "Japanese dolls": "Japanese dolls",
           "Plush": "a plush toy", "Puppet": "a puppet", "Dollhouse": "a dollhouse", "Wind-up toy": "a wind-up toy",
           "Executive toy": "an executive desk toy"}, TOY_NOTES),
    group("What baby or bath toys are in this picture?",
          {"Baby toys": "baby toys", "Bath toy": "a bath toy", "Rattle": "a rattle"}, TOY_NOTES),
    group("What learning or play things are in this picture?",
          {"Educational toy": "an educational toy", "Abacus": "an abacus", "Marble (Toy)": "marbles",
           "Kaleidoscope": "a kaleidoscope", "Pinwheel": "a pinwheel", "Yo-yo": "a yo-yo",
           "Bubble blowing toy": "a bubble-blowing toy", "Water gun": "a water gun", "Hula hoop": "a hula hoop",
           "Fitness toy": "an exercise toy"}, TOY_NOTES),
    group("What play equipment is in this picture?",
          {"Playhouse": "a playhouse", "Seesaw": "a seesaw"}, PLAYGROUND_NOTE),
    group("What nursery furniture is in this picture?",
          {"Changing table": "a changing table", "Bunk bed": "a bunk bed", "Nursery": "a nursery room"},
          RECALL_NOTE),
]


def build_open_images_toys(limit):
    """open_images_toys (see the module docstring): every photo with a confirmed child, person or face left out."""
    from expression_packs import OI_CHILD
    return with_yes_notes(build_oi_gap("open_images_toys", TOYS_OI, limit, 9421,
                                       without=tuple(OI_CHILD) + NO_PEOPLE_LABELS), TOYS_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories; no file whose words name a child.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below; no photo with a child in it.")
MET_LICENCE = ("The Metropolitan Museum of Art, Open Access (CC0, https://www.metmuseum.org/about-the-met/"
               "policies-and-documents/open-access): public-domain objects, each credited below.")
TOYS_PACKS = {
    "commons_toys_by_type": (build_commons_toys_by_type, COMMONS_LICENCE.format(
        what="toy vehicle, block, doll, plush, mechanical, puppet, construction and educational toy")),
    "commons_ride_ons_playgrounds": (build_commons_ride_ons_playgrounds, COMMONS_LICENCE.format(
        what="rocking horse, tricycle, ride-on toy, pedal car and playground equipment")),
    "commons_nursery_more": (build_commons_nursery_more, COMMONS_LICENCE.format(
        what="baby walker, changing table, cradle, diaper and toy chest")),
    "commons_museum_toys": (build_commons_museum_toys, COMMONS_LICENCE.format(what="antique toy and museum toy")),
    "met_toys": (build_met_toys, MET_LICENCE),
    "open_images_toys": (build_open_images_toys, OI_LICENCE),
}
TOYS_LIMITS = {
    "commons_toys_by_type": 2000,          # 44 categories
    "commons_ride_ons_playgrounds": 1200,  # 14 categories
    "commons_nursery_more": 300,           # 6 categories, few files
    "commons_museum_toys": 300,            # 2 categories with their subcategories
    "met_toys": 500,                       # the Met's dolls, toys and rattles
    "open_images_toys": 2500,              # 33 labels; LEGO and toy vehicles have most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
TOYS_COMMONS_KEYS = ("commons_toys_by_type", "commons_ride_ons_playgrounds", "commons_nursery_more",
                     "commons_museum_toys")
# The Commons category specs of the packs (for the self-test).
TOYS_SPECS = TOYS + RIDE_ONS + NURSERY + MUSEUM_TOYS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a toys pack builder.")
    parser.add_argument("key", choices=sorted(TOYS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = TOYS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
