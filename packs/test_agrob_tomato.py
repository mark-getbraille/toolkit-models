"""A self-test of the AgRobTomato answer (packs/land_industry_packs.py tomato_answer), with made-up label lists
only: nothing is downloaded. It checks that the answer gives only the counts of the dataset's own stage labels, in
ripening order, says "None is fully ripe." only when no tomato is labelled ripe, and is empty with no stage label.

Run it from the repository's folder:   python3 -m pytest packs/test_agrob_tomato.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
from land_industry_packs import tomato_answer, LAND_PACKS, LAND_LIMITS  # noqa: E402


def test_counts_in_ripening_order():
    assert tomato_answer(["reddish", "unriped", "unriped"]) == (
        "The tomatoes marked in this photo: 2 unripe (green) and 1 reddish (nearly ripe). None is fully ripe.")


def test_ripe_named_without_none_note():
    got = tomato_answer(["riped", "breaking", "unriped"])
    assert got == ("The tomatoes marked in this photo: 1 unripe (green), 1 breaking (just starting to change "
                   "colour) and 1 fully ripe (red).")


def test_no_stage_label_gives_nothing():
    assert tomato_answer([]) == ""
    assert tomato_answer(["leaf", "stem"]) == ""


def test_registered():
    assert "agrob_tomato" in LAND_PACKS and LAND_LIMITS["agrob_tomato"] == 450
