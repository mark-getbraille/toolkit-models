"""Picture packs for PHOTOGRAPHY (the owner's request of 2026-11-22): cameras of every era, lenses and lighting, film
and the darkroom, and historic photographic processes as objects. Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than
one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise a box camera from a
twin-lens reflex, a lens hood from a lens cap, an enlarger, a safelight, a roll of 120 film, and a daguerreotype from
a tintype, and to say the safety rules that go with darkroom work and the old processes.

Answers say only what the source says (a Commons category's name, the museum record's own words, an Open Images label
people confirmed), never a guess: no maker, model, date or sitter is named unless the category or record names it.
People in historic portraits are described only, never identified beyond the record's own words; files whose words
speak of post-mortem or memorial portraits, or nudity, are left out. The safety notes (the same words in the kit's
photography_sources.py and in the reference books, textbooks/photography.py):
  DARKROOM_NOTE   darkroom chemicals: ventilation, gloves and eye protection, never mix them except as the
                  instructions say, labelled and away from food, children and pets, used fixer to a collection site.
  HISTORIC_NOTE   mercury (daguerreotypes), cyanide and ether (wet collodion): history only, never attempted without
                  expert training.
  UV_NOTE         the UV light of alternative processes (cyanotype, platinum, gum): protect eyes and skin.
  NITRATE_NOTE    old cellulose nitrate film burns fiercely: stored apart, a conservator asked.
  FLASH_NOTE      flash powder and old flashbulbs: history only (flash powder is an explosive mixture).

The packs (PHOTOGRAPHY_PACKS):
  commons_cameras_by_type      Wikimedia Commons (CC0, public domain or CC BY files only): box, folding, twin-lens
                               reflex, rangefinder, view and large format, medium format, SLR and digital SLR,
                               compact, bridge, stereo, panoramic, pinhole, subminiature, toy and disposable cameras,
                               press cameras, daguerreotype cameras and the camera obscura.
  commons_camera_makers        Commons: cameras by maker (Kodak, Leica, Hasselblad, Nikon, Canon, Pentax, Olympus,
                               Minolta, Fujifilm, Zeiss Ikon, Voigtlander, Mamiya, Yashica, Praktica, Exakta, Contax,
                               Zenit, Graflex, Linhof, Rolleiflex, Holga).
  commons_lenses_lighting      Commons: photographic lenses (zoom, prime, telephoto, wide-angle, fisheye, macro), lens
                               mounts, hoods, caps and filters, shutters, viewfinders and bellows, light and exposure
                               meters, electronic flashes, ring flashes, flashbulbs and flash powder (history),
                               tripods, tripod heads, monopods, cable releases and camera straps.
  commons_film_darkroom        Commons: darkrooms, enlargers and safelights, 35 mm, 120, 135, 110 and 126 film,
                               reversal (slide) film and instant film, film canisters, contact sheets, glass plate
                               negatives, photograms, slide projectors, light tables, film scanners and photographic
                               studios.
  commons_historic_processes   Commons: daguerreotypes and their cases, ambrotypes, tintypes, calotypes, salt prints,
                               albumen prints, cartes de visite and cabinet cards, collodion process, cyanotypes,
                               platinum prints, gum bichromate, autochromes, hand-coloured photographs and stereo
                               cards, described as objects.
  nmah_photography             The Smithsonian's National Museum of American History (CC0 pictures from the
                               Smithsonian open-access bucket): cameras, lenses, shutters, light meters, flash units,
                               enlargers and darkroom equipment, projectors and viewers, and daguerreotypes,
                               ambrotypes and tintypes as objects, answered with the record's own name, maker, date,
                               place and materials.
  open_images_photography      Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                               kinds of camera, lenses and camera accessories, darkroom and film things, slides and
                               photo albums, and kinds of photograph. No label is asked twice (packs/test_photography.py
                               checks).

Not repeated here (asked by other packs): device_packs (Film cameras, Instant cameras, Polaroid cameras), things_packs
(Digital cameras; the Open Images labels Digital camera, Instant camera, Single-lens reflex camera, Camera lens,
Tripod, Video camera), chemical_packs (Photographic chemicals), privacy_packs (security cameras), home_health_packs
(Loupes), computer_basics_packs (Memory cards), and the Open Images labels Camera, Photography, Selfie, Projector and
Binoculars. What was looked at and left out is in the kit's photography_sources.py (PHOTOGRAPHY_NOT_INCLUDED).

    python packs/photography_packs.py commons_historic_processes --limit 8      (prints a few rows: a quick check)
"""

import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, listing_out_of_time, pass_random, fetch_all, SI_BUCKET, si_keys
from food_packs import with_twins
from gaps_oi_packs import group, build_oi_gap, QUICK
from outdoor_cooking_packs import thing, with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

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

ASK_WHAT = "What is this?"

# Files whose words speak of post-mortem or memorial portraits are left out (the packs describe objects).
NOT_MEMORIAL = re.compile(r"^(?!.*\b(post[- ]?mortem|memorial portrait|mourning|deceased|dead|corpse|death)\b)",
                          re.I | re.S)

# ----------------------------------------------------------------- Commons: cameras by type

CAMERAS_BY_TYPE = [
    thing("Box cameras", "a box camera, a simple camera with a fixed lens and shutter in a box, made for roll film"),
    thing("Folding cameras", "a folding camera, whose lens on a bellows folds into the body when closed", deeper=True),
    thing("Twin-lens reflex cameras", "a twin-lens reflex (TLR) camera: one lens takes the picture and the other, "
                                      "above it, shows the view on a ground glass seen from above", deeper=True),
    thing("Rangefinder cameras", "a rangefinder camera, focused by lining up two images in its rangefinder window",
          deeper=True),
    thing("View cameras", "a view camera, a large camera on a stand, focused on a ground glass under a dark cloth"),
    thing("Large format cameras", "a large format camera, which takes sheet film of 4 by 5 inches or larger",
          deeper=True),
    thing("Medium format cameras", "a medium format camera, which usually takes 120 roll film", deeper=True),
    thing("SLR cameras", "a single-lens reflex (SLR) camera: a mirror shows the view through the taking lens",
          deeper=True),
    thing("Digital SLR cameras", "a digital single-lens reflex (DSLR) camera", deeper=True),
    thing("Compact cameras", "a compact camera, a small camera with a built-in lens", deeper=True),
    thing("Bridge cameras", "a bridge camera, a digital camera with a long built-in zoom lens", deeper=True),
    thing("Stereo cameras", "a stereo camera, with two lenses side by side for pictures seen in 3D", deeper=True),
    thing("Panoramic cameras", "a panoramic camera, which takes very wide pictures", deeper=True),
    thing("Pinhole cameras", "a pinhole camera, which has a tiny hole instead of a lens"),
    thing("Subminiature cameras", "a subminiature camera, a very small camera for narrow film", deeper=True),
    thing("Toy cameras", "a toy camera, a simple plastic camera"),
    thing("Disposable cameras", "a disposable (single-use) film camera", deeper=True),
    thing("Speed Graphic cameras", "a Speed Graphic, a press camera for sheet film used by news photographers"),
    thing("Daguerreotype cameras", "a daguerreotype camera, a wooden box camera of the 1840s", HISTORIC_NOTE),
    thing("Camera obscura", "a camera obscura, a dark room or box in which a hole or lens throws an image of the "
                            "outside onto a surface", pattern=NOT_MEMORIAL),
]

# ----------------------------------------------------------------- Commons: cameras by maker

CAMERA_MAKERS = [
    thing("Kodak cameras", "a Kodak camera (Eastman Kodak Company)", deeper=True),
    thing("Leica cameras", "a Leica camera", deeper=True),
    thing("Hasselblad cameras", "a Hasselblad camera, a Swedish medium format camera", deeper=True),
    thing("Nikon cameras", "a Nikon camera", deeper=True),
    thing("Canon cameras", "a Canon camera", deeper=True),
    thing("Pentax cameras", "a Pentax camera", deeper=True),
    thing("Olympus cameras", "an Olympus camera", deeper=True),
    thing("Minolta cameras", "a Minolta camera", deeper=True),
    thing("Fujifilm cameras", "a Fujifilm camera", deeper=True),
    thing("Zeiss Ikon cameras", "a Zeiss Ikon camera", deeper=True),
    thing("Voigtländer cameras", "a Voigtlander camera", deeper=True),
    thing("Mamiya cameras", "a Mamiya camera", deeper=True),
    thing("Yashica cameras", "a Yashica camera", deeper=True),
    thing("Praktica cameras", "a Praktica camera", deeper=True),
    thing("Exakta cameras", "an Exakta camera", deeper=True),
    thing("Contax cameras", "a Contax camera", deeper=True),
    thing("Zenit cameras", "a Zenit camera", deeper=True),
    thing("Graflex cameras", "a Graflex camera", deeper=True),
    thing("Linhof cameras", "a Linhof camera", deeper=True),
    thing("Rolleiflex", "a Rolleiflex, a twin-lens reflex camera", deeper=True),
    thing("Holga cameras", "a Holga, a plastic medium format toy camera", deeper=True),
]

# ----------------------------------------------------------------- Commons: lenses, lighting and support

LENSES_LIGHTING = [
    thing("Photographic lenses", "a photographic lens", deeper=True),
    thing("Zoom lenses", "a zoom lens, whose focal length can be changed", deeper=True),
    thing("Prime lenses", "a prime lens, a lens with one fixed focal length", deeper=True),
    thing("Telephoto lenses", "a telephoto lens, a long lens that makes far things look close", deeper=True),
    thing("Wide-angle lenses", "a wide-angle lens, which takes in a wide view", deeper=True),
    thing("Fisheye lenses", "a fisheye lens, an extremely wide lens that bends straight lines", deeper=True),
    thing("Macro lenses", "a macro lens, for photographing small things close up", deeper=True),
    thing("Lens mounts", "a lens mount, the fitting that joins a lens to a camera body", deeper=True),
    thing("Lens hoods", "a lens hood, which shades the lens from stray light"),
    thing("Lens caps", "a lens cap, which covers and protects the front of a lens"),
    thing("Photographic filters", "a photographic filter, glass or resin fitted in front of a lens", deeper=True),
    thing("Camera shutters", "a camera shutter, which opens for a set time to let light reach the film or sensor",
          deeper=True),
    thing("Viewfinders", "a viewfinder, the window through which the photographer frames the picture",
          deeper=True),
    thing("Camera bellows", "camera bellows, the folding light-tight sleeve between lens and body", deeper=True),
    thing("Light meters", "a light meter, which measures light to set the exposure"),
    thing("Exposure meters", "an exposure meter (light meter), which measures light to set the exposure",
          deeper=True),
    thing("Electronic flashes", "an electronic flash unit for a camera", deeper=True),
    thing("Ring flashes", "a ring flash, a round flash around the lens for close-up pictures"),
    thing("Flashbulbs", "a flashbulb, a one-time bulb that burned to make a flash", FLASH_NOTE),
    thing("Flash powder", "flash powder or a flash lamp for it, used for flash pictures before flashbulbs",
          FLASH_NOTE, deeper=True),
    thing("Tripods (photography)", "a camera tripod, a three-legged stand that holds a camera steady", deeper=True),
    thing("Tripod heads", "a tripod head, which holds the camera on a tripod and lets it turn and tilt", deeper=True),
    thing("Monopods", "a monopod, a one-legged camera support"),
    thing("Cable releases", "a cable release, which fires the shutter without touching the camera"),
    thing("Camera straps", "a camera strap", deeper=True),
]

# ----------------------------------------------------------------- Commons: film and the darkroom

FILM_DARKROOM = [
    thing("Darkrooms", "a darkroom, where films and prints are developed", DARKROOM_NOTE, True),
    thing("Enlargers", "a photographic enlarger, which projects a negative onto paper to make a print",
          DARKROOM_NOTE, True),
    thing("Safelights", "a safelight, a dim coloured darkroom lamp that does not fog photographic paper",
          DARKROOM_NOTE),
    thing("35 mm film", "35 mm film", NITRATE_NOTE, True),
    thing("120 film", "120 roll film, the medium format film", deeper=True),
    thing("135 film", "135 film, 35 mm film in a cassette", deeper=True),
    thing("110 film", "110 film, a small cartridge film", deeper=True),
    thing("126 film", "126 film, a square-format cartridge film", deeper=True),
    thing("Reversal film", "reversal (slide) film, which gives positive transparencies", deeper=True),
    thing("Instant film", "instant film, which develops by itself after the picture is taken", deeper=True),
    thing("Film canisters", "a film canister, the small can a roll of film is kept in", deeper=True),
    thing("Contact sheets", "a contact sheet, prints of a whole roll of negatives laid on one sheet of paper",
          deeper=True),
    thing("Glass plate negatives", "a glass plate negative, a photographic negative on a sheet of glass: hold it "
                                   "by its edges", "", True, NOT_MEMORIAL),
    thing("Photograms", "a photogram, a picture made by laying things on photographic paper and exposing it to "
                        "light, without a camera", deeper=True),
    thing("Slide projectors", "a slide projector", deeper=True),
    thing("Light tables", "a light table, a lit surface for viewing negatives and slides"),
    thing("Film scanners", "a film scanner, which makes digital copies of negatives and slides", deeper=True),
    thing("Photographic studios", "a photographic studio", deeper=True, pattern=NOT_MEMORIAL),
]

# ----------------------------------------------------------------- Commons: historic processes as objects

HISTORIC_PROCESSES = [
    thing("Daguerreotypes", "a daguerreotype, a photograph on a silvered copper plate, usually kept in a case "
                            "(1839 to the 1850s)", HISTORIC_NOTE, True, NOT_MEMORIAL),
    thing("Daguerreotype cases", "a daguerreotype case, a small hinged case that holds and protects a "
                                 "daguerreotype or ambrotype", "", False, NOT_MEMORIAL),
    thing("Ambrotypes", "an ambrotype, a collodion photograph on glass backed with black (1850s and 1860s)",
          HISTORIC_NOTE, True, NOT_MEMORIAL),
    thing("Tintypes", "a tintype (ferrotype), a collodion photograph on a thin dark iron plate", HISTORIC_NOTE, True,
          NOT_MEMORIAL),
    thing("Calotypes", "a calotype, an early paper-negative photograph (William Henry Fox Talbot's process)",
          deeper=True, pattern=NOT_MEMORIAL),
    thing("Salt prints", "a salt print (salted paper print), an early photographic print on paper", UV_NOTE, True,
          NOT_MEMORIAL),
    thing("Albumen prints", "an albumen print, a photographic print on paper coated with egg white", "", True,
          NOT_MEMORIAL),
    thing("Cartes de visite", "a carte de visite, a small photograph mounted on a card", "", True, NOT_MEMORIAL),
    thing("Cabinet cards", "a cabinet card, a photograph mounted on a large card", "", True, NOT_MEMORIAL),
    thing("Collodion process", "the wet collodion process, which made glass negatives, ambrotypes and tintypes",
          HISTORIC_NOTE, True, NOT_MEMORIAL),
    thing("Cyanotypes", "a cyanotype, a blue photographic print made with iron salts and sunlight", UV_NOTE, True,
          NOT_MEMORIAL),
    thing("Platinum prints", "a platinum print (platinotype)", UV_NOTE, True, NOT_MEMORIAL),
    thing("Gum bichromate", "a gum bichromate print, made with pigment, gum arabic and a dichromate", UV_NOTE, True,
          NOT_MEMORIAL),
    thing("Autochromes", "an autochrome, an early colour photograph on glass", "", True, NOT_MEMORIAL),
    thing("Hand-colored photographs", "a hand-coloured photograph", "", True, NOT_MEMORIAL),
    thing("Stereo cards", "a stereo card, two nearly matching photographs side by side, seen in 3D with a "
                          "stereoscope", "", True, NOT_MEMORIAL),
]


def build_commons_cameras_by_type(limit):
    """The commons_cameras_by_type pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CAMERAS_BY_TYPE, limit, "camtype")


def build_commons_camera_makers(limit):
    """The commons_camera_makers pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CAMERA_MAKERS, limit, "cammaker")


def build_commons_lenses_lighting(limit):
    """The commons_lenses_lighting pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(LENSES_LIGHTING, limit, "photolens")


def build_commons_film_darkroom(limit):
    """The commons_film_darkroom pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FILM_DARKROOM, limit, "darkroom")


def build_commons_historic_processes(limit):
    """The commons_historic_processes pack (see the module docstring); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(HISTORIC_PROCESSES, limit, "photoproc", adults_only=True)


# ----------------------------------------------------------------- NMAH photographic history (CC0)

# The NMAH object names kept, with the plain words of the answer (the first that matches the record's Object Name or
# title), and the notes that go with them.
NMAH_NAMES = [(re.compile(p, re.I), words, note) for p, words, note in [
    (r"\bdaguerreotypes?\b(?! camera)", "a daguerreotype, a photograph on a silvered copper plate", HISTORIC_NOTE),
    (r"\bambrotypes?\b", "an ambrotype, a collodion photograph on glass", HISTORIC_NOTE),
    (r"\b(tintypes?|ferrotypes?)\b", "a tintype, a collodion photograph on a thin iron plate", HISTORIC_NOTE),
    (r"\bcyanotypes?\b", "a cyanotype, a blue photographic print", UV_NOTE),
    (r"\b(enlargers?|enlarging)\b", "a photographic enlarger", DARKROOM_NOTE),
    (r"\b(developing tanks?|developing tray|film tank|processing tank|print washer|print dryer|darkroom)\b",
     "darkroom equipment", DARKROOM_NOTE),
    (r"\bsafelights?\b", "a darkroom safelight", DARKROOM_NOTE),
    (r"\b(exposure|light) meters?\b|\bphotometers?\b|\bactinometers?\b", "a light (exposure) meter", ""),
    (r"\bflash ?(bulbs?|lamps?|guns?|units?|powder)\b|\bflashgun\b", "a photographic flash", FLASH_NOTE),
    (r"\bshutters?\b", "a camera shutter", ""),
    (r"\blens(es)?\b(?! cap)", "a photographic lens", ""),
    (r"\bstereoscopes?\b|\bstereo viewers?\b", "a stereoscope, a viewer for stereo pictures", ""),
    (r"\b(slide|lantern) projectors?\b|\bmagic lanterns?\b", "a projector for slides", ""),
    (r"\btripods?\b", "a camera tripod", ""),
    (r"\bcameras?\b", "a camera", ""),
]]
NMAH_PHOTO_NOT = re.compile(r"\b(motion picture|movie|cine|television|video|x-ray|surveillance|gun camera|toy gun|"
                            r"patent model|postcard|poster|stamp|coin|medal|post[- ]?mortem|memorial|mourning|"
                            r"deceased|nude|naked)\b", re.I)
NMAH_PHOTO_WORDS = re.compile(r"camera|daguerreotype|ambrotype|tintype|ferrotype|cyanotype|enlarger|darkroom|"
                              r"safelight|light meter|exposure meter|flash|shutter|photographic|stereoscope|lantern",
                              re.I)


def nmah_photo_row(record):
    """(picture address, rows) for an NMAH record of a camera, lens, darkroom thing or historic photograph object
    with a CC0 picture, or None. The answer gives the record's own object name, maker, date, place and materials;
    nothing about a sitter beyond the record's own title."""
    content = record.get("content") or {}
    title = clean(record.get("title") or "")
    free = content.get("freetext") or {}
    names = [clean(o.get("content")) for o in free.get("objectType") or [] if o.get("label") == "Object Name"]
    object_name = names[0] if names else title
    text = f"{object_name} {title}"
    if NMAH_PHOTO_NOT.search(text):
        return None
    found = next(((w, n) for p, w, n in NMAH_NAMES if p.search(object_name) or p.search(title)), None)
    if not found:
        return None
    plain, note = found
    media = ((content.get("descriptiveNonRepeating") or {}).get("online_media") or {}).get("media") or []
    picture = next((m for m in media if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"
                    and m.get("content")), None)
    if not picture:
        return None
    makers = [clean(n.get("content")) for n in free.get("name") or [] if "maker" in (n.get("label") or "").lower()
              or "manufacturer" in (n.get("label") or "").lower()]
    makers = [m for m in makers if not re.match(r"^(unknown|unidentified|anonymous)\b", m, re.I)]
    dates = [clean(d.get("content")) for d in free.get("date") or [] if "made" in (d.get("label") or "").lower()]
    places = [clean(p.get("content")) for p in free.get("place") or [] if "made" in (p.get("label") or "").lower()]
    materials = [clean(p.get("content")) for p in free.get("physicalDescription") or []
                 if "material" in (p.get("content") or "")]
    materials = [re.sub(r"\s*\((?:overall|\?+|unknown) material\)|\((?:part: )?([a-z ]+?) material\)",
                        lambda m: f"({m.group(1)})" if m.group(1) else "", m) for m in materials]
    answer = f"This is {plain}"
    if title and title.lower() not in plain.lower():
        answer += f" (its record calls it \"{title}\")"
    if makers:
        answer += f", made by {makers[0]}"
    if places:
        answer += (" in " if makers else ", made in ") + places[0].replace("United States: ", "")
    if dates:
        answer += f", {dates[0]}"
    answer += "."
    materials = [m.strip() for m in materials if m.strip()]
    if materials:
        answer += f" Its record gives its materials: {', '.join(materials)}."
    if note:
        answer += f" {note}"
    ids = content.get("descriptiveNonRepeating") or {}
    credit = (f"National Museum of American History, Smithsonian Institution, CC0: {title} "
              f"({ids.get('record_ID', '')}), {ids.get('guid', '')}")
    return picture["content"] + "&max=2048", [{"question": ASK_WHAT, "answer": answer, "credit": credit}]


def build_nmah_photography(limit):
    """The NMAH records of cameras, lenses, darkroom equipment and historic photograph objects with a CC0 picture,
    read from the Smithsonian open-access bucket (the museum's metadata files, in a fixed shuffled order, a quick word
    check before each record is read), until enough are found or the listing time is spent."""
    s, items = session(), []
    keys = si_keys("nmah")
    pass_random("nmah-photography").shuffle(keys)
    for key in keys:
        if listing_out_of_time() or len(items) >= limit * 1.2:
            break
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=300).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            if '"CC0"' not in line or not NMAH_PHOTO_WORDS.search(line[:4000]):
                continue
            try:
                got = nmah_photo_row(json.loads(line))
            except ValueError:
                continue
            if got:
                url, rows = got
                items.append((f"nmah-photo-{len(items):05d}.jpg", url, rows))
        say(f"  NMAH {key.rsplit('/', 1)[-1]}: {len(items)} records so far")
    pass_random("nmah-photography-order").shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=6, pause=0.1)[:limit])


# ----------------------------------------------------------------- Open Images

PHOTOGRAPHY_OI = [
    group("What kind of camera is in this picture?",
          {"Film camera": "a film camera", "Box camera": "a box camera", "Reflex camera": "a reflex camera",
           "Point-and-shoot camera": "a point-and-shoot camera", "Disposable camera": "a disposable camera",
           "Mirrorless interchangeable-lens camera": "a mirrorless camera", "Stereo camera": "a stereo camera"}),
    group("What camera lenses or accessories are in this picture?",
          {"Lens": "a lens", "Telephoto lens": "a telephoto lens", "Fisheye lens": "a fisheye lens",
           "Lens cap": "a lens cap", "Lens hood": "a lens hood", "Camera accessory": "a camera accessory",
           "Camera strap": "a camera strap", "Camera battery": "a camera battery",
           "Camera remote control": "a camera remote control", "Light meter": "a light meter",
           "Flash (Photography)": "a camera flash"}),
    group("What darkroom or film things are in this picture?",
          {"Darkroom": "a darkroom", "Enlarger": "an enlarger", "Photographic film": "photographic film",
           "Negative": "a negative", "Photographic paper": "photographic paper",
           "Photographic fixer": "photographic fixer"}, DARKROOM_NOTE),
    group("What photographs or viewers are in this picture?",
          {"Photograph album": "a photo album", "Slide projector": "a slide projector",
           "Digital photo frame": "a digital photo frame", "Photo booth": "a photo booth"}),
    group("What kind of photography is this?",
          {"Monochrome photography": "black-and-white (monochrome) photography",
           "Macro photography": "macro (close-up) photography", "Aerial photography": "aerial photography",
           "Still life photography": "still life photography", "Panorama": "a panorama"}),
]


def build_open_images_photography(limit):
    """open_images_photography (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_photography", PHOTOGRAPHY_OI, limit, 9411), PHOTOGRAPHY_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
NMAH_LICENCE = ("National Museum of American History, Smithsonian Institution (Smithsonian Open Access, "
                "https://www.si.edu/openaccess): pictures and records CC0, each record credited below.")
PHOTOGRAPHY_PACKS = {
    "commons_cameras_by_type": (build_commons_cameras_by_type, COMMONS_LICENCE.format(
        what="box, folding, twin-lens reflex, rangefinder, view, large and medium format, SLR, compact, stereo, "
             "panoramic, pinhole and other camera")),
    "commons_camera_makers": (build_commons_camera_makers, COMMONS_LICENCE.format(what="cameras-by-maker")),
    "commons_lenses_lighting": (build_commons_lenses_lighting, COMMONS_LICENCE.format(
        what="lens, filter, shutter, light meter, flash, tripod and camera accessory")),
    "commons_film_darkroom": (build_commons_film_darkroom, COMMONS_LICENCE.format(
        what="darkroom, enlarger, safelight, film format, contact sheet, glass plate, slide projector and studio")),
    "commons_historic_processes": (build_commons_historic_processes, COMMONS_LICENCE.format(
        what="daguerreotype, ambrotype, tintype, calotype, salt and albumen print, cyanotype, platinum print and "
             "other historic photographic process")),
    "nmah_photography": (build_nmah_photography, NMAH_LICENCE),
    "open_images_photography": (build_open_images_photography, OI_LICENCE),
}
PHOTOGRAPHY_LIMITS = {
    "commons_cameras_by_type": 1200,       # 20 categories
    "commons_camera_makers": 1200,         # 21 makers
    "commons_lenses_lighting": 1200,       # 25 categories
    "commons_film_darkroom": 1100,         # 18 categories
    "commons_historic_processes": 1500,    # 16 categories, albumen prints and glass plates large
    "nmah_photography": 600,               # the NMAH photographic history records with a CC0 picture
    "open_images_photography": 1500,       # 34 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
PHOTOGRAPHY_COMMONS_KEYS = ("commons_cameras_by_type", "commons_camera_makers", "commons_lenses_lighting",
                            "commons_film_darkroom", "commons_historic_processes")
# The Commons category specs of the packs (for the self-test).
PHOTOGRAPHY_SPECS = CAMERAS_BY_TYPE + CAMERA_MAKERS + LENSES_LIGHTING + FILM_DARKROOM + HISTORIC_PROCESSES


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try a photography pack builder.")
    parser.add_argument("key", choices=sorted(PHOTOGRAPHY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = PHOTOGRAPHY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
