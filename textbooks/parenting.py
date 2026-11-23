"""Parenting and family resources for the reference library, in the group "Reference, parenting and family" (the
owner's request of 2026-11-22). Keys: parenting (every book), parent:<name>. The Center for Parent Information and
Resources' special education guides (parent:cpir_parent_guides) are in "Teaching and homeschooling" (group key "k12",
the top-level section of 23 November 2026).

What this module builds, in plain words, each IN FULL (every page of the guide, read from the publisher's own site):
  - CDC's parenting pages, kept whole with their text unchanged as CDC's terms ask: Positive Parenting Tips by age,
    the Essentials for Parenting toddlers and teens, CDC's parent information by age and the child development
    pages; the childhood vaccine pages with the child and teen immunization schedules (the easy-to-read one for
    parents and the official one with its notes); children's mental health and adverse childhood experiences; and
    the injury pages for children (car seats, drowning, teen drivers, child abuse and neglect prevention);
  - the Child Welfare Information Gateway's topic pages for families (parenting, prevention, adoption, foster and
    kinship care, safety, youth, how to report abuse);
  - the Center for Parent Information and Resources' parent guides (disability fact sheets, early intervention, the
    IEP, parent rights and disagreements), public domain by its own statement;
  - NICHD's health topics and NIDA's pages for parents and teens;
  - CPSC's child safety guides (safe sleep and cribs, toys, magnets, water beads, button batteries, poison
    prevention, drowning at home) and Anchor It (furniture and TV tip-overs);
  - the Public Health Agency of Canada's pregnancy, baby and parenting pages (personal use only, non-US note);
  - the National Council on Disability's report on parents with disabilities, Rocking the Cradle (2012), whole.
  (The family health books already in family_health.py, CDC's Learn the Signs. Act Early., Safe to Sleep and the
  crisis lines, are not repeated. Child care, pregnancy and infant feeding are in early_childhood.py, and books to
  read aloud to children in read_aloud.py, in the same group.)

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): Head Start's ECLKC, the Department of
Education's parent and IDEA pages, StopBullying.gov, the FTC's and FBI's online safety pages (all answer programs
"403"), MyPlate (not reachable), the Gateway's publication PDFs (their host's robots.txt answers "403"),
HealthyChildren.org and Common Sense Media (copyright; AI readers shut out), ZERO TO THREE, Safe Kids Worldwide, the
NFB, APH, Perkins and AFB (copyright).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's, the Gateway's, CPSC's and CPIR's own statements are checked at every build and their conditions met in
each book's notice; canada.ca's terms allow non-commercial reproduction (personal use only).

Run from the repository's folder:
  python3 textbooks/parenting.py parent:cdc_parenting --out build/textbooks --limit 5
  python3 textbooks/parenting.py --list parenting
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "parenting"
GROUPS = {GROUP: "Reference, parenting and family"}
# A work its publisher has put in the public domain by its own statement (such as CPIR's "This product is public
# domain"), added to sources.ALLOWED through more_refs.allowed().
PD_DEDICATED = "Public domain (dedicated by its publisher)"
ALLOWED = {PD_DEDICATED: "open"}

# CDC's terms (the same as family_health.py): checked at every build, kept whole, credit and no-endorsement notice.
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
NOT_MEDICAL = "Health information, not medical advice: talk with your child's doctor or nurse."
CDC_PUBLISHER = "Centers for Disease Control and Prevention (CDC)"


def cdc_sites(sites, extra=""):
    """The page pattern of one or more CDC sites (the folder names, such as "parents"): every .html page under them
    except the Spanish copies, the media files and the site index itself; extra: more addresses (a pattern) to
    keep."""
    alt = "|".join(sites)
    own = rf"https://www\.cdc\.gov/({alt})/(?!es/|media/|site\.html)[a-z0-9-]+(/[a-z0-9-]+)*\.html"
    return rf"^({own}{'|' + extra if extra else ''})$"


def cdc_book(name, title, subject, sites, description, units, urls=(), extra="", limit=200):
    """A CDC web guide made of whole CDC sites, each read from its own site index ("site.html", which lists every
    page of the site), kept whole under CDC's terms."""
    entry = K.guide(GROUP, name, title, subject, CDC_PUBLISHER,
                    [f"https://www.cdc.gov/{s}/site.html" for s in sites], cdc_sites(sites, extra), description,
                    CDC_NOTICE + " " + NOT_MEDICAL, depth=1, units=units, limit=limit)
    entry["urls"] = list(urls)
    return dict(entry, licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True)


IMZ = "https://www.cdc.gov/vaccines/hcp/imz-schedules/"
GUIDES = [
    cdc_book("cdc_parenting", "Positive parenting and Essentials for Parenting (CDC)", "Parenting",
             ["child-development", "parents", "parenting-toddlers", "parenting-teens"],
             "CDC's pages for parents, every page: Positive Parenting Tips for each age (infants, toddlers 1 to 2 "
             "and 2 to 3, preschoolers, middle childhood and teens), the Essentials for Parenting toddlers and "
             "preschoolers (communicating, structure and rules, noticing and naming feelings, responding to "
             "behaviour, time-outs) and teens, CDC's parent information by age (infants, children and teens: "
             "health, safety, milestones and conditions), and the child development pages (developmental "
             "disabilities, safety for children with disabilities).",
             units=[(r"/positive-parenting-tips/", "Positive Parenting Tips"),
                    (r"/parenting-toddlers/", "Essentials for Parenting Toddlers and Preschoolers"),
                    (r"/parenting-teens/", "Essentials for Parenting Teens"), (r"/parents/", "Parent information"),
                    (r".", "Child development")],
             urls=["https://www.cdc.gov/child-development/positive-parenting-tips/index.html"]),
    cdc_book("cdc_child_vaccines", "Vaccines for your children and the immunization schedules (CDC)",
             "Childhood vaccines", ["vaccines-children"],
             "CDC's childhood vaccine pages for parents, every page (why vaccines matter, the diseases they "
             "prevent, before, during and after shots, keeping records, travel and when your child is sick), with "
             "the easy-to-read immunization schedule for parents and the official child and adolescent "
             "immunization schedule (by age, catch-up, by medical condition, its notes, appendix and addendum).",
             units=[(r"/imz-schedules/", "Immunization schedules"), (r".", "Vaccines for your children")],
             urls=["https://www.cdc.gov/vaccines/imz-schedules/child-easyread.html"] +
                  [IMZ + p for p in ("child-adolescent-age.html", "child-adolescent-catch-up.html",
                                     "child-adolescent-medical-indication.html", "child-adolescent-notes.html",
                                     "child-adolescent-appendix.html", "child-adolescent-addendum.html")],
             extra=r"https://www\.cdc\.gov/vaccines/(hcp/)?imz-schedules/child-[a-z-]+\.html"),
    cdc_book("cdc_children_mental_health", "Children's mental health and adverse childhood experiences (CDC)",
             "Children's mental health", ["children-mental-health", "aces"],
             "CDC's children's mental health pages, every page (anxiety and depression, behaviour and conduct "
             "problems, obsessive-compulsive disorder, post-traumatic stress disorder, treatment and getting help, "
             "data), and the pages on adverse childhood experiences (ACEs) and how to prevent them.",
             units=[(r"/aces/", "Adverse childhood experiences"), (r".", "Children's mental health")]),
    cdc_book("cdc_child_safety", "Keeping children safe: car seats, drowning, teen drivers and abuse prevention (CDC)",
             "Child injury prevention", ["child-passenger-safety", "drowning", "teen-drivers", "child-abuse-neglect"],
             "CDC's injury prevention pages for children and teens, every page: child passenger safety (car "
             "seats, booster seats and seat belts by age), drowning prevention (water safety, swimming skills, "
             "pools and bathtubs), teen drivers (risk factors, graduated licensing, parents' role) and child abuse "
             "and neglect prevention (risk and protective factors, what parents and communities can do).",
             units=[(r"/child-passenger-safety/", "Child passenger safety"), (r"/drowning/", "Drowning prevention"),
                    (r"/teen-drivers/", "Teen drivers"), (r".", "Child abuse and neglect prevention")]),
]

# ====================================================================== Child Welfare Information Gateway

# The Gateway (a service of the Children's Bureau, US Department of Health and Human Services) says on its list of
# publications: "Publications may be freely reproduced and distributed. However, when doing so, please credit
# Information Gateway." (checked at every build). Its topic pages for families are read; the publications' PDFs are
# on artifacts.childwelfare.gov, whose robots.txt answers "403", so they are not read (NOT_INCLUDED).
CWIG = "https://www.childwelfare.gov"
CWIG_TERMS = CWIG + "/all-information-gateway-publications-and-resources/"
CWIG_TEXT = r"Publications may be freely reproduced and distributed"
CWIG_TOPICS = "parents-and-caregivers|prevention|permanency|safety-and-risk|well-being|youth"
GUIDES.append(dict(
    K.guide(GROUP, "cwig_family_topics", "Parenting, foster care, adoption, kinship care and abuse prevention (Child "
            "Welfare Information Gateway)", "Child welfare for families", "Child Welfare Information Gateway "
            "(Children's Bureau, US Department of Health and Human Services)",
            [f"{CWIG}/topics/{t}/" for t in CWIG_TOPICS.split("|")],
            rf"^https://www\.childwelfare\.gov/(topics/({CWIG_TOPICS})(/[a-z0-9-]+)?|how-report-child-abuse-and-"
            r"neglect|find-help-personal-situation|state-child-abuse-and-neglect-reporting-numbers)/?$",
            "The Child Welfare Information Gateway's topic pages for families and caregivers, every page: parents "
            "and caregivers (fathers, birth parents, parenting supports), preventing child abuse and neglect "
            "(protective factors, family support), permanency (adoption, foster care, kinship care by relatives, "
            "adoption search and reunion, reunifying families, young people leaving foster care), safety and risk, "
            "children's well-being and youth; with how to report child abuse and neglect, the state reporting "
            "numbers and where to find help with a personal situation.",
            "From Child Welfare Information Gateway (childwelfare.gov), a service of the Children's Bureau, US "
            "Department of Health and Human Services: a US government work; its publications \"may be freely "
            "reproduced and distributed\" with credit to Information Gateway. To report child abuse or neglect, "
            "call your state's number or the Childhelp National Child Abuse Hotline, 1-800-422-4453.", depth=2,
            follow=rf"^https://www\.childwelfare\.gov/topics/({CWIG_TOPICS})/?$",
            units=[(r"/topics/parents-and-caregivers", "Parents and caregivers"), (r"/topics/prevention", "Prevention"),
                   (r"/topics/permanency", "Adoption, foster care and kinship care"),
                   (r"/topics/safety-and-risk", "Safety and risk"), (r"/topics/well-being", "Well-being"),
                   (r"/topics/youth", "Youth"), (r".", "Getting help")], limit=150),
    licence_page=CWIG_TERMS, licence_text=CWIG_TEXT,
    urls=[CWIG + "/state-child-abuse-and-neglect-reporting-numbers/"]))

# ====================================================================== Center for Parent Information and Resources

# parentcenterhub.org (funded by the US Department of Education's Office of Special Education Programs) says on every
# page: "This product is public domain. Authorization to reproduce it in whole or in part is granted." Each page is
# checked for that line (page_mark). Its robots.txt asks for 600 seconds between requests; the builder waits its
# longest pause (60 seconds), so the book is kept to the pages its family hubs list.
CPIR = "https://www.parentcenterhub.org"
CPIR_TEXT = r"This product is public domain\. Authorization to reproduce it in whole or in part is granted"
CPIR_HUBS = ["specific-disabilities", "disability-landing", "partc", "iep", "disagree", "family-information-guides"]
CPIR_NOT_PAGES = (r"login|logout|register|password|profile|members|activity|dashboard|checkout|payment|transaction|"
                  r"listing|categor|location|single-|search|region|conference|webinar|forums|groups|embed|external|"
                  r"cart|contact|find-your-center|branchmptac|rptacs|napcc|surveyitembank|centersconnect|nepact|"
                  r"buzz-from-the-hub|parent-center|parentcenter|the-parent|welcome-parent|the-cpir|whatiscpir|resourcelibrary|ta-resources|"
                  r"resources-in-|resource-family|resources-tta|wp-|tag|author|feed|buzz|korean|osep|naptac|dissem|web-|"
                  r"essa|rda|spp-apr|priority-|regs-|fapebrief|10-great|glossar|raisecenter")
# The special education guides are in "Teaching and homeschooling" (group key "k12", the top-level section of 23
# November 2026), with the IEP guide and the teaching books; key and request word unchanged.
GUIDES.append(dict(
    K.guide("k12", "cpir_parent_guides", "Parent guides to disabilities, special education and early intervention "
            "(Center for Parent Information and Resources)", "Special education and disabilities for parents",
            "Center for Parent Information and Resources (CPIR), funded by the US Department of Education",
            [f"{CPIR}/{h}/" for h in CPIR_HUBS],
            rf"^https://www\.parentcenterhub\.org/(?!(?:{CPIR_NOT_PAGES}))[a-z0-9-]+/?$",
            "The Center for Parent Information and Resources' guides for families, as its family hubs list them: "
            "getting started (where to find your Parent Training and Information Center), the fact sheets on "
            "specific disabilities (autism, ADHD, blindness and visual impairment, deafness, Down syndrome, "
            "learning disabilities, intellectual disability, speech and language and the rest), early intervention "
            "for babies and toddlers (Part C of IDEA), special education in school (evaluation, the IEP, parent "
            "rights, transition to adulthood) and family engagement.",
            "From the Center for Parent Information and Resources (parentcenterhub.org): \"This product is public "
            "domain. Authorization to reproduce it in whole or in part is granted.\" No endorsement by the US "
            "Department of Education is intended or should be inferred.", depth=1, limit=120,
            content=(r'<div id="main-content"[^>]*>', r'<footer\b|<div id="sidebar"')),
    licence=PD_DEDICATED, licence_page=CPIR + "/", licence_text=CPIR_TEXT, page_mark=CPIR_TEXT,
    licence_url="https://www.parentcenterhub.org/"))

# ====================================================================== NIH: NICHD health topics and NIDA for parents

GUIDES += [
    K.guide(GROUP, "nichd_health_topics", "Child and family health topics (NICHD)", "Child health",
            "Eunice Kennedy Shriver National Institute of Child Health and Human Development (NICHD), National "
            "Institutes of Health", "https://www.nichd.nih.gov/health/topics",
            r"^https://www\.nichd\.nih\.gov/health/topics/(?!factsheets|Pages|espanol)[a-z0-9-]+(/(conditioninfo|"
            r"about)(/[a-z0-9-]+)?)?$",
            "Every NICHD health topic, with its overview and its condition information pages (what it is, its "
            "symptoms, causes, diagnosis and treatment): pregnancy and pregnancy loss, preterm labour and birth, "
            "breastfeeding, newborn screening, birth defects and congenital anomalies, Down syndrome, fragile X, "
            "autism, cerebral palsy, intellectual and developmental disabilities, learning disabilities, puberty, "
            "childhood obesity, sudden infant death syndrome, and reproductive health.",
            "A work of the National Institutes of Health (public domain). " + NOT_MEDICAL, depth=2,
            follow=r"^https://www\.nichd\.nih\.gov/health/topics/[a-z0-9-]+(/conditioninfo)?$", limit=800),
    K.guide(GROUP, "nida_parents_teens", "Drugs, alcohol and vaping: for parents and teens (NIDA)",
            "Substance use prevention for families", "National Institute on Drug Abuse (NIDA), National Institutes "
            "of Health", "https://nida.nih.gov/research-topics/parents-educators",
            r"^https://nida\.nih\.gov/research-topics/parents-educators(/[a-z0-9-]+)*$",
            "NIDA's pages for parents and teens (what was NIDA for Teens), every page: conversation starters for "
            "talking with children and teens about drugs, the Mind Matters series on how drugs affect the brain "
            "(for children aged 11 to 13), lessons and activities, and the facts on vaping, cannabis, alcohol, "
            "opioids and other drugs as they are written for teens.",
            "A work of the National Institutes of Health (public domain). If you or your teen needs help, call or "
            "text 988, or find treatment at findtreatment.gov.", depth=2,
            follow=r"^https://nida\.nih\.gov/research-topics/parents-educators/[a-z0-9-]+$", limit=80),
]

# ====================================================================== CPSC child safety

# CPSC's copyright notice (on its privacy page, checked at every build): "Web page text, brochures, and posters
# presented on CPSC websites are public information. You may freely distribute ..." with credit to CPSC and no
# suggestion of CPSC's endorsement; pictures may belong to others, and the builder leaves pictures out.
CPSC = "https://www.cpsc.gov"
CPSC_TERMS = CPSC + "/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy"
CPSC_TEXT = r"Web page text, brochures, and posters presented on CPSC websites are public information"
CPSC_CENTRES = ("Button-Cell-Coin-Battery-Information-Center|In-Home-Drowning-Safety-Information-Center|Magnets|"
                "Poison-Prevention-Information-Center|Toys|Water-Beads-Information-Center")
CPSC_GUIDE_WORDS = r"[A-Za-z-]*(Kids|Babies|Baby|Crib|Toy|Furniture|Window|Batter|Child|Nursery)[A-Za-z-]*"
GUIDES.append(dict(
    K.guide(GROUP, "cpsc_child_safety", "Child safety at home: safe sleep, cribs, toys, tip-overs and batteries (CPSC "
            "and Anchor It)", "Child product safety", "US Consumer Product Safety Commission (CPSC)",
            [CPSC + "/SafeSleep"] + [f"{CPSC}/Safety-Education/Safety-Education-Centers/{c}"
                                     for c in CPSC_CENTRES.split("|")] +
            [CPSC + "/Safety-Education/Safety-Guides/Home-Indoors-Home-Kids-and-Babies-Furniture-Furnishings-and-"
             "Decorations-Electronics-and-Electrical/Get-On-Top-of-It-Before-They-Do", "https://www.anchorit.gov/"],
            rf"^https://(www\.cpsc\.gov/(SafeSleep|Safety-Education/Safety-Education-Centers/({CPSC_CENTRES})"
            rf"(/[A-Za-z0-9-]+)*|Safety-Education/Safety-Guides/{CPSC_GUIDE_WORDS}/[A-Za-z0-9-]+)|www\.anchorit\.gov/"
            r"(?!wp-|feed|news-press|espanol|privacy-policy|contact-us)([a-z0-9-]+/)*)$",
            "The CPSC's child safety guides, every page: safe sleep for babies (cribs, bassinets and play yards, a "
            "bare sleep space, infant products to avoid), the ABCs of baby safety and getting ready for a baby, toy "
            "safety (age labels, small parts and choking, magnets, water beads), button and coin batteries, poison "
            "prevention and child-resistant packaging, drowning at home (pools, bathtubs, buckets), and furniture and TV tip-overs with Anchor It (how to anchor furniture and TVs, what you'll "
            "need, installing an anchoring kit).",
            "From the US Consumer Product Safety Commission (cpsc.gov, anchorit.gov): public information, freely "
            "distributed with credit to CPSC; this copy does not suggest CPSC's endorsement. Pictures are left out. "
            "To report an unsafe product or a child's injury: SaferProducts.gov or 1-800-638-2772. Check recalls at "
            "cpsc.gov/Recalls.", depth=2,
            follow=rf"^https://www\.cpsc\.gov/Safety-Education/Safety-Education-Centers/({CPSC_CENTRES})$",
            units=[(r"/SafeSleep|Crib|Bab", "Safe sleep and baby products"), (r"anchorit|Furniture|Get-On-Top",
                                                                               "Furniture and TV tip-overs"),
                   (r"Toys|Magnets|Water-Beads", "Toys, magnets and water beads"),
                   (r"Batter", "Button and coin batteries"), (r"Poison", "Poison prevention"),
                   (r"Drowning", "Drowning at home"), (r".", "More child safety")], limit=200),
    licence_page=CPSC_TERMS, licence_text=CPSC_TEXT))

# ====================================================================== Canada (personal use) and parents with disabilities

# The Government of Canada's terms (canada.ca/en/transparency/terms.html, checked at every build): "Unless otherwise
# specified you may reproduce the materials in whole or in part for non-commercial purposes, and in any format,
# without charge or further permission", with the title, author and the address of the original named (the
# builder's credit line and originals do that). Commercial reproduction needs permission, so the book is marked
# personal use only. (Its name avoids the words "non-commercial", which build_textbooks.licence_short would shorten to
# a Creative Commons name.)
CROWN_NC = "Crown copyright (Canada), canada.ca terms for personal and public use"
ALLOWED[CROWN_NC] = "non-commercial"
CANADA_TERMS = "https://www.canada.ca/en/transparency/terms.html"
CANADA_TEXT = r"you may reproduce the materials in whole or in part for non-commercial purposes"
PHAC = "https://www.canada.ca/en/public-health/services"
GUIDES.append(dict(
    K.guide(GROUP, "canada_parenting", "Pregnancy, babies and parenting (Public Health Agency of Canada)",
            "Parenting (Canada)", "Public Health Agency of Canada (Government of Canada, canada.ca)",
            [PHAC + "/child-infant-health.html", PHAC + "/pregnancy.html"],
            r"^https://www\.canada\.ca/en/public-health/services/(health-promotion/childhood-adolescence|"
            r"child-infant-health|pregnancy)(/[a-z0-9-]+)*\.html$",
            "The Public Health Agency of Canada's pages for parents, every page: pregnancy (healthy pregnancy, the "
            "Sensible Guide to a Healthy Pregnancy, labour and birth), infant and child health (breastfeeding and "
            "infant nutrition, safe sleep, postpartum health, mental health during and after pregnancy, the Nobody's "
            "Perfect parenting sheets, injury prevention) and childhood and adolescence.",
            "Canadian source, personal use only: reproduced under the Government of Canada's terms for "
            "non-commercial reproduction; a copy of the version on canada.ca (the address of each page is at its "
            "end), not the official version, made without the Government of Canada's endorsement. Health care, "
            "benefits and the services named are Canada's.", depth=2,
            follow=r"^https://www\.canada\.ca/en/public-health/services/(child-infant-health|pregnancy)(/[a-z0-9-]+)"
                   r"*\.html$", units=[(r"/pregnancy", "Pregnancy"), (r"/child-infant-health", "Babies and children"),
                                      (r".", "Parenting")], limit=200, country="Canada"),
    licence=CROWN_NC, licence_url=CANADA_TERMS, licence_page=CANADA_TERMS, licence_text=CANADA_TEXT,
    personal_use=True))

# The National Council on Disability's report on the rights of parents with disabilities (blind parents included):
# a US government work, read whole from its PDF.
PDFS = [
    K.us_pdf(GROUP, name="ncd_rocking_the_cradle", title="Rocking the Cradle: Ensuring the Rights of Parents with "
             "Disabilities and Their Children (National Council on Disability)",
             subject="Parents with disabilities", publisher="National Council on Disability (NCD)",
             pdf="https://www.ncd.gov/assets/uploads/reports/2012/ncd-rocking-the-cradle.pdf",
             page="https://www.ncd.gov/report/rocking-the-cradle-ensuring-the-rights-of-parents-with-disabilities-and-"
                  "their-children/", published="2012-09-27", version="2012 report",
             description="The National Council on Disability's report on parents with disabilities, blind and "
                         "visually impaired parents among them: the barriers they meet in child welfare, family "
                         "courts, adoption and assisted reproduction, the supports that help (adaptive parenting "
                         "equipment and techniques, personal assistance, peer support), the laws that protect "
                         "them (the ADA, Section 504) and NCD's recommendations.",
             notice="A work of the National Council on Disability, an independent federal agency (public domain)."),
]

COLLECTION = K.Collection("parent", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"parenting": lambda: [f"parent:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "parenting_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public "
                     "domain on four conditions (credit CDC, no endorsement, no change to the substance, free on "
                     "CDC's site), met in each CDC book's notice; the pages are kept whole. www.cdc.gov's robots.txt "
                     "allows the pages; no AI rules (checked 2026-11-22).",
}
LICENCE_LINES["parenting_childwelfare"] = (
    "www.childwelfare.gov/all-information-gateway-publications-and-resources/ (checked at every build): "
    "\"Publications may be freely reproduced and distributed. However, when doing so, please credit Information "
    "Gateway\"; a US government work (Children's Bureau). robots.txt: \"User-agent: *\" \"Allow: /\"; no AI rules "
    "(checked 2026-11-22).")
LICENCE_LINES["parenting_nih"] = (
    "www.nichd.nih.gov and nida.nih.gov: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
    "policies page at every build); robots.txt allows the pages; no AI rules (checked 2026-11-22).")
LICENCE_LINES["parenting_cpsc"] = (
    "www.cpsc.gov/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy (checked at every build): \"Web page "
    "text, brochures, and posters presented on CPSC websites are public information. You may freely distribute\" "
    "them, crediting CPSC and not suggesting CPSC's endorsement (both in the notice); pictures, which may belong to "
    "others, are left out. robots.txt of cpsc.gov and anchorit.gov allows the pages; no AI rules (checked "
    "2026-11-22).")
LICENCE_LINES["parenting_canada"] = (
    "www.canada.ca/en/transparency/terms.html (checked at every build): \"Unless otherwise specified you may "
    "reproduce the materials in whole or in part for non-commercial purposes, and in any format, without charge or "
    "further permission\", naming the title, author and the address of the original; commercial reproduction needs "
    "permission, so the book is personal use only. robots.txt allows /en/public-health/; no AI rules (checked "
    "2026-11-22).")
LICENCE_LINES["parenting_ncd"] = (
    "www.ncd.gov: the National Council on Disability is an independent federal agency, so its reports are works of "
    "the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build); robots.txt allows "
    "/assets/uploads/; no AI rules (checked 2026-11-22).")
LICENCE_LINES["parenting_cpir"] = (
    "www.parentcenterhub.org (every page, checked on each page read): \"This product is public domain. "
    "Authorization to reproduce it in whole or in part is granted. While permission to reprint material from this "
    "website is not necessary, the citation should be: Center for Parent Information and Resources\". robots.txt: "
    "Crawl-delay 600 (the builder waits 60 seconds, its longest pause), nothing else refused; no AI rules (checked "
    "2026-11-22).")
NOT_INCLUDED = [
    ("Head Start Early Childhood Learning and Knowledge Center (ECLKC, now headstart.gov)", "Public domain, but "
     "eclkc.ohs.acf.hhs.gov and headstart.gov answer programs \"403 Forbidden\" (checked 2026-11-22). Link-only. "
     "Index: https://headstart.gov/"),
    ("US Department of Education parent guides and the IDEA special education parent pages", "Public domain, but "
     "www.ed.gov and sites.ed.gov answer programs \"403 Forbidden\", robots.txt included (checked 2026-11-22). The "
     "Center for Parent Information and Resources (funded by the Department) is built (parent:cpir_parent_guides). "
     "Link-only. Index: https://www.ed.gov/parents and https://sites.ed.gov/idea/parents-families/"),
    ("StopBullying.gov", "Public domain, but www.stopbullying.gov answers programs \"403 Forbidden\", robots.txt "
     "included (checked 2026-11-22). Link-only. Index: https://www.stopbullying.gov/"),
    ("FTC kids online safety (consumer.ftc.gov; OnGuardOnline now leads there) and the FBI's Safe Online Surfing",
     "Public domain, but consumer.ftc.gov and sos.fbi.gov answer programs \"403 Forbidden\", robots.txt included "
     "(checked 2026-11-22). Link-only. Index: https://consumer.ftc.gov/features/protecting-kids-online and "
     "https://sos.fbi.gov/"),
    ("USDA MyPlate for kids (myplate.gov)", "Public domain, but www.myplate.gov could not be reached from the build "
     "machine (502 upstream, again on 2026-11-22). WIC's pages are built (early:wic_breastfeeding). Link-only. "
     "Index: https://www.myplate.gov/life-stages/kids"),
    ("HealthyChildren.org (American Academy of Pediatrics) and Common Sense Media", "Copyright of the AAP and of "
     "Common Sense Media, and both sites' robots.txt shut out AI companies' readers (checked 2026-11-22), so they "
     "are not read. Link-only. Index: https://www.healthychildren.org/ and https://www.commonsensemedia.org/"),
    ("ZERO TO THREE and Safe Kids Worldwide", "\"©2026 ZERO TO THREE\" and \"© Safe Kids Worldwide\"; not openly "
     "licensed (checked 2026-11-22). Link-only. Index: https://www.zerotothree.org/resource/ and "
     "https://www.safekids.org/safetytips"),
    ("Blind parents: NFB's blind parents community and guides, APH, Perkins and the American Foundation for the "
     "Blind", "\"Copyright © 2026 National Federation of the Blind\", \"Copyright © 2026 American Printing House\", "
     "\"© 2026 Perkins School for the Blind\" and \"© Copyright 2026 American Foundation for the Blind\" (checked "
     "2026-11-22); not openly licensed. The National Council on Disability's report on parents with disabilities "
     "is built (parent:ncd_rocking_the_cradle). Link-only. Index: https://nfb.org/our-community/blind-parents, "
     "https://nfb.org/programs-services/advocacy/advocacy-resources/blind-parents-essential-guide-effective-"
     "communication, https://www.perkins.org/resources/ and https://www.afb.org/"),
    ("Guides for blind and visually impaired parents on the Internet Archive", "The guides found (Off to a Good "
     "Start, Parenting Preschoolers, Talk to Me, ERIC documents) are for parents OF blind children and are in "
     "copyright or lending-only; the open ones are older than 1931 and out of date (Light on Dark Paths, 1883); "
     "no open guide on parenting with a visual impairment was found (checked 2026-11-22). Index: "
     "https://archive.org/search?query=blind+parents"),
    ("CPSC window covering (blind cord) safety guide", "CPSC's consumer guide to corded window coverings is not "
     "linked from its safety education pages or listed in its sitemap (only rulemaking papers are, checked "
     "2026-11-22), and no other open guide to it was found. Link-only: the industry's own safety site is "
     "copyright. Index: https://www.cpsc.gov/Safety-Education and "
     "https://windowcoverings.org/"),
    ("Child Welfare Information Gateway publications (factsheets for families, bulletins, state statutes series) as "
     "PDFs", "Freely reproducible, but the PDFs are on artifacts.childwelfare.gov, whose robots.txt answers \"403 "
     "Forbidden\" (checked 2026-11-22), so programs may not read them; the topic pages are built "
     "(parent:cwig_family_topics). Link-only. Index: https://www.childwelfare.gov/find-resources/"
     "explore-information-gateway-publication-series/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
