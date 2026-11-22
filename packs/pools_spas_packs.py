"""Picture packs for POOLS, SPAS AND HOT TUBS (the owner's request of 2026-11-22). Used by build_packs.py in the same
way as its own PACKS (build_<key>(limit) returns [(file name, JPEG bytes or None, row)]).

Why: the owner wants the picture describer to name pool equipment in a photo (the pump, the sand filter, a pool
cleaner or robot, the ladder, the cover, the rescue hook) and to say the safety rules that go with pools: drowning
prevention and never mixing pool chemicals.

EQUIPMENT AND CHEMISTRY ONLY (the owner's rule): no category about swimming, swimwear or bathers is used, and Commons
"Hot tubs" is left out because its photos often show people in swimwear (hot tub safety is in the books instead).
Answers say only what the source says (a Commons category's name), and every answer ends with the notes that fit
(the same words as the kit's practical_sources.py):
  DROWNING_NOTE   never leave children alone near water, a four-sided fence with a self-closing, self-latching gate,
                  drain covers in place, learn CPR (CDC and the CPSC's Pool Safely).
  POOL_CHEM_NOTE  the household chemical packs' pool note, word for word: dry, closed, away from children; never mix;
                  chemical to water, never water to chemical.

The pack (POOLS_SPAS_PACKS):
  commons_pool_equipment   Wikimedia Commons (CC0, public domain or CC BY files only): swimming pool equipment,
                           pool pumps, sand filters (pool files only), pool cleaners and robotic pool cleaners, pool
                           covers and ladders, and shepherd's crooks (the rescue pole hook; pool files only).

Not repeated here: chemical_packs (pool test kits, pool chemicals, algae in pools, by file words), the Open Images
swimming pool and hot tub labels (the public places pack asks them). No Open Images pack: its pool photos are of
swimming people, which the owner's rule leaves out.

    python packs/pools_spas_packs.py commons_pool_equipment --limit 8
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from outdoor_cooking_packs import thing

DROWNING_NOTE = ("Drowning prevention: never leave children alone in or near water, even for a moment; fence a pool "
                 "on all four sides with a self-closing, self-latching gate; keep drain covers in place so no one is "
                 "trapped by the suction; and learn CPR.")
POOL_CHEM_NOTE = ("Keep pool chemicals dry, closed and away from children. Never mix different pool chemicals, and "
                  "add the chemical to water, never water to the chemical: they can catch fire or give off toxic gas.")

# Commons "Sand filters" also holds water works and "Shepherd's crooks" the shepherd's staff: only pool files.
POOL_WORDS = re.compile(r"\b(pools?|swimming|spas?|lifeguards?|rescue|hot tubs?|jacuzzi)\b", re.I)
POOL_EQUIPMENT = [
    thing("Swimming pool equipment", "swimming pool equipment", f"{POOL_CHEM_NOTE} {DROWNING_NOTE}"),
    thing("Swimming pool pumps", "a swimming pool pump, which pushes the water through the filter",
          f"{POOL_CHEM_NOTE} {DROWNING_NOTE}"),
    thing("Sand filters", "a sand filter, which cleans pool water by passing it through sand; it is cleaned by "
                          "backwashing", f"{POOL_CHEM_NOTE} {DROWNING_NOTE}", pattern=POOL_WORDS),
    thing("Pool cleaners", "a pool cleaner, which vacuums the pool floor and walls", DROWNING_NOTE),
    thing("Robotic pool cleaners", "a robotic pool cleaner, which crawls round the pool by itself", DROWNING_NOTE),
    thing("Swimming pool covers", "a swimming pool cover; a safety cover must be fully fastened, and standing water "
                                  "on any cover is a drowning risk", DROWNING_NOTE),
    thing("Swimming pool ladders", "a swimming pool ladder", DROWNING_NOTE),
    thing("Shepherd's crooks", "a shepherd's crook, a rescue pole with a hook kept by a pool to reach a person in "
                               "the water", DROWNING_NOTE, pattern=POOL_WORDS),
]


def build_commons_pool_equipment(limit):
    """The commons_pool_equipment pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(POOL_EQUIPMENT, limit, "poolgear", adults_only=True)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
POOLS_SPAS_PACKS = {
    "commons_pool_equipment": (build_commons_pool_equipment, COMMONS_LICENCE.format(
        what="swimming pool equipment, pump, sand filter, pool cleaner, cover, ladder and rescue hook")),
}
POOLS_SPAS_LIMITS = {
    "commons_pool_equipment": 250,     # 8 categories, few files in most
}
POOLS_SPAS_COMMONS_KEYS = ("commons_pool_equipment",)
POOLS_SPAS_SPECS = POOL_EQUIPMENT


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(POOLS_SPAS_PACKS, "Try the pool equipment pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
