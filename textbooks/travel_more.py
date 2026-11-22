"""More travel for the reference library, in the group "Reference, travel" (the owner's request of 2026-11-22: flesh
out travel; a sibling of travel.py, trip:). Keys: tripmore:<name>. Request word: travel-more (every book here).

The government travel sites that refused programs before (travel.py's NOT_INCLUDED) were tried again this way:
govinfo.gov first, the Internet Archive second.
  - govinfo.gov: its search API needs a free api.data.gov key, so tripmore:govinfo_travel_publications is a SIGN-UP
    ENTRY (govinfo_kit.govinfo_search_maker): with the owner's key in GOVINFO_API_KEY it searches govinfo's agency
    publications (collection GOVPUB) for State Department, TSA, Transportation and Customs travel booklets and reads
    each one's public PDF; without the key the manifest says where to sign up. (govinfo's public pages refuse
    robots on its search, so nothing is searched without the key.)
  - the Internet Archive: the Wayback Machine's exact copies of the official pages ("id_" captures, each pinned by
    its date; govinfo_kit.wayback_book), read IN FULL:
      tripmore:dot_fly_rights_wayback: the Department of Transportation's Fly Rights (the consumer guide to air
        travel) and its pages on refunds, bumping and oversales, and service animals;
      tripmore:tsa_wayback: TSA Cares (help for travellers with disabilities and medical conditions), the special
        procedures for screening, the medical items of "What Can I Bring?", travel tips and the questions people ask;
      tripmore:cbp_know_before_you_go_wayback: Customs and Border Protection's Know Before You Go for US citizens
        and its page on prohibited and restricted items;
      tripmore:state_travel_wayback: the State Department's travel pages: international travel, the traveller's
        checklist, travellers with special considerations, your health abroad, emergencies, driving abroad, and
        passports and how to apply.
    Old Internet Archive scans of State Department booklets of the 1980s ("Your Trip Abroad", "A Safe Trip Abroad",
    "Tips for Travelers to ...") were found too, but their rules and phone numbers are decades out of date and they
    are microfiche scans: not built (NOT_INCLUDED).
  - national parks and public lands, as historical guides: the Department of the Interior's National Parks
    Portfolio (1916) and Glimpses of Our National Parks (1916), works of the US government published before 1931.
  - historic travel guides published before 1931, each marked as historical (OLD_GUIDE_NOTE): Baedeker's The United
    States (1909), The Dominion of Canada (1907), London and Its Environs (1911), Paris and Environs (1913) and Egypt
    and the Sudan (1914), and the Lincoln Highway Association's Complete Official Road Guide (1918).

Already in the library and not repeated: travel.py (trip:: USA.gov passports and travel, FAA PackSafe, park passes
and accessibility), transport_rights.py (travel:: the Air Carrier Access Act rule, the Access Board), the CDC Yellow
Book (firstaid:cdc_yellow_book), the Forest Service's and Park Service's outdoor safety pages (outdoors:), national
park campgrounds (rvs:), Wikivoyage (whole in the Kiwix library) and its phrasebooks (lang:wikivoyage_phrasebooks).

Not built (NOT_INCLUDED): Amtrak (copyright), the Bureau of Land Management's and Recreation.gov's pages (not
checked yet), today's commercial guidebooks (copyright) and the old State Department booklets.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
the old guides are public domain as published before 1931 (the year checked on the Internet Archive's record at every
build).

Run from the repository's folder:
  python3 textbooks/travel_more.py tripmore:tsa_wayback --out build/textbooks --limit 3
  python3 textbooks/travel_more.py --list travel-more
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import govinfo_kit as GK  # noqa: E402
import refs_kit as K  # noqa: E402
import travel as T  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = T.GROUP                        # "travel": the same group as travel.py
GROUPS = dict(T.GROUPS)                # {"travel": "Reference, travel"}
TRAVEL_NOTE = T.TRAVEL_NOTE

# What is said in every old guide's description ("{year}" is filled in): it is marked as historical.
OLD_GUIDE_NOTE = ("Published in {year}: a historical travel guide, kept for its history. Its routes, prices, hotels, "
                  "timetables, rules and borders are those of {year} and none of it is current; its views of the "
                  "peoples and places it describes are those of its time, and some are outdated and offensive. Do "
                  "not plan a trip from it.")

DOT = "https://www.transportation.gov"
TSA = "https://www.tsa.gov"
CBP = "https://www.cbp.gov"
STATE = "https://travel.state.gov/content/travel/en"
DRUPAL_MAIN = (r"<main\b[^>]*>", r"</main>")

# (capture stamp, official address): the Wayback Machine's captures found with its availability API on 2026-11-22;
# captures older than 2024 were not taken (rules change).
DOT_PAGES = [("20261115231232", f"{DOT}/airconsumer/fly-rights"),
             ("20261115225156", f"{DOT}/individuals/aviation-consumer-protection/refunds"),
             ("20261025054931", f"{DOT}/individuals/aviation-consumer-protection/bumping-oversales"),
             ("20240804005355", f"{DOT}/individuals/aviation-consumer-protection/service-animals")]
TSA_PAGES = [("20261118060307", f"{TSA}/travel/tsa-cares"),
             ("20261111071346", f"{TSA}/travel/security-screening/whatcanibring/medical"),
             ("20261116103948", f"{TSA}/travel/travel-tips"),
             ("20261107011528", f"{TSA}/travel/frequently-asked-questions"),
             ("20261116115312", f"{TSA}/travel/security-screening/whatcanibring/all")]
CBP_PAGES = [("20261117154109", f"{CBP}/travel/us-citizens/know-before-you-go"),
             ("20261121191416", f"{CBP}/travel/us-citizens/know-before-you-go/prohibited-and-restricted-items")]
STATE_PAGES = [("20250812091410", f"{STATE}/international-travel.html"),
               ("20250808213855", f"{STATE}/international-travel/before-you-go/travelers-checklist.html"),
               ("20250809223112", f"{STATE}/international-travel/before-you-go/travelers-with-special-"
                                  "considerations.html"),
               ("20250809141930", f"{STATE}/international-travel/before-you-go/your-health-abroad.html"),
               ("20250714124707", f"{STATE}/international-travel/before-you-go/driving-and-road-safety.html"),
               ("20250729112819", f"{STATE}/international-travel/emergencies.html"),
               ("20260526062616", f"{STATE}/passports.html"),
               ("20260516165259", f"{STATE}/passports/how-apply.html")]

GUIDES = [
    GK.wayback_book(GROUP, "dot_fly_rights_wayback", "Fly Rights and air travel consumer rights: refunds, bumping, "
                    "service animals (US Department of Transportation)", "Air travel: passengers' rights",
                    "US Department of Transportation, Office of Aviation Consumer Protection", DOT_PAGES,
                    "The Department of Transportation's Fly Rights, its consumer guide to air travel (fares, "
                    "reservations and tickets, delays and cancellations, overbooking, baggage, passengers with "
                    "disabilities, complaints), and its pages on refunds, on bumping and oversales, and on service "
                    "animals on flights.",
                    f"A work of the US Department of Transportation (public domain). {TRAVEL_NOTE}",
                    units=[(r"fly-rights", "Fly Rights"), (r".", "Passengers' rights")], content=DRUPAL_MAIN),
    GK.wayback_book(GROUP, "tsa_wayback", "TSA Cares and airport screening: disabilities, medical items, what you can "
                    "bring (Transportation Security Administration)", "Air travel: security screening",
                    "Transportation Security Administration (TSA), US Department of Homeland Security", TSA_PAGES,
                    "TSA's pages for travellers: TSA Cares (the helpline for travellers with disabilities and medical "
                    "conditions, 855-787-2227, and asking for a passenger support specialist), screening of medical "
                    "items, medicines and devices, travel tips, the questions people ask, and the first page of the "
                    "What Can I Bring? list (items allowed in carry-on and checked bags).",
                    f"A work of the Transportation Security Administration (public domain). Your airline may have its "
                    f"own rules. {TRAVEL_NOTE}",
                    units=[(r"tsa-cares|medical", "Disabilities and medical conditions"), (r"whatcanibring/all",
                                                                                           "What can I bring?"),
                           (r".", "Travel tips")], content=DRUPAL_MAIN),
    GK.wayback_book(GROUP, "cbp_know_before_you_go_wayback", "Know Before You Go: coming back to the US through "
                    "customs (US Customs and Border Protection)", "International travel: customs",
                    "US Customs and Border Protection (CBP), US Department of Homeland Security", CBP_PAGES,
                    "Customs and Border Protection's guide for US citizens returning from abroad: travel documents, "
                    "declaring what you bring back, duty-free exemptions, and the prohibited and restricted items "
                    "(food, plants, animals, medicines, money over $10,000, firearms and more).",
                    f"A work of US Customs and Border Protection (public domain). {TRAVEL_NOTE}",
                    content=DRUPAL_MAIN),
    GK.wayback_book(GROUP, "state_travel_wayback", "International travel and passports: checklist, health abroad, "
                    "emergencies, driving (US Department of State)", "International travel and passports",
                    "Bureau of Consular Affairs, US Department of State (travel.state.gov)", STATE_PAGES,
                    "The State Department's travel pages: international travel, the traveller's checklist, travellers "
                    "with special considerations (disabilities, older travellers, students and others), your health "
                    "abroad, emergencies abroad, driving and road safety abroad, and passports and how to apply.",
                    f"A work of the US Department of State (public domain). {TRAVEL_NOTE}",
                    units=[(r"passport", "Passports"), (r".", "Travelling abroad")]),
]

GOVINFO_BOOK = GK.govinfo_search_maker(
    "tripmore", GROUP, "govinfo_travel_publications", "Government travel booklets from govinfo.gov (State, TSA, "
    "Transportation, Customs)", "Travel: government booklets",
    "Travel booklets of the State Department, TSA, the Department of Transportation and Customs and Border "
    "Protection found on govinfo.gov (the federal agencies' own publications), each read whole from its public PDF. "
    "A sign-up entry: it needs the owner's free api.data.gov key.",
    f"Works of the US government (public domain), from govinfo.gov. Older booklets may be out of date. {TRAVEL_NOTE}",
    "(travel OR traveler OR traveling OR passport OR \"fly rights\" OR customs) AND (\"Department of State\" OR "
    "\"Transportation Security Administration\" OR \"Department of Transportation\" OR \"Customs and Border\")",
    r"travel|passport|fly rights|know before you go|abroad|airline|air travel")

PARKS_NOTICE = ("A work of the US Department of the Interior (public domain), published in 1916: a historical guide. "
                "Park roads, fees, hotels and rules have all changed; see today's park pages (trip:nps_passes_"
                "accessibility and nps.gov).")


def _old(name, title, subject, publisher, archive, year, description, country="United States", notice=""):
    """One old travel guide of the Internet Archive (old_ia_books.old_book), marked as historical."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=OLD_GUIDE_NOTE,
                    notice=notice, country=country)


PDFS = [
    _old("interior_national_parks_portfolio_1916", "National Parks Portfolio (Robert Sterling Yard, US Department of "
         "the Interior, 1916)", "National parks: historical guide", "US Department of the Interior (Robert Sterling "
         "Yard)", "nationalparkspor1916unit", 1916,
         "The Department of the Interior's illustrated portfolio of the national parks in the year the National Park "
         "Service was created: Yellowstone, Yosemite, Sequoia, Mount Rainier, Crater Lake, Mesa Verde, Glacier, Rocky "
         "Mountain and the others, with the Grand Canyon. Its photographs are described only by their captions.",
         notice=PARKS_NOTICE),
    _old("interior_glimpses_national_parks_1916", "Glimpses of Our National Parks (US Department of the Interior, "
         "1916)", "National parks: historical guide", "US Department of the Interior", "glimpsesofournat00unit", 1916,
         "A short guide by the Department of the Interior to the national parks of 1916: what each park is, how to "
         "get there and what to see.", notice=PARKS_NOTICE),
    _old("baedeker_united_states_1909", "The United States, with Excursions to Mexico, Cuba, Porto Rico and Alaska: "
         "Handbook for Travellers (Karl Baedeker, 4th edition, 1909)", "Historical travel guide: the United States",
         "Karl Baedeker (Leipzig; Charles Scribner's Sons, New York)", "unitedstateswith00karl", 1909,
         "Baedeker's guide to the United States of 1909: routes by rail and steamer, the cities and their sights, the "
         "national parks, and excursions to Mexico, Cuba, Puerto Rico and Alaska.", country="Germany"),
    _old("baedeker_dominion_of_canada_1907", "The Dominion of Canada, with Newfoundland and an Excursion to Alaska: "
         "Handbook for Travellers (Karl Baedeker, 3rd edition, 1907)", "Historical travel guide: Canada",
         "Karl Baedeker (Leipzig)", "dominionofcan00karl", 1907,
         "Baedeker's guide to Canada of 1907: routes, cities, the Rockies and the Pacific coast, Newfoundland and an "
         "excursion to Alaska.", country="Germany"),
    _old("baedeker_london_1911", "London and Its Environs: Handbook for Travellers (Karl Baedeker, 16th edition, 1911)",
         "Historical travel guide: London", "Karl Baedeker (Leipzig)", "londonitsenviron00baed", 1911,
         "Baedeker's guide to London and the places around it in 1911.", country="Germany"),
    _old("baedeker_paris_1913", "Paris and Environs, with Routes from London to Paris: Handbook for Travellers (Karl "
         "Baedeker, 18th edition, 1913)", "Historical travel guide: Paris", "Karl Baedeker (Leipzig)",
         "parisenviro00karl", 1913, "Baedeker's guide to Paris and the places around it on the eve of the First "
         "World War, with the routes from London.", country="Germany"),
    _old("baedeker_egypt_sudan_1914", "Egypt and the Sudan: Handbook for Travellers (Karl Baedeker, 7th edition, "
         "1914)", "Historical travel guide: Egypt and the Sudan", "Karl Baedeker (Leipzig)", "egyptsdnhand00karl",
         1914, "Baedeker's guide to Egypt and the Sudan of 1914, with its long introductions on ancient Egyptian "
         "history, religion and art by the Egyptologists of its day.", country="Germany"),
    _old("lincoln_highway_road_guide_1918", "The Complete Official Road Guide of the Lincoln Highway (Lincoln Highway "
         "Association, 3rd edition, 1918)", "Historical travel guide: the first coast-to-coast road",
         "The Lincoln Highway Association", "completeofficial1918unse", 1918,
         "The road guide to the Lincoln Highway, the first road across the United States from New York to San "
         "Francisco, town by town, with advice for motorists of 1918."),
]

MAKERS = {"govinfo_travel_publications": GOVINFO_BOOK}
COLLECTION = K.Collection("tripmore", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"travel-more": lambda: [f"tripmore:{g['name']}" for g in GUIDES] +
                                 ["tripmore:govinfo_travel_publications"] + [f"tripmore:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "tripmore_wayback": "web.archive.org: the Wayback Machine's exact copies (\"id_\") of pages of the US Department "
                        "of Transportation, TSA, Customs and Border Protection and the State Department, works of the "
                        "US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build); each "
                        "capture is pinned by its date (found 2026-11-22).",
    "tripmore_govinfo": "api.govinfo.gov: a sign-up entry; the owner's free api.data.gov key is read from "
                        "GOVINFO_API_KEY at build time, never stored in the repository; the PDFs are read from "
                        "govinfo.gov's public /content/ addresses, which robots.txt allows (checked 2026-11-22).",
    "tripmore_old_guides": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every "
                           "build); the National Parks Portfolio and Glimpses of Our National Parks are also works of "
                           "the US government. Baedeker's guides are German and British printings, public domain in "
                           "the US as published before 1931.",
}

NOT_INCLUDED = [
    ("State Department travel booklets of the 1980s on the Internet Archive (Your Trip Abroad, A Safe Trip Abroad, "
     "Travel Tips for Older Americans, Tips for Travelers to ...)", "Public domain, but decades out of date (rules, "
     "phone numbers, countries) and only microfiche scans; today's pages are built from Wayback copies "
     "(tripmore:state_travel_wayback). Index: https://archive.org/search?query=%22tips+for+travelers%22"),
    ("TSA, DOT and State Department pages not captured by the Wayback Machine since 2024 (TSA's disability page, "
     "DOT's wheelchairs and baggage pages, the State Department's travellers with disabilities and older "
     "travellers pages)", "No capture since 2024 was found (availability API, 2026-11-22); older captures may be out "
     "of date. Link-only. Index: https://www.tsa.gov/travel/special-procedures"),
    ("Bureau of Land Management and Recreation.gov visitor pages", "Not checked yet; the Forest Service's and Park "
     "Service's outdoor pages are built (outdoors:, wild:, rvs:). Index: https://www.blm.gov/visit"),
    ("Commercial guidebooks (Lonely Planet, Rick Steves, Fodor's) and modern Baedekers", "Copyright of their "
     "publishers; link-only. Wikivoyage (CC BY-SA) is whole in the Kiwix library. Index: https://en.wikivoyage.org/"),
    ("CDC Yellow Book", "Already built (firstaid:cdc_yellow_book); not built twice. Index: "
     "https://www.cdc.gov/yellow-book/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
