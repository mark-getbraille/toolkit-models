"""Pack builder for CLOTHING CARE LABELS CLOSE UP, extending home_packs.laundry_symbols (which has each Commons symbol
file with its meaning, clean computer-made rows of those files, and the 14 photos of Category:Laundry tags). Used by
build_packs.py in the same way as its own PACKS: build_laundry_care_labels(limit) returns [(file name, JPEG bytes or
None, row)], where a row is {"question", "answer", "credit"}, plus "synthetic": true on the computer-made labels. A
picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file"
names the same picture (food_packs.with_twins). The limit counts pictures.

Why: the care label is sewn inside the garment, small and often faded; a blind person needs the symbols read out in
plain words ("Machine wash at 30 °C, gentle cycle. Do not bleach. Do not tumble dry. Iron on low.").

The pack (laundry_care_labels) has two parts:
  1. COMPUTER-MADE CARE LABELS (rows marked "synthetic": true). Woven or printed labels drawn here with Pillow from a
     fixed seed: the GINETEX / ISO 3758 and ASTM D5489 care symbols (washtub, triangle, square with circle, square
     with lines, iron, circle; dots for heat, bars for a gentler cycle, a cross for "do not"), drawn from simple shapes
     (no one's artwork is copied), in the usual order, with the label's other printed lines (made-up fibre content,
     size, "Made in" country and sometimes the ASTM words, such as "MACHINE WASH COLD"), then photographed by
     phone_photo.py (turned, tilted, uneven light, blur, on a fabric-coloured background). Because the label was made
     from the meanings, every answer is exact: "What do these washing symbols mean?", "What does the label say about
     washing?", "Can this go in the tumble dryer?", "What is this garment made of?". The symbols are a GINETEX
     trademark (a trademark, not a copyright: describing and drawing them on care labels is what they are for).
  2. COMMONS PHOTOS OF REAL CARE LABELS found with Commons search (care label, washing label, laundry label, care
     instructions, care tag, washing symbols) whose words are about clothes or textiles and that are NOT in
     Category:Laundry tags (laundry_symbols has those): files CC0, public domain or CC BY (each file's licence
     checked on its own page); "What is this?" -> "This is a clothing care label ..." and the file's own
     description, which is the only place a symbol's meaning is read from.

Open datasets of care-label photos looked at: the Roboflow Universe laundry-symbol sets (some CC BY 4.0 or MIT) need
a Roboflow account and their photos' origin is not stated; they are sign-up entries in
training-kit/kit/daily_access_sources.py. No other open set was found (November 2026).

Safety: labels and fabric only; no people (Commons files whose words name a person or nudity are left out). The pack
may be used for picture-making.

    python packs/care_label_packs.py laundry_care_labels --limit 8 --no-commons      (a quick check)
"""

import random
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import say, pass_random, ALT_TEXT
from phone_photo import font, phone_photo

LABEL_Q = "What do these washing symbols mean?"
WASH_Q = "What does the label say about washing?"
DRYER_Q = "Can this go in the tumble dryer?"
FABRIC_Q = "What is this garment made of?"
WHAT_Q = "What is this?"
SEED = 9304
WASH, BLEACH, TUMBLE, DRY, IRON, CLEAN = "wash", "bleach", "tumble", "dry", "iron", "clean"
ORDER = (WASH, BLEACH, TUMBLE, DRY, IRON, CLEAN)

# Every symbol drawn here: (kind, how it is drawn, its meaning, the ASTM words a US label may print beside it or "").
# The meanings are the same words as home_packs.LAUNDRY_SYMBOLS.
SYMBOLS = [
    (WASH, ("tub", 0, 0), "Machine washable.", "MACHINE WASH"),
    (WASH, ("tub", 30, 0), "Machine wash at 30 °C.", "MACHINE WASH COLD"),
    (WASH, ("tub", 30, 1), "Machine wash at 30 °C, gentle cycle.", "MACHINE WASH COLD GENTLE CYCLE"),
    (WASH, ("tub", 30, 2), "Machine wash at 30 °C, very gentle cycle.", "MACHINE WASH COLD DELICATE CYCLE"),
    (WASH, ("tub", 40, 0), "Machine wash at 40 °C.", "MACHINE WASH WARM"),
    (WASH, ("tub", 40, 1), "Machine wash at 40 °C, gentle cycle.", "MACHINE WASH WARM GENTLE CYCLE"),
    (WASH, ("tub", 60, 0), "Machine wash at 60 °C.", "MACHINE WASH HOT"),
    (WASH, ("tub", 95, 0), "Machine wash at 95 °C.", ""),
    (WASH, ("tub-hand", 0, 0), "Hand wash only.", "HAND WASH ONLY"),
    (WASH, ("tub-x", 0, 0), "Do not wash.", "DO NOT WASH"),
    (BLEACH, ("triangle", 0), "Any bleach may be used.", "BLEACH WHEN NEEDED"),
    (BLEACH, ("triangle-lines", 0), "Only non-chlorine (oxygen) bleach may be used.", "NON-CHLORINE BLEACH ONLY"),
    (BLEACH, ("triangle-x", 0), "Do not bleach.", "DO NOT BLEACH"),
    (TUMBLE, ("dryer", 1), "Tumble dry on low heat.", "TUMBLE DRY LOW"),
    (TUMBLE, ("dryer", 2), "Tumble dry on normal heat.", "TUMBLE DRY MEDIUM"),
    (TUMBLE, ("dryer", 0), "Tumble drying is allowed.", "TUMBLE DRY"),
    (TUMBLE, ("dryer-x", 0), "Do not tumble dry.", "DO NOT TUMBLE DRY"),
    (DRY, ("line", 0), "Hang to dry.", "LINE DRY"),
    (DRY, ("flat", 0), "Dry flat.", "DRY FLAT"),
    (DRY, ("drip", 0), "Drip dry: hang up wet, without wringing.", "DRIP DRY"),
    (DRY, ("line-shade", 0), "Hang to dry in the shade.", "LINE DRY IN SHADE"),
    (IRON, ("iron", 1), "Iron on low (up to 110 °C).", "IRON LOW"),
    (IRON, ("iron", 2), "Iron on medium (up to 150 °C).", "IRON MEDIUM"),
    (IRON, ("iron", 3), "Iron on high (up to 200 °C).", "IRON HIGH"),
    (IRON, ("iron-x", 0), "Do not iron.", "DO NOT IRON"),
    (CLEAN, ("circle", "P"), "Professional dry cleaning with tetrachloroethene (P).", "DRY CLEAN"),
    (CLEAN, ("circle", "F"), "Professional dry cleaning with hydrocarbon solvents (F).", "DRY CLEAN"),
    (CLEAN, ("circle", "W"), "Professional wet cleaning.", "PROFESSIONAL WET CLEAN"),
    (CLEAN, ("circle-x", ""), "Do not dry clean.", "DO NOT DRY CLEAN"),
]
FIBRES = ("100% COTTON", "100% POLYESTER", "60% COTTON 40% POLYESTER", "95% COTTON 5% ELASTANE", "100% WOOL",
          "80% WOOL 20% NYLON", "100% LINEN", "100% SILK", "70% VISCOSE 30% POLYAMIDE", "100% ACRYLIC",
          "50% COTTON 50% MODAL", "92% POLYESTER 8% SPANDEX")
FIBRE_WORDS = {"COTTON": "cotton", "POLYESTER": "polyester", "ELASTANE": "elastane", "WOOL": "wool",
               "NYLON": "nylon", "LINEN": "linen", "SILK": "silk", "VISCOSE": "viscose", "POLYAMIDE": "polyamide",
               "ACRYLIC": "acrylic", "MODAL": "modal", "SPANDEX": "spandex"}
COUNTRIES = ("BANGLADESH", "VIETNAM", "PORTUGAL", "TURKEY", "INDIA", "CHINA", "CAMBODIA", "MEXICO", "ITALY",
             "SRI LANKA", "PAKISTAN", "CANADA", "USA")
SIZES = ("XS", "S", "M", "L", "XL", "XXL", "8", "10", "12", "14", "32", "34")


def fibre_words(line):
    """ "60% COTTON 40% POLYESTER" -> "60% cotton and 40% polyester"."""
    parts = [f"{p} {FIBRE_WORDS[f]}" for p, f in re.findall(r"(\d+%) ([A-Z]+)", line)]
    return " and ".join([", ".join(parts[:-1]), parts[-1]]) if len(parts) > 1 else parts[0]


def draw_symbol(draw, shape, x, y, size, ink):
    """One care symbol drawn from simple shapes in a size-by-size box at (x, y)."""
    w = max(2, size // 14)
    kind = shape[0]
    pad = size * 0.12
    left, top, right, bottom = x + pad, y + pad, x + size - pad, y + size - pad
    cross = kind.endswith("-x")

    def dots(n, cx, cy, r):
        """n heat dots in a row centred at (cx, cy)."""
        for i in range(n):
            ox = cx + (i - (n - 1) / 2) * r * 3
            draw.ellipse([ox - r, cy - r, ox + r, cy + r], fill=ink)

    if kind.startswith("tub"):
        mid = top + (bottom - top) * 0.3
        draw.line([(left, mid), (left + (right - left) * 0.1, bottom), (right - (right - left) * 0.1, bottom),
                   (right, mid)], fill=ink, width=w)
        wave = [(left + i * (right - left) / 8, mid - (size * 0.05 if i % 2 else 0)) for i in range(9)]
        draw.line(wave, fill=ink, width=w)
        if kind == "tub-hand":
            draw.line([(x + size * 0.45, mid + size * 0.05), (x + size * 0.62, y + size * 0.15)], fill=ink, width=w)
            draw.ellipse([x + size * 0.56, y + size * 0.08, x + size * 0.72, y + size * 0.22], outline=ink, width=w)
        elif shape[1]:
            text = str(shape[1])
            f = font(int(size * 0.28), bold=True)
            tw = draw.textlength(text, font=f)
            draw.text((x + (size - tw) / 2, mid + size * 0.06), text, font=f, fill=ink)
        for i in range(shape[2]):
            yy = bottom + w * 2 + i * w * 2.5
            draw.line([(left, yy), (right, yy)], fill=ink, width=w)
    elif kind.startswith("triangle"):
        draw.polygon([(x + size / 2, top), (left, bottom), (right, bottom)], outline=ink, width=w)
        if kind == "triangle-lines":
            draw.line([(x + size * 0.42, bottom), (x + size * 0.58, top + size * 0.3)], fill=ink, width=w)
            draw.line([(x + size * 0.56, bottom), (x + size * 0.68, top + size * 0.48)], fill=ink, width=w)
    elif kind.startswith("dryer"):
        draw.rectangle([left, top, right, bottom], outline=ink, width=w)
        r = (right - left) * 0.36
        draw.ellipse([x + size / 2 - r, y + size / 2 - r, x + size / 2 + r, y + size / 2 + r], outline=ink, width=w)
        dots(shape[1], x + size / 2, y + size / 2, size * 0.035)
    elif kind in ("line", "flat", "drip", "line-shade"):
        draw.rectangle([left, top, right, bottom], outline=ink, width=w)
        if kind in ("line", "line-shade"):
            draw.arc([left, top - (bottom - top) * 0.35, right, top + (bottom - top) * 0.35], 0, 180, fill=ink,
                     width=w)
        elif kind == "flat":
            draw.line([(left + size * 0.12, y + size / 2), (right - size * 0.12, y + size / 2)], fill=ink, width=w)
        else:
            for f in (0.35, 0.5, 0.65):
                draw.line([(x + size * f, top + size * 0.12), (x + size * f, bottom - size * 0.12)], fill=ink,
                          width=w)
        if kind == "line-shade":
            draw.line([(left, top + size * 0.25), (left + size * 0.25, top)], fill=ink, width=w)
    elif kind.startswith("iron"):
        base = bottom - size * 0.1
        draw.polygon([(left, base), (left + size * 0.12, top + size * 0.3), (right - size * 0.1, top + size * 0.3),
                      (right, base)], outline=ink, width=w)
        draw.line([(left + size * 0.3, top + size * 0.3), (left + size * 0.35, top + size * 0.12),
                   (right - size * 0.12, top + size * 0.12)], fill=ink, width=w)
        dots(shape[1], x + size * 0.52, base - size * 0.16, size * 0.035)
    elif kind.startswith("circle"):
        draw.ellipse([left, top, right, bottom], outline=ink, width=w)
        if shape[1]:
            f = font(int(size * 0.42), bold=True)
            tw = draw.textlength(shape[1], font=f)
            draw.text((x + (size - tw) / 2, y + size * 0.26), shape[1], font=f, fill=ink)
    if cross:
        draw.line([(x + pad * 0.5, y + pad * 0.5), (x + size - pad * 0.5, y + size - pad * 0.5)], fill=ink, width=w)
        draw.line([(x + size - pad * 0.5, y + pad * 0.5), (x + pad * 0.5, y + size - pad * 0.5)], fill=ink, width=w)


def choose_symbols(rng):
    """One symbol of each kind in the usual order (the natural-drying one only sometimes), consistent: a "do not
    wash" label has no bleach or tumble symbol."""
    picks = []
    for kind in ORDER:
        if kind == DRY and rng.random() < 0.6:
            continue
        picks.append(rng.choice([s for s in SYMBOLS if s[0] == kind]))
    if picks[0][2] == "Do not wash.":
        picks = [p for p in picks if p[0] not in (BLEACH, TUMBLE)]
    return picks


def make_label(n, seed=SEED):
    """The n-th computer-made care label: (file name, JPEG bytes, rows). The same n and seed give the same label."""
    from PIL import Image, ImageDraw
    rng = random.Random(f"{seed}-{n}")
    picks = choose_symbols(rng)
    fibre, country, size = rng.choice(FIBRES), rng.choice(COUNTRIES), rng.choice(SIZES)
    words = rng.random() < 0.5                         # US style: the ASTM words printed below the symbols
    symbol = rng.randint(70, 110)
    gap = symbol // 4
    width = max(len(picks) * (symbol + gap) + gap, 520)
    lines = [f"SIZE {size}", fibre, f"MADE IN {country}"]
    if words:
        lines += [p[3] for p in picks if p[3]]
    line_h = int(symbol * 0.32)
    height = symbol + gap * 3 + len(lines) * (line_h + 6)
    woven = rng.random() < 0.5
    paper = rng.choice([(250, 248, 240), (245, 245, 245), (236, 232, 220), (30, 30, 34), (240, 236, 245)])
    ink = (20, 20, 20) if sum(paper) > 300 else (235, 235, 230)
    label = Image.new("RGB", (width, height), paper)
    draw = ImageDraw.Draw(label)
    if woven:                                          # the fine weave of a woven label
        shade = tuple(max(0, c - 10) for c in paper)
        for yy in range(0, height, 3):
            draw.line([(0, yy), (width, yy)], fill=shade)
    x0 = (width - (len(picks) * (symbol + gap) - gap)) // 2
    for i, p in enumerate(picks):
        draw_symbol(draw, p[1], x0 + i * (symbol + gap), gap, symbol, ink)
    f = font(line_h, bold=rng.random() < 0.3, kind=rng.randrange(8))
    yy = symbol + gap * 2
    for line in lines:
        tw = draw.textlength(line, font=f)
        draw.text(((width - tw) / 2, yy), line, font=f, fill=ink)
        yy += line_h + 6
    background = rng.choice([(40, 60, 110), (150, 30, 40), (60, 60, 60), (210, 200, 180), (90, 120, 80),
                             (20, 20, 20), (180, 180, 200)])
    data = phone_photo(label, rng, background=background, strength=rng.uniform(0.4, 1.0))
    credit = ("A computer-made care label drawn with Pillow (synthetic; made-up fibre, size and country), "
              "packs/care_label_packs.py, CC0")
    meanings = " ".join(p[2] for p in picks)
    tumble = next((p[2] for p in picks if p[0] == TUMBLE), "")
    rows = [{"question": LABEL_Q, "answer": meanings},
            {"question": WASH_Q, "answer": picks[0][2] if picks[0][0] == WASH else "It does not say."},
            {"question": DRYER_Q, "answer": ("No: " + tumble[0].lower() + tumble[1:]) if tumble.startswith("Do not")
             else ("Yes: " + tumble[0].lower() + tumble[1:]) if tumble else "The label has no tumble-drying symbol."},
            {"question": FABRIC_Q, "answer": f"The label says {fibre_words(fibre)}."}]
    return f"care-label-{n:05d}.jpg", data, [dict(r, credit=credit, synthetic=True) for r in rows]


# ----------------------------------------------------------------- Commons photos of real care labels

SEARCHES = ('intitle:"care label"', 'intitle:"care labels"', 'intitle:"washing label"', 'intitle:"laundry label"',
            'intitle:"care instructions"', 'intitle:"care tag"', 'intitle:"washing symbols"')
# A found file must be about clothes or textiles (a "hand washing instructions" sign in a toilet is not a care label).
CLOTHING_WORDS = re.compile(r"\b(care labels?|care tags?|laundry|garments?|cloth(es|ing)?|textiles?|fabrics?|shirts?|"
                            r"t-shirts?|jackets?|sweaters?|jumpers?|trousers|jeans|dress(es)?|socks|washing symbols?|"
                            r"wash(ing)? labels?)\b", re.I)
PERSON_WORDS = re.compile(r"\b(man|men|woman|women|person|people|boy|girl|child|baby|wearing|portrait|selfie)\b",
                          re.I)


def commons_label_photos(want):
    """[(file name, address, rows)] for Commons photos of care labels found by search, not in Category:Laundry tags,
    free files only."""
    from food_packs import commons_get, commons_members
    from home_packs import home_entries, file_name, NUDE
    from build_packs import session
    s = session()
    known = set(commons_members(s, "Laundry tags", "file"))
    titles = []
    for query in SEARCHES:
        data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": 100,
                               "srsearch": f"{query} filetype:bitmap"})
        titles += [r["title"] for r in (data.get("query") or {}).get("search") or []
                   if r["title"] not in known and r["title"] not in titles]
    say(f"Commons care labels: {len(titles)} files found by search (not in Laundry tags)")
    items = []
    for title, url, credit, text in home_entries(s, titles):
        words = f"{title} {text}"
        if NUDE.search(words) or PERSON_WORDS.search(words) or not CLOTHING_WORDS.search(words) or \
                re.search(r"\bhand ?washing\b|\bhands?\b", words, re.I):
            continue
        rows = [{"question": WHAT_Q, "answer": "This is a clothing care label: its symbols say how to wash, bleach, "
                                             "dry, iron and clean the garment.", "credit": credit}]
        if text:
            rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
        items.append((file_name("care-photo", title), url, rows))
        if len(items) >= want:
            break
    return items


def build_laundry_care_labels(limit, commons=True):
    """The laundry_care_labels pack (see the module docstring): the Commons photos first, the computer-made labels
    for the rest of the limit."""
    from food_packs import with_twins
    from home_packs import commons_fetch
    photos = with_twins(commons_fetch(commons_label_photos(limit // 4))) if commons else []
    made = sum(1 for e in photos if e[1] is not None)
    entries = list(photos)
    for n in range(max(0, limit - made)):
        name, data, rows = make_label(n)
        entries += with_twins([(name, data, rows)])
    rng = pass_random(SEED)
    pictures = [e for e in entries if e[1] is not None]
    rng.shuffle(pictures)
    keep = {e[0] for e in pictures[:limit]}
    return [e for e in pictures[:limit]] + [e for e in entries if e[1] is None and
                                            e[2]["file"].split("/", 1)[-1] in keep]


# ----------------------------------------------------------------- the packs

CARE_LABEL_PACKS = {
    "laundry_care_labels": (build_laundry_care_labels,
                            "Computer-made care labels drawn with Pillow by packs/care_label_packs.py (synthetic, CC0; "
                            "the care symbols are a GINETEX trademark, drawn here from simple shapes), and Wikimedia "
                            "Commons photos of care labels (https://commons.wikimedia.org): files CC0, public domain "
                            "or CC BY, credited below; captions CC0."),
}
CARE_LABEL_LIMITS = {
    "laundry_care_labels": 3000,     # a few dozen Commons photos, the rest computer-made
}
CARE_LABEL_COMMONS_KEYS = ("laundry_care_labels",)


def main(argv=None):
    """Build the pack with a small limit and print its rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the care label pack builder.")
    parser.add_argument("key", choices=sorted(CARE_LABEL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--no-commons", action="store_true", help="only the computer-made labels")
    parser.add_argument("--save", default="", help="a folder to write the pictures to")
    args = parser.parse_args(argv)
    entries = build_laundry_care_labels(args.limit, commons=not args.no_commons)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:300])
        if data and args.save:
            os.makedirs(args.save, exist_ok=True)
            with open(os.path.join(args.save, name), "wb") as f:
                f.write(data)
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
