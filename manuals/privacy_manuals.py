"""The collection "Password managers, security keys, routers, VPNs and home cameras (manuals)" (category key
privacy_security): the owner's request of 2026-11-22 for privacy, security and digital safety. categories.py adds it
to CATEGORIES under its own heading.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia         the Internet Archive's manual collections, searched by the words in IA_WORDS (security keys, password
             managers, VPNs, authenticators, firewalls, Wi-Fi and mesh routers, security cameras and video
             doorbells, antivirus software, fingerprint and smart card readers). The plain words "router", "modem",
             "webcam" (computers), "smart lock", "shredder", "baby monitor" and "alarm system" are already searched
             by other collections, so they are not repeated here;
  makers     the password manager, security key, authenticator, VPN, router, home camera and antivirus makers: by
             the owner's rule their own manuals and help pages are LINK-ONLY, for the person (or the personal
             assistant) to open in a browser or fetch with Program Downloader; nothing is read from their sites
             (their terms keep all rights);
  documents  the openly licensed manuals the index may mark "full" (the Program Downloader may copy them whole):
             KeePassXC's User Guide and Getting Started guide (GNU GPL, its COPYING file);
  guidance   the public guides the reference library builds in full (textbooks/privacy_books.py: CISA, NIST SP
             800-63B, the UK NCSC, Security in a Box, the Tor manual), and the FTC's and the FBI's reporting pages
             as links.

The safety notice is said first (NOTICE): buy security keys and download apps only from the maker or a store you
trust, keep a spare key and recovery codes, change router and camera default passwords, and how to report scams.
"""

NOTICE = ("Read this first. Buy security keys and download password managers, authenticator and VPN apps only from "
          "the maker's own site or an official app store: fake apps and second-hand keys can be traps. Register a "
          "spare security key and keep recovery codes somewhere safe. Change the default password of every router, "
          "camera and smart device, turn on automatic updates, and use WPA3 or WPA2. Nobody from a real company "
          "will call you to fix your computer or ask for your codes: report scams at ReportFraud.ftc.gov or "
          "ic3.gov, and if the person targeted is 60 or older call the National Elder Fraud Hotline, "
          "1-833-372-8311.")

IA_WORDS = ["yubikey", "security key", "password manager", "vpn", "authenticator", "firewall", "wireless router",
            "mesh wifi", "security camera", "video doorbell", "home security", "antivirus", "fingerprint reader",
            "smart card reader"]

RULE = ("by the owner's rule the maker's own manuals and help pages are link-only: nothing is read from its site; "
        "its page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="privacy_security", prefix="ps", documents="manuals", access="link", reason=RULE)


def _maker(key, maker, kind, library, site):
    """One maker, link-only (see RULE)."""
    return dict(_COMMON, key=key, maker=maker, type=kind, library=library, site=site)


MAKERS = [
    # password managers
    _maker("bitwarden", "Bitwarden", "password manager", "https://bitwarden.com/help/", "bitwarden.com"),
    _maker("1password", "1Password", "password manager", "https://support.1password.com/", "1password.com"),
    _maker("dashlane", "Dashlane", "password manager", "https://support.dashlane.com/", "dashlane.com"),
    _maker("keeper", "Keeper Security", "password manager", "https://docs.keeper.io/", "keepersecurity.com"),
    _maker("proton", "Proton (Proton Pass, Proton VPN, Proton Mail)", "password manager, VPN and encrypted email",
           "https://proton.me/support", "proton.me"),
    # security keys and authenticators
    _maker("yubico", "Yubico (YubiKey)", "security key", "https://docs.yubico.com/", "yubico.com"),
    _maker("google-titan", "Google Titan Security Key", "security key", "https://support.google.com/titansecuritykey/",
           "store.google.com"),
    _maker("feitian", "FEITIAN", "security key", "https://www.ftsafe.com/support", "ftsafe.com"),
    _maker("nitrokey", "Nitrokey", "security key", "https://docs.nitrokey.com/", "nitrokey.com"),
    _maker("token2", "Token2", "security key and code token", "https://www.token2.com/site/page/guides", "token2.com"),
    _maker("microsoft-authenticator", "Microsoft Authenticator", "authenticator app",
           "https://support.microsoft.com/account-billing/microsoft-authenticator-help", "microsoft.com"),
    _maker("google-authenticator", "Google Authenticator", "authenticator app",
           "https://support.google.com/accounts/answer/1066447", "google.com"),
    _maker("authy", "Twilio Authy", "authenticator app", "https://help.twilio.com/topic/authy", "authy.com"),
    # VPNs
    _maker("mullvad", "Mullvad VPN", "VPN", "https://mullvad.net/en/help", "mullvad.net"),
    _maker("ivpn", "IVPN", "VPN", "https://www.ivpn.net/knowledgebase/", "ivpn.net"),
    _maker("nordvpn", "NordVPN", "VPN", "https://support.nordvpn.com/", "nordvpn.com"),
    _maker("expressvpn", "ExpressVPN", "VPN", "https://www.expressvpn.com/support/", "expressvpn.com"),
    _maker("surfshark", "Surfshark", "VPN", "https://support.surfshark.com/", "surfshark.com"),
    # routers and mesh Wi-Fi (the computers collection searches the Internet Archive for "router" itself)
    _maker("eero", "eero (Amazon)", "mesh Wi-Fi router", "https://support.eero.com/", "eero.com"),
    _maker("google-nest-wifi", "Google Nest Wifi", "mesh Wi-Fi router", "https://support.google.com/googlenest/",
           "store.google.com"),
    _maker("ubiquiti", "Ubiquiti (UniFi, AmpliFi)", "router and access point", "https://help.ui.com/", "ui.com"),
    _maker("netgear-security", "NETGEAR (Armor and router security)", "router",
           "https://www.netgear.com/support/", "netgear.com"),
    # home cameras and doorbells
    _maker("ring", "Ring", "video doorbell and home camera", "https://ring.com/support", "ring.com"),
    _maker("arlo", "Arlo", "home security camera", "https://www.arlo.com/en-us/support/", "arlo.com"),
    _maker("wyze", "Wyze", "home security camera", "https://support.wyze.com/", "wyze.com"),
    # security software
    _maker("microsoft-defender", "Microsoft Defender", "antivirus",
           "https://support.microsoft.com/windows/stay-protected-with-the-windows-security-app", "microsoft.com"),
    _maker("malwarebytes", "Malwarebytes", "antivirus", "https://help.malwarebytes.com/", "malwarebytes.com"),
    _maker("bitdefender", "Bitdefender", "antivirus", "https://www.bitdefender.com/consumer/support/",
           "bitdefender.com"),
    _maker("norton", "Norton (Gen Digital)", "antivirus", "https://support.norton.com/", "norton.com"),
]

# Openly licensed manuals: "full" (the Program Downloader may copy them whole when robots.txt allows).
GPL_KEEPASSXC = "GNU GPL version 2 or 3 (the KeePassXC Team; the project's COPYING file)"
GPL_REASON = ("KeePassXC and its documentation are under the GNU GPL (COPYING: \"License: GPL-2 or GPL-3\"); "
              "keepassxc.org's robots.txt only names its sitemap (all allowed)")
DOCUMENTS = [
    dict(key="keepassxc-user-guide", by="The KeePassXC Team", product="KeePassXC",
         title="KeePassXC User Guide (the free, offline password manager)",
         url="https://keepassxc.org/docs/KeePassXC_UserGuide", type="password manager", document="manual",
         access="full", rights=GPL_KEEPASSXC, reason=GPL_REASON),
    dict(key="keepassxc-getting-started", by="The KeePassXC Team", product="KeePassXC",
         title="KeePassXC Getting Started Guide", url="https://keepassxc.org/docs/KeePassXC_GettingStarted",
         type="password manager", document="manual", access="full", rights=GPL_KEEPASSXC, reason=GPL_REASON),
]

GUIDANCE = [
    dict(title="Secure Our World: strong passwords, multi-factor authentication, phishing and updates (CISA; built "
               "in full in the reference library: privacy:cisa_secure_our_world)",
         url="https://www.cisa.gov/secure-our-world/use-strong-passwords",
         by="the Cybersecurity and Infrastructure Security Agency"),
    dict(title="Authentication and Authenticator Management: passwords, passkeys and security keys (NIST SP "
               "800-63B-4; in the reference library: privacy:nist_sp_800_63b_4)",
         url="https://pages.nist.gov/800-63-4/", by="the National Institute of Standards and Technology"),
    dict(title="Password managers and 2-step verification (UK NCSC; in the reference library: "
               "privacy:ncsc_individuals_families)",
         url="https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/password-managers",
         by="the UK National Cyber Security Centre"),
    dict(title="Security in a Box: password managers, two-factor and safer browsing (in the reference library: "
               "privacy:security_in_a_box)", url="https://securityinabox.org/en/passwords/password-managers",
         by="Front Line Defenders and Tactical Tech"),
    dict(title="Tor Browser manual (in the reference library: privacy:tor_manual)",
         url="https://tb-manual.torproject.org/", by="the Tor Project"),
    dict(title="Report fraud and scams (FTC; open it in a browser: ftc.gov refuses programs)",
         url="https://reportfraud.ftc.gov/", by="the Federal Trade Commission"),
    dict(title="Report internet crime (FBI Internet Crime Complaint Center)", url="https://www.ic3.gov/",
         by="the Federal Bureau of Investigation"),
]

CATEGORY = dict(
    name="Password managers, security keys, routers, VPNs and home cameras (manuals)",
    description="Password managers, security keys and code tokens, authenticator apps, VPN apps, Wi-Fi and mesh "
                "routers, home security cameras and video doorbells, and antivirus software: the Internet Archive's "
                "manuals, the makers' help pages (links), KeePassXC's openly licensed guides, and the public "
                "security guidance. Links only, except the openly licensed guides.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, documents=DOCUMENTS, guidance=GUIDANCE, notice=NOTICE)
