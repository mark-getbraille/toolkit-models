"""Photography for the reference library, in its own group "Reference, photography" (the owner's request of
2026-11-22): digital and film cameras and their controls, lenses, composition and lighting, editing, file formats and
archiving, the darkroom, historic and alternative processes, photo conservation and the history of photography.
Keys: photography (every book), photo:<name>. The arts and crafts guide (arts:index) lists these books by the request
word photography.

What this module builds, in plain words, each IN FULL:
  - photo:index, a guide to photography in the library: cameras and the exposure triangle, lenses, composition and
    lighting, phones and photography for blind and low-vision people, editing, file formats and archiving,
    printing, film and film cameras, exposure without a meter (sunny 16), the darkroom, historic and alternative
    processes, conservation, history, and the manual collections and picture packs (CC0, the toolkit's own list);
  - US Navy and Army photography manuals from the Internet Archive, each judged at every build by the release rule
    for military publications (military_release.py; the builder says truthfully what the front pages print): the
    Navy's Photography (Basic) NAVEDTRA 14209 (1993) and Photography (Advanced) NAVEDTRA 14208 (1995), the Navy
    Photographer's Mate Training Series modules 3 and 4 (1983) and Photographer's Mate 1 & C (1974), the Army's
    Still Photography TM 11-401-2 (1969), and the Air Corps' Basic Photography TM 1-219 (1941), Aerial Photography
    TM 1-220 (1941) and FM 1-35 (1941) and FM 30-21 Role of Aerial Photography (1940). Read whole (no part of them is
    about explosives);
  - the Federal Agencies Digital Guidelines Initiative's Technical Guidelines for Digitizing Cultural Heritage
    Materials (third edition, 2023), the Library of Congress's still image format descriptions (Sustainability of
    Digital Formats: TIFF, JPEG, JPEG 2000, PNG, DNG and camera raw and others) and its pages on caring for
    photographs, albums, light damage and digitising collections; the National Archives' pages on preserving
    photographs, film-based negatives and family archives;
  - the National Park Service's Conserve O Gram leaflets on photographs (series 14: mounting corners, enclosures,
    chronology of processes, caring for prints, colour, special formats and monochrome processes, film-base
    identification, cold storage) and its nitrate film leaflets, and the NPS Museum Handbook's appendices on
    photographic collections (R) and cellulose nitrate and ester film (M);
  - the darktable user manual (GPL 3.0) and the GIMP 3.0 user manual (GFDL 1.2 or later), share-alike, separate
    books (both programs are mouse-driven: the books are for learning their words and for sighted helpers);
  - old public-domain photography books (published before 1931; the builder checks each item's year at every
    build): Eastman Kodak's How to Make Good Pictures (1920), Picture Taking and Picture Making (1898), Elementary
    Photographic Chemistry (1924) and its camera instruction books (Bulls-Eye 1895, No. 4A Folding Kodak 1906);
    Mees's Fundamentals of Photography (1920), Neblette (1927), Abney, Hasluck, Cassell's Cyclopaedia (1911), Wall's
    Dictionary (1897), the British Journal Photographic Almanac (1915), Roche and Anthony's How to Make Photographs
    (1883), Watkins on exposure and development (1919), Bayley on enlarging (1910), Taylor and Hodges on lenses; the
    historic processes (Snelling on the daguerreotype 1850, Hardwich and Humphrey on collodion 1857, Coale on
    albumen 1858, Towler's Silver Sunbeam 1864, Burbank's printing methods 1891, Maclean 1898, Bolte's carbon
    printing 1897, the Platinotype 1916) and histories (Tissandier 1877, Werge 1890, Brothers 1899).
  Every book carries PHOTO_SAFETY in its notice: darkroom chemicals (ventilation, gloves, never mix, disposal), the
  mercury, cyanide and ether of historic processes (history only, never without expert training), UV light, nitrate
  film, and Poison Control. The old books also carry OLD_NOTE (out of date, history).

Already in the library and linked, not repeated: the Library of Congress's personal digital archiving guide
(pcb:loc_personal_digital_archiving) and its audio and video formats (media:loc_av_formats), the vision section
(vision:index) and audio description (describe:index), Photography Stack Exchange (se:index, Kiwix, reference only),
Wikibooks' photography books (in the Kiwix library wikibooks_en_all), the darkroom chemicals' safety data sheets
(manual collection photo_chemicals) and the camera manual collections (film_cameras_darkroom, digital_cameras).

Not built (NOT_INCLUDED, link-only): Adobe Lightroom and Photoshop help (Adobe's copyright), RawPedia (RawTherapee:
the site shuts out programs), Kodak publications of 1931-1963 (Kodak often renewed; no renewal check could be made),
the camera makers' manuals and Mike Butkus's library (links in the manual collections), the Smithsonian's care pages
(non-commercial terms), the describer apps' help pages, and others below.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build;
NPS's own statement checked on its disclaimer page), GPL-3.0 (darktable manual), GFDL 1.2 or later (GIMP manual),
public domain by age (published before 1931).

Run from the repository's folder:
  python3 textbooks/photography.py photo:loc_care_photographs --out build/textbooks --limit 3
  python3 textbooks/photography.py --list photography
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker
from old_ia_books import old_book  # noqa: E402

GROUP = "photography"
GROUPS = {GROUP: "Reference, photography"}

# The safety notice every book carries (the picture packs say the same things in packs/photography_packs.py).
PHOTO_SAFETY = ("Safety: darkroom chemicals: work with good ventilation, wear nitrile gloves and eye protection, never "
                "mix photographic chemicals except as their instructions say, keep them labelled and away from food, "
                "children and pets, and take used fixer (it carries silver) and other used solutions to a collection "
                "site as local rules say; read each product's safety data sheet. Historic processes used mercury "
                "(daguerreotypes), potassium cyanide and ether (wet collodion) and other poisons: they are history "
                "only; never attempt them without expert training and proper equipment. Alternative processes "
                "(cyanotype, platinum, gum) are exposed in sunlight or under UV lamps: protect your eyes and skin. "
                "Old film on cellulose nitrate base burns fiercely: store it apart and ask a conservator. In a "
                "poisoning call Poison Control at 1-800-222-1222, or 911 in an emergency.")
OLD_NOTE = ("Out of date: written for the plates, papers, chemicals and cameras of its day; read it as history and "
            "follow today's makers' instructions and safety data sheets.")

# ====================================================================== military and government manuals

MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "military photographers: its equipment and procedures are military ones and may be old. ")


def _mil(name, title, subject, publisher, archive, published, description, **more):
    """One military photography manual of the Internet Archive as a PDF entry, judged by the release rule
    (military=True: the builder reads its front pages); read whole."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description, notice=MIL_NOTICE + PHOTO_SAFETY, military=True, **more)


NAVY = "Naval Education and Training Command, US Navy"
ARMY = "Headquarters, Department of the Army"
AIR_CORPS = "War Department (US Army Air Corps)"
PDFS = [
    _mil("navy_navedtra_14209_photography_basic", "Photography (Basic), NAVEDTRA 14209 (US Navy, 1993)",
         "Photography basics: cameras, exposure, film and darkroom", NAVY, "photo1_202104", "1993",
         "The Navy's basic photography course, whole: the history of photography, light and optics, lenses and "
         "focus, cameras (view, press, medium format, 35 mm), exposure (aperture, shutter speed, film speed, light "
         "meters and the exposure triangle), filters, composition, lighting and flash, black-and-white and colour "
         "film and paper, chemistry and processing in the darkroom, printing, finishing and copying."),
    _mil("navy_navedtra_14208_photography_advanced", "Photography (Advanced), NAVEDTRA 14208 (US Navy, 1995)",
         "Photojournalism, quality assurance, electronic imaging and aerial photography", NAVY, "photo2_202104",
         "1995",
         "The Navy's advanced photography course, whole: basic photojournalism (news pictures and captions), "
         "photographic quality assurance (densitometry and process control), electronic (digital) imaging, aerial "
         "photography, and supply and logistics for a photo lab."),
    _mil("navy_ph_training_series_module_3_1983", "Navy Photographer's Mate Training Series, Module 3: Laboratory "
         "Procedures, Processing and Printing B&W and Color Materials (NAVEDTRA 373-03-45-83, 1983)",
         "Darkroom processing and printing", NAVY, "navyphotographer021736mbp", "1983",
         "Module 3 of the Navy's photographer's mate series, whole: chemical mixing, black-and-white film and paper "
         "processing, contact and projection printing, finishing negatives and prints, processing and printing "
         "colour negative and positive materials, processing machines, care of laboratory equipment, and running a "
         "photo stockroom."),
    _mil("navy_ph_training_series_module_4_1983", "Navy Photographer's Mate Training Series, Module 4: Audiovisual "
         "Productions, Quality Assurance and Specialized Photography (NAVEDTRA 373-04-67-83, 1983)",
         "Audiovisual production and specialised photography", NAVY, "navyphotographer021737mbp", "1983",
         "Module 4 of the Navy's photographer's mate series, whole: audiovisual productions (planning, scripts, "
         "slide, motion picture and multi-image shows), photographic quality assurance, aerial reconnaissance "
         "photography, and specialised photography (underwater, cold and tropical weather, periscope and screen "
         "photography)."),
    _mil("navy_photographers_mate_1_c_1974", "Photographer's Mate 1 & C, Rate Training Manual (NAVEDTRA 10375-C, "
         "1974)", "Portraits, aerial and underwater photography", "Naval Training Command, US Navy",
         "micro_IA41153155_0671", "1974",
         "The Navy's rate training manual for first class and chief photographer's mates (the ERIC copy), whole: "
         "portraiture, quality assurance, machine processing, motion picture equipment and technique, aerial "
         "cameras and missions, and underwater photography."),
    _mil("army_tm_11_401_2_still_photography_1969", "Army Pictorial Techniques, Equipments and Systems: Still "
         "Photography (TM 11-401-2, 1969)", "Still photography technique", ARMY, "TM11-401-2", "1969",
         "The Army's still photography manual, whole: photographic controls (exposure, composition, perspective, "
         "swing and tilt, filters, film), portraits and groups, copy photography, photographing equipment, legal "
         "and panoramic photography, poor light and action, infrared, flash, colour photography and instant "
         "(diffusion transfer) photography."),
    _mil("air_corps_tm_1_219_basic_photography_1941", "Basic Photography (TM 1-219, US Army Air Corps, 1941)",
         "Photography basics (1941)", AIR_CORPS, "TM1-219", "1941",
         "The Air Corps' basic photography manual of 1941, whole: light and lenses, cameras and shutters, "
         "sensitive materials, exposure, developing negatives, printing and enlarging, and the darkroom."),
    _mil("air_corps_tm_1_220_aerial_photography_1941", "Aerial Photography (TM 1-220, US Army Air Corps, 1941)",
         "Aerial photography (1941)", AIR_CORPS, "TM1-220", "1941",
         "The Air Corps' aerial photography manual of 1941, whole: aerial cameras and mounts, flying for vertical "
         "and oblique pictures, mosaics, processing aerial film and the uses of aerial photographs."),
    _mil("air_corps_fm_1_35_aerial_photography_1941", "Aerial Photography (FM 1-35, Air Corps Field Manual, 1941)",
         "Aerial photography (1941)", AIR_CORPS, "Fm1-35", "1941",
         "The Air Corps field manual on aerial photography, whole: the organisation of photographic units, aerial "
         "photographic missions, cameras, and the use of the pictures."),
    _mil("army_fm_30_21_role_of_aerial_photography_1940", "Military Intelligence: Role of Aerial Photography "
         "(FM 30-21, 1940)", "Aerial photographs and their reading (1940)", ARMY, "FM_30_21_M_I_R_A_P_1940", "1940",
         "The Army's 1940 field manual on aerial photographs as a source of information, whole: kinds of aerial "
         "photographs, how they are taken and distributed, and reading them (scale, stereo viewing, identifying "
         "what is seen)."),
]

# FADGI (digitizationguidelines.gov, the federal agencies' digitising guidelines; the newest technical guidelines PDF)
FADGI = "https://www.digitizationguidelines.gov/guidelines/digitize-technical.html"
PDFS.append(K.us_pdf(
    GROUP, name="fadgi_technical_guidelines", title="Technical Guidelines for Digitizing Cultural Heritage Materials "
    "(FADGI, third edition)", subject="Digitising photographs and documents",
    publisher="Federal Agencies Digital Guidelines Initiative (Library of Congress, National Archives and other "
              "federal agencies)", page=FADGI, pdf_pattern=r"FADGITechnicalGuidelines[^/]*\.pdf$",
    version="the newest edition linked from digitizationguidelines.gov (the third edition, May 2023, when checked)",
    published="2023-05",
    description="The federal agencies' digitising guidelines, whole: the FADGI star quality levels, image "
                "parameters (resolution, tone and colour, noise), targets and measurement, file formats and "
                "metadata, and the recommendations for each kind of original: photographic prints, negatives and "
                "transparencies, books, manuscripts, maps and art.",
    notice=f"From the Federal Agencies Digital Guidelines Initiative: a work of the US government (public domain). "
           f"{PHOTO_SAFETY}"))

# NPS Conserve O Gram leaflets (series 14, photographs) and the Museum Handbook appendices, each a PDF.
NPS = "https://www.nps.gov"
NPS_TERMS = NPS + "/aboutus/disclaimer.htm"
NPS_TEXT = r"material created by the National Park Service and presented on this website, unless otherwise " \
           r"indicated, is generally considered in the public domain"
NPS_NOTICE = ("From the National Park Service: \"material created by the National Park Service ... is generally "
              "considered in the public domain\"; source: National Park Service (nps.gov). ")
COG_PAGE = NPS + "/subjects/museums/conserve-o-grams.htm"
COG = [("14-01", "Making Mounting Corners for Photographs and Paper Objects"),
       ("14-02", "Storage Enclosures for Photographic Prints and Negatives"),
       ("14-03", "Chronology of Photographic Processes"),
       ("14-04", "Caring for Photographs: General Guidelines"),
       ("14-05", "Caring for Photographs: Special Formats"),
       ("14-06", "Caring for Color Photographs"),
       ("14-07", "Caring for Photographs: Special Monochrome Processes"),
       ("14-09", "Identification of Film-Base Photographic Materials"),
       ("14-10", "Cold Storage for Photograph Collections: An Overview"),
       ("14-11", "Cold Storage for Photograph Collections: Using Individual Freezer Units"),
       ("14-12", "Cold Storage for Photograph Collections: Vapor-Proof Packaging")]


def nps_pdf(name, title, subject, pdf, description, page=COG_PAGE):
    """One NPS PDF (a Conserve O Gram or a Museum Handbook appendix), NPS's statement checked at every build."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher="National Park Service (Museum "
                    "Management Program)", pdf=pdf, page=page, licence_page=NPS_TERMS, licence_text=NPS_TEXT,
                    version=f"the PDF on nps.gov ({pdf.rsplit('/', 1)[-1]})", description=description,
                    notice=NPS_NOTICE + PHOTO_SAFETY)


for number, cog_title in COG:
    PDFS.append(nps_pdf(f"nps_cog_{number.replace('-', '_')}", f"{cog_title} (NPS Conserve O Gram {number})",
                        "Caring for photographs", f"{NPS}/subjects/museums/upload/{number}_508.pdf",
                        f"The National Park Service's Conserve O Gram {number}, whole: {cog_title.lower()}, for "
                        f"museum staff and anyone keeping old photographs."))
MH = NPS + "/subjects/museums/mh1.htm"
PDFS += [
    nps_pdf("nps_museum_handbook_appendix_r_photographs", "Curatorial Care of Photographic Collections (NPS Museum "
            "Handbook, Part I, Appendix R)", "Caring for photographic collections",
            NPS + "/subjects/museums/upload/MHI_AppR_PhotographicColl.pdf",
            "The NPS Museum Handbook's appendix on photographs, whole: the structure of photographs, identifying "
            "processes (daguerreotypes, ambrotypes, tintypes, albumen and silver gelatin prints, negatives, colour "
            "materials), how they deteriorate, the storage environment, enclosures, handling, exhibition and cold "
            "storage.", page=MH),
    nps_pdf("nps_museum_handbook_appendix_m_nitrate_film", "Management of Cellulose Nitrate and Cellulose Ester "
            "Film (NPS Museum Handbook, Part I, Appendix M)", "Nitrate and acetate film",
            NPS + "/subjects/museums/upload/MHI_AppM_CelluloseNitrate.pdf",
            "The NPS Museum Handbook's appendix on nitrate and acetate (ester) film, whole: identifying nitrate "
            "film, its fire and health hazards, deterioration, inspection, cold storage, copying and duplicating, "
            "and safe disposal.", page=MH),
]

# ====================================================================== web guides (US government)

LOC_FDD = "https://www.loc.gov/preservation/digital/formats/fdd/"
LOC_CARE = "https://www.loc.gov/preservation/care/"
NARA = "https://www.archives.gov/preservation/"
GUIDES = [
    K.guide(GROUP, "loc_still_image_formats", "Still image formats for keeping photographs (Library of Congress)",
            "Image file formats and preservation", "Library of Congress (Sustainability of Digital Formats)",
            LOC_FDD + "still_fdd.shtml",
            r"^https://www\.loc\.gov/preservation/digital/formats/fdd/fdd\d{6}\.shtml$",
            "The Library of Congress's descriptions of the still image formats: TIFF, JPEG and JPEG 2000, PNG, GIF, "
            "WebP and HEIF, DNG and the camera raw formats, PDF images and many more; what each holds, how open and "
            "widely used it is, and what it means for keeping photographs for the long term.",
            f"From the Library of Congress: a work of the US government (public domain); source: Sustainability of "
            f"Digital Formats, Library of Congress (loc.gov/preservation/digital/formats). {PHOTO_SAFETY}", depth=1,
            content=(r'<div class="fdd">', r'<div align="right" class="update">'), limit=260,
            units=[(r".", "Format descriptions")]),
    X.page_list_book(GROUP, "loc_care_photographs", "Caring for photographs, albums and collections (Library of "
                     "Congress)", "Caring for photographs", "Library of Congress (Preservation Directorate)",
                     [LOC_CARE + p for p in ("photo.html", "albums.html", "light.html", "scan.html")],
                     r"^https://www\.loc\.gov/preservation/care/(photo|albums|light|scan)\.html$",
                     "The Library of Congress's collections care pages: identifying photographs and their processes, "
                     "handling, storing and housing prints, negatives and slides, scrapbooks and albums, limiting "
                     "light damage on display, and digitising collections.",
                     f"From the Library of Congress: a work of the US government (public domain). {PHOTO_SAFETY}",
                     units=[(r"photo", "Photographs"), (r"albums", "Scrapbooks and albums"),
                            (r"light", "Light damage"), (r".", "Digitising")],
                     content=(r'<div id="main_body"', r'<div id="footer"')),
    X.page_list_book(GROUP, "nara_preserving_photographs", "Preserving photographs, negatives and family archives "
                     "(National Archives)", "Preserving photographs", "National Archives and Records Administration",
                     [NARA + p for p in ("holdings-maintenance/photographs", "holdings-maintenance/film-based",
                                         "holdings-maintenance/cold-storage", "family-archives/",
                                         "family-archives/handling.html", "family-archives/storing.html",
                                         "family-archives/displaying.html", "family-archives/digitizing.html",
                                         "family-archives/repairing.html", "family-archives/mold-insects.html")],
                     r"^https://www\.archives\.gov/preservation/(holdings-maintenance/(photographs|film-based|"
                     r"cold-storage)|family-archives/([a-z-]+\.html)?)$",
                     "The National Archives' preservation pages: handling and housing photographs and the many "
                     "processes in its holdings, film-based negatives and transparencies (nitrate, acetate and "
                     "polyester), cold storage, and its family archives pages on handling, storing, displaying, "
                     "digitising and repairing family papers and photographs and dealing with mould and insects.",
                     f"From the National Archives: a work of the US government (public domain). {PHOTO_SAFETY}",
                     units=[(r"holdings", "Photographs and film"), (r".", "Family archives")],
                     content=(r'<div id="main-col" class="col-sm-10">', r'<div class="region region-footer')),
    dict(X.page_list_book(GROUP, "nps_nitrate_film_care", "Nitrate film: care, handling, shipping and disposal "
                          "(NPS Conserve O Grams)", "Nitrate film", "National Park Service (Museum Management "
                          "Program)",
                          [NPS + "/articles/000/cog-14-8-nitrate-film-care.htm",
                           NPS + "/articles/000/conserve-o-gram-20-2-handling-shipping-cellulose-nitrate.htm",
                           NPS + "/subjects/museums/conserve-o-gram-2-22-disposal-of-cellulose-nitrate-film.htm",
                           NPS + "/subjects/museums/conserve-o-gram-19-11-preservation-reformatting-selecting-a-copy-"
                                 "technology.htm"],
                          r"^https://www\.nps\.gov/(articles/000|subjects/museums)/[a-z0-9-]+\.htm$",
                          "The National Park Service's Conserve O Grams on cellulose nitrate film: caring for it, "
                          "handling and shipping it (it is a hazardous material), disposing of it, and choosing a "
                          "copying technology for fragile originals.", NPS_NOTICE + PHOTO_SAFETY,
                          content=(r'<div id="main" role="main" class="MainContent">',
                                   r'<div id="related_content_position">|<footer\b'),
                          units=[(r".", "Nitrate film")]),
         licence_page=NPS_TERMS, licence_text=NPS_TEXT),
]

# ====================================================================== editing manuals (share-alike)

DARKTABLE = "https://docs.darktable.org/usermanual/stable/en/"
GIMP = "https://docs.gimp.org/3.0/en/"
EDIT_NOTE = ("darktable and GIMP are mouse-driven programs that screen readers can use only in part: this book is for "
             "learning their words and ideas, and for sighted helpers.")
GUIDES += [
    dict(K.WEB, group=GROUP, name="darktable_user_manual", title="darktable user manual (raw photo editing)",
         subject="Raw photo editing (darktable)", publisher="The darktable project", country="International",
         licence="GPL-3.0", licence_url="https://www.gnu.org/licenses/gpl-3.0.html", licence_page=DARKTABLE,
         licence_text=r"This documentation is released under the GPL 3\.0 license", source=DARKTABLE,
         crawl=[(DARKTABLE, 2)], pages=r"^https://docs\.darktable\.org/usermanual/(stable|\d+\.\d+)/en/(?!contributing/)[a-z0-9/_-]+/$",
         content=(r"<main\b[^>]*>", r"</main>"), limit=700,
         unit_rules=[(r"/en/overview/", "Overview"), (r"/en/lighttable/", "Lighttable"),
                     (r"/en/darkroom/", "Darkroom"), (r"/en/module-reference/", "Module reference"),
                     (r"/en/preferences-settings/", "Preferences"), (r".", "Other parts")],
         description="The darktable user manual, every page: importing and organising photos (the lighttable, tags, "
                     "ratings and collections), the darkroom (scene-referred editing, exposure, filmic and sigmoid "
                     "tone mapping, colour calibration and white balance, denoising, cropping, masks), every "
                     "processing module, exporting, the other views (map, slideshow, print, tethering), preferences "
                     "and keyboard shortcuts. " + EDIT_NOTE,
         notice=f"The darktable user manual (docs.darktable.org), by the darktable project, released under the GNU "
                f"General Public License version 3: share-alike, so anything made from it keeps the same licence. "
                f"Screenshots are left out. {PHOTO_SAFETY}"),
    dict(K.WEB, group=GROUP, name="gimp_user_manual", title="GIMP 3.0 user manual (image editing)",
         subject="Image editing (GIMP)", publisher="The GIMP Documentation Team", country="International",
         licence="GFDL 1.2 or later", licence_url="https://www.gnu.org/licenses/old-licenses/fdl-1.2.html",
         licence_page=GIMP + "index.html",
         licence_text=r"GNU Free Documentation License, Version 1\.2 or any later version", source=GIMP + "index.html",
         crawl=[(GIMP + "index.html", 2)], pages=r"^https://docs\.gimp\.org/3\.0/en/[A-Za-z0-9_.-]+\.html$",
         content=(r"<body\b[^>]*>", r"</body>"),
         drop=K.DROP + [r'<div class="navheader">.*?</div>', r'<div class="navfooter">.*?</div>'], limit=1500,
         unit_rules=[(r"/en/gimp-(tool|tools)", "Tools"), (r"/en/(filters|plug-in|gimp-filter)", "Filters"),
                     (r"/en/gimp-(image|layer|edit|select|view|file|colors?)-", "Menus"),
                     (r"/en/gimp-(tutorial|using)", "Using GIMP"), (r".", "The manual")],
         description="The GIMP 3.0 user manual, every page: getting started, the image window, layers, selections, "
                     "paths, colours and colour management, painting, the tools, the filters, every menu, "
                     "preferences, keyboard shortcuts and the glossary. " + EDIT_NOTE,
         notice=f"The GIMP User Manual, copyright (c) 2002-2026 The GIMP Documentation Team: \"Permission is granted "
                f"to copy, distribute and/or modify this document under the terms of the GNU Free Documentation "
                f"License, Version 1.2 or any later version ... with no Invariant Sections, no Front-Cover Texts, "
                f"and no Back-Cover Texts\" (share-alike). Screenshots are left out. {PHOTO_SAFETY}",
         changes="the manual's pages made into web pages, with the navigation bars and screenshots left out"),
]
ALLOWED = {"GFDL": "share-alike", "GPL-3.0": "share-alike"}

# ====================================================================== old public-domain books (before 1931)

HISTORY = "Historic processes (history only)"


def _old(name, title, subject, publisher, archive, year, description, history=False):
    """One old public-domain photography book (published before 1931), with the out-of-date note and the safety
    notice; history=True for a book on the old processes (mercury, cyanide), said to be history only."""
    note = OLD_NOTE + (" HISTORY ONLY: its processes used mercury, cyanide, ether or other poisons; never attempt "
                       "them without expert training." if history else "")
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=PHOTO_SAFETY)


KODAK = "Eastman Kodak Company, Rochester, N.Y."
OLD = [
    _old("kodak_how_to_make_good_pictures_1920", "How to Make Good Pictures: a book for the amateur photographer "
         "(Eastman Kodak, 1920)", "Taking pictures with a film camera", KODAK, "howtomakegoodpic00east_1", 1920,
         "Kodak's handbook for amateurs: loading film, holding the camera, focusing, exposure in sun and shade, "
         "portraits, landscapes, flash and interiors, developing (tank and tray), printing and enlarging."),
    _old("kodak_picture_taking_and_making_1898", "Picture Taking and Picture Making (Eastman Kodak, 1898)",
         "Taking and printing pictures (1898)", KODAK, "picturetakingpic00eastuoft", 1898,
         "Kodak's early guide to taking pictures and making prints with its cameras and papers."),
    _old("kodak_elementary_photographic_chemistry_1924", "Elementary Photographic Chemistry (Eastman Kodak, 1924)",
         "Darkroom chemistry", KODAK, "elementaryphotog00east", 1924,
         "Kodak's plain explanation of the chemistry of photography: the sensitive emulsion, developers and how "
         "they work, stop baths, fixing, washing, intensifying and reducing, toning, and mixing solutions."),
    _old("kodak_bulls_eye_camera_instructions_1895", "Instructions for Using the Bulls-Eye Camera (Eastman Kodak, "
         "1895)", "Historic camera instruction books", KODAK, "instructionsforu00east", 1895,
         "Kodak's instruction book for the Bulls-Eye box camera: loading the roll film, taking pictures, time "
         "exposures and unloading."),
    _old("kodak_no_4a_folding_kodak_1906", "Picture Taking with the No. 4A Folding Kodak (Eastman Kodak, 1906)",
         "Historic camera instruction books", KODAK, "picturetakingwit00east", 1906,
         "Kodak's instruction book for the No. 4A Folding Kodak: opening the camera, the finder, focusing scale, "
         "shutter and stops, loading film, time and instantaneous exposures, and closing it."),
    _old("mees_fundamentals_of_photography_1920", "The Fundamentals of Photography (C. E. Kenneth Mees, 1920)",
         "How photography works", "Eastman Kodak Company", "fundamentalsofph00mees", 1920,
         "Mees's clear account of how photography works: light and lenses, the camera, the sensitive emulsion, "
         "exposure, development, printing, colour sensitivity and filters, and colour photography."),
    _old("neblette_photography_principles_practice_1927", "Photography: its principles and practice (C. B. "
         "Neblette, 1927)", "Photography textbook (1927)", "D. Van Nostrand Company, New York",
         "photographyitspr00nebl", 1927,
         "A college textbook of photography: optics and lenses, cameras and shutters, sensitive materials, "
         "exposure, development, printing processes, enlarging, colour, and applied photography."),
    _old("abney_instruction_in_photography_1900", "Instruction in Photography (W. de W. Abney, 1900 edition)",
         "Photography handbook (1900)", "Sampson Low, Marston and Company, London", "instructioninpho00abnerich",
         1900, "Abney's long-running handbook: lenses, cameras, plates and films, exposure, development, printing "
               "processes, enlarging and lantern slides."),
    _old("hasluck_book_of_photography_1905", "The Book of Photography: practical, theoretic and applied (Paul N. "
         "Hasluck, 1905)", "Photography handbook (1905)", "Cassell and Company, London", "bookofphotograph00hasluoft",
         1905, "Hasluck's large handbook of photography in practice, theory and its applications."),
    _old("hasluck_photographic_cameras_accessories_1902", "Photographic Cameras and Accessories (Paul N. Hasluck, "
         "1902)", "Cameras and how they were made", "Cassell and Company, London", "photographiccame00hasluoft", 1902,
         "How to make cameras, dark slides, shutters and stands, with many engravings and diagrams: the parts of a "
         "camera explained by building them."),
    _old("cassells_cyclopaedia_of_photography_1911", "Cassell's Cyclopaedia of Photography (Bernard E. Jones, ed., "
         "1911)", "Photography encyclopaedia (1911)", "Cassell and Company, London and New York",
         "cassellscyclopae00jone", 1911, "An encyclopaedia of photography in alphabetical entries: processes, "
                                        "apparatus, chemicals, terms and methods of its day."),
    _old("wall_dictionary_of_photography_1897", "The Dictionary of Photography (E. J. Wall, 1897)",
         "Photography dictionary (1897)", "Hazell, Watson and Viney, London", "dictionaryofphot00wall_2", 1897,
         "Wall's dictionary of photographic terms, processes, formulas and apparatus for amateurs and "
         "professionals."),
    _old("british_journal_photographic_almanac_1915", "The British Journal Photographic Almanac and Photographer's "
         "Daily Companion (1915)", "Photographic almanac (1915)", "Henry Greenwood and Co., London (George E. Brown, "
         "editor)", "in.ernet.dli.2015.93598", 1915,
         "The yearly almanac of the British Journal of Photography: articles on methods, the epitome of progress, "
         "formulas and tables (exposure, chemicals, lenses) and the year's apparatus."),
    _old("roche_anthony_how_to_make_photographs_1883", "How to Make Photographs: a manual for amateurs (T. C. "
         "Roche, ed. H. T. Anthony, 1883)", "Dry plate photography (1883)", "E. and H. T. Anthony and Co., New York",
         "howtomakephotogr00roch", 1883,
         "Anthony's manual for amateurs of the dry plate era: the camera and lens, exposing, developing and "
         "printing."),
    _old("watkins_manual_exposure_development_1919", "Photography: the Watkins Manual of Exposure and Development "
         "(Alfred Watkins, 1919)", "Exposure without a meter", "Burke and James, Chicago", "photographywatk00watkgoog",
         1919, "Watkins's manual of judging exposure from the light, the subject and the plate's speed, and of "
               "timing development by the factor method: exposure without an electric meter."),
    _old("bayley_photographic_enlarging_1910", "Photographic Enlarging: a handbook for amateur photographers (R. "
         "Child Bayley, 1910)", "Enlarging in the darkroom", "Iliffe and Sons, London", "gri_33125001604848", 1910,
         "Enlarging negatives onto bromide paper: enlargers and their light sources, focusing, exposure, "
         "development and finishing."),
    _old("taylor_optics_of_photography_1904", "The Optics of Photography and Photographic Lenses (J. Traill Taylor, "
         "1904 edition)", "Lenses", "Whittaker and Co., London and New York", "opticsofphotogra00taylrich", 1904,
         "How photographic lenses work: refraction, focal length, aperture and f-numbers, depth of field, lens "
         "faults and the kinds of lens."),
    _old("hodges_photographic_lenses_1895", "Photographic Lenses: how to choose, and how to use (John A. Hodges, "
         "1895)", "Lenses", "Percy Lund and Co., Bradford", "photographiclens00hodg", 1895,
         "A practical guide to choosing and using photographic lenses: kinds of lens, focal length, stops, depth of "
         "field and testing a lens."),
    # historic and alternative processes (history only)
    _old("snelling_history_practice_photography_1850", "The History and Practice of the Art of Photography (Henry "
         "H. Snelling, 1850)", HISTORY, "G. P. Putnam, New York", "historypracticeo00snel_1", 1850,
         "One of the first American photography books: the history of the invention and full instructions for the "
         "daguerreotype and the early paper processes.", history=True),
    _old("hardwich_photographic_chemistry_collodion_1857", "A Manual of Photographic Chemistry, including the "
         "Practice of the Collodion Process (T. F. Hardwich, 1857)", HISTORY, "John Churchill, London",
         "amanualphotogra02hardgoog", 1857,
         "Hardwich's manual of the chemistry of the wet collodion process: making negatives and positives on "
         "glass, silver printing on salted and albumen paper.", history=True),
    _old("humphrey_collodion_process_1857", "A Practical Manual of the Collodion Process: ambrotypes and positive "
         "and negative pictures (S. D. Humphrey, 1857)", HISTORY, "Humphrey's Journal, New York",
         "practicalmanualo00humprich", 1857,
         "Humphrey's American manual of the collodion process: ambrotypes, negatives on glass and paper prints.",
         history=True),
    _old("coale_albumen_process_1858", "Manual of Photography adapted to amateur practice: Whipple's albumen "
         "process (George B. Coale, 1858)", HISTORY, "J. B. Lippincott, Philadelphia", "manualofphotogra00coal",
         1858, "An amateur's manual of the albumen-on-glass process of the 1850s.", history=True),
    _old("towler_silver_sunbeam_1864", "The Silver Sunbeam: a practical and theoretical text-book on sun drawing "
         "and photographic printing (John Towler, 1864)", HISTORY, "J. H. Ladd, New York",
         "silversunbeampra00towluoft", 1864,
         "Towler's famous textbook of the wet and dry collodion processes, ambrotypes, tintypes and silver "
         "printing.", history=True),
    _old("burbank_photographic_printing_methods_1891", "Photographic Printing Methods (W. H. Burbank, 1891)",
         "Alternative printing processes", "Scovill and Adams, New York", "photographicprin00burbuoft", 1891,
         "Burbank's guide to the printing processes of 1891: silver (salted and albumen), platinum, cyanotype (blue "
         "print), carbon, and bromide and chloride papers.", history=True),
    _old("maclean_popular_printing_processes_1898", "Popular Photographic Printing Processes (Hector Maclean, "
         "1898)", "Alternative printing processes", "L. Upcott Gill, London", "popularphotograp00macl", 1898,
         "A practical guide to printing with gelatino-chloride, platinotype, carbon, bromide, collodio-chloride "
         "and other papers of 1898.", history=True),
    _old("bolte_carbon_printing_1897", "Carbon Printing (Max Bolte, 1897)", "Alternative printing processes",
         "E. and H. T. Anthony and Co., New York", "carbonprintingco00bolt", 1897,
         "Instructions for the carbon (pigment) printing process.", history=True),
    _old("platinotype_simplest_process_1916", "The Platinotype: simplest photographic process producing highest "
         "quality prints (1916)", "Alternative printing processes", "Willis and Clements, Philadelphia",
         "platinotypesimpl00phil", 1916, "Willis and Clements's instructions for platinum printing.", history=True),
    # history
    _old("tissandier_history_handbook_photography_1877", "A History and Handbook of Photography (Gaston Tissandier, "
         "1877 English edition)", "History of photography", "Sampson Low, London", "historyhandbooko00tissuoft", 1877,
         "Tissandier's history of photography from the camera obscura to the 1870s, with a handbook of the "
         "processes of the time.", history=True),
    _old("werge_evolution_of_photography_1890", "The Evolution of Photography (John Werge, 1890)",
         "History of photography", "Piper and Carter, London", "evolutionofphoto00werguoft", 1890,
         "A photographer's history of photography from 1839, with a chronology of discoveries and inventions and "
         "his own memories of the early processes.", history=True),
    _old("brothers_photography_history_processes_1899", "Photography: its history, processes, apparatus and "
         "materials (A. Brothers, 1899 edition)", "History of photography", "Charles Griffin and Co., London",
         "photographyitshi00brotuoft", 1899,
         "Brothers's history of photography and working details of the important processes, apparatus and "
         "materials up to 1899.", history=True),
]
PDFS += OLD

# ====================================================================== the index

SUNNY_16 = ("Exposure without a meter (the sunny 16 rule): in bright sun, set the aperture to f/16 and the shutter "
            "speed to 1 over the film's ISO (for ISO 100 film, 1/100 or 1/125 second); open up one stop (f/11) for "
            "slight overcast, two (f/8) for overcast, three (f/5.6) for heavy overcast and four (f/4) for open "
            "shade or sunset.")
SECTIONS = [
    ("Cameras and their controls", "The exposure triangle: aperture (the f-number: a smaller number lets in more "
     "light and gives less depth of field), shutter speed (a faster speed stops motion), and ISO (film speed or "
     "sensor gain: higher is brighter but grainier). White balance, focus and metering modes are explained in the "
     "Navy and Army manuals and in the camera's own manual.", [
        ("key", "photo:navy_navedtra_14209_photography_basic", "Photography (Basic): cameras, exposure and the "
                                                               "exposure triangle"),
        ("key", "photo:army_tm_11_401_2_still_photography_1969", "Still photography: controls, filters and film"),
        ("key", "photo:mees_fundamentals_of_photography_1920", "How photography works (Mees)"),
        ("key", "se:index", "Photography Stack Exchange (in the Kiwix library; reference only)"),
        ("link", "Wikibooks: Basic Photography and Digital Photography", "https://en.wikibooks.org/wiki/"
         "Basic_Photography", "CC BY-SA, already in the Kiwix library (wikibooks_en_all); not built again"),
        ("manuals", "digital_cameras", "Digital camera manuals (makers' pages as links)"),
        ("manuals", "film_cameras_darkroom", "Film camera manuals, light meters and flash units")]),
    ("Lenses, composition and lighting", "Focal length, depth of field, filters, flash and studio light.", [
        ("key", "photo:taylor_optics_of_photography_1904", "The optics of photographic lenses"),
        ("key", "photo:hodges_photographic_lenses_1895", "Choosing and using lenses"),
        ("key", "photo:navy_navedtra_14209_photography_basic", "Composition, lighting and flash (Navy)"),
        ("pack", "commons_lenses_lighting", "Lenses, filters, light meters, flashes and tripods"),
        ("pack", "open_images_photography", "Cameras, lenses and accessories in everyday photos")]),
    ("Phone photography, and photography for blind and low-vision people", "Phone cameras, describer apps and "
     "tactile pictures. The toolkit's own picture describer and its packs are built for this.", [
        ("key", "vision:index", "Blind and low-vision living: a guide to the library"),
        ("key", "describe:index", "Describing pictures and video"),
        ("link", "Be My Eyes, Seeing AI and Aira (describer apps)", "https://www.bemyeyes.com/",
         "the companies' copyright and terms; open their help pages in a browser"),
        ("link", "Apple: use the Camera with VoiceOver on iPhone", "https://support.apple.com/guide/iphone/",
         "Apple's copyright; open it in a browser"),
        ("link", "Google Lookout and TalkBack help", "https://support.google.com/accessibility/android/",
         "Google's copyright; open it in a browser"),
        ("link", "Tactile graphics guidelines (Braille Authority of North America)", "https://www.brailleauthority.org/",
         "BANA's copyright; open it in a browser")]),
    ("Editing photos", "Raw developing and image editing.", [
        ("key", "photo:darktable_user_manual", "darktable user manual (GPL)"),
        ("key", "photo:gimp_user_manual", "GIMP 3.0 user manual (GFDL)"),
        ("link", "Adobe Lightroom help", "https://helpx.adobe.com/lightroom-cc/user-guide.html",
         "Adobe's copyright; link-only"),
        ("link", "Adobe Photoshop help", "https://helpx.adobe.com/photoshop/user-guide.html",
         "Adobe's copyright; link-only"),
        ("link", "RawPedia (RawTherapee)", "https://rawpedia.rawtherapee.com/", "the site shuts out programs; open "
                                                                              "it in a browser")]),
    ("File formats, RAW and keeping photos safe", "Formats for the long term, digitising and personal archiving.", [
        ("key", "photo:loc_still_image_formats", "Still image formats, camera raw and DNG (Library of Congress)"),
        ("key", "photo:fadgi_technical_guidelines", "Digitising photographs (FADGI)"),
        ("key", "pcb:loc_personal_digital_archiving", "Personal digital archiving: photos (Library of Congress)"),
        ("key", "media:loc_av_formats", "Sound and moving image formats (Library of Congress)"),
        ("key", "photo:nara_preserving_photographs", "Preserving photographs and family archives (National "
                                                     "Archives)")]),
    ("Printing", "Darkroom prints, enlarging and the old printing processes.", [
        ("key", "photo:bayley_photographic_enlarging_1910", "Enlarging"),
        ("key", "photo:navy_ph_training_series_module_3_1983", "Processing and printing black-and-white and colour "
                                                               "(Navy)")]),
    ("Film and film cameras", "Film types and formats (35 mm, 120, sheet film), and cameras of every era: box, "
     "folding, rangefinder, twin-lens reflex, SLR, medium and large format.", [
        ("key", "photo:kodak_how_to_make_good_pictures_1920", "How to Make Good Pictures (Kodak, 1920)"),
        ("key", "photo:hasluck_photographic_cameras_accessories_1902", "How cameras are made"),
        ("key", "photo:kodak_no_4a_folding_kodak_1906", "A folding camera's instruction book (1906)"),
        ("key", "photo:kodak_bulls_eye_camera_instructions_1895", "A box camera's instruction book (1895)"),
        ("manuals", "film_cameras_darkroom", "Film camera and darkroom manuals; Mike Butkus's library as a link"),
        ("pack", "commons_cameras_by_type", "Cameras by type"),
        ("pack", "commons_camera_makers", "Cameras by maker"),
        ("pack", "nmah_photography", "Cameras and photographic objects of the National Museum of American History")]),
    ("Exposure without a meter", SUNNY_16, [
        ("key", "photo:watkins_manual_exposure_development_1919", "Judging exposure from the light (Watkins, 1919)"),
        ("key", "photo:kodak_how_to_make_good_pictures_1920", "Exposure in sun and shade (Kodak)")]),
    ("Developing film and the darkroom", "Developing black-and-white and colour film, enlargers, safelights, "
     "chemicals and their safety.", [
        ("key", "photo:kodak_elementary_photographic_chemistry_1924", "Darkroom chemistry (Kodak, 1924)"),
        ("key", "photo:navy_ph_training_series_module_3_1983", "Laboratory procedures (Navy, 1983)"),
        ("key", "photo:air_corps_tm_1_219_basic_photography_1941", "Basic photography and the darkroom (1941)"),
        ("manuals", "photo_chemicals", "Photographic and darkroom chemicals: safety data sheets"),
        ("pack", "commons_film_darkroom", "Darkrooms, enlargers, safelights and film formats")]),
    ("Alternative and historic processes", "Daguerreotype, ambrotype, tintype, wet plate collodion, albumen, salt "
     "prints, cyanotype, platinum and palladium, gum bichromate and carbon: history only where mercury, cyanide or "
     "ether were used; protect eyes and skin from UV.", [
        ("key", "photo:snelling_history_practice_photography_1850", "The daguerreotype (Snelling, 1850)"),
        ("key", "photo:towler_silver_sunbeam_1864", "Wet collodion, ambrotypes and tintypes (Towler, 1864)"),
        ("key", "photo:hardwich_photographic_chemistry_collodion_1857", "Collodion chemistry (Hardwich, 1857)"),
        ("key", "photo:burbank_photographic_printing_methods_1891", "Salt, albumen, platinum, cyanotype and carbon "
                                                                    "printing"),
        ("key", "photo:platinotype_simplest_process_1916", "Platinum printing"),
        ("pack", "commons_historic_processes", "Historic photographic processes as objects")]),
    ("Caring for photographs", "Handling, enclosures, cold storage, nitrate film and identifying processes.", [
        ("key", "photo:nps_cog_14_03", "Chronology of photographic processes (NPS)"),
        ("key", "photo:nps_cog_14_04", "Caring for photographs (NPS)"),
        ("key", "photo:nps_museum_handbook_appendix_r_photographs", "Photographic collections (NPS Museum Handbook)"),
        ("key", "photo:nps_nitrate_film_care", "Nitrate film (NPS)"),
        ("key", "photo:loc_care_photographs", "Caring for photographs and albums (Library of Congress)"),
        ("link", "Smithsonian: caring for photographs", "https://www.si.edu/mci",
         "the Smithsonian's non-commercial terms; open it in a browser"),
        ("link", "Image Permanence Institute: Graphics Atlas", "http://www.graphicsatlas.org/",
         "the Institute's copyright; open it in a browser")]),
    ("History of photography", "From the camera obscura to the snapshot.", [
        ("key", "photo:tissandier_history_handbook_photography_1877", "Tissandier (1877)"),
        ("key", "photo:werge_evolution_of_photography_1890", "Werge (1890)"),
        ("key", "photo:brothers_photography_history_processes_1899", "Brothers (1899)")]),
    ("Military and government photography manuals", "Navy and Army manuals, read whole.", [
        ("key", "photo:navy_navedtra_14208_photography_advanced", "Photography (Advanced), Navy"),
        ("key", "photo:navy_ph_training_series_module_4_1983", "Audiovisual and specialised photography, Navy"),
        ("key", "photo:navy_photographers_mate_1_c_1974", "Photographer's Mate 1 & C, Navy"),
        ("key", "photo:air_corps_tm_1_220_aerial_photography_1941", "Aerial photography, Air Corps"),
        ("key", "photo:army_fm_30_21_role_of_aerial_photography_1940", "Aerial photographs, Army")]),
]
INDEX = X.index_maker("photo", GROUP, "Photography: a guide to the library", "Photography",
                      "A guide to photography in the library: cameras and their controls, lenses, phones and "
                      "photography for blind people, editing, formats and archiving, film, exposure without a meter, "
                      "the darkroom, historic processes, conservation and history.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("photo", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"photography": lambda: ["photo:index"] + [f"photo:{g['name']}"
                                                                           for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "photo_military": "The Navy and Army photography manuals: works of the US Navy, Army and Army Air Corps, read from "
                      "the Internet Archive; the builder reads each one's front pages and follows the shared "
                      "distribution rule (NAVEDTRA 14209 and 14208 print \"Distribution Statement A: Approved for "
                      "public release; distribution is unlimited\", checked 2026-11-22).",
    "photo_gov": "loc.gov, archives.gov and digitizationguidelines.gov: works of the US government (17 U.S.C. 105, "
                 "checked on govinfo.gov's policies page at every build); robots.txt allows the pages and has no AI "
                 "rules (checked 2026-11-22; digitizationguidelines.gov has no robots.txt).",
    "photo_nps": "www.nps.gov/aboutus/disclaimer.htm (checked at every build): NPS material \"is generally considered "
                 "in the public domain\", credited in the notice; NPS's robots.txt allows the pages.",
    "photo_editing": "docs.darktable.org (\"This documentation is released under the GPL 3.0 license\") and "
                     "docs.gimp.org (GNU Free Documentation License 1.2 or later, no invariant sections), both "
                     "checked at every build: share-alike, separate books; robots.txt allows the pages (checked "
                     "2026-11-22).",
    "photo_old": "Old books published before 1931 (the builder checks each Internet Archive item's year at every "
                 "build): public domain in the US.",
    "photo_index": "The index (photo:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Adobe Lightroom and Photoshop user guides", "Adobe's copyright; link-only from the index. Index: "
     "https://helpx.adobe.com/photoshop/user-guide.html"),
    ("RawPedia (RawTherapee documentation, CC BY-SA)", "The site answers programs with a bot challenge (\"One moment, "
     "please...\", checked 2026-11-22), so it is not read; link-only. Index: https://rawpedia.rawtherapee.com/"),
    ("Kodak publications of 1931-1963 (How to Make Good Pictures later editions, Kodak Data Books, the Kodak "
     "Reference Handbook)", "Kodak often renewed its copyrights, and the Stanford Copyright Renewal Database shuts "
     "out programs (checked 2026-11-22), so no evidence of non-renewal could be gathered: link-only for the owner. "
     "Index: https://exhibits.stanford.edu/copyrightrenewals"),
    ("Kodak No. 1A Autographic Kodak Junior manual (Internet Archive item kodak-1-a-jr, 1922)", "Public domain by age, "
     "but uploaded by a person with no word of where the scan came from (it may be a camera manual site's scan); "
     "left out. The Kodak instruction books of the Getty and Toronto scans are built. Index: "
     "https://archive.org/details/kodak-1-a-jr"),
    ("The gum-bichromate process (J. Cruwys Richards, London, Iliffe, 190-?)", "Its Internet Archive record gives no "
     "exact year (\"[190-?]\"), so the builder could not confirm it was published before 1931; not built. Index: "
     "https://archive.org/details/gumbichromatepro00rich"),
    ("Navy Photographer's Mate 3 & 2 (NAVPERS 10355-A, 1971) and Photographer's Mate 2 (1958, 1959)", "The Internet "
     "Archive's copies are lending-library scans (access restricted): not downloadable. Index: "
     "https://archive.org/details/photographersmat0000notg"),
    ("Camera makers' manuals and Mike Butkus's camera manual library", "The makers' copyright and Mr Butkus's own "
     "scans under his terms: links in the manual collections film_cameras_darkroom and digital_cameras. Index: "
     "https://www.orphancameras.com/"),
    ("Smithsonian care pages (Museum Conservation Institute) and the Smithsonian's photography guides", "The "
     "Smithsonian's website terms allow personal, educational and non-commercial use only (its Open Access images are "
     "CC0 and are in the picture packs); link-only. Index: https://www.si.edu/termsofuse"),
    ("Image Permanence Institute Graphics Atlas and the Northeast Document Conservation Center leaflets", "Their own "
     "copyright; link-only. Index: http://www.graphicsatlas.org/"),
    ("Describer apps' help pages (Be My Eyes, Seeing AI, Aira, Envision) and the phone makers' camera accessibility "
     "guides (Apple VoiceOver, Google Lookout and TalkBack)", "The companies' copyright; link-only from the index. "
     "Index: https://www.bemyeyes.com/"),
    ("NASA photography guides", "No NASA how-to-photograph guide was found as a whole document in this pass; NASA's "
     "image use guidelines are about rights, and NASA's pictures are in the picture packs (nasa_library_packs). "
     "Index: https://www.nasa.gov/nasa-brand-center/images-and-media/"),
    ("Wikibooks photography books (Basic Photography, Digital Photography, Photography/...)", "CC BY-SA, already in "
     "the Kiwix library (wikibooks_en_all); not built again. Index: https://en.wikibooks.org/wiki/Basic_Photography"),
    ("Science Museum Group and George Eastman Museum collections", "Non-commercial or their own terms; not built. "
     "Index: https://collection.sciencemuseumgroup.org.uk/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
