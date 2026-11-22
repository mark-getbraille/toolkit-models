"""When Wikimedia Commons keeps refusing (429) part-way through a Commons topic pack, the pictures already found are
kept instead of losing hours of work (commons_home_repair failed this way on 22 November 2026). Nothing here goes to
the internet: the Commons calls are replaced with made-up answers."""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import home_packs as h  # noqa: E402


def fake(monkeypatch, refuse_after):
    calls = {"n": 0}

    def entries(s, batch):
        calls["n"] += 1
        if calls["n"] > refuse_after:
            raise RuntimeError("Wikimedia Commons kept refusing requests (429); try again later.")
        return [(t, f"https://example.org/{t}", "credit", "") for t in batch]

    monkeypatch.setattr(h, "session", lambda: None)
    monkeypatch.setattr(h, "category_files", lambda s, c, d: [f"File:{c}-{i}.jpg" for i in range(40)])
    monkeypatch.setattr(h, "home_entries", entries)
    monkeypatch.setattr(h, "commons_fetch", lambda items: items)
    monkeypatch.setattr(h, "with_twins", lambda items: items)


SPECS = [("Hammers", 0, [("What is this?", "This is a hammer.")]),
         ("Saws", 0, [("What is this?", "This is a saw.")])]


def test_refusal_keeps_what_was_found(monkeypatch):
    fake(monkeypatch, refuse_after=1)
    got = h.build_commons_topic(SPECS, 40, "test")
    assert got, "the pictures found before Commons stopped answering are kept"


def test_refusal_with_nothing_found_still_fails(monkeypatch):
    fake(monkeypatch, refuse_after=0)
    with pytest.raises(RuntimeError):
        h.build_commons_topic(SPECS, 40, "test")
