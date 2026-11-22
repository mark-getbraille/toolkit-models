"""PHOTOGRAPHY for the Picture Model Training Kit (the owner's request of 2026-11-22: cameras of every era, lenses and
lighting, film and the darkroom, and historic photographic processes). This file lists:
  - the ready-made packs built in packs/photography_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_cameras_by_type, commons_camera_makers, commons_lenses_lighting, commons_film_darkroom,
    commons_historic_processes, nmah_photography and open_images_photography;
  - the share-alike Commons files of the main camera, lens and darkroom categories (group "share-alike": only with
    the share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (PHOTOGRAPHY_NOT_INCLUDED);
  - which topic add-ons hold them (PHOTOGRAPHY_TOPICS): "art" and "crafts" hold every one, "machines" the camera,
    lens and darkroom equipment packs (cameras as devices). No new topic.

As in making_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, the museum record's words, a label
people checked). People in historic portraits are described, never identified beyond the record. The darkroom,
historic process, UV, nitrate film and flash powder notes are the same words as the packs'
(packs/test_photography.py checks).

Picture-making (PHOTOGRAPHY_PICTURE_MAKING_OK): the Commons camera, maker, lens and darkroom collections and the
share-alike one (things); never the historic processes (mostly portraits of people), the NMAH records (daguerreotypes
and tintypes among them) or the Open Images photos, which show people.

    python -c "import sources, photography_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/photography_packs.py.
DARKROOM_NOTE = ("Darkroom safety: work with good ventilation, wear nitrile gloves and eye protection, never mix "
                 "photographic chemicals except as their instructions say, keep them labelled and away from food, "
                 "children and pets, and take used fixer (it carries silver) and other used solutions to a collection "
                 "site as local rules say.")
HISTORIC_NOTE = ("Historic processes: daguerreotypes were developed over heated mercury, and wet collodion used ether "
                 "and potassium cyanide; these are history only: never attempt them without expert training and "
                 "proper equipment.")
UV_NOTE = ("UV light: alternative processes such as cyanotype, platinum and gum prints are exposed in sunlight or "
           "under UV lamps: protect your eyes and skin, and wear gloves with the sensitising chemicals.")
NITRATE_NOTE = ("Old film: film on cellulose nitrate base (common before the 1950s) burns fiercely and gives off "
                "toxic gas: store it apart, cool and away from heat, and ask a conservator.")
FLASH_NOTE = ("History only: flash powder is an explosive mixture and old flashbulbs can shatter; never make or fire "
              "them.")

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
NMAH_OPEN = "Pictures and records CC0 (Smithsonian Open Access)"
NMAH_CREDIT = "National Museum of American History, Smithsonian Institution, https://www.si.edu/openaccess"
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def gear(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# The main categories of packs/photography_packs.py whose files need no word filter (the share-alike entry has none):
# camera types, lenses and the darkroom; no portraits. The answers are the packs' own words.
PHOTOGRAPHY_SA = [
    gear("Box cameras", "a box camera, a simple camera with a fixed lens and shutter in a box, made for roll film"),
    gear("Folding cameras", "a folding camera, whose lens on a bellows folds into the body when closed", deeper=True),
    gear("Twin-lens reflex cameras", "a twin-lens reflex (TLR) camera: one lens takes the picture and the other, "
                                     "above it, shows the view on a ground glass seen from above", deeper=True),
    gear("Rangefinder cameras", "a rangefinder camera, focused by lining up two images in its rangefinder window",
         deeper=True),
    gear("View cameras", "a view camera, a large camera on a stand, focused on a ground glass under a dark cloth"),
    gear("SLR cameras", "a single-lens reflex (SLR) camera: a mirror shows the view through the taking lens",
         deeper=True),
    gear("Photographic lenses", "a photographic lens", deeper=True),
    gear("Lens hoods", "a lens hood, which shades the lens from stray light"),
    gear("Exposure meters", "an exposure meter (light meter), which measures light to set the exposure",
         deeper=True),
    gear("Darkrooms", "a darkroom, where films and prints are developed", DARKROOM_NOTE, True),
    gear("Enlargers", "a photographic enlarger, which projects a negative onto paper to make a print", DARKROOM_NOTE,
         True),
    gear("120 film", "120 roll film, the medium format film", deeper=True),
]


def prepare_photography_commons_sa(source, data_dir, work, cap):
    """Commons camera, lens and darkroom categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(PHOTOGRAPHY_SA, cap, source.test, "photo-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

PHOTOGRAPHY_SOURCES = [
    Source("commons_cameras_by_type", "Cameras by type: box, folding, twin-lens reflex, rangefinder, view and large "
                                      "format, medium format, SLR and digital SLR, compact, bridge, stereo, panoramic, "
                                      "pinhole, subminiature, toy, disposable and press cameras and the camera "
                                      "obscura (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 260 MB"),
    Source("commons_camera_makers", "Cameras by maker: Kodak, Leica, Hasselblad, Nikon, Canon, Pentax, Olympus, "
                                    "Minolta, Fujifilm, Zeiss Ikon, Voigtlander, Mamiya, Yashica, Praktica, Exakta, "
                                    "Contax, Zenit, Graflex, Linhof, Rolleiflex and Holga (Wikimedia Commons, "
                                    "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 260 MB"),
    Source("commons_lenses_lighting", "Lenses, lighting and camera supports: zoom, prime, telephoto, wide-angle, "
                                      "fisheye and macro lenses, mounts, hoods, caps, filters, shutters, viewfinders, "
                                      "light meters, flashes and flashbulbs, tripods, monopods and cable releases "
                                      "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 260 MB"),
    Source("commons_film_darkroom", "Film and the darkroom: darkrooms, enlargers, safelights, film formats, film "
                                    "canisters, contact sheets, glass plate negatives, photograms, slide "
                                    "projectors, light tables, film scanners and studios, with darkroom safety notes "
                                    "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1100, 15, prepare_pack, "about 240 MB"),
    Source("commons_historic_processes", "Historic photographic processes as objects: daguerreotypes and cases, "
                                         "ambrotypes, tintypes, calotypes, salt and albumen prints, cartes de visite, "
                                         "cabinet cards, collodion, cyanotypes, platinum and gum prints, autochromes, "
                                         "hand-coloured photographs and stereo cards (Wikimedia Commons, ready-made "
                                         "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 330 MB"),
    Source("nmah_photography", "The National Museum of American History's photographic history objects: cameras, "
                               "lenses, shutters, light meters, flashes, enlargers and darkroom equipment, viewers, "
                               "and daguerreotypes, ambrotypes and tintypes as objects (Smithsonian Open Access, "
                               "ready-made pack)",
           NMAH_OPEN, NMAH_CREDIT, "permissive", 600, 10, prepare_pack, "about 130 MB"),
    Source("open_images_photography", "Kinds of camera, lenses and camera accessories, light meters and flashes, "
                                      "darkrooms, enlargers, film, negatives and photographic paper, photo albums, "
                                      "slide projectors and kinds of photograph (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 320 MB"),
    Source("photography_commons_sa", "Wikimedia Commons: box, folding, twin-lens reflex, rangefinder, view and SLR "
                                     "cameras, lenses, lens hoods, exposure meters, darkrooms, enlargers and 120 "
                                     "film, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 700, 10, prepare_photography_commons_sa,
           "about 150 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: cameras, lenses and darkroom things.
PHOTOGRAPHY_PICTURE_MAKING_OK = {"commons_cameras_by_type", "commons_camera_makers", "commons_lenses_lighting",
                                 "commons_film_darkroom", "photography_commons_sa"}

# Which topic add-ons hold each collection (topics.py lists the same keys; packs/test_photography.py checks).
_EQUIPMENT = ("commons_cameras_by_type", "commons_camera_makers", "commons_lenses_lighting", "commons_film_darkroom",
              "photography_commons_sa")
PHOTOGRAPHY_TOPICS = {
    "art": tuple(s.key for s in PHOTOGRAPHY_SOURCES),
    "crafts": tuple(s.key for s in PHOTOGRAPHY_SOURCES),
    "machines": _EQUIPMENT,
}

PHOTOGRAPHY_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Film cameras, Instant cameras and Polaroid cameras "
        "(device_packs), Digital cameras (things_packs), Photographic chemicals (chemical_packs), security cameras "
        "(privacy_packs), Loupes (home_health_packs) and Memory cards (computer_basics_packs): not asked twice.",
    "Commons categories that do not exist under the names tried (November 2026)": "Single-lens reflex cameras, "
        "Digital single-lens reflex cameras, Mirrorless interchangeable-lens cameras, Mirrorless cameras, "
        "Point-and-shoot cameras, Press cameras, Brownie cameras, Camera phones, Photographic film, Photographic "
        "negatives, Photographic paper, Photographic enlargers, Developing tanks, Photographic trays, Softboxes, "
        "Photographic reflectors, Leaf shutters, Focal-plane shutters, Sheet film, Roll film, Dry plates, "
        "Photographic slides, Union cases, Salted paper prints, Palladium prints, Carbon prints, Woodburytypes, "
        "Wet plate collodion, Cellulose nitrate film, Kallitypes, Lumen prints and Vandyke brown prints; Action cameras, Camera lenses, "
        "Flash (photography), Photogravures, Stereographs and Lantern slides exist but hold no files. The packs use "
        "the categories that hold files (SLR cameras, Digital SLR cameras, Enlargers, Salt prints, Collodion "
        "process, Stereo cards ...).",
    "Open Images labels asked elsewhere": "Camera, Digital camera, Instant camera, Single-lens reflex camera, Camera "
        "lens, Tripod, Video camera, Photography, Selfie, Projector and Binoculars: asked by other packs, never "
        "twice. Nude photography is never asked; Photographer, Portrait and Photo shoot are people photos and are "
        "left out.",
    "Science Museum Group collection (London)": "Its object pictures are CC BY-NC-SA (non-commercial share-alike) "
        "with some CC BY; not checked picture by picture, so not used in this version (a personal-use candidate). "
        "https://collection.sciencemuseumgroup.org.uk/",
    "The Metropolitan Museum of Art's photographs (daguerreotypes and others)": "Open Access CC0, but the Met's "
        "photographs department is almost all portraits and views, and few photographic apparatus objects; the "
        "general Met packs already read the Met's open access. Not repeated.",
    "George Eastman Museum and other camera museum collections": "Their pictures carry their own terms (no open "
        "licence found for the object photos); not used. https://www.eastman.org/",
    "Makers' product photos (Canon, Nikon, Sony, Fujifilm, Leica, Hasselblad, Ilford, Kodak Alaris, Polaroid, "
    "Lomography)": "the makers' copyright; not used. Their manuals are listed as links in the manual collections "
        "film_cameras_darkroom and digital_cameras.",
    "Mike Butkus's camera manual library (butkus.org)": "his own scans under his own terms: link-only in the manual "
        "collection film_cameras_darkroom, never a picture source.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the photography share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PHOTOGRAPHY_SOURCES if s.key == "photography_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="photography-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
