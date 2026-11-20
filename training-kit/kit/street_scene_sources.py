"""US AND CANADIAN STREET SCENES for the Picture Model Training Kit: the collections that cannot be ready-made packs
because of their licence, and the ones that need a sign-up, need permission, or were looked at and left out. The
open ones (Commons crosswalks, pedestrian signals, traffic lights by state, curb cuts, tactile paving, street signs,
roundabouts, interchanges, school zones, road works, bike lanes, bus stops, sidewalks, suburbs, driveways and porches,
and the Federal Highway Administration's photos) are packs in packs/street_scene_packs.py.

As in drug_firearm_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit
on the user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.
Every licence was checked at its source in November 2026 (the link and the terms line are in each entry).

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia).
  "noncommercial"  non-commercial terms: the personal-use box (Alt+Q); a result is for personal use only.

NEVER GUESS A SIGNAL STATE: the Bosch answers say only the colours its makers labelled by hand, light by light, and
the Commons share-alike entry asks a traffic light's colour only from a "Traffic lights at red (yellow, green) state"
category.

The collections (STREET_SCENE_SOURCES):
  share-alike
    street_scene_commons_sa  Wikimedia Commons files under CC BY-SA or GFDL of the open packs' categories (crosswalks,
                           pedestrian signals and push buttons, traffic lights by state, curb cuts, tactile paving,
                           street signs, roundabouts, interchanges, school zone signs, road works, bike lanes, bus
                           stops, sidewalks, suburbs, driveways, porches). Captions CC0.
  noncommercial
    bosch_traffic_lights   Bosch Small Traffic Lights Dataset (Behrendt and Novak, Robert Bosch LLC, Palo Alto,
                           2017; Zenodo 12706046, "LICENSE FOR NONCOMMERCIAL PURPOSES", the CC BY-NC-SA 4.0 text with
                           Robert Bosch LLC as licensor): 5,093 frames filmed from a car in Palo Alto, Los Altos and
                           Mountain View, California, every traffic light boxed by hand with its state (red, yellow,
                           green, off, and the arrows). "What colour are the traffic lights ahead showing?" The
                           frames are read one by one from the 6.2 GB training zip (HTTP ranges), with its train.yaml.

Needing sign-up (STREET_SCENE_SIGN_UP), permission candidates (STREET_SCENE_PERMISSION_CANDIDATES), and looked at but
not included (STREET_SCENE_NOT_INCLUDED, with the reason).

    python kit/street_scene_sources.py bosch_traffic_lights --cap 8      (from the kit folder: a quick check)
"""

import json
import os
import random
import re

from home_sources import commons_sa_items
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS, remote_zip, zip_members
from extra_sources import say
from sources import Source

LIGHT_Q = "What colour is the traffic light showing?"
LIGHTS_AHEAD_Q = "What colour are the traffic lights ahead showing?"

# Words that leave a share-alike file out: crashes, injuries and death (these are everyday collections).
HARM = re.compile(r"\b(crash\w*|collisions?|accidents?|wreck\w*|killed|dead|deaths?|died|fatal\w*|injur\w*|wounded|"
                  r"blood\w*|memorial|ghost bike|riot\w*|protest\w*|arrest\w*)\b", re.I)


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

def spec(category, question, answer, deeper=True):
    """(category, question, answer, also one level of its subcategories) for home_sources.commons_sa_items."""
    return (category, question, answer, deeper)


CROSSWALK = "Yes, there is a crosswalk: a marked place for people to cross the street."
STREET_SCENE_SA = [
    spec("Pedestrian crossings in the United States", "Is there a crosswalk here?", CROSSWALK),
    spec("Pedestrian crossings in Canada", "Is there a crosswalk here?", CROSSWALK),
    spec("Continental crosswalks in the United States", "What kind of crosswalk is this?",
         "It is a continental crosswalk: wide white bars side by side across the street, each bar running the same "
         "way as the traffic."),
    spec("Ladder crosswalks in the United States", "What kind of crosswalk is this?",
         "It is a ladder crosswalk: two white lines across the street with wide bars between them, like the rungs "
         "of a ladder."),
    spec("Raised pedestrian crossings in Canada", "What kind of crosswalk is this?",
         "It is a raised crosswalk: the crossing is built up to the height of the sidewalk, so cars slow down and you "
         "cross on the level.", False),
    spec("Curb cuts in the United States", "Is there a curb ramp here?",
         "Yes, there is a curb ramp (a curb cut), where the sidewalk slopes down to the street."),
    spec("Tactile paving in the United States", "Is there tactile paving here?",
         "Yes, there is tactile paving: detectable warning strips of raised bumps (truncated domes), often yellow, "
         "that you can feel with your feet or cane."),
    spec("Pedestrian signals in the United States", "Is there a pedestrian signal here?",
         "Yes, there is a pedestrian signal: the light that shows a walking person when you may start to cross and "
         "a raised hand when you should not."),
    spec("Pedestrian signals in Canada", "Is there a pedestrian signal here?",
         "Yes, there is a pedestrian signal: the light that shows a walking person when you may start to cross and "
         "a raised hand when you should not."),
    spec("Pedestrian signal push buttons in the United States", "Is there a push button for the walk signal?",
         "Yes, there is a pedestrian push button. Press it to ask for the walk signal."),
    spec("Traffic lights at red state in the United States", LIGHT_Q,
         "The traffic light is red: traffic facing it must stop."),
    spec("Traffic lights at green state in the United States", LIGHT_Q,
         "The traffic light is green: traffic facing it may go. A green light for cars does not always mean it is "
         "safe to cross; check the pedestrian signal and listen for turning cars before you cross."),
    spec("Traffic lights at red state in Canada", LIGHT_Q, "The traffic light is red: traffic facing it must stop."),
    spec("Traffic lights at green state in Canada", LIGHT_Q,
         "The traffic light is green: traffic facing it may go. A green light for cars does not always mean it is "
         "safe to cross; check the pedestrian signal and listen for turning cars before you cross."),
    spec("Street signs in Ontario", "What does this sign tell me?",
         "It is a street name sign, showing the name of the street, usually on a pole at a corner."),
    spec("Street signs in the United States by state", "What does this sign tell me?",
         "It is a street name sign, showing the name of the street, usually on a pole at a corner."),
    spec("Roundabouts in the United States by state", "What kind of place is this?",
         "This is a roundabout: traffic goes one way around a central island and drivers entering give way to "
         "traffic already in it."),
    spec("Interchange ramps in the United States", "What kind of road is this?",
         "This is a highway ramp, where traffic joins or leaves a highway at an interchange."),
    spec("Roadworks in the United States", "What kind of place is this?",
         "This is road work (a construction zone). Watch for cones, barriers, open trenches, closed sidewalks and "
         "detours."),
    spec("Cycle lanes in the United States by state", "What kind of road is this?",
         "This is a bike lane: a part of the street marked for bicycles."),
    spec("Cycle lanes in Canada", "What kind of road is this?",
         "This is a bike lane: a part of the street marked for bicycles."),
    spec("Bus stops in the United States by state", "What kind of place is this?", "This is a bus stop."),
    spec("Bus stops in Canada", "What kind of place is this?", "This is a bus stop."),
    spec("Suburbs in the United States", "What kind of place is this?",
         "This is a suburban street: a quiet residential area of houses, usually with lawns and driveways."),
    spec("Porches in the United States", "What is this?", "This is a porch: a covered area at the entrance of a "
                                                          "house."),
]


def sa_items(specs, cap, test, prefix):
    """home_sources.commons_sa_items (files under CC BY-SA or GFDL, the categories sharing the cap, children left
    out), without the files whose words name a crash, injury, death or protest; and a traffic light's colour only
    where the file is not also filed under another colour (a file found under two colour categories is dropped)."""
    items = commons_sa_items(specs, cap, test, prefix, adults_only=True)
    colours = {}
    for name, _, row in items:
        if row["question"] == LIGHT_Q:
            colours.setdefault(name, set()).add(row["answer"])
    bad = {name for name, _, row in items if HARM.search(f"{name.replace('_', ' ')} {row['answer']}")}
    bad |= {name for name, said in colours.items() if len(said) > 1}
    if bad:
        say(f"  {len(bad)} files left out by their words or two colours")
    return [i for i in items if i[0] not in bad]


def prepare_street_scene_commons_sa(source, data_dir, work, cap):
    """Commons street scene categories, files under CC BY-SA or GFDL."""
    items = sa_items(STREET_SCENE_SA, cap, source.test, "street-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- noncommercial: Bosch Small Traffic Lights

BOSCH = "https://zenodo.org/api/records/12706046/files/dataset_train_rgb.zip/content"
BOSCH_YAML = "dataset_train_rgb/train.yaml"
BOSCH_CREDIT = ("Bosch Small Traffic Lights Dataset (Karsten Behrendt and Libor Novak, Robert Bosch LLC, 2017), "
                "https://zenodo.org/records/12706046, licence for non-commercial purposes")
BOSCH_WIDTH = 1280
# The makers' labels, as said in a sentence: (one light, several lights).
BOSCH_WORDS = {
    "Red": ("red", "red"), "Yellow": ("yellow", "yellow"), "Green": ("green", "green"),
    "off": ("switched off (dark)", "switched off (dark)"),
    "RedLeft": ("a red left arrow", "red left arrows"), "GreenLeft": ("a green left arrow", "green left arrows"),
    "RedRight": ("a red right arrow", "red right arrows"), "GreenRight": ("a green right arrow", "green right arrows"),
    "RedStraight": ("a red straight-ahead arrow", "red straight-ahead arrows"),
    "GreenStraight": ("a green straight-ahead arrow", "green straight-ahead arrows"),
    "GreenStraightRight": ("a green arrow for straight ahead and right", "green arrows for straight ahead and right"),
    "GreenStraightLeft": ("a green arrow for straight ahead and left", "green arrows for straight ahead and left"),
    "RedStraightLeft": ("a red arrow for straight ahead and left", "red arrows for straight ahead and left"),
}
FAR = 20                      # pixels: lights smaller than this (in a 1280 x 720 frame) are far off
NUMBER_WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
ENTRY = re.compile(r"^- boxes:(.*?)\n  path: (\S+)", re.S | re.M)
BOX = re.compile(r"\{label: (\w+), occluded: (true|false), x_max: ([\d.]+), x_min: ([\d.]+), y_max: ([\d.]+),\s*"
                 r"y_min: ([\d.]+)\}")


def bosch_frames(text):
    """[(picture path in the zip, [(label, x middle as a share of the width, height in pixels)])] from train.yaml
    (read with regular expressions, so no YAML library is needed). Hidden (occluded) lights are left out of each
    frame's list; a frame with a hidden light is skipped (its state may be unclear)."""
    out = []
    for boxes, path in ENTRY.findall(text):
        found = BOX.findall(boxes)
        if not found or any(occluded == "true" for _, occluded, *_ in found):
            continue
        lights = [(label, (float(x_max) + float(x_min)) / 2 / BOSCH_WIDTH, float(y_max) - float(y_min))
                  for label, _, x_max, x_min, y_max, y_min in found]
        if any(label not in BOSCH_WORDS for label, _, _ in lights):
            continue
        out.append(("dataset_train_rgb/" + path.lstrip("./"), lights))
    return out


def bosch_answer(lights):
    """ "There are three traffic lights ahead: two show red and one shows a red left arrow." from a frame's lights
    (labels only; nothing guessed). The lights are small in these frames, so "ahead" and the count are said, not
    where each is, and "in the distance" when even the biggest is under FAR pixels tall."""
    far = " in the distance" if max(h for _, _, h in lights) < FAR else ""
    groups = {}
    for label, _, _ in lights:
        groups[label] = groups.get(label, 0) + 1
    if len(lights) == 1:
        one = BOSCH_WORDS[lights[0][0]][0]
        return f"There is one traffic light ahead{far}, and it {'is' if lights[0][0] == 'off' else 'shows'} {one}."
    parts = []
    for label, n in sorted(groups.items(), key=lambda kv: -kv[1]):
        one, many = BOSCH_WORDS[label]
        if n == len(lights):
            verb = "are" if label == "off" else "show"
            parts.append(f"{'both' if n == 2 else 'all'} {verb} {many}")
        else:
            verb = ("is" if n == 1 else "are") if label == "off" else ("shows" if n == 1 else "show")
            parts.append(f"{NUMBER_WORDS[n] if n <= 10 else n} {verb} {one if n == 1 else many}")
    count = NUMBER_WORDS[len(lights)] if len(lights) <= 10 else str(len(lights))
    joined = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"There are {count} traffic lights ahead{far}: {joined}."


def prepare_bosch_traffic_lights(source, data_dir, work, cap):
    """Bosch Small Traffic Lights: frames whose lights are all visible and at least 8 pixels tall, spread over the
    labels (frames with a yellow, an arrow or a dark light are taken first: green and red are common), each with
    "What colour are the traffic lights ahead showing?" from the makers' labels."""
    archive = remote_zip(BOSCH)
    frames = [f for f in bosch_frames(archive.read(BOSCH_YAML).decode("utf-8", "replace"))
              if min(h for _, _, h in f[1]) >= 8]
    rng = random.Random(2017)
    rng.shuffle(frames)
    rare = [f for f in frames if any(label not in ("Red", "Green") for label, _, _ in f[1])]
    common = [f for f in frames if f not in rare]
    want = cap + source.test
    picked = (rare[:want // 3] + common)[:want]
    chosen = [(path, {"question": LIGHTS_AHEAD_Q, "answer": bosch_answer(lights), "split": "",
                      "credit": BOSCH_CREDIT, "place": "California, USA",
                      "facts": {"labels": [label for label, _, _ in lights]}})
              for path, lights in picked]
    say(f"  Bosch Small Traffic Lights: {len(frames)} usable frames, {len(chosen)} chosen ({len(rare)} with a "
        f"yellow, dark or arrow light).")
    return zip_members(source, data_dir, work, lambda: remote_zip(BOSCH), chosen, workers=3)


# ----------------------------------------------------------------- the table

SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
STREET_SCENE_SOURCES = [
    Source("street_scene_commons_sa", "Wikimedia Commons: US and Canadian crosswalks, pedestrian signals, traffic "
                                      "lights by colour, curb cuts, tactile paving, street signs, roundabouts, bike "
                                      "lanes, bus stops and suburbs, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2000, 20, prepare_street_scene_commons_sa, "about 400 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("bosch_traffic_lights", "Traffic lights and their colours seen from a car in California (Bosch Small "
                                   "Traffic Lights Dataset, personal use)",
           "Licence for non-commercial purposes (Robert Bosch LLC; the CC BY-NC-SA 4.0 text), "
           "https://zenodo.org/records/12706046",
           BOSCH_CREDIT, "noncommercial", 3000, 30, prepare_bosch_traffic_lights,
           "about 3 GB read from a 6.2 GB zip (only the chosen frames)",
           terms="https://zenodo.org/records/12706046/files/non-commercial_license.pdf",
           terms_summary="Non-commercial use only, with credit; anything made from it keeps the same terms."),
]

# The collections a picture-making model may learn from: none (people walk through these street photos).
STREET_SCENE_PICTURE_MAKING_OK = set()

STREET_SCENE_SIGN_UP = {
    "LISA Traffic Light Dataset (UC San Diego, about 43,000 frames from San Diego with every light's state)":
        "https://www.kaggle.com/datasets/mbornoe/lisa-traffic-light-dataset : CC BY-NC-SA 4.0 (as its Kaggle page "
        "and mirrors state; the Kaggle page itself was not readable from this machine), behind a free Kaggle login "
        "(KAGGLE_USERNAME and KAGGLE_KEY). Non-commercial: it would be a personal-use entry with the light states "
        "as answers, like bosch_traffic_lights. Not built.",
    "LISA Traffic Sign Dataset (UC San Diego, 6,610 frames, 47 US sign types)":
        "https://cvrr.ucsd.edu/lisa-traffic-signs-dataset : 'released under academic license agreement' (research "
        "only; the agreement's text is not on the page), downloaded after accepting it. Not built.",
    "BDD100K (Berkeley DeepDrive, 100,000 driving videos and frames in New York and the San Francisco Bay Area, "
    "with traffic light colours and signs)":
        "https://bdd-data.berkeley.edu : an account and acceptance of its licence (educational, research and "
        "not-for-profit use; commercial use reserved for its members), as university_sources.py notes. Not built.",
    "Mapillary Traffic Sign Dataset and Mapillary Vistas":
        "https://www.mapillary.com/dataset : an account; CC BY-NC-SA 4.0 for research (already listed in "
        "personal_sources.py). Mapillary's API (street-level photos, CC BY-SA 4.0) needs an access token; its "
        "photos of Germany are already the share-alike StreetSurfaceVis entry (extra_sources.py).",
    "KartaView (formerly OpenStreetCam) street-level photos":
        "https://kartaview.org : photos CC BY-SA 4.0 (OpenStreetMap wiki), but its API needs an account and key "
        "and has undocumented rate limits; the photos have no labels of crossings or signals, so answers would "
        "have to be written by a person. Not built.",
    "Roboflow Universe and Kaggle crosswalk, zebra crossing and pedestrian-light sets":
        "each needs a free account and API key, and most are web-scraped photos or other people's datasets "
        "re-uploaded under a new licence (a Roboflow copy of Bosch is marked CC BY 4.0 although Bosch's own "
        "licence is non-commercial). Only a set whose page names its own photos and an open licence would do. "
        "Not built.",
}

STREET_SCENE_PERMISSION_CANDIDATES = {
    "Pedestrian and Bicycle Information Center (PBIC) Image Library, UNC Highway Safety Research Center for FHWA":
        "Has: thousands of captioned photos of crosswalks, curb ramps, pedestrian signals, bike lanes and traffic "
        "calming across the US (pedbikeimages.org). Terms: free 'in any non-commercial projects including web "
        "pages, presentations and reports' (PBIC's 2009 announcement) and pedbikeinfo.org's usage guidelines bar "
        "redistribution; the photos are credited to their photographers (Dan Burden and others). Ask: "
        "pbic@pedbikeinfo.org, whether a personal-use kit entry may download them for describing to blind people.",
    "NYC DOT, Seattle DOT, SFMTA and other city transport departments (Flickr photostreams)":
        "Has: many thousands of photos of their own crosswalks, plazas, signals and bike lanes. Their Commons "
        "categories hold no copy of their streams (Commons 'New York City Department of Transportation' 47 loose "
        "files, 'Seattle Department of Transportation' 2, November 2026), and Flickr's API terms forbid storing "
        "photos (see state_sources.py). Ask each department to upload its stream to Commons under an open licence, "
        "or for permission.",
}

STREET_SCENE_NOT_INCLUDED = {
    "Open Images V7: traffic light, traffic sign, stop sign, street light, pedestrian crossing":
        "already asked in the open open_images_street pack (world_life_packs.py: traffic lights, stop signs, street "
        "lights, crossings, curbs, sidewalks, bus stops, from the labels people checked). Open Images has no "
        "location, so it cannot be kept to the USA and Canada, and it labels no light colour. Not repeated.",
    "ImVisible / PTL pedestrian traffic lights":
        "already the open ptl_crossings pack (Shanghai, MIT licence). No North American pedestrian-light set with "
        "labelled states and an open licence was found.",
    "Library of Congress, Carol M. Highsmith Archive":
        "already the open loc_highsmith pack (6,000 of about 70,000 photos, captions as answers). A topic search of "
        "the archive (November 2026) found few street-scene records: 'intersection' 266, 'street sign' 125, "
        "'porch' 121, 'suburban' 104, 'sidewalk' 72, 'freeway' 49, 'traffic light' 7, 'crosswalk' 0. Not built "
        "as a separate pack.",
    "FHWA MUTCD sign images and the MUTCD drawings":
        "already the open us_road_signs pack (the MUTCD drawings on Commons with their numbers).",
    "FHWA Flickr stream (bridges, staff events, history paintings)":
        "only its photos whose own caption names a road scene are used (us_dot_street_photos); the rest are bridge "
        "parts, events and paintings.",
    "NHTSA (National Highway Traffic Safety Administration) photos":
        "Commons's NHTSA category holds 50 loose files (logos, crash tests, officials, November 2026), not street "
        "scenes; crash photos are left out of these everyday packs anyway. Not built.",
    "State DOT photo libraries (Oregon, North Carolina, Massachusetts, Alaska and others)":
        "already the open commons_state_roads pack (their Commons copies, licence by licence). Not repeated.",
    "Canadian city open data (Toronto, Vancouver, Montreal, Ottawa, Calgary)":
        "no street photo library under the Open Government Licence was found: Toronto's portal has no photo "
        "collection and Montréal's photos are vertical aerial surveys (canada_sources.py); the City of Vancouver "
        "Archives refused this machine (403); Ottawa's and Calgary's portals were not searched for photos in "
        "this pass (unverified). Archive photos copied to Commons under open licences are in commons_ca_archives.",
    "US city open data (NYC, Seattle, San Francisco)":
        "not searched photo by photo in this pass (unverified); their transport departments publish their photos "
        "on Flickr (see STREET_SCENE_PERMISSION_CANDIDATES).",
    "Commons categories with no files (November 2026)":
        "'Accessible pedestrian signals', 'Countdown pedestrian signals', 'Street name signs in the United States', "
        "'School zones', 'Bike lanes in the United States', 'Road works in the United States', 'Work zones in the "
        "United States', 'On-ramps in the United States' and 'Detectable warning surfaces' do not exist; the "
        "spellings 'Audible traffic signals', 'Countdown traffic signals', 'Street signs', 'School zone warning road "
        "signs', 'Cycle lanes', 'Roadworks' and 'Interchange ramps' do and are used. No Commons category names a "
        "pedestrian signal's state (walk or don't walk), so that is asked only where a file's own words say it.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one street scene collection.")
    parser.add_argument("key", choices=[s.key for s in STREET_SCENE_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in STREET_SCENE_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="street-scene-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
