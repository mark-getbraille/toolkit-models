"""Picture packs for HOME REPAIR AND UPKEEP and PEST CONTROL (the owner's request of 2026-11-22: home repair, upkeep
and handcrafts; the textile crafts are in textile_crafts_packs.py). Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than
one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

What was already in other packs, and so is NOT repeated here (each Commons category is asked by one pack only;
packs/test_home_crafts.py checks it): plumbing parts, valves, traps, taps, toilets, outlets, switches, breakers,
panels and wire (hardware_packs commons_plumbing_electrical), hand and trade tools, ladders, power and garden tools,
snow blowers and lawn mowers (hardware_packs), breaker panels, fuse boxes, meters, stopcocks, sump pumps, furnaces,
smoke and carbon monoxide alarms (home_safety_packs), household hazards such as frayed cords, leaks and mould
(household_hazard_packs), bicycle parts, chains, tyres and repair stands (mechanical_packs), household pest species,
bed bugs, cockroaches, termites, ticks, mosquitoes, mousetraps and water damage (home_packs commons_pests and
open_images_home), insecticides and pesticides in their containers (chemical_packs), and paint rollers, masking tape,
peeling paint and house painting (chemical_packs and hardware_packs).

Answers say only what the source says: a Commons category's name (with one short line written here on what that kind
of thing is), or an Open Images label people confirmed. No repair instructions are made up, nothing is guessed about
the state of a part, and no reading is invented. Safety notes (fixed sentences, below) follow the answers about
electrical work, gas, ladders and roofs, engines, pesticides, poisons and traps, stinging insects, lead and mould.

The packs (all open: CC0, public domain or CC BY, checked file by file; labels CC BY 4.0 for Open Images):
  commons_home_repair        Wikimedia Commons: building repairs, pipe patching, plumbing tools, grease traps, lead
                             pipes (with the lead note), toilet tanks and seats, tap aerators, drains, caulking,
                             draught excluders, roofing, slate and metal roofs and rain gutters (with the ladder and
                             roof note), gutter guards, laminate, vinyl and linoleum floors, floor sanding and sanding
                             (with the lead paint note), glaziers, chimney sweeps, damp (with the mould note), window
                             cleaning, spring cleaning, power strips (with the electrical note), handymen and repair
                             cafés. People work in many of these photos: describing only.
  commons_locks_engines_bikes Commons: door locks, pin tumbler locks, locksmithing, locksmith tools and shops, key
                             blanks and smart locks; two- and four-stroke and Briggs & Stratton small engines (with the
                             engine note); bicycle maintenance, repair shops and stations, repair kits, multi tools,
                             pumps, chain tools, chain wear indicators, chain whips, crank extractors, freewheel
                             removers, pedal wrenches, tyre patches, tyre levers, wheel truing stands, bottom bracket
                             and spoke tools.
  commons_pest_control       Commons: rat traps and glue traps (with the trap note), rodenticides and pesticide labels
                             (with the pesticide note), bug zappers, mosquito nets, pest control, fumigation (with its
                             own note), integrated pest management, pigeon control, bat houses and ant trails; and the
                             household pests home_packs commons_pests does not ask about: pantry beetles and weevils
                             (red flour beetle, rice weevil, cigarette and drugstore beetles), woodworm and the house
                             longhorn beetle, brown and black rats, human and dog fleas, house dust mites, firebrats,
                             earwigs, house centipedes, pill bugs, varied carpet beetles, the common wasp and the
                             European paper wasp (with the sting note), black garden and pavement ants, and the
                             smokybrown and brown-banded cockroaches. "What pest is this?" -> "This looks like a rice
                             weevil. It infests stored rice, wheat and other grains." Files whose words speak of
                             dissection, blood or a carcass are left out (NO_GORE).
  open_images_home_upkeep    Open Images V7: roofs, rain gutters, chimneys, attics, basements, garage doors, window
                             screens, wallpaper, plaster, flooring and carpet, laundry rooms; plumbing, valves,
                             sinks, bathtub spouts and hoses; boilers (with the gas note); electrical wiring,
                             supplies and switches (with the electrical note); locks, hinges and door knockers; wood
                             stain and varnish; hammer drills, garden tools, riding mowers and snow blowers (with the
                             engine note); laundry supplies;
                             bicycle parts; and pests and wildlife (insects, beetles, moths, bees, rodents, squirrels,
                             raccoons, bats, gophers, birds' nests and beehives). Labels no other pack asks
                             (packs/test_home_crafts.py checks). Labels that judge people by their trade (Electrician,
                             Roofer, Handyman, Bicycle mechanic, Cobbler) are left out, as the drinks packs leave out
                             Bartender.

What was looked at and left out (Bugwood's insect images, CDC PHIL pest photos already in other packs, extension
service photos and others) is in training-kit/kit/home_crafts_sources.py, with the share-alike Commons files.

    python packs/home_upkeep_packs.py commons_pest_control --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

# ----------------------------------------------------------------- the safety notes (fixed sentences)

ELECTRICAL_NOTE = ("Electrical safety: turn the power off at the breaker or fuse box and check it is off with a "
                   "tester before touching wiring; if in doubt, call a licensed electrician.")
POWER_STRIP_NOTE = ("Electrical safety: do not plug one power strip into another or overload it, and replace any "
                    "strip or cord that is damaged or gets hot.")
GAS_NOTE = ("Gas safety: if you smell gas, leave at once and call the gas company or 911 from outside. Gas and oil "
            "boilers should be serviced every year by a qualified technician, with a carbon monoxide alarm nearby.")
LADDER_NOTE = ("Ladder and roof safety: falls from ladders and roofs cause serious injuries; set a ladder on firm, "
               "level ground, keep three points of contact, stay off wet or steep roofs, and have someone with you.")
ENGINE_NOTE = ("Engine safety: run petrol engines only outdoors (their exhaust carbon monoxide can kill), let them "
               "cool before refuelling, and disconnect the spark plug before working on a blade.")
PESTICIDE_NOTE = ("Pesticide safety: read and follow the whole label (the label is the law), keep the product away "
                  "from children and pets, and store it in its original container. Poison Control: 1-800-222-1222 "
                  "in the US.")
TRAP_NOTE = ("Set traps and bait stations where children and pets cannot reach them. Do not sweep or vacuum rodent "
             "droppings dry: wear gloves, wet them with disinfectant first, then wipe them up (CDC advice).")
FUMIGATION_NOTE = ("Fumigation is done only by licensed professionals: the gas is deadly, so nobody may go back in "
                   "until the building has been cleared.")
STING_NOTE = ("Keep away from the nest: wasps sting to defend it. Anyone allergic to stings should keep their "
              "emergency medicine with them; call 911 for a severe reaction.")
LEAD_PAINT_NOTE = ("Homes built before 1978 may have lead paint: do not dry-sand, scrape or burn old paint without "
                   "lead-safe methods (the EPA's Renovate Right guide).")
LEAD_PIPE_NOTE = ("Lead pipes can put lead into drinking water: have the water tested and ask the water utility about "
                  "replacing them.")
MOULD_NOTE = ("Fix the source of the moisture first; the EPA advises that mould covering more than about 10 square "
              "feet is best cleaned up by a professional.")
LABEL_NOTE = ("A pesticide label gives the signal word (Caution, Warning or Danger), first aid, directions for use, "
              "storage and disposal, and the EPA registration number; read all of it before use.")

ASK_WHAT = "What is this?"
ASK_HAPPENING = "What is happening here?"
PEST_Q = "What pest is this?"
# Files whose own words speak of dissection, blood, a carcass or a dead animal are left out of the pest pack (only
# what is ordinary in a pest guide is kept). A negative look-ahead, so it works as build_commons_topic's "must".
NO_GORE = re.compile(r"^(?!.*\b(dissect\w*|blood\w*|carcass\w*|corpses?|dead|killed|gore|gory|entrails|"
                     r"decapitat\w*|mutilat\w*|roadkill)\b)", re.I | re.S)


def what(category, words, note="", deeper=False, must=None):
    """A Commons spec for home_packs.build_commons_topic: "What is this?" -> "This is <words>." and the note after;
    deeper: its subcategories too; must: only files whose title or words match this pattern."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {note}" if note else ""))])
    return spec + (must,) if must is not None else spec


def doing(category, words, note="", deeper=False):
    """A Commons spec for a scene: "What is happening here?" -> "This shows <words>." and the note after."""
    return (category, deeper, [(ASK_HAPPENING, f"This shows {words}." + (f" {note}" if note else ""))])


def pest(category, name, about="", note="", deeper=True):
    """A Commons spec for a pest species: "What pest is this?" -> "This looks like <name>. <about>" and the note;
    files with gory words are left out (NO_GORE)."""
    answer = f"This looks like {name}." + (f" {about}" if about else "") + (f" {note}" if note else "")
    return (category, deeper, [(PEST_Q, answer)], NO_GORE)


# ----------------------------------------------------------------- Commons: home repair and upkeep

HOME_REPAIR = [
    doing("Building repairs", "building repairs under way"),
    what("Pipe patching", "a patched pipe: a clamp, wrap or patch over a leak in a pipe"),
    what("Plumbing tools", "a plumbing tool"),
    what("Grease traps", "a grease trap, which catches fat and oil before they reach the drains"),
    what("Lead pipe plumbing", "lead water pipe", LEAD_PIPE_NOTE),
    what("Toilet tanks", "a toilet tank (cistern), which holds the water for the flush", deeper=True),
    what("Toilet seats", "a toilet seat"),
    what("Faucet aerators", "a tap (faucet) aerator, the small screen at the tip of a tap that mixes air into the "
                            "water"),
    what("Drains", "a drain"),
    doing("Caulking", "caulking: sealing a joint or gap with a bead of sealant"),
    what("Draught excluders", "a draught excluder, which stops cold air coming in under or around a door"),
    what("Roofing", "roofing", LADDER_NOTE, deeper=True),
    what("Slate roofs", "a slate roof", LADDER_NOTE),
    what("Metal roofs", "a metal roof", LADDER_NOTE),
    what("Rain gutters", "a rain gutter, which carries rain from the edge of the roof to the downspout",
         LADDER_NOTE),
    what("Gutter guards", "a gutter guard, a screen that keeps leaves out of a gutter", LADDER_NOTE),
    what("Laminate flooring", "laminate flooring", deeper=True),
    what("Vinyl flooring", "vinyl flooring", deeper=True),
    what("Linoleum", "linoleum flooring"),
    doing("Floor sanding", "floor sanding: sanding a wooden floor before it is refinished", LEAD_PAINT_NOTE),
    doing("Sanding", "sanding: smoothing a surface with sandpaper or a sander", LEAD_PAINT_NOTE),
    doing("Glaziers", "a glazier at work: fitting or replacing glass"),
    doing("Chimney sweeps", "a chimney sweep, who cleans soot out of chimneys", LADDER_NOTE),
    what("Damp", "damp in a building: moisture and the stains or mould it brings", MOULD_NOTE, deeper=True),
    doing("Window cleaning", "window cleaning", LADDER_NOTE, deeper=True),
    doing("Spring cleaning", "spring cleaning", deeper=True),
    what("Power strips", "a power strip: a row of sockets on a lead", POWER_STRIP_NOTE, deeper=True),
    doing("Handyman", "a handyman at work"),
    doing("Repair Cafés", "a repair café, where volunteers help people mend their things", deeper=True),
]

# ----------------------------------------------------------------- Commons: locks, small engines and bicycles

LOCKS_ENGINES_BIKES = [
    what("Door locks", "a door lock"),
    what("Pin tumbler locks", "a pin tumbler lock, the common cylinder lock whose key lifts a row of pins to the "
                              "right height", deeper=True),
    doing("Locksmithing", "locksmithing: making, fitting, repairing and opening locks", deeper=True),
    what("Locksmith tools", "a locksmith's tool", deeper=True),
    what("Locksmith shops", "a locksmith's shop"),
    what("Key blanks", "key blanks: uncut keys that a locksmith cuts to fit a lock"),
    what("Smart locks", "a smart lock, an electronic door lock opened with a code, a card or a phone"),
    what("Two-stroke engines", "a two-stroke engine, the kind used on chainsaws, string trimmers and small "
                               "motorcycles", ENGINE_NOTE),
    what("Four-stroke engines", "a four-stroke engine", ENGINE_NOTE),
    what("Briggs & Stratton engines", "a Briggs & Stratton small engine, the kind used on lawn mowers and other "
                                      "garden machines", ENGINE_NOTE),
    doing("Bicycle maintenance", "bicycle maintenance", deeper=True),
    what("Bicycle repair shops", "a bicycle repair shop"),
    what("Bicycle repair stations", "a bicycle repair station: a public stand with tools and a pump", deeper=True),
    what("Bicycle repair kits", "a bicycle repair kit", deeper=True),
    what("Bicycle multi tools", "a bicycle multi-tool: several hex keys, screwdrivers and other tools folded into "
                                "one", deeper=True),
    what("Bicycle pumps", "a bicycle pump", deeper=True),
    what("Chain tools", "a chain tool, which pushes a pin out to break or join a bicycle chain", deeper=True),
    what("Chain wear indicators", "a chain wear indicator, a gauge that shows when a bicycle chain has stretched"),
    what("Chain whips", "a chain whip, which holds a bicycle's rear sprockets still while they are unscrewed"),
    what("Crank extractors", "a crank extractor (crank puller), which pulls a bicycle's crank arm off its axle"),
    what("Freewheel removers", "a freewheel remover, which unscrews a bicycle's freewheel"),
    what("Pedal wrenches", "a pedal wrench, a long thin spanner for bicycle pedals"),
    what("Tire patches", "a tyre patch, glued over a hole in an inner tube", deeper=True),
    what("Tyre levers", "tyre levers, which lift a tyre off the wheel rim"),
    what("Wheel truing stands", "a wheel truing stand, which holds a bicycle wheel while its spokes are adjusted "
                                "so it runs straight"),
    what("Bottom bracket tools", "a bottom bracket tool, for taking out and fitting a bicycle's bottom bracket"),
    what("Spoke tools", "a spoke tool (spoke key), which tightens or loosens the nipples of bicycle spokes",
         deeper=True),
]

# ----------------------------------------------------------------- Commons: pest control and more household pests

PEST_CONTROL = [
    what("Rat traps", "a rat trap", TRAP_NOTE, deeper=True),
    what("Glue traps", "a glue trap (sticky trap)", TRAP_NOTE, deeper=True),
    what("Rodenticides", "rat or mouse poison (a rodenticide)", PESTICIDE_NOTE + " " + TRAP_NOTE),
    what("Pesticide labels", "a pesticide label", LABEL_NOTE),
    what("Bug zappers", "a bug zapper, an electric insect killer whose light draws insects in"),
    what("Mosquito nets", "a mosquito net"),
    doing("Pest control", "pest control"),
    doing("Fumigation", "fumigation: a building or space sealed and filled with a pesticide gas to kill pests",
          FUMIGATION_NOTE, deeper=True),
    doing("Integrated pest management", "integrated pest management (IPM): preventing and controlling pests with the "
                                        "least risk, by sealing gaps, removing food and water, watching for pests and "
                                        "using pesticides only when needed"),
    what("Pigeon control", "pigeon control: spikes, nets or wires that keep pigeons off ledges", deeper=True),
    what("Bat houses", "a bat house, a box where bats can roost instead of in a building", deeper=True),
    what("Ant trails", "a trail of ants"),
    pest("Tribolium castaneum", "a red flour beetle", "It infests flour, cereal and other dry food."),
    pest("Sitophilus oryzae", "a rice weevil", "It infests stored rice, wheat and other grains."),
    pest("Lasioderma serricorne", "a cigarette beetle", "It infests spices, dried food and tobacco."),
    pest("Stegobium paniceum", "a drugstore beetle (biscuit beetle)", "It infests dried food, spices and books."),
    pest("Anobium punctatum", "a common furniture beetle (woodworm)", "Its larvae bore into wooden furniture and "
                                                                      "timber, leaving small round holes."),
    pest("Hylotrupes bajulus", "a house longhorn beetle", "Its larvae bore into softwood roof timbers."),
    pest("Rattus norvegicus", "a brown rat (Norway rat)"),
    pest("Rattus rattus", "a black rat (roof rat)"),
    pest("Pulex irritans", "a human flea"),
    pest("Ctenocephalides canis", "a dog flea"),
    pest("Dermatophagoides pteronyssinus", "a house dust mite", "Dust mites are too small to see without a "
                                                                "magnifier; they live in bedding and carpets and can "
                                                                "set off allergies and asthma."),
    pest("Thermobia domestica", "a firebrat, an insect like a silverfish that likes warm places"),
    pest("Forficula auricularia", "a European earwig"),
    pest("Scutigera coleoptrata", "a house centipede", "It has very long legs and eats other household insects."),
    pest("Armadillidium vulgare", "a pill bug (woodlouse)", "It rolls into a ball and lives in damp places."),
    pest("Anthrenus verbasci", "a varied carpet beetle", "Its larvae eat wool, fur, feathers and stored food."),
    pest("Vespula vulgaris", "a common wasp", "", STING_NOTE),
    pest("Polistes dominula", "a European paper wasp", "", STING_NOTE),
    pest("Lasius niger", "a black garden ant"),
    pest("Tetramorium caespitum", "a pavement ant"),
    pest("Periplaneta fuliginosa", "a smokybrown cockroach"),
    pest("Supella longipalpa", "a brown-banded cockroach"),
]


def build_commons_home_repair(limit):
    """The commons_home_repair pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(HOME_REPAIR, limit, "homerepair")


def build_commons_locks_engines_bikes(limit):
    """The commons_locks_engines_bikes pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(LOCKS_ENGINES_BIKES, limit, "lockbike")


def build_commons_pest_control(limit):
    """The commons_pest_control pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PEST_CONTROL, limit, "pestctl")


# ----------------------------------------------------------------- Open Images: home upkeep and pests

UPKEEP_OI = [
    group("What parts of the house are in this picture?",
          {"Roof": "a roof", "Rain gutter": "a rain gutter", "Chimney": "a chimney", "Attic": "an attic",
           "Basement": "a basement", "Garage door": "a garage door", "Window screen": "a window screen",
           "Wallpaper": "wallpaper", "Plaster": "plaster", "Flooring": "flooring",
           "Laminate flooring": "laminate flooring", "Carpet": "carpet", "Laundry room": "a laundry room"}),
    group("What plumbing is in this picture?",
          {"Plumbing": "plumbing", "Valve": "a valve", "Bathroom sink": "a bathroom sink",
           "Kitchen sink": "a kitchen sink", "Bathtub spout": "a bathtub spout", "Hose": "a hose"}),
    group("What heating equipment is in this picture?", {"Boiler": "a boiler"}, GAS_NOTE),
    group("What electrical things are in this picture?",
          {"Electrical wiring": "electrical wiring", "Electrical supply": "electrical supplies", "Switch": "a switch"},
          ELECTRICAL_NOTE),
    group("What door or lock hardware is in this picture?",
          {"Lock": "a lock", "Hinge": "a hinge", "Door knocker": "a door knocker"}),
    group("What wood finishes are in this picture?", {"Wood stain": "wood stain", "Varnish": "varnish"}),
    group("What tools are in this picture?", {"Hammer drill": "a hammer drill", "Garden tool": "a garden tool"}),
    group("What machines with engines are in this picture?",
          {"Riding mower": "a riding mower", "Snow blower": "a snow blower"}, ENGINE_NOTE),
    group("What laundry things are in this picture?", {"Laundry supply": "laundry supplies"}),
    group("What bicycle parts are in this picture?",
          {"Bicycle part": "a bicycle part", "Bicycle chain": "a bicycle chain", "Bicycle tire": "a bicycle tyre",
           "Bicycle wheel": "a bicycle wheel", "Bicycle drivetrain part": "a bicycle drivetrain part",
           "Bicycle pedal": "a bicycle pedal", "Bicycle saddle": "a bicycle saddle",
           "Bicycle handlebar": "bicycle handlebars", "Bicycle frame": "a bicycle frame"}),
    group("What pests or animals are in this picture?",
          {"Pest": "a pest", "Insect": "an insect", "Beetle": "a beetle", "Moth": "a moth", "Bee": "a bee",
           "Rodent": "a rodent", "Squirrel": "a squirrel", "Raccoon": "a raccoon", "Bat (Animal)": "a bat",
           "Gopher": "a gopher"}),
    group("What nests or hives are in this picture?", {"Bird nest": "a bird's nest", "Beehive": "a beehive"}),
]


def build_open_images_home_upkeep(limit):
    """open_images_home_upkeep (see the module docstring)."""
    return build_oi_gap("open_images_home_upkeep", UPKEEP_OI, limit, 9301)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
HOME_UPKEEP_PACKS = {
    "commons_home_repair": (build_commons_home_repair, COMMONS_LICENCE.format(
        what="home repair, plumbing, roofing, gutter, flooring, glazing, damp and cleaning")),
    "commons_locks_engines_bikes": (build_commons_locks_engines_bikes, COMMONS_LICENCE.format(
        what="lock and locksmithing, small engine and bicycle repair tool")),
    "commons_pest_control": (build_commons_pest_control, COMMONS_LICENCE.format(
        what="pest control and household pest species")),
    "open_images_home_upkeep": (build_open_images_home_upkeep, OI_LICENCE),
}
HOME_UPKEEP_LIMITS = {
    "commons_home_repair": 1200,           # 29 categories, few files in some
    "commons_locks_engines_bikes": 900,    # 27 categories, many small
    "commons_pest_control": 1200,          # 34 categories
    "open_images_home_upkeep": 2500,       # 49 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
HOME_UPKEEP_COMMONS_KEYS = ("commons_home_repair", "commons_locks_engines_bikes", "commons_pest_control")
# Every Commons spec of these packs (for the self-test).
HOME_UPKEEP_SPECS = HOME_REPAIR + LOCKS_ENGINES_BIKES + PEST_CONTROL


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a home upkeep pack builder.")
    parser.add_argument("key", choices=sorted(HOME_UPKEEP_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = HOME_UPKEEP_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
