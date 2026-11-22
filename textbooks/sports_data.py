"""The data-made books of the sports collection (textbooks/sports.py, keys sport:): teams and players from Wikidata,
the Olympic Games from Wikidata, baseball statistics from Retrosheet, and football (soccer) league tables from
openfootball. Not a source module itself (it is not in more_refs.MODULES): sports.py lists these makers in its
Collection, and this file holds the work.

What each maker does, in plain words:
  teams_<league>   one book per league (NFL, NBA, MLB, NHL, MLS, the Premier League and others in LEAGUES): a page per
                   team (founded, folded, home venue, home city, sport, head coach, its years in the league and the
                   league titles Wikidata records) and a page per notable player (the players of those teams with the
                   most Wikipedia articles, Wikidata's own measure of notability: their positions, teams with years,
                   awards with years and, only for people who have died, the years of birth and death). Only facts
                   Wikidata states; no invented biography, nothing private about living people (no birth date,
                   birthplace, family or address). Wikidata is CC0.
  olympics         the Summer and Winter Olympic Games (Wikidata): each Games' dates, host city and country, number
                   of participants, and the event winners Wikidata records ("winner", P1346), exactly as it records
                   them.
  stats_retrosheet_seasons   every season's team records (won, lost, tied, runs scored and allowed) worked out from
                   Retrosheet's box scores (its team statistics file), one page per season, by league.
  stats_retrosheet_careers   career batting and pitching totals worked out from Retrosheet's box scores (players with
                   at least CAREER_HITS hits, CAREER_WINS wins or CAREER_SAVES saves), pages by the first letter of the
                   last name, and leader boards. Retrosheet's notice (RETRO_NOTICE) is shown prominently on every page,
                   as its terms require.
  stats_football_<code>      one book per league (the English Premier League, the Bundesliga, La Liga, Serie A, Ligue 1,
                   Major League Soccer): each season's table worked out from openfootball's match results (CC0), a page
                   per season and a page of champions.

Every book says where its facts come from and the date they were read ("as of"). The tables are worked out here from
the sources' own rows and say so: points deductions, forfeits and other decisions of a league are not in the data, so a
few tables may differ from the official ones.

Wikidata is asked through its Query Service (query.wikidata.org/sparql), Wikimedia's documented interface for
programs (its robots.txt asks web crawlers to keep away from /sparql; it is used here as the repository's picture
collections use it: one query at a time, with the User-Agent Wikimedia's policy asks for, waiting as long as the
service asks when it says "429"), and through the Wikibase API (wbgetentities) for each player's statements.
"""

import csv
import datetime
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "sports"
WIKIDATA_LICENCE = "CC0 1.0"
WIKIDATA_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
WDQS = "https://query.wikidata.org/sparql"
WB_API = "https://www.wikidata.org/w/api.php"
WD_ENTITY = "https://www.wikidata.org/wiki/"
WDQS_PAUSE = 2.0                       # seconds between two queries
_last = {"wdqs": 0.0, "wb": 0.0}

# How many notable players each league book holds (the players of its teams with the most Wikipedia articles).
PLAYERS_PER_LEAGUE = 150

SPORTS_NOTE = ("Facts as Wikidata states them on the day they were read (the \"as of\" date on the first page); "
               "Wikidata is written by volunteers and can be wrong or out of date. Nothing here is a biography: only "
               "career facts are given for living people, and no private details.")

# ====================================================================== the leagues

# (book name, Wikidata id, words its English label must match (checked at build), title, sport, request word part).
LEAGUES = [
    ("nfl", "Q1215884", r"National Football League", "National Football League (NFL)", "American football",
     "football"),
    ("nba", "Q155223", r"National Basketball Association", "National Basketball Association (NBA)", "basketball",
     "basketball"),
    ("wnba", "Q2593221", r"Women's National Basketball Association",
     "Women's National Basketball Association (WNBA)", "basketball", "basketball"),
    ("mlb", "Q1163715", r"Major League Baseball", "Major League Baseball (MLB)", "baseball", "baseball"),
    ("nhl", "Q1215892", r"National Hockey League", "National Hockey League (NHL)", "ice hockey", "hockey"),
    ("mls", "Q18543", r"Major League Soccer", "Major League Soccer (MLS)", "association football (soccer)",
     "soccer"),
    ("nwsl", "Q1101443", r"National Women's Soccer League", "National Women's Soccer League (NWSL)",
     "association football (soccer)", "soccer"),
    ("premier_league", "Q9448", r"Premier League", "Premier League (England)", "association football (soccer)",
     "soccer"),
    ("womens_super_league", "Q950844", r"Women's Super League", "Women's Super League (England)",
     "association football (soccer)", "soccer"),
    ("la_liga", "Q324867", r"La Liga", "La Liga (Spain)", "association football (soccer)", "soccer"),
    ("bundesliga", "Q82595", r"Bundesliga", "Bundesliga (Germany)", "association football (soccer)", "soccer"),
    ("serie_a", "Q15804", r"Serie A", "Serie A (Italy)", "association football (soccer)", "soccer"),
    ("ligue_1", "Q13394", r"Ligue 1", "Ligue 1 (France)", "association football (soccer)", "soccer"),
    ("ipl", "Q396412", r"Indian Premier League", "Indian Premier League (cricket)", "cricket", "cricket"),
    ("big_bash", "Q4905035", r"Big Bash League", "Big Bash League (cricket, Australia)", "cricket", "cricket"),
    ("super_rugby", "Q855988", r"Super Rugby", "Super Rugby (rugby union)", "rugby union", "rugby"),
    ("nll", "Q1550259", r"National Lacrosse League", "National Lacrosse League (box lacrosse)", "lacrosse",
     "lacrosse"),
    ("pll", "Q60750165", r"Premier Lacrosse League", "Premier Lacrosse League (field lacrosse)", "lacrosse",
     "lacrosse"),
]
LEAGUE_BY_NAME = {row[0]: row for row in LEAGUES}

# ====================================================================== asking Wikidata


def _wait(kind, pause):
    """Keep the pause between two requests of one kind."""
    wait = pause - (time.monotonic() - _last[kind])
    if wait > 0:
        time.sleep(wait)


def _cached(cache, name):
    """The path of a cached answer (None without a cache folder)."""
    if not cache:
        return None
    folder = os.path.join(cache, "wikidata")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, K.sha(name) + ".json")


def wdqs(query, cache=None, tries=6):
    """The result rows of a SPARQL query ([{variable: value}], values as plain strings; ids as "Q123"). One query at a
    time, WDQS_PAUSE apart; a "429" or "503" answer is waited out (its Retry-After, at most five minutes) and asked
    again. The answer is kept in the cache folder for the same day."""
    import build_textbooks as B
    path = _cached(cache, f"wdqs {datetime.date.today()} {query}")
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    url = WDQS + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    for attempt in range(tries):
        _wait("wdqs", WDQS_PAUSE)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": B.USER_AGENT,
                                                       "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            delay = e.headers.get("Retry-After") if e.headers else None
            time.sleep(min(300, int(delay) if (delay or "").isdigit() else 60 * (attempt + 1)))
        except (urllib.error.URLError, OSError):
            if attempt == tries - 1:
                raise
            time.sleep(30 * (attempt + 1))
        finally:
            _last["wdqs"] = time.monotonic()
    rows = [{k: short_id(v.get("value", "")) for k, v in b.items()} for b in data["results"]["bindings"]]
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    return rows


def short_id(value):
    """ "Q123" from an entity address, else the value as it is."""
    m = re.match(r"^https?://www\.wikidata\.org/entity/([QP]\d+)$", value or "")
    return m.group(1) if m else value


def entities(ids, cache=None, props="claims|labels"):
    """{id: entity} of Wikidata items, 50 at a time from the Wikibase API (English labels only)."""
    import build_textbooks as B
    out, ids = {}, [i for i in dict.fromkeys(ids) if re.match(r"^Q\d+$", i or "")]
    for start in range(0, len(ids), 50):
        chunk = ids[start:start + 50]
        url = WB_API + "?" + urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(chunk),
                                                     "props": props, "languages": "en", "format": "json"})
        path = _cached(cache, f"wb {datetime.date.today()} {url}")
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            _wait("wb", 1.0)
            try:
                data = json.loads(B.fetch(url))
            finally:
                _last["wb"] = time.monotonic()
            if "entities" not in data:
                raise ValueError(f"the Wikibase API answered without entities ({str(data)[:200]})")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
        out.update(data.get("entities", {}))
    return out


def labels(ids, cache=None):
    """{id: English label} of Wikidata items (the id itself when there is no English label)."""
    found = entities(ids, cache, props="labels")
    return {i: (found.get(i, {}).get("labels", {}).get("en", {}).get("value") or i) for i in ids}


def claim_values(entity, prop):
    """[(value, {qualifier: [values]})] of an entity's statements of prop (deprecated ones left out); a value is an
    item id ("Q5"), a time ("+1987-01-01T00:00:00Z" -> "1987") or a string."""
    out = []
    for st in entity.get("claims", {}).get(prop, []):
        if st.get("rank") == "deprecated":
            continue
        snak = st.get("mainsnak", {})
        value = _snak_value(snak)
        if value is None:
            continue
        quals = {}
        for q, snaks in (st.get("qualifiers") or {}).items():
            quals[q] = [v for v in (_snak_value(s) for s in snaks) if v is not None]
        out.append((value, quals))
    return out


def _snak_value(snak):
    """The plain value of one snak, or None (no value, unknown value)."""
    if snak.get("snaktype") != "value":
        return None
    dv = snak.get("datavalue", {})
    v = dv.get("value")
    if dv.get("type") == "wikibase-entityid":
        return v.get("id")
    if dv.get("type") == "time":
        return year_of(v.get("time", ""))
    if dv.get("type") == "quantity":
        return str(v.get("amount", "")).lstrip("+")
    return v if isinstance(v, str) else None


def year_of(value):
    """The year of a Wikidata time ("+1987-05-02T00:00:00Z" -> "1987"; "" when it has none)."""
    m = re.match(r"^[+]?(-?\d{1,4})-", str(value or ""))
    return str(int(m.group(1))) if m else ""


def date_of(value):
    """The date part of a time ("1987-05-02", or the year alone when the day is not known)."""
    m = re.match(r"^[+]?(\d{4})-(\d\d)-(\d\d)", str(value or ""))
    if not m:
        return year_of(value)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m.group(2) != "00" and m.group(3) != "00" else m.group(1)


def years_words(start, end):
    """ "1990 to 1995", "from 1990", "until 1995" or ""."""
    if start and end:
        return start if start == end else f"{start} to {end}"
    if start:
        return f"from {start}"
    return f"until {end}" if end else ""


# ====================================================================== teams and players


def teams_query(league):
    """The SPARQL query of a league's teams: items with a "league" (P118) statement naming it, with the years of that
    statement, the team's founding, folding, home venue, home city and head coach; people, seasons and team seasons
    are left out."""
    return """SELECT ?team ?teamLabel ?from ?to ?inception ?dissolved ?venueLabel ?placeLabel ?coachLabel ?sportLabel
WHERE {
  ?team p:P118 ?st . ?st ps:P118 wd:%s .
  FILTER NOT EXISTS { ?team wdt:P31 wd:Q5 }
  FILTER NOT EXISTS { ?team wdt:P5138 ?season }
  FILTER NOT EXISTS { ?team wdt:P3450 ?competition }
  OPTIONAL { ?st pq:P580 ?from } OPTIONAL { ?st pq:P582 ?to }
  OPTIONAL { ?team wdt:P571 ?inception } OPTIONAL { ?team wdt:P576 ?dissolved }
  OPTIONAL { ?team wdt:P115 ?venue } OPTIONAL { ?team wdt:P159 ?place }
  OPTIONAL { ?team wdt:P286 ?coach } OPTIONAL { ?team wdt:P641 ?sport }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}""" % league


def champions_query(league):
    """The SPARQL query of a league's seasons with a winner (P1346): the season items of the league (P3450)."""
    return """SELECT ?season ?seasonLabel ?winner ?winnerLabel ?time WHERE {
  ?season wdt:P3450 wd:%s ; wdt:P1346 ?winner .
  OPTIONAL { ?season wdt:P585 ?time } OPTIONAL { ?season wdt:P580 ?time }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}""" % league


def players_query(team_ids, most=PLAYERS_PER_LEAGUE):
    """The SPARQL query of the most notable players of some teams: people with a "member of sports team" (P54)
    statement naming one of them, ordered by their number of Wikipedia articles (sitelinks)."""
    values = " ".join(f"wd:{t}" for t in team_ids)
    return """SELECT DISTINCT ?p ?sl WHERE {
  VALUES ?team { %s }
  ?p wdt:P54 ?team ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?sl .
} ORDER BY DESC(?sl) LIMIT %d""" % (values, most)


def gather_teams(rows):
    """{team id: {name, years: [(from, to)], inception, dissolved, venues, places, coaches, sports}} from the rows of
    teams_query (one row per combination of the optional facts)."""
    teams = {}
    for r in rows:
        tid = r.get("team")
        if not re.match(r"^Q\d+$", tid or ""):
            continue
        t = teams.setdefault(tid, {"name": r.get("teamLabel") or tid, "years": set(), "inception": set(),
                                   "dissolved": set(), "venues": set(), "places": set(), "coaches": set(),
                                   "sports": set()})
        if r.get("from") or r.get("to"):
            t["years"].add((year_of(r.get("from")), year_of(r.get("to"))))
        for field, key in (("inception", "inception"), ("dissolved", "dissolved")):
            if r.get(key):
                t[field].add(year_of(r[key]))
        for field, key in (("venues", "venueLabel"), ("places", "placeLabel"), ("coaches", "coachLabel"),
                           ("sports", "sportLabel")):
            value = r.get(key)
            if value and not re.match(r"^Q\d+$", value):        # an item with no English label is left out
                t[field].add(value)
    return teams


def gather_champions(rows):
    """{team id: [season names]} and [(season name, winner name, year)] from the rows of champions_query."""
    by_team, seasons = {}, []
    for r in rows:
        season, winner = r.get("seasonLabel") or r.get("season"), r.get("winner")
        if not season or not winner:
            continue
        by_team.setdefault(winner, [])
        if season not in by_team[winner]:
            by_team[winner].append(season)
        seasons.append((season, r.get("winnerLabel") or winner, year_of(r.get("time"))))
    seasons = sorted(set(seasons), key=lambda s: (s[2] or "9999", s[0]))
    return by_team, seasons


def team_page_body(team, champions, players):
    """The HTML of one team's page: its facts as a list, its league titles and its notable players in this book."""
    import build_textbooks as B
    pairs = [("Sport", ", ".join(sorted(team["sports"]))),
             ("Founded", ", ".join(sorted(team["inception"]))),
             ("Folded", ", ".join(sorted(team["dissolved"]))),
             ("Years in this league", "; ".join(years_words(a, b) for a, b in sorted(team["years"]) if a or b)),
             ("Home venue", ", ".join(sorted(team["venues"]))),
             ("Home city or headquarters", ", ".join(sorted(team["places"]))),
             ("Head coach", ", ".join(sorted(team["coaches"])))]
    body = K.dl(pairs) or "<p>Wikidata gives no more facts about this team.</p>"
    if champions:
        body += "<h2>League titles Wikidata records</h2><ul>" + "".join(
            f"<li>{B.esc(s)}</li>" for s in sorted(champions)) + "</ul>"
    if players:
        body += "<h2>Notable players in this book</h2><ul>" + "".join(
            f'<li><a href="{B.esc(path)}">{B.esc(name)}</a></li>' for name, path in sorted(players)) + "</ul>"
    return body


def player_facts(entity, names):
    """The facts of one player (a Wikidata entity) that the book may show: {name, alive, born, died, positions,
    teams: [(team name, years)], awards: [(award name, year)], sports, countries}. For a living person (no date of
    death), no birth date or place is kept."""
    label = entity.get("labels", {}).get("en", {}).get("value") or entity.get("id", "")
    died = [v for v, _q in claim_values(entity, "P570")]
    facts = {"name": label, "alive": not died, "born": "", "died": ""}
    if died:
        facts["died"] = died[0]
        born = [v for v, _q in claim_values(entity, "P569")]
        facts["born"] = born[0] if born else ""
    name = lambda i: names.get(i, i)  # noqa: E731
    facts["positions"] = sorted({name(v) for v, _q in claim_values(entity, "P413") if not re.match(r"^Q\d+$",
                                                                                                    name(v))})
    teams = []
    for v, q in claim_values(entity, "P54"):
        if re.match(r"^Q\d+$", name(v)):
            continue
        start, end = (q.get("P580") or [""])[0], (q.get("P582") or [""])[0]
        teams.append((name(v), years_words(start, end), start or "9999"))
    facts["teams"] = [(t, y) for t, y, _s in sorted(teams, key=lambda x: (x[2], x[0]))]
    awards = []
    for v, q in claim_values(entity, "P166"):
        if re.match(r"^Q\d+$", name(v)):
            continue
        awards.append((name(v), (q.get("P585") or [""])[0]))
    facts["awards"] = sorted(set(awards), key=lambda a: (a[1] or "9999", a[0]))
    facts["sports"] = sorted({name(v) for v, _q in claim_values(entity, "P641") if not re.match(r"^Q\d+$", name(v))})
    facts["countries"] = sorted({name(v) for v, _q in claim_values(entity, "P1532")
                                 if not re.match(r"^Q\d+$", name(v))})
    return facts


def referenced_ids(entity):
    """The item ids a player's shown statements name (for their labels)."""
    ids = set()
    for prop in ("P413", "P54", "P166", "P641", "P1532"):
        ids |= {v for v, _q in claim_values(entity, prop) if re.match(r"^Q\d+$", str(v))}
    return ids


def player_page_body(facts, team_paths):
    """The HTML of one player's page (only the facts of player_facts)."""
    import build_textbooks as B
    pairs = [("Sport", ", ".join(facts["sports"])), ("Plays for the country of", ", ".join(facts["countries"])),
             ("Positions", ", ".join(facts["positions"]))]
    if not facts["alive"]:
        pairs += [("Born", facts["born"]), ("Died", facts["died"])]
    body = K.dl(pairs)
    if facts["teams"]:
        items = []
        for team, years in facts["teams"]:
            words = B.esc(team)
            if team in team_paths:
                words = f'<a href="{B.esc(team_paths[team])}">{words}</a>'
            items.append(f"<li>{words}" + (f" ({B.esc(years)})" if years else "") + "</li>")
        body += "<h2>Teams</h2><ul>" + "".join(items) + "</ul>"
    if facts["awards"]:
        body += "<h2>Awards and honours</h2><ul>" + "".join(
            f"<li>{B.esc(a)}" + (f" ({B.esc(y)})" if y else "") + "</li>" for a, y in facts["awards"]) + "</ul>"
    return body or "<p>Wikidata gives no more career facts for this player.</p>"


def about_page(title, what, read_day, sources_html, note=SPORTS_NOTE):
    """The first page of a data book: what it holds, where from and as of when (note: the source's own caution)."""
    import build_textbooks as B
    return (f"<p>{B.esc(what)}</p><p>As of {B.esc(read_day)}: the facts were read on that day.</p>"
            + (f"<p>{B.esc(note)}</p>" if note else "") + sources_html)


def team_book(name, work, cache=None, left_out=None, limit=None):
    """The book of one league (name "teams_<league>"): see the module docstring."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    league_name = name.split(":", 1)[0][len("teams_"):]
    row = LEAGUE_BY_NAME.get(league_name)
    if row is None:
        left_out.append({"title": name, "reason": "Unknown league."})
        return None
    _key, qid, must, title, sport, _word = row
    rows = wdqs(f'SELECT ?l WHERE {{ wd:{qid} rdfs:label ?l . FILTER(LANG(?l) = "en") }}', cache)
    found = rows[0].get("l", "") if rows else ""
    if not re.search(must, found):
        left_out.append({"title": title, "reason": f"Wikidata's item {qid} is now named {found!r}, not the league "
                                                   "this book is for; left out until the list is checked."})
        return None
    teams = gather_teams(wdqs(teams_query(qid), cache))
    if not teams:
        left_out.append({"title": title, "reason": "Wikidata lists no teams for this league."})
        return None
    by_team, seasons = gather_champions(wdqs(champions_query(qid), cache))
    player_ids = [r["p"] for r in wdqs(players_query(sorted(teams)), cache) if re.match(r"^Q\d+$", r.get("p", ""))]
    found_players = entities(player_ids, cache)
    names = labels(sorted({i for e in found_players.values() for i in referenced_ids(e)}), cache)
    today = datetime.date.today().isoformat()
    book = K.new_book(f"sport_teams_{league_name}", f"{title}: teams and notable players (Wikidata)",
                      f"Sports teams and players: {sport}", GROUP, "Wikidata contributors (www.wikidata.org)",
                      WIKIDATA_LICENCE, WIKIDATA_URL, f"{WD_ENTITY}{qid}",
                      f"The teams of the {title} with their facts and league titles, and its most notable players "
                      "with their positions, teams and awards, from Wikidata (CC0).",
                      f"Facts from Wikidata (CC0), as of {today}. {SPORTS_NOTE}", country="International",
                      changes="facts read from Wikidata and written out as pages", version=f"Wikidata as of {today}")
    team_paths = {t["name"]: f"team-{B.slug(t['name'], 50)}-{tid.lower()}" for tid, t in teams.items()}
    player_pages = []
    for pid in player_ids:
        entity = found_players.get(pid)
        if not entity:
            continue
        facts = player_facts(entity, names)
        player_pages.append((facts, f"player-{B.slug(facts['name'], 50)}-{pid.lower()}"))
    sources_html = ("<p>Source: Wikidata, the free knowledge base (CC0): the league's item "
                    f'<a href="{WD_ENTITY}{qid}">{qid}</a>, its teams\' "league" statements, its seasons\' winners, '
                    f"and the statements of the {len(player_pages)} players of its teams who have the most "
                    "Wikipedia articles (Wikidata's own measure of how widely known someone is). A team or player "
                    "with few statements on Wikidata has a short page.</p>")
    book.pages.append(B.Page("about", "About this book", about_page(title, book.description, today, sources_html)))
    if seasons:
        rows = [(s, w, y) for s, w, y in seasons]
        book.pages.append(B.Page("champions", "League titles (champions) Wikidata records",
                                 K.rows_table(rows, ("Season", "Winner", "Year")), 1, "Champions"))
    team_players = {}
    for facts, path in player_pages:
        for team, _years in facts["teams"]:
            if team in team_paths:
                team_players.setdefault(team, []).append((facts["name"], path))
    for tid, t in sorted(teams.items(), key=lambda kv: kv[1]["name"].lower()):
        book.pages.append(B.Page(team_paths[t["name"]], t["name"],
                                 team_page_body(t, by_team.get(tid, []), team_players.get(t["name"], [])), 2,
                                 "Teams"))
    for facts, path in sorted(player_pages, key=lambda fp: last_name(fp[0]["name"])):
        book.pages.append(B.Page(path, facts["name"], player_page_body(facts, team_paths), 3, "Notable players"))
    if limit:
        book.pages = book.pages[:limit]
    book.published = today
    return book


def last_name(name):
    """The sort key of a person's name: the last word first ("Babe Ruth" -> "ruth babe")."""
    words = (name or "").split()
    return " ".join([words[-1]] + words[:-1]).lower() if words else ""


def team_sign(name):
    """The weekly sign of a league book: the month (Wikidata changes every day, so the book is read again monthly)."""
    return datetime.date.today().strftime("%Y-%m")


# ====================================================================== the Olympic Games

OLYMPIC_KINDS = {"Q159821": "Summer Olympic Games", "Q82414": "Winter Olympic Games"}


def games_query():
    """The SPARQL query of the Summer and Winter Olympic Games with their dates, place, country and participants."""
    return """SELECT ?g ?gLabel ?kind ?start ?end ?time ?placeLabel ?countryLabel ?n WHERE {
  VALUES ?kind { wd:Q159821 wd:Q82414 }
  ?g wdt:P31 ?kind .
  OPTIONAL { ?g wdt:P580 ?start } OPTIONAL { ?g wdt:P582 ?end } OPTIONAL { ?g wdt:P585 ?time }
  OPTIONAL { ?g wdt:P276 ?place } OPTIONAL { ?g wdt:P17 ?country } OPTIONAL { ?g wdt:P1132 ?n }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""


def winners_query(kind):
    """The SPARQL query of the events of one kind of Games with a winner (P1346): event -> part of (P361) a sport at
    the Games -> part of the Games."""
    return """SELECT ?g ?event ?eventLabel ?winnerLabel WHERE {
  ?g wdt:P31 wd:%s .
  ?sportAt wdt:P361 ?g .
  ?event wdt:P361 ?sportAt ; wdt:P1346 ?winner .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}""" % kind


def gather_games(rows):
    """{games id: {name, kind, start, end, places, countries, participants}} from games_query rows."""
    games = {}
    for r in rows:
        gid = r.get("g")
        if not re.match(r"^Q\d+$", gid or ""):
            continue
        g = games.setdefault(gid, {"name": r.get("gLabel") or gid, "kind": OLYMPIC_KINDS.get(r.get("kind"), ""),
                                   "start": "", "end": "", "places": set(), "countries": set(), "participants": ""})
        g["start"] = g["start"] or date_of(r.get("start") or r.get("time"))
        g["end"] = g["end"] or date_of(r.get("end"))
        for field, key in (("places", "placeLabel"), ("countries", "countryLabel")):
            if r.get(key) and not re.match(r"^Q\d+$", r[key]):
                g[field].add(r[key])
        if r.get("n"):
            g["participants"] = g["participants"] or str(r["n"]).split(".")[0]
    return games


def olympics_book(name, work, cache=None, left_out=None, limit=None):
    """The Olympic Games book (see the module docstring): a page per Games, newest last."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    games = gather_games(wdqs(games_query(), cache))
    if not games:
        left_out.append({"title": "The Olympic Games", "reason": "Wikidata answered with no Games."})
        return None
    winners = {}
    for kind in OLYMPIC_KINDS:
        try:
            rows = wdqs(winners_query(kind), cache)
        except (urllib.error.URLError, OSError, ValueError) as e:
            left_out.append({"title": f"Event winners of the {OLYMPIC_KINDS[kind]}", "reason": f"Wikidata's "
                             f"query did not answer ({e}); the Games pages are built without them."})
            continue
        for r in rows:
            if r.get("eventLabel") and r.get("winnerLabel") and not re.match(r"^Q\d+$", r["winnerLabel"]):
                winners.setdefault(r.get("g"), set()).add((r["eventLabel"], r["winnerLabel"]))
    today = datetime.date.today().isoformat()
    book = K.new_book("sport_olympics", "The Olympic Games: hosts, dates and event winners (Wikidata)",
                      "Olympic Games", GROUP, "Wikidata contributors (www.wikidata.org)", WIKIDATA_LICENCE,
                      WIKIDATA_URL, f"{WD_ENTITY}Q5389",
                      "Every Summer and Winter Olympic Games on Wikidata: dates, host city and country, number of "
                      "participants, and the event winners Wikidata records.",
                      f"Facts from Wikidata (CC0), as of {today}. {SPORTS_NOTE}", country="International",
                      changes="facts read from Wikidata and written out as pages", version=f"Wikidata as of {today}")
    sources_html = ("<p>Source: Wikidata (CC0): the items that are \"instance of\" Summer Olympic Games (Q159821) or "
                    "Winter Olympic Games (Q82414), and the events whose \"winner\" (P1346) Wikidata records. Many "
                    "events have no winner recorded on Wikidata; a winner is named exactly as Wikidata names it "
                    "(a person, a team or a country). Medal tables are not given: olympics.com's results are "
                    "copyright.</p>")
    book.pages.append(B.Page("about", "About this book", about_page("Olympic Games", book.description, today,
                                                                    sources_html)))
    order = sorted(games.items(), key=lambda kv: (kv[1]["start"] or "9999", kv[1]["name"]))
    summary = [(g["name"], g["start"], ", ".join(sorted(g["places"])), ", ".join(sorted(g["countries"])))
               for _gid, g in order]
    book.pages.append(B.Page("all-games", "Every Games in order",
                             K.rows_table(summary, ("Games", "Opened", "Host city", "Country")), 1, "The Games"))
    for gid, g in order:
        body = K.dl([("Kind", g["kind"]), ("Opened", g["start"]), ("Closed", g["end"]),
                     ("Host city", ", ".join(sorted(g["places"]))), ("Country", ", ".join(sorted(g["countries"]))),
                     ("Participants", g["participants"])])
        rows = sorted(winners.get(gid, set()))
        if rows:
            body += f"<h2>Event winners Wikidata records ({len(rows)})</h2>" + K.rows_table(rows, ("Event", "Winner"))
        book.pages.append(B.Page(f"games-{B.slug(g['name'], 50)}-{gid.lower()}", g["name"], body, 2,
                                 g["kind"] or "The Games"))
    if limit:
        book.pages = book.pages[:limit]
    book.published = today
    return book


# ====================================================================== Retrosheet (baseball)

RETRO = "https://www.retrosheet.org"
RETRO_FILES = {"teamstats": RETRO + "/downloads/teamstats.zip", "batting": RETRO + "/downloads/batting.zip",
               "pitching": RETRO + "/downloads/pitching.zip", "allplayers": RETRO + "/downloads/allplayers.zip",
               "teams": RETRO + "/teams.zip"}
# The statement Retrosheet's terms (www.retrosheet.org/notice.txt) require to "appear prominently", word for word.
RETRO_NOTICE = ("The information used here was obtained free of charge from and is copyrighted by Retrosheet. "
                "Interested parties may contact Retrosheet at \"www.retrosheet.org\".")
RETRO_LICENCE = "Retrosheet terms (free use with its notice shown)"
RETRO_TERMS = RETRO + "/notice.txt"
RETRO_CAVEAT = ("Worked out here from Retrosheet's box scores of regular-season games. Retrosheet keeps adding and "
                "correcting games, and some early seasons are not complete, so these totals can differ from the "
                "official ones (forfeits, protested games and games Retrosheet does not yet have).")
CAREER_HITS = 1000
CAREER_WINS = 100
CAREER_SAVES = 100


def _int(value):
    """A whole number from a cell ("" and words count as 0)."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def zip_rows(path):
    """The rows (dicts) of the one CSV file in a zip, read a line at a time."""
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(name) as f:
            yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace", newline=""))


def retro_teams(rows):
    """[(code, league, city, nickname, first, last)] from Retrosheet's teams.csv rows."""
    return [(r.get("TEAM", ""), r.get("LEAGUE", ""), r.get("CITY", ""), r.get("NICKNAME", ""),
             _int(r.get("FIRST")), _int(r.get("LAST"))) for r in rows]


def team_name(teams, code, season):
    """(league, "City (CODE)") of a team code in a season, from retro_teams (the code itself when not found).
    Retrosheet's teams.csv gives each code only its latest nickname (Cleveland's code says "Guardians" for 1927
    too), so the city and code are used, never a nickname the team may not have had that season."""
    for c, league, city, _nick, first, last in teams:
        if c == code and first <= season <= last:
            return league or "Other", f"{city} ({code})" if city else code
    return "Other", code


def season_records(rows, teams):
    """{season: {league: {team name: [won, lost, tied, runs scored, runs allowed, games]}}} from Retrosheet's
    teamstats rows: only "value" rows of regular-season games (each team's row of each game counted once)."""
    out = {}
    for r in rows:
        if r.get("stattype") != "value" or r.get("gametype") != "regular":
            continue
        season = _int((r.get("date") or "")[:4])
        if not season:
            continue
        league, name = team_name(teams, r.get("team", ""), season)
        rec = out.setdefault(season, {}).setdefault(league, {}).setdefault(name, [0, 0, 0, 0, 0, 0])
        rec[0] += _int(r.get("win"))
        rec[1] += _int(r.get("loss"))
        rec[2] += _int(r.get("tie"))
        rec[3] += _int(r.get("b_r"))
        rec[4] += _int(r.get("p_r"))
        rec[5] += 1
    return out


def pct(won, lost):
    """The winning percentage as baseball writes it (".625"), or "" with no decisions."""
    if won + lost == 0:
        return ""
    value = won / (won + lost)
    return f"{value:.3f}".lstrip("0") if value < 1 else "1.000"


LEAGUE_NAMES = {"AL": "American League", "NL": "National League", "FL": "Federal League", "PL": "Players' League",
                "AA": "American Association", "UA": "Union Association", "NA": "National Association",
                "NNL": "Negro National League", "NAL": "Negro American League", "ECL": "Eastern Colored League",
                "ANL": "American Negro League", "EWL": "East-West League", "NSL": "Negro Southern League"}


def league_words(code):
    """A league's name from its Retrosheet code ("AL" -> "American League"; "ECL;ANL" -> both names; "Other" for
    teams Retrosheet gives no league)."""
    if code == "Other":
        return "Other teams (no league given)"
    return " / ".join(LEAGUE_NAMES.get(c, c) for c in code.split(";"))


def season_page_body(leagues):
    """One season's page: a table per league, the best record first."""
    import build_textbooks as B
    body = ""
    for league in sorted(leagues, key=lambda lg: (lg == "Other", league_words(lg))):
        teams = leagues[league]
        rows = sorted(teams.items(), key=lambda kv: (-(kv[1][0] / max(1, kv[1][0] + kv[1][1])), -kv[1][0], kv[0]))
        table = [(name, w, lo, t, pct(w, lo), rs, ra, g) for name, (w, lo, t, rs, ra, g) in rows]
        body += f"<h2>{B.esc(league_words(league))}</h2>" + K.rows_table(
            table, ("Team", "Won", "Lost", "Tied", "Pct.", "Runs scored", "Runs allowed", "Games"))
    return body


def career_totals(batting_rows, pitching_rows):
    """({player id: batting totals}, {player id: pitching totals}) from Retrosheet's batting and pitching rows ("value"
    rows of regular-season games). Batting: g, ab, r, h, 2b, 3b, hr, rbi, bb, k, sb; pitching: g, gs, w, l, sv,
    outs, h, er, bb, k."""
    bat, pit = {}, {}
    for r in batting_rows:
        if r.get("stattype") != "value" or r.get("gametype") != "regular":
            continue
        t = bat.setdefault(r.get("id", ""), {k: 0 for k in ("g", "ab", "r", "h", "2b", "3b", "hr", "rbi", "bb", "k",
                                                            "sb")})
        t["g"] += 1
        for k, col in (("ab", "b_ab"), ("r", "b_r"), ("h", "b_h"), ("2b", "b_d"), ("3b", "b_t"), ("hr", "b_hr"),
                       ("rbi", "b_rbi"), ("bb", "b_w"), ("k", "b_k"), ("sb", "b_sb")):
            t[k] += _int(r.get(col))
    for r in pitching_rows:
        if r.get("stattype") != "value" or r.get("gametype") != "regular":
            continue
        t = pit.setdefault(r.get("id", ""), {k: 0 for k in ("g", "gs", "w", "l", "sv", "outs", "h", "er", "bb", "k")})
        t["g"] += 1
        for k, col in (("gs", "p_gs"), ("w", "wp"), ("l", "lp"), ("sv", "save"), ("outs", "p_ipouts"), ("h", "p_h"),
                       ("er", "p_er"), ("bb", "p_w"), ("k", "p_k")):
            t[k] += _int(r.get(col))
    return bat, pit


def innings(outs):
    """Innings pitched as baseball writes them (outs 1000 -> "333.1")."""
    return f"{outs // 3}.{outs % 3}"


def era(er, outs):
    """Earned run average (earned runs per nine innings), or "" with no innings."""
    return f"{er * 27 / outs:.2f}" if outs else ""


def avg(h, ab):
    """Batting average (".312"), or "" with no at bats."""
    return (f"{h / ab:.3f}".lstrip("0") if h < ab else "1.000") if ab else ""


def player_names(rows):
    """{player id: "First Last"} from Retrosheet's allplayers rows (each player's first row)."""
    names = {}
    for r in rows:
        pid = r.get("id", "")
        if pid and pid not in names:
            names[pid] = " ".join(w for w in (r.get("first", ""), r.get("last", "")) if w)
    return names


def retro_book(kind, cache, left_out):
    """A new Retrosheet book with its notice ("seasons" or "careers")."""
    today = datetime.date.today().isoformat()
    what = {"seasons": ("sport_stats_retrosheet_seasons", "Baseball season records, every season Retrosheet has "
                        "(worked out from Retrosheet's box scores)", "Every regular season's team records by league: "
                        "won, lost, tied, winning percentage, runs scored and allowed, worked out from Retrosheet's "
                        "box scores."),
            "careers": ("sport_stats_retrosheet_careers", "Baseball career totals and leaders (worked out from "
                        "Retrosheet's box scores)", f"Career batting totals of the players with at least "
                        f"{CAREER_HITS} hits and pitching totals of the pitchers with at least {CAREER_WINS} wins or "
                        f"{CAREER_SAVES} saves, and the career leaders, worked out from Retrosheet's box scores.")}
    name, title, description = what[kind]
    return K.new_book(name, title, "Baseball statistics", GROUP, "Retrosheet (www.retrosheet.org)", RETRO_LICENCE,
                      RETRO_TERMS, RETRO + "/downloads/csvdownloads.html", description,
                      f"{RETRO_NOTICE} {RETRO_CAVEAT}", changes="totals and tables worked out from Retrosheet's "
                      "files", version=f"Retrosheet files read {today}")


def retro_ready(cache, left_out, title):
    """True when Retrosheet's downloads may be read (robots.txt and AI rules), else the reason in left_out."""
    if not K.readable(RETRO_FILES["teamstats"], cache):
        left_out.append({"title": title, "reason": "www.retrosheet.org's robots.txt or AI rules do not allow the "
                         "downloads to be read now."})
        return False
    return True


def retro_notice_html():
    """Retrosheet's statement, shown prominently at the top of a page."""
    import build_textbooks as B
    return f"<p><strong>{B.esc(RETRO_NOTICE)}</strong></p>"


def retro_seasons_book(name, work, cache=None, left_out=None, limit=None):
    """The season records book (see the module docstring)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    book = retro_book("seasons", cache, left_out)
    if not retro_ready(cache, left_out, book.title):
        return None
    teams = retro_teams(zip_rows(K.download_file(RETRO_FILES["teams"], cache, "retrosheet-teams.zip", 7)))
    records = season_records(zip_rows(K.download_file(RETRO_FILES["teamstats"], cache, "retrosheet-teamstats.zip",
                                                      7)), teams)
    if not records:
        left_out.append({"title": book.title, "reason": "Retrosheet's team statistics file had no regular-season "
                         "rows."})
        return None
    first, last = min(records), max(records)
    book.pages.append(B.Page("about", "About this book", retro_notice_html() + about_page(
        book.title, book.description, datetime.date.today().isoformat(),
        f"<p>Seasons {first} to {last}, as Retrosheet's files have them. {B.esc(RETRO_CAVEAT)} The latest season "
        "may still be in progress or not yet complete in Retrosheet's files. Teams are named by their city and "
        "Retrosheet's team code.</p>", note="")))
    for season in sorted(records):
        if limit and len(book.pages) >= limit:
            break
        book.pages.append(B.Page(f"season-{season}", f"The {season} season", retro_notice_html() +
                                 season_page_body(records[season]), 1, f"{season // 10 * 10}s"))
    book.published = datetime.date.today().isoformat()
    return book


def leader_rows(totals, names, field, most=50, key=None):
    """The most players by one total: [(rank, name, value)]."""
    order = sorted(totals.items(), key=lambda kv: (-(key(kv[1]) if key else kv[1][field]), names.get(kv[0], kv[0])))
    return [(i + 1, names.get(pid, pid), (key(t) if key else t[field])) for i, (pid, t) in enumerate(order[:most])]


def retro_careers_book(name, work, cache=None, left_out=None, limit=None):
    """The career totals book (see the module docstring)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    book = retro_book("careers", cache, left_out)
    if not retro_ready(cache, left_out, book.title):
        return None
    names = player_names(zip_rows(K.download_file(RETRO_FILES["allplayers"], cache, "retrosheet-allplayers.zip", 7)))
    bat, pit = career_totals(zip_rows(K.download_file(RETRO_FILES["batting"], cache, "retrosheet-batting.zip", 7)),
                             zip_rows(K.download_file(RETRO_FILES["pitching"], cache, "retrosheet-pitching.zip", 7)))
    hitters = {p: t for p, t in bat.items() if t["h"] >= CAREER_HITS}
    pitchers = {p: t for p, t in pit.items() if t["w"] >= CAREER_WINS or t["sv"] >= CAREER_SAVES}
    if not hitters and not pitchers:
        left_out.append({"title": book.title, "reason": "No player reached the totals in Retrosheet's files."})
        return None
    book.pages.append(B.Page("about", "About this book", retro_notice_html() + about_page(
        book.title, book.description, datetime.date.today().isoformat(), f"<p>{B.esc(RETRO_CAVEAT)}</p>", note="")))
    boards = [("Hits", "h", None), ("Home runs", "hr", None), ("Runs batted in", "rbi", None), ("Runs", "r", None),
              ("Stolen bases", "sb", None)]
    body = retro_notice_html()
    for title, field, key in boards:
        body += f"<h2>{title}</h2>" + K.rows_table(leader_rows(bat, names, field, 50, key), ("Rank", "Player", title))
    book.pages.append(B.Page("batting-leaders", "Career batting leaders", body, 1, "Leaders"))
    body = retro_notice_html()
    for title, field, key in (("Wins", "w", None), ("Strikeouts", "k", None), ("Saves", "sv", None),
                              ("Innings pitched", "outs", None)):
        rows = leader_rows(pit, names, field, 50, key)
        if field == "outs":
            rows = [(rank, who, innings(v)) for rank, who, v in rows]
        body += f"<h2>{title}</h2>" + K.rows_table(rows, ("Rank", "Player", title))
    book.pages.append(B.Page("pitching-leaders", "Career pitching leaders", body, 1, "Leaders"))
    for kind, group, head in (("batting", hitters, ("Player", "Games", "At bats", "Runs", "Hits", "Doubles",
                                                    "Triples", "Home runs", "RBI", "Walks", "Strikeouts",
                                                    "Stolen bases", "Average")),
                              ("pitching", pitchers, ("Pitcher", "Games", "Starts", "Won", "Lost", "Saves",
                                                      "Innings", "Hits", "Earned runs", "Walks", "Strikeouts",
                                                      "ERA"))):
        letters = {}
        for pid, t in group.items():
            who = names.get(pid, pid)
            letters.setdefault((last_name(who)[:1] or "?").upper(), []).append((who, t))
        for letter in sorted(letters):
            rows = []
            for who, t in sorted(letters[letter], key=lambda wt: last_name(wt[0])):
                if kind == "batting":
                    rows.append((who, t["g"], t["ab"], t["r"], t["h"], t["2b"], t["3b"], t["hr"], t["rbi"], t["bb"],
                                 t["k"], t["sb"], avg(t["h"], t["ab"])))
                else:
                    rows.append((who, t["g"], t["gs"], t["w"], t["l"], t["sv"], innings(t["outs"]), t["h"], t["er"],
                                 t["bb"], t["k"], era(t["er"], t["outs"])))
            book.pages.append(B.Page(f"{kind}-{letter.lower()}", f"Career {kind}: last names {letter}",
                                     retro_notice_html() + K.rows_table(rows, head), 2 if kind == "batting" else 3,
                                     f"Career {kind}"))
    if limit:
        book.pages = book.pages[:limit]
    book.published = datetime.date.today().isoformat()
    return book


def retro_sign(name):
    """The weekly sign of a Retrosheet book: the Last-Modified dates of its files."""
    files = ("teams", "teamstats") if name == "stats_retrosheet_seasons" else ("allplayers", "batting", "pitching")
    return K.sha([K.last_modified(RETRO_FILES[f]) for f in files])


# ====================================================================== openfootball (football / soccer)

OPENFOOTBALL = "https://raw.githubusercontent.com/openfootball/football.json/master"
OPENFOOTBALL_SITE = "https://github.com/openfootball/football.json"
FIRST_SEASON = 2010
# (book name, file code, title, calendar-year seasons)
FOOTBALL_LEAGUES = [("en1", "en.1", "English Premier League", False), ("de1", "de.1", "German Bundesliga", False),
                    ("es1", "es.1", "Spanish La Liga (Primera División)", False),
                    ("it1", "it.1", "Italian Serie A", False), ("fr1", "fr.1", "French Ligue 1", False),
                    ("mls", "mls", "Major League Soccer", True)]
FOOTBALL_BY_NAME = {row[0]: row for row in FOOTBALL_LEAGUES}
TABLE_CAVEAT = ("Worked out here from the match results in openfootball's data: 3 points for a win, 1 for a draw, "
                "ordered by points, then goal difference, then goals scored. Points deductions, awarded matches and "
                "the league's other decisions are not in the data, so a few tables can differ from the official "
                "ones; a season still being played is not finished.")


def season_names(calendar, today=None):
    """The season folder names to look for, oldest first: "2010-11" ... or "2010" ... up to this year's."""
    year = (today or datetime.date.today()).year
    if calendar:
        return [str(y) for y in range(FIRST_SEASON, year + 1)]
    return [f"{y}-{str(y + 1)[2:]}" for y in range(FIRST_SEASON, year + 1)]


def league_table(matches):
    """[(team, played, won, drawn, lost, goals for, goals against, goal difference, points)] from openfootball matches
    (each {"team1", "team2", "score": {"ft": [a, b]}}); matches without a full-time score are left out."""
    table = {}
    for m in matches:
        if not isinstance(m, dict):
            continue
        score = m.get("score") or {}
        ft = score.get("ft") if isinstance(score, dict) else score     # a few files give the score as [a, b]
        t1, t2 = m.get("team1"), m.get("team2")
        if not (t1 and t2 and isinstance(ft, list) and len(ft) == 2 and all(isinstance(x, int) for x in ft)):
            continue
        for team, gf, ga in ((t1, ft[0], ft[1]), (t2, ft[1], ft[0])):
            row = table.setdefault(team, [0, 0, 0, 0, 0, 0])
            row[0] += 1
            row[1 if gf > ga else 2 if gf == ga else 3] += 1
            row[4] += gf
            row[5] += ga
    rows = [(team, p, w, d, lo, gf, ga, gf - ga, 3 * w + d) for team, (p, w, d, lo, gf, ga) in table.items()]
    return sorted(rows, key=lambda r: (-r[8], -r[7], -r[5], r[0]))


def football_book(name, work, cache=None, left_out=None, limit=None):
    """The book of one league (name "stats_football_<code>"): a page per season and a page of champions."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    row = FOOTBALL_BY_NAME.get(name[len("stats_football_"):])
    if row is None:
        left_out.append({"title": name, "reason": "Unknown league."})
        return None
    code_name, code, title, calendar = row
    today = datetime.date.today().isoformat()
    book = K.new_book(f"sport_stats_football_{code_name}", f"{title}: season tables (openfootball)",
                      "Football (soccer) statistics", GROUP, "openfootball contributors (github.com/openfootball)",
                      WIKIDATA_LICENCE, WIKIDATA_URL, OPENFOOTBALL_SITE,
                      f"Every {title} season in openfootball's data since {FIRST_SEASON}: the final table worked "
                      "out from the match results, and the champions.",
                      f"From openfootball's football.json (CC0 1.0, public domain dedication), as of {today}. "
                      f"{TABLE_CAVEAT}", country="International",
                      changes="tables worked out from the match results", version=f"football.json read {today}")
    seasons, champions = [], []
    for season in season_names(calendar):
        url = f"{OPENFOOTBALL}/{season}/{code}.json"
        try:
            data = json.loads(B.fetch(url, cache))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
        table = league_table(data.get("matches") or [])
        if table:
            seasons.append((season, data.get("name") or f"{title} {season}", table, url))
    if not seasons:
        left_out.append({"title": book.title, "reason": "openfootball has no season of this league."})
        return None
    book.pages.append(B.Page("about", "About this book", about_page(
        title, book.description, today, f"<p>Source: openfootball's football.json "
        f'(<a href="{OPENFOOTBALL_SITE}">{OPENFOOTBALL_SITE}</a>), CC0. {B.esc(TABLE_CAVEAT)}</p>', note="")))
    for season, season_title, table, url in seasons:
        champions.append((season, table[0][0], table[0][8]))
    book.pages.append(B.Page("champions", "Top of the table, season by season",
                             K.rows_table(champions, ("Season", "Top of the table", "Points")), 1, "Champions"))
    head = ("Position", "Team", "Played", "Won", "Drawn", "Lost", "Goals for", "Goals against", "Goal difference",
            "Points")
    for season, season_title, table, url in seasons:
        if limit and len(book.pages) >= limit:
            break
        rows = [(i + 1,) + r for i, r in enumerate(table)]
        book.originals.append({"url": url, "kind": "json"})
        book.pages.append(B.Page(f"season-{season}", season_title, K.rows_table(rows, head), 2, "Seasons"))
    book.published = today
    return book


def football_sign(name):
    """The weekly sign of a league book: the week (the current season changes every matchday)."""
    return datetime.date.today().strftime("%G-W%V")


# ====================================================================== the makers sports.py lists

MAKERS = {f"teams_{row[0]}": (team_book, team_sign) for row in LEAGUES}
MAKERS["olympics"] = (olympics_book, team_sign)
MAKERS["stats_retrosheet_seasons"] = (retro_seasons_book, retro_sign)
MAKERS["stats_retrosheet_careers"] = (retro_careers_book, retro_sign)
MAKERS.update({f"stats_football_{row[0]}": (football_book, football_sign) for row in FOOTBALL_LEAGUES})
