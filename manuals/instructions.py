"""A copy of the Digital Accessibility Toolkit's app/toolkit/manuals/instructions.py (keep the two alike): plain-text
instructions, the shared record format (format 1, also the Picture Describers website's export) and tidying OCR text
into numbered steps. The builder (build_manuals.py) uses extract() on Open Food Facts' texts and to_record() to
write the index; the toolkit reads the same records.

The toolkit's own description follows.

Short instructions as plain text: cooking instructions of a frozen pizza or a microwave meal, the directions on a
product's label, read at once (no PDF, no "open the manual" step), as the owner asked:

    "Cooking instructions for DiGiorno Rising Crust Pepperoni. Conventional oven: 1. Preheat oven to 400°F.
     2. Remove pizza from box and plastic wrap. 3. Bake on center rack 22 to 25 minutes. Let stand 5 minutes.
     Safety: Cook to an internal temperature of 165°F. (Open Food Facts contributors, CC BY-SA.)"

Where they come from (each keeps its credit and licence, said at the end):
  - the offline instruction collections (collections.py): per product, by barcode, made by the toolkit-models
    workflow from Open Food Facts (the "preparation" field, and the text of its back-of-pack photos read with OCR;
    CC BY-SA) and from the Picture Describers website's volunteers (describe.getbraille.com; checked by two people);
  - a photo of the back of the package (the Camera window's key I, or a picture): its text, read by the program's
    text reader, goes through extract() here;
  - when a frozen or ready meal has none: the US Department of Agriculture's general food-safety guidance
    (general_guidance; public domain), said plainly to be general guidance, not the package's.

The record format (from_record / to_record), shared with the collections and the volunteers' export (format 1):
  {"format": 1, "barcode", "product_name", "brand", "quantity", "kind": "cooking"|"directions"|"warnings"|"storage",
   "methods": [{"name", "steps": [...], "temperature", "time"}], "standing_time", "safety": [...], "notes",
   "text" (numbered plain text ready to read aloud), "source", "source_url", "image_url", "image_licence",
   "licence", "credit", "reviews", "accepted_at"}
The same tidying is in the toolkit-models builder (manuals/instructions.py there): keep the two alike.

Main parts: Method, Instructions (words(), steps_text()), from_record, extract(text, product) -> Instructions or
None, looks_like(text), tidy(text), general_guidance(name, categories), USDA_TEMPERATURES.
Nothing here uses the network or a model.
"""

import re
from dataclasses import dataclass, field

KINDS = {"cooking": "Cooking instructions", "directions": "Directions", "warnings": "Warnings",
         "storage": "Storage"}
METHOD_NAMES = [("conventional oven", "Conventional oven"), ("toaster oven", "Toaster oven"),
                ("air fryer", "Air fryer"), ("microwave", "Microwave"), ("stovetop", "Stovetop"),
                ("stove top", "Stovetop"), ("skillet", "Skillet"), ("grill", "Grill"), ("oven", "Conventional oven")]
START = re.compile(r"\b(cooking|heating|baking|preparation|prep|microwave|oven|directions|instructions|how to "
                   r"(?:cook|prepare|use|heat)|preheat|to prepare|to heat|to cook)\b", re.I)
STOP = re.compile(r"\b(ingredients?\s*:|nutrition facts|distributed by|manufactured (?:by|for)|made in\b|contains\s*:|"
                  r"allergen|net wt|questions\s*(?:or comments)?\s*\?|visit us|www\.|https?:|©|upc\b|"
                  r"serving size|amount per serving|% daily value)", re.I)
VERBS = re.compile(r"\b(preheat|bake|cook|heat|microwave|remove|place|stir|let stand|stand|rotate|turn|cover|"
                   r"vent|puncture|peel|apply|rinse|shake|spray|use|pour|add|boil|simmer|fry|serve)\b", re.I)
TEMPERATURE = re.compile(r"(\d{3})\s*(?:°|º|˚|degrees?|deg\.?)?\s*([FC])\b", re.I)
TIME = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:-|–|to)\s*(\d+(?:[.,]\d+)?)\s*(min(?:ute)?s?|sec(?:ond)?s?|hours?|hrs?)\b"
                  r"|(\d+(?:\s+\d/\d|[.,]\d+)?)\s*(min(?:ute)?s?|sec(?:ond)?s?|hours?|hrs?)\b", re.I)
SAFETY = re.compile(r"\b(165|160|145)\s*°?\s*F\b|internal temperature|cook thoroughly|not ready to eat|do not eat "
                    r"(?:raw|uncooked)|food safety|keep frozen|must be cooked|for food safety|do not refreeze|"
                    r"refrigerate (?:leftovers|after)|caution|warning|hot\b.*\bhandle", re.I)
STANDING = re.compile(r"\b(let (?:it )?(?:stand|sit|rest|cool)|standing time|stand(?:s)? for)\b", re.I)
HEADING = re.compile(r"(?:(?:cooking|heating|baking|preparation|prep|microwave|oven|use)\s+)?(?:instructions|"
                     r"directions|method)|how to (?:cook|prepare|use|heat)", re.I)
MAX_STEPS = 14
MAX_STEP = 220              # characters: a longer "step" is a whole column of the package read as one line
MAX_SAFETY = 160
# Package text that is never an instruction step.
NOISE = re.compile(r"\b(calories|total fat|saturated fat|trans fat|cholesterol|sodium|carbohydrate|dietary fiber|"
                   r"protein \d|% ?dv|daily value|ingredients?\s*:|net wt|serving size|servings per|best by|"
                   r"distributed by|manufactured|nutrition|www\.|\.com\b|upc)", re.I)


@dataclass
class Method:
    """One way to prepare it: name ("Microwave"), steps (sentences, in order), temperature ("400°F"), time ("22 to
    25 minutes")."""
    name: str
    steps: list = field(default_factory=list)
    temperature: str = ""
    time: str = ""


@dataclass
class Instructions:
    """Plain-text instructions of one product (see the module docstring for the fields of the shared format).
    general: True for general guidance that is not the package's own (USDA); machine_read: read by OCR from a
    package photo and not checked by a person (said with its credit)."""
    product: str = ""
    brand: str = ""
    barcode: str = ""
    kind: str = "cooking"
    methods: list = field(default_factory=list)
    standing_time: str = ""
    safety: list = field(default_factory=list)
    notes: str = ""
    text: str = ""
    source: str = ""
    source_url: str = ""
    licence: str = ""
    credit: str = ""
    reviews: int = 0
    general: bool = False
    machine_read: bool = False

    @property
    def heading(self):
        """"Cooking instructions for DiGiorno Rising Crust Pepperoni"."""
        name = " ".join(w for w in (self.brand, self.product) if w and (not self.product or
                                                                          self.brand.lower() not in
                                                                          self.product.lower())).strip()
        kind = KINDS.get(self.kind, "Instructions")
        return f"{kind} for {name}" if name else kind

    def steps_text(self):
        """The instructions themselves as numbered plain text: the given text, else made from the methods, the
        standing time, the safety lines and the notes."""
        if self.text.strip():
            return self.text.strip()
        parts = []
        for m in self.methods:
            steps = " ".join(f"{i}. {_sentence(s)}" for i, s in enumerate(m.steps, 1))
            parts.append(f"{m.name}: {steps}" if m.name else steps)
        if self.standing_time:
            parts.append(_sentence(f"Standing time: {self.standing_time}"))
        if self.safety:
            parts.append("Safety: " + " ".join(_sentence(s) for s in self.safety))
        if self.notes:
            parts.append(_sentence(self.notes))
        return "\n".join(p for p in parts if p)

    def credit_words(self):
        """The source, credited as given: "(Open Food Facts contributors, CC BY-SA 4.0. Checked by 2 volunteers.)"."""
        who = self.credit or self.source
        bits = [b for b in (who, self.licence) if b]
        line = ", ".join(bits)
        if self.reviews:
            line += f". Checked by {self.reviews} volunteer{'s' if self.reviews != 1 else ''}"
        elif self.machine_read:
            line += ". Read by machine from a package photo: it may have mistakes; check the package"
        return f"({line}.)" if line else ""

    def words(self):
        """Everything said and shown: the heading, the instructions and the credit at the end; general guidance
        says so first."""
        intro = ("This product's own instructions were not found. General food-safety guidance, not the package's: "
                 if self.general else "")
        body = self.steps_text()
        return f"{intro}{self.heading}:\n{body}\n{self.credit_words()}".strip()

    def is_empty(self):
        """True when there is nothing to read."""
        return not (self.text.strip() or any(m.steps for m in self.methods) or self.safety)


def _sentence(text):
    """text ending with a full stop (or its own ! or ?)."""
    text = str(text or "").strip()
    return text if not text or text[-1] in ".!?:" else text + "."


def from_record(rec):
    """Instructions from a record of the shared format (a dict; see the module docstring), or None when it has no
    instructions."""
    if not isinstance(rec, dict):
        return None
    methods = []
    for m in rec.get("methods") or []:
        if isinstance(m, dict):
            steps = [str(s).strip() for s in m.get("steps") or [] if str(s).strip()]
            methods.append(Method(str(m.get("name") or ""), steps, str(m.get("temperature") or ""),
                                  str(m.get("time") or "")))
    try:
        reviews = int(rec.get("reviews") or 0)
    except (TypeError, ValueError):
        reviews = 0
    out = Instructions(str(rec.get("product_name") or ""), str(rec.get("brand") or ""), str(rec.get("barcode") or ""),
                       str(rec.get("kind") or "cooking"), methods, str(rec.get("standing_time") or ""),
                       [str(s) for s in rec.get("safety") or [] if str(s).strip()], str(rec.get("notes") or ""),
                       str(rec.get("text") or ""), str(rec.get("source") or ""), str(rec.get("source_url") or ""),
                       str(rec.get("licence") or ""), str(rec.get("credit") or ""), reviews,
                       machine_read=rec.get("from") == "photo" and not reviews)
    return None if out.is_empty() else out


def to_record(ins):
    """The shared-format record of Instructions (the text made when it has none)."""
    return {"format": 1, "barcode": ins.barcode, "product_name": ins.product, "brand": ins.brand, "kind": ins.kind,
            "methods": [{"name": m.name, "steps": m.steps, "temperature": m.temperature, "time": m.time}
                        for m in ins.methods],
            "standing_time": ins.standing_time, "safety": ins.safety, "notes": ins.notes, "text": ins.steps_text(),
            "source": ins.source, "source_url": ins.source_url, "licence": ins.licence, "credit": ins.credit,
            "reviews": ins.reviews}


# ------------------------------------------------------------------------------------------- reading OCR text

def _units(text):
    """Temperatures as "400°F" and times as "22 to 25 minutes"."""
    text = TEMPERATURE.sub(lambda m: f"{m.group(1)}°{m.group(2).upper()}", text)

    def time_words(m):
        if m.group(1):
            a, b, unit = m.group(1), m.group(2), m.group(3)
        else:
            a, b, unit = m.group(4), None, m.group(5)
        u = unit.lower()
        word = "seconds" if u.startswith("sec") else "hours" if u.startswith("h") else "minutes"
        if b is None and a in ("1", "1.0"):
            word = word[:-1]
        return f"{a} to {b} {word}" if b else f"{a} {word}"
    return TIME.sub(time_words, text)


def _sentence_case(text):
    """Text written in capitals ("PREHEAT OVEN TO 400°F.") in ordinary sentence case; mixed text is kept."""
    letters = [c for c in text if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) / len(letters) < 0.7:
        return text
    low = text.lower()
    low = re.sub(r"(^|[.!?]\s+|\n)([a-z])", lambda m: m.group(1) + m.group(2).upper(), low)
    low = re.sub(r"(\d)\s*(°|º|˚|degrees?)?\s*f\b", lambda m: m.group(1) + (m.group(2) or " ") + "F", low)
    return low.replace("°c", "°C")


def tidy(text):
    """OCR text made readable: broken words joined, one space between words, capitals in sentence case, units
    written out."""
    text = str(text or "").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)           # a word broken at the end of a line
    text = re.sub(r"[•●▪■◆*·]+", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return _units(_sentence_case(text)).strip()


def looks_like(text):
    """True when text reads like cooking or use instructions: a temperature, a time or "microwave", and a verb; or
    a "Directions" heading and two verbs."""
    text = str(text or "")
    if (TEMPERATURE.search(text) or TIME.search(text) or re.search(r"microwave", text, re.I)) and VERBS.search(text):
        return True
    # Label directions ("Directions: Shake well. Apply to wet hair ..."): the heading and two verbs.
    return bool(re.search(r"\b(directions|how to use|instructions)\b", text, re.I)) and len(VERBS.findall(text)) >= 2


def _method_of(line):
    """(name, rest of the line) when line starts a method ("MICROWAVE: Remove ..."), else None."""
    low = line.lower().strip(" :-")
    for word, name in METHOD_NAMES:
        m = re.match(r"(?:for\s+|to\s+(?:cook|heat)\s+in\s+(?:the\s+|a\s+)?)?" + re.escape(word) +
                     r"(?:\s+(?:directions|instructions|method|cooking|heating|oven))?\s*(?:\(.*?\))?\s*[:.\-]?\s*",
                     low)
        if m and (m.end() == len(low) or low[m.end() - 1:m.end()] in (":", ".", "-", " ") and
                  (":" in line[:m.end() + 2] or m.end() == len(low) or line[:len(word)].isupper())):
            return name, line.strip()[m.end():].strip(" :-")
    return None


def _steps_of(text):
    """The steps of a method's text: by its own numbers ("1. ... 2. ...") when it has them, else one per
    sentence; short pieces are joined to the step before."""
    text = " ".join(text.split())
    numbered = re.split(r"(?:^|\s)(?:step\s*)?\d{1,2}\s*[.)]\s+(?=[A-Za-z])", text, flags=re.I)
    pieces = [p for p in numbered if p.strip()] if len(numbered) > 2 else \
        re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    steps = []
    for p in pieces:
        p = p.strip(" ;,")
        if not p:
            continue
        if steps and len(p) < 12:
            steps[-1] = steps[-1].rstrip(".") + " " + p
        else:
            steps.append(p[0].upper() + p[1:])
    return steps[:MAX_STEPS]


def _section(text):
    """The part of text with the instructions: from the first heading or sentence that starts them (START, with a
    temperature, a time or a verb soon after) to the first heading that does not belong (STOP)."""
    best = None
    for m in START.finditer(text):
        window = text[m.start():m.start() + 500]
        if looks_like(window):
            best = m.start()
            break
    if best is None:
        return ""
    # Begin at the start of that line, or at the heading when the line has other words before it.
    line_start = text.rfind("\n", 0, best) + 1
    if best - line_start > 40 or re.search(r"[.!?]", text[line_start:best]):
        line_start = best
    best = line_start
    rest = text[best:]
    stop = STOP.search(rest, 20)
    return rest[:stop.start()] if stop else rest


def extract(text, product="", brand="", barcode="", source="", licence="", credit="", source_url=""):
    """The Instructions in OCR text (a back-of-pack photo, Open Food Facts' preparation field), or None when it has
    none (looks_like). Methods are found by their headings (Conventional oven, Microwave, Air fryer ...); safety
    lines (165°F, cook thoroughly, keep frozen ...) and the standing time are kept apart."""
    text = tidy(text)
    section = _section(text) or (text if looks_like(text) and len(text) < 1500 else "")
    if not section:
        return None
    methods, current = [], Method("")
    safety, standing = [], ""
    for line in section.split("\n"):
        line = line.strip()
        if not line:
            continue
        started = _method_of(line)
        if started is not None:
            if current.steps or current.name:
                methods.append(current)
            current = Method(started[0])
            line = started[1]
            if not line:
                continue
        current.steps.append(line)
    if current.steps or current.name:
        methods.append(current)
    out = []
    for m in methods:
        steps = []
        for s in _steps_of(" ".join(m.steps)):
            s = re.sub(r"^(?:" + HEADING.pattern + r")\s*:\s*", "", s, flags=re.I).strip()
            if not s:
                continue
            s = s[0].upper() + s[1:]
            if NOISE.search(s) or len(s) > MAX_STEP or not re.search(r"[a-z]{3}", s):
                continue                        # nutrition facts, ingredients, a whole column read as one line
            if SAFETY.search(s) and not VERBS.search(s.split(".")[0][:12] or "") or re.search(
                    r"internal temperature|cook thoroughly|not ready to eat|keep frozen", s, re.I):
                if s not in safety and len(s) <= MAX_SAFETY:
                    safety.append(s)
                continue
            if HEADING.fullmatch(s.strip(" :.")):
                continue                        # a bare heading ("Cooking instructions")
            steps.append(s)
        if not steps:
            continue
        joined = " ".join(steps)
        t = TEMPERATURE.search(joined)
        tm = re.search(r"\d+(?:\s+\d/\d|[.,]\d+)?(?:\s*to\s*\d+(?:\s+\d/\d)?)?\s*(?:minutes?|seconds?|hours?)",
                       joined)
        name = m.name if m.name else ("" if len(methods) == 1 else "Instructions")
        out.append(Method(name, steps, f"{t.group(1)}°{t.group(2).upper()}" if t else "",
                          tm.group(0) if tm else ""))
    # Safety lines printed elsewhere on the package ("Keep frozen. Not ready to eat. Cook thoroughly.").
    for s in re.split(r"(?<=[.!?])\s+|\n", text):
        s = s.strip()
        if s and len(s) < 160 and re.search(r"internal temperature|cook thoroughly|not ready to eat|keep frozen|"
                                            r"do not refreeze", s, re.I) and s not in safety:
            safety.append(s)
    ins = Instructions(product, brand, barcode, "cooking" if re.search(r"oven|microwave|bake|cook|heat|°F", section,
                                                                       re.I) else "directions",
                       out, standing, safety, source=source, licence=licence, credit=credit, source_url=source_url)
    return ins if good_enough(ins) else None


def good_enough(ins):
    """True when extracted instructions are worth reading out: at least two steps in all, most of them starting
    with words (not numbers or stray letters), and for cooking a step with a temperature, a time or "microwave"."""
    steps = [st for m in ins.methods for st in m.steps]
    if len(steps) < 2:
        return False
    wordy = sum(1 for st in steps if re.match(r"[A-Za-z][a-z]+\b", st) and VERBS.search(st))
    if wordy < max(1, len(steps) // 2):
        return False
    if ins.kind == "cooking":
        return any(TEMPERATURE.search(st) or TIME.search(st) or re.search(r"microwave", st, re.I) for st in steps)
    return True


# --------------------------------------------------------------------------------------- general guidance (USDA)

USDA_SOURCE = "US Department of Agriculture, Food Safety and Inspection Service (public domain)"
USDA_URL = "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/" \
           "safe-temperature-chart"
# Safe minimum internal temperatures (USDA FSIS "Safe Minimum Internal Temperature Chart"): words -> (food, line).
USDA_TEMPERATURES = [
    (r"chicken|turkey|poultry|duck|goose", "Poultry (chicken, turkey, duck), whole or ground: 165°F"),
    (r"ground|burger|meatball|sausage|meatloaf", "Ground meats (beef, pork, veal, lamb): 160°F"),
    (r"beef|pork|veal|lamb|steak|roast|chop", "Beef, pork, veal and lamb steaks, chops and roasts: 145°F, then rest "
                                              "3 minutes"),
    (r"fish|salmon|tuna|cod|shrimp|shellfish|seafood|crab|lobster", "Fish and shellfish: 145°F"),
    (r"egg|quiche|omelet|frittata", "Egg dishes: 160°F"),
    (r"ham", "Fully cooked ham, reheated: 140°F (165°F if it was not packaged in a USDA-inspected plant)"),
    (r"leftover|casserole|lasagna|lasagne|pizza|meal|entree|entrée|dinner|bowl|burrito|pot pie|frozen",
     "Leftovers, casseroles and frozen or ready meals: 165°F"),
]
FROZEN_WORDS = re.compile(r"frozen|microwav|ready[- ]meals?|ready-made meals?|tv dinners?|pot pies?|frozen entr", re.I)


def general_guidance(name="", categories=""):
    """The USDA's general guidance for a frozen or ready meal that has no instructions of its own, or None for
    other products. It says plainly that it is general guidance, not the package's."""
    words = f"{name} {categories}"
    if not FROZEN_WORDS.search(words):
        return None
    temps = [line for pattern, line in USDA_TEMPERATURES if re.search(r"\b(?:" + pattern + r")", words, re.I)]
    if not temps:
        temps = [USDA_TEMPERATURES[-1][1]]
    steps = ["Follow the cooking directions on the package if you can get them read",
             "Cook until it is steaming hot all the way through, to a safe internal temperature checked with a food "
             "thermometer in several places: " + "; ".join(temps[:3]),
             "In a microwave, cover it, stir or turn it halfway, and let it stand for the time the package says "
             "(standing time finishes the cooking)",
             "Do not eat a frozen meal raw or partly cooked when the package says \"cook thoroughly\" or \"not ready "
             "to eat\""]
    return Instructions(name, "", "", "cooking", [Method("", steps)], source=USDA_SOURCE, source_url=USDA_URL,
                        licence="public domain", credit="USDA Food Safety and Inspection Service", general=True)
