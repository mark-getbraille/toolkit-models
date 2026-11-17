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

Only requests and Pillow are needed (as for the rest of the kit). Nothing is sent anywhere except the downloads.
"""

import html
import json
import os
import re
import shutil
import time

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
    r"verkracht\w*|ontvoer\w*|geweld\w*|viol|enlèvement|vergewaltig\w*|stupro|violación|seduc\w*)\b", re.I)

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
    r"sheep|rabbits?|hares?|birds?|cocks? and hens?|hens?|deer|stags?|hond\w*|paard\w*|dier\w*)\b", re.I)

# Photo-only words: youthful or doubtful wording and Commons problem categories.
PHOTO_DOUBT = re.compile(
    r"\b(teen\w*|girls?|boys?|young\w*|school\w*|uniform\w*|college|coed\w*|amateur porn|porn\w*|xxx|onlyfans|"
    r"camgirl\w*|webcam\w*|sex tape|leak\w*|ex-?girlfriend|ex-?boyfriend|hidden|candid|creepshot\w*|"
    r"stolen|scraped|reddit|tumblr|imgur|xhamster|pornhub|xvideos|redtube|youporn|motherless)\b", re.I)
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
        return True
    return sum(w in ENGLISH_WORDS for w in words) / len(words) >= 0.12


def useful_words(*texts):
    """How many words of the texts say something about the picture (catalogue words not counted)."""
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", " ".join(clean(t) for t in texts if t))
    return len([w for w in words if w.lower() not in STOP and len(w) > 2])


def screen(*texts, photo=False):
    """"" when the texts may be used; otherwise the reason they are left out (adults only, consent, no violence, no
    animals; photo=True adds the photo rules: no youthful or doubtful wording)."""
    text = " ".join(clean(t) for t in texts if t)
    no_art_school = ART_SCHOOL.sub(" ", text)
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
        parts.insert(1, sentence(generic))
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
                               generic="It is an erotic or nude artwork showing adults")
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
                                   generic="It is an erotic or nude artwork showing adults")
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
                                       generic="It is an erotic or nude artwork showing adults")
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
                               generic="It is an erotic artwork showing adults")
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
                name, title = f"si-{re.sub(r'[^\\w.-]', '_', x.get('url', x.get('id', '')))}.jpg", clean(x.get("title"))
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
                                       generic="It is an erotic artwork showing adults")
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
                                       generic="It is an erotic or sexual-health picture showing adults",
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
                                       generic="It is an erotic artwork showing adults")
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
        generic="It shows an erotic artwork of adults"),
    "sex_drawings": dict(
        categories=[("Sex positions", 2), ("Human sexual activity diagrams", 1), ("Sex education", 1),
                    ("Kama Sutra", 1), ("I modi - nine fragments - Agostino Veneziano", 0),
                    ("Erotic prints in the Metropolitan Museum of Art", 1), ("Erotic engravings", 1),
                    ("Erotic illustrations", 1), ("Erotic drawings", 1), ("People having sex in art", 1),
                    ("Erotic paintings", 1)],
        lead="A drawing, print or painting", people_photo=False, drawings_only=True,
        generic="It is a drawing of adults having sex or being intimate"),
    "sex_photos": dict(
        categories=[("Human sexual activity", 2), ("Nude couples", 1)],
        lead="A photograph of adults", people_photo=True, photos_only=True, own_work=True,
        generic="It is a photograph of adults having sex or being intimate"),
    "inclusive": dict(
        categories=[("LGBT sex", 2), ("Gay sex", 1), ("Lesbian sex", 1), ("Transgender sexuality", 1),
                    ("Interracial sex", 1), ("Sexual activity during pregnancy", 0), ("Gay erotic art", 1),
                    ("Lesbian erotic art", 1), ("Bisexual erotic art", 1), ("Safer sex", 1),
                    ("Disability and sexuality", 1)],
        lead="A picture of adults", people_photo=True, own_work=True,
        generic="It is a picture of adults being intimate or having sex"),
    "sex_toys": dict(
        categories=[("Sex toys", 1), ("Dildos", 1), ("Vibrators", 1), ("Butt plugs", 1), ("Anal beads", 1),
                    ("Cock rings", 1), ("Sex dolls", 0), ("Personal lubricants", 1)],
        lead="A product photograph of a sex toy", people_photo=True,
        generic="It is a photograph of a sex toy"),
    "contraception": dict(
        categories=[("Condoms", 1), ("Female condoms", 1), ("Male condoms", 1), ("Contraceptive pills", 1),
                    ("Contraceptive devices", 1), ("Intrauterine devices", 1), ("Contraceptive implants", 1),
                    ("Contraceptive injections", 0), ("Dental dams", 1), ("Latex dental dams", 0),
                    ("Emergency contraception", 1), ("Vaginal rings", 0), ("Spermicides", 1), ("Safer sex", 0)],
        lead="A photograph of a sexual-health item", people_photo=True,
        generic="It is a photograph of a condom, contraceptive or other sexual-health item"),
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


def english_description(description):
    """The English part of a Commons description (Commons often gives several languages)."""
    m = re.search(r"(?:^|\s)(?:English|en)[:\s]+(.+?)(?=\s(?:Deutsch|Français|Español|Italiano|Nederlands|Polski|"
                  r"Português|Русский|日本語|中文|de|fr|es|it|nl|pl|pt|ru|ja|zh)[:\s]|$)", description)
    return clean(m.group(1)) if m else clean(description)


def commons_check(ws, group, pageid, title, info):
    """(draft, credit, licence, page, note) for a usable Commons file of a group, or None (recorded as left out)."""
    name = f"commons-{pageid}.jpg"
    description = english_description(meta_value(info, "ImageDescription"))
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
    elif re.search(r"\b(logos?|icons?|wordmarks?|pictograms?|emblems?|flags?|maps?|charts?|graphs?)\b", text, re.I):
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
    parts = [lead, sentence(g["generic"]) if thin else "",
             f"Its description says: {sentence(caption)}" if caption else ""]
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
            if sum(len(x) for x in lists) > cap * 2 + 10:
                break
        if sum(len(x) for x in lists) > cap * 2 + 10:
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
            "It is a pin-up, burlesque or art-nude photograph of an adult." if thin else "",
            f"Its description says: {sentence(caption)}"] if p)
        details = "; ".join(f"name: {n}; birth year: {b}; photo year: {year}" for n, b, _bd in found)
        items.append((name, info["thumburl"], text, f"{stem} by {(meta_value(info, 'Artist') or 'unknown')[:100]}, "
                      f"via Wikimedia Commons; shows {who}", licence,
                      "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_"), CONTENT,
                      (THIN_NOTE + " " if thin else "") + f"Adulthood from Wikidata birth year and photo date: {who}.",
                      details))
    say(f"Commons vintage named photographs: {len(items)} usable files")
    left += rs.fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- the collections

COMMONS_TERMS = "https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia"


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
