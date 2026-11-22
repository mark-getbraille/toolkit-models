"""Disabilities other than blindness, and disability rights beyond it, for the reference library, in the group
"Reference, disability and accessibility" (the owner's request of 2026-11-22; blindness and low vision have their own
collection). Keys: disability (every book), dis:<name>.

What this module builds, in plain words, each IN FULL (every page of the guide, read from the publisher's own site):
  - CDC's autism pages: signs and symptoms, screening and diagnosis, treatment and intervention services, autism in
    teenagers and adults, information for families and educators;
  - CDC's disability and health pages: what disability is, disability inclusion, disability barriers, healthy living,
    the kinds of disabilities, and data on disability in the United States;
  - CDC's hearing loss in children pages, with its parents' guide to hearing loss: screening and diagnosis, types of
    hearing loss, treatment and intervention (hearing aids, cochlear implants, sign language, early intervention),
    and the questions to ask;
  - CDC's pages on cerebral palsy, spina bifida, muscular dystrophy, Tourette syndrome, fragile X syndrome and fetal
    alcohol spectrum disorders (what each is, signs, diagnosis, treatment, living with it);
  - the FDA's hearing aid pages (types of hearing aids, over-the-counter hearing aids, how to get them, benefits and
    limitations, hearing aids and cellphones, other hearing devices) and its cochlear implant page;
  - the Department of Education's Office for Civil Rights pamphlet "Students with Disabilities Preparing for
    Postsecondary Education: Know Your Rights and Responsibilities" (2011, read whole from ERIC's copy on the
    Internet Archive because ed.gov refuses programs).
  Every book's notice ends with NOT_MEDICAL (general information, ask a doctor or audiologist), and the rights book
  with LEGAL ("General information, not legal advice; check the current rules or ask an accredited representative or
  lawyer.").

Already in the library and not repeated (link by name): NIDCD's hearing, balance, voice, speech and language pages,
with hearing aids, cochlear implants, American Sign Language and augmentative and alternative communication devices
(dir:nidcd_health); CDC's traumatic brain injury and concussion pages (firstaid:cdc_seizures_concussion); NICHD's
pages on intellectual and developmental disabilities, learning disabilities and dyslexia, Down syndrome and autism
(parent:nichd_health_topics); the Center for Parent Information and Resources' guides to IDEA, IEPs and specific
disabilities (parent:cpir_parent_guides); ACL's independent living, developmental disabilities and assistive
technology programmes (dir:acl_programs, elec:acl_assistive_technology); ADA.gov with service animals and the ADA
titles (legal:ada_gov), the ADA National Network fact sheets (legal:adata_factsheets), EEOC (legal:eeoc_workers),
the Fair Housing Act guides (civic:), the Access Board's accessible design guides (travel:access_board_ada_guide and
the ADA Standards), the laws themselves (law: keys: the ADA, the Rehabilitation Act, IDEA, the Fair Housing Act and
their regulations), disability employment policy and Ticket to Work (work:), Social Security disability
benefits (the benefits collection), NIMH's autism and ADHD brochures (fam:nimh_publications), and the blindness and
low vision collection (the vision helper's books, with the ADA, Section 504 and 508 and SSDI/SSI blindness rules).

Not built (NOT_INCLUDED, link-only): the FCC's relay service and captioning guides and the Department of Education's
IDEA and Section 504 pages (both refuse programs), the Model Systems Knowledge Translation Center's spinal cord
injury, brain injury and burn fact sheets (no open licence stated), and the
non-profits' guides (NAD, HLAA, ASHA, Autism Society, The Arc, United Spinal: copyright).

Licences: CDC's terms (checked at every build: credit CDC, no endorsement, kept whole); the FDA's pages and the OCR
pamphlet are works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build). robots.txt allows every page read; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/disability_life.py dis:cdc_autism --out build/textbooks --limit 5
  python3 textbooks/disability_life.py --list disability
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "disability"                   # "Reference, disability and accessibility" (sources.GROUPS already names it)
GROUPS = {}

# The line every legal or benefits book of these collections ends with (the owner's words of 2026-11-22).
LEGAL = "General information, not legal advice; check the current rules or ask an accredited representative or lawyer."
NOT_MEDICAL = ("General information, not medical advice or a diagnosis: ask your doctor, audiologist or therapist "
               "about your own situation.")

# CDC's terms (as in parenting.py and outdoor_cooking.py): checked at every build, kept whole, credit and the
# no-endorsement notice.
CDC = "https://www.cdc.gov"
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
CDC_PUBLISHER = "Centers for Disease Control and Prevention (CDC)"


def cdc_site_book(group, name, title, subject, sites, description, notice, units, limit=200):
    """A CDC web guide made of whole CDC sites, each read from its own site index ("site.html", which lists every
    page of the site), kept whole under CDC's terms; notice: what follows CDC's own conditions."""
    alt = "|".join(sites)
    pages = rf"^https://www\.cdc\.gov/({alt})/(?!es/|media/|site\.html|php/|hcp/)[a-z0-9-]+(/[a-z0-9-]+)*\.html$"
    entry = K.guide(group, name, title, subject, CDC_PUBLISHER, [f"{CDC}/{s}/site.html" for s in sites], pages,
                    description, f"{CDC_NOTICE} {notice}", depth=1, units=units, limit=limit)
    return dict(entry, licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True)


GUIDES = [
    cdc_site_book(GROUP, "cdc_autism", "Autism spectrum disorder: signs, diagnosis and services (CDC)",
                  "Autism", ["autism"],
                  "CDC's autism pages, every page: what autism spectrum disorder is, its signs and symptoms, "
                  "screening and diagnosis, treatment and intervention services, autism in teenagers and adults, "
                  "information for families and for educators, and CDC's data and research.", NOT_MEDICAL,
                  units=[(r"/data|/research", "Data and research"), (r".", "Autism")]),
    cdc_site_book(GROUP, "cdc_disability_health", "Disability and health: inclusion, barriers and healthy living "
                  "(CDC)", "Disability and health", ["disability-and-health"],
                  "CDC's disability and health pages, every page: what disability is and how common it is, the kinds "
                  "of disabilities (mobility, cognition, hearing, vision, independent living, self-care), disability "
                  "inclusion and the barriers people meet (attitudes, communication, physical, policy, "
                  "transportation), healthy living, emergency preparedness, and information for health care "
                  "providers.", NOT_MEDICAL,
                  units=[(r"/data|/disability-data", "Data"), (r".", "Disability and health")]),
    cdc_site_book(GROUP, "cdc_hearing_loss_children", "Hearing loss in children, with the parents' guide (CDC)",
                  "Hearing loss in children", ["hearing-loss-children", "hearing-loss-children-guide"],
                  "CDC's hearing loss in children pages and its parents' guide, every page: newborn hearing "
                  "screening, signs and diagnosis, types and causes of hearing loss, treatment and intervention "
                  "services (hearing aids, cochlear implants, early intervention, communication choices such as "
                  "American Sign Language, cued speech and spoken language), and questions to ask the care team.",
                  NOT_MEDICAL, units=[(r"-guide/", "Parents' guide"), (r".", "Hearing loss in children")]),
    cdc_site_book(GROUP, "cdc_developmental_conditions", "Cerebral palsy, spina bifida, muscular dystrophy, Tourette "
                  "syndrome, fragile X and FASD (CDC)", "Developmental disabilities",
                  ["cerebral-palsy", "spina-bifida", "muscular-dystrophy", "tourette-syndrome", "fragile-x-syndrome",
                   "fasd"],
                  "CDC's pages on six conditions, every page: cerebral palsy, spina bifida, muscular dystrophy "
                  "(Duchenne and Becker), Tourette syndrome and tic disorders, fragile X syndrome, and fetal alcohol "
                  "spectrum disorders: what each is, its signs and causes, diagnosis, treatment and therapies, and "
                  "living with it at home, at school and as an adult.", NOT_MEDICAL,
                  units=[(r"/cerebral-palsy/", "Cerebral palsy"), (r"/spina-bifida/", "Spina bifida"),
                         (r"/muscular-dystrophy/", "Muscular dystrophy"), (r"/tourette", "Tourette syndrome"),
                         (r"/fragile-x", "Fragile X syndrome"), (r".", "Fetal alcohol spectrum disorders")],
                  limit=250),
]

FDA_HEARING = "https://www.fda.gov/medical-devices/hearing-aids/"
FDA_PAGES = ["https://www.fda.gov/medical-devices/consumer-products/hearing-aids"] + [FDA_HEARING + p for p in (
    "hearing-loss", "types-hearing-aids", "otc-hearing-aids-what-you-should-know", "how-get-hearing-aids",
    "hearing-aid-benefits-and-limitations", "hearing-aids-and-cellphones", "other-hearing-devices-and-products")] + \
    ["https://www.fda.gov/medical-devices/implants-and-prosthetics/cochlear-implants"]
GUIDES.append(K.us_web(
    GROUP, name="fda_hearing_aids", title="Hearing aids, over-the-counter hearing aids and cochlear implants (FDA)",
    subject="Hearing aids and cochlear implants", publisher="US Food and Drug Administration (FDA)",
    source=FDA_PAGES[0], crawl=[(FDA_PAGES[0], 0)], urls=list(FDA_PAGES),
    pages=r"^https://www\.fda\.gov/medical-devices/(consumer-products/hearing-aids|hearing-aids/[a-z0-9-]+|"
          r"implants-and-prosthetics/cochlear-implants)$",
    description="The FDA's pages on hearing devices: hearing loss, the types of hearing aids, over-the-counter "
                "hearing aids for adults with mild to moderate hearing loss and what to know before buying, how to "
                "get hearing aids (with or without a hearing professional), their benefits and limitations, hearing "
                "aids and cellphones (hearing aid compatibility ratings), personal sound amplification products and "
                "other hearing devices, and cochlear implants (how they work, who may benefit, risks).",
    notice=f"From the US Food and Drug Administration: a US government work (public domain). {NOT_MEDICAL}",
    unit_rules=[(r"cochlear", "Cochlear implants"), (r".", "Hearing aids")], limit=len(FDA_PAGES) + 5))

PDFS = [
    K.us_pdf(GROUP, name="ocr_students_postsecondary", title="Students with Disabilities Preparing for "
             "Postsecondary Education: Know Your Rights and Responsibilities (US Department of Education, Office for "
             "Civil Rights, 2011)", subject="Disability rights in college", publisher="US Department of Education, "
             "Office for Civil Rights", archive="ERIC_ED537242", published="2011-09",
             version="September 2011 edition (ERIC ED537242, Internet Archive item ERIC_ED537242)",
             description="The Office for Civil Rights' questions and answers for students with disabilities going "
                         "to college or a trade school: how the ADA and Section 504 apply after high school (and how "
                         "that differs from IDEA and an IEP in school), telling the school about a disability, the "
                         "documentation a school may ask for, academic adjustments and auxiliary aids (such as "
                         "accessible formats, note takers and interpreters), and what to do if you think you were "
                         "treated unfairly.",
             notice=f"A work of the US Department of Education (public domain), read from ERIC's copy. 2011 edition: "
                    f"the rights it explains (the ADA and Section 504) still apply, but check the Office for Civil "
                    f"Rights' current pages for addresses and complaint steps. {LEGAL}"),
]

COLLECTION = K.Collection("dis", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"disability": lambda: [f"dis:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "disability_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public "
                      "domain on four conditions (credit CDC, no endorsement, no change to the substance, free on "
                      "CDC's site), met in each CDC book's notice; the pages are kept whole. robots.txt allows the "
                      "pages; no AI rules (checked 2026-11-22).",
    "disability_fda_ocr": "www.fda.gov and the Office for Civil Rights pamphlet (ERIC ED537242 on the Internet "
                          "Archive): works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's "
                          "policies page at every build); robots.txt allows the pages; no AI rules (checked "
                          "2026-11-22).",
}
NOT_INCLUDED = [
    ("FCC consumer guides: telecommunications relay services, video relay service (VRS), IP CTS, closed captioning, "
     "hearing aid compatibility, 711", "Public domain, but www.fcc.gov refuses programs (\"403\", robots.txt "
     "included, checked 2026-11-22). The FDA's hearing aids and cellphones page is built (dis:fda_hearing_aids). "
     "Link-only. Index: https://www.fcc.gov/consumers/guides/telecommunications-relay-service-trs and "
     "https://www.fcc.gov/consumers/guides/closed-captioning-television"),
    ("Department of Education: IDEA (sites.ed.gov/idea), Section 504 FAQs and OCR pages for students", "Public "
     "domain, but www.ed.gov and sites.ed.gov refuse programs (\"403\", robots.txt included, checked 2026-11-22). "
     "The OCR postsecondary pamphlet is built from ERIC's copy, and the Center for Parent Information and "
     "Resources' IDEA and IEP guides are in the library (parent:cpir_parent_guides). Link-only. Index: "
     "https://sites.ed.gov/idea/ and https://www.ed.gov/about/offices/list/ocr/504faq.html"),
    ("Model Systems Knowledge Translation Center fact sheets (spinal cord injury, traumatic brain injury, burn "
     "injury: wheelchairs, skin care, pressure injuries, bladder and bowel, adjusting to life)", "Made under a "
     "NIDILRR grant (Administration for Community Living), not a government work; its pages state no open licence "
     "(the footer says only that the contents do not necessarily represent federal policy), checked 2026-11-22. "
     "Link-only for the owner to read or fetch for his own use. Index: https://msktc.org/sci/factsheets and "
     "https://msktc.org/tbi/factsheets"),
    ("NAD, HLAA, ASHA (including its AAC pages), Autism Society, The Arc, United Spinal Association, Christopher & "
     "Dana Reeve Foundation, Brain Injury Association of America, International Dyslexia Association guides",
     "Copyright of each organisation; link-only. Index: https://www.nad.org/ https://www.hearingloss.org/ "
     "https://www.asha.org/public/speech/disorders/aac/ https://thearc.org/ https://unitedspinal.org/"),
    ("CDC ADHD pages", "Left to the mental health collection (another part of the library), which covers ADHD with "
     "NIMH's brochures; not repeated here. Index: https://www.cdc.gov/adhd/"),
    ("Surgeon General and NIH pages on chronic illness", "Chronic conditions are in the home health books "
     "(homecare:cdc_long_term_conditions and the NHS long-term conditions); invisible disabilities at work are in "
     "ODEP's pages (work:odep) and the ADA National Network fact sheets (legal:adata_factsheets); the Job "
     "Accommodation Network is link-only (its robots.txt shuts out AI readers: work_disability.py). Index: "
     "https://askjan.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
