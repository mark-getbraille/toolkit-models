"""Knots, rope work, pack lashings and mountain rope work from US military and Coast Guard manuals, for the reference
library, in the group "Reference, knots and outdoor skills" (the owner's request of 2026-11-22: deepen the knots,
lashings and bushcraft holdings with official military and coast guard guides). Keys: knots-military (every book),
kmil:<name>. A sibling of knots_outdoor.py (knot:) and bushcraft.py (bush:), in the same group.

What this module builds, in plain words, each read from its Internet Archive copy and judged at every build by the
release rule for US military publications (military_release.py: the builder reads the front pages and says
truthfully in the notice whether Distribution Statement A is printed; a restricted marking is never republished):
  - the US Coast Guard's Boat Crew Handbook: Seamanship Fundamentals (BCH 16114.4A, 2020), part of the handbook
    series that took over from the old Boat Crew Seamanship Manual (COMDTINST M16114.5): line types and care, knots
    and splices, deck fittings and line handling, then boat characteristics, stability, weather and boat handling;
  - the Army's Manual of Pack Transportation (Quartermaster Corps, 1917) and Pack Transportation (FM 25-7, 1944):
    lash ropes and slings, the diamond hitch and the other pack hitches, lashed loads and the care of pack animals
    (read whole, FM 25-7's chapter on hanger and adapter loads included as history);
  - two Marine Corps mountain leader's guides, read whole: Mountain Warfare Operations (MCRP 12-10A.3, 2014) and
    Winter Operations (MCRP 12-10A.2, formerly MCRP 3-35.1B). Since the owner's decision of 22 November 2026 old
    military manuals are kept whole; only parts about explosives, demolition, mines, grenades, booby traps,
    improvised explosives or sabotage are left out (build_textbooks.NOT_FIELD_SAFE);
  - the Navy's Boatswain's Mate 2c (1944) and the Bluejacket's Manual (1917), whole, and the Admiralty Manual of
    Seamanship of 1908 (revised 1915), public domain in the UK and the US;
  - the Admiralty Manuals of Seamanship of 1951 to 1972 (seven volumes, every downloadable Internet Archive copy of
    an edition published in 1975 or earlier), by the owner's informed decision of 22 November 2026: public domain in
    the UK (Crown copyright ends 50 years after publication) but possibly restored in the US by the URAA (1996).
    They carry CROWN_NOTICE, the licence UK_CROWN_EXPIRED and the mark us_restoration_risk=True (crown_expired_book),
    and never a US public-domain licence.
  Every book carries knots_outdoor.OUTDOOR_SAFETY (rope loads, climbing training, sharp tools, fire and local rules).

Already in the library and not repeated: the Army's rigging manual FM 5-125 and Military Mountaineering TC 3-97.61
(field manuals), the survival manuals (ATP 3-50.21, FM 21-76 / MCRP 3-02F, AFR 64-4), cold weather FM 31-70 and TC
21-3, Knight's Modern Seamanship (thin:boating) and the Coast Guard's recreational boating guide (outdoors:).

Not built (NOT_INCLUDED, with the reason and an address): the Admiralty Manual of Seamanship of 1983, 1995 and later
(still Crown copyright in the UK: link-only for Program Downloader), the 1932 and 1937 editions and the other copies
that are lending-library scans, FM 31-27 and FM 3-05.213 (restricted markings), MCRP 3-02H and AFH 10-644 (evasion),
Canada's Down But Not Out and B-GL-382-006 Survival (Crown copyright in force), and others listed below.

Run from the repository's folder:
  python3 textbooks/knots_military.py kmil:army_fm_25_7_pack_transportation_1944 --out build/textbooks --limit 3
  python3 textbooks/knots_military.py --list knots-military
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knots_outdoor as KO  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = KO.GROUP                       # "knots": the same group as knots_outdoor.py
GROUPS = dict(KO.GROUPS)               # {"knots": "Reference, knots and outdoor skills"}

# The first words of every notice here; the builder puts the truthful release line in front of it (what the front pages
# print about distribution, and whose work it is: build_textbooks.military_notice).
MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "military crews: its rules and equipment are military ones and may be old. ")


def _mil(name, title, subject, publisher, archive, published, description, notice="", **more):
    """One military manual of the Internet Archive as a PDF entry, judged by the release rule (military=True, or
    distribution_a=True for a field manual, whose parts about weapons and tactics the builder leaves out)."""
    fields = dict(military=True)
    fields.update(more)
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description, notice=MIL_NOTICE + (notice + " " if notice else "") + KO.OUTDOOR_SAFETY,
                    **fields)


# The chapters kept from the two mountain leader's guides (looked for in each part's title and in the heading printed
# on its first page; see build_textbooks.kept_part).
MOUNTAIN_PARTS = (r"\b(foreword|rope management|lifting and crossing|rappelling|rescue climbing|steep climbing|"
                  r"alpine equipment|survival|glaciers|climbing rating|glossary)\b")
# Every part of FM 25-7 but its chapter on hanger and adapter loads (weapons and ammunition on pack saddles).
PACK_PARTS = r"^(?!.*\bhanger and adapter\b)"
WINTER_PARTS = (r"\b(foreword|avalanche|ice reconnaissance|ski equipment|ski techniques|skijoring|casualty "
                r"evacuation|snow shelters|glossary)\b")

PDFS = [
    _mil("uscg_bch_seamanship_fundamentals", "Boat Crew Handbook: Seamanship Fundamentals (US Coast Guard, BCH "
         "16114.4A, 2020)", "Marlinspike seamanship and boat handling", "US Coast Guard, Office of Boat Forces",
         "boat-crew-handbook-seamanship-fundamentals", "2020",
         "The Coast Guard's handbook for boat crews: marlinspike seamanship (the types and characteristics of "
         "natural and synthetic line, inspecting, handling, maintaining and stowing line, knots and splices, deck "
         "fittings and line handling), boat nomenclature, construction, watertight integrity and equipment, "
         "stability, weather and oceanography, and boat handling (forces, basic manoeuvring, near other objects, "
         "to and from a dock, alongside another vessel and in heavy weather).",
         "Recreational boaters follow the Coast Guard's boating rules (outdoors:uscg_boating_safety).",
         work="a work of the US Coast Guard"),
    _mil("army_manual_pack_transportation_1917", "Manual of Pack Transportation (US Army Quartermaster Corps, 1917)",
         "Pack lashings and hitches", "War Department, Quartermaster Corps (US Army)", "packtransport00unitrich",
         "1917",
         "The Army's classic manual of packing loads on mules and horses (H. W. Daly's method): the aparejo and "
         "pack saddles, lash ropes, slings and cinches, making up loads, the diamond hitch and the other pack "
         "hitches, loading and unloading, and caring for pack animals on the trail. Published in 1917 (also public "
         "domain as published before 1931): its animal care is that of its day; ask a veterinarian or an "
         "experienced packer today.", work="a work of the US Army"),
    _mil("army_fm_25_7_pack_transportation_1944", "Pack Transportation (FM 25-7, 1944)", "Pack lashings and hitches",
         "War Department (US Army)", "Fm25-7", "1944",
         "The Army's 1944 field manual of pack transport: choosing and training pack animals, pack saddles and how "
         "to fit them, preparing cargo, slings, lashed loads and the pack hitches (the diamond, the squaw hitch and "
         "others), pack trains, marches and bivouacs, and emergency ways to pack. The machine-read text of this "
         "scan has some mistakes. Read whole, its chapter on hanger and adapter loads (carrying the weapons and "
         "ammunition of its day on pack saddles) included as history.", distribution_a=True, military=False,
         work="a work of the US Army"),
    _mil("usmc_mcrp_12_10a3_mountain_rope_work", "Mountain Leader's Guide to Mountain Warfare Operations (MCRP "
         "12-10A.3, 2014)", "Mountaineering rope work",
         "US Marine Corps (Marine Corps Combat Development Command)",
         "mountain-leaders-guide-to-mountain-warfare-operations-mcrp-12-10-a.-3", "2014",
         "The Marine Corps mountain leader's guide, read whole: rope management, knots and anchors, systems for "
         "lifting and crossing (mechanical advantage, rope bridges), rappelling and climbing, rescue climbing, steep "
         "climbing, alpine equipment and movement, survival, glaciers, and its military chapters (intelligence, "
         "command, manoeuvre, security, fires and force protection). Any part about explosives or demolition is "
         "left out.", distribution_a=True, military=False, work="a work of the US Marine Corps"),
    _mil("usmc_mcrp_12_10a2_winter_operations", "Mountain Leader's Guide to Winter Operations (MCRP 12-10A.2, "
         "formerly MCRP 3-35.1B)", "Winter mountain travel",
         "US Marine Corps (Marine Corps Combat Development Command)",
         "mountain-leaders-guide-to-winter-operations-mcrp-12-10-a.-2", "2013",
         "The Marine Corps guide to winter mountain operations, read whole: avalanche-prone terrain (stability "
         "tests, checklists and transceiver search), reconnaissance of ice, ski equipment and its care, ski "
         "techniques, skijoring, over-snow casualty evacuation, snow shelters, tracking, vehicles, firing positions "
         "and training. Any part about explosives or demolition is left out.",
         "Avalanche terrain kills: take an avalanche course, carry a transceiver, probe and shovel, and check the "
         "local avalanche forecast.", distribution_a=True, military=False,
         work="a work of the US Marine Corps"),
]

# Whole Navy manuals, gunnery and small-arms chapters included (the owner's decision of 22 November 2026: the
# historical naval gunnery and small arms of these manuals are of historical interest and no one has that hardware).
PDFS += [
    _mil("navy_boatswains_mate_2c_1944", "Boatswain's Mate 2c (US Navy, NAVPERS 10005, 1944)",
         "Deck seamanship and marlinspike work", "Bureau of Naval Personnel (US Navy)", "BoatswainsMate2cNAVPERS",
         "1944",
         "The Navy's 1944 rate training manual for boatswain's mates, read whole: deck seamanship, marlinspike "
         "work (line, knots, splices and rigging), ground tackle, boats, cargo handling, the boatswain's mate as a "
         "gunner, and the duties of the rate. A historical manual: its gunnery chapter describes Second World War "
         "ship's guns, kept as history.", work="a work of the US Navy"),
    dict(old_book(GROUP, "bluejackets_manual_1917", "The Bluejacket's Manual (US Navy, 1917)",
                  "Seamanship, knots and boats", "United States Naval Institute", "bluejacketsmanua0000norm", 1917,
                  "The classic handbook for sailors of the US Navy, read whole: knots, bends, hitches and splices, "
                  "boats and boat handling, the compass and navigation basics, signals, ship's routine and customs, "
                  "first aid, swimming, and the infantry drill, small arms and landing-force chapters of its day, "
                  "kept as history.", note="Published in {year}: its rules, first aid and equipment are those of "
                  "its day.", notice=KO.OUTDOOR_SAFETY)),   # published by the Naval Institute (not a government work):
                                                                # public domain as published before 1931
    old_book(GROUP, "admiralty_manual_of_seamanship_1915", "Manual of Seamanship, Volume 1 (Admiralty, UK, 1908, "
             "revised and reprinted 1915)", "Seamanship, knots, splices and rigging", "Admiralty (Great Britain)",
             "manual-seamanship-1915", 1915,
             "The Royal Navy's manual of seamanship, volume 1: the parts of a ship, knots, bends, hitches, splices "
             "and fancy work, blocks and tackles, rigging, anchors and cables, boats under oars and sail, the "
             "compass and lead line, signals, and ship's routine. Public domain in the UK (Crown copyright ended 50 "
             "years after publication) and in the US (published before 1931).",
             note="Published in {year}: the ships, gear and rules are those of its day.",
             notice=KO.OUTDOOR_SAFETY, country="United Kingdom"),
]

# ---------------------------------------------------------------------- the Admiralty manuals of 1951 to 1975
# The owner's informed decision of 22 November 2026: every downloadable Internet Archive copy of an Admiralty
# seamanship, boat or rigging manual published in 1975 or earlier is built in full. They are public domain in the UK
# (Crown copyright in a published work ends 50 years after the end of the year of publication), but they were still
# in copyright there on 1 January 1996, so the US may have restored their copyright (the URAA restoration of foreign
# works, 95 years from publication). The owner was told this and chose to include them. Each carries the same truthful
# notice (CROWN_NOTICE), the licence UK_CROWN_EXPIRED (never a US public-domain licence) and the marks
# uk_crown_expired=True (the builder checks the year at every build: build_textbooks.uk_crown_last_year) and
# us_restoration_risk=True (so they can be found, and kept out of anything that claims US public-domain status).
DECISION_DATE = "22 November 2026"
UK_CROWN_EXPIRED = "Public domain in the UK (Crown copyright expired)"
UK_CROWN_URL = ("https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/"
                "uk-government-licensing-framework/crown-copyright/")
CROWN_NOTICE = ("Crown copyright (UK). Public domain in the UK, where Crown copyright in published works ends 50 years "
                "after publication. Its US copyright may have been restored (URAA, 1996); included at the owner's "
                f"decision ({DECISION_DATE}).")
CROWN_SCAN = ("Read from its Internet Archive scan (digitised by Google Books from a university library): the "
              "machine-read text has the scanner's mistakes, and its pictures are described only by their captions.")
CROWN_NOTE = ("Published in {year} for the Royal Navy: its ships, gear, signals and rules are those of its day "
              "(the collision rules have changed since); never use it for navigation.")
# The licence these books carry, added to the toolkit's allowed licences (more_refs.allowed): an open licence in the
# toolkit's sense (no conditions), shown with its own name so it never reads as US public domain.
ALLOWED = {UK_CROWN_EXPIRED: "open"}


def crown_expired_book(name, title, archive, year, description, subject="Seamanship, boats, knots and rigging"):
    """One Admiralty manual whose UK Crown copyright has ended (published in 1975 or earlier), from its downloadable
    Internet Archive copy, built in full with the owner's notice (see the comment above)."""
    return dict(group=GROUP, name=name, title=title, subject=subject, publisher="Admiralty (Great Britain), "
                "published by His or Her Majesty's Stationery Office", archive=archive, country="United Kingdom",
                licence=UK_CROWN_EXPIRED, licence_url=UK_CROWN_URL, uk_crown_expired=True, us_restoration_risk=True,
                level="reference", published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                description=f"{description} {CROWN_NOTE.format(year=year)}",
                notice=f"{CROWN_NOTICE} {CROWN_SCAN} {KO.OUTDOOR_SAFETY}",
                changes="its scanned pages' machine-read text (with the scanner's mistakes) made into web pages, ten "
                        "pages at a time or one per chapter")


VOLUME_1951 = ("the 1951 edition (B.R. 67, in three volumes, 1951 to 1954), which replaced the 1937 edition")
VOLUME_1964 = ("the 1964 to 1967 edition (B.R. 67), which replaced the 1951 edition")
CROWN_PDFS = [
    crown_expired_book("admiralty_manual_of_seamanship_1951_v1", "Manual of Seamanship, Volume I (Admiralty, UK, B.R. "
                       "67 (1/51), 1951)", "manual-seamanship-1951-v1", 1951,
                       f"Volume I of {VOLUME_1951}: the textbook for naval cadets and seaman boys under training. "
                       "General sea terms, types of ship, warship design and construction, routine and organisation, "
                       "rope and its usage (knots, bends, hitches, whippings and splices), rigging, ship's boats "
                       "(pulling, sailing and power boats), anchors and cables, the mariner's compass, conning and "
                       "steering, sounding by lead and line, charts, buoyage and lights, naval communications and "
                       "ceremonial."),
    crown_expired_book("admiralty_manual_of_seamanship_1951_v2", "Manual of Seamanship, Volume II (Admiralty, UK, "
                       "B.R. 67 (2/51), 1952)", "manual-seamanship-1951-v2", 1952,
                       f"Volume II of {VOLUME_1951}: the continuation of Volume I for junior officers, petty officers "
                       "and men seeking advancement: ship recognition and safety, fire-fighting, rope and its usage, "
                       "rigging, boatwork, life-saving appliances, anchors and cables, laying out hawsers and anchors "
                       "and towing, replenishment at sea, damage control and stability, ship maintenance, the rule of "
                       "the road (the 1910 regulations), conning and steering, compasses, speed and distance, "
                       "sounding, charts, tides and tidal streams, pilotage, time and the stars, and the weather; and "
                       "the naval chapters of its day (paravanes and minesweeping, aircraft, communications and "
                       "ceremonial), kept as history."),
    crown_expired_book("admiralty_manual_of_seamanship_1951_v3", "Manual of Seamanship, Volume III (Admiralty, UK, "
                       "B.R. 67 (3/51), 1954)", "manual-seamanship-1951-v3", 1954,
                       f"Volume III of {VOLUME_1951}: the more advanced seamanship for experienced seamen, a book of "
                       "reference: the officer of the watch in harbour and at sea, the rule of the road, manoeuvring "
                       "in company, handling ships in narrow waters and in heavy weather, towing at sea, moorings, "
                       "salvage and wreck dispersal, fire-fighting, abandoning ship, survival and rescue, warship "
                       "construction and equipment, merchant ships and cargo stowage."),
    crown_expired_book("admiralty_manual_of_seamanship_1964_v1", "Admiralty Manual of Seamanship, Volume 1 (B.R. "
                       "67(1), 1964)", "admiralty-manual-sea-v1", 1964,
                       f"Volume 1 of {VOLUME_1964}: the basic book of seamanship for officers and men joining the "
                       "Royal Navy: types of ship and their parts, fibre, man-made and wire rope and how to handle "
                       "it, bends and hitches, derricks and winches, types and classes of boat, sailing rigs, hints "
                       "to coxswains of boats, the gyro and magnetic compasses, conning and steering, buoyage and "
                       "sounding."),
    crown_expired_book("admiralty_manual_of_seamanship_1967_v2", "Admiralty Manual of Seamanship, Volume 2 (B.R. "
                       "67(2), 1967)", "admiralty-manual-sea-v2", 1967,
                       f"Volume 2 of {VOLUME_1964}: more technical detail, a general textbook and reference book for "
                       "ratings seeking advancement and for junior officers: advanced splicing, the strength of "
                       "rigging fittings and gear, derricks, winches and cranes, the supply, maintenance, repair and "
                       "buoyancy of boats, elementary ship stability, latitude, longitude and charts, and the naval "
                       "work of its day (target towing), kept as history."),
    crown_expired_book("admiralty_manual_of_seamanship_1964_v3", "Admiralty Manual of Seamanship, Volume 3 (B.R. "
                       "67(3), 1964, the 1967 impression)", "admiralty-manual-sea-v3", 1967,
                       f"Volume 3 of {VOLUME_1964}, mainly for officers: ship knowledge, stability and maintenance "
                       "organisation and the more advanced seamanship of a ship's officers. This copy is the 1967 "
                       "impression of the 1964 volume."),
    crown_expired_book("admiralty_manual_of_seamanship_1972_v1", "Admiralty Manual of Seamanship, Volume 1 (B.R. "
                       "67(1), consolidated edition 1972, incorporating Change 1)", "admiraltymanualseamanshipv1-1972",
                       1972,
                       f"Volume 1 of {VOLUME_1964}, in its consolidated edition of 1972 (the 1964 volume with its "
                       "first change): types of ship, fibre, man-made and wire rope, bends and hitches, derricks and "
                       "winches, types of boat and sailing rigs, hints to coxswains, compasses, buoyage and "
                       "sounding."),
]
PDFS += CROWN_PDFS

COLLECTION = K.Collection("kmil", GROUP, pdfs=PDFS,
                          words={"knots-military": lambda: [f"kmil:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "knots_military": "Internet Archive copies of US Coast Guard, Navy, Army and Marine Corps manuals: works of the US "
                      "government (17 U.S.C. 105); each is judged at every build by the release rule for military "
                      "publications (military_release.py: Distribution Statement A printed for the two Marine Corps "
                      "guides; no statement printed on the Coast Guard handbook and the 1917 and 1944 pack manuals, "
                      "checked 2026-11-22); archive.org's robots.txt allows the files; no "
                      "AI rules (checked 2026-11-22).",
    "knots_military_crown": "Internet Archive copies (collection admiralty-publications) of the Admiralty Manuals of "
                            "Seamanship of 1951 to 1972: Crown copyright (UK), ended 50 years after publication, so "
                            "public domain in the UK (the builder checks each item's year at every build: 1975 or "
                            "earlier in 2026); their US copyright may have been restored (URAA, 1996); included at "
                            "the owner's decision (22 November 2026), marked us_restoration_risk; not downloadable "
                            "lending-library copies are never read (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("Admiralty Manual of Seamanship (UK, BR 67), 1951 to 1972 editions: their lending-library copies", "The 1951, "
     "1964, 1967 and 1972 editions are built in full from their downloadable Internet Archive copies (kmil:admiralty_"
     "manual_of_seamanship_1951_v1 and the others: public domain in the UK, where Crown copyright in published works "
     "ends 50 years after publication; still in copyright there on 1 January 1996, so their US copyright may have "
     "been restored by the URAA, 1996; included at the owner's decision of 22 November 2026, marked "
     "us_restoration_risk). The other copies found (bwb_KT-594-508, bwb_KV-026-742, admiraltymanualo0001vari, "
     "admiraltymanualo0000admi, admiraltymanualo0002vari, admiraltymanualo0002admi, bwb_KV-186-592 and the 1951 "
     "manualofseamansh0001vari_n6g9) are lending-library scans that cannot be downloaded (searched 2026-11-22). Index: "
     "https://archive.org/details/admiralty-publications"),
    ("Admiralty Manual of Seamanship (BR 67), 1983 and 1995 editions, and every edition published after 1975", "Still "
     "Crown copyright in the UK (it lasts 50 years from publication: the 1995 edition until the end of 2045), so not "
     "built; link-only for the owner to fetch himself with Program Downloader. The 1995 edition has a downloadable "
     "copy: https://archive.org/details/br67manualseamanship1995; the 1983 volume 2 "
     "(admiraltymanualo0003navy) and another 1995 copy (admiraltymanualo0000grea) are lending-library scans. Index: "
     "https://archive.org/details/br67manualseamanship1995"),
    ("Admiralty Manual of Seamanship (UK), 1932 and 1937 editions", "Public domain in the UK and in the US (their "
     "Crown copyright had ended before 1996, so nothing was restored), but the Internet Archive's copies are "
     "lending-library scans that cannot be downloaded (checked 2026-11-22). Index: "
     "https://archive.org/details/manualofseamansh0001vari"),
    ("UK War Office Manual of Field Engineering (1911, reprinted 1914; 1933 with amendments to 1939)", "Public domain "
     "(Crown copyright ended; the 1911 edition is also US public domain as published before 1931), and its knots, "
     "lashings and spar chapters are good, but they sit among chapters on demolitions, explosives and field "
     "fortification, and the scans (122 MB and 657 MB) have no chapter bookmarks to cut those out safely: "
     "link-only. Index: https://archive.org/details/1914-uk-manual-of-field-engineering-1911"),
    ("US Navy Seaman (1981) and Boatswain's Mate 3 & 2 (1959) rate training manuals", "Lending-library scans on the "
     "Internet Archive that cannot be downloaded (checked 2026-11-22). Index: "
     "https://archive.org/details/seaman00nava"),
    ("US Navy NAVEDTRA Seaman (14067) and Boatswain's Mate (14343) courses; Naval Ships' Technical Manual chapter 613 "
     "(wire and fibre rope)", "No copy with a text layer was found on the Internet Archive (searched 2026-11-22), "
     "and navsea.navy.mil refuses automated requests (403). Index: https://archive.org/search?query=NAVEDTRA+seaman"),
    ("US Coast Guard Boat Crew Seamanship Manual (COMDTINST M16114.5C) and the Coast Guard Auxiliary's seamanship "
     "courses", "uscg.mil, dco.uscg.mil and media.defense.gov refuse automated requests (403, checked 2026-11-22); "
     "the Boat Crew Handbook series took over its seamanship parts, and its Seamanship Fundamentals is built "
     "here. The Auxiliary's course books are sold by the Auxiliary and its own copyright. Index: "
     "https://www.dco.uscg.mil/Our-Organization/Assistant-Commandant-for-Response-Policy-CG-5R/"),
    ("FM 31-27 Pack Animals in Support of Army Special Operations Forces (2000) and FM 3-05.213 Special Forces Use of "
     "Pack Animals (2004)", "FM 31-27's front page prints \"Distribution restricted to United States (U.S.) "
     "Government agencies\" and a destruction notice, and no government site publishes it openly: never republished "
     "(the 1917 and 1944 pack manuals are built instead). FM 3-05.213 is its Special Forces successor, not checked "
     "further for the same reason. Index: https://archive.org/details/fm-31-27-pack-animals-in-support-of-army-sof-2000"),
    ("MCRP 3-02H Survival, Evasion and Recovery; AFH 10-644 SERE Operations; SERE and resistance training", "Evasion, "
     "resistance and escape are left out by the toolkit's rules; the survival manuals without evasion (FM 21-76 / "
     "MCRP 3-02F, ATP 3-50.21, AFR 64-4) are in the library. Index: "
     "https://archive.org/details/milmanual-mcrp-3-02h-survival-evasion-and-recovery"),
    ("FM 3-97.61 Military Mountaineering (2002)", "The edition before TC 3-97.61 (2025), which is already in the "
     "library (pdf:army_tc_3_97_61_mountaineering). Index: "
     "https://archive.org/details/military-mountaineering-fm-3-97.61-tc-90-6-1"),
    ("Canada: Down But Not Out (RCAF and Department of National Defence survival manual) and B-GL-382-006/FP-001 "
     "Survival (1992)", "Canadian Crown copyright lasts 50 years from publication, so the 1984 edition of Down But "
     "Not Out (a lending-library scan) and the 1992 Army survival manual are still in copyright in Canada; the 1950s "
     "editions were not found as downloadable copies, and as foreign works still in copyright in Canada on 1 January "
     "1996 they may be restored in the US. Link-only. Index: https://archive.org/details/b-gl-382-006-fp-001-survival"),
    ("Australia: Australian Army survival and fieldcraft pamphlets; Royal Australian Navy seamanship manuals",
     "Australian Crown copyright in published works lasts 50 years, so works published before 1975 are public "
     "domain there, but no copy from 1945 or earlier (the latest year also safe in the US) was found; the Internet "
     "Archive's fieldcraft pamphlets are infantry tactics, and its survival kit card has no date. Index: "
     "https://archive.org/search?query=australian+army+survival"),
    ("New Zealand: Maritime New Zealand boating and knot guides; New Zealand Mountain Safety Council", "New Zealand "
     "Crown copyright lasts 100 years, but much NZ government work is CC BY 4.0: maritimenz.govt.nz refuses "
     "automated requests (403) so its licence could not be checked; the Mountain Safety Council is a charity whose "
     "copyright page was not found (404). The Department of Conservation's outdoor safety pages (CC BY 4.0) are "
     "built in bushcraft.py. Index: https://www.maritimenz.govt.nz/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
