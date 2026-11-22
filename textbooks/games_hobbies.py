"""Games and hobbies for the reference library, in the group "Reference, games and hobbies" (the owner's request of
2026-11-22). Keys: games-hobbies (every book), games:<name>.

What this module builds, in plain words: old public-domain books of game rules and hobbies from the Internet Archive
(published before 1931; the builder checks each item's year at every build), each IN FULL:
  - Foster's Complete Hoyle (1916): the rules of the card games (whist, bridge, poker, cribbage, rummy, pinochle,
    euchre, solitaire and many more), dominoes, backgammon, checkers, chess, dice games and others;
  - Arthur Smith's The Game of Go (1908), the first book on go in English;
  - José Raúl Capablanca's Chess Fundamentals (1921);
  - Babcock's Rules for Mah-Jongg (1923), the "red book" that brought mahjong rules to America;
  - James Lees's Complete Guide to the Game of Draughts (Checkers) (1915);
  - the first Cross Word Puzzle Book (Simon and Schuster, 1924), with its answers;
  - Ebenezer Prout's Harmony: its Theory and Practice (1889) and Percy Goetschius's Exercises in Melody-Writing
    (1900) for music theory;
  - Henry Johnson's The Stamp Collector (1920) for stamp collecting.
  Each old book's description says what has changed since (modern rules of bridge, chess and mahjong, prices).

Already in the library and not repeated: the Internet Archive's books on chess, checkers, games and puzzles, and on
music theory (the "games" and "music" topics of open_catalogues.py), the old piano tuning and violin making books
(instr:), the musical instrument and video game manuals (manual collections), and Wikibooks (Chess, Go, Music
Theory) whole in the Kiwix library.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): Pagat.com card game rules, the FIDE Laws of
Chess, the American Go Association's rules, Scrabble's rules, the official league rules of the sports, Open Music
Theory and Hutchinson's Music Theory for the 21st-Century Classroom (licence not confirmed or robots.txt refuses),
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


PDFS = [
    book("fosters_complete_hoyle_1916", "Foster's Complete Hoyle: an encyclopedia of games (R. F. Foster, 1916)",
         "Card and table game rules", "R. F. Foster (Frederick A. Stokes)", "fosterscompleteh00fost", 1916,
         "The rules of the indoor games played in America: whist, auction bridge, poker, cribbage, rummy, pinochle, "
         "euchre, five hundred, hearts, bezique, piquet, many solitaires (patience), dominoes, backgammon, checkers, "
         "chess, dice games, roulette and others, with the laws, the chances and advice on play."),
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
    book("cross_word_puzzle_book_1924", "The Cross Word Puzzle Book, first series (Simon and Schuster, 1924)",
         "Crossword puzzles", "Prosper Buranelli, F. Gregory Hartswick and Margaret Petherbridge (Simon and Schuster)",
         "crosswordpuzzleb00unse", 1924,
         "The first book of crossword puzzles (1924), the puzzles from the New York World with their clues and "
         "answers. The grids are pictures: their clues and answers are read as text.",
         note="Published in {year}: an old book; some clues use words and facts of its time."),
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

COLLECTION = K.Collection("games", GROUP, pdfs=PDFS,
                          words={"games-hobbies": lambda: [f"games:{g['name']}" for g in PDFS]})

LICENCE_LINES = {
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
    ("Open Music Theory (Gotham and others, CC BY-SA)", "Openly licensed, but its host viva.pressbooks.pub's "
     "robots.txt refuses programs (checked 2026-11-22); link-only. Index: https://viva.pressbooks.pub/"
     "openmusictheory/"),
    ("Music Theory for the 21st-Century Classroom (Robert Hutchinson)", "Its pages state no licence the builder could "
     "find (checked 2026-11-22); link-only until one is confirmed. Index: https://musictheory.pugetsound.edu/mt21c/"),
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
