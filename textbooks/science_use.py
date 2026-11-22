"""Science you can use for the reference library, in the group "Reference, science you can use" (the owner's request
of 2026-11-22). Keys: science-use (every book), science:<name>.

What this module builds, in plain words, each IN FULL from the US government agency that publishes it:
  - measurements and units: NIST Special Publication 811, the Guide for the Use of the International System of Units
    (SI) (2008, with its conversion factors from US customary units), NIST Special Publication 330, The International
    System of Units (SI) (2019), and NIST's unit conversion page (cooking, length, weight, volume and temperature);
  - the periodic table: NIST's Periodic Table of the Elements (2024: every element's symbol, number, atomic weight,
    ground state and ionisation energy, read from its PDF);
  - water: the USGS Water Science School (the water cycle, groundwater, water quality, how much water we use, water
    properties and floods), every page its sitemap lists;
  - earthquakes: the USGS Earthquake Hazards Program's pages for everyone (the science of earthquakes, cool
    earthquake facts, and how to prepare);
  - the ocean: NOAA's National Ocean Service "Ocean Facts", every fact page (tides, currents, waves, sea life, the
    deep sea, coasts and navigation);
  - the night sky: NASA's Skywatching pages (What's Up each month, the planets, meteor showers, eclipses, the Moon's
    phases and how to observe them).
  Every book says in its notice what to do in danger (earthquakes: drop, cover and hold on; the ocean: rip currents).

Already in the library and not repeated: the NIST weights-and-measures handbooks (Handbook 44, 130 and 133:
reference_more.py), the USGS's This Dynamic Earth (plate tectonics), the NWS weather safety pages and NOAA Weather
Radio (prep:), NASA's news releases (periodicals), the OpenStax physics, chemistry, astronomy and biology textbooks
(the "Textbooks" group: college-physics-bundle, university-physics-bundle, chemistry-bundle, astronomy), and
Wikibooks whole in the Kiwix library.

Not built (NOT_INCLUDED, link-only): the NWS JetStream online weather school (refuses programs), PubChem's periodic
table (robots.txt refuses programs), NOAA's education resource collections (refuse programs), climate.gov (refuses
programs), NASA Space Place (a NASA/JPL site whose pages carry JPL's terms), SciJinks (did not answer).

Run from the repository's folder:
  python3 textbooks/science_use.py science:noaa_ocean_facts --out build/textbooks --limit 3
  python3 textbooks/science_use.py --list science-use
"""

import datetime
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "scienceuse"
GROUPS = {GROUP: "Reference, science you can use"}

NIST = "National Institute of Standards and Technology (NIST)"
QUAKE_SAFETY = ("In an earthquake: drop, cover and hold on; stay away from windows; after the shaking, check for gas "
                "leaks and expect aftershocks. In danger call 911.")
OCEAN_SAFETY = ("At the beach: if a rip current pulls you, swim parallel to the shore, then back to land; swim near a "
                "lifeguard, and leave the water when thunder roars.")

PDFS = [
    K.us_pdf(GROUP, name="nist_sp811_si_guide", title="Guide for the Use of the International System of Units (SI) "
             "(NIST Special Publication 811, 2008)", subject="Measurements and units", publisher=NIST,
             pdf="https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf",
             page="https://www.nist.gov/pml/special-publication-811", published="2008-03", version="2008 edition",
             description="NIST's guide to using metric (SI) units correctly: the base and derived units, prefixes "
                         "(kilo, milli, micro), writing unit symbols and numbers, units accepted for use with the SI, "
                         "and the long appendix of conversion factors from US customary and other units to SI.",
             notice="A work of NIST (public domain)."),
    K.us_pdf(GROUP, name="nist_sp330_si_2019", title="The International System of Units (SI) (NIST Special "
             "Publication 330, 2019)", subject="Measurements and units", publisher=NIST,
             pdf="https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.330-2019.pdf",
             page="https://www.nist.gov/pml/special-publication-330", published="2019-08", version="2019 edition",
             description="The United States edition of the SI brochure after the 2019 redefinition: the seven "
                         "defining constants, the base units (second, metre, kilogram, ampere, kelvin, mole, candela) "
                         "and how each is defined, derived units, prefixes and writing rules.",
             notice="A work of NIST (public domain)."),
    K.us_pdf(GROUP, name="nist_periodic_table", title="Periodic Table of the Elements (NIST, 2024)",
             subject="The periodic table", publisher=NIST,
             pdf="https://www.nist.gov/system/files/documents/2024/06/25/NIST_periodictable_June24_iupac.pdf",
             page="https://www.nist.gov/pml/periodic-table-elements", published="2024-06", version="June 2024 edition",
             description="NIST's one-page periodic table: each element's atomic number, symbol, name, standard "
                         "atomic weight, ground-state configuration and ionisation energy, with the groups and "
                         "periods and the defining constants. It is a chart, so its words are read in the PDF's own "
                         "order (element by element).",
             notice="A work of NIST (public domain)."),
]

GUIDES = [
    K.us_web(GROUP, name="nist_unit_conversion", title="Unit conversion: metric and US customary units (NIST)",
             subject="Measurements and units", publisher=NIST + ", Office of Weights and Measures",
             source="https://www.nist.gov/pml/owm/metric-si/unit-conversion",
             crawl=[("https://www.nist.gov/pml/owm/metric-si/unit-conversion", 0)],
             urls=["https://www.nist.gov/pml/owm/metric-si/unit-conversion",
                   "https://www.nist.gov/pml/owm/metric-si/si-units"],
             pages=r"^https://www\.nist\.gov/pml/owm/metric-si/[a-z0-9-]+$", limit=8,
             description="NIST's pages on converting between metric and US customary units (length, area, volume, "
                         "weight, temperature, and cooking measures) and the SI units.",
             notice="A work of NIST (public domain)."),
    K.us_web(GROUP, name="usgs_earthquakes_for_everyone", title="Earthquakes for everyone: the science, facts and "
             "preparing (USGS)", subject="Earthquakes", publisher="US Geological Survey (USGS), Earthquake Hazards "
             "Program", source="https://www.usgs.gov/programs/earthquake-hazards/education",
             crawl=[("https://www.usgs.gov/programs/earthquake-hazards/education", 0)],
             urls=["https://www.usgs.gov/programs/earthquake-hazards/education",
                   "https://www.usgs.gov/programs/earthquake-hazards/science-everyone",
                   "https://www.usgs.gov/natural-hazards/earthquake-hazards/science/science-earthquakes",
                   "https://www.usgs.gov/natural-hazards/earthquake-hazards/science/cool-earthquake-facts",
                   "https://www.usgs.gov/natural-hazards/earthquake-hazards/science/prepare"],
             pages=r"^https://www\.usgs\.gov/(programs|natural-hazards)/earthquake-hazards/(science/)?[a-z0-9-]+$",
             licence_page="https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
             licence_text=r"the content of most USGS websites is in the U\.S\. Public Domain", limit=10,
             description="The USGS Earthquake Hazards Program's pages for everyone: what earthquakes are and why they "
                         "happen (faults, plates, seismic waves, magnitude and intensity), cool earthquake facts, and "
                         "how to prepare and stay safe.",
             notice="From the US Geological Survey: a US government work (public domain). " + QUAKE_SAFETY),
    K.guide(GROUP, "noaa_ocean_facts", "Ocean Facts (NOAA National Ocean Service)", "The ocean",
            "NOAA National Ocean Service", "https://oceanservice.noaa.gov/facts",
            r"^https://oceanservice\.noaa\.gov/facts/[a-z0-9-]+\.html$",
            "NOAA's Ocean Facts, every fact page: why the ocean is salty and blue, tides, currents and waves, rip "
            "currents, tsunamis, the deep sea and its animals, coral reefs, coasts and estuaries, navigation and "
            "charts, and how people use and protect the ocean.",
            "From NOAA's National Ocean Service: a US government work (public domain). " + OCEAN_SAFETY, depth=2,
            follow=r"^https://oceanservice\.noaa\.gov/facts/oceanfacts-[a-z]+\.html$",
            units=[(r"oceanfacts-", "Ocean facts by topic"), (r".", "Ocean facts")], limit=260),
    dict(K.guide(GROUP, "nasa_skywatching", "Skywatching: the night sky month by month (NASA)", "Astronomy and the "
                 "night sky", "National Aeronautics and Space Administration (NASA)", "https://science.nasa.gov/"
                 "skywatching", r"^https://science\.nasa\.gov/skywatching(/[a-z0-9-]+){1,2}/?$",
                 "NASA's Skywatching pages: What's Up (the planets, stars and events to look for each month), the "
                 "Moon's phases, meteor showers, eclipses, the night sky with binoculars and a telescope, and tips "
                 "for observing.",
                 "From NASA: \"NASA content ... generally are not subject to copyright in the United States\" "
                 "(NASA's media usage guidelines, checked at every build); NASA does not endorse this copy. Never "
                 "look at the Sun without proper solar filters.", depth=1, limit=80),
         licence_page="https://www.nasa.gov/nasa-brand-center/images-and-media/",
         licence_text=r"generally are not subject to copyright in the United States"),
]

# ====================================================================== the USGS Water Science School (a maker)

# Its pages are listed only near the end of usgs.gov's 77-part sitemap (past the 50 parts the shared reader looks at),
# and the school has copies of many pages in other languages, so this module finds the English pages itself.
USGS_SITEMAP = "https://www.usgs.gov/sitemap.xml"
WSS_PAGES = r"^https://www\.usgs\.gov/water-science-school/science/[a-z0-9-]+$"
# The language versions end with the language's name ("...-water-cycle-punjabi"); they are left out.
WSS_LANGUAGE = re.compile(r"-(spanish|espanol|portuguese|french|german|italian|russian|ukrainian|polish|chinese|"
                          r"japanese|korean|vietnamese|thai|indonesian|malay|tagalog|hindi|bengali|punjabi|urdu|"
                          r"nepali|tamil|telugu|marathi|gujarati|kannada|malayalam|sinhala|burmese|khmer|lao|"
                          r"mongolian|kazakh|uzbek|kyrgyz|tajik|turkmen|azerbaijani|armenian|georgian|turkish|"
                          r"arabic|persian|farsi|pashto|hebrew|greek|amharic|somali|swahili|hausa|yoruba|igbo|zulu|"
                          r"xhosa|afrikaans|dutch|swedish|norwegian|danish|finnish|icelandic|czech|slovak|slovenian|"
                          r"croatian|serbian|bosnian|bulgarian|romanian|hungarian|albanian|macedonian|latvian|"
                          r"lithuanian|estonian|belarusian|basque|catalan|galician|welsh|irish|maltese|haitian|"
                          r"creole|hmong|samoan|maori|hawaiian|quechua|guarani|esperanto|latin|[a-z]+-language)$")
WSS_ENTRY = K.us_web(
    GROUP, name="usgs_water_science_school", title="The USGS Water Science School", subject="Water science",
             publisher="US Geological Survey (USGS)", source="https://www.usgs.gov/water-science-school",
             pages=WSS_PAGES,
             unit_rules=[(r"groundwater|aquifer|well", "Groundwater"), (r"quality|ph-|hardness|temperature|"
                                                                        r"turbidity|nitrogen|bacteria", "Water quality"),
                         (r"use|irrigation|domestic|industrial|thermoelectric", "Water use"),
                         (r"flood|drought|stream|river|runoff", "Rivers, floods and droughts"),
                         (r".", "The water cycle and water's properties")],
             licence_page="https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
             licence_text=r"the content of most USGS websites is in the U\.S\. Public Domain", limit=220,
             description="The USGS's school of water for everyone, every page: the water cycle and where the "
                         "world's water is, groundwater and wells, water properties (density, surface tension, "
                         "hardness, pH), water quality, how much water people use at home, on farms and in industry, "
                         "rivers, floods and droughts.",
             notice="From the US Geological Survey: a US government work (public domain; pictures by others are left "
                    "out).")


def water_science_urls(cache=None):
    """The English Water Science School pages listed in usgs.gov's sitemap (every part of its index is read, one
    request at a time)."""
    import build_textbooks as B
    pages, found = re.compile(WSS_PAGES), []
    parts = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", B.fetch(USGS_SITEMAP, cache))
    for part in parts:
        for url in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", B.fetch(html.unescape(part), cache)):
            if pages.match(url) and not WSS_LANGUAGE.search(url):
                found.append(url)
    return sorted(dict.fromkeys(found))


def water_science_book(name, work, cache=None, left_out=None, limit=None):
    """The Water Science School as one book: its English pages from the sitemap, read by directory_sources'
    guide reader (which checks robots.txt and the USGS licence line at every build)."""
    import directory_sources as D
    urls = water_science_urls(cache)
    if not urls:
        (left_out if left_out is not None else []).append({"title": WSS_ENTRY["title"],
                                                           "reason": "The sitemap listed no pages."})
        return None
    entry = dict(WSS_ENTRY, urls=urls[:WSS_ENTRY["limit"]], crawl=None, sitemap="", start=[])
    book = D.guide_book(entry, cache, left_out, limit)
    if book is not None:
        book.name = "science_usgs_water_science_school"
        book.version = f"pages read {datetime.date.today().isoformat()}"
    return book


def water_science_sign(name):
    """The weekly check's sign for the Water Science School: the month, so it is read again once a month."""
    import directory_sources as D
    return D.month_token()


COLLECTION = K.Collection(
    "science", GROUP, guides=GUIDES, pdfs=PDFS,
    makers={"usgs_water_science_school": (water_science_book, water_science_sign)},
    words={"science-use": lambda: [f"science:{g['name']}" for g in GUIDES + PDFS] + ["science:usgs_water_science_school"]})

LICENCE_LINES = {
    "scienceuse_nist": "nvlpubs.nist.gov and www.nist.gov: works of NIST (17 U.S.C. 105, checked on govinfo.gov's "
                       "policies page at every build); robots.txt allows the files (checked 2026-11-22).",
    "scienceuse_usgs": "www.usgs.gov/information-policies-and-instructions/copyrights-and-credits (checked at every "
                       "build): most USGS content is in the US public domain; others' pictures are left out.",
    "scienceuse_noaa": "oceanservice.noaa.gov: a work of NOAA (17 U.S.C. 105); robots.txt allows the pages "
                       "(2026-11-22).",
    "scienceuse_nasa": "www.nasa.gov/nasa-brand-center/images-and-media/ (checked at every build): NASA content "
                       "\"generally are not subject to copyright in the United States\"; no endorsement is implied.",
}
NOT_INCLUDED = [
    ("NWS JetStream, the online school for weather", "Public domain (NWS pages are in the public domain), but "
     "JetStream answers programs \"403\" on both weather.gov and noaa.gov (checked again 2026-11-22). Link-only. "
     "Index: https://www.noaa.gov/jetstream"),
    ("PubChem periodic table and element pages", "Public domain data, but pubchem.ncbi.nlm.nih.gov's robots.txt "
     "refuses the periodic table pages to programs (2026-11-22); NIST's periodic table is built. Link-only. Index: "
     "https://pubchem.ncbi.nlm.nih.gov/periodic-table/"),
    ("NOAA education resource collections and climate.gov", "Public domain, but both answered this build machine "
     "\"403\" (2026-11-22). Link-only. Index: https://www.noaa.gov/education/resource-collections and "
     "https://www.climate.gov/"),
    ("NASA Space Place", "Run by NASA's Jet Propulsion Laboratory (Caltech), whose pages carry JPL's own image and "
     "content terms; not checked as public domain. Link-only. Index: https://spaceplace.nasa.gov/"),
    ("SciJinks (NOAA and NASA weather for students)", "Its site did not answer (\"502\", 2026-11-22). Link-only. "
     "Index: https://scijinks.gov/"),
    ("Everyday physics and chemistry open textbooks (OpenStax, LibreTexts)", "OpenStax's physics, chemistry and "
     "astronomy books are already in the library (Textbooks group); LibreTexts is non-commercial for much of its "
     "content. Index: https://openstax.org/subjects/science"),
    ("Wikibooks science explainers (CC BY-SA)", "Already whole in the Kiwix library (wikibooks_en_all). Index: "
     "https://en.wikibooks.org/wiki/Subject:Science"),
    ("NIST Handbook 44 and the other weights-and-measures handbooks", "Already built (reference_more.py: "
     "nist_handbook_44_2025 and others). Index: https://www.nist.gov/pml/owm/publications"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
