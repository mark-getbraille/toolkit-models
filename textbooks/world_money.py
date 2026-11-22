"""Telling foreign banknotes and coins apart without sight, for the reference library, in the group "Reference,
blind and low-vision living" (the owner's request of 2026-11-22). Keys: world-money (every book), wmoney:<name>.

What this module builds, in plain words:
  - wmoney:index, a guide to the library for money when travelling (the toolkit's own facts and links, CC0): each
    central bank's features for blind and partially sighted people (raised marks, sizes, large numbers and colours),
    US money, currency readers and apps, and old money, with the books by key, the picture packs, the manual
    collection, and the central banks whose pages are links only;
  - IN FULL, the central banks' own pages where their terms allow it, each kept whole with its text unchanged
    (pictures of banknotes are left out: every bank restricts them):
      wmoney:rba_banknote_accessibility   the Reserve Bank of Australia's pages for people with vision impairment
                                          (the raised bumps on each note's long edges, the lengths from 130 to 158
                                          mm, large numbers and colours, and the Banknote Measure device),
                                          under CC BY 4.0;
      wmoney:ecb_visually_impaired        the European Central Bank's page for visually impaired people (euro note
                                          sizes, colours, large numerals, raised print and the raised lines with
                                          their breaks, and the coins' sizes and edges), under the ECB's copyright
                                          notice (free use with the source cited);
      wmoney:boc_blind_partially_sighted  the Bank of Canada's page for blind and partially sighted people (the
                                          six-dot tactile symbols, the large high-contrast numbers and the vertical
                                          notes), under the Bank of Canada's terms of use (free use with
                                          attribution; bank note images excepted).
  Every book carries MONEY_NOTE in its notice.

Already in the library and not repeated: the Bureau of Engraving and Printing's US currency accessibility pages and the
free US Currency Reader Program (vision:bep_currency_access), and the money books (money, money-work).

Not built (NOT_INCLUDED, link-only): the Reserve Bank of New Zealand (its robots.txt says ai-train=no), the Bank of
England (personal, non-commercial use only), the Bank of Japan, the Banco de Mexico, the Reserve Bank of India and the
People's Bank of China (their terms were not checked for this use), and the US Currency Education Program (its terms were not
checked one by one).

Run from the repository's folder:
  python3 textbooks/world_money.py wmoney:ecb_visually_impaired --out build/textbooks --limit 3
  python3 textbooks/world_money.py --list world-money
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "vision"                       # "Reference, blind and low-vision living" (vision_living.py)
GROUPS = {}

MONEY_NOTE = ("These are each central bank's own descriptions of its current notes and coins; designs change, and "
              "older series may lack the features. A currency reader or a money identifier app can help; in the US, "
              "blind and visually impaired people can get a free currency reader from the Bureau of Engraving and "
              "Printing.")
UNCHANGED_NOTE = "Kept whole with its text unchanged; pictures of banknotes are left out."

RBA_LICENCE = "CC BY 4.0"
RBA_LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
RBA_TERMS = "https://www.rba.gov.au/copyright/"
RBA_TEXT = r"provided under a Creative Commons Attribution 4\.0 International License"
ECB_LICENCE = "ECB copyright notice"
ECB_TERMS = "https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html"
ECB_TEXT = r"users of this website may make free use of the information obtained directly from it"
BOC_LICENCE = "Bank of Canada terms of use"
BOC_TERMS = "https://www.bankofcanada.ca/terms/"
BOC_TEXT = r"the Bank permits you to freely use, copy, distribute and transmit its website content"
# The two banks' own terms: free use with the source credited (and changes stated), so "open"; the books are still
# kept whole and unchanged, as the ECB asks that the information "appear accurately".
ALLOWED = {ECB_LICENCE: "open", BOC_LICENCE: "open"}

RBA = "https://banknotes.rba.gov.au/resources/for-people-with-vision-impairment/"
RBA_PAGES = [RBA + "accessibility-features/", RBA + "banknotes-measure-device/"]
ECB_PAGES = ["https://www.ecb.europa.eu/euro/visually/html/index.en.html"]
BOC_PAGES = ["https://www.bankofcanada.ca/banknotes/audience-specific-resources/blind-and-partially-sighted/"]


def bank_book(name, title, subject, publisher, urls, pages, description, notice, country, licence, licence_url,
              terms, text, content=K.MAIN):
    """A central bank's fixed list of pages, each read whole and kept unchanged, under the bank's own licence (its
    terms page and line checked at every build)."""
    entry = X.page_list_book(GROUP, name, title, subject, publisher, urls, pages, description,
                             f"{notice} {UNCHANGED_NOTE} {MONEY_NOTE}", units=[(r".", subject)], content=content)
    return dict(entry, country=country, licence=licence, licence_url=licence_url, licence_page=terms,
                licence_text=text, unchanged=True)


GUIDES = [
    bank_book("rba_banknote_accessibility", "Australian banknotes for people with vision impairment (Reserve Bank of "
              "Australia)", "Australian banknotes by touch", "Reserve Bank of Australia", RBA_PAGES,
              r"^https://banknotes\.rba\.gov\.au/resources/for-people-with-vision-impairment/[a-z-]+/$",
              "The Reserve Bank of Australia's pages for people who are blind or have low vision: the raised bumps on "
              "the long edges of the new series of notes (one on the $5, two on the $10, three on the $20, four on "
              "the $50 and five on the $100), the different lengths of each note, the large bold numbers and colour "
              "contrasts, and the credit-card sized Banknote Measure device, which uses the notes' lengths.",
              "Source: Reserve Bank of Australia (banknotes.rba.gov.au), licensed under CC BY 4.0 "
              "(https://creativecommons.org/licenses/by/4.0/).", "Australia", RBA_LICENCE, RBA_LICENCE_URL,
              RBA_TERMS, RBA_TEXT, content=(r'<div role="main" id="content"[^>]*>', r'<footer\b')),
    bank_book("ecb_visually_impaired", "Euro banknotes and coins for visually impaired people (European Central "
              "Bank)", "Euro notes and coins by touch", "European Central Bank", ECB_PAGES,
              r"^https://www\.ecb\.europa\.eu/euro/visually/html/index\.en\.html$",
              "The European Central Bank's page for blind and partially sighted people: the euro notes' sizes (the "
              "higher the value, the larger the note), their colours, the large numerals, the raised print, the "
              "raised lines on the left and right edges of the front (no breaks on the 5 and 50 euro notes, one "
              "break on the 10 and 100, two breaks on the 20 and 200), and the coins' sizes, shapes, colours and "
              "edges.",
              "Source: European Central Bank (www.ecb.europa.eu), used under its copyright notice: free use with the "
              "ECB cited as the source; this information may be obtained free of charge from the ECB's website.",
              "European Union", ECB_LICENCE, ECB_TERMS, ECB_TERMS, ECB_TEXT),
    bank_book("boc_blind_partially_sighted", "Canadian bank notes for blind and partially sighted people (Bank of "
              "Canada)", "Canadian bank notes by touch", "Bank of Canada", BOC_PAGES,
              r"^https://www\.bankofcanada\.ca/banknotes/audience-specific-resources/blind-and-partially-sighted/$",
              "The Bank of Canada's page for blind and partially sighted people: the tactile feature of six-dot "
              "symbols (not braille; one on the $5, two on the $10, three on the $20, four on the $50, two with a "
              "wider space on the $100), the large high-contrast numbers on both sides, and the vertical $10 and $20 "
              "notes.",
              "Source: Bank of Canada (www.bankofcanada.ca), used under its terms of use (attribution; not endorsed "
              "by the Bank); this content is available free of charge on the Bank's website.", "Canada", BOC_LICENCE,
              BOC_TERMS, BOC_TERMS, BOC_TEXT),
]

# ====================================================================== the index

SECTIONS = [
    ("Australia, the euro and Canada: features you can feel", "Raised marks, sizes and large numbers.", [
        ("key", "wmoney:rba_banknote_accessibility", "Australian banknotes: raised bumps and lengths (RBA)"),
        ("key", "wmoney:ecb_visually_impaired", "Euro notes and coins: sizes, raised lines and edges (ECB)"),
        ("key", "wmoney:boc_blind_partially_sighted", "Canadian notes: six-dot tactile symbols and large numbers (Bank "
                                                      "of Canada)"),
        ("pack", "commons_money_sides", "US and Canadian coins and notes by side, with how to tell them by touch")]),
    ("United States money", "All US bills are one size; the free currency reader.", [
        ("key", "vision:bep_currency_access", "Telling US bills apart: the US Currency Reader Program (BEP)"),
        ("manuals", "money_devices", "Currency readers, money counters and coin sorters, as links"),
        ("link", "US Currency Education Program: notes and their features", "https://www.uscurrency.gov/denominations",
         "its terms were not checked one by one; open it in a browser")]),
    ("Other countries' central banks", "Their own pages on telling notes apart.", [
        ("link", "Bank of England: banknote features", "https://www.bankofengland.co.uk/banknotes",
         "personal, non-commercial use only by its terms"),
        ("link", "Reserve Bank of New Zealand: banknotes", "https://www.rbnz.govt.nz/money-and-cash",
         "its robots.txt says ai-train=no; open it in a browser"),
        ("link", "Bank of Japan: banknotes and coins", "https://www.boj.or.jp/en/note_tfjgs/index.htm",
         "its terms were not checked for this use"),
        ("link", "Banco de Mexico: banknotes", "https://www.banxico.org.mx/banknotes-and-coins/",
         "its terms were not checked for this use"),
        ("link", "Reserve Bank of India: banknotes and the MANI app", "https://www.rbi.org.in/",
         "its terms were not checked for this use"),
        ("link", "People's Bank of China", "http://www.pbc.gov.cn/en/", "its terms were not checked for this use")]),
    ("Old coins and banknotes", "Money of 1930 or earlier, and museum coins.", [
        ("pack", "commons_world_money", "Old coins and banknotes of 21 countries, by country, value and side"),
        ("pack", "met_world_coins", "Coins at the Met"),
        ("pack", "open_images_money", "Money, cash, coin purses and piggy banks in everyday photos")]),
]
INDEX = X.index_maker("wmoney", GROUP, "Foreign money without sight: a guide to the library",
                      "Foreign banknotes and coins",
                      "A guide to the library for money when travelling: the central banks' features for blind and "
                      "partially sighted people (Australia, the euro, Canada), US money and currency readers, other "
                      "central banks' pages, and old money.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("wmoney", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"world-money": lambda: ["wmoney:index"] + [f"wmoney:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "wmoney_rba": "www.rba.gov.au/copyright (checked at every build; banknotes.rba.gov.au/copyright points to it): "
                  "RBA material other than banknote images, logos and third-party material \"is provided under a "
                  "Creative Commons Attribution 4.0 International License\"; credited in the notice; banknote "
                  "pictures left out. robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "wmoney_ecb": "www.ecb.europa.eu/services/using-our-site/disclaimer (checked at every build): \"users of this "
                  "website may make free use of the information obtained directly from it\", accurately and with the "
                  "ECB cited, and buyers told it is free on the ECB's site; met in the notice, the page kept whole. "
                  "robots.txt allows the page; no AI rules (checked 2026-11-22).",
    "wmoney_boc": "www.bankofcanada.ca/terms (checked at every build): \"the Bank permits you to freely use, copy, "
                  "distribute and transmit its website content\" with attribution, no suggestion of endorsement and "
                  "the free-of-charge notice for paid services; bank note images excepted (left out). robots.txt "
                  "allows the page; no AI rules (checked 2026-11-22).",
    "wmoney_index": "The index (wmoney:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Reserve Bank of New Zealand banknote pages", "Its robots.txt carries \"Content-Signal: ai-train=no\" and shuts "
     "out AI crawlers (checked 2026-11-22), so nothing is read. Link-only. Index: "
     "https://www.rbnz.govt.nz/money-and-cash"),
    ("Bank of England banknote pages", "Its terms allow downloading for "
     "\"personal use or internal use within an individual organisation for non-commercial purposes\" (checked "
     "2026-11-22); not built. Link-only. Index: https://www.bankofengland.co.uk/banknotes"),
    ("Bank of Japan, Banco de Mexico, Reserve Bank of India and People's Bank of China banknote pages", "Their terms "
     "were not checked for this use, so nothing is read from them. Link-only. Index: "
     "https://www.boj.or.jp/en/note_tfjgs/index.htm and https://www.banxico.org.mx/banknotes-and-coins/"),
    ("US Currency Education Program denomination pages (uscurrency.gov)", "A Federal Reserve Board site whose terms "
     "were not checked one by one; the Bureau of Engraving and Printing's own pages are built "
     "(vision:bep_currency_access). Index: https://www.uscurrency.gov/denominations"),
    ("Pictures of current banknotes from the central banks", "Every bank restricts them (the RBA's consent asks that "
     "every copy be destroyed after use; the Bank of Canada asks written permission; the ECB sets sizes and "
     "resolutions): left out of these books and of the picture packs. Index: "
     "https://banknotes.rba.gov.au/legal/reproducing-banknotes/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
