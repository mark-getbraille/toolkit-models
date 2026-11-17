"""Unexploded ordnance, landmine, civilian firearm and children's-rite picture collections for the Picture Model
Training Kit whose licence keeps them out of the open packs. The open ones found in the same search (Wikimedia
Commons CC0, public domain and CC BY files of munition models, unexploded and loose munitions, demining and bomb
disposal, firearm and cartridge models, and children's rites; the AMLID drone landmine photos; Europeana's open-rights
rite photos) are ready-made packs: packs/safety_rites_packs.py.

The owner's rule: every collection found goes in under its licence category (open -> pack; share-alike,
non-commercial or research -> an entry here; sign-up -> listed below; owners who keep all rights -> the permission
list, as candidates for a permission letter). Nothing here is in a ready-made pack or re-shared by the kit's makers.
Each collection is downloaded by the kit on the user's own computer, straight from its makers, only when the user
ticks the matching choice. Groups (Source.group, as in sources.py, extra_sources.py and packs/SOURCE-RULES.md):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with
                   them is CC BY-SA.
  "noncommercial"  CC BY-NC and BY-NC-SA: the personal-use box (Alt+Q); the result is for personal use only.

The collections (SAFETY_RITES_SOURCES):
  share-alike
    commons_uxo_sa         Wikimedia Commons photos under CC BY-SA or GFDL of landmines, minefields, cluster
                           munitions, grenades, mortar and artillery ammunition, IEDs, loose ammunition,
                           demining and bomb disposal (UXO_CATEGORIES, as the open commons_uxo pack). The category's
                           plain sentence and the file's caption, each ending with SAFETY_LINE.
    commons_firearms_sa    Wikimedia Commons photos under CC BY-SA or GFDL of firearm and cartridge models found
                           through Wikidata (CC0: the kind, maker P176 and cartridge P739), as the open commons_firearms
                           and commons_cartridges packs: "This looks like a Glock 17, a semi-automatic pistol, made by
                           Glock, chambered in 9×19 mm Parabellum." Gun answers end with GUN_LINE.
    commons_child_rites_sa Wikimedia Commons photos under CC BY-SA or GFDL of baptisms, christenings, the brit milah
                           (setting only), first communions, confirmations, bar and bat mitzvahs and other children's
                           rites, through the same STRICT CHILD RULE as the open pack (child_rite_ok).
  noncommercial
    mineinsight            MineInsight (Malizia and others, Royal Military Academy of Belgium and KU Leuven; IEEE
                           Robotics and Automation Letters 2026; CC BY-NC-SA 4.0, github.com/mariomlz99/MineInsight):
                           a ground robot's colour camera along test tracks with 15 kinds of (inert) landmines among
                           everyday litter, with hand-checked boxes. "What is on the ground here?" -> "This looks
                           like a PFM-1 (also called the butterfly mine), a Soviet anti-personnel mine, and a TMA-2,
                           an anti-tank mine, among litter: a metal tuna can and a plastic water bottle." + SAFETY_LINE.
                           The mines' kinds and countries come from Wikidata (MINEINSIGHT_MINES, checked November 2026).
                           The frames are read one by one out of the 3.8 GB and 2.8 GB zips of tracks 1 and 2 (HTTP
                           ranges); only frames at least a second apart are used (about 340), so the robot's video is
                           not repeated.

SAFETY RULES (the same as packs/safety_rites_packs.py): no answer says how to disarm, handle, move, fire, load,
clean, change or buy anything; captions naming handling are not learnt; rows whose words name the dead or injured are
marked "content": "graphic" (except for guns and cartridges, where such files are left out); a dead or injured child,
sexual violence, torture and executions are always left out; rows naming a child carry "child": True. No collection
here may be used for picture-making (SAFETY_RITES_PICTURE_MAKING_OK is empty).

Needing sign-up (SAFETY_RITES_SIGN_UP), owners to ask for permission (SAFETY_RITES_PERMISSION: the mine-action
organisations, with their contacts), and looked at and not included (SAFETY_RITES_NOT_INCLUDED) are listed below.

    python kit/safety_rites_sources.py mineinsight --data <empty folder> --cap 8     (a quick check)
"""

import io
import json
import os
import random
import re
import time
import zipfile

import sources
from extra_sources import commons_get, commons_session
from events_safety_sources import commons_files, caption, marked, WIKIDATA_SPARQL
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS, remote_zip, zip_members
from sources import NARRATE, Source, clean

SAFETY_LINE = ("Do not touch it or go closer. Move back carefully the way you came, warn others, and report it to the "
               "police, military or a mine-action organisation.")
GUN_LINE = "Treat every gun as loaded, and keep your fingers away from the trigger."
ASK_WHAT = "What is this?"
ASK_HAPPENING = "What is happening in this picture?"
ASK_GROUND = "What is on the ground here?"
COMMONS_TERMS = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def full_stop(text):
    """The text ending with a full stop."""
    text = clean(text)
    return text if not text or text[-1] in ".!?" else text + "."


def with_line(answer, line):
    """An answer with its safety line after it."""
    return f"{full_stop(answer)} {line}" if line else full_stop(answer)


def a_or_an(phrase):
    """ "a" or "an" before a phrase ("an anti-tank mine", "a US", "an 8×57 mm", "a .38 Special")."""
    m = re.match(r"^(\d+)", phrase)
    if m:
        n = m.group(1)
        return "an" if n.startswith("8") or n in ("11", "18") else "a"
    if phrase.startswith(".") or re.match(r"^(U\.?S\b|Uni|Euro|one\b)", phrase):
        return "a"
    return "an" if phrase[:1].lower() in "aeiou" else "a"


# ----------------------------------------------------------------- Commons helpers (share-alike)

def subcats(s, category):
    """The names of a Commons category's subcategories ([] when it cannot be read)."""
    try:
        data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                               "cmtype": "subcat", "cmlimit": 500})
    except RuntimeError:
        return []
    return [m["title"].split(":", 1)[-1] for m in (data.get("query") or {}).get("categorymembers") or []]


def files_in(s, category, depth, avoid, most=300):
    """Up to most file titles of a Commons category and, for depth 1 or 2, of its subcategories (and theirs), names
    matching avoid left out."""
    def page(cat):
        """The first page of a category's files."""
        try:
            data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{cat}",
                                   "cmtype": "file", "cmlimit": 500})
        except RuntimeError:
            return []
        return [m["title"] for m in (data.get("query") or {}).get("categorymembers") or []]
    titles, level = page(category), [category]
    for _ in range(depth):
        below = [c for parent in level for c in subcats(s, parent) if not avoid.search(c)][:15]
        for sub in below:
            titles += page(sub)
        level = below
    return [t for t in dict.fromkeys(titles) if not avoid.search(t.split(":", 1)[-1])][:most]


def file_words(f):
    """A share-alike Commons file's own words: title, text and categories."""
    return " ".join([f["title"].split(":", 1)[-1].rsplit(".", 1)[0].replace("_", " "), f["text"],
                     " ".join(f["categories"])])


def take(s, prefix, titles, want, rows_of, rng, used):
    """[(file name, address, row)] for up to want copyleft files among titles (shuffled), rows from rows_of(f)."""
    titles = [t for t in titles if t not in used]
    rng.shuffle(titles)
    items, got = [], 0
    for start in range(0, len(titles), 40):
        if got >= want:
            break
        try:
            files = commons_files(s, titles[start:start + 40])
        except RuntimeError as e:                    # Commons kept refusing: keep what came
            say(f"  {str(e)[:100]}")
            time.sleep(120)
            break
        for f in files:
            rows = rows_of(f) if got < want else []
            if rows:
                used.add(f["title"])
                items += [(f"{prefix}-{f['pageid']}.jpg", f["url"], r) for r in rows]
                got += 1
    return items, got


# ----------------------------------------------------------------- share-alike: unexploded ordnance

# Captions naming handling are not learnt (as packs/safety_rites_packs.py HANDLING).
HANDLING = re.compile(r"\b(disarm\w*|defus\w*|render(ed|ing|s)? (it |them )?safe|dispos(e|ed|ing|al) of|detonat\w*|"
                      r"demolition|blow(n|ing|s)? up|controlled (explosion|burn|detonation)|(explosive|demolition) "
                      r"charges?|C-?4|pick(s|ed|ing)? up|carr(y|ies|ied|ying)|lift(s|ed|ing)?|(un)?load(s|ed|ing)?|"
                      r"fir(e|es|ed|ing)\b|throw(s|n|ing)?|threw|launch\w*|fuz(e|es|ed|ing)|remov\w*|dismantl\w*|"
                      r"disassembl\w*|handl(e|es|ed|ing)|mov(e|es|ed|ing)|transport\w*|stack(s|ed|ing)?|"
                      r"prob(e|es|ed|ing)|excavat\w*|dig(s|ging)?|dug|uncover\w*|procedures?|techniques?|training|"
                      r"exercise|drill|how to|instructions?|step[- ]by[- ]step)\b", re.I)
NOT_THE_DANGER = re.compile(r"\b(in art|art|advertis\w*|posters?|stamps?|logos?|icons?|badges?|insignia|drawings?|"
                            r"diagrams?|illustrations?|paintings?|vector|svg|maps?|videos?|cutaways?|sectioned|"
                            r"manuals?|factor(y|ies)|manufactur\w*|workers?|reload\w*|loading|hoisting|training|"
                            r"practice|exercises?|firing|launch\w*|toys?|scale models?|replicas?|memorials?|"
                            r"sculptures?|warning signs|nuclear|timers?|pipe bombs?|suicide vests?|bombings?|"
                            r"victims|robots?|vehicles?|machines?|unexploded ordnance|monuments?|pomnik|denkmal|statues?|charts?|"
                            r"graphs?|comparison|bullet drop|ballistics?|design week|expo)\b", re.I)
# A caption is learnt only when it is in English (no translation here): two or more common English words.
ENGLISH = re.compile(r"\b(the|of|and|with|in|at|on|a|an|is|from|during|for|by)\b", re.I)
# Pictures of munitions in use, not lying around: dropped from or loaded on aircraft, stored aboard ships, being
# fired. Left out of the munition packs (the answer's warning would not fit, and they teach nothing about finding one).
IN_USE = re.compile(r"\b(dropp\w*|in flight|bomb bays?|pylons?|wings? of|under the wing|aircraft|airplanes?|"
                    r"B-\d+\w*|bombers?|fighters?|jets?|helicopters?|inventor\w*|aboard|carriers?|loaded|loading|"
                    r"ordnancem[ae]n|aviation ordnance|weapons? (loaders?|load\w*)|being fired|firing|launch\w*|"
                    r"in action)\b", re.I)
# The same categories as the open commons_uxo pack: (question, answer, depth).
UXO_CATEGORIES = {
    "Landmines": (ASK_WHAT, "This looks like a landmine.", 0),
    "Anti-personnel landmines": (ASK_WHAT, "This looks like an anti-personnel landmine.", 1),
    "Anti-tank landmines": (ASK_WHAT, "This looks like an anti-tank landmine.", 1),
    "Landmines by country": (ASK_WHAT, "This looks like a landmine.", 1),
    "Minefields": (ASK_WHAT, "This looks like a minefield: an area where landmines have been laid.", 1),
    "Cluster bombs": (ASK_WHAT, "This looks like a cluster bomb or its bomblets.", 1),
    "Hand grenades": (ASK_WHAT, "This looks like a hand grenade.", 1),
    "Mortar ammunition": (ASK_WHAT, "This looks like a mortar bomb (a mortar shell).", 1),
    "Shells (artillery)": (ASK_WHAT, "This looks like an artillery shell.", 1),
    "Artillery ammunition": (ASK_WHAT, "This looks like artillery ammunition: shells for a large gun.", 0),
    "Improvised explosive devices": (ASK_WHAT, "This looks like an improvised explosive device (IED): a home-made "
                                               "bomb.", 0),
    "Ammunition": (ASK_WHAT, "This looks like ammunition.", 0),
    "Ammunition belts": (ASK_WHAT, "This looks like a belt of ammunition: cartridges linked together in a row.", 0),
    "Demining": (ASK_HAPPENING, "This shows demining: specialists clearing landmines from an area.", 1),
    "Explosive ordnance disposal": (ASK_HAPPENING, "This shows explosive ordnance disposal (bomb disposal) "
                                                   "specialists at work. Only trained specialists do this.", 0),
}


def prepare_commons_uxo_sa(source, data_dir, work, cap):
    """Commons photos of unexploded and loose munitions, minefields and demining under CC BY-SA or GFDL: the
    category's sentence and the caption (unless it names handling), each with SAFETY_LINE."""
    s, rng, used = commons_session(), random.Random(711), set()
    want = int((cap + source.test) * 1.2) + 2
    per = max(4, want // len(UXO_CATEGORIES) + 1)
    items, pictures = [], 0
    for category, (question, answer, depth) in UXO_CATEGORIES.items():
        def rows_of(f, question=question, answer=answer):
            """The rows of one file, marked as packs do; [] when its words must be left out."""
            if IN_USE.search(f"{f['title']} {f['text']}"):
                return []
            rows = [{"question": question, "answer": with_line(answer, SAFETY_LINE), "split": "",
                     "credit": f["credit"]}]
            text = caption(f["text"])
            if text and not HANDLING.search(text) and len(ENGLISH.findall(text)) >= 2:
                rows.append({"question": NARRATE, "answer": with_line(text, SAFETY_LINE), "split": "",
                             "credit": f["credit"]})
            return marked(rows, f["title"], " ".join(f["categories"]))
        got, n = take(s, "uxo-sa", files_in(s, category, depth, NOT_THE_DANGER), per, rows_of, rng, used)
        items += got
        pictures += n
    say(f"  Fetching {pictures} Commons munition and demining photos (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: firearms and cartridges

def sparql(s, query, tries=4):
    """The rows of a Wikidata query ([{name: value}], entity addresses cut to their Q-number); [] when it failed."""
    for attempt in range(tries):
        try:
            r = s.get(WIKIDATA_SPARQL, params={"query": query, "format": "json"}, timeout=120)
            if r.status_code == 200:
                return [{k: v["value"].rsplit("/entity/", 1)[-1] for k, v in b.items()}
                        for b in r.json()["results"]["bindings"]]
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(10 * (attempt + 1))
    return []


# (Wikidata class, how an answer says it, gun or cartridge), most specific first (as the open packs).
GUN_KINDS = [("Q6889079", "AR-15-style rifle (a semi-automatic rifle)", "gun"), ("Q486396", "shotgun", "gun"),
             ("Q3389302", "semi-automatic pistol", "gun"), ("Q170382", "revolver", "gun"), ("Q1907525", "pistol", "gun"),
             ("Q40280158", "bolt-action rifle", "gun"), ("Q2291248", "semi-automatic rifle", "gun"),
             ("Q183302", "carbine", "gun"), ("Q124072", "rifle", "gun"),
             ("Q1763371", "shotgun shell", "cartridge"), ("Q9150235", "revolver cartridge", "cartridge"),
             ("Q9150231", "pistol cartridge", "cartridge"), ("Q7333267", "rifle cartridge", "cartridge"),
             ("Q37144", "cartridge", "cartridge")]
GUN_ACTIONS = re.compile(r"\b(fir(e|es|ed|ing)\b|shoot\w*|shot (at|by|dead)|aim(s|ed|ing)?|range|target|"
                         r"load(s|ed|ing)?|unload\w*|reload\w*|handload\w*|clean(s|ed|ing)?|maintenance|"
                         r"disassembl\w*|field[- ]?strip\w*|parts?|modif\w*|convert\w*|conversion|build\w*|kits?|"
                         r"sale|shop|store|dealer|price|buy\w*|purchas\w*|auction|gunshot|murder\w*|crime|suicide|"
                         r"robbery|wounded|killed|dead|victims?|evidence|airsoft|replica|toys?|props?|blank[- ]firing|"
                         r"cap guns?|paintball|drawings?|diagrams?|patents?|advertis\w*|cutaways?|sectioned|"
                         r"x-?rays?|how to|instructions?)\b", re.I)
GUN_WORDS = re.compile(r"\b(AR-?15|AK-?\d+|M-?16|guns?|pistols?|revolvers?|rifles?|shotguns?|carbines?|firearms?|handguns?)\b", re.I)
AMMO_WORDS = re.compile(r"\b(cartridges?|rounds?|ammo|ammunition|bullets?|shells?|casings?|cases|brass)\b", re.I)


# Words in a model's name that do not pick it out ("Model", "Revolver"), for model_named.
GENERIC_NAME = {"model", "revolver", "revolvers", "pistol", "pistols", "rifle", "rifles", "carbine", "shotgun", "gun",
                "army", "navy", "pattern", "mark", "mine", "mines", "bomb", "bombs", "grenade", "grenades", "shell",
                "type", "the", "and", "of", "new", "pocket", "cartridge", "magnum", "special", "auto", "automatic",
                "semi", "mod", "mle", "no", "single", "action", "double"}


def model_named(label, text):
    """True when a file's own words (title and caption) name the model: one of the name's distinctive words ("Starr",
    "P7", "BLU-109", "Parabellum") or its first number, so a general picture filed in a model's category (a table of
    several guns) is not called that model."""
    words = [w for w in re.findall(r"[\w.-]+", label) if w.lower().strip(".-") not in GENERIC_NAME and len(w) >= 2]
    for w in words:
        if re.search(r"(?<![\w])" + re.escape(w.strip(".")) + r"(?![\w])", text, re.I):
            return True
    number = re.search(r"\d+", label)
    return bool(number) and bool(re.search(r"(?<!\d)" + number.group(0) + r"(?!\d)", text))


# Pictures whose focus is people (parades, soldiers, police, hunters, portraits), not the gun: left out.
PEOPLE_FOCUS = re.compile(r"\b(soldiers?|troops?|marines?|sailors?|airm[ae]n|parades?|march\w*|defile|ceremon\w*|"
                          r"officers?|police\w*|guards?|hunters?|hunting|portrait|man|men|woman|women|people|"
                          r"crowd|team|squad|upacara|gelar|reenact\w*|re-enact\w*)\b", re.I)

def gun_models(s, want):
    """[(item, Commons category, answer, "gun" or "cartridge", label)]: Wikidata firearm and cartridge models with a Commons
    category and a name (a capital letter or a digit), each under its first kind, with maker and cartridge."""
    seen, out = set(), []
    for qid, phrase, kind in GUN_KINDS:
        rows = sparql(s, f"""SELECT ?item ?cat ?label (SAMPLE(?ml) AS ?maker) (COUNT(DISTINCT ?m) AS ?makers)
            (GROUP_CONCAT(DISTINCT ?al; separator="|") AS ?ammo) WHERE {{ ?c wdt:P279* wd:{qid} .
            {{ ?item wdt:P279 ?c }} UNION {{ ?item wdt:P31 ?c }} ?item wdt:P373 ?cat .
            ?item rdfs:label ?label . FILTER(LANG(?label) = "en")
            OPTIONAL {{ ?item wdt:P176 ?m . ?m rdfs:label ?ml . FILTER(LANG(?ml) = "en") }}
            OPTIONAL {{ ?item wdt:P739 ?a . ?a rdfs:label ?al . FILTER(LANG(?al) = "en") }} }}
            GROUP BY ?item ?cat ?label""")
        for r in rows:
            label = clean(r.get("label"))
            if r["item"] in seen or not re.search(r"[A-Z0-9]", label) or label.startswith("Category:"):
                continue
            seen.add(r["item"])
            if kind == "cartridge":
                name = re.sub(r"(\d)mm\b", r"\1 mm", re.sub(r"^(\d+) gauge\b", r"\1-gauge", label))
                noun = phrase if phrase != "cartridge" else "cartridge"
                answer = f"This is {a_or_an(name)} {name} {noun}."
            else:
                kind_word = phrase.split(" (")[0].split()[-1]
                answer = f"This looks like {a_or_an(label)} {label}" + \
                    ("" if kind_word in label.lower() else f", {a_or_an(phrase)} {phrase}")
                maker = clean(r.get("maker"))
                if r.get("makers") == "1" and maker and maker.split()[0].lower() not in label.lower():
                    answer += f", made by {maker}"
                ammo = [a for a in (r.get("ammo") or "").split("|") if a]
                if len(ammo) == 1:
                    answer += f", chambered in {ammo[0]}"
                elif len(ammo) == 2:
                    answer += f", made for {ammo[0]} or {ammo[1]} cartridges"
                answer = with_line(answer, GUN_LINE)
            out.append((r["item"], r["cat"], answer, kind, label))
        time.sleep(1)
    random.Random(721).shuffle(out)
    return out


def prepare_commons_firearms_sa(source, data_dir, work, cap, per_item=3):
    """Commons photos of firearm and cartridge models under CC BY-SA or GFDL (see the module docstring)."""
    s, rng, used = commons_session(), random.Random(723), set()
    want = int((cap + source.test) * 1.2) + 2
    models = gun_models(s, want)
    say(f"  Wikidata: {len(models)} firearm and cartridge models with a Commons category")
    items, pictures = [], 0
    for item, category, answer, kind, label in models:
        if pictures >= want:
            break

        def rows_of(f, answer=answer, kind=kind, label=label):
            """The rows of one file; [] when its words name an action, harm, a child or the wrong thing, or do not
            name the model."""
            words = file_words(f)
            own = f"{f['title'].split(':', 1)[-1]} {f['text']}"
            if GUN_ACTIONS.search(words) or CHILD_WORDS.search(words) or PEOPLE_FOCUS.search(own) \
                    or not model_named(label, own):
                return []
            if (kind == "gun" and AMMO_WORDS.search(words) and not GUN_WORDS.search(words)) or \
                    (kind == "cartridge" and (GUN_WORDS.search(words) or not AMMO_WORDS.search(words))):
                return []
            rows = [{"question": ASK_WHAT, "answer": answer, "split": "", "credit": f["credit"]}]
            text = caption(f["text"])
            if text and not HANDLING.search(text):
                rows.append({"question": NARRATE, "answer": with_line(text, GUN_LINE if kind == "gun" else ""),
                             "split": "", "credit": f["credit"]})
            rows = marked(rows, f["title"], " ".join(f["categories"]))
            return [] if any(r.get("content") == "graphic" for r in rows) else rows
        got, n = take(s, f"firearm-sa-{item}", files_in(s, category, 0, re.compile(r"\b(svg|drawings?)\b", re.I)),
                      per_item, rows_of, rng, used)
        items += got
        pictures += n
    say(f"  Fetching {pictures} Commons firearm and cartridge photos (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: children's rites

# THE STRICT CHILD RULE, as packs/safety_rites_packs.py (keep the two in step).
NOT_FOR_RITES = re.compile(
    r"circumcis\w*|beschneid\w*|besnijd\w*|circonc\w*|circunci\w*|obrzez\w*|обрез\w*|s[üu]nnet\w*|sunat\w*|"
    r"khitan\w*|khatna|ختان|\b(cut|cuts|cutting|incision|wound\w*|blood\w*|bleed\w*|knife|knives|izmel|scalpel|"
    r"clamp\w*|plastibell|gomco|mogen|metzitzah|periah|bandag\w*|surg\w*|operation|procedure|naked|nude|nudity|"
    r"nakedness|unclothed|undress\w*|bare|bottom|buttock\w*|genital\w*|foreskin\w*|prepuce|penis|scrot\w*|nappy|"
    r"nappies|diaper\w*|bath\w*|topless|nackt\w*|naakt|nu|nue|nus|desnud\w*|nudo|nuda|nudi|nagi|nago|голы\w*|"
    r"обнаж\w*|çıplak|telanjang|ערום|עירום|illustrations?|miniatures?|manuscripts?|paintings?|drawings?|engravings?|etchings?|lithograph\w*|prints?)\b",
    re.I)
IMMERSION = re.compile(r"\b(immers\w*|dipp\w*|dunk\w*|plung\w*|submer\w*|untertauch\w*|onderdomp\w*|погруж\w*|"
                       r"orthodox\w*|православ\w*|ortodox\w*|ορθόδοξ\w*)\b", re.I)
BABY = re.compile(r"\b(bab(y|ies)|infants?|newborns?|toddlers?|child\w*|son|daughter|boy|girl|kids?|bébé|"
                  r"säugling\w*|kind|niño|niña|bambin\w*|младен\w*|ребен\w*)\b", re.I)
BRIS_SETTING = re.compile(r"\b(family|families|guests?|blessing|bless\w*|sandek|kvatter|godfather|chair of elijah|"
                          r"elijah'?s chair|celebrat\w*|party|meal|seudah|kiddush|ceremony|synagogue|rabbi|"
                          r"grandfather|father|mother|parents|wrapped|naming)\b", re.I)
RITE_AVOID = re.compile(r"\b(in art|art|paintings?|drawings?|prints?|engravings?|sculptures?|statues?|reliefs?|"
                        r"windows?|stained glass|icons?|books?|certificates?|plaques?|food|cakes?|animal|debaptism|"
                        r"communist|fonts|baptistr\w*|items|videos?|stamps?|postcards?|mohels?|mohalim|"
                        r"circumcis\w*|jesus|christ|zipporah|moses|eliezer|knives?)\b", re.I)
# Commons category -> (rite, child's rite, depth, bris rule); the Wikidata items are named in the open pack.
RITE_CATEGORIES = {
    "Infant baptism": ("an infant baptism (a christening)", True, 1, False),
    "Christening": ("a christening (an infant baptism)", True, 1, False),
    "Baptism": ("a baptism, the Christian rite of admission with water", False, 1, False),
    "Immersion baptism": ("a baptism by immersion", False, 1, False),
    "Believer's baptism": ("a believer's baptism, in which the person being baptised declares their faith", False,
                           1, False),
    "Brit milah": ("a brit milah (bris), the Jewish ceremony held on a baby boy's eighth day", True, 0, True),
    "Sandek": ("a brit milah (bris): the sandek is the person who holds the baby", True, 0, True),
    "First Communion": ("a first communion, when a child receives the Eucharist for the first time", True, 2, False),
    "Confirmation": ("a confirmation, the church ceremony in which baptism is confirmed", False, 1, False),
    "Bar mitzvah": ("a bar mitzvah, the Jewish coming-of-age ceremony of a boy of 13", True, 1, False),
    "Bat mitzvah": ("a bat mitzvah, the Jewish coming-of-age ceremony of a girl of 12", True, 0, False),
    "Shichi-Go-San": ("Shichi-Go-San, the Japanese rite of passage for children of three, five and seven", True, 1,
                      False),
}


# A rite picture's own words (title and caption) must name the rite (in one of several languages); a picture of a building
# (a baptistery, a church, ruins) or a document is not a picture of the rite, whatever its category.
RITE_SHOWN = re.compile(r"baptis(m|ms|ed|ing|e|es)\b|bapt[eê]me|batismo|bautiz\w*|bautismo|battesimo|taufe|doop|"
                        r"christen\w*|k[rř]e?st\w*|chrzest|communion|comuni[oó]n|communie|kommunion|konfirm\w*|"
                        r"confirma\w*|firmung|birmov\w*|bierzmowan\w*|mitzva\w*|mitsva\w*|\bbris\b|\bbrit\b|"
                        r"\bmila(h)?\b|pidyon|aqiqah|akika|shichi|753|七五三|ceremon\w*|godparent\w*|godfather|godmother", re.I)
NOT_THE_RITE = re.compile(r"baptister\w*|baptistr\w*|architecture|building|fa[cç]ade|exterior|ruins?|\bdocuments?\b|"
                          r"register|archiv\w*|\bconf\.|\b(cups?|spoons?|mugs?|bowls?|plates?|rattles?|medals?|coins?|"
                          r"candles?|objects?|museum|cradles?|berceau|plays?|theat(re|er)|performance|"
                          r"re-?enact\w*)\b|mus[ée]e|museo|museu|muzeum|музей", re.I)



def child_rite_ok(text, bris=False, described=True):
    """THE STRICT CHILD RULE: True only when a record's words may be used for a child's rite (see the open pack)."""
    if NOT_FOR_RITES.search(text) or (IMMERSION.search(text) and BABY.search(text)):
        return False
    return not bris or (described and bool(BRIS_SETTING.search(text)))


def prepare_commons_child_rites_sa(source, data_dir, work, cap):
    """Commons photos of children's rites under CC BY-SA or GFDL, through the strict child rule: "What is happening
    in this picture?" with the rite, and the caption; every row of a child's rite marked "child"."""
    s, rng, used = commons_session(), random.Random(731), set()
    want = int((cap + source.test) * 1.2) + 2
    per = max(4, want // len(RITE_CATEGORIES) + 1)
    items, pictures = [], 0
    for category, (rite, child_rite, depth, bris) in RITE_CATEGORIES.items():
        def rows_of(f, rite=rite, child_rite=child_rite, bris=bris):
            """The rows of one file, or [] when the strict rule leaves it out."""
            text = caption(f["text"])
            own = f"{f['title'].split(':', 1)[-1]} {f['text']}"
            if not RITE_SHOWN.search(own) or NOT_THE_RITE.search(own):
                return []
            if not child_rite_ok(file_words(f), bris, described=bool(text)):
                return []
            child = child_rite or bool(CHILD_WORDS.search(file_words(f)))
            rows = [{"question": ASK_HAPPENING, "answer": f"This is {rite}.", "split": "", "credit": f["credit"]}]
            if text and (not bris or BRIS_SETTING.search(text)):
                rows.append({"question": NARRATE, "answer": text, "split": "", "credit": f["credit"]})
            return [dict(r, child=True) if child else r for r in marked(rows, f["title"])]
        got, n = take(s, "rite-sa", files_in(s, category, depth, RITE_AVOID), per, rows_of, rng, used)
        items += got
        pictures += n
    say(f"  Fetching {pictures} Commons rite photos (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- non-commercial: MineInsight

MINEINSIGHT_DAV = "https://cloud.cylab.be/public.php/dav/files/"
# (track, images share, labels share): the colour camera of tracks 1 and 2, sequence 1 (track 3 has no colour frames).
MINEINSIGHT_TRACKS = [("track_1_s1", "ZLWzz9sEoBLyTQF", "srREd5Ppk7cCMsa"),
                      ("track_2_s1", "63grqsSRSMYzQqE", "RxEW938WWT9gXGj")]
MINEINSIGHT_TARGETS = "https://raw.githubusercontent.com/mariomlz99/MineInsight/main/tracks_inventory/targets_list.yaml"
MINEINSIGHT_CREDIT = ("MineInsight dataset (Mario Malizia and others, Royal Military Academy of Belgium and KU Leuven), "
                      "https://github.com/mariomlz99/MineInsight , CC BY-NC-SA 4.0")
# The mines of MineInsight with their kind and country from Wikidata (checked November 2026); a name Wikidata does not
# have is said only as "a ... landmine".
MINEINSIGHT_MINES = {
    "PFM-1": "a PFM-1 (also called the butterfly mine), a Soviet anti-personnel mine",      # Q525179
    "PMN": "a PMN, a Soviet anti-personnel mine",                                           # Q1721001
    "MON-50": "a MON-50, a Soviet directional anti-personnel mine",                         # Q1139759
    "MON-90": "a MON-90, a Soviet anti-personnel mine",                                     # Q6717054
    "PROM-1": "a PROM-1, a Yugoslav anti-personnel mine",                                    # Q1416598
    "VS-50": "a VS-50, an Italian anti-personnel mine",                                     # Q4007062
    "Type 72P": "a Type 72, a Chinese anti-personnel mine",                                 # Q1523910
    "M6": "an M6, an anti-tank mine",                                                       # Q2040620
    "TM-46": "a TM-46, an anti-tank mine",                                                  # Q2985502
    "TMA-2": "a TMA-2, an anti-tank mine",                                                  # Q7670646
    "TMM-1": "a TMM-1, an anti-tank mine",                                                  # Q1341385
}


def mineinsight_targets(s):
    """{target id: name} from MineInsight's targets list (a small YAML file: "- id: 33" then "name: PFM-1")."""
    text = s.get(MINEINSIGHT_TARGETS, timeout=60).text
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"\s*-\s*id:\s*(\d+)", line)
        if m:
            current = int(m.group(1))
            continue
        m = re.match(r"\s*name:\s*(.+?),?\s*$", line)
        if m and current is not None:
            out[current] = clean(m.group(1))
    return out


def mineinsight_answer(names):
    """"This looks like a PMN, a Soviet anti-personnel mine, among litter: a metal tuna can." from the names in one
    frame's boxes; "" when no mine is in the frame."""
    mines, litter = [], []
    for name in names:
        if name in MINEINSIGHT_MINES or re.match(r"^(C-3|M-35|TC-3\.6|M\d)", name):
            said = MINEINSIGHT_MINES.get(name, f"{a_or_an(name)} {name} landmine")
            if said not in mines:
                mines.append(said)
        else:
            thing = re.sub(r"\s*\(.*?\)", "", name).strip().lower()          # "(slightly crumpled)" left out
            if thing and thing not in litter:
                litter.append(thing)
    if not mines:
        return ""
    mines = mines[:3]
    answer = "This looks like " + (mines[0] if len(mines) == 1 else ", ".join(mines[:-1]) + ", and " + mines[-1])
    if litter:
        answer += ", among litter: " + " and ".join(f"{a_or_an(n)} {n}" for n in litter[:2])
    return with_line(answer, SAFETY_LINE)


def prepare_mineinsight(source, data_dir, work, cap, gap=1.0):
    """MineInsight's colour frames with at least one mine, at least gap seconds apart, read out of the tracks' image
    zips piece by piece; "What is on the ground here?" (see the module docstring)."""
    s = commons_session()
    targets = mineinsight_targets(s)
    want = int((cap + source.test) * 1.2) + 2
    chosen = []
    for track, images, labels in MINEINSIGHT_TRACKS:
        labels_zip = zipfile.ZipFile(io.BytesIO(s.get(MINEINSIGHT_DAV + labels, timeout=600).content))
        image_zip = remote_zip(MINEINSIGHT_DAV + images)
        pictures = {re.sub(r"\.jpe?g$", "", n.rsplit("/", 1)[-1]): n for n in image_zip.namelist()
                    if n.lower().endswith((".jpg", ".jpeg"))}
        last = -gap
        for name in sorted(n for n in labels_zip.namelist() if n.endswith(".txt")):
            stem = name.rsplit("/", 1)[-1][:-4]
            m = re.search(r"_(\d+)_(\d+)$", stem)
            if not m or stem not in pictures:
                continue
            when = int(m.group(1)) + int(m.group(2)) / 1e9
            if when - last < gap:
                continue
            ids = [int(line.split()[0]) for line in labels_zip.read(name).decode().splitlines() if line.strip()]
            answer = mineinsight_answer([targets.get(i, "") for i in ids if targets.get(i)])
            if answer:
                last = when
                chosen.append((track, pictures[stem], {"question": ASK_GROUND, "answer": answer, "split": "",
                                                       "credit": f"{MINEINSIGHT_CREDIT}, {track}, frame {stem}"}))
        say(f"  MineInsight {track}: {sum(1 for c in chosen if c[0] == track)} frames with mines")
    random.Random(741).shuffle(chosen)
    chosen = chosen[:want]
    rows = []
    for track, images, _ in MINEINSIGHT_TRACKS:
        mine = [(n, r) for t, n, r in chosen if t == track]
        if mine:
            rows += zip_members(source, data_dir, work, lambda images=images: remote_zip(MINEINSIGHT_DAV + images),
                                mine, workers=3)
    return rows


# ----------------------------------------------------------------- needing sign-up, permission, not included

SAFETY_RITES_SIGN_UP = {
    "DVIDS (Defense Visual Information Distribution Service): US forces photos, public domain, among them many "
    "explosive ordnance disposal, demining and weapons-cache photos":
        "https://www.dvidshub.net : its API needs a free key (https://api.dvidshub.net). Many of its photos are "
        "already on Wikimedia Commons and reach the open commons_uxo pack (Explosive ordnance disposal categories).",
    "Flickr accounts of the US Army, US Navy, US Marine Corps and US State Department (public domain US government "
    "photos, among them EOD and conventional-weapons-destruction photos)":
        "a free Flickr API key (https://www.flickr.com/services/api/); check each photo's licence on its page.",
    "Roboflow Universe landmine and UXO detection sets": "https://universe.roboflow.com : a free account and API key; "
                                                         "each set shows its own licence, and most photos come from "
                                                         "web searches (personal use at most).",
    "Kaggle landmine and UXO image sets": "https://www.kaggle.com : a Kaggle account; check each set's licence and "
                                          "where its photos came from.",
    "MineInsight's other camera streams (VIS-SWIR and LWIR, and the ROS 2 recordings of 5 to 78 GB)":
        "https://github.com/mariomlz99/MineInsight (CC BY-NC-SA 4.0): only the colour frames are used here; the "
        "others are not colour photos.",
}

# Owners who keep all rights: candidates for a permission letter (as permission_sources.py). Checked November 2026.
SAFETY_RITES_PERMISSION = {
    "The HALO Trust (mine clearance photos from about 30 countries)":
        "Terms of use (https://www.halotrust.org/us/terms-of-use, section 4.8): 'All such rights are reserved'; "
        "personal use only, photographs not to be used apart from their text. Ask: mail@halotrust.org (the terms "
        "name it for any other use); media enquiries through https://www.halotrust.org/media-centre/.",
    "MAG (Mines Advisory Group)":
        "Site footer: 'Photos ©MAG unless otherwise stated'; terms (https://www.maginternational.org/terms-and-"
        "conditions/) allow personal, non-commercial use only and ask for 'express written permission' otherwise. "
        "Ask: info@maginternational.org, or the press room https://www.maginternational.org/news-and-insights/"
        "press-room/.",
    "GICHD (Geneva International Centre for Humanitarian Demining), its photos and the IMAS mine identification "
    "material":
        "Terms of use (https://www.gichd.org/terms-of-use/): 'All rights are reserved'; personal and informational "
        "use, 'Reproduced with permission of GICHD', 'Materials may not be modified'. Ask: info@gichd.org, Maison de "
        "la paix, Chemin Eugène-Rigot 2C, PO Box 1300, CH-1211 Geneva 1, Switzerland.",
    "UNMAS (United Nations Mine Action Service) and UN Photo":
        "UN photographs are 'the property of the United Nations' (https://media.un.org/photo/en/guidelines); use "
        "beyond credited journalistic or academic use needs the UN's photo licence. Ask: the UNMAS contact form "
        "https://www.unmas.org/en/contact-us (the Geneva office: unmasgeneva@un.org) and UN Photo "
        "(https://media.un.org/photo/en/guidelines).",
    "ICRC audiovisual archives (mine-risk education and weapon-contamination photos)":
        "Terms (https://avarchives.icrc.org/UsingTerms): personal use only; 'For commercial use, prior authorization "
        "in writing'; no changes, and no 'incorporating it into any database'. Ask through https://avarchives.icrc."
        "org/Contact (the archive says it is not answering requests at present; try again later).",
    "Landmine and Cluster Munition Monitor (ICBL-CMC) report photos":
        "Copyright policy (https://the-monitor.org): do not copy report material, link to it; photos carry their "
        "own credits (often Humanity & Inclusion or other agencies). Ask: monitor@icblcmc.org.",
    "OSCE demining photos (Ukraine, Tajikistan and others)":
        "CC BY-ND 4.0 (osce.org photo pages): no changes allowed, which training on them may count as; ask the OSCE "
        "press office through https://www.osce.org/contacts before use.",
    "US Department of State, Office of Weapons Removal and Abatement (PM/WRA), 'To Walk the Earth in Safety'":
        "State Department staff photos are US government work (public domain), but most photos in its reports are "
        "credited to partners (HALO, MAG, NPA and others) who keep their rights. No photo listing a program can "
        "read. Ask: pm-cpa@state.gov (Bureau of Political-Military Affairs public affairs).",
}

SAFETY_RITES_NOT_INCLUDED = {
    "Wikimedia Commons 'Circumcision surgical procedure', 'Circumcision of a baby', circumcision celebrations "
    "(sünnet, khitanan) and 'Circumcision of Jesus' art":
        "children, or the procedure itself: left out entirely by the owner's strict child rule. Adult medical "
        "circumcision is already in the adult review collections (review_sources.py).",
    "Religious art of baptism, circumcision and the infant Jesus (museums, Europeana prints and paintings)":
        "art often shows unclothed infants and cherubs, which the records do not say, so all paintings, drawings and "
        "prints are left out of the rites collections.",
    "Upanayana and Mundan (Commons)": "boys are often shown bare-chested or with shaved heads in close-up; left out "
                                      "under 'when unsure, leave it out'.",
    "Commons 'Unexploded ordnance' and the landmine and UXO warning-sign categories": "already in the open "
                                                                                     "commons_safety pack "
                                                                                     "(graphic_packs.py) and its "
                                                                                     "share-alike entry "
                                                                                     "(graphic_sources.py).",
    "UAV VNIR hyperspectral landmine and UXO benchmark (arXiv 2510.02700)": "hyperspectral images on a Google "
                                                                            "Drive link, not colour photos.",
    "Demining Research Community test-field data (Oklahoma State University)": "not yet released as open data "
                                                                               "(November 2026).",
    "3D-printed landmine replica photos (Taras Shevchenko National University of Kyiv thesis)":
        "described in a thesis; no download or licence found.",
}


# ----------------------------------------------------------------- the table

SAFETY_RITES_SOURCES = [
    Source("commons_uxo_sa", "Wikimedia Commons photos of landmines, unexploded munitions and demining "
                             "(share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page)",
           "Wikimedia Commons contributors, each file under CC BY-SA or GFDL with its author named, "
           "https://commons.wikimedia.org", "share-alike", 1000, 20, prepare_commons_uxo_sa,
           "about 400 MB of pictures", terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary=COMMONS_TERMS),
    Source("commons_firearms_sa", "Wikimedia Commons photos of firearm and cartridge models (share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page); model facts from Wikidata (CC0)",
           "Wikimedia Commons contributors, each file under CC BY-SA or GFDL with its author named, "
           "https://commons.wikimedia.org ; model facts from Wikidata, https://www.wikidata.org (CC0)",
           "share-alike", 2000, 20, prepare_commons_firearms_sa, "about 800 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/", terms_summary=COMMONS_TERMS),
    Source("commons_child_rites_sa", "Wikimedia Commons photos of baptisms, first communions, bar and bat mitzvahs "
                                     "and other children's rites (share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page)",
           "Wikimedia Commons contributors, each file under CC BY-SA or GFDL with its author named, "
           "https://commons.wikimedia.org", "share-alike", 800, 20, prepare_commons_child_rites_sa,
           "about 300 MB of pictures", terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary=COMMONS_TERMS),
    Source("mineinsight", "MineInsight: landmines among litter, seen by a demining robot's camera (personal use)",
           "CC BY-NC-SA 4.0 (https://github.com/mariomlz99/MineInsight, LICENSE)", MINEINSIGHT_CREDIT,
           "noncommercial", 320, 20, prepare_mineinsight, "about 300 MB read out of 6.6 GB of zips",
           terms="https://creativecommons.org/licenses/by-nc-sa/4.0/",
           terms_summary="CC BY-NC-SA 4.0: non-commercial use with credit, and anything made from it keeps the same "
                         "licence. Personal, non-commercial use only."),
]

# The collections a picture-making model may learn from: none (munitions, guns and children's rites are never
# learnt by picture-making).
SAFETY_RITES_PICTURE_MAKING_OK = set()


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print its answers (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one safety or rites collection.")
    parser.add_argument("key", choices=[s.key for s in SAFETY_RITES_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in SAFETY_RITES_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="safety-rites-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows:
        print(json.dumps({"credit": row["credit"][:100], "question": row["question"], "answer": row["answer"]},
                         ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, "
          f"{sum(1 for r in rows if r.get('content') == 'graphic')} rows marked graphic, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
