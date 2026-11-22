"""Describing pictures and video for the reference library, in its own group "Reference, picture and video
description" (the owner's request of 2026-11-22: pictures for the picture describer, toward his video description
feature). Keys: describer-guides (every book), describe:<name>.

What this module builds, in plain words:
  - describe:cfr_47_79_video_accessibility: the FCC's rules for the accessibility of video programming, 47 CFR part
    79 IN FULL, from govinfo.gov's newest annual edition (the same way as the library's other CFR books): closed
    captioning (79.1), the video description rules (79.3: which stations and systems must carry audio description,
    how many hours, and passing it through), emergency information made accessible (79.2 and 79.105), and the rules
    for apparatus and menus (79.101 to 79.110). A work of the US government (17 U.S.C. 105). The eCFR's own site is
    not read: its robots.txt disallows its full-text services (see sources.NOT_INCLUDED); www.fcc.gov answers
    programs "403", so the FCC's consumer guides are links;
  - describe:index, a guide to describing pictures and video in the library: the audio description guidelines (W3C
    WAI's media guide, already built by audio_media.py as media:wai_media_accessibility, with its "audio description"
    and "description script" pages; WCAG 2.2's audio description criteria; the FCC rules above), the guidelines
    that are copyright and so only links (the DCMP Description Key, the American Council of the Blind's Audio
    Description Project, the FCC's consumer guide), describing images on the web (the WAI images tutorial), and the
    picture packs made for the describer (menus, formulas and structures, screens, film stills, comics).

Already in the library and linked, not repeated: media:wai_media_accessibility (audio_media.py), WCAG 2.2 and
Understanding WCAG 2.2 (nonprofit:), the WAI tutorials (nonprofit:w3c_wai_tutorials) and the
telecommunications accessibility rules (law:cfr_47_telecom_accessibility).

Not built (NOT_INCLUDED, link-only): the DCMP Description Key (copyright), the American Council of the Blind's Audio
Description Project guidelines (copyright), the FCC's audio description consumer guide (fcc.gov refuses programs).

Run from the repository's folder:
  python3 textbooks/audio_description.py describe:cfr_47_79_video_accessibility --out build/textbooks
  python3 textbooks/audio_description.py --list describer-guides
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker

GROUP = "describing"
GROUPS = {GROUP: "Reference, picture and video description"}

# (name, title, subject, title number, volume, part, description). Title 47 volume 4 holds parts 70 to 79.
CFR_PARTS = [
    ("cfr_47_79_video_accessibility", "Accessibility of Video Programming: closed captioning and audio (video) "
     "description (47 CFR Part 79)", "Audio description and captioning rules", 47, 4, 79,
     "The FCC's rules for accessible video programming: closed captioning of television and of video shown on the "
     "internet (79.1, 79.4), the video description (audio description) rules (79.3: which broadcast stations and "
     "pay-TV systems must carry it, how many hours each quarter, and passing it through to viewers), making "
     "emergency information accessible to blind and deaf viewers (79.2, 79.105), and the rules for the apparatus "
     "and on-screen menus that must let people turn captions and description on (79.101 to 79.110)."),
]
NOTICE = ("The Code of Federal Regulations, a work of the US government (public domain); this copy is not the official "
          "version. For a complaint about missing audio description or captions, contact the FCC (fcc.gov/complaints) "
          "or the TV provider.")


def cfr_book(name, work, cache=None, left_out=None, limit=None):
    """One CFR part (CFR_PARTS) as a book: sources.CFR's fields with this module's group and notice, built by
    build_textbooks.lawdoc_book from govinfo's newest annual edition."""
    import build_textbooks as B
    import sources
    _n, title, subject, t, vol, part, description = next(p for p in CFR_PARTS if p[0] == name)
    entry = sources._cfr(name, title, subject, t, vol, part, description, group=GROUP)
    entry["name"] = f"describe_{name}"
    entry["notice"] = NOTICE
    book = B.lawdoc_book(entry, cache, left_out)
    if book is not None and limit:
        book.pages = book.pages[:limit]
    return book


def cfr_sign(name):
    """A CFR part's sign of change: the newest annual edition's address (a new edition changes it)."""
    import build_textbooks as B
    _n, _title, _subject, t, vol, part, _d = next(p for p in CFR_PARTS if p[0] == name)
    url, _text = B.govinfo_edition("cfr", dict(title=t, volume=vol, part=part))
    return K.sha(url)


# ====================================================================== the index

SECTIONS = [
    ("Audio description guidelines", "How to describe what happens on screen for blind viewers: what to describe, "
     "when, and in what words.", [
        ("key", "media:wai_media_accessibility", "Making Audio and Video Media Accessible (W3C WAI): its audio "
                                                 "description pages and how to write a description script"),
        ("key", "nonprofit:w3c_wcag22", "WCAG 2.2: the audio description success criteria (1.2.3, 1.2.5, 1.2.7)"),
        ("key", "nonprofit:w3c_understanding_wcag22", "Understanding WCAG 2.2: what audio description is for"),
        ("link", "DCMP Description Key (Described and Captioned Media Program)", "https://dcmp.org/learn/"
         "descriptionkey", "the DCMP's copyright; open it in a browser or fetch it with Program Downloader"),
        ("link", "Audio Description Project (American Council of the Blind)", "https://adp.acb.org/",
         "the American Council of the Blind's copyright; open it in a browser")]),
    ("The rules in the United States", "Which programmes must carry audio description and captions.", [
        ("key", "describe:cfr_47_79_video_accessibility", "47 CFR part 79: captioning and video description rules"),
        ("key", "law:cfr_47_telecom_accessibility", "The FCC's other accessibility rules (47 CFR parts 6, 7, 14)"),
        ("link", "FCC: audio description", "https://www.fcc.gov/audio-description",
         "fcc.gov refuses programs; open it in a browser")]),
    ("Describing pictures", "Text alternatives and image descriptions.", [
        ("key", "nonprofit:w3c_wai_tutorials", "The W3C WAI tutorials, with the images tutorial (informative, "
                                               "decorative, functional and complex images)")]),
    ("Picture packs for the picture describer", "The packs that teach the describer to read and describe these.", [
        ("pack", "nypl_menus", "Historical menus with their transcribed dishes and prices (NYPL)"),
        ("pack", "synthetic_menus", "Modern menus read in order (computer-made)"),
        ("pack", "synthetic_formulas", "Printed formulas with their exact LaTeX and a spoken reading"),
        ("pack", "chem_structures", "Chemical structures with their names, formulas and SMILES"),
        ("pack", "synthetic_screens", "Computer and phone screens read in order, with what each button does"),
        ("pack", "pd_film_stills", "Stills from public-domain films with each film's own record"),
        ("pack", "commons_golden_age_comics", "Public-domain Golden Age comics with their own records")]),
]
INDEX = X.index_maker("describe", GROUP, "Describing pictures and video: a guide to the library",
                      "Picture and video description", "A guide to describing pictures and video in the library: "
                      "audio description guidelines, the US rules, describing images, and the describer's picture "
                      "packs.", SECTIONS)
MAKERS = {"index": INDEX}
MAKERS.update({name: (cfr_book, cfr_sign) for name, *_rest in CFR_PARTS})

COLLECTION = K.Collection("describe", GROUP, makers=MAKERS,
                          words={"describer-guides": lambda: ["describe:index"] +
                                 [f"describe:{p[0]}" for p in CFR_PARTS]})

LICENCE_LINES = {
    "describe_cfr": "47 CFR part 79 from govinfo.gov's annual edition: a work of the US government (17 U.S.C. 105), "
                    "the line checked on govinfo.gov's policies page at every build, as for the library's other CFR "
                    "books; govinfo.gov's robots.txt allows /content/pkg/ (checked 2026-11-22).",
    "describe_index": "The index (describe:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("DCMP Description Key (Described and Captioned Media Program)", "Copyright of the National Association of the "
     "Deaf / DCMP; no open licence found, and dcmp.org refuses programs (403, checked 2026-11-22). Link-only. "
     "Index: https://dcmp.org/learn/descriptionkey"),
    ("American Council of the Blind, Audio Description Project guidelines", "\"Website Design & Content © 2026 "
     "American Council of the Blind\"; not openly licensed. Link-only. Index: https://adp.acb.org/"),
    ("FCC consumer guide: audio description", "Public domain, but www.fcc.gov answers programs \"403\" (checked "
     "2026-11-22); the rules themselves (47 CFR part 79) are built from govinfo.gov. Index: "
     "https://www.fcc.gov/audio-description"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
