"""The collection "Computer and phone basics: getting-started guides (manuals)" (category key computer_basics): the
owner's request of 2026-11-22 for computer and phone basics for beginners. practical_manuals.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each guide belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (quick start and getting
            started guides, iPad, iPhone, Android, Kindle and Fire tablets, Chromebooks, Echo speakers, printers'
            setup guides). The plain words computer, laptop, keyboard, router, modem, tablet and smartphone are already
            searched by the computers and personal_electronics collections, so they are not repeated here;
  makers    the big makers' own help and user guide libraries (Apple, Google, Microsoft, Samsung, Amazon, Dell, HP,
            Lenovo): by the owner's rule LINK-ONLY, for the person (or the personal assistant) to open in a browser
            or fetch with Program Downloader; nothing is read from their sites;
  guidance  the free beginner courses (GCFGlobal, DigitalLearn, Northstar; copyright, links) and the guides the
            reference library builds in full (the LibreOffice guides, the Library of Congress's personal digital
            archiving pages, Microsoft's support articles).

The notice is said first (NOTICE): restart first, updates, backups, downloads only from the maker or the official
store, and never give a password or code to a caller.
"""

NOTICE = ("When something stops working, restart it first. Keep the system and apps updated, back up your files, "
          "download programs and apps only from the maker's own site or the official app store, and never give a "
          "password or sign-in code to someone who calls, texts or emails you.")

IA_WORDS = ["quick start guide", "getting started guide", "quick setup guide", "ipad", "iphone", "android",
            "kindle", "kindle fire", "fire tablet", "chromebook guide", "echo dot", "printer setup"]

RULE = ("by the owner's rule the maker's own guides are link-only: nothing is read from its site; its help page is "
        "listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="computer_basics", prefix="pcb", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="apple", maker="Apple", type="iPhone, iPad, Mac and Apple Watch user guide",
         library="https://support.apple.com/guide/", site="support.apple.com"),
    dict(key="google", maker="Google", type="Android, Pixel, Chromebook and Google Nest help",
         library="https://support.google.com/", site="support.google.com"),
    dict(key="microsoft", maker="Microsoft", type="Windows, Office and Surface help",
         library="https://support.microsoft.com/", site="support.microsoft.com"),
    dict(key="samsung", maker="Samsung", type="Galaxy phone and tablet user manual",
         library="https://www.samsung.com/us/support/", site="samsung.com"),
    dict(key="amazon", maker="Amazon", type="Kindle, Fire tablet and Echo help",
         library="https://www.amazon.com/gp/help/customer/display.html", site="amazon.com"),
    dict(key="dell", maker="Dell", type="laptop and desktop manual", library="https://www.dell.com/support/",
         site="dell.com"),
    dict(key="hp", maker="HP", type="laptop, desktop and printer manual", library="https://support.hp.com/",
         site="support.hp.com"),
    dict(key="lenovo", maker="Lenovo", type="laptop, desktop and tablet manual", library="https://support.lenovo.com/",
         site="support.lenovo.com"),
]]

GUIDANCE = [
    dict(title="LibreOffice Getting Started, Writer and Calc guides (CC BY 4.0; built in full in the reference "
               "library: pcb:libreoffice_getting_started and the others)", url="https://books.libreoffice.org/en/",
         by="the LibreOffice Documentation Team"),
    dict(title="Personal Digital Archiving: keeping photos, email and records safe (in the reference library: "
               "pcb:loc_personal_digital_archiving)", url="https://www.digitalpreservation.gov/personalarchiving/",
         by="the Library of Congress"),
    dict(title="GCFGlobal computer, internet and smartphone lessons (copyright; open them in a browser)",
         url="https://edu.gcfglobal.org/en/topics/tech/", by="the Goodwill Community Foundation"),
    dict(title="DigitalLearn.org beginner courses (copyright; open them in a browser)",
    url="https://www.digitallearn.org/",
         by="the Public Library Association"),
    dict(title="Northstar Digital Literacy (copyright; open it in a browser)",
         url="https://www.digitalliteracyassessment.org/", by="Literacy Minnesota"),
]

CATEGORY = dict(
    name="Computer and phone basics: getting-started guides (manuals)",
    description="Quick start and getting started guides for computers, phones, tablets, e-readers, smart speakers and "
                "printers: the Internet Archive's guides, the big makers' help libraries (links) and the free beginner "
                "courses. Links only.",
    kind="manuals", licence="CC0 (facts and links); each guide belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
