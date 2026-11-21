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
  journals     Articles, open-access journals  eLife papers whole, their digest (plain-language summary) first
                                               (CC BY, read from Europe PMC: eLife's own API host disallows all
                                               robots); review
                                               articles from the Europe PMC open-access subset (CC BY and CC0 only)
                                               on topics useful to a blind adult
  news         News, open-licensed             Global Voices (CC BY 3.0); Voice of America's own reporting (public
                                               domain; news-agency and partner copy left out; the last 60 days and
                                               every year back to 2001) and VOA Learning English by year; NASA news
                                               releases (public
                                               domain); KFF Health News (CC BY-NC-ND 4.0) and The Conversation (CC
                                               BY-ND 4.0), both whole and unchanged. News ages fast: the entries
                                               carry a "note" saying so, and "published" is the newest item's date
  periodicals  Magazines and newsletters       USDA ERS "Amber Waves" (public domain)
  history      Reference, history              the State Department's "Milestones" essays and "Foreign Relations of
                                               the United States" volumes (public domain and CC0); historic
                                               newspapers from Chronicling America (Library of Congress; only those
                                               published more than 95 years ago); VOA radio scripts of the 1970s
                                               (Internet Archive, public domain)

The whole-and-unchanged rule (sources.WHOLE_AND_UNCHANGED, the owner's decision of 2026-11-18): a NoDerivatives
licence (CC BY-ND, CC BY-NC-ND) is used only for works kept WHOLE with their TEXT UNCHANGED, converted in format
only, because Creative Commons 4.0 section 2(a)(4) allows "technical modifications necessary to exercise the
Licensed Rights in all media and formats" and says they "never produce Adapted Material" (CC 2.5 and 3.0: "modifications
as are technically necessary to exercise the rights in other media and formats"). A source with "unchanged": True
is never excerpted, cut, summarised or reworded: each article is kept entire (no partner or "related" boxes are cut
out of it, and headings are never dropped even when empty), its HTML is only cleaned up (menus, scripts and
decorative pictures left out; headings, links and the descriptions of pictures kept), and every page carries the
credit, the licence's name and address, the original address and the line "Converted to an accessible format; the
text is unchanged." An invisible tracking picture (The Conversation's 1-pixel page-view counter) is not part of an
article's text and is left out: The Conversation's guidelines ask for it only "when republishing online", and a ZIM
book is read offline, so leaving it out is the reading closest to their written terms. Whole articles that are not
under the licence (a partner's story, one marked "All Rights Reserved") are left out entirely, never trimmed. Each
site's robots.txt and republishing terms are obeyed too.

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
import calendar
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
MAX_ORIGINALS = 100              # the most item addresses listed in a book's "originals" (keeps textbooks.json small;
                                 # every item's own original address is on its page in the book in any case)

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

VOA_NOTICE = ("All text, audio and video material produced exclusively by the Voice of America is in the public "
              "domain (VOA's copyright statement). Credit: voanews.com, Voice of America.")
VOA_LICENCE_TEXT = r"produced exclusively by the Voice of America is in the public domain"

# VOA radio scripts of the 1970s, one book per month: a single year ran past the 4-hour build job limit.
VOA_HISTORY_MONTHS = [f"{y}-{m:02d}" for y in range(1970, 1980) for m in range(1, 13)]

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
        daily=lambda today: _years(0, today), pieces=lambda today: _years(3, today), piece_rule=r"^(19|20)\d\d$"),
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
        group="journals", driver="elife", series_title="eLife papers with their digests (plain-language summaries)",
        subject="Science and medicine explained", publisher="eLife Sciences Publications and the papers' authors "
        "(from Europe PMC)", country="International", licence="CC BY 4.0", licence_url=CC_BY_4,
        source="https://europepmc.org/",
        description="Research papers in eLife that have a plain-language summary (\"eLife digest\", written for "
                    "everyone), each paper whole: its digest first, then its abstract, text and references, from the "
                    "papers' open-access full text in Europe PMC. One book per year.",
        changes="each whole paper made into a web page, its digest first, with the figures as their captions (until "
                "2026-11-21 only the digest was kept; the reference-library audit made it the whole paper)",
        pieces=lambda today: _years(4, today), piece_rule=r"^20\d\d$"),
    "europepmc_reviews": dict(
        group="journals", driver="europepmc", series_title="Open-access health reviews",
        subject="Health and medicine", publisher="The articles' authors and journals (from Europe PMC's open-access "
        "subset)", country="International", licence="CC BY", licence_url=CC_BY_4,
        source="https://europepmc.org/",
        description="Review articles from open-access journals (Creative Commons Attribution or CC0 only), newest "
                    "first, on one topic. Each article's authors, journal, date, DOI and own licence are on its "
                    "page.",
        changes="made into web pages with the figures as their captions (the reference lists kept)",
        pieces=lambda today: list(EPMC_TOPICS), piece_rule="^(" + "|".join(EPMC_TOPICS) + r")(-(19|20)\d\d)?$",
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
        daily=lambda today: _years(0, today), pieces=lambda today: _years(1, today), piece_rule=r"^20\d\d$"),
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
        catalogue_note="Not for commercial use: commercial use needs KFF Health News's permission (its terms ask to "
                       "be contacted first for use in commercial products such as academic textbooks).",
        page_credit="This story was produced by KFF Health News. KFF Health News is a national newsroom that "
                    "produces in-depth journalism about health issues and is one of the core operating programs at KFF "
                    "— the independent source for health policy research, polling, and journalism.",
        licence_page="https://kffhealthnews.org/syndication/",
        licence_text=r"Attribution-NonCommercial-NoDerivatives 4\.0 International \(CC BY-NC-ND 4\.0\)",
        skip=r"All Rights Reserved|reprinted with permission|republished (?:with permission|from)|"
             r"originally (?:been )?published (?:by|in|on)",
        skip_reason="marked \"All Rights Reserved\" or published first by another outlet",
        daily=lambda today: _years(0, today), pieces=lambda today: _years(1, today), piece_rule=r"^20\d\d$"),
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
        daily=lambda today: _years(0, today), pieces=lambda today: _years(1, today), piece_rule=r"^20\d\d$"),
    "the_conversation": dict(
        group="news", driver="atom", series_title="The Conversation",
        subject="News and analysis by academic experts", publisher="The Conversation", country="International",
        licence="CC BY-ND 4.0", licence_url="https://creativecommons.org/licenses/by-nd/4.0/", unchanged=True,
        source="https://theconversation.com/",
        feed="https://theconversation.com/{piece}/articles.atom", rights=r"attribution, no derivatives",
        credit="This article is republished from The Conversation under a Creative Commons license.",
        # The 1-pixel page-view counter is not text; asked for only "when republishing online" (a ZIM is offline).
        drop_html=[r'<img\b[^>]*counter\.theconversation\.com[^>]*>'],
        description="Articles written by university researchers and edited by journalists, from one edition of The "
                    "Conversation (its latest articles, as its news feed lists them), each whole and unchanged.",
        notice="Republished from The Conversation under a Creative Commons licence (CC BY-ND 4.0), whole and "
               "unchanged. Each article names its authors and their institutions. Photographs are left out (The "
               "Conversation does not license them for republication).",
        licence_page="https://theconversation.com/us/republishing-guidelines",
        licence_text=r"publish all our work under a\s*(?:<[^>]+>\s*)*Creative Commons",
        daily=lambda today: ["us", "uk", "au", "ca", "africa", "global"],
        pieces=lambda today: ["us", "uk", "au", "ca", "africa", "global"],
        piece_rule=r"^(us|uk|au|ca|africa|global|nz|europe)(-20[1-2]\d)?$", budget_minutes=200),
    "voa": dict(
        group="news", driver="voa", series_title="Voice of America news",
        subject="US and world news", publisher="Voice of America (VOA)", country="United States",
        licence="Public domain (VOA's own reporting)", licence_url="https://www.voanews.com/p/5338.html",
        source="https://www.voanews.com/",
        description="News stories written by Voice of America's own reporters: the last 60 days (recent) or one "
                    "year (back to 2001). Stories that use material from news agencies (AP, Reuters, AFP and others) "
                    "or from partners are left out, as VOA's terms ask.",
        notice=VOA_NOTICE,
        changes="made into web pages with the pictures, videos and site menus left out; stories with news-agency "
                "or partner material left out",
        licence_page="https://www.voanews.com/p/5338.html", licence_text=VOA_LICENCE_TEXT,
        # recent and the last three years by default; every year back to 2001 by key (pub:voa:2001 ... pub:voa:2022).
        daily=lambda today: ["recent"] + _years(0, today),
        pieces=lambda today: ["recent"] + _years(2, today), piece_rule=r"^(recent|199[5-9]|20[0-2]\d)$", days=60,
        budget_minutes=200),
    "voa_learning": dict(
        group="news", driver="voa", site="https://learningenglish.voanews.com",
        series_title="VOA Learning English", subject="News in simpler English", publisher="Voice of America (VOA)",
        country="United States", licence="Public domain (VOA's own reporting)",
        licence_url="https://www.voanews.com/p/5338.html", source="https://learningenglish.voanews.com/",
        description="Voice of America's Learning English stories, written in slower, simpler English, one year per "
                    "book (back to 2001). Stories using news-agency or partner material are left out.",
        notice=VOA_NOTICE + " (The Kiwix library's VOA Learning English is a snapshot of the current site, with its "
                            "videos; these books are the text of past years.)",
        changes="made into web pages with the pictures, audio, videos and site menus left out; stories with "
                "news-agency or partner material left out",
        licence_page="https://www.voanews.com/p/5338.html", licence_text=VOA_LICENCE_TEXT,
        daily=lambda today: _years(0, today),
        pieces=lambda today: _years(2, today), piece_rule=r"^20[0-2]\d$", budget_minutes=200),
    "voa_history": dict(
        group="history", driver="voa_history", series_title="Voice of America radio scripts",
        subject="US and world history (radio scripts)", publisher="Voice of America (VOA)", country="United States",
        licence=US_GOV, licence_url=US_GOV_URL, source="https://archive.org/details/voa-radio-scripts",
        collection="voa-radio-scripts",
        description="Scripts of VOA's English radio reports (Backgrounders, This Week, Dateline, From the Bookshelf "
                    "and others), scanned by the Internet Archive from the Library of Congress's microfilm, as their "
                    "machine-read text. One book per month (a whole year did not fit in one build job); so far only the "
                    "1970s are online as text.",
        notice="Works of the Voice of America, a US government agency (public domain; the Internet Archive marks each "
               "with the Public Domain Mark). The machine-read text has the scanner's mistakes. VOA's older "
               "broadcasts survive mostly as sound recordings, which are not in these books.",
        changes="the machine-read text of each script, made into web pages", date_label="Broadcast",
        pieces=lambda today: VOA_HISTORY_MONTHS, piece_rule=r"^19[4-9](0s|\d(-(0[1-9]|1[0-2]))?)$"),
    "uk_hansard": dict(
        group="news", driver="uk_hansard", series_title="Hansard, UK Parliament debates",
        subject="UK Parliament: debates (House of Commons and House of Lords)", publisher="UK Parliament",
        country="United Kingdom", licence="Open Parliament Licence v3.0",
        licence_url="https://www.parliament.uk/site-information/copyright-parliament/open-parliament-licence/",
        source="https://hansard.parliament.uk/",
        description="The official report of what was said in the House of Commons and the House of Lords, one page "
                    "per debate (with its sitting date), from Parliament's Hansard API. One book per year.",
        notice="Contains Parliamentary information licensed under the Open Parliament Licence v3.0.",
        changes="made into web pages, one per debate",
        pieces=lambda today: _years(0, today), daily=lambda today: _years(0, today),
        piece_rule=r"^(18|19|20)\d\d$", budget_minutes=200),
    "oireachtas_debates": dict(
        group="news", driver="oireachtas", series_title="Oireachtas debates (Dáil and Seanad)",
        subject="Irish Parliament: debates", publisher="Houses of the Oireachtas", country="Ireland",
        licence="CC BY 4.0", licence_url=CC_BY_4, source="https://www.oireachtas.ie/en/debates/",
        description="The official reports of the debates of Dáil Éireann and Seanad Éireann, one page per sitting "
                    "day, from the Oireachtas open data. One book per year.",
        notice="Houses of the Oireachtas, licensed under the Oireachtas (Open Data) PSI Licence, which incorporates "
               "the Creative Commons Attribution 4.0 International License.",
        changes="made into web pages, one per sitting day, with each speaker's name before their words",
        licence_page="https://www.oireachtas.ie/en/open-data/license/",
        licence_text=r"Oireachtas \(Open Data\) PSI Licence",
        pieces=lambda today: _years(0, today), daily=lambda today: _years(0, today), piece_rule=r"^(19|20)\d\d$"),
    "govuk_speeches": dict(
        group="news", driver="govuk_speeches", series_title="UK government speeches (GOV.UK)",
        subject="Speeches and statements by UK ministers and officials", publisher="HM Government (GOV.UK)",
        country="United Kingdom", licence="OGL-UK-3.0",
        licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        source="https://www.gov.uk/search/news-and-communications",
        description="Speeches, statements to Parliament and transcripts published on GOV.UK, each with the date it "
                    "was delivered, the speaker and the department. One book per year.",
        notice="Contains public sector information licensed under the Open Government Licence v3.0.",
        changes="made into web pages with the pictures left out (their descriptions kept)",
        licence_page="https://www.gov.uk/help/terms-conditions",
        licence_text=r"published under the Open Government Licence",
        pieces=lambda today: _years(0, today), daily=lambda today: _years(0, today), piece_rule=r"^(19|20)\d\d$"),
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
    "elife_digests": "Each eLife paper's own <license> in Europe PMC (for example PMC11655060: ali:license_ref "
                     "https://creativecommons.org/licenses/by/4.0/); its digest is the abstract titled \"eLife "
                     "digest\" (abstract-type plain-language-summary). eLife's own API is not used.",
    "europepmc_reviews": "Each article's own <license> in its full text (for example PMC13194245: \"This article "
                         "is licensed under a Creative Commons Attribution 4.0 International License\"); only CC BY "
                         "(any version) and CC0 are kept. www.ebi.ac.uk/robots.txt does not restrict the Europe PMC "
                         "REST service.",
    "global_voices": "globalvoices.org footer: \"This site is licensed as Creative Commons Attribution 3.0\" "
                     "(creativecommons.org/licenses/by/3.0/). robots.txt: \"Crawl-delay: 10\", only /wp-admin/, "
                     "/wp-includes/ and /site/ disallowed; the WordPress REST API (/wp-json/) is used.",
    "uk_hansard": "Hansard is Parliamentary copyright, licensed under the Open Parliament Licence v3.0 "
                  "(parliament.uk). "
                  "The licence page and hansard.parliament.uk refuse automated requests (a Cloudflare check), so the "
                  "licence could not be checked again by the builder: recorded by hand. Read from Parliament's "
                  "documented Hansard API (hansard-api.parliament.uk).",
    "oireachtas_debates": "www.oireachtas.ie/en/open-data/license/ and its PDF: \"OIREACHTAS (OPEN DATA) PSI LICENCE: "
                          "Licence incorporating the Creative Commons Attribution 4.0 International License\"; "
                          "\"The terms on which the Licensee may re-use documents covered by this Licence are those "
                          "set out in the Creative Commons Attribution 4.0 International License\". Read from the "
                          "documented "
                          "API (api.oireachtas.ie) and data.oireachtas.ie.",
    "govuk_speeches": "www.gov.uk/help/terms-conditions: \"Most content on GOV.UK is subject to Crown copyright "
                      "protection and is published under the Open Government Licence (OGL)\". GOV.UK's search and "
                      "content APIs are public; robots.txt only disallows print pages and site search pages.",
    "voa_history": "archive.org collection voa-radio-scripts: each item \"Scanned from Library of Congress microfilm "
                   "01769 (113 reels, 1953-1980)\", creator \"..., Voice of America\", licenseurl "
                   "https://creativecommons.org/publicdomain/mark/1.0/; 2,173 items, all 1976-1978 (checked "
                   "2026-11-19). archive.org/robots.txt allows /details/, /metadata/ and /download/.",
    "voa_learning": "The VOA copyright statement (www.voanews.com/p/5338.html) covers Learning English, a VOA "
                    "service; learningenglish.voanews.com/robots.txt allows /a/ (no Crawl-delay). Kiwix's "
                    "voa_learning_en_all (2025-01, 892 articles, 7 GB with videos) is a snapshot of the current "
                    "site, not the archive.",
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
    ("eLife's own API (api.elifesciences.org)", "API host robots.txt disallows all (\"User-agent: * Disallow: /\"); "
     "the eLife digests are taken from Europe PMC's open-access full texts instead."),
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
    ("NPR (National Public Radio)", "Not included. Its terms of use (www.npr.org/about-npr/179876898/terms-of-use) "
     "forbid copying or using its material for commercial purposes \"without the prior written consent of NPR\" and "
     "say: \"You may not use, or enable others to use, any content ... to build or train large language models, "
     "machine learning tools, or artificial intelligence (AI) systems without the prior written consent of NPR\"; "
     "its robots.txt also blocks AI crawlers. A permission letter to NPR has been drafted for the owner."),
    ("Radio Free Europe/Radio Liberty, Radio Free Asia, Alhurra/MBN", "US-funded but private corporations (grantees), "
     "not US government agencies: their reporting is their own copyright, not public domain, and no reuse licence "
     "was found (RFE/RL's terms pages could not be found automatically; rfa.org and alhurra.com redirect)."),
    ("PBS NewsHour transcripts", "Copyright of NewsHour Productions; not openly licensed."),
    ("C-SPAN", "Its own video and transcripts are its copyright (and c-span.org refuses automated requests). House "
     "and Senate floor proceedings are public domain; their record is the Congressional Record (govinfo), not built "
     "yet."),
    ("White House, State Department and Defense Department briefings and transcripts", "Public domain (whitehouse.gov: "
     "\"government-produced materials appearing on this site are not copyright protected\"), but whitehouse.gov's "
     "API and state.gov and defense.gov refuse automated requests (403)."),
    ("Hansard of the Parliament of Canada and Government of Canada news releases", "Canada's House of Commons asks "
     "for the Speaker's permission to reproduce its proceedings (parliamentary privilege); the canada.ca web pages "
     "(news releases among them) allow only non-commercial reproduction. Not built (a personal-use group would be "
     "needed). The publications deposited on open.canada.ca under the Open Government Licence - Canada are "
     "different (commercial use allowed): they are built as pub:canada_ogl."),
    ("CBC/Radio-Canada, BBC, ABC (Australia), RTÉ", "Copyright of each broadcaster; not openly licensed (abc.net.au "
     "and rte.ie also refuse automated requests to their terms pages)."),
    ("Hansard of the Parliament of Australia and Australian government media releases", "aph.gov.au blocks automated "
     "requests (\"Page Blocked by WAF\"); not checked further."),
    ("RNZ, New Zealand Hansard and Beehive releases", "RNZ's terms page could not be found automatically (robots.txt "
     "asks Crawl-delay 7); parliament.nz allows all robots and beehive.govt.nz has a copyright page, but their "
     "licence wording could not be read automatically (pages built by scripts). Check by hand before adding."),
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
    ("UK National Archives education resources (the old /education/resources/ pages)", "Re-checked 2026-11-21: its "
     "robots.txt now says \"Content-Signal: ai-train=no, search=yes, ai-input=yes\" (it said ai-input=no before). "
     "An offline reference book that the person reads and the Assistant searches to answer them is AI input "
     "(allowed); it never trains or fine-tunes a model (ai-train=no obeyed). So the CURRENT teaching resources are "
     "built (guide:uk_national_archives_teaching_resources, Open Government Licence, one page every 10 seconds as "
     "its Crawl-delay asks; reasoning in reference_more.py). The old pages listed here are gone from the site (410, or "
     "moved to the new resources), so they are not built."),
    ("Dictionary of Canadian Biography and Australian Dictionary of Biography", "Copyright of their publishers "
     "(University of Toronto/Université Laval; Australian National University): not openly licensed."),
    ("Wikisource and Project Gutenberg history books", "Already in the Kiwix library."),
    ("Low-tech Magazine", "Already in the Kiwix library (solar.lowtechmagazine.com_mul_all), so not built again."),
    ("VOA broadcasts before the web (1942 to 2000) other than the 1970s scripts", "They survive mostly as sound "
     "recordings (out of scope: no text). The Library of Congress's microfilm of VOA scripts (1953-1980) is on the "
     "Internet Archive as text only for the 1970s so far. The National Archives catalogue's API needs a key and its "
     "robots.txt disallows automated reading, so nothing is taken from it."),
    ("Make:, Hackaday, Practical Action", "Copyright of their publishers, or no licence stated."),
]


# ====================================================================== keys

def _back(first, today=None, skip_current=False):
    """Years from this year (or last year) back to first, newest first, as strings."""
    year = (today or datetime.date.today()).year - (1 if skip_current else 0)
    return [str(y) for y in range(year, first - 1, -1)]


US_STATES = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
             "district-of-columbia", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas",
             "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
             "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey", "new-mexico", "new-york",
             "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode-island",
             "south-carolina", "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington",
             "west-virginia", "wisconsin", "wyoming", "puerto-rico", "virgin-islands"]


def frus_volumes():
    """Every volume id of Foreign Relations of the United States in the Office of the Historian's repository (its
    file list, read with git without downloading the volumes), newest first."""
    import subprocess
    import tempfile
    folder = os.path.join(tempfile.gettempdir(), "frus-list")
    try:
        if not os.path.isdir(os.path.join(folder, ".git")):
            subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout",
                            SOURCES["frus"]["repo"], folder], check=True, timeout=1800)
        names = subprocess.run(["git", "-C", folder, "ls-tree", "--name-only", "HEAD", "volumes/"],
                               capture_output=True, text=True, check=True).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return list(SOURCES["frus"]["pieces"](None))
    ids = [n.rsplit("/", 1)[-1][:-4] for n in names if n.endswith(".xml")]
    return sorted(ids, key=lambda v: (re.search(r"\d{4}", v).group(0) if re.search(r"\d{4}", v) else "0", v),
                  reverse=True)


# Every source's pieces back to its beginning, newest first (the backfill works through them; they can also be
# built by key). The earliest years were checked on 2026-11-19.
ALL_PIECES = {
    "voa_history": lambda t: VOA_HISTORY_MONTHS + ["1990s", "1980s", "1960s", "1950s", "1940s"],
    "voa_learning": lambda t: _back(2001, t, True),
    "state_milestones": lambda t: ["all"],
    "frus": lambda t: frus_volumes(),
    "crs": lambda t: _back(1971, t, True),
    "amber_waves": lambda t: ["2020s", "2010s", "2000s"],
    "kff_health_news": lambda t: _back(2009, t, True),
    "global_voices": lambda t: _back(2004, t, True),
    "elife_digests": lambda t: _back(2012, t, True),
    "europepmc_reviews": lambda t: list(EPMC_TOPICS) + [f"{k}-{y}" for y in _back(2000, t)[6:] for k in EPMC_TOPICS],
    "govuk_speeches": lambda t: _back(2000, t, True),
    "oireachtas_debates": lambda t: _back(1919, t, True),
    "voa": lambda t: _back(1995, t, True),
    "nasa_news": lambda t: _back(2004, t, True),
    "the_conversation": lambda t: [f"{e}-{y}" for y in _back(2011, t, True)
                                   for e in ("us", "uk", "au", "ca", "africa", "global", "nz", "europe")],
    "uk_hansard": lambda t: _back(1803, t, True),
    "chronicling_america": lambda t: [f"{st}-{d}s" for d in range(1920, 1760, -10) for st in US_STATES],
}
# Small and quick sources first, then the big ones.
BACKFILL_ORDER = ["voa_history", "voa_learning", "state_milestones", "frus", "crs", "amber_waves", "kff_health_news",
                  "global_voices", "elife_digests", "europepmc_reviews", "govuk_speeches", "oireachtas_debates", "voa",
                  "nasa_news", "the_conversation", "uk_hansard", "chronicling_america"]


def daily_keys(today=None):
    """The keys of the daily refresh (the workflow's daily schedule): every source's spec["daily"] pieces (the
    current ones). The pieces read from Voice of America's two sites are joined with "+" into one key, so they are
    built one after another in one job (one request at a time to VOA)."""
    voa, other = [], []
    for name, spec in SOURCES.items():
        for piece in spec.get("daily", lambda t: [])(today):
            (voa if spec.get("driver") == "voa" else other).append(f"pub:{name}:{piece}")
    return (["+".join(voa)] if voa else []) + other


def done_keys(catalogue):
    """The piece keys already collected: in the catalogue's "pieces_done" (built complete, or found empty), or a book
    built from the key that is not marked "complete": false."""
    done = set((catalogue or {}).get("pieces_done", []))
    done |= {b["key"] for b in (catalogue or {}).get("books", []) if b.get("key") and b.get("complete") is not False}
    return done


def next_backfill(catalogue, today=None, pieces=None):
    """The next piece the backfill schedule builds: the first source of BACKFILL_ORDER with a piece not yet collected
    (newest first; a piece marked "complete": false is built again to go on); "" when everything is collected.
    pieces: {source: list of pieces} instead of ALL_PIECES (for tests)."""
    done = done_keys(catalogue)
    # A piece that failed three times (a site that stopped answering) is skipped so the others go on; it can still
    # be built by key, and a success clears it.
    done |= {k for k, n in (catalogue or {}).get("pieces_failed", {}).items() if n >= 3}
    for name in BACKFILL_ORDER:
        for piece in pieces[name] if pieces is not None and name in pieces else ALL_PIECES[name](today):
            key = f"pub:{name}:{piece}"
            if key not in done and not (len(piece) == 7 and f"pub:{name}:{piece[:4]}" in done):
                return key                     # (a month whose whole year was already built counts as done)
    return ""


def expand_keys(words, today=None):
    """The one-piece keys ("pub:crs:2026") of a list of words ("pub:all", "pub:news", "pub:crs", "pub:crs:2026",
    "pub:daily"); keys joined with "+" (built one after another in one job) are kept joined when every part is
    valid."""
    out = []
    for w in words:
        if "+" in w:
            parts = w.split("+")
            if all(expand_keys([x], today) == [x] for x in parts):
                out.append(w)
            continue
        if w == "pub:daily":
            out += daily_keys(today)
            continue
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
    """True when the site's robots.txt allows url (spec: the source; no source is exempt)."""
    return B.allowed_by_robots(url, cache)


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
    their label and caption ("Figure 2: ..."), tables stay tables, formulas become text (mathtext), and the back
    matter is kept whole (acknowledgements, appendices, notes, and the reference list as a numbered list: since the
    reference-library audit of 2026-11-21, so each article is the whole document)."""

    INLINE = {"bold": "strong", "italic": "em", "sup": "sup", "sub": "sub", "underline": "em", "sc": ""}
    SKIP = {"object-id", "graphic", "media", "alternatives", "inline-graphic",
            "label", "title", "caption", "table-wrap-foot", "permissions", "funding-group"}
    DEFAULT_TITLES = {"ack": "Acknowledgements", "ref-list": "References", "fn-group": "Notes", "app": "Appendix"}

    @staticmethod
    def reference(ref):
        """One reference of a reference list in words: a mixed citation as written (it has its own punctuation),
        an element citation as its parts joined by spaces."""
        cite = next((x for x in ref if _tag(x) in ("mixed-citation", "element-citation", "citation")), ref)
        if _tag(cite) == "element-citation":
            return " ".join(t.strip() for t in cite.itertext() if t.strip())
        return " ".join("".join(cite.itertext()).split())

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
        if tag == "ref-list":
            title = el.find("{*}title")
            words = self.html(title, depth) if title is not None and _words(title) else \
                ("References" if depth <= 2 else "")    # inside a section already titled: no second heading
            refs = "".join(f"<li>{B.esc(self.reference(r))}</li>" for r in el if _tag(r) == "ref")
            inner = "".join(self.convert(x, min(depth + 1, 6)) for x in el if _tag(x) == "ref-list")
            return (f"<h{depth}>{words}</h{depth}>" if words else "") + (f"<ol>{refs}</ol>" if refs else "") + inner
        if tag == "fn":
            return f"<p>{self.html(el, depth)}</p>" if not el.findall("{*}p") else self.html(el, depth)
        if tag in ("sec", "boxed-text", "ack", "fn-group", "app", "app-group", "glossary"):
            title = el.find("{*}title")
            words = self.html(title, depth) if title is not None and _words(title) else self.DEFAULT_TITLES.get(tag, "")
            head = f"<h{depth}>{words}</h{depth}>" if words else ""
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
    stated). The body starts with its plain-language summary (when it has one), then the abstract, the text and the
    back matter (acknowledgements, appendices, notes and references)."""
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
    summary = ""
    for a in abstracts:
        kind = a.get("abstract-type", "")
        t = a.find("{*}title")
        heading = _words(t) or ("Plain-language summary" if kind in SUMMARY_TYPES else "Abstract")
        parts.append(f"<h2>{B.esc(heading)}</h2>" + j.html(a, 3))
        if not summary and (kind in SUMMARY_TYPES or "digest" in heading.lower()):
            summary = Jats().html(a, 2)
    body = next((x for x in root if _tag(x) == "body"), None)
    if body is not None:
        parts.append(j.html(body, 2))
    back = next((x for x in root if _tag(x) == "back"), None)
    if back is not None:                              # acknowledgements, appendices, notes, references
        parts.append(j.html(back, 2))
    return {"title": title, "authors": authors, "journal": journal, "date": date, "doi": doi, "licence": licence,
            "licence_url": licence_url, "body": "".join(parts), "summary": summary}


def epmc_articles(spec, query, want, cache, left_out, title, wanted=None):
    """The newest articles a Europe PMC search finds (newest first, 100 a page), each read from its full text
    (jats_article) and kept only when its own licence is CC BY or CC0, and wanted(article) is true; at most want.
    Returns [(search result, article)]."""
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
            if wanted is None or wanted(art):
                out.append((r, art))
        nxt = data.get("nextCursorMark")
        if not results or not nxt or nxt == cursor:
            break
        cursor = nxt
    if refused:
        left_out.append({"title": title, "reason": f"{refused} articles were left out: their own licence is not "
                         "CC BY or CC0, or their text could not be read."})
    return out


def epmc_credit(r, art):
    """(date, credit line) of a Europe PMC article: the first day it was public online (the issue date in the
    article can lie in the future), and its authors, title, journal, date and DOI."""
    when = B.iso_date(r.get("firstPublicationDate", "")) or art["date"]
    return when, (f"{art['authors']}. {art['title']}. {art['journal']}, {when}."
                  f"{(' DOI ' + art['doi'] + '.') if art['doi'] else ''}")


def europepmc_items(spec, piece, cache, left_out, today):
    """The newest review articles on the topic piece (EPMC_TOPICS) in Europe PMC's open-access subset under CC BY
    or CC0 (asked for in the search, and checked again in each article's own text), at most spec["per_piece"]."""
    year = (today or datetime.date.today()).year
    topic, _, only = piece.partition("-")              # "vision" (the last years) or "vision-2015" (one older year)
    name, words = EPMC_TOPICS[topic]
    first, last = (int(only), int(only)) if only else (year - spec["years_back"], year)
    name = f"{name}, {only}" if only else name
    query = (f"(TITLE:({words}) OR KW:({words})) AND (LICENSE:\"cc by\" OR LICENSE:\"cc0\") AND OPEN_ACCESS:y AND "
             f"PUB_TYPE:\"review\" AND LANG:eng AND IN_EPMC:y AND FIRST_PDATE:[{first}-01-01 TO {last}-12-31]")
    out = []
    for r, art in epmc_articles(spec, query, spec.get("per_piece", 150), cache, left_out,
                                f"{spec['series_title']}: {name}"):
        when, credit = epmc_credit(r, art)
        body = clean(art["body"], "https://europepmc.org/")
        out.append(item(f"https://europepmc.org/article/PMC/{r['pmcid']}", art["title"] or r.get("title", ""), when,
                        body, month_unit(when)[-4:], byline=credit, licence=art["licence"],
                        licence_url=art["licence_url"] or B._licence_address(art["licence"])))
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


def elife_digest_items(spec, piece, cache, left_out, today):
    """The papers first published in the year piece that have an eLife digest (the plain-language summary eLife's
    editors write for some of its papers), taken from each paper's open-access full text in Europe PMC (CC BY or
    CC0, checked per paper): the whole paper, its digest first, with the paper's credit. eLife's own API is not used
    (its robots.txt disallows all)."""
    query = (f"JOURNAL:\"eLife\" AND \"eLife digest\" AND OPEN_ACCESS:y AND (LICENSE:\"cc by\" OR LICENSE:\"cc0\") "
             f"AND FIRST_PDATE:[{piece}-01-01 TO {piece}-12-31]")
    out = []
    for r, art in epmc_articles(spec, query, spec.get("limit", MAX_ITEMS), cache, left_out,
                                f"{spec['series_title']}, {piece}", wanted=lambda a: bool(a["summary"])):
        when, credit = epmc_credit(r, art)
        body = clean(art["body"], "https://elifesciences.org/")        # the digest first, then the whole paper
        out.append(item(f"https://europepmc.org/article/PMC/{r['pmcid']}", art["title"] or r.get("title", ""), when,
                        body, month_unit(when), byline=credit, licence=art["licence"],
                        licence_url=art["licence_url"] or B._licence_address(art["licence"])))
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


def conversation_archive_items(spec, piece, cache, left_out, today):
    """The articles of one edition and year of The Conversation (piece "us-2015"), from its yearly archive sitemap
    (theconversation.com/<edition>/sitemap_archive_<year>.xml), each read from its page and kept whole and unchanged
    (the article body, with its authors and date); stops after spec["budget_minutes"] (the next run goes on from the
    cache)."""
    import time
    edition, year = piece.rsplit("-", 1)
    found = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>",
                       B.fetch(f"https://theconversation.com/{edition}/sitemap_archive_{year}.xml", None))
    out, failed, start, whole = [], 0, time.monotonic(), bool(spec.get("unchanged"))
    for number, url in enumerate(found):
        if time.monotonic() - start > spec.get("budget_minutes", 200) * 60:
            INCOMPLETE[(spec["name"], piece)] = (number, len(found))
            left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"Not finished in this run: "
                             f"{number} of {len(found)} articles read; build the key again to go on."})
            break
        if not robots_ok(spec, url, cache):
            failed += 1
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        raw = div_inner(text, r'<div[^>]*itemprop="articleBody"[^>]*>')
        if not raw:
            failed += 1
            continue
        for pattern in spec.get("drop_html", []):
            raw = re.sub(pattern, "", raw)
        when = B.iso_date((re.search(r'itemprop="datePublished"[^>]*content="([^"]+)"', text) or
                           re.search(r'<time[^>]*datetime="([^"]+)"', text) or [None, ""])[1])
        authors = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", a)).split())
                   for a in re.findall(r'<a[^>]*class="[^"]*author-name[^"]*"[^>]*>(.*?)</a>', text, re.S)]
        credit = f"{spec['credit']} " if spec.get("credit") else ""
        out.append(item(url, B.first_heading(text), when, clean(raw, url, whole), month_unit(when),
                        byline=f"{credit}By {'; '.join(authors)}" if authors else credit.strip()))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} articles could not be "
                         "read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


def atom_items(spec, piece, cache, left_out, today):
    """The articles of a news feed (spec["feed"] with the piece, such as The Conversation's edition "us"), each
    kept whole and unchanged; an entry whose own <rights> does not match spec["rights"] is left out."""
    if re.search(r"-\d{4}$", piece):                         # a year of an edition: its archive sitemap
        return conversation_archive_items(spec, piece, cache, left_out, today)
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
        raw = content.text if content is not None and content.text else ""
        for pattern in spec.get("drop_html", []):                # invisible counters only, never text
            raw = re.sub(pattern, "", raw)
        body = clean(raw, link, whole)
        credit = f"{spec['credit']} " if spec.get("credit") else ""
        out.append(item(link, _words(e.find(f"{ATOM}title")), when, body, month_unit(when),
                        byline=f"{credit}By {authors}" if authors else credit.strip()))
    if wrong:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{wrong} articles were left out: "
                         "their own licence line is not the one that was checked."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== Voice of America (and Learning English)

VOA_SITE = "https://www.voanews.com"
# Material VOA licenses from news agencies or takes from partners is not in the public domain: a story whose byline
# or text names a news agency, or says it was published first elsewhere, is left out whole.
WIRE = re.compile(r"\b(Associated Press|Reuters|Agence France[- ]Presse|AFP|Bloomberg|Xinhua|United Press "
                  r"International|UPI|Deutsche Presse-Agentur|dpa|Kyodo|Yonhap|ANSA|EFE|Getty Images)\b|\(AP\)|"
                  r"\bAP\b|originally (?:been )?published|republished (?:with|from|by)|reprinted with permission")
SLUG_DATE = re.compile(r"-((?:19|20)\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])-")
INCOMPLETE = {}                  # (source, piece) -> (stories read, stories listed) of a year not finished in time


def voa_sitemap(spec):
    """[(address, lastmod)] of every story (/a/) in the site's sitemaps (read fresh), newest sitemap first."""
    site = spec.get("site", VOA_SITE)
    index = B.fetch(f"{site}/sitemap.xml", None)
    maps = [u for u in re.findall(r"<loc>\s*([^<\s]+\.xml\.gz)\s*</loc>", index)]
    maps.sort(key=lambda u: [int(n) for n in re.findall(r"\d+", u.rsplit("/", 1)[-1])])
    for m in maps:
        data = B.fetch(m, None, binary=True)
        try:
            data = gzip.decompress(data)
        except OSError:
            pass                                             # already unpacked
        found = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>\s*<lastmod>\s*([^<\s]+)", data.decode("utf-8", "replace"))
        yield [(u, when) for u, when in found if "/a/" in u]


def voa_year_of(url, lastmod):
    """The year a story belongs to: the date in its address when it has one (older stories: "a-13-2008-05-31-
    voa7"; their pages say the day the site moved, 2009), else the year of its last change."""
    m = SLUG_DATE.search(url)
    return m.group(1) if m else lastmod[:4]


def voa_story(spec, url, cache, records=None):
    """("story", item) for one of VOA's own stories, ("wire", None) for one with news-agency or partner material,
    ("none", None) for a page that is not a written story (a video or audio page) or cannot be read. records: what
    earlier runs found ({address: [kind, item]}, from the year's records file in the release, see load_records); a
    story found there is not read again, and what is read now is added to it."""
    if records is not None and url in records:
        kind, found = records[url]
        return kind, found
    kind, found = "none", None
    if robots_ok(spec, url, cache):
        try:
            text = B.fetch(url, None)
        except (urllib.error.URLError, OSError):
            return "none", None                              # not recorded: tried again next time
        art = next((d for d in json_ld(text) if d.get("@type") in ("NewsArticle", "Article", "ReportageNewsArticle")),
                   {})
        authors = art.get("author") or []
        authors = [a.get("name", "") for a in (authors if isinstance(authors, list) else [authors])
                   if isinstance(a, dict)]
        raw = div_inner(text, r'<div class="wsw">')
        plain = html.unescape(re.sub(r"<[^>]+>", " ", raw))
        if raw and (any(WIRE.search(a) for a in authors) or WIRE.search(plain)):
            kind = "wire"
        elif raw and plain.strip():
            m = SLUG_DATE.search(url)
            when = "-".join(m.groups()) if m else (B.iso_date(art.get("datePublished", "")) or B.page_date(text))
            title = B.first_heading(text) or html.unescape(art.get("headline") or art.get("name") or "")
            kind = "story"
            found = item(url, title, when, clean(raw, url), month_unit(when),
                         byline=("By " + ", ".join(a for a in authors if a)) if any(authors) else "")
    if records is not None:
        records[url] = [kind, found]
    return kind, found


# The records of a long piece (what each address turned out to be, with the stories' text) are published in the
# release next to the book, as <book name>.records.json.xz, so a year built over many runs never depends on the
# Actions cache (which drops old entries). SIDE_FILES collects the files build_periodicals writes and uploads.
SIDE_FILES = {}                  # (source, piece) -> (file name, bytes)


def release_for(name):
    """The GitHub release a source's books are published in ("publications-voa"): one release per source keeps each
    under GitHub's limit of 1,000 files per release (the textbooks have their own release, "textbooks")."""
    return f"publications-{name.replace('_', '-')}"


def release_url(name):
    """The download address of a source's release."""
    return f"{B.RELEASE.rsplit('/', 1)[0]}/{release_for(name)}"


def records_name(name, piece):
    """The file name of a piece's records in the release ("voa_2008.records.json.xz")."""
    return f"{name}_{piece}.records.json.xz"


def load_records(name, piece):
    """{address: [kind, item]} from the piece's records file in the release ({} when there is none yet)."""
    import lzma
    try:
        data = B.fetch(f"{release_url(name)}/{records_name(name, piece)}", None, binary=True)
        return json.loads(lzma.decompress(data).decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError, lzma.LZMAError):
        return {}


def keep_records(name, piece, records):
    """Remember the piece's records to be written and uploaded next to its book (sorted, xz-compressed)."""
    import lzma
    data = json.dumps(dict(sorted(records.items())), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    SIDE_FILES[(name, piece)] = (records_name(name, piece), lzma.compress(data, preset=9))


WAYBACK = "https://web.archive.org"
WAYBACK_PAUSE = 5.0
VOA_OLD_HOSTS = ["www.voa.gov", "voa.gov", "www.voanews.com", "voanews.com"]
# The first part of an address on VOA's old sites that names a service in another language (left out: English only).
VOA_LANGUAGES = {
    "albanian", "amharic", "arabic", "armenian", "azeri", "bangla", "bengali", "bosnian", "brazilian", "bulgarian",
    "burmese", "cantonese", "chinese", "croatian", "czech", "dari", "estonian", "farsi", "french", "georgian",
    "greek", "hausa", "hindi", "hungarian", "indonesian", "khmer", "kinyarwanda", "kirundi", "korean", "kurdish",
    "lao", "latvian", "lithuanian", "macedonian", "mandarin", "ndebele", "oromo", "pashto", "persian", "polish",
    "portuguese", "romanian", "russian", "serbian", "shona", "slovak", "slovene", "somali", "spanish", "swahili",
    "tibetan", "tigrigna", "turkish", "ukrainian", "urdu", "uzbek", "vietnamese", "afaan", "afl", "cpanel"}


def wayback_captures(spec, year, cache):
    """[(capture time, address)] of the web pages of VOA's old sites captured in one year by the Internet Archive's
    Wayback Machine (its documented CDX API: one capture per address, HTML answers with status 200, read 5,000 at a
    time), without the services in other languages, pictures and scripts."""
    out, seen = [], set()
    # The Wayback Machine limits automated use and stops answering for a while when asked too fast (seen from the
    # build machine on 2026-11-19): one request every WAYBACK_PAUSE seconds.
    B.CRAWL_DELAY["web.archive.org"] = max(B.CRAWL_DELAY.get("web.archive.org", 0), WAYBACK_PAUSE)
    for host in VOA_OLD_HOSTS:
        resume = ""
        while True:
            query = urllib.parse.urlencode({"url": f"{host}/*", "from": year, "to": year, "output": "json",
                                            "filter": ["statuscode:200", "mimetype:text/html"], "collapse": "urlkey",
                                            "fl": "timestamp,original", "limit": 5000, "showResumeKey": "true",
                                            **({"resumeKey": resume} if resume else {})}, doseq=True)
            try:
                rows = json.loads(B.fetch(f"{WAYBACK}/cdx/search/cdx?{query}", cache) or "[]")
            except (urllib.error.URLError, OSError, ValueError) as e:
                raise RuntimeError(f"the Wayback Machine did not answer ({e}); try again later") from e
            resume = ""
            if rows and rows[-1] and len(rows[-1]) == 1:     # the last row is the key to read on from
                resume = rows[-1][0]
                rows = rows[:-2] if len(rows) > 1 and not rows[-2] else rows[:-1]
            for row in rows[1:] if rows and rows[0] == ["timestamp", "original"] else rows:
                if len(row) != 2:
                    continue
                ts, url = row
                path = urllib.parse.urlsplit(url).path.lower()
                first = path.strip("/").split("/")[0] if path.strip("/") else ""
                if first in VOA_LANGUAGES or not re.search(r"\.(s?html?|cfm|asp)$", path):
                    continue
                key = re.sub(r"^https?://(www\.)?", "", url.lower()).replace(":80/", "/")
                if key not in seen:
                    seen.add(key)
                    out.append((ts, url))
            if not resume:
                break
    return out


def voa_wayback_story(spec, ts, url, records):
    """("story", item), ("wire", None) or ("none", None) for one page of VOA's old sites as the Wayback Machine
    captured it (its original HTML, the "id_" form): a written English story of at least 120 words, without
    news-agency material; dated by the date it gives ("DATE=5/31/98", "May 31, 1998") or else the capture's day."""
    if url in records:
        return records[url]
    kind, found = "none", None
    try:
        text = B.fetch(f"{WAYBACK}/web/{ts}id_/{url}", None)
    except (urllib.error.URLError, OSError):
        return "none", None
    body = re.search(r"(?is)<body\b[^>]*>(.*)</body>", text)
    body = body.group(1) if body else text
    plain = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ",
                                                                   body))).split())
    if len(plain.split()) >= 120:
        if WIRE.search(plain):
            kind = "wire"
        else:
            m = re.search(r"DATE=\s*(\d{1,2})/(\d{1,2})/(\d{2,4})", plain)
            if m:
                y = int(m.group(3)) + (1900 if len(m.group(3)) == 2 and int(m.group(3)) > 40 else 0) + \
                    (2000 if len(m.group(3)) == 2 and int(m.group(3)) <= 40 else 0)
                when = f"{y:04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
            else:
                when = B.iso_date(plain[:600]) or f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
            if not when.startswith(ts[:2]) and not when.startswith("19") and not when.startswith("20"):
                when = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
            title = re.search(r"(?is)<title[^>]*>(.*?)</title>", text)
            title = " ".join(html.unescape(title.group(1)).split()) if title else url
            kind, found = "story", item(f"{WAYBACK}/web/{ts}/{url}", title, when,
                                        clean(body, f"{WAYBACK}/web/{ts}/{url}"), month_unit(when),
                                        byline="Voice of America (as captured by the Internet Archive's Wayback "
                                               "Machine)")
    records[url] = [kind, found]
    return kind, found


def voa_items(spec, piece, cache, left_out, today):
    """VOA's own stories, newest first: piece "recent" (changed in the last spec["days"] days) or a year ("2019":
    every story of that year in the sitemaps, back to 2001). Stories with news-agency or partner material are left
    out whole. A year is large (up to about 80,000 addresses at one request a second), so a run stops after
    spec["budget_minutes"] and the book says how far it got (INCOMPLETE); the next run goes on from the year's
    records file in the release (load_records)."""
    import time
    if spec["name"] == "voa" and piece != "recent" and piece < "2001":
        return voa_wayback_items(spec, piece, cache, left_out, today)
    if piece == "recent":
        since = ((today or datetime.date.today()) - datetime.timedelta(days=spec.get("days", 60))).isoformat()
        urls = []
        for found in voa_sitemap(spec):
            recent = [u for u, when in found if when[:10] >= since]
            urls += [u for u in recent if u not in urls]
            if not recent or len(urls) >= spec.get("limit", 1500):
                break
        urls = urls[:spec.get("limit", 1500)]
    else:
        urls = list(dict.fromkeys(u for found in voa_sitemap(spec) for u, when in found
                                  if voa_year_of(u, when) == piece))
        urls = urls[:spec.get("limit", 200000)]
    out, counts, start = [], {"wire": 0, "none": 0}, time.monotonic()
    budget = spec.get("budget_minutes", 200) * 60
    records = load_records(spec["name"], piece) if piece != "recent" else None
    for number, url in enumerate(urls):
        if piece != "recent" and time.monotonic() - start > budget:
            INCOMPLETE[(spec["name"], piece)] = (number, len(urls))
            left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"Not finished in this run: "
                             f"{number} of {len(urls)} addresses read; build the key again to go on (the cache keeps "
                             "what was read)."})
            break
        kind, found = voa_story(spec, url, cache, records)
        if kind == "story":
            out.append(found)
        else:
            counts[kind] += 1
    if records is not None:
        keep_records(spec["name"], piece, records)
    if counts["wire"] or counts["none"]:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{counts['wire']} stories with "
                         f"news-agency or partner material were left out; {counts['none']} addresses are not written "
                         "stories (video or audio pages) or could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


def voa_wayback_items(spec, piece, cache, left_out, today):
    """VOA's own English stories of a year before 2001 (piece "1998"), from the Wayback Machine's captures of VOA's
    old sites (www.voa.gov and voanews.com), one request at a time, within spec["budget_minutes"] a run; what was
    read is kept in the year's records file in the release (load_records), so the next run goes on."""
    import time
    records = load_records(spec["name"], piece)
    captures = wayback_captures(spec, piece, cache)
    out, counts, start = [], {"wire": 0, "none": 0}, time.monotonic()
    for number, (ts, url) in enumerate(captures):
        if time.monotonic() - start > spec.get("budget_minutes", 200) * 60:
            INCOMPLETE[(spec["name"], piece)] = (number, len(captures))
            left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"Not finished in this run: "
                             f"{number} of {len(captures)} captured pages read; build the key again to go on."})
            break
        kind, found = voa_wayback_story(spec, ts, url, records)
        if kind == "story" and found["date"][:4] == piece:
            out.append(found)
        elif kind != "story":
            counts[kind] += 1
    keep_records(spec["name"], piece, records)
    if counts["wire"] or counts["none"]:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{counts['wire']} pages with "
                         f"news-agency material were left out; {counts['none']} captured pages are not stories "
                         "(menus, schedules, short pages) or could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== VOA radio scripts (Internet Archive)

IA = "https://archive.org"


def voa_history_items(spec, piece, cache, left_out, today):
    """VOA radio scripts of one year (piece "1975") or one decade (piece "1970s") from the Internet Archive's collection voa-radio-scripts
    (scanned from the Library of Congress's microfilm; Public Domain Mark), each script's machine-read (OCR) text.
    Only items marked public domain and credited to the Voice of America are kept."""
    first = int(piece[:4])
    last = first + 9 if piece.endswith("s") else first
    start, end = f"{first}-01-01", f"{last}-12-31"
    if len(piece) == 7:                                  # one month, "1976-03"
        month = int(piece[5:])
        start = f"{piece}-01"
        end = f"{piece}-{calendar.monthrange(first, month)[1]:02d}"
    query = urllib.parse.urlencode({"q": f"collection:{spec['collection']} AND date:[{start} TO "
                                         f"{end}]", "fl[]": ["identifier", "date"], "rows": 20000,
                                    "output": "json"}, doseq=True)
    search = f"{IA}/advancedsearch.php?{query}"
    if not robots_ok(spec, search, cache):
        return []
    docs = json.loads(B.fetch(search, None)).get("response", {}).get("docs", [])
    out, refused = [], 0
    for d in sorted(docs, key=lambda d: d.get("date", ""))[:spec.get("limit", MAX_ITEMS * 4)]:
        ident = d["identifier"]
        try:
            meta = json.loads(B.fetch(f"{IA}/metadata/{ident}", cache))
        except (urllib.error.URLError, OSError, ValueError):
            refused += 1
            continue
        m = meta.get("metadata", {})
        creator = " ".join(m.get("creator") if isinstance(m.get("creator"), list) else [m.get("creator") or ""])
        txt = next((f["name"] for f in meta.get("files", []) if f.get("format") == "DjVuTXT"), "")
        if "publicdomain" not in (m.get("licenseurl") or "") or "Voice of America" not in creator or not txt:
            refused += 1
            continue
        try:
            text = B.fetch(f"{IA}/download/{ident}/{urllib.parse.quote(txt)}", cache)
        except (urllib.error.URLError, OSError):
            refused += 1
            continue
        when = B.iso_date(m.get("date", ""))
        title = re.sub(r"\s*\(VOA Radio Script\)\s*$", "", m.get("title", ident))
        byline = re.sub(r",?\s*Voice of America\s*$", "", creator).strip()
        out.append(item(f"{IA}/details/{ident}", title, when, ocr_html(text), when[:4],
                        byline=f"By {byline}, Voice of America" if byline else "Voice of America"))
    if refused:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{refused} items were left out: not "
                         "marked public domain, not credited to the Voice of America, or without a text."})
    if not docs:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": "The Internet Archive has no VOA "
                         "radio scripts as text for these years (only the 1970s so far)."})
    return out


# ====================================================================== parliaments and government speeches

HANSARD_API = "https://hansard-api.parliament.uk"


def hansard_items(el, depth=3):
    """The HTML of a Hansard API debate's items and child debates: each contribution with its speaker's name."""
    parts = []
    for it in el.get("Items", []):
        value = it.get("Value") or ""
        if it.get("HRSTag") == "hs_ColumnNumber" or not re.sub(r"<[^>]+>", "", value).strip():
            continue
        who = it.get("AttributedTo")
        lead = f"<strong>{B.esc(who)}:</strong> " if who else ""
        tag = "h3" if it.get("ItemType") == "Timestamp" else "p"
        parts.append(f"<{tag}>{lead}{value}</{tag}>")
    for child in el.get("ChildDebates", []):
        title = (child.get("Overview") or {}).get("Title", "")
        parts.append(f"<h{depth}>{B.esc(title)}</h{depth}>" + hansard_items(child, min(depth + 1, 6)))
    return "".join(parts)


def uk_hansard_items(spec, piece, cache, left_out, today):
    """The debates of the House of Commons and the House of Lords in the year piece, from Parliament's Hansard API:
    each sitting day's main debates (the top of its section tree), one page each, under the sitting month. Days of the
    last two weeks are read fresh (the report is corrected for a while), older ones from the cache."""
    import time
    year, today = int(piece), today or datetime.date.today()
    fresh_from = today - datetime.timedelta(days=14)
    out, start, failed = [], time.monotonic(), 0
    day = datetime.date(year, 1, 1)
    while day.year == year and day <= today:
        if time.monotonic() - start > spec.get("budget_minutes", 200) * 60:
            INCOMPLETE[(spec["name"], piece)] = (day.timetuple().tm_yday, 365)
            left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"Not finished in this run: read "
                             f"up to {day}; build the key again (the cache keeps what was read)."})
            break
        use = None if day >= fresh_from else cache
        for house in ("Commons", "Lords"):
            url = f"{HANSARD_API}/overview/sectiontrees.json?date={day}&house={house}&section=Debate"
            try:
                trees = json.loads(B.fetch(url, use))
            except (urllib.error.URLError, OSError, ValueError):
                failed += 1
                continue
            for tree in trees if isinstance(trees, list) else []:
                nodes = tree.get("SectionTreeItems") or []
                root = next((n["Id"] for n in nodes if n.get("ParentId") is None), None)
                for n in nodes:
                    if n.get("ParentId") != root or not n.get("ExternalId") or n.get("HRSTag") == "hs_3MainHdg":
                        continue
                    try:
                        debate = json.loads(B.fetch(f"{HANSARD_API}/debates/debate/{n['ExternalId']}.json", use))
                    except (urllib.error.URLError, OSError, ValueError):
                        failed += 1
                        continue
                    body = clean(hansard_items(debate), "https://hansard.parliament.uk/")
                    if not body:
                        continue
                    where = (debate.get("Overview") or {}).get("Location") or f"House of {house}"
                    title = f"{' '.join((n.get('Title') or '').split())} ({where}, {day})"
                    link = f"https://hansard.parliament.uk/{house}/{day}/debates/{n['ExternalId']}"
                    out.append(item(link, title, day.isoformat(), body, month_unit(day.isoformat())))
        day += datetime.timedelta(days=1)
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} days or debates could "
                         "not be read."})
    return out


OIREACHTAS_API = "https://api.oireachtas.ie/v1"


def akn_html(el, depth=2):
    """The HTML of an Akoma Ntoso debate record (the Oireachtas' XML): headings of its sections, each speech's
    speaker before their paragraphs, and the paragraphs; everything else as its words."""
    parts = [B.esc(el.text)] if el.text and el.text.strip() else []
    for child in el:
        tag = _tag(child)
        if tag in ("meta", "recordedTime"):
            pass
        elif tag == "heading":
            parts.append(f"<h{depth}>{B.esc(_words(child))}</h{depth}>")
        elif tag == "debateSection":
            parts.append(akn_html(child, min(depth + 1, 6)))
        elif tag == "from":
            parts.append(f"<p><strong>{B.esc(_words(child))}:</strong></p>")
        elif tag in ("p", "summary", "narrative"):
            parts.append(f"<p>{B.esc(_words(child))}</p>")
        else:
            parts.append(akn_html(child, depth))
        if child.tail and child.tail.strip():
            parts.append(B.esc(child.tail))
    return "".join(parts)


def oireachtas_items(spec, piece, cache, left_out, today):
    """The sitting days of Dáil Éireann and Seanad Éireann in the year piece, from the Oireachtas open data API, one
    page per chamber and day (the day's whole debate record). Days of the last two weeks are read fresh."""
    today = today or datetime.date.today()
    fresh_from = (today - datetime.timedelta(days=14)).isoformat()
    out, failed, skip = [], 0, 0
    while True:
        query = urllib.parse.urlencode({"chamber_type": "house", "date_start": f"{piece}-01-01",
                                        "date_end": f"{piece}-12-31", "limit": 200, "skip": skip})
        data = json.loads(B.fetch(f"{OIREACHTAS_API}/debates?{query}", None))
        results = data.get("results", [])
        for r in results:
            rec = r.get("debateRecord", {})
            day = rec.get("date", "")
            chamber = (rec.get("chamber") or {}).get("showAs") or (rec.get("house") or {}).get("showAs", "")
            xml = ((rec.get("formats") or {}).get("xml") or {}).get("uri")
            if not xml or not day:
                continue
            try:
                root = ET.fromstring(B.fetch(xml, None if day >= fresh_from else cache).encode("utf-8"))
            except (urllib.error.URLError, OSError, ET.ParseError):
                failed += 1
                continue
            body = clean(akn_html(root), "https://www.oireachtas.ie/")
            link = xml.rsplit("/debate/", 1)[0].replace("https://data.oireachtas.ie/akn/ie/debateRecord/",
                                                         "https://www.oireachtas.ie/en/debates/debate/")
            out.append(item(link, f"{chamber} debates, {day}", day, body, month_unit(day)))
        skip += len(results)
        if len(results) < 200:
            break
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} days could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


GOVUK = "https://www.gov.uk"


def govuk_speeches_items(spec, piece, cache, left_out, today):
    """The speeches published on GOV.UK in the year piece (search API, document type "speech", then each one's
    record from the content API): the speech as published, the speaker, department, and the day it was delivered."""
    out, start, failed = [], 0, 0
    while True:
        query = urllib.parse.urlencode({"filter_content_store_document_type": "speech", "count": 1000,
                                        "start": start, "order": "-public_timestamp",
                                        "filter_public_timestamp": f"from:{piece}-01-01,to:{piece}-12-31",
                                        "fields": "link,public_timestamp"})
        data = json.loads(B.fetch(f"{GOVUK}/api/search.json?{query}", None))
        results = data.get("results", [])
        for r in results:
            link = r.get("link", "")
            if len(out) >= spec.get("limit", 20000):
                break
            if not link.startswith("/"):
                continue
            try:
                d = json.loads(B.fetch(f"{GOVUK}/api/content{link}", cache))
            except (urllib.error.URLError, OSError, ValueError):
                failed += 1
                continue
            det = d.get("details") or {}
            when = B.iso_date(det.get("delivered_on") or d.get("first_published_at") or r.get("public_timestamp", ""))
            links = d.get("links") or {}
            who = ", ".join(x.get("title", "") for x in links.get("speaker", []))
            orgs = ", ".join(x.get("title", "") for x in links.get("organisations", []))
            kind = det.get("speech_type_explanation") or ""
            byline = "; ".join(x for x in (who, orgs, kind) if x)
            out.append(item(f"{GOVUK}{link}", d.get("title", link), when, clean(det.get("body", ""), f"{GOVUK}{link}"),
                            month_unit(when), byline=byline))
        start += len(results)
        if len(results) < 1000 or len(out) >= spec.get("limit", 20000):
            break
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} speeches could not be "
                         "read."})
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


DRIVERS = {"crs": crs_items, "amber_waves": amber_waves_items, "elife": elife_digest_items,
           "europepmc": europepmc_items,
           "wordpress": wordpress_items, "atom": atom_items, "voa": voa_items, "voa_history": voa_history_items,
           "milestones": milestones_items, "uk_hansard": uk_hansard_items, "oireachtas": oireachtas_items,
           "govuk_speeches": govuk_speeches_items,
           "frus": frus_items, "chronam": chronam_items}


# ====================================================================== the books

def piece_label(name, piece):
    """How a piece is named in its book's title ("2026", "the 2010s", "Blindness and low vision", "recent")."""
    if name == "europepmc_reviews":
        topic, _, only = piece.partition("-")
        return EPMC_TOPICS[topic][0] + (f", {only}" if only else "")
    if name == "uk_hansard" and piece.isdigit():
        return piece
    if name == "voa" and piece == "recent":
        return "recent stories"
    if name == "the_conversation" and re.search(r"-\d{4}$", piece):
        edition, year = piece.rsplit("-", 1)
        return f"{piece_label(name, edition)}, {year}"
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
    if spec.get("repo"):                       # the source's own open repository (TEI files), as a zip
        book.originals.append({"url": spec["repo"].rstrip("/") + "/archive/HEAD.zip", "kind": "zip"})
    if spec["driver"] == "crs":                 # the list of every report, with each report's files
        book.originals.append({"url": CRS_SITE + "reports.csv", "kind": "csv"})
    book.originals += [{"url": i["url"], "kind": "html"} for i in items[:MAX_ORIGINALS]]   # each item's original
    book.personal_use = bool(spec.get("personal_use"))   # a non-commercial source: "personal use only"
    book.published = PUBLISHED.get((name, piece)) or B.newest_date([i["date"] for i in items])
    book.series, book.piece, book.item_dates = name, piece, [i["date"] for i in items]
    book.incomplete = INCOMPLETE.get((name, piece))
    if book.incomplete:
        book.description += (f" Not complete yet: {book.incomplete[0]:,} of {book.incomplete[1]:,} addresses read; "
                             "each build adds more.")
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
    spec = SOURCES.get(getattr(book, "series", ""), {})
    note = " ".join(x for x in (GROUP_NOTES.get(book.group, ""), spec.get("catalogue_note", "")) if x)
    done = getattr(book, "incomplete", None)
    return {"group_name": GROUPS.get(book.group, book.group), "series": getattr(book, "series", ""),
            "piece": getattr(book, "piece", ""), "items": len(book.pages), "newest": dates[-1] if dates else "",
            "oldest": dates[0] if dates else "", "note": note, "complete": not done}


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
        spec = SOURCES[key.split(":")[1]]
        # News pieces and VOA years are rebuilt under the same monthly name; the other pieces keep every version.
        versioned = not spec.get("daily") and spec["driver"] != "voa"
        for book in books:
            entry = B.write_book(book, out_dir, date, versioned=versioned)
            entry.update(catalogue_extra(book))
            entry["key"] = key
            entry["release"] = release_for(spec["name"])         # its own release (see release_for)
            entry["url"] = f"{release_url(spec['name'])}/{entry['file']}"
            if versioned:
                import updates                   # here, not at the top: updates imports the builder
                entry["fingerprint"] = updates.pub_sign(key)
            print(f"{entry['file']}: {entry['items']} items, {entry['size']:,} bytes, {entry['licence']}")
            entries.append(entry)
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower())
        files = [e["file"] for e in entries]
        for (name, piece), (side, data) in list(SIDE_FILES.items()):
            if f"pub:{name}:{piece}" == key:                 # the piece's records, uploaded next to its book
                with open(os.path.join(out_dir, side), "wb") as f:
                    f.write(data)
                files.append(side)
                del SIDE_FILES[(name, piece)]
        _src, _name, _piece = key.split(":", 2)
        finished = (_name, _piece) not in INCOMPLETE and not any("could not be built" in x["reason"] for x in left_out)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": release_for(key.split(":")[1]), "books": entries,
                    "left_out": left_out, "files": files, "failed": failed,
                    "done": [key] if finished else []}         # collected (or empty): the backfill moves on
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
    p.add_argument("--next-backfill", default=None, metavar="TEXTBOOKS_JSON",
                   help="print the next piece to backfill, from the published catalogue (nothing when all done)")
    a = p.parse_args(argv)
    if a.next_backfill is not None:
        catalogue = {}
        if os.path.exists(a.next_backfill):
            with open(a.next_backfill, encoding="utf-8") as f:
                catalogue = json.load(f)
        print(next_backfill(catalogue))
        return 0
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build_periodicals(a.keys, a.out, a.cache)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# More sources from the reference inventory of 2026-11-21 (Canada's Open Government Licence publications, GAO
# reports, the US Government Manual, ERIC open full texts, GOV.UK guides, UK safety alerts, USDA Farmers' Bulletins):
# publications_more.py adds them to SOURCES, DRIVERS, ALL_PIECES, LICENCE_LINES and NOT_INCLUDED when imported.
import publications_more  # noqa: E402,F401

# General-interest blogs and online magazines with open licences (Pluralistic, the Creative Commons blog, Waging
# Nonviolence, Wikimedia's Diff, EFF Deeplinks, the GDS accessibility blog), the owner's request of 2026-11-21:
# blogs.py adds them to SOURCES, DRIVERS, ALL_PIECES, BACKFILL_ORDER, LICENCE_LINES and NOT_INCLUDED when imported.
import blogs  # noqa: E402,F401
