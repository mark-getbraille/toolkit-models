"""Genealogy and family history for the reference library, in its own group "Reference, genealogy" (the owner's
request of 2026-11-22). Keys: genealogy (every book), gen:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the National Archives' (NARA) genealogy guides, every page: starting your family history, the census records
    1790 to 1950 (what each census asked, Soundex, the 72-year rule), immigration and ship passenger lists,
    naturalisation records, military service and pension records from the Revolution to Vietnam, ordering veterans'
    records from the National Personnel Records Center, and land records and homestead files;
  - the Census Bureau's family history pages: finding census records, the 72-year rule, the 1890 census and its
    loss, censuses of American Indians, proof of age from old census records, and the most common US names;
  - CDC's "Where to Write for Vital Records" (National Center for Health Statistics): every state's and territory's
    vital records office for birth, death, marriage and divorce records, with addresses, fees and what each holds,
    kept whole with its text unchanged as CDC's terms ask;
  - gen:index, a guide to genealogy in the library, with the sources that are links only (the Library of Congress
    genealogy guides, the Social Security Administration's records requests and the Death Master File,
    FamilySearch, and state archives).

Every book's notice ends with the records note: fees, forms and addresses change, so check with the office before
you send a request or money; birth and death records are often restricted for a number of years.

Not built (NOT_INCLUDED, link-only): the Library of Congress research guides (guides.loc.gov shuts out AI companies'
readers), the Social Security Administration's SS-5 and Death Master File pages (ssa.gov refuses programs),
FamilySearch and its Research Wiki (it refuses programs, and its terms keep all rights), and the paid genealogy
sites (copyright).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's terms checked at every build and its conditions met in the notice.

Run from the repository's folder:
  python3 textbooks/genealogy.py gen:cdc_where_to_write_vital_records --out build/textbooks --limit 5
  python3 textbooks/genealogy.py --list genealogy
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - CDC's terms and notice
import practical_index as X  # noqa: E402 - the index maker

GROUP = "genealogy"
GROUPS = {GROUP: "Reference, genealogy"}
NOTE = ("Fees, forms and addresses change: check with the office before you send a request or money. Birth and death "
        "records are often restricted for a number of years, and only certain relatives may order them.")

NARA = "https://www.archives.gov"
NARA_TOPICS = "genealogy|census|immigration|naturalization|military|land"
NARA_STARTS = [f"{NARA}/research/{t}" for t in ("genealogy", "census", "immigration", "military", "land")] + [
    f"{NARA}/veterans/military-service-records"]
CENSUS = "https://www.census.gov/about/history/census-records-family-history"
W2W = "https://www.cdc.gov/nchs/w2w/index.htm"

GUIDES = [
    K.guide(GROUP, "nara_genealogy", "Genealogy at the National Archives: census, immigration, naturalisation, "
            "military and land records (NARA)", "Family history records", "National Archives and Records "
            "Administration (NARA)", NARA_STARTS,
            rf"^https://www\.archives\.gov/(research/({NARA_TOPICS})(/[a-z0-9-]+)*(\.html)?|"
            rf"veterans/military-service-records(/[a-z0-9-]+)*(\.html)?)/?$",
            "The National Archives' genealogy guides, every page: getting started with family history and the "
            "records NARA holds, the census records from 1790 to 1950 (what each census asked, Soundex indexes, "
            "the 72-year rule, the lost 1890 census, Native American censuses), immigration and ship passenger "
            "lists, naturalisation records, military service and pension records from the American Revolution to "
            "Vietnam, requesting veterans' service records from the National Personnel Records Center, and land "
            "entry and homestead records.",
            f"From the National Archives (archives.gov): works of the US government (public domain). {NOTE}",
            depth=2, follow=rf"^https://www\.archives\.gov/(research/({NARA_TOPICS})|veterans/military-service-"
                            rf"records)(/[a-z0-9-]+)?/?$",
            units=[(r"/census", "Census records"), (r"/(immigration|naturalization)", "Immigration and "
                    "naturalisation"), (r"/(military|veterans)", "Military records"), (r"/land", "Land records"),
                   (r".", "Getting started")],
            content=(r'<div id="main-col"[^>]*>', r'<div id="sidebar"|<footer\b'), limit=400),
    K.guide(GROUP, "census_family_history", "Census records and family history (US Census Bureau)",
            "Census records", "US Census Bureau", CENSUS + ".html",
            r"^https://www\.census\.gov/about/history/census-records-family-history(/[A-Za-z0-9-]+)*\.html$",
            "The Census Bureau's history pages for family historians, every page: finding census records, the "
            "72-year rule that keeps records private, the 1890 census and its loss in a fire, the 1890 veterans' "
            "census, censuses of American Indians, getting proof of age from old census records (the Age Search "
            "service), and the most common US first names and surnames.",
            f"From the US Census Bureau: a work of the US government (public domain). {NOTE}", depth=2,
            content=(r'<div class="responsivegrid uscb-template-container-title', r'<footer\b'), limit=60,
            units=[(r".", "Census records and family history")]),
    dict(K.guide(GROUP, "cdc_where_to_write_vital_records", "Where to write for vital records: birth, death, marriage "
                 "and divorce records in every state (CDC NCHS)", "Vital records offices",
                 M.CDC_PUBLISHER + ", National Center for Health Statistics", W2W,
                 r"^https://www\.cdc\.gov/nchs/w2w/[a-z_]+\.htm$",
                 "The National Center for Health Statistics' guide to vital records, every page: for each state, "
                 "territory and the District of Columbia, the office that holds birth, death, marriage and divorce "
                 "records, its address, the cost of a copy, the years it holds and the remarks on how to order.",
                 f"{M.CDC_NOTICE} {NOTE}", depth=1, limit=70, units=[(r".", "Vital records offices")]),
         licence_page=M.CDC_TERMS, licence_text=M.CDC_TEXT, unchanged=True),
]

# ====================================================================== the index

SECTIONS = [
    ("Getting started", "Start with what you know, then census, vital, immigration, military and land records.", [
        ("key", "gen:nara_genealogy", "Genealogy at the National Archives: getting started"),
        ("link", "Library of Congress: genealogy and local history research guides", "https://guides.loc.gov/genealogy",
         "guides.loc.gov shuts out AI companies' readers, so it is not read; open it in a browser")]),
    ("Census records", "The US census from 1790 to 1950 and how to find a family in it.", [
        ("key", "gen:nara_genealogy", "Census records 1790 to 1950 (National Archives)"),
        ("key", "gen:census_family_history", "Census records and family history (Census Bureau)")]),
    ("Birth, death, marriage and divorce records", "Vital records are kept by the states.", [
        ("key", "gen:cdc_where_to_write_vital_records", "Where to write for vital records, state by state (CDC)"),
        ("link", "Social Security: request a copy of a deceased person's application (SS-5) under FOIA",
         "https://www.ssa.gov/foia/request.html", "ssa.gov refuses programs; open it in a browser"),
        ("link", "Social Security Death Master File (who may get it and how)",
         "https://www.ssa.gov/dataexchange/request_dmf.html", "ssa.gov refuses programs; open it in a browser")]),
    ("Immigration, naturalisation and passports", "Ship passenger lists, naturalisation and citizenship records.", [
        ("key", "gen:nara_genealogy", "Immigration and naturalisation records (National Archives)"),
        ("word", "immigration", "Today's immigration and citizenship books (request word)")]),
    ("Military records", "Service, pension and draft records, and ordering a veteran's file.", [
        ("key", "gen:nara_genealogy", "Military service and pension records; the National Personnel Records Center"),
        ("word", "veterans", "Veterans' benefits, burial and records (request word)")]),
    ("Land records", "Land entry case files and homesteads.", [
        ("key", "gen:nara_genealogy", "Land records and homestead files (National Archives)")]),
    ("More genealogy sites (links only)", "Free and paid sites with their own terms.", [
        ("link", "FamilySearch and its Research Wiki", "https://www.familysearch.org/en/wiki/Main_Page",
         "it refuses programs and its terms keep all rights; free to use in a browser with an account"),
        ("link", "State archives and historical societies (Council of State Archivists' directory)",
         "https://www.statearchivists.org/connect/resources-state", "each state's own site"),
        ("link", "Ancestry, MyHeritage and Findmypast", "https://www.ancestry.com/",
         "paid sites, copyright; many public libraries offer them free inside the library")]),
]
INDEX = X.index_maker("gen", GROUP, "Genealogy: a guide to the library", "Genealogy and family history",
                      "A guide to family history in the library: getting started, census records, vital records, "
                      "immigration, military and land records, and the genealogy sites that are links only.",
                      SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("gen", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"genealogy": lambda: ["gen:index"] + [f"gen:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "gen_us_gov": "archives.gov and census.gov: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
                  "policies page at every build); archives.gov asks 10 seconds between pages, which the builder "
                  "keeps; robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "gen_cdc": "CDC's terms (www.cdc.gov/other/agencymaterials.html, as mind_cdc), checked at every build; the NCHS "
               "pages are kept whole.",
    "gen_index": "The index (gen:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Library of Congress genealogy and local history research guides", "Public domain, but guides.loc.gov's "
     "robots.txt shuts out AI companies' readers, so it is not read (checked 2026-11-22). Link-only. Index: "
     "https://guides.loc.gov/genealogy"),
    ("Social Security Administration: SS-5 requests under FOIA and the Death Master File", "Public domain, but "
     "www.ssa.gov answers programs \"403\" (checked 2026-11-22). Link-only. Index: "
     "https://www.ssa.gov/foia/request.html"),
    ("FamilySearch Research Wiki", "www.familysearch.org answers programs \"403\" (checked 2026-11-22) and its terms "
     "of use keep all rights to its content; no open licence was found, so it is link-only. Index: "
     "https://www.familysearch.org/en/wiki/Main_Page"),
    ("State vital records offices' own sites", "Each state's own site; CDC's where-to-write guide (built: "
     "gen:cdc_where_to_write_vital_records) lists every office with its address and fees. Index: "
     "https://www.cdc.gov/nchs/w2w/index.htm"),
    ("Ancestry, MyHeritage, Findmypast and other paid genealogy sites", "Copyright and paid; link-only. Index: "
     "https://www.ancestry.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
