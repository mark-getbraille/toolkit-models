"""Pack builder for MEDICINE NAMES AND STRENGTHS ON PACKAGES AND LABELS: photos of prescription bottles, boxes,
blister packs, inhalers, insulin pens, eye drops and other medicine packages whose own Commons title names a medicine
AND its strength ("Ibuprofen 400 mg tablets.jpg", "Lantus 100 units/ml insulin pen.jpg"). Used by build_packs.py in
the same way as its own PACKS: build_commons_medication_labels(limit) returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus "place" where the file's camera coordinates give a country. A
picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file"
names the same picture (food_packs.with_twins). The limit counts pictures.

Why: "What medicine is this, and how strong?" is one of the questions blind people most often need answered, and the
existing medicine packs say only what kind of thing a package is ("a pill bottle") or which medicine a pill looks like.

THE NAME AND STRENGTH COME ONLY FROM THE LABEL DATA, never from the picture: a file is used only when its own title (or,
failing that, its own description) names a medicine from MEDICINES and, within a few words, a strength with its unit
(STRENGTH: mg, mcg, g, ml, IU, units, %, and "per ml" or "per dose" forms). The answer says where it comes from and ends
with PHARMACIST_NOTE: "This looks like ibuprofen 400 mg, going by the photo's own title. Check with your pharmacist
before taking any medicine: a photo cannot show the whole label." Two different strengths in the words give no answer
(the photo may show two packs). Brand names are said as the title has them, with the generic name from MEDICINES
("Lantus (insulin glargine) 100 units/ml").

The pack (open, checked at the source in November 2026):
  commons_medication_labels  Wikimedia Commons, found with Commons search (srsearch intitle:<medicine name> and a unit
                             of strength, files only): files CC0, public domain, CC BY or an open government
                             licence (each file's licence checked on its own page; never BY-SA, NC or ND); captions
                             CC0. Files that sit in a category med_vet_packs.med_commons_medicines or
                             med_commons_supplies reads (or one of its subcategories) are left out: those packs
                             already show them.

Left out by their words (med_vet_packs.left_out_because, the current-items rule of the medicine packs): anything old,
historic, discontinued or in a museum, patients, injuries, drug misuse, children, and people (the pack shows packages
only). Illegal drugs are never in MEDICINES.

Looked at and not built here (the reasons are in training-kit/kit/daily_access_sources.py and med_vet_sources.py):
DailyMed's package and label pictures (the drug makers' artwork, "may be protected" by NLM's own words: the kit's
research entries dailymed_human_labels and dailymed_vet_labels, which already take each label's package, carton,
bottle or container picture), NLM's C3PI pills (research use: c3pi_pills), the Commons categories of pill bottles,
blister packs, inhalers, insulin pens, eye drops and pill organizers (med_vet_packs), Open Images medicine labels
(med_vet_packs.open_images_medical, everyday_packs), Amazon Berkeley Objects' medication listings
(packaged_goods_packs.abo_packaged_goods), Mobile-Captured Drug Packs (Mendeley Data bsmy5jjysy, CC BY 4.0, but no
names or strengths with its 2,000 photos) and the Italian OTC medicines set on Hugging Face (no statement of where its
pictures come from).

Safety (packs/SOURCE-RULES.md): no sexual content; no people. Never used for picture-making (a model must never learn
to draw medicine labels): the kit puts it in NOT_FOR_PICTURE_MAKING.

    python packs/medication_label_packs.py commons_medication_labels --limit 8      (a quick check)
"""

import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, ALT_TEXT

MEDICINE_Q = "What medicine is this, and what strength?"
WHAT_Q = "What is this?"
PHARMACIST_NOTE = ("Check with your pharmacist before taking any medicine: a photo cannot show the whole label.")

# Medicines looked for (generic names, and brand names with their generic name). Only medicines sold today, none of
# them illegal drugs; the owner's current-items rule also leaves out files whose words say old or discontinued.
GENERICS = (
    "acetaminophen", "paracetamol", "ibuprofen", "naproxen", "aspirin", "diclofenac", "celecoxib", "amoxicillin",
    "azithromycin", "doxycycline", "cephalexin", "ciprofloxacin", "metronidazole", "nitrofurantoin", "clarithromycin",
    "penicillin", "metformin", "glipizide", "gliclazide", "sitagliptin", "insulin glargine", "insulin lispro",
    "insulin aspart", "insulin", "atorvastatin", "simvastatin", "rosuvastatin", "pravastatin", "lisinopril", "ramipril",
    "enalapril", "losartan", "valsartan", "amlodipine", "nifedipine", "metoprolol", "atenolol", "bisoprolol",
    "propranolol", "carvedilol", "hydrochlorothiazide", "furosemide", "spironolactone", "warfarin", "apixaban",
    "rivaroxaban", "clopidogrel", "levothyroxine", "omeprazole", "esomeprazole", "pantoprazole", "lansoprazole",
    "ranitidine", "famotidine", "loratadine", "cetirizine", "fexofenadine", "diphenhydramine", "chlorphenamine",
    "salbutamol", "albuterol", "budesonide", "fluticasone", "montelukast", "beclometasone", "prednisone",
    "prednisolone", "hydrocortisone", "dexamethasone", "sertraline", "fluoxetine", "citalopram", "escitalopram",
    "paroxetine", "venlafaxine", "duloxetine", "bupropion", "mirtazapine", "trazodone", "amitriptyline", "gabapentin",
    "pregabalin", "lamotrigine", "levetiracetam", "carbamazepine", "valproate", "quetiapine", "risperidone",
    "olanzapine", "aripiprazole", "lithium", "donepezil", "levodopa", "tramadol", "codeine", "morphine", "oxycodone",
    "naloxone", "ondansetron", "loperamide", "allopurinol", "colchicine", "tamsulosin", "finasteride", "sildenafil",
    "latanoprost", "timolol", "folic acid", "ferrous sulfate", "vitamin d", "cholecalciferol", "methotrexate",
    "hydroxychloroquine", "epinephrine", "adrenaline", "melatonin", "oseltamivir", "acyclovir",
    "valacyclovir", "fluconazole", "clotrimazole", "miconazole", "terbinafine", "mupirocin", "ivermectin",
)
BRANDS = {
    "Tylenol": "acetaminophen", "Panadol": "paracetamol", "Advil": "ibuprofen", "Motrin": "ibuprofen",
    "Nurofen": "ibuprofen", "Aleve": "naproxen", "Voltaren": "diclofenac",
    "Lipitor": "atorvastatin",
    "Crestor": "rosuvastatin", "Zocor": "simvastatin", "Glucophage": "metformin", "Lantus": "insulin glargine",
    "Humalog": "insulin lispro", "NovoRapid": "insulin aspart", "Novolog": "insulin aspart",
    "Synthroid": "levothyroxine",
    "Eltroxin": "levothyroxine", "Prilosec": "omeprazole", "Losec": "omeprazole", "Nexium": "esomeprazole",
    "Zantac": "ranitidine", "Pepcid": "famotidine", "Claritin": "loratadine", "Zyrtec": "cetirizine",
    "Allegra": "fexofenadine", "Benadryl": "diphenhydramine", "Ventolin": "salbutamol", "Pulmicort": "budesonide",
    "Flovent": "fluticasone", "Flixotide": "fluticasone", "Singulair": "montelukast", "Zoloft": "sertraline",
    "Prozac": "fluoxetine", "Lexapro": "escitalopram", "Wellbutrin": "bupropion", "Neurontin": "gabapentin",
    "Lyrica": "pregabalin", "Lamictal": "lamotrigine", "Keppra": "levetiracetam", "Seroquel": "quetiapine",
    "Xarelto": "rivaroxaban", "Eliquis": "apixaban", "Plavix": "clopidogrel", "Coumadin": "warfarin",
    "Imodium": "loperamide", "Zofran": "ondansetron", "Flomax": "tamsulosin", "Viagra": "sildenafil",
    "Xalatan": "latanoprost", "EpiPen": "epinephrine", "Narcan": "naloxone", "Tamiflu": "oseltamivir",
    "Zovirax": "acyclovir", "Diflucan": "fluconazole", "Lamisil": "terbinafine", "Augmentin": "amoxicillin and "
    "clavulanic acid", "Zithromax": "azithromycin", "Cipro": "ciprofloxacin",
}
NAMES = sorted(list(GENERICS) + list(BRANDS), key=len, reverse=True)
NAME = re.compile(r"\b(" + "|".join(re.escape(n) for n in NAMES) + r")\b", re.I)
UNIT = r"(?:mg|mcg|µg|μg|g|ml|mL|IU|i\.u\.|units?|%)"
STRENGTH = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)\s?(" + UNIT[3:-1] + r")(?:\s?(?:/|per)\s?(\d+(?:[.,]\d+)?\s?)?"
                      r"(ml|mL|dose|actuation|puff|tablet|g))?(?![\w])", re.I)
# The forms a title may name, said as it names them.
FORMS = re.compile(r"\b(tablets?|caplets?|capsules?|softgels?|syrup|suspension|oral solution|drops|eye drops|"
                   r"ear drops|nasal spray|inhaler|insulin pen|pen|injection|vial|cream|ointment|gel|patch(es)?|"
                   r"suppositor(y|ies)|lozenges?|chewables?|granules|powder|sachets?|blister( pack)?|bottle|box|"
                   r"package|packet|carton)\b", re.I)
NEAR = 40           # the strength must start within this many characters after the medicine's name


def strength_text(m):
    """ "400 mg", "100 units/ml" or "0.5%" from a STRENGTH match, in plain lower case units."""
    number = m.group(1).replace(",", ".")
    unit = m.group(2).lower().replace("μg", "mcg").replace("µg", "mcg").replace("i.u.", "IU").replace("iu", "IU")
    unit = "units" if unit in ("unit", "units") else unit
    per = m.group(4)
    if per:
        amount = (m.group(3) or "").replace(",", ".").strip()
        per = f"/{amount} {per.lower()}" if amount and amount != "1" else f"/{per.lower()}"
    return f"{number}{'' if unit == '%' else ' '}{unit}{per or ''}"


def name_and_strength(text):
    """(medicine words, strength, form) from a file's title or description, or None: a name from MEDICINES followed
    within NEAR characters by a strength; None when no name, no strength, two different names or two different
    strengths are given (the photo may show two packs)."""
    text = re.sub(r"^File:", "", text or "").replace("_", " ")
    text = re.sub(r"\.(jpe?g|png|tiff?|webp)$", "", text, flags=re.I)
    names = {m.group(1).lower(): m for m in NAME.finditer(text)}
    if not names:
        return None
    generic_of = {n.lower(): g for n, g in BRANDS.items()}
    generics = {generic_of.get(n, n) for n in names}
    generics = {x for x in generics if not any(x != y and x in y for y in generics)}   # "insulin" in a Lantus title
    if len(generics) > 1:
        return None
    found = set()
    first = None
    for key, m in names.items():
        for s in STRENGTH.finditer(text):
            if m.end() <= s.start() <= m.end() + NEAR:
                found.add(strength_text(s))
                first = first or (m, s)
    if len(found) != 1:
        return None
    m, _s = first
    said = m.group(1)
    brand = next((b for b in BRANDS if b.lower() == said.lower()), None)
    words = f"{brand} ({BRANDS[brand]})" if brand else said.lower()
    form = FORMS.search(text)
    return words, found.pop(), form.group(1).lower() if form else ""


def medicine_rows(title, text, credit):
    """The rows for one file, or [] when neither its title nor its description names a medicine and one strength."""
    got = name_and_strength(title)
    source = "the photo's own title"
    if not got:
        got = name_and_strength(text)
        source = "the photo's own description"
    if not got:
        return []
    words, strength, form = got
    rows = [{"question": MEDICINE_Q, "answer": f"This looks like {words} {strength}"
             f"{' ' + form if form else ''}, going by {source}. {PHARMACIST_NOTE}", "credit": credit}]
    if text:
        rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
    return rows


def med_pack_categories(s):
    """The Commons categories med_vet_packs' medicine and supply packs read (and the subcategories of those they read
    one level down): a file in one of them is already shown there."""
    from med_vet_packs import MEDICINE_SPECS, SUPPLY_SPECS
    from food_packs import commons_members
    cats = set()
    for sp in MEDICINE_SPECS + SUPPLY_SPECS:
        cats.add(sp["category"])
        if sp["depth"]:
            cats |= {c.split(":", 1)[-1] for c in commons_members(s, sp["category"], "subcat")}
    return cats


def file_categories(s, titles):
    """{title: set of its (visible) category names}, 50 files a request."""
    from food_packs import commons_get
    out = {}
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "categories",
                               "clshow": "!hidden", "cllimit": 500})
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            out[p.get("title")] = {c["title"].split(":", 1)[-1] for c in p.get("categories") or []}
        time.sleep(1)
    return out


def search_titles(s, name, most=100):
    """Commons file titles whose title contains the medicine's name and whose words have a unit of strength (Commons
    search, files only)."""
    from food_packs import commons_get
    data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": most,
                           "srsearch": f'intitle:"{name}" (mg OR mcg OR ml OR units OR IU) filetype:bitmap'})
    return [r["title"] for r in (data.get("query") or {}).get("search") or []]


def build_commons_medication_labels(limit):
    """The commons_medication_labels pack (see the module docstring)."""
    from food_packs import with_twins
    from home_packs import commons_fetch, file_name
    from med_vet_packs import left_out_because
    from work_farm_mech_packs import free_entries
    s, rng = session(), pass_random(9303)
    names = list(NAMES)
    rng.shuffle(names)
    titles = []
    for name in names:
        titles += [t for t in search_titles(s, name) if t not in titles]
        if len(titles) > limit * 10 + 100:
            break
    say(f"Commons medication labels: {len(titles)} files found by name")
    shown = med_pack_categories(s)
    cats = file_categories(s, titles)
    titles = [t for t in titles if not cats.get(t, set()) & shown]
    say(f"Commons medication labels: {len(titles)} files not in the medicine packs' categories")
    items = []
    for title, url, credit, text, _raw in free_entries(s, titles):
        if left_out_because(title, text):
            continue
        rows = medicine_rows(title, text, credit)
        if rows:
            items.append((file_name("medlabel", title), url, rows))
        if len(items) >= int(limit * 1.15) + 2:
            break
    say(f"Commons medication labels: {len(items)} files name a medicine and its strength")
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- the packs

MEDICATION_PACKS = {
    "commons_medication_labels": (build_commons_medication_labels,
                                  "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain, CC BY "
                                  "or an open government licence (credited below) whose own title or description "
                                  "names a medicine and its strength; captions CC0."),
}
MEDICATION_LIMITS = {
    "commons_medication_labels": 300,     # about 180 medicine names searched; few files state a strength
}
MEDICATION_COMMONS_KEYS = ("commons_medication_labels",)


def main(argv=None):
    """Build the pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the medication label pack builder.")
    parser.add_argument("key", choices=sorted(MEDICATION_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = MEDICATION_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
