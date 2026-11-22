"""A shared Wikimedia Commons builder for the picture-reading packs (handwriting, charts, date codes, sign language,
weather maps: handwriting_packs.py, chart_packs.py, date_code_packs.py, sign_language_packs.py, weather_map_packs.py).

Unlike home_packs.build_commons_topic, which takes only photos, these packs also want DRAWINGS: charts, diagrams,
fingerspelling charts and signatures are often SVG files. Commons sends a PNG of an SVG; a see-through PNG is laid on
white here (flat_smaller), so black ink on a see-through page does not turn into black on black.

A spec is (category, deeper, rows_for): the Commons category (without "Category:"; or "search:<words>", the files
Commons' own search finds for those words), whether its subcategories are read
too (one level, leaving out subcategories whose names match LEFT_OUT_SUBCATS), and rows_for(title, text), a function
that gives the [(question, answer)] for one file from its title and its own English caption or description ("" when
it has none), or [] to leave the file out. Every answer comes from those words or from the category's name: nothing
is guessed from the picture.

Only files whose licence is CC0, public domain, CC BY, MIT or Apache (home_packs.home_entries, which never takes
BY-SA, NC or ND), never files whose words are about nudity or sex; files whose words name a child are left out when
adults_only, else their rows are marked "child".

    (used by the pack files; not run on its own)
"""

import io
import math
import re

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, LONG_SIDE
from food_packs import commons_members, with_twins
from home_packs import home_entries, commons_fetch, file_name, NUDE
from expression_packs import mark_child, CHILD

# Subcategories never read: art, people's portraits and pictures that are not of the thing itself.
LEFT_OUT_SUBCATS = re.compile(r"\b(nude|naked|erotic|sex\w*|porn\w*|videos?|audio|sounds?|people|portraits?|"
                              r"tattoos?|in art|paintings?|sculptures?|caricatures?|forger\w*|fakes?)\b", re.I)


def flat_smaller(data):
    """A picture as JPEG bytes at most LONG_SIDE pixels on the long side, with any see-through parts laid on white
    (drawn charts and signatures come from Commons as see-through PNGs); None when it cannot be read or is tiny."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            back = Image.new("RGBA", img.size, (255, 255, 255, 255))
            back.alpha_composite(img)
            img = back
        img = img.convert("RGB")
    except Exception:  # noqa: BLE001 - left out
        return None
    if min(img.size) < 64:
        return None
    img.thumbnail((LONG_SIDE, LONG_SIDE))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=90)
    return out.getvalue()


def search_titles(s, words, most=1000):
    """The titles of Commons files whose page has these words (Commons' own search, files only), at most most."""
    from food_packs import commons_get
    titles, params = [], {"action": "query", "list": "search", "srsearch": words, "srnamespace": 6,
                          "srlimit": 500}
    while len(titles) < most:
        data = commons_get(s, params)
        titles += [m["title"] for m in (data.get("query") or {}).get("search", [])]
        if "continue" not in data:
            break
        params.update(data["continue"])
    return titles[:most]


def category_titles(s, category, deeper):
    """The file titles of a Commons category, and of its subcategories (one level) when deeper; subcategories
    named in LEFT_OUT_SUBCATS are not read. A category that does not exist gives none. A "category" written
    "search:<words>" is a Commons search for those words instead (files only)."""
    if category.startswith("search:"):
        return search_titles(s, category.split(":", 1)[1])
    titles = commons_members(s, category, "file")
    if deeper:
        for sub in commons_members(s, category, "subcat"):
            if not LEFT_OUT_SUBCATS.search(sub):
                titles += commons_members(s, sub.split(":", 1)[-1], "file")
    return list(dict.fromkeys(titles))


def build_described(specs, limit, prefix, adults_only=True, extra_row=None):
    """A pack from Commons specs (see the module's docstring): the categories take turns (in a fixed shuffled
    order) so each gets an even share, until there are enough pictures. extra_row(title, text, category) may give
    one more {"question", "answer"} for a file (or None). Returns pack entries [(name, JPEG, row)], each picture
    once with its other rows pointing at it."""
    s, items, seen = session(), [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.2 / max(1, len(order))))
    want = int(limit * 1.2) + 2
    queues = [[category, deeper, rows_for, None] for category, deeper, rows_for in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            category, deeper, rows_for, titles = q
            if titles is None:
                titles = [t for t in category_titles(s, category, deeper) if t not in seen]
                pass_random(prefix + category).shuffle(titles)
                say(f"Commons {category}: {len(titles)} files")
            batch, q[3] = titles[:share * 2], titles[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            got = 0
            for title, url, credit, text in home_entries(s, batch, drawings=True):
                if got >= share or title in seen:
                    continue
                words = f"{title} {text}"
                if NUDE.search(words) or (adults_only and CHILD.search(words)):
                    continue
                pairs = rows_for(title, text)
                if not pairs:
                    continue
                seen.add(title)
                rows = [mark_child({"question": qn, "answer": an, "credit": credit}, words) for qn, an in pairs]
                if extra_row:
                    more = extra_row(title, text, category)
                    if more:
                        rows.append(mark_child(dict(more, credit=credit), words))
                items.append((file_name(prefix, title), url, rows))
                got += 1
            if not q[3]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    fetched = []
    for name, data, rows in commons_fetch(items[:want], raw=True):
        data = flat_smaller(data)
        if data:
            fetched.append((name, data, rows))
    return with_twins(fetched[:limit])


def file_words(title):
    """A Commons file title as words: "File:Abraham Lincoln signature.svg" -> "Abraham Lincoln signature"."""
    name = title.split(":", 1)[-1].rsplit(".", 1)[0]
    return re.sub(r"\s+", " ", name.replace("_", " ")).strip()
