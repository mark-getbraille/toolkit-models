"""Tests of the sources added in kit/sources_audio.py (audio with matching text, and government form letters). Every
archive, recording, book, page and letter here is made up; no network is used (a fake fetcher hands back the
made-up bytes)."""

import csv
import io
import json
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import build_dataset  # noqa: E402
import readers_more  # noqa: E402
import sources_audio as sa  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402


class FakeFetcher:
    """Hands back made-up bytes for each address (a dict); an unknown address is a 404."""

    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def get(self, url):
        self.asked.append(url)
        for key, value in self.pages.items():
            if url == key or (key.endswith("*") and url.startswith(key[:-1])):
                return value if isinstance(value, bytes) else value.encode("utf-8")
        import urllib.error
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)

    def open_stream(self, url):
        return io.BytesIO(self.get(url))


def targz(files):
    """A .tar.gz of {name: bytes or text} in the given order."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in files.items():
            data = data if isinstance(data, bytes) else data.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


LIBRISPEECH = targz({
    "LibriSpeech/LICENSE.TXT": "CC BY 4.0",
    "LibriSpeech/dev-clean/11/22/11-22-0001.flac": b"fLaC-one",
    "LibriSpeech/dev-clean/11/22/11-22-0000.flac": b"fLaC-zero",
    "LibriSpeech/dev-clean/11/22/11-22.trans.txt":
        "11-22-0000 THE KETTLE SANG ON THE HOB\n11-22-0001 AND THE CAT SLEPT\n",
    "LibriSpeech/dev-clean/11/22/11-22-0002.flac": b"fLaC-two",
})
LIBRITTS = targz({
    "./LibriTTS/dev-clean/33/44/33_44_000001_000000.normalized.txt": "Mister Brown came home.",
    "./LibriTTS/dev-clean/33/44/33_44_000001_000000.original.txt": "Mr. Brown came home.",
    "./LibriTTS/dev-clean/33/44/33_44_000001_000000.wav": b"RIFF-wave",
    "./LibriTTS/dev-clean/33/44/33_44_000002_000000.wav": b"RIFF-no-text",
})


def test_sources_registered():
    """The three sources are in writing_sources with their licences; librivox is opt-in; the new styles exist."""
    known = writing_sources.by_key()
    assert known["librispeech"].licence == "CC BY 4.0" and known["librispeech"].licence_class == writing_sources.OPEN
    assert known["gov_letters"].licence.startswith("Public domain")
    assert "ai-train=no" in known["librivox"].warnings[0] and "librivox" not in sa.OPT_IN
    assert {"nonfiction_prose", "form_letter"} <= set(styles.STYLES)
    assert any("ssa.gov" in why for _, why in writing_sources.NOT_USED)
    assert any("LibriVox's own website" in name for name, _ in writing_sources.NOT_USED)


def test_speech_pairs_any_order():
    """An utterance is given when both its audio and its text have been seen, whatever their order; audio without
    text is never given; LibriTTS uses the book's own text and keeps the normalized one."""
    pairs = list(sa.read_librispeech(FakeFetcher({sa.SPEECH_SETS[0][1]: LIBRISPEECH, sa.SPEECH_SETS[1][1]: LIBRITTS}),
                                     say=lambda _: None, audio_pairs=10))
    speech = [p for p in pairs if p["set"] == "librispeech-dev-clean"]
    assert [(p["audio_name"], p["text"]) for p in speech] == [("11-22-0000.flac", "THE KETTLE SANG ON THE HOB"),
                                                             ("11-22-0001.flac", "AND THE CAT SLEPT")]
    assert speech[0]["alignment"] == "utterance" and speech[0]["licence"] == "CC BY 4.0"
    assert speech[0]["speaker"] == "11" and speech[0]["chapter"] == "22"
    tts = [p for p in pairs if p["set"] == "libritts-dev-clean"]
    assert len(tts) == 1 and tts[0]["text"] == "Mr. Brown came home."
    assert tts[0]["normalized_text"] == "Mister Brown came home." and tts[0]["audio"] == b"RIFF-wave"


def test_speech_limit():
    """No more than the limit is taken from a set."""
    got = sa.speech_pairs(sa.tar_members(io.BytesIO(LIBRISPEECH)), "librispeech", 1)
    assert len(got) == 1


CATALOGUE_ROWS = [
    {"Text#": "11", "Type": "Text", "Title": "Alice's Adventures in Wonderland", "Language": "en",
     "Authors": "Carroll, Lewis, 1832-1898", "Subjects": "Fantasy fiction", "Bookshelves": "Children's Literature"},
    {"Text#": "28885", "Type": "Text", "Title": "Alice's Adventures in Wonderland", "Language": "en",
     "Authors": "Carroll, Lewis, 1832-1898", "Subjects": "Fantasy fiction", "Bookshelves": ""},
    {"Text#": "500", "Type": "Text", "Title": "A History of Kettles", "Language": "en",
     "Authors": "Smith, Jane, 1801-1870", "Subjects": "Kettles -- History", "Bookshelves": "History"},
]


def test_gutenberg_match():
    """A description's Gutenberg link wins; otherwise title and author surname, the lowest number; none without."""
    alice = sa.gutenberg_match(CATALOGUE_ROWS, "Alice's Adventures in Wonderland (version 2)", "Lewis Carroll")
    assert alice["Text#"] == "11"
    assert sa.gutenberg_match(CATALOGUE_ROWS, "Whatever", "Nobody",
                              "Text: http://www.gutenberg.org/etext/500")["Text#"] == "500"
    assert sa.gutenberg_match(CATALOGUE_ROWS, "The History of Kettles", "Jane Smith")["Text#"] == "500"
    assert sa.gutenberg_match(CATALOGUE_ROWS, "A History of Kettles", "Someone Else") is None
    assert sa.book_style(CATALOGUE_ROWS[0]) == "fiction_prose" and sa.book_style(CATALOGUE_ROWS[2]) == \
        "nonfiction_prose"


def book(chapters, toc=True):
    """A made-up Gutenberg file with a contents list and the given number of chapters."""
    words = " ".join(["The kettle sang softly while the old cat dreamed of mice in the warm kitchen."] * 40)
    parts = ["*** START OF THE PROJECT GUTENBERG EBOOK KETTLES ***", "A HISTORY OF KETTLES", ""]
    if toc:
        parts += [f"CHAPTER {n}. Part {n}" for n in range(1, chapters + 1)] + [""]
    for n in range(1, chapters + 1):
        parts += [f"CHAPTER {n}. Part {n}", "", f"Chapter {n} begins. " + words, "", words, "",
                  f"Chapter {n} goes on, and this sentence is long enough not to be taken for a heading.", ""]
    parts += ["*** END OF THE PROJECT GUTENBERG EBOOK KETTLES ***"]
    return "\n".join(parts)


def test_chapters_skip_contents():
    """The contents list's headings are not chapters."""
    chaps = sa.chapters_of(readers_more.gutenberg_body(book(3)))
    assert [h for h, _ in chaps] == ["CHAPTER 1. Part 1", "CHAPTER 2. Part 2", "CHAPTER 3. Part 3"]
    assert chaps[1][1].startswith("Chapter 2 begins.")


def catalogue_csv():
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(CATALOGUE_ROWS[0]))
    writer.writeheader()
    writer.writerows(CATALOGUE_ROWS)
    return buf.getvalue()


def librivox_pages(files):
    search = {"response": {"docs": [{"identifier": "kettles_librivox", "title": "A History of Kettles",
                                     "creator": "Jane Smith", "description": "A LibriVox recording."}]}}
    meta = {"files": [{"name": f"kettles_{n:02d}_64kb.mp3", "size": "1000", "length": "10:00", "artist": "Reader"}
                      for n in range(1, files + 1)] + [{"name": "kettles_01_128kb.mp3"}]}
    return {readers_more.GUTENBERG_MIRROR + "cache/epub/feeds/pg_catalog.csv": catalogue_csv(),
            "https://archive.org/advancedsearch.php*": json.dumps(search),
            readers_more.GUTENBERG_MIRROR + "cache/epub/500/pg500.txt": book(3),
            "https://archive.org/metadata/kettles_librivox": json.dumps(meta),
            "https://archive.org/download/kettles_librivox/*": b"ID3-mp3"}


def test_librivox_chapters_paired():
    """Each chapter's MP3 is paired with that chapter's text (chapter alignment), at most chapters of them; the book
    also gives nonfiction writing examples."""
    fetcher = FakeFetcher(librivox_pages(3))
    records = list(sa.read_librivox(fetcher, say=lambda _: None, books=1, chapters=2))
    audio = [r for r in records if r["type"] == "audio_pair"]
    assert [r["audio_name"] for r in audio] == ["kettles_01_64kb.mp3", "kettles_02_64kb.mp3"]
    assert audio[1]["text"].startswith("CHAPTER 2. Part 2\n\nChapter 2 begins.") and audio[1]["alignment"] == "chapter"
    assert audio[0]["book"] == "A History of Kettles" and audio[0]["author"] == "Jane Smith"
    assert audio[0]["text_url"].endswith("/pg500.txt") and "Public domain" in audio[0]["licence"]
    assert not any("librivox.org" in u for u in fetcher.asked)
    texts = [r for r in records if r["type"] == "text"]
    assert texts and all(r["style_label"] == "nonfiction_prose" for r in texts)
    assert texts[0]["instruction"].startswith("Continue this nonfiction book")


def test_librivox_mismatch_skipped():
    """A book whose recordings and chapters do not match one for one is skipped (nothing downloaded)."""
    fetcher = FakeFetcher(librivox_pages(5))
    said = []
    assert list(sa.read_librivox(fetcher, say=said.append, books=1)) == []
    assert "do not match" in said[0] and not any("/download/" in u for u in fetcher.asked)


def test_save_pair(tmp_path):
    """A pair is saved as its audio file and a .txt beside it, listed in pairs.jsonl; the README names the licence."""
    sa._STARTED.clear()
    pairs = list(sa.read_librispeech(FakeFetcher({sa.SPEECH_SETS[0][1]: LIBRISPEECH}), say=lambda _: None,
                                     sets=["librispeech-dev-clean"], audio_pairs=5))
    for p in pairs:
        sa.save_pair(str(tmp_path), "librispeech", p)
    folder = tmp_path / "librispeech"
    lines = [json.loads(x) for x in (folder / "pairs.jsonl").read_text("utf-8").splitlines()]
    assert len(lines) == 2 and lines[1]["audio"] == "librispeech-dev-clean_11/11-22-0001.flac"
    assert (folder / "librispeech-dev-clean_11" / "11-22-0001.txt").read_text("utf-8").strip() == "AND THE CAT SLEPT"
    assert (folder / "librispeech-dev-clean_11" / "11-22-0001.flac").read_bytes() == b"fLaC-one"
    assert "librispeech: CC BY 4.0" in (tmp_path / "README.txt").read_text("utf-8")


LETTER_MD = """---
title: 'Change in Enrollment Status'
author: Veterans Affairs
---

<div class="example-container">

addressee<br>
city

Dear addressee:

This letter is about the change in your enrollment. Because of this change, we may have paid you more than you were
due, and we need to hear from you soon about the reasons for the change in your credit hours.

### What We Need

Please send us a statement explaining why you reduced the number of your credit hours, with any evidence you have.

### When We Need It

Send us your statement within 30 days.

Sincerely,

</div>
"""
BEFORE_AFTER_MD = """---
title: Lead Warning
author: Environmental Protection Agency
---

* #### Before

  Exposure to lead-based paint hazards may result in adverse health effects in young children.

* #### After

  Lead paint can make young children sick.
{: .example-side-by-side}
"""
IRS_PAGE = ("<html><body><nav>Menu Home</nav><main><h1>Understanding your CP2000 notice</h1>"
            + "".join(f"<p>The information we received from third parties does not match your return, part {n}. "
                      "Review the notice and reply by the date listed so we can resolve it.</p>" for n in range(8))
            + "<h2>What you need to do</h2><ul><li>Review the notice.</li><li>Reply by the date listed.</li></ul>"
            + "<h2>Page Last Reviewed or Updated</h2><p>01-Jan-2026</p></main></body></html>")


def gov_pages():
    pages = {sa.PLG_RAW + "notices/change-in-enrollment-status.md": LETTER_MD,
             sa.PLG_RAW + "before-and-after/lead-warning.md": BEFORE_AFTER_MD,
             sa.IRS_SITEMAP: "<sitemapindex><sitemap><loc>https://www.irs.gov/sitemap.xml?page=1</loc></sitemap>"
                             "</sitemapindex>",
             "https://www.irs.gov/sitemap.xml?page=1": "<urlset>"
             "<url><loc>https://www.irs.gov/individuals/understanding-your-cp2000-notice</loc></url>"
             "<url><loc>https://www.irs.gov/individuals/understanding-your-irs-notice-or-letter</loc></url>"
             "<url><loc>https://www.irs.gov/newsroom/something</loc></url></urlset>",
             "https://www.irs.gov/individuals/understanding-your-cp2000-notice": IRS_PAGE}
    return pages


def test_gov_letters():
    """The plainlanguage.gov letter is a form letter with its headings in the instruction; a before-and-after page
    gives a rewrite pair; an IRS notice page gives its explanation without the page's closing parts; the IRS list
    page itself is not a notice."""
    fetcher = FakeFetcher(gov_pages())
    records = list(sa.read_gov_letters(fetcher, say=lambda _: None))
    letter = next(r for r in records if r["style_label"] == "form_letter")
    assert "What We Need; When We Need It" in letter["instruction"] and "Veterans Affairs" in letter["instruction"]
    assert "<br>" not in letter["response"] and "###" not in letter["response"] and "<div" not in letter["response"]
    assert "Send us your statement within 30 days." in letter["response"]
    assert "\n\nWhat We Need\n\nPlease send" in letter["response"]
    rewrite = next(r for r in records if r["kind"] == "plain-language rewrite")
    assert rewrite["response"] == "Lead paint can make young children sick."
    assert "adverse health effects" in rewrite["instruction"]
    irs = [r for r in records if r["group"] == "IRS"]
    assert len(irs) == 1 and "CP2000 notice" in irs[0]["instruction"]
    assert "Page Last Reviewed" not in irs[0]["response"] and "Menu Home" not in irs[0]["response"]
    assert "- Review the notice.\n\n- Reply by the date listed." in irs[0]["response"]
    assert not any(u.endswith("understanding-your-irs-notice-or-letter") for u in fetcher.asked)


def test_build_saves_audio_folder(tmp_path, monkeypatch):
    """build_dataset saves audio pairs in out/audio_text/<source>/ (not as examples), counts them in the report,
    and gives gov_letters' records their styles; librivox is left out unless named."""
    sa._STARTED.clear()
    source = writing_sources.by_key()["librispeech"]
    monkeypatch.setattr(sa, "SPEECH_SETS", sa.SPEECH_SETS[:1])
    fetcher = FakeFetcher({sa.SPEECH_SETS[0][1]: LIBRISPEECH})
    rows, counts = build_dataset.build_source(source, fetcher, 50, lambda _: None, set(), {"audio_pairs": 5},
                                              attach_dir=str(tmp_path / "messages"))
    assert rows == [] and counts["audio and text pairs saved"] == 2
    assert (tmp_path / "audio_text" / "librispeech" / "pairs.jsonl").exists()
    rows, counts = build_dataset.build_source(writing_sources.by_key()["gov_letters"], FakeFetcher(gov_pages()), 50,
                                              lambda _: None, set(), {}, attach_dir=str(tmp_path / "messages"))
    assert {r["style"] for r in rows} == {"form_letter", "plain_language_gov"}
    assert all(r["licence_class"] == writing_sources.OPEN for r in rows)
    seen = []
    monkeypatch.setattr(build_dataset, "build_source",
                        lambda source, *a, **k: (seen.append(source.key), ([], build_dataset.Counter()))[1])
    monkeypatch.setattr(build_dataset, "write_outputs", lambda *a, **k: ([], []))
    build_dataset.main(["--out", str(tmp_path / "out")])
    assert "librivox" in seen and "librispeech" in seen
    seen.clear()
    build_dataset.main(["--out", str(tmp_path / "out"), "--sources", "librivox"])
    assert seen == ["librivox"]
