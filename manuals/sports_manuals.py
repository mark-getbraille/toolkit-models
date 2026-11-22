"""The collection "Sports equipment (manuals)" (category key sports_equipment), under its own heading "Sports" (the
owner's request of 2026-11-22: sports as a top-level section). categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (basketball hoops and goals,
            pitching and ball machines, batting cages, table tennis tables, soccer and hockey goals, rebounders,
            trampolines, skates, skateboards, ski boots, snowboard bindings, sports helmets, golf carts and push
            carts, golf rangefinders and GPS units, scoreboards, shot clocks, radar guns and punching bags); no word
            another collection already searches (fitness trackers, treadmills and rowing machines are
            fitness_equipment's; bicycles bicycles'; ski bindings, cycling computers and snowshoes outdoors');
  makers    the big sports equipment makers, LINK-ONLY by the owner's rule: their own manuals, fitting guides and
            recall pages are for the person (or the personal assistant) to open in a browser or fetch with Program
            Downloader; nothing is read from their sites (their terms keep all rights);
  guidance  the reference library's sports books (textbooks/sports.py: the guide, the rule books) and the CDC's HEADS
            UP concussion pages (built in full: firstaid:cdc_seizures_concussion), the CPSC's recall search and
            NOCSAE's helmet standards, as links. No open coaching or officiating guide was found under an open licence
            (the NFHS, US Soccer, USA Hockey and Special Olympics coaching guides are copyright): links only.

The notice is said first (NOTICE): assembly and anchoring of hoops and goals (tip-over deaths), trampoline rules,
helmet fit and certification, concussion (CDC HEADS UP), and 911.
"""

HEADING = "Sports"

NOTICE = ("Read the safety section first. Assemble and anchor basketball hoops, soccer goals and other movable goals "
          "exactly as the manual says: a goal that tips over can kill; never let anyone climb or hang on one. "
          "Trampolines: one person at a time, with netting and padding, and an adult watching. A helmet protects only "
          "when it is certified for the sport, fits snugly and is replaced after a hard hit. After a blow to the "
          "head, stop playing and see a doctor (CDC HEADS UP). In an emergency call 911.")

IA_WORDS = ["basketball hoop", "basketball goal", "pitching machine", "tennis ball machine", "batting cage",
            "table tennis table", "ping pong table", "soccer goal", "hockey goal", "rebounder", "trampoline",
            "inline skate", "ice skate", "skateboard", "ski boot", "snowboard binding", "football helmet",
            "hockey helmet", "golf cart", "golf push cart", "golf rangefinder", "golf gps", "scoreboard", "shot clock",
            "radar gun", "punching bag"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="sports_equipment", prefix="sp", documents="manuals, fitting guides and instructions",
               access="link", reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="spalding", maker="Spalding", type="basketball hoops and balls", library="https://www.spalding.com/",
         site="spalding.com"),
    dict(key="lifetime-sports", maker="Lifetime Products", type="basketball hoops and portable goals",
         library="https://www.lifetime.com/", site="lifetime.com"),
    dict(key="goalrilla", maker="Goalrilla (Escalade Sports)", type="in-ground basketball hoops",
         library="https://www.goalrilla.com/", site="goalrilla.com"),
    dict(key="jugs", maker="JUGS Sports", type="pitching machines", library="https://jugssports.com/",
         site="jugssports.com"),
    dict(key="lobster", maker="Lobster Sports", type="tennis ball machines", library="https://www.lobstersports.com/",
         site="lobstersports.com"),
    dict(key="wilson-sporting", maker="Wilson Sporting Goods", type="balls, bats, gloves and rackets",
         library="https://www.wilson.com/", site="wilson.com"),
    dict(key="rawlings", maker="Rawlings", type="baseball gloves, bats and batting helmets",
         library="https://www.rawlings.com/", site="rawlings.com"),
    dict(key="riddell", maker="Riddell", type="football helmets and shoulder pads (fitting guides)",
         library="https://www.riddell.com/", site="riddell.com"),
    dict(key="schutt", maker="Schutt Sports", type="football and baseball helmets",
         library="https://schuttsports.com/", site="schuttsports.com"),
    dict(key="bauer", maker="Bauer Hockey", type="hockey skates, helmets and protective gear",
         library="https://www.bauer.com/", site="bauer.com"),
    dict(key="ccm", maker="CCM Hockey", type="hockey skates, helmets and protective gear",
         library="https://ccmhockey.com/", site="ccmhockey.com"),
    dict(key="callaway", maker="Callaway Golf", type="golf clubs and rangefinders",
         library="https://www.callawaygolf.com/", site="callawaygolf.com"),
    dict(key="bushnell-golf", maker="Bushnell Golf", type="golf rangefinders and GPS units",
         library="https://www.bushnellgolf.com/", site="bushnellgolf.com"),
    dict(key="clicgear", maker="Clicgear", type="golf push carts", library="https://www.clicgear.com/",
         site="clicgear.com"),
    dict(key="springfree", maker="Springfree Trampoline", type="trampolines",
         library="https://www.springfreetrampoline.com/", site="springfreetrampoline.com"),
    dict(key="stiga", maker="STIGA", type="table tennis tables", library="https://www.stigasports.com/",
         site="stigasports.com"),
    dict(key="everlast-boxing", maker="Everlast", type="punching bags and boxing gloves", library="https://www.everlast.com/",
         site="everlast.com"),
    dict(key="rossignol", maker="Rossignol", type="skis, ski boots and snowboards",
         library="https://www.rossignol.com/", site="rossignol.com"),
    dict(key="burton", maker="Burton", type="snowboards and bindings", library="https://www.burton.com/",
         site="burton.com"),
    dict(key="rollerblade", maker="Rollerblade", type="inline skates", library="https://www.rollerblade.com/",
         site="rollerblade.com"),
]]

GUIDANCE = [
    dict(title="Sports: a guide to the library (in the reference library: sport:index, request word sports-rules)",
         url="https://github.com/mark-getbraille/toolkit-models", by="the toolkit"),
    dict(title=("HEADS UP: concussion signs, symptoms and returning to play (CDC; in the reference library: "
                "firstaid:cdc_seizures_concussion)"), url="https://www.cdc.gov/heads-up/",
         by="the Centers for Disease Control and Prevention"),
    dict(title="Recalls of sports equipment (CPSC recall search)", url="https://www.cpsc.gov/Recalls",
         by="the US Consumer Product Safety Commission"),
    dict(title="Movable soccer goal safety (CPSC)",
         url="https://www.cpsc.gov/Safety-Education/Safety-Guides/Sports-Fitness-and-Recreation",
         by="the US Consumer Product Safety Commission"),
    dict(title="Helmet standards for football, baseball, lacrosse and more (NOCSAE; copyright, open it in a browser)",
         url="https://nocsae.org/", by="the National Operating Committee on Standards for Athletic Equipment"),
    dict(title="Fitness equipment and activity trackers (manual collection fitness_equipment)",
         url="https://odphp.health.gov/moveyourway", by="the toolkit (the collection's own guidance)"),
]

CATEGORY = dict(
    name="Sports equipment (manuals)",
    description=("Basketball hoops and goals, pitching and ball machines, batting cages, table tennis tables, soccer "
                 "and hockey goals, trampolines, skates, skateboards, ski boots, snowboard bindings, sports helmets, "
                 "golf carts, rangefinders and GPS units, scoreboards, radar guns and punching bags: the Internet "
                 "Archive's manuals, the makers' manual pages (links) and the safety guidance. Links only."),
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE, heading=HEADING)
