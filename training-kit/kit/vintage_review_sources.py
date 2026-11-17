"""REVIEW-ONLY picture collections of NON-SEXUAL NUDE PHOTOGRAPHS made before 1926 (at least 100 years old): figure
studies (academies) made for artists, Eadweard Muybridge's "Animal Locomotion" (1887) human motion plates,
historical medical photographs of adults, and early physical-culture photographs, for a private, local picture
describer used by a BLIND ADULT.

Why: a blind adult meets these pictures in books, museums and art classes and cannot otherwise know what they show.
The describer should say plainly what is there: who (a man, a woman), what they are doing, the pose and the setting.

Why only photographs made before 1926: the owner's attorney advises that for photographs of nude people where
consent is unclear, photographs over 100 years old are acceptable because the people shown are almost certainly no
longer living. That advice is about CONSENT ONLY. It does nothing about the risk that someone shown is under 18,
which is why the rules below are strict and why every picture is checked by a person before it is ever used.

Nothing here trains by itself. Each collection is downloaded into a "Describe pictures" workspace
(describe_package.py) where every picture arrives with a DRAFT description (made from the record's own title,
plate description and subject words) and the status "needs another look", never "described" or "checked". A
sighted, trusted adult screens every picture (REVIEW-INSTRUCTIONS.txt, written into the workspace), DELETES any
picture where the person might be under 18, any sexual picture and any degrading or non-consensual picture, corrects
the description, and marks "checked" only adult, non-sexual figure studies, motion studies or medical pictures.

HARD RULES kept by every fetch function here (vintage_screen() below; any one of them leaves a record out):
  - DATED BEFORE 1926. The record's own date is required; the LATEST year it allows counts ("ca. 1900-1930" or
    "192-" is too late; "19th century" is 1900 at the latest). A record without a date is left out.
  - ADULTS ONLY. Left out when the title, description, subject tags, plate notes or the series it belongs to mention
    or suggest a child or young person in any language (review_sources.CHILD, adult_review_sources.MINOR,
    and MINOR_MORE here: child, boy, girl, youth, adolescent, teen, juvenile, infant, baby, young,
    school, student, ephebe, doll and the same in Dutch, French, German, Italian, Spanish, Portuguese, Latin,
    Russian and Greek) or give an age under 18. A record must ALSO name an adult (ADULT: man, woman, adult, female
    or male model, athlete, wrestler, strongman, soldier, mother, father, an age of 18 or over, Muybridge's own
    "Model 95" numbering, a named adult such as Eugen Sandow ...). No adult word: left out.
  - NOTHING SEXUAL. Left out: anything described as erotic, obscene, pornographic, risque, lewd, glamour, boudoir,
    pin-up, burlesque, "French postcard", brothel or prostitution, lovers, kissing or embracing, and the genres
    "Erotica" and "Glamour photographs" (SEXUAL_WORDS). Photographers known for erotic studio photographs, or for
    nude photographs of adolescents, are left out by name (MAKERS_LEFT_OUT: von Gloeden, Pluschow, Galdi,
    F. Holland Day, Moulin, Belloc, Braquehais, d'Olivier, Agelou, Bellocq, Mandel, Otto Schmidt and others).
    Anonymous vintage erotic photography often shows minors and their age cannot be verified; the attorney's advice
    about consent does not change that.
  - NO COLONIAL "TYPE" OR ANTHROPOMETRIC PHOTOGRAPHS (COLONIAL). Ethnographic and anthropometric photographs of nude
    people ("native types", "anthropological study", measurement photographs, "Hottentot" and the like, and nude
    photographs labelled by a colonised people or place: "Algerian woman", "Zulu", "Moorish" ...) were usually taken
    without real consent and are degrading. They are left out by keywords and by the names of the collections that
    hold them (Pitt Rivers, Royal Anthropological Institute, Bureau of American Ethnology, Musee de l'Homme ...).
  - NO PEOPLE WHO COULD NOT REFUSE (NO_CONSENT): asylum and psychiatric patients, prisoners, enslaved people,
    "freak show" photographs, Charcot's "hysteria" photographs. Also no violence, wounds or death, no myths about
    rape, and no animals (adult_review_sources.VIOLENCE, MYTH, ANIMAL; a Muybridge rider on a horse is left out too).
  - NOT INTIMATE: a record about the genitals or breasts (a medical close-up) belongs with the "intimate" medical
    collections of review_sources.py and is left out here.
  - ABOUT NUDITY: the record must say the person is nude, naked, semi-nude or that it is an academy or figure study
    (NUDE_WORDS). A clothed Muybridge plate is simply not part of this collection.
  - PHOTOGRAPHS ONLY: a photograph of a painting, drawing or sculpture ("after a drawing", "process print after
    Rodin") is left out.
  - LICENCE: public domain (Public Domain Mark, "No Copyright - United States", "No known restrictions"), CC0 or
    CC BY, checked per item. CC BY-SA files are in the separate share-alike collection (commons_vintage_nudes_sa).
    Never NC or ND.
  When unsure, a record is left out.

How to use (for the kit's own code):
  VINTAGE_REVIEW_SOURCES  a list of plain dicts: key, name, category ("open" or "share-alike"), licence, terms,
                          terms_summary, credit, content ("nudity"), cap, download (size), fetch (a function
                          fetch_<key>(folder, cap, say)), plus "review_only": True.
  NOT_INCLUDED            sources looked at and left out, with the reason.
  Each fetch function downloads into folder (made into a describing workspace when it is not one yet), skips
  pictures already there or already tried, so a stopped run carries on where it was, and returns a plain summary
  with how many records each search found and how many passed the filters. Each also says up to five titles it
  left out, with the reason, so the filters can be seen working.

    python vintage_review_sources.py <key> <folder> [cap]      (a quick test of one collection)
    python vintage_review_sources.py count                      (how many records pass at each source; nothing
                                                                 is downloaded)

CONTENT TAG: "nudity" (sources.CONTENTS), used only when the person chooses "Include nudity"; describing.json also
says "never_for_picture_making": true: these pictures are never used to train picture-making.

PLUMBING the rest of the kit needs (not done here; other files are being edited by others):
  - wizard/describe_window.review_lists, kit/run_review.all_sources and kit/train.review_details: add
    ("vintage_review_sources", "VINTAGE_REVIEW_SOURCES", "vintage") beside the adult list, with the same guarded
    import (a missing or broken list is left out with a note).
  - .github/workflows/training-kit.yml: --hidden-import vintage_review_sources; tools/make_manifests.py: add the
    module to its list and a heading "Vintage nude photographs (review only)".
  - own_data.check_folder already uses only "checked" pictures from a workspace whose describing.json has
    "review_only": true.

Only requests and Pillow are needed (as for the rest of the kit). Nothing is sent anywhere except the downloads.
"""

import os
import re
import shutil
import time

import adult_review_sources as ar
import describe_package as dp
import review_sources as rs

CONTENT = "nudity"
LATEST_YEAR = 1925                        # made in this year or earlier: at least 100 years old (in 2026)
REVIEW_FILE = rs.REVIEW_FILE
CREDITS_FILE = rs.CREDITS_FILE
SHOW_LEFT_OUT = ar.SHOW_LEFT_OUT
clean, sentence, take_turns = ar.clean, rs.sentence, ar.take_turns

REVIEW_INSTRUCTIONS = """REVIEW-ONLY COLLECTION: {name}

These pictures are NON-SEXUAL NUDE PHOTOGRAPHS made before 1926: figure studies made for artists, Eadweard
Muybridge's motion studies, historical medical photographs and early physical-culture photographs. They were
collected so that a blind adult's private, local describer can say plainly and accurately what such a picture shows.
NONE of them is used for training until a person has checked it. They are never used to make pictures.

Why only old photographs: the people shown can no longer be asked for their consent, and the owner's legal advice is
that photographs over 100 years old are acceptable for that reason. That advice is about consent ONLY. It does not
make a picture of a young person acceptable. Age is the main thing you are checking.

This collection must be screened by a sighted, trusted ADULT.

For every picture:
1. DELETE the picture (do not just skip it) when anyone in it might be under 18. If you are not sure that everyone
   is an adult, delete it. Old records do not always say a model's age, and some old photographers used young
   models: judge from the picture, not from the record.
2. DELETE any picture that is sexual in any way: an erotic or "French postcard" style pose, a pose that shows off the
   genitals, anything that looks made to arouse rather than for artists, science or medicine.
3. DELETE any picture that seems degrading or taken without consent: colonial "native type" or measurement
   photographs, a person held or posed against their will, a patient in an asylum or a prisoner, a "freak show"
   photograph, or a person who looks distressed or humiliated.
4. DELETE any picture that is not a photograph of real people (a painting, drawing or statue), and any picture that
   is mainly a close-up of the genitals or breasts (those belong in the medical collections).
5. Read the draft description. It was made from the record's own title, plate description and subject words, and
   may be wrong or thin. Correct it so that it says plainly, accurately and without judgement who is there (how
   many adults, man or woman), what they are doing, the pose, what is visible and the setting. For a Muybridge plate,
   say how many frames there are and from which sides. Keep the date and the credit at the end.
6. Mark the picture "checked" ONLY when it is an adult, non-sexual figure study, motion study or medical picture
   and the description is accurate and plain.

Only checked pictures are ever trained on. Pictures that are new, described, skipped or need another look are
never used from this collection.

Where each picture comes from, its date and its licence are in CREDITS.txt and in each picture's notes.
Source: {credit}
Licence or terms: {licence}
"""

# ----------------------------------------------------------------- filters

# More words that mention or suggest a child or young person, beyond review_sources.CHILD and
# adult_review_sources.MINOR (more languages, and words such as "ephebe" and "doll").
MINOR_MORE = re.compile(
    r"\b(ephebe\w*|éphèbe\w*|efeb\w*|jüngling\w*|kinder\w*|knaben|garçonnet\w*|gamin\w*|adolescen\w*|"
    r"criança\w*|menin[oa]s?|rapaz\w*|puer|pueri|puella\w*|dolls?|cadets?|scouts?|nurser\w*|cradles?|cribs?|"
    r"school\w*|écol\w*|schul\w*|scuol\w*|escuel\w*|lyc[eé]\w*|gymnasiast\w*|"
    r"under ?age\w*|minderjährig\w*|mineur\w*|minorenn\w*|menor(es)? de edad|boyish|girlish|barely|"
    r"twinks?|femboys?|co-?eds?|college)\b|"
    r"(ребён|ребен|мальчи|девоч|дети|детск|подрост|παιδ|έφηβ|κορίτσ|αγόρ)", re.I)

# Words that name an adult. A record must have one (as well as passing every other rule).
ADULT = re.compile(
    r"\b(man|men|woman|women|adults?|gentlem[ae]n|lad(y|ies)|female models?|male models?|"
    r"model (no\.? ?)?\d+|athletes?|wrestlers?|boxers?|strong ?m[ae]n|bodybuilders?|weight-?lifters?|"
    r"soldiers?|sailors?|labou?rers?|blacksmiths?|mothers?|fathers?|wives|wife|husbands?|elderly|old (man|woman)|"
    r"middle-aged|femmes?|hommes?|frau(en)?|männer|mann|donna|donne|uomo|uomini|mujer(es)?|hombres?|vrouw(en)?)\b|"
    r"\b(E\. Muybridge|Eadweard Muybridge (himself|walking|ascending|throwing|running|lifting|sitting)|"
    r"Eugen Sandow|Sandow|Bernarr Macfadden|Macfadden)\b", re.I)

# Words that say the person is nude, or that the picture is an academy (a nude figure study made for artists).
NUDE_WORDS = re.compile(
    r"\b(nudes?|nudity|naked|unclothed|undraped|semi-?nude|half-?naked|nus?|nues?|nackt\w*|aktstudie\w*|akt|"
    r"naakt\w*|desnud\w*|nud[oaie]|académies?|academies?|academy figures?|figure stud(y|ies)|life stud(y|ies)|"
    r"étude de nu|pelvis cloth|loin ?cloths?|fig leaf)\b", re.I)

# Anything sexual, erotic or pornographic, and the genres of studio erotica (case does not matter).
SEXUAL_WORDS = re.compile(
    r"\b(erotic\w*|erotica|érotique\w*|erotisch\w*|erotismo|obscen\w*|pornogra\w*|porn\w*|risqu[eé]\w*|lewd\w*|"
    r"indecen\w*|licentious|lascivious|lubric\w*|smut\w*|salacious|naughty|saucy|sexy|sexual\w*|sexology|sex|"
    r"glamou?r\w*|boudoir|pin-?ups?|burlesque|cabaret|showgirls?|chorus girls?|bathing beaut\w*|"
    r"french postcards?|cartes? postales? (érotiques?|de charme)|postcards? de charme|stag|"
    r"brothels?|bordel\w*|prostitut\w*|courtesans?|harem\w*|odalisques?|demi-?mond\w*|storyville|"
    r"lovers?|love-?making|kiss\w*|embrac\w*|caress\w*|seduc\w*|sensual\w*|voluptu\w*|tempt\w*|"
    r"lingerie|stockings?|garters?|corsets?|negligee|déshabillé|"
    r"erect\w*|arous\w*|masturbat\w*|penis|phall\w*|coit\w*|intercourse|fellatio|cunnilingus|orgasm\w*)\b", re.I)

# Colonial ethnographic and anthropometric "type" photographs, and nude photographs labelled by a colonised people
# or place (left out: usually taken without real consent, and degrading). "Indian clubs" (an exercise) is allowed.
COLONIAL = re.compile(
    r"\b(ethnograph\w*|ethnolog\w*|anthropolog\w*|anthropometr\w*|anthropomètr\w*|craniometr\w*|bertillon\w*|"
    r"measur\w*|types?|racial|races of|natives?|indigenous|aborigin\w*|tribes?|tribal|savages?|primitive\w*|"
    r"hottentot\w*|bushm[ae]n|khoi\w*|venus hottentot|zulus?|kaffirs?|kafirs?|negro\w*|negress\w*|nègre\w*|"
    r"négresse\w*|mulatt\w*|colon(y|ies|ial\w*)|orient\w*|exotic\w*|"
    r"africa|african(?![- ]american)|algeri\w*|egypt\w*|moroc\w*|maroc\w*|tunis\w*|sudan\w*|congo\w*|nubia\w*|"
    r"abyssinia\w*|ethiopia\w*|senegal\w*|somali\w*|zanzibar|arabs?|arabian|moor\w*|mauresque\w*|ouled|kabyle\w*|"
    r"bedouin\w*|berber\w*|fellah\w*|india|hindu\w*|burm\w*|ceylon\w*|siam\w*|malay\w*|java\w*|bali\w*|"
    r"borneo|sumatra\w*|papua\w*|new guinea|melanesia\w*|polynesia\w*|samoa\w*|tahiti\w*|fiji\w*|hawaii\w*|"
    r"maori\w*|andaman\w*|ainu|philippin\w*|igorot\w*|filipin[oa]s?|eskimo\w*|inuit|sioux|apache\w*|"
    r"pitt rivers|royal anthropological|bureau of (american )?ethnology|musée de l'homme|musee de l'homme)\b|"
    r"\bIndians?\b(?! clubs?)", re.I)

# People who could not refuse: asylum and psychiatric patients, prisoners, enslaved people, "freak show" photographs.
NO_CONSENT = re.compile(
    r"\b(asylums?|lunatic\w*|insane|insanity|madness|madhouse|mental\w*|psychiatr\w*|idiot\w*|imbecil\w*|"
    r"cretin\w*|feeble-?minded|hysteri\w*|salp[eê]tri[eè]re|charcot|bethlem|bedlam|friern|hanwell|colney hatch|"
    r"prison\w*|convicts?|criminals?|inmates?|workhouse\w*|penitentiar\w*|enslaved|slaves?|slavery|"
    r"freaks?|sideshow\w*|side-show\w*|human exhibit\w*|exhibited as|human zoo\w*|captive\w*)\b", re.I)

# Photographers known for erotic studio photographs, or for nude photographs of adolescents or children: left out by
# name whatever a record says.
MAKERS_LEFT_OUT = re.compile(
    r"(gloeden|pl[uü]e?schow|galdi|holland day|d'agata|dodgson|lewis carroll|f[eé]lix[- ]jacques[- ]antoine moulin|"
    r"\bmoulin\b|belloc\b|braquehais|d'olivier|louis-camille|ag[eé]lou|bellocq|\bmandel\b|otto schmidt|"
    r"neue photographische gesellschaft|\bnpg\b|julia margaret cameron|alice boughton|heinrich k[uü]e?hn|"
    r"clarence h\.? white|manass[eé]|marcel meys|alexandre quinet)", re.I)

# A photograph of an artwork rather than of real people.
ART_COPY = re.compile(
    r"\b(of|after) (a |an |the )?(paintings?|drawings?|sculptures?|statues?|frescoe?s?|engravings?|etchings?|"
    r"watercolou?rs?|lithographs?|bronzes?|marbles?)\b|\bprocess print\b|\bphotomechanical print after\b|"
    r"\b(painting|sculpture|statue|drawing) by\b", re.I)


def year_of(text):
    """The LATEST year a record's date allows, or None when it gives no usable year: "1887" -> 1887,
    "[between 1890 and 1910?]" -> 1910, "192-" -> 1929, "19--" -> 1999, "late 19th century" -> 1900,
    "20th century" -> 2000. Taking the latest year means a picture only counts as old when it surely is."""
    text = clean(text)
    years = [int(y) for y in re.findall(r"(?<!\d)(1[6-9]\d\d|20[0-2]\d)(?!\d)", text)]
    years += [int(d) * 10 + 9 for d in re.findall(r"(?<!\d)(1[6-9]\d|20[0-2])-(?!\d)", text)]
    years += [int(c) * 100 + 99 for c in re.findall(r"(?<!\d)(1[6-9]|20)--", text)]
    years += [int(c) * 100 for c in re.findall(r"\b(1[6-9]|2[01])(?:st|nd|rd|th) century\b", text, re.I)]
    return max(years) if years else None


def vintage_screen(texts, date_text, maker="", need_nude=True):
    """"" when a record may be used; otherwise the plain reason it is left out. texts: the record's title,
    description, subject tags, notes and series (all are checked); date_text: the record's own date; maker: the
    photographer or creator (checked against MAKERS_LEFT_OUT). The order of the checks is the order of the rules in
    this module's docstring."""
    text = " ".join(clean(t) for t in texts if t)
    text = re.sub(r"\banimal (locomotion|movements?)\b", r"Muybridge \1", text, flags=re.I)  # the book's title
    year = year_of(date_text)
    if year is None:
        return "no date in the record (a date before 1926 is required)"
    if year > LATEST_YEAR:
        return f"may be from after {LATEST_YEAR} (the record's date allows {year})"
    for pattern in (rs.CHILD, ar.MINOR, MINOR_MORE):
        m = pattern.search(text)
        if m:
            return f"mentions or suggests a child or young person ('{m.group(0)}')"
    if any(a < 18 for a in rs.ages(text)):
        return "gives an age under 18"
    m = SEXUAL_WORDS.search(text)
    if m:
        return f"sexual, erotic or pornographic wording ('{m.group(0)}')"
    m = MAKERS_LEFT_OUT.search(f"{maker} {text}")
    if m:
        return f"a photographer known for erotic photographs or young models ('{m.group(0)}')"
    m = COLONIAL.search(text)
    if m:
        return f"a colonial ethnographic or 'type' photograph, or labelled by a colonised people ('{m.group(0)}')"
    m = NO_CONSENT.search(text)
    if m:
        return f"a person who could not refuse (asylum, prison, freak show ...) ('{m.group(0)}')"
    why = ar.screen(text)                             # violence, myths about rape, animals (and children again)
    if why:
        return why
    m = rs.GENITAL.search(text) or rs.BREAST.search(text)
    if m:
        return f"about the genitals or breasts (belongs to the intimate medical collections) ('{m.group(0)}')"
    m = ART_COPY.search(text)
    if m:
        return f"a photograph of an artwork, not of real people ('{m.group(0)}')"
    if not ADULT.search(text):
        return "no word in the record says the person is an adult (man, woman, adult model ...)"
    if need_nude and not NUDE_WORDS.search(text):
        return "the record does not say the person is nude (not part of this collection)"
    return ""


# Old catalogue words put in plain, respectful words (the meaning kept).
DATED_WORDS = [(re.compile(p, re.I), w) for p, w in [
    (r"\bcrippled\b", "disabled"), (r"\bcripples?\b", "disabled person"), (r"\bhandicapped persons\b", "disabled people"),
    (r"\bhandicapped\b", "disabled"), (r"\babnormal movements?\b", "movement affected by a condition"),
    (r"\.;", ";"), (r"\s+;", ";")]]


def draft(lead, said="", date="", credit=""):
    """A plain draft description: the lead and what the record says ("A plate from ...: a nude man walks."), then
    "Date: ..." and "Credit: ..."."""
    said = ar.plain(said).rstrip(". ")
    for old, new in DATED_WORDS:
        said = old.sub(new, said)
    if re.match(r"(A|An|Two|Three|Four) [a-z]", said):
        said = said[0].lower() + said[1:]               # "...(1887): a naked woman walking."
    parts = [sentence(f"{lead}: {said}" if said else lead)]
    if date:
        parts.append(f"Date: {clean(date).strip('[]')}.")
    if credit:
        parts.append(sentence(f"Credit: {credit}"))
    return " ".join(p for p in parts if p)


def muybridge_lead(plate=""):
    """ "A plate from Eadweard Muybridge's Animal Locomotion (1887)" (with the plate number when known)."""
    return "A plate from Eadweard Muybridge's Animal Locomotion (1887)" + (f", plate {plate}" if plate else "")


# ----------------------------------------------------------------- the review workspace

class VintageWorkspace(ar.AdultWorkspace):
    """The review workspace of a vintage nude collection: content "nudity", never for picture-making, these review
    instructions, CREDITS.txt with the date of each photograph, and left-out examples with the reason. Pictures arrive
    with the status "needs another look", never "described" or "checked"."""

    def __init__(self, folder, source, say=None):
        """Open (or make) the workspace and write the review instructions (not the adult collections' ones)."""
        rs.ReviewWorkspace.__init__(self, folder, source, say)
        self.left_out = []                       # (title, reason) examples, for the summary
        self.counts = {}                         # {search: [records found, records that passed]}
        self.workspace.data.update(content=CONTENT, never_for_picture_making=True, review_only=True,
                                   made_before=LATEST_YEAR + 1)
        self.workspace.save()
        with open(os.path.join(self.folder, REVIEW_FILE), "w", encoding="utf-8", newline="\r\n") as f:
            f.write(REVIEW_INSTRUCTIONS.format(name=source["name"], credit=source["credit"],
                                               licence=f"{source['licence']} ({source['terms_summary']})"))

    def tally(self, search, passed):
        """Count one record found by a search, and whether it passed the filters (for the summary)."""
        found = self.counts.setdefault(search, [0, 0])
        found[0] += 1
        found[1] += 1 if passed else 0

    def count_text(self):
        """"search: found N, passed M (P%)" for every search, in one line."""
        return "; ".join(f"'{q}': {n} found, {p} passed ({100 * p // n if n else 0}%)"
                         for q, (n, p) in self.counts.items())

    def flush(self):
        """Add the queued pictures, each with the status "needs another look", its date, credit, licence and source
        page in its notes and in CREDITS.txt."""
        if not self.waiting:
            self.save_tried()
            return
        files = [os.path.join(self.staging, n) for n, *_ in self.waiting]
        dp.add_pictures(self.workspace, files, person="")
        lines = []
        for item in self.waiting:
            name, credit, licence, page, content, note, date = item[:7]
            if self.workspace.pictures.get(name) is None:
                continue                                  # the same picture was there already
            self.workspace.entry(name).update(
                status=dp.LOOK, described_by="", described_at="", checked_by="", checked_at="",
                changed_at=dp.now(), content=content, review="review-only",
                notes=clean(f"REVIEW ONLY (vintage nude photograph, made before {LATEST_YEAR + 1}). Draft "
                            f"description from the record; a sighted, trusted adult must check it and delete it if "
                            f"anyone might be under 18 (see {REVIEW_FILE}). {note} Date: {date}. Credit: {credit}. "
                            f"Licence: {licence}. Source: {page}"))
            lines.append("\t".join([name, credit, licence, page, date]))
            self.added += 1
        self.workspace.save()
        with open(os.path.join(self.folder, CREDITS_FILE), "a", encoding="utf-8", newline="\r\n") as f:
            if f.tell() == 0:
                f.write(f"Credits for {self.source['name']}\nfile\tcredit\tlicence\tsource page\tdate\n")
            f.write("\n".join(lines) + ("\n" if lines else ""))
        shutil.rmtree(self.staging, ignore_errors=True)
        self.waiting = []
        self.save_tried()
        self.say(f"{self.source['name']}: {len(self.workspace.pictures)} pictures in the review workspace.")

    def finish(self, found, left):
        """Add what is queued; say the search counts and up to SHOW_LEFT_OUT left-out titles; give back a summary."""
        if self.counts:
            self.say(f"{self.source['name']}: {self.count_text()}")
        self.flush()
        if self.left_out:
            self.say("Left out, for example: " + "; ".join(f'"{t}" ({w})' for t, w in self.left_out[:SHOW_LEFT_OUT]))
        summary = (f"{self.source['name']}: {self.added} new pictures added for review "
                   f"({len(self.workspace.pictures)} in the workspace); {found} records looked at, {left} left out by "
                   f"the date, adults-only, non-sexual, consent and licence rules or because the picture could not be "
                   f"downloaded. Every picture needs a check by a sighted, trusted adult before it can be used "
                   f"(see {REVIEW_FILE}).")
        self.say(summary)
        return summary


def check(ws, search, name, title, texts, date, maker="", need_nude=True):
    """True when a record passes vintage_screen (counted for the search); otherwise it is remembered as left out."""
    why = vintage_screen(texts, date, maker, need_nude)
    ws.tally(search, not why)
    if why:
        ws.leave_out(name, title, why)
    return not why


def run(key, items_function, folder, cap, say, most=None):
    """Fill the review workspace of collection key: items_function(ws, s, most) gives (items, looked, left), where
    items are [(name, url, text, credit, licence, page, content, note, date)]; the pictures are downloaded until the
    workspace holds cap pictures (no cap: all of them, as in review_sources.fill). most: how many usable records to
    look for (default a little over twice cap)."""
    source = source_by_key(key)
    ws, s = VintageWorkspace(folder, source, say), rs.session()
    if most is None:
        most = cap * 2 + 10 if cap else 100000
    items, looked, left = items_function(ws, s, most)
    say(f"{source['name']}: {len(items)} usable records")
    left += rs.fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Boston Public Library (public domain)

BPL = "https://www.digitalcommonwealth.org/search.json"
BPL_COLLECTION = "Eadweard Muybridge's Animal Locomotion"
BPL_IIIF = "https://iiif.digitalcommonwealth.org/iiif/2/{}/full/1600,/0/default.jpg"
BPL_OPEN = ("No Copyright - United States", "No known copyright restrictions", "No known restrictions")


def bpl_items(ws, s, most):
    """Usable plates of the Boston Public Library's copy of Animal Locomotion (783 records, each with Muybridge's own
    plate description, the volume ("Vol. III. : Females (nude)") and subject words such as Women, Nudes, Walking)."""
    items, looked, left, page = [], 0, 0, 1
    while len(items) < most:
        data = rs.get_json(s, BPL, params={"f[collection_name_ssim][]": BPL_COLLECTION, "per_page": 100,
                                           "page": page})
        rows = (data or {}).get("data") or []
        for x in rows:
            a = x.get("attributes") or {}
            if a.get("curator_model_suffix_ssi") != "DigitalObject":
                continue
            looked += 1
            name = "bpl-" + re.sub(r"[^\w-]+", "_", x.get("id", "")) + ".jpg"
            title = clean(a.get("title_info_primary_tsi"))
            if ws.done(name):
                continue
            rights = clean(a.get("rightsstatement_ss")) + " " + clean(a.get("rights_ss"))
            if not any(r.lower() in rights.lower() for r in BPL_OPEN) or not a.get("exemplary_image_ssi"):
                ws.leave_out(name, title, "not marked public domain, or no picture")
                ws.tally("Animal Locomotion plates", False)
                left += 1
                continue
            subjects = [clean(t) for t in a.get("subject_topic_tsim") or []]
            abstract = clean(a.get("abstract_tsi"))
            series = clean(a.get("related_item_series_ssi"))
            date = " ".join(a.get("date_tsim") or []) or clean(a.get("date_start_dtsi"))[:4]
            texts = [title, abstract, " ".join(subjects), series]
            if not check(ws, "Animal Locomotion plates", name, f"{title}: {abstract}", texts, date,
                         " ".join(a.get("name_tsim") or [])):
                left += 1
                continue
            plate = (re.search(r"Plate (\d+)", title) or [None, ""])[1]
            who = ", ".join(t.lower() for t in subjects if t.lower() != "human locomotion")
            said = "; ".join(p for p in [f'Muybridge\'s own description: "{abstract.rstrip(".")}"' if abstract else "",
                                         f"the library's subject words: {who}" if who else ""] if p)
            text = draft(muybridge_lead(plate), said, "1887", "Boston Public Library, public domain")
            items.append((name, BPL_IIIF.format(a["exemplary_image_ssi"]), text,
                          f"{title}, Eadweard Muybridge, Boston Public Library Rare Books Department",
                          "public domain (No Copyright - United States)", clean(a.get("identifier_uri_ss")), CONTENT,
                          f"Volume: {series}." if series else "", "1887"))
        if len(rows) < 100:
            break
        page += 1
    return items, looked, left


def fetch_bpl_muybridge(folder, cap, say=print):
    """Boston Public Library: Eadweard Muybridge's Animal Locomotion (1887) plates of nude adult men and women,
    public domain ("No Copyright - United States"). The records give Muybridge's own plate descriptions and subject
    words (Women, Men, Nudes, Walking ...); plates of children, plates with a child word anywhere in the record or
    its volume title, and plates without an adult word are left out."""
    return run("bpl_muybridge", bpl_items, folder, cap, say)


# ----------------------------------------------------------------- Library of Congress (no known restrictions)

LOC = "https://www.loc.gov/photos/"
LOC_QUERIES = ("muybridge animal locomotion", "muybridge nude", "Sandow")
# A description part that only says what the object is ("1 photomechanical print : collotype.", "on cabinet card").
LOC_PHYSICAL = re.compile(r"^\d+ \w*\s?(print|photograph|negative|transparenc|slide)|^on (a )?cabinet card|"
                          r"^\d+ photomechanical", re.I)
# Catalogue subject words that say nothing about what a picture shows.
CATALOGUE_SUBJECTS = re.compile(r"^(motion study photographs|reproductions|book illustrations|collotypes|photography|"
                                r"human locomotion|animal locomotion|locomotion|cabinet photographs|portrait "
                                r"photographs|photographic prints|albumen prints|gelatin silver prints|literature|"
                                r"muybridge|amusements|recreation|[a-z]+, [a-z]+)$", re.I)


def loc_items(ws, s, most):
    """Usable Library of Congress photographs: Muybridge plates and Napoleon Sarony's photographs of the strongman
    Eugen Sandow (1893), with "No known restrictions on publication" only."""
    lists, looked, left = [], 0, 0
    for q in LOC_QUERIES:
        found, page = [], 1
        while len(found) < most and page <= 10:
            data = rs.get_json(s, LOC, params={"q": q, "fo": "json", "c": 100, "sp": page})
            rows = (data or {}).get("results") or []
            for x in rows:
                item = x.get("item") or {}
                looked += 1
                name = "loc-" + re.sub(r"[^\w-]+", "_", str(item.get("id") or x.get("id", ""))[-40:]) + ".jpg"
                title = clean(x.get("title"))
                if ws.done(name) or name in {i[0] for i in found}:
                    continue
                rights = clean(item.get("rights_advisory") or x.get("rights_advisory"))
                pictures = [u.split("#")[0] for u in x.get("image_url") or [] if u.split("#")[0].endswith(".jpg")]
                if not rights.lower().startswith("no known restrictions") or not pictures:
                    ws.leave_out(name, title, "rights not 'No known restrictions', or no picture")
                    ws.tally(q, False)
                    left += 1
                    continue
                parts = [clean(p) for d in x.get("description") or [] for p in str(d).split("|")]
                description = " ".join(re.sub(r"^Pl\. ?\d+\.? ?", "", p) for p in parts
                                       if p and not LOC_PHYSICAL.search(p))
                notes = [clean(n) for n in item.get("notes") or [] if not re.search(r"unverified|title from", n, re.I)]
                subjects = [clean(t) for t in x.get("subject") or []]
                date = clean(item.get("date") or x.get("date"))
                maker = " ".join(clean(c) for c in item.get("contributors") or x.get("contributor") or [])
                if not check(ws, q, name, f"{title} {description}"[:120], [title, description, " ".join(notes),
                                                                           " ".join(subjects)], date, maker):
                    left += 1
                    continue
                muybridge = "muybridge" in maker.lower()
                useful = [t for t in subjects if not CATALOGUE_SUBJECTS.search(t)]
                lead = muybridge_lead((re.search(r"\b(?:pl\.?|plate) ?(\d+)", title + " " + description, re.I)
                                       or [None, ""])[1]) if muybridge else "A photograph"
                said = "; ".join(p for p in [title if not muybridge else "", description,
                                             "the library's subject words: " + ", ".join(useful[:6])
                                             if useful else ""] if p)
                text = draft(lead, said, year_of(date) or date, "Library of Congress Prints and Photographs "
                                                                "Division, no known restrictions")
                found.append((name, pictures[-1], text, f"{title}, {maker or 'photographer not named'}, Library "
                              f"of Congress", "public domain (no known restrictions on publication)",
                              clean(x.get("id")), CONTENT, "", str(year_of(date) or date)))
            if len(rows) < 100:
                break
            page += 1
        lists.append(found)
    return take_turns(lists), looked, left


def fetch_loc_motion_studies(folder, cap, say=print):
    """Library of Congress: Muybridge's Animal Locomotion plates (1887) and Sarony's photographs of the strongman
    Eugen Sandow (1893), "No known restrictions on publication" only. Many LoC records give no more than "Animal
    locomotion", so only those whose description names an adult and says the person is nude are used."""
    return run("loc_motion_studies", loc_items, folder, cap, say)


# ----------------------------------------------------------------- Smithsonian (CC0)

SI = "https://api.si.edu/openaccess/api/v1.0/search"
SI_QUERIES = ('"animal locomotion" AND muybridge', '"physical culture" AND nude', "Sandow")


def si_items(ws, s, most):
    """Usable Smithsonian records (mostly the Smithsonian American Art Museum's Muybridge plates, whose titles and
    topics are good: "Woman Pouring a Basin of Water over Her Head", topic "Nudity"); CC0 pictures only. Needs a
    free api.data.gov key in SI_API_KEY (the shared DEMO_KEY allows only a few searches an hour)."""
    key = os.environ.get("SI_API_KEY") or "DEMO_KEY"
    lists, looked, left = [], 0, 0
    for q in SI_QUERIES:
        found, start = [], 0
        while len(found) < most and start < 3000:
            try:
                answer = s.get(SI, params={"q": f"{q} AND online_media_type:Images", "api_key": key, "rows": 100,
                                           "start": start}, timeout=90)
                data = answer.json() if answer.status_code == 200 else None
            except Exception:  # noqa: BLE001 - nothing found for this search
                answer, data = None, None
            if data is None or "response" not in data:
                ws.say("Smithsonian: no answer, or the API key's hourly limit is used up (the shared DEMO_KEY allows "
                       "very few searches). A free key from api.data.gov in SI_API_KEY gives more; a new run carries "
                       "on where it stopped.")
                break
            rows = data["response"].get("rows") or []
            for x in rows:
                looked += 1
                c = x.get("content") or {}
                dnr = c.get("descriptiveNonRepeating") or {}
                media = [m for m in ((dnr.get("online_media") or {}).get("media") or [])
                         if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"]
                name = "si-" + re.sub(r"[^\w.-]", "_", x.get("id") or "") + ".jpg"
                title = clean(x.get("title"))
                if ws.done(name):
                    continue
                if not media:
                    ws.leave_out(name, title, "no CC0 picture")
                    ws.tally(q, False)
                    left += 1
                    continue
                topics = [clean(t) for t in ((c.get("indexedStructured") or {}).get("topic") or [])]
                notes = " ".join(ar.si_text(c, "notes"))
                date = " ".join(ar.si_text(c, "date"))
                maker = " ".join(ar.si_text(c, "name"))
                if not check(ws, q, name, title, [title, notes, " ".join(topics), " ".join(ar.si_text(c, "setName"))],
                             date, maker):
                    left += 1
                    continue
                muybridge = "muybridge" in f"{maker} {title}".lower()
                useful = [t.lower() for t in topics if not CATALOGUE_SUBJECTS.search(t)]
                said = "; ".join(p for p in [re.sub(r",? from the book Animal Locomotion", "", title),
                                             rs.first_sentences(notes, 50, 2),
                                             "the museum's subject words: " + ", ".join(useful[:6]) if useful else ""]
                                 if p)
                text = draft(muybridge_lead() if muybridge else "A photograph", said, year_of(date) or date,
                             f"{dnr.get('data_source') or 'Smithsonian'}, CC0")
                found.append((name, media[0]["content"] + "&max=1600", text,
                              f"{title}, {maker or 'photographer not named'}, {dnr.get('data_source') or 'Smithsonian'}",
                              "CC0", clean(dnr.get("record_link")), CONTENT, "", str(year_of(date) or date)))
            if len(rows) < 100:
                break
            start += 100
            time.sleep(1)
        lists.append(found)
    return take_turns(lists), looked, left


def fetch_smithsonian_muybridge(folder, cap, say=print):
    """Smithsonian Open Access (CC0): Muybridge's Animal Locomotion plates (Smithsonian American Art Museum and the
    National Museum of American History) and physical-culture photographs. The NMAH plate records name only the
    plate number, so they are left out by the adult-word rule; the SAAM records describe each plate."""
    return run("smithsonian_muybridge", si_items, folder, cap, say)


# ----------------------------------------------------------------- Wellcome Collection (public domain, CC0, CC BY)

WELLCOME = "https://api.wellcomecollection.org/catalogue/v2/works"
WELLCOME_QUERIES = ("Muybridge naked", "Muybridge nude", "naked man photograph", "naked woman photograph",
                    "nude photograph", "physical culture photograph", "strongman photograph", "Sandow",
                    "academie photograph", "figure study photograph", "patient naked photograph")
WELLCOME_LICENCES = {"pdm": "public domain (Public Domain Mark)", "cc-0": "CC0", "cc-by": "CC BY 4.0"}
WELLCOME_PHOTO = re.compile(r"\b(photograph\w*|collotypes?|albumen|gelatin|motion study|cabinet card\w*|"
                            r"cartes? de visite|platinum print\w*|glass (plate )?negatives?|lantern slides?)\b", re.I)
WELLCOME_GENRES_LEFT_OUT = re.compile(r"\b(erotica|glamour|pornograph\w*|humorous|caricatures?|cartoons?)\b", re.I)
# Text that every Muybridge plate record carries ("... men, women, and children ..."): it is about the whole book,
# not the plate, so it is not read.
WELLCOME_BOOK_NOTE = re.compile(r"^One of 781 collotypes", re.I)


def wellcome_items(ws, s, most):
    """Usable Wellcome Collection photographs made before 1926 (Muybridge plates, physical culture, academies and
    adult medical photographs), Public Domain Mark, CC0 or CC BY only."""
    lists, looked, left = [], 0, 0
    for q in WELLCOME_QUERIES:
        found, page = [], 1
        while len(found) < most and page <= 10:
            data = rs.get_json(s, WELLCOME, params={"query": q, "pageSize": 100, "page": page, "workType": "k",
                                                    "include": "production,subjects,genres,notes,contributors",
                                                    "production.dates.to": f"{LATEST_YEAR}-12-31"})
            rows = (data or {}).get("results") or []
            for x in rows:
                looked += 1
                name = f"wellcome-{x.get('id')}.jpg"
                title = clean(x.get("title"))
                if ws.done(name) or name in {i[0] for i in found}:
                    continue
                thumb = x.get("thumbnail") or {}
                lic = (thumb.get("license") or {}).get("id", "")
                if lic not in WELLCOME_LICENCES or "/thumbs/" not in thumb.get("url", ""):
                    ws.leave_out(name, title, f"licence not open ({lic or 'none'}), or no picture")
                    ws.tally(q, False)
                    left += 1
                    continue
                genres = [clean(g.get("label")) for g in x.get("genres") or []]
                subjects = [clean(t.get("label")) for t in x.get("subjects") or []]
                notes = [clean(c) for n in x.get("notes") or [] for c in n.get("contents") or []
                         if not WELLCOME_BOOK_NOTE.search(clean(c))]
                makers = " ".join(clean((c.get("agent") or {}).get("label")) for c in x.get("contributors") or [])
                date = " ".join(clean(d.get("label")) for p in x.get("production") or [] for d in p.get("dates") or [])
                if WELLCOME_GENRES_LEFT_OUT.search(" ".join(genres)):
                    ws.leave_out(name, title, f"genre left out ({', '.join(genres)})")
                    ws.tally(q, False)
                    left += 1
                    continue
                if not WELLCOME_PHOTO.search(f"{title} {' '.join(genres)}"):
                    ws.leave_out(name, title, "not a photograph")
                    ws.tally(q, False)
                    left += 1
                    continue
                texts = [title, " ".join(subjects), " ".join(genres), " ".join(notes)]
                if not check(ws, q, name, title, texts, f"{date} {title}", makers):
                    left += 1
                    continue
                muybridge = "muybridge" in f"{title} {makers}".lower()
                said = re.sub(r"\.? ?(Collotype|Photograph\w*|Albumen print)\b.*$", "", title).strip()
                lead = muybridge_lead() if muybridge else "A historical photograph from the Wellcome Collection"
                text = draft(lead, said, year_of(f"{date} {title}"), f"Wellcome Collection, {WELLCOME_LICENCES[lic]}")
                url = thumb["url"].replace("/thumbs/", "/image/").replace("!200,200", "!1600,1600")
                found.append((name, url, text, f"{title}, Wellcome Collection", WELLCOME_LICENCES[lic],
                              f"https://wellcomecollection.org/works/{x.get('id')}", CONTENT,
                              ("Subjects: " + ", ".join(subjects) + ".") if subjects else "",
                              str(year_of(f"{date} {title}"))))
            if (data or {}).get("totalPages", 1) <= page:
                break
            page += 1
        lists.append(found)
    return take_turns(lists), looked, left


def fetch_wellcome_vintage_nudes(folder, cap, say=print):
    """Wellcome Collection: photographs made before 1926 of nude adults: Muybridge plates ("A naked woman walking.
    Collotype after Eadweard Muybridge, 1887."), physical culture and strongmen, academies, and adult medical
    photographs (H.W. Berend's orthopaedic photographs and the like). Public Domain Mark, CC0 or CC BY only;
    erotica, glamour and humorous genres, colonial and asylum photographs are left out."""
    return run("wellcome_vintage_nudes", wellcome_items, folder, cap, say)


# ----------------------------------------------------------------- Wikimedia Commons (licence per file)

# Category searches (Commons category names change; the search finds the current ones). Only the first few
# categories each search finds are read, one level of sub-categories deep, and only when their names pass the rules.
COMMONS_SEARCHES = ("Animal Locomotion Muybridge", "Muybridge human locomotion", "Eugen Sandow",
                    "Bernarr Macfadden", "Physical culture photographs", "Academic nude photographs 19th century",
                    "Nude photographs by Eugène Durieu")
COMMONS_CATEGORY_LEFT_OUT = re.compile(r"(erotic|porn|pin-?up|burlesque|glamour|boudoir|postcards|children|"
                                       r"boys|girls|kids|youth|infant|baby|school|ethnograph|anthropolog|types|"
                                       r"native|naturism in .*20\d\d|19[3-9]\d|20\d\d)", re.I)


def commons_categories(s, ws):
    """The Commons categories to read: for each search, the first 4 category hits whose names pass the rules, and
    their sub-categories one level deep."""
    found = []
    for q in COMMONS_SEARCHES:
        data = ar.commons_query(s, {"action": "query", "list": "search", "srsearch": q, "srnamespace": 14,
                                    "srlimit": 10}) or {}
        hits = [h["title"][9:] for h in (data.get("query") or {}).get("search", [])]
        kept = [h for h in hits if not COMMONS_CATEGORY_LEFT_OUT.search(h)][:4]
        for h in hits:
            if h not in kept and COMMONS_CATEGORY_LEFT_OUT.search(h):
                ws.leave_out("", f"Category:{h}", "a category about erotica, children, ethnography or a late date")
        for cat in kept:
            for sub in ar.commons_subcats(s, cat, 1, ws):
                if sub not in found and not COMMONS_CATEGORY_LEFT_OUT.search(sub):
                    found.append(sub)
    return found


def commons_items(kind):
    """An items function for Commons files of licence kind ("open" or "share-alike")."""
    def items_function(ws, s, most):
        """Usable Commons files of the categories commons_categories finds."""
        lists, looked, left = [], 0, 0
        for cat in commons_categories(s, ws):
            found = []
            for pageid, title, info in ar.commons_files(s, cat):
                name = f"commons-{pageid}.jpg"
                if ws.done(name) or any(name in {i[0] for i in x} for x in lists + [found]):
                    continue
                licence = ar.meta_value(info, "LicenseShortName")
                if rs.commons_licence_kind(licence) not in ("", kind):
                    continue                              # counted in the other licence's collection
                looked += 1
                stem = os.path.splitext(title)[0].replace("_", " ")
                description = ar.english_description(ar.meta_value(info, "ImageDescription"))
                categories = ar.meta_value(info, "Categories")
                date = ar.meta_value(info, "DateTimeOriginal")
                maker = ar.meta_value(info, "Artist")
                why = ""
                if not info.get("thumburl") or not info.get("mime", "").startswith("image/") or \
                        "svg" in info.get("mime", ""):
                    why = "not a photograph file"
                elif rs.commons_licence_kind(licence) != kind:
                    why = f"licence not open ({licence or 'none'})"
                elif ar.PROBLEM_CATEGORY.search(categories):
                    why = "in a deletion, copyright or identity-problem category"
                elif ar.DRAWN.search(f"{stem} {description}") and not re.search(r"photograph|collotype", description,
                                                                                  re.I):
                    why = "a drawing, print or painting, not a photograph"
                if why:
                    ws.leave_out(name, stem, why)
                    ws.tally(cat, False)
                    left += 1
                    continue
                if not check(ws, cat, name, stem, [stem, description, categories], date, maker):
                    left += 1
                    continue
                muybridge = "muybridge" in f"{stem} {maker} {categories}".lower()
                caption = rs.first_sentences(ar.plain(description) or ar.plain(stem), 60, 2)
                text = draft(muybridge_lead() if muybridge else "A photograph from Wikimedia Commons", caption,
                             year_of(date), f"{maker[:80] or 'unknown'}, via Wikimedia Commons, {licence}")
                found.append((name, info["thumburl"], text, f"{stem} by {maker[:120] or 'unknown'}, via Wikimedia "
                              f"Commons", licence, "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_"),
                              CONTENT, f"Commons category: {cat}.", str(year_of(date))))
                if len(found) >= most:
                    break
            if found:
                ws.say(f"Commons '{cat}': {len(found)} usable files")
            lists.append(found)
        return take_turns(lists), looked, left
    return items_function


def fetch_commons_vintage_nudes(folder, cap, say=print):
    """Wikimedia Commons (public domain, CC0 or CC BY, checked per file): Muybridge's human motion plates, Eugen
    Sandow and Bernarr Macfadden-era physical-culture photographs and academies, dated before 1926 by the file's own
    date (a file without a date is left out)."""
    return run("commons_vintage_nudes", commons_items("open"), folder, cap, say)


def fetch_commons_vintage_nudes_sa(folder, cap, say=print):
    """The same as fetch_commons_vintage_nudes, for CC BY-SA files (share-alike)."""
    return run("commons_vintage_nudes_sa", commons_items("share-alike"), folder, cap, say)


# ----------------------------------------------------------------- the collections

PD_SUMMARY = "public domain: free for any use; credit the library or museum"
VINTAGE_REVIEW_SOURCES = [
    dict(key="bpl_muybridge", name="Boston Public Library: Muybridge's Animal Locomotion, adult nude motion studies "
         "(1887, review only)", category="open",
         licence="Public domain (No Copyright - United States; checked per plate)",
         terms="https://www.digitalcommonwealth.org/collections/commonwealth:70795t73j", terms_summary=PD_SUMMARY,
         credit="Boston Public Library, Rare Books Department, Eadweard Muybridge, Animal Locomotion (1887)",
         content=CONTENT, cap=400, download="about 120 MB", fetch=fetch_bpl_muybridge, review_only=True),
    dict(key="loc_motion_studies", name="Library of Congress: Muybridge plates and Sandow photographs, adult nudes "
         "(before 1926, review only)", category="open",
         licence="Public domain (No known restrictions on publication; checked per item)",
         terms="https://www.loc.gov/free-to-use/", terms_summary=PD_SUMMARY,
         credit="Library of Congress Prints and Photographs Division", content=CONTENT, cap=200,
         download="about 30 MB", fetch=fetch_loc_motion_studies, review_only=True),
    dict(key="smithsonian_muybridge", name="Smithsonian: Muybridge plates and physical-culture photographs, adult "
         "nudes (before 1926, review only)", category="open", licence="CC0 (each picture's usage checked)",
         terms="https://www.si.edu/openaccess", terms_summary="CC0: free for any use; the API needs a free "
         "api.data.gov key (SI_API_KEY)", credit="Smithsonian Institution Open Access (Smithsonian American Art "
         "Museum and others), CC0", content=CONTENT, cap=200, download="about 30 MB",
         fetch=fetch_smithsonian_muybridge, review_only=True),
    dict(key="wellcome_vintage_nudes", name="Wellcome Collection: adult nude photographs before 1926 (Muybridge, "
         "physical culture, medical; review only)", category="open",
         licence="Public Domain Mark, CC0 or CC BY 4.0 (checked per picture)",
         terms="https://wellcomecollection.org/pages/Wvmu3yAAAIUQ4C7F",
         terms_summary="public domain, or CC BY: free to use with credit to the Wellcome Collection",
         credit="Wellcome Collection, public domain or CC BY 4.0", content=CONTENT, cap=400,
         download="about 80 MB", fetch=fetch_wellcome_vintage_nudes, review_only=True),
    dict(key="commons_vintage_nudes", name="Wikimedia Commons: adult nude motion studies, physical culture and "
         "academies before 1926 (review only)", category="open",
         licence="Public domain, CC0 or CC BY (each file's own licence and date checked)", terms=ar.COMMONS_TERMS,
         terms_summary="public domain, or free to use with credit to each author (in CREDITS.txt)",
         credit="Wikimedia Commons, public domain, CC0 or CC BY, credited in CREDITS.txt", content=CONTENT, cap=300,
         download="about 60 MB", fetch=fetch_commons_vintage_nudes, review_only=True),
    dict(key="commons_vintage_nudes_sa", name="Wikimedia Commons: adult nude motion studies, physical culture and "
         "academies before 1926, share-alike (review only)", category="share-alike",
         licence="CC BY-SA (each file's own licence and date checked)", terms=ar.COMMONS_TERMS,
         terms_summary="free to use with credit; anything shared that is made from them must be CC BY-SA",
         credit="Wikimedia Commons, CC BY-SA, credited in CREDITS.txt", content=CONTENT, cap=100,
         download="about 20 MB", fetch=fetch_commons_vintage_nudes_sa, review_only=True),
]


def source_by_key(key):
    """The VINTAGE_REVIEW_SOURCES entry with this key."""
    return next(s for s in VINTAGE_REVIEW_SOURCES if s["key"] == key)


# Sources looked at (November 2026) and not included, with the reason.
NOT_INCLUDED = {
    "National Library of Medicine Digital Collections (collections.nlm.nih.gov)": "not added: no open search API "
        "answered from the build machine (November 2026). Its public-domain historical medical photographs can be "
        "added later; some are also on Wikimedia Commons and are read by commons_vintage_nudes.",
    "University of Pennsylvania Archives, Muybridge collection": "not added: no search API; the same plates are read "
        "from the Boston Public Library, the Library of Congress, the Smithsonian, Wellcome and Commons.",
    "The Met's photographs (Department of Photographs, CC0)": "not added: tried in November 2026. Of 380 "
        "public-domain nude photographs found by 7 searches, 1 passed: the Met's titles are '[Female Nude]' or "
        "'[Nude Study]' with no adult word (the adult-word rule), several photographers are left out by name "
        "(Moulin, Braquehais, d'Olivier), and anonymous photographs are never used. Its Animal Locomotion items are "
        "whole books, not single plates.",
    "Anonymous vintage nude and erotic photographs ('French postcards', studio erotica, daguerreotype nudes)":
        "never used: they often show minors and their age cannot be verified. The attorney's advice about consent "
        "does not change that.",
    "Wilhelm von Gloeden, Wilhelm von Pluschow, Vincenzo Galdi, F. Holland Day and similar": "never used: their nude "
        "photographs often show adolescents. Left out by name (MAKERS_LEFT_OUT).",
    "Colonial ethnographic and anthropometric photographs (Pitt Rivers Museum, Royal Anthropological Institute, "
    "'native types')": "never used: usually taken without real consent, and degrading.",
    "Asylum and hospital photographs of psychiatric patients (Charcot's Salpetriere, Hugh Diamond and the like)":
        "never used: the people could not refuse.",
    "Early naturism (Freikorperkultur) photographs": "not searched on purpose: family naturism photographs very often "
        "include children. An adult naturism photograph found by the other searches is used only when its record "
        "names an adult and no child.",
}


# ----------------------------------------------------------------- quick tests

ITEMS = {"bpl_muybridge": bpl_items, "loc_motion_studies": loc_items, "smithsonian_muybridge": si_items,
         "wellcome_vintage_nudes": wellcome_items,
         "commons_vintage_nudes": commons_items("open"), "commons_vintage_nudes_sa": commons_items("share-alike")}


def count_all(folder, say=print, most=100000):
    """How many records pass at each source (nothing is downloaded): for each collection, the records looked at,
    the number usable and the pass rate per search. folder is a scratch folder for the workspaces' bookkeeping."""
    for key, items_function in ITEMS.items():
        try:
            ws = VintageWorkspace(os.path.join(folder, key), source_by_key(key), say)
            items, looked, left = items_function(ws, rs.session(), most)
            say(f"{key}: {looked} records looked at, {len(items)} usable "
                f"({100 * len(items) // looked if looked else 0}%). {ws.count_text()}")
        except Exception as e:  # noqa: BLE001 - one source failing does not stop the count
            say(f"{key}: could not be counted ({e})")


def main(argv):
    """Quick test: python vintage_review_sources.py <key> <folder> [cap], or count <folder>. Prints only titles,
    dates and drafts, never pictures."""
    if len(argv) >= 3 and argv[1] == "count":
        count_all(argv[2])
        return 0
    if len(argv) < 3:
        print("python vintage_review_sources.py <key> <folder> [cap]\n"
              "python vintage_review_sources.py count <folder>\nkeys: "
              + ", ".join(s["key"] for s in VINTAGE_REVIEW_SOURCES))
        return 1
    source = source_by_key(argv[1])
    source["fetch"](argv[2], int(argv[3]) if len(argv) > 3 else 5, print)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
