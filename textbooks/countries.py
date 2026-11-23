"""Countries of the world and maps, for the reference library, in the group "Reference, world geography" (beside
geography.py's World Factbook; the owner's request of 2026-11-23: offline knowledge of every country). Keys:
ctry:<name>, and the request words below.

What this module builds, in plain words, each book read WHOLE:
  - ctry:cs_<country>: the Library of Congress Country Studies (the Army's Area Handbook series, DA Pam 550), written
    by the Library's Federal Research Division between 1988 and 2015, one book per country or region: history,
    geography, people and society, economy, government and politics, and national security, with a chronology, a
    bibliography and a glossary. Read from the Internet Archive's copies of the Library's own scans (collection
    "library_of_congress": text layer, downloadable, year known), or a Defense Technical Information Center (DTIC)
    copy. All 80 books of the Library's online collection are here, and Greece (1995, DTIC copy). Every
    description says the edition year and that political facts (leaders, borders, figures) are dated.
  - ctry:ah_<country>_<year>: the older Area Handbooks (1969 to 1977, by Foreign Area Studies of The American
    University), only for countries with no later edition the library may build (Afghanistan, Burundi, Guatemala,
    Guinea, Italy, Senegal, Sierra Leone). They are public domain because they were published by the Government
    Printing Office before 1978 without a copyright notice (each copy's front pages are checked at every build).
  - ctry:bgn_<country>: the State Department's Background Notes, one short country profile each (1982 to 1990, the
    newest edition on the Internet Archive for each of 59 countries, from the Government Printing Office's
    microfiche): land and people, history, government, economy, foreign relations, travel notes. Dated, said in each.
  - Maps and map reading (described in words; no map pictures are needed): ctry:usgs_map_basics (the USGS fact
    sheets on map scales, map and compass, the UTM grid and US Topo maps), ctry:usgs_exploring_maps (the USGS
    teaching packet on what maps show and how to read them), ctry:dma_datums_grids (the Defense Mapping Agency's
    guide to datums, ellipsoids, grids and grid references, 1992) and ctry:census_garm (the Census Bureau's
    Geographic Areas Reference Manual, 1994: every kind of area the census uses, from states to blocks).
  - Gazetteers and geographies published before 1931, marked historical: Lippincott's New Gazetteer (1906, two
    volumes), Chambers's Concise Gazetteer of the World (1914) and Chisholm's Handbook of Commercial Geography (1922).
  - World Bank data books under CC BY 3.0 IGO: The Little Data Book 2016 (one page of figures per country) and The
    Little Green Data Book 2017 (environment figures per country), read from the World Bank's Open Knowledge
    Repository (the licence read from each record at every build).
  - ctry:index, a plain-words guide by continent and country to EVERY country book in the library: the country
    studies, Background Notes and older handbooks here, the World Factbook (geo:factbook), the Defense Language
    Institute's "Countries in Perspective" books (lgov:cip_...), the Peace Corps's country books and language
    courses (pc:, pclang:), history books (hist:) and old travel guides (tripmore:), found in the code at build
    time, so books added later are listed too; then maps and map reading, gazetteers and data books, and the
    sources that are links only.

Request words (each at most 256 jobs; sources.expand_keys): ctry-africa, ctry-americas, ctry-asia, ctry-europe,
ctry-middle-east, ctry-oceania (this module's books for that part of the world, with the index), ctry-maps (the map
books and the index) and countries (every book of this module).

Licences, truthfully (each book's notice says which applies):
  - the Federal Research Division's country studies: works of the Library of Congress's staff for the US Army (17
    U.S.C. 105). Some printings carry the line "Copyright (c) <year> United States Government as represented by the
    Secretary of the Army"; the Library of Congress's rights statement for the series says "All other text and
    graphics are in the public domain" (only some photographs, marked in their captions, are copyrighted; no
    photographs are used here). That statement is read again at every build (LOC_RIGHTS). They are Army pamphlets,
    so the release rule for military publications is applied too (military_release.py), with the Library's own open
    copy (its loc.gov record) named for it;
  - the older Area Handbooks: published by the Government Printing Office before 1978 with no copyright notice
    (approtech.NO_NOTICE, OLD_FRONT checks the copy's front pages);
  - Background Notes, the USGS, Census and Defense Mapping Agency books: works of the US government;
  - old gazetteers and geographies: public domain in the US as published before 1931 (the builder checks the year);
  - the World Bank books: CC BY 3.0 IGO (an open licence that asks for credit).

Not built (NOT_INCLUDED, link-only): the Area Handbooks of 1978 to 1986 by The American University (Kenya, Liberia,
Morocco, Tanzania, Tunisia, Zambia, Zimbabwe, Argentina, Costa Rica, Guatemala, Afghanistan, Burma, Italy), whose
copies print "Copyright (c) The American University" or "Copyright (c) ... United States Government as represented
by the Secretary of the Army. All rights reserved." and which are not in the Library of Congress's public-domain
collection; ERIC's copies of the 1970 and 1971 handbooks for Oceania and Burma (stamped as copyrighted material);
the State Department's live country pages and its archived Background Notes (state.gov refuses programs); the UN
Statistical Yearbook (copyright United Nations); and others listed below.

Run from the repository's folder:
  python3 textbooks/countries.py ctry:cs_chad --out build/textbooks --limit 3
  python3 textbooks/countries.py --list ctry-africa
"""

import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approtech as AT  # noqa: E402 - the "no copyright notice" licence (NO_NOTICE) and its statute page
import geography as G  # noqa: E402 - the group, and the World Factbook's country list by region
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

PREFIX = "ctry"
GROUP = G.GROUP                        # "geography": "Reference, world geography"
GROUPS = dict(G.GROUPS)

# The parts of the world of the request words and the index: (word part, title).
CONTINENTS = [("africa", "Africa"), ("americas", "The Americas"), ("asia", "Asia"), ("europe", "Europe"),
              ("middle-east", "The Middle East"), ("oceania", "Oceania and Antarctica")]
CONTINENT_TITLE = dict(CONTINENTS)
# The World Factbook's regions (geography.REGIONS folders) in those parts; oceans and the world are left out.
FOLDER_CONTINENT = {"africa": "africa", "antarctica": "oceania", "australia-oceania": "oceania",
                    "central-asia": "asia", "east-n-southeast-asia": "asia", "south-asia": "asia", "europe": "europe",
                    "middle-east": "middle-east", "north-america": "americas",
                    "central-america-n-caribbean": "americas", "south-america": "americas"}
# Places whose part of the world is not their Factbook region's, and Factbook pages that are not countries.
CONTINENT_OVERRIDE = {"Russia": "europe"}
NOT_A_COUNTRY = {"European Union"}


def factbook_places():
    """{place name: (Factbook region folder, part of the world)} of every World Factbook page but the oceans, the
    world and the European Union (geography.REGION_CODES)."""
    out = {}
    for folder, codes in G.REGION_CODES.items():
        if folder not in FOLDER_CONTINENT:
            continue
        for name in codes.values():
            if name not in NOT_A_COUNTRY:
                out[name] = (folder, CONTINENT_OVERRIDE.get(name, FOLDER_CONTINENT[folder]))
    return out


PLACES = factbook_places()

# ====================================================================== the Library of Congress country studies

LOC_RIGHTS = "https://www.loc.gov/collections/country-studies/about-this-collection/rights-and-access/?fo=json"
LOC_TEXT = r"All other text and graphics are in the public domain"
LOC_COLLECTION = "https://www.loc.gov/collections/country-studies/"
FRD = "Federal Research Division, Library of Congress, for the Department of the Army (Area Handbook series, DA Pam 550)"
SCAN = ("Read from the Internet Archive's copy of its scan: the machine-read text has the scanner's mistakes, and its "
        "maps, charts and photographs are described only by their captions (no pictures are included).")
DATED = ("Dated: its facts are those of {year}: governments, leaders, borders, place names, populations and figures have "
         "changed since, so read it as a well-researched history and background, and see the World Factbook "
         "(geo:factbook) for the last figures.")

# (key part, title, Internet Archive item, edition year, Library of Congress record number or "", [Factbook places]).
STUDIES = [
    # Africa
    ("algeria", "Algeria: A Country Study", "algeriacountryst00metz_0", 1994, "94043019", ["Algeria"]),
    ("angola", "Angola: A Country Study", "angolacountrystu00coll_0", 1991, "90003244", ["Angola"]),
    ("chad", "Chad: A Country Study", "chadcountrystudy00coll", 1990, "89600373", ["Chad"]),
    ("cote_divoire", "Côte d'Ivoire: A Country Study", "cotedivoirecount00hand_0", 1991, "90005878",
     ["Cote d'Ivoire"]),
    ("egypt", "Egypt: A Country Study", "egyptcountrystud00metz", 1991, "91029876", ["Egypt"]),
    ("ethiopia", "Ethiopia: A Country Study", "ethiopiacountrys00ofca_0", 1993, "92000507", ["Ethiopia", "Eritrea"]),
    ("ghana", "Ghana: A Country Study", "ghanacountrystud00berr_0", 1995, "95018891", ["Ghana"]),
    ("indian_ocean", "Indian Ocean: Five Island Countries (Madagascar, Mauritius, Comoros, Seychelles, Maldives)",
     "indianoceanfivei00metz_0", 1995, "95016570", ["Madagascar", "Mauritius", "Comoros", "Seychelles", "Maldives"]),
    ("libya", "Libya: A Country Study", "libyacountrystud00metz_0", 1989, "88600480", ["Libya"]),
    ("mauritania", "Mauritania: A Country Study", "mauritaniacountr00hand_0", 1990, "89600361", ["Mauritania"]),
    ("nigeria", "Nigeria: A Country Study", "nigeriacountryst00metz_0", 1992, "92009026", ["Nigeria"]),
    ("somalia", "Somalia: A Country Study", "somaliacountryst00metz_0", 1993, "93016246", ["Somalia"]),
    ("south_africa", "South Africa: A Country Study", "southafricacount00byrn", 1997, "96048983", ["South Africa"]),
    ("sudan", "Sudan: A Country Study", "sudancountrystud00unse", 2015, "2014043450", ["Sudan", "South Sudan"]),
    ("uganda", "Uganda: A Country Study", "ugandacountrystu00byrn_0", 1992, "92000513", ["Uganda"]),
    ("zaire", "Zaire: A Country Study (now the Democratic Republic of the Congo)", "zairecountrystud00medi_0", 1994,
     "94025092", ["Congo DR"]),
    # The Americas
    ("bolivia", "Bolivia: A Country Study", "boliviacountryst00huds_0", 1991, "90026427", ["Bolivia"]),
    ("brazil", "Brazil: A Country Study", "brazilcountrystu00huds_0", 1998, "97036500", ["Brazil"]),
    ("chile", "Chile: A Country Study", "chilecountrystud00huds_0", 1994, "94021663", ["Chile"]),
    ("colombia", "Colombia: A Country Study", "colombiacountrys00huds", 2010, "2010009203", ["Colombia"]),
    ("cuba", "Cuba: A Country Study", "cubacountrystudy00huds", 2002, "2002018893", ["Cuba"]),
    ("dominican_republic_haiti", "Dominican Republic and Haiti: Country Studies", "dominicanrepubli00metz", 2001,
     "2001023524", ["Dominican Republic", "Haiti"]),
    ("ecuador", "Ecuador: A Country Study", "ecuadorcountryst00hanr_0", 1991, "91009494", ["Ecuador"]),
    ("el_salvador", "El Salvador: A Country Study", "elsalvadorcountr00hagg", 1990, "89048948", ["El Salvador"]),
    ("guyana_belize", "Guyana and Belize: Country Studies", "guyanabelizecoun00merr_0", 1993, "93010956",
     ["Guyana", "Belize"]),
    ("honduras", "Honduras: A Country Study", "hondurascountrys00merr_0", 1995, "94043036", ["Honduras"]),
    ("commonwealth_caribbean", "Islands of the Commonwealth Caribbean: A Regional Study", "islandsofcommonw00medi",
     1989, "88600483", ["Jamaica", "Trinidad and Tobago", "The Bahamas", "Barbados", "Dominica", "Grenada",
                        "Saint Lucia", "Saint Vincent and the Grenadines", "Antigua and Barbuda",
                        "Saint Kitts and Nevis", "Anguilla", "British Virgin Islands", "Cayman Islands", "Montserrat",
                        "Turks and Caicos Islands"]),
    ("mexico", "Mexico: A Country Study", "mexicocountrystu00merr_0", 1997, "97013481", ["Mexico"]),
    ("nicaragua", "Nicaragua: A Country Study", "nicaraguacountry00merr_0", 1994, "94021664", ["Nicaragua"]),
    ("panama", "Panama: A Country Study", "panamacountrystu00medi", 1989, "88600486", ["Panama"]),
    ("paraguay", "Paraguay: A Country Study", "paraguaycountrys00hanr_0", 1990, "89600299", ["Paraguay"]),
    ("peru", "Peru: A Country Study", "perucountrystudy00huds_0", 1993, "93019676", ["Peru"]),
    ("uruguay", "Uruguay: A Country Study", "uruguaycountryst00huds_0", 1992, "92006702", ["Uruguay"]),
    ("venezuela", "Venezuela: A Country Study", "venezuelacountry00hagg", 1993, "92010376", ["Venezuela"]),
    # Asia
    ("bangladesh", "Bangladesh: A Country Study", "bangladeshcountr00heit", 1989, "89600298", ["Bangladesh"]),
    ("cambodia", "Cambodia: A Country Study", "cambodiacountrys00ross", 1990, "89600150", ["Cambodia"]),
    ("china", "China: A Country Study", "chinacountrystud00word", 1988, "87600493", ["China"]),
    ("india", "India: A Country Study", "indiacountrystud00heit", 1996, "96019266", ["India"]),
    ("indonesia", "Indonesia: A Country Study", "indonesiacountry00fred", 2011, "2011038834", ["Indonesia"]),
    ("japan", "Japan: A Country Study", "japancountrystud00dola", 1992, "91029874", ["Japan"]),
    ("laos", "Laos: A Country Study", "laoscountrystudy00sava_0", 1995, "95017235", ["Laos"]),
    ("mongolia", "Mongolia: A Country Study", "mongoliacountrys00word_0", 1991, "90006289", ["Mongolia"]),
    ("nepal_bhutan", "Nepal and Bhutan: Country Studies", "nepalbhutancount00sava", 1993, "93012226",
     ["Nepal", "Bhutan"]),
    ("north_korea", "North Korea: A Country Study", "northkoreacountr00word", 2008, "2008028547", ["North Korea"]),
    ("pakistan", "Pakistan: A Country Study", "pakistancountrys00bloo_0", 1995, "95017247", ["Pakistan"]),
    ("philippines", "Philippines: A Country Study", "philippinescount00dola_0", 1993, "92039812", ["Philippines"]),
    ("singapore", "Singapore: A Country Study", "singaporecountry00lepo", 1991, "90025755", ["Singapore"]),
    ("south_korea", "South Korea: A Country Study", "southkoreacountr00sava_0", 1992, "91039109", ["South Korea"]),
    ("sri_lanka", "Sri Lanka: A Country Study", "srilankacountrys00ross", 1990, "89600372", ["Sri Lanka"]),
    ("thailand", "Thailand: A Country Study", "thailandcountrys00lepo", 1989, "88600485", ["Thailand"]),
    ("vietnam", "Vietnam: A Country Study", "vietnamcountryst00cima_0", 1989, "88600482", ["Vietnam"]),
    ("central_asia", "Kazakstan, Kyrgyzstan, Tajikistan, Turkmenistan, and Uzbekistan: Country Studies",
     "kazakstankyrgyzs00curt_0", 1997, "97005110", ["Kazakhstan", "Kyrgyzstan", "Tajikistan", "Turkmenistan",
                                                     "Uzbekistan"]),
    ("caucasus", "Armenia, Azerbaijan, and Georgia: Country Studies", "armeniaazerbaija00curt", 1995, "94045459",
     ["Armenia", "Azerbaijan", "Georgia"]),
    # The Middle East
    ("iran", "Iran: A Country Study", "irancountrystudy00curt_0", 2008, "2008011784", ["Iran"]),
    ("iraq", "Iraq: A Country Study", "iraqcountrystudy00metz_0", 1990, "89013940", ["Iraq"]),
    ("israel", "Israel: A Country Study", "israelcountrystu00metz_0", 1990, "90006119",
     ["Israel", "West Bank", "Gaza Strip"]),
    ("jordan", "Jordan: A Country Study", "jordancountrystu00metz", 1991, "91006858", ["Jordan"]),
    ("lebanon", "Lebanon: A Country Study", "lebanoncountryst00coll", 1989, "88600488", ["Lebanon"]),
    ("persian_gulf", "Persian Gulf States: Country Studies (Kuwait, Bahrain, Qatar, United Arab Emirates, Oman)",
     "persiangulfstate00metz_0", 1994, "93046476", ["Kuwait", "Bahrain", "Qatar", "United Arab Emirates", "Oman"]),
    ("saudi_arabia", "Saudi Arabia: A Country Study", "saudiarabiacount00metz_0", 1993, "93028506", ["Saudi Arabia"]),
    ("syria", "Syria: A Country Study", "syriacountrystud00coll_0", 1988, "87600488", ["Syria"]),
    ("turkey", "Turkey: A Country Study", "turkeycountrystu00metz_0", 1996, "95049612", ["Turkey"]),
    # Europe
    ("albania", "Albania: A Country Study", "albaniacountryst00zick", 1994, "93042885", ["Albania"]),
    ("austria", "Austria: A Country Study", "austriacountryst00sols_0", 1994, "94021665", ["Austria"]),
    ("belarus_moldova", "Belarus and Moldova: Country Studies", "belarusmoldovaco00fedo_0", 1995, "95045993",
     ["Belarus", "Moldova"]),
    ("bulgaria", "Bulgaria: A Country Study", "bulgariacountrys00curt_0", 1993, "93010955", ["Bulgaria"]),
    ("cyprus", "Cyprus: A Country Study", "cypruscountrystu00sols", 1993, "92036090", ["Cyprus"]),
    ("czechoslovakia", "Czechoslovakia: A Country Study (now the Czech Republic and Slovakia)",
     "czechoslovakiaco00gawd", 1989, "88600487", ["Czech Republic", "Slovakia"]),
    ("east_germany", "East Germany: A Country Study (the German Democratic Republic, before 1990)",
     "eastgermanycount00bura_0", 1988, "87600490", ["Germany"]),
    ("baltic_states", "Estonia, Latvia, and Lithuania: Country Studies", "estonialatvialit00iwas_0", 1996,
     "96004057", ["Estonia", "Latvia", "Lithuania"]),
    ("finland", "Finland: A Country Study", "finlandcountryst00sols", 1990, "89600315", ["Finland"]),
    ("germany", "Germany: A Country Study", "germanycountryst00sols", 1996, "96020927", ["Germany"]),
    ("greece", "Greece: A Country Study", "DTIC_ADA302893", 1995, "", ["Greece"]),
    ("hungary", "Hungary: A Country Study", "hungarycountryst00bura_0", 1990, "90006426", ["Hungary"]),
    ("poland", "Poland: A Country Study", "polandcountrystu00curt_0", 1994, "93046235", ["Poland"]),
    ("portugal", "Portugal: A Country Study", "portugalcountrys00sols_0", 1993, "93030722", ["Portugal"]),
    ("romania", "Romania: A Country Study", "romaniacountryst00bach_0", 1991, "90006449", ["Romania"]),
    ("russia", "Russia: A Country Study", "russiacountrystu00curt", 1998, "97007563", ["Russia"]),
    ("soviet_union", "Soviet Union: A Country Study (before its break-up in 1991)", "sovietunioncount00zick", 1991,
     "90025756", ["Russia", "Ukraine", "Belarus", "Moldova", "Estonia", "Latvia", "Lithuania", "Armenia",
                  "Azerbaijan", "Georgia", "Kazakhstan", "Kyrgyzstan", "Tajikistan", "Turkmenistan", "Uzbekistan"]),
    ("spain", "Spain: A Country Study", "spaincountrystud00sols_0", 1990, "90006127", ["Spain"]),
    ("yugoslavia", "Yugoslavia: A Country Study (before its break-up)", "yugoslaviacountr00curt_0", 1992, "91040323",
     ["Serbia", "Montenegro", "Croatia", "Slovenia", "Bosnia and Herzegovina", "Macedonia", "Kosovo"]),
]


def study_entry(key, title, archive, year, loc, places):
    """The PDF entry of one country study (see the module docstring): read whole from its Internet Archive copy, the
    Library of Congress's rights statement checked at every build, judged by the release rule for military
    publications (with the Library's own record named as the government's open copy)."""
    covers = ", ".join(places)
    description = (f"The Library of Congress country study \"{title}\" ({year} edition), read whole: its historical "
                   f"setting; the society and its environment (geography, climate, people, languages, religion, "
                   f"education, health and welfare); the economy; government and politics, including foreign "
                   f"relations; and national security; with a country profile, chronology, bibliography and "
                   f"glossary. It covers: {covers}. {DATED.format(year=year)}")
    notice = (f"Written by the Federal Research Division of the Library of Congress for the US Army's Country Studies "
              f"(Area Handbook) program. The Library of Congress's rights statement for the series says the text and "
              f"graphics are in the public domain, except some photographs whose captions say they are copyrighted "
              f"(no photographs are included here); a line on some printings, \"Copyright ... United States "
              f"Government as represented by the Secretary of the Army\", does not change that statement. The views "
              f"are the authors', not an official US government position. {SCAN}")
    if not loc:
        notice = (f"Written by the Federal Research Division of the Library of Congress for the US Army's Country "
                  f"Studies (Area Handbook) program: a work of the US government, with no copyright notice. The "
                  f"views are the authors', not an official US government position. {SCAN}")
    fields = dict(name=f"cs_{key}", title=f"{title} (Library of Congress, {year})",
                  subject=f"Countries of the world: {covers}", publisher=FRD, archive=archive, published=str(year),
                  version=f"{year} edition (Internet Archive item {archive})", description=description,
                  notice=notice, military=True, work="a work of the Library of Congress's Federal Research Division "
                                                    "for the US Army", country="International",
                  source=f"https://www.loc.gov/item/{loc}/" if loc else f"https://archive.org/details/{archive}",
                  places=list(places))
    if loc:
        fields.update(licence_page=LOC_RIGHTS, licence_text=LOC_TEXT, gov=f"https://www.loc.gov/item/{loc}/?fo=json")
    return K.us_pdf(GROUP, **fields)


STUDY_PDFS = [study_entry(*s) for s in STUDIES]

# ====================================================================== older Area Handbooks (1969 to 1977)

# The front pages of an older handbook must show what it is (sold by the Superintendent of Documents, written by
# Foreign Area Studies, or its "DA Pam" number: one is enough, as the machine-read text of an old scan misspells some
# words) and must not print a copyright notice, a "permission to reproduce this copyrighted material" stamp or a
# restricted marking (checked at every build by build_textbooks.pdfdoc_book on the PDF's first twelve pages).
OLD_FRONT = (r"(?is)^(?!.*(?:copyright|copy-\s*righted|permission\s+to\s+reproduce|distribution\s+authori[sz]ed|"
             r"for\s+official\s+use\s+only)).*(?:superintendent\s+of\s+do|foreign\s+area\s+studies|\bDA\s+Pam\b)")
OLD_HANDBOOK_NOTICE = ("An Army Area Handbook (DA Pam 550 series) written by Foreign Area Studies of The American "
                       "University and sold to the public by the US Government Printing Office. It was published "
                       "before 1978 with no copyright notice (its front pages are checked at every build), so it is in "
                       "the public domain in the US: before 1978 a published work kept its copyright only with a "
                       "notice. ")
# (key part, title, Internet Archive item, year, [Factbook places], why this older edition).
OLD_HANDBOOKS = [
    ("afghanistan_1973", "Area Handbook for Afghanistan (fourth edition)", "area-handbook-for-afghanistan", 1973,
     ["Afghanistan"], "The 1986 country study is a copyrighted edition (link-only)."),
    ("burundi_1969", "Area Handbook for Burundi", "DTIC_AD0700157", 1969, ["Burundi"],
     "No later edition was published."),
    ("guatemala_1970", "Area Handbook for Guatemala", "DTIC_AD0705258", 1970, ["Guatemala"],
     "The 1983 country study is a copyrighted edition (link-only)."),
    ("guinea_1975", "Area Handbook for Guinea (second edition)", "DTIC_ADA018316", 1975, ["Guinea"],
     "No later edition was published."),
    ("italy_1977", "Area Handbook for Italy", "DTIC_ADA042816", 1977, ["Italy"],
     "The 1985 country study is a copyrighted edition (link-only)."),
    ("senegal_1974", "Area Handbook for Senegal (second edition)", "ERIC_ED109022", 1974, ["Senegal"],
     "No later edition was published."),
    ("sierra_leone_1976", "Area Handbook for Sierra Leone", "DTIC_ADA034792", 1976, ["Sierra Leone"],
     "No later edition was published."),
]


def old_handbook_entry(key, title, archive, year, places, why):
    """The PDF entry of one older Area Handbook (public domain: published before 1978 without a copyright notice)."""
    return dict(group=GROUP, name=f"ah_{key}", title=f"{title} ({year})", subject="Countries of the world: " +
                ", ".join(places), publisher="Foreign Area Studies, The American University, for the Department of "
                "the Army (DA Pam 550 series); US Government Printing Office", archive=archive,
                country="International", licence=AT.NO_NOTICE, licence_url=AT.NO_NOTICE_URL,
                licence_page=AT.NO_NOTICE_PAGE, licence_text=AT.NO_NOTICE_TEXT, pdf_licence_text=OLD_FRONT,
                level="reference", published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                description=(f"The Army's Area Handbook for {', '.join(places)} ({year}), read whole: the country's "
                             f"history, geography, people, society, religion, education, health, economy, "
                             f"government, foreign relations and national security, as they were in {year}. "
                             f"Historical: {why} {DATED.format(year=year)} Some words for peoples and places are "
                             f"those of its day."),
                notice=OLD_HANDBOOK_NOTICE + SCAN, places=list(places),
                changes="its scanned pages' machine-read text (with the scanner's mistakes) made into web pages, one "
                        "per chapter or ten pages at a time")


OLD_PDFS = [old_handbook_entry(*h) for h in OLD_HANDBOOKS]

# ====================================================================== the State Department's Background Notes

BGN_NOTICE = ("Background Notes, by the US Department of State's Bureau of Public Affairs: a work of the US government "
              "(public domain). Read from the Internet Archive's scan of the Government Printing Office's microfiche "
              "(or ERIC's copy): the machine-read text has the scanner's mistakes, and its map is described only by "
              "its caption.")
# (key part, country as titled, Internet Archive item, edition month, [Factbook places]).
BGN = [
    ("afghanistan", "Afghanistan", "micro_IA41152813_0392", "1986-07", ["Afghanistan"]),
    ("algeria", "Algeria", "micro_IA41152806_0945", "1985-10", ["Algeria"]),
    ("argentina", "Argentina", "micro_IA41152813_0393", "1986-06", ["Argentina"]),
    ("australia", "Australia", "micro_IA41152605_0679", "1989-03", ["Australia"]),
    ("belgium", "Belgium", "micro_IA41152634_0459", "1985-11", ["Belgium"]),
    ("benin", "Benin", "micro_IA41152607_0870", "1989-03", ["Benin"]),
    ("botswana", "Botswana", "micro_IA41152616_0336", "1990-10", ["Botswana"]),
    ("brazil", "Brazil", "micro_IA41152647_0825", "1990-10", ["Brazil"]),
    ("burma", "Burma", "micro_IA41152823_0438", "1986-05", ["Burma"]),
    ("burundi", "Burundi", "micro_IA41152634_0460", "1985-10", ["Burundi"]),
    ("cambodia", "Cambodia", "micro_IA41152616_0337", "1990-12", ["Cambodia"]),
    ("canada", "Canada", "micro_IA41152603_0909", "1989-06", ["Canada"]),
    ("chile", "Chile", "micro_IA41152647_0826", "1990-11", ["Chile"]),
    ("china", "China", "ERIC_ED258906", "1983-12", ["China"]),
    ("costa_rica", "Costa Rica", "micro_IA41152605_0680", "1989-03", ["Costa Rica"]),
    ("cuba", "Cuba", "micro_IA41152635_0044", "1990-10", ["Cuba"]),
    ("fiji", "Fiji", "micro_IA41152634_0461", "1985-11", ["Fiji"]),
    ("finland", "Finland", "micro_IA41152647_0827", "1990-08", ["Finland"]),
    ("france", "France", "micro_IA41152647_0828", "1990-11", ["France"]),
    ("gabon", "Gabon", "micro_IA41152634_0462", "1985-09", ["Gabon"]),
    ("west_germany", "Federal Republic of Germany (West Germany)", "micro_IA41152607_0871", "1989-05", ["Germany"]),
    ("guinea", "Guinea", "micro_IA41152634_0463", "1985-10", ["Guinea"]),
    ("guyana", "Guyana", "micro_IA41152604_0851", "1989-05", ["Guyana"]),
    ("holy_see", "The Holy See", "micro_IA41152607_0872", "1989-04", ["Vatican City (Holy See)"]),
    ("hungary", "Hungary", "micro_IA41152604_0852", "1989-05", ["Hungary"]),
    ("india", "India", "micro_IA41152605_0681", "1989-03", ["India"]),
    ("indonesia", "Indonesia", "micro_IA41152607_0873", "1989-04", ["Indonesia"]),
    ("iraq", "Iraq", "micro_IA41152606_0579", "1982-08", ["Iraq"]),
    ("italy", "Italy", "micro_IA41152647_0829", "1990-10", ["Italy"]),
    ("japan", "Japan", "micro_IA41152607_0875", "1989-02", ["Japan"]),
    ("kenya", "Kenya", "micro_IA41152606_0580", "1982-09", ["Kenya"]),
    ("kuwait", "Kuwait", "micro_IA41152806_0946", "1985-09", ["Kuwait"]),
    ("laos", "Laos", "micro_IA41152813_0394", "1986-05", ["Laos"]),
    ("luxembourg", "Luxembourg", "micro_IA41152602_0814", "1982-09", ["Luxembourg"]),
    ("macau", "Macau", "micro_IA41152602_0815", "1982-10", ["Macau"]),
    ("malawi", "Malawi", "micro_IA41152634_0464", "1985-09", ["Malawi"]),
    ("mali", "Mali", "micro_IA41152823_0441", "1986-04", ["Mali"]),
    ("morocco", "Morocco", "micro_IA41152813_0395", "1986-07", ["Morocco"]),
    ("north_korea", "North Korea", "micro_IA41152639_0142", "1989-07", ["North Korea"]),
    ("oman", "Oman", "micro_IA41152603_0910", "1989-06", ["Oman"]),
    ("papua_new_guinea", "Papua New Guinea", "micro_IA41152603_0911", "1989-07", ["Papua New Guinea"]),
    ("peru", "Peru", "micro_IA41152602_0816", "1982-10", ["Peru"]),
    ("poland", "Poland", "micro_IA41152806_0947", "1985-08", ["Poland"]),
    ("seychelles", "Seychelles", "micro_IA41152657_0420", "1986-04", ["Seychelles"]),
    ("sierra_leone", "Sierra Leone", "micro_IA41152813_0396", "1986-07", ["Sierra Leone"]),
    ("somalia", "Somalia", "micro_IA41152657_0421", "1986-04", ["Somalia"]),
    ("sudan", "Sudan", "micro_IA41152806_0949", "1985-08", ["Sudan"]),
    ("switzerland", "Switzerland", "micro_IA41152605_0682", "1989-03", ["Switzerland"]),
    ("syria", "Syria", "micro_IA41152823_0443", "1986-06", ["Syria"]),
    ("taiwan", "Taiwan", "micro_IA41152806_0950", "1985-09", ["Taiwan"]),
    ("trinidad_and_tobago", "Trinidad and Tobago", "micro_IA41152607_0876", "1989-04", ["Trinidad and Tobago"]),
    ("tunisia", "Tunisia", "micro_IA41152647_0830", "1990-11", ["Tunisia"]),
    ("uae", "United Arab Emirates", "micro_IA41152606_0581", "1982-08", ["United Arab Emirates"]),
    ("united_kingdom", "United Kingdom", "micro_IA41152647_0831", "1990-10", ["United Kingdom"]),
    ("uruguay", "Uruguay", "micro_IA41152647_0832", "1990-11", ["Uruguay"]),
    ("ussr", "The Soviet Union (U.S.S.R.)", "micro_IA41152806_0951", "1985-10", ["Russia"]),
    ("venezuela", "Venezuela", "micro_IA41152647_0833", "1990-11", ["Venezuela"]),
    ("yugoslavia", "Yugoslavia", "micro_IA41152607_0877", "1989-04",
     ["Serbia", "Montenegro", "Croatia", "Slovenia", "Bosnia and Herzegovina", "Macedonia", "Kosovo"]),
    ("zaire", "Zaire (now the Democratic Republic of the Congo)", "micro_IA41152634_0466", "1985-11", ["Congo DR"]),
]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def month_words(month):
    """"1986-07" -> "July 1986"."""
    year, number = month.split("-")
    return f"{MONTHS[int(number) - 1]} {year}"


def bgn_entry(key, country, archive, month, places):
    """The PDF entry of one Background Notes (a short State Department country profile)."""
    when = month_words(month)
    return K.us_pdf(GROUP, name=f"bgn_{key}", title=f"Background Notes: {country} (US Department of State, {when})",
                    subject=f"Countries of the world: {', '.join(places)}", publisher="US Department of State, "
                    "Bureau of Public Affairs (Government Printing Office)", archive=archive, country="International",
                    published=month, version=f"{when} edition (Internet Archive item {archive})",
                    description=(f"The State Department's Background Notes on {country}, {when}: a short profile of "
                                 f"the land and people, history, government and political conditions, economy, "
                                 f"defence, foreign relations and relations with the United States, with travel "
                                 f"notes and a reading list. Dated: its leaders, figures and travel advice are those "
                                 f"of {when}; see the World Factbook (geo:factbook) for the last figures."),
                    notice=BGN_NOTICE, places=list(places))


BGN_PDFS = [bgn_entry(*b) for b in BGN]

# ====================================================================== maps and map reading

USGS = "US Geological Survey (USGS), US Department of the Interior"
MAP_NOTE = (" A map-reading guide, in words: its drawings are described only by their captions, so the text alone "
            "teaches what the symbols, scales and grids mean.")
USGS_MAP_BASICS = K.us_pdf(GROUP, name="usgs_map_basics", title="Map basics: scales, map and compass, the UTM grid and "
                           "US Topo maps (USGS fact sheets)", subject="Maps and map reading", publisher=USGS,
                           source="https://pubs.usgs.gov/publication/fs01502", published="2017",
                           description="Four short USGS fact sheets in one book: Map Scales (what a scale such as "
                                       "1:24,000 means, and how large a scale must be to show a feature); Finding "
                                       "Your Way with Map and Compass (how to orient a topographic map, take a "
                                       "bearing and allow for the difference between true and magnetic north); "
                                       "The Universal Transverse Mercator Grid (how the UTM zones and metre grid let "
                                       "you give a position as two numbers); and US Topo: Topographic Maps for the "
                                       "Nation (what today's USGS topographic maps hold)." + MAP_NOTE,
                           notice="Fact sheets of the US Geological Survey: works of the US government (public "
                                  "domain).")
MAP_BASICS_PARTS = [
    ("Map Scales (Fact Sheet 015-02, 2002)", "https://pubs.usgs.gov/fs/2002/0015/report.pdf",
     "https://pubs.usgs.gov/publication/fs01502"),
    ("Finding Your Way with Map and Compass (Fact Sheet 035-01, 2001)", "https://pubs.usgs.gov/fs/2001/0035/report.pdf",
     "https://pubs.usgs.gov/publication/fs03501"),
    ("The Universal Transverse Mercator (UTM) Grid (Fact Sheet 077-01, 2001)",
     "https://pubs.usgs.gov/fs/2001/0077/report.pdf", "https://pubs.usgs.gov/publication/fs07701"),
    ("US Topo: Topographic Maps for the Nation (Fact Sheet 2017-3045)",
     "https://pubs.usgs.gov/fs/2017/3045/fs20173045.pdf", "https://pubs.usgs.gov/publication/fs20173045"),
]
GARM_BASE = "https://www2.census.gov/geo/pdfs/reference/GARM/"
CENSUS_GARM = K.us_pdf(GROUP, name="census_garm", title="Geographic Areas Reference Manual (US Census Bureau, 1994)",
                       subject="Maps and map reading (census geography)", publisher="US Census Bureau, US Department "
                       "of Commerce", source="https://www.census.gov/programs-surveys/geography/guidance.html",
                       published="1994",
                       description="The Census Bureau's manual of every kind of area it counts people in, chapter by "
                                   "chapter: census geography and its history, states and counties, American Indian "
                                   "and Alaska Native areas, regions and divisions, Puerto Rico and the outlying "
                                   "areas, county subdivisions, places (cities, towns and census-designated places), "
                                   "census tracts, block groups and blocks, urban and rural, metropolitan areas, "
                                   "voting districts, and how land and water areas are measured, with a glossary. "
                                   "Written for the 1990 census: area names and rules have been updated since, but "
                                   "the ideas are the same." + MAP_NOTE,
                       notice="A publication of the US Census Bureau: a work of the US government (public domain).")
GARM_PARTS = [("Contents", "GARMcont.pdf")] + [
    (f"Chapter {n}: {t}", f"Ch{n}GARM.pdf") for n, t in [
        (1, "Census Bureau Geography"), (2, "Geographic Overview"), (3, "Local Census Statistical Areas Committees "
                                                                        "and Other Local Assistance"),
        (4, "States, Counties, and Statistically Equivalent Entities"), (5, "American Indian and Alaska Native Areas"),
        (6, "Statistical Groupings of States and Counties"), (7, "Puerto Rico and the Outlying Areas"),
        (8, "County Subdivisions"), (9, "Places"), (10, "Census Tracts and Block Numbering Areas"),
        (11, "Census Blocks and Block Groups"), (12, "The Urban and Rural Classifications"),
        (13, "Metropolitan Areas"), (14, "Voting Districts"), (15, "Area Measurement and Water Classification")]
] + [("Glossary", "glosGARM.pdf")]

MAP_PDFS = [
    K.us_pdf(GROUP, name="usgs_exploring_maps", title="Exploring Maps (USGS teaching packet, 1993)",
             subject="Maps and map reading", publisher=USGS, pdf="https://pubs.usgs.gov/unnumbered/70043847/report.pdf",
             page="https://pubs.usgs.gov/publication/70043847", published="1993",
             description="The USGS's teaching packet on maps: what a map is and what it is for, where things are "
                         "(grids, latitude and longitude), direction and distance, scale, symbols and the legend, "
                         "how land and elevation are shown (contour lines), map projections, and how maps are made "
                         "and used for navigation and planning, with classroom activities." + MAP_NOTE,
             notice="A teaching packet of the US Geological Survey: a work of the US government (public domain)."),
    K.us_pdf(GROUP, name="dma_datums_grids", title="Datums, Ellipsoids, Grids, and Grid Reference Systems (Defense "
             "Mapping Agency, DMA TM 8358.1, 1992)", subject="Maps and map reading (grids and coordinates)",
             publisher="Defense Mapping Agency (now the National Geospatial-Intelligence Agency)",
             archive="DTIC_ADA247651", published="1992", version="1992 edition (Internet Archive item DTIC_ADA247651)",
             description="The Defense Mapping Agency's technical manual of how positions are given on maps: the "
                         "shape of the earth (ellipsoids) and datums (why the same place has slightly different "
                         "coordinates on different maps), map projections, the UTM and UPS grids, the Military Grid "
                         "Reference System (MGRS) and how to read and write a grid reference, and other national "
                         "grids, with the datum and ellipsoid of each country's maps." + MAP_NOTE,
             notice="A technical manual of the Defense Mapping Agency.", military=True,
             work="a work of the Defense Mapping Agency (US Department of Defense)"),
]

# ====================================================================== old gazetteers and geographies (before 1931)

HISTORICAL = ("Historical: published in {year}, so its countries, borders, names, populations and opinions are those "
              "of its day (many countries named in it no longer exist, and some words about peoples are offensive "
              "today). Use the World Factbook (geo:factbook) for today's facts.")
OLD_GEO = [
    old_book(GROUP, "lippincott_gazetteer_1906_v1", "Lippincott's New Gazetteer of the World, Volume 1 (A to L, "
             "1906)", "Gazetteers (historical)", "Angelo Heilprin and Louis Heilprin (J. B. Lippincott Company)",
             "lippincottsnewga0001ange", 1906,
             "Lippincott's pronouncing gazetteer, volume 1: every country, region, city, town, river, lake, mountain "
             "and island of the world from A to L, with how to say its name, where it is, its population at the "
             "time and a short description.", note=HISTORICAL, country="International"),
    old_book(GROUP, "lippincott_gazetteer_1906_v2", "Lippincott's New Gazetteer of the World, Volume 2 (M to Z, "
             "1906)", "Gazetteers (historical)", "Angelo Heilprin and Louis Heilprin (J. B. Lippincott Company)",
             "lippincottsnewga0002ange", 1906,
             "Lippincott's pronouncing gazetteer, volume 2: the places of the world from M to Z, with pronunciation, "
             "location, population and description.", note=HISTORICAL, country="International"),
    old_book(GROUP, "chambers_concise_gazetteer_1914", "Chambers's Concise Gazetteer of the World (1914)",
             "Gazetteers (historical)", "David Patrick and William Geddie (W. and R. Chambers, London)",
             "chambersconciseg00patrrich", 1914,
             "A one-volume gazetteer of the world on the eve of the First World War: places with pronunciation, "
             "position, population, history and trade.", note=HISTORICAL, country="United Kingdom"),
    old_book(GROUP, "chisholm_commercial_geography_1922", "Handbook of Commercial Geography (George G. Chisholm, "
             "1922 edition)", "Geography of trade (historical)", "George G. Chisholm (Longmans, Green and Co., London)",
             "handbookofcomm00chis", 1922,
             "The classic geography of the world's trade, revised after the First World War: the conditions of "
             "production (climate, soils, transport), the world's commodities from grain and cotton to coal and "
             "metals, and a survey of every country and region with its products, trade routes and ports.",
             note=HISTORICAL, country="United Kingdom"),
]

# ====================================================================== World Bank data books (CC BY 3.0 IGO)

OKR = "https://openknowledge.worldbank.org"
WB_NOTICE = ("Published by the World Bank under the Creative Commons Attribution 3.0 IGO licence (CC BY 3.0 IGO): "
             "\"World Bank. {title}. Washington, DC: World Bank.\" The licence is read from the World Bank's record "
             "at every build. Its figures are those of its year and are dated; the World Bank's own site has the "
             "newest data. This is not an official World Bank translation or edition.")
# (key, Open Knowledge Repository handle, title, what it holds).
WB_BOOKS = [
    ("wb_little_data_book_2016", "10986/23968", "The Little Data Book 2016",
     "The World Bank's pocket book of country figures: one page per country and per region and income group, with "
     "the same key figures for each (population, life expectancy, schooling, income, economy, trade, energy, "
     "environment, communications), mostly for 2014."),
    ("wb_little_green_data_book_2017", "10986/27466", "The Little Green Data Book 2017",
     "The World Bank's pocket book of environment figures: one page per country with its land, forests, farming, "
     "water, energy, emissions, pollution and natural resources, mostly for 2015."),
]


def wb_maker(key, handle, title, what):
    """(book function, sign function) of one World Bank data book, read with the builder's DSpace reader
    (build_textbooks.dspace_book: the licence read from its record, the PDF one page per chapter)."""

    def book_fn(name, work, cache=None, left_out=None, limit=None):
        """The book of a World Bank data book, in this module's group with its credit line."""
        import build_textbooks as B
        book = B.dspace_book((OKR, handle, f"{PREFIX}_{key}", title, "Countries of the world (data)", "World Bank",
                              "CC BY 3.0 IGO"), work, cache, left_out)
        if book is None:
            return None
        book.group, book.description = GROUP, f"{what} {book.description}"
        book.notice = WB_NOTICE.format(title=title)
        book.version = f"Open Knowledge Repository record {handle}"
        if limit:
            book.pages = book.pages[:limit]
        return book

    def sign_fn(name):
        """The sign of a World Bank book: its handle (a published edition does not change)."""
        return K.sha(OKR, handle)

    return book_fn, sign_fn


# ====================================================================== books of several PDFs

def pdf_set_maker(entry, parts):
    """(book function, sign function) of a book made of several PDFs, read with pdf_set.pdf_set_book."""

    def book_fn(name, work, cache=None, left_out=None, limit=None):
        """The book: every PDF of parts, one after another."""
        import pdf_set
        book = pdf_set.pdf_set_book(entry, parts, work, cache, left_out, limit)
        if book is not None:
            book.name = f"{PREFIX}_{entry['name']}"
            book.notice = entry["notice"]
            book.version = f"{len(parts)} PDFs read"
        return book

    def sign_fn(name):
        """The sign of a book of several PDFs: its list of PDFs (the publications are fixed editions)."""
        return K.sha(parts)

    return book_fn, sign_fn


# ====================================================================== the index (a guide by continent and country)

# Other modules whose books are listed in the index under the countries they name, with how each is described. Only
# keys whose name holds a country's name (or one of its ALIASES) are listed; the Defense Language Institute's keys
# only for its "Countries in Perspective" books.
RELATED = [("languages_gov", "lgov:cip_", "Defense Language Institute"), ("peace_corps", "pc:", "Peace Corps"),
           ("peace_corps_languages", "pclang:", "Peace Corps language course"), ("history", "hist:", "History"),
           ("travel_more", "tripmore:", "Old travel guide")]
# The names of a Factbook place as they appear in key names (each an underscore-joined word list), where they are
# not just its own name; a place listed here is matched only by these names.
ALIASES = {
    "Congo DR": ["congo", "zaire", "drcongo", "democratic_republic_of_the_congo"],
    "Congo": ["republic_of_congo", "congo_brazzaville"],
    "Cote d'Ivoire": ["cote_d_ivoire", "cote_divoire", "ivory_coast"],
    "Burma": ["burma", "myanmar"], "Czech Republic": ["czech_republic", "czech"], "The Gambia": ["gambia"],
    "The Bahamas": ["bahamas"],
    "Vatican City (Holy See)": ["holy_see", "vatican"], "Timor-Leste": ["timor_leste", "east_timor"],
    "United Arab Emirates": ["uae", "united_arab_emirates"], "Bosnia and Herzegovina": ["bosnia_and_herzegovina", "bosnia"],
    "Macedonia": ["macedonia", "north_macedonia"], "Swaziland": ["swaziland", "eswatini"],
    "Micronesia": ["micronesia"], "Solomon Islands": ["solomons", "solomon_islands"],
    "Papua New Guinea": ["papua_new_guinea", "new_guinea", "png", "papua", "tok_pisin"], "Cape Verde": ["cape_verde", "cabo_verde"],
    "Sao Tome and Principe": ["sao_tome"], "Saint Lucia": ["saint_lucia", "st_lucia"],
    "Trinidad and Tobago": ["trinidad"], "Guinea-Bissau": ["guinea_bissau"],
    "Central African Republic": ["central_african_republic", "car"], "West Bank": ["west_bank", "palestine"],
    "Marshall Islands": ["marshall_islands"], "Western Sahara": ["western_sahara"],
    # languages spoken in one country only, as the Peace Corps courses name them
    "Thailand": ["thailand", "thai"], "Nepal": ["nepal", "nepali"], "Mongolia": ["mongolia", "mongolian"],
    "Philippines": ["philippines", "philippine", "tagalog", "cebuano", "ilokano", "ilonggo", "bikol", "ivatan",
                    "aklanon"],
    "South Korea": ["south_korea", "korea", "korean"], "Fiji": ["fiji", "fijian"], "Samoa": ["samoa", "samoan"],
    "Vanuatu": ["vanuatu", "bislama"], "Albania": ["albania", "albanian"], "Armenia": ["armenia", "armenian"],
    "Azerbaijan": ["azerbaijan", "azerbaijani"], "Bulgaria": ["bulgaria", "bulgarian"],
    "Estonia": ["estonia", "estonian"], "Sri Lanka": ["sri_lanka", "sinhala"], "Bangladesh": ["bangladesh", "bangla"],
    "Afghanistan": ["afghanistan", "dari"], "Madagascar": ["madagascar", "malagasy", "sakalava"],
    "Lesotho": ["lesotho", "sesotho"], "Botswana": ["botswana", "setswana"], "Malawi": ["malawi", "chichewa"],
}
# Places never matched by name (their names are too common as words in book keys), and keys never matched (the
# history books of US states, such as Georgia and New Mexico).
NEVER_MATCHED = {"United States", "Jersey", "Guernsey"}
NEVER_KEYS = re.compile(r"^hist:state_")


def aliases(place):
    """The word lists (tuples) that stand for a place in key names: its ALIASES, else its own name (without
    "The")."""
    own = re.sub(r"[^a-z0-9]+", "_", re.sub(r"^the ", "", place.lower().replace("'", ""))).strip("_")
    names = ALIASES.get(place) or [own]
    return [tuple(n.split("_")) for n in names]


def places_named(key, places=None):
    """The Factbook places a book key names (see RELATED), longest names first so "papua_new_guinea" is not also
    "guinea" and "south_sudan" not also "sudan"."""
    places = PLACES if places is None else places
    if NEVER_KEYS.search(key):
        return []
    words = re.split(r"[_:\-]+", key.split(":", 1)[-1].lower())
    used = [False] * len(words)
    found = []
    candidates = sorted(((len(a), p, a) for p in places if p not in NEVER_MATCHED for a in aliases(p)),
                        key=lambda x: -x[0])
    for size, place, alias in candidates:
        for i in range(len(words) - size + 1):
            if tuple(words[i:i + size]) == alias and not any(used[i:i + size]):
                used[i:i + size] = [True] * size
                if place not in found:
                    found.append(place)
    return found


def related_books():
    """{place: [(key, label, title)]} of the other modules' books (RELATED) that name a place, read from the code at
    build time."""
    import more_refs
    out = {}
    for module_name, prefix, label in RELATED:
        module = next((m for m in more_refs.modules() if m.__name__ == module_name), None)
        if module is None:
            continue
        c = module.COLLECTION
        for key in c.own_keys():
            if not key.startswith(prefix) or key.endswith(":index"):
                continue
            entry = c.pdfs.get(key.split(":", 1)[1]) or c.guides.get(key.split(":", 1)[1]) or {}
            for place in places_named(key):
                out.setdefault(place, []).append((key, label, entry.get("title") or key))
    return out


# The copyrighted Area Handbooks of 1978 to 1986 and ERIC's copyrighted copies: link-only, listed under their
# countries. (place, title, Internet Archive item, year, what its copy prints).
LINK_ONLY = [
    ("Afghanistan", "Afghanistan: A Country Study", "DTIC_ADA176034", 1986, "Copyright (c) 1986 United States "
     "Government as represented by the Secretary of the Army"),
    ("Argentina", "Argentina: A Country Study", "DTIC_ADA175758", 1985, "Copyright (c) 1985 United States Government "
     "as represented by the Secretary of the Army"),
    ("Burma", "Burma: A Country Study", "DTIC_ADA142227", 1983, "Copyright (c) 1983 United States Government as "
     "represented by the Secretary of the Army"),
    ("Burma", "Area Handbook for Burma (ERIC's copy)", "ERIC_ED059142", 1971, "ERIC's stamp \"permission to reproduce "
     "this copyrighted material\""),
    ("Costa Rica", "Costa Rica: A Country Study", "DTIC_ADA150076", 1983, "Copyright (c) 1983 United States "
     "Government as represented by the Secretary of the Army"),
    ("Guatemala", "Guatemala: A Country Study", "DTIC_ADA142359", 1983, "Copyright (c) 1983 United States Government "
     "as represented by the Secretary of the Army"),
    ("Italy", "Italy: A Country Study", "DTIC_ADA189672", 1985, "Copyright (c) 1985 United States Government as "
     "represented by the Secretary of the Army"),
    ("Kenya", "Kenya: A Country Study", "DTIC_ADA147503", 1983, "Copyright (c) 1984 United States Government as "
     "represented by the Secretary of the Army. All rights reserved"),
    ("Liberia", "Liberia: A Country Study", "DTIC_ADA159331", 1985, "Copyright (c) 1985 United States Government as "
     "represented by the Secretary of the Army"),
    ("Morocco", "Morocco: A Country Study", "DTIC_ADA169723", 1985, "Copyright (c) 1985 United States Government as "
     "represented by the Secretary of the Army"),
    ("Australia", "Area Handbook for Oceania (ERIC's copy)", "ERIC_ED056946", 1970, "ERIC's stamp \"permission to "
     "reproduce this copyrighted material\""),
    ("Tanzania", "Tanzania: A Country Study", "DTIC_ADA064121", 1978, "Copyright (c) The American University, 1978"),
    ("Tunisia", "Tunisia: A Country Study", "DTIC_ADA195427", 1986, "Copyright (c) 1988 United States Government as "
     "represented by the Secretary of the Army"),
    ("Zambia", "Zambia: A Country Study", "DTIC_ADA080107", 1979, "Copyright (c) The American University"),
    ("Zimbabwe", "Zimbabwe: A Country Study", "DTIC_ADA135022", 1983, "Copyright (c) 1983 United States Government "
     "as represented by the Secretary of the Army"),
]


def own_books():
    """{place: [(key, label, title)]} of this module's country books (country studies, older handbooks, Background
    Notes)."""
    out = {}
    for entries, label in ((STUDY_PDFS, "Country study"), (OLD_PDFS, "Older Area Handbook"),
                           (BGN_PDFS, "Background Notes")):
        for e in entries:
            for place in e["places"]:
                out.setdefault(place, []).append((f"{PREFIX}:{e['name']}", label, e["title"]))
    return out


def factbook_line(place):
    """The index's line for a place's World Factbook page: which index page of the Factbook to open."""
    folder = PLACES[place][0]
    continent = next(c for f, _r, c in G.REGIONS if f == folder)
    return ("key", "geo:factbook", f"The World Factbook's page on {place}: open the Factbook's \"Index: {continent}\" "
                                   f"and choose {place}")


def country_entries(place, own=None, related=None):
    """The index entries of one place: the Factbook page, this module's books, the other modules' books and the
    copyrighted editions that are links only."""
    own = own_books() if own is None else own
    related = {} if related is None else related
    entries = [factbook_line(place)]
    for key, label, title in own.get(place, []) + related.get(place, []):
        entries.append(("key", key, f"{label}: {title}"))
    for where, title, item, year, printed in LINK_ONLY:
        if where == place:
            entries.append(("link", f"{title} ({year})", f"https://archive.org/details/{item}",
                            f"its copy prints \"{printed}\": still in copyright, so link-only"))
    return entries


MAP_ENTRIES = [
    ("key", "ctry:usgs_exploring_maps", "Exploring Maps (USGS): what maps show, grids, latitude and longitude, "
                                        "direction, distance, scale, symbols, contour lines and projections"),
    ("key", "ctry:usgs_map_basics", "USGS fact sheets: map scales, using a map and compass, the UTM grid and US Topo "
                                    "maps"),
    ("key", "pdf:usgs_topographic_map_symbols", "Topographic Map Symbols (USGS): every symbol on a topographic map in "
                                                "words: contour lines, roads, buildings, boundaries, water, plants"),
    ("key", "pdf:army_fm_3_25_26_map_reading", "Map Reading and Land Navigation (Army FM 3-25.26): grid references, "
                                               "the compass, elevation and relief, terrain, orienteering and GPS"),
    ("key", "ctry:dma_datums_grids", "Datums, Ellipsoids, Grids and Grid Reference Systems (Defense Mapping Agency): "
                                     "why coordinates differ between maps, UTM, UPS and the military grid (MGRS)"),
    ("key", "pdf:usgs_map_projections_working_manual", "Map Projections: A Working Manual (USGS): how the round earth "
                                                       "is drawn flat, projection by projection"),
    ("key", "pdf:usgs_map_projections_bulletin_1532", "Map Projections Used by the USGS (shorter)"),
    ("key", "pdf:noaa_us_chart_no_1", "U.S. Chart No. 1 (NOAA and NGA): every symbol and abbreviation on nautical "
                                      "charts: depths, dangers, buoys, lights and harbours"),
    ("key", "pdf:faa_aeronautical_chart_users_guide", "Aeronautical Chart User's Guide (FAA): the symbols of air "
                                                      "charts"),
    ("key", "pdf:bowditch_american_practical_navigator_1914", "The American Practical Navigator (Bowditch, 1914): "
                                                               "navigation at sea, charts and tables"),
    ("key", "ctry:census_garm", "Geographic Areas Reference Manual (Census Bureau): states, counties, places, tracts, "
                                "blocks, metropolitan areas and how areas are measured"),
]
WORLD_ENTRIES = [
    ("key", "geo:factbook", "The World Factbook (CIA, last edition): every country, territory and ocean, with the map "
                            "in words"),
    ("key", "geo:index", "World geography: the library's geography guide"),
    ("key", "ctry:wb_little_data_book_2016", "The Little Data Book 2016 (World Bank): one page of figures per "
                                             "country"),
    ("key", "ctry:wb_little_green_data_book_2017", "The Little Green Data Book 2017 (World Bank): environment figures "
                                                   "per country"),
    ("key", "ctry:lippincott_gazetteer_1906_v1", "Lippincott's New Gazetteer, A to L (1906, historical)"),
    ("key", "ctry:lippincott_gazetteer_1906_v2", "Lippincott's New Gazetteer, M to Z (1906, historical)"),
    ("key", "ctry:chambers_concise_gazetteer_1914", "Chambers's Concise Gazetteer of the World (1914, historical)"),
    ("key", "ctry:chisholm_commercial_geography_1922", "Chisholm's Handbook of Commercial Geography (1922, "
                                                       "historical)"),
    ("word", "lgov-dli-countries", "The Defense Language Institute's Countries in Perspective books, all 83"),
    ("word", "pub:history", "History periodicals and the State Department's Foreign Relations of the United States "
                            "(FRUS) volumes"),
    ("word", "travel", "Travel books"),
    ("key", "pclang:index", "Peace Corps language courses, by language and country"),
    ("key", "pc:index", "Peace Corps manuals and guides"),
]
LINKS = [
    ("State Department country pages and travel advisories", "https://www.state.gov/countries-and-areas-list/",
     "state.gov refuses programs; open it in a browser"),
    ("State Department Background Notes, archived to about 2012", "https://2009-2017.state.gov/r/pa/ei/bgn/index.htm",
     "the archive refuses programs; the 1982 to 1990 editions are built here"),
    ("Library of Congress Country Studies (the 80 books online)", LOC_COLLECTION,
     "the same books as here, as the Library's own web pages and PDFs"),
    ("UN Statistical Yearbook", "https://unstats.un.org/UNSDWebsite/publications/statistical-yearbook/",
     "copyright United Nations: link-only"),
    ("World Bank open data (the newest figures)", "https://data.worldbank.org/", "a data site (CC BY 4.0), not a book"),
]


def index_sections(related=None):
    """[(part, intro, [(heading, entries)])] of the index: a part per continent with a heading per place, then maps,
    the world and links. related: {place: books} of the other modules (related_books() when None)."""
    related = related_books() if related is None else related
    own = own_books()
    parts = [("How to use this guide", "This guide lists every book about countries in the library, by part of the "
              "world and then by country, with the key to ask for each. Each country lists its World Factbook page "
              "first (the newest facts, from the CIA's last edition of 2026), then the Library of Congress country "
              "study (a full book on its history, people, economy and government, written between 1988 and 2015), "
              "the State Department's Background Notes (a short profile from the 1980s), older Army handbooks, the "
              "Defense Language Institute's country book, Peace Corps books and language courses, history books and "
              "old travel guides. The older books are history: their political facts are dated. Countries that no "
              "longer exist (the Soviet Union, Yugoslavia, Czechoslovakia, East Germany, Zaire) are listed under "
              "the countries of today.", [("Parts of the world", [("word", f"ctry-{w}", f"{t}: this module's books")
                                                                   for w, t in CONTINENTS])])]
    for word, title in CONTINENTS:
        headings = []
        for place in sorted((p for p, (_f, c) in PLACES.items() if c == word), key=str.lower):
            headings.append((place, country_entries(place, own, related)))
        parts.append((title, f"The countries and territories of {title.lower() if word != 'americas' else 'the Americas'}"
                      f", in alphabetical order, each a heading.", headings))
    parts.append(("Maps and map reading", "The library's map-reading guides, described in words: no map pictures are "
                  "needed. A map's scale says how much smaller it is than the land (1:24,000 means one inch on the "
                  "map is 24,000 inches, about a third of a mile); its grid or latitude and longitude give a position "
                  "as two numbers; contour lines join points of the same height, so lines close together mean steep "
                  "ground; symbols in the legend stand for roads, water, buildings and boundaries; and a compass "
                  "bearing, corrected for the difference between true and magnetic north, says which way to go.",
                  [("Map-reading guides", MAP_ENTRIES)]))
    parts.append(("Gazetteers, data books and the world", "The whole world in one book: the World Factbook, data "
                  "books, old gazetteers (historical) and the other collections with books about countries.",
                  [("Books and collections", WORLD_ENTRIES)]))
    parts.append(("Links only", "Sources the builder cannot read or may not copy; open them in a browser.",
                  [("Links", [("link", n, u, why) for n, u, why in LINKS])]))
    return parts


def index_book(name, work, cache=None, left_out=None, limit=None):
    """ctry:index: one page per part (see index_sections), each place a heading with its books as a list."""
    import build_textbooks as B
    import practical_index as X
    left_out = left_out if left_out is not None else []
    book = K.new_book(f"{PREFIX}_index", "Countries of the world: a guide to the library by continent and country",
                      "Countries of the world", GROUP, "Digital Accessibility Toolkit (an index of the library)",
                      X.CC0_INDEX, K.CC0_URL, X.TOOLKIT_REPO,
                      "A guide to every country book in the library, by continent and country: the World Factbook, "
                      "the Library of Congress country studies, Background Notes, the Defense Language Institute's "
                      "country books, Peace Corps books and courses, history and old travel guides; then maps and map "
                      "reading, gazetteers and data books, and the links.",
                      "Facts and links only (CC0). Each book listed has its own licence, shown in that book; each "
                      "link-only source belongs to its publisher.", country="International",
                      changes="an index written for the toolkit")
    known = {}
    for number, (part, intro, headings) in enumerate(index_sections(), 1):
        if limit and len(book.pages) >= limit:
            break
        body = [f"<p>{B.esc(intro)}</p>"]
        for heading, entries in headings:
            items = []
            for kind, what, words, *more in entries:
                if kind == "key":
                    if what not in known:
                        known[what] = X.key_exists(what)
                    if not known[what]:
                        left_out.append({"title": what, "reason": "The library has no book with this key now."})
                        continue
                    items.append(f"<li>{B.esc(words)} (key {B.esc(what)})</li>")
                elif kind == "word":
                    items.append(f"<li>{B.esc(words)} (request word {B.esc(what)})</li>")
                else:
                    items.append(f'<li>Link only: {B.esc(what)}: <a href="{B.esc(words)}">{B.esc(words)}</a>. '
                                 f"{B.esc(more[0])}.</li>")
            if items:
                body.append(f"<h2>{B.esc(heading)}</h2><ul>{''.join(items)}</ul>")
        book.pages.append(B.Page(f"part-{number}-{B.slug(part, 40)}", part, "".join(body), number, ""))
    book.published = ""
    book.version = "made from the library's code at build time"
    return book


def index_sign(name):
    """The weekly sign of the index: a fingerprint of everything it lists (it changes when books are added)."""
    return K.sha(index_sections())


# ====================================================================== the collection and its request words

PDFS = STUDY_PDFS + OLD_PDFS + BGN_PDFS + MAP_PDFS + OLD_GEO
MAKERS = {"index": (index_book, index_sign), "usgs_map_basics": pdf_set_maker(USGS_MAP_BASICS, MAP_BASICS_PARTS),
          "census_garm": pdf_set_maker(CENSUS_GARM, [(t, GARM_BASE + f, GARM_BASE) for t, f in GARM_PARTS])}
MAKERS.update({key: wb_maker(key, handle, title, what) for key, handle, title, what in WB_BOOKS})
MAP_KEYS = ["ctry:usgs_exploring_maps", "ctry:usgs_map_basics", "ctry:dma_datums_grids", "ctry:census_garm"]


def continent_keys(word):
    """ctry:index and this module's country books about the places of one part of the world (CONTINENTS)."""
    keys = [f"{PREFIX}:index"]
    for e in STUDY_PDFS + OLD_PDFS + BGN_PDFS:
        if any(PLACES[p][1] == word for p in e["places"]):
            keys.append(f"{PREFIX}:{e['name']}")
    return keys


def every_key():
    """Every key of this module (the request word countries)."""
    return [f"{PREFIX}:index"] + [f"{PREFIX}:{p['name']}" for p in PDFS] + \
        [f"{PREFIX}:{k}" for k in MAKERS if k != "index"]


WORDS = {f"ctry-{w}": (lambda w=w: continent_keys(w)) for w, _t in CONTINENTS}
WORDS["ctry-maps"] = lambda: [f"{PREFIX}:index"] + MAP_KEYS
WORDS["countries"] = every_key
COLLECTION = K.Collection(PREFIX, GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "countries_loc_studies": "Library of Congress Country Studies (Federal Research Division, 1988 to 2015), read from "
                             "the Internet Archive's copies of the Library's scans (collection library_of_congress) "
                             "and one DTIC copy (Greece): the Library's rights statement for the series (loc.gov, "
                             "read at every build): \"Several of the books in the series contain photographs that have "
                             "been copyrighted. The captions for these photographs clearly indicate the protected "
                             "status of the images. All other text and graphics are in the public domain.\" (checked "
                             "2026-11-23). Judged also by the release rule for military publications (DA Pam 550).",
    "countries_old_handbooks": "Area Handbooks of 1969 to 1977 (Foreign Area Studies, The American University, for "
                               "the Army; sold by the Government Printing Office): no copyright notice printed (front "
                               "pages read 2026-11-23, and checked again at every build, OLD_FRONT); published "
                               "before 1978 without a notice, so public domain in the US.",
    "countries_background_notes": "State Department Background Notes, 1982 to 1990, from the Internet Archive's scans "
                                  "of the GPO microfiche (us-government-printing-office collection) and ERIC: works "
                                  "of the US government (17 U.S.C. 105); archive.org's robots.txt allows the files.",
    "countries_maps": "USGS fact sheets and Exploring Maps (pubs.usgs.gov, robots.txt allows /fs/ and /unnumbered/), "
                      "the Census Bureau's Geographic Areas Reference Manual (www2.census.gov, no robots.txt rule for "
                      "our reader) and the Defense Mapping Agency's TM 8358.1 (DTIC copy on the Internet Archive): "
                      "works of the US government (checked 2026-11-23).",
    "countries_world_bank": "World Bank Open Knowledge Repository records 10986/23968 and 10986/27466: dc.rights "
                            "\"CC BY 3.0 IGO\" (checked 2026-11-23; read again at every build).",
}

NOT_INCLUDED = [
    ("Army Area Handbooks of 1978 to 1986 by Foreign Area Studies, The American University: Afghanistan (1986), "
     "Argentina (1985), Burma (1983), Costa Rica (1983), Guatemala (1983), Italy (1985), Kenya (1983), Liberia (1985), "
     "Morocco (1985), Tanzania (1978), Tunisia (1986), Zambia (1979), Zimbabwe (1983)", "Their copies (DTIC scans on "
     "the Internet Archive) print \"Copyright (c) The American University\" or \"Copyright (c) <year> United States "
     "Government as represented by the Secretary of the Army. All rights reserved.\" They were written under contract, "
     "not by government staff, and are not in the Library of Congress's public-domain collection: still in copyright, "
     "so link-only (ctry:index lists each under its country). For Afghanistan, Guatemala and Italy the public-domain "
     "editions of 1973, 1970 and 1977 are built. Index: https://archive.org/details/DTIC_ADA147503"),
    ("ERIC's copies of the Area Handbooks for Oceania (1970) and Burma (1971)", "ERIC stamped them \"permission to "
     "reproduce this copyrighted material ... has been granted\", so they are treated as copyrighted: link-only. "
     "Index: https://archive.org/details/ERIC_ED056946"),
    ("Microfiche copies of the Belgium, Morocco and Rwanda country studies (micro_IA41152808_0570, "
     "micro_IA41152823_0081, micro_IA41152808_0567)", "Only one page of each was scanned so far (checked 2026-11-23); "
     "no other downloadable copy of these editions was found. Index: "
     "https://archive.org/details/micro_IA41152808_0570"),
    ("Area Handbooks of the 1960s and 1970s for countries with a later country study (Albania, Bulgaria, Romania, "
     "Germany, South Vietnam, North Korea, China, Cuba, Ecuador, Honduras, Laos, Mexico, Thailand, Uruguay, Jordan, "
     "the Indian Ocean territories, South Africa, Czechoslovakia, Bolivia, Colombia, Nepal)", "Left out on purpose: the "
     "later Library of Congress country study is built instead (the owner's rule: older handbooks only for countries "
     "without a later edition). Index: https://archive.org/search?query=title%3A%22area+handbook+for%22"),
    ("The other editions of the country studies on the Internet Archive", "Lending-library copies (not downloadable) "
     "and duplicate uploads of the same editions; the Library of Congress's own scans are built. Index: "
     "https://archive.org/details/library_of_congress"),
    ("State Department Background Notes after 1990 and the \"U.S. Relations With\" fact sheets", "Public domain, but "
     "www.state.gov and its archives (1997-2001, 2001-2009 and 2009-2017.state.gov) answer programs with an error "
     "page (checked 2026-11-23), and the GPO's permanent copies (permanent.access.gpo.gov) are closed to programs by "
     "its robots.txt. The 1982 to 1990 editions on the Internet Archive are built. Index: "
     "https://2009-2017.state.gov/r/pa/ei/bgn/index.htm"),
    ("UN Statistical Yearbook and other UN country data books", "Copyright United Nations (the UNdata terms free the "
     "data, not the books): link-only. Index: https://unstats.un.org/UNSDWebsite/publications/statistical-yearbook/"),
    ("World Development Indicators (World Bank) and newer World Bank data books", "CC BY 3.0 IGO, but the WDI books "
     "are mostly large tables better read as data; the Little Data Book 2016 and Little Green Data Book 2017 give "
     "each country's figures as one page. The World Bank's data site has the newest figures (CC BY 4.0). Index: "
     "https://openknowledge.worldbank.org/"),
    ("USGS \"Maps for America\" (Thompson, 1979 to 1987)", "The Internet Archive's copies are lending-library scans and "
     "pubs.usgs.gov has no PDF of it (checked 2026-11-23). Index: https://archive.org/details/mapsforamericaca00thom"),
    ("Lippincott's Gazetteer of the World editions of 1880 to 1898, Longman's Gazetteer (1895, 1906) and the Columbia "
     "Lippincott Gazetteer (1952, 1961)", "The 1906 Lippincott's New Gazetteer and the 1914 Chambers's are built as "
     "the newest public-domain gazetteers; the older editions repeat them, and the Columbia Lippincott (after 1930) is "
     "still in copyright and a lending-library scan. Index: https://archive.org/details/lippincottsnewga0001ange"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
