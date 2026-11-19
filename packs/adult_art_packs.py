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
                    WIDER (November 2026, the owner's request: the describer struggles with nudes): also every nude
                    and academic study (ACADEMY: académie d'homme, life study, écorché, academy figure ...) from
                    museums art_nudes does not read, each record's own licence checked: the Minneapolis Institute
                    of Art ("Public Domain", full image), Statens Museum for Kunst (Public Domain Mark or CC0), the
                    Rijksmuseum (Public Domain Mark or CC0), Europeana (CC0, Public Domain Mark or CC BY; its key from
                    the build's EUROPEANA_KEY secret), four more Smithsonian units (Cooper Hewitt, Freer and Sackler,
                    African Art, Hirshhorn: CC0), the J. Paul Getty Museum (Linked Art, linked_art.py: each
                    IMAGE'S own rights statement CC0 or Public Domain Mark; getty_items also gives erotic_art and
                    nude_photo_studies their Getty works), and the non-sexual nudes the erotic_art searches find. Danish and
                    Dutch titles are put in English word for word (foreign_title) or the work is left out; the
                    providers' English only (never Europeana's machine translations). Left out as well: death,
                    killing and torture (NUDE_HARM), specimens and documents (NOT_ART). Not read yet, with the
                    reason: MUSEUM_NUDES_LATER.
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
from build_packs import session, say, clean, first_sentences, LONG_SIDE, COMMONS_FREE, pass_random
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
    r"carte(s)?[- ]de[- ]visite|cabinet card\w*|stereograph\w*|stereoview\w*|stereo card\w*|collodion|negatives?|"
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
    elif NUDE_HARM.search(text):
        reason = f"death, killing or torture: {NUDE_HARM.search(text).group(0)}"
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
# Death, killing and torture: never in a nudes pack (graphic scenes are other packs' and need their own choice).
NUDE_HARM = re.compile(r"\b(corpses?|cadavers?|dead|death|dying|killed|killing|murder\w*|tortur\w*|flayed|"
                       r"executions?|executed|beheaded|severed|massacre\w*|suicide|slaughter\w*|martyrdom|"
                       r"crucifixion|lynch\w*)\b", re.I)

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
    (r"Lapiths?", THEME_FORCE, "It shows the centaurs trying to carry off the Lapith women by force."),
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
    # The stories of abduction and rape make a work sexual by their names; the PURSUIT stories (Daphne, Syrinx,
    # Arethusa, Io, Aegina, Antiope) do not: a porcelain "Apollo and Daphne" is not erotica.
    return any(theme == THEME_FORCE and not PURSUIT.search(said) and pattern.search(text)
               for pattern, theme, said in MYTH_FACTS)


PURSUIT = re.compile(r"\bpursu", re.I)


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


# Academic studies of the nude ("académie", "life study", "écorché", "academy figure"): nude by definition, even when
# the record does not say "nude".
# ("académie" alone also names academies and buildings, and "from the life" portraits: neither counts alone.)
ACADEMY = re.compile(r"\b(acad[ée]mies? (d'homme|de femme|study|drawing|figure)s?|academy (figures?|studies|study|"
                     r"drawings?)|academic (nudes?|studies|study|drawings?)|life (studies|study|drawings?|class)|"
                     r"[ée]corch[ée]s?|model (study|studies)|studies? (of|from) (a|the) (nude )?model|"
                     r"figure studies from the model)\b", re.I)


NOT_ART = re.compile(r"\b(specimens?|herbarium|fossils?|plants?|botan\w*|zoolog\w*|maps?|charts?|letters?|"
                     r"manuscript text|books? cover)\b", re.I)


def nude_candidate(source, name, url, title, credit, kind="", artist="", date="", medium="", text="", place="",
                   others=()):
    """(name, picture address, rows) for a museum_art_nudes work from a source that art_nudes does not read, or
    None: its words must name nudity (body_packs.NUDITY_WORDS) or an academic nude study (ACADEMY), it must pass
    nudes_left_out(routed=True) (no photograph, nothing sexual, no sexual violence, the child rules), and its rows are
    art_nudes's (body_packs.art_rows), marked "child" when its words name a sacred or winged child figure."""
    words = " ".join(clean(t) for t in (title, text, *others) if t)
    if not (body_packs.NUDITY_WORDS.search(words) or ACADEMY.search(words)):
        return None
    if NOT_ART.search(f"{kind} {title}"):
        return None                               # a specimen or a document, not a work of art
    if nudes_left_out(source, title, text, *others, kind=f"{kind} {medium}", routed=True):
        return None
    female, male = body_packs.nudity_kind(words)
    rows = body_packs.art_rows(text, credit, title, singular_kind(kind), artist, date, medium, female, male)
    if place:
        rows = made_in(rows, place_from_text(place))
    if minor_word(words):
        rows = [dict(r, child=True) for r in rows]
    return (name, url, rows)


def singular_kind(kind):
    """A museum's classification as one kind ("Prints, works on paper" -> "print", "Paintings" -> "painting")."""
    kind = re.sub(r"^works of art$", "work of art", clean(kind).split(",")[0].split(";")[0].strip(), flags=re.I)
    return re.sub(r"(?<=[a-z])s$", "", kind) if re.fullmatch(r"[A-Za-z ]+s", kind) and not kind.lower().endswith(
        ("ss", "us")) else kind


def route_to_nudes(source, name, url, title, credit, kind="", artist="", date="", medium="", text="", place="",
                   others=()):
    """Offer a non-sexual work found by an erotic search to museum_art_nudes (nude_candidate); kept in ROUTED. True
    when kept."""
    if any(n == name for n, _, _ in ROUTED):
        return False
    item = nude_candidate(source, name, url, title, credit, kind, artist, date, medium, text, place, others)
    if item:
        ROUTED.append(item)
    return bool(item)


# ----------------------------------------------------------------- museum_art_nudes: more museums

MIA = "https://search.artsmia.org/"
NUDE_QUERIES = ("nude", "naked", "académie", "academy figure", "life study", "figure study", "écorché",
                "nude model", "female nude", "male nude", "bather", "bathers")


def mia_records(s, query, most):
    """Minneapolis Institute of Art search hits (its public search API) for one query."""
    data = get_json(s, MIA + requests_quote(query), params={"size": most}) or {}
    return [h.get("_source") or {} for h in (data.get("hits") or {}).get("hits") or []]


def requests_quote(text):
    """text for a web address path."""
    from urllib.parse import quote
    return quote(text)


def mia_nudes(want, photos=False):
    """(name, picture address, rows) for Minneapolis Institute of Art works whose own record says "Public Domain"
    and whose image may be shown in full: nudes and academic studies (nude_candidate), or, with photos=True, nude
    photographs for nude_photo_studies (nude_photo_left_out)."""
    s, items, seen = session(), [], set()
    for q in NUDE_QUERIES:
        for r in mia_records(s, q, 500):
            oid = str(r.get("id") or "")
            if not oid or oid in seen:
                continue
            seen.add(oid)
            title = clean(r.get("title"))
            if r.get("rights_type") != "Public Domain" or r.get("image") != "valid" or \
                    r.get("Rights_Image_Display") not in (None, "", "Full") or not title:
                note("Mia", title or oid, "not public domain, or no full picture")
                continue
            kind = clean(r.get("classification") or r.get("object_name"))
            artist = clean(r.get("artist"))
            credit = f"Minneapolis Institute of Art, public domain: {title}" + (f", {artist}" if artist else "") + \
                f", https://collections.artsmia.org/art/{oid}"
            url = f"https://{int(oid) % 7}.api.artsmia.org/800/{oid}.jpg" if oid.isdigit() else ""
            text = clean(r.get("text") or r.get("description"))
            is_photo = bool(PHOTO_WORDS.search(f"{kind} {r.get('medium')}"))
            if photos:
                if is_photo and not nude_photo_left_out(title, text, kind=f"{kind} {r.get('medium')}"):
                    items.append((f"mia-{oid}.jpg", url, nude_photo_rows(title, credit)))
                continue
            item = nude_candidate("Mia", f"mia-{oid}.jpg", url, title, credit, kind, artist, clean(r.get("dated")),
                                  clean(r.get("medium")), text, clean(r.get("country")))
            if item:
                items.append(item)
        time.sleep(0.5)
        if len(items) >= want:
            break
    say(f"Minneapolis Institute of Art{' photographs' if photos else ''}: {len(items)} usable")
    return items[:want]


SMK = "https://api.smk.dk/api/v1/art/search/"
SMK_QUERIES = ("nøgen", "nøgne", "akt", "aktstudie", "nude", "naked", "model", "académie", "croquis")
# Danish and Dutch catalogue words of nude titles, in English; a title is used only when every word is known (or
# the record gives an English title).
FOREIGN_WORDS = {
    "nøgen": "nude", "nøgne": "nude", "halvnøgen": "half-nude", "akt": "nude study", "aktstudie": "nude study",
    "aktstudier": "nude studies", "model": "model", "modellen": "the model", "mandlig": "male", "kvindelig": "female",
    "kvinde": "woman", "kvinder": "women", "mand": "man", "mænd": "men", "liggende": "reclining", "stående": "standing",
    "siddende": "seated", "knælende": "kneeling", "ryg": "back", "set": "seen", "fra": "from", "ryggen": "behind",
    "studie": "study", "studier": "studies", "af": "of", "en": "a", "et": "a", "med": "with", "og": "and", "i": "in",
    "badende": "bathing", "figur": "figure", "figurer": "figures", "hoved": "head", "arm": "arm", "arme": "arms",
    "ben": "legs", "torso": "torso", "naakt": "nude", "naakte": "nude", "vrouw": "woman", "vrouwen": "women",
    "man": "man", "mannen": "men", "staand": "standing", "staande": "standing", "zittend": "seated",
    "zittende": "seated", "liggend": "reclining", "liggende_nl": "reclining", "knielend": "kneeling",
    "knielende": "kneeling", "op": "on", "de": "the", "het": "the", "een": "a", "van": "of", "met": "with",
    "rug": "back", "rugfiguur": "figure seen from behind", "studie_nl": "study", "academie": "académie",
    "académie": "académie", "naaktstudie": "nude study", "modelstudie": "model study", "badende_nl": "bathing",
    "baadster": "bather", "baadsters": "bathers", "bader": "bather", "figuur": "figure", "mannelijk": "male",
    "vrouwelijk": "female", "zijaanzicht": "side view", "vooraanzicht": "front view", "croquis": "sketch",
}


def foreign_title(title):
    """A short Danish or Dutch nude title in English when every word is known ("Nøgen mandlig model" -> "Nude male
    model"), else ""."""
    words = re.findall(r"[\wæøåÆØÅéÉ'-]+", clean(title).lower())
    out = []
    for w in words:
        english = FOREIGN_WORDS.get(w) or FOREIGN_WORDS.get(w + "_nl")
        if not english:
            return ""
        out.append(english)
    text = " ".join(out)
    return text[:1].upper() + text[1:] if text else ""


def smk_nudes(want):
    """(name, picture address, rows) for Statens Museum for Kunst works (its open API) with a public-domain or CC0
    licence on their own record, found by Danish and English nude words: the English title, or the Danish one put
    in English (foreign_title); nude_candidate checks them."""
    s, items, seen = session(), [], set()
    for q in SMK_QUERIES:
        offset = 0
        while offset < 2000:
            data = get_json(s, SMK, params={"keys": q, "offset": offset, "rows": 100, "lang": "en",
                                            "filters": "[has_image:true],[public_domain:true]"}) or {}
            records = data.get("items") or []
            for it in records:
                oid = clean(it.get("object_number") or it.get("id"))
                if not oid or oid in seen:
                    continue
                seen.add(oid)
                rights = clean(it.get("rights"))
                picture = it.get("image_thumbnail") or ""
                if not re.search(r"publicdomain/(mark|zero)", rights) or not picture:
                    note("SMK", oid, "not public domain, or no picture")
                    continue
                titles = it.get("titles") or []
                english = next((clean(t.get("title")) for t in titles if (t.get("language") or "").lower()
                                .startswith(("eng", "en"))), "")
                danish = next((clean(t.get("title")) for t in titles), "")
                title = english or foreign_title(danish)
                if not title:
                    note("SMK", danish, "no English title and the Danish one could not be put in English")
                    continue
                kind = clean(((it.get("object_names") or [{}])[0] or {}).get("name"))
                medium = ", ".join(clean(t) for t in (it.get("techniques") or [])[:2])
                artist = clean(((it.get("production") or [{}])[0] or {}).get("creator"))
                date = clean(((it.get("production_date") or [{}])[0] or {}).get("period"))
                credit = f"Statens Museum for Kunst (SMK), public domain ({rights}): {title}" + \
                    (f", {artist}" if artist else "") + f", {it.get('frontend_url', '')}"
                others = [danish, q if q in ("nøgen", "nøgne", "akt", "aktstudie") else ""]
                if q in ("nøgen", "nøgne", "akt", "aktstudie") and not body_packs.NUDITY_WORDS.search(title):
                    others.append("nude")             # found by a Danish nude word: the record is about a nude
                item = nude_candidate("SMK", f"smk-{re.sub(r'[^\w-]', '_', oid)}.jpg", picture, title, credit, kind,
                                      artist, date, medium, "", "Denmark" if not artist else "", others)
                if item:
                    items.append(item)
            offset += len(records)
            if len(records) < 100 or len(items) >= want:
                break
            time.sleep(0.5)
        if len(items) >= want:
            break
    say(f"SMK: {len(items)} usable")
    return items[:want]


RIJKS = "https://data.rijksmuseum.nl/search/collection"
RIJKS_SEARCHES = ({"title": "naakt"}, {"description": "naakt"}, {"title": "naakte"}, {"title": "academie"},
                  {"title": "modelstudie"}, {"title": "naaktstudie"}, {"title": "nude"})


def rijks_record(s, uri):
    """The fields of one Rijksmuseum object (its linked-data record, as the kit's adult_review_sources reads it), or
    None."""
    data = get_json(s, uri, params={"_profile": "edm-framed", "_mediatype": "application/ld+json"})
    if not data or "aggregatedCHO" not in data:
        return None
    c = data["aggregatedCHO"]

    def as_list(value):
        """A linked-data value as a list."""
        return value if isinstance(value, list) else [value] if value else []

    def first(value):
        """The first text of a value."""
        value = as_list(value)
        return clean(value[0]) if value and isinstance(value[0], str) else ""
    title, desc = c.get("title") or {}, c.get("description") or {}
    maker = ""
    for who in as_list(c.get("creator")):
        labels = as_list(who.get("http://www.w3.org/2004/02/skos/core#prefLabel") if isinstance(who, dict) else None)
        maker = next((clean(x.get("@value")) for x in labels if isinstance(x, dict) and x.get("@language") == "en"),
                     maker)
    kinds = []
    for t in as_list(c.get("dcType")) + as_list(c.get("http://www.europeanafashion.eu/edmfp/technique")):
        for x in as_list(t.get("http://www.w3.org/2004/02/skos/core#prefLabel") if isinstance(t, dict) else None):
            if isinstance(x, dict) and x.get("@language") == "en":
                kinds.append(clean(x.get("@value")))
    created = as_list(c.get("created"))
    date = next((clean(x.get("@value")) for x in created if isinstance(x, dict) and x.get("@language") == "en"), "")
    shown = (data.get("isShownBy") or {}).get("id", "")
    return {"title": first(title.get("en")), "title_nl": first(title.get("nl")), "desc_en": first(desc.get("en")),
            "maker": maker, "date": date, "kind": "; ".join(kinds), "rights": clean(data.get("edmRights")),
            "picture": shown.replace("/full/max/", "/full/1600,/"),
            "page": clean((data.get("isShownAt") or {}).get("id"))}


def rijks_nudes(want):
    """(name, picture address, rows) for Rijksmuseum works found by Dutch and English nude words, public domain or
    CC0 on their own record, with an English title (or a Dutch one put in English)."""
    s, lists = session(), []
    for search in RIJKS_SEARCHES:
        found, url, params = [], RIJKS, dict(search, imageAvailable="true")
        while url and len(found) < want * 3 + 20:
            data = get_json(s, url, params=params)
            if not data:
                break
            found += [(x["id"].rsplit("/", 1)[-1], x["id"]) for x in data.get("orderedItems") or []]
            url, params = (data.get("next") or {}).get("id"), None
        lists.append(found)
    items = []
    for oid, uri in take_turns(lists):
        if len(items) >= want:
            break
        time.sleep(0.2)
        r = rijks_record(s, uri)
        if not r or not re.search(r"publicdomain/(mark|zero)", r["rights"]) or not r["picture"]:
            note("Rijksmuseum", oid, "not public domain, or no picture")
            continue
        title = r["title"] or foreign_title(r["title_nl"])
        if not title:
            note("Rijksmuseum", r["title_nl"], "no English title and the Dutch one could not be put in English")
            continue
        credit = f"Rijksmuseum, public domain ({r['rights']}): {title}" + (f", {r['maker']}" if r["maker"] else "") + \
            f", {r['page']}"
        others = [r["title_nl"]] + (["nude"] if re.search(r"\bnaakt", r["title_nl"], re.I) else [])
        item = nude_candidate("Rijksmuseum", f"rijks-{oid}.jpg", r["picture"], title, credit,
                              r["kind"].split(";")[0], r["maker"], r["date"], "", r["desc_en"], "", others)
        if item:
            items.append(item)
    say(f"Rijksmuseum: {len(items)} usable")
    return items


EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EUROPEANA_QUERIES = ("nude", "naked", "nude study", "académie", "life drawing", "naakt", "nøgen", "Aktstudie",
                     "nudo", "desnudo")
EUROPEANA_FREE = re.compile(r"creativecommons\.org/(publicdomain/(zero|mark)/|licenses/by/\d)", re.I)


def europeana_nudes(want):
    """(name, picture address, rows) for Europeana artworks found by nude words in several languages, whose own
    rights statement is CC0, the Public Domain Mark or CC BY (never SA, NC or ND), with an English title (or one
    put in English by foreign_title). The key is the build's EUROPEANA_KEY (a repository secret in CI, the person's
    own setting locally; never in the repository), else Europeana's public test key."""
    s, lists = session(), []
    key = os.environ.get("EUROPEANA_KEY") or "api2demo"
    for q in EUROPEANA_QUERIES:
        data = get_json(s, EUROPEANA, params={"wskey": key, "query": q, "qf": "TYPE:IMAGE", "reusability": "open",
                                              "rows": 100, "profile": "rich"}) or {}
        found = []
        for it in data.get("items") or []:
            rights = " ".join(it.get("rights") or [])
            picture = (it.get("edmIsShownBy") or [""])[0]
            if not EUROPEANA_FREE.search(rights) or re.search(r"by-(sa|nc|nd)", rights) or not picture:
                note("Europeana", (it.get("title") or [""])[0], "licence not open, or no picture")
                continue
            # Only the provider's own English (Europeana adds machine translations to other records' titles, often
            # wrong), or a Danish or Dutch title put in English word for word.
            original = clean((it.get("title") or [""])[0])
            title = original if (it.get("language") or []) == ["en"] else foreign_title(original)
            if not title:
                note("Europeana", original, "no English title")
                continue
            kind = clean(((it.get("dcTypeLangAware") or {}).get("en") or it.get("dcType") or [""])[0])
            provider = clean((it.get("dataProvider") or ["Europeana"])[0])
            artist = clean((it.get("dcCreator") or [""])[0])
            if re.search(r"https?:|^#|^\d|_person$|^[A-F0-9-]{20,}$", artist):
                artist = ""                       # an identifier, not a name
            credit = f"{provider} via Europeana, {rights}: {title}" + (f", {artist}" if artist else "") + \
                f", https://www.europeana.eu/item{it['id']}"
            desc = clean((it.get("dcDescriptionLangAware") or {}).get("en", [""])[0]) if \
                isinstance(it.get("dcDescriptionLangAware"), dict) else ""
            others = [original] + (["nude"] if q in ("naakt", "nøgen", "Aktstudie", "nudo", "desnudo") else [])
            item = nude_candidate("Europeana", "europeana-" + re.sub(r"[^\w-]+", "_", it["id"])[-80:] + ".jpg",
                                  picture, title, credit, kind, artist, clean((it.get("year") or [""])[0]), "",
                                  desc, "", others)
            if item:
                found.append(item)
        lists.append(found)
        time.sleep(0.5)
    items = take_turns(lists)
    say(f"Europeana: {len(items)} usable")
    return items[:want]


# ----------------------------------------------------------------- The J. Paul Getty Museum (Linked Art)

GETTY_NUDE_WORDS = r"nude|naked|nudity|acad[eé]mie|academy figure|life study|[eé]corch|bather|figure study"
GETTY_EROTIC_WORDS = r"erotic|shunga|lovers|intercourse|making love|lovemaking|amorous|copulat|kama sutra|mithuna"
GETTY_SEEN = {}                    # {object address: (record, picture, rights)}: read once for all three packs


def getty_items(want, role):
    """(name, picture address, rows) of Getty Museum objects (linked_art.py: its SPARQL endpoint finds them by
    their names, then each object's Linked Art record and its image's record are read, paced), the IMAGE'S OWN
    rights statement CC0 or the Public Domain Mark. role decides the pack and the rules: "nudes" (museum_art_nudes:
    nude_candidate; not photographs, not sexual), "erotic" (erotic_art: erotic_left_out, the review route and the
    allow-list as the other museums), "photos" (nude_photo_studies: nude_photo_left_out)."""
    import linked_art as la
    s = session()
    pattern = GETTY_EROTIC_WORDS if role == "erotic" else GETTY_NUDE_WORDS
    uris = la.getty_objects(s, pattern)
    pass_random(f"getty-{role}").shuffle(uris)
    say(f"Getty Museum ({role}): {len(uris)} objects found by their names")
    items = []
    for uri in uris:
        if len(items) >= want:
            break
        if uri not in GETTY_SEEN:
            GETTY_SEEN[uri] = la.getty_record(s, uri)
        record, picture, rights = GETTY_SEEN[uri]
        if not record:
            continue
        f = la.plain_fields(record)
        title, oid = f["title"], uri.rsplit("/", 1)[-1]
        if not picture or rights not in ("CC0", "Public Domain Mark"):
            note("Getty", title or oid, f"its image is not CC0 or public domain ({rights or 'no open image'})")
            continue
        home = next((x["id"] for x in la.as_list(record.get("subject_of")) if isinstance(x, dict) and
                     "getty.edu/art/collection" in str(x.get("id", ""))), uri)
        credit = f"The J. Paul Getty Museum, {rights} (open content): {title}" + \
            (f", {f['artist']}" if f["artist"] else "") + f", {home}"
        name, kind_text = f"getty-{oid[:36]}.jpg", f"{f['kind']} {' '.join(la.types(record))} {f['medium']}"
        is_photo = bool(PHOTO_WORDS.search(kind_text))
        if role == "photos":
            if is_photo and not nude_photo_left_out(title, f["text"], kind=kind_text):
                items.append((name, picture, nude_photo_rows(title, credit)))
            continue
        if role == "erotic":
            why = erotic_left_out(f["text"], f["medium"], kind=kind_text, title=title)
            if reviewed(why, "Getty Museum", oid, title, home):
                why = ""
            if why:
                note("Getty", title, why)
                continue
            items.append((name, picture, erotic_rows(credit, title, f["kind"], f["artist"], f["date"], f["medium"],
                                                     f["text"], (), "museum", f["place"])))
            continue
        item = nude_candidate("Getty", name, picture, title, credit, f["kind"], f["artist"], f["date"],
                              f["medium"], f["text"], f["place"])
        if item:
            items.append(item)
    say(f"Getty Museum ({role}): {len(items)} usable")
    return items


# ----------------------------------------------------------------- The Met, a second pass (wider words)

# The owner's list (November 2026): more words and the departments where nudes, erotica and nude photographs are.
MET_MORE_TERMS = ("nude", "naked", "bather", "bathers", "Venus", "Adam and Eve", "Susanna", "Bathsheba", "Leda",
                  "académie", "figure study", "life drawing", "torso", "odalisque", "nymph", "satyr", "Danaë",
                  "Three Graces", "Saint Sebastian", "Hercules", "Apollo", "kouros", "male nude", "female nude")
# Drawings and Prints, Photographs, Greek and Roman Art, Asian Art, Modern Art, European Sculpture and Decorative Arts.
MET_MORE_DEPARTMENTS = (9, 19, 13, 6, 21, 12)
MET_SEEN = {}                      # {object id: record}: read once for all three packs


def met_ids(s, params, most=2000):
    """Object ids of one Met v1.1 search (with images), up to most."""
    ids, offset = [], 0
    while len(ids) < most:
        page = get_json(s, MET + "v1.1/search", params=dict(params, hasImages="true", limit=100, offset=offset)) \
            or {}
        found = page.get("objectIDs") or []
        ids += found
        offset += len(found)
        if not found or offset >= (page.get("total") or 0):
            break
        time.sleep(0.2)
    return ids[:most]


def met_known_ids(s):
    """The Met objects the other readers already take: those tagged Female or Male Nudes (art_nudes and
    museum_art_nudes, body_packs.met_items) and those of the erotic searches (met_erotic)."""
    known = set()
    for tag in body_packs.MET_TAGS:
        known.update(met_ids(s, {"q": tag, "tags": "true"}, 6000))
    for q in MET_QUERIES:
        known.update(met_ids(s, {"q": q}, 3000))
    return known


def met_more(want, role, s=None, known=None):
    """(name, picture address, rows) of Met objects found by MET_MORE_TERMS (all departments, and each of
    MET_MORE_DEPARTMENTS) that the other readers do not take (met_known_ids), isPublicDomain, by role: "nudes"
    (museum_art_nudes: nude_candidate), "erotic" (erotic_art: erotic_left_out, the review route), "photos"
    (nude_photo_studies: nude_photo_left_out)."""
    s = s or session()
    known = met_known_ids(s) if known is None else known
    lists = []
    for term in MET_MORE_TERMS:
        lists.append(met_ids(s, {"q": term}, 400))
        for department in MET_MORE_DEPARTMENTS:
            lists.append(met_ids(s, {"q": term, "departmentId": department}, 100))
    ids = [i for i in take_turns([[(x,) for x in l] for l in lists]) if i[0] not in known]
    say(f"Met second pass ({role}): {len(ids)} objects not taken by the other readers")
    items = []
    for (oid,) in ids:
        if len(items) >= want:
            break
        if oid not in MET_SEEN:
            time.sleep(0.1)
            MET_SEEN[oid] = get_json(s, f"{MET}v1/objects/{oid}") or {}
        o = MET_SEEN[oid]
        title = clean(o.get("title"))
        picture = o.get("primaryImage") or o.get("primaryImageSmall")
        if not o.get("isPublicDomain") or not picture or not title:
            continue
        tags = [t.get("term", "") for t in (o.get("tags") or [])]
        kind = f"{o.get('classification')} {o.get('objectName')} {o.get('medium')}"
        artist = clean(o.get("artistDisplayName"))
        credit = f"The Metropolitan Museum of Art, public domain (CC0): {title}" + (f", {artist}" if artist else "") \
            + f", {o.get('objectURL', '')}"
        name = f"met-{oid}.jpg"
        if role == "photos":
            if PHOTO_WORDS.search(kind) and not nude_photo_left_out(title, " ".join(tags), kind=kind):
                items.append((name, picture, nude_photo_rows(title, credit)))
            continue
        why = erotic_left_out(" ".join(tags), o.get("objectName"), o.get("medium"), o.get("culture"), kind=kind,
                              title=title)
        if role == "erotic":
            if reviewed(why, "The Met", oid, title, o.get("objectURL", "")):
                why = ""
            if not why:
                items.append((name, picture, erotic_rows(credit, title, o.get("objectName"), artist,
                                                         o.get("objectDate"), o.get("medium"), "", tags, "museum",
                                                         o.get("culture") or o.get("country"))))
            continue
        if why == NOT_SEXUAL:
            item = nude_candidate("Met", name, picture, title, credit, o.get("objectName"), artist,
                                  o.get("objectDate"), o.get("medium"), "", o.get("culture") or o.get("country"),
                                  tags)
            if item:
                items.append(item)
    say(f"Met second pass ({role}): {len(items)} usable")
    return items


# More Smithsonian units read from the open-access data (as body_packs.si_items): Cooper Hewitt (drawings and
# prints), the Freer and Sackler galleries, the National Museum of African Art and the Hirshhorn.
SI_MORE_UNITS = ("chndm", "fsg", "nmafa", "hmsg")


def si_more_nudes(want):
    """(name, picture address, rows) for CC0 nudes of SI_MORE_UNITS (body_packs.si_items with this pack's screen)."""
    def screen(source, title, *texts, kind=""):
        """nudes_left_out for works art_nudes does not read."""
        return nudes_left_out(source, title, *texts, kind=kind, routed=True)
    return body_packs.si_items(want, drop=screen, units=SI_MORE_UNITS)


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
    answer = plain(lead(title, singular_kind(kind), artist, date, medium))
    words = first_sentences(plain(text), 90) if text else ""
    if words and words.lower() not in answer.lower():
        answer += " " + sentence(words)
    tags = [plain(t).lower() for t in tags if clean(t) and len(clean(t)) < 40]
    if tags:
        answer += " " + sentence(f"The {owner}'s subject tags: " + ", ".join(dict.fromkeys(tags)))
    record_words = " ".join(clean(t) for t in (title, text, " ".join(tags)) if t)
    if not SEX_ACT.search(answer) and TOPIC.search(NOT_TOPIC.sub(" ", record_words)):
        answer += f" The {owner} files it as erotic art."       # only when the record's own words say so
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
    """The nude_photo_studies pack: Wellcome Collection photographs (wellcome_nude_photos) and the Minneapolis
    Institute of Art's public-domain nude photographs (mia_nudes(photos=True)), each by nude_photo_left_out."""
    items = wellcome_nude_photos(int(limit * 1.0) + 2)
    for key, collect in (("mia", lambda n: mia_nudes(n, photos=True)), ("getty", lambda n: getty_items(n, "photos")),
                         ("met_more", lambda n: met_more(n, "photos"))):
        try:
            items += collect(int(limit * 0.3) + 2)
        except Exception as error:  # noqa: BLE001 - one source down: the others
            say(f"{key} photographs: left out ({error})")
    return finish("nude_photo_studies", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- the packs

# Sources looked at for museum_art_nudes and nude_photo_studies and not read yet (November 2026), with the reason.
MUSEUM_NUDES_LATER = {
    "Paris Musées (incl. Petit Palais, Beaux-Arts collections)": "its API needs a personal token: for the local kit",
    "Harvard Art Museums": "its API needs a key, and its robots.txt disallows all robots: not read",
    "Brooklyn Museum": "its API needs a key: for the local kit",
    "Te Papa": "its API needs a key: for the local kit",
    "Finnish National Gallery": "its API needs a key: for the local kit",
    "Nationalmuseum Sweden": "open API not explored in this pass",
    "Yale University Art Gallery and Yale Center for British Art": "their search (LUX) answers automated readers "
        "with an AWS WAF challenge and their sites with a Cloudflare challenge; the IIIF manifests are open but "
        "cannot be searched, and walking every manifest would go against those challenges: not read",
    "Princeton University Art Museum": "its data API and IIIF manifests give no rights statement on the record "
        "(\"restrictions: None\" is not public domain or CC0), and its website is behind a Cloudflare challenge: "
        "not in the CI packs; a personal-use reader for the local kit is possible later",
    "Walters, LACMA, Barnes, RISD Museum": "no current open search API found in this pass",
    "Royal Academy of Arts": "no open API and no open licence on its images: not read",
    "Wikimedia Commons (nude paintings, sculpture, academic drawings, life drawing)": "Commons refused every request "
        "from the build machine (429) during this pass, so category names could not be checked: a later pass, in "
        "the Commons lane",
}

# Each source's share of erotic_art (a source with fewer gives what it has).
EROTIC_SHARES = (("met", met_erotic, 0.25), ("aic", aic_erotic, 0.1), ("cma", cma_erotic, 0.1),
                 ("wellcome", wellcome_erotic, 0.2), ("commons", commons_erotic, 0.35),
                 ("getty", lambda n: getty_items(n, "erotic"), 0.05), ("met_more", lambda n: met_more(n, "erotic"), 0.05))
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
    # Museums art_nudes does not read (their works are never in art_nudes): the Minneapolis Institute of Art, SMK,
    # the Rijksmuseum and more Smithsonian units, each about a tenth of the pack.
    for key, collect in (("mia", mia_nudes), ("smk", smk_nudes), ("rijks", rijks_nudes), ("si_more", si_more_nudes),
                         ("europeana", europeana_nudes), ("getty", lambda n: getty_items(n, "nudes")),
                         ("met_more", lambda n: met_more(n, "nudes"))):
        try:
            items += collect(max(2, round(limit * 0.1 * 1.3)))
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
                         "Fine-art nudity and academic studies of the nude (Madonna and Child, putti and cherubs, "
                         "mythology, bathers, lovers, classical statues, life drawings) that art_nudes leaves out or "
                         "does not read, from open-access collections, each work credited below with its own licence: "
                         "The Metropolitan Museum of Art (public domain, CC0), Art Institute of Chicago (CC0), "
                         "Cleveland Museum of Art (CC0), National Gallery of Art, Washington (CC0), Smithsonian "
                         "Institution (CC0), Minneapolis Institute of Art (public domain), Statens Museum for Kunst "
                         "and Rijksmuseum (Public Domain Mark or CC0), Europeana partners (CC0, Public Domain Mark or "
                         "CC BY), The J. Paul Getty Museum (open content, CC0 per image). No photographs, no sexual acts or sexual violence, and no child "
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
    "museum_art_nudes": 2000,       # the first five museums' left-outs, Mia (~100), SMK (~200), Rijksmuseum,
                                     # Europeana (~150), more Smithsonian units, routed works (test, 19 Nov 2026)
    "erotic_art": 1500,
    "nude_photo_studies": 300,     # Wellcome (147 usable in the test) and Mia's public-domain photographs
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
