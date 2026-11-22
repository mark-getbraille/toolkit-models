"""Picture packs for WEATHER MAPS AND FORECAST GRAPHICS from the US National Weather Service (NOAA; public domain,
works of the US government, 17 U.S.C. 105). Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes
once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

The owner's request of 2026-11-21. The answers explain a map from what is KNOWN about it, never from a reading of the
picture: the product (which map it is and who makes it), its time (from the archive's file name), the legend that
every map of that product uses (from NOAA's own product descriptions), and, for hurricane graphics, the summary that
the National Hurricane Center's public advisory of the same number gives in words. Where a front or a storm is on the
map is never said unless the advisory says it.

The packs:
  wpc_surface_maps    The Weather Prediction Center's surface analysis archive (wpc.ncep.noaa.gov/archives/sfc,
                      no robots.txt; checked 2026-11-21): the US analysis with station reports, the fronts-only US
                      and North America analyses, the analysis over a satellite picture and the analysis over the
                      radar composite (rain and snow echoes), at a random time between 2012 and 2025.
                      "What does this weather map show?" and "What time is this weather map for?"
  nhc_forecast_cones  The National Hurricane Center's archive of forecast cone graphics (nhc.noaa.gov, whose
                      robots.txt allows all), Atlantic and eastern Pacific storms of 2018 to 2024: the five-day cone
                      with its track line and the current wind field, with the storm's name and advisory number, the
                      advisory's own summary (location, strongest winds, movement, pressure) and the legend.

Not built (in the kit's picture_reading_sources.py): the Storm Prediction Center (robots.txt disallows every robot),
radar.weather.gov (no archive) and the raw radar files on AWS (not pictures).

    python packs/weather_map_packs.py wpc_surface_maps --limit 4      (prints a few rows: a quick check)
"""

import datetime
import json
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, fetch_all, pass_random
from food_packs import with_twins

MAP_SHOWS = "What does this weather map show?"
MAP_TIME = "What time is this weather map for?"
DESCRIBE = "Describe this picture."
NOT_READ = ("This explanation comes from the kind of map and its time, not from reading this particular map.")

# ----------------------------------------------------------------- WPC surface analysis archive

WPC_ARCHIVE = "https://www.wpc.ncep.noaa.gov/archives/sfc"
WPC_PAGE = "https://www.wpc.ncep.noaa.gov/archives/web_pages/sfc/sfc_archive.php"
FRONTS = ("Fronts are drawn as lines: a cold front is blue with triangles, a warm front red with half circles, an "
          "occluded front purple with both, and a stationary front alternates red half circles and blue triangles; "
          "a dashed line is a trough. H marks a centre of high pressure and L a centre of low pressure, with its "
          "pressure in millibars, and the thin curved lines (isobars) join places with the same air pressure.")
STATIONS = ("The small circles with numbers around them are weather station reports: the temperature at the upper "
            "left and the dew point at the lower left, in degrees Fahrenheit, and a line with barbs showing where "
            "the wind blows from and how strong it is.")
# map type in the archive: (what the map is, what it adds to the fronts)
WPC_MAPS = {
    "namussfc": ("the Weather Prediction Center's surface analysis of the United States, with weather station "
                 "reports", STATIONS),
    "usfntsfc": ("the Weather Prediction Center's surface analysis of the United States, fronts and pressure only",
                 ""),
    "namfntsfc": ("the Weather Prediction Center's surface analysis of North America, fronts and pressure only", ""),
    "ussatsfc": ("the Weather Prediction Center's surface analysis of the United States drawn over a satellite "
                 "picture", "Under the analysis is an infrared satellite picture: the brighter the cloud, the colder "
                        "and higher its top."),
    "radsfcus_exp": ("the Weather Prediction Center's surface analysis of the United States drawn over the national "
                     "radar composite", "The coloured patches are radar echoes of rain, snow or hail, coloured by "
                                       "strength (reflectivity in dBZ) on the scale at the left: blue and green for "
                                       "light, yellow and orange for moderate, red and purple for heavy."),
}
WPC_YEARS = (2012, 2025)
WPC_HOURS = (0, 6, 12, 18)


def wpc_time_words(when):
    """"12:00 UTC on Monday 1 January 2024" for a datetime."""
    return f"{when:%H}:00 UTC on {when:%A} {when.day} {when:%B %Y}"


def wpc_rows(kind, when):
    """The rows of one WPC map: what it shows and its legend, and its time."""
    what, more = WPC_MAPS[kind]
    stamp = wpc_time_words(when)
    shows = f"This is {what}, for {stamp}, from the National Weather Service's archive. {FRONTS}"
    if more:
        shows += f" {more}"
    credit = (f"NOAA/NWS Weather Prediction Center, surface analysis archive ({WPC_PAGE}), {kind} for {stamp}, "
              f"public domain (work of the US government)")
    return [{"question": MAP_SHOWS, "answer": f"{shows} {NOT_READ}", "credit": credit},
            {"question": MAP_TIME, "answer": f"It is the surface analysis for {stamp}.", "credit": credit}]


def wpc_items(want, seed="wpc"):
    """(name, address, rows) for want maps: the map types take turns, each at a random 6-hourly time."""
    rnd = pass_random(seed)
    start = datetime.datetime(WPC_YEARS[0], 1, 1)
    days = (datetime.datetime(WPC_YEARS[1], 12, 31) - start).days
    items, seen = [], set()
    kinds = list(WPC_MAPS)
    while len(items) < want:
        kind = kinds[len(items) % len(kinds)]
        when = start + datetime.timedelta(days=rnd.randrange(days), hours=rnd.choice(WPC_HOURS))
        stamp = f"{when:%Y%m%d%H}"
        if (kind, stamp) in seen:
            continue
        seen.add((kind, stamp))
        items.append((f"wpc-{kind}-{stamp}.jpg", f"{WPC_ARCHIVE}/{when:%Y}/{kind}{stamp}.gif", wpc_rows(kind, when)))
    return items


def build_wpc_surface_maps(limit):
    """The wpc_surface_maps pack: one archived map per request, a second apart (a missing map is skipped)."""
    items = wpc_items(int(limit * 1.1) + 4)
    return with_twins(fetch_all(items, workers=1, pause=1.0)[:limit])


# ----------------------------------------------------------------- NHC forecast cone archive

NHC = "https://www.nhc.noaa.gov/archive"
NHC_YEARS = range(2018, 2025)
CONE = "5day_cone_with_line_and_wind"
CONE_LEGEND = ("The white area (days 1 to 3) and the dotted area (days 4 and 5) together are the cone: the probable "
               "path of the storm's centre, not its size; hazards can reach well outside it. The black line and dots "
               "are the forecast track and positions, lettered by strength (D: tropical depression, S: tropical "
               "storm, H: hurricane, M: major hurricane). Coloured lines along the coast are watches and warnings: "
               "red for a hurricane warning, pink for a hurricane watch, blue for a tropical storm warning and "
               "yellow for a tropical storm watch. The orange area around the centre is where tropical-storm-force "
               "winds are blowing now, and the brown area hurricane-force winds.")
ADVISORY_TITLE = re.compile(r"((?:Post-|Potential )?(?:Tropical|Subtropical|Hurricane|Major|Remnants)[\w -]*?)\s+"
                            r"Advisory Number\s+(\d+)", re.I)
SUMMARY_LINES = re.compile(r"^(LOCATION|ABOUT|MAXIMUM SUSTAINED WINDS|PRESENT MOVEMENT|MINIMUM CENTRAL PRESSURE)"
                           r"(?:\.\.\.|\s)(.+)$", re.M)
COMPASS = {"N": "north", "NNE": "north-north-east", "NE": "north-east", "ENE": "east-north-east", "E": "east",
           "ESE": "east-south-east", "SE": "south-east", "SSE": "south-south-east", "S": "south",
           "SSW": "south-south-west", "SW": "south-west", "WSW": "west-south-west", "W": "west",
           "WNW": "west-north-west", "NW": "north-west", "NNW": "north-north-west"}


def plain_units(value):
    """"65 MPH...100 KM/H" -> "65 mph (100 km/h)"; "10 MI...15 KM" -> "10 miles (15 km)"."""
    value = re.sub(r"(\d[\d.]*) MPH\.\.\.(\d[\d.]*) KM/H", r"\1 mph (\2 km/h)", value)
    value = re.sub(r"(\d[\d.]*) MI\.\.\.(\d[\d.]*) KM", r"\1 miles (\2 km)", value)
    value = re.sub(r"(\d[\d.]*) MB\.\.\.(\d[\d.]*) INCHES", r"\1 mb (\2 inches)", value)
    return value


def advisory_summary(text):
    """(storm and advisory heading, [summary lines in plain words]) from a public advisory's text, or ("", [])."""
    text = re.sub(r"<[^>]+>", "", text or "")
    head = ADVISORY_TITLE.search(text)
    block = text.split("SUMMARY OF", 1)[-1].split("WATCHES AND WARNINGS", 1)[0] if "SUMMARY OF" in text else ""
    lines = []
    for field, value in SUMMARY_LINES.findall(block):
        value = plain_units(clean(value))
        if field == "LOCATION":
            m = re.match(r"([\d.]+)([NS])\s+([\d.]+)([EW])$", value)
            if m:
                value = (f"{m.group(1)} degrees {'north' if m.group(2) == 'N' else 'south'}, {m.group(3)} degrees "
                         f"{'west' if m.group(4) == 'W' else 'east'}")
            lines.append(f"the centre is at {value}")
        elif field == "ABOUT":
            value = re.sub(r"\b(NNE|NE|ENE|ESE|SE|SSE|SSW|SW|WSW|WNW|NW|NNW|N|E|S|W)\b(?= OF)",
                           lambda m: COMPASS[m.group(1)], value)
            value = value.replace("...", ", ")
            near, _, place = value.partition(" OF ")
            place = re.sub(r"\b(Of|The|And|In|On|At)\b", lambda m: m.group(1).lower(), place.title())
            lines.append(f"about {near.lower()} of {place}" if place else f"about {value.lower()}")
        elif field == "PRESENT MOVEMENT":
            m = re.match(r"([NSEW]{1,3}) OR (\d+) DEGREES AT (.+)$", value)
            value = f"{COMPASS.get(m.group(1), m.group(1))} ({m.group(2)} degrees) at {m.group(3)}" if m else value
            lines.append(f"it is moving {value.lower()}" if not value.upper().startswith("STATIONARY")
                         else "it is nearly stationary")
        elif field == "MAXIMUM SUSTAINED WINDS":
            lines.append(f"its strongest sustained winds are {value.lower()}")
        else:
            lines.append(f"its lowest central pressure is {value.lower()}")
    heading = re.sub(r"\s+", " ", head.group(0)).strip() if head else ""
    return heading, lines


def storm_list(s, year):
    """[(storm id like "AL102023", name, classification)] from the NHC archive's page for a year."""
    page = s.get(f"{NHC}/{year}/", timeout=60).text
    out = []
    for basin, number, name_page, title in re.findall(
            r"atcf_index=(al|ep)(\d\d)\s*-->\s*<a href=\"(\w+)\.shtml\?\">([^<]+)</a>", page):
        out.append((f"{basin.upper()}{number}{year}", name_page, clean(title)))
    return out


def cone_rows(storm_id, title, advisory, summary_text, year):
    """The rows of one cone graphic."""
    heading, lines = advisory_summary(summary_text)
    name = heading.split(" Advisory")[0] if heading else title.title()
    basin = "Atlantic" if storm_id.startswith("AL") else "eastern Pacific"
    page = f"{NHC}/{year}/{storm_id[:4].lower()}/{storm_id.lower()}.public.{int(advisory):03d}.shtml"
    credit = (f"NOAA/NWS National Hurricane Center, {name} advisory {advisory} ({year} {basin} season), forecast "
              f"cone graphic and public advisory ({page}), public domain (work of the US government)")
    about = (f"This is the National Hurricane Center's five-day forecast cone graphic for {name}, advisory "
             f"{advisory}, in the {year} {basin} hurricane season.")
    if lines:
        about += " The advisory says " + "; ".join(lines) + "."
    about += f" {CONE_LEGEND}"
    rows = [{"question": MAP_SHOWS, "answer": about, "credit": credit}]
    if lines:
        rows.append({"question": "Where is the storm and how strong is it?",
                     "answer": f"According to advisory {advisory}, " + "; ".join(lines) + ".", "credit": credit})
    return rows


def build_nhc_forecast_cones(limit):
    """The nhc_forecast_cones pack: storms of the chosen years in a fixed random order, at most two advisories of
    each (full-numbered ones, whose public advisory gives the summary), one request a second."""
    s, items = session(), []
    storms = []
    for year in NHC_YEARS:
        try:
            storms += [(year, *x) for x in storm_list(s, year)]
        except Exception as error:  # noqa: BLE001 - one year down does not stop the pack
            say(f"NHC {year}: left out ({error})")
        time.sleep(1)
    pass_random("nhc").shuffle(storms)
    say(f"NHC: {len(storms)} storms")
    for year, storm_id, name_page, title in storms:
        if len(items) >= limit * 1.1 + 2:
            break
        try:
            page = s.get(f"{NHC}/{year}/{name_page}_graphics.php", params={"product": CONE}, timeout=60).text
        except Exception:  # noqa: BLE001 - the next storm
            continue
        time.sleep(1)
        numbers = re.findall(rf"graphics/{storm_id}/{storm_id}_{CONE}_(\d+)\.png", page)
        if not numbers:
            continue
        for advisory in random.Random(storm_id).sample(numbers, min(2, len(numbers))):
            url = f"{NHC}/{year}/{storm_id[:4].lower()}/{storm_id.lower()}.public.{int(advisory):03d}.shtml"
            try:
                text = s.get(url, timeout=60).text
            except Exception:  # noqa: BLE001 - the graphic is still kept, without the summary
                text = ""
            time.sleep(1)
            items.append((f"nhc-{storm_id}-{advisory}.jpg",
                          f"{NHC}/{year}/graphics/{storm_id}/{storm_id}_{CONE}_{advisory}.png",
                          cone_rows(storm_id, title, advisory, text, year)))
    return with_twins(fetch_all(items, workers=1, pause=1.0)[:limit])


# ----------------------------------------------------------------- the packs

WEATHER_MAP_PACKS = {
    "wpc_surface_maps": (build_wpc_surface_maps, "NOAA/National Weather Service, Weather Prediction Center, surface "
                                                 f"analysis archive ({WPC_PAGE}): public domain, works of the US "
                                                 "government (17 U.S.C. 105). Each map credited below."),
    "nhc_forecast_cones": (build_nhc_forecast_cones, "NOAA/National Weather Service, National Hurricane Center "
                                                     "archive (https://www.nhc.noaa.gov/archive/): forecast cone "
                                                     "graphics and public advisories, public domain, works of the "
                                                     "US government (17 U.S.C. 105). Each graphic credited below."),
}
WEATHER_MAP_LIMITS = {"wpc_surface_maps": 1200, "nhc_forecast_cones": 400}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one weather map pack builder.")
    parser.add_argument("key", choices=sorted(WEATHER_MAP_PACKS))
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args(argv)
    entries = WEATHER_MAP_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
