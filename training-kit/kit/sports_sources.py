"""SPORTS for the Picture Model Training Kit (the owner's request of 2026-11-22: a top-level section with its own topic
add-on, "sports"). This file lists:
  - the ready-made packs built in packs/sports_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_sports_equipment, commons_sports_gear, commons_sports_venues, commons_sports_action and
    open_images_sports;
  - the share-alike Commons files of the equipment, gear and venue categories (group "share-alike": only with the
    share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (SPORTS_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it (the packs from the kit's own release),
only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name in a fixed plain sentence, a label people
checked): no team, player, score or brand. Answers about protective gear and contact or combat sports end with
GEAR_NOTE (the same words as the packs'; packs/test_sports.py checks).

Picture-making (SPORTS_PICTURE_MAKING_OK): only the things and places (equipment, gear, venues and their share-alike
files); sources.py puts every other key in NOT_FOR_PICTURE_MAKING (athletes in action and the Open Images photos show
people: describing only). Topics: all of them in "sports", with the existing sports collections (wikidata_sports, the
adaptive sports of fitness_nutrition_sources.py); the venues also in "places" and athletes in action also in "people".

    python -c "import sources, sports_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/sports_packs.py.
GEAR_NOTE = ("Protective gear works only when it fits and is in good condition. After a blow to the head, stop "
             "playing and see a doctor; do not play again until a doctor says it is safe (CDC HEADS UP).")
ICE_NOTE = "Ice safety: never go on natural ice unless it is known to be thick enough, and never alone."

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def gear(category, words, notes="", deeper=False, question="What is this?"):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, question, f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# Main categories of packs/sports_packs.py (things and places, no people as the subject).
SPORTS_SA = [
    gear("Cricket bats", "a cricket bat, a flat-faced willow bat"),
    gear("Field hockey sticks", "a field hockey stick, a stick with a curved, flat-faced head"),
    gear("Lacrosse sticks", "a lacrosse stick, a stick with a netted pocket at the head"),
    gear("Curling stones", "a curling stone, a heavy round granite stone with a handle, slid along the ice"),
    gear("Starting blocks", "starting blocks, which sprinters push off from at the start of a race"),
    gear("American football helmets", "an American football helmet with a face mask", GEAR_NOTE, True),
    gear("Batting helmets", "a batting helmet, worn by baseball and softball batters", GEAR_NOTE, True),
    gear("Shin guards", "shin guards (shin pads), which protect the front of the lower legs", GEAR_NOTE),
    gear("Fencing masks", "a fencing mask, with a mesh front that protects the face", GEAR_NOTE),
    gear("Figure skates", "figure skates, with toe picks at the front of the blade", ICE_NOTE),
    gear("Association football goals", "a football (soccer) goal: two posts, a crossbar and a net", deeper=True),
    gear("Basketball goals", "a basketball goal: a hoop with a net, on a backboard", deeper=True),
    gear("Tennis courts", "a tennis court", deeper=True, question="What kind of place is this?"),
    gear("Basketball courts", "a basketball court", deeper=True, question="What kind of place is this?"),
    gear("Ice rinks", "an ice rink", ICE_NOTE, True, question="What kind of place is this?"),
    gear("Baseball fields", "a baseball field (a diamond)", deeper=True, question="What kind of place is this?"),
    gear("Athletics tracks", "an athletics track, an oval running track with lanes", deeper=True,
         question="What kind of place is this?"),
    gear("Velodromes", "a velodrome, a banked track for cycle racing", deeper=True,
         question="What kind of place is this?"),
]


def prepare_sports_commons_sa(source, data_dir, work, cap):
    """Commons sports equipment, gear and venue categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(SPORTS_SA, cap, source.test, "sports-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

SPORTS_SOURCES = [
    Source("commons_sports_equipment", "Sports equipment: cricket, field hockey and rugby balls, cricket and softball "
                                       "bats, hockey and lacrosse sticks, boxing gloves, bowling pins, curling "
                                       "stones, javelins, starting blocks, hurdles and home plates (Wikimedia "
                                       "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_sports_gear", "Sports gear: helmets, pads and guards, goaltender equipment, fencing masks, "
                                  "skates, ski boots and bindings, goals and nets, racing bicycles, karts and racing "
                                  "wheelchairs, with protective gear notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 330 MB"),
    Source("commons_sports_venues", "Sports places: courts, ice rinks, fields, pitcher's mounds, dugouts, tracks, "
                                    "velodromes, bowling alleys, ski jumps, golf courses and grandstands (Wikimedia "
                                    "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1300, 15, prepare_pack, "about 290 MB"),
    Source("commons_sports_action", "Athletes in action, adults only: high jump, long jump, javelin, shot put, "
                                    "discus, hammer, hurdling, and football, volleyball, field hockey, rugby, "
                                    "baseball and tennis matches (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 110 MB"),
    Source("open_images_sports", "Sports being played, combat sports, races, winter and athletics events, para sports, "
                                 "balls, bats and sticks, protective gear, sports shoes and skates, sports places, "
                                 "racing vehicles and officials, adults only (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 3000, 30, prepare_pack, "about 650 MB"),
    Source("sports_commons_sa", "Wikimedia Commons: sports bats and sticks, curling stones, helmets, shin guards, "
                                "fencing masks, skates, goals, courts, rinks, fields, tracks and velodromes, files "
                                "under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_sports_commons_sa, "about 180 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: things and places only; never the athletes in action or the
# Open Images photos, which show people.
SPORTS_PICTURE_MAKING_OK = {"commons_sports_equipment", "commons_sports_gear", "commons_sports_venues",
                            "sports_commons_sa"}

SPORTS_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Basketballs, American footballs, Baseballs, Softballs, "
        "Tennis balls, Golf balls, Volleyballs, Bowling balls, Ice hockey pucks, Baseball bats, Baseball gloves, Golf "
        "clubs, Ice hockey sticks, Shuttlecocks, Skis and Snowboards (everyday_extras_packs: "
        "commons_toys_sports_music), Guide runners, Blind cricket, Torball, Sitting volleyball, Boccia and "
        "Para-cycling (fitness_nutrition_packs: commons_adaptive_sports), Goalball, Blind football and the "
        "wheelchair sports (disability_packs): not asked twice; the sports topic uses those packs as they are "
        "where they hold only sports.",
    "Commons categories with no files under the names tried (2026-11-22)": "Goalballs, Beep baseball, Showdown "
        "(sport), Lacrosse balls, Badminton rackets, Squash rackets, Tennis rackets (8 files, not a category), "
        "Goalkeeper gloves, Ice skates, Swimming goggles, Kickboards, Lane ropes, Pole vault poles, Shot puts, "
        "Discuses, Baseball bases, Boxing rings, Motorsport circuits, Rugby pitches, Lacrosse fields, Softball "
        "fields, Field hockey pitches, Curling rinks, Olympic swimming pools, Running prostheses and the \"<sport> "
        "players in action\" categories (none exist on Commons).",
    "Swimming pools and swimmers on Commons": "Many photos of people in swimwear, children among them: left out of the "
                                              "people packs; pool equipment is the pools_spas packs'.",
    "Open Images labels asked elsewhere": "The sports, equipment and grounds of open_images_culture (Tennis, Golf, "
        "Ice hockey, Baseball bat, Stadium, Scoreboard and others) and the exercise equipment, outdoor and snow sports "
        "labels of gaps_oi_packs and outdoors_packs: never asked twice.",
    "Open Images labels with too few checked photos (counted 2026-11-22)": "Powerchair football, Pickleball, "
        "Pitching machine, Race car driver, Football boot, Scrum cap, Whistle, Hockey helmet and Baseball (ball) have "
        "fewer than ten human-checked photos; the generic labels Sports equipment, Sports uniform, Athlete, Player, "
        "Team sport and Ball game say too little.",
    "Team logos, jerseys and players by name": "Logos and kits are trademarks and players are people: no pack names "
                                               "a team or a person; Wikidata's team and player facts are in the "
                                               "reference library (sport: books), not in pictures.",
    "Smithsonian sports collections (CC0)": "The Smithsonian Open Access API needs a personal api.data.gov key, which "
                                            "the repository never stores; left out of the packs.",
    "USABA, IBSA, NBBA and the IPC photos": "Copyright of each organisation (and usaba.org's robots.txt shuts out "
                                            "AI companies' readers); not used.",
    "Para sports categories on Commons (wheelchair fencing, para athletics, para swimming, para ice hockey, "
    "wheelchair curling and others)": "Their category names could not be confirmed on 2026-11-22 (Commons kept "
        "answering 429); not asked. The para sports are in open_images_sports and the existing adaptive packs.",
    "Cheerleading and youth leagues": "Mostly children: left out (the owner's rule: no minors-focused files).",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the sports share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in SPORTS_SOURCES if s.key == "sports_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="sports-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
