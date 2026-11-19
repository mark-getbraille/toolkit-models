"""Pack builders for (A) DRUGS, COUNTERFEIT PILLS AND PARAPHERNALIA and (B) FIREARMS AND FIREARM ACCESSORIES, used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" when the record says where the
photo was taken (places.py). A picture with more than one question comes once with its JPEG and then as (None, None,
row) twins pointing at it (food_packs.with_twins). The limit counts pictures.

Why: the Digital Accessibility Toolkit already explains drugs and firearms with safety notes and links the makers'
manuals; its picture describer should also be able to say what a blind person's camera is pointed at: "This looks
like a bong", "These look like ecstasy tablets", "This looks like a speedloader", "This looks like a Glock pistol".
Every fact in an answer comes from the source's own words (a Commons category's name, a file's caption, a CBP or CDC
caption, a Wikidata item), never guessed and never written by an AI model. The fixed sentences of the category tables
below were written for these packs from the category named beside each one.

(A) Drugs, counterfeit pills and paraphernalia
  commons_drugs        Wikimedia Commons categories of drugs as substances and products (DRUG_CATEGORIES): cannabis
                       buds, edibles, hashish, joints and other cannabis products; cocaine and crack; heroin;
                       methamphetamine; ecstasy (MDMA) tablets and capsules; fentanyl and fentanyl patches;
                       psilocybin mushrooms; opium; ketamine; GHB; counterfeit medicines; seized drugs. "What is
                       this?" -> "These look like ecstasy tablets: pressed pills sold as the drug MDMA, often coloured
                       and stamped with a logo." followed by DRUG_LINE, and the file's own caption.
  commons_drug_paraphernalia  Commons categories of the things used to take drugs and tobacco (PARAPHERNALIA):
                       bongs, smoking pipes, chillums, hookahs, electronic cigarettes and disposable vapes, cannabis
                       vaporizers, rolling papers, herb grinders, drug paraphernalia and heroin paraphernalia.
  commons_cbp_seizures US Customs and Border Protection's own photos on Commons ("Photographs by U.S. Customs and
                       Border Protection", 6,174 files, November 2026; public domain as works of the US government,
                       each file's licence checked) whose TITLE names a drug seizure (CBP_DRUG): "What does this photo
                       show?" -> "This is a US Customs and Border Protection photo of a drug seizure: CBP Officers
                       Seize 95 lbs of Liquid Methamphetamine at Eagle Pass." (CBP's own title), and its caption.
                       Titles that name a person arrested or a smuggler, money, tunnels, testimony or ceremonies are
                       left out (CBP_NOT). The photos often show CBP officers: describing only.
  cdc_phil_drugs       CDC Public Health Image Library photos of street drugs and paraphernalia, e-cigarettes and
                       counterfeit pills (PHIL_DRUG_KEYWORDS), public domain (each item's own copyright field must say
                       "Permission is not required for public domain images", as medical_packs.phil_record checks),
                       with the CDC's caption. Photos of patients, lesions, laboratories and microscope pictures are
                       left out. A small pack: 43 photos found, 6 passed the checks in a test (19 November 2026).
  Rules for (A): no picture of anyone using a drug (USE words: smoking, injecting, snorting, "high" ...), no
  overdoses or the dead, nothing graphic, no child (a file whose words name a child is left out, never marked), no
  chemical structures, drawings, charts, posters, art or advertisements (DRUG_AVOID). In commons_drugs and
  commons_drug_paraphernalia files whose words name a person are left out too, so they show the things themselves.
  DRUG_LINE ends every answer about a substance or pill: "Drugs cannot be identified for sure by how they look: only a
  laboratory test can tell what is in them." (the lesson of DEA's "One Pill Can Kill": counterfeit pills look like
  real medicines).

(B) Firearms and firearm accessories (objects only)
  commons_firearm_accessories  Commons categories of accessories (ACCESSORIES): holsters, speedloaders, moon and
                       stripper clips, magazine loaders, telescopic sights and named civilian scopes, red dot (reflex)
                       and holographic sights, magnifiers, iron sights, night and thermal sights, tactical (weapon)
                       lights, laser sights, slings, foregrips, shooting rests, commercially made suppressors, muzzle
                       brakes, brass catchers, gun cases, cleaning equipment, gun safes, racks and lockers, trigger
                       locks, snap caps and bore sighters. "This looks like a speedloader: a round holder that puts a
                       full set of cartridges into a revolver's cylinder at once."
  commons_firearm_kinds  The files filed directly in Commons's firearm KIND categories (revolvers, semi-automatic
                       pistols, derringers, shotguns by action, rifles by action, flintlocks, muskets, air guns:
                       KINDS) and in its MANUFACTURER categories ("Pistols by manufacturer", "Revolvers by
                       manufacturer", "Rifles by manufacturer", "Shotguns by manufacturer": "This looks like a Smith &
                       Wesson revolver."). Only each category's own files (depth 0): the model categories under them
                       are commons_firearms's (safety_rites_packs.py), so the same photo is seldom in both.
  wikidata_firearms    Wikidata firearm models (safety_rites_packs.FIREARM_KINDS: pistols, revolvers, shotguns,
                       rifles, carbines, muskets; machine guns and submachine guns left out) that have a picture (P18)
                       but NO Commons category (P373): commons_firearms reads the models that have one, so these are
                       other models. "This looks like a Glock 19, an Austrian semi-automatic pistol, made by Glock
                       Ges.m.b.H., chambered in 9×19 mm Parabellum." (safety_rites_packs.firearm_answer, from
                       Wikidata, CC0), and the file's caption.
  Every answer about a gun ends with GUN_LINE: "Treat every gun as loaded, and keep your fingers away from the
  trigger." (the owner's line, as in commons_firearms). Rules for (B): no loading, firing, shooting, cleaning in
  progress, modification, reloading or purchase words in a gun's files (safety_rites_packs.gun_ok and GUN_ACTIONS);
  no picture of anyone being shot, wounded or killed, no gun pointed at a person (POINTED), no crime scenes, toys,
  airsoft or replicas, drawings or patents; files whose words name people (soldiers, police, hunters, portraits:
  safety_rites_packs.PEOPLE_FOCUS and device_packs.PERSON) are left out, so they show the things themselves; files
  naming a child are left out. Nothing that is for MAKING a suppressor or converting a gun to automatic fire
  (solvent traps, baffle or build kits, drilled cups, filter adapters, auto sears, conversion kits: NOT_FOR_MAKING),
  as the manuals collection's FIREARMS_EXCLUDE.
  Not repeated here: Commons's "Magazines (firearms)" and its subcategories are in the open commons_uxo pack
  (safety_rites_packs.py); firearm and cartridge MODELS with a Commons category are commons_firearms and
  commons_cartridges; military small arms and their sights are commons_military (service_packs.py); the Army
  technical-manual figures are field_manual_figures; the small-arms recognition manuals are the kit's personal
  uxo_personal_sources.

Licences (packs/SOURCE-RULES.md, "open"; checked November 2026): Commons files one by one, CC0, public domain or CC BY
(never BY-SA, NC or ND: those are the kit's drug_firearm_commons_sa in training-kit/kit/drug_firearm_sources.py);
Commons captions are structured data, CC0 (https://commons.wikimedia.org/wiki/Commons:Structured_data); Wikidata CC0;
CBP photos are works of the US government (17 U.S.C. 105; each Commons file's licence still checked); CDC PHIL items
only when their own copyright field says public domain. None of these packs is ever used for picture-making (the
kit's NOT_FOR_PICTURE_MAKING), and those that can show people are in its PEOPLE_AND_BODILY_PACK_KEYS.

    python packs/drug_firearm_packs.py commons_drugs --limit 8      (prints a few rows: a quick check)
"""

import re
import sys
import time
from urllib.parse import unquote

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, considered, listing_out_of_time, fetch_all
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from food_packs import with_twins
from expression_packs import CHILD
from device_packs import PERSON
from world_packs import full_stop
from places import where
from service_packs import (safety, finish, file_name, commons_files, sparql, a_or_an, ASK_WHAT, ASK_DESCRIBE,
                           GRAPHIC, NOT_SHOWN_WAR, HOW_TO)
from safety_rites_packs import (titles_of, take_files, words_of, with_line, gun_ok, wd_model_facts, demonyms,
                                firearm_answer, label_ok, AI_TEXT, PEOPLE_FOCUS, GUN_FILES, GUN_LINE, FIREARM_KINDS,
                                FIREARM_AVOID)

ASK_PHOTO = "What does this photo show?"
DRUG_LINE = "Drugs cannot be identified for sure by how they look: only a laboratory test can tell what is in them."
MEDICINE_LINE = "Check the packaging or ask a pharmacist to be sure."
CBP_CATEGORY = "Photographs by U.S. Customs and Border Protection"


# ----------------------------------------------------------------- shared word checks

# Category and file names that are not a photo of the drug or thing: chemistry, drawings, charts, art, laws, people.
DRUG_AVOID = re.compile(r"\b(chemical structures?|structures?|structural|molecul\w*|molecular|models?|diagrams?|svg|"
                        r"drawings?|illustrations?|in art|art|paintings?|posters?|logos?|icons?|charts?|maps?|"
                        r"statistics|graphs?|graphics?|information graphics|infographics?|videos?|animations?|"
                        r"advertis\w*|legal documents|documents?|synthesis|pharmacology|text|stamps?|laws?|"
                        r"protests?|polling|organizations?|research|people|smokers|consumption|culture|"
                        r"cultivation|plants?|leaves|seedlings|seeds|fields?|herbarium|religion|history|media|"
                        r"museums?|shops?|stores?|dispensar\w*|bars?|lounges?|cafes?|caf[ée]s|signs?|"
                        r"walk|anonymous|bear|psychosis|nodding|injection|analogs|advertisements)\b", re.I)
# Words of someone using a drug (left out: no picture of anyone taking drugs), an overdose or a death.
USE = re.compile(r"\b(smok(es|ed|ing)|smoker\w*|inhal\w*|inject\w*|shoot(s|ing)? up|snort\w*|sniff\w*|vap(es|ed|ing)|"
                 r"vaper\w*|toking|puff\w*|exhal\w*|high on|stoned|intoxicat\w*|overdos\w*|OD|addict\w*|users?|"
                 r"junkies?|dealer\w*|nodding|unconscious|dead|death|died|corpses?|syringe in|needle in|arm)\b", re.I)
# Things named with a use word that are not someone using a drug ("smoking pipe", "vaping device"): taken out of a
# file's words before USE is checked.
USE_NOUNS = re.compile(r"\b(smoking|vaping|vape|injecting|injection|smoke) (pipes?|devices?|accessor\w*|articles?|"
                       r"paraphernalia|products?|implements?|equipment|bowls?|mixtures?|blends?|kits?|pens?|"
                       r"liquids?|juices?|shops?|supplies|tobacco|papers?)\b", re.I)


def use_words(f):
    """A file's own words (its title and caption, not its categories) without the USE_NOUNS phrases, for USE."""
    own = f"{f['title'].split(':', 1)[-1].rsplit('.', 1)[0].replace('_', ' ')} {f['caption']}"
    return USE_NOUNS.sub(" ", own)


# Words of people in a file of a things-only pack (device_packs.PERSON has the general ones).
MORE_PEOPLE = re.compile(r"\b(officers?|agents?|police\w*|troopers?|deputies|soldiers?|guards?|officials?|"
                         r"smugglers?|suspects?|arrest\w*|detain\w*|portrait|faces?|hands?|mouth|lips)\b", re.I)


def drug_left_out(f, people_ok=False):
    """Why a Commons file of a drug or paraphernalia category is left out by its words ("" when kept): something
    sexual, violent or graphic, a child, a person using a drug or an overdose, a drawing or chart, AI-written words,
    and (unless people_ok) any person."""
    words = words_of(f)
    keep, marks = safety([f["caption"], words])
    if not keep or marks.get("content") == "graphic" or GRAPHIC.search(words):
        return "its words name harm, death or something never shown"
    if marks.get("child") or CHILD.search(words):
        return "its words name a child"
    if USE.search(use_words(f)):
        return "its words name someone using a drug, an overdose or a death"
    if DRUG_AVOID.search(f["title"].split(":", 1)[-1].rsplit(".", 1)[0]):
        return "its file name says it is a drawing, chart, document or not the thing itself"
    if not people_ok and (PERSON.search(words) or MORE_PEOPLE.search(words) or PEOPLE_FOCUS.search(words)):
        return "its words name a person (this pack shows the things themselves)"
    return ""


def thing_rows(f, question, answer, line="", why=drug_left_out):
    """The rows of one Commons file: the category's question and answer (with its line), and the file's own caption
    (with the line) unless it reads like instructions or was written by an AI tool; [] when its words leave it out
    (noted as considered)."""
    reason = why(f)
    if reason:
        considered(f["title"], f["url"], reason)
        return []
    rows = [{"question": question, "answer": with_line(answer, line), "credit": f["credit"], **where(f["place"])}]
    caption = f["caption"]
    if caption and not HOW_TO.search(caption) and not AI_TEXT.search(caption) and not NOT_FOR_MAKING.search(caption):
        rows.append({"question": ASK_DESCRIBE, "answer": with_line(caption, line), "credit": f["credit"],
                     **where(f["place"])})
    return rows


QUICK_CATEGORIES = 0        # main()'s --categories N: a quick check reads only N random categories (0: all)


def table_pack(key, table, limit, seed, rows_of, avoid, skip_cats=None):
    """A pack from a table {Commons category: (question, answer, depth, line)}: the categories share the limit,
    each file used once (the first category that takes it), files in a category matching skip_cats left out."""
    s, rng = session(), pass_random(seed)
    if QUICK_CATEGORIES:
        table = dict(pass_random(key).sample(sorted(table.items()), min(QUICK_CATEGORIES, len(table))))
    per = max(4, int(limit * 1.3) // max(1, len(table)) + 1)
    items, used = [], set()
    for category, (question, answer, depth, line) in table.items():
        if listing_out_of_time():
            say(f"  {key}: stopped looking at half the time limit")
            break

        def rows(f, question=question, answer=answer, line=line):
            """The rows of one file of this category (none for a file of a skipped category)."""
            if skip_cats is not None and skip_cats.search(f["cats"]):
                considered(f["title"], f["url"], "already in another of these packs")
                return []
            return rows_of(f, question, answer, line)

        got = take_files(s, key, titles_of(s, category, depth, avoid), per, rows, rng, skip=used, used=used)
        items += got
        say(f"  Commons {category}: {len(got)} free pictures")
    return finish(key, items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- (A) commons_drugs

def drug(answer, depth=0, line=DRUG_LINE, question=ASK_WHAT):
    """One row of DRUG_CATEGORIES or PARAPHERNALIA: (question, answer, depth of subcategories read, line)."""
    return (question, answer, depth, line)


DRUG_CATEGORIES = {
    "Cannabis buds": drug("This looks like cannabis (marijuana) flower: the dried buds of the cannabis plant, which are "
                          "smoked or vaped.", 1),
    "Cannabis edibles": drug("This looks like a cannabis edible: a food or sweet made with cannabis.", 1),
    "Products from cannabis": drug("This looks like a product made from cannabis.", 1),
    "Hashish": drug("This looks like hashish (hash): resin from the cannabis plant pressed into a block.", 1),
    "Joints (cannabis)": drug("This looks like a joint: cannabis rolled in paper to be smoked.", 1),
    "Cocaine": drug("This looks like cocaine: an illegal stimulant drug, usually a white powder."),
    "Cocaine hydrochloride": drug("This looks like cocaine: an illegal stimulant drug, usually a white powder."),
    "Crack cocaine": drug("This looks like crack cocaine: cocaine made into small off-white rocks that are smoked.", 1),
    "Heroin": drug("This looks like heroin: an illegal opioid drug, a white or brown powder or a black sticky tar."),
    "Methamphetamine": drug("This looks like methamphetamine (meth): an illegal stimulant drug, often clear or white "
                            "crystals or a powder."),
    "Seizing methamphetamine in the United States": drug("This photo is of a methamphetamine (meth) seizure in the "
                                                         "United States: the drug, or things found where it was "
                                                         "made."),
    "Ecstasy tablets": drug("These look like ecstasy tablets: pressed pills sold as the drug MDMA, often coloured and "
                            "stamped with a logo."),
    "MDMA capsules": drug("These look like capsules of MDMA (ecstasy or molly)."),
    "MDMA salt": drug("This looks like MDMA (ecstasy or molly) as crystals or a powder."),
    "Fentanyl": drug("This is filed as fentanyl: a very strong opioid, made as a medicine and also made illegally as a "
                     "powder or pressed into counterfeit pills."),
    "Fentanyl patches": drug("This looks like a fentanyl patch: a skin patch that gives a very strong opioid pain "
                             "medicine.", line=MEDICINE_LINE),
    "Psilocybin mushrooms": drug("These look like psilocybin mushrooms (magic mushrooms), which contain a "
                                 "hallucinogenic drug."),
    "Opium": drug("This looks like opium: the dried sap of the opium poppy, from which morphine and heroin are made."),
    "Ketamine": drug("This looks like ketamine: an anaesthetic medicine that is also used illegally as a drug."),
    "GHB": drug("This looks like GHB: a sedative drug, usually a clear liquid."),
    "Counterfeit medications": drug("This looks like a counterfeit (fake) medicine: made to look like a real "
                                    "medicine, but it may hold the wrong drug, too much of it, or none.", 1),
    "Seized drugs": drug("These look like illegal drugs seized by police or customs.", 1),
}


def drug_rows(f, question, answer, line):
    """The rows of one file of a drug category (thing_rows with the drug checks; no people)."""
    return thing_rows(f, question, answer, line, drug_left_out)


def build_commons_drugs(limit):
    """The commons_drugs pack (see the module docstring). CBP's own photos are left to commons_cbp_seizures."""
    return table_pack("commons_drugs", DRUG_CATEGORIES, limit, 5101, drug_rows, DRUG_AVOID,
                      skip_cats=re.compile(re.escape(CBP_CATEGORY)))


# ----------------------------------------------------------------- (A) commons_drug_paraphernalia

PARAPHERNALIA = {
    "Bongs": drug("This looks like a bong: a water pipe used to smoke cannabis or tobacco.", 1, ""),
    "Smoking pipes": drug("This looks like a smoking pipe, used to smoke tobacco or other dried plants.", 1, ""),
    "Chillums": drug("This looks like a chillum: a straight pipe, often of clay, used to smoke cannabis or tobacco.",
                     1, ""),
    "Hookahs": drug("This looks like a hookah (a shisha pipe): a tall water pipe with a hose, used to smoke "
                    "flavoured tobacco.", 1, ""),
    "Electronic cigarettes": drug("This looks like an electronic cigarette (a vape): a battery device that heats a "
                                  "liquid into a vapour to breathe in, usually with nicotine.", 1, ""),
    "Disposable electronic cigarettes": drug("This looks like a disposable vape: an electronic cigarette that is "
                                             "thrown away when it is empty.", 1, ""),
    "Cannabis vaporizers": drug("This looks like a cannabis vaporizer: a device that heats cannabis into a vapour to "
                                "breathe in.", 1, ""),
    "Cigarette rolling papers": drug("These look like rolling papers: thin papers for rolling cigarettes or joints "
                                     "by hand.", 1, ""),
    "Herb grinders": drug("This looks like a herb grinder: a small round box with teeth inside, used to grind "
                          "cannabis or herbs.", 0, ""),
    "Drug paraphernalia": drug("This looks like drug paraphernalia: equipment used to take illegal drugs.", 1, ""),
    "Heroin paraphernalia": drug("This looks like paraphernalia used for heroin, such as needles, spoons or foil.",
                                 0, ""),
}


def build_commons_drug_paraphernalia(limit):
    """The commons_drug_paraphernalia pack (see the module docstring)."""
    return table_pack("commons_drug_paraphernalia", PARAPHERNALIA, limit, 5111, drug_rows, DRUG_AVOID)


# ----------------------------------------------------------------- (A) commons_cbp_seizures

CBP_DRUG = re.compile(r"\b(cocaine|crack|heroin|fentanyl|meth|methamphetamine|marijuana|cannabis|hashish|narcotics?|"
                      r"drugs?|pills?|tablets?|ecstasy|MDMA|opium|ketamine|kratom|khat|steroids?|oxycodone|"
                      r"tramadol|carfentanil|pseudoephedrine|GHB|GBL)\b", re.I)
# Titles of CBP drug files that are about something else: arrests and smugglers (identifiable people), money,
# tunnels, hearings, ceremonies, dogs at work and training.
CBP_NOT = re.compile(r"\b(arrest\w*|nab\w*|apprehend\w*|smugglers?|man|woman|men|women|driver|traveler|"
                     r"passenger|teen\w*|juvenile|currency|cash|money|tunnel|testimony|hearing|ceremony|memorial|"
                     r"symposium|visit|secretary|commissioner|award|training|dogs?|canine|K-?9|"
                     r"press conference)\b", re.I)
CBP_SAYS = "This is a US Customs and Border Protection photo of a drug seizure: "


def cbp_title(title):
    """A CBP file's title as said: without "File:", the Flickr number in brackets and the file ending."""
    text = title.split(":", 1)[-1].rsplit(".", 1)[0]
    return re.sub(r"\s*\(\d{6,}\)\s*$", "", text).replace("_", " ").strip()


def cbp_rows(f):
    """The rows of one CBP file: what the photo shows (CBP's own title) and its caption; [] when left out."""
    words = words_of(f)
    keep, marks = safety([f["caption"], words])
    if not keep or marks or GRAPHIC.search(words) or CHILD.search(words) or USE.search(USE_NOUNS.sub(" ", f["caption"])):
        considered(f["title"], f["url"], "its words name harm, a child or someone using a drug")
        return []
    title = cbp_title(f["title"])
    rows = [{"question": ASK_PHOTO, "answer": full_stop(CBP_SAYS + title), "credit": f["credit"],
             **where(f["place"] or "USA")}]
    if f["caption"] and not AI_TEXT.search(f["caption"]) and not CBP_NOT.search(f["caption"]):
        rows.append({"question": ASK_DESCRIBE, "answer": full_stop(f["caption"]), "credit": f["credit"],
                     **where(f["place"] or "USA")})
    return rows


def cbp_titles(titles):
    """The CBP file titles that name a drug seizure and nothing left out (the others noted as considered)."""
    out = []
    for t in titles:
        said = cbp_title(t)
        if CBP_DRUG.search(said) and not CBP_NOT.search(said):
            out.append(t)
    return out


def build_commons_cbp_seizures(limit):
    """The commons_cbp_seizures pack (see the module docstring)."""
    s, rng = session(), pass_random(5121)
    titles = cbp_titles(titles_of(s, CBP_CATEGORY, 0, DRUG_AVOID))
    say(f"  CBP: {len(titles)} files whose title names a drug seizure")
    items = take_files(s, "cbp", titles, int(limit * 1.3) + 2, cbp_rows, rng)
    return finish("commons_cbp_seizures", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- (A) cdc_phil_drugs

PHIL_DRUG_KEYWORDS = ("heroin", "marijuana", "drug paraphernalia", "counterfeit", "street drugs", "amphetamine",
                      "barbiturate", "e-cigarette", "vaping", "cocaine", "narcotic", "opioid", "LSD")
PHIL_DRUG_WORDS = re.compile(r"\b(heroin|marijuana|cannabis|paraphernalia|counterfeit|street drugs?|amphetamines?|"
                             r"barbiturates?|tranquilizers?|e-cigarettes?|electronic cigarettes?|vap(e|es|ing)|"
                             r"cocaine|narcotics?|opioids?|LSD|pills?|tablets?|capsules?|syringes?)\b", re.I)
# Not a photo of a drug or of paraphernalia: patients and their skin, laboratories, microscope pictures, insects,
# plants growing, charts and posters, people at work.
PHIL_NOT_DRUG = re.compile(r"\b(patients?|lesions?|ulcer\w*|skin|forearms?|abscess\w*|infection|laborator\w*|"
                           r"technicians?|pipett\w*|micrograph\w*|microscop\w*|magnifi\w*|beetles?|larva\w*|"
                           r"insects?|plant|leaflets?|chart|graph|poster|infographic|illustration|student|survey\w*|"
                           r"residents?|advisory|youth|high school|percent|%)\b", re.I)


def phil_drug_left_out(r):
    """Why a PHIL record is left out ("" when kept): not public domain, no drug named, not a photo of a drug or of
    paraphernalia, harm, a child or someone using a drug."""
    caption = r.get("caption") or ""
    if not r.get("public"):
        return "not marked public domain"
    if not PHIL_DRUG_WORDS.search(caption):
        return "its caption names no drug or paraphernalia"
    if PHIL_NOT_DRUG.search(caption):
        return "not a photo of a drug or of paraphernalia (a patient, a laboratory, a chart, an insect ...)"
    if GRAPHIC.search(caption) or NOT_SHOWN_WAR.search(caption) or CHILD.search(caption):
        return "its caption names harm or a child"
    if re.search(r"\b(inject\w*|snort\w*|being smoked|smoking it|overdos\w*)\b", caption, re.I):
        return "its caption names someone using a drug"
    return ""


def build_cdc_phil_drugs(limit):
    """The cdc_phil_drugs pack: PHIL keyword searches (medical_packs.phil_records: public-domain items with a picture
    and a caption), each record checked by phil_drug_left_out, the CDC's caption as "Describe this picture."."""
    from medical_packs import phil_records, phil_credit
    from med_vet_packs import phil_caption
    items = []
    for r in phil_records(PHIL_DRUG_KEYWORDS):
        if len(items) >= limit * 1.2 + 2 or listing_out_of_time():
            break
        name = f"phil-{r['pid']}.jpg"
        why = phil_drug_left_out(r)
        caption = "" if why else phil_caption(r["caption"])
        if why or not caption:
            considered(name, r.get("picture"), why or "its caption is too short")
            continue
        items.append((name, r["picture"], [{"question": ASK_DESCRIBE, "answer": caption, "credit": phil_credit(r),
                                            "facts": {"phil_id": r["pid"]}}]))
    say(f"CDC PHIL drugs: {len(items)} usable")
    return with_twins(fetch_all(items, workers=3)[:limit])


# ----------------------------------------------------------------- (B) shared gun checks

# A gun pointed at someone, people shot, crime scenes: never kept (the gun packs' own GUN_ACTIONS and
# service_packs.GRAPHIC catch most; these are the rest).
POINTED = re.compile(r"\b(point(s|ed|ing)? (a |the |his |her )?(gun|pistol|rifle|revolver|shotgun|weapon)s? at|"
                     r"at gunpoint|held up|hold-?up|hostages?|threat\w*|mass shooting|shooting (victims?|scene)|"
                     r"crime scenes?|homicide|assassinat\w*|attacks?|attackers?|massacres?|spree|terroris\w*|"
                     r"killers?|perpetrat\w*|shooters?|shootings?|used (by|in) the)\b", re.I)
# Artillery and other large guns: not firearms (some Commons accessory categories, such as "Muzzle brakes", hold
# them too).
ARTILLERY = re.compile(r"\b(artillery|cannons?|howitzers?|anti-?tank|anti-?aircraft|tanks?|field guns?|naval guns?|"
                       r"gun turrets?|turrets?|warships?|ships?|fortress\w*|flak|pak ?\d+|mortars?|"
                       r"\d+(\.\d+)? ?cm|\d{2,3} ?mm (gun|cannon))\b", re.I)
# Anything for MAKING a suppressor or converting a gun to automatic fire (as manuals/categories.FIREARMS_EXCLUDE).
NOT_FOR_MAKING = re.compile(r"\b(solvent traps?|baffles?|build kits?|form 1|drilled|indexed|filter adapters?|"
                            r"oil filters?|fuel filters?|home-?made|homemade|improvised|auto ?sears?|lightning links?|"
                            r"conversion kits?|full[- ]auto conversion|switch(es)? for glock|glock switch(es)?|"
                            r"3D[- ]printed|ghost guns?|80% lowers?|jigs?)\b", re.I)
# Gun accessories may be shown with cleaning, cases, shops and kits (unlike a gun's files): the checks for them.
ACCESSORY_NOT = re.compile(r"\b(fir(e|es|ed|ing)\b|shoot(s|ing)? (at|people|someone)|shot (at|by|dead)|gunshot|"
                           r"murder\w*|crime|suicide|robbery|police evidence|evidence|airsoft|replica|toys?|props?|"
                           r"paintball|nerf|drawings?|diagrams?|patents?|advertis\w*|cutaways?|x-?rays?|exploded "
                           r"view)\b", re.I)


def accessory_left_out(f):
    """Why a Commons file of an accessory category is left out ("" when kept)."""
    words = words_of(f)
    keep, marks = safety([f["caption"], words])
    if not keep or marks or GRAPHIC.search(words) or CHILD.search(words):
        return "its words name harm, death, a child or something never shown"
    if ACCESSORY_NOT.search(words) or POINTED.search(words):
        return "its words name shooting, crime, a toy or replica, or a drawing"
    if ARTILLERY.search(words):
        return "its words name artillery or another large gun, not a firearm"
    if NOT_FOR_MAKING.search(words):
        return "its words name something for making a suppressor or converting a gun"
    if PEOPLE_FOCUS.search(words) or PERSON.search(words) or MORE_PEOPLE.search(words):
        return "its words name a person (this pack shows the things themselves)"
    return ""


# A file's own words naming more than one gun ("Flintlock pistol and revolver", "Pistols", "a collection of rifles"):
# one kind or maker's answer would not fit it.
GUN = r"(guns?|pistols?|revolvers?|rifles?|shotguns?|carbines?|muskets?|derringers?|handguns?)"
MANY_GUNS = re.compile(rf"\b{GUN}\s+(and|&|with|or|vs\.?|versus)\s+(an? |the |\w+ ){{0,3}}{GUN}\b|"
                       r"\b(pistols|revolvers|rifles|shotguns|carbines|muskets|derringers|handguns|guns|firearms)\b|"
                       r"\b(collection|display|several|various|assortment|comparison|compared|group|row|rack)\b",
                       re.I)


def gun_rows_ok(f):
    """True when a gun file's own words (title and caption) name one gun, not several."""
    own = f"{f['title'].split(':', 1)[-1].rsplit('.', 1)[0].replace('_', ' ')} {f['caption']}"
    return not MANY_GUNS.search(own)


def gun_left_out(f):
    """Why a Commons file of a gun is left out ("" when kept): safety_rites_packs.gun_ok (no actions, harm, toys,
    drawings, children, cartridges alone), a gun pointed at someone, making or converting, and people."""
    words = words_of(f)
    if not gun_ok(f, "gun") or POINTED.search(words) or NOT_FOR_MAKING.search(words) or ARTILLERY.search(words):
        return "its words name an action with a gun, harm, a toy, a drawing, a child, or making or converting one"
    if PEOPLE_FOCUS.search(words) or PERSON.search(words) or MORE_PEOPLE.search(words):
        return "its words name a person (this pack shows the guns themselves)"
    return ""


def accessory_rows(f, question, answer, line):
    """The rows of one file of an accessory category (a gun's line when the category is a gun in a holster)."""
    return thing_rows(f, question, answer, line, gun_left_out if line else accessory_left_out)


def gun_rows(f, question, answer, line):
    """The rows of one file of a gun kind or maker category, each with GUN_LINE; none for a file whose own words
    name several guns (MANY_GUNS)."""
    if not gun_rows_ok(f):
        considered(f["title"], f["url"], "its words name several guns, so one kind's answer would not fit")
        return []
    return thing_rows(f, question, answer, line, gun_left_out)


# ----------------------------------------------------------------- (B) commons_firearm_accessories

def acc(answer, depth=0, line=""):
    """One row of ACCESSORIES: (question, answer, depth, line)."""
    return (ASK_WHAT, answer, depth, line)


ACCESSORIES = {
    "Holsters": acc("This looks like a holster: a case worn on a belt or under the arm that holds a handgun."),
    "Revolvers in holster": acc("This looks like a revolver in its holster.", line=GUN_LINE),
    "Pistols in holster": acc("This looks like a pistol in its holster.", line=GUN_LINE),
    "Speedloaders": acc("This looks like a speedloader: a round holder that puts a full set of cartridges into a "
                        "revolver's cylinder at once."),
    "Moon clips": acc("This looks like a moon clip: a flat metal ring that holds a revolver's cartridges together."),
    "Stripper clips": acc("This looks like a stripper clip: a metal strip that holds a row of cartridges for filling a "
                          "magazine."),
    "Magazine loaders": acc("This looks like a magazine loader: a tool that helps push cartridges into a gun "
                            "magazine."),
    "Telescopic sights": acc("This looks like a telescopic sight (a scope): a small telescope mounted on a gun for "
                             "aiming."),
    "Leupold telescopic sight": acc("This looks like a Leupold rifle scope: a telescopic sight mounted on a gun for "
                                    "aiming."),
    "NightForce Optics": acc("This looks like a Nightforce rifle scope: a telescopic sight mounted on a gun for "
                             "aiming."),
    "Swarovski telescopic sights for rifles": acc("This looks like a Swarovski rifle scope: a telescopic sight "
                                                  "mounted on a gun for aiming."),
    "SIG Tango6": acc("This looks like a SIG Sauer Tango6 rifle scope: a telescopic sight mounted on a gun for "
                      "aiming."),
    "Reflex sights": acc("This looks like a red dot (reflex) sight: a small sight that shows a lit dot to aim with."),
    "Holographic firearm sights": acc("This looks like a holographic sight: a sight with a small window that shows a "
                                      "lit aiming mark."),
    "Aimpoint": acc("This looks like an Aimpoint red dot sight: a small sight that shows a lit dot to aim with."),
    "Red dot magnifier": acc("This looks like a red dot magnifier: a small telescope fitted behind a red dot sight to "
                             "make the target look closer."),
    "Iron sights": acc("These look like iron sights: the metal front and rear sights on a gun, used for aiming."),
    "Night vision sights": acc("This looks like a night-vision sight for a gun."),
    "Thermal imaging sights": acc("This looks like a thermal sight for a gun: it shows warm things in the dark."),
    "Tactical lights": acc("This looks like a tactical light: a strong flashlight, often mounted on a gun."),
    "Surefire lights": acc("This looks like a SureFire light: a strong flashlight, often mounted on a gun."),
    "Streamlight TLR-1": acc("This looks like a Streamlight TLR-1: a light that mounts on a handgun or rifle."),
    "Laser sights": acc("This looks like a laser sight: a small laser mounted on a gun that shows a dot where it "
                        "points."),
    "Slings (firearms)": acc("This looks like a gun sling: a strap for carrying a rifle or shotgun over the "
                             "shoulder."),
    "Foregrip": acc("This looks like a foregrip: a handle under the front of a rifle."),
    "Shooting rests": acc("This looks like a shooting rest: a stand that holds a rifle steady on a bench."),
    "Firearm silencers": acc("This looks like a suppressor (a silencer): a tube fitted to the end of a gun's barrel "
                             "that makes the shot quieter."),
    "Muzzle brakes": acc("This looks like a muzzle brake: a part on the end of a barrel that lets gas out of the "
                         "sides to reduce the kick."),
    "Brass catcher": acc("This looks like a brass catcher: a small bag that catches the empty cartridge cases a gun "
                         "throws out."),
    "Firearm cases": acc("This looks like a gun case: a padded or hard case for carrying a gun."),
    "Gun cleaning equipment": acc("This looks like gun cleaning equipment: rods, brushes, patches or oil for "
                                  "cleaning a gun."),
    "Gun swabs": acc("This looks like a gun swab: a cloth or cotton pad used to clean the inside of a barrel."),
    "Gun safes": acc("This looks like a gun safe: a locked steel cabinet for storing guns safely.", 1),
    "Gun racks": acc("This looks like a gun rack: a stand or wall rack that holds guns upright."),
    "Small arms lockers": acc("This looks like a gun locker: a locked cabinet for storing guns."),
    "Trigger locks": acc("This looks like a trigger lock: a lock fitted over a gun's trigger so it cannot be fired."),
    "Snap caps": acc("These look like snap caps: dummy cartridges with no powder or primer."),
    "Bore sighter": acc("This looks like a bore sighter: a tool used to line up a sight with a gun's barrel."),
}
# Category and file names that are not the accessory itself (or are military or people categories).
ACCESSORY_AVOID = re.compile(GUN_FILES.pattern + r"|\b(people|wearing|in use|in art|logos?|maps?|charts?|"
                                                 r"videos?|patents?)\b", re.I)


def build_commons_firearm_accessories(limit):
    """The commons_firearm_accessories pack (see the module docstring)."""
    return table_pack("commons_firearm_accessories", ACCESSORIES, limit, 5201, accessory_rows, ACCESSORY_AVOID)


# ----------------------------------------------------------------- (B) commons_firearm_kinds

def kind(answer):
    """One row of KINDS: (question, answer, depth 0, GUN_LINE)."""
    return (ASK_WHAT, answer, 0, GUN_LINE)


KINDS = {
    "Revolvers": kind("This looks like a revolver: a handgun with a turning cylinder that holds the cartridges."),
    "Pistols": kind("This looks like a pistol: a handgun."),
    "Semi-automatic pistols": kind("This looks like a semi-automatic pistol: a handgun that holds its cartridges in a "
                                   "magazine in the grip."),
    "Derringers": kind("This looks like a derringer: a very small pocket pistol."),
    "Percussion revolvers": kind("This looks like a percussion (cap-and-ball) revolver, an old kind of revolver."),
    "Flintlock pistols": kind("This looks like a flintlock pistol: an old kind of pistol, loaded from the muzzle."),
    "Flintlock muskets": kind("This looks like a flintlock musket: an old long gun, loaded from the muzzle."),
    "Muskets": kind("This looks like a musket: an old long gun, loaded from the muzzle."),
    "Shotguns": kind("This looks like a shotgun: a long gun that fires shells of small pellets."),
    "Double-barreled shotguns": kind("This looks like a double-barrelled shotgun: a shotgun with two barrels side by "
                                     "side or one over the other."),
    "Pump-action shotguns": kind("This looks like a pump-action shotgun: a shotgun with a sliding fore-end."),
    "Semi-automatic shotguns": kind("This looks like a semi-automatic shotgun."),
    "Rifles": kind("This looks like a rifle: a long gun with a grooved barrel."),
    "Bolt-action rifles": kind("This looks like a bolt-action rifle: a rifle with a bolt and handle on its side."),
    "Lever-action rifles": kind("This looks like a lever-action rifle: a rifle with a lever below the grip."),
    "Semi-automatic rifles": kind("This looks like a semi-automatic rifle."),
    "Single-shot rifles": kind("This looks like a single-shot rifle: a rifle that holds one cartridge at a time."),
    "Hunting rifles": kind("This looks like a hunting rifle."),
    "Air rifles": kind("This looks like an air rifle: a gun that fires pellets with compressed air, not gunpowder."),
    "Air pistols": kind("This looks like an air pistol: a handgun that fires pellets with compressed air, not "
                        "gunpowder."),
}
# The Commons categories of makers, by kind ("Smith & Wesson revolvers" -> a Smith & Wesson revolver).
MAKER_PARENTS = {"Pistols by manufacturer": "pistol", "Revolvers by manufacturer": "revolver",
                 "Rifles by manufacturer": "rifle", "Shotguns by manufacturer": "shotgun"}
# Maker category names that are not a maker's name and kind (a person's, a place's, a sentence).
NOT_A_MAKER = re.compile(r"'s\b|\bmade by\b|\b(wz|model|mod|army|navy)\b|\d", re.I)


def maker_answer(category, noun):
    """"This looks like a Smith & Wesson revolver." from a maker category's name ("Smith & Wesson revolvers",
    "Glock", "Harrington & Richardson Firearms"); "" when the name is not a maker's."""
    if NOT_A_MAKER.search(category):
        return ""
    brand = re.sub(r",?\s*(firearms|arms company|revolvers?|pistols?|rifles?|shotguns?|guns?)$", "", category.strip(),
                   flags=re.I).strip(" ,")
    if not brand or not label_ok(brand):
        return ""
    return f"This looks like {a_or_an(brand)} {brand} {noun}."


def maker_table(s):
    """{maker category: (question, answer, 0, GUN_LINE)} from the subcategories of MAKER_PARENTS."""
    from food_packs import commons_members
    out = {}
    for parent, noun in MAKER_PARENTS.items():
        try:
            subs = [c.split(":", 1)[-1] for c in commons_members(s, parent, "subcat")]
        except RuntimeError:
            continue
        for sub in subs:
            answer = maker_answer(sub, noun)
            if answer:
                out.setdefault(sub, kind(answer))
    return out


def build_commons_firearm_kinds(limit):
    """The commons_firearm_kinds pack (see the module docstring)."""
    table = dict(KINDS)
    table.update(maker_table(session()))
    say(f"  {len(table)} kind and maker categories")
    return table_pack("commons_firearm_kinds", table, limit, 5211, gun_rows, GUN_FILES)


# ----------------------------------------------------------------- (B) wikidata_firearms

def models_with_pictures(s):
    """[(item, Commons file title, kind phrase)]: Wikidata firearm models of FIREARM_KINDS (an item counted under its
    first kind) that have a picture (P18) but no Commons category (P373), leaving out the machine-gun and
    submachine-gun trees (FIREARM_AVOID)."""
    query = """SELECT DISTINCT ?item ?img WHERE {{ ?c wdt:P279* wd:{q} . ?item wdt:P279 ?c . ?item wdt:P18 ?img .
        FILTER NOT EXISTS {{ ?item wdt:P373 ?cat }} }}"""
    avoid = set()
    for q in FIREARM_AVOID:
        avoid.update(r["item"] for r in sparql(s, f"""SELECT DISTINCT ?item WHERE {{ ?c wdt:P279* wd:{q} .
            ?item wdt:P279 ?c . }}"""))
        time.sleep(1)
    out, taken = [], set(avoid)
    for q, phrase in FIREARM_KINDS:
        for r in sparql(s, query.format(q=q)):
            item = r["item"]
            if item.startswith("Q") and item not in taken:
                taken.add(item)
                title = "File:" + re.sub(r"%20|_", " ", r["img"].rsplit("/", 1)[-1])
                out.append((item, unquote(title), phrase))
        time.sleep(1)
    say(f"  Wikidata: {len(out)} firearm models with a picture and no Commons category")
    return out


def build_wikidata_firearms(limit):
    """The wikidata_firearms pack (see the module docstring)."""
    s, rng = session(), pass_random(5221)
    models = models_with_pictures(s)
    rng.shuffle(models)
    models = models[:int(limit * 1.4) + 2]
    facts = wd_model_facts(s, [m[0] for m in models])
    adjectives = demonyms(s, {o for f in facts.values() for o in f["origins"]})
    by_title = {}
    for item, title, phrase in models:
        if item in facts:
            answer = firearm_answer(item, facts[item], facts, phrase, adjectives)
            if answer:
                by_title.setdefault(title, (item, answer))
    items = []
    titles = list(by_title)
    for start in range(0, len(titles), 50):
        if listing_out_of_time():
            break
        try:
            files = commons_files(s, titles[start:start + 50])
        except RuntimeError as e:
            say(f"  {str(e)[:100]}")
            break
        for f in files:
            item, answer = by_title.get(f["title"], (None, None))
            if not item:
                continue
            if AI_TEXT.search(f["caption"]):
                f["caption"] = ""
            reason = gun_left_out(f)
            if reason:
                considered(f["title"], f["url"], reason)
                continue
            rows = [{"question": ASK_WHAT, "answer": with_line(answer, GUN_LINE), "credit": f["credit"],
                     "facts": {"wikidata": item}, **where(f["place"])}]
            if f["caption"] and not HOW_TO.search(f["caption"]):
                rows.append({"question": ASK_DESCRIBE, "answer": with_line(f["caption"], GUN_LINE),
                             "credit": f["credit"], "facts": {"wikidata": item}, **where(f["place"])})
            items.append((file_name("wd-firearm", f"{item}-{f['title'].split(':', 1)[-1].rsplit('.', 1)[0]}"),
                          f["url"], rows))
    say(f"  Wikidata firearms: {len(items)} free pictures")
    return finish("wikidata_firearms", items, limit, workers=2, pause=0.5)


DRUG_FIREARM_PACKS = {
    "commons_drugs": (build_commons_drugs,
                      "Wikimedia Commons categories of drugs (cannabis, cocaine, heroin, methamphetamine, ecstasy, "
                      "fentanyl, counterfeit medicines, seized drugs): each picture CC0, public domain or CC BY (each "
                      "author credited below); captions CC0 (Commons structured data)."),
    "commons_drug_paraphernalia": (build_commons_drug_paraphernalia,
                                   "Wikimedia Commons categories of bongs, pipes, hookahs, vapes, rolling papers, "
                                   "grinders and drug paraphernalia: each picture CC0, public domain or CC BY (each "
                                   "author credited below); captions CC0 (Commons structured data)."),
    "commons_cbp_seizures": (build_commons_cbp_seizures,
                             "US Customs and Border Protection photos of drug seizures, copied to Wikimedia Commons: "
                             "works of the US government, public domain (17 U.S.C. 105); each file's licence checked "
                             "on Commons (credited below)."),
    "cdc_phil_drugs": (build_cdc_phil_drugs,
                       "CDC Public Health Image Library (https://phil.cdc.gov): public-domain photos of drugs and "
                       "paraphernalia, with the CDC's captions (each item credited below)."),
    "commons_firearm_accessories": (build_commons_firearm_accessories,
                                    "Wikimedia Commons categories of firearm accessories (holsters, speedloaders, "
                                    "clips, scopes and sights, lights, lasers, slings, suppressors, cases, cleaning "
                                    "equipment, safes and locks): each picture CC0, public domain or CC BY (each "
                                    "author credited below); captions CC0."),
    "commons_firearm_kinds": (build_commons_firearm_kinds,
                              "Wikimedia Commons categories of firearm kinds and makers: each picture CC0, public "
                              "domain or CC BY (each author credited below); captions CC0."),
    "wikidata_firearms": (build_wikidata_firearms,
                          "Wikidata firearm models (data CC0) with their pictures from Wikimedia Commons: each picture "
                          "CC0, public domain or CC BY (each author credited below); captions CC0."),
}

# The limits of the workflow (pack-build.yml), from the sizes found in November 2026.
DRUG_FIREARM_LIMITS = {
    "commons_drugs": 800,                # 22 categories, about 1,100 files before the checks
    "commons_drug_paraphernalia": 1000,  # 11 categories, about 1,300 files before the checks
    "commons_cbp_seizures": 300,         # 202 CBP files whose title names a drug seizure (19 November 2026)
    "cdc_phil_drugs": 60,                # 43 PHIL photos found; 6 passed the checks in a test (19 November 2026)
    "commons_firearm_accessories": 1500, # 38 categories, about 4,500 files before the checks (most military lights)
    "commons_firearm_kinds": 2000,       # 20 kind and about 90 maker categories, their own files only
    "wikidata_firearms": 500,            # 441 models with a picture and no Commons category (many pictures BY-SA)
}


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try one drug or firearm pack builder.")
    parser.add_argument("key", choices=sorted(DRUG_FIREARM_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--categories", type=int, default=0, help="read only this many random categories")
    args = parser.parse_args(argv)
    global QUICK_CATEGORIES
    QUICK_CATEGORIES = args.categories
    entries = DRUG_FIREARM_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False))
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
