"""Graphic-scene collections for the Picture Model Training Kit whose licence keeps them out of the open packs: war,
disasters, injuries and death, and practical safety scenes, described plainly. The open ones (Library of Congress,
National Archives, US Holocaust Memorial Museum, and the CC0, public-domain and CC BY files of Wikimedia Commons)
are ready-made packs: packs/graphic_packs.py.

The owner's rule: a blind person deserves an unfiltered view of the world, and a blind person caught in a war zone
or a disaster needs to understand what is around them. So these pictures are described accurately, factually and
respectfully, without euphemism and without sensationalism, using each record's own caption. A row whose words say
the picture shows the dead or injured (people or animals), wounds, or destruction with casualties carries
"content": "graphic" and is used only with the graphic-scenes choice (train.py --with-graphic; sources.keep_allowed);
a picture-making model never learns from any collection here (GRAPHIC_PICTURE_MAKING_OK is empty).

Left out, whatever a record says (not_shown, the same rules as packs/graphic_packs.py): sexual violence; anything
sexual or nude; a picture whose focus is a dead or injured child (children in ordinary war or disaster scenes are kept
and marked "child"); torture, execution and hanging scenes and propaganda made to glorify killing, unless the record
is presented as evidence (the liberation of the camps, exhumations, war-crimes investigations and trials); captions
holding old slurs.

Nothing here is in a ready-made pack or re-shared by the kit's makers. Each collection is downloaded by the kit on the
user's own computer, straight from its makers, only when the user ticks the matching choice. Groups (Source.group, as
in sources.py and extra_sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with
                   them is CC BY-SA.
  "noncommercial"  non-commercial licences: only with --personal-noncommercial; the add-on is for personal use only.

The collections (GRAPHIC_SOURCES):
  share-alike
    commons_graphic_sa   Wikimedia Commons war, disaster and safety categories (the same ones as the open packs
                         commons_war, commons_disasters and commons_safety): files under CC BY-SA or GFDL (never NC or
                         ND), with the file's English caption or the start of its English description; the safety
                         categories also get their plain question and answer about the hazard or sign.
  noncommercial
    iwm_photos           Imperial War Museums (London): photographs of the First and Second World Wars and later
                         conflicts, with the museum's descriptions, under the IWM Non Commercial Licence. Read from the
                         museum's own collection search on the user's computer. (Its site refused the machine this entry
                         was written on, with a Cloudflare check, so it could not be tried there; when the site refuses,
                         the kit says so and leaves the collection out.)

Needing sign-up or permission (cannot be downloaded automatically; GRAPHIC_SIGN_UP has the links): DVIDS (US military
photos, public domain; its API needs a free key), the National Museum of Health and Medicine's Otis Historical
Archives (Civil War and military-medicine photographs of wounds; US government, but the archive asks for a
permission-to-use form first) and the Flickr copies of government photo libraries (FEMA, NMHM, the US Army), which
need a free Flickr API key. Looked at and not included: GRAPHIC_NOT_INCLUDED.

    python kit/graphic_sources.py commons_graphic_sa --data <empty folder> --cap 8     (a quick check)
"""

import os
import random
import re
import time

import sources
from extra_sources import NUDE, commons_file_name, commons_members, commons_sa_entries, commons_session
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS, first_sentences
from sources import NARRATE, Source, clean

# ----------------------------------------------------------------- the content rules (as packs/graphic_packs.py)

GRAPHIC = re.compile(r"\b(dead|death|deaths|died|dying|corpses?|cadavers?|bodies|bod(?:y|ies) of|killed|slain|"
                     r"wounded|wounds?|casualt\w*|injur\w*|bleeding|blood\w*|bloodied|mass graves?|graves? of|"
                     r"burial|buried|burying|massacre\w*|atrocit\w*|skeletons?|skulls?|remains of|human remains|"
                     r"mutilat\w*|amputat\w*|amputees?|charred|burned alive|cremat\w*|exhum\w*|fatalit\w*|"
                     r"stretchers?|litters?|gunshot|shrapnel|severed|decompos\w*|starv\w*|emaciat\w*|"
                     r"carcass\w*|morgue|body bags?)\b", re.I)
SEXUAL_VIOLENCE = re.compile(r"\b(rape[ds]?|raping|rapists?|sexual(?:ly)? (?:assault\w*|abuse\w*|violence|"
                             r"slavery|exploit\w*)|molest\w*|forced prostitution|comfort women)\b", re.I)
KILLING = re.compile(r"\b(tortur\w*|execut(?:e|ed|es|ing|ion|ions|ioners?)|behead\w*|hanged|hangings?|gallows|"
                     r"lynch\w*|firing squad|shot dead|shooting of (?:the )?(?:prisoners?|civilians?|hostages?)|"
                     r"being shot|about to be shot)\b", re.I)
EVIDENCE = re.compile(r"\b(liberat\w*|exhum\w*|war crimes?|evidence|investigat\w*|tribunal|trials?|documented|"
                      r"documenting|inspection tour|forced confrontation)\b", re.I)
PROPAGANDA = re.compile(r"\bpropaganda\b", re.I)
SLURS = re.compile(r"\b(japs?|nips?|niggers?|negroes|coloreds?|squaws?|redskins?|gooks?|krauts?|huns)\b", re.I)
NOT_CHILD = re.compile(r"\binfantr\w*|\bkinds? of\b", re.I)
NOT_ENGLISH = re.compile(r"[^\x00-ɏ‐-‧]|\b[a-z]{2}:\S")


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def child_in(*texts):
    """True when any of texts mentions a child (personal_sources.CHILD_WORDS, without "infantry" and the like)."""
    return any(CHILD_WORDS.search(NOT_CHILD.sub(" ", t or "")) for t in texts)


def not_shown(*texts):
    """True when a picture's words say it must be left out (see the module docstring)."""
    joined = " ".join(t for t in texts if t)
    if not joined:
        return False
    graphic = bool(GRAPHIC.search(joined))
    if SEXUAL_VIOLENCE.search(joined) or NUDE.search(joined) or SLURS.search(joined):
        return True
    if graphic and child_in(joined):
        return True
    if KILLING.search(joined) and not EVIDENCE.search(joined):
        return True
    return bool(PROPAGANDA.search(joined) and (graphic or KILLING.search(joined)))


def tagged(row, *texts):
    """row with "content": "graphic" when its answer or texts are graphic, and "child": True when they name a
    child."""
    words = (row.get("answer", ""), *texts)
    if any(GRAPHIC.search(t or "") for t in words):
        row = dict(row, content="graphic")
    if child_in(*words):
        row = dict(row, child=True)
    return row


def caption(text, most=70):
    """A caption as an answer: tidied, its first sentences (at most about most words), a capital first letter and a
    full stop; "" when it is shorter than 6 words or not in English."""
    text = re.sub(r"\[[^\]]*\]|\{\{[^}]*\}\}", " ", clean(text)).strip(" .,")
    text = first_sentences(text, most)
    if len(text.split()) < 6 or NOT_ENGLISH.search(text):
        return ""
    return text[0].upper() + text[1:] + ("" if text.endswith((".", "!", "?")) else ".")


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

# The categories of the open packs (packs/graphic_packs.py COMMONS_WAR and COMMONS_DISASTERS), with whether one level
# of subcategories is used too.
GRAPHIC_CATEGORIES = {
    "War casualties": True, "Wounded soldiers": True, "Casualties of World War I": True,
    "Civilian casualties of World War II": True, "Casualties of the Korean War": True,
    "Casualties of the Vietnam War": True, "Casualties of the Iraq War": True, "Field hospitals": True,
    "Liberation of Nazi concentration camps": True, "Aftermath of World War I": True,
    "Aftermath of World War II": True, "Hiroshima in ruins": True, "Ruins in Warsaw after WWII": True,
    "The Blitz": True, "Destroyed buildings in Syria": True,
    "Destructions during the 2022 Russian invasion of Ukraine": True,
    "War damages in Kyiv Oblast (2022 Russian invasion of Ukraine)": True,
    "Damaged infrastructure in the 2022 Russian invasion of Ukraine": True,
    "Earthquake damage": True, "Flood damage": True, "Tornado damage": True, "Landslides": True,
    "Collapsed buildings": True, "Destroyed buildings": True, "Rubble": True,
}
# The safety categories (packs/graphic_packs.py SAFETY), each with its question and plain answer about the hazard or
# sign. The answers describe; they never give tactical or weapon-use advice.
SAFETY = {
    "Downed power lines": ("What hazards are in this picture?", "Power lines have fallen down here. A fallen line may "
                           "still be live, and the ground or water around it can carry electricity."),
    "Flooded roads": ("What hazards are in this picture?", "The road is flooded. The water hides the road surface, "
                      "holes and the edge of the road, and moving water can sweep a person or a car away."),
    "Burning buildings": ("What hazards are in this picture?", "A building is on fire: there are flames and smoke."),
    "Unexploded ordnance": ("What hazards are in this picture?", "This shows unexploded ordnance: a bomb, shell, "
                            "rocket or grenade that did not go off and can still explode if it is touched or moved."),
    "Landmine warning signs": ("What does this sign mean?", "It warns of landmines: the area beyond it may have mines "
                               "in the ground and is dangerous to enter."),
    "Checkpoints": ("What kind of place is this?", "It is a checkpoint, where guards or soldiers stop people and "
                    "vehicles to check them before they pass."),
    "Air raid shelters": ("What kind of place is this?", "It is an air-raid shelter: a protected place, often "
                          "underground, where people go during an air raid."),
    "Fallout shelter signs": ("What does this sign mean?", "It marks a fallout shelter: a building or basement where "
                              "people can shelter from radioactive fallout."),
    "Refugee camps": ("What kind of place is this?", "It is a refugee camp, where people who have fled war or "
                      "disaster live in tents or shelters."),
    "Evacuation route signs": ("What does this sign mean?", "It is an evacuation route sign: it shows the way to "
                               "leave the area in an emergency, such as a hurricane, a tsunami or a flood."),
}
NOT_IT = re.compile(r"\b(art|artworks?|drawings?|illustrations?|paintings?|sculptures?|statues?|memorials?|"
                    r"monuments?|cemeter\w*|graves?|tombs?|posters?|propaganda|cartoons?|maps?|diagrams?|logos?|"
                    r"stamps?|videos?|executions?|hangings?|torture|nude|naked|reenact\w*|models?|toys?|svg|"
                    r"portraits?)\b", re.I)


def category_titles(s, category, deeper):
    """The file titles of a Commons category and, when deeper, of one level of its subcategories (leaving out those
    NOT_IT names and those about children); [] when the category cannot be read."""
    try:
        titles = commons_members(s, category, "file")
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                sub = sub.split(":", 1)[-1]
                if not NOT_IT.search(sub) and not child_in(sub):
                    titles += commons_members(s, sub, "file")
    except Exception as e:  # noqa: BLE001 - a missing or refused category is left out
        say(f"    Commons {category}: left out ({str(e)[:100]})")
        return []
    return [t for t in dict.fromkeys(titles) if not NOT_IT.search(t)]


def prepare_commons_graphic_sa(source, data_dir, work, cap):
    """Wikimedia Commons war, disaster and safety categories, files under CC BY-SA or GFDL (never NC or ND): the
    file's English caption or description as "Describe this picture.", and for the safety categories their question
    and answer too; rows marked graphic and child as the module docstring says. The categories share the cap."""
    s = commons_session()
    want = int((cap + source.test) * 1.2)
    categories = [(c, deeper, None) for c, deeper in GRAPHIC_CATEGORIES.items()] + \
                 [(c, False, qa) for c, qa in SAFETY.items()]
    per_category = max(5, want // len(categories) * 2)
    items, seen = [], set()
    for category, deeper, qa in categories:
        titles = [t for t in category_titles(s, category, deeper) if t not in seen]
        random.Random(category).shuffle(titles)
        found = 0
        for start in range(0, min(len(titles), per_category * 3), 50):
            for title, url, credit, text in commons_sa_entries(s, titles[start:start + 50]):
                answer = caption(text)
                name_words = re.sub(r"[_-]+", " ", title.split(":", 1)[-1].rsplit(".", 1)[0])
                if title in seen or not_shown(answer, name_words) or (not answer and not qa):
                    continue
                seen.add(title)
                name = commons_file_name("cgsa", title)
                rows = ([{"question": qa[0], "answer": qa[1]}] if qa else []) + \
                       ([{"question": NARRATE, "answer": answer}] if answer else [])
                for row in rows:            # every row of the picture marked alike (its file's words count)
                    items.append((name, url, tagged(dict(row, split="", credit=credit), answer, name_words)))
                found += 1
                if found >= per_category:
                    break
            if found >= per_category:
                break
        say(f"    Commons {category}: {found} share-alike pictures")
    random.Random(411).shuffle(items)
    say(f"  Fetching {len({n for n, _, _ in items})} Commons war, disaster and safety pictures (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- non-commercial: Imperial War Museums

IWM = "https://www.iwm.org.uk"
IWM_LICENCE = "https://www.iwm.org.uk/corporate/policies/non-commercial-licence"
IWM_WORDS = ("wounded", "casualties", "first aid", "stretcher bearers", "dressing station", "bomb damage", "ruins",
             "air raid", "shelter", "refugees", "evacuation", "flood", "fire", "liberation", "Blitz", "Belsen")


def iwm_page(s, path):
    """(title, description, picture address, licence words) of an IWM object page, from its meta tags; None when
    the page cannot be read."""
    try:
        r = s.get(IWM + path, timeout=60)
    except Exception:  # noqa: BLE001 - left out
        return None
    if r.status_code != 200:
        return None
    meta = dict(re.findall(r'<meta (?:property|name)="((?:og|twitter):[a-z:]+)" content="([^"]*)"', r.text))
    licence = "IWM Non Commercial Licence" if "Non Commercial Licence" in r.text or "Non-Commercial Licence" in r.text \
        else ""
    return clean(meta.get("og:title")), clean(meta.get("og:description")), meta.get("og:image", ""), licence


def prepare_iwm_photos(source, data_dir, work, cap):
    """Imperial War Museums photographs under the IWM Non Commercial Licence: object pages found with IWM_WORDS in
    the museum's collection search (photographs only), the museum's description (or title, when longer) as "Describe
    this picture." Only pages that name the Non Commercial Licence are used. Raises a plain error when the museum's
    site refuses the computer (it sometimes asks browsers to pass a check first)."""
    s = commons_session()
    want = int((cap + source.test) * 1.2)
    per_word = want // len(IWM_WORDS) + 2
    items, seen, refused = [], set(), 0
    for word in IWM_WORDS:
        found = 0
        for page in range(1, 6):
            try:
                r = s.get(IWM + "/collections/search", params={"query": word, "filters[webCategory][Photographs]": "on",
                                                              "media-records": "records-with-media", "page": page},
                          timeout=60)
            except Exception:  # noqa: BLE001 - next word
                break
            if r.status_code != 200:
                refused += 1
                break
            paths = [p for p in dict.fromkeys(re.findall(r'href="(/collections/item/object/\d+)"', r.text))
                     if p not in seen]
            if not paths:
                break
            for path in paths:
                seen.add(path)
                time.sleep(1)
                info = iwm_page(s, path)
                if not info or not info[2] or not info[3]:
                    continue
                title, description, picture, licence = info
                text = description if len(description.split()) > len(title.split()) else title
                answer = caption(text, 80)
                if not answer or not_shown(answer, title):
                    continue
                credit = f"{title[:150]}, Imperial War Museums, {licence} ({IWM_LICENCE}), {IWM}{path}"
                row = tagged({"question": NARRATE, "answer": answer, "split": "", "credit": credit}, title)
                items.append((f"iwm-{path.rsplit('/', 1)[-1]}.jpg", picture, row))
                found += 1
                if found >= per_word:
                    break
            if found >= per_word:
                break
    if not items and refused:
        raise RuntimeError("the Imperial War Museums website refused this computer (it may ask browsers to pass a "
                           "check first); try again later")
    say(f"  Fetching {len(items[:want])} Imperial War Museums photographs (non-commercial).")
    return fetch_shared(items[:want], os.path.join(data_dir, source.key), workers=3)


# ----------------------------------------------------------------- needing sign-up, and not included

GRAPHIC_SIGN_UP = {
    "DVIDS, the Defense Visual Information Distribution Service (US military photos with captions, public domain)":
        "https://api.dvidshub.net/ : a free API key is needed to search and download (sign-up at "
        "https://www.dvidshub.net/). Check each photo's own terms: a few are marked otherwise.",
    "National Museum of Health and Medicine, Otis Historical Archives (Civil War and military-medicine photographs of "
    "wounds and surgery; US government)":
        "https://medicalmuseum.health.mil/index.cfm/collections/archives/index : the archive sends scans after a "
        "permission-to-use form (personal, research or publication use); its few files on Wikimedia Commons are in "
        "the open commons_war pack. Pictures received can be put in the own-pictures folder.",
    "Flickr copies of government photo libraries (FEMA, the National Museum of Health and Medicine, the US Army, "
    "DVIDS)":
        "https://www.flickr.com/services/api/misc.api_keys.html : a free Flickr API key is needed; check each "
        "photo's licence on its page.",
}

GRAPHIC_NOT_INCLUDED = {
    "FEMA photo library (public domain)": "www.fema.gov refused the machine these entries were made on (403); FEMA's "
                                          "photos on Wikimedia Commons are in the open commons_disasters pack.",
    "NOAA Photo Library (public domain)": "its site forwards to www.noaa.gov/digital-library, which refused the "
                                          "machine (403).",
    "President of Ukraine (president.gov.ua, CC BY 4.0 by its own statement)": "its site refused the machine (403); "
                                                                              "its photos copied to Wikimedia "
                                                                              "Commons reach the open commons_war "
                                                                              "pack.",
    "Commercial news agencies (AP, Reuters, Getty, AFP)": "commercial and copyrighted; not used.",
}


# ----------------------------------------------------------------- the table

GRAPHIC_SOURCES = [
    Source("commons_graphic_sa", "War, disaster and safety scenes from Wikimedia Commons, described plainly "
                                 "(share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page); captions CC0",
           "Wikimedia Commons contributors, war, disaster and safety categories, each file under CC BY-SA or GFDL "
           "with its author named, https://commons.wikimedia.org/wiki/Category:War_casualties",
           "share-alike", 1500, 15, prepare_commons_graphic_sa, "about 600 MB of pictures"),
    Source("iwm_photos", "Imperial War Museums: photographs of the World Wars and later conflicts, described plainly "
                         "(personal use)",
           f"IWM Non Commercial Licence ({IWM_LICENCE}): non-commercial use with credit",
           "Imperial War Museums, London, photographs under the IWM Non Commercial Licence, credited per photograph, "
           "https://www.iwm.org.uk/collections", "noncommercial", 1500, 15, prepare_iwm_photos,
           "about 600 MB of pictures", terms=IWM_LICENCE,
           terms_summary="IWM Non Commercial Licence: you may use the photographs for non-commercial purposes with "
                         "credit to the Imperial War Museums; no commercial use. Personal use only."),
]

# The collections a picture-making model may learn from: none of these (graphic scenes, people and children).
GRAPHIC_PICTURE_MAKING_OK = set()


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print the questions and answers of a few rows
    (a quick check; the pictures are not shown)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try one graphic-scene collection.")
    parser.add_argument("key", choices=[s.key for s in GRAPHIC_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in GRAPHIC_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="graphic-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:12]:
        print(json.dumps({k: row.get(k) for k in ("question", "answer", "content", "child")}, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('content') == 'graphic')} rows marked graphic, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
