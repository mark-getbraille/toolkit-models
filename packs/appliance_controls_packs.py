"""Pack builders for APPLIANCE CONTROLS CLOSE UP: knobs and rotary switches, control panels, push buttons, touch
screens, timers, air-conditioner remote controls, smart thermostats and cooktop controls, on stoves, ovens,
microwaves, washers, dryers, dishwashers, thermostats, coffee makers and air conditioners. Used by build_packs.py in
the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus "place" where the file's camera coordinates give a country and
"child": true where the words of a picture name a child. A picture with more than one question comes once with its
JPEG and then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit
counts pictures.

Why: a blind person at home has to work flat touch panels, unmarked knobs and buttons; a describer must say what the
control is, where it is, and (only when it is known for sure) what it is set to.

NEVER GUESS A SETTING. A knob's position, a dial's temperature, a programme or a display's reading is given only where
the Commons file's own title or description states it with a unit or a name ("set to 180 °C", "dial is on 'Cotton
40'"): home_safety_packs.display_reading, which also gives nothing when the words name two different settings. Open
Images has no setting labels, so its rows never state one.

The packs (all open, checked at the source in November 2026):
  commons_appliance_controls     Wikimedia Commons categories (CONTROL_SPECS); the broad ones (Rotary switches, Control
                                 panels, Push buttons, Touchscreens, Timers) only for files whose own words name a
                                 home appliance (APPLIANCE_WORDS), so lift, car, factory, aircraft and electronics
                                 panels and switches are left out. Files CC0,
                                 public domain or CC BY (each file's licence checked on its own page); captions CC0.
                                 "What is this?" and, where the file's words state it, "What does the display or dial
                                 show?".
  open_images_appliance_controls Google Open Images V7: photos where people checked by hand whether a control knob,
                                 control panel, push button, LED display, display screen, doorbell, garage door
                                 opener, drip, percolator or vacuum coffee maker, air conditioner, clothes dryer,
                                 kitchen stove or convection oven is there (labels CC BY 4.0; each photo's own licence
                                 checked, photographer named).

Not repeated (other packs ask the same of the same photos): thermostats, control knobs, microwave ovens, washing
machines, lift buttons and seven-segment displays (home_packs commons_appliances, seven_segment), dishwashers, clothes
dryers, electric ovens, cooking stoves, remote controls, keypads and light switches (us_modern_packs
commons_us_controls), STATED settings on those (home_safety_packs commons_home_safety), gas stoves and induction
cookers (home_packs commons_kitchen), coffee machines, air conditioners, fridges and space heaters as devices
(device_packs), espresso machines and kitchen timers as things (things_packs), and Amazon Berkeley Objects' appliance
listings (things_packs abo_products: catalogue photos, no control or setting labels). Datasets of appliance panels that
are not open (Zenodo 7586107, the Appliance Knobs set under OpenRAIL, a water-heater panel set under CC BY-NC-SA) are
listed with the reason in training-kit/kit/daily_access_sources.py.

Safety (packs/SOURCE-RULES.md): no sexual content (home_packs.NUDE); rows whose words name a child are marked "child".
The Commons pack shows things and may be used for picture-making; the Open Images photos often show people and are
for describing only.

    python packs/appliance_controls_packs.py commons_appliance_controls --limit 8      (a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

WHAT_Q = "What is this?"
DISPLAY_Q = "What does the display or dial show?"
CONTROLS_NOTE = "A setting is not said unless it is known for sure: feel for raised marks, or ask someone to mark it."

# Words in a file's title or description that show a broad category's file is about a home appliance.
APPLIANCE_WORDS = re.compile(r"\b(ovens?|stoves?|cookers?|cooktops?|hobs?|ranges?|microwaves?|washing machines?|"
                             r"washers?|dryers?|tumble ?dryers?|dishwashers?|fridges?|refrigerators?|freezers?|"
                             r"thermostats?|heaters?|boilers?|furnaces?|air[- ]?condition\w*|a/?c units?|heat pumps?|"
                             r"coffee (makers?|machines?)|espresso|kettles?|toasters?|rice cookers?|bread (makers?|"
                             r"machines?)|blenders?|food processors?|kitchen|laundry|household appliances?|"
                             r"home appliances?|appliances?)\b", re.I)


def control(category, words, deeper=False, must=None):
    """A Commons spec for a control: "What is this?" -> "This is <words>." and the controls note; must: a pattern the
    file's title or words must match."""
    spec = (category, deeper, [(WHAT_Q, f"This is {words}. {CONTROLS_NOTE}")])
    return spec + (must,) if must else spec


CONTROL_SPECS = [
    control("Rotary switches", "a rotary switch: a knob that clicks round to choose a setting", True, APPLIANCE_WORDS),
    control("Control panels", "the control panel of a home appliance", True, APPLIANCE_WORDS),
    control("Push buttons", "a push button on a home appliance", True, APPLIANCE_WORDS),
    control("Touchscreens", "the touch screen of a home appliance: flat buttons you press on the glass", True,
            APPLIANCE_WORDS),
    control("Timers", "a timer on a home appliance or in the kitchen", True, APPLIANCE_WORDS),
    control("Air conditioner remote controls", "an air-conditioner remote control: buttons for power, mode, fan "
                                               "speed and temperature", True),
    control("Nest Learning Thermostat", "a Nest smart thermostat: a round dial with a screen; turn the ring to change "
                                        "the temperature and press it to choose"),
    control("Cooktops", "a cooktop (hob), with knobs or touch controls for each burner or zone", True),
]


def with_settings(entries):
    """entries with a "What does the display or dial show?" row added to each picture whose own description (its
    "Write a short description ..." row, the file's words) states one setting or reading
    (home_safety_packs.display_reading); nothing is added otherwise."""
    from home_safety_packs import display_reading
    from build_packs import ALT_TEXT
    out = []
    for name, data, row in entries:
        out.append((name, data, row))
        if row.get("question") == ALT_TEXT:
            said = display_reading(row["answer"])
            if said:
                extra = {k: v for k, v in row.items() if k not in ("question", "answer")}
                if data is not None:
                    extra["file"] = f"pictures/{name}"
                out.append((None, None, dict(extra, question=DISPLAY_Q, answer=said)))
    return out


def build_commons_appliance_controls(limit):
    """The commons_appliance_controls pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return with_settings(build_commons_topic(CONTROL_SPECS, limit, "applctl"))


# ----------------------------------------------------------------- Open Images

CONTROLS_OI = [
    group("What controls are in this picture?",
          {"Control knob": "a control knob", "Control panel": "a control panel", "Push-button": "a push button",
           "Doorbell": "a doorbell", "Garage door opener": "a garage door opener"}, CONTROLS_NOTE),
    group("What kind of display is in this picture?",
          {"Led display": "an LED display", "Display device": "a display screen"},
          "I can say a display is there, not what it shows."),
    group("What appliance is this?",
          {"Drip coffee maker": "a drip coffee maker", "Coffee percolator": "a coffee percolator",
           "Vacuum coffee maker": "a vacuum coffee maker", "Air conditioning": "an air conditioner",
           "Clothes dryer": "a clothes dryer", "Kitchen stove": "a kitchen stove",
           "Convection oven": "a convection oven"}),
]


def build_open_images_appliance_controls(limit):
    """open_images_appliance_controls (see the module docstring)."""
    return build_oi_gap("open_images_appliance_controls", CONTROLS_OI, limit, 9302)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories; captions CC0.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
APPLIANCE_CONTROLS_PACKS = {
    "commons_appliance_controls": (build_commons_appliance_controls, COMMONS_LICENCE.format(
        what="rotary switch, appliance control panel, push button, touch screen, timer, remote control, smart "
             "thermostat and cooktop")),
    "open_images_appliance_controls": (build_open_images_appliance_controls, OI_LICENCE),
}
APPLIANCE_CONTROLS_LIMITS = {
    "commons_appliance_controls": 600,        # 8 categories; the broad ones only for appliance files
    "open_images_appliance_controls": 2000,   # 14 labels
}
APPLIANCE_CONTROLS_COMMONS_KEYS = ("commons_appliance_controls",)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an appliance controls pack builder.")
    parser.add_argument("key", choices=sorted(APPLIANCE_CONTROLS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = APPLIANCE_CONTROLS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
