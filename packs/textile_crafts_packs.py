"""Picture packs for the TEXTILE CRAFTS and MENDING (the owner's request of 2026-11-22: home repair, upkeep and
handcrafts; home repair and pest control are in home_upkeep_packs.py; pottery, jewellery, paper, glass, woodcarving
and the other non-textile crafts belong to another helper's packs). Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than
one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

Already in other packs, and so NOT repeated (packs/test_home_crafts.py checks that no Commons category here is named
by another pack file): sewing machines, sergers, rotary cutters, shears, needles, thimbles, pincushions, seam rippers
and bobbins (hardware_packs commons_sewing_food_equipment), Singer sewing machines and tape measures (hardware and
things packs), people sewing, knitting and weaving (people_activity_packs), denim, corduroy, fleece, velvet, flannel,
lace and satin, and patterns such as tartan (everyday_extras_packs commons_clothing_patterns), clothing care labels
(care_label_packs), and the museum collections read whole (met_collection, aic_collection, cleveland_collection,
cooper_hewitt).

Answers say only what the source says: the Commons category's name (with one short line written here on what that
craft, tool or fabric is) or the label people confirmed (Open Images), or the Smithsonian record's own object name,
maker, date, place and materials. No pattern, stitch count, fibre content or size is ever guessed.

The packs (all open: CC0, public domain or CC BY, checked file by file; Open Images labels CC BY 4.0; the
Smithsonian's records and pictures CC0):
  commons_knit_crochet_lace   Wikimedia Commons: knitting needles, knitted objects, knitting machines, cable knitting,
                              stockinette and garter stitch; crochet, crochet hooks, crocheted objects, amigurumi,
                              granny squares, filet and Tunisian crochet; tatting, bobbin lace, needle lace and lace
                              bobbins; macramé; yarn, skeins and yarn shops.
  commons_quilt_embroidery_weaving  Commons: quilting, quilts, patchwork and patchwork quilts, quilting frames and
                              Hawaiian quilts; embroidery, embroidery hoops and stitches, needlepoint, crewel work,
                              smocking, sashiko and embroidery machines; looms (hand, inkle, rigid heddle, backstrap),
                              tablet weaving and weaving shuttles; spinning wheels, drop spindles, distaffs and carding;
                              natural dyes, dyeing, tie-dye, batik and shibori; felting, needle felting and felt; rag
                              rugs.
  commons_sewing_mending      Commons: sewing patterns, dress forms and tailoring; buttons, buttonholes, zips, snap
                              fasteners, hems, seams, stitches, sewing thread, safety pins, haberdashery, elastic and
                              hook-and-loop tape; mending, repaired clothing, darning, darning mushrooms and eggs;
                              sewing kits, boxes, baskets and tables; treadle sewing machines and sewing machine repair.
  commons_upholstery_leather_shoes  Commons: upholstery, upholsterers, upholstered furniture and upholstery tools;
                              leatherwork; shoemaking, cobblers, shoe repair shops and shoe polish; furniture
                              restoration, cane seats (caning), varnishing and wood veneer patching (with the
                              finishing safety note: ventilation, and lead paint in old finishes).
  commons_fabrics_fibres      Commons fabrics and fibres by name: linen, silk, tweed, taffeta, muslin, calico, jersey,
                              organza, damask, brocade, chintz, seersucker, twill, nylon, rayon, wool, mohair, alpaca and
                              merino wool, roving, fabric swatches and textile samples. "What fabric is this?" -> "It
                              is seersucker: a thin cotton cloth with puckered stripes."
  open_images_textile_crafts  Open Images V7: crochet, cross-stitch, embroidery, needlework, quilts, quilting, patchwork,
                              lace and tapestry; looms, thread, sewing needles, sewing machine needles and feet, zips and
                              knots; textiles, wool, leather, denim, silk, velvet, satin, linen, household linens and dye.
                              Labels no other pack asks.
  nmah_textiles_sewing        The Smithsonian's National Museum of American History open-access records (CC0): quilts,
                              coverlets, samplers, lace, embroidery and needlework, hooked rugs, sewing machines (and
                              their patent models), spinning wheels, looms, shuttles, knitting needles, crochet hooks,
                              thimbles, needle cases, darning eggs and sewing boxes, named from the record ("This is a
                              quilt (its record calls it \"Log Cabin Quilt\"), made by ... in Ohio, about 1880. Its record
                              gives its materials: cotton, silk.").

What was looked at and left out (Ravelry and Pinterest: not allowed by their terms; Cooper Hewitt and the V&A; the
Bugwood and extension photos; Commons categories that do not exist) is in training-kit/kit/home_crafts_sources.py, with
the share-alike Commons files.

    python packs/textile_crafts_packs.py commons_fabrics_fibres --limit 8      (prints a few rows: a quick check)
"""

import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, pass_random, listing_out_of_time, fetch_all, SI_BUCKET, si_keys
from gaps_oi_packs import group, build_oi_gap, QUICK

ASK_WHAT = "What is this?"
ASK_HAPPENING = "What is happening here?"
FABRIC_Q = "What fabric is this?"
CRAFT_Q = "What craft is this?"
FINISH_NOTE = ("Work with strippers, stains and varnishes in fresh air, away from flames, wearing gloves; old finishes "
               "and paint may contain lead (homes and furniture from before 1978), so do not sand or scrape them "
               "without lead-safe methods.")
LEATHER_NOTE = "Leather tools and blades are sharp: cut away from your body, on a cutting mat."


def what(category, words, note="", deeper=False):
    """A Commons spec for home_packs.build_commons_topic: "What is this?" -> "This is <words>." and the note."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {note}" if note else ""))])


def craft(category, words, deeper=False, note=""):
    """A Commons spec for a craft shown being done or its work: "What craft is this?" -> "This is <words>."."""
    return (category, deeper, [(CRAFT_Q, f"This is {words}." + (f" {note}" if note else ""))])


def doing(category, words, note="", deeper=False):
    """A Commons spec for a scene: "What is happening here?" -> "This shows <words>." and the note after."""
    return (category, deeper, [(ASK_HAPPENING, f"This shows {words}." + (f" {note}" if note else ""))])


def fabric(category, words, deeper=False):
    """A Commons spec for a fabric or fibre: "What fabric is this?" -> "It is <words>."."""
    return (category, deeper, [(FABRIC_Q, f"It is {words}.")])


# ----------------------------------------------------------------- Commons: knitting, crochet, lace, macramé, yarn

KNIT_CROCHET_LACE = [
    what("Knitting needles", "a pair of knitting needles", deeper=True),
    what("Knitted objects", "something knitted"),
    what("Knitting machines", "a knitting machine", deeper=True),
    craft("Cable knitting", "cable knitting: knitting with raised, twisted cords that look like rope"),
    craft("Stockinette stitch", "knitting in stockinette (stocking) stitch: smooth rows of V shapes on the front"),
    craft("Garter stitch", "knitting in garter stitch: every row knitted, giving bumpy ridges on both sides"),
    craft("Crochet", "crochet: fabric made by pulling loops of yarn through one another with a hook"),
    what("Crochet hooks", "a crochet hook", deeper=True),
    what("Crocheted objects", "something crocheted"),
    what("Amigurumi", "amigurumi: a small crocheted or knitted stuffed toy", deeper=True),
    what("Granny squares", "a granny square: a crocheted square of rounds, often joined with others into a blanket"),
    craft("Filet crochet", "filet crochet: a grid of open and filled squares that makes a picture", deeper=True),
    craft("Tunisian crochet", "Tunisian crochet: crochet worked with a long hook that holds many loops at once"),
    craft("Tatting", "tatting: lace made of knots and loops, worked with a small shuttle", deeper=True),
    craft("Bobbin lace", "bobbin lace: lace made by twisting and crossing threads wound on bobbins"),
    craft("Needle lace", "needle lace: lace made with a needle and thread, stitch by stitch"),
    what("Lace bobbins", "lace bobbins, which hold the threads for bobbin lace"),
    craft("Macrame", "macramé: knotting cord into patterns", deeper=True),
    what("Yarn", "yarn"),
    what("Skeins", "a skein of yarn: a loosely wound coil of yarn", deeper=True),
    what("Yarn shops", "a yarn shop"),
]

# ----------------------------------------------------------------- Commons: quilting, embroidery, weaving, spinning, dyeing

QUILT_EMBROIDERY_WEAVING = [
    craft("Quilting", "quilting: stitching layers of fabric and padding together"),
    what("Quilts", "a quilt", deeper=True),
    craft("Patchwork", "patchwork: pieces of fabric sewn together into a larger design"),
    what("Patchwork quilts", "a patchwork quilt", deeper=True),
    what("Quilting frames", "a quilting frame, which holds a quilt taut while it is stitched"),
    what("Hawaiian quilts", "a Hawaiian quilt: one large cut-out design, often of plants, appliquéd on a plain "
                            "background", deeper=True),
    craft("Embroidery", "embroidery: decorating fabric with stitches"),
    what("Embroidery hoops", "an embroidery hoop, two rings that hold fabric taut for stitching"),
    craft("Embroidery stitches", "embroidery stitches"),
    craft("Needlepoint", "needlepoint: stitching wool or thread through a stiff open canvas", deeper=True),
    craft("Crewel embroidery", "crewel embroidery: embroidery in wool yarn"),
    craft("Smocking", "smocking: gathering fabric into small pleats held by decorative stitches", deeper=True),
    craft("Sashiko", "sashiko: Japanese running-stitch embroidery, used to strengthen and mend cloth", deeper=True),
    what("Embroidery machines", "an embroidery machine", deeper=True),
    what("Looms", "a loom, for weaving thread into cloth"),
    what("Hand looms", "a hand loom"),
    what("Inkle looms", "an inkle loom, for weaving narrow bands"),
    craft("Tablet weaving", "tablet (card) weaving: weaving bands by turning a pack of cards that hold the threads",
          deeper=True),
    what("Rigid heddle looms", "a rigid heddle loom, a simple loom for beginners"),
    what("Backstrap looms", "a backstrap loom, held taut by a strap round the weaver's back", deeper=True),
    what("Weaving shuttles", "a weaving shuttle, which carries the weft thread across the loom", deeper=True),
    what("Spinning wheels", "a spinning wheel, for twisting fibre into yarn", deeper=True),
    what("Drop spindles", "a drop spindle, a weighted stick for spinning yarn by hand", deeper=True),
    what("Distaffs", "a distaff, which holds the fibre while it is spun", deeper=True),
    doing("Carding", "carding: combing fibre between toothed brushes so it can be spun"),
    what("Natural dyes", "natural dyes, made from plants, insects or minerals", deeper=True),
    doing("Dyeing", "dyeing: colouring yarn, fabric or other material"),
    craft("Tie-dye", "tie-dye: fabric tied or folded before dyeing so it takes the colour in patterns",
          deeper=True),
    craft("Batik", "batik: patterns drawn on cloth in wax before dyeing, so the waxed parts stay undyed"),
    craft("Shibori", "shibori: Japanese tie-dyeing, with cloth bound, stitched or folded before dyeing", deeper=True),
    craft("Felting", "felting: matting wool fibres together into felt", deeper=True),
    craft("Needle felting", "needle felting: shaping wool by stabbing it with a barbed needle"),
    what("Felt", "felt: a fabric of wool fibres matted together"),
    what("Rag rugs", "a rag rug, made from strips of old fabric", deeper=True),
]

# ----------------------------------------------------------------- Commons: sewing notions and mending

SEWING_MENDING = [
    what("Sewing patterns", "a sewing pattern"),
    what("Dress forms", "a dress form (tailor's dummy), for fitting and draping clothes"),
    doing("Tailoring", "tailoring: making or altering fitted clothes"),
    what("Buttons", "buttons", deeper=True),
    what("Buttonholes", "a buttonhole", deeper=True),
    what("Zippers", "a zip (zipper)"),
    what("Snap fasteners", "a snap fastener (press stud)", deeper=True),
    what("Hems", "a hem: an edge of fabric folded over and sewn", deeper=True),
    what("Seams", "a seam, where two pieces of fabric are sewn together", deeper=True),
    what("Stitches", "stitches"),
    what("Sewing thread", "sewing thread", deeper=True),
    what("Safety pins", "a safety pin", deeper=True),
    what("Haberdashery", "haberdashery: buttons, threads, ribbons and other small sewing things"),
    what("Elastic", "elastic"),
    what("Velcro", "hook-and-loop tape (Velcro)", deeper=True),
    craft("Mending", "mending: repairing worn or torn clothes or cloth"),
    what("Repaired clothing", "repaired clothing", deeper=True),
    craft("Darning", "darning: weaving thread across a hole to fill it"),
    what("Darning mushrooms", "a darning mushroom, held inside a sock or sleeve while it is darned"),
    what("Darning eggs", "a darning egg, held inside a sock while it is darned", deeper=True),
    what("Sewing kits", "a sewing kit"),
    what("Sewing boxes", "a sewing box", deeper=True),
    what("Sewing baskets", "a sewing basket", deeper=True),
    what("Sewing tables", "a sewing table", deeper=True),
    what("Treadle sewing machines", "a treadle sewing machine, worked by a foot pedal"),
    doing("Sewing machine repair", "sewing machine repair", deeper=True),
]

# ----------------------------------------------------------------- Commons: upholstery, leather, shoes, furniture

UPHOLSTERY_LEATHER_SHOES = [
    craft("Upholstery", "upholstery: padding and covering furniture"),
    doing("Upholsterers", "an upholsterer at work", deeper=True),
    what("Upholstered furniture", "upholstered furniture", deeper=True),
    what("Upholstery tools", "an upholstery tool", deeper=True),
    craft("Leatherwork", "leatherwork: making things from leather", note=LEATHER_NOTE),
    doing("Shoemaking", "shoemaking"),
    doing("Cobblers", "a cobbler: someone who mends shoes", deeper=True),
    what("Shoe repair shops", "a shoe repair shop", deeper=True),
    what("Shoe polish", "shoe polish", deeper=True),
    doing("Furniture restoration", "furniture restoration", FINISH_NOTE, deeper=True),
    what("Caning (furniture)", "a cane seat: a chair seat woven from strips of rattan cane", deeper=True),
    doing("Varnishing", "varnishing", FINISH_NOTE),
    what("Wood veneer patching", "a patch in wood veneer, a repair to the thin surface layer of furniture"),
]

# ----------------------------------------------------------------- Commons: fabrics and fibres by name

FABRICS_FIBRES = [
    fabric("Linen", "linen: a crisp, strong cloth woven from flax"),
    fabric("Silk", "silk: a fine, smooth, shiny fibre made by silkworms, and the cloth woven from it"),
    fabric("Tweed", "tweed: a rough, thick woollen cloth, often flecked with colours"),
    fabric("Taffeta", "taffeta: a crisp, smooth woven cloth that rustles", deeper=True),
    fabric("Muslin", "muslin: a light, loosely woven cotton cloth", deeper=True),
    fabric("Calico", "calico: a plain-woven cotton cloth", deeper=True),
    fabric("Jersey (fabric)", "jersey: a soft, stretchy knitted fabric"),
    fabric("Organza", "organza: a thin, stiff, see-through fabric", deeper=True),
    fabric("Damask", "damask: a woven fabric with a pattern that shows as shiny and matt areas", deeper=True),
    fabric("Brocade", "brocade: a rich woven fabric with a raised pattern, often with metallic threads"),
    fabric("Chintz", "chintz: a glazed cotton cloth printed with flowers", deeper=True),
    fabric("Seersucker", "seersucker: a thin cotton cloth with puckered stripes", deeper=True),
    fabric("Twill", "twill: cloth woven with diagonal ridges, as in denim and gabardine"),
    fabric("Nylon", "nylon: a strong synthetic material made into fabric, thread and rope"),
    fabric("Rayon", "rayon: a soft fabric made from wood pulp (viscose)", deeper=True),
    fabric("Wool", "wool: the fibre from sheep's fleece, and yarn and cloth made from it"),
    fabric("Mohair", "mohair: a silky fibre from Angora goats", deeper=True),
    fabric("Alpaca wool", "alpaca wool: a soft fibre from alpacas", deeper=True),
    fabric("Merino wool", "merino wool: a fine, soft wool from merino sheep"),
    fabric("Roving", "roving: a long, soft rope of combed fibre, ready to be spun"),
    fabric("Fabric swatches", "a fabric swatch: a small sample of cloth"),
    fabric("Textile samples", "a textile sample"),
]


def build_commons_knit_crochet_lace(limit):
    """The commons_knit_crochet_lace pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(KNIT_CROCHET_LACE, limit, "knitlace")


def build_commons_quilt_embroidery_weaving(limit):
    """The commons_quilt_embroidery_weaving pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(QUILT_EMBROIDERY_WEAVING, limit, "quiltweave")


def build_commons_sewing_mending(limit):
    """The commons_sewing_mending pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(SEWING_MENDING, limit, "sewmend")


def build_commons_upholstery_leather_shoes(limit):
    """The commons_upholstery_leather_shoes pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(UPHOLSTERY_LEATHER_SHOES, limit, "upholster")


def build_commons_fabrics_fibres(limit):
    """The commons_fabrics_fibres pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FABRICS_FIBRES, limit, "fabricname")


# ----------------------------------------------------------------- Open Images: textile crafts

TEXTILE_OI = [
    group("What needlework or textile craft is in this picture?",
          {"Crochet": "crochet", "Cross-stitch": "cross-stitch", "Embroidery": "embroidery",
           "Needlework": "needlework", "Quilt": "a quilt", "Quilting": "quilting", "Patchwork": "patchwork",
           "Lace": "lace", "Tapestry": "a tapestry"}),
    group("What sewing or craft things are in this picture?",
          {"Loom": "a loom", "Thread": "thread", "Sewing needle": "a sewing needle",
           "Sewing machine needle": "a sewing machine needle", "Sewing machine feet": "a sewing machine foot",
           "Zipper": "a zip (zipper)", "Knot": "a knot"}),
    group("What fabrics or materials are in this picture?",
          {"Textile": "a textile", "Wool": "wool", "Leather": "leather", "Denim": "denim", "Silk": "silk",
           "Velvet": "velvet", "Satin": "satin", "Linen": "linen",
           "Linens": "household linens (sheets, towels or tablecloths)", "Dye": "dye"}),
]


def build_open_images_textile_crafts(limit):
    """open_images_textile_crafts (see the module docstring)."""
    return build_oi_gap("open_images_textile_crafts", TEXTILE_OI, limit, 9302)


# ----------------------------------------------------------------- Smithsonian NMAH: textiles and sewing (CC0)

# Object names (the record's "Object Name" or title) with the plain name the answer gives; the first that matches.
NMAH_TEXTILE_NAMES = [(re.compile(p, re.I), n) for p, n in [
    (r"\bsewing machines?\b", "a sewing machine"), (r"\bquilts?\b", "a quilt"), (r"\bcoverlets?\b", "a coverlet"),
    (r"\bsamplers?\b", "a sampler (a piece of embroidery showing stitches, letters and patterns)"),
    (r"\bhooked rugs?\b|\brugs?,? hooked\b", "a hooked rug"), (r"\bbobbin lace\b|\blace\b", "a piece of lace"),
    (r"\bembroider(y|ies|ed)\b", "a piece of embroidery"), (r"\bneedlework\b", "a piece of needlework"),
    (r"\bspinning wheels?\b|\bwheels?,? spinning\b", "a spinning wheel"), (r"\blooms?\b", "a loom"),
    (r"\bshuttles?\b(?! ?(bus|craft|launch))", "a shuttle (for weaving, tatting or a sewing machine)"),
    (r"\bknitting needles?\b|\bneedles?,? knitting\b", "knitting needles"),
    (r"\bknitting sheaths?\b", "a knitting sheath"), (r"\bcrochet hooks?\b|\bhooks?,? crochet\b", "a crochet hook"),
    (r"\bthimbles?\b", "a thimble"), (r"\bneedle ?cases?\b|\bneedle ?books?\b", "a needle case"),
    (r"\bdarning (eggs?|balls?|mushrooms?)\b|\bdarners?\b", "a darning egg"),
    (r"\bsewing (box|boxes|kits?|cases?|baskets?|birds?|clamps?)\b", "a sewing box or sewing tool"),
    (r"\bpin ?cushions?\b", "a pincushion"), (r"\bniddy[- ]noddys?\b|\breels?,? (yarn|clock)\b", "a yarn reel"),
    (r"\bswifts?\b,? (yarn|skein)|\byarn winders?\b", "a yarn winder (swift)"),
    (r"\bhackles?\b|\bhatchels?\b|\bheckles?\b", "a flax hackle, for combing flax fibre"),
    (r"\bwool cards?\b|\bcards?,? (wool|hand)\b", "a pair of wool cards, for carding fibre"),
    (r"\btatting\b", "a piece of tatting"),
]]
NMAH_TEXTILE_NOT = re.compile(r"\b(photograph|print|poster|lithograph|negative|postcard|stamp|coin|medal|costume|"
                              r"dress|gown|uniform|toy|doll|game|advertis\w*|trade card|catalog(ue)?|booklet|"
                              r"manual|sheet music|label|flag|banner)\b", re.I)
NMAH_TEXTILE_WORDS = re.compile(r"sewing|quilt|coverlet|sampler|hooked rug|lace|embroider|needlework|spinning|loom|"
                                r"shuttle|knitting|crochet|thimble|needle|darning|darner|pin ?cushion|niddy|yarn|"
                                r"swift|hackle|hatchel|heckle|wool card|tatting", re.I)


def nmah_textile_row(record):
    """(picture address, rows) for an NMAH record of a quilt, sampler, lace, needlework or sewing, spinning or weaving
    tool with a CC0 picture, or None. The answer gives the object's own name, maker, date, place and materials as
    catalogued (hardware_packs.nmah_row does the same for hardware)."""
    content = record.get("content") or {}
    title = clean(record.get("title") or "")
    free = content.get("freetext") or {}
    names = [clean(o.get("content")) for o in free.get("objectType") or [] if o.get("label") == "Object Name"]
    object_name = names[0] if names else title
    if NMAH_TEXTILE_NOT.search(f"{object_name} {title}"):
        return None
    plain = next((n for p, n in NMAH_TEXTILE_NAMES if p.search(object_name)), None) or \
        next((n for p, n in NMAH_TEXTILE_NAMES if p.search(title)), None)
    if not plain:
        return None
    media = ((content.get("descriptiveNonRepeating") or {}).get("online_media") or {}).get("media") or []
    picture = next((m for m in media if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"
                    and m.get("content")), None)
    if not picture:
        return None
    makers = [clean(n.get("content")) for n in free.get("name") or [] if "maker" in (n.get("label") or "").lower()
              or "manufacturer" in (n.get("label") or "").lower()]
    makers = [m for m in makers if not re.match(r"^(unknown|unidentified|anonymous)\b", m, re.I)]
    dates = [clean(d.get("content")) for d in free.get("date") or [] if "made" in (d.get("label") or "").lower()]
    places = [clean(p.get("content")) for p in free.get("place") or [] if "made" in (p.get("label") or "").lower()]
    materials = []
    for p in free.get("physicalDescription") or []:
        words = p.get("content") or ""
        if "material" not in words:
            continue
        words = re.sub(r"\s*\((?:overall|\?+|unknown) material\)", "", words)
        words = re.sub(r"\((?:part: )?([a-z ]+?) material\)", r"(\1)", words)
        materials.append(clean(words))
    patent = bool(re.search(r"\bpatent model\b", f"{object_name} {title}", re.I))
    answer = f"This is {plain}" + (" (a patent model)" if patent and "patent" not in plain else "")
    if title and title.lower() not in plain.lower():
        answer += f" (its record calls it \"{title}\")"
    if makers:
        answer += f", made by {makers[0]}"
    if places:
        answer += (" in " if makers else ", made in ") + places[0].replace("United States: ", "")
    if dates:
        answer += f", {dates[0]}"
    answer += "."
    materials = [m for m in materials if m]
    if materials:
        answer += f" Its record gives its materials: {', '.join(materials)}."
    nr = content.get("descriptiveNonRepeating") or {}
    credit = (f"National Museum of American History, Smithsonian Institution, CC0: {title} "
              f"({nr.get('record_ID', '')}), {nr.get('guid', '')}")
    rows = [{"question": ASK_WHAT, "answer": answer, "credit": credit}]
    if materials:
        rows.append({"question": "What is it made of?", "answer": f"Its record gives its materials: "
                                                                  f"{', '.join(materials)}.", "credit": credit})
    return picture["content"] + "&max=2048", rows


def build_nmah_textiles_sewing(limit, most_files=None):
    """The NMAH records of quilts, samplers, lace, needlework and sewing, spinning and weaving tools with a CC0
    picture, read from the Smithsonian open-access bucket (the museum's metadata files in a fixed shuffled order, a
    quick word check before each record is read), until enough are found or half the time limit is spent. Each kind
    of object gets a fair share, so sewing machine patent models do not fill the pack. most_files: read at most so
    many metadata files (a quick live check)."""
    s, by_kind = session(), {}
    keys = si_keys("nmah")
    pass_random("nmah-textiles").shuffle(keys)
    found = 0
    for key in keys[:most_files] if most_files else keys:
        if listing_out_of_time() or found >= limit * 2:
            break
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=300).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            if '"CC0"' not in line or not NMAH_TEXTILE_WORDS.search(line[:4000]):
                continue
            try:
                got = nmah_textile_row(json.loads(line))
            except ValueError:
                continue
            if got:
                url, rows = got
                kind = rows[0]["answer"].split(" (", 1)[0].split(",", 1)[0]
                by_kind.setdefault(kind, []).append((url, rows))
                found += 1
        say(f"  NMAH {key.rsplit('/', 1)[-1]}: {found} records so far")
    items, share = [], max(10, int(limit * 1.2) // max(1, len(by_kind)))
    for kind in sorted(by_kind):
        items += by_kind[kind][:share]
    pass_random("nmah-textiles-order").shuffle(items)
    from food_packs import with_twins
    named = [(f"nmah-tex-{i:05d}.jpg", url, rows) for i, (url, rows) in enumerate(items[:int(limit * 1.1) + 2])]
    return with_twins(fetch_all(named, workers=6, pause=0.1)[:limit])


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
TEXTILE_CRAFTS_PACKS = {
    "commons_knit_crochet_lace": (build_commons_knit_crochet_lace, COMMONS_LICENCE.format(
        what="knitting, crochet, lace, tatting, macramé and yarn")),
    "commons_quilt_embroidery_weaving": (build_commons_quilt_embroidery_weaving, COMMONS_LICENCE.format(
        what="quilting, embroidery, weaving, spinning, dyeing and felting")),
    "commons_sewing_mending": (build_commons_sewing_mending, COMMONS_LICENCE.format(
        what="sewing notion, pattern, mending and darning")),
    "commons_upholstery_leather_shoes": (build_commons_upholstery_leather_shoes, COMMONS_LICENCE.format(
        what="upholstery, leatherwork, shoe repair and furniture restoration")),
    "commons_fabrics_fibres": (build_commons_fabrics_fibres, COMMONS_LICENCE.format(what="fabric and fibre")),
    "open_images_textile_crafts": (build_open_images_textile_crafts, OI_LICENCE),
    "nmah_textiles_sewing": (build_nmah_textiles_sewing,
                             "National Museum of American History, Smithsonian Institution, open access (CC0): "
                             "records and pictures, each credited below. https://www.si.edu/openaccess"),
}
TEXTILE_CRAFTS_LIMITS = {
    "commons_knit_crochet_lace": 1200,           # 21 categories
    "commons_quilt_embroidery_weaving": 2000,    # 34 categories
    "commons_sewing_mending": 1200,              # 26 categories
    "commons_upholstery_leather_shoes": 700,     # 13 categories
    "commons_fabrics_fibres": 1000,              # 22 categories
    "open_images_textile_crafts": 2000,          # 26 labels
    "nmah_textiles_sewing": 1000,                # a fair share for each kind of object
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
TEXTILE_CRAFTS_COMMONS_KEYS = ("commons_knit_crochet_lace", "commons_quilt_embroidery_weaving",
                               "commons_sewing_mending", "commons_upholstery_leather_shoes", "commons_fabrics_fibres")
# Every Commons spec of these packs (for the self-test).
TEXTILE_CRAFTS_SPECS = (KNIT_CROCHET_LACE + QUILT_EMBROIDERY_WEAVING + SEWING_MENDING + UPHOLSTERY_LEATHER_SHOES +
                        FABRICS_FIBRES)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try a textile crafts pack builder.")
    parser.add_argument("key", choices=sorted(TEXTILE_CRAFTS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    parser.add_argument("--files", type=int, default=0, help="nmah_textiles_sewing: read at most so many files")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    if args.key == "nmah_textiles_sewing":
        entries = build_nmah_textiles_sewing(args.limit, args.files or None)
    else:
        entries = TEXTILE_CRAFTS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
