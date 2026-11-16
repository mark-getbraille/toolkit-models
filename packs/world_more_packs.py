"""Pack builders for more picture collections found by searching in other languages, used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}. A picture that has more than one row comes once with its JPEG and then
again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins), so the zip holds each
picture only once. The limit counts pictures. Rows whose text mentions a child carry "child": True (as in
expression_packs.py), in any of the languages below.

  xm3600        Crossmodal-3600 (Google, 2022): 3,600 photos from around the world (Open Images, each CC BY 2.0 with
                its Flickr photographer named), each described by native speakers in 36 languages. The captions were
                written by people in each language, not translated, and are CC BY 4.0. Every picture gets one row per
                language with the question asked in that language ("Kuvaile tätä kuvaa." "Kaksi lasta leikkii
                hiekalla."), and one English row from the English captions (also written by people, so no machine
                translation is needed). Quechua is left out (no question in Quechua could be checked).
  europeana_fi  Finnish museum photographs and art (the Finnish Heritage Agency, Helsinki City Museum, the Museum of
                Finnish Architecture and others), through Europeana's search: records whose picture is CC BY 4.0, CC0
                or Public Domain Mark, with the museum's Finnish "sisällön kuvaus" (content description: what the
                picture shows). Europeana's record text is CC0. Where the museum also wrote an English "content
                description", that is the English row; otherwise build_packs adds a machine translation.
  europeana_cs  The Náprstek Museum of Asian, African and American Cultures, Prague (part of the National Museum),
                through Europeana: objects and photographs whose picture is CC BY 4.0, with the museum's short Czech
                description ("Miska z kalebasy zdobená vypalovaným vzorem ryb a hada."). Machine-translated to English
                by build_packs.

Europeana asks programs to use their own free API key (https://pro.europeana.eu/page/get-api): set EUROPEANA_KEY.
Without it the builders use Europeana's public demonstration key "api2demo", which works but is meant for trials.

Collections looked at and left out (checked at the source in November 2026), with the reason:
  Gallica (BnF, France)        Public-domain pictures, but commercial reuse needs a paid licence from the BnF.
  Finna (Finland) API          api.finna.fi answers programs with a Cloudflare "Just a moment..." page; the same
                               Finnish records come through Europeana instead (europeana_fi).
  National Museum of Korea     e-museum pictures are KOGL type 1 (allowed), but www.emuseum.go.kr refused connections
                               from this (US) machine, and its open API on data.go.kr needs a service key (sign-up).
  Korea MFDS pill pictures     "의약품 낱알식별 정보" (data.go.kr 15057639) has no restriction on use, but the API needs a
                               data.go.kr service key (sign-up), and the pictures are on nedrug.mfds.go.kr, which reset
                               connections from this machine. "알약 이미지 데이터" (15112582) is downloaded from the
                               Korea Pharmaceutical Information Center's site (sign-up).
  AI Hub (Korea)               Most datasets need a Korean sign-up and an application; many are for Korean residents.
  Deutsche Digitale Bibliothek, Trove, DigitalNZ, DigitaltMuseum    APIs need a (free) key: sign-up.
  Fortepan (Hungary), Deutsche Fotothek and many Europeana providers    CC BY-SA: not allowed.
  UIT-ViIC, KTVIC (Vietnamese), HCMUS Vietnamese captions    No licence from the authors (only third-party copies).
  Japanese, Korean and Arabic caption sets on Hugging Face (e.g. japanese-photos-captioned, metmuseum_w_korean_captions,
  laion-coco-arabic, pixmo-captions-arabic)    Written or translated by AI models.
  Multi30k, Flickr8k in Turkish, Hindi, Bengali    Flickr30k and Flickr8k pictures are not openly licensed.
  WIT (Wikipedia image text)   CC BY-SA.

Answers are the collections' own words (nothing is written by an AI model); the questions are fixed sentences.

    python packs/world_more_packs.py xm3600 --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import os
import random
import re
import sys
import tarfile
import time
import zipfile

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say
from food_packs import with_twins, count_pictures
from expression_packs import CHILD
from world_packs import capped_words, full_stop, ASK_JA, ASK_SV, ASK_NL, ASK_ZH, ASK_EN

# "Describe this picture." in each language of Crossmodal-3600 (Quechua left out).
ASK = {
    "ar": "صف هذه الصورة.", "bn": "এই ছবিটি বর্ণনা করুন।", "cs": "Popište tento obrázek.", "da": "Beskriv dette billede.",
    "de": "Beschreibe dieses Bild.", "el": "Περίγραψε αυτή την εικόνα.", "en": ASK_EN, "es": "Describe esta imagen.",
    "fa": "این تصویر را توصیف کنید.", "fi": "Kuvaile tätä kuvaa.", "fil": "Ilarawan ang larawang ito.",
    "fr": "Décris cette image.", "he": "תאר את התמונה הזאת.", "hi": "इस चित्र का वर्णन करें।", "hr": "Opiši ovu sliku.",
    "hu": "Írd le ezt a képet.", "id": "Jelaskan gambar ini.", "it": "Descrivi questa immagine.", "ja": ASK_JA,
    "ko": "이 사진을 설명해 주세요.", "mi": "Whakaahuatia tēnei pikitia.", "nl": ASK_NL, "no": "Beskriv dette bildet.",
    "pl": "Opisz to zdjęcie.", "pt": "Descreva esta imagem.", "ro": "Descrie această imagine.",
    "ru": "Опиши это изображение.", "sv": ASK_SV, "sw": "Eleza picha hii.", "te": "ఈ చిత్రాన్ని వివరించండి.",
    "th": "อธิบายภาพนี้", "tr": "Bu fotoğrafı tarif et.", "uk": "Опиши це зображення.", "vi": "Hãy mô tả bức ảnh này.",
    "zh": ASK_ZH,
}

# Words for a child in the other languages of these packs (expression_packs.CHILD has English, the main European
# languages, Russian, Japanese and Chinese). Wide on purpose, like CHILD: a picture any caption of which mentions one
# of these is marked "child".
CHILD_MORE = re.compile(
    r"\b(barn|barnet|barnen|pojke\w*|flick\w*|gutt\w*|jente\w*|dreng\w*|pige\w*|bebis|lapsi|lapse\w*|lasten?|lapsia|"
    r"poika|poja\w*|tyttö\w*|vauva\w*|dítě|děti|dět\w*|chlap(ec|ce|ci)\w*|dívk\w*|holčič\w*|kluk\w*|miminko|"
    r"chłop(iec|cy|ca)\w*|dziewczyn\w*|niemowl\w*|çocu\w*|bebek\w*|gyer(e|m)\w*|kislány\w*|kisfiú\w*|copi(l|ii)\w*|"
    r"băiat\w*|dijete|djec\w*|dječa\w*|djevojčic\w*|anak|bayi|mtoto|watoto|tamaiti|tamariki|pēpi|bata|"
    r"παιδ\w*|αγόρ\w*|κορίτσ\w*|μωρ\w*|дитин\w*|діт\w*|хлопчик\w*|дівчин\w*|дівчат\w*)\b|"
    r"trẻ em|em bé|cậu bé|cô bé|đứa trẻ|bé trai|bé gái|طفل|أطفال|اطفال|رضيع|ولد|فتاة|بنت|کودک|بچه|ילד|תינוק|"
    r"बच्च|लड़क|शिशु|শিশু|বাচ্চা|ছেলে|মেয়ে|เด็ก|ทารก|어린이|아기|소년|소녀|아이들|아이가|아이는|아이와|아이를|아이의|"
    r"赤ちゃん|男の子|女の子|幼児|小孩|小朋友|婴儿|పిల్ల|బాలుడు|బాలిక", re.I)


def mentions_child(*texts):
    """True when any of texts mentions a child, in any language of these packs."""
    return any(CHILD.search(t or "") or CHILD_MORE.search(t or "") for t in texts)


def marked(row, child):
    """The row with "child": True when child is true."""
    return dict(row, child=True) if child else row


# ----------------------------------------------------------------- Crossmodal-3600 (36 languages)

XM_WEB = "https://google.github.io/crossmodal-3600/web-data/"
XM_PICTURES = "https://open-images-dataset.s3.amazonaws.com/crossmodal-3600/images.tgz"   # 302 MB, all 3,600 photos
XM_CJK = {"ja", "zh"}
XM_NO_STOP = {"th"}                                   # Thai has no full stop


def xm_answer(caption, language):
    """A Crossmodal-3600 caption as an answer: spaces tidied, first letter a capital, ending with a full stop."""
    text = clean(caption)
    if language in XM_CJK:
        return full_stop(text.replace(" ", ""), "。")
    if language in XM_NO_STOP:
        return text
    text = text[:1].upper() + text[1:]
    return full_stop(text, "।" if language in ("hi", "bn") else ".")


def xm_rows(record, credit):
    """The rows of one Crossmodal-3600 picture: the first caption in each language (English first), all marked
    "child" when any caption mentions a child."""
    rows, texts = [], []
    for language in ["en"] + sorted(k for k in ASK if k != "en"):
        captions = [c for c in (record.get(language) or {}).get("caption") or [] if clean(c)]
        texts += captions
        if captions:
            answer = xm_answer(captions[0], language)
            if len(answer) >= 4:
                rows.append({"question": ASK[language], "answer": answer, "credit": credit})
    child = mentions_child(*texts)
    return [marked(r, child) for r in rows]


def build_xm3600(limit):
    """The Crossmodal-3600 pack: [(name, JPEG, row)], one row per language for each picture. The captions come from
    Google's captions.zip, the photographers from its image_attributions.csv (every photo is CC BY 2.0), and the
    photos from its single archive, read as it downloads."""
    s = session()
    lines = zipfile.ZipFile(io.BytesIO(s.get(XM_WEB + "captions.zip", timeout=600).content)).read("captions.jsonl")
    records = {}
    for line in lines.decode("utf-8").splitlines():
        record = json.loads(line)
        records[record["image/key"]] = record
    photos = {}
    for r in csv.DictReader(io.StringIO(s.get(XM_WEB + "image_attributions.csv", timeout=120).text)):
        if "/licenses/by/2.0" in (r.get("License") or ""):
            photos[r["ImageID"]] = (clean(r.get("Author")) or "an unnamed photographer", r.get("OriginalLandingURL", ""))
    say(f"Crossmodal-3600: {len(records)} pictures, {len(photos)} with a CC BY 2.0 photographer")
    wanted = sorted(set(records) & set(photos))
    random.Random(51).shuffle(wanted)
    wanted = set(wanted[:limit])
    fetched = []
    with s.get(XM_PICTURES, timeout=1800, stream=True) as response:
        response.raise_for_status()
        response.raw.decode_content = True
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            for member in tar:
                image_id = os.path.basename(member.name).rsplit(".", 1)[0]
                if not member.isfile() or image_id not in wanted:
                    continue
                data = smaller(tar.extractfile(member).read())
                if not data:
                    continue
                author, page = photos[image_id]
                credit = (f"Photo by {author}" + (f" ({page})" if page else "") + ", CC BY 2.0; captions from "
                          "Crossmodal-3600 (Thapliyal et al., 2022), Google, CC BY 4.0")
                rows = xm_rows(records[image_id], credit)
                if rows:
                    fetched.append((f"xm3600-{image_id}.jpg", data, rows))
                if len(fetched) >= len(wanted):
                    break
    say(f"Crossmodal-3600: {len(fetched)} pictures, {sum(len(r) for _, _, r in fetched)} rows, "
        f"{sum(1 for _, _, r in fetched if r[0].get('child'))} pictures marked child")
    return with_twins(fetched)


# ----------------------------------------------------------------- Europeana (Finnish and Czech museums)

EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EU_FREE = {"creativecommons.org/licenses/by/4.0": "CC BY 4.0", "creativecommons.org/publicdomain/zero/1.0": "CC0",
           "creativecommons.org/publicdomain/mark/1.0": "Public Domain Mark"}
EU_RIGHTS = 'RIGHTS:("http://creativecommons.org/licenses/by/4.0/" OR ' \
            '"http://creativecommons.org/publicdomain/zero/1.0/" OR "http://creativecommons.org/publicdomain/mark/1.0/")'


def eu_key():
    """The Europeana API key: EUROPEANA_KEY, or the public demonstration key."""
    return os.environ.get("EUROPEANA_KEY") or "api2demo"


def eu_licence(item):
    """The licence name of a Europeana record's picture, or "" when it is not one of the allowed licences."""
    rights = " ".join(item.get("rights") or [])
    return next((name for key, name in EU_FREE.items() if key in rights), "")


def eu_providers(s, query, filters):
    """{museum: number of records} for a Europeana query."""
    params = [("wskey", eu_key()), ("query", query), ("media", "true"), ("rows", "0"), ("profile", "facets"),
              ("facet", "DATA_PROVIDER"), ("f.DATA_PROVIDER.facet.limit", "100"), ("qf", "TYPE:IMAGE"),
              ("qf", EU_RIGHTS)] + [("qf", f) for f in filters]
    data = s.get(EUROPEANA, params=params, timeout=120).json()
    facet = next((f for f in data.get("facets") or [] if f.get("name") == "DATA_PROVIDER"), {})
    return {x["label"]: x["count"] for x in facet.get("fields") or []}


def eu_records(s, query, filters, provider, most):
    """Europeana records of one museum for a query (at most most), page by page with Europeana's cursor."""
    params = [("wskey", eu_key()), ("query", query), ("media", "true"), ("rows", "100"), ("profile", "rich"),
              ("qf", "TYPE:IMAGE"), ("qf", EU_RIGHTS), ("qf", f'DATA_PROVIDER:"{provider}"')] + \
        [("qf", f) for f in filters]
    cursor, seen = "*", 0
    while cursor and seen < most:
        time.sleep(0.5)
        try:
            data = s.get(EUROPEANA, params=params + [("cursor", cursor)], timeout=120).json()
        except Exception:  # noqa: BLE001 - the museum's remaining records are left out
            return
        items = data.get("items") or []
        for item in items:
            yield item
        seen += len(items)
        cursor = data.get("nextCursor") if items else None


def eu_picture(address):
    """Europeana's 400-pixel copy of a record's picture, or "". The museums' own picture servers (zetcom.app for the
    Finnish museums, esbirky.cz for the Náprstek Museum) refuse downloads from programs (401 and 404 answers), so
    Europeana's thumbnail service is used: https://api.europeana.eu/thumbnail/v3/400/<MD5 of the picture address>."""
    import hashlib
    if not address.startswith("http"):
        return ""
    return "https://api.europeana.eu/thumbnail/v3/400/" + hashlib.md5(address.encode("utf-8")).hexdigest()


def eu_credit(item, licence):
    """The credit of a Europeana record: title, museum, licence and the record's Europeana page."""
    title = clean((item.get("title") or [""])[0])
    title = title if len(title) <= 100 else title[:97].rsplit(" ", 1)[0] + "..."
    museum = clean((item.get("dataProvider") or [""])[0])
    page = item.get("guid") or f"https://www.europeana.eu/item{item.get('id', '')}"
    return f"{title}, {museum}, {licence}; record text CC0, via Europeana: {page.split('?')[0]}"


# Finnish: the "sisällön kuvaus" (content description) parts of the records; "content description" is the museum's
# own English. Parts that are numbers, places, name lists, notes or catalogue words are left out.
FI_CONTENT = re.compile(r"^\s*sisällön kuvaus:\s*(.+)", re.I | re.S)
EN_CONTENT = re.compile(r"^\s*content description:\s*(.+)", re.I | re.S)
FI_PHYSICAL = re.compile(r"^\s*fyysinen kuvaus:\s*(.+)", re.I | re.S)
FI_NOT_SHOWN = re.compile(r"numero|@paikka|kuvaajatieto|julkaisu:|vasemmalta|oikealta:|ylärivi|alarivi|eturivi|takarivi|"
                          r"^esinekuva|^alue \d|^kortteli|^koekuoppa|^\W*$|^huom\b|^(ulko|sisä)kuva,|kuva otettu|"
                          r"inventointi|dokumentointi|restaurointi \d|^kuvattu (lännestä|idästä|etelästä|pohjoisesta)|"
                          r"kuvauspaikka|planssi|tuntematon", re.I)
FI_ORIENTATION = re.compile(r"^(vaaka|pysty|neliö|mustavalkoinen|värillinen)\W*$", re.I)


def fi_first_line(text):
    """The first line of a description part, without dates and places on its later lines."""
    return clean(re.split(r"\s*\n\s*", text.strip())[0])


def fi_answer(descriptions):
    """(Finnish answer, the museum's own English or "") from a Finnish record's description parts, or ("", "")."""
    shown, physical, english = [], "", ""
    for part in descriptions:
        content = FI_CONTENT.match(part)
        if content:
            line = fi_first_line(content.group(1))
            if not FI_NOT_SHOWN.search(line):
                shown.append(line)
        elif FI_PHYSICAL.match(part):
            line = fi_first_line(FI_PHYSICAL.match(part).group(1))
            if not FI_ORIENTATION.match(line) and len(line.split()) >= 4:
                physical = line
        elif EN_CONTENT.match(part):
            english = fi_first_line(EN_CONTENT.match(part).group(1))
    text = " ".join(full_stop(t) for t in shown + ([physical] if physical else []))
    answer = capped_words(text, 70)
    if len(answer.split()) < 4 or len(answer) < 25:
        return "", ""
    return answer, (capped_words(english, 70) if len(english.split()) >= 4 else "")


# Czech (Náprstek Museum): film sizes, inventory numbers and the like at the end of descriptions.
CS_CATALOGUE = re.compile(r",?\s*(čb|barevný|bar\.)\s+(film|diapozitiv|negativ)[^.]*\.?|,?\s*\d+([,.]\d+)?\s*x\s*"
                          r"\d+([,.]\d+)?\s*(cm|mm)\.?|\s*inv\.?\s*č\.?\s*[\w./-]+\.?", re.I)


def cs_answer(descriptions):
    """The Czech answer of a Náprstek Museum record (its first description without film sizes), or ""."""
    text = CS_CATALOGUE.sub("", clean(descriptions[0] if descriptions else "")).strip(" ,;")
    answer = capped_words(full_stop(text), 70)
    return answer if len(answer.split()) >= 4 else ""


EU_SOURCES = {
    "europeana_fi": {"language": "fi", "query": '"sisällön kuvaus"', "filters": [], "answer": fi_answer},
    # (Europeana's museum counts ignore a museum filter, so the one museum is named here.)
    "europeana_cs": {"language": "cs", "query": "*", "answer": lambda d: (cs_answer(d), ""), "filters": [],
                     "providers": {"Náprstek Museum of Asian, African and American Cultures": 12435}},
}


def eu_descriptions(item, language):
    """A Europeana record's description parts in one language (all its descriptions when none is marked)."""
    aware = item.get("dcDescriptionLangAware") or {}
    parts = list(aware.get(language) or []) + list(aware.get("en") or [])
    return parts or list(item.get("dcDescription") or [])


def build_europeana(key, limit):
    """A Europeana pack: [(name, JPEG, row)], museum by museum (no museum gives more than about 40% of the pack),
    each record's description in its language and, where the museum wrote one, its English twin."""
    source = EU_SOURCES[key]
    s, items, seen = session(), [], set()
    providers = source.get("providers") or eu_providers(s, source["query"], source["filters"])
    say(f"Europeana {key}: {sum(providers.values())} records from {len(providers)} museums")
    per_museum = max(20, int(limit * 1.5 * 0.4))
    for provider, count in sorted(providers.items(), key=lambda kv: -kv[1]):
        found = 0
        for item in eu_records(s, source["query"], source["filters"], provider, min(count, per_museum * 8)):
            licence = eu_licence(item)
            picture = eu_picture((item.get("edmIsShownBy") or [""])[0])
            answer, english = source["answer"](eu_descriptions(item, source["language"]))
            if not licence or not picture.startswith("http") or not answer or answer in seen:
                continue
            seen.add(answer)
            credit = eu_credit(item, licence)
            child = mentions_child(answer, english, " ".join(item.get("title") or []))
            rows = [marked({"question": ASK[source["language"]], "answer": answer, "credit": credit}, child)]
            if english:
                rows.append(marked({"question": ASK_EN, "answer": english, "credit": credit}, child))
                rows[0]["twinned"] = True              # build_packs.add_translations leaves it untranslated
            items.append((f"{key}-{len(items)}.jpg", picture, rows))
            found += 1
            if found >= per_museum:
                break
        say(f"  {provider}: {found} usable")
        if len(items) >= limit * 1.5:
            break
    random.Random(52).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.4) + 2], workers=4, pause=0.2)
    return with_twins(fetched[:limit])


def build_europeana_fi(limit):
    """The Finnish museums pack (see the module docstring)."""
    return build_europeana("europeana_fi", limit)


def build_europeana_cs(limit):
    """The Náprstek Museum pack (see the module docstring)."""
    return build_europeana("europeana_cs", limit)


# ----------------------------------------------------------------- the packs

WORLD_MORE_PACKS = {
    "xm3600": (build_xm3600, "Captions: Crossmodal-3600 (Ashish V. Thapliyal, Jordi Pont-Tuset, Xi Chen and Radu "
                             "Soricut, 'Crossmodal-3600: A Massively Multilingual Multimodal Evaluation Dataset', EMNLP "
                             "2022), Google LLC, CC BY 4.0, https://google.github.io/crossmodal-3600/ (captions written "
                             "by native speakers in 36 languages). Photos: Open Images, each CC BY 2.0, credited below "
                             "with its photographer and Flickr page."),
    "europeana_fi": (build_europeana_fi, "Finnish museums (the Finnish Heritage Agency, Helsinki City Museum and "
                                         "others) through Europeana, https://www.europeana.eu: record text CC0 "
                                         "(https://pro.europeana.eu/page/europeana-data-exchange-agreement); "
                                         "pictures CC BY 4.0, CC0 or Public Domain Mark, each credited below with its "
                                         "museum and record."),
    "europeana_cs": (build_europeana_cs, "Náprstek Museum of Asian, African and American Cultures (National Museum, "
                                         "Prague) through Europeana, https://www.europeana.eu: record text CC0; "
                                         "pictures CC BY 4.0, each credited below with its record."),
}

# How many pictures a full build takes from each collection.
WORLD_MORE_LIMITS = {
    "xm3600": 3600,                   # all of it: 3,600 pictures, about 35 rows each
    "europeana_fi": 6000,             # of more than 100,000 Finnish records with a content description
    "europeana_cs": 4000,             # of about 12,400 Náprstek records
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one world pack builder.")
    parser.add_argument("key", choices=sorted(WORLD_MORE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = WORLD_MORE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
