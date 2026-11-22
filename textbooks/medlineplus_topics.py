"""MedlinePlus (US National Library of Medicine) for the reference library: only its public-domain parts (the owner's
request of 2026-11-22). Keys: medlineplus (every book), mlp:<name>.

What this module builds, in plain words, each IN FULL:
  - Health topics (English) and Temas de salud (Spanish): every health topic's summary written by NLM (what it is,
    causes, symptoms, diagnosis, treatment, prevention), one page per topic, A to Z (about 1,000 topics each);
  - Medical tests: every lab and medical test page (what it is, what it is used for, why you need it, what happens,
    how to prepare, risks, what the results mean), with its references;
  - Genetics: every genetic condition summary (about 1,300), every gene summary, and the handbook "Help Me Understand
    Genetics".

What is NOT taken (copyrighted and licensed to MedlinePlus only): the A.D.A.M. Medical Encyclopedia, the AHFS drug
information write-ups (American Society of Health-System Pharmacists), the herbs and supplements monographs (Natural
Medicines), the links to other organisations' pages (only their summaries are written by NLM; a topic page's links
are not copied), and pictures. From each topic page only the "Summary" block is read; from each test and genetics
page only the article's main column.

Licence: medlineplus.gov/about/using/usingcontent/ (checked at every build) lists what is in the public domain:
"Summaries on health topic pages", "Medical test information", "Summaries on Genetics pages, including health
condition, gene, and chromosome pages and the Help Me Understand Genetics handbook"; NLM asks for the credit
"Courtesy of MedlinePlus from the National Library of Medicine" (on every book).

Why not the XML files: MedlinePlus publishes its health topics as XML (medlineplus.gov/xml.html), but its robots.txt
says "Disallow: /xml/", so the files are not fetched; the same summaries are read from the topic pages, which
robots.txt allows. Requests go one at a time with the builder's pause.

Run from the repository's folder:
  python3 textbooks/medlineplus_topics.py mlp:health_topics --out build/textbooks --limit 5
  python3 textbooks/medlineplus_topics.py --list medlineplus
"""

import os
import string
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"
SITE = "https://medlineplus.gov"
LICENCE_PAGE = f"{SITE}/about/using/usingcontent/"
CREDIT = "Courtesy of MedlinePlus from the National Library of Medicine."
NOTICE = (CREDIT + " A work of the US National Library of Medicine (public domain). Health information, not medical "
          "advice: talk with your doctor or other health care provider about your own health.")
PUBLISHER = "US National Library of Medicine (MedlinePlus)"
LETTERS = list("abcdefghijklmnopqrstuvw") + ["xyz"]


def letter_rules(prefix):
    """Unit rules that put a page into "A" ... "Z" by the first letter of its address after prefix."""
    return [(rf"{prefix}{c}", c.upper()) for c in string.ascii_lowercase] + [(r".", "0-9")]


def topics(name, title, folder, language, description):
    """A health-topics book (English or Spanish): the summary block of every topic page of the A to Z lists."""
    base = f"{SITE}/{folder}"
    return K.us_web(
        GROUP, name=name, title=title, subject="Health topics", publisher=PUBLISHER, language=language,
        source=f"{base}healthtopics.html", licence_page=LICENCE_PAGE, licence_text=r"Summaries on health topic pages",
        description=description, notice=NOTICE,
        crawl=[(f"{base}healthtopics_{x}.html", 1) for x in LETTERS],
        pages=rf"^{base.replace('.', chr(92) + '.')}(?!healthtopics|all_|about|encyclopedia|druginfo|lab-tests|sitemap)"
              r"[a-z0-9]+\.html$",
        content=(r'<div id="topic-summary"[^>]*>', r"</div>"), unit_rules=letter_rules(base.replace(".", r"\.")),
        changes="each topic's summary made into a web page (its links to other organisations, pictures and "
                "encyclopedia boxes left out)", limit=1600)


GUIDES = [
    topics("health_topics", "MedlinePlus health topics (summaries, A to Z)", "", "eng",
           "Every MedlinePlus health topic summary written by the National Library of Medicine, one page per topic "
           "from A to Z: diseases and conditions, symptoms, tests, treatments, wellness and safety, each explaining "
           "what it is, its causes and symptoms, how it is diagnosed and treated, and how to prevent it."),
    topics("temas_de_salud", "MedlinePlus en español: temas de salud (resúmenes, de la A a la Z)", "spanish/", "spa",
           "Every Spanish MedlinePlus health topic summary (Temas de salud) written by the National Library of "
           "Medicine, one page per topic from A to Z."),
    K.us_web(GROUP, name="medical_tests", title="MedlinePlus medical tests", subject="Medical and lab tests",
             publisher=PUBLISHER, source=f"{SITE}/lab-tests/", licence_page=LICENCE_PAGE,
             licence_text=r"Medical test information", notice=NOTICE,
             description="Every MedlinePlus medical test page: what the test is, what it is used for, why you need "
                         "it, what happens during it, how to prepare, its risks and what the results mean, with "
                         "references.",
             crawl=[(f"{SITE}/lab-tests/", 1)], pages=rf"^{SITE.replace('.', chr(92) + '.')}/lab-tests/[a-z0-9-]+/$",
             content=(r'<div class="main">', r'<div class="side"'), unit_rules=letter_rules(r"/lab-tests/"),
             limit=600),
    K.us_web(GROUP, name="genetic_conditions", title="MedlinePlus Genetics: genetic conditions",
             subject="Genetics (health conditions)", publisher=PUBLISHER, source=f"{SITE}/genetics/condition/",
             licence_page=LICENCE_PAGE, licence_text=r"Summaries on Genetics pages", notice=NOTICE,
             description="Every genetic condition summary of MedlinePlus Genetics (formerly Genetics Home Reference): "
                         "its description, how common it is, its genetic causes, how it is inherited and its other "
                         "names, with references.",
             crawl=[(f"{SITE}/genetics/condition/", 2)],
             follow=rf"^{SITE.replace('.', chr(92) + '.')}/genetics/condition-[a-z0-9]/$",
             pages=rf"^{SITE.replace('.', chr(92) + '.')}/genetics/condition/[a-z0-9-]+/$",
             content=(r'<div class="main">', r'<div class="side"'), unit_rules=letter_rules(r"/condition/"),
             limit=2500),
    K.us_web(GROUP, name="genes", title="MedlinePlus Genetics: genes", subject="Genetics (genes)",
             publisher=PUBLISHER, source=f"{SITE}/genetics/gene/", licence_page=LICENCE_PAGE,
             licence_text=r"Summaries on Genetics pages", notice=NOTICE,
             description="Every gene summary of MedlinePlus Genetics: the gene's normal function, the health "
                         "conditions related to its changes, where it is on its chromosome and its other names.",
             crawl=[(f"{SITE}/genetics/gene/", 2)],
             follow=rf"^{SITE.replace('.', chr(92) + '.')}/genetics/gene-[a-z0-9]/$",
             pages=rf"^{SITE.replace('.', chr(92) + '.')}/genetics/gene/[a-z0-9-]+/$",
             content=(r'<div class="main">', r'<div class="side"'), unit_rules=letter_rules(r"/gene/"),
             limit=2500),
    K.us_web(GROUP, name="genetics_handbook", title="Help Me Understand Genetics (MedlinePlus)",
             subject="Genetics (handbook)", publisher=PUBLISHER, source=f"{SITE}/genetics/understanding/",
             licence_page=LICENCE_PAGE, licence_text=r"Help Me Understand Genetics handbook", notice=NOTICE,
             description="The whole handbook: cells and DNA, how genes work, genetic mutations and health, "
                         "inheriting genetic conditions, genetic testing, genetic consultation, gene therapy, the "
                         "Human Genome Project, genomic research and precision medicine.",
             crawl=[(f"{SITE}/genetics/understanding/", 2)],
             follow=rf"^{SITE.replace('.', chr(92) + '.')}/genetics/understanding/[a-z]+/$",
             pages=rf"^{SITE.replace('.', chr(92) + '.')}/genetics/understanding/([a-z]+/)*$",
             content=(r'<div class="main">', r'<div class="side"'),
             unit_rules=[(r"/basics/", "Cells and DNA"), (r"/howgeneswork/", "How genes work"),
                         (r"/mutationsanddisorders/", "Genetic mutations and health"),
                         (r"/inheritance/", "Inheriting genetic conditions"),
                         (r"/testing/", "Genetic testing"), (r"/consult/", "Genetic consultation"),
                         (r"/therapy/", "Gene therapy"), (r"/hgp/", "The Human Genome Project"),
                         (r"/genomicresearch/", "Genomic research"), (r"/precisionmedicine/", "Precision medicine"),
                         (r".", "Help Me Understand Genetics")], limit=300),
]

COLLECTION = K.Collection("mlp", GROUP, guides=GUIDES,
                          words={"medlineplus": lambda: [f"mlp:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "medlineplus_public_domain": "medlineplus.gov/about/using/usingcontent/ (read 2026-11-22, checked at every "
                                 "build): \"MedlinePlus information that is in the public domain includes ... "
                                 "Summaries on health topic pages; Medical test information; Summaries on Genetics "
                                 "pages, including health condition, gene, and chromosome pages and the Help Me "
                                 "Understand Genetics handbook\", with the credit \"Courtesy of MedlinePlus from the "
                                 "National Library of Medicine\". robots.txt allows the pages read and disallows "
                                 "/xml/ (so the XML files are not fetched); no AI rules.",
}
NOT_INCLUDED = [
    ("MedlinePlus health topic XML files (mplus_topics_*.xml)", "Public domain, but medlineplus.gov's robots.txt says "
     "\"Disallow: /xml/\", so they are not fetched; the same summaries are read from the topic pages "
     "(mlp:health_topics, mlp:temas_de_salud). Index: https://medlineplus.gov/xml.html"),
    ("A.D.A.M. Medical Encyclopedia (MedlinePlus)", "Copyrighted by A.D.A.M., Inc. (Ebix) and licensed to "
     "MedlinePlus only. Link-only for the personal assistant. Index: https://medlineplus.gov/encyclopedia.html"),
    ("MedlinePlus drug information (AHFS Consumer Medication Information) and herbs and supplements", "Copyrighted "
     "by the American Society of Health-System Pharmacists and by Natural Medicines, licensed to MedlinePlus only. "
     "Link-only. Index: https://medlineplus.gov/druginformation.html"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
