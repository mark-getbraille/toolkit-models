"""A small reader for LINKED ART (JSON-LD) museum records, for any pack that reads a Linked Art collection.

Linked Art (https://linked.art) is the shared JSON-LD form, built on CIDOC-CRM and the Getty AAT, in which many
museums publish their records: an object ("HumanMadeObject") has names (identified_by), statements
(referred_to_by), types (classified_as), its making (produced_by: who, when), what it is made of (made_of), its
pictures (shows -> a VisualItem whose digitally_shown_by gives IIIF image services) and rights (subject_to). This
module turns such a record into the plain fields the packs use, and checks rights the way the packs must: the
picture's OWN rights statement must be CC0 or the Public Domain Mark (rights_of), else it is not open.

Used by adult_art_packs.py for the J. Paul Getty Museum (its SPARQL endpoint finds the objects; each object's
record and its image's record are read here). Nothing here is specific to one museum except getty_* at the end.

Main parts:
  fetch(s, url)                 a record (JSON), paced (PAUSE seconds between requests), None on failure
  title(record), statements(record), types(record), maker(record), date(record), materials(record)
  rights_of(node)               "CC0", "Public Domain Mark" or "" (from subject_to, anywhere inside node)
  iiif_service(visual_item)     the IIIF Image API base address of a VisualItem, or ""
  image_url(service, size)      a picture address from a IIIF base ("/full/!1600,1600/0/default.jpg")
  plain_fields(record)          {"title", "kind", "artist", "date", "medium", "text", "place"} for the packs
"""

import re
import time

PAUSE = 0.5                        # seconds between two requests to one Linked Art server
_last = [0.0]
AAT_PRIMARY_TITLE = "300404670"    # "preferred terms" / primary title
AAT_DESCRIPTION = ("300080091", "300435416")          # description, description (activity)
AAT_MATERIALS = ("300435429", "300010358")            # materials statement, materials
AAT_CULTURE = "300055768"
AAT_BRIEF = "300418049"                               # "brief text" (a form, not a kind of statement)
GENERIC_TYPES = re.compile(r"^(artwork|work|works|object|objects|collection item|human-made object|"
                           r"classification \(category\))$", re.I)
OPEN_RIGHTS = (("publicdomain/zero", "CC0"), ("publicdomain/mark", "Public Domain Mark"))


def as_list(value):
    """A JSON-LD value as a list (a single value or none become a list)."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def fetch(s, url, pause=None, timeout=60, tries=3):
    """The JSON record at url, waiting at least PAUSE seconds since the last request; None on failure."""
    for attempt in range(tries):
        wait = (PAUSE if pause is None else pause) - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = s.get(url, timeout=timeout, headers={"Accept": "application/ld+json, application/json"})
            if r.status_code == 200:
                return r.json()
            if r.status_code in (403, 404, 410):
                return None
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(2 * (attempt + 1))
    return None


def type_ids(node):
    """The ids of a node's classified_as types (the AAT numbers at their end)."""
    return [str(t.get("id", "")) for t in as_list(node.get("classified_as")) if isinstance(t, dict)]


def has_type(node, *aat):
    """True when one of the node's types ends with one of the AAT numbers."""
    return any(i.rstrip("/").endswith(a) for i in type_ids(node) for a in aat)


def title(record):
    """The object's primary title (an identified_by Name classified as primary title), else its first name, else
    its _label."""
    names = [n for n in as_list(record.get("identified_by")) if isinstance(n, dict) and n.get("type") == "Name"]
    for name in names:
        if has_type(name, AAT_PRIMARY_TITLE) and name.get("content"):
            return str(name["content"]).strip()
    for name in names:
        if name.get("content"):
            return str(name["content"]).strip()
    return str(record.get("_label") or "").strip()


def statements(record):
    """{kind of statement: text} of the object's referred_to_by texts (description, materials, culture, credit
    ...), the kind from the statement's own type label (not "Brief Text")."""
    out = {}
    for st in as_list(record.get("referred_to_by")):
        if not isinstance(st, dict) or not st.get("content"):
            continue
        labels = [str(t.get("_label") or "") for t in as_list(st.get("classified_as")) if isinstance(t, dict)
                  and not str(t.get("id", "")).endswith(AAT_BRIEF)]
        key = (labels[0] if labels else str(st.get("_label") or "statement")).lower()
        out.setdefault(key, str(st["content"]).strip())
    return out


def _statement(record, aat, words):
    """The first statement of the record whose type is one of aat, or whose kind names one of words."""
    for st in as_list(record.get("referred_to_by")):
        if isinstance(st, dict) and st.get("content") and has_type(st, *aat):
            return str(st["content"]).strip()
    for kind, text in statements(record).items():
        if any(w in kind for w in words):
            return text
    return ""


def types(record):
    """The labels of the object's own types (Drawings, Paintings, Photographs ...), generic ones left out."""
    out = []
    for t in as_list(record.get("classified_as")):
        label = str(t.get("_label") or "").strip() if isinstance(t, dict) else ""
        if label and not GENERIC_TYPES.match(label):
            out.append(label)
    return out


def maker(record):
    """Who made it: the carried_out_by labels of produced_by and its parts."""
    production = record.get("produced_by") or {}
    people = as_list(production.get("carried_out_by"))
    for part in as_list(production.get("part")):
        if isinstance(part, dict):
            people += as_list(part.get("carried_out_by"))
    labels = [str(p.get("_label") or "").strip() for p in people if isinstance(p, dict)]
    return "; ".join(dict.fromkeys(l for l in labels if l))


def date(record):
    """When it was made: the produced_by timespan's name, else its _label."""
    span = (record.get("produced_by") or {}).get("timespan") or {}
    for name in as_list(span.get("identified_by")):
        if isinstance(name, dict) and name.get("content"):
            return str(name["content"]).strip()
    return str(span.get("_label") or "").strip()


def materials(record):
    """What it is made of: the materials statement, else the made_of labels."""
    said = _statement(record, AAT_MATERIALS, ("material", "medium"))
    if said:
        return said
    return ", ".join(str(m.get("_label") or "").strip() for m in as_list(record.get("made_of"))
                     if isinstance(m, dict) and m.get("_label"))


def rights_of(node):
    """"CC0" or "Public Domain Mark" when the node's own subject_to rights (looked for anywhere inside the node,
    in the types of each Right) name that Creative Commons statement; "" otherwise (anything else is not open)."""
    found = []

    def walk(n, inside_right=False):
        """Look through the node for Rights and their types."""
        if isinstance(n, dict):
            right = inside_right or n.get("type") == "Right"
            ident = str(n.get("id", ""))
            if right:
                for part, name in OPEN_RIGHTS:
                    if part in ident:
                        found.append(name)
            for k, v in n.items():
                if k in ("subject_to", "classified_as") or right:
                    walk(v, right)
        elif isinstance(n, list):
            for x in n:
                walk(x, inside_right)
    walk({"subject_to": node.get("subject_to")} if isinstance(node, dict) else {})
    return found[0] if found else ""


IIIF_BASE = re.compile(r"^(https?://[^\s]+?/iiif/[^\s]*?)(/full/.*)?$")


def iiif_service(visual_item):
    """The IIIF Image API base address in a VisualItem's digitally_shown_by access points, or ""."""
    for digital in as_list(visual_item.get("digitally_shown_by")):
        for point in as_list(digital.get("access_point") if isinstance(digital, dict) else None):
            ident = str(point.get("id", "")) if isinstance(point, dict) else ""
            if "/iiif/" in ident and "/full/" not in ident:
                return ident.rstrip("/")
    for digital in as_list(visual_item.get("digitally_shown_by")):
        for point in as_list(digital.get("access_point") if isinstance(digital, dict) else None):
            m = IIIF_BASE.match(str(point.get("id", "")) if isinstance(point, dict) else "")
            if m:
                return m.group(1).rstrip("/")
    return ""


def image_url(service, size=1600):
    """A picture address from a IIIF Image API base."""
    return f"{service}/full/!{size},{size}/0/default.jpg" if service else ""


def plain_fields(record):
    """The fields the packs use, from a Linked Art object record."""
    return {"title": title(record), "kind": (types(record) or [""])[0], "artist": maker(record),
            "date": date(record), "medium": materials(record),
            "text": _statement(record, AAT_DESCRIPTION, ("description",)),
            "place": _statement(record, (AAT_CULTURE,), ("culture",))}


# ----------------------------------------------------------------- The J. Paul Getty Museum

GETTY_SPARQL = "https://data.getty.edu/museum/collection/sparql"
GETTY_QUERY = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
SELECT DISTINCT ?o WHERE {{ ?o a crm:E22_Human-Made_Object ; crm:P1_is_identified_by ?n .
  ?n crm:P190_has_symbolic_content ?t . FILTER(REGEX(?t, "{pattern}", "i")) }} LIMIT {limit}"""


def getty_objects(s, pattern, limit=2000):
    """The Getty Museum object addresses whose name matches a regular expression (its SPARQL endpoint)."""
    try:
        r = s.post(GETTY_SPARQL, data={"query": GETTY_QUERY.format(pattern=pattern, limit=limit)},
                   headers={"Accept": "application/sparql-results+json"}, timeout=180)
        rows = r.json().get("results", {}).get("bindings", []) if r.status_code == 200 else []
    except Exception:  # noqa: BLE001 - nothing found
        rows = []
    return [b["o"]["value"] for b in rows if b.get("o", {}).get("value")]


def getty_record(s, uri):
    """(object record, picture address, rights) of one Getty object: the image's OWN rights statement (its
    VisualItem's subject_to) decides; ("", "") when it has no open image."""
    record = fetch(s, uri)
    if not record:
        return None, "", ""
    for shown in as_list(record.get("shows")):
        if not isinstance(shown, dict) or not shown.get("id"):
            continue
        visual = fetch(s, shown["id"])
        if not visual:
            continue
        rights, service = rights_of(visual), iiif_service(visual)
        if service:
            return record, image_url(service), rights
    return record, "", ""
