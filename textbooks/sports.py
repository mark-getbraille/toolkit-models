"""Sports for the reference library, in its own group "Reference, sports" (the owner's request of 2026-11-22: a new
top-level section). Keys: sport:<name>. Request words (each well under 256 jobs; sources.expand_keys):
  sports-rules         the rules of the sports: old official rule books in the US public domain, and the index
  sports-teams         every league book of teams and notable players (Wikidata), and the Olympic Games
  sports-teams-<sport> one sport's league books: football (American), basketball, baseball, hockey, soccer, cricket,
                       rugby, lacrosse
  sports-stats         statistics: baseball season records and career totals (Retrosheet), football (soccer) season
                       tables (openfootball), the old Spalding baseball record and athletic almanac
  sports               all of them

What this module builds, in plain words:
  - sport:index, a guide to sports in the library (the toolkit's own facts and links, CC0): one part per sport (the
    rules, the history books, the teams and statistics books, the picture packs and the manuals), blind and adaptive
    sports (goalball, beep baseball, blind football, showdown, tandem cycling, para sports), sports safety and
    concussion, and the official rule books of today's leagues and federations as LINKS ONLY (they are copyright);
  - IN FULL, old official rule books and guides in the US public domain (published before 1931; the builder checks
    each Internet Archive item's year at every build): James Naismith's first printed basketball rules (1892) and his
    and Luther Gulick's Basket Ball (1894), Spalding's guides of the Athletic Library (baseball 1919, collegiate
    basketball 1906, "soccer" football 1916, rugby 1910, cricket 1906, field hockey 1922, golf 1915, lawn tennis 1922,
    the athletic almanac 1914 and the 1911 baseball record), the NCAA football guide (1919) and lacrosse guide
    (1922), the AAU's athletic rules (1911), the official rules for ice hockey, speed skating, figure skating and
    curling (1921), ice hockey and ice polo (1898), volley ball and lawn games (1903), indoor baseball, the game that
    became softball (1891 and 1897), the official women's basketball rules (1906), the US War Department's Rules for
    Boxing (Commission on Training Camp Activities, 1918, a US government work), wrestling (1912 and 1925), jiu-jitsu
    (1913 and 1923), the bicycle guide (1897), and two books of the rules of many sports (1886 and 1896). Every
    description says plainly that the rules are history: today's official rules are different;
  - the data books of sports_data.py: a book per league of teams and notable players and the Olympic Games
    (Wikidata, CC0), baseball season records and career totals (Retrosheet, with its notice), and football (soccer)
    season tables (openfootball, CC0).
Every book carries SPORTS_SAFETY (concussion: stop playing and see a doctor, CDC HEADS UP; heat; protective gear; old
rule books are history).

Already in the library and not repeated (linked from the index): the CDC's HEADS UP concussion pages
(firstaid:cdc_seizures_concussion), the physical activity guidelines (fit:), Snow and Ice Sports (1923,
bush:jessup_snow_ice_sports_1923), the outdoors books (outdoors:), games (games:), blind and low-vision living (vision:)
and the Stack Exchange reading guide (se:index, with Physical Fitness).

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): today's official rule books (NFL, NBA, MLB,
NHL, NCAA, the IFAB Laws of the Game, World Athletics, the ITF, the USGA and R&A, World Rugby, the ICC, FIBA, FIVB,
FINA/World Aquatics, UWW, FIA, NASCAR, the USABA's and IBSA's blind sports rules), the Lahman Baseball Database (CC
BY-SA 3.0, but no download a program may read), Sports-Reference and the leagues' own statistics (copyright),
Wikibooks' sports books (already whole in the Kiwix library), Wikipedia's articles (in Kiwix) and olympics.com.

Run from the repository's folder:
  python3 textbooks/sports.py sport:naismith_basket_ball_1894 --out build/textbooks --limit 3
  python3 textbooks/sports.py --list sports-teams
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sports_data as SD  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = SD.GROUP                        # "sports"
GROUPS = {GROUP: "Reference, sports"}

SPORTS_SAFETY = ("Sports safety: after a blow to the head, stop playing and see a doctor; with a concussion, do not "
                 "go back to play until a doctor says it is safe (CDC HEADS UP). Drink water and rest in the shade in "
                 "hot weather. Wear the protective gear the sport's current rules require, fitted properly. General "
                 "information, not medical advice; in an emergency call 911.")
RULES_NOTE = ("Published in {year}: an old rule book kept as history. The rules, equipment and safety advice of "
              "{year} are not today's: check the current official rules of your league or federation before you "
              "play or coach.")
OLD_STATS_NOTE = ("Published in {year}: an old book of records and statistics kept as history; the records have "
                  "been broken and some figures corrected since.")
USGOV_NOTE = ("A US government work (Commission on Training Camp Activities, War Department and Navy Department, "
              "Government Printing Office, 1918), public domain. " + RULES_NOTE)


def rules(name, title, subject, publisher, archive, year, description, note=RULES_NOTE, country="United States"):
    """One old public-domain rule book or guide of the Internet Archive, with the safety notice."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=SPORTS_SAFETY, country=country)


SPALDING = "American Sports Publishing Company (Spalding's Athletic Library), New York"

RULE_PDFS = [
    # basketball
    rules("naismith_rules_for_basket_ball_1892", "Rules for Basket Ball (James Naismith, 1892)", "Basketball rules",
          "James Naismith (Triangle Publishing Company, Springfield, Massachusetts)", "cihm_27780", 1892,
          "One of the first printed copies of the rules of basketball, by the game's inventor, James Naismith, from "
          "a copy held by a Canadian library (Canadiana microfilm): the thirteen original rules, the court, the "
          "ball and the goals."),
    rules("naismith_basket_ball_1894", "Basket Ball (James Naismith and Luther Halsey Gulick, 1894)",
          "Basketball rules", f"James Naismith and Luther Halsey Gulick ({SPALDING})", "basketball00nais", 1894,
          "The early rules of basketball as Naismith and Gulick set them out for the YMCA, with notes on how to "
          "play the positions."),
    rules("spalding_collegiate_basket_ball_1906", "Spalding's Official Collegiate Basket Ball Guide (1906)",
          "Basketball rules", SPALDING, "spaldingsofficia01fish", 1906,
          "The official rules of college basketball for the 1906-07 season, with the record of the season, the "
          "teams and their pictures (described only by their captions)."),
    rules("womens_basket_ball_rules_1906", "Official Women's Basket Ball Rules (adopted 1899; 1906 edition)",
          "Basketball rules (women's game)", SPALDING, "officialwomensba00newy", 1906,
          "The rules of the women's game of basketball as adopted in June 1899 (the court divided into zones, "
          "players kept to their zone), in the 1906 edition.",
          note=RULES_NOTE + " Its ideas of what women may do in sport are those of its day."),
    # baseball and softball
    rules("spalding_base_ball_guide_1919", "Spalding's Official Base Ball Guide (1919)", "Baseball rules and records",
          SPALDING, "spaldingsbasebal19191chic", 1919,
          "The official guide of major league baseball for 1919: the playing rules, the records and averages of the "
          "1918 season, the leagues and the World Series.",
          note=RULES_NOTE + " Professional baseball was segregated then: the Negro leagues are not in it."),
    rules("hancock_indoor_base_ball_1891", "Hancock's Indoor Base Ball Guide (George W. Hancock, 1891)",
          "Indoor baseball (the start of softball)", "George W. Hancock (Chicago)", "hancocksindoorba00hanc", 1891,
          "The rules of indoor baseball by its inventor, George Hancock of Chicago (1887): the game played indoors "
          "with a large soft ball and a small bat that grew into softball."),
    rules("indoor_base_ball_rules_1897", "Constitution, By-laws and Playing Rules of the Association of Indoor Base "
          "Ball Clubs (1897)", "Indoor baseball (the start of softball)", "Association of Indoor Base Ball Clubs "
          "(Chicago)", "constitutionbyla01asso", 1897,
          "The playing rules of indoor baseball as its clubs' association set them in 1897."),
    # American football
    rules("ncaa_football_guide_1919", "The Official National Collegiate Athletic Association Football Guide (1919)",
          "American football rules", SPALDING, "officialnational09nationa", 1919,
          "The official rules book of college football for 1919, with the rules committee's notes, the records of "
          "the 1918 season and the teams.",
          note=RULES_NOTE + " The helmets and safety rules of 1919 gave little protection; today's rules on "
                            "tackling and helmets were made to prevent head and neck injuries."),
    # soccer, rugby, cricket, field hockey, lacrosse
    rules("spalding_soccer_guide_1916", "Spalding's Official \"Soccer\" Football Guide (1916-17)",
          "Association football (soccer) rules", SPALDING, "spaldingsofficia01coch", 1916,
          "The laws of association football (soccer) as played in the United States in 1916, with the records of "
          "the leagues and the national challenge cup."),
    rules("spalding_rugby_guide_1910", "Spalding's Official Rugby Foot Ball Guide (1910)", "Rugby rules", SPALDING,
          "spaldingsofficialru00", 1910,
          "The laws of rugby union football as played in the United States and Canada in 1910."),
    rules("spalding_cricket_guide_1906", "Spalding's Official Cricket Guide (1906)", "Cricket rules and records",
          SPALDING, "spaldingsofficia01flann", 1906,
          "The laws of cricket and the American cricket season of 1905, with its clubs and averages."),
    rules("spalding_field_hockey_guide_1922", "Spalding's Field Hockey Guide (United States Field Hockey "
          "Association, 1922)", "Field hockey rules", SPALDING, "spaldingsfieldho00unit", 1922,
          "The official rules of field hockey for women's and girls' play in the United States in 1922, published "
          "for the United States Field Hockey Association and the American Physical Education Association."),
    rules("ncaa_lacrosse_guide_1922", "The Official National Collegiate Athletic Association Lacrosse Guide "
          "(1922-23)", "Lacrosse rules", SPALDING, "officialnational16nationa", 1922,
          "The official rules of college lacrosse for 1922-23, with the season's records. Lacrosse comes from the "
          "games of the Haudenosaunee and other Native nations; this book tells it from the colleges' side.",
          note=RULES_NOTE + " Some of its words about lacrosse's Native origins are those of its day."),
    # golf, tennis
    rules("spalding_golf_guide_1915", "Spalding's Official Golf Guide (1915)", "Golf rules and records", SPALDING,
          "spaldingsofficia07unit", 1915,
          "The rules of golf as approved by the United States Golf Association in 1915, with the amateur and open "
          "championships of the year."),
    rules("spalding_lawn_tennis_annual_1922", "Spalding's Lawn Tennis Annual (1922)", "Tennis rules and records",
          SPALDING, "spaldingslawnten1922unse", 1922,
          "The laws of lawn tennis as adopted by the United States Lawn Tennis Association, with the 1921 season's "
          "championships and rankings."),
    # track and field
    rules("aau_athletic_rules_1911", "Official Athletic Rules and Official Handbook of the Amateur Athletic Union "
          "(1911)", "Track and field rules", SPALDING, "officialathletic03amate", 1911,
          "The Amateur Athletic Union's rules of track and field and other amateur sports in 1911: running, "
          "hurdling, jumping, throwing, walking, swimming, boxing and wrestling, and the rules of amateur status."),
    # winter sports
    rules("ice_hockey_skating_curling_rules_1921", "Official Rules for Ice Hockey, Speed Skating, Figure Skating and "
          "Curling (1921)", "Ice hockey and skating rules", SPALDING, "officialrulesfor07newy", 1921,
          "The official rules of amateur ice hockey, speed skating, figure skating and curling in the United States "
          "in 1921.",
          note=RULES_NOTE + " Ice safety: never go on natural ice unless it is known to be thick enough."),
    rules("tuthill_ice_hockey_ice_polo_1898", "Ice Hockey and Ice Polo Guide (J. A. Tuthill, 1898)",
          "Ice hockey rules", f"J. A. Tuthill ({SPALDING})", "icehockeyicepolo00tuth", 1898,
          "Ice hockey as played in 1898, with its rules and those of ice polo, an American game on skates."),
    # volleyball and lawn games
    rules("games_lawn_hockey_volley_ball_1903", "The Games of Lawn Hockey, Tether Ball, Golf-Croquet, Hand Tennis, "
          "Volley Ball and Others (1903)", "Volleyball and lawn games rules", SPALDING, "gamesoflawnhocke01newy",
          1903,
          "The rules of several games of 1903, among them volley ball (invented by William G. Morgan in 1895), lawn "
          "hockey, tether ball, golf-croquet, hand tennis and hand polo."),
    # combat sports
    rules("us_rules_for_boxing_1918", "Rules for Boxing (Commission on Training Camp Activities, 1918)",
          "Boxing rules", "Commission on Training Camp Activities (War and Navy Departments; Government Printing "
          "Office)", "rulesforboxing00unit", 1918,
          "The rules of boxing for the US Army and Navy training camps of the First World War: the ring, the "
          "gloves, rounds, fouls and the referee's duties.", note=USGOV_NOTE),
    rules("hitchcock_wrestling_catch_as_catch_can_1912", "Wrestling: Catch-as-Catch-Can Style (Edward Hitchcock Jr. "
          "and Richard F. Nelligan, 1912)", "Wrestling", f"Edward Hitchcock Jr. and Richard F. Nelligan ({SPALDING})",
          "wrestlingcatchas00hitc", 1912,
          "Holds, breaks and counters of catch-as-catch-can wrestling (the style amateur freestyle wrestling grew "
          "from), with the rules, by Amherst College's athletic instructors.",
          note=RULES_NOTE + " Practise holds only with a trained coach and a partner who agrees, on proper mats."),
    rules("gallagher_amateur_wrestling_1925", "Amateur Wrestling (Edward Clark Gallagher, 1925)", "Wrestling",
          "Edward Clark Gallagher (Co-operative Publishing Company)", "AmateurWrestling", 1925,
          "Holds, trips, locks and counters as taught by Edward C. Gallagher, the wrestling coach of Oklahoma A and "
          "M College.",
          note=RULES_NOTE + " Practise holds only with a trained coach and a partner who agrees, on proper mats."),
    rules("higashi_spalding_jiu_jitsu_1913", "Spalding's Jiu Jitsu (Katsuguma Higashi, 1913)", "Martial arts",
          f"Katsuguma Higashi ({SPALDING})", "spaldings-jiu-jitsu", 1913,
          "The Japanese art of jiu-jitsu explained by Katsuguma Higashi, with the falls, holds and throws, and the "
          "poses described only by their captions.",
          note=RULES_NOTE + " Learn throws, locks and chokes only from a qualified instructor: they can injure."),
    rules("liederman_science_of_wrestling_jiu_jitsu_1923", "The Science of Wrestling and the Art of Jiu-Jitsu (Earle "
          "E. Liederman, 1923)", "Wrestling and martial arts", "Earle E. Liederman (New York)",
          "scienceofwrestli00lied", 1923,
          "Wrestling holds and the art of jiu-jitsu, with training and conditioning, by a physical culture "
          "teacher of the 1920s.",
          note=RULES_NOTE + " Learn throws, locks and chokes only from a qualified instructor: they can injure."),
    # cycling
    rules("spalding_bicycle_guide_1897", "Spalding's Official Bicycle Guide (1897)", "Cycling", SPALDING,
          "spaldingsofficia01nels", 1897,
          "Cycling in the bicycle craze of the 1890s: the racing rules of the League of American Wheelmen, records, "
          "training and riding.",
          note=RULES_NOTE + " Wear a helmet, which riders of 1897 did not have."),
    # many sports
    rules("benedict_hand_book_sporting_rules_1886", "Spalding's Hand Book of Sporting Rules and Training (George H. "
          "Benedict, 1886)", "Rules of many sports", "George H. Benedict (A. G. Spalding and Brothers)",
          "spaldingshandboo00bene", 1886,
          "The codes of rules of the popular sports of 1886 (athletics, boxing, wrestling, rowing, cycling, swimming, "
          "lacrosse, polo and many others) and how athletes trained."),
    rules("outdoor_sports_pastimes_1896", "Outdoor Sports and Pastimes: Correct Rules (1896)",
          "Rules of many sports", "Union Publishing", "outdoorsportspas00unio_0", 1896,
          "The rules of the outdoor games of 1896: athletics, base ball, bicycling, cricket, croquet, curling, foot "
          "ball, golf, lacrosse, lawn tennis, polo and others."),
    rules("morgan_girls_and_athletics_1917", "Girls and Athletics (Mary C. Morgan, editor, 1917)",
          "Rules of many sports (girls' and women's sports)", f"Mary C. Morgan, editor ({SPALDING})",
          "girlsathleticsgi00morg", 1917,
          "A summary of the sports played by girls and women in 1917 (basket ball, field hockey, volley ball, "
          "indoor baseball, swimming, track and field and others), with their rules and how to organise them.",
          note=RULES_NOTE + " Its ideas of what girls and women should play are those of its day."),
]

STATS_PDFS = [
    rules("spalding_base_ball_record_1911", "Spalding's Official Base Ball Record (1911)", "Baseball statistics",
          SPALDING, "spaldingsofficia06", 1911,
          "The records and averages of the major and minor leagues of 1910: batting, fielding and pitching averages "
          "of every player, the standings and the World Series.", note=OLD_STATS_NOTE),
    rules("spalding_athletic_almanac_1914", "Spalding's Official Athletic Almanac (1914)", "Track and field records",
          SPALDING, "spaldingsofficia00sull", 1914,
          "The records of track and field and other amateur sports up to 1914: world, American and college records, "
          "the 1913 championships, and the Olympic Games of 1912 in Stockholm.", note=OLD_STATS_NOTE),
]

# ====================================================================== the index

SECTIONS = [
    ("How this collection is arranged", "The rules of each sport (old official rule books, which are history, and "
     "links to today's official rules), teams and players (Wikidata), statistics, pictures and manuals.", [
        ("word", "sports-rules", "The rule books and this guide"),
        ("word", "sports-teams", "Every league book of teams and notable players, and the Olympic Games"),
        ("word", "sports-stats", "Baseball and football (soccer) statistics"),
        ("pack", "commons_sports_equipment", "Balls, bats, rackets, sticks and pucks, for the picture describer"),
        ("pack", "commons_sports_venues", "Fields, courts, rinks, tracks and stadiums"),
        ("manuals", "sports_equipment", "Sports equipment makers' manuals, as links")]),
    ("Football (American)", "Rules, history, teams and statistics.", [
        ("key", "sport:ncaa_football_guide_1919", "The NCAA's official football rules of 1919 (history)"),
        ("key", "sport:teams_nfl", "NFL teams and notable players"),
        ("link", "NFL Rulebook", "https://operations.nfl.com/the-rules/nfl-rulebook/", "copyright of the NFL"),
        ("link", "NCAA football rules", "https://www.ncaa.org/sports/2013/11/5/playing-rules-administration.aspx",
         "copyright of the NCAA"),
        ("link", "Pro Football Reference", "https://www.pro-football-reference.com/",
         "statistics; copyright of Sports Reference")]),
    ("Soccer (association football)", "The laws of the game, leagues and tables.", [
        ("key", "sport:spalding_soccer_guide_1916", "The laws of soccer as played in 1916 (history)"),
        ("key", "sport:stats_football_en1", "Premier League season tables"),
        ("key", "sport:stats_football_mls", "Major League Soccer season tables"),
        ("key", "sport:teams_premier_league", "Premier League clubs and notable players"),
        ("key", "sport:teams_mls", "MLS clubs and notable players"),
        ("link", "IFAB Laws of the Game", "https://www.theifab.com/laws-of-the-game-documents/",
         "free to read and download, but the IFAB's terms forbid copying or republishing them; fetch it for "
         "personal use")]),
    ("Basketball", "From Naismith's first rules to today's leagues.", [
        ("key", "sport:naismith_rules_for_basket_ball_1892", "Naismith's first printed rules (1892)"),
        ("key", "sport:naismith_basket_ball_1894", "Basket Ball (Naismith and Gulick, 1894)"),
        ("key", "sport:teams_nba", "NBA teams and notable players"),
        ("key", "sport:teams_wnba", "WNBA teams and notable players"),
        ("link", "NBA Official Rules", "https://official.nba.com/", "copyright of the NBA"),
        ("link", "FIBA Official Basketball Rules", "https://www.fiba.basketball/documents", "copyright of FIBA")]),
    ("Baseball and softball", "Rules, history, teams and statistics.", [
        ("key", "sport:spalding_base_ball_guide_1919", "Spalding's Official Base Ball Guide (1919)"),
        ("key", "sport:hancock_indoor_base_ball_1891", "Indoor baseball, the start of softball (1891)"),
        ("key", "sport:teams_mlb", "MLB teams and notable players"),
        ("key", "sport:stats_retrosheet_seasons", "Every season's team records (Retrosheet)"),
        ("key", "sport:stats_retrosheet_careers", "Career totals and leaders (Retrosheet)"),
        ("link", "Official Baseball Rules (MLB)", "https://www.mlb.com/official-information/umpires/official-rules",
         "copyright of Major League Baseball"),
        ("link", "Lahman Baseball Database (SABR)", "https://sabr.org/lahman-database/",
         "CC BY-SA 3.0, but its downloads sit behind a file host whose robots.txt keeps programs out; download it "
         "in a browser"),
        ("link", "USA Softball rules", "https://www.usasoftball.com/", "copyright of USA Softball")]),
    ("Ice hockey and winter sports", "Rules, history and teams.", [
        ("key", "sport:ice_hockey_skating_curling_rules_1921", "Ice hockey, skating and curling rules (1921)"),
        ("key", "sport:tuthill_ice_hockey_ice_polo_1898", "Ice hockey and ice polo (1898)"),
        ("key", "sport:teams_nhl", "NHL teams and notable players"),
        ("key", "bush:jessup_snow_ice_sports_1923", "Snow and Ice Sports (1923): skis, skating, hockey, curling"),
        ("link", "NHL Rulebook", "https://www.nhl.com/info/official-rules", "copyright of the NHL"),
        ("link", "FIS rules (skiing and snowboarding)", "https://www.fis-ski.com/en/inside-fis/document-library",
         "copyright of the International Ski and Snowboard Federation")]),
    ("Tennis, golf, volleyball and racket sports", "Rules and history.", [
        ("key", "sport:spalding_lawn_tennis_annual_1922", "Lawn tennis laws and records (1922)"),
        ("key", "sport:spalding_golf_guide_1915", "The rules of golf (1915)"),
        ("key", "sport:games_lawn_hockey_volley_ball_1903", "Volley ball and lawn games (1903)"),
        ("link", "ITF Rules of Tennis", "https://www.itftennis.com/en/about-us/governance/rules-and-regulations/",
         "copyright of the International Tennis Federation"),
        ("link", "Rules of Golf (USGA and R&A)", "https://www.usga.org/rules.html", "copyright of the USGA and R&A"),
        ("link", "FIVB volleyball rules", "https://www.fivb.com/", "copyright of the FIVB")]),
    ("Track and field, swimming and cycling", "Rules, records and history.", [
        ("key", "sport:aau_athletic_rules_1911", "The AAU's athletic rules (1911)"),
        ("key", "sport:spalding_athletic_almanac_1914", "Athletic records to 1914, with the 1912 Olympics"),
        ("key", "sport:spalding_bicycle_guide_1897", "Cycling rules and records (1897)"),
        ("key", "sport:olympics", "The Olympic Games (Wikidata)"),
        ("link", "World Athletics Book of Rules", "https://worldathletics.org/about-iaaf/documents/book-of-rules",
         "copyright of World Athletics"),
        ("link", "World Aquatics rules", "https://www.worldaquatics.com/rules", "copyright of World Aquatics")]),
    ("Wrestling, boxing and martial arts", "Rules and history; learn holds only from a qualified coach.", [
        ("key", "sport:us_rules_for_boxing_1918", "Rules for Boxing (US government, 1918)"),
        ("key", "sport:hitchcock_wrestling_catch_as_catch_can_1912", "Catch-as-catch-can wrestling (1912)"),
        ("key", "sport:higashi_spalding_jiu_jitsu_1913", "Jiu-jitsu (1913)"),
        ("link", "United World Wrestling rules", "https://uww.org/governance", "copyright of United World Wrestling")]),
    ("Cricket, rugby, lacrosse and field hockey", "Rules, teams and history.", [
        ("key", "sport:spalding_cricket_guide_1906", "The laws of cricket (1906)"),
        ("key", "sport:spalding_rugby_guide_1910", "The laws of rugby (1910)"),
        ("key", "sport:ncaa_lacrosse_guide_1922", "College lacrosse rules (1922)"),
        ("key", "sport:spalding_field_hockey_guide_1922", "Field hockey rules (1922)"),
        ("key", "sport:teams_ipl", "Indian Premier League teams and notable players"),
        ("key", "sport:teams_super_rugby", "Super Rugby teams and notable players"),
        ("link", "MCC Laws of Cricket", "https://www.lords.org/mcc/the-laws-of-cricket", "copyright of the MCC"),
        ("link", "World Rugby laws", "https://www.world.rugby/the-game/laws/home", "copyright of World Rugby")]),
    ("Motorsports", "No old rule book in the public domain was found; links only.", [
        ("link", "FIA regulations (Formula One and other series)", "https://www.fia.com/regulation/category/110",
         "copyright of the FIA"),
        ("link", "NASCAR rules", "https://www.nascar.com/", "copyright of NASCAR")]),
    ("Blind and adaptive sports", "Goalball, beep baseball, blind football, showdown, tandem cycling and the para "
     "sports. Their rule books belong to their federations: links only.", [
        ("pack", "commons_adaptive_sports", "Guide running, blind cricket, torball, sitting volleyball, boccia, "
                                            "para-cycling and Nordic walking"),
        ("pack", "commons_disability", "Goalball, blind football and wheelchair sports"),
        ("pack", "open_images_sports", "Para table tennis, para-alpine skiing and sledge hockey photos"),
        ("key", "vision:index", "Blind and low-vision living: the guide"),
        ("link", "US Association of Blind Athletes (goalball, beep kickball, judo, tandem cycling)",
         "https://www.usaba.org/", "copyright, and its robots.txt shuts out AI companies' readers"),
        ("link", "International Blind Sports Federation (IBSA) rules: goalball, blind football, judo, showdown",
         "https://ibsasport.org/", "copyright of IBSA"),
        ("link", "National Beep Baseball Association rules", "https://www.nbba.org/", "copyright of the NBBA"),
        ("link", "International Paralympic Committee", "https://www.paralympic.org/", "copyright of the IPC")]),
    ("Sports safety, fitness and more", "Concussion, exercise and where else to look.", [
        ("key", "firstaid:cdc_seizures_concussion", "Concussion signs and HEADS UP (CDC)"),
        ("key", "fit:physical_activity_guidelines", "Physical Activity Guidelines for Americans"),
        ("key", "fit:odphp_move_your_way", "Move Your Way"),
        ("word", "games-hobbies", "Board and card games (games, not sports)"),
        ("key", "se:index", "Stack Exchange reading guide (with Physical Fitness; reading only)"),
        ("manuals", "fitness_equipment", "Fitness equipment and activity trackers, as links"),
        ("link", "Wikibooks sports books (Football (Soccer), Baseball, Tennis, Rugby Union, Cricket, Fencing, Table "
                 "Tennis, Badminton, Ultimate Frisbee, Coaching Youth Middle Distance Runners)",
         "https://en.wikibooks.org/wiki/Football_(Soccer)", "CC BY-SA, already whole in the Kiwix library "
                                                             "(wikibooks_en_all)")]),
]
INDEX = X.index_maker("sport", GROUP, "Sports: a guide to the library", "Sports",
                      "A guide to sports in the library: the rules of each sport, teams and players, statistics, "
                      "blind and adaptive sports, sports safety, the picture packs and the manuals, and today's "
                      "official rule books as links.", SECTIONS)
MAKERS = dict(SD.MAKERS, index=INDEX)


def _teams_words():
    """The request words of the league books: sports-teams (every league and the Olympics) and one per sport."""
    words = {"sports-teams": lambda: [f"sport:teams_{row[0]}" for row in SD.LEAGUES] + ["sport:olympics"]}
    for word in dict.fromkeys(row[5] for row in SD.LEAGUES):
        words[f"sports-teams-{word}"] = (lambda w=word: [f"sport:teams_{row[0]}" for row in SD.LEAGUES
                                                         if row[5] == w])
    return words


WORDS = {
    "sports-rules": lambda: ["sport:index"] + [f"sport:{p['name']}" for p in RULE_PDFS],
    "sports-stats": lambda: ["sport:stats_retrosheet_seasons", "sport:stats_retrosheet_careers"] +
                            [f"sport:stats_football_{row[0]}" for row in SD.FOOTBALL_LEAGUES] +
                            [f"sport:{p['name']}" for p in STATS_PDFS],
}
WORDS.update(_teams_words())
WORDS["sports"] = lambda: list(dict.fromkeys(k for w in ("sports-rules", "sports-teams", "sports-stats")
                                             for k in WORDS[w]()))

COLLECTION = K.Collection("sport", GROUP, pdfs=RULE_PDFS + STATS_PDFS, makers=MAKERS, words=WORDS)

# Retrosheet's terms as a licence the builder may repackage ("open": free use, its notice shown on every page).
ALLOWED = {SD.RETRO_LICENCE: "open"}

LICENCE_LINES = {
    "sport_old_books": ("Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, "
                        "so a later reprint is refused); archive.org's robots.txt allows the files; no AI rules "
                        "(checked 2026-11-22). Rules for Boxing (1918) is also a US government work (Government "
                        "Printing Office)."),
    "sport_wikidata": ("Wikidata: all structured data CC0 1.0 (www.wikidata.org/wiki/Wikidata:Licensing). Asked "
                       "through the Query Service (query.wikidata.org/sparql), Wikimedia's documented interface for "
                       "programs, and the Wikibase API (wbgetentities); their robots.txt lines keep web crawlers away "
                       "from /sparql and /w/, and they are used as the repository's picture collections use them: one "
                       "request at a time with the User-Agent Wikimedia's policy asks for, waiting when told 429 "
                       "(checked 2026-11-22)."),
    "sport_retrosheet": ("www.retrosheet.org/notice.txt (checked 2026-11-22): \"Recipients of Retrosheet data are "
                         "free to make any desired use of the information, including (but not limited to) selling "
                         "it, giving it away, or producing a commercial product based upon the data. Retrosheet has "
                         "one requirement ... the following statement must appear prominently\" (shown on every "
                         "page). robots.txt disallows only /boxesetc/ and /gamelogs/; the CSV downloads are read."),
    "sport_openfootball": "github.com/openfootball/football.json LICENSE.md: CC0 1.0 Universal (checked 2026-11-22); "
                          "read from raw.githubusercontent.com.",
    "sport_index": "The index (sport:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("Today's official league rule books: NFL Rulebook, NBA Official Rules, MLB Official Baseball Rules, NHL "
     "Rulebook, NCAA rule books, NFHS rules", "Copyright of each league and association (no open licence, no free "
     "reproduction); link-only from the index (sport:index). The old public-domain rule books (before 1931) are "
     "built as history. Index: https://operations.nfl.com/the-rules/nfl-rulebook/"),
    ("IFAB Laws of the Game (association football)", "Free to download, but the IFAB's terms of service (December "
     "2022, checked 2026-11-22) say its content, \"including ... the Laws of the Game\", \"shall not be used, "
     "reproduced, copied, distributed ... republished\" beyond use on its own sites: not built; link-only for the "
     "owner's personal copy. Spalding's \"Soccer\" Football Guide (1916) is built as history. Index: "
     "https://www.theifab.com/laws-of-the-game-documents/"),
    ("World Athletics, ITF, USGA and R&A Rules of Golf, World Rugby, ICC and MCC Laws of Cricket, FIBA, FIVB, World "
     "Aquatics, United World Wrestling, FIS, FIA and NASCAR rules", "Copyright of each federation; link-only. Index: "
     "https://worldathletics.org/about-iaaf/documents/book-of-rules"),
    ("Blind and adaptive sports rules: USABA, IBSA (goalball, blind football, showdown, judo), the National Beep "
     "Baseball Association, the IPC", "Copyright, and www.usaba.org's robots.txt shuts out AI companies' readers "
     "(checked 2026-11-22); link-only (fitness_nutrition.py lists them too). Index: https://ibsasport.org/ and "
     "https://www.nbba.org/"),
    ("Lahman Baseball Database (SABR)", "CC BY-SA 3.0 (its readme, checked 2026-11-22), but its files are offered "
     "only through sabr.box.com, whose robots.txt disallows programs except the shared-link pages (which need a "
     "browser to download), and the old GitHub copy (chadwickbureau/baseballdatabank) is gone. Not built; Retrosheet "
     "(free use with its notice) gives the season and career books instead. Index: https://sabr.org/lahman-database/"),
    ("Retrosheet game logs and box score pages", "robots.txt disallows /gamelogs/ and /boxesetc/: not read; the CSV "
     "downloads (/downloads/) are. Index: https://www.retrosheet.org/game.htm"),
    ("Sports-Reference sites (Baseball, Pro Football, Basketball, Hockey, FBref) and the leagues' official statistics "
     "(NFL, NBA, NHL, MLB)", "Copyright (their terms forbid copying the data); link-only. Index: "
     "https://www.sports-reference.com/"),
    ("Wikibooks sports books (Football (Soccer), Baseball, Tennis, Rugby Union, Cricket, Fencing, Table Tennis, "
     "Badminton, Ultimate Frisbee, Coaching Youth Middle Distance Runners)", "CC BY-SA, already whole in the Kiwix "
     "library (wikibooks_en_all), which the toolkit reads; not repeated. Index: "
     "https://en.wikibooks.org/wiki/Football_(Soccer)"),
    ("Wikipedia's articles on teams and players", "Share-alike text, already whole in the Kiwix library; the league "
     "books use only Wikidata's CC0 facts. Index: https://en.wikipedia.org/wiki/Portal:Sports"),
    ("Olympic results and medal tables (olympics.com)", "Copyright of the IOC; the Olympic Games book uses Wikidata's "
     "CC0 facts. Index: https://www.olympics.com/en/olympic-games"),
    ("Spalding's Official Foot Ball Guide (1915) and Spalding's Winter Sports (1913)", "The Internet Archive's copies "
     "are Google scans with no text layer (Image Container PDF only, checked 2026-11-22); the NCAA football guide "
     "(1919) and Snow and Ice Sports (1923, bush:) are built instead. Index: "
     "https://archive.org/details/spaldingsoffici00campgoog"),
    ("Intercollegiate swimming rules (1915)", "The Internet Archive's copy is marked \"Confidential--not for "
     "publication\" (an advance copy); left out. The AAU's athletic rules (1911) and Girls and Athletics (1917) "
     "cover swimming. Index: https://archive.org/details/advancecopyofint00newy"),
    ("Motorsports rule books before 1931", "No public-domain copy with a text layer was found on the Internet Archive "
     "(searched 2026-11-22); link-only (FIA, NASCAR). Index: https://archive.org/search?query=automobile+racing+rules"),
    ("Sports Stack Exchange", "Not among the Stack Exchange reading-only books (stack_exchange.py lists Physical "
     "Fitness); reading only in any case. Index: https://download.kiwix.org/zim/stack_exchange/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
