"""Self-test of the blogs and online magazines added to the periodicals builder on 2026-11-21 (blogs.py), with MADE-UP
data only: nothing is downloaded.

It checks that:
  - the blogs are registered in periodicals.py (keys, year and month pieces, drivers, licence lines, the daily
    refresh and their place in the hourly backfill), and every piece rule accepts its own pieces;
  - a WordPress blog's posts of one month are read whole; a post without the blog's licence line, serialized fiction
    and stories republished from other outlets are left out and counted;
  - a site whose robots.txt says "ai-train=no" or shuts out AI readers by name is not read at all;
  - a blog read from its sitemaps keeps only the posts of the piece, with their dates and authors;
  - an archive read by halving finds the month's posts without reading every page;
  - the books carry the month in their title, the licence, and "personal use only" only for a non-commercial source;
  - copyrighted and refused blogs are in NOT_INCLUDED with their feed or archive address.

Run it from the repository's folder:   python3 -m pytest textbooks/test_blogs.py
"""

import datetime
import json
import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import blogs as G  # noqa: E402
import cookbooks  # noqa: E402
import periodicals as P  # noqa: E402
import sources  # noqa: E402

TODAY = datetime.date(2026, 11, 21)
COLOPHON = ("<p>This work &#8211; excluding any serialized fiction &#8211; is licensed under a Creative Commons "
            "Attribution 4.0 license.</p>")


def use(monkeypatch, routes):
    """Answer every request from routes [(piece of address, answer)]; anything else (robots.txt included) is 404."""
    asked = []

    def fetch(url, cache=None, binary=False, tries=4):
        asked.append(url)
        for piece, answer in routes:
            if piece in url:
                answer = answer(url) if callable(answer) else answer
                return answer.encode() if binary else answer
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(cookbooks, "_ai", {})
    return asked


def post(date, title, body, author="A. Writer", link=None):
    """One made-up post as the WordPress REST API gives it."""
    return {"id": 1, "date": f"{date}T10:00:00", "link": link or f"https://example.org/{date}/{len(title)}/",
            "title": {"rendered": title}, "content": {"rendered": body},
            "_embedded": {"author": [{"name": author}]}}


def test_registered():
    for name, spec in G.SOURCES.items():
        assert P.SOURCES[name] is spec and spec["driver"] in P.DRIVERS and spec["group"] in sources.GROUPS
        assert name in P.BACKFILL_ORDER and name in P.LICENCE_LINES
        pieces = spec["pieces"](TODAY) + P.ALL_PIECES[name](TODAY) + spec["daily"](TODAY) + ["2025-10"]
        assert all(re.match(spec["piece_rule"], p) for p in pieces), name
        assert P.ALL_PIECES[name](TODAY)[0] == "2025" and P.ALL_PIECES[name](TODAY)[-1] == str(spec["first_year"])
        assert B.licence_kind(spec["licence"], False) in ("open", "share-alike"), name   # CC BY, OGL; CC BY-SA
        assert f"pub:{name}:2026" in P.daily_keys(TODAY)
    order = P.BACKFILL_ORDER
    assert order.index("pluralistic") < order.index("voa") and order.index("eff_deeplinks") < order.index("uk_hansard")
    assert order.index("crs") < order.index("pluralistic")                     # the old order is kept around them
    assert P.expand_keys(["pub:pluralistic:2025-10", "pub:pluralistic:2025-13"], TODAY) == ["pub:pluralistic:2025-10"]
    assert P.piece_label("eff_deeplinks", "2025-10") == "October 2025" and P.piece_label("pluralistic", "2024") == "2024"
    assert P.piece_label("crs", "2026") == "2026"                             # the other sources keep their labels
    assert G.SOURCES["gds_accessibility_blog"]["group"] == "disability"


def test_span():
    assert G.span("2025") == (datetime.date(2025, 1, 1), datetime.date(2026, 1, 1))
    assert G.span("2025-12") == (datetime.date(2025, 12, 1), datetime.date(2026, 1, 1))
    assert G.in_piece("2025-10-31", "2025-10") and not G.in_piece("2025-11-01", "2025-10") and G.in_piece("2025-11", "2025")


def test_wordpress_month_whole_and_checked(monkeypatch):
    posts = [post("2025-10-20", "Enshittification, again", "<h2>Today's links</h2><p>Long essay.</p>" + COLOPHON),
             post("2025-10-12", "Red Team Blues (part 3 of 9)", "<p>Chapter text.</p>" + COLOPHON),
             post("2025-10-05", "No licence line", "<p>Missing colophon.</p>")]
    asked = use(monkeypatch, [("/robots.txt", "User-agent: *\nDisallow:\n"),
                              ("/wp-json/wp/v2/posts", json.dumps(posts))])
    left = []
    items = G.wordpress_items(G.SOURCES["pluralistic"], "2025-10", None, left, TODAY)
    assert [i["title"] for i in items] == ["Enshittification, again"]
    assert items[0]["date"] == "2025-10-20" and items[0]["unit"] == "October 2025"
    assert items[0]["byline"] == "By A. Writer, Cory Doctorow (Pluralistic)"
    assert "Today" in items[0]["body"] and "Creative Commons" in items[0]["body"]   # whole, colophon kept
    api = [u for u in asked if "/wp-json/" in u][0]
    assert "after=2025-10-01T00:00:00" in api and "before=2025-11-01T00:00:00" in api
    reasons = " ".join(x["reason"] for x in left)
    assert "1 posts were left out: they do not carry" in reasons and "serialized fiction" in reasons


def test_wordpress_republished_left_out(monkeypatch):
    posts = [post("2025-10-02", "Own story", "<p>Our reporting.</p>"),
             post("2025-10-01", "Partner story", "<p>This story was originally published by Other Outlet.</p>")]
    use(monkeypatch, [("/wp-json/wp/v2/posts", json.dumps(posts))])
    left = []
    items = G.wordpress_items(G.SOURCES["waging_nonviolence"], "2025-10", None, left, TODAY)
    assert [i["title"] for i in items] == ["Own story"] and "republished from other outlets" in left[0]["reason"]


def test_ai_refusing_site_is_not_read(monkeypatch):
    for robots in ("User-agent: *\nContent-Signal: search=yes,ai-train=no\nAllow: /\n",
                   "User-agent: *\nDisallow:\n\nUser-agent: ClaudeBot\nDisallow: /\n"):
        asked = use(monkeypatch, [("/robots.txt", robots), ("/wp-json/", json.dumps([post("2025-10-02", "x", "y")]))])
        left = []
        assert G.wordpress_items(G.SOURCES["waging_nonviolence"], "2025-10", None, left, TODAY) == []
        assert not [u for u in asked if "/wp-json/" in u] and "AI readers" in left[0]["reason"]


def page(date, title, body, author="Wiki Person"):
    """A made-up post page."""
    return (f'<html><head><meta property="og:title" content="{title}" />'
            f'<meta property="article:published_time" content="{date}T12:00:00+00:00" />'
            f'<meta name="author" content="{author}" /></head><body><nav>Menu</nav>'
            f'<div class="entry-content wrapper-small"><p>{body}</p><div><p>Inner block.</p></div></div>'
            f'<footer>Content licensed under Creative Commons Attribution-ShareAlike 4.0</footer></body></html>')


def test_sitemap_items(monkeypatch):
    base = "https://diff.wikimedia.org"
    use(monkeypatch, [
        ("/sitemap.xml", f"<sitemapindex><sitemap><loc>{base}/sitemap-1.xml</loc></sitemap></sitemapindex>"),
        ("/sitemap-1.xml", f"<urlset><url><loc>{base}/</loc></url><url><loc>{base}/2025/10/03/hello/</loc></url>"
                           f"<url><loc>{base}/2025/10/20/second/</loc></url>"
                           f"<url><loc>{base}/2025/09/30/old/</loc></url></urlset>"),
        ("/2025/10/03/hello/", page("2025-10-03", "Hello", "First post.")),
        ("/2025/10/20/second/", page("2025-10-20", "Second", "Later post."))])
    left = []
    items = G.sitemap_items(G.SOURCES["wikimedia_diff"], "2025-10", None, left, TODAY)
    assert [(i["title"], i["date"]) for i in items] == [("Second", "2025-10-20"), ("Hello", "2025-10-03")]
    assert "Inner block." in items[0]["body"] and "Menu" not in items[0]["body"]
    assert items[0]["byline"].startswith("By Wiki Person")


def test_archive_found_by_halving(monkeypatch):
    # 300 archive pages, newest first: page n lists posts of month (2026-11 minus n // 3 months).
    def month_of(n):
        y, m = divmod(2026 * 12 + 10 - n // 3, 12)
        return f"{y}/{m + 1:02d}"

    def archive(url):
        n = int(url.rsplit("=", 1)[1])
        if n >= 300:
            return "<html>No more.</html>"
        return "".join(f'<article class="node node--teaser"><a href="/deeplinks/{month_of(n)}/post-{n}-{k}">x</a>'
                       f'<a href="/deeplinks/2026/11/popular">related</a></article>' for k in range(2))

    def article(url):
        y, m = re.search(r"/deeplinks/(\d{4})/(\d\d)/", url).groups()
        return (f'<meta property="article:published_time" content="{y}-{m}-15T09:00:00-07:00" />'
                f'<meta property="og:title" content="{url.rsplit("/", 1)[1]}" />'
                f'<div class="field field--name-body field--type-text"><p>Body.</p></div>')
    asked = use(monkeypatch, [("/updates?page=", archive), ("/deeplinks/", article)])
    left = []
    items = G.archive_items(G.SOURCES["eff_deeplinks"], "2020-01", None, left, TODAY)
    assert items and all(i["date"].startswith("2020-01") for i in items)
    assert len(items) == 6                                   # 3 pages of that month, 2 posts each
    assert len([u for u in asked if "/updates?page=" in u]) < 25            # not 250 pages


def test_book_title_licence_and_personal_use(monkeypatch):
    items = [P.item("https://pluralistic.net/2025/10/20/x/", "Essay", "2025-10-20", "<p>Text.</p>", "October 2025")]
    book = P.make_book("pluralistic", "2025-10", items)
    assert book.title == "Pluralistic (Cory Doctorow), October 2025" and book.licence == "CC BY 4.0"
    assert book.personal_use is False and book.originals[0]["url"] == items[0]["url"]
    monkeypatch.setitem(G.SOURCES["pluralistic"], "personal_use", True)    # a non-commercial source would say so
    assert P.make_book("pluralistic", "2025-10", items).personal_use is True


def test_not_included_with_addresses():
    rows = {t: r for t, r in P.NOT_INCLUDED}
    for name in ("Boing Boing", "Techdirt", "Hackaday", "ProPublica", "Wired", "The 19th", "openDemocracy"):
        title = next(t for t in rows if t.startswith(name))
        assert re.search(r"(Feed|Archive|Feeds): https?://", rows[title]), title
    assert "ai-train=no" in rows[next(t for t in rows if t.startswith("Boing Boing"))]
