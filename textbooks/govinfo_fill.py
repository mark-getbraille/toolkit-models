"""More books for the thin reference sections, from official copies that programs may read (the owner's request of
2026-11-22). Keys: gpo:<name> (one book), gpo:new:<area> (a sign-up book, see below). Request words: govinfo-fill
(every book) and one word per section (gpo-car, gpo-motor, gpo-pools, gpo-recycling, gpo-ready, gpo-mind,
gpo-aging, gpo-veterans, gpo-genealogy, gpo-relate).

Why this module exists, in plain words: many agency websites refuse programs ("403 Forbidden": NHTSA, FMCSA, CDC,
CPSC, FEMA, Ready.gov, SSA, HHS, SAMHSA) or put a bot check in front of their pages (NIA). The earlier modules list
what refused in their NOT_INCLUDED lists. The same publications, or similar ones by the same agencies, are often
kept elsewhere by official or library hands that do let programs in:
  - GovInfo (www.govinfo.gov), the Government Publishing Office's official site. Its "GOVPUB" collection keeps the
    publications that federal agencies put on their own websites, harvested by the Federal Depository Library
    Program (each copy says "This content was harvested from online sources of the original hosting or authoring
    agency"). Its PDF and metadata addresses need no key, and its robots.txt allows them;
  - the agency's own site where it does let programs in (census.gov, medicare.gov);
  - the Internet Archive's copies of US government publications (military manuals among them).
How the books were found: GovInfo's sitemaps list every GOVPUB package; a package's name starts with the
publisher's Superintendent of Documents class (TD 8 is NHTSA, HS 5 is FEMA, HE 20.8100 is NIMH, HE 20.400 is SAMHSA,
VA is Veterans Affairs and so on), so the packages of the agencies that refused were picked out and each one's
MODS record (title, date, pages, publishers) read once by a one-off research script on 2026-11-22 (not part of the
build). Every chosen PDF was then opened to check its text layer, its publishers (a book made with an organisation
outside the federal government, or holding someone else's copyrighted text, was left out and is listed in
NOT_INCLUDED) and the words of its description. The books below are the ones a person would
want (guides and booklets for the public, not research notes or reports to Congress).

Every book is a work of the US government (public domain, 17 U.S.C. 105; the builder checks govinfo's quotation of
that law at every build), read whole as one PDF (build_textbooks.pdfdoc_book: one page per chapter). Its notice says
which agency wrote it, its date or edition, where the copy comes from, that it is not the current edition when a
newer one exists, and the section's own safety or help note. The military manuals (Army and Navy vehicle, tyre,
battery, driver, motorcycle and trailer manuals) are judged by the release rule for military publications
(military_release.py) and read WHOLE, except that parts about explosives, demolition, mines, grenades, booby traps
and sabotage are left out (build_textbooks.NOT_FIELD_SAFE: such as the "destruction of materiel to prevent enemy
use" chapters of vehicle manuals).

The sign-up books (gpo:new:<area>): GovInfo's search API (api.govinfo.gov) needs a free api.data.gov key. When the
owner has one, he sets it in the environment variable GOVINFO_API_KEY (the build's settings or his own computer;
never in the repository: the key is sent only to api.govinfo.gov, in a request header); each section then gets a
list of the newest GovInfo publications of its agencies (title, date, agency and the links to the PDF and the
record), so new booklets can be found and added. Without the key the build says where to sign up
(https://api.data.gov/signup/) and builds nothing for that key.

Not built (NOT_INCLUDED): the FDLP's catalog (catalog.gpo.gov refuses programs), permanent.fdlp.gov (its robots.txt
refuses every program), the NCBI Bookshelf (a reCAPTCHA check; its FTP site's robots.txt refuses every program),
EPA's NSCEP library, and the Internet Archive's lending-library copies (borrow only).

Run from the repository's folder:
  python3 textbooks/govinfo_fill.py --list govinfo-fill
  python3 textbooks/govinfo_fill.py gpo:census_measuring_america --out build/textbooks --limit 5
"""

import datetime
import html
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import govinfo_kit as GK  # noqa: E402 - the shared govinfo names (one key for every govinfo sign-up entry)
import practical_index as PI  # noqa: E402 - the EPA's terms (as recycling.py uses them)
import aging_end_of_life as AG  # noqa: E402 - the sections' groups and notes are the existing modules' own
import car_care as CC  # noqa: E402
import disaster_ready as DR  # noqa: E402
import driving as DV  # noqa: E402
import genealogy as GE  # noqa: E402
import mental_health as MH  # noqa: E402
import motorcycles_rvs as MR  # noqa: E402
import pools_spas as PS  # noqa: E402
import recycling as RC  # noqa: E402
import relationships as RL  # noqa: E402
import veterans as VT  # noqa: E402

PREFIX = "gpo"
# The same names as govinfo_kit.py (the history, travel and education collections' govinfo helpers), so the owner
# sets one key, GOVINFO_API_KEY, for every govinfo sign-up entry.
GOVINFO = GK.GOVINFO
KEY_ENV = GK.GOVINFO_KEY_ENV
SIGNUP = GK.GOVINFO_SIGNUP
API = GK.GOVINFO_API + "/search"

# ---------------------------------------------------------------------- the sections

# area: (request word, group (the existing module's), the section's name, its safety or help note, the
# Superintendent of Documents classes its sign-up book searches on GovInfo)
AREAS = {
    "car": ("gpo-car", CC.GROUP, "Car care and driving",
            CC.SAFETY + " " + DV.DRIVE_SAFETY, ["TD8", "TD2_300"]),
    "drive": ("gpo-car", DV.GROUP, "Driving and road rules", DV.DRIVE_SAFETY, []),     # car's list covers it
    "motor": ("gpo-motor", MR.GROUP, "Motorcycles, RVs and trailers", MR.ROAD_SAFETY, ["TD8"]),
    "pools": ("gpo-pools", PS.GROUP, "Pools and spas", PS.POOL_SAFETY, ["Y3_C76_3", "HE20_7000"]),
    "recycle": ("gpo-recycling", RC.GROUP, "Recycling and waste", RC.NOTE, ["EP", "EP4_50"]),
    "ready": ("gpo-ready", DR.GROUP, "Emergency preparedness and disasters", DR.SAFETY_NOTE,
              ["HS5", "HS5_100", "HS5_200", "FEM1"]),
    "mind": ("gpo-mind", MH.GROUP, "Mental health and wellbeing", MH.HEALTH_NOTE,
             ["HE20_400", "HE20_8100", "HE20_100"]),
    "aging": ("gpo-aging", AG.GROUP, "Aging and end of life", AG.NOTE, ["HE20_3850", "HE22", "SSA1"]),
    "veterans": ("gpo-veterans", VT.GROUP, "Veterans", VT.CRISIS + " " + VT.LEGAL, ["VA"]),
    "gen": ("gpo-genealogy", GE.GROUP, "Genealogy", GE.NOTE, ["AE", "C3"]),
    "relate": ("gpo-relate", RL.GROUP, "Communication and relationships", RL.HOTLINES, ["HE25", "HE24"]),
}


def group_of(area):
    """The library group of a section (the existing module's group, so the books sit beside its own)."""
    return AREAS[area][1]


def note_of(area):
    """The safety or help note every book of a section ends with."""
    return AREAS[area][3]


# ---------------------------------------------------------------------- the three kinds of entry

def govinfo(area, name, title, subject, publisher, package, published, description, newer="", epa=False):
    """A publication kept by GovInfo (a GOVPUB package harvested from the agency's own site): its PDF is read
    whole. package: the GovInfo package name ("GOVPUB-HE20_3850-PURL-gpo156646"); published: its date or year as
    GovInfo's record gives it; newer: a sentence saying the edition is not the newest and where the current one is
    (said in the notice), or "". epa: an EPA publication, kept under the EPA's own terms like recycling.py's EPA
    pages (non-commercial: personal use only)."""
    pdf = f"{GOVINFO}/content/pkg/{package}/pdf/{package}.pdf"
    notice = (f"A work of the US government ({publisher}, {published[:4]}): public domain under 17 U.S.C. 105. This "
              f"copy is GovInfo's (the Government Publishing Office's official site), which keeps what the agency "
              f"published on its own website (package {package}). {newer + ' ' if newer else ''}"
              f"{note_of(area)}")
    entry = K.us_pdf(group_of(area), name=name, title=title, subject=subject, publisher=publisher, pdf=pdf,
                     page=f"{GOVINFO}/app/details/{package}", published=published, area=area,
                     version=f"GovInfo package {package} ({published})", description=description,
                     notice=" ".join(notice.split()))
    if epa:     # the EPA's own terms, as recycling.py keeps them: personal use only (non-commercial)
        entry.update(licence=PI.EPA_TERMS, licence_url=PI.EPA_DISCLAIMER, licence_page=PI.EPA_DISCLAIMER,
                     licence_text=PI.EPA_TEXT, personal_use=True,
                     notice=" ".join(f"{RC.EPA_NOTICE} This copy is GovInfo's (package {package}). {newer} "
                                     f"{note_of(area)}".split()))
    return entry


def official(area, name, title, subject, publisher, pdf, page, published, description, newer=""):
    """A publication read from the agency's own site, where its robots.txt lets programs in (census.gov,
    medicare.gov). published: its date or edition; "" for a yearly edition read anew each time it changes."""
    when = f", {published[:4]}" if published else ""
    notice = (f"A work of the US government ({publisher}{when}): public domain under 17 U.S.C. 105, read from the "
              f"agency's own site. {newer + ' ' if newer else ''}{note_of(area)}")
    entry = K.us_pdf(group_of(area), name=name, title=title, subject=subject, publisher=publisher, pdf=pdf,
                     page=page, area=area, version=f"{pdf} ({published or 'the current edition'})",
                     description=description, notice=" ".join(notice.split()))
    if published:
        entry["published"] = published
    return entry


def archive(area, name, title, subject, publisher, item, published, description, military=False, newer=""):
    """A US government publication read from its Internet Archive copy. military: an Army, Navy or Marine Corps
    manual, judged by the release rule (military_release.py: the builder puts the truthful release line first) and
    read whole, with the parts about explosives, demolition, mines, grenades, booby traps and sabotage left out
    (distribution_a turns on build_textbooks.NOT_FIELD_SAFE)."""
    # A military book's notice starts with the builder's own truthful release line (build_textbooks.military_notice),
    # which already says whose work it is and that it is public domain; so this part only says where the copy is from.
    who = "" if military else f"A work of the US government ({publisher}, {published[:4]}): public domain under 17 " \
                              f"U.S.C. 105, read from the Internet Archive's copy"
    where = f"{who or 'Read from the Internet Archive' + chr(39) + 's copy'} (item {item}), whose machine-read text " \
            f"may have the scanner's mistakes."
    notice = f"{where} {newer + ' ' if newer else ''}{note_of(area)}"
    entry = K.us_pdf(group_of(area), name=name, title=title, subject=subject, publisher=publisher, archive=item,
                     published=published, area=area, version=f"Internet Archive item {item}",
                     description=description, notice=" ".join(notice.split()))
    if military:
        entry.update(distribution_a=True, work=f"a work of the US armed forces ({publisher})")
    return entry


# ---------------------------------------------------------------------- the sign-up books (GovInfo's search API)

def api_search(key, docclass, size=100):
    """The newest GovInfo GOVPUB publications of one Superintendent of Documents class (GovInfo's "docClass", such as
    "TD8" or "HS5_100"; the query form was tried against the live API on 2026-11-22), from GovInfo's search API:
    [{title, packageId, dateIssued, governmentAuthor}], newest first. The key goes in the X-Api-Key header (never in
    the address, so it is not written to any log). Raises urllib.error.HTTPError when the API refuses."""
    import build_textbooks as B
    body = json.dumps({"query": f"collection:GOVPUB AND docclass:{docclass}", "pageSize": size, "offsetMark": "*",
                       "sorts": [{"field": "publishdate", "sortOrder": "DESC"}]}).encode("utf-8")
    # keyed_urlopen: the key goes only to api.govinfo.gov, also when it answers "moved".
    with B.keyed_urlopen(API, {"X-Api-Key": key}, data=body, method="POST", headers={
            "User-Agent": B.USER_AGENT, "Content-Type": "application/json", "Accept": "application/json"},
            timeout=120) as r:
        return json.load(r).get("results", [])


def rows_html(rows):
    """A list of GovInfo search results as HTML: each title with its date, agency and the links to its PDF and its
    GovInfo record."""
    import build_textbooks as B
    items = []
    for r in rows:
        pkg = str(r.get("packageId", ""))
        authors = r.get("governmentAuthor") or []
        who = ", ".join(authors if isinstance(authors, list) else [str(authors)])
        items.append(f"<li><strong>{B.esc(html.unescape(str(r.get('title', pkg))))}</strong> "
                     f"({B.esc(str(r.get('dateIssued', ''))[:10])}{'; ' + B.esc(who) if who else ''}). "
                     f"<a href=\"{GOVINFO}/content/pkg/{pkg}/pdf/{pkg}.pdf\">PDF</a>, "
                     f"<a href=\"{GOVINFO}/app/details/{pkg}\">GovInfo record</a>.</li>")
    return "<ul>" + "".join(items) + "</ul>" if items else "<p>Nothing was found.</p>"


def new_book(name, work, cache=None, left_out=None, limit=None):
    """A sign-up book (gpo:new:<area>): the newest GovInfo publications of the section's agencies, one page per
    Superintendent of Documents class. It needs the owner's own api.data.gov key in GOVINFO_API_KEY; without it,
    left_out says where to sign up and nothing is built."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    area = name.split(":", 1)[1] if ":" in name else ""
    if area not in AREAS:
        left_out.append({"title": f"{PREFIX}:{name}", "reason": "Unknown section."})
        return None
    _word, group, label, note, classes = AREAS[area]
    title = f"New on GovInfo: {label.lower()} (US government publications)"
    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        left_out.append({"title": title, "reason": f"A sign-up entry: GovInfo's search API needs the owner's own free "
                         f"api.data.gov key (sign up at {SIGNUP}, then set {KEY_ENV} in the build's settings, never "
                         f"in the repository).", "url": SIGNUP, "fetch_yourself": True})
        return None
    book = K.new_book(f"{PREFIX}_new_{area}", title, label, group, "US Government Publishing Office (GovInfo); each "
                      "publication's own agency", K.US_GOV, K.US_GOV_URL, GOVINFO + "/app/collection/govpub",
                      f"The newest US government publications on {label.lower()} that GovInfo keeps (its GOVPUB "
                      f"collection: what the agencies publish on their own websites), with links to each PDF.",
                      f"Works of the US government (public domain under 17 U.S.C. 105), listed from GovInfo's search "
                      f"API. Each entry links to the publication itself; the list is read anew at every build. {note}",
                      changes="GovInfo's search results made into lists, one page per agency class")
    for chapter, docclass in enumerate(classes, 1):
        if limit and len(book.pages) >= limit:
            break
        try:
            rows = api_search(key, docclass)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                left_out.append({"title": title, "reason": f"GovInfo's API refused the key in {KEY_ENV} ({e.code}); "
                                 f"check it at {SIGNUP}."})
                return None
            left_out.append({"title": f"{title}: {docclass}", "reason": f"GovInfo's API answered {e.code}."})
            continue
        except (urllib.error.URLError, OSError, ValueError) as e:
            left_out.append({"title": f"{title}: {docclass}",
                             "reason": f"GovInfo's API could not be read ({B.hide_keys(e)})."})
            continue
        book.pages.append(B.Page(f"class-{docclass.lower()}", f"Publications of class {docclass.replace('_', '.')}",
                                 rows_html(rows), chapter))
        book.originals.append({"url": API, "kind": "json", "title": f"GovInfo search: docclass {docclass}"})
    book.version = f"GovInfo search API, read {datetime.date.today().isoformat()}"
    return book if book.pages else None


def new_sign(name):
    """The weekly sign of a sign-up book: the week (GovInfo adds publications every day); "" without the key, so
    nothing is rebuilt then."""
    return K.sha(name, datetime.date.today().isocalendar()[:2]) if os.environ.get(KEY_ENV, "").strip() else ""


# ====================================================================== the books, section by section

ARMY = "Headquarters, Department of the Army"
NAVY = "Naval Education and Training Command, US Navy"
NHTSA = "National Highway Traffic Safety Administration (NHTSA), US Department of Transportation"
FMCSA = "Federal Motor Carrier Safety Administration (FMCSA), US Department of Transportation"
OLD_MANUAL = ("An old military manual: its vehicles, fuels and some methods are out of date, and it was written for "
              "soldiers, so follow your own vehicle's owner's manual for anything you do; kept for its clear "
              "explanations of how the parts work.")

# ---------------------------------------------------------------------- car care
CAR = [
    govinfo("car", "nhtsa_tire_safety_2008", "Tire Safety: Everything Rides on It (NHTSA, 2008)", "Tyre safety",
            NHTSA, "GOVPUB-TD8-PURL-gpo10013", "2008",
            "NHTSA's consumer booklet on tyres (DOT HS 810 900, 14 pages): basic tyre maintenance (pressure, "
            "tread, balancing and alignment, repairs), the load limits of tyres and vehicles, the Uniform Tire "
            "Quality Grading System, what the markings on a tyre's sidewall mean, and tyre safety tips.",
            newer="Published in 2008: NHTSA's tyre pages on nhtsa.gov are the current advice."),
    govinfo("car", "nhtsa_tire_psi_quiz_2005", "What's Your PSI? A Short Quiz to Test Your Knowledge of Tire "
            "Safety (NHTSA, 2005)", "Tyre safety", NHTSA, "GOVPUB-TD8-PURL-gpo838", "2005",
            "NHTSA's two-page tyre quiz with its answers (DOT HS 809 866): why you cannot judge pressure by "
            "looking, checking every tyre and the spare at least once a month, measuring when the tyres are cold, "
            "and where the right pressure is written.", newer="Published in 2005."),
    govinfo("car", "nhtsa_defects_and_recalls_2006", "Motor Vehicle Safety Defects and Recalls: What Every "
            "Vehicle Owner Should Know (NHTSA, 2006)", "Vehicle recalls", NHTSA, "GOVPUB-TD8-PURL-gpo10008",
            "2006-03",
            "NHTSA's booklet on recalls (DOT HS 808 795, March 2006): when a recall is necessary, what is and is "
            "not a safety-related defect (with examples), how to report a safety problem to NHTSA and how the "
            "report is used, and what owners can expect when a recall is announced.",
            newer="Published in 2006: phone numbers and web addresses have changed; check a vehicle for open "
                  "recalls by its VIN at nhtsa.gov/recalls (the library's recalls books list NHTSA's recalls)."),
    govinfo("car", "nhtsa_odometer_fraud_1996", "Odometer Fraud: Traffic Safety Tips (NHTSA, 1996)",
            "Buying a used car", NHTSA, "GOVPUB-TD8-PURL-LPS68360", "1996",
            "NHTSA's four-page leaflet on odometer fraud (summer 1996): what it is, why it is costly, the federal "
            "law against rolling back odometers, and how a buyer of a used car can spot signs of it.",
            newer="Published in 1996: the hotline numbers in it have changed."),
    archive("car", "army_tm_9_8000_1985", "Principles of Automotive Vehicles (TM 9-8000, 1985)",
            "How cars and trucks work", ARMY, "tm-9-8000-principles-of-automotive-vehicles-1985", "1985-10-25",
            "The Army's textbook of how its vehicles work, part by part (25 October 1985, reprinted with Change "
            "1): the characteristics and kinds of military vehicles, piston engines, gasoline and diesel fuel "
            "systems, and on through the power train to the rest of the vehicle, in more than thirty chapters.", military=True, newer=OLD_MANUAL),
    archive("car", "army_tm_9_2700_1947", "Principles of Automotive Vehicles (TM 9-2700, 1947)",
            "How cars and trucks work", "War Department / Department of the Army", "TM9-2700", "1947-11-18",
            "The Army's 1947 textbook of how motor vehicles work: engines (principles of operation, practical "
            "application, performance and construction), gasoline and diesel fuel systems, and the rest of the "
            "vehicle, chapter by chapter. A scan of a university library copy.", military=True,
            newer=OLD_MANUAL),
    archive("car", "army_tm_9_1870_1_tires_1955", "Care and Maintenance of Pneumatic Tires (TM 9-1870-1, 1955)",
            "Tyre care", ARMY, "TM9-1870-1", "1955-02-18",
            "The Army's manual on tyres and inner tubes (18 February 1955, with its changes to 1967): how tubed "
            "and tubeless tyres are made, their care and use, the common causes of tyre failures, mounting and "
            "demounting, and repairing tubeless tyres, valves and tubes.", military=True, newer=OLD_MANUAL),
    archive("car", "army_tm_9_6140_200_14_batteries_1998", "Maintenance Manual for Lead-Acid Storage Batteries "
            "(TM 9-6140-200-14, 1998)", "Car and truck batteries", ARMY,
            "tm-9-6140-200-14-maintenance-manual-for-lead-acid-storage-batteries-1998", "1998",
            "The Army's manual for 12-volt and 24-volt lead-acid vehicle batteries: how a battery works, the "
            "operator's preventive maintenance checks and services, maintenance and troubleshooting, sealed gel "
            "batteries, and how to dispose of a battery.", military=True,
            newer="Written for military batteries; follow your own battery's label and your car's manual."),
    archive("car", "navy_construction_mechanic_3_2_1978", "Construction Mechanic 3 & 2 (US Navy rate training "
            "manual, 1978)", "Automotive repair", NAVY, "ERIC_ED170540", "1978",
            "The Navy's training manual for Seabee construction mechanics: internal combustion engines and how "
            "they are built, fuel systems, cooling and lubricating systems, automotive electricity, power trains, "
            "chassis and bodies, brakes, construction equipment and maintenance, with inspection guides. Read "
            "from the copy kept by ERIC, the Department of Education's library (the drawings are not copied).",
            military=True, newer=OLD_MANUAL),
]

# ---------------------------------------------------------------------- driving and road rules
DRIVE = [
    govinfo("drive", "nhtsa_winter_driving_2017", "Winter Driving Tips (NHTSA, 2017)", "Winter driving", NHTSA,
            "GOVPUB-TD8-PURL-gpo87907", "2017",
            "NHTSA's five pages of winter driving advice: getting the car serviced and checking for recalls "
            "before winter (battery, cooling system, tyres), knowing how your car handles on snow and ice, "
            "staying alert on the road, driving in winter conditions and around snow ploughs, and protecting "
            "children."),
    govinfo("drive", "nhtsa_stepping_out_2003", "Stepping Out: Mature Adults, Be Healthy, Walk Safely (NHTSA, "
            "2003)", "Walking safely", NHTSA, "GOVPUB-TD8-PURL-LPS105942", "2003-02",
            "NHTSA's booklet for older walkers (DOT HS 809 556, February 2003): the health benefits of walking, "
            "getting started and staying motivated, and staying safe at intersections, in parking lots, where "
            "there are no sidewalks and in bad weather, and making a community safer to walk in.",
            newer="Published in 2003."),
    govinfo("drive", "nhtsa_kids_bicycle_safety_2006", "Kids and Bicycle Safety (NHTSA, 2006)", "Bicycle safety",
            NHTSA, "GOVPUB-TD8-PURL-LPS74715", "2006-04",
            "NHTSA's two-page bicycle safety sheet for children (DOT HS 810 601, April 2006): wearing a properly "
            "fitted helmet, adjusting the bicycle, checking it before riding, and the rules of the road for "
            "riders."),
    govinfo("drive", "fmcsa_no_zone_2008", "What Is the No-Zone? Don't Hang Out in the No-Zone (FMCSA, 2008)",
            "Sharing the road with trucks", FMCSA, "GOVPUB-TD2_300-PURL-LPS117263", "2008",
            "FMCSA's two-page leaflet (FMCSA-MC-99-017) on the No-Zones: the danger areas around trucks and buses "
            "where crashes are more likely, some of them blind spots where a car disappears from the driver's "
            "view."),
    govinfo("drive", "fmcsa_smart_drivers_2001", "Smart Drivers: Share the Road Safely (FMCSA, 2001)",
            "Sharing the road with trucks", FMCSA, "GOVPUB-TD2_300-PURL-gpo39454", "2001",
            "FMCSA's two-page leaflet (DOT-MC-01-089) for car drivers: how large trucks differ from cars "
            "(stopping distance, blind spots, wide turns) and how to share the road with them safely."),
    archive("drive", "army_fm_21_305_1993", "Manual for the Wheeled Vehicle Driver (FM 21-305, 1993)",
            "Driving", "Headquarters, Department of the Army and Department of the Air Force",
            "fm-21-305-manual-for-the-wheeled-vehicle-driver-1993", "1993-08",
            "The Army and Air Force driver's manual (FM 21-305 / AFMAN 24-306, August 1993): driver "
            "regulations and responsibilities (with fuel-efficient operation), traffic controls (signals and "
            "signs), speed control, good driving practices, intersections, pedestrians, bicyclists and animals, "
            "and operating practices and manoeuvres, among its many chapters.", military=True,
            newer="Written for military drivers in 1993; your state's driver handbook has today's law."),
    archive("drive", "army_tc_21_305_100_cdl_1996", "The Military Commercial Driver's License Driver's Manual "
            "(TC 21-305-100, 1996)", "Commercial driver's licence", ARMY,
            "tc-21-305-100-the-military-commercial-drivers-license-drivers-manual-1996", "1996-08-19",
            "The Army's manual for soldiers preparing for the commercial driver's licence tests (19 August "
            "1996): the vehicle classes, the tests and the Safety Act rules, safe driving, the inspections before, "
            "during and after a trip, hazardous materials, and the pre-trip inspection, basic control skills and "
            "driving tests.", military=True,
            newer="Written in 1996: the CDL rules have changed since (FMCSA's rules, and your state's CDL manual, "
                  "are today's law)."),
    archive("drive", "army_tm_21_305_drivers_manual_1944", "Driver's Manual (TM 21-305, 1944)", "Driving",
            "War Department", "TM21-305", "1944-11",
            "The War Department's driver's manual of November 1944: you and your vehicle, protecting it from "
            "abuse, getting there safely (solo and in a column), bad roads and cross-country driving, driving in "
            "warfare or manoeuvres, four hidden enemies, preventive maintenance, and what to do if something goes "
            "wrong. A scan of a university library copy.", military=True,
            newer="Written in 1944 for army drivers: kept as history and for its plain advice on looking after a "
                  "vehicle; today's traffic law is in your state's handbook."),
]

# ---------------------------------------------------------------------- motorcycles, RVs and trailers
MOTOR = [
    archive("motor", "army_tm_10_515_motorcycle_1942", "The Motorcycle (TM 10-515, 1942)", "Motorcycles",
            "War Department (prepared under the direction of the Quartermaster General)", "1942TM10-515",
            "1942-09-25",
            "The War Department's manual on the motorcycle (25 September 1942): types of motorcycles, training "
            "riders, the parts and their maintenance (pistons, valves, bearings, carburettor, lighting and "
            "ignition, cooling, oiling, transmission, chains, wheels, brakes, front fork and frame), operation in "
            "cold weather, breaking in, and inspections.", military=True,
            newer="Written in 1942: kept as history and for how a motorcycle's parts work."),
    archive("motor", "army_tm_9_879_harley_wla_1943", "Motorcycle, Solo (Harley-Davidson Model WLA) (TM 9-879, "
            "1943)", "Motorcycles", "War Department", "TM9-879", "1943-10-18",
            "The War Department's operator and maintenance manual for the Harley-Davidson WLA (18 October 1943): "
            "controls and operation, preventive maintenance services, lubrication, troubleshooting, the engine, "
            "clutch, transmission, chains and sprockets, fuel system and the other parts.", military=True,
            newer="Written in 1943 for one wartime motorcycle: kept as history and for how its parts work."),
    archive("motor", "army_tm_9_2330_202_14_trailer_m101_m116", "Operator's, Unit, Direct Support and General "
            "Support Maintenance Manual: Trailer, Cargo, 3/4 Ton, M101 Series, and Trailer, Chassis, M116 Series "
            "(TM 9-2330-202-14&P, 1997)", "Trailers: coupling, brakes, lights and maintenance", ARMY,
            "trl-1-ton-m-116-tm-9-2330-202-14-p-m-116-14-p", "1997-05",
            "The Army's operator and maintenance manual for its small two-wheel cargo trailers: the operator's "
            "controls and indicators, the operator's preventive maintenance checks and services, operation under "
            "usual and unusual conditions, unit maintenance (axles, accessory items and the rest), and the repair "
            "parts lists.", military=True,
            newer="Written for military trailers (a pintle hitch and military connector); a civilian trailer's "
                  "own manual and your state's rules come first."),
    govinfo("motor", "usfa_rv_fires_2022", "Recreational Vehicle Fires (2018-2020) (US Fire Administration, "
            "2022)", "RV fire safety", "US Fire Administration, FEMA (National Fire Data Center)",
            "GOVPUB-HS5-PURL-gpo187721", "2022-05",
            "The US Fire Administration's three-page data snapshot (May 2022) on fires in motorhomes and travel "
            "trailers reported to fire departments from 2018 to 2020: how many there were, the deaths, injuries "
            "and losses they caused, how many were in self-propelled RVs, and when they happened (time of day, "
            "day of the week and month)."),
]

# ---------------------------------------------------------------------- pools and spas
CPSC = "US Consumer Product Safety Commission (CPSC)"
POOLS = [
    govinfo("pools", "cpsc_pool_safety_barriers_2017", "Safety Barrier Guidelines for Residential Pools: Preventing "
            "Child Drownings (CPSC, 2017)", "Pool fences and barriers", CPSC, "GOVPUB-Y3_C76_3-PURL-gpo85685", "2017",
            "CPSC's guidelines for fences, gates, doors and other barriers around home swimming pools, spas and hot "
            "tubs, so young children cannot get to the water unseen; it says barriers never replace adult "
            "supervision, and that some states and towns have put these guidelines into their building codes. "
            "CPSC prints that the document is in the public domain."),
    govinfo("pools", "cpsc_spas_hot_tubs_alert_1996", "Spas, Hot Tubs, and Whirlpools: Safety Alert (CPSC, 1996)",
            "Hot tub safety", CPSC, "GOVPUB-Y3_C76_3-PURL-LPS51051", "1996",
            "CPSC's one-page safety alert on spas, hot tubs and whirlpools: the hazards of drowning, hair "
            "entanglement and body entrapment at the drain, and why old spas should get new, safer drain covers.",
            newer="Published in 1996: the Virginia Graeme Baker Pool and Spa Safety Act (2007) has since made safer "
                  "drain covers the law for public pools and spas."),
]

# ---------------------------------------------------------------------- recycling and waste (EPA: personal use)
RECYCLE = [
    govinfo("recycle", "epa_food_loss_waste_strategy_2024", "National Strategy for Reducing Food Loss and Waste and "
            "Recycling Organics (EPA, USDA and FDA, 2024)", "Food waste and composting",
            "US Environmental Protection Agency, US Department of Agriculture and US Food and Drug Administration",
            "GOVPUB-EP-PURL-gpo250252", "2024",
            "The federal strategy for cutting food loss and waste and for recycling food scraps and other organic "
            "waste (composting and the like): its background, goal, the challenges and the objectives and actions "
            "the three agencies set.", epa=True),
    govinfo("recycle", "epa_ecigarette_disposal_2023", "How to Safely Dispose of E-Cigarettes: Information for "
            "Individuals (EPA, 2023)", "Household hazardous waste", "US Environmental Protection Agency, Office of "
            "Resource Conservation and Recovery", "GOVPUB-EP-PURL-gpo246076", "2023",
            "EPA's one-page guide to getting rid of used and unwanted e-cigarettes and vapes, which hold nicotine "
            "and lithium batteries: why they belong at a household hazardous waste collection site and not in the "
            "trash or recycling (they can cause fires and release toxic chemicals).", epa=True),
]

# ---------------------------------------------------------------------- emergency preparedness and disasters
FEMA = "Federal Emergency Management Agency (FEMA), US Department of Homeland Security"
USFA = "US Fire Administration, FEMA"
READY = [
    govinfo("ready", "fema_are_you_ready_2020", "Are You Ready? An In-Depth Guide to Citizen Preparedness (FEMA "
            "P-2064, 2020)", "Emergency preparedness", FEMA, "GOVPUB-HS5_100-PURL-gpo159555", "2020-09",
            "FEMA's newer, shorter edition of its preparedness guide (P-2064, September 2020, 29 pages): the "
            "benefits of planning ahead, knowing your risks, protective actions for every disaster and for each "
            "hazard (from active shooter, earthquake, extreme heat, flood and hurricane to pandemics, power "
            "outages, wildfire and winter storms), making a plan, gathering supplies, protecting documents and "
            "property, and recovering from a disaster. The library's 2004 edition (prep:"
            "fema_are_you_ready) is the long one."),
    govinfo("ready", "fema_cert_basic_training_2019", "CERT Basic Training: Participant Manual (FEMA, 2019)",
            "Community emergency response", FEMA + ", Community Emergency Response Team (CERT) program",
            "GOVPUB-HS5_100-PURL-gpo185734", "2019-08",
            "The participant manual of the Community Emergency Response Team course (August 2019 update), unit by "
            "unit: disaster preparedness, the CERT organisation, disaster medical operations, disaster psychology, "
            "fire safety and utility controls, light search and rescue operations, and terrorism and CERT, ending "
            "with a course review, final exam and disaster simulation. CERT trains volunteers to help their families and neighbours when "
            "professional responders cannot come at once."),
    govinfo("ready", "fema_take_control_older_adults_2023", "Take Control in 1, 2, 3: Disaster Preparedness Guide "
            "for Older Adults (FEMA, 2023)", "Preparedness for older adults", FEMA, "GOVPUB-HS5_100-PURL-gpo253002",
            "2023",
            "FEMA's three-step guide for older adults: step 1, assess your needs (a self-assessment); step 2, make a "
            "plan and an emergency kit suited to your needs; step 3, engage your support network of family, "
            "friends, caregivers, neighbours and others."),
    govinfo("ready", "fema_alerts_and_warnings_2021", "Be Aware, Be Prepared, Take Action: A Guide for Alerts and "
            "Warnings (FEMA, 2021)", "Emergency alerts", FEMA, "GOVPUB-HS5_100-PURL-gpo177123", "2021-08",
            "FEMA's guide (August 2021) to the alerts and warnings you may get on a TV, phone or radio: for each "
            "hazard (tornadoes, floods, hurricanes, earthquakes, tsunamis, winter storms and others), what a watch "
            "or a warning means and what to do if it reaches you at home, with twelve ways to prepare before a "
            "disaster."),
    govinfo("ready", "fema_family_communication_plan_2018", "Create Your Family Emergency Communication Plan "
            "(FEMA, 2018)", "Family emergency plan", FEMA, "GOVPUB-HS5_100-PURL-gpo115612", "2018",
            "FEMA's eight-page guide and forms for a family emergency communication plan: collect the contact "
            "information of everyone in the household, decide where to meet, share the plan and practise it, so "
            "everyone (children, people with disabilities and outside caregivers too) can reach each other."),
    govinfo("ready", "fema_emergency_supply_list_2014", "Emergency Supply List (FEMA, 2014)", "Emergency kit",
            FEMA, "GOVPUB-HS5_100-PURL-gpo126182", "2014",
            "Ready.gov's two-page checklist of what to put in an emergency supply kit, and the additional items to "
            "consider (medicines and glasses, infant formula, pet food, important documents, cash, bedding and "
            "clothing, and others)."),
    govinfo("ready", "fema_safeguard_documents_2018", "Safeguard Critical Documents and Valuables (FEMA, 2018)",
            "Important papers", FEMA, "GOVPUB-HS5_100-PURL-gpo127771", "2018",
            "FEMA's three-page checklist for keeping financial, medical and other important documents, contacts "
            "and valuables safe before a disaster, so recovery can start quickly."),
    govinfo("ready", "fema_twelve_ways_to_prepare_2018", "12 Ways to Prepare (FEMA, 2018)", "Emergency "
            "preparedness", FEMA, "GOVPUB-HS5_100-PURL-gpo159544", "2018-04",
            "FEMA's two-page card (V-1021, April 2018) of twelve ways to prepare: sign up for alerts, make a plan, "
            "save for a rainy day, practise drills, test the family communication plan, safeguard documents, plan "
            "with neighbours, make your home safer, know evacuation routes, assemble supplies, get involved, and "
            "document and insure property."),
    govinfo("ready", "fema_pets_disasters_2021", "Prepare Your Pets for Disasters (FEMA, 2021)", "Pets in "
            "emergencies", FEMA, "GOVPUB-HS5_100-PURL-gpo159547", "2021",
            "FEMA's two-page guide to including pets in the family's emergency plan: a safe place to take them, a "
            "buddy system, records and a microchip, and what to put in a pet's emergency kit."),
    govinfo("ready", "fema_tornado_2018", "Be Prepared for a Tornado (FEMA, 2018)", "Tornadoes", FEMA,
            "GOVPUB-HS5_100-PURL-gpo173190", "2018-03",
            "FEMA's two-page sheet (V-1010, March 2018): what tornadoes are, where to shelter under a tornado "
            "warning, and how to stay safe before, during and after one."),
    govinfo("ready", "fema_earthquake_checklist_2023", "Earthquake Safety Checklist (FEMA B-526, 2023)",
            "Earthquakes", FEMA, "GOVPUB-HS5_100-PURL-gpo252214", "2023-10",
            "FEMA's earthquake checklist (B-526, October 2023): important numbers and meeting places, supplies, "
            "making the home safer, turning off gas, water and electricity, and what to do during and after an "
            "earthquake."),
    govinfo("ready", "fema_protect_home_flood_2003", "Protecting Your Home from Flood Damage: Mitigation Ideas for "
            "Reducing Flood Loss (FEMA Region III, 2003)", "Floods", "FEMA Region III", "GOVPUB-HS5_100-PURL-LPS73856",
            "2003-11",
            "FEMA's booklet on protecting a home from flood damage: the National Flood Insurance Program and "
            "building in the floodplain, flood insurance, building permits, selecting a contractor, "
            "water-resistant building materials, and tips for repairing a flood-damaged house.",
            newer="Published in 2003: check FloodSmart.gov and your local floodplain office for today's rules."),
    govinfo("ready", "fema_rebuilding_after_wildfire_2020", "Rebuilding After a Wildfire (FEMA, 2020)", "Wildfire "
            "recovery", FEMA + ", Federal Insurance and Mitigation Administration", "GOVPUB-HS5_100-PURL-gpo194519",
            "2020",
            "FEMA's four pages on returning to and rebuilding a fire-damaged home."),
    govinfo("ready", "fema_help_after_disaster_2008", "Help After a Disaster: Applicant's Guide to the Individuals "
            "& Households Program (FEMA 545, 2008)", "Disaster assistance", FEMA, "GOVPUB-HS5_100-PURL-LPS113786",
            "2008-07",
            "FEMA's guide for disaster survivors applying for its Individuals and Households Program (July 2008): "
            "the types of assistance, your civil rights, the assistance process step by step, and who is "
            "eligible.", newer="Published in 2008: the program's rules and amounts have changed; apply and check "
                               "today's rules at DisasterAssistance.gov or 1-800-621-3362."),
    govinfo("ready", "usfa_fire_safety_older_adults_2018", "Fire Safety for Older Adults (US Fire Administration, "
            "2018)", "Home fire safety", USFA, "GOVPUB-HS5_200-PURL-gpo119393", "2018-10",
            "The US Fire Administration's guide (FA-221, October 2018): why the risk of dying in a home fire grows "
            "with age, smoke alarms (with devices for people with hearing loss), escape plans, and preventing "
            "fires from cooking, heating, smoking, electricity and medical oxygen."),
    govinfo("ready", "usfa_fire_safety_disabilities_2020", "Fire Safety for People with Disabilities (US Fire "
            "Administration, 2020)", "Home fire safety", USFA, "GOVPUB-HS5_200-PURL-gpo153049", "2020",
            "The US Fire Administration's one-page guide for people with physical and mental disabilities: smoke "
            "alarms (with vibrating pads or strobe lights for deaf and hard of hearing people), and planning an "
            "escape around your abilities."),
    govinfo("ready", "usfa_electrical_fire_safety_2015", "Electrical Fire Safety (US Fire Administration, 2015)",
            "Home fire safety", USFA, "GOVPUB-HS5_200-PURL-gpo188257", "2015",
            "The US Fire Administration's two pages of electrical safety tips: plugging appliances straight into "
            "the wall, extension cords, light bulbs of the right wattage, cords and outlets."),
    govinfo("ready", "usfa_wildfire_evacuation_2020", "Wildfire Evacuation (US Fire Administration, 2020)",
            "Wildfires", USFA, "GOVPUB-HS5_200-PURL-gpo142565", "2020",
            "The US Fire Administration's one page of tips for evacuating safely from a wildfire: leave at once "
            "when told, stay informed, and know your community's evacuation plan and two ways out."),
    govinfo("ready", "samhsa_trouble_coping_after_disaster_2007", "Having Trouble Coping After a Disaster? There Is "
            "Hope (SAMHSA, 2007)", "Coping after a disaster", "Substance Abuse and Mental Health Services "
            "Administration (SAMHSA)", "GOVPUB-HE20_400-PURL-gpo13214", "2007",
            "SAMHSA's two-page leaflet on the problems that can follow a traumatic event (sleep, eating, worry, "
            "anger, pulling away from people) and when and where to ask for help.",
            newer="Today's help line for anyone distressed by a disaster is the Disaster Distress Helpline: call or "
                  "text 1-800-985-5990."),
]

# ---------------------------------------------------------------------- mental health and wellbeing
SAMHSA = "Substance Abuse and Mental Health Services Administration (SAMHSA), US Department of Health and Human Services"
SAMHSA_PD = "SAMHSA's own notice says the publication is in the public domain and asks that it not be sold."
OSG = "Office of the US Surgeon General, US Department of Health and Human Services"
CMS = "Centers for Medicare & Medicaid Services (CMS), US Department of Health and Human Services"
MEDICARE_PUBS = "https://www.medicare.gov/publications"
MIND = [
    official("mind", "cms_medicare_mental_health_benefits", "Medicare & Your Mental Health Benefits (CMS "
             "publication 10184)", "Mental health care and Medicare", CMS,
             "https://www.medicare.gov/publications/10184-medicare-and-your-mental-health-benefits.pdf",
             MEDICARE_PUBS, "",
             "Medicare's official booklet on mental health benefits: who is eligible, what is covered (outpatient "
             "and inpatient mental health care, prescription drugs and more), and where to get help. The builder "
             "reads the current edition each time Medicare changes it."),
    govinfo("mind", "osg_workplace_mental_health_2022", "The U.S. Surgeon General's Framework for Workplace Mental "
            "Health & Well-Being (2022)", "Mental health at work", OSG, "GOVPUB-HE20-PURL-gpo188872", "2022",
            "The Surgeon General's framework of five essentials for mental health and well-being at work: "
            "protection from harm, connection and community, work-life harmony, mattering at work, and "
            "opportunity for growth, with practice examples."),
    govinfo("mind", "osg_facing_addiction_report_2016", "Facing Addiction in America: The Surgeon General's Report "
            "on Alcohol, Drugs, and Health (2016)", "Addiction", OSG + " and SAMHSA", "GOVPUB-HE20-PURL-gpo75951",
            "2016",
            "The first Surgeon General's report on substance use (413 pages): the neurobiology of addiction, "
            "prevention, treatment, recovery, health care systems and substance use, and a vision for the future. "
            "Its figures, some adapted with permission from copyrighted articles, are not copied (only their "
            "captions as text)."),
    govinfo("mind", "osg_facing_addiction_opioids_2018", "Facing Addiction in America: The Surgeon General's "
            "Spotlight on Opioids (2018)", "Opioids and addiction", OSG, "GOVPUB-HE20-PURL-gpo122832", "2018",
            "The Surgeon General's 2018 spotlight on the opioid crisis: what opioid misuse and opioid use disorder "
            "are, treatment and the medications for it, and what families, communities and others can do."),
    govinfo("mind", "samhsa_helping_loved_one_suicidal_2021", "Helping Your Loved One Who Is Suicidal: A Guide "
            "for Family and Friends (SAMHSA, 2021)", "Suicide prevention", SAMHSA, "GOVPUB-HE20_400-PURL-gpo153315",
            "2021",
            "SAMHSA's guide for the family and friends of someone who may be suicidal: the warning signs, what to "
            "do when they are urgent, how to get your loved one connected to mental health care, and taking care "
            "of yourself.", newer=f"{SAMHSA_PD} The Lifeline it names is now 988 (call or text)."),
    govinfo("mind", "samhsa_coping_with_grief_2017", "Tips for Survivors: Coping with Grief After a Disaster or "
            "Traumatic Event (SAMHSA, 2017)", "Grief", SAMHSA, "GOVPUB-HE20_400-PURL-gpo108756", "2017",
            "SAMHSA's tip sheet on grief: what it is, the grieving process, what happens when grief is "
            "interrupted or becomes complicated or traumatic, and ways to cope and to get help."),
    govinfo("mind", "samhsa_how_to_deal_with_grief_2008", "How to Deal with Grief (SAMHSA, 2008)", "Grief", SAMHSA,
            "GOVPUB-HE20_400-PURL-gpo12616", "2008",
            "SAMHSA's two pages on grief: how grief differs from depression, the signs of depression, and how to "
            "cope with grief."),
    govinfo("mind", "samhsa_traumatic_event_stress_2007", "Tips for Survivors of a Traumatic Event: Managing Your "
            "Stress (SAMHSA, 2007)", "Stress after trauma", SAMHSA, "GOVPUB-HE20_400-PURL-gpo13031", "2007",
            "SAMHSA's tip sheet for people who have lived through a natural disaster, mass violence or terrorism: "
            "the signs of stress, how to relieve it, and when to get help."),
    govinfo("mind", "samhsa_talking_to_children_trauma_2007", "Tips for Talking to Children and Youth After "
            "Traumatic Events: A Guide for Parents and Educators (SAMHSA, 2007)", "Children after trauma", SAMHSA,
            "GOVPUB-HE20_400-PURL-gpo13034", "2007",
            "SAMHSA's guide to how children respond to trauma at different ages (preschool, early childhood, "
            "adolescence) and how parents and teachers can recognise problems and help."),
    govinfo("mind", "samhsa_stress_disease_outbreaks_2014", "Coping with Stress During Infectious Disease "
            "Outbreaks (SAMHSA, 2014)", "Stress", SAMHSA, "GOVPUB-HE20_400-PURL-gpo135625", "2014",
            "SAMHSA's tip sheet on the stress that news of an outbreak can bring: what to know, the signs of "
            "stress, ways to cope, and where to get help."),
    govinfo("mind", "samhsa_healthier_life_wellness_2016", "Creating a Healthier Life: A Step-by-Step Guide to "
            "Wellness (SAMHSA, 2016)", "Wellness", SAMHSA, "GOVPUB-HE20_400-PURL-gpo119300", "2016",
            "SAMHSA's guide to wellness in eight dimensions (emotional, physical, occupational, intellectual, "
            "financial, social, environmental and spiritual) and steps for working on each."),
    govinfo("mind", "samhsa_recovering_mental_health_2005", "Recovering Your Mental Health: A Self-Help Guide "
            "(SAMHSA, 2005)", "Mental health recovery", SAMHSA + " (prepared by Mary Ellen Copeland)",
            "GOVPUB-HE20_400-PURL-LPS80208", "2005",
            "SAMHSA's self-help guide (SMA-3504) for people working on their own recovery: taking a look at "
            "yourself, what to do if symptoms are very serious, and the things people have found helpful.",
            newer=SAMHSA_PD),
    govinfo("mind", "samhsa_understanding_depression_caregiver_2017", "Understanding Depression: Get the Facts, "
            "for Caregivers (SAMHSA, 2017)", "Depression", SAMHSA, "GOVPUB-HE20_400-PURL-gpo160318", "2017",
            "SAMHSA's fact sheet for parents and caregivers of a youth or young adult with depression: what the "
            "diagnosis means, treatment and recovery, and how to support them."),
    govinfo("mind", "samhsa_understanding_anxiety_caregiver_2017", "Understanding Anxiety Disorders: Get the "
            "Facts, for Caregivers (SAMHSA, 2017)", "Anxiety", SAMHSA, "GOVPUB-HE20_400-PURL-gpo160302", "2017",
            "SAMHSA's fact sheet for parents and caregivers of a youth or young adult with an anxiety disorder: "
            "what the diagnosis means, treatment and recovery, and how to support them."),
    govinfo("mind", "samhsa_talk_to_someone_2010", "Should You Talk to Someone About a Drug, Alcohol, or Mental "
            "Health Problem? (SAMHSA, 2010)", "Getting help", SAMHSA, "GOVPUB-HE20_400-PURL-gpo12240", "2010",
            "SAMHSA's four-page leaflet of questions to help you decide whether you need help with substance use, "
            "a mental health problem or both, and about getting treatment."),
    govinfo("mind", "samhsa_substance_treatment_families_2004", "What Is Substance Abuse Treatment? A Booklet for "
            "Families (SAMHSA, 2004)", "Addiction treatment", SAMHSA, "GOVPUB-HE20_400-PURL-LPS107366", "2004",
            "SAMHSA's booklet for families of someone with an alcohol or drug problem: what treatment is, its "
            "kinds and stages, and how families can take part and get help for themselves.",
            newer=f"Published in 2004. {SAMHSA_PD} SAMHSA's National Helpline is 1-800-662-4357."),
    govinfo("mind", "samhsa_mat_opioids_families_2011", "Medication-Assisted Treatment for Opioid Addiction: "
            "Facts for Families and Friends (SAMHSA, 2011)", "Addiction treatment", SAMHSA,
            "GOVPUB-HE20_400-PURL-gpo124269", "2011",
            "SAMHSA's booklet for families and friends: what opioids and opioid addiction are, the medications "
            "used to treat it (methadone, buprenorphine, naltrexone), and what to expect in treatment.",
            newer=f"Published in 2011. {SAMHSA_PD}"),
]

# ---------------------------------------------------------------------- aging and end of life
NIA = "National Institute on Aging (NIA), National Institutes of Health"
AGING = [
    official("aging", "cms_medicare_hospice_benefits", "Medicare Hospice Benefits (CMS publication 02154)",
             "Hospice care", CMS, "https://www.medicare.gov/publications/02154-medicare-hospice-benefits.pdf",
             MEDICARE_PUBS, "",
             "Medicare's official booklet on hospice: who is eligible, what services hospice care includes, how "
             "to find a hospice, and what Medicare pays. The builder reads the current edition each time Medicare "
             "changes it."),
    official("aging", "cms_medicare_home_health_care", "Medicare & Home Health Care (CMS publication 10969)",
             "Home health care", CMS, "https://www.medicare.gov/publications/10969-medicare-and-home-health-care.pdf",
             MEDICARE_PUBS, "",
             "Medicare's official booklet on home health care: who is eligible, what services are covered, how to "
             "find and compare home health agencies, and your rights."),
    official("aging", "cms_your_medicare_benefits", "Your Medicare Benefits (CMS publication 10116)",
             "Medicare coverage", CMS, "https://www.medicare.gov/publications/10116-your-medicare-benefits.pdf",
             MEDICARE_PUBS, "",
             "Medicare's official booklet on the items and services Original Medicare covers, in alphabetical "
             "order, with what you pay."),
    official("aging", "cms_medicare_drug_coverage", "Your Guide to Medicare Drug Coverage (CMS publication 11109)",
             "Prescription drug coverage", CMS,
             "https://www.medicare.gov/publications/11109-your-guide-to-medicare-prescription-drug-coverage.pdf",
             MEDICARE_PUBS, "",
             "Medicare's official booklet on drug coverage: how it works, your choices, and how to get Extra Help "
             "if you have limited income and resources."),
    govinfo("aging", "cms_discharge_planning_checklist_2019", "Your Discharge Planning Checklist: For Patients and "
            "Their Caregivers Preparing to Leave a Hospital, Nursing Home, or Other Care Setting (CMS, 2019)",
            "Leaving the hospital", CMS, "GOVPUB-HE22-PURL-gpo154162", "2019",
            "Medicare's checklist for patients and their caregivers to use early and often during a stay, to plan "
            "a safe discharge home or to another care setting."),
    govinfo("aging", "cms_medicare_rights_protections_2018", "Medicare Rights & Protections (CMS, 2018)",
            "Medicare rights", CMS, "GOVPUB-HE22-PURL-gpo173199", "2018",
            "Medicare's booklet on your rights: those of everyone with Medicare, in Original Medicare, in a "
            "Medicare Advantage or other plan, and in a drug plan, and the Medicare Beneficiary Ombudsman.",
            newer="Published in 2018: check Medicare.gov or 1-800-MEDICARE for today's rules."),
    govinfo("aging", "nia_caring_alzheimers_2019", "Caring for a Person with Alzheimer's Disease: Your Easy-to-Use "
            "Guide from the National Institute on Aging (2019)", "Alzheimer's caregiving", NIA,
            "GOVPUB-HE20_3850-PURL-gpo159452", "2019",
            "NIA's 106-page caregiver's guide: understanding Alzheimer's disease and its stages, how it changes "
            "people and strategies for coping, helping family members understand, planning ahead (health, legal "
            "and financial), keeping the person safe, everyday care, and caring for yourself."),
    govinfo("aging", "nia_home_safety_alzheimers_2006", "Home Safety for People with Alzheimer's Disease (NIA, 2006)",
            "Alzheimer's caregiving", NIA, "GOVPUB-HE20_3850-PURL-LPS70328", "2006",
            "NIA's booklet for people caring at home for someone with Alzheimer's disease: making the home safer "
            "room by room, driving and the warning signs of unsafe driving, natural disaster safety, and who would "
            "care for the person if something happened to you.", newer="Published in 2006."),
    govinfo("aging", "nia_legal_financial_dementia_2020", "Legal and Financial Planning for People Living with "
            "Dementia (NIA, 2020)", "Planning ahead", NIA + ", Alzheimer's and Related Dementias Education and "
            "Referral Center", "GOVPUB-HE20_3850-PURL-gpo156735", "2020",
            "NIA's fact sheet on planning ahead after a diagnosis of dementia: why it matters, how to do it (legal "
            "and financial documents), where to get help, and things to consider."),
    govinfo("aging", "nia_frontotemporal_disorders_2012", "Frontotemporal Disorders: Information for Patients, "
            "Families, and Caregivers (NIA, 2012)", "Dementia", NIA, "GOVPUB-HE20_3850-PURL-gpo21715", "2012",
            "NIA's booklet on frontotemporal disorders: the basics, the types (including primary progressive "
            "aphasia and movement disorders), causes, diagnosis, common symptoms, treatment and management, and "
            "help for caregivers."),
    govinfo("aging", "nia_talking_with_your_doctor_2021", "Talking with Your Doctor: A Guide for Older People "
            "(NIA, 2021)", "Talking with doctors", NIA, "GOVPUB-HE20_3850-PURL-gpo156646", "2021",
            "NIA's guide: choosing a doctor you can talk with, preparing for an appointment, giving and getting "
            "information, making decisions with your doctor, talking about clinical trials, talking to "
            "specialists and hospital staff, and difficult but necessary conversations."),
    govinfo("aging", "nia_long_distance_caregiving_2010", "So Far Away: Twenty Questions and Answers About "
            "Long-Distance Caregiving (NIA, 2010)", "Caregiving", NIA, "GOVPUB-HE20_3850-PURL-gpo20459", "2010-08",
            "NIA's booklet for people who care for a relative who lives far away: getting started, things you can "
            "do, finding more help, support for caregivers, and points to remember."),
    govinfo("aging", "nia_exercise_physical_activity_2018", "Exercise & Physical Activity: Your Everyday Guide "
            "from the National Institute on Aging (2018)", "Exercise for older adults", NIA,
            "GOVPUB-HE20_3850-PURL-gpo124822", "2018",
            "NIA's book on staying active: why physical activity matters, the four kinds of exercise (endurance, "
            "strength, balance and flexibility), finding your starting point, setting goals and writing a plan, "
            "and exercises to try."),
    govinfo("aging", "nia_whats_on_your_plate_2019", "What's on Your Plate? Smart Food Choices for Healthy Aging "
            "(NIA, 2019)", "Eating well", NIA, "GOVPUB-HE20_3850-PURL-gpo156668", "2019",
            "NIA's guide to healthy eating as you age: healthy eating patterns, important nutrients, food "
            "shopping and saving on the cost, keeping food safe, sample menus and recipes, and roadblocks to "
            "healthy eating."),
    govinfo("aging", "nia_loneliness_social_isolation_2020", "Understanding Loneliness and Social Isolation: How "
            "to Stay Connected (NIA, 2020)", "Loneliness", NIA, "GOVPUB-HE20-PURL-gpo160004", "2020",
            "NIA's booklet on loneliness and social isolation in older age: how they affect health and well-being, "
            "and ways to stay connected, with words to know and resources."),
    govinfo("aging", "samhsa_older_adults_after_disasters_2019", "Helping Older Adults After Disasters: A Guide to "
            "Providing Support (SAMHSA, 2019)", "Older adults and disasters", SAMHSA,
            "GOVPUB-HE20_400-PURL-gpo135847", "2019",
            "SAMHSA's guide to disaster recovery in older age: common reactions and the signs that more help is "
            "needed, and how to work with and support older adults after a disaster."),
]

# ---------------------------------------------------------------------- veterans
VA = "US Department of Veterans Affairs (VA)"
NCPTSD = VA + ", National Center for PTSD"
VETERANS = [
    govinfo("veterans", "va_tap_va_benefits_participant_guide_2018", "VA Benefits I and II: Participant Guide "
            "(Transition Assistance Program, VA, 2018)", "Leaving the military", VA, "GOVPUB-VA-PURL-gpo106493",
            "2018",
            "The participant guide of the VA's Benefits I and II course, taught to service members in the "
            "Transition Assistance Program before they leave the military: an overview of the VA, key resources, "
            "and VA health care, disability compensation, education, vocational rehabilitation and employment, "
            "home loans, life insurance, housing help, burial and the other benefits, with how to apply.",
            newer="Version 1.1 of 2018: rules and rates change (the PACT Act of 2022 added toxic-exposure "
                  "benefits); check VA.gov."),
    govinfo("veterans", "va_health_benefits_guide_2012", "Veterans Health Benefits Guide (VA, 2012)", "VA health "
            "care", VA, "GOVPUB-VA-PURL-gpo46892", "2012",
            "The VA's guide to its health care: the nationwide system and the medical benefits package, "
            "eligibility and enrolment, the services offered, and what veterans pay.",
            newer="Published in 2012: eligibility, copays and programs have changed; check VA.gov or call "
                  "1-877-222-8387."),
    govinfo("veterans", "va_mental_health_services_guide_2011", "Guide to VA Mental Health Services for Veterans & "
            "Families (VA, 2011)", "Mental health care", VA + ", South Central Mental Illness Research, Education "
            "and Clinical Center", "GOVPUB-VA-PURL-gpo71628", "2011",
            "A consumer guide to the mental health services the VA offers veterans and their families and how to "
            "get them.", newer="Published in 2011: check VA.gov for today's services."),
    govinfo("veterans", "ncptsd_understanding_ptsd_treatment_2019", "Understanding PTSD and PTSD Treatment "
            "(National Center for PTSD, 2019)", "PTSD", NCPTSD, "GOVPUB-VA-PURL-gpo123944", "2019-05",
            "The National Center for PTSD's booklet: what PTSD is, what can cause it, its symptoms, how to know "
            "whether you have it, why to get treatment, common questions about treatment, what happens in it, and "
            "where to get help."),
    govinfo("veterans", "ncptsd_ptsd_family_friends_2019", "Understanding PTSD: A Guide for Family and Friends "
            "(National Center for PTSD, 2019)", "PTSD", NCPTSD, "GOVPUB-VA-PURL-gpo124742", "2019-05",
            "The National Center for PTSD's booklet for the people close to someone with PTSD: learning about "
            "PTSD, supporting and communicating with your loved one, and taking care of yourself."),
    govinfo("veterans", "ncptsd_ptsd_and_aging_2019", "Understanding PTSD and Aging (National Center for PTSD, "
            "2019)", "PTSD", NCPTSD, "GOVPUB-VA-PURL-gpo132202", "2019-09",
            "The National Center for PTSD's booklet on PTSD in later life: what PTSD is, its causes, signs and "
            "symptoms, how aging can affect it, and treatment."),
    govinfo("veterans", "ncptsd_returning_war_zone_personnel_2010", "Returning from the War Zone: A Guide for "
            "Military Personnel (National Center for PTSD, 2010)", "Coming home", NCPTSD, "GOVPUB-VA-PURL-gpo539",
            "2010-09",
            "The National Center for PTSD's guide for service members coming home from deployment: reunion with "
            "family, common stress reactions, and when and where to get help."),
    govinfo("veterans", "ncptsd_returning_war_zone_families_2010", "Returning from the War Zone: A Guide for "
            "Families of Military Members (National Center for PTSD, 2010)", "Coming home", NCPTSD,
            "GOVPUB-VA-PURL-gpo541", "2010-09",
            "The National Center for PTSD's companion guide for families: why a reunion can be both happy and "
            "stressful, the reactions to expect, and how to help and get help."),
    govinfo("veterans", "va_talk_to_child_suicide_attempt_2016", "How to Talk to a Child About a Suicide Attempt in "
            "Your Family (VA, 2016)", "Suicide prevention", VA + ", Rocky Mountain MIRECC for Suicide Prevention",
            "GOVPUB-VA-PURL-gpo82596", "2016",
            "The VA's guides for families on talking with children about a suicide attempt in the family, for "
            "families of preschoolers, school-age children and teenagers."),
    govinfo("veterans", "va_military_sexual_trauma_2016", "You're Not Alone in Recovering from Military Sexual "
            "Trauma (VA, 2016)", "Military sexual trauma", VA + ", Veterans Health Administration",
            "GOVPUB-VA-PURL-gpo135504", "2016",
            "The VA's leaflet on military sexual trauma: what it is, how it can affect people, and the free care "
            "the VA offers."),
    govinfo("veterans", "va_disabled_veterans_benefits_summary_2012", "Summary of VA Benefits for Disabled Veterans "
            "(VA, 2012)", "Disability compensation", VA + ", Veterans Benefits Administration",
            "GOVPUB-VA-PURL-gpo54049", "2012-11",
            "The VA's summary of tax-free benefits for veterans with a service-connected disability and their "
            "dependents: disability compensation and the other benefits that go with it.",
            newer="Published in 2012: rates and rules have changed; check VA.gov."),
    govinfo("veterans", "va_pension_benefits_summary_2012", "Summary of VA Pension Benefits: Supplemental Income for "
            "Wartime Veterans (VA, 2012)", "VA pension", VA + ", Veterans Benefits Administration",
            "GOVPUB-VA-PURL-gpo69264", "2012-11",
            "The VA's summary of its pension for wartime veterans with limited income: who may qualify, the income "
            "and net worth limits, and how the payment is worked out.",
            newer="Published in 2012: the limits change every year; check VA.gov."),
    govinfo("veterans", "va_aid_and_attendance_2015", "Enhanced or Special Monthly Pension (Aid and Attendance or "
            "Housebound) (VA, 2015)", "VA pension", VA, "GOVPUB-VA-PURL-gpo74179", "2015",
            "The VA's two-page fact sheet on the extra pension for veterans and survivors who need the aid and "
            "attendance of another person or are housebound.",
            newer="Published in 2015: check VA.gov for today's rules and rates."),
    govinfo("veterans", "va_caregiver_support_services_2025", "Program of General Caregiver Support Services: Fact "
            "Sheet (VA, 2025)", "Caregivers", VA + ", Caregiver Support Program", "GOVPUB-VA-PURL-gpo254834",
            "2025-10",
            "The VA's fact sheet (October 2025) on support for family caregivers of veterans: what the general "
            "caregiver support services offer and how to reach the Caregiver Support Program (Caregiver Support "
            "Line 1-855-260-3274)."),
]

# ---------------------------------------------------------------------- genealogy
NARA = "National Archives and Records Administration (NARA)"
GENEALOGY = [
    official("gen", "census_measuring_america_2002", "Measuring America: The Decennial Censuses From 1790 to 2000 "
             "(Census Bureau, 2002)", "History of the census", "US Census Bureau, US Department of Commerce",
             "https://www2.census.gov/library/publications/2002/dec/pol_02-ma.pdf",
             "https://www.census.gov/library/publications/2002/dec/pol_02-ma.html", "2002-09",
             "The Census Bureau's history of every census from 1790 to 2000 (POL/02-MA, September 2002): for each "
             "census, its background and the questions asked (with the forms and instructions), so a family "
             "historian can see what each census can tell about an ancestor."),
    govinfo("gen", "nara_citing_records_2010", "Citing Records in the National Archives of the United States "
            "(NARA General Information Leaflet 17, 2010)", "Citing records", NARA, "GOVPUB-AE-PURL-gpo195475",
            "2010",
            "NARA's leaflet on citing its records: the elements of a citation, and guidelines for textual, "
            "microform, non-textual and electronic records, records in affiliated archives, and documents "
            "digitised on NARA's web site."),
    govinfo("gen", "nara_land_entry_files_2009", "Research in the Land Entry Files of the General Land Office: "
            "Record Group 49 (NARA Reference Information Paper 114, 2009)", "Land records", NARA + " (compiled by "
            "Kenneth Hawkins)", "GOVPUB-AE-PURL-gpo142072", "2009",
            "NARA's guide to the land entry case files of the General Land Office (more than ten million "
            "transfers of public land to private owners): how the land was surveyed, the kinds of land entries, "
            "and how to find and order an ancestor's file."),
]

# ---------------------------------------------------------------------- CDC's books (pools; relationships)
CDC = "Centers for Disease Control and Prevention (CDC), US Department of Health and Human Services"
CDC_VP = CDC + ", Division of Violence Prevention"
CDC_CREDIT = ("CDC asks that its materials be credited and says that a copy does not imply its endorsement: this copy "
              "is not endorsed by CDC, HHS or the US Government.")
POOLS += [
    govinfo("pools", "cdc_storing_pool_chemicals_2014", "Storing Pool Chemicals Safely (CDC, 2014)", "Pool "
            "chemicals", CDC, "GOVPUB-HE20_7000-PURL-gpo123784", "2014",
            "CDC's one-page checklist (CS232164-A) for storing pool chemicals safely: training, reading the whole "
            "label or safety data sheet, the pool's emergency chemical spill plan, safety equipment, and following "
            "the label's storage directions.", newer=CDC_CREDIT),
    govinfo("pools", "cdc_using_pool_chemicals_2014", "Using Pool Chemicals Safely (CDC, 2014)", "Pool chemicals",
            CDC, "GOVPUB-HE20_7000-PURL-gpo123790", "2014",
            "CDC's one-page checklist (CS232164-C) for using pool chemicals safely: training, asking for help, "
            "reading the label or safety data sheet, the emergency spill plan, goggles, gloves and mask, and the "
            "product directions.", newer=CDC_CREDIT),
]

# ---------------------------------------------------------------------- communication and relationships
RELATE = [
    govinfo("relate", "osg_epidemic_loneliness_isolation_2023", "Our Epidemic of Loneliness and Isolation: The U.S. "
            "Surgeon General's Advisory on the Healing Effects of Social Connection and Community (2023)",
            "Loneliness and social connection", OSG, "GOVPUB-HE20-PURL-gpo212387", "2023",
            "The Surgeon General's advisory (82 pages): why social connection matters, what it is, whether it is "
            "declining, what makes people more or less connected and who is at highest risk, the effects of "
            "technology, how connection affects health, and a national strategy with recommendations for "
            "individuals, families, communities, workplaces and governments."),
    govinfo("relate", "osg_recipes_for_connection_2024", "Recipes for Connection: Inspiring Social Connection One "
            "Bite at a Time (Office of the Surgeon General, 2024)", "Social connection", OSG,
            "GOVPUB-HE20-PURL-gpo235634", "2024",
            "The Surgeon General's guide to bringing people together over food: ingredients for any gathering, "
            "making the invitation (with real examples), conversation prompts, and true stories of small and "
            "large gatherings that built connection."),
    govinfo("relate", "samhsa_speaking_out_for_yourself_2005", "Speaking Out for Yourself: A Self-Help Guide "
            "(SAMHSA, 2005)", "Speaking up for yourself", SAMHSA + " (prepared by Mary Ellen Copeland)",
            "GOVPUB-HE20_400-PURL-LPS122682", "2005",
            "SAMHSA's self-help guide (SMA-3719) to self-advocacy: steps to being an effective self-advocate, "
            "knowing your rights, addressing daily issues, and when others need to take over.", newer=SAMHSA_PD),
    govinfo("relate", "samhsa_making_keeping_friends_2005", "Making and Keeping Friends: A Self-Help Guide (SAMHSA, "
            "2005)", "Friendship", SAMHSA + " (prepared by Mary Ellen Copeland)", "GOVPUB-HE20_400-PURL-LPS122683",
            "2005",
            "SAMHSA's self-help guide (SMA-3716): making friends, keeping friendships strong, setting and honouring "
            "boundaries, resolving problems in relationships, and building the skills that help friendships.",
            newer=SAMHSA_PD),
    govinfo("relate", "samhsa_difference_a_friend_makes_2007", "What a Difference a Friend Makes (SAMHSA, 2007)",
            "Supporting a friend", SAMHSA, "GOVPUB-HE20_400-PURL-LPS82818", "2007",
            "SAMHSA's brochure for young adults on supporting a friend who lives with a mental illness: what "
            "mental health and mental illness are, recovery and support, myths and facts, and what you would do."),
    govinfo("relate", "cdc_understanding_ipv_2012", "Understanding Intimate Partner Violence: Fact Sheet (CDC, "
            "2012)", "Partner violence", CDC_VP, "GOVPUB-HE20_7000-PURL-gpo16817", "2012",
            "CDC's two-page fact sheet on intimate partner violence: what it is (physical and sexual violence, "
            "threats, and emotional abuse), how it affects health, who is at risk, and how it can be "
            "prevented.", newer=CDC_CREDIT),
    govinfo("relate", "cdc_dating_matters_2011", "Dating Matters: Strategies to Promote Healthy Teen Relationships "
            "(CDC, 2011)", "Healthy teen relationships", CDC_VP, "GOVPUB-HE20_7000-PURL-gpo15349", "2011",
            "CDC's two-page overview of teen dating violence (how common it is and its risk factors) and of Dating "
            "Matters, its community approach to stopping it before it starts.", newer=CDC_CREDIT),
    govinfo("relate", "cdc_preventing_bullying_2018", "Preventing Bullying (CDC, 2018)", "Bullying", CDC_VP,
            "GOVPUB-HE20_7000-PURL-gpo177207", "2018",
            "CDC's two-page fact sheet: what bullying is (physical, verbal, social and electronic), its "
            "consequences, and how it can be prevented.", newer=CDC_CREDIT),
    govinfo("relate", "cdc_preventing_ipv_lifespan_2017", "Preventing Intimate Partner Violence Across the "
            "Lifespan: A Technical Package of Programs, Policies, and Practices (CDC, 2017)", "Partner violence",
            CDC_VP, "GOVPUB-HE20_7000-PURL-gpo91182", "2017",
            "CDC's package of the strategies with the best evidence for preventing intimate partner violence, "
            "from teaching safe and healthy relationship skills and engaging influential adults and peers to "
            "supporting survivors, each with its approaches and the evidence for them.", newer=CDC_CREDIT),
    govinfo("relate", "cdc_essentials_for_childhood_2014", "Essentials for Childhood: Steps to Create Safe, Stable, "
            "and Nurturing Relationships and Environments (CDC, 2014)", "Families and children", CDC_VP,
            "GOVPUB-HE20_7000-PURL-gpo91964", "2014-08",
            "CDC's framework of steps communities can take so that every child has safe, stable, nurturing "
            "relationships and environments, to prevent child abuse and neglect.", newer=CDC_CREDIT),
]


# ====================================================================== the collection

BOOKS = {"car": CAR, "drive": DRIVE, "motor": MOTOR, "pools": POOLS, "recycle": RECYCLE, "ready": READY,
         "mind": MIND, "aging": AGING, "veterans": VETERANS, "gen": GENEALOGY, "relate": RELATE}
PDFS = [b for books in BOOKS.values() for b in books]
NEW_AREAS = [a for a in AREAS if AREAS[a][4]]          # the sections with a sign-up book (gpo:new:<area>)


def keys_of_word(word):
    """The keys of one section word (gpo-car: the car and driving books and the car sign-up book), in order."""
    areas = [a for a in AREAS if AREAS[a][0] == word]
    keys = [f"{PREFIX}:{b['name']}" for a in areas for b in BOOKS[a]]
    return keys + [f"{PREFIX}:new:{a}" for a in areas if a in NEW_AREAS]


def all_keys():
    """Every key of the module: every book, then the sign-up books."""
    return [f"{PREFIX}:{b['name']}" for b in PDFS] + [f"{PREFIX}:new:{a}" for a in NEW_AREAS]


WORDS = {"govinfo-fill": all_keys}
WORDS.update({w: (lambda w=w: keys_of_word(w)) for w in dict.fromkeys(AREAS[a][0] for a in AREAS)})

COLLECTION = K.Collection(PREFIX, CC.GROUP, pdfs=PDFS, words=WORDS, makers={"new": (new_book, new_sign)},
                          pieces={"new": lambda: list(NEW_AREAS)})

# The groups are the existing modules' own (their GROUPS add them to sources.GROUPS); none is new here.
GROUPS = {}

LICENCE_LINES = {
    "govinfo_fill_govinfo": "www.govinfo.gov (the US Government Publishing Office): its robots.txt allows "
                            "/content/pkg/ and /metadata/pkg/ (only /app/search/ and site admin pages are refused, "
                            "and no AI company's reader is named; checked 2026-11-22). The GOVPUB packages are "
                            "publications of US federal agencies (17 U.S.C. 105; the line checked on govinfo's "
                            "policies page at every build); each book was checked to name no co-publisher outside "
                            "the federal government and to print no copyright notice (2026-11-22). EPA "
                            "publications keep the EPA's own non-commercial terms (personal use), as recycling.py.",
    "govinfo_fill_agencies": "www.medicare.gov and www2.census.gov: robots.txt allows the PDFs read (checked "
                             "2026-11-22); works of the US government (17 U.S.C. 105).",
    "govinfo_fill_military": "archive.org (its robots.txt allows the files): US Army and Navy manuals, judged by "
                             "the release rule for military publications at every build (military_release.py) and "
                             "read whole, with parts about explosives, demolition, mines, grenades, booby traps "
                             "and sabotage left out (build_textbooks.NOT_FIELD_SAFE).",
    "govinfo_fill_signup": "api.govinfo.gov (GovInfo's search API): a sign-up entry; it needs the owner's own free "
                           "api.data.gov key in GOVINFO_API_KEY (never in the repository; sent only to "
                           "api.govinfo.gov in the X-Api-Key header). Sign up at https://api.data.gov/signup/.",
}

GI = f"{GOVINFO}/app/details/"
NOT_INCLUDED = [
    ("The Federal Depository Library Program's catalog (catalog.gpo.gov)", "It refuses programs (\"403\", even for "
     "robots.txt; checked 2026-11-22), so official copies were found through GovInfo's sitemaps and MODS records "
     "instead. Link-only. Index: https://catalog.gpo.gov/"),
    ("permanent.fdlp.gov (GPO's archive of agency web copies)", "Its robots.txt says \"Disallow: /\" to every program "
     "(checked 2026-11-22); not read. Index: https://permanent.fdlp.gov/"),
    ("NCBI Bookshelf copies of Surgeon General's reports and other HHS books", "Public domain when written by HHS, "
     "but www.ncbi.nlm.nih.gov answers programs with a reCAPTCHA check and ftp.ncbi.nlm.nih.gov's robots.txt refuses "
     "every program (checked 2026-11-22). Two Surgeon General's reports and the loneliness advisory are built from "
     "GovInfo instead. Link-only. Index: https://www.ncbi.nlm.nih.gov/books/"),
    ("EPA's National Service Center for Environmental Publications (nepis.epa.gov)", "Its robots.txt asks programs "
     "to come only between 01:00 and 10:45 UTC and one page every 10 seconds, its search is an interactive "
     "application, and the EPA's terms are non-commercial; not read in this pass. EPA's booklets kept by GovInfo are "
     "built instead (personal use). Index: https://nepis.epa.gov/"),
    ("GovInfo copies published together with organisations outside the federal government", "Not built, because "
     "the co-publisher may hold copyright: Repairing Your Flooded Home (FEMA and the American Red Cross, 2010), "
     "Helping Children Cope with Disaster (FEMA and the American Red Cross, 2004), Take Control in 1, 2, 3 for "
     "Caregivers (FEMA and the Rosalynn Carter Institute for Caregivers, 2024), Earthquake Safety at Home (FEMA "
     "P-530, prepared by the Applied Technology Council, with others' graphics), Driving When You Have Macular "
     "Degeneration (NHTSA and the American Optometric Association), DriveWell (NHTSA and the American Society on "
     "Aging) and What You Need to Know About Air Bags (Automotive Coalition for Traffic Safety). Link-only. Index: "
     f"{GI}GOVPUB-HS5_100-PURL-gpo2638"),
    ("GovInfo copies that hold others' copyrighted text", "Not built: End of Life: Helping with Comfort and Care "
     "(NIA, 2008: it reprints a page \"Copyright National Hospice and Palliative Care Organization, all rights "
     "reserved\"), SAMHSA's After an Attempt guides (first developed by the National Alliance on Mental Illness), "
     "the VA's Information and Support After a Suicide Attempt (2012, which includes NAMI's brochure), "
     "Hospitalization Happens (NIA, first produced by North Carolina's Division of Aging), and SAMHSA's Anger "
     "Management workbook and Helping Yourself Heal guides (their notices except material from copyrighted "
     f"sources). Link-only. Index: {GI}GOVPUB-HE20_3850-PURL-LPS91814"),
    ("Administration for Children and Families relationship and fatherhood briefs on GovInfo", "Healthy "
     "Relationships: Assess, Improve, Take Action (2019), Promoting Positive Coparenting Relationships (2019), "
     "Connected to Others Is a Good Place to Be (2020) and Navigating Seasons of Change (2024) were written by "
     "contractors (RTI International, the National Responsible Fatherhood Clearinghouse, PATH) and print no "
     "public-domain notice, so they are not built. Link-only. Index: https://www.acf.hhs.gov/ofa/programs/"
     "healthy-marriage"),
    ("NHTSA child car seat booklets on GovInfo (Are You Using It Right?, 2005; A Parent's Guide to Buying and Using "
     "Booster Seats, 2005)", "Their age and size advice is out of date (today's advice keeps children rear-facing "
     "longer), and the first asks to be copied without changes; not built. The current advice is NHTSA's car seat "
     "pages (they refuse programs). Link-only. Index: https://www.nhtsa.gov/vehicle-safety/car-seats-and-booster-"
     "seats"),
    ("NHTSA motorcycle rider and towing booklets, FMCSA consumer guides, CDC's Model Aquatic Health Code, CPSC's "
     "Pool Safely booklets and SSA's benefit booklets", "Not on GovInfo: its NHTSA class holds research notes on "
     "motorcycles but no rider or towing booklet, its FMCSA class two leaflets (built) and moving guides, its CDC "
     "class pool chemical sheets (built) but no Model Aquatic Health Code, its CPSC class the pool barrier "
     "guidelines (built), and its SSA class leaflets and reports but no current retirement, disability or "
     "survivors booklet (searched every GOVPUB package of those agencies, 2026-11-22). The Internet Archive has "
     "none either. Link-only. Index: https://www.ssa.gov/pubs/ and https://www.cdc.gov/model-aquatic-health-code/"),
    ("Newer editions of Federal Benefits for Veterans, Dependents and Survivors", "Neither GovInfo nor the Internet "
     "Archive has a copy newer than 2020 that may be read: the Internet Archive's 2003 to 2017 editions are "
     "lending-library scans (borrow only). The VA's Transition Assistance Program course guide, VA Benefits I and "
     "II (2018), is built. Index: https://department.va.gov/get-started/"),
    ("GovInfo copies whose text cannot be read aloud", "Compendium on Solid Waste Management by Vermicomposting "
     "(EPA, 1980: scanned pages without words) and two National Archives reference papers (Using Civilian Records "
     "for Genealogical Research, 2006; Records of Military Agencies Relating to African Americans, 2006), whose "
     f"text layers are garbled. Link-only. Index: {GI}GOVPUB-AE-PURL-LPS113951"),
    ("NIMH brochures on GovInfo and Medicare & You", "Already in the library from the agencies' own sites (NIMH's "
     "brochures: fam:nimh_publications; Medicare & You: gov_help.py); not repeated. Index: "
     "https://www.nimh.nih.gov/health/publications"),
    ("The Internet Archive's lending-library copies (Are You Ready? 2002 and 2004, Federal Benefits for Veterans "
     "2003 to 2017, NIA's exercise guides)", "Borrow-only scans for print-disabled readers (\"printdisabled\"), "
     "not open copies; not built. Index: https://archive.org/details/printdisabled"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
