"""Games and hobbies for the reference library, in the group "Reference, games and hobbies" (the owner's requests of
2026-11-22). Keys: games:<name>; request words (each well under 256 jobs):
  card-games     the card game rule books
  board-games    board, tile, dice and traditional games
  games-hobbies  puzzles, music theory, stamps and the openly licensed role-playing rules

What this module builds, in plain words, each IN FULL. Old public-domain books come from the Internet Archive
(published before 1931; the builder checks each item's year at every build):
  - card games: Foster's Complete Hoyle (1916: whist, bridge, poker, cribbage, rummy, pinochle, euchre, hearts, five
    hundred, solitaires, casino games as games, and many more), Fox's Hoyle's Games (1905), Lady Cadogan's
    Illustrated Games of Patience (1887) and Royal Auction Bridge (1914);
  - board games: Arthur Smith's The Game of Go (1908), Capablanca's Chess Fundamentals (1921), Lasker's Common Sense
    in Chess, Freeborough and Ranken's Chess Openings, Babcock's Rules for Mah-Jongg (1923), Lees's Guide to Draughts
    (Checkers) (1915), Stewart Culin's studies of mancala, chess and playing cards (with pachisi, the Parcheesi and
    ludo family), Chinese dice and dominoes, Korean games and the Games of the North American Indians, and
    Falkener's Games Ancient and Oriental (backgammon, draughts, mancala and the ancient games);
  - puzzles, music and hobbies: the first Cross Word Puzzle Book (1924), Dudeney's Amusements in Mathematics and The
    Canterbury Puzzles, Prout's Harmony and Goetschius's Exercises in Melody-Writing, and Johnson's The Stamp
    Collector (1920);
  - role-playing games under open licences: the Dungeons & Dragons System Reference Document 5.1 (CC BY 4.0, with
    Wizards of the Coast's attribution notice) and the Fate SRD (Fate Core, Fate Accelerated and Fate Condensed,
    CC BY 3.0, with Evil Hat's attribution notice).
  Each old book's description says what has changed since (modern rules of bridge, chess notation and mahjong).

Already in the library and not repeated: the Internet Archive's books on chess, checkers, games and puzzles, and on
music theory (the "games" and "music" topics of open_catalogues.py), the old piano tuning and violin making books
(instr:), the musical instrument and video game manuals (manual collections), and Wikibooks (Chess, Go, Music
Theory) whole in the Kiwix library.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): Pagat.com card game rules, the FIDE Laws of
Chess, Wikibooks' game books (in Kiwix), the Game Accessibility Guidelines and AbleGamers (no open licence), the American Go Association's rules, Scrabble's rules, the official league rules of the sports (Open Music
Theory and Music Theory for the 21st-Century Classroom are now built in music_learning.py, musiclearn:),
AudioGames.net and the accessible game makers, the US Mint's and the Smithsonian National Postal Museum's pages.

Run from the repository's folder:
  python3 textbooks/games_hobbies.py games:capablanca_chess_fundamentals_1921 --out build/textbooks --limit 3
  python3 textbooks/games_hobbies.py --list games-hobbies
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "gameshobby"
GROUPS = {GROUP: "Reference, games and hobbies"}

RULES_NOTE = ("Published in {year}: an old book. Some games' rules and scoring have changed since (contract bridge, "
              "for example, replaced auction bridge after 1925); house rules and today's official rules may differ.")
OLD_NOTE = "Published in {year}: an old book; its prices, addresses and some of its terms are out of date."


def book(name, title, subject, publisher, archive, year, description, note=RULES_NOTE, country="United States"):
    """One old game or hobby book of the Internet Archive."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, country=country)


CARD_PDFS = [
    book("fosters_complete_hoyle_1916", "Foster's Complete Hoyle: an encyclopedia of games (R. F. Foster, 1916)",
         "Card and table game rules", "R. F. Foster (Frederick A. Stokes)", "fosterscompleteh00fost", 1916,
         "The rules of the indoor games played in America: whist, auction bridge, poker, cribbage, rummy, pinochle, "
         "euchre, five hundred, hearts, bezique, piquet, many solitaires (patience), dominoes, backgammon, checkers, "
         "chess, dice games, roulette and others, with the laws, the chances and advice on play."),
    book("fox_hoyles_games_1905", "Fox's Revised Edition of Hoyle's Games (1905)", "Card and table game rules",
         "Fox (New York)", "foxsrevisedediti00newy", 1905,
         "The standard Hoyle of 1905: the rules, laws and technical terms of whist, euchre, poker, cribbage, "
         "pinochle, casino, piquet, bezique, solitaire, backgammon, dominoes, checkers, chess and the other games of "
         "its day."),
    book("cadogan_games_of_patience_1887", "Illustrated Games of Patience (Lady Adelaide Cadogan, 1887)",
         "Solitaire (patience)", "Lady Adelaide Cadogan (Sampson Low)", "illustratedgames00cadoiala", 1887,
         "Twenty-five patience (solitaire) games, each with how to lay out the cards and the rules of play; the "
         "layouts are pictures, so they are described only by the text.", country="United Kingdom"),
    book("royal_auction_bridge_1914", "Royal Auction Bridge with Nullos (1914)", "Bridge", "R. F. Foster",
         "royalauctionbrid027157mbp", 1914,
         "Auction bridge as played in 1914: bidding, the royal spades and nullos, play of the hand and scoring.",
         note="Published in {year}: auction bridge, the game before contract bridge (1925 onward); today's bidding "
              "and scoring are different, but the play of the cards is the same."),
]
BOARD_PDFS = [
    book("smith_game_of_go_1908", "The Game of Go, the National Game of Japan (Arthur Smith, 1908)", "Go",
         "Arthur Smith (Moffat, Yard)", "gameofgonational00smitrich", 1908,
         "The first English book on go: the board and stones, the rules (capturing, ko, life and death, counting "
         "territory), openings, handicaps and illustrative games.",
         note="Published in {year}: an old book. The rules are the Japanese ones of its time; today's rule sets "
              "(Japanese, Chinese, AGA) differ in scoring details, and the opening theory has moved on."),
    book("capablanca_chess_fundamentals_1921", "Chess Fundamentals (José Raúl Capablanca, 1921)", "Chess",
         "José Raúl Capablanca (Harcourt, Brace)", "chessfundamental00capa", 1921,
         "The world champion's lessons for players: first principles and simple endings, the middle game, winning "
         "positions, general strategy and illustrative games, in descriptive notation (\"P-K4\").",
         note="Published in {year}: an old book in the old descriptive notation (today's books use algebraic "
              "notation, \"e4\"); the moves of chess have not changed."),
    book("lasker_common_sense_in_chess", "Common Sense in Chess (Emanuel Lasker)", "Chess",
         "Emanuel Lasker (David McKay)", "commonsenseinche00laskrich", 1910,
         "The world champion's lectures on the principles of play: the openings, the middle game, attack and "
         "defence, and the endgame, in descriptive notation.",
         note="Published in {year}: an old book in descriptive notation; the moves of chess have not changed."),
    book("freeborough_chess_openings", "Chess Openings, Ancient and Modern (Freeborough and Ranken)", "Chess",
         "E. Freeborough and C. E. Ranken (Kegan Paul)", "chessopeningsanc00freerich", 1905,
         "A reference of chess openings move by move, with their variations, in descriptive notation.",
         note="Published in {year}: opening theory has moved on a great deal since; descriptive notation.",
         country="United Kingdom"),
    book("babcock_rules_mah_jongg_1923", "Babcock's Rules for Mah-Jongg: the Red Book of Rules (1923)", "Mahjong",
         "Joseph Park Babcock (Mah-Jongg Sales Company of America)", "babcock_202209", 1923,
         "The rules of mahjong as first standardised for American players: the tiles (suits, honours, flowers), "
         "building the wall, play, melds (pungs, chows, kongs), going out and scoring.",
         note="Published in {year}: an old book. American mahjong today follows the National Mah Jongg League's "
              "yearly card, and Chinese, Japanese (riichi) and other styles differ: the tiles are the same."),
    book("lees_guide_draughts_checkers_1915", "A Complete Guide to the Game of Draughts (Checkers) (James Lees, 1915)",
         "Checkers (draughts)", "James Lees", "completeguidetog00lees", 1915,
         "Checkers (draughts) from the rules to the openings: the board and its numbered squares, the laws of the "
         "game, and the standard openings and endgame positions, move by move.", country="United Kingdom"),
    book("culin_mancala_1896", "Mancala, the National Game of Africa (Stewart Culin, 1896)", "Mancala",
         "Stewart Culin (US National Museum report)", "mancalanationalg00culi", 1896,
         "The mancala games (sowing games played with seeds or stones in rows of pits) across Africa and Asia: the "
         "boards and how several versions are played.", note=OLD_NOTE),
    book("culin_chess_playing_cards_1898", "Chess and Playing-Cards (Stewart Culin, 1898)", "Traditional games",
         "Stewart Culin (US National Museum report)", "chessplayingcard00culi", 1898,
         "The history of chess, playing cards, dice and the race games (pachisi, the family of Parcheesi and ludo) "
         "in many countries, from the Smithsonian's collection.", note=OLD_NOTE),
    book("culin_chinese_dice_dominoes_1895", "Chinese Games with Dice and Dominoes (Stewart Culin, 1895)",
         "Dice and dominoes", "Stewart Culin (US National Museum report)", "chinesegameswith01culi", 1895,
         "Chinese dice and domino games and how they are played.", note=OLD_NOTE),
    book("culin_korean_games_1895", "Korean Games, with notes on the corresponding games of China and Japan "
         "(Stewart Culin, 1895)", "Traditional games", "Stewart Culin (University of Pennsylvania)",
         "cu31924023272424", 1895,
         "Traditional games of Korea, China and Japan: board games (including go and its relatives), dice, cards, "
         "children's games and outdoor games.", note=OLD_NOTE),
    book("culin_games_north_american_indians_1907", "Games of the North American Indians (Stewart Culin, 1907)",
         "Traditional games", "Stewart Culin (Bureau of American Ethnology, 24th Annual Report)",
         "gamesofnorthamer00culirich", 1907,
         "The games of the Native peoples of North America as Culin recorded them nation by nation: dice and stick "
         "games, guessing games, hoop and pole, ball games, lacrosse and others.",
         note="Published in {year}: an old government report; its words about Native peoples are of its time and some "
              "are offensive today. Many of these games are still played and belong to their communities."),
    book("falkener_games_ancient_oriental_1892", "Games Ancient and Oriental, and How to Play Them (Edward Falkener, "
         "1892)", "Traditional games", "Edward Falkener (Longmans, Green)", "gamesancientorie00falkuoft", 1892,
         "The games of ancient Egypt, Greece and Rome, chess and its oriental forms, draughts, backgammon, mancala "
         "and magic squares, with how to play them.", note=OLD_NOTE, country="United Kingdom"),
]
PDFS = [
    book("cross_word_puzzle_book_1924", "The Cross Word Puzzle Book, first series (Simon and Schuster, 1924)",
         "Crossword puzzles", "Prosper Buranelli, F. Gregory Hartswick and Margaret Petherbridge (Simon and Schuster)",
         "crosswordpuzzleb00unse", 1924,
         "The first book of crossword puzzles (1924), the puzzles from the New York World with their clues and "
         "answers. The grids are pictures: their clues and answers are read as text.",
         note="Published in {year}: an old book; some clues use words and facts of its time."),
    book("dudeney_amusements_in_mathematics_1917", "Amusements in Mathematics (Henry Ernest Dudeney, 1917)",
         "Puzzles", "Henry Ernest Dudeney (Thomas Nelson)", "amusementsinmath00dude", 1917,
         "Hundreds of logic, number, geometry, chessboard and moving-counter puzzles, with their solutions.",
         note=OLD_NOTE, country="United Kingdom"),
    book("dudeney_canterbury_puzzles_1919", "The Canterbury Puzzles (Henry Ernest Dudeney, 1919)", "Puzzles",
         "Henry Ernest Dudeney (Thomas Nelson)", "canterburypuzzle00dudeuoft", 1919,
         "Puzzles told as tales of Chaucer's pilgrims and others, with full solutions.", note=OLD_NOTE,
         country="United Kingdom"),
    book("prout_harmony_1889", "Harmony: its Theory and Practice (Ebenezer Prout, 1889)", "Music theory",
         "Ebenezer Prout (Augener)", "harmonyitsthe00prouuoft", 1889,
         "A complete course in harmony: intervals, chords and their progressions, part-writing, cadences, modulation, "
         "seventh chords, suspensions and passing notes, with exercises. Music examples are printed notation, so "
         "they are described only by the text around them.",
         note="Published in {year}: an old book; its rules are those of classical harmony, still taught, though "
              "today's textbooks use other terms in places.", country="United Kingdom"),
    book("goetschius_melody_writing_1900", "Exercises in Melody-Writing (Percy Goetschius, 1900)", "Music theory",
         "Percy Goetschius (G. Schirmer)", "exercisesinmelod00goet", 1900,
         "A course in writing melodies: the scale, phrases and cadences, the period form, melodic movement, "
         "modulation and the song forms, with exercises.",
         note="Published in {year}: an old book; music examples are printed notation, described only by the text."),
    book("johnson_stamp_collector_1920", "The Stamp Collector: a guide to the world's postage stamps (Henry Johnson, "
         "1920)", "Stamp collecting", "Henry Johnson (Herbert Jenkins)", "stampcollectorgu00johnuoft", 1920,
         "Collecting postage stamps: what to collect, paper, watermarks, perforations and printing methods, "
         "errors and varieties, forgeries, mounting and albums, and the stamps of the world's countries.",
         note=OLD_NOTE, country="United Kingdom"),
]

# ====================================================================== openly licensed role-playing rules

SRD_NOTICE = ("This work includes material taken from the System Reference Document 5.1 (\"SRD 5.1\") by Wizards of "
              "the Coast LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 "
              "is licensed under the Creative Commons Attribution 4.0 International License available at "
              "https://creativecommons.org/licenses/by/4.0/legalcode. Dungeons & Dragons is a trademark of Wizards of "
              "the Coast; this copy is not endorsed by them.")
PDFS.append(dict(
    group=GROUP, name="dnd_srd_5_1_cc", title="System Reference Document 5.1 (Dungeons & Dragons fifth edition rules, "
    "CC BY 4.0)", subject="Tabletop role-playing games", publisher="Wizards of the Coast LLC", country="United States",
    licence="CC BY 4.0", licence_url="https://creativecommons.org/licenses/by/4.0/",
    licence_page="https://www.dndbeyond.com/srd", licence_text=r"publish content under Creative Commons",
    archive="srd-5.1-ccby-4.0-license_202301", level="reference", published="2023-01",
    version="SRD 5.1, Creative Commons release of January 2023 (Internet Archive item srd-5.1-ccby-4.0-license_202301; "
            "Wizards' own address refuses programs)",
    description="The fifth-edition Dungeons & Dragons rules Wizards of the Coast released under CC BY 4.0: races, "
                "classes, equipment, ability checks, combat, spellcasting and the spell list, the rules for running "
                "the game, magic items and monsters.",
    notice=SRD_NOTICE))
FATE = "https://fate-srd.com"
GUIDES = [dict(
    K.WEB, group=GROUP, name="fate_srd", title="Fate Core and Fate Accelerated: the System Reference Documents",
    subject="Tabletop role-playing games", publisher="Evil Hat Productions (Fate SRD site)", country="United States",
    licence="CC BY 3.0", licence_url="https://creativecommons.org/licenses/by/3.0/", licence_page=FATE + "/",
    licence_text=r"Creative Commons Attribution 3\.0 Unported", source=FATE + "/", sitemap=FATE + "/sitemap.xml",
    pages=r"^https://fate-srd\.com/(fate-core|fate-accelerated|fate-condensed)(/[a-z0-9-]+)+$",
    unit_rules=[(r"/fate-accelerated", "Fate Accelerated"), (r"/fate-condensed", "Fate Condensed"),
                (r".", "Fate Core")], limit=220,
    description="The rules of the Fate role-playing game, every page: Fate Core (aspects, skills, stunts, actions and "
                "outcomes, challenges, contests and conflicts, running the game), Fate Accelerated and Fate Condensed.",
    notice="This work is based on Fate Core System and Fate Accelerated Edition (found at https://www.faterpg.com/), "
           "products of Evil Hat Productions, LLC, developed, authored, and edited by Leonard Balsera, Brian Engard, "
           "Jeremy Keller, Ryan Macklin, Mike Olson, Clark Valentine, Amanda Valentine, Fred Hicks, and Rob Donoghue, "
           "and licensed for our use under the Creative Commons Attribution 3.0 Unported license "
           "(https://creativecommons.org/licenses/by/3.0/). Fate is a trademark of Evil Hat Productions, LLC.")]

COLLECTION = K.Collection("games", GROUP, pdfs=CARD_PDFS + BOARD_PDFS + PDFS, guides=GUIDES, words={
    "card-games": lambda: [f"games:{g['name']}" for g in CARD_PDFS],
    "board-games": lambda: [f"games:{g['name']}" for g in BOARD_PDFS],
    "games-hobbies": lambda: [f"games:{g['name']}" for g in PDFS + GUIDES]})

LICENCE_LINES = {
    "games_rpg": "www.dndbeyond.com/srd (checked at every build): the SRD is offered to \"publish content under Creative "
                 "Commons\" (CC BY 4.0), read from the Internet Archive's copy because media.dndbeyond.com refuses "
                 "programs; fate-srd.com (checked at every build): CC BY 3.0, robots.txt allows everything (2026-11-22).",
    "games_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so a "
                       "later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                       "2026-11-22).",
}
NOT_INCLUDED = [
    ("Pagat.com card game rules (John McLeod)", "\"(c) John McLeod\": copyright; link-only. Foster's Complete Hoyle "
     "(1916) is built for the classic games. Index: https://www.pagat.com/"),
    ("FIDE Laws of Chess", "Copyright of FIDE (no open licence found in its handbook); link-only. Capablanca's Chess "
     "Fundamentals is built. Index: https://handbook.fide.com/chapter/E012023"),
    ("Go rules (American Go Association, Japanese and Chinese rules; Sensei's Library)", "The AGA rules are the "
     "AGA's copyright and Sensei's Library's pages are under its own OpenContent licence (not checked as allowed); "
     "link-only. Smith's The Game of Go (1908) is built. Index: https://www.usgo.org/aga-concise-rules-go and "
     "https://senseis.xmp.net/"),
    ("Scrabble's rules and word lists", "Copyright and trademarks of Hasbro and Mattel, and the word lists of NASPA "
     "and Collins; link-only. Index: https://scrabble.hasbro.com/en-us/rules"),
    ("Official sports rules (NFL, NBA, MLB, NHL, FIFA Laws of the Game, NCAA rule books, USA Pickleball)", "Each "
     "league's copyright; no public-domain government edition exists; link-only. Index: "
     "https://www.theifab.com/laws/ and https://www.ncaa.org/sports/2013/11/5/playing-rules-administration.aspx"),
    ("Open Music Theory (Gotham and others, CC BY-SA)", "Its second edition's host viva.pressbooks.pub refuses "
     "programs; the first edition (openmusictheory.github.io, CC BY-SA 4.0) is built in the music collection "
     "(musiclearn:open_music_theory, 2026-11-23). Index: https://viva.pressbooks.pub/openmusictheory/"),
    ("Music Theory for the 21st-Century Classroom (Robert Hutchinson)", "Its colophon gives the GNU Free "
     "Documentation License 1.2 or later (found 2026-11-23); built in the music collection "
     "(musiclearn:music_theory_21st_century_classroom). Index: https://musictheory.pugetsound.edu/mt21c/"),
    ("Morphy's games, Lasker's Manual of Chess (1927) and Nimzowitsch's My System", "The Internet Archive copies found "
     "are later reprints or new translations (copyright) or have no text layer; left out. Index: "
     "https://archive.org/search?query=morphy+games+chess"),
    ("Wikibooks game books (Chess, Go, Card games, Puzzles)", "CC BY-SA, already whole in the Kiwix library "
     "(wikibooks_en_all). Index: https://en.wikibooks.org/wiki/Subject:Games"),
    ("Game Accessibility Guidelines and AbleGamers resources", "No open licence was found on their pages "
     "(2026-11-22): link-only. Index: https://gameaccessibilityguidelines.com/ and https://ablegamers.org/"),
    ("Canasta, Yahtzee, Farkle and other modern games' official rules", "Canasta (1939) and the modern dice and "
     "party games are later than 1931 or trademarked publishers' rules: link-only (Pagat.com describes many). "
     "Index: https://www.pagat.com/rummy/canasta.html"),
    ("Accessible games: AudioGames.net, American Printing House games, braille and large-print cards, tactile chess "
     "sets", "Copyright of each organisation and maker; link-only. Index: https://www.audiogames.net/ and "
     "https://www.aph.org/"),
    ("US Mint coin collecting pages and the Smithsonian National Postal Museum", "The US Mint's site refuses programs "
     "(\"403\", 2026-11-22); the Postal Museum's pages are under the Smithsonian's terms of use (only its Open Access "
     "items are CC0). Link-only. Index: https://www.usmint.gov/learn/collecting-basics and "
     "https://postalmuseum.si.edu/"),
    ("Photography and model railway books", "No public-domain guide with a text layer and current advice was found "
     "(the old photography books teach plate and darkroom processes; the model locomotive books are steam "
     "engineering); left out. Index: https://archive.org/search?query=subject%3Aphotography"),
    ("Game console, puzzle and hobby makers' manuals", "Already in the manual collections (video games, computers "
     "and game consoles); links for the makers. Index: https://www.nintendo.com/us/support/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
