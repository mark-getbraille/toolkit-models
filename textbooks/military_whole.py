"""Whole US military manuals that earlier rules left out by their title or by a chapter about weapons, tactics,
evasion or combat, for the reference library, in the group "Reference, field manuals" (the owner's rule of
22 November 2026: military manuals are read WHOLE, as history; only parts about explosives, demolition, mines,
grenades, booby traps, improvised explosives and sabotage are cut). Keys: military-whole (every book),
milw:<name>.

What this module builds, in plain words, each read from its Internet Archive copy and judged at every build by the
release rule for US military publications (military_release.py: the builder reads the front pages and says
truthfully in the notice whether Distribution Statement A is printed; a restricted marking is never republished):
  - Survival, Evasion, Resistance and Escape (SERE) Operations (Air Force Handbook 10-644, 2017): the Air Force's
    whole survival textbook, survival medicine, weather and climates, the open sea, clothing, shelter, fire, water,
    food, land navigation and travel, river travel, signalling and recovery, evasion and urban survival (the DTIC
    copy; its front page says "There are no releasability restrictions on this publication");
  - Survival, Evasion, and Recovery (FM 21-76-1, MCRP 3-02H, NWP 3-50.3, AFTTP(I) 3-2.26, 1999): the multiservice
    pocket guide (one publication under four numbers; Distribution Statement A printed);
  - the Ranger Handbook (TC 3-21.76, 19 September 2025, the Army's own training circular; Distribution Statement A
    printed): leadership, operations orders, fire support, communications, movement, patrols, battle drills,
    military mountaineering, machine guns, urban, waterborne, mounted and aviation operations, and tactical combat
    casualty care. Its chapter 5, Demolitions, is cut (it is bookmarked, so the builder can cut it). The private
    reprints sold in shops are their publishers' copyright and are not used;
  - Desert Operations (FM 90-3, 1993), Jungle Operations (FM 90-5, 1982) and Mountain Operations (FM 3-97.6, 2000):
    the environment and its effects on people and equipment, living and working there, water, health and the
    military chapters, read whole;
  - the Seabee Combat Handbook, volumes 1 (1993) and 2 (1996) (Navy nonresident training courses, Distribution
    Statement A printed): Seabee history, field equipment, the service rifle and pistol, land navigation, evasion
    and survival, first aid, field communications, defence planning, counter-ambush, medical evacuation and CBR
    decontamination. Volume 1's chapter 12 (hand grenades, land mines and booby traps) is cut;
  - Basic Military Requirements (NAVEDTRA 12043, 1992): the Navy's basic course, heritage and history,
    organisation, customs, conduct and justice, uniforms, drill, ship terms, safety, seamanship, damage control,
    CBR defence, small arms, survival, first aid and watch standing;
  - FM 31-27 Pack Animals in Support of Army Special Operations Forces (2000) and FM 3-05.213 Special Forces Use of
    Pack Animals (2004): their front pages print restricted markings, and no government site publishes them
    openly (searched 2026-11-22), so the builder never makes them into a book: it puts them in the catalogue's
    left_out with their address, PERSONAL USE, for the owner's Program Downloader "To do yourself" list.

The cut is made by part: every part (bookmark or printed chapter heading) whose title names explosives, demolition,
mines, grenades, booby traps, improvised explosives or sabotage is left out (build_textbooks.NOT_FIELD_SAFE, applied
because each entry has distribution_a). Each manual here was opened on 2026-11-22 and its parts listed: the parts
about explosives are bookmarked in every one of them, so they can be cut. A manual whose explosives part cannot be
cut (no bookmarks, no printed headings) is not built; NOT_INCLUDED says which and why.

Elsewhere, under the same rule: the radio manuals FM 6-02.53 and ATP 6-02.53 (radio_books.py, radio:) and the
Bluejackets' Manual of 1927 (knots_military.py, kmil:).

Run from the repository's folder:
  python3 textbooks/military_whole.py milw:usaf_afh_10_644_sere_2017 --out build/textbooks --limit 3
  python3 textbooks/military_whole.py --list military-whole
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "fieldmanual"                  # "Reference, field manuals" (sources.GROUPS)
GROUPS = {}                            # the group is already named in sources.GROUPS

# The first words of every notice here; the builder puts the truthful release line in front of it (what the front
# pages print about distribution, and whose work it is: build_textbooks.military_notice).
NOTICE = ("The release line before this says what its own front pages print about distribution. A military manual, "
          "read whole as history: its equipment, rules and procedures are military ones and may be old. Parts about "
          "explosives, demolition, mines, grenades and booby traps are left out. ")
SURVIVAL_NOTE = ("For outdoor emergencies today, call 911 (or 112) when you can; a survival course and the current "
                 "outdoor safety guides of the National Park Service and Forest Service are better teachers than a "
                 "book alone.")


def _whole(name, title, subject, publisher, archive, published, description, work, notice="", **more):
    """One military manual of the Internet Archive as a PDF entry, read whole: distribution_a makes the builder judge
    its front pages by the release rule and cut only the parts about explosives (NOT_FIELD_SAFE)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description, notice=NOTICE + notice, distribution_a=True, work=work, **more)


ARMY = "Headquarters, Department of the Army"
PDFS = [
    _whole("usaf_afh_10_644_sere_2017", "Survival, Evasion, Resistance, and Escape (SERE) Operations (Air Force "
           "Handbook 10-644, 2017)", "Survival", "Department of the Air Force", "DTIC_AD1030991", "2017-03-27",
           "The Air Force's whole SERE textbook (652 pages): the mission, conditions affecting survival, the "
           "psychology of survival, SERE medicine, weather, environments and the world's climates, the open sea, "
           "local people, body temperature and clothing, shelter, firecraft, equipment, water, food, land navigation, "
           "land and river travel, signalling and communication, recovery, evasion and urban areas.",
           "a work of the US Air Force", SURVIVAL_NOTE),
    _whole("sere_fm_21_76_1_mcrp_3_02h_1999", "Survival, Evasion, and Recovery: Multiservice Procedures (FM 21-76-1, "
           "MCRP 3-02H, NWP 3-50.3, AFTTP(I) 3-2.26, 1999)", "Survival",
           "Air Land Sea Application Center (US Army, Marine Corps, Navy and Air Force)",
           "milmanual-mcrp-3-02h-survival-evasion-and-recovery", "1999-06",
           "The armed forces' pocket guide to survival, evasion and recovery: the quick reference checklist, "
           "evasion, navigation, signalling and recovery, medical care, water, food, shelter and fire, and the will to "
           "survive.", "a work of the US armed forces", SURVIVAL_NOTE),
    _whole("army_tc_3_21_76_ranger_handbook_2025", "Ranger Handbook (TC 3-21.76, 2025)", "Small-unit leadership",
           ARMY, "ranger-handbook-tc-3-21.76-19-september-2025", "2025-09-19",
           "The Army's Ranger Handbook, read whole as published by the Army: leadership, troop leading procedures and "
           "orders, fire support, communications, movement, patrols, battle drills, military mountaineering, machine "
           "gun employment, urban, waterborne, mounted patrol and aviation operations, tactical combat casualty care "
           "and the quick reference cards.", "a work of the US Army"),
    _whole("army_fm_90_3_desert_operations_1993", "Desert Operations (FM 90-3, 1993)", "Desert operations", ARMY,
           "fm-90-3-desert-operations-1993", "1993-08",
           "The Army's desert manual, read whole: the desert environment and its effects on people and equipment, "
           "preparing for the desert, operations and combat service support, desert countries, aircraft, equipment, "
           "NBC weapons, concealment, mountains, water use and preventing fratricide.", "a work of the US Army",
           "Heat kills: drink water, rest in the shade and know the signs of heat illness."),
    _whole("army_fm_90_5_jungle_operations_1982", "Jungle Operations (FM 90-5, 1982)", "Jungle operations", ARMY,
           "milmanual-fm-90-5-jungle-operations", "1982",
           "The Army's jungle manual, read whole: the jungle environment, life in the jungle (health, water, food, "
           "shelter), preparing and training, operations, combat service support, navigation and tracking, crossing "
           "jungle obstacles and rivers (rope bridges and rafts), waterborne operations, shelters, NBC defence and "
           "communications.", "a work of the US Army"),
    _whole("army_fm_3_97_6_mountain_operations_2000", "Mountain Operations (FM 3-97.6, 2000)", "Mountain operations",
           ARMY, "fm-3-97.6-mountain-operations-2000", "2000-11",
           "The Army's mountain operations manual, read whole: the mountain environment and weather, command, "
           "firepower and protection, manoeuvre, logistics, mountain illnesses and injuries, and forecasting weather "
           "in the mountains.", "a work of the US Army"),
    _whole("navy_seabee_combat_handbook_v1_1993", "Seabee Combat Handbook, Volume 1 (NAVEDTRA 14234, 1993)",
           "Seabee field skills", "Naval Education and Training Professional Development and Technology Center (US "
           "Navy)", "seabee-combat-handbook-volume-1", "1993-04",
           "The Navy construction battalions' field course, volume 1, read whole: Seabee history and the laws of war, "
           "special clothing and equipment, the service rifle and pistol, combat formations and patrols, land "
           "navigation, evasion, survival and escape, protective measures, entanglements, CBR defence, first aid and "
           "field sanitation, field radios, and support weapons.", "a work of the US Navy"),
    _whole("navy_seabee_combat_handbook_v2_1996", "Seabee Combat Handbook, Volume 2 (NAVEDTRA 14235, 1996)",
           "Seabee field skills", "Naval Education and Training Professional Development and Technology Center (US "
           "Navy)", "seabee-combat-handbook-volume-2", "1996-03",
           "The Navy construction battalions' field course, volume 2, read whole: the combat operations centre and "
           "company command post, setting up medical evacuation, planning a defence, counter-ambush and convoys, and "
           "CBR decontamination, with a glossary and the decontamination tables. Its chapter bookmarks say only "
           "\"ch\": the parts are named by their page numbers.", "a work of the US Navy",
           keep_parts=r"^(?!.*\b(explosives?|demolitions?|land\s*mines?|booby|grenades?)\b)"),
    _whole("navy_basic_military_requirements_1992", "Basic Military Requirements (NAVEDTRA 12043, 1992)",
           "Navy basics", "Naval Education and Training Command (US Navy)", "basicmilitaryreq003571mbp", "1992-04",
           "The Navy's basic course for every sailor, read whole: heritage and naval history, organisation, customs "
           "and courtesies, leadership, conduct and justice, policies and programs, uniforms, professional "
           "development, drill, ship terms and the ships and aircraft of the Navy, safety, seamanship, damage control, "
           "CBR defence, surface preservation, small arms, survival, first aid, watch standing and communications.",
           "a work of the US Navy"),
    # Restricted markings ("Distribution restricted to United States (U.S.) Government agencies", "Distribution
    # authorized to ..."), and no open copy on a government site was found (searched 2026-11-22): the builder puts
    # them in left_out with their address, personal use, for the owner's Program Downloader. Never built into a book.
    _whole("army_fm_31_27_pack_animals_2000", "Pack Animals in Support of Army Special Operations Forces (FM 31-27, "
           "2000)", "Pack animals", ARMY, "fm-31-27-pack-animals-in-support-of-army-sof-2000", "2000-02",
           "Pack animal management, care and training, animal health, packing equipment, horsemanship, techniques, "
           "organisation and movement, and llamas (personal use only: it prints a restricted marking).",
           "a work of the US Army"),
    _whole("army_fm_3_05_213_pack_animals_2004", "Special Forces Use of Pack Animals (FM 3-05.213, 2004)",
           "Pack animals", ARMY, "fm-3-05.213-sf-use-of-pack-animals-2004", "2004-06",
           "The successor of FM 31-27: pack animal management, care and training, health, packing equipment, "
           "horsemanship, packing formations and a 21-day training programme (personal use only: it prints a "
           "restricted marking).", "a work of the US Army"),
]

# The keys whose copies print a restricted marking (personal use, never built into a book).
PERSONAL_USE = ("army_fm_31_27_pack_animals_2000", "army_fm_3_05_213_pack_animals_2004")

COLLECTION = K.Collection("milw", GROUP, pdfs=PDFS,
                          words={"military-whole": lambda: [f"milw:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "military_whole": "Internet Archive copies (one a DTIC copy) of US Army, Navy, Air Force and Marine Corps manuals: "
                      "works of the US government (17 U.S.C. 105), each judged at every build by the release rule "
                      "for military publications (military_release.py): Distribution Statement A printed on MCRP "
                      "3-02H, the Ranger Handbook, FM 3-97.6, the Seabee Combat Handbooks and Basic Military "
                      "Requirements; no statement printed on AFH 10-644 (\"no releasability restrictions\"), FM 90-3 "
                      "and FM 90-5; restricted markings on FM 31-27 and FM 3-05.213 (personal use, never built); "
                      "checked 2026-11-22. archive.org's robots.txt allows the files and has no AI rules.",
}

NOT_INCLUDED = [
    ("Ranger Medic Handbook (75th Ranger Regiment, 2007)", "Allowed by the rule (a unit publication that prints no "
     "distribution statement), but its bookmarks point to files that are not in the PDF and its pages print no "
     "chapter headings the builder can find, so it would be one 154-page page that no one can move through: not built "
     "until a copy with working bookmarks is found. The 2022 edition is a private publisher's reprint (\"Copyright "
     "2022 Breakaway Media, LLC ... All rights reserved\"): link-only. Index: "
     "https://archive.org/details/ranger-medic-handbook-2007"),
    ("Ranger Handbook (SH 21-76, 1992, 2000, 2006 and 2011; TC 3-21.76, 2017)", "Older editions of the handbook "
     "built here (TC 3-21.76, 2025); the 2017 copy's bookmarks also skip chapter 11. Shop reprints (for example "
     "\"Ranger Handbook: Not for the Weak or Fainthearted\") are their publishers' copyright: never used. Index: "
     "https://archive.org/details/tc-3-21-76-ranger-handbook-april-2017"),
    ("The Bluejackets' Manual, 1918 (6th edition)", "Public domain (published before 1931), but its scan has no "
     "bookmarks and no chapter headings the builder can find, and pages 599 to 601 describe how the Navy's contact "
     "mines and their detonators work: a mines part that cannot be cut, so it is left out by the explosives rule. The "
     "1917 and 1927 editions are built (kmil:). Index: https://archive.org/details/bluejacketsmanua0000lieu"),
    ("The Bluejackets' Manual, the Internet Archive item dated 1902 (bluejacketsmanua12mcle)", "Its record says 1902, "
     "but its chapters (aircraft recognition, chemical warfare defence, the telephone talker) are those of a Second "
     "World War edition, which the US Naval Institute published under its own copyright; renewal was not checked: "
     "link-only. Index: https://archive.org/details/bluejacketsmanua12mcle"),
    ("Navy Gunner's Mate rate training manuals", "No Internet Archive copy that can be downloaded was found (searched "
     "2026-11-22); allowed by the rule when one is found (its parts about explosives cut). Index: "
     "https://archive.org/search?query=gunner%27s+mate"),
    ("FM 24-18 Tactical Single-Channel Radio Communications Techniques (1987)", "Its front pages print "
     "\"Distribution authorized to ...\" (restricted) and no government site publishes it openly, and half its pages "
     "are pictures without words: personal use only, for the owner to fetch himself (Program Downloader). Index: "
     "https://archive.org/details/milmanual-fm-24-18-tactical-single-channel-radio-communications-techni"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
