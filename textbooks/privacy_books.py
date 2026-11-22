"""Privacy, security and digital safety for the reference library, in its own group "Reference, privacy, security and
digital safety" (the owner's request of 2026-11-22). Keys: privacy (every book), privacy-scams (scams, fraud and
reporting), privacy-ai (AI risk and safety), privacy:<name> (one book).

What this module builds, in plain words, each IN FULL (every page of the guide, or the whole PDF):
  Open (CC BY 4.0):
    - EFF's Surveillance Self-Defense, its glossary and playlists (the guides themselves are already in the library
      as nonprofit:eff_surveillance_self_defense, so they are not repeated);
    - the Tor Project's manual and support pages (Tor Browser, onion services, censorship), English only.
  Share-alike (CC BY-SA 4.0, or the GNU GPL; a book made from them keeps the licence):
    - Security in a Box (Front Line Defenders and Tactical Tech): passwords, two-factor, phones and computers,
      malware, safer browsing, secure chat and email, backups and destroying data;
    - Privacy Guides: threat modelling, the basics, and its tool recommendations;
    - OWASP's Cheat Sheet Series pages on sign-in, passwords, multi-factor, account recovery and privacy;
    - the GnuPG manual ("Using the GNU Privacy Guard", GPL 3 or later).
  US government works (public domain), with the licence line checked at every build:
    - CISA's Secure Our World pages (strong passwords, multi-factor, phishing, updates; and the business pages) and
      the #StopRansomware Guide;
    - NIST: the Cybersecurity Framework 2.0 and its small business quick-start guide, Small Business Information
      Security (NIST IR 7621), Digital Identity Guidelines (SP 800-63-4 and 800-63B-4: passwords, passkeys,
      authenticators), An Introduction to Information Security (SP 800-12), the AI Risk Management Framework (AI
      100-1) with its Playbook, the Generative AI Profile (AI 600-1) and the US AI Safety Institute's (now CAISI's)
      draft on managing misuse risk (AI 800-1);
    - the FTC's Identity Theft: A Recovery Plan (from the Internet Archive: ftc.gov refuses programs);
    - the FBI's Internet Crime Complaint Center (IC3) annual report and elder fraud report;
    - the Justice Department's Stop Elder Fraud pages (the National Elder Fraud Hotline, 1-833-372-8311);
    - the Department of Education's FERPA pages for parents and students;
    - the privacy rules themselves: HIPAA's privacy and security rules (45 CFR 164), FERPA's (34 CFR 99) and
      COPPA's (16 CFR 312), as law books (LAWS, built by the library's law builder).
  Other countries (each with its non-US notice):
    - the UK National Cyber Security Centre's advice for individuals and families (Open Government Licence v3.0);
    - the UK Data Protection Act 2018 and the UK GDPR from legislation.gov.uk (OGL);
    - Canada's PIPEDA from Justice Laws, and Get Cyber Safe, the Canadian Centre for Cyber Security's public
      awareness site (Government of Canada terms: personal use only);
    - the International Scientific Report on the Safety of Advanced AI (interim report, May 2024; GOV.UK, OGL).
Every book's notice ends with SAFETY: report scams (ReportFraud.ftc.gov, 7726, ic3.gov, the Elder Fraud Hotline).

Already in the library and not repeated: EFF Surveillance Self-Defense's guides (nonprofit:), the CFPB's fraud,
credit report and older Americans pages (money:cfpb_consumer_tools), the Fair Credit Reporting Act (law:
us_code_consumer_credit) and the US Code in full (code:), and Microsoft's and Apple's open documentation (techdocs).
Not built (NOT_INCLUDED, each with the reason and an address): FTC consumer pages and IdentityTheft.gov, the FCC's
consumer guides, HHS's HIPAA pages for individuals, csrc.nist.gov (its robots.txt shuts out AI readers; the PDFs are
read from nvlpubs.nist.gov), ENISA, EUR-Lex (the EU AI Act and GDPR), the OECD AI principles, the International AI
Safety Report 2025 and 2026, the UK AI Security Institute, and company help pages (Apple, Google, Microsoft, Meta,
AI companies): link-only.

Run from the repository's folder:
  python3 textbooks/privacy_books.py privacy:cisa_secure_our_world --out build/textbooks --limit 5
  python3 textbooks/privacy_books.py --list privacy
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "privacy"
GROUPS = {GROUP: "Reference, privacy, security and digital safety"}

# The notice every book ends with (the picture packs say the same in packs/synthetic_scams_packs.py).
SAFETY = ("Staying safe: never give passwords, codes or payment to someone who contacts you; check with the company "
          "yourself, using a number or website you already know. Report scams to the FTC at ReportFraud.ftc.gov, "
          "forward scam texts to 7726 (SPAM), report internet crime to the FBI at ic3.gov, and if the person "
          "targeted is 60 or older, call the National Elder Fraud Hotline: 1-833-372-8311.")
NOT_LEGAL = "General information, not legal advice; laws differ by country and state and change."

CC_BY = "CC BY 4.0"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"
CC_BY_SA = "CC BY-SA 4.0"
CC_BY_SA_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
GPL3 = "GPL-3.0-or-later"                  # the same name as at_docs.GPL3 (allowed there as share-alike)
GPL3_URL = "https://www.gnu.org/licenses/gpl-3.0.html"
OGL_UK = "OGL-UK-3.0"
OGL_UK_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"


def page_list_book(name, title, subject, publisher, urls, pages, description, notice, units=(), **more):
    """A US government web guide of a fixed list of pages (no crawl beyond them): the first address is its source."""
    return K.us_web(GROUP, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=f"{notice} {SAFETY}", crawl=[(urls[0], 0)], urls=list(urls),
                    pages=pages, unit_rules=list(units), limit=len(urls) + 5, **more)


def open_guide(name, title, subject, publisher, country, licence, licence_url, licence_page, licence_text, start,
               pages, description, notice, depth=1, follow=None, units=(), limit=300, **more):
    """A web guide under an open licence (not a US government work), read by crawling from start, its licence line
    checked on licence_page at every build."""
    starts = [start] if isinstance(start, str) else list(start)
    return dict(K.WEB, group=GROUP, name=name, title=title, subject=subject, publisher=publisher, country=country,
                licence=licence, licence_url=licence_url, licence_page=licence_page, licence_text=licence_text,
                source=starts[0], description=description, notice=f"{notice} {SAFETY}",
                crawl=[(s.rstrip("/"), depth) for s in starts], follow=follow, pages=pages, unit_rules=list(units),
                limit=limit, **more)


# ====================================================================== open guides (CC BY)

GUIDES = [
    open_guide("eff_ssd_glossary_playlists", "Surveillance Self-Defense: glossary and playlists (EFF)",
               "Digital security words and plans", "Electronic Frontier Foundation (EFF)", "International", CC_BY,
               CC_BY_URL, "https://www.eff.org/copyright", r"Creative Commons Attribution 4\.0 International License",
               ["https://ssd.eff.org/glossary", "https://ssd.eff.org/"],
               r"^https://ssd\.eff\.org/(glossary|playlist)/[a-z0-9-]+$",
               "The rest of EFF's Surveillance Self-Defense: its glossary (every term, such as encryption, "
               "end-to-end encryption, metadata, phishing, threat model, two-factor authentication and VPN, explained "
               "in plain words) and its playlists, the reading orders for people in different situations (a security "
               "starter pack, the privacy breakdown of mobile phones, activists, journalists, students, LGBTQ youth, "
               "reproductive healthcare). The guides themselves are in the library as Surveillance Self-Defense.",
               "Surveillance Self-Defense by the Electronic Frontier Foundation (ssd.eff.org), licensed under CC BY "
               "4.0; EFF says its statements about law may be accurate in one place only and may have changed.",
               content=(r'id="main-content"[^>]*>', r"<footer"),
               drop=K.DROP + [r'<p class="breadcrumbs".*?</p>'],
               units=[(r"/playlist/", "Playlists"), (r"/glossary/", "Glossary")], limit=400),
    open_guide("tor_manual", "Tor Browser and Tor: the manual (Tor Project)", "Anonymous browsing (Tor)",
               "The Tor Project, Inc.", "International", CC_BY, CC_BY_URL,
               "https://www.torproject.org/about/trademark/",
               r"Creative Commons Attribution 4\.0 International License", "https://tb-manual.torproject.org/",
               r"^https://tb-manual\.torproject\.org/(?!(ar|de|es|fa|fr|ga|hu|id|it|ja|ka|ko|pl|pt-BR|ro|ru|sv|th|tr|"
               r"uk|zh-CN|zh-TW|static|fonts)/)[a-z0-9-]+(/[a-z0-9-]+)*/?$",
               "The Tor Project's manual, every English page: what Tor is and how it protects your privacy, "
               "downloading and installing Tor Browser, running it for the first time, circumvention and bridges "
               "where Tor is blocked, managing identities, onion services, security settings, updating, "
               "troubleshooting and uninstalling, Tor on Android, relays, and the glossary.",
               "From the Tor Project (tb-manual.torproject.org): \"copyrightable content ... is licensed under a "
               "Creative Commons Attribution 4.0 International License\"; \"Tor\" and the onion logo are the Tor "
               "Project's trademarks and this copy is not endorsed by it. Download Tor Browser only from "
               "torproject.org.", depth=2,
               follow=r"^https://tb-manual\.torproject\.org/[a-z0-9-]+/$",
               units=[(r"/tor-browser/|/about/|/downloading|/installation|/running", "Tor Browser"),
                      (r"/anti-censorship/|/circumvention|/bridges", "Censorship and bridges"),
                      (r"/onion-services|/relays/|/little-t-tor/", "Onion services and relays"),
                      (r".", "More")], limit=300),
]

# ====================================================================== share-alike guides

GUIDES += [
    open_guide("security_in_a_box", "Security in a Box: digital security tools and tactics", "Digital security "
               "(practical guides)", "Front Line Defenders and Tactical Tech", "International", CC_BY_SA,
               CC_BY_SA_URL, "https://securityinabox.org/en/",
               r"Creative Commons Attribution-ShareAlike 4\.0 International", "https://securityinabox.org/en/",
               r"^https://securityinabox\.org/en/(?!blog/|data-use-policy|disclaimer)[a-z0-9-]+/[a-z0-9-]+/?$",
               "Security in a Box, every English guide: assessing risks and planning (physical security, private "
               "communication, multiple identities, safer travel), passwords, password managers and two-factor "
               "authentication, protecting Android, iPhone, Windows, Mac and Linux devices, malware, safer browsing, "
               "anonymity and getting round censorship, secure chat and email, social media, recovering from account "
               "compromise, backups, secure file storage and destroying sensitive information, with its tool "
               "guides.", "Security in a Box by Front Line Defenders and Tactical Tech (securityinabox.org), "
               "licensed under CC BY-SA 4.0: a book made from it keeps that licence.",
               units=[(r"/assess-plan/", "Assess and plan"), (r"/passwords/", "Passwords and accounts"),
                      (r"/phones-and-computers/", "Phones and computers"),
                      (r"/internet-connection/", "Internet connection"), (r"/communication/", "Communication"),
                      (r"/files/", "Files and backups"), (r".", "About")], limit=200),
    open_guide("privacy_guides", "Privacy Guides: protecting your data and privacy", "Privacy (practical guides)",
               "Privacy Guides (non-profit) and its contributors", "International", CC_BY_SA, CC_BY_SA_URL,
               "https://www.privacyguides.org/en/about/notices/",
               r"Creative Commons Attribution-ShareAlike 4\.0 International", "https://www.privacyguides.org/en/",
               r"^https://www\.privacyguides\.org/en/(?!(articles|news|videos|about|meta|assets)/)[a-z0-9-]+"
               r"(/[a-z0-9-]+)*/$",
               "Privacy Guides, every English guide page: threat modelling, common threats and misconceptions, "
               "account creation and deletion, passwords and multi-factor authentication, email and VPN overviews, "
               "Android, iOS, Windows, macOS and Linux privacy, and its recommendations of privacy tools (browsers, "
               "password managers, encrypted messengers and email, VPNs, encryption software, DNS, search engines) "
               "with the criteria it uses.",
               "Privacy Guides (privacyguides.org) content is licensed under CC BY-SA 4.0: a book made from it keeps "
               "that licence; this copy does not suggest Privacy Guides endorses it. Its recommendations name "
               "products; prices and features change.", depth=2,
               follow=r"^https://www\.privacyguides\.org/en/(basics|os|advanced|tools)?/?$",
               units=[(r"/basics/", "The basics"), (r"/os/", "Operating systems"), (r"/advanced/", "Advanced"),
                      (r".", "Tools")], limit=250),
]

OWASP = "https://cheatsheetseries.owasp.org/cheatsheets/"
OWASP_SHEETS = ["Authentication", "Password_Storage", "Multifactor_Authentication", "Forgot_Password",
                "Credential_Stuffing_Prevention", "Session_Management", "Transport_Layer_Security",
                "User_Privacy_Protection", "Choosing_and_Using_Security_Questions", "LLM_Prompt_Injection_Prevention"]
GUIDES.append(dict(open_guide(
    "owasp_cheat_sheets", "OWASP Cheat Sheets: sign-in, passwords, multi-factor and privacy",
    "Account security (for website builders)", "OWASP Foundation (Cheat Sheet Series Team)", "International",
    CC_BY_SA, CC_BY_SA_URL, OWASP + "Authentication_Cheat_Sheet.html",
    r"Creative Commons Attribution-ShareAlike 4\.0 International", OWASP + "Authentication_Cheat_Sheet.html",
    r"^https://cheatsheetseries\.owasp\.org/cheatsheets/[A-Za-z_]+_Cheat_Sheet\.html$",
    "The OWASP Cheat Sheet Series pages on keeping accounts safe, written for people who build websites but "
    "useful to anyone who wants to know what a good sign-in looks like: authentication, storing passwords, "
    "multi-factor authentication, forgotten-password and recovery flows, credential stuffing, sessions, secure "
    "connections (TLS), protecting users' privacy, security questions, and preventing prompt injection in AI "
    "assistants.", "From the OWASP Cheat Sheet Series (cheatsheetseries.owasp.org), licensed under CC BY-SA 4.0: a "
    "book made from it keeps that licence.", depth=0),
    crawl=[(OWASP + s + "_Cheat_Sheet.html", 0) for s in OWASP_SHEETS],
    urls=[OWASP + s + "_Cheat_Sheet.html" for s in OWASP_SHEETS], limit=len(OWASP_SHEETS) + 2))

GNUPG = "https://www.gnupg.org/documentation/manuals/gnupg/"
GUIDES.append(open_guide(
    "gnupg_manual", "Using the GNU Privacy Guard (the GnuPG manual)", "Email and file encryption (GnuPG)",
    "The GnuPG project (g10 Code GmbH, Werner Koch and the Free Software Foundation)", "International", GPL3,
    GPL3_URL, GNUPG, r"under the terms of the GNU General Public License as published by the Free Software "
                     r"Foundation; either version 3", GNUPG + "index.html",
    r"^https://www\.gnupg\.org/documentation/manuals/gnupg/[A-Za-z0-9_.-]+\.html$",
    "The GnuPG manual, every page: what GnuPG is, invoking gpg and its commands and options for encrypting, "
    "signing and checking files and email, managing keys and trust, the agent and smart cards, S/MIME (gpgsm), "
    "configuration files and helper tools.",
    "The GNU Privacy Guard manual, licensed under the GNU General Public License version 3 or later (the licence "
    "text is its \"Copying\" chapter): a book made from it keeps that licence. GnuPG is a command-line program; "
    "most people use it through an email or file-encryption app.", depth=3,
    follow=r"^https://www\.gnupg\.org/documentation/manuals/gnupg/[A-Za-z0-9_.-]+\.html$",
    content=(r"<body\b[^>]*>", r"</body>"),
    drop=K.DROP + [r'<div class="(header|nav-panel)">.*?</div>'], limit=400))

# ====================================================================== US government web guides

CISA = "https://www.cisa.gov/secure-our-world/"
CISA_PAGES = [CISA + p for p in ("use-strong-passwords", "turn-mfa", "recognize-and-report-phishing",
                                 "update-software", "require-strong-passwords", "teach-employees-avoid-phishing",
                                 "update-business-software")]
GUIDES.append(page_list_book(
    "cisa_secure_our_world", "Secure Our World: four easy ways to stay safe online (CISA)", "Online safety basics",
    "Cybersecurity and Infrastructure Security Agency (CISA)", CISA_PAGES,
    r"^https://www\.cisa\.gov/secure-our-world/[a-z0-9-]+$",
    "CISA's Secure Our World pages: use strong passwords and a password manager, turn on multi-factor "
    "authentication, recognise and report phishing, and update software; and the same four steps for small "
    "businesses (require strong passwords, teach employees to avoid phishing, update business software).",
    "From the Cybersecurity and Infrastructure Security Agency (cisa.gov): a US government work (public domain).",
    units=[(r"require|teach|business", "For small businesses"), (r".", "For everyone")]))

AIRC = "https://airc.nist.gov/airmf-resources/playbook/"
GUIDES.append(page_list_book(
    "nist_ai_rmf_playbook", "AI Risk Management Framework Playbook (NIST)", "AI risk management",
    "National Institute of Standards and Technology (NIST)",
    [AIRC] + [AIRC + p + "/" for p in ("govern", "map", "measure", "manage", "faq")],
    r"^https://airc\.nist\.gov/airmf-resources/playbook/([a-z-]+/)?$",
    "NIST's Playbook for the AI Risk Management Framework: suggested actions, documentation and references for "
    "each of the framework's four functions (Govern, Map, Measure and Manage), and its questions and answers.",
    "From NIST's Trustworthy and Responsible AI Resource Center (airc.nist.gov): a US government work (public "
    "domain). The Playbook is voluntary guidance and is updated from time to time.",
    units=[(r"/govern/", "Govern"), (r"/map/", "Map"), (r"/measure/", "Measure"), (r"/manage/", "Manage"),
           (r".", "About the Playbook")]))

# justice.gov/stopelderfraud is served by the Office for Victims of Crime's site (ovc.ojp.gov), where its pages live.
OVC = "https://ovc.ojp.gov/program/stop-elder-fraud/"
DOJ_PAGES = [OVC + p for p in ("overview", "about-hotline", "common-scams-and-warning-signs", "faqs", "resources",
                               "providing-help-restoring-hope")]
GUIDES.append(page_list_book(
    "doj_stop_elder_fraud", "Stop Elder Fraud and the National Elder Fraud Hotline (US Department of Justice)",
    "Elder fraud", "US Department of Justice, Office for Victims of Crime", DOJ_PAGES,
    r"^https://ovc\.ojp\.gov/program/stop-elder-fraud/[a-z0-9-]+$",
    "The Justice Department's Stop Elder Fraud pages: the National Elder Fraud Hotline (1-833-FRAUD-11, "
    "1-833-372-8311: who answers, when, and how they help), common scams against older adults and their warning "
    "signs (government impersonation, tech support, romance, grandparent, lottery and sweepstakes scams), "
    "questions and answers, and where to get help and report.",
    "From the US Department of Justice's Office for Victims of Crime (ovc.ojp.gov): a US government work (public "
    "domain)."))

ED = "https://studentprivacy.ed.gov"
ED_PAGES = [ED + "/ferpa", ED + "/faq/what-ferpa",
            ED + "/resources/parent-guide-family-educational-rights-and-privacy-act-ferpa",
            ED + "/resources/eligible-student-guide-family-educational-rights-and-privacy-act-ferpa",
            ED + "/resources/protection-pupil-rights-amendment-ppra-general-guidance"]
GUIDES.append(page_list_book(
    "ed_ferpa", "FERPA: student records privacy for parents and students (US Department of Education)",
    "Student privacy (FERPA)", "US Department of Education, Student Privacy Policy Office", ED_PAGES,
    r"^https://studentprivacy\.ed\.gov/(ferpa|faq/[a-z0-9-]+|resources/[a-z0-9-]+)$",
    "The Department of Education's pages on the Family Educational Rights and Privacy Act (FERPA): what it is, "
    "the parent's guide and the eligible student's guide (seeing education records, asking for corrections, when "
    "schools may share records, directory information), and the Protection of Pupil Rights Amendment (surveys).",
    f"From the US Department of Education (studentprivacy.ed.gov): a US government work (public domain). {NOT_LEGAL}",
    content=(r"<body\b[^>]*>", r"<footer\b")))

# ====================================================================== other countries' web guides

NCSC = "https://www.ncsc.gov.uk"
NCSC_PAGES = [NCSC + "/section/information-for/individuals-families"] + [NCSC + p for p in (
    "/collection/top-tips-for-staying-secure-online", "/collection/top-tips-for-staying-secure-online/"
    "activate-2-step-verification-on-your-email", "/collection/top-tips-for-staying-secure-online/password-managers",
    "/collection/top-tips-for-staying-secure-online/use-strong-passwords", "/collection/phishing-scams",
    "/guidance/setting-2-step-verification-2sv", "/guidance/securing-your-devices", "/guidance/data-breaches",
    "/guidance/shopping-online-securely", "/guidance/social-media-how-to-use-it-safely",
    "/guidance/smart-devices-in-the-home", "/guidance/smart-security-cameras-using-them-safely-in-your-home",
    "/guidance/buying-selling-second-hand-devices", "/guidance/what-is-an-antivirus-product",
    "/guidance/sextortion-scams-how-to-protect-yourself", "/guidance/online-gaming-for-families-and-individuals",
    "/guidance/how-to-spot-scammers-claiming-to-be-from-the-ncsc")]
GUIDES.append(dict(
    K.WEB, group=GROUP, name="ncsc_individuals_families", title="Staying secure online: advice for individuals and "
    "families (UK National Cyber Security Centre)", subject="Online safety (United Kingdom)",
    publisher="National Cyber Security Centre (NCSC), United Kingdom", country="United Kingdom", licence=OGL_UK,
    licence_url=OGL_UK_URL, licence_page=NCSC + "/section/about-this-website/terms-and-conditions",
    licence_text=r"Open Government Licence", source=NCSC_PAGES[0], crawl=[(NCSC_PAGES[0], 0)], urls=NCSC_PAGES,
    pages=r"^https://www\.ncsc\.gov\.uk/(section|collection|guidance)/[a-z0-9-]+(/[a-z0-9-]+)?$",
    unit_rules=[(r"phishing|sextortion|scammers", "Scams and phishing"),
                (r"password|2-step|2sv", "Passwords and 2-step verification"), (r".", "Devices and everyday life")],
    limit=len(NCSC_PAGES) + 5,
    description="The NCSC's advice for individuals and families: its top tips for staying secure online (strong "
                "passwords made of three random words, password managers, 2-step verification, updates, backups), "
                "phishing and scams and how to report them, securing devices, data breaches, shopping and social "
                "media, smart devices and security cameras at home, buying and selling second-hand devices, "
                "antivirus, sextortion scams, online gaming, and spotting scammers who claim to be the NCSC.",
    notice=f"Contains public sector information licensed under the Open Government Licence v3.0 (UK National Cyber "
           f"Security Centre). UK advice: in the UK, report scam emails to report@phishing.gov.uk and scam texts to "
           f"7726, and fraud to Report Fraud (Action Fraud); in the US, use the lines below. {SAFETY}"))

# Get Cyber Safe (the Canadian Centre for Cyber Security's public awareness site): the Government of Canada's terms
# allow non-commercial reproduction only (as in parenting.py), so the book is personal use only.
CROWN_NC = "Crown copyright (Canada), canada.ca terms for personal and public use"   # parenting.CROWN_NC
CANADA_TERMS = "https://www.canada.ca/en/transparency/terms.html"
CANADA_TEXT = r"you may reproduce the materials in whole or in part for non-commercial purposes"
GCS = "https://www.getcybersafe.gc.ca/en"
GUIDES.append(dict(open_guide(
    "canada_get_cyber_safe", "Get Cyber Safe: secure your accounts, devices and connections (Government of Canada)",
    "Online safety (Canada)", "Canadian Centre for Cyber Security (Communications Security Establishment), "
    "Government of Canada", "Canada", CROWN_NC, CANADA_TERMS, CANADA_TERMS, CANADA_TEXT,
    [GCS + "/secure-your-accounts", GCS + "/secure-your-devices", GCS + "/secure-your-connections",
     GCS + "/secure-your-information", GCS + "/glossary"],
    r"^https://www\.getcybersafe\.gc\.ca/en/(secure-your-[a-z-]+(/[a-z0-9-]+)?|glossary|blogs/[a-z0-9-]+)$",
    "Get Cyber Safe, the Government of Canada's online safety site: securing accounts (passphrases, passwords and "
    "PINs, password managers, multi-factor authentication, social media), devices (computers, phones, gaming "
    "systems, TVs and smart devices, system updates), connections (public Wi-Fi, VPNs, Bluetooth, firewalls, "
    "home networks) and information, its glossary, and its articles on scams and safe shopping.",
    "Canadian source, personal use only: reproduced under the Government of Canada's terms for non-commercial "
    "reproduction; a copy of the version on getcybersafe.gc.ca (each page's address is at its end), not the "
    "official version, made without the Government of Canada's endorsement. In Canada, report fraud to the "
    "Canadian Anti-Fraud Centre (1-888-495-8501).",
    follow=r"^https://www\.getcybersafe\.gc\.ca/en/secure-your-[a-z-]+$",
    units=[(r"accounts", "Accounts"), (r"devices", "Devices"), (r"connections", "Connections"),
           (r"information", "Information"), (r".", "Glossary and articles")], limit=150),
    personal_use=True))

# ====================================================================== PDFs

NIST = "National Institute of Standards and Technology (NIST)"
NV = "https://nvlpubs.nist.gov/nistpubs/"


def nist_pdf(name, title, subject, path, page, published, version, description, notice=""):
    """A NIST publication read whole from nvlpubs.nist.gov (csrc.nist.gov shuts out AI readers; nvlpubs does not)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=NIST, pdf=NV + path, page=page,
                    published=published, version=version, description=description,
                    notice=f"A work of NIST (US government work, public domain), available free of charge from "
                           f"nvlpubs.nist.gov. {notice}{SAFETY}")


PDFS = [
    K.us_pdf(GROUP, name="cisa_stopransomware_guide", title="#StopRansomware Guide (CISA and partners)",
             subject="Ransomware: prevention and response", publisher="Cybersecurity and Infrastructure Security "
             "Agency (CISA), with the FBI, NSA and MS-ISAC",
             pdf="https://www.cisa.gov/sites/default/files/2025-03/StopRansomware-Guide%20508.pdf",
             page="https://www.cisa.gov/resources-tools/resources/stopransomware-guide", published="2023-10",
             version="#StopRansomware Guide (October 2023 edition, accessible file of March 2025)",
             description="The joint #StopRansomware Guide: how ransomware and data extortion attacks happen, "
                         "best practices to prevent them (offline, encrypted backups; updates; multi-factor "
                         "authentication; phishing awareness), and a checklist for responding to an attack "
                         "(detect, contain, recover, report).",
             notice=f"A work of CISA and its US government partners (public domain). Report ransomware to CISA or "
                    f"the FBI. {SAFETY}"),
    nist_pdf("nist_csf_2", "The NIST Cybersecurity Framework (CSF) 2.0", "Cybersecurity framework",
             "CSWP/NIST.CSWP.29.pdf", "https://www.nist.gov/cyberframework", "2024-02-26", "CSF 2.0 (NIST CSWP 29)",
             "NIST's Cybersecurity Framework 2.0: the six functions (Govern, Identify, Protect, Detect, Respond, "
             "Recover), the categories of outcomes under each, profiles and tiers, for any organisation."),
    nist_pdf("nist_sp_1300_csf_small_business", "NIST Cybersecurity Framework 2.0: Small Business Quick-Start Guide "
             "(NIST SP 1300)", "Cybersecurity for small businesses", "SpecialPublications/NIST.SP.1300.pdf",
             "https://www.nist.gov/cyberframework", "2024-02", "NIST SP 1300",
             "NIST's quick-start guide to the Cybersecurity Framework for small businesses: what to do first under "
             "each function, in short checklists."),
    nist_pdf("nist_ir_7621_small_business", "Small Business Information Security: The Fundamentals (NIST IR 7621 "
             "Rev. 1)", "Cybersecurity for small businesses", "ir/2016/NIST.IR.7621r1.pdf",
             "https://www.nist.gov/itl/smallbusinesscyber", "2016-11", "NIST IR 7621 Revision 1",
             "NIST's guide for small businesses: understanding and managing information security risk, protecting "
             "information, the basics (backups, updates, passwords, firewalls, Wi-Fi, training), and planning for "
             "incidents."),
    nist_pdf("nist_sp_800_63_4", "Digital Identity Guidelines (NIST SP 800-63-4)", "Digital identity",
             "SpecialPublications/NIST.SP.800-63-4.pdf", "https://pages.nist.gov/800-63-4/", "2025-08",
             "NIST SP 800-63-4 (August 2025)",
             "NIST's Digital Identity Guidelines: identity proofing, authentication and federation, the assurance "
             "levels, and how services should choose them, including privacy, usability and equity."),
    nist_pdf("nist_sp_800_63b_4", "Authentication and Authenticator Management (NIST SP 800-63B-4)",
             "Passwords, passkeys and authenticators", "SpecialPublications/NIST.SP.800-63B-4.pdf",
             "https://pages.nist.gov/800-63-4/", "2025-08", "NIST SP 800-63B-4 (August 2025)",
             "NIST's rules for signing in: passwords (length over complexity, no forced regular changes, checking "
             "against breached passwords), one-time codes, security keys and syncable authenticators (passkeys), "
             "phishing resistance, and account recovery."),
    nist_pdf("nist_sp_800_12", "An Introduction to Information Security (NIST SP 800-12 Rev. 1)",
             "Information security basics", "SpecialPublications/NIST.SP.800-12r1.pdf",
             "https://www.nist.gov/publications/introduction-information-security", "2017-06",
             "NIST SP 800-12 Revision 1",
             "NIST's introduction to information security: its elements and roles, threats and vulnerabilities, "
             "risk management, policy, and the families of security controls."),
    nist_pdf("nist_ai_100_1_rmf", "Artificial Intelligence Risk Management Framework (AI RMF 1.0, NIST AI 100-1)",
             "AI risk management", "ai/NIST.AI.100-1.pdf", "https://www.nist.gov/itl/ai-risk-management-framework",
             "2023-01", "AI RMF 1.0 (NIST AI 100-1)",
             "NIST's voluntary framework for managing the risks of AI: what trustworthy AI is (valid and reliable, "
             "safe, secure, accountable and transparent, explainable, privacy-enhanced, fair), and the four "
             "functions Govern, Map, Measure and Manage."),
    nist_pdf("nist_ai_600_1_genai", "Generative AI Profile of the AI RMF (NIST AI 600-1)", "Generative AI risks",
             "ai/NIST.AI.600-1.pdf", "https://www.nist.gov/itl/ai-risk-management-framework", "2024-07",
             "NIST AI 600-1 (July 2024)",
             "NIST's profile for generative AI: the risks it names (confabulation, that is made-up answers; "
             "information integrity and deepfakes; data privacy; information security; harmful content; "
             "intellectual property) and the actions it suggests for each."),
    nist_pdf("nist_ai_800_1_misuse", "Managing Misuse Risk for Dual-Use Foundation Models (NIST AI 800-1, second "
             "public draft)", "AI safety (policy)", "ai/NIST.AI.800-1.ipd2.pdf",
             "https://www.nist.gov/caisi", "2025-01", "NIST AI 800-1, second public draft (January 2025)",
             "The US AI Safety Institute's draft guidance (the institute is now NIST's Center for AI Standards and "
             "Innovation, CAISI) for AI developers on anticipating, measuring and managing the risk that powerful "
             "models are misused, and on being open about it.",
             "A DRAFT, published for comment; not final guidance. "),
    K.us_pdf(GROUP, name="ftc_identity_theft_recovery_plan", title="Identity Theft: A Recovery Plan (FTC)",
             subject="Identity theft recovery", publisher="Federal Trade Commission (FTC)",
             archive="501a-idt-a-recovery-plan-508",
             version="FTC publication 501A (Internet Archive item 501a-idt-a-recovery-plan-508)",
             description="The FTC's step-by-step booklet for identity theft victims: what to do right away (call "
                         "the companies, place a fraud alert, get your credit reports, report to IdentityTheft.gov), "
                         "what to do next (close new accounts, remove bogus charges, correct your credit report, "
                         "think about a credit freeze), and special forms of identity theft (tax, medical, child, "
                         "government benefits), with sample letters.",
             notice=f"A work of the Federal Trade Commission (public domain), read from the Internet Archive's copy "
                    f"because ftc.gov refuses programs. The current version and the personal recovery plan are at "
                    f"IdentityTheft.gov. {SAFETY}"),
    K.us_pdf(GROUP, name="ic3_annual_report", title="Internet Crime Report (FBI Internet Crime Complaint Center)",
             subject="Internet crime and scams (statistics)", publisher="Federal Bureau of Investigation, Internet "
             "Crime Complaint Center (IC3)", pdf="https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf",
             page="https://www.ic3.gov/AnnualReport/Reports", version="IC3 Internet Crime Report 2025",
             description="The FBI's yearly report of the internet crime people reported to IC3: the most common "
                         "scams (phishing, extortion, investment and cryptocurrency fraud, tech support and "
                         "government impersonation, romance and business email compromise), the losses, the age "
                         "groups targeted, and how to report.",
             notice=f"A work of the FBI (US government work, public domain). {SAFETY}"),
    K.us_pdf(GROUP, name="ic3_elder_fraud_report", title="Elder Fraud Report (FBI Internet Crime Complaint Center)",
             subject="Elder fraud", publisher="Federal Bureau of Investigation, Internet Crime Complaint Center "
             "(IC3)", pdf="https://www.ic3.gov/AnnualReport/Reports/2023_IC3ElderFraudReport.pdf",
             page="https://www.ic3.gov/AnnualReport/Reports", published="2024-04", version="IC3 Elder Fraud Report "
             "2023 (the newest elder fraud report IC3 lists)",
             description="The FBI's report on internet fraud against people 60 and older: the scams that cost them "
                         "most (tech support, government impersonation, investment, romance, lottery and "
                         "grandparent scams), how they work, the warning signs, and how to report.",
             notice=f"A work of the FBI (US government work, public domain). {SAFETY}"),
    dict(group=GROUP, name="intl_ai_safety_interim_report", title="International Scientific Report on the Safety of "
         "Advanced AI: interim report (May 2024)", subject="AI safety (science and policy)",
         publisher="UK Department for Science, Innovation and Technology and the AI Safety Institute (an independent "
         "international expert panel chaired by Yoshua Bengio)", country="International", licence=OGL_UK,
         licence_url=OGL_UK_URL, level="reference",
         pdf="https://assets.publishing.service.gov.uk/media/6716673b96def6d27a4c9b24/international_scientific_report_"
             "on_the_safety_of_advanced_ai_interim_report.pdf",
         page="https://www.gov.uk/government/publications/international-scientific-report-on-the-safety-of-advanced-"
              "ai", licence_page="https://www.gov.uk/government/publications/international-scientific-report-on-the-"
                                 "safety-of-advanced-ai", licence_text=r"Open Government Licence v3\.0",
         published="2024-05-17", version="Interim report, 17 May 2024 (the October 2024 file on GOV.UK)",
         description="The first international scientific report on the safety of general-purpose AI: what these "
                     "systems can do, the risks the experts found (malicious use such as scams, deepfakes and "
                     "disinformation; malfunctions such as bias and loss of control; systemic risks such as privacy "
                     "and jobs) and the technical ways to reduce them.",
         notice="Contains public sector information licensed under the Open Government Licence v3.0. An INTERIM "
                f"report: the full International AI Safety Report (2025, 2026) is at internationalaisafetyreport.org "
                f"(link only). {SAFETY}"),
]

# ====================================================================== the privacy rules (law books)


def laws(S):
    """The privacy rules as law books for sources.LAWS, made with sources' own helpers (S is the sources module, so
    this module does not import it): HIPAA's privacy and security rules, FERPA's and COPPA's rules, the UK Data
    Protection Act 2018 and UK GDPR, and Canada's PIPEDA; each in the group of this module."""
    out = [
        S._cfr("cfr_45_164_hipaa_privacy_security", "HIPAA Privacy, Security and Breach Notification Rules (45 CFR "
               "part 164)", "Health privacy (HIPAA)", 45, 1, 164, "The HHS rules under HIPAA: the Privacy Rule "
               "(your rights to see and get copies of your health records, to ask for corrections, to know who "
               "they were shared with, and when doctors, insurers and their contractors may use and share them), "
               "the Security Rule and the Breach Notification Rule.", group=GROUP),
        S._cfr("cfr_34_99_ferpa", "Family Educational Rights and Privacy (FERPA) rules (34 CFR part 99)",
               "Student privacy (FERPA)", 34, 1, 99, "The Department of Education's FERPA rules: parents' and "
               "eligible students' rights to see education records and ask for corrections, when schools may "
               "share records without consent, directory information, and complaints.", group=GROUP),
        S._cfr("cfr_16_312_coppa", "Children's Online Privacy Protection Rule (COPPA, 16 CFR part 312)",
               "Children's online privacy (COPPA)", 16, 1, 312, "The FTC's COPPA Rule: what websites, apps and "
               "online services aimed at children under 13 must tell parents, the parental consent they need, "
               "parents' rights to review and delete their child's information, and data security.", group=GROUP),
        dict(S._uk("uk_data_protection_act_2018", "Data Protection Act 2018 (United Kingdom)", "Data protection (UK)",
                   "ukpga/2018/12", "The UK's Data Protection Act 2018 with its amendments: how the UK GDPR applies, "
                   "law enforcement and intelligence processing, the Information Commissioner, and offences."),
             group=GROUP),
        dict(S._uk("uk_gdpr", "UK General Data Protection Regulation (UK GDPR)", "Data protection (UK)",
                   "eur/2016/679", "The UK GDPR (the EU General Data Protection Regulation as kept in UK law): "
                   "the principles of data protection, lawful bases, people's rights (access, correction, erasure, "
                   "objection, portability), controllers' duties, breaches and transfers. The EU's own GDPR is "
                   "much the same text; it is on EUR-Lex (link only)."), group=GROUP),
        dict(S._canada("canada_pipeda", "Personal Information Protection and Electronic Documents Act (PIPEDA, S.C. "
                       "2000, c. 5)", "Privacy law (Canada)", "acts/P-8.6", "Canada's federal private-sector "
                       "privacy law: how businesses may collect, use and disclose personal information (with the "
                       "ten fair information principles in its Schedule 1), your right to see and correct it, and "
                       "complaints to the Privacy Commissioner of Canada."), group=GROUP),
    ]
    return out


LAW_NAMES = ["cfr_45_164_hipaa_privacy_security", "cfr_34_99_ferpa", "cfr_16_312_coppa", "uk_data_protection_act_2018",
             "uk_gdpr", "canada_pipeda"]

# ====================================================================== keys

SCAM_BOOKS = ["cisa_secure_our_world", "cisa_stopransomware_guide", "ftc_identity_theft_recovery_plan",
              "ic3_annual_report", "ic3_elder_fraud_report", "doj_stop_elder_fraud", "ncsc_individuals_families",
              "canada_get_cyber_safe"]
AI_BOOKS = ["nist_ai_100_1_rmf", "nist_ai_rmf_playbook", "nist_ai_600_1_genai", "nist_ai_800_1_misuse",
            "intl_ai_safety_interim_report", "owasp_cheat_sheets"]


def all_keys():
    """Every key of the request word "privacy": this module's books and the privacy law books."""
    return [f"privacy:{g['name']}" for g in GUIDES + PDFS] + [f"law:{n}" for n in LAW_NAMES]


COLLECTION = K.Collection("privacy", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"privacy": all_keys,
                                 "privacy-scams": lambda: [f"privacy:{n}" for n in SCAM_BOOKS],
                                 "privacy-ai": lambda: [f"privacy:{n}" for n in AI_BOOKS]})

LICENCE_LINES = {
    "privacy_open": "ssd.eff.org (EFF): www.eff.org/copyright (checked at every build): \"freely distributed at will "
                    "under the Creative Commons Attribution 4.0 International License (CC-BY)\"; tb-manual."
                    "torproject.org: www.torproject.org/about/trademark/ (checked at every build): \"licensed under a "
                    "Creative Commons Attribution 4.0 International License\". robots.txt allows both; no AI rules "
                    "(checked 2026-11-22).",
    "privacy_share_alike": "securityinabox.org (its footer, checked at every build), privacyguides.org/en/about/"
                           "notices/ (\"Generally, content on this website is released under ... CC-BY-SA-4.0\") and "
                           "cheatsheetseries.owasp.org (each page's footer): CC BY-SA 4.0; the GnuPG manual: GNU GPL "
                           "version 3 or later (its title page). Share-alike: a book made from them keeps the "
                           "licence. robots.txt allows all four; no AI rules (checked 2026-11-22).",
    "privacy_us_gov": "cisa.gov, nvlpubs.nist.gov, airc.nist.gov, ic3.gov, ovc.ojp.gov and studentprivacy.ed.gov: "
                      "works "
                      "of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build). "
                      "csrc.nist.gov's robots.txt shuts out AI companies' readers, so NIST's PDFs are read from "
                      "nvlpubs.nist.gov, which has no such rule. The FTC's booklet is read from the Internet Archive "
                      "(ftc.gov refuses programs, 403).",
    "privacy_uk": "www.ncsc.gov.uk/section/about-this-website/terms-and-conditions (checked at every build): "
                  "content \"subject to Crown copyright ... the Open Government Licence (OGL) v3.0\"; images and logos "
                  "left out. GOV.UK's publication page of the interim AI safety report: \"All content is available "
                  "under the Open Government Licence v3.0\". legislation.gov.uk: OGL v3.0 (as for the other UK laws).",
    "privacy_canada": "getcybersafe.gc.ca links to canada.ca/en/transparency/terms.html (checked at every build): "
                      "non-commercial reproduction allowed, so Get Cyber Safe is personal use only; PIPEDA from the "
                      "Justice Laws website under the Reproduction of Federal Law Order.",
}

NOT_INCLUDED = [
    ("FTC consumer advice on privacy, identity theft and scams (consumer.ftc.gov) and IdentityTheft.gov",
     "Public domain, but ftc.gov and consumer.ftc.gov refuse programs (403, robots.txt included, checked again "
     "2026-11-22), and IdentityTheft.gov is an app that needs JavaScript. The Wayback Machine did not answer "
     "reliably from the build machine; its copies can be added later. The FTC's recovery booklet is built from the "
     "Internet Archive (privacy:ftc_identity_theft_recovery_plan). Link-only. Index: https://consumer.ftc.gov/"
     "features/scam-alerts and https://www.identitytheft.gov/"),
    ("FCC consumer guides (robocalls, spoofing, SIM swapping, phone privacy)", "Public domain, but www.fcc.gov "
     "refuses programs (403, robots.txt included, 2026-11-22). Link-only. Index: https://www.fcc.gov/consumers/"
     "guides"),
    ("HHS HIPAA for individuals (your rights under HIPAA)", "Public domain, but www.hhs.gov refuses programs (403, "
     "robots.txt included, 2026-11-22), and no Internet Archive copy was found. The HIPAA rules themselves are "
     "built (law:cfr_45_164_hipaa_privacy_security). Link-only. Index: https://www.hhs.gov/hipaa/for-individuals/"
     "index.html"),
    ("CFPB pages on fraud, credit reports, credit freezes and older Americans", "Already in the library: "
     "money:cfpb_consumer_tools (every page of the CFPB's consumer guides, fraud and credit reports included); not "
     "built again. Index: https://www.consumerfinance.gov/consumer-tools/fraud/"),
    ("EFF Surveillance Self-Defense guides", "Already in the library (nonprofit:eff_surveillance_self_defense); "
     "this module adds only its glossary and playlists (privacy:eff_ssd_glossary_playlists). Index: "
     "https://ssd.eff.org/"),
    ("NIST Computer Security Resource Center (csrc.nist.gov)", "Its robots.txt shuts out AI companies' readers "
     "(ClaudeBot, GPTBot), so it is not read; NIST's PDFs are read from nvlpubs.nist.gov instead. Index: "
     "https://csrc.nist.gov/publications"),
    ("ENISA (EU Agency for Cybersecurity) publications", "Reuse is allowed with credit, but www.enisa.europa.eu's "
     "robots.txt shuts out AI companies' readers; not read. Link-only. Index: https://www.enisa.europa.eu/"
     "publications"),
    ("EU AI Act (Regulation (EU) 2024/1689) and EU GDPR (Regulation (EU) 2016/679) from EUR-Lex", "Reuse is "
     "allowed with the source named, but eur-lex.europa.eu answers programs with a bot check (HTTP 202, no page). "
     "The UK GDPR (almost the same text as the EU GDPR) is built from legislation.gov.uk. Link-only. Index: "
     "https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng and https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng"),
    ("OECD AI Principles (OECD Recommendation on Artificial Intelligence)", "www.oecd.org refuses programs (403) "
     "and legalinstruments.oecd.org shows the text only with JavaScript; the OECD's terms were not confirmed open "
     "for this text. Link-only. Index: https://oecd.ai/en/ai-principles"),
    ("International AI Safety Report 2025 and 2026", "GOV.UK now sends readers to internationalaisafetyreport.org, "
     "whose robots.txt shuts out AI companies' readers; not read. The interim report of May 2024 is built from "
     "GOV.UK (privacy:intl_ai_safety_interim_report). Link-only. Index: https://internationalaisafetyreport.org/"),
    ("UK AI Security Institute research and reports (aisi.gov.uk)", "No open licence statement was found on its "
     "site (it is not on GOV.UK); link-only until one is. Index: https://www.aisi.gov.uk/research"),
    ("Canadian Centre for Cyber Security guidance for organisations (cyber.gc.ca)", "The same Government of Canada "
     "terms (non-commercial); its consumer site Get Cyber Safe is built (personal use). Index: "
     "https://www.cyber.gc.ca/en/guidance"),
    ("Company privacy and safety help pages: Apple, Google, Microsoft, Meta, Amazon, OpenAI, Anthropic and other AI "
     "companies", "The companies' copyright (no open licence on the pages); link-only for the owner to open or "
     "fetch with Program Downloader. Microsoft's and Apple's openly licensed documentation is already in the "
     "library (techdocs). Index: https://support.apple.com/guide/personal-safety/welcome/web and "
     "https://myaccount.google.com/security-checkup and https://support.microsoft.com/security"),
    ("Get Safe Online (UK), AARP Fraud Watch Network, Consumer Reports Security Planner", "Copyright, and "
     "getsafeonline.org's robots.txt shuts out AI companies' readers; link-only. Index: "
     "https://www.aarp.org/money/scams-fraud/"),
    ("State privacy laws (California's CCPA/CPRA and others)", "California's site refuses programs "
     "(sources.REFERENCE_NOT_INCLUDED); the California Privacy Protection Agency's pages are the state's copyright "
     "with no reuse licence found. Link-only. Index: https://cppa.ca.gov/"),
]

PRACTICE_SUBJECTS = [
    (r"online safety \(united kingdom\)|data protection \(uk\)", "where to report scams and fraud (Report Fraud, "
     "report@phishing.gov.uk and 7726 in the UK, rather than the FTC and IC3), and the data protection law and "
     "regulator (the UK GDPR and the Information Commissioner's Office, rather than US sector laws)"),
    (r"online safety \(canada\)|privacy law \(canada\)", "where to report fraud (the Canadian Anti-Fraud Centre, "
     "1-888-495-8501, rather than the FTC and IC3) and the privacy law and regulator (PIPEDA and the Privacy "
     "Commissioner of Canada)"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
