"""Mental health and wellbeing for the reference library, in its own group "Reference, mental health and wellbeing"
(the owner's request of 2026-11-22). Keys: mental-health (every book), mind:<name>.
This module also holds the small helpers the other three new health modules use (fitness_nutrition.py,
sexual_health.py, aging_end_of_life.py): cdc_book, pages_book, help_lines_book and the notes.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - NIMH's health topics (depression, anxiety, panic, PTSD, bipolar disorder, OCD, ADHD, eating disorders,
    schizophrenia, suicide prevention, caring for your mental health, coping with traumatic events, psychotherapies
    such as CBT and DBT, mental health medications, brain stimulation therapies ...). NIMH's brochures are already
    fam:nimh_publications: not repeated;
  - CDC's mental health and suicide prevention pages (coping with stress, caring for your mental health, the help
    lines, warning signs and how to help), kept whole with their text unchanged as CDC's terms ask;
  - the VA National Center for PTSD (understanding PTSD, its treatments: talk therapy such as CPT, PE and EMDR, and
    medicines; getting help, self-help and coping, families);
  - the Office on Women's Health's mental health pages (stress, depression, anxiety, eating disorders ...);
  - CDC's alcohol and tobacco pages (drinking less, alcohol's effects, quitting smoking and vaping, the quitline
    1-800-QUIT-NOW), kept whole;
  - Smokefree.gov (NCI): quit plans, cravings and triggers, withdrawal, stress and mood, quitting vaping, helping
    someone quit;
  - NIDA's drug topics (each drug: what it is, its effects and risks; treatment and recovery, harm reduction,
    naloxone and overdose). NIDA's pages for parents and teens are already parent:nida_parents_teens;
  - NCI's pages for caregivers of people with advanced cancer, with grief, bereavement and loss;
  - "Help lines": a page written for this library with the help numbers (Crisis Text Line, the Veterans Crisis
    Line, the Disaster Distress Helpline, SAMHSA's National Helpline, the quitline, the problem gambling helpline),
    each checked on an official page at every build: a number whose words are gone is not stated.
  (The 988 crisis numbers are fam:crisis_lines; MedlinePlus's summaries are mlp:health_topics; the medicines'
  own labels are the med: books: not repeated.)

Every book's notice ends with the health note: general information, not medical advice or a diagnosis; in an
emergency call 911; in a mental health crisis call or text 988.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): SAMHSA (refuses programs), NIAAA and
Rethinking Drinking (its agency's robots.txt says ai-train=no), the Surgeon General's advisory on loneliness
(hhs.gov refuses programs), the National Institute on Aging (bot check), HIV.gov (its robots.txt shuts out every
reader), and the copyright guides (Mental Health America, NAMI, the American Psychological Association, Mayo
Clinic, the National Council on Problem Gambling's pages).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's terms, NCI's reuse policy and the Office on Women's Health's disclaimer are checked at every build and
their conditions met in each notice. The help lines page's own words are CC0.

Run from the repository's folder:
  python3 textbooks/mental_health.py mind:help_lines --out build/textbooks
  python3 textbooks/mental_health.py --list mental-health
"""

import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "mentalhealth"
GROUPS = {GROUP: "Reference, mental health and wellbeing"}

# The health note every health book of the four new modules ends with (the owner's words), and its adaptations.
HEALTH_NOTE = ("General information, not medical advice or a diagnosis. In an emergency call 911; in a mental health "
               "crisis call or text 988.")

# CDC's terms (as in parenting.py and outdoor_cooking.py): checked at every build, kept whole, credit and the
# no-endorsement notice.
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
CDC_PUBLISHER = "Centers for Disease Control and Prevention (CDC)"
CDC = "https://www.cdc.gov"

# NCI's reuse policy (cancer.gov and smokefree.gov, both NCI sites): text free of copyright, credit NCI.
NCI_TERMS = "https://www.cancer.gov/policies/copyright-reuse"
NCI_TEXT = r"all text within National Cancer Institute \(NCI\) products is free of copyright"
NCI_CREDIT = ("Source: the National Cancer Institute (NCI), whose text \"is free of copyright and may be reused\"; "
              "this copy does not imply NCI's endorsement.")

# The content marks of the VA's older page template (ptsd.va.gov, va.gov/geriatrics, cem.va.gov): the article
# starts at its inner content box and ends before the footer; pages on the new template have a <main>.
VA_CONTENT = (r'<div id="innerContentWrapper"[^>]*>|<main\b[^>]*>',
              r'<div id="footer2022"|<div id="footer-effect"|</main>')

# The Office on Women's Health's disclaimer (as in early_childhood.py).
OWH_TERMS = "https://www.womenshealth.gov/about-us/disclaimers"
OWH_TEXT = r"All material contained on these pages are free of copyright restrictions"
OWH_CREDIT = ("From the Office on Women's Health (womenshealth.gov): \"All material contained on these pages are free "
              "of copyright restrictions\". The OWH Helpline: 1-800-994-9662.")


def cdc_book(group, name, title, subject, sites, description, units, note, urls=(), limit=300):
    """A CDC web guide made of whole CDC sites (the folder names, such as "mental-health"), each read from its own
    site index ("site.html", which lists every page of the site), kept whole under CDC's terms with CDC's notice and
    the given note. Spanish copies, media files and the pages for professionals (hcp/, php/) are left out."""
    alt = "|".join(sites)
    pages = rf"^https://www\.cdc\.gov/({alt})/(?!es/|media/|site\.html|php/|hcp/)[a-z0-9-]+(/[a-z0-9-]+)*\.html$"
    entry = K.guide(group, name, title, subject, CDC_PUBLISHER, [f"{CDC}/{s}/site.html" for s in sites], pages,
                    description, f"{CDC_NOTICE} {note}", depth=1, units=units, limit=limit)
    entry["urls"] = list(urls)
    return dict(entry, licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True)


def pages_book(group, name, title, subject, publisher, urls, pages, description, notice, units=(), **more):
    """A web guide of a fixed list of pages (nothing found beyond them), read in the order listed; the first address
    is its source."""
    return K.us_web(group, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=notice, crawl=[(urls[0], 0)], urls=list(urls), pages=pages,
                    unit_rules=list(units), limit=len(urls) + 5, **more)


def owh_book(group, name, title, subject, sections, description, note, limit=200):
    """An Office on Women's Health guide made of whole sections of womenshealth.gov (such as "menopause"), every page
    under them, with OWH's licence line checked at every build."""
    alt = "|".join(sections)
    entry = K.guide(group, name, title, subject, "Office on Women's Health (OWH), US Department of Health and Human "
                    "Services", [f"https://www.womenshealth.gov/{s}" for s in sections],
                    rf"^https://www\.womenshealth\.gov/({alt})(/[a-z0-9-]+)*$", description, f"{OWH_CREDIT} {note}",
                    depth=2, follow=rf"^https://www\.womenshealth\.gov/({alt})(/[a-z0-9-]+)?$", limit=limit)
    return dict(entry, licence_page=OWH_TERMS, licence_text=OWH_TEXT)


# ====================================================================== help lines (checked at every build)

def text_of(html_text):
    """The words of an HTML page (scripts and styles left out), on one line."""
    import html
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ",
                                                                   html_text or ""))).split())


def help_lines_book(prefix, group, name, title, subject, checks, intro, description, note, fetch=None, cache=None):
    """A short page written for this library listing help lines, each checked on its official page now: checks is
    [(heading, official page, regular expression that must still be on it, the words to say)]. A line whose page does
    not answer, or no longer says its words, is left out and the page says which source to check instead. fetch:
    a function(url) -> HTML (the builder's fetch by default; the self-test passes a made-up one)."""
    import build_textbooks as B
    get = fetch or (lambda url: B.fetch(url, None) if K.readable(url, cache) else "")
    pages, said, missing, checked = {}, [], [], []
    for heading, url, must, words in checks:
        if url not in pages:
            try:
                pages[url] = text_of(get(url))
            except Exception:  # noqa: BLE001 - a site not answering: its numbers are not stated
                pages[url] = ""
        ok = bool(re.search(must, pages[url], re.I))
        checked.append((heading, url, ok))
        (said if ok else missing).append((heading, words, url))
    body = [f"<p><strong>{B.esc(intro)}</strong></p>"]
    for heading in dict.fromkeys(h for h, _u, _m, _w in checks):
        mine = [x for x in said if x[0] == heading]
        body.append(f"<h2>{B.esc(heading)}</h2>")
        if mine:
            body.append("<ul>" + "".join(f"<li>{B.esc(w)} (Checked on {B.esc(u)}.)</li>" for _h, w, u in mine)
                        + "</ul>")
        for _h, _w, url in [x for x in missing if x[0] == heading]:
            body.append(f"<p>This number could not be checked when this book was made: look it up on {B.esc(url)}."
                        "</p>")
    body.append(f"<p>{B.esc(note)}</p>")
    today = datetime.date.today().isoformat()
    # The originals are only the US government pages checked (public domain): the other sites' pages are their
    # makers' copyright, so they are named in the text but never offered as files to copy.
    gov = [u for u in dict.fromkeys(u for _h, u, _ok in checked) if re.search(r"\.gov(/|$)", u)]
    book = K.new_book(f"{prefix}_{name}", title, subject, group, "GetBraille.com (written for this library)", "CC0",
                      K.CC0_URL, gov[0] if gov else "", description,
                      "Written for this library; its own words are CC0. Every "
                      "number was checked on the official page named beside it on the day shown. " + note,
                      changes="written for this library", published=today)
    book.version = f"checked {today}: {sum(1 for c in checked if c[2])} of {len(checked)} lines confirmed"
    book.originals = [{"url": u, "kind": "html"} for u in gov]
    book.pages.append(B.Page(name.replace("_", "-"), title, "\n".join(body), 0, ""))
    return book


CDC_HELP = CDC + "/mental-health/caring/index.html"
HELP_CHECKS = [
    ("Crisis and suicide", "https://www.crisistextline.org/", r"Text HOME to 741741",
     "Crisis Text Line: text HOME to 741741 to reach a trained volunteer crisis counsellor, any time."),
    ("Crisis and suicide", CDC_HELP, r"Call 988 and press 1.{0,40}838255",
     "Veterans Crisis Line (veterans, service members and their families): call 988 and press 1, or text 838255."),
    ("Crisis and suicide", CDC_HELP, r"Disaster Distress Helpline.{0,200}1-800-985-5990",
     "Disaster Distress Helpline (SAMHSA), for distress after a natural or human-caused disaster: call or text "
     "1-800-985-5990, 24 hours a day."),
    ("Drugs, alcohol, tobacco and gambling", CDC_HELP, r"1-800-662-HELP \(4357\)",
     "SAMHSA's National Helpline, for treatment and support for mental health and substance use: call "
     "1-800-662-HELP (1-800-662-4357), free and confidential; or visit findtreatment.gov."),
    ("Drugs, alcohol, tobacco and gambling", CDC + "/tobacco/about/how-to-quit.html", r"1-800-QUIT-NOW",
     "Quitline, free coaching to quit smoking: call 1-800-QUIT-NOW (1-800-784-8669); or visit smokefree.gov."),
    ("Drugs, alcohol, tobacco and gambling", "https://www.ncpgambling.org/help-treatment/", r"1-800-MY-RESET",
     "National Problem Gambling Helpline: call or text 1-800-MY-RESET (1-800-697-3738)."),
]


def help_book(name, work, cache=None, left_out=None, limit=None):
    """The mental health help lines page, its numbers checked on the official pages now."""
    return help_lines_book("mind", GROUP, name, "Help lines: crisis, disaster distress, addiction, quitting and "
                           "gambling (US)", "Mental health help lines", HELP_CHECKS,
                           "If you or someone else is in danger right now, call 911. In a mental health crisis, call "
                           "or text 988 (the 988 Suicide & Crisis Lifeline; the crisis lines book has more ways to "
                           "reach it).", "The US help lines for a crisis, disaster distress, drugs and alcohol, "
                           "quitting tobacco and problem gambling, each checked on an official page when the book was "
                           "made.", HEALTH_NOTE, cache=cache)


# ====================================================================== the books

NIMH = "https://www.nimh.nih.gov/health/topics"
GUIDES = [
    K.guide(GROUP, "nimh_health_topics", "Mental health topics: conditions, treatments and help (NIMH)",
            "Mental health conditions and treatments", "National Institute of Mental Health (NIMH), National "
            "Institutes of Health", NIMH,
            r"^https://www\.nimh\.nih\.gov/health/topics/(?!espanol)[a-z0-9-]+(/[a-z0-9-]+)?$",
            "Every NIMH health topic page: anxiety disorders (generalised anxiety, panic, social anxiety, phobias), "
            "depression, bipolar disorder, obsessive-compulsive disorder, post-traumatic stress disorder, ADHD, "
            "autism, borderline personality disorder, eating disorders, schizophrenia, disruptive mood "
            "dysregulation disorder, suicide prevention; caring for your mental health, coping with traumatic "
            "events, substance use and mental health; the treatments: psychotherapies (cognitive behavioural "
            "therapy, dialectical behaviour therapy and others), mental health medications (antidepressants, "
            "anti-anxiety medicines, stimulants, antipsychotics, mood stabilisers: what they are and how to talk "
            "with your doctor; the medicines' own labels are the medicines books), brain stimulation therapies; and "
            "mental health for children, teens, men, women and older adults.",
            f"A work of the National Institute of Mental Health (public domain). {HEALTH_NOTE}", depth=2,
            follow=r"^https://www\.nimh\.nih\.gov/health/topics/(?!espanol)[a-z0-9-]+$",
            units=[(r"psychotherap|medications|brain-stimulation|technology", "Treatments"),
                   (r"caring|coping|substance|child|men-and|women-and|older", "Wellbeing and coping"),
                   (r".", "Conditions")], limit=150),
    cdc_book(GROUP, "cdc_mental_health_suicide", "Mental health, stress and suicide prevention (CDC)",
             "Coping and suicide prevention", ["mental-health", "suicide"],
             "CDC's mental health and suicide prevention pages, every page: caring for your mental health and coping "
             "with stress, how to get help and the help lines (988, the Veterans Crisis Line, the Disaster Distress "
             "Helpline, SAMHSA's National Helpline, the domestic violence and sexual assault hotlines, the Eldercare "
             "Locator), mental health conditions and their treatment, the warning signs of suicide, how to help "
             "someone in crisis and how to prevent suicide.",
             units=[(r"/suicide/", "Suicide prevention"), (r".", "Mental health and coping")], note=HEALTH_NOTE),
    K.guide(GROUP, "va_ptsd", "PTSD: understanding it, its treatments and getting help (VA National Center for PTSD)",
            "PTSD and trauma", "National Center for PTSD, US Department of Veterans Affairs",
            "https://www.ptsd.va.gov/understand/index.asp",
            r"^https://www\.ptsd\.va\.gov/PTSD/(understand|understand_tx|gethelp|family)/([a-z_]+/)?[a-z_]+\.asp$",
            "The National Center for PTSD's pages for the public: what PTSD is, its kinds (after combat, violence and "
            "abuse, disasters), common reactions after trauma, how it is measured, PTSD in adults, veterans, "
            "children and teens, related problems (substance use, anger, chronic pain, depression, grief, moral "
            "injury, sleep problems, suicide, traumatic brain injury), the treatments (talk therapies such as "
            "cognitive processing therapy, prolonged exposure and EMDR, and medicines), choosing a treatment, "
            "finding a therapist, crisis help, self-help and coping, and help for families.",
            f"A work of the US Department of Veterans Affairs (public domain). {HEALTH_NOTE} Veterans: dial 988 then "
            f"press 1.", depth=1,
            units=[(r"/understand_tx/", "Treatment"), (r"/gethelp/", "Getting help"), (r"/family/", "Families"),
                   (r".", "Understanding PTSD")], limit=80, content=VA_CONTENT),
    owh_book(GROUP, "owh_mental_health", "Mental health, stress and wellbeing (Office on Women's Health)",
             "Mental health and wellbeing", ["mental-health"],
             "The Office on Women's Health's mental health pages, every page: good mental health and stress, "
             "mental health conditions (depression, anxiety, eating disorders, postpartum depression, PTSD, "
             "bipolar disorder, borderline personality disorder, schizophrenia), getting help and paying for it, "
             "and taking care of yourself.", HEALTH_NOTE),
    cdc_book(GROUP, "cdc_alcohol_tobacco", "Alcohol and tobacco: drinking less, quitting smoking and vaping (CDC)",
             "Alcohol and tobacco", ["alcohol", "tobacco"],
             "CDC's alcohol and tobacco pages, every page: alcohol use and your health, drinking less, binge "
             "drinking, alcohol and pregnancy, alcohol and other drugs; smoking and tobacco use, the health effects, "
             "e-cigarettes and vaping, how to quit (the quitline 1-800-QUIT-NOW, medicines to quit, coping with "
             "cravings), the benefits of quitting and secondhand smoke.",
             units=[(r"/alcohol/", "Alcohol"), (r".", "Tobacco and quitting")], note=HEALTH_NOTE, limit=400),
    dict(K.guide(GROUP, "smokefree_gov", "Quitting smoking and vaping (Smokefree.gov, National Cancer Institute)",
                 "Quitting smoking", "Smokefree.gov (National Cancer Institute)", "https://smokefree.gov/",
                 r"^https://smokefree\.gov/(quit-smoking|challenges-when-quitting|tools-tips|quit-vaping-resources|"
                 r"help-others-quit|build-your-quit-plan)(/[a-z0-9-]+)*$",
                 "Every page of Smokefree.gov's guides: why to quit and getting started, building a quit plan, the "
                 "day you quit, quit methods and nicotine replacement therapy, cravings and triggers, withdrawal, "
                 "stress, mood and weight gain when quitting, staying smokefree, quitting vaping, text programmes "
                 "and extra help, and helping someone else quit.",
                 f"{NCI_CREDIT} {HEALTH_NOTE} Free help to quit: 1-800-QUIT-NOW.", depth=2,
                 follow=r"^https://smokefree\.gov/(quit-smoking|challenges-when-quitting|tools-tips|"
                        r"quit-vaping-resources|help-others-quit)$",
                 units=[(r"vaping", "Quitting vaping"), (r"challenges", "Challenges when quitting"),
                        (r"help-others", "Helping others quit"), (r".", "Quitting smoking")], limit=120,
                 content=(r'id="main-content"[^>]*>', r'<footer\b')),
         licence_page=NCI_TERMS, licence_text=NCI_TEXT),
    K.guide(GROUP, "nida_drug_topics", "Drugs, addiction, treatment and recovery (NIDA)", "Drugs and addiction",
            "National Institute on Drug Abuse (NIDA), National Institutes of Health",
            "https://nida.nih.gov/research-topics",
            r"^https://nida\.nih\.gov/research-topics/(?!parents-educators|publications|trends-statistics|"
            r"drugs-a-to-z)[a-z0-9-]+$",
            "NIDA's topic page for each drug and subject, every page: alcohol, cannabis, cocaine, fentanyl, heroin, "
            "inhalants, ketamine, kratom, MDMA, methamphetamine, opioids, prescription and over-the-counter "
            "medicines, psychedelics, steroids, synthetic cannabinoids and cathinones, tobacco, nicotine and "
            "vaping, xylazine; addiction science and drugs and the brain; treatment and recovery, harm reduction, "
            "drug checking and testing, co-occurring disorders, prevention and stigma.",
            f"A work of the National Institute on Drug Abuse (public domain). {HEALTH_NOTE} Poison Help: "
            f"1-800-222-1222.", depth=1, units=[(r"treatment|harm-reduction|drug-checking|stigma|prevention|"
                                                 r"co-occurring", "Treatment, recovery and prevention"),
                                                (r".", "Drugs and addiction")], limit=80),
    dict(K.guide(GROUP, "nci_grief_caregivers", "Grief, bereavement and caring for someone with advanced cancer (NCI)",
                 "Grief and bereavement", "National Cancer Institute (NCI), National Institutes of Health",
                 "https://www.cancer.gov/about-cancer/advanced-cancer/caregivers",
                 r"^https://www\.cancer\.gov/about-cancer/advanced-cancer/caregivers(/[a-z0-9-]+){0,2}$",
                 "NCI's pages for family caregivers of someone with advanced cancer: caring for yourself while "
                 "caring for someone, talking with the person and the family, planning for the last days and weeks, "
                 "and grief, bereavement and loss (what grief is, how it changes over time, complicated grief, "
                 "children and grief, and where to find support).",
                 f"{NCI_CREDIT} {HEALTH_NOTE} NCI's Contact Center: 1-800-4-CANCER (1-800-422-6237).", depth=2,
                 follow=r"^https://www\.cancer\.gov/about-cancer/advanced-cancer/caregivers(/[a-z0-9-]+)?$",
                 units=[(r"bereavement|grief", "Grief and bereavement"), (r".", "Caring for someone")], limit=40),
         licence_page=NCI_TERMS, licence_text=NCI_TEXT),
]

COLLECTION = K.Collection("mind", GROUP, guides=GUIDES,
                          makers={"help_lines": (help_book, lambda name: datetime.date.today().strftime("%Y-%m"))},
                          words={"mental-health": lambda: [f"mind:{g['name']}" for g in GUIDES] + ["mind:help_lines"]})

LICENCE_LINES = {
    "mind_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public domain "
                "on four conditions (credit CDC, no endorsement, no change to the substance, free on CDC's site), met "
                "in each CDC book's notice; the pages are kept whole. robots.txt allows the pages; no AI rules "
                "(checked 2026-11-22).",
    "mind_nimh_nida_va": "www.nimh.nih.gov, nida.nih.gov and www.ptsd.va.gov: works of the US government (17 U.S.C. "
                         "105, checked on govinfo.gov's policies page at every build); robots.txt allows the pages; "
                         "no AI rules (checked 2026-11-22).",
    "mind_nci": "www.cancer.gov/policies/copyright-reuse (checked at every build): \"all text within National Cancer "
                "Institute (NCI) products is free of copyright and may be reused\", credit NCI (in the notice); "
                "smokefree.gov is an NCI site. Pictures are left out (NCI's graphics are a mix of copyrighted and "
                "free ones).",
    "mind_owh": "www.womenshealth.gov/about-us/disclaimers (checked at every build): \"All material contained on "
                "these pages are free of copyright restrictions\".",
    "mind_help_lines": "Help lines: written for this library (CC0); every number is checked at each build on the "
                       "official page named beside it (cdc.gov, crisistextline.org, ncpgambling.org: robots.txt "
                       "allows them; no AI rules). Only the facts (the numbers and how to reach them) are stated.",
}
NOT_INCLUDED = [
    ("SAMHSA publications, the SAMHSA Library and FindTreatment.gov's guides", "Public domain, but www.samhsa.gov "
     "and library.samhsa.gov refuse programs (\"Access Denied\", robots.txt included; checked again 2026-11-22). "
     "SAMHSA's help line numbers are stated in mind:help_lines from CDC's page. Link-only. Index: "
     "https://library.samhsa.gov/ and https://findtreatment.gov/"),
    ("NIAAA's Rethinking Drinking and the NIAAA Alcohol Treatment Navigator", "Public domain, but NIAAA's main site's "
     "robots.txt says \"Content-Signal: search=yes,ai-train=no,use=reference\" and shuts out AI companies' readers by "
     "name; its Rethinking Drinking site has no such line, but it is the same agency's wish, so neither is read nor "
     "copied from the Internet Archive (item rethinking-drinking_202203). CDC's alcohol pages are built instead "
     "(mind:cdc_alcohol_tobacco). Link-only. Index: https://rethinkingdrinking.niaaa.nih.gov/ and "
     "https://alcoholtreatment.niaaa.nih.gov/"),
    ("Our Epidemic of Loneliness and Isolation: the US Surgeon General's Advisory on the Healing Effects of Social "
     "Connection and Community (2023)", "Public domain, but www.hhs.gov refuses programs (\"Access Denied\", its "
     "robots.txt included, checked 2026-11-22), and no Internet Archive copy of the PDF was found. Link-only. Index: "
     "https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf"),
    ("National Institute on Aging: grief, mourning, depression and loneliness in older adults", "Public domain, but "
     "www.nia.nih.gov answers programs with a bot check (\"405\"; checked again 2026-11-22). Link-only. Index: "
     "https://www.nia.nih.gov/health/grief-and-mourning"),
    ("HIV.gov (mental health and HIV)", "Its robots.txt line \"Disallow: *#query=*\" reads, by the robots.txt "
     "standard (a \"#\" begins a comment), as \"Disallow: *\": every page is refused, so it is not read. CDC's HIV "
     "pages are in the sexual health books (sexhealth:cdc_sti_hiv). Link-only. Index: https://www.hiv.gov/"),
    ("Mental Health America, NAMI, the American Psychological Association, the American Psychiatric Association, "
     "Mayo Clinic and Psychology Today guides and directories", "Copyright, not openly licensed (checked "
     "2026-11-22). Link-only. Index: https://mhanational.org/ , https://www.nami.org/ and https://www.apa.org/"),
    ("The National Council on Problem Gambling's pages and Gamblers Anonymous literature", "\"(c) Copyright NCPG "
     "2026. All Rights Reserved\"; only the helpline number is stated (checked on its page at every build). No US "
     "government guide on problem gambling was found. Link-only. Index: https://www.ncpgambling.org/help-treatment/"),
    ("Mindfulness and relaxation guides (NCCIH, the VA Whole Health library)", "NCCIH (www.nccih.nih.gov) and the VA "
     "Whole Health pages were not built in this pass: NIMH's \"caring for your mental health\", CDC's coping pages and "
     "the PTSD self-help pages cover coping and relaxation. A candidate for a later pass. Index: "
     "https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety and "
     "https://www.va.gov/WHOLEHEALTHLIBRARY/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
