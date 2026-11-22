"""Picture pack of STILLS FROM PUBLIC-DOMAIN FILMS (the owner's request of 2026-11-22: pictures for the picture
describer, toward his video description feature). Used by build_packs.py in the same way as its own PACKS:
build_<key>(limit) returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes once
with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

The pack (FILM_STILLS_PACKS):
  pd_film_stills  A few stills (at most MOST_STILLS) from each of many public-domain films on the Internet Archive:
                  - Prelinger Archives films (collection prelinger) whose item carries a public-domain mark
                    (licenseurl: the Public Domain Dedication, the Public Domain Mark or CC0). The Prelinger
                    Archives' own advice is followed: "DO NOT ASSUME that all Prelinger Archives films are in the
                    public domain"; a film without the mark is left out (see civil_defense_packs.py);
                  - National Park Service videos (creator the National Park Service, with the item's public-domain
                    mark): US government works (17 U.S.C. 105);
                  - NASA films whose creator is NASA (US government works, 17 U.S.C. 105).
                  Stills are taken with ffmpeg at changes of scene (civil_defense_packs.ffmpeg_stills and
                  good_stills: titles and credits skipped, burned-in marks cut off, blurred, dark and repeated frames
                  left out), spread over the film; without ffmpeg, the Archive's own frame thumbnails of the film
                  (its ".thumbs" folder) are used instead.
                  Each still gets "Where is this picture from?" and "What film is this from?" with a fixed sentence
                  from the film's own record (its title, year and maker, and which archive) and the record's own
                  description quoted ("The film's catalogue record describes it: ..."). Nothing is said about what
                  the still itself shows, so nothing is guessed: what a still shows is for the audio-description
                  work the owner is building (the reference book "audio-description", textbooks/audio_description.py,
                  gives the guidelines). A film whose record has no description (under 8 words) gives no rows: its
                  stills are set aside for a person to describe (build_packs.needs_description).
                  Left out: civil defense films (they are the cd_films pack), home movies (private people who never
                  agreed to be shown), outtakes and unedited reels (no description of their own), anything whose
                  record names nudity or sex, the dead or victims (civil_defense_figures.LEAVE_OUT), and films whose
                  record names racist caricature or minstrel shows (RACIST): they are not taught as normal here.
                  Rows of films about war, disasters or injuries carry "content": "graphic", about medicine
                  "content": "medical", and about children, schools or pupils "child": True (never for
                  picture-making). The pack shows people, so it is never used for picture-making.

Needs the ffmpeg program and numpy (as cd_films): "sudo apt-get install -y ffmpeg".

    python packs/film_stills_packs.py pd_film_stills --limit 6 --items nps-video-seki-river-safety
"""

import os
import re
import shutil
import sys
import tempfile
from urllib.parse import quote

import build_packs  # noqa: F401 - loaded first, as the other pack modules do
import civil_defense_packs as cd
from build_packs import considered, listing_out_of_time, needs_description, pass_random, say, session
from food_packs import with_twins

ARCHIVE = cd.ARCHIVE
FROM_Q = "Where is this picture from?"
FILM_Q = "What film is this from?"
MOST_STILLS = 6
# The three kinds of film and their searches on the Internet Archive.
QUERIES = {
    "prelinger": 'mediatype:movies AND collection:prelinger AND licenseurl:*publicdomain*',
    "nps": 'mediatype:movies AND creator:"National Park Service" AND licenseurl:*publicdomain*',
    "nasa": 'mediatype:movies AND (creator:NASA OR creator:"National Aeronautics and Space Administration") AND '
            'NOT title:(mxf OR jpg OR srt OR mp4 OR mov)',
}
ARCHIVE_NAMES = {"prelinger": "the Prelinger Archives", "nps": "the National Park Service",
                 "nasa": "NASA"}
NASA = re.compile(r"^\W*(NASA|National Aeronautics and Space Administration)\b", re.I)
NPS = re.compile(r"^\W*National Park Service\b", re.I)
HOME_MOVIE = re.compile(r"\b(home movies?|outtakes?|unedited|raw footage|reel \d+|trims)\b", re.I)
RACIST = re.compile(r"\b(racis[mt]\w*|caricatur\w*|minstrel\w*|blackface|pickaninn\w*|darkie\w*|sambo|"
                    r"stereotyp\w*)\b", re.I)


def film_kind(meta):
    """("prelinger", "nps" or "nasa", how it is free) of a film, or ("", the reason it is not used)."""
    words = " ".join([cd.text_of(meta.get("title")), cd.text_of(meta.get("description")),
                      cd.text_of(meta.get("subject"))])
    creators = cd.listed(meta.get("creator"))
    collections = [c.lower() for c in cd.listed(meta.get("collection"))]
    licence = cd.text_of(meta.get("licenseurl"))
    if cd.LEAVE_OUT.search(words):
        return "", "its record names the dead, victims, Hiroshima or Nagasaki, nudity or sex"
    if RACIST.search(words):
        return "", "its record names racist caricature or a minstrel show"
    if HOME_MOVIE.search(cd.text_of(meta.get("title"))):
        return "", "a home movie, outtakes or an unedited reel"
    if cd.CD_TOPIC.search(cd.text_of(meta.get("title"))) and re.search(r"civil defen[cs]e|fallout|shelter", words,
                                                                       re.I):
        return "", "a civil defense film (the cd_films pack)"
    if cd.NC_ND.search(licence):
        return "", f"its licence is non-commercial or no-derivatives ({licence})"
    if any(NASA.match(c) for c in creators):
        return "nasa", f"public domain: made by NASA, {cd.PD_US}"
    if any(NPS.match(c) for c in creators) and cd.PD_MARK.search(licence):
        return "nps", f"public domain: made by the National Park Service, {cd.PD_US} (the item's mark: {licence})"
    if "prelinger" in collections and cd.PD_MARK.search(licence):
        return "prelinger", f"public domain (the item's mark: {licence})"
    return "", "no public-domain mark and not made by NASA or the National Park Service (Prelinger: 'DO NOT ASSUME')"


def lead(meta, kind):
    """ "A still from the 1950 film 'In Our Hands', made by Wilding Picture Productions, Inc. (the Prelinger
    Archives, on the Internet Archive)."."""
    title = cd.tidy_title(cd.text_of(meta.get("title")))
    year = cd.year_of(meta, cd.text_of(meta.get("title")))
    maker = next((c for c in cd.listed(meta.get("creator")) if c.lower() not in ("none", "unknown")), "")
    made = f", made by {maker}" if maker and "@" not in maker else ""
    return (f"A still from the {str(year) + ' ' if year else ''}film '{title}'{made} ({ARCHIVE_NAMES[kind]}, on the "
            f"Internet Archive).")


def thumbs(s, identifier, data, folder):
    """[(seconds, path)] of the Archive's own frame thumbnails of a film (its ".thumbs" folder), for when ffmpeg is
    missing; the seconds are read from the thumbnail's number."""
    out = []
    for f in data.get("files", []):
        name = f.get("name", "")
        found = re.search(r"\.thumbs/.*_(\d+)\.jpg$", name)
        if f.get("format") != "Thumbnail" or not found:
            continue
        path = os.path.join(folder, f"{len(out):05d}.jpg")
        if cd.download(s, f"{ARCHIVE}download/{quote(identifier)}/{quote(name)}", path, 5_000_000):
            out.append((float(found.group(1)), path))
    return out


def candidates(s, items=None):
    """[(identifier, kind searched)] to read: items when given, else each search in turn, shuffled in a fixed
    order, the three kinds taking turns."""
    if items:
        return [(i, "") for i in items]
    lists = []
    for kind, query in QUERIES.items():
        found = [d["identifier"] for d in cd.search(s, query, rows=3000) if d.get("identifier")]
        pass_random(f"films-{kind}").shuffle(found)
        lists.append([(i, kind) for i in found])
    out = []
    for group in zip(*[lst + [None] * (max(map(len, lists)) - len(lst)) for lst in lists]):
        out += [g for g in group if g]
    return out


def build_pd_film_stills(limit, items=None):
    """Stills from public-domain films (see the module docstring), at most limit pictures."""
    s, fetched, seen = session(), [], set()
    for identifier, _searched in candidates(s, items):
        if len(fetched) >= limit or listing_out_of_time():
            break
        data = cd.item(s, identifier)
        meta = data.get("metadata") or {}
        page_url = f"{ARCHIVE}details/{identifier}"
        kind, basis = film_kind(meta) if meta else ("", "not found on the Internet Archive")
        title_key = (cd.tidy_title(cd.text_of(meta.get("title"))).lower(), cd.year_of(meta))
        if kind and title_key in seen:
            kind, basis = "", "another copy of a film already used"
        name, _ = cd.film_file(data) if kind else ("", 0)
        if kind and not name:
            kind, basis = "", "no video copy small enough"
        if not kind:
            considered(identifier, page_url, basis)
            continue
        seen.add(title_key)
        folder = tempfile.mkdtemp(prefix="pd-film-")
        try:
            stills_folder = os.path.join(folder, "stills")
            os.makedirs(stills_folder)
            if shutil.which("ffmpeg"):
                video = os.path.join(folder, "film" + os.path.splitext(name)[1])
                url = f"{ARCHIVE}download/{quote(identifier)}/{quote(name)}"
                if not cd.download(s, url, video, cd.FILM_MOST_BYTES):
                    considered(identifier, url, "the film could not be downloaded")
                    continue
                stills, length = cd.ffmpeg_stills(video, stills_folder)
            else:
                url = page_url
                stills = thumbs(s, identifier, data, stills_folder)
                length = max([t for t, _ in stills] + [0.0]) + cd.SKIP_END + 1
            kept, left = cd.good_stills(stills, length, min(MOST_STILLS, limit - len(fetched)))
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        sentence = lead(meta, kind)
        about = re.sub(r"^.{0,120}?SUMMARY \(from the NPS AudioVideo record\)\s*", "", cd.film_description(meta))
        about = about if len(about.split()) >= 8 else ""
        words = " ".join([cd.text_of(meta.get("title")), cd.text_of(meta.get("description")),
                          cd.text_of(meta.get("subject"))])
        marks = {}
        if cd.GRAPHIC.search(words):
            marks["content"] = "graphic"
        elif cd.MEDICAL.search(words):
            marks["content"] = "medical"
        if cd.CHILD.search(words):
            marks["child"] = True
        credit = f"{cd.tidy_title(cd.text_of(meta.get('title')))}, Internet Archive {page_url}; {basis}"
        base = re.sub(r"[^a-z0-9]+", "_", identifier.lower()).strip("_")[:40]
        answer = sentence + (f" The film's catalogue record describes it: \"{about}\"" if about else "")
        for t, jpeg in kept:
            still = f"film_{base}_{t:07.1f}.jpg"
            if not about:
                needs_description(still, url, credit, basis, "open", title=cd.text_of(meta.get("title")),
                                  reason="the film's record has no description", extra={"lead": sentence,
                                  "seconds": round(t, 1), **marks}, page_url=f"{page_url}?start={int(t)}", data=jpeg)
                continue
            considered(still, url, "")
            rows = [dict({"question": q, "answer": answer, "credit": credit, "seconds": round(t, 1)}, **marks)
                    for q in (FROM_Q, FILM_Q)]
            fetched.append((still, jpeg, rows))
        say(f"  {identifier}: {len(kept)} stills" + (" (set aside: no description)" if not about else "") +
            (f"; left out: {', '.join(f'{v} {k}' for k, v in left.items())}" if left else ""))
    return with_twins(fetched[:limit])


FILM_STILLS_PACKS = {
    "pd_film_stills": (build_pd_film_stills,
                       "Stills from public-domain films on the Internet Archive (https://archive.org): Prelinger "
                       "Archives films carrying a public-domain mark, and National Park Service and NASA films (US "
                       "government works, 17 U.S.C. 105), each with its record's title, year, maker and description; "
                       "each film's basis is in its credit."),
}
FILM_STILLS_LIMITS = {"pd_film_stills": 2500}
FILM_STILLS_COMMONS_KEYS = ()


def main(argv=None):
    """Build the pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the public-domain film stills pack builder.")
    parser.add_argument("key", choices=sorted(FILM_STILLS_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--items", nargs="*", help="Internet Archive identifiers to read instead of searching")
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = build_pd_film_stills(args.limit, args.items)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
        if data and args.save:
            os.makedirs(args.save, exist_ok=True)
            with open(os.path.join(args.save, name), "wb") as f:
                f.write(data)
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
