"""The photography manual collections (the owner's request of 2026-11-22), under the heading "Arts and crafts" with the
darkroom chemicals collection photo_chemicals (chemicals.py). categories.py adds them to CATEGORIES and gives the
three keys of HEADING_KEYS the heading.

What they list, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  film_cameras_darkroom  Film cameras of every era and darkroom equipment: the Internet Archive's manual collections
                         searched by FILM_WORDS (camera instruction books, rangefinders, twin-lens reflexes, medium
                         and large format, enlargers, light meters, flash units, developing tanks, slide projectors);
                         the film and darkroom makers (Kodak, Ilford, Polaroid, Leica, Hasselblad, Mamiya, Lomography,
                         Paterson, Beseler) LINK-ONLY by the owner's rule; the US Army's camera and darkroom equipment
                         manuals of the 1940s (public domain, public_guides, each judged by the military release
                         rule); and Mike Butkus's camera manual library, link-only (his own scans under his own
                         terms).
  digital_cameras        Digital cameras and accessories: the Internet Archive's manuals searched by DIGITAL_WORDS
                         (mirrorless, DSLR, compact and bridge cameras, action cameras, camera lenses, speedlights,
                         camera gimbals); the camera makers (Canon, Nikon, Sony, Fujifilm, Panasonic, Pentax/Ricoh, OM
                         System/Olympus, Leica, Hasselblad, GoPro, DJI) LINK-ONLY.
No word another collection already searches is used: "film camera" and "35mm" are older_electronics', "digital
camera" personal_electronics', "trail camera" outdoors', "security camera" privacy_security's.

The notice is said first (NOTICE): darkroom chemicals (ventilation, gloves, never mix, disposal; their safety data
sheets are in photo_chemicals), lithium batteries, old flash units' high-voltage capacitors, and old nitrate film.
The reference books are in the library's photography group (textbooks/photography.py, request word photography).
"""

HEADING = "Arts and crafts"
# The collections under the heading here (photo_chemicals is chemicals.py's darkroom chemicals collection).
HEADING_KEYS = ("film_cameras_darkroom", "digital_cameras", "photo_chemicals")

NOTICE = ("Read the safety section first. Darkroom chemicals: work with good ventilation, wear nitrile gloves and eye "
          "protection, never mix them except as the instructions say, and take used fixer and other solutions to a "
          "collection site as local rules say (their safety data sheets are in the collection photo_chemicals). "
          "Charge camera batteries only with their own charger, and never use a swollen or damaged lithium battery. "
          "Old flash units hold a high-voltage capacitor that can shock even when switched off: do not open them. "
          "Old film on cellulose nitrate base burns fiercely: store it apart and ask a conservator.")

FILM_WORDS = ["camera instruction book", "camera instructions", "rangefinder camera", "twin lens reflex",
              "medium format", "large format", "view camera", "folding camera", "box camera", "enlarger",
              "light meter", "exposure meter", "flash unit", "flashgun", "developing tank", "slide projector",
              "kodak", "brownie", "polaroid land", "rolleiflex", "yashica", "pentax spotmatic", "nikon f",
              "canon ae-1", "minolta srt", "olympus om"]

DIGITAL_WORDS = ["mirrorless camera", "dslr", "digital slr", "compact camera", "bridge camera", "action camera",
                 "gopro", "camera lens", "speedlight", "speedlite", "camera gimbal", "lumix", "cyber-shot", "coolpix",
                 "powershot", "finepix", "eos rebel"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")


def _makers(category, prefix, makers):
    """The makers of one collection, each link-only with the shared reason."""
    return [dict(category=category, prefix=prefix, documents="manuals and guides", access="link", reason=RULE,
                 types=[], **m) for m in makers]


FILM_MAKERS = _makers("film_cameras_darkroom", "fc", [
    dict(key="kodak-film", maker="Kodak (film and photo chemicals; Kodak Alaris and Kodak Professional)",
         type="film, data sheets and technical publications", library="https://imaging.kodakalaris.com/",
         site="kodakalaris.com"),
    dict(key="ilford-photo", maker="Ilford Photo (Harman Technology)", type="film, paper and darkroom technical "
         "sheets", library="https://www.ilfordphoto.com/", site="ilfordphoto.com"),
    dict(key="polaroid", maker="Polaroid", type="instant cameras and film", library="https://www.polaroid.com/",
         site="polaroid.com"),
    dict(key="leica", maker="Leica Camera", type="film and digital cameras and lenses",
         library="https://leica-camera.com/", site="leica-camera.com"),
    dict(key="hasselblad", maker="Hasselblad", type="medium format cameras", library="https://www.hasselblad.com/",
         site="hasselblad.com"),
    dict(key="mamiya", maker="Mamiya (Phase One)", type="medium format cameras", library="https://www.phaseone.com/",
         site="phaseone.com"),
    dict(key="lomography", maker="Lomography", type="film cameras, lenses and film", library="https://www.lomography.com/",
         site="lomography.com"),
    dict(key="paterson", maker="Paterson Photographic", type="developing tanks and darkroom equipment",
         library="https://www.patersonphotographic.com/", site="patersonphotographic.com"),
    dict(key="beseler", maker="Beseler", type="enlargers", library="https://www.beselerphoto.com/",
         site="beselerphoto.com"),
    dict(key="butkus", maker="Mike Butkus's camera manual library (orphancameras.com, butkus.org)",
         type="scans of old camera, flash and meter manuals (his own scans under his own terms)",
         library="https://www.orphancameras.com/", site="orphancameras.com"),
])

DIGITAL_MAKERS = _makers("digital_cameras", "dc", [
    dict(key="canon-cameras", maker="Canon", type="EOS and PowerShot cameras, lenses and speedlites",
         library="https://www.usa.canon.com/support", site="canon.com"),
    dict(key="nikon-cameras", maker="Nikon", type="Z, D and Coolpix cameras, lenses and speedlights",
         library="https://downloadcenter.nikonimglib.com/", site="nikonimglib.com"),
    dict(key="sony-cameras", maker="Sony", type="Alpha and Cyber-shot cameras and lenses",
         library="https://www.sony.com/electronics/support", site="sony.com"),
    dict(key="fujifilm-cameras", maker="Fujifilm", type="X and GFX cameras, lenses and instax",
         library="https://fujifilm-x.com/support/", site="fujifilm-x.com"),
    dict(key="panasonic-lumix", maker="Panasonic (Lumix)", type="Lumix cameras and lenses",
         library="https://help.na.panasonic.com/", site="panasonic.com"),
    dict(key="ricoh-pentax", maker="Ricoh Imaging (Pentax and Ricoh)", type="Pentax and Ricoh GR cameras",
         library="https://www.ricoh-imaging.com/", site="ricoh-imaging.com"),
    dict(key="om-system-cameras", maker="OM Digital Solutions (OM System and Olympus)", type="OM System and Olympus cameras",
         library="https://explore.omsystem.com/", site="omsystem.com"),
    dict(key="gopro", maker="GoPro", type="action cameras", library="https://community.gopro.com/", site="gopro.com"),
    dict(key="dji-cameras", maker="DJI", type="camera gimbals and pocket cameras", library="https://www.dji.com/support",
         site="dji.com"),
])


def _guide(ia, title, year):
    """One US Army camera or darkroom equipment manual: its Internet Archive item, title and year (military: its
    front text is read by the shared release check)."""
    return dict(ia=ia, title=title, by="the US Army", year=year, military=True)


ARMY_GUIDES = [
    _guide("TM11-404", "Photographic Darkroom Equipment: Processing Equipment PH-395 (TM 11-404, 1943)", 1943),
    _guide("TM11-405", "Photographic Darkroom Equipment: Processing Equipment PH-406 (TM 11-405, 1943)", 1943),
    _guide("TM11-2352", "Camera Equipment PH-104 (TM 11-2352, 1945)", 1945),
    _guide("TM11-2361", "Camera PH-324 (TM 11-2361, 1945)", 1945),
    _guide("TM11-2364", "Camera PH-501/PF (TM 11-2364, 1944)", 1944),
    _guide("TM11-2366", "Photographic Equipment PH-383 (TM 11-2366, 1944)", 1944),
    _guide("TM11-2377", "Camera PH-503/PF (TM 11-2377, 1945)", 1945),
]

GUIDANCE = [
    dict(title="Photography: a guide to the library (in the reference library: photo:index, request word "
               "photography)", url="https://github.com/mark-getbraille/toolkit-models", by="the toolkit"),
    dict(title="Photographic and darkroom chemicals: safety data sheets (manual collection photo_chemicals)",
         url="https://www.ilfordphoto.com/", by="the toolkit (the chemicals collection)"),
    dict(title="Caring for photographs (Library of Congress; in the reference library: photo:loc_care_photographs)",
         url="https://www.loc.gov/preservation/care/photo.html", by="the Library of Congress"),
    dict(title="Mike Butkus's camera manual library (his own scans and terms; open it in a browser)",
         url="https://www.orphancameras.com/", by="Mike Butkus"),
]

CATEGORIES = {
    "film_cameras_darkroom": dict(
        name="Film cameras and darkroom equipment (manuals)",
        description="Film cameras of every era (box, folding, rangefinder, twin-lens reflex, SLR, medium and large "
                    "format, instant), light meters, flash units, enlargers, developing tanks and slide projectors: "
                    "the Internet Archive's manuals, the makers' pages and Mike Butkus's library as links, and the "
                    "US Army's camera and darkroom equipment manuals of the 1940s (public domain).",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker; the Army manuals are US "
                                "government works (public domain)",
        any_year=True, ia=FILM_WORDS, makers=FILM_MAKERS, public_guides=ARMY_GUIDES, guidance=GUIDANCE,
        notice=NOTICE, heading=HEADING,
        ia_exclude=r"\b(video game|game manual|toy|motion picture|cine|movie|projector lamp catalog(?:ue)?)\b"),
    "digital_cameras": dict(
        name="Digital cameras, lenses and flashes (manuals)",
        description="Mirrorless, DSLR, compact, bridge and action cameras, camera lenses, speedlights and camera "
                    "gimbals: the Internet Archive's manuals and the camera makers' manual pages (links).",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=DIGITAL_WORDS, makers=DIGITAL_MAKERS, guidance=GUIDANCE, notice=NOTICE, heading=HEADING),
}
