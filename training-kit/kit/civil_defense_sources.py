"""OLD CIVIL DEFENCE BOOKLETS AND FILMS that cannot be ready-made packs (the UK, Canada, Australia and New Zealand), and
the source-by-source record of what was looked at for the civil defence collections (November 2026). The open US
collections (US government works) are packs in packs/civil_defense_packs.py: cd_booklets and cd_films.

WHY THESE ARE NOT OPEN. They are Crown or Commonwealth works:
  - United Kingdom: Crown copyright in a published work lasts 50 years from the end of the year it was first
    published (Copyright, Designs and Patents Act 1988, section 163(3)(b); the older rule was the same). So the Home
    Office handbooks and manuals published in 1975 or before are out of copyright in the UK, while "Protect and
    Survive" (the booklet and films of 1980) stays in Crown copyright until the end of 2030, "Domestic Nuclear
    Shelters" (1981) until 2031 and "Civil Defence: Why We Need It" (1983) until 2033. The Open Government Licence does
    not cover them: the National Archives' terms say Crown copyright material on ITS website is under the OGL "unless
    otherwise indicated", and its copies of records may be used only "for private study or research for a
    non-commercial purpose" or education; its robots.txt also says "Content-Signal: ai-train=no".
  - Canada: Crown copyright lasts "for the remainder of the calendar year of the first publication of the work and for
    a period of fifty years following the end of that calendar year" (Copyright Act, section 12), so federal civil
    defence and Emergency Measures Organization booklets of 1975 or before are out of copyright in Canada; the
    Government of Canada lets anyone "reproduce the materials in whole or in part for non-commercial purposes ...
    without charge or further permission" (canada.ca terms).
  - Australia: Commonwealth copyright in a published work lasts 50 years from first publication (Copyright Act 1968,
    section 180, as changed in 2019), so the 1987 and 1989 civil defence handbooks stay in copyright until 2037 and
    2039.
  - New Zealand: Crown copyright lasts 100 years from the end of the year a work is made (Copyright Act 1994, section
    26), so the 1963 householders' handbook stays in copyright until 2063.
  - And in the United States, where this kit's packs are published: the copyright of foreign works that were still
    protected at home on 1 January 1996 was restored (17 U.S.C. 104A), for 95 years from publication; that covers
    every UK, Canadian, Australian and New Zealand civil defence work published after 1945. The Internet Archive
    uploaders' "public domain" marks on these copies are the uploaders' own and are not relied on.
So each is used only for the user's personal training, downloaded by the kit on the user's own computer from the
Internet Archive copy named below (one request at a time, three seconds apart, the kit's User-Agent), and never
re-shared:
  research (no licence is given: personal, non-commercial use only; Alt+Z after agreeing)
    cd_uk_booklets_research   UK Home Office civil defence handbooks, manuals and pocket books (1949 to 1963) and
                              the later public leaflets ("Protect and Survive", 1980; "Domestic Nuclear Shelters",
                              1981; "Civil Defence: Why We Need It", 1983): the pictures on their pages.
    cd_uk_films_research      UK government civil defence films: the twenty "Protect and Survive" public information
                              films (1980) and Home Office films of the 1950s and 1960s ("Rescue and Relief", 1964;
                              "The Warden and the Householder", 1961): stills.
    cd_aus_nz_research        Australia's "Nuclear Weapons: Their Effects and Your Protection" (1987) and "Domestic
                              Fallout Shelter Guide" (1989), and New Zealand's "Householders' Handbook for
                              Emergencies" (1963): the pictures on their pages.
  noncommercial (Alt+Q)
    cd_canada_nc              Canadian federal civil defence booklets of the 1950s and the Emergency Measures
                              Organization's "Blueprint for Survival" pamphlets (about 1959 to 1962), the University of
                              Toronto's copies: the pictures on their pages.

WHAT THE ANSWERS SAY. The booklets' pictures are found as in the packs (kit/civil_defense_figures.py). Every picture
gets "Where is this picture from?" with a fixed sentence from the item's record ("It is a drawing from a 1963 UK
Home Office civil defence handbook, 'Advising the Householder on Protection Against Nuclear Attack'."); a picture
with its own printed caption ("Fig. 4. An inner refuge") also gets "What does this picture show?" with that caption.
Film stills are made by the kit's video_frames.py (it reads only the parts of each film it needs; date stamps, logos
and frame lines near the edges are cropped off), title cards and blank frames are left out
(civil_defense_figures.still_problem), and each still gets "Where is this picture from?" with "A still from the
1980 UK government civil defence film 'Protect and Survive: Choosing a Fall-out Room'.". Nothing is guessed from a
picture.

SAFETY. As in the packs: rows whose words, or whose booklet or film, are about attack, bombs, blasts, casualties or
injuries carry "content": "graphic"; first-aid rows carry "content": "medical"; rows whose words name children or
schools carry "child": True. CIVIL_DEFENSE_PICTURE_MAKING_OK is empty: these show people, attack and injuries.

    python kit/civil_defense_sources.py --record                    (prints the source-by-source record)
    python kit/civil_defense_sources.py cd_canada_nc --cap 4        (a quick check; prints a few rows)
"""

import json
import os
import re
import shutil
import time
import urllib.parse

import civil_defense_figures as figures
from extra_sources import say
from sources import Source, USER_AGENT, smaller

PAUSE = 3.0                 # seconds before each request to the Internet Archive
ARCHIVE = "https://archive.org/"
FROM_Q = "Where is this picture from?"
DRAWING_Q = "What does this picture show?"
MOST_PER_ITEM = 40          # at most this many pictures from one booklet or film

UK_TERMS = "https://www.legislation.gov.uk/ukpga/1988/48/section/163"
CANADA_TERMS = "https://www.canada.ca/en/transparency/terms.html"
CANADA_LAW = "https://laws-lois.justice.gc.ca/eng/acts/c-42/page-3.html"
AUSTRALIA_LAW = "https://www.legislation.gov.au/C1968A00063/latest/text"
NZ_LAW = "https://www.legislation.govt.nz/act/public/1994/0143/latest/DLM345917.html"
URAA = "https://www.law.cornell.edu/uscode/text/17/104A"

# The items (Internet Archive identifier: (title as said in an answer, year or 0, what it is)). Checked by hand on
# 2026-11-18; each has a PDF (booklets) or an MP4 copy (films).
UK_BOOKLETS = {
    "CDHandbookNo3": ("Civil Defence Handbook No. 3", 1953, "handbook"),
    "CivilDefenceHandbookNo1WirelessInstructionsForCivilDefence": ("Wireless Instructions for Civil Defence", 0,
                                                                   "handbook"),
    "CivilDefenceHandbookNo7Rescue": ("Rescue", 1960, "handbook"),
    "CivilDefenceHandbookNo.10AdvisingTheHouseholderOnProtectionAgainst": (
        "Advising the Householder on Protection Against Nuclear Attack", 1963, "handbook"),
    "CivilDefenceManualOfBasicTrainingVolumeIIBasicFireFighting": ("Basic Fire Fighting", 1949, "manual"),
    "CivilDefenceManualOfBasicTrainingVolumeIIBasicFirstAid": ("Basic First Aid", 1949, "manual"),
    "CivilDefenceManualOfBasicTrainingVolumeIIBasicMethodsOfProtectionAgainstHighExplosiveMissiles": (
        "Basic Methods of Protection Against High Explosive Missiles", 1949, "manual"),
    "CivilDefenceManualOfBasicTrainingVolume1PrinciplesOfDamageControl": ("Principles of Damage Control", 1951,
                                                                          "manual"),
    "CivilDefenceManualOfBasicTrainingVolume1HeadquartersSection": ("Headquarters Section", 1953, "manual"),
    "CivilDefencePocketBookNo4WardenSection": ("Civil Defence Pocket Book No. 4: Warden Section", 0, "pocket book"),
    "civildefencepocketbookno3": ("Civil Defence Pocket Book No. 3", 1960, "pocket book"),
    "ManualOfCivilDefenceVol1Pamphlet1NuclearWeapons": ("Nuclear Weapons", 0, "manual"),
    "ProtectAndSurvive": ("Protect and Survive", 1980, "booklet"),
    "DomesticNuclearShelters_201708": ("Domestic Nuclear Shelters", 1981, "booklet"),
    "civil-defence-why-we-need-it": ("Civil Defence: Why We Need It", 1983, "booklet"),
}
UK_FILMS = {
    "ProtectAndSurvive1NuclearExplosionsExplained_201806": ("Protect and Survive: Nuclear Explosions Explained", 1980),
    "ProtectAndSurvive2TheWarnings": ("Protect and Survive: The Warnings", 1980),
    "ProtectAndSurvive3WhatToDoWhenTheWarningsSound": ("Protect and Survive: What to Do When the Warnings Sound", 1980),
    "ProtectAndSurvive4StayAtHome": ("Protect and Survive: Stay at Home", 1980),
    "ProtectAndSurvive5ChoosingAFallOutRoom": ("Protect and Survive: Choosing a Fall-out Room", 1980),
    "ProtectAndSurvive6Refuges": ("Protect and Survive: Refuges", 1980),
    "ProtectAndSurvive7MaterialsToUseForYourFallOutRoomAndRefuge": (
        "Protect and Survive: Materials to Use for Your Fall-out Room and Refuge", 1980),
    "ProtectAndSurvive8MakeYourFallOutRoomAndRefugeNow": ("Protect and Survive: Make Your Fall-out Room and Refuge Now",
                                                          1980),
    "ProtectAndSurvive9WhatToPutInYourFallOutRoom": ("Protect and Survive: What to Put in Your Fall-out Room", 1980),
    "ProtectAndSurvive10ActionAfterWarnings": ("Protect and Survive: Action After Warnings", 1980),
    "ProtectAndSurvive11WaterAndFood": ("Protect and Survive: Water and Food", 1980),
    "ProtectAndSurvive12Sanitation": ("Protect and Survive: Sanitation", 1980),
    "ProtectAndSurvive13FirePrecautions": ("Protect and Survive: Fire Precautions", 1980),
    "ProtectAndSurvive14TheImportanceOfYourRadio": ("Protect and Survive: The Importance of Your Radio", 1980),
    "ProtectAndSurvive15LifeUnderFallOutConditions": ("Protect and Survive: Life Under Fall-out Conditions", 1980),
    "ProtectAndSurvive16WhatToDoAfterAnAttack": ("Protect and Survive: What to Do After an Attack", 1980),
    "ProtectAndSurvive17SanitationCare": ("Protect and Survive: Sanitation Care", 1980),
    "ProtectAndSurvive18WaterConsumption": ("Protect and Survive: Water Consumption", 1980),
    "ProtectAndSurvive19FoodConsumption": ("Protect and Survive: Food Consumption", 1980),
    "ProtectAndSurvive20Casualties": ("Protect and Survive: Casualties", 1980),
    "RescueAndRelief": ("Rescue and Relief", 1964),
    "TheWardenAndTheHouseholder1961": ("The Warden and the Householder", 1961),
    "TheWardenHisDutiesTraining": ("The Warden, His Duties and Training", 0),
    "CivilDefenceGetsNewGear": ("Civil Defence Gets New Gear", 0),
    "700PracticeCivilDefence": ("700 Practice Civil Defence", 0),
    "CareOfTheHomeless": ("Care of the Homeless", 0),
}
CANADA_BOOKLETS = {
    "31761117081851": ("Your Basement Fallout Shelter (Blueprint for Survival No. 1)", 0, "pamphlet"),
    "31761117081869": ("Fallout on the Farm (Blueprint for Survival No. 3)", 0, "pamphlet"),
    "31761117081646": ("Eleven Steps to Survival (Blueprint for Survival No. 4)", 0, "pamphlet"),
    "31761117081935": ("Survival in Likely Target Areas (Blueprint for Survival)", 0, "pamphlet"),
    "31761117081927": ("Blast Shelters (Blueprint for Survival No. 6)", 0, "pamphlet"),
    "31761117081638": ("Basement Fallout Shelter: A Guide for Use in the Design of", 0, "guide"),
    "31761117081976": ("Plans and Specifications for Family Blast Shelters (30 p.s.i.)", 0, "pamphlet"),
    "31761117081984": ("Plans and Specifications for Family Blast Shelters (10 p.s.i.)", 0, "pamphlet"),
    "31761114615115": ("What the Home Nursing Auxiliary Should Know About Civil Defence", 1957, "booklet"),
    "31761114615123": ("Civil Defence Notebook", 1957, "booklet"),
    "31761115522500": ("Civil Defence and Your Life", 0, "pamphlet"),
}
AUS_NZ_BOOKLETS = {
    "cd-38429837-1": ("Nuclear Weapons: Their Effects and Your Protection", 1987, "handbook", "Australian"),
    "cd-38429837-2": ("Domestic Fallout Shelter Guide", 1989, "guide", "Australian"),
    "HouseholdersHandbook1963": ("Householders' Handbook for Emergencies", 1963, "handbook", "New Zealand"),
}


def http():
    """A requests session with the kit's User-Agent."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def item_files(s, identifier):
    """The files of an Internet Archive item ([] when it does not answer)."""
    time.sleep(PAUSE)
    try:
        r = s.get(f"{ARCHIVE}metadata/{urllib.parse.quote(identifier)}", timeout=90)
        return r.json().get("files", []) if r.status_code == 200 else []
    except Exception:  # noqa: BLE001 - left out
        return []


def text_pdf(files):
    """The name of an item's PDF with OCR words in it ("Text PDF" or "Additional Text PDF"), or ""."""
    for wanted in ("Text PDF", "Additional Text PDF"):
        for f in files:
            if f.get("format") == wanted and str(f.get("name", "")).lower().endswith(".pdf"):
                return f["name"]
    return ""


def marks_for(*texts):
    """The marks of a row from the words known about it: "content" graphic or medical, "child"."""
    words = " ".join(t for t in texts if t)
    marks = {}
    if figures.GRAPHIC.search(words):
        marks["content"] = "graphic"
    elif figures.MEDICAL.search(words):
        marks["content"] = "medical"
    if figures.CHILD.search(words):
        marks["child"] = True
    return marks


def a_or_an(word):
    """"a" or "an" for the word that follows."""
    return "an" if re.match(r"[aeiou]|8|1[18]\d\d\b", str(word), re.I) else "a"


def booklet_rows(fig, page, number, title, year, kind, who, credit):
    """The rows of one picture from a booklet: "Where is this picture from?" always; "What does this picture show?"
    with its printed caption, or for the cover. who: "UK Home Office", "Canadian", "Australian" ..."""
    made = f"{a_or_an(year)} {year} {who}" if year else f"{a_or_an(who)} {who}"
    lead = f"{a_or_an(fig['kind'])} {fig['kind']} from {made} civil defence {kind}, '{title}'"
    marks = marks_for(fig["caption"], title)
    rows = [dict({"question": FROM_Q, "answer": f"It is {lead}.", "split": "", "credit": credit}, **marks)]
    caption = fig["caption"]
    if page == 0 and number == 0 and fig["share"] >= 0.3 and not caption:
        rows.append(dict({"question": DRAWING_Q, "answer": f"It is the cover of {made} civil defence {kind}, "
                                                           f"'{title}'.", "split": "", "credit": credit}, **marks))
    elif caption and figures.caption_ok(caption) and not figures.LEAVE_OUT.search(caption):
        text = caption[:1].lower() + caption[1:] if re.match(r"[A-Z][a-z]", caption) else caption
        said = f"figure {fig['label']}, {text}" if fig["label"] else text
        rows.append(dict({"question": DRAWING_Q, "answer": f"This is {lead}: {said}.", "split": "",
                          "credit": credit}, **marks))
    return rows


def prepare_booklets(source, data_dir, work, cap, items, who_of, licence_words):
    """The pictures of the booklets in items ({identifier: (title, year, kind[, who])}): each booklet's PDF is
    downloaded once, its pages are looked at (civil_defense_figures.page_figures) and its pictures saved. who_of: the
    words for who made it ("UK Home Office"), or None to take them from the item (its fourth field)."""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        say("  The civil defence booklets need pypdfium2 (pip install pypdfium2): left out.")
        return []
    s = http()
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows = []
    for identifier, (title, year, kind, *rest) in items.items():
        if len({r["picture"] for r in rows}) >= cap + source.test:
            break
        who = who_of or (rest[0] if rest else "")
        name = text_pdf(item_files(s, identifier))
        if not name:
            say(f"  {identifier}: no PDF with words found: left out")
            continue
        time.sleep(PAUSE)
        try:
            r = s.get(f"{ARCHIVE}download/{urllib.parse.quote(identifier)}/{urllib.parse.quote(name)}", timeout=600)
            doc = pdfium.PdfDocument(r.content) if r.status_code == 200 else None
        except Exception as e:  # noqa: BLE001 - left out
            say(f"  {identifier}: could not be read ({type(e).__name__})")
            continue
        if doc is None:
            continue
        page_url = f"{ARCHIVE}details/{identifier}"
        credit = f"{title}" + (f" ({year})" if year else "") + f", {who} civil defence; {licence_words}; Internet " \
                                                               f"Archive copy {page_url}"
        got, wanted = 0, cap + source.test
        for n in range(len(doc)):
            if got >= MOST_PER_ITEM or len({r["picture"] for r in rows}) >= wanted:
                break
            for i, fig in enumerate(figures.page_figures(doc[n])[:4]):
                path = os.path.join(folder, f"{re.sub(r'[^A-Za-z0-9]+', '_', identifier)[:50]}_p{n + 1:03d}_{i}.jpg")
                if not smaller(fig["jpeg"], path):
                    continue
                got += 1
                rows += [dict(row, picture=path) for row in booklet_rows(fig, n, i, title, year, kind, who,
                                                                         f"{credit}, page {n + 1}")]
        doc.close()
        say(f"  {title}: {got} pictures")
    return rows


def prepare_films(source, data_dir, work, cap, films, who, licence_words):
    """Stills of the films in films ({identifier: (title, year)}), made by the kit's video_frames.py (PyAV, in
    requirements-video.txt): about one every 6 seconds, the sharpest of each moment, marks near the edges cropped off;
    title cards and blank frames are then left out (civil_defense_figures.still_problem)."""
    try:
        import numpy as np
        from PIL import Image
        import video_frames
    except ImportError as e:
        say(f"  The civil defence films need the video packages (requirements-video.txt): left out ({e}).")
        return []
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows, share = [], max(4, (cap + source.test) // max(1, len(films)) + 1)
    for identifier, (title, year) in films.items():
        if len({r["picture"] for r in rows}) >= cap + source.test:
            break
        out = os.path.join(work, f"cd-film-{identifier}")
        shutil.rmtree(out, ignore_errors=True)
        time.sleep(PAUSE)
        try:
            video_frames.make_pictures([f"archive:{identifier}"], out, every=6.0, max_frames=min(MOST_PER_ITEM,
                                       share * 2), speech=False, say=say, overlays="crop")
        except Exception as e:  # noqa: BLE001 - a film that cannot be read is left out
            say(f"  {title}: could not be read ({type(e).__name__})")
            continue
        stills = sorted(n for n in os.listdir(out) if n.lower().endswith(".jpg")) if os.path.isdir(out) else []
        made = f"the {year} {who}" if year else f"{a_or_an(who)} {who}"
        answer = f"A still from {made} civil defence film '{title}'."
        marks = marks_for(title)
        kept = 0
        for name in stills:
            if kept >= share:
                break
            with open(os.path.join(out, name), "rb") as f:
                data = f.read()
            gray = np.asarray(Image.open(os.path.join(out, name)).convert("L").resize((320, 240)))
            if figures.still_problem(gray):
                continue
            path = os.path.join(folder, f"{re.sub(r'[^A-Za-z0-9]+', '_', identifier)[:50]}_{name}")
            if not smaller(data, path):
                continue
            kept += 1
            rows.append(dict({"question": FROM_Q, "answer": answer, "split": "", "picture": path,
                              "credit": f"{title}" + (f" ({year})" if year else "") + f", {who}; {licence_words}; "
                                        f"Internet Archive copy {ARCHIVE}details/{identifier}"}, **marks))
        shutil.rmtree(out, ignore_errors=True)
        say(f"  {title}: {kept} stills")
    return rows


UK_WORDS = ("Crown copyright (expired in the UK for works published in 1975 or before; restored in the US); "
            "personal use only")


def prepare_cd_uk_booklets_research(source, data_dir, work, cap):
    """UK Home Office civil defence booklets (see the module docstring)."""
    return prepare_booklets(source, data_dir, work, cap, UK_BOOKLETS, "UK Home Office", UK_WORDS)


def prepare_cd_uk_films_research(source, data_dir, work, cap):
    """UK government civil defence films (see the module docstring)."""
    return prepare_films(source, data_dir, work, cap, UK_FILMS, "UK government", UK_WORDS)


def prepare_cd_canada_nc(source, data_dir, work, cap):
    """Canadian civil defence and Emergency Measures Organization booklets (see the module docstring)."""
    return prepare_booklets(source, data_dir, work, cap, CANADA_BOOKLETS, "Canadian",
                            f"Crown copyright, reproduced for non-commercial use under the Government of Canada's "
                            f"terms ({CANADA_TERMS})")


def prepare_cd_aus_nz_research(source, data_dir, work, cap):
    """Australian and New Zealand civil defence handbooks (see the module docstring)."""
    return prepare_booklets(source, data_dir, work, cap, AUS_NZ_BOOKLETS, None,
                            "Commonwealth of Australia or New Zealand Crown copyright; personal use only")


# ----------------------------------------------------------------- the collections

CIVIL_DEFENSE_SOURCES = [
    Source("cd_uk_booklets_research", "UK civil defence handbooks and leaflets, 1949 to 1983, with Protect and "
                                      "Survive (Home Office; Internet Archive copies; personal use)",
           "Crown copyright: out of copyright in the UK for works published in 1975 or before (CDPA 1988 s.163), "
           "in copyright until 2030 to 2033 for the 1980s leaflets; restored in the US (17 U.S.C. 104A). No licence "
           "is given: personal, non-commercial use only",
           "UK Home Office and Central Office of Information, civil defence publications (Crown copyright), via the "
           "Internet Archive, https://archive.org", "research", 400, 10, prepare_cd_uk_booklets_research,
           "about 300 MB of PDFs", terms=UK_TERMS,
           terms_summary="No licence is stated: personal, non-commercial use only (Crown copyright, see the "
                         "UK Copyright Act section 163)."),
    Source("cd_uk_films_research", "UK civil defence films: the Protect and Survive films (1980) and Home Office "
                                   "films of the 1950s and 1960s, stills (Internet Archive copies; personal use)",
           "Crown copyright (the 1980 films until the end of 2030; restored in the US, 17 U.S.C. 104A). No licence "
           "is given: personal, non-commercial use only",
           "UK Home Office and Central Office of Information civil defence films (Crown copyright), via the "
           "Internet Archive, https://archive.org", "research", 400, 10, prepare_cd_uk_films_research,
           "about 300 MB (only the parts of each film needed are read)", terms=UK_TERMS,
           terms_summary="No licence is stated: personal, non-commercial use only (Crown copyright)."),
    Source("cd_canada_nc", "Canadian civil defence and Emergency Measures Organization booklets, 1950s and 1960s "
                           "(University of Toronto copies on the Internet Archive; non-commercial)",
           "Crown copyright (Copyright Act s.12: out of copyright in Canada 50 years after publication); the "
           "Government of Canada allows non-commercial reproduction without permission (canada.ca terms)",
           "Government of Canada (Civil Defence; Emergency Measures Organization), University of Toronto copies via "
           "the Internet Archive, https://archive.org", "noncommercial", 300, 10, prepare_cd_canada_nc,
           "about 150 MB of PDFs", terms=CANADA_TERMS,
           terms_summary="You may reproduce Government of Canada materials for non-commercial purposes, without "
                         "charge or further permission, naming the title and author and saying it is a copy."),
    Source("cd_aus_nz_research", "Australian and New Zealand civil defence handbooks, 1963 to 1989 (Internet Archive "
                                 "copies; personal use)",
           "Commonwealth of Australia copyright (50 years from publication) and New Zealand Crown copyright (100 "
           "years from making); no licence is given: personal, non-commercial use only",
           "Australian Natural Disasters Organisation and New Zealand Ministry of Civil Defence publications, via "
           "the Internet Archive, https://archive.org", "research", 150, 5, prepare_cd_aus_nz_research,
           "about 80 MB of PDFs", terms=AUSTRALIA_LAW,
           terms_summary="No licence is stated: personal, non-commercial use only (Crown and Commonwealth "
                         "copyright)."),
]

# The collections a picture-making model may learn from: none (people, attack and injuries are shown).
CIVIL_DEFENSE_PICTURE_MAKING_OK = set()


# ----------------------------------------------------------------- the source-by-source record

PACK = "built: packs/civil_defense_packs.py"
KIT = "kit entry (downloaded on the user's own computer)"
NOT_IN = "not included"


def entry(source, offers, terms, terms_url, robots, result):
    """One line of the record: the source, what it offers, its licence or terms line and where it is written, what
    its robots.txt says, and what was done (built, kit entry or not included, with the reason)."""
    return {"source": source, "offers": offers, "terms": terms, "terms_url": terms_url, "robots": robots,
            "result": result}


IA_ROBOTS = "archive.org/robots.txt disallows only /control/ and /report/ (read 2026-11-18)"
CIVIL_DEFENSE_RECORD = [
    entry("Internet Archive: US civil defense booklets (Federal Civil Defense Administration, Office of Civil and "
          "Defense Mobilization, Office of Civil Defense, Defense Civil Preparedness Agency, early FEMA)",
          "about 140 items by those agencies (search by creator), and more under the subject 'civil defense'; PDFs "
          "with OCR words", "US government works are not protected by copyright: 'Copyright protection under this "
          "title is not available for any work of the United States Government' (17 U.S.C. 105). The Archive's own "
          "terms (archive.org/about/terms, a page that needs JavaScript; not read in full)",
          "https://www.law.cornell.edu/uscode/text/17/105", IA_ROBOTS,
          PACK + " cd_booklets (open, public domain); items only lent by the Archive (inlibrary, printdisabled), "
                 "microfiche scans, contractor and state items, and items an uploader marked NC or ND are left out"),
    entry("Internet Archive: Prelinger Archives civil defense films", "about 50 civil defense films ('Duck and "
          "Cover', 'Survival Under Atomic Attack', 'About Fallout', 'Operation Cue' ...)",
          "'DO NOT ASSUME that all Prelinger Archives films are in the public domain' ... 'Many Prelinger films carry "
          "a "
          "Creative Commons Public Domain Dedication ... this Public Domain dedication still governs films to which "
          "it has been affixed.'", "https://www.panix.com/~footage/prelarch.html", IA_ROBOTS,
          PACK + " cd_films (open): only items with a public-domain mark, or made by a US federal agency; "
                 "'Medical Aspects of Nuclear Radiation' (1950) left out (shows the ruins of Hiroshima)"),
    entry("Internet Archive: FedFlix (NTIS and National Archives copies of US government films)", "civil defense "
          "films such as 'Duck and Cover' (NTIS AVA11109VNB1), 'Operation Doorstep', 'Civil Defense Scenes'",
          "US government works (17 U.S.C. 105); NTIS and NARA items carry a public-domain or CC0 mark",
          "https://archive.org/details/FedFlix", IA_ROBOTS,
          PACK + " cd_films (open); a second copy of a film already used is skipped"),
    entry("HathiTrust (full-view US federal documents)", "many FCDA and OCD booklets in full view",
          "not read: the site answers with a Cloudflare 'Just a moment...' challenge to automated clients (403), even "
          "for robots.txt and its acceptable-use page", "https://www.hathitrust.org/the-collection/terms-conditions/"
          "acceptable-use-policy/", "refused (403)", NOT_IN + ": the site refuses automated clients; the same "
                                                          "booklets are on the Internet Archive"),
    entry("US National Archives catalogue (catalog.archives.gov)", "civil defense photographs, posters and films",
          "US government works; the v2 API needs an API key (sign-up)", "https://catalog.archives.gov/api/v2",
          "catalog.archives.gov/robots.txt: 'User-agent: * Disallow: /'", NOT_IN + ": robots.txt disallows "
          "everything and the API needs a key; NARA's films are used through their Internet Archive copies (FedFlix)"),
    entry("Library of Congress (loc.gov)", "books search for civil defense and fallout, 1950-1985: mostly "
          "congressional reports and hearings (text, no pictures)", "US government works; LoC items say whether "
          "rights are known", "https://www.loc.gov/legal/", "loc.gov/robots.txt disallows /search (the JSON "
          "collections endpoints are not disallowed); Crawl-Delay 5", NOT_IN + ": no illustrated civil defense "
          "booklets found beyond those on the Internet Archive; its civil defence photos 1900-1945 are already in "
          "the loc_war_disaster pack"),
    entry("UK: Home Office civil defence handbooks and manuals, 1949-1963 (Internet Archive uploads)", "about 15 "
          "handbooks, manuals and pocket books", "Crown copyright 'until the end of the period of 50 years from the "
          "end of the calendar year in which it was first so published' (CDPA 1988 s.163(3)(b)): expired in the UK; "
          "restored in the US by 17 U.S.C. 104A (95 years from publication)", UK_TERMS, IA_ROBOTS,
          KIT + " cd_uk_booklets_research (research: no licence; the uploaders' public-domain marks are not the "
                "Crown's)"),
    entry("UK: 'Protect and Survive' booklet (1980), 'Domestic Nuclear Shelters' (1981), 'Civil Defence: Why We Need "
          "It' (1983)", "public leaflets", "Crown copyright until the end of 2030, 2031 and 2033 (CDPA s.163(3)(b))",
          UK_TERMS, IA_ROBOTS, KIT + " cd_uk_booklets_research (research)"),
    entry("UK: 'Protect and Survive' films (1980) and Home Office films of the 1950s and 1960s (Internet Archive "
          "uploads)", "20 short public information films; about 6 Home Office training films",
          "Crown copyright (the 1980 films until the end of 2030; older films' terms not worked out film by film); "
          "restored in the US", UK_TERMS, IA_ROBOTS, KIT + " cd_uk_films_research (research)"),
    entry("UK: The National Archives (nationalarchives.gov.uk)", "public information films and records",
          "'The material featured on this website is subject to Crown copyright protection and licensed for use "
          "under the Open Government Licence unless otherwise indicated.' Digital copies of records 'may only be used "
          "for: private study or research for a non-commercial purpose' or education",
          "https://www.nationalarchives.gov.uk/terms-and-conditions/copyright/",
          "'Content-Signal: ai-train=no, search=yes, ai-input=no'; Crawl-delay 10",
          NOT_IN + ": its robots.txt reserves AI training, and its record copies are research only"),
    entry("Canada: federal Civil Defence (1950s) and Emergency Measures Organization 'Blueprint for Survival' "
          "pamphlets (University of Toronto copies on the Internet Archive)", "about 12 booklets and pamphlets",
          "Copyright Act s.12: Crown copyright lasts 'for the remainder of the calendar year of the first publication "
          "of the work and for a period of fifty years following the end of that calendar year'; canada.ca: 'you may "
          "reproduce the materials in whole or in part for non-commercial purposes, and in any format, without charge "
          "or further permission'", CANADA_TERMS, IA_ROBOTS,
          KIT + " cd_canada_nc (non-commercial; restored in the US, so not an open pack)"),
    entry("Canada: Alberta Civil Defence circulars and Emergency Measures Organization reports (University of "
          "Alberta copies)", "newsletters, circulars and annual reports", "Alberta Crown copyright", "https://"
          "archive.org/details/albertagovernmentpublications", IA_ROBOTS,
          NOT_IN + ": newsletters and reports with few pictures (the other helper's Alberta open publications are "
                   "in the textbooks)"),
    entry("Australia: 'Nuclear Weapons: Their Effects and Your Protection' (1987) and 'Domestic Fallout Shelter "
          "Guide' (1989)", "two handbooks", "Commonwealth copyright in a published work: 50 years from first "
          "publication (Copyright Act 1968 s.180; the law's page was not read: austlii refused, 403)",
          AUSTRALIA_LAW, IA_ROBOTS, KIT + " cd_aus_nz_research (research)"),
    entry("New Zealand: 'Householders' Handbook for Emergencies' (1963, Ministry of Civil Defence)", "one handbook",
          "Crown copyright: 100 years from the end of the year the work was made (Copyright Act 1994 s.26; the law's "
          "page did not answer, not read)", NZ_LAW, IA_ROBOTS, KIT + " cd_aus_nz_research (research)"),
    entry("Ireland: 'Cosaint Shibhialta: Survival in a Nuclear War' (1965, Civil Defence Ireland)", "one booklet",
          "Irish Government copyright (not worked out); no licence on the item", "https://archive.org/details/"
          "cosaint-shibhialta-bas-beatha", IA_ROBOTS, NOT_IN + ": its terms were not worked out (unverified)"),
    entry("Periscope Film uploads on the Internet Archive ('Let's Face It', 1954 and others)", "civil defense films",
          "'https://creativecommons.org/licenses/by-nc-nd/4.0/' on each item", "https://archive.org/details/"
          "PeriscopeFilm", IA_ROBOTS, NOT_IN + ": no-derivatives licence (a still is a change); the same films are "
                                               "used from other public-domain copies where they exist"),
]


def main(argv=None):
    """Print the record, or try one collection with a small cap (a quick check: prints a few rows)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Civil defence collections: the record, or a quick check.")
    parser.add_argument("key", nargs="?", default="")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--cap", type=int, default=4)
    args = parser.parse_args(argv)
    if args.record or not args.key:
        for line in CIVIL_DEFENSE_RECORD:
            print(json.dumps(line, ensure_ascii=False))
        return 0
    source = next(s for s in CIVIL_DEFENSE_SOURCES if s.key == args.key)
    folder = tempfile.mkdtemp(prefix="cd-")
    source.test = 0
    rows = source.prepare(source, folder, folder, args.cap)
    for row in rows[:args.cap * 2]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, in {folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
