"""The sources of the Writing Kit: the ones it uses (SOURCES) and the ones that were checked and cannot be used
(NOT_USED), each with the reason. Every licence, robots.txt and terms page was checked by hand in November 2026; the
robots.txt is also read again by fetch.py every time the kit downloads anything.

Licence classes (the same words as the Picture Model Training Kit):
  open               may be used and shared for any purpose, with credit (public domain, CC0, CC BY, Apache, MIT);
  share-alike        may be used for any purpose with credit, but whatever is made from it and shared must carry the
                     same licence (CC BY-SA);
  personal use only  no licence lets others re-use the text; it is used only on the owner's own computer to train
                     the owner's own model, and neither the data nor the trained add-on is shared.
By default the builder uses only open and share-alike sources; --personal adds the personal-use ones. Corpora that
are public but whose writers never gave up their copyright (Enron, mailing lists, Usenet, IRC, public comments) are
personal use only unless the source's own terms say otherwise.
"""

from dataclasses import dataclass, field

OPEN, SHARE_ALIKE, PERSONAL = "open", "share-alike", "personal use only"
CLASSES = [OPEN, SHARE_ALIKE, PERSONAL]


@dataclass
class Source:
    """One source the kit can read. key is what --sources takes; reader is the name of the function in readers.py."""
    key: str
    name: str
    licence: str
    licence_class: str
    licence_url: str
    credit: str
    home: str
    reader: str
    notes: str = ""
    warnings: list = field(default_factory=list)


SOURCES = [
    Source(
        key="oasst2",
        name="OpenAssistant Conversations (OASST2)",
        licence="Apache License 2.0",
        licence_class=OPEN,
        licence_url="https://www.apache.org/licenses/LICENSE-2.0",
        credit="OpenAssistant (LAION) and its volunteer contributors",
        home="https://huggingface.co/datasets/OpenAssistant/oasst2",
        reader="read_oasst2",
        notes="Human-written conversations (OASST2 includes all of OASST1). The kit takes only English requests to "
              "write or improve an email, letter, note, text message, memo or announcement, with the best-ranked "
              "human answer; machine-written ones (marked synthetic) are skipped. Official file: "
              "2023-11-05_oasst2_ready.trees.jsonl.gz."),
    Source(
        key="dolly",
        name="databricks-dolly-15k",
        licence="CC BY-SA 3.0",
        licence_class=SHARE_ALIKE,
        licence_url="https://creativecommons.org/licenses/by-sa/3.0/",
        credit="Databricks, Inc. and its employees",
        home="https://huggingface.co/datasets/databricks/databricks-dolly-15k",
        reader="read_dolly",
        notes="Instructions and answers written by Databricks employees. The kit takes only the requests to write "
              "an email, letter, note, message, memo or announcement. Official file: databricks-dolly-15k.jsonl."),
    Source(
        key="enron",
        name="Enron Email Dataset (CMU, May 2015 version)",
        licence="No licence. Made public by the US Federal Energy Regulatory Commission (FERC) during its 2003 "
                "investigation; distributed by Carnegie Mellon University (William Cohen) as a resource for "
                "researchers, with a request to be sensitive to the privacy of the people involved",
        licence_class=PERSONAL,
        licence_url="https://www.cs.cmu.edu/~enron/",
        credit="Enron Email Dataset, prepared by the CALO Project (SRI) and distributed by William W. Cohen, "
               "Carnegie Mellon University",
        home="https://www.cs.cmu.edu/~enron/",
        reader="read_enron",
        notes="The kit reads the one official file (enron_mail_20150507.tar.gz, 1.7 GB) as it arrives and stops "
              "once it has enough; it uses each person's own sent mail, whole, with its quoted thread. This copy has "
              "no attachments (they were taken out before it was published). The corpus was NOT redacted by anyone "
              "before release (unlike the government email releases, which the agencies reviewed and redacted). The "
              "emails were written by Enron employees, who keep their copyright, so it is personal use only.",
        warnings=["The robots.txt of www.cs.cmu.edu blocks two single companies' AI crawlers (Meta's "
                  "meta-externalagent and ByteDance's Bytespider) along with some search crawlers. It does not "
                  "block AI-training crawlers in general (GPTBot, ClaudeBot, CCBot and Google-Extended are allowed) "
                  "and has no ai-train=no signal; it allows this kit with a 10-second Crawl-delay. The owner "
                  "should decide whether to use it; it is off unless --personal is given."]),
    Source(
        key="w3c",
        name="W3C public mailing list archives (lists.w3.org)",
        licence="No public licence. People who post to W3C public lists give W3C permission to publish their "
                "messages in its archives; W3C staff have said posters have not given that permission to others",
        licence_class=PERSONAL,
        licence_url="https://www.w3.org/Mail/",
        credit="Messages from the W3C public mailing list archives (https://lists.w3.org/Archives/Public/)",
        home="https://lists.w3.org/Archives/Public/",
        reader="read_w3c",
        notes="The kit reads the public HTML archive pages of a few W3C lists (by default the accessibility lists "
              "w3c-wai-ig, w3c-wai-gl and public-aria), one page every 3 seconds. robots.txt closes the raw "
              "'mboxes' downloads and the member-only archives, and the kit never reads them. Attachments linked from "
              "a message page are downloaded too and saved beside the message."),
    Source(
        key="usenet", name="Usenet newsgroups (Giganews collection on the Internet Archive)",
        licence="No licence. Old public Usenet posts kept by the Internet Archive; the writers keep their copyright",
        licence_class=PERSONAL, licence_url="https://archive.org/details/giganews",
        credit="Usenet posts from the Giganews collection, Internet Archive", home="https://archive.org/details/giganews",
        reader="read_usenet",
        notes="One official mbox file per newsgroup (alt.vacation, misc.writing.moderated, misc.writing by default), "
              "read as it arrives. Posts keep their quoted text; old uuencoded files are left out of the text."),
    Source(
        key="debian", name="Debian mailing lists (lists.debian.org)",
        licence="No licence. Public list archives; the writers keep their copyright",
        licence_class=PERSONAL, licence_url="https://www.debian.org/MailingLists/",
        credit="Messages from the Debian mailing list archives (https://lists.debian.org/)",
        home="https://lists.debian.org/", reader="read_debian",
        notes="The public HTML archive of debian-user, one page at a time; attachment links are downloaded too."),
    Source(
        key="irc", name="Ubuntu IRC logs (irclogs.ubuntu.com)",
        licence="No licence. Ubuntu publishes the logs of its public IRC channels; the writers keep their copyright",
        licence_class=PERSONAL, licence_url="https://irclogs.ubuntu.com/",
        credit="Ubuntu IRC logs (https://irclogs.ubuntu.com/)", home="https://irclogs.ubuntu.com/",
        reader="read_irc", notes="Plain-text daily logs of #ubuntu and #ubuntu-offtopic on a few days."),
    Source(
        key="sms", name="SMS Spam Collection (UCI Machine Learning Repository)",
        licence="CC BY 4.0", licence_class=OPEN, licence_url="https://creativecommons.org/licenses/by/4.0/",
        credit="Tiago A. Almeida and Jose Maria Gomez Hidalgo, SMS Spam Collection, UCI Machine Learning Repository",
        home="https://archive.ics.uci.edu/dataset/228/sms+spam+collection", reader="read_sms",
        notes="Real text messages. Only the ordinary ones (marked 'ham') are used, never the spam."),
    Source(
        key="taskmaster", name="Taskmaster-1 (Google)", licence="CC BY 4.0", licence_class=OPEN,
        licence_url="https://creativecommons.org/licenses/by/4.0/",
        credit="Bill Byrne, Karthik Krishnamoorthi, Chinnadhurai Sankar, Arvind Neelakantan, Amit Dubey, Kyu-Young "
               "Kim and Andy Cedilnik, Google LLC (Taskmaster-1)",
        home="https://github.com/google-research-datasets/Taskmaster", reader="read_taskmaster",
        notes="Spoken-style conversations between two people, one playing an assistant (the WOZ part)."),
    Source(
        key="sgd", name="Schema-Guided Dialogue (Google)", licence="CC BY-SA 4.0", licence_class=SHARE_ALIKE,
        licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
        credit="Rastogi et al., Google Research, Schema-Guided Dialogue dataset",
        home="https://github.com/google-research-datasets/dstc8-schema-guided-dialogue", reader="read_sgd",
        notes="Chats between a customer and a virtual assistant (first training file)."),
    Source(
        key="multiwoz", name="MultiWOZ 2.2", licence="MIT License", licence_class=OPEN,
        licence_url="https://github.com/budzianowski/multiwoz/blob/master/LICENSE",
        credit="Pawel Budzianowski and the MultiWOZ authors", home="https://github.com/budzianowski/multiwoz",
        reader="read_multiwoz", notes="Chats between a visitor and a tourist information clerk (first training file)."),
    Source(
        key="topical", name="Topical-Chat (Amazon)", licence="Community Data License Agreement - Sharing 1.0",
        licence_class=SHARE_ALIKE, licence_url="https://cdla.dev/sharing-1-0/",
        credit="Amazon.com, Inc. or its affiliates (Topical-Chat)", home="https://github.com/alexa/Topical-Chat",
        reader="read_topical", notes="Friendly chats between two strangers about a topic (one official file)."),
    Source(
        key="wikitalk", name="Wikipedia talk pages (Simple English Wikipedia dump)",
        licence="CC BY-SA 4.0 (and GFDL)", licence_class=SHARE_ALIKE,
        licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
        credit="Simple English Wikipedia contributors", home="https://dumps.wikimedia.org/simplewiki/",
        reader="read_wikitalk",
        notes="Discussion pages from the official dump, read as it arrives; each comment ends with its signature. "
              "While Wikimedia moves to new dumps, this file is offered only from the 1st to the 14th of each "
              "month (it was not offered on the day of the test build, 21 November 2026)."),
    Source(
        key="gutenberg", name="Letters in the public domain (Project Gutenberg)",
        licence="Public domain in the United States (published before 1930)", licence_class=OPEN,
        licence_url="https://www.gutenberg.org/policy/license.html",
        credit="Project Gutenberg volunteers (https://www.gutenberg.org/)", home="https://www.gutenberg.org/",
        reader="read_gutenberg",
        notes="Books of letters found in Gutenberg's catalogue, from its official mirror gutenberg.pglaf.org (the "
              "main site asks programs to use mirrors). Gutenberg's header and licence text are taken off, as its "
              "licence allows for public-domain books."),
    Source(
        key="sbcsae", name="Santa Barbara Corpus of Spoken American English (transcripts)",
        licence="CC BY-ND 3.0 US (no changes allowed)", licence_class=PERSONAL,
        licence_url="https://creativecommons.org/licenses/by-nd/3.0/us/",
        credit="John W. Du Bois, Wallace L. Chafe, Charles Meyer, Sandra A. Thompson, Robert Englebretson and "
               "Nii Martey, Santa Barbara Corpus of Spoken American English, UC Santa Barbara",
        home="https://www.linguistics.ucsb.edu/research/santa-barbara-corpus-spoken-american-english",
        reader="read_sbcsae",
        notes="Each transcript is used whole and unchanged (the licence allows no changes), so it is personal use "
              "only: a trained model could count as a changed version."),
    Source(
        key="regulations", name="Public comments to US federal agencies (regulations.gov)",
        licence="Public records, but each comment's writer keeps the copyright", licence_class=PERSONAL,
        licence_url="https://www.regulations.gov/user-notice",
        credit="Public comments from regulations.gov", home="https://www.regulations.gov/",
        reader="read_regulations",
        notes="Needs a free API key from api.data.gov in the setting REGULATIONS_GOV_API_KEY; without one it is "
              "skipped. Comments with only an attachment are left out."),
    Source(
        key="scotus", name="US Supreme Court oral argument transcripts", licence="Public domain (US government work)",
        licence_class=OPEN, licence_url="https://www.supremecourt.gov/oral_arguments/argument_transcript.aspx",
        credit="Supreme Court of the United States", home="https://www.supremecourt.gov/oral_arguments/",
        reader="read_scotus",
        notes="The official PDF transcripts (read with pdftotext); the whole transcript is also saved as plain text."),
    Source(
        key="hearings", name="US Congress committee hearings (GovInfo, CHRG)",
        licence="Public domain (US government work, 17 U.S.C. 105)", licence_class=OPEN,
        licence_url="https://www.govinfo.gov/about/policies", credit="US Government Publishing Office, GovInfo",
        home="https://www.govinfo.gov/app/collection/chrg", reader="read_hearings",
        notes="Packages found through GovInfo's own sitemaps (which its robots.txt lists); witnesses' prepared "
              "statements are part of the record too."),
    Source(
        key="fedreg", name="Federal Register public meeting notices", licence="Public domain (US government work)",
        licence_class=OPEN, licence_url="https://www.federalregister.gov/reader-aids/developer-resources",
        credit="Office of the Federal Register, National Archives", home="https://www.federalregister.gov/",
        reader="read_fedreg", notes="The free official API (no key); each notice's own summary is the answer."),
    Source(
        key="hansard", name="Canada House of Commons debates (Hansard)",
        licence="Reproduction permitted if accurate and not presented as official, but not for commercial purposes "
                "(House of Commons important notices)",
        licence_class=PERSONAL, licence_url="https://www.ourcommons.ca/en/important-notices",
        credit="House of Commons of Canada, Debates (Hansard)", home="https://www.ourcommons.ca/en/parliamentary-business",
        reader="read_hansard",
        notes="The official English XML of each sitting. Canadian English spelling and Canadian parliamentary "
              "procedure; every instruction says so."),
    Source(
        key="edgar", name="SEC EDGAR business writing (press releases, letters to the SEC, shareholder letters)",
        licence="Public records filed with the SEC (US government database; the companies' own writing is public "
                "record and freely reused)", licence_class=OPEN,
        licence_url="https://www.sec.gov/privacy#dissemination", credit="Companies' filings on SEC EDGAR",
        home="https://www.sec.gov/edgar", reader="read_edgar",
        notes="Uses EDGAR full-text search and the filing archive, paced well under EDGAR's 10 requests a second. "
              "EDGAR requires each program to give a contact name and email in its user agent: the kit takes it "
              "from the computer setting SEC_USER_AGENT and skips EDGAR without it."),
    Source(
        key="abcd", name="ABCD: Action-Based Conversations Dataset (ASAPP)", licence="MIT License",
        licence_class=OPEN, licence_url="https://github.com/asappresearch/abcd/blob/master/LICENSE",
        credit="ASAPP Research (Chen et al., 2021)", home="https://github.com/asappresearch/abcd",
        reader="read_abcd", notes="Customer service chats between people playing an agent and a customer."),
    Source(
        key="openstax_business", name="OpenStax business books (communication, management and ethics chapters)",
        licence="CC BY 4.0", licence_class=OPEN, licence_url="https://creativecommons.org/licenses/by/4.0/",
        credit="OpenStax, Rice University: Introduction to Business 2e, Business Ethics, Principles of Management, "
               "Organizational Behavior", home="https://openstax.org/subjects/business",
        reader="read_openstax_business",
        notes="Sections whose titles are about communication, meetings, negotiation, writing, teams and the like, "
              "from OpenStax's own GitHub repositories."),
    Source(
        key="oanc", name="Open American National Corpus (OANC)",
        licence="Free for any use, including commercial, without restriction (American National Corpus project)",
        licence_class=OPEN, licence_url="https://anc.org/data/oanc/",
        credit="American National Corpus project (Nancy Ide and colleagues), Open ANC",
        home="https://anc.org/data/oanc/", reader="read_oanc",
        notes="The official download (330 MB) is a GitHub release file, which GitHub's robots.txt closes to "
              "programs ('Disallow: /*/*/download/*'), so the owner downloads it once in a browser from "
              "anc.org/data/oanc/download/ and gives it with --oanc-file. Telephone conversations (its free part of Switchboard) and "
              "face-to-face conversations are kept as transcripts and chats; fundraising letters, Slate articles, "
              "government reports and travel guides become writing pairs."),
    Source(
        key="wikinews", name="English Wikinews", licence="CC BY 2.5", licence_class=OPEN,
        licence_url="https://creativecommons.org/licenses/by/2.5/", credit="Wikinews contributors",
        home="https://en.wikinews.org/", reader="read_wikinews",
        notes="News articles from the official dump (pages-articles, which Wikimedia offers all month)."),
    Source(
        key="nsf", name="NSF award abstracts", licence="Public domain (US government work)", licence_class=OPEN,
        licence_url="https://www.nsf.gov/policies/site-policies", credit="US National Science Foundation",
        home="https://www.research.gov/common/webapi/awardapisearch-v1.htm", reader="read_nsf",
        notes="Project summaries of funded grants, from NSF's free award API (no key)."),
    Source(
        key="presidential", name="Compilation of Presidential Documents (GovInfo)",
        licence="Public domain (US government work)", licence_class=OPEN,
        licence_url="https://www.govinfo.gov/about/policies", credit="Office of the Federal Register, GovInfo",
        home="https://www.govinfo.gov/app/collection/cpd", reader="read_presidential",
        notes="Remarks, speeches, statements and letters, found through GovInfo's sitemaps; whole texts saved too."),
    Source(
        key="blogs", name="Open-licence blogs and citizen news (Pluralistic, Global Voices)",
        licence="CC BY 4.0 (Pluralistic) and CC BY 3.0 (Global Voices)", licence_class=OPEN,
        licence_url="https://creativecommons.org/licenses/by/4.0/",
        credit="Cory Doctorow, Pluralistic (pluralistic.net); Global Voices authors (globalvoices.org)",
        home="https://pluralistic.net/", reader="read_blog_feeds",
        notes="The full posts in each site's own feed (Global Voices asks for 10 seconds between requests)."),
    Source(
        key="fineweb", name="FineWeb sample: conversational web pages (Hugging Face)",
        licence="ODC-By 1.0 for the collection; each page keeps its own copyright", licence_class=PERSONAL,
        licence_url="https://opendatacommons.org/licenses/by/1-0/", credit="Hugging Face, FineWeb (sample-10BT)",
        home="https://huggingface.co/datasets/HuggingFaceFW/fineweb", reader="read_fineweb",
        notes="A modest sample read through the official dataset viewer interface: only pages whose address "
              "suggests a forum, review or questions page."),
    Source(
        key="idl", name="UCSF Industry Documents Library: company emails released in litigation (2010 on)",
        licence="Made public by court order and settlements; UCSF offers them for research, teaching and other fair "
                "use; the companies' writers keep their copyright", licence_class=PERSONAL,
        licence_url="https://www.industrydocuments.ucsf.edu/help/copyright/",
        credit="UCSF Industry Documents Library (Opioids, Drug, Food, Chemical, Fossil Fuel and Tobacco collections)",
        home="https://www.industrydocuments.ucsf.edu/", reader="read_idl",
        notes="About 3.8 million public opioid-industry emails alone (2000s to 2020s); the kit reads the newest "
              "public emails from 2010 on in each industry through the library's search interface (Solr), which "
              "gives each document's text, and the attachments listed with each email. Its download server refused "
              "this kit, so PDFs are not fetched; the text comes from the search interface."),
    Source(
        key="doj_google", name="US v. Google (2023 search trial) exhibits that are emails (Department of Justice)",
        licence="Published by the US Department of Justice as trial exhibits; the emails' writers (Google, Apple, "
                "Samsung and others) keep their copyright", licence_class=PERSONAL,
        licence_url="https://www.justice.gov/atr/us-and-plaintiff-states-v-google-llc-2020-trial-exhibits",
        credit="US Department of Justice, Antitrust Division", home=
        "https://www.justice.gov/atr/us-and-plaintiff-states-v-google-llc-2020-trial-exhibits",
        reader="read_doj_google",
        notes="About 2,000 exhibit PDFs (mostly 2010s to 2020s); only those that are emails are used, read with "
              "pdftotext; each PDF is saved beside its email."),
    Source(
        key="gutenberg_creative", name="Public-domain fiction, poetry, plays and humour (Project Gutenberg)",
        licence="Public domain in the United States", licence_class=OPEN,
        licence_url="https://www.gutenberg.org/policy/license.html",
        credit="Project Gutenberg volunteers (https://www.gutenberg.org/)", home="https://www.gutenberg.org/",
        reader="read_gutenberg_creative",
        notes="Books found in Gutenberg's catalogue by subject (short stories, fiction, juvenile fiction and fairy "
              "tales, poetry, drama, humour), from the official mirror; labelled fiction_prose, children_story, "
              "poetry, screenplay_drama or humour."),
    Source(
        key="doctorow", name="Cory Doctorow's Creative Commons novels",
        licence="CC BY-NC-SA (each book states its version)", licence_class=PERSONAL,
        licence_url="https://creativecommons.org/licenses/by-nc-sa/3.0/", credit="Cory Doctorow (craphound.com)",
        home="https://craphound.com/", reader="read_doctorow",
        notes="The plain-text editions on his site's download pages; a book whose file does not state a Creative "
              "Commons licence is skipped. Non-commercial, so personal use only."),
    Source(
        key="scanned_federal",
        name="Scanned US federal email releases, read with OCR (Internet Archive copies)",
        licence="Public domain: works of the US federal government (17 U.S.C. 105), marked public domain on the "
                "Internet Archive; messages written from outside the federal government keep their writers' "
                "copyright and are marked personal use only, one by one",
        licence_class=OPEN, licence_url="https://creativecommons.org/publicdomain/mark/1.0/",
        credit="US Department of State, Department of Homeland Security, National Institutes of Health and "
               "Environmental Protection Agency FOIA releases; copies kept by the National Security Archive, The "
               "Memory Hole and others on the Internet Archive",
        home="https://archive.org/details/ClintonEmails10-21", reader="read_ia_federal",
        notes="Scanned pages of printed emails: the Clinton State Department emails (the 21 October 2016 release, "
              "one PDF per email, and the 31 August 2015 release), a DHS FOIA release, the NIH FOIA emails of "
              "April 2022 and the EPA Flint water documents (May 2016). The official State Department reading room "
              "(foia.state.gov) closes its robots.txt to all programs, so the Internet Archive copies are used; "
              "each item's metadata is read at every build and an item not marked public domain is skipped. The "
              "pages are read with OCR on this computer (ocr.py); only pages with a good confidence score are "
              "kept. Each message's page pictures and OCR text are saved beside it. Messages whose sender's "
              "address is outside the federal government (a company, a private address, a state office) are "
              "personal use only and need --personal. The Internet Archive's terms offer its collections for "
              "scholarship and research."),
    Source(
        key="scanned_state",
        name="Scanned state government email releases, read with OCR (Internet Archive copies)",
        licence="State government records released under state public-records laws; not federal works, and no "
                "licence is given, so personal use only",
        licence_class=PERSONAL, licence_url="https://archive.org/details/palinemails",
        credit="State of Alaska (Sarah Palin's governor emails, scanned by the Anchorage Daily News) and State of "
               "Michigan (Governor Rick Snyder's Flint emails); copies on the Internet Archive",
        home="https://archive.org/details/palinemails", reader="read_ia_state",
        notes="Sarah Palin's Alaska emails (released 10 June 2011) and Governor Snyder's Flint water emails "
              "(January 2016), from their Internet Archive copies; michigan.gov refuses programs (it answers "
              "'Access Denied' even for its robots.txt), so its own PDFs are not used. Read with OCR like the "
              "federal releases."),
    Source(
        key="govinfo_exhibits",
        name="Scanned email exhibits in US Congress hearing records (GovInfo), read with OCR",
        licence="Public domain: works of the US government (GovInfo); exhibits from outside the government keep "
                "their writers' copyright and are marked personal use only, one by one",
        licence_class=OPEN, licence_url="https://www.govinfo.gov/about/policies",
        credit="US Government Publishing Office, GovInfo (Congressional Hearings collection)",
        home="https://www.govinfo.gov/app/collection/chrg", reader="read_govinfo_exhibits",
        notes="Hearing records print submitted documents as scanned pictures ('[GRAPHICS NOT AVAILABLE IN TIFF "
              "FORMAT]' in their text). The kit reads only the hearings whose text shows such pictures next to the "
              "word email, downloads the official PDF, and reads only its picture pages with OCR."),
]

# Used only with --scanned-folder: PDFs the owner downloaded himself. Each PDF is personal use only unless it is a
# US federal government work (readers_scanned.government_reason); each row says which.
SCANNED_FOLDER = Source(
    key="scanned_folder", name="Scanned PDFs from your own folder (--scanned-folder), read with OCR",
    licence="Your own downloads: personal use only, except US federal government works (public domain), which are "
            "marked open one by one", licence_class=PERSONAL, licence_url="",
    credit="The releases you downloaded (see each example's source file in the messages folder)", home="",
    reader="read_scanned_folder",
    notes="A PDF counts as a government work when its folder or file name says 'public domain', 'government work', "
          "'US government' or 'federal', or when its first pages carry a US federal release stamp or FOIA "
          "exemption codes such as (b)(6).")

NOT_USED = [
    ("Hillary Clinton emails on the State Department's own site (foia.state.gov)",
     "The robots.txt of foia.state.gov says 'User-agent: * / Disallow: /' (no programs at all). The same releases "
     "are read from their Internet Archive copies, marked public domain (source scanned_federal); the copies on "
     "WikiLeaks and news sites are not used."),
    ("Jeb Bush's Florida governor emails (jebemails.com, 2015, and the Internet Archive item JebBushEmails)",
     "The original release site is gone: jebemails.com now belongs to an unrelated email-marketing business. The "
     "only copy found on the Internet Archive (JebBushEmails, a 400 MB 7z file of text, not scanned pages) was "
     "uploaded anonymously with no description of its origin and no licence, and the 2015 release exposed "
     "thousands of Floridians' Social Security numbers and private details before they were redacted, so an "
     "unreviewed copy is not used. No official source remains. If you download a reviewed copy yourself, "
     "--scanned-folder can read its PDFs."),
    ("Sarah Palin's Alaska emails on DocumentCloud and its Internet Archive mirror",
     "DocumentCloud's robots.txt reserves AI training ('ai-train=no'), so its copy and the Internet Archive "
     "mirrors of DocumentCloud documents (collection 'documentcloud') are left out. The Anchorage Daily News scans "
     "on the Internet Archive (item palinemails) are used instead (source scanned_state)."),
    ("Michigan's own Flint email pages (michigan.gov)",
     "www.michigan.gov answers 'Access Denied' to programs, even for its robots.txt, so the site is treated as "
     "closed. Governor Snyder's Flint emails are read from their Internet Archive copies (source scanned_state) "
     "and the EPA's Flint documents from theirs (source scanned_federal). The searchable copy at the University of "
     "Iowa is a research archive, not an official download, and was not used."),
    ("US National Archives email records (catalog.archives.gov)",
     "The robots.txt of catalog.archives.gov says 'Disallow: /' for all programs; its API needs a personal key, and "
     "the email records there are mostly scanned PDFs. Not used."),
    ("MuckRock released documents (muckrock.com)",
     "Many are public-domain government records, but MuckRock's robots.txt says 'Content-Signal: search=yes, "
     "ai-train=no, use=reference' and blocks AI crawlers (GPTBot, ClaudeBot, CCBot and others): an express "
     "reservation against AI training. Not used."),
    ("Apache Software Foundation mailing lists (lists.apache.org, mail-archives.apache.org)",
     "The robots.txt of mail-archives.apache.org closes the whole site to all programs and says bot operators must "
     "contact the ASF to be allowed; mailing list posts have no public licence. Not used."),
    ("IETF mailing lists (mailarchive.ietf.org, www.ietf.org/mail-archive)",
     "Under the IETF's rules (BCP 78, the 'Note Well') posts are Contributions licensed to the IETF Trust, not to "
     "the public; robots.txt closes the bulk export (/arch/export/), the old text archive address now leads to the "
     "home page, and the anonymous IMAP access is not a web address this kit can use. Not used."),
    ("Linux kernel mailing lists (lore.kernel.org)",
     "Its robots.txt closes the whole site to every program ('User-agent: * / Disallow: /') and names AI crawlers "
     "(GPTBot, ClaudeBot, CCBot, Google-Extended and many more) separately. Not used."),
    ("Stack Exchange data dump",
     "The posts are CC BY-SA, but since 2024 the official dump needs a login and terms that forbid using it to "
     "train AI models; the archive.org copies of newer dumps are community re-uploads, not official, and Stack "
     "Exchange's API terms likewise restrict AI training. Comments and posts are therefore not used."),
    ("DailyDialog",
     "CC BY-NC-SA 4.0 (would be personal use), but its official download (yanran.li) answers 'Service "
     "Unavailable' and the Hugging Face copy is only a loading script pointing there; unofficial copies are not "
     "used."),
    ("PersonaChat (ConvAI2)",
     "The MIT licence on ParlAI covers its program code; the conversations themselves have no stated licence from "
     "their publisher, and the Hugging Face copies are unofficial with 'unknown' licences. Synthetic-Persona-Chat "
     "is machine-written. Not used."),
    ("CoQA",
     "Its passages carry several different licences (some for research only), and its answers are short "
     "question-answering, not conversation. Not used."),
    ("Switchboard and CALLHOME transcripts",
     "Licensed by the Linguistic Data Consortium (LDC) to members and buyers only; not freely downloadable. Not "
     "used."),
    ("Wikisource letters and the Kiwix copies of Gutenberg",
     "Wikisource's letters are mostly the same public-domain books as Project Gutenberg's, which the kit reads "
     "from Gutenberg's official mirror; the Kiwix ZIM copies are whole libraries of many gigabytes, so they were "
     "not needed."),
    ("Open-licence forum archives",
     "No forum was found that offers an official bulk download under an open licence other than Wikipedia's talk "
     "pages (used) and Stack Exchange (terms forbid AI training). Not used."),
    ("City council minutes and meeting transcripts",
     "Each city publishes its own, on its own site and terms, mostly as PDF minutes rather than transcripts, and "
     "whether they are public domain depends on the state. No single official bulk source was found; the Council "
     "Data Project's transcripts are machine-made speech recognition. Not used for now."),
    ("stindardlogic/email-writing-sft-100k (Hugging Face, Apache 2.0)",
     "Machine-written ('synthetic') emails whose card does not say how or with which model they were made. "
     "Machine-written emails would teach the model a machine's style, so it was left out."),
    ("wardacoder/business-email-dataset (Hugging Face, MIT)",
     "Machine-written by GPT-4o-mini (OpenAI's terms limit using its output to train other models). Left out."),
    ("Isotonic/marketing_email_samples and other small email sets on Hugging Face",
     "Non-commercial (CC BY-NC) or no licence at all, marketing or spam emails, or Enron copies of unknown "
     "preparation. The official Enron file is used instead (personal use only)."),
    ("HuggingFaceH4/no_robots",
     "Human-written and good, but CC BY-NC 4.0 (non-commercial); kept out so the default build stays open or "
     "share-alike."),
    ("Legistar (webapi.legistar.com) city and county councils: Seattle, Boston, Denver, Oakland and others",
     "The Web API has no robots.txt and needs no key, but it gives only agenda item titles, actions and votes; the "
     "minutes, agendas and video transcripts are files on legistar1.com, legistar2.granicus.com and Granicus "
     "hosts whose robots.txt says 'Disallow: /' to all programs. Not used."),
    ("Granicus video transcripts and CivicPlus AgendaCenter and BoardDocs sites (including school boards)",
     "Each council or school district has its own site and terms; the files are PDFs on hosts that are either "
     "closed to programs (Granicus) or have no bulk download, and no licence beyond each body's own. Not used."),
    ("Council Data Project (Seattle, Portland, Boston, Denver, Oakland and other instances)",
     "The project's software is open source, but its transcripts are machine speech recognition (not people's own "
     "writing) and no licence for the data is stated. Not used."),
    ("DocumentCloud public documents",
     "DocumentCloud's robots.txt says 'Content-Signal: search=yes, ai-train=no, use=reference' and blocks AI "
     "crawlers. Not used."),
    ("OpenStates (state legislatures)",
     "Its API needs a key (it would go in the computer's settings, never in the files), but it carries bills, "
     "votes and events, not hearing transcripts or committee minutes. Not used."),
    ("FCC ECFS public comments, FERC eLibrary and NTSB public hearings",
     "ECFS needs an api.data.gov key and most comment text is inside attached files; FERC eLibrary holds formal "
     "filings rather than conversation; NTSB hearing transcripts are PDFs inside individual dockets with no bulk "
     "route. Not used in this round (the regulations.gov reader shows how a keyed comment source works)."),
    ("CRTC public process submissions (crtc.gc.ca)",
     "Its robots.txt says 'Content-Signal: search=yes, ai-train=no, use=reference' and blocks AI crawlers. Not used."),
    ("Ontario Hansard (ola.org)",
     "The site answers 'Access Denied' to programs, even for robots.txt, so it is treated as closed. Not used."),
    ("Senate of Canada debates, and the British Columbia, Alberta and Nova Scotia Hansards",
     "Their robots.txt files allow programs (Nova Scotia asks for 10 seconds between requests), but their "
     "reproduction terms are each legislature's own (none uses the Open Government Licence) and they were not "
     "built in this round; the House of Commons reader shows the pattern. Not used yet."),
    ("Toronto (TMMIS) and other Canadian city council minutes (Vancouver, Ottawa, Calgary, Edmonton, Winnipeg, "
     "Halifax)",
     "Toronto's open data under its Open Government Licence has only meeting statistics, votes and attendance, not "
     "minutes; the minutes system (secure.toronto.ca) refuses programs. The other cities publish minutes as PDFs on "
     "their own sites, not as open data. Not used."),
    ("MuckRock released documents (again, for meeting records)",
     "Still 'ai-train=no' in its robots.txt. Not used."),
    ("Avocado Research Email Collection",
     "Real business email from a defunct company, but licensed by the Linguistic Data Consortium to members only. "
     "Not used."),
    ("Corporate emails in court and government records (FTC and SEC exhibits, congressional investigation "
     "document dumps)",
     "They are scanned exhibit PDFs inside individual dockets with no bulk route. Scanned exhibits printed in "
     "hearing records come in through the GovInfo exhibits source (read with OCR); any others you download "
     "yourself can be read with --scanned-folder."),
    ("TweetSumm (customer service on Twitter)",
     "CDLA-Sharing, but it publishes only tweet IDs and summaries; the tweets themselves come from a Kaggle copy that "
     "needs a login and Kaggle's terms. Not used."),
    ("Bitext customer support set (Hugging Face)",
     "CDLA-Sharing, but machine-generated by Bitext's own language generation; left out like the other "
     "machine-written sets."),
    ("Business Communication for Success, Business Writing for Everyone, BCcampus, Lumen and LibreTexts "
     "business communication books",
     "CC BY books that are already in the reference library (textbooks/); this kit reads the OpenStax business "
     "books directly. Reading the others here was not built in this round."),
    ("Small Business Administration guides, USAJOBS postings and federal HR letters",
     "Public domain, but SBA's guides are web pages without a bulk route and USAJOBS needs an API key plus an email "
     "address as the user agent (it would go in the computer's settings). Not built in this round."),
    ("Earnings call transcripts",
     "Not on EDGAR; the services that publish them (Seeking Alpha, Motley Fool and others) are copyrighted. Not used."),
    ("plainlanguage.gov examples, agency press releases, SSA, IRS and VA sample letters, State Department "
     "statements, military writing guides, GAO and CRS reports",
     "Public domain, but spread over many agency web pages without bulk routes (several guides and reports are "
     "already in the reference library); not built in this round. The Federal Register, presidential documents, "
     "hearings and EDGAR sources cover formal American writing."),
    ("CourtListener bulk data and Supreme Court opinions",
     "Court opinions are public domain, but courtlistener.com refused this kit's requests (403), its API needs a "
     "token and its bulk files are many gigabytes; Supreme Court opinions were not built in this round (its oral "
     "arguments are used)."),
    ("Wikipedia featured articles",
     "CC BY-SA, but they need the full English Wikipedia dump (over 20 GB) or page-by-page requests; not built in "
     "this round."),
    ("The Conversation and NPR transcripts",
     "Their robots.txt files block AI-training crawlers (GPTBot, ClaudeBot, CCBot, Google-Extended and others). "
     "Not used."),
    ("KFF Health News and ProPublica",
     "CC BY-NC-ND (personal use, whole and unchanged); their feeds are open to programs, but they were not built in "
     "this round."),
    ("NASA and other US government podcasts, Public Radio Exchange",
     "NASA transcripts are public domain but are separate web pages without a bulk route; PRX content is each "
     "producer's own. Not built in this round."),
    ("YouTube automatic captions",
     "YouTube's terms forbid automated downloading. Not used."),
    ("Common Crawl and C4",
     "Huge; the FineWeb sample (taken from Common Crawl and filtered) stands in for them. Not used separately."),
    ("Amazon Reviews 2023 (McAuley Lab)",
     "Its Hugging Face page states no licence, and the reviews belong to their writers and Amazon; it is offered "
     "for research. Not used."),
    ("Congressional investigation exhibits on congress.gov",
     "congress.gov's robots.txt blocks AI-training crawlers (GPTBot, ClaudeBot, CCBot, Google-Extended and others). "
     "Not used."),
    ("House Oversight, Senate Commerce and PSI, House Judiciary (2020 tech antitrust), Boeing 737 MAX and January 6 "
     "committee document releases",
     "Committee sites allow programs (oversight.house.gov's robots.txt allows all), but each release is a "
     "separate PDF on a separate page with no list a program can follow; not built in this round. Download the "
     "ones you want and use --scanned-folder (they are marked government works when their pages carry federal "
     "stamps or the folder name says so). Hearing records on GovInfo are read by the GovInfo exhibits source."),
    ("FTC v. Meta, Epic v. Apple, Oracle v. Google, Waymo v. Uber and Theranos trial exhibits",
     "Published as PDFs on court and agency pages or on CourtListener, which refused this kit (403) and whose API "
     "needs a token; not built in this round. US v. Google's DOJ exhibits are used."),
    ("FBI Vault and agency FOIA reading rooms (DHS, HHS, EPA) on the agencies' own sites, and congressional "
     "releases about Hunter Biden",
     "Federal records released as scanned PDF pages one release at a time, with no list a program can follow. "
     "Several releases (DHS, NIH, EPA Flint) are read from their public-domain Internet Archive copies (source "
     "scanned_federal); others can be downloaded by hand and read with --scanned-folder. The FBI's Clinton "
     "investigation files on the Internet Archive are interview reports, not emails, and were not used."),
    ("State Department FOIA reading room (again)",
     "robots.txt still closes foia.state.gov to all programs. Not used."),
    ("Climate Investigations Center",
     "Its robots.txt allows programs, but its documents are PDFs that mostly come from the Industry Documents "
     "Library's fossil fuel collection, which the kit reads directly."),
    ("Archive of Our Own (AO3)",
     "Its terms forbid scraping and AI training, its robots.txt blocks AI crawlers (GPTBot, CCBot), and its authors "
     "have objected. Excluded."),
    ("FanFiction.Net", "Its robots.txt says 'Content-Signal: ai-train=no'. Excluded."),
    ("Wattpad", "Its robots.txt blocks AI-training crawlers (GPTBot), and its terms forbid scraping. Excluded."),
    ("Openly licensed fan fiction",
     "No collection of fan works released under an open licence with a bulk download was found (single works on "
     "the Internet Archive carry mixed or no licences, and fan works also depend on the original's copyright). "
     "Not used."),
    ("Reddit WritingPrompts (and the Hugging Face copies of it)",
     "Reddit's robots.txt closes the site to programs and its terms forbid AI training without an agreement; the "
     "dataset copies carry Reddit's terms. Excluded."),
    ("TinyStories and other machine-written story sets on Hugging Face",
     "Written by AI models; left out like the other machine-written sets."),
    ("Pluralistic's serialised fiction",
     "Published inside Pluralistic's posts under the same CC BY 4.0 licence, so it arrives with the blogs source "
     "rather than separately."),
    ("Free Culture fiction collections, Feedbooks originals, Smashwords and Lulu free books",
     "Licences differ book by book (many 'free' books are not openly licensed) and there is no bulk route with "
     "licence data; not built in this round. Doctorow's novels are used."),
    ("StoryWeaver and the Global Digital Library children's stories, Wikibooks creative writing",
     "CC BY and CC BY-SA, and StoryWeaver's robots.txt allows programs, but the children's stories are already in "
     "the reference library and were not re-read here; Wikibooks' creative writing books are guides rather than "
     "stories. Not built in this round."),
    ("Wikisource poetry, plays and fiction; the Library of Congress poetry collections; public-domain screenplays "
     "on the Internet Archive",
     "Mostly the same public-domain works as Project Gutenberg (which the kit reads), or scanned items without "
     "text and clear licence data. Not built in this round."),
]


def by_key():
    """{key: Source}."""
    return {s.key: s for s in SOURCES}
