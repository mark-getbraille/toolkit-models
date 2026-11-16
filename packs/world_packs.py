"""Pack builders for five picture collections from outside the English-speaking world, used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes, row)], where a row
is {"question", "answer", "credit"} (or, for COCO photos, {"url", "question", "answer", "credit"} with no picture).

Every collection's descriptions are in its own language, so the question is asked in that language too:
  japan_search    Japan Search (jpsearch.go.jp), Japan's national portal: museum and archive records whose picture is
                  CC0, public domain (PDM) or CC BY, and whose database lets its descriptions be shared (CC0, CC BY,
                  or the Government of Japan Standard Terms of Use, which match CC BY 4.0). Only the sentences of the
                  Japanese description that say what is shown are kept. Asked: "この写真を説明してください。"
  ksamsok         K-samsök (kulturarvsdata.se), Sweden's heritage search: records whose picture is CC0, PDM or CC BY
                  and that have a "Motiv" description (what the picture shows). Asked: "Beskriv bilden."
  rijksmuseum     The Rijksmuseum, Amsterdam (data.rijksmuseum.nl): works whose picture is CC0 or public domain, with
                  the museum's Dutch description of what the work shows (English where only that exists).
                  Asked: "Beschrijf deze afbeelding." (or "Describe this picture.").
  stair_captions  STAIR Captions (CC BY 4.0): Japanese captions of COCO photos, the first caption of each photo, only
                  photos under CC BY 2.0 or no known copyright (rows carry the photo's COCO address, as COCO's photos
                  are not copied into packs).
  coco_cn         COCO-CN (MIT): Chinese sentences written by people (the manually written set and the 2020 iCap
                  set, never the machine translations), on the same free COCO photos. Asked: "请描述这张图片。"

Answers are capped at about 80 words (200 characters for Japanese and Chinese).

    python packs/world_packs.py ksamsok --limit 8      (prints a few rows: a quick check of one builder)
"""

import json
import random
import re
import sys
import time

from build_packs import session, clean, smaller, fetch_all, first_sentences, say, COCO_FREE, coco_licences  # noqa: F401

ASK_JA = "この写真を説明してください。"
ASK_SV = "Beskriv bilden."
ASK_NL = "Beschrijf deze afbeelding."
ASK_ZH = "请描述这张图片。"
ASK_EN = "Describe this picture."
COCO_PHOTO = "photo from COCO (cocodataset.org), CC BY 2.0 or no known copyright restrictions"


# ----------------------------------------------------------------- shared helpers

def capped_words(text, words=80):
    """The first sentences of a text, at most about words words; one very long sentence is cut at words words."""
    text = first_sentences(text, words)
    parts = text.split()
    if len(parts) > words:
        text = " ".join(parts[:words]).rstrip(",;:") + "..."
    return text


def capped_chars(sentences, chars=200):
    """Japanese or Chinese sentences joined in order while they fit in chars characters (a sentence longer than
    chars on its own is left out)."""
    out = ""
    for sentence in sentences:
        if len(out + sentence) <= chars:
            out += sentence
    return out


def cjk_sentences(text):
    """A Japanese or Chinese text cut into sentences, each keeping its full stop."""
    return [s.strip() for s in re.findall(r"[^。！？!?]+[。！？!?]?", text) if s.strip()]


def full_stop(text, mark="."):
    """The text ending with a full stop."""
    text = text.strip()
    return text if not text or text[-1] in ".!?。！？…" else text + mark


def big_enough(entries, side=400):
    """The entries whose picture is at least side pixels on its long side (thumbnails are too small to describe)."""
    import io
    from PIL import Image
    return [e for e in entries if max(Image.open(io.BytesIO(e[1])).size) >= side]


def picture_side(s, url):
    """The long side in pixels of the picture at url (0 when it cannot be read): a check of a collection's pictures
    before taking many of them."""
    import io
    from PIL import Image
    try:
        return max(Image.open(io.BytesIO(s.get(url, timeout=60).content)).size)
    except Exception:  # noqa: BLE001 - unreadable
        return 0


def safe_name(text):
    """A file-name-safe version of a record identifier."""
    return re.sub(r"[^\w.-]+", "_", str(text))[:80]


# ----------------------------------------------------------------- Japan Search (Japan)

JPS_SEARCH = "https://jpsearch.go.jp/api/item/search/jps-cross"
JPS_DATABASE = "https://jpsearch.go.jp/api/database/"
JPS_RIGHTS = {"cc0": "CC0", "pdm": "Public Domain Mark", "ccby": "CC BY"}   # the f-rights values of the shareable
JPS_WINDOW = 2000          # the search gives at most the first 2,000 results of a query (from + size)
# Readings printed inside the text (furigana): ＠きらすなご＠, ＊じんごじ＊, （ずいけいしゅうほう）, 〈ひのとしもと・...〉.
JPS_READINGS = re.compile(r"[＠@＊*][ぁ-ゖァ-ヺー・]+[＠@＊*]|（[ぁ-ゖー・]+）|\([ぁ-ゖー・]+\)|〈[ぁ-ゖー・][^〉]*〉")
# Words that show a sentence says what is in the picture (drawn, figure, colour, pattern, standing, holding ...).
JPS_SHOWN = re.compile(r"描|図は|図に|画面|姿|表され|表した|文様|模様|彩色|着色|色の|色で|色に|形の|形を|施され|配され|"
                       r"配した|あしら|写っ|写され|撮影|立つ|立っ|座る|座っ|持つ|持っ|着た|着て|着用|並ぶ|並んで|浮か|"
                       r"咲|見える|手に|背景|中央|左に|右に|上部|下部|前景|遠景|彫|刻ま|飾|囲ま|乗る|乗っ|向か|眺め|"
                       r"人物|風景|様子|装飾")
# Records about written documents (letters, deeds, ledgers, copied texts): their pictures are pages of writing.
JPS_DOCUMENT = re.compile(r"書簡|書状|書翰|文書|願書|証文|手紙|断簡|写本|古文書|帳簿|一札|御仕置|届書|書付|書写|の写し|和歌")
JPS_DOCUMENT_TYPES = {"ancdoc", "docs", "book", "map", "article", "periodical", "mscore", "古文書", "文書", "図書", "地図",
                      "書跡", "典籍", "書跡・典籍", "古文書・書跡"}


def jps_text_licence(rights):
    """The licence of a Japan Search database's descriptions (its "metadataRights" text), or None when they may not
    be shared freely or the terms are unclear. Japan Search's policy (https://jpsearch.go.jp/policy) says metadata
    without stated terms is CC0."""
    text = " ".join(str(v) for v in (rights or {}).values())
    if not text.strip():
        return "CC0 (Japan Search policy)"
    if re.search(r"by-sa|by-nc|by-nd|-nc\b|-nd\b|-sa\b|異な|vary|varies|著作権あり|copyright|確認|refer|禁止|不可", text, re.I):
        return None
    if re.search(r"publicdomain/zero|\bCC0\b", text, re.I):
        return "CC0"
    if re.search(r"publicdomain/mark|\bPDM\b", text, re.I):
        return "Public Domain Mark"
    if re.search(r"licenses/by/|CC BY(?![-\w])", text, re.I):
        return "CC BY 4.0"
    if re.search(r"政府標準利用規約|Standard Terms of Use|公共データ利用規約|\bPDL\b", text):
        return "Government of Japan Standard Terms of Use (compatible with CC BY 4.0)"
    return None


def jps_answer(description):
    """The sentences of a Japanese description that say what is shown, at most 200 characters, or ""."""
    text = JPS_READINGS.sub("", clean(description))
    if JPS_DOCUMENT.search(text):
        return ""
    text = re.sub(r"^画像\s*\d+\s*[)）]\s*", "", text)
    shown = [s for s in cjk_sentences(text) if JPS_SHOWN.search(s)]
    answer = full_stop(capped_chars(shown, 200), "。")
    return answer if len(answer) >= 8 else ""


def jps_row(record, text_licence):
    """(picture address, row) for a Japan Search record with a free picture and a description of what it shows."""
    c = record.get("common") or {}
    picture_licence = JPS_RIGHTS.get(c.get("contentsRightsType"))
    if not picture_licence or JPS_DOCUMENT_TYPES & set((record.get("rdfindex") or {}).get("type") or []):
        return None
    pictures = (c.get("contentsUrl") if c.get("contentsType") == "image" else None) or c.get("thumbnailUrl") or []
    url = next((u for u in pictures if str(u).startswith("http")), None)
    answer = jps_answer(c.get("description"))
    if not url or not answer:
        return None
    page = f"https://jpsearch.go.jp/item/{c.get('id') or record.get('id')}"
    credit = (f"{clean(c.get('title'))}, {clean(c.get('provider'))}. Picture: {picture_licence}; description: "
              f"{text_licence}. Via Japan Search: {page}" + (f" ({c['linkUrl']})" if c.get("linkUrl") else ""))
    return url, {"question": ASK_JA, "answer": answer, "credit": credit}


def build_japan_search(limit):
    """The Japan Search pack's pictures: [(name, JPEG, row)]. Searches each shareable licence database by database
    (the search shows only 2,000 results per query), about one request a second."""
    s, items, seen = session(), [], set()
    per_database = max(50, int(limit * 0.35))      # no database gives more than about a third of the pack
    licences, sizes = {}, {}                        # each database's description licence and picture size
    for rights in JPS_RIGHTS:
        params = {"f-rights": rights, "f-contents": ["image", "description"], "size": 1}
        facets = s.get(JPS_SEARCH, params=params, timeout=60).json().get("facets", [])
        databases = next((f["counts"] for f in facets if f.get("key") == "db"), {})
        say(f"Japan Search {rights}: {sum(databases.values())} records in {len(databases)} databases")
        for db, count in sorted(databases.items(), key=lambda kv: -kv[1]):
            if db not in licences:
                time.sleep(1)
                try:
                    licences[db] = jps_text_licence(s.get(JPS_DATABASE + db, timeout=60).json().get("metadataRights"))
                except Exception:  # noqa: BLE001 - unknown terms: left out
                    licences[db] = None
            if not licences[db]:
                continue
            found = 0
            for start in range(0, min(count, JPS_WINDOW), 100):
                time.sleep(1)
                try:
                    page = s.get(JPS_SEARCH, timeout=60, params={"f-rights": rights, "f-db": db, "size": 100,
                                                                 "f-contents": ["image", "description"],
                                                                 "from": start}).json().get("list", [])
                except Exception:  # noqa: BLE001 - next database
                    break
                for record in page:
                    got = jps_row(record, licences[db])
                    if got and db not in sizes:
                        sizes[db] = picture_side(s, got[0])
                        if sizes[db] < 400:
                            say(f"  {db}: pictures too small ({sizes[db]} pixels), left out")
                    if got and sizes.get(db, 0) >= 400 and got[1]["answer"] not in seen:
                        seen.add(got[1]["answer"])
                        items.append((f"jps-{safe_name(record.get('id'))}.jpg", got[0], got[1]))
                        found += 1
                if not page or found >= per_database or (start >= 200 and found < 5) or sizes.get(db, 400) < 400:
                    break
            if found:
                say(f"  {db} ({licences[db]}): {found} usable")
            if len(items) >= limit * 1.3:
                break
    random.Random(31).shuffle(items)
    return big_enough(fetch_all(items[:int(limit * 1.5)], workers=4, pause=0.2))[:limit]


# ----------------------------------------------------------------- K-samsök (Sweden)

KS_API = "https://kulturarvsdata.se/ksamsok/api"
KS_LICENCES = {"cc0": "CC0", "pdmark": "Public Domain Mark", "by": "CC BY"}
KS_LICENCE_BASE = "http://kulturarvsdata.se/resurser/license#"
KS_MONTHS = "januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december"
# Sentences that are not about what is shown: dates, photographers, orders, series, notes and name lists.
KS_NOT_SHOWN = re.compile(rf"^((år|ca\.?|omkring)\s+)?\d{{4}}\.?$|^(\d{{1,2}}\s+)?({KS_MONTHS})\s+\d{{4}}|"
                          r"^(reportage|beställ|foto(graf)?\b|fotograferad|neg\b|negativ|obs\b|se även|jämför|serie|"
                          r"bild\s*\d|personer\s*:|fr\.\s*v|tryckt text|anm\b|inv\.?\s*nr|reprofoto|kopia|[\w\s]{0,40}inv\.?\s*nr)|"
                          r"^\W*$", re.I)
# Descriptions of a whole book, album or folder (what it contains, not what the picture shows).
KS_NOT_A_PICTURE = re.compile(r"^(foto)?album|^anteckningsbok|^tidbok|^skissbok|^fotoserie|^tidningsklipp|"
                              r"^kuvert|^förteckning|^gratulationshäfte|^oidentifier|\(avbildad|^(dessa|de här) fotografier|"
                              r"^fotografierna|^samlingen|^denna samling", re.I)


def ks_local(tag):
    """An XML tag without its namespace."""
    return tag.rsplit("}", 1)[-1]


def ks_text(element, name):
    """The text of the first descendant called name, or ""."""
    for child in element.iter():
        if ks_local(child.tag) == name and (child.text or "").strip():
            return child.text.strip()
    return ""


def ks_resource(element):
    """The rdf:resource address of an element."""
    return element.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", "")


def ks_answer(motiv):
    """A Swedish "Motiv" description without dates, photographers and notes, at most about 80 words, or ""."""
    text = clean(motiv)
    if KS_NOT_A_PICTURE.search(text):
        return ""
    swedish = re.split(r"\n\s*-\s*\n", motiv or "")[0]          # a line "-" starts an English translation
    sentences = [s for s in re.split(r"(?<=[.!?])\s+|\s*\n\s*", swedish) if s.strip()]
    kept = [clean(s) for s in sentences if not KS_NOT_SHOWN.search(clean(s))]
    answer = " ".join(full_stop(s) for s in kept if s)
    answer = re.sub(r"\s*[\w ]{0,40}\binv\.?\s*nr\.?\s*[\w./:-]+\.?", "", answer)    # inventory numbers
    answer = capped_words(answer, 80)
    return answer if len(answer.split()) >= 6 else ""


def ks_row(entity):
    """(picture address, row) for a K-samsök record with a free picture and a "Motiv" description, or None."""
    motiv = ""
    for d in (e for e in entity.iter() if ks_local(e.tag) == "ItemDescription"):
        if ks_text(d, "type") == "Motiv":
            motiv = ks_text(d, "desc")
            break
    answer = ks_answer(motiv)
    if not answer:
        return None
    item_licence = next((ks_resource(e) for e in entity.iter() if ks_local(e.tag) == "itemLicense"), "")
    if item_licence and item_licence.split("#")[-1] not in KS_LICENCES:
        return None                                   # the record text itself is not free
    for image in (e for e in entity.iter() if ks_local(e.tag) == "Image"):
        licence = next((ks_resource(e).split("#")[-1] for e in image.iter() if ks_local(e.tag) == "mediaLicense"), "")
        if licence not in KS_LICENCES:
            continue
        high, low = ks_text(image, "highresSource"), ks_text(image, "lowresSource")
        # DigitaltMuseum's large pictures are 1,200 pixels; other museums' "highres" can be the original scan.
        url = high if high and ("dimu.org" in high or not low) else (low or ks_text(image, "thumbnailSource"))
        if not url:
            continue
        title = clean(ks_text(entity, "itemLabel") or ks_text(entity, "itemTitle"))
        title = title if len(title) <= 100 else title[:97].rsplit(" ", 1)[0] + "..."
        page = ks_text(entity, "url") or entity.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        organisation = ks_text(entity, "serviceOrganizationFull") or ks_text(entity, "serviceOrganization")
        credit = f"{title}, {organisation}, {KS_LICENCES[licence]}, via K-samsök: {page}"
        return url, {"question": ASK_SV, "answer": answer, "credit": credit}
    return None


def build_ksamsok(limit):
    """The K-samsök pack's pictures: [(name, JPEG, row)]. Goes through each museum's free pictures that have a
    description (one request a second) and keeps the "Motiv" descriptions; a museum whose first pages give few is
    left early."""
    import xml.etree.ElementTree as ET
    s, items, seen = session(), [], set()
    per_museum = max(30, int(limit * 0.08))
    for licence in KS_LICENCES:
        query = f'thumbnailExists=j and itemDescription=* and mediaLicense="{KS_LICENCE_BASE}{licence}"'
        stats = s.get(KS_API, timeout=120, params={"method": "statisticSearch", "index": "serviceOrganization=*",
                                                   "query": query, "removeBelow": 100}).text
        museums = re.findall(r"<value>([^<]*)</value></indexFields><records>(\d+)</records>", stats)
        say(f"K-samsök {licence}: {len(museums)} museums")
        for museum, count in museums:
            found = 0
            for start in range(1, min(int(count), 20000), 100):
                time.sleep(1)
                try:
                    root = ET.fromstring(s.get(KS_API, timeout=120, params={
                        "method": "search", "query": f"{query} and serviceOrganization={museum}",
                        "hitsPerPage": 100, "startRecord": start}).content)
                except Exception:  # noqa: BLE001 - next museum
                    break
                entities = [e for e in root.iter() if ks_local(e.tag) == "Entity"]
                for entity in entities:
                    got = ks_row(entity)
                    if got and got[1]["answer"] not in seen:
                        seen.add(got[1]["answer"])
                        items.append((f"ksamsok-{len(items)}.jpg", got[0], got[1]))
                        found += 1
                if not entities or found >= per_museum or (start > 200 and found < 10):
                    break
            if found:
                say(f"  {museum}: {found} usable")
            if len(items) >= limit * 1.3:
                break
        if len(items) >= limit * 1.3:
            break
    random.Random(32).shuffle(items)
    return big_enough(fetch_all(items[:int(limit * 1.3)], workers=4, pause=0.2))[:limit]


# ----------------------------------------------------------------- Rijksmuseum (the Netherlands)

RM_SEARCH = "https://data.rijksmuseum.nl/search/collection"
RM_TYPES = ("painting", "drawing", "print", "photograph", None)     # None: any kind of object
RM_DESCRIPTION = "300435452"                                         # AAT "description"
RM_DUTCH, RM_ENGLISH = "300388256", "300388277"
RM_FREE = {"publicdomain/zero": "CC0", "publicdomain/mark": "Public Domain"}
# Sentences about the object's place in a series or album, or its inscriptions, not about what it shows.
RM_NOT_SHOWN = re.compile(r"^(onderdeel van|prent uit|blad uit|pagina|uit (een|het|de) (album|serie|reeks)|"
                          r"met (een )?(\w+ )?(bijschrift|onderschrift|opschrift)|genummerd|gesigneerd|gedateerd|"
                          r"gemerkt|verso|recto|onderwerpsrubrieken|part of|print from|page from|from (an|the) (album|series)|"
                          r"with (an? )?(\w+ )?(caption|inscription)|numbered|signed|dated)\b", re.I)


def rm_walk(node):
    """Every dictionary inside a Linked Art record."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from rm_walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from rm_walk(value)


def rm_answer(text):
    """A Rijksmuseum description without series and inscription sentences, at most about 80 words, or ""."""
    sentences = re.split(r"(?<=[.!?])\s+", clean(text))
    answer = capped_words(" ".join(s for s in sentences if s and not RM_NOT_SHOWN.search(s)), 80)
    return answer if len(answer.split()) >= 6 else ""


def rm_row(record):
    """(picture address, row) for a Rijksmuseum object with a CC0 or public-domain picture and a description of
    what it shows, or None."""
    descriptions = {}
    for statement in record.get("referred_to_by") or []:
        if any(str(c.get("id", "")).endswith(RM_DESCRIPTION) for c in statement.get("classified_as") or []):
            language = str(((statement.get("language") or [{}])[0]).get("id", "")).rsplit("/", 1)[-1]
            descriptions.setdefault(language, statement.get("content"))
    question, answer = ASK_NL, rm_answer(descriptions.get(RM_DUTCH))
    if not answer:
        question, answer = ASK_EN, rm_answer(descriptions.get(RM_ENGLISH))
    if not answer:
        return None
    picture, licence, page = None, None, None
    for node in rm_walk(record):
        points = [p.get("id", "") for p in node.get("access_point") or [] if isinstance(p, dict)]
        if node.get("type") == "DigitalObject" and any("iiif" in p for p in points) and not picture:
            terms = " ".join(str(r.get("content", "")) for r in node.get("referred_to_by") or [])
            licence = next((name for key, name in RM_FREE.items() if key in terms), None)
            if not licence and re.search(r"creativecommons\.org/licenses/by/", terms):
                licence = "CC BY 4.0"
            picture = next(p for p in points if "iiif" in p)
        if not page:
            page = next((p for p in points if p.startswith("https://www.rijksmuseum.nl/")), None)
    if not picture or not licence:
        return None
    picture = re.sub(r"/full/[^/]+/0/default\.jpg$", "/full/!2048,2048/0/default.jpg", picture)
    title = next((clean(n.get("content")) for n in record.get("identified_by") or [] if n.get("type") == "Name"), "")
    credit = f"{title}, Rijksmuseum, Amsterdam, {licence}: {page or record.get('id')}"
    return picture, {"question": question, "answer": answer, "credit": credit}


def build_rijksmuseum(limit):
    """The Rijksmuseum pack's pictures: [(name, JPEG, row)]. Walks the search results of several kinds of object
    (works with a picture and a Dutch description), takes every third object so one series does not fill the pack,
    and reads each object's record."""
    import concurrent.futures
    s = session()
    s.headers["Accept"] = "application/ld+json"
    wanted = int(limit * 1.3)
    per_type = wanted // len(RM_TYPES) + 1
    items, seen = [], set()

    def one(address):
        """One object's record, or None."""
        time.sleep(0.25)
        try:
            return s.get(address, timeout=60).json()
        except Exception:  # noqa: BLE001 - left out
            return None

    for kind in RM_TYPES:
        params = {"imageAvailable": "true", "description": "een"}
        if kind:
            params["type"] = kind
        address, found = RM_SEARCH, 0
        with concurrent.futures.ThreadPoolExecutor(4) as pool:
            while address and found < per_type:
                try:
                    page = s.get(address, params=params, timeout=60).json()
                except Exception:  # noqa: BLE001 - next kind
                    break
                params = None                                  # the next page's address carries the query
                address = (page.get("next") or {}).get("id")
                ids = [o["id"] for o in page.get("orderedItems", [])][::3]
                for record in pool.map(one, ids):
                    got = rm_row(record) if record else None
                    if got and got[1]["answer"] not in seen and found < per_type:
                        seen.add(got[1]["answer"])
                        items.append((f"rijksmuseum-{safe_name(record['id'].rsplit('/', 1)[-1])}.jpg", *got))
                        found += 1
        say(f"Rijksmuseum {kind or 'other'}: {found} usable")
    random.Random(33).shuffle(items)
    return fetch_all(items[:int(limit * 1.2)], workers=4, pause=0.2)[:limit]


# ----------------------------------------------------------------- STAIR Captions (Japanese captions of COCO)

STAIR = "shunk031/STAIR-Captions"


def build_stair_captions(limit):
    """The STAIR Captions pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]. Reads only
    the caption columns of the dataset's files (not their pictures), file by file until there are enough."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    free = coco_licences()
    say(f"COCO: {len(free)} photos under CC BY 2.0 or no known copyright")
    files = sorted(f for f in HfApi().list_repo_files(STAIR, repo_type="dataset")
                   if f.startswith("v1.2.0/") and f.endswith(".parquet"))
    random.Random(34).shuffle(files)
    fs, rows, done = HfFileSystem(), [], set()
    for name in files:
        with fs.open(f"datasets/{STAIR}/{name}", "rb", block_size=1 << 20) as f:
            table = pq.ParquetFile(f).read(columns=["image_id", "annotations"]).to_pylist()
        for record in table:
            image_id = record["image_id"]
            captions = (record.get("annotations") or {}).get("caption") or []
            if image_id not in free or image_id in done or not captions:
                continue
            caption = full_stop(clean(captions[0]).replace(" ", ""), "。")
            if len(caption) < 8:
                continue
            done.add(image_id)
            rows.append({"url": free[image_id], "question": ASK_JA, "answer": caption[:200],
                         "credit": f"STAIR Captions (Yoshikawa et al., 2017), CC BY 4.0; {COCO_PHOTO}"})
        say(f"STAIR Captions {name}: {len(rows)} captions so far")
        if len(rows) >= limit:
            break
    random.Random(35).shuffle(rows)
    return [(None, None, r) for r in rows[:limit]]


# ----------------------------------------------------------------- COCO-CN (Chinese sentences on COCO)

COCO_CN = "AIMClab-RUC/COCO-CN"
COCO_CN_ARCHIVE = "coco-cn-version1805v1.1.tar.gz"
COCO_CN_WRITTEN = "imageid.human-written-caption.txt"     # the manually written sentences (not the translations)
COCO_CN_ICAP = "https://raw.githubusercontent.com/li-xirong/coco-cn/master/data/coco-cn_ext.icap2020.txt"


def coco_cn_sentences(lines, source):
    """{COCO image id: (sentence, source)} from COCO-CN lines "COCO_train2014_000000573854#0<tab>sentence", the
    first sentence of each picture."""
    out = {}
    for line in lines:
        match = re.match(r"\S*?_(\d+)#(\d+)\s+(.+)", line.strip())
        if match:
            image_id, number, sentence = int(match.group(1)), int(match.group(2)), clean(match.group(3))
            if image_id not in out or number < out[image_id][2]:
                out[image_id] = (sentence, source, number)
    return {k: v[:2] for k, v in out.items()}


def build_coco_cn(limit):
    """The COCO-CN pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]. Only the
    sentences people wrote: the manually written set (Hugging Face) and the 2020 iCap set (GitHub); never the
    machine-translated (Baidu) or the translated sentences."""
    import tarfile
    from huggingface_hub import hf_hub_download
    free = coco_licences()
    archive = hf_hub_download(COCO_CN, COCO_CN_ARCHIVE, repo_type="dataset")
    with tarfile.open(archive) as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith("/" + COCO_CN_WRITTEN))
        written = tar.extractfile(member).read().decode("utf-8").splitlines()
    sentences = coco_cn_sentences(written, "COCO-CN (Li et al., 2019), MIT")
    icap = session().get(COCO_CN_ICAP, timeout=120).text.splitlines()
    for image_id, value in coco_cn_sentences(icap, "COCO-CN iCap 2020 sentences (Li et al.), MIT").items():
        sentences.setdefault(image_id, value)
    rows = []
    for image_id, (sentence, source) in sorted(sentences.items()):
        answer = full_stop(sentence.replace(" ", ""), "。")
        if image_id in free and len(answer) >= 8:
            rows.append({"url": free[image_id], "question": ASK_ZH, "answer": answer[:200],
                         "credit": f"{source}; {COCO_PHOTO}"})
    say(f"COCO-CN: {len(rows)} sentences on free COCO photos (of {len(sentences)} pictures)")
    random.Random(36).shuffle(rows)
    return [(None, None, r) for r in rows[:limit]]


# ----------------------------------------------------------------- the packs

WORLD_PACKS = {
    "japan_search": (build_japan_search, "Japan Search (jpsearch.go.jp), run by the National Diet Library: pictures "
                                         "CC0, Public Domain Mark or CC BY; descriptions CC0, CC BY or the Government "
                                         "of Japan Standard Terms of Use (compatible with CC BY 4.0), each record "
                                         "credited below with its holding institution. https://jpsearch.go.jp/policy"),
    "ksamsok": (build_ksamsok, "K-samsök (kulturarvsdata.se), the Swedish National Heritage Board's search of "
                               "Swedish museums: pictures CC0, Public Domain Mark or CC BY, each credited below with "
                               "its museum. https://www.raa.se/hitta-information/k-samsok/"),
    "rijksmuseum": (build_rijksmuseum, "Rijksmuseum, Amsterdam: pictures and descriptions CC0 or public domain. "
                                       "https://data.rijksmuseum.nl/policy/"),
    "stair_captions": (build_stair_captions, "Captions: STAIR Captions (Yoshikawa, Shigeto and Takeuchi, 2017), "
                                             "CC BY 4.0, https://huggingface.co/datasets/shunk031/STAIR-Captions. "
                                             "Photos are not in this pack: the kit fetches them from "
                                             "https://cocodataset.org (only photos under CC BY 2.0 or no known "
                                             "copyright)."),
    "coco_cn": (build_coco_cn, "Sentences: COCO-CN (Li et al., 2019), MIT licence, "
                               "https://huggingface.co/datasets/AIMClab-RUC/COCO-CN and "
                               "https://github.com/li-xirong/coco-cn (human-written sentences only). Photos are not in "
                               "this pack: the kit fetches them from https://cocodataset.org (only photos under CC BY "
                               "2.0 or no known copyright)."),
}

# How many pictures a full build takes from each collection (about what each offers after the licence and
# description checks).
WORLD_LIMITS = {
    "japan_search": 3000,
    "ksamsok": 5000,
    "rijksmuseum": 6000,
    "stair_captions": 20000,
    "coco_cn": 4000,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one world pack builder.")
    parser.add_argument("key", choices=sorted(WORLD_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = WORLD_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
