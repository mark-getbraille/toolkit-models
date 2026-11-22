"""The six PRACTICAL LIFE manual collections in one place (the owner's request of 2026-11-22), so categories.py needs
only one small hook: driver, CDL and motorcycle handbooks (driving_manuals.py), computer and phone getting-started
guides (computer_basics_manuals.py), cleaning machines and household management (household_manuals.py), outdoor tools
(knots_outdoor_manuals.py), pools, spas and hot tubs (pools_spas_manuals.py), and RVs, trailers, towing and motorcycle
gear (motorcycles_rvs_manuals.py). Each file describes its own category, its safety notice, its makers (all
link-only) and its guidance.

CATEGORIES: {category key: category} of the six.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from computer_basics_manuals import CATEGORY as _COMPUTER  # noqa: E402
from driving_manuals import CATEGORY as _DRIVING  # noqa: E402
from household_manuals import CATEGORY as _HOUSEHOLD  # noqa: E402
from knots_outdoor_manuals import CATEGORY as _OUTDOOR  # noqa: E402
from motorcycles_rvs_manuals import CATEGORY as _MOTO_RV  # noqa: E402
from pools_spas_manuals import CATEGORY as _POOLS  # noqa: E402

CATEGORIES = {
    "driving_handbooks": _DRIVING,
    "computer_basics": _COMPUTER,
    "household_cleaning": _HOUSEHOLD,
    "outdoor_tools": _OUTDOOR,
    "pools_spas": _POOLS,
    "motorcycles_rvs": _MOTO_RV,
}
