"""STILLS FROM PUBLIC-DOMAIN FILMS for the Picture Model Training Kit (the owner's request of 2026-11-22: pictures for
the picture describer, toward his video description feature). This file lists the ready-made pack built in
packs/film_stills_packs.py (group "permissive"; the kit downloads it with prepare_pack) and what was looked at and
left out, with the reason (FILM_STILLS_NOT_INCLUDED):
  pd_film_stills   a few stills from each of many public-domain films on the Internet Archive: Prelinger Archives
                   films that carry a public-domain mark, and National Park Service and NASA films (US government
                   works). Each still is answered with the film's title, year, maker and the archive's own
                   description of the film, quoted; nothing is said about what the still itself shows. Stills of
                   films with no description go to the pack's needs zip, for a person to describe (the Describe
                   pictures window, needs_workspace.py).

The guidelines for describing video (the DCMP Description Key as a link, the W3C's audio description pages, the FCC's
rules) are the reference book "audio-description" (textbooks/audio_description.py). The civil defense films are the
cd_films pack. Topics: art (Art and museum objects) and people (People and everyday activities). Picture-making
(FILM_STILLS_PICTURE_MAKING_OK): none (the stills show people).

    python -c "import sources, film_stills_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

FILM_STILLS_SOURCES = [
    Source("pd_film_stills", "Stills from public-domain films (Prelinger Archives, National Park Service, NASA) with "
                             "each film's title, year, maker and description (Internet Archive, ready-made pack)",
           "Public domain (the item's public-domain mark, or a US government work, 17 U.S.C. 105; each film's basis "
           "in CREDITS.txt)", "Prelinger Archives, the National Park Service and NASA, via the Internet Archive, "
           "https://archive.org", "permissive", 2500, 25, prepare_pack, "about 300 MB"),
]

FILM_STILLS_PICTURE_MAKING_OK = set()

FILM_STILLS_NOT_INCLUDED = {
    "Prelinger films without a public-domain mark": "the Prelinger Archives' own advice: 'DO NOT ASSUME that all "
        "Prelinger Archives films are in the public domain'; only marked films are used.",
    "Home movies, outtakes and unedited reels": "private people who never agreed to be shown, and no description "
                                                "of their own.",
    "Films whose records name racist caricature or minstrel shows": "left out (they are not taught as normal).",
    "Described Video (DCMP) and audio-described films": "the Described and Captioned Media Program's videos are its "
        "and their makers' copyright, lent to eligible users only; not used.",
    "Civil defense films": "already the cd_films pack.",
}
