"""The collection "Home health tests (instructions for use)" (category key home_health_tests): at-home test kits'
Instructions for Use and quick reference guides, the owner's request of 2026-11-22. categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each document belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (pregnancy tests, glucose
            meters, COVID-19 home tests ...), as the other collections;
  udi       the FDA's device identifier database (AccessGUDID through openFDA, public domain): every over-the-counter
            device whose GMDN term has these words, with its brand, model, maker and barcode numbers, so a test kit in
            the hand can be matched by its UPC;
  makers    the makers the owner named (First Response, Clearblue, BinaxNOW, iHealth, Flowflex, Lucira, OraQuick,
            Accu-Chek, OneTouch, FreeStyle, Contour, Everlywell, LetsGetChecked): by the owner's rule their own copies
            of the instructions are LINK-ONLY, for the person (or the personal assistant) to open in a browser;
            nothing is read from their sites;
  guidance  the FDA's and CDC's own pages (US government works), which the reference library builds in full
            (textbooks/home_tests.py): the FDA's home use tests guide, its list of at-home COVID-19 tests with each
            test's Instructions for Use links, and CDC's testing guidance.
The Instructions for Use that FDA posts with emergency use authorisations and clearances are the makers' documents:
FDA's website policies say posted material may be copyrighted, so they are linked (from the FDA list), not copied.

The safety notice is said first: "Follow the test's own instructions; faint lines can be hard to read; contact a
doctor or pharmacist about any result."
"""

SAFETY = ("Follow the test's own instructions; faint lines can be hard to read; contact a doctor or pharmacist about "
          "any result.")

IA_WORDS = ["pregnancy test", "ovulation test", "fertility monitor", "glucose meter", "blood glucose",
            "glucose monitor", "glucometer", "test strips", "lancing device", "cholesterol test", "covid-19 test",
            "covid test", "antigen test", "self test", "home test", "hiv test", "drug test", "alcohol test",
            "breathalyzer", "urine test", "a1c test", "ketone meter", "inr monitor", "coagulation monitor"]

# GMDN words of the FDA identifier database (over-the-counter devices only, build_manuals.udi_entries).
UDI_TERMS = ['"chorionic"', '"luteinizing"', '"glucose"', '"SARS-CoV-2"', '"influenza"', '"HIV1"', '"cholesterol"',
             '"cannabinoid"', '"opiate"', '"amphetamine"', '"faecal"', '"ketone"', '"nitrite"', '"alcohol"',
             '"self-test"']

RULE = ("by the owner's rule the maker's own Instructions for Use and quick reference guides are link-only: nothing "
        "is read from its site; its page is listed for the person to open")
_COMMON = dict(category="home_health_tests", prefix="ht", documents="instructions for use", access="link",
               reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="first-response", maker="First Response (Church & Dwight)", type="pregnancy and ovulation test",
         library="https://www.firstresponse.com/", site="firstresponse.com"),
    dict(key="clearblue", maker="Clearblue (Swiss Precision Diagnostics)", type="pregnancy and ovulation test",
         library="https://www.clearblue.com/", site="clearblue.com"),
    dict(key="binaxnow", maker="BinaxNOW (Abbott)", type="COVID-19 and flu home test",
         library="https://www.globalpointofcare.abbott/us/en/product-details/navica-binaxnow-covid-19-us.html",
         site="globalpointofcare.abbott"),
    dict(key="ihealth", maker="iHealth Labs", type="COVID-19 and flu home test", library="https://ihealthlabs.com/",
         site="ihealthlabs.com"),
    dict(key="flowflex", maker="Flowflex (ACON Laboratories)", type="COVID-19 and flu home test",
         library="https://flowflexcovid.com/", site="flowflexcovid.com"),
    dict(key="lucira", maker="Lucira (Pfizer)", type="COVID-19 and flu molecular home test",
         library="https://www.lucirabypfizer.com/", site="lucirabypfizer.com"),
    dict(key="oraquick", maker="OraQuick (OraSure Technologies)", type="HIV self-test",
         library="https://www.oraquick.com/", site="oraquick.com"),
    dict(key="accu-chek", maker="Accu-Chek (Roche)", type="blood glucose meter", library="https://www.accu-chek.com/",
         site="accu-chek.com"),
    dict(key="onetouch", maker="OneTouch (LifeScan)", type="blood glucose meter", library="https://www.onetouch.com/",
         site="onetouch.com"),
    dict(key="freestyle", maker="FreeStyle (Abbott Diabetes Care)", type="blood glucose meter and sensor",
         library="https://www.freestyle.abbott/us-en/home.html", site="freestyle.abbott"),
    dict(key="contour", maker="Contour (Ascensia Diabetes Care)", type="blood glucose meter",
         library="https://www.diabetes.ascensia.com/", site="diabetes.ascensia.com"),
    dict(key="everlywell", maker="Everlywell", type="home collection kit", library="https://www.everlywell.com/",
         site="everlywell.com"),
    dict(key="letsgetchecked", maker="LetsGetChecked", type="home collection kit",
         library="https://www.letsgetchecked.com/", site="letsgetchecked.com"),
]]

GUIDANCE = [
    dict(title="Home use tests (FDA; built in full in the reference library: hometest:fda_home_use_tests)",
         url="https://www.fda.gov/medical-devices/in-vitro-diagnostics/home-use-tests",
         by="the US Food and Drug Administration"),
    dict(title="At-home OTC COVID-19 diagnostic tests, with each test's Instructions for Use and Quick Reference "
               "links (FDA; in the reference library: hometest:fda_otc_covid_tests)",
         url="https://www.fda.gov/medical-devices/coronavirus-covid-19-and-medical-devices/home-otc-covid-19-"
             "diagnostic-tests", by="the US Food and Drug Administration"),
    dict(title="COVID-19 testing: what you need to know (CDC)", url="https://www.cdc.gov/covid/testing/index.html",
         by="the US Centers for Disease Control and Prevention"),
    dict(title="CLIA-waived tests database (FDA; open it in a browser: it refuses programs)",
         url="https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfClia/analyteswaived.cfm",
         by="the US Food and Drug Administration"),
]

CATEGORY = dict(
    name="Home health tests (instructions for use)",
    description="At-home test kits and meters: pregnancy and ovulation tests, COVID-19, flu and RSV home tests, HIV "
                "self-tests, blood glucose meters and sensors, cholesterol and A1c tests, drug and alcohol tests, "
                "colon cancer (FIT) and urinary tract infection tests, and home collection kits: the makers' "
                "Instructions for Use and quick reference guides (links), the FDA's device records with barcode "
                "numbers, and the FDA's and CDC's guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); FDA device records are public domain; each document belongs to "
                            "its maker",
    ia=IA_WORDS, udi=UDI_TERMS, makers=MAKERS, guidance=GUIDANCE, notice=SAFETY)
