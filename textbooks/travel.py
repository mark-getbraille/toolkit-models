"""Travel for the reference library, in the group "Reference, travel" (the owner's request of 2026-11-22). Keys: travel
(every book), trip:<name>. (The key prefix is "trip" because "travel:" already names transport_rights.py's books.)

What this module builds, in plain words, each IN FULL:
  - USA.gov's travel pages: passports (applying, renewing, children's passports, lost passports), travel documents
    for children and for foreign citizens, travelling abroad (alerts, getting help abroad, money abroad), travel
    within the US, REAL ID, and driving in the US as a non-citizen;
  - the FAA's PackSafe pages: what you may pack in carry-on and checked bags (batteries and power banks, medical
    oxygen and other medical devices, lighters, aerosols, mobility aids with batteries) and why;
  - the National Park Service's pages on the America the Beautiful passes (with the free lifetime Access Pass for
    US citizens and permanent residents with a permanent disability) and on accessibility in the parks.
  The synthetic (SPECIMEN) passports and boarding passes and the travel signs are picture packs:
  packs/travel_packs.py.

Already in the library and not repeated: the Air Carrier Access Act rule, 14 CFR part 382 (law:cfr_14_382_air_travel_
disability), the Access Board's transport guidelines (transport), the ADA's service animal pages (legal:ada_gov),
CDC's Yellow Book, Health Information for International Travel (firstaid:cdc_yellow_book: travel health, medicines
and vaccines), USDA APHIS's pet travel pages (home:aphis_pets), and, in the Kiwix library, Wikivoyage and CDC's
Travelers' Health pages.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): travel.state.gov (passports, visas, country
information, driving abroad), TSA (TSA Cares, what can I bring), the Department of Transportation's Fly Rights and
disabled passenger pages, US Customs and Border Protection (Know Before You Go, travelling with medicines): all
answer programs "403"; Amtrak (copyright and refuses programs).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
the Park Service's own public domain statement is checked at every build. robots.txt of usa.gov (10 seconds between
pages, which the builder keeps), faa.gov and nps.gov (5 seconds) allow the pages; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/travel.py trip:faa_packsafe --out build/textbooks --limit 5
  python3 textbooks/travel.py --list travel
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "travel"
GROUPS = {GROUP: "Reference, travel"}
TRAVEL_NOTE = ("Rules, fees and documents change: check the agency's own site before you travel. In an emergency "
               "abroad, call the nearest US embassy or consulate.")

USA = "https://www.usa.gov"
USA_TRAVEL_HUBS = ["travel", "passport", "travel-abroad", "travel-documents-children",
                   "travel-documents-foreign-citizens", "travel-money", "travel-to-within-us", "real-id",
                   "non-citizen-driving"]
# USA.gov's pages that are not about travel (menus, other topics' hubs): never kept.
USA_NOT_TRAVEL = ("about|about-the-us|accessibility-policy|agency-index|benefits|blog|branches-of-government|"
                  "immigration-and-citizenship|money|partner-with-usagov|phone|privacy-security|site-issue-report-form|"
                  "voting-and-elections|espanol|contact|search|life-events|state-governments|federal-agencies|"
                  "holidays|presidents|tribes|local-governments|elected-officials|forms|laws-and-regulations|"
                  "housing-help|scams-and-fraud|jobs-and-unemployment|health-insurance|disability-services|"
                  "website-analytics|benefit-finder")

NPS = "https://www.nps.gov"
NPS_TERMS = NPS + "/aboutus/disclaimer.htm"
NPS_TEXT = r"material created by the National Park Service and presented on this website, unless otherwise " \
           r"indicated, is generally considered in the public domain"
NPS_PAGES = [NPS + "/planyourvisit/passes.htm", NPS + "/aboutus/accessibility.htm"]

GUIDES = [
    K.guide(GROUP, "usa_gov_travel", "Passports, travel documents, travelling abroad and REAL ID (USA.gov)",
            "Passports and travel documents", "USAGov, General Services Administration (USA.gov)",
            [f"{USA}/{h}" for h in USA_TRAVEL_HUBS], rf"^https://www\.usa\.gov/(?!(?:{USA_NOT_TRAVEL})$)[a-z0-9-]+$",
            "USA.gov's travel pages: how to apply for or renew a passport, passport cards, expedited passports, "
            "lost or stolen passports, travel documents for children and for foreign citizens visiting the US, "
            "travelling abroad (travel advisories, getting help from an embassy, money and credit cards abroad), "
            "travel within the US, REAL ID for flying in the US, and driving in the US as a non-citizen.",
            f"A work of the US government (USAGov, General Services Administration; public domain). {TRAVEL_NOTE}",
            units=[(r"/passport", "Passports"), (r"/travel-documents|/real-id|/non-citizen", "Travel documents"),
                   (r"/travel-abroad|/travel-money|/abroad", "Travelling abroad"), (r".", "Travel")], limit=80),
    K.guide(GROUP, "faa_packsafe", "PackSafe: what you can pack in carry-on and checked bags (FAA)",
            "Air travel: packing batteries, medical devices and other items", "Federal Aviation Administration (FAA)",
            "https://www.faa.gov/hazmat/packsafe", r"^https://www\.faa\.gov/hazmat/packsafe(/[a-z0-9_-]+)*$",
            "The FAA's PackSafe pages: which items may go in carry-on and checked bags and how to pack them safely: "
            "lithium batteries, power banks and spare batteries (carry-on only), electronic cigarettes and vapes, "
            "medical oxygen and portable oxygen concentrators, medical devices and mobility aids with batteries, "
            "lighters and matches, aerosols, and what to do if a device overheats on board.",
            f"A work of the Federal Aviation Administration (public domain). Your airline and TSA may have their own "
            f"rules; ask the airline about mobility aids and medical devices before you fly. {TRAVEL_NOTE}",
            depth=2, follow=r"^https://www\.faa\.gov/hazmat/packsafe(/[a-z0-9_-]+)?$", limit=80),
    dict(K.us_web(GROUP, name="nps_passes_accessibility", title="National park passes (with the free Access Pass) and "
                  "accessibility in the parks (National Park Service)", subject="Parks: passes and accessibility",
                  publisher="National Park Service (US Department of the Interior)", source=NPS_PAGES[0],
                  description="The Park Service's pages on the America the Beautiful passes (the annual, senior, "
                              "military, fourth-grade and volunteer passes, and the free lifetime Access Pass for US "
                              "citizens and permanent residents with a permanent disability: who may get it and how) "
                              "and on accessibility in the national parks.",
                  notice=f"From the National Park Service: \"material created by the National Park Service ... is "
                         f"generally considered in the public domain\"; source: National Park Service (nps.gov). "
                         f"Each park has its own accessibility page. {TRAVEL_NOTE}",
                  crawl=[(NPS_PAGES[0], 0)], urls=list(NPS_PAGES),
                  pages=r"^https://www\.nps\.gov/(planyourvisit/passes|aboutus/accessibility)\.htm$",
                  content=(r'<div id="main" role="main" class="MainContent">',
                           r'<div id="related_content_position">|<footer\b'),
                  unit_rules=[(r"passes", "Passes"), (r".", "Accessibility")], limit=5),
         licence_page=NPS_TERMS, licence_text=NPS_TEXT),
]

COLLECTION = K.Collection("trip", GROUP, guides=GUIDES,
                          words={"travel": lambda: [f"trip:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "trip_usa_faa": "www.usa.gov and www.faa.gov: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
                    "policies page at every build); usa.gov's robots.txt asks 10 seconds between pages, which the "
                    "builder keeps; no AI rules (checked 2026-11-22).",
    "trip_nps": "www.nps.gov/aboutus/disclaimer.htm (checked at every build): NPS material \"is generally considered "
                "in the public domain\", credited in the notice; 5 seconds between pages as its robots.txt asks.",
}

NOT_INCLUDED = [
    ("travel.state.gov: passports, visas, country information pages, travel advisories, driving abroad and the "
     "Smart Traveler Enrollment Program", "Public domain, but travel.state.gov answers programs \"403\", "
     "robots.txt included (checked 2026-11-22). USA.gov's passport and travel pages are built (trip:usa_gov_travel). "
     "Link-only. Index: https://travel.state.gov/content/travel/en/international-travel.html"),
    ("TSA: TSA Cares (help for travellers with disabilities and medical conditions: 855-787-2227), What Can I Bring?, "
     "screening with disabilities and medical devices", "Public domain, but www.tsa.gov answers programs \"403\" "
     "(checked again 2026-11-22). The FAA's PackSafe is built (trip:faa_packsafe). Link-only. Index: "
     "https://www.tsa.gov/travel/tsa-cares and https://www.tsa.gov/travel/security-screening/whatcanibring/all"),
    ("Fly Rights and the Department of Transportation's pages for passengers with disabilities (Air Carrier Access "
     "Act, service animals, wheelchairs)", "Public domain, but www.transportation.gov answers programs \"403\" "
     "(checked 2026-11-22), and no Internet Archive copy of the current PDF was found. The rule itself is built "
     "(law:cfr_14_382_air_travel_disability). Link-only. Index: https://www.transportation.gov/airconsumer/"
     "fly-rights"),
    ("US Customs and Border Protection: Know Before You Go, travelling with medicines, what you may bring back",
     "Public domain, but www.cbp.gov answers programs \"403\", robots.txt included (checked 2026-11-22). Link-only. "
     "Index: https://www.cbp.gov/travel/us-citizens/know-before-you-go"),
    ("Amtrak accessibility and travel information", "Amtrak's own copyright, and www.amtrak.com answers programs "
     "\"403\" (checked 2026-11-22). Link-only. Index: https://www.amtrak.com/accessible-travel-services"),
    ("CDC Yellow Book (travel health, travelling with medicines, vaccines)", "Already built in full "
     "(firstaid:cdc_yellow_book); CDC's Travelers' Health pages are also in the Kiwix library. Index: "
     "https://www.cdc.gov/yellow-book/"),
    ("Wikivoyage travel guides", "CC BY-SA, already whole in the Kiwix library; its phrasebooks are built "
     "(lang:wikivoyage_phrasebooks). Index: https://en.wikivoyage.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
