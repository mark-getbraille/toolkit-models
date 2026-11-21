"""General-interest blogs and online magazines with open licences, added to the periodicals builder (periodicals.py:
its SOURCES, DRIVERS, ALL_PIECES, BACKFILL_ORDER, LICENCE_LINES and NOT_INCLUDED), the owner's request of 2026-11-21
("Boing Boing and similar blogs, as periodical books by year, in full").

Each blog is one source with one book per year ("pub:pluralistic:2025") or per month ("pub:pluralistic:2025-10", for
small test builds); the daily refresh rebuilds the current year, and the hourly backfill goes back year by year as far
as each blog goes (ALL_PIECES, newest first). Every post is kept whole, with its date, author, original address and
the blog's licence line.

  pluralistic           Cory Doctorow's Pluralistic (CC BY 4.0; serialized fiction, which the licence excludes, is
                        left out), from its WordPress REST API, 2020 to now
  creative_commons_blog The Creative Commons blog (CC BY 4.0), WordPress REST API, 2002 to now
  waging_nonviolence    Waging Nonviolence (CC BY 4.0; stories republished from other outlets left out), WordPress
                        REST API, 2009 to now
  wikimedia_diff        Diff, the Wikimedia community blog (CC BY-SA 4.0), from its sitemaps and its post pages
                        (its REST API is closed), 2019 to now
  eff_deeplinks         The Electronic Frontier Foundation's Deeplinks blog (CC BY 4.0), from the blog's own archive
                        pages (/updates?page=N, found by halving) and its post pages, one every 30 seconds as its
                        robots.txt asks, 2003 to now; robots.txt disallows "?page=" except on /updates, so the
                        archive read is /updates?page=N, keeping only its Deeplinks posts
  gds_accessibility_blog  The UK Government Digital Service's accessibility blog (Open Government Licence v3.0),
                        WordPress REST API, 2013 to now (group "disability")

The owner's rules, checked by hand on 2026-11-21 (LICENCE_LINES) and again by the builder:
  - robots.txt is obeyed, and a site whose robots.txt shuts out AI companies' readers by name (ClaudeBot,
    anthropic-ai, Claude-Web, GPTBot, CCBot) or says "ai-train=no" (Content-Signal) is not read at all
    (cookbooks.ai_refused, the rule the other builders follow). That rule leaves out Boing Boing, Techdirt, Kottke,
    MetaFilter, Mother Jones, Lifehacker, Mental Floss, Wired and Ars Technica, whatever their licence;
  - only the feeds, sitemaps, WordPress REST API or the blog's own archive pages are read, one request at a time,
    with the builder's pause or the site's Crawl-delay;
  - a site that forbids taking its stories wholesale or automatically (ProPublica, The 19th, Common Dreams) is not
    built, even under a Creative Commons licence;
  - copyrighted blogs and magazines are in NOT_INCLUDED with their feed or archive address, for the owner's Program
    Downloader to fetch for personal use.
"""

import datetime
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import periodicals as P  # noqa: E402

CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
CC_BY_SA_4 = "https://creativecommons.org/licenses/by-sa/4.0/"
OGL_UK_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
PIECE_RULE = r"^(19|20)\d\d(-(0[1-9]|1[0-2]))?$"     # a year ("2025") or a month ("2025-10")


def _this_year(today=None):
    """This year (or the year of `today`)."""
    return (today or datetime.date.today()).year


def _years(first, today=None):
    """Years as strings from this year back to first, newest first."""
    return [str(y) for y in range(_this_year(today), first - 1, -1)]


def span(piece):
    """(first day, the day after the last day) of a year piece ("2025") or a month piece ("2025-10"), as dates."""
    year = int(piece[:4])
    if len(piece) == 4:
        return datetime.date(year, 1, 1), datetime.date(year + 1, 1, 1)
    month = int(piece[5:7])
    end = datetime.date(year + (month == 12), month % 12 + 1, 1)
    return datetime.date(year, month, 1), end


def in_piece(date, piece):
    """True when an ISO date ("2025-10-23" or longer) falls in the piece ("2025" or "2025-10")."""
    return bool(date) and date[:len(piece)] == piece


def readable(url, cache):
    """True when the builder may read url: robots.txt allows our reader, and the site does not shut out AI companies'
    readers or say "ai-train=no" (the owner's rule: such sites are not read at all; cookbooks.ai_refused)."""
    import cookbooks                 # here, not at the top: cookbooks is only needed for this check
    return B.allowed_by_robots(url, cache) and not cookbooks.ai_refused(url, cache)


def words_of(fragment):
    """The plain words of an HTML fragment."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment or "")).split())


def checked(spec, title, text, left_out, counts):
    """True when a post may be kept: its text carries the licence line the source asks for (spec["require"]), and
    neither its text (spec["skip"]) nor its title (spec["skip_title"]) marks it as not under the blog's licence.
    counts: {"licence": n, "skip": n} of posts left out, said in left_out at the end."""
    plain = words_of(text)
    if spec.get("require") and not re.search(spec["require"], plain, re.I):
        counts["licence"] = counts.get("licence", 0) + 1
        return False
    if (spec.get("skip") and re.search(spec["skip"], plain, re.I)) or \
            (spec.get("skip_title") and re.search(spec["skip_title"], title or "", re.I)):
        counts["skip"] = counts.get("skip", 0) + 1
        return False
    return True


def report(spec, piece, counts, left_out):
    """Say in left_out how many posts of the piece were left out, and why."""
    label = f"{spec['series_title']}, {piece}"
    if counts.get("licence"):
        left_out.append({"title": label, "reason": f"{counts['licence']} posts were left out: they do not carry the "
                         "blog's licence line."})
    if counts.get("skip"):
        left_out.append({"title": label, "reason": f"{counts['skip']} posts were left out: "
                         f"{spec.get('skip_reason', 'not under the blog licence')}."})
    if counts.get("failed"):
        left_out.append({"title": label, "reason": f"{counts['failed']} posts could not be read."})


def byline(spec, authors):
    """"By <authors>, <publisher>" (or "" without authors)."""
    authors = [a for a in authors if a]
    return f"By {', '.join(authors)}, {spec['publisher']}" if authors else ""


# ====================================================================== WordPress REST API (by year or month)

def wordpress_items(spec, piece, cache, left_out, today):
    """The posts of one year or month of a WordPress blog, from its REST API (/wp-json/wp/v2/posts, 100 a page,
    newest first), each whole: its title, date, authors and full text. A post without the licence line the source
    requires, or one its skip rules mark (republished from elsewhere, serialized fiction), is left out and counted.
    The current year is always read afresh; older pages come from the cache."""
    start, end = span(piece)
    current = end > (today or datetime.date.today())
    site = spec["site"]
    out, counts = [], {}
    for page in range(1, 400):
        url = (f"{site}/wp-json/wp/v2/posts?after={start.isoformat()}T00:00:00&before={end.isoformat()}T00:00:00"
               f"&per_page=100&page={page}&orderby=date&order=desc&_embed=author"
               f"&_fields=id,date,link,title,content,_links,_embedded")
        if not readable(url, cache):
            left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": "robots.txt does not allow "
                             "its REST API (or the site shuts out AI readers)."})
            break
        try:
            posts = json.loads(B.fetch(url, None if current else cache))
        except urllib.error.HTTPError as e:
            if e.code == 400:                                # past the last page
                break
            raise
        if not isinstance(posts, list) or not posts:
            break
        for p in posts:
            content = (p.get("content") or {}).get("rendered", "")
            title = html.unescape(re.sub(r"<[^>]+>", "", (p.get("title") or {}).get("rendered", "")))
            if not checked(spec, title, content, left_out, counts):
                continue
            authors = [a.get("name", "") for a in (p.get("_embedded") or {}).get("author", []) if isinstance(a, dict)]
            when = B.iso_date(p.get("date", ""))
            link = p.get("link", site)
            out.append(P.item(link, title, when, P.clean(content, link, True), P.month_unit(when),
                              byline=byline(spec, authors)))
        if len(posts) < 100 or len(out) >= spec.get("limit", P.MAX_ITEMS):
            break
    report(spec, piece, counts, left_out)
    out = out[:spec.get("limit", P.MAX_ITEMS)]
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== post pages (sitemaps, archive pages)

def meta(text, prop):
    """The content of a <meta property|name="prop"> tag, "" when there is none."""
    m = re.search(rf'<meta[^>]+(?:property|name)="{re.escape(prop)}"[^>]+content="([^"]*)"', text) or \
        re.search(rf'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="{re.escape(prop)}"', text)
    return html.unescape(m.group(1)) if m else ""


def page_authors(text):
    """The authors of a post page: its <meta name="author">, else its byline links (rel="author"), else the Person
    names of its JSON-LD."""
    if meta(text, "author"):
        return [meta(text, "author")]
    names = [words_of(a) for a in re.findall(r'<a\b[^>]*rel="author"[^>]*>(.*?)</a>', text, re.S)]
    if names:
        return list(dict.fromkeys(n for n in names if n))
    for d in P.json_ld(text):
        for a in d.get("author", []) if isinstance(d.get("author"), list) else [d.get("author")]:
            if isinstance(a, dict) and a.get("name"):
                names.append(a["name"])
    return list(dict.fromkeys(names))


def page_items(spec, piece, urls, cache, left_out, counts):
    """Read each post page of urls (in order) into an item: its body (spec["content"]: the regular expression of the
    element that holds the post), title (og:title, else its first heading), publication date
    (article:published_time, else the date in its address) and authors. Stops after spec["budget_minutes"] (the
    piece is then marked not complete; the next build goes on from the cache)."""
    start_time, out = time.monotonic(), []
    for number, url in enumerate(urls):
        if time.monotonic() - start_time > spec.get("budget_minutes", 200) * 60:
            P.INCOMPLETE[(spec["name"], piece)] = (number, len(urls))
            left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"Not finished in this run: "
                             f"{number} of {len(urls)} posts read; build the key again to go on."})
            break
        if not readable(url, cache):
            counts["failed"] = counts.get("failed", 0) + 1
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            counts["failed"] = counts.get("failed", 0) + 1
            continue
        raw = P.div_inner(text, spec["content"])
        if not raw:
            counts["failed"] = counts.get("failed", 0) + 1
            continue
        title = meta(text, "og:title") or B.first_heading(text)
        if not checked(spec, title, text if spec.get("require_on_page") else raw, left_out, counts):
            continue
        when = B.iso_date(meta(text, "article:published_time"))
        if not when:
            m = re.search(r"/((?:19|20)\d\d)/(\d\d)/(?:(\d\d)/)?", url)
            when = "-".join(g for g in m.groups() if g) if m else ""
        out.append(P.item(url, title, when, P.clean(raw, url, True), P.month_unit(when),
                          byline=byline(spec, page_authors(text))))
    return out


def sitemap_urls(spec, cache, fresh):
    """Every post address in the blog's sitemaps (spec["sitemap"], an index whose sitemaps are read too)."""
    found, todo, seen = [], [spec["sitemap"]], set()
    while todo:
        sm = todo.pop(0)
        if sm in seen or not readable(sm, cache):
            continue
        seen.add(sm)
        text = B.fetch(sm, None if fresh else cache)
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text):
            loc = html.unescape(loc)
            (todo if re.search(r"sitemap[^/]*\.xml$", loc) else found).append(loc)
    return found


def sitemap_items(spec, piece, cache, left_out, today):
    """The posts of one year or month of a blog read from its sitemaps (addresses with the date in them,
    spec["post_url"] with the groups year and month) and its post pages, newest first."""
    current = span(piece)[1] > (today or datetime.date.today())
    rule = re.compile(spec["post_url"])
    urls = []
    for url in sitemap_urls(spec, cache, current):
        m = rule.match(url)
        if m and in_piece(f"{m.group(1)}-{m.group(2)}", piece):
            urls.append(url)
    urls = sorted(dict.fromkeys(urls), reverse=True)[:spec.get("limit", P.MAX_ITEMS)]
    counts = {}
    out = page_items(spec, piece, urls, cache, left_out, counts)
    report(spec, piece, counts, left_out)
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ---------------------------------------------------------------------- EFF Deeplinks: its archive pages

def archive_page(spec, number, cache, fresh):
    """[(year-month, address)] of the posts listed on one archive page (spec["archive"] with the page number), in
    page order; [] past the last page."""
    url = spec["archive"].format(page=number)
    if not readable(url, cache):
        return []
    try:
        text = B.fetch(url, None if fresh else cache)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    out = []
    # Only the listed posts (spec["archive_item"]: one teaser each), never the "related" links around them.
    for block in re.findall(spec["archive_item"], text, re.S) if spec.get("archive_item") else [text]:
        for path, year, month in re.findall(spec["archive_link"], block)[:1 if spec.get("archive_item") else None]:
            out.append((f"{year}-{month}", urllib.parse.urljoin(url, path)))
    return list(dict.fromkeys(out))


def archive_items(spec, piece, cache, left_out, today):
    """The posts of one year or month of a blog whose archive lists its posts newest first on numbered pages: the
    first page that reaches back to the piece is found by halving (a dozen pages, not hundreds), then pages are read
    on until they are older than the piece; each post page is read once (kept in the cache)."""
    start, end = span(piece)
    current = end > (today or datetime.date.today())
    first, last = start.strftime("%Y-%m"), (end - datetime.timedelta(days=1)).strftime("%Y-%m")
    pages = {}

    def listed(n):
        """The posts on archive page n (each page read once in this build; fresh for the current year)."""
        if n not in pages:
            pages[n] = archive_page(spec, n, cache, current and n < 60)
        return pages[n]
    low, high = 0, spec.get("archive_pages", 4000)
    while low < high:                    # the first page whose oldest post is not newer than the piece's last month
        mid = (low + high) // 2
        posts = listed(mid)
        if posts and min(p[0] for p in posts) > last:
            low = mid + 1
        else:
            high = mid
    urls, n = [], max(0, low - 1)
    while True:
        posts = listed(n)
        if not posts:
            break
        urls += [u for ym, u in posts if first <= ym <= last]
        if max(p[0] for p in posts) < first:
            break
        n += 1
    urls = list(dict.fromkeys(urls))[:spec.get("limit", P.MAX_ITEMS)]
    counts = {}
    out = page_items(spec, piece, urls, cache, left_out, counts)
    report(spec, piece, counts, left_out)
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== the sources

COMMON = dict(country="International", pieces=None, piece_rule=PIECE_RULE, budget_minutes=200)

SOURCES = {
    "pluralistic": dict(
        COMMON, group="periodicals", driver="blog_wordpress", site="https://pluralistic.net",
        series_title="Pluralistic (Cory Doctorow)", subject="Technology, monopoly, labour and culture: essays and "
        "links", publisher="Cory Doctorow (Pluralistic)", country="United States", licence="CC BY 4.0",
        licence_url=CC_BY_4, source="https://pluralistic.net/",
        description="Cory Doctorow's daily newsletter and blog: long essays on technology, monopoly, copyright, "
                    "labour and politics, with his links and \"Object permanence\" look-backs. Every post whole. "
                    "One book per year.",
        notice="Pluralistic by Cory Doctorow, licensed under a Creative Commons Attribution 4.0 licence (each post's "
               "own colophon: \"This work - excluding any serialized fiction - is licensed under a Creative Commons "
               "Attribution 4.0 license\"). Serialized fiction is left out. Pictures are left out (their "
               "descriptions kept).",
        changes="each post made into a web page with the pictures left out (their descriptions kept)",
        # No licence page: the licence is in every post's colophon, and each post is checked for it (require).
        require=r"licensed under a Creative Commons Attribution 4\.0",
        skip_title=r"\b(serial(?:i[sz]ed)?|chapter \d+|part \d+ of)\b|\bfiction\b",
        skip_reason="serialized fiction, which the blog's licence does not cover",
        daily=lambda today: [str(_this_year(today))], first_year=2020),
    "creative_commons_blog": dict(
        COMMON, group="periodicals", driver="blog_wordpress", site="https://creativecommons.org",
        series_title="Creative Commons blog", subject="Open culture, open licences and the commons",
        publisher="Creative Commons", country="International", licence="CC BY 4.0", licence_url=CC_BY_4,
        source="https://creativecommons.org/blog/",
        description="News and essays from Creative Commons on open licences, open access, open education, culture, "
                    "the public domain and artificial intelligence and the commons. One book per year.",
        notice="Creative Commons blog posts, licensed under the Creative Commons Attribution 4.0 International "
               "licence unless otherwise marked (creativecommons.org/policies). Posts marked with another licence "
               "are left out. Pictures are left out (their descriptions kept).",
        changes="each post made into a web page with the pictures left out (their descriptions kept)",
        licence_page="https://creativecommons.org/policies/",
        licence_text=r"all content on this site is licensed under the Creative Commons Attribution 4\.0 International "
                     r"license unless otherwise marked",
        skip=r"\b(?:CC BY-NC|CC BY-ND|NonCommercial|NoDerivatives|All rights reserved)\b",
        skip_reason="marked with a licence other than CC BY 4.0",
        daily=lambda today: [str(_this_year(today))], first_year=2002),
    "waging_nonviolence": dict(
        COMMON, group="periodicals", driver="blog_wordpress", site="https://wagingnonviolence.org",
        series_title="Waging Nonviolence", subject="Nonviolent movements and social change",
        publisher="Waging Nonviolence", country="International", licence="CC BY 4.0", licence_url=CC_BY_4,
        source="https://wagingnonviolence.org/",
        description="Waging Nonviolence's reporting and analysis of people-powered movements around the world: "
                    "strikes, protests, organising and the history of nonviolent action. One book per year.",
        notice="Waging Nonviolence content falls under a Creative Commons Attribution 4.0 International License (the "
               "site's footer). Stories republished from other outlets are left out. Pictures are left out (their "
               "descriptions kept).",
        changes="each story made into a web page with the pictures left out (their descriptions kept); stories "
                "republished from other outlets left out",
        licence_page="https://wagingnonviolence.org/",
        licence_text=r"Waging Nonviolence content falls under a Creative Commons Attribution 4\.0",
        skip=r"(?:originally|first) (?:been )?(?:published|appeared) (?:by|in|on|at)\b|\breprinted (?:with|by)\b|"
             r"\brepublished (?:with permission|from)\b",
        skip_reason="republished from other outlets (they are under those outlets' terms)",
        daily=lambda today: [str(_this_year(today))], first_year=2009),
    "wikimedia_diff": dict(
        COMMON, group="periodicals", driver="blog_sitemap", series_title="Diff (Wikimedia community blog)",
        subject="Wikipedia, Wikimedia and free knowledge", publisher="Wikimedia Foundation and Wikimedia "
        "community authors (Diff)", country="International", licence="CC BY-SA 4.0", licence_url=CC_BY_SA_4,
        source="https://diff.wikimedia.org/", sitemap="https://diff.wikimedia.org/sitemap.xml",
        post_url=r"^https://diff\.wikimedia\.org/((?:19|20)\d\d)/(\d\d)/\d\d/[^/]+/$",
        content=r'<div class="entry-content[^"]*"[^>]*>',
        description="Stories by Wikimedia volunteers, affiliates and the Wikimedia Foundation about Wikipedia and "
                    "its sister projects, events, tools and free knowledge around the world (posts in English and "
                    "other languages). One book per year.",
        notice="Diff content is licensed under Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA) unless "
               "otherwise noted (the site's footer); this book is shared under the same licence. Pictures are left "
               "out (their descriptions kept).",
        changes="each post made into a web page with the pictures left out (their descriptions kept)",
        licence_page="https://diff.wikimedia.org/",
        licence_text=r"Content licensed under Creative Commons Attribution-ShareAlike 4\.0",
        daily=lambda today: [str(_this_year(today))], first_year=2019),
    "eff_deeplinks": dict(
        COMMON, group="periodicals", driver="blog_archive", series_title="EFF Deeplinks blog",
        subject="Digital rights, privacy and free expression", publisher="Electronic Frontier Foundation (EFF)",
        country="United States", licence="CC BY 4.0", licence_url=CC_BY_4, source="https://www.eff.org/deeplinks",
        archive="https://www.eff.org/updates?page={page}",
        archive_item=r'<article[^>]*node--teaser.*?</article>',
        archive_link=r'href="(/deeplinks/((?:19|20)\d\d)/(\d\d)/[a-z0-9-]+)"', archive_pages=4000,
        content=r'<div class="field field--name-body[^"]*"[^>]*>',
        description="The Electronic Frontier Foundation's blog on privacy, surveillance, free speech, copyright, "
                    "security and the law of the internet, written by its lawyers, technologists and activists. One "
                    "book per year (read one post every 30 seconds, as EFF's robots.txt asks, so a year can take "
                    "more than one build).",
        notice="Any and all original material on the EFF website may be freely distributed at will under the "
               "Creative Commons Attribution 4.0 International License (EFF's copyright policy). Pictures are left "
               "out (their descriptions kept).",
        changes="each post made into a web page with the pictures left out (their descriptions kept)",
        licence_page="https://www.eff.org/copyright",
        licence_text=r"Any and all original material on the EFF website may be freely distributed at will under the "
                     r"Creative Commons Attribution 4\.0",
        daily=lambda today: [str(_this_year(today))], first_year=2003),
    "gds_accessibility_blog": dict(
        COMMON, group="disability", driver="blog_wordpress", site="https://accessibility.blog.gov.uk",
        series_title="Accessibility in government (GDS blog)", subject="Digital accessibility in government "
        "services", publisher="Government Digital Service, UK Government", country="United Kingdom",
        licence="OGL-UK-3.0", licence_url=OGL_UK_URL, source="https://accessibility.blog.gov.uk/",
        description="The UK Government Digital Service's blog on making government websites and services "
                    "accessible: user research with disabled people, assistive technology, testing, the public "
                    "sector accessibility regulations and WCAG. One book per year.",
        notice="Contains public sector information licensed under the Open Government Licence v3.0. The UK's "
               "accessibility law (the Public Sector Bodies Accessibility Regulations 2018 and the Equality Act "
               "2010) differs from the US ADA and Section 508.",
        changes="each post made into a web page with the pictures left out (their descriptions kept)",
        licence_page="https://accessibility.blog.gov.uk/",
        licence_text=r"Open Government Licence v3\.0",
        daily=lambda today: [str(_this_year(today))], first_year=2013),
}
for _name, _spec in SOURCES.items():
    _spec["name"] = _name
    _spec["pieces"] = (lambda first: lambda today: _years(max(first, _this_year(today) - 1), today))(
        _spec["first_year"])                                  # this year and last year by default

DRIVERS = {"blog_wordpress": wordpress_items, "blog_sitemap": sitemap_items, "blog_archive": archive_items}

# Every year back to each blog's first (checked 2026-11-21: the oldest post of each REST API or sitemap), newest
# first; the current year is the daily refresh's.
ALL_PIECES = {name: (lambda first: lambda t: _years(first, t)[1:])(spec["first_year"])
              for name, spec in SOURCES.items()}

# Where they go in the hourly backfill: the small blogs before Voice of America's big years, the slow EFF blog (30
# seconds a post) before UK Hansard.
BACKFILL_BEFORE = {"gds_accessibility_blog": "voa", "pluralistic": "voa", "waging_nonviolence": "voa",
                   "creative_commons_blog": "voa", "wikimedia_diff": "voa", "eff_deeplinks": "uk_hansard"}

LICENCE_LINES = {
    "pluralistic": "Each post's colophon (for example pluralistic.net/2026/11/19/loan-out-companies/): \"This work "
                   "- excluding any serialized fiction - is licensed under a Creative Commons Attribution 4.0 "
                   "license. That means you can use it any way you like, including commercially, provided that you "
                   "attribute it to me, Cory Doctorow\". pluralistic.net/robots.txt: \"user-agent: * disallow:\" (no "
                   "AI rules); its WordPress REST API is open.",
    "creative_commons_blog": "creativecommons.org/policies/: \"all content on this site is licensed under the "
                             "Creative Commons Attribution 4.0 International license unless otherwise marked\". "
                             "robots.txt: \"User-agent: * Disallow:\" (no AI rules); WordPress REST API open.",
    "waging_nonviolence": "wagingnonviolence.org footer: \"Waging Nonviolence content falls under a Creative Commons "
                          "Attribution 4.0 International License.\" robots.txt: \"User-agent: * Disallow:\" (no AI "
                          "rules); WordPress REST API open.",
    "wikimedia_diff": "diff.wikimedia.org footer: \"Content licensed under Creative Commons Attribution-ShareAlike "
                      "4.0 (CC-BY-SA) unless otherwise noted.\" robots.txt disallows only /wp-admin/ (no AI rules); "
                      "its REST API answers \"rest_disabled\", so the sitemaps and post pages are read.",
    "eff_deeplinks": "www.eff.org/copyright: \"Any and all original material on the EFF website may be freely "
                     "distributed at will under the Creative Commons Attribution 4.0 International License\". "
                     "www.eff.org/robots.txt: \"Crawl-delay: 30\" for all readers; GPTBot, ClaudeBot, anthropic-ai "
                     "and CCBot get a Crawl-delay only, not a Disallow (no Content-Signal). It disallows "
                     "\"/*?*page=\" but allows \"/updates?page=\", so the archive is read from /updates (the "
                     "paged RSS feed ignores its page number).",
    "gds_accessibility_blog": "accessibility.blog.gov.uk footer: \"All content is available under the Open "
                              "Government Licence v3.0, except where otherwise stated\". robots.txt disallows only "
                              "/wp-admin/ (no AI rules); WordPress REST API open.",
}

# Looked at on 2026-11-21 and not built. The address after "Feed:" or "Archive:" is for the owner's Program
# Downloader (personal use only).
NOT_INCLUDED = [
    ("Boing Boing (boingboing.net)", "Its posts carry a CC BY-NC-SA 3.0 link (personal use would be allowed), but "
     "its robots.txt says \"Content-Signal: search=yes,ai-train=no,use=reference\", shuts out ClaudeBot, GPTBot, "
     "CCBot and other AI crawlers by name, and disallows its WordPress REST API (/wp-json/wp/v2) to every reader, so "
     "it is not read. Feed: https://boingboing.net/feed"),
    ("Techdirt (techdirt.com)", "Its robots.txt says \"ai-train=no\" and shuts out AI crawlers and AI agents by name "
     "(ClaudeBot, Claude-User, GPTBot and others), so it is not read whatever its licence. Feed: "
     "https://www.techdirt.com/feed/"),
    ("Kottke (kottke.org)", "Copyright of Jason Kottke (no open licence found), and its robots.txt shuts out CCBot "
     "and anthropic-ai. Feed: https://feeds.kottke.org/main"),
    ("MetaFilter (metafilter.com)", "Its robots.txt says \"ai-train=no\" and shuts out AI crawlers by name; posts "
     "and comments belong to their members (no site-wide open licence). Feed: https://rss.metafilter.com/metafilter.rss"),
    ("Hackaday (hackaday.com)", "\"Copyright © 2026\" (Supplyframe/Hackaday.com); no open licence. Robots allows "
     "readers. Feed: https://hackaday.com/blog/feed/"),
    ("Lifehacker (lifehacker.com)", "Copyright of Ziff Davis; its robots.txt shuts out AI crawlers by name. Feed: "
     "https://lifehacker.com/feed/rss"),
    ("Atlas Obscura (atlasobscura.com)", "Copyright of Atlas Obscura; its robots.txt refuses automated readers "
     "(403). Feed: https://www.atlasobscura.com/feeds/latest"),
    ("Mental Floss (mentalfloss.com)", "Copyright of its publisher; its robots.txt shuts out GPTBot and ClaudeBot. "
     "Feed: https://www.mentalfloss.com/rss.xml"),
    ("The Marginalian (themarginalian.org)", "Copyright of Maria Popova; no open licence. Archive: "
     "https://www.themarginalian.org/wp-sitemap.xml"),
    ("Open Culture (openculture.com)", "\"©2006-2026 Open Culture, LLC. All rights reserved.\", and its robots.txt "
     "disallows its WordPress REST API. Feed: https://www.openculture.com/feed"),
    ("Low-tech Magazine (solar.lowtechmagazine.com)", "Already in the Kiwix library "
     "(solar.lowtechmagazine.com_mul_all), so not built again; its site now says \"© Kris De Decker\". Feed: "
     "https://solar.lowtechmagazine.com/posts/index.xml"),
    ("Make: (makezine.com)", "\"Make Community LLC. © 2026 All Rights Reserved\"; no open licence. Feed: "
     "https://makezine.com/feed/"),
    ("Instructables (instructables.com)", "Each project has its own licence chosen by its maker (many CC BY-NC-SA), "
     "but its robots.txt disallows the PDF, text and HTML copies (\"/*.html$\", \"/*.pdf$\") and Autodesk's terms "
     "page could not be read automatically (404); not built. Archive: https://www.instructables.com/sitemap.xml"),
    ("ProPublica (propublica.org)", "CC BY-NC-ND 3.0 for its stories, but \"Steal Our Stories\" says: \"You can't "
     "republish our material wholesale, or automatically; you need to select stories to be republished "
     "individually.\" Not built (checked again 2026-11-21). Feed: https://www.propublica.org/feeds/propublica/main"),
    ("Grist (grist.org)", "\"© 1999-2026 Grist Magazine, Inc. All rights reserved.\"; its republishing page could not "
     "be found (404) and robots.txt disallows its republish pages. Feed: https://grist.org/feed/"),
    ("Mother Jones (motherjones.com)", "Copyright of the Foundation for National Progress; its robots.txt shuts out "
     "GPTBot, ClaudeBot and anthropic-ai. Feed: https://www.motherjones.com/feed/"),
    ("The 19th (19thnews.org)", "CC BY-NC-ND 4.0, but its republishing terms say \"Do not scrape our website\" and "
     "require its tracking pixel; not built. Feed: https://19thnews.org/feed/"),
    ("Common Dreams (commondreams.org)", "CC BY-NC-ND 3.0, but its terms say \"You cannot automatically republish all "
     "articles; select stories individually.\" Not built. Feed: https://www.commondreams.org/feeds/feed.rss"),
    ("openDemocracy (opendemocracy.net)", "Each article says \"published under a Creative Commons "
     "Attribution-NonCommercial 4.0 International licence\" (personal use would be allowed), but its 56,000 articles "
     "are listed in two sitemaps without dates, its content API needs a key, and its pages have no stable article "
     "element; not built yet. Feed: https://www.opendemocracy.net/rss/"),
    ("The Markup (themarkup.org)", "Its terms say it publishes \"many of its articles\" under a Creative Commons "
     "licence, article by article; not checked one by one. Feed: https://themarkup.org/feeds/rss.xml"),
    ("Wired (wired.com) and Ars Technica (arstechnica.com)", "Copyright of Condé Nast; both robots.txt files shut out "
     "ClaudeBot and CCBot. Feeds: https://www.wired.com/feed/rss and https://feeds.arstechnica.com/arstechnica/index"),
    ("KFF Health News, Global Voices and The Conversation", "Already in the library (pub:kff_health_news, "
     "pub:global_voices, pub:the_conversation)."),
]


SUPERSEDED = {"ProPublica", "Low-tech Magazine"}


# ====================================================================== registration in periodicals.py

def register(module):
    """Add these blogs to the periodicals builder (module: periodicals): their sources, drivers, every piece back to
    the first year, their place in the hourly backfill, licence lines and what was not built."""
    for name, spec in SOURCES.items():
        module.SOURCES.setdefault(name, spec)
        module.GROUPS.setdefault(spec["group"], module.sources.GROUPS[spec["group"]])
    module.DRIVERS.update(DRIVERS)
    for name, pieces in ALL_PIECES.items():
        module.ALL_PIECES.setdefault(name, pieces)
    for name, before in BACKFILL_BEFORE.items():
        if name not in module.BACKFILL_ORDER:
            order = module.BACKFILL_ORDER
            order.insert(order.index(before) if before in order else len(order), name)
    module.LICENCE_LINES.update(LICENCE_LINES)
    # Rows of the periodicals' own list that a row here replaces (checked again, now with the feed address).
    module.NOT_INCLUDED[:] = [r for r in module.NOT_INCLUDED if r[0] not in SUPERSEDED]
    for row in NOT_INCLUDED:
        if row not in module.NOT_INCLUDED:
            module.NOT_INCLUDED.append(row)


_old_piece_label = P.piece_label


def piece_label(name, piece):
    """How a piece of a blog is named in its book's title ("2025", "October 2025")."""
    if name in SOURCES and re.match(r"^\d{4}-\d\d$", piece):
        return P.month_unit(piece + "-01")
    if name in SOURCES:
        return piece
    return _old_piece_label(name, piece)


if getattr(P.piece_label, "__module__", "") != __name__:
    P.piece_label = piece_label
register(P)
