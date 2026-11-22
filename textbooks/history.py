"""History for the reference library, a top-level section in the group "Reference, history" (the owner's request of
2026-11-22: flesh out history, grouped by era and region, with an index). Keys: hist:<name>. Request words: history
(every book), and by era and region: history-documents, history-us-early (to 1865), history-us-modern (1865 on),
history-people (African American, Native American, women's, disability and immigrant history), history-military,
history-states and history-world (each at most 256 jobs).

What this module builds, in plain words, each IN FULL:
  - hist:index, a guide to history in the library by era and region (the toolkit's own facts and links, CC0), which
    links the history already in other collections instead of copying it: the State Department's Milestones essays
    and Foreign Relations of the United States volumes, Chronicling America newspapers and VOA scripts (the
    periodicals' pub:history), the front pages of history (news:), the founding documents and Supreme Court cases
    (civ:, court:), the literature collection's history narratives (Herodotus, Thucydides, Gibbon, Parkman, Douglass,
    Lincoln, Du Bois, Wells), sacred texts (sacred:), whole military manuals (milw:), holidays, genealogy and
    geography, and OpenStax U.S. History and World History (osbooks:, already pinned to their last CC BY 4.0 commits);
  - hist:nara_milestone_documents: the National Archives' 100 milestone documents of American history (from the Lee
    Resolution to the Voting Rights Act), each with the Archives' essay and the full transcript (archives.gov,
    public domain, 10 seconds between pages as its robots.txt asks);
  - hist:loc_primary_source_sets: every Library of Congress primary source set for teachers: the background essay
    and teaching suggestions written by the Library's staff, and the list of primary sources in the set with their
    loc.gov addresses (read from loc.gov's JSON API, which answers programs; its web pages refuse them);
  - hist:ppp_selected_addresses: a curated selection from the Public Papers of the Presidents on govinfo.gov
    (inaugural addresses, State of the Union addresses, addresses to the nation at turning points, and remarks on
    the Americans with Disabilities Act), each read from its official PDF; and hist:ppp_index, an index of every
    volume of the Public Papers on govinfo, president by president, with the address of each volume's PDF (the whole
    series is about 127 volumes of about 1,000 pages each: too large to build whole, so the owner fetches the
    volumes he wants with Program Downloader), and the Compilation of Presidential Documents;
  - the National Park Service's Historical Handbook Series (numbers 1 to 40, 1949 to 1969, written by Park Service
    historians: battlefields, forts, colonial towns and ancient sites), read from the NPS History Electronic Library
    (npshistory.com), a private archive of Park Service publications; each book is a work of the Park Service;
  - US Army Center of Military History publications (public domain), read from their Internet Archive copies
    because history.army.mil refuses programs: American Military History, the World War II campaign brochures, the
    Korean War brochures, and histories of Black soldiers, the Women's Army Corps and the Army Nurse Corps. Judged
    by the military release rule (military_release.py) and read WHOLE: only parts about explosives, demolition,
    mines, grenades, booby traps, improvised explosives and sabotage are left out (distribution_a=True:
    build_textbooks.NOT_FIELD_SAFE);
  - old public-domain history books (published before 1931; the builder checks each Internet Archive item's year at
    every build), each marked as historical with HISTORY_NOTE: US history textbooks and classics (Fiske, Channing,
    Muzzey, Hart, Turner, Henry Adams, the Beards, MacDonald's documents), African American history (Woodson,
    Williams, Washington, Du Bois), Native American history (the Smithsonian's Handbook of American Indians, Helen
    Hunt Jackson, Charles Eastman), women's history (the History of Woman Suffrage, Stanton), disability history
    (Harry Best's The Blind and The Deaf, Helen Keller), immigrant history (Riis, Antin, Addams, Coolidge), state
    histories, and world history (Breasted, Myers, Robinson, Robinson and Beard, Hayes, Van Loon, Wells, and histories
    of India, China, Japan, Russia, Latin America, Africa and the Muslim dynasties).

Not built (NOT_INCLUDED, link-only): the whole Public Papers (too large: the index lists every volume), the
Smithsonian's pages (si.edu refuses programs), history.army.mil (refuses programs), LibreTexts history books
(already in the open courses, course:libretexts:human), the Library of Congress's old American Memory teacher pages
(replaced by the classroom materials built here), the later Park Service handbooks by outside authors, and
copyrighted modern histories.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build),
and books published before 1931 (public domain in the US; the year checked on the Internet Archive's record at every
build). The index is CC0.

Run from the repository's folder:
  python3 textbooks/history.py hist:nara_milestone_documents --out build/textbooks --limit 3
  python3 textbooks/history.py --list history-people
"""

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import govinfo_kit as GK  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "history"
GROUPS = {GROUP: "Reference, history"}           # the same name as sources.GROUPS["history"] (periodicals.py)

# What is said in every old history book's description ("{year}" is filled in): it is marked as historical.
HISTORY_NOTE = ("Published in {year}: a historical book, kept for its history. Its facts are those known in its day "
                "and later research has corrected many of them; its views and words are those of its time, and some "
                "of what it says about Native American, African American, Asian, immigrant and other peoples, about "
                "women and about disabled people is outdated and offensive.")

# The eras and regions of the request words; each book carries one or more of these tags.
EARLY, MODERN, PEOPLE, MILITARY, STATES, WORLD, DOCS = ("us-early", "us-modern", "people", "military", "states",
                                                         "world", "documents")


# ====================================================================== the National Archives' milestone documents

NARA = "https://www.archives.gov/milestone-documents"
# The 96 milestone documents listed on archives.gov/milestone-documents/list (read 2026-11-22), in date order.
NARA_DOCS = [
    "lee-resolution", "declaration-of-independence", "treaty-of-alliance-with-france", "original-design-of-the-great-"
    "seal-of-the-united-states", "articles-of-confederation", "treaty-of-paris", "virginia-plan", "northwest-ordinance",
    "constitution", "federal-judiciary-act", "president-george-washingtons-first-inaugural-speech", "bill-of-rights",
    "patent-for-cotton-gin", "alien-and-sedition-acts", "jeffersons-secret-message-to-congress", "louisiana-purchase-"
    "treaty", "marbury-v-madison", "treaty-of-ghent", "mcculloch-v-maryland", "missouri-compromise", "monroe-doctrine",
    "gibbons-v-ogden", "jacksons-message-to-congress-on-indian-removal", "treaty-of-guadalupe-hidalgo",
    "compromise-of-1850", "kansas-nebraska-act", "dred-scott-v-sandford", "telegram-announcing-the-surrender-of-fort-"
    "sumter", "homestead-act", "pacific-railway-act", "morrill-act", "emancipation-proclamation", "war-department-"
    "general-order-143", "wade-davis-bill", "13th-amendment", "check-for-the-purchase-of-alaska", "14th-amendment",
    "fort-laramie-treaty", "15th-amendment", "act-establishing-yellowstone-national-park", "thomas-edisons-patent-"
    "application-for-the-light-bulb", "chinese-exclusion-act", "pendleton-act", "interstate-commerce-act", "dawes-act",
    "sherman-anti-trust-act", "plessy-v-ferguson", "delome-letter", "joint-resolution-for-annexing-the-hawaiian-"
    "islands", "platt-amendment", "roosevelt-corollary", "16th-amendment", "17th-amendment", "keating-owen-child-labor-"
    "act", "zimmermann-telegram", "address-to-congress-declaration-of-war-against-germany", "president-woodrow-wilsons-"
    "14-points", "19th-amendment", "boulder-canyon-project-act", "tennessee-valley-authority-act", "national-"
    "industrial-recovery-act", "national-labor-relations-act", "social-security-act", "president-franklin-roosevelts-"
    "radio-address", "president-franklin-roosevelts-annual-message-to-congress", "lend-lease-act", "executive-order-"
    "8802", "joint-address-to-congress-declaration-of-war-against-japan", "executive-order-9066", "general-eisenhowers-"
    "order-of-the-day", "servicemens-readjustment-act", "manhattan-project-notebook", "surrender-of-germany",
    "united-nations-charter", "surrender-of-japan", "articles-of-agreement-of-surrender", "truman-doctrine",
    "marshall-plan", "press-release-announcing-us-recognition-of-israel", "executive-order-9981", "armistice-"
    "agreement-restoration-south-korean-state", "brown-v-board-of-education", "censure-of-senator-joseph-mccarthy",
    "national-interstate-and-defense-highways-act", "executive-order-10730", "president-dwight-d-eisenhowers-farewell-"
    "address", "executive-order-10924", "president-john-f-kennedys-inaugural-address", "john-glenns-official-"
    "communication-with-the-command-center", "aerial-photograph-of-missiles-in-cuba", "test-ban-treaty",
    "official-program-for-the-march-on-washington", "civil-rights-act", "tonkin-gulf-resolution", "voting-rights-act",
    "medicare-and-medicaid-act",
]

GUIDES = [
    dict(K.us_web(GROUP, name="nara_milestone_documents", title="Milestone Documents of American History, with their "
                  "transcripts (National Archives)", subject="US history: primary documents",
                  publisher="National Archives and Records Administration", source=f"{NARA}/list",
                  description="The National Archives' 100 milestone documents of American history, from the Lee "
                              "Resolution (1776) to the Voting Rights Act (1965) and Medicare (1965), in date order: "
                              "for each, the Archives' essay on what it is and why it matters, and the full "
                              "transcript of the document (the Declaration of Independence, the Constitution, the "
                              "Emancipation Proclamation, the Homestead Act, the 19th Amendment, Executive Order "
                              "9066, Brown v. Board of Education, the Civil Rights Act and the others).",
                  notice="From the National Archives (archives.gov): works of the US government (public domain). "
                         "The transcripts keep the documents' own spelling. The pictures of the documents are left "
                         "out; the Archives' descriptions of them are kept.",
                  crawl=[(f"{NARA}/{NARA_DOCS[0]}", 0)], urls=[f"{NARA}/{d}" for d in NARA_DOCS],
                  pages=r"^https://www\.archives\.gov/milestone-documents/(?!list$)[a-z0-9-]+$",
                  content=(r'<div id="main-col"[^>]*>', r'<div id="sidebar"|<footer\b'),
                  unit_rules=[(r"/(lee-resolution|declaration|treaty-of-alliance|original-design|articles-of-confed|"
                               r"treaty-of-paris|virginia-plan|northwest|constitution|federal-judiciary|president-"
                               r"george|bill-of-rights)", "Founding the nation, 1776 to 1791"),
                              (r"/(patent-for-cotton|alien|jeffersons|louisiana|marbury|treaty-of-ghent|mcculloch|"
                               r"missouri|monroe|gibbons|jacksons|treaty-of-guadalupe|compromise|kansas|dred)",
                               "The young republic and expansion, 1793 to 1857"),
                              (r"/(telegram|homestead|pacific-railway|morrill|emancipation|war-department|wade|13th|"
                               r"check-for|14th|fort-laramie|15th)", "Civil War and Reconstruction, 1861 to 1870"),
                              (r"/(act-establishing|thomas-edison|chinese|pendleton|interstate-commerce|dawes|"
                               r"sherman|plessy|delome|joint-resolution-for-annexing|platt|roosevelt-corollary|16th|"
                               r"17th|keating)", "The Gilded Age and the Progressive Era, 1872 to 1916"),
                              (r"/(zimmermann|address-to-congress|president-woodrow|19th|boulder|tennessee|national-"
                               r"industrial|national-labor|social-security|president-franklin)",
                               "World War I, the 1920s and the New Deal, 1917 to 1941"),
                              (r"/(lend-lease|executive-order-8802|joint-address|executive-order-9066|general-eisen|"
                               r"servicemens|manhattan|surrender|united-nations|articles-of-agreement)",
                               "World War II, 1941 to 1945"),
                              (r".", "The postwar era and civil rights, 1947 to 1965")], limit=105),
         published="1965"),
]


# ====================================================================== the Library of Congress's primary source sets

LOC = "https://www.loc.gov"
LOC_SETS = f"{LOC}/classroom-materials/?fa=partof_type:primary+source+set&fo=json&c=150"
LOC_ALL = f"{LOC}/classroom-materials/?fo=json&c=150"
LOC_NOTICE = ("From the Library of Congress (loc.gov): the background essays and teaching suggestions are written by "
              "the Library's staff, works of the US government (public domain). The primary sources themselves are "
              "listed by title with their loc.gov addresses only; each item's own rights are stated on its loc.gov "
              "page.")


def loc_json(url, cache=None):
    """The JSON of one loc.gov address read with "fo=json" (the API answers programs; the web pages do not)."""
    import build_textbooks as B
    url = url + ("&" if "?" in url else "?") + "fo=json" if "fo=json" not in url else url
    return json.loads(B.fetch(url, cache))


def loc_set_list(cache=None):
    """[(title, address)] of every primary source set, in the API's order (every page of results). The listing is
    always read fresh (never from the cache folder): loc.gov's search sometimes answers with no results at all, so
    when the filtered listing is empty the whole list of classroom materials is read and filtered here."""
    for listing in (LOC_SETS, LOC_ALL):
        out, url = [], listing
        while url:
            data = loc_json(url, None)
            for r in data.get("results", []):
                types = r.get("partof_type") or []
                if "primary source set" in [str(t).lower() for t in types] and r.get("url"):
                    out.append((str(r.get("title", "")).strip(), r["url"]))
            url = (data.get("pagination") or {}).get("next")
        if out:
            return out
    return []


def loc_set_html(data):
    """The HTML of one set: its eras, the staff's essay and suggestions (menus, pictures and forms left out), and the
    list of its primary sources (title and loc.gov address)."""
    import build_textbooks as B
    parts = []
    eras = data.get("era") or []
    if eras:
        parts.append(f"<p>Eras: {B.esc('; '.join(str(e) for e in eras))}</p>")
    for comp in (data.get("content") or {}).get("components") or []:
        body = comp.get("html") or ""
        body = re.sub(r"<nav\b.*?</nav>|<img\b[^>]*>|<script\b.*?</script>|<form\b.*?</form>", "", body, flags=re.S)
        parts.append(body)
    items = []
    for item in data.get("set") or []:
        title = " ".join(str(item.get("title", "")).split())
        link = item.get("link") or ""
        link = link if link.startswith("http") else LOC + link
        if title:
            items.append(f'<li>{B.esc(title)}: <a href="{B.esc(link)}">{B.esc(link)}</a></li>')
    if items:
        parts.append("<h2>Primary sources in this set</h2><ul>" + "".join(items) + "</ul>")
    return "".join(parts)


def loc_sets_book(name, work, cache=None, left_out=None, limit=None):
    """The book of every primary source set: one page per set, the parts by the set's first era."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    if not K.readable(LOC_SETS, cache):
        left_out.append({"title": "Library of Congress primary source sets", "reason": "loc.gov's robots.txt does not "
                         "allow reading the classroom materials now.", "url": f"{LOC}/classroom-materials/"})
        return None
    licence = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", B.fetch(K.GOVINFO_POLICY, cache))).split())
    if not re.search(K.GOVINFO_TEXT, licence):
        left_out.append({"title": "Library of Congress primary source sets", "reason": "govinfo.gov's policies page no "
                         "longer quotes 17 U.S.C. 105."})
        return None
    book = K.new_book("hist_loc_primary_source_sets", "Primary source sets for teaching history (Library of Congress)",
                      "US history: primary sources for teaching", GROUP, "Library of Congress", K.US_GOV, K.US_GOV_URL,
                      f"{LOC}/classroom-materials/",
                      "Every Library of Congress primary source set for teachers: for each topic (Abraham Lincoln, "
                      "the Harlem Renaissance, immigration, the Dust Bowl, women's suffrage, the civil rights "
                      "movement, each state and many more), the background essay and teaching suggestions written by "
                      "the Library's staff and the list of primary sources in the set (letters, photographs, maps, "
                      "newspapers, recordings) with their loc.gov addresses.", LOC_NOTICE,
                      changes="each set's essay and suggestions made into one web page, its pictures left out, its "
                              "primary sources listed by title and address")
    for number, (title, url) in enumerate(loc_set_list(cache), 1):
        if limit and len(book.pages) >= limit:
            break
        try:
            data = loc_json(url, cache)
        except (ValueError, OSError) as e:
            left_out.append({"title": title, "reason": f"It could not be read ({e}).", "url": url})
            continue
        era = ((data.get("era") or ["Other"])[0])
        book.pages.append(B.Page(f"set-{number}-{B.slug(title, 40)}", title or url, loc_set_html(data), number,
                                 str(era)))
        book.originals.append({"url": url + "?fo=json", "kind": "json", "title": title})
    book.published = ""
    return book


def loc_sets_sign(name):
    """The weekly sign: the list of sets and the month (the Library adds sets from time to time)."""
    import directory_sources as D
    try:
        return K.sha(loc_set_list(None), D.month_token())
    except (ValueError, OSError):
        return ""


# ====================================================================== the Public Papers of the Presidents (govinfo)

PPP_NOTICE = ("From the Public Papers of the Presidents of the United States, published by the Office of the Federal "
              "Register (National Archives) on govinfo.gov: works of the US government (public domain). The papers "
              "are printed as the White House released them.")
# The curated selection: (govinfo package, granule, note). Volumes from 1991 on are split into documents
# ("granules"); older volumes are one PDF each (listed in the index, hist:ppp_index). Checked in govinfo's MODS
# records on 2026-11-22.
PPP_SELECTED = [
    ("PPP-1991-book1", "PPP-1991-book1-doc-pg42-3", ""),
    ("PPP-1991-book1", "PPP-1991-book1-doc-pg74", ""),
    ("PPP-1991-book1", "PPP-1991-book1-doc-pg218-3", ""),
    ("PPP-1992-book1", "PPP-1992-book1-doc-pg156-2", ""),
    ("PPP-1993-book1", "PPP-1993-book1-doc-pg1", ""),
    ("PPP-1993-book1", "PPP-1993-book1-doc-pg1198-2", ""),
    ("PPP-1994-book1", "PPP-1994-book1-doc-pg126-3", ""),
    ("PPP-1994-book1", "PPP-1994-book1-doc-pg1318", ""),
    ("PPP-1997-book1", "PPP-1997-book1-doc-pg43", ""),
    ("PPP-1997-book1", "PPP-1997-book1-doc-pg109", ""),
    ("PPP-2001-book1", "PPP-2001-book1-doc-pg1", ""),
    ("PPP-2001-book2", "PPP-2001-book2-doc-pg1099", ""),
    ("PPP-2001-book2", "PPP-2001-book2-doc-pg1140", ""),
    ("PPP-2005-book1", "PPP-2005-book1-doc-pg66", ""),
    ("PPP-2005-book1", "PPP-2005-book1-doc-pg113", ""),
    ("PPP-2009-book1", "PPP-2009-book1-doc-pg1", ""),
    ("PPP-2009-book1", "PPP-2009-book1-doc-pg145-2", ""),
    ("PPP-2010-book2", "PPP-2010-book2-doc-pg1097", ""),
    ("PPP-2013-book1", "PPP-2013-book1-doc-pg45", ""),
    ("PPP-2013-book1", "PPP-2013-book1-doc-pg97", ""),
    ("PPP-2015-book1", "PPP-2015-book1-doc-pg747", ""),
    ("PPP-2016-book1", "PPP-2016-book1-doc-pg26", ""),
]
PPP_BOOK = GK.granule_maker(
    "hist", GROUP, "ppp_selected_addresses", "Presidential addresses, 1991 to 2016: a selection from the Public Papers "
    "of the Presidents", "US history: presidential addresses", "Office of the Federal Register, National Archives "
    "(Public Papers of the Presidents, on govinfo.gov)",
    "A selection from the Public Papers of the Presidents, each document read whole from its official PDF: the "
    "inaugural addresses of 1993, 1997, 2001, 2005, 2009 and 2013, State of the Union addresses, the addresses on "
    "the Persian Gulf War (1991) and on the attacks of 11 September 2001, remarks on the anniversaries of the "
    "Americans with Disabilities Act, and the eulogy for Clementa Pinckney (2015). Older addresses (Washington's "
    "first inaugural, Franklin Roosevelt's Four Freedoms, Eisenhower's farewell, Kennedy's inaugural) are in the "
    "National Archives' milestone documents (hist:nara_milestone_documents).", PPP_NOTICE, PPP_SELECTED)

# Every volume of the Public Papers on govinfo.gov (its PPP sitemaps and each volume's MODS title, read 2026-11-22):
# [(package, title)]. Franklin Roosevelt's papers (1933 to 1945) were published privately, not in this series.
PPP_VOLUMES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogues", "ppp_volumes.json")


def ppp_volumes():
    """[(package, title)] of every volume (catalogues/ppp_volumes.json)."""
    with open(PPP_VOLUMES_FILE, encoding="utf-8") as f:
        return [tuple(row) for row in json.load(f)]


def ppp_president(title):
    """The president's name in a volume's title ("... United States: John F. Kennedy (1961)" -> "John F. Kennedy")."""
    m = re.search(r":\s*(.+?)\s*\(", title)
    return m.group(1) if m else title


def ppp_index_book(name, work, cache=None, left_out=None, limit=None):
    """The index of every volume, one page per president (no download: the list is the module's own)."""
    import build_textbooks as B
    book = K.new_book("hist_ppp_index", "Public Papers of the Presidents: every volume on govinfo, president by "
                      "president (an index)", "US history: presidential papers", GROUP, "Digital Accessibility "
                      "Toolkit (an index of govinfo.gov)", X.CC0_INDEX, K.CC0_URL, f"{GK.GOVINFO}/app/collection/ppp",
                      "An index of the Public Papers of the Presidents of the United States on govinfo.gov, from "
                      "Herbert Hoover (1929) to Barack Obama (2016), one page per president: each volume's title and "
                      "the addresses of its PDF and its govinfo page, for fetching with Program Downloader, with a "
                      "note on the Compilation of Presidential Documents (the weekly and daily releases).",
                      "Facts and links only (CC0). The volumes themselves are works of the US government (public "
                      "domain), each about 1,000 pages.", changes="an index written for the toolkit")
    presidents = []
    for package, title in ppp_volumes():
        who = ppp_president(title)
        if not presidents or presidents[-1][0] != who:
            presidents.append((who, []))
        presidents[-1][1].append((package, title))
    for number, (who, volumes) in enumerate(presidents, 1):
        if limit and len(book.pages) >= limit:
            break
        items = "".join(f'<li>{B.esc(t)}: PDF <a href="{GK.public_pdf(p)}">{GK.public_pdf(p)}</a>; details '
                        f'<a href="{GK.GOVINFO}/app/details/{p}">{GK.GOVINFO}/app/details/{p}</a></li>'
                        for p, t in volumes)
        book.pages.append(B.Page(f"president-{number}-{B.slug(who, 40)}", who,
                                 f"<p>{len(volumes)} volume(s) of the Public Papers.</p><ul>{items}</ul>", number, ""))
    book.pages.append(B.Page("compilation-of-presidential-documents", "The Compilation of Presidential Documents",
                             "<p>The Weekly Compilation of Presidential Documents (1965 to 2009) and the Daily "
                             "Compilation of Presidential Documents (from 2009) print each president's statements, "
                             "speeches and orders as they are released; the Public Papers are made from them. Both "
                             "are on govinfo.gov: "
                             f'<a href="{GK.GOVINFO}/app/collection/cpd">{GK.GOVINFO}/app/collection/cpd</a>.</p>',
                             len(presidents) + 1, ""))
    book.published = ""
    return book


def ppp_index_sign(name):
    """The weekly sign of the index: a fingerprint of the list of volumes."""
    return K.sha(ppp_volumes())


# ====================================================================== the Park Service's Historical Handbooks

NPSH = "https://npshistory.com/handbooks/historical"
NPS_NOTICE = ("A work of the National Park Service (US Department of the Interior), written by its historians: a US "
              "government work (public domain). Read from the NPS History Electronic Library (npshistory.com), a "
              "private archive of Park Service publications, because nps.gov no longer holds the old handbooks. An "
              "old handbook: park facilities, roads and visiting details in it are those of its day, and its "
              "account of the events is that of its time.")

# (number, file on npshistory.com, short name, title, year printed, tags). One edition each (checked 2026-11-22).
NPS_HANDBOOKS = [
    (1, "1-1961", "custer_battlefield", "Custer Battlefield (Little Bighorn)", "1949, reprinted 1961", (MODERN,
                                                                                                    PEOPLE)),
    (2, "2-1957", "jamestown", "Jamestown, Virginia: the townsite and its story", "1949, revised 1957", (EARLY,)),
    (3, "3-1961", "lincoln_museum_fords_theatre", "The Lincoln Museum and the House Where Lincoln Died (Ford's "
     "Theatre)", "1949, reprinted 1961", (EARLY,)),
    (4, "4-1959", "saratoga", "Saratoga", "1950, revised 1959", (EARLY,)),
    (5, "5-1961", "fort_mchenry", "Fort McHenry", "1954, reprinted 1961", (EARLY,)),
    (6, "6-1962", "custis_lee_mansion", "Custis-Lee Mansion: the Robert E. Lee Memorial (Arlington House)",
     "1950, revised 1962", (EARLY,)),
    (7, "7-1961", "morristown", "Morristown: a military capital of the American Revolution", "1950, reprinted 1961",
     (EARLY,)),
    (8, "8-1961", "hopewell_village", "Hopewell Village (Hopewell Furnace)", "1954, reprinted 1961", (EARLY,)),
    (9, "9-1962", "gettysburg", "Gettysburg", "1954, revised 1962", (EARLY,)),
    (10, "10-1955", "shiloh", "Shiloh", "1955", (EARLY,)),
    (11, "11-1954", "statue_of_liberty", "Statue of Liberty", "1954", (MODERN, PEOPLE)),
    (12, "12-1961", "fort_sumter", "Fort Sumter", "1952, reprinted 1961", (EARLY,)),
    (13, "13-1961", "petersburg", "Petersburg", "1951, reprinted 1961", (EARLY,)),
    (14, "14-1957", "yorktown", "Yorktown: climax of the Revolution", "1954, revised 1957", (EARLY,)),
    (15, "15-1961", "manassas", "Manassas (Bull Run)", "1953, reprinted 1961", (EARLY,)),
    (16, "16-1965", "fort_raleigh", "Fort Raleigh (the Roanoke colony)", "1952, revised 1965", (EARLY,)),
    (17, "17-1956", "independence", "Independence (Independence Hall)", "1954, revised 1956", (EARLY,)),
    (18, "18-1961", "fort_pulaski", "Fort Pulaski", "1954, reprinted 1961", (EARLY,)),
    (19, "19-1956", "fort_necessity", "Fort Necessity", "1954, revised 1956", (EARLY,)),
    (20, "20-1954", "fort_laramie", "Fort Laramie", "1954", (MODERN, PEOPLE)),
    (21, "21-1961", "vicksburg", "Vicksburg", "1954, reprinted 1961", (EARLY,)),
    (22, "22-1961", "kings_mountain", "Kings Mountain", "1955, reprinted 1961", (EARLY,)),
    (23, "23-1957", "bandelier", "Bandelier (ancestral Pueblo sites)", "1955, reprinted 1957", (EARLY, PEOPLE)),
    (24, "24-1961", "ocmulgee", "Ocmulgee (ancient Native American mounds)", "1956, reprinted 1961", (EARLY, PEOPLE)),
    (25, "25-1961", "chickamauga_chattanooga", "Chickamauga and Chattanooga Battlefields", "1956, reprinted 1961",
     (EARLY,)),
    (26, "26-1956", "george_washington_birthplace", "George Washington Birthplace", "1956", (EARLY,)),
    (27, "27-1961", "montezuma_castle", "Montezuma Castle (Sinagua cliff dwellings)", "1958, reprinted 1961",
     (EARLY, PEOPLE)),
    (28, "28-1961", "scotts_bluff", "Scotts Bluff (the Oregon Trail)", "1958, reprinted 1961", (EARLY,)),
    (29, "29-1961", "chalmette", "Chalmette (the Battle of New Orleans)", "1958, reprinted 1961", (EARLY,)),
    (30, "30-1961", "guilford_courthouse", "Guilford Courthouse", "1959, reprinted 1961", (EARLY,)),
    (31, "31-1961", "antietam", "Antietam", "1960, revised 1961", (EARLY,)),
    (32, "32-1961", "vanderbilt_mansion", "Vanderbilt Mansion", "1960, reprinted 1961", (MODERN,)),
    (33, "33-1961", "richmond", "Richmond Battlefield", "1961", (EARLY,)),
    (34, "34-1963", "wright_brothers", "Wright Brothers National Memorial", "1961, reprinted 1963", (MODERN,)),
    (35, "35-1962", "fort_union", "Fort Union (New Mexico)", "1962", (MODERN,)),
    (36, "36-1962", "aztec_ruins", "Aztec Ruins (ancestral Pueblo great house)", "1962", (EARLY, PEOPLE)),
    (37, "37-1964", "whitman_mission", "Whitman Mission", "1964", (EARLY, PEOPLE)),
    (38, "38-1965", "fort_davis", "Fort Davis (Texas)", "1965", (MODERN,)),
    (39, "39-1966", "fredericksburg_spotsylvania", "Fredericksburg and Spotsylvania County Battlefields", "1966",
     (EARLY,)),
    (40, "40-1969", "golden_spike", "Golden Spike (the first transcontinental railroad)", "1969", (MODERN,)),
]


def _nps(number, file, short, title, printed, tags):
    """One Historical Handbook as a PDF entry (read whole from its npshistory.com copy)."""
    return dict(K.us_pdf(GROUP, name=f"nps_handbook_{number:02d}_{short}",
                         title=f"{title} (National Park Service Historical Handbook No. {number}, {printed})",
                         subject="US history: national historic sites", publisher="National Park Service",
                         pdf=f"{NPSH}/{file}.pdf", page=f"{NPSH}.htm",
                         description=f"The Park Service's Historical Handbook No. {number}: the history of {title} "
                                     f"and of the place the Park Service keeps, written by its historians "
                                     f"(printed {printed}).",
                         notice=NPS_NOTICE, published=printed[:4], version=f"Historical Handbook No. {number}, "
                         f"printed {printed} (npshistory.com copy {file}.pdf)"), tags=tags)


# ====================================================================== US Army Center of Military History

CMH = "US Army Center of Military History"
CMH_NOTICE = ("The release line before this says what its own front pages print about distribution. A history "
              "published by the US Army Center of Military History, read from its Internet Archive copy because "
              "history.army.mil refuses programs. Read whole: only parts about explosives, demolition, mines, "
              "grenades, booby traps, improvised explosives or sabotage are left out.")


def _cmh(name, title, archive, published, description, tags):
    """One Center of Military History publication of the Internet Archive, judged by the release rule and read whole
    but for explosives parts (distribution_a=True)."""
    return dict(K.us_pdf(GROUP, name=f"cmh_{name}", title=title, subject="US military history", publisher=CMH,
                         archive=archive, published=published, distribution_a=True,
                         version=f"{published} edition (Internet Archive item {archive})", description=description,
                         notice=CMH_NOTICE), tags=tags)


# The World War II campaign brochures (CMH Pub 72-1 to 72-40, 1991 to 2004): (pub number, archive item, campaign).
WW2_CAMPAIGNS = [
    ("72-1", "DefenseOfTheAmericas", "Defense of the Americas", "1991"),
    ("72-3", "PhilippineIslands", "Philippine Islands", "1992"),
    ("72-4", "CentralPacific", "Central Pacific", "1992"), ("72-5", "IndiaBurma", "India-Burma", "1992"),
    ("72-6", "AleutianIslands", "Aleutian Islands", "1992"), ("72-7", "Papua", "Papua", "1992"),
    ("72-8", "Guadalcanal", "Guadalcanal", "1993"), ("72-9", "NewGuinea", "New Guinea", "1993"),
    ("72-10", "NorthernSolomons", "Northern Solomons", "1998"),
    ("72-11", "AlgeriafrenchMorocco", "Algeria-French Morocco", "1993"),
    ("72-12", "TunisiaCmh72-12", "Tunisia", "2004"), ("72-13", "Egypt-Libya", "Egypt-Libya", "1993"),
    ("72-16", "Sicily", "Sicily", "1993"), ("72-17", "Naples-Foggia", "Naples-Foggia", "1994"),
    ("72-18", "NormandyCmh72-18", "Normandy", "1994"), ("72-19", "Anzio", "Anzio", "2004"),
    ("72-21", "Burma1942", "Burma, 1942", "1995"), ("72-22", "EastIndies", "East Indies", "1995"),
    ("72-23", "EasternMandates", "Eastern Mandates", "1992"),
    ("72-24", "BismarkArchipelago", "Bismarck Archipelago", "1994"),
    ("72-25", "RhinelandCmh72-25", "Rhineland", "1995"), ("72-26", "Ardennes-Alsace", "Ardennes-Alsace", "1995"),
    ("72-27", "Leyte", "Leyte", "1994"), ("72-28", "Luzon", "Luzon", "1996"),
    ("72-29", "WesternPacific", "Western Pacific", "1994"), ("72-30", "NorthernFrance", "Northern France", "1995"),
    ("72-31", "SouthernFrance", "Southern France", "1994"), ("72-33", "PoValley", "Po Valley", "1992"),
    ("72-34", "NorthApennines", "North Apennines", "1994"), ("72-35", "Ryukus", "Ryukyus", "2004"),
    ("72-36", "CentralEurope", "Central Europe", "1996"), ("72-37", "CentralBurma", "Central Burma", "1996"),
    ("72-38", "ChinaDefensive", "China Defensive", "1996"), ("72-39", "ChinaOffensive", "China Offensive", "1995"),
    ("72-40", "SouthernPhilippines", "Southern Philippines", "1996"),
]
KOREA = [("19-6", "CMHPub19-6", "The Outbreak, 27 June to 15 September 1950", "2000"),
         ("19-7", "CMHPub19-7", "The UN Offensive, 16 September to 2 November 1950", "2000"),
         ("19-8", "CMHPub19-8", "The Chinese Intervention, November 1950 to 24 January 1951", "2000"),
         ("19-9", "CMHPub19-9", "Restoring the Balance, 25 January to 8 July 1951", "2001"),
         ("19-10", "CMHPub19-10", "Years of Stalemate, July 1951 to July 1953", "2000")]

CMH_BOOKS = [
    _cmh("30_21_american_military_history_v1", "American Military History, Volume I: The United States Army and the "
         "Forging of a Nation, 1775-1917 (CMH Pub 30-21, 2009)", "cmh-pub-30-21-nsia", "2009",
         "The Army's own survey textbook of American military history from the colonial militias and the Revolution "
         "through the War of 1812, the Mexican War, the Civil War, the Indian Wars, the war with Spain and the "
         "Philippines, to 1917.", (MILITARY, EARLY)),
    _cmh("72_2_brief_history_ww2", "A Brief History of World War II: The U.S. Army Campaigns of World War II (CMH Pub "
         "72-2, 1992)", "ABriefHistoryOfWwii", "1992",
         "A short overview of the US Army's part in the Second World War, from the series of commemorative campaign "
         "brochures.", (MILITARY, MODERN)),
    _cmh("72_32_mobilization", "Mobilization: A World War II Commemorative Pamphlet (CMH Pub 72-32, 1994)",
         "Mobilization", "1994", "How the US Army grew from a small peacetime force to more than eight million "
         "soldiers in the Second World War.", (MILITARY, MODERN)),
] + [
    _cmh(f"{pub.replace('-', '_')}_{re.sub('[^a-z0-9]+', '_', name.lower()).strip('_')}", f"{name}: The U.S. Army "
         f"Campaigns of World War II (CMH Pub {pub}, {year})", archive, year,
         f"The Center of Military History's commemorative brochure on the {name} campaign of the Second World War: "
         "the strategic setting, the operations and an analysis, with suggestions for further reading.",
         (MILITARY, MODERN, WORLD))
    for pub, archive, name, year in WW2_CAMPAIGNS
] + [
    _cmh(f"{pub.replace('-', '_')}_korean_war", f"The Korean War: {name} (CMH Pub {pub}, {year})", archive, year,
         f"The Center of Military History's commemorative brochure on the Korean War: {name}.",
         (MILITARY, MODERN, WORLD))
    for pub, archive, name, year in KOREA
] + [
    _cmh("11_4_1_employment_of_negro_troops", "The Employment of Negro Troops (Ulysses Lee; CMH Pub 11-4-1, 2001 "
         "printing)", "CMHPub11-4-1", "2001", "Ulysses Lee's history, in the official US Army in World War II series, "
         "of how the Army recruited, trained, segregated and used Black soldiers in the Second World War. (Its "
         "title uses the word of its day.)", (MILITARY, MODERN, PEOPLE)),
    _cmh("50_1_1_integration_of_the_armed_forces", "Integration of the Armed Forces, 1940-1965 (Morris J. MacGregor; "
         "CMH Pub 50-1-1, 2001 printing)", "cmhPub-50-1-1-nsia", "2001", "Morris MacGregor's history of how the "
         "armed forces moved from segregation to integration, from the Second World War through Executive Order 9981 "
         "(1948) to the mid-1960s.", (MILITARY, MODERN, PEOPLE)),
    _cmh("11_8_womens_army_corps", "The Women's Army Corps (Mattie E. Treadwell; CMH Pub 11-8, 1991 printing)",
         "CMHPub11-8", "1991", "Mattie Treadwell's history, in the official US Army in World War II series, of the "
         "Women's Army Auxiliary Corps and the Women's Army Corps.", (MILITARY, MODERN, PEOPLE)),
    _cmh("72_15_womens_army_corps_commemoration", "The Women's Army Corps: A Commemoration of World War II Service "
         "(CMH Pub 72-15, 1993)", "TheWomensArmyCorps", "1993", "A short commemorative history of the Women's Army "
         "Corps in the Second World War.", (MILITARY, MODERN, PEOPLE)),
    _cmh("72_14_army_nurse_corps_commemoration", "The Army Nurse Corps: A Commemoration of World War II Service (CMH "
         "Pub 72-14, 1993)", "ArmyNurseCorps", "1993", "A short commemorative history of Army nurses in the Second "
         "World War.", (MILITARY, MODERN, PEOPLE)),
    _cmh("85_1_army_nurse_corps_highlights", "Highlights in the History of the Army Nurse Corps (CMH Pub 85-1, 1996)",
         "HighlightsInTheHistoryOfTheArmyNurseCorps", "1996", "A chronology of the Army Nurse Corps from the "
         "Revolution to the 1990s.", (MILITARY, MODERN, PEOPLE)),
    _cmh("30_4_sinews_of_war", "The Sinews of War: Army Logistics, 1775-1953 (James A. Huston; CMH Pub 30-4, 1990 "
         "printing)", "cmh-pub-30-4", "1990", "James Huston's history of how the Army was supplied and moved, from "
         "the Revolution to the Korean War.", (MILITARY, EARLY, MODERN)),
    _cmh("76_1_vietnam_deepening_involvement", "The U.S. Army Campaigns of the Vietnam War: Deepening Involvement, "
         "1945-1965 (CMH Pub 76-1, 2012)", "CMHPub76-1", "2012", "The first of the Center of Military History's "
         "brochures on the Vietnam War: from the end of the Second World War to the arrival of American combat "
         "troops in 1965.", (MILITARY, MODERN, WORLD)),
    _cmh("90_28_dust_off", "Dust Off: Army Aeromedical Evacuation in Vietnam (CMH Pub 90-28)", "CMHPub90-28", "2008",
         "How the Army's medical helicopters carried the wounded in the Vietnam War.", (MILITARY, MODERN, WORLD)),
]


# ====================================================================== old public-domain history books

def _old(name, title, subject, publisher, archive, year, description, tags, country="United States"):
    """One old public-domain history book (old_ia_books.old_book) marked as historical (HISTORY_NOTE)."""
    return dict(old_book(GROUP, name, title, subject, publisher, archive, year, description, note=HISTORY_NOTE,
                         country=country), tags=tags)




OLD_BOOKS = [
    # ---------------------------------------------------------------- US history: textbooks, classics, documents
    _old("fiske_history_us_schools_1894", "A History of the United States for Schools (John Fiske, 1894)",
         "US history: school textbook", "John Fiske (Houghton, Mifflin)", "historyofuniteds00fiskuoft", 1894,
         "John Fiske's school history of the United States from the discovery of America to the 1890s, with topical "
         "analyses and questions for each chapter.", (EARLY, MODERN)),
    _old("channing_short_history_us_1909", "A Short History of the United States for School Use (Edward Channing, "
         "1909 printing)", "US history: school textbook", "Edward Channing (Macmillan)", "shorthistoryofun00chan",
         1909, "Edward Channing's short school history of the United States from the European discoveries to the "
         "early 1900s.", (EARLY, MODERN)),
    _old("muzzey_american_history_1911", "An American History (David Saville Muzzey, 1911)", "US history: high "
         "school textbook", "David Saville Muzzey (Ginn and Company)", "americanhistory02muzz", 1911,
         "David Muzzey's high school history of the United States, one of the most used school histories of the "
         "twentieth century, from the colonies to 1911.", (EARLY, MODERN)),
    _old("hart_essentials_american_history_1905", "Essentials in American History (Albert Bushnell Hart, 1905)",
         "US history: school textbook", "Albert Bushnell Hart (American Book Company)", "essentialsiname01hartgoog",
         1905, "Albert Bushnell Hart's history of the United States from the discovery to the present day of 1905.",
         (EARLY, MODERN)),
    _old("beard_rise_american_civilization_v1_1927", "The Rise of American Civilization, Volume I: The Agricultural "
         "Era (Charles A. Beard and Mary R. Beard, 1927)", "US history: social and economic history", "Charles A. "
         "Beard and Mary R. Beard (Macmillan)", "riseofamericanci007896mbp", 1927,
         "The Beards' history of American society, economy, politics and culture from the colonies to the Civil "
         "War.", (EARLY,)),
    _old("beard_rise_american_civilization_v2_1927", "The Rise of American Civilization, Volume II: The Industrial "
         "Era (Charles A. Beard and Mary R. Beard, 1927)", "US history: social and economic history", "Charles A. "
         "Beard and Mary R. Beard (Macmillan)", "riseofamericanci02bear", 1927,
         "The Beards' history of American society, economy, politics and culture from the Civil War to the 1920s.",
         (MODERN,)),
    _old("turner_frontier_american_history_1920", "The Frontier in American History (Frederick Jackson Turner, "
         "1920)", "US history: the frontier", "Frederick Jackson Turner (Henry Holt)", "cu31924016878013", 1920,
         "Turner's essays on the frontier in American history, beginning with his 1893 paper \"The Significance of "
         "the Frontier in American History\". Later historians have questioned his thesis, and it leaves out much of "
         "what the westward movement meant for Native nations.", (EARLY, MODERN)),
    _old("adams_jefferson_administration_v1_1889", "History of the United States during the First Administration of "
         "Thomas Jefferson, Volume I (Henry Adams, 1889)", "US history: the early republic", "Henry Adams (Charles "
         "Scribner's Sons)", "cu31924092892631", 1889,
         "The first volume of Henry Adams's history of the Jefferson and Madison administrations: the United States "
         "in 1800 (its people, roads, ideas and regions) and Jefferson's first years.", (EARLY,)),
    _old("macdonald_documentary_source_book_1916", "Documentary Source Book of American History, 1606-1913 (William "
         "MacDonald, 1916 edition)", "US history: documents", "William MacDonald (Macmillan)",
         "documentarysour01macdgoog", 1916,
         "The texts of the charters, laws, treaties, proclamations and other documents of American history from the "
         "Virginia charter of 1606 to 1913, each with a short introduction.", (EARLY, MODERN, DOCS)),
    _old("hart_history_told_by_contemporaries_v2_1898", "American History Told by Contemporaries, Volume II: Building "
         "of the Republic, 1689-1783 (Albert Bushnell Hart, editor)", "US history: eyewitness accounts", "Albert "
         "Bushnell Hart, editor (Macmillan)", "toldcontemporari02hartrich", 1897,
         "Letters, diaries, speeches and reports by people who lived through the colonial wars and the American "
         "Revolution, chosen and introduced by Albert Bushnell Hart.", (EARLY, DOCS)),
    # ---------------------------------------------------------------- African American history
    _old("woodson_negro_in_our_history_1927", "The Negro in Our History (Carter G. Woodson, 1922; a 1927 edition)",
         "African American history", "Carter G. Woodson (Associated Publishers)",
         "negroinourhistor0000unse_k7k7", 1927,
         "Carter G. Woodson's history of African Americans from Africa and the slave trade through slavery, the "
         "Civil War, Reconstruction and the early twentieth century, by the founder of Negro History Week (now "
         "Black History Month). (Its title uses the word of its day.)", (PEOPLE, EARLY, MODERN)),
    _old("williams_history_negro_race_1885", "History of the Negro Race in America from 1619 to 1880 (George "
         "Washington Williams, 1882; the 1885 printing)", "African American history", "George Washington Williams "
         "(G. P. Putnam's Sons)", "historyofnegrora00willuoft", 1885,
         "The first major history of African Americans by a Black historian: Africa, slavery in each colony, Black "
         "soldiers in the Revolution and the Civil War, and citizens after emancipation. (Its title uses the word "
         "of its day.)", (PEOPLE, EARLY)),
    _old("washington_story_of_the_negro_v1_1909", "The Story of the Negro, Volume I (Booker T. Washington, 1909)",
         "African American history", "Booker T. Washington (Doubleday, Page)", "storyofthenegro01washrich", 1909,
         "Booker T. Washington's account of the rise of African Americans from slavery: their African background, "
         "slavery, freedom and progress. (Its title uses the word of its day.)", (PEOPLE, EARLY, MODERN)),
    _old("dubois_suppression_slave_trade_1896", "The Suppression of the African Slave-Trade to the United States of "
         "America, 1638-1870 (W. E. B. Du Bois, 1896)", "African American history", "W. E. B. Du Bois (Longmans, "
         "Green; Harvard Historical Studies)", "suppressionofafr00dubo", 1896,
         "Du Bois's doctoral study, the first in the Harvard Historical Studies: how the colonies and the United "
         "States tried, and failed for decades, to end the African slave trade.", (PEOPLE, EARLY)),
    _old("dubois_the_negro_1915", "The Negro (W. E. B. Du Bois, 1915)", "African and African American history",
         "W. E. B. Du Bois (Henry Holt; Home University Library)", "negro00dubo", 1915,
         "Du Bois's short history of the peoples of Africa and of the African diaspora in the Americas. (Its title "
         "uses the word of its day.)", (PEOPLE, WORLD)),
    # ---------------------------------------------------------------- Native American history
    _old("hodge_handbook_american_indians_v1_1907", "Handbook of American Indians North of Mexico, Part 1, A to M "
         "(Frederick Webb Hodge, editor; Bureau of American Ethnology Bulletin 30, 1907)", "Native American "
         "history", "Bureau of American Ethnology, Smithsonian Institution (Government Printing Office)",
         "handbookamindians01hodgrich", 1907,
         "The Smithsonian's encyclopedia of the Native nations of North America north of Mexico, their towns, "
         "leaders, languages and ways of life, A to M. Its names of nations and its views are those of 1907; many "
         "nations now use other names.", (PEOPLE, EARLY)),
    _old("hodge_handbook_american_indians_v2_1910", "Handbook of American Indians North of Mexico, Part 2, N to Z "
         "(Frederick Webb Hodge, editor; Bureau of American Ethnology Bulletin 30)", "Native American history",
         "Bureau of American Ethnology, Smithsonian Institution (Government Printing Office)",
         "handbookamindians02hodgrich", 1907,
         "The second part of the Smithsonian's encyclopedia of the Native nations of North America, N to Z, with "
         "the synonymy (the other names of each nation). Its names and views are those of its time.",
         (PEOPLE, EARLY)),
    _old("jackson_century_of_dishonor_1881", "A Century of Dishonor (Helen Hunt Jackson, 1881)", "Native American "
         "history", "Helen Hunt Jackson (Harper and Brothers)", "centuryofdishono00jackrich", 1881,
         "Helen Hunt Jackson's account of the United States government's broken treaties and dealings with the "
         "Delaware, Cheyenne, Nez Perce, Sioux, Ponca, Winnebago and Cherokee nations, written to move Congress.",
         (PEOPLE, EARLY, MODERN)),
    _old("eastman_soul_of_the_indian_1911", "The Soul of the Indian (Charles A. Eastman, Ohiyesa, 1911)",
         "Native American history and religion", "Charles A. Eastman, Ohiyesa (Houghton Mifflin)", "bp_1448876",
         1911, "The Dakota physician and writer Charles Eastman (Ohiyesa) on the religion and moral life of his "
         "people before contact with white Americans.", (PEOPLE, EARLY)),
    _old("eastman_indian_boyhood_1914", "Indian Boyhood (Charles A. Eastman, Ohiyesa, 1902; the 1914 printing)",
         "Native American history: memoir", "Charles A. Eastman, Ohiyesa (Little, Brown)", "indianboyhood00east_1",
         1914, "Charles Eastman's memoir of his Dakota childhood in Minnesota and Canada before he went to school "
         "among white Americans.", (PEOPLE, MODERN)),
    _old("eastman_from_deep_woods_1916", "From the Deep Woods to Civilization (Charles A. Eastman, Ohiyesa, 1916)",
         "Native American history: memoir", "Charles A. Eastman, Ohiyesa (Little, Brown)", "deepwoodsto00eastrich",
         1916, "The second part of Charles Eastman's autobiography: his schooling, his work as a physician at Pine "
         "Ridge at the time of the Wounded Knee massacre (1890), and his life after.", (PEOPLE, MODERN)),
    # ---------------------------------------------------------------- women's history
    _old("stanton_anthony_gage_woman_suffrage_v1_1881", "History of Woman Suffrage, Volume I, 1848-1861 (Elizabeth "
         "Cady Stanton, Susan B. Anthony and Matilda Joslyn Gage, editors, 1881)", "Women's history", "Elizabeth "
         "Cady Stanton, Susan B. Anthony and Matilda Joslyn Gage (Fowler and Wells)", "historyofwomansu01stan", 1881,
         "The suffrage movement's own history, with its speeches, letters and reports: from the Seneca Falls "
         "Convention (1848) to the Civil War.", (PEOPLE, EARLY)),
    _old("stanton_anthony_gage_woman_suffrage_v2_1887", "History of Woman Suffrage, Volume II, 1861-1876 (Elizabeth "
         "Cady Stanton, Susan B. Anthony and Matilda Joslyn Gage, editors; 1887 printing)", "Women's history",
         "Elizabeth Cady Stanton, Susan B. Anthony and Matilda Joslyn Gage", "historyofwomansu02stanuoft", 1887,
         "The second volume of the suffrage movement's history: women's work in the Civil War, the fight over the "
         "Fourteenth and Fifteenth Amendments, and the movement's split and growth to 1876.", (PEOPLE, MODERN)),
    _old("stanton_eighty_years_and_more_1898", "Eighty Years and More: Reminiscences 1815-1897 (Elizabeth Cady "
         "Stanton, 1898)", "Women's history: memoir", "Elizabeth Cady Stanton (European Publishing Company)",
         "cu31924032654315", 1898, "Elizabeth Cady Stanton's memoir of her life and of the women's rights movement "
         "she helped to found.", (PEOPLE, EARLY, MODERN)),
    _old("addams_twenty_years_hull_house_1910", "Twenty Years at Hull-House (Jane Addams, 1910)", "Women's and "
         "immigrant history: memoir", "Jane Addams (Macmillan)", "twentyyearsathu00addagoog", 1910,
         "Jane Addams's account of Hull-House, the Chicago settlement house she founded in 1889 among immigrant "
         "families, and of the reforms it worked for.", (PEOPLE, MODERN)),
    # ---------------------------------------------------------------- disability history
    _old("best_the_blind_1919", "The Blind: Their Condition and the Work Being Done for Them in the United States "
         "(Harry Best, 1919)", "Disability history: blind people", "Harry Best (Macmillan)", "blind00bestgoog", 1919,
         "Harry Best's survey of blind people in the United States in the 1910s: their numbers and causes of "
         "blindness, schools for the blind, work, pensions and relief, the raised types (the \"war of the dots\" "
         "between braille and New York Point), libraries and the organisations of and for blind people. A record of "
         "its time; its words and many of its assumptions are outdated.", (PEOPLE, MODERN)),
    _old("best_the_deaf_1914", "The Deaf: Their Position in Society and the Provision for Their Education in the "
         "United States (Harry Best, 1914)", "Disability history: deaf people", "Harry Best (Thomas Y. Crowell)",
         "deaftheirpositio00bestrich", 1914,
         "Harry Best's survey of deaf people in the United States in the 1910s: schools for the deaf, the methods "
         "debate (sign language and oralism), work and organisations. A record of its time; its words and many of "
         "its assumptions are outdated.", (PEOPLE, MODERN)),
    _old("keller_story_of_my_life_1905", "The Story of My Life (Helen Keller, 1903; the 1905 printing)",
         "Disability history: memoir", "Helen Keller, with letters and a supplementary account by Anne Sullivan and "
         "John Albert Macy (Doubleday, Page)", "storyofmylife005396mbp", 1905,
         "Helen Keller's account of her childhood, of learning language with Anne Sullivan, and of her schooling to "
         "Radcliffe College, with her letters and Anne Sullivan's reports.", (PEOPLE, MODERN)),
    # ---------------------------------------------------------------- immigrant history
    _old("riis_how_the_other_half_lives_1890", "How the Other Half Lives: Studies among the Tenements of New York "
         "(Jacob A. Riis, 1890)", "Immigrant history: city life", "Jacob A. Riis (Charles Scribner's Sons)",
         "howotherhalflive00riis_1", 1890,
         "Jacob Riis's report on the crowded tenements of New York's immigrant neighbourhoods, which moved readers "
         "to housing reform. It is written with the ethnic stereotypes of its day.", (PEOPLE, MODERN)),
    _old("antin_promised_land_1912", "The Promised Land (Mary Antin, 1912; a 1928 printing)", "Immigrant history: "
         "memoir", "Mary Antin (Houghton Mifflin)", "promisedland006049mbp", 1928,
         "Mary Antin's memoir of her Jewish childhood in the Russian Empire and her family's new life in Boston.",
         (PEOPLE, MODERN)),
    _old("coolidge_chinese_immigration_1909", "Chinese Immigration (Mary Roberts Coolidge, 1909)", "Immigrant "
         "history: Chinese Americans", "Mary Roberts Coolidge (Henry Holt)", "cu31924021182757", 1909,
         "Mary Roberts Coolidge's history of Chinese immigration to the United States, the anti-Chinese movement and "
         "the exclusion laws.", (PEOPLE, MODERN)),
    _old("abbott_immigrant_and_community_1917", "The Immigrant and the Community (Grace Abbott, 1917)", "Immigrant "
         "history", "Grace Abbott (The Century Company)", "immigrantcommuni00abbo", 1917,
         "Grace Abbott, later head of the federal Children's Bureau, on the problems immigrants met in American "
         "cities (exploitation, work, courts, schooling) and what communities could do.", (PEOPLE, MODERN)),
    # ---------------------------------------------------------------- world history
    _old("breasted_ancient_times_1916", "Ancient Times: A History of the Early World (James Henry Breasted, 1916)",
         "World history: the ancient world", "James Henry Breasted (Ginn and Company)", "in.ernet.dli.2015.213688",
         1916, "James Henry Breasted's school history of the ancient world: early humans, Egypt, Mesopotamia, the "
         "Persians, the Greeks and the Romans to the fall of Rome.", (WORLD,)),
    _old("breasted_history_of_egypt_1921", "A History of Egypt from the Earliest Times to the Persian Conquest "
         "(James Henry Breasted, 1921 printing)", "World history: ancient Egypt", "James Henry Breasted (Charles "
         "Scribner's Sons)", "b29978439", 1921,
         "Breasted's history of ancient Egypt from its beginnings to the Persian conquest. Archaeology since has "
         "added much.", (WORLD,)),
    _old("myers_general_history_1906", "General History for Colleges and High Schools (Philip Van Ness Myers, 1906 "
         "edition)", "World history: survey", "Philip Van Ness Myers (Ginn and Company)", "generalhistoryfo00myer",
         1906, "Myers's survey of world history from the ancient East through Greece, Rome, the Middle Ages and "
         "modern Europe to about 1900, centred on Europe as school books then were.", (WORLD,)),
    _old("robinson_medieval_and_modern_times_1919", "Medieval and Modern Times (James Harvey Robinson, 1919 "
         "edition)", "World history: Europe since the fall of Rome", "James Harvey Robinson (Ginn and Company)",
         "medievalmoderobi00robi", 1919,
         "Robinson's history of western Europe from the end of the Roman Empire to the First World War.", (WORLD,)),
    _old("robinson_beard_development_modern_europe_v1_1907", "The Development of Modern Europe, Volume I (James "
         "Harvey Robinson and Charles A. Beard, 1907)", "World history: modern Europe", "James Harvey Robinson and "
         "Charles A. Beard (Ginn and Company)", "india.history.resource.88382", 1907,
         "Robinson and Beard's history of Europe from the early eighteenth century, through the French Revolution "
         "and Napoleon, to the revolutions of 1848.", (WORLD,)),
    _old("hayes_political_social_modern_europe_v1_1925", "A Political and Social History of Modern Europe, Volume I, "
         "1500-1815 (Carlton J. H. Hayes, 1925 edition)", "World history: modern Europe", "Carlton J. H. Hayes "
         "(Macmillan)", "politicalsocialh0001caro", 1925,
         "Hayes's history of Europe from the sixteenth century to the fall of Napoleon: the commercial revolution, "
         "the Reformation, absolute monarchy, the Enlightenment and the French Revolution.", (WORLD,)),
    _old("van_loon_story_of_mankind_1922", "The Story of Mankind (Hendrik Willem van Loon, 1921; a 1922 printing)",
         "World history for young readers", "Hendrik Willem van Loon (Boni and Liveright)", "in.gov.ignca.2859",
         1922, "Van Loon's world history for young readers, the first winner of the Newbery Medal (1922): from "
         "prehistory to the First World War.", (WORLD,)),
    _old("wells_short_history_of_the_world_1922", "A Short History of the World (H. G. Wells, 1922)", "World history: "
         "survey", "H. G. Wells (Macmillan)", "cu31924028328908", 1922,
         "Wells's short history of the world from the origins of life to the First World War (his longer Outline of "
         "History is in the literature collection, lit:wells_outline_of_history).", (WORLD,),
         country="United Kingdom"),
    _old("smith_oxford_history_of_india_1919", "The Oxford History of India from the Earliest Times to the End of "
         "1911 (Vincent A. Smith, 1919)", "World history: India", "Vincent A. Smith (Clarendon Press)",
         "oxfordhistoryofi00smituoft", 1919,
         "Vincent Smith's history of India from ancient times to 1911. It was written by a British colonial "
         "official from the view of British rule, and Indian historians have since rewritten much of it.", (WORLD,),
         country="United Kingdom"),
    _old("pott_sketch_of_chinese_history_1903", "A Sketch of Chinese History (F. L. Hawks Pott, 1903)", "World "
         "history: China", "F. L. Hawks Pott (Kelly and Walsh, Shanghai)", "sketchofchineseh00pott", 1903,
         "A short history of China from the earliest dynasties to the Boxer Uprising, by the president of St. John's "
         "College, Shanghai.", (WORLD,), country="China"),
    _old("murdoch_history_of_japan_v1_1925", "A History of Japan, Volume I: From the Origins to the Arrival of the "
         "Portuguese in 1542 (James Murdoch; the 1925 printing)", "World history: Japan", "James Murdoch (Kegan Paul, "
         "Trench, Trubner)", "murdoch-a-history-of-japan-v-1", 1925,
         "The first volume of James Murdoch's history of Japan, from its beginnings to 1542.", (WORLD,),
         country="United Kingdom"),
    _old("kluchevsky_history_of_russia_v1_1911", "A History of Russia, Volume I (V. O. Kluchevsky, translated by C. "
         "J. Hogarth, 1911)", "World history: Russia", "V. O. Kluchevsky, translated by C. J. Hogarth (J. M. Dent)",
         "AHistoryOfRussiaVolI", 1911,
         "The first volume of the Russian historian Kluchevsky's history of Russia, from the early Slavs and Kievan "
         "Rus.", (WORLD,), country="United Kingdom"),
    _old("shepherd_latin_america_1914", "Latin America (William R. Shepherd, 1914)", "World history: Latin America",
         "William R. Shepherd (Henry Holt; Home University Library)", "latinamerica00shep", 1914,
         "A short history of Latin America from the Spanish and Portuguese colonies through independence to 1914, "
         "and its peoples and cultures.", (WORLD,)),
    _old("johnston_colonization_of_africa_1905", "A History of the Colonization of Africa by Alien Races (Harry H. "
         "Johnston, 1905 edition)", "World history: Africa", "Harry H. Johnston (Cambridge University Press)",
         "AHistoryOfTheColonizationOfAfricaByAlienRaces", 1905,
         "A history of Africa's colonisation from ancient times to 1905, by a British colonial administrator. It is "
         "written from the colonisers' view, with the racial ideas of its day; read it as a record of how "
         "colonisers saw Africa, not as Africa's own history.", (WORLD,), country="United Kingdom"),
    _old("lane_poole_mohammedan_dynasties_1894", "The Mohammedan Dynasties: Chronological and Genealogical Tables "
         "with Historical Introductions (Stanley Lane-Poole, 1894)", "World history: the Islamic world", "Stanley "
         "Lane-Poole (Archibald Constable)", "mohammedandynast00lane", 1894,
         "The ruling dynasties of the Islamic world from the caliphs to the nineteenth century, each with its rulers' "
         "dates and a short history. Its title uses an outdated name for Muslims.", (WORLD,),
         country="United Kingdom"),
]

# ---------------------------------------------------------------- state histories (one per state, before 1931)
# (state, archive item, year, title, publisher): the American Commonwealths series and other state histories.
STATE_BOOKS = [
    ("Virginia", "virginiahistoryo00cook_0", 1900, "Virginia: A History of Her People (John Esten Cooke; American "
     "Commonwealths)", "Houghton, Mifflin"),
    ("Maryland", "marylandhistor00brow", 1884, "Maryland: The History of a Palatinate (William Hand Browne; American "
     "Commonwealths)", "Houghton, Mifflin"),
    ("Massachusetts", "historymassachu01austgoog", 1876, "The History of Massachusetts from the Landing of the "
     "Pilgrims (George Lowell Austin)", "B. B. Russell"),
    ("Connecticut", "connecticutstudy00john", 1903, "Connecticut: A Study of a Commonwealth-Democracy (Alexander "
     "Johnston; American Commonwealths)", "Houghton, Mifflin"),
    ("Vermont", "vermontstudyofin00robi", 1892, "Vermont: A Study of Independence (Rowland E. Robinson; American "
     "Commonwealths)", "Houghton, Mifflin"),
    ("New York", "newyorkplantingg01robe_0", 1904, "New York: The Planting and the Growth of the Empire State, "
     "Volume I (Ellis H. Roberts; American Commonwealths)", "Houghton, Mifflin"),
    ("Pennsylvania", "shorthistoryofpe00burn", 1912, "A Short History of Pennsylvania (Smith Burnham)",
     "Burnham"),
    ("Georgia", "historyofgeorgia00evan", 1908, "A History of Georgia for Use in Schools (Lawton B. Evans)",
     "American Book Company"),
    ("Kentucky", "youngpeopleshist00thom", 1897, "A Young People's History of Kentucky (Ed. Porter Thompson)",
     "A. R. Fleming"),
    ("Tennessee", "bub_gb_HlUVAAAAYAAJ", 1903, "History of Tennessee: Its People and Its Institutions", ""),
    ("Ohio", "ohiofirstfruitso00kingrich", 1891, "Ohio: First Fruits of the Ordinance of 1787 (Rufus King; American "
     "Commonwealths)", "Houghton, Mifflin"),
    ("Indiana", "bub_gb_OXUmzX6kE-4C", 1919, "Indiana and Indianans (Jacob Piatt Dunn)", "American Historical "
     "Society"),
    ("Illinois", "wallersbriefhist00wal", 1910, "Waller's Brief History of Illinois (Elbert Waller)", ""),
    ("Michigan", "bac8762.0001.001.umich.edu", 1915, "History of Michigan, Volume I (Charles Moore)", "Lewis "
     "Publishing"),
    ("Minnesota", "cu31924064984101", 1921, "A History of Minnesota, Volume I (William Watts Folwell)", "Minnesota "
     "Historical Society"),
    ("Missouri", "missouriboneofco04carr", 1892, "Missouri: A Bone of Contention (Lucien Carr; American "
     "Commonwealths)", "Houghton, Mifflin"),
    ("Kansas", "kansaspreludetow00spri_0", 1885, "Kansas: The Prelude to the War for the Union (Leverett W. Spring; "
     "American Commonwealths)", "Houghton, Mifflin"),
    ("Texas", "texascontestofci01garr", 1903, "Texas: A Contest of Civilizations (George P. Garrison; American "
     "Commonwealths)", "Houghton, Mifflin"),
    ("New Mexico", "leadingfactsofne0001ralp_h1c9", 1911, "The Leading Facts of New Mexican History, Volume I (Ralph "
     "Emerson Twitchell)", "Torch Press"),
    ("California", "californiafromc00roycgoog", 1886, "California, from the Conquest in 1846 to the Second Vigilance "
     "Committee in San Francisco (Josiah Royce; American Commonwealths)", "Houghton, Mifflin"),
    ("Oregon", "cu31924028884869", 1922, "History of Oregon (Charles H. Carey)", "Pioneer Historical Publishing"),
    ("Washington", "stateofwashingto00washuoft", 1893, "The State of Washington: A Brief History of the Discovery, "
     "Settlement and Organization of Washington", ""),
    ("Hawaii", "briefhistoryofhaw00alex", 1899, "A Brief History of the Hawaiian People (W. D. Alexander)",
     "American Book Company"),
]
for _state, _archive, _year, _title, _pub in STATE_BOOKS:
    OLD_BOOKS.append(_old(f"state_{re.sub('[^a-z0-9]+', '_', _state.lower())}_{_year}", f"{_title}, {_year}",
                          f"State history: {_state}", _pub or "(publisher as printed in the book)", _archive, _year,
                          f"An old history of {_state}, as written in {_year}.", (STATES,)))


# ====================================================================== the index

SECTIONS = [
    ("How to find history in the library", "History books are grouped by era and region. Ask for a request word to "
     "get a group: history-documents, history-us-early, history-us-modern, history-people, history-military, "
     "history-states and history-world.", [
        ("word", "history", "Every history book of this collection"),
        ("word", "pub:history", "The State Department's Milestones essays and Foreign Relations of the United States "
                                "volumes, historic newspapers (Chronicling America) and VOA radio scripts of the "
                                "1970s (the periodicals collection)"),
        ("word", "osbooks:us-history", "OpenStax U.S. History (CC BY 4.0, the last CC BY commit), a college textbook"),
        ("word", "osbooks:world-history", "OpenStax World History, Volumes 1 and 2 (CC BY 4.0, the last CC BY "
                                          "commit)"),
        ("word", "opencourses", "LibreTexts' open history books (course:libretexts:human pieces) and other open "
                                "courses")]),
    ("Primary documents and speeches", "The documents themselves, in their own words.", [
        ("key", "hist:nara_milestone_documents", "The National Archives' 100 milestone documents, with transcripts"),
        ("key", "civ:archives_founding_documents", "The Constitution, Bill of Rights, amendments and Declaration"),
        ("key", "hist:ppp_selected_addresses", "Presidential addresses, 1991 to 2016 (Public Papers)"),
        ("key", "hist:ppp_index", "Every volume of the Public Papers of the Presidents, 1929 to 2017 (index)"),
        ("key", "hist:macdonald_documentary_source_book_1916", "Documentary Source Book of American History"),
        ("key", "hist:hart_history_told_by_contemporaries_v2_1898", "American History Told by Contemporaries, II"),
        ("key", "lit:lincoln_speeches_letters", "Lincoln's speeches and letters"),
        ("key", "lit:federalist", "The Federalist papers"),
        ("key", "lit:paine_common_sense", "Thomas Paine, Common Sense"),
        ("key", "hist:loc_primary_source_sets", "Library of Congress primary source sets for teaching"),
        ("word", "court-opinions", "Supreme Court opinions and landmark cases"),
        ("key", "civ:supreme_court_cases", "Landmark Supreme Court cases (civics)")]),
    ("United States to 1865: colonies, revolution, the young republic and the Civil War", "From the first colonies "
     "to the end of the Civil War.", [
        ("word", "history-us-early", "Every book of this era (request word)"),
        ("key", "hist:nps_handbook_02_jamestown", "Jamestown (Park Service handbook)"),
        ("key", "hist:nps_handbook_17_independence", "Independence Hall (Park Service handbook)"),
        ("key", "hist:nps_handbook_14_yorktown", "Yorktown (Park Service handbook)"),
        ("key", "hist:adams_jefferson_administration_v1_1889", "Henry Adams on the United States in 1800"),
        ("key", "hist:beard_rise_american_civilization_v1_1927", "The Beards: the agricultural era"),
        ("key", "hist:nps_handbook_09_gettysburg", "Gettysburg (Park Service handbook)"),
        ("key", "hist:cmh_30_21_american_military_history_v1", "American Military History, Volume I (the Army)"),
        ("key", "lit:parkman_oregon_trail", "Francis Parkman, The Oregon Trail"),
        ("key", "lit:douglass_narrative", "Frederick Douglass's Narrative")]),
    ("United States since 1865: Reconstruction to the present", "From Reconstruction to the twenty-first century.", [
        ("word", "history-us-modern", "Every book of this era (request word)"),
        ("key", "hist:beard_rise_american_civilization_v2_1927", "The Beards: the industrial era"),
        ("key", "hist:turner_frontier_american_history_1920", "Turner, The Frontier in American History"),
        ("key", "hist:nps_handbook_40_golden_spike", "Golden Spike: the first transcontinental railroad"),
        ("key", "hist:cmh_72_2_brief_history_ww2", "A Brief History of World War II (the Army)"),
        ("key", "news:front_pages", "Front pages of history from Chronicling America"),
        ("word", "holidays", "Federal holidays and their histories")]),
    ("African American history", "From Africa and slavery to civil rights.", [
        ("key", "hist:woodson_negro_in_our_history_1927", "Carter G. Woodson, The Negro in Our History"),
        ("key", "hist:williams_history_negro_race_1885", "George Washington Williams's history (1882)"),
        ("key", "hist:dubois_suppression_slave_trade_1896", "Du Bois on the African slave trade (1896)"),
        ("key", "lit:dubois_souls_of_black_folk", "Du Bois, The Souls of Black Folk"),
        ("key", "lit:washington_up_from_slavery", "Booker T. Washington, Up from Slavery"),
        ("key", "hist:cmh_50_1_1_integration_of_the_armed_forces", "Integration of the Armed Forces, 1940-1965"),
        ("link", "Smithsonian National Museum of African American History and Culture", "https://nmaahc.si.edu/",
         "si.edu refuses programs; open it in a browser")]),
    ("Native American history", "The Native nations of North America, in old books marked as historical and in the "
     "words of Native writers.", [
        ("key", "hist:hodge_handbook_american_indians_v1_1907", "The Smithsonian's Handbook of American Indians"),
        ("key", "hist:jackson_century_of_dishonor_1881", "Helen Hunt Jackson, A Century of Dishonor"),
        ("key", "hist:eastman_soul_of_the_indian_1911", "Charles Eastman (Ohiyesa), The Soul of the Indian"),
        ("key", "lit:mclaughlin_sioux", "Myths and legends of the Sioux (literature)"),
        ("link", "National Museum of the American Indian", "https://americanindian.si.edu/",
         "si.edu refuses programs; open it in a browser")]),
    ("Women's history", "The suffrage movement and women's work.", [
        ("key", "hist:stanton_anthony_gage_woman_suffrage_v1_1881", "History of Woman Suffrage, Volume I"),
        ("key", "hist:stanton_eighty_years_and_more_1898", "Elizabeth Cady Stanton, Eighty Years and More"),
        ("key", "hist:cmh_11_8_womens_army_corps", "The Women's Army Corps (the Army)"),
        ("link", "National Women's History Museum", "https://www.womenshistory.org/", "copyright; open it in a "
         "browser")]),
    ("Disability history", "How blind, deaf and disabled people lived and organised, and the laws they won.", [
        ("key", "hist:best_the_blind_1919", "Harry Best, The Blind (1919)"),
        ("key", "hist:best_the_deaf_1914", "Harry Best, The Deaf (1914)"),
        ("key", "hist:keller_story_of_my_life_1905", "Helen Keller, The Story of My Life"),
        ("key", "hist:ppp_selected_addresses", "Presidents' remarks on the anniversaries of the ADA"),
        ("word", "court-opinions", "Landmark disability rights cases (court:landmark_disability)"),
        ("link", "Smithsonian: EveryBody, an artifact history of disability in America",
         "https://everybody.si.edu/", "si.edu refuses programs; open it in a browser")]),
    ("Immigrant history", "Coming to America, and the laws that opened and closed the door.", [
        ("key", "hist:riis_how_the_other_half_lives_1890", "Jacob Riis, How the Other Half Lives"),
        ("key", "hist:antin_promised_land_1912", "Mary Antin, The Promised Land"),
        ("key", "hist:coolidge_chinese_immigration_1909", "Mary Roberts Coolidge, Chinese Immigration"),
        ("key", "hist:nps_handbook_11_statue_of_liberty", "Statue of Liberty (Park Service handbook)"),
        ("word", "immigration", "Today's immigration law and guides")]),
    ("Military history", "The Army's own histories, read whole but for explosives parts.", [
        ("word", "history-military", "Every military history book (request word)"),
        ("key", "hist:cmh_30_21_american_military_history_v1", "American Military History, Volume I"),
        ("key", "hist:cmh_72_18_normandy", "Normandy (World War II campaign brochure)"),
        ("word", "military-whole", "Whole military manuals (milw:)"),
        ("link", "Naval History and Heritage Command", "https://www.history.navy.mil/", "its site could not be "
         "checked; open it in a browser")]),
    ("State histories", "One old history of each of many states, as written before 1931.", [
        ("word", "history-states", "Every state history (request word)"),
        ("word", "newspapers", "Historic newspapers of each state (news:state:<state>)")]),
    ("World history", "The ancient world, Europe, Asia, Africa, Latin America and the Islamic world.", [
        ("word", "history-world", "Every world history book (request word)"),
        ("key", "lit:herodotus_history_1", "Herodotus"),
        ("key", "lit:thucydides_jowett", "Thucydides"),
        ("key", "lit:gibbon_decline_fall", "Gibbon, The Decline and Fall of the Roman Empire"),
        ("key", "lit:wells_outline_of_history", "Wells, The Outline of History"),
        ("word", "sacred-texts", "Sacred and philosophical texts of the world's religions"),
        ("word", "geography", "The CIA World Factbook and the geography index")]),
    ("Family history", "Tracing your own family's history.", [
        ("word", "genealogy", "Genealogy: National Archives guides, the Census Bureau, vital records")]),
]
INDEX = X.index_maker("hist", GROUP, "History: a guide to the library", "History",
                      "A guide to history in the library by era and region: primary documents and speeches, the "
                      "United States to 1865 and since, African American, Native American, women's, disability and "
                      "immigrant history, military history, state histories, world history and family history.",
                      SECTIONS)


# ====================================================================== the collection

GUIDES[0]["tags"] = (DOCS, EARLY, MODERN)
PDFS = [_nps(*h) for h in NPS_HANDBOOKS] + CMH_BOOKS + OLD_BOOKS
MAKERS = {"index": INDEX, "loc_primary_source_sets": (loc_sets_book, loc_sets_sign),
          "ppp_selected_addresses": PPP_BOOK, "ppp_index": (ppp_index_book, ppp_index_sign)}
MAKER_TAGS = {"index": (DOCS,), "loc_primary_source_sets": (DOCS, EARLY, MODERN),
              "ppp_selected_addresses": (DOCS, MODERN), "ppp_index": (DOCS, MODERN)}

# The request words and the tags they take (history: every book).
WORD_TAGS = {"history-documents": DOCS, "history-us-early": EARLY, "history-us-modern": MODERN,
             "history-people": PEOPLE, "history-military": MILITARY, "history-states": STATES,
             "history-world": WORLD}


def keys_with(tag=None):
    """The keys of every book with tag (every book when tag is None), the index first."""
    keys = ["hist:index"]
    for name, tags in MAKER_TAGS.items():
        if name != "index" and (tag is None or tag in tags):
            keys.append(f"hist:{name}")
    for e in GUIDES + PDFS:
        if tag is None or tag in e["tags"]:
            keys.append(f"hist:{e['name']}")
    return keys


WORDS = {"history": lambda: keys_with()}
WORDS.update({w: (lambda t=t: keys_with(t)) for w, t in WORD_TAGS.items()})
COLLECTION = K.Collection("hist", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "hist_us_gov": "archives.gov, loc.gov, govinfo.gov: works of the US government (17 U.S.C. 105, checked on "
                   "govinfo.gov's policies page at every build). archives.gov's robots.txt asks Crawl-delay 10, which "
                   "the builder keeps; loc.gov's asks Crawl-delay 5 and its web pages answer programs \"403\", so its "
                   "JSON API (fo=json, which answers) is read; govinfo.gov's allows /content/ and /metadata/. No AI "
                   "rules on any of them (checked 2026-11-22).",
    "hist_nps_handbooks": "npshistory.com (the NPS History Electronic Library, a private archive): the Historical "
                          "Handbooks are works of the National Park Service written by its historians (public "
                          "domain, 17 U.S.C. 105); the site's notice says most of its content is public domain and "
                          "names the few copyrighted works it hosts with permission (none of them read here). "
                          "robots.txt allows all but /cgi-bin/; no AI rules (checked 2026-11-22).",
    "hist_cmh": "Center of Military History publications from their Internet Archive copies, judged at every build by "
                "the military release rule (military_release.py: an archive.org copy without a restricted marking is "
                "public, with a truthful release line); read whole but for explosives parts (NOT_FIELD_SAFE).",
    "hist_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so a "
                      "later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                      "2026-11-22). British, Chinese and translated books are public domain in the US as published "
                      "before 1931.",
    "hist_index": "The index books (hist:index, hist:ppp_index) are the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("Public Papers of the Presidents, every volume whole (1929 to 2017, about 127 volumes)", "Public domain, but "
     "about 127,000 pages: too large for the library. The index (hist:ppp_index) lists every volume's PDF address for "
     "Program Downloader, and a selection of addresses is built (hist:ppp_selected_addresses). Franklin Roosevelt's "
     "papers were published privately and are not on govinfo. Index: https://www.govinfo.gov/app/collection/ppp"),
    ("Compilation of Presidential Documents (weekly 1965-2009, daily since 2009)", "Public domain on govinfo.gov, but "
     "thousands of short releases; the Public Papers are made from them. Link-only from the index. Index: "
     "https://www.govinfo.gov/app/collection/cpd"),
    ("US Army Center of Military History website (history.army.mil)", "Public domain, but history.army.mil answers "
     "programs \"403\", robots.txt included (checked 2026-11-22). Its publications are read from Internet Archive "
     "copies instead (hist:cmh_*). Index: https://history.army.mil/html/bookshelves/collect/index.html"),
    ("Smithsonian Institution pages (NMAAHC, the National Museum of the American Indian, EveryBody, Smithsonian "
     "magazine)", "www.si.edu and its museums' sites answer programs \"403\" (checked 2026-11-22); the magazine is "
     "copyright. Link-only from the index. Index: https://www.si.edu/"),
    ("Library of Congress American Memory teacher pages and lesson plans", "American Memory was retired; its teacher "
     "pages became the classroom materials, whose primary source sets are built (hist:loc_primary_source_sets). The "
     "lesson plans are not built yet. Index: https://www.loc.gov/classroom-materials/"),
    ("LibreTexts history books (Humanities bookshelf)", "Already in the library: every LibreTexts book whose licence "
     "allows it is in the open courses (course:libretexts:human pieces); not built twice. Index: "
     "https://human.libretexts.org/Bookshelves/History"),
    ("OpenStax U.S. History and World History", "Already in the library, pinned to their last CC BY 4.0 commits "
     "(osbooks:us-history and osbooks:world-history, sources.OSBOOKS_PINS); not built twice. Index: "
     "https://openstax.org/subjects/humanities"),
    ("National Park Service Historical Handbooks of the later series (1970s and after) by outside authors",
     "Several were written under contract by authors who are not federal employees (John Blassingame, Wilma Dykeman, "
     "Eleanor Roosevelt's recollections), so they may be copyright; only the numbered series by Park Service "
     "historians is built. Index: https://npshistory.com/handbooks/historical.htm"),
    ("History of Woman Suffrage, Volumes III to VI, and Woodrow Wilson's History of the American People", "Volumes "
     "III to VI: the Internet Archive copies found do not say clearly which volume or year they are; Wilson's "
     "history defends segregation and the Ku Klux Klan and is not chosen for a reference shelf. Index: "
     "https://archive.org/search?query=history+of+woman+suffrage"),
    ("Modern histories (Howard Zinn, the Oxford History of the United States, Ken Burns, Crash Course History)",
     "Copyright of their authors and publishers; link-only. Index: https://openlibrary.org/subjects/history"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
