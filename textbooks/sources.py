"""Which textbooks and reference works the textbooks workflow builds, where each comes from, and what was checked.

Every source here was checked by hand on 2026-11-18 (the licence line is quoted in LICENCE_LINES), and the builder
checks each book's licence again from the source itself every time it runs (build_textbooks.py: the OpenStax
collection file, the Siyavula book's copyright page, the DSpace record of the international body). A book whose
licence is not one of ALLOWED, or no longer says what is written here, is left out of the release and listed with
the reason in textbooks.json ("left_out").

Licences and how they are shown in the Digital Accessibility Toolkit:
  open          CC BY, CC0, public domain, Open Government Licence: shown as they are
  share-alike   CC BY-SA: shown as they are (copies and changes keep the same licence)
  non-commercial  CC BY-NC, CC BY-NC-SA: shown with "not for commercial use" (fine for personal and school use)
  never         any "NoDerivatives" (ND) licence: a ZIM file is a new arrangement of the work (its pages split
                and rewritten as web pages, math turned into text), which counts as an adaptation, so ND works are
                left out.

Kinds of source:
  osbooks   an OpenStax book repository on GitHub (github.com/openstax/osbooks-*), CNXML and pictures; one
            repository can hold several books (its META-INF/books.xml lists them)
  siyavula  a Siyavula textbook read from its online reader (www.siyavula.com/read/..., allowed by its robots.txt);
            the reader has the formulas as LaTeX, which is turned into text (the EPUB has them only as pictures
            without descriptions)
  dspace    a publication in the open repository of an international body (a DSpace 7 site: the World Health
            Organization's IRIS, the World Bank's Open Knowledge Repository, FAO's): its record gives the title,
            licence and the original PDF, which is turned into one page per chapter of its bookmarks
"""

# The OpenStax repositories (each holds one or more books). Checked with "git ls-remote" on 2026-11-18.
OSBOOKS = [
    "anatomy-physiology", "biology-bundle", "chemistry-bundle", "college-physics-bundle",
    "university-physics-bundle", "physics", "statistics", "astronomy", "psychology", "introduction-sociology",
    "microbiology", "american-government", "us-history", "world-history", "principles-economics-bundle",
    "introductory-statistics-bundle", "calculus-bundle", "college-algebra-bundle", "prealgebra-bundle",
    "contemporary-mathematics", "business-ethics", "introduction-business", "introduction-philosophy",
    "writing-guide", "entrepreneurship", "principles-accounting-bundle", "introduction-intellectual-property",
    "introduction-anthropology", "introduction-political-science", "college-success-bundle", "principles-marketing",
    "business-law", "principles-finance", "data-science", "lifespan-development", "organic-chemistry",
    "life-liberty-pursuit-happiness", "foundations-information-systems", "workplace-software-skills",
]

# Siyavula (South Africa): the books of its online reader; subject path, grade, title, subject in words.
SIYAVULA = [
    ("mathematics", 10, "Mathematics Grade 10", "Mathematics"),
    ("mathematics", 11, "Mathematics Grade 11", "Mathematics"),
    ("mathematics", 12, "Mathematics Grade 12", "Mathematics"),
    ("physical-sciences", 10, "Physical Sciences Grade 10", "Physics and chemistry"),
    ("physical-sciences", 11, "Physical Sciences Grade 11", "Physics and chemistry"),
    ("physical-sciences", 12, "Physical Sciences Grade 12", "Physics and chemistry"),
    ("natural-sciences", 7, "Natural Sciences Grade 7", "Science"),
    ("natural-sciences", 8, "Natural Sciences Grade 8", "Science"),
    ("natural-sciences", 9, "Natural Sciences Grade 9", "Science"),
]

# Reference works of international bodies (the "Reference works" part of the Textbooks group): DSpace site,
# handle, id, short title, subject, body, licence expected (checked again from the record when built).
DSPACE = [
    ("https://iris.who.int", "10665/371090", "who_essential_medicines_2023",
     "WHO Model List of Essential Medicines, 23rd list (2023)", "Medicine", "World Health Organization",
     "CC BY-NC-SA 3.0 IGO"),
    ("https://openknowledge.worldbank.org", "10986/41919", "worldbank_wdr_2024", "World Development Report 2024",
     "Economics", "World Bank", "CC BY 3.0 IGO"),
    ("https://openknowledge.fao.org", "20.500.14283/cd2616en", "fao_sofa_2024",
     "The State of Food and Agriculture 2024", "Agriculture", "Food and Agriculture Organization (FAO)",
     "CC BY-NC-SA 3.0 IGO"),
]

# The licence lines found when each source was checked by hand (quoted from the source).
LICENCE_LINES = {
    "osbooks": "Each OpenStax collection file states its own licence, for example osbooks-physics: "
               "<md:license url=\"http://creativecommons.org/licenses/by/4.0/\">Creative Commons Attribution "
               "License</md:license>; osbooks-anatomy-physiology (since March 2026): \"Creative Commons "
               "Attribution-NonCommercial-ShareAlike 4.0 International\".",
    "siyavula": "Siyavula's reader pages: \"All Siyavula textbook content made available on this site is released "
                "under the terms of a Creative Commons Attribution License.\" The books' copyright page: \"This "
                "book is released under the CC-BY 4.0 license. ... you have to acknowledge Siyavula Education as "
                "the original author ... Everything Maths and Everything Science are trademarks of Siyavula "
                "Education and cannot be used without permission\" (so the books are named by subject and grade, "
                "with Siyavula credited, never with those trademarks).",
    "who": "WHO IRIS record 10665/371090: dc.rights \"CC BY-NC-SA 3.0 IGO\".",
    "worldbank": "World Bank OKR record 10986/41919: dc.rights \"CC BY 3.0 IGO\".",
    "fao": "FAO record 20.500.14283/cd2616en: dc.rights.license \"CC BY NC SA 3.0 IGO\" (its page also mentions a "
           "CC BY 4.0 copyright page; the stricter licence of the record is used).",
}

ALLOWED = {
    "CC0": "open", "PD": "open", "OGL": "open", "CC BY": "open", "CC BY-SA": "share-alike",
    "CC BY-NC": "non-commercial", "CC BY-NC-SA": "non-commercial",
}

# What was looked at and not included, with the reason (shown in textbooks.json and the toolkit's manual).
NOT_INCLUDED = [
    ("BCcampus Open Textbooks (Canada)", "Its Pressbooks site answers automated requests with a bot check "
     "(Cloudflare \"Just a moment\"), also for the book exports, so it cannot be fetched automatically."),
    ("eCampusOntario Open Library (Canada)", "Its Pressbooks site refuses automated requests (403), robots.txt "
     "included."),
    ("CAUL Open Educational Resources Collective (Australia and New Zealand)", "Its Pressbooks site refuses "
     "automated requests (403)."),
    ("OpenLearn, The Open University (UK)", "www.open.edu refuses automated requests (403), robots.txt included; "
     "its courses are mostly CC BY-NC-SA and could be added if the Open University allows automated download."),
    ("Oak National Academy (UK)", "Its curriculum resources are offered through an API that needs a sign-up key; "
     "not fetched without one."),
    ("Scoilnet and NCCA (Ireland)", "No open licence was found for their materials."),
    ("Te Pūkenga and New Zealand open textbooks", "No openly licensed collection with an automated download was "
     "found."),
    ("NCERT textbooks (India)", "Copyright NCERT, all rights reserved: not openly licensed."),
    ("NROER (India)", "Licences differ per item and were not checked one by one."),
    ("DOT4D and UCT open textbooks (South Africa)", "Their repository (open.uct.ac.za) allows automated download, "
     "but each book's licence was not checked one by one yet; add them to DSPACE after checking each."),
    ("Commonwealth of Learning (oasis.col.org)", "The repository is mostly reports; its open textbooks were not "
     "checked one by one yet."),
    ("UNESCO (unesdoc.unesco.org)", "Its document pages refuse automated requests (403)."),
    ("OECD", "Its licences differ per publication and were not checked one by one."),
    ("Siyavula Mathematical Literacy and Life Sciences", "Only PDFs without a reader version with text formulas; "
     "left out until their pictures of formulas can be described."),
]
