"""The collection "Board games, puzzles, hobbies and accessible games (rules and manuals)" (category key
games_hobbies): the owner's request of 2026-11-22 for games and hobbies. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each rule book belongs to its publisher):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (board and card game rules,
            chess clocks and chess computers, mahjong and dominoes sets, model railroads and trains, coin and stamp
            albums). Video game and console manuals are already the video_games and computers collections;
  makers    the game publishers and accessible game makers: LINK-ONLY by the owner's rule (their rules are their
            copyright);
  guidance  the reference library's old public-domain rule books (textbooks/games_hobbies.py) and the accessible
            games pages as links.

The notice says first that modern rules are the publishers' and that the old public-domain rule books may differ.
"""

NOTICE = "Rules belong to each game's publisher: the links open the official rules. The old public-domain rule books in the reference library (Foster's Complete Hoyle, Babcock's Mah-Jongg) may differ from today's official rules. Small game pieces are a choking hazard for children under 3."

IA_WORDS = ["board game", "card game", "rules of play", "chess clock", "chess computer", "electronic chess", "mahjong", "dominoes", "model railroad", "model train", "lionel", "coin album", "stamp album"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="games_hobbies", prefix="gm", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="hasbro", maker="Hasbro", type="board games (Monopoly, Scrabble in North America, Clue)", library="https://instructions.hasbro.com/", site="hasbro.com"),
    dict(key="mattel", maker="Mattel Games", type="card and board games (UNO, Scrabble outside North America)", library="https://service.mattel.com/", site="mattel.com"),
    dict(key="aph-games", maker="American Printing House for the Blind", type="accessible games, braille playing cards and tactile boards", library="https://www.aph.org/", site="aph.org"),
    dict(key="maxi-aids", maker="MaxiAids", type="large-print and braille playing cards and games", library="https://www.maxiaids.com/", site="maxiaids.com"),
    dict(key="dgt", maker="DGT (Digital Game Technology)", type="chess clocks and electronic boards", library="https://digitalgametechnology.com/", site="digitalgametechnology.com"),
    dict(key="national-mah-jongg-league", maker="National Mah Jongg League", type="the yearly American mahjong card", library="https://www.nationalmahjonggleague.org/", site="nationalmahjonggleague.org"),
    dict(key="lionel", maker="Lionel", type="model trains", library="https://www.lionel.com/", site="lionel.com"),
    dict(key="bachmann", maker="Bachmann Trains", type="model trains", library="https://www.bachmanntrains.com/", site="bachmanntrains.com"),
]]

GUIDANCE = [
    dict(title="Foster's Complete Hoyle and the other old rule books (in the reference library: games-hobbies)",
         url="https://archive.org/details/fosterscompleteh00fost", by="the Internet Archive"),
    dict(title="Pagat.com card game rules (copyright, open it in a browser)",
         url="https://www.pagat.com/", by="John McLeod"),
    dict(title="AudioGames.net: games for blind players (copyright, open it in a browser)",
         url="https://www.audiogames.net/", by="AudioGames.net"),
]

CATEGORY = dict(
    name='Board games, puzzles, hobbies and accessible games (rules and manuals)',
    description="Board and card game rules, chess clocks and chess computers, mahjong and dominoes, model trains, coin and stamp albums, and accessible games (braille and large-print cards, tactile boards): the Internet Archive's rule books, the publishers' rules pages (links) and the reference library's old public-domain rule books. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
