"""More WCAG and accessibility guides for the "disability" group (Reference, disability and accessibility), the
owner's request of 2026-11-21 ("widen the accessibility part"). sources.py imports this module at its end and adds its
lists to NONPROFIT (the W3C documents, built by build_textbooks.webguide_book; keys nonprofit:<name>), GOV_GUIDES
(government web guides; keys guide:<name>), ALLOWED, LICENCE_LINES, NOT_INCLUDED and PRACTICE_SUBJECTS, so the
builder needs no change. Every book is "in full": every page of the guide, each whole.

Already in the library before this module (sources.py): WCAG 2.2 (w3c_wcag22), Understanding WCAG 2.2
(w3c_understanding_wcag22), the WAI tutorials (w3c_wai_tutorials), the WAI curricula (w3c_wai_curricula),
Section508.gov (section508_gov), ADA.gov's guidance (ada_gov_guidance), the 2010 ADA Standards (PDF), the ADA and ABA
Accessibility Guidelines (36 CFR part 1191, a law book), the ICEB Rules of Unified English Braille and GOV.UK's
guides for disabled people.

Added here (checked by hand on 2026-11-21; the builder checks each licence page again at every build and obeys
robots.txt):
  W3C (W3C Document License, kept whole and unchanged as the licence asks; sources.WHOLE_AND_UNCHANGED):
    WCAG 2.1, Techniques for WCAG 2.2, the ARIA Authoring Practices Guide, How to Meet WCAG (Quick Reference), Easy
    Checks, Accessibility Fundamentals (with How People with Disabilities Use the Web), the WAI's Web Accessibility
    Laws & Policies, ATAG 2.0, UAAG 2.0, EPUB Accessibility 1.1 and WCAG2ICT
  US government (public domain): the US Access Board's Revised 508 Standards and Guidelines, its ADA and ABA
    Accessibility Standards and its Guide to the ADA Accessibility Standards; the ICT Testing Baseline; the National
    Library Service for the Blind and Print Disabled's informational publications (reference guides)
  UK government (Open Government Licence v3.0): the GOV.UK Service Manual's accessibility pages (the GDS
    accessibility blog is a periodical: blogs.py, pub:gds_accessibility_blog)
  The A11y Project (Apache License 2.0): its posts and checklist

What was looked at and not built (AAArdvark's "WCAG in Plain English", WebAIM, Deque, Microsoft, Apple, the BBC, NFB,
ACB, BANA, DAISY, NNELS, Benetech, the Australian and Canadian government standards, MDN) is in NOT_INCLUDED with the
reason and, for copyrighted guides, the guide's index or sitemap address for the owner's Program Downloader (personal
use only).
"""

# These names are the same as in sources.py (this module is imported at its end, so it cannot import them).
US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"
GOVINFO_POLICY = "https://www.govinfo.gov/about/policies"
GOVINFO_TEXT = r"Copyright protection under this title is not available for any work of the United States Government"
OGL_UK_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
W3C_LICENCE_PAGE = "https://www.w3.org/copyright/document-license-2023/"
W3C_LICENCE_TEXT = r"Permission to copy, and distribute the contents of this document, or the W3C document from which " \
                   r"this statement is linked, in any medium for any purpose"
TR_BODY = (r"<body\b[^>]*>", r"</body>")
APACHE = "Apache License 2.0"


# ---------------------------------------------------------------------- W3C documents (NONPROFIT, keys nonprofit:)

def w3c_entries(W3C):
    """The W3C documents, as NONPROFIT entries built on sources.W3C (its group, publisher, licence, notice, licence
    check and "whole and unchanged" mark). A one-page Technical Report is read from its address (urls) with its whole
    <body>; a guide of many pages from its contents page (start), every page its address rule (pages) matches."""
    tr = dict(W3C, content=TR_BODY, limit=1, licence_page=W3C_LICENCE_PAGE, licence_text=W3C_LICENCE_TEXT)
    return [
        dict(tr, name="w3c_wcag21", title="Web Content Accessibility Guidelines (WCAG) 2.1",
             source="https://www.w3.org/TR/WCAG21/", urls=["https://www.w3.org/TR/WCAG21/"],
             pages=r"^https://www\.w3\.org/TR/WCAG21/$",
             description="The W3C Recommendation WCAG 2.1 (with its status section), whole and unchanged. Many laws "
                         "and policies (the European standard EN 301 549, the US ADA Title II rule of 2024) point to "
                         "WCAG 2.1 level AA."),
        dict(W3C, name="w3c_techniques_wcag22", title="Techniques for WCAG 2.2 (W3C WAI)",
             source="https://www.w3.org/WAI/WCAG22/Techniques/",
             description="W3C's techniques for meeting WCAG 2.2: general, HTML, ARIA, CSS, client-side script, PDF "
                         "and other techniques, and the common failures, each with its description, examples, tests "
                         "and related success criteria; every page whole and unchanged.",
             start=["https://www.w3.org/WAI/WCAG22/Techniques/"],
             pages=r"^https://www\.w3\.org/WAI/WCAG22/Techniques/[a-z-]+/[A-Z]+\d+$", limit=700),
        dict(W3C, name="w3c_aria_apg", title="ARIA Authoring Practices Guide (W3C WAI)",
             source="https://www.w3.org/WAI/ARIA/apg/",
             description="W3C's guide to building accessible widgets with WAI-ARIA: each design pattern (accordion, "
                         "combobox, dialog, menu, tabs, tree view and more) with its keyboard interaction and roles, "
                         "states and properties, and the practices (landmarks, names and descriptions, keyboard "
                         "interface, grid and table properties); every page whole and unchanged.",
             start=["https://www.w3.org/WAI/ARIA/apg/patterns/", "https://www.w3.org/WAI/ARIA/apg/practices/"],
             pages=r"^https://www\.w3\.org/WAI/ARIA/apg/(?:patterns|practices)/[a-z0-9-]+/$", limit=120),
        dict(W3C, name="w3c_wcag22_quickref", title="How to Meet WCAG 2.2 (Quick Reference, W3C WAI)",
             source="https://www.w3.org/WAI/WCAG22/quickref/", urls=["https://www.w3.org/WAI/WCAG22/quickref/"],
             pages=r"^https://www\.w3\.org/WAI/WCAG22/quickref/$", limit=1,
             page_mark=r"Copyright (?:&#xA9;|&copy;|\u00a9) \d{4}",      # its footer names "W3C" only
             description="W3C's customizable quick reference to WCAG 2.2: every guideline and success criterion "
                         "with its sufficient and advisory techniques and failures, on one page, whole and "
                         "unchanged (all filters shown)."),
        dict(W3C, name="w3c_easy_checks", title="Easy Checks: a first review of web accessibility (W3C WAI)",
             source="https://www.w3.org/WAI/test-evaluate/easy-checks/",
             urls=["https://www.w3.org/WAI/test-evaluate/easy-checks/"],
             start=["https://www.w3.org/WAI/test-evaluate/easy-checks/"],
             pages=r"^https://www\.w3\.org/WAI/test-evaluate/easy-checks/(?:[a-z-]+/)?$", limit=40,
             description="Simple checks anyone can do to get a first idea of a web page's accessibility: page title, "
                         "image text alternatives, headings, colour contrast, zoom, keyboard access, forms, multimedia "
                         "and more; every page whole and unchanged."),
        dict(W3C, name="w3c_accessibility_fundamentals", title="Accessibility Fundamentals (W3C WAI)",
             source="https://www.w3.org/WAI/fundamentals/",
             urls=["https://www.w3.org/WAI/fundamentals/", "https://www.w3.org/WAI/people-use-web/"],
             start=["https://www.w3.org/WAI/fundamentals/", "https://www.w3.org/WAI/people-use-web/"],
             pages=r"^https://www\.w3\.org/WAI/(?:fundamentals|people-use-web)/(?:[a-z-]+/){0,2}$", limit=60,
             description="W3C's introduction to web accessibility: what it is and why it matters, the accessibility "
                         "principles, how the components of web development work together, accessibility, usability "
                         "and inclusion, and how people with disabilities use the web (their stories, tools and "
                         "barriers); every page whole and unchanged."),
        dict(W3C, name="w3c_wai_policies", title="Web Accessibility Laws & Policies (W3C WAI)",
             source="https://www.w3.org/WAI/policies/", urls=["https://www.w3.org/WAI/policies/"],
             start=["https://www.w3.org/WAI/policies/"],
             pages=r"^https://www\.w3\.org/WAI/policies/(?:[a-z-]+/)?$", limit=120,
             description="W3C's list of the web accessibility laws and policies of governments around the world, "
                         "one page per country, with each policy's type, the standard it uses and its web address; "
                         "every page whole and unchanged. Each country's laws apply only there, and W3C says the "
                         "list is not legal advice."),
        dict(tr, name="w3c_atag20", title="Authoring Tool Accessibility Guidelines (ATAG) 2.0",
             source="https://www.w3.org/TR/ATAG20/", urls=["https://www.w3.org/TR/ATAG20/"],
             pages=r"^https://www\.w3\.org/TR/ATAG20/$",
             description="The W3C Recommendation ATAG 2.0: how authoring tools (editors, content management systems, "
                         "social media) should be accessible to authors with disabilities and help every author make "
                         "accessible content; whole and unchanged."),
        dict(tr, name="w3c_uaag20", title="User Agent Accessibility Guidelines (UAAG) 2.0",
             source="https://www.w3.org/TR/UAAG20/", urls=["https://www.w3.org/TR/UAAG20/"],
             pages=r"^https://www\.w3\.org/TR/UAAG20/$",
             description="The W3C Working Group Note UAAG 2.0: how browsers, media players and other user agents "
                         "should work for people with disabilities and with assistive technologies; whole and "
                         "unchanged."),
        dict(tr, name="w3c_epub_a11y_11", title="EPUB Accessibility 1.1",
             publisher="W3C Publishing Maintenance Working Group (and the International Digital Publishing Forum)",
             subject="Accessible publishing (EPUB)", source="https://www.w3.org/TR/epub-a11y-11/",
             urls=["https://www.w3.org/TR/epub-a11y-11/"], pages=r"^https://www\.w3\.org/TR/epub-a11y-11/$",
             description="The W3C Recommendation for accessible EPUB publications: discoverability metadata, the "
                         "WCAG requirements for EPUB, page navigation, media overlays and how to state conformance; "
                         "whole and unchanged."),
        dict(tr, name="w3c_wcag2ict_22", title="Guidance on Applying WCAG 2.2 to Non-Web ICT (WCAG2ICT)",
             source="https://www.w3.org/TR/wcag2ict-22/", urls=["https://www.w3.org/TR/wcag2ict-22/"],
             pages=r"^https://www\.w3\.org/TR/wcag2ict-22/$",
             description="The W3C Group Note on applying WCAG 2.2 to documents and software that are not web pages "
                         "(word-processing files, PDFs, desktop and mobile applications, kiosks); the US Revised 508 "
                         "Standards and EN 301 549 rely on this approach; whole and unchanged."),
    ]


# ---------------------------------------------------------------------- government guides (GOV_GUIDES, keys guide:)

US_GUIDE = dict(group="disability", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
                licence_page=GOVINFO_POLICY, licence_text=GOVINFO_TEXT, page_mark="", start=[], units="",
                sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"])
ACCESS_BOARD = "US Access Board (Architectural and Transportation Barriers Compliance Board)"

GOV_GUIDES = [
    dict(US_GUIDE, name="access_board_ict_508", title="Revised Section 508 Standards and Section 255 Guidelines "
         "(US Access Board)", subject="Digital accessibility (US federal ICT standards)", publisher=ACCESS_BOARD,
         source="https://www.access-board.gov/ict/", urls=["https://www.access-board.gov/ict/"],
         pages=r"^https://www\.access-board\.gov/ict/$", limit=1,
         description="The US Access Board's Information and Communication Technology (ICT) Standards and "
                     "Guidelines: the Revised Section 508 Standards for federal agencies and the Section 255 "
                     "Guidelines for telecommunications equipment, with their advisory notes; they adopt WCAG 2.0 "
                     "level AA for web content, documents and software."),
    dict(US_GUIDE, name="access_board_ada_aba_standards", title="ADA and ABA Accessibility Standards (US Access "
         "Board)", subject="Accessible buildings and facilities", publisher=ACCESS_BOARD,
         source="https://www.access-board.gov/ada/",
         urls=["https://www.access-board.gov/ada/", "https://www.access-board.gov/aba/"],
         pages=r"^https://www\.access-board\.gov/(?:ada|aba)/$", limit=2,
         description="The accessibility standards for buildings and facilities under the Americans with "
                     "Disabilities Act and the Architectural Barriers Act, as the Access Board publishes them on "
                     "the web: scoping, accessible routes, doors, ramps, elevators, toilet rooms, signs (with braille), "
                     "communication elements and recreation facilities."),
    dict(US_GUIDE, name="access_board_ada_guide", title="Guide to the ADA Accessibility Standards (US Access Board)",
         subject="Accessible buildings and facilities", publisher=ACCESS_BOARD,
         source="https://www.access-board.gov/ada/guides/", start=["https://www.access-board.gov/ada/guides/"],
         pages=r"^https://www\.access-board\.gov/ada/guides/chapter-[a-z0-9-]+/$", limit=80,
         description="The Access Board's plain-language technical guide to the ADA Accessibility Standards, chapter "
                     "by chapter: how to use the standards, new construction and alterations, floor surfaces, "
                     "reach ranges, accessible routes, entrances, doors, ramps, elevators, plumbing, communication "
                     "elements and signs, and recreation facilities."),
    dict(US_GUIDE, name="ict_testing_baseline", title="ICT Testing Baseline for Accessibility (US federal)",
         subject="Digital accessibility testing", publisher="US Access Board and the federal ICT Accessibility "
         "Testing Baseline community", source="https://ictbaseline.access-board.gov/",
         sitemap="https://ictbaseline.access-board.gov/sitemap.xml",
         pages=r"^https://ictbaseline\.access-board\.gov/[A-Za-z0-9/_-]+$", limit=120,
         unit_rules=[(r"/document-baselines/", "Document baselines"), (r"/web/|/baseline/", "Web baseline"),
                     (r".", "About the baseline")],
         description="The US federal ICT Testing Baseline: the minimum tests agencies use to check web content, "
                     "software and electronic documents against the Revised Section 508 Standards (keyboard access, "
                     "focus, names and roles, contrast, forms, tables, multimedia), with the document baselines for "
                     "Word, PowerPoint, Excel and PDF."),
    dict(US_GUIDE, name="nls_informational_publications", title="NLS reference guides on blindness, braille and "
         "disability", subject="Blindness, braille and disability (reference guides)",
         publisher="National Library Service for the Blind and Print Disabled (NLS), Library of Congress",
         source="https://www.loc.gov/nls/services-and-resources/informational-publications/",
         start=["https://www.loc.gov/nls/services-and-resources/informational-publications/"],
         pages=r"^https://www\.loc\.gov/nls/services-and-resources/informational-publications/[a-z0-9-]+/?$",
         limit=80,
         description="The NLS informational publications (the former reference circulars and reference guides): "
                     "about braille, braille literacy and resources for transcribers, braille embossers, assistive "
                     "technology and where to get it, magnifiers, audiobook players and reading apps, GPS and "
                     "wayfinding apps, audio description, deafblindness, employment, transition to independent "
                     "living, travel and recreation, emergency preparedness, disabled veterans and resources for "
                     "children and parents.",
         notice="A work of the Library of Congress (US government work, not under copyright in the United States). "
                "The organizations, products and prices named are as the NLS listed them; check with each one, as "
                "details change."),
    dict(name="govuk_service_manual_accessibility", title="GOV.UK Service Manual: accessibility and assisted digital",
         subject="Digital accessibility in government services", group="disability",
         publisher="Government Digital Service, UK Government (GOV.UK)", country="United Kingdom",
         licence="OGL-UK-3.0", licence_url=OGL_UK_URL,
         source="https://www.gov.uk/service-manual/helping-people-to-use-your-service",
         licence_page="https://www.gov.uk/help/terms-conditions", licence_text=r"Open Government Licence",
         page_mark="", units="", sitemap="", unit_rules=[],
         urls=["https://www.gov.uk/service-manual/helping-people-to-use-your-service"],
         start=["https://www.gov.uk/service-manual/helping-people-to-use-your-service"],
         pages=r"^https://www\.gov\.uk/service-manual/helping-people-to-use-your-service(?:/[a-z0-9-]+)?$",
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=40,
         description="The UK government's Service Manual on making services accessible: an introduction, "
                     "understanding WCAG 2.2, testing for accessibility (including with assistive technologies), "
                     "getting an accessibility audit, accessibility statements, and assisted digital support for "
                     "people who cannot use online services on their own.",
         notice="Contains public sector information licensed under the Open Government Licence v3.0. UK law (the "
                "Public Sector Bodies Accessibility Regulations 2018 and the Equality Act 2010) applies there; US "
                "services follow the ADA and Section 508 instead."),
    dict(name="a11y_project", title="The A11y Project: posts and checklist", subject="Digital accessibility "
         "(practical guides)", group="disability", publisher="The A11y Project (The Accessibility Project) and its "
         "contributors", country="International", licence=APACHE,
         licence_url="https://www.apache.org/licenses/LICENSE-2.0", source="https://www.a11yproject.com/",
         licence_page="https://www.a11yproject.com/", licence_text=r"The Accessibility Project\.\s*APLv2",
         page_mark=r"APLv2", units="", sitemap="", unit_rules=[],
         urls=["https://www.a11yproject.com/checklist/"], start=["https://www.a11yproject.com/posts/"],
         pages=r"^https://www\.a11yproject\.com/(?:posts/[a-z0-9-]+/|checklist/)$",
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=120,
         description="The A11y Project's community-written guides to digital accessibility (how to hide content, "
                     "write alt text, build accessible forms and buttons, test with screen readers, and myths about "
                     "accessibility) and its WCAG-based checklist.",
         notice="© The Accessibility Project, licensed under the Apache License 2.0 (APLv2, the site's footer); each "
                "post names its author."),
]

# The A11y Project's licence (a permissive licence like CC BY: copying and changes allowed with the notice kept).
ALLOWED = {"Apache License": "open", APACHE: "open"}

LICENCE_LINES = {
    "w3c_more": "www.w3.org/copyright/document-license-2023/: \"Permission to copy, and distribute the contents of "
                "this document, or the W3C document from which this statement is linked, in any medium for any "
                "purpose and without fee or royalty is hereby granted\" (with the URL, the copyright notice and the "
                "status). WCAG 2.1, ATAG 2.0, UAAG 2.0, EPUB Accessibility 1.1 and WCAG2ICT link this licence from "
                "their copyright lines (\"permissive document license\", \"document use rules\"); the WAI pages "
                "(Techniques, ARIA APG, Quick Reference, Easy Checks, Fundamentals, Policies) say \"See Permission "
                "to Use WAI Material\" (www.w3.org/WAI/about/using-wai-material/: the W3C Document License). "
                "www.w3.org/robots.txt allows /TR/ and /WAI/ (no AI rules).",
    "access_board": "The US Access Board is a federal agency: its standards and guides are works of the US "
                    "government (17 U.S.C. 105; govinfo.gov/about/policies). www.access-board.gov/robots.txt: "
                    "\"User-Agent: *\" with no Disallow; ictbaseline.access-board.gov the same (checked 2026-11-21).",
    "nls_informational_publications": "A work of the Library of Congress (17 U.S.C. 105). www.loc.gov/robots.txt "
                                      "allows /nls/ (Crawl-delay 5).",
    "govuk_service_manual_accessibility": "www.gov.uk/help/terms-conditions: \"Most content on GOV.UK is subject to "
                                          "Crown copyright protection and is published under the Open Government "
                                          "Licence (OGL)\". robots.txt disallows only print and search pages.",
    "a11y_project": "www.a11yproject.com footer: \"© 2013-2024 The Accessibility Project. APLv2\" linking "
                    "www.apache.org/licenses/LICENSE-2.0; its repository (github.com/a11yproject/a11yproject.com), "
                    "which holds the posts, is under the Apache License 2.0. robots.txt has no rules for readers.",
}

PRACTICE_SUBJECTS = [
    (r"accessib|wcag|aria\b|braille|blindness", "accessibility laws and how they are enforced (the European "
     "Accessibility Act and EN 301 549, the UK Equality Act and public sector regulations, the Accessible Canada Act "
     "and Ontario's AODA, Australia's Disability Discrimination Act, rather than the US ADA and Section 508), local "
     "services and braille codes"),
]

# Looked at on 2026-11-21 and not built. "Index:" or "Sitemap:" is the address the owner's Program Downloader can
# fetch for personal use only.
NOT_INCLUDED = [
    ("AAArdvark Accessibility, \"WCAG in Plain English\" (aaardvarkaccessibility.com)", "\"© Copyright 2026, "
     "AAArdvark. All rights reserved.\"; no open licence (its terms of service are for its testing product). Its "
     "robots.txt allows readers (no AI rules). Index: https://aaardvarkaccessibility.com/wcag-plain-english/ ; "
     "Sitemap: https://aaardvarkaccessibility.com/wcag_article-sitemap.xml"),
    ("WebAIM articles (webaim.org)", "\"©2026 WebAIM, Utah State University\", with its own copyright and terms of "
     "use; not openly licensed. Index: https://webaim.org/articles/"),
    ("Deque University free pages and Deque's blog (dequeuniversity.com, deque.com)", "Copyright of Deque Systems; "
     "not openly licensed. Index: https://dequeuniversity.com/resources/"),
    ("Microsoft accessibility documentation (learn.microsoft.com)", "Microsoft's documentation is under its own "
     "terms of use (some repositories are CC BY 4.0, chosen one by one); not built. Index: "
     "https://learn.microsoft.com/en-us/accessibility/"),
    ("Apple accessibility documentation (developer.apple.com, support.apple.com)", "Copyright of Apple; not openly "
     "licensed. Index: https://developer.apple.com/accessibility/"),
    ("BBC GEL accessibility guidance and Mobile Accessibility Guidelines (bbc.co.uk/gel)", "Copyright of the BBC, "
     "and www.bbc.co.uk/robots.txt shuts out ClaudeBot, GPTBot, CCBot and other AI crawlers by name, so it is not "
     "read. Index: https://www.bbc.co.uk/gel/guidelines/category/accessibility"),
    ("National Federation of the Blind free guides (nfb.org)", "Copyright of the NFB; not openly licensed. Index: "
     "https://nfb.org/resources"),
    ("American Council of the Blind guides (acb.org)", "\"© 1961-2026 American Council of the Blind\"; not openly "
     "licensed. Index: https://www.acb.org/"),
    ("Braille Authority of North America rules and guidelines (brailleauthority.org)", "Copyright of BANA (free PDF "
     "downloads, but no licence to repackage them). Index: https://www.brailleauthority.org/"),
    ("DAISY Consortium Accessible Publishing Knowledge Base (kb.daisy.org)", "\"© 2026 The DAISY Consortium\"; its "
     "terms of use page did not state an open licence. Index: https://kb.daisy.org/publishing/docs/"),
    ("NNELS guides (nnels.ca) and Benetech's DIAGRAM Center (diagramcenter.org)", "Their sites did not answer this "
     "machine (connection refused), so their licences and robots.txt could not be checked. Index: "
     "https://nnels.ca/ and http://diagramcenter.org/"),
    ("Australian Government Digital Transformation Agency accessibility guidance (digital.gov.au)", "The site did "
     "not answer this machine, so its licence (Australian government sites are often CC BY 4.0) could not be "
     "checked; check by hand before adding. Index: https://www.digital.gov.au/policy/digital-experience/toolkit"),
    ("Accessibility Standards Canada (accessible.canada.ca) and canada.ca accessibility guidance", "Under the "
     "canada.ca terms (www.canada.ca/en/transparency/terms.html: non-commercial reproduction only), which the "
     "library does not build from web pages (publications deposited on open.canada.ca under the Open Government "
     "Licence - Canada are different and are built as pub:canada_ogl). Index: https://accessible.canada.ca/"),
    ("MDN Web Docs accessibility pages (developer.mozilla.org)", "CC BY-SA 2.5, but the whole of MDN is already in "
     "the Kiwix library (developer.mozilla.org_en_all), its accessibility pages included."),
    ("Understanding WCAG 2.1 and WCAG 2.0", "Superseded by Understanding WCAG 2.2, which is in the library "
     "(w3c_understanding_wcag22) and covers every 2.1 and 2.0 success criterion."),
]
