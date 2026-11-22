"""GAMES AND HOBBIES for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/games_packs.py (group "permissive"; the kit downloads them with
    prepare_pack);
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (GAMES_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it, only when the user ticks the matching
choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say: no card's rank or game position is guessed, casino games are
named as games only, and board, tile and dice games end with SMALL_PARTS_NOTE, the same words as the packs'
(packs/test_leisure_packs.py checks).

Picture-making (GAMES_PICTURE_MAKING_OK): the Commons card, board game and puzzle collections (things); sources.py
puts every other key in NOT_FOR_PICTURE_MAKING (the Open Images photos show people playing).
Topics: all in the home topic (Home and household).

    python -c "import sources, games_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The note, word for word as in packs/games_packs.py.
SMALL_PARTS_NOTE = "Small pieces: keep them away from children under 3, who can choke on them."

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def gear(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# Categories of packs/games_packs.py, the same answers.
GAMES_SA = [
    gear("Backgammon", "backgammon", SMALL_PARTS_NOTE),
    gear("Draughts", "draughts (checkers)", SMALL_PARTS_NOTE),
    gear("Goban", "a goban, the board for go: a grid of 19 by 19 lines", SMALL_PARTS_NOTE),
    gear("Mancala", "a mancala game, played by sowing seeds or stones around rows of pits", SMALL_PARTS_NOTE, True),
    gear("Chinese checkers", "Chinese checkers, a race game on a star-shaped board", SMALL_PARTS_NOTE),
    gear("Cribbage", "cribbage: the card game and its pegging board", SMALL_PARTS_NOTE, True),
    gear("Sudoku", "a sudoku puzzle: a 9 by 9 grid to fill so every row, column and box has the digits 1 to 9"),
    gear("Dartboards", "a dartboard", "Darts: stand well clear of the board and the thrower."),
]


def prepare_games_commons_sa(source, data_dir, work, cap):
    """Commons backgammon, draughts, go, mancala, Chinese checkers, cribbage, sudoku and dartboard categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(GAMES_SA, cap, source.test, "games-commons-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


GAMES_SOURCES = [
    Source("commons_card_games", "Card games: playing cards, poker, blackjack, solitaire, cribbage, craps and roulette (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 700, 10, prepare_pack, "about 150 MB"),
    Source("commons_board_games_world", "Board games of the world: backgammon, draughts, go, xiangqi, mahjong, mancala, Chinese checkers, ludo, pachisi, Scrabble, bingo, dice and role-playing games (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 220 MB"),
    Source("commons_puzzles_hobbies", "Sudoku, crosswords, stamp albums, dartboards and billiard tables (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 5, prepare_pack, "about 110 MB"),
    Source("open_images_games", "People playing card games, poker, dominoes, mahjong, darts and tabletop games, postage stamps and toy trains (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 800, 10, prepare_pack, "about 170 MB"),
    Source("games_commons_sa", "Wikimedia Commons: backgammon, draughts, go boards, mancala, Chinese checkers, cribbage, sudoku and dartboards, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 400, 10, prepare_games_commons_sa, "about 100 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons games (things); never Open Images (people).
GAMES_PICTURE_MAKING_OK = {"commons_card_games", "commons_board_games_world", "commons_puzzles_hobbies",
                           "games_commons_sa"}

GAMES_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Chess sets, Dice, Dominoes, Mahjong tiles, Jigsaw puzzles, "
        "Rubik's Cube, Board games, Darts and Model railways: not asked twice; the chess and card datasets "
        "(chess_pieces, chess_positions, chess_drawings, playing_cards, drawn_cards) cover chess and card faces.",
    "Braille, large-print and tactile games": "No Commons category of braille playing cards, braille dice, tactile "
        "chess sets or games for blind players was found (November 2026), and the makers' product photos (APH, "
        "MaxiAids) are their copyright; the manual collection games_hobbies links them.",
    "Commons categories that do not exist (November 2026)": "Cribbage boards, Go boards, Crossword puzzles, Nine men's "
        "morris, Liar's dice, Polyhedral dice, Playing card suits.",
    "BoardGameGeek images": "Each image is its uploader's (BoardGameGeek's terms forbid reuse); not used.",
    "Open Images labels asked elsewhere": "Playing card, Dice, Chess, Chessboard, Board game, Jigsaw puzzle, Billiard "
        "table, Dartboard, Coin: asked by other packs.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the games and hobbies share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in GAMES_SOURCES if s.key == "games_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="games_co-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
