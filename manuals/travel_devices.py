"""The collection "Translators, travel adapters and luggage (manuals)" (category key travel_devices): the owner's
request of 2026-11-22 for travel and language learning. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia         the Internet Archive's manual collections, searched by the words in IA_WORDS (electronic translators and
             dictionaries, voltage converters, travel adapters, luggage scales, suitcases and luggage locks);
  makers     the makers of translators, travel electronics and luggage: by the owner's rule their own manuals are
             LINK-ONLY, for the person (or the personal assistant) to open in a browser or fetch with Program
             Downloader; nothing is read from their sites;
  documents  the FAA's PackSafe pages (a US government work, given in FULL: what batteries, power banks and medical
             devices may fly, and how), TSA's What Can I Bring and TSA Cares (links: tsa.gov refuses programs), and the
             reference library's travel and language books (textbooks/travel.py and languages.py).

The notice is said first (NOTICE): spare lithium batteries and power banks in carry-on bags only.
"""

NOTICE = ("Spare lithium batteries and power banks go in carry-on bags only, never in checked bags; keep devices "
          "switched off or protected from being turned on. Check that a converter or adapter suits the device's "
          "voltage before you plug it in abroad. TSA Cares (855-787-2227) helps travellers with disabilities.")

IA_WORDS = ["electronic translator", "language translator", "electronic dictionary", "voltage converter",
            "travel adapter", "luggage scale", "suitcase", "luggage lock"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="travel_devices", prefix="td", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="pocketalk", maker="Pocketalk", type="voice translator", library="https://www.pocketalk.com/support",
         site="pocketalk.com"),
    dict(key="vasco", maker="Vasco Electronics", type="voice translator", library="https://vasco-electronics.com/",
         site="vasco-electronics.com"),
    dict(key="franklin", maker="Franklin Electronic Publishers", type="electronic dictionary and translator",
         library="https://www.franklin.com/", site="franklin.com"),
    dict(key="samsonite", maker="Samsonite", type="suitcase and luggage", library="https://shop.samsonite.com/",
         site="samsonite.com"),
    dict(key="travelpro", maker="Travelpro", type="suitcase and luggage", library="https://www.travelpro.com/",
         site="travelpro.com"),
    dict(key="ceptics", maker="Ceptics", type="travel adapter and voltage converter", library="https://ceptics.com/",
         site="ceptics.com"),
    dict(key="travel-sentry", maker="Travel Sentry", type="TSA-accepted luggage lock",
         library="https://www.travelsentry.org/", site="travelsentry.org"),
]]

DOCUMENTS = [
    dict(key="faa-packsafe", by="Federal Aviation Administration", product="batteries, power banks and medical devices",
         title="PackSafe: what you can pack in carry-on and checked bags (FAA; in the reference library: "
               "trip:faa_packsafe)", url="https://www.faa.gov/hazmat/packsafe", type="travel electronics",
         document="guide", access="full", rights="a US government work (public domain)",
         reason="a US government work; robots.txt allows this builder"),
    dict(key="tsa-what-can-i-bring", by="Transportation Security Administration", product="carry-on and checked bags",
         title="What Can I Bring? (TSA)", url="https://www.tsa.gov/travel/security-screening/whatcanibring/all",
         type="luggage", document="guide", access="link", rights="a US government work (public domain)",
         reason="tsa.gov answers programs \"403\" (checked 2026-11-22); open it in a browser"),
    dict(key="tsa-cares", by="Transportation Security Administration", product="travellers with disabilities",
         title="TSA Cares: help for travellers with disabilities and medical conditions (TSA)",
         url="https://www.tsa.gov/travel/tsa-cares", type="luggage", document="guide", access="link",
         rights="a US government work (public domain)",
         reason="tsa.gov answers programs \"403\" (checked 2026-11-22); open it in a browser"),
]

GUIDANCE = [
    dict(title="Passports, travel documents and REAL ID (USA.gov; in the reference library: trip:usa_gov_travel)",
         url="https://www.usa.gov/travel", by="USAGov"),
    dict(title="Phrasebooks and language courses (in the reference library: languages)",
         url="https://en.wikivoyage.org/wiki/Wikivoyage:Phrasebooks", by="Wikivoyage contributors and the FSI"),
]

CATEGORY = dict(
    name="Translators, travel adapters and luggage (manuals)",
    description="Electronic and voice translators, electronic dictionaries, voltage converters and travel adapters, "
                "luggage scales, suitcases and luggage locks: the Internet Archive's manuals, the makers' manual "
                "pages (links), the FAA's PackSafe rules for batteries and medical devices, and TSA's pages (links).",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, documents=DOCUMENTS, guidance=GUIDANCE, notice=NOTICE)
