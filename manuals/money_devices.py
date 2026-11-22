"""The collection "Currency readers, money counters and cash registers (manuals)" (category key money_devices): the
owner's request of 2026-11-22 for money, work and business. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia         the Internet Archive's manual collections, searched by the words in IA_WORDS (currency and bill readers,
             money and coin counters, counterfeit detectors, cash registers and receipt printers, check writers and
             adding machines). "calculator" and "label maker" are already searched by office_supplies;
  makers     the makers of currency readers, money counters and cash registers: by the owner's rule their own manuals
             are LINK-ONLY, for the person (or the personal assistant) to open in a browser or fetch with Program
             Downloader; nothing is read from their sites;
  documents  the Bureau of Engraving and Printing's free U.S. Currency Reader Program for blind and visually impaired
             people and the currency education pages (links: their terms were not checked one by one), and the
             reference library's money books (built in full: textbooks/money_work.py and money_help.py).

The notice is said first (NOTICE): how a currency reader is checked, and where the free one comes from.
"""

NOTICE = ("Blind and visually impaired people in the US can get a free currency reader from the Bureau of Engraving and "
          "Printing's U.S. Currency Reader Program. Check a new reader against notes you know, keep it charged or its "
          "batteries fresh, and update it when the maker releases new notes.")

IA_WORDS = ["currency reader", "bill reader", "money reader", "money counter", "coin counter", "coin sorter",
            "counterfeit detector", "cash register", "receipt printer", "check writer", "adding machine"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="money_devices", prefix="md", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="orbit-research", maker="Orbit Research (iBill)", type="talking currency reader",
         library="https://www.orbitresearch.com/", site="orbitresearch.com"),
    dict(key="cassida", maker="Cassida", type="money counter and counterfeit detector",
         library="https://www.cassidausa.com/", site="cassidausa.com"),
    dict(key="royal", maker="Royal Consumer Business Products", type="cash register and money counter",
         library="https://royal.com/", site="royal.com"),
    dict(key="sharp-registers", maker="Sharp (cash registers)", type="cash register",
         library="https://business.sharpusa.com/", site="business.sharpusa.com"),
    dict(key="casio-registers", maker="Casio (cash registers)", type="cash register",
         library="https://support.casio.com/", site="support.casio.com"),
    dict(key="accubanker", maker="AccuBANKER", type="money counter and counterfeit detector",
         library="https://www.accubanker.com/", site="accubanker.com"),
]]

DOCUMENTS = [
    dict(key="bep-currency-reader", by="Bureau of Engraving and Printing (US Department of the Treasury)",
         product="currency reader", title="U.S. Currency Reader Program: a free currency reader for blind and visually "
         "impaired people (BEP)", url="https://www.bep.gov/", type="talking currency reader", document="guide",
         access="link", rights="a US government work (public domain)",
         reason="its program page moved (the old address answered 404 on 2026-11-22); open bep.gov and choose the "
                "currency reader program"),
    dict(key="uscurrency-denominations", by="U.S. Currency Education Program (Federal Reserve Board)",
         product="US banknotes", title="US banknotes and their security features, note by note (uscurrency.gov)",
         url="https://www.uscurrency.gov/denominations", type="banknote", document="guide", access="link",
         rights="the Federal Reserve Board's terms (not checked one by one)",
         reason="its terms were not checked one by one; the page is listed for the person to open"),
]

GUIDANCE = [
    dict(title="Money, banking, credit and debt (CFPB, FDIC; built in full in the reference library: money)",
         url="https://www.consumerfinance.gov/consumer-tools/", by="the Consumer Financial Protection Bureau"),
    dict(title="IRS publications, pay and benefits at work, O*NET (built in full in the reference library: "
               "money-work)", url="https://www.irs.gov/forms-instructions", by="the Internal Revenue Service"),
]

CATEGORY = dict(
    name="Currency readers, money counters and cash registers (manuals)",
    description="Talking currency readers, bill and coin counters, counterfeit detectors, cash registers, receipt "
                "printers, check writers and adding machines: the Internet Archive's manuals, the makers' manual "
                "pages (links) and the Bureau of Engraving and Printing's free currency reader program. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, documents=DOCUMENTS, guidance=GUIDANCE, notice=NOTICE)
