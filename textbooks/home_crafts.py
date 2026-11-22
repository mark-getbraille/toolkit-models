"""Home repair, upkeep, pest control and the textile crafts for the reference library (the owner's request of
2026-11-22). Keys: home-crafts (every book), craft:<name>.

Groups: the home repair, pest, heating, stain and mending books are in "Reference, home repair and pests"; the
textile craft books (quilting, embroidery, weaving, spinning, dyeing, tatting, macramé, needlework and knitting,
upholstery and leatherwork) are in "Reference, arts and crafts" (CRAFT_GROUP, the group of crafts_books.py), the one
top-level group for crafts (the owner's request of 22 November 2026). Their keys did not change.

What this module builds, in plain words, each IN FULL:
  - the EPA's pages on controlling pests safely at home, marked "personal use only" (the EPA's copyright statement,
    checked at every build, allows its documents for non-commercial, scientific and educational purposes): safe pest
    control and when a pesticide is really needed, bed bugs (how to find them, do-it-yourself control, protecting
    your home, what landlords need to know), mosquito control, how to read a pesticide label, and WaterSense's Fix a
    Leak pages (finding and fixing leaking toilets, taps and showerheads) and home water maintenance;
  - the USDA's Home and Garden Bulletin "Removing Stains from Fabrics: Home Methods" (1965), a US government work,
    read whole from its Internet Archive copy (stain by stain: what to use and in what order);
  - old public-domain craft and mending books (published before 1931; the builder checks each item's year on the
    Internet Archive at every build): Marie Webster's Quilts (1915), Grace Christie's Embroidery and Tapestry Weaving
    (1906), Luther Hooper's Hand-Loom Weaving (1910), Mary Meigs Atwater's Shuttle-Craft Book of American Hand-Weaving
    (1928), Clarence Hutton's Kinks on Wool Carding and Spinning (1912), Ethel Mairet's Book on Vegetable Dyes (1916),
    the Butterick Tatting and Netting (1895), Sylvia's Book of Macramé Lace (1890?), Lucretia Hale's Plain Needlework,
    Knitting and Mending (1879), Maud Nicoll's Knitting and Sewing (1918), Charles Leland's Manual of Mending and
    Repairing (1896), Paul Hasluck's Upholstery (1904) and Boot Making and Mending (1898), Emil Johnson's Furniture
    Upholstery for Schools (1919), Charles Bower's Practical Shoe Repairing (1923) and Adelaide Mickel's Leather Work
    (1915). Each old book's description says what is out of date in it (old chemicals, dyes and safety advice).
  - emergency and secondary heating (added the same day): the EPA's Burn Wise pages (wood stoves, fireplaces,
    seasoning and storing firewood, chimney sweeps; personal use only) and the US Fire Administration's heating,
    electrical, power-outage and preparing-for-fire pages (smoke alarms, extinguishers, escape plans; public domain),
    each with the carbon monoxide, 3-feet and gas-professional safety note in its notice.
  - emergency lighting (added the same day): the US Fire Administration's candle and power-outage pages in the same
    book. (Lantern and lamp makers' manuals are the manual collection emergency_lighting, links only.)
  (Already in the library and not repeated: the EPA's mould, radon, lead and indoor air guides (home:epa_home_health),
  the Energy Saver articles (energy_saver_articles), the old sewing, knitting and crochet books of thin:sewing, the
  USDA Farmers' Bulletins on home sewing, stains and household pests (pub:usda_farmers_bulletins) and Dillmont's
  Encyclopedia of Needlework (Kiwix's Project Gutenberg).)

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): CDC's rodent, bed bug and healthy homes pages,
CPSC's home and tool safety guides, OSHA's ladder safety papers and Ready.gov (all answered this build machine "403"
on 2026-11-22; CDC's and CPSC's pages are allowed by their terms, so they can be added when they answer again), the
Healthy Housing Reference Manual (CDC/HUD, the same), university extension guides (copyright or non-commercial),
Instructables, Ravelry and Park Tool's repair help (terms), and Wikibooks (already whole in Kiwix).

Licences: the EPA's copyright statement is checked on its disclaimer page at every build (personal use only); the
USDA bulletin is a work of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); the old books are in the US public domain (published before 1931). robots.txt of epa.gov and archive.org
allow the pages; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/home_crafts.py craft:epa_safe_pest_control --out build/textbooks --limit 5
  python3 textbooks/home_crafts.py --list home-crafts
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "homecraft"
GROUPS = {GROUP: "Reference, home repair and pests"}
# The textile craft books' group: "Reference, arts and crafts" (named in crafts_books.py's GROUPS).
CRAFT_GROUP = "crafts"

# The EPA's terms: the same names as pets_home.py (that module adds EPA_TERMS to sources.ALLOWED as non-commercial).
EPA_TERMS = "EPA website copyright statement"
EPA_DISCLAIMER = "https://www.epa.gov/web-policies-and-procedures/epa-disclaimers"
EPA_TEXT = r"These documents may be freely distributed and used for non-commercial, scientific and educational purposes"
PESTICIDE_SAFETY = ("Pesticide safety: read and follow the whole label (the label is the law), keep pesticides away "
                    "from children and pets, and store them in their original containers. Poison Control: "
                    "1-800-222-1222 in the US.")
EPA_NOTICE = ("From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
              "distributed and used for non-commercial, scientific and educational purposes\". " + PESTICIDE_SAFETY)

OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"
OLD_NOTICE = ("An old book in the US public domain (published before 1931), read from its Internet Archive scan: the "
              "machine-read text has the scanner's mistakes, and its pictures are described only by their captions.")
OLD_CRAFT_NOTE = (" Published in {year}: an old book whose patterns, sizes and fashions are out of date, kept for its "
                  "explanations of methods and tools; measures are in inches and yards.")
OLD_CHEMICAL_NOTE = (" Published in {year}: an old book. Some of the chemicals, dyes, mordants, solvents and finishes it "
                     "names are now known to be poisonous or are banned (lead, arsenic, chrome, benzene, naphtha and "
                     "others): never use them; follow current safety labels and work in fresh air. Kept for its "
                     "explanations of methods and tools; the machine-read text has the scanner's mistakes.")
OLD_TOOLS_NOTE = (" Published in {year}: an old book whose tools, materials and safety advice are out of date (old "
                  "finishes may contain lead; use eye protection and keep blades guarded), kept for its explanations "
                  "of methods; the machine-read text has the scanner's mistakes.")

# ====================================================================== EPA (personal use)

EPA_PEST = "safepestcontrol|bedbugs|mosquitocontrol|pesticide-labels"
WATERSENSE = "fix-leak-week|home-maintenance|bathroom-faucets|showerheads|residential-toilets|how-we-use-water"
GUIDES = [
    dict(K.guide(GROUP, "epa_safe_pest_control", "Controlling pests safely at home: bed bugs, mosquitoes and pesticide "
                 "labels (EPA)", "Pest control at home", "US Environmental Protection Agency (EPA)",
                 [f"https://www.epa.gov/{s}" for s in EPA_PEST.split("|")],
                 rf"^https://www\.epa\.gov/({EPA_PEST})(/(?!forms/)[a-z0-9-]+)*$",
                 "The EPA's pages for controlling pests safely at home, every page: do you really need a pesticide, "
                 "getting rid of pests safely (prevention, integrated pest management), reducing a child's chances of "
                 "pesticide poisoning, pesticides in food and drinking water, registered products; bed bugs (what "
                 "they look like and their life cycle, how to find them, do-it-yourself control, protecting your "
                 "home and yourself when travelling, the safety issues of controlling them, what landlords need to "
                 "know, myths); mosquito control (life cycle, controlling larvae, the pesticides used for adult "
                 "mosquitoes, misting systems); and how to read a pesticide label (keep safe: read the label first, "
                 "label questions and answers).",
                 EPA_NOTICE, depth=1,
                 units=[(r"/bedbugs", "Bed bugs"), (r"/mosquitocontrol", "Mosquito control"),
                        (r"/pesticide-labels", "Reading pesticide labels"), (r".", "Safe pest control")],
                 limit=120),
         licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
         personal_use=True,
         urls=["https://www.epa.gov/bedbugs/do-it-yourself-bed-bug-control",
               "https://www.epa.gov/pesticide-labels/keep-safe-read-label-first"]),
    dict(K.guide(GROUP, "epa_fix_a_leak", "Finding and fixing household leaks (EPA WaterSense)", "Plumbing leaks and "
                 "water use at home", "US Environmental Protection Agency (EPA), WaterSense",
                 [f"https://www.epa.gov/watersense/{s}" for s in WATERSENSE.split("|")],
                 rf"^https://www\.epa\.gov/watersense/({WATERSENSE})$",
                 "WaterSense's pages for homes: Fix a Leak Week (how to check for leaks, the toilet dye test, leaking "
                 "taps and showerheads, outdoor leaks, when to call a plumber), home water maintenance, bathroom taps, "
                 "showerheads and toilets, and how we use water at home.",
                 EPA_NOTICE.replace(" " + PESTICIDE_SAFETY, "") + " Turn off the water at the shut-off valve before "
                 "working on a tap or toilet; for gas water heaters and anything you are unsure of, call a licensed "
                 "plumber.", depth=1, units=[(r"fix-leak-week", "Fix a Leak"), (r".", "Water at home")], limit=20),
         licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
         personal_use=True, urls=["https://www.epa.gov/watersense/fix-leak-week"]),
]

# ====================================================================== emergency and secondary heating

# The same safety words as packs/heating_packs.py HEAT_SAFETY (the coordinator's addition of 2026-11-22).
HEAT_SAFETY = ("Heating safety: keep anything that can burn at least 3 feet (1 metre) away. Stoves, fireplaces and "
               "fuel-burning heaters make carbon monoxide, which can kill: have a working carbon monoxide alarm, "
               "never use outdoor heaters, grills or generators indoors, and if the alarm sounds or anyone feels ill "
               "(headache, dizziness, nausea), get everyone out and call 911. Gas lines, gas appliances and stove "
               "installation are work for a qualified professional.")
BURNWISE_NOT = ("forms/|epa-approved-test-labs|residential-wood-burning-appliance-laboratory|wood-burning-resources-|"
                "hangtag|case-studies|ordinances|toolkit|tribes|order-form")
USFA_PAGES = (r"prevent-fires/(heating|candle|appliance-and-electrical|severe-weather|basement-and-garage|"
              r"home-hazardous-materials)|prepare-for-fire(/[a-z0-9-]+)?")
GUIDES += [
    dict(K.guide(GROUP, "epa_burn_wise", "Burn Wise: wood stoves, fireplaces and firewood (EPA)", "Wood heating",
                 "US Environmental Protection Agency (EPA), Burn Wise program", "https://www.epa.gov/burnwise",
                 rf"^https://www\.epa\.gov/burnwise(/(?!{BURNWISE_NOT})[a-z0-9-]+)?$",
                 "The EPA's Burn Wise pages for people who heat with wood, every page for homes: best wood-burning "
                 "practices and tips for a better burn, choosing a wood-burning appliance and telling whether a stove "
                 "is EPA-certified, installation and maintenance, chimney sweeps, building firewood storage and "
                 "seasoning wood, energy efficiency, wood smoke and your health, backyard fires, changing out an old "
                 "stove, and frequent questions.",
                 "From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be "
                 "freely distributed and used for non-commercial, scientific and educational purposes\". " +
                 HEAT_SAFETY, depth=1, limit=40),
         licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
         personal_use=True, urls=["https://www.epa.gov/burnwise/best-wood-burning-practices",
                                  "https://www.epa.gov/burnwise/wood-burning-installation-and-maintenance"]),
    K.guide(GROUP, "usfa_home_heating_fire_safety", "Heating, candle, electrical and home fire safety: smoke "
            "alarms, extinguishers and escape plans (US Fire Administration)", "Home heating and fire safety",
            "US Fire Administration (FEMA)",
            ["https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/heating",
             "https://www.usfa.fema.gov/prevention/home-fires/prepare-for-fire"],
            rf"^https://www\.usfa\.fema\.gov/prevention/home-fires/({USFA_PAGES})/$",
            "The US Fire Administration's home fire safety pages, every page of these parts: heating fire safety "
            "(space heaters, fireplaces and wood stoves, chimneys, furnaces, carbon monoxide), candle fire safety, "
            "appliance and "
            "electrical fire safety, fire safety in severe weather and power outages (generators and candles), the "
            "basement and garage, hazardous materials at home, and preparing for fire: smoke alarms, heat alarms, "
            "fire extinguishers, home fire sprinklers and home fire escape plans.",
            "A work of the US Fire Administration, part of FEMA (public domain). " + HEAT_SAFETY, depth=1,
            units=[(r"/heating", "Heating fire safety"), (r"/candle", "Candles"),
                   (r"/prepare-for-fire", "Preparing for fire"),
                   (r".", "More fire safety")], limit=40,
            urls=["https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/heating/",
                  "https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/candle/",
                  "https://www.usfa.fema.gov/prevention/home-fires/prepare-for-fire/smoke-alarms/"]),
]

# ====================================================================== the USDA stain guide and the old craft books

PDFS = [
    K.us_pdf(GROUP, name="usda_removing_stains_1965", title="Removing Stains from Fabrics: Home Methods (USDA Home "
             "and Garden Bulletin 62, 1965)", subject="Laundry and stain removal",
             publisher="US Department of Agriculture, Agricultural Research Service", archive="removingstainsfr00unit",
             published="1965", version="1965 printing",
             description="The USDA's guide to removing stains at home: general directions (treat stains quickly, "
                         "test the fabric first, work from the back), the stain removers (absorbents, detergents, "
                         "solvents, bleaches, enzyme products) and how to use each safely, and a stain-by-stain list "
                         "(blood, coffee and tea, grass, grease, ink, mildew, rust, wine and many others) with what "
                         "to use and in what order. Published in 1965: some fabrics, products and solvents it names "
                         "have changed; follow the care label and the product's own label, never mix bleach with "
                         "ammonia or other cleaners, and use dry-cleaning solvents only in fresh air.",
             notice="A work of the US Department of Agriculture (public domain), read from the Internet Archive's "
                    "scan (the machine-read text has the scanner's mistakes)."),
]


def _old(name, title, subject, publisher, archive, year, description, note=OLD_CRAFT_NOTE, country="United States",
         group=CRAFT_GROUP):
    """One old public-domain book of the Internet Archive (published before 1931) as a PDF entry, in the arts and
    crafts group unless group says otherwise (the mending and shoe repair books are home repair)."""
    return dict(group=group, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                country=country, licence=OLD_LICENCE, licence_url=OLD_URL, old_public_domain=True, level="reference",
                published=str(year), version=f"{year} edition", description=description + note.format(year=year),
                notice=OLD_NOTICE, changes="its scanned pages' machine-read text (with the scanner's mistakes) made "
                                           "into web pages, ten pages at a time or one per chapter")


# The old craft and mending books: the craft books in the arts and crafts group, the mending and shoe repair books
# (group=GROUP) in the home repair group.
PDFS += [
    _old("webster_quilts_1915", "Quilts: Their Story and How to Make Them (Marie D. Webster, 1915)", "Quilting",
         "Marie D. Webster (Doubleday, Page and Company)", "quiltstheirstory00webs", 1915,
         "The first book of American quilt history: patchwork, appliqué and quilting, the old patterns and their "
         "names, how quilts are planned, pieced, set and quilted, and the quilting party."),
    _old("christie_embroidery_tapestry_1906", "Embroidery and Tapestry Weaving (Grace Christie, 1906)",
         "Embroidery and tapestry weaving", "Grace Christie (John Hogg, London)", "cu31924031240017", 1906,
         "A practical textbook of embroidery and tapestry weaving: materials and frames, the stitches (chain, "
         "satin, couching, laid work, darning and the rest), designing for stitches, and weaving a small tapestry.",
         country="United Kingdom"),
    _old("hooper_hand_loom_weaving_1910", "Hand-Loom Weaving, Plain and Ornamental (Luther Hooper, 1910)",
         "Hand weaving", "Luther Hooper (John Hogg, London)", "handloomweavingp00hoop", 1910,
         "Weaving on hand looms from the start: the loom and its parts, warping and threading, plain weaving, "
         "twills, tapestry and patterned weaving, and the old looms of many countries.", country="United Kingdom"),
    _old("atwater_shuttle_craft_1928", "The Shuttle-Craft Book of American Hand-Weaving (Mary Meigs Atwater, 1928)",
         "Hand weaving", "Mary Meigs Atwater (Macmillan)", "shuttlecraftbook028554mbp", 1928,
         "The book that revived American hand-weaving: looms, warping and threading, the four-harness overshot "
         "weaves, summer and winter, crackle and other drafts, and coverlets."),
    _old("hutton_wool_carding_spinning_1912", "Kinks on Wool Carding and Spinning (Clarence Hutton, 1912)",
         "Spinning", "Clarence Hutton", "kinksonwoolcardi00huttrich", 1912,
         "Short, practical hints on carding and spinning wool: preparing the fibre, carding, and spinning and "
         "twisting yarn evenly.", note=OLD_TOOLS_NOTE),
    _old("mairet_vegetable_dyes_1916", "A Book on Vegetable Dyes (Ethel M. Mairet, 1916)", "Natural dyeing",
         "Ethel M. Mairet (Douglas Pepler, Ditchling)", "bookonvegetabled00mairrich", 1916,
         "Dyeing wool, silk, cotton and linen with plants: mordanting, and recipes for blues (woad and indigo), "
         "reds (madder), yellows, browns and blacks.", note=OLD_CHEMICAL_NOTE, country="United Kingdom"),
    _old("butterick_tatting_netting_1895", "Tatting and Netting (Butterick Publishing Company, 1895)",
         "Tatting and netting", "Butterick Publishing Company", "tattingnetting00butt", 1895,
         "How to tat with a shuttle and how to net: the knots and stitches, then edgings, insertions and other "
         "designs worked out step by step."),
    _old("sylvia_macrame_lace_1890", "Sylvia's Book of Macramé Lace (about 1890)", "Macramé",
         "Sylvia's Home Help Series (London)", "sylviasbookofmac00lond", 1890,
         "Macramé knotting: the cords, the cushion and the knots (half hitch, flat knot, Solomon's bar and the "
         "rest), with designs for fringes and borders.", country="United Kingdom"),
    _old("hale_plain_needlework_1879", "Plain Needlework, Knitting and Mending, for All, at Home and in Schools "
         "(Lucretia P. Hale, 1879)", "Sewing, knitting and mending", "Lucretia P. Hale (S. W. Tilton and Company)",
         "plainneedleworkk00hale", 1879,
         "Hand sewing from the first stitches (hemming, overcasting, running, backstitching, felling), "
         "buttonholes, knitting, and mending: patching, darning and repairing worn clothes."),
    _old("nicoll_knitting_sewing_1918", "Knitting and Sewing: how to make seventy useful articles (Maud Churchill "
         "Nicoll, 1918)", "Knitting and sewing", "Maud Churchill Nicoll (George H. Doran Company)",
         "knittingsewingho00nico", 1918,
         "Knitting and sewing instructions written for the war effort of 1918: socks, sweaters, helmets, mufflers "
         "and other knitted things, and simple sewn articles, each worked out row by row."),
    _old("leland_manual_of_mending_1896", "A Manual of Mending and Repairing (Charles Godfrey Leland, 1896)",
         "Mending and repairing", "Charles Godfrey Leland (Chatto and Windus, London)", "manualofmending00lela",
         1896,
         "Mending things at home: cements and glues, repairing china, glass, wood, furniture, leather, books, "
         "metal and clothes.", note=OLD_CHEMICAL_NOTE, country="United Kingdom", group=GROUP),
    _old("hasluck_upholstery_1904", "Upholstery (Paul N. Hasluck, 1904)", "Upholstery",
         "Paul N. Hasluck (Cassell and Company)", "upholsterywithnu00hasl", 1904,
         "Upholstering chairs, couches and other furniture: tools and materials, webbing, springing, stuffing, "
         "covering, buttoning and re-covering old work.", note=OLD_TOOLS_NOTE, country="United Kingdom"),
    _old("johnson_furniture_upholstery_1919", "Furniture Upholstery for Schools (Emil A. Johnson, 1919)",
         "Upholstery", "Emil A. Johnson (Manual Arts Press)", "furnitureuphols00john", 1919,
         "An upholstery course: tools and materials, upholstering slip seats, chair seats and backs, and spring "
         "seats, step by step.", note=OLD_TOOLS_NOTE),
    _old("hasluck_boot_making_mending_1898", "Boot Making and Mending (Paul N. Hasluck, 1898)", "Shoe repair",
         "Paul N. Hasluck (Cassell and Company)", "bootmakingmendin00hasl", 1898,
         "Making and mending boots and shoes: tools, leather, lasts, soling and heeling, patching, lasting and "
         "finishing.", note=OLD_TOOLS_NOTE, country="United Kingdom", group=GROUP),
    _old("bower_practical_shoe_repairing_1923", "Practical Shoe Repairing (Charles Leslie Bower, 1923)",
         "Shoe repair", "Charles Leslie Bower", "practicalshoerep00bowe", 1923,
         "The shoe repairer's trade: the shop and its tools and machines, taking off and putting on soles and "
         "heels, stitching, patching and finishing.", note=OLD_TOOLS_NOTE, group=GROUP),
    _old("mickel_leather_work_1915", "Leather Work (Adelaide Mickel, 1915)", "Leatherwork",
         "Adelaide Mickel (Manual Arts Press)", "in.ernet.dli.2015.88834", 1915,
         "Leather craft for beginners: tools, kinds of leather, cutting, tooling and modelling, staining, lacing "
         "and making purses, cases and covers.", note=OLD_TOOLS_NOTE),
]

COLLECTION = K.Collection("craft", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"home-crafts": lambda: [f"craft:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "homecraft_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): \"These "
                     "documents may be freely distributed and used for non-commercial, scientific and educational "
                     "purposes. Commercial use of the documents available from the EPA websites may be protected\". "
                     "So the EPA books are personal use only. www.epa.gov's robots.txt allows the pages; no AI rules "
                     "(checked 2026-11-22).",
    "homecraft_usda_stains": "The USDA's Home and Garden Bulletin 62 is a work of the US government (17 U.S.C. 105, "
                             "checked on govinfo.gov's policies page at every build), read from the Internet "
                             "Archive's copy (removingstainsfr00unit); archive.org's robots.txt allows it.",
    "homecraft_usfa": "www.usfa.fema.gov: works of the US government (FEMA; 17 U.S.C. 105, checked on govinfo.gov's "
                      "policies page at every build); robots.txt names only a sitemap, nothing refused; no AI rules "
                      "(checked 2026-11-22).",
    "homecraft_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every "
                           "build, so a later reprint is refused); archive.org's robots.txt allows the files; no AI "
                           "rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("CDC's rodent, bed bug, flea, tick, lice, hantavirus, mould and healthy homes pages", "Public domain under CDC's "
     "terms, but www.cdc.gov answered this build machine \"403 Forbidden\" for every page and its robots.txt on "
     "2026-11-22, so it could not be read; add them (as parenting.py's CDC books) when CDC answers again. Link-only. "
     "Index: https://www.cdc.gov/rodents/ and https://www.cdc.gov/healthy-homes/"),
    ("Healthy Housing Reference Manual and Inspection Manual (CDC and HUD)", "Public domain, but its CDC address "
     "answered \"403 Forbidden\" (2026-11-22) and no Internet Archive copy was found. Link-only. Index: "
     "https://www.cdc.gov/healthy-homes/"),
    ("CPSC home, tool, ladder, lawn mower, generator and electrical safety guides", "Public information under CPSC's "
     "notice (as parenting.py's CPSC book), but www.cpsc.gov answered \"403 Forbidden\" on 2026-11-22. Link-only. "
     "Index: https://www.cpsc.gov/Safety-Education/Safety-Guides"),
    ("OSHA ladder and power tool safety QuickCards", "Public domain, but www.osha.gov answered \"403 Forbidden\", "
     "robots.txt included (2026-11-22). Link-only. Index: https://www.osha.gov/ladders"),
    ("DOE Energy Saver Guide (PDF) and ENERGY STAR heating and cooling guide", "The Energy Saver Guide's PDF and the "
     "ENERGY STAR guide's address answer \"404\" (removed, 2026-11-22); the Energy Saver articles still on energy.gov "
     "are already built (energy_saver_articles). Link-only. Index: https://www.energy.gov/energysaver/"),
    ("University extension home, pest and sewing guides (Penn State, UC IPM, Kentucky and others)", "Copyright of "
     "their universities (\"All rights reserved\") or CC BY-NC-SA without a usable bulk route; as found for the "
     "garden guides in pets_home.py. Link-only. Index: https://extension.psu.edu/ and https://ipm.ucanr.edu/"),
    ("USDA Farmers' Bulletins on sewing machines, stains and household insects", "Already in the library by decade "
     "(pub:usda_farmers_bulletins), for example Farmers' Bulletin 861, Removal of Stains from Clothing (1917), and "
     "Sewing Machines: Cleaning and Adjusting (1943). Index: https://archive.org/details/usda-farmersbulletin"),
    ("Instructables, Ravelry and Park Tool's repair help", "Instructables' robots.txt disallows its files and "
     "pictures and most projects are CC BY-NC-SA; Ravelry's terms do not allow collecting it; Park Tool's repair "
     "help is \"© Park Tool Co.\" (copyright). Link-only. Index: https://www.parktool.com/en-us/blog/repair-help "
     "and https://www.instructables.com/"),
    ("Wikibooks (Sewing, Knitting, Bicycle Maintenance and Repair, Home Improvement)", "CC BY-SA, and already whole "
     "in the Kiwix library's Wikibooks. Index: https://en.wikibooks.org/wiki/Bicycle_Maintenance_and_Repair"),
    ("CPSC carbon monoxide, portable heater and generator safety pages; CDC carbon monoxide pages", "Public "
     "information and public domain, but www.cpsc.gov and www.cdc.gov answered this build machine \"403 Forbidden\" "
     "(2026-11-22); the US Fire Administration's heating pages (built: craft:usfa_home_heating_fire_safety) cover the "
     "same safety rules. Link-only. Index: https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-"
     "Monoxide-Information-Center and https://www.cdc.gov/carbon-monoxide/"),
    ("NFPA heating and carbon monoxide safety tips", "\"© National Fire Protection Association\": copyright, not "
     "openly licensed. Link-only. Index: https://www.nfpa.org/education-and-research/home-fire-safety"),
    ("DOE Energy Saver wood and pellet heating; USDA APHIS \"Don't Move Firewood\" and emerald ash borer pages",
     "Energy Saver's wood and pellet heating page answers \"404\" (removed in energy.gov's redesign; the remaining "
     "articles are energy_saver_articles), and www.aphis.usda.gov answered \"403 Forbidden\" (2026-11-22). "
     "dontmovefirewood.org is The Nature Conservancy's (copyright). Link-only. Index: "
     "https://www.aphis.usda.gov/plant-pests-diseases/eab and https://www.dontmovefirewood.org/"),
    ("Forest Service and extension firewood guides; old stove and heating books", "No openly licensed extension "
     "firewood guide was found (copyright or non-commercial); the Forest Products Laboratory's site refuses programs "
     "(as found for the hardware guides). The old books found on the Internet Archive are stove makers' sales "
     "catalogues and steam-heating treatises, not guides; the USDA Farmers' Bulletins Construction of Chimneys and "
     "Fireplaces (1930) and Machinery for Cutting Firewood (1919) are already in pub:usda_farmers_bulletins. Index: "
     "https://www.fpl.fs.usda.gov/"),
    ("Emergency lighting and candles during power outages: Ready.gov, CDC, CPSC and the Red Cross", "Ready.gov, "
     "www.cdc.gov and www.cpsc.gov answered this build machine \"403 Forbidden\" (2026-11-22); the Red Cross's pages "
     "are \"© American Red Cross\" (copyright). The US Fire Administration's candle and power-outage pages are built "
     "(craft:usfa_home_heating_fire_safety). Link-only. Index: https://www.ready.gov/power-outages, "
     "https://www.cdc.gov/natural-disasters/safety/power-outages.html and https://www.redcross.org/get-help/how-to-"
     "prepare-for-emergencies/types-of-emergencies/power-outage.html"),
    ("Lamp and lantern books: Coleman, Petromax, Aladdin and Dietz instructions, old lamp books, US Army lighting "
     "manuals", "The owner wants modern lanterns and lamps, nothing from before 1900, so the old lamp books and "
     "catalogues are left out. The makers' current instructions (lighting, shutdown, mantles, generators, pumps, "
     "troubleshooting) are copyright: they are links in the manual collection emergency_lighting, and Coleman's old "
     "manuals are in the Internet Archive collection of camping_outdoor, for the owner to fetch with Program "
     "Downloader. No public-release US government or military lantern manual was found (the TM 10 series found "
     "covers water heaters, 1945). Index: https://archive.org/details/manuals_coleman"),
    ("US Army cold-weather and field heater manuals", "The cold-weather field manuals (FM 31-70, TC 21-3 and others) "
     "are in the field manual library (fieldmanuals); the space heater technical manuals found (TM 9-4520-271-24P, "
     "2006) are parts lists, with nothing to read for using a heater. (A missing distribution statement no longer "
     "leaves out a military manual: military_release.py.) Index: "
     "https://archive.org/details/milmanual-fm-31-70-basic-cold-weather-manual"),
    ("Encyclopedia of Needlework (Thérèse de Dillmont) and Weldon's Practical Needlework", "Dillmont is in the Kiwix "
     "library's Project Gutenberg books; no Internet Archive copy of Weldon's Practical Needlework volumes with a "
     "text layer was found (only Weldon's fancy-dress book). Index: https://www.gutenberg.org/ebooks/20776"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
