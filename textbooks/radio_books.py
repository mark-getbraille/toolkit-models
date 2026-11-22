"""Radio communications for the reference library, in its own group "Reference, radio communications" (the owner's
request of 2026-11-22: a full section on ham and other two-way radio, and off-grid mesh and data radio, separate from
preparedness). Keys: radio (every book), radio:<name>.

What this module builds, in plain words, each IN FULL:
  - the FCC's rules: 47 CFR Part 97 (the amateur radio service), Part 95 (the personal radio services: GMRS, FRS,
    MURS, CB, and the others) and Part 80 (stations in the maritime services: marine VHF), from govinfo.gov's newest
    annual edition (the eCFR's own robots.txt shuts out programs from its full-text services);
  - Canada's Radiocommunication Regulations (SOR/96-484) from Justice Laws (non-US: Canadian rules; ISED's own
    RIC and RBR pages are canada.ca's non-commercial terms, so they are linked, not copied);
  - the NCVEC question pools for the US amateur licence exams, released into the public domain by the NCVEC
    Question Pool Committee: Technician (Element 2), General (Element 3) and Amateur Extra (Element 4), each the
    newest release with its errata, as published (every question, its four answers and the letter of the right one);
  - CISA's Auxiliary Communications Field Operations Guide (AUXFOG, 2016): the frequencies, channel plans, net
    procedures and forms that amateur and auxiliary operators use alongside emergency managers;
  - the National Weather Service's Weather Spotter's Field Guide (SKYWARN, 2011): how to spot and report severe
    storms safely;
  - Meshtastic's documentation (GPL-3.0, share-alike), every page: what Meshtastic and LoRa are, licence-free
    radio bands, devices and boards (LILYGO T-Beam and T-Echo, Heltec, RAK WisBlock and others), antennas,
    flashing and setting up a node, channels and encryption, device roles, battery and solar nodes, the apps,
    MQTT, and troubleshooting;
  - US military radio and antenna manuals from the Internet Archive (radio operating, antennas and wave
    propagation): FM 24-19 (personal use: it prints a restricted marking), MCRP 3-40.3C, TC 9-64 and TM 11-666. By the
    owner's rule (2026-11-22) a military publication found openly on archive.org is kept whether or not it prints
    Distribution Statement A, with a truthful notice (military_book); a copy that prints a restricted marking
    (Distribution B to F, FOUO, CUI, NOFORN, an export-control warning) is personal use only; one with a classified
    marking (Confidential, Secret) is kept only when it also shows that it was declassified or released; manuals are
    read whole (the owner's rule of 22 November 2026), so Tactical Radio Operations (FM 6-02.53, 2009) and its
    successor Techniques for Tactical Radios and Retransmission (ATP 6-02.53, July 2025) are here too; only parts about
    explosives, demolition, mines, grenades and booby traps are left out.
  - "Radio links to fetch yourself": a short book written here (CC0) of what could not be copied (the FCC's service
    pages, which refused the builder on 2026-11-22; ARRL, RSGB and
    QST material; AREDN's documentation, CC BY-NC-ND; Reticulum's manual, whose licence forbids use in AI training
    datasets; JS8Call's guide; Winlink and VARA; APRS; CHIRP; Briar; MeshCore; goTenna, Beartooth and the satellite
    messengers; the NTIA frequency chart; ISED's radio rules pages), with what each is and its address, for the owner
    to fetch himself with Program Downloader.

Already in the library and not repeated: the NOAA Weather Radio pages and the station and SAME code list by county
(emergency_prep.py, prep:nwr_guide and prep:nwr_stations), the old public-domain radio books (electronics_books.py,
elec:), and the Navy's NEETS modules on radio-frequency communications (elec: and sources.NEETS).

Safety: every book's notice carries RADIO_SAFETY: keep antennas far from power lines (contact can kill); do not
climb towers without training and fall protection; ground the station and disconnect antennas in lightning; follow
the FCC's RF exposure limits; transmit only where you are licensed or the service allows it, and never use
encryption on amateur frequencies.

Licences: the CFR and the FCC, CISA, NWS and military works are works of the US government (17 U.S.C. 105, the line
checked on govinfo.gov's policies page at every build; the NWS guide on weather.gov's disclaimer); the NCVEC pools'
public-domain release is checked on each pool's own page at every build; Meshtastic's licence on its repository's
LICENSE file at every build; Canada's regulations under the Reproduction of Federal Law Order. robots.txt of every
site read allows the pages and has no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/radio_books.py radio:ncvec_technician_pool --out build/textbooks
  python3 textbooks/radio_books.py --list radio
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "radio"
GROUPS = {GROUP: "Reference, radio communications"}

# The radio safety words (the same as packs/radio_packs.py, the kit and the manuals; the self-tests check).
RADIO_SAFETY = ("Radio safety: keep every antenna, mast and feed line far from power lines, more than the length of "
                "the antenna and mast from the nearest line (contact can kill). Never climb a tower without training "
                "and fall protection. Ground your station, and disconnect antennas when lightning is near. Follow the "
                "FCC's RF exposure limits and keep transmitting antennas away from people. Transmit only where you "
                "are licensed or the service allows it; encryption is not allowed on amateur frequencies; in an "
                "emergency, call 911 first.")
US_NOTICE = "A work of {who} (public domain in the US). " + RADIO_SAFETY

# ====================================================================== the rules (CFR and Canada)

# (name, title, subject, title number, volume, part, description). Title 47 volume 5 holds parts 80 to the end.
CFR_PARTS = [
    ("cfr_47_97_amateur", "Amateur Radio Service (47 CFR Part 97)", "Amateur radio rules", 47, 5, 97,
     "The FCC's rules for amateur (ham) radio: the basis and purpose of the service, licences and operator classes "
     "(Technician, General, Amateur Extra), call signs and station identification, the frequency bands and modes "
     "each class may use, power limits, prohibited transmissions (no business use, no music, no obscuring the "
     "meaning: no encryption), emergency communications, RACES, repeaters and auxiliary stations, remote control, "
     "digital and satellite operation, RF exposure, and volunteer examiners."),
    ("cfr_47_95_personal_radio", "Personal Radio Services: GMRS, FRS, MURS, CB and others (47 CFR Part 95)",
     "Personal radio rules", 47, 5, 95,
     "The FCC's rules for the personal radio services: the General Mobile Radio Service (GMRS, a licence for you and "
     "your family, repeaters allowed), the Family Radio Service (FRS, no licence), the Multi-Use Radio Service "
     "(MURS, no licence), the Citizens Band (CB) service, and the other personal services (wireless medical "
     "telemetry, radio control, personal locator beacons): channels, power, antennas, who may use them, and the "
     "rules for the radios themselves."),
    ("cfr_47_80_marine", "Stations in the Maritime Services: marine VHF (47 CFR Part 80)", "Marine radio rules",
     47, 5, 80,
     "The FCC's rules for marine radio: ship and coast stations, when a licence is needed, operating procedures, "
     "distress, urgency and safety calls (Channel 16 and DSC), the marine VHF channels, and the equipment rules."),
]


def cfr_book(name, work, cache=None, left_out=None, limit=None):
    """One CFR part (CFR_PARTS) as a book: sources.CFR's fields with this module's group and notice, built by
    build_textbooks.lawdoc_book from govinfo's newest annual edition."""
    import build_textbooks as B
    import sources
    _n, title, subject, t, vol, part, description = next(p for p in CFR_PARTS if p[0] == name)
    entry = sources._cfr(name, title, subject, t, vol, part, description, group=GROUP)
    entry["name"] = f"radio_{name}"
    entry["notice"] = ("The Code of Federal Regulations, a work of the US government (public domain); this copy is not "
                       "the official version. " + RADIO_SAFETY)
    book = B.lawdoc_book(entry, cache, left_out)
    if book is not None and limit:
        book.pages = book.pages[:limit]
    return book


def cfr_sign(name):
    """A CFR part's sign of change: the newest annual edition's address (a new edition changes it)."""
    import build_textbooks as B
    _n, _title, _subject, t, vol, part, _d = next(p for p in CFR_PARTS if p[0] == name)
    url, _text = B.govinfo_edition("cfr", dict(title=t, volume=vol, part=part))
    return K.sha(url)


def canada_book(name, work, cache=None, left_out=None, limit=None):
    """Canada's Radiocommunication Regulations (SOR/96-484) from Justice Laws, as sources._canada builds a law."""
    import build_textbooks as B
    import sources
    entry = sources._canada("radio_canada_radiocommunication_regulations", "Radiocommunication Regulations "
                            "(Canada, SOR/96-484)", "Radio rules (Canada)", "regulations/SOR-96-484",
                            "Canada's Radiocommunication Regulations: radio licences and certificates (including the "
                            "amateur radio operator certificate), exemptions from licensing for licence-free radios, "
                            "interference, equipment certification and the duties of radio operators.")
    entry["group"] = GROUP
    entry["notice"] = entry["notice"] + (" Non-US: these are Canada's rules (Innovation, Science and Economic "
                                         "Development Canada); in the US the FCC's rules apply. ") + RADIO_SAFETY
    book = B.lawdoc_book(entry, cache, left_out)
    if book is not None and limit:
        book.pages = book.pages[:limit]
    return book


def canada_sign(name):
    """The Canadian regulations' sign of change: the month (read again monthly; Justice Laws gives no cheap sign)."""
    import directory_sources as D
    return K.sha("SOR-96-484", D.month_token())


# ====================================================================== the NCVEC question pools (public domain)

NCVEC = "https://www.ncvec.org/index.php"
NCVEC_PD = "Public domain (released by the NCVEC Question Pool Committee)"
ALLOWED = {NCVEC_PD: "open", "GPL-3.0": "share-alike"}
NCVEC_TEXT = r"releases? .{0,120}?into (the )?public domain"
# (name, element, title, the pool's own page, the words its PDF's address must have)
POOLS = [
    ("ncvec_technician_pool", "Element 2", "Technician Class question pool (NCVEC, 2026 to 2030)",
     f"{NCVEC}/2026-2030-technician-question-pool", r"2026-2030.*Technician.*Pool.*\.pdf$"),
    ("ncvec_general_pool", "Element 3", "General Class question pool (NCVEC, 2023 to 2027)",
     f"{NCVEC}/2023-2027-general-question-pool-release", r"General.*Pool.*2023-2027.*\.pdf$"),
    ("ncvec_extra_pool", "Element 4", "Amateur Extra Class question pool (NCVEC, 2024 to 2028)",
     f"{NCVEC}/2024-2028-extra-class-question-pool-release", r"2024-2028.*Extra.*Pool.*\.pdf$"),
]


def first_pdf(page_text, base, pattern):
    """The FIRST PDF linked from a pool's page whose address matches pattern (the NCVEC lists the newest release,
    with all its errata, at the top; build_textbooks.newest_pdf would pick by the years in the name, which are the
    same for every release of one pool). "" when none."""
    import html
    import urllib.parse
    for href in re.findall(r'href="([^"]+\.pdf)"', page_text):
        url = urllib.parse.urljoin(base, html.unescape(href)).replace(" ", "%20")
        if re.search(pattern, urllib.parse.unquote(url), re.I):
            return url
    return ""


def pool_entry(name):
    """The PDF entry of one pool (without its PDF address, which pool_book finds on the page at build time)."""
    _n, element, title, page, _pattern = next(p for p in POOLS if p[0] == name)
    return dict(group=GROUP, name=f"radio_{name}", title=title, subject="Amateur radio licence exams",
                publisher="National Conference of Volunteer Examiner Coordinators (NCVEC), Question Pool Committee",
                country="United States", licence=NCVEC_PD, licence_url=page, licence_page=page,
                licence_text=NCVEC_TEXT, level="reference", page=page,
                description=f"The official question pool for the US amateur radio {title.split(' question')[0]} "
                            f"licence exam ({element}), as the NCVEC Question Pool Committee published it: the "
                            "syllabus by sub-element and topic, then every question with its four answer choices and "
                            "the letter of the right answer in brackets (with the FCC rule it comes from, where "
                            "given). The exam draws its questions from this pool. Diagrams are referred to by "
                            "number; they are drawings in a separate file on the NCVEC page.",
                notice="Released into the public domain by the NCVEC Question Pool Committee (its words are checked "
                       "on the pool's page at every build). Check the NCVEC page for errata issued after this copy. "
                       + RADIO_SAFETY)


def pool_book(name, work, cache=None, left_out=None, limit=None):
    """One question pool: its page must still say the pool is released into the public domain; its newest PDF (the
    first one listed) is read whole by build_textbooks.pdfdoc_book."""
    import build_textbooks as B
    _n, _element, title, page, pattern = next(p for p in POOLS if p[0] == name)
    if not B.allowed_by_robots(page, cache):
        left_out.append({"title": title, "reason": "The NCVEC site's robots.txt does not allow reading its page."})
        return None
    pdf = first_pdf(B.fetch(page, cache), page, pattern)
    if not pdf:
        left_out.append({"title": title, "reason": "The pool's page links no PDF of the pool."})
        return None
    entry = dict(pool_entry(name), pdf=pdf, published="", version=f"the release read on the NCVEC page ({pdf})")
    book = B.pdfdoc_book(entry, work, cache, left_out)
    if book is not None:
        book.version = entry["version"]
        if limit:
            book.pages = book.pages[:limit]
    return book


def pool_sign(name):
    """A pool's sign of change: the address of its newest PDF (errata make a new file name)."""
    import build_textbooks as B
    _n, _element, _title, page, pattern = next(p for p in POOLS if p[0] == name)
    return K.sha(first_pdf(B.fetch(page, None), page, pattern))


# ====================================================================== US government PDFs (AUXFOG, SKYWARN)

PDFS = [
    K.us_pdf(GROUP, name="cisa_auxfog_2016", title="Auxiliary Communications Field Operations Guide (AUXFOG, CISA, "
             "2016)", subject="Emergency communications (auxiliary and amateur)",
             publisher="US Department of Homeland Security, Office of Emergency Communications (now CISA)",
             archive="auxiliary-communications-field-operations-guide-auxfog-2016", published="2016",
             version="2016 edition (Internet Archive item auxiliary-communications-field-operations-guide-auxfog-2016)",
             description="The pocket guide for amateur and auxiliary radio operators who support emergency managers: "
                         "the amateur bands and band plans, national calling and simplex frequencies, the "
                         "interoperability channels, the phonetic alphabet, net procedures and message handling, "
                         "the ICS forms (ICS 205, 213, 214), digital modes, and antenna and power references.",
             notice=US_NOTICE.format(who="the US Department of Homeland Security (CISA)") + " Frequencies and "
                    "procedures change: check with your local emergency management and ARES or RACES group."),
    dict(K.us_pdf(GROUP, name="nws_weather_spotters_field_guide_2011", title="Weather Spotter's Field Guide: a guide "
                  "to being a SKYWARN spotter (National Weather Service, 2011)", subject="Storm spotting (SKYWARN)",
                  publisher="National Weather Service (NOAA)",
                  pdf="https://www.weather.gov/media/owlie/SGJune6-11(1).pdf",
                  page="https://www.weather.gov/skywarn/", published="2011-06", version="June 2011 edition",
                  description="The NWS guide for SKYWARN storm spotters: thunderstorm structure, what to look for "
                              "(wall clouds, funnel clouds, tornadoes, shelf clouds, hail, damaging winds, flooding), "
                              "how to report (what, where, when) and, first of all, staying safe while spotting.",
                  notice="From the National Weather Service (NOAA), whose web pages and publications are in the "
                         "public domain. Spotting is done from a safe place; never chase storms or drive into "
                         "flood water. " + RADIO_SAFETY),
         licence_page="https://www.weather.gov/disclaimer",
         licence_text=r"National Weather Service \(NWS\) Web pages are in the public domain"),
]

# ====================================================================== military radio and antenna manuals

# The owner's rule of 2026-11-22 for military publications (refined three times the same day), applied here in this
# module's own check (military_book), whatever the shared checks of build_textbooks say:
#   - published openly (here: the Internet Archive) and printing Distribution Statement A: kept, "approved for public
#     release" said;
#   - printing NO distribution statement: kept, with "published openly by the Internet Archive; its front pages print
#     no distribution statement" (never claimed approved for public release);
#   - printing a restricted marking (Distribution B to F, "distribution authorized to", FOUO, CUI, NOFORN, an
#     export-control warning) and found only on a non-government host such as archive.org: personal use only;
#   - printing a classified marking (Confidential, Secret, Top Secret): kept only when the text also shows it was
#     declassified or released; otherwise left out (leaked, never-released material stays out);
#   - parts about explosives, demolition, mines, grenades and booby traps (build_textbooks.NOT_FIELD_SAFE) are
#     always left out; weapons and tactics are kept as history (the owner's rule of 22 November 2026).
CLASSIFIED = re.compile(r"\b(TOP\s+SECRET|SECRET|CONFIDENTIAL)\b")             # capitals, as markings are printed
DECLASSIFIED = re.compile(r"declassified|unclassified|approved\s+for\s+(public\s+)?release|released\s+under|"
                          r"downgraded|declassification", re.I)
MILITARY = dict(group=GROUP, country="United States", licence=K.US_GOV, licence_url=K.US_GOV_URL,
                licence_page=K.GOVINFO_POLICY, licence_text=K.GOVINFO_TEXT, level="reference", military=True)


def _mil(name, title, subject, publisher, archive, published, description):
    """One military manual of the Internet Archive as an entry for military_book."""
    return dict(MILITARY, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                published=published, version=f"Internet Archive item {archive}", description=description,
                notice="A work of the US armed forces (public domain in the US). It is a military manual: its "
                       "frequencies, equipment and procedures are military ones and may be old; amateur and personal "
                       "radio rules are in the FCC's rules books. " + RADIO_SAFETY)


MILITARY_MANUALS = [
    _mil("army_fm_24_19_radio_operators_handbook", "Radio Operator's Handbook (FM 24-19)", "Radio operating",
         "Headquarters, Department of the Army", "milmanual-fm-24-19-radio-operators-handbook", "",
         "The Army radio operator's handbook: radiotelephone procedure, the phonetic alphabet and numbers, prowords, "
         "message format, nets and net control, authentication, radio checks and signal reports, and antenna and "
         "power basics."),
    _mil("usmc_mcrp_3_40_3c_antenna_handbook", "Antenna Handbook (MCRP 3-40.3C, 1999)", "Antennas",
         "US Marine Corps", "MCRP3-403C", "1999",
         "The Marine Corps antenna handbook: radio wave fundamentals and propagation, antenna basics (polarisation, "
         "gain, impedance, SWR), HF, VHF and UHF antennas, field-expedient antennas with their dimensions, siting, "
         "transmission lines and grounding."),
    _mil("army_tc_9_64_wave_propagation", "Communications-Electronics Fundamentals: Wave Propagation, Transmission "
         "Lines, and Antennas (TC 9-64, 2004)", "Antennas and propagation", "Headquarters, Department of the Army",
         "TC9-64", "2004",
         "A training circular on how radio waves travel, transmission lines (coaxial cable, impedance, standing "
         "waves) and antennas (dipoles, verticals, arrays, directional antennas), with worked explanations."),
    _mil("army_tm_11_666_antennas_propagation", "Antennas and Radio Propagation (TM 11-666, 1953)",
         "Antennas and propagation", "Department of the Army", "tm11666departmen00depa", "1953",
         "The classic Army technical manual on antennas and radio propagation: the ionosphere, ground and sky waves, "
         "half-wave and quarter-wave antennas, long wires, rhombics, arrays, feeding antennas and field-expedient "
         "repairs. Published in 1953: its equipment is old, but the physics has not changed."),
]

# Read whole under the owner's rule of 22 November 2026 (their titles name tactics, which the old rule never chose).
# Both print Distribution Statement A (read 2026-11-22); no part of either is about explosives.
MILITARY_MANUALS += [
    _mil("army_fm_6_02_53_tactical_radio_2009", "Tactical Radio Operations (FM 6-02.53, 2009)", "Radio operating",
         "Headquarters, Department of the Army", "FM6-02x53", "2009-08",
         "The Army's 2009 manual of tactical radios, read whole: applications, HF, VHF and UHF radios, single-channel "
         "satellite and airborne radios, antennas, communications security management, electronic protection, radio "
         "operating procedures, FM radio networks, single-channel radio principles, antenna selection, "
         "communications in unusual environments (jungle, desert, mountains, cold, cities), time conversion, "
         "compromise recovery, data and co-site interference."),
    _mil("army_atp_6_02_53_tactical_radios_2025", "Techniques for Tactical Radios and Retransmission (ATP 6-02.53, "
         "2025)", "Radio operating", "Headquarters, Department of the Army",
         "techniques-for-tactical-radios-and-retransmission-atp-6-02.53", "2025-07",
         "The successor of FM 6-02.53, read whole: tactical radio employment and planning, recognising and "
         "responding to electromagnetic attack, retransmission team training, waveforms, HF radio networks, time "
         "conversion, communications in adverse conditions, antenna selection and techniques, and radio platforms."),
]


def military_book(name, work, cache=None, left_out=None, limit=None):
    """One military manual (MILITARY_MANUALS) read whole by build_textbooks.pdfdoc_book, then judged by its own front
    pages under the owner's rule (see the comment above MILITARY): its notice says truthfully what it prints."""
    import build_textbooks as B
    entry = next(dict(m) for m in MILITARY_MANUALS if m["name"] == name)
    entry["distribution_a"] = False                  # this module's own check below, not the shared one
    entry["name"] = f"radio_{name}"
    book = B.pdfdoc_book(entry, work, cache, left_out)
    if book is None:
        return None
    front = B.front_text(os.path.join(work, f"{entry['name']}.pdf"))
    verdict = military_verdict(front)
    if verdict == "out":
        left_out.append({"title": entry["title"], "reason": "Its front pages print a classified marking with no sign "
                         "that it was declassified or released, so it is left out."})
        return None
    book.notice = military_notice(verdict, front) + " " + entry["notice"]
    book.personal_use = verdict == "restricted"
    kept = [p for p in book.pages if not B.NOT_FIELD_SAFE.search(p.title)]
    if len(kept) < len(book.pages):
        book.description += " Parts about explosives, demolition, mines or booby traps are left out."
    book.pages = kept[:limit] if limit else kept
    return book


def military_verdict(front):
    """"public" (Distribution Statement A printed), "none" (no statement), "restricted" (a restricted marking:
    personal use, as the copy is on a non-government host), "declassified" (a classified marking with a
    declassification or release marking) or "out" (a classified marking without one)."""
    import build_textbooks as B
    if CLASSIFIED.search(front):
        return "declassified" if DECLASSIFIED.search(front) else "out"
    if B.RESTRICTED.search(front):
        return "restricted"
    return "public" if B.DISTRIBUTION_A.search(front) else "none"


def military_notice(verdict, front):
    """The truthful sentence about a military manual's release, from what its own front pages print."""
    import build_textbooks as B
    if verdict == "public":
        return "Its front pages print Distribution Statement A: approved for public release; distribution is unlimited."
    if verdict == "none":
        return ("Published openly by the Internet Archive (archive.org); its front pages print no distribution "
                "statement.")
    if verdict == "restricted":
        marking = B.RESTRICTED.search(front).group(0)
        return (f"PERSONAL USE ONLY: its front pages print a restricted marking (\"{marking}\"), and this copy is from "
                "the Internet Archive, not a government website.")
    return "Its front pages print an old classification marking with a declassification or release marking."


def military_sign(name):
    """A military manual's sign of change: its Internet Archive item's files."""
    import updates
    entry = next(m for m in MILITARY_MANUALS if m["name"] == name)
    return updates.pdf_sign(entry)


# ====================================================================== web guides (Meshtastic)

MESHTASTIC = "https://meshtastic.org"
MESHTASTIC_LICENCE = "https://raw.githubusercontent.com/meshtastic/meshtastic/master/LICENSE"
GUIDES = [
    dict(K.WEB, group=GROUP, name="meshtastic_docs", title="Meshtastic documentation: off-grid LoRa mesh radio",
         subject="Mesh radio (Meshtastic and LoRa)", publisher="Meshtastic LLC and the Meshtastic contributors",
         country="International", licence="GPL-3.0", licence_url="https://www.gnu.org/licenses/gpl-3.0.html",
         licence_page=MESHTASTIC_LICENCE, licence_text=r"GNU GENERAL PUBLIC LICENSE\s+Version 3",
         source=f"{MESHTASTIC}/docs/", sitemap=f"{MESHTASTIC}/sitemap.xml",
         pages=rf"^https://meshtastic\.org/docs/(?!development|legal|community|2\.\d|\d\.\d)[a-z0-9_/-]+/?$",
         unit_rules=[(r"/docs/(introduction|overview|about)", "What Meshtastic is"),
                     (r"/docs/getting-started", "Getting started"), (r"/docs/hardware", "Devices, antennas and power"),
                     (r"/docs/configuration", "Configuration: channels, roles and modules"),
                     (r"/docs/software", "Apps and software"), (r"/docs/meshtasticd", "Meshtastic on Linux"),
                     (r".", "More")],
         description="Meshtastic's documentation, every page: what Meshtastic is (an open, off-grid text messaging "
                     "mesh on licence-free LoRa radio, with no phone network needed), how far it reaches and what "
                     "affects range, the devices and boards (LILYGO T-Beam, T-Echo and T-Deck, Heltec, RAK "
                     "WisBlock, Seeed and others), antennas, batteries and solar nodes, flashing the firmware, "
                     "setting up a node and joining a mesh, channels and encryption, device roles (client, router, "
                     "repeater), modules (position, telemetry, store and forward, MQTT), the Android, Apple, web and "
                     "command-line apps, and troubleshooting. In the US it uses the licence-free 902 to 928 MHz band; "
                     "licensed hams may run it with higher power without encryption.",
         notice="Meshtastic's documentation is licensed under the GNU General Public License version 3 (share-alike: "
                "a copy or change must keep the same licence; its licence file is checked at every build). "
                "Meshtastic® is a registered trademark of Meshtastic LLC. " + RADIO_SAFETY,
         limit=350),
]

# ====================================================================== "Radio links to fetch yourself"

# Each: (title, who publishes it, what it is and why it is not copied, address). This book holds these words only
# (written here, CC0) and the addresses.
LINK_ONLY = [
    ("The FCC's pages on amateur, GMRS, FRS, MURS, CB and marine radio, and RF safety", "Federal Communications "
     "Commission", "Plain-language pages on each radio service, licences (ULS, vanity call signs) and RF exposure "
     "(public domain). fcc.gov refused this build machine's reader (403) on 2026-11-22; the FCC's rules themselves "
     "(47 CFR Parts 80, 95 and 97) are in this library.",
     "https://www.fcc.gov/wireless/bureau-divisions/mobility-division/amateur-radio-service"),
    ("ARRL: licensing, ARES, the National Traffic System and the band plan", "ARRL, the national association for "
     "amateur radio", "The ARRL's licence manuals, ARES (Amateur Radio Emergency Service) and National Traffic System "
     "pages, the US band plan chart and QST magazine. \"© ARRL\" (copyright); link-only.",
     "https://www.arrl.org/"),
    ("RSGB: amateur radio in the UK", "Radio Society of Great Britain (non-US)", "RSGB's licence and operating "
     "guides and band plans; copyright; link-only.", "https://rsgb.org/"),
    ("RACES (Radio Amateur Civil Emergency Service)", "FEMA and state emergency management", "RACES is the amateur "
     "radio service that local and state governments activate in emergencies, under 47 CFR 97.407 (in the Part 97 "
     "book). Local RACES pages belong to each county; ask your emergency management office.",
     "https://www.fema.gov/"),
    ("SKYWARN storm spotter training", "National Weather Service", "Free spotter classes from your local NWS "
     "office (online and in person). The Weather Spotter's Field Guide is in this library; the class schedule is "
     "on each office's page.", "https://www.weather.gov/skywarn/"),
    ("AREDN (Amateur Radio Emergency Data Network) documentation", "Amateur Radio Emergency Data Network, Inc.",
     "High-speed amateur mesh networks on modified Wi-Fi equipment (ham licence required, no encryption). Its "
     "documentation is CC BY-NC-ND 4.0 (non-commercial, no derivatives), which this library cannot split into pages; "
     "fetch it yourself.", "https://docs.arednmesh.org/"),
    ("Broadband-Hamnet", "Broadband-Hamnet project", "The original amateur Wi-Fi mesh firmware (ham licence "
     "required); its pages state no open licence; link-only.", "https://www.broadband-hamnet.org/"),
    ("Reticulum Network Stack manual, RNode, Sideband and NomadNet", "Mark Qvist", "Reticulum is an encrypted "
     "networking stack that runs over LoRa (RNode), packet radio, Wi-Fi and the internet; Sideband and NomadNet are "
     "its messaging apps. Its licence forbids use of the software and documentation in creating AI or machine "
     "learning training datasets; this library is not a training set, but the licence is not a standard open one, "
     "so the manual is link-only (read it, or fetch it yourself).", "https://reticulum.network/manual/"),
    ("MeshCore", "MeshCore project (Scott Powell / Ripple Radios)", "Another LoRa mesh firmware with repeaters and "
     "room servers. Its code is MIT-licensed, but its documentation is spread over its repository and wiki without a "
     "stated licence for the documents; link-only.", "https://github.com/meshcore-dev/MeshCore"),
    ("JS8Call guide", "Jordan Sherer, KN4CRD", "Keyboard-to-keyboard weak-signal HF messaging (ham licence "
     "required). The guide is the author's copyright document; link-only.", "https://js8call.com/"),
    ("Winlink and VARA", "Amateur Radio Safety Foundation (Winlink); EA5HVK (VARA)", "Radio email over HF and VHF "
     "(ham licence required; Winlink also has licensed emergency and government uses). Their help pages are "
     "copyright; VARA is commercial software; link-only.", "https://winlink.org/"),
    ("APRS (Automatic Packet Reporting System) specification and pages", "The late Bob Bruninga, WB4APR, and the "
     "APRS community", "Position, weather and short messages over VHF packet (ham licence required); also LoRa APRS "
     "on 433 MHz. The specification and aprs.org pages are copyright; link-only.", "http://www.aprs.org/"),
    ("CHIRP radio programming software", "The CHIRP project", "Free software to program many handheld and mobile "
     "radios from a computer (GPL software). Its website's robots.txt sets content signals for collecting its pages, "
     "and its wiki has no stated licence for the documents, so it is link-only; the program itself is a download "
     "from its site.", "https://chirpmyradio.com/"),
    ("Briar (phone mesh messaging over Bluetooth and Wi-Fi)", "The Briar Project", "Encrypted messaging that works "
     "phone to phone over Bluetooth and Wi-Fi when the internet is down. Its manual states no licence for its words; "
     "link-only.", "https://briarproject.org/manual/"),
    ("goTenna, Beartooth and other commercial mesh devices", "Their makers", "Phone-paired mesh radios sold by "
     "companies; their manuals are copyright (the manual collection mesh_data_radios has links).",
     "https://gotenna.com/"),
    ("Satellite messengers: Garmin inReach, ZOLEO, SPOT", "Their makers", "Two-way satellite texting and SOS "
     "devices that need a subscription; manuals copyright (links in the manual collection mesh_data_radios).",
     "https://www.garmin.com/en-US/p/837461"),
    ("Wi-Fi HaLow (IEEE 802.11ah)", "Wi-Fi Alliance and chip makers", "Long-range, low-power Wi-Fi at 900 MHz. The "
     "standard and the Wi-Fi Alliance's pages are copyright; no open user documentation was found.",
     "https://www.wi-fi.org/discover-wi-fi/wi-fi-certified-halow"),
    ("NTIA United States Frequency Allocations chart", "National Telecommunications and Information "
     "Administration", "The wall chart of every US frequency allocation (public domain); it is a large coloured "
     "picture, not text, so it is linked rather than built.",
     "https://www.ntia.gov/page/united-states-frequency-allocation-chart"),
    ("ISED Canada radio rules pages (RIC-3 amateur, RBR-4, RSS)", "Innovation, Science and Economic Development "
     "Canada (non-US)", "The amateur certificate study guide, standards and band plans. The canada.ca web pages' terms "
     "allow non-commercial reproduction only, and these pages were not found on open.canada.ca under the Open "
     "Government Licence; the Radiocommunication Regulations themselves are in this library.",
     "https://ised-isde.canada.ca/site/spectrum-management-telecommunications/en/licences-and-certificates/"
     "amateur-radio-operator-certificate"),
]


def links_book(name, work, cache=None, left_out=None, limit=None):
    """The "Radio links to fetch yourself" book: one page per entry of LINK_ONLY, written here (CC0). The addresses
    are not recorded as originals (nothing was read from them)."""
    import build_textbooks as B
    book = K.new_book("radio_links_to_fetch_yourself", "Radio links to fetch yourself", "Radio communications (links)",
                      GROUP, "Digital Accessibility Toolkit (this list's own words)", K.CC0, K.CC0_URL,
                      "https://github.com/mark-getbraille/toolkit-models",
                      "Radio guides and documentation that could not be copied into the library: ARRL and RSGB, "
                      "RACES and SKYWARN classes, AREDN and Broadband-Hamnet, Reticulum, MeshCore, JS8Call, Winlink "
                      "and VARA, APRS, CHIRP, Briar, commercial mesh devices and satellite messengers, Wi-Fi HaLow, "
                      "the NTIA frequency chart and ISED's pages: what each is and its address.",
                      "This list's own words are CC0; each guide belongs to its publisher. " + RADIO_SAFETY,
                      country="International", changes="written for this library: addresses and short descriptions only")
    book.published = "2026-11-22"
    for i, (title, who, what, url) in enumerate(LINK_ONLY[:limit] if limit else LINK_ONLY, 1):
        book.pages.append(B.Page(f"link-{i}-{B.slug(title, 40)}", title,
                                 K.dl([("Published by", who), ("What it is", what), ("Address", url)]), 0,
                                 "Links to fetch yourself"))
    return book


def links_sign(name):
    """The links book's sign of change: the list itself."""
    return K.sha(LINK_ONLY)


MAKERS = {"links_to_fetch_yourself": (links_book, links_sign),
          "canada_radiocommunication_regulations": (canada_book, canada_sign)}
MAKERS.update({p[0]: (cfr_book, cfr_sign) for p in CFR_PARTS})
MAKERS.update({p[0]: (pool_book, pool_sign) for p in POOLS})
MAKERS.update({m["name"]: (military_book, military_sign) for m in MILITARY_MANUALS})


def all_keys():
    """Every key of this module, in reading order: rules, exam pools, guides and PDFs, manuals, links."""
    return ([f"radio:{p[0]}" for p in CFR_PARTS] + ["radio:canada_radiocommunication_regulations"] +
            [f"radio:{p[0]}" for p in POOLS] + [f"radio:{g['name']}" for g in GUIDES] +
            [f"radio:{p['name']}" for p in PDFS] + [f"radio:{m['name']}" for m in MILITARY_MANUALS] +
            ["radio:links_to_fetch_yourself"])


COLLECTION = K.Collection("radio", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words={"radio": all_keys})

LICENCE_LINES = {
    "radio_us_government": "47 CFR (govinfo.gov annual edition), fcc.gov, CISA's AUXFOG and the US military manuals: "
                           "works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at "
                           "every build); the NWS spotter guide under weather.gov/disclaimer (public domain).",
    "radio_ncvec": "Each NCVEC pool page (ncvec.org, checked at every build): \"The NCVEC Question Pool Committee "
                   "hereby releases ... into public domain\"; ncvec.org's robots.txt allows the pages and the "
                   "downloads (checked 2026-11-22).",
    "radio_meshtastic": "github.com/meshtastic/meshtastic LICENSE (checked at every build): GNU General Public License "
                        "version 3 for the documentation site's source; meshtastic.org's robots.txt refuses only "
                        "/docs/2.7/ (old versions), no AI rules (checked 2026-11-22).",
    "radio_canada": "Justice Laws: the Reproduction of Federal Law Order (SI/97-5) allows reproducing federal "
                    "regulations without charge or permission.",
    "radio_military": "Internet Archive copies of US military radio manuals, kept by the owner's rule of 2026-11-22 "
                      "(military_book: a truthful notice from each manual's own front pages; restricted markings "
                      "personal use; classified markings only when declassified or released).",
    "radio_links": "The \"Radio links to fetch yourself\" book is this toolkit's own words (CC0) with addresses.",
}
NOT_INCLUDED = [(title + " [" + who + "]", what + " Index: " + url) for title, who, what, url in LINK_ONLY] + [
    ("Wikibooks amateur radio books", "Wikibooks has no amateur radio book with more than a page or two (searched "
     "2026-11-22); Wikipedia's radio articles are in the Kiwix library. Index: https://en.wikibooks.org/"),
    ("FM 24-18, Tactical Single-Channel Radio Communications Techniques (1987) and Field Radio Techniques (1965)",
     "Both Internet Archive copies are page pictures without their words (no text layer), so they cannot be read "
     "aloud; FM 24-19 and the antenna handbooks are built. Index: "
     "https://archive.org/details/milmanual-fm-24-18-tactical-single-channel-radio-communications-techni"),
    ("Old public-domain radio books", "Already in the electronics books (elec:, published before 1931). Index: "
     "https://archive.org/details/texts"),
    ("Field Antenna Handbook (DTIC ADA155204, 1984) and other DTIC radio reports", "Not taken: a DTIC report's "
     "distribution marking must be read item by item; the Marine Corps and Army antenna handbooks above cover the "
     "same ground. Index: https://archive.org/details/DTIC_ADA155204"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
