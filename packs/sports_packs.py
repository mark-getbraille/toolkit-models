"""Picture packs for SPORTS, a top-level section of the toolkit (the owner's request of 2026-11-22). Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes
or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row) rows
naming the same picture. The limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise sports equipment,
protective gear, the places sports are played and athletes in action, and to say the safety notes that go with them.

Answers say only what the source says (a Commons category's name, said in a fixed plain sentence written here, or an
Open Images label people confirmed), never a guess: no team, player, score or brand is named. Team logos and jerseys
are trademarks: no category here has a logo as its subject. Answers about protective gear and contact or combat sports
end with GEAR_NOTE (the same words in the kit's sports_sources.py):
  GEAR_NOTE   protective gear works only when it fits and is in good condition; after a blow to the head, stop
              playing and see a doctor (CDC HEADS UP).
  ICE_NOTE    natural ice: never go on it unless it is known to be thick enough.

The packs (SPORTS_PACKS):
  commons_sports_equipment   Wikimedia Commons (CC0, public domain or CC BY files only): cricket, field hockey and
                             rugby balls, cricket, softball and table tennis bats, field hockey and lacrosse sticks,
                             boxing and batting gloves, bowling pins, curling stones, épées, javelins, starting
                             blocks, hurdles, home plates, batting tees, pitching machines and stopwatches.
  commons_sports_gear        Commons: American football, batting, ice hockey, ski and racing helmets, shoulder pads,
                             shin guards, cricket pads, goaltender equipment, fencing masks, inline, figure and ice
                             hockey skates, ski boots, bindings and poles, goals and nets (football, ice hockey,
                             tennis, volleyball, basketball goals, goalposts), racing, track and time trial bicycles,
                             karts, racing wheelchairs and Formula One cars.
  commons_sports_venues      Commons: basketball, tennis, volleyball, beach volleyball, squash, badminton and netball
                             courts, ice rinks, American football and baseball fields, pitcher's mounds, dugouts,
                             running and athletics tracks, velodromes, bowling alleys, ski jumping hills, golf courses,
                             driving ranges, diving platforms, cricket pitches and grandstands.
  commons_sports_action      Commons: athletics events in action (high jump, long jump, javelin, shot put, discus,
                             hammer, hurdling), football, volleyball, field hockey, rugby, baseball and tennis
                             matches, and para sports (para ice hockey, powerchair and amputee football, para table
                             tennis) (SPORTS_ACTION). Adults only: files whose own
                             words name a child, youth, junior, school or an age group are left out. People-heavy:
                             describing only, never for picture-making.
  open_images_sports         Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                             sports being played (soccer, handball, rugby, lacrosse, softball, field hockey, water polo,
                             beach volleyball, netball, Gaelic games and others), combat sports, racing, winter
                             events, athletics events, para sports, balls, bats and sticks, protective gear, footwear
                             and skates, sports places, racing vehicles and officials. Only labels no other pack asks
                             (packs/test_sports.py checks); photos with a child label are left out. Describing only.

Not repeated here, and linked instead: the balls, bats, gloves, golf clubs, ice hockey sticks and pucks, shuttlecocks,
skis and snowboards of everyday_extras_packs (commons_toys_sports_music); the Open Images sports, equipment and grounds
of culture_packs (open_images_culture) and its Wikidata sports (wikidata_sports); guide running, blind cricket,
torball, sitting volleyball, boccia and para-cycling (fitness_nutrition_packs: commons_adaptive_sports); goalball,
blind football and wheelchair sports (disability_packs); exercise equipment (gaps_oi_packs, fitness_nutrition_packs);
hiking, climbing, snow sports, paddling and fishing (outdoors_packs); board and card games (games_packs: games, not
sports). Commons has no category of goalballs, beep baseballs or showdown tables with files (checked 2026-11-22). What
was looked at and left out is in the kit's sports_sources.py (SPORTS_NOT_INCLUDED).

    python packs/sports_packs.py commons_sports_gear --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from outdoor_cooking_packs import with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

GEAR_NOTE = ("Protective gear works only when it fits and is in good condition. After a blow to the head, stop "
             "playing and see a doctor; do not play again until a doctor says it is safe (CDC HEADS UP).")
ICE_NOTE = "Ice safety: never go on natural ice unless it is known to be thick enough, and never alone."
ASK_WHAT = "What is this?"
ASK_PLACE = "What kind of place is this?"
ASK_SPORT = "What sport is this?"

# Files whose own words name a young athlete or a school or age-group game: left out of the people packs (with
# home_packs.build_commons_topic's adults_only, which leaves out files naming a child).
YOUTH = re.compile(r"\b(youth|juniors?|junior high|high school|middle school|secondary school|elementary|primary "
                   r"school|schools?|scholastic|little league|under[- ]?\d{1,2}|u[- ]?\d{1,2}|kids?|cadets?|"
                   r"jugend|junioren|juvenil|infantil|minis?|biddy|pee[- ]?wee|bantam|midget|atom|novice|"
                   r"girls?|boys?)\b", re.I)
ADULT_ONLY = re.compile(r"^(?!.*" + YOUTH.pattern[2:-2] + r"\b).*", re.I | re.S)


def thing(category, words, notes="", deeper=False, pattern=None, question=ASK_WHAT):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, "This is <words>." and the
    notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(question, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


def place(category, words, deeper=False, notes=""):
    """A Commons spec for a sports place: "What kind of place is this?" -> "This is <words>."."""
    return thing(category, words, notes, deeper, question=ASK_PLACE)


def action(category, words, deeper=True):
    """A Commons spec for adults playing: "What sport is this?" -> "This is <words>.", adults only."""
    return thing(category, words, "", deeper, ADULT_ONLY, ASK_SPORT)


# ----------------------------------------------------------------- Commons: equipment

EQUIPMENT = [
    thing("Cricket balls", "a cricket ball, a hard leather ball with a raised stitched seam", deeper=True),
    thing("Field hockey balls", "a field hockey ball, a small hard plastic ball"),
    thing("Rugby balls", "a rugby ball, an oval ball", deeper=True),
    thing("Cricket bats", "a cricket bat, a flat-faced willow bat"),
    thing("Softball bats", "a softball bat", deeper=True),
    thing("Table tennis bats", "a table tennis bat (a ping-pong paddle), a wooden blade with rubber faces"),
    thing("Field hockey sticks", "a field hockey stick, a stick with a curved, flat-faced head"),
    thing("Lacrosse sticks", "a lacrosse stick, a stick with a netted pocket at the head"),
    thing("Boxing gloves", "boxing gloves, padded gloves for boxing", GEAR_NOTE, True),
    thing("Batting gloves", "batting gloves, thin gloves a batter wears to grip the bat"),
    thing("Bowling pins", "bowling pins, which stand at the end of a bowling lane to be knocked down"),
    thing("Curling stones", "a curling stone, a heavy round granite stone with a handle, slid along the ice"),
    thing("Épées", "an épée, a fencing sword with a stiff blade and a large bell guard", GEAR_NOTE),
    thing("Javelins", "a javelin, a spear thrown for distance in athletics", deeper=True),
    thing("Starting blocks", "starting blocks, which sprinters push off from at the start of a race"),
    thing("Hurdles", "a hurdle, a barrier runners jump over in hurdle races"),
    thing("Home plates", "home plate, the five-sided rubber base in baseball and softball", deeper=True),
    thing("Batting tees", "a batting tee, a stand that holds the ball for batting practice"),
    thing("Pitching machines", "a pitching machine, which throws balls for batting practice"),
    thing("Stopwatches", "a stopwatch, for timing races and training"),
]

# ----------------------------------------------------------------- Commons: protective gear, skates, goals, vehicles

GEAR = [
    thing("American football helmets", "an American football helmet with a face mask", GEAR_NOTE, True),
    thing("Batting helmets", "a batting helmet, worn by baseball and softball batters", GEAR_NOTE, True),
    thing("Ice hockey helmets", "an ice hockey helmet", GEAR_NOTE, True),
    thing("Ski helmets", "a ski helmet", GEAR_NOTE, True),
    thing("Racing helmets", "a racing helmet, worn by racing drivers", GEAR_NOTE, True),
    thing("Shoulder pads", "shoulder pads, worn under the jersey in American football and ice hockey", GEAR_NOTE,
          True),
    thing("Shin guards", "shin guards (shin pads), which protect the front of the lower legs", GEAR_NOTE),
    thing("Cricket pads", "cricket pads (leg guards), worn by batters and the wicket-keeper", GEAR_NOTE),
    thing("Ice hockey goaltender equipment", "ice hockey goaltender equipment: the mask, leg pads, blocker and "
                                             "catching glove", GEAR_NOTE, True),
    thing("Fencing masks", "a fencing mask, with a mesh front that protects the face", GEAR_NOTE),
    thing("Inline skates", "inline skates, with their wheels in one line", GEAR_NOTE, True),
    thing("Figure skates", "figure skates, with toe picks at the front of the blade", ICE_NOTE),
    thing("Ice hockey skates", "ice hockey skates", ICE_NOTE, True),
    thing("Ski boots", "ski boots, stiff boots that click into ski bindings", deeper=True),
    thing("Ski bindings", "ski bindings, which hold the boot to the ski and release it in a fall", deeper=True),
    thing("Ski poles", "ski poles", deeper=True),
    thing("Association football goals", "a football (soccer) goal: two posts, a crossbar and a net", deeper=True),
    thing("Ice hockey goals", "an ice hockey goal (the net)", deeper=True),
    thing("Tennis nets", "a tennis net across the middle of the court"),
    thing("Volleyball nets", "a volleyball net, hung high across the court"),
    thing("Basketball goals", "a basketball goal: a hoop with a net, on a backboard", deeper=True),
    thing("Goalposts", "goalposts", deeper=True),
    thing("Racing bicycles", "a racing bicycle (a road racing bike) with drop handlebars", GEAR_NOTE),
    thing("Track bicycles", "a track bicycle, a fixed-gear bike with no brakes for racing on a velodrome",
          deeper=True),
    thing("Time trial bicycles", "a time trial bicycle, shaped to cut through the air, with low handlebars",
          deeper=True),
    thing("Karts", "a kart (go-kart), a small open four-wheeled racing car", GEAR_NOTE, True),
    thing("Racing wheelchairs", "a racing wheelchair, a light three-wheeled chair for wheelchair racing",
          deeper=True),
    thing("Formula One cars", "a Formula One car, an open-wheel single-seat racing car", deeper=True),
]

# ----------------------------------------------------------------- Commons: places

VENUES = [
    place("Basketball courts", "a basketball court", True),
    place("Tennis courts", "a tennis court", True),
    place("Volleyball courts", "a volleyball court", True),
    place("Beach volleyball courts", "a beach volleyball court, on sand"),
    place("Squash courts", "a squash court, a walled indoor court", True),
    place("Badminton courts", "a badminton court"),
    place("Netball courts", "a netball court", True),
    place("Ice rinks", "an ice rink", True, ICE_NOTE),
    place("Ice hockey rinks", "an ice hockey rink, with boards around the ice", True),
    place("American football fields", "an American football field, marked with yard lines", True),
    place("Baseball fields", "a baseball field (a diamond)", True),
    place("Pitcher's mounds", "a pitcher's mound, the raised dirt circle in the middle of a baseball infield"),
    place("Dugouts", "a dugout, the team bench beside a baseball field", True),
    place("Running tracks", "a running track", True),
    place("Athletics tracks", "an athletics track, an oval running track with lanes", True),
    place("Velodromes", "a velodrome, a banked track for cycle racing", True),
    place("Bowling alleys", "a bowling alley, with lanes and pins", True),
    place("Ski jumping hills", "a ski jumping hill, with its steep in-run and landing slope", True),
    place("Golf courses", "a golf course"),
    place("Driving ranges", "a golf driving range, where golfers practise long shots", True),
    place("Diving platforms", "a diving platform (a diving tower) above a pool", True),
    place("Cricket pitches", "a cricket pitch, the strip in the middle of the field with a wicket at each end",
          True),
    place("Grandstands", "a grandstand, the large covered seating at a sports ground", True),
]

# ----------------------------------------------------------------- Commons: athletes in action (adults only)

SPORTS_ACTION = [
    action("High jump", "the high jump, an athletics event: athletes jump over a bar set ever higher"),
    action("Long jump", "the long jump, an athletics event: athletes run and jump as far as they can into sand"),
    action("Javelin throw", "the javelin throw, an athletics event"),
    action("Shot put", "the shot put, an athletics event: athletes push a heavy metal ball as far as they can"),
    action("Discus throw", "the discus throw, an athletics event"),
    action("Hammer throw", "the hammer throw, an athletics event: athletes swing and throw a metal ball on a wire"),
    action("Hurdling", "hurdling, racing over hurdles"),
    action("Association football matches", "a football (soccer) match"),
    action("Volleyball matches", "a volleyball match"),
    action("Field hockey matches", "a field hockey match"),
    action("Rugby union matches", "a rugby union match", deeper=True),
    action("Baseball games", "a baseball game"),
    action("Tennis matches", "a tennis match"),
    # para sports not in fitness_nutrition_packs or disability_packs (Commons, checked 2026-11-22)
    action("Para ice hockey", "para ice hockey (sledge hockey): players sit on sledges and use two short sticks"),
    action("Powerchair football", "powerchair football, football played in power wheelchairs with a large ball"),
    action("Amputee football", "amputee football: outfield players use crutches, goalkeepers have one arm"),
    action("Para table tennis", "para table tennis, table tennis for disabled players"),
]

def build_commons_sports_equipment(limit):
    """The commons_sports_equipment pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(EQUIPMENT, limit, "sportequip")


def build_commons_sports_gear(limit):
    """The commons_sports_gear pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(GEAR, limit, "sportgear")


def build_commons_sports_venues(limit):
    """The commons_sports_venues pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(VENUES, limit, "sportvenue")


def build_commons_sports_action(limit):
    """The commons_sports_action pack (see the module docstring): adults only."""
    from home_packs import build_commons_topic
    return build_commons_topic(SPORTS_ACTION, limit, "sportaction", adults_only=True)


# ----------------------------------------------------------------- Open Images

SPORTS_OI = [
    group("What sport is being played here?",
          {"Soccer": "soccer (association football)", "Handball": "handball", "Rugby union": "rugby union",
           "Rugby league": "rugby league", "Lacrosse": "lacrosse", "Softball": "softball",
           "Field hockey": "field hockey", "Water polo": "water polo", "Beach volleyball": "beach volleyball",
           "Australian rules football": "Australian rules football", "Gaelic football": "Gaelic football",
           "Hurling": "hurling", "Netball": "netball", "Ultimate": "ultimate (ultimate frisbee)",
           "Squash (Sport)": "squash", "Racquetball": "racquetball", "Disc golf": "disc golf"}),
    group("What combat sport is this?",
          {"Wrestling": "wrestling", "Martial arts": "martial arts", "Professional boxing": "professional boxing",
           "Mixed martial arts": "mixed martial arts", "Muay thai": "Muay Thai", "Kickboxing": "kickboxing"},
          GEAR_NOTE),
    group("What kind of race is this?",
          {"Auto racing": "auto racing", "Formula one": "Formula One racing", "Motorcycle racing": "motorcycle racing",
           "Motocross": "motocross", "Kart racing": "kart racing", "Road bicycle racing": "road bicycle racing",
           "Track cycling": "track cycling", "Bmx racing": "BMX racing", "Triathlon": "a triathlon",
           "Marathon": "a marathon"}),
    group("What winter sport is this?",
          {"Cross-country skiing": "cross-country skiing", "Ski jumping": "ski jumping", "Biathlon": "biathlon",
           "Speed skating": "speed skating", "Bobsleigh": "bobsleigh", "Luge": "luge"}),
    group("What athletics event is this?",
          {"Pole vault": "the pole vault", "Shot put": "the shot put", "Javelin throw": "the javelin throw",
           "Discus throw": "the discus throw", "Weightlifting": "weightlifting"}),
    group("What para sport is this?",
          {"Para table tennis": "para table tennis",
           "Para-alpine skiing": "para-alpine skiing", "Sledge hockey": "sledge hockey (para ice hockey)"}),
    group("What balls, bats or sticks are in this picture?",
          {"Basketball (Ball)": "a basketball", "Soccer ball": "a soccer ball", "Lacrosse stick": "a lacrosse stick",
           "Lacrosse ball": "a lacrosse ball", "Golf club": "a golf club", "Golf bag": "a golf bag",
           "Softball bat": "a softball bat", "Cricket bat": "a cricket bat", "Hockey puck": "a hockey puck",
           "Water polo ball": "a water polo ball", "Fencing weapon": "a fencing sword", "Javelin": "a javelin"}),
    group("What protective gear is in this picture?",
          {"Football helmet": "a football helmet", "Baseball protective gear": "baseball protective gear",
           "Lacrosse helmet": "a lacrosse helmet", "Batting helmet": "a batting helmet",
           "Goaltender mask": "a goaltender's mask", "Cricket helmet": "a cricket helmet", "Ski helmet": "a ski helmet",
           "Knee pad": "knee pads", "Elbow pad": "elbow pads", "Shin guard": "shin guards",
           "Soccer shin guard": "soccer shin guards", "Shoulder pads": "shoulder pads", "Batting glove": "batting "
           "gloves", "Soccer goalie glove": "goalkeeper gloves", "Headgear (Sports equipment)": "protective headgear"},
          GEAR_NOTE),
    group("What sports shoes or skates are in this picture?",
          {"Track spikes": "track spikes (running shoes with spikes)", "Figure skate": "figure skates",
           "Inline skates": "inline skates", "Ski boot": "ski boots", "Ski binding": "ski bindings",
           "American football cleat": "American football cleats", "Soccer cleat": "soccer cleats"}),
    group("What sports place or equipment is this?",
          {"Sports venue": "a sports venue", "Arena": "an arena", "Baseball park": "a baseball park",
           "Soccer-specific stadium": "a soccer stadium", "Ice rink": "an ice rink", "Tennis court": "a tennis court",
           "Dugout": "a dugout", "Volleyball net": "a volleyball net", "Basketball hoop": "a basketball hoop",
           "Hurdle": "a hurdle", "Mat (Sports equipment)": "a sports mat"}),
    group("What racing vehicles are in this picture?",
          {"Race car": "a race car", "Racing bicycle": "a racing bicycle", "Formula one car": "a Formula One car",
           "Go-kart": "a go-kart", "Golf cart": "a golf cart"}),
    group("Who is this official or player?",
          {"Referee": "a referee", "Baseball umpire": "a baseball umpire", "Cricket umpire": "a cricket umpire",
           "Goalkeeper": "a goalkeeper"}),
]


def adults_only(entries):
    """entries without the pictures that have a child label (oi_gap_rows marks their rows "child"): the sports packs
    show adults only."""
    bad = {picture_of(name, row) for name, _data, row in entries if row.get("child")}
    return [(name, data, row) for name, data, row in entries if picture_of(name, row) not in bad]


def picture_of(name, row):
    """The picture an entry belongs to: its own name, or for a (None, None, row) twin the name in row["file"]
    ("pictures/<name>")."""
    return name if name else str(row.get("file") or "").rsplit("/", 1)[-1]


def build_open_images_sports(limit):
    """open_images_sports (see the module docstring)."""
    entries = with_yes_notes(build_oi_gap("open_images_sports", SPORTS_OI, int(limit * 1.2) + 2, 9401), SPORTS_OI)
    entries = adults_only(entries)
    pictures = [name for name, data, _row in entries if data][:limit]
    keep = set(pictures)
    return [(name, data, row) for name, data, row in entries if picture_of(name, row) in keep]


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
SPORTS_PACKS = {
    "commons_sports_equipment": (build_commons_sports_equipment, COMMONS_LICENCE.format(
        what="sports ball, bat, stick, glove, pin, curling stone, javelin, hurdle and training equipment")),
    "commons_sports_gear": (build_commons_sports_gear, COMMONS_LICENCE.format(
        what="sports helmet, pad, skate, ski gear, goal, net, racing bicycle, kart and racing wheelchair")),
    "commons_sports_venues": (build_commons_sports_venues, COMMONS_LICENCE.format(
        what="sports court, rink, field, track, velodrome, golf course and grandstand")),
    "commons_sports_action": (build_commons_sports_action, COMMONS_LICENCE.format(
        what="athletics events, team sports matches and para sports in action (adults only)")),
    "open_images_sports": (build_open_images_sports, OI_LICENCE),
}
SPORTS_LIMITS = {
    "commons_sports_equipment": 900,       # 20 categories
    "commons_sports_gear": 1500,           # 28 categories
    "commons_sports_venues": 1300,         # 23 categories
    "commons_sports_action": 1100,         # 17 categories, deeper
    "open_images_sports": 3000,            # 97 labels; Soccer has most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
SPORTS_COMMONS_KEYS = ("commons_sports_equipment", "commons_sports_gear", "commons_sports_venues",
                       "commons_sports_action")
# The Commons category specs of the packs (for the self-test).
SPORTS_SPECS = EQUIPMENT + GEAR + VENUES + SPORTS_ACTION


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a sports pack builder.")
    parser.add_argument("key", choices=sorted(SPORTS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = SPORTS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
