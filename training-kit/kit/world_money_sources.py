"""FOREIGN BANKNOTES AND COINS for the Picture Model Training Kit (the owner's request of 2026-11-22). This file
lists:
  - the ready-made packs built in packs/world_money_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_world_money (old coins and banknotes of 21 countries and of the Smithsonian's National
    Numismatic Collection), met_world_coins and open_images_money;
  - the sources looked at and left out, with the reason (WORLD_MONEY_NOT_INCLUDED): above all the CURRENT money of
    each country, because central banks restrict pictures of their money in ways a shared training collection
    cannot be sure to meet.

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer, only when the user ticks the matching choice. Every licence and reproduction rule was
checked at its source in November 2026.

Answers name the country, denomination and side only as the source says (the Commons category, the subcategory, the
file's own title, the museum's record). How current notes are told apart by touch (raised lines, bumps, dots, sizes)
is in the reference library's world-money book, from the central banks' own pages (the Reserve Bank of Australia
under CC BY 4.0, the European Central Bank and the Bank of Canada under their attribution terms). US money is in
commons_us_money and commons_money_sides, Canadian money in commons_ca_money and commons_money_sides.

Picture-making: never (sources.py puts every key in NOT_FOR_PICTURE_MAKING): a model that makes pictures of money is
not wanted. Topics: "documents" (Documents, maps and signs), as the US bills and synthetic bills are; the
accessible-money facts are in the vision topic's books, not here.

    python -c "import sources, world_money_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = ("Pictures CC0, public domain or CC BY (credited in CREDITS.txt), money dated 1930 or earlier only; "
                "captions CC0")
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
MET_OPEN = "CC0 (The Metropolitan Museum of Art Open Access, each object's isPublicDomain checked)"
MET_CREDIT = "The Metropolitan Museum of Art, https://www.metmuseum.org (each object credited in CREDITS.txt)"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt); pictures made small")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")

WORLD_MONEY_SOURCES = [
    Source("commons_world_money", "Old coins and banknotes (1930 or earlier) of Japan, Mexico, the UK, China, "
                                  "India, Australia, Switzerland, Korea, Brazil, the Nordic countries, Poland, "
                                  "Turkey, the Philippines, Thailand, Russia, Germany, France, Italy and Spain, by "
                                  "country, value and side (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 250 MB"),
    Source("met_world_coins", "Coins at the Met: Greek, Roman, Islamic and later coins, answered from the museum's "
                              "records (ready-made pack)",
           MET_OPEN, MET_CREDIT, "permissive", 800, 10, prepare_pack, "about 150 MB"),
    Source("open_images_money", "Money, cash and currency, dollars, nickels, dimes, Japanese yen, coin purses and "
                                "piggy banks, pictures made small (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 120 MB"),
]

# No key of this file is for picture-making (see the module docstring).
WORLD_MONEY_PICTURE_MAKING_OK = set()

WORLD_MONEY_NOT_INCLUDED = {
    "Current Australian banknotes": "the Reserve Bank of Australia consents to electronic images only below "
        "three-quarters size, at 72 dpi or less, with every copy destroyed after use (banknotes.rba.gov.au/legal/"
        "reproducing-banknotes, read 22 November 2026); a kept training collection cannot meet that. Left out; "
        "the RBA's accessibility pages (CC BY 4.0) are in the world-money book.",
    "Current euro banknotes and coins": "the European Central Bank's reproduction rules (Decision ECB/2013/10) "
        "set sizes and resolutions for pictures of euro notes, and the coins' national sides belong to each "
        "country; unclear for a training collection, so left out. The ECB's page for blind and partially "
        "sighted people is in the world-money book.",
    "Current UK, Canadian, Japanese, Mexican, Chinese and Indian money": "the Bank of Canada asks for written "
        "permission to reproduce its notes (bankofcanada.ca terms, section 2.1, read 22 November 2026); the Bank "
        "of England, the Bank of Japan, the Banco de Mexico, the People's Bank of China and the Reserve Bank of "
        "India have their own reproduction rules, not checked for this use, and modern UK coins are Crown "
        "copyright. Left out: only money dated 1930 or earlier is taken.",
    "Current money of the other countries": "not checked country by country; left out by the same rule (money "
        "dated 1930 or earlier only), as the owner asked where the rules are unclear.",
    "American Numismatic Society (MANTIS, numismatics.org)": "its pictures of objects made in 1925 or earlier carry "
        "the Public Domain Mark and later ones are non-commercial, but its robots.txt shuts out AI crawlers "
        "(ClaudeBot, GPTBot and others; checked 22 November 2026), so nothing is read from it; link-only: "
        "https://numismatics.org/search/",
    "Smithsonian National Numismatic Collection through its API": "api.si.edu refused automated requests and only "
        "2 of 5,434 of its open-access records carry a picture (everyday_extras_packs notes); its CC0 photos on "
        "Commons are used instead (the \"National Numismatic Collection\" category, old money only).",
    "Reserve Bank of New Zealand pages": "its robots.txt says ai-train=no and shuts out AI crawlers; not read.",
    "Bank of England, Bank of Japan, Banco de Mexico, Reserve Bank of India and People's Bank of China pages on "
    "telling notes apart": "the Bank of England's terms allow personal, non-commercial use only; the others' terms "
        "were not found open; links only, in the world-money book's list.",
    "Already in the kit": "US coins and bills (commons_us_money, commons_money_sides), Canadian money "
        "(commons_ca_money), Indian and Thai banknotes (banknotes, CC BY), Bangladeshi taka (bd_taka), Ghanaian "
        "money (ghana_money) and the made-up bills (synthetic_bills): not repeated; the Open Images labels "
        "Banknote, Coin and Wallet are asked by other packs.",
}
