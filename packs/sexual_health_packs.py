"""Picture packs for SEXUAL AND REPRODUCTIVE HEALTH (the owner's request of 2026-11-22): products and medical items
only, adult, factual and clinical; no nudity and nothing sexual. Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]. The limit counts
pictures.

Why: the owner is blind and wants his offline assistant to say what a contraceptive or period product or a test kit
is when he holds it up to the camera, with the plain facts the reference books give (textbooks/sexual_health.py).

Safety, in three layers: only these product categories are read; every file's own title and words must name a
product or packaging and must not name a body part, a sexual act, a demonstration model or use (SAFE_WORDS, checked
for every file, on top of the builder's own nudity filter, home_packs.NUDE); and files whose words name a child are
left out (adults_only). The pack is in NO topic add-on (the owner's choice: not the sensitive topics, and not loaded
by chance with the everyday home add-on), is never used for picture-making, and carries no "content" mark because it
shows products, not bodies.

Answers say only what the Commons category names, with a plain clinical line written here from CDC's and FDA's
pages, and every answer ends with the health note (the owner's words, adapted):
  SEX_NOTE  "General information, not medical advice or a diagnosis: ask a doctor, nurse or pharmacist, and use each
            product as its own directions say. In an emergency call 911; in a mental health crisis call or text 988."
The words are the same as the reference books' (textbooks/sexual_health.py NOTE; packs/test_health_life.py checks).

The pack (SEXUAL_HEALTH_PACKS):
  commons_contraception_menstrual  Wikimedia Commons (CC0, public domain or CC BY files only): male and female
                                   condoms, intrauterine devices, contraceptive implants, cervical caps, contraceptive
                                   patches, vaginal rings, emergency contraception, spermicides, menstrual cups,
                                   tampons, cloth menstrual pads and HIV test kits.

Not here: pregnancy tests and home test kits (med_vet_packs, health_test_packs), pills and blister packs (med_vet_packs,
pill_packs), period underwear (its photos show people in underwear) and personal lubricants (left out with the other
sexual products, as packaged_goods_packs does). Open Images was counted on 2026-11-22: Condom and Tampon have no
human-checked photos and Pregnancy test one, so there is no Open Images pack. What was looked at and left out is in
the kit's sexual_health_sources.py.

    python packs/sexual_health_packs.py commons_contraception_menstrual --limit 8      (prints a few rows)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

SEX_NOTE = ("General information, not medical advice or a diagnosis: ask a doctor, nurse or pharmacist, and use each "
            "product as its own directions say. In an emergency call 911; in a mental health crisis call or text 988.")
ASK_WHAT = "What is this?"

# A file is taken only when its own title and words do NOT name a body part, a sexual act, a demonstration model,
# blood or use on a person, AND do name the product, its packaging or a test (checked for every file).
NOT_SAFE = (r"penis|penile|phall\w*|dildo\w*|vagina\w*|vulva\w*|labia|genital\w*|erect\w*|scrotum|testic\w*|breast\w*|"
            r"nipple\w*|naked|nude|nudity|topless|sex|sexual\w*|sexy|intercourse|erotic\w*|porn\w*|fetish\w*|kink\w*|"
            r"bdsm|lingerie|underwear|panties|bikini|anatom\w*|model|demonstrat\w*|banana|cucumber|worn|wearing|"
            r"inserted|insertion|inserting|used|blood\w*|bleed\w*|stain\w*|menses|ultrasound|x-ray|radiograph\w*|"
            r"surgery|surgical|uterus|cervix|womb|child|children|kid|kids|boy|girl|baby|infant|teen\w*")
PRODUCT = (r"condoms?|kondom\w*|preservati\w*|pack\w*|box(es)?|wrapper\w*|foil|dispenser\w*|vending|machine|"
           r"iud|intrauterine|device|implant\w*|nexplanon|implanon|jadelle|cap|patch(es)?|ring|nuvaring|"
           r"contracept\w*|emergency|plan b|levonorgestrel|ulipristal|ella|pill\w*|tablet\w*|spermicid\w*|gel|foam|"
           r"film|sponge|menstrual|cup|tampons?|applicator\w*|pad\w*|cloth|reusable|washable|sanitary|"
           r"hiv|test\w*|kit\w*|self-test\w*|oraquick|rapid|strip\w*|cassette")
SAFE_WORDS = re.compile(rf"^(?!.*\b({NOT_SAFE})\b).*\b({PRODUCT})\b", re.I | re.S)


def thing(category, words, deeper=False):
    """A Commons spec for home_packs.build_commons_topic with the safety filter: (category, deeper, [("What is
    this?", "This is <words>." and the health note)], SAFE_WORDS)."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}. {SEX_NOTE}")], SAFE_WORDS)


CONTRACEPTION_MENSTRUAL = [
    thing("Male condoms", "a male (external) condom, a barrier method of birth control that also lowers the chance "
                          "of sexually transmitted infections"),
    thing("Condoms", "a condom, a barrier method of birth control that also lowers the chance of sexually "
                     "transmitted infections"),
    thing("Female condoms", "a female (internal) condom, a barrier method of birth control that also lowers the "
                            "chance of sexually transmitted infections"),
    thing("Intrauterine devices", "an intrauterine device (IUD), a small T-shaped device that a clinician places to "
                                  "prevent pregnancy for several years; there are copper and hormonal kinds"),
    thing("Contraceptive implants", "a contraceptive implant, a thin rod that a clinician places under the skin of "
                                    "the upper arm; it releases a hormone that prevents pregnancy for several years"),
    thing("Cervical caps", "a cervical cap, a small soft cup used with spermicide to prevent pregnancy"),
    thing("Contraceptive patches", "a contraceptive patch, a skin patch that releases hormones to prevent "
                                   "pregnancy; it is changed on the schedule its directions give"),
    thing("Vaginal rings", "a contraceptive vaginal ring, a small flexible ring that releases hormones to prevent "
                           "pregnancy"),
    thing("Emergency contraception", "emergency contraception, pills taken after unprotected sex to lower the "
                                     "chance of pregnancy; the sooner they are taken, the better they work", True),
    thing("Spermicides", "spermicide, a gel, foam, film or suppository that stops sperm; used alone it is less "
                         "effective than most other birth control methods"),
    thing("Menstrual cups", "a menstrual cup, a soft reusable cup of silicone or rubber for collecting period blood; "
                            "empty, rinse and clean it as its directions say"),
    thing("Tampons", "a tampon, a plug of absorbent material used during a period; change it every 4 to 8 hours and "
                     "use the lowest absorbency you need, to lower the risk of toxic shock syndrome (FDA)"),
    thing("Cloth menstrual pads", "a cloth menstrual pad, a washable, reusable pad used during a period"),
    thing("HIV tests", "an HIV test; with an HIV self-test the result comes at home, and a positive self-test must "
                       "be confirmed by a health care provider (CDC)"),
]


def build_commons_contraception_menstrual(limit):
    """The commons_contraception_menstrual pack (see the module docstring): only files that pass SAFE_WORDS, never a
    file naming a child."""
    from home_packs import build_commons_topic
    return build_commons_topic(CONTRACEPTION_MENSTRUAL, limit, "contramens", adults_only=True)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
SEXUAL_HEALTH_PACKS = {
    "commons_contraception_menstrual": (build_commons_contraception_menstrual, COMMONS_LICENCE.format(
        what="condom, IUD, contraceptive implant, patch and ring, emergency contraception, menstrual cup, tampon, "
             "cloth pad and HIV test")),
}
SEXUAL_HEALTH_LIMITS = {
    "commons_contraception_menstrual": 400,  # 14 categories, about 430 files before the safety filter
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
SEXUAL_HEALTH_COMMONS_KEYS = ("commons_contraception_menstrual",)
# The Commons category specs of the packs (for the self-test).
SEXUAL_HEALTH_SPECS = list(CONTRACEPTION_MENSTRUAL)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the sexual health pack builder.")
    parser.add_argument("key", choices=sorted(SEXUAL_HEALTH_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = SEXUAL_HEALTH_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
