"""Picture pack of PUBLIC-DOMAIN GOLDEN AGE COMICS (the owner's request of 2026-11-22: pictures for the picture
describer). Used by build_packs.py in the same way as its own PACKS: build_<key>(limit) returns [(file name, JPEG
bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row)
rows naming the same picture. The limit counts pictures.

The pack (COMICS_PACKS):
  commons_golden_age_comics  Comic book covers, pages and panels of the 1930s to 1950s from the Wikimedia Commons
                    category "Golden Age of Comic Books" and its subcategories (two levels down), ONLY files whose
                    Commons page records the evidence that they are in the US public domain: the licence templates
                    "PD-US-not renewed" (published 1929 to 1963 and the copyright not renewed), "PD-US-no notice"
                    (published without a copyright notice before 1978) or "PD-US-expired" (published before 1931),
                    read from the file's own categories (PD_EVIDENCE). A file marked only "public domain" with no such
                    reason is left out: the owner's rule is that 1931 to 1963 works need evidence of no renewal.
                    WHY NOT THE COMIC SITES: the Digital Comic Museum and Comic Book Plus host public-domain comics,
                    but their robots.txt files (checked 2026-11-22) say "Content-Signal: ai-train=no" (Digital Comic
                    Museum) and block AI crawlers by name, ClaudeBot and anthropic-ai included (both sites), so
                    nothing is taken from them. The Internet Archive's comics uploads (comics_inbox) mix public-domain
                    and copyrighted comics (Action Comics, Human Torch ...) with no evidence per item, so they are not
                    used either.
                    ANSWERS ONLY FROM THE RECORD: no comic here has a transcription or a panel-by-panel description,
                    so the answers never describe the panels. "What comic is this from?" is answered from the Commons
                    file's own caption or description (the title, issue, publisher, page or panel as its uploader
                    wrote them, quoted), and "Is this comic in the public domain?" from its licence template. A file
                    whose record says too little (under five words) gives no rows: it is set aside with its hints
                    (title, date, categories) for a person to describe (build_packs.needs_description), the
                    "describe it yourself" route; the kit's comics entry explains it.
                    Left out: files whose words name racist caricature or stereotypes (RACIST): they are not taught as
                    normal; nudity or sex (the packs' NUDE words); and files whose record names war atrocities or gore
                    are kept only with "content": "graphic". The pack shows drawn people only; it may not be used for
                    picture-making all the same (comic art is the artists' style).

    python packs/comics_packs.py commons_golden_age_comics --limit 6
"""

import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import clean, considered, needs_description, pass_random, say, session
from food_packs import commons_description, commons_get, commons_members, with_twins

ROOT = "Golden Age of Comic Books"
FROM_Q = "What comic is this from?"
PD_Q = "Is this comic in the public domain?"
# The categories Commons' public-domain templates add, as the evidence of US public domain.
PD_EVIDENCE = {
    "not renewed": (re.compile(r"\bPD[ -]US[ -]not[ -]renewed\b", re.I),
                    "its US copyright was not renewed (Commons licence template PD-US-not renewed)"),
    "no notice": (re.compile(r"\bPD[ -]US[ -]no[ -]notice\b", re.I),
                  "it was published in the US without a copyright notice (Commons licence template PD-US-no notice)"),
    "expired": (re.compile(r"\bPD[ -]US[ -]expired\b|\bPD[ -]US[ -]19[0-2]\d\b", re.I),
                "it was published before 1931, so its US copyright has expired (Commons licence template "
                "PD-US-expired)"),
}
RACIST = re.compile(r"\b(racis[mt]\w*|caricatur\w*|stereotyp\w*|minstrel\w*|blackface|pickaninn\w*|sambo|"
                    r"golliwog\w*|yellow peril|jap\b|japs\b)\b", re.I)
NUDE = re.compile(r"\b(nud\w*|naked|topless|erotic\w*|sex\w*|porn\w*|lingerie|good girl art)\b", re.I)
GRAPHIC = re.compile(r"\b(gore|gory|atrocit\w*|torture\w*|corpses?|decapitat\w*|massacre\w*)\b", re.I)


def comic_files(s, depth=2):
    """The file titles of the root category and its subcategories, depth levels down."""
    titles, level, seen = list(commons_members(s, ROOT, "file")), [ROOT], {ROOT}
    for _ in range(depth):
        nxt = []
        for category in level:
            for sub in commons_members(s, category, "subcat"):
                name = sub.split(":", 1)[-1]
                if name not in seen:
                    seen.add(name)
                    nxt.append(name)
                    titles += commons_members(s, name, "file")
        level = nxt
    return list(dict.fromkeys(titles))


def evidence(categories):
    """(key, words) of the first public-domain evidence in a file's categories, or ("", "")."""
    for key, (pattern, words) in PD_EVIDENCE.items():
        if pattern.search(categories or ""):
            return key, words
    return "", ""


def comic_entry(title, info, caption):
    """What one Commons file gives: ("use", rows-to-be) or ("needs", hints) or ("out", reason), from its imageinfo
    (url, thumburl, mime, extmetadata) and its English caption."""
    meta = info.get("extmetadata") or {}
    value = (lambda key: clean((meta.get(key) or {}).get("value")))
    licence, categories = value("LicenseShortName"), value("Categories")
    description = value("ImageDescription")
    words = " ".join([title, caption or "", description, categories])
    key, basis = evidence(categories)
    if info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
        return "out", "not a JPEG or PNG picture"
    if not key or not re.match(r"public domain|pd", licence, re.I):
        return "out", f"no evidence of US public domain on its page (licence: {licence or 'none'})"
    if RACIST.search(words):
        return "out", "its words name racist caricature or stereotypes"
    if NUDE.search(words):
        return "out", "its words are about nudity or sex"
    about = commons_description(caption, description)
    marks = {"content": "graphic"} if GRAPHIC.search(words) else {}
    artist = value("Artist") or "unknown"
    page = "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")
    credit = f"{title} by {artist}, public domain in the US: {basis}, {page}"
    if not about:
        return "needs", {"credit": credit, "licence": f"Public domain in the US: {basis}", "page_url": page,
                         "url": info["thumburl"], "title": title.split(":", 1)[-1].rsplit(".", 1)[0],
                         "date": value("DateTimeOriginal"), "categories": categories[:300], "marks": marks}
    rows = [dict({"question": FROM_Q, "answer": f"The Wikimedia Commons record of this picture says: \"{about.rstrip('.')}.\"",
                  "credit": credit}, **marks),
            dict({"question": PD_Q, "answer": f"Yes, in the United States, according to its Commons page: {basis}.",
                  "credit": credit}, **marks)]
    return "use", (info["thumburl"], rows)


def build_commons_golden_age_comics(limit):
    """The commons_golden_age_comics pack (see the module docstring)."""
    from home_packs import commons_fetch, file_name
    s = session()
    titles = comic_files(s)
    pass_random("golden-age-comics").shuffle(titles)
    say(f"Commons {ROOT}: {len(titles)} files")
    items = []
    for start in range(0, len(titles), 50):
        if len(items) >= limit * 1.15:
            break
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 1280,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|Categories|"
                                                      "DateTimeOriginal", "iiextmetadatalanguage": "en"})
        pages = [p for p in ((data.get("query") or {}).get("pages") or {}).values() if p.get("pageid")]
        captions = {}
        if pages:
            entities = commons_get(s, {"action": "wbgetentities", "ids": "|".join(f"M{p['pageid']}" for p in pages),
                                       "props": "labels", "languages": "en"}).get("entities", {})
            captions = {k: ((v.get("labels") or {}).get("en") or {}).get("value", "") for k, v in entities.items()}
        for p in pages:
            title = p["title"]
            kind, got = comic_entry(title, (p.get("imageinfo") or [{}])[0], captions.get(f"M{p['pageid']}", ""))
            name = file_name("comic", title)
            if kind == "out":
                considered(name, "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"), got)
            elif kind == "needs":
                needs_description(name, got["url"], got["credit"], got["licence"], "open", title=got["title"],
                                  reason="its Commons record does not say which comic, issue or page it is",
                                  extra={"date": got["date"], "categories": got["categories"], **got["marks"]},
                                  page_url=got["page_url"])
            else:
                items.append((name, got[0], got[1]))
        time.sleep(1)
    return with_twins(commons_fetch(items)[:limit])


COMICS_PACKS = {
    "commons_golden_age_comics": (build_commons_golden_age_comics,
                                  "Wikimedia Commons (https://commons.wikimedia.org), category Golden Age of Comic "
                                  "Books and its subcategories: only files whose page gives the evidence that they "
                                  "are in the US public domain (PD-US-not renewed, PD-US-no notice or PD-US-expired), "
                                  "each credited below with its basis; answers quote each file's own record."),
}
COMICS_LIMITS = {"commons_golden_age_comics": 1500}
COMICS_COMMONS_KEYS = ("commons_golden_age_comics",)


def main(argv=None):
    """Build the pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the Golden Age comics pack builder.")
    parser.add_argument("key", choices=sorted(COMICS_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    entries = COMICS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
