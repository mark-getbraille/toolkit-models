"""Picture packs for PERSONAL CARE AND BEAUTY PRODUCTS (the owner's request of 2026-11-22): makeup, skin care, hair
care and styling tools, shaving, nail care, perfumes and colognes, bath things, oral care holders and tubes, and
historic cosmetics, as PRODUCTS and their packaging. Used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one
question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

Why: the owner is blind and wants the picture describer to tell a lipstick from a lip balm, a hair dye from a
shampoo, a perfume from a cologne, a straight razor from a shaving brush, and to say the safety notes that go with
each one.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed, a museum's
own record), never a guess: no brand, shade or scent is named unless the category itself names it (Nivea, Chanel
No. 5). The safety notes (the same words in the kit's personal_care_sources.py) come from the US Food and Drug
Administration's public-domain cosmetics pages and Poison Help (HRSA):
  COSMETIC_NOTE  stop using a product that causes a rash, redness or swelling; do not share eye makeup; throw out
                 a product whose colour or smell changes.
  HAIR_DYE_NOTE  patch test before each use as the label says; never dye eyebrows or eyelashes (it can blind).
  HEAT_NOTE      hair dryers and irons: keep away from water, unplug after use, let irons cool on a heat-proof place.
  FLAME_NOTE     sprays, perfumes and nail polish remover can catch fire: away from flames and heat.
  BLADE_NOTE     razors and blades are sharp: carry and throw away used blades in a closed container.
  POISON_NOTE    keep cosmetics, mouthwash and nail products out of children's reach; if swallowed call Poison Help
                 1-800-222-1222.

People: only products and hands. Every Commons category is read through NO_PERSON (files whose words name a woman,
man, model, face, portrait, wearing, applying or a child are left out), and the Open Images photos with a confirmed
person, face or child label are left out (PEOPLE_LABELS). No nudity (home_packs.NUDE is applied to every file).

The packs (PERSONAL_CARE_PACKS):
  commons_personal_care_products  Wikimedia Commons (CC0, public domain or CC BY files only): kohl, bronzer, false
                              eyelashes and eyelash curlers, nail art, artificial nails and nail scissors; skin care
                              products, petroleum jelly, Vaseline, Nivea, talcum powder, cotton pads and balls, bath
                              bombs, bath salts, bubble bath and loofahs; hair gel, hair wax, hair dyes, hair rollers,
                              bobby pins and hair pins, hair ties and scrunchies, beard trimmers; straight razors,
                              shaving brushes, shaving soap, razor blades and shaving mugs; perfumes, eau de Cologne,
                              colognes, perfume atomizers and Chanel No. 5; toothbrush holders and toothpaste tubes,
                              hand mirrors and toiletry bags.
  commons_historic_cosmetics  Commons: ancient Egyptian cosmetics, unguentaria, aryballoi and alabastra (ancient
                              perfume and oil bottles) and perfume burners (mostly museum photos).
  met_historic_cosmetics      The Metropolitan Museum of Art (CC0, each object's isPublicDomain checked): kohl
                              tubes, cosmetic boxes and jars, perfume and scent bottles, unguent and toilet boxes,
                              found by those words in the object's own name (MET_WORDS); answered from the record.
  open_images_personal_care   Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark): lip
                              gloss, face powder, makeup brushes and mirrors, nail care and artificial nails, hair
                              ties and irons, electric shavers, shaving cream and aftershave, hair spray, soaps,
                              lotion, shampoo, sunscreen and skin care. No label is asked twice
                              (packs/test_gaps_pictures.py checks).

Not repeated here (other packs have them): commons_personal (shampoo, conditioner, toothpaste, deodorants, shower
gels, soap, sunscreen, lipsticks, mascara, nail polish, face powder, hairbrushes, razors), commons_makeup_grooming
(cosmetics, eye shadow, foundation, concealer, lip gloss and balm, makeup brushes, nail files, combs, curling irons,
electric shavers, shaving cream, safety razors, tweezers, cotton swabs, hair clips, toothbrushes, floss,
mouthwash), commons_dental_care (oral care: interdental brushes, oral irrigators, tongue scrapers and the rest),
commons_contraception_menstrual (feminine care: tampons, menstrual cups, pads), commons_hairstyles and the kit's
commons_hairstyles_sa (hairstyles), and the Open Images labels other packs ask (Cosmetics, Lipstick, Eye shadow,
Mascara, Nail polish, Perfume, Deodorant, Comb, Hair dryer, Razor, Toothbrush, Toothpaste, Mouthwash, Dental floss,
Manicure, Wig, Hairbrush, Tweezers, Cotton swab). Open Beauty Facts is left out (it blocks AI crawlers). What was
looked at and left out is in the kit's personal_care_sources.py (PERSONAL_CARE_NOT_INCLUDED).

    python packs/personal_care_packs.py commons_personal_care_products --limit 8      (a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from outdoor_cooking_packs import with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

COSMETIC_NOTE = ("Cosmetics safety (FDA): stop using a product that gives you a rash, redness, itching or swelling; "
                 "never share eye makeup; throw away a product whose colour or smell has changed.")
HAIR_DYE_NOTE = ("Hair dye (FDA): do the skin patch test the label describes before every use, follow the "
                 "directions, and never use hair dye on eyebrows or eyelashes: it can hurt the eyes and even blind.")
HEAT_NOTE = ("Hot styling tools: keep hair dryers and irons away from water, sinks and baths, unplug them after use, "
             "and let irons cool on a heat-proof surface.")
FLAME_NOTE = ("Fire: sprays, perfumes and nail polish remover can catch fire: keep them away from flames, cigarettes "
              "and heat.")
BLADE_NOTE = "Sharp blades: handle by the handle, and throw used blades away in a closed container."
POISON_NOTE = ("Keep cosmetics, perfume, mouthwash and nail products out of children's reach; if one is swallowed, "
               "call Poison Help at 1-800-222-1222.")

ASK_WHAT = "What is this?"

# Files that show a person rather than a product (hands are fine): the owner asked for products only.
NO_PERSON = re.compile(r"^(?!.*\b(wom[ae]n|m[ae]n|girls?|boys?|lad(y|ies)|gentlem[ae]n|models?|portraits?|faces?|"
                       r"selfies?|wearing|applying|applied|makeup artists?|brides?|actress\w*|actors?|singers?|"
                       r"barbers?|hairdressers?|salons?|child\w*|kids?|bab(y|ies)|teen\w*|people|persons?|"
                       r"nude|naked|topless)\b)", re.I | re.S)


def thing(category, words, notes="", deeper=False):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)], NO_PERSON), so only files whose words name no person are taken."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))], NO_PERSON)


# ----------------------------------------------------------------- Commons: products

MAKEUP_NOTES = f"{COSMETIC_NOTE} {POISON_NOTE}"
PRODUCTS = [
    # makeup and nails
    thing("Kohl (cosmetics)", "kohl, a dark eye makeup", MAKEUP_NOTES, True),
    thing("Bronzer", "bronzer, a powder that gives the skin a sun-tanned colour", MAKEUP_NOTES),
    thing("False eyelashes", "false eyelashes", f"{COSMETIC_NOTE} Eyelash glue can cause an allergic reaction."),
    thing("Eyelash curlers", "an eyelash curler"),
    thing("Nail art", "nail art (decorated fingernails)", f"{FLAME_NOTE} {POISON_NOTE}"),
    thing("Artificial nails", "artificial nails (false nails)", f"{FLAME_NOTE} {POISON_NOTE}"),
    thing("Nail scissors", "nail scissors", BLADE_NOTE),
    # skin care and the bath
    thing("Skin care products", "a skin care product", COSMETIC_NOTE, True),
    thing("Petroleum jelly", "petroleum jelly", "", True),
    thing("Vaseline", "Vaseline (petroleum jelly)"),
    thing("Nivea", "a Nivea product (skin care)", COSMETIC_NOTE, True),
    thing("Talcum powder", "talcum powder", "Do not breathe in the powder.", True),
    thing("Cotton pads", "cotton pads"),
    thing("Cotton balls", "cotton balls"),
    thing("Bath bombs", "a bath bomb", COSMETIC_NOTE),
    thing("Bath salts", "bath salts", POISON_NOTE),
    thing("Bubble bath", "bubble bath", COSMETIC_NOTE),
    thing("Loofahs", "a loofah (a bath sponge)"),
    # hair care and styling
    thing("Hair gel", "hair gel", "", True),
    thing("Hair wax", "hair wax"),
    thing("Hair dyes", "hair dye", f"{HAIR_DYE_NOTE} {POISON_NOTE}", True),
    thing("Hair rollers", "hair rollers (curlers)", HEAT_NOTE),
    thing("Bobby pins", "bobby pins (hair grips)"),
    thing("Hair pins", "hair pins", "", True),
    thing("Hair ties", "hair ties (hair elastics)", "", True),
    thing("Scrunchies", "a scrunchie (a fabric-covered hair tie)"),
    thing("Beard trimmers", "a beard trimmer", HEAT_NOTE.replace("Hot styling tools: keep hair dryers and irons",
                                                                 "Electric tools: keep them")),
    # shaving
    thing("Straight razors", "a straight razor", BLADE_NOTE, True),
    thing("Shave brushes", "a shaving brush", deeper=True),
    thing("Shaving soap", "shaving soap", "", True),
    thing("Razor blades", "razor blades", BLADE_NOTE, True),
    thing("Shaving mugs", "a shaving mug"),
    # perfume
    thing("Perfumes", "perfume", f"{FLAME_NOTE} {POISON_NOTE}", True),
    thing("Eau de Cologne", "eau de Cologne", f"{FLAME_NOTE} {POISON_NOTE}", True),
    thing("Colognes", "cologne", f"{FLAME_NOTE} {POISON_NOTE}", True),
    thing("Perfume atomizers", "a perfume atomizer (a spray bottle for perfume)", FLAME_NOTE),
    thing("Chanel No. 5", "Chanel No. 5 perfume", f"{FLAME_NOTE} {POISON_NOTE}"),
    # oral care things and carrying
    thing("Toothbrush holders", "a toothbrush holder"),
    thing("Toothpaste tubes", "a tube of toothpaste", POISON_NOTE),
    thing("Hand mirrors", "a hand mirror", "", True),
    thing("Toiletry bags", "a toiletry bag (a wash bag)", "", True),
]

# ----------------------------------------------------------------- Commons: historic cosmetics

HISTORIC = [
    thing("Ancient Egyptian cosmetics", "ancient Egyptian cosmetics or a cosmetic container", deeper=True),
    thing("Unguentaria", "an unguentarium, a small ancient bottle for perfumed oil", deeper=True),
    thing("Aryballoi", "an aryballos, a small ancient Greek flask for perfumed oil", deeper=True),
    thing("Alabastra", "an alabastron, a small ancient bottle for perfume or oil", deeper=True),
    thing("Perfume burners", "a perfume burner (incense burner)", deeper=True),
]


def build_commons_personal_care_products(limit):
    """The commons_personal_care_products pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PRODUCTS, limit, "pcare")


def build_commons_historic_cosmetics(limit):
    """The commons_historic_cosmetics pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(HISTORIC, limit, "oldcosm")


# ----------------------------------------------------------------- the Met (CC0)

MET_SEARCHES = ("kohl", "cosmetic", "perfume", "scent bottle", "unguent", "toilet box", "ointment")
# The object's own name must say it is a cosmetic or perfume container (the search also finds paintings of them).
MET_WORDS = re.compile(r"\b(kohl|cosmetic|perfume|scent|unguent|ointment|toilet (box|set|case)|rouge|powder box|"
                       r"compact|mirror)\b", re.I)


def met_themed(o):
    """True when a Met object belongs to met_historic_cosmetics (museum_general_packs leaves it to this pack)."""
    return bool(MET_WORDS.search(o.get("objectName") or ""))


MET_MOST = 3000            # object ids read from each Met search at most


def met_search_items(searches, keep, want, prefix):
    """(file name, picture address, rows) of Met objects found by the searches whose record keep() accepts:
    public domain with a picture, not a highlight (the kit's met), musical instrument, nude or erotica
    (museum_general_packs.met_excluded), answered from the record (museum_general_packs.met_rows); a record with no
    subject tags still names the object, which is what this pack asks. Shared by the toys and world money packs."""
    import time
    from build_packs import session, say, pass_random
    from museum_general_packs import MET, get_json, met_excluded, met_rows
    from service_packs import safety
    from body_packs import MINOR
    s, rng, ids = session(), pass_random(prefix), []
    for q in searches:                       # the v1.1 search, paged (v1/search was retired on 2026-10-01)
        offset = 0
        while offset < MET_MOST:
            page = get_json(s, MET + "v1.1/search", params={"q": q, "hasImages": "true", "limit": 100,
                                                             "offset": offset}) or {}
            found = page.get("objectIDs") or []
            ids += [i for i in found if i not in ids]
            offset += len(found)
            if not found or offset >= (page.get("total") or 0):
                break
            time.sleep(0.3)
    rng.shuffle(ids)
    items = []
    for oid in ids:
        if len(items) >= want or build_packs.listing_out_of_time():
            break
        time.sleep(0.1)
        o = get_json(s, f"{MET}v1/objects/{oid}") or {}
        why = met_excluded(o)                # a themed object is one of these packs' own, so it is kept
        if (why and not why.startswith("a themed object")) or not keep(o):
            continue
        rows, _described = met_rows(o)
        ok, marks = safety([r["answer"] for r in rows])
        if not ok:
            continue
        if MINOR.search(" ".join(r["answer"] for r in rows)):
            marks["child"] = True
        items.append((f"{prefix}-{oid}.jpg", o.get("primaryImage") or o.get("primaryImageSmall"),
                      [dict(r, **marks) for r in rows]))
    say(f"  Met {prefix}: {len(items)} objects of {len(ids)} found")
    return items


def build_met_historic_cosmetics(limit):
    """The met_historic_cosmetics pack (see the module docstring)."""
    from archive_packs import finish_marked
    items = met_search_items(MET_SEARCHES, met_themed, int(limit * 1.2) + 2, "met-cosmetics")
    return finish_marked("met_historic_cosmetics", items, limit, workers=4, pause=0.2)


# ----------------------------------------------------------------- Open Images

# Photos with any of these confirmed are left out (only products and hands).
PEOPLE_LABELS = ("Person", "Human face", "Woman", "Man", "Human head", "Human eye", "Human mouth", "Human hair",
                 "Human nose", "Human body", "Lip", "Eyelash", "Smile", "Selfie", "Model", "Bride", "Beauty",
                 "Fashion model")
CARE_OI = [
    group("What makeup things are in this picture?",
          {"Lip gloss": "lip gloss", "Face powder": "face powder", "Makeup brushes": "makeup brushes",
           "Makeup mirror": "a makeup mirror"}, f"{COSMETIC_NOTE} {POISON_NOTE}"),
    group("What nail care things are in this picture?",
          {"Nail care": "nail care things", "Artificial nails": "artificial nails"}, f"{FLAME_NOTE} {POISON_NOTE}"),
    group("What hair care things are in this picture?",
          {"Hair tie": "a hair tie", "Hair spray": "hair spray"}, FLAME_NOTE),
    group("Is there a hair iron in this picture?", {"Hair iron": "a hair iron"}, HEAT_NOTE),
    group("What shaving things are in this picture?",
          {"Electric shaver": "an electric shaver", "Shaving cream": "shaving cream", "Aftershave": "aftershave"},
          POISON_NOTE),
    group("What soap or skin care products are in this picture?",
          {"Bar soap": "a bar of soap", "Liquid hand soap": "liquid hand soap", "Lotion": "lotion",
           "Shampoo": "shampoo", "Sunscreen": "sunscreen", "Skin care": "skin care products",
           "Personal care": "personal care products"}, POISON_NOTE),
]


def build_open_images_personal_care(limit):
    """open_images_personal_care (see the module docstring): photos with a person's face or body left out."""
    from expression_packs import OI_CHILD
    return with_yes_notes(build_oi_gap("open_images_personal_care", CARE_OI, limit, 9411,
                                       without=PEOPLE_LABELS + tuple(OI_CHILD)), CARE_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
MET_LICENCE = ("The Metropolitan Museum of Art, Open Access (CC0, https://www.metmuseum.org/about-the-met/"
               "policies-and-documents/open-access): public-domain objects, each credited below.")
PERSONAL_CARE_PACKS = {
    "commons_personal_care_products": (build_commons_personal_care_products, COMMONS_LICENCE.format(
        what="makeup, nail, skin care, bath, hair care, shaving, perfume and toiletry")),
    "commons_historic_cosmetics": (build_commons_historic_cosmetics, COMMONS_LICENCE.format(
        what="ancient cosmetics, perfume bottle and perfume burner")),
    "met_historic_cosmetics": (build_met_historic_cosmetics, MET_LICENCE),
    "open_images_personal_care": (build_open_images_personal_care, OI_LICENCE),
}
PERSONAL_CARE_LIMITS = {
    "commons_personal_care_products": 1200,   # 42 categories, few files in some
    "commons_historic_cosmetics": 300,        # 5 categories, mostly museum photos
    "met_historic_cosmetics": 600,            # the Met's kohl tubes, cosmetic boxes and perfume bottles
    "open_images_personal_care": 1500,        # 19 labels; lip gloss and nail care have most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
PERSONAL_CARE_COMMONS_KEYS = ("commons_personal_care_products", "commons_historic_cosmetics")
# The Commons category specs of the packs (for the self-test).
PERSONAL_CARE_SPECS = PRODUCTS + HISTORIC


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a personal care pack builder.")
    parser.add_argument("key", choices=sorted(PERSONAL_CARE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = PERSONAL_CARE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
