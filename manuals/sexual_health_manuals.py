"""The collection "Contraceptive and period products (instructions for use)" (category key contraceptive_products):
the owner's request of 2026-11-22 (sexual and reproductive health: products only, clinical, nothing explicit).
categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (condoms, contraceptives,
            menstrual cups and fertility trackers); no word another
            collection already searches (pregnancy and ovulation tests and fertility monitors are home_health_tests');
  makers    the big makers, LINK-ONLY by the owner's rule: their own manuals and guides are for the person (or the
            personal assistant) to open in a browser or fetch with Program Downloader; nothing is read from their
            sites (their terms keep all rights);
  guidance  the US government pages the reference library builds in full (textbooks/sexual_health.py: FDA's birth
            control pages and chart, CDC's contraception and STI pages), as links.

The notice is said first (NOTICE): use each product as its own directions say; ask a doctor, nurse or pharmacist; 911
and 988.
"""

NOTICE = ("Use each product exactly as its own directions say. General information, not medical advice or a diagnosis:"
          " ask a doctor, nurse or pharmacist which method fits you. In an emergency call 911; in a mental health "
          "crisis call or text 988.")

IA_WORDS = ["condom", "contraceptive", "contraception", "menstrual cup", "fertility tracker"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="contraceptive_products", prefix="cp", documents="manuals and instructions",
               access="link", reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="opill",
         maker="Opill (Perrigo), the over-the-counter birth control pill",
         type="contraceptive pill",
         library="https://opill.com/",
         site="opill.com"),
    dict(key="plan-b",
         maker="Plan B One-Step (Foundation Consumer Healthcare)",
         type="emergency contraception",
         library="https://www.planbonestep.com/",
         site="planbonestep.com"),
    dict(key="caya",
         maker="Caya (diaphragm)",
         type="diaphragm",
         library="https://caya.us.com/",
         site="caya.us.com"),
    dict(key="trojan",
         maker="Trojan (Church & Dwight)",
         type="condoms",
         library="https://www.trojanbrands.com/",
         site="trojanbrands.com"),
    dict(key="durex",
         maker="Durex (Reckitt)",
         type="condoms",
         library="https://www.durex.com/",
         site="durex.com"),
    dict(key="diva",
         maker="DIVA (DivaCup)",
         type="menstrual cup",
         library="https://divacup.com/",
         site="divacup.com"),
    dict(key="oraquick",
         maker="OraQuick HIV Self-Test (OraSure)",
         type="HIV self-test",
         library="https://www.oraquick.com/",
         site="oraquick.com"),
]]

GUIDANCE = [
               dict(title=("Birth control and the Birth Control Chart (FDA; in the reference library: "
                          "sexhealth:fda_birth_control_menopause and sexhealth:fda_birth_control_chart)"),
                    url="https://www.fda.gov/consumers/womens-health-topics/birth-control",
                    by="the US Food and Drug Administration"),
               dict(title="Contraception (CDC; in the reference library: sexhealth:cdc_contraception_reproductive)",
                    url="https://www.cdc.gov/contraception/index.html",
                    by="the US Centers for Disease Control and Prevention"),
               dict(title="Tampons and menstrual products (FDA)",
                    url="https://www.fda.gov/consumers/consumer-updates/what-you-should-know-about-tampons",
                    by="the US Food and Drug Administration"),
           ]

CATEGORY = dict(
    name="Contraceptive and period products (instructions for use)",
    description=("Condoms, over-the-counter birth control pills, emergency contraception, diaphragms, menstrual cups "
                 "and HIV self-tests: the Internet Archive's instructions, the makers' instruction pages (links) and "
                 "FDA's and CDC's guidance. Products only; links only."),
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
