"""Tests of the polite downloader (kit/fetch.py): robots.txt rules, AI-training signals, waits and the cache. No
network is used: the robots.txt texts are made up and the "site" is a fake opener."""

import io
import os
import sys
import urllib.error

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import fetch  # noqa: E402


@pytest.fixture(autouse=True)
def short_waits(monkeypatch):
    """The tests do not need the real 3-second wait between requests."""
    monkeypatch.setattr(fetch, "DEFAULT_DELAY", 0.01)


def robots(text):
    return fetch.Robots("https://example.com", text)


def test_ai_train_no_refuses_the_site():
    r = robots("User-agent: *\nContent-Signal: search=yes,ai-train=no\nAllow: /\n")
    allowed, reason, _ = r.check("https://example.com/page")
    assert not allowed and "ai-train=no" in reason


def test_content_signal_for_another_crawler_only_does_not_count():
    r = robots("User-agent: SomeBot\nContent-Signal: ai-train=no\nDisallow: /\n\nUser-agent: *\nAllow: /\n")
    assert r.signals == {}
    assert r.check("https://example.com/page")[0]


def test_blocking_ai_training_crawlers_refuses_the_site():
    r = robots("User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n")
    allowed, reason, _ = r.check("https://example.com/page")
    assert not allowed and "GPTBot" in reason


def test_blocking_single_company_crawlers_is_only_a_warning():
    r = robots("User-agent: Bytespider\nDisallow: /\n\nUser-agent: *\nCrawl-delay: 10\n")
    allowed, _, warnings = r.check("https://example.com/page")
    assert allowed and warnings and "Bytespider" in warnings[0]
    assert r.delay == 10


def test_closed_paths_are_refused_and_open_ones_allowed():
    r = robots("User-agent: *\nDisallow: */mboxes/\nDisallow: /Archives/Member/\n")
    assert not r.check("https://example.com/Archives/Public/list/mboxes/2024.mbx")[0]
    assert not r.check("https://example.com/Archives/Member/x")[0]
    assert r.check("https://example.com/Archives/Public/list/2024JanMar/0001.html")[0]
    assert r.delay == fetch.DEFAULT_DELAY


class FakeOpener:
    """Answers robots.txt with a given text and every other address with its own name; counts the requests."""

    def __init__(self, robots_text, missing=False):
        self.robots_text = robots_text
        self.missing = missing
        self.asked = []

    def open(self, req, timeout=60):
        url = req.full_url
        self.asked.append(url)
        if url.endswith("/robots.txt"):
            if self.missing:
                raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
            return io.BytesIO(self.robots_text.encode())
        return io.BytesIO(url.encode())


def test_fetcher_obeys_robots_and_keeps_its_name(tmp_path):
    opener = FakeOpener("User-agent: *\nDisallow: /private/\n")
    f = fetch.Fetcher(say=lambda t: None, opener=opener)
    assert f.get("https://example.com/open/page") == b"https://example.com/open/page"
    with pytest.raises(fetch.RobotsRefusal):
        f.get("https://example.com/private/page")
    assert opener.asked.count("https://example.com/robots.txt") == 1     # read once per site
    assert "private" not in " ".join(opener.asked)


def test_a_site_without_robots_txt_is_open():
    f = fetch.Fetcher(say=lambda t: None, opener=FakeOpener("", missing=True))
    assert f.get("https://example.org/a") == b"https://example.org/a"


def test_cache_means_a_page_is_only_downloaded_once(tmp_path):
    opener = FakeOpener("User-agent: *\nAllow: /\n")
    f = fetch.Fetcher(say=lambda t: None, opener=opener, cache_dir=str(tmp_path))
    f.get("https://example.com/p")
    f.get("https://example.com/p")
    assert opener.asked.count("https://example.com/p") == 1


def test_the_user_agent_names_no_person():
    assert "WritingKit" in fetch.USER_AGENT and "@" not in fetch.USER_AGENT


def test_wildcard_rules_are_obeyed():
    r = robots("User-agent: *\nDisallow: /*/*/download/*\nDisallow: /*.atom$\nAllow: /open/*.atom$\n")
    assert not r.check("https://example.com/owner/repo/releases/download/v1/file.zip")[0]
    assert not r.check("https://example.com/feed.atom")[0]
    assert r.check("https://example.com/feed.atom?x=1")[0]
    assert r.check("https://example.com/open/feed.atom")[0]
    assert r.check("https://example.com/owner/repo")[0]


def test_a_group_for_this_kit_replaces_the_star_group():
    r = robots("User-agent: *\nAllow: /\n\nUser-agent: WritingKit\nDisallow: /private/*\n")
    assert r.check("https://example.com/page")[0]
    assert not r.check("https://example.com/private/page")[0]
