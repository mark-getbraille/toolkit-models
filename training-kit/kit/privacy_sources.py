"""PRIVACY, SECURITY AND DIGITAL SAFETY for the Picture Model Training Kit (the owner's request of 2026-11-22). This
file lists:
  - the ready-made packs built in packs/privacy_packs.py and packs/synthetic_scams_packs.py (group "permissive"; the
    kit downloads them with prepare_pack): commons_privacy_security, commons_privacy_screens and
    synthetic_scam_examples;
  - the share-alike Commons files of the security-device categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (PRIVACY_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it (the packs from the kit's own release),
only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, or, for the computer-made examples, the
facts the generator drew), and end with the plain safety notes that fit: report scams (ReportFraud.ftc.gov, 7726,
ic3.gov), check with the company yourself, never share codes, router and camera settings, ransomware and so on. The
notes are the same words as the packs' (packs/test_privacy.py checks). DEFENSIVE ONLY: the computer-made scam examples
use made-up names, ".example" addresses and 555-01xx numbers, each marked EXAMPLE, and show the warning signs.

Picture-making (PRIVACY_PICTURE_MAKING_OK): only the Commons security devices (things) and their share-alike files;
sources.py puts every other key in NOT_FOR_PICTURE_MAKING (never the scam examples or the screenshots: a model must
never learn to draw convincing scams or sign-in pages).
Topic: privacy (Privacy, security and digital safety).

    python -c "import sources, privacy_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The notes, word for word as in packs/privacy_packs.py and packs/synthetic_scams_packs.py.
VERIFY_NOTE = ("Check it yourself: contact the company or person using a phone number or website you already know is "
               "real, not one given in the message.")
REPORT_NOTE = ("Report scams to the FTC at ReportFraud.ftc.gov; forward scam texts to 7726 (SPAM); report internet "
               "crime to the FBI at ic3.gov.")
CODE_NOTE = ("Never share a verification code with anyone who contacts you; a real company will not ask you to read "
             "it back.")
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

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def device(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# The device categories of packs/privacy_packs.py whose files need no word filter (the share-alike entry has none);
# the screenshots (phishing, sign-in pages, ransomware) are left out of the share-alike entry on purpose.
PRIVACY_SA = [
    device("YubiKey", "a YubiKey, a hardware security key: you plug it in or tap it to prove it is you when you sign "
                      "in", KEY_NOTE),
    device("RSA SecurID", "an RSA SecurID token, a small device that shows a new sign-in code every minute",
           CODE_NOTE),
    device("Smart cards", "a smart card, a card with a chip that holds keys or identity for signing in or paying"),
    device("Fingerprint scanners", "a fingerprint scanner, which unlocks a device or account with your fingerprint",
           BIO_NOTE, True),
    device("Webcam covers", "a webcam cover, a small slide or sticker that blocks a computer's camera when it is not "
                            "in use", "", True),
    device("Wi-Fi routers and access points", "a Wi-Fi router or access point, which runs a home or office wireless "
                                              "network", ROUTER_NOTE),
    device("IP cameras", "an IP camera, a security camera that connects to a network or the internet", CAMERA_NOTE,
           True),
    device("Security cameras", "a security camera (CCTV camera), which records video of a place"),
    device("Skimming (fraud)", "a card skimmer, a hidden device criminals fit to card readers to copy cards",
           f"{SKIM_NOTE} {REPORT_NOTE}"),
]


def prepare_privacy_commons_sa(source, data_dir, work, cap):
    """Commons security key, code token, smart card, fingerprint scanner, webcam cover, router, camera and card
    skimmer categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(PRIVACY_SA, cap, source.test, "privacy-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

PRIVACY_SOURCES = [
    Source("commons_privacy_security", "Security and privacy things: YubiKeys and security keys, code tokens, smart "
                                       "cards, fingerprint scanners, webcam covers, Wi-Fi routers, home and security "
                                       "cameras, smart home devices, door access systems, card skimmers and "
                                       "keyloggers, with safety notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_privacy_screens", "Security screens and tools: phishing and scam messages, HTTPS and padlock "
                                      "icons, ransomware notes, reCAPTCHA, sign-in screens, authenticator and password "
                                      "manager apps, VeraCrypt, GnuPG, the Tor Browser and Signal, with safety and "
                                      "reporting notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 120 MB"),
    Source("synthetic_scam_examples", "Scam and safe message examples, computer-made with made-up names, .example web "
                                      "addresses and 555-01xx numbers, each marked EXAMPLE: scam texts, phishing "
                                      "emails, fake virus pop-ups and sign-in pages, scam letters and QR stickers, "
                                      "and safe code texts, alerts and browser warnings, with the warning signs "
                                      "(synthetic, ready-made pack)",
           "CC0 (drawn by packs/synthetic_scams_packs.py from a fixed seed; no real message, person or company)",
           "Computer-made by the kit's makers (packs/synthetic_scams_packs.py)", "permissive", 3000, 30, prepare_pack,
           "about 400 MB"),
    Source("privacy_commons_sa", "Wikimedia Commons: YubiKeys, code tokens, smart cards, fingerprint scanners, "
                                 "webcam covers, Wi-Fi routers, IP and security cameras and card skimmers, files "
                                 "under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 10, prepare_privacy_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons security devices (things) only; never the
# screenshots (phishing, sign-in pages, ransomware) or the computer-made scam examples.
PRIVACY_PICTURE_MAKING_OK = {"commons_privacy_security", "privacy_commons_sa"}

PRIVACY_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Routers, Smart speakers, Amazon Echo, Google Home and Paper "
        "shredders (device_packs), Webcams, Modems and Hard disk drives (things_packs), Error messages and the "
        "CAPTCHA screenshots (everyday_extras_packs), Padlocks (hardware_packs, home_packs): not asked twice.",
    "Commons categories that do not exist or hold no files (November 2026)": "Security keys, Security tokens, "
        "Hardware security keys, Titan Security Key, Nitrokey, Privacy screens, Privacy filters, Wi-Fi routers, "
        "Authenticator apps, Two-factor authentication, Passkeys, One-time passwords, Password managers, Encryption, "
        "Phishing emails, Email spam, Spam, Tech support scams, Scareware, Video doorbells, Surveillance cameras, "
        "CCTV cameras, Card skimmers, ATM skimmers, Faraday bags, RFID blocking, Kensington locks, Laptop locks, "
        "Hard disk destruction, Data destruction, WannaCry, FileVault, Pretty Good Privacy, Tor (network). The packs "
        "use the categories that hold files.",
    "Commons Scams, Confidence tricksters and Computer security as a whole": "too mixed (portraits of hackers and "
        "tricksters, events, logos, old swindles): only their useful subcategories are used (419 scams, Data "
        "breaches, Evil twin, Keystroke logging, Login, Antivirus software).",
    "Commons Cybersecurity and Infrastructure Security Agency": "mostly photos of events and officials, not "
        "advice pictures; CISA's guidance is in the reference library (books) instead.",
    "Open Images": "no human-checked label is specific to privacy or security (no security key, router, webcam "
        "cover, phishing or padlock label with photos); the general labels (Computer, Laptop, Mobile phone, Camera, "
        "Credit card, Envelope) are asked by other packs or say nothing about safety.",
    "FTC, CISA and FBI consumer pictures": "consumer.ftc.gov refuses programs (403); CISA's and the FBI's pages carry "
        "few pictures, mostly logos and stock photos that are not theirs to share. Their advice is in the reference "
        "library (books), and the computer-made examples teach the same warning signs.",
    "Real phishing emails and scam texts collected from people": "real messages carry real people's names, numbers "
        "and working scam links; only computer-made examples with made-up details are used "
        "(synthetic_scam_examples).",
    "Company help-page pictures (Apple, Google, Microsoft, Meta, security key and password manager makers)": "the "
        "makers' copyright; not used. Their help pages are listed as links in the reference library and the manual "
        "collection privacy_security.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the privacy share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PRIVACY_SOURCES if s.key == "privacy_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="privacy-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
