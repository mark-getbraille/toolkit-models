"""PUBLIC-DOMAIN GOLDEN AGE COMICS for the Picture Model Training Kit (the owner's request of 2026-11-22: pictures for
the picture describer). This file lists the ready-made pack built in packs/comics_packs.py (group "permissive"; the
kit downloads it with prepare_pack) and what was looked at and left out, with the reason (COMICS_NOT_INCLUDED):
  commons_golden_age_comics  comic book covers, pages and panels of the 1930s to 1950s from Wikimedia Commons, only
                     files whose Commons page gives the evidence that they are in the US public domain (licence
                     templates PD-US-not renewed, PD-US-no notice or PD-US-expired). Answers quote the file's own
                     record (which comic, issue, page) and its public-domain basis; nothing describes the panels.

DESCRIBE IT YOURSELF: no transcriptions or panel descriptions of these comics exist, so the panels are never
described by the pack. Pictures whose record is too short are not thrown away: they go into the pack's needs zip
(needs-commons_golden_age_comics, release "needs-description"), which opens in the kit's "Describe pictures" window
(needs_workspace.py) as a review collection: a person describes the panel layout and what happens, and only pictures
a person marks checked are ever trained on. The same window takes any comic page the owner adds himself ("Your own
pictures"). Comics whose record names racist caricature or stereotypes are left out, not taught as normal.

Topic: art (Art and museum objects). Picture-making (COMICS_PICTURE_MAKING_OK): none (comic art is its artists'
style).

    python -c "import sources, comics_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMICS_SOURCES = [
    Source("commons_golden_age_comics", "Golden Age comic book covers and pages (1930s to 1950s) in the US public "
                                        "domain, with which comic, issue and page each is, from its own record "
                                        "(Wikimedia Commons, ready-made pack)",
           "Public domain in the United States (copyright not renewed, no notice, or expired; each file's basis in "
           "CREDITS.txt)", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org",
           "permissive", 1500, 20, prepare_pack, "about 300 MB"),
]

COMICS_PICTURE_MAKING_OK = set()

COMICS_NOT_INCLUDED = {
    "Digital Comic Museum (digitalcomicmuseum.com)": "its robots.txt (checked 2026-11-22) says 'Content-Signal: "
        "ai-train=no' and disallows ClaudeBot and anthropic-ai, so nothing is taken from it.",
    "Comic Book Plus (comicbookplus.com)": "its robots.txt (checked 2026-11-22) blocks AI training crawlers by name, "
        "ClaudeBot, anthropic-ai and Claude-Web included, so nothing is taken from it.",
    "Internet Archive comics uploads (comics_inbox, folkscanomy)": "public-domain and copyrighted comics mixed, with "
        "no evidence of non-renewal per item (Action Comics, Human Torch and other renewed titles are there); not "
        "used.",
    "Panel-by-panel descriptions of these comics": "none exist with an open licence; the pack's needs zip is the way "
        "to add them (see the module docstring), never invented answers.",
    "Comics whose records name racist caricature or stereotypes": "left out (they are not taught as normal).",
}
