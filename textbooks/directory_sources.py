"""The repositories of the reference-directory inventory (2026-11-21) built as ZIM books (keys "directory",
"directory-personal" and dir:<name> or dir:<name>:<piece>).

Why: the owner's research of 2026-11-21 listed every open-repository directory in full (OpenDOAR, ROAR, re3data,
the OER World Map, DOAJ, GovInfo, the US federal agencies, data.gov, Wikimedia, the Internet Archive) and marked 63
repositories "include in full" and 80 "personal use only". This module builds the books that are whole books or web
guides; the sources that come in pieces by date (journals, the Federal Register, the Congressional Record, hearings,
Wikinews, Frontiers for Young Minds, the Internet Archive's collections) are in directory_pubs.py, which adds them
to the periodicals builder (keys pub:<source>:<piece>).

What this module builds (each source checked by hand on 2026-11-21; the lines quoted are in LICENCE_LINES):
  US agency web guides, public domain (17 U.S.C. 105), one book each, read page by page from the agency's own site
  (robots.txt obeyed, one request at a time with a pause): the National Eye Institute (English and Spanish), NIDCD,
  NCCIH, the Administration for Community Living, the VA's benefit pages and its Blind Rehabilitation Service, US
  Courts' self-help guides, Energy Saver's remaining articles, Nutrition.gov, the National Agricultural Library's
  topic guides and Military OneSource.
  Children's stories, CC BY 4.0, from Learning Equality's Kolibri Studio public channels (the official offline
  packages): Pratham Books' StoryWeaver and the Global Digital Library, one book per language and reading level,
  with the reading level as the grade level.
  Open textbooks and courses: GALILEO Open Learning Materials (CC BY and CC BY-SA only, read through its OAI-PMH
  feed), Lumen Learning's CC BY courses (Pressbooks' own API), Raspberry Pi Projects (CC BY-SA 4.0), Sickle Cell
  Open Education.
  Reference data: the Encyclopaedia Britannica's 1st to 8th editions from the National Library of Scotland's Data
  Foundry (bulk downloads; public domain, marked old, with the non-US note), and the OEIS (CC BY-SA 4.0, its bulk
  files).

Every book has its licence and notice, "published" (the publisher's own date where it gives one), "version", the key
and fingerprint for the weekly update check (sign()), "originals" (the builder's originals_of, with may_download from
the licence and robots.txt), the grade level where it applies and the non-US practice note where it applies. A site
that shuts out AI companies' readers by name in its robots.txt, or says "ai-train=no", is never read (ai_refused).

Personal-use repositories: PERSONAL lists all 80 with what was done; those that can be read by a program under their
terms are built with Book.personal_use (shown as "personal use only"), the rest are said with the reason. Item 2 (the
Internet Archive's Books for People with Print Disabilities) needs the owner's own qualifying account and is not
built (OWNER_NOTES).

Keys: directory (every open book here and every piece of directory_pubs' default pieces), directory-personal (the
personal-use ones), dir:<name> (one book or every piece of one source), dir:<name>:<piece>. Run from the repository's
folder:
  python3 textbooks/build_textbooks.py dir:nei_eye_health --out build/textbooks --cache build/textbooks-cache
  python3 textbooks/directory_sources.py dir:nei_eye_health --out build/textbooks --limit 5     (a small test)
  python3 textbooks/directory_sources.py --list directory
"""

import argparse
import datetime
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.robotparser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import sources  # noqa: E402

US_GOV, US_GOV_URL = sources.US_GOV, sources.US_GOV_URL
GOVINFO_POLICY, GOVINFO_TEXT = sources.GOVINFO_POLICY, sources.GOVINFO_TEXT
CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
CC_BY_SA_4 = "https://creativecommons.org/licenses/by-sa/4.0/"
TIME_BUDGET = 3.4 * 3600         # seconds one key may take before it stops (a build job's limit is 4 hours)
PERSONAL_RELEASE = "personal-directory"   # the release of the personal-use books (the workflow makes "personal-*")

# ====================================================================== polite reading

# AI companies' readers named in robots.txt files. A site whose robots.txt shuts any of them out, or says
# "ai-train=no" in a Content-Signal line, is not read at all (the owner's rule; see cookbooks.ai_refused, which this
# extends with the user-directed readers such as Claude-User).
AI_AGENTS = ("ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai", "Claude-Web", "GPTBot", "ChatGPT-User",
             "CCBot")
_ai = {}


def ai_refused(url, cache=None):
    """True when the site's robots.txt shuts out an AI company's reader (AI_AGENTS) from url, or says "ai-train=no"
    in a Content-Signal line. A missing robots.txt refuses nothing."""
    parts = urllib.parse.urlsplit(url)
    site = f"{parts.scheme}://{parts.netloc}"
    if site not in _ai:
        try:
            text = B.fetch(site + "/robots.txt", cache)
        except (urllib.error.URLError, OSError):
            text = ""
        if re.search(r"<html\b", text[:2000], re.I):
            text = ""                                  # a web page instead of a robots.txt: no rules
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(text.splitlines())
        signal = bool(re.search(r"^\s*content-signal\s*:.*ai-train\s*=\s*no", text, re.I | re.M))
        named = [a for a in AI_AGENTS if re.search(rf"^\s*user-agent\s*:\s*{re.escape(a)}\s*$", text, re.I | re.M)]
        _ai[site] = (rp, signal, named)
    rp, signal, named = _ai[site]
    return signal or any(not rp.can_fetch(a, url) for a in named)


def readable(url, cache=None):
    """True when the builder may read url: robots.txt allows our reader and no AI-reader block applies."""
    return B.allowed_by_robots(url, cache) and not ai_refused(url, cache)


def month_token(today=None):
    """"2026-11": part of some fingerprints, so a source with no cheap sign of change is rebuilt once a month."""
    return (today or datetime.date.today()).strftime("%Y-%m")


def sha(*parts):
    """A short checksum of some values."""
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]


# ====================================================================== US agency web guides

# Each guide has the fields of sources.GOV_GUIDES (read by build_textbooks.webguide_book) and, for sites whose
# links are not plain <a href> or that have no sitemap, "crawl": [(start address, depth)] with "follow" (a regular
# expression of the hub pages whose links are read too). Pages are found by crawl() and grouped into parts by
# "unit_rules" ([(regular expression, part name)], first match wins). "language": "spa" for a Spanish book.
NEI = "https://www.nei.nih.gov"
NEI_POLICY = NEI + "/web-policies/copyright-policy"
NEI_TEXT = r"information on the National Eye Institute website is in the public domain"
MAIN = (r"<main\b[^>]*>", r"</main>")
DROP = [r"<nav\b.*?</nav>", r"<aside\b.*?</aside>", r"<form\b.*?</form>", r"<button\b.*?</button>"]
US = dict(country="United States", licence=US_GOV, licence_url=US_GOV_URL, licence_page=GOVINFO_POLICY,
          licence_text=GOVINFO_TEXT, page_mark="", start=[], units="", sitemap="", unit_rules=[], content=MAIN,
          drop=DROP)

GUIDES = [
    dict(US, name="nei_eye_health", title="Eye health information (National Eye Institute)",
         subject="Eye health and vision loss", group="health",
         publisher="National Eye Institute (NEI), National Institutes of Health", source=NEI + "/eye-health-information",
         description="The National Eye Institute's eye-health pages, every one: eye conditions and diseases "
                     "(glaucoma, macular degeneration, diabetic retinopathy, cataracts, low vision and many more: "
                     "symptoms, causes, diagnosis, treatment and research), healthy vision, vision rehabilitation, "
                     "clinical trials, and NEI's education and outreach materials.",
         licence_page=NEI_POLICY, licence_text=NEI_TEXT, notice="Courtesy: National Eye Institute, National Institutes "
         "of Health (NEI/NIH). Information, not medical advice: ask an eye doctor about your own eyes.",
         sitemap=NEI + "/sitemap.xml",
         pages=r"^https://www\.nei\.nih\.gov/(eye-health-information|about/education-and-outreach)(/[a-z0-9-]+)+$",
         unit_rules=[(r"/eye-conditions-and-diseases", "Eye conditions and diseases"),
                     (r"/healthy-vision", "Healthy vision"), (r"/vision-rehabilitation", "Vision rehabilitation"),
                     (r"/clinical-trials", "Clinical trials"), (r"/education-and-outreach", "Education and outreach"),
                     (r".", "More eye-health information")],
         drop=DROP + [r'<a[^>]*class="[^"]*print[^"]*"[^>]*>.*?</a>'], limit=700),
    dict(US, name="nei_eye_health_spanish", title="Información sobre la salud ocular (National Eye Institute, en "
         "español)", subject="Eye health and vision loss (Spanish)", group="health", language="spa",
         publisher="National Eye Institute (NEI), National Institutes of Health",
         source=NEI + "/espanol/informacion-sobre-la-salud-ocular",
         description="The National Eye Institute's eye-health pages in Spanish: eye conditions and diseases, healthy "
                     "vision and vision rehabilitation, every page.",
         licence_page=NEI_POLICY, licence_text=NEI_TEXT, notice="Courtesy: National Eye Institute, National Institutes "
         "of Health (NEI/NIH). Información, no consejo médico: consulte a un oculista.",
         sitemap=NEI + "/sitemap.xml",
         pages=r"^https://www\.nei\.nih\.gov/espanol/informacion-sobre-la-salud-ocular(/[a-z0-9-]+)+$",
         unit_rules=[(r"/enfermedades|/afecciones", "Enfermedades y afecciones de los ojos"),
                     (r".", "Más información")], limit=200),
    dict(US, name="nidcd_health", title="Hearing, balance, smell, taste, voice, speech and language (NIDCD)",
         subject="Hearing, deafblindness and communication", group="health",
         publisher="National Institute on Deafness and Other Communication Disorders (NIDCD), National Institutes of "
                   "Health", source="https://www.nidcd.nih.gov/health",
         description="NIDCD's health information, every page: hearing loss and hearing aids, cochlear implants, "
                     "tinnitus, Usher syndrome (deafblindness), balance disorders, smell and taste, voice, speech and "
                     "language, assistive devices, and NIDCD's health statistics.",
         notice="Information, not medical advice: ask a doctor or audiologist.",
         sitemap="https://www.nidcd.nih.gov/sitemap.xml",
         pages=r"^https?://(www\.)?nidcd\.nih\.gov/health/[a-z0-9-]+(/[a-z0-9-]+)*$",
         rewrite=(r"^https?://(www\.)?nidcd\.nih\.gov/", "https://www.nidcd.nih.gov/"),
         unit_rules=[(r"/statistics", "Health statistics"),
                     (r"hearing|deaf|cochlear|tinnitus|usher|ear-|otosclerosis|auditory|meniere|vestibular|pendred|"
                      r"captions|telecomm|sign-language|listen", "Hearing and deafness"),
                     (r"balance|dizz", "Balance"), (r"smell|taste", "Smell and taste"),
                     (r"voice|speech|language|stutter|apraxia|dysphonia|vocal|hoarse|papilloma|autism", "Voice, speech "
                      "and language"), (r".", "More")], limit=300),
    dict(US, name="nccih_health", title="Complementary and integrative health: herbs, supplements and practices "
         "(NCCIH)", subject="Dietary supplements and complementary health", group="health",
         publisher="National Center for Complementary and Integrative Health (NCCIH), National Institutes of Health",
         source="https://www.nccih.nih.gov/health/atoz",
         description="NCCIH's health information A to Z, every page: herbs at a glance, dietary supplements, mind "
                     "and body practices (acupuncture, yoga, meditation, massage), what the science says about them "
                     "for pain, anxiety, sleep and other conditions, and their safety and interactions.",
         notice="Information, not medical advice: tell your doctor and pharmacist about any supplement you take.",
         content=(r"(?=<h1\b)", r"<footer\b"), drop=DROP + [r"<!-- slice-start id=\"nccih-right-menu.*?<!-- slice-end"],
         crawl=[("https://www.nccih.nih.gov/health/atoz", 1), ("https://www.nccih.nih.gov/health/herbsataglance", 1),
                ("https://www.nccih.nih.gov/health/providers", 1)],
         follow=r"^https://www\.nccih\.nih\.gov/health/(atoz|herbsataglance|providers)$",
         pages=r"^https://www\.nccih\.nih\.gov/health/(?!atoz$|espanol|providers$)[a-z0-9-]+(/[a-z0-9-]+)?$",
         unit_rules=[(r"/providers/", "For health professionals"), (r".", "Health topics A to Z")], limit=700),
    dict(US, name="acl_programs", title="Community living for older adults and people with disabilities (ACL)",
         subject="Independent living, ageing and disability services", group="disability",
         publisher="Administration for Community Living (ACL), US Department of Health and Human Services",
         source="https://acl.gov/programs",
         description="The Administration for Community Living's programme pages, every one: centers for "
                     "independent living, area agencies on aging, aging and disability resource centers, assistive "
                     "technology, caregiver support, elder justice and long-term care ombudsmen, protection and "
                     "advocacy, nutrition, falls prevention, transportation, employment and disability research.",
         content=(r'<div class="region region-content">', r'<section\s+class="sidebar-right"|<footer\b'),
         crawl=[("https://acl.gov/programs", 2)],
         follow=r"^https://acl\.gov/programs/[A-Za-z0-9-]+$",
         pages=r"^https://acl\.gov/(programs/[A-Za-z0-9/_-]+|brain-health)$",
         unit_rules=[(r"aging-and-disability-networks", "Aging and disability networks"),
                     (r"caregiv", "Caregivers"), (r"connecting-people|consumer-control|transportation|veteran",
                                                  "Connecting people to services"),
                     (r"health-wellness|brain-health|opioid", "Health and wellness"),
                     (r"protecting-rights|elder-justice|advocacy|guardianship", "Rights and protection from abuse"),
                     (r"research-and-development|evaluations", "Research"), (r"post-injury", "After an injury"),
                     (r".", "More programmes")], limit=400),
    dict(US, name="va_benefits", title="VA benefits and health care: the guides (US Department of Veterans Affairs)",
         subject="Veterans' benefits and health care", group="consumer",
         publisher="US Department of Veterans Affairs (VA.gov)", source="https://www.va.gov/",
         description="VA.gov's benefit guides, every page: health care (eligibility, how to apply, copays, mental "
                     "health, health needs and conditions), disability compensation, education and training, careers "
                     "and employment (Veteran Readiness and Employment), pension, housing assistance, life insurance, "
                     "burials and memorials, family and caregiver benefits, records, and VA's resources and support "
                     "articles. Online forms and sign-in tools are left out.",
         crawl=[(f"https://www.va.gov/{hub}/", 2) for hub in
                ("health-care", "disability", "education", "careers-employment", "pension", "housing-assistance",
                 "life-insurance", "burials-memorials", "family-and-caregiver-benefits", "records", "resources")],
         follow=r"^https://www\.va\.gov/(health-care|disability|education|careers-employment|pension|"
                r"housing-assistance|life-insurance|burials-memorials|family-and-caregiver-benefits|records|"
                r"resources)/([a-z0-9-]+/)?$",
         pages=r"^https://www\.va\.gov/(health-care|disability|education|careers-employment|pension|"
               r"housing-assistance|life-insurance|burials-memorials|family-and-caregiver-benefits|records|resources)"
               r"/(?![a-z0-9/-]*(?:introduction|form-|-form|apply-for|application|status|sign-in|/start|confirmation"
               r"|eligibility-check|calculator|tool|schedule))[a-z0-9/-]*$",
         unit_rules=[(r"/health-care/", "Health care"), (r"/disability/", "Disability compensation"),
                     (r"/education/", "Education and training"), (r"/careers-employment/", "Careers and employment"),
                     (r"/pension/", "Pension"), (r"/housing-assistance/", "Housing assistance"),
                     (r"/life-insurance/", "Life insurance"), (r"/burials-memorials/", "Burials and memorials"),
                     (r"/family-and-caregiver-benefits/", "Family and caregiver benefits"), (r"/records/", "Records"),
                     (r".", "Resources and support")], limit=900),
    dict(US, name="va_blind_rehabilitation", title="Blind and Visual Impairment Rehabilitation Services (VA)",
         subject="Blind rehabilitation for veterans", group="disability",
         publisher="US Department of Veterans Affairs, Veterans Health Administration (Rehabilitation and Prosthetic "
                   "Services)", source="https://www.prosthetics.va.gov/blindrehab/",
         description="The VA's Blind Rehabilitation Service: its blind rehabilitation centers, outpatient and "
                     "low-vision clinics, Visual Impairment Services Team (VIST) coordinators, what is taught "
                     "(orientation and mobility, living skills, manual skills, visual skills, assistive technology) "
                     "and how veterans and service members can take part.",
         crawl=[("https://www.prosthetics.va.gov/blindrehab/", 2)],
         follow=r"^https://www\.prosthetics\.va\.gov/PROSTHETICS/blindrehab/[A-Za-z0-9_-]+\.asp$",
         pages=r"^https://www\.prosthetics\.va\.gov/PROSTHETICS/blindrehab/[A-Za-z0-9_-]+\.asp$",
         content=(r'<div id="tier4innerContent">', r'<div id="footer|<footer\b|<!-- \*+ START FOOTER'),
         title_from=r'<div id="tier4innerContent">.*?<h1[^>]*>(.*?)</h1>', limit=120),
    dict(US, name="uscourts_self_help", title="US federal courts: jury service, bankruptcy basics and filing without "
         "a lawyer", subject="The courts and legal self-help", group="law",
         publisher="Administrative Office of the US Courts (uscourts.gov)", source="https://www.uscourts.gov/",
         description="The federal judiciary's own guides for the public: how the courts work and the types of cases "
                     "(civil, criminal, bankruptcy, appeals), jury service (being summoned, qualifications and "
                     "excuses, juror pay, scams), Bankruptcy Basics (each chapter, the process, the discharge, the "
                     "glossary), filing a bankruptcy case without an attorney, filing a case, and the glossary of "
                     "legal terms.",
         urls=[("https://www.uscourts.gov/about-federal-courts/court-role-and-structure", "How the courts work"),
               ("https://www.uscourts.gov/about-federal-courts/types-cases", "Types of cases"),
               ("https://www.uscourts.gov/faqs-filing-a-case", "Filing a case"),
               ("https://www.uscourts.gov/court-programs/bankruptcy/filing-without-attorney", "Bankruptcy"),
               ("https://www.uscourts.gov/glossary", "Glossary")],
         crawl=[("https://www.uscourts.gov/court-programs/jury-service", 2),
                ("https://www.uscourts.gov/court-programs/bankruptcy/bankruptcy-basics", 1),
                ("https://www.uscourts.gov/about-federal-courts/types-cases", 1),
                ("https://www.uscourts.gov/about-federal-courts/court-role-and-structure", 1)],
         follow=r"^https://www\.uscourts\.gov/court-programs/jury-service(/[a-z0-9-]+)?$",
         pages=r"^https://www\.uscourts\.gov/(court-programs/jury-service(/[a-z0-9-]+)*|court-programs/bankruptcy/"
               r"bankruptcy-basics(/[a-z0-9-]+)?|about-federal-courts/types-cases(/[a-z0-9-]+)?|about-federal-courts/"
               r"court-role-and-structure(/(?!court-website-links)[a-z0-9-]+)?)$",
         unit_rules=[(r"/jury-service", "Jury service"), (r"/bankruptcy", "Bankruptcy"),
                     (r"/types-cases", "Types of cases"), (r"/court-role-and-structure", "How the courts work"),
                     (r".", "More")], limit=120),
    dict(US, name="energy_saver_articles", title="Energy Saver articles (US Department of Energy)",
         subject="Home energy: heating, cooling, water heating and saving energy", group="consumer",
         publisher="US Department of Energy, Office of Energy Efficiency and Renewable Energy (Energy Saver)",
         source="https://www.energy.gov/energysaver",
         description="The Energy Saver articles still on energy.gov: heat pumps, water heaters, standby power, "
                     "keeping pipes from freezing, fireplaces, buying an efficient home, lighting, solar at home, "
                     "and the Energy 101 explainers (their videos' descriptions as text).",
         sitemap="https://www.energy.gov/sitemap.xml",
         pages=r"^https://www\.energy\.gov/energysaver/(articles/)?[a-z0-9-]+$",
         unit_rules=[(r"energy-101", "Energy 101 explainers"), (r".", "Articles")], limit=200),
    dict(US, name="nutrition_gov", title="Nutrition.gov: food and nutrition information (USDA)",
         subject="Food and nutrition", group="health",
         publisher="US Department of Agriculture, National Agricultural Library (Nutrition.gov)",
         source="https://www.nutrition.gov/",
         description="Every page of Nutrition.gov: basic nutrition, nutrition through life's stages, diet and health "
                     "conditions, what's in food, shopping, cooking and meal planning, food security, food safety, "
                     "dietary supplements, healthy weight and exercise, expert answers, and its recipes.",
         sitemap="https://www.nutrition.gov/sitemap.xml",
         pages=r"^https?://www\.nutrition\.gov/(topics|recipes|expert-q-a|child-nutrition-programs)(/[a-z0-9-]+)*$",
         rewrite=(r"^http://", "https://"),
         unit_rules=[(r"/recipes", "Recipes"), (r"/expert-q-a", "Expert answers"),
                     (r"/topics/basic-nutrition", "Basic nutrition"), (r"/topics/nutrition-life-stage", "Life stages"),
                     (r"/topics/diet-and-health-conditions", "Diet and health conditions"),
                     (r"/topics/whats-food", "What's in food"), (r"/topics/shopping-cooking", "Shopping, cooking and "
                                                                                       "meal planning"),
                     (r"/topics/food-security", "Food security and access"), (r"/topics/food-safety", "Food safety"),
                     (r"/topics/dietary-supplements", "Dietary supplements"),
                     (r"/topics/(healthy-living|exercise)", "Healthy weight and exercise"), (r".", "More")],
         notice="Information, not medical advice.", limit=400),
    dict(US, name="nal_topic_guides", title="National Agricultural Library topic guides (USDA)",
         subject="Food safety, gardening, animal welfare and farming", group="science",
         publisher="US Department of Agriculture, National Agricultural Library (NAL)",
         source="https://www.nal.usda.gov/",
         description="The National Agricultural Library's topic guides: human nutrition and food safety, animal "
                     "health and welfare (pets and farm animals), farms and agricultural production, plant production "
                     "and gardening, natural resources and the environment, rural development and agricultural "
                     "economics, with their lists of trusted resources.",
         sitemap="https://www.nal.usda.gov/sitemap.xml",
         pages=r"^https://www\.nal\.usda\.gov/(human-nutrition-and-food-safety|animal-health-and-welfare|"
               r"farms-and-agricultural-production-systems|plant-production-gardening|"
               r"natural-resources-conservation-environment|rural-development-communities|"
               r"economics-business-and-trade)(/[a-z0-9-]+)*$",
         unit_rules=[(r"human-nutrition", "Human nutrition and food safety"),
                     (r"animal-health", "Animal health and welfare"), (r"farms-", "Farms and agriculture"),
                     (r"plant-production", "Plants and gardening"), (r"natural-resources", "Natural resources"),
                     (r"rural-development", "Rural development"), (r".", "Economics, business and trade")],
         limit=200),
    dict(US, name="military_onesource", title="Military OneSource: guides for service members and their families "
         "(US Department of Defense)", subject="Military families: money, moving, caregiving, benefits",
         group="consumer", publisher="US Department of Defense, Military Community and Family Policy (Military "
                                     "OneSource)", source="https://www.militaryonesource.mil/",
         description="Military OneSource's articles, every one: military basics, moving (PCS), deployment, financial "
                     "and legal help, education and employment, health and wellness, relationships and parenting, "
                     "special needs (the Exceptional Family Member Program), casualty assistance and funerals, "
                     "National Guard and Reserve, recreation, transition and retirement, emergencies, and benefits.",
         sitemap="https://www.militaryonesource.mil/sitemap_index.xml",
         pages=r"^https://www\.militaryonesource\.mil/(military-basics|moving-pcs|deployment|financial-legal|"
               r"education-employment|health-wellness|relationships|parenting|special-needs|casualty-mortuary-affairs|"
               r"military-funeral-honors|national-guard-reserves|recreation-travel-shopping|transition-retirement|"
               r"emergencies-disasters|benefits|branch-of-service|leaders-service-providers)/[a-z0-9/-]+$",
         unit_rules=[(r"/benefits/", "Benefits"), (r"/military-basics/", "Military basics"),
                     (r"/moving-pcs/", "Moving (PCS)"), (r"/deployment/", "Deployment"),
                     (r"/financial-legal/", "Financial and legal"), (r"/education-employment/", "Education and "
                                                                                                 "employment"),
                     (r"/health-wellness/", "Health and wellness"), (r"/relationships/", "Relationships"),
                     (r"/parenting/", "Parenting"), (r"/special-needs/", "Special needs"),
                     (r"/(casualty|military-funeral)", "Casualty assistance and funerals"),
                     (r"/national-guard", "National Guard and Reserve"), (r"/recreation", "Recreation, travel and "
                                                                                          "shopping"),
                     (r"/transition", "Transition and retirement"), (r"/emergencies", "Emergencies and disasters"),
                     (r".", "For leaders and service providers")], limit=1200),
]
GUIDES_BY_NAME = {g["name"]: g for g in GUIDES}

HREF = re.compile(r'\bhref\s*=\s*"([^"]+)"|\bhref\s*=\s*\'([^\']+)\'', re.I)


def any_links(text, base):
    """Every address a page links to, from any element's href (plain <a> links, and the web components some sites
    use, such as VA.gov's <va-link href=...>), without "#..." parts and repeats, in order."""
    out = []
    for m in HREF.finditer(text):
        url = urllib.parse.urljoin(base, html.unescape(m.group(1) or m.group(2))).split("#")[0]
        if url.startswith("http") and url not in out:
            out.append(url)
    return out


def unit_of(url, rules):
    """The part a page belongs to: the name of the first rule whose regular expression finds the address."""
    return next((unit for pattern, unit in rules or [] if re.search(pattern, url)), "")


def crawl(entry, cache=None, limit=None):
    """[(address, part)] of a guide's pages, in reading order: the fixed entry["urls"], then the pages found from
    each crawl start (its own address too) following the hub pages entry["follow"] up to the start's depth; only
    addresses matching entry["pages"] are kept, robots.txt is asked for each page read, and at most entry["limit"]."""
    pages, follow = re.compile(entry["pages"]), re.compile(entry.get("follow") or r"$^")
    rules = entry.get("unit_rules") or []
    found, seen = [], set()

    def keep(url, unit=""):
        if url not in seen and pages.match(url):
            seen.add(url)
            found.append((url, unit or unit_of(url, rules)))
    for url in entry.get("urls", []):
        keep(*url) if isinstance(url, tuple) else keep(url)
    for start, depth in entry.get("crawl", []):
        frontier, visited = [start], set()
        keep(start)
        for _level in range(depth):
            nxt = []
            for hub in frontier:
                if hub in visited or not readable(hub, cache):
                    continue
                visited.add(hub)
                try:
                    text = B.fetch(hub, cache)
                except (urllib.error.URLError, OSError):
                    continue
                for url in any_links(text, hub):
                    url = url.rstrip("/") + "/" if hub.endswith("/") and not re.search(r"\.\w+$", url) and \
                        url.startswith(start) else url
                    keep(url)
                    if follow.match(url) and url not in visited:
                        nxt.append(url)
            frontier = nxt
    return found[:limit or entry.get("limit", 500)]


def guide_book(entry, cache=None, left_out=None, limit=None):
    """The Book of one agency guide (GUIDES), or None (the reason in left_out): the site's robots.txt and its AI
    rules are checked first, the pages are found from its sitemap (build_textbooks.webguide_plan) or by crawl(), then
    read by build_textbooks.webguide_book (which checks the licence line on the licence page at every build).
    limit: read only so many pages (a small test build)."""
    left_out = left_out if left_out is not None else []
    if ai_refused(entry["source"], cache):
        left_out.append({"title": entry["title"], "reason": "The site's robots.txt shuts out AI companies' readers or "
                         "says ai-train=no; it is not read."})
        return None
    spec = dict(entry)
    if limit:
        spec["limit"] = limit
    if entry.get("crawl"):
        spec["urls"], spec["sitemap"], spec["start"] = crawl(spec, cache, limit), "", []
    elif entry.get("rewrite"):                   # a sitemap that lists old forms of the addresses (http, no www)
        pattern, replacement = entry["rewrite"]
        plan = B.webguide_plan(spec, cache)
        spec["urls"] = list(dict.fromkeys((re.sub(pattern, replacement, u), unit) for u, unit in plan))
        spec["sitemap"], spec["start"] = "", []
    book = B.webguide_book(spec, cache, left_out)
    if book is None:
        return None
    book.language = entry.get("language", "eng")
    book.version = f"pages read {datetime.date.today().isoformat()}"
    return book


def guide_sign(entry):
    """A guide's weekly sign of change: the list of its pages (an added, removed or renamed page changes it) with the
    sitemap's dates where it gives them, and the month, so every guide is read again at least once a month."""
    import updates                               # here, not at the top: updates imports the builder
    if entry.get("crawl"):
        return sha([u for u, _unit in crawl(entry, None)], month_token())
    return sha(updates.guide_sign(entry), month_token())


# ====================================================================== keys, signs, the build

def all_keys(personal=False):
    """Every build key of this module's own books (personal=True: the personal-use ones)."""
    if personal:
        return [f"dir:{name}" for name in PERSONAL_BOOKS]
    return [f"dir:{g['name']}" for g in GUIDES] + [k for name in PIECED for k in PIECED[name]["keys"]()]


def expand_keys(words):
    """The keys the words stand for: "directory" (every open book of this module, and directory_pubs' sources with
    their default pieces), "directory-personal" (the personal-use books and pieces), dir:<name> (one book, or every
    piece of a source in pieces), dir:<name>:<piece>."""
    keys = []
    for w in words:
        if w == "directory":
            import directory_pubs                # here, not at the top: it imports the periodicals builder
            keys += all_keys() + directory_pubs.default_keys()
        elif w == "directory-personal":
            import directory_pubs
            keys += all_keys(True) + directory_pubs.default_keys(personal=True)
        elif w.startswith("dir:") and w.count(":") == 1 and w[4:] in PIECED:
            keys += PIECED[w[4:]]["keys"]()
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change of one key ("" when it cannot be asked: then nothing is rebuilt)."""
    parts = key.split(":")
    name = parts[1] if len(parts) > 1 else ""
    try:
        if name in GUIDES_BY_NAME:
            return guide_sign(GUIDES_BY_NAME[name])
        if name in PIECED:
            return PIECED[name]["sign"](parts[2] if len(parts) > 2 else "")
        if name in PERSONAL_BOOKS:
            return PERSONAL_BOOKS[name]["sign"](key)
    except (urllib.error.URLError, OSError, ValueError, KeyError, LookupError):
        return ""
    return ""


def books_for(key, work, cache=None, left_out=None, limit=None):
    """[Book] of one key (several for a piece of a source in pieces)."""
    parts = key.split(":")
    name, piece = parts[1], (parts[2] if len(parts) > 2 else "")
    if name in GUIDES_BY_NAME:
        book = guide_book(GUIDES_BY_NAME[name], cache, left_out, limit)
        return [book] if book is not None else []
    if name in PIECED:
        return PIECED[name]["books"](piece, work, cache, left_out, limit)
    if name in PERSONAL_BOOKS:
        return PERSONAL_BOOKS[name]["books"](piece, work, cache, left_out, limit)
    left_out.append({"title": key, "reason": "Unknown key."})
    return []


def release_of(key, book):
    """The release a book goes to: "textbooks", or PERSONAL_RELEASE for a personal-use book."""
    return PERSONAL_RELEASE if book.personal_use else "textbooks"


def build_directory(keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys into out_dir and write manifest-<key>.json for each (as build_textbooks.build does);
    returns {key: manifest}. Every book is a new version (versioned file names). limit: a small test build (only so
    many pages or items; manifests named "..._sample")."""
    manifests = {}
    work = os.path.join(cache or out_dir, "work")
    os.makedirs(out_dir, exist_ok=True)
    for key in expand_keys(keys):
        if not key.startswith("dir:"):
            print(f"Not a key of this module: {key}; skipped.")
            continue
        left_out, entries, release = [], [], "textbooks"
        fingerprint = "" if limit else sign(key)
        try:
            books = books_for(key, work, cache, left_out, limit)
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            books = []
        for book in books:
            if not book.pages:
                left_out.append({"title": book.title, "reason": "No pages could be read."})
                continue
            release = release_of(key, book)
            entry = B.write_book(book, out_dir, date, versioned=True)
            entry.update({"key": key, "fingerprint": fingerprint, "release": release})
            if release != "textbooks":
                entry["url"] = f"{B.RELEASE.rsplit('/', 1)[0]}/{release}/{entry['file']}"
            print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, {entry['licence_text']}")
            entries.append(entry)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": release, "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if limit else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


# Sources of this module that come in pieces or as several books: name -> {keys(), books(piece, work, cache,
# left_out, limit), sign(piece)}; filled in below, source by source.
PIECED = {}
# The personal-use books of this module: name -> the same fields.
PERSONAL_BOOKS = {}


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "nei": "www.nei.nih.gov/web-policies/copyright-policy (read 2026-11-21, checked again at every build): \"Unless "
           "otherwise noted, information on the National Eye Institute website is in the public domain. Public domain "
           "information may be freely distributed and copied, but, as a courtesy, we request that the National Eye "
           "Institute be given an appropriate acknowledgement\". robots.txt: \"User-agent: *\" with only Drupal's "
           "system folders disallowed.",
    "us_agency_guides": "NIDCD, NCCIH, ACL, VA.gov and the VA's prosthetics site, uscourts.gov, energy.gov, "
                        "Nutrition.gov, nal.usda.gov and militaryonesource.mil: works of the US government (17 U.S.C. "
                        "105); the line checked at every build is govinfo.gov's quotation of 17 U.S.C. 105, as for "
                        "the FAA and IRS books. Each site's robots.txt allows the pages read (checked 2026-11-21 and "
                        "at every build); none names an AI company's reader or says ai-train=no. VA.gov's robots.txt "
                        "disallows its sitemap, so its pages are found from its benefit hubs' links.",
}

GROUP_NOTES = {}

NOT_INCLUDED = [
    ("AHRQ patient and consumer guides (www.ahrq.gov)", "Public domain, but its robots.txt shuts out AI companies' "
     "readers by name (anthropic-ai, Claude-Web, GPTBot, CCBot: \"Disallow: /\"), so by the owner's rule it is not "
     "read at all (checked 2026-11-21)."),
    ("CareerOneStop (www.careeronestop.org, US Department of Labor)", "Its robots.txt (Cloudflare's managed list) "
     "says \"User-agent: Claude-User Disallow: /\" and shuts out the other AI assistants' readers, so it is not read "
     "and its terms page was not opened (checked 2026-11-21). Its Content-Signal says ai-train=yes, but the named "
     "block wins."),
    ("Investor.gov (SEC investor education)", "The site answers every program, robots.txt included, with \"Access "
     "Denied\" (403, Akamai), checked 2026-11-21."),
    ("StudentAid.gov", "The site closes the connection without answering programs (robots.txt included), checked "
     "2026-11-21."),
    ("HUD guides (www.hud.gov: renting, fair housing, buying a home)", "Its pages give programs only an empty frame "
     "(the page's own text is not in what the server sends: \"Rental Assistance\" holds 780 characters of menus), and "
     "it has no sitemap (404) or API; checked 2026-11-21. Fair housing law is in the library as the Fair Housing Act "
     "and 24 CFR part 100 (law: keys)."),
    ("Energy Saver's home guides (heating and cooling, insulation, appliances)", "Removed from energy.gov in its "
     "redesign: its sitemap (99,494 addresses, read 2026-11-21) keeps only 39 Energy Saver articles, which are built "
     "(dir:energy_saver_articles)."),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["directory"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many pages or items")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build_directory(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
