"""Picture packs for CHARTS, DIAGRAMS AND INFOGRAPHICS WITH EXPLANATIONS: textbook figures with the alt text their
authors wrote for screen-reader users, and Wikimedia Commons charts with their own descriptions. Used by build_packs.py
in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None,
row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the
same picture. The limit counts pictures.

The owner's request of 2026-11-21. Every answer that explains a chart is the source's own text (the figure's alt text,
its title and caption, or the Commons file's caption or description); the kind of chart comes from the Commons
category. No value is ever read off a chart by a program.

The packs:
  openstax_figures  OpenStax textbooks (Rice University): Principles of Economics 3e, Introductory Statistics 2e,
                    Biology 2e, Chemistry 2e, College Physics 2e and Astronomy 2e. Each figure's alt text, written by
                    OpenStax for screen-reader users ("Describe this picture."), and its title and caption ("What
                    does this figure show?"). OpenStax changed its books to CC BY-NC-SA in March and April 2026, and
                    openstax.org's robots.txt keeps programs out of the book files; so the books are read from their
                    own GitHub repositories (github.com/openstax/osbooks-...) at the last version before each
                    book's licence change, which OpenStax published under CC BY 4.0 (OPENSTAX_BOOKS names each
                    version; the builder checks the licence written in that version). Only figures OpenStax drew
                    itself (no credit line) or whose credit names a US government source or states CC BY, CC0 or
                    public domain (body_packs.openstax_credit_free); only drawn figures (no credit at all) or
                    figures whose words say graph, chart, diagram, map, illustration and the like; nothing about
                    reproduction, nudity or childbirth.
  commons_charts    Wikimedia Commons (CC0, public domain or CC BY files only): pie, bar, line and area charts,
                    histograms, Venn diagrams, population pyramids, organisation charts and timelines, each only
                    when its file has an English caption or description of eight words or more: "What kind of chart
                    is this?" -> "This is a pie chart." and "What does this chart show?" -> its own description.

Already in the kit, not repeated: plotqa (text_packs.py), owid_charts (ngo_packs.py), the anatomy pack's OpenStax
Anatomy and Physiology figures (body_packs.py), and for personal use chartqa, ai2d, scienceqa and dvqa. TQA (CC BY-NC)
is a personal-use entry in the kit's picture_reading_sources.py, with what was left out (SciCap and others).

    python packs/chart_packs.py openstax_figures --limit 6      (prints a few rows: a quick check)
"""

import html
import json
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, fetch_all
from food_packs import with_twins, sentence
from body_packs import openstax_credit_free
from described_commons import build_described

DESCRIBE = "Describe this picture."
FIGURE_SHOWS = "What does this figure show?"
CHART_KIND = "What kind of chart is this?"
CHART_SHOWS = "What does this chart show?"

# ----------------------------------------------------------------- OpenStax figures (GitHub, CC BY 4.0 versions)

OPENSTAX_RAW = "https://raw.githubusercontent.com/openstax"
# (repository, the last commit before the book's licence was changed to CC BY-NC-SA, book, book's name)
OPENSTAX_BOOKS = [
    ("osbooks-principles-economics-bundle", "020e54dbecb376f27b37c3498f9347a45961c11a", "principles-economics-3e",
     "Principles of Economics 3e"),
    ("osbooks-introductory-statistics-bundle", "50ec91749080bb040b57bb40c34337cacc994cba",
     "introductory-statistics-2e", "Introductory Statistics 2e"),
    ("osbooks-biology-bundle", "d2779c2edfb435e75047325434fe2fe93d5aa120", "biology-2e", "Biology 2e"),
    ("osbooks-chemistry-bundle", "32c719622fbb7a0ca729cd645c1df4cf4e7d5b3a", "chemistry-2e", "Chemistry 2e"),
    ("osbooks-college-physics-bundle", "f98d7a792138a6133fe7267d17e70aa04e9ccbed", "college-physics-2e",
     "College Physics 2e"),
    ("osbooks-astronomy", "63157f370b09c06a4cc12832384aaaf4de1ced3b", "astronomy-2e", "Astronomy 2e"),
]
CC_BY_4 = re.compile(r'license url="https?://creativecommons\.org/licenses/by/4\.0/?"')
# Words that make a figure a chart, diagram or drawing (photos have a credit line and none of these words).
CHART_WORDS = re.compile(r"\b(graphs?|charts?|diagrams?|plots?|histograms?|curves?|maps?|illustrat\w*|drawings?|"
                         r"models?|cycles?|timelines?|flow ?charts?|axis|axes|schematic|tables?|"
                         r"structures?|cross[- ]sections?)\b", re.I)
NOT_SHOWN = re.compile(r"\b(nud\w*|naked|sex\w*|genital\w*|penis|vagina\w*|vulva|uter\w*|testes|testicle\w*|"
                       r"intercourse|childbirth|breast\w*|fetus\w*|foetus\w*|embryo\w*|ovar\w*|sperm\w*|"
                       r"menstrua\w*|pregnan\w*|reproduct\w*|corpse\w*|dead body|autops\w*)\b", re.I)


def strip_markup(text):
    """CNXML text without its tags (emphasis, links, sub- and superscripts), entities read, spaces tidied."""
    text = re.sub(r"<sub>(.*?)</sub>", r"\1", text or "", flags=re.S)
    text = re.sub(r"<sup>(.*?)</sup>", r"^\1", text, flags=re.S)
    text = re.sub(r"<link\b[^>]*/>", "", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = clean(html.unescape(text))
    return re.sub(r"\s+([,.;:)])", r"\1", text)


def cnxml_figures(cnxml):
    """[(id, title, caption, credit, alt text, media file)] for the one-picture figures of a CNXML module. The
    credit is cut from the end of the caption ("(credit: modification of work by NASA)")."""
    out = []
    for fid, block in re.findall(r'<figure\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</figure>', cnxml, re.S):
        images = re.findall(r'<image\b[^>]*\bsrc="([^"]+)"', block)
        medias = re.findall(r"<media\b", block)
        if len(images) != 1 or len(medias) != 1 or "<subfigure" in block:
            continue
        alt = re.search(r'<media\b[^>]*\balt="([^"]*)"', block)
        title = re.search(r"<title>(.*?)</title>", block, re.S)
        caption = re.search(r"<caption>(.*?)</caption>", block, re.S)
        caption = strip_markup(caption.group(1)) if caption else ""
        credit = ""
        cut = re.search(r"\(\s*(image\s+)?credits?\b[^)]*(\([^)]*\)[^)]*)*\)?\s*$", caption, re.I)
        if cut:
            caption, credit = caption[:cut.start()].strip(), cut.group(0).strip(" ()")
        out.append((fid, strip_markup(title.group(1)) if title else "", caption, credit,
                    strip_markup(html.unescape(alt.group(1))) if alt else "", images[0].rsplit("/", 1)[-1]))
    return out


def figure_rows(fig, book_name, page):
    """The rows of one OpenStax figure, or [] when it is left out (see the module docstring)."""
    fid, title, caption, credit, alt, media = fig
    words = f"{title} {caption} {alt}"
    if not media.lower().endswith((".jpg", ".jpeg", ".png")) or NOT_SHOWN.search(words + " " + credit):
        return []
    if credit and (not openstax_credit_free(credit) or not CHART_WORDS.search(words)):
        return []
    source = f"OpenStax, {book_name} ({page}), figure {fid}, CC BY 4.0" + (f"; {credit}" if credit else "")
    rows = []
    if len(alt.split()) >= 8:
        rows.append({"question": DESCRIBE, "answer": sentence(alt), "credit": source})
    if len(caption.split()) >= 5:
        shows = sentence(f"{title.rstrip('.:')}: {caption}" if title else caption)
        rows.append({"question": FIGURE_SHOWS, "answer": shows, "credit": source})
    return rows


def openstax_items(want):
    """(name, picture address, rows) for the figures of the OpenStax books, a fair share from each book."""
    s, items = session(), []
    share = want // len(OPENSTAX_BOOKS) + 1
    for repo, commit, slug, book_name in OPENSTAX_BOOKS:
        base = f"{OPENSTAX_RAW}/{repo}/{commit}"
        try:
            collection = s.get(f"{base}/collections/{slug}.collection.xml", timeout=60).text
        except Exception as error:  # noqa: BLE001 - one book down does not stop the pack
            say(f"OpenStax {book_name}: left out ({error})")
            continue
        if not CC_BY_4.search(collection):
            say(f"OpenStax {book_name}: this version is not marked CC BY 4.0, left out")
            continue
        modules = re.findall(r'document="(m\d+)"', collection)
        random.Random(slug).shuffle(modules)
        got = 0
        for module in modules:
            if got >= share:
                break
            try:
                cnxml = s.get(f"{base}/modules/{module}/index.cnxml", timeout=60).text
            except Exception:  # noqa: BLE001 - the next module
                continue
            page = f"https://github.com/openstax/{repo}/blob/{commit}/modules/{module}/index.cnxml"
            for fig in cnxml_figures(cnxml):
                rows = figure_rows(fig, book_name, page)
                if rows:
                    name = re.sub(r"[^\w.-]+", "_", f"openstax-{slug}-{fig[5].rsplit('.', 1)[0]}")[:110] + ".jpg"
                    items.append((name, f"{base}/media/{fig[5]}", rows))
                    got += 1
            time.sleep(0.3)
        say(f"OpenStax {book_name}: {got} figures")
    return items


def build_openstax_figures(limit):
    """The openstax_figures pack (see the module docstring)."""
    items = openstax_items(int(limit * 1.1) + 6)
    random.Random(2026).shuffle(items)
    return with_twins(fetch_all(items, workers=4, pause=0.3)[:limit])


# ----------------------------------------------------------------- Commons charts with their own descriptions

def chart(kind):
    """A rows_for function: the chart's kind from its category, and what it shows from its own description; a
    file without a real description (eight words or more) is left out."""
    def rows_for(title, text):
        if len((text or "").split()) < 8:
            return []
        return [(CHART_KIND, f"This is {kind}."), (CHART_SHOWS, text)]
    return rows_for


COMMONS_CHARTS = [
    ("Pie charts", True, chart("a pie chart")),
    ("Bar charts", True, chart("a bar chart")),
    ("Line charts", True, chart("a line chart")),
    ("Area charts", True, chart("an area chart")),
    ("Histograms", True, chart("a histogram")),
    ("Venn diagrams", True, chart("a Venn diagram")),
    ("Population pyramids", False, chart("a population pyramid, a chart of a population by age and sex")),
    ("Organizational charts", True, chart("an organisation chart")),
    ("Timelines", True, chart("a timeline")),
]


def build_commons_charts(limit):
    """The commons_charts pack (see the module docstring)."""
    return build_described(COMMONS_CHARTS, limit, "chart", adults_only=True)


# ----------------------------------------------------------------- the packs

CHART_PACKS = {
    "openstax_figures": (build_openstax_figures, "OpenStax (Rice University), Principles of Economics 3e, "
                                                 "Introductory Statistics 2e, Biology 2e, Chemistry 2e, College "
                                                 "Physics 2e and Astronomy 2e, CC BY 4.0 (the versions published "
                                                 "before OpenStax's 2026 change to CC BY-NC-SA, read from "
                                                 "https://github.com/openstax); each figure credited below. "
                                                 "Download for free at https://openstax.org."),
    "commons_charts": (build_commons_charts, "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public "
                                             "domain or CC BY (credited below); captions CC0."),
}
CHART_LIMITS = {"openstax_figures": 3000, "commons_charts": 1500}
CHART_COMMONS_KEYS = ("commons_charts",)


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one chart pack builder.")
    parser.add_argument("key", choices=sorted(CHART_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    entries = CHART_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
