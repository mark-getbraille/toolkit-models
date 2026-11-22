"""Emergency preparedness for the reference library (the owner's request of 2026-11-22). Keys: preparedness (every
book), prep:<name>.

What this module builds, in plain words, each IN FULL:
  - the National Weather Service's weather safety pages (weather.gov/safety: heat, cold and winter storms, floods,
    hurricanes, tornadoes, thunderstorms and lightning, wildfire, rip currents and the beach, tsunamis, fog, drought,
    wind and dust, air quality, space weather, and preparedness), every page;
  - the NOAA Weather Radio All Hazards pages (what it is, SAME county codes, receivers, reception, the special needs
    page for deaf and hard of hearing people, frequently asked questions);
  - the NOAA Weather Radio station and frequency list by county: one page per state (and territory) with a table of
    every county or part of a county, its SAME code (the 6-digit code you program into a weather radio), the
    station that covers it, its call sign, frequency, power and status, made from the data file weather.gov's own
    county coverage pages use (www.weather.gov/source/nwr/JS/CCL.js);
  - FEMA's "Are You Ready? An In-depth Guide to Citizen Preparedness" (IS-22, August 2004), the whole guide, from the
    Internet Archive's copy (fema.gov and ready.gov refuse programs).

Licence: weather.gov/disclaimer (checked at every build): "The information on National Weather Service (NWS) Web
pages are in the public domain, unless specifically noted otherwise, and may be used without charge for any lawful
purpose"; FEMA's guide is a work of the US government (public domain). weather.gov has no robots.txt rules
(checked 2026-11-22); archive.org's robots.txt allows the files.

The station list is read again by the weekly check when the data file changes (a station out of service, a new
frequency).

Run from the repository's folder:
  python3 textbooks/emergency_prep.py prep:nwr_stations --out build/textbooks
  python3 textbooks/emergency_prep.py prep:nws_safety --out build/textbooks --limit 5
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"                          # "Reference, health and safety"
NWS = "https://www.weather.gov"
NWS_LICENCE = f"{NWS}/disclaimer"
NWS_TEXT = r"National Weather Service \(NWS\) Web pages are in the public domain"
CCL = f"{NWS}/source/nwr/JS/CCL.js"
NWS_NOTICE = ("From the National Weather Service (NOAA), whose web pages are in the public domain. For warnings now, "
              "listen to NOAA Weather Radio, local radio and TV, or your phone's Wireless Emergency Alerts; in danger, "
              "call 911.")
NWS_CONTENT = (r'<div class="cms-content">', r'<!-- end of <div class="partial-width-borderbottom"> -->|'
                                             r'<div class="footer">')

GUIDES = [
    K.us_web(GROUP, name="nws_safety", title="Weather safety (National Weather Service)",
             subject="Weather safety and preparedness", publisher="National Weather Service (NOAA)",
             source=f"{NWS}/safety/", licence_page=NWS_LICENCE, licence_text=NWS_TEXT, notice=NWS_NOTICE,
             description="Every weather safety page of the National Weather Service: how to prepare for, stay safe "
                         "during and recover from heat, cold and winter storms, floods, hurricanes, tornadoes, "
                         "thunderstorms and lightning, wildfires, rip currents and the beach, tsunamis, fog, drought, "
                         "wind and dust storms, poor air quality and space weather, with the warnings each hazard "
                         "has.",
             crawl=[(f"{NWS}/safety", 1)], pages=r"^https://www\.weather\.gov/safety/[a-z0-9-]+$",
             content=NWS_CONTENT,
             unit_rules=[(r"/safety/heat", "Heat"), (r"/safety/(cold|winter)", "Cold and winter"),
                         (r"/safety/flood", "Floods"), (r"/safety/hurricane", "Hurricanes"),
                         (r"/safety/tornado", "Tornadoes"), (r"/safety/(thunderstorm|lightning)",
                                                             "Thunderstorms and lightning"),
                         (r"/safety/wildfire|/safety/fire", "Wildfires"),
                         (r"/safety/(beach|ripcurrent)", "Rip currents and the beach"),
                         (r"/safety/tsunami", "Tsunamis"), (r"/safety/(wind|dust)", "Wind and dust"),
                         (r".", "Other hazards and preparedness")],
             limit=120),
    K.us_web(GROUP, name="nwr_guide", title="NOAA Weather Radio All Hazards: how it works",
             subject="Weather radio", publisher="National Weather Service (NOAA)", source=f"{NWS}/nwr/",
             licence_page=NWS_LICENCE, licence_text=NWS_TEXT, notice=NWS_NOTICE,
             description="The NOAA Weather Radio All Hazards pages: what the network is, the alerts it broadcasts, "
                         "Specific Area Message Encoding (SAME) and how to program a receiver with your county's "
                         "code, choosing a receiver, reception, the special needs page (receivers for people who are "
                         "deaf, hard of hearing or blind), the Emergency Alert System, tsunami alerting and the "
                         "frequently asked questions.",
             crawl=[(f"{NWS}/nwr", 1)],
             pages=r"^https://www\.weather\.gov/nwr/(?!county_coverage|counties|station_search|Maps|outages|"
                   r"nwr_outage_report|sites|station_listing)[A-Za-z_]+$",
             content=NWS_CONTENT, limit=40),
]

ARE_YOU_READY = K.us_pdf(
    GROUP, name="fema_are_you_ready", title="Are You Ready? An In-depth Guide to Citizen Preparedness (FEMA IS-22, "
    "2004)", subject="Emergency preparedness", publisher="Federal Emergency Management Agency (FEMA)",
    description="FEMA's whole guide to citizen preparedness: getting informed, making a plan, assembling a disaster "
                "supplies kit, shelter, hazard-specific preparedness (floods, tornadoes, hurricanes, thunderstorms, "
                "winter storms, extreme heat, earthquakes, volcanoes, landslides, tsunamis, fires, wildfires), "
                "technological and accidental hazards (hazardous materials, household chemicals, nuclear power "
                "plants), terrorism, and recovering from disaster.",
    published="2004-08", version="IS-22, August 2004 (Internet Archive item FemaEmergencyHandbook-areYouReady)",
    archive="FemaEmergencyHandbook-areYouReady", pdf_licence_text=r"Are You Ready\?",
    notice="A work of the Federal Emergency Management Agency (not under copyright in the United States). This is the "
           "2004 edition; Ready.gov has newer advice and phone numbers may have changed.")


# ====================================================================== the weather radio stations

FIELDS = ("ST", "STATE", "COUNTY", "SAME", "SITENAME", "SITELOC", "SITESTATE", "FREQ", "CALLSIGN", "PWR", "STATUS",
          "WFO", "REMARKS")


def ccl_rows(text):
    """The rows of CCL.js ([{field: value}]) from its lines like SAME[12] = "002013";."""
    rows = {}
    for field, n, value in re.findall(r'^([A-Z]+)\[(\d+)\]\s*=\s*"(.*?)";', text, re.M):
        if field in FIELDS:
            rows.setdefault(int(n), {})[field] = value
    return [rows[n] for n in sorted(rows)]


REMARKS = {"C": "central part", "N": "north", "S": "south", "E": "east", "W": "west", "NE": "northeast",
           "NW": "northwest", "SE": "southeast", "SW": "southwest", "CENTRAL": "central part"}


def remark_words(code):
    """"C|E" -> "central part, east" (the part of the county a station covers); "" for the whole county."""
    return ", ".join(REMARKS.get(p.strip().upper(), p.strip()) for p in (code or "").split("|") if p.strip())


def stations_book(name, work, cache=None, left_out=None, limit=None):
    """The station and frequency list by state and county."""
    import build_textbooks as B
    if not re.search(NWS_TEXT, " ".join(re.sub(r"<[^>]+>", " ", B.fetch(NWS_LICENCE, cache)).split())):
        left_out.append({"title": name, "reason": "weather.gov's disclaimer no longer says public domain."})
        return None
    rows = ccl_rows(B.fetch(CCL, None))
    book = K.new_book("prep_nwr_stations", "NOAA Weather Radio stations and frequencies by county",
                      "Weather radio stations (by county)", GROUP, "National Weather Service (NOAA)", K.US_GOV,
                      K.US_GOV_URL, f"{NWS}/nwr/counties",
                      "Every county (or part of a county) covered by NOAA Weather Radio All Hazards, one page per "
                      "state and territory: the county's SAME code to program into a weather radio, and each station "
                      "that covers it with its call sign, frequency, transmitter power, the part of the county it "
                      "reaches and whether it is on the air.", NWS_NOTICE,
                      changes="the county coverage data made into one table per state")
    book.version = f"county coverage data read {__import__('datetime').date.today().isoformat()}"
    book.published = K.last_modified(CCL)
    book.originals.append({"url": CCL, "kind": "txt"})
    book.pages.append(B.Page("how-to-use", "How to use this list",
                             "<p>Find your state, then your county. Program the 6-digit SAME code into a weather "
                             "radio that has SAME, and tune it to the frequency of a station that covers your "
                             "county (the weather radio band is 162.400 to 162.550 MHz). If several stations cover "
                             "your county, choose the one you hear best. A status other than \"NORMAL\" means the "
                             "station was degraded or off the air when this list was made.</p>", 0, "About"))
    states = {}
    for r in rows:
        states.setdefault(r.get("STATE") or r.get("ST", ""), []).append(r)
    for state in sorted(states):
        if limit and len(book.pages) > limit:
            break
        table = [(r.get("COUNTY", ""), r.get("SAME", ""), remark_words(r.get("REMARKS")) or "whole county",
                  f"{r.get('SITENAME', '')} ({r.get('SITELOC', '')}, {r.get('SITESTATE', '')})".replace(" (, )", ""),
                  r.get("CALLSIGN", ""), r.get("FREQ", ""), r.get("PWR", ""), r.get("STATUS", "").title(),
                  r.get("WFO", "").replace("|", ", "))
                 for r in sorted(states[state], key=lambda r: (r.get("COUNTY", ""), r.get("FREQ", "")))]
        body = K.rows_table(table, ("County", "SAME code", "Part covered", "Station (transmitter site)",
                                    "Call sign", "Frequency (MHz)", "Power (watts)", "Status",
                                    "Weather Service office"))
        book.pages.append(B.Page(B.slug(state, 40), f"Weather radio in {state}", body, 0, "States and territories"))
    return book


def stations_sign(name):
    """The station list's sign: the data file's server date and size."""
    import updates
    return K.sha(updates.head_signs(CCL))


COLLECTION = K.Collection("prep", GROUP, guides=GUIDES, pdfs=[ARE_YOU_READY],
                          makers={"nwr_stations": (stations_book, stations_sign)},
                          words={"preparedness": lambda: ["prep:nws_safety", "prep:nwr_guide", "prep:nwr_stations",
                                                          "prep:fema_are_you_ready"]})

GROUPS = {}
LICENCE_LINES = {
    "nws_public_domain": "weather.gov/disclaimer (checked at every build): \"The information on National Weather "
                         "Service (NWS) Web pages are in the public domain, unless specifically noted otherwise, and "
                         "may be used without charge for any lawful purpose so long as it is not presented in a way "
                         "that implies an endorsement\". www.weather.gov has no robots.txt (404: no rules), checked "
                         "2026-11-22.",
    "fema_are_you_ready_archive": "FEMA IS-22 (2004): a work of the US government; the Internet Archive item "
                                  "FemaEmergencyHandbook-areYouReady (creator FEMA, marked public domain) is read "
                                  "because fema.gov and ready.gov refuse programs; archive.org's robots.txt allows it.",
}
NOT_INCLUDED = [
    ("Ready.gov guides and FEMA's current publications (fema.gov)", "Public domain, but www.ready.gov and www.fema.gov "
     "answer programs \"Access Denied\" (robots.txt included, checked 2026-11-22). The 2004 \"Are You Ready?\" guide "
     "is built from the Internet Archive instead (prep:fema_are_you_ready); the Kiwix library also has Ready.gov. "
     "Index: https://www.ready.gov/ and https://www.fema.gov/emergency-managers/risk-management/building-science/"
     "publications"),
    ("Other FEMA publications on the Internet Archive", "The other FEMA items found there are lending-library scans "
     "(\"printdisabled\", borrow only) or research papers about FEMA, not FEMA's own guides; not built. Index: "
     "https://archive.org/search?query=creator%3AFEMA"),
    ("NWS JetStream weather school", "Said already: its pages refuse programs (403). Index: "
     "https://www.noaa.gov/jetstream"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
