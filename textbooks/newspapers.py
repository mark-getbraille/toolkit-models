"""Historical newspapers for the reference library (the owner's request of 2026-11-22), in their own group "Reference,
historical newspapers": a curated selection from the Library of Congress's Chronicling America (digitized US
newspapers, 1770 to 1963, with the machine-read OCR text of every page). Keys: newspapers (every book),
newspapers-front (the index and the front pages book), news:<name>, news:state:<state>.

Chronicling America is huge (over 20 million pages), so only a selection is built, around major events (EVENTS):
  - news:front_pages, "Front pages of history": for each event, the front page (page 1) of several newspapers from
    different states printed in the days after it, each page with the newspaper's title, the date, the Library of
    Congress page address and the whole OCR text;
  - news:state:<state>, one book per state (and the District of Columbia): for each event, up to two of that state's
    newspapers printed in the days after it, their first four pages with title, date, address and OCR text;
  - news:index, "Historical newspapers: a guide" (facts and links, CC0): the events and the books, why newspapers
    after 1930 are links only, how to fetch more (the loc.gov search address of every event and state, for Program
    Downloader; its API and rate limits), and where the complete collection is: the writing kit's source
    american_stories_newspapers and Hugging Face (dell-research-harvard/AmericanStories, Harvard's American Stories
    dataset of the whole of Chronicling America), which are not rebuilt as books here.
The existing pub:chronicling_america:<state>-<decade> pieces (periodicals.py: one issue a month of one state and
decade) stay as they are; this module is the event-centred selection.

Copyright: the Library of Congress's rights statement (on every issue) says "Newspapers published in the United
States more than 95 years ago are in the public domain in their entirety", and that newer ones "are also believed to
be in the public domain, but may contain some copyrighted third party materials" and that "Responsibility for making
an independent legal assessment of an item ... rests with persons desiring to use the item". Following the library's
rule (works of 1931 to 1963 only with evidence of no renewal), only issues published more than 95 years ago (before
1931 in 2026) are built, and each must carry that rights statement; the events of 1931 to 1963 (Pearl Harbor, D-Day,
V-E and V-J Day, the Kennedy assassination ...) are links only in the index, with their loc.gov search addresses.

OCR errors are expected: every book and page says that the text was machine-read from old, often damaged pages and
has many mistakes (wrong letters, run-together columns, advertisements mixed in), and that the page image at the
address is the true record. Old newspapers also print the language and views of their time, some of them offensive.

Polite reading: loc.gov's API documentation asks for about 20 searches a minute at most (it answers 429 and blocks
for a while when asked too fast), and its robots.txt asks Crawl-delay 5: every request here waits LOC_PAUSE seconds,
and a 429 stops the book at once (keeping what was read and saying so in left_out). robots.txt allows /collections/
and /resource/ (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/newspapers.py news:index --out build/textbooks
  python3 textbooks/newspapers.py news:state:vermont --out build/textbooks --limit 3
"""

import datetime
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "newspapers"
GROUPS = {GROUP: "Reference, historical newspapers"}

LOC = "https://www.loc.gov"
SEARCH = LOC + "/collections/chronicling-america/"
RIGHTS = "https://www.loc.gov/collections/chronicling-america/about-this-collection/rights-and-access/"
API_DOCS = "https://www.loc.gov/apis/json-and-yaml/"
LOC_PAUSE = 5.0                  # seconds between two loc.gov requests (robots.txt Crawl-delay 5)
LICENCE = "Public domain (published before 1931)"
LICENCE_URL = RIGHTS
FRONT_PER_EVENT = 6              # front pages per event in news:front_pages
STATE_ISSUES = 2                 # issues per event in a state book
STATE_PAGES = 4                  # pages read of each of those issues
AMERICAN_STORIES = "https://huggingface.co/datasets/dell-research-harvard/AmericanStories"

OCR_NOTE = ("The text was machine-read (OCR) from old, often damaged newspaper pages: expect many mistakes (wrong "
            "letters and words, columns run together, advertisements mixed into stories). The page image at the "
            "Library of Congress address is the true record. Old newspapers print the language and views of their "
            "time, and some of it is offensive.")
NOTICE = ("From Chronicling America (Library of Congress and the National Digital Newspaper Program). The Library of "
          "Congress believes that the newspapers in Chronicling America are in the public domain or have no known "
          "copyright restrictions; newspapers published in the United States more than 95 years ago are in the "
          "public domain in their entirety, and only those are kept here. " + OCR_NOTE)

# The events: (id, title, first day, last day). The days after an event, when the news was printed.
EVENTS = [
    ("lee-surrender-1865", "Lee's surrender at Appomattox (9 April 1865)", "1865-04-10", "1865-04-14"),
    ("lincoln-1865", "The assassination of President Lincoln (14 April 1865)", "1865-04-15", "1865-04-21"),
    ("golden-spike-1869", "The first transcontinental railroad is completed (10 May 1869)", "1869-05-11",
     "1869-05-15"),
    ("chicago-fire-1871", "The Great Chicago Fire (8 to 10 October 1871)", "1871-10-10", "1871-10-16"),
    ("garfield-1881", "The death of President Garfield (19 September 1881)", "1881-09-20", "1881-09-24"),
    ("johnstown-flood-1889", "The Johnstown Flood (31 May 1889)", "1889-06-01", "1889-06-06"),
    ("maine-1898", "The sinking of the USS Maine (15 February 1898)", "1898-02-16", "1898-02-21"),
    ("mckinley-1901", "The assassination of President McKinley (shot 6 September 1901)", "1901-09-07",
     "1901-09-16"),
    ("wright-1903", "The Wright brothers' first flights (17 December 1903)", "1903-12-18", "1903-12-24"),
    ("san-francisco-1906", "The San Francisco earthquake and fire (18 April 1906)", "1906-04-18", "1906-04-24"),
    ("titanic-1912", "The sinking of the Titanic (15 April 1912)", "1912-04-15", "1912-04-20"),
    ("war-1917", "The United States enters the First World War (6 April 1917)", "1917-04-06", "1917-04-10"),
    ("armistice-1918", "The Armistice ends the First World War (11 November 1918)", "1918-11-11", "1918-11-15"),
    ("influenza-1918", "The influenza pandemic in the United States (October 1918)", "1918-10-10", "1918-10-14"),
    ("suffrage-1920", "Women win the vote: the 19th Amendment (26 August 1920)", "1920-08-26", "1920-08-31"),
    ("lindbergh-1927", "Lindbergh flies the Atlantic alone (21 May 1927)", "1927-05-21", "1927-05-25"),
    ("crash-1929", "The stock market crash (24 to 29 October 1929)", "1929-10-24", "1929-10-31"),
]
# Events after 1930: links only (see the module docstring).
LATER_EVENTS = [
    ("hindenburg-1937", "The Hindenburg disaster (6 May 1937)", "1937-05-07", "1937-05-10"),
    ("pearl-harbor-1941", "The attack on Pearl Harbor (7 December 1941)", "1941-12-07", "1941-12-10"),
    ("d-day-1944", "D-Day: the Normandy landings (6 June 1944)", "1944-06-06", "1944-06-09"),
    ("ve-day-1945", "Victory in Europe (8 May 1945)", "1945-05-07", "1945-05-10"),
    ("vj-day-1945", "Victory over Japan (14 and 15 August 1945)", "1945-08-14", "1945-08-17"),
    ("brown-1954", "Brown v. Board of Education (17 May 1954)", "1954-05-17", "1954-05-20"),
    ("sputnik-1957", "Sputnik (4 October 1957)", "1957-10-05", "1957-10-08"),
    ("kennedy-1963", "The assassination of President Kennedy (22 November 1963)", "1963-11-22", "1963-11-26"),
]
STATES = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
          "district of columbia", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas",
          "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
          "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
          "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
          "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington",
          "west virginia", "wisconsin", "wyoming"]


def piece(state):
    """A state's key piece ("new york" -> "new-york")."""
    return state.replace(" ", "-")


def last_year(today=None):
    """The last year whose newspapers are built: published more than 95 years ago."""
    return (today or datetime.date.today()).year - 96


def search_url(start, end, state="", count=50):
    """The loc.gov API address of the English-language issues printed between two days (in one state)."""
    facets = "language:english" + (f"|location_state:{state}" if state else "")
    query = urllib.parse.urlencode({"fa": facets, "dates": f"{start}/{end}", "fo": "json", "c": count,
                                    "at": "results,pagination"})
    return f"{SEARCH}?{query}"


def browse_url(start, end, state=""):
    """The loc.gov search page of the same issues (for a browser or Program Downloader)."""
    facets = "language:english" + (f"|location_state:{state}" if state else "")
    return f"{SEARCH}?" + urllib.parse.urlencode({"fa": facets, "dates": f"{start}/{end}"})


class SlowDown(Exception):
    """loc.gov answered 429 (too many requests): stop and keep what was read."""


def loc_json(url, cache=None):
    """The JSON answer of a loc.gov address, read politely (LOC_PAUSE between requests); SlowDown on 429; an answer
    cut off on the way is asked for again (three tries)."""
    import build_textbooks as B
    for host in ("www.loc.gov", "tile.loc.gov"):
        B.CRAWL_DELAY[host] = max(B.CRAWL_DELAY.get(host, 0), LOC_PAUSE)
    for attempt in range(3):
        try:
            return json.loads(B.fetch(url, cache))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise SlowDown() from e
            raise
        except http.client.HTTPException:             # an answer cut off on the way (IncompleteRead): try again
            if attempt == 2:
                raise
            time.sleep(LOC_PAUSE * (attempt + 2))


def issues(start, end, state="", cache=None):
    """The issues printed between two days (in one state), as [{title, date, issue address, state}], one per
    newspaper title, in the order loc.gov gives (the answers list the newspapers themselves first: those have no
    day in their date and are skipped)."""
    answer = loc_json(search_url(start, end, state), cache)
    out, titles = [], set()
    for r in answer.get("results", []):
        when = r.get("date", "")
        resource = ((r.get("resources") or [{}])[0].get("url") or "").split("?")[0]
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", when) or not resource:
            continue
        name = re.sub(r",\s*[A-Z][a-z]+ \d{1,2}, \d{4}$", "", r.get("title", "")).strip()
        if name in titles:
            continue
        titles.add(name)
        states = r.get("location_state") or [state]
        out.append({"title": r.get("title", name), "newspaper": name, "date": when, "issue": resource,
                    "state": (states[0] if states else state).title()})
    return out


def page_text(issue, number, cache=None):
    """(OCR text, page address, total pages, rights statement) of one page of an issue."""
    res = loc_json(f"{issue}?sp={number}&fo=json", cache)
    total = int((res.get("pagination") or {}).get("total") or 1)
    rights = " ".join((res.get("item") or {}).get("rights") or [])
    full = (res.get("resource") or {}).get("fulltext_file")
    text = ""
    if full:
        ocr = loc_json(full, cache)
        text = next(iter(ocr.values()), {}).get("full_text", "") if isinstance(ocr, dict) and ocr else ""
    return text, f"{issue}?sp={number}", total, rights


def pages_html(found, event_title, pages, cache=None, left_out=None):
    """The HTML of some issues' pages ([(issue, pages read)]) under one event; issues whose rights statement does not
    say public domain, or that are too new, are left out (said in left_out)."""
    import build_textbooks as B
    import periodicals
    left_out = left_out if left_out is not None else []
    body = []
    for issue in found:
        if int(issue["date"][:4]) > last_year():
            left_out.append({"title": issue["title"], "reason": "Published less than 95 years ago: link only."})
            continue
        parts, number, total, rights = [], 1, 1, ""
        while number <= min(total, pages):
            try:
                text, address, total, rights_here = page_text(issue["issue"], number, cache)
            except (http.client.HTTPException, urllib.error.URLError, OSError, ValueError):
                left_out.append({"title": f"{issue['title']}, page {number}", "reason": "It could not be read "
                                 "(the answer was cut off); the issue keeps the pages read before it."})
                break
            rights = rights or rights_here
            parts.append(f'<h3>Page {number}</h3><p>Address: <a href="{B.esc(address)}">{B.esc(address)}</a></p>'
                         + (periodicals.ocr_html(text) or "<p>(No machine-read text for this page.)</p>"))
            number += 1
        if not re.search(r"public domain", rights, re.I):
            left_out.append({"title": issue["title"], "reason": "Its rights statement does not say public domain."})
            continue
        body.append(f"<h2>{B.esc(issue['newspaper'])}, {B.esc(issue['date'])} ({B.esc(issue['state'])})</h2>"
                    f"<p>Newspaper: {B.esc(issue['title'])}. Date: {B.esc(issue['date'])}. Issue: "
                    f'<a href="{B.esc(issue["issue"])}">{B.esc(issue["issue"])}</a>. About: '
                    f"{B.esc(event_title)}.</p>" + "".join(parts))
    return "".join(body)


def news_book(name, title, description):
    """An empty book of this module with its fields."""
    return K.new_book(f"news_{name.replace(':', '_').replace('-', '_')}", title, "Historic newspapers", GROUP,
                      "Library of Congress and the National Digital Newspaper Program (Chronicling America)",
                      LICENCE, LICENCE_URL, SEARCH, description, NOTICE,
                      changes="the machine-read text of each page, made into web pages")


def built_events(today=None):
    """The events whose newspapers may be built now (published more than 95 years ago)."""
    return [e for e in EVENTS if int(e[2][:4]) <= last_year(today)]


def front_pages_book(name, work, cache=None, left_out=None, limit=None):
    """news:front_pages: page 1 of FRONT_PER_EVENT newspapers (different states where possible) after each event."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    book = news_book("front_pages", "Front pages of history (Chronicling America)",
                     "The front pages of American newspapers in the days after great events from 1865 to 1929, each "
                     "with its title, date, Library of Congress address and machine-read text. " + OCR_NOTE)
    try:
        for number, (eid, etitle, start, end) in enumerate(built_events(), 1):
            if limit and len(book.pages) >= limit:
                break
            found, states = [], set()
            for issue in issues(start, end, cache=cache):
                if issue["state"] not in states or len(found) < FRONT_PER_EVENT // 2:
                    found.append(issue)
                    states.add(issue["state"])
                if len(found) >= FRONT_PER_EVENT:
                    break
            body = pages_html(found, etitle, 1, cache, left_out)
            if body:
                intro = (f"<p>Front pages printed between {start} and {end}. More issues: "
                         f'<a href="{B.esc(browse_url(start, end))}">{B.esc(browse_url(start, end))}</a>.</p>')
                book.pages.append(B.Page(eid, etitle, intro + body, number, ""))
    except SlowDown:
        left_out.append({"title": book.title, "reason": "The Library of Congress asked us to slow down (429); the "
                         "rest was not read."})
    return book


def state_book(name, work, cache=None, left_out=None, limit=None):
    """news:state:<state>: up to STATE_ISSUES of the state's newspapers after each event, STATE_PAGES pages each."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    state = name.split(":", 1)[1].replace("-", " ")
    if state not in STATES:
        left_out.append({"title": name, "reason": "Not a state of this module."})
        return None
    book = news_book(f"state_{piece(state)}", f"Historic newspapers of {state.title()} around great events "
                     "(Chronicling America)", f"Newspapers of {state.title()} in the days after great events from "
                     "1865 to 1929, each page with its title, date, Library of Congress address and machine-read "
                     "text. " + OCR_NOTE)
    book.region = state.title()
    try:
        for number, (eid, etitle, start, end) in enumerate(built_events(), 1):
            if limit and len(book.pages) >= limit:
                break
            found = issues(start, end, state, cache)[:STATE_ISSUES]
            body = pages_html(found, etitle, STATE_PAGES, cache, left_out)
            if body:
                book.pages.append(B.Page(eid, etitle, f"<p>Printed between {start} and {end}.</p>" + body, number,
                                         ""))
    except SlowDown:
        left_out.append({"title": book.title, "reason": "The Library of Congress asked us to slow down (429); the "
                         "rest was not read."})
    if not book.pages:
        left_out.append({"title": book.title, "reason": "Chronicling America has no English-language issues of this "
                         "state for these events (its holdings differ by state)."})
    return book


def index_book(name, work, cache=None, left_out=None, limit=None):
    """news:index: the guide (see the module docstring), made offline; nothing is downloaded."""
    import build_textbooks as B
    book = K.new_book("news_index", "Historical newspapers: a guide (Chronicling America)", "Historic newspapers",
                      GROUP, "Digital Accessibility Toolkit (an index of the library)", X.CC0_INDEX, K.CC0_URL,
                      X.TOOLKIT_REPO, "A guide to the historical newspaper books, the events they cover, why newer "
                      "newspapers are links only, how to fetch more, and where the complete collection is.",
                      "Facts and links only (CC0). " + OCR_NOTE, changes="an index written for the toolkit")
    rows = "".join(f"<li>{B.esc(t)}: printed {s} to {e}. Search: <a href=\"{B.esc(browse_url(s, e))}\">"
                   f"{B.esc(browse_url(s, e))}</a></li>" for _i, t, s, e in EVENTS)
    book.pages.append(B.Page("events", "The events and the books", (
        "<p>The front pages book (key news:front_pages) has the front pages of several newspapers after each event "
        "below; each state's book (keys news:state:alabama to news:state:wyoming, and news:state:district-of-"
        "columbia) has up to two of that state's newspapers after each event, four pages each, where Chronicling "
        f"America has them. Request word: newspapers (or newspapers-front for this guide and the front pages).</p>"
        f"<ul>{rows}</ul>"), 1, ""))
    later = "".join(f"<li>{B.esc(t)}: <a href=\"{B.esc(browse_url(s, e))}\">{B.esc(browse_url(s, e))}</a></li>"
                    for _i, t, s, e in LATER_EVENTS)
    book.pages.append(B.Page("after-1930", "Events after 1930: links only", (
        "<p>Newspapers published in the United States more than 95 years ago are in the public domain. The Library of "
        "Congress believes its newer newspapers are also in the public domain but says they may contain copyrighted "
        "material and that each user must make their own assessment, so this library does not copy them. Open "
        f"them at the Library of Congress:</p><ul>{later}</ul>"), 2, ""))
    states = "".join(f"<li>{B.esc(s.title())}: <a href=\"{B.esc(browse_url('1770-01-01', '1930-12-31', s))}\">"
                     f"{B.esc(browse_url('1770-01-01', '1930-12-31', s))}</a></li>" for s in STATES)
    book.pages.append(B.Page("fetch-more", "How to fetch more", (
        "<p>Chronicling America holds over 20 million pages. To read more, open a search address below in a browser, "
        "or give it to Program Downloader. Change the dates in the address (dates=1918-11-11/1918-11-15) for another "
        "time. The Library of Congress's free API returns the same searches as data when fo=json is added; its "
        "documentation is at "
        f'<a href="{API_DOCS}">{API_DOCS}</a>. Please read slowly: the Library asks for no more than about 20 '
        "searches a minute and blocks programs that ask faster.</p>"
        f"<p>The complete collection (all of Chronicling America, 1774 to 1963, as cleaned-up article text) is in "
        "the writing kit, as its source american_stories_newspapers, and on Hugging Face as Harvard's American "
        f'Stories dataset: <a href="{AMERICAN_STORIES}">{AMERICAN_STORIES}</a>. It is not rebuilt as books here.</p>'
        f"<h2>Every state, 1770 to 1930</h2><ul>{states}</ul>"), 3, ""))
    book.pages.append(B.Page("about-the-text", "About the text and its mistakes", (
        f"<p>{B.esc(OCR_NOTE)}</p><p>Rights: {B.esc(NOTICE)} The rights statement: "
        f'<a href="{RIGHTS}">{RIGHTS}</a>.</p>'), 4, ""))
    if limit:
        book.pages = book.pages[:limit]
    book.published = ""
    return book


def index_sign(name):
    """The weekly sign of the guide: a fingerprint of its lists."""
    return K.sha(EVENTS, LATER_EVENTS, STATES, AMERICAN_STORIES)


def selection_sign(name):
    """The weekly sign of a selection book: its events and the year limit (a new year opens newer newspapers)."""
    return K.sha(EVENTS, name, last_year())


MAKERS = {"index": (index_book, index_sign), "front_pages": (front_pages_book, selection_sign),
          "state": (state_book, selection_sign)}
PIECES = {"state": lambda: [piece(s) for s in STATES]}
COLLECTION = K.Collection("news", GROUP, makers=MAKERS, pieces=PIECES, words={
    "newspapers": lambda: ["news:index", "news:front_pages"] + [f"news:state:{piece(s)}" for s in STATES],
    "newspapers-front": lambda: ["news:index", "news:front_pages"]})

LICENCE_LINES = {
    "news_chronicling_america": "Each issue's rights statement (loc.gov API, checked page by page at every build): "
                                "\"The Library of Congress believes that the newspapers in Chronicling America are in "
                                "the public domain or have no known copyright restrictions. Newspapers published in "
                                "the United States more than 95 years ago are in the public domain in their "
                                "entirety.\" Only issues published more than 95 years ago are built; later events are "
                                "links only. www.loc.gov/robots.txt allows /collections/ and /resource/ (Crawl-delay "
                                "5, kept; checked 2026-11-22).",
    "news_index": "The guide (news:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Chronicling America newspapers of 1931 to 1963 (Pearl Harbor, D-Day, V-E and V-J Day, the Kennedy "
     "assassination ...)", "The Library of Congress believes they are in the public domain but warns they may "
     "contain copyrighted material and leaves the assessment to the user; the library's rule needs evidence of no "
     "renewal for works of 1931 to 1963, so they are links only (news:index gives each event's search address). "
     "Index: https://www.loc.gov/collections/chronicling-america/"),
    ("The whole of Chronicling America as books", "Over 20 million pages: far too many for books. The complete text "
     "is in the writing kit (source american_stories_newspapers) and on Hugging Face (dell-research-harvard/"
     "AmericanStories); a curated selection is built here. Index: "
     "https://huggingface.co/datasets/dell-research-harvard/AmericanStories"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
