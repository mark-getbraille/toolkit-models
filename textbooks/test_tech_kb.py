"""Self-test of the computer-help documentation added on 2026-11-22 (tech_kb.py), with MADE-UP articles only:
nothing is downloaded or cloned.

It checks that:
  - every book is registered once in the group "techdocs", with a licence the toolkit may repackage, asked for by
    techdocs, tech:microsoft, tech:apple and one key each; the builder and the weekly check send tech: keys here;
  - DocFX Markdown becomes HTML: front matter title and date, code blocks kept, notes as quotations, pictures as
    their descriptions, includes inlined, zone and moniker marks dropped, links between articles of the book pointed
    at its pages, site links made absolute, other links as plain words;
  - DocC Markdown (the Swift book): <doc:> links, double-backtick code and @Metadata blocks;
  - the articles come in order (DocC by the book's topic list; others index first), without partials or includes;
  - the current long-term-support PowerShell version is found;
  - a book whose repository no longer states its licence is not built; the copyrighted sources are recorded with
    their index or sitemap for the Program Downloader.

Run it from the repository's folder:   python3 -m pytest textbooks/test_tech_kb.py
"""

import os
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import refs_common as R  # noqa: E402
import sources  # noqa: E402
import tech_kb as T  # noqa: E402
import updates  # noqa: E402


def write(path, text):
    """Write a made-up file (its folders made)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_registered_in_the_techdocs_group():
    assert sources.GROUPS["techdocs"] == "Reference, computer help and technology"
    keys = T.all_keys()
    assert len(keys) == len(set(keys)) == len(T.BOOKS)
    assert sources.expand_keys(["techdocs"]) == keys == sources.expand_keys(["group:techdocs"])
    assert sources.expand_keys(["tech:apple"]) == ["tech:swift_book", "tech:swift_org_docs"]
    assert R.module_for("tech:ms_teams_support") is T
    for b in T.BOOKS:
        lic = T.APACHE if b in T.APPLE_BOOKS else T.CC_BY
        assert B.licence_kind(B.licence_short(lic), False) == "open", b["name"]
        assert b["repo"] and b["branch"] and b["folders"] and b["source"].startswith("https://"), b["name"]
    assert set(T.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in T.NOT_INCLUDED)
    text = " ".join(t + " " + w for t, w in T.NOT_INCLUDED)
    for words in ("support.microsoft.com/_sitemaps/sitemapindex.xml", "sitemap-index-en-us.xml", "Narrator",
                  "VoiceOver", "Human Interface Guidelines"):
        assert words in text, words


def test_builder_and_weekly_check_send_tech_keys_here(monkeypatch, tmp_path):
    monkeypatch.setattr(T, "sign", lambda key: f"signed {key}")
    assert updates.fingerprint("tech:swift_book") == "signed tech:swift_book"
    called = []
    monkeypatch.setattr(T, "build", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["tech:ms_powershell"], str(tmp_path))
    assert called == [["tech:ms_powershell"]]


DOCFX = """---
title: Fix a frozen screen
ms.date: 03/04/2025
---
# Fix a frozen screen

Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Delete</kbd>. See [the overview](overview.md#start), [Narrator](/windows/narrator)
and [an outside page](https://www.example.org/x) and [a page not in this book](../other/missing.md).

> [!NOTE]
> Save your work first.

[!INCLUDE [shared](../includes/shared-step.md)]

:::image type="content" source="media/screen.png" alt-text="The Task Manager window.":::

::: zone pivot="windows-11"
```powershell
# a comment, not a heading
Get-Process | Stop-Process -Name "x"
```
::: zone-end
"""


def test_docfx_article(tmp_path):
    root = str(tmp_path)
    write(os.path.join(root, "support", "includes", "shared-step.md"), "---\nms.topic: include\n---\nRestart the "
                                                                       "computer.\n")
    here = os.path.join(root, "support", "windows", "frozen.md")
    links = {os.path.normpath(os.path.join(root, "support", "windows", "overview.md")): "support-windows-overview"}
    title, out = T.md_page(DOCFX, here, root, links)
    assert title == "Fix a frozen screen" and "<h1" not in out and "# Fix" not in out
    assert '<a href="support-windows-overview#start">the overview</a>' in out
    assert '<a href="https://learn.microsoft.com/windows/narrator">Narrator</a>' in out
    assert '<a href="https://www.example.org/x">an outside page</a>' in out and "a page not in this book" in out
    assert "missing.md" not in out
    assert "<blockquote><p><strong>Note:</strong> Save your work first.</p></blockquote>" in out
    assert "Restart the computer." in out and "ms.topic" not in out
    assert "(Picture: The Task Manager window.)" in out
    assert "<pre><code># a comment, not a heading\nGet-Process | Stop-Process -Name &quot;x&quot;</code></pre>" in out
    assert ":::" not in out and "zone" not in out
    assert T.ms_date("03/04/2025") == "2025-03-04" and T.ms_date("2025-11-04T00:00") == "2025-11-04"


def test_docc_article(tmp_path):
    text = ("# The Basics\n\n@Metadata {\n  @Available(Swift, introduced: 5.0)\n}\n\nUse ``Int`` for integers, "
            "as described in <doc:CollectionTypes#Arrays> and <doc:Missing>.\n\n> Note: Constants can't change.\n")
    title, out = T.md_page(text, str(tmp_path / "TheBasics.md"), str(tmp_path), {"doc:CollectionTypes": "tspl-ct"},
                           "docc")
    assert title == "The Basics" and "@Metadata" not in out and "@Available" not in out
    assert "<code>Int</code>" in out and "``" not in out
    assert '<a href="tspl-ct#Arrays">Collection Types</a>' in out and "Missing" in out and "doc:" not in out
    assert "<blockquote><p>Note: Constants can&#x27;t change.</p></blockquote>" in out or \
        "<blockquote><p>Note: Constants can't change.</p></blockquote>" in out


def test_article_order(tmp_path):
    root = str(tmp_path)
    docc = os.path.join(root, "TSPL.docc")
    write(os.path.join(docc, "The-Swift-Programming-Language.md"), "# TSPL\n## Topics\n### Welcome to Swift\n- "
          "<doc:AboutSwift>\n### Language Guide\n- <doc:TheBasics>\n")
    write(os.path.join(docc, "LanguageGuide", "TheBasics.md"), "# The Basics\n")
    write(os.path.join(docc, "GuidedTour", "AboutSwift.md"), "# About Swift\n")
    got = T.articles(root, ["TSPL.docc"], "docc")
    assert [(u, os.path.basename(p)) for u, p in got] == [("Welcome to Swift", "AboutSwift.md"),
                                                          ("Language Guide", "TheBasics.md")]
    for rel in ("support/windows/zeta.md", "support/windows/index.md", "support/windows/_partial.md",
                "support/windows/includes/x.md", "support/windows/printing/a.md", "support/windows/toc.md"):
        write(os.path.join(root, rel), "# x\n")
    got = T.articles(root, ["support/windows"], "docfx")
    assert [(u, os.path.relpath(p, root)) for u, p in got] == [
        ("Overview", "support/windows/index.md"), ("Overview", "support/windows/zeta.md"),
        ("Printing", "support/windows/printing/a.md")]


def test_powershell_lts(tmp_path):
    root = str(tmp_path)
    for v in ("5.1", "7.4", "7.6", "7.7"):
        os.makedirs(os.path.join(root, "reference", v))
    assert T.lts_version(root) == "7.6"                    # the newest but one when the article is missing
    write(os.path.join(root, "reference", "docs-conceptual", "install", "PowerShell-Support-Lifecycle.md"),
          "The current LTS release is PowerShell 7.4.20.")
    assert T.lts_version(root) == "7.4"


def test_licence_checked_before_cloning(monkeypatch):
    monkeypatch.setattr(R, "shallow_clone", lambda *a, **k: (_ for _ in ()).throw(AssertionError("cloned")))

    def fetch(url, cache=None, binary=False, tries=4):
        if url.endswith("/LICENSE"):
            return "All rights reserved."
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(D, "_ai", {})
    left_out = []
    assert T.books_for("tech:ms_teams_support", "work", None, left_out) == []
    assert "licence" in left_out[0]["reason"]
