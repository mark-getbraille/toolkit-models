"""TRAVEL for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists the ready-made packs
built in packs/travel_packs.py (group "permissive"; the kit downloads them with prepare_pack) and the sources looked
at and left out, with the reason (TRAVEL_NOT_INCLUDED):
  synthetic_travel_documents  computer-made SPECIMEN passport data pages and boarding passes (made-up people, the
                              made-up country Utopia, made-up airlines; never usable as real documents);
  commons_travel_signs        Wikimedia Commons: the US DOT/AIGA passenger symbol signs, airport signs, passport
                              control, baggage carousels, jet bridges, taxi signs and currency exchange offices.

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on the
user's own computer from the kit's own release, only when the user ticks the matching choice. Topic: documents
(Documents, maps and signs). Picture-making (TRAVEL_PICTURE_MAKING_OK): none: a model must never learn to draw
convincing travel documents, and the Commons photos show travellers.

    python -c "import sources, travel_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

TRAVEL_SOURCES = [
    Source("synthetic_travel_documents", "Passports and boarding passes, computer-made SPECIMEN examples with made-up "
                                         "names: whose document it is, the expiry date, the flight, gate, boarding "
                                         "time and seat (synthetic, ready-made pack)",
           "CC0 (drawn by packs/travel_packs.py from a fixed seed; made-up people, country and airlines, marked "
           "SPECIMEN)", "Computer-made by the kit's makers (packs/travel_packs.py)", "permissive", 3000, 30,
           prepare_pack, "about 450 MB"),
    Source("commons_travel_signs", "Travel signs: the US DOT/AIGA passenger symbol signs (baggage check-in, customs, "
                                   "immigration, taxi, currency exchange ...), airport signs, passport control, "
                                   "baggage carousels and jet bridges (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 120 MB"),
]

# No collection here may be used for picture-making (see the module docstring).
TRAVEL_PICTURE_MAKING_OK = set()

TRAVEL_NOT_INCLUDED = {
    "Real passports, visas and boarding passes (Commons and other photo sites)": "They carry real people's names, "
        "numbers and photos; only computer-made SPECIMEN examples are used.",
    "Commons airport categories already used by other packs": "Airport gates, departure boards, departure and arrival "
        "halls, airport escalators and airport interiors (indoor_packs), US airport terminals and TSA checkpoints "
        "(us_modern_packs), Canadian airports (canada_packs).",
    "Open Images travel labels": "Airport terminal, luggage and the other travel labels are already asked by "
        "indoor_packs and gaps_oi_packs.",
}
