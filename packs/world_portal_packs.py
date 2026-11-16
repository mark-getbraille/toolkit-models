"""Pack builders for open picture collections found by searching national open-data portals, Zenodo and Europeana's
Hungarian, Greek, Norwegian and Polish providers in their own languages. Used by build_packs.py in the same way as its
own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"} with an optional "place" (packs/places.py) and "child": True. A picture that has
more than one row comes once with its JPEG and then again as (None, None, row) rows whose "file" names the same
picture (food_packs.with_twins), so the zip holds each picture only once. The limit counts pictures.

  europeana_hu  Hungarian museums and libraries in MaNDA (the National Digital Archive of Hungary) through Europeana:
                the Rippl-Rónai Museum in Kaposvár (village life photographs whose titles describe them: "Nyári
                csirkeól ... deszka ajtóval"), the Porcelain Museum in Hódmezővásárhely (plates, jugs and figures
                described by shape, colour and pattern), the Kuny Domokos Museum in Tata, the Déri Museum in
                Debrecen, the Csorba Győző Library in Pécs and others. Pictures CC BY 4.0, CC0 or Public Domain Mark.
                The museum's Hungarian text is the answer; where it also wrote English, that is the English row.
  europeana_el  Greek museums through Europeana (records sent by the National Documentation Centre, EKT,
                searchculture.gr): the Philatelic and Postal Museum (postal objects described with what they are
                made of and what is written on them), the Faltaits Folk Art and Ethnographic Museum on Skyros
                (everyday tools and pottery), the Athens City Museum (photographs of Athens streets 1965-1970), the
                Laskaridis Foundation (sea paintings with long descriptions), the Historical and Ethnological
                Society of Greece (photographs of Athens monuments) and others. Pictures CC BY 4.0, CC0 or Public
                Domain Mark. Library postcards and portrait archives whose records give only a name are left out.
  europeana_no  Norwegian museums in DigitaltMuseum through Europeana: the Norwegian Museum of Cultural History
                (Norsk Folkemuseum), Domkirkeodden in Hamar, the Museum in Nord-Østerdalen, Glomdal Museum, the
                Norwegian Maritime Museum and others: photographs of homes, farms, work, transport and town life,
                with the museum's Norwegian caption ("To menn og en kvinne foran et fjøs", "Kåre Sørlie ved sin
                rutebuss, GMC 1934-modell"). Pictures CC BY 4.0, CC0 or Public Domain Mark. Lists of names ("fra
                venstre: ...") are left out.
  europeana_pl  Polish regional digital libraries and museums through Europeana (the Grodzka Gate - NN Theatre
                in Lublin, the Mazowsze, Silesian and other digital libraries): photographs and postcards whose
                Polish title or description says what they show ("Legionowo. Budowa kafara parowego w 1936 roku").
                Pictures CC BY 4.0, CC0 or Public Domain Mark.

Europeana's record text is CC0; each picture is credited with its title, museum, licence and Europeana page. The
pictures are Europeana's own 400-pixel copies (its thumbnail service), as in world_more_packs.py, whose Europeana
helpers are used here. Set EUROPEANA_KEY to use your own free key (else the public key "api2demo").

The answers are in Hungarian, Greek, Norwegian and Polish. build_packs.add_translations adds English rows only for
the pack keys in its TRANSLATE list, which this file does not change: PORTAL_TRANSLATE below names each pack's
language and a Helsinki-NLP model to add to build_packs.MT_MODELS for it (checked on Hugging Face in November 2026:
opus-mt-tc-big-hu-en CC BY 4.0, opus-mt-tc-big-el-en CC BY 4.0, opus-mt-tc-big-gmq-en already used for Swedish, and
opus-mt-pl-en Apache 2.0). Rows whose museum wrote English are marked "twinned" and are not translated.

Collections looked at and left out (checked at the source in November 2026), with the reason:
  Marseille - Photographies 1/3, 2/3, 3/3 (data.gouv.fr, Ville de Marseille, Licence Ouverte 2.0, public domain
    prints, 277 photographs with long French descriptions and coordinates): open, but the picture server
    donneesculturelles.e-mrs.fr reset every connection from this machine, so it could not be built or tested.
  Fonds de la Guerre 14-18 (data.gouv.fr, Ministère de la Culture, base Mémoire, 18,982 photos, Licence Ouverte for
    the records): each picture's own notice says "Ministère de la Culture - Médiathèque ... - Diffusion RMN", so the
    pictures' terms are not clearly open; many show war damage and the dead.
  Museums Victoria Collections API (Australia, CC BY and public domain): answers programs with a Cloudflare
    "Just a moment..." page.
  open.canada.ca (Ingenium artefacts and others): the portal rejected requests from this machine; Ingenium's object
    pictures are CC BY-NC-ND in any case (the OGL covers only its records).
  Image and Sound Archive of Menorca, Digital Memory of Catalonia (Europeana, Spain): records carry only a title in
    brackets or a collection-wide text, or are posters.
  Hellenic Literary and Historical Archive (ELIA), Veria Central Public Library (Europeana, Greece): records give only a
    person's name or a postcard's catalogue line.
  Polish university libraries (Wrocław, Jagiellonian): mostly book pages, maps and prints with catalogue text.

Answers are the collections' own words (nothing is written by an AI model); the questions are fixed sentences.

    python packs/world_portal_packs.py europeana_hu --limit 8      (prints a few rows: a quick check of one builder)
"""

import json
import random
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, fetch_all, say
from food_packs import with_twins, count_pictures
from world_packs import capped_words, full_stop, ASK_EN
from world_more_packs import (ASK, mentions_child, marked, eu_providers, eu_records, eu_licence, eu_picture,
                              eu_credit)
from places import country_named, place_name, where


# ----------------------------------------------------------------- shared helpers

# Child words these four languages need beyond world_more_packs.CHILD_MORE (wide on purpose, as there).
CHILD_EXTRA = re.compile(r"\b(pike|piker|pikene|småbarn|spedbarn\w*|skolebarn\w*|fiú\w*|lány\w*|csecsem\w*|óvod\w*|"
                         r"iskolás\w*|νήπι\w*|μαθητ\w*|dzie(c|ck)\w*|uczni\w*|uczenni\w*)\b", re.I)
# Records that mention nudity are left out (no sexual content; nude art has its own pack and rules).
NUDE = re.compile(r"naken|nakne|akt\b|aktkép|meztelen|γυμν|nag(i|a|ie|ich)\b|akt(y|u|em)?\b|nude|naked", re.I)
# Parts of a description that are catalogue notes, not what the picture shows.
CATALOGUE = re.compile(r"inventory number|^\s*(wymiary|méret|mérete|dimensions?)\b|\d+([,.]\d+)?\s*[x×χΧ]\s*\d+"
                       r"([,.]\d+)?\s*(cm|mm|εκ)|καρτ ποστάλ|^αντίγραφο|^νο\.|^no\.\s*\d|^k\. \d|negativet|"
                       r"innsamlingsarkiv|^\s*(fénykép|kép|fotografia|zdjęcie|φωτογραφία)\W*$|μουσείο\W*$", re.I)
# Lists of the people in a photo ("fra venstre: ...", "balról jobbra: ...", "od lewej: ...").
NAME_LIST = re.compile(r"fra venstre|til høyre:|bakerste rad|første rad|foran f\.v\.|balról|jobbról|od lewej|"
                       r"od prawej|από αριστερά", re.I)
# A person's dates of birth and death ("1763. május 9. – ... 1845."), as in a biography rather than a description.
LIFE_DATES = re.compile(r"\(\s*[^()]*\d{4}[^()]*[–-][^()]*\d{4}\s*\)|\d{4}\.\s*\w+\s*\d{1,2}\.\s*[–-]")


def first_line(text):
    """The first line of a record text, tidied."""
    return clean(re.split(r"\s*\n\s*", str(text or "").strip())[0])


def words(text):
    """How many words a text has."""
    return len(text.split())


def sentence_case(text):
    """A caption written all in capitals ("HAMAR STADION, SKØYTER") in ordinary letters, first letter a capital."""
    if text.upper() == text and any(c.isalpha() for c in text):
        text = text.lower()
    return text[:1].upper() + text[1:]


def usable_parts(parts):
    """A record's description parts that say what the picture shows: first lines only, no catalogue notes, no lists
    of names and no biographies."""
    out = []
    for part in parts:
        line = first_line(part)
        if line and not CATALOGUE.search(line) and not NAME_LIST.search(line) and not LIFE_DATES.search(line):
            out.append(line)
    return out


def joined(title, description):
    """A short title and a description as one answer ("Falitányér. Klasszikus mélytányér forma ..."), the title left
    out when the description already starts with it or the title is long (then it is a caption of its own)."""
    if not title or words(title) > 4 or description.lower().startswith(title.lower().rstrip(".")):
        return full_stop(description)
    return full_stop(title) + " " + full_stop(description)


def lang_parts(item, language):
    """A Europeana record's description parts in one language (those not marked with any language as well)."""
    aware = item.get("dcDescriptionLangAware") or {}
    return list(aware.get(language) or []) + list(aware.get("def") or [])


def answer_from(title, local, most=70):
    """An answer from a record's title and its usable description parts in the record's language, or ""."""
    title = sentence_case(clean(title)).rstrip(" .")
    described = [p for p in local if words(p) >= 4 and p.rstrip(". ").lower() != title.lower()]
    if described:
        text = joined(title, max(described[:3], key=len))
    elif words(title) >= 5 and not NAME_LIST.search(title):
        text = full_stop(title)
    else:
        return ""
    return capped_words(text, most)


def english_from(item):
    """The museum's own English description of a record, or ""."""
    english = [p for p in usable_parts((item.get("dcDescriptionLangAware") or {}).get("en") or []) if words(p) >= 5]
    return capped_words(full_stop(english[0]), 70) if english else ""


# ----------------------------------------------------------------- the answers of each language

def hu_answer(item):
    """(Hungarian answer, English answer) of a Hungarian record."""
    title = (item.get("title") or [""])[0]
    return answer_from(title, usable_parts(lang_parts(item, "hu"))), english_from(item)


def el_answer(item):
    """(Greek answer, English answer) of a Greek record: its longest description, after its title when that is
    short ("Η Αθήνα του '65 - '70 - Κολωνάκι. Σόλωνος και Χ. Τρικούπη.")."""
    title = (item.get("title") or [""])[0]
    return answer_from(title, usable_parts(lang_parts(item, "el"))), english_from(item)


def no_answer(item):
    """(Norwegian answer, "") of a Norwegian record: a description that says more than the title, or else the
    title's last part when that is a caption ("Folldal, Rykroken, To menn og en kvinne foran et fjøs" -> "To menn og
    en kvinne foran et fjøs."; the place is in the row's place)."""
    title = sentence_case(clean((item.get("title") or [""])[0]))
    parts = usable_parts(lang_parts(item, "no"))
    caption = title.split(", ")[-1] if ", " in title else title
    if words(caption) >= 4 and caption != title:
        title = caption[:1].upper() + caption[1:]
    return answer_from(title, [sentence_case(p) for p in parts]), english_from(item)


def pl_answer(item):
    """(Polish answer, English answer) of a Polish record: its description, or a title that is a caption."""
    title = (item.get("title") or [""])[0]
    return answer_from(title, usable_parts(lang_parts(item, "pl"))), english_from(item)


# ----------------------------------------------------------------- places

def eu_place(item):
    """Where a Europeana record's picture is from, from the record's own place labels: "Folldal, Norway" from
    DigitaltMuseum's "Norge, Hedmark, Folldal, Rykroken", or a country named among the labels; "" when none."""
    country = ""
    for label in item.get("edmPlaceLabel") or []:
        text = clean(label.get("def") if isinstance(label, dict) else label)
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if len(parts) >= 3 and country_named(parts[0]):
            return place_name(parts[2], country_named(parts[0]))          # Norge, county, municipality, ...
        country = country or country_named(text)
    return country


# ----------------------------------------------------------------- the Europeana packs

PORTAL_EU = {
    "europeana_hu": {"language": "hu", "answer": hu_answer, "filters": ['COUNTRY:"Hungary"'],
                     "leave_out": {"Hungarian Theatre Museum and Institute", "Hungarian Franciscan Library and "
                                   "Archives - Budapest", "Europeana 1989", "National Archives of Hungary"},
                     "objects": {"Porcelain Museum", "Museum of Kuny Domokos - Tata"}},
    "europeana_el": {"language": "el", "answer": el_answer, "filters": ['COUNTRY:"Greece"'],
                     "only": {"Philatelic Postal Museum", "Manos & Anastasia Faltaits Folk Art & Ethnographic Museum",
                              "Athens City Museum – Vouros-Eutaxias Foundation", "Aikaterini Laskaridis Foundation",
                              "Historical & Ethnological Society of Greece",
                              "Varnavas Folklore Company of the Municipality of Marathon",
                              "Laboratory of Folklore and Social Anthropology - Department of History and Ethnology - "
                              "Democritus University of Thrace", "Municipality of Thasos",
                              "Greek Biotope - Wetland Center"},
                     "objects": {"Philatelic Postal Museum", "Manos & Anastasia Faltaits Folk Art & Ethnographic "
                                 "Museum"}},
    "europeana_no": {"language": "no", "answer": no_answer, "filters": ['COUNTRY:"Norway"'], "objects": set()},
    "europeana_pl": {"language": "pl", "answer": pl_answer, "query": "fotografia OR pocztówka OR zdjęcie",
                     "filters": ['COUNTRY:"Poland"'], "objects": set(),
                     "leave_out": {"Library of the Wroclaw University", "Jagiellonian Library", "Asia and Pacific "
                                   "Museum", "Repository of University of Wroclaw", "Digital Repository Research "
                                   "Institutes", "Toruń Regional Museum"}},
}


def build_portal_europeana(key, limit):
    """A Europeana pack: [(name, JPEG, row)], museum by museum (no museum gives more than about 40% of the pack):
    a row in the record's language and, where the museum wrote English, an English row (marked "twinned" so
    build_packs does not translate the first). Records mentioning nudity are left out."""
    source = PORTAL_EU[key]
    language, query = source["language"], source.get("query", "*")
    s, items, seen = session(), [], set()
    providers = eu_providers(s, query, source["filters"])
    providers = {p: n for p, n in providers.items() if p not in source.get("leave_out", ())
                 and ("only" not in source or p in source["only"])}
    say(f"Europeana {key}: {sum(providers.values())} records from {len(providers)} museums")
    per_museum = max(20, int(limit * 1.5 * 0.4))
    for provider, count in sorted(providers.items(), key=lambda kv: -kv[1]):
        found = 0
        for item in eu_records(s, query, source["filters"], provider, min(count, per_museum * 8)):
            licence = eu_licence(item)
            picture = eu_picture((item.get("edmIsShownBy") or [""])[0])
            answer, english = source["answer"](item)
            text = " ".join([answer, english] + list(item.get("title") or []))
            if not licence or not picture.startswith("http") or not (answer or english) or NUDE.search(text):
                continue
            if (answer or english) in seen:
                continue
            seen.add(answer or english)
            credit = eu_credit(item, licence)
            child = mentions_child(text) or bool(CHILD_EXTRA.search(text))
            place = where(eu_place(item), "origin" if provider in source["objects"] else None)
            rows = []
            if answer:
                rows.append(marked({"question": ASK[language], "answer": answer, "credit": credit, **place}, child))
            if english:
                rows.append(marked({"question": ASK_EN, "answer": english, "credit": credit, **place}, child))
                rows[0]["twinned"] = True              # build_packs.add_translations leaves it untranslated
            items.append((f"{key}-{len(items)}.jpg", picture, rows))
            found += 1
            if found >= per_museum:
                break
        say(f"  {provider}: {found} usable")
        if len(items) >= limit * 1.5:
            break
    random.Random(53).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.4) + 2], workers=4, pause=0.2)
    return with_twins(fetched[:limit])


def build_europeana_hu(limit):
    """The Hungarian museums pack (see the module docstring)."""
    return build_portal_europeana("europeana_hu", limit)


def build_europeana_el(limit):
    """The Greek museums pack (see the module docstring)."""
    return build_portal_europeana("europeana_el", limit)


def build_europeana_no(limit):
    """The Norwegian museums pack (see the module docstring)."""
    return build_portal_europeana("europeana_no", limit)


def build_europeana_pl(limit):
    """The Polish digital libraries pack (see the module docstring)."""
    return build_portal_europeana("europeana_pl", limit)


# ----------------------------------------------------------------- the packs

EU_TEXT = "record text CC0 (https://pro.europeana.eu/page/europeana-data-exchange-agreement); pictures CC BY 4.0, " \
          "CC0 or Public Domain Mark, each credited below with its museum and record."

PORTAL_PACKS = {
    "europeana_hu": (build_europeana_hu, "Hungarian museums and libraries (MaNDA: the Rippl-Rónai Museum, the "
                                         "Porcelain Museum, the Kuny Domokos Museum and others) through Europeana, "
                                         "https://www.europeana.eu: " + EU_TEXT),
    "europeana_el": (build_europeana_el, "Greek museums (the Philatelic and Postal Museum, the Faltaits Museum, the "
                                         "Athens City Museum, the Laskaridis Foundation and others, through EKT "
                                         "searchculture.gr) through Europeana, https://www.europeana.eu: " + EU_TEXT),
    "europeana_no": (build_europeana_no, "Norwegian museums in DigitaltMuseum (the Norwegian Museum of Cultural "
                                         "History, Domkirkeodden, the Museum in Nord-Østerdalen, Glomdal Museum and "
                                         "others) through Europeana, https://www.europeana.eu: " + EU_TEXT),
    "europeana_pl": (build_europeana_pl, "Polish regional digital libraries and museums (the Grodzka Gate - NN "
                                         "Theatre, the Mazowsze Digital Library and others) through Europeana, "
                                         "https://www.europeana.eu: " + EU_TEXT),
}

# How many pictures a full build takes from each collection.
PORTAL_LIMITS = {
    "europeana_hu": 4000,             # of about 33,000 open Hungarian records (many have no description)
    "europeana_el": 4000,             # of about 23,000 open records from the chosen Greek museums
    "europeana_no": 6000,             # of about 207,000 open Norwegian records (most have only a short title)
    "europeana_pl": 1500,             # of a few thousand Polish photographs and postcards with a caption
}

# The language of each pack, for build_packs.TRANSLATE, with a Helsinki-NLP model and revision for build_packs.MT_MODELS
# (the gmq model is the one build_packs already uses for Swedish; it also reads Norwegian).
PORTAL_TRANSLATE = {
    "europeana_hu": ("hu", "Helsinki-NLP/opus-mt-tc-big-hu-en", "c184817a80146c4e315c97ae18e59d1fe84972bb"),
    "europeana_el": ("el", "Helsinki-NLP/opus-mt-tc-big-el-en", "a69108562775c6727edf3540346f9d8900b73634"),
    "europeana_no": ("no", "Helsinki-NLP/opus-mt-tc-big-gmq-en", "b243b46fc9e1eaf068ae0d8ae896ac1acd7d2380"),
    "europeana_pl": ("pl", "Helsinki-NLP/opus-mt-pl-en", "7f2bb874fdfb6139f9842b91a9b75c4a6c93401c"),
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one portal pack builder.")
    parser.add_argument("key", choices=sorted(PORTAL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = PORTAL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
