"""The list of reference-source modules added on 2026-11-22, so the shared files need only one small hook each:
sources.py (expand_keys and its records at the end), build_textbooks.build (sends their keys here) and
updates.fingerprint (the weekly check asks sign() here).

Each module named in MODULES has: COLLECTION (a refs_kit.Collection: its keys, signs and build), GROUPS,
LICENCE_LINES and NOT_INCLUDED (what was checked and what was not built, with the reason and the index address), and
optionally daily_keys() (keys rebuilt by the daily refresh, such as this month's FDA recalls).

To add a source: write its module with those names and add it to MODULES.
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The modules, in the order of the owner's requests (2026-11-22).
MODULES = [
    "food_data",            # USDA FoodData Central (fdc:)
    "fda_recalls",          # FDA food, drug and device recalls and drug shortages (fda:)
    "medlineplus_topics",   # MedlinePlus health topics (mlp:)
    "at_docs",              # NVDA, NVDA add-ons, liblouis, Department of Education AT guides (atdoc:)
    "law_codes",            # the US Code in full and open state codes (code:)
    "legal_help",           # plain-language legal help guides (legal:)
    "emergency_prep",       # NWS weather safety, NOAA Weather Radio, FEMA publications (prep:)
    "money_help",           # CFPB, FDIC, FTC consumer guides (money:)
    "transport_rights",     # DOT aviation consumer guides, FTA, Access Board (travel:)
    "gov_help",             # digital.gov, USA.gov, Benefits.gov, Medicare, SSA (help:)
    "work_disability",      # JAN, ADA National Network, ODEP, Ticket to Work, AbleData (work:)
    "civic_help",           # voting (EAC, Vote.gov) and housing (HUD) (civic:)
    "family_health",        # parenting, aging and caregiving, mental health, crisis lines (fam:)
    "pets_home",            # pets (APHIS) and home health (EPA, personal use) (home:)
    "home_tests",           # at-home medical tests: FDA guides, test lists and device records (hometest:)
    "parenting",            # parenting and family: CDC, Child Welfare Information Gateway, CPIR, CPSC ... (parent:)
    "early_childhood",      # child care, pregnancy, newborns and infant feeding: ChildCare.gov, OWH, CDC, WIC, NHS (early:)
    "read_aloud",           # picture books (Book Dash, African Storybook) and old nursery rhymes (readaloud:)
    "home_crafts",          # home repair, pest control and textile crafts: EPA, USDA stains, old craft books (craft:)
    "electronics_books",    # electronics repair and assistive-technology care: Kuphaldt, NEETS, NLS, VA, Wikibooks (elec:)
    "building_books",       # light construction: Army carpentry and masonry, Navy builder, OSHA, Wood Handbook (build:)
    "crafts_books",         # arts and crafts: Wikibooks origami and bookbinding, old pottery, jewellery, glass books (craft:)
    # life skills (the owner's request of 2026-11-22)
    "car_care",             # old public-domain car care books (car:)
    "gardening",            # USDA hardiness zones, NRCS soil health, lawn weeds, old gardening books (garden:)
    "first_aid",            # emergency and wilderness first aid: CDC, NHS, ST 31-91B, emergency childbirth (firstaid:)
    "home_health",          # home treatment, long-term conditions, caregiving: NHS, CDC, NIDDK, NHLBI, VA (homecare:)
    "dental_care",          # NIDCR, CDC oral health, NHS dental pages, Oral Health in America (dental:)
    "eye_care",             # NEI, CDC vision health, FDA contact lenses, NHS eyes, VA blind rehabilitation (eyes:)
    "eyecare_products",     # eye medicines by use (DailyMed) and eye care device records (openFDA) (eyeprod:)
    "midwifery",            # CDC Hear Her, maternal and infant health, NHS after-birth pages (birth:)
    "instrument_care",      # old public-domain piano tuning and violin making books (instr:)
    "outdoor_cooking",      # emergency, camp and outdoor cooking: CDC, Ready.gov, USFA, CPSC, USFS, NPS, EPA, Army (outcook:)
    # emergency preparedness and radio communications (the owner's request of 2026-11-22)
    "disaster_ready",       # Ready.gov, NRC, CISA, ASPR and emPOWER, SBA, EPA disasters and smoke, links (ready:)
    "radio_books",          # radio rules, NCVEC question pools, AUXCOMM, military radio manuals, mesh radio docs (radio:)
    # money, language learning, travel and civics (the owner's request of 2026-11-22)
    "money_work",           # IRS publications, CFPB home buying, DOL, NLRB, HealthCare.gov, O*NET (mw:)
    "languages",            # FSI and Peace Corps courses, Wikivoyage phrasebooks, Tatoeba sentences, ASL (lang:)
    "travel",               # FAA PackSafe, USA.gov travel pages, national park passes (trip:)
    "civics",               # Constitution, civics test, Ben's Guide, jury service, Supreme Court cases (civ:)
]

_loaded = {}


def modules():
    """The modules that exist (a module not yet written is skipped), imported once."""
    out = []
    for name in MODULES:
        if name not in _loaded:
            try:
                _loaded[name] = importlib.import_module(name)
            except ModuleNotFoundError as e:
                if e.name != name:
                    raise
                _loaded[name] = None
        if _loaded[name] is not None:
            out.append(_loaded[name])
    return out


def module_for(word):
    """The module whose key prefix or request word this is, or None."""
    for m in modules():
        c = m.COLLECTION
        if c.owns(word) or word in c.words:
            return m
    return None


def expand_keys(word):
    """The keys of one request word, or None when no module here knows it."""
    m = module_for(word)
    return m.COLLECTION.expand_keys([word]) if m else None


def owns(key):
    """True when a module here builds this key."""
    return any(m.COLLECTION.owns(key) for m in modules())


def build(keys, out_dir, cache=None, date=None):
    """Build keys with their modules; returns {key: manifest}."""
    manifests = {}
    for key in keys:
        m = module_for(key)
        if m:
            manifests.update(m.COLLECTION.build([key], out_dir, cache, date))
    return manifests


def sign(key):
    """The weekly sign of change of one key ("" when none of these modules knows it)."""
    m = module_for(key)
    return m.COLLECTION.sign(key) if m else ""


def daily_keys():
    """The keys the daily refresh rebuilds (this month's recalls and the drug shortages list)."""
    keys = []
    for m in modules():
        if hasattr(m, "daily_keys"):
            keys += m.daily_keys()
    return keys


def allowed():
    """The licences these modules add to sources.ALLOWED ({short name: kind}), such as the GNU licences of the NVDA
    and liblouis documentation (share-alike)."""
    out = {}
    for m in modules():
        out.update(getattr(m, "ALLOWED", {}))
    return out


def no_changes():
    """The no-changes licences these modules add to sources.NO_CHANGES ({short name: kind}): a permission to copy
    and distribute freely that says nothing of changes, so the work is kept whole with its text unchanged."""
    out = {}
    for m in modules():
        out.update(getattr(m, "NO_CHANGES", {}))
    return out


def records():
    """(GROUPS, LICENCE_LINES, NOT_INCLUDED, PRACTICE_SUBJECTS) of every module, for sources.py."""
    groups, lines, rows, practice = {}, {}, [], []
    for m in modules():
        groups.update(getattr(m, "GROUPS", {}))
        lines.update(getattr(m, "LICENCE_LINES", {}))
        rows += list(getattr(m, "NOT_INCLUDED", []))
        practice += list(getattr(m, "PRACTICE_SUBJECTS", []))
    return groups, lines, rows, practice
