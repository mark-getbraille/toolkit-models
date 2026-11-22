"""The six PRACTICAL LIFE collections' picture packs in one place (the owner's request of 2026-11-22), so build_packs.py
needs only one small hook: driving and road rules (driving_packs.py), computer and phone basics
(computer_basics_packs.py), cleaning and household management (household_packs.py), knots, rope and outdoor skills
(knots_outdoor_packs.py), pools, spas and hot tubs (pools_spas_packs.py), and motorcycles, RVs and trailers
(motorcycles_rvs_packs.py). Each of those files describes its own packs, sources and safety notes.

This file gathers:
  PRACTICAL_PACKS         {key: (builder, licence text)} of every pack of the six files
  PRACTICAL_LIMITS        {key: the number of pictures the build workflow asks for}
  PRACTICAL_COMMONS_KEYS  the packs that read Wikimedia Commons (build_packs.COMMONS_KEYS)
  PRACTICAL_SPECS         every Commons category spec, for the self-test
and try_pack(), the small command line each file's main() uses.
"""

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
import computer_basics_packs as _computer
import driving_packs as _driving
import household_packs as _household
import knots_outdoor_packs as _knots
import motorcycles_rvs_packs as _moto
import pools_spas_packs as _pools

# (packs, limits, Commons keys, Commons specs) of each collection, in the order of the owner's request.
COLLECTIONS = [
    (_driving.DRIVING_PACKS, _driving.DRIVING_LIMITS, _driving.DRIVING_COMMONS_KEYS, _driving.DRIVING_SPECS),
    (_computer.COMPUTER_BASICS_PACKS, _computer.COMPUTER_BASICS_LIMITS, _computer.COMPUTER_BASICS_COMMONS_KEYS,
     _computer.COMPUTER_BASICS_SPECS),
    (_household.HOUSEHOLD_PACKS, _household.HOUSEHOLD_LIMITS, _household.HOUSEHOLD_COMMONS_KEYS,
     _household.HOUSEHOLD_SPECS),
    (_knots.KNOTS_OUTDOOR_PACKS, _knots.KNOTS_OUTDOOR_LIMITS, _knots.KNOTS_OUTDOOR_COMMONS_KEYS,
     _knots.KNOTS_OUTDOOR_SPECS),
    (_pools.POOLS_SPAS_PACKS, _pools.POOLS_SPAS_LIMITS, _pools.POOLS_SPAS_COMMONS_KEYS, _pools.POOLS_SPAS_SPECS),
    (_moto.MOTORCYCLES_RVS_PACKS, _moto.MOTORCYCLES_RVS_LIMITS, _moto.MOTORCYCLES_RVS_COMMONS_KEYS,
     _moto.MOTORCYCLES_RVS_SPECS),
]

PRACTICAL_PACKS, PRACTICAL_LIMITS, PRACTICAL_SPECS = {}, {}, []
PRACTICAL_COMMONS_KEYS = ()
for _packs, _limits, _commons, _specs in COLLECTIONS:
    PRACTICAL_PACKS.update(_packs)
    PRACTICAL_LIMITS.update(_limits)
    PRACTICAL_COMMONS_KEYS += tuple(_commons)
    PRACTICAL_SPECS += list(_specs)

# Every Open Images question group of the six files (for the self-test's "asked twice" check).
PRACTICAL_OI_GROUPS = (_driving.DRIVING_OI + _computer.COMPUTER_OI + _household.CLEANING_OI + _knots.KNOTS_OI +
                       _moto.MOTO_RV_OI)


def try_pack(packs, description, argv=None):
    """Build one of packs with a small limit and print its rows: the quick check behind each file's main()."""
    import argparse
    import json
    from gaps_oi_packs import QUICK
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("key", choices=sorted(packs))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = packs[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0
