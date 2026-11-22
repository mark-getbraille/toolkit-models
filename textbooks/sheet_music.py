"""Sheet music for the reference library (the owner's request of 2026-11-22), in its own group "Reference, sheet
music". Keys: sheet-music (every book), music:<name>. The owner is a braille transcriber, so every score says whether
the National Library Service for the Blind and Print Disabled (NLS) lists a braille edition of it.

What this module builds, in plain words:
  - the Mutopia Project's free scores (www.mutopiaproject.org), a curated set of well-known works (OPUS: Bach,
    Beethoven, Mozart, Chopin, Schubert, Handel, Vivaldi, Satie, Joplin, Debussy, Grieg, Schumann, Tchaikovsky,
    Brahms, Pachelbel, Clementi, Sor, Tarrega, Foster). Each score is one page: its facts from the score's own data
    file (title, composer, opus, instruments, style, the edition it was typeset from, the typesetter, the LilyPond
    version and the licence), the NLS note, the whole LilyPond source as text (LilyPond is a plain-text music language,
    so the score itself can be read and edited with a screen reader), and the score's files as downloadable originals
    (the PDF for A4 and for US Letter paper, the LilyPond source and the MIDI file). The licence is read from each
    score's data file at every build, and the scores go into one book per licence, so share-alike scores stay apart:
      music:mutopia_public_domain   scores Mutopia marks "Public Domain" (old music, and the typesetter's edition
                                    dedicated to the public domain)
      music:mutopia_cc_by           scores under Creative Commons Attribution (3.0 or 4.0; each page says which)
      music:mutopia_cc_by_sa        scores under Creative Commons Attribution-ShareAlike (2.5, 3.0 or 4.0)
    A score under any other licence is left out and said in the manifest;
  - music:nls_braille_music: the NLS Music Section's own catalogue pages (US government work): the braille piano score
    catalogue (four pages, composers A to Z), the organ and violin braille score catalogues, piano methods in braille,
    the holiday music catalogue, music appreciation and biographies, popular music lead sheets, music periodicals,
    opera librettos, materials by and about blind musicians, Music Notes from the Music Section and Circular No. 4 for
    braille music transcribers. (The Music Section's main page is in vision:nls_services and is not repeated.) The
    same piano, organ and violin catalogue pages are what each Mutopia page is checked against: the catalogue lines
    that name the work under its composer, with their BRM numbers, are quoted; when none match, the page says so and
    gives the NLS catalogue's address (the NLS online catalogue's robots.txt turns programs away, so it is never
    searched by this program);
  - music:index, "Sheet music and braille music: a guide to the library" (facts and links, CC0): the curated works by
    composer and by instrument, with each composer's IMSLP page as a link, the braille music resources (NLS, the Music
    Braille Code, Dancing Dots, the Library of Congress), and the music books already in the library by key.

Link-only (NOT_INCLUDED): IMSLP, the Petrucci Music Library (imslp.org): its scores are public domain in Canada but not
always elsewhere, and its robots.txt disallows the score files (/images/, /imglnks/, /wiki/File:, the download page
Special:ImagefromIndex) and its work and instrument listings; only its composer pages are named, as links. Dancing Dots
(GOODFEEL braille music software and its guides: copyright of Dancing Dots). The Music Braille Code 2015 (BANA:
copyright, already link-only in vision_living.py). The NLS piano catalogue's braille files (BRF) are not read (the same
catalogue is read from its web pages).

Musical instrument care and repair books are in instrument_care.py (instr:), music theory in games_hobbies.py; no
manuals category is added (instrument makers' manuals belong with instrument care).

Licences: Mutopia's legal page (www.mutopiaproject.org/legal.html) explains its three licence kinds; each score's own
data file (<name>.rdf, mp:licence) is read at every build; www.mutopiaproject.org/robots.txt allows all
("User-agent: * Disallow:"), no AI rules (checked 2026-11-22). The NLS pages: US government work (17 U.S.C. 105, the
line checked on govinfo.gov at every build); www.loc.gov/robots.txt allows /nls/ (Crawl-delay 5, kept).

Run from the repository's folder:
  python3 textbooks/sheet_music.py music:index --out build/textbooks
  python3 textbooks/sheet_music.py music:mutopia_public_domain --out build/textbooks --limit 5
"""

import html
import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "sheetmusic"
GROUPS = {GROUP: "Reference, sheet music"}

MUTOPIA = "https://www.mutopiaproject.org"
FTP = MUTOPIA + "/ftp/"
MUTOPIA_LEGAL = MUTOPIA + "/legal.html"
NLS_MUSIC = "https://www.loc.gov/nls/services-and-resources/music-service-and-materials/"
NLS_PIANO = "https://www.loc.gov/nls/braille-audio-reading-materials/music-materials/piano-scores-braille/"
NLS_CATALOGUES = [NLS_PIANO + p + "/" for p in ("braille-composers-aaron-czibulka", "braille-composers-dalmaine-ives",
                                                 "braille-composers-jacob-quilter",
                                                 "braille-composers-rachmaninoff-zuschneid")] + \
    [NLS_MUSIC + "organ-scores-braille/", NLS_MUSIC + "violin-scores-catalog/"]
NLS_CATALOGUE_SEARCH = "https://nlscatalog.loc.gov/"
IMSLP_CATEGORY = "https://imslp.org/wiki/Category:"
MAX_LY = 150_000                 # characters of LilyPond shown on a page; a longer source is a download only
MAX_PIECES = 30                  # scores read from one work's folder at most

SCORE_NOTE = ("Mutopia's scores are typeset by volunteers from old public-domain editions; check against another "
              "edition before you transcribe or perform from one.")

# The curated works: (Mutopia folder under /ftp/, composer as NLS lists it, composer as shown, the work, instrument
# family, a regular expression of how the NLS catalogues name the work, or "" when it is not looked for).
OPUS = [
    ("BachJS/BWV846", "Bach, Johann Sebastian", "Johann Sebastian Bach",
     "The Well-Tempered Clavier, Book I: Prelude and Fugue No. 1 in C major, BWV 846", "keyboard",
     r"wohltemperierte|well-tempered|BWV 846"),
    ("BachJS/BWV847", "Bach, Johann Sebastian", "Johann Sebastian Bach",
     "The Well-Tempered Clavier, Book I: Prelude and Fugue No. 2 in C minor, BWV 847", "keyboard",
     r"wohltemperierte|well-tempered|BWV 847"),
    ("BachJS/BWV772", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Invention No. 1 in C major, BWV 772",
     "keyboard", r"invention"),
    ("BachJS/BWV779", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Invention No. 8 in F major, BWV 779",
     "keyboard", r"invention"),
    ("BachJS/BWV784", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Invention No. 13 in A minor, BWV 784",
     "keyboard", r"invention"),
    ("BachJS/BWV939", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Little Prelude in C major, BWV 939",
     "keyboard", r"little prelude|kleine pr[aä]ludien"),
    ("BachJS/BWV971", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Italian Concerto, BWV 971", "keyboard",
     r"italian concerto|italienisches konzert|BWV 971"),
    ("BachJS/BWV565", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Toccata and Fugue in D minor, BWV 565",
     "organ", r"toccata.{0,12}fug|BWV 565"),
    ("BachJS/BWV582", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Passacaglia in C minor, BWV 582", "organ",
     r"passacaglia|BWV 582"),
    ("BachJS/BWV645", "Bach, Johann Sebastian", "Johann Sebastian Bach",
     "Wachet auf, ruft uns die Stimme (Schübler chorale), BWV 645", "organ", r"wachet auf|sch[uü]bler|BWV 645"),
    ("BachJS/BWV1007", "Bach, Johann Sebastian", "Johann Sebastian Bach", "Cello Suite No. 1 in G major, BWV 1007",
     "strings", r"cello suite|suites? for (solo )?(violon)?cello|BWV 1007"),
    ("BeethovenLv/O13", "Beethoven, Ludwig van", "Ludwig van Beethoven",
     "Piano Sonata No. 8 in C minor, \"Pathétique\", Op. 13", "keyboard", r"path[eé]tique|op\. ?13\b"),
    ("BeethovenLv/O27", "Beethoven, Ludwig van", "Ludwig van Beethoven",
     "Piano Sonata No. 14 in C-sharp minor, \"Moonlight\", Op. 27 No. 2", "keyboard", r"moonlight|op\. ?27"),
    ("BeethovenLv/O49", "Beethoven, Ludwig van", "Ludwig van Beethoven", "Two Easy Sonatas, Op. 49", "keyboard",
     r"op\. ?49"),
    ("BeethovenLv/WoO59", "Beethoven, Ludwig van", "Ludwig van Beethoven", "Für Elise, WoO 59", "keyboard",
     r"f[uü]r elise|WoO 59"),
    ("MozartWA/KV331", "Mozart, Wolfgang Amadeus", "Wolfgang Amadeus Mozart",
     "Piano Sonata in A major, K. 331 (with the Rondo alla Turca)", "keyboard", r"K\.? ?331|alla turca|turkish"),
    ("MozartWA/KV545", "Mozart, Wolfgang Amadeus", "Wolfgang Amadeus Mozart",
     "Piano Sonata in C major, K. 545 (\"Sonata facile\")", "keyboard", r"K\.? ?545|facile"),
    ("MozartWA/KV265", "Mozart, Wolfgang Amadeus", "Wolfgang Amadeus Mozart",
     "Twelve Variations on \"Ah vous dirai-je, Maman\", K. 265", "guitar", r"K\.? ?265|vous dirai"),
    ("MozartWA/KV525", "Mozart, Wolfgang Amadeus", "Wolfgang Amadeus Mozart", "Eine kleine Nachtmusik, K. 525",
     "strings", r"kleine nachtmusik|K\.? ?525"),
    ("MozartWA/KV622", "Mozart, Wolfgang Amadeus", "Wolfgang Amadeus Mozart", "Clarinet Concerto in A major, K. 622",
     "ensemble", ""),
    ("MozartWA/KV626", "Mozart, Wolfgang Amadeus", "Wolfgang Amadeus Mozart", "Requiem, K. 626", "voice",
     r"requiem"),
    ("ChopinFF/O28", "Chopin, Frédéric", "Frédéric Chopin", "Twenty-four Preludes, Op. 28", "keyboard",
     r"pr[eé]lud"),
    ("ChopinFF/O9", "Chopin, Frédéric", "Frédéric Chopin", "Three Nocturnes, Op. 9", "keyboard", r"nocturn"),
    ("ChopinFF/O64", "Chopin, Frédéric", "Frédéric Chopin", "Waltz in D-flat major, \"Minute\", Op. 64 No. 1",
     "keyboard", r"waltz|valse|minute"),
    ("ChopinFF/O66", "Chopin, Frédéric", "Frédéric Chopin", "Fantaisie-Impromptu, Op. 66", "keyboard",
     r"fantais|impromptu"),
    ("SchubertF/D899", "Schubert, Franz", "Franz Schubert", "Four Impromptus, D. 899 (Op. 90)", "keyboard",
     r"impromptu"),
    ("SchubertF/D780", "Schubert, Franz", "Franz Schubert", "Moments musicaux, D. 780 (Op. 94)", "keyboard",
     r"moments? musicaux"),
    ("SchubertF/D839", "Schubert, Franz", "Franz Schubert", "Ave Maria (Ellens dritter Gesang), D. 839", "voice",
     r"ave maria"),
    ("SchubertF/D911", "Schubert, Franz", "Franz Schubert", "Winterreise, D. 911: Einsamkeit", "voice",
     r"winterreise"),
    ("HandelGF/hallelujah", "Handel, George Frideric", "George Frideric Handel",
     "Hallelujah chorus from Messiah, HWV 56", "voice", r"messiah|hallelujah"),
    ("HandelGF/HWV56", "Handel, George Frideric", "George Frideric Handel", "Messiah, HWV 56", "voice",
     r"messiah"),
    ("VivaldiA/O8", "Vivaldi, Antonio", "Antonio Vivaldi", "The Four Seasons, Op. 8 Nos. 1 to 4", "strings",
     r"four seasons|stagioni|primavera|inverno"),
    ("SatieE/gymnopedie_1", "Satie, Erik", "Erik Satie", "Gymnopédie No. 1", "keyboard", r"gymnop"),
    ("SatieE/gymnopedie_2", "Satie, Erik", "Erik Satie", "Gymnopédie No. 2", "keyboard", r"gymnop"),
    ("SatieE/gymnopedie_3", "Satie, Erik", "Erik Satie", "Gymnopédie No. 3", "keyboard", r"gymnop"),
    ("SatieE/Gnossienne", "Satie, Erik", "Erik Satie", "Gnossiennes Nos. 1 to 3", "keyboard", r"gnossienne"),
    ("JoplinS/entertainer", "Joplin, Scott", "Scott Joplin", "The Entertainer", "keyboard", r"entertainer"),
    ("JoplinS/maple", "Joplin, Scott", "Scott Joplin", "Maple Leaf Rag", "keyboard", r"maple leaf"),
    ("JoplinS/solace", "Joplin, Scott", "Scott Joplin", "Solace", "keyboard", r"solace"),
    ("DebussyC/L75", "Debussy, Claude", "Claude Debussy", "Suite bergamasque: Clair de lune", "keyboard",
     r"clair de lune|bergamasque"),
    ("DebussyC/L66", "Debussy, Claude", "Claude Debussy", "Two Arabesques", "keyboard", r"arabesque"),
    ("GriegE/O46", "Grieg, Edvard", "Edvard Grieg", "Peer Gynt Suite No. 1, Op. 46", "keyboard",
     r"peer gynt|mountain king|bergk[oø]nig"),
    ("SchumannR/O15", "Schumann, Robert", "Robert Schumann", "Kinderszenen (Scenes from Childhood), Op. 15",
     "keyboard", r"kinderscenen|kinderszenen|scenes from childhood|tr[aä]umerei"),
    ("SchumannR/O68", "Schumann, Robert", "Robert Schumann", "Album for the Young, Op. 68", "keyboard",
     r"album f[uü]r die jugend|album for the young"),
    ("TchaikovskyPI/O39", "Tchaikovsky, Peter Ilich", "Pyotr Ilyich Tchaikovsky", "Album for the Young, Op. 39",
     "keyboard", r"album for the young|children'?s album|jugend"),
    ("BrahmsJ/LullabyBrahms-C", "Brahms, Johannes", "Johannes Brahms", "Lullaby (Wiegenlied), Op. 49 No. 4",
     "keyboard", r"lullaby|wiegenlied"),
    ("PachelbelJ/CanonInD", "Pachelbel, Johann", "Johann Pachelbel", "Canon in D", "strings", r"canon"),
    ("ClementiM/O36", "Clementi, Muzio", "Muzio Clementi", "Sonatinas, Op. 36", "keyboard", r"sonatina"),
    ("SorF/O60", "Sor, Fernando", "Fernando Sor", "Twenty-five Progressive Lessons, Op. 60", "guitar", ""),
    ("SorF/O35", "Sor, Fernando", "Fernando Sor", "Twenty-four Exercises (Studies), Op. 35", "guitar", ""),
    ("TarregaF/Alhambra", "Tárrega, Francisco", "Francisco Tárrega", "Recuerdos de la Alhambra", "guitar", ""),
    ("TarregaF/lagrima-duo", "Tárrega, Francisco", "Francisco Tárrega", "Lágrima (guitar duo)", "guitar", ""),
    ("TarregaF/adelita", "Tárrega, Francisco", "Francisco Tárrega", "Adelita", "guitar", ""),
    ("FosterSC/oldfolks", "Foster, Stephen Collins", "Stephen Foster", "Old Folks at Home", "voice",
     r"old folks"),
    ("FosterSC/hardtimes", "Foster, Stephen Collins", "Stephen Foster", "Hard Times Come Again No More", "voice",
     r"hard times"),
]
FAMILIES = {"keyboard": "Piano and keyboard", "organ": "Organ", "strings": "Strings", "guitar": "Guitar",
            "voice": "Voice and choir", "ensemble": "Orchestra and ensembles"}
COMPOSER_PAGES = {  # IMSLP's category page name of each composer (links only)
    "Johann Sebastian Bach": "Bach,_Johann_Sebastian", "Ludwig van Beethoven": "Beethoven,_Ludwig_van",
    "Wolfgang Amadeus Mozart": "Mozart,_Wolfgang_Amadeus", "Frédéric Chopin": "Chopin,_Frédéric",
    "Franz Schubert": "Schubert,_Franz", "George Frideric Handel": "Handel,_George_Frideric",
    "Antonio Vivaldi": "Vivaldi,_Antonio", "Erik Satie": "Satie,_Erik", "Scott Joplin": "Joplin,_Scott",
    "Claude Debussy": "Debussy,_Claude", "Edvard Grieg": "Grieg,_Edvard", "Robert Schumann": "Schumann,_Robert",
    "Pyotr Ilyich Tchaikovsky": "Tchaikovsky,_Pyotr", "Johannes Brahms": "Brahms,_Johannes",
    "Johann Pachelbel": "Pachelbel,_Johann", "Muzio Clementi": "Clementi,_Muzio", "Fernando Sor": "Sor,_Fernando",
    "Francisco Tárrega": "Tárrega,_Francisco", "Stephen Foster": "Foster,_Stephen_Collins",
}

# The three licence books: lane -> (key name, title, book licence, licence address, kind of score licence).
LANES = {
    "pd": ("mutopia_public_domain", "Mutopia scores: public domain", "Public domain (dedicated by its publisher)",
           MUTOPIA_LEGAL),
    "by": ("mutopia_cc_by", "Mutopia scores: Creative Commons Attribution", "CC BY",
           "https://creativecommons.org/licenses/by/4.0/"),
    "sa": ("mutopia_cc_by_sa", "Mutopia scores: Creative Commons Attribution-ShareAlike", "CC BY-SA",
           "https://creativecommons.org/licenses/by-sa/4.0/"),
}


# ====================================================================== reading Mutopia

def lane_of(licence):
    """The licence book a score's mp:licence puts it in: "pd", "by", "sa", or "" (left out)."""
    words = (licence or "").strip().lower()
    if words in ("public domain", "creative commons public domain"):
        return "pd"
    if re.fullmatch(r"creative commons attribution[- ]sharealike \d\.\d", words):
        return "sa"
    if re.fullmatch(r"creative commons attribution \d\.\d", words):
        return "by"
    return ""


def listing(url, cache=None):
    """The file and folder names of a Mutopia folder (its web server's index page), in order."""
    import build_textbooks as B
    text = B.fetch(url, cache)
    return [h for h in re.findall(r'href="([^"?/#][^"]*)"', text) if not h.startswith(("http", "mailto"))]


def rdf_fields(text):
    """{field: value} of a Mutopia data file (mp:title, mp:composer, mp:for, mp:licence ...)."""
    return {k: html.unescape(" ".join(v.split())) for k, v in re.findall(r"<mp:(\w+)>(.*?)</mp:\1>", text, re.S)}


def piece_folders(path, cache=None):
    """The score folders of one work's folder: the folder itself when it holds a data file (.rdf), else its
    subfolders that hold one (at most MAX_PIECES). Returns [(folder address, its file names)]."""
    url = FTP + path.strip("/") + "/"
    names = listing(url, cache)
    if any(n.endswith(".rdf") for n in names):
        return [(url, names)]
    out = []
    for sub in [n for n in names if n.endswith("/")][:MAX_PIECES]:
        try:
            files = listing(url + sub, cache)
        except urllib.error.HTTPError:
            continue
        if any(n.endswith(".rdf") for n in files):
            out.append((url + sub, files))
    return out


def read_scores(cache=None, left_out=None, opus=None, limit=None):
    """Every curated score: [{opus row fields, folder, files, rdf fields, lane}] (a score whose licence is not one of
    the three is left out, said in left_out). limit: stop after so many scores (a small test build)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    scores = []
    for path, nls_composer, composer, work, family, nls in (opus or OPUS):
        try:
            folders = piece_folders(path, cache)
        except (urllib.error.URLError, OSError) as e:
            left_out.append({"title": f"Mutopia: {work}", "reason": f"Its folder could not be read ({e})."})
            continue
        for folder, files in folders:
            rdf = next(n for n in files if n.endswith(".rdf"))
            fields = rdf_fields(B.fetch(folder + rdf, cache))
            lane = lane_of(fields.get("licence", ""))
            if not lane:
                left_out.append({"title": f"Mutopia: {fields.get('title', folder)}", "reason": "Its licence ("
                                 f"{fields.get('licence', 'none given')}) is not one this library builds."})
                continue
            scores.append(dict(path=path, nls_composer=nls_composer, composer=composer, work=work, family=family,
                               nls=nls, folder=folder, files=files, rdf=fields, lane=lane))
            if limit and len(scores) >= limit:
                return scores
    return scores


# ====================================================================== the NLS braille music catalogues

def catalogue_lines(text):
    """The lines of words of an NLS catalogue page (its <main> part, tags removed)."""
    m = re.search(r"<main\b.*?</main>", text, re.S)
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", m.group(0) if m else text, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", text))
    return [" ".join(line.split()) for line in text.splitlines() if line.strip()]


# A composer's heading in the NLS catalogues: "Bach, Johann Sebastian, 1685-1750" or "Grieg, Edvard" (names only,
# each word capitalised, an optional "van"/"de", and optional years).
HEADING = re.compile(r"^[A-Z][\w'.-]+(?: (?:van|von|de|di|da|del|le|la))?, [A-Z][a-zà-ÿ.]+"
                     r"(?: (?:[A-Z][a-zà-ÿ.]*|van|von|de|di|da|del))*(?:, [\d?]{4}-?[\d?]{0,4})?$")


def nls_matches(lines, composer, pattern, span=1500):
    """[(catalogue line, BRM number)] of the lines under a composer's heading (within span lines of it) that match
    pattern, each with the first BRM number on it or the next three lines ("" when none)."""
    if not pattern:
        return []
    found = []
    rule = re.compile(pattern, re.I)
    for i, line in enumerate(lines):
        if not line.startswith(composer):
            continue
        for j in range(i + 1, min(i + span, len(lines))):
            if HEADING.match(lines[j]) and not lines[j].startswith(composer.split(",")[0] + ","):
                break                                    # the next composer's heading
            if rule.search(lines[j]):
                brm = next((m.group(0) for k in range(j, min(j + 4, len(lines)))
                            for m in [re.search(r"\bBRM ?\d{4,6}\b", lines[k])] if m), "")
                found.append((lines[j], brm.replace(" ", "")))
    return list(dict.fromkeys(found))


def nls_catalogues(cache=None):
    """{catalogue address: its lines} of the NLS piano, organ and violin braille catalogues ({} for a page that
    cannot be read: then the pages say the check could not be made)."""
    import build_textbooks as B
    B.CRAWL_DELAY["www.loc.gov"] = max(B.CRAWL_DELAY.get("www.loc.gov", 0), 5)
    out = {}
    for url in NLS_CATALOGUES:
        try:
            if B.allowed_by_robots(url, cache):
                out[url] = catalogue_lines(B.fetch(url, cache))
        except (urllib.error.URLError, OSError):
            pass
    return out


def nls_note(score, catalogues):
    """The page's note on NLS braille editions (HTML)."""
    import build_textbooks as B
    if not score["nls"]:
        return ("<p>Braille editions: not looked for in the NLS piano, organ and violin catalogues (this work is "
                f'for another instrument). Search the NLS catalogue: <a href="{NLS_CATALOGUE_SEARCH}">'
                f"{NLS_CATALOGUE_SEARCH}</a>.</p>")
    if not catalogues:
        return ("<p>Braille editions: the NLS catalogues could not be read at this build. Search the NLS catalogue: "
                f'<a href="{NLS_CATALOGUE_SEARCH}">{NLS_CATALOGUE_SEARCH}</a>.</p>')
    rows = []
    for url, lines in catalogues.items():
        for line, brm in nls_matches(lines, score["nls_composer"], score["nls"]):
            rows.append(f"<li>{B.esc(line)}{' (' + B.esc(brm) + ')' if brm else ''}: "
                        f'<a href="{B.esc(url)}">{B.esc(url)}</a></li>')
    if rows:
        return ("<p>Braille editions: the NLS braille music catalogues list these entries under "
                f"{B.esc(score['nls_composer'])} that match this work (borrow them from the NLS Music Section; check "
                f"that the edition is the one you need):</p><ul>{''.join(rows[:12])}</ul>")
    return ("<p>Braille editions: no matching entry was found under "
            f"{B.esc(score['nls_composer'])} in the NLS piano, organ and violin braille catalogues read at this "
            "build (an entry may be named differently, or be in another catalogue). Search the NLS catalogue: "
            f'<a href="{NLS_CATALOGUE_SEARCH}">{NLS_CATALOGUE_SEARCH}</a>, or ask the NLS Music Section.</p>')


# ====================================================================== the books

def score_page(score, catalogues, cache=None):
    """One score's page (build_textbooks.Page) and its originals [{url, kind}]."""
    import build_textbooks as B
    f, folder = score["rdf"], score["folder"]
    facts = K.dl([("Title", f.get("title")), ("Composer", score["composer"]), ("Opus", f.get("opus")),
                  ("Lyricist", f.get("lyricist")), ("Arranger", f.get("arranger")), ("Instruments", f.get("for")),
                  ("Style", f.get("style")), ("Date of composition", f.get("date")),
                  ("Edition typeset from", f.get("source")), ("Typeset by", f.get("maintainer")),
                  ("LilyPond version", f.get("lilypondVersion")), ("Mutopia number", f.get("id")),
                  ("Licence", f.get("licence")), ("Mutopia folder", folder)])
    originals, links = [], []
    kinds = {".pdf": ("pdf", "PDF score"), ".ly": ("ly", "LilyPond source"), ".mid": ("midi", "MIDI file"),
             ".zip": ("zip", "zip file")}
    for name in score["files"]:
        ext = os.path.splitext(name)[1].lower()
        if ext in kinds and "preview" not in name:
            kind, words = kinds[ext]
            paper = " (A4 paper)" if "-a4" in name else " (US Letter paper)" if "-let" in name else ""
            originals.append({"url": folder + name, "kind": kind})
            links.append(f'<li><a href="{B.esc(folder + name)}">{B.esc(words + paper)}: {B.esc(name)}</a></li>')
    body = facts + nls_note(score, catalogues)
    if links:
        body += "<h2>Files</h2><ul>" + "".join(links) + "</ul>"
    ly = f.get("lyFile", "")
    if ly and ly in score["files"]:
        try:
            text = B.fetch(folder + ly, cache)
        except (urllib.error.URLError, OSError):
            text = ""
        if text and len(text) <= MAX_LY:
            body += ("<h2>The score as LilyPond text</h2><p>The whole score in LilyPond, a plain-text music "
                     f"language.</p><pre>{B.esc(text)}</pre>")
        elif text:
            body += f"<p>The LilyPond source is long ({len(text):,} characters): download it from the Files list.</p>"
    else:
        body += ("<p>This score's LilyPond source is in a separate zip file in its Mutopia folder (several files); "
                 "download it from there.</p>")
    title = f"{score['composer']}: {f.get('title') or score['work']}"
    page = B.Page(B.slug(f"{score['composer']} {f.get('title', '')} {folder.rstrip('/').rsplit('/', 1)[-1]}", 80),
                  title, body, 0, FAMILIES[score["family"]])
    return page, originals


def lane_book(lane):
    """(book function, sign function) of one licence book of Mutopia scores."""
    key_name, title, licence, licence_url = LANES[lane]

    def book_fn(name, work, cache=None, left_out=None, limit=None):
        """The book: every curated score of this licence, one page each, grouped by instrument family."""
        left_out = left_out if left_out is not None else []
        scores = [s for s in read_scores(cache, left_out, limit=(limit * 3 if limit else None)) if s["lane"] == lane]
        if limit:
            scores = scores[:limit]
        catalogues = nls_catalogues(cache)
        if not catalogues:
            left_out.append({"title": title, "reason": "The NLS catalogues could not be read; the pages say so."})
        notice = {"pd": "The scores in this book are marked \"Public Domain\" by the Mutopia Project: the music is "
                        "old and in the public domain, and the typesetter dedicated the edition to the public "
                        "domain.",
                  "by": "The scores in this book are under the Creative Commons Attribution licence (3.0 or 4.0, "
                        "each score's own version on its page): credit the Mutopia Project and the typesetter named "
                        "on the page.",
                  "sa": "The scores in this book are under the Creative Commons Attribution-ShareAlike licence (2.5, "
                        "3.0 or 4.0, each score's own version on its page): credit the Mutopia Project and the "
                        "typesetter named on the page, and share copies and changes under the same licence."}[lane]
        book = K.new_book(f"music_{key_name}", title, "Sheet music (scores and LilyPond sources)", GROUP,
                          "The Mutopia Project (volunteer typesetters)", licence, licence_url, MUTOPIA,
                          "Free scores of well-known works from the Mutopia Project: each score's facts, whether the "
                          "NLS lists a braille edition, the whole LilyPond source as text, and the PDF, LilyPond and "
                          "MIDI files to download.", f"{notice} {SCORE_NOTE}", country="International",
                          changes="each score's data, LilyPond source and file list made into a web page")
        order = list(FAMILIES)
        for score in sorted(scores, key=lambda s: (order.index(s["family"]), s["composer"], s["work"])):
            page, originals = score_page(score, catalogues, cache)
            book.pages.append(page)
            book.originals += originals
        book.published = ""
        return book

    def sign_fn(name):
        """The weekly sign: the curated list and the month (scores are revised now and then)."""
        import directory_sources as D
        return K.sha(OPUS, lane, D.month_token())

    return book_fn, sign_fn


def index_sections():
    """The index's sections (practical_index.index_maker): the works by composer, by instrument, braille music and
    the library's other music books."""
    by_composer = {}
    for path, _nls_composer, composer, work, family, _nls in OPUS:
        by_composer.setdefault(composer, []).append((work, family, path))
    sections = []
    for composer in sorted(by_composer, key=lambda c: c.split()[-1]):
        rows = [("link", f"{work} ({FAMILIES[family].lower()}), in the Mutopia books", f"{FTP}{path}/",
                 "the Mutopia folder of the score") for work, family, path in by_composer[composer]]
        rows.append(("link", f"IMSLP: {composer}'s page", IMSLP_CATEGORY + COMPOSER_PAGES[composer],
                     "IMSLP's scores are public domain in Canada but not always in other countries, and its robots.txt "
                     "turns programs away from the score files: open it in a browser"))
        sections.append((f"Composer: {composer}", "The curated works of this composer in the Mutopia books (request "
                         "word sheet-music), and the composer's page at IMSLP.", rows))
    by_family = {}
    for _path, _n, composer, work, family, _nls in OPUS:
        by_family.setdefault(family, []).append(f"{composer}, {work}")
    for family, works in by_family.items():
        sections.append((f"Instrument: {FAMILIES[family]}", "The curated works for these instruments: "
                         + "; ".join(works) + ".", [
                             ("key", "music:mutopia_public_domain", "Mutopia scores: public domain"),
                             ("key", "music:mutopia_cc_by", "Mutopia scores: Creative Commons Attribution"),
                             ("key", "music:mutopia_cc_by_sa", "Mutopia scores: Creative Commons Attribution-"
                                                               "ShareAlike")]))
    sections.append(("Braille music", "Braille music for blind musicians and transcribers.", [
        ("key", "music:nls_braille_music", "The NLS Music Section's braille music catalogues and transcriber "
                                           "circular"),
        ("key", "vision:nls_services", "The NLS's services, with its music service"),
        ("key", "pdf:braille_music_notation_1930", "Braille Music Notation (1930: an old code, out of date)"),
        ("link", "NLS Music Section", NLS_MUSIC, "US government; its pages are in music:nls_braille_music"),
        ("link", "Music Braille Code 2015 (BANA)", "https://brailleauthority.org/music-braille-code",
         "copyright of BANA: free to read, not repackaged"),
        ("link", "Dancing Dots (GOODFEEL braille music translation software)", "https://www.dancingdots.com/",
         "copyright of Dancing Dots: link only"),
        ("link", "NFB music braille transcribing certification", "https://nfb.org/programs-services/braille-"
         "certification/music-braille-transcribing", "copyright of the NFB: link only"),
        ("link", "Library of Congress Performing Arts reading room", "https://www.loc.gov/rr/perform/",
         "the Library of Congress's music collections: open it in a browser")]))
    sections.append(("More music in the library", "Music theory, history and instrument care.", [
        ("key", "games:prout_harmony_1889", "Harmony: Its Theory and Practice (Prout, 1889)"),
        ("key", "games:goetschius_melody_writing_1900", "Exercises in Melody-Writing (Goetschius, 1900)"),
        ("key", "lit:stanford_forsyth_history_of_music", "A History of Music (Stanford and Forsyth)"),
        ("key", "lit:krehbiel_how_to_listen", "How to Listen to Music (Krehbiel)"),
        ("word", "instrument-care", "Piano tuning and violin making books (instrument care)"),
        ("word", "stack-exchange", "Music: Practice and Theory questions and answers (Kiwix, reference only, not for "
                                   "AI training)")]))
    return sections


INDEX = X.index_maker("music", GROUP, "Sheet music and braille music: a guide to the library",
                      "Sheet music and braille music", "A guide to the free scores in the library by composer and by "
                      "instrument, the braille music resources, and the links to IMSLP.", index_sections(),
                      country="International")

NLS_PAGES = [NLS_PIANO] + NLS_CATALOGUES + [NLS_MUSIC + p + "/" for p in (
    "piano-methods-braille", "holiday-music-catalog", "music-appreciation", "music-biographies",
    "popular-music-lead-sheets-sequential-list-issue", "circular-no-5-music-periodicals-available-nls",
    "circular-no-16-opera-librettos", "nls-music-section-materials-created-by-about-blind-and-visually-impaired-"
    "musicians", "music-notes-from-the-music-section", "circular-no-4-braille-music-transcribers")]
GUIDES = [X.page_list_book(
    GROUP, "nls_braille_music", "NLS braille music catalogues and the Music Section's guides",
    "Braille music", "National Library Service for the Blind and Print Disabled (NLS), Library of Congress", NLS_PAGES,
    r"^https://www\.loc\.gov/nls/(braille-audio-reading-materials/music-materials|services-and-resources/"
    r"music-service-and-materials)/[a-z0-9/-]+$",
    "The NLS Music Section's catalogues of braille music scores (piano, organ and violin, with their BRM numbers), "
    "piano methods in braille, the holiday music catalogue, music appreciation and biographies, popular music lead "
    "sheets, music periodicals, opera librettos, materials by and about blind musicians, Music Notes and Circular "
    "No. 4 for braille music transcribers.",
    "From the National Library Service for the Blind and Print Disabled, Library of Congress: a work of the US "
    "government (public domain). The scores themselves are lent by the NLS Music Section to eligible readers; ask "
    "the Music Section for the current list.",
    units=[(r"piano-scores|braille-composers", "Piano scores in braille"), (r"organ|violin", "Organ and violin"),
           (r"transcribers", "For transcribers"), (r".", "Other catalogues and guides")],
    version="www.loc.gov/nls music pages")]

MAKERS = {"index": INDEX, **{LANES[lane][0]: lane_book(lane) for lane in LANES}}
COLLECTION = K.Collection("music", GROUP, guides=GUIDES, makers=MAKERS, words={
    "sheet-music": lambda: ["music:index", "music:nls_braille_music"] + [f"music:{LANES[x][0]}" for x in LANES]})

LICENCE_LINES = {
    "music_mutopia": "Mutopia Project: each score's data file (<name>.rdf, mp:licence: \"Public Domain\", \"Creative "
                     "Commons Attribution 3.0/4.0\" or \"Creative Commons Attribution-ShareAlike 2.5/3.0/4.0\") read "
                     "at every build; www.mutopiaproject.org/legal.html explains the three; robots.txt \"User-agent: "
                     "* Disallow:\" (all allowed), no AI rules (checked 2026-11-22).",
    "music_nls": "www.loc.gov/nls music pages: works of the US government (17 U.S.C. 105, checked on govinfo.gov at "
                 "every build); robots.txt allows /nls/ (Crawl-delay 5, kept). The NLS online catalogue "
                 "(search.nlscatalog.loc.gov) robots.txt: \"Disallow: /\", so it is never searched.",
    "music_index": "The index (music:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("IMSLP, the Petrucci Music Library (imslp.org)", "Its scores are public domain in Canada but not always in the "
     "US or Europe, and its robots.txt disallows the score files (/images/, /imglnks/, /wiki/File:, "
     "Special:ImagefromIndex) and its /works, /instruments and /library listings (Crawl-delay 2); it asks automated "
     "readers not to download. Only each curated composer's page is named in music:index, as a link. Index: "
     "https://imslp.org/wiki/Main_Page"),
    ("Dancing Dots (GOODFEEL braille music software, guides)", "Copyright of Dancing Dots; link-only from "
     "music:index. Index: https://www.dancingdots.com/"),
    ("NLS online catalogue searches (nlscatalog.loc.gov)", "Its robots.txt says \"Disallow: /\" to every program, "
     "so it is never searched; the NLS's own catalogue web pages (piano, organ, violin) are read instead and each "
     "score says what they list. Index: https://nlscatalog.loc.gov/"),
    ("NLS piano catalogue braille files (Braille-Scores-Piano1.brf ...)", "The same catalogue is read from its web "
     "pages (music:nls_braille_music). Index: https://www.loc.gov/nls/services-and-resources/music-service-and-"
     "materials/piano-scores-braille/"),
    ("A manuals category for instruments and notation", "Not added: instrument makers' manuals belong with "
     "instrument care (instr:, manuals of instrument care), and notation is in the books here. Index: "
     "https://www.mutopiaproject.org/browse.html"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
