"""Pack builders for FINE-ART NUDITY and EROTIC ART (sexual acts between adults in art and illustration), used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)], where a row is {"question", "answer", "credit"} (plus "place" when the record says where the
work was made). A picture with more than one question comes once with its JPEG and then as (None, None, row) twins
pointing at it (food_packs.with_twins). The limit counts pictures.

Why: a blind adult meets nudes and erotic art in museums, books and on the web and cannot otherwise know what they
show. The describer should say it plainly and accurately, as a museum guide would: neither coy nor gratuitous. The
owner decided (November 2026) to bring back the museum works the other packs leave out, under the rules below. Both
packs are labelled collections, so a training can leave them out: the kit uses museum_art_nudes only with the "art
with nudity" choice and erotic_art only with the "adult sexual content" choice (which needs the nudity choice too),
and NEITHER is ever used for picture-making (training-kit/kit/sources.py NOT_FOR_PICTURE_MAKING and
PEOPLE_AND_BODILY_PACK_KEYS). Every erotic_art row also carries "content": "sexual".

The packs (ADULT_ART_PACKS):
  museum_art_nudes  Fine-art nudity that body_packs.art_nudes leaves out because its very wide word lists (MINOR,
                    SEXUAL) name a young person or something it counts as sexual: Madonna and Child, putti, cherubs
                    and Cupid, Venus and Cupid, nymphs and satyrs, Susanna, Bathsheba, Danae, odalisques, bathers,
                    lovers and kisses, classical statues of youths. Read from the same five museums as art_nudes
                    (body_packs met_items, aic_items, cma_items, nga_items, si_items: The Met's "Female Nudes" and
                    "Male Nudes" tags, the Art Institute of Chicago, the Cleveland Museum of Art, the National Gallery
                    of Art and the Smithsonian American Art Museum), with this pack's own screen (nudes_left_out)
                    instead of art_nudes's, so no work is in both packs. Asked "Describe this picture." and "Is there
                    nudity in this picture?" (body_packs.art_rows: the museum's own words, alt text where it has
                    it). Rows of works whose words name a child carry "child": true.
                    Left out (nudes_left_out): PHOTOGRAPHS (never a photograph in this pack, so never a photograph
                    of a nude child); any sexual act or erotica (SEX_ACT: those go to erotic_art's screen); sexual
                    violence and the stories that are about it (SEX_VIOLENCE: rape, abduction, Leda, Europa, the
                    Sabines, Lucretia, Ganymede ...); and ANY work whose words name a child or young person (MINOR)
                    TOGETHER with a sexual or romantic word (body_packs.SEXUAL: kiss, embrace, lovers, seduction,
                    nymphs, satyrs, courtesans ...); and any work whose nude subject is a REAL child or young person
                    (a girl, a boy, a youth, a son, students ...: real_young_person). The only children kept are
                    the owner's list, in plainly non-sexual works: the Christ Child and the infant Saint John, the
                    Holy Family, putti, cherubs, Cupid and angels (SACRED_OR_WINGED).
  erotic_art        Sexual acts and erotica in ART and ILLUSTRATION from open-access institution records: Japanese
                    shunga and Indian, Persian and Nepalese erotic paintings, Greek and Roman vases, European erotic
                    prints (The Met, the Art Institute of Chicago, the Cleveland Museum of Art), historical erotica
                    and sex-education pictures (the Wellcome Collection), and Wikimedia Commons categories of erotic
                    sculpture, reliefs, frescoes and pottery (Khajuraho, Konark, Pompeii, Greek and Moche pottery:
                    photographs OF ARTWORKS) and of drawings of sex positions, sex-education diagrams and Kama Sutra
                    illustrations (drawings only). Asked "Describe this picture." and "Is there sexual content in
                    this picture?".
                    FIRST: is the work sexual (an explicit act or an erotic scene, or rape or abduction: is_sexual)?
                    A work that is not is left out as "not about sex or erotica", never as a young-person exclusion;
                    if it shows nudity it is offered to museum_art_nudes (route_to_nudes), whose child rules apply.
                    THEN, for a sexual work, ADULTS ONLY: any young-person word (art_minor_word, whole words: child,
                    boy, girl (not "girlfriend", "chorus girl" ...), infant, baby, teen, adolescent, juvenile, a
                    minor, underage, schoolgirl, pupil, student, bare "young" or "youth", putto, cherub, Cupid, Eros,
                    Ganymede and the other youths of myth, virgin, apprentice, the Japanese youth words wakashu,
                    chigo, kagema, furisode, kamuro, shinzo, 若衆, 稚児 ...) or an age under 18 in figures or words.
                    GIRL OR BOY ONLY (the owner's decision): a sexual artwork whose ONLY young-person words are
                    girl(s), boy(s), lad or lass (older catalogue English for young women or men) is held for the
                    team's review instead (REVIEW): its title and catalogue link go on a review list written only on
                    the owner's own computer (ADULT_ART_REVIEW_LIST, or --review-list; never committed or published),
                    and it is kept only when packs/erotic_art_allow.txt allows it after a sighted person has looked
                    at the museum's page. Never for photographs, never with any clear minor word.
                    The adult phrases "young woman", "young man", "young couple", "maiden", "nymph" and "youthful"
                    do not count (the owner's decision, November 2026), EXCEPT in a Japanese work, where catalogues
                    often put wakashu and musume into English that way (there "young", "youth", "maid" and
                    "attendant" count too). Kinship words, "petit", "little", painting "schools" and "Asia Minor" do
                    not count; incest and parent-child pairings are left out on their own (INCEST). A sexual artwork
                    showing a minor stays out without exception. Also left out: killing, death, torture, execution,
                    suicide and private pictures (HARM); any animal or creature (no bestiality; Leda, Pasiphae);
                    records that are not an artwork; and every PHOTOGRAPH (photographs are training-kit/kit/
                    adult_photo_review.py's, on the owner's own computer, documented adults only).
                    KEPT AND SAID PLAINLY (the owner's decision): works of sexual violence and no consent (abduction
                    and rape themes, the Sabine women, Persephone, Lucretia, coercion, sleep or drunkenness, voyeurs)
                    and of restraint. theme_of adds a factual sentence ("It shows the abduction of Persephone
                    (Proserpina) by Hades (Pluto), who carried her off by force."; "the work depicts sexual violence,
                    not consent") and every row of such a work carries "theme": "sexual violence (artwork)", "no
                    consent (artwork)" or "restraint (artwork)", so the kit can leave them out
                    (train.py --without-sexual-violence).
                    Answers follow training-kit/HOW TO DESCRIBE SEXUAL CONTENT, NUDITY AND CONSENT.txt: plain
                    anatomical words, who does what, force or distress said factually, no judgement and no
                    titillation (PLAIN turns "obscene", "lewd", "lascivious", "sexy" into "explicit" or "sexual"),
                    and age said only when the record documents it.

Licences (packs/SOURCE-RULES.md, "open"; each item's own record is checked): The Met isPublicDomain (Open Access,
CC0); the Art Institute is_public_domain (its pictures of public-domain works and its data CC0); Cleveland
share_license_status CC0; the National Gallery of Art open access (CC0); the Smithsonian media usage CC0; the
Wellcome Collection licence pdm (Public Domain Mark), cc-0 or cc-by; Wikimedia Commons per file CC0, public domain or
CC BY (never SA, NC or ND). "Publicly viewable" is never enough: a record without one of these is left out.

The fixed sentences here were written for these packs; every other word of an answer is the institution's own
(title, maker, date, medium, description, subject tags), with catalogue and crude words put in plain adult English
(PLAIN), never written by an AI model.

    python packs/adult_art_packs.py erotic_art --limit 8      (prints a few rows and some left-out records)
"""

import os
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, first_sentences, LONG_SIDE, COMMONS_FREE
from food_packs import commons_get, commons_members, sentence
from service_packs import finish
from places import where, place_from_text
import body_packs
from body_packs import lead, made_in, MINOR, SEXUAL

DESCRIBE = "Describe this picture."
IS_SEXUAL = "Is there sexual content in this picture?"
SEXUAL_YES = "Yes. It is erotic art: the {owner}'s record files it among erotic or sexual works."
CONTENT = "sexual"

# What each screen left out and why (source, title, reason), for the quick check and the tests.
LEFT = []


def note(source, title, reason):
    """Remember that a record was left out and why (the first 2,000 only)."""
    if len(LEFT) < 2000:
        LEFT.append((source, clean(title)[:90], reason))


# ----------------------------------------------------------------- the word screens

# More words that name or may name a child or young person, beyond body_packs.MINOR: the kit's lists
# (training-kit/kit/review_sources.CHILD, adult_review_sources.MINOR) and the shunga and Edo words for youths,
# apprentices and young attendants (wakashu, chigo, kagema, furisode, kamuro, shinzo) in English and Japanese.
MINOR_MORE = re.compile(
    r"\b(wakash[uū]\w*|chigo|kagema|furisode|kamuro|shinz[oō]|iroko|tween\w*|nymphets?|lolita\w*|loli|shota\w*|"
    r"chibi|barely legal|underage|under-age|under 18|pubert\w*|prepubert\w*|p(a)?ediatric\w*|paediatr\w*|pupils?|"
    r"preschool\w*|apprentice\w*|novices?|page ?boys?|maids?|maidservants?|lass(ie)?s?|lads?|innocen\w*|little|"
    r"petite|uniforms?|kind|kinderen|knaap\w*|jonge|jugend\w*|joven\w*|nappy|nappies|diapers?|girlhood|boyhood|"
    r"adonis|endymion|attis|hylas|hyacinth\w*|narcissus|ganymed\w*|erastes|eromenos|pederast\w*|paederast\w*|"
    r"incest\w*)\b|"
    r"若衆|稚児|陰間|振袖|禿|新造|小姓|少年|少女|子供|子ども|こども|童|娘|幼|稚",
    re.I)
# An age in years ("a 16-year-old", "aged 15", "age: 14").
AGE = re.compile(r"\b(\d{1,3})[- ](?:year|yr)s?[- ]old\b|\baged (\d{1,3})\b|\b(\d{1,3}) ?(?:years?|yrs?) "
                 r"(?:of age|old)\b|\b(\d{1,3}) ?y/?o\b|\bage[: ]+(\d{1,3})\b", re.I)


# "Amorous" is an adult word that body_packs.MINOR's "amor..." (the Italian amorino, a little Cupid) would catch.
AMOROUS = re.compile(r"\bamorous(ly|ness)?\b", re.I)


def minor_word(text):
    """The first word of text that names or may name a child or young person ("" when none): body_packs.MINOR
    (child, boy, girl, infant, youth, young, adolescent, maiden, school, student, putto, cherub, Cupid, Eros,
    Madonna, son, daughter, family ...) and MINOR_MORE; an age under 18 counts too."""
    text = AMOROUS.sub(" ", text or "")
    found = MINOR.search(text) or MINOR_MORE.search(text)
    if found:
        return found.group(0)
    for m in AGE.finditer(text or ""):
        age = int(next(g for g in m.groups() if g))
        if age < 18:
            return m.group(0)
    return ""


# Sexual acts and erotica (a museum_art_nudes record with any of these is not a plain nude; in erotic_art they say
# what the record is about).
SEX_ACT = re.compile(
    r"\b(erotic\w*|erotica|erotisch\w*|érotique\w*|shunga|makura-?e|higa|spring (pictures?|prints?|palace)|"
    r"porn\w*|intercourse|coit\w*|copulat\w*|sex|sexual\w*|sexuality|sex acts?|love-?making|lovemaking|"
    r"making love|orgy|orgies|masturbat\w*|orgasm\w*|ejaculat\w*|erect|erections?|ithyphall\w*|phall\w*|"
    r"priap\w*|fellatio|cunnilingus|kama ?sutra|kamasutra|mithuna|maithuna|brothel\w*|bordello|lupanar|"
    r"fornicat\w*|aretino|i modi|amorous|carnal|lascivi\w*|lewd\w*|obscen\w*|bawdy)\b|"
    r"春画|枕絵|秘画|艶本|笑い絵|好色", re.I)
# Sexual violence and the stories that are about it (never shown, SOURCE-RULES.md), for museum_art_nudes.
SEX_VIOLENCE = re.compile(
    r"\b(rap(e|ed|es|ing|ist|ists)|ravish\w*|abduct\w*|kidnap\w*|assault\w*|violat\w*|forc(ed|ibly)|"
    r"captiv\w*|enslav\w*|slave\w*|verkracht\w*|vergewaltig\w*|enlèvement|stupro|violación)\b|"
    r"\b(Leda|Europa|Sabines?|Lucretia|Lucrece|Tarquin\w*|Ganymede|Pasipha[eë]|Proserpin\w*|Persephone|"
    r"Orithyia|Deianira|Nessus|Philomela|Tereus|Callisto|Antiope|Aegina|Io|Daphne|Syrinx|Arethusa)\b")

# Animals and creatures (the kit's adult_review_sources.ANIMAL, kept the same): never in erotic_art, so never
# bestiality (the octopus print, Leda's swan, Pan's goat, Europa's bull).
ANIMAL = re.compile(
    r"\b(animals?|beasts?|bestial\w*|zoophil\w*|horses?|stallions?|mares?|dogs?|swans?|bulls?|goats?|donkeys?|"
    r"octop\w*|tentacle\w*|monsters?|creatures?|demons?|kappa|foxe?s?|serpents?|snakes?|apes?|monkeys?|pigs?|"
    r"sheep|rabbits?|hares?|birds?|hens?|deer|stags?|interspecies|aliens?|hond\w*|paard\w*|dier\w*)\b|"
    r"蛸|タコ|河童|狐|犬|馬", re.I)

# A photograph (never in these packs: an old photograph of a nude or of sex is anonymous, and age cannot be known).
PHOTO_WORDS = re.compile(
    r"\b(photograph\w*|photos?|albumen|gelatin silver|silver gelatin|daguerreotype\w*|ambrotype\w*|tintype\w*|"
    r"carte(s)? de visite|cabinet card\w*|stereograph\w*|stereoview\w*|stereo card\w*|collodion|negatives?|"
    r"lantern slide\w*|glass plate\w*|platinum print|palladium print|cyanotype\w*|photogravure\w*|"
    r"chromogenic|inkjet print|pigment print|dye transfer|salted paper|calotype\w*|film still\w*|foto\w*|"
    r"photographie\w*|postcards?)\b", re.I)
# What an erotic_art museum record must be: an artwork (as adult_review_sources.ART_KIND).
ART_KIND = re.compile(
    r"\b(prints?|woodblock\w*|woodcut\w*|etching\w*|engraving\w*|lithograph\w*|mezzotint\w*|aquatint\w*|"
    r"drawing\w*|sketch\w*|paintings?|painted|watercolou?r\w*|gouache\w*|ink|oil on|tempera|fresco\w*|murals?|"
    r"sculpture\w*|statue\w*|statuette\w*|figure|figurine\w*|relief\w*|carv\w*|bronze|marble|terracotta|ivory|"
    r"ceramic\w*|porcelain|pottery|earthenware|stoneware|vessel\w*|vases?|bowls?|cups?|kylix|amphora\w*|"
    r"krater\w*|lekythos|netsuke|scrolls?|albums?|folio\w*|leaf|leaves|miniature\w*|illustration\w*|"
    r"illuminat\w*|manuscript\w*|book|books|ehon|shunga|surimono|kakemono|tile|textile|embroider\w*|lacquer\w*|"
    r"plaque\w*|medal\w*|coin|gem|cameo\w*|intaglio|lamp|oil lamp|mirror|tsuba|inro|panel|box|boxes|"
    r"plates?|dish(es)?|jars?|snuff ?box\w*)\b", re.I)
# What an erotic_art record must be about (so that "erotic" deep in an essay on a landscape does not count).
TOPIC = re.compile(SEX_ACT.pattern + r"|\b(nude couples?|couple embracing|embracing couple|lovers)\b", re.I)
# Phrases that look on topic but are not ("Art Lovers", the Indian "Shunga period").
NOT_TOPIC = re.compile(r"\b(art|music|nature|book|wine|dog|cat|horse|garden|opera|theatre|theater) lovers\b|"
                       r"\blovers of\b|\bshunga (period|dynasty|empire|kingdom)\b|\bsex(ual)? education\b(?! "
                       r"(diagram|drawing|illustration))", re.I)
# Religious symbols that are not pictures of people.
SYMBOL = re.compile(r"\b(linga\w*|lingam\w*|yoni|shivling\w*|shiva ?linga\w*)\b", re.I)


def nudes_left_out(source, title, *texts, kind="", routed=False):
    """True when a museum record is NOT for museum_art_nudes (the reason noted in LEFT): it is art_nudes's (neither
    body_packs.MINOR nor body_packs.SEXUAL names anything), a photograph, a sexual act or erotica, sexual violence,
    or a child or young person together with a sexual or romantic word. A kept record whose words name a child is
    remembered in CHILD_TITLES (its rows get "child": true). routed=True for a work found by the erotic searches
    (route_to_nudes), which is not art_nudes's whatever its words."""
    text = " ".join(clean(t) for t in (title, *texts) if t)
    minor, wide = minor_word(text), SEXUAL.search(text)
    reason = ""
    if not MINOR.search(text) and not wide and not routed:
        reason = "in art_nudes already"           # (a work routed from the erotic searches is not art_nudes's)
    elif PHOTO_WORDS.search(f"{clean(kind)} {clean(title)}"):
        reason = "a photograph (this pack has none)"
    elif SEX_ACT.search(text):
        reason = f"sexual act or erotica: {SEX_ACT.search(text).group(0)}"
    elif SEX_VIOLENCE.search(text):
        reason = f"sexual violence or its story: {SEX_VIOLENCE.search(text).group(0)}"
    elif minor and wide:
        reason = f"a young person ({minor}) with a sexual or romantic word ({wide.group(0)})"
    elif minor and real_young_person(text):
        reason = f"a real child or young person as the nude subject ({real_young_person(text)})"
    if reason:
        if reason != "in art_nudes already":
            note(source, title, reason)
        return True
    if minor:
        CHILD_TITLES.add(clean(title).rstrip("."))
    return False


CHILD_TITLES = set()

# The only children museum_art_nudes keeps (the owner's list): the Christ Child with the Madonna, the infant Saint
# John, the Holy Family, putti, cherubs, Cupid and other winged child figures, and angels. A generic child word
# ("child", "infant", "baby", "children") is taken as one of them only when one of them is named too.
SACRED_OR_WINGED = re.compile(
    r"\b((Madonna|Virgin|Mary)( and| with)( the)? (Child|Infant)\w*|Christ Child|Child Jesus|Infants? (Christ|Jesus|"
    r"Saint John|St\.? John)\w*|Holy Family|Madonna\w*|Virgin|Nativity|Christ|Jesus|Saint John|St\.? John|"
    r"put(to|ti|ten|tini)|cupids?|amor(ino|ini|etto|etti)|amoretti|cherub\w*|angel\w*|seraph\w*|genius|genii|"
    r"bambino|bambin\w*|enfant J[ée]sus|Christkind\w*|Jesuskind\w*|kindeke)\b", re.I)
GENERIC_CHILD = re.compile(r"\b(child(ren)?|infants?|bab(y|ies)|kids?)\b", re.I)


def real_young_person(text):
    """The first word of a nude work's text that names a REAL child or young person as its subject (a girl, a boy,
    a youth, a son, students ...), not one of the sacred or winged figures museum_art_nudes may keep (SACRED_OR_
    WINGED); a generic child word counts unless such a figure is named. "" when none."""
    rest = SACRED_OR_WINGED.sub(" ", text)
    if SACRED_OR_WINGED.search(text):
        rest = GENERIC_CHILD.sub(" ", rest)
    return minor_word(rest)


# Works from Japan, where catalogues often put the shunga words for youths into English as "young man" (wakashu)
# or "young woman" (musume): in them, adult-sounding "young" phrases still leave a work out.
JAPANESE = re.compile(r"\b(shunga|ukiyo-?e|japan\w*|edo|meiji|makura-?e|higa|ehon|harunobu|utamaro|hokusai|"
                      r"kuniyoshi|toyokuni|kunisada|moronobu|eisen|kory[uū]sai|kiyonaga|shunch[oō]|sukenobu|"
                      r"shunsh[oō]|eishi|sugimura|okumura|torii)\b|[\u3040-\u30ff\u4e00-\u9fff]", re.I)
# Adult phrases that do not leave an ARTWORK out (the owner's decision, November 2026): they mostly describe adults.
ADULT_PHRASES = re.compile(r"\b(young (wom[ae]n|m[ae]n|couples?|lad(y|ies)|wi(fe|ves)|husbands?|lovers?)|"
                           r"maidens?|nymphs?|youthful)\b", re.I)


# The young-person words of a SEXUAL artwork (whole words only; the coordinator's sample of the first list, November
# 2026, showed kinship words, "petit", "little", painting "schools", "Asia Minor" and names such as "Virginia"
# catching works that are neither sexual nor about minors). Kept, without exception: child, children, boy(s),
# girl(s) (adult phrases such as "girlfriend" or "chorus girl" excepted), infant, baby, toddler, teen, adolescent,
# juvenile, puberty, a minor or minors, underage, schoolgirl, schoolboy, school pupil, pupil, student, school
# uniform, ages under 18, the Japanese youth words, putto, cherub, Cupid, Eros, Ganymede and the other youths of
# myth, virgin; and bare "young" or "youth" (only the adult phrases of ADULT_PHRASES are rescued).
SEX_MINOR = re.compile(
    r"\b(child|children|childhood|childlike|kids?|boys?|boyhood|boyish|girls?|girlhood|girlish|infants?|infancy|"
    r"bab(y|ies)|toddlers?|newborns?|teen|teens|teenage\w*|teenager\w*|adolescen\w*|juvenile\w*|pubert\w*|"
    r"pubescen\w*|prepubescen\w*|minors|underage|under-age|under 18|schoolgirls?|schoolboys?|school ?(girls?|boys?|"
    r"pupils?|children|uniforms?)|pupils?|students?|young|youngsters?|youths?|lads?|lass(ie)?s?|nymphets?|"
    r"lolita\w*|loli|shota\w*|barely legal|put(to|ti|tini)|cherub\w*|cupids?|amor(ino|ini|etto|etti)|amoretti|"
    r"eros|erotes|ganymed\w*|hylas|hyacinth(us)?|narcissus|endymion|adonis|attis|kouros|kouroi|ephebe\w*|"
    r"virgins?|apprentices?|wakash[uū]|chigo|kagema|furisode|kamuro|shinz[oō]|iroko|musume|enfant\w*|"
    r"fillette\w*|gar[cç]on\w*|ragazz\w*|fanciull\w*|bambin\w*|ni[nñ][oa]s?|muchach\w*|m[aä]dchen|"
    r"knabe\w*|kinder|kindje\w*|meisje\w*|jongen\w*|knaap\w*|puer|pueri|puella\w*|jeune\w*)\b|"
    r"\b(a|the|any) minor\b(?! (arts?|keys?|gods?|godd?ess\w*|deit\w*|planets?|prophets?|orders?|damage|"
    r"repairs?|role|figure))|"
    r"若衆|稚児|陰間|振袖|禿|新造|小姓|少年|少女|子供|子ども|こども|童|娘|幼|稚", re.I)
# Adult phrases with "girl" (not a child).
GIRL_ADULT = re.compile(r"\b(girlfriends?|call ?girls?|show ?girls?|chorus ?girls?|cover ?girls?|pin-?up ?girls?|"
                        r"working ?girls?|dancing ?girls?|bar ?girls?)\b", re.I)
# In a Japanese work, the words catalogues use in English for wakashu, musume or young attendants also count.
JAPANESE_MINOR = re.compile(r"\b(young\w*|youth\w*|maids?|maidservants?|attendants?|little|petite?)\b", re.I)
JAPANESE_COUPLE = re.compile(r"\byoung couples?\b", re.I)
# Ages in words under 18 ("fifteen years old", "aged sixteen").
AGE_WORDS = re.compile(r"\b(aged |age )?(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
                       r"fourteen|fifteen|sixteen|seventeen)[- ](years?[- ]old|year-old)\b|\baged (one|two|three|"
                       r"four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
                       r"seventeen)\b", re.I)
# Incest, parent-child pairings and families in a sexual work (left out: the kinship words no longer count as
# young-person words, so these are named here; a family in a sexual series may include a child the record does not
# name, such as "The Satyr's Family").
INCEST = re.compile(r"\b(incest\w*|father and daughters?|mother and sons?|brother and sisters?|sister and "
                    r"brothers?|his daughters?|her sons?|Amnon|famil(y|ies)|famille|familie)\b|\bLot\b", re.I)


def art_minor_word(text):
    """The young-person word of a SEXUAL artwork ("" when none): SEX_MINOR on the text without the adult phrases
    (ADULT_PHRASES: "young woman", "maiden", "nymph", "youthful" ...; GIRL_ADULT: "girlfriend", "chorus girl" ...);
    in a Japanese work (JAPANESE) the adult phrases are not rescued and JAPANESE_MINOR counts too; ages under 18 in
    figures or words."""
    return ", ".join(art_minor_words(text))


def art_minor_words(text):
    """Every young-person word of a sexual artwork's text (see art_minor_word), in order, each once."""
    japanese = bool(JAPANESE.search(text))
    # In a Japanese work "young couple" alone is rescued (the owner's decision); "young man" or "young woman" on its
    # own, and every youth word, still count.
    rest = GIRL_ADULT.sub(" ", JAPANESE_COUPLE.sub(" ", text) if japanese else ADULT_PHRASES.sub(" ", text))
    found = [m.group(0) for pattern in (SEX_MINOR, JAPANESE_MINOR if japanese else None, AGE_WORDS) if pattern
             for m in pattern.finditer(rest)]
    found += [m.group(0) for m in AGE.finditer(rest) if int(next(g for g in m.groups() if g)) < 18]
    return list(dict.fromkeys(found))


# In older catalogue English "girl(s)", "boy(s)", "lad" and "lass" often mean young women or men. A sexual ARTWORK
# whose ONLY young-person words are these goes to a review list instead of being dropped silently; the owner's
# sighted team looks at the museum's own page and may allow it (erotic_art_allow.txt). Never for photographs.
AMBIGUOUS_YOUNG = re.compile(r"^(girls?|boys?|lads?|lass(ie)?s?)$", re.I)
REVIEW = "for review: its only young-person word may mean a young adult in older English"


# A girl or boy WATCHING a sexual scene is a child in a sexual scene, not a young adult taking part: never reviewed.
ONLOOKER = re.compile(r"\b(girls?|boys?|lads?|lass(ie)?s?)\b[^.;]{0,40}\b(looks? on|looking on|watch\w*|peep\w*|"
                      r"spy\w*|spies|observ\w*|sees|seeing|onlookers?)\b|\b(watched|observed|seen|spied on) by "
                      r"(an? |the |two |three )?(young )?(girls?|boys?|lads?|lass(ie)?s?)\b", re.I)


def only_ambiguous(words, text=""):
    """True when every young-person word found is girl(s), boy(s), lad or lass, and no girl or boy is watching."""
    return bool(words) and all(AMBIGUOUS_YOUNG.match(w) for w in words) and not ONLOOKER.search(text)


# The myths whose art shows sex with an animal (Leda and the swan, Pasiphae and the bull): left out like ANIMAL.
ANIMAL_MYTH = re.compile(r"\b(Leda|Pasipha[eë])\b")
# Never shown, whatever the theme: killing, death, wounds, torture, execution and suicide (graphic harm), and
# private or leaked pictures.
HARM = re.compile(r"\b(murder\w*|kill\w*|death|dead|dying|corpses?|blood\w*|wound\w*|tortur\w*|executions?|"
                  r"beheaded|severed|martyr\w*|crucif\w*|sacrific\w*|suicide|wars?|battles?|leak\w*|revenge|"
                  r"stolen|hacked|hidden cameras?|upskirt\w*)\b", re.I)

# The themes an erotic artwork may show, said plainly in its answer and kept in its rows' "theme" (the kit can leave
# them out: train.py --without-sexual-violence). FORCE: sexual violence; NO_CONSENT: someone who cannot consent or
# is watched in secret; RESTRAINT: restraint or striking.
THEME_FORCE = "sexual violence (artwork)"
THEME_NO_CONSENT = "no consent (artwork)"
THEME_RESTRAINT = "restraint (artwork)"
FORCE = re.compile(r"\b(rap(e|ed|es|ing|ist|ists)|ravish\w*|abduct\w*|kidnap\w*|assault\w*|violen\w*|"
                   r"forc(es|ed|ibly|ing)|coerc\w*|captiv\w*|slave\w*|prisoners?|against (her|his|their) will|"
                   r"resist\w*|struggl\w*|weapons?|swords?|daggers?|knife|verkracht\w*|ontvoer\w*|geweld\w*|"
                   r"vergewaltig\w*|enlèvement|stupro|violación)\b", re.I)
NO_CONSENT = re.compile(r"\b(sleep\w*|asleep|drunk\w*|intoxica\w*|unconscious|drugged|voyeur\w*|peep\w*|"
                        r"spy\w*|spying|surprised|unaware|without (her|his|their) (consent|knowledge)|in public|"
                        r"public sex|exhibitionis\w*)\b", re.I)
RESTRAINT = re.compile(r"\b(whip\w*|flagell\w*|beat(ing|en)|sadis\w*|masochis\w*|bdsm|bondage|shibari|bound|"
                       r"tied|ropes?|chain(ed|s)?|gag(ged|s)?|spank\w*|punish\w*|chastis\w*|humiliat\w*|"
                       r"discipline|dominatri\w*|femdom)\b", re.I)
# The stories of force or no consent that art tells, each said plainly (written for this pack; case matters).
MYTH_FACTS = [
    (r"Sabines?", THEME_FORCE, "It shows the abduction of the Sabine women, the Roman legend in which Roman men "
                               "carried off women by force."),
    (r"Proserpin\w*|Persephone|Pluto|Hades", THEME_FORCE, "It shows the abduction of Persephone (Proserpina) by "
                                                         "Hades (Pluto), who carried her off by force."),
    (r"Europa", THEME_FORCE, "It shows the abduction of Europa by Zeus (Jupiter)."),
    (r"Lucretia|Lucrece|Tarquin\w*", THEME_FORCE, "It shows the story of Lucretia, who was raped by Tarquin."),
    (r"Orithyia|Boreas", THEME_FORCE, "It shows the abduction of Orithyia by Boreas, the north wind."),
    (r"Deianira|Nessus", THEME_FORCE, "It shows the centaur Nessus carrying off Deianira by force."),
    (r"Philomela|Tereus", THEME_FORCE, "It shows the story of Philomela, who was raped by Tereus."),
    (r"Callisto", THEME_FORCE, "It shows the story of Callisto, whom Zeus (Jupiter) forced himself on."),
    (r"Cassandra|Ajax", THEME_FORCE, "It shows the rape of Cassandra by Ajax."),
    (r"Lapiths?|Centaurs?", THEME_FORCE, "It shows the centaurs trying to carry off the Lapith women by force."),
    (r"Potiphar\w*", THEME_FORCE, "It shows Potiphar's wife trying to force herself on Joseph."),
    (r"Dinah", THEME_FORCE, "It shows the story of Dinah, who was raped by Shechem."),
    (r"Daphne|Syrinx|Arethusa", THEME_FORCE, "It shows a nymph fleeing a god who pursues her."),
    (r"Io|Aegina|Antiope", THEME_FORCE, "It shows a woman pursued by Zeus (Jupiter)."),
    (r"Susann?ah?", THEME_NO_CONSENT, "It shows Susanna, spied on and threatened by two elders."),
    (r"Bathsheba", THEME_NO_CONSENT, "It shows Bathsheba bathing, watched in secret by a king."),
]
MYTH_FACTS = [(re.compile(rf"\b({p})\b"), theme, said) for p, theme, said in MYTH_FACTS]


def theme_of(text):
    """(theme, plain sentence) of an erotic artwork's words, or ("", ""): a story of force or no consent
    (MYTH_FACTS), else force, no consent or restraint words, said factually and without eroticising."""
    for pattern, theme, said in MYTH_FACTS:
        if pattern.search(text):
            return theme, said
    for pattern, theme, said in (
            (FORCE, THEME_FORCE, "The record's words name force (\"{w}\"): the work depicts sexual violence, not "
                                 "consent."),
            (NO_CONSENT, THEME_NO_CONSENT, "The record's words say \"{w}\": a person in it cannot consent, or is "
                                           "watched without consent."),
            (RESTRAINT, THEME_RESTRAINT, "The record's words name restraint or striking (\"{w}\").")):
        m = pattern.search(text)
        if m:
            return theme, said.format(w=m.group(0))
    return "", ""


# Words and stories of SEXUAL violence (rape, abduction and the force myths of MYTH_FACTS): a work naming them is
# sexual. Sleep, watching, restraint or a weapon alone are not (a "Sleeping Venus" is a nude, not erotica).
SEXUAL_FORCE = re.compile(r"\b(rap(e|ed|es|ing|ist|ists)|ravish\w*|abduct\w*|kidnap\w*|verkracht\w*|ontvoer\w*|"
                          r"vergewaltig\w*|enlèvement|stupro|violación)\b", re.I)


def is_sexual(text):
    """True when an artwork's words say it is sexual: an explicit act or an erotic scene (TOPIC), or sexual
    violence (SEXUAL_FORCE, or a force story of MYTH_FACTS)."""
    if TOPIC.search(NOT_TOPIC.sub(" ", text)) or SEXUAL_FORCE.search(text):
        return True
    return any(theme == THEME_FORCE and pattern.search(text) for pattern, theme, _ in MYTH_FACTS)


NOT_SEXUAL = "not about sex or erotica"


def erotic_left_out(*texts, kind="", title="", need_topic=True, need_art=True):
    """The reason an erotic_art record is left out, or "" when it may be used. FIRST whether it is sexual
    (is_sexual; need_topic=False for a Commons category of erotic art, which is sexual by being there): a record
    that is not is left out as NOT_SEXUAL and is never counted as a young-person exclusion (its nudity, if any, may
    go to museum_art_nudes: route_to_nudes). Then, for a sexual work: a young-person word or an age under 18
    (art_minor_word); incest; killing, death, torture or private pictures (HARM); an animal or creature (no
    bestiality); a religious symbol; a photograph; not an artwork (need_art). Force, no consent and restraint do
    NOT leave a work out: theme_of names them in its answer."""
    text = " ".join(clean(t) for t in (title, *texts) if t)
    if need_topic and not is_sexual(text):
        return NOT_SEXUAL
    words = art_minor_words(text)
    if words:
        if only_ambiguous(words, text) and not PHOTO_WORDS.search(f"{clean(kind)} {clean(title)}"):
            return f"{REVIEW} ({', '.join(words)})"
        return f"names or may name a young person ({', '.join(words)})"
    for pattern, why in ((INCEST, "incest, a parent and child, or a family"),
                         (HARM, "killing, death, torture or a private picture"), (ANIMAL, "an animal or creature"),
                         (ANIMAL_MYTH, "an animal or creature (a myth of sex with an animal)"),
                         (SYMBOL, "a religious symbol, not people")):
        m = pattern.search(text)
        if m:
            return f"{why} ({m.group(0)})"
    if PHOTO_WORDS.search(f"{clean(kind)} {clean(title)}"):
        return "a photograph (no photographs of sexual acts in this pass)"
    if need_art and not ART_KIND.search(clean(kind)):
        return "the record does not show an artwork"
    return ""


ALLOW_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erotic_art_allow.txt")
# The review list is written only on the owner's own computer (the environment variable ADULT_ART_REVIEW_LIST names
# the file, or main()'s quick try writes it), never in the repository or a published build: a list of sexual
# artworks whose records mention girls or boys is for the team's eyes only.
REVIEW_ITEMS = []


def allowed_items(path=None):
    """{(institution, id): note} from the allow-list (lines "institution<TAB>id<TAB>note"; "#" starts a comment)."""
    out = {}
    try:
        with open(path or ALLOW_FILE, encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.rstrip("\n").split("\t")]
                if len(parts) >= 2 and parts[0] and not parts[0].startswith("#"):
                    out[(parts[0], parts[1])] = parts[2] if len(parts) > 2 else ""
    except FileNotFoundError:
        pass
    return out


def reviewed(why, institution, item_id, title, link):
    """For a work left out with REVIEW: True when the allow-list allows it (it is then kept); otherwise it is put on
    the review list (REVIEW_ITEMS) and False. Any other reason: False."""
    if not why.startswith(REVIEW):
        return False
    if (institution, str(item_id)) in allowed_items():
        return True
    if not any(r[0] == institution and r[1] == str(item_id) for r in REVIEW_ITEMS):
        REVIEW_ITEMS.append((institution, str(item_id), clean(title)[:200], link, why[len(REVIEW):].strip(" ()")))
    return False


def write_review_list(path):
    """Write the review list: one line per work, institution, id, title, catalogue link, the words, and a blank
    decision for the team (titles and links only: no pictures)."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("# erotic_art works whose only young-person word is girl(s), boy(s), lad or lass. Look at the "
                "museum's own page;\n# if every figure is clearly an adult, copy the line's institution and id to "
                "packs/erotic_art_allow.txt with a note.\n# institution\tid\ttitle\tlink\twords\tdecision\n")
        for institution, item_id, title, link, words in REVIEW_ITEMS:
            f.write(f"{institution}\t{item_id}\t{title}\t{link}\t{words}\t\n")


# Works found by the erotic searches that are NOT sexual but show nudity: offered to museum_art_nudes, where its own
# child rules apply (nudes_left_out(routed=True): putti, Cupid and the Christ Child are fine there in a plainly
# non-sexual work). (name, picture address, rows) items, filled by the museum readers below.
ROUTED = []


def route_to_nudes(source, name, url, title, credit, kind="", artist="", date="", medium="", text="", place="",
                   others=()):
    """Offer a non-sexual work found by an erotic search to museum_art_nudes: kept in ROUTED when its words name
    nudity (body_packs.NUDITY_WORDS) and it passes nudes_left_out(routed=True). Rows as art_nudes's (body_packs
    art_rows), marked "child" when its words name a sacred or winged child figure."""
    words = " ".join(clean(t) for t in (title, text, *others) if t)
    if not body_packs.NUDITY_WORDS.search(words) or any(n == name for n, _, _ in ROUTED):
        return False
    if nudes_left_out(source, title, text, *others, kind=f"{kind} {medium}", routed=True):
        return False
    female, male = body_packs.nudity_kind(words)
    rows = body_packs.art_rows(text, credit, title, kind, artist, date, medium, female, male)
    if place:
        rows = made_in(rows, place_from_text(place))
    if minor_word(words):
        rows = [dict(r, child=True) for r in rows]
    ROUTED.append((name, url, rows))
    return True


# ----------------------------------------------------------------- plain words

# Catalogue and crude words in plain adult English (the source's meaning kept, nothing invented); each changed once.
PLAIN = [(re.compile(p, re.I), w) for p, w in [
    (r"\bsumizuri-e\b", "black-ink print (sumizuri-e)"), (r"\bnishiki-e\b", "full-colour print (nishiki-e)"),
    (r"\bshunga\b", "shunga (Japanese erotic art)"), (r"\bhiga\b", "higa (erotic pictures)"),
    (r"\bmakura-?e\b", "makura-e (erotic pictures)"), (r"\b(maithuna|mithuna)\b", r"\1 (an amorous couple)"),
    (r"\brecto\b", "front"), (r"\bverso\b", "back"), (r"\bcoitus\b", "sex"), (r"\bcoital\b", "sexual"),
    (r"\bcopulating\b", "having sex"), (r"\bcopulation\b", "sex"), (r"\bfucking\b", "having sex"),
    (r"\bfucks?\b", "has sex with"), (r"\bcocks?\b", "penis"), (r"\bdicks?\b", "penis"),
    (r"\bpuss(y|ies)\b", "vulva"), (r"\btits\b", "breasts"), (r"\bboobs?\b", "breasts"), (r"\bcum\b", "semen"),
    (r"\bfellatio\b", "oral sex on a penis (fellatio)"), (r"\bcunnilingus\b", "oral sex on a vulva (cunnilingus)"),
    (r"\bharigata\b", "harigata (a Japanese dildo)"), (r"\bnayika\b", "nayika (the heroine)"),
    (r"\bobscen\w*\b", "explicit"), (r"\b(lewd\w*|lascivious\w*|lustful|bawdy|sexy|smutty|dirty)\b", "sexual"),
    (r"<[^>]+>", " ")]]


def plain(text):
    """Text with catalogue and crude words in plain adult English (each pattern changed once)."""
    text = clean(text)
    for pattern, words in PLAIN:
        def same_case(m, words=words):
            """The plain words, with a capital first letter when the word replaced had one."""
            out = m.expand(words)
            return out[:1].upper() + out[1:] if m.group(0)[:1].isupper() else out
        text = pattern.sub(same_case, text, count=1)
    return clean(text)


def erotic_rows(credit, title, kind="", artist="", date="", medium="", text="", tags=(), owner="museum",
                place=""):
    """The two rows of an erotic_art picture, each with "content": "sexual": "Describe this picture." (the record's
    opening sentence, its description in plain words and its subject tags) and "Is there sexual content ...?"."""
    answer = plain(lead(title, kind, artist, date, medium))
    words = first_sentences(plain(text), 90) if text else ""
    if words and words.lower() not in answer.lower():
        answer += " " + sentence(words)
    tags = [plain(t).lower() for t in tags if clean(t) and len(clean(t)) < 40]
    if tags:
        answer += " " + sentence(f"The {owner}'s subject tags: " + ", ".join(dict.fromkeys(tags)))
    if not SEX_ACT.search(answer):
        answer += f" The {owner} files it as erotic art."
    rows = [{"question": DESCRIBE, "answer": answer, "credit": credit, "content": CONTENT},
            {"question": IS_SEXUAL, "answer": SEXUAL_YES.format(owner=owner), "credit": credit, "content": CONTENT}]
    rows = with_theme(rows, " ".join(clean(t) for t in (title, text, " ".join(tags)) if t))
    return made_in(rows, place_from_text(place)) if place else rows


def with_theme(rows, words):
    """Rows with the work's theme (theme_of): its plain sentence added to the description, the yes-answer saying it,
    and "theme" in every row; rows unchanged when it has none."""
    theme, said = theme_of(words)
    if not theme:
        return rows
    yes = {THEME_FORCE: "Yes. It is erotic art that depicts sexual violence: force, not consent.",
           THEME_NO_CONSENT: "Yes. It is erotic art in which a person cannot consent or is watched without consent.",
           THEME_RESTRAINT: "Yes. It is erotic art that shows restraint or striking."}[theme]
    out = []
    for r in rows:
        answer = (f"{r['answer']} {said}" if r["question"] == DESCRIBE else yes)
        out.append(dict(r, answer=answer, theme=theme))
    return out


def get_json(s, url, params=None, method="get", body=None, tries=3):
    """A JSON answer, tried again on a passing error; None when it cannot be had."""
    for attempt in range(tries):
        try:
            r = s.post(url, params=params, json=body, timeout=90) if method == "post" else \
                s.get(url, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (400, 403, 404, 410):
                return None
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(3 * (attempt + 1))
    return None


def take_turns(lists):
    """The items of several lists, one from each in turn; items whose name (first value) was seen are dropped."""
    out, seen = [], set()
    lists = [list(x) for x in lists]
    while any(lists):
        for items in lists:
            if items:
                item = items.pop(0)
                if item[0] not in seen:
                    seen.add(item[0])
                    out.append(item)
    return out


# ----------------------------------------------------------------- erotic_art: The Met (CC0)

MET = "https://collectionapi.metmuseum.org/public/collection/"
MET_QUERIES = ("shunga", "Spring pictures", "erotic", "erotica", "mithuna", "Kama Sutra", "makura-e")


def met_erotic(want):
    """(name, picture address, rows) for public-domain Met works found by MET_QUERIES that pass erotic_left_out."""
    s, lists = session(), []
    for q in MET_QUERIES:
        data = get_json(s, MET + "v1.1/search", params={"q": q, "hasImages": "true", "limit": 500}) or {}
        lists.append([(f"met-{i}.jpg", i) for i in (data.get("objectIDs") or [])[:max(80, want * 3)]])
        time.sleep(0.5)
    ids = take_turns(lists)
    say(f"Met: {len(ids)} objects found by the searches")
    items = []
    for name, oid in ids:
        if len(items) >= want:
            break
        time.sleep(0.15)
        o = get_json(s, f"{MET}v1/objects/{oid}") or {}
        title = clean(o.get("title"))
        if not o.get("isPublicDomain") or not o.get("primaryImageSmall") or not title:
            note("Met", title or str(oid), "not public domain, or no picture")
            continue
        tags = [t.get("term", "") for t in (o.get("tags") or [])]
        kind = f"{o.get('classification')} {o.get('objectName')} {o.get('medium')}"
        why = erotic_left_out(" ".join(tags), o.get("objectName"), o.get("medium"), o.get("culture"),
                              kind=kind, title=title)
        artist = clean(o.get("artistDisplayName"))
        credit = f"The Metropolitan Museum of Art, public domain (CC0): {title}" + (f", {artist}" if artist else "") \
            + f", {o.get('objectURL', '')}"
        if why == NOT_SEXUAL:
            route_to_nudes("Met", name, o["primaryImage"] or o["primaryImageSmall"], title, credit,
                           o.get("objectName"), artist, o.get("objectDate"), o.get("medium"),
                           "", o.get("culture") or o.get("country"), tags)
        if reviewed(why, "The Met", oid, title, o.get("objectURL", "")):
            why = ""
        if why:
            note("Met", title, why)
            continue
        rows = erotic_rows(credit, title, o.get("objectName"), artist, o.get("objectDate"), o.get("medium"),
                           "", tags, "museum", o.get("culture") or o.get("country"))
        items.append((name, o["primaryImage"] or o["primaryImageSmall"], rows))
    say(f"Met: {len(items)} usable")
    return items


# ----------------------------------------------------------------- erotic_art: Art Institute of Chicago (CC0)

AIC = "https://api.artic.edu/api/v1/artworks/search"
AIC_TITLE = ("shunga", "erotic", "spring picture", "love-making", "lovemaking", "mithuna", "makura")
AIC_SUBJECT = ("erotica", "sexuality", "erotic art")
AIC_FIELDS = ["id", "title", "subject_titles", "term_titles", "classification_titles", "classification_title",
              "description", "short_description", "thumbnail", "image_id", "artist_display", "date_display",
              "medium_display", "place_of_origin", "is_public_domain"]


def aic_erotic(want):
    """(name, picture address, rows) for public-domain Art Institute works whose title or subjects name erotica
    (each record's is_public_domain checked too) that pass erotic_left_out."""
    s = session()
    s.headers["AIC-User-Agent"] = s.headers["User-Agent"]
    should = [{"match_phrase": {"title": w}} for w in AIC_TITLE] + \
             [{"match_phrase": {"subject_titles": w}} for w in AIC_SUBJECT]
    items, page = [], 1
    while len(items) < want and page <= 20:
        body = {"query": {"bool": {"should": should, "minimum_should_match": 1,
                                   "filter": [{"term": {"is_public_domain": True}}]}},
                "fields": AIC_FIELDS, "limit": 100, "page": page}
        data = get_json(s, AIC, method="post", body=body)
        records = (data or {}).get("data") or []
        for a in records:
            title = clean(a.get("title"))
            if not a.get("is_public_domain") or not a.get("image_id") or not title:
                note("AIC", title, "not public domain, or no picture")
                continue
            desc = clean(a.get("short_description") or a.get("description"))
            alt = clean((a.get("thumbnail") or {}).get("alt_text"))
            subjects = a.get("subject_titles") or []
            kind = f"{a.get('classification_title')} {' '.join(a.get('classification_titles') or [])} " \
                   f"{a.get('medium_display')} {' '.join(a.get('term_titles') or [])}"
            why = erotic_left_out(desc, alt, " ".join(subjects), kind=kind, title=title)
            artist = clean(a.get("artist_display")).split("\n")[0]
            credit = f"Art Institute of Chicago, CC0 (public domain): {title}, {artist}, " \
                     f"https://www.artic.edu/artworks/{a['id']}"
            text = alt if len(alt.split()) >= 8 else desc
            classification = re.sub(r"s? \(visual works?\)", "", clean(a.get("classification_title")))
            picture = f"https://www.artic.edu/iiif/2/{a['image_id']}/full/1686,/0/default.jpg"
            if why == NOT_SEXUAL:
                route_to_nudes("AIC", f"aic-{a['id']}.jpg", picture, title, credit, classification,
                               re.sub(r"\s*\(.*", "", artist), a.get("date_display"), a.get("medium_display"), text,
                               a.get("place_of_origin"), subjects)
            if reviewed(why, "Art Institute of Chicago", a["id"], title, f"https://www.artic.edu/artworks/{a['id']}"):
                why = ""
            if why:
                note("AIC", title, why)
                continue
            rows = erotic_rows(credit, title, classification, re.sub(r"\s*\(.*", "", artist),
                               a.get("date_display"), a.get("medium_display"), text,
                               [t for t in subjects if not SEX_ACT.search(t) or t.lower() == "erotica"], "museum",
                               a.get("place_of_origin"))
            items.append((f"aic-{a['id']}.jpg", picture, rows))
        if len(records) < 100:
            break
        page += 1
        time.sleep(1)
    say(f"Art Institute of Chicago: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- erotic_art: Cleveland Museum of Art (CC0)

CMA = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_QUERIES = ("erotic", "shunga", "mithuna", "kama sutra", "sexual", "lovemaking")


def cma_erotic(want):
    """(name, picture address, rows) for CC0 Cleveland works found by CMA_QUERIES that pass erotic_left_out; its
    curators' descriptions are good."""
    s, lists = session(), []
    for q in CMA_QUERIES:
        found, skip = [], 0
        while len(found) < want * 2 + 10:
            data = get_json(s, CMA, params={"q": q, "has_image": 1, "cc0": 1, "limit": 100, "skip": skip}) or {}
            records = data.get("data") or []
            for a in records:
                title = clean(a.get("title"))
                web = ((a.get("images") or {}).get("print") or (a.get("images") or {}).get("web") or {}).get("url")
                if a.get("share_license_status") != "CC0" or not web or not title:
                    note("Cleveland", title, "not CC0, or no picture")
                    continue
                desc = clean(a.get("digital_description") or a.get("wall_description") or a.get("description"))
                kind = f"{a.get('type')} {a.get('technique')}"
                why = erotic_left_out(desc, a.get("type"), a.get("technique"), kind=kind, title=title)
                maker = clean(((a.get("creators") or [{}])[0] or {}).get("description"))
                credit = f"Cleveland Museum of Art, CC0: {title}, {maker or 'unknown maker'}, {a.get('url', '')}"
                culture = str((a.get("culture") or [""])[0]).split(",")[0]
                if why == NOT_SEXUAL:
                    route_to_nudes("Cleveland", f"cma-{a['id']}.jpg", web, title, credit, a.get("type"),
                                   re.sub(r"\s*\(.*", "", maker), a.get("creation_date"), a.get("technique"), desc,
                                   culture)
                if reviewed(why, "Cleveland Museum of Art", a["id"], title, a.get("url", "")):
                    why = ""
                if why:
                    note("Cleveland", title, why)
                    continue
                rows = erotic_rows(credit, title, a.get("type"), re.sub(r"\s*\(.*", "", maker),
                                   a.get("creation_date"), a.get("technique"), desc, (), "museum", culture)
                found.append((f"cma-{a['id']}.jpg", web, rows))
            skip += len(records)
            if len(records) < 100:
                break
            time.sleep(0.5)
        lists.append(found)
    items = take_turns(lists)
    say(f"Cleveland Museum of Art: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- erotic_art: Wellcome Collection

WELLCOME = "https://api.wellcomecollection.org/catalogue/v2/images"
WELLCOME_QUERIES = ("sexual intercourse", "erotica", "love making", "kama sutra", "coitus", "sex positions",
                    "erotic painting", "shunga")
WELLCOME_LICENCES = {"pdm": "public domain (Public Domain Mark)", "cc-0": "CC0", "cc-by": "CC BY 4.0"}


def wellcome_erotic(want):
    """(name, picture address, rows) for Wellcome Collection pictures of erotica and sex (Indian, Persian,
    Nepalese and Japanese erotic paintings, European erotic etchings, sexual-health prints), each with the licence
    pdm, cc-0 or cc-by, that pass erotic_left_out. Its titles are plain descriptions ("A couple engaged in sexual
    intercourse. Gouache painting by an Indian artist.")."""
    s, lists = session(), []
    for q in WELLCOME_QUERIES:
        found, page = [], 1
        while len(found) < want * 2 + 10 and page <= 5:
            data = get_json(s, WELLCOME, params={"query": q, "pageSize": 100, "page": page,
                                                 "locations.license": ",".join(WELLCOME_LICENCES),
                                                 "include": "source.subjects,source.genres"}) or {}
            for x in data.get("results") or []:
                src = x.get("source") or {}
                title = clean(src.get("title"))
                loc = (x.get("locations") or [{}])[0]
                lic = (loc.get("license") or {}).get("id", "")
                if lic not in WELLCOME_LICENCES or not loc.get("url", "").endswith("info.json") or not title:
                    note("Wellcome", title, f"licence not open ({lic or 'none'}), or no picture")
                    continue
                subjects = [clean(t.get("label")) for t in src.get("subjects") or []]
                genres = [clean(t.get("label")) for t in src.get("genres") or []]
                kind = f"{title} {' '.join(genres)}"
                why = erotic_left_out(" ".join(subjects), " ".join(genres), kind=kind, title=title)
                if reviewed(why, "Wellcome Collection", src.get("id", ""), title,
                            f"https://wellcomecollection.org/works/{src.get('id', '')}"):
                    why = ""
                if why:
                    note("Wellcome", title, why)
                    continue
                credit = f"Wellcome Collection, {WELLCOME_LICENCES[lic]}: {title[:150]}, " \
                         f"https://wellcomecollection.org/works/{src.get('id', '')}"
                rows = erotic_rows(credit, title, "", "", "", "", "",
                                   [t for t in subjects if not t.isupper()][:6], "library")
                found.append((f"wellcome-{x['id']}.jpg", loc["url"].replace("info.json", "full/!1600,1600/0/default.jpg"),
                              rows))
            if (data.get("totalPages") or 1) <= page:
                break
            page += 1
            time.sleep(0.5)
        lists.append(found)
    items = take_turns(lists)
    say(f"Wellcome Collection: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- erotic_art: Wikimedia Commons (licence per file)

# The categories read, with how deep into subcategories (a subcategory is read only when its own name passes
# erotic_left_out's word screens). "art": photographs OF artworks (sculpture, reliefs, frescoes, pottery);
# "drawn": drawings, prints and diagrams only.
COMMONS_ART = [("Erotic sculptures of Konark Sun Temple", 0), ("Erotic sculptures in India", 2),
               ("Erotic sculptures in Nepal", 1), ("Mithuna", 1), ("Erotic reliefs", 1),
               ("Sexuality in ancient Roman sculptures", 1), ("Lupanar (Pompeii)", 1), ("Erotic pottery", 2),
               ("Erotic sculptures", 1), ("Erotic frescos in Pompeii", 1), ("Erotic art of ancient Rome", 1),
               ("Erotic art of ancient Greece", 1)]
COMMONS_DRAWN = [("Sex positions", 2), ("Human sexual activity diagrams", 1), ("Kama Sutra", 1),
                 ("I modi - nine fragments - Agostino Veneziano", 0), ("Erotic prints in the Metropolitan Museum of Art", 1),
                 ("Erotic engravings", 1), ("Erotic illustrations", 1), ("Erotic drawings", 1),
                 ("People having sex in art", 1), ("Erotic paintings", 1), ("Shunga", 1)]
DRAWN = re.compile(r"\b(drawings?|drawn|illustrations?|illustrated|diagrams?|vector|svg|sketch\w*|engravings?|"
                   r"etchings?|lithographs?|woodcuts?|woodblock|prints?|watercolou?rs?|paintings?|painted|gouache|"
                   r"miniatures?|ukiyo-?e|shunga|schematic|line art)\b", re.I)
ARTWORK = re.compile(r"\b(sculpt\w*|temple|relief\w*|fresco\w*|mural|pottery|vases?|kylix|krater|amphora|ceramic\w*|"
                     r"statue\w*|carv\w*|figurine\w*|lamps?|mosaic\w*|painting\w*|museum|terracotta|bronze|marble|"
                     r"Pompeii|Herculaneum|Khajuraho|Konark|Moche|lupanar)\b", re.I)
PROBLEM_CATEGORY = re.compile(r"deletion|copyright violation|possible copyright|unidentified|no permission|"
                              r"missing permission|personality rights|consent|review needed|nominated|disputed|"
                              r"speedy|unknown source|no source", re.I)
NOT_A_PICTURE = re.compile(r"\b([Ll]ogos?|[Ii]cons?|[Ww]ordmarks?|[Pp]ictograms?|[Ee]mblems?|[Ff]lags?|[Mm]aps?|"
                           r"[Cc]harts?|[Gg]raphs?|[Tt]ext|[Pp]ages?|[Cc]overs?)\b")


def commons_meta(info, key):
    """One extmetadata field of a Commons file as plain text."""
    return clean(((info.get("extmetadata") or {}).get(key) or {}).get("value"))


def commons_subcats(s, category, depth):
    """category and its subcategories down to depth whose names pass the word screens (not a problem category)."""
    found, todo = [category], [(category, depth)]
    while todo:
        cat, d = todo.pop(0)
        if d <= 0:
            continue
        try:
            subs = [c.split(":", 1)[-1] for c in commons_members(s, cat, "subcat")]
        except RuntimeError:
            continue
        for sub in subs:
            why = erotic_left_out(sub, need_topic=False, need_art=False) or \
                ("a problem category" if PROBLEM_CATEGORY.search(sub) else "")
            if why:
                note("Commons", f"Category:{sub}", why)
            elif sub not in found:
                found.append(sub)
                todo.append((sub, d - 1))
    return found


def commons_infos(s, titles):
    """[(title, imageinfo)] of Commons files, 50 a request."""
    out = []
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": LONG_SIDE,
                               "iiextmetadatafilter": "LicenseShortName|ImageDescription|Artist|Categories|"
                                                      "ObjectName|DateTimeOriginal",
                               "iiextmetadatalanguage": "en"})
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            if p.get("pageid"):
                out.append((p["title"], (p.get("imageinfo") or [{}])[0]))
    return out


def commons_licence_open(licence):
    """True when a Commons licence is CC0, public domain or CC BY (never SA, NC or ND)."""
    return bool(COMMONS_FREE.match(licence or "")) and not re.search(r"\b(SA|NC|ND)\b", (licence or "").upper())


def commons_item(title, info, group):
    """(name, picture address, rows) for one Commons file of a group ("art" or "drawn"), or None (noted in LEFT)."""
    licence, mime = commons_meta(info, "LicenseShortName"), info.get("mime", "")
    description = re.sub(r"^\s*English\s*:\s*", "", commons_meta(info, "ImageDescription"))
    categories = commons_meta(info, "Categories")
    stem = title.split(":", 1)[-1].rsplit(".", 1)[0].replace("_", " ")
    text = f"{stem} {commons_meta(info, 'ObjectName')} {description}"
    drawn = mime == "image/svg+xml" or bool(DRAWN.search(f"{text} {categories}"))
    why = ""
    if mime not in ("image/jpeg", "image/png", "image/svg+xml", "image/tiff") or not info.get("thumburl"):
        why = "not a still picture"
    elif not commons_licence_open(licence):
        why = f"licence not CC0, public domain or CC BY ({licence or 'none'})"
    elif PROBLEM_CATEGORY.search(categories):
        why = "in a deletion, copyright or consent-problem category"
    elif NOT_A_PICTURE.search(stem):
        why = "a logo, map, chart, page or cover"
    else:
        why = erotic_left_out(text, categories, need_art=False, need_topic=False)
        if why.startswith("a photograph"):
            why = ""                       # a photograph OF an artwork is checked below instead
        if reviewed(why, "Wikimedia Commons", title, stem, "https://commons.wikimedia.org/wiki/" +
                    title.replace(" ", "_")):
            why = ""
    if not why and group == "drawn" and not drawn:
        why = "not a drawing (this group is drawings and illustrations only)"
    if not why and group == "art" and not drawn and not ARTWORK.search(f"{text} {categories}"):
        why = "its words do not say it is an artwork (sculpture, relief, fresco, pottery ...)"
    if not why and not drawn and re.search(r"\b1[89]\d\d\b|vintage|antique|daguerreotype|albumen", text, re.I) \
            and not ARTWORK.search(text):
        why = "an old photograph rather than a photograph of an artwork"
    if why:
        note("Commons", stem, why)
        return None
    artist = commons_meta(info, "Artist")[:100] or "unknown"
    page = "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")
    credit = f"{title} by {artist}, {licence}, {page}"
    kind = "a drawing or print" if drawn else "a photograph of an artwork (sculpture, relief, fresco or pottery)"
    words = first_sentences(plain(description), 80) if len(description.split()) >= 4 else ""
    answer = sentence(f"{stem}: {kind}") + (" " + sentence(words) if words else "")
    if not SEX_ACT.search(answer):
        answer += " It is filed on Wikimedia Commons among erotic art."
    rows = [{"question": DESCRIBE, "answer": answer, "credit": credit, "content": CONTENT},
            {"question": IS_SEXUAL, "answer": "Yes. It is erotic art: it is filed on Wikimedia Commons among erotic "
                                              "or sexual works.", "credit": credit, "content": CONTENT}]
    rows = with_theme(rows, f"{text} {categories}")
    name = "commons-" + re.sub(r"[^\w.-]+", "_", stem)[:80] + ".jpg"
    url = info["thumburl"]
    return (name, url, rows)


def commons_erotic(want):
    """(name, picture address, rows) for Commons files of COMMONS_ART (photographs of artworks) and COMMONS_DRAWN
    (drawings only), taking turns between the categories."""
    s, lists, seen = session(), [], set()
    for group, table in (("art", COMMONS_ART), ("drawn", COMMONS_DRAWN)):
        for category, depth in table:
            for cat in commons_subcats(s, category, depth):
                if cat in seen or build_packs.listing_out_of_time():
                    continue
                seen.add(cat)
                try:
                    titles = commons_members(s, cat, "file")[:max(30, want)]
                except RuntimeError:
                    continue
                found = [x for x in (commons_item(t, i, group) for t, i in commons_infos(s, titles)) if x]
                if found:
                    say(f"  Commons {cat}: {len(found)} usable")
                lists.append(found)
                if sum(len(x) for x in lists) > want * 2 + 10:
                    break
    items = take_turns(lists)
    say(f"Wikimedia Commons: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- nude_photo_studies: Wellcome Collection

# The owner's decision (November 2026): NON-SEXUAL nude photographs (studio and art-school poses, medical and
# anthropometric photographs) that an institution shows publicly with an OPEN licence may be used without a
# documented age. This pack's safeguard instead: the record must DESCRIBE AN ADULT (ADULT_CUE: a woman, a man, a
# young woman or young man, an adult, a model ...), name no child or young person (art_minor_word: the clear minor
# words and ages under 18; "young woman" and "young man" allowed), no group, family or class (people whose ages
# are not given), and nothing sexual (SEX_ACT, TOPIC: those photographs belong only to the kit's documented-adult
# set). Personal-use photographs (not open) are the kit's local builder's (training-kit/kit/adult_photo_review.py).
NUDE_PHOTO_QUERIES = ("naked photograph", "nude photograph", "posing naked", "nude model photograph",
                      "naked man photograph", "naked woman photograph", "anthropometric photograph naked",
                      "naked stereograph")
ADULT_CUE = re.compile(r"\b(wom[ae]n|m[ae]n|lad(y|ies)|gentlem[ae]n|adults?|adult (male|female)|(male|female) "
                       r"models?|artist'?s models?|athletes?|wrestlers?|strong ?m[ae]n|bodybuilders?|soldiers?|"
                       r"sailors?|dancers?|wi(fe|ves)|husbands?|elderly|old (wom[ae]n|m[ae]n))\b", re.I)
PEOPLE_UNKNOWN = re.compile(r"\b(group|groups|crowd|several|people|famil(y|ies)|tribe\w*|villagers?|class|"
                            r"classes|series of (wom[ae]n|m[ae]n|people|figures)|population|mothers?|fathers?|"
                            r"parents?|siblings?|brothers?|sisters?|growth|development|puberty|tanner)\b", re.I)
ART_REPRODUCTION = re.compile(r"\b(photograph|photo|halftone|reproduction)\w*,? [^.]{0,20}\bof an? ([\w-]+ ){0,3}"
                              r"(drawing|painting|print|sculpture|statue|engraving|miniature|manuscript|relief|"
                              r"fresco|mural)s?\b|"
                              r"\bafter an? (drawing|painting|print|sculpture|statue|engraving)\b", re.I)


def nude_photo_left_out(title, *texts, kind=""):
    """The reason a record is not for nude_photo_studies, or "" when it may be used: not a photograph (or a
    photograph of an artwork); no nudity named; anything sexual; a young-person word or an age under 18; a group,
    family or class; no word describing an adult (ADULT_CUE); harm; an animal."""
    text = " ".join(clean(t) for t in (title, *texts) if t)
    if not PHOTO_WORDS.search(f"{clean(kind)} {text}") or ART_REPRODUCTION.search(text):
        return "not a photograph of people (or a photograph of an artwork)"
    if not body_packs.NUDITY_WORDS.search(text):
        return "no nudity named"
    if SEX_ACT.search(text) or TOPIC.search(NOT_TOPIC.sub(" ", text)) or SEXUAL_FORCE.search(text):
        return "sexual (only the kit's documented-adult set may hold sexual photographs)"
    minor = minor_word_photo(text)
    if minor:
        return f"names or may name a young person ({minor})"
    if PEOPLE_UNKNOWN.search(text):
        return f"a group, family or class, whose ages are not given ({PEOPLE_UNKNOWN.search(text).group(0)})"
    if not ADULT_CUE.search(text):
        return "the record does not describe an adult"
    for pattern, why in ((HARM, "harm"), (ANIMAL, "an animal")):
        if pattern.search(text):
            return why
    return ""


def minor_word_photo(text):
    """The young-person word of a nude photograph's record ("" when none): art_minor_word's words, with "young
    woman" and "young man" allowed (and nothing else rescued: no maiden, nymph or youthful), in any culture."""
    rest = GIRL_ADULT.sub(" ", re.sub(r"\byoung (wom[ae]n|m[ae]n)\b", " ", text, flags=re.I))
    found = SEX_MINOR.search(rest) or AGE_WORDS.search(rest) or re.search(r"\b(maidens?|nymphs?|youthful|"
                                                                         r"little|petite?|small (wom[ae]n|m[ae]n|"
                                                                         r"figure))\b", rest, re.I)
    if found:
        return found.group(0)
    for m in AGE.finditer(rest):
        if int(next(g for g in m.groups() if g)) < 18:
            return m.group(0)
    return ""


NUDE_PHOTO_YES = "Yes: it is a non-sexual nude photograph, a studio, art-school, medical or anthropometric study."
OPEN_WELLCOME = {"pdm": "public domain (Public Domain Mark)", "cc-0": "CC0", "cc-by": "CC BY 4.0"}


def nude_photo_rows(title, credit, subjects=()):
    """The two rows of a nude photograph: its description in the record's own words, plainly and non-sexually,
    and the nudity question. Every row "content": "nudity"."""
    words = sentence(plain(title).rstrip("."))
    tags = [plain(t).lower() for t in subjects if clean(t) and len(clean(t)) < 40 and not clean(t).isupper()]
    if tags:
        words += " " + sentence("The library's subject tags: " + ", ".join(dict.fromkeys(tags)))
    return [{"question": DESCRIBE, "answer": words, "credit": credit, "content": "nudity"},
            {"question": "Is there nudity in this picture?", "answer": NUDE_PHOTO_YES, "credit": credit,
             "content": "nudity"}]


def wellcome_nude_photos(want, s=None):
    """(name, picture address, rows) for Wellcome Collection photographs that pass nude_photo_left_out and whose
    own licence is open (pdm, cc-0, cc-by)."""
    s, lists = s or session(), []
    for q in NUDE_PHOTO_QUERIES:
        found, page = [], 1
        while len(found) < want * 2 + 10 and page <= 5:
            data = get_json(s, WELLCOME, params={"query": q, "pageSize": 100, "page": page,
                                                 "locations.license": ",".join(OPEN_WELLCOME),
                                                 "include": "source.subjects,source.genres"}) or {}
            for x in data.get("results") or []:
                src = x.get("source") or {}
                title = clean(src.get("title"))
                loc = (x.get("locations") or [{}])[0]
                lic = (loc.get("license") or {}).get("id", "")
                if lic not in OPEN_WELLCOME or not loc.get("url", "").endswith("info.json") or not title:
                    note("Wellcome photo", title, f"licence not open ({lic or 'none'}), or no picture")
                    continue
                subjects = [clean(t.get("label")) for t in src.get("subjects") or []]
                genres = [clean(t.get("label")) for t in src.get("genres") or []]
                why = nude_photo_left_out(title, " ".join(subjects), kind=" ".join(genres))
                if why:
                    note("Wellcome photo", title, why)
                    continue
                credit = f"Wellcome Collection, {OPEN_WELLCOME[lic]}: {title[:150]}, " \
                         f"https://wellcomecollection.org/works/{src.get('id', '')}"
                found.append((f"wellcome-{x['id']}.jpg",
                              loc["url"].replace("info.json", "full/!1600,1600/0/default.jpg"),
                              nude_photo_rows(title, credit, subjects)))
            if (data.get("totalPages") or 1) <= page:
                break
            page += 1
            time.sleep(0.5)
        lists.append(found)
    items = take_turns(lists)
    say(f"Wellcome Collection nude photographs: {len(items)} usable")
    return items[:want]


def build_nude_photo_studies(limit):
    """The nude_photo_studies pack (see wellcome_nude_photos)."""
    return finish("nude_photo_studies", wellcome_nude_photos(int(limit * 1.3) + 2), limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- the packs

# Each source's share of erotic_art (a source with fewer gives what it has).
EROTIC_SHARES = (("met", met_erotic, 0.25), ("aic", aic_erotic, 0.1), ("cma", cma_erotic, 0.1),
                 ("wellcome", wellcome_erotic, 0.2), ("commons", commons_erotic, 0.35))
# Each museum's share of museum_art_nudes (as body_packs.ART_SHARES).
NUDES_SHARES = (("met", body_packs.met_items, 0.45), ("nga", body_packs.nga_items, 0.25),
                ("si", body_packs.si_items, 0.12), ("cma", body_packs.cma_items, 0.08),
                ("aic", body_packs.aic_items, 0.1))


def build_erotic_art(limit):
    """The erotic_art pack (see the module docstring)."""
    items = []
    for key, collect, share in EROTIC_SHARES:
        try:
            items += collect(max(2, round(limit * share * 1.3)))
        except Exception as error:  # noqa: BLE001 - one source down does not stop the pack
            say(f"{key}: left out ({error})")
    if os.environ.get("ADULT_ART_REVIEW_LIST"):
        write_review_list(os.environ["ADULT_ART_REVIEW_LIST"])
    say(f"erotic_art: {len(REVIEW_ITEMS)} works for the team's review (only girl, boy, lad or lass named)")
    return finish("erotic_art", items, limit, workers=3, pause=0.3)


def build_museum_art_nudes(limit):
    """The museum_art_nudes pack (see the module docstring): the body_packs museum readers with nudes_left_out as
    their screen; rows of works whose words name a child marked "child"."""
    items = []
    for key, collect, share in NUDES_SHARES:
        try:
            items += collect(max(2, round(limit * share * 1.3)), drop=nudes_left_out)
        except Exception as error:  # noqa: BLE001 - one museum down does not stop the pack
            say(f"{key}: left out ({error})")
    # The non-sexual nudes the erotic searches found (route_to_nudes): about a tenth of the pack.
    try:
        ROUTED.clear()
        for collect in (met_erotic, aic_erotic, cma_erotic):
            collect(max(20, limit))
        items += ROUTED[:max(2, round(limit * 0.1 * 1.3))]
    except Exception as error:  # noqa: BLE001 - the routed works are a small extra
        say(f"routed from the erotic searches: left out ({error})")
    marked = []
    for name, url, rows in items:
        child = any(r["answer"].startswith(t) for t in CHILD_TITLES for r in rows[:1])
        marked.append((name, url, [dict(r, child=True) if child else r for r in rows]))
    return finish("museum_art_nudes", marked, limit, workers=4, pause=0.2)


ADULT_ART_PACKS = {
    "museum_art_nudes": (build_museum_art_nudes,
                         "Fine-art nudity (Madonna and Child, putti and cherubs, mythology, bathers, lovers, classical "
                         "statues) that art_nudes leaves out, from open-access museum collections, each work credited "
                         "below: The Metropolitan Museum of Art (public domain, CC0), Art Institute of Chicago (CC0), "
                         "Cleveland Museum of Art (CC0), National Gallery of Art, Washington (CC0), Smithsonian "
                         "American Art Museum (CC0). No photographs, no sexual acts or sexual violence, and no child "
                         "in any work with sexual or romantic wording."),
    "erotic_art": (build_erotic_art,
                   "Erotic art and illustration showing adults (shunga, Indian and Persian erotic painting, Greek and "
                   "Roman vases and frescoes, temple sculpture, European erotic prints, sex-education drawings), each "
                   "item credited below: The Metropolitan Museum of Art (public domain, CC0), Art Institute of Chicago "
                   "(CC0), Cleveland Museum of Art (CC0), Wellcome Collection (public domain, CC0 or CC BY 4.0), "
                   "Wikimedia Commons (each file CC0, public domain or CC BY). Any record whose words name or may name "
                   "a young person, violence, no consent or an animal was left out; no photographs of people."),
    "nude_photo_studies": (build_nude_photo_studies,
                           "Non-sexual nude photographs (studio, art-school, medical and anthropometric studies) "
                           "from the Wellcome Collection, each with an open licence on its own record (public domain "
                           "mark, CC0 or CC BY 4.0) and credited below. Only records that describe an adult; none "
                           "naming a child or young person, a group or a family, or anything sexual."),
}

# The limits of the workflow (pack-build.yml), from the test builds of November 2026 (see the commit message).
ADULT_ART_LIMITS = {
    "museum_art_nudes": 1500,
    "erotic_art": 1500,
    "nude_photo_studies": 300,
}


def main(argv=None):
    """Build one pack with a small limit and print its rows and some left-out records (a quick check)."""
    import argparse
    import json
    import random
    parser = argparse.ArgumentParser(description="Try one adult art pack builder.")
    parser.add_argument("key", choices=sorted(ADULT_ART_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--review-list", default="", help="erotic_art: write the review list to this file (on your "
                                                          "own computer; never commit it)")
    args = parser.parse_args(argv)
    if args.review_list:
        os.environ["ADULT_ART_REVIEW_LIST"] = args.review_list
    entries = ADULT_ART_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False))
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    print(f"Left out: {len(LEFT)}, for example:")
    for source, title, reason in random.Random(1).sample(LEFT, min(25, len(LEFT))):
        print(f"  {source}: {title}  ({reason})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
