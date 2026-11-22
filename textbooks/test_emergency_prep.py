"""Self-test of the emergency preparedness books (emergency_prep.py), with MADE-UP data only: nothing is downloaded.

It checks that the four books are registered, the weather radio data file becomes one table per state with the SAME
code, frequency and part of the county in words, a changed weather.gov disclaimer stops the build, and Ready.gov and
FEMA are said as not read with their index addresses.

Run it from the repository's folder:   python3 -m pytest textbooks/test_emergency_prep.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import emergency_prep as E  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

CCL = '''var ST = [];
ST[0] = "VT";\nSTATE[0] = "Vermont";\nCOUNTY[0] = "Madeup";\nSAME[0] = "050999";\nSITENAME[0] = "Hilltop";
SITELOC[0] = "Hill";\nSITESTATE[0] = "VT";\nFREQ[0] = "162.475";\nCALLSIGN[0] = "WXX99";\nPWR[0] = "1000";
STATUS[0] = "NORMAL";\nWFO[0] = "Burlington|VT";\nREMARKS[0] = "C|E";
'''


def test_registered():
    assert sources.expand_keys(["preparedness"]) == ["prep:nws_safety", "prep:nwr_guide", "prep:nwr_stations",
                                                     "prep:fema_are_you_ready"]
    assert E.ARE_YOU_READY["archive"] and E.ARE_YOU_READY["published"] == "2004-08"
    assert re.match(E.GUIDES[0]["pages"], "https://www.weather.gov/safety/heat-hazards")
    assert not re.match(E.GUIDES[1]["pages"], "https://www.weather.gov/nwr/county_coverage")
    assert any("ready.gov" in r and "Index: https://" in r for _t, r in E.NOT_INCLUDED)


def test_station_book(monkeypatch):
    answers = {E.NWS_LICENCE: "<p>The information on National Weather Service (NWS) Web pages are in the public "
                              "domain, unless</p>", E.CCL: CCL}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: answers[url])
    monkeypatch.setattr(K, "last_modified", lambda url: "2026-11-20")
    book = E.stations_book("nwr_stations", "/tmp/none", None, [])
    page = book.pages[1]
    assert page.title == "Weather radio in Vermont"
    assert "<td>050999</td><td>central part, east</td><td>Hilltop (Hill, VT)</td><td>WXX99</td><td>162.475</td>" \
        in page.body
    assert book.published == "2026-11-20" and book.licence == K.US_GOV and "911" in book.notice
    answers[E.NWS_LICENCE] = "Copyright"
    left = []
    assert E.stations_book("nwr_stations", "/tmp/none", None, left) is None and left
