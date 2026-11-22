"""COMPUTER AND PHONE SCREENS for the Picture Model Training Kit (the owner's request of 2026-11-22: pictures for the
picture describer). This file lists the ready-made pack built in packs/screens_packs.py (group "permissive"; the kit
downloads it with prepare_pack) and what was looked at and left out, with the reason (SCREENS_NOT_INCLUDED):
  synthetic_screens  computer-made screens in generic Windows-like, Mac-like, Android-like and iPhone-like looks (no
                     company's logos, icons or trademarked designs): dialog boxes, save-changes questions, permission
                     prompts, error messages, update notices, settings, sign-in and two-step verification screens,
                     file pickers, print dialogs, CAPTCHAs (with the accessible way round), cookie banners, app store
                     pages, lock screens and notifications. Each is read in order (title, text, fields, buttons),
                     with the default and focused button and what each button does.

The screens already in the kit, which this pack extends: commons_screens (real screenshots from Wikimedia Commons,
everyday_extras_packs.py), and the research entries rico_screens, rico_widgets and screenqa_rico (Android app
screens, personal use). Scam screens (fake virus pop-ups, fake sign-in pages) are the synthetic_scam_examples pack
(privacy_sources.py), not drawn again here. Topic: documents (Documents, maps and signs), beside the phone screens
already there. Picture-making (SCREENS_PICTURE_MAKING_OK): none (a model must never learn to draw convincing system
screens).

    python -c "import sources, screens_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

SCREENS_SOURCES = [
    Source("synthetic_screens", "Computer and phone screens read in order: dialog boxes, error messages, permission "
                                "prompts, sign-in and code screens, settings, file pickers, print dialogs, CAPTCHAs, "
                                "cookie banners, app pages, lock screens; which button is the default and what each "
                                "does (computer-made, synthetic, ready-made pack)",
           "CC0 (drawn by packs/screens_packs.py from a fixed seed; generic looks, made-up apps)",
           "Computer-made by the kit's makers (packs/screens_packs.py)", "permissive", 3000, 30, prepare_pack,
           "about 300 MB"),
]

SCREENS_PICTURE_MAKING_OK = set()

SCREENS_NOT_INCLUDED = {
    "Screenshots of real programs and phones (Windows, macOS, Android, iOS, apps)": "the makers own their designs, "
        "icons and logos; only computer-made screens in generic looks are drawn, and commons_screens takes only "
        "Commons screenshots under CC0, public domain, CC BY, MIT or Apache.",
    "ScreenSpot, GUI-World, Mind2Web and other GUI-agent screenshot sets": "screenshots of third-party sites and apps "
        "with no licence for the pictures (see bigtech_sources.py); not used.",
    "Rico and ScreenQA": "already the research entries rico_screens, rico_widgets and screenqa_rico; not repeated.",
    "Fake virus pop-ups, fake sign-in pages and other scam screens": "the synthetic_scam_examples pack teaches their "
        "warning signs; they are not drawn twice.",
}
