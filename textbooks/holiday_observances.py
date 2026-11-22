"""Holidays and observances for the reference library, in its own group "Reference, holidays and observances" (the
owner's request of 2026-11-22). Keys: holidays (every book), holiday:<name>.

What this module builds, in plain words:
  - the US federal holidays, IN FULL from the government's own pages: the Office of Personnel Management's federal
    holiday dates for each year (with its notes on holidays that fall on a weekend) and USA.gov's holidays page;
  - their history: the Congressional Research Service's report "Federal Holidays: Evolution and Current Practices"
    (R41990, 2021: how each of the federal holidays came to be, and the law behind them) and its "Juneteenth National
    Independence Day: A New Federal Holiday" (IN11697, 2022), both whole from the Library of Congress's copies at the
    Internet Archive; the Department of Labor's history of Labor Day and the VA's history of Veterans Day;
  - the major religious and cultural observances, presented neutrally: the opening section of the English Wikipedia
    article on each (Christian, Jewish, Muslim, Hindu, Buddhist, Sikh, Chinese and other East Asian, Persian, African
    American and Mexican observances, and widely kept cultural days), CC BY-SA 4.0, as a separate SHARE-ALIKE book;
  - other countries' public holidays from their governments: the UK's bank holidays for England and Wales, Scotland
    and Northern Ireland (GOV.UK, Open Government Licence) and Canada's public holidays (Canada Revenue Agency,
    personal use only under canada.ca's terms), each marked as not US;
  - an old public-domain book, The Book of Holidays (McSpadden, 1917), with a note on what is out of date;
  - holiday:index, a guide to holidays in the library, with the World Factbook's "national holiday" entry for every
    country, the holiday picture packs, and the sources that are links only.

Not built (NOT_INCLUDED, link-only): the Library of Congress's holiday research guides (guides.loc.gov shuts out AI
companies' readers), interfaith calendars (copyright), New Zealand's and Australia's public holiday pages
(non-commercial or unchecked terms), and the Memorial Day history on cem.va.gov (its page template has no content
mark the builder can find; the CRS report covers Memorial Day's history).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
CC BY-SA 4.0 for the Wikipedia excerpts (Wikipedia's copyright page checked at every build); the Open Government
Licence for GOV.UK (its terms page checked); canada.ca's non-commercial terms (personal use only); the old book's
Internet Archive record must show a date before 1931.

Run from the repository's folder:
  python3 textbooks/holiday_observances.py holiday:us_federal_holidays --out build/textbooks
  python3 textbooks/holiday_observances.py --list holidays
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker and page lists
import sacred_texts as S  # noqa: E402 - the Wikipedia lead-section marks
from old_ia_books import old_book  # noqa: E402
from parenting import CROWN_NC, CANADA_TERMS, CANADA_TEXT  # noqa: E402 - canada.ca's terms, checked there too

GROUP = "holidays"
GROUPS = {GROUP: "Reference, holidays and observances"}
NOT_US = ("Not US: this page is about another country's public holidays, which are set by that country's own laws "
          "and may differ by region.")

OPM = "https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/"
USA_HOLIDAYS = "https://www.usa.gov/holidays"
HISTORY_PAGES = ["https://www.dol.gov/general/laborday/history",
                 "https://department.va.gov/veterans-day/history-of-veterans-day/"]

# (Wikipedia article, tradition): the observances whose opening sections are read.
OBSERVANCES = [
    ("Advent", "Christian"), ("Christmas", "Christian"), ("Epiphany_(holiday)", "Christian"), ("Lent", "Christian"),
    ("Ash_Wednesday", "Christian"), ("Holy_Week", "Christian"), ("Good_Friday", "Christian"),
    ("Easter", "Christian"), ("Pentecost", "Christian"), ("All_Saints'_Day", "Christian"),
    ("Rosh_Hashanah", "Jewish"), ("Yom_Kippur", "Jewish"), ("Sukkot", "Jewish"), ("Hanukkah", "Jewish"),
    ("Purim", "Jewish"), ("Passover", "Jewish"), ("Shavuot", "Jewish"),
    ("Ramadan", "Muslim"), ("Eid_al-Fitr", "Muslim"), ("Eid_al-Adha", "Muslim"), ("Islamic_New_Year", "Muslim"),
    ("Mawlid", "Muslim"), ("Ashura", "Muslim"),
    ("Diwali", "Hindu"), ("Holi", "Hindu"), ("Navaratri", "Hindu"), ("Raksha_Bandhan", "Hindu"),
    ("Vesak", "Buddhist"), ("Bodhi_Day", "Buddhist"), ("Vaisakhi", "Sikh"), ("Guru_Nanak_Gurpurab", "Sikh"),
    ("Chinese_New_Year", "East Asian"), ("Mid-Autumn_Festival", "East Asian"), ("Bon_Festival", "East Asian"),
    ("Nowruz", "Persian and Central Asian"), ("Kwanzaa", "Cultural observances"),
    ("Day_of_the_Dead", "Cultural observances"), ("Lunar_New_Year", "East Asian"),
    ("Thanksgiving", "Cultural observances"), ("Halloween", "Cultural observances"),
    ("Valentine's_Day", "Cultural observances"), ("Mother's_Day", "Cultural observances"),
    ("Father's_Day", "Cultural observances"), ("New_Year's_Eve", "Cultural observances"),
]
OBSERVANCE_URLS = [S.WIKI + a for a, _t in OBSERVANCES]
TRADITIONS = list(dict.fromkeys(t for _a, t in OBSERVANCES))


def tradition_rules():
    """[(address pattern, part)]: each observance under its tradition's part."""
    return [(r"/" + re.escape(a) + "$", t) for a, t in OBSERVANCES]


GUIDES = [
    X.page_list_book(
        GROUP, "us_federal_holidays", "US federal holidays: this year's and coming years' dates (OPM and USA.gov)",
        "US federal holidays", "US Office of Personnel Management (OPM) and USAGov (General Services "
        "Administration)", [OPM, USA_HOLIDAYS],
        r"^https://www\.(opm\.gov/policy-data-oversight/pay-leave/federal-holidays/|usa\.gov/holidays)$",
        "The US government's own pages on federal holidays: the Office of Personnel Management's dates of every "
        "federal holiday for this year and the years ahead (New Year's Day, Birthday of Martin Luther King, Jr., "
        "Washington's Birthday, Memorial Day, Juneteenth National Independence Day, Independence Day, Labor Day, "
        "Columbus Day, Veterans Day, Thanksgiving Day, Christmas Day, and Inauguration Day in the Washington, DC "
        "area), with its notes on holidays that fall on a Saturday or Sunday; and USA.gov's holidays page.",
        "Works of the US government (public domain). Federal holidays apply to federal employees and the District of "
        "Columbia; each state sets its own legal holidays, and businesses choose their own days off.",
        units=[(r"opm", "Federal holiday dates"), (r".", "Holidays (USA.gov)")]),
    X.page_list_book(
        GROUP, "us_holiday_histories", "The history of Labor Day and Veterans Day (Department of Labor and VA)",
        "Holiday history", "US Department of Labor and US Department of Veterans Affairs", HISTORY_PAGES,
        r"^https://(www\.dol\.gov/general/laborday/history|department\.va\.gov/veterans-day/history-of-veterans-"
        r"day/)$",
        "Two holiday histories from the departments that keep them: the Department of Labor's history of Labor Day "
        "(its origins in the labor movement of the 1880s, the first parades, and the 1894 federal law) and the VA's "
        "history of Veterans Day (Armistice Day, 11 November 1918, the change to Veterans Day in 1954, and the "
        "Uniform Monday Holiday Act).", "Works of the US government (public domain).",
        units=[(r"dol", "Labor Day"), (r".", "Veterans Day")]),
    dict(K.WEB, group=GROUP, name="wikipedia_observances", title="Religious and cultural observances: short "
         "introductions (Wikipedia excerpts)", subject="Religious and cultural observances",
         publisher="Wikipedia contributors (Wikimedia Foundation)", country="International",
         licence="CC BY-SA 4.0", licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
         licence_page=S.WIKI_LICENCE_PAGE, licence_text=r"Creative Commons Attribution-ShareAlike 4\.0",
         source=OBSERVANCE_URLS[0], crawl=[(OBSERVANCE_URLS[0], 0)], urls=list(OBSERVANCE_URLS),
         pages=r"^https://en\.wikipedia\.org/wiki/[A-Za-z0-9_(),%.'-]+$", content=(S.LEAD_START, S.LEAD_END),
         drop=S.LEAD_DROP, unit_rules=tradition_rules(), limit=len(OBSERVANCE_URLS) + 5,
         description="A short, neutral introduction to each major religious and cultural observance: the opening "
                     "section of its English Wikipedia article, grouped by tradition (" + ", ".join(TRADITIONS) +
                     "). Dates of many observances follow lunar or lunisolar calendars and move each year.",
         notice="From Wikipedia, the free encyclopedia (en.wikipedia.org), by its contributors; each page names its "
                "article. Licensed CC BY-SA 4.0: share-alike, so anything made from this book keeps the same "
                "licence. Only each article's opening section is kept; footnotes, infoboxes and pictures are left "
                "out. Customs differ between communities and families; each community's own sources say most."),
    dict(X.page_list_book(
        GROUP, "govuk_bank_holidays", "UK bank holidays: England and Wales, Scotland, Northern Ireland (GOV.UK)",
        "UK public holidays", "GOV.UK (UK Government)", ["https://www.gov.uk/bank-holidays"],
        r"^https://www\.gov\.uk/bank-holidays$",
        "GOV.UK's list of the UK's bank holidays for this year and the next, for England and Wales, Scotland and "
        "Northern Ireland separately, with substitute days when a holiday falls on a weekend.",
        f"Contains public sector information licensed under the Open Government Licence v3.0 (GOV.UK). {NOT_US}",
        country="United Kingdom", units=[(r".", "United Kingdom")]),
        licence="OGL-UK-3.0", licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        licence_page="https://www.gov.uk/help/terms-conditions", licence_text=r"Open Government Licence"),
    dict(X.page_list_book(
        GROUP, "canada_public_holidays", "Canada's public holidays (Canada Revenue Agency)", "Canadian public holidays",
        "Canada Revenue Agency", ["https://www.canada.ca/en/revenue-agency/services/tax/public-holidays.html"],
        r"^https://www\.canada\.ca/en/revenue-agency/services/tax/public-holidays\.html$",
        "The Canada Revenue Agency's list of Canada's public holidays and their dates (New Year's Day, Good Friday, "
        "Easter Monday, Victoria Day, Canada Day, Civic Holiday, Labour Day, the National Day for Truth and "
        "Reconciliation, Thanksgiving, Remembrance Day, Christmas Day and Boxing Day), with the provinces' own "
        "holidays noted.",
        f"Crown copyright (Canada); personal use only under canada.ca's terms, which allow copies \"for "
        f"non-commercial purposes\". Source: Canada Revenue Agency. {NOT_US}", country="Canada",
        units=[(r".", "Canada")]),
        licence=CROWN_NC, licence_url=CANADA_TERMS, licence_page=CANADA_TERMS, licence_text=CANADA_TEXT,
        personal_use=True),
]


def crs_report(name, title, archive, published, description):
    """A Congressional Research Service report read whole from the Library of Congress's copy at the Internet
    Archive (a work of the US government)."""
    return K.us_pdf(GROUP, name=name, title=title, subject="Holiday history",
                    publisher="Congressional Research Service, Library of Congress", archive=archive,
                    published=published, version=f"{published} (Internet Archive item {archive})",
                    description=description,
                    notice="A report of the Congressional Research Service (Library of Congress): a work of the US "
                           "government (public domain). It describes the law as of its date.")


PDFS = [
    crs_report("crs_federal_holidays_evolution", "Federal Holidays: Evolution and Current Practices (Congressional "
               "Research Service, R41990, 2021)", "crs-r41990.11", "2021-07-01",
               "How the United States' federal holidays came to be: the first four holidays of 1870, Washington's "
               "Birthday, Decoration Day (Memorial Day), Labor Day, Armistice Day (Veterans Day), Inauguration Day, "
               "Columbus Day, Martin Luther King Jr.'s Birthday and Juneteenth, the Uniform Monday Holiday Act of "
               "1968, how federal holidays apply to federal employees, and the commemorations Congress has "
               "proposed."),
    crs_report("crs_juneteenth", "Juneteenth National Independence Day: A New Federal Holiday (Congressional "
               "Research Service, IN11697, 2022)", "crs-in11697.4", "2022-01-13",
               "The history of Juneteenth (19 June 1865, when news of emancipation reached Galveston, Texas), its "
               "celebration over the years, and the 2021 law that made it the eleventh permanent federal holiday."),
    old_book(GROUP, "mcspadden_book_of_holidays_1917", "The Book of Holidays (McSpadden, 1917)", "Holiday history",
             "J. Walker McSpadden (Thomas Y. Crowell Company)", "bookofholidays01mcsp", 1917,
             "The stories behind the American holidays of 1917: New Year's Day, Lincoln's and Washington's birthdays, "
             "Valentine's Day, St Patrick's Day, Easter, Arbor Day, Mother's Day, Memorial Day, Flag Day, "
             "Independence Day, Labor Day, Columbus Day, Hallowe'en, Thanksgiving and Christmas.",
             note="Published in {year}: it predates several of today's federal holidays (Veterans Day, Martin Luther "
                  "King Jr.'s Birthday, Juneteenth), and some of its accounts of history and of other peoples "
                  "reflect the views of its time."),
]

# ====================================================================== the index

SECTIONS = [
    ("US federal holidays", "The eleven annual federal holidays and Inauguration Day; states set their own.", [
        ("key", "holiday:us_federal_holidays", "Federal holiday dates (OPM) and USA.gov's holidays page"),
        ("key", "holiday:crs_federal_holidays_evolution", "Federal Holidays: Evolution and Current Practices (CRS)"),
        ("key", "holiday:crs_juneteenth", "Juneteenth National Independence Day (CRS)"),
        ("key", "holiday:us_holiday_histories", "The history of Labor Day and Veterans Day"),
        ("key", "holiday:mcspadden_book_of_holidays_1917", "The Book of Holidays (1917)"),
        ("pack", "commons_us_holidays", "American holidays and events, for the picture describer")]),
    ("Religious and cultural observances", "Short neutral introductions, by tradition.", [
        ("key", "holiday:wikipedia_observances", "Religious and cultural observances (Wikipedia excerpts)"),
        ("word", "sacred-texts", "Sacred and philosophical texts (request word)")]),
    ("Other countries' public holidays", "Each country sets its own; the Factbook names each country's national day.", [
        ("key", "holiday:govuk_bank_holidays", "UK bank holidays (GOV.UK)"),
        ("key", "holiday:canada_public_holidays", "Canada's public holidays (Canada Revenue Agency)"),
        ("key", "geo:factbook", "The World Factbook: every country's \"National holiday\" (under Government)"),
        ("pack", "commons_ca_holidays", "Canadian holidays, for the picture describer"),
        ("link", "New Zealand public holidays (Employment New Zealand)", "https://www.employment.govt.nz/"
         "leave-and-holidays/public-holidays/public-holidays-and-anniversary-dates", "Crown copyright, personal use "
         "only; open it in a browser"),
        ("link", "Australia public holidays (australia.gov.au)", "https://www.australia.gov.au/public-holidays",
         "its terms were not checked; open it in a browser"),
        ("link", "Ireland public holidays (Citizens Information)", "https://www.citizensinformation.ie/en/employment/"
         "employment-rights-and-conditions/leave-and-holidays/public-holidays/", "open it in a browser")]),
    ("More (links only)", "Research guides and calendars.", [
        ("link", "Library of Congress: holidays and observances research guides", "https://guides.loc.gov/holidays",
         "guides.loc.gov shuts out AI companies' readers; open it in a browser"),
        ("link", "Memorial Day history (VA National Cemetery Administration)",
         "https://www.cem.va.gov/history/memdayhistory.asp", "a US government page; open it in a browser")]),
]
INDEX = X.index_maker("holiday", GROUP, "Holidays and observances: a guide to the library", "Holidays and "
                      "observances", "A guide to holidays in the library: US federal holidays and their history, "
                      "religious and cultural observances, and other countries' public holidays.", SECTIONS,
                      country="International")
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("holiday", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"holidays": lambda: ["holiday:index"] + [f"holiday:{g['name']}"
                                                                          for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "holiday_us_gov": "opm.gov, usa.gov, dol.gov and department.va.gov: works of the US government (17 U.S.C. 105, "
                      "checked on govinfo.gov's policies page at every build); robots.txt allows the pages; no AI "
                      "rules (checked 2026-11-22). The CRS reports are read from the Library of Congress's copies at the "
                      "Internet Archive (collection loc-congressional-research-service, marked public domain).",
    "holiday_wikipedia": "en.wikipedia.org/wiki/Wikipedia:Copyrights (checked at every build, as sacred_wikipedia): "
                         "CC BY-SA 4.0, a separate share-alike book.",
    "holiday_govuk": "www.gov.uk/help/terms-conditions (checked at every build): \"Most content on GOV.UK is subject "
                     "to Crown copyright protection and is published under the Open Government Licence\"; the "
                     "bank holidays page carries the OGL v3.0 line.",
    "holiday_canada": "canada.ca terms (checked at every build, as in parenting.py): non-commercial reproduction only, "
                      "so the Canadian book is personal use only.",
    "holiday_old_book": "The Book of Holidays (1917): the Internet Archive record's date before 1931, checked at "
                        "every build.",
    "holiday_index": "The index (holiday:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Library of Congress holiday research guides and \"Today in History\"", "Public domain, but guides.loc.gov shuts "
     "out AI companies' readers and www.loc.gov answered \"403\" to its classroom pages (checked 2026-11-22). "
     "Link-only. Index: https://guides.loc.gov/holidays"),
    ("Interfaith calendars (Interfaith Calendar, Shap Calendar of Religious Festivals, BBC religion calendars)",
     "Copyright of their publishers; the Wikipedia introductions (CC BY-SA) are built instead. Index: "
     "https://www.interfaith-calendar.org/"),
    ("New Zealand, Australian and Irish public holiday pages", "Employment New Zealand allows only personal or "
     "non-commercial reproduction; australia.gov.au's and gov.ie's terms could not be read (gov.ie answers \"403\"); "
     "link-only from the index. Index: https://www.employment.govt.nz/leave-and-holidays/public-holidays/"
     "public-holidays-and-anniversary-dates"),
    ("Memorial Day history (cem.va.gov)", "Public domain, but its old page template mixes the menus into the page "
     "with no mark of where the article starts; the CRS report covers Memorial Day's history. Index: "
     "https://www.cem.va.gov/history/memdayhistory.asp"),
    ("Heritage month pages (Black History Month, Women's History Month and others) on government sites", "Several "
     "federal heritage month sites were taken down in 2025; the Wikipedia introductions and the CRS report cover "
     "the federal holidays. Index: https://www.usa.gov/holidays"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
