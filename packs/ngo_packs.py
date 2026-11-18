"""Pack builders for pictures published openly by NON-PROFIT ORGANISATIONS. Used by build_packs.py in the same way as
its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}. A picture with more than one question comes once with its JPEG and then again as
(None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

The packs (open; checked at the source on 2026-11-18):
  owid_charts   Our World in Data (Global Change Data Lab, a UK charity): its published charts as pictures (the
                PNG every chart page offers), with "What does this chart show?" answered from the chart's own
                record (its title, subtitle, kind of chart and the countries or regions it shows) and "Where does
                the data in this chart come from?" from the chart's own citation, which is printed on the picture.
                Licence: "Unless otherwise stated, you can use, reproduce, and distribute any chart we made (those
                with our logo and CC BY copyright stamp), provided that you cite us" and "Data produced by us falls
                under our permissive CC BY license" (https://ourworldindata.org/faqs); every chart's credit line
                names its page. Charts whose record says they are not published, or which show only a table, are
                left out. robots.txt allows the chart pages and their PNG, config and metadata addresses.

Charts teach a describer to read a graph aloud: its title, what is measured, what kind of chart it is and which
places it compares. Nothing is written by an AI model and nothing is guessed: every answer is built from the
chart's own record. The pictures are charts, without people, so they may be used for picture-making.

Other non-profit picture collections looked at (Gapminder's Dollar Street and the Zooniverse camera-trap releases on
LILA are already packs; the not-open ones and those needing permission are in training-kit/kit/ngo_sources.py).

    python packs/ngo_packs.py owid_charts --limit 8      (prints a few rows: a quick check)
"""

import concurrent.futures
import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, say, considered, pass_random, listing_out_of_time, fetch_all
from food_packs import with_twins, count_pictures

OWID = "https://ourworldindata.org"
OWID_CREDIT = "Our World in Data, CC BY 4.0, {url}"
CHART_Q = "What does this chart show?"
SOURCE_Q = "Where does the data in this chart come from?"
CHART_KINDS = {"LineChart": "line chart", "DiscreteBar": "bar chart", "StackedBar": "stacked bar chart",
               "StackedDiscreteBar": "stacked bar chart", "StackedArea": "stacked area chart",
               "ScatterPlot": "scatter plot", "SlopeChart": "slope chart", "Marimekko": "Marimekko chart",
               "WorldMap": "world map"}


def markdown_text(text):
    """Plain words from a chart's subtitle or note: links and its "#dod:" glossary marks keep only their words."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text or "")
    text = re.sub(r"[*_`]+", "", text)
    return " ".join(text.split())


def place_list(names):
    """"World, Europe and Africa" (at most eight; "and N more" after that)."""
    names = [n for n in names if n]
    if len(names) > 8:
        names = names[:8] + [f"{len(names) - 8} more"]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def chart_kind(config):
    """The kind of picture the chart's PNG shows, in words ("line chart", "world map"), or "" for a table only."""
    if config.get("tab") == "map" or (config.get("hasChartTab") is False and config.get("hasMapTab")):
        return "world map"
    if config.get("tab") == "table":
        return ""
    kinds = config.get("chartTypes") or ([config["type"]] if config.get("type") else ["LineChart"])
    return CHART_KINDS.get(kinds[0], "chart") if kinds else "world map" if config.get("hasMapTab") else ""


def chart_rows(slug, config, metadata):
    """The rows of one chart (see the module docstring), or (None, reason) when it is left out."""
    if config.get("isPublished") is False:
        return None, "the chart is not published"
    title = markdown_text(config.get("title") or (metadata.get("chart") or {}).get("title") or "")
    if not title:
        return None, "the chart has no title"
    kind = chart_kind(config)
    if not kind:
        return None, "the chart shows only a table"
    url = f"{OWID}/grapher/{slug}"
    credit = OWID_CREDIT.format(url=url)
    answer = f'This is a {kind} from Our World in Data titled "{title}".'
    subtitle = markdown_text(config.get("subtitle") or "")
    if subtitle:
        answer += " " + subtitle.rstrip(".") + "."
    places = config.get("selectedEntityNames") or (metadata.get("chart") or {}).get("selection") or []
    if kind != "world map" and places:
        answer += f" It shows {place_list(places)}."
    elif kind == "world map":
        answer += " Each country is coloured by its value; the key says what each colour means."
    rows = [{"question": CHART_Q, "answer": answer, "credit": credit}]
    citation = markdown_text((metadata.get("chart") or {}).get("citation") or config.get("sourceDesc") or "")
    if citation:
        rows.append({"question": SOURCE_Q, "answer": f"The chart names its data source: {citation.rstrip('.')}.",
                     "credit": credit})
    return rows, ""


def owid_slugs(s):
    """The addresses' names (slugs) of every published chart, from the site's sitemap."""
    text = s.get(f"{OWID}/sitemap.xml", timeout=120).text
    return list(dict.fromkeys(re.findall(r"<loc>\s*https://ourworldindata\.org/grapher/([a-z0-9-]+)\s*</loc>", text)))


def build_owid_charts(limit):
    """Our World in Data charts (see the module docstring): about 4,300 charts, a random choice of limit."""
    s = session()
    slugs = owid_slugs(s)
    say(f"  {len(slugs)} charts in the sitemap")
    pass_random(9061).shuffle(slugs)

    def one(slug):
        """(slug, rows or None, reason) of one chart, from its config and metadata."""
        try:
            config = s.get(f"{OWID}/grapher/{slug}.config.json", timeout=60).json()
            metadata = s.get(f"{OWID}/grapher/{slug}.metadata.json", timeout=60).json()
        except Exception as e:  # noqa: BLE001 - left out
            return slug, None, f"its record could not be read ({type(e).__name__})"
        rows, why = chart_rows(slug, config, metadata)
        return slug, rows, why

    items = []
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for start in range(0, len(slugs), 40):
            if len(items) >= limit * 1.1 or listing_out_of_time():
                break
            for slug, rows, why in pool.map(one, slugs[start:start + 40]):
                name = f"owid-{slug}.jpg"
                url = f"{OWID}/grapher/{slug}.png"
                if rows is None:
                    considered(name, url, why)
                    continue
                items.append((name, url, rows))
    return with_twins(fetch_all(items[:int(limit * 1.1)], workers=4)[:limit])


NGO_PACKS = {
    "owid_charts": (build_owid_charts, "Our World in Data (Global Change Data Lab), charts CC BY 4.0, each with its "
                                       "chart page below. https://ourworldindata.org"),
}
NGO_LIMITS = {"owid_charts": 3000}      # of about 4,300 charts; 3 small requests each


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one non-profit pack builder.")
    parser.add_argument("key", choices=sorted(NGO_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = NGO_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
