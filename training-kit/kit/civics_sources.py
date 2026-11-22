"""CITIZENSHIP AND CIVICS for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists the
ready-made pack built in packs/civics_packs.py (group "permissive"; the kit downloads it with prepare_pack) and the
sources looked at and left out, with the reason (CIVICS_NOT_INCLUDED):
  synthetic_civic_documents  computer-made SPECIMEN sample ballots and jury summonses (made-up places, candidates,
                             measures and courts; never usable as real documents).

Legal answers end with "General information, not tax or legal advice; check the current rules or ask a
professional." Topic: money (Money and paperwork). Picture-making (CIVICS_PICTURE_MAKING_OK): none.

    python -c "import sources, civics_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

CIVICS_SOURCES = [
    Source("synthetic_civic_documents", "Sample ballots and jury summonses, computer-made SPECIMEN examples with "
                                        "made-up places and names: the contests and choices, how to mark a ballot, "
                                        "when and where to report for jury duty (synthetic, ready-made pack)",
           "CC0 (drawn by packs/civics_packs.py from a fixed seed; made-up places, candidates and courts, marked "
           "SPECIMEN)", "Computer-made by the kit's makers (packs/civics_packs.py)", "permissive", 1500, 15,
           prepare_pack, "about 250 MB"),
]

CIVICS_PICTURE_MAKING_OK = set()

CIVICS_NOT_INCLUDED = {
    "Real ballots, voter cards and court papers": "They carry real people's names and choices; only computer-made "
        "SPECIMEN examples are used.",
    "Photos of polling places and voting machines": "Polling places have people in them and the Commons categories "
        "were not checked one by one; left for a later collection.",
}
