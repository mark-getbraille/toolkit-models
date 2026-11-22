"""The collection "Outdoor tools: axes, saws, knives, compasses and rope (manuals)" (category key outdoor_tools): the
owner's request of 2026-11-22 for knots, rope and practical outdoor skills. practical_manuals.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (axes and hatchets, folding
            and bow saws, pocket knives and multi-tools, knife sharpeners, compasses, climbing rope and harnesses);
  makers    the axe, saw, knife, compass and rope makers (Fiskars, Gränsfors Bruk, Estwing, Silky, Bahco, Victorinox,
            Leatherman, Work Sharp, Suunto, Silva, Brunton, Petzl, Black Diamond): by the owner's rule LINK-ONLY, for
            the person (or the personal assistant) to open in a browser or fetch with Program Downloader;
  guidance  the guides the reference library builds in full (the Forest Service's axe and crosscut saw manuals,
            the Army's rigging and land navigation manuals) and the knot sites that are copyright, as links.

The safety notice is said first (NOTICE): sharp tools and rope that holds people.
"""

NOTICE = ("Cut away from your body, keep people at least two tool lengths away, wear eye protection and sturdy boots, "
          "and keep blades covered. A knot weakens a rope: for climbing, lifting or rescue use rated gear and learn "
          "from a qualified instructor.")

IA_WORDS = ["hatchet", "felling axe", "splitting axe", "folding saw", "bow saw", "pocket knife", "multi-tool",
            "multitool", "knife sharpener", "sharpening system", "baseplate compass", "lensatic compass",
            "climbing rope", "climbing harness"]

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
    dict(title="Animated Knots (copyright; open it in a browser)", url="https://www.animatedknots.com/",
         by="Animated Knots by Grog"),
]

CATEGORY = dict(
    name="Outdoor tools: axes, saws, knives, compasses and rope (manuals)",
    description="Axes and hatchets, folding and bow saws, pocket knives and multi-tools, sharpeners, compasses and "
                "climbing rope and harnesses: the Internet Archive's manuals, the makers' pages (links) and the "
                "government's axe, saw, rigging and land navigation guides. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
