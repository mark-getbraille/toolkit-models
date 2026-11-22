"""Sexual and reproductive health for the reference library, in its own group "Reference, sexual and reproductive
health" (the owner's request of 2026-11-22): adult, factual and clinical; nothing explicit. Keys: sexual-health
(every book), sexhealth:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - CDC's contraception and reproductive health pages (every birth control method and how well it works, emergency
    contraception, infertility, menopause and women's reproductive health), kept whole as CDC's terms ask;
  - CDC's sexually transmitted infection and HIV pages (each STI: signs, testing and treatment; getting tested;
    HIV basics, testing, PrEP and PEP, living with HIV), kept whole;
  - the HHS Office of Population Affairs' reproductive health pages (preventing pregnancy and contraception,
    understanding fertility, STIs, preventing HIV, reproductive cancers);
  - the Office on Women's Health's menstrual cycle, menopause and relationships and safety pages (periods and
    period problems, menopause symptoms and treatment, healthy relationships, domestic and intimate partner
    violence, sexual assault, getting help);
  - CDC's intimate partner violence and sexual violence prevention pages, kept whole;
  - FDA's birth control and menopause pages, and FDA's Birth Control Chart (2024), the whole PDF;
  - NIDDK's erectile dysfunction pages (causes, diagnosis, treatment);
  - "Help lines": a page written for this library with the National Domestic Violence Hotline and the National
    Sexual Assault Hotline (RAINN), checked on CDC's page at every build.
  (NICHD's fertility and infertility topics are already parent:nichd_health_topics, the pregnancy guides
  early:owh_pregnancy_breastfeeding and the home test kits hometest:: not repeated.)

Every book's notice ends with the health note: general information, not medical advice or a diagnosis; in an
emergency call 911; in a mental health crisis call or text 988.

Not built (NOT_INCLUDED, link-only): HIV.gov (its robots.txt refuses every page), RAINN's site (refuses programs),
Planned Parenthood, Mayo Clinic, Scarleteen and the American Sexual Health Association (copyright), the National
Institute on Aging's sexuality and menopause pages (bot check), and CDC's LGBTQ+ health pages (moved; MedlinePlus's
LGBTQ+ health summary is in mlp:health_topics).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's terms and the Office on Women's Health's disclaimer are checked at every build and their conditions
met in the notice.

Run from the repository's folder:
  python3 textbooks/sexual_health.py sexhealth:help_lines --out build/textbooks
  python3 textbooks/sexual_health.py --list sexual-health
"""

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared helpers and notes of the four new health modules

GROUP = "sexualhealth"
GROUPS = {GROUP: "Reference, sexual and reproductive health"}
NOTE = ("General information, not medical advice or a diagnosis: ask a doctor, nurse or pharmacist, and use each "
        "product as its own directions say. In an emergency call 911; in a mental health crisis call or text 988.")

HELP_CHECKS = [
    ("Abuse and violence", M.CDC_HELP, r"800-799-SAFE \(7233\) Text \"?START\"? to 88788",
     "National Domestic Violence Hotline: call 1-800-799-SAFE (1-800-799-7233), text START to 88788, or chat at "
     "thehotline.org, free and confidential, 24 hours a day; TTY 1-800-787-3224."),
    ("Abuse and violence", M.CDC_HELP, r"800-656-HOPE \(4673\)",
     "National Sexual Assault Hotline (RAINN): call 1-800-656-HOPE (1-800-656-4673) or chat online, free and "
     "confidential, 24 hours a day."),
    ("Abuse and violence", M.CDC_HELP, r"1-888-373-7888",
     "National Human Trafficking Hotline: call 1-888-373-7888, 24 hours a day, in more than 200 languages."),
]


def help_book(name, work, cache=None, left_out=None, limit=None):
    """The abuse and violence help lines page, its numbers checked on CDC's page now."""
    return M.help_lines_book("sexhealth", GROUP, name, "Help lines: domestic violence, sexual assault and "
                             "trafficking (US)", "Abuse and violence help lines", HELP_CHECKS,
                             "If you are in danger right now, call 911.", "The US hotlines for domestic violence, "
                             "sexual assault and human trafficking, checked on CDC's page when the book was made.",
                             NOTE, cache=cache)


# FDA's website policy, as in fitness_nutrition.py (checked at every build).
FDA_TERMS = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_TEXT = r"are not copyrighted\. They are in the public domain"

GUIDES = [
    M.cdc_book(GROUP, "cdc_contraception_reproductive", "Contraception, infertility and reproductive health (CDC)",
               "Contraception and reproductive health", ["contraception", "reproductive-health"],
               "CDC's contraception and reproductive health pages, every page: the birth control methods (the "
               "implant, IUDs, the shot, the pill, the patch, the ring, the diaphragm, condoms, fertility awareness, "
               "sterilisation, emergency contraception) and how well each works, choosing a method, infertility "
               "(causes, treatment, assisted reproductive technology), women's reproductive health and menopause.",
               units=[(r"/contraception/", "Contraception"), (r".", "Reproductive health and infertility")],
               note=NOTE),
    M.cdc_book(GROUP, "cdc_sti_hiv", "Sexually transmitted infections and HIV: prevention, testing and treatment (CDC)",
               "STIs and HIV", ["sti", "hiv"],
               "CDC's STI and HIV pages, every page: each sexually transmitted infection (chlamydia, gonorrhoea, "
               "syphilis, herpes, HPV, trichomoniasis, mycoplasma genitalium and others: signs, testing and "
               "treatment), how to lower the risk, getting tested and treated; HIV basics, testing (including "
               "self-tests), PrEP and PEP, treatment as prevention, and living with HIV.",
               units=[(r"/hiv/", "HIV"), (r".", "Sexually transmitted infections")], note=NOTE, limit=500),
    K.guide(GROUP, "opa_reproductive_health", "Contraception, fertility, STIs and HIV prevention (HHS Office of "
            "Population Affairs)", "Contraception and reproductive health", "Office of Population Affairs (OPA), US "
            "Department of Health and Human Services", "https://opa.hhs.gov/reproductive-health",
            r"^https://opa\.hhs\.gov/reproductive-health(/[a-z0-9-]+){0,2}$",
            "The Office of Population Affairs' reproductive health pages, every page: preventing pregnancy and the "
            "contraceptive methods, understanding fertility basics, sexually transmitted infections, preventing "
            "HIV, and reproductive cancers.",
            f"A work of the US Department of Health and Human Services (public domain). {NOTE}", depth=2,
            follow=r"^https://opa\.hhs\.gov/reproductive-health/[a-z0-9-]+$", limit=60),
    M.owh_book(GROUP, "owh_periods_menopause_relationships", "Periods, menopause, and relationships and safety "
               "(Office on Women's Health)", "Menstruation, menopause and relationships",
               ["menstrual-cycle", "menopause", "relationships-and-safety"],
               "The Office on Women's Health's pages, every page: the menstrual cycle (your period, period problems, "
               "premenstrual syndrome, heavy bleeding, endometriosis), menopause (the signs, treatment of symptoms, "
               "menopause hormone therapy, health after menopause) and relationships and safety (healthy "
               "relationships, domestic and intimate partner violence, sexual assault and rape, how to get help, "
               "leaving safely).",
               NOTE + " If you are being hurt: the National Domestic Violence Hotline, 1-800-799-7233.", limit=250),
    M.cdc_book(GROUP, "cdc_violence_prevention", "Intimate partner violence and sexual violence (CDC)",
               "Healthy relationships and violence prevention", ["intimate-partner-violence", "sexual-violence"],
               "CDC's pages on intimate partner violence and sexual violence, every page: what they are, the signs, "
               "risk and protective factors, healthy relationships and consent, how to prevent them, and where to "
               "get help.", units=[(r"/sexual-violence/", "Sexual violence"), (r".", "Intimate partner violence")],
               note=NOTE),
    dict(M.pages_book(GROUP, "fda_birth_control_menopause", "Birth control and menopause (FDA Office of Women's "
                      "Health)", "Contraception and menopause", "US Food and Drug Administration (FDA)",
                      ["https://www.fda.gov/consumers/womens-health-topics/birth-control",
                       "https://www.fda.gov/consumers/womens-health-topics/menopause"],
                      r"^https://www\.fda\.gov/consumers/womens-health-topics/(birth-control|menopause)$",
                      "FDA's pages on birth control (the FDA-approved methods, how to choose, how well each works, "
                      "the over-the-counter options and the questions to ask) and on menopause (its symptoms and the "
                      "FDA-approved treatments, with their risks).",
                      "From the US Food and Drug Administration: \"the contents of the FDA website ... are not "
                      "copyrighted\"; credit to the US Food and Drug Administration. " + NOTE),
         licence_page=FDA_TERMS, licence_text=FDA_TEXT),
    K.guide(GROUP, "niddk_erectile_dysfunction", "Erectile dysfunction (NIDDK)", "Sexual function",
            "National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), National Institutes of Health",
            "https://www.niddk.nih.gov/health-information/urologic-diseases/erectile-dysfunction",
            r"^https://www\.niddk\.nih\.gov/health-information/urologic-diseases/erectile-dysfunction(/[a-z0-9-]+)?$",
            "NIDDK's erectile dysfunction pages, every page: what it is and how common it is, its symptoms and "
            "causes (including diabetes, heart disease, medicines and emotional factors), diagnosis, treatment "
            "(lifestyle changes, counselling, medicines, devices and surgery) and eating, diet and nutrition.",
            f"A work of the National Institutes of Health (public domain). {NOTE}", depth=1, limit=20),
]

PDFS = [
    K.us_pdf(GROUP, name="fda_birth_control_chart", title="Birth Control Chart (FDA Office of Women's Health, 2024)",
             subject="Contraception", publisher="US Food and Drug Administration, Office of Women's Health",
             pdf="https://www.fda.gov/media/150299/download",
             page="https://www.fda.gov/consumers/womens-health-topics/birth-control", published="2024",
             version="2024 edition (FDA_OWH_BirthControlChart_English_2024)", licence_page=FDA_TERMS,
             licence_text=FDA_TEXT,
             description="FDA's chart of the FDA-approved birth control methods: for each one, how it works, how "
                         "often it is used, how many women out of 100 may get pregnant in a year of typical use, and "
                         "its possible side effects and risks.",
             notice="From the US Food and Drug Administration (not copyrighted; credit to FDA). " + NOTE),
]

COLLECTION = K.Collection("sexhealth", GROUP, guides=GUIDES, pdfs=PDFS,
                          makers={"help_lines": (help_book, lambda name: datetime.date.today().strftime("%Y-%m"))},
                          words={"sexual-health": lambda: [f"sexhealth:{g['name']}" for g in GUIDES + PDFS] +
                                 ["sexhealth:help_lines"]})

LICENCE_LINES = {
    "sexhealth_cdc_owh": "CDC's terms (as mind_cdc) and OWH's disclaimer (as mind_owh), checked at every build; the "
                         "CDC pages are kept whole with CDC's conditions in the notice.",
    "sexhealth_fda": "www.fda.gov/about-fda/about-website/website-policies (checked at every build): \"the contents "
                     "of the FDA website ... are not copyrighted. They are in the public domain\"; credit to FDA.",
    "sexhealth_opa_niddk": "opa.hhs.gov and www.niddk.nih.gov: works of the US government (17 U.S.C. 105, checked on "
                           "govinfo.gov's policies page at every build); robots.txt allows the pages; no AI rules "
                           "(checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("HIV.gov (HIV basics, testing, prevention, living well)", "Its robots.txt line \"Disallow: *#query=*\" reads, by "
     "the robots.txt standard (a \"#\" begins a comment), as \"Disallow: *\": every page is refused (checked "
     "2026-11-22). CDC's HIV pages are built (sexhealth:cdc_sti_hiv). Link-only. Index: "
     "https://www.hiv.gov/hiv-basics"),
    ("RAINN (rainn.org): sexual assault information and the hotline's own pages", "rainn.org answers programs \"403 "
     "Forbidden\" (checked 2026-11-22), and its pages are copyright; the hotline's number is stated from CDC's page "
     "(sexhealth:help_lines). Link-only. Index: https://rainn.org/"),
    ("The National Domestic Violence Hotline's guides (thehotline.org)", "Copyright of the National Domestic Violence "
     "Hotline; only the numbers are stated (sexhealth:help_lines). Link-only. Index: https://www.thehotline.org/"),
    ("Planned Parenthood, Mayo Clinic, Scarleteen, the American Sexual Health Association and Bedsider",
     "Copyright, not openly licensed (checked 2026-11-22). Link-only. Index: https://www.plannedparenthood.org/ , "
     "https://www.ashasexualhealth.org/ and https://www.bedsider.org/"),
    ("National Institute on Aging: sexuality in later life and menopause", "Public domain, but www.nia.nih.gov "
     "answers programs with a bot check (\"405\"; checked 2026-11-22). OWH's menopause pages are built instead. "
     "Link-only. Index: https://www.nia.nih.gov/health/menopause"),
    ("CDC LGBTQ+ health pages and NIH's Sexual and Gender Minority Research Office", "CDC's old LGBT health site "
     "(www.cdc.gov/lgbthealth) answered \"404\" when checked on 2026-11-22 and no new site index was found; the NIH "
     "office's pages are about research, not health advice. MedlinePlus's LGBTQ+ health summary is in "
     "mlp:health_topics. Link-only. Index: https://medlineplus.gov/lgbtqihealth.html"),
    ("FDA's birth control chart in other languages", "Only the English chart is built "
     "(sexhealth:fda_birth_control_chart); FDA also offers it in Spanish and other languages. Index: "
     "https://www.fda.gov/consumers/womens-health-topics/birth-control"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
