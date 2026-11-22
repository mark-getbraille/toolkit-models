"""The collection "Telescopes, microscopes and home weather stations (manuals)" (category key science_instruments):
the owner's request of 2026-11-22 for science you can use. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (telescopes and their mounts,
            microscopes, home weather stations, barometers, anemometers, rain gauges, planetarium projectors);
  makers    the telescope, microscope and weather station makers: LINK-ONLY by the owner's rule;
  guidance  the reference library's science books (textbooks/science_use.py: NASA Skywatching, NIST units, NOAA and
            USGS).

The safety notice is said first: never look at the Sun through a telescope or binoculars without a proper solar
filter.
"""

NOTICE = 'Read the safety section first. Never point a telescope, binoculars or a finder at the Sun without a certified solar filter over the front: it blinds instantly. Mount outdoor weather sensors away from power lines, and never on a roof in a storm.'

IA_WORDS = ["telescope", "equatorial mount", "goto mount", "microscope", "weather station", "barometer", "anemometer", "rain gauge", "planetarium", "star projector"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="science_instruments", prefix="sc", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="celestron", maker="Celestron", type="telescopes and microscopes", library="https://www.celestron.com/pages/manuals-software", site="celestron.com"),
    dict(key="meade", maker="Meade Instruments", type="telescopes", library="https://www.meade.com/", site="meade.com"),
    dict(key="sky-watcher", maker="Sky-Watcher", type="telescopes and mounts", library="https://www.skywatcherusa.com/", site="skywatcherusa.com"),
    dict(key="ambient-weather", maker="Ambient Weather", type="home weather stations", library="https://ambientweather.com/", site="ambientweather.com"),
    dict(key="davis", maker="Davis Instruments", type="weather stations", library="https://www.davisinstruments.com/", site="davisinstruments.com"),
    dict(key="la-crosse", maker="La Crosse Technology", type="weather stations and clocks", library="https://www.lacrossetechnology.com/", site="lacrossetechnology.com"),
    dict(key="amscope", maker="AmScope", type="microscopes", library="https://amscope.com/", site="amscope.com"),
]]

GUIDANCE = [
    dict(title="Skywatching (NASA; in the reference library: science:nasa_skywatching)",
         url="https://science.nasa.gov/skywatching/", by="NASA"),
    dict(title="Unit conversion (NIST; in the reference library: science:nist_unit_conversion)",
         url="https://www.nist.gov/pml/owm/metric-si/unit-conversion", by="the National Institute of Standards and Technology"),
    dict(title="Citizen weather observers (NOAA CoCoRaHS and CWOP pages; open them in a browser)",
         url="https://www.cocorahs.org/", by="CoCoRaHS"),
]

CATEGORY = dict(
    name='Telescopes, microscopes and home weather stations (manuals)',
    description="Telescopes and their mounts, microscopes, home weather stations, barometers, anemometers, rain gauges and planetarium projectors: the Internet Archive's manuals, the makers' manual pages (links) and the reference library's science books. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
