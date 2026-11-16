"""REVIEW-ONLY picture collections: medical and educational pictures of adult genitals and breasts (healthy, normal
variation, and common conditions), and the Fitzpatrick17k skin-condition set.

Why: the owner is blind. A blind person cannot ask a friend whether their genitals or breasts look normal, so the
private, local describer should be able to describe healthy anatomy and its normal variation, normal variants that
often worry people (pearly penile papules, Fordyce spots, vulval papillomatosis, uneven labia, inverted nipples,
accessory nipples and so on) and common conditions (genital warts, herpes, syphilis sores, thrush, lichen sclerosus,
balanitis, mastitis, the warning signs of breast cancer and so on), clinically and respectfully.

Nothing here trains by itself. Each collection is downloaded into a "Describe pictures" workspace
(describe_package.py) where every picture arrives with a DRAFT description (made from the source's own caption or
label, in plain clinical words, ending "Only a doctor can diagnose this.") and the status "needs another look", never
"described" or "checked". A sighted, trusted adult screens every picture (REVIEW-INSTRUCTIONS.txt, written into the
workspace) and marks it "checked" only when it is an adult, medical or educational, and correctly described.

HARD RULES kept by every fetch function here:
  - ADULTS ONLY. A record is left out when its text (title, caption, abstract, description, label, categories or file
    address) mentions or suggests a child (CHILD: child, infant, baby, newborn, adolescent, teen, minor, puberty,
    paediatric, nappy or diaper, school, son, daughter and more) or gives any age under 18. Where a source gives no
    ages, only clinical or educational sources are used, and the human review must confirm adulthood. Where a
    condition is common in children (phimosis, hydrocele, molluscum, gynaecomastia), Commons files are kept only when
    their text shows an adult.
  - NO SEXUAL CONTENT (SEXUAL): no sexual activity, arousal or erection, nothing erotic or pornographic, nothing from
    porn or adult-entertainment sites, no Commons file in a sexual, erotic, art, body-modification or nudity-culture
    category (BLOCKED_CATEGORY). "Sexually transmitted infection" is a clinical phrase and is allowed.
  - REVIEW-ONLY: status "needs another look" on arrival; describing.json is marked "review_only" with the content
    tag; the kit must train only on pictures marked "checked" in these workspaces (see PLUMBING below).

ALL SKIN TONES (the owner's requirement): conditions look different on darker skin, so each picture's entry records
"skin_type" ("I-II", "III-IV", "V-VI" or "not stated"), only from what the source says (Fitzpatrick17k's own skin
type; a Fitzpatrick type or an ethnicity written in a caption or abstract), never guessed. Fitzpatrick17k is sampled
in turns across skin-type groups and conditions; PubMed Central is searched on purpose for skin-of-colour articles and
for authors in Africa, Asia, Latin America and the Middle East. Each summary gives the count per group.

How to use (for the kit's own code):
  REVIEW_SOURCES   a list of plain dicts: key, name, category ("open", "share-alike", "noncommercial", "research"),
                   licence, terms, terms_summary, credit, content ("intimate" or "medical"), cap, download (size),
                   fetch (a function fetch_<key>(folder, cap, say)), plus "review_only": True.
  NOT_INCLUDED     sources looked at and left out, with the reason.
  FITZ_EXCLUDED_LABELS, FITZ_GENITAL_LABELS   the Fitzpatrick17k labels left out (usually a child) and the labels that
                   are usually at a genital site (their pictures are tagged "intimate" one by one).
  Each fetch function downloads into folder (made into a describing workspace when it is not one yet), skips
  pictures already there or already tried, so a stopped run carries on where it was, and returns a plain summary.

    python review_sources.py <key> <folder> [cap]      (a quick test of one collection)

PLUMBING the rest of the kit needs (not done here; other files are being edited by others):
  - own_data.check_folder uses "described" AND "checked" pictures. For a workspace whose describing.json has
    "review_only": true it must use "checked" pictures only (and describe_package.describe() and import_package can
    set "described", so the check must be in own_data, not only here).
  - Content "intimate" (the whole collection, or one picture whose entry says "content": "intimate", as in
    Fitzpatrick17k) is used only when BOTH "Include nudity" and "Include medical and anatomy pictures" are ticked, and
    never for picture-making training. sources.CONTENTS knows only "", "nudity" and "medical" today.

Only requests and Pillow are needed (as for the rest of the kit). Nothing is sent anywhere except the downloads.
"""

import concurrent.futures
import csv
import html
import io
import json
import os
import re
import shutil
import time

import describe_package as dp

USER_AGENT = "PictureModelTrainingKit/2 (https://github.com/mark-getbraille/toolkit-models)"
DOCTOR = "Only a doctor can diagnose this."
SEE_SOON = "See a doctor soon about any new change like this."
REVIEW_FILE = "REVIEW-INSTRUCTIONS.txt"
CREDITS_FILE = "CREDITS.txt"
TRIED_FILE = ".review-tried.json"        # ids already tried (kept or left out), so a new run does not try them again
STAGING = ".incoming"                    # a hidden folder (own_data and add_pictures skip it) for downloads in progress
LONG_SIDE = 2048
SMALLEST = 120                           # pixels: smaller pictures are left out
BATCH = 20                               # pictures added to the workspace at a time

REVIEW_INSTRUCTIONS = """REVIEW-ONLY COLLECTION: {name}

These pictures are medical and educational pictures that may show adult genitals or breasts. They were collected so
that a blind person's private, local describer can describe healthy bodies, normal variation and common conditions.
NONE of them is used for training until a person has checked it.

This collection must be screened by a sighted, trusted adult.

For every picture:
1. DELETE the picture (do not just skip it) when it shows, or may show, a child or a young person under 18.
2. DELETE any picture that is sexual or pornographic in any way.
3. DELETE any picture that is not medical or educational (for example a holiday photo, art, or an advert).
4. Read the draft description. It was made from the source's own caption or label and may be wrong or too technical.
   Correct it so that it says plainly and respectfully what is visible. Keep the last sentence "Only a doctor can
   diagnose this." (and, for a warning sign such as a breast lump, "See a doctor soon about any new change like
   this.").
5. Mark the picture "checked" ONLY when you are sure that it shows an adult, is medical or educational, and is
   correctly described.

Only checked pictures are ever trained on. Pictures that are new, described, skipped or need another look are
never used from this collection.

Skin tone: this collection should show people of all races and skin tones, because conditions look different on
darker skin (redness can look purple, dark brown or grey, and some marks are harder to see). A skin type is written
in a description only when the source states it; do not guess one. Please note in the picture's notes, or tell the
person who gave you this collection, any skin-tone gaps you see (for example "almost no dark skin among the breast
pictures"). The count per skin-type group is in describing.json ("skin_type_counts") and in CREDITS.txt.

Where each picture comes from, and its licence, is in CREDITS.txt and in each picture's notes.
Source: {credit}
Licence or terms: {licence}
"""

# ----------------------------------------------------------------- filters

# Words that mention or suggest a child or young person. Wide on purpose.
CHILD = re.compile(
    r"\b(child\w*|kids?|boys?|girls?|infan\w*|bab(y|ies)|toddlers?|newborns?|new-borns?|neonat\w*|teen\w*|"
    r"adolescen\w*|minors?|underage|under-age|under 18|juvenile\w*|youths?|pubert\w*|prepubert\w*|peripubert\w*|"
    r"tanner stage|p(a)?ediatric\w*|paediatr\w*|nappy|nappies|diapers?|school\w*|preschool\w*|pupils?|sons?|"
    r"daughters?|congenital\w*|fetus|fetal|foetus|foetal|\d+[- ](month|week|day)s?[- ]old|girlhood|boyhood)\b", re.I)

# Sexual activity, arousal, erotica, pornography and the like ("sexually transmitted" is allowed).
SEXUAL = re.compile(
    r"\b(porn\w*|erotic\w*|sexy|nsfw|xxx|masturbat\w*|orgasm\w*|ejaculat\w*|aroused|arousal|erect|erections?|"
    r"erectile|tumescen\w*|intercourse|coitus|coital|foreplay|sex ?toys?|dildos?|vibrators?|fetish\w*|bdsm|bondage|"
    r"kink\w*|cock|cocks|dick|pussy|tits|boobs?|cum|penetrat\w*|fellatio|cunnilingus|oral sex|anal sex|"
    r"having sex|sex acts?|sex work\w*|strip(per|tease)\w*|naturis\w*|nudis\w*|nude models?|glamou?r|playboy|"
    r"onlyfans|selfies?|hentai|hardcore|softcore|condoms?|enlargement|lingerie|seductive|sensual\w*)\b", re.I)

# Commons categories that are never used (sexual, art, nudity culture, body modification and the like).
BLOCKED_CATEGORY = re.compile(
    r"(sex|porn|erotic|nud(e|ity|ism)|naked|naturis|art\b|artwork|in art|painting|sculpture|statue|drawing by|"
    r"tattoo|piercing|modification|accessor|sleeve|sheath|rigidity|erect|ejaculat|masturbat|insertion|severed|"
    r"enlargement|plethysmograph|phallometr|shaving|selfie|exhibitionis|facing (left|right)|men with|women with|"
    r"helicopter|grower|shower|condom|cock|fetish|bdsm|bondage|lingerie|underwear|swimwear|bikini|topless|"
    r"breastfeed|breast-feed|lactat|nursing|children|child|bab(y|ies)|infant|boys|girls|teen|youth|puberty)", re.I)

# Words naming the genitals or the area around them.
GENITAL = re.compile(
    r"\b(genit\w*|penis|penile|glans|prepuc\w*|foreskin|frenulum|coronal|scrot\w*|testic\w*|testis|testes|"
    r"epididym\w*|spermatic|vulv\w*|labia\w*|labium|clitor\w*|vestibul\w*|introitus|fourchette|vagin\w*|"
    r"perine\w*|perianal|anogenital|pubic|pubis|groin|inguinal|intertrigo|"
    r"balan\w*|phimosis|paraphimosis|hydrocele|varicocele|bartholin\w*)\b", re.I)

# Words naming the breasts or chest.
BREAST = re.compile(
    r"\b(breasts?|mammary|nipples?|areola\w*|gyn(a)?ecomastia|mastitis|mastectomy|lumpectomy|peau d.orange|"
    r"inframammary|polythelia|supernumerary nipples?|accessory nipples?|chest wall)\b", re.I)

AGE = re.compile(r"\b(\d{1,3})[- ](?:year|yr)s?[- ]old\b|\baged (\d{1,3})\b|\b(\d{1,3}) ?(?:years?|yrs?) (?:of age|old)\b|"
                 r"\b(\d{1,3}) ?y/?o\b|\bage[: ]+(\d{1,3})\b", re.I)
ADULT_WORDS = re.compile(r"\b(adults?|man|men|woman|women|gentleman|lady|elderly|older|middle-aged|"
                         r"postmenopausal|menopaus\w*|grandmother|grandfather|husband|wife)\b", re.I)


def clean(text):
    """Text with its spaces tidied ("" for nothing)."""
    return " ".join(html.unescape(str(text or "")).split())


def no_tags(text):
    """Text without HTML or XML tags."""
    return clean(re.sub(r"<[^>]+>", " ", str(text or "")))


def ages(text):
    """The ages in years a text gives ("a 45-year-old man", "aged 70", "age: 33")."""
    return [int(next(g for g in m.groups() if g)) for m in AGE.finditer(text or "")]


def child_free(*texts):
    """True when none of the texts mentions or suggests a child and every age they give is 18 or more."""
    text = " ".join(clean(t) for t in texts if t)
    return not CHILD.search(text) and all(a >= 18 for a in ages(text))


def adult_shown(*texts):
    """(True, age or None) when the texts are child-free AND show an adult (an age of 18 or more, or an adult word);
    otherwise (False, None)."""
    text = " ".join(clean(t) for t in texts if t)
    if not child_free(text):
        return False, None
    found = ages(text)
    if found:
        return True, found[0]
    return bool(ADULT_WORDS.search(text)), None


def not_sexual(*texts):
    """True when none of the texts names sexual activity, arousal, erotica or pornography."""
    return not SEXUAL.search(" ".join(clean(t) for t in texts if t))


# ----------------------------------------------------------------- skin tone (recorded only when the source says it)

# Conditions look different on darker skin (redness can look purple, dark brown or grey; some marks are harder to
# see), so every collection records the skin type or the ethnicity its source states, samples evenly across skin
# types where it has them, and the summary counts pictures per skin-type group so gaps are visible.
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
SKIN_WORDS = {1: "very fair", 2: "fair", 3: "light brown", 4: "moderate brown", 5: "dark brown",
              6: "very dark brown to black"}
GROUPS = ("I-II", "III-IV", "V-VI", "not stated")
FITZ_TEXT = re.compile(r"\bFitzpatrick (?:skin )?(?:photo)?(?:type|phototype|class)s? ?(VI|IV|V|I{1,3}|[1-6])\b|"
                       r"\bskin (?:photo)?type ?(VI|IV|V|I{1,3}|[1-6])\b|\bphototype ?(VI|IV|V|I{1,3}|[1-6])\b")
ETHNICITY = re.compile(
    r"\b((?:African[- ]American|Afro-\w+|Black|African|Nigerian|Ghanaian|Kenyan|Ethiopian|Somali|Sudanese|"
    r"Ugandan|Tanzanian|Congolese|Cameroonian|Senegalese|South African|Caribbean|Jamaican|Haitian|Indian|"
    r"Pakistani|Bangladeshi|Sri Lankan|Nepali|South Asian|East Asian|Southeast Asian|Asian|Chinese|Japanese|"
    r"Korean|Vietnamese|Thai|Filipino|Filipina|Indonesian|Malay|Hispanic|Latino|Latina|Latinx|Mexican|"
    r"Brazilian|Colombian|Peruvian|Middle Eastern|Arab|Iranian|Persian|Turkish|Egyptian|Moroccan|Saudi|"
    r"Indigenous|Aboriginal|Maori|Pacific Islander|Native American|White|Caucasian)) "
    r"(?:man|woman|male|female|patient|person|adult|gentleman|lady|men|women|descent|origin|heritage)\b")


def fitz_type(value):
    """A Fitzpatrick skin type 1 to 6 from a table value ("5", "-1"), or None."""
    try:
        number = int(float(str(value).strip()))
    except ValueError:
        return None
    return number if 1 <= number <= 6 else None


def fitz_group(value):
    """The skin-type group of a Fitzpatrick value: "I-II", "III-IV", "V-VI" or "not stated"."""
    number = fitz_type(value)
    return GROUPS[(number - 1) // 2] if number else GROUPS[3]


def skin_from_text(*texts):
    """(group, words) for the skin type or ethnicity a source's own text states, never guessed:
    ("V-VI", "on dark brown skin (Fitzpatrick type V)"), ("not stated", "the source describes the person as Nigerian")
    or ("not stated", "") when it says nothing."""
    text = " ".join(clean(t) for t in texts if t)
    m = FITZ_TEXT.search(text)
    if m:
        value = next(g for g in m.groups() if g)
        number = int(value) if value.isdigit() else {v: k for k, v in ROMAN.items()}[value]
        return GROUPS[(number - 1) // 2], f"on {SKIN_WORDS[number]} skin (Fitzpatrick type {ROMAN[number]})"
    m = ETHNICITY.search(text)
    if m:
        return GROUPS[3], f"the source describes the person as {m.group(1)}"
    return GROUPS[3], ""


def darker_skin_colours(text):
    """An explanation with "red" followed by how redness often looks on darker skin (for Fitzpatrick IV to VI)."""
    return re.sub(r"\bred\b", "red (on darker skin often purple, dark brown or grey)", text, count=1)


def balanced(rows, group_of, label_of):
    """rows in a balanced order: taking turns between the groups (skin types), and within each group taking turns
    between the labels (conditions); the group "not stated" comes last in each round."""
    groups = {}
    for row in rows:
        groups.setdefault(group_of(row), {}).setdefault(label_of(row), []).append(row)
    queues = {}
    for group, labels in groups.items():
        order, lists = [], [list(v) for _k, v in sorted(labels.items())]
        while any(lists):
            for items in lists:
                if items:
                    order.append(items.pop(0))
        queues[group] = order
    names = sorted(queues, key=lambda g: (g == GROUPS[3], g))
    out = []
    while any(queues[g] for g in names):
        for g in names:
            if queues[g]:
                out.append(queues[g].pop(0))
    return out


# ----------------------------------------------------------------- plain words and conditions

PLAIN_WORDS = [
    (r"\bmaculopapular\b", "flat and raised (maculopapular)"), (r"\bvesicular\b", "blistering (vesicular)"),
    (r"\bvesicles\b", "small fluid-filled blisters (vesicles)"), (r"\bpustules\b", "pus-filled bumps (pustules)"),
    (r"\bpapules\b", "small raised bumps (papules)"), (r"\bmacules\b", "flat spots (macules)"),
    (r"\berythematous\b", "reddened"), (r"\berythema\b", "redness (erythema)"), (r"\bcutaneous\b", "skin"),
    (r"\blesions\b", "spots or sores"), (r"\blesion\b", "spot or sore"), (r"\bulcerations?\b", "open sores"),
    (r"\bedema\b|\boedema\b", "swelling"), (r"\bedematous\b|\boedematous\b", "swollen"),
    (r"\bpurulent\b", "pus-filled"), (r"\bexudate\b", "discharge"), (r"\bindurated\b", "hardened"),
    (r"\bdorsal\b", "upper"), (r"\bventral\b", "under"), (r"\bdistal\b", "far"), (r"\bproximal\b", "near"),
    (r"\blateral\b", "side"), (r"\bpatient[’']s\b", "person's"), (r"\bthe patient\b", "the person"),
    (r"\ba patient\b", "a person"), (r"\blithotomy position\b", "examination position (lying on the back, knees up)"),
    (r"\bintroitus\b", "vaginal opening (introitus)"), (r"\bprepuce\b", "foreskin (prepuce)"),
    (r"\bglans penis\b", "head of the penis (glans)"), (r"\burinary meatus\b", "opening of the urethra"),
    (r"\blabium majus\b", "outer lip (labium majus)"), (r"\blabia majora\b", "outer lips (labia majora)"),
    (r"\blabia minora\b", "inner lips (labia minora)"), (r"\bperineum\b", "area between the genitals and the anus "
                                                                        "(perineum)"),
    (r"\binguinal\b", "groin"), (r"\blymphadenopathy\b", "swollen lymph glands"), (r"\bpruritus\b", "itching"),
    (r"\bpruritic\b", "itchy"), (r"\bhyperpigment\w*\b", "darker"), (r"\bhypopigment\w*\b", "paler"),
    (r"\bdepigment\w*\b", "lost its colour"),
]
PLAIN_WORDS = [(re.compile(p, re.I), w) for p, w in PLAIN_WORDS]


def plain(text):
    """Text with medical words in plain words (the medical word kept in brackets where useful)."""
    for pattern, words in PLAIN_WORDS:
        text = pattern.sub(words, text)
    return re.sub(r"\b([Aa]) (?=[aeio]|u(?:pper|lcer|nder|nusual))", r"\1n ", text)          # "a upper view" -> "an upper view"


# (pattern, plain name, explanation, warning sign?) for genital and breast anatomy, normal variants and conditions.
# The first that matches names the condition in a draft ("This looks like ..."); a warning sign adds SEE_SOON.
CONDITIONS = [
    # normal variants that often worry people
    (r"pearly penile papules?|hirsuties (coronae glandis|papillaris)", "pearly penile papules", "harmless tiny "
     "skin-coloured bumps in rows around the rim of the head of the penis, a normal variant", False),
    (r"fordyce'?s? (spots?|granules?|glands?)|ectopic sebaceous", "Fordyce spots", "harmless tiny pale yellow or "
     "white spots, oil glands seen through the skin, a normal variant", False),
    (r"(vulv\w*|vestibular) papillomatosis|micropapillomatosis", "vulval papillomatosis", "harmless small soft "
     "finger-like bumps inside the inner lips, a normal variant", False),
    (r"angiokeratom\w*", "angiokeratomas", "harmless small dark red or purple spots made of tiny blood vessels", False),
    (r"tyson'?s? glands?", "Tyson's glands", "harmless small bumps beside the frenulum, a normal variant", False),
    (r"labi\w* (asymmetr\w*|hypertroph\w*)|(asymmetr\w*|enlarged|elongated|protruding) labia|labial hypertroph\w*",
     "uneven or larger inner lips", "a common normal variation in the size and shape of the labia", False),
    (r"inverted nipples?|nipple inversion|flat nipples?", "inverted or flat nipples", "nipples that point inward or "
     "lie flat; often normal from birth, but a nipple that newly turns in needs a doctor", False),
    (r"accessory nipples?|supernumerary nipples?|polythelia|third nipple", "an extra nipple", "a harmless small extra "
     "nipple, usually on the line from the armpit to the groin", False),
    (r"montgomery'?s? (glands?|tubercles?)", "Montgomery glands", "small normal bumps on the areola", False),
    (r"striae|stretch marks?", "stretch marks", "lines in the skin from stretching, common and harmless", False),
    # conditions of the genitals
    (r"condylom\w* lata|secondary syphilis", "secondary syphilis", "a later stage of syphilis, with a rash or moist "
     "patches; curable with antibiotics", False),
    (r"genital warts?|condylom\w* acuminat\w*|anogenital warts?|venereal warts?|condylomas?\b", "genital warts",
     "a common infection with a wart virus (HPV), with small skin-coloured bumps", False),
    (r"genital herpes|herpes genitalis|herpes simplex|hsv-?2|hsv-?1", "genital herpes", "a common virus infection "
     "that comes and goes, with small painful blisters that break into sores", False),
    (r"chancroid|haemophilus ducreyi|h\. ducreyi", "chancroid", "a bacterial infection that causes painful sores",
     False),
    (r"chancre|primary syphilis", "a syphilis sore (chancre)", "the first sign of syphilis, a usually painless "
     "firm sore; syphilis is curable with antibiotics", False),
    (r"syphili\w*|treponema", "syphilis", "a bacterial infection that is curable with antibiotics", False),
    (r"lymphogranuloma venereum|\blgv\b", "lymphogranuloma venereum", "a chlamydia infection that can cause sores "
     "and swollen groin glands", False),
    (r"donovanosis|granuloma inguinale", "donovanosis", "a bacterial infection with slowly growing red sores", False),
    (r"gonorrh\w*|gonococc\w*", "gonorrhoea", "a bacterial infection, often with discharge", False),
    (r"chlamydi\w*", "chlamydia", "a common bacterial infection, often without signs", False),
    (r"trichomon\w*", "trichomoniasis", "a common infection with a tiny parasite, often with discharge", False),
    (r"molluscum", "molluscum contagiosum", "a harmless virus that causes small, pearly, dimpled bumps", False),
    (r"pubic lice|pthir\w* pubis|phthir\w*|crab lice|pediculosis pubis", "pubic lice", "tiny insects that live in "
     "pubic hair", False),
    (r"scabies", "scabies", "tiny mites that burrow in the skin and cause an itchy rash", False),
    (r"mpox|monkeypox", "mpox", "a virus infection that causes spots that turn into blisters and sores", False),
    (r"lichen sclerosus|balanitis xerotica obliterans|\bbxo\b", "lichen sclerosus", "a long-lasting skin condition "
     "with white, thin, sometimes itchy patches; treatable", False),
    (r"lichen planus", "lichen planus", "an inflammatory condition with purplish bumps or white lacy patches", False),
    (r"lichen simplex", "lichen simplex", "thickened skin from long-term scratching", False),
    (r"zoon'?s? balanitis|plasma cell balanitis", "Zoon's balanitis", "a long-lasting shiny red patch on the head "
     "of the penis", False),
    (r"balanitis|balanoposthitis", "balanitis", "redness and soreness of the head of the penis", False),
    (r"vulvovaginal candid\w*|candid\w*|thrush|yeast infection", "thrush (candida)", "a common yeast infection with "
     "redness, itching and sometimes white discharge", False),
    (r"bacterial vaginosis", "bacterial vaginosis", "a common imbalance of vaginal bacteria, often with discharge",
     False),
    (r"tinea cruris|jock itch", "tinea cruris (jock itch)", "a fungal infection of the groin with a red, itchy, "
     "ring-edged rash", False),
    (r"intertrigo", "intertrigo", "a rash in skin folds from rubbing and moisture", False),
    (r"hidradenitis", "hidradenitis suppurativa", "a long-lasting condition with painful lumps in the armpits and "
     "groin", False),
    (r"folliculitis|ingrown hairs?", "folliculitis", "inflamed hair roots, small red or pus-filled bumps", False),
    (r"epidermoid cysts?|sebaceous cysts?|scrotal calcinosis", "skin cysts", "harmless small firm lumps under the "
     "skin", False),
    (r"bartholin\w* (cyst|abscess)", "a Bartholin's cyst", "a swelling of a gland beside the vaginal opening", False),
    (r"phimosis", "phimosis", "a foreskin that is too tight to pull back", False),
    (r"paraphimosis", "paraphimosis", "a foreskin stuck behind the head of the penis, which needs a doctor quickly",
     False),
    (r"varicocele", "a varicocele", "swollen veins above a testicle that can feel like a bag of worms; often harmless",
     False),
    (r"hydrocele", "a hydrocele", "a fluid-filled swelling around a testicle, usually harmless", False),
    (r"peyronie", "Peyronie's disease", "scar tissue in the penis that can make it curve", False),
    (r"vitiligo", "vitiligo", "patches of skin that have lost their colour", False),
    (r"psoriasis", "psoriasis", "a long-lasting skin condition with red, scaly patches", False),
    (r"eczema|dermatitis", "dermatitis", "inflamed, itchy skin", False),
    (r"circumcis\w*", "a circumcised penis", "a penis whose foreskin was removed, a common normal appearance", False),
    (r"penile (cancer|carcinoma)|carcinoma of the penis|(squamous cell )?carcinoma (in situ )?of the penis",
     "a possible cancer of the penis", "a growth or sore that needs a doctor's examination", True),
    (r"vulv\w* (cancer|carcinoma|intraepithelial)|\bvin\b", "a possible cancer of the vulva", "a growth, sore or "
     "patch that needs a doctor's examination", True),
    (r"testicular (cancer|tumou?r)|(cancer|tumou?r) of the testi", "a possible testicular tumour", "a lump in a "
     "testicle, which needs a doctor's examination", True),
    (r"extramammary paget", "extramammary Paget's disease", "a rare red, scaly patch that can be a skin cancer", True),
    # conditions and warning signs of the breast
    (r"paget'?s? disease (of the )?(nipple|breast)|mammary paget", "Paget's disease of the nipple", "a red, scaly, "
     "sometimes weeping nipple that can be a sign of breast cancer", True),
    (r"inflammatory breast (cancer|carcinoma)", "inflammatory breast cancer", "a breast cancer that makes the breast "
     "red, swollen and warm, often with skin like orange peel", True),
    (r"peau d.orange", "orange-peel skin (peau d'orange)", "dimpled, swollen skin like orange peel, a warning sign "
     "on the breast", True),
    (r"nipple (retraction|inversion of recent|newly inverted)|retracted nipple", "a pulled-in nipple", "a nipple "
     "that has newly turned in, a warning sign", True),
    (r"skin (dimpling|retraction|tethering)|dimpl\w* of the (skin|breast)", "dimpled skin", "skin pulled in over a "
     "lump, a warning sign", True),
    (r"nipple discharge|bloody discharge|galactorrh\w*", "nipple discharge", "fluid coming from a nipple when not "
     "breastfeeding", True),
    (r"breast abscess|subareolar abscess", "a breast abscess", "a painful collection of pus in the breast", False),
    (r"mastitis", "mastitis", "inflammation of the breast, which becomes red, warm and painful", False),
    (r"nipple eczema|eczema of the (nipple|areola)", "nipple eczema", "itchy, scaly skin on the nipple or areola",
     False),
    (r"gyn(a)?ecomastia", "gynaecomastia", "enlarged breast tissue in a man, common and usually harmless", False),
    (r"breast reconstruct\w*|reconstructed breast|implant", "a reconstructed breast", "a breast rebuilt after surgery",
     False),
    (r"mastectomy", "the chest after a mastectomy", "the operation that removes a breast; the scar and flat chest "
     "are expected", False),
    (r"lumpectomy|breast-conserving", "a breast after a lumpectomy", "the operation that removes a lump; a scar is "
     "expected", False),
    (r"breast (cancer|carcinoma|tumou?r|malignan\w*|mass|lump)|carcinoma of the breast|phyllodes",
     "a breast lump or tumour", "a lump or change in the breast that needs a doctor's examination", True),
    (r"fibroadenoma", "a fibroadenoma", "a common harmless lump in the breast", True),
    (r"(breast|mammary) cyst", "a breast cyst", "a fluid-filled lump, usually harmless", True),
]
CONDITIONS = [(re.compile(rf"\b({p})", re.I), name, why, warn) for p, name, why, warn in CONDITIONS]


def condition_in(*texts):
    """(plain name, explanation, warning sign?) of the first condition the texts name, or None."""
    text = " ".join(clean(t) for t in texts if t)
    for pattern, name, why, warn in CONDITIONS:
        if pattern.search(text):
            return name, why, warn
    return None


def looks_like(name, why):
    """ "This looks like X (explanation)." """
    return f"This looks like {name} ({why})." if why else f"This looks like {name}."


def sentence(text):
    """Text with a capital first letter and a full stop."""
    text = clean(text).strip(" ,;:")
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    return text if text.endswith((".", "!", "?")) else text + "."


def first_sentences(text, words=70, most=3):
    """The first sentences of text, at most about words words and most sentences."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", clean(text))
    out = []
    for part in parts[:most]:
        if out and len(" ".join(out + [part]).split()) > words:
            break
        out.append(part)
    text = " ".join(out)
    if len(text.split()) > words:
        text = " ".join(text.split()[:words]).rstrip(",;:") + " ..."
    return text


def skin_sentence(words):
    """The sentence for skin_from_text's words ("" when the source says nothing)."""
    if not words:
        return ""
    return sentence(f"It is {words}" if words.startswith("on ") else words)


def draft(lead, caption, condition_texts, extra="", skin_words=""):
    """A draft description: the lead ("A clinical photograph from ..."), the caption in plain words, "This looks like"
    when a condition is named, the skin type or ethnicity the source states (skin_words, from skin_from_text), extra,
    and the closing sentences (SEE_SOON for a warning sign, then DOCTOR)."""
    caption = sentence(plain(caption)) if caption else ""
    if clean(lead).endswith(":"):
        parts = [clean(lead)[0].upper() + clean(lead)[1:] + (" " + caption if caption else " (no caption).")]
    else:
        parts = [sentence(lead), caption]
    found = condition_in(*condition_texts)
    darker = bool(re.search(r"type (IV|V|VI)\)", skin_words or ""))
    if found:
        parts.append(looks_like(found[0], darker_skin_colours(found[1]) if darker else found[1]))
    if skin_words:
        parts.append(skin_sentence(skin_words))
    if extra:
        parts.append(sentence(extra))
    if found and found[2]:
        parts.append(SEE_SOON)
    parts.append(DOCTOR)
    return " ".join(p for p in parts if p)


# ----------------------------------------------------------------- downloading

def session():
    """A requests session with the kit's name (Wikimedia asks for one with a web address)."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def get(s, url, tries=4, **kwargs):
    """A GET that waits and tries again on errors and on "too many requests"; the response, or None."""
    for attempt in range(tries):
        try:
            r = s.get(url, timeout=kwargs.pop("timeout", 90), **kwargs)
            if r.status_code in (429, 502, 503, 504):
                time.sleep(min(60, 5 * (attempt + 1) * (attempt + 1)))
                continue
            return r
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(5 * (attempt + 1))
    return None


def get_json(s, url, **kwargs):
    """GET JSON; tries again when the answer is not JSON (Wikimedia's rate-limit page is plain text). None on fail."""
    for attempt in range(5):
        r = get(s, url, **kwargs)
        if r is None:
            return None
        try:
            return r.json()
        except ValueError:
            time.sleep(10 * (attempt + 1))
    return None


def jpeg(data):
    """JPEG bytes (at most LONG_SIDE pixels, the right way up, without the camera's hidden details), or None when it
    is not a picture or is smaller than SMALLEST pixels."""
    try:
        from PIL import Image, ImageOps
        with Image.open(io.BytesIO(data)) as picture:
            picture = ImageOps.exif_transpose(picture)
            if min(picture.size) < SMALLEST:
                return None
            picture = picture.convert("RGB")
            picture.thumbnail((LONG_SIDE, LONG_SIDE), Image.LANCZOS)
            out = io.BytesIO()
            picture.save(out, "JPEG", quality=90)
            return out.getvalue()
    except Exception:  # noqa: BLE001 - not a picture
        return None


def download_picture(s, url):
    """The JPEG bytes of the picture at url, or None."""
    r = get(s, url, timeout=120)
    if r is None or r.status_code != 200 or not r.content:
        return None
    if "html" in (r.headers.get("content-type") or "").lower():
        return None
    return jpeg(r.content)


# ----------------------------------------------------------------- the review workspace

class ReviewWorkspace:
    """A describing workspace filled by one review collection: adds pictures with a draft description and the status
    "needs another look", records credits, remembers what was tried, and writes the review instructions."""

    def __init__(self, folder, source, say=None):
        """Open (or make) the workspace in folder for source (one of REVIEW_SOURCES)."""
        self.source, self.say = source, say or (lambda text: None)
        self.workspace = dp.make_workspace(folder, f"Review only: {source['name']}")
        data = self.workspace.data
        data.update(review_only=True, content=source["content"], review_source=source["key"],
                    review_category=source["category"])
        self.workspace.save()
        self.folder = self.workspace.folder
        self.staging = os.path.join(self.folder, STAGING)
        self.waiting = []
        self.added = 0
        self.tried = set(self.read_tried())
        with open(os.path.join(self.folder, REVIEW_FILE), "w", encoding="utf-8", newline="\r\n") as f:
            f.write(REVIEW_INSTRUCTIONS.format(name=source["name"], credit=source["credit"],
                                               licence=f"{source['licence']} ({source['terms_summary']})"))

    def read_tried(self):
        """The ids tried in earlier runs."""
        try:
            with open(os.path.join(self.folder, TRIED_FILE), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return []

    def save_tried(self):
        """Remember the ids tried so far."""
        with open(os.path.join(self.folder, TRIED_FILE), "w", encoding="utf-8") as f:
            json.dump(sorted(self.tried), f)

    def count(self):
        """How many pictures the workspace holds (with those waiting to be added)."""
        return len(self.workspace.pictures) + len(self.waiting)

    def full(self, cap):
        """True when the workspace holds cap pictures."""
        return cap and self.count() >= cap

    def done(self, name):
        """True when this picture (by its file name, which is also its id) is there or was tried before."""
        return name in self.workspace.pictures or name in self.tried

    def mark_tried(self, name):
        """Remember that this picture was tried (kept, left out or failed), so a new run does not fetch it again."""
        self.tried.add(name)

    def add(self, name, data, text, credit, licence, page, content=None, note="", skin=GROUPS[3]):
        """Queue one picture (JPEG bytes) with its draft description, credit and skin-type group (GROUPS: only what
        the source states); added in batches."""
        os.makedirs(self.staging, exist_ok=True)
        with open(os.path.join(self.staging, name), "wb") as f:
            f.write(data)
        dp.write_file_text(os.path.join(self.staging, os.path.splitext(name)[0] + ".txt"), text)
        self.waiting.append((name, credit, licence, page, content or self.source["content"], note, skin))
        self.mark_tried(name)
        if len(self.waiting) >= BATCH:
            self.flush()

    def flush(self):
        """Add the queued pictures to the workspace and set each one to "needs another look" (never "described" or
        "checked"), with its credit, licence and source page in its notes and in CREDITS.txt."""
        if not self.waiting:
            self.save_tried()
            return
        files = [os.path.join(self.staging, n) for n, *_ in self.waiting]
        dp.add_pictures(self.workspace, files, person="")
        lines = []
        for name, credit, licence, page, content, note, skin in self.waiting:
            entry = self.workspace.pictures.get(name)
            if entry is None:
                continue                                  # the same picture was there already
            entry = self.workspace.entry(name)
            entry.update(status=dp.LOOK, described_by="", described_at="", checked_by="", checked_at="",
                         changed_at=dp.now(), content=content, review="review-only", skin_type=skin,
                         notes=clean(f"REVIEW ONLY. Draft description from the source's own caption or label; a "
                                     f"sighted, trusted adult must check it (see {REVIEW_FILE}). {note} "
                                     f"Credit: {credit}. Licence: {licence}. Source: {page}"))
            lines.append(f"{name}\t{credit}\t{licence}\t{page}\tskin type {skin}"
                         + ("\tINTIMATE" if content == "intimate" else ""))
            self.added += 1
        self.workspace.save()
        with open(os.path.join(self.folder, CREDITS_FILE), "a", encoding="utf-8", newline="\r\n") as f:
            if f.tell() == 0:
                f.write(f"Credits for {self.source['name']}\nfile\tcredit\tlicence\tsource page\tskin type "
                        f"(as the source states it)\n")
            f.write("\n".join(lines) + ("\n" if lines else ""))
        shutil.rmtree(self.staging, ignore_errors=True)
        self.waiting = []
        self.save_tried()
        self.say(f"{self.source['name']}: {len(self.workspace.pictures)} pictures in the review workspace.")

    def skin_counts(self):
        """{skin-type group: how many pictures} in the workspace (GROUPS; "not stated" when the source says none)."""
        found = {g: 0 for g in GROUPS}
        for entry in self.workspace.pictures.values():
            group = entry.get("skin_type") if entry.get("skin_type") in found else GROUPS[3]
            found[group] += 1
        return found

    def finish(self, found, left_out):
        """Add what is queued and give back a plain summary (with the count per skin-type group)."""
        self.flush()
        skins = self.skin_counts()
        self.workspace.data["skin_type_counts"] = skins
        self.workspace.save()
        summary = (f"{self.source['name']}: {self.added} new pictures added for review "
                   f"({len(self.workspace.pictures)} in the workspace); {found} records looked at, "
                   f"{left_out} left out by the adults-only, no-sexual-content and medical-only rules or because the "
                   f"picture could not be downloaded. Skin type as the source states it: "
                   + ", ".join(f"{g} {n}" for g, n in skins.items()) +
                   f". Every picture needs a check by a sighted, trusted adult before it can be used "
                   f"(see {REVIEW_FILE}).")
        self.say(summary)
        return summary


def fill(ws, items, cap, s, workers=4):
    """Download items [(name, url, text, credit, licence, page, content, note, skin group)] into the review
    workspace ws until it holds cap pictures; returns how many could not be downloaded."""
    failed = 0
    todo = [i for i in items if not ws.done(i[0])]
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for start in range(0, len(todo), workers * 4):
            if ws.full(cap):
                break
            chunk = todo[start:start + workers * 4]
            for item, data in zip(chunk, pool.map(lambda i: download_picture(s, i[1]), chunk)):
                if ws.full(cap):
                    break
                if data is None:
                    ws.mark_tried(item[0])
                    failed += 1
                    continue
                name, _url, text, credit, licence, page, content, note, skin = item
                ws.add(name, data, text, credit, licence, page, content, note, skin)
    return failed


# ----------------------------------------------------------------- CDC Public Health Image Library (public domain)

PHIL = "https://wwwn.cdc.gov/phil/"
PHIL_PUBLIC = "Permission is not required for public domain images"
PHIL_KEYWORDS = (
    "genital warts", "condylomata acuminata", "chancre", "primary syphilis", "secondary syphilis", "condylomata lata",
    "genital herpes", "herpes genitalis", "chancroid", "lymphogranuloma venereum", "granuloma inguinale",
    "donovanosis", "gonorrhea", "gonococcal", "chlamydia", "trichomoniasis", "balanitis", "candidiasis vulva",
    "vulvovaginal", "molluscum contagiosum", "pubic lice", "pediculosis pubis", "scabies penis", "mpox genital",
    "monkeypox genital", "penis", "penile", "scrotum", "scrotal", "vulva", "labia", "vaginal", "perineum",
    "tinea cruris", "breast", "nipple", "mastitis", "breast cancer")
PHIL_NOT_CLINICAL = re.compile(
    r"\b(micrograph\w*|microscop\w*|magnifi\w*|\d+x\b|TEM|SEM|electron|culture\w*|colon(y|ies)|agar|petri|slides?|"
    r"specimen\w*|stain\w*|graph|chart|maps?|posters?|illustration\w*|drawings?|diagrams?|cartoons?|infographic\w*|"
    r"vials?|laborator\w*|mosquito\w*|ticks?|fleas?|mites?|louse|lice|rats?|rodents?|virions?|smear\w*|gram)\b",
    re.I)


def phil_field(page, field):
    """One field of a PHIL details page (lblDesc, lblCopyRight, lblContprov, lblPhotoCredit)."""
    m = re.search(rf'<span id="{field}">(.*?)</span>\s*</td>', page, re.S)
    return no_tags(m.group(1)) if m else ""


def phil_search(s, keyword, most=300):
    """The PHIL ids (photos only) a keyword search finds, all result pages (the site pages with postbacks)."""
    page_url = PHIL + "QuickSearch.aspx"
    box = "ctl00$contentArea2$ucQuickSearch$txtQuickKeywords"

    def hidden(text):
        """The form's hidden fields."""
        return {m.group(1): html.unescape(m.group(2)) for m in
                re.finditer(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', text)}
    try:
        text = s.get(page_url, timeout=60).text
        text = s.post(page_url, timeout=120, data=dict(hidden(text), **{
            box: keyword, "ctl00$contentArea2$ucQuickSearch$bntSearch": "Search",
            "ctl00$contentArea2$ucQuickSearch$chkTypes$chkTypes_0": "Photo"})).text
    except Exception:  # noqa: BLE001 - nothing found
        return []
    ids, page = [], 1
    while len(ids) < most:
        ids += [p for p in dict.fromkeys(re.findall(r"Details\.aspx\?pid=(\d+)", text)) if p not in ids]
        links = re.findall(r"__doPostBack\(&#39;([^&]+dpImages[^&]+)&#39;,&#39;&#39;\)\">(\d+|\.\.\.)<", text)
        nxt = [t for t, n in links if n == str(page + 1)] or [t for t, n in links if n == "..."][-1:]
        if not nxt or page > 40:
            break
        try:
            text = s.post(page_url, timeout=120, data=dict(hidden(text), **{"__EVENTTARGET": nxt[0],
                                                                            "__EVENTARGUMENT": "", box: keyword})).text
        except Exception:  # noqa: BLE001 - what was found so far
            break
        page += 1
        time.sleep(0.5)
    return ids


def phil_record(s, pid):
    """{"caption", "public", "picture"} for one PHIL item, or None."""
    r = get(s, f"{PHIL}Details.aspx?pid={pid}")
    if r is None or r.status_code != 200:
        return None
    page = r.text
    picture = re.search(r'(?:src|href)="([^"]*PHIL_Images/[^"]*_lores\.jpg)"', page, re.I)
    rights = phil_field(page, "lblCopyRight")
    who = f"{phil_field(page, 'lblContprov')} {phil_field(page, 'lblPhotoCredit')}"
    public = rights.startswith(PHIL_PUBLIC) and "copyright protected" not in rights.lower() \
        and "©" not in who and "copyright" not in who.lower()
    url = re.sub(r"(?<!:)/{2,}", "/", picture.group(1)) if picture else ""
    if url and not url.startswith("http"):
        url = "https://phil.cdc.gov" + ("" if url.startswith("/") else "/") + url
    return {"caption": phil_field(page, "lblDesc"), "public": public, "picture": url,
            "credit": clean(who) or "CDC"}


def fetch_cdc_phil_intimate(folder, cap, say=print):
    """CDC PHIL: public-domain clinical photographs of genital and breast conditions (STIs, thrush, balanitis,
    mastitis, breast cancer signs). Only items whose own copyright field says public domain; only captions that name
    the genitals or breasts, are clinical photographs (not microscope pictures, posters or insects), name no child
    (congenital syphilis is left out by the word "congenital"), give no age under 18 and nothing sexual. PHIL captions
    rarely give an age, so the review must confirm the person is an adult."""
    source = source_by_key("cdc_phil_intimate")
    ws, s = ReviewWorkspace(folder, source, say), session()
    lists = []
    for keyword in PHIL_KEYWORDS:
        found = phil_search(s, keyword, most=max(20, cap))
        lists.append(found)
        say(f"CDC PHIL: '{keyword}': {len(found)} photos")
    ids = []                                     # taking turns between the searches, so every condition has a share
    while any(lists):
        for found in lists:
            if found:
                pid = found.pop(0)
                if pid not in ids:
                    ids.append(pid)
    looked = left = 0
    for pid in ids:
        if ws.full(cap):
            break
        name = f"phil-{pid}.jpg"
        if ws.done(name):
            continue
        looked += 1
        record = phil_record(s, pid)
        caption = record["caption"] if record else ""
        if not record or not record["public"] or not record["picture"] or not child_free(caption) \
                or not not_sexual(caption) or PHIL_NOT_CLINICAL.search(caption) \
                or not (GENITAL.search(first_sentences(caption, 60, 2)) or BREAST.search(first_sentences(caption, 60,
                                                                                                     2))):
            ws.mark_tried(name)
            left += 1
            continue
        data = download_picture(s, record["picture"])
        if data is None:
            ws.mark_tried(name)
            left += 1
            continue
        text = first_sentences(caption, 60, 2)
        page = f"https://phil.cdc.gov/Details.aspx?pid={pid}"
        skin, skin_words = skin_from_text(caption)
        ws.add(name, data, draft("A clinical photograph from the US Centers for Disease Control and Prevention. "
                                 "The CDC's caption says:", text, [text, caption], skin_words=skin_words),
               f"CDC Public Health Image Library, ID {pid}, {record['credit']}", "public domain (US government work)",
               page, note="No age given: confirm the person is an adult. Skin type: "
                          + (skin_words or "not stated by the source; note it if you can see it plainly."), skin=skin)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- PubMed Central case reports (CC BY or CC0)

EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PMC_S3 = "https://pmc-oa-opendata.s3.amazonaws.com/"
PMC_FREE = {"CC BY": "CC BY", "CC0": "CC0"}       # PMC's own licence codes allowed (never NC, ND or SA)
PMC_BASE = ('IN_PMC:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND (PUB_TYPE:"Case Reports" OR TITLE:"case report" '
            'OR TITLE:"case series" OR PUB_TYPE:"Review") AND ')
PMC_GENITAL = PMC_BASE + (
    '(TITLE:penile OR TITLE:penis OR TITLE:scrotal OR TITLE:scrotum OR TITLE:vulvar OR TITLE:vulval OR TITLE:vulva '
    'OR TITLE:labial OR TITLE:"labia minora" OR TITLE:genital OR TITLE:balanitis OR TITLE:"lichen sclerosus" OR '
    'TITLE:"pearly penile" OR TITLE:fordyce OR TITLE:"vestibular papillomatosis" OR TITLE:condyloma OR '
    'TITLE:chancre OR TITLE:varicocele OR TITLE:hydrocele OR TITLE:phimosis OR TITLE:prepuce OR TITLE:foreskin OR '
    'TITLE:glans OR TITLE:angiokeratoma OR TITLE:"genital herpes" OR TITLE:syphilis OR TITLE:"Bartholin")')
PMC_BREAST = PMC_BASE + (
    '(TITLE:breast OR TITLE:nipple OR TITLE:areola OR TITLE:gynecomastia OR TITLE:gynaecomastia OR TITLE:mastitis '
    'OR TITLE:mastectomy OR TITLE:"Paget" OR TITLE:polythelia OR TITLE:"accessory breast")')
# Skin of colour, searched on purpose: articles that speak of darker skin, and articles by authors in Africa, South
# Asia, East and Southeast Asia, Latin America and the Middle East (where most patients have darker skin).
SKIN_OF_COLOUR = ('("skin of color" OR "skin of colour" OR "dark skin" OR "darker skin" OR "pigmented skin" OR '
                  '"black skin" OR "Fitzpatrick" OR "skin phototype" OR "skin type V" OR "skin type VI" OR '
                  '"African American" OR "ethnic skin")')
REGIONS = ('(AFF:Nigeria OR AFF:Ghana OR AFF:Kenya OR AFF:"South Africa" OR AFF:Ethiopia OR AFF:Uganda OR '
           'AFF:Tanzania OR AFF:Cameroon OR AFF:Senegal OR AFF:Sudan OR AFF:Egypt OR AFF:Morocco OR AFF:Tunisia OR '
           'AFF:India OR AFF:Pakistan OR AFF:Bangladesh OR AFF:"Sri Lanka" OR AFF:Nepal OR AFF:China OR AFF:Japan '
           'OR AFF:Korea OR AFF:Thailand OR AFF:Vietnam OR AFF:Indonesia OR AFF:Malaysia OR AFF:Philippines OR '
           'AFF:Brazil OR AFF:Mexico OR AFF:Colombia OR AFF:Peru OR AFF:Chile OR AFF:Argentina OR AFF:"Saudi Arabia" '
           'OR AFF:Iran OR AFF:Iraq OR AFF:Jordan OR AFF:Lebanon OR AFF:Qatar OR AFF:Oman OR AFF:Turkey)')
PMC_QUERIES = [("genital, skin of colour", f"{PMC_GENITAL} AND {SKIN_OF_COLOUR}"),
               ("breast, skin of colour", f"{PMC_BREAST} AND {SKIN_OF_COLOUR}"),
               ("genital, Africa, Asia, Latin America, Middle East", f"{PMC_GENITAL} AND {REGIONS}"),
               ("breast, Africa, Asia, Latin America, Middle East", f"{PMC_BREAST} AND {REGIONS}"),
               ("genital", PMC_GENITAL), ("breast", PMC_BREAST)]
NOT_PHOTO = re.compile(
    r"\b(histolog\w*|histopatholog\w*|H&E|hematoxylin|haematoxylin|immunohisto\w*|immunostain\w*|microscop\w*|"
    r"magnification|cytolog\w*|smear|stain(ed|ing)?|CT|computed tomograph\w*|MRI|MR imag\w*|magnetic resonance|"
    r"ultraso\w*|sonograph\w*|doppler|mammogra\w*|tomosynthesis|x-?rays?|radiograph\w*|PET|scintigra\w*|"
    r"angiogra\w*|chart|graph|diagram|schematic|flow ?chart|algorithm|table|illustration|drawing|timeline|kaplan|"
    r"western blot|sequenc\w+|pedigree|cartoon|[x×] ?\d{2,4}\b|\d{2,4} ?[x×])", re.I)
IS_PHOTO = re.compile(
    r"\b(photograph\w*|photos?|clinical (appearance|image|picture|presentation|view|aspect|features?)|appearance|"
    r"on examination|physical examination|close-up|view of|lesions?|ulcers?|nodules?|mass|swelling|plaques?|"
    r"papules?|rash|erythema\w*|patch(es)?|post-?operative\w*|pre-?operative\w*|intra-?operative\w*|after "
    r"(surgery|treatment)|before (surgery|treatment)|follow-?up|reconstruct\w*|dermoscop\w*|colposcop\w*)\b", re.I)


def europe_pmc(s, query, want):
    """Europe PMC search results (title, abstract, authors) for a query, newest first, until want results."""
    out, cursor = [], "*"
    while len(out) < want:
        data = get_json(s, EUROPE_PMC, params={"query": query, "format": "json", "resultType": "core",
                                               "pageSize": 500, "cursorMark": cursor, "sort": "P_PDATE_D desc"},
                        timeout=180)
        if not data:
            break
        results = (data.get("resultList") or {}).get("result") or []
        out += [r for r in results if r.get("pmcid")]
        if not results or data.get("nextCursorMark") in (None, cursor):
            break
        cursor = data["nextCursorMark"]
        time.sleep(1)
    return out


def pmc_article(s, pmcid):
    """(PMC's own metadata, article XML) from PMC's open-access bucket (the newest version), or (None, None)."""
    r = get(s, PMC_S3, params={"list-type": "2", "prefix": f"metadata/{pmcid}.", "max-keys": 20}, timeout=60)
    keys = re.findall(r"<Key>(metadata/[^<]+\.json)</Key>", r.text) if r is not None else []
    if not keys:
        return None, None
    key = max(keys, key=lambda k: int((re.search(r"\.(\d+)\.json$", k) or re.search(r"()$", k)).group(1) or 0))
    meta = get_json(s, PMC_S3 + key, timeout=60)
    if not meta or not meta.get("xml_url"):
        return None, None
    r = get(s, meta["xml_url"].replace("s3://pmc-oa-opendata/", PMC_S3).split("?")[0], timeout=120)
    return (meta, r.text) if r is not None and r.status_code == 200 else (None, None)


def pmc_figures(xml, meta):
    """[(label, caption, picture address)] for the one-picture figures of an article."""
    media = {}
    for url in meta.get("media_urls") or []:
        file = url.split("?")[0].rsplit("/", 1)[-1]
        stem, ext = file.rsplit(".", 1) if "." in file else (file, "")
        if ext.lower() in ("jpg", "jpeg", "png", "gif", "webp", "tif", "tiff") and \
                (stem not in media or ext.lower() in ("jpg", "jpeg")):     # a JPEG first when there are two
            media[stem] = url.replace("s3://pmc-oa-opendata/", PMC_S3).split("?")[0]
    out = []
    for fig in re.findall(r"<fig\b.*?</fig>", xml, re.S):
        graphics = re.findall(r'<graphic\b[^>]*xlink:href="([^"]+)"', fig)
        if len(graphics) != 1:
            continue
        stem = graphics[0].rsplit("/", 1)[-1]
        stem = stem.rsplit(".", 1)[0] if re.search(r"\.(jpe?g|png|gif|webp|tiff?)$", stem, re.I) else stem
        if stem not in media:
            continue
        label = no_tags(re.search(r"<label>(.*?)</label>", fig, re.S).group(1)) if "<label>" in fig else ""
        caption = re.search(r"<caption>(.*?)</caption>", fig, re.S)
        out.append((label, no_tags(caption.group(1)) if caption else "", media[stem]))
    return out


SEX_WORD = re.compile(r"\b(man|male|gentleman|woman|female|lady)\b", re.I)


def who_from(text, age):
    """ "a 45-year-old man" (or "an adult" when the age is not known)."""
    if not age:
        return "an adult"
    m = re.search(rf"\b{age}[- ](?:year|yr)s?[- ]old\s+(\w+)", text, re.I)
    sex = SEX_WORD.search(m.group(1)) if m else None
    sex = {"man": "man", "male": "man", "gentleman": "man"}.get(sex.group(1).lower(), "woman") if sex else "person"
    article = "an" if str(age).startswith("8") or str(age) in ("11", "18") else "a"
    return f"{article} {age}-year-old {sex}"


def pmc_items(s, record):
    """[(name, url, text, credit, licence, page, content, note)] for the usable figures of one article."""
    title, abstract = no_tags(record.get("title")), no_tags(record.get("abstractText"))
    if not child_free(title, abstract) or not not_sexual(title, abstract):
        return []
    adult_article, age = adult_shown(title, abstract)
    if adult_article and not ages(f"{title} {abstract}"):
        adult_article = False                            # an adult word alone is not enough for an article
    meta, xml = pmc_article(s, record["pmcid"])
    if not meta or meta.get("license_code") not in PMC_FREE or meta.get("is_retracted"):
        return []
    licence = PMC_FREE[meta["license_code"]]
    authors = clean(record.get("authorString"))
    if len(authors) > 120:
        authors = authors[:authors.rfind(",", 0, 120)] + " et al."
    page = f"https://pmc.ncbi.nlm.nih.gov/articles/{meta['pmcid']}/"
    out = []
    for label, caption, url in pmc_figures(xml, meta):
        words = len(caption.split())
        if words < 5 or not child_free(caption) or not not_sexual(caption) or NOT_PHOTO.search(caption) \
                or not IS_PHOTO.search(caption):
            continue
        if not (GENITAL.search(caption) or BREAST.search(caption) or GENITAL.search(title) or BREAST.search(title)):
            continue
        ok, caption_age = adult_shown(caption)
        if not adult_article and not (ok and ages(caption)):
            continue                                     # no age of 18 or more in the title, abstract or caption
        who = who_from(f"{title} {abstract}", age) if adult_article else who_from(caption, caption_age)
        name = f"pmc-{meta['pmcid']}-{re.sub(r'[^A-Za-z0-9]+', '_', label or url.rsplit('/', 1)[-1])[:30]}.jpg"
        credit = (f"{authors}, \"{title.rstrip('.')}\", {clean(meta.get('citation'))}, {label or 'figure'}")
        skin, skin_words = skin_from_text(caption, title, abstract)
        text = draft(f"A clinical picture from a published medical case report about {who}. The authors' caption "
                     "says:", first_sentences(caption, 80, 3), [caption, title], skin_words=skin_words)
        out.append((name, url, text, credit, licence, page, "intimate",
                    "Skin type: " + (skin_words or "not stated by the authors."), skin))
    return out[:3]                                        # at most three figures of one article


def fetch_pmc_intimate(folder, cap, say=print):
    """PubMed Central: figures of case reports and reviews about adult genital and breast conditions and normal
    variants, licence CC BY or CC0 checked in PMC's own metadata. Adults only: the title or abstract gives the
    patient's age as 18 or more, or (for reviews) the caption does; no child words anywhere; clinical photographs
    only (no scans, X-rays, mammograms, microscope pictures or charts); nothing sexual."""
    source = source_by_key("pmc_intimate")
    ws, s = ReviewWorkspace(folder, source, say), session()
    want = max(60, cap * 2)
    lists = []
    for what, query in PMC_QUERIES:
        found = europe_pmc(s, query, want)
        say(f"Europe PMC: {len(found)} articles ({what})")
        lists.append(found)
    # Taking turns between the searches, so skin of colour, both body areas and every region have their share;
    # an article found twice is used once.
    records, seen = [], set()
    while any(lists):
        for found in lists:
            if found:
                record = found.pop(0)
                if record["pmcid"] not in seen:
                    seen.add(record["pmcid"])
                    records.append(record)
    looked = left = 0
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for start in range(0, len(records), 16):
            if ws.full(cap):
                break
            chunk = [r for r in records[start:start + 16] if f"article-{r['pmcid']}" not in ws.tried]
            for record, items in zip(chunk, pool.map(lambda r: pmc_items(s, r), chunk)):
                ws.mark_tried(f"article-{record['pmcid']}")
                looked += 1
                left += not items
                left += fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


# ----------------------------------------------------------------- Wikimedia Commons (licence per file)

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
# (category, needs an adult shown in its text, needs a genital or breast word in its text). Only these categories
# are read (no sub-categories), and only files whose own text is clearly medical or anatomical.
COMMONS_CATEGORIES = [
    ("Human penis (medical)", False, False), ("Anatomy of the human penis", False, False),
    ("Circumcised and uncircumcised human penises in comparison", True, False), ("Human penis", False, False),
    ("Human glans penis", False, False), ("Human foreskin", True, False), ("Human scrotum", False, False),
    ("Human testicles", False, False), ("Human vulva", False, False), ("Labia minora", False, False),
    ("Fordyce's spots on human penis", False, False), ("Fordyce's spots on scrotum", False, False),
    ("Fordyce's spots on vulva", False, False), ("Genital warts", False, False), ("Anal condylomata", False, False),
    ("Genital herpes", False, False), ("Primary syphilis", False, False), ("Syphilis", False, True),
    ("Chancroid", False, False), ("Donovanosis", False, False), ("Lymphogranuloma venereum", False, False),
    ("Lichen sclerosus", False, False), ("Balanitis", False, False), ("Balanitis xerotica obliterans", False, False),
    ("Bartholin's cyst", False, False), ("Varicocele", False, False), ("Hydrocele", True, False),
    ("Phimosis", True, False), ("Paraphimosis", True, False), ("Penile cancer", False, False),
    ("Vulvar cancer", False, False), ("Pubic lice", False, False), ("Tinea cruris", False, False),
    ("Molluscum contagiosum", True, True), ("Mpox", False, True), ("Candidiasis", False, True),
    ("Diseases and disorders of the penis", False, False),
    ("Gynecomastia", True, False), ("Mastectomy", False, False), ("Breast reconstruction", False, False),
    ("Mastitis", False, False), ("Breast abscess", False, False), ("Paget's disease of the breast", False, False),
    ("Supernumerary nipples", False, False), ("Diseases and disorders of the breast", False, False),
    ("Breast cancer", False, True), ("Human nipples", False, False), ("Stretch marks", False, True),
]
# A file's own text must have one of these words (or name a condition in CONDITIONS) to count as medical.
MEDICAL_WORDS = re.compile(
    r"\b(anatom\w*|medical|medicine|clinical|clinic|patients?|diagnos\w*|diseases?|disorders?|conditions?|"
    r"infections?|infected|symptoms?|signs? of|normal|variation|variant|diversity|examination|dermatolog\w*|"
    r"urolog\w*|gyn(a)?ecolog\w*|surg\w*|post-?operative|operation|scars?|lesions?|rash|ulcers?|cysts?|tumou?rs?|"
    r"cancer|carcinoma|swelling|inflammation|diagram|textbook|atlas|health|education\w*)\b", re.I)
NOT_EDUCATIONAL = re.compile(r"\b(ribbons?|logos?|awareness|posters?|stamps?|march|walk|race|run|campaign|"
                             r"fundrais\w*|t-shirts?|merchandise|pink ribbon|celebrit\w*|portrait|protest\w*)\b",
                             re.I)
# Not a picture of a body: microscope and laboratory pictures (useful elsewhere, not for describing a body).
LABORATORY = re.compile(r"\b(\w*micrograph\w*|microscop\w*|histolog\w*|histopatholog\w*|stain\w*|gram-|magnif\w*|"
                        r"smear\w*|culture\w*|petri|agar|specimen\w*|slides?|bacteri(um|a) under)\b", re.I)
OPEN_LICENCE = re.compile(r"^(cc0|cc-zero|public domain|pd\b|pd-|cc by \d|cc-by-\d|cc by-\d|attribution$)", re.I)
SHARE_ALIKE = re.compile(r"^(cc by-sa|cc-by-sa)", re.I)


def commons_licence_kind(licence):
    """ "open" (CC0, public domain, CC BY), "share-alike" (CC BY-SA) or "" (anything else: left out)."""
    licence = clean(licence)
    if re.search(r"\b(nc|nd)\b|non-?commercial|no ?deriv", licence, re.I):
        return ""
    if SHARE_ALIKE.match(licence):
        return "share-alike"
    if OPEN_LICENCE.match(licence) and "SA" not in licence.upper().replace("USA", ""):
        return "open"
    return ""


def commons_items(s, category, needs_adult, needs_topic, kind, say):
    """[(name, url, text, credit, licence, page, content, note)] for the usable files of one Commons category whose
    licence is of kind ("open" or "share-alike"); (items, looked at, left out)."""
    params = {"action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": f"Category:{category}",
              "gcmtype": "file", "gcmlimit": 50, "prop": "imageinfo", "iiprop": "url|extmetadata|mime",
              "iiurlwidth": 1600, "maxlag": 5,
              "iiextmetadatafilter": "LicenseShortName|ImageDescription|Artist|Categories|ObjectName"}
    items, looked, left = [], 0, 0
    while True:
        data = get_json(s, COMMONS_API, params=params)
        if not data:
            break
        for p in (data.get("query") or {}).get("pages", {}).values():
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}

            def value(k, meta=meta):
                """One extmetadata field as plain text."""
                return no_tags((meta.get(k) or {}).get("value"))
            title = p.get("title", "")[5:]
            description, categories = value("ImageDescription"), value("Categories")
            licence = value("LicenseShortName")
            looked += 1
            text = f"{title} {value('ObjectName')} {description}"
            if commons_licence_kind(licence) != kind:
                continue                                  # counted in the other Commons collection
            mime = info.get("mime", "")
            ok = (mime.startswith("image/") and "gif" not in mime and info.get("thumburl")
                  and child_free(text, categories) and not_sexual(text) and not BLOCKED_CATEGORY.search(categories)
                  and not NOT_EDUCATIONAL.search(text) and not LABORATORY.search(f"{text} {categories}")
                  and len(re.findall(r"\w+", description)) >= 3
                  and (MEDICAL_WORDS.search(text) or condition_in(text))
                  and (not needs_topic or GENITAL.search(text) or BREAST.search(text))
                  and (not needs_adult or adult_shown(text)[0]))
            if not ok:
                left += 1
                continue
            drawn = bool(re.search(r"\b(diagram|drawing|illustration|svg|scheme|textbook)\b", text, re.I)) \
                or mime == "image/svg+xml"
            lead = ("A medical drawing" if drawn else "A medical photograph") + \
                f" from Wikimedia Commons (category: {category}). Its description says:"
            caption = first_sentences(re.sub(r"^(English|en)[:\s]+", "", description) or
                                      os.path.splitext(title)[0].replace("_", " "), 60, 2)
            artist = value("Artist") or "unknown"
            skin, skin_words = skin_from_text(text)
            items.append((f"commons-{p['pageid']}.jpg", info["thumburl"],
                          draft(lead, caption, [text, category], skin_words=skin_words),
                          f"{title} by {artist[:120]}, via Wikimedia Commons", licence,
                          "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_"), "intimate",
                          ("" if adult_shown(text)[0] else "No age given: confirm the person is an adult. ")
                          + "Skin type: " + (skin_words or "not stated by the source."), skin))
        if "continue" not in data:
            break
        params.update(data["continue"])
        time.sleep(1)
    say(f"Commons '{category}': {len(items)} usable files")
    return items, looked, left


def commons_fetch(key, kind, folder, cap, say):
    """Fill the review workspace of collection key with Commons files of licence kind from COMMONS_CATEGORIES."""
    source = source_by_key(key)
    ws, s = ReviewWorkspace(folder, source, say), session()
    looked = left = 0
    lists = []
    for category, needs_adult, needs_topic in COMMONS_CATEGORIES:
        items, n, m = commons_items(s, category, needs_adult, needs_topic, kind, say)
        lists.append(items)
        looked, left = looked + n, left + m
        time.sleep(1)
    # Taking turns between the categories, so every condition and body area has its share; skin types are taken
    # in turns too where a file's text states one.
    items, seen = [], set()
    while any(lists):
        for found in lists:
            if found:
                item = found.pop(0)
                if item[0] not in seen:
                    seen.add(item[0])
                    items.append(item)
    items = balanced(items, lambda i: i[8], lambda i: "")
    left += fill(ws, items, cap, s, workers=2)
    return ws.finish(looked, left)


def fetch_commons_intimate(folder, cap, say=print):
    """Wikimedia Commons, CC0, public domain or CC BY files (licence checked per file) from medical and anatomy
    categories of the genitals and breasts (COMMONS_CATEGORIES; no sub-categories). Only files whose own title and
    description are clearly medical or anatomical, in no sexual, erotic, art, nudity-culture or body-modification
    category, naming no child. Commons gives no ages: the review must confirm the person is an adult (where a
    condition is common in children, the file's text must show an adult)."""
    return commons_fetch("commons_intimate", "open", folder, cap, say)


def fetch_commons_intimate_sa(folder, cap, say=print):
    """The same as fetch_commons_intimate, for CC BY-SA files (share-alike)."""
    return commons_fetch("commons_intimate_sa", "share-alike", folder, cap, say)


# ----------------------------------------------------------------- Fitzpatrick17k (the whole set, for review)

FITZ_CSV = "https://raw.githubusercontent.com/mattgroh/fitzpatrick17k/main/fitzpatrick17k.csv"
# Labels that usually mean a child: left out before review.
FITZ_EXCLUDED_LABELS = {
    "juvenile xanthogranuloma": "a condition of babies and young children",
    "congenital nevus": "a birthmark, pictures mostly of babies and children",
    "aplasia cutis": "missing skin at birth, pictures of newborns",
    "incontinentia pigmenti": "a condition seen in newborn girls",
    "acrodermatitis enteropathica": "pictures mostly of infants",
    "port wine stain": "a birthmark, pictures mostly of babies and children",
    "lymphangioma": "pictures mostly of children",
    "epidermolysis bullosa": "pictures mostly of babies and children",
    "langerhans cell histiocytosis": "pictures mostly of children",
    "nevus sebaceous of jadassohn": "a birthmark, pictures mostly of children",
    "xeroderma pigmentosum": "pictures mostly of children",
    "urticaria pigmentosa": "pictures mostly of children",
    "epidermal nevus": "a birthmark, pictures mostly of children",
    "pilomatricoma": "pictures mostly of children",
    "tuberous sclerosis": "pictures often of children",
    "naevus comedonicus": "a birthmark (the atlas files it under congenital naevi)",
}
FITZ_GENITAL_LABELS = {"fordyce spots", "hidradenitis", "lichen planus", "lichen sclerosus", "scabies",
                       "psoriasis", "lichen simplex", "neurodermatitis", "folliculitis"}
# Labels that are always a genital site (their pictures are tagged intimate whatever the address says).
FITZ_ALWAYS_GENITAL = {"fordyce spots"}
FITZ_SITE = re.compile(r"\b(genital|penis|penile|glans|scrotum|scrotal|vulva|vulvar|vulval|labia|perianal|anal|"
                       r"groin|inguinal|buttocks?|gluteal|breasts?|nipples?|areola|axilla|axillary|face|facial|"
                       r"scalp|nails?|hands?|palms?|feet|foot|soles?|legs?|arms?|trunk|back|lips?|oral|mouth|"
                       r"tongue|eyelids?|lids|eyes?|ears?|nose|neck|fingers?|toes?|knees?|elbows?|chest|abdomen)\b",
                       re.I)
FITZ_SITE_WORDS = {"genital": "the genitals", "penis": "the penis", "penile": "the penis", "glans": "the penis",
                   "scrotum": "the scrotum", "scrotal": "the scrotum", "vulva": "the vulva", "vulvar": "the vulva",
                   "vulval": "the vulva", "labia": "the labia", "perianal": "the skin around the anus",
                   "anal": "the skin around the anus", "groin": "the groin", "inguinal": "the groin",
                   "buttock": "the buttocks", "buttocks": "the buttocks", "gluteal": "the buttocks",
                   "axilla": "the armpit", "axillary": "the armpit", "oral": "the mouth", "lids": "the eyelids",
                   "facial": "the face"}
FITZ_INTIMATE_SITES = {"the genitals", "the penis", "the scrotum", "the vulva", "the labia",
                       "the skin around the anus", "the buttocks", "the breast", "the breasts", "the nipple",
                       "the nipples", "the areola"}
# label: (plain name, explanation)
FITZ_PLAIN = {
    "acanthosis nigricans": ("acanthosis nigricans", "dark, velvety skin in body folds, often linked to insulin"),
    "acne": ("acne", "spots, blackheads and bumps from blocked hair roots"),
    "acne vulgaris": ("acne", "spots, blackheads and bumps from blocked hair roots"),
    "acquired autoimmune bullous diseaseherpes gestationis": ("pemphigoid gestationis",
                                                              "an itchy blistering rash in pregnancy"),
    "actinic keratosis": ("actinic keratosis", "a rough, scaly patch from sun damage that can become a cancer"),
    "allergic contact dermatitis": ("allergic contact dermatitis", "an itchy rash where the skin touched something "
                                    "it is allergic to"),
    "basal cell carcinoma": ("basal cell carcinoma", "a common, slow-growing skin cancer"),
    "basal cell carcinoma morpheiform": ("basal cell carcinoma (morpheaform)", "a scar-like type of a common skin "
                                         "cancer"),
    "becker nevus": ("a Becker naevus", "a large, harmless brown patch, often hairy"),
    "behcets disease": ("Behcet's disease", "an inflammatory illness with mouth and genital sores"),
    "calcinosis cutis": ("calcinosis cutis", "hard chalky lumps of calcium in the skin"),
    "cheilitis": ("cheilitis", "sore, cracked, inflamed lips"),
    "dariers disease": ("Darier's disease", "an inherited condition with greasy, crusted bumps"),
    "dermatofibroma": ("a dermatofibroma", "a harmless firm bump in the skin"),
    "dermatomyositis": ("dermatomyositis", "an illness with a purplish rash and muscle weakness"),
    "disseminated actinic porokeratosis": ("disseminated superficial actinic porokeratosis", "many small "
                                           "ring-shaped scaly spots on sun-exposed skin"),
    "drug eruption": ("a drug rash", "a rash caused by a medicine"),
    "drug induced pigmentary changes": ("skin colour changes from a medicine", "darker or bluish patches caused by a "
                                        "medicine"),
    "dyshidrotic eczema": ("dyshidrotic eczema", "itchy small blisters on the hands or feet"),
    "eczema": ("eczema", "dry, itchy, inflamed skin"),
    "ehlers danlos syndrome": ("Ehlers-Danlos syndrome", "an inherited condition with very stretchy skin and loose "
                               "joints"),
    "erythema annulare centrifigum": ("erythema annulare centrifugum", "red rings that slowly spread outwards"),
    "erythema elevatum diutinum": ("erythema elevatum diutinum", "firm red-brown bumps over the joints"),
    "erythema multiforme": ("erythema multiforme", "a rash of target-shaped spots, often after an infection"),
    "erythema nodosum": ("erythema nodosum", "tender red lumps, usually on the shins"),
    "factitial dermatitis": ("factitious dermatitis", "skin damage a person causes themselves"),
    "fixed eruptions": ("a fixed drug eruption", "a round dark patch that comes back in the same place after a "
                        "medicine"),
    "folliculitis": ("folliculitis", "inflamed hair roots, small red or pus-filled bumps"),
    "fordyce spots": ("Fordyce spots", "harmless tiny pale yellow or white spots, oil glands seen through the skin "
                      "of the lips or genitals, a normal variant"),
    "granuloma annulare": ("granuloma annulare", "harmless rings of small smooth bumps"),
    "granuloma pyogenic": ("a pyogenic granuloma", "a harmless red lump that bleeds easily"),
    "hailey hailey disease": ("Hailey-Hailey disease", "an inherited condition with sore, cracked patches in "
                              "skin folds"),
    "halo nevus": ("a halo naevus", "a mole with a pale ring around it, usually harmless"),
    "hidradenitis": ("hidradenitis suppurativa", "a long-lasting condition with painful lumps in the armpits and "
                     "groin"),
    "ichthyosis vulgaris": ("ichthyosis vulgaris", "dry, scaly skin like fish scales"),
    "kaposi sarcoma": ("Kaposi sarcoma", "a cancer with purple or brown patches or lumps"),
    "keloid": ("a keloid", "a raised, overgrown scar"),
    "keratosis pilaris": ("keratosis pilaris", "harmless rough little bumps, usually on the upper arms"),
    "lentigo maligna": ("lentigo maligna", "a slowly spreading brown patch that is an early melanoma"),
    "lichen amyloidosis": ("lichen amyloidosis", "itchy brown bumps, usually on the shins"),
    "lichen planus": ("lichen planus", "an inflammatory condition with purplish bumps or white lacy patches"),
    "lichen simplex": ("lichen simplex", "thickened skin from long-term scratching"),
    "livedo reticularis": ("livedo reticularis", "a purple net-like pattern on the skin"),
    "lupus erythematosus": ("lupus", "an autoimmune condition that can cause red, scaly or scarring patches"),
    "lupus subacute": ("subacute lupus", "red ring-shaped or scaly patches on sun-exposed skin"),
    "lyme disease": ("Lyme disease", "a tick-borne infection; the rash often looks like a bull's-eye"),
    "malignant melanoma": ("a melanoma", "a serious skin cancer that often looks like an unusual mole"),
    "melanoma": ("a melanoma", "a serious skin cancer that often looks like an unusual mole"),
    "milia": ("milia", "harmless tiny white bumps"),
    "mucinosis": ("mucinosis", "bumps or patches from a build-up of mucin in the skin"),
    "mucous cyst": ("a mucous cyst", "a harmless soft fluid-filled bump"),
    "mycosis fungoides": ("mycosis fungoides", "a slow lymphoma of the skin with red scaly patches"),
    "myiasis": ("myiasis", "an infestation of the skin with fly larvae"),
    "necrobiosis lipoidica": ("necrobiosis lipoidica", "shiny yellow-brown patches on the shins, linked to diabetes"),
    "nematode infection": ("a roundworm infection", "a winding, itchy track or rash from worms in the skin"),
    "neurodermatitis": ("neurodermatitis", "thickened, itchy skin from long-term scratching"),
    "neurofibromatosis": ("neurofibromatosis", "an inherited condition with soft lumps and coffee-coloured patches"),
    "neurotic excoriations": ("skin-picking marks", "sores from repeated picking"),
    "neutrophilic dermatoses": ("a neutrophilic dermatosis", "painful red plaques or ulcers from inflammation"),
    "nevocytic nevus": ("a mole", "a common, usually harmless brown spot"),
    "papilomatosis confluentes and reticulate": ("confluent and reticulated papillomatosis", "brown scaly patches "
                                                 "in a net pattern on the chest or back"),
    "paronychia": ("paronychia", "an infection of the skin around a nail"),
    "pediculosis lids": ("lice on the eyelashes", "tiny insects and their eggs on the lashes"),
    "perioral dermatitis": ("perioral dermatitis", "a rash of small red bumps around the mouth"),
    "photodermatoses": ("a sun-related rash", "a rash on skin exposed to the sun"),
    "pilar cyst": ("a pilar cyst", "a harmless smooth lump, usually on the scalp"),
    "pityriasis lichenoides chronica": ("pityriasis lichenoides chronica", "small scaly red-brown spots that come and "
                                        "go"),
    "pityriasis rosea": ("pityriasis rosea", "a harmless rash that starts with one larger patch and goes by itself"),
    "pityriasis rubra pilaris": ("pityriasis rubra pilaris", "orange-red scaly skin with patches of normal skin"),
    "porokeratosis actinic": ("actinic porokeratosis", "small ring-shaped scaly spots on sun-exposed skin"),
    "porokeratosis of mibelli": ("porokeratosis of Mibelli", "a ring-shaped patch with a raised edge"),
    "porphyria": ("porphyria", "fragile, blistering skin on sun-exposed areas"),
    "prurigo nodularis": ("prurigo nodularis", "very itchy hard bumps"),
    "psoriasis": ("psoriasis", "a long-lasting skin condition with red, scaly patches"),
    "pustular psoriasis": ("pustular psoriasis", "psoriasis with pus-filled spots"),
    "pyogenic granuloma": ("a pyogenic granuloma", "a harmless red lump that bleeds easily"),
    "rhinophyma": ("rhinophyma", "a thickened, bumpy nose from rosacea"),
    "rosacea": ("rosacea", "redness and spots on the face"),
    "sarcoidosis": ("sarcoidosis", "an inflammatory illness that can cause bumps or patches on the skin"),
    "scabies": ("scabies", "tiny mites that burrow in the skin and cause an itchy rash"),
    "scleroderma": ("scleroderma", "hard, tight, shiny skin"),
    "scleromyxedema": ("scleromyxoedema", "thickened skin with many small firm bumps"),
    "seborrheic dermatitis": ("seborrhoeic dermatitis", "a red, flaky rash on the scalp, face or chest"),
    "seborrheic keratosis": ("a seborrhoeic keratosis", "a harmless warty brown growth"),
    "solid cystic basal cell carcinoma": ("basal cell carcinoma", "a common, slow-growing skin cancer"),
    "squamous cell carcinoma": ("squamous cell carcinoma", "a common skin cancer, often a scaly lump or a sore that "
                                "does not heal"),
    "stasis edema": ("stasis oedema", "swelling of the lower legs from poor vein circulation"),
    "stevens johnson syndrome": ("Stevens-Johnson syndrome", "a serious reaction, usually to a medicine, with "
                                 "blistering skin and sore mouth, which needs a hospital"),
    "striae": ("stretch marks", "lines in the skin from stretching, common and harmless"),
    "sun damaged skin": ("sun-damaged skin", "skin aged by the sun, with wrinkles and uneven colour"),
    "superficial spreading melanoma ssm": ("a melanoma", "a serious skin cancer that often looks like an unusual "
                                           "mole"),
    "syringoma": ("syringomas", "harmless small skin-coloured bumps, often around the eyes"),
    "telangiectases": ("telangiectasia", "small visible blood vessels in the skin"),
    "tick bite": ("a tick bite", "a small red bump where a tick bit"),
    "tungiasis": ("tungiasis", "a sand flea burrowed in the skin, usually of the foot"),
    "urticaria": ("hives (urticaria)", "itchy raised welts that come and go"),
    "vitiligo": ("vitiligo", "patches of skin that have lost their colour"),
    "xanthomas": ("xanthomas", "yellowish fatty bumps, sometimes linked to high cholesterol"),
}
FITZ_WARNING = {"melanoma", "malignant melanoma", "superficial spreading melanoma ssm", "lentigo maligna",
                "basal cell carcinoma", "basal cell carcinoma morpheiform", "solid cystic basal cell carcinoma",
                "squamous cell carcinoma", "kaposi sarcoma", "actinic keratosis", "mycosis fungoides"}
FITZ_LABEL_CHILD = re.compile(r"\b(infan\w*|neonat\w*|juvenile|childhood|child|p(a)?ediatric|congenital|diaper|"
                              r"nappy)\b", re.I)


def fitz_slug(url):
    """The words of an atlas picture's address that may say more than the label ("psoriasis-genital"), or ""."""
    if "dermaamin" not in (url or ""):
        return ""
    parts = url.split("?")[0].rstrip("/").split("/")
    return clean(re.sub(r"[-_]+|\d+|\.jpe?g$", " ", f"{parts[-2]} {parts[-1]}", flags=re.I))


def fitz_site(slug):
    """The body site the address names, in plain words ("the penis"), or ""."""
    m = FITZ_SITE.search(slug or "")
    if not m:
        return ""
    word = m.group(1).lower()
    return FITZ_SITE_WORDS.get(word, f"the {word}")


def fitz_draft(label, slug, number=None):
    """The draft description of one Fitzpatrick17k picture: "This looks like <condition> (<explanation>).", the
    body site when the atlas address gives it, the skin type the set gives ("It is on dark brown skin (Fitzpatrick
    type V)."), DOCTOR (and SEE_SOON for a possible cancer). On types IV to VI, "red" in the explanation says how
    redness often looks on darker skin (a general fact, for the reviewer to correct to what the picture shows)."""
    if re.search(r"pearly penile papules", slug, re.I):          # the atlas files these under Fordyce spots
        name, why = "pearly penile papules", ("harmless tiny skin-coloured bumps in rows around the rim of the head "
                                              "of the penis, a normal variant")
    else:
        name, why = FITZ_PLAIN.get(label, (label, ""))
    if number and number >= 4:
        why = darker_skin_colours(why)
    site = fitz_site(slug)
    parts = [looks_like(name, why)]
    if site and number:
        parts.append(f"It is on {site}, on {SKIN_WORDS[number]} skin (Fitzpatrick type {ROMAN[number]}).")
    elif site:
        parts.append(f"It is on {site}.")
    elif number:
        parts.append(f"It is on {SKIN_WORDS[number]} skin (Fitzpatrick type {ROMAN[number]}).")
    if label in FITZ_WARNING:
        parts.append(SEE_SOON)
    parts.append(DOCTOR)
    return " ".join(parts)


def fitz_rows(s):
    """The Fitzpatrick17k table: [dict] (an empty list when it cannot be read)."""
    r = get(s, FITZ_CSV, timeout=120)
    if r is None or r.status_code != 200:
        return []
    return list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig", "replace"))))


FITZ_HOSTS = {}                           # {atlas host: True when a few of its pictures answer}


def fitz_host_answers(s, url):
    """True when the atlas that holds url still serves pictures (three of its addresses in the table are tried once
    per run); a host that no longer answers (DermaAmin was rebuilt in 2026) is left out, so the skin-type balance is
    made among pictures that can really be downloaded."""
    host = re.sub(r"^https?://(www\.)?", "", clean(url)).split("/")[0]
    if not host:
        return False
    if host not in FITZ_HOSTS:
        samples = FITZ_SAMPLES.get(host, [])
        FITZ_HOSTS[host] = any(download_picture(s, u.replace("http://", "https://")) for u in samples[:3])
    return FITZ_HOSTS[host]


FITZ_SAMPLES = {}                         # {atlas host: a few of its picture addresses}, filled by fetch_fitzpatrick17k


def fitz_keep(row):
    """(True, "") when a Fitzpatrick17k row may be used; otherwise (False, why)."""
    label, url = clean(row.get("label")).lower(), clean(row.get("url"))
    slug = fitz_slug(url)
    if not url:
        return False, "no picture address"
    if label in FITZ_EXCLUDED_LABELS or FITZ_LABEL_CHILD.search(label):
        return False, "a label that usually means a child"
    if not child_free(slug):
        return False, "the picture's address names a child"
    if not not_sexual(slug):
        return False, "the picture's address names something sexual"
    if clean(row.get("qc")).startswith("3"):
        return False, "marked wrongly labelled by the set's own check"
    return True, ""


def fetch_fitzpatrick17k(folder, cap, say=print):
    """Fitzpatrick17k (Groh et al., 2021): the whole skin-condition set, for review. Labels CC BY-NC-SA 3.0; the
    pictures belong to the two atlases they link to (DermaAmin and Atlas Dermatologico, all rights reserved), so the
    category is "research" (personal use only). Labels that usually mean a child are left out before review
    (FITZ_EXCLUDED_LABELS, and any label or picture address naming an infant, newborn, child, juvenile, congenital
    condition or nappy rash). Pictures of a usually genital label (FITZ_ALWAYS_GENITAL) or whose address names a
    genital, breast or buttock site are tagged "intimate" one by one. Note: in November 2026 the DermaAmin addresses
    (about three quarters of the set) no longer answered (the site was rebuilt); those pictures are tried once and
    left out."""
    source = source_by_key("fitzpatrick17k")
    ws, s = ReviewWorkspace(folder, source, say), session()
    rows = fitz_rows(s)
    say(f"Fitzpatrick17k: {len(rows)} records in the table")
    items, left, why_left = [], 0, {}
    # Balanced: an equal share for each skin-type group (I-II, III-IV, V-VI, then unknown), and within each group
    # an equal share for each condition, so a small cap still shows every skin tone and many conditions.
    for row in rows[::97]:                # a spread of addresses for each host
        host = re.sub(r"^https?://(www\.)?", "", clean(row.get("url"))).split("/")[0]
        FITZ_SAMPLES.setdefault(host, []).append(clean(row.get("url")))
    rows = [r for r in rows if fitz_host_answers(s, r.get("url"))]
    say("Fitzpatrick17k: picture hosts that answer: " + ", ".join(f"{h} {'yes' if ok else 'NO'}"
                                                                  for h, ok in FITZ_HOSTS.items() if h))
    order = balanced(rows, lambda r: fitz_group(r.get("fitzpatrick_scale")), lambda r: clean(r.get("label")).lower())
    for row in order:
        ok, why = fitz_keep(row)
        if not ok:
            left += 1
            why_left[why] = why_left.get(why, 0) + 1
            continue
        label, url = clean(row["label"]).lower(), clean(row["url"])
        slug = fitz_slug(url)
        site = fitz_site(slug)
        intimate = label in FITZ_ALWAYS_GENITAL or site in FITZ_INTIMATE_SITES or bool(GENITAL.search(slug)) \
            or bool(BREAST.search(slug))
        atlas = "DermaAmin (dermaamin.com)" if "dermaamin" in url else "Atlas Dermatologico (atlasdermatologico.com.br)"
        number = fitz_type(row.get("fitzpatrick_scale"))
        note = (f"Fitzpatrick skin type {ROMAN[number] if number else 'not given'}; label '{label}'"
                + (f"; the atlas file name says '{slug}'" if slug else "") + ". No age given: confirm the person is "
                "an adult." + (" INTIMATE: a genital, breast or buttock site." if intimate else ""))
        items.append((f"f17k-{row['md5hash']}.jpg", url.replace("http://", "https://"),
                      fitz_draft(label, slug, number),
                      f"Fitzpatrick17k (Groh et al., 2021), label '{label}', picture from {atlas}",
                      "labels CC BY-NC-SA 3.0; picture all rights reserved by the atlas (personal use only)", url,
                      "intimate" if intimate else "medical", note, fitz_group(row.get("fitzpatrick_scale"))))
    say("Fitzpatrick17k left out before download: " + (", ".join(f"{n} ({w})" for w, n in why_left.items())
                                                      or "none"))
    left += fill(ws, items, cap, s, workers=4)
    return ws.finish(len(rows), left)


# ----------------------------------------------------------------- the collections

PERSONAL = "personal use only"
REVIEW_SOURCES = [
    dict(key="cdc_phil_intimate", name="CDC clinical photographs of genital and breast conditions (review only)",
         category="open", licence="Public domain (US government work; each picture's own copyright field checked)",
         terms="https://phil.cdc.gov/",
         terms_summary="public domain; no permission needed; credit the CDC Public Health Image Library",
         credit="CDC Public Health Image Library (PHIL), https://phil.cdc.gov, public domain",
         content="intimate", cap=400, download="about 60 MB", fetch=fetch_cdc_phil_intimate, review_only=True),
    dict(key="pmc_intimate", name="Medical case-report pictures of adult genitals and breasts (review only)",
         category="open", licence="CC BY or CC0 (each article's licence checked in PubMed Central's own metadata)",
         terms="https://pmc.ncbi.nlm.nih.gov/tools/openftlist/",
         terms_summary="CC BY or CC0: free to use with credit to the authors (credited per picture)",
         credit="Authors of the case reports and reviews in PubMed Central, CC BY or CC0, credited in CREDITS.txt",
         content="intimate", cap=2000, download="about 500 MB", fetch=fetch_pmc_intimate, review_only=True),
    dict(key="commons_intimate", name="Wikimedia Commons medical pictures of genitals and breasts, open licences "
                                      "(review only)",
         category="open", licence="CC0, public domain or CC BY (each file's own licence checked)",
         terms="https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia",
         terms_summary="CC0, public domain or CC BY: free to use with credit to each author (in CREDITS.txt)",
         credit="Wikimedia Commons authors, CC0, public domain or CC BY, credited in CREDITS.txt",
         content="intimate", cap=600, download="about 120 MB", fetch=fetch_commons_intimate, review_only=True),
    dict(key="commons_intimate_sa", name="Wikimedia Commons medical pictures of genitals and breasts, share-alike "
                                         "(review only)",
         category="share-alike", licence="CC BY-SA (each file's own licence checked)",
         terms="https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia",
         terms_summary="CC BY-SA: free to use with credit; anything shared that is made from them must be CC BY-SA",
         credit="Wikimedia Commons authors, CC BY-SA, credited in CREDITS.txt",
         content="intimate", cap=600, download="about 120 MB", fetch=fetch_commons_intimate_sa, review_only=True),
    dict(key="fitzpatrick17k", name="Fitzpatrick17k skin conditions on all skin tones (review only)",
         category="research",
         licence="Labels CC BY-NC-SA 3.0 (github.com/mattgroh/fitzpatrick17k); pictures belong to the atlases "
                 "DermaAmin and Atlas Dermatologico (all rights reserved)",
         terms="https://github.com/mattgroh/fitzpatrick17k",
         terms_summary="labels non-commercial share-alike; pictures all rights reserved by the atlases: personal "
                       "use only, never shared",
         credit="Fitzpatrick17k (Groh, Harris, Soenksen et al., 2021, CVPR Workshops), CC BY-NC-SA 3.0 labels; "
                "pictures from DermaAmin and Atlas Dermatologico",
         content="medical", cap=17000, download="about 1 GB (only about 3,900 pictures still answer)",
         fetch=fetch_fitzpatrick17k, review_only=True),
]


def source_by_key(key):
    """The REVIEW_SOURCES entry with this key."""
    return next(s for s in REVIEW_SOURCES if s["key"] == key)


# Sources looked at (November 2026) and not included, with the reason.
NOT_INCLUDED = {
    "Labia Library (Women's Health Victoria)": "can't be included: its gallery says 'Photographs (c) Breeana Dunbar. "
        "All rights reserved' and 'reproduced with kind permission from Show Off Books ... All rights reserved'; the "
        "permission is for the Labia Library only.",
    "The Vulva Gallery (Hilde Atalanta)": "can't be included: illustrations are the artist's copyrighted work, sold "
        "as prints and books; no licence to copy.",
    "Know Your Lemons (Worldwide Breast Cancer)": "can't be included: '(c) All rights reserved' with its own Image "
        "Use Policy (permission needed); the pictures are mostly lemon illustrations, not photographs.",
    "Breastcancer.org and similar charity galleries": "can't be included: licensed stock photographs, all rights "
        "reserved.",
    "DermNet (dermnetnz.org)": "can't be included: watermarked images are CC BY-NC-ND (the site terms say 'you may "
        "not remix, transform, or build upon any images' and 'must not remove the watermark'); training uses "
        "resized copies, and clean pictures need a paid licence.",
    "NCI Visuals Online (visualsonline.cancer.gov)": "not added: the site did not answer from the build machine "
        "(November 2026). Its public-domain items can be added later; some are also on Wikimedia Commons.",
    "Office on Women's Health (womenshealth.gov)": "no picture gallery of anatomy or conditions found; its few "
        "pictures are stock photographs.",
    "NIH/NLM (MedlinePlus, Open-i)": "MedlinePlus pictures are licensed from A.D.A.M. (copyrighted); Open-i serves "
        "PubMed Central figures, which pmc_intimate reads directly with each article's own licence.",
    "OpenStax Anatomy and Physiology (first edition) and Gray's Anatomy plates": "already in the 'anatomy' pack "
        "(reproductive anatomy and breast figures included there); not duplicated.",
    "Breastfeeding pictures": "already in the birth_and_feeding pack; Commons files about breastfeeding or nursing "
        "are left out here (BLOCKED_CATEGORY).",
    "Commons categories Hypospadias and Peyronie's disease": "left out: hypospadias pictures are nearly all of "
        "children; Peyronie's pictures show an erection.",
    "Commons sexual, art and nudity categories (for example 'Penile sex', 'Human penis by degree of rigidity', "
    "'Penis enlargement', 'Male ejaculation', 'Human penis in art', naturism)": "never read; any file that is also "
        "in such a category is left out.",
    "Porn or adult-entertainment sites": "never used.",
    # Skin-of-colour sources (looked at on purpose, November 2026).
    "DDI, Stanford Diverse Dermatology Images (ddi-dataset.github.io)": "sign-up: a Research Use Agreement "
        "(personal, non-commercial research only; no sharing or reproducing; each user registers). Category "
        "'research'; the person training can sign up and add it themselves. Not genital or breast specific.",
    "Skin of Color Society (skinofcolorsociety.org)": "can't be included: '(c) Skin of Color Society. All rights "
        "reserved'; no open picture library.",
    "Brown Skin Matters (brownskinmatters.com)": "can't be included: '(c) All Rights Reserved'; pictures are "
        "contributed by the public and shared on social media, with no licence to copy.",
    "Mind the Gap (Mukwende, Tamony and Turner, St George's)": "can't be included: a copyrighted handbook (sold as a "
        "book); no picture licence.",
    "Skin Deep (skindeep.dftb.org, Don't Forget the Bubbles)": "not added: the site did not answer from the build "
        "machine (November 2026), and it is a children's skin project (paediatric pictures), so it does not fit "
        "these adults-only collections in any case.",
    "PAD-UFES-20 skin types": "already in the skin_lesion_photos pack (which leaves out intimate sites); it records "
        "Fitzpatrick types, but has no genital or breast pictures to add here.",
}


def main(argv):
    """Quick test: python review_sources.py <key> <folder> [cap]. Prints only titles, labels and drafts."""
    if len(argv) < 3:
        print("python review_sources.py <key> <folder> [cap]\nkeys: " + ", ".join(s["key"] for s in REVIEW_SOURCES))
        return 1
    source = source_by_key(argv[1])
    source["fetch"](argv[2], int(argv[3]) if len(argv) > 3 else 5, print)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
