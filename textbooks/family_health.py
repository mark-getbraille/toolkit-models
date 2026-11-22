"""Parenting and child safety, aging and caregiving, and mental health for the reference library (the owner's
requests of 2026-11-22). Keys: family-health (every book), fam:<name>.

What this module builds, in plain words, each IN FULL:
  - CDC's "Learn the Signs. Act Early." (developmental milestones from 2 months to 5 years, what to do if you are
    concerned, early intervention contacts by state, the milestone checklists), kept whole with its text unchanged
    as CDC's terms ask;
  - NICHD's Safe to Sleep campaign (reducing the risk of SIDS and other sleep-related infant deaths: back sleeping,
    a safe sleep area, breastfeeding, tummy time, the questions people ask);
  - the Administration for Community Living's programme pages for older adults, people with disabilities and
    family caregivers (caregiver support, nutrition, elder rights and elder abuse, the long-term care ombudsman,
    the aging and disability networks);
  - NIMH's mental health publications for the public: every brochure and fact sheet (anxiety, depression, bipolar
    disorder, ADHD, autism, eating disorders, PTSD, schizophrenia, suicide prevention and the rest);
  - "Crisis lines": a short page written for this library with the US and Canadian suicide and crisis numbers,
    checked on the official sites at every build (988lifeline.org, 988.ca): if the words checked are gone, the
    page says so and gives only the sites to check.

Not built (NOT_INCLUDED): NHTSA's car seat guides (nhtsa.gov refuses programs), the National Institute on Aging's
guides (nia.nih.gov answers programs with a bot check, "405"), the Eldercare Locator (a JavaScript application),
SAMHSA's publications (samhsa.gov and its library refuse programs).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's "Use of Agency Materials" page is checked for its public-domain line and its conditions (credit, no
endorsement, no change to the substance, free on CDC's site) are met in the notice. The crisis page's own words are
CC0.

Run from the repository's folder:
  python3 textbooks/family_health.py fam:crisis_lines --out build/textbooks
"""

import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
NOT_MEDICAL = "Health information, not medical advice: talk with your doctor or other health care provider."

GUIDES = [
    dict(K.guide(GROUP, "cdc_act_early", "Learn the Signs. Act Early.: developmental milestones (CDC)",
                 "Child development and milestones", "Centers for Disease Control and Prevention (CDC)",
                 "https://www.cdc.gov/act-early/index.html",
                 r"^https://www\.cdc\.gov/act-early/(?!media/)[a-z0-9-]+(/[a-z0-9-]+)*\.html$",
                 "CDC's whole \"Learn the Signs. Act Early.\" programme for families: the milestones children reach "
                 "at 2, 4, 6 and 9 months, 1 year, 15 and 18 months, 2 years, 30 months, 3, 4 and 5 years (social and "
                 "emotional, language, thinking and movement), what to do if you are concerned, developmental "
                 "monitoring and screening, early intervention and how to reach it in every state, the milestone "
                 "checklists and tips for parents and educators.", CDC_NOTICE, depth=2,
                 follow=r"^https://www\.cdc\.gov/act-early/[a-z0-9-]+/index\.html$",
                 units=[(r"/milestones/", "Milestones by age"), (r"/early-intervention/", "Early intervention"),
                        (r"/families/", "For families"), (r".", "Learn the Signs. Act Early.")], limit=120),
         licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True),
    K.guide(GROUP, "safe_to_sleep", "Safe to Sleep: reducing the risk of SIDS (NICHD)", "Infant safe sleep",
            "Eunice Kennedy Shriver National Institute of Child Health and Human Development (NICHD)",
            "https://safetosleep.nichd.nih.gov/",
            r"^https://safetosleep\.nichd\.nih\.gov/(about|reduce-risk|safe-sleep|resources/infant-loss)(/[A-Za-z-]+)*$",
            "Every page of the Safe to Sleep campaign: what SIDS and other sleep-related infant deaths are, their "
            "causes and risk factors, ways to reduce the risk (babies sleep on their backs, in a safe sleep area with "
            "nothing else in it, sharing a room but not a bed), breastfeeding, tummy time, the questions parents "
            "ask, and support after the loss of a baby.",
            "A work of the National Institutes of Health (public domain). " + NOT_MEDICAL, depth=2,
            follow=r"^https://safetosleep\.nichd\.nih\.gov/(about|reduce-risk|safe-sleep)$", limit=40),
    K.guide(GROUP, "acl_aging_caregiving", "Aging, disability and caregiving programmes (Administration for "
            "Community Living)", "Aging and caregiving", "Administration for Community Living (ACL), US Department "
            "of Health and Human Services", "https://acl.gov/programs",
            r"^https://acl\.gov/(programs(/[a-z0-9-]+){1,2}|about-acl/[a-z0-9-]+)$",
            "The Administration for Community Living's programme pages: support for family caregivers, health and "
            "wellness, nutrition (meals), elder justice and elder abuse, the long-term care ombudsman, legal "
            "assistance, aging and disability resource centres, assistive technology (the AT Act programs), "
            "employment, housing and independent living, and the aging and disability networks.",
            "A work of the US Department of Health and Human Services (public domain). To find local services, call "
            "the Eldercare Locator, 1-800-677-1116.", depth=2,
            follow=r"^https://acl\.gov/programs/[a-z0-9-]+$", limit=150),
    K.guide(GROUP, "nimh_publications", "Mental health brochures and fact sheets (National Institute of Mental "
            "Health)", "Mental health", "National Institute of Mental Health (NIMH)",
            "https://www.nimh.nih.gov/health/publications",
            r"^https://www\.nimh\.nih\.gov/health/publications/(?![a-z0-9-]*-listing$)(?!brochures-and-fact-sheets|espanol)"
            r"[a-z0-9-]+$",
            "Every NIMH brochure and fact sheet for the public: anxiety disorders, depression (in women, men, teens "
            "and older adults), bipolar disorder, ADHD, autism, borderline personality disorder, eating disorders, "
            "obsessive-compulsive disorder, panic disorder, PTSD, schizophrenia, seasonal affective disorder, "
            "suicide prevention, caring for your mental health, finding help and taking part in research.",
            "A work of the National Institute of Mental Health (public domain). " + NOT_MEDICAL + " If you are in "
            "crisis, call or text 988 (US) or 9-8-8 (Canada).", depth=2,
            follow=r"^https://www\.nimh\.nih\.gov/health/publications/[a-z0-9-]+-listing$", limit=200),
]


# ====================================================================== crisis lines (checked at every build)

# (country, official page, what must still be on it, what the page says when it is)
CHECKS = [
    ("United States", "https://988lifeline.org/help-yourself/for-deaf-hard-of-hearing/",
     r"dial 711 then 988", "988 Suicide & Crisis Lifeline: call or text 988, or chat at 988lifeline.org, 24 hours a "
     "day. TTY users: use your relay service, or dial 711 then 988. Deaf and hard of hearing people who use American "
     "Sign Language can use the 988 videophone."),
    ("United States", "https://988lifeline.org/help-yourself/for-deaf-hard-of-hearing/", r"838255",
     "Veterans Crisis Line: dial 988 then press 1, or text 838255."),
    ("Canada", "https://988.ca/", r"Call 9-8-8 Text 9-8-8|call or text 9-8-8", "9-8-8 Suicide Crisis Helpline: call "
     "or text 9-8-8, 24 hours a day, every day of the year, in English and French. Talk Suicide Canada's old number "
     "and site (talksuicide.ca) now lead to 9-8-8."),
]


def crisis_book(name, work, cache=None, left_out=None, limit=None):
    """The crisis lines page, its numbers checked on the official sites now."""
    import build_textbooks as B
    lines, checked = [], []
    pages = {}
    for country, url, must, words in CHECKS:
        if url not in pages:
            try:
                text = B.fetch(url, None) if K.readable(url, cache) else ""
            except Exception:  # noqa: BLE001 - a site not answering: its numbers are not stated
                text = ""
            pages[url] = " ".join(B.html.unescape(re.sub(r"<[^>]+>", " ", re.sub(
                r"(?s)<(script|style)[^>]*>.*?</\1>", " ", text))).split())
        ok = bool(re.search(must, pages[url], re.I))
        checked.append((country, url, ok))
        if ok:
            lines.append((country, words, url))
    body = ["<p><strong>If you or someone else is in danger right now, call 911 (in the US and Canada).</strong></p>"]
    for country in ("United States", "Canada"):
        mine = [x for x in lines if x[0] == country]
        body.append(f"<h2>{country}</h2>")
        if mine:
            body.append("<ul>" + "".join(f"<li>{B.esc(w)} (Checked on {B.esc(u)}.)</li>" for _c, w, u in mine)
                        + "</ul>")
        else:
            site = "988lifeline.org" if country == "United States" else "988.ca"
            body.append(f"<p>The numbers could not be checked when this book was made: look them up on {site}.</p>")
    body.append("<p>988 in the US connects you to a local crisis centre by your phone's area code; calls, texts and "
                "chats are free and confidential. Outside the US and Canada, ask your local emergency number.</p>")
    book = K.new_book("fam_crisis_lines", "Crisis lines: suicide and mental health crisis numbers (US and Canada)",
                      "Mental health crisis help", GROUP, "GetBraille.com (written for this library)", "CC0",
                      K.CC0_URL, "https://988lifeline.org/", "The US and Canadian suicide and crisis numbers, with "
                      "the ways to reach them by phone, text, chat, relay service and videophone, checked on the "
                      "official sites when the book was made.", "Written for this library; its own words are CC0. "
                      "The numbers were checked on 988lifeline.org and 988.ca on the day shown.",
                      changes="written for this library", published=datetime.date.today().isoformat())
    book.version = "checked " + datetime.date.today().isoformat() + ": " + ", ".join(
        f"{c} {'confirmed' if ok else 'not confirmed'}" for c, _u, ok in checked)
    book.originals = [{"url": u, "kind": "html"} for u in dict.fromkeys(u for _c, u, _ok in checked)]
    book.pages.append(B.Page("crisis-lines", "Crisis lines", "\n".join(body), 0, ""))
    return book


COLLECTION = K.Collection("fam", GROUP, guides=GUIDES,
                          makers={"crisis_lines": (crisis_book, lambda name: datetime.date.today().strftime("%Y-%m"))},
                          words={"family-health": lambda: [f"fam:{g['name']}" for g in GUIDES] + ["fam:crisis_lines"]})

GROUPS = {}
LICENCE_LINES = {
    "cdc_agency_materials": "www.cdc.gov/other/agencymaterials.html (checked at every build): \"Most of the "
                            "information on the CDC and ATSDR websites is not subject to copyright, is in the public "
                            "domain\", on four conditions: credit CDC, a no-endorsement disclaimer, no change to the "
                            "substantive content, and saying it is free on CDC's site; all four are in the book's "
                            "notice, and the pages are kept whole with their text unchanged.",
    "nichd_acl_nimh": "safetosleep.nichd.nih.gov, acl.gov and nimh.nih.gov: works of the US government (17 U.S.C. "
                      "105, checked on govinfo.gov's policies page at every build); robots.txt allows the pages; no "
                      "AI rules (checked 2026-11-22).",
    "crisis_lines": "Crisis lines: written for this library (CC0); every number is checked at each build on "
                    "988lifeline.org and 988.ca (robots.txt allows both; no AI rules).",
}
NOT_INCLUDED = [
    ("NHTSA car seat guides (nhtsa.gov)", "Public domain, but www.nhtsa.gov answers programs \"403 Forbidden\" "
     "(robots.txt included, checked 2026-11-22). Link-only. Index: https://www.nhtsa.gov/vehicle-safety/"
     "car-seats-and-booster-seats"),
    ("National Institute on Aging health guides (nia.nih.gov)", "Public domain, but nia.nih.gov answers programs with "
     "a bot check (\"405\", robots.txt included; one page tried, 2026-11-22). Link-only. Index: "
     "https://www.nia.nih.gov/health/topics"),
    ("Eldercare Locator resources (eldercare.acl.gov)", "A JavaScript application whose pages come to programs "
     "without their text; ACL's own programme pages are built instead (fam:acl_aging_caregiving). Link-only. Index: "
     "https://eldercare.acl.gov/"),
    ("SAMHSA publications and the SAMHSA Library", "Public domain, but www.samhsa.gov and library.samhsa.gov answer "
     "programs \"403 Forbidden\" (checked 2026-11-22). Link-only. Index: https://library.samhsa.gov/"),
    ("Crisis line directories by state", "988 routes each call to a local centre by area code, so no state list is "
     "needed; the Lifeline's own list of local centres is not offered for reuse. Index: https://988lifeline.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
