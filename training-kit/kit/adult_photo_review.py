"""DOCUMENTED ADULTS ONLY: photographs of nudity and of adult sexual acts from institution catalogues, gathered on the
owner's own computer (never in CI, never published), for a private picture describer used by a blind adult.

Why: the open packs (packs/adult_art_packs.py) hold ART only; photographs of nudity or sex are left out there because
an anonymous photograph's people cannot be shown to be adults. This module takes a photograph ONLY when the
institution's own record DOCUMENTS that every person in it is an adult, before anything is downloaded or shown:

  THE GATE (documented(), run on the record's words before any picture is fetched)
  1. It must be a PHOTOGRAPH (not an artwork: art is for adult_art_packs.py) showing nudity or sex (TOPIC).
  2. Hard screen, adult_review_sources.screen(photo=True): ANY word that names or may name a child or young person
     (child, boy, girl, infant, baby, minor, teen, adolescent, juvenile, school, pupil, young, youth, maiden,
     youthful, little, petite, virgin, son, daughter ...), any age under 18, violence or no consent (sleep,
     drunkenness, voyeurs, hidden cameras, leaks, force, bondage ...), the myths about rape or a minor, animals, and
     doubtful photo words (amateur, candid, porn sites ...). Such a record is LEFT OUT ENTIRELY: not listed, not
     shown, not downloaded; only the NUMBER left out for each reason goes in the log (search-log.txt).
  3. Adulthood DOCUMENTED in the record, one of:
       a) the record STATES the people are adults ("adult models", "consenting adults", "the models were over
          18" ...: STATED_ADULTS), with no word that takes it back; or
       b) every person the record NAMES carries a birth year (a heading such as "Doe, Jane, 1890-1960"), every one
          of them was 18 or over at the photo's EARLIEST possible date (19 years apart, or 18 with the exact dates:
          proven_adult), every name in the record has a birth year, and the record names as many proven adults as
          it implies people: two or more for a couple, lovers or any sexual act, one for a single nude. A record that
          says "unidentified", "unknown", "anonymous", "others", "group" and the like is left out.
     Anonymous records are left out. Residual risk, said plainly: a catalogue can be wrong (a wrong date, or a name
     that is the photographer's rather than the sitter's); the reviewer window is there for a second look.
  3b. NON-SEXUAL NUDE STUDIES (the owner's decision): a nude photograph with nothing sexual in its record may
     instead DESCRIBE AN ADULT ("a woman", "a man", "a young woman", "an adult", "a male model": ADULT_CUE) and
     name no group, family or class (PEOPLE_UNKNOWN). Only personal-use ones are taken here; open ones are the
     open pack nude_photo_studies (packs/adult_art_packs.py, built in CI).
  4. Licence: the record's own rights statement decides the GROUP, "open" (public domain, CC0, CC BY, "No known
     restrictions on publication") or "personal use only" (anything else). Personal-use pictures go into a workspace
     whose "review_category" is "noncommercial", so training uses them only with the personal-use choice.

  WHAT HAPPENS TO A DOCUMENTED RECORD (the owner's decision): it is APPROVED AUTOMATICALLY and downloaded into a
  "Describe pictures" workspace under <review folder>/approved/<content>-<group> (content "sexual" or "nudity";
  describing.json "review_only", "documented_adults", "never_for_picture_making", "never_publish" and
  "needs_explicit_choice" true), marked "checked" with "adult_approved_by": "documented adult (<reason>)", its
  description written from the record's own words. It is logged in decisions.csv as "approved: documented adult
  (<reason>)" and listed in review-list.csv (title, institution, catalogue text, rights, group, page, picture
  address, reason, file, status). own_data.py uses a picture of such a workspace ONLY when its entry has
  adult_approved_by and it is still "checked"; training with any of it is personal use only (review pictures),
  needs the matching content choice (--with-sexual and --with-nudity), and is never used for picture-making.
  The reviewer window (training-kit/wizard/adult_photo_window.py) gives an optional second look: Reject (or Unsure,
  which counts as Reject) DELETES the picture and its description, removes it from the workspace and adds its id to
  blocked.txt, so it is never fetched again.

Sources (official APIs only, paced): the Library of Congress (loc.gov JSON API, its robots.txt Crawl-Delay of 5
seconds kept), the Wellcome Collection (catalogue API). The Smithsonian needs an api.data.gov key and is not read
yet. Nothing is sent anywhere except these searches and downloads.

    python adult_photo_review.py search "<review folder>" [most]     (search, check and download documented items)
    python adult_photo_review.py list "<review folder>"              (say what is approved)
"""

import csv
import datetime
import io
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import adult_review_sources as ars  # noqa: E402 - the kit's adults-only word screens
import describe_package as dp  # noqa: E402

KEY = "adult_photo_review"
USER_AGENT = "PictureModelTrainingKit/2"
DEFAULT_FOLDER = os.path.join("B:\\", "Picture Library", "Review", "Documented adult photographs")
REVIEW_LIST = "review-list.csv"
DECISIONS = "decisions.csv"
BLOCKED = "blocked.txt"
SEARCH_LOG = "search-log.txt"
APPROVED = "approved"
LIST_COLUMNS = ("id", "title", "institution", "catalogue_text", "rights", "group", "page_url", "image_url",
                "reason", "content", "file", "status")
LOC_PAUSE = 5.0                    # loc.gov robots.txt: Crawl-Delay 5
WELLCOME_PAUSE = 0.5
OPEN, PERSONAL = "open", "personal use only"


def clean(text):
    """Text with its spaces tidied and HTML removed ("" for nothing)."""
    return ars.clean(text if isinstance(text, str) else " ".join(map(str, text)) if isinstance(text, list) else
                     str(text or ""))


def now():
    """The time now, as written in the logs."""
    return datetime.datetime.now().isoformat(timespec="seconds")


# ----------------------------------------------------------------- the gate

PHOTO = ars.PHOTO_WORDS
NOT_PHOTO = re.compile(r"\b(engraving|etching|lithograph\w*|woodcut|drawing|painting|watercolou?r|sculpture|"
                       r"cartoon|poster|illustration|screen ?print|silkscreen)\b", re.I)
NUDE = re.compile(r"\b(nude\w*|naked|nudity|unclothed|undressed|topless|bare-breasted)\b", re.I)
SEX = re.compile(r"\b(sex|sexual (intercourse|acts?|activity|positions?)|intercourse|coitus|copulat\w*|"
                 r"love-?making|making love|fellatio|cunnilingus|masturbat\w*|erotic\w*|erotica)\b", re.I)
STATED_ADULTS = re.compile(
    r"\b(adult (models?|volunteers?|participants?|actors?|actresses|performers?|subjects?|couples?|men and women|"
    r"women and men)|consenting adults?|(models?|participants?|volunteers?|performers?|subjects?|sitters?|"
    r"people|persons) (were|are|was|is) (all )?(adults?|over (the age of )?(18|eighteen|21|twenty-one)|"
    r"aged (1[89]|[2-9]\d)( or over| and over)?))\b", re.I)
TAKEN_BACK = re.compile(r"\b(not|no longer|un(?:verified|known|confirmed)|may not be|possibly|probably|presumed|"
                        r"believed to be|said to be|claimed)\b[^.]{0,30}\badult", re.I)
SEVERAL = re.compile(r"\b(couples?|lovers|two|pair|partners?|men and women|women and men|man and (a )?woman|"
                     r"woman and (a )?man|women|men|sex|sexual|intercourse|coitus|copulat\w*|love-?making|"
                     r"making love|fellatio|cunnilingus)\b", re.I)
UNNAMED = re.compile(r"\b(unidentified|unknown|anonymous|unnamed|others?|group|groups|crowd|several|three|four|"
                     r"various|models?\b(?! (were|are|was|is)))", re.I)
# A personal name heading with a birth year: "Doe, Jane, 1890-1960", "Doe, Jane, 1890-", "Doe, Jane (1890-1960)".
NAMED = re.compile(r"^\s*([^,()\d]+,[^,()\d]+?)[,\s(]+(?:b\.\s*)?(1[6-9]\d\d|20[0-2]\d)\s*-\s*(\d{4})?\)?")
# A heading that is a personal name WITHOUT dates (a person the record names but whose age cannot be proven).
NAME_ONLY = re.compile(r"^\s*[A-Z][\w'.-]+, [A-Z][\w'.-]+(?: [A-Z][\w'.-]+)*\s*$")
YEARS = re.compile(r"\b(1[6-9]\d\d|20[0-2]\d)\b")


def proven_adult(birth_year, birth_date, year, date):
    """True when a person born in birth_year was 18 or over in year: 19 years apart, or 18 apart with both exact
    dates showing the 18th birthday had passed (adult_review_sources.proven_adult)."""
    return ars.proven_adult(birth_year, birth_date, year, date)


def earliest_year(*dates):
    """The earliest year any of the record's dates allows (an uncertain "1920-1930" or "ca. 1925" counts as its
    earliest year), or 0 when the record gives none."""
    years = [int(y) for d in dates for y in YEARS.findall(clean(d))]
    return min(years) if years else 0


def licence_group(rights):
    """"open" when a rights statement is public domain, CC0, CC BY (not NC or ND) or "no known restrictions";
    otherwise "personal use only" (the personal-use labelling of the kit)."""
    text = clean(rights).lower()
    if re.search(r"\b(nc|nd|non-?commercial|no-?deriv\w*|all rights reserved|in copyright|inc)\b", text):
        return PERSONAL
    if re.search(r"public ?domain|\bpdm\b|\bcc0\b|cc-0|creative commons zero|no known (copyright )?restrictions|"
                 r"\bcc[ -]?by\b|cc-by", text):
        return OPEN
    return PERSONAL


# NON-SEXUAL NUDE STUDIES (the owner's decision, November 2026): a nude photograph with nothing sexual in its record
# (a studio, art-school, medical or anthropometric study) needs no documented age, but its record must DESCRIBE AN
# ADULT (ADULT_CUE), name no group, family or class (PEOPLE_UNKNOWN) and no young person ("young woman" and "young
# man" are allowed). Open ones are the open pack packs/adult_art_packs.py nude_photo_studies (built in CI); this
# builder takes the personal-use ones. The words are the same as that pack's (a test compares them).
ADULT_CUE = re.compile(r"\b(wom[ae]n|m[ae]n|lad(y|ies)|gentlem[ae]n|adults?|adult (male|female)|(male|female) "
                       r"models?|artist'?s models?|athletes?|wrestlers?|strong ?m[ae]n|bodybuilders?|soldiers?|"
                       r"sailors?|dancers?|wi(fe|ves)|husbands?|elderly|old (wom[ae]n|m[ae]n))\b", re.I)
PEOPLE_UNKNOWN = re.compile(r"\b(group|groups|crowd|several|people|famil(y|ies)|tribe\w*|villagers?|class|"
                            r"classes|series of (wom[ae]n|m[ae]n|people|figures)|population|mothers?|fathers?|"
                            r"parents?|siblings?|brothers?|sisters?|growth|development|puberty|tanner)\b", re.I)
YOUNG_ADULT = re.compile(r"\byoung (wom[ae]n|m[ae]n)\b", re.I)
STUDY_CATEGORY = "a non-sexual nude study with open rights (in the nude_photo_studies pack instead)"
# The owner's adjustment: in 1800s and 1900s captions "girl(s)", "boy(s)", "lad" and "lass" often mean young adults.
# A SEXUAL photograph whose ONLY young-person words are these is listed by its link in the "Ask the institution
# first" section, and is approved only with the institution's documentation that every person was 18 or over
# (AGE_EVIDENCE: an age, a birth date or year, or the word adult). Every other minor word still leaves it out.
GIRL_BOY = re.compile(r"\b(girls?|boys?|lads?|lass(ie)?s?)\b", re.I)
ASK_FIRST = "only girl, boy, lad or lass named: ask the institution first"
AGE_EVIDENCE = re.compile(r"\b(18|eighteen|(1[89]|[2-9]\d) ?(years?|yrs?)|aged (1[89]|[2-9]\d)|adults?|born|"
                          r"dates? of birth|birth ?dates?|(1[6-9]|20)\d\d)\b", re.I)


def documented(texts, names=(), dates=(), kind_texts=(), rights=""):
    """(reason, content) when a record may be taken: reason says how adulthood is documented (or that it is a
    non-sexual nude study describing an adult, for personal-use rights); content is "sexual" or "nudity".
    Otherwise ("", why) where why is one of the counted CATEGORIES (the record itself is never said). texts: the
    record's words; names: its personal-name headings; dates: its dates; kind_texts: its format words; rights: its
    rights statement."""
    text = " ".join(clean(t) for t in texts if t)
    kind = " ".join(clean(t) for t in kind_texts if t)
    if not PHOTO.search(f"{kind} {text}") or NOT_PHOTO.search(kind):
        return "", "not a photograph"
    if not (NUDE.search(text) or SEX.search(text)):
        return "", "not about nudity or sex"
    content = "sexual" if SEX.search(text) else "nudity"
    # "young woman" and "young man" are allowed in a non-sexual nude photograph's record only.
    screened = YOUNG_ADULT.sub(" ", text) if content == "nudity" else text
    why = ars.screen(screened, " ".join(clean(n) for n in names), photo=True)
    if why and content == "sexual" and GIRL_BOY.search(screened) and \
            not ars.screen(GIRL_BOY.sub(" ", screened), " ".join(clean(n) for n in names), photo=True):
        return "", ASK_FIRST                      # only girl(s), boy(s), lad or lass: ask the institution first
    if why:
        return "", ("a child or young person, or an age under 18" if "young person" in why or "under 18" in why else
                    "violence, no consent, a myth, an animal or doubtful photo wording")
    if STATED_ADULTS.search(text) and not TAKEN_BACK.search(text):
        return f"the record states: {STATED_ADULTS.search(text).group(0)}", content
    if content == "nudity" and not names:
        if PEOPLE_UNKNOWN.search(text) or UNNAMED.search(text):
            return "", "not every person is documented"
        cue = ADULT_CUE.search(text)
        if not cue:
            return "", "adulthood not documented (anonymous, or a birth or photo date missing or under 18)"
        if licence_group(rights) == OPEN:
            return "", STUDY_CATEGORY
        return f"a non-sexual nude study; the record describes an adult (\"{cue.group(0)}\")", content
    if UNNAMED.search(text):
        return "", "not every person is documented"
    year = earliest_year(*dates)
    proven, unproven = [], 0
    for name in names:
        name = clean(name).split("--")[0]          # "Doe, Jane, 1890-1960--Portraits": the name part
        m = NAMED.match(name)
        if m:
            born = int(m.group(2))
            if year and proven_adult(born, "", year, ""):
                proven.append(f"{m.group(1).strip()}, born {born}")
            else:
                unproven += 1
        elif NAME_ONLY.match(name):
            unproven += 1
    if unproven or not proven:
        return "", "adulthood not documented (anonymous, or a birth or photo date missing or under 18)"
    if SEVERAL.search(text) and len(proven) < 2:
        return "", "not every person is documented"
    return f"named, photo year {year}: " + "; ".join(proven), content


CATEGORIES = ("not a photograph", "not about nudity or sex", "a child or young person, or an age under 18",
              "violence, no consent, a myth, an animal or doubtful photo wording", "not every person is documented",
              "adulthood not documented (anonymous, or a birth or photo date missing or under 18)", "blocked earlier",
              "already approved", "the picture could not be downloaded", STUDY_CATEGORY, ASK_FIRST)


# ----------------------------------------------------------------- the review folder

class ReviewFolder:
    """The review folder: review-list.csv, decisions.csv, blocked.txt, search-log.txt and the approved workspaces."""

    def __init__(self, folder):
        """Use (and make) the review folder."""
        self.folder = os.path.abspath(folder)
        os.makedirs(self.folder, exist_ok=True)

    def path(self, name):
        """A file in the review folder."""
        return os.path.join(self.folder, name)

    def items(self):
        """The rows of review-list.csv (dicts), in order."""
        try:
            with open(self.path(REVIEW_LIST), encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []

    def save_items(self, items):
        """Write review-list.csv (safely: a new file first, then put in place)."""
        temporary = self.path(REVIEW_LIST + ".new")
        with open(temporary, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=LIST_COLUMNS)
            w.writeheader()
            for item in items:
                w.writerow({k: item.get(k, "") for k in LIST_COLUMNS})
        os.replace(temporary, self.path(REVIEW_LIST))

    def blocked(self):
        """The ids that are never fetched again."""
        try:
            with open(self.path(BLOCKED), encoding="utf-8") as f:
                return {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            return set()

    def block(self, item_id):
        """Never fetch this id again."""
        with open(self.path(BLOCKED), "a", encoding="utf-8") as f:
            f.write(item_id + "\n")

    def log(self, item_id, decision, person, reason=""):
        """Add one decision to decisions.csv: time, id, decision, by whom, reason."""
        new = not os.path.exists(self.path(DECISIONS))
        with open(self.path(DECISIONS), "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["time", "id", "decision", "by", "reason"])
            w.writerow([now(), item_id, decision, person, reason])

    def decisions(self):
        """The rows of decisions.csv (dicts)."""
        try:
            with open(self.path(DECISIONS), encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []

    def workspace(self, content, group):
        """The approved workspace for a content ("sexual" or "nudity") and licence group (made when missing)."""
        folder = os.path.join(self.folder, APPROVED, f"{content}-{'open' if group == OPEN else 'personal'}")
        ws = dp.make_workspace(folder, f"Documented adult photographs ({content}, {group})")
        ws.data.update(review_only=True, documented_adults=True, content=content, review_source=KEY,
                       review_category="" if group == OPEN else "noncommercial", needs_explicit_choice=True,
                       never_for_picture_making=True, never_publish=True)
        ws.save()
        return ws

    def write_log(self, counts, found, approved):
        """search-log.txt: how many records were looked at, approved, and left out for each reason (numbers only:
        a left-out record is never named)."""
        with open(self.path(SEARCH_LOG), "a", encoding="utf-8") as f:
            f.write(f"{now()}: {found} records looked at, {approved} documented and approved.\n")
            for reason in CATEGORIES:
                if counts.get(reason):
                    f.write(f"  left out, {reason}: {counts[reason]}\n")


def smaller_jpeg(data):
    """The picture as JPEG bytes, at most describe_package.LONG_SIDE pixels (made in memory); None when unreadable."""
    try:
        from PIL import Image, ImageOps
        with Image.open(io.BytesIO(data)) as picture:
            picture = ImageOps.exif_transpose(picture).convert("RGB")
            picture.thumbnail((dp.LONG_SIDE, dp.LONG_SIDE))
            out = io.BytesIO()
            picture.save(out, "JPEG", quality=dp.JPEG_QUALITY)
            return out.getvalue()
    except Exception:  # noqa: BLE001 - not a picture
        return None


def description_of(record, reason=""):
    """A plain description from the record's own words, following the guide (HOW TO DESCRIBE SEXUAL CONTENT, NUDITY
    AND CONSENT.txt): "A photograph from <institution>, <year>. <title>. <catalogue text>", crude and judgement
    words put plainly (adult_review_sources.plain), and how the record documents that the people are adults (age is
    said only as documented)."""
    parts = [f"A photograph from the {record['institution']}" + (f", {record['year']}" if record.get("year") else "")
             + "."]
    title = clean(record["title"]).rstrip(".")
    if title:
        parts.append(f'The catalogue\'s title is "{title}".')
    text = ars.rs.first_sentences(ars.plain(record.get("catalogue_text", "")), 80, 3)
    if text and text.lower() not in title.lower():
        parts.append(ars.sentence(text))
    if reason:
        parts.append(ars.sentence(f"The catalogue documents that the people shown are adults ({reason})"))
    return " ".join(JUDGEMENT.sub(lambda m: "explicit" if m.group(0).lower().startswith("obscen") else "sexual",
                                  p) for p in parts)


# Judgement words a description never uses (the guide's rule 4): put plainly.
JUDGEMENT = re.compile(r"\b(obscen\w*|lewd\w*|lascivious\w*|lustful|bawdy|sexy|smutty|dirty)\b", re.I)


def approve(review, record, data, reason, content):
    """Store a documented record's picture (bytes in memory) in its approved workspace as "checked", log it and
    list it. Returns the file name."""
    ws = review.workspace(content, record["group"])
    name = dp.free_name(ws.folder, dp.safe_name(record["id"]) + ".jpg", ws.pictures)
    with open(ws.path(name), "wb") as f:
        f.write(data)
    dp.write_file_text(dp.description_path(ws.folder, name), description_of(record, reason))
    entry = ws.entry(name)
    by = f"documented adult ({reason})"
    entry.update(status=dp.CHECKED, described_by="catalogue record", described_at=now(), checked_by=by,
                 checked_at=now(), added_at=now(), changed_at=now(), hash=dp.bytes_hash(data), content=content,
                 adult_approved_by=by, credit=f"{record['title'][:150]}, {record['institution']}",
                 licence=record["rights"][:200], page_url=record["page_url"], source_url=record["image_url"],
                 category=record["group"], not_for_picture_making="yes",
                 notes=f"Approved automatically: {by}. Rights: {record['rights'][:200]}.")
    ws.save()
    review.log(record["id"], "approved: " + by, "automatic", reason)
    return os.path.relpath(ws.path(name), review.folder)


def reject(review, item_id, person, decision="rejected"):
    """The reviewer's Reject (or Unsure): delete the picture and its description, remove it from its workspace,
    block the id and log the decision. True when a picture was removed."""
    items = review.items()
    removed = False
    for item in items:
        if item["id"] != item_id:
            continue
        path = os.path.join(review.folder, item.get("file", ""))
        if item.get("file") and os.path.isfile(path):
            ws = dp.open_workspace(os.path.dirname(path))
            name = os.path.basename(path)
            for leftover in (path, dp.description_path(ws.folder, name)):
                if os.path.exists(leftover):
                    os.remove(leftover)
            ws.pictures.pop(name, None)
            ws.save()
            removed = True
        item.update(status=decision, file="")
    review.save_items(items)
    review.block(item_id)
    review.log(item_id, decision, person)
    return removed


def confirm(review, item_id, person):
    """The reviewer's Approve on an approved picture: the second look is logged (nothing else changes)."""
    items = review.items()
    for item in items:
        if item["id"] == item_id:
            item["status"] = f"approved, confirmed by {person}"
    review.save_items(items)
    review.log(item_id, "confirmed: every person is clearly an adult", person)


def fetch_into_memory(session, url, timeout=60):
    """A picture's bytes from its institution, held in memory only (no file, no cache): None on failure."""
    try:
        r = session.get(url, timeout=timeout)
        return r.content if r.status_code == 200 and r.content else None
    except Exception:  # noqa: BLE001 - not reachable
        return None


# ----------------------------------------------------------------- link-only records and enquiries

# The owner's change (November 2026): a SEXUAL photograph whose record passes every word screen (no minor word:
# "girl" and "boy" stay hard exclusions for photographs) but does not document that everyone is an adult is not
# just dropped: it is listed BY ITS LINK ONLY in link-only.csv (institution, id, title, catalogue text, rights,
# group, catalogue page: never a picture or a picture address), so the owner can ask the institution about the
# sitters (enquiry()). It is approved ONLY with documentation the institution gives (approve_documented): never on
# anyone's judgement of how old the people look, which cannot settle age; nobody needs to open the picture to send
# an enquiry. Undecided or unsure counts as not approved.
LINK_ONLY = "link-only.csv"
LINK_COLUMNS = ("section", "id", "institution", "title", "catalogue_text", "rights", "group", "page_url", "status",
                "enquiry", "decided_by", "decided_at", "evidence")
ASK_FIRST_SECTION = ("Ask the institution first: send the enquiry BEFORE opening the page. These records name a "
                     "girl, boy, lad or lass; they are approved only with the institution's documentation that every "
                     "person was 18 or over.")
NO_DOCUMENTATION_SECTION = "No documented adulthood: approved only with the institution's documentation."
ENQUIRIES = "enquiries"
UNDOCUMENTED = ("not every person is documented",
                "adulthood not documented (anonymous, or a birth or photo date missing or under 18)")
MIN_EVIDENCE = 20                  # characters of documentation a reviewer must give to approve


def link_items(review):
    """The rows of link-only.csv (dicts)."""
    try:
        with open(review.path(LINK_ONLY), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def save_link_items(review, items):
    """Write link-only.csv (safely)."""
    temporary = review.path(LINK_ONLY + ".new")
    with open(temporary, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LINK_COLUMNS)
        w.writeheader()
        for item in items:
            w.writerow({k: item.get(k, "") for k in LINK_COLUMNS})
    os.replace(temporary, review.path(LINK_ONLY))


def link_only(review, record, ask_first=False):
    """List a sexual record without documented adulthood by its link only (never twice, never a blocked one);
    ask_first: in the "Ask the institution first" section (only girl, boy, lad or lass named)."""
    items = link_items(review)
    if record["id"] in review.blocked() or any(i["id"] == record["id"] for i in items):
        return False
    items.append({"section": ASK_FIRST_SECTION if ask_first else NO_DOCUMENTATION_SECTION, "id": record["id"], "institution": record["institution"], "title": record["title"],
                  "catalogue_text": record["catalogue_text"][:1000], "rights": record["rights"],
                  "group": licence_group(record["rights"]), "page_url": record["page_url"],
                  "status": "waiting for documentation"})
    save_link_items(review, items)
    return True


ENQUIRY = """To: [the institution's rights and reproductions, or collections, contact]
From: [YOUR NAME] <[YOUR EMAIL]>
Subject: Question about the people shown in catalogue record {id}

Dear colleagues,

I am preparing a private, accessible picture-description tool for a blind adult and would like to include the
photograph described in your catalogue record below, which is publicly listed with the rights statement shown.

  Title: {title}
  Record: {id}
  Link: {page_url}
  Rights statement: {rights}

Before using it, I need to be certain that everyone shown was an adult (18 or over) and took part willingly. Does
your institution hold any information about the people photographed: their identities, their ages or dates of
birth, the date of the photograph, or model releases or other consent records? Anything you can share, or a
pointer to where such information is kept, would be very welcome.

If no such information exists, I will not use the photograph.

Thank you for your help.

With kind regards,
[YOUR NAME]
"""


def enquiry(review, item_id):
    """Write a polite enquiry to the institution about one link-only record into the review folder's enquiries
    folder (placeholders for the sender: the owner fills in and sends it himself). Returns its path."""
    items = link_items(review)
    item = next(i for i in items if i["id"] == item_id)
    folder = review.path(ENQUIRIES)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, dp.safe_name(item_id) + ".txt")
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(ENQUIRY.format(**{k: item.get(k, "") for k in ("id", "title", "page_url", "rights")}))
    item["enquiry"] = os.path.relpath(path, review.folder)
    save_link_items(review, items)
    review.log(item_id, "enquiry written", "", "")
    return path


class NotEnoughEvidence(ValueError):
    """Approval was asked without documentation from the institution."""


def approve_documented(review, item_id, person, evidence, s=None, image_url=None):
    """Approve a link-only record WITH DOCUMENTATION FROM THE INSTITUTION (evidence: pasted or summarised, at least
    MIN_EVIDENCE characters; a reviewer's name is needed too). Only then is its picture found (image_url_for) and
    downloaded into the approved workspace, logged with the name, time and evidence. Raises NotEnoughEvidence
    otherwise, before anything is fetched."""
    evidence, person = clean(evidence), clean(person)
    if len(evidence) < MIN_EVIDENCE or not person:
        raise NotEnoughEvidence("Approval needs the reviewer's name and the documentation the institution gave "
                                "(identities, ages or model releases), pasted or summarised.")
    items = link_items(review)
    item = next(i for i in items if i["id"] == item_id)
    if item.get("section") == ASK_FIRST_SECTION and not AGE_EVIDENCE.search(evidence):
        raise NotEnoughEvidence("This record names a girl, boy, lad or lass: approval needs the institution's "
                                "documentation that every person was 18 or over (an age, a birth date or year, or "
                                "that they were adults).")
    s = s or session()
    url = image_url or image_url_for(s, item)
    data = smaller_jpeg(fetch_into_memory(s, url) or b"") if url else None
    if not data:
        return False
    reason = f"documentation from the institution: {evidence[:300]}"
    record = {"id": item["id"], "title": item["title"], "institution": item["institution"],
              "catalogue_text": item["catalogue_text"], "rights": item["rights"], "group": item["group"],
              "page_url": item["page_url"], "image_url": url, "year": ""}
    file = approve(review, record, data, reason, "sexual")
    review.log(item_id, "approved with documentation", person, evidence[:500])
    listed = review.items()
    listed.append({**{k: record.get(k, "") for k in LIST_COLUMNS}, "reason": reason, "content": "sexual",
                   "file": file, "status": "approved: documented by the institution"})
    review.save_items(listed)
    item.update(status="approved with documentation", decided_by=person, decided_at=now(), evidence=evidence[:500])
    save_link_items(review, items)
    return True


def not_approved(review, item_id, person, decision="not approved"):
    """Not approved (or unsure): recorded, and the record is blocked (never listed or fetched again)."""
    items = link_items(review)
    for item in items:
        if item["id"] == item_id:
            item.update(status=decision, decided_by=person, decided_at=now())
    save_link_items(review, items)
    review.block(item_id)
    review.log(item_id, decision, person)


def image_url_for(s, item):
    """The picture address of a link-only record, read from its institution's record only when it is approved."""
    try:
        if item["id"].startswith("loc-"):
            data = s.get(item["page_url"], params={"fo": "json"}, timeout=90).json()
            images = [i.split("#")[0] for i in as_list((data.get("item") or {}).get("image_url") or
                                                       data.get("image_url")) if isinstance(i, str)]
            return images[-1] if images else ""
        if item["id"].startswith("wellcome-"):
            work = s.get(WELLCOME + "works/" + item["id"][9:], params={"include": "images"}, timeout=90).json()
            image = s.get(WELLCOME + "images/" + work["images"][0]["id"], timeout=90).json()
            return image["locations"][0]["url"].replace("info.json", "full/!1600,1600/0/default.jpg")
    except Exception:  # noqa: BLE001 - not found
        return ""
    return ""


# ----------------------------------------------------------------- the sources

def session():
    """A requests session with the kit's plain user agent."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def as_list(value):
    """A loc.gov field as a list (it gives some fields as one text, others as a list)."""
    if not value:
        return []
    return value if isinstance(value, list) else [value]


LOC = "https://www.loc.gov/photos/"
LOC_QUERIES = ("nude photograph", "nudes photographs", "sexual intercourse photograph", "erotic photographs",
               "nude studies photographs", "adult models nude")


def loc_records(s, most, pause=LOC_PAUSE):
    """Candidate records from the Library of Congress: search results whose words are about nudity or sex, then
    each item's own record (names with dates, rights advisory, notes). Gives dicts for documented()."""
    seen = set()
    for q in LOC_QUERIES:
        try:
            time.sleep(pause)
            data = s.get(LOC, params={"q": q, "fo": "json", "c": 100}, timeout=90).json()
        except Exception:  # noqa: BLE001 - the next search
            continue
        for r in data.get("results") or []:
            url = r.get("url") or r.get("id") or ""
            if not url or url in seen or "/item/" not in url:
                continue
            seen.add(url)
            words = " ".join(clean(r.get(k)) for k in ("title", "description", "subject"))
            if not (NUDE.search(words) or SEX.search(words)):
                yield {"skip": "not about nudity or sex"}
                continue
            try:
                time.sleep(pause)
                item = (s.get(url, params={"fo": "json"}, timeout=90).json() or {}).get("item") or {}
            except Exception:  # noqa: BLE001 - the next record
                continue
            images = [i.split("#")[0] for i in as_list(r.get("image_url")) if isinstance(i, str) and i]
            yield {"id": "loc-" + url.rstrip("/").rsplit("/", 1)[-1], "title": clean(item.get("title") or r.get("title")),
                   "institution": "Library of Congress", "page_url": url,
                   "image_url": images[-1] if images else "",
                   "catalogue_text": clean(" ".join(clean(x) for x in as_list(item.get("summary")) +
                                                    as_list(item.get("notes")) + as_list(r.get("description")))),
                   "names": [clean(n) for n in as_list(item.get("subject_headings")) + as_list(item.get("names"))
                             if NAMED.match(clean(n).split("--")[0]) or NAME_ONLY.match(clean(n).split("--")[0])],
                   "dates": [clean(item.get("date")), clean(item.get("created_published"))],
                   "kind": [clean(r.get("original_format")), clean(item.get("medium")), clean(item.get("format"))],
                   "rights": clean(item.get("rights_advisory") or item.get("rights") or "")}
            if len(seen) >= most:
                return


WELLCOME = "https://api.wellcomecollection.org/catalogue/v2/"
WELLCOME_QUERIES = ("nude photograph", "sexual intercourse photograph", "sex education photograph",
                    "naked photograph", "adult models photograph")
WELLCOME_LICENCES = {"pdm": "Public Domain Mark", "cc-0": "CC0", "cc-by": "CC BY 4.0",
                     "cc-by-nc": "CC BY-NC 4.0", "cc-by-nc-nd": "CC BY-NC-ND 4.0", "inc": "In copyright"}


def wellcome_records(s, most, pause=WELLCOME_PAUSE):
    """Candidate records from the Wellcome Collection: works with a picture, their person subjects (with dates),
    production dates, notes and the picture's own licence."""
    seen = 0
    for q in WELLCOME_QUERIES:
        try:
            time.sleep(pause)
            data = s.get(WELLCOME + "works", params={"query": q, "pageSize": 100, "items.locations.locationType":
                                                     "iiif-image", "include": "subjects,production,notes,genres,"
                                                     "images,contributors"}, timeout=90).json()
        except Exception:  # noqa: BLE001 - the next search
            continue
        for w in data.get("results") or []:
            seen += 1
            if seen > most:
                return
            images = w.get("images") or []
            if not images:
                continue
            notes = " ".join(clean(c) for n in w.get("notes") or [] for c in n.get("contents") or [])
            names = [clean(sub.get("label")) for sub in w.get("subjects") or []
                     if any(c.get("type") == "Person" for c in sub.get("concepts") or [])]
            try:
                time.sleep(pause)
                image = s.get(WELLCOME + "images/" + images[0]["id"], timeout=90).json()
            except Exception:  # noqa: BLE001 - the next record
                continue
            loc = (image.get("locations") or [{}])[0]
            licence = (loc.get("license") or {}).get("id", "")
            yield {"id": "wellcome-" + w["id"], "title": clean(w.get("title")), "institution": "Wellcome Collection",
                   "page_url": f"https://wellcomecollection.org/works/{w['id']}",
                   "image_url": loc.get("url", "").replace("info.json", "full/!1600,1600/0/default.jpg"),
                   "catalogue_text": clean(f"{clean(w.get('description'))} {notes} "
                                           + " ".join(clean(x.get("label")) for x in w.get("subjects") or [])),
                   "names": names,
                   "dates": [clean(d.get("label")) for p in w.get("production") or [] for d in p.get("dates") or []],
                   "kind": [clean((w.get("workType") or {}).get("label"))] +
                           [clean(g.get("label")) for g in w.get("genres") or []],
                   "rights": WELLCOME_LICENCES.get(licence, licence or "no licence stated")}


SOURCES = (("Library of Congress", loc_records), ("Wellcome Collection", wellcome_records))


def search(folder, most=200, say=print, sources=SOURCES, s=None):
    """Search every source, check each record with documented() BEFORE anything is fetched, download and approve
    the documented ones, and log only the numbers left out. Returns (approved, counts)."""
    review, s = ReviewFolder(folder), s or session()
    items = review.items()
    listed = {i["id"] for i in items}
    blocked = review.blocked()
    counts, found, approved = {}, 0, 0
    for name, records in sources:
        say(f"{name}: searching ...")
        for record in records(s, most):
            if "skip" in record:
                counts[record["skip"]] = counts.get(record["skip"], 0) + 1
                found += 1
                continue
            found += 1
            if record["id"] in blocked:
                counts["blocked earlier"] = counts.get("blocked earlier", 0) + 1
                continue
            if record["id"] in listed:
                counts["already approved"] = counts.get("already approved", 0) + 1
                continue
            reason, content = documented([record["title"], record["catalogue_text"]], record["names"],
                                         record["dates"], record["kind"], record["rights"])
            if not reason:
                counts[content] = counts.get(content, 0) + 1
                if content == ASK_FIRST or (content in UNDOCUMENTED and
                                            SEX.search(f"{record['title']} {record['catalogue_text']}")):
                    link_only(review, record, ask_first=content == ASK_FIRST)   # by its link only, for an enquiry
                continue                          # never fetched or shown
            data = smaller_jpeg(fetch_into_memory(s, record["image_url"]) or b"") if record["image_url"] else None
            if not data:
                counts["the picture could not be downloaded"] = counts.get("the picture could not be downloaded",
                                                                           0) + 1
                continue
            record["group"] = licence_group(record["rights"])
            record["year"] = earliest_year(*record["dates"]) or ""
            file = approve(review, record, data, reason, content)
            items.append({**{k: record.get(k, "") for k in LIST_COLUMNS}, "reason": reason, "content": content,
                          "file": file, "status": "approved: documented adult"})
            listed.add(record["id"])
            review.save_items(items)
            approved += 1
        say(f"{name}: done.")
    review.write_log(counts, found, approved)
    say(f"{found} records looked at, {approved} documented and approved; "
        + ", ".join(f"{v} {k}" for k, v in counts.items()) + ".")
    return approved, counts


def main(argv=None):
    """search or list (see the module docstring)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("search", "list"):
        print(__doc__.strip().splitlines()[-2].strip())
        print(__doc__.strip().splitlines()[-1].strip())
        return 1
    folder = argv[1] if len(argv) > 1 else DEFAULT_FOLDER
    if argv[0] == "search":
        search(folder, int(argv[2]) if len(argv) > 2 else 200)
    else:
        for item in ReviewFolder(folder).items():
            print(f"{item['status']}: {item['title'][:80]} ({item['institution']}; {item['group']}; {item['reason']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
