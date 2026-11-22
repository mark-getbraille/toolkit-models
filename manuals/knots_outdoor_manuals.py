"""The collection "Outdoor tools: axes, saws, knives, compasses and rope (manuals)" (category key outdoor_tools): the
owner's request of 2026-11-22 for knots, rope and practical outdoor skills. practical_manuals.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (axes and hatchets, folding
            and bow saws, pocket knives and multi-tools, knife sharpeners, compasses, climbing rope and harnesses,
            and since 2026-11-22 blocks and tackle, marlinespikes, rope splicing and pack saddles);
  makers    the axe, saw, knife, compass and rope makers (Fiskars, Gränsfors Bruk, Estwing, Silky, Bahco, Victorinox,
            Leatherman, Work Sharp, Suunto, Silva, Brunton, Petzl, Black Diamond, and the rope makers Samson, New
            England Ropes and Sterling): by the owner's rule LINK-ONLY, for
            the person (or the personal assistant) to open in a browser or fetch with Program Downloader;
  guidance  the guides the reference library builds in full (the Forest Service's axe and crosscut saw manuals,
            the Army's rigging and land navigation manuals, the Coast Guard's marlinspike seamanship handbook, the
            Marine Corps mountain leader's rope chapters, the Army's pack manual and the bushcraft index) and the
            knot sites that are copyright, as links.

The safety notice is said first (NOTICE): sharp tools and rope that holds people.
"""

NOTICE = ("Cut away from your body, keep people at least two tool lengths away, wear eye protection and sturdy boots, "
          "and keep blades covered. A knot weakens a rope: never load a rope beyond its working load limit, and for "
          "climbing, lifting or rescue use rated gear and learn from a qualified instructor. Know and follow local "
          "rules on fires and cutting.")

IA_WORDS = ["hatchet", "felling axe", "splitting axe", "folding saw", "bow saw", "pocket knife", "multi-tool",
            "multitool", "knife sharpener", "sharpening system", "baseplate compass", "lensatic compass",
            "climbing rope", "climbing harness",
            # knots and rigging (added 2026-11-22 with the military and bushcraft books)
            "block and tackle", "marlinspike", "rope splicing", "pack saddle"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="outdoor_tools", prefix="ot", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="fiskars", maker="Fiskars", type="axe, hatchet and saw", library="https://www.fiskars.com/",
         site="fiskars.com"),
    dict(key="gransfors", maker="Gränsfors Bruk", type="axe (with The Axe Book)",
         library="https://www.gransforsbruk.com/",
         site="gransforsbruk.com"),
    dict(key="estwing", maker="Estwing", type="axe and hatchet",
         library="https://www.estwing.com/", site="estwing.com"),
    dict(key="silky", maker="Silky", type="folding and pruning saw", library="https://www.silkysaws.com/",
         site="silkysaws.com"),
    dict(key="bahco", maker="Bahco", type="bow saw and hand saw", library="https://www.bahco.com/", site="bahco.com"),
    dict(key="victorinox", maker="Victorinox", type="Swiss Army knife and multi-tool",
         library="https://www.victorinox.com/", site="victorinox.com"),
    dict(key="leatherman", maker="Leatherman", type="multi-tool and knife", library="https://www.leatherman.com/",
         site="leatherman.com"),
    dict(key="work-sharp", maker="Work Sharp", type="knife and tool sharpener",
         library="https://www.worksharptools.com/",
         site="worksharptools.com"),
    dict(key="suunto", maker="Suunto", type="compass", library="https://www.suunto.com/", site="suunto.com"),
    dict(key="silva", maker="Silva", type="compass", library="https://silva.se/", site="silva.se"),
    dict(key="brunton", maker="Brunton", type="compass", library="https://www.brunton.com/", site="brunton.com"),
    dict(key="petzl", maker="Petzl", type="climbing rope, harness and rescue gear (technical notices)",
         library="https://www.petzl.com/", site="petzl.com"),
    dict(key="black-diamond", maker="Black Diamond", type="climbing gear (instructions)",
         library="https://www.blackdiamondequipment.com/", site="blackdiamondequipment.com"),
    # rope makers (splicing guides and working loads), added 2026-11-22
    dict(key="samson-rope", maker="Samson Rope", type="synthetic rope (splicing guides and rope care)",
         library="https://www.samsonrope.com/", site="samsonrope.com"),
    dict(key="new-england-ropes", maker="New England Ropes", type="rope and cordage (splicing instructions)",
         library="https://www.neropes.com/", site="neropes.com"),
    dict(key="sterling-rope", maker="Sterling Rope", type="climbing and rescue rope (use and care)",
         library="https://sterlingrope.com/", site="sterlingrope.com"),
]]

GUIDANCE = [
    dict(title="An Ax to Grind: A Practical Ax Manual (US Forest Service; built in full in the reference library: "
               "knot:usfs_ax_manual)", url="https://www.fs.usda.gov/t-d/pubs/htmlpubs/htm99232823/toc.htm",
         by="the US Forest Service"),
    dict(title="Crosscut Saw Manual (US Forest Service; in the reference library: knot:usfs_crosscut_saw_manual)",
         url="https://www.fs.usda.gov/t-d/pubs/pdfpubs/pdf77712508/pdf77712508dpi300.pdf", by="the US Forest Service"),
    dict(title="Rigging Techniques: knots, hitches, splices and lashings (Army FM 5-125; in the reference library: "
               "pdf:army_fm_5_125_rigging)",
         url="https://archive.org/details/fm-5-125-rigging-techniques-procedures-and-applications-1995",
         by="the US Army"),
    dict(title="Map Reading and Land Navigation (Army FM 3-25.26; in the reference library: "
               "pdf:army_fm_3_25_26_map_reading)", url="https://archive.org/details/FM3-25x26", by="the US Army"),
    dict(title="Boat Crew Handbook: Seamanship Fundamentals, marlinspike seamanship (US Coast Guard; in the reference "
               "library: kmil:uscg_bch_seamanship_fundamentals)",
         url="https://archive.org/details/boat-crew-handbook-seamanship-fundamentals", by="the US Coast Guard"),
    dict(title="Mountain Leader's Guide: rope management, knots, anchors and rescue (US Marine Corps MCRP 12-10A.3; "
               "its technical chapters in the reference library: kmil:usmc_mcrp_12_10a3_mountain_rope_work)",
         url="https://archive.org/details/mountain-leaders-guide-to-mountain-warfare-operations-mcrp-12-10-a.-3",
         by="the US Marine Corps"),
    dict(title="Manual of Pack Transportation: lash ropes and the diamond hitch (US Army, 1917; in the reference "
               "library: kmil:army_manual_pack_transportation_1917)",
         url="https://archive.org/details/packtransport00unitrich", by="the US Army"),
    dict(title="Bushcraft and woodcraft: a guide to the library (bush:index), with New Zealand's Department of "
               "Conservation outdoor safety pages (bush:nz_doc_outdoor_safety)",
         url="https://www.doc.govt.nz/parks-and-recreation/know-before-you-go/",
         by="the Department of Conservation (New Zealand)"),
    dict(title="Animated Knots (copyright; open it in a browser)", url="https://www.animatedknots.com/",
         by="Animated Knots by Grog"),
]

CATEGORY = dict(
    name="Outdoor tools: axes, saws, knives, compasses and rope (manuals)",
    description="Axes and hatchets, folding and bow saws, pocket knives and multi-tools, sharpeners, compasses, "
                "climbing rope and harnesses, blocks and tackle, rope splicing and pack saddles: the Internet "
                "Archive's manuals, the makers' and rope makers' pages (links) and the government's axe, saw, "
                "rigging, marlinspike, mountain rope and land navigation guides. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
