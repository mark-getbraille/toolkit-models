"""SEXUAL AND REPRODUCTIVE HEALTH (products and medical items only) for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/sexual_health_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_contraception_menstrual;
  - the sources looked at for these subjects and left out, with the reason (SEXUAL_HEALTH_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category names, with a plain line, and every answer ends with the note
(general information, not medical advice or a diagnosis; use each product as its own directions say; 911; 988), the same words as the packs' (packs/test_health_life.py checks).

Picture-making (SEXUAL_HEALTH_PICTURE_MAKING_OK): none.
Topics: the health topic (Health and medical pictures; the owner's decision of 22 November 2026): never the sensitive topics,
and not the everyday home add-on. The pack shows products only: no nudity, nothing sexual, no content mark.

    python -c "import sources, sexual_health_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

SEXUAL_HEALTH_SOURCES = [
    Source("commons_contraception_menstrual", "Contraceptive and period products and HIV tests: condoms, IUDs, "
                                              "implants, patches, rings, emergency contraception, menstrual cups, "
                                              "tampons and cloth pads, products only (Wikimedia Commons, ready-made "
                                              "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 5, prepare_pack, "about 70 MB"),
]
SEXUAL_HEALTH_PICTURE_MAKING_OK = set()
SEXUAL_HEALTH_NOT_INCLUDED = {
    "Open Images labels for this subject": "Condom and Tampon have no human-checked photos in Open Images V7 and "
        "Pregnancy test one (counted 2026-11-22).",
    "Period underwear, personal lubricants and dental dams on Commons": "their photos show people in underwear or "
        "sexual products, which the owner's rule keeps out of this collection; not used.",
    "Commons categories that do not exist (2026-11-22)": "Oral contraceptive pills, Birth control pills, Copper IUDs, "
        "Diaphragms (contraception), NuvaRing, Contraceptive sponges, Sanitary napkins, Sanitary pads, Menstrual "
        "pads, HIV self-tests, Pregnancy tests (pregnancy tests are med_vet_packs' Pregnancy test).",
    "Planned Parenthood, Bedsider and makers' product photos": "copyright; not used.",
}
