"""Audio and media production for the reference library, in its own group "Reference, audio and media production"
(the owner's request of 2026-11-22): recording, editing with a screen reader, podcasting, video basics, captions
and audio description, and keeping recordings safe for the long term. Keys: audio-media (every book), media:<name>.

What this module builds, in plain words, each IN FULL:
  - the Audacity Manual (version 3.7), every page: recording, editing, effects, generators and analysers, the menus,
    preferences and keyboard shortcuts, tutorials (recording from a microphone, making a podcast, digitising tapes
    and records), and exporting audio. Licensed CC BY 3.0 by the Audacity Team (its front page says so, checked at
    every build);
  - the OSARA guide (Open Source Accessibility for the REAPER Application, by James Teh, NV Access and others):
    installing OSARA, its keyboard commands for REAPER with a screen reader, reviewing and editing tracks and items,
    and its settings. GNU GPL version 2 (share-alike, a separate book), the line checked on the page at every build;
  - W3C WAI's "Making Audio and Video Media Accessible", every page: planning, captions and subtitles, transcripts,
    audio description, sign languages, media players and the people and organisations involved; kept whole and
    unchanged under the W3C Document License (like the WCAG books already in the library);
  - the Library of Congress's format descriptions for sound and moving images (Sustainability of Digital Formats):
    each audio and video format (WAVE, Broadcast WAVE, FLAC, MP3, AAC, MP4, Matroska and many more) and what it
    means for keeping recordings for the long term;
  - media:index, a guide to audio and media in the library: recording and microphones, editing with a screen
    reader, podcasting, video, captions and audio description standards, preservation, and the gear manuals.

Already in the library and linked, not repeated: WCAG 2.2 and the W3C techniques (nonprofit:w3c_wcag22 and the
others), the NVDA user guide and commands (atdoc:), the Library of Congress personal digital archiving guide
(pcb:loc_personal_digital_archiving), and the musical instruments and pro audio manuals (microphones, mixers, audio
interfaces, recorders).

Not built (NOT_INCLUDED, link-only): REAPER's own user guide (Cockos's copyright), the FCC's captioning and audio
description consumer guides (fcc.gov refuses programs), DCMP's Captioning Key and Description Key (copyright), and
the microphone and recorder makers' guides (the manual collection audio_gear lists them as links).

Licences: CC BY 3.0 (Audacity Manual), GPL-2.0 (OSARA), the W3C Document License (kept whole and unchanged), and works
of the US government (the Library of Congress's pages; 17 U.S.C. 105, the line checked on govinfo.gov's policies page
at every build).

Run from the repository's folder:
  python3 textbooks/audio_media.py media:osara_guide --out build/textbooks
  python3 textbooks/audio_media.py --list audio-media
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker

GROUP = "audiomedia"
GROUPS = {GROUP: "Reference, audio and media production"}

AUD = "https://manual.audacityteam.org"
AUD_LICENCE_PAGE = AUD + "/index.html"           # the front page's "Copyright:" paragraph
AUD_TEXT = r"Pages in this Manual are available under the terms of the Creative Commons Attribution 3\.0"
OSARA = "https://osara.reaperaccessibility.com/"
OSARA_TEXT = r"License: GNU General Public License version 2"
# The W3C fields, the same as sources.W3C (which cannot be imported here: sources imports this module at its end).
W3C_NOTICE = ("Copyright © World Wide Web Consortium (W3C®). Used under the W3C Document License "
              "(https://www.w3.org/copyright/document-license-2023/); the status of each document is on its page.")
W3C_FIELDS = dict(licence="W3C Document License", licence_url="https://www.w3.org/copyright/document-license-2023/",
                  unchanged=True, licence_page="https://www.w3.org/WAI/about/using-wai-material/",
                  licence_text=r"W3C Document License\s*,?\s*which grants permission to copy and distribute complete "
                               r"documents in any medium", page_mark=r"World Wide Web Consortium", sitemap="",
                  unit_rules=[], units="", content=(r"<main\b[^>]*>", r"</main>"), drop=[])
WAI_MEDIA = "https://www.w3.org/WAI/media/av/"
LOC_FDD = "https://www.loc.gov/preservation/digital/formats/fdd/"

GUIDES = [
    dict(K.WEB, group=GROUP, name="audacity_manual", title="Audacity Manual (version 3.7): recording, editing, "
         "effects and keyboard shortcuts", subject="Audio editing (Audacity)", publisher="The Audacity Team",
         country="International", licence="CC BY 3.0", licence_url="https://creativecommons.org/licenses/by/3.0/",
         licence_page=AUD_LICENCE_PAGE, licence_text=AUD_TEXT, source=AUD + "/index.html",
         crawl=[(AUD + "/index.html", 2), (AUD + "/man/subject_index.html", 1), (AUD + "/man/menu_reference.html", 1)],
         pages=r"^https://manual\.audacityteam\.org/man/(?!license|credits)[A-Za-z0-9_]+\.html$",
         content=(r'<div id="content"[^>]*>', r'<div id="footer"'),
         unit_rules=[(r"/man/tutorial", "Tutorials"), (r"/man/(effect|generat|analy|noise|nyquist)", "Effects, "
                      "generators and analyzers"), (r"/man/(.*_menu|menu_)", "Menus"),
                     (r"/man/(.*preferences|keyboard|shortcut)", "Preferences and keyboard shortcuts"),
                     (r".", "Using Audacity")], limit=900,
         description="The Audacity Manual, every page: the main window, tracks and selection, recording (from a "
                     "microphone, from a USB turntable or tape deck), editing (cut, copy, paste, split, labels), "
                     "every effect, generator and analyser (noise reduction, normalise, compressor, equalisation), "
                     "every menu, the preferences and the keyboard shortcuts, and the tutorials, including those for "
                     "making a podcast and digitising tapes and records, and exporting to MP3, WAV and other formats.",
         notice="The Audacity Manual, by the Audacity Team (manual.audacityteam.org), licensed under the Creative "
                "Commons Attribution 3.0 licence; the authors do not endorse this copy. Screenshots are left out; "
                "the manual describes Audacity 3.7. Keep the volume down when monitoring with headphones."),
    dict(K.WEB, group=GROUP, name="osara_guide", title="OSARA: Open Source Accessibility for the REAPER Application "
         "(user guide and keyboard commands)", subject="Audio editing with a screen reader (REAPER and OSARA)",
         publisher="James Teh, NV Access Limited and the OSARA contributors", country="International",
         licence="GPL-2.0", licence_url="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
         licence_page=OSARA, licence_text=OSARA_TEXT, source=OSARA, crawl=[(OSARA, 0)], urls=[OSARA],
         pages=r"^https://osara\.reaperaccessibility\.com/$", content=(r"<body\b[^>]*>", r"</body>"), limit=3,
         unit_rules=[(r".", "OSARA")],
         description="The OSARA guide, whole: what OSARA does for REAPER, installing it (with the SWS extension), "
                     "the keyboard commands it adds and the REAPER commands it makes speak (moving through tracks "
                     "and items, selecting, editing, envelopes, markers and regions, the mixer), peak and level "
                     "reports, its configuration and the key map.",
         notice="OSARA documentation, copyright NV Access Limited, James Teh and the OSARA contributors, licensed "
                "under the GNU General Public License version 2: share-alike, so anything made from it keeps the same "
                "licence. REAPER itself is Cockos's program; its own user guide is linked from the index, not "
                "copied."),
    dict(K.WEB, **W3C_FIELDS, group=GROUP, name="wai_media_accessibility", title="Making Audio and Video Media "
         "Accessible (W3C WAI)", subject="Captions, transcripts and audio description",
         publisher="W3C Web Accessibility Initiative (WAI)", country="International", notice=W3C_NOTICE,
         source=WAI_MEDIA, crawl=[(WAI_MEDIA, 1)], pages=r"^https://www\.w3\.org/WAI/media/av/([a-z-]+/)?$",
         limit=20,
         description="W3C WAI's media guide, every page whole and unchanged: planning audio and video content, "
                     "captions and subtitles, transcripts and how to transcribe, audio description (and how to write "
                     "a description script), sign languages, choosing an accessible media player, and who does what."),
    K.guide(GROUP, "loc_av_formats", "Sound and moving image formats for keeping recordings (Library of Congress)",
            "Audio and video formats and preservation", "Library of Congress (Sustainability of Digital Formats)",
            [LOC_FDD + "sound_fdd.shtml", LOC_FDD + "video_fdd.shtml"],
            r"^https://www\.loc\.gov/preservation/digital/formats/fdd/fdd\d{6}\.shtml$",
            "The Library of Congress's descriptions of the sound and moving image formats: each format (WAVE and "
            "Broadcast WAVE, AIFF, FLAC, MP3, AAC, Ogg Vorbis and Opus, MIDI, MP4 and QuickTime, Matroska, the "
            "DV and MPEG families and many more), what it holds, how open and widely used it is, and what it "
            "means for keeping recordings for the long term.",
            "From the Library of Congress: a work of the US government (public domain); source: Sustainability of "
            "Digital Formats, Library of Congress (loc.gov/preservation/digital/formats).", depth=1,
            content=(r'<div class="fdd">', r'<div align="right" class="update">'), limit=260,
            units=[(r".", "Format descriptions")]),
]

# ====================================================================== the index

SECTIONS = [
    ("Recording and microphones", "Microphones, recorders, levels and recording technique.", [
        ("key", "media:audacity_manual", "Recording in Audacity: levels, microphones and the recording tutorials"),
        ("manuals", "audio_gear", "Voice and field recorders, podcast microphones and headphones: makers' manuals, "
                                  "as links"),
        ("manuals", "musical_instruments", "Microphones, mixers, audio interfaces and multitrack recorders")]),
    ("Editing audio with a screen reader", "Audacity and REAPER with OSARA both work with NVDA and JAWS.", [
        ("key", "media:audacity_manual", "The Audacity Manual: editing, effects and keyboard shortcuts"),
        ("key", "media:osara_guide", "OSARA for REAPER: the keyboard commands"),
        ("key", "atdoc:nvda_key_commands", "NVDA's keyboard commands"),
        ("link", "REAPER user guide (Cockos)", "https://www.reaper.fm/userguide.php",
         "Cockos's copyright; open it in a browser or fetch it with Program Downloader"),
        ("link", "REAPER Accessibility Wiki (community)", "https://reaperaccessibility.com/",
         "the community's own terms; open it in a browser")]),
    ("Podcasting", "Planning, recording, editing and publishing a podcast.", [
        ("key", "media:audacity_manual", "Audacity's podcast and voice recording tutorials"),
        ("key", "media:wai_media_accessibility", "Transcripts for podcasts (W3C WAI)")]),
    ("Video, captions and audio description", "Captions, transcripts, audio description and the standards.", [
        ("key", "media:wai_media_accessibility", "Making Audio and Video Media Accessible (W3C WAI)"),
        ("key", "nonprofit:w3c_wcag22", "WCAG 2.2: the captions and audio description success criteria"),
        ("key", "nonprofit:w3c_understanding_wcag22", "Understanding WCAG 2.2"),
        ("link", "FCC: closed captioning on television", "https://www.fcc.gov/consumers/guides/closed-captioning-"
         "television", "fcc.gov refuses programs; open it in a browser"),
        ("link", "FCC: audio description", "https://www.fcc.gov/audio-description",
         "fcc.gov refuses programs; open it in a browser"),
        ("link", "DCMP Captioning Key and Description Key", "https://dcmp.org/learn/captioningkey",
         "the Described and Captioned Media Program's copyright; open it in a browser")]),
    ("Keeping recordings safe", "File formats and archiving for the long term.", [
        ("key", "media:loc_av_formats", "Sound and moving image formats (Library of Congress)"),
        ("key", "pcb:loc_personal_digital_archiving", "Personal digital archiving: audio, video and photos (Library "
                                                      "of Congress)")]),
]
INDEX = X.index_maker("media", GROUP, "Audio and media production: a guide to the library",
                      "Audio and media production", "A guide to audio and media in the library: recording and "
                      "microphones, editing with a screen reader, podcasting, video, captions and audio description, "
                      "and keeping recordings safe.", SECTIONS, country="International")
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("media", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"audio-media": lambda: ["media:index"] + [f"media:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "media_audacity": "manual.audacityteam.org/index.html (checked at every build): \"Pages in this Manual are "
                      "available under the terms of the Creative Commons Attribution 3.0 license\"; robots.txt: none "
                      "(the site answers 404, so every page is allowed); no AI rules (checked 2026-11-22).",
    "media_osara": "osara.reaperaccessibility.com (checked at every build): \"License: GNU General Public License "
                   "version 2.0\": share-alike, a separate book; no robots.txt rules.",
    "media_w3c": "W3C WAI's media guide under the W3C Document License (the same check as sources.W3C), kept whole "
                 "and unchanged.",
    "media_loc": "loc.gov/preservation/digital/formats: the Library of Congress's own descriptions, works of the US "
                 "government (17 U.S.C. 105); robots.txt allows the pages; no AI rules on www.loc.gov (checked "
                 "2026-11-22).",
    "media_index": "The index (media:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("REAPER User Guide (Cockos)", "Cockos's copyright; link-only from the index. OSARA's own guide (GPL) is built. "
     "Index: https://www.reaper.fm/userguide.php"),
    ("FCC consumer guides on closed captioning, audio description and the captioning rules (47 CFR 79)", "Public "
     "domain, but www.fcc.gov answers programs \"403\" (checked 2026-11-22). The rules themselves are in the eCFR "
     "(Title 47, part 79). Link-only. Index: https://www.fcc.gov/consumers/guides/closed-captioning-television"),
    ("DCMP Captioning Key and Description Key (Described and Captioned Media Program)", "Copyright of the National "
     "Association of the Deaf / DCMP; no open licence found. Link-only. Index: https://dcmp.org/learn/captioningkey"),
    ("Podcasting and microphone technique guides (makers' and broadcasters' guides)", "No openly licensed guide was "
     "found beyond the Audacity Manual's tutorials (built); the makers' guides are links in the manual collection "
     "audio_gear. Index: https://manual.audacityteam.org/man/tutorials.html"),
    ("Audacity Support site (support.audacityteam.org)", "Muse Group's own site with its own terms; the CC BY Audacity "
     "Manual is built instead. Index: https://support.audacityteam.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
