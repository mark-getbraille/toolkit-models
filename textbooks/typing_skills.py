"""Typing and keyboard skills for the reference library, in its own group "Reference, typing and keyboard skills" (the
owner's request of 2026-11-22). Keys: typing (every book), typing:<name>.

What this module builds, in plain words:
  - four old public-domain touch typing courses (published before 1931) from the Internet Archive, each whole with a
    note on what is out of date: Practical Typewriting by the All-Finger Method, Which Leads to Operation by Touch
    (Torrey, 1894), Expert Typewriting (Eldridge, 1912), 20th Century Touch Typewriting (Grisso, 1920) and A
    Scientific Course in Typewriting (Depew, 1922). Their home-row method, finger charts and graded drills still
    teach touch typing on a modern QWERTY keyboard; their machines' carriage returns, margins and paper handling do
    not apply to a computer;
  - typing:index, a guide to keyboard skills in the library: touch typing, keyboard layouts, screen reader keyboard
    commands (the NVDA and Orca guides already in the library), Windows and Mac keyboard shortcuts (links: the
    makers' copyright), and braille keyboards (Perkins-style six-key input on phones and braille displays: the
    vision section).

Not built (NOT_INCLUDED, link-only): Microsoft's and Apple's keyboard shortcut pages and the JAWS, Narrator and
VoiceOver command references (the makers' copyright), modern typing tutors (copyright or paid), and a modern
openly licensed typing course (none found beyond Wikibooks, which is in the Kiwix library).

Licences: the old books' Internet Archive records must show a date before 1931 (checked at every build); the index is
CC0.

Run from the repository's folder:
  python3 textbooks/typing_skills.py typing:depew_scientific_course_typewriting_1922 --out build/textbooks --limit 5
  python3 textbooks/typing_skills.py --list typing
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker
from old_ia_books import old_book  # noqa: E402

GROUP = "typing"
GROUPS = {GROUP: "Reference, typing and keyboard skills"}
OLD_NOTE = ("Published in {year} for typewriters: the home-row method, the finger chart and the drills still work on "
            "a computer's QWERTY keyboard, but the carriage return, margin, tabulator and paper instructions do not "
            "apply (on a computer, Enter starts a new paragraph). The machine-read text of its drills may have "
            "scanning mistakes.")


def _old(name, title, publisher, archive, year, description):
    """One old public-domain typing course (published before 1931) with the typewriter note."""
    return old_book(GROUP, name, title, "Touch typing", publisher, archive, year, description, note=OLD_NOTE)


PDFS = [
    _old("torrey_practical_typewriting_1894", "Practical Typewriting by the All-Finger Method, Which Leads to "
         "Operation by Touch (Torrey, 1894)", "Bates Torrey (Fowler and Wells Company)", "practicaltypewri00torr",
         1894, "One of the first touch typing courses: using all the fingers, the place of each finger on the "
         "keyboard, graded exercises from single letters to words, sentences and business letters, and typing "
         "without looking at the keys."),
    _old("eldridge_expert_typewriting_1912", "Expert Typewriting (Eldridge, 1912)", "Fritz Eldridge (American Book "
         "Company)", "experttypewritin0000unse", 1912,
         "A school course in touch typing: posture, the home keys, lessons that add a few keys at a time, rhythm "
         "drills, accuracy before speed, and practice copy for letters and documents."),
    _old("grisso_20th_century_touch_typewriting_1920", "20th Century Touch Typewriting (Grisso, 1920)",
         "I. E. Grisso", "20thcenturytouch0000iegr", 1920,
         "A graded touch typing course: the keyboard by rows, finger reaches, drills for the letters, figures and "
         "symbols, speed and accuracy tests, and business forms."),
    _old("depew_scientific_course_typewriting_1922", "A Scientific Course in Typewriting (Depew, 1922)",
         "Ollie Depew (Allyn and Bacon)", "scientificcourse00depe", 1922,
         "A touch typing course built on the study of how typists learn: correct posture and stroking, the home "
         "row, reaches to the upper and lower rows, rhythm, and graded speed practice."),
]

# ====================================================================== the index

SECTIONS = [
    ("Touch typing", "Learning to type without looking: the home row (A S D F with the left hand, J K L ; with the "
     "right; the small bumps on F and J help you find it), then one row at a time.", [
         ("key", "typing:torrey_practical_typewriting_1894", "Practical Typewriting by the All-Finger Method (1894)"),
         ("key", "typing:eldridge_expert_typewriting_1912", "Expert Typewriting (1912)"),
         ("key", "typing:grisso_20th_century_touch_typewriting_1920", "20th Century Touch Typewriting (1920)"),
         ("key", "typing:depew_scientific_course_typewriting_1922", "A Scientific Course in Typewriting (1922)"),
         ("key", "atdoc:nvda_user_guide", "NVDA's input help mode (press NVDA+1, then any key to hear its name): "
                                          "the NVDA User Guide")]),
    ("Screen reader keyboard commands", "The commands of the screen readers.", [
        ("key", "atdoc:nvda_key_commands", "NVDA Commands Quick Reference"),
        ("key", "atdoc:nvda_user_guide", "NVDA User Guide"),
        ("key", "vision:orca_help", "Orca screen reader help (Linux)"),
        ("link", "JAWS keyboard commands (Freedom Scientific)", "https://support.freedomscientific.com/Content/"
         "Documents/Manuals/JAWS/Keystrokes.pdf", "Vispero's copyright; open it in a browser"),
        ("link", "Narrator keyboard commands (Microsoft)", "https://support.microsoft.com/en-us/windows/"
         "appendix-b-narrator-keyboard-commands-and-touch-gestures-8bdab3f4-b3e9-4554-7f28-8b15bd37410a",
         "Microsoft's copyright; open it in a browser"),
        ("link", "VoiceOver commands for Mac (Apple)", "https://support.apple.com/guide/voiceover/welcome/mac",
         "Apple's copyright; open it in a browser")]),
    ("Windows and Mac keyboard shortcuts", "The shortcuts for the computer itself.", [
        ("link", "Keyboard shortcuts in Windows (Microsoft)", "https://support.microsoft.com/en-us/windows/"
         "keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec", "Microsoft's copyright"),
        ("link", "Mac keyboard shortcuts (Apple)", "https://support.apple.com/en-us/102650", "Apple's copyright"),
        ("word", "computer-basics", "Computer and phone basics, with the LibreOffice guides' shortcuts")]),
    ("Keyboard layouts", "QWERTY, Dvorak and the keyboards of other languages.", [
        ("link", "Windows keyboard layouts (Microsoft)", "https://learn.microsoft.com/en-us/globalization/"
         "windows-keyboard-layouts", "Microsoft's copyright; each layout shown as a picture"),
        ("word", "languages", "Language courses: typing in another language starts with its keyboard")]),
    ("Braille keyboards", "Six-key Perkins-style typing on braille displays, braille writers and phones (screen input "
     "on iPhone and Android).", [
        ("key", "vision:index", "Blind and low-vision living: braille, braille writers and braille displays"),
        ("word", "vision-living", "The vision section's books (request word)"),
        ("link", "Braille Screen Input on iPhone (Apple)", "https://support.apple.com/guide/iphone/type-onscreen-"
         "braille-iph10366cc30/ios", "Apple's copyright; open it in a browser"),
        ("link", "TalkBack braille keyboard (Google)", "https://support.google.com/accessibility/android/answer/"
         "9728765", "Google's copyright; open it in a browser")]),
]
INDEX = X.index_maker("typing", GROUP, "Typing and keyboard skills: a guide to the library", "Typing and keyboard "
                      "skills", "A guide to keyboard skills in the library: touch typing, screen reader commands, "
                      "Windows and Mac shortcuts, keyboard layouts and braille keyboards.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("typing", GROUP, pdfs=PDFS, makers=MAKERS,
                          words={"typing": lambda: ["typing:index"] + [f"typing:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "typing_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                        "a later reprint is refused); archive.org's robots.txt allows the files; no AI rules "
                        "(checked 2026-11-22).",
    "typing_index": "The index (typing:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Microsoft and Apple keyboard shortcut pages; JAWS, Narrator, VoiceOver and TalkBack command references",
     "The makers' copyright; link-only from the index (typing:index). NVDA's own guides are already in the library "
     "(atdoc:). Index: https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-"
     "9796-cb9706c75eec"),
    ("Modern typing tutors (Talking Typer, TypingClub, Typio, Keybr and others)", "Copyright or paid programs; "
     "link-only. Index: https://www.aph.org/"),
    ("Openly licensed modern touch typing course", "None found beyond the Wikibooks typing book, which is already in "
     "the Kiwix library (Wikibooks in full). Index: https://en.wikibooks.org/wiki/Typing"),
    ("Rational Typewriting (SoRelle and Cutler, 1916) and The Van Sant System of Touch Typewriting (1902)", "Public "
     "domain, but their Internet Archive scans are 300 to 450 MB each, too large for the builder's pass; four other "
     "courses of the same period are built. Index: https://archive.org/details/RationalTypewriting-RevisedEdition"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
