"""Picture packs for PRIVACY, SECURITY AND DIGITAL SAFETY (the owner's request of 2026-11-22): the real-photo side of
the section. Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as
(None, None, row) rows naming the same picture. The limit counts pictures. The computer-made scam and safe message
examples are a separate pack (packs/synthetic_scams_packs.py).

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise the things that
keep people private and safe online (security keys, code tokens, fingerprint readers, webcam covers, routers, home
cameras and smart speakers) and the screens that matter (phishing, padlocks and HTTPS, ransomware notes, CAPTCHAs,
sign-in pages, authenticator and password manager apps), and to say the plain safety advice that goes with each.

Answers say only what the source says (a Commons category's name), never a guess: no brand or model is named unless
the category names it. Each answer ends with the notes that fit (the same words in the kit's privacy_sources.py; the
scam notes come from packs/synthetic_scams_packs.py):
  KEY_NOTE        security keys: register a spare, keep it safe.
  ROUTER_NOTE     change the default admin password, WPA3 or WPA2, firmware updates (CISA).
  CAMERA_NOTE     home cameras and smart speakers: default passwords, two-step verification, updates, what they record.
  BIO_NOTE        a fingerprint is a convenience; keep a strong passcode behind it.
  SKIM_NOTE       card skimmers: loose or added parts, cover the PIN, tap to pay.
  KEYLOG_NOTE     keyloggers: unknown plugs, security software.
  RANSOM_NOTE     ransomware: disconnect, do not pay, report to the FBI or CISA, offline backups (3-2-1).
  CAPTCHA_NOTE    CAPTCHAs: audio challenges and accessible alternatives.
  SIGNIN_NOTE     check the address before typing a password; password manager and two-step verification.
  PM_NOTE         a password manager: a different strong password for every account.
  WIFI_NOTE       public Wi-Fi: check the network's name with staff, use mobile data or a VPN for private things.
  BREACH_NOTE     after a breach: change the password, two-step verification, credit freeze.
and VERIFY_NOTE, REPORT_NOTE, CODE_NOTE, PADLOCK_NOTE from the scam examples.

The packs (PRIVACY_PACKS):
  commons_privacy_security   Wikimedia Commons (CC0, public domain or CC BY files only): YubiKeys and FIDO2 security
                             keys, RSA SecurID tokens, smart cards, fingerprint scanners (Touch ID), webcam covers,
                             Wi-Fi routers, IP and Wi-Fi cameras, security cameras and their warning signs, Google Nest
                             and Ring devices, door access systems, card skimmers and keystroke loggers.
  commons_privacy_screens    Commons: phishing and voice phishing, advance-fee ("419") scams, HTTPS and padlock icons,
                             ransomware, reCAPTCHA, sign-in screens, Google Authenticator and multi-factor
                             authentication, password managers (KeePass, KeePassXC, Bitwarden), VeraCrypt, GnuPG, the
                             Tor Browser, Signal, antivirus software, data breaches and evil-twin Wi-Fi.

Not repeated here: device_packs (Routers, Smart speakers, Amazon Echo, Google Home, Paper shredders), things_packs
(Webcams, Modems, Hard disk drives), everyday_extras_packs (Error messages, CAPTCHAs among its screenshots),
hardware_packs and home_packs (Padlocks). Open Images was looked at and left out (the kit's
privacy_sources.py, PRIVACY_NOT_INCLUDED, says why).

    python packs/privacy_packs.py commons_privacy_security --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from synthetic_scams_packs import VERIFY_NOTE, REPORT_NOTE, CODE_NOTE, PADLOCK_NOTE

# ----------------------------------------------------------------- the notes (the kit uses the same words)

KEY_NOTE = ("Security keys: register a second (spare) key on each account and keep it somewhere safe, so losing one "
            "key does not lock you out.")
ROUTER_NOTE = ("Router safety (CISA): change the default admin password, turn on WPA3 or WPA2 encryption with a strong "
               "Wi-Fi password, and install firmware updates; replace a router the maker no longer updates.")
CAMERA_NOTE = ("Connected cameras and smart speakers: change the default password, turn on two-step verification and "
               "automatic updates, and think about who and what they can see and hear.")
BIO_NOTE = ("A fingerprint is a convenient way to unlock; keep a strong passcode or password behind it, as the device "
            "falls back to that.")
SKIM_NOTE = ("Card skimmers: before you use a card reader, check for loose, bulky or added parts; cover the keypad "
             "when you type your PIN; tap to pay where you can.")
KEYLOG_NOTE = ("Keyloggers: check for an unknown plug between the keyboard and the computer, and keep the computer's "
               "security software and updates on.")
RANSOM_NOTE = ("Ransomware: disconnect the device from the internet, do not pay, and report it to the FBI at ic3.gov "
               "or to CISA; keep backups offline (the 3-2-1 rule: three copies, on two kinds of storage, one away from "
               "home).")
CAPTCHA_NOTE = ("CAPTCHAs check that you are a person, not a program. Many have an audio challenge; if one blocks you, "
                "ask the website for another way to verify, as screen reader users often have to.")
SIGNIN_NOTE = ("Before you type a password, check the web address; use a password manager and turn on two-step "
               "verification.")
PM_NOTE = ("A password manager makes and remembers a different strong password for every account; protect it with a "
           "long passphrase and two-step verification.")
WIFI_NOTE = ("Public Wi-Fi: check the network's exact name with the staff, and use mobile data or a trusted VPN for "
             "banking and other private things.")
BREACH_NOTE = ("After a data breach: change that password (and anywhere you used it), turn on two-step verification, "
               "and think about a free credit freeze.")
SCAM_NOTES = f"{VERIFY_NOTE} {REPORT_NOTE}"
ASK_WHAT = "What is this?"
NOTES = (KEY_NOTE, ROUTER_NOTE, CAMERA_NOTE, BIO_NOTE, SKIM_NOTE, KEYLOG_NOTE, RANSOM_NOTE, CAPTCHA_NOTE, SIGNIN_NOTE,
         PM_NOTE, WIFI_NOTE, BREACH_NOTE)


def thing(category, words, notes="", deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


# ----------------------------------------------------------------- Commons: security devices and things

# "FIDO2" also holds logos and diagrams, "Keystroke logging" screenshots and drawings: only files whose own words
# name the thing itself.
KEY_WORDS = re.compile(r"\b(keys?|tokens?|yubikey|titan|solo ?keys?|nitrokey|usb|nfc)\b", re.I)
KEYLOGGER_WORDS = re.compile(r"\b(key ?loggers?|keystroke loggers?|hardware)\b", re.I)
SECURITY_THINGS = [
    thing("YubiKey", "a YubiKey, a hardware security key: you plug it in or tap it to prove it is you when you sign "
                     "in", KEY_NOTE),
    thing("FIDO2", "a FIDO2 security key, a small device that signs you in safely without sending a password",
          KEY_NOTE, True, KEY_WORDS),
    thing("RSA SecurID", "an RSA SecurID token, a small device that shows a new sign-in code every minute", CODE_NOTE),
    thing("Smart cards", "a smart card, a card with a chip that holds keys or identity for signing in or paying"),
    thing("Fingerprint scanners", "a fingerprint scanner, which unlocks a device or account with your fingerprint",
          BIO_NOTE, True),
    thing("Webcam covers", "a webcam cover, a small slide or sticker that blocks a computer's camera when it is not "
                           "in use", "", True),
    thing("Wi-Fi routers and access points", "a Wi-Fi router or access point, which runs a home or office wireless "
                                             "network", ROUTER_NOTE),
    thing("IP cameras", "an IP camera, a security camera that connects to a network or the internet", CAMERA_NOTE,
          True),
    thing("Wi-Fi cameras", "a Wi-Fi camera, a home security camera that connects over wireless", CAMERA_NOTE),
    thing("Security cameras", "a security camera (CCTV camera), which records video of a place"),
    thing("Security camera warning signs", "a sign warning that security cameras (CCTV) record in this area", "",
          True),
    thing("Google Nest", "a Google Nest smart home device (Google Nest makes smart speakers, displays, thermostats, "
                         "cameras and smoke alarms)", CAMERA_NOTE, True),
    thing("Ring (company)", "a Ring device (Ring makes video doorbells and home security cameras)", CAMERA_NOTE,
          True),
    thing("Access control systems", "an access control system: a keypad, card reader or electronic lock that "
                                    "controls who can open a door"),
    thing("Skimming (fraud)", "a card skimmer, a hidden device criminals fit to card readers to copy cards",
          f"{SKIM_NOTE} {REPORT_NOTE}"),
    thing("Keystroke logging", "a keystroke logger (keylogger), a hidden device or program that records what is "
                               "typed", KEYLOG_NOTE, pattern=KEYLOGGER_WORDS),
]

# ----------------------------------------------------------------- Commons: screens, scams and privacy tools

# "Phishing" also holds logos and cartoons: only files whose own words name a message, page or screenshot.
PHISH_WORDS = re.compile(r"\b(e-?mails?|mails?|messages?|sms|texts?|screenshots?|web ?sites?|pages?|login|sign[- ]?in|"
                         r"phishing (e-?mail|attempt|site|page|example)|scam)\b", re.I)
SCREENS = [
    thing("Phishing", "an example of phishing: a message or web page that tries to trick you into giving away "
                      "passwords, money or personal details", SCAM_NOTES, pattern=PHISH_WORDS),
    thing("Voice phishing", "a picture about voice phishing (vishing): scam phone calls that pretend to be a bank, "
                            "a company or the government", SCAM_NOTES),
    thing("419 scams", "an advance-fee (\"419\") scam message, which promises a large sum of money in return for a "
                       "fee paid first", SCAM_NOTES),
    thing("HTTPS", "a picture about HTTPS, the secure way web pages are sent; browsers show it with a padlock or "
                   "\"https\" in the address bar", PADLOCK_NOTE, True),
    thing("Padlock icons", "a padlock icon, the symbol apps and browsers use for security, locking or encryption",
          PADLOCK_NOTE, True),
    thing("Ransomware", "a ransomware screen or a picture about ransomware: malicious software that locks or "
                        "scrambles files and demands payment", RANSOM_NOTE, True),
    thing("ReCAPTCHA", "a reCAPTCHA, a test a website uses to check that you are a person, not a program",
          CAPTCHA_NOTE),
    thing("Login", "a sign-in (login) screen", SIGNIN_NOTE, True),
    thing("Google Authenticator", "Google Authenticator, an app that shows six-digit sign-in codes that change every "
                                  "30 seconds", CODE_NOTE),
    thing("Multi-factor authentication", "a picture about multi-factor (two-step) authentication: signing in with a "
                                         "password plus a second proof, such as a code, a security key or a "
                                         "fingerprint", "", True),
    thing("KeePass", "KeePass, a free password manager", PM_NOTE, True),
    thing("KeePassXC", "KeePassXC, a free password manager", PM_NOTE, True),
    thing("Bitwarden", "Bitwarden, a password manager", PM_NOTE, True),
    thing("VeraCrypt", "VeraCrypt, free software that encrypts files, drives and whole disks"),
    thing("GNU Privacy Guard", "GnuPG (GNU Privacy Guard), free software for encrypting and signing email and files",
          "", True),
    thing("Tor Browser", "the Tor Browser, a web browser that hides your location and browsing from the sites you "
                         "visit and from your internet provider", "", True),
    thing("Signal (software)", "Signal, an end-to-end encrypted messaging and calling app", "", True),
    thing("Antivirus software", "antivirus (security) software", "Keep it and the computer's own updates turned on.",
          True),
    thing("Data breaches", "a picture about a data breach, when records of people's personal data are stolen or "
                           "exposed", BREACH_NOTE, True),
    thing("Evil twin (wireless networks)", "a picture about an \"evil twin\": a fake Wi-Fi network named like a real "
                                           "one, to spy on people who join it", WIFI_NOTE),
]


def build_commons_privacy_security(limit):
    """The commons_privacy_security pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(SECURITY_THINGS, limit, "privsec")


def build_commons_privacy_screens(limit):
    """The commons_privacy_screens pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(SCREENS, limit, "privscreen")


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
PRIVACY_PACKS = {
    "commons_privacy_security": (build_commons_privacy_security, COMMONS_LICENCE.format(
        what="security key, code token, smart card, fingerprint scanner, webcam cover, router, camera, smart home, "
             "door access, card skimmer and keylogger")),
    "commons_privacy_screens": (build_commons_privacy_screens, COMMONS_LICENCE.format(
        what="phishing, scam, HTTPS, padlock icon, ransomware, CAPTCHA, sign-in, authenticator, password manager, "
             "encryption, Tor, Signal, antivirus, data breach and Wi-Fi")),
}
PRIVACY_LIMITS = {
    "commons_privacy_security": 900,      # 16 categories; Security cameras and Fingerprint scanners have most
    "commons_privacy_screens": 600,       # 20 categories, few files in most
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
PRIVACY_COMMONS_KEYS = ("commons_privacy_security", "commons_privacy_screens")
# The Commons category specs of the packs (for the self-test).
PRIVACY_SPECS = SECURITY_THINGS + SCREENS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a privacy and security pack builder.")
    parser.add_argument("key", choices=sorted(PRIVACY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = PRIVACY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
