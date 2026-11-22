"""Picture packs for GAMES AND HOBBIES (the owner's requests of 2026-11-22). Used by build_packs.py in the same way as
its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with
more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit
counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise card games and
cards, the board and tile games of many cultures (backgammon, draughts, go, xiangqi, mahjong, mancala, Chinese
checkers, ludo and pachisi), dice and table games, puzzles, stamp albums and dartboards.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no card's rank, a position's moves or a game's score is named unless the category itself names it. Casino
games are named as games only. Board, tile and dice games end with SMALL_PARTS_NOTE (the kit uses the same words in
games_sources.py).

The packs (GAMES_PACKS):
  commons_card_games          Wikimedia Commons (CC0, public domain or CC BY files only): playing cards and
                              French-suited cards, poker, blackjack, solitaire (patience), cribbage, craps and
                              roulette.
  commons_board_games_world   Commons: backgammon, draughts, go (boards and stones), xiangqi (Chinese chess),
                              mahjong, mancala, bao and oware, Chinese checkers, ludo, pachisi and Parcheesi, chess
                              clocks, Scrabble, bingo, dice games and tabletop role-playing games.
  commons_puzzles_hobbies     Commons: sudoku, crosswords, stamp albums, dartboards and billiard tables.
  open_images_games           Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                              card games, poker, dominoes, mahjong, darts, tabletop games, postage stamps and toy
                              trains. No label is asked twice (packs/test_games.py checks).

Not repeated here: the chess packs (chess_pieces, chess_positions, chess_drawings), the playing card packs
(playing_cards, drawn_cards), wikidata_toys_games, the Commons categories other packs ask (Chess sets, Dice, Dominoes,
Mahjong tiles, Jigsaw puzzles, Rubik's Cube, Board games, Darts, Model railways) and the Open Images labels other packs
ask (Playing card, Dice, Chess, Chessboard, Board game, Jigsaw puzzle, Billiard table, Dartboard, Coin and others). No
Commons category of braille or tactile games was found (the kit's games_sources.py says so).

    python packs/games_packs.py commons_board_games_world --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from homestead_packs import thing

SMALL_PARTS_NOTE = "Small pieces: keep them away from children under 3, who can choke on them."

CARDS = [
    thing("Playing cards", "playing cards"),
    thing("French-suited playing cards", "French-suited playing cards (hearts, diamonds, clubs and spades)",
          deeper=True),
    thing("Poker", "a game of poker", deeper=True),
    thing("Blackjack", "a game of blackjack (twenty-one)", deeper=True),
    thing("Solitaire", "solitaire (patience), a card game for one player", deeper=True),
    thing("Cribbage", "cribbage: the card game and its pegging board", SMALL_PARTS_NOTE, True),
    thing("Craps", "craps, a dice game", SMALL_PARTS_NOTE),
    thing("Roulette", "roulette: the wheel and its betting table"),
]
BOARDS = [
    thing("Backgammon", "backgammon", SMALL_PARTS_NOTE),
    thing("Draughts", "draughts (checkers)", SMALL_PARTS_NOTE),
    thing("Go (game)", "the game of go (weiqi, baduk)", SMALL_PARTS_NOTE),
    thing("Goban", "a goban, the board for go: a grid of 19 by 19 lines", SMALL_PARTS_NOTE),
    thing("Go stones", "go stones, the black and white pieces of go", SMALL_PARTS_NOTE),
    thing("Xiangqi", "xiangqi (Chinese chess)", SMALL_PARTS_NOTE, True),
    thing("Mahjong", "mahjong, a tile game", SMALL_PARTS_NOTE, True),
    thing("Mancala", "a mancala game, played by sowing seeds or stones around rows of pits", SMALL_PARTS_NOTE, True),
    thing("Bao (game)", "bao, an East African mancala game with four rows of pits", SMALL_PARTS_NOTE),
    thing("Oware", "oware, a West African mancala game with two rows of six pits", SMALL_PARTS_NOTE),
    thing("Chinese checkers", "Chinese checkers, a race game on a star-shaped board", SMALL_PARTS_NOTE),
    thing("Ludo", "ludo, a race game for two to four players moved by dice", SMALL_PARTS_NOTE),
    thing("Pachisi", "pachisi, the Indian race game on a cross-shaped board", SMALL_PARTS_NOTE),
    thing("Parcheesi", "Parcheesi, the American race game based on pachisi", SMALL_PARTS_NOTE),
    thing("Chess clocks", "a chess clock, two linked clocks that time each player's moves"),
    thing("Scrabble", "a Scrabble board and tiles", SMALL_PARTS_NOTE),
    thing("Bingo", "bingo: the cards and numbered balls"),
    thing("Dice games", "a dice game", SMALL_PARTS_NOTE),
    thing("Tabletop role-playing games", "a tabletop role-playing game"),
]
PUZZLES = [
    thing("Sudoku", "a sudoku puzzle: a 9 by 9 grid to fill so every row, column and box has the digits 1 to 9"),
    thing("Crosswords", "a crossword puzzle", deeper=True),
    thing("Stamp albums", "a stamp album, a book for collecting postage stamps", deeper=True),
    thing("Dartboards", "a dartboard", "Darts: stand well clear of the board and the thrower."),
    thing("Billiard tables", "a billiard (pool) table"),
]


def build_commons_card_games(limit):
    """The commons_card_games pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CARDS, limit, "gmcards")


def build_commons_board_games_world(limit):
    """The commons_board_games_world pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BOARDS, limit, "gmboards")


def build_commons_puzzles_hobbies(limit):
    """The commons_puzzles_hobbies pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PUZZLES, limit, "gmpuzzles")


GAMES_OI = [
    group("What games are being played here?",
          {"Card game": "a card game", "Poker": "poker", "Dominoes": "dominoes", "Mahjong": "mahjong",
           "Dart": "darts", "Tabletop game": "a tabletop game"}),
    group("What hobby things are in this picture?",
          {"Postage stamp": "a postage stamp", "Toy train": "a toy train"}),
]


def build_open_images_games(limit):
    """open_images_games (see the module docstring)."""
    return build_oi_gap("open_images_games", GAMES_OI, limit, 9403)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
GAMES_PACKS = {
    "commons_card_games": (build_commons_card_games, COMMONS_LICENCE.format(
        what="playing card, poker, blackjack, solitaire, cribbage, craps and roulette")),
    "commons_board_games_world": (build_commons_board_games_world, COMMONS_LICENCE.format(
        what="backgammon, draughts, go, xiangqi, mahjong, mancala, race game, Scrabble, bingo and dice game")),
    "commons_puzzles_hobbies": (build_commons_puzzles_hobbies, COMMONS_LICENCE.format(
        what="sudoku, crossword, stamp album, dartboard and billiard table")),
    "open_images_games": (build_open_images_games, OI_LICENCE),
}
GAMES_LIMITS = {
    "commons_card_games": 700,             # 8 categories; Playing cards has most files
    "commons_board_games_world": 1000,     # 19 categories
    "commons_puzzles_hobbies": 500,        # 5 categories
    "open_images_games": 800,              # 8 labels
}
GAMES_COMMONS_KEYS = ("commons_card_games", "commons_board_games_world", "commons_puzzles_hobbies")
GAMES_SPECS = CARDS + BOARDS + PUZZLES


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a games and hobbies pack builder.")
    parser.add_argument("key", choices=sorted(GAMES_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = GAMES_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
