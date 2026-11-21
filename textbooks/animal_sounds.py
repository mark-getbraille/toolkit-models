"""Animal sounds: a reference book of North American animal calls, as text with the recordings (textbooks release).

Why a reference book and not a training collection: the picture describer cannot hear, so a recording teaches it
nothing. What helps a blind person is a page per animal that says, in words, what its call sounds like, and a link to
an open recording to listen to. A future audio model would need thousands of recordings per species under licences
that allow training; the open ones are far too few (below), so no kit dataset is made now.

Where the pages come from (checked by hand on 2026-11-21):
  NPS Sound Gallery (www.nps.gov/subjects/sound/gallery.htm, US National Park Service)   recordings made in national
      parks, each on a page of its own with the park, a caption, the credit and a written "Audio Transcript" that
      describes the sound ("The loud screeching, groaning sounds of elks bugling."). The gallery says "The files are
      in the public domain and may be downloaded." robots.txt allows /subjects/ (checked again for every page);
      its Crawl-delay of 5 seconds is written for bingbot only, but the builder keeps it too (NPS_PACE), so about
      45 pages take four minutes. Only the animal groups are
      used (amphibians, birds, insects, mammals, reptiles, and the chickens of the cultural-historical group); the
      machine, weather, water and music sounds are not. The book holds the page's own words, the recording itself
      (its MP3 file, copied into the book: the gallery says the files are in the public domain and may be
      downloaded; changed on 2026-11-21 from links only, the reference-library audit) and the address of the
      original MP3 file. A recording larger than MAX_MP3 bytes, or one robots.txt does not allow, stays a link.

Looked at and not used (NOT_INCLUDED says why): xeno-canto (its robots.txt shuts out AI crawlers by name, and most
recordings are CC BY-NC-SA), the Macaulay Library (contributors keep the copyright; reuse needs permission), Freesound
(robots.txt disallows its API to robots; each file its own licence), and the USFWS and USGS sites (public domain, but
no species-indexed list of recordings a program can read was found).

Key: "sounds" (one book, nps_animal_sounds). Run from the repository's folder:
    python3 textbooks/build_textbooks.py sounds --out build/textbooks
"""

import html
import re
import urllib.parse

import build_textbooks as B

GALLERY = "https://www.nps.gov/subjects/sound/gallery.htm"
NPS_PACE = 5.0                   # seconds between two requests to www.nps.gov (its robots.txt asks bingbot for this)
NPS_SITE = "https://www.nps.gov"
MAX_MP3 = 15_000_000             # bytes: a larger recording stays a link only (a guard against a long file)
ANIMAL_GROUPS = ("Amphibians", "Birds", "Insects", "Mammals", "Reptiles")
# Animal pages filed under another group of the gallery: {page path: the group it goes in}.
ANIMAL_EXTRAS = {"/subjects/sound/sounds-chickens.htm": "Birds"}
LICENCE_LINE = ("NPS Sound Gallery (https://www.nps.gov/subjects/sound/gallery.htm, read 2026-11-21): \"The files "
                "are in the public domain and may be downloaded.\" The gallery asks users to give the appropriate "
                "credit, which every page of the book does.")
NOT_INCLUDED = [
    ("xeno-canto (xeno-canto.org)", "Its robots.txt shuts out AI crawlers by name (anthropic-ai, ClaudeBot, GPTBot "
     "and others), and most of its recordings are CC BY-NC-SA, so it is not read at all."),
    ("Macaulay Library (Cornell Lab of Ornithology)", "Not openly licensed: contributors keep the copyright and "
     "reuse needs permission (eBird and Macaulay Library help pages)."),
    ("Freesound (freesound.org)", "Each file has its own Creative Commons licence, but robots.txt disallows /api/ "
     "and /apiv2/ to robots, so no program reads it."),
    ("US Fish and Wildlife Service and US Geological Survey sites", "Public domain, but no species-indexed list of "
     "recordings that a program can read was found; recordings of theirs that are on Wikimedia Commons could be "
     "added later."),
    ("Yellowstone and Glacier Bay sound libraries (nps.gov park pages)", "Public domain like the gallery, but laid "
     "out differently on each park's site; not read in this first version."),
]


def text_of(fragment):
    """Plain text of an HTML fragment: tags dropped, entities read, spaces tidied."""
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment or "", flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text).strip()


def gallery_links(page):
    """[(group, page address)] of the gallery's animal sound pages, in the gallery's order: the links after each
    group heading ("<strong>Birds</strong>"), only for the animal groups, plus ANIMAL_EXTRAS."""
    out, group = [], ""
    for m in re.finditer(r"<strong>\s*([^<]+?)\s*</strong>|href=\"([^\"]+\.htm)\"", page):
        if m.group(1):
            group = m.group(1).strip()
            continue
        path = urllib.parse.urlsplit(urllib.parse.urljoin(NPS_SITE, m.group(2))).path
        if not path.startswith("/subjects/sound/") or path.endswith(("gallery.htm", "siteindex.htm",
                                                                      "contactus.htm", "events.htm")):
            continue
        place = ANIMAL_EXTRAS.get(path) or (group if group in ANIMAL_GROUPS else "")
        if place and (place, NPS_SITE + path) not in out:
            out.append((place, NPS_SITE + path))
    return out


def sound_page(page, url):
    """What one gallery page says: {"title", "caption", "description", "credit", "transcript", "mp3s", "url"}, or
    None when it has no MP3 recording. The description, credit and transcript are the lines that follow the player
    ("Sound recording of bugling elk, Great Sand Dunes ...", "Credit / Author:", "Audio Transcript")."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    title = re.sub(r"^Sound Gallery\s*[-–:]\s*", "", text_of(h1.group(1) if h1 else ""), flags=re.I)
    mp3s = list(dict.fromkeys(urllib.parse.urljoin(url, m) for m in
                              re.findall(r"<source[^>]+src=\"([^\"]+\.mp3)\"", page, re.I)))
    if not title or not mp3s:
        return None
    caption = ""
    fig = re.search(r"<figcaption>(.*?)</figcaption>", page, re.S)
    if fig:
        caption = text_of(re.sub(r"<p class=\"figcredit\">.*?</p>", "", fig.group(1), flags=re.S))
    after = page[page.find("</audio>"):]
    stop = re.search(r"Listen to more|Last updated", after)
    lines = [text_of(x) for x in re.split(r"<(?:/?p|/?div|br|/h\d|h\d)[^>]*>", after[:stop.start() if stop else None])]
    lines = [x for x in lines if x]
    description = lines[0] if lines and not lines[0].lower().startswith(("credit", "audio transcript")) else ""
    credit = transcript = ""
    for i, line in enumerate(lines):
        if line.lower().startswith("credit") and not credit:
            rest = re.sub(r"^credit\s*/\s*author:?\s*", "", line, flags=re.I)
            credit = rest or (lines[i + 1] if i + 1 < len(lines) else "")
        if line.lower().startswith("audio transcript") and not transcript:
            rest = re.sub(r"^audio transcript:?\s*", "", line, flags=re.I)
            transcript = rest or (lines[i + 1] if i + 1 < len(lines) else "")
    return {"title": title, "caption": caption, "description": description, "credit": credit or "NPS",
            "transcript": transcript, "mp3s": mp3s, "url": url}


def page_body(sound, copies=None):
    """The body of one animal's page: what the sound is like (the transcript), the caption and description, the
    credit, the recordings copied into the book (copies: {MP3 address: path in the book}, played with an <audio>
    player), and the links to the original MP3 files and to the original page."""
    esc = B.esc
    copies = copies or {}
    out = []
    if sound["transcript"]:
        out.append(f"<p>What it sounds like: {esc(sound['transcript'])}</p>")
    for text in (sound["caption"], sound["description"]):
        if text and text != sound["transcript"]:
            out.append(f"<p>{esc(text)}</p>")
    links = "".join(f'<li><a href="{esc(m)}">Listen: {esc(sound["title"])}'
                    f'{f" ({i})" if len(sound["mp3s"]) > 1 else ""}</a> (MP3 sound file, public domain)</li>'
                    for i, m in enumerate(sound["mp3s"], 1))
    players = "".join(f'<p><audio controls src="{esc(copies[m])}">Recording: {esc(sound["title"])}</audio></p>'
                      for m in sound["mp3s"] if m in copies)
    out.append(f"<h2>Recording</h2>{players}<ul>{links}</ul>")
    out.append(f'<p>Credit: {esc(sound["credit"])}, US National Park Service. Original page: '
               f'<a href="{esc(sound["url"])}">{esc(sound["url"])}</a>.</p>')
    return "\n".join(out)


def about_body():
    """The "About this book" page: what it is, how to use it, where it comes from, and what was left out."""
    left = "".join(f"<li>{B.esc(name)}: {B.esc(why)}</li>" for name, why in NOT_INCLUDED)
    return ("<p>Animal calls recorded in US national parks, one page per recording, grouped by kind of animal. Each "
            "page says in words what the sound is like (the Park Service's own audio transcript), holds the "
            "recording itself to play, and links to the original recording.</p>"
            f"<p>{B.esc(LICENCE_LINE)}</p>"
            f"<h2>Not in this book</h2><ul>{left}</ul>")


def recording(url, cache=None, left_out=None):
    """The bytes of one MP3 recording (public domain, "may be downloaded"), or None when robots.txt does not allow
    it, it cannot be read, it is not an MP3 or it is larger than MAX_MP3 (then the page keeps only its link, and
    left_out says why)."""
    left_out = left_out if left_out is not None else []
    if not B.allowed_by_robots(url, cache):
        left_out.append({"title": url, "reason": "robots.txt does not allow the recording; linked only."})
        return None
    try:
        data = B.fetch(url, cache, binary=True)
    except Exception as e:  # noqa: BLE001 - the page keeps its link
        left_out.append({"title": url, "reason": f"The recording could not be read ({e}); linked only."})
        return None
    is_mp3 = isinstance(data, bytes) and (data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"))
    if not is_mp3 or len(data) > MAX_MP3:
        left_out.append({"title": url, "reason": "The recording is not an MP3 file or is too large; linked only."})
        return None
    return data


def nps_book(cache=None, left_out=None):
    """The book "Animal sounds of US national parks" from the NPS Sound Gallery (robots.txt checked for every page;
    a page that cannot be read is listed in left_out)."""
    left_out = left_out if left_out is not None else []
    if not B.allowed_by_robots(GALLERY, cache):
        left_out.append({"title": "NPS Sound Gallery", "reason": "robots.txt does not allow it now."})
        return None
    book = B.Book(name="nps_animal_sounds", title="Animal sounds of US national parks", subject="Animal sounds",
                  level="reference", group="science", publisher="US National Park Service (Natural Sounds)",
                  country="United States", licence=B.sources.US_GOV, licence_url=GALLERY, source=GALLERY,
                  description="North American animal calls recorded in national parks (birds, mammals, frogs and "
                              "toads, insects, alligators): what each sounds like in words, with the recording to "
                              "listen to.",
                  changes="the animal pages of the gallery made into one book: each page's caption, description, "
                          "credit and audio transcript, with the recordings (copied unchanged) and links to them")
    B.CRAWL_DELAY["www.nps.gov"] = max(B.CRAWL_DELAY.get("www.nps.gov", 0), NPS_PACE)
    pages, by_group = [], {}
    for group, url in gallery_links(B.fetch(GALLERY, cache)):
        if not B.allowed_by_robots(url, cache):
            left_out.append({"title": url, "reason": "robots.txt does not allow it."})
            continue
        try:
            sound = sound_page(B.fetch(url, cache), url)
        except Exception as e:  # noqa: BLE001 - one page's failure does not stop the others
            left_out.append({"title": url, "reason": f"It could not be read ({e})."})
            continue
        if sound is None:
            left_out.append({"title": url, "reason": "No recording on the page."})
            continue
        by_group.setdefault(group, []).append(sound)
    used = {"index", "about-this-book", "style-css"}
    for group in ANIMAL_GROUPS:
        for sound in sorted(by_group.get(group, []), key=lambda s: s["title"].casefold()):
            path = B.slug(sound["title"])
            while path in used:
                path += "-2"
            used.add(path)
            copies = {}
            for k, mp3 in enumerate(sound["mp3s"], 1):
                book.originals.append({"url": mp3, "kind": "mp3"})
                data = recording(mp3, cache, left_out)
                if data:
                    media = f"media/{path}{f'-{k}' if k > 1 else ''}.mp3"
                    book.resources[media] = (data, "audio/mpeg")
                    copies[mp3] = media
            book.originals.append({"url": sound["url"], "kind": "html"})
            pages.append(B.Page(path, sound["title"], page_body(sound, copies), 0, group))
    book.pages = [B.Page("about-this-book", "About this book", about_body())] + pages if pages else []
    return book
