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
    (a field manual: parts about weapons or tactics are left out by the builder, and FM 25-7's chapter on hanger and
    adapter loads, which carry weapons and ammunition, by keep_parts);
  - two Marine Corps mountain leader's guides, only their safe chapters (keep_parts, build_textbooks.kept_part):
    Mountain Warfare Operations (MCRP 12-10A.3, 2014): rope management, knots and anchors, lifting and crossing
    systems, rappelling and climbing, rescue, steep climbing, alpine movement, survival and glaciers; and Winter
    Operations (MCRP 12-10A.2, formerly MCRP 3-35.1B): avalanches, ice, ski equipment and techniques, skijoring,
    over-snow casualty evacuation and snow shelters. Their chapters on intelligence, command, manoeuvre, security,
    fires, force protection, tracking and firing positions are left out.
  Every book carries knots_outdoor.OUTDOOR_SAFETY (rope loads, climbing training, sharp tools, fire and local rules).

Already in the library and not repeated: the Army's rigging manual FM 5-125 and Military Mountaineering TC 3-97.61
(field manuals), the survival manuals (ATP 3-50.21, FM 21-76 / MCRP 3-02F, AFR 64-4), cold weather FM 31-70 and TC
21-3, Knight's Modern Seamanship (thin:boating) and the Coast Guard's recreational boating guide (outdoors:).

Not built (NOT_INCLUDED, with the reason and an address): the UK Admiralty Manual of Seamanship (the 1937 edition only
as a lending-library scan; the 1951 to 1972 editions are public domain in the UK but may still be in copyright in the
US by the 1996 restoration of foreign works, so link-only), FM 31-27 and FM 3-05.213 (restricted markings), MCRP
3-02H and AFH 10-644 (evasion), Canada's Down But Not Out and B-GL-382-006 Survival (Crown copyright in force), and
others listed below.

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

COLLECTION = K.Collection("kmil", GROUP, pdfs=PDFS,
                          words={"knots-military": lambda: [f"kmil:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "knots_military": "Internet Archive copies of US Coast Guard, Navy, Army and Marine Corps manuals: works of the US "
                      "government (17 U.S.C. 105); each is judged at every build by the release rule for military "
                      "publications (military_release.py: Distribution Statement A printed for the two Marine Corps "
                      "guides; no statement printed on the Coast Guard handbook and the 1917 and 1944 pack manuals, "
                      "checked 2026-11-22); archive.org's robots.txt allows the files; no "
                      "AI rules (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("Admiralty Manual of Seamanship (UK, BR 67), 1951, 1964, 1967 and 1972 editions", "Crown copyright in published "
     "works lasts 50 years from publication, so they are public domain in the UK; but they were still in copyright "
     "there on 1 January 1996, so the US may have restored their copyright (the URAA restoration of foreign works, 95 "
     "years from publication): link-only for the owner to fetch himself (Program Downloader). The downloadable copies: "
     "https://archive.org/details/manual-seamanship-1951-v1, https://archive.org/details/manual-seamanship-1951-v2, "
     "https://archive.org/details/manual-seamanship-1951-v3, https://archive.org/details/admiralty-manual-sea-v1, "
     "https://archive.org/details/admiralty-manual-sea-v2, https://archive.org/details/admiralty-manual-sea-v3 and "
     "https://archive.org/details/admiraltymanualseamanshipv1-1972. The 1908 edition (revised 1915) is built in full. "
     "Index: https://archive.org/details/manual-seamanship-1951-v1"),
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
