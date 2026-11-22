"""Stack Exchange's practical how-to sites as REFERENCE BOOKS ONLY (the owner's request of 2026-11-22), in their own
group "Reference, Stack Exchange (reading only)". Keys: stack-exchange (every book), se:<name>.

READING ONLY, NEVER TRAINING. Stack Exchange now restricts the use of its content to train AI: its robots.txt
(stackexchange.com, checked 2026-11-22) says "Content-signal: search=no, ai-train=no" and "Disallow: /" to every
program. So:
  - nothing here ever reads a Stack Exchange website (the robots.txt above turns programs away anyway);
  - the questions and answers come only from the Kiwix project's ready-made ZIM files of each site
    (download.kiwix.org/zim/stack_exchange/), which the owner's apps already list from the Kiwix catalogue; they are
    NOT rebuilt here. This module adds, for each one, a label (KIWIX_LABELS, merged into textbooks.json
    "kiwix_labels") and its name in KIWIX_REFERENCE_ONLY (textbooks.json "kiwix_reference_only"), so the toolkit
    shows the notice and keeps them out of anything that trains a model;
  - every entry carries reference_only=True and REFERENCE_ONLY_NOTICE, and every book this module writes carries
    "reference_only": true in its catalogue entry (ReferenceOnlyCollection);
  - the self-tests (textbooks/test_stack_exchange.py and training-kit/tests/test_no_stack_exchange.py) check that no
    picture pack, training-kit collection or topic add-on names a Stack Exchange site or one of these Kiwix books.

What this module builds, in plain words: se:index, "Stack Exchange how-to sites: a reading guide", the toolkit's own
list (facts and links, CC0): one page per subject (home and garden, food and drink, outdoors and travel, vehicles,
making and electronics, pets and family, money, law and work, health and fitness, computers and phones, language,
music and hobbies), each site with what it is for, its Kiwix book name, the size of Kiwix's October 2026 file, and the
folder to fetch it from; a page on how to get them; and a page on their licence and terms. No Stack Exchange text is
copied into it.

Licence of the Kiwix files: each ZIM holds the site's questions and answers as Stack Exchange publishes them, under
Creative Commons Attribution-ShareAlike (CC BY-SA 2.5, 3.0 or 4.0 by the date each post was written; Stack Exchange's
terms of service, updated 13 November 2025, license every post to it under CC BY-SA 4.0 and its "Creative Commons Data
Dump" under CC BY-SA), with each post's author named. Kiwix (openZIM) adds nothing to the licence; its files are free
to download and share.

Not built (NOT_INCLUDED): an Accessibility Stack Exchange (none exists: the proposal never became a site; accessibility
questions are on User Experience, ux.stackexchange.com, listed here), Health Stack Exchange (closed; its successor
Medical Sciences is listed), Stack Overflow itself (107 GB: a programming site, not a how-to one) and the Stack
Exchange data dump (it is the same content as Kiwix's files, and its terms limit reuse to personal, non-commercial
use outside the dump's own licence).

Run from the repository's folder:
  python3 textbooks/stack_exchange.py se:index --out build/textbooks
  python3 textbooks/stack_exchange.py --list stack-exchange
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "stackexchange"
GROUPS = {GROUP: "Reference, Stack Exchange (reading only)"}

# The notice the owner asked for, on every entry, book and Kiwix label of this module.
REFERENCE_ONLY_NOTICE = ("For reading and looking things up only; not for AI training (Stack Exchange's terms).")
SE_LICENCE = "CC BY-SA (2.5, 3.0 or 4.0 by the date of each post), each post's author named"
KIWIX_FOLDER = "https://download.kiwix.org/zim/stack_exchange/"
KIWIX_DATE = "2026-10"                   # the month of the Kiwix files whose sizes are given below
ADVICE_NOTE = ("Answers are written by volunteers and may be wrong or out of date. For health, law, money, electrical, "
               "gas and car safety questions, check with a qualified professional or an official source before you "
               "act.")

# The sites, by subject: (Kiwix book name, plain name, what it is for, size of Kiwix's file in KIWIX_DATE).
SUBJECTS = [
    ("Home and garden", [
        ("diy.stackexchange.com_en_all", "Home Improvement", "home repair, wiring, plumbing, heating and building "
         "questions from contractors and serious do-it-yourselfers", "1.9 GB"),
        ("gardening.stackexchange.com_en_all", "Gardening and Landscaping", "growing plants, lawns, trees, pests and "
         "plant diseases", "890 MB"),
        ("woodworking.stackexchange.com_en_all", "Woodworking", "wood, joints, finishes and woodworking tools",
         "102 MB"),
        ("crafts.stackexchange.com_en_all", "Arts and Crafts", "knitting, sewing, paper, paint and other crafts",
         "56 MB"),
        ("sustainability.stackexchange.com_en_all", "Sustainable Living", "saving energy and water, recycling and "
         "living greener", "26 MB"),
        ("lifehacks.stackexchange.com_en_all", "Lifehacks", "tips and tricks for everyday problems", "47 MB")]),
    ("Food and drink", [
        ("cooking.stackexchange.com_en_all", "Seasoned Advice (cooking)", "cooking methods, ingredients, food safety "
         "and kitchen equipment", "227 MB"),
        ("coffee.stackexchange.com_en_all", "Coffee", "brewing and choosing coffee", "17 MB"),
        ("homebrew.stackexchange.com_en_all", "Homebrewing", "making beer, wine and cider at home", "36 MB"),
        ("alcohol.stackexchange.com_en_all", "Beer, Wine and Spirits", "drinks and their serving", "13 MB"),
        ("vegetarianism.stackexchange.com_en_all", "Veganism and Vegetarianism", "plant-based eating", "9.3 MB")]),
    ("Outdoors and travel", [
        ("outdoors.stackexchange.com_en_all", "The Great Outdoors", "hiking, camping, climbing and outdoor skills",
         "135 MB"),
        ("bicycles.stackexchange.com_en_all", "Bicycles", "riding, fixing and choosing bicycles", "476 MB"),
        ("travel.stackexchange.com_en_all", "Travel", "planning trips, visas, flights and getting around", "441 MB"),
        ("expatriates.stackexchange.com_en_all", "Expatriates", "living and working in another country", "41 MB")]),
    ("Vehicles, making and electronics", [
        ("mechanics.stackexchange.com_en_all", "Motor Vehicle Maintenance and Repair", "car, truck and motorcycle "
         "care and repair", "326 MB"),
        ("3dprinting.stackexchange.com_en_all", "3D Printing", "3D printers, materials and printing problems",
         "115 MB"),
        ("electronics.stackexchange.com_en_all", "Electrical Engineering", "electronics, circuits and repair",
         "4.0 GB"),
        ("ham.stackexchange.com_en_all", "Amateur Radio", "ham radio equipment, licences and operating", "74 MB"),
        ("arduino.stackexchange.com_en_all", "Arduino", "Arduino boards and projects", "248 MB"),
        ("raspberrypi.stackexchange.com_en_all", "Raspberry Pi", "Raspberry Pi computers and projects", "285 MB"),
        ("drones.stackexchange.com_en_all", "Drones and Model Aircraft", "flying and building drones", "12 MB")]),
    ("Pets and family", [
        ("pets.stackexchange.com_en_all", "Pets", "caring for pets and their health and behaviour", "83 MB"),
        ("parenting.stackexchange.com_en_all", "Parenting", "raising children from babies to teenagers", "57 MB"),
        ("interpersonal.stackexchange.com_en_all", "Interpersonal Skills", "getting along with people", "38 MB")]),
    ("Money, law and work", [
        ("money.stackexchange.com_en_all", "Personal Finance and Money", "budgets, banking, taxes, saving and "
         "investing", "242 MB"),
        ("law.stackexchange.com_en_all", "Law", "questions about laws and legal systems (not legal advice)",
         "179 MB"),
        ("workplace.stackexchange.com_en_all", "The Workplace", "jobs, careers and working life", "234 MB"),
        ("freelancing.stackexchange.com_en_all", "Freelancing", "working for yourself", "13 MB"),
        ("patents.stackexchange.com_en_all", "Ask Patents", "patents and finding earlier inventions", "34 MB")]),
    ("Health and fitness", [
        ("medicalsciences.stackexchange.com_en_all", "Medical Sciences", "questions on medicine and health science "
         "(the successor of the closed Health site; not medical advice)", "58 MB"),
        ("fitness.stackexchange.com_en_all", "Physical Fitness", "exercise, training and fitness", "76 MB"),
        ("psychology.stackexchange.com_en_all", "Psychology and Neuroscience", "how the mind and brain work",
         "61 MB")]),
    ("Computers and phones", [
        ("superuser.com_en_all", "Super User", "Windows, Mac and Linux computers, programs and hardware for power "
         "users", "3.7 GB"),
        ("askubuntu.com_en_all", "Ask Ubuntu", "the Ubuntu Linux system", "2.6 GB"),
        ("apple.stackexchange.com_en_all", "Ask Different (Apple)", "Mac, iPhone and iPad", "1.1 GB"),
        ("android.stackexchange.com_en_all", "Android Enthusiasts", "Android phones and tablets", "393 MB"),
        ("softwarerecs.stackexchange.com_en_all", "Software Recommendations", "finding a program for a job",
         "212 MB"),
        ("hardwarerecs.stackexchange.com_en_all", "Hardware Recommendations", "choosing computer hardware", "40 MB"),
        ("webapps.stackexchange.com_en_all", "Web Applications", "web services such as email and office sites",
         "276 MB"),
        ("unix.stackexchange.com_en_all", "Unix and Linux", "Linux and other Unix systems", "1.2 GB"),
        ("security.stackexchange.com_en_all", "Information Security", "keeping computers and accounts safe",
         "419 MB"),
        ("tor.stackexchange.com_en_all", "Tor", "the Tor private browsing network", "30 MB"),
        ("ux.stackexchange.com_en_all", "User Experience", "designing usable programs and sites, with many "
         "accessibility questions (there is no separate accessibility site)", "521 MB"),
        ("ebooks.stackexchange.com_en_all", "Ebooks", "ebook readers and formats", "14 MB")]),
    ("Language, music and hobbies", [
        ("ell.stackexchange.com_en_all", "English Language Learners", "learning English", "453 MB"),
        ("english.stackexchange.com_en_all", "English Language and Usage", "English words, grammar and usage",
         "738 MB"),
        ("languagelearning.stackexchange.com_en_all", "Language Learning", "learning any language", "12 MB"),
        ("music.stackexchange.com_en_all", "Music: Practice and Theory", "playing instruments, reading music and "
         "music theory", "329 MB"),
        ("sound.stackexchange.com_en_all", "Sound Design", "recording and editing sound", "73 MB"),
        ("photo.stackexchange.com_en_all", "Photography", "cameras and taking pictures", "430 MB"),
        ("genealogy.stackexchange.com_en_all", "Genealogy and Family History", "tracing family history", "61 MB"),
        ("boardgames.stackexchange.com_en_all", "Board and Card Games", "rules and play of board and card games",
         "103 MB"),
        ("chess.stackexchange.com_en_all", "Chess", "chess rules, openings and play", "78 MB")]),
]

SITES = [dict(kiwix=n, name=t, what=w, size=s, subject=subj, reference_only=True, notice=REFERENCE_ONLY_NOTICE,
              licence=SE_LICENCE) for subj, rows in SUBJECTS for n, t, w, s in rows]

# The Kiwix library's books of this module: {Kiwix book name: label}, merged into textbooks.json "kiwix_labels"
# (build_textbooks.merge), and their names, merged into "kiwix_reference_only".
KIWIX_LABELS = {s["kiwix"]: f"CC BY-SA; reference only. {REFERENCE_ONLY_NOTICE}" for s in SITES}
KIWIX_REFERENCE_ONLY = sorted(KIWIX_LABELS)

# Every Stack Exchange host, for the self-tests' search of the packs and the kit (a site of the network is
# <name>.stackexchange.com, or one of these own domains).
SE_HOSTS = ("stackexchange.com", "stackoverflow.com", "superuser.com", "serverfault.com", "askubuntu.com",
            "mathoverflow.net", "stackapps.com")


def site_rows(rows):
    """The index page's list of sites (HTML)."""
    import build_textbooks as B
    items = []
    for s in rows:
        items.append(f"<li><strong>{B.esc(s['name'])}</strong>: {B.esc(s['what'])}. Kiwix book: "
                     f"{B.esc(s['kiwix'])} (about {B.esc(s['size'])} in {KIWIX_DATE}). Fetch it from "
                     f'<a href="{KIWIX_FOLDER}">{KIWIX_FOLDER}</a> (the newest file whose name starts with '
                     f"{B.esc(s['kiwix'])}). {B.esc(REFERENCE_ONLY_NOTICE)}</li>")
    return "<ul>" + "".join(items) + "</ul>"


def index_book(name, work, cache=None, left_out=None, limit=None):
    """se:index: the reading guide (see the module docstring). Made offline from SUBJECTS; nothing is downloaded."""
    import build_textbooks as B
    book = K.new_book("se_index", "Stack Exchange how-to sites: a reading guide (reference only)",
                      "Questions and answers (reference only)", GROUP,
                      "Digital Accessibility Toolkit (an index of the Kiwix library)", X.CC0_INDEX, K.CC0_URL,
                      X.TOOLKIT_REPO, "A guide to Stack Exchange's practical question-and-answer sites in the Kiwix "
                      "library, by subject: what each is for, its Kiwix book and how big it is. "
                      + REFERENCE_ONLY_NOTICE,
                      f"{REFERENCE_ONLY_NOTICE} Facts and links only (CC0); the sites' questions and answers are "
                      f"CC BY-SA, by their authors, in Kiwix's own files. {ADVICE_NOTE}",
                      country="International", changes="an index written for the toolkit")
    head = f"<p><strong>{B.esc(REFERENCE_ONLY_NOTICE)}</strong></p>"
    for number, (subject, rows) in enumerate(SUBJECTS, 1):
        sites = [s for s in SITES if s["subject"] == subject]
        book.pages.append(B.Page(f"part-{number}-{B.slug(subject, 40)}", subject, head + site_rows(sites), number,
                                 "Sites by subject"))
    book.pages.append(B.Page("how-to-get-them", "How to get these books", head + (
        "<p>These are the Kiwix project's own files; the toolkit lists them from the Kiwix catalogue, so pick them "
        "there like any other Kiwix book. With Program Downloader, open the Kiwix folder "
        f'<a href="{KIWIX_FOLDER}">{KIWIX_FOLDER}</a> and fetch the newest file of the site you want (its name ends '
        "with the year and month, such as _2026-10.zim). Kiwix makes a new file every few months. Big sites (Home "
        "Improvement, Super User, Ask Ubuntu, Electrical Engineering) are several gigabytes: check your free space "
        "first.</p>"), 0, "More"))
    book.pages.append(B.Page("licence-and-terms", "Licence and terms", head + (
        "<p>The questions and answers are under Creative Commons Attribution-ShareAlike (CC BY-SA 2.5, 3.0 or 4.0, by "
        "the date of each post), each with its author named. Stack Exchange's robots.txt turns programs away and says "
        "ai-train=no, and Stack Exchange restricts using its content to train AI. So these books are for reading and "
        "looking things up only: the toolkit never uses them to train a model, and nothing in this library copies "
        f"them.</p><p>{B.esc(ADVICE_NOTE)}</p>"), 0, "More"))
    book.pages.append(B.Page("not-included", "Not included, and why", "<ul>" + "".join(
        f"<li>{B.esc(t)}: {B.esc(r)}</li>" for t, r in NOT_INCLUDED) + "</ul>", 0, "More"))
    if limit:
        book.pages = book.pages[:limit]
    book.published = ""
    return book


def index_sign(name):
    """The weekly sign of the index: a fingerprint of its list."""
    return K.sha(SUBJECTS, NOT_INCLUDED, REFERENCE_ONLY_NOTICE)


class ReferenceOnlyCollection(K.Collection):
    """A Collection whose every book is marked reference only: the catalogue entry gets "reference_only": true and
    the notice, so the toolkit never offers it for training."""

    def build(self, keys, out_dir, cache=None, date=None, limit=None):
        """Build as usual, then mark every written entry and rewrite its manifest."""
        manifests = super().build(keys, out_dir, cache, date, limit)
        for key, manifest in manifests.items():
            for entry in manifest["books"]:
                entry["reference_only"] = True
                entry["reference_only_notice"] = REFERENCE_ONLY_NOTICE
            safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if limit else "")
            with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=1, ensure_ascii=False)
        return manifests


MAKERS = {"index": (index_book, index_sign)}
COLLECTION = ReferenceOnlyCollection("se", GROUP, makers=MAKERS, words={"stack-exchange": lambda: ["se:index"]})

LICENCE_LINES = {
    "se_kiwix": "Kiwix's Stack Exchange ZIM files (download.kiwix.org/zim/stack_exchange/, listed 2026-11-22): the "
                "sites' questions and answers under CC BY-SA (2.5, 3.0 or 4.0 by post date) with each author named; "
                "Stack Exchange's terms of service (updated 13 November 2025): posts are licensed under CC BY-SA 4.0 "
                "and the Creative Commons Data Dump under CC BY-SA. stackexchange.com/robots.txt: \"Content-signal: "
                "search=no, ai-train=no\" and \"Disallow: /\" for every program, so no Stack Exchange site is read "
                "and these books are marked reference only (never used for training). The Kiwix files are not "
                "rebuilt; only labelled (kiwix_labels, kiwix_reference_only).",
    "se_index": "The reading guide (se:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Accessibility Stack Exchange", "No such site exists (the proposal never became a site); accessibility questions "
     "are on User Experience (ux.stackexchange.com_en_all, listed as reference only). Index: "
     "https://download.kiwix.org/zim/stack_exchange/"),
    ("Health Stack Exchange", "Closed by Stack Exchange; its successor Medical Sciences (medicalsciences."
     "stackexchange.com_en_all) is listed. Index: https://download.kiwix.org/zim/stack_exchange/"),
    ("Stack Overflow (stackoverflow.com_en_all, 107 GB)", "A programming site, not a practical how-to one, and far "
     "too big for this library; it stays in the Kiwix catalogue for anyone who wants it (reference only). Index: "
     "https://download.kiwix.org/zim/stack_exchange/"),
    ("The Stack Exchange data dump and the Stack Exchange websites themselves", "The websites' robots.txt says "
     "\"ai-train=no\" and \"Disallow: /\" to every program, so they are never read; the data dump holds the same "
     "posts as Kiwix's files. Nothing is rebuilt: the Kiwix files are only labelled reference only. Index: "
     "https://stackexchange.com/sites"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
