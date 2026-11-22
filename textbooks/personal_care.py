"""Personal care and beauty products for the reference library, in the group "Reference, home health care and first
aid" (the owner's request of 2026-11-22). Keys: personal-care (every book), pcare:<name>.

What this module builds, in plain words:
  - pcare:index, a guide to the library for personal care (the toolkit's own facts and links, CC0): cosmetics safety
    and labels, hair dyes and hair products, tattoos and permanent makeup, oral care, feminine care, recalls, with
    the books by key, the picture packs (including the dental and the contraception and period packs) and the links;
  - IN FULL, three short books from the US Food and Drug Administration's cosmetics pages (US government works, in
    the public domain by FDA's own website policy, checked at every build):
      pcare:fda_cosmetics_safety   using cosmetics safely, the cosmetics questions and answers, cosmetics labels,
                                   allergens and fragrances, cosmetic or drug (or soap), what FDA does and does not
                                   approve, cosmetics in pregnancy, and how to report a problem;
      pcare:fda_cosmetic_products  makeup, novelty makeup, hair products, hair cleansing products, hair dyes (the
                                   patch test, never on eyebrows or eyelashes), hair smoothing products that release
                                   formaldehyde, nail care products, soaps and lotions, tanning products, wipes and
                                   aromatherapy;
      pcare:fda_tattoos            tattoos, temporary tattoos, henna and "black henna", and permanent makeup.
  Every book carries CARE_SAFETY in its notice (the same advice as the picture packs' notes).

Already in the library and not repeated: the FDA Enforcement Report books (cosmetics recalls among food and drugs,
fda:), MedlinePlus's summaries (mlp:health_topics), the dental books (dental-care) and the contraception and period
books (sexual-health).

Not built (NOT_INCLUDED, link-only): Open Beauty Facts (blocks AI crawlers), the makers' product pages (copyright),
the American Academy of Dermatology's pages (copyright), and the CPSC's hair dryer pages (cpsc.gov refuses programs).

Licences: works of the US government; FDA's website policies page says its contents "are not copyrighted. They are
in the public domain".

Run from the repository's folder:
  python3 textbooks/personal_care.py pcare:fda_tattoos --out build/textbooks --limit 3
  python3 textbooks/personal_care.py --list personal-care
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import first_aid as F  # noqa: E402 - the home health group

GROUP = F.GROUP
GROUPS = {}

# The same advice as the picture packs' notes (packs/personal_care_packs.py), written for a book.
CARE_SAFETY = ("Personal care safety (FDA): stop using a product that gives you a rash, redness, itching or swelling, "
               "and tell your doctor; never share eye makeup; do the skin patch test before every hair dye and never "
               "dye eyebrows or eyelashes; sprays, perfumes and nail polish remover can catch fire; keep cosmetics, "
               "mouthwash and nail products away from children, and call Poison Help at 1-800-222-1222 if one is "
               "swallowed. Report a problem with a cosmetic to the FDA.")

FDA = "https://www.fda.gov/cosmetics"
FDA_POLICY = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_TEXT = r"are not copyrighted\. They are in the public domain"
FDA_NOTICE = ("From the US Food and Drug Administration (fda.gov): a US government work, not copyrighted (FDA's "
              "website policies). Pictures are left out.")
FDA_PUBLISHER = "US Food and Drug Administration (FDA)"
PAGES = r"^https://www\.fda\.gov/cosmetics/([a-z0-9-]+/)?[a-z0-9-]+$"

SAFETY_PAGES = [FDA + "/" + p for p in (
    "resources-consumers-cosmetics/using-cosmetics-safely", "resources-consumers-cosmetics/cosmetics-faqs",
    "cosmetics-labeling", "cosmetic-ingredients/allergens-cosmetics", "cosmetic-ingredients/fragrances-cosmetics",
    "cosmetics-laws-regulations/it-cosmetic-drug-or-both-or-it-soap",
    "cosmetics-laws-regulations/fda-authority-over-cosmetics-how-cosmetics-are-not-fda-approved-are-fda-regulated",
    "resources-consumers-cosmetics/cosmetics-pregnancy",
    "cosmetics-compliance-enforcement/how-report-cosmetic-product-related-complaint")]
PRODUCT_PAGES = [FDA + "/cosmetic-products/" + p for p in (
    "makeup", "novelty-makeup", "hair-products", "hair-cleansing-products", "hair-dyes",
    "hair-smoothing-products-release-formaldehyde-when-heated", "nail-care-products", "soaps-lotions",
    "cosmetic-tanning-products", "disposable-wipes", "aromatherapy")]
TATTOO_PAGES = [FDA + "/cosmetic-products/" + p for p in (
    "tattoos-temporary-tattoos-permanent-makeup", "tattoos-permanent-makeup-fact-sheet",
    "temporary-tattoos-hennamehndi-and-black-henna-fact-sheet")]


def fda_book(name, title, subject, urls, description, units):
    """A fixed list of FDA cosmetics pages, each read whole (FDA's policy line checked at every build)."""
    entry = X.page_list_book(GROUP, name, title, subject, FDA_PUBLISHER, urls, PAGES, description,
                             f"{FDA_NOTICE} {CARE_SAFETY}", units=units)
    return dict(entry, licence_page=FDA_POLICY, licence_text=FDA_TEXT)


GUIDES = [
    fda_book("fda_cosmetics_safety", "Using cosmetics safely: labels, allergens and your questions (FDA)",
             "Cosmetics safety", SAFETY_PAGES,
             "The FDA's pages for people who use cosmetics: using cosmetics safely (keep them clean, do not share "
             "them, throw them out when they change), the questions people ask most, what a cosmetic label must say "
             "and what the words on it mean, allergens and fragrances in cosmetics, whether a product is a cosmetic, "
             "a drug, both, or soap, what the FDA does and does not approve, cosmetics during pregnancy, and how to "
             "report a bad reaction or a problem with a product.",
             [(r"labeling|allergens|fragrances", "Labels and ingredients"),
              (r"laws-regulations", "Cosmetics and the law"), (r"report", "Reporting a problem"),
              (r".", "Using cosmetics safely")]),
    fda_book("fda_cosmetic_products", "Makeup, hair dyes, hair and nail products, soaps and lotions (FDA)",
             "Cosmetic products", PRODUCT_PAGES,
             "The FDA's pages on kinds of cosmetic products: makeup and novelty makeup (glitter, face paint), hair "
             "products and hair cleansing products, hair dyes (the skin patch test before every use, never on "
             "eyebrows or eyelashes, allergic reactions), hair smoothing products that release formaldehyde when "
             "heated, nail care products, soaps and lotions, tanning products, disposable wipes and aromatherapy.",
             [(r"hair", "Hair products and hair dyes"), (r"nail", "Nail care"), (r"makeup", "Makeup"),
              (r".", "Skin, soaps and other products")]),
    fda_book("fda_tattoos", "Tattoos, temporary tattoos, henna and permanent makeup (FDA)", "Tattoos and henna",
             TATTOO_PAGES,
             "The FDA's pages on tattoos and permanent makeup (the risks: infections, allergic reactions, "
             "contaminated inks, removal), the fact sheet on tattoos and permanent makeup, and temporary tattoos, "
             "henna (mehndi) and \"black henna\", which can cause serious skin reactions.",
             [(r".", "Tattoos and henna")]),
]

# ====================================================================== the index

SECTIONS = [
    ("Cosmetics safety and labels", "Using makeup and skin care safely, and reading the label.", [
        ("key", "pcare:fda_cosmetics_safety", "Using cosmetics safely: labels, allergens and your questions (FDA)"),
        ("key", "pcare:fda_cosmetic_products", "Makeup, hair dyes, hair and nail products, soaps and lotions (FDA)"),
        ("pack", "commons_personal_care_products", "Makeup, skin care, bath, hair care, shaving and perfume products"),
        ("pack", "open_images_personal_care", "Lip gloss, face powder, makeup brushes, nail care, shavers, soaps and "
                                              "lotions"),
        ("pack", "commons_makeup_grooming", "Cosmetics, eye shadow, foundation, combs, curling irons, shavers"),
        ("pack", "commons_personal", "Shampoo, toothpaste, deodorants, lipsticks, mascara, nail polish, razors")]),
    ("Hair care, hair dyes and hairstyles", "Hair products, hair dyes and the patch test, and hairstyles.", [
        ("key", "pcare:fda_cosmetic_products", "Hair dyes and hair smoothing products (FDA)"),
        ("pack", "commons_hairstyles", "Hairstyles"),
        ("manuals", "personal_care_appliances", "Hair dryer, straightener, curling iron, clipper and trimmer "
                                                "manuals, as links")]),
    ("Tattoos, henna and permanent makeup", "The risks and what to ask before you get one.", [
        ("key", "pcare:fda_tattoos", "Tattoos, temporary tattoos, henna and permanent makeup (FDA)")]),
    ("Oral care", "Toothbrushes, floss, mouthwash and dental care.", [
        ("word", "dental-care", "The dental care books (NIDCR, CDC, NHS)"),
        ("pack", "commons_dental_care", "Toothbrushes, interdental brushes, floss and other oral care things")]),
    ("Feminine care", "Period products and their safety.", [
        ("word", "sexual-health", "The sexual health books, with period products and toxic shock syndrome"),
        ("pack", "commons_contraception_menstrual", "Tampons, pads, menstrual cups and contraceptives")]),
    ("Old cosmetics in museums", "Kohl tubes, perfume bottles and cosmetic boxes.", [
        ("pack", "commons_historic_cosmetics", "Ancient Egyptian cosmetics and ancient perfume bottles"),
        ("pack", "met_historic_cosmetics", "Kohl tubes, cosmetic boxes and perfume bottles at the Met")]),
    ("Recalls and reporting", "When a product is recalled or causes harm.", [
        ("word", "fda-recalls", "The FDA's monthly recall books, with cosmetics recalls"),
        ("link", "Poison Help", "https://poisonhelp.hrsa.gov/", "call 1-800-222-1222 in the US; open it in a "
                                                                 "browser"),
        ("link", "Open Beauty Facts (ingredients of cosmetics by barcode)", "https://world.openbeautyfacts.org/",
         "its site blocks AI crawlers, so nothing is read from it; open it in a browser")]),
]
INDEX = X.index_maker("pcare", GROUP, "Personal care and beauty products: a guide to the library",
                      "Personal care products",
                      "A guide to the library for personal care: cosmetics safety and labels, hair care and hair dyes, "
                      "tattoos and henna, oral care, feminine care, old cosmetics in museums, and recalls.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("pcare", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"personal-care": lambda: ["pcare:index"] + [f"pcare:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "pcare_fda": "www.fda.gov/about-fda/about-website/website-policies (checked at every build): the contents of the "
                 "FDA website \"are not copyrighted. They are in the public domain\"; credit given. robots.txt allows "
                 "/cosmetics/; no AI rules (checked 2026-11-22).",
    "pcare_index": "The index (pcare:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Open Beauty Facts (cosmetics by barcode, ingredients and photos)", "Its site blocks AI crawlers (robots.txt, "
     "checked 2026-11-22), so nothing is read from it. Link-only. Index: https://world.openbeautyfacts.org/"),
    ("Makers' product pages and safety data (L'Oreal, Estee Lauder, Procter & Gamble, Unilever, Johnson & Johnson)",
     "The makers' copyright. Link-only. Index: https://www.cosmeticsinfo.org/"),
    ("American Academy of Dermatology skin, hair and nail care pages", "Copyright of the AAD; link-only. Index: "
     "https://www.aad.org/public/everyday-care"),
    ("CPSC hair dryer and electrical safety pages", "Public information, but www.cpsc.gov refuses programs (403, "
     "checked 2026-11-22). Link-only. Index: https://www.cpsc.gov/Safety-Education/Safety-Guides"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
