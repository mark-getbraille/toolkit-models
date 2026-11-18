"""Pack builders for two safety subjects and one family-life subject, used by build_packs.py in the same way as its
own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}, plus "place" when the record says where the photo was taken (places.py), "child":
True when the picture's words name a child (or the rite is a child's rite), and "content": "graphic" for pictures
whose record names the dead or injured. A picture with more than one question comes once with its JPEG and then as
(None, None, row) twins pointing at it (food_packs.with_twins). The limit counts pictures.

Why: a blind person in a former war zone must be warned when the camera sees a mine, a shell or a grenade; a blind gun
owner, or someone living with one, should be able to tell a revolver from a pistol and a .22 cartridge from a 12-gauge
shell; and a blind parent or guest at a christening, a bris or a first communion should hear what the photos of the
day show. Every fact in an answer comes from the source's own record or from Wikidata (CC0), never guessed and never
written by an AI model. The fixed sentences of the category tables below were written for these packs, from the
Wikidata item named beside each one.

1) Unexploded ordnance, landmines and ammunition found lying around
  commons_munition_models  Wikimedia Commons categories of munition MODELS found through Wikidata: landmines (anti-
                       personnel, anti-tank, bounding and sea mines), cluster bombs and their bomblets, hand, rifle and
                       anti-tank grenades, mortar bombs, artillery shells and rockets, aircraft bombs (MUNITION_KINDS,
                       nuclear weapons left out). "What is this?" -> "This looks like a PFM-1, a Soviet anti-personnel
                       mine." (the model's English label, the kind, and the country of origin, Wikidata P495), and the
                       file's caption as "Describe this picture.".
  commons_uxo          Wikimedia Commons categories of the same dangers in general (UXO_CATEGORIES): landmines and
                       minefields, cluster munitions, grenades, mortar and artillery ammunition, shell fragments,
                       improvised explosive devices, loose ammunition, ammunition boxes and belts, gun magazines, spent
                       cartridge cases, abandoned military equipment, and the people who deal with them (demining, mine
                       detection, bomb disposal by US Army and Navy explosive ordnance disposal teams, International
                       Mine Awareness Day events: mine-risk education). The category's plain sentence and the caption.
  amlid_landmines      AMLID, the Adaptive Multispectral Landmine Identification Dataset (James Gallagher, Zenodo
                       18001447, CC BY 4.0): drone photos of a test field with anti-personnel and anti-tank mines of
                       metal and plastic, with hand-drawn boxes. Only the plain colour photos (fusion level 0, no heat
                       image mixed in). "What does this drone photo show?" -> "This drone photo, taken from 10 metres
                       up, shows two anti-personnel mines and one anti-tank mine on the ground, of metal and plastic."
                       Its 2 GB 7-Zip archive is downloaded once and opened with bsdtar or 7-Zip (as plp_floating_targets
                       in land_industry_packs.py does), so the build machine needs libarchive-tools or p7zip.
  EVERY answer of these three packs ends with SAFETY_LINE: "Do not touch it or go closer. Move back carefully the way
  you came, warn others, and report it to the police, military or a mine-action organisation." No answer says how to
  disarm, handle, move, fire or use anything: a caption that names any handling (HANDLING, service_packs.HOW_TO) is not
  learnt (the picture keeps its "What is this?" row), and categories about making, loading, firing, training,
  cut-away or sectioned munitions are not read (NOT_THE_DANGER), and pictures of munitions in use (dropped from or
  loaded on aircraft, stored aboard ships, being fired: IN_USE) are left out. Rows whose words name the dead or injured are marked
  "content": "graphic"; a dead or injured child, sexual violence, torture and executions are left out
  (service_packs.safety). Children in mine-risk-education photos are kept and marked "child".
  Not repeated here: the open commons_safety pack (graphic_packs.py) already has the Commons categories "Unexploded
  ordnance" (with one level of its subcategories), "Unexploded ordnance warning signs" and "Landmine warning signs"
  (with its subcategories by country: the red skull signs and "Danger Mines" signs in many languages), so every file
  of those categories is skipped here (covered_titles). Small arms as military models are in commons_military
  (service_packs.py).

2) Civilian firearms and cartridges (identified and described as objects only)
  commons_firearms     Wikimedia Commons categories of firearm models found through Wikidata (FIREARM_KINDS: pistols,
                       revolvers, shotguns, rifles and carbines; machine guns and submachine guns are left to
                       commons_military): the model, its family (a "subclass of" that is itself a firearm model: the
                       Colt M1911, the Glock), its kind, its maker (P176), its cartridge (P739 "ammunition") and its
                       country (P495). "What is this?" -> "This looks like a Colt M1911 (a semi-automatic pistol),
                       here a Kongsberg Colt, made by Kongsberg Våpenfabrikk, chambered in .45 ACP." Every answer about
                       a gun ends with GUN_LINE: "Treat every gun as loaded, and keep your fingers away from the
                       trigger."
  commons_cartridges   Wikimedia Commons categories of cartridge models found through Wikidata (CARTRIDGE_KINDS):
                       "This is a .22 Long Rifle rimfire cartridge." / "These are .38 Special revolver cartridges." /
                       "This is a 12-gauge shotgun shell." (rimfire or centrefire and the kind from Wikidata's classes;
                       one or many from the file's words), spent cases or live rounds when the caption or title says
                       so, and the headstamp when the caption gives its text ("The headstamp reads 'WIN 38 SPL'.").
                       No safety line is added to cartridge answers (the owner gave the gun line for guns only); the
                       loose and military ammunition of commons_uxo keeps SAFETY_LINE.
  Rules for both: no loading, firing, cleaning, modification, reloading or purchase words are learnt (a file whose
  words name them is left out: GUN_ACTIONS), nothing compares how deadly guns are, no picture of anyone being shot is
  kept, and nothing here is marked graphic: a file whose words name the dead or wounded is left out. Files naming a
  child are left out. People holding guns are kept only when the record is about the gun. Wikidata's firearm models
  overlap commons_military's "weapon" group, so some photos of the same models (not always the same files) are in
  both packs, with a different answer (this pack's answer names the maker and cartridge and ends with GUN_LINE).

3) Religious rites involving children, described respectfully and factually
  commons_child_rites  Wikimedia Commons categories (RITE_CATEGORIES): baptism and christening (infant and believer's
                       baptism, immersion and pouring), christening gowns, the brit milah (bris) (only the "Brit milah"
                       and "Sandek" categories), the pidyon haben, the aqiqah, first communion, confirmation, bar and bat
                       mitzvah, and Shichi-Go-San. Commons has no categories for the namakarana, naam karan, child
                       dedication or chrismation (November 2026). "What is happening in this picture?" -> "This is a
                       christening, with a priest and the godparents, at a font." (the rite, then only the people,
                       place and way of baptising that the file's own words name: rite_details), and the caption.
  europeana_child_rites  Europeana photos of the same rites whose own rights statement is CC0, the Public Domain Mark
                       or CC BY (never BY-SA, NC or ND), with an English title that names the rite (no translation):
                       first communion photos from Girona, confirmations in Swedish churches, christenings.
  THE STRICT CHILD RULE (child_rite_ok): a record is left out when its title, caption, description or categories
  name the procedure on a child or any undress, in any language (NOT_FOR_RITES: circumcision being performed, the
  cut, the wound, blood, a knife or clamp, "naked", "nude", genitals, foreskin, penis, bath, nappy, bare skin, and
  their German, Dutch, French, Spanish, Italian, Portuguese, Polish, Russian, Turkish, Hebrew and Indonesian forms).
  Infant immersion and Orthodox infant baptism (babies are usually unclothed when dipped) are left out whenever the
  record names a baby and either immersion or the Orthodox church, even when it does not say naked (when unsure,
  leave it out). Brit milah pictures are kept only when their words name the ceremony's setting (the family, guests,
  the blessing, the sandek, the chair of Elijah, the celebration or meal) and have a caption or description, never
  from the title alone; the "Mohels", "Circumcision in Israel" and art categories are not read. Paintings, drawings
  and prints are left out (service_packs.PAINTED), because religious art often shows unclothed infants and cherubs.
  A picture's own title or caption must name the rite (RITE_SHOWN), so a photo merely filed in a rite's category is
  not called that rite; buildings, objects, museum pieces, documents and stage plays are left out (NOT_THE_RITE).
  Medical circumcision is ADULT-only and is not in these packs at all: the adult review collections
  (training-kit/kit/review_sources.py: "Circumcised and uncircumcised human penises in comparison", "Human foreskin",
  "Phimosis") already cover it, and Commons's "Circumcision surgical procedure" files are almost all of babies and
  children (Plastibell devices, restraint boards, "Circumcision of a baby") or drawings, so they are left out
  entirely. Every rite row carries "child": True when the rite is a child's rite or the words name a child, so
  picture-making never learns from them.

Share-alike, non-commercial and research collections on the same subjects, the collections needing sign-up, and the
mine-action organisations whose pictures need a permission letter are in training-kit/kit/safety_rites_sources.py.

    python packs/safety_rites_packs.py commons_uxo --limit 8      (prints titles and answers: a quick check)
"""

import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, smaller
from food_packs import commons_members, count_pictures, with_twins
from expression_packs import CHILD
from everyday_packs import number_word
from world_packs import full_stop
from documentary_packs import tidy, usable, get_json
from places import where, place_from_text
from service_packs import (safety, finish, file_name, commons_files, sparql, kind_items, a_or_an, ADJECTIVES,
                           NOT_COUNTRY, HOW_TO, GRAPHIC, NOT_SHOWN_WAR, PAINTED, ASK_WHAT, ASK_DESCRIBE)

SAFETY_LINE = ("Do not touch it or go closer. Move back carefully the way you came, warn others, and report it to the "
               "police, military or a mine-action organisation.")
GUN_LINE = "Treat every gun as loaded, and keep your fingers away from the trigger."
ASK_HAPPENING = "What is happening in this picture?"
ASK_PLACE = "What kind of place is this?"
ASK_DRONE = "What does this drone photo show?"


def article_for(phrase):
    """ "a" or "an" before a model name, knowing how numbers are said: "an 8×57 mm", "an 11-gauge", "an 18",
    "a .38 Special", "a 12-gauge"; otherwise as service_packs.a_or_an."""
    m = re.match(r"^(\d+)", phrase)
    if m:
        n = m.group(1)
        return "an" if n.startswith("8") or n in ("11", "18") or (len(n) in (5, 6) and n[:2] in ("11", "18")) \
            else "a"
    return "a" if phrase.startswith(".") else a_or_an(phrase)


def with_line(answer, line):
    """An answer with its safety line after it: "This looks like a hand grenade. Do not touch it ..."."""
    return f"{full_stop(answer)} {line}" if line else full_stop(answer)


# ----------------------------------------------------------------- shared Commons helpers

# Captions that describe handling a munition: not learnt, whatever else they say (the picture keeps its other rows).
HANDLING = re.compile(r"\b(disarm\w*|defus\w*|render(ed|ing|s)? (it |them )?safe|dispos(e|ed|ing|al) of|detonat\w*|"
                      r"demolition|blow(n|ing|s)? up|controlled (explosion|burn|detonation)|(explosive|demolition) "
                      r"charges?|C-?4|plac(e|es|ed|ing) (a |the )?charges?|pick(s|ed|ing)? up|carr(y|ies|ied|ying)|"
                      r"lift(s|ed|ing)?|(un)?load(s|ed|ing)?|fir(e|es|ed|ing)\b|throw(s|n|ing)?|threw|launch\w*|"
                      r"arm(s|ed|ing)? (the|a|it)|fuz(e|es|ed|ing)|pull(s|ed|ing)? the pin|remov\w*|dismantl\w*|"
                      r"disassembl\w*|handl(e|es|ed|ing)|mov(e|es|ed|ing)|transport\w*|stack(s|ed|ing)?|"
                      r"prob(e|es|ed|ing)|prodd\w*|excavat\w*|dig(s|ging)?|dug|uncover\w*|cut(s|ting)? (the |a )?wires?|"
                      r"procedures?|techniques?|training|exercise|drill|how to|instructions?|step[- ]by[- ]step)\b",
                      re.I)
# Category and file names that are not a danger found lying around: making, loading, firing, training, art, cut-away
# and sectioned munitions (they show how one works inside), manuals, toys and videos.
NOT_THE_DANGER = re.compile(r"\b(in art|art|advertis\w*|posters?|stamps?|coins?|logos?|icons?|badges?|symbols?|"
                            r"insignia|emblems?|drawings?|diagrams?|schem\w*|illustrations?|paintings?|cartoons?|"
                            r"vector|svg|maps?|charts?|graphics?|text|videos?|audio|animations?|renders?|3d|"
                            r"cutaways?|cut-away|sectioned|cross[- ]sections?|inside|manuals?|AFMAN|field manual|"
                            r"factor(y|ies)|manufactur\w*|assembly|filling|workers?|production|propellants?|reload\w*|"
                            r"loading|hoisting|transport|throwing|grenadiers?|training|trainers?|practice|exercises?|"
                            r"explosions? of|firing|launch\w*|toys?|scale models?|models? of|replicas?|lego|airsoft|props?|"
                            r"memorials?|monuments?|pomnik|denkmal|sculptures?|statues?|ornaments?|jewel\w*|handwritten|signed|"
                            r"bullet drop|ballistics?|comparison|design week|expo|"
                            r"protests?|demonstrations against|campaign|documents?|certificates?|"
                            r"people (throwing|associated)|male people|nuclear|timers?|pipe bombs?|suicide vests?|"
                            r"bombings?|plot|depots?|bunkers?)\b", re.I)


QUICK_CATEGORIES = 0        # main()'s --categories N: a quick check reads only N random categories (0: all)


def chosen(table, key):
    """The table's (category, value) pairs, all of them, or QUICK_CATEGORIES random ones for a quick check."""
    pairs = list(table.items())
    return random.Random(key).sample(pairs, min(QUICK_CATEGORIES, len(pairs))) if QUICK_CATEGORIES else pairs


# Pictures of munitions in use, not lying around: dropped from or loaded on aircraft, stored aboard ships, being
# fired. Left out of the munition packs (the answer's warning would not fit, and they teach nothing about finding one).
IN_USE = re.compile(r"\b(dropp\w*|in flight|bomb bays?|pylons?|wings? of|under the wing|aircraft|airplanes?|"
                    r"B-\d+\w*|bombers?|fighters?|jets?|helicopters?|inventor\w*|aboard|carriers?|loaded|loading|"
                    r"ordnancem[ae]n|aviation ordnance|weapons? (loaders?|load\w*)|being fired|firing|launch\w*|"
                    r"in action|drops?|tests?|testing|competition|build\w*|prepar\w*|assembl\w*|mount\w*|upload\w*)\b", re.I)


def titles_of(s, category, depth, avoid=NOT_THE_DANGER, most_subcats=12):
    """The file titles of a Commons category and, for depth 1 or 2, of its subcategories (and theirs), leaving out
    subcategories and files whose names avoid matches; [] when the category cannot be read."""
    try:
        titles = commons_members(s, category, "file")
    except RuntimeError:
        return []
    level = [category]
    for _ in range(depth):
        below = []
        for parent in level:
            try:
                subs = [c.split(":", 1)[-1] for c in commons_members(s, parent, "subcat")]
            except RuntimeError:
                break
            for sub in [c for c in subs if not avoid.search(c)][:most_subcats]:
                below.append(sub)
                try:
                    titles += commons_members(s, sub, "file")
                except RuntimeError:
                    break
        level = below
    return [t for t in dict.fromkeys(titles) if not avoid.search(t.split(":", 1)[-1].rsplit(".", 1)[0])]


def covered_titles(s):
    """The Commons files that the open commons_safety pack (graphic_packs.py) already reads: its "Unexploded
    ordnance", "Unexploded ordnance warning signs" and "Landmine warning signs" categories (with the subcategories it
    reads). They are skipped here, so no picture is in both packs."""
    from graphic_packs import SAFETY, commons_titles
    out = set()
    for category in ("Unexploded ordnance", "Unexploded ordnance warning signs", "Landmine warning signs"):
        out.update(commons_titles(s, category, SAFETY[category][2]))
    say(f"  {len(out)} files already in commons_safety (skipped)")
    return out


def words_of(f):
    """A Commons file's own words: its title, caption and categories."""
    return " ".join([f["title"].split(":", 1)[-1].rsplit(".", 1)[0].replace("_", " "), f["caption"], f["cats"]])


def danger_rows(f, question, answer, line=SAFETY_LINE):
    """The rows of one Commons file of a munition or a danger: the question with answer and the safety line, and its
    caption (with the safety line) unless the caption names handling or reads like instructions; [] when its words
    must be left out (service_packs.safety)."""
    keep, extra = safety([f["caption"], words_of(f)])
    if not keep or IN_USE.search(f"{f['title']} {f['caption']}"):
        return []
    rows = [{"question": question, "answer": with_line(answer, line), "credit": f["credit"], **where(f["place"]),
             **extra}]
    if f["caption"] and not HANDLING.search(f["caption"]) and not HOW_TO.search(f["caption"]):
        rows.append({"question": ASK_DESCRIBE, "answer": with_line(f["caption"], line), "credit": f["credit"],
                     **where(f["place"]), **extra})
    return rows


# Captions written by an AI tool (some Commons uploaders paste them): never learnt (the owner's rule: no AI-written
# text). The file keeps its other rows.
AI_TEXT = re.compile(r"\b(AI overview|AI answers?|AI[- ]generated|generated by (AI|ChatGPT|an AI)|ChatGPT|Google Lens|"
                     r"Gemini|Copilot|Midjourney|DALL-?E|Stable Diffusion|large language model)\b", re.I)


def take_files(s, key, titles, want, rows_of, rng, skip=(), batch=40, used=None):
    """[(name, picture address, rows)] for up to want free files among titles (shuffled), rows from rows_of(f)
    ([] leaves the file out), files in skip left out; the titles taken are added to used (a set) when given."""
    titles = [t for t in titles if t not in skip]
    rng.shuffle(titles)
    items = []
    for start in range(0, len(titles), batch):
        if len(items) >= want:
            break
        try:
            files = commons_files(s, titles[start:start + batch])
        except RuntimeError as e:                    # Commons kept refusing: keep what came, try the next category
            say(f"  {str(e)[:100]}")
            time.sleep(120)
            break
        for f in files:
            if AI_TEXT.search(f["caption"]):
                f["caption"] = ""
            rows = rows_of(f)
            if rows and len(items) < want:
                if used is not None:
                    used.add(f["title"])
                items.append((file_name(key.replace("_", "-"), f["title"].split(":", 1)[-1].rsplit(".", 1)[0]),
                              f["url"], rows))
    return items


# ----------------------------------------------------------------- Wikidata: model facts

def wd_model_facts(s, items):
    """{item: facts} for Wikidata items, 100 a query: English label, P279 parents (ids), makers (P176 labels),
    cartridges (P739 labels), origins (P495 ids), and English aliases."""
    out, items = {}, list(items)
    for start in range(0, len(items), 100):
        values = " ".join(f"wd:{q}" for q in items[start:start + 100])
        rows = sparql(s, f"""SELECT ?item ?label (GROUP_CONCAT(DISTINCT STRAFTER(STR(?p), "entity/"); separator="|") AS ?parents)
            (GROUP_CONCAT(DISTINCT ?ml; separator="|") AS ?makers) (GROUP_CONCAT(DISTINCT ?al; separator="|") AS ?ammo)
            (GROUP_CONCAT(DISTINCT STRAFTER(STR(?o), "entity/"); separator="|") AS ?origins) (GROUP_CONCAT(DISTINCT ?alias; separator="|") AS ?aka)
            WHERE {{ VALUES ?item {{ {values} }} ?item rdfs:label ?label . FILTER(LANG(?label) = "en")
            OPTIONAL {{ ?item wdt:P279 ?p }} OPTIONAL {{ ?item wdt:P495 ?o }}
            OPTIONAL {{ ?item wdt:P176 ?m . ?m rdfs:label ?ml . FILTER(LANG(?ml) = "en") }}
            OPTIONAL {{ ?item wdt:P739 ?a . ?a rdfs:label ?al . FILTER(LANG(?al) = "en") }}
            OPTIONAL {{ ?item skos:altLabel ?alias . FILTER(LANG(?alias) = "en") }} }} GROUP BY ?item ?label""")
        for r in rows:
            split = lambda k: [v for v in (r.get(k) or "").split("|") if v]           # noqa: E731
            out[r["item"]] = {"label": clean(r.get("label")), "parents": split("parents"), "makers": split("makers"),
                              "ammo": split("ammo"), "origins": [o for o in split("origins") if o.startswith("Q")],
                              "aka": split("aka")}
        time.sleep(1)
    return out


def demonyms(s, ids):
    """{country id: adjective} ("Soviet", "Italian") from ADJECTIVES, else Wikidata's English demonym."""
    out = {q: ADJECTIVES[q] for q in ids if q in ADJECTIVES}
    rest = [q for q in ids if q not in out]
    for start in range(0, len(rest), 200):
        values = " ".join(f"wd:{q}" for q in rest[start:start + 200])
        for r in sparql(s, f"""SELECT ?x ?label (SAMPLE(?d) AS ?dem) WHERE {{ VALUES ?x {{ {values} }}
                ?x rdfs:label ?label . FILTER(LANG(?label) = "en")
                OPTIONAL {{ ?x wdt:P1549 ?d . FILTER(LANG(?d) = "en") }} }} GROUP BY ?x ?label"""):
            if r.get("dem") and not NOT_COUNTRY.search(r.get("label", "")):
                out[r["x"]] = r["dem"]
    return out


def models_of(s, kinds, avoid_qids=()):
    """[(item, Commons category, kind phrase)] for every kind (qid, phrase) in kinds, an item counted under its first
    kind, leaving out items in the class trees of avoid_qids; and {item: set of the kind qids whose tree holds it}."""
    taken = set()
    for qid in avoid_qids:
        taken.update(kind_items(s, qid))
        time.sleep(1)
    chosen, member = [], {}
    for qid, phrase in kinds:
        for item, (cat, _) in kind_items(s, qid).items():
            member.setdefault(item, set()).add(qid)
            if item not in taken:
                taken.add(item)
                chosen.append((item, cat, phrase))
        time.sleep(1)
    say(f"  Wikidata: {len(chosen)} models with a Commons category")
    return chosen, member


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


def label_ok(label):
    """True for a usable English model label: not empty, not a bare Q-number or a Commons category name, and with a
    capital letter or a digit (a model's name: "PFM-1", "Glock 17", ".38 Special"), not a general kind in small letters
    ("semi-automatic pistol"), which Wikidata's class trees also hold."""
    return bool(label) and not re.match(r"^(Q\d+|Category:)", label) and bool(re.search(r"[A-Z0-9]", label))


# ----------------------------------------------------------------- 1a. munition models

# (Wikidata class, how an answer says it), most specific first.
MUNITION_KINDS = [
    ("Q1849288", "bounding anti-personnel mine"), ("Q1148188", "anti-personnel mine"), ("Q828414", "anti-tank mine"),
    ("Q189929", "sea mine"), ("Q178795", "landmine"), ("Q18694371", "cluster bomblet (a submunition)"),
    ("Q184158", "cluster bomb"), ("Q4774484", "anti-tank grenade"), ("Q1520392", "rifle grenade"),
    ("Q173517", "hand grenade"), ("Q12314199", "grenade"), ("Q554308", "mortar bomb (a mortar shell)"),
    ("Q318028", "artillery shell"), ("Q622818", "artillery round"), ("Q1137468", "aircraft bomb"),
    ("Q2037215", "rocket"),
]
# Not munitions found lying around: nuclear weapons (museum casings), and cartridges (commons_cartridges).
MUNITION_AVOID = ("Q12802", "Q37144", "Q1763371")


def munition_answer(facts, phrase, adjectives):
    """"This looks like a PFM-1 (also called the butterfly mine), a Soviet anti-personnel mine" from Wikidata."""
    name = facts["label"]
    adjective = adjectives.get(facts["origins"][0], "") if len(facts["origins"]) == 1 else ""
    kind = f"{adjective} {phrase}".strip()
    nickname = next((a for a in facts["aka"] if re.search(r"\b(butterfly|bouncing betty|pineapple|potato masher|"
                                                          r"toe popper)\b", a, re.I)), "")
    also = f" (also called the {nickname.lower()})" if nickname else ""
    return f"This looks like {article_for(name)} {name}{also}, {a_or_an(kind)} {kind}"


def build_commons_munition_models(limit, per_item=5):
    """The commons_munition_models pack (see the module docstring)."""
    s, rng = session(), random.Random(4401)
    models, _ = models_of(s, MUNITION_KINDS, MUNITION_AVOID)
    facts = wd_model_facts(s, [m[0] for m in models])
    adjectives = demonyms(s, {o for f in facts.values() for o in f["origins"]})
    skip = covered_titles(s)
    rng.shuffle(models)
    items = []
    for item, category, phrase in models:
        if len(items) >= limit * 1.3:
            break
        f_ = facts.get(item)
        if not f_ or not label_ok(f_["label"]):
            continue
        answer = munition_answer(f_, phrase, adjectives)
        items += take_files(s, f"munition-{item}", titles_of(s, category, 1), per_item,
                            lambda f, label=f_["label"]: danger_rows(f, ASK_WHAT, answer) if model_named(
                                label, f"{f['title'].split(':', 1)[-1]} {f['caption']}") else [], rng, skip)
    say(f"  Commons munition models: {len(items)} free pictures")
    return finish("commons_munition_models", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- 1b. dangers by Commons category

# Commons category -> (question, answer, depth of subcategories read). Each answer is followed by SAFETY_LINE.
UXO_CATEGORIES = {
    "Landmines": (ASK_WHAT, "This looks like a landmine.", 0),                                   # Q178795
    "Anti-personnel landmines": (ASK_WHAT, "This looks like an anti-personnel landmine.", 0),    # Q1148188
    "Anti-tank landmines": (ASK_WHAT, "This looks like an anti-tank landmine.", 0),              # Q828414
    "Landmines by country": (ASK_WHAT, "This looks like a landmine.", 1),
    "Landmines in museums": (ASK_WHAT, "This looks like a landmine, here in a museum.", 1),
    "Minefields": (ASK_PLACE, "This looks like a minefield: an area where landmines have been laid.", 1),
    "Cluster bombs": (ASK_WHAT, "This looks like a cluster bomb or its bomblets.", 0),           # Q184158
    "Cluster munitions": (ASK_WHAT, "This looks like a cluster munition or its bomblets.", 0),
    "Submunitions": (ASK_WHAT, "This looks like a submunition: a bomblet from a cluster bomb.", 1),
    "Hand grenades": (ASK_WHAT, "This looks like a hand grenade.", 0),                           # Q173517
    "Hand grenades by country": (ASK_WHAT, "This looks like a hand grenade.", 1),
    "Stick grenades": (ASK_WHAT, "This looks like a stick grenade: a hand grenade on a wooden handle.", 1),
    "Grenades": (ASK_WHAT, "This looks like a grenade.", 0),
    "Mortar ammunition": (ASK_WHAT, "This looks like a mortar bomb (a mortar shell).", 0),       # Q554308
    "Shells (artillery)": (ASK_WHAT, "This looks like an artillery shell.", 1),                  # Q318028
    "Artillery ammunition": (ASK_WHAT, "This looks like artillery ammunition: shells for a large gun.", 0),
    "Artillery ammunition of Ukraine": (ASK_WHAT, "This looks like artillery ammunition: shells for a large gun.",
                                        1),
    "Shell fragments": (ASK_WHAT, "These look like fragments of an exploded shell.", 1),
    "Improvised explosive devices": (ASK_WHAT, "This looks like an improvised explosive device (IED): a home-made "
                                               "bomb.", 0),                                       # Q1249453
    "Ammunition": (ASK_WHAT, "This looks like ammunition.", 0),                                  # Q185785
    "Ammunition of Ukraine": (ASK_WHAT, "This looks like ammunition.", 1),
    "Ammunition boxes": (ASK_WHAT, "This looks like an ammunition box.", 0),
    "Ammunition belts": (ASK_WHAT, "This looks like a belt of ammunition: cartridges linked together in a row.",
                         1),                                                                      # Q1853245
    "Magazines (firearms)": (ASK_WHAT, "This looks like a gun magazine: a case that holds cartridges for a firearm.",
                             1),                                                                  # Q148958
    "Cartridge cases": (ASK_WHAT, "These look like cartridge cases: the metal cases of cartridges, often left "
                                  "after firing.", 1),                                            # Q3433892
    "Abandoned military equipment": (ASK_WHAT, "This looks like abandoned military equipment.", 1),
    "Landmines in Ukraine": (ASK_WHAT, "This looks like a landmine, in Ukraine.", 1),
    "Demining": (ASK_HAPPENING, "This shows demining: specialists clearing landmines from an area.", 0),  # Q1345044
    "Demining by country": (ASK_HAPPENING, "This shows demining: specialists clearing landmines from an area.", 1),
    "Demining in Ukraine": (ASK_HAPPENING, "This shows demining in Ukraine: specialists clearing landmines.", 1),
    "Mine detection": (ASK_HAPPENING, "This shows mine detection: specialists searching the ground for landmines.",
                       0),
    "Explosive ordnance disposal": (ASK_HAPPENING, "This shows explosive ordnance disposal (bomb disposal) "
                                                   "specialists at work. Only trained specialists do this.", 0),
    "Explosive ordnance disposal in the United States": (ASK_HAPPENING, "This shows explosive ordnance disposal (bomb "
                                                                        "disposal) specialists at work. Only trained "
                                                                        "specialists do this.", 1),
    "International Mine Awareness Day": (ASK_HAPPENING, "This shows an event of the International Mine Awareness Day, "
                                                        "which teaches people about the danger of landmines.", 0),
    "Mine recognition sets": (ASK_WHAT, "This looks like a mine recognition set: copies of mines shown to teach "
                                        "people what mines look like.", 0),
}
# Subcategories of the table's categories that are elsewhere or not dangers (warning signs: commons_safety; vector
# drawings and maps; the sandals of a museum).
UXO_AVOID = re.compile(NOT_THE_DANGER.pattern + r"|\b(warning signs|no landmines found|minesweep\w*|sandals|"
                                                r"victims|robots?|dogs?|rats?|vehicles?|machines?|PPE|suits?)\b",
                       re.I)


def build_commons_uxo(limit):
    """The commons_uxo pack (see the module docstring): the categories take turns, a file used once."""
    s, rng = session(), random.Random(4409)
    skip = set(covered_titles(s))
    per = max(4, int(limit * 1.3) // len(UXO_CATEGORIES) + 1)
    items = []
    for category, (question, answer, depth) in chosen(UXO_CATEGORIES, "uxo"):
        got = take_files(s, "uxo", titles_of(s, category, depth, UXO_AVOID), per,
                         lambda f: danger_rows(f, question, answer), rng, skip, used=skip)
        items += got
        say(f"  Commons {category}: {len(got)} free pictures")
    return finish("commons_uxo", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- 1c. AMLID drone photos

AMLID = "https://zenodo.org/api/records/18001447/files/landmine_final%20-%20Copy.7z/content"
AMLID_CREDIT = ("Adaptive Multispectral Landmine Identification Dataset (AMLID), James Gallagher, Zenodo "
                "doi:10.5281/zenodo.18001447, CC BY 4.0")
AMLID_KINDS = {"ap": ("anti-personnel mine", "anti-personnel mines"), "at": ("anti-tank mine", "anti-tank mines")}


def amlid_answer(names, altitude):
    """"This drone photo, taken from 10 metres up, shows two anti-personnel mines and one anti-tank mine on the
    ground, of metal and plastic." from a photo's box labels (ap_metal, at_plastic ...); "" when it has none."""
    counts = {k: sum(1 for n in names if n.startswith(k + "_")) for k in AMLID_KINDS}
    parts = [f"{number_word(n)} {AMLID_KINDS[k][0 if n == 1 else 1]}" for k, n in counts.items() if n]
    if not parts:
        return ""
    materials = sorted({n.split("_", 1)[1] for n in names if "_" in n} & {"metal", "plastic"})
    answer = "This drone photo" + (f", taken from {altitude} metres up," if altitude else "") + \
        " shows " + " and ".join(parts) + " on the ground"
    if materials:
        answer += ", of " + " and ".join(materials)
    return answer


def download_resuming(url, path, tries=30):
    """Download url to path, carrying on from where a stalled or broken download stopped (HTTP range requests; Zenodo
    sends large files slowly and sometimes stops): up to tries attempts, each with a 2-minute stall limit."""
    s = session()
    for attempt in range(tries):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        try:
            with s.get(url, stream=True, timeout=120, headers={"Range": f"bytes={have}-"} if have else {}) as r:
                if r.status_code == 416:                       # nothing left to fetch
                    return
                r.raise_for_status()
                total = have + int(r.headers.get("content-length", 0))
                with open(path, "ab" if r.status_code == 206 else "wb") as f:
                    for chunk in r.iter_content(1 << 22):
                        f.write(chunk)
                if os.path.getsize(path) >= total:
                    return
        except Exception as e:  # noqa: BLE001 - carried on from where it stopped
            say(f"  download stopped at {have // (1 << 20)} MB ({str(e)[:80]}); carrying on")
            time.sleep(min(60, 5 * (attempt + 1)))
    raise RuntimeError(f"{url} could not be downloaded")


def amlid_photos(folder):
    """Download AMLID's archive into folder and take out its plain colour photos (0_lwir) and their labels with bsdtar
    or 7-Zip; [(photo path, label path)], [] when neither program is there."""
    archive = os.path.join(folder, "amlid.7z")
    download_resuming(AMLID, archive)
    if shutil.which("bsdtar"):
        command = ["bsdtar", "-xf", archive, "-C", folder, "*/0_lwir/*"]
    elif shutil.which("7z"):
        command = ["7z", "x", "-y", f"-o{folder}", archive, "-r", "*/0_lwir/*"]
    else:
        say("  AMLID: neither bsdtar nor 7z is installed, so its 7-Zip archive cannot be opened")
        return []
    subprocess.run(command, check=True, capture_output=True)
    os.remove(archive)
    out = []
    for root, _, files in os.walk(folder):
        for name in sorted(files):
            if name.lower().endswith(".jpg") and os.path.basename(root) == "0_lwir":
                label = os.path.join(root, name[:-4] + ".xml")
                if os.path.exists(label):
                    out.append((os.path.join(root, name), label))
    return out


def build_amlid_landmines(limit):
    """The amlid_landmines pack (see the module docstring): plain colour drone photos with at least one mine."""
    rng, out = random.Random(4421), []
    with tempfile.TemporaryDirectory() as folder:
        photos = amlid_photos(folder)
        rng.shuffle(photos)
        say(f"  AMLID: {len(photos)} colour photos")
        for photo, label in photos:
            if len(out) >= limit:
                break
            try:
                names = [o.findtext("name") or "" for o in ET.parse(label).getroot().iter("object")]
            except ET.ParseError:
                continue
            m = re.search(r"/(\d+)m/", photo.replace(os.sep, "/"))
            answer = amlid_answer(names, m.group(1) if m else "")
            with open(photo, "rb") as f:
                picture = smaller(f.read()) if answer else None
            if picture:
                where_in = os.path.relpath(photo, folder).replace(os.sep, "/")
                out.append((file_name("amlid", where_in.rsplit(".", 1)[0]), picture,
                            [{"question": ASK_DRONE, "answer": with_line(answer, SAFETY_LINE),
                              "credit": f"{AMLID_CREDIT}, file {where_in}"}]))
    say(f"amlid_landmines: {len(out)} pictures")
    return with_twins(out)


# ----------------------------------------------------------------- 2a. civilian firearms

FIREARM_KINDS = [
    ("Q6889079", "AR-15-style rifle (a semi-automatic rifle)"), ("Q16000423", "semi-automatic shotgun"),
    ("Q545385", "double-barrelled shotgun"), ("Q486396", "shotgun"), ("Q4215416", "pocket pistol (a small handgun)"),
    ("Q3389302", "semi-automatic pistol"), ("Q170382", "revolver"), ("Q1907525", "pistol"),
    ("Q40280158", "bolt-action rifle"), ("Q42513247", "single-shot rifle"), ("Q2291248", "semi-automatic rifle"),
    ("Q190570", "sniper rifle"), ("Q177456", "assault rifle"), ("Q1194268", "battle rifle"), ("Q183302", "carbine"),
    ("Q178243", "musket"), ("Q124072", "rifle"),
]
# Machine guns and submachine guns stay with commons_military.
FIREARM_AVOID = ("Q12800", "Q178550")
# Files left out of the gun and cartridge packs: actions with a gun (loading, firing, cleaning, changing, reloading,
# buying), shooting people, crime, toys and replicas, and drawings.
GUN_ACTIONS = re.compile(r"\b(fir(e|es|ed|ing)\b|shoot\w*|shot (at|by|dead)|aim(s|ed|ing)?|range|target|"
                         r"load(s|ed|ing)?|unload\w*|reload\w*|handload\w*|clean(s|ed|ing)?|maintenance|"
                         r"disassembl\w*|field[- ]?strip\w*|exploded view|parts?|modif\w*|convert\w*|conversion|"
                         r"build\w*|kits?|for sale|sale|shop|store|dealer|price|buy\w*|purchas\w*|auction|"
                         r"gunshot|murder\w*|crime|suicide|robbery|wounded|killed|victims?|police evidence|evidence|"
                         r"airsoft|replica|toys?|props?|blank[- ]firing|cap guns?|paintball|nerf|drawings?|diagrams?|"
                         r"patents?|advertis\w*|cutaways?|sectioned|x-?rays?|how to|instructions?)\b", re.I)
# File names left out before their records are read (gun_ok checks the rest).
GUN_FILES = re.compile(r"\b(drawings?|diagrams?|svg|vector|in art|advertis\w*|patents?|cutaways?|sectioned|toys?|"
                       r"airsoft|replicas?)\b", re.I)
# Pictures whose focus is people (parades, soldiers, police, hunters, portraits), not the gun, and museum pictures
# of several guns ("Revolvers - Starr Model 1863, Joslyn ..."): left out.
PEOPLE_FOCUS = re.compile(r"\b(soldiers?|troops?|marines?|sailors?|airm[ae]n|parades?|march\w*|defile|ceremon\w*|"
                          r"officers?|police\w*|guards?|hunters?|hunting|portrait|man|men|woman|women|people|"
                          r"crowd|team|squad|upacara|gelar|prajurit|marinir|tentara|latihan|soldat\w*|marksm[ae]n|"
                          r"reenact\w*|re-enact\w*)\b|\b(revolvers|pistols|rifles|shotguns|guns|firearms) -|солдат\w*|"
                          r"военн\w*", re.I)
GUN_WORDS = re.compile(r"\b(AR-?15|AK-?\d+|M-?16|guns?|pistols?|revolvers?|rifles?|shotguns?|carbines?|muskets?|firearms?|handguns?)\b",
                       re.I)
AMMO_WORDS = re.compile(r"\b(cartridges?|rounds?|ammo|ammunition|bullets?|shells?|casings?|cases|brass|headstamps?)"
                        r"\b", re.I)


def gun_ok(f, kind):
    """True when a Commons file of a gun or cartridge category may be used: no action, harm, toy or drawing words,
    no child named, nothing graphic or forbidden; for kind "gun" not a picture of cartridges alone, for kind
    "cartridge" not a picture of a gun."""
    text = words_of(f)
    if GUN_ACTIONS.search(text) or GRAPHIC.search(text) or NOT_SHOWN_WAR.search(text) or CHILD.search(text):
        return False
    if kind == "gun":
        return not (AMMO_WORDS.search(text) and not GUN_WORDS.search(text))
    return bool(AMMO_WORDS.search(text)) and not GUN_WORDS.search(text)


def calibre_words(ammo):
    """", chambered in .45 ACP" / ", made for .38 Special or .38 Long Colt cartridges" / ", made in several
    calibres" from a model's Wikidata cartridges (P739)."""
    ammo = [a for a in ammo if label_ok(a)]
    if len(ammo) == 1:
        return f", chambered in {ammo[0]}"
    if len(ammo) == 2:
        return f", made for {ammo[0]} or {ammo[1]} cartridges"
    return ", made in several calibres" if ammo else ""


def firearm_answer(item, facts, all_facts, phrase, adjectives):
    """"This looks like a Colt M1911 (a semi-automatic pistol), here a Kongsberg Colt, made by Kongsberg
    Våpenfabrikk, chambered in .45 ACP." from Wikidata; "" when the label cannot be used."""
    name = facts["label"]
    if not label_ok(name):
        return ""
    family = next((all_facts[p]["label"] for p in facts["parents"] if p in all_facts and p != item
                   and label_ok(all_facts[p]["label"])), "")
    adjective = adjectives.get(facts["origins"][0], "") if len(facts["origins"]) == 1 else ""
    kind = f"{adjective} {phrase}".strip()
    if family and family != name:
        answer = f"This looks like {article_for(family)} {family} ({a_or_an(kind)} {kind}), here " \
                 f"{article_for(name)} {name}"
    elif phrase.split(" (")[0].split()[-1] in name.lower() and not adjective:
        answer = f"This looks like {article_for(name)} {name}"            # "an Udar revolver", not "..., a revolver"
    else:
        answer = f"This looks like {article_for(name)} {name}, {a_or_an(kind)} {kind}"
    makers = [m for m in facts["makers"] if label_ok(m)]
    if len(makers) == 1 and makers[0].split()[0].lower() not in name.lower():
        answer += f", made by {makers[0]}"
    return answer + calibre_words(facts["ammo"])


def build_commons_firearms(limit, per_item=4):
    """The commons_firearms pack (see the module docstring)."""
    s, rng = session(), random.Random(4431)
    models, _ = models_of(s, FIREARM_KINDS, FIREARM_AVOID)
    facts = wd_model_facts(s, [m[0] for m in models])
    adjectives = demonyms(s, {o for f in facts.values() for o in f["origins"]})
    rng.shuffle(models)
    items = []
    for item, category, phrase in models:
        if len(items) >= limit * 1.3:
            break
        if item not in facts:
            continue
        answer = firearm_answer(item, facts[item], facts, phrase, adjectives)
        if not answer:
            continue

        def rows_of(f, answer=answer, label=facts[item]["label"]):
            """The firearm rows of one file: the model, and its caption, each with GUN_LINE."""
            own = f"{f['title'].split(':', 1)[-1]} {f['caption']}"
            if not gun_ok(f, "gun") or PEOPLE_FOCUS.search(own) or not model_named(label, own):
                return []
            rows = [{"question": ASK_WHAT, "answer": with_line(answer, GUN_LINE), "credit": f["credit"],
                     **where(f["place"])}]
            if f["caption"] and not HANDLING.search(f["caption"]):
                rows.append({"question": ASK_DESCRIBE, "answer": with_line(f["caption"], GUN_LINE),
                             "credit": f["credit"], **where(f["place"])})
            return rows

        items += take_files(s, f"firearm-{item}", titles_of(s, category, 0, GUN_FILES), per_item, rows_of, rng)
    say(f"  Commons firearms: {len(items)} free pictures")
    return finish("commons_firearms", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- 2b. cartridges

CARTRIDGE_KINDS = [("Q1763371", "shotgun shell"), ("Q9150235", "revolver"), ("Q29820118", "revolver"),
                   ("Q9150231", "pistol"), ("Q1076124", "rifle"), ("Q7333267", "rifle"), ("Q37144", "")]
RIMFIRE, CENTREFIRE = "Q1289462", "Q190476"
SPENT = re.compile(r"\b(spent|fired|empty|casings?|(cartridge|shell) cases|brass)\b", re.I)
LIVE = re.compile(r"\b(live|unfired|loaded) (rounds?|cartridges?|ammunition|ammo)\b", re.I)
MANY = re.compile(r"\b(cartridges|rounds|shells|casings|cases|bullets|box(es)? of|several|various|comparison|compared|"
                  r"group|set|row|lineup|collection|two|three|four|five|six|seven|eight|nine|ten|dozen)\b", re.I)
HEADSTAMP = re.compile(r"head ?stamp\w*\s*(?:reads?|reading|marked|says|of|:)?\s*['\"“‘]([A-Z0-9][^'\"”’]{1,24})['\"”’]",
                       re.I)


# Calibres written in a file's words ("7.62 x 54 mm R", ".38 Special", "12 gauge"), to find pictures of several.
CALIBRES = re.compile(r"\d+(?:[.,]\d+)?\s*[x×]\s*\d+|(?<![\w.])\.\d{2,3}\b|\b\d+[- ]gauge\b", re.I)


def cartridge_name(label):
    """A cartridge's Wikidata label as said: "12 gauge" -> "12-gauge", "9×19mm Parabellum" -> "9×19 mm Parabellum"."""
    label = re.sub(r"^(\d+) gauge\b", r"\1-gauge", clean(label))
    return re.sub(r"(\d)mm\b", r"\1 mm", label)


def cartridge_answer(name, phrase, rimfire, f):
    """"This is a .22 Long Rifle rimfire cartridge." / "These are .38 Special revolver cartridges." / "This is a
    12-gauge shotgun shell.", with spent or live and the headstamp when the file's words say so."""
    words = words_of(f)
    many = bool(MANY.search(f["caption"] + " " + f["title"]))
    spent = bool(SPENT.search(words)) and not LIVE.search(words)
    if phrase == "shotgun shell":
        noun = "shotgun shell"
    else:
        noun = ("rimfire " if rimfire else (phrase + " " if phrase else "")) + "cartridge"
    if spent:
        noun = noun.replace("cartridge", "cartridge case").replace("shotgun shell", "shotgun shell case")
    plural = noun + ("s" if not noun.endswith("s") else "es")
    if many:
        answer = f"These are {'fired (spent) ' if spent else ''}{name} {plural}"
    else:
        answer = f"This is {'a' if spent else article_for(name)} {'fired (spent) ' if spent else ''}{name} {noun}"
    answer = full_stop(answer)
    if LIVE.search(words):
        answer += " They are live rounds, with their bullets in place." if many else \
            " It is a live round, with its bullet in place."
    m = HEADSTAMP.search(f["caption"])
    if m:
        answer += f" The headstamp reads '{m.group(1).strip()}'."
    return answer


def build_commons_cartridges(limit, per_item=5):
    """The commons_cartridges pack (see the module docstring)."""
    s, rng = session(), random.Random(4441)
    models, member = models_of(s, CARTRIDGE_KINDS, ("Q12802",))
    rimfire = set(kind_items(s, RIMFIRE))
    facts = wd_model_facts(s, [m[0] for m in models])
    rng.shuffle(models)
    items = []
    for item, category, phrase in models:
        if len(items) >= limit * 1.3:
            break
        if item not in facts or not label_ok(facts[item]["label"]):
            continue
        name = cartridge_name(facts[item]["label"])

        def rows_of(f, name=name, phrase=phrase, rim=item in rimfire):
            """The cartridge rows of one file: what it is, and its caption."""
            own = f"{f['title'].split(':', 1)[-1]} {f['caption']}"
            if not gun_ok(f, "cartridge") or not model_named(name, own) or len(CALIBRES.findall(own)) >= 2:
                return []                              # several calibres in one picture: not one model
            rows = [{"question": ASK_WHAT, "answer": cartridge_answer(name, phrase, rim, f), "credit": f["credit"],
                     **where(f["place"])}]
            if f["caption"] and not HANDLING.search(f["caption"]):
                rows.append({"question": ASK_DESCRIBE, "answer": full_stop(f["caption"]), "credit": f["credit"],
                             **where(f["place"])})
            return rows

        items += take_files(s, f"cartridge-{item}", titles_of(s, category, 0, GUN_FILES), per_item, rows_of, rng)
    say(f"  Commons cartridges: {len(items)} free pictures")
    return finish("commons_cartridges", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- 3. religious rites involving children

# Never shown with a child's rite: the procedure on a child, the cut, blood, tools, any undress or bare body part,
# in many languages. A record whose words match is left out entirely.
NOT_FOR_RITES = re.compile(
    r"circumcis\w*|beschneid\w*|besnijd\w*|circonc\w*|circunci\w*|obrzez\w*|обрез\w*|s[üu]nnet\w*|"
    r"sunat\w*|khitan\w*|khatna|ختان|\b(cut|cuts|cutting|incision|wound\w*|blood\w*|bleed\w*|"
    r"knife|knives|izmel|scalpel|clamp\w*|plastibell|gomco|mogen|metzitzah|periah|bandag\w*|surg\w*|operation|"
    r"procedure|naked|nude|nudity|nakedness|unclothed|undress\w*|bare|bottom|buttock\w*|genital\w*|foreskin\w*|"
    r"prepuce|penis|scrot\w*|nappy|nappies|diaper\w*|bath\w*|topless|nackt\w*|naakt|nu|nue|nus|desnud\w*|nudo|nuda|"
    r"nudi|nude|nagi|nago|голы\w*|обнаж\w*|çıplak|telanjang|ערום|עירום|illustrations?|miniatures?|manuscripts?)\b", re.I)
# Infant immersion and Orthodox infant baptism: babies are usually unclothed, so left out when a baby is named.
IMMERSION = re.compile(r"\b(immers\w*|dipp\w*|dunk\w*|plung\w*|submer\w*|untertauch\w*|onderdomp\w*|"
                       r"погруж\w*|orthodox\w*|православ\w*|ortodox\w*|ορθόδοξ\w*)\b", re.I)
BABY = re.compile(r"\b(bab(y|ies)|infants?|newborns?|toddlers?|child\w*|son|daughter|boy|girl|kids?|"
                  r"bébé|baby's|säugling\w*|kind|niño|niña|bambin\w*|младен\w*|ребен\w*|дит\w*)\b", re.I)
# A bris picture must name its setting, not the procedure.
BRIS_SETTING = re.compile(r"\b(family|families|guests?|blessing|bless\w*|sandek|kvatter|godfather|chair of elijah|"
                          r"elijah'?s chair|celebrat\w*|party|meal|seudah|kiddush|ceremony|synagogue|rabbi|"
                          r"grandfather|father|mother|parents|wrapped|naming)\b", re.I)
# Commons category -> (rite, Wikidata item of its facts, whether it is a child's rite, depth, bris rule).
RITE_CATEGORIES = {
    "Infant baptism": ("an infant baptism (a christening)", "Q1741926", True, 1, False),
    "Christening": ("a christening (an infant baptism)", "Q4240357", True, 1, False),
    "Baptism": ("a baptism, the Christian rite of admission with water", "Q35856", False, 0, False),
    "Baptism by country": ("a baptism, the Christian rite of admission with water", "Q35856", False, 1, False),
    "Immersion baptism": ("a baptism by immersion", "Q9299434", False, 1, False),
    "Believer's baptism": ("a believer's baptism, in which the person being baptised declares their faith",
                           "Q1532651", False, 1, False),
    "Baptism in Jordan River": ("a baptism in the Jordan River", "Q35856", False, 0, False),
    "Christening gowns": ("a christening gown, the long white garment a baby wears to be baptised", "Q4857590", True,
                          1, False),
    "Brit milah": ("a brit milah (bris), the Jewish ceremony held on a baby boy's eighth day", "Q848599", True, 0,
                   True),
    "Sandek": ("a brit milah (bris): the sandek is the person who holds the baby", "Q2670936", True, 0, True),
    "Pidyon haben": ("a pidyon haben, the Jewish ceremony of the redemption of a firstborn son", "Q1416453", True, 0,
                     False),
    "Aqiqah": ("an aqiqah, the Islamic celebration of a baby's birth", "Q1022864", True, 0, False),
    "First Communion": ("a first communion, when a child receives the Eucharist for the first time", "Q1362402",
                        True, 0, False),
    "First Communion by country": ("a first communion, when a child receives the Eucharist for the first time",
                                   "Q1362402", True, 2, False),
    "First Communion clothing": ("a first communion, when a child receives the Eucharist for the first time",
                                 "Q1362402", True, 0, False),
    "Confirmation": ("a confirmation, the church ceremony in which baptism is confirmed", "Q188613", False, 1, False),
    "Bar mitzvah": ("a bar mitzvah, the Jewish coming-of-age ceremony of a boy of 13", "Q28807008", True, 0, False),
    "Bar mitzvahs at the Western Wall": ("a bar mitzvah at the Western Wall in Jerusalem", "Q28807008", True, 0,
                                         False),
    "Bat mitzvah": ("a bat mitzvah, the Jewish coming-of-age ceremony of a girl of 12", "Q2365689", True, 0, False),
    "Shichi-Go-San": ("Shichi-Go-San, the Japanese rite of passage for children of three, five and seven",
                      "Q1072387", True, 1, False),
}
RITE_AVOID = re.compile(r"\b(in art|art|paintings?|drawings?|prints?|engravings?|sculptures?|statues?|reliefs?|"
                        r"windows?|stained glass|icons?|books?|certificates?|plaques?|food|cakes?|animal|debaptism|"
                        r"communist|fonts|baptistr\w*|items|videos?|stamps?|postcards?|mohels?|mohalim|"
                        r"circumcis\w*|jesus|christ|zipporah|moses|eliezer|knives?)\b", re.I)
# Details an answer may name, when the file's words do: (pattern, how it is said, part).
RITE_DETAILS = [
    (r"\bpriests?\b|\bfather [A-Z]", "a priest", "who"), (r"\bpastors?\b", "a pastor", "who"),
    (r"\bministers?\b", "a minister", "who"), (r"\bvicars?\b", "a vicar", "who"), (r"\bbishops?\b", "a bishop", "who"),
    (r"\brabbis?\b", "a rabbi", "who"), (r"\bsandek\b", "the sandek", "who"), (r"\bimams?\b", "an imam", "who"),
    (r"\bgodparents?\b", "the godparents", "who"), (r"\bgod(father|mother)\b", "a godparent", "who"),
    (r"\bparents\b", "the parents", "who"), (r"\bfamil(y|ies)\b", "the family", "who"),
    (r"\bguests\b", "guests", "who"), (r"\bconfirm(ands|ees)\b|\bkonfirmand", "the young people being confirmed",
                                       "who"),
    (r"\bwhite (gown|dress|robe)s?\b|\bchristening gown\b", "a white gown", "who"),
    (r"\bfonts?\b", "at a font", "where"), (r"\brivers?\b", "in a river", "where"), (r"\blakes?\b", "in a lake", "where"),
    (r"\bsea\b|\bbeach\b", "by the sea", "where"), (r"\bsynagogue\b", "in a synagogue", "where"),
    (r"\bwestern wall\b|\bkotel\b", "at the Western Wall", "where"), (r"\bcathedral\b", "in a cathedral", "where"),
    (r"\bchurch\b|\bchapel\b", "in a church", "where"),
    (r"\bpour(s|ed|ing)? water\b|\baffusion\b", "by pouring water", "how"),
    (r"\bsprinkl\w*", "by sprinkling water", "how"), (r"\bimmers\w*", "by immersion", "how"),
]
RITE_DETAILS = [(re.compile(p, re.I), said, part) for p, said, part in RITE_DETAILS]


def rite_details(text):
    """", with a priest and the godparents, at a font, by pouring water" from the words of a record (at most three
    people or things, one place and one way); "" when the words name none."""
    who, where_, how = [], "", ""
    for pattern, said, part in RITE_DETAILS:
        if pattern.search(text):
            if part == "who" and said not in who:
                who.append(said)
            elif part == "where" and not where_:
                where_ = said
            elif part == "how" and not how:
                how = said
    who = who[:3]
    out = ""
    if who:
        out += ", with " + (" and ".join(who) if len(who) <= 2 else f"{who[0]}, {who[1]} and {who[2]}")
    return out + (f", {where_}" if where_ else "") + (f", {how}" if how else "")


# Europeana's type and concept words for art (its photo records also carry "Retrato", portrait, which
# service_packs.PAINTED would take for a painting).
ART_TYPES = re.compile(r"\b(paintings?|pintura|prints?|engravings?|gravura|etchings?|lithograph\w*|litografia|"
                       r"drawings?|desenho|watercolou?rs?|aquarela|holy cards?)\b", re.I)


def child_rite_ok(text, bris=False, described=True, art=PAINTED):
    """THE STRICT CHILD RULE (see the module docstring): True only when a record's words (title, caption,
    description, categories) may be used for a child's rite. art: the pattern of words that make it a work of art
    (left out)."""
    if NOT_FOR_RITES.search(text) or NOT_SHOWN_WAR.search(text) or art.search(text):
        return False
    if IMMERSION.search(text) and BABY.search(text):
        return False
    if bris and not (described and BRIS_SETTING.search(text)):
        return False
    return True


# A rite picture's own words (title and caption) must name the rite (in one of several languages); a picture of a building
# (a baptistery, a church, ruins) or a document is not a picture of the rite, whatever its category.
RITE_SHOWN = re.compile(r"baptis(m|ms|ed|ing|e|es)\b|bapt[eê]me|batismo|bautiz\w*|bautismo|battesimo|taufe|doop|"
                        r"christen\w*|k[rř]e?st\w*|chrzest|communion|comuni[oó]n|communie|kommunion|konfirm\w*|"
                        r"confirma\w*|firmung|birmov\w*|bierzmowan\w*|mitzva\w*|mitsva\w*|\bbris\b|\bbrit\b|"
                        r"\bmila(h)?\b|pidyon|aqiqah|akika|shichi|753|七五三|ceremon\w*|godparent\w*|godfather|godmother", re.I)
NOT_THE_RITE = re.compile(r"baptister\w*|baptistr\w*|architecture|building|fa[cç]ade|exterior|ruins?|\bdocuments?\b|"
                          r"register|archiv\w*|\bconf\.|\b(cups?|spoons?|mugs?|bowls?|plates?|rattles?|medals?|coins?|"
                          r"candles?|objects?|museum|cradles?|berceau|plays?|theat(re|er)|performance|reliefs?|plaques?|"
                          r"sculptures?|bronze|statues?|"
                          r"re-?enact\w*)\b|mus[ée]e|museo|museu|muzeum|музей", re.I)

RITE_LOG = {"kept": [], "left out": []}     # titles, for the quick check (main prints ten of each)


def rite_rows(rite, child_rite, details_text, credit, caption, place, bris=False):
    """The rows of one rite picture: "What is happening in this picture?" with the rite and the details its words
    name, and its caption; every row marked "child" for a child's rite or when the words name a child."""
    extra = {"child": True} if child_rite or CHILD.search(details_text) else {}
    gown = rite.startswith("a christening gown")
    details = "" if gown else rite_details(details_text)
    # a detail the rite already says ("at the Western Wall") is not said twice
    details = [d for d in details.split(", ") if d and d.split(" ", 1)[-1] not in rite]
    answer = f"This is {rite}" + (", " + ", ".join(details) if details else "")
    rows = [{"question": ASK_WHAT if gown else ASK_HAPPENING, "answer": full_stop(answer), "credit": credit,
             **where(place), **extra}]
    if caption and (not bris or BRIS_SETTING.search(caption)):
        rows.append({"question": ASK_DESCRIBE, "answer": full_stop(caption), "credit": credit, **where(place),
                     **extra})
    return rows


def build_commons_child_rites(limit):
    """The commons_child_rites pack (see the module docstring): the categories take turns, each file once, every
    file through child_rite_ok."""
    s, rng = session(), random.Random(4451)
    per = max(4, int(limit * 1.3) // len(RITE_CATEGORIES) + 1)
    items, seen = [], set()
    for category, (rite, _, child_rite, depth, bris) in chosen(RITE_CATEGORIES, "rites"):
        titles = [t for t in titles_of(s, category, depth, RITE_AVOID) if t not in seen]

        def rows_of(f, rite=rite, child_rite=child_rite, bris=bris):
            """The rows of one file, or [] when the strict rule leaves it out (logged for the check)."""
            text = words_of(f)
            own = f"{f['title'].split(':', 1)[-1]} {f['caption']}"
            gown = rite.startswith("a christening gown")       # an object: museum gowns are welcome
            if not (RITE_SHOWN.search(own) or (gown and re.search(r"gowns?|dress", own, re.I))) \
                    or (NOT_THE_RITE.search(own) and not gown):
                return []                                   # not a picture of the rite (not logged: not the rule)
            if not child_rite_ok(text, bris, described=bool(f["caption"])):
                RITE_LOG["left out"].append(f["title"])
                return []
            RITE_LOG["kept"].append(f["title"])
            return rite_rows(rite, child_rite, f"{f['title']} {f['caption']}", f["credit"], f["caption"],
                             f["place"], bris)

        got = take_files(s, "rite", titles, per, rows_of, rng)
        seen.update(t for t in titles)
        items += got
        say(f"  Commons {category}: {len(got)} free pictures")
    return finish("commons_child_rites", items, limit, workers=2, pause=0.5)


EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EUROPEANA_KEY = "api2demo"         # Europeana's public test key; a full build may set EUROPEANA_KEY to its own
EUROPEANA_FREE = re.compile(r"creativecommons\.org/(publicdomain/(zero|mark)/|licenses/by/\d)", re.I)
# Europeana searches: (query, English title words that must be there, the rite as an answer says it, child's rite).
EUROPEANA_RITES = [
    ('title:(christening OR baptism) NOT "of christ"', r"\b(christening|baptism)\b",
     "a baptism, the Christian rite of admission with water", False),
    ('title:"first communion"', r"\bfirst communion\b", "a first communion, when a child receives the Eucharist "
                                                        "for the first time", True),
    ("title:confirmation AND (church OR priest OR confirmand OR bishop)", r"\bconfirmation\b",
     "a confirmation, the church ceremony in which baptism is confirmed", False),
    ('title:("bar mitzvah" OR "bat mitzvah")', r"\b(bar|bat) mitzvah\b", "a bar or bat mitzvah, the Jewish "
                                                                          "coming-of-age ceremony", True),
]
PHOTO_TYPE = re.compile(r"photo|fotogra|stereograph|negative|glass plate|lantern slide|carte de visite|"
                        r"cabinet card|diapositi", re.I)


def build_europeana_child_rites(limit):
    """The europeana_child_rites pack (see the module docstring): photos only, open rights only, English titles
    naming the rite, every record through child_rite_ok."""
    s, items, seen = session(), [], set()
    key = os.environ.get("EUROPEANA_KEY") or EUROPEANA_KEY      # empty when the build has no key saved
    per = max(3, int(limit * 1.3) // len(EUROPEANA_RITES) + 1)
    for query, must, rite, child_rite in EUROPEANA_RITES:
        taken = 0
        for start in (1, 101, 201, 301):
            if taken >= per:
                break
            data = get_json(s, EUROPEANA, {"wskey": key, "query": query, "qf": ["TYPE:IMAGE"], "reusability": "open",
                                           "rows": 100, "profile": "rich", "start": start}) or {}
            for record in data.get("items") or []:
                rights = " ".join(record.get("rights") or [])
                picture = (record.get("edmIsShownBy") or [""])[0]
                title = clean((record.get("title") or [""])[0])
                kinds = " ".join(record.get("dcType") or []) + " " + \
                    " ".join(sum(((record.get("dcTypeLangAware") or {}).values()), []))
                description = clean((record.get("dcDescription") or [""])[0])
                concepts = " ".join(c.get("def", "") if isinstance(c, dict) else str(c)
                                    for c in record.get("edmConceptLabel") or [])
                text = f"{title} {description} {kinds} {concepts}"
                if record.get("id") in seen or taken >= per or not picture or not EUROPEANA_FREE.search(rights) \
                        or re.search(r"by-(sa|nc|nd)", rights) or not re.search(must, title, re.I) \
                        or not PHOTO_TYPE.search(kinds):
                    continue
                seen.add(record["id"])
                if not child_rite_ok(text, art=ART_TYPES):
                    RITE_LOG["left out"].append(title)
                    continue
                RITE_LOG["kept"].append(title)
                taken += 1
                provider = clean((record.get("dataProvider") or ["Europeana"])[0])
                credit = f"{provider} via Europeana, \"{title[:150]}\", {rights}, " \
                         f"https://www.europeana.eu/item{record['id']}"
                labels = record.get("edmPlaceLabelLangAware") or {}
                place = next((p for p in map(place_from_text, (labels.get("en") or [])) if p), "")
                caption = tidy(title) if usable(tidy(title)) else ""
                rows = rite_rows(rite, child_rite, title, credit, caption, place)
                items.append((file_name("europeana-rite", record["id"]), picture, rows))
            time.sleep(0.5)
        say(f"  Europeana {query}: {taken} photos")
    return finish("europeana_child_rites", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- the packs

COMMONS_TERMS = ("captions CC0; pictures CC0, public domain (most US forces photos) or CC BY, each with its author "
                 "and file page below; facts from Wikidata (CC0, https://www.wikidata.org/wiki/Wikidata:Licensing)")

SAFETY_RITES_PACKS = {
    "commons_munition_models": (build_commons_munition_models,
                                "Wikimedia Commons categories of landmine, grenade, shell, bomb and rocket models, found "
                                f"through Wikidata, https://commons.wikimedia.org : {COMMONS_TERMS}. Every answer ends "
                                "with a safety warning written for the pack."),
    "commons_uxo": (build_commons_uxo,
                    "Wikimedia Commons categories of landmines, minefields, unexploded and loose munitions, demining "
                    f"and bomb disposal, https://commons.wikimedia.org : {COMMONS_TERMS}. The plain sentence of each "
                    "category and the safety warning were written for the pack."),
    "amlid_landmines": (build_amlid_landmines,
                        f"{AMLID_CREDIT}, https://zenodo.org/records/18001447 : drone photos and hand-drawn boxes. "
                        "The safety warning was written for the pack."),
    "commons_firearms": (build_commons_firearms,
                         "Wikimedia Commons categories of firearm models, found through Wikidata (maker, cartridge, "
                         f"country), https://commons.wikimedia.org : {COMMONS_TERMS}. Every answer ends with a gun "
                         "safety line written for the pack."),
    "commons_cartridges": (build_commons_cartridges,
                           "Wikimedia Commons categories of cartridge models, found through Wikidata (kind, rimfire), "
                           f"https://commons.wikimedia.org : {COMMONS_TERMS}."),
    "commons_child_rites": (build_commons_child_rites,
                            "Wikimedia Commons categories of baptism, christening, brit milah, first communion, "
                            "confirmation, bar and bat mitzvah and other rites, https://commons.wikimedia.org : "
                            f"{COMMONS_TERMS}. Pictures pass a strict child-protection filter."),
    "europeana_child_rites": (build_europeana_child_rites,
                              "Europeana, https://www.europeana.eu : photos whose own rights statement is CC0, the "
                              "Public Domain Mark or CC BY, each with its provider and record below. Pictures pass a "
                              "strict child-protection filter."),
}

# How many pictures a full build takes from each collection.
SAFETY_RITES_LIMITS = {
    "commons_munition_models": 1500,  # about 300 Wikidata munition models with a Commons category, up to 5 files each
    "commons_uxo": 2000,              # 35 categories, about 60 files each at most (many have fewer free files)
    "amlid_landmines": 1100,          # all 1,097 plain colour photos with labels (each has mines)
    "commons_firearms": 3000,         # about 1,500 firearm models with a Commons category, up to 4 files each
    "commons_cartridges": 1500,       # about 350 cartridge models with a Commons category, up to 5 files each
    "commons_child_rites": 1200,      # 20 categories; the strict filter leaves out many files
    "europeana_child_rites": 400,     # open-rights photos with English titles (few)
}


def main(argv=None):
    """Run one builder with a small limit and print its titles and answers only (a quick check, writes nothing);
    for the rites packs, also ten kept and ten left-out titles of the strict child rule."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one safety, firearms or rites pack builder.")
    parser.add_argument("key", choices=sorted(SAFETY_RITES_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--categories", type=int, default=0, help="read only this many random categories (0: all)")
    args = parser.parse_args(argv)
    global QUICK_CATEGORIES
    QUICK_CATEGORIES = args.categories
    entries = SAFETY_RITES_PACKS[args.key][0](args.limit)
    for name, _, row in entries:
        title = row["credit"].split(" by ")[0] if "commons" in args.key else row["credit"][:120]
        say(f"{title}\n    {row['question']} -> {row['answer']}"
            + (" [child]" if row.get("child") else "") + (" [graphic]" if row.get("content") else ""))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    if RITE_LOG["kept"] or RITE_LOG["left out"]:
        for kind in ("kept", "left out"):
            say(f"Strict child rule, {kind} ({len(RITE_LOG[kind])}):")
            for title in RITE_LOG[kind][:10]:
                say(f"    {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
