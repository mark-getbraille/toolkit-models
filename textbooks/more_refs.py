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
    "home_crafts",          # home repair and pests (EPA, USDA stains); textile craft books in the arts and crafts group (craft:)
    "electronics_books",    # electronics repair and assistive-technology care: Kuphaldt, NEETS, NLS, VA, Wikibooks (elec:)
    "building_books",       # light construction: Army carpentry and masonry, Navy builder, OSHA, Wood Handbook (build:)
    "crafts_books",         # arts and crafts: Wikibooks origami and bookbinding, old pottery, jewellery, glass books (craft:)
    "arts_crafts_index",    # arts and crafts, a top-level section: the guide to every craft book, manual and pack (arts:)
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
    # practical life (the owner's request of 2026-11-22; shared helpers in practical_index.py)
    "driving",              # driving and road rules: state and provincial handbook indexes, MUTCD, CDC, Army TC 21-305-20 (drive:)
    "computer_basics",      # computer and phone basics: LibreOffice guides (CC BY), Library of Congress archiving (pcb:)
    "household",            # cleaning and household management: FDA, EPA Safer Choice, CPSC checklist, old books (house:)
    "knots_outdoor",        # knots and outdoor skills: Forest Service axe and saw manuals, old knot books (knot:)
    "knots_military",       # knots, rope, pack and mountain manuals: Coast Guard, Navy, Army, Marine Corps (kmil:)
    "military_whole",       # whole military manuals: SERE, Ranger Handbook, desert/jungle/mountain, Seabee, BMR (milw:)
    "gov_forms",            # US federal forms with their instructions: IRS, Medicare, VA, passports, OPM (form:)
    "state_laws",           # state statutes and codes, per state, from official bulk downloads (statelaw:)
    "bushcraft",            # bushcraft and woodcraft: old woodcraft classics, NZ DOC outdoor safety, index (bush:)
    "pools_spas",           # pools, spas and hot tubs: CDC, Army TB MED 575, Navy NAVMED P-5010-4 (pool:)
    "motorcycles_rvs",      # motorcycles, RVs and trailers: Army trailer manual, NPS campgrounds, Motor Camping (rvs:)
    # leisure and learning (the owner's request of 2026-11-22)
    "homestead",            # homesteading and small livestock: EPA wells and septic, FDA eggs, old livestock books (homestead:)
    "outdoors",             # outdoor recreation: USCG boating, USFS, NPS, FWS, NOAA fish species, old woodcraft (outdoors:)
    "games_hobbies",        # card and board games, puzzles, D&D SRD 5.1 and Fate SRD, music theory, stamps (games:)
    "sacred_texts",         # sacred and philosophical texts: public-domain translations, Wikipedia intros (sacred:)
    "science_use",          # science you can use: NIST units, USGS, NOAA, NASA (science:)
    "literature",           # literature and culture: novels, poetry, plays, myths, essays, history (lit:)
    "plant_id",             # plant identification: Forest Service wildflowers, NCCIH herbs, invasives, old field guides (plantid:)
    # emergency preparedness and radio communications (the owner's request of 2026-11-22)
    "disaster_ready",       # Ready.gov, NRC, CISA, ASPR and emPOWER, SBA, EPA disasters and smoke, links (ready:)
    "radio_books",          # radio rules, NCVEC question pools, AUXCOMM, military radio manuals, mesh radio docs (radio:)
    # privacy, security and digital safety (the owner's request of 2026-11-22)
    "privacy_books",        # EFF, Tor, Security in a Box, Privacy Guides, OWASP, GnuPG, CISA, NIST, FTC, IC3, NCSC (privacy:)
    "vision_living",        # blind and low-vision living: the index, Orca, NLS, BEP, Access Board, EEOC, RSA, APH (vision:)
    "power_books",          # power and electrical: DOE wind, small wind, hydro and solar, Treasury, IRS, Army generators (power:)
    # money, language learning, travel and civics (the owner's request of 2026-11-22)
    "money_work",           # IRS publications, CFPB home buying, DOL, NLRB, HealthCare.gov, O*NET (mw:)
    "languages",            # FSI and Peace Corps courses, Wikivoyage phrasebooks, Tatoeba sentences, ASL (lang:)
    "travel",               # FAA PackSafe, USA.gov travel pages, national park passes (trip:)
    "civics",               # Constitution, civics test, Ben's Guide, jury service, Supreme Court cases (civ:)
    # people: disability, veterans, education, relationships, immigration (the owner's request of 2026-11-22)
    "disability_life",      # deaf and hard of hearing, autism, mobility, disability rights beyond blindness (dis:)
    "veterans",             # VA benefits booklet, homeless, mental health, crisis line, DOL VETS, discharge (veteran:)
    "education_help",       # apprenticeships, adult education, college planning, study skills, accommodations (edu:)
    "relationships",        # communication, conflict resolution, healthy relationships, cultural etiquette (relate:)
    "immigration",          # USCIS Policy Manual and guides, M-618, EOIR, Canada newcomers (immig:)
    # health and life (the owner's request of 2026-11-22), each in its own group
    "mental_health",        # NIMH topics, CDC, VA PTSD, OWH, Smokefree.gov, NIDA, NCI grief, help lines (mind:)
    "fitness_nutrition",    # Physical Activity and Dietary Guidelines, Move Your Way, CDC, NHLBI, NIDDK, OWH (fit:)
    "sexual_health",        # CDC contraception, STIs, HIV, violence; OPA, OWH, FDA, NIDDK, help lines (sexhealth:)
    "aging_end_of_life",    # ACL long-term care, VA geriatrics, NCI end of life, NIDCD, IRS, VA burial, DOJ (aging:)
    "wilderness_first_aid", # NPS and USFS backcountry safety, NIOSH outdoor hazards, CDC, NOAA SARSAT, TB MEDs (wild:)
    # personal care, toys and world money (the owner's request of 2026-11-22)
    "personal_care",        # FDA cosmetics safety, products and tattoos, with the personal care index (pcare:)
    "toys_books",           # CPSC Which Toy for Which Child and playground handbook (1997), the toys index (toys:)
    "world_money",          # RBA, ECB and Bank of Canada pages for blind people, the world money index (wmoney:)
    # sports, a top-level section (the owner's request of 2026-11-22)
    "sports",               # rules (old public-domain rule books), teams and players (Wikidata), stats (Retrosheet, openfootball) (sport:)
    # Kiwix references, sheet music, newspapers and old-time radio (the owner's request of 2026-11-22)
    "stack_exchange",       # Stack Exchange how-to sites in the Kiwix library, REFERENCE ONLY, never training (se:)
    "a11y_community",       # accessibility communities: GNOME, ArchWiki and KDE accessibility pages, index (a11yc:)
    "sheet_music",          # Mutopia scores (LilyPond and PDF), NLS braille music catalogues, IMSLP links (music:)
    "newspapers",           # Chronicling America: front pages of history and state books around major events (news:)
    "old_radio",            # old-time radio scripts: USDA and wartime government radio, index of links (otr:)
    # small boats (the owner's request of 2026-11-22)
    "small_boats",          # Navigation Rules, boating CFR, Coast Guard and Army boat manuals, NOAA, NWS, old boat books (boat:)
    # home manufacturing and making (the owner's request of 2026-11-22), its own group
    "making_books",         # 3D printing, lasers, CNC, lathes: Klipper, FreeCAD, LinuxCNC, OpenSCAD, FDA, NIST (make:)
    # reference gaps (the owner's request of 2026-11-22), each in its own group
    "geography",            # the CIA World Factbook (last edition, by continent) and a geography index (geo:)
    "pet_care",             # pet care: CDC Healthy Pets, FDA CVM pet food and poisons, old dog and cat books (pet:)
    "genealogy",            # genealogy: NARA guides, Census Bureau family history, CDC vital records offices (gen:)
    "audio_media",          # audio and media: Audacity Manual, OSARA, W3C WAI media guide, LoC AV formats (media:)
    "audio_description",    # describing pictures and video: 47 CFR part 79 (audio description rules), index (describe:)
    "typing_skills",        # typing: old public-domain touch typing courses and a keyboard skills index (typing:)
    "recycling",            # recycling and waste: EPA (personal use), FDA medicine disposal, DEA take-back (recycle:)
    "game_fish",            # game and fish: CDC game diseases, APHIS and USGS CWD, FDA and EPA fish advice (gamefish:)
    "holiday_observances",  # holidays: OPM, CRS histories, Wikipedia observances, UK and Canada holidays (holiday:)
    # foraging and home food preserving (the owner's request of 2026-11-22), each in its own group
    "foraging",             # edible wild plants and foraging: NPS park rules, UK FSA, USDA 1936, FM 21-76 1957, old fungi books (forage:)
    "preserving",           # home food preserving: CDC botulism, UK FSA, old preserving books as history, Kerr 1945 (preserve:)
    # the master guide to the whole library, made from the code at build time (the owner's request of 2026-11-22)
    "library_guide",        # one book: every group, manual, topic, pack, writing source, B: folder (libguide:)
    # court opinions, patents, quotations and proverbs (the owner's request of 2026-11-22)
    "court_opinions",       # Supreme Court opinions by volume and landmark cases by subject, from govinfo (court:)
    "patents",              # famous patents (Wikisource), assistive and household patents (USPTO, sign-up) (pat:)
    "quotations",           # Bartlett, Hoyt, Brewer, proverb and idiom books, Wikiquote from its dump (quote:)
    # photography, its own group (the owner's request of 2026-11-22)
    "photography",          # cameras, darkroom, historic processes: Navy and Army manuals, LoC, NARA, NPS, FADGI, darktable, GIMP, old books (photo:)
    # old public-domain and open books for nine thin life-skills groups (the owner's request of 2026-11-22)
    "oldbooks_life",        # household, instruments, garden, outdoors, science, computer, typing, media, genealogy, etiquette (olife:)
    # history, travel and education (the owner's request of 2026-11-22; shared helpers in govinfo_kit.py)
    "history",              # history by era and region: NARA, LoC, Public Papers, NPS handbooks, CMH, old books (hist:)
    "travel_more",          # travel: Wayback copies of DOT, TSA, CBP, State; govinfo sign-up; old guidebooks (tripmore:)
    "education_more",       # education: ED booklets (ERIC copies), FAFSA form, old education classics (edumore:)
    # official copies for the thin sections, from GovInfo, agency sites and the Internet Archive (2026-11-22)
    "govinfo_fill",         # NHTSA, FEMA, SAMHSA, NIA, CMS, VA, NARA, CDC, CPSC, EPA booklets; Army and Navy manuals (gpo:)
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
    """The module whose key prefix or request word this is, or None. Two modules may share a key prefix (home_crafts
    and crafts_books both use "craft:"): when the first one by prefix does not really have the key (its own_keys),
    another module with the same prefix that has it is chosen."""
    for m in modules():
        c = m.COLLECTION
        if word in c.words:
            return m
        if c.owns(word):
            sharers = [o for o in modules() if o is not m and o.COLLECTION.owns(word)]
            if not sharers or word in c.own_keys():     # own_keys only asked when a prefix is shared
                return m
            return next((o for o in sharers if word in o.COLLECTION.own_keys()), m)
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


def kiwix_labels():
    """The labels these modules give Kiwix files of the toolkit's Kiwix library ({ZIM name: licence words}), such as
    Wikiquote's (quotations.py)."""
    out = {}
    for m in modules():
        out.update(getattr(m, "KIWIX_LABELS", {}))
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
