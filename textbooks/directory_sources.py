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
  Open courses: Lumen Learning's CC BY and CC BY-SA courses (Pressbooks' own API) and Raspberry Pi Projects (CC
  BY-SA 4.0, each project's steps from the Foundation's public repositories, found from its sitemap). Personal use
  only: Open Yale Courses (CC BY-NC-SA 3.0, each lecture's transcript).
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
personal-use ones), dir:<name> (one book or every piece of one source), dir:<name>:<piece>, and
directory-all:<source>[:<n>] (every piece of one source back to its beginning, or its n-th block of 200, so one
request stays within a workflow run's 256 jobs). Run from the repository's folder:
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
        return [k for src in PERSONAL_BOOKS.values() for k in src["keys"]()]
    return [f"dir:{g['name']}" for g in GUIDES] + \
        [k for name, src in PIECED.items() for k in (src["default"]() if "default" in src else src["keys"]())]


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
        elif w.startswith("directory-all:"):
            keys += all_pieces(*w.split(":")[1:3])
        elif w.startswith("dir:") and w.count(":") == 1 and w[4:] in PIECED:
            keys += PIECED[w[4:]]["keys"]()
        elif w.startswith("dir:") and w.count(":") == 1 and w[4:] in PERSONAL_BOOKS:
            keys += PERSONAL_BOOKS[w[4:]]["keys"]()
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


CHUNK = 200                      # piece keys in one "directory-all:<source>:<n>" word (one workflow run: at most 256)


def all_pieces(name, chunk=""):
    """Every piece key of one source back to its beginning ("directory-all:federal_register_rules"), or the n-th
    block of CHUNK of them ("directory-all:federal_register_rules:2"), so a request stays within one workflow run's
    256 jobs. name: a source of this module (dir:) or of directory_pubs (pub:)."""
    if name in PIECED or name in PERSONAL_BOOKS:
        keys = (PIECED.get(name) or PERSONAL_BOOKS[name])["keys"]()
    else:
        import directory_pubs                    # here, not at the top: it imports the periodicals builder
        keys = [f"pub:{name}:{p}" for p in directory_pubs.ALL_PIECES[name](None)]
    if chunk:
        n = int(chunk)
        keys = keys[(n - 1) * CHUNK:n * CHUNK]
    return keys


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
# left_out, limit), sign(piece)} (PIECED_SOURCES, below, source by source).
PERSONAL_BOOKS = {}              # the personal-use books of this module: name -> the same fields


# ====================================================================== children's stories (Kolibri Studio)

STUDIO = "https://studio.learningequality.org"
# Learning Equality's Kolibri Studio public channels (studio.learningequality.org/api/public/v1/channels): each one
# is a SQLite file of topics and resources with each resource's licence and files. Both channels below are CC BY
# throughout (checked 2026-11-21: every resource's license_name is "CC BY").
STORY_CHANNELS = {
    "storyweaver": dict(id="131e543dbecf5776bb13cfcfddf05605", title="Pratham Books' StoryWeaver",
                        publisher="Pratham Books' StoryWeaver and its partner publishers (from Learning Equality's "
                                  "Kolibri Studio channel)", country="India", source="https://storyweaver.org.in/",
                        kind="document"),
    "gdl": dict(id="0e173fca6e9052f8a474a2fb84055faf", title="Global Digital Library", country="International",
                publisher="Global Digital Library (Norad) and its partner publishers (from Learning Equality's Kolibri "
                          "Studio channel)", source="https://digitallibrary.io/", kind="h5p"),
}
# Reading levels of both libraries (StoryWeaver's own names for its four levels; the Global Digital Library uses the
# same four), given as the book's grade level.
LEVEL_WORDS = {"1": "Level 1: beginning to read (StoryWeaver's and the Global Digital Library's reading level; about "
                    "preschool to grade 1)",
               "2": "Level 2: learning to read (about grades 1 to 2)",
               "3": "Level 3: reading independently (about grades 2 to 4)",
               "4": "Level 4: reading proficiently (about grades 3 to 5)"}


def story_db(name, work):
    """An open connection to a story channel's SQLite file (downloaded into work once a day)."""
    import courses                               # here, not at the top: courses imports the builder
    spec = STORY_CHANNELS[name]
    return courses.kolibri_db(spec, work, str(courses.kolibri_channel_info(spec).get("version") or ""))


def story_tree(db):
    """[(node id, title, kind, description, author, licence, owner, language, level, category)] of every story:
    StoryWeaver's tree is category / publisher / language / level / story, the Global Digital Library's language /
    level / story."""
    nodes = {r[0]: r[1:] for r in db.execute("select id, title, parent_id, kind, description, author, license_name, "
                                             "license_owner from content_contentnode")}
    out = []
    for node_id, (title, parent, kind, desc, author, lic, owner) in nodes.items():
        if kind == "topic":
            continue
        chain, q = [], parent
        while q:
            chain.append(nodes[q][0])
            q = nodes[q][1]
        level = next((re.sub(r"\D", "", c) for c in chain if re.fullmatch(r"Level \d", c or "")), "")
        if len(chain) >= 5:                      # StoryWeaver
            language, category = chain[1], chain[3]
        else:                                    # the Global Digital Library
            language, category = (chain[1] if len(chain) > 1 else ""), ""
        out.append((node_id, title, kind, desc or "", author or "", lic or "", owner or "", language, level, category))
    return out


def story_pieces(name, work=None):
    """Every piece ("english-1": a language and a reading level) of a story channel, from its tree; the English
    pieces first."""
    work = work or os.path.join("build", "textbooks-cache", "work")
    rows = story_tree(story_db(name, work))
    pieces = sorted({(B.slug(r[7]), r[8] or "0") for r in rows if r[7]}, key=lambda p: (p[0] != "english", p))
    return [f"{lang}-{level}" for lang, level in pieces]


def h5p_text(data):
    """[(page title, HTML)] of an H5P interactive book (the Global Digital Library's stories): each chapter's texts
    (H5P.AdvancedText) in order; pictures are left out (their alt text kept when they have one)."""
    import io
    import zipfile
    try:
        content = json.loads(zipfile.ZipFile(io.BytesIO(data)).read("content/content.json"))
    except (zipfile.BadZipFile, KeyError, ValueError):
        return []
    pages = []
    for n, chapter in enumerate(content.get("chapters") or [], 1):
        parts = []

        def walk(x):
            if isinstance(x, dict):
                if isinstance(x.get("text"), str):
                    parts.append(x["text"])
                if x.get("alt"):
                    parts.append(f"<p>Picture: {B.esc(x['alt'])}</p>")
                for v in x.values():
                    if isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(chapter.get("params") or {})
        body = B._Cleaner({}, "").clean("".join(p if "<" in p else f"<p>{B.esc(p)}</p>" for p in parts))
        if re.sub(r"<[^>]+>", "", body).strip():
            pages.append((((chapter.get("metadata") or {}).get("title") or f"Page {n}"), body))
    return pages


def story_books(name, piece, work, cache=None, left_out=None, limit=None):
    """[Book] of one piece of a story channel: every story of one language at one reading level, one page per story
    (a StoryWeaver PDF's text, page by page; a Global Digital Library H5P book's pages), with its author, publisher,
    licence and description; stories that appear in several categories once. limit: only so many stories."""
    import courses                               # here, not at the top: courses imports the builder
    spec = STORY_CHANNELS[name]
    left_out = left_out if left_out is not None else []
    url = f"{STUDIO}/content/databases/{spec['id']}.sqlite3"
    if not readable(url, cache):
        left_out.append({"title": spec["title"], "reason": "robots.txt does not allow Kolibri Studio's channel file."})
        return []
    db = story_db(name, work)
    info = courses.kolibri_channel_info(spec)
    meta = db.execute("select version, last_updated from content_channelmetadata").fetchone() or (None, None)
    lang_slug, _, level = piece.rpartition("-")
    rows = [r for r in story_tree(db) if B.slug(r[7]) == lang_slug and (r[8] or "0") == level]
    if not rows:
        left_out.append({"title": f"{spec['title']}: {piece}", "reason": "The channel has no stories for this piece."})
        return []
    language = rows[0][7]
    seen, pages, owners, counts, originals = set(), [], set(), {}, []
    start = time.monotonic()
    for node_id, title, kind, desc, author, lic, owner, _lang, _lvl, category in sorted(rows, key=lambda r: r[1]):
        if (title, author) in seen or (limit and len(seen) >= limit):
            continue
        if time.monotonic() - start > TIME_BUDGET:
            counts["stories not read this time (the time for one build ran out)"] = \
                counts.get("stories not read this time (the time for one build ran out)", 0) + 1
            continue
        seen.add((title, author))
        if lic != "CC BY":
            counts[f"stories under \"{lic or 'no licence'}\""] = counts.get(f"stories under \"{lic or 'no licence'}\"",
                                                                             0) + 1
            continue
        files = courses.kolibri_files(db, node_id)
        credit = " ".join(x for x in (f"By {author}." if author else "", f"Published by {owner}." if owner else "",
                                      "Licence: CC BY 4.0.") if x)
        intro = (f"<p>{B.esc(' '.join(desc.split()))}</p>" if desc else "") + f"<p>{B.esc(credit)}</p>"
        path = f"s-{node_id[:12]}"
        got = []
        if kind == "document":
            for checksum, ext, _l in files.get("document", []):
                if ext != "pdf":
                    continue
                local = courses.download(courses.kolibri_file_url(checksum, ext),
                                         os.path.join(work, "kolibri", "files", f"{checksum}.pdf"))
                got = courses.pdf_pages_as_pages(local, path, title, 0, category or "Stories")
                os.remove(local)
                originals.append({"url": courses.kolibri_file_url(checksum, ext), "kind": "pdf"})
                break
        else:
            for checksum, ext, _l in files.get("h5p", []):
                data = B.fetch(courses.kolibri_file_url(checksum, ext), None, binary=True)
                parts = h5p_text(data)
                if parts:
                    body = "".join(f"<h2>{B.esc(t)}</h2>{b}" for t, b in parts)
                    got = [B.Page(path, title, body, 0, category or "Stories")]
                originals.append({"url": courses.kolibri_file_url(checksum, ext), "kind": "h5p"})
                break
        if not got:
            counts["stories without readable text"] = counts.get("stories without readable text", 0) + 1
            continue
        got[0].body = intro + got[0].body
        pages += got
        if owner:
            owners.add(owner)
    if not pages:
        return []
    level_words = LEVEL_WORDS.get(level, "")
    published = B.iso_date(info.get("last_published") or str(meta[1] or ""))
    book = B.Book(
        name=f"{name}_{B.slug(piece, 50).replace('-', '_')}",
        title=f"{spec['title']}: stories in {language}" + (f", level {level}" if level in LEVEL_WORDS else ""),
        subject="Children's stories and early reading", level="school", group="k12", publisher=spec["publisher"],
        country=spec["country"], licence="CC BY 4.0", licence_url=CC_BY_4, source=spec["source"],
        language=two_to_three(language), grades=level_words, published=published,
        version=f"Kolibri Studio channel \"{spec['title']}\" version {info.get('version') or meta[0]}",
        description=f"Children's picture stories in {language} from {spec['title']}" +
                    (f", {level_words.split(' (')[0]}" if level_words else "") + ": every story of the channel at "
                    "this level, one page each, with its words, author and publisher (the pictures are left out). "
                    "Good for early reading and for braille reading and transcription practice." +
                    (" Left out: " + "; ".join(f"{n} {what}" for what, n in sorted(counts.items())) + "." if counts
                     else ""),
        notice=("Publishers named in the channel: " + ", ".join(sorted(owners)) + ". " if owners else "") +
               "Each story is under the Creative Commons Attribution 4.0 licence; its own credits are on its page.",
        changes="each story's PDF or interactive book made into a web page of its words (pictures left out)")
    book.pages = pages
    book.originals = [{"url": f"{STUDIO}/content/databases/{spec['id']}.sqlite3", "kind": "sqlite"}] + originals[:200]
    return [book]


LANGUAGE_CODES = {"english": "eng", "hindi": "hin", "marathi": "mar", "kannada": "kan", "french": "fra", "tamil": "tam",
                  "telugu": "tel", "spanish": "spa", "korean": "kor", "urdu": "urd", "portuguese": "por",
                  "bengali": "ben", "gujarati": "guj", "punjabi": "pan", "odia": "ori", "malayalam": "mal",
                  "german": "deu", "italian": "ita", "thai": "tha", "vietnamese": "vie", "nepali": "nep",
                  "afrikaans": "afr", "amharic": "amh", "arabic": "ara", "kiswahili": "swa", "swahili": "swa"}


def two_to_three(language):
    """The three-letter code of a language name ("English" -> "eng"; "mul" when not known)."""
    return next((code for word, code in LANGUAGE_CODES.items() if word in language.lower()), "mul")


def _story_source(name):
    """The PIECED entry of a story channel."""
    return {"keys": lambda: [f"dir:{name}:{p}" for p in story_pieces(name)],
            "books": lambda piece, work, cache, left_out, limit: story_books(name, piece, work, cache, left_out,
                                                                             limit),
            "sign": lambda piece: str(__import__("courses").kolibri_channel_info(STORY_CHANNELS[name]).get("version")
                                      or "")}


PIECED_SOURCES = {"storyweaver": _story_source("storyweaver"), "gdl": _story_source("gdl")}
# The pieces built by default (the "directory" word): English at every level; other languages by key
# (dir:storyweaver lists every language and level from the channel).
for _name in ("storyweaver", "gdl"):
    PIECED_SOURCES[_name]["default"] = (lambda n=_name: [f"dir:{n}:english-{level}" for level in "1234"])


# ====================================================================== Encyclopaedia Britannica, 1st to 8th editions

NLS_EB_ZIP = "https://nlsfoundry.s3.amazonaws.com/text/nls-text-encyclopaediaBritannica.zip"
NLS_EB_PAGE = "https://data.nls.uk/data/digitised-collections/encyclopaedia-britannica/"
NLS_EB_TEXT = r"free of known copyright restrictions"
EB_EDITIONS = {"EB.1": "First edition, 1771", "EB.3": "First edition, 1773 printing", "EB.4": "Second edition",
               "EB.5": "Third edition", "EB.6": "Supplement to the third edition", "EB.7": "Fourth edition",
               "EB.8": "Fifth edition", "EB.9": "Supplement to the fourth, fifth and sixth editions",
               "EB.10": "Sixth edition", "EB.11": "Seventh edition", "EB.12": "Eighth edition"}
EB_NOTE = ("An old encyclopaedia (published 1768 to 1860), kept for its history and its words: its science, "
           "medicine, geography, law and its descriptions of peoples are out of date, and some of its language is "
           "offensive today. Never take its medical, legal or safety advice. The text was read by a scanner (OCR) "
           "without correction and has its mistakes (the long s is often read as f).")
EB_CHUNK = 60000                 # characters of a volume per book page


def eb_zip(work):
    """The path of the Data Foundry's text download (downloaded into work once per job)."""
    path = os.path.join(work, "nls", os.path.basename(NLS_EB_ZIP))
    if not os.path.exists(path):
        import courses                           # here, not at the top: courses imports the builder
        courses.download(NLS_EB_ZIP, path)
    return path


def eb_inventory(zf):
    """[(file name, title, edition code)] of the volumes, from the dataset's inventory CSV, in its order."""
    import csv
    name = next(n for n in zf.namelist() if n.endswith("inventory.csv"))
    rows = csv.reader(zf.read(name).decode("utf-8-sig").splitlines())
    out = []
    for row in rows:
        if len(row) >= 2:
            code = (re.search(r"- (EB\.\d+)\s*$", row[1]) or re.search(r"()", "")).group(1)
            out.append((row[0], row[1], code))
    return out


def eb_volume_pages(text, volume, number, unit):
    """[B.Page] of one volume's OCR text, in pieces of about EB_CHUNK characters cut at paragraph ends, each titled
    with the volume and the first headword in capitals it holds."""
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n|\n(?=[A-Z][A-Z]{2,}[ ,.])", text) if p.strip()]
    pages, chunk, size, part = [], [], 0, 1

    def flush():
        nonlocal chunk, size, part
        if not chunk:
            return
        head = next((m.group(0) for p in chunk for m in [re.match(r"[A-Z][A-Z'-]{2,}", p)] if m), "")
        title = f"{volume}, part {part}" + (f" (from {head.title()})" if head else "")
        pages.append(B.Page(f"v{number}-{part}", title, "".join(f"<p>{B.esc(p)}</p>" for p in chunk), number, unit))
        chunk, size, part = [], 0, part + 1
    for p in paras:
        chunk.append(p)
        size += len(p)
        if size >= EB_CHUNK:
            flush()
    flush()
    return pages


def eb_books(piece, work, cache=None, left_out=None, limit=None):
    """[Book] of one edition (piece "eb-1", "eb-12": the dataset's edition codes EB.1 to EB.12): every volume's
    whole OCR text, in pages of about EB_CHUNK characters, the volumes as the parts."""
    import zipfile
    left_out = left_out if left_out is not None else []
    code = "EB." + piece.split("-", 1)[1]
    if not readable(NLS_EB_PAGE, cache) or not re.search(NLS_EB_TEXT, B.fetch(NLS_EB_PAGE, None)):
        left_out.append({"title": f"Encyclopaedia Britannica {piece}", "reason": "The Data Foundry's page no longer "
                         "states that the collection is free of known copyright restrictions."})
        return []
    zf = zipfile.ZipFile(eb_zip(work))
    vols = [v for v in eb_inventory(zf) if v[2] == code]
    if limit:
        vols = vols[:1]
    pages, years = [], []
    for number, (fname, title, _code) in enumerate(vols, 1):
        member = next((n for n in zf.namelist() if n.endswith("/" + fname) or n == fname), "")
        if not member:
            continue
        text = zf.read(member).decode("utf-8", "replace")
        volume = re.sub(r"^.*?\b(Volume|Supplement)\b", r"\1", title.split(" - ")[-2] if " - " in title else title)
        years += re.findall(r"\b1[78]\d\d\b", title)
        got = eb_volume_pages(text, volume, number, volume)
        pages += got[:limit] if limit else got
    if not pages:
        left_out.append({"title": f"Encyclopaedia Britannica {piece}", "reason": "No volume of this edition is in the "
                         "dataset."})
        return []
    edition = EB_EDITIONS.get(code, code)
    book = B.Book(
        name=f"encyclopaedia_britannica_{piece.replace('-', '_')}", title=f"Encyclopaedia Britannica, {edition} "
        "(National Library of Scotland)", subject="Encyclopaedia (historical)", level="reference", group="history",
        publisher="Encyclopaedia Britannica (Edinburgh, 1768-1860); digitised by the National Library of Scotland "
                  "(Data Foundry)", country="United Kingdom", licence="Public domain (published before 1931)",
        licence_url="https://rightsstatements.org/page/NKC/1.0/", source=NLS_EB_PAGE,
        published=min(years) if years else "", version="Data Foundry text dataset (DOI 10.34812/cb5h-qf89)",
        description=f"The {edition} of the Encyclopaedia Britannica, every volume's whole text as the National "
                    f"Library of Scotland's Data Foundry gives it ({len(vols)} volumes), in pages of about ten "
                    "thousand words, each named by its volume and its first headword.",
        notice=EB_NOTE + " Rights: the National Library of Scotland says items up to 1853 are free of known copyright "
                         "and in the public domain, and items from 1854 to 1860 likely to be free of known copyright "
                         "restrictions (No Known Copyright); all were published before 1931, so they are in the US "
                         "public domain.",
        practice_note="Scottish source of the 18th and 19th centuries: its laws, money (pounds, shillings and "
                      "pence), weights and measures, place names and medicine are those of Britain at the time and "
                      "differ from present US practice.",
        changes="each volume's OCR text cut into pages of about ten thousand words (words unchanged)")
    book.pages = pages
    book.originals = [{"url": NLS_EB_ZIP, "kind": "zip"}]
    return [book]


EB_PIECES = [f"eb-{c.split('.')[1]}" for c in EB_EDITIONS]
PIECED_SOURCES["encyclopaedia_britannica"] = {
    "keys": lambda: [f"dir:encyclopaedia_britannica:{p}" for p in EB_PIECES],
    "books": eb_books, "sign": lambda piece: sha(__import__("updates").head_signs(NLS_EB_ZIP))}


# ====================================================================== OEIS (its bulk files)

OEIS = "https://oeis.org"
OEIS_FILES = {"names": OEIS + "/names.gz", "stripped": OEIS + "/stripped.gz"}
OEIS_LICENCE_PAGE = OEIS + "/wiki/The_OEIS_End-User_License_Agreement"
OEIS_TEXT = r"Creative Commons Attribution Share-Alike 4\.0 license"
OEIS_PIECE = 10000               # sequences in one book
OEIS_PAGE = 100                  # sequences on one page


def oeis_data(work, cache=None):
    """{A-number: [name, terms]} from the OEIS's bulk files (names.gz and stripped.gz), read once per job."""
    import gzip
    if "_oeis" in globals() and _oeis:
        return _oeis
    out = {}
    for kind, url in OEIS_FILES.items():
        if not readable(url, cache):
            raise LookupError(f"robots.txt does not allow {url}")
        text = gzip.decompress(B.fetch(url, None, binary=True)).decode("utf-8", "replace")
        for line in text.splitlines():
            if not line.startswith("A"):
                continue
            number, _, rest = line.partition(" ")
            row = out.setdefault(number, ["", ""])
            row[0 if kind == "names" else 1] = rest.strip().strip(",") if kind == "stripped" else rest.strip()
    globals()["_oeis"] = out
    return out


_oeis = {}


def oeis_books(piece, work, cache=None, left_out=None, limit=None):
    """[Book] of one block of 10,000 sequences (piece "0" is A000001 to A010000, "1" is A010001 to A020000 ...): each
    sequence's number, name and first terms, 100 to a page."""
    left_out = left_out if left_out is not None else []
    if ai_refused(OEIS + "/", cache):
        left_out.append({"title": "OEIS", "reason": "The site shuts out AI companies' readers."})
        return []
    if not readable(OEIS_LICENCE_PAGE, cache) or not re.search(OEIS_TEXT, B.fetch(OEIS_LICENCE_PAGE, None)):
        left_out.append({"title": "OEIS", "reason": "Its licence page no longer states CC BY-SA 4.0."})
        return []
    data = oeis_data(work, cache)
    first = int(piece) * OEIS_PIECE + 1
    numbers = [f"A{n:06d}" for n in range(first, first + OEIS_PIECE) if f"A{n:06d}" in data]
    if limit:
        numbers = numbers[:limit * OEIS_PAGE]
    pages = []
    for i in range(0, len(numbers), OEIS_PAGE):
        block = numbers[i:i + OEIS_PAGE]
        items = "".join(f"<li><strong>{n}</strong>: {B.esc(data[n][0].rstrip('.'))}. Terms: "
                        f"{B.esc(data[n][1].replace(',', ', '))}"
                        f" (<a href=\"{OEIS}/{n}\">{OEIS}/{n}</a>)</li>" for n in block)
        pages.append(B.Page(f"{block[0].lower()}-{block[-1].lower()}", f"{block[0]} to {block[-1]}",
                            f"<ul>{items}</ul>", 0, f"{numbers[0]} to {numbers[-1]}"))
    if not pages:
        return []
    book = B.Book(
        name=f"oeis_{numbers[0].lower()}_{numbers[-1].lower()}", title=f"OEIS: integer sequences {numbers[0]} to "
        f"{numbers[-1]}", subject="Mathematics (integer sequences)", level="reference", group="science",
        publisher="The OEIS Foundation (The On-Line Encyclopedia of Integer Sequences)", country="International",
        licence="CC BY-SA 4.0", licence_url=CC_BY_SA_4, source=OEIS + "/",
        published=datetime.date.today().isoformat(), version=f"OEIS bulk files of {datetime.date.today().isoformat()}",
        description=f"The On-Line Encyclopedia of Integer Sequences, sequences {numbers[0]} to {numbers[-1]}: each "
                    "one's number, name and first terms, as the OEIS's bulk files give them (the comments, formulas "
                    "and references are on each sequence's page at oeis.org).",
        notice="The OEIS is made available under the Creative Commons Attribution Share-Alike 4.0 license; credit: The "
               "On-Line Encyclopedia of Integer Sequences, published electronically at https://oeis.org.",
        changes="the bulk files' lines made into web pages, 100 sequences to a page")
    book.pages = pages
    book.originals = [{"url": u, "kind": "gz"} for u in OEIS_FILES.values()]
    return [book]


PIECED_SOURCES["oeis"] = {"keys": lambda: [f"dir:oeis:{n}" for n in range(40)], "books": oeis_books,
                          "sign": lambda piece: month_token()}


# ====================================================================== buckets

def bucket_of(text, n):
    """A stable bucket number (0 to n-1) of a text."""
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % n


# ====================================================================== Lumen Learning (Pressbooks' API)

LUMEN = "https://courses.lumenlearning.com"
LUMEN_BUCKETS = 8


def lumen_catalogue(cache=None):
    """Every Lumen Learning Pressbooks book with a CC BY or CC BY-SA licence in its metadata (the network's
    /wp-json/pressbooks/v2/books list, 10 a page): [(address, name, licence, licence address, authors, updated)].
    Lumen's main site asks 3 seconds between requests (lumenlearning.com/robots.txt), kept here for its courses too."""
    B.CRAWL_DELAY["courses.lumenlearning.com"] = max(3.0, B.CRAWL_DELAY.get("courses.lumenlearning.com", 0))
    out, page = [], 1
    while page < 400:
        try:
            data = json.loads(B.fetch(f"{LUMEN}/wp-json/pressbooks/v2/books?per_page=10&page={page}", None))
        except urllib.error.HTTPError:
            break
        if not data:
            break
        for b in data:
            m = b.get("metadata") or {}
            lic = m.get("license") or {}
            short = B.licence_short(str(lic.get("name") or lic.get("code") or ""), str(lic.get("url") or ""))
            if B.licence_kind(short) in ("open", "share-alike") and m.get("inCatalog", True) is not False:
                authors = ", ".join(a.get("name", "") for a in m.get("author") or [] if isinstance(a, dict))
                out.append((b.get("link", ""), m.get("name", ""), short, str(lic.get("url") or ""), authors,
                            B.iso_date(str(m.get("lastUpdated") or ""))))
        page += 1
    return out


def lumen_book(link, title, licence, licence_url, authors, updated, cache=None, left_out=None, limit=None):
    """The Book of one Lumen course: its table of contents (Pressbooks' /wp-json/pressbooks/v2/toc) and each
    chapter's content from /wp-json/pressbooks/v2/chapters/<id>, in order, the parts as the units."""
    toc = json.loads(B.fetch(f"{link.rstrip('/')}/wp-json/pressbooks/v2/toc", None))
    entries = []
    for kind in ("front-matter", "parts", "back-matter"):
        for item in toc.get(kind) or []:
            if kind == "parts":
                for ch in item.get("chapters") or []:
                    entries.append(("chapters", ch, item.get("title", "")))
            else:
                entries.append((kind, item, ""))
    pages = []
    for kind, ch, unit in entries[:limit] if limit else entries:
        api = f"{link.rstrip('/')}/wp-json/pressbooks/v2/{kind}/{ch.get('id')}"
        if not readable(api, cache):
            continue
        try:
            data = json.loads(B.fetch(api, cache))
        except (urllib.error.URLError, OSError, ValueError):
            continue
        body = B._Cleaner({}, link).clean((data.get("content") or {}).get("rendered", ""))
        if re.sub(r"<[^>]+>", "", body).strip():
            pages.append(B.Page(B.slug(ch.get("slug") or ch.get("title", ""), 50) or f"p{len(pages)}",
                                html.unescape(ch.get("title", "")), body, 0, html.unescape(unit)))
    if not pages:
        return None
    book = B.Book(name=f"lumen_{B.slug(urllib.parse.urlsplit(link).path.strip('/'), 50).replace('-', '_')}",
                  title=f"{html.unescape(title)} (Lumen Learning)", subject=html.unescape(title), level="college",
                  group="course", publisher="Lumen Learning and the course's authors", country="United States",
                  licence=licence, licence_url=licence_url or B._licence_address(licence), source=link,
                  authors=authors, published=updated, version=f"Pressbooks, updated {updated}" if updated else "",
                  description=f"{html.unescape(title)}: a Lumen Learning open course, every chapter, from Pressbooks' "
                              "own API.", changes="each chapter made into a web page (pictures left out, their "
                                                   "descriptions kept)")
    book.pages = pages
    return book


def lumen_books(piece, work, cache=None, left_out=None, limit=None):
    """[Book] of one bucket of Lumen Learning's CC BY and CC BY-SA courses (piece "0" to "7")."""
    left_out = left_out if left_out is not None else []
    if ai_refused(LUMEN + "/", cache):
        left_out.append({"title": "Lumen Learning", "reason": "The site shuts out AI companies' readers."})
        return []
    out, start = [], time.monotonic()
    for row in lumen_catalogue(cache):
        if bucket_of(row[0], LUMEN_BUCKETS) != int(piece) or (limit and len(out) >= 1):
            continue
        if time.monotonic() - start > TIME_BUDGET:
            left_out.append({"title": row[1], "reason": "The time for one build ran out; built next time."})
            continue
        try:
            book = lumen_book(*row, cache=cache, left_out=left_out, limit=limit)
        except Exception as e:  # noqa: BLE001 - one book's failure does not stop the others
            left_out.append({"title": row[1], "reason": f"It could not be read ({e})."})
            book = None
        if book is not None:
            out.append(book)
    return out


PIECED_SOURCES["lumen"] = {"keys": lambda: [f"dir:lumen:{n}" for n in range(LUMEN_BUCKETS)], "books": lumen_books,
                           "sign": lambda piece: sha(sorted((r[0], r[5]) for r in lumen_catalogue()
                                                            if bucket_of(r[0], LUMEN_BUCKETS) == int(piece)))}


# ====================================================================== Raspberry Pi Projects (CC BY-SA 4.0)

RPI_SITEMAP = "https://projects-static.raspberrypi.org/sitemaps/sitemap.xml.gz"
RPI_RAW = "https://raw.githubusercontent.com/raspberrypilearning"
RPI_BUCKETS = 6


def rpi_projects(cache=None):
    """The slugs of every English project of projects.raspberrypi.org, from its sitemap (gzipped, listed in its
    robots.txt); each project's text is in the Raspberry Pi Foundation's public repository of the same name."""
    import gzip
    root = gzip.decompress(B.fetch(RPI_SITEMAP, None, binary=True)).decode("utf-8", "replace")
    urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", root)
    subs = [u for u in urls if u.endswith(".xml.gz") or u.endswith(".xml")]
    for sub in subs[:20]:
        data = B.fetch(sub, None, binary=True)
        urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", (gzip.decompress(data) if sub.endswith(".gz") else data)
                           .decode("utf-8", "replace"))
    not_projects = {"projects", "codeclub", "pathways", "collections", "jam", "en"}
    return sorted({m.group(1) for u in urls for m in [re.search(r"projects\.raspberrypi\.org/en/(?:projects/)?"
                                                                r"([a-z0-9-]+)/?$", u)]
                   if m and m.group(1) not in not_projects})


def md_inline(text):
    """Markdown inline marks as HTML: pictures as "Picture: " and their description, links, bold, italics, code;
    kramdown attribute lists ({:target="_blank"}) left out."""
    text = re.sub(r"\{:[^}]*\}", "", text)
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)           # raw HTML in the Markdown (a video player) left out
    out = B.esc(text)
    out = re.sub(r"!\[([^\]]*)\]\([^)]*\)", lambda m: f"(Picture: {m.group(1)})" if m.group(1).strip() else "", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)[^)]*\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", out)
    out = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", out)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", out)


def markdown_html(text):
    """A Raspberry Pi project step (Markdown with the Foundation's "--- task ---", "--- collapse ---", "--- code ---"
    and "--- hint ---" blocks) as HTML: headings, paragraphs, lists, code as preformatted text, each block said in
    words ("Task:", "More:", "Hint:")."""
    out, para, items, code, in_code, front = [], [], [], [], False, False
    labels = {"task": "Task", "collapse": "More", "hint": "Hint", "hints": "Hints", "challenge": "Challenge",
              "no-print": "", "print-only": "", "save": "Save your project"}

    def flush():
        if para:
            out.append(f"<p>{md_inline(' '.join(para))}</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{md_inline(x)}</li>" for x in items) + "</ul>")
            items.clear()
    for line in text.replace("\r", "").split("\n"):
        block = re.match(r"^\s*---\s*(/?)([a-z-]+)\s*---\s*$", line)
        if in_code:
            if line.strip().startswith("```") or (block and block.group(2) == "code" and block.group(1)):
                out.append("<pre>" + B.esc("\n".join(code)) + "</pre>")
                code, in_code = [], False
            elif front:                              # the block's own settings between two "---" lines
                if line.strip() == "---":
                    front = 1 if front is True else False
                elif front is True:                  # no settings: this is code already
                    front = False
                    code.append(line)
            else:
                code.append(line)
            continue
        if line.strip().startswith("```"):
            flush()
            in_code = True
            continue
        if block:
            flush()
            name = block.group(2)
            if name == "code" and not block.group(1):
                in_code, front = True, True
            elif not block.group(1) and labels.get(name):
                out.append(f"<p><strong>{labels[name]}:</strong></p>")
            continue
        if line.strip() == "---":                   # a block's own title lines follow ("title: ...")
            continue
        m = re.match(r"^\s*title:\s*(.+)$", line)
        if m and not para:
            out.append(f"<h3>{md_inline(m.group(1))}</h3>")
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            flush()
            level = min(len(h.group(1)) + 1, 6)
            out.append(f"<h{level}>{md_inline(h.group(2))}</h{level}>")
        elif re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            if para:
                flush()
            items.append(re.sub(r"^\s*([-*+]|\d+\.)\s+", "", line))
        elif not line.strip():
            flush()
        else:
            if items and line.startswith("  "):
                items[-1] += " " + line.strip()
            else:
                para.append(line.strip())
    flush()
    return "\n".join(x for x in out if x)


def rpi_meta(slug, cache=None):
    """(branch, title, description, step titles) of a project from its repository's en/meta.yml ("master" or
    "main" branch); None when it has none."""
    for branch in ("master", "main"):
        url = f"{RPI_RAW}/{slug}/{branch}/en/meta.yml"
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            continue
        title = (re.search(r"^title:\s*(.+)$", text, re.M) or re.search(r"()", "")).group(1).strip().strip("'\"")
        desc = re.search(r"^description:\s*(.+(?:\n\s{2,}.+)*)", text, re.M)
        steps = re.findall(r"^\s*-\s*title:\s*(.+)$", text, re.M)
        return branch, title or slug, " ".join(desc.group(1).split()).strip("'\"") if desc else "", steps
    return None


def rpi_books(piece, work, cache=None, left_out=None, limit=None):
    """[Book] of one bucket of Raspberry Pi projects (piece "0" to "5"): each project's steps in order (from its
    public repository's en/step_<n>.md), the projects as the parts; a project whose LICENCE.md does not give CC BY-SA
    4.0 is left out."""
    left_out = left_out if left_out is not None else []
    if ai_refused("https://projects.raspberrypi.org/en", cache):
        left_out.append({"title": "Raspberry Pi Projects", "reason": "The site shuts out AI companies' readers."})
        return []
    pages, done, closed, start = [], 0, 0, time.monotonic()
    for slug in rpi_projects(cache):
        if bucket_of(slug, RPI_BUCKETS) != int(piece) or (limit and done >= limit):
            continue
        if time.monotonic() - start > TIME_BUDGET:
            left_out.append({"title": f"Raspberry Pi project {slug}", "reason": "The time for one build ran out."})
            continue
        meta = rpi_meta(slug, cache)
        if meta is None:
            continue
        branch, title, desc, steps = meta
        try:
            licence = B.fetch(f"{RPI_RAW}/{slug}/{branch}/LICENCE.md", cache)
        except (urllib.error.URLError, OSError):
            licence = ""
        if "by-sa/4.0" not in licence:
            closed += 1
            continue
        for n, step in enumerate(steps, 1):
            try:
                text = B.fetch(f"{RPI_RAW}/{slug}/{branch}/en/step_{n}.md", cache)
            except (urllib.error.URLError, OSError):
                continue
            body = (f"<p>{B.esc(desc)}</p>" if n == 1 and desc else "") + markdown_html(text)
            pages.append(B.Page(f"{slug}-{n}", f"{title}: {step.strip().strip(chr(39) + chr(34))}", body, 0, title))
        done += 1
    if closed:
        left_out.append({"title": "Raspberry Pi Projects", "reason": f"{closed} projects' repositories do not give the "
                         "CC BY-SA 4.0 licence: left out."})
    if not pages:
        return []
    book = B.Book(name=f"raspberry_pi_projects_{piece}", title=f"Raspberry Pi Projects: coding and electronics, part "
                  f"{int(piece) + 1} of {RPI_BUCKETS}", subject="Coding and electronics projects", level="school",
                  group="k12", publisher="Raspberry Pi Foundation", country="United Kingdom", licence="CC BY-SA 4.0",
                  licence_url=CC_BY_SA_4, source="https://projects.raspberrypi.org/en",
                  grades="Ages 7 to 18 (projects at every level, from first Scratch games to Python and electronics)",
                  version=f"read {datetime.date.today().isoformat()}",
                  description="The Raspberry Pi Foundation's step-by-step coding and electronics projects (Scratch, "
                              "Python, HTML and CSS, physical computing, machine learning), each project's steps in "
                              "order with its code as text; the pictures are left out (their descriptions kept).",
                  notice="Raspberry Pi Foundation projects, licensed under the Creative Commons Attribution-ShareAlike "
                         "4.0 International licence; each project is at https://projects.raspberrypi.org/en/projects/"
                         "<its name>.",
                  practice_note="UK source: spellings, school years and some hardware names follow UK use.",
                  changes="each step's Markdown made into a web page (pictures left out, their descriptions kept)")
    book.pages = pages
    return [book]


PIECED_SOURCES["raspberry_pi_projects"] = {
    "keys": lambda: [f"dir:raspberry_pi_projects:{n}" for n in range(RPI_BUCKETS)], "books": rpi_books,
    "sign": lambda piece: sha(sorted(s for s in rpi_projects() if bucket_of(s, RPI_BUCKETS) == int(piece)),
                              month_token())}


# ====================================================================== personal use only

OYC = "https://oyc.yale.edu"
OYC_TERMS = OYC + "/terms"
OYC_TEXT = r"Creative Commons Attribution-Noncommercial-Share Alike 3\.0"


def oyc_courses(cache=None):
    """The course addresses of Open Yale Courses ("https://oyc.yale.edu/astronomy/astr-160"), from its course list."""
    text = B.fetch(OYC + "/courses", None)
    return sorted({u.rstrip("/") for u in any_links(text, OYC + "/courses")
                   if re.match(r"^https://oyc\.yale\.edu/[a-z-]+/[a-z]+-\d+[a-z]?/?$", u)})


def oyc_books(piece, work, cache=None, left_out=None, limit=None):
    """[Book] of one Open Yale course (piece: its code, "astr-160"): the course page and every lecture's page with its
    whole transcript, personal use only (CC BY-NC-SA 3.0)."""
    left_out = left_out if left_out is not None else []
    course = next((c for c in oyc_courses(cache) if c.endswith("/" + piece)), "")
    if not course:
        left_out.append({"title": f"Open Yale Courses {piece}", "reason": "The course is no longer listed."})
        return []
    entry = dict(US, name=f"open_yale_courses_{piece.replace('-', '_')}", title="", subject="College course "
                 "(lecture transcripts)", group="course", level="college", country="United States",
                 publisher="Open Yale Courses (Yale University)", licence="CC BY-NC-SA 3.0",
                 licence_url="https://creativecommons.org/licenses/by-nc-sa/3.0/us/", source=course,
                 licence_page=OYC_TERMS, licence_text=OYC_TEXT, personal_use=True,
                 description="", crawl=[(course, 1)], follow=r"$^",
                 pages=rf"^{re.escape(course)}(/(lecture|session)-\d+)?$",
                 unit_rules=[(r"lecture|session", "Lectures"), (r".", "About the course")], limit=60,
                 title_from=r"<h2>([A-Z]{2,6} \d+[a-z]? - (?:Lecture|Session) \d+[^<]*)</h2>")
    text = B.fetch(course, cache)
    entry["title"] = f"{B.first_heading(text) or piece} (Open Yale Courses)"
    entry["description"] = (f"{entry['title']}: the course page and every lecture with its whole transcript, as Open "
                            "Yale Courses publishes them (the videos are not included). Personal use only.")
    entry["notice"] = ("Most of the lectures and course material within Open Yale Courses are licensed under a Creative "
                       "Commons Attribution-Noncommercial-Share Alike 3.0 license; third-party content named in a "
                       "lecture's credits is not covered.")
    book = guide_book(entry, cache, left_out, limit)
    return [book] if book is not None else []


PERSONAL_BOOKS["open_yale_courses"] = {
    "keys": lambda: [f"dir:open_yale_courses:{c.rsplit('/', 1)[-1]}" for c in oyc_courses()],
    "books": oyc_books, "sign": lambda key: month_token()}

# The 80 repositories the inventory marked "personal use only", each with what was done: (name, the inventory's
# section, what was done: a build key, or the reason it is not built).
PERSONAL = [
    ("Irish Health Publications Archive (hselibrary.ie)", "OpenDOAR", "Not built: no feed or API; its publications "
     "are deposited in Lenus (below)."),
    ("Bookshare", "OpenDOAR", "Not built: membership only (the owner's own account); never redistributable. See "
     "OWNER_NOTES."),
    ("Exploratorium Digital Library", "OpenDOAR", "Not built: www.exploratorium.edu answers programs with 403 "
     "(robots.txt included)."),
    ("Werner Icking Music Archive", "OpenDOAR", "Not built: sheet music as pictures (PDF scans), no text; for braille "
     "music transcription the owner opens it in a browser."),
    ("A Celebration of Women Writers (University of Pennsylvania)", "OpenDOAR", "Not built: its pages say only "
     "\"Copyright 1994-2026\" with no licence; most of its works are in Project Gutenberg and Wikisource (Kiwix)."),
    ("Biblioteca Virtual Miguel de Cervantes", "OpenDOAR", "Not built: Spanish literature under the site's own terms, "
     "which limit reuse."),
    ("First World War Poetry Digital Archive (Oxford)", "OpenDOAR", "Not built: images and catalogue records; the "
     "poems' texts are in Project Gutenberg and Wikisource (Kiwix)."),
    ("Historic American Sheet Music (Duke)", "OpenDOAR", "Not built: sheet music as pictures, no text."),
    ("Lenus, The Irish Health Repository", "OpenDOAR", "Not built yet: its DSpace OAI-PMH records give no file "
     "addresses (Crawl-delay 10); a reader of its REST API would be needed."),
    ("Papers Past (New Zealand)", "OpenDOAR", "Not built: its robots.txt address answers with a bot-check page."),
    ("Policy Archive", "OpenDOAR", "Not built: its robots.txt disallows every PDF (\"Disallow: /*.pdf\") and the "
     "bitstreams."),
    ("Riberdis (Spain)", "OpenDOAR", "Not built: Spanish-language documents, copyright per item."),
    ("Applied Math and Science Education Repository (AMSER)", "ROAR", "Not built: a list of links to other sites "
     "(a referatory), no texts of its own."),
    ("ATE Central", "ROAR", "Not built: a referatory of technician-education materials, licence per item."),
    ("Exploratorium Digital Library", "ROAR", "Not built: 403 (as above)."),
    ("Digital Collections, National Library of Medicine", "ROAR", "Not built: collections.nlm.nih.gov's robots.txt "
     "shuts out anthropic-ai and GPTBot (\"Disallow: /\")."),
    ("Oxford Text Archive", "re3data", "Not built: access restricted per item (many need registration and a signed "
     "agreement)."),
    ("International Music Score Library Project (IMSLP)", "re3data", "Not built: scores as pictures, no text (for "
     "braille music transcription, opened in a browser)."),
    ("NIST Digital Library of Mathematical Functions", "re3data", "Not built: its notice says \"Bulk copying, "
     "reproduction, or redistribution in any form is not permitted\" (dlmf.nist.gov/about/notices)."),
    ("Agrega 2 (Spain)", "OER World Map", "Not built: Spanish."),
    ("Applied Math and Science Education Repository", "OER World Map", "Not built: referatory (as above)."),
    ("Bundeszentrale für politische Bildung: Lernen", "OER World Map", "Not built: German."),
    ("Curriki", "OER World Map", "Not built: mostly non-commercial items on a site with no feed or API."),
    ("e-genius (Austria)", "OER World Map", "Not built: German."),
    ("eBook-Lessons (Austria)", "OER World Map", "Not built: German."),
    ("eCampusOntario Open Library", "OER World Map", "Not built yet: a catalogue of Pressbooks books on many hosts, "
     "licence per book; the reader of Lumen's Pressbooks API could be pointed at them later."),
    ("EDUCARE (Brazil)", "OER World Map", "Not built: Portuguese."),
    ("EmRede (Brazil)", "OER World Map", "Not built: Portuguese."),
    ("HELM Open (University of Nottingham)", "OER World Map", "Not built: interactive learning objects (animations), "
     "little text."),
    ("Instructables", "OER World Map", "Not built: its robots.txt disallows /howto/ and every .html page, and each "
     "project is its author's copyright."),
    ("IntechOpen", "OER World Map", "Not built: its robots.txt has a group for ClaudeBot, GPTBot and CCBot; books are "
     "reached through DOAB, which is blocked."),
    ("Intellectum (Colombia)", "OER World Map", "Not built: Spanish."),
    ("Kidsome", "OER World Map", "Not built: CC BY-NC-ND children's videos and games; no feed."),
    ("Kita Fachtexte (Germany)", "OER World Map", "Not built: German."),
    ("La Trobe eBureau", "OER World Map", "Not built yet: Pressbooks textbooks, licence per book; could use the "
     "Pressbooks reader later."),
    ("Library of Open Educational Resources (aoe.fi)", "OER World Map", "Not built: Finnish."),
    ("METU OpenCourseWare", "OER World Map", "Not built: course pages, mostly slides; host not checked further."),
    ("Netaji Subhas Open University OER Repository", "OER World Map", "Not built: DSpace of study materials; host "
     "not checked further."),
    ("Open Institutional Repository, Autonomous University of the State of Hidalgo", "OER World Map", "Not built: "
     "Spanish."),
    ("Open Oregon State", "OER World Map", "Not built: open.oregonstate.education answers programs with 403."),
    ("Open Yale Courses", "OER World Map", "Built: dir:open_yale_courses:<course> (every course, each lecture's "
     "transcript; CC BY-NC-SA 3.0, personal use only)."),
    ("Open.Ed (University of Edinburgh)", "OER World Map", "Not built: a guide to Edinburgh's open materials on other "
     "sites."),
    ("OpenCourseWare Universidad Carlos III de Madrid", "OER World Map", "Not built: Spanish."),
    ("OpenMichigan: Deep Blue", "OER World Map", "Not built: the host did not answer (inventory)."),
    ("PDXOPEN (Portland State)", "OER World Map", "Not built: bepress Digital Commons, whose PDFs answer programs "
     "with a bot check (as RIT's and GALILEO's do)."),
    ("Proedu (Brazil)", "OER World Map", "Not built: Portuguese."),
    ("SaberULA (Venezuela)", "OER World Map", "Not built: Spanish."),
    ("Saskatchewan Open Education Resources", "OER World Map", "Not built: saskoer.ca now answers with a parked "
     "page."),
    ("Saving Planets", "OER World Map", "Not built: a small site with no feed."),
    ("Spoken Tutorial", "OER World Map", "Not built: video tutorials."),
    ("Teachers Without Borders", "OER World Map", "Not built: no feed or API."),
    ("TeachingOERmath.info", "OER World Map", "Not built: a small site with no feed."),
    ("UFPA Multimidia (Brazil)", "OER World Map", "Not built: Portuguese."),
    ("University of Tripoli Digital Repository", "OER World Map", "Not built: Arabic research outputs."),
    ("VideoLectures.NET", "OER World Map", "Not built: videos (CC BY-NC-ND)."),
    ("Wawasan Open University OER Repository", "OER World Map", "Not built: a WEKO repository with no feed that "
     "answered."),
    ("Youth Start (Austria)", "OER World Map", "Not built: German."),
    ("Disability Studies Quarterly", "DOAJ", "Built: pub:dsq:<year> (Janeway OAI-PMH; CC BY-NC-ND 4.0, each article "
     "whole and unchanged)."),
    ("Journal of Accessibility and Design for All", "DOAJ", "Built: pub:jacces:<year> (OJS OAI-PMH; CC BY-NC 4.0)."),
    ("Canadian Journal of Disability Studies", "DOAJ", "Built: pub:cjds:<year> (OJS OAI-PMH; CC BY-NC-ND 4.0, whole "
     "and unchanged)."),
    ("Developmental Disabilities Network Journal", "DOAJ", "Not built: its bepress PDFs answer programs with a bot "
     "check (403), although its OAI-PMH feed answers."),
    ("Disability, CBR and Inclusive Development", "DOAJ", "Built: pub:dcidj:<year> (OJS OAI-PMH; CC BY-NC-ND 4.0, "
     "whole and unchanged)."),
    ("Indian Journal of Ophthalmology", "DOAJ", "Built: pub:jnl_indian_journal_ophthalmology:<piece> (Europe PMC; "
     "CC BY-NC-SA)."),
    ("NLM Digital Collections", "US agencies", "Not built: AI-reader block (as above)."),
    ("Catalog of US Government Publications (GPO)", "data.gov", "Not built: a finding list of records, not texts "
     "(catalog.gpo.gov answers 403); its booklets are reached through govinfo and the Internet Archive collections."),
    ("NIST Digital Library of Mathematical Functions", "data.gov", "Not built: no bulk copying (as above)."),
    ("National Sexual Violence Resource Center", "data.gov", "Not built: its robots.txt says ai-train=no and shuts "
     "out ClaudeBot and anthropic-ai."),
    ("Internet Archive: Community Texts", "Internet Archive", "Built: pub:ia_opensource:<subject> (items with a "
     "Creative Commons or public-domain licence address only)."),
    ("Internet Archive: Canadian Government Publications Portal", "Internet Archive", "Built: "
     "pub:ia_governmentpublications:<subject> (Crown copyright, non-commercial reproduction)."),
    ("Internet Archive: Government Documents (Worldwide)", "Internet Archive", "Not built as one source: 18 million "
     "items of every country and licence; its US and Canadian parts are built (FEDLINK, US Government Documents, the "
     "Canadian portal)."),
    ("Internet Archive: Books for People with Print Disabilities", "Internet Archive", "Not built: needs the owner's "
     "own qualifying account. See OWNER_NOTES."),
    ("Internet Archive: Texts to Borrow", "Internet Archive", "Not built: controlled lending only; no program may "
     "download them."),
    ("Internet Archive Books", "Internet Archive", "Built: pub:ia_internetarchivebooks:<subject> (items before 1931 "
     "only)."),
    ("Internet Archive: Medical Heritage Library", "Internet Archive", "Built: pub:ia_medicalheritagelibrary:<subject> "
     "(before 1931; history only)."),
    ("Internet Archive: JSTOR Early Journal Content", "Internet Archive", "Built: pub:ia_jstor_ejc:<subject>."),
    ("Internet Archive: Periodicals", "Internet Archive", "Built: pub:ia_periodicals:<subject> (before 1931)."),
    ("Internet Archive: The Magazine Rack", "Internet Archive", "Not built: magazines, mostly in copyright; its few "
     "open items are in Community Texts and Folkscanomy."),
    ("Internet Archive: Folkscanomy", "Internet Archive", "Built: pub:ia_folkscanomy:<subject> (open licence "
     "address only)."),
    ("Internet Archive: University of Toronto Government Publications", "Internet Archive", "Built: "
     "pub:ia_uoftgovpubs:<subject> (Crown copyright, non-commercial reproduction)."),
    ("Internet Archive: Wellcome Library", "Internet Archive", "Built: pub:ia_wellcomelibrary:<subject> (before "
     "1931)."),
]

# What only the owner can do (not built here).
OWNER_NOTES = [
    ("Internet Archive: Books for People with Print Disabilities (item 2 of the ranked list)", "5.47 million "
     "in-copyright books, open only to qualified print-disabled readers through the Archive's accessible-books "
     "programme. The owner qualifies: sign in at archive.org with the owner's own account after qualifying (through "
     "a certifying authority or the Archive's print-disability programme), then borrow or download the DAISY or EPUB "
     "files for personal reading. Never redistributed, so nothing is built here."),
    ("Bookshare", "Accessible books (DAISY, BRF, EPUB) for people with a print disability, with the owner's own "
     "membership; never redistributable, so nothing is built here."),
]

PIECED = PIECED_SOURCES


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
    ("GALILEO Open Learning Materials (oer.galileo.usg.edu)", "Its OAI-PMH feed answers and lists the CC BY and CC "
     "BY-SA textbooks, but every PDF answers programs with Cloudflare's bot check (403 \"Just a moment...\"), "
     "although robots.txt allows them (checked 2026-11-21): not built."),
    ("Sickle Cell Open Education (sicklecellanaemia.org)", "The domain is now parked and for sale (checked "
     "2026-11-21); the material is gone."),
    ("NTRL, the National Technical Reports Library (ntrl.ntis.gov)", "No robots.txt (allowed), but its search is a "
     "script application with no documented API or bulk download, and its PDFs are reached only through that "
     "search; not built. Agency reports are reached through govinfo and the Internet Archive's FEDLINK collection."),
    ("Global Digital Library website (digitallibrary.io)", "Its own site answers robots.txt with a web page; its "
     "books are built from its Kolibri Studio channel instead (dir:gdl)."),
    ("StoryWeaver website (storyweaver.org.in)", "A script application behind Cloudflare with no documented API; its "
     "stories are built from Pratham Books' StoryWeaver channel on Kolibri Studio instead (dir:storyweaver; the "
     "channel was last published in 2018)."),
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
