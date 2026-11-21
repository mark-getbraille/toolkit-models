"""The sources of the Writing Kit: the ones it uses (SOURCES) and the ones that were checked and cannot be used
(NOT_USED), each with the reason. Every licence, robots.txt and terms page was checked by hand in November 2026; the
robots.txt is also read again by fetch.py every time the kit downloads anything.

Licence classes (the same words as the Picture Model Training Kit):
  open               may be used and shared for any purpose, with credit (public domain, CC0, CC BY, Apache, MIT);
  share-alike        may be used for any purpose with credit, but whatever is made from it and shared must carry the
                     same licence (CC BY-SA);
  personal use only  no licence lets others re-use the text; it is used only on the owner's own computer to train
                     the owner's own model, and neither the data nor the trained add-on is shared.
By default the builder uses only open and share-alike sources; --personal adds the personal-use ones.
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
              "once it has enough; it uses only each person's own sent mail, never attachments (the file has none). "
              "The emails were written by Enron employees, so they are not US government works; with no licence "
              "they are personal use only. Every message is scrubbed and most are dropped (see SCRUBBING.txt).",
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
              "'mboxes' downloads and the member-only archives, and the kit never reads them. Only the message "
              "text is used; attachments are never downloaded."),
]

NOT_USED = [
    ("Hillary Clinton emails, US State Department FOIA release (foia.state.gov)",
     "Public domain US government records, but the robots.txt of foia.state.gov says 'User-agent: * / Disallow: /' "
     "(no programs at all), and there is no other official bulk download; the copies elsewhere (WikiLeaks and news "
     "sites) are not official. The records are also scanned PDF pages, not text."),
    ("Jeb Bush's Florida governor emails (jebemails.com, 2015)",
     "The original release site is gone: jebemails.com now belongs to an unrelated email-marketing business. The "
     "2015 release also exposed thousands of Floridians' Social Security numbers and private details (they were "
     "redacted later). No official source remains."),
    ("Sarah Palin's Alaska governor emails (2011 state release)",
     "Alaska released them as about 24,000 printed pages; the only digital copies are scans made by news "
     "organisations, not an official bulk download, and they are images rather than text."),
    ("Other state public-records email releases (for example Michigan's Flint water emails)",
     "Michigan released the Flint emails in 2016 as PDF page images (about 445,000 pages in all), with residents' "
     "personal details in them and no bulk text download; the searchable copy at the University of Iowa is a "
     "research archive, not an official bulk download. Other states' releases looked at were the same kind of "
     "scanned pages. Not used."),
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
    ("IETF mailing lists (mailarchive.ietf.org)",
     "Under the IETF's rules (BCP 78, the 'Note Well') posts are Contributions licensed to the IETF Trust, not to "
     "the public, and robots.txt closes the bulk export (/arch/export/). The W3C lists give the same kind of "
     "technical-list mail, so the IETF lists were left out."),
    ("Stack Exchange data dump",
     "The posts are CC BY-SA, but since 2024 the official dump needs a login and terms that forbid using it to "
     "train AI models; the archive.org copies of newer dumps are community re-uploads, not official. Not used."),
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
]


def by_key():
    """{key: Source}."""
    return {s.key: s for s in SOURCES}
