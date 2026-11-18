"""Periodicals, journals, reports, news and history for the Digital Accessibility Toolkit's Assistant, as ZIM books.

The textbooks builder (build_textbooks.py) makes one ZIM book per textbook. This module adds publications that come
out again and again (government reports, open-access journal articles, open-licensed news, magazines) and works of
history. Each source is split into downloadable pieces (by year, decade, topic, edition, volume, or state and
decade) so nobody has to download all of it, and every item (article, report, story, document) says its date, so
the Assistant can prefer newer ones.

It reuses the textbooks builder: its Book and Page, its polite fetch (one request at a time per site, a pause,
the cache, robots.txt and its Crawl-delay), its HTML cleaner (_Cleaner, drop_hidden), its licence helpers and its
ZIM writer (write_book, which uses zimwrite.py). build_textbooks.build() hands every "pub:" key to
build_periodicals(), and sources.expand_keys() expands "publications" and "pub:..." words.

Groups (the "group" field of each catalogue entry; the names are in sources.GROUPS):
  reports      Reference, government reports   Congressional Research Service reports (public domain)
  journals     Articles, open-access journals  eLife digests (plain-language summaries, CC BY 4.0); review
                                               articles from the Europe PMC open-access subset (CC BY and CC0 only)
                                               on topics useful to a blind adult
  news         News, open-licensed             Global Voices (CC BY 3.0); Voice of America's own reporting (public
                                               domain; news-agency copy left out); NASA news releases (public
                                               domain); KFF Health News (CC BY-NC-ND 4.0) and The Conversation (CC
                                               BY-ND 4.0), both whole and unchanged. News ages fast: the entries
                                               carry a "note" saying so, and "published" is the newest item's date
  periodicals  Magazines and newsletters       USDA ERS "Amber Waves" (public domain)
  history      Reference, history              the State Department's "Milestones" essays and "Foreign Relations of
                                               the United States" volumes (public domain and CC0); historic
                                               newspapers from Chronicling America (Library of Congress; only those
                                               published more than 95 years ago)

The whole-and-unchanged rule (sources.WHOLE_AND_UNCHANGED, the owner's decision of 2026-11-18): a NoDerivatives
licence (CC BY-ND, CC BY-NC-ND) is used only for works kept WHOLE with their TEXT UNCHANGED, converted in format
only, because Creative Commons 4.0 section 2(a)(4) allows "technical modifications necessary to exercise the
Licensed Rights in all media and formats" and says they "never produce Adapted Material" (CC 2.5 and 3.0: "modifications
as are technically necessary to exercise the rights in other media and formats"). A source with "unchanged": True
is never excerpted, cut, summarised or reworded: each article is kept entire (no partner or "related" boxes are cut
out of it, and headings are never dropped even when empty), its HTML is only cleaned up (menus, scripts and
decorative pictures left out; headings, links and the descriptions of pictures kept), and every page carries the
credit, the licence's name and address, the original address and the line "Converted to an accessible format; the
text is unchanged." Whole articles that are not under the licence (a partner's story, one marked "All Rights
Reserved") are left out entirely, never trimmed. Each site's robots.txt and republishing terms are obeyed too.

Keys (one ZIM book per piece):
  pub:all                      every source, its default pieces (the newspapers have none: ask for them by name)
  pub:reports, pub:journals, pub:news, pub:periodicals, pub:history   every source of that group, default pieces
  pub:<source>                 one source, its default pieces ("pub:crs")
  pub:<source>:<piece>         one piece ("pub:crs:2026", "pub:europepmc_reviews:vision", "pub:amber_waves:2010s",
                               "pub:the_conversation:uk", "pub:frus:frus1961-63v11",
                               "pub:chronicling_america:vermont-1910s")

What was looked at and not built, and why, is in NOT_INCLUDED; the licence lines checked by hand are in
LICENCE_LINES.

Use from the command line (the textbooks workflow calls it through build_textbooks.py):
  python textbooks/periodicals.py pub:crs:2026 --out build/textbooks --cache build/textbooks-cache
  python textbooks/periodicals.py pub:all --list      (only print the piece keys)
"""

import argparse
import csv
import datetime
import gzip
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import mathtext  # noqa: E402
import sources  # noqa: E402

GROUPS = {k: sources.GROUPS[k] for k in ("reports", "journals", "news", "periodicals", "history")}
GROUP_NOTES = {
    "news": "News ages fast: these stories are kept for reference, and the Assistant prefers newer items.",
}
MAX_ITEMS = 2500                 # the most items in one piece (a guard against a source that changed shape)

CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"


# ====================================================================== the sources

def _years(back, today=None):
    """The default pieces of a yearly source: this year and the `back` years before it, newest first."""
    year = (today or datetime.date.today()).year
    return [str(y) for y in range(year, year - back - 1, -1)]


# Topics of the Europe PMC review articles: key -> (name, the words searched in titles and abstracts).
EPMC_TOPICS = {
    "vision": ("Blindness and low vision", '"visual impairment" OR blindness OR "low vision" OR "vision loss" OR '
               'glaucoma OR "macular degeneration" OR "diabetic retinopathy"'),
    "hearing": ("Hearing and deafblindness", '"hearing loss" OR deafblind* OR tinnitus OR "cochlear implant"'),
    "assistive": ("Disability and assistive technology", '"assistive technology" OR "people with disabilities" OR '
                  '"accessibility" OR "screen reader"'),
    "diabetes": ("Diabetes", 'diabetes'),
    "heart": ("Heart and blood pressure", '"heart disease" OR hypertension OR "blood pressure" OR stroke'),
    "mental_health": ("Mental health", 'depression OR anxiety OR "mental health" OR loneliness'),
    "ageing": ("Healthy ageing", '"healthy ageing" OR "healthy aging" OR "older adults" OR falls OR dementia'),
    "nutrition": ("Food and nutrition", 'nutrition OR diet OR "physical activity" OR exercise'),
    "sleep": ("Sleep", 'sleep OR insomnia OR "circadian rhythm"'),
}

US_GOV, US_GOV_URL = sources.US_GOV, sources.US_GOV_URL

SOURCES = {
    "crs": dict(
        group="reports", driver="crs", series_title="Congressional Research Service reports",
        subject="US law, policy and government", publisher="Congressional Research Service, Library of Congress "
        "(from EveryCRSReport.com)", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
        source="https://www.everycrsreport.com/",
        description="Reports the Congressional Research Service writes for the US Congress: short In Focus briefs, "
                    "Insights, Legal Sidebars and full reports on law, health, benefits, the economy, science and "
                    "world affairs. One book per year of the reports' latest update.",
        notice="CRS Reports, as a work of the United States Government, are not subject to copyright protection in "
               "the United States (the Disclaimer printed in every CRS report). A report may include copyrighted "
               "pictures or material from a third party; the pictures are left out of this book. CRS reports are "
               "written for Members of Congress and should not be relied upon for other purposes than public "
               "understanding.",
        changes="made into web pages with the pictures left out",
        pieces=lambda today: _years(3, today), piece_rule=r"^(19|20)\d\d$"),
    "amber_waves": dict(
        group="periodicals", driver="amber_waves", series_title="Amber Waves (USDA Economic Research Service)",
        subject="Food, farming and rural America", publisher="Economic Research Service, US Department of "
        "Agriculture", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
        source="https://www.ers.usda.gov/amber-waves",
        description="The Economic Research Service's magazine on food prices and spending, nutrition programmes, "
                    "farming, trade and rural life. One book per decade.",
        notice="A work of the US Department of Agriculture (US government work, not under copyright in the "
               "United States). Charts and photographs are left out.",
        changes="made into web pages with the site's menus, charts and photographs left out",
        pieces=lambda today: ["2020s", "2010s", "2000s"], piece_rule=r"^(19|20)\d0s$"),
    "elife_digests": dict(
        group="journals", driver="elife", series_title="eLife digests (plain-language summaries of research)",
        subject="Science and medicine explained", publisher="eLife Sciences Publications", country="International",
        licence="CC BY 4.0", licence_url=CC_BY_4, source="https://elifesciences.org/digests",
        description="Short plain-language summaries (digests) of new research papers in biology and medicine, "
                    "written by eLife's editors for everyone. One book per year.",
        changes="made into web pages with the pictures left out (their captions kept)",
        # api.elifesciences.org's robots.txt says "Disallow: /" to every crawler; this is eLife's documented public
        # API for programs (no key), read at one request a second; see the module's report and LICENCE_LINES.
        api_robots_exempt=True,
        pieces=lambda today: _years(4, today), piece_rule=r"^20\d\d$"),
    "europepmc_reviews": dict(
        group="journals", driver="europepmc", series_title="Open-access health reviews",
        subject="Health and medicine", publisher="The articles' authors and journals (from Europe PMC's open-access "
        "subset)", country="International", licence="CC BY", licence_url=CC_BY_4,
        source="https://europepmc.org/",
        description="Review articles from open-access journals (Creative Commons Attribution or CC0 only), newest "
                    "first, on one topic. Each article's authors, journal, date, DOI and own licence are on its "
                    "page.",
        changes="made into web pages with the figures and the reference lists left out (figure captions kept)",
        pieces=lambda today: list(EPMC_TOPICS), piece_rule="^(" + "|".join(EPMC_TOPICS) + ")$",
        per_piece=150, years_back=5),
    "global_voices": dict(
        group="news", driver="wordpress", site="https://globalvoices.org", series_title="Global Voices",
        subject="World news and citizen media", publisher="Global Voices", country="International",
        licence="CC BY 3.0", licence_url="https://creativecommons.org/licenses/by/3.0/",
        source="https://globalvoices.org/",
        description="Stories by Global Voices' volunteer writers and translators about people and communities "
                    "around the world, often ones the big news outlets miss. One book per year.",
        changes="made into web pages with the pictures left out (their descriptions kept); articles republished "
                "from partner outlets are left out",
        licence_page="https://globalvoices.org/",
        licence_text=r"licensed as\s*<a[^>]*creativecommons\.org/licenses/by/3\.0",
        # Articles Global Voices republishes from partner outlets are under those outlets' terms, not CC BY.
        skip=r"originally (?:been )?published|\brepublished\b|is being (?:re)?published|"
             r"content[- ](?:sharing|partnership) agreement|produced (?:as part of|by|for|with)",
        skip_reason="republished from partner outlets (they are under those outlets' terms)",
        pieces=lambda today: _years(1, today), piece_rule=r"^20\d\d$"),
    "kff_health_news": dict(
        group="news", driver="wordpress", site="https://kffhealthnews.org", series_title="KFF Health News",
        subject="US health news", publisher="KFF Health News", country="United States",
        licence="CC BY-NC-ND 4.0", licence_url="https://creativecommons.org/licenses/by-nc-nd/4.0/", unchanged=True,
        source="https://kffhealthnews.org/",
        description="Stories by KFF Health News, the national newsroom on health policy, insurance, Medicare and "
                    "Medicaid, drug prices and public health, each whole and unchanged. One book per year.",
        notice="KFF Health News is a national newsroom that produces in-depth journalism about health issues and is "
               "one of the core operating programs at KFF (its standard attribution). Its stories are shared under "
               "CC BY-NC-ND 4.0; stories marked \"All Rights Reserved\" and stories from other outlets are left out.",
        page_credit="This story was produced by KFF Health News. KFF Health News is a national newsroom that "
                    "produces in-depth journalism about health issues and is one of the core operating programs at KFF "
                    "— the independent source for health policy research, polling, and journalism.",
        licence_page="https://kffhealthnews.org/syndication/",
        licence_text=r"Attribution-NonCommercial-NoDerivatives 4\.0 International \(CC BY-NC-ND 4\.0\)",
        skip=r"All Rights Reserved|reprinted with permission|republished (?:with permission|from)|"
             r"originally (?:been )?published (?:by|in|on)",
        skip_reason="marked \"All Rights Reserved\" or published first by another outlet",
        pieces=lambda today: _years(1, today), piece_rule=r"^20\d\d$"),
    "nasa_news": dict(
        group="news", driver="wordpress", site="https://www.nasa.gov", rest_base="press-release",
        series_title="NASA news releases", subject="Space, science and NASA missions",
        publisher="National Aeronautics and Space Administration (NASA)", country="United States",
        licence=US_GOV, licence_url=US_GOV_URL, source="https://www.nasa.gov/news/releases/latest/",
        description="NASA's official news releases (a US government work). One book per year.",
        notice="A work of NASA (US government work, not under copyright in the United States). NASA's insignia and "
               "logos are not in the public domain; the pictures are left out.",
        changes="made into web pages with the pictures left out (their descriptions kept)",
        licence_page="https://www.nasa.gov/nasa-brand-center/images-and-media/",
        licence_text=r"generally are not subject to copyright in the United States",
        pieces=lambda today: _years(1, today), piece_rule=r"^20\d\d$"),
    "the_conversation": dict(
        group="news", driver="atom", series_title="The Conversation",
        subject="News and analysis by academic experts", publisher="The Conversation", country="International",
        licence="CC BY-ND 4.0", licence_url="https://creativecommons.org/licenses/by-nd/4.0/", unchanged=True,
        source="https://theconversation.com/",
        feed="https://theconversation.com/{piece}/articles.atom", rights=r"attribution, no derivatives",
        credit="This article is republished from The Conversation under a Creative Commons license.",
        description="Articles written by university researchers and edited by journalists, from one edition of The "
                    "Conversation (its latest articles, as its news feed lists them), each whole and unchanged.",
        notice="Republished from The Conversation under a Creative Commons licence (CC BY-ND 4.0), whole and "
               "unchanged. Each article names its authors and their institutions. Photographs are left out (The "
               "Conversation does not license them for republication).",
        licence_page="https://theconversation.com/us/republishing-guidelines",
        licence_text=r"publish all our work under a\s*(?:<[^>]+>\s*)*Creative Commons",
        pieces=lambda today: ["us", "uk", "au", "ca", "africa", "global"],
        piece_rule=r"^(us|uk|au|ca|africa|global|nz|europe)$"),
    "voa": dict(
        group="news", driver="voa", series_title="Voice of America news",
        subject="US and world news", publisher="Voice of America (VOA)", country="United States",
        licence="Public domain (VOA's own reporting)", licence_url="https://www.voanews.com/p/5338.html",
        source="https://www.voanews.com/",
        description="Recent news stories written by Voice of America's own reporters (the last 60 days). Stories "
                    "that use material from news agencies (AP, Reuters, AFP) are left out, as VOA's terms ask.",
        notice="All text, audio and video material produced exclusively by the Voice of America is in the public "
               "domain (VOA's copyright statement). Credit: voanews.com, Voice of America.",
        changes="made into web pages with the pictures, videos and site menus left out; stories with news-agency "
                "material left out",
        licence_page="https://www.voanews.com/p/5338.html",
        licence_text=r"produced exclusively by the Voice of America is in the public domain",
        pieces=lambda today: ["recent"], piece_rule=r"^recent$", days=60),
    "state_milestones": dict(
        group="history", driver="milestones", series_title="Milestones in the History of U.S. Foreign Relations",
        subject="US history and foreign relations", publisher="Office of the Historian, US Department of State",
        country="United States", licence="CC0 1.0", licence_url="https://creativecommons.org/publicdomain/zero/1.0/",
        source="https://history.state.gov/milestones", repo="https://github.com/HistoryAtState/milestones",
        description="Short essays by the State Department's Office of the Historian on the milestones of US "
                    "foreign relations from 1750 to 2000, one part per period. (The Office has retired the series: "
                    "it is kept for reference and no longer updated.)",
        notice="A work of the United States government (public domain in the United States) and dedicated to the "
               "public domain worldwide (CC0 1.0), as the Office of the Historian's repository states.",
        changes="made into web pages with the pictures left out",
        date_label="Last revised", pieces=lambda today: ["all"], piece_rule=r"^all$"),
    "frus": dict(
        group="history", driver="frus", series_title="Foreign Relations of the United States",
        subject="US diplomatic history (documents)", publisher="Office of the Historian, US Department of State",
        country="United States", licence="CC0 1.0", licence_url="https://creativecommons.org/publicdomain/zero/1.0/",
        source="https://history.state.gov/historicaldocuments", repo="https://github.com/HistoryAtState/frus",
        description="The official documentary record of US foreign policy: one volume per book, every document "
                    "with its date, place and source note.",
        notice="A work of the United States government (public domain in the United States) and dedicated to the "
               "public domain worldwide (CC0 1.0), as the Office of the Historian's repository states.",
        changes="made into web pages, one per document, with its notes after it",
        date_label="Dated",
        # A few well-known volumes by default; any volume of the series is one key (pub:frus:frus1964-68v01).
        pieces=lambda today: ["frus1945Malta", "frus1945Berlinv02", "frus1961-63v11", "frus1969-76v01"],
        piece_rule=r"^frus[0-9A-Za-z-]+$"),
    "chronicling_america": dict(
        group="history", driver="chronam", series_title="Historic American newspapers (Chronicling America)",
        subject="Historic newspapers", publisher="Library of Congress and the National Digital Newspaper Program",
        country="United States", licence="Public domain (published before 1931)",
        licence_url="https://www.loc.gov/collections/chronicling-america/about-this-collection/rights-and-access/",
        source="https://www.loc.gov/collections/chronicling-america/",
        description="A sample of English-language newspaper issues of one state and one decade (one issue a "
                    "month), every page's machine-read (OCR) text, from the Library of Congress. The OCR text has "
                    "the mistakes of the machine reading.",
        notice="The Library of Congress believes that the newspapers in Chronicling America are in the public domain "
               "or have no known copyright restrictions; newspapers published in the United States more than 95 "
               "years ago are in the public domain in their entirety, and only those are kept here.",
        changes="the machine-read text of each page, made into web pages",
        date_label="Published", per_month=1,
        # Huge: no default pieces. One key per state and decade: pub:chronicling_america:vermont-1910s.
        pieces=lambda today: [], piece_rule=r"^[a-z]+(?:-[a-z]+)*-1[6-9][0-9]0s$"),
}

# "Public domain (published before 1931)" is the US public domain of old works (95 years after publication).
PUBLIC_DOMAIN_OLD = "Public domain (published before 1931)"

for _name, _spec in SOURCES.items():
    _spec["name"] = _name

# "Public domain (VOA's own reporting)" is not one of sources.ALLOWED's names; it is treated as the US government
# public domain (VOA is a US government broadcaster; 17 U.S.C. 105).
LICENCE_ALIASES = {"Public domain (VOA's own reporting)": US_GOV}

LICENCE_LINES = {
    "crs": "Each CRS report's Disclaimer (for example IF10719, 2026-11-17): \"CRS Reports, as a work of the United "
           "States Government, are not subject to copyright protection in the United States. Any CRS Report may "
           "be reproduced and distributed in its entirety without permission from CRS. However, as a CRS Report "
           "may include copyrighted images or material from a third party, you may need to obtain the permission "
           "of the copyright holder if you wish to copy or otherwise use copyrighted material.\" EveryCRSReport.com "
           "offers its bulk list (reports.csv) and every report's HTML for download; it has no robots.txt.",
    "amber_waves": "A work of the USDA Economic Research Service (17 U.S.C. 105). www.ers.usda.gov/robots.txt: "
                   "\"User-agent: * Allow: /\". No separate licence page was found on ers.usda.gov.",
    "elife_digests": "Each research article in eLife's API (/articles/<id>): copyright.license \"CC-BY-4.0\", "
                     "statement \"This article is distributed under the terms of the Creative Commons Attribution "
                     "License\"; each digest is checked against its article's licence at every build. "
                     "api.elifesciences.org/robots.txt says \"User-agent: * Disallow: /\" (meant for crawlers; the "
                     "API is eLife's documented public interface for programs).",
    "europepmc_reviews": "Each article's own <license> in its full text (for example PMC13194245: \"This article "
                         "is licensed under a Creative Commons Attribution 4.0 International License\"); only CC BY "
                         "(any version) and CC0 are kept. www.ebi.ac.uk/robots.txt does not restrict the Europe PMC "
                         "REST service.",
    "global_voices": "globalvoices.org footer: \"This site is licensed as Creative Commons Attribution 3.0\" "
                     "(creativecommons.org/licenses/by/3.0/). robots.txt: \"Crawl-delay: 10\", only /wp-admin/, "
                     "/wp-includes/ and /site/ disallowed; the WordPress REST API (/wp-json/) is used.",
    "voa": "www.voanews.com/p/5338.html, Copyright Statement: \"All text, audio and video material produced "
           "exclusively by the Voice of America is in the public domain. ... voanews.com content may also contain "
           "... copyrighted material that is licensed for use in VOA programming only.\" and \"VOA has individual "
           "licenses from Agence France Presse (AFP), the Associated Press (AP) and Reuters\" (so any story naming "
           "them is left out). robots.txt allows /a/ (the stories).",
    "kff_health_news": "kffhealthnews.org/syndication/: \"We share all stories and photographs produced by KFF "
                       "Health News staff under a Creative Commons license ... Attribution-NonCommercial-NoDerivatives "
                       "4.0 International (CC BY-NC-ND 4.0)\"; \"If a story is labeled 'All Rights Reserved,' KFF "
                       "Health "
                       "News cannot grant permission to republish that item\" (left out); asks to preserve all story "
                       "hyperlinks and the tagline (kept: whole and unchanged). robots.txt: \"Disallow:\" (nothing). "
                       "Note: it asks to be asked before use \"in commercial products such as academic textbooks\".",
    "nasa_news": "www.nasa.gov/nasa-brand-center/images-and-media/: NASA content \"generally are not subject to "
                 "copyright in the United States\"; \"The NASA Insignia, Logotype, identifiers, and imagery are not in "
                 "the public domain\" (pictures left out). robots.txt: \"User-agent: * Allow: /\".",
    "the_conversation": "theconversation.com/us/republishing-guidelines: \"We believe in the free flow of information "
                        "and publish all our work under a Creative Commons — Attribution/No derivatives license\"; "
                        "each feed entry: <rights>Licensed as Creative Commons – attribution, no derivatives."
                        "</rights>. It asks for its page view counter \"when republishing online\" (a ZIM book is "
                        "read offline; the counter's picture is in each article unchanged but never loaded) and says "
                        "photographs need their own permission (left out). robots.txt allows the articles.",
    "state_milestones": "github.com/HistoryAtState/milestones LICENSE.md: \"As a work of the United States "
                        "government, this project is in the public domain within the United States of America. "
                        "Additionally, we waive copyright and related rights in the work worldwide through the CC0 1.0 "
                        "Universal public domain dedication.\" Read with git (history.state.gov asks Crawl-delay 20).",
    "frus": "github.com/HistoryAtState/frus LICENSE.md: the same words as Milestones (US government work, CC0 1.0).",
    "chronicling_america": "Each issue's rights statement (loc.gov API): \"The Library of Congress believes that the "
                           "newspapers in Chronicling America are in the public domain or have no known copyright "
                           "restrictions. Newspapers published in the United States more than 95 years ago are in the "
                           "public domain in their entirety.\" Only issues published before 1931 are kept. "
                           "www.loc.gov/robots.txt allows /collections/ and /resource/.",
}

# Looked at (2026-11-18) and not built, with the reason.
NOT_INCLUDED = [
    ("GAO reports and WatchBlog (gao.gov)", "Public domain, but www.gao.gov refuses automated requests (Akamai "
     "\"Access Denied\", robots.txt included)."),
    ("Congressional Budget Office (cbo.gov)", "Public domain, but cbo.gov answers automated requests with a bot check "
     "(\"Please enable JS\")."),
    ("BLS Occupational Outlook Handbook (bls.gov)", "Public domain and very useful, but www.bls.gov refuses "
     "automated requests (\"Access Denied\", robots.txt included). Its data API needs a sign-up key and does not "
     "carry the handbook's text."),
    ("NIH News in Health (newsinhealth.nih.gov)", "Public domain, but the site refuses automated requests (403, "
     "robots.txt included)."),
    ("FDA Consumer Updates (fda.gov)", "Public domain and allowed by robots.txt (Crawl-delay 30); not built yet: "
     "its list page is filled by a script, so each update's address would have to come from the sitemap."),
    ("NASA magazines and education pages (nasa.gov)", "Mostly not under copyright, but NASA's pages mix in "
     "third-party pictures and its insignia; not built yet (the WordPress API works and robots.txt allows it)."),
    ("Federal Reserve consumer publications", "No licence or public-domain statement was found on its consumer "
     "pages; not checked one by one."),
    ("UK House of Commons Library briefings (Open Parliament Licence)", "commonslibrary.parliament.uk answers "
     "automated requests with a bot check (Cloudflare \"Just a moment\"); the Open Parliament Licence would be "
     "allowed."),
    ("ONS bulletins (Open Government Licence)", "Allowed (\"published under the Open Government Licence\"), not "
     "built yet: the bulletins are mostly charts and tables."),
    ("Library of Parliament HillStudies (Canada)", "No open licence was found on lop.parl.ca; the House of Commons' "
     "notices speak of parliamentary privilege and permission to reproduce."),
    ("Statistics Canada (Open Licence)", "www150.statcan.gc.ca refuses automated requests to its licence page "
     "(403)."),
    ("Australian Parliamentary Library", "www.aph.gov.au blocks automated requests (\"Page Blocked by WAF\")."),
    ("Australian Bureau of Statistics (CC BY 4.0)", "Allowed (\"All material presented on this website is provided "
     "under a Creative Commons Attribution 4.0 International licence\"); not built yet: its releases are mostly "
     "tables and charts."),
    ("New Zealand Parliament research papers and Irish government publications", "No licence page could be "
     "confirmed automatically (404); not checked by hand yet."),
    ("Cochrane plain-language summaries", "Copyright of Cochrane and Wiley; not openly licensed."),
    ("PLOS journals", "CC BY; their review articles are included through Europe PMC's open-access subset (the same "
     "articles, with each one's licence checked), so PLOS is not read separately."),
    ("arXiv", "Most papers are not under an open licence that allows changes, and few are useful to a general "
     "reader; left out."),
    ("Disability Studies Quarterly and other DOAJ journals", "Each journal's and article's licence must be checked "
     "one by one (many are CC BY-NC-ND); not built yet."),
    ("Journal of Visual Impairment & Blindness; British Journal of Visual Impairment", "Copyright of their "
     "publishers (SAGE): not openly licensed."),
    ("Wikinews", "Wikinews was closed and made read-only by the Wikimedia Foundation in 2026; it is not in the "
     "Kiwix catalogue. Its archive (CC BY 2.5) could be made into one book later."),
    ("ProPublica", "CC BY-NC-ND, but its \"Steal Our Stories\" terms say: \"You can't republish our material "
     "wholesale, or automatically; you need to select stories to be republished individually\", and ask for its "
     "PixelPing tag: left out (stories could be added one by one, chosen by hand)."),
    ("CalMatters", "Not a Creative Commons licence: its own republishing terms (calmatters.org/about/republish/: "
     "credit, \"Do not edit the article\", \"Do not sell our stories\"); left out until CalMatters agrees to an "
     "offline accessible copy."),
    ("The Conversation's older articles", "Its news feed lists only each edition's latest 50 articles and has no "
     "further pages; the archive would need its sitemaps (not checked yet)."),
    ("Wikinews (as news)", "Closed and read-only since 2026 and not in the Kiwix catalogue; its archive (CC BY 2.5) "
     "could become one history book later."),
    # history (looked at on 2026-11-18)
    ("US Army Center of Military History books (history.army.mil)", "Public domain, but history.army.mil refuses "
     "automated requests (403, robots.txt included). Copies on the Internet Archive could be added to sources.PDF_DOCS "
     "one by one (histories only, never combat manuals)."),
    ("Naval History and Heritage Command (history.navy.mil)", "Public domain, but its secure connection could not be "
     "checked from the build machine (certificate error); not built yet."),
    ("House history (history.house.gov)", "Public domain, but its robots.txt says \"User-agent: * Disallow: /\"."),
    ("Senate Historical Office (senate.gov)", "Its robots.txt could not be read (the site answers with a web page); "
     "not built."),
    ("Federal Judicial Center history (fjc.gov)", "Public domain and allowed (Crawl-delay 30); not built yet."),
    ("National Park Service history publications", "Public domain on nps.gov, but scattered over park pages; the big "
     "collection (npshistory.com) is not an official NPS site. Not built yet."),
    ("Library of Congress essays", "Not built yet; the newspapers (Chronicling America) are."),
    ("Te Ara, the Encyclopedia of New Zealand", "CC BY-NC 3.0 NZ would be allowed, but teara.govt.nz refuses "
     "automated requests (403, robots.txt included)."),
    ("Dictionary of Irish Biography", "\"Copyright Dictionary of Irish Biography\"; no open licence was found (and "
     "Crawl-delay 30)."),
    ("UK National Archives education resources", "Open Government Licence, but its robots.txt says \"Content-Signal: "
     "ai-train=no, search=yes, ai-input=no\": the Assistant would use the text as AI input, so it is left out."),
    ("Dictionary of Canadian Biography and Australian Dictionary of Biography", "Copyright of their publishers "
     "(University of Toronto/Université Laval; Australian National University): not openly licensed."),
    ("Wikisource and Project Gutenberg history books", "Already in the Kiwix library."),
    ("Low-tech Magazine", "Already in the Kiwix library (solar.lowtechmagazine.com_mul_all), so not built again."),
    ("VOA Learning English", "Already in the Kiwix library (voa_learning_en_all)."),
    ("Make:, Hackaday, Practical Action", "Copyright of their publishers, or no licence stated."),
]


# ====================================================================== keys

def expand_keys(words, today=None):
    """The one-piece keys ("pub:crs:2026") of a list of words ("pub:all", "pub:news", "pub:crs", "pub:crs:2026")."""
    out = []
    for w in words:
        parts = w.split(":")
        if parts[0] != "pub" or len(parts) < 2:
            continue
        what = parts[1]
        if len(parts) == 3:
            spec = SOURCES.get(what)
            if spec and re.match(spec["piece_rule"], parts[2]):
                out.append(w)
            continue
        if what == "all":
            names = list(SOURCES)
        elif what in GROUPS:
            names = [n for n, s in SOURCES.items() if s["group"] == what]
        elif what in SOURCES:
            names = [what]
        else:
            continue
        for name in names:
            out += [f"pub:{name}:{p}" for p in SOURCES[name]["pieces"](today)]
    return list(dict.fromkeys(out))


# ====================================================================== helpers

def clean(fragment, base, whole=False):
    """A web page fragment as the plain HTML the books use (the textbooks' cleaner): headings one level down from
    <h1> (the page has its own), no menus, scripts, hidden marks, empty links or empty blocks; pictures become
    "Picture: " and their description, or are left out when they have none. Only the format changes, never the
    words; with whole=False (not a no-changes licence) headings left with nothing under them are dropped too."""
    body = B._Cleaner({}, base).clean(B.drop_hidden(fragment or ""))
    body = re.sub(r"<(/?)h1>", r"<\1h2>", body)
    body = re.sub(r'<a href="[^"]*">\s*</a>', "", body)
    for _ in range(2):
        body = re.sub(r"<(p|div|span|li|section|strong|em)>\s*</\1>", "", body)
    body = re.sub(r"[ \t]*\n\s*", "\n", re.sub(r"[ \t]{2,}", " ", body))
    return (body if whole else drop_empty_headings(body)).strip()


def drop_empty_headings(body):
    """The HTML without headings that have nothing under them (followed at once by a heading of the same or a
    higher level, or by the end): what is left of a reference list or of supplementary files."""
    pattern = re.compile(r"<h([2-6])>(?:(?!</h[2-6]>).)*?</h\1>\s*(?=<h([1-6])>|$)", re.S)
    while True:
        m = next((m for m in pattern.finditer(body) if m.group(2) is None or int(m.group(2)) <= int(m.group(1))),
                 None)
        if m is None:
            return body
        body = body[:m.start()] + body[m.end():]


def div_inner(text, start):
    """The HTML inside the element that the regular expression start opens (such as '<div class="wsw">'), up to
    its own closing tag (nested elements of the same name are counted); "" when start is not found."""
    m = re.search(start, text)
    if not m:
        return ""
    tag = re.match(r"<(\w+)", m.group(0)).group(1)
    depth = 1
    for t in re.finditer(rf"<(/?){tag}\b[^>]*>", text[m.end():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return text[m.end():m.end() + t.start()]
    return text[m.end():]


def month_unit(date):
    """The contents heading of an item's month ("2026-11-17" -> "November 2026"; "" when there is no month)."""
    m = re.match(r"(\d{4})-(\d\d)", date or "")
    if not m:
        return date[:4] if date else ""
    return f"{datetime.date(int(m.group(1)), int(m.group(2)), 1):%B %Y}"


def json_ld(page_text):
    """The schema.org objects (JSON-LD) of a web page, as a list of dicts."""
    out = []
    for raw in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', page_text, re.S):
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        for d in data if isinstance(data, list) else data.get("@graph", [data]):
            if isinstance(d, dict):
                out.append(d)
    return out


def robots_ok(spec, url, cache):
    """True when the site's robots.txt allows url (or the source is a documented public API, api_robots_exempt)."""
    return spec.get("api_robots_exempt") or B.allowed_by_robots(url, cache)


def licence_still_stated(spec, cache):
    """True when the source's licence page still says what was checked by hand (or it has none to check)."""
    if not spec.get("licence_page"):
        return True
    try:
        text = B.fetch(spec["licence_page"], None)
    except (urllib.error.URLError, OSError):
        return False
    words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())
    return bool(re.search(spec["licence_text"], text) or re.search(spec["licence_text"], words))


def item(url, title, date, body, unit="", byline="", licence="", licence_url=""):
    """One article of a piece: its original address, title, publication date ("YYYY-MM-DD" or shorter), cleaned
    body, contents heading, byline, and its own licence when it differs between articles."""
    return {"url": url, "title": " ".join((title or "").split()) or url, "date": date, "body": body, "unit": unit,
            "byline": byline, "licence": licence, "licence_url": licence_url}


# ====================================================================== Congressional Research Service

CRS_SITE = "https://www.everycrsreport.com/"
CRS_KINDS = [("IF", "In Focus (two-page briefs)"), ("IN", "Insights (short analyses)"),
             ("LSB", "Legal Sidebars"), ("", "Reports")]


def crs_kind(number):
    """The contents heading of a CRS report number ("IF10719" -> "In Focus (two-page briefs)")."""
    return next(name for prefix, name in CRS_KINDS if number.startswith(prefix))


def crs_items(spec, piece, cache, left_out, today):
    """The CRS reports whose latest version came out in the year piece, from EveryCRSReport's reports.csv (read
    fresh every time) and each report's HTML (kept in the cache: its file name has its checksum)."""
    rows = list(csv.DictReader(io.StringIO(B.fetch(CRS_SITE + "reports.csv", None))))
    rows = [r for r in rows if r.get("latestPubDate", "").startswith(piece) and r.get("latestHTML")]
    rows.sort(key=lambda r: r["latestPubDate"], reverse=True)
    out, failed = [], 0
    for r in rows[:spec.get("limit", MAX_ITEMS)]:
        url = CRS_SITE + r["latestHTML"]
        if not robots_ok(spec, url, cache):
            failed += 1
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        title = r["title"]
        body = clean(text, url)
        body = re.sub(r"<div>\s*" + re.escape(B.esc(title)) + r"\s*</div>", "", body, count=1)
        out.append(item(f"{CRS_SITE}reports/{r['number']}.html", f"{title} ({r['number']})",
                        B.iso_date(r["latestPubDate"]), body, crs_kind(r["number"])))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} reports could not be "
                         "read or are not allowed by the site's robots.txt."})
    order = [name for _p, name in CRS_KINDS]
    out.sort(key=lambda i: (order.index(i["unit"]), [-ord(c) for c in i["date"]]))
    return out


# ====================================================================== Amber Waves (USDA ERS)

ERS_SITE = "https://www.ers.usda.gov"
# Where an article's text ends: the "Get Amber Waves delivered" box, the other site blocks, or the page footer.
AMBER_END = r'<div\b[^>]*\bblock-block-content|<div\b[^>]*\bblock-ers-|<footer\b|</article>'
AMBER_URL = re.compile(r"^https://www\.ers\.usda\.gov/amber-waves/((?:19|20)\d\d)/([a-z]+)/[a-z0-9-]+$")


def amber_waves_items(spec, piece, cache, left_out, today):
    """The Amber Waves articles of the decade piece ("2010s"), found in the ERS sitemap (read fresh), newest
    first, one contents heading per year."""
    urls = []
    for page in range(1, 30):
        try:
            text = B.fetch(f"{ERS_SITE}/sitemap.xml?page={page}", None)
        except urllib.error.HTTPError:
            break
        locs = [html.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)]
        if not locs:
            break
        urls += [u for u in locs if AMBER_URL.match(u) and u not in urls]
    decade = int(piece[:4])
    urls = [u for u in urls if decade <= int(AMBER_URL.match(u).group(1)) < decade + 10]
    urls.sort(key=lambda u: B.iso_date("{1} {0}".format(*AMBER_URL.match(u).groups())), reverse=True)
    out, failed = [], 0
    for url in urls[:spec.get("limit", MAX_ITEMS)]:
        year, month = AMBER_URL.match(url).groups()
        if not robots_ok(spec, url, cache):
            failed += 1
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        m = re.search(r"<h1\b", text)
        body = text[m.start():] if m else text
        end = re.search(AMBER_END, body)
        body = clean(re.sub(r"<h1\b[^>]*>.*?</h1>", "", body[:end.start()] if end else body, count=1, flags=re.S),
                     url)
        day = re.search(r"<li>\s*(\d{1,2})/(\d{1,2})/((?:19|20)\d\d)\s*</li>", text)   # "2/23/2026" under the byline
        when = f"{day.group(3)}-{int(day.group(1)):02d}-{int(day.group(2)):02d}" if day else \
            B.iso_date(f"{month} {year}")
        out.append(item(url, B.first_heading(text), when, body, year))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} articles could not be "
                         "read or are not allowed by the site's robots.txt."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== eLife digests

ELIFE_API = "https://api.elifesciences.org"
ELIFE_LICENCES = {"CC-BY-4.0": ("CC BY 4.0", CC_BY_4),
                  "CC0-1.0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/")}


def elife_blocks(blocks, depth=2):
    """The HTML of eLife's content blocks (paragraph, section, list, quote, image: its caption as "Picture: ")."""
    out = []
    for b in blocks or []:
        kind = b.get("type")
        if kind == "paragraph":
            out.append(f"<p>{b.get('text', '')}</p>")
        elif kind == "section":
            out.append(f"<h{depth}>{B.esc(b.get('title', ''))}</h{depth}>" + elife_blocks(b.get("content"),
                                                                                       min(depth + 1, 6)))
        elif kind == "list":
            tag = "ol" if b.get("prefix") in ("number", "alpha-lower", "alpha-upper", "roman-lower") else "ul"
            items = "".join(f"<li>{x if isinstance(x, str) else elife_blocks(x)}</li>" for x in b.get("items", []))
            out.append(f"<{tag}>{items}</{tag}>")
        elif kind == "quote":
            out.append(f"<blockquote>{elife_blocks(b.get('text'))}</blockquote>")
        elif kind == "image":
            image = b.get("image", {})
            words = " ".join(re.sub(r"<[^>]+>", " ", c.get("text", "")) for c in b.get("caption", [])
                             if c.get("type") == "paragraph")
            words = " ".join(html.unescape(f"{image.get('alt', '')} {words}").split())
            if words:
                out.append(f"<p>Picture: {B.esc(words)}</p>")
    return "".join(out)


def elife_items(spec, piece, cache, left_out, today):
    """The eLife digests published in the year piece, from eLife's public API (newest first, 100 a page). Each
    digest's research article is read to check its licence (CC BY 4.0 or CC0); a digest whose article has another
    licence is left out."""
    year, out, wrong = piece, [], 0
    for page in range(1, 100):
        data = json.loads(B.fetch(f"{ELIFE_API}/digests?per-page=100&page={page}&order=desc", None))
        found = data.get("items", [])
        if not found:
            break
        for d in found:
            when = B.iso_date(d.get("published", ""))
            if not when.startswith(year):
                continue
            related = (d.get("relatedContent") or [{}])[0]
            article_id = related.get("id") or d["id"]
            try:
                article = json.loads(B.fetch(f"{ELIFE_API}/articles/{article_id}", cache))
            except (urllib.error.URLError, OSError, ValueError):
                wrong += 1
                continue
            lic = ELIFE_LICENCES.get((article.get("copyright") or {}).get("license", ""))
            if not lic:
                wrong += 1
                continue
            about = article.get("title") or related.get("title", "")
            authors = article.get("authorLine") or related.get("authorLine", "")
            doi = article.get("doi") or related.get("doi", "")
            body = (f"<p><em>{B.esc(d.get('impactStatement', ''))}</em></p>" if d.get("impactStatement") else "") + \
                elife_blocks(d.get("content"))
            body = clean(body, "https://elifesciences.org/")
            body += (f"<p>This digest explains the research article \"{B.esc(re.sub(r'<[^>]+>', '', about))}\" by "
                     f"{B.esc(authors)}, eLife{(', DOI ' + B.esc(doi)) if doi else ''}.</p>")
            subjects = ", ".join(s.get("name", "") for s in d.get("subjects", []))
            out.append(item(f"https://elifesciences.org/digests/{d['id']}", d.get("title", ""), when, body,
                            month_unit(when), byline=f"Subjects: {subjects}" if subjects else "",
                            licence=lic[0], licence_url=lic[1]))
        if all(B.iso_date(d.get("published", ""))[:4] < year for d in found) or len(found) < 100:
            break                                            # newest first: the rest are older (or no more pages)
        if len(out) >= spec.get("limit", MAX_ITEMS):
            out = out[:spec.get("limit", MAX_ITEMS)]
            break
    if wrong:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{wrong} digests were left out: "
                         "their article's licence is not CC BY 4.0 or CC0, or it could not be read."})
    return out


# ====================================================================== Europe PMC open-access review articles

EPMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
SUMMARY_TYPES = {"summary", "executive-summary", "author-summary", "plain-language-summary", "lay-summary"}


def _tag(el):
    """An element's tag without its namespace."""
    return el.tag.rsplit("}", 1)[-1] if isinstance(el.tag, str) else ""


def _words(el):
    """All the text of an element on one line."""
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def jats_licence(root):
    """(short licence, address) of a JATS article from its <permissions>, ("", "") when it states none."""
    for lic in root.iter():
        if _tag(lic) != "license":
            continue
        hrefs = [v for k, v in lic.attrib.items() if k.endswith("href")]
        hrefs += [_words(x) for x in lic.iter() if _tag(x) == "license_ref"]
        url = next((h for h in hrefs if "creativecommons.org" in h), "")
        return B.licence_short(_words(lic), url), url.replace("http://", "https://")
    return "", ""


def open_enough(short):
    """True for the licences the journals group keeps: CC BY (any version, also IGO) and CC0, nothing else."""
    return short == "CC0 1.0" or bool(re.fullmatch(r"CC BY( \d\.\d)?( IGO)?", short or ""))


class Jats:
    """Turns a JATS (journal article XML) element into the books' plain HTML: sections become headings, figures
    their label and caption ("Figure 2: ..."), tables stay tables, formulas become text (mathtext), references
    are left out."""

    INLINE = {"bold": "strong", "italic": "em", "sup": "sup", "sub": "sub", "underline": "em", "sc": ""}
    SKIP = {"ref-list", "fn-group", "ack", "object-id", "graphic", "media", "alternatives", "inline-graphic",
            "label", "title", "caption", "table-wrap-foot", "permissions", "funding-group"}

    def html(self, el, depth=2):
        """The HTML of el's text and children (not its own tag)."""
        parts = [B.esc(el.text)] if el.text else []
        for child in el:
            parts.append(self.convert(child, depth))
            if child.tail:
                parts.append(B.esc(child.tail))
        return "".join(parts)

    def convert(self, el, depth):
        """The HTML of one JATS element."""
        tag = _tag(el)
        if tag == "math":
            return f'<span class="math" role="math">{B.esc(mathtext.mathml_text(el))}</span>'
        if tag in ("inline-formula", "disp-formula"):
            math = next((x for x in el.iter() if _tag(x) == "math"), None)
            text = mathtext.mathml_text(math) if math is not None else _words(el)
            elem = "div" if tag == "disp-formula" else "span"
            return f'<{elem} class="math" role="math" aria-label="{B.esc(text)}">{B.esc(text)}</{elem}>'
        if tag in self.SKIP:
            return ""
        if tag == "sec" or tag == "boxed-text":
            title = el.find("{*}title")
            head = f"<h{depth}>{self.html(title, depth)}</h{depth}>" if title is not None and _words(title) else ""
            return head + self.html(el, min(depth + 1, 6))
        if tag == "p":
            return f"<p>{self.html(el, depth)}</p>"
        if tag == "list":
            kind = "ol" if el.get("list-type") in ("order", "arabic", "alpha-lower", "roman-lower") else "ul"
            return f"<{kind}>{self.html(el, depth)}</{kind}>"
        if tag == "list-item":
            return f"<li>{self.html(el, depth)}</li>"
        if tag in ("fig", "table-wrap"):
            label = _words(el.find(".//{*}label"))
            cap = el.find(".//{*}caption")
            words = " ".join(x for x in (label, _words(cap)) if x)
            if tag == "fig":
                return f"<p>Figure: {B.esc(words)}</p>" if words else ""
            table = next((x for x in el.iter() if _tag(x) == "table"), None)
            return (f"<p><strong>{B.esc(words)}</strong></p>" if words else "") + \
                (self.convert(table, depth) if table is not None else "")
        if tag in ("table", "thead", "tbody", "tr", "td", "th"):
            return f"<{tag}>{self.html(el, depth)}</{tag}>"
        if tag in ("ext-link", "uri"):
            href = next((v for k, v in el.attrib.items() if k.endswith("href")), "")
            return f'<a href="{B.esc(href)}">{self.html(el, depth)}</a>' if href.startswith("http") else \
                self.html(el, depth)
        if tag == "disp-quote":
            return f"<blockquote>{self.html(el, depth)}</blockquote>"
        if tag in self.INLINE and self.INLINE[tag]:
            t = self.INLINE[tag]
            return f"<{t}>{self.html(el, depth)}</{t}>"
        return self.html(el, depth)                          # xref, named-content, styled-content ...: their text


def jats_article(xml_text):
    """{title, authors, journal, date, doi, licence, licence_url, body} of a JATS article ("" fields when not
    stated). The body starts with its plain-language summary (when it has one), then the abstract and the text."""
    root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    meta = next((x for x in root.iter() if _tag(x) == "article-meta"), root)
    title = _words(next((x for x in meta.iter() if _tag(x) == "article-title"), None))
    names = []
    for c in meta.iter():
        if _tag(c) == "contrib" and c.get("contrib-type", "author") == "author":
            sur = _words(next((x for x in c.iter() if _tag(x) == "surname"), None))
            given = _words(next((x for x in c.iter() if _tag(x) == "given-names"), None))
            if sur:
                names.append(f"{given} {sur}".strip())
    authors = ", ".join(names[:3]) + (" et al." if len(names) > 3 else "")
    journal = _words(next((x for x in root.iter() if _tag(x) == "journal-title"), None))
    doi = next((_words(x) for x in meta.iter() if _tag(x) == "article-id" and x.get("pub-id-type") == "doi"), "")
    date = ""
    for d in meta.iter():
        if _tag(d) == "pub-date":
            y = _words(d.find("year")) if d.find("year") is not None else ""
            mo = _words(d.find("month")) if d.find("month") is not None else ""
            da = _words(d.find("day")) if d.find("day") is not None else ""
            if y:
                found = y + (f"-{int(mo):02d}" if mo.isdigit() else "") + (f"-{int(da):02d}" if da.isdigit() and
                                                                          mo.isdigit() else "")
                date = max(date, found) if date else found
    licence, licence_url = jats_licence(root)
    j = Jats()
    parts = []
    abstracts = [a for a in meta.iter() if _tag(a) == "abstract"]
    abstracts.sort(key=lambda a: a.get("abstract-type") not in SUMMARY_TYPES)
    for a in abstracts:
        kind = a.get("abstract-type", "")
        t = a.find("{*}title")
        heading = _words(t) or ("Plain-language summary" if kind in SUMMARY_TYPES else "Abstract")
        parts.append(f"<h2>{B.esc(heading)}</h2>" + j.html(a, 3))
    body = next((x for x in root if _tag(x) == "body"), None)
    if body is not None:
        parts.append(j.html(body, 2))
    return {"title": title, "authors": authors, "journal": journal, "date": date, "doi": doi, "licence": licence,
            "licence_url": licence_url, "body": "".join(parts)}


def europepmc_items(spec, piece, cache, left_out, today):
    """The newest review articles on the topic piece (EPMC_TOPICS) in Europe PMC's open-access subset under CC BY
    or CC0 (asked for in the search, and checked again in each article's own text), at most spec["per_piece"]."""
    year = (today or datetime.date.today()).year
    name, words = EPMC_TOPICS[piece]
    query = (f"(TITLE:({words}) OR KW:({words})) AND (LICENSE:\"cc by\" OR LICENSE:\"cc0\") AND OPEN_ACCESS:y AND "
             f"PUB_TYPE:\"review\" AND LANG:eng AND IN_EPMC:y AND FIRST_PDATE:[{year - spec['years_back']}-01-01 TO "
             f"{year}-12-31]")
    want = spec.get("per_piece", 150)
    out, cursor, refused, seen = [], "*", 0, set()
    while len(out) < want:
        params = urllib.parse.urlencode({"query": query, "format": "json", "resultType": "lite", "pageSize": 100,
                                         "cursorMark": cursor, "sort": "P_PDATE_D desc"})
        data = json.loads(B.fetch(f"{EPMC_API}/search?{params}", None))
        results = data.get("resultList", {}).get("result", [])
        for r in results:
            pmcid = r.get("pmcid")
            if not pmcid or pmcid in seen or len(out) >= want:
                continue
            seen.add(pmcid)
            try:
                art = jats_article(B.fetch(f"{EPMC_API}/{pmcid}/fullTextXML", cache))
            except (urllib.error.URLError, OSError, ET.ParseError):
                refused += 1
                continue
            if not open_enough(art["licence"]):
                refused += 1
                continue
            # The first day it was public (online); the issue date in the article can lie in the future.
            when = B.iso_date(r.get("firstPublicationDate", "")) or art["date"]
            credit = (f"{art['authors']}. {art['title']}. {art['journal']}, {when}."
                      f"{(' DOI ' + art['doi'] + '.') if art['doi'] else ''}")
            body = clean(art["body"], "https://europepmc.org/")
            body += "<p>The article's list of references is left out; it is in the original.</p>"
            out.append(item(f"https://europepmc.org/article/PMC/{pmcid}", art["title"] or r.get("title", ""), when,
                            body, month_unit(when)[-4:], byline=credit, licence=art["licence"],
                            licence_url=art["licence_url"] or B._licence_address(art["licence"])))
        nxt = data.get("nextCursorMark")
        if not results or not nxt or nxt == cursor:
            break
        cursor = nxt
    if refused:
        left_out.append({"title": f"{spec['series_title']}: {name}", "reason": f"{refused} articles were left out: "
                         "their own licence is not CC BY or CC0, or their text could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== WordPress news sites (REST API)

def wordpress_items(spec, piece, cache, left_out, today):
    """The posts of the year piece of a WordPress site (Global Voices, KFF Health News, NASA's news releases), from
    its REST API (/wp-json/wp/v2/<rest_base>, 100 a page, newest first; the site's Crawl-delay obeyed), without the
    ones spec["skip"] (a regular expression on the text) marks as not under the site's licence. A whole-and-
    unchanged source keeps every post's text as it is."""
    year = int(piece)
    current = year >= (today or datetime.date.today()).year
    whole = bool(spec.get("unchanged"))
    skip = re.compile(spec["skip"], re.I) if spec.get("skip") else None
    site, base = spec["site"], spec.get("rest_base", "posts")
    out, skipped = [], 0
    for page in range(1, 200):
        url = (f"{site}/wp-json/wp/v2/{base}?after={year}-01-01T00:00:00&before={year + 1}-01-01T00:00:00"
               f"&per_page=100&page={page}&orderby=date&order=desc&_embed=author"
               f"&_fields=id,date,modified,link,title,content,_links,_embedded")
        if not robots_ok(spec, url, cache):
            break
        try:
            posts = json.loads(B.fetch(url, None if current else cache))
        except urllib.error.HTTPError as e:
            if e.code == 400:                                # past the last page
                break
            raise
        if not posts:
            break
        for p in posts:
            content = (p.get("content") or {}).get("rendered", "")
            if skip and skip.search(html.unescape(re.sub(r"<[^>]+>", " ", content))):
                skipped += 1
                continue
            title = html.unescape(re.sub(r"<[^>]+>", "", (p.get("title") or {}).get("rendered", "")))
            authors = ", ".join(a.get("name", "") for a in (p.get("_embedded") or {}).get("author", [])
                                if isinstance(a, dict) and a.get("name"))
            when = B.iso_date(p.get("date", ""))
            out.append(item(p.get("link", site), title, when, clean(content, p.get("link", site), whole),
                            month_unit(when), byline=f"By {authors}, {spec['publisher']}" if authors else ""))
        if len(posts) < 100 or len(out) >= spec.get("limit", MAX_ITEMS):
            out = out[:spec.get("limit", MAX_ITEMS)]
            break
    if skipped:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{skipped} articles were left out: "
                         f"{spec.get('skip_reason', 'not under the site licence')}."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== Atom news feeds (The Conversation)

ATOM = "{http://www.w3.org/2005/Atom}"


def atom_items(spec, piece, cache, left_out, today):
    """The articles of a news feed (spec["feed"] with the piece, such as The Conversation's edition "us"), each
    kept whole and unchanged; an entry whose own <rights> does not match spec["rights"] is left out."""
    url = spec["feed"].format(piece=piece)
    if not robots_ok(spec, url, cache):
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": "robots.txt does not allow its feed."})
        return []
    root = ET.fromstring(B.fetch(url, None).encode("utf-8"))
    whole = bool(spec.get("unchanged"))
    out, wrong = [], 0
    for e in root.iter(f"{ATOM}entry"):
        rights = _words(e.find(f"{ATOM}rights"))
        if spec.get("rights") and not re.search(spec["rights"], rights, re.I):
            wrong += 1
            continue
        link = next((x.get("href") for x in e.findall(f"{ATOM}link") if x.get("rel", "alternate") == "alternate"),
                    "")
        when = B.iso_date(_words(e.find(f"{ATOM}published")) or _words(e.find(f"{ATOM}updated")))
        authors = "; ".join(_words(a.find(f"{ATOM}name")) for a in e.findall(f"{ATOM}author"))
        content = e.find(f"{ATOM}content")
        body = clean(content.text if content is not None and content.text else "", link, whole)
        credit = f"{spec['credit']} " if spec.get("credit") else ""
        out.append(item(link, _words(e.find(f"{ATOM}title")), when, body, month_unit(when),
                        byline=f"{credit}By {authors}" if authors else credit.strip()))
    if wrong:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{wrong} articles were left out: "
                         "their own licence line is not the one that was checked."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== Voice of America

VOA_SITE = "https://www.voanews.com"
# Material VOA licenses from news agencies is not in the public domain; a story that names one is left out.
WIRE = re.compile(r"\b(Associated Press|Reuters|Agence France[- ]Presse|AFP)\b|\(AP\)|\bAP\b")


def voa_items(spec, piece, cache, left_out, today):
    """Voice of America's own stories of the last spec["days"] days, from its sitemaps (read fresh), without any
    story by or naming a news agency, newest first."""
    since = ((today or datetime.date.today()) - datetime.timedelta(days=spec.get("days", 60))).isoformat()
    index = B.fetch(f"{VOA_SITE}/sitemap.xml", None)
    maps = [u for u in re.findall(r"<loc>\s*([^<\s]+\.xml\.gz)\s*</loc>", index)]
    maps.sort(key=lambda u: [int(n) for n in re.findall(r"\d+", u.rsplit("/", 1)[-1])])
    urls = []
    for m in maps:
        data = B.fetch(m, None, binary=True)
        try:
            data = gzip.decompress(data)
        except OSError:
            pass                                             # already unpacked
        found = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>\s*<lastmod>\s*([^<\s]+)", data.decode("utf-8", "replace"))
        recent = [u for u, when in found if when[:10] >= since and "/a/" in u]
        urls += [u for u in recent if u not in urls]
        if not recent or len(urls) >= spec.get("limit", 1500):
            break
    out, wire, failed = [], 0, 0
    for url in urls[:spec.get("limit", 1500)]:
        if not robots_ok(spec, url, cache):
            failed += 1
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        art = next((d for d in json_ld(text) if d.get("@type") in ("NewsArticle", "Article", "ReportageNewsArticle")),
                   {})
        authors = art.get("author") or []
        authors = [a.get("name", "") for a in (authors if isinstance(authors, list) else [authors])
                   if isinstance(a, dict)]
        raw = div_inner(text, r'<div class="wsw">')
        if not raw:
            failed += 1
            continue
        plain = html.unescape(re.sub(r"<[^>]+>", " ", raw))
        if any(WIRE.search(a) for a in authors) or WIRE.search(plain):
            wire += 1
            continue
        when = B.iso_date(art.get("datePublished", "")) or B.page_date(text)
        title = B.first_heading(text) or html.unescape(art.get("headline") or art.get("name") or "")
        out.append(item(url, title, when, clean(raw, url), month_unit(when),
                        byline=("By " + ", ".join(a for a in authors if a)) if any(authors) else ""))
    if wire or failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{wire} stories with news-agency "
                         f"material were left out; {failed} could not be read or are not allowed by robots.txt."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== history: the Office of the Historian (TEI)

TEI = "{http://www.tei-c.org/ns/1.0}"
VOLUME_TITLES = {}               # piece -> the title of a FRUS volume (for its book's title)
PUBLISHED = {}                   # (source, piece) -> when the publisher published it, when that is not the newest
                                 # item's date (a FRUS volume: its own publication date, not its documents' dates)


def git_checkout(repo, paths, work):
    """A shallow, sparse copy of a GitHub repository with only paths (files or folders) in it, in work (kept between
    runs); returns its folder. git is used, as for the OpenStax books (the repositories are public)."""
    import subprocess
    folder = os.path.join(work, repo.rstrip("/").rsplit("/", 1)[-1])
    if not os.path.isdir(os.path.join(folder, ".git")):
        os.makedirs(work, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", repo, folder],
                       check=True, timeout=3600)
    subprocess.run(["git", "-C", folder, "sparse-checkout", "set", "--no-cone", *paths], check=True, timeout=3600)
    return folder


def _work(cache):
    """The folder for downloaded repositories (inside the cache when there is one)."""
    import tempfile
    return os.path.join(cache or tempfile.gettempdir(), "work")


class Tei:
    """Turns TEI (the XML of the Office of the Historian's publications) into the books' plain HTML: paragraphs,
    lists, tables, headings of inner parts, page marks ("[Page 12]"), and the notes (source notes and footnotes) as
    numbered notes after the text; persons, places and dates are kept as their words."""

    def __init__(self):
        """Start with no notes."""
        self.notes = []

    def html(self, el, depth=2):
        """The HTML of el's text and children (not its own tag)."""
        parts = [B.esc(el.text)] if el.text else []
        for child in el:
            parts.append(self.convert(child, depth))
            if child.tail:
                parts.append(B.esc(child.tail))
        return "".join(parts)

    def convert(self, el, depth):
        """The HTML of one TEI element."""
        tag = _tag(el)
        if tag in ("graphic", "teiHeader", "figDesc") or tag == "head":
            return ""
        if tag == "note":
            self.notes.append(self.html(el, depth))
            n = len(self.notes)
            return f'<sup><a href="#note-{n}">[{n}]</a></sup>'
        if tag == "div":
            return self.section(el, depth)
        if tag in ("p", "opener", "closer", "dateline", "signed", "salute", "postscript", "byline", "ab"):
            return f"<p>{self.html(el, depth)}</p>"
        if tag == "list":
            head = el.find(f"{TEI}head")
            words = f"<p><strong>{self.html(head, depth)}</strong></p>" if head is not None else ""
            return words + f"<ul>{self.html(el, depth)}</ul>"
        if tag == "item":
            return f"<li>{self.html(el, depth)}</li>"
        if tag == "label":
            return f"{self.html(el, depth)} "
        if tag == "table":
            return f"<table>{self.html(el, depth)}</table>"
        if tag == "row":
            return f"<tr>{self.html(el, depth)}</tr>"
        if tag == "cell":
            cell = "th" if el.get("role") == "label" else "td"
            return f"<{cell}>{self.html(el, depth)}</{cell}>"
        if tag == "lb":
            return "<br>"
        if tag == "pb":
            return f'<span class="pagenum">[Page {B.esc(el.get("n", ""))}]</span> ' if el.get("n") else ""
        if tag == "hi":
            rend = el.get("rend", "")
            t = "em" if "italic" in rend else "strong" if ("bold" in rend or "strong" in rend) else \
                "sup" if "super" in rend else "sub" if "sub" in rend else ""
            return f"<{t}>{self.html(el, depth)}</{t}>" if t else self.html(el, depth)
        if tag == "figure":
            head = el.find(f"{TEI}head")
            return f"<p>Picture: {B.esc(_words(head))}</p>" if head is not None and _words(head) else ""
        if tag == "ref" and (el.get("target") or "").startswith("http"):
            return f'<a href="{B.esc(el.get("target"))}">{self.html(el, depth)}</a>'
        if tag in ("quote", "q", "cit"):
            return f"<blockquote>{self.html(el, depth)}</blockquote>" if el.find(f"{TEI}p") is not None else \
                self.html(el, depth)
        return self.html(el, depth)

    def section(self, el, depth):
        """An inner part with its heading."""
        head = el.find(f"{TEI}head")
        words = f"<h{depth}>{head_words(head)}</h{depth}>" if head is not None and _words(head) else ""
        return words + self.html(el, min(depth + 1, 6))

    def notes_html(self):
        """The numbered notes collected so far, as a list after the text ("" when none); then forgets them."""
        if not self.notes:
            return ""
        out = "<h2>Notes</h2><ol>" + "".join(f'<li id="note-{i}">{t}</li>' for i, t in enumerate(self.notes, 1)) + \
            "</ol>"
        self.notes = []
        return out


def head_words(head):
    """The words of a TEI <head> without its notes, escaped."""
    if head is None:
        return ""
    copy = ET.fromstring(ET.tostring(head))
    for parent in list(copy.iter()):
        for child in list(parent):
            if _tag(child) == "note":
                tail = child.tail
                parent.remove(child)
                if tail:
                    parent.text = (parent.text or "") + tail
    return B.esc(_words(copy))


def milestones_items(spec, piece, cache, left_out, today):
    """The essays of "Milestones in the History of U.S. Foreign Relations" (one per section of each period's TEI
    file in the Office of the Historian's repository), in the order of the periods; each dated by its last revision
    (the file's revisionDesc)."""
    folder = git_checkout(spec["repo"], ["/chapters/"], _work(cache))
    out = []
    for name in sorted(os.listdir(os.path.join(folder, "chapters"))):
        if not name.endswith(".xml"):
            continue
        root = ET.parse(os.path.join(folder, "chapters", name)).getroot()
        period = name[:-4]
        short = _words(next((t for t in root.iter(f"{TEI}title") if t.get("type") == "short"), None)) or period
        revised = {}
        for change in root.iter(f"{TEI}change"):
            for target in (change.get("target") or "").split():
                revised[target.lstrip("#")] = max(revised.get(target.lstrip("#"), ""), change.get("when", ""))
        text = root.find(f"{TEI}text")
        for part in (text if text is not None else []):
            for div in part.findall(f"{TEI}div"):
                ident = div.get("{http://www.w3.org/XML/1998/namespace}id", "")
                t = Tei()
                body = t.html(div, 2) + t.notes_html()
                title = " ".join(html.unescape(head_words(div.find(f"{TEI}head"))).split()) or ident
                out.append(item(f"https://history.state.gov/milestones/{period}/{ident}", title,
                                B.iso_date(revised.get(ident, "")), body, short))
    return out


def frus_items(spec, piece, cache, left_out, today):
    """The documents of one volume of Foreign Relations of the United States (piece: its id, such as
    "frus1961-63v11"), from the Office of the Historian's repository: its preface and sources first, then one page per
    document (and editorial note), dated by the document's own date, under its chapter's heading."""
    folder = git_checkout(spec["repo"], [f"/volumes/{piece}.xml"], _work(cache))
    path = os.path.join(folder, "volumes", f"{piece}.xml")
    if not os.path.exists(path):
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": "There is no such volume."})
        return []
    root = ET.parse(path).getroot()
    published = [d.get("when", "") for d in root.iter(f"{TEI}date") if d.get("type") == "publication-date"]
    PUBLISHED[(spec["name"], piece)] = B.newest_date([B.iso_date(d) for d in published])
    VOLUME_TITLES[piece] = " ".join(_words(next((t for t in root.iter(f"{TEI}title")
                                                  if t.get("type") == "complete"), None)).split())
    base = f"https://history.state.gov/historicaldocuments/{piece}"
    out = []

    def walk(el, chapter):
        """Add the documents under el; chapter: the heading of the part they are in."""
        for div in el.findall(f"{TEI}div"):
            kind, sub = div.get("type"), div.get("subtype")
            ident = div.get("{http://www.w3.org/XML/1998/namespace}id", "")
            title = " ".join(html.unescape(head_words(div.find(f"{TEI}head"))).split())
            if kind == "document":
                when = next((d.get("when") for d in div.iter(f"{TEI}date") if d.get("when")), "") or \
                    next((v for k, v in div.attrib.items() if k.endswith("doc-dateTime-min")), "")
                t = Tei()
                head = div.find(f"{TEI}head")
                if head is not None:                         # the source note of the heading comes first
                    for note in head.iter(f"{TEI}note"):
                        t.notes.append(t.html(note, 2))
                body = t.html(div, 2) + t.notes_html()
                out.append(item(f"{base}/{ident}", title or ident, B.iso_date(when or ""), body, chapter))
            elif kind == "section" and sub in ("preface", "sources", "abbreviations", "persons", "terms"):
                t = Tei()
                out.append(item(f"{base}/{ident}", title or ident, "", t.html(div, 2) + t.notes_html(),
                                "About this volume"))
            elif kind in ("compilation", "chapter", "subchapter", "section") and sub not in ("index",
                                                                                           "table-of-contents"):
                walk(div, title or chapter)
    text = root.find(f"{TEI}text")
    for part in (list(text) if text is not None else []):
        walk(part, "")
    return out


# ====================================================================== history: Chronicling America (loc.gov)

LOC = "https://www.loc.gov"
# loc.gov limits automated use (its API documentation: about 20 searches a minute; too many and it answers 429 and
# blocks for a while), so its searches and pages are read at most one every LOC_PAUSE seconds.
LOC_PAUSE = 4.0


def ocr_html(text):
    """A newspaper page's machine-read text as HTML: its lines kept, paragraphs at blank lines."""
    paras = [p for p in re.split(r"\n\s*\n", text or "") if p.strip()]
    return "".join("<p>" + "<br>\n".join(B.esc(line.strip()) for line in p.splitlines() if line.strip()) + "</p>"
                   for p in paras)


def chronam_items(spec, piece, cache, left_out, today):
    """A sample of the English-language newspaper issues of one state and decade (piece "vermont-1910s"):
    spec["per_month"] issues a month from the Library of Congress's API, each issue one page with the OCR text of all
    its pages. Only issues published more than 95 years ago (US public domain) and whose rights statement says
    public domain are kept."""
    m = re.match(r"^(.*)-(\d{4})s$", piece)
    state, decade = m.group(1).replace("-", " "), int(m.group(2))
    for host in ("www.loc.gov", "tile.loc.gov"):
        B.CRAWL_DELAY[host] = max(B.CRAWL_DELAY.get(host, 0), LOC_PAUSE)
    last = (today or datetime.date.today()).year - 96            # published more than 95 years ago
    out, refused = [], 0
    found = []                                                   # (year, search result) of one issue a month
    slow_down = {"title": f"{spec['series_title']}, {piece}", "reason": "The Library of Congress asked us to slow "
                 "down (429); the rest of the decade was not read."}
    for year in range(decade, min(decade + 9, last) + 1):
        if slow_down in left_out:
            break
        for month in range(1, 13):
            end = (datetime.date(year + month // 12, month % 12 + 1, 1) - datetime.timedelta(days=1)).day
            query = urllib.parse.urlencode({"fa": f"location_state:{state}|language:english",
                                            "dates": f"{year}-{month:02d}-01/{year}-{month:02d}-{end:02d}",
                                            "fo": "json", "c": 25, "at": "results,pagination"})
            url = f"{LOC}/collections/chronicling-america/?{query}"
            if not robots_ok(spec, url, cache):
                break
            # The answers also list the newspapers themselves (no day in their date): only issues are kept.
            try:
                answer = json.loads(B.fetch(url, cache))
            except urllib.error.HTTPError as e:
                if e.code == 429:                                # asked to slow down: stop, keep what we have
                    left_out.append(slow_down)
                    break
                raise
            issues = [r for r in answer.get("results", [])
                      if re.fullmatch(r"\d{4}-\d\d-\d\d", r.get("date", "")) and r.get("resources")]
            found += [(year, r) for r in issues[:spec.get("per_month", 1)]]
    seen = set()
    for year, r in found:
        when = B.iso_date(r.get("date", ""))
        issue = ((r.get("resources") or [{}])[0].get("url") or "").split("?")[0]
        if not issue or not when or int(when[:4]) > last or issue in seen:
            continue
        seen.add(issue)
        pages, number, total, rights = [], 1, 1, ""
        while number <= min(total, 60):
            try:
                res = json.loads(B.fetch(f"{issue}?sp={number}&fo=json", cache))
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    raise
                if slow_down not in left_out:
                    left_out.append(slow_down)
                break
            total = int((res.get("pagination") or {}).get("total") or 1)
            rights = rights or " ".join((res.get("item") or {}).get("rights") or [])
            full = (res.get("resource") or {}).get("fulltext_file")
            text = ""
            if full:
                ocr = json.loads(B.fetch(full, cache))
                text = next(iter(ocr.values()), {}).get("full_text", "") if isinstance(ocr, dict) else ""
            pages.append(f'<p class="pagenum">[Page {number}]</p>' + ocr_html(text))
            number += 1
        if slow_down in left_out:
            break                                                # an issue cut short is not kept
        if not re.search(r"public domain", rights, re.I):
            refused += 1
            continue
        out.append(item(r.get("url") or issue, r.get("title", issue), when, "\n".join(pages), str(year)))
    if refused:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{refused} issues were left out: "
                         "their rights statement does not say public domain."})
    return out


DRIVERS = {"crs": crs_items, "amber_waves": amber_waves_items, "elife": elife_items, "europepmc": europepmc_items,
           "wordpress": wordpress_items, "atom": atom_items, "voa": voa_items, "milestones": milestones_items,
           "frus": frus_items, "chronam": chronam_items}


# ====================================================================== the books

def piece_label(name, piece):
    """How a piece is named in its book's title ("2026", "the 2010s", "Blindness and low vision", "recent")."""
    if name == "europepmc_reviews":
        return EPMC_TOPICS[piece][0]
    if name == "voa":
        return "recent stories"
    if name == "the_conversation":
        return {"us": "United States edition", "uk": "UK edition", "au": "Australia edition", "ca": "Canada edition",
                "africa": "Africa edition", "global": "global edition", "nz": "New Zealand edition",
                "europe": "Europe edition"}.get(piece, piece)
    if name == "frus":
        return re.sub(r"^Foreign Relations of the United States,\s*", "", VOLUME_TITLES.get(piece, piece))
    if name == "state_milestones":
        return "1750 to 2000"
    if name == "chronicling_america":
        state, decade = piece.rsplit("-", 1)
        return f"{state.replace('-', ' ').title()}, the {decade}"
    return f"the {piece}" if piece.endswith("s") else piece


def make_book(name, piece, items):
    """The Book of one piece: one page per item (in the order the driver gives: newest first for news), each
    starting with its date ("Published: 2026-11-17", or the source's own date_label, such as "Dated" for a historical
    document), byline and original address, and ending with its own licence when it has one. For a whole-and-unchanged
    source (spec["unchanged"]: a NoDerivatives or other no-changes licence, kept whole and only converted) every page
    ends with the licence's name and address and the line "Converted to an accessible format; the text is
    unchanged."."""
    spec = SOURCES[name]
    whole = bool(spec.get("unchanged"))
    licence = LICENCE_ALIASES.get(spec["licence"], spec["licence"])
    licence_url = spec["licence_url"]
    own = sorted({i["licence"] for i in items if i["licence"]})
    if own and len(own) == 1:
        licence, licence_url = own[0], items[0]["licence_url"] or licence_url
    book = B.Book(name=f"{name}_{piece}", title=f"{spec['series_title']}, {piece_label(name, piece)}",
                  subject=spec["subject"], level="reference", group=spec["group"], publisher=spec["publisher"],
                  country=spec["country"], licence=licence, licence_url=licence_url, source=spec["source"],
                  description=spec["description"], changes=spec.get("changes", ""), unchanged=whole,
                  notice=" ".join(x for x in (spec.get("notice", ""), GROUP_NOTES.get(spec["group"], ""),
                                              "Each article's own licence is on its page." if len(own) > 1 else "")
                                  if x))
    paths = set()
    for i in items:
        path = B.slug(f"{i['date']} {i['title']}", 70)
        while path in paths or path in ("index", "style-css"):
            path += "-2"
        paths.add(path)
        head = ['<p class="published">']
        if i["date"]:
            head.append(f'{B.esc(spec.get("date_label", "Published"))}: <time datetime="{B.esc(i["date"])}">'
                        f'{B.esc(i["date"])}</time>. ')
        if i["byline"]:
            head.append(f"{B.esc(i['byline'].rstrip('.'))}. ")
        head.append(f'Original: <a href="{B.esc(i["url"])}">{B.esc(i["url"])}</a>.</p>')
        tail = f'<p class="credit">{B.esc(spec["page_credit"])}</p>' if spec.get("page_credit") else ""
        if i["licence"] or whole:
            lic, lic_url = (i["licence"], i["licence_url"]) if i["licence"] else (licence, licence_url)
            tail += (f'<p class="licence">Licence of this article: {B.esc(B.licence_words(lic, whole))} '
                    f'(<a href="{B.esc(lic_url)}">{B.esc(lic_url)}</a>).'
                    f'{(" " + B.UNCHANGED) if whole else ""}</p>')
        book.pages.append(B.Page(path, i["title"], "".join(head) + "\n" + i["body"] + tail, 0, i["unit"]))
    book.published = PUBLISHED.get((name, piece)) or B.newest_date([i["date"] for i in items])
    book.series, book.piece, book.item_dates = name, piece, [i["date"] for i in items]
    return book


def books_for_key(key, cache=None, left_out=None, today=None):
    """[Book] of one piece key ("pub:crs:2026"); [] (and a reason in left_out) when its licence page no longer says
    what was checked or nothing could be read."""
    left_out = left_out if left_out is not None else []
    _pub, name, piece = key.split(":", 2)
    spec = SOURCES[name]
    title = f"{spec['series_title']}, {piece_label(name, piece)}"
    licence = LICENCE_ALIASES.get(spec["licence"], spec["licence"])
    if not B.licence_kind(licence, bool(spec.get("unchanged"))):
        left_out.append({"title": title, "reason": f"Its licence ({licence}) is not one the toolkit may repackage."})
        return []
    if not licence_still_stated(spec, cache):
        left_out.append({"title": title, "reason": f"Its licence page ({spec['licence_page']}) no longer states "
                         "the licence that was checked."})
        return []
    items = DRIVERS[spec["driver"]](spec, piece, cache, left_out, today)
    if not items:
        left_out.append({"title": title, "reason": "No items could be read."})
        return []
    return [make_book(name, piece, items)]


def catalogue_extra(book):
    """The fields a periodical's catalogue entry has besides the textbooks' ones: group_name (the collection's
    name), series and piece (the source and which part of it), items (how many articles), newest and oldest (their
    publication dates), and note (for news: that it ages fast)."""
    dates = sorted(d for d in getattr(book, "item_dates", []) if d)
    return {"group_name": GROUPS.get(book.group, book.group), "series": getattr(book, "series", ""),
            "piece": getattr(book, "piece", ""), "items": len(book.pages), "newest": dates[-1] if dates else "",
            "oldest": dates[0] if dates else "", "note": GROUP_NOTES.get(book.group, "")}


def build_periodicals(keys, out_dir, cache=None, date=None, today=None):
    """Build the pieces of keys (see expand_keys) into out_dir as ZIM files, write manifest-<key>.json for each
    piece key (as build_textbooks.build does) and return {key: manifest}; each manifest's "books" are catalogue
    entries in the textbooks' shape (build_textbooks.manifest_entry) plus catalogue_extra's fields."""
    manifests = {}
    os.makedirs(out_dir, exist_ok=True)
    for key in expand_keys(keys, today):
        left_out, entries = [], []
        try:
            books = books_for_key(key, cache, left_out, today)
        except Exception as e:  # noqa: BLE001 - one piece's failure does not stop the others; said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            books = []
        for book in books:
            entry = B.write_book(book, out_dir, date)
            entry.update(catalogue_extra(book))
            print(f"{entry['file']}: {entry['items']} items, {entry['size']:,} bytes, {entry['licence']}")
            entries.append(entry)
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower())
        manifest = {"key": key, "books": entries, "left_out": left_out, "files": [e["file"] for e in entries]}
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["pub:all"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--list", action="store_true", help="only print the piece keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build_periodicals(a.keys, a.out, a.cache)
    return 0


if __name__ == "__main__":
    sys.exit(main())
