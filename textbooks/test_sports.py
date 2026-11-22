"""Self-test of the sports collection (sports.py and sports_data.py, keys sport:, group "Reference, sports") with
MADE-UP data only: nothing is downloaded.

It checks that the module is registered once with its request words (each at most 256 jobs; sports-teams split by
sport), reaches sources.py with its group, licence lines, ALLOWED and NOT_INCLUDED rows (each with an address); that
every rule book is dated before 1931, says its rules are history and carries the safety notice; that the official
league rule books (IFAB, NFL ...), the Lahman database and Sports-Reference are link-only; that the data books are
made right from made-up rows: a league table from match results, Retrosheet season records and career totals (with
Retrosheet's notice on every page), a team page and a player page from made-up Wikidata (a living player gets no
birth date), and the Olympic Games; and that the index is made offline with keys the library has.

Run it from the repository's folder:   python3 -m pytest textbooks/test_sports.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import sports  # noqa: E402
import sports_data as SD  # noqa: E402


def test_registered_with_its_words():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert sports in more_refs.modules() and prefixes.count("sport") == 1
    every = set()
    for word in ["sports-rules", "sports-teams", "sports-stats", "sports"] + \
            [f"sports-teams-{w}" for w in ("football", "basketball", "baseball", "hockey", "soccer", "cricket",
                                           "rugby", "lacrosse")]:
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        assert all(k.startswith("sport:") for k in keys), word
        every |= set(keys)
    assert every == set(sports.COLLECTION.own_keys())
    assert set(sources.expand_keys(["sports"])) == every
    assert sources.GROUPS["sports"] == "Reference, sports"
    assert set(sports.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED[SD.RETRO_LICENCE] == "open"
    for row in sports.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_rule_books():
    for g in sports.RULE_PDFS + sports.STATS_PDFS:
        assert g["group"] == "sports" and g["old_public_domain"] and int(g["published"]) < 1931, g["name"]
        assert "Published in" in g["description"] and sports.SPORTS_SAFETY in g["notice"], g["name"]
        assert B.licence_kind(B.licence_short(g["licence"])) == "open", g["name"]
    boxing = sports.COLLECTION.pdfs["us_rules_for_boxing_1918"]
    assert "US government work" in boxing["description"]
    assert "HEADS UP" in sports.SPORTS_SAFETY and "911" in sports.SPORTS_SAFETY


def test_link_only_sources():
    rows = " ".join(r[0] + " " + r[1] for r in sports.NOT_INCLUDED)
    for words in ("IFAB", "NFL", "Lahman", "Sports-Reference", "USABA", "Wikibooks", "olympics.com"):
        assert words in rows, words
    keys = " ".join(sources.expand_keys(["sports"]))
    for left_out in ("ifab", "lahman", "nfl_rulebook"):
        assert left_out not in keys


def test_league_table():
    matches = [{"team1": "Ayton", "team2": "Beeford", "score": {"ft": [2, 0]}},
               {"team1": "Beeford", "team2": "Ceeville", "score": {"ft": [1, 1]}},
               {"team1": "Ceeville", "team2": "Ayton", "score": {"ft": [0, 3]}},
               {"team1": "Ayton", "team2": "Ceeville", "score": [1, 1]},
               {"team1": "Ayton", "team2": "Beeford"}]                       # not played yet: left out
    table = SD.league_table(matches)
    assert table[0] == ("Ayton", 3, 2, 1, 0, 6, 1, 5, 7)
    assert [r[0] for r in table] == ["Ayton", "Ceeville", "Beeford"]
    assert SD.season_names(False, __import__("datetime").date(2012, 5, 1)) == ["2010-11", "2011-12", "2012-13"]


def test_retrosheet_seasons_and_careers():
    teams = SD.retro_teams([{"TEAM": "NYA", "LEAGUE": "AL", "CITY": "New York", "NICKNAME": "Yankees",
                             "FIRST": "1903", "LAST": "2025"}])
    rows = [{"stattype": "value", "gametype": "regular", "date": "19270415", "team": "NYA", "win": "1", "loss": "0",
             "tie": "0", "b_r": "5", "p_r": "2"},
            {"stattype": "official", "gametype": "regular", "date": "19270415", "team": "NYA", "win": "1",
             "loss": "0", "tie": "0", "b_r": "5", "p_r": "2"},
            {"stattype": "value", "gametype": "worldseries", "date": "19271005", "team": "NYA", "win": "1",
             "loss": "0", "tie": "0", "b_r": "5", "p_r": "4"},
            {"stattype": "value", "gametype": "regular", "date": "19270416", "team": "NYA", "win": "0", "loss": "1",
             "tie": "0", "b_r": "1", "p_r": "3"}]
    records = SD.season_records(rows, teams)
    assert records == {1927: {"AL": {"New York (NYA)": [1, 1, 0, 6, 5, 2]}}}
    body = SD.season_page_body(records[1927])
    assert "American League" in body and "<td>.500</td>" in body
    bat, pit = SD.career_totals(
        [{"stattype": "value", "gametype": "regular", "id": "ruthb101", "b_ab": "4", "b_h": "2", "b_hr": "1"},
         {"stattype": "value", "gametype": "regular", "id": "ruthb101", "b_ab": "3", "b_h": "1", "b_hr": "0"}],
        [{"stattype": "value", "gametype": "regular", "id": "youngc01", "wp": "1", "p_ipouts": "27", "p_er": "2"}])
    assert bat["ruthb101"]["h"] == 3 and bat["ruthb101"]["g"] == 2 and SD.avg(3, 7) == ".429"
    assert pit["youngc01"]["w"] == 1 and SD.innings(28) == "9.1" and SD.era(2, 27) == "2.00"
    assert SD.player_names([{"id": "ruthb101", "first": "Babe", "last": "Ruth"}]) == {"ruthb101": "Babe Ruth"}
    assert "copyrighted by Retrosheet" in SD.retro_notice_html()
    assert SD.RETRO_NOTICE.startswith("The information used here was obtained free of charge from and is "
                                      "copyrighted by Retrosheet.")


def made_up_entity(qid, label, died=None, born=None):
    """A made-up Wikidata entity with a few statements."""
    def item(prop, value, quals=None):
        st = {"mainsnak": {"snaktype": "value", "datavalue": {"type": "wikibase-entityid", "value": {"id": value}}},
              "rank": "normal"}
        if quals:
            st["qualifiers"] = {p: [{"snaktype": "value", "datavalue": {"type": "time", "value": {"time": t}}}]
                                for p, t in quals.items()}
        return st

    def time(value):
        return {"mainsnak": {"snaktype": "value", "datavalue": {"type": "time", "value": {"time": value}}},
                "rank": "normal"}
    claims = {"P54": [item("P54", "Q100", {"P580": "+1990-00-00T00:00:00Z", "P582": "+1995-00-00T00:00:00Z"})],
              "P413": [item("P413", "Q200")], "P166": [item("P166", "Q300", {"P585": "+1993-00-00T00:00:00Z"})],
              "P569": [time(born or "+1966-03-04T00:00:00Z")]}
    if died:
        claims["P570"] = [time(died)]
    return {"id": qid, "labels": {"en": {"value": label}}, "claims": claims}


def test_team_and_player_pages():
    names = {"Q100": "Made-up City Comets", "Q200": "goaltender", "Q300": "Made-up Trophy"}
    living = SD.player_facts(made_up_entity("Q1", "Pat Example"), names)
    assert living["alive"] and living["born"] == "" and living["teams"] == [("Made-up City Comets", "1990 to 1995")]
    body = SD.player_page_body(living, {"Made-up City Comets": "team-comets"})
    assert "1966" not in body and "Born" not in body and 'href="team-comets"' in body and "Made-up Trophy" in body
    dead = SD.player_facts(made_up_entity("Q2", "Old Timer", died="+2001-01-01T00:00:00Z"), names)
    assert dead["born"] == "1966" and dead["died"] == "2001"
    assert "Born" in SD.player_page_body(dead, {})
    teams = SD.gather_teams([{"team": "Q100", "teamLabel": "Made-up City Comets", "from": "1990-01-01T00:00:00Z",
                              "inception": "1972-01-01T00:00:00Z", "venueLabel": "Made-up Arena",
                              "placeLabel": "Q999"}])
    team = teams["Q100"]
    assert team["inception"] == {"1972"} and team["places"] == set()        # an unlabelled item is left out
    by_team, seasons = SD.gather_champions([{"season": "Q5", "seasonLabel": "1993 season", "winner": "Q100",
                                             "winnerLabel": "Made-up City Comets", "time": "1993-06-01T00:00:00Z"}])
    page = SD.team_page_body(team, by_team["Q100"], [("Pat Example", "player-pat")])
    assert "Made-up Arena" in page and "1993 season" in page and "player-pat" in page
    assert seasons == [("1993 season", "Made-up City Comets", "1993")]
    assert SD.last_name("Babe Ruth") == "ruth babe"
    for row in SD.LEAGUES:
        assert row[1].startswith("Q") and row[2] and row[5]


def test_olympics_rows():
    games = SD.gather_games([{"g": "Q8", "gLabel": "Made-up Games", "kind": "Q159821",
                              "start": "1996-07-19T00:00:00Z", "placeLabel": "Made-up City", "n": "10318"}])
    assert games["Q8"]["kind"] == "Summer Olympic Games" and games["Q8"]["start"] == "1996-07-19"
    assert games["Q8"]["participants"] == "10318"


def test_index_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    book_fn, _sign = sports.COLLECTION.makers["index"]
    left_out = []
    book = book_fn("index", "work", None, left_out)
    assert book.pages and book.licence == X.CC0_INDEX and not left_out, left_out
    text = " ".join(p.body for p in book.pages)
    for words in ("goalball", "Beep Baseball", "theifab.com", "firstaid:cdc_seizures_concussion"):
        assert words in text, words
