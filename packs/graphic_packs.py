"""Pack builders for GRAPHIC scenes, described plainly: war, disasters, injuries and death, and the practical safety
scenes someone caught in a war zone or a disaster needs to understand (collapsed buildings, rubble, fire and smoke,
flooding, fallen power lines, unexploded-ordnance and mine warning signs, checkpoints, shelters, first-aid stations,
evacuation routes). The owner's rule: a blind person deserves an unfiltered view of the world, so these pictures are
described accurately, factually and respectfully, without euphemism and without sensationalism.

They are used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" when the record
says where the photo was taken (places.py), "child": True when the caption mentions a child (expression_packs.CHILD),
and "content": "graphic" when the picture shows dead or injured people or animals, wounds, or severe destruction with
casualties (GRAPHIC below). The kit uses a row marked graphic only when the person training ticks the graphic-scenes
choice (train.py --with-graphic), and a picture-making model never learns from any of these packs. The limit counts
pictures.

Every picture gets "Describe this picture." with its record's own caption, tidied (catalogue codes, square brackets,
file notes and US state abbreviations sorted out), at least 6 words long; a picture whose record names the place also
gets "Where was this photo taken?" as a second row for the same picture (food_packs.with_twins). Nothing is written by
an AI model. The safety scenes also get a plain question about the hazard or sign, with an answer written here for
the whole category (SAFETY), which describes the hazard and never gives tactical or weapon-use advice.

Left out, whatever the record says (not_shown): sexual violence; anything sexual or nude (documentary_packs.
NOT_SHOWN); a picture whose focus is a dead or injured child (graphic words and child words in the same caption;
children in ordinary war or disaster scenes are kept and marked child); torture, execution and hanging scenes and
propaganda made to glorify killing, unless the record is a documented historical record presented as evidence
(EVIDENCE: the liberation of the camps, exhumations, war-crimes investigations and trials), which is kept with its
factual caption; and captions holding old slurs (some 1940s captions), which are left out rather than repeated.

The packs (licences checked at the source in November 2026):
  loc_civil_war     Library of Congress, Civil War glass negatives and related prints (about 8,800 records:
                    Alexander Gardner's, Timothy O'Sullivan's and Mathew Brady's photographs, among them the
                    battlefield dead at Antietam, Gettysburg and Petersburg, field hospitals and ruined towns) and Roger
                    Fenton's Crimean War photographs (about 260), read at random and with the search words dead,
                    wounded, ruins, hospital and burial. "No known restrictions on publication." The
                    Library's titles are short, so each answer ends with the war and its years ("A photograph from the
                    American Civil War, 1861 to 1865."), from the collection's own description; the title itself must
                    be at least 4 words and the whole answer at least 6.
  loc_war_disaster  Library of Congress: the Bain News Service photographs (about 1900 to 1920; the First World War,
                    fires, floods, earthquakes, wrecks), found with war and disaster search words, and the Farm Security
                    Administration / Office of War Information photographs of floods, fires, air-raid drills, civil
                    defence and first aid (1935 to 1945). "No known restrictions."
  nara_war          US National Archives, "Photographs of American Military Activities, ca. 1918 - ca. 1981" (the
                    Army Signal Corps series 111-SC: the First and Second World Wars, Korea and Vietnam, with the
                    Signal Corps captions), found with search words such as wounded, casualties, aid station,
                    destroyed and refugees. US government work, public domain; only records marked "Unrestricted".
  ushmm             United States Holocaust Memorial Museum photo archive: only photographs whose record says
                    "Copyright: Public Domain" (mostly US Army Signal Corps photographs held by the National Archives;
                    the camps' liberation, survivors, the dead found by the liberators, war-crimes trials, ghettos and
                    deportations), with the museum's caption. Photographs under any other rights statement (agency
                    agreements, "exclusively with provenance", the museum's own copyright) are left out.
  commons_war       Wikimedia Commons categories of war casualties, wounded soldiers, field hospitals, aftermath and
                    ruins (the World Wars, Korea, Vietnam, Iraq, Hiroshima and Nagasaki, Warsaw, the Blitz) and of
                    modern war damage (the Russian invasion of Ukraine, the Syrian civil war), and the National
                    Museum of Health and Medicine's files on Commons. Only files whose own licence is CC0, public
                    domain or CC BY (each author credited; the CC BY-SA files are a share-alike kit entry,
                    training-kit/kit/graphic_sources.py), with the file's English caption or description.
  commons_disasters Wikimedia Commons categories of earthquake, flood, tornado, landslide and fire damage, collapsed
                    buildings, debris and rubble, and the FEMA photographs on Commons (US government
                    work). Licences as commons_war.
  commons_safety    Wikimedia Commons categories of practical safety scenes: fallen power lines, flooded roads,
                    smoke, burning buildings, unexploded ordnance and its warning signs, landmine warning signs,
                    checkpoints, barricades and sandbags, air-raid and fallout shelters and their signs, air-raid
                    sirens, first-aid stations, field hospitals, refugee camps, evacuation-route, emergency-exit and
                    assembly-point signs. Each file gets the category's question with a plain answer about the hazard
                    or sign (SAFETY) and, when it has one, its own description. Licences as commons_war.

Looked at and not used here (checked at the source in November 2026), with the reason; the ones that are not open
are kit entries in training-kit/kit/graphic_sources.py:
  Imperial War Museums          IWM Non Commercial Licence (non-commercial: a kit entry); its site refused this machine
                                (Cloudflare 403). Its old photographs whose Crown copyright has expired are on Commons
                                and reach commons_war through its categories.
  National Museum of Health and Medicine, Otis Historical Archives   US government, but the archive's own terms ask for a
                                permission-to-use form before images are sent (sign-up, listed in graphic_sources.py);
                                its few files on Commons are in commons_war.
  DVIDS (US military photos)    Public domain, but its API needs a key (sign-up, listed in graphic_sources.py).
  FEMA photo library, NOAA Photo Library, USGS image pages   Public domain, but their sites refused this machine (403);
                                FEMA's and USGS's photos on Commons are in commons_disasters.
  President of Ukraine (president.gov.ua) and Ukraine's ministries   The President's site states CC BY 4.0 for its
                                materials, but refused this machine (403); its photos copied to Commons under CC BY
                                4.0 reach commons_war through the Ukraine war-damage categories.

    python packs/graphic_packs.py ushmm --limit 8      (prints a few rows: a quick check of one builder)
"""

import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, NARRATE
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from build_packs import listing_out_of_time
from build_packs import needs_description  # pictures set aside for a description (see build_packs)
from food_packs import count_pictures, commons_members, commons_entries, commons_place, credit_licence
from expression_packs import CHILD
from world_packs import capped_words
from places import country_named, place_name
from documentary_packs import tidy, picture_rows, get_json, finish, loc_picture, loc_place, NOT_SHOWN, LOC

# ----------------------------------------------------------------- the content rules

# Words that mean a picture shows the dead or injured (people or animals), wounds, or destruction with casualties:
# its rows are marked "content": "graphic".
GRAPHIC = re.compile(r"\b(dead|death|deaths|died|dying|corpses?|cadavers?|bodies|bod(?:y|ies) of|killed|slain|"
                     r"wounded|wounds?|casualt\w*|injur\w*|bleeding|blood\w*|bloodied|mass graves?|graves? of|"
                     r"burial|buried|burying|massacre\w*|atrocit\w*|skeletons?|skulls?|human remains|"
                     r"remains of (?:the )?(?:dead|soldiers?|victims?|bodies|men|women|people|prisoners?|"
                     r"inmates?|civilians?)|"
                     r"mutilat\w*|amputat\w*|amputees?|charred|burned alive|cremat\w*|exhum\w*|fatalit\w*|"
                     r"stretchers?|litters?|gunshot|shrapnel|severed|decompos\w*|starv\w*|emaciat\w*|burn victims?|"
                     r"hit by (?:a |an )?(?:fire ?bomb|bomb|shell|bullet|shrapnel|sniper)|"
                     r"carcass\w*|morgue|body bags?)\b", re.I)
# Sexual violence: always left out.
SEXUAL_VIOLENCE = re.compile(r"\b(rape[ds]?|raping|rapists?|sexual(?:ly)? (?:assault\w*|abuse\w*|violence|"
                             r"slavery|exploit\w*)|molest\w*|forced prostitution|comfort women)\b", re.I)
# Scenes of killing and torture (and the like): left out unless the record is evidence (EVIDENCE).
KILLING = re.compile(r"\b(tortur\w*|execut(?:e|ed|es|ing|ion|ions|ioners?)|behead\w*|hanged|hangings?|gallows|"
                     r"lynch\w*|firing squad|shot dead|shooting of (?:the )?(?:prisoners?|civilians?|hostages?)|"
                     r"being shot|about to be shot)\b", re.I)
# A documented historical record presented as evidence: liberation of the camps, exhumations, war-crimes
# investigations and trials.
EVIDENCE = re.compile(r"\b(liberat\w*|exhum\w*|war crimes?|evidence|investigat\w*|tribunal|trials?|documented|"
                      r"documenting|inspection tour|forced confrontation)\b", re.I)
PROPAGANDA = re.compile(r"\bpropaganda\b", re.I)
# Old slurs found in some 1940s captions (Signal Corps and others): such captions are left out rather than repeated.
SLURS = re.compile(r"\b(japs?|nips?|niggers?|negroes|coloreds?|squaws?|redskins?|gooks?|krauts?|huns)\b", re.I)
# Words that expression_packs.CHILD takes for a child but are not one here ("infantry", "a kind of").
NOT_CHILD = re.compile(r"\binfantr\w*|\bkinds? of\b", re.I)


def child_in(*texts):
    """True when any of texts mentions a child (expression_packs.CHILD, without NOT_CHILD's look-alikes)."""
    return any(CHILD.search(NOT_CHILD.sub(" ", t or "")) for t in texts)


def not_shown(*texts):
    """True when the words of a picture (its caption and other record texts) say it must be left out: sexual
    violence, anything sexual or nude, a dead or injured child as the focus (graphic words and child words together),
    a killing or torture scene that is not presented as evidence, propaganda showing killing or the dead, or an old
    slur."""
    joined = " ".join(t for t in texts if t)
    if not joined:
        return False
    graphic = bool(GRAPHIC.search(joined))
    if SEXUAL_VIOLENCE.search(joined) or NOT_SHOWN.search(joined) or SLURS.search(joined):
        return True
    if graphic and child_in(joined):
        return True
    if KILLING.search(joined) and not EVIDENCE.search(joined):
        return True
    return bool(PROPAGANDA.search(joined) and (graphic or KILLING.search(joined)))


def rows_for(answer, credit, place="", *texts):
    """The rows of one picture (documentary_packs.picture_rows: "Describe this picture." and, with a place, "Where was
    this photo taken?"), marked "child" only when child_in finds a child in the answer or texts (so "infantry" is
    not taken for a child) and marked graphic (marked) when the answer or texts are graphic."""
    rows = [{k: v for k, v in r.items() if k != "child"} for r in picture_rows(answer, credit, place)]
    if child_in(answer, *texts):
        rows = [dict(r, child=True) for r in rows]
    return marked(rows, *texts)


def is_graphic(*texts):
    """True when the words of a picture say it shows the dead or injured, wounds or destruction with casualties."""
    return any(GRAPHIC.search(t or "") for t in texts)


def marked(rows, *texts):
    """rows with "content": "graphic" added to each when the picture's words (its rows' answers and texts) are
    graphic (is_graphic)."""
    if is_graphic(*(r.get("answer", "") for r in rows), *texts):
        return [dict(r, content="graphic") for r in rows]
    return rows


def graphic_aside(name, url, credit, licence, text="", title="", reason="", page_url="", place="", extra=None):
    """Set aside a picture of a graphic-scenes pack that passed every other check but whose caption is too short or
    not English (build_packs.needs_description), after not_shown on everything known of it. Every picture set aside
    from these packs is marked "graphic" (its words are too few to tell; the kit then uses it only with the
    graphic-scenes choice, never for picture-making) and "child" when child_in finds a child. True when set aside."""
    extra = dict(extra or {})
    known = [text, title, *(str(v) for v in extra.values())]
    if not_shown(*known):
        return False
    extra["content"] = "graphic"
    if child_in(*known):
        extra["child"] = True
    return needs_description(name, url, credit, licence, text=text, title=title, reason=reason, page_url=page_url,
                             place=place, extra=extra)


def finish_graphic(key, items, limit, workers=4, pause=0.2):
    """documentary_packs.finish (shuffle, download, twin rows), after leaving out what not_shown refuses (on every
    row's answer); the builders have marked the graphic pictures already. Says how many pictures are graphic."""
    items = [(name, url, rows) for name, url, rows in items if not not_shown(*(r["answer"] for r in rows))]
    entries = finish(key, items, limit, workers=workers, pause=pause)
    say(f"{key}: {sum(1 for _, d, r in entries if d is not None and r.get('content') == 'graphic')} pictures marked "
        "graphic")
    return entries


# US state abbreviations in old captions ("Petersburg, Va."), written out.
STATES = {"Ala.": "Alabama", "Ark.": "Arkansas", "Cal.": "California", "Calif.": "California", "Colo.": "Colorado",
          "Conn.": "Connecticut", "Del.": "Delaware", "D.C.": "D.C.", "Fla.": "Florida", "Ga.": "Georgia",
          "Ill.": "Illinois", "Ind.": "Indiana", "Kan.": "Kansas", "Ky.": "Kentucky", "La.": "Louisiana",
          "Md.": "Maryland", "MD": "Maryland", "Mass.": "Massachusetts", "Mich.": "Michigan", "Minn.": "Minnesota",
          "Miss.": "Mississippi", "Mo.": "Missouri", "N.C.": "North Carolina", "N.J.": "New Jersey",
          "N.Y.": "New York", "Neb.": "Nebraska", "Okla.": "Oklahoma", "Pa.": "Pennsylvania",
          "S.C.": "South Carolina", "Tenn.": "Tennessee", "Tex.": "Texas", "Va.": "Virginia", "Vt.": "Vermont",
          "W.Va.": "West Virginia", "Wis.": "Wisconsin"}
STATE_WORDS = re.compile(r"(?<![\w.])(" + "|".join(re.escape(k) for k in sorted(STATES, key=len, reverse=True))
                         + r")(?=[\s,;)\]]|$)")


def caption_of(text, most=80):
    """A record's caption as an answer: tidied (documentary_packs.tidy), US state abbreviations written out, at most
    about most words, put in sentence case when it was typed in capitals."""
    text = re.sub(r"\s*\(v\.\s*\d+,\s*p\.\s*\d+[^)]*\)", "", clean(text))   # "(v.7, p. 313, ...)": a book reference
    text = STATE_WORDS.sub(lambda m: STATES[m.group(1)], text)
    letters = [c for c in text if c.isalpha()]
    if len(letters) > 10 and sum(c.isupper() for c in letters) >= 0.8 * len(letters):
        text = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text.lower())
    return tidy(capped_words(text, most))


def words(text):
    """How many words text has."""
    return len(text.split())


# ----------------------------------------------------------------- Library of Congress

LOC_NOT_A_PHOTO = re.compile(r"\b(maps?|plans?|drawings?|diagrams?|charts?|graphs?|title cards?|caption cards?|"
                             r"untitled|sheet music|"
                             r"cartoons?|posters?|prints? \(?engraving)\b", re.I)
CIVIL_WAR = "A photograph from the American Civil War, 1861 to 1865."
CRIMEA = "A photograph by Roger Fenton from the Crimean War, 1855."
BAIN = "A news photograph from the Bain News Service, about 1900 to 1920."
# key: [(search address, extra parameters, the most records the search gives, credit name, sentence added, words the
#        title itself must have)]
LOC_GRAPHIC_SETS = {
    "loc_civil_war": [
        ("collections/civil-war-glass-negatives/", extra, 8800,
         "Civil War Glass Negatives and Related Prints, Library of Congress, Prints and Photographs Division",
         CIVIL_WAR, 4)
        for extra in ({}, {"q": "dead"}, {"q": "wounded"}, {"q": "ruins"}, {"q": "hospital"}, {"q": "burial"})] + [
        ("collections/fenton-crimean-war-photographs/", {}, 270,
         "Roger Fenton Crimean War Photograph Collection, Library of Congress, Prints and Photographs Division",
         CRIMEA, 4)],
    "loc_war_disaster": [
        ("photos/", {"fa": "partof:bain collection", "q": word}, 1500,
         "George Grantham Bain Collection, Library of Congress, Prints and Photographs Division", BAIN, 4)
        for word in ("ruins", "wounded", "war", "earthquake", "flood", "fire", "explosion", "wreck", "red cross")] + [
        ("collections/fsa-owi-black-and-white-negatives/", {"q": word}, 1500,
         "U.S. Farm Security Administration/Office of War Information Black & White Photographs, Library of "
         "Congress, Prints and Photographs Division", "", 6)
        for word in ("flood", "fire", "tornado", "air raid", "first aid", "civilian defense", "refugees",
                     "bombed", "wounded", "dust storm")],
}


def loc_free(record):
    """True when the Library says the photo has no known restrictions on publication (its rights advisory may be a
    text or a list of texts) and it is online."""
    advisory = (record.get("item") or {}).get("rights_advisory") or ""
    if isinstance(advisory, list):
        advisory = " ".join(str(a) for a in advisory)
    return not record.get("access_restricted") and clean(advisory).lower().startswith("no known restrictions")


def loc_graphic_items(s, path, extra, total, name, added, least, want, rng, answers):
    """[(name, picture address, rows)] from random result pages of one Library of Congress collection or search
    (at most 30 pages), a few from each page and each caption once (answers: the captions taken so far, shared by
    the whole pack). The title must be at least least words; added (a sentence about the collection) is put after
    it. The Library asks programs to keep to about one request a second, so each page waits."""
    def page_of(number):
        """One page of 100 results (JSON), after the wait the Library asks for."""
        time.sleep(2)
        return get_json(s, LOC + path, {"fo": "json", "c": 100, "sp": number, "at": "results,pagination", **extra},
                        pause=15) or {}
    first = page_of(1)
    total = min(total, int(((first.get("pagination") or {}).get("of")) or 0))
    pages = list(range(1, total // 100 + 2))
    rng.shuffle(pages)
    items = []
    per_page = max(3, want // 10)
    for page in pages[:30]:
        if listing_out_of_time():          # leave the rest of the time for fetching what was found
            break
        taken = 0
        results = (first if page == 1 else page_of(page)).get("results") or []
        for record in results:
            title = clean(record.get("title"))
            caption = caption_of(title)
            picture = loc_picture(record)
            if not loc_free(record) or not picture or LOC_NOT_A_PHOTO.search(title) \
                    or caption.lower() in answers or taken >= per_page:
                continue
            answer = f"{caption} {added}".strip()
            item = record.get("item") or {}
            summary = clean(item.get("summary"))
            if words(caption) < least or words(answer) < 6:     # free, a photo, too short a title: set aside
                link = re.sub(r"^(https?:)?//", "https://", item.get("link") or record.get("id") or "")
                control = re.sub(r"\W", "", str(item.get("control_number") or item.get("id") or len(items)))
                graphic_aside(f"loc-{control}.jpg", picture, f"{title[:150]}, {name}, no known restrictions on "
                              f"publication, {link}", "no known restrictions on publication", text=caption,
                              title=title, page_url=link, place=loc_place(record),
                              reason=f"its title is under {max(least, 6)} words",
                              extra={"summary": summary, "collection": name.split(",")[0],
                                     "search": extra.get("q", "")})
                continue
            if not_shown(answer, summary):
                continue
            answers.add(caption.lower())
            taken += 1
            link = re.sub(r"^(https?:)?//", "https://", item.get("link") or record.get("id") or "")
            credit = f"{title[:150]}, {name}, no known restrictions on publication, {link}"
            control = re.sub(r"\W", "", str(item.get("control_number") or item.get("id") or len(items)))
            items.append((f"loc-{control}.jpg", picture,
                          rows_for(answer, credit, loc_place(record), summary)))
        if len(items) >= want:
            break
    say(f"  {name.split(',')[0]} {extra.get('q', '')}: {len(items)} usable records")
    return items


def build_loc_graphic(key, limit):
    """A Library of Congress pack of LOC_GRAPHIC_SETS: records from each set (the first set of loc_civil_war, the
    big one, gets most), their titles as answers."""
    s, rng, items, answers = session(), pass_random(sum(map(ord, key))), [], set()
    sets = LOC_GRAPHIC_SETS[key]
    total = sum(n for _, _, n, _, _, _ in sets)
    for path, extra, n, name, added, least in sets:
        if listing_out_of_time():
            break
        share = max(1 / (len(sets) * 2), n / total)
        items += loc_graphic_items(s, path, extra, n, name, added, least, int(limit * share * 1.4) + 4, rng, answers)
    return finish_graphic(key, items, limit, workers=3, pause=0.5)


def build_loc_civil_war(limit):
    """The Civil War and Crimean War pack (see the module docstring)."""
    return build_loc_graphic("loc_civil_war", limit)


def build_loc_war_disaster(limit):
    """The Bain and FSA/OWI war and disaster pack (see the module docstring)."""
    return build_loc_graphic("loc_war_disaster", limit)


# ----------------------------------------------------------------- US National Archives (Signal Corps)

NARA = "https://catalog.archives.gov/"
NARA_SEARCH = NARA + "proxy/records/search"           # the catalogue's own public search (the v2 API needs a key)
NARA_SIGNAL_CORPS = 530707          # Photographs of American Military Activities, ca. 1918 - ca. 1981 (111-SC)
NARA_SERIES_NAME = ("Photographs of American Military Activities, ca. 1918 - ca. 1981, Records of the Office of the "
                    "Chief Signal Officer (111-SC)")
NARA_WORDS = ("wounded", "casualties", "dead", "killed", "litter", "aid station", "evacuation hospital", "medics",
              "ruins", "destroyed", "bomb damage", "rubble", "refugees", "civilians", "burning", "mine field",
              "booby trap", "shell hole", "flood", "Korea wounded", "Vietnam wounded", "first aid")
NARA_MOST_BYTES = 30_000_000        # the Signal Corps scans are JPEGs of about 22 MB; larger files are left out
NARA_NOTES = re.compile(r"\s*\((?:NOTE:[^)]*|[^)]*FICHE[^)]*)\)|^\s*(?:Original caption:\s*)?(?:Photograph of\s+)?|"
                        r"\s*\b\d{2,3}-SC-\d+\w*\b|\s*\bPhotographer:.*$", re.I)
# A heading of capitalised words before a Signal Corps caption ("KOREA KOREAN CONFLICT Three Korean women ...").
NARA_HEADING = re.compile(r"^(?:[A-Z][A-Z.'-]+\s+){2,}(?=[A-Z][a-z])")


def nara_picture(record):
    """The address of a record's picture: a ready-made thumbnail or smaller copy when the record has one, else its
    JPEG (or GIF) under NARA_MOST_BYTES; "" when there is none."""
    best, best_rank = "", 9
    for obj in record.get("digitalObjects") or []:
        for key in ("objectThumbnailUrl", "thumbnailUrl"):
            if obj.get(key):
                return obj[key]
        kind, url = obj.get("objectType") or "", obj.get("objectUrl") or ""
        size = int(obj.get("objectFileSize") or 0)
        if not url or not size or size > NARA_MOST_BYTES:
            continue
        rank = 0 if "JPG" in kind or "JPEG" in kind else 1 if "GIF" in kind else 9
        if rank < best_rank:
            best, best_rank = url, rank
    return best


def nara_search(s, params, tries=6):
    """One page of the catalogue's search (JSON), trying again when the catalogue answers with its web page instead
    (it does so when busy); None when it never answered."""
    for attempt in range(tries):
        try:
            r = s.get(NARA_SEARCH, params=params, timeout=120)
            if r.status_code == 200 and r.text.lstrip().startswith("{"):
                return r.json()
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(15 * (attempt + 1))
    return None


def nara_place(record):
    """The place of a NARA record from its geographic subject headings ("Bastogne (Belgium)" -> "Bastogne,
    Belgium"); "" when none names a country this file knows."""
    for subject in record.get("subjects") or []:
        if subject.get("authorityType") != "geographicPlaceName":
            continue
        heading = clean(subject.get("heading")).strip(" .")
        m = re.match(r"^(.+?)\s*\(([^()]+)\)$", heading)
        if m:
            region = STATES.get(m.group(2).strip(), m.group(2).strip())
            if region in STATES.values():
                return place_name(m.group(1), region, "USA")
            country = country_named(region)
            if country:
                return place_name(m.group(1), country)
        elif country_named(heading):
            return country_named(heading)
    return ""


def build_nara_war(limit):
    """The NARA Signal Corps pack: for each of NARA_WORDS, a few random pages of the series' search, the records
    marked "Unrestricted" with a picture, their title (or scope note when it is longer) as the answer."""
    s, rng, items, answers = session(), pass_random(83), [], set()
    want = int(limit * 1.4 / len(NARA_WORDS)) + 3
    for word in NARA_WORDS:
        found = 0
        first = nara_search(s, {"ancestorNaId": NARA_SIGNAL_CORPS, "availableOnline": "true", "limit": 100,
                                "page": 1, "q": word})
        total = int(((((first or {}).get("body") or {}).get("hits") or {}).get("total") or {}).get("value") or 0)
        pages = list(range(1, max(1, min(total, 10000) // 100) + 1))
        rng.shuffle(pages)
        for page in pages[:6]:
            if listing_out_of_time():          # leave the rest of the time for fetching
                break
            data = first if page == 1 else nara_search(s, {"ancestorNaId": NARA_SIGNAL_CORPS,
                                                           "availableOnline": "true", "limit": 100, "page": page,
                                                           "q": word})
            time.sleep(1)
            for hit in (((data or {}).get("body") or {}).get("hits") or {}).get("hits") or []:
                record = (hit.get("_source") or {}).get("record") or {}
                if (record.get("useRestriction") or {}).get("status") != "Unrestricted" or found >= want:
                    continue
                title, note = clean(record.get("title")), clean(record.get("scopeAndContentNote"))
                text = note if words(note) > words(title) and words(note) < 120 else title
                answer = caption_of(NARA_NOTES.sub("", NARA_HEADING.sub("", text)))
                picture = nara_picture(record)
                if not picture or answer.lower() in answers or LOC_NOT_A_PHOTO.search(title):
                    continue
                if words(answer) < 6:                    # free, a photo, a too short caption: set aside
                    graphic_aside(f"nara-{record.get('naId')}.jpg", picture,
                                  f"{title[:150]}, {NARA_SERIES_NAME}, U.S. National Archives and Records "
                                  f"Administration, public domain (US government work), {NARA}id/{record.get('naId')}",
                                  "public domain (US government work)", text=answer, title=title,
                                  page_url=f"{NARA}id/{record.get('naId')}", place=nara_place(record),
                                  reason="its caption is under six words", extra={"note": note, "search": word})
                    continue
                if not_shown(answer, title, note):
                    continue
                answers.add(answer.lower())
                found += 1
                credit = (f"{title[:150]}, {NARA_SERIES_NAME}, U.S. National Archives and Records Administration, "
                          f"public domain (US government work), {NARA}id/{record.get('naId')}")
                items.append((f"nara-{record.get('naId')}.jpg", picture,
                              rows_for(answer, credit, nara_place(record), title, note)))
            if found >= want:
                break
        say(f"  NARA Signal Corps '{word}': {found} usable records")
    return finish_graphic("nara_war", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- US Holocaust Memorial Museum

USHMM = "https://collections.ushmm.org/search/"
USHMM_PICTURE = "https://collections.ushmm.org/iiif-b/assets/{}"
USHMM_TERMS = "https://www.ushmm.org/copyright-and-legal-information/terms-of-use"
USHMM_WORDS = ("liberation", "survivors", "corpses", "mass grave", "atrocities", "concentration camp", "ghetto",
               "deportation", "displaced persons", "war crimes trial", "ruins", "refugees", "", "")


def ushmm_place(geography):
    """The place of a USHMM record from its geography ("Ohrdruf, [Thuringia] Germany" -> "Ohrdruf, Germany";
    "Auschwitz, [Upper Silesia] Poland" -> "Auschwitz, Poland"); "" when the last word is not a country this file
    knows (old country names such as "Czechoslovakia" or "Yugoslavia" give no place)."""
    text = re.sub(r"\[[^\]]*\]", " ", clean(geography))
    parts = [p.strip(" ,.") for p in text.split(",") if p.strip(" ,.")]
    if not parts:
        return ""
    last = parts[-1].split()
    country = country_named(" ".join(last[-2:])) or country_named(last[-1]) if last else ""
    if not country:
        return ""
    town = parts[0] if len(parts) > 1 else ""
    return place_name(town, country)


def build_ushmm(limit):
    """The USHMM pack: photographs whose only rights statement is "Public Domain", found with USHMM_WORDS (the
    empty word: random pages of all of them), the museum's caption as the answer and the place from the record.
    The museum's keywords (CORPSES, HUMAN REMAINS ...) count when the pictures are marked graphic."""
    s, rng, items, seen = session(), pass_random(89), [], set()
    want = int(limit * 1.4 / len(USHMM_WORDS)) + 3
    for word in USHMM_WORDS:
        found = 0
        params = {"per_page": 100, "f[record_type_facet][]": "Photograph", "f[photo_copyright][]": "Public Domain"}
        if word:
            params["q"] = word
        first = get_json(s, USHMM + "catalog.json", dict(params, page=1)) or {}
        total_pages = int((((first.get("response") or {}).get("pages") or {}).get("total_pages")) or 1)
        pages = list(range(1, total_pages + 1))
        rng.shuffle(pages)
        for page in pages[:4]:
            if listing_out_of_time():          # leave the rest of the time for fetching
                break
            time.sleep(1)
            data = first if page == 1 else get_json(s, USHMM + "catalog.json", dict(params, page=page)) or {}
            for doc in (data.get("response") or {}).get("docs") or []:
                rights = set(doc.get("photo_copyright") or [])
                resource = (doc.get("pho_resource") or [""])[0]
                if rights != {"Public Domain"} or not resource or doc.get("id") in seen or found >= want:
                    continue
                caption = caption_of(doc.get("title_display") or " ".join(doc.get("title") or []), 90)
                keywords = " ".join(doc.get("keyword") or []).lower()
                if words(caption) < 6:                   # public domain with a too short caption: set aside
                    if graphic_aside(f"ushmm-{doc.get('identifier') or doc.get('id')}.jpg",
                                     USHMM_PICTURE.format(resource),
                                     f"{caption[:150] or 'Photograph'}, United States Holocaust Memorial Museum photo "
                                     f"archive, photograph {doc.get('identifier')}, Copyright: Public Domain, "
                                     f"{USHMM}catalog/{doc.get('id')} ; terms: {USHMM_TERMS}", "Public Domain",
                                     text=caption, page_url=f"{USHMM}catalog/{doc.get('id')}",
                                     place=ushmm_place(" ".join(doc.get("geography") or [])),
                                     reason="its caption is under six words",
                                     extra={"keywords": keywords[:300],
                                            "date": clean(" ".join(doc.get("display_date") or []))}):
                        seen.add(doc.get("id"))
                    continue
                if not_shown(caption, keywords):
                    continue
                seen.add(doc.get("id"))
                found += 1
                date = clean(" ".join(doc.get("display_date") or []))
                credit = (f"{caption[:150]}" + (f" ({date})" if date else "") + ", United States Holocaust Memorial "
                          f"Museum photo archive, photograph {doc.get('identifier')}, Copyright: Public Domain, "
                          f"{USHMM}catalog/{doc.get('id')} ; terms: {USHMM_TERMS}")
                place = ushmm_place(" ".join(doc.get("geography") or []))
                items.append((f"ushmm-{doc.get('identifier') or doc.get('id')}.jpg", USHMM_PICTURE.format(resource),
                              rows_for(caption, credit, place, keywords)))
            if found >= want:
                break
        say(f"  USHMM '{word or 'any'}': {found} usable photographs")
    return finish_graphic("ushmm", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- Wikimedia Commons

# Subcategories that are not photographs of the scene itself (art, memorials, maps ...) or whose focus is children.
COMMONS_NOT_IT = re.compile(r"\b(art|arts|artworks?|drawings?|illustrations?|paintings?|sculptures?|statues?|"
                            r"memorials?|monuments?|cemeter\w*|graves?|gravestones?|tombs?|posters?|propaganda|"
                            r"cartoons?|comics?|maps?|diagrams?|logos?|icons?|stamps?|coins?|videos?|films?|audio|"
                            r"executions?|hangings?|torture|nude|naked|in fiction|in literature|reenact\w*|"
                            r"museums? exhibits?|models?|toys?|games?|svg|charts?|graphs?|documents?|letters?|"
                            r"newspapers?|portraits?|people by name)\b", re.I)
# A description that is not in English or is not a description (codes, other scripts).
NOT_ENGLISH = re.compile(r"[^\x00-ɏ‐-‧]|\b[a-z]{2}:\S")
# Descriptions that are catalogue records rather than descriptions ("Format: Lysbilde / Dias Dato / Date: 1952 ...").
METADATA = re.compile(r"\b(format|dato|date|fotograf|photographer|sted|place|photo source|source|digitized by|"
                      r"oppdatert|update|author|license|licence|camera|wikipedia|accession|object number)\s*:", re.I)
ENGLISH_WORDS = re.compile(r"\b(the|of|in|and|on|after|with|at|by|from|a|an|is|are|was|were)\b", re.I)

COMMONS_WAR = {
    # category: whether one level of its subcategories is used too
    "War casualties": True, "Wounded soldiers": True, "Casualties of World War I": True,
    "Civilian casualties of World War II": True, "Casualties of the Korean War": True,
    "Casualties of the Vietnam War": True, "Casualties of the Iraq War": True, "Dead soldiers": True,
    "World War II transport of wounded": True, "Wounded soldiers in Second Boer War": False,
    "Field hospitals": True, "Holocaust victims": True, "Liberation of Nazi concentration camps": True,
    "Aftermath of World War I": True, "Aftermath of World War II": True, "Hiroshima in ruins": True,
    "Nagasaki in ruins": True, "Ruins in Warsaw after WWII": True, "Bombing of Dresden in World War II": True,
    "The Blitz": True, "Bomb craters": True, "Destroyed buildings in Syria": True,
    "Destroyed in Syria in the 2010s": True, "Destructions during the 2022 Russian invasion of Ukraine": True,
    "War damages in Kyiv Oblast (2022 Russian invasion of Ukraine)": True,
    "War damages in Odesa (2022 Russian invasion of Ukraine)": True,
    "Damaged infrastructure in the 2022 Russian invasion of Ukraine": True,
    "Damaged medical buildings in the 2022 Russian invasion of Ukraine": True,
    "Rocket strike on a shopping center in Kremenchuk, 27 June 2022": False,
    "Destroyed vehicles in the 2022 Russian invasion of Ukraine": False,
    "National Museum of Health and Medicine": True, "Otis Historical Archives": False,
}
COMMONS_DISASTERS = {
    "Earthquake damage": True, "Earthquake damage in California": True,
    "Buildings damaged by the 2010 Canterbury earthquake": True, "2010 Haiti earthquake damage": True,
    "Damage of the 2023 Kahramanmaraş earthquakes in Adıyaman": False, "Flood damage": True, "Floods": True,
    "2011 Brisbane flood damage": False, "Johnstown Flood": True, "1966 flood of Florence": True,
    "Bridges destroyed by floods": True, "Tornado damage": True, "Landslides": True, "Collapsed buildings": True,
    "Debris": True, "Rubble": True, "House fires": True,
    "Images from FEMA": True,
}
# The practical safety scenes: category -> (question, answer about the hazard or sign, whether one level of its
# subcategories is used too). The answers describe; they never give tactical or weapon-use advice.
HAZARDS = "What hazards are in this picture?"
SIGN = "What does this sign mean?"
PLACE_Q = "What kind of place is this?"
SAFETY = {
    "Downed power lines": (HAZARDS, "Power lines have fallen down here. A fallen line may still be live, and the "
                                    "ground or water around it can carry electricity.", False),
    "Flooded roads": (HAZARDS, "The road is flooded. The water hides the road surface, holes and the edge of the "
                               "road, and moving water can sweep a person or a car away.", True),
    "Smoke": (HAZARDS, "There is smoke in this picture: it can hide the way ahead and make breathing hard.", False),
    "Burning buildings": (HAZARDS, "A building is on fire: there are flames and smoke.", True),
    "House fires": (HAZARDS, "A house is on fire or has burned: there are flames, smoke or charred ruins.", False),
    "Collapsed buildings": (HAZARDS, "A building has collapsed: its walls and floors have fallen into rubble, and "
                                     "what is still standing may fall.", False),
    "Rubble": (HAZARDS, "There is rubble here: broken concrete, bricks and debris from damaged buildings.", False),
    "Unexploded ordnance": (HAZARDS, "This shows unexploded ordnance: a bomb, shell, rocket or grenade that did not "
                                     "go off and can still explode if it is touched or moved.", True),
    "Unexploded ordnance warning signs": (SIGN, "It warns of unexploded ordnance: bombs or shells that did not go "
                                                "off may be in the ground here, and the area is dangerous.", False),
    "Landmine warning signs": (SIGN, "It warns of landmines: the area beyond it may have mines in the ground and is "
                                     "dangerous to enter.", True),
    "Checkpoints": (PLACE_Q, "It is a checkpoint, where guards or soldiers stop people and vehicles to check them "
                             "before they pass.", True),
    "Military checkpoints": (PLACE_Q, "It is a military checkpoint, where soldiers stop people and vehicles to "
                                      "check them before they pass.", True),
    "Barricades": (HAZARDS, "There is a barricade here, blocking the way.", True),
    "Sandbags": (PLACE_Q, "There are sandbags here, piled up as a barrier against flood water or as protection.",
                 True),
    "Air raid shelters": (PLACE_Q, "It is an air-raid shelter: a protected place, often underground, where people "
                                   "go during an air raid.", True),
    "Fallout shelter signs": (SIGN, "It marks a fallout shelter: a building or basement where people can shelter "
                                    "from radioactive fallout.", True),
    "Air raid sirens": (PLACE_Q, "It is an air-raid siren, which sounds a loud warning when an attack or another "
                                 "danger is coming.", False),
    "First aid stations": (PLACE_Q, "It is a first-aid station, where injured people are given first aid.", True),
    "Field hospitals": (PLACE_Q, "It is a field hospital: a temporary hospital, often in tents, set up near a war or "
                                 "disaster to treat the injured.", False),
    "Refugee camps": (PLACE_Q, "It is a refugee camp, where people who have fled war or disaster live in tents or "
                               "shelters.", True),
    "Evacuation route signs": (SIGN, "It is an evacuation route sign: it shows the way to leave the area in an "
                                     "emergency, such as a hurricane, a tsunami or a flood.", True),
    "Emergency exit signs": (SIGN, "It is an emergency exit sign: it shows the way out of the building in an "
                                   "emergency.", True),
    "Assembly point signs": (SIGN, "It marks an assembly point: the place where people gather after leaving a "
                                   "building in an emergency, so everyone can be counted.", True),
}


QUICK_CATEGORIES = 0        # main()'s --categories N: a quick check reads only N random categories (0: all)


def commons_answer(text):
    """A Commons caption or description as an answer: tidied and at most about 70 words; "" when it is not in
    English or shorter than 6 words."""
    answer = caption_of(text, 70)
    if words(answer) < 6 or NOT_ENGLISH.search(answer) or METADATA.search(answer) \
            or len(ENGLISH_WORDS.findall(answer)) < 1:
        return ""
    return answer


def commons_titles(s, category, deeper):
    """The file titles of a Commons category and, when deeper, of one level of its subcategories (leaving out the
    subcategories COMMONS_NOT_IT names and those about children, such as "Child casualties"); file names that
    COMMONS_NOT_IT names are left out too."""
    try:
        titles = commons_members(s, category, "file")
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                sub = sub.split(":", 1)[-1]
                if not COMMONS_NOT_IT.search(sub) and not child_in(sub):
                    titles += commons_members(s, sub, "file")
    except Exception as e:  # noqa: BLE001 - a missing or refused category is left out
        say(f"  Commons {category}: left out ({str(e)[:100]})")
        return []
    return [t for t in dict.fromkeys(titles) if not COMMONS_NOT_IT.search(t)]


def build_commons(key, categories, limit, safety=False):
    """A Commons pack: for each category, its files (see commons_titles) whose licence is CC0, public domain or CC BY
    (food_packs.commons_entries), each with its English caption or description as "Describe this picture." and, for
    the safety categories (safety=True: categories is SAFETY), the category's question and answer too. The
    categories share the limit; a file is used once, under the first category it is met in."""
    s, items, seen = session(), [], set()
    if QUICK_CATEGORIES:                              # a quick check (main --categories): only a few categories
        categories = dict(pass_random(key).sample(sorted(categories.items()), min(QUICK_CATEGORIES,
                                                                                     len(categories))))
    per_category = max(6, limit // len(categories) * 2)
    for category, value in categories.items():
        question, answer, deeper = value if safety else (None, None, value)
        titles = commons_titles(s, category, deeper)
        titles = [t for t in titles if t not in seen]
        pass_random(category).shuffle(titles)
        found = 0
        try:
            refused = False
            entries = list(commons_entries(s, titles[:per_category * 3]))
        except RuntimeError as e:                    # Commons kept refusing: keep what was found and stop asking
            say(f"  Commons {category}: {e} The pack keeps the {len(items)} pictures found so far.")
            entries, refused = [], True
        for title, url, credit, text in entries:
            described = commons_answer(text)
            name_words = re.sub(r"[_-]+", " ", title.split(":", 1)[-1].rsplit(".", 1)[0])
            if not_shown(described, name_words):
                continue
            if not described and not question:       # free, but no English caption of six words: set aside
                stem = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
                graphic_aside(f"{key.replace('_', '-')}-{stem}.jpg",
                              re.sub(r"/\d+px-([^/]+)$", r"/1280px-\1", url), credit, credit_licence(credit),
                              text=caption_of(text, 70), title=name_words,
                              page_url="https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                              place=commons_place(title).get("place", ""),
                              reason="no English caption or description of six words or more",
                              extra={"category": category})
                continue
            rows = []
            if question:
                rows.append({"question": question, "answer": answer, "credit": credit})
            if described:
                rows.append({"question": NARRATE, "answer": described, "credit": credit})
            if child_in(described, name_words):
                rows = [dict(r, child=True) for r in rows]
            rows = [dict(r, **commons_place(title)) for r in rows]
            if is_graphic(described, name_words):    # the file's own words (not the category's answer) decide
                rows = [dict(r, content="graphic") for r in rows]
            seen.add(title)
            name = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
            items.append((f"{key.replace('_', '-')}-{name}.jpg", re.sub(r"/\d+px-([^/]+)$", r"/1280px-\1", url),
                          rows))
            found += 1
            if found >= per_category:
                break
        say(f"  Commons {category}: {found} free pictures ({len(titles)} files)")
        if refused:
            break
    return finish_graphic(key, items, limit, workers=2, pause=0.5)


def build_commons_war(limit):
    """The Commons war pack (see the module docstring)."""
    return build_commons("commons_war", COMMONS_WAR, limit)


def build_commons_disasters(limit):
    """The Commons disasters pack (see the module docstring)."""
    return build_commons("commons_disasters", COMMONS_DISASTERS, limit)


def build_commons_safety(limit):
    """The Commons practical safety pack (see the module docstring)."""
    return build_commons("commons_safety", SAFETY, limit, safety=True)


# ----------------------------------------------------------------- the packs

LOC_TERMS = "https://www.loc.gov/legal/ (Prints and Photographs Division rights statements)"
COMMONS_TERMS = ("captions CC0; pictures CC0, public domain or CC BY, each with its author below (the CC BY-SA files "
                 "are a share-alike kit entry)")
GRAPHIC_NOTE = ("Graphic scenes (war, disasters, injuries and death) are described plainly; rows marked 'graphic' are "
                "used only when the graphic-scenes choice is made, and never for picture-making.")

GRAPHIC_PACKS = {
    "loc_civil_war": (build_loc_civil_war, "Civil War Glass Negatives and Related Prints, and the Roger Fenton Crimean "
                                           "War Photograph Collection, Library of Congress, Prints and Photographs "
                                           "Division, https://www.loc.gov/collections/civil-war-glass-negatives/ : 'No "
                                           f"known restrictions on publication'. Titles from the Library's records. "
                                           f"{LOC_TERMS} {GRAPHIC_NOTE}"),
    "loc_war_disaster": (build_loc_war_disaster, "George Grantham Bain Collection and U.S. Farm Security "
                                                 "Administration/Office of War Information photographs, Library of "
                                                 "Congress, Prints and Photographs Division, https://www.loc.gov/"
                                                 "pictures/collection/ggbain/ : 'No known restrictions on "
                                                 f"publication'. Captions from the Library's records. {LOC_TERMS} "
                                                 + GRAPHIC_NOTE),
    "nara_war": (build_nara_war, f"{NARA_SERIES_NAME}, U.S. National Archives and Records Administration, "
                                 f"{NARA}id/{NARA_SIGNAL_CORPS} : US government work, public domain; only records "
                                 f"marked 'Unrestricted'. Captions by the Signal Corps. {GRAPHIC_NOTE}"),
    "ushmm": (build_ushmm, "United States Holocaust Memorial Museum photo archive, https://collections.ushmm.org/search/"
                           " : only photographs whose record says 'Copyright: Public Domain' (mostly US Army Signal "
                           f"Corps photographs held by the National Archives); terms of use: {USHMM_TERMS}. Captions "
                           f"by the museum. {GRAPHIC_NOTE}"),
    "commons_war": (build_commons_war, "Wikimedia Commons, war casualties, aftermath, ruins and war-damage categories, "
                                       f"https://commons.wikimedia.org/wiki/Category:War_casualties : {COMMONS_TERMS}. "
                                       + GRAPHIC_NOTE),
    "commons_disasters": (build_commons_disasters, "Wikimedia Commons, earthquake, flood, tornado, landslide and fire "
                                                   "damage categories and the FEMA photographs, https://commons."
                                                   f"wikimedia.org/wiki/Category:Earthquake_damage : {COMMONS_TERMS}. "
                                                   + GRAPHIC_NOTE),
    "commons_safety": (build_commons_safety, "Wikimedia Commons, practical safety scenes (fallen power lines, flooded "
                                             "roads, fire and smoke, unexploded ordnance and mine warning signs, "
                                             "checkpoints, shelters, first aid, evacuation signs), "
                                             f"https://commons.wikimedia.org : {COMMONS_TERMS}. The answers about each "
                                             "hazard or sign were written for the pack. " + GRAPHIC_NOTE),
}

# How many pictures a full build takes from each collection.
GRAPHIC_LIMITS = {
    "loc_civil_war": 3000,          # of about 9,000 records (many are stereo pairs or the same title twice)
    "loc_war_disaster": 3000,       # from the Bain and FSA/OWI war and disaster searches
    "nara_war": 1500,               # of about 100,000 Signal Corps records; their scans are large (about 22 MB each)
    "ushmm": 2500,                  # of about 3,900 public-domain photographs
    "commons_war": 2500,            # free files of the war categories
    "commons_disasters": 2500,      # free files of the disaster categories
    "commons_safety": 2000,         # free files of the safety categories
}


def main(argv=None):
    """Run one builder with a small limit and print the title and answers of its rows (a quick check that writes
    nothing; pictures are not shown)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one graphic pack builder.")
    parser.add_argument("key", choices=sorted(GRAPHIC_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--categories", type=int, default=0,
                        help="Commons packs: read only this many random categories (a quicker check)")
    args = parser.parse_args(argv)
    global QUICK_CATEGORIES
    QUICK_CATEGORIES = args.categories
    entries = GRAPHIC_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name or row.get("file"), "picture": data is not None, "question": row["question"],
                        "answer": row["answer"], "content": row.get("content", ""), "child": bool(row.get("child")),
                        "place": row.get("place", "")}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, d, r in entries if d is not None and r.get('content') == 'graphic')} pictures marked graphic, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
