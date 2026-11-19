"""REVIEW-ONLY picture collections about ADULT SEXUALITY: nudity, intimacy, sexual acts and positions, sex toys and
sexual-health items, for a private, local picture describer used by a BLIND ADULT.

Why: a blind adult cannot otherwise know what such a picture shows (an artwork in a museum, a sex-education drawing,
a product photo of a sex toy or a condom). The describer should be able to say plainly, accurately and without
judgement who is there, what they are doing, the position, what is visible and the setting.

Nothing here trains by itself. Each collection is downloaded into a "Describe pictures" workspace
(describe_package.py) where every picture arrives with a DRAFT description (made from the source's own title,
caption, subject tags or description, tidied into plain English) and the status "needs another look", never
"described" or "checked". A sighted, trusted adult screens every picture (REVIEW-INSTRUCTIONS.txt, written into the
workspace), DELETES anything that shows or may show anyone under 18, anything non-consensual, violent, private or
leaked, corrects the description, and marks a picture "checked" only when everything is right.

HARD RULES kept by every fetch function here (screen() below):
  - ADULTS ONLY. A record is left out when its title, description, tags, categories or file name mention or suggest
    a child or young person (review_sources.CHILD, plus MINOR here: putto, cupid, cherub, Eros, Ganymede, young,
    youth, maiden, school (not an art school such as "Kano school"), student, uniform, petite, little, virgin and
    the same in Dutch, French, German, Italian and Spanish) or give an age under 18.
  - CONSENT and NO VIOLENCE. Left out: rape, abduction, assault, force, captives, death and wounds, whipping and
    bondage, sleep or drunkenness (no consent), voyeurs and hidden cameras, leaked or stolen pictures, incest, and
    the myths and stories that are about rape, abduction or a minor (Leda, Europa, the Sabine women, Lucretia,
    Danae, Susanna, Io, Antiope, Callisto, Proserpina, Bathsheba, Lot, Potiphar's wife, satyrs and nymphs and more;
    MYTH below). Also bestiality and creatures (animals, the octopus print, kappa and the like).
  - ARTWORKS (museums, Wellcome, Europeana): open-access records only (CC0, public domain, CC BY, CC BY-SA, checked
    per item), and the record must show an artwork (print, painting, drawing, sculpture, ceramic, fresco ...).
    PHOTOGRAPHS from museum and library records are left out: old erotic photographs are anonymous, and many show
    minors or people photographed without real consent.
  - VINTAGE PHOTOGRAPHS (commons_vintage_named) are used ONLY when the person is NAMED (Commons "depicts" links a
    Wikidata person) and adulthood is PROVABLE: Wikidata's birth date (at least to the year) and the photo's own
    date show the person was 18 or over (19 or more years apart, or the exact dates when both are known). Public
    domain only, and taken in 1930 or earlier, or released by the photographer under CC0 or CC BY. The name, birth
    year and photo year are written in CREDITS.txt.
  - OTHER PHOTOGRAPHS only from Wikimedia Commons sexual-content categories (Commons requires the consent of
    identifiable people: COM:SEX, COM:IDENT). Photographs of people must be the uploader's "own work", be in no
    deletion, copyright or identity-problem category, and have no youthful wording ("teen", "girl", "boy", "young",
    school uniforms). Product photos (sex toys, condoms) must show no person, or follow the same rules.
  - US PATENT DRAWINGS (us_patent_drawings) only from the USPTO Open Data Portal (its API, with a free key in
    USPTO_ODP_API_KEY; skipped with a plain message without one). Public domain: the USPTO says the text and
    drawings of a patent are typically not subject to copyright, except where the patent carries a copyright or
    mask-work notice (37 CFR 1.71(d)/(e)); any patent with copyright or mask-work wording is left out. Each patent's
    title, abstract and figure descriptions pass screen(), and its whole text must not mention a child, an animal,
    harm, restraint, BDSM or non-consensual use. Technical drawings could in principle be an open collection, but
    they show sex toys and sometimes adult anatomy, so they stay review-only with content "sexual" like the rest.
  - PRODUCT PHOTOS through OPENVERSE (openverse_products) show NO PERSON: any person, body or youthful word in the
    title, description or tags (also the machine-made tags) leaves the picture out, and so does any sexual act,
    fetish or BDSM word, any adult site and any sensitive flag. Only sites whose terms allow re-use by program are
    used (Wikimedia Commons, open museums and libraries; never Flickr, whose terms forbid robots). Commons files are
    checked again on Commons and left out when the Commons collections here already read them. Openverse's rate
    limits are kept and its terms followed (credit, "not endorsed by Openverse").
  - NOTHING from porn sites, scraped web sets (LAION and the like), Reddit, forums or any source of unknown
    provenance. When unsure, a record is left out.

How to use (for the kit's own code):
  ADULT_REVIEW_SOURCES  a list of plain dicts: key, name, category ("open", "share-alike", "noncommercial",
                        "research"), licence, terms, terms_summary, credit, content ("sexual"), cap, download (size),
                        fetch (a function fetch_<key>(folder, cap, say)), plus "review_only": True.
  NOT_INCLUDED          sources looked at and left out, with the reason (including sign-up-only ones).
  CONTRACT_CANDIDATES   companies and bodies whose catalogues could be licensed by contract (nothing downloaded).
  Each fetch function downloads into folder (made into a describing workspace when it is not one yet), skips
  pictures already there or already tried, so a stopped run carries on where it was, and returns a plain summary.
  Each also says up to five titles it left out, with the reason, so the filters can be seen working.

    python adult_review_sources.py <key> <folder> [cap]      (a quick test of one collection)

PLUMBING the rest of the kit needs (not done here; other files are being edited by others):
  - own_data.check_folder must use only "checked" pictures from a workspace whose describing.json has
    "review_only": true (the same rule as review_sources.py).
  - Content "sexual" (describing.json "content": "sexual", "needs_explicit_choice": true) may be used only when the
    person makes an extra, explicit choice for it; it must never be used for picture-making training and never be
    put in a published model ("never_for_picture_making" and "never_publish" are true in describing.json).

Only requests and Pillow are needed (as for the rest of the kit; patent drawing sheets are read out of the USPTO's
PDF by pdf_images() here, with Pillow). Nothing is sent anywhere except the downloads (and the searches they need;
the USPTO key goes only to api.uspto.gov).
"""

import io
import os
import random
import re
import shutil
import struct
import time
import zipfile
import zlib

import describe_package as dp
import review_sources as rs

CONTENT = "sexual"
REVIEW_FILE = rs.REVIEW_FILE
CREDITS_FILE = rs.CREDITS_FILE
SHOW_LEFT_OUT = 5                         # how many left-out titles each fetch says (to show the filters work)

REVIEW_INSTRUCTIONS = """REVIEW-ONLY COLLECTION: {name}

These pictures are about ADULT SEXUALITY: nudity, intimacy, sexual acts and positions, sex toys and sexual-health
items. They were collected so that a blind adult's private, local describer can say plainly and accurately what
such a picture shows. NONE of them is used for training until a person has checked it. They are never used to make
pictures and never put in a published model.

This collection must be screened by a sighted, trusted ADULT.

For every picture:
1. DELETE the picture (do not just skip it) when it shows, or may show, anyone under 18. If you are not sure that
   everyone is an adult, delete it. In old artworks, winged children (cupids, putti, cherubs) count as children:
   delete the picture.
2. DELETE any picture that shows or suggests anything non-consensual or violent (force, rape, abduction, someone
   asleep, drunk or unaware, hurting, restraint, a hidden camera), and anything involving an animal.
3. DELETE any picture that seems private or leaked: a photograph that looks taken without the person knowing, a
   picture that looks copied from a porn site, or any photograph whose source you doubt.
4. Read the draft description. It was made from the source's own title, caption or record and may be wrong,
   too thin or in the wrong order. Correct it so that it says plainly, accurately and without judgement:
   who is present (how many adults, and what can be seen of them), what they are doing, their positions, what is
   visible and the setting. Use plain adult words (penis, vulva, breasts, sex, oral sex), neither crude nor coy.
   Do not guess at things you cannot see. A note "needs a fuller description" means the record said too little:
   please write the description from the picture.
5. Mark the picture "checked" ONLY when everything is right: everyone is clearly an adult, nothing is
   non-consensual, violent or private, and the description is correct.

Only checked pictures are ever trained on. Pictures that are new, described, skipped or need another look are
never used from this collection.

Where each picture comes from, and its licence, is in CREDITS.txt and in each picture's notes.
Source: {credit}
Licence or terms: {licence}
"""

# ----------------------------------------------------------------- filters

# Words that mention or suggest a child or young person, beyond review_sources.CHILD. Wide on purpose; English,
# Dutch, French, German, Italian and Spanish (museum records are not always in English).
MINOR = re.compile(
    r"\b(putt[oi]s?|puttini|cupids?|amor(ino|ini|etto|etti|ini)?|amoretti|cupido|cherub\w*|ganymed\w*|young\w*|"
    r"youth\w*|juvenile\w*|maiden\w*|lolita\w*|nymphets?|schoolgirls?|schoolboys?|students?|uniforms?|petite|"
    r"barely legal|virgin\w*|innocen\w*|little|lads?|lass(ie)?s?|teenage\w*|tween\w*|loli|shota\w*|chibi|"
    r"kind|kinderen|kindje\w*|meisje\w*|jongen\w*|jonge|knaap\w*|jeune\w*|enfant\w*|fillette\w*|garçon\w*|"
    r"mädchen|knabe\w*|junge[nr]?|jugend\w*|bambin\w*|fanciull\w*|ragazz\w*|niñ[oa]s?|joven\w*|muchach\w*|"
    r"hylas|narcissus|adonis|hyacinth\w*|endymion|attis|psyche|embryo\w*)\b", re.I)

# "kind" is the Dutch and German word for a child, but in English it means "sort": "a kind of", "this kind", "all
# kinds". Those English uses are taken out before MINOR looks at the text, so they no longer leave a record out.
ENGLISH_KIND = re.compile(
    r"\b(?:a|the|this|that|these|those|any|some|every|one|each|what|which|same|other|another|all|its|their|"
    r"his|her|our|many|several|various|different|unusual|rare|first|only|new|similar)\s+kinds?\b|\bkinds?\s+of\b",
    re.I)

# "school" is a child word, except an art school ("Kano school", "school of Rembrandt").
ART_SCHOOL = re.compile(
    r"\b(?!(?:Boarding|High|Primary|Secondary|Grammar|Middle|Elementary|Sunday|Catholic|Public|Private|Girls'?|"
    r"Boys'?|Nursery|Junior|Senior|Summer|Night|Riding|Dance|Ballet)\b)[A-Z][\w'-]+ [Ss]chool\b(?! ?(girl|boy|"
    r"uniform|child|pupil|student))|\b[Ss]chool of (?=[A-Z])")

# Violence, no consent, private or leaked pictures (case does not matter).
VIOLENCE = re.compile(
    r"\b(rap(e|ed|es|ing|ist|ists)|ravish\w*|abduct\w*|kidnap\w*|assault\w*|violen\w*|forc(ed|ibly|ing)|coerc\w*|"
    r"captiv\w*|slave\w*|prisoners?|tortur\w*|murder\w*|kill\w*|death|dead|dying|corpses?|blood\w*|wound\w*|"
    r"whip\w*|flagell\w*|beat(ing|en)|sadis\w*|masochis\w*|bdsm|bondage|shibari|bound|tied|ropes?|chain(ed|s)?|"
    r"gag(ged|s)?|spank\w*|punish\w*|chastis\w*|humiliat\w*|wars?|battles?|executions?|sleep\w*|asleep|drunk\w*|"
    r"intoxica\w*|unconscious|drugged|voyeur\w*|peep\w*|spy\w*|spying|surprised|hidden cameras?|upskirt\w*|"
    r"downblouse|creep\w*|leak\w*|revenge|stolen|hacked|non-?consensual|without (her|his|their) (consent|knowledge)"
    r"|unaware|dogging|in public|public sex|sex in public|outdoor sex|glory ?holes?|exhibitionis\w*|incest\w*|martyr\w*|crucif\w*|sacrific\w*|suicide|severed|beheaded|weapons?|swords?|daggers?|guns?|"
    r"verkracht\w*|ontvoer\w*|geweld\w*|viol|enlèvement|vergewaltig\w*|stupro|violación|seduc\w*|fouets?|"
    r"fess[ée]e?s?|verges|peitsch\w*|züchtig\w*|rute|frust[ae]|látigo|azot\w*|orties blanches|"
    r"van ma[eë]le|discipline|dominatri\w*|femdom|slaves?)\b", re.I)

# Stories about rape, abduction or a minor, and other names that need their capital letter (case matters).
MYTH = re.compile(
    r"\b(Leda|Europa|Sabines?|Lucretia|Lucrece|Tarquin\w*|Danae|Danaë|Susann?ah?|Io|Antiope|Callisto|Proserpin\w*|"
    r"Persephone|Pluto|Hades|Philomela|Tereus|Cassandra|Ajax|Dinah|Tamar|Bathsheba|Lot|Potiphar\w*|Pasipha[eë]|"
    r"Daphne|Syrinx|Arethusa|Boreas|Orithyia|Deianira|Nessus|Lapiths?|Centaur\w*|Satyrs?|Pan|Fauns?|Silenus|"
    r"Hermaphrodit\w*|Salmacis|Medusa|Thetis|Semele|Judith|Holofernes|Salome|Cleopatra|Sebastian|Andromeda|"
    r"Eros|Angelica|Ruggiero|Rinaldo|Armida|Zeus|Jupiter|Jove|Apollo|Poseidon|Neptune|Triton\w*|Nereid\w*)\b")

# Animals and creatures (bestiality is never allowed; animals in erotic scenes are left out altogether).
ANIMAL = re.compile(
    r"\b(animals?|beasts?|bestial\w*|zoophil\w*|horses?|stallions?|mares?|dogs?|swans?|bulls?|goats?|donkeys?|"
    r"octop\w*|tentacle\w*|monsters?|creatures?|demons?|kappa|foxe?s?|serpents?|snakes?|apes?|monkeys?|pigs?|"
    r"sheep|rabbits?|hares?|birds?|cocks? and hens?|hens?|deer|stags?|interspecies|aliens?|extraterrestrials?|"
    r"exophilia|gamiani|hond\w*|paard\w*|dier\w*)\b", re.I)

# Photo-only words: youthful or doubtful wording and Commons problem categories.
PHOTO_DOUBT = re.compile(
    r"\b(teen\w*|girls?|boys?|young\w*|school\w*|uniform\w*|college|coed\w*|amateur porn|porn\w*|xxx|onlyfans|"
    r"camgirl\w*|webcam\w*|sex tape|leak\w*|ex-?girlfriend|ex-?boyfriend|hidden|candid|creepshot\w*|"
    r"stolen|scraped|reddit|tumblr|imgur|xhamster|pornhub|xvideos|redtube|youporn|motherless|femboys?|twinks?|"
    r"boyish|girlish|youthful|baby ?face\w*|childlike|barely|tiny|small ?(girl|boy|teen)|daddy|step-?\w+)\b", re.I)
PROBLEM_CATEGORY = re.compile(r"(deletion|copyright violation|possible copyright|unidentified|no permission|"
                              r"missing permission|personality rights warning|consent missing|"
                              r"without consent|flickr review needed|license review needed|"
                              r"nominated|disputed|speedy|unknown source|no source)", re.I)

# What a museum record must be: an artwork, not a photograph or a book cover.
ART_KIND = re.compile(
    r"\b(prints?|woodblock\w*|woodcut\w*|etching\w*|engraving\w*|lithograph\w*|mezzotint\w*|aquatint\w*|"
    r"drawing\w*|sketch\w*|paintings?|painted|watercolou?r\w*|gouache\w*|ink|oil on|tempera|fresco\w*|murals?|"
    r"sculpture\w*|statue\w*|statuette\w*|figure|figurine\w*|relief\w*|carv\w*|bronze|marble|terracotta|ivory|"
    r"ceramic\w*|porcelain|pottery|vessel\w*|vases?|bowls?|cups?|kylix|amphora\w*|krater\w*|lekythos|netsuke|"
    r"scrolls?|albums?|folio\w*|leaf|leaves|miniature\w*|illustration\w*|illuminat\w*|manuscript\w*|book|books|"
    r"ehon|shunga|surimono|kakemono|tile|textile|embroider\w*|lacquer\w*|plaque\w*|medal\w*|coin|gem|cameo\w*|"
    r"intaglio|lamp|oil lamp|mirror|tsuba|inro|panel|box|boxes|saucers?|dish(es)?|plates?|teapots?|jars?|"
    r"snuff ?box\w*)\b", re.I)
PHOTO_WORDS = re.compile(
    r"\b(photograph\w*|photos?|albumen|gelatin silver|silver gelatin|daguerreotype\w*|ambrotype\w*|tintype\w*|"
    r"carte(s)? de visite|cabinet card\w*|stereograph\w*|stereoview\w*|stereo card\w*|collodion|negatives?|"
    r"lantern slide\w*|glass plate\w*|platinum print|cyanotype\w*|photogravure\w*|postcards?|film still\w*|"
    r"foto\w*|photographie\w*)\b", re.I)

# What a broad museum search must be about (so that "erotic" in a long essay on a landscape does not count).
TOPIC = re.compile(
    r"\b(erotic\w*|erotica|erotisch\w*|érotique\w*|shunga|spring (pictures?|prints?|palace)|makura-?e|higa|"
    r"sex|sexual\w*|sexuality|lovers?|love-?making|lovemaking|making love|amorous|intimate|intimacy|"
    r"(couple|lovers) embracing|embracing (couple|lovers)|kiss\w*|amorous couples?|loving couples?|nudes?|nudity|naked|undress\w*|bath(ing|er|ers)|courtesans?|brothel\w*|mithuna|maithuna|"
    r"kama ?sutra|kamasutra|rati|phall\w*|genital\w*|penis|vulva|coit\w*|intercourse|copulat\w*|venus|"
    r"odalisques?|boudoir|in bed|bedroom|minnaars|naakt|vrij(en|end)|liefdes\w*|bordeel)\b", re.I)

# Words that are not useful in a description (counted out of the "useful words" of a record).
STOP = set("""a an the of and or in on at to from by for with without as is are was were be been this that these
those it its his her their he she they them sheet album page plate leaf leaves folio no number nos part volume vol
series set untitled from title titled print prints woodblock woodcut book books illustrated illustration japan japanese
edo period meiji ink color colour colors colours on paper silk sumizuri e nishiki recto verso detail one two three
first second third fragment object image work artwork collection museum gift purchase fund ca circa century unknown
artist anonymous unidentified attributed style school workshop after copy""".split())

# Plain English for catalogue words and crude words (the source's meaning kept; nothing invented).
PLAIN = [(re.compile(p, re.I), w) for p, w in [
    (r"\bsumizuri-e\b", "black-ink print (sumizuri-e)"), (r"\bnishiki-e\b", "full-colour print (nishiki-e)"),
    (r"\bshunga\b", "shunga (Japanese erotic art)"), (r"\bhiga\b", "higa (erotic pictures)"),
    (r"\bmakura-?e\b", "makura-e (erotic pictures)"), (r"\b(maithuna|mithuna)\b", r"\1 (an amorous couple)"),
    (r"\brecto\b", "front"), (r"\bverso\b", "back"), (r"\bcoitus\b", "sex"), (r"\bcoital\b", "sexual"),
    (r"\bcopulating\b", "having sex"), (r"\bcopulation\b", "sex"), (r"\bfucking\b", "having sex"),
    (r"\bfucks?\b", "has sex with"), (r"\bcocks?\b", "penis"), (r"\bdicks?\b", "penis"), (r"\bpuss(y|ies)\b", "vulva"),
    (r"\btits\b", "breasts"), (r"\bboobs?\b", "breasts"), (r"\bcum\b", "semen"), (r"\bblow-?jobs?\b",
                                                                                  "oral sex on a penis (fellatio)"),
    (r"\bhand-?jobs?\b", "touching a penis by hand"), (r"\bdoggy[- ]?style\b", "from behind (doggy style)"),
    (r"\bmissionary position\b", "missionary position (one partner lying on the back, the other on top, facing)"),
    (r"\bcowgirl position\b", "woman-on-top position (cowgirl)"), (r"\bspooning\b", "lying on their sides, one "
                                                                                    "behind the other (spooning)"),
    (r"\bsixty-?nine\b|\b69 position\b", "the 69 position (each giving oral sex to the other at the same time)"),
    (r"\bcunnilingus\b", "oral sex on a vulva (cunnilingus)"), (r"\bfellatio\b", "oral sex on a penis (fellatio)"),
    (r"\bdildo\b", "dildo (a sex toy shaped like a penis)"), (r"\bbutt plug\b", "butt plug (an anal sex toy)"),
    (r"\bharigata\b", "harigata (a Japanese dildo)"), (r"\bnayika\b", "nayika (the heroine)"),
    (r"\bsakhi\b", "sakhi (her confidante)"), (r"<[^>]+>", " "),
]]

LEFT_OUT_CAP = 200                        # at most this many left-out examples are kept per run


def clean(text):
    """Text with its spaces tidied and HTML removed ("" for nothing)."""
    return rs.no_tags(text)


def plain(text):
    """Text with catalogue words and crude words put in plain adult English."""
    text = clean(text)
    for pattern, words in PLAIN:
        text = pattern.sub(words, text)
    return clean(text)


# Phrases that look on topic but are not ("Art Lovers", the Indian "Shunga period").
NOT_TOPIC = re.compile(r"\b(art|music|nature|book|wine|dog|cat|horse|garden|opera|theatre|theater) lovers\b|"
                       r"\blovers of\b|\bshunga (period|dynasty|empire|kingdom)\b|\bcouples? of (years|days)\b", re.I)


def a_an(words):
    """words with "A" or "An" in front, as English needs ("An album leaf", "A print")."""
    return ("An " if re.match(r"[aeiouAEIOU]", words or "") else "A ") + words


ENGLISH_WORDS = set("the a an of and with in on by is are her his their two woman women man men couple from at "
                    "to this which who scene print painting lovers".split())


def is_english(text):
    """True when a text reads as English (enough common English words); short texts count as English."""
    words = re.findall(r"[A-Za-z']+", clean(text).lower())
    if len(words) < 4:
        return not re.search(r"[À-ÿĀ-ž]", clean(text))   # a short text with accented letters is not English
    return sum(w in ENGLISH_WORDS for w in words) / len(words) >= 0.12


def useful_words(*texts):
    """How many words of the texts say something about the picture (catalogue words not counted)."""
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", " ".join(clean(t) for t in texts if t))
    return len([w for w in words if w.lower() not in STOP and len(w) > 2])


def screen(*texts, photo=False):
    """"" when the texts may be used; otherwise the reason they are left out (adults only, consent, no violence, no
    animals; photo=True adds the photo rules: no youthful or doubtful wording)."""
    text = " ".join(clean(t) for t in texts if t)
    no_art_school = ENGLISH_KIND.sub(" ", ART_SCHOOL.sub(" ", text))
    for pattern, why in ((rs.CHILD, "mentions or suggests a child or young person"),
                         (MINOR, "mentions or suggests a child or young person")):
        m = pattern.search(no_art_school)
        if m:
            return f"{why} ('{m.group(0)}')"
    if any(a < 18 for a in rs.ages(text)):
        return "gives an age under 18"
    m = VIOLENCE.search(text)
    if m:
        return f"violence, no consent or a private picture ('{m.group(0)}')"
    m = MYTH.search(text)
    if m:
        return f"a story about rape, abduction or a minor, or a god's pursuit ('{m.group(0)}')"
    m = ANIMAL.search(text)
    if m:
        return f"an animal or creature ('{m.group(0)}')"
    if photo:
        m = PHOTO_DOUBT.search(text)
        if m:
            return f"a photograph with youthful or doubtful wording ('{m.group(0)}')"
    return ""


def first(value):
    """The first item of a list (or the value itself), as plain text."""
    if isinstance(value, list):
        value = value[0] if value else ""
    if isinstance(value, dict):
        value = value.get("en") or next(iter(value.values()), "")
        return first(value)
    return clean(value)


def sentence(text):
    """Text with a capital first letter and a full stop."""
    return rs.sentence(text)


def art_draft(kind, title, description="", tags=(), maker="", date="", place="", generic="", owner="museum"):
    """(draft description, needs a fuller one?) for an artwork: "A <kind> from <place>, <date>, by <maker>.", the
    title, the record's description (first sentences, in plain words) and its subject tags. When the record has
    fewer than 5 useful words, generic is used and the second value is True."""
    lead = kind
    if re.fullmatch(r"[A-Z][a-z]+(ese|an|ish|ic|i)", maker or "") and not place:
        place, maker = maker, ""                 # "Japanese" is where it is from, not who made it
    if place:
        lead += f" from {place}"
    if date:
        lead += f", {date}"
    if maker and not re.match(r"^(unknown|anonymous|unidentified)", maker, re.I):
        lead += f", by {maker}"
    parts = [sentence(lead)]
    if description and not is_english(description):
        description = ""                         # not English: the caller keeps it in the notes for the reviewer
    if title:
        own = "" if is_english(title) else " (in the original language)"
        shown = plain(title).rstrip(".")
        parts.append(f'The {owner}\'s title{own} is "{shown[:1].upper() + shown[1:]}".')
        if own:
            title = ""
    if description:
        parts.append(sentence(rs.first_sentences(plain(description), 70, 3)))
    tags = [plain(t).lower() for t in tags if clean(t)]
    if tags:
        parts.append(sentence(f"The {owner}'s subject tags: " + ", ".join(dict.fromkeys(tags))))
    thin = useful_words(title, description, " ".join(tags)) < 5
    if thin and generic:
        parts.append(sentence(generic))
    return " ".join(p for p in parts if p), thin


THIN_NOTE = "needs a fuller description: the record says too little, so please write what the picture shows."


# ----------------------------------------------------------------- the review workspace

class AdultWorkspace(rs.ReviewWorkspace):
    """review_sources.ReviewWorkspace for adult sexual content: its own review instructions, content "sexual" with
    the extra flags, and CREDITS.txt with a details column (for vintage photographs: name, birth year, photo year).
    Pictures arrive with the status "needs another look", never "described" or "checked"."""

    def __init__(self, folder, source, say=None):
        """Open (or make) the workspace and write the adult review instructions."""
        super().__init__(folder, source, say)
        self.left_out = []                       # (title, reason) examples, for the summary
        self.workspace.data.update(content=CONTENT, needs_explicit_choice=True, never_for_picture_making=True,
                                   never_publish=True, review_only=True)
        self.workspace.save()
        with open(os.path.join(self.folder, REVIEW_FILE), "w", encoding="utf-8", newline="\r\n") as f:
            f.write(REVIEW_INSTRUCTIONS.format(name=source["name"], credit=source["credit"],
                                               licence=f"{source['licence']} ({source['terms_summary']})"))

    def leave_out(self, name, title, why):
        """Remember that a record was left out (by its id name, so it is not tried again) and why."""
        if name:
            self.mark_tried(name)
        if len(self.left_out) < LEFT_OUT_CAP:
            self.left_out.append((clean(title)[:100] or "(no title)", why))

    def flush(self):
        """Add the queued pictures, each with the status "needs another look", its credit, licence and source page in
        its notes and in CREDITS.txt (the last column holds details such as a named model's birth and photo year)."""
        if not self.waiting:
            self.save_tried()
            return
        files = [os.path.join(self.staging, n) for n, *_ in self.waiting]
        dp.add_pictures(self.workspace, files, person="")
        lines = []
        for item in self.waiting:
            # review_sources may add fields after these seven (it added "narration"); only these are used here.
            name, credit, licence, page, content, note, details = item[:7]
            if self.workspace.pictures.get(name) is None:
                continue                                  # the same picture was there already
            entry = self.workspace.entry(name)
            entry.update(status=dp.LOOK, described_by="", described_at="", checked_by="", checked_at="",
                         changed_at=dp.now(), content=content, review="review-only",
                         notes=clean(f"REVIEW ONLY (adult sexual content). Draft description from the source's own "
                                     f"record; a sighted, trusted adult must check it (see {REVIEW_FILE}). {note} "
                                     f"{details if details != rs.GROUPS[3] else ''} Credit: {credit}. "
                                     f"Licence: {licence}. Source: {page}"))
            lines.append("\t".join([name, credit, licence, page, details if details != rs.GROUPS[3] else ""]))
            self.added += 1
        self.workspace.save()
        with open(os.path.join(self.folder, CREDITS_FILE), "a", encoding="utf-8", newline="\r\n") as f:
            if f.tell() == 0:
                f.write(f"Credits for {self.source['name']}\nfile\tcredit\tlicence\tsource page\tdetails\n")
            f.write("\n".join(lines) + ("\n" if lines else ""))
        shutil.rmtree(self.staging, ignore_errors=True)
        self.waiting = []
        self.save_tried()
        self.say(f"{self.source['name']}: {len(self.workspace.pictures)} pictures in the review workspace.")

    def finish(self, found, left):
        """Add what is queued; say up to SHOW_LEFT_OUT left-out titles with the reason; give back a plain summary."""
        self.flush()
        if self.left_out:
            self.say("Left out, for example: " + "; ".join(f'"{t}" ({w})' for t, w in self.left_out[:SHOW_LEFT_OUT]))
        summary = (f"{self.source['name']}: {self.added} new pictures added for review "
                   f"({len(self.workspace.pictures)} in the workspace); {found} records looked at, {left} left out by "
                   f"the adults-only, consent, no-violence and licence rules or because the picture could not be "
                   f"downloaded. Every picture needs a check by a sighted, trusted adult before it can be used "
                   f"(see {REVIEW_FILE}).")
        self.say(summary)
        return summary


def take_turns(lists):
    """The items of several lists, taking one from each in turn (so every search or category has its share);
    items whose first value (the id name) was seen already are dropped."""
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


def art_check(ws, name, title, texts, kind_texts, need_topic=True):
    """True when an artwork record may be used: it passes screen(), its kind is an artwork and not a photograph,
    and (need_topic) it is about nudity, intimacy or sex. Otherwise it is recorded as left out and False."""
    why = screen(*texts)
    kind = " ".join(clean(t) for t in kind_texts if t)
    if not why and PHOTO_WORDS.search(kind + " " + clean(title)):
        why = "an old photograph (anonymous: age and consent cannot be checked)"
    if not why and not ART_KIND.search(kind):
        why = "the record does not show an artwork (print, painting, drawing, sculpture ...)"
    about = clean(texts[0]) + " " + " ".join(rs.first_sentences(clean(t), 60, 2) for t in texts[1:] if t)
    if not why and need_topic and not TOPIC.search(NOT_TOPIC.sub(" ", about)):
        why = "not about nudity, intimacy or sex"
    if why:
        ws.leave_out(name, title, why)
        return False
    return True


# ----------------------------------------------------------------- The Metropolitan Museum of Art (CC0)

MET = "https://collectionapi.metmuseum.org/public/collection/"
MET_QUERIES = ("shunga", "Spring pictures", "erotic", "erotica", "lovers", "couple embracing", "nude couple",
               "mithuna", "Kama Sutra", "nude")


def met_ids(s, query, most):
    """Object ids of a v1.1 search (with images), up to most."""
    ids, offset = [], 0
    while len(ids) < most:
        data = rs.get_json(s, MET + "v1.1/search", params={"q": query, "hasImages": "true", "limit": 100,
                                                           "offset": offset})
        found = (data or {}).get("objectIDs") or []
        ids += found
        if len(found) < 100:
            break
        offset += 100
    return ids[:most]


def fetch_met_erotic(folder, cap, say=print):
    """The Met: public-domain (CC0) erotic and nude artworks (shunga, "Spring pictures", Indian mithuna couples,
    Greek and Roman vases, European prints and drawings), from v1.1 searches, only isPublicDomain records. The
    records have titles and subject tags but no description, so many drafts need a fuller description."""
    source = source_by_key("met_erotic")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    lists = [[(f"met-{i}.jpg", i) for i in met_ids(s, q, max(60, cap * 3))] for q in MET_QUERIES]
    ids = take_turns(lists)
    say(f"The Met: {len(ids)} objects found by the searches")
    looked = left = 0
    for name, oid in ids:
        if ws.full(cap) and (len(ws.left_out) >= SHOW_LEFT_OUT or looked > cap + 150):
            break                                 # full, and enough left-out examples to show the filters
        if ws.done(name):
            continue
        looked += 1
        o = rs.get_json(s, f"{MET}v1/objects/{oid}") or {}
        tags = [t.get("term", "") for t in (o.get("tags") or [])]
        title = clean(o.get("title"))
        if not o.get("isPublicDomain") or not o.get("primaryImageSmall"):
            ws.leave_out(name, title, "not public domain or no picture")
            left += 1
            continue
        kind = [o.get("objectName"), o.get("classification"), o.get("medium"), o.get("department")]
        if not art_check(ws, name, title, [title, " ".join(tags), o.get("objectName"), o.get("medium")], kind):
            left += 1
            continue
        text, thin = art_draft(a_an(f"{clean(o.get('objectName') or 'work of art').lower()} "
                               f"({clean(o.get('medium')).lower() or 'medium not stated'})"),
                               title, "", tags, clean(o.get("artistDisplayName")), clean(o.get("objectDate")),
                               clean(o.get("culture") or o.get("country")),
                               generic="The record says little more; the museum lists it among erotic or nude art")
        if ws.full(cap):
            continue                              # full: only screened, to show what the filters leave out
        data = rs.download_picture(s, o["primaryImageSmall"])
        if data is None:
            ws.leave_out(name, title, "the picture could not be downloaded")
            left += 1
            continue
        ws.add(name, data, text, f"{title}, {clean(o.get('artistDisplayName')) or 'unknown artist'}, "
                                 f"The Metropolitan Museum of Art, {clean(o.get('creditLine'))}",
               "CC0 (Open Access, public domain)", clean(o.get("objectURL")), CONTENT, THIN_NOTE if thin else "")
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Art Institute of Chicago (CC0 for PD works)

AIC = "https://api.artic.edu/api/v1/artworks/search"
AIC_IIIF = "https://www.artic.edu/iiif/2"
AIC_TITLE = ("shunga", "erotic", "lovers", "spring picture", "love-making", "lovemaking", "embrace", "nude couple",
             "mithuna", "courtesan")
AIC_SUBJECT = ("erotica", "sexuality", "lovers", "nudes")


def fetch_aic_erotic(folder, cap, say=print):
    """Art Institute of Chicago: public-domain erotic and nude artworks (title or subject search; is_public_domain
    only; the museum releases pictures of public-domain works under CC0)."""
    source = source_by_key("aic_erotic")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    should = [{"match_phrase": {"title": w}} for w in AIC_TITLE] + \
             [{"match": {"subject_titles": w}} for w in AIC_SUBJECT]
    fields = ["id", "title", "subject_titles", "term_titles", "classification_titles", "description",
              "short_description", "image_id", "artist_display", "date_display", "medium_display", "place_of_origin",
              "is_public_domain"]
    items, looked, left, page = [], 0, 0, 1
    while len(items) < cap * 2 + 20 and page <= 40:
        body = {"query": {"bool": {"should": should, "minimum_should_match": 1,
                                   "filter": [{"term": {"is_public_domain": True}}]}},
                "fields": fields, "limit": 100, "page": page}
        data = None
        for attempt in range(4):                  # tried again on a passing error
            try:
                data = s.post(AIC, json=body, timeout=90).json()
                break
            except Exception:  # noqa: BLE001 - tried again
                time.sleep(5 * (attempt + 1))
        if data is None:
            break
        rows = data.get("data") or []
        for x in rows:
            looked += 1
            name, title = f"aic-{x['id']}.jpg", clean(x.get("title"))
            if ws.done(name):
                continue
            if not x.get("image_id"):
                ws.leave_out(name, title, "no picture")
                left += 1
                continue
            desc = clean(x.get("description") or x.get("short_description"))
            texts = [title, desc, " ".join(x.get("subject_titles") or [])]
            kind = [x.get("medium_display"), " ".join(x.get("classification_titles") or []),
                    " ".join(x.get("term_titles") or [])]
            if not art_check(ws, name, title, texts, kind):
                left += 1
                continue
            text, thin = art_draft(f"A work of art ({clean(x.get('medium_display')).lower() or 'medium not stated'})",
                                   title, desc, x.get("subject_titles") or [], clean(x.get("artist_display")),
                                   clean(x.get("date_display")).rstrip("."), clean(x.get("place_of_origin")),
                                   generic="The record says little more; the museum lists it among erotic or nude art")
            items.append((name, f"{AIC_IIIF}/{x['image_id']}/full/843,/0/default.jpg", text,
                          f"{title}, {clean(x.get('artist_display'))}, Art Institute of Chicago", "CC0 (public domain)",
                          f"https://www.artic.edu/artworks/{x['id']}", CONTENT, THIN_NOTE if thin else "",
                          rs.GROUPS[3]))
        if len(rows) < 100:
            break
        page += 1
    say(f"Art Institute of Chicago: {len(items)} usable records")
    s.headers["AIC-User-Agent"] = rs.USER_AGENT           # the museum's picture server asks for this header
    left += rs.fill(ws, items, cap, s)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Cleveland Museum of Art (CC0)

CMA = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_QUERIES = ("erotic", "shunga", "lovers", "mithuna", "embrace", "nude", "couple")


def fetch_cleveland_erotic(folder, cap, say=print):
    """Cleveland Museum of Art: CC0 erotic and nude artworks (Indian erotic paintings and temple couples, Japanese
    prints, European nudes). Its records have good descriptions written by curators."""
    source = source_by_key("cleveland_erotic")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    lists, looked, left = [], 0, 0
    for q in CMA_QUERIES:
        found, skip = [], 0
        while len(found) < cap * 2 + 10:
            data = rs.get_json(s, CMA, params={"q": q, "has_image": 1, "cc0": 1, "limit": 100, "skip": skip})
            rows = (data or {}).get("data") or []
            for x in rows:
                looked += 1
                name, title = f"cma-{x['id']}.jpg", clean(x.get("title"))
                web = ((x.get("images") or {}).get("web") or {}).get("url")
                if ws.done(name) or x.get("share_license_status") != "CC0" or not web:
                    continue
                desc = clean(x.get("digital_description") or x.get("wall_description") or x.get("description"))
                maker = "; ".join(clean(c.get("description")) for c in (x.get("creators") or [])[:2])
                kind = [x.get("type"), x.get("technique"), x.get("department")]
                if not art_check(ws, name, title, [title, desc], kind):
                    left += 1
                    continue
                text, thin = art_draft(a_an(f"{clean(x.get('type')).lower() or 'work of art'}"
                                            + (f" ({clean(x.get('technique')).lower()})" if x.get("technique")
                                               else "")),
                                       title, desc, [], maker, clean(x.get("creation_date")), clean(x.get("culture")
                                                                                                    and x["culture"][0]),
                                       generic="The record says little more; the museum lists it among erotic or nude art")
                found.append((name, web, text, f"{title}, {maker or 'unknown artist'}, Cleveland Museum of Art",
                              "CC0", clean(x.get("url")), CONTENT, THIN_NOTE if thin else "", rs.GROUPS[3]))
            if len(rows) < 100:
                break
            skip += 100
        lists.append(found)
    items = take_turns(lists)
    say(f"Cleveland Museum of Art: {len(items)} usable records")
    left += rs.fill(ws, items, cap, s)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Rijksmuseum (public domain)

RIJKS = "https://data.rijksmuseum.nl/search/collection"
RIJKS_SEARCHES = ({"title": "shunga"}, {"description": "shunga"}, {"description": "erotisch"},
                  {"description": "erotische"}, {"description": "erotic"}, {"title": "minnaars"})
RIJKS_OPEN = ("publicdomain/mark", "publicdomain/zero")
DUTCH = [(re.compile(p, re.I), w) for p, w in [
    (r"\berotische?\b", "erotic"), (r"\bboek(je)?\b", "book"), (r"\bprent\b", "print"), (r"\bdeel (\d+) van (\d+)\b",
                                                                                          r"part \1 of \2"),
    (r"\bminnaars\b", "lovers"), (r"\bliefdespaar\b", "loving couple"), (r"\bpaar\b", "couple"),
    (r"\bnaakte?\b", "nude"), (r"\bman en vrouw\b", "a man and a woman"), (r"\bvrijend\w*\b", "making love"),
    (r"\bvrouw(en)?\b", "woman"), (r"\bman(nen)?\b", "man"), (r"\bmet\b", "with"), (r"\ben\b", "and"),
    (r"\bin bed\b", "in bed"), (r"\bkamer\b", "room"), (r"\bbad\b", "bath"), (r"\btwee\b", "two"),
    (r"\been\b", "a"), (r"\bkoppelaarster\b", "procuress"), (r"\bklein\b", "small"),
    (r"\bprentenboek\b", "picture book"), (r"\bover\b", "about"), (r"\bgewillige\b", "willing"),
    (r"\bvrijpartij\b", "love-making"), (r"\bkussend\w*\b", "kissing"), (r"\bomhelzend\w*\b", "embracing")]]


def dutch_to_english(text):
    """A short Dutch catalogue phrase in English where its words are known; None when Dutch words are left."""
    out = clean(text)
    for pattern, words in DUTCH:
        out = pattern.sub(words, out)
    left = [w for w in re.findall(r"[A-Za-z]+", out) if w.lower() not in
            set("erotic book print part of lovers loving couple nude a man and woman making love with in bed room "
                "bath shunga two procuress small picture about willing album love-making kissing embracing "
                "women".split()) and not w.isdigit()]
    return out if not left else None


def rijks_record(s, uri):
    """(title, Dutch title, description, maker, date, kind, rights, picture address, page) of a Rijksmuseum object,
    or None."""
    data = rs.get_json(s, uri, params={"_profile": "edm-framed", "_mediatype": "application/ld+json"})
    if not data or "aggregatedCHO" not in data:
        return None
    c = data["aggregatedCHO"]
    title = c.get("title") or {}
    desc = c.get("description") or {}
    maker = ""
    for who in c.get("creator") if isinstance(c.get("creator"), list) else [c.get("creator") or {}]:
        labels = who.get("http://www.w3.org/2004/02/skos/core#prefLabel") or []
        labels = labels if isinstance(labels, list) else [labels]
        maker = next((clean(x.get("@value")) for x in labels if x.get("@language") == "en"), maker)
    kinds = []
    def as_list(value):
        """A value as a list (linked data gives one item or a list)."""
        return value if isinstance(value, list) else [value] if value else []
    for t in as_list(c.get("dcType")) + as_list(c.get("http://www.europeanafashion.eu/edmfp/technique")):
        for x in as_list(t.get("http://www.w3.org/2004/02/skos/core#prefLabel") if isinstance(t, dict) else None):
            if isinstance(x, dict) and x.get("@language") == "en":
                kinds.append(clean(x.get("@value")))
    created = c.get("created") if isinstance(c.get("created"), list) else [c.get("created") or {}]
    date = next((clean(x.get("@value")) for x in created if isinstance(x, dict) and x.get("@language") == "en"), "")
    shown = (data.get("isShownBy") or {}).get("id", "")
    return {"title": first(title.get("en")), "title_nl": first(title.get("nl")), "desc_en": first(desc.get("en")),
            "desc_nl": first(desc.get("nl")), "maker": maker, "date": date, "kind": "; ".join(kinds),
            "rights": clean(data.get("edmRights")), "picture": shown.replace("/full/max/", "/full/1600,/"),
            "page": clean((data.get("isShownAt") or {}).get("id"))}


def fetch_rijks_erotic(folder, cap, say=print):
    """Rijksmuseum: public-domain erotic prints and books (mostly Japanese shunga, and European erotic prints),
    from the linked-data search; only public-domain-mark or CC0 records. The descriptions are often in Dutch: a
    short phrase is put in English where its words are known, otherwise the Dutch is kept in the notes only."""
    source = source_by_key("rijks_erotic")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    lists = []
    for search in RIJKS_SEARCHES:
        found, url, params = [], RIJKS, dict(search, imageAvailable="true")
        while url and len(found) < max(60, cap * 3):
            data = rs.get_json(s, url, params=params)
            if not data:
                break
            found += [(f"rijks-{x['id'].rsplit('/', 1)[-1]}.jpg", x["id"]) for x in data.get("orderedItems") or []]
            url, params = (data.get("next") or {}).get("id"), None
        lists.append(found)
    ids = take_turns(lists)
    say(f"Rijksmuseum: {len(ids)} objects found by the searches")
    looked = left = 0
    for name, uri in ids:
        if ws.full(cap) and (len(ws.left_out) >= SHOW_LEFT_OUT or looked > cap + 150):
            break                                 # full, and enough left-out examples to show the filters
        if ws.done(name):
            continue
        looked += 1
        r = rijks_record(s, uri)
        if not r or not any(k in r["rights"] for k in RIJKS_OPEN) or not r["picture"]:
            ws.leave_out(name, r["title"] if r else uri, "not public domain or no picture")
            left += 1
            continue
        english = r["desc_en"] or dutch_to_english(r["desc_nl"]) or ""
        texts = [r["title"], r["title_nl"], r["desc_en"], r["desc_nl"]]
        if not art_check(ws, name, r["title"] or r["title_nl"], texts,
                         [r["kind"], r["title"], r["desc_nl"], r["desc_en"]]):
            left += 1
            continue
        title_en = r["title"] or dutch_to_english(r["title_nl"]) or f"{r['title_nl']} (Dutch title)"
        text, thin = art_draft(a_an(r['kind'].split(';')[0].lower() or 'work of art'), title_en,
                               english, [], r["maker"], r["date"], "",
                               generic="The record says little more; it is listed as erotic art")
        if ws.full(cap):
            continue                              # full: only screened, to show what the filters leave out
        data = rs.download_picture(s, r["picture"])
        if data is None:
            ws.leave_out(name, r["title"], "the picture could not be downloaded")
            left += 1
            continue
        note = (THIN_NOTE + " " if thin else "") + (f"Dutch description: {r['desc_nl']}." if r["desc_nl"] else "")
        ws.add(name, data, text, f"{r['title'] or r['title_nl']}, {r['maker'] or 'unknown artist'}, Rijksmuseum "
                                 f"Amsterdam", "public domain (Public Domain Mark) or CC0", r["page"], CONTENT, note)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Smithsonian National Museum of Asian Art (CC0)

SI = "https://api.si.edu/openaccess/api/v1.0/search"
SI_QUERIES = ("shunga", "erotic", "lovers", '"spring pictures"', "mithuna", "embrace")


def si_text(content, field):
    """The texts of one freetext field of a Smithsonian record."""
    return [clean(x.get("content")) for x in ((content.get("freetext") or {}).get(field) or [])]


def fetch_smithsonian_shunga(folder, cap, say=print):
    """Smithsonian National Museum of Asian Art (the Freer and Sackler galleries, unit NMAA): CC0 Japanese shunga
    and Indian and Persian erotic paintings. Needs a free api.data.gov key in the SI_API_KEY environment variable
    (the shared DEMO_KEY allows only a few searches an hour). Only media marked CC0."""
    source = source_by_key("smithsonian_shunga")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    key = os.environ.get("SI_API_KEY") or "DEMO_KEY"
    lists, looked, left = [], 0, 0
    for q in SI_QUERIES:
        found, start = [], 0
        while len(found) < cap * 2 + 10:
            try:
                answer = s.get(SI, params={"q": f"{q} AND unit_code:NMAA", "api_key": key, "rows": 100,
                                           "start": start}, timeout=90)
                data = answer.json() if answer.status_code == 200 else None
            except Exception:  # noqa: BLE001 - nothing found for this search
                answer, data = None, None
            if answer is not None and answer.status_code == 429 or (data and "response" not in data):
                say("Smithsonian: the API key's hourly limit is used up (the shared DEMO_KEY allows very few "
                    "searches). Get a free key at api.data.gov, put it in SI_API_KEY and run this again; it carries "
                    "on where it stopped.")
                lists.append(found)
                return finish_si(ws, lists, cap, s, looked, left, say, key)
            rows = ((data or {}).get("response") or {}).get("rows") or []
            for x in rows:
                looked += 1
                c = x.get("content") or {}
                dnr = c.get("descriptiveNonRepeating") or {}
                media = [m for m in ((dnr.get("online_media") or {}).get("media") or [])
                         if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"]
                record_id = re.sub(r"[^\w.-]", "_", x.get("url") or x.get("id") or "")
                name, title = f"si-{record_id}.jpg", clean(x.get("title"))
                if ws.done(name):
                    continue
                if not media:
                    ws.leave_out(name, title, "no CC0 picture")
                    left += 1
                    continue
                notes = " ".join(si_text(c, "notes"))
                kind = si_text(c, "physicalDescription") + si_text(c, "objectType")
                topics = [clean(t) for t in ((c.get("indexedStructured") or {}).get("topic") or [])]
                if not art_check(ws, name, title, [title, notes, " ".join(topics)], kind):
                    left += 1
                    continue
                text, thin = art_draft(a_an((kind[0] if kind else 'work of art').lower()), title, notes, topics,
                                       "; ".join(si_text(c, "name")[:1]), "; ".join(si_text(c, "date")[:1]),
                                       "; ".join(si_text(c, "place")[:1]),
                                       generic="The record says little more; it is listed as erotic art")
                found.append((name, media[0]["content"] + "&max=1600", text,
                              f"{title}, Smithsonian National Museum of Asian Art", "CC0",
                              clean((dnr.get("record_link") or "")), CONTENT, THIN_NOTE if thin else "",
                              rs.GROUPS[3]))
            if len(rows) < 100:
                break
            start += 100
        lists.append(found)
        time.sleep(1)
    return finish_si(ws, lists, cap, s, looked, left, say, key)


def finish_si(ws, lists, cap, s, looked, left, say, key):
    """Download the usable Smithsonian records found so far and give back the summary."""
    items = take_turns(lists)
    say(f"Smithsonian: {len(items)} usable records" + ("" if key != "DEMO_KEY" else
                                                         " (with the shared DEMO_KEY; set SI_API_KEY for more)"))
    left += rs.fill(ws, items, cap, s)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Wellcome Collection (CC BY, public domain)

WELLCOME = "https://api.wellcomecollection.org/catalogue/v2/"
WELLCOME_QUERIES = ("sexual intercourse", "erotica", "love making", "kama sutra", "coitus", "sex positions",
                    "sexology", "contraception", "condom", "nude couple")
WELLCOME_LICENCES = {"cc-by": "CC BY 4.0", "pdm": "public domain (Public Domain Mark)", "cc-0": "CC0"}


def fetch_wellcome_erotica(folder, cap, say=print):
    """Wellcome Collection: historical erotica, sexology and contraception pictures (Indian, Persian, Nepalese and
    Japanese erotic paintings, European erotic etchings, sexual-health prints), CC BY, CC0 or public domain only.
    Its titles are already plain descriptions ("A couple engaged in sexual intercourse. Gouache painting ...").
    Photographs are left out (anonymous)."""
    source = source_by_key("wellcome_erotica")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    lists, looked, left = [], 0, 0
    for q in WELLCOME_QUERIES:
        found, page = [], 1
        while len(found) < cap * 2 + 10:
            data = rs.get_json(s, WELLCOME + "images", params={"query": q, "pageSize": 100, "page": page,
                                                               "locations.license": "cc-by,pdm,cc-0",
                                                               "include": "source.subjects,source.genres"})
            rows = (data or {}).get("results") or []
            for x in rows:
                looked += 1
                name = f"wellcome-{x['id']}.jpg"
                src = x.get("source") or {}
                title = clean(src.get("title"))
                loc = (x.get("locations") or [{}])[0]
                lic = (loc.get("license") or {}).get("id", "")
                if ws.done(name):
                    continue
                if lic not in WELLCOME_LICENCES or not loc.get("url", "").endswith("info.json"):
                    ws.leave_out(name, title, f"licence not open ({lic or 'none'})")
                    left += 1
                    continue
                subjects = [clean(t.get("label")) for t in src.get("subjects") or []]
                genres = [clean(t.get("label")) for t in src.get("genres") or []]
                texts = [title, " ".join(subjects), " ".join(genres)]
                if not art_check(ws, name, title, texts, [title, " ".join(genres)]):
                    left += 1
                    continue
                text, thin = art_draft("A historical picture from the Wellcome Collection", title, "",
                                       [t for t in subjects if not t.isupper()], "", "", "",
                                       generic="The record says little more; it is listed among erotica or sexual-health pictures",
                                       owner="library")
                found.append((name, loc["url"].replace("info.json", "full/!1600,1600/0/default.jpg"), text,
                              f"{title}, Wellcome Collection", WELLCOME_LICENCES[lic],
                              f"https://wellcomecollection.org/works/{src.get('id', '')}", CONTENT,
                              THIN_NOTE if thin else "", rs.GROUPS[3]))
            if (data or {}).get("totalPages", 1) <= page:
                break
            page += 1
        lists.append(found)
    items = take_turns(lists)
    say(f"Wellcome Collection: {len(items)} usable records")
    left += rs.fill(ws, items, cap, s)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Europeana (open re-use rights only)

EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EUROPEANA_QUERIES = ("erotic print", "erotic drawing", "erotic painting", "erotica", "shunga", "kama sutra",
                     "erotic engraving", "erotic sculpture", "lovers embrace")


def rights_kind(url):
    """("open" or "share-alike", plain licence) for a rights address; ("", "") for anything else (NC, ND, in
    copyright, unknown)."""
    url = clean(url).lower()
    if re.search(r"-nc|-nd|/nc|/nd|rightsstatements", url):
        return "", ""
    if "publicdomain/mark" in url:
        return "open", "public domain (Public Domain Mark)"
    if "publicdomain/zero" in url:
        return "open", "CC0"
    m = re.search(r"licenses/(by(?:-sa)?)/(\d\.\d)", url)
    if m:
        return ("share-alike" if "sa" in m.group(1) else "open"), f"CC {m.group(1).upper()} {m.group(2)}"
    return "", ""


def fetch_europeana_erotic(folder, cap, say=print):
    """Europeana: erotic prints, drawings, paintings and sculpture from European museums and libraries with open
    re-use rights (public domain, CC0, CC BY or CC BY-SA, checked per record; never NC, ND or "in copyright").
    Photographs are left out (anonymous), and abstract works are left out (they teach nothing about what is shown).
    Uses the public demonstration key; a free key can be set in EUROPEANA_KEY."""
    source = source_by_key("europeana_erotic")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    key = os.environ.get("EUROPEANA_KEY") or "api2demo"
    lists, looked, left = [], 0, 0
    for q in EUROPEANA_QUERIES:
        found, cursor = [], "*"
        while cursor and len(found) < cap * 2 + 10:
            data = rs.get_json(s, EUROPEANA, params={"wskey": key, "query": q, "reusability": "open", "media": "true",
                                                     "qf": "TYPE:IMAGE", "rows": 100, "profile": "rich",
                                                     "cursor": cursor})
            if not data:
                break
            for x in data.get("items") or []:
                looked += 1
                name = "europeana-" + re.sub(r"[^\w-]+", "_", x.get("id", ""))[-80:] + ".jpg"
                title = first(x.get("title"))
                kind, lic = rights_kind(first(x.get("rights")))
                picture = first(x.get("edmIsShownBy")) or first(x.get("edmPreview"))
                if ws.done(name):
                    continue
                if not kind or not picture:
                    ws.leave_out(name, title, "licence not open, or no picture")
                    left += 1
                    continue
                desc = first(x.get("dcDescription"))
                types = " ".join(clean(t) for t in (x.get("dcTypeLangAware") or {}).get("en", []) +
                                 (x.get("dcType") or []))
                if re.search(r"\babstract\b", f"{title} {desc}", re.I):
                    ws.leave_out(name, title, "an abstract work")
                    left += 1
                    continue
                if not art_check(ws, name, title, [title, desc, types], [types, title, desc]):
                    left += 1
                    continue
                maker = first(x.get("dcCreator"))
                text, thin = art_draft(f"A work of art ({types.lower()[:60] or 'kind not stated'})", title, desc, [],
                                       maker, first(x.get("year")), "",
                                       generic="The record says little more; it is listed as erotic art")
                if not is_english(desc) or not is_english(title):
                    thin = True
                note = (THIN_NOTE + " " if thin else "") + (
                    f"Original-language record: {title}. {rs.first_sentences(desc, 80, 3)}"
                    if not (is_english(desc) and is_english(title)) else "")
                found.append((name, picture, text, f"{title}, {maker or 'unknown artist'}, "
                              f"{first(x.get('dataProvider'))}, via Europeana", lic, first(x.get("guid")), CONTENT,
                              note, rs.GROUPS[3]))
            cursor = data.get("nextCursor")
        lists.append(found)
    items = take_turns(lists)
    say(f"Europeana: {len(items)} usable records")
    left += rs.fill(ws, items, cap, s)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Wikimedia Commons (licence per file)

COMMONS = rs.COMMONS_API

# Each Commons group: the categories read (with how deep into sub-categories), what kind of picture it is, and its
# own rules. Sub-categories are read only when their own names pass screen().
COMMONS_GROUPS = {
    "erotic_sculpture": dict(
        categories=[("Erotic sculptures of Konark Sun Temple", 0), ("Erotic sculptures in India", 2),
                    ("Erotic sculptures in Nepal", 1), ("Mithuna", 1), ("Erotic reliefs", 1),
                    ("Sexuality in ancient Roman sculptures", 1), ("Lupanar (Pompeii)", 1), ("Erotic pottery", 2),
                    ("Fellatio in sculptures", 1), ("Erotic sculptures", 1)],
        lead="A photograph of an erotic artwork (sculpture, fresco or pottery)", people_photo=False,
        generic="The record says little more; it is filed on Commons among erotic sculpture, frescoes or pottery"),
    "sex_drawings": dict(
        categories=[("Sex positions", 2), ("Human sexual activity diagrams", 1), ("Sex education", 1),
                    ("Kama Sutra", 1), ("I modi - nine fragments - Agostino Veneziano", 0),
                    ("Erotic prints in the Metropolitan Museum of Art", 1), ("Erotic engravings", 1),
                    ("Erotic illustrations", 1), ("Erotic drawings", 1), ("People having sex in art", 1),
                    ("Erotic paintings", 1)],
        lead="A drawing, print or painting", people_photo=False, drawings_only=True,
        generic="The record says little more; it is filed on Commons among drawings of sex, sex positions or erotic art"),
    "sex_photos": dict(
        categories=[("Human sexual activity", 2), ("Nude couples", 1)],
        lead="A photograph", people_photo=True, photos_only=True, own_work=True,
        generic="The record says little more; it is filed on Commons under human sexual activity"),
    "inclusive": dict(
        categories=[("LGBT sex", 2), ("Gay sex", 1), ("Lesbian sex", 1), ("Transgender sexuality", 1),
                    ("Interracial sex", 1), ("Sexual activity during pregnancy", 0), ("Gay erotic art", 1),
                    ("Lesbian erotic art", 1), ("Bisexual erotic art", 1), ("Safer sex", 1),
                    ("Disability and sexuality", 1)],
        lead="A picture", people_photo=True, own_work=True,
        generic="The record says little more; it is filed on Commons under LGBTQ+, inclusive or safer sex"),
    "sex_toys": dict(
        categories=[("Sex toys", 1), ("Dildos", 1), ("Vibrators", 1), ("Butt plugs", 1), ("Anal beads", 1),
                    ("Cock rings", 1), ("Sex dolls", 0), ("Personal lubricants", 1)],
        lead="A product photograph of a sex toy", people_photo=True,
        generic="The record says little more; it is filed on Commons among sex toys"),
    "contraception": dict(
        categories=[("Condoms", 1), ("Female condoms", 1), ("Male condoms", 1), ("Contraceptive pills", 1),
                    ("Contraceptive devices", 1), ("Intrauterine devices", 1), ("Contraceptive implants", 1),
                    ("Contraceptive injections", 0), ("Dental dams", 1), ("Latex dental dams", 0),
                    ("Emergency contraception", 1), ("Vaginal rings", 0), ("Spermicides", 1), ("Safer sex", 0)],
        lead="A photograph of a sexual-health item", people_photo=True,
        generic="The record says little more; it is filed on Commons among condoms, contraceptives or sexual-health items"),
}

DRAWN = re.compile(r"\b(drawings?|drawn|illustrations?|illustrated|diagrams?|vector|svg|sketch\w*|cartoons?|"
                   r"engravings?|etchings?|lithographs?|woodcuts?|prints?|watercolou?rs?|paintings?|clip ?art|"
                   r"schematic|line art|icons?)\b", re.I)
PERSON = re.compile(r"\b(man|men|woman|women|person|people|couple|nude|naked|model|wearing|using|holding|"
                    r"hand|hands|body|penis|vulva|vagina|anus|breasts?|self|selfie)\b", re.I)


def commons_query(s, params):
    """One Commons API answer (JSON), waiting politely; None on failure."""
    params = dict(params, format="json", maxlag=5)
    time.sleep(1)
    return rs.get_json(s, COMMONS, params=params)


def commons_subcats(s, category, depth, ws):
    """category and its sub-categories down to depth, leaving out those whose names fail screen() or are about
    something else (art of minors, violence, animals ...)."""
    found, todo = [category], [(category, depth)]
    while todo:
        cat, d = todo.pop(0)
        if d <= 0:
            continue
        data = commons_query(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{cat}",
                                 "cmtype": "subcat", "cmlimit": 200}) or {}
        for x in (data.get("query") or {}).get("categorymembers", []):
            sub = x["title"][9:]
            why = screen(sub, photo=True) or (PROBLEM_CATEGORY.search(sub) and "a problem category")
            if why:
                ws.leave_out("", f"Category:{sub}", why)
                continue
            if sub not in found:
                found.append(sub)
                todo.append((sub, d - 1))
    return found


def commons_files(s, category):
    """[(pageid, title, imageinfo)] for the files of one Commons category (no sub-categories)."""
    params = {"action": "query", "generator": "categorymembers", "gcmtitle": f"Category:{category}",
              "gcmtype": "file", "gcmlimit": 50, "prop": "imageinfo", "iiprop": "url|extmetadata|mime",
              "iiurlwidth": 1600,
              "iiextmetadatafilter": "LicenseShortName|ImageDescription|Artist|Categories|ObjectName|Credit|"
                                     "DateTimeOriginal|UsageTerms"}
    out = []
    while True:
        data = commons_query(s, params)
        if not data:
            break
        for p in (data.get("query") or {}).get("pages", {}).values():
            out.append((p["pageid"], p.get("title", "")[5:], (p.get("imageinfo") or [{}])[0]))
        if "continue" not in data or len(out) > 3000:
            break
        params.update(data["continue"])
    return out


def meta_value(info, key):
    """One extmetadata field of a Commons file as plain text."""
    return rs.no_tags(((info.get("extmetadata") or {}).get(key) or {}).get("value"))


# Commons boilerplate that says nothing about what a picture shows.
BOILERPLATE = re.compile(r"This is a photo of (an? )?(ASI )?monument[^.]*\.?|This is an image of[^.]*monument[^.]*\.?|"
                         r"Photo(graph)? taken by [^.]*\.?|Taken (by|with) [^.]*\.?|\bOwn work\b\.?|"
                         r"Camera location[^.]*\.?|View all coordinates[^.]*\.?", re.I)


def english_description(description):
    """The English part of a Commons description (Commons often gives several languages)."""
    m = re.search(r"(?:^|\s)(?:English|en)[:\s]+(.+?)(?=\s(?:Deutsch|Français|Español|Italiano|Nederlands|Polski|"
                  r"Português|Русский|日本語|中文|de|fr|es|it|nl|pl|pt|ru|ja|zh)[:\s]|$)", description)
    return clean(m.group(1)) if m else clean(description)


def commons_check(ws, group, pageid, title, info):
    """(draft, credit, licence, page, note) for a usable Commons file of a group, or None (recorded as left out)."""
    name = f"commons-{pageid}.jpg"
    description = clean(BOILERPLATE.sub(" ", english_description(meta_value(info, "ImageDescription"))))
    categories = meta_value(info, "Categories")
    credit_src, licence = meta_value(info, "Credit"), meta_value(info, "LicenseShortName")
    mime = info.get("mime", "")
    stem = os.path.splitext(title)[0].replace("_", " ")
    text = f"{stem} {meta_value(info, 'ObjectName')} {description}"
    drawn = mime == "image/svg+xml" or bool(DRAWN.search(f"{text} {categories}"))
    # A photograph of people (any photo in the sexual-activity groups; in the product groups, one whose text names
    # a person or body) must be the uploader's own work, so that consent rests with the person who uploaded it.
    has_person = bool(PERSON.search(text)) or group not in ("sex_toys", "contraception")
    why = ""
    if not mime.startswith("image/") or "gif" in mime or not info.get("thumburl"):
        why = "not a still picture"
    elif re.search(r"\b([Ll]ogos?|[Ii]cons?|[Ww]ordmarks?|[Pp]ictograms?|[Ee]mblems?|[Ff]lags?|[Mm]aps?|[Cc]harts?|"
                   r"[Gg]raphs?)\b", text):     # lower or title case only ("MAP" is a museum's initials)
        why = "a logo, icon, map or chart (teaches nothing about what a picture shows)"
    elif not rs.commons_licence_kind(licence):
        why = f"licence not open ({licence or 'none'})"
    elif PROBLEM_CATEGORY.search(categories):
        why = "in a deletion, copyright or identity-problem category"
    else:
        why = screen(text, categories, photo=not drawn)
    if not why and re.search(r"\b(linga\w*|lingam\w*|yoni|shivling\w*|shiva ?linga\w*)\b", f"{text} {categories}", re.I):
        why = "a religious symbol (linga or yoni), not a picture of adults"
    if not why and group == "sex_drawings" and not drawn:
        why = "not a drawing (this collection is for drawings and illustrations)"
    if not why and COMMONS_GROUPS[group].get("photos_only") and drawn:
        why = "a drawing (counted in the drawings collection)"
    if not why and not drawn and has_person and COMMONS_GROUPS[group]["people_photo"]:
        if not re.search(r"\bown work\b", credit_src, re.I):
            why = "a photograph of people that is not the uploader's own work (consent cannot be checked)"
        elif PHOTO_WORDS.search(f"{text} {categories}") and re.search(r"\b1[89]\d\d\b|vintage|antique", text, re.I):
            why = "an old photograph (anonymous: age and consent cannot be checked)"
    if not why and group == "erotic_sculpture" and PHOTO_WORDS.search(text) and re.search(
            r"\b1[89]\d\d\b|vintage", text) and not re.search(r"sculpt|temple|fresco|relief|pottery|vase", text, re.I):
        why = "an old photograph rather than a photo of an artwork"
    if why:
        ws.leave_out(name, stem, why)
        return None
    original = ""
    if description and not is_english(description):
        original, description = description, ""   # not English: kept in the notes for the reviewer
    if not description and not is_english(stem):
        original, stem = original or stem, ""
    caption = rs.first_sentences(plain(description) or plain(stem), 70, 3)
    thin = useful_words(description or stem) < 5
    g = COMMONS_GROUPS[group]
    if drawn and group != "sex_drawings":
        lead = "A drawing or illustration"
    elif not drawn and group in ("sex_toys", "contraception") and PERSON.search(text):
        lead = "A photograph of a person with a sex toy" if group == "sex_toys" else \
            "A photograph of a person with a sexual-health item"
    else:
        lead = g["lead"]
    lead += " from Wikimedia Commons."
    parts = [lead, f"Its description says: {sentence(caption)}" if caption else "",
             sentence(g["generic"]) if thin else ""]
    artist = meta_value(info, "Artist") or "unknown"
    page = "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_")
    note = (THIN_NOTE + " " if thin else "") + (f"Original-language description: {original[:300]}. " if original
                                                else "") + \
        (f"Source as stated on Commons: {credit_src[:120]}." if credit_src else "")
    return (" ".join(p for p in parts if p), f"{os.path.splitext(title)[0]} by {artist[:120]}, via Wikimedia Commons", licence, page, note)


def commons_group_fetch(key, group, kind, folder, cap, say):
    """Fill the review workspace of collection key with the files of one Commons group whose licence is of kind
    ("open" or "share-alike"), taking turns between the categories."""
    source = source_by_key(key)
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    lists, looked, left, seen = [], 0, 0, set()
    for category, depth in COMMONS_GROUPS[group]["categories"]:
        for cat in commons_subcats(s, category, depth, ws):
            if cat in seen:
                continue
            seen.add(cat)
            found = []
            for pageid, title, info in commons_files(s, cat):
                name = f"commons-{pageid}.jpg"
                if name in {i[0] for i in found} or ws.done(name):
                    continue
                if rs.commons_licence_kind(meta_value(info, "LicenseShortName")) not in ("", kind):
                    continue                              # counted in the other licence's collection
                looked += 1
                checked = commons_check(ws, group, pageid, title, info)
                if checked is None:
                    left += 1
                    continue
                text, credit, licence, page, note = checked
                found.append((name, info["thumburl"], text, credit, licence, page, CONTENT, note, rs.GROUPS[3]))
            if found:
                say(f"Commons '{cat}': {len(found)} usable files")
            lists.append(found)
            if sum(len(x) for x in lists) > cap * 2 + 10 or looked > cap * 30 + 300:
                break
        if sum(len(x) for x in lists) > cap * 2 + 10 or looked > cap * 30 + 300:
            break
    items = take_turns(lists)
    left += rs.fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


def fetch_commons_erotic_sculpture(folder, cap, say=print):
    """Commons photographs (CC0, public domain or CC BY) of erotic sculpture, frescoes and pottery: Khajuraho,
    Konark, Pompeii, ancient Greek and Moche pottery. The artworks are centuries old; the photos are the uploaders'."""
    return commons_group_fetch("commons_erotic_sculpture", "erotic_sculpture", "open", folder, cap, say)


def fetch_commons_erotic_sculpture_sa(folder, cap, say=print):
    """The same as fetch_commons_erotic_sculpture, for CC BY-SA photographs."""
    return commons_group_fetch("commons_erotic_sculpture_sa", "erotic_sculpture", "share-alike", folder, cap, say)


def fetch_commons_sex_drawings(folder, cap, say=print):
    """Commons drawings and illustrations (CC0, public domain or CC BY): sex positions, sex-education drawings,
    Kama Sutra illustrations and vintage erotic engravings and book illustrations (drawings only)."""
    return commons_group_fetch("commons_sex_drawings", "sex_drawings", "open", folder, cap, say)


def fetch_commons_sex_drawings_sa(folder, cap, say=print):
    """The same as fetch_commons_sex_drawings, for CC BY-SA drawings."""
    return commons_group_fetch("commons_sex_drawings_sa", "sex_drawings", "share-alike", folder, cap, say)


def fetch_commons_sex_photos(folder, cap, say=print):
    """Commons photographs of adult sexual activity (CC0, public domain or CC BY), from Commons' sexual-content
    categories only. Commons requires consent for identifiable people (COM:SEX, COM:IDENT); here a photograph of
    people must also be the uploader's own work, in no deletion or problem category, with no youthful wording."""
    return commons_group_fetch("commons_sex_photos", "sex_photos", "open", folder, cap, say)


def fetch_commons_sex_photos_sa(folder, cap, say=print):
    """The same as fetch_commons_sex_photos, for CC BY-SA photographs."""
    return commons_group_fetch("commons_sex_photos_sa", "sex_photos", "share-alike", folder, cap, say)


def fetch_commons_inclusive(folder, cap, say=print):
    """Commons pictures of LGBTQ+ sex, interracial couples, sex in pregnancy, safer sex and disability and sexuality
    (CC0, public domain or CC BY): drawings, artworks and photographs; photographs of people must be the uploader's
    own work. (Commons has almost nothing on older adults' or disabled people's sexuality: a gap.)"""
    return commons_group_fetch("commons_inclusive", "inclusive", "open", folder, cap, say)


def fetch_commons_inclusive_sa(folder, cap, say=print):
    """The same as fetch_commons_inclusive, for CC BY-SA pictures."""
    return commons_group_fetch("commons_inclusive_sa", "inclusive", "share-alike", folder, cap, say)


def fetch_commons_sex_toys(folder, cap, say=print):
    """Commons product photographs of sex toys (CC0, public domain or CC BY): dildos, vibrators, butt plugs, anal
    beads, rings, love eggs and the like."""
    return commons_group_fetch("commons_sex_toys", "sex_toys", "open", folder, cap, say)


def fetch_commons_sex_toys_sa(folder, cap, say=print):
    """The same as fetch_commons_sex_toys, for CC BY-SA photographs."""
    return commons_group_fetch("commons_sex_toys_sa", "sex_toys", "share-alike", folder, cap, say)


def fetch_commons_contraception(folder, cap, say=print):
    """Commons photographs of condoms, contraceptives and sexual-health items (CC0, public domain or CC BY)."""
    return commons_group_fetch("commons_contraception", "contraception", "open", folder, cap, say)


def fetch_commons_contraception_sa(folder, cap, say=print):
    """The same as fetch_commons_contraception, for CC BY-SA photographs."""
    return commons_group_fetch("commons_contraception_sa", "contraception", "share-alike", folder, cap, say)


# ----------------------------------------------------------------- vintage photographs of NAMED, provably adult people

VINTAGE_CATEGORIES = [("Pin-up photographs", 1), ("Vintage nude photographs", 2), ("Erotische Fotografie 1890-1920", 0),
                      ("Erotische Fotografie 1845-1890", 0), ("Bathing beauties", 1), ("Burlesque performers", 1)]
WIKIDATA = "https://www.wikidata.org/w/api.php"
PD_BEFORE = 1930                          # a photo taken in this year or earlier is public domain in the US


def wikidata_people(s, qids):
    """{qid: (label, birth year, birth date "YYYY-MM-DD" or "")} for the Wikidata items that are humans (P31 Q5)
    with a birth date given at least to the year (P569 precision 9 or more); others are not returned."""
    people = {}
    qids = list(dict.fromkeys(qids))
    for start in range(0, len(qids), 50):
        data = rs.get_json(s, WIKIDATA, params={"action": "wbgetentities", "ids": "|".join(qids[start:start + 50]),
                                                "props": "claims|labels", "languages": "en", "format": "json"})
        for qid, e in ((data or {}).get("entities") or {}).items():
            claims = e.get("claims") or {}
            human = any(((c.get("mainsnak") or {}).get("datavalue") or {}).get("value", {}).get("id") == "Q5"
                        for c in claims.get("P31", []))
            births = []
            for c in claims.get("P569", []):
                v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}
                if v.get("precision", 0) >= 9 and re.match(r"^\+\d{4}-", v.get("time", "")):
                    births.append(v)
            years = {int(v["time"][1:5]) for v in births}
            if human and len(years) == 1:            # one agreed birth year (two different years: not reliable)
                v = births[0]
                date = v["time"][1:11] if v.get("precision") == 11 else ""
                people[qid] = (clean(((e.get("labels") or {}).get("en") or {}).get("value")) or qid,
                               years.pop(), date)
        time.sleep(1)
    return people


def depicted(s, pageids):
    """{pageid: [Wikidata ids]} of the people a Commons file "depicts" (structured data P180)."""
    out = {}
    for start in range(0, len(pageids), 50):
        data = commons_query(s, {"action": "wbgetentities",
                                 "ids": "|".join(f"M{p}" for p in pageids[start:start + 50])}) or {}
        for mid, e in (data.get("entities") or {}).items():
            statements = e.get("statements") or {}
            ids = [((c.get("mainsnak") or {}).get("datavalue") or {}).get("value", {}).get("id")
                   for c in (statements.get("P180") or [])]
            out[int(mid[1:])] = [i for i in ids if i]
    return out


def photo_year(info):
    """(earliest year, full date "YYYY-MM-DD" or "") of a Commons photo's own date, or (None, "")."""
    text = meta_value(info, "DateTimeOriginal")
    years = [int(y) for y in re.findall(r"\b(1[89]\d\d|20[0-2]\d)\b", text)]
    if not years:
        return None, ""
    m = re.search(r"\b(1[89]\d\d|20[0-2]\d)-(\d\d)-(\d\d)\b", text)
    return min(years), (m.group(0) if m and len(set(years)) == 1 else "")


def proven_adult(birth_year, birth_date, year, date):
    """True when a person born then was surely 18 or over on a photo taken then: 19 or more years apart, or 18
    years apart with both exact dates showing the 18th birthday had passed."""
    if year - birth_year >= 19:
        return True
    if year - birth_year == 18 and birth_date and date:
        return date[5:] >= birth_date[5:]
    return False


def fetch_commons_vintage_named(folder, cap, say=print):
    """Commons vintage pin-up, burlesque and art-nude photographs, ONLY of NAMED people whose adulthood is
    PROVABLE: the file "depicts" a Wikidata human with one agreed birth date (at least to the year), and the
    photo's own date shows they were 18 or over. Public domain and taken in 1930 or earlier, or released under CC0
    or CC BY. Anonymous photographs, and any without a date or a birth date, are left out. CREDITS.txt records the
    name, the birth year and the photo year."""
    source = source_by_key("commons_vintage_named")
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    candidates, looked, left = [], 0, 0
    for category, depth in VINTAGE_CATEGORIES:
        for cat in commons_subcats(s, category, depth, ws):
            for pageid, title, info in commons_files(s, cat):
                name = f"commons-{pageid}.jpg"
                if ws.done(name) or any(c[0] == pageid for c in candidates):
                    continue
                looked += 1
                stem = os.path.splitext(title)[0].replace("_", " ")
                description = english_description(meta_value(info, "ImageDescription"))
                licence = meta_value(info, "LicenseShortName")
                categories = meta_value(info, "Categories")
                # "pin-up girl" names a genre of the time; the adulthood check below is by birth date instead.
                text = re.sub(r"pin-?up girls?|bathing girls?|show ?girls?|chorus girls?|ziegfeld girls?", "pin-up",
                              f"{stem} {description}", flags=re.I)
                year, date = photo_year(info)
                why = ""
                if not info.get("thumburl") or not info.get("mime", "").startswith("image/"):
                    why = "not a still picture"
                elif PROBLEM_CATEGORY.search(categories):
                    why = "in a deletion, copyright or identity-problem category"
                elif year is None:
                    why = "the photo has no date, so age cannot be proven"
                elif not (re.match(r"^(public domain|pd\b|pd-)", licence, re.I) and year <= PD_BEFORE) and \
                        not re.match(r"^(cc0|cc by \d|cc-by-\d)", licence, re.I):
                    why = f"not public domain from {PD_BEFORE} or earlier, nor CC0 or CC BY ({licence}, {year})"
                else:
                    why = screen(text, re.sub(r"pin-?up girls?|show ?girls?|chorus girls?|ziegfeld girls?", "",
                                              categories, flags=re.I))
                if why:
                    ws.leave_out(name, stem, why)
                    left += 1
                    continue
                candidates.append((pageid, title, info, stem, description, licence, year, date))
            if len(candidates) > cap * 6 + 40:
                break
        if len(candidates) > cap * 6 + 40:
            break
    shown = depicted(s, [c[0] for c in candidates])
    people = wikidata_people(s, [q for qs in shown.values() for q in qs])
    items = []
    for pageid, title, info, stem, description, licence, year, date in candidates:
        name = f"commons-{pageid}.jpg"
        found = [people[q] for q in shown.get(pageid, []) if q in people]
        if not shown.get(pageid):
            ws.leave_out(name, stem, "no named person (anonymous: age and consent cannot be checked)")
            left += 1
            continue
        if not found or len(found) != len(shown[pageid]):
            ws.leave_out(name, stem, "a depicted person without one reliable birth date on Wikidata")
            left += 1
            continue
        if not all(proven_adult(b, bd, year, date) for _n, b, bd in found):
            ws.leave_out(name, stem, "age 18 or over cannot be proven from the birth and photo dates")
            left += 1
            continue
        who = "; ".join(f"{n} (born {b}, about {year - b} in {year})" for n, b, _bd in found)
        caption = rs.first_sentences(plain(description) or plain(stem), 70, 3)
        thin = useful_words(description or stem) < 5
        text = " ".join(p for p in [
            f"A vintage photograph from {year} of {', '.join(n for n, _b, _bd in found)}.",
            f"Its description says: {sentence(caption)}" if is_english(caption) else "",
            "The record says little more; it is filed on Commons among pin-up, burlesque or nude "
            "photographs." if thin or not is_english(caption) else ""] if p)
        details = "; ".join(f"name: {n}; birth year: {b}; photo year: {year}" for n, b, _bd in found)
        items.append((name, info["thumburl"], text, f"{stem} by {(meta_value(info, 'Artist') or 'unknown')[:100]}, "
                      f"via Wikimedia Commons; shows {who}", licence,
                      "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_"), CONTENT,
                      (THIN_NOTE + " " if thin else "") + f"Adulthood from Wikidata birth year and photo date: {who}.",
                      details))
    say(f"Commons vintage named photographs: {len(items)} usable files")
    left += rs.fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- reading drawing sheets out of a PDF

PDF_OBJECT = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj\b", re.S)
PDF_STREAM = re.compile(rb"\bstream(?:\r\n|\r|\n)")


def pdf_number(head, name, default=None):
    """A whole number from a PDF object's dictionary (/Width 2560), or default when it is missing or indirect."""
    m = re.search(rb"/" + name + rb"\s+(-?\d+)(?!\s+\d+\s+R)", head)
    return int(m.group(1)) if m else default


def ccitt_tiff(data, width, height, k, black_is_1=False):
    """TIFF bytes around a PDF's CCITT fax-coded picture (the way USPTO stores drawing sheets: black and white,
    Group 4), so that Pillow can open it. k < 0 is Group 4, otherwise Group 3."""
    compression = 4 if k < 0 else 3
    entries = [(256, 4, width), (257, 4, height), (258, 3, 1), (259, 3, compression),
               (262, 3, 1 if black_is_1 else 0), (273, 4, 0), (278, 4, height), (279, 4, len(data))]
    if compression == 3:
        entries.append((292, 4, 1 if k > 0 else 0))   # T4Options: two-dimensional coding when k > 0
    entries.sort()
    start = 8 + 2 + 12 * len(entries) + 4
    out = b"II*\x00" + struct.pack("<I", 8) + struct.pack("<H", len(entries))
    for tag, kind, value in entries:
        if tag == 273:
            value = start                              # the picture data comes straight after the directory
        out += struct.pack("<HHII", tag, kind, 1, value) if kind == 4 else struct.pack("<HHIHH", tag, kind, 1,
                                                                                         value, 0)
    return out + struct.pack("<I", 0) + data


def pdf_images(data):
    """[picture bytes Pillow can open] for the pictures in a PDF, in the order they are stored (a USPTO drawings
    PDF has one scanned sheet per page, stored in page order). Fax-coded (CCITT), JPEG and simple compressed
    (Flate) pictures are read; anything else is skipped. Only Pillow and the standard library are needed."""
    found = []
    for m in PDF_OBJECT.finditer(data or b""):
        body = m.group(3)
        s = PDF_STREAM.search(body)
        if not s:
            continue
        head = body[:s.start()]
        if not re.search(rb"/Subtype\s*/Image\b", head):
            continue
        raw = body[s.end():]
        length = pdf_number(head, b"Length")
        end = raw.rfind(b"endstream")
        raw = raw[:length] if length is not None and length <= len(raw) else raw[:end].rstrip(b"\r\n")
        width, height = pdf_number(head, b"Width"), pdf_number(head, b"Height")
        if not width or not height:
            continue
        try:
            if b"/CCITTFaxDecode" in head:
                found.append(ccitt_tiff(raw, width, height, pdf_number(head, b"K", 0),
                                        bool(re.search(rb"/BlackIs1\s+true", head))))
            elif b"/DCTDecode" in head:
                found.append(raw)
            elif b"/FlateDecode" in head and not re.search(rb"/Predictor\s+([2-9]|1\d)", head):
                from PIL import Image
                bits = pdf_number(head, b"BitsPerComponent", 8)
                mode = {1: "1", 8: "RGB" if b"/DeviceRGB" in head else "L"}.get(bits)
                if mode:
                    picture = Image.frombytes(mode, (width, height), zlib.decompress(raw))
                    out = io.BytesIO()
                    picture.save(out, "PNG")
                    found.append(out.getvalue())
        except (ValueError, zlib.error, OSError):
            continue                                   # a picture that cannot be read: skipped
    return found


# ----------------------------------------------------------------- US patent drawings (public domain, USPTO)

# US patents: the USPTO's terms (https://www.uspto.gov/terms-use-uspto-websites) say "Subject to limited
# exceptions reflected in 37 CFR 1.71(d) & (e) and 1.84(s), the text and drawings of a patent are typically not
# subject to copyright restrictions." Those exceptions are a copyright or mask-work notice the applicant put in the
# patent; a patent with any such notice (or any copyright wording at all) is left out here.
# The drawings, the full text and the search come from the USPTO Open Data Portal (api.uspto.gov), the USPTO's own
# channel for automated use. It needs a free API key (data.uspto.gov, "API key management"), read from the
# environment variable USPTO_ODP_API_KEY (in a GitHub workflow: a repository secret of that name). Without it the
# collection is skipped with a plain message. The key is only ever sent to api.uspto.gov.
# The PatentsView API was paused on 20 March 2026 while it moves into the Open Data Portal; Google Patents is not
# used (see NOT_INCLUDED).
USPTO_KEY_ENV = "USPTO_ODP_API_KEY"
ODP = "https://api.uspto.gov/api/v1/"
ODP_HOST = "https://api.uspto.gov/"
PATENT_TERMS = "https://www.uspto.gov/terms-use-uspto-websites"
PATENT_LICENCE = ("public domain (USPTO: \"the text and drawings of a patent are typically not subject to copyright "
                  "restrictions\"; patents with a copyright or mask-work notice, 37 CFR 1.71(d)/(e), left out)")
PATENT_PER_PATENT = 3                     # at most this many drawing sheets from one patent (so many patents share)
PATENT_PAUSE = 1.0                        # seconds between calls to the Open Data Portal
PATENT_XML_MOST = 20_000_000              # bytes: a bigger "full text" is a weekly bulk file, not one patent

# What is searched: (field of the Open Data Portal's search, the query, the class codes an answer must carry).
# CPC A61H19 "Massage for the genitals; devices for improving sexual intercourse"; A61F5/41 "Devices for promoting
# penis erection"; A61F6/04 "Condoms, sheaths or the like" (A61F2006/04x oral condoms); A61F6/065 "Condom-like
# devices worn by females"; A61F5/4553 receptacles "placed in the vagina, e.g. for catamenial use" (menstrual cups);
# and the old US classes 600/38 to 600/41 (sexual appliances), used until 2015.
PATENT_FAMILIES = [
    ("cpcClassificationBag", r"A61H19*", ("A61H19",)),
    ("cpcClassificationBag", r"A61F5\/41*", ("A61F5/41",)),
    ("cpcClassificationBag", r"A61F6\/04*", ("A61F6/04",)),
    ("cpcClassificationBag", r"A61F2006\/04*", ("A61F2006/04",)),
    ("cpcClassificationBag", r"A61F6\/065*", ("A61F6/065",)),
    ("cpcClassificationBag", r"A61F5\/4553*", ("A61F5/4553",)),
    ("uspcSymbolText", r"600\/038* OR applicationMetaData.uspcSymbolText:600\/039* OR "
                       r"applicationMetaData.uspcSymbolText:600\/040* OR applicationMetaData.uspcSymbolText:600\/041*",
     ("600/038", "600/039", "600/040", "600/041")),
]

# The device in plain words, from the most specific class the patent carries (first match wins).
PATENT_KINDS = [
    ("A61F6/065", "a female condom (a condom worn inside the vagina)"),
    ("A61F2006/042", "an oral condom (a barrier for oral sex)"),
    ("A61F6/04", "a condom"), ("A61F2006/04", "a condom"),
    ("A61F5/4553", "a menstrual cup or a similar device worn inside the vagina"),
    ("A61F5/41", "a device that helps the penis become or stay erect"),
    ("A61H19/44", "a long, rounded device for putting inside the body, such as a dildo"),
    ("A61H19/40", "a device for putting inside the genitals (such as the vagina)"),
    ("A61H19/34", "a device for stimulating the clitoris"),
    ("A61H19/32", "a device the genitals are put into, such as a vibrating penis ring"),
    ("A61H19/30", "a device for stimulating the genitals from outside"),
    ("A61H19/50", "a device for use during sex"),
    ("A61H19", "a device for sexual stimulation or genital massage"),
    ("600/03", "a sexual device"), ("600/04", "a sexual device"),
]

# Any copyright or mask-work wording: the patent is left out (37 CFR 1.71(d)/(e), 1.84(s)).
COPYRIGHT_NOTICE = re.compile(r"\bcopyright\w*|\bmask[- ]works?\b|©|&#169;|&copy;|\(c\)\s*(?:19|20)\d\d\b|"
                              r"\ball rights reserved\b", re.I)

# Technical phrases that would wrongly look like a child, sleep or a "kind" ("sleep mode", "Young's modulus", "of
# this kind"): taken out before the patent's words are screened. Nothing else is softened.
TECH_NEUTRAL = re.compile(
    r"\b(?:sleep|standby|wake|idle|power-?save)[- ]?(?:modes?|states?|timers?|functions?|cycles?)\b|"
    r"\byoung'?s modulus\b|\b(?:a|any|this|that|the same|each|every|some|other|similar|one|which|what|all) "
    r"kinds? of\b|\bof (?:this|that|the same|any|a similar|this general) kind\b|\bkind of\b", re.I)

# In a patent's full text: harm, no consent, restraint and BDSM (with review_sources.CHILD and ANIMAL from above).
PATENT_HARM = re.compile(
    r"\b(?:rap(?:e|ed|es|ing|ist)|non-?consensual\w*|without (?:her|his|their|the (?:user|partner|person|wearer)'?s?) "
    r"(?:consent|knowledge)|unconscious|asleep|sleeping (?:person|partner|user|woman|man)|drugged|bdsm|bondage|"
    r"shibari|restrain\w*|handcuff\w*|shackl\w*|manacl\w*|whip\w*|flogg\w*|spank\w*|tortur\w*|gag(?:ged|s)?|"
    r"punish\w*|humiliat\w*|dominatri\w*|slaves?|incest\w*|voyeur\w*|hidden cameras?|sadis\w*|masochis\w*|"
    r"fetish\w*|chastity)\b", re.I)

# A figure description that names the body: the drawing may show anatomy (the reviewer is told).
BODY_WORDS = re.compile(r"\b(?:user|wearer|body|anatom\w*|penis|penile|vagina\w*|vulva\w*|clitor\w*|labia\w*|"
                        r"anus|anal|rectum|scrotum|testic\w*|perine\w*|pelvi\w*|breasts?|nipples?|man|woman|male|"
                        r"female|person|hand|finger\w*|torso|thigh\w*|groin|cervix|uterus)\b", re.I)

FIG_START = re.compile(r"^\s*(?:FIGS?|FIGURES?|Figs?|Figures?)\s*\.?\s*((?:\d+\s*[A-Za-z]?(?:\(\w\))?\s*(?:,|and|&|"
                       r"to|through|thru|-|–)?\s*)+?)\s+(?:is|are|shows?|illustrates?|depicts?|represents?|presents?|"
                       r"provides?|displays?)\b\s*(.*)$", re.S)
FIG_SPLIT = re.compile(r"(?<=[.;])\s+(?=(?:FIGS?|FIGURES?|Figs?|Figures?)\s*\.?\s*\d)")

# The patent wording that says nothing about the picture, taken out of a figure description.
FIG_BOILERPLATE = [re.compile(p, re.I) for p in [
    r",?\s*(?:constructed\s+|made\s+|formed\s+|configured\s+)?(?:in accordance with|according to)\s+(?:the\s+)?"
    r"(?:principles|teachings)\s+of\s+(?:the|this)\s+(?:present\s+)?(?:invention|disclosure)\b",
    r",?\s*(?:(?:constructed|made|formed|configured)\s+)?(?:according to|in accordance with|consistent with|"
    r"embodying|of|in|for|showing|illustrating)?\s*(?:an?|one|the|another|a further|some|certain|various|other)\s+"
    r"(?:(?:preferred|exemplary|alternative|alternate|illustrative|example|first|second|third|fourth|fifth|further|"
    r"other|particular|non-limiting|specific|modified|additional)\s+)*(?:embodiments?|aspects?|implementations?)\b"
    r"(?:\s+(?:of|according to|in accordance with)\s+(?:the|this)\s+(?:present\s+)?(?:invention|disclosure|"
    r"application|subject matter|teachings?))?",
    r",?\s*(?:of|according to|in accordance with|embodying)\s+(?:the|this)\s+(?:present\s+)?(?:invention|"
    r"disclosure|application)\b",
    r"\s+(?:hereof|herein|thereof)\b", r"\s+of the$"]]

# Patent drawing words in plain English.
FIG_PLAIN = [(re.compile(p, re.I), w) for p, w in [
    (r"\bFIGS\.?\s*(?=\d)", "figures "), (r"\bFIG\.?\s*(?=\d)", "figure "),
    (r"\bcross[- ]?sectional (views?)", r"cross-section \1 (as if cut through)"),
    (r"\b(?<!cross-)(?<!cross )sectional (views?)", r"cross-section \1 (as if cut through)"),
    (r"\bexploded (?:perspective |isometric )?(views?)", r"exploded \1 (the parts drawn apart)"),
    (r"\b(side|front|rear|back|top|bottom|left|right|end) elevation(?:al)? (views?)", r"\1 \2"),
    (r"\belevation(?:al)? (views?)", r"side-on \1"), (r"\btop plan (views?)", r"\1 from above"),
    (r"\bbottom plan (views?)", r"\1 from below"), (r"\bplan (views?)", r"\1 from above (plan view)"),
    (r"\bisometric (views?)", r"three-dimensional \1"), (r"\bperspective (views?)", r"\1 at an angle (perspective)"),
    (r"\bschematic (?:diagram|view|illustration|representation|drawing)(s?)\b", r"simplified diagram\1"),
    (r"\bschematic(?:ally)?\b", "simplified"), (r"\bblock diagram\b", "block diagram (boxes for the parts, not a "
                                                                        "picture of the device)"),
    (r"\bflow ?charts?\b|\bflow diagrams?\b", "flow chart (steps, not a picture of the device)"),
    (r"\btaken (?:generally |substantially )?(?:along|on|through) (?:the )?(?:lines?|plane) ([\w']+) ?- ?([\w']+)",
     r"as if cut along line \1-\2"), (r"\bpartially cut[- ]?away\b|\bpartial cut[- ]?away\b|\bcut[- ]?away\b",
                                      "with part cut away to show the inside"),
    (r"\bdistal end\b", "far end (distal end)"), (r"\bproximal end\b", "near end (proximal end)"),
]]


def figure_plain(text):
    """A patent's figure description in plain words: "a perspective view of a vibrator according to one embodiment of
    the present invention;" becomes "a view at an angle (perspective) of a vibrator"."""
    text = clean(text).rstrip(" ;.:,")
    text = re.sub(r"\s*(?:;|,)?\s*\band\s*$", "", text)
    for pattern in FIG_BOILERPLATE:
        text = pattern.sub("", text)
    for pattern, words in FIG_PLAIN:
        text = pattern.sub(words, text)
    text = re.sub(r" \(as if cut through\)(,? as if cut along)", r"\1", text)
    text = re.sub(r"\s+([,;.])", r"\1", clean(text)).rstrip(" ;.:,")
    return re.sub(r"\s*\band$", "", text)


def figure_labels(text):
    """The figure labels of a figure description's start ("2A and 2B" -> ["2A", "2B"]; "3 through 5" -> 3, 4, 5)."""
    tokens = re.findall(r"\d+\s*[A-Za-z]?(?![a-z])|through|thru|to|-|–", text)
    labels, i = [], 0
    while i < len(tokens):
        t = tokens[i].replace(" ", "")
        if t in ("through", "thru", "to", "-", "–"):
            i += 1
            continue
        if (i + 2 < len(tokens) and tokens[i + 1] in ("through", "thru", "to", "-", "–") and t.isdigit()
                and tokens[i + 2].replace(" ", "").isdigit() and 0 < int(tokens[i + 2]) - int(t) < 30):
            labels += [str(n) for n in range(int(t), int(tokens[i + 2].replace(" ", "")) + 1)]
            i += 3
            continue
        labels.append(t.upper() if t[-1:].isalpha() else t)
        i += 1
    return list(dict.fromkeys(labels))


def brief_figures(paragraphs):
    """[(figure labels, plain description)] from the paragraphs of a patent's "Brief description of the drawings"
    (each "FIG. 1 is a ..." sentence; one paragraph may hold several)."""
    if isinstance(paragraphs, str):
        paragraphs = [paragraphs]
    out = []
    for paragraph in paragraphs:
        for piece in FIG_SPLIT.split(clean(paragraph)):
            m = FIG_START.match(piece)
            if not m:
                continue
            labels, words = figure_labels(m.group(1)), figure_plain(m.group(2))
            if labels and words:
                out.append((labels, words))
    return out


def xml_text(fragment):
    """Plain text of an XML fragment (tags removed, entities decoded)."""
    return clean(re.sub(r"<[^>]+>", " ", fragment or ""))


def patent_text(xml):
    """{title, abstract, drawings: [paragraphs], text: all words, number, date, inventors} from a USPTO patent's
    full-text XML (us-patent-grant). The "Brief description of the drawings" is its <description-of-drawings>, the
    part between the brief-description-of-drawings markers, or the paragraphs after that heading."""
    xml = xml or ""
    section = ""
    m = re.search(r"<description-of-drawings\b[^>]*>(.*?)</description-of-drawings>", xml, re.S)
    if m:
        section = m.group(1)
    else:
        m = re.search(r"<\?brief-description-of-drawings[^>]*end=\"lead\"[^>]*\?>(.*?)"
                      r"<\?brief-description-of-drawings[^>]*end=\"tail\"[^>]*\?>", xml, re.S)
        if m:
            section = m.group(1)
        else:
            m = re.search(r"<heading\b[^>]*>\s*(?:BRIEF )?DESCRIPTION OF (?:THE )?(?:SEVERAL VIEWS OF THE )?"
                          r"(?:DRAWINGS?|FIGURES?)[^<]*</heading>(.*?)(?=<heading\b|</description>)", xml, re.S | re.I)
            section = m.group(1) if m else ""
    paragraphs = [xml_text(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", section, re.S)] or \
        ([xml_text(section)] if section.strip() else [])
    names = []
    for who in re.findall(r"<(?:inventor|us-applicant|applicant)\b[^>]*>(.*?)</(?:inventor|us-applicant|applicant)>",
                          xml, re.S):
        first_name = xml_text("".join(re.findall(r"<first-name>(.*?)</first-name>", who, re.S)))
        last_name = xml_text("".join(re.findall(r"<last-name>(.*?)</last-name>", who, re.S)))
        if last_name and f"{first_name} {last_name}".strip() not in names:
            names.append(f"{first_name} {last_name}".strip())
    pub = re.search(r"<publication-reference\b.*?<doc-number>(.*?)</doc-number>.*?<date>(\d{8})</date>", xml, re.S)
    title = re.search(r"<invention-title\b[^>]*>(.*?)</invention-title>", xml, re.S)
    abstract = re.search(r"<abstract\b[^>]*>(.*?)</abstract>", xml, re.S)
    return {"title": xml_text(title.group(1)) if title else "", "abstract": xml_text(abstract.group(1)) if abstract
            else "", "drawings": [p for p in paragraphs if p], "text": xml_text(xml),
            "number": pub.group(1).lstrip("0") if pub else "", "date": pub.group(2) if pub else "",
            "inventors": names}


def patent_problem(title, abstract, figure_words, full_text, raw=""):
    """"" when a patent may be used; otherwise why it is left out: a copyright or mask-work notice (37 CFR 1.71(d)/(e)),
    screen() on its title, abstract and figure descriptions (adults only, consent, no violence, no animals), or a
    child, an animal, harm, restraint or BDSM anywhere in its full text."""
    if COPYRIGHT_NOTICE.search(f"{raw} {full_text}"):
        return "the patent carries a copyright or mask-work notice (37 CFR 1.71(d)/(e)), so it is not free to use"
    why = screen(*(TECH_NEUTRAL.sub(" ", clean(t)) for t in (title, abstract, figure_words)))
    if why:
        return why
    text = TECH_NEUTRAL.sub(" ", clean(full_text))
    for pattern, reason in ((rs.CHILD, "the patent's text mentions a child or young person"),
                            (ANIMAL, "the patent's text mentions an animal or creature"),
                            (PATENT_HARM, "the patent's text mentions harm, no consent, restraint or BDSM")):
        m = pattern.search(text)
        if m:
            return f"{reason} ('{m.group(0)}')"
    if any(a < 18 for a in rs.ages(text)):
        return "the patent's text gives an age under 18"
    return ""


def patent_kind(codes):
    """The device in plain words from a patent's class codes (CPC like "A61H19/44" or US like "600/038000")."""
    codes = [re.sub(r"\s+", "", clean(c)).upper() for c in codes or [] if c]
    for prefix, words in PATENT_KINDS:
        if any(c.startswith(prefix.upper()) for c in codes):
            return words
    return "a sexual device"


def patent_title(title):
    """A patent title as a plain title ("VIBRATING MASSAGER" -> "Vibrating massager")."""
    title = clean(title).rstrip(".")
    if title.isupper():
        title = title.capitalize()
    return title[:1].upper() + title[1:]


def patent_credit(number, title, inventors, year):
    """ "US Patent 9,876,543, Title, First Inventor and others, 2017; public domain (USPTO)"."""
    shown = f"{int(number):,}" if str(number).isdigit() else number
    who = ", ".join(inventors[:2]) + (" and others" if len(inventors) > 2 else "") if inventors else \
        "inventor not stated"
    return f"US Patent {shown}, {patent_title(title)}, {who}, {year or 'year not stated'}; public domain (USPTO)"


def sheet_figures(figures, sheets):
    """{sheet number (1, 2, ...): (labels, description)} when the drawing sheets can be matched to the figures one to
    one (as many sheets as figure descriptions, each about one figure); {} when they cannot."""
    if not figures or len(figures) != sheets or any(len(labels) != 1 for labels, _ in figures):
        return {}
    return {i + 1: figures[i] for i in range(sheets)}


def patent_draft(kind, title, sheet, sheets, figures):
    """(draft description, note for the reviewer) for one drawing sheet of a patent: "This is a drawing from a US
    patent for a condom, titled "...": figure 2, a side view ..." when the sheet's figure is known; otherwise the
    sheet number and the patent's own list of figures, and the reviewer is asked which figure the sheet shows."""
    matched = sheet_figures(figures, sheets).get(sheet)
    lead = f'This is a drawing from a US patent for {kind}, titled "{patent_title(title)}"'
    style = "Like most patent drawings, it is a black-and-white line drawing, with numbers that point to the parts."
    if matched:
        text = f"{lead}: figure {matched[0][0]}, {matched[1]}. {style}"
        note = ""
    else:
        listed = "; ".join(f"figure{'s' if len(l) > 1 else ''} {' and '.join(l)}, {w}" for l, w in figures[:6])
        text = (f"{lead} (drawing sheet {sheet} of {sheets}). The patent lists its figures like this: {listed}"
                f"{'; and more' if len(figures) > 6 else ''}. {style}")
        note = ("Which figure is on this sheet is not known: please say which figure or figures it shows and keep "
                "only their description.")
    if BODY_WORDS.search(" ".join(w for _, w in figures)):
        note += (" The patent's figure descriptions mention the body, so a drawing may show anatomy: check that it "
                 "shows only an adult body.")
    return text, note.strip()


def odp_get(s, key, url, **kwargs):
    """A GET from the Open Data Portal with the API key (sent only to api.uspto.gov), pausing politely; the response
    or None."""
    if not url.startswith(ODP_HOST):
        return None
    time.sleep(PATENT_PAUSE)
    return rs.get(s, url, headers={"X-API-KEY": key, "Accept": "*/*"}, **kwargs)


def odp_search(s, key, family, offset, limit=100):
    """One page of granted utility patents of one PATENT_FAMILIES entry: [(patent number, application number,
    title, inventors, year, class codes, grant XML address)]; None when the key is refused."""
    field, query, prefixes = family
    body = {"q": f"applicationMetaData.{field}:{query}",
            "filters": [{"name": "applicationMetaData.applicationTypeLabelName", "value": ["Utility"]}],
            "pagination": {"offset": offset, "limit": limit}}
    time.sleep(PATENT_PAUSE)
    data = None
    for attempt in range(4):
        try:
            r = s.post(ODP + "patent/applications/search", json=body, timeout=90,
                       headers={"X-API-KEY": key, "Accept": "application/json"})
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(5 * (attempt + 1))
            continue
        if r.status_code in (401, 403):
            return None
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(60, int(r.headers.get("Retry-After") or 0) or 10 * (attempt + 1)))
            continue
        data = r.json() if r.status_code == 200 else {}
        break
    rows = []
    for x in (data or {}).get("patentFileWrapperDataBag") or []:
        md = x.get("applicationMetaData") or {}
        number = clean(md.get("patentNumber"))
        codes = list(md.get("cpcClassificationBag") or []) + [clean(md.get("uspcSymbolText"))]
        flat = [re.sub(r"\s+", "", c).upper() for c in codes if c]
        if not number or not any(c.startswith(p.upper()) for c in flat for p in prefixes):
            continue                                   # not granted, or not really in the class searched
        inventors = [clean(i.get("inventorNameText") or f"{i.get('firstName', '')} {i.get('lastName', '')}")
                     for i in md.get("inventorBag") or []]
        rows.append((number, clean(x.get("applicationNumberText")), clean(md.get("inventionTitle")),
                     [i for i in inventors if i] or [clean(md.get("firstInventorName"))],
                     clean(md.get("grantDate"))[:4], codes,
                     clean((x.get("grantDocumentMetaData") or {}).get("fileLocationURI"))))
    return rows


def grant_xml(s, key, url):
    """The full-text XML of one granted patent from its Open Data Portal address, or "" (a weekly bulk file, which
    holds thousands of patents, is not downloaded)."""
    if not url:
        return ""
    r = odp_get(s, key, url, stream=True)
    if r is None or r.status_code != 200:
        return ""
    if int(r.headers.get("Content-Length") or 0) > PATENT_XML_MOST:
        r.close()
        return ""
    data = b""
    for chunk in r.iter_content(1 << 16):
        data += chunk
        if len(data) > PATENT_XML_MOST:
            r.close()
            return ""
    if data[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                names = [n for n in z.namelist() if n.lower().endswith(".xml")]
                data = z.read(names[0]) if names else b""
        except zipfile.BadZipFile:
            return ""
    text = data.decode("utf-8", "replace")
    return text if text.count("<us-patent-grant") == 1 else ""


def drawings_pdf_url(s, key, application):
    """The address of the latest drawings document (code "DRW...", PDF) of an application, or ""."""
    r = odp_get(s, key, f"{ODP}patent/applications/{application}/documents")
    try:
        docs = (r.json() if r is not None and r.status_code == 200 else {}).get("documentBag") or []
    except ValueError:
        docs = []
    best = ("", "")
    for d in docs:
        if not clean(d.get("documentCode")).upper().startswith("DRW"):
            continue
        for option in d.get("downloadOptionBag") or []:
            if clean(option.get("mimeTypeIdentifier")).upper() == "PDF" and option.get("downloadUrl"):
                when = clean(d.get("officialDate"))
                if when >= best[0]:
                    best = (when, option["downloadUrl"])
    return best[1]


def fetch_us_patent_drawings(folder, cap, say=print):
    """US patent drawings of sex toys, erection aids, condoms and menstrual cups (CPC A61H19, A61F5/41, A61F6/04,
    A61F6/065, A61F5/4553 and the old US classes 600/38-41), from the USPTO Open Data Portal: the drawing sheets
    (from the patent's drawings PDF) with each figure's own description from the patent's "Brief description of the
    drawings", in plain words, and the patent's title. Public domain; any patent with a copyright or mask-work notice
    is left out. Needs a free key in USPTO_ODP_API_KEY; without it nothing is downloaded and the reason is said.
    At most PATENT_PER_PATENT sheets per patent; the patents are taken in a shuffled order that stays the same from
    run to run, so a stopped run carries on."""
    key = os.environ.get(USPTO_KEY_ENV, "").strip()
    source = source_by_key("us_patent_drawings")
    if not key:
        message = (f"{source['name']}: skipped. This collection needs a free USPTO Open Data Portal API key in the "
                   f"{USPTO_KEY_ENV} environment variable (in a GitHub workflow, a repository secret of that name). "
                   f"A key is made at data.uspto.gov, under API key management. Nothing was downloaded.")
        say(message)
        return message
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    want = max(40, cap // PATENT_PER_PATENT * 2 // len(PATENT_FAMILIES) + 20)
    lists = []
    for family in PATENT_FAMILIES:
        found, offset = [], 0
        while len(found) < want and offset < 3000:
            rows = odp_search(s, key, family, offset)
            if rows is None:
                message = (f"{source['name']}: the Open Data Portal refused the key in {USPTO_KEY_ENV}. Check that "
                           "the key is right and still active (data.uspto.gov, API key management).")
                say(message)
                return ws.finish(0, 0) + " " + message
            found += [(f"uspatent-{r[0]}", r) for r in rows]
            if not rows:
                break
            offset += 100
        random.Random(f"us_patent_drawings {family[1]}").shuffle(found)
        lists.append(found)
    patents = take_turns(lists)
    say(f"US patent drawings: {len(patents)} granted patents found in the classes searched")
    if not patents:
        say("The search found nothing. The Open Data Portal's search wording may have changed; nothing was added.")
    looked = left = 0
    for tag, (number, application, title, inventors, year, codes, xml_url) in patents:
        if ws.full(cap) and (len(ws.left_out) >= SHOW_LEFT_OUT or looked > cap // PATENT_PER_PATENT + 20):
            break
        if tag in ws.tried:
            continue
        looked += 1
        why = patent_problem(title, "", "", "")
        info = {}
        if not why:
            info = patent_text(grant_xml(s, key, xml_url))
            if not info["text"]:
                why = "no full text of the patent to check (its figure descriptions and wording)"
        if not why:
            why = patent_problem(info["title"] or title, info["abstract"], " ".join(info["drawings"]),
                                 info["text"])
        figures = brief_figures(info.get("drawings")) if not why else []
        if not why and not figures:
            why = "no figure descriptions (\"FIG. 1 is ...\") in the patent"
        if why:
            ws.leave_out(tag, f"US {number}: {title}", why)
            left += 1
            continue
        if ws.full(cap):
            continue                                   # full: only screened, to show what the filters leave out
        pdf_url = drawings_pdf_url(s, key, application)
        r = odp_get(s, key, pdf_url, timeout=180) if pdf_url else None
        sheets = pdf_images(r.content) if r is not None and r.status_code == 200 else []
        if not sheets:
            ws.leave_out(tag, f"US {number}: {title}", "no drawings document could be read")
            left += 1
            continue
        title = info["title"] or title
        credit = patent_credit(number, title, info["inventors"] or inventors, year or info["date"][:4])
        page = f"https://ppubs.uspto.gov/pubwebapp/external.html?q={number}.pn."
        kind = patent_kind(codes)
        for sheet in range(1, min(len(sheets), PATENT_PER_PATENT) + 1):
            name = f"uspatent-{number}-sheet{sheet}.jpg"
            data = rs.jpeg(sheets[sheet - 1])
            if ws.done(name) or data is None or ws.full(cap):
                continue
            text, note = patent_draft(kind, title, sheet, len(sheets), figures)
            ws.add(name, data, text, credit, PATENT_LICENCE, page, CONTENT,
                   (note + " " if note else "") + "Drawings as filed with the application (USPTO file wrapper).")
        ws.mark_tried(tag)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Openverse product photos (no person)

# Openverse (api.openverse.org, run by the WordPress project) indexes openly licensed pictures held elsewhere. Its
# terms (https://docs.openverse.org/terms_of_service.html): keep to the rate limits (without an account 20 searches
# a minute and 200 a day), do not scrape the catalogue, respect the terms of the sites that hold the pictures, credit
# CC works, and say that the product was made with Openverse but is not endorsed by it. Openverse does not check
# licences, so a Wikimedia Commons picture's licence is read again from Commons itself.
# Almost all of Openverse's sex-toy and condom pictures are on Flickr, whose terms forbid robots and scraping
# outside its own API (which needs an account): Flickr pictures are not downloaded (see NOT_INCLUDED). Only the
# sites in OV_SITES, whose terms allow re-use of their open pictures by program, are used.
OPENVERSE = "https://api.openverse.org/v1/images/"
OPENVERSE_TERMS = "https://docs.openverse.org/terms_of_service.html"
OV_PAUSE = 3.5                            # seconds between searches (20 a minute without an account)
OV_PAGES = 3                              # result pages of 20 per search (200 searches a day without an account)
OV_LICENCES = {"open": "cc0,pdm,by", "share-alike": "by-sa"}
OV_SITES = {"wikimedia": "Wikimedia Commons", "wellcome_collection": "Wellcome Collection",
            "met": "The Metropolitan Museum of Art", "clevelandmuseum": "Cleveland Museum of Art",
            "europeana": "Europeana", "smithsonian": "the Smithsonian"}
OV_QUERIES = ("dildo", "sex toy", "vibrator sex toy", "butt plug", "anal beads", "cock ring", "love eggs",
              "kegel balls", "strap-on dildo", "condom", "female condom", "dental dam", "personal lubricant",
              "menstrual cup", "vaginal ring", "contraceptive diaphragm", "intrauterine device", "contraceptive pills")

# What the picture must be about: a sex toy or a sexual-health item. "vibrator", "lubricant" and "diaphragm" also
# name machines, so they count only with a word that makes them sexual.
PRODUCT = re.compile(
    r"\b(dildos?|sex ?toys?|butt ?plugs?|anal (?:beads?|plugs?|toys?)|cock ?rings?|penis rings?|love eggs?|"
    r"ben ?wa balls?|kegel (?:balls?|weights?|exercisers?)|strap-?ons?|(?:(?:fe)?male |internal |external |oral )?"
    r"condoms?|femidoms?|dental dams?|"
    r"menstrual cups?|vaginal rings?|nuva ?rings?|intrauterine devices?|iuds?|contraceptive (?:pills?|implants?|"
    r"diaphragms?|devices?|sponges?|patch(?:es)?)|birth control pills?|diaphragms? \(contracepti\w+\)|"
    r"(?:sex|adult|personal|clitoral|g-?spot|wand|bullet|couples?'?) (?:toy )?vibrators?|"
    r"vibrators? \((?:sex|adult) toy\)|personal (?:lubricants?|lube)|sexual lubricants?|lubricant gel)\b", re.I)
PRODUCT_CONTEXT = re.compile(r"\b(sex(?:ual)?|adult|erotic|personal|intimate|pleasure|toys?)\b", re.I)
NOT_PRODUCT = re.compile(r"\b(newfoundland|town|village|road ?sign|street sign|concrete|engineering|laboratory "
                         r"vibrator|shaker table|vibration test\w*|nasa|machine|engine|automotive|car|bicycle|"
                         r"industrial|vending|dispenser|advert\w*|billboard|poster|campaign|protest\w*|march|"
                         r"demonstration|cartoon|meme|drawing|sculpture|art|graffiti)\b", re.I)

# The sites porn and adult pictures come from (never used).
ADULT_SITE = re.compile(r"(porn|xxx|xhamster|xvideos|redtube|youporn|onlyfans|chaturbate|brazzers|motherless|"
                        r"spankbang|fetlife|literotica|kink\.com|clips4sale|manyvids|\bsex\.com|nsfw|camgirl|"
                        r"adultfriendfinder|eporner|tnaflix|beeg|tube8|hentai)", re.I)

# Words that mean a person may be in the picture (also the machine-made tags Openverse adds).
OV_PERSON = re.compile(
    r"\b(person|persons|people|man|men|woman|women|adults?|girls?|boys?|guys?|lad(?:y|ies)|child\w*|kids?|bab(?:y|ies)|"
    r"teen\w*|portrait\w*|faces?|hands?|fingers?|body|bodies|skin|human\w*|models?|selfies?|lips|mouth|legs?|feet|"
    r"foot|arms?|nude|naked|nudity|breasts?|nipples?|penis|vagina|vulva|buttocks|bum|ass|couples?|lingerie|"
    r"underwear|bikini|female|male|wearing|worn|wears|crowd|audience|speaker|students?|fashion|beauty|sexy|sensual|"
    r"poses?|posing|smil\w*|hair|he|she|his|her|him|self|myself|me|my|using|holding|held|user|users)\b", re.I)
# Sexual acts, porn words, fetish and BDSM (with screen() for the rest).
OV_ACT = re.compile(
    r"\b(fuck\w*|blow-?jobs?|hand-?jobs?|masturbat\w*|orgasm\w*|penetrat\w*|pegging|fisting|having sex|sex acts?|"
    r"intercourse|anal sex|oral sex|threesome|orgy|orgies|cum\w*|porn\w*|xxx|nsfw|erotic\w*|hentai|fetish\w*|"
    r"kink\w*|leather|latex fetish|collars?|cuffs?|harness\w*|gimp|mistress|master|submissive|dominant|"
    r"pet ?play|puppy ?play|pony ?play|chastity|spreader|sounding|electro-?play|e-?stim)\b", re.I)


# Product wording that is not a person ("adult toys", "an adult shop", "for adults only").
ADULT_PHRASE = re.compile(r"\badult (?:toys?|products?|stores?|shops?|novelt\w+|items?|goods)\b|"
                          r"\bfor adults(?: only)?\b|\badults only\b", re.I)


def ov_tags(item):
    """(tags people gave, all tags including the machine-made ones) of an Openverse record."""
    tags = item.get("tags") or []
    given = [clean(t.get("name")) for t in tags if isinstance(t, dict) and not t.get("accuracy")]
    every = [clean(t.get("name")) for t in tags if isinstance(t, dict)]
    return [t for t in given if t], [t for t in every if t]


def ov_site(item):
    """The plain name of an Openverse record's source site when its terms allow re-use by program; "" otherwise."""
    source = clean(item.get("source")).lower()
    if source.startswith("smithsonian"):
        return OV_SITES["smithsonian"]
    return OV_SITES.get(source, "")


def ov_licence(item):
    """("open" or "share-alike", plain licence) of an Openverse record; ("", "") for anything else (NC, ND ...)."""
    lic, version = clean(item.get("license")).lower(), clean(item.get("license_version"))
    if lic in ("cc0", "pdm"):
        return "open", "CC0" if lic == "cc0" else "public domain (Public Domain Mark)"
    if lic == "by":
        return "open", f"CC BY {version}".strip()
    if lic == "by-sa":
        return "share-alike", f"CC BY-SA {version}".strip()
    return "", ""


def ov_product(*texts):
    """The sex toy or sexual-health item a record names (in plain words), or ""."""
    text = " ".join(clean(t) for t in texts if t)
    m = PRODUCT.search(text)
    if m:
        item = re.sub(r"(?<=[a-z])s$", "", m.group(0).lower()) if not m.group(0).lower().endswith("ss") else \
            m.group(0).lower()
        item = re.sub(r"^sex ?toy$", "sex toy", re.sub(r"^butt ?plug$", "butt plug", re.sub(r"^cock ?ring$",
                                                                                          "cock ring", item)))
        return "IUD (intrauterine device)" if item == "iud" else plain(item)
    m = re.search(r"\b(vibrators?|lubricants?|lube)\b", text, re.I)
    if m and PRODUCT_CONTEXT.search(text):
        return re.sub(r"s$", "", m.group(0).lower())
    return ""


def ov_check(item, kind):
    """(reason left out or "", the item named) for one Openverse record in the collection of licence kind ("open" or
    "share-alike"): the site's terms must allow re-use by program, the licence must be of that kind (never NC or
    ND), nothing from an adult site, no sensitive flag, about a sex toy or sexual-health item, NO PERSON in the
    picture by its title, description or any tag (also machine-made tags), no sexual act, fetish or BDSM, and
    screen() with the photo rules."""
    title = clean(item.get("title"))
    given, every = ov_tags(item)
    desc = clean(item.get("description"))
    if clean(item.get("source")).lower() == "flickr":
        return "a Flickr picture (Flickr's terms forbid robots and downloading outside its own API)", ""
    if not ov_site(item):
        return f"a site whose terms for re-use by program were not checked ({clean(item.get('source')) or 'none'})", ""
    lic_kind, _ = ov_licence(item)
    if lic_kind != kind:
        return f"licence not in this collection ({clean(item.get('license')) or 'none'})", ""
    where = " ".join(clean(item.get(k)) for k in ("source", "provider", "foreign_landing_url", "url", "creator",
                                                  "creator_url"))
    if ADULT_SITE.search(where) or ADULT_SITE.search(" ".join(every)):
        return "from a porn or adult site", ""
    if item.get("mature") or item.get("unstable__sensitivity"):
        return "marked as sensitive or mature on Openverse", ""
    product = ov_product(title, desc, " ".join(given))
    if not product:
        return "not about a sex toy or sexual-health item", ""
    if NOT_PRODUCT.search(f"{title} {desc} {' '.join(given)}"):
        return "about a place, sign, machine, advert or artwork rather than the item itself", ""
    without_items = ADULT_PHRASE.sub(" ", PRODUCT.sub(" ", f"{title} {desc}"))
    tag_words = " ".join(ADULT_PHRASE.sub(" ", PRODUCT.sub(" ", t)) for t in every)
    m = OV_PERSON.search(without_items) or OV_PERSON.search(tag_words)
    if m:
        return f"a person may be in the picture ('{m.group(0)}'; consent cannot be checked)", ""
    m = OV_ACT.search(f"{title} {desc} {' '.join(every)}")
    if m:
        return f"a sexual act, porn, fetish or BDSM word ('{m.group(0)}')", ""
    why = screen(title, desc, " ".join(every), photo=True)
    return (why, "") if why else ("", product)


def ov_commons_check(info, title, kind, product_categories):
    """The reason a Wikimedia Commons file found through Openverse is left out, or "": Commons' own licence must be
    of kind, no problem category, not already in the Commons sex-toy or contraception collections (any of its
    categories read by them), no person by its description or categories, and screen() with the photo rules."""
    licence = meta_value(info, "LicenseShortName")
    categories = meta_value(info, "Categories")
    description = english_description(meta_value(info, "ImageDescription"))
    if not info.get("mime", "").startswith("image/") or "gif" in info.get("mime", "") or not info.get("thumburl"):
        return "not a still picture"
    if rs.commons_licence_kind(licence) != kind:
        return f"Commons licence not in this collection ({licence or 'none'})"
    if PROBLEM_CATEGORY.search(categories):
        return "in a deletion, copyright or identity-problem category"
    if {c.strip() for c in categories.split("|")} & set(product_categories):
        return "already in the Commons sex-toy or contraception collections"
    m = OV_PERSON.search(ADULT_PHRASE.sub(" ", PRODUCT.sub(" ", f"{description} {categories}")))
    if m:
        return f"a person may be in the picture ('{m.group(0)}'; consent cannot be checked)"
    m = OV_ACT.search(f"{title} {description} {categories}")
    if m:
        return f"a sexual act, porn, fetish or BDSM word ('{m.group(0)}')"
    return screen(title, description, categories, photo=True)


class Quiet:
    """Stands in for a workspace when only Commons category names are wanted (nothing is recorded)."""

    def leave_out(self, *_args):
        """Nothing to record."""


def commons_product_categories(s):
    """The names of every Commons category the sex-toy and contraception collections read (with sub-categories)."""
    found = set()
    for group in ("sex_toys", "contraception"):
        for category, depth in COMMONS_GROUPS[group]["categories"]:
            found.update(commons_subcats(s, category, depth, Quiet()))
    return found


def ov_draft(site, product, title, description, tags):
    """(draft description, needs a fuller one?) for an Openverse product photo."""
    parts = [f"A product photograph of {a_an(product)[0].lower() + a_an(product)[1:]} from {site}; its record names "
             f"no person in the picture."]
    if title:
        own = "" if is_english(title) else " (in the original language)"
        parts.append(f'Its title{own} is "{plain(title).rstrip(".")}".')
    if description:
        parts.append(f"Its description says: {sentence(rs.first_sentences(plain(description), 60, 2))}")
    if tags:
        parts.append(sentence("Its tags: " + ", ".join(dict.fromkeys(plain(t).lower() for t in tags[:10]))))
    thin = useful_words(title, description, " ".join(tags)) < 5 or not is_english(title)
    if thin:
        parts.append("The record says little more; it was found by a search for sex toys or sexual-health items.")
    return " ".join(parts), thin


def fetch_openverse(key, kind, folder, cap, say):
    """Fill collection key with Openverse product photos of licence kind ("open" or "share-alike") from the sites in
    OV_SITES, keeping to Openverse's rate limits; Commons files are checked again on Commons and those already in
    the Commons sex-toy and contraception collections are left out."""
    source = source_by_key(key)
    ws, s = AdultWorkspace(folder, source, say), rs.session()
    rows, looked, left, calls = [], 0, 0, 0
    for query in OV_QUERIES:
        for page in range(1, OV_PAGES + 1):
            time.sleep(OV_PAUSE)
            calls += 1
            data = rs.get_json(s, OPENVERSE, params={"q": query, "license": OV_LICENCES[kind], "page": page,
                                                     "page_size": 20, "excluded_source": "flickr"})
            results = (data or {}).get("results") or []
            rows += results
            if len(results) < 20 or page >= ((data or {}).get("page_count") or 1):
                break
        if calls > 150:
            say("Openverse: stopping the searches for today (Openverse allows 200 a day without an account).")
            break
    say(f"Openverse: {len(rows)} records found by {calls} searches")
    candidates, commons = [], {}
    seen = set()
    for item in rows:
        landing = clean(item.get("foreign_landing_url"))
        curid = re.search(r"[?&]curid=(\d+)", landing)
        name = f"commons-{curid.group(1)}.jpg" if curid else f"openverse-{clean(item.get('id'))}.jpg"
        if name in seen or ws.done(name):
            continue
        seen.add(name)
        looked += 1
        why, product = ov_check(item, kind)
        if why:
            ws.leave_out(name, item.get("title"), why)
            left += 1
            continue
        if clean(item.get("source")).lower() == "wikimedia":
            if not curid:
                ws.leave_out(name, item.get("title"), "no Commons page id to check the licence on Commons")
                left += 1
                continue
            commons[int(curid.group(1))] = (name, item, product)
        else:
            candidates.append((name, item, product, None))
    if commons:
        product_categories = commons_product_categories(s)
        tops = sum(len(COMMONS_GROUPS[g]["categories"]) for g in ("sex_toys", "contraception"))
        # Only top-level names back means Commons did not answer: no dedupe is possible, so nothing is checked now.
        ids = sorted(commons) if len(product_categories) > tops else []
        for start in range(0, len(ids), 50):
            data = commons_query(s, {"action": "query", "pageids": "|".join(map(str, ids[start:start + 50])),
                                     "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": 1600,
                                     "iiextmetadatafilter": "LicenseShortName|ImageDescription|Artist|Categories|"
                                                            "Credit"}) or {}
            for pid, p in ((data.get("query") or {}).get("pages") or {}).items():
                if not pid.lstrip("-").isdigit() or int(pid) not in commons:
                    continue
                name, item, product = commons.pop(int(pid))
                info = (p.get("imageinfo") or [{}])[0]
                why = ov_commons_check(info, clean(p.get("title", ""))[5:], kind, product_categories)
                if why:
                    ws.leave_out(name, item.get("title"), why)
                    left += 1
                    continue
                candidates.append((name, item, product, (p.get("title", "")[5:], info)))
        for name, item, product in commons.values():   # no answer from Commons (busy): tried again next run
            ws.leave_out("", item.get("title"), "could not be checked on Wikimedia Commons now (tried again next time)")
            left += 1
        if commons:
            say(f"Openverse: {len(commons)} Commons files could not be checked on Commons now; they are tried again "
                "next time.")
    items = []
    for name, item, product, commons_file in candidates:
        given, _every = ov_tags(item)
        title = clean(item.get("title"))
        if commons_file:
            file_title, info = commons_file
            licence = meta_value(info, "LicenseShortName")
            description = english_description(meta_value(info, "ImageDescription"))
            creator = meta_value(info, "Artist") or clean(item.get("creator")) or "unknown"
            url, page, site = info["thumburl"], "https://commons.wikimedia.org/wiki/File:" + file_title.replace(
                " ", "_"), "Wikimedia Commons"
        else:
            licence = ov_licence(item)[1]
            description, creator = "", clean(item.get("creator")) or "unknown"
            url, page, site = clean(item.get("url")), clean(item.get("foreign_landing_url")), ov_site(item)
        text, thin = ov_draft(site, product, title, description if is_english(description) else "", given)
        items.append((name, url, text, f'"{title or "untitled"}" by {creator[:100]}, {site}, {licence}; found with '
                      f"Openverse (not endorsed by Openverse)", licence, page, CONTENT, THIN_NOTE if thin else "",
                      rs.GROUPS[3]))
    say(f"Openverse: {len(items)} usable product photos")
    left += rs.fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


def fetch_openverse_products(folder, cap, say=print):
    """Openverse product photos of sex toys, condoms and sexual-health items with NO PERSON in the picture (CC0,
    public domain or CC BY), from Wikimedia Commons (licence checked again on Commons; files already in the Commons
    sex-toy and contraception collections left out) and open museum and library sites. Flickr is not used."""
    return fetch_openverse("openverse_products", "open", folder, cap, say)


def fetch_openverse_products_sa(folder, cap, say=print):
    """The same as fetch_openverse_products, for CC BY-SA photos."""
    return fetch_openverse("openverse_products_sa", "share-alike", folder, cap, say)


# ----------------------------------------------------------------- the collections

COMMONS_TERMS ="https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia"


def commons_source(key, name, kind, fetch, cap, download):
    """An ADULT_REVIEW_SOURCES entry for a Commons collection of licence kind ("open" or "share-alike")."""
    if kind == "open":
        licence, summary = ("CC0, public domain or CC BY (each file's own licence checked)",
                            "free to use with credit to each author (in CREDITS.txt)")
    else:
        licence, summary = ("CC BY-SA (each file's own licence checked)",
                            "free to use with credit; anything shared that is made from them must be CC BY-SA")
    return dict(key=key, name=name + (" (review only)" if kind == "open" else ", share-alike (review only)"),
                category=kind, licence=licence, terms=COMMONS_TERMS, terms_summary=summary,
                credit=f"Wikimedia Commons authors, {licence.split(' (')[0]}, credited in CREDITS.txt",
                content=CONTENT, cap=cap, download=download, fetch=fetch, review_only=True)


ADULT_REVIEW_SOURCES = [
    dict(key="met_erotic", name="The Met: erotic and nude artworks (review only)", category="open",
         licence="CC0 (Open Access; isPublicDomain checked per object)",
         terms="https://www.metmuseum.org/policies/image-resources",
         terms_summary="public domain, CC0: free for any use; credit The Met",
         credit="The Metropolitan Museum of Art, Open Access, CC0", content=CONTENT, cap=600,
         download="about 120 MB", fetch=fetch_met_erotic, review_only=True),
    dict(key="aic_erotic", name="Art Institute of Chicago: erotic and nude artworks (review only)", category="open",
         licence="CC0 (public-domain works only; is_public_domain checked per object)",
         terms="https://www.artic.edu/open-access/open-access-images",
         terms_summary="public-domain works' pictures under CC0: free for any use", credit="Art Institute of Chicago, "
         "CC0", content=CONTENT, cap=300, download="about 40 MB", fetch=fetch_aic_erotic, review_only=True),
    dict(key="cleveland_erotic", name="Cleveland Museum of Art: erotic and nude artworks (review only)",
         category="open", licence="CC0 (share_license_status checked per object)",
         terms="https://www.clevelandart.org/open-access", terms_summary="CC0: free for any use",
         credit="The Cleveland Museum of Art, Open Access, CC0", content=CONTENT, cap=300, download="about 60 MB",
         fetch=fetch_cleveland_erotic, review_only=True),
    dict(key="rijks_erotic", name="Rijksmuseum: erotic prints and shunga (review only)", category="open",
         licence="Public Domain Mark or CC0 (checked per object)",
         terms="https://data.rijksmuseum.nl/policy/information-and-data-policy",
         terms_summary="public domain: free for any use; credit the Rijksmuseum",
         credit="Rijksmuseum Amsterdam, public domain", content=CONTENT, cap=150, download="about 40 MB",
         fetch=fetch_rijks_erotic, review_only=True),
    dict(key="smithsonian_shunga", name="Smithsonian National Museum of Asian Art: shunga and erotic paintings "
         "(review only)", category="open", licence="CC0 (each picture's usage checked)",
         terms="https://www.si.edu/openaccess", terms_summary="CC0: free for any use; the API needs a free "
         "api.data.gov key (SI_API_KEY)", credit="Smithsonian National Museum of Asian Art (Freer and Sackler), "
         "Open Access, CC0", content=CONTENT, cap=300, download="about 60 MB", fetch=fetch_smithsonian_shunga,
         review_only=True),
    dict(key="wellcome_erotica", name="Wellcome Collection: historical erotica, sexology and contraception "
         "(review only)", category="open", licence="CC BY 4.0, CC0 or public domain (checked per picture)",
         terms="https://wellcomecollection.org/pages/Wvmu3yAAAIUQ4C7F",
         terms_summary="CC BY: free to use with credit to the Wellcome Collection; public domain: free",
         credit="Wellcome Collection, CC BY 4.0 or public domain", content=CONTENT, cap=300,
         download="about 60 MB", fetch=fetch_wellcome_erotica, review_only=True),
    dict(key="europeana_erotic", name="Europeana: erotic prints, drawings and paintings from European museums "
         "(review only)", category="share-alike",
         licence="Public domain, CC0, CC BY or CC BY-SA (each record's rights checked; never NC or ND)",
         terms="https://www.europeana.eu/en/rights",
         terms_summary="free to use with credit; CC BY-SA items: what is shared from them must be CC BY-SA",
         credit="Europeana and its contributing museums, credited in CREDITS.txt", content=CONTENT, cap=400,
         download="about 80 MB", fetch=fetch_europeana_erotic, review_only=True),
    commons_source("commons_erotic_sculpture", "Wikimedia Commons photos of erotic sculpture, frescoes and pottery "
                   "(Khajuraho, Konark, Pompeii)", "open", fetch_commons_erotic_sculpture, 500, "about 100 MB"),
    commons_source("commons_erotic_sculpture_sa", "Wikimedia Commons photos of erotic sculpture, frescoes and "
                   "pottery (Khajuraho, Konark, Pompeii)", "share-alike", fetch_commons_erotic_sculpture_sa, 500,
                   "about 100 MB"),
    commons_source("commons_sex_drawings", "Wikimedia Commons drawings of sex positions, sex education and vintage "
                   "erotic illustrations", "open", fetch_commons_sex_drawings, 500, "about 60 MB"),
    commons_source("commons_sex_drawings_sa", "Wikimedia Commons drawings of sex positions, sex education and "
                   "vintage erotic illustrations", "share-alike", fetch_commons_sex_drawings_sa, 500, "about 60 MB"),
    commons_source("commons_sex_photos", "Wikimedia Commons photographs of adult sexual activity", "open",
                   fetch_commons_sex_photos, 300, "about 60 MB"),
    commons_source("commons_sex_photos_sa", "Wikimedia Commons photographs of adult sexual activity", "share-alike",
                   fetch_commons_sex_photos_sa, 300, "about 60 MB"),
    commons_source("commons_inclusive", "Wikimedia Commons LGBTQ+, interracial, pregnancy, safer-sex and disability "
                   "sexuality pictures", "open", fetch_commons_inclusive, 300, "about 50 MB"),
    commons_source("commons_inclusive_sa", "Wikimedia Commons LGBTQ+, interracial, pregnancy, safer-sex and "
                   "disability sexuality pictures", "share-alike", fetch_commons_inclusive_sa, 300, "about 50 MB"),
    commons_source("commons_sex_toys", "Wikimedia Commons product photos of sex toys", "open",
                   fetch_commons_sex_toys, 400, "about 60 MB"),
    commons_source("commons_sex_toys_sa", "Wikimedia Commons product photos of sex toys", "share-alike",
                   fetch_commons_sex_toys_sa, 400, "about 60 MB"),
    commons_source("commons_contraception", "Wikimedia Commons photos of condoms, contraceptives and sexual-health "
                   "items", "open", fetch_commons_contraception, 400, "about 60 MB"),
    commons_source("commons_contraception_sa", "Wikimedia Commons photos of condoms, contraceptives and "
                   "sexual-health items", "share-alike", fetch_commons_contraception_sa, 400, "about 60 MB"),
    dict(key="commons_vintage_named", name="Wikimedia Commons vintage pin-up, burlesque and art-nude photographs of "
         "named, provably adult people (review only)", category="open",
         licence="Public domain (taken in 1930 or earlier), CC0 or CC BY (each file's licence and date checked)",
         terms=COMMONS_TERMS, terms_summary="public domain or free to use with credit (in CREDITS.txt)",
         credit="Wikimedia Commons; ages from Wikidata birth dates; name, birth year and photo year in CREDITS.txt",
         content=CONTENT, cap=200, download="about 30 MB", fetch=fetch_commons_vintage_named, review_only=True),
    dict(key="us_patent_drawings", name="US patent drawings of sex toys, erection aids, condoms and menstrual cups "
         "(review only)", category="open", licence=PATENT_LICENCE, terms=PATENT_TERMS,
         terms_summary="public domain: free for any use; credit each patent (number, title, inventor, year). Needs a "
         f"free USPTO Open Data Portal API key in the {USPTO_KEY_ENV} environment variable",
         credit="United States Patent and Trademark Office (Open Data Portal); each patent's number, title, inventor "
         "and year in CREDITS.txt", content=CONTENT, cap=1500, download="about 400 MB",
         fetch=fetch_us_patent_drawings, review_only=True),
    dict(key="openverse_products", name="Openverse product photos of sex toys, condoms and sexual-health items, no "
         "person in the picture (review only)", category="open",
         licence="CC0, public domain or CC BY (each picture's licence checked; Commons files on Commons itself)",
         terms=OPENVERSE_TERMS, terms_summary="free to use with credit to each author (in CREDITS.txt); made with "
         "Openverse, not endorsed by Openverse; Openverse's rate limits kept",
         credit="Wikimedia Commons, museum and library authors found with Openverse (not endorsed by Openverse), "
         "credited in CREDITS.txt", content=CONTENT, cap=300, download="about 40 MB",
         fetch=fetch_openverse_products, review_only=True),
    dict(key="openverse_products_sa", name="Openverse product photos of sex toys, condoms and sexual-health items, no "
         "person in the picture, share-alike (review only)", category="share-alike",
         licence="CC BY-SA (each picture's licence checked; Commons files on Commons itself)",
         terms=OPENVERSE_TERMS, terms_summary="free to use with credit; anything shared that is made from them must "
         "be CC BY-SA; made with Openverse, not endorsed by Openverse",
         credit="Wikimedia Commons, museum and library authors found with Openverse (not endorsed by Openverse), "
         "credited in CREDITS.txt", content=CONTENT, cap=300, download="about 40 MB",
         fetch=fetch_openverse_products_sa, review_only=True),
]


def source_by_key(key):
    """The ADULT_REVIEW_SOURCES entry with this key."""
    return next(s for s in ADULT_REVIEW_SOURCES if s["key"] == key)


# Sources looked at (November 2026) and not included, with the reason.
NOT_INCLUDED = {
    "National Gallery of Art (api.nga.gov)": "not added: the API answered with a Cloudflare check page from the build "
        "machine (November 2026). Its open data (github.com/NationalGalleryOfArt/opendata, CC0) has no subject "
        "tags, so erotic works could only be found by title; it can be added later.",
    "Japan Search (jpsearch.go.jp), keyword 春画 (shunga)": "not added: only about 94 records with open terms (CC0 39 "
        "public domain mark, 10 CC BY, 37 CC BY-SA, 8 CC0); the rest are non-commercial, no-derivatives or "
        "unassessed. Many matches are false (an artist's name containing the characters), records are in Japanese "
        "only, and items are whole books whose first picture is the cover. The Met, Rijksmuseum, Art Institute and "
        "Smithsonian collections give single shunga sheets with English records instead.",
    "Library of Congress (loc.gov)": "not added: 'erotic' finds 31 items and 'shunga' 3; most are photographs of "
        "unnamed women described as 'young' (left out by the rules), sound recordings or non-sexual items, and the "
        "few prints have no rights field in the search answer. Too few usable pictures for a collection.",
    "Smithsonian (api.si.edu) without a key": "sign-up: the API needs a free api.data.gov key; the shared DEMO_KEY "
        "allows only a few requests an hour. smithsonian_shunga reads SI_API_KEY.",
    "Europeana with its own key": "sign-up (free) for heavy use; the public demonstration key 'api2demo' works for "
        "this collection's size. europeana_erotic reads EUROPEANA_KEY.",
    "OpenStax and other open sex-education textbooks": "OpenStax Anatomy and Physiology and Biology have "
        "reproductive anatomy figures (already in the kit's 'anatomy' pack) but no drawings of sexual activity or "
        "positions; not duplicated. Commons' sex-education category is read by commons_sex_drawings.",
    "Government sexual-health sites (CDC, NHS, HHS)": "their condom and contraception pictures are mostly stock "
        "photographs (not public domain); public-domain CDC PHIL items are in review_sources.cdc_phil_intimate. "
        "Commons' condom and contraception categories are used instead.",
    "Anonymous vintage erotic photographs (museums, libraries, Commons, Wellcome, Europeana)": "never used: age and "
        "consent cannot be checked, and many historical erotic photographs show minors or people photographed "
        "without real consent. Only named people with a provable adult age (commons_vintage_named).",
    "Commons photographs of people that are not the uploader's own work (Flickr and other imports)": "left out of "
        "commons_sex_photos: the person's consent cannot be checked from the file page.",
    "Porn sites, scraped web sets (LAION and the like), Reddit, Tumblr, forums, unknown-provenance sets":
        "never used.",
    "BDSM, bondage and fetish categories": "left out: restraint and pain cannot be told apart from violence in a "
        "picture, and consent cannot be checked.",
    "Commons 'Sex in public', 'Outdoor sex', 'Dogging', 'Voyeurism' and 'Glory holes' categories": "left out: "
        "bystanders or the people shown may not have agreed.",
    # Academic adult and NSFW datasets: none documents performer consent or age records.
    "NPDI Pornography-800 and Pornography-2k (Avila et al., Moreira et al.)": "excluded: videos collected from "
        "pornography websites (and YouTube for the non-porn part); no performer consent or age records.",
    "LSPD, Large-Scale Pornographic Dataset (2022)": "excluded: pictures and videos collected from the web; no "
        "consent or age records.",
    "'Adult Content Dataset' and similar Kaggle or GitHub NSFW sets": "excluded: scraped from porn sites and the "
        "web; no consent or age records.",
    "NSFW Data Scraper (alex000kim) and NudeNet's training data": "excluded: scrapers of Reddit and other sites; "
        "no consent or age records.",
    "Yahoo open_nsfw": "excluded: a model only, no data (and trained on unpublished web data).",
    # Producers and platforms: no openly licensed, consent-documented release found.
    "Ethical or feminist producers with Creative Commons releases": "none found with a clear open licence AND "
        "documented performer consent and age records (November 2026). Their catalogues can only be licensed by "
        "contract: see CONTRACT_CANDIDATES.",
    "Flickr 'restricted' photos under CC licences": "excluded: the Flickr API shows restricted photos only to a "
        "signed-in adult account with safe search off (sign-up), and nothing on a photo page proves the uploader "
        "is the person shown, their age or their consent; limiting to models' own accounts cannot be done "
        "reliably by a program. Commons photos that came from Flickr are left out of the photograph collections "
        "for the same reason.",
    # Archives.
    "The Kinsey Institute (Indiana University)": "restricted: the collections are seen by appointment by "
        "researchers; pictures are not openly licensed. Can be asked about by letter.",
    "Schwules Museum Berlin": "not open: its online collection is shown without an open licence; any items it "
        "gave to Europeana with open rights are read by europeana_erotic.",
    "Wellcome Collection sexology and erotica": "included (wellcome_erotica, CC BY or public domain).",
    # Instructional sexuality material (terms as generally published; check again before any agreement).
    "AMAZE (amaze.org) sex-education videos": "not open: free to watch and share as they are, but no open "
        "licence for copying frames into training (contract candidate).",
    "Scarleteen (scarleteen.com)": "not open: all rights reserved (contract candidate).",
    "OMGYes, Kenneth Play, Betty Dodson Foundation, Beducated": "not open: paid or copyrighted teaching material "
        "(contract candidates).",
    "Positions for people with limited mobility (how-to diagrams)": "no openly licensed set found; a gap. Disability "
        "charities' guides are copyrighted (contract candidates).",
    # Inclusive sexuality.
    "Sexual Health and Disability Alliance (SHADA), Love Lives and Disability, Enhance the UK 'Undressing "
    "Disability', Planned Parenthood disability resources": "not open: copyrighted text and photographs "
        "(contract candidates).",
    "NHS and other Crown material": "the Open Government Licence covers Crown text, but NHS website pictures are "
        "mostly licensed stock photographs: not included.",
    "CDC, Australian and Canadian health departments' LGBTQ+ sexual-health pictures": "mostly stock photographs or "
        "third-party pictures excluded from their open licences; CDC public-domain items are in the CDC PHIL "
        "collection of review_sources.py. Not included here.",
    "Open photographs of disabled people's or older adults' sexuality": "a GAP: none found on Commons or in any "
        "open source (Commons has no category for older adults' sexuality and one file under 'Disability and "
        "sexuality', read by commons_inclusive).",
    # Patents, product photos and sex-education catalogues (looked at November 2026).
    "PatentsView API (search.patentsview.org)": "not used: paused on 20 March 2026 while PatentsView moves into the "
        "USPTO Open Data Portal; us_patent_drawings uses the Open Data Portal instead.",
    "Google Patents (patents.google.com, patentimages.storage.googleapis.com)": "not used: robots.txt allows "
        "only the single patent pages (search is disallowed), the picture store has no robots.txt or terms, and "
        "Google's terms forbid scraping content that does not belong to the user; no clear permission for "
        "automated downloading. The USPTO's own Open Data Portal is used instead.",
    "USPTO Patent Public Search (ppubs.uspto.gov) and bulk full-text-with-images files": "not used for collecting: "
        "the USPTO's terms say its online databases are not meant for bulk downloads (automated heavy use may be "
        "blocked), and the weekly bulk files with images are many gigabytes. The Open Data Portal API is the "
        "USPTO's channel for automated use.",
    "US patents filed before 2001": "a gap: the Open Data Portal's file-wrapper data starts with applications "
        "filed in 2001, so older sex-toy and condom patents (old US classes 600/38-41) are not reached.",
    "US design patents (drawings only)": "not added yet: they carry no CPC class for these devices and no figure "
        "text beyond the view names; can be added later.",
    "Flickr pictures found with Openverse": "not downloaded: almost all of Openverse's sex-toy and condom photos are "
        "on Flickr, and Flickr's terms forbid robots, scraping and downloading outside its own API (which needs an "
        "account and key). Openverse's terms ask users to respect the hosting site's terms. A Flickr API key "
        "could be considered later; photos with people would still be left out (consent cannot be checked).",
    "Openverse sites other than Wikimedia Commons and open museums and libraries": "not used: their terms for "
        "re-use by program were not checked (stock sites such as Rawpixel limit downloading).",
    "MedlinePlus and A.D.A.M. medical illustrations (NIH)": "not open: the pictures are licensed from A.D.A.M., "
        "Inc. and are copyrighted, although MedlinePlus is a US government site.",
    "CDC condom and contraception how-to pictures (cdc.gov)": "not added: the pages mix public-domain CDC "
        "drawings with licensed stock photographs and say third-party pictures need permission; picture-by-picture "
        "provenance is not given. CDC PHIL (clearly public domain) is used in review_sources.cdc_phil_intimate.",
    "FDA birth control chart and HHS Office of Population Affairs contraception pages": "not added: mostly text "
        "and licensed stock pictures; no clearly public-domain set of product drawings found.",
    "Open textbooks on human sexuality (Lumen Learning, LibreTexts, OpenStax Psychology)": "not added: their "
        "figures are mixed: Commons and Flickr pictures, stock photos and all-rights-reserved items under one book "
        "licence, so each picture's own provenance is not clear. OpenStax anatomy figures are in the 'anatomy' "
        "pack; Commons pictures are read directly by the Commons collections here.",
    "Sex-position catalogues and sex-toy guides by publishers and retailers (Kama Sutra books with modern "
    "illustrations, Lovehoney, Adam & Eve, Good Vibrations, Babeland, Cosmopolitan and similar)": "not open: "
        "copyrighted catalogues and product photos (retailers' sites also forbid scraping). Old public-domain "
        "Kama Sutra illustrations on Commons are read by commons_sex_drawings.",
    "Makers' own manuals and product pictures for a sex toy the owner has": "not a collection here: the toolkit's "
        "Manuals lookup can fetch a maker's manual for the owner's personal use.",
}

# Companies and bodies whose catalogues could be licensed by contract (nothing is downloaded from them). Any
# agreement should give: written performer consent to this use, age records (US 18 U.S.C. 2257 or the local
# equivalent), permission to train a private description model, and no picture-making or publication.
CONTRACT_CANDIDATES = [
    "Lust Cinema / XConfessions (Erika Lust)", "Bellesa", "CrashPad Series (Pink and White Productions)",
    "Four Chambers (Vex Ashley)", "FrolicMe", "Joymii", "Comstock Films", "Make Love Not Porn (if still operating)",
    "OMGYes", "Kenneth Play", "Betty Dodson Foundation", "Beducated", "AMAZE", "Scarleteen",
    "Sexual Health and Disability Alliance", "Love Lives and Disability", "Enhance the UK (Undressing Disability)",
    "Planned Parenthood", "The Kinsey Institute",
    # Product catalogues (photos of sex toys with no person): makers and retailers.
    "Lovehoney", "Adam & Eve", "Good Vibrations", "Babeland", "We-Vibe and Womanizer (WOW Tech)", "LELO",
    "Dame Products", "Fun Factory", "Durex and Trojan (condom makers)",
]


def main(argv):
    """Quick test: python adult_review_sources.py <key> <folder> [cap]. Prints only titles, licences and drafts."""
    if len(argv) < 3:
        print("python adult_review_sources.py <key> <folder> [cap]\nkeys: "
              + ", ".join(s["key"] for s in ADULT_REVIEW_SOURCES))
        return 1
    source = source_by_key(argv[1])
    source["fetch"](argv[2], int(argv[3]) if len(argv) > 3 else 5, print)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
