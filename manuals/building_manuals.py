"""Light construction around the home in the manual library (the owner's request of 2026-11-22): decking, sheds,
fencing, concrete and masonry products, insulation, tile setting systems, ramps, stairlifts and home access products.
categories.py adds the collection home_construction; build_manuals.py builds it. An INDEX of facts and links only.

  makers   the makers' installation-guide libraries, LINK ONLY in this first version (their terms were not checked
           one by one, so nothing is read; each library is listed for the person to open in a browser);
  ia       the Internet Archive's manuals of shed kits, deck and fence systems, stairlifts and ramps;
  public_guides  US government works from the Internet Archive: the Army's Carpentry (FM 5-426) and Concrete and
           Masonry (FM 5-428), Use and Care of Hand Tools and Measuring Tools (TM 9-243), each kept only when its
           front text says Distribution Statement A (build_manuals.public_guide_entries), and OSHA's scaffold guide;
  guidance the US Access Board's guide to ramps and curb ramps, OSHA's construction and ladder pages and NIOSH's
           ladder-safety and falls pages, linked for the person to open (osha.gov and cdc.gov refuse programs).
Home repair (plumbing, outlets, drywall, painting, roofs, floors, doors and windows) is another collection's, and the
hardware makers (Simpson Strong-Tie, GRK and the rest) are in fasteners_anchors already.
"""

INDEX_LICENCE = "CC0 (facts and links); each manual belongs to its maker; the public-domain guides are US government " \
                "works"
LINK_REASON = ("listed for the person to open in a browser; nothing is read from its site in this first version "
               "(its terms were not checked one by one)")
_COMMON = dict(prefix="bc", types=[], documents="installation guides and manuals", category="home_construction")
MAKERS = [dict(_COMMON, access="link", reason=LINK_REASON, **m) for m in [
    dict(key="trex", maker="Trex", type="composite decking and railing", library="https://www.trex.com/"),
    dict(key="timbertech", maker="TimberTech and AZEK", type="composite decking and railing",
         library="https://www.timbertech.com/"),
    dict(key="fiberon", maker="Fiberon", type="composite decking", library="https://www.fiberondecking.com/"),
    dict(key="quikrete", maker="QUIKRETE", type="concrete and masonry products", library="https://www.quikrete.com/"),
    dict(key="sakrete", maker="Sakrete", type="concrete and masonry products", library="https://www.sakrete.com/"),
    dict(key="owens-corning", maker="Owens Corning", type="insulation", library="https://www.owenscorning.com/"),
    dict(key="johns-manville", maker="Johns Manville", type="insulation", library="https://www.jm.com/"),
    dict(key="rockwool", maker="ROCKWOOL", type="mineral wool insulation", library="https://www.rockwool.com/"),
    dict(key="schluter", maker="Schluter Systems", type="tile setting systems", library="https://www.schluter.com/"),
    dict(key="custom-building", maker="Custom Building Products", type="tile setting materials",
         library="https://www.custombuildingproducts.com/"),
    dict(key="lp-building", maker="LP Building Solutions", type="sheathing, siding and shed panels",
         library="https://lpcorp.com/"),
    dict(key="suncast", maker="Suncast", type="shed", library="https://www.suncast.com/"),
    dict(key="arrow-storage", maker="Arrow Storage Products", type="shed", library="https://www.arrowsheds.com/"),
    dict(key="lifetime", maker="Lifetime Products", type="shed", library="https://www.lifetime.com/"),
    dict(key="ez-access", maker="EZ-ACCESS", type="wheelchair ramp", library="https://www.ezaccess.com/"),
    dict(key="prairie-view", maker="Prairie View Industries", type="wheelchair ramp", library="https://www.pvi.com/"),
    dict(key="bruno", maker="Bruno Independent Living Aids", type="stairlift", library="https://www.bruno.com/"),
    dict(key="acorn-stairlifts", maker="Acorn Stairlifts", type="stairlift", library="https://www.acornstairlifts.com/"),
    dict(key="harvey-handrails", maker="Harvey Building Products (handrails and railings)", type="railing",
         library="https://www.harveybp.com/"),
]]

IA_WORDS = ["shed kit", "storage building", "storage shed", "deck kit", "decking", "fence kit", "fence panel",
            "stair lift", "stairlift", "wheelchair ramp", "modular ramp", "pergola", "gazebo", "carport",
            "greenhouse kit"]


def _guide(ia, title, by, year, military=False):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military training manual (whose front text must say it is approved for public release)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


GUIDES = [
    _guide("fm-5-426-carpentry-1995", "Carpentry (FM 5-426, 1995)", "the US Army", 1995, True),
    _guide("fm-5-428-concrete-and-masonry-1998", "Concrete and Masonry (FM 5-428, 1998)", "the US Army", 1998, True),
    _guide("use-and-care-of-hand-tools-and-measuring-tools-1983", "Use and Care of Hand Tools and Measuring Tools "
           "(TM 9-243, 1983)", "the US Army", 1983, True),
    _guide("DTIC_ADA400342", "A Guide to Scaffold Use in the Construction Industry (OSHA 3150, 2001)",
           "the US Occupational Safety and Health Administration", 2001),
]
LINKS = [
    dict(title="Guide to the ADA Standards, chapter 4: ramps and curb ramps (US Access Board)",
         url="https://www.access-board.gov/ada/guides/chapter-4-ramps-and-curb-ramps/", by="the US Access Board"),
    dict(title="Construction industry safety (OSHA)", url="https://www.osha.gov/construction",
         by="the US Occupational Safety and Health Administration"),
    dict(title="Stairways and ladders (OSHA)", url="https://www.osha.gov/ladders",
         by="the US Occupational Safety and Health Administration"),
    dict(title="Ladder safety and the NIOSH ladder safety app (NIOSH)", url="https://www.cdc.gov/niosh/falls/",
         by="the US National Institute for Occupational Safety and Health"),
]

NOTICE = ("Read the installation guide and safety section first. Decks, sheds, fences, stairs, ramps and structural "
          "work usually need a building permit and must meet local codes. Use fall protection at height, eye and "
          "hearing protection with power tools, and gloves and eye protection with wet concrete. A stairlift or "
          "platform lift is installed by a trained installer.")

CATEGORIES = {
    "home_construction": dict(
        name="Light construction: decks, sheds, fences, concrete, insulation, ramps and stairlifts (installation "
             "guides)",
        description="Composite decking and railings, concrete and masonry mixes, insulation, tile setting "
                    "systems, sheds, wheelchair ramps and stairlifts: the makers' installation guides (Trex, "
                    "TimberTech, Fiberon, QUIKRETE, Sakrete, Owens Corning, Johns Manville, ROCKWOOL, Schluter, "
                    "Suncast, Arrow, EZ-ACCESS, Prairie View, Bruno, Acorn and others; links), the Internet "
                    "Archive's manuals, the Army's carpentry, concrete and masonry and hand tool manuals, OSHA's "
                    "scaffold guide, and the Access Board's ramp guidance.",
        kind="manuals", licence=INDEX_LICENCE, ia=IA_WORDS, makers=MAKERS, public_guides=GUIDES, guidance=LINKS,
        notice=NOTICE),
}
