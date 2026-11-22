"""Pack builder for SCAM AND SAFE MESSAGE EXAMPLES, COMPUTER-MADE (SYNTHETIC) ONLY: made-up scam texts (smishing),
phishing emails, fake virus pop-ups, fake sign-in pages, scam letters and QR-code stickers, beside real-looking SAFE
examples (a verification-code text, an appointment reminder, a new-sign-in alert, the browser's own "connection is
not private" warning, an authenticator app, an update notice). Everything is drawn here with Pillow from a fixed seed
(SEED); nothing is downloaded, and no real message, person or company is copied. Used by build_packs.py in the same
way as its own PACKS: build_synthetic_scam_examples(limit) returns [(file name, JPEG bytes or None, row)], every row
marked "synthetic": true and "example": true. A picture with more than one question comes once with its JPEG and then
again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts
pictures.

Why: the owner is blind and wants his picture describer and offline assistant to help him and others stay safe
online. A sighted person spots a scam by its look (an odd web address, a red "virus" pop-up, a demand for gift
cards); a blind person often meets these as a photo or screenshot that the describer must read and judge. These
examples teach the describer to read the message and to NAME THE WARNING SIGNS it really shows.

DEFENSIVE ONLY, and never usable as a working phishing template:
  - every picture carries a banner "EXAMPLE - made-up message for training. Not real." and every answer says
    "made-up example";
  - every company, agency, person and town is invented here; web addresses are under the reserved ".example"
    domain; phone numbers are in the 555-01xx range set aside for fiction;
  - the scam texts are short, generic and full of the warning signs the answers point out (urgency, threats,
    gift cards, odd addresses): they show what to recognise, not how to deceive.

The questions, each answered from the template's own facts (the generator wrote the picture, so nothing is guessed):
  "What is this?"            the kind of message and who it pretends to be from, said to be a made-up example;
  "What does it say?"        the words on the screen, in reading order;
  "Is this a scam?"          for a scam, the warning signs THIS example shows; for a safe example, the signs it does
                             not show, with the caution that still applies; for the browser's own warning, what it
                             protects you from;
  "What should I do?"        the steps that fit (do not click or call, check with the company yourself, report),
                             ending with the notes below.
The notes (the same words in the kit's privacy_sources.py; packs/test_privacy.py checks):
  VERIFY_NOTE     contact the company or person yourself, with a number or website you already know.
  REPORT_NOTE     ReportFraud.ftc.gov, forward scam texts to 7726 (SPAM), the FBI at ic3.gov.
  ELDER_NOTE      the National Elder Fraud Hotline, 1-833-372-8311.
  GIFT_NOTE       only scammers demand gift cards, wire transfers, payment apps or cryptocurrency (FTC).
  CODE_NOTE       never share a verification code.
  POPUP_NOTE      real security warnings never ask you to call a number (FTC); close the browser.
  PADLOCK_NOTE    a padlock only means the connection is encrypted, not that the site is honest.
  VOICE_NOTE      family code word and call back: voices can be faked with AI.

Never used for picture-making (a model must never learn to draw convincing scams): the kit puts the key in
NOT_FOR_PICTURE_MAKING.

    python packs/synthetic_scams_packs.py synthetic_scam_examples --limit 12 --save some-folder      (a quick check)
"""

import random
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo

SEED = 9311
KIND_Q = "What is this?"
READ_Q = "What does it say?"
SCAM_Q = "Is this a scam?"
DO_Q = "What should I do?"
BANNER = "EXAMPLE - made-up message for training. Not real."
CREDIT = ("A computer-made example drawn with Pillow by packs/synthetic_scams_packs.py (synthetic: made-up names, "
          "companies, web addresses under .example and 555-01xx phone numbers; not a real message), CC0")

# ----------------------------------------------------------------- the notes (the kit uses the same words)

VERIFY_NOTE = ("Check it yourself: contact the company or person using a phone number or website you already know is "
               "real, not one given in the message.")
REPORT_NOTE = ("Report scams to the FTC at ReportFraud.ftc.gov; forward scam texts to 7726 (SPAM); report internet "
               "crime to the FBI at ic3.gov.")
ELDER_NOTE = ("If the person targeted is 60 or older, the National Elder Fraud Hotline can help: 1-833-372-8311 "
              "(1-833-FRAUD-11).")
GIFT_NOTE = ("Anyone who demands payment by gift card, wire transfer, payment app or cryptocurrency is a scammer "
             "(FTC).")
CODE_NOTE = ("Never share a verification code with anyone who contacts you; a real company will not ask you to read "
             "it back.")
POPUP_NOTE = ("Real security warnings from tech companies never ask you to call a phone number (FTC). Close the "
              "browser; if it will not close, restart the computer, and do not call the number.")
PADLOCK_NOTE = ("A padlock or \"https\" only means the connection is encrypted; it does not prove the site is "
                "honest. Check the web address itself.")
VOICE_NOTE = ("Scammers can fake a loved one's voice with AI: agree on a family code word, and hang up and call the "
              "person back on a number you know.")
NOTES = (VERIFY_NOTE, REPORT_NOTE, ELDER_NOTE, GIFT_NOTE, CODE_NOTE, POPUP_NOTE, PADLOCK_NOTE, VOICE_NOTE)

# ----------------------------------------------------------------- made-up names

FIRST = ("Maria", "James", "Aisha", "Wei", "Daniel", "Priya", "Robert", "Fatima", "Carlos", "Linda", "Kwame", "Sofia",
         "Thomas", "Mei", "Olivia", "Ahmed", "Grace", "Luis", "Hannah", "Samuel", "Nadia", "George", "Yuki", "Ruth")
LAST = ("Alvarez", "Brennan", "Okafor", "Lindqvist", "Marchetti", "Haddad", "Novak", "Pereira", "Tanaka", "Whitlow",
        "Osei", "Kowalski", "Delacroix", "Fenwick", "Iqbal", "Moreau", "Castellano", "Ashby", "Nakamura", "Quinlan")
GRANDKIDS = ("Tyler", "Emma", "Jordan", "Chloe", "Ethan", "Ava", "Noah", "Lily")
BANKS = ("Harborview Community Bank", "Lakeshore Savings Union", "Northfield Trust", "Bluewater Credit Union")
COURIERS = ("SwiftParcel", "Parcelwise Delivery", "RapidRoute Post", "Hometown Courier")
STORES = ("MegaMart", "ShopRidge", "Brightway Stores", "Corner Market Online")
SOFTWARE = ("ShieldPro Antivirus", "SecureNest Protection", "GuardWave Security")
TOLLS = ("State Toll Services", "Turnpike Billing Center", "Express Lanes Customer Service")
AGENCIES = ("National Benefits Office", "Federal Revenue Bureau", "Office of Social Payments")
CLINICS = ("Lakeside Family Clinic", "Riverbend Health Center", "Maple Street Dental")
CRYPTO = ("CoinHarbor", "BitSummit Trade", "NovaChain Markets")


def slug(name):
    """ "harborviewcommunitybank" from "Harborview Community Bank" (for made-up .example addresses)."""
    return "".join(c for c in name.lower() if c.isalnum())


def phone(rng, prefix="1-800"):
    """A made-up phone number in the 555-01xx range set aside for fiction."""
    return f"{prefix}-555-01{rng.randint(0, 99):02d}"


def money(rng, low, high, cents=True):
    """ "$12.95" (or "$300" without cents), a made-up amount."""
    value = rng.randint(low, high)
    return f"${value}.{rng.choice((0, 49, 95, 99)):02d}" if cents else f"${value:,}"


# ----------------------------------------------------------------- the templates

def template(rng, kind):
    """The made-up facts of one example of kind: a dict with "frame" (text, chat, email, popup, browser, letter,
    sign, app, notice), "words" (what it is), "sender", "subject", "lines" (the body), "verdict" (scam, safe or
    warning), "signs" (the warning signs it shows, or for a safe one the good signs), "steps" (what to do) and
    "notes" (the notes that fit)."""
    first, last = rng.choice(FIRST), rng.choice(LAST)
    bank, courier, store = rng.choice(BANKS), rng.choice(COURIERS), rng.choice(STORES)
    d = {"kind": kind, "subject": "", "steps": [], "notes": [VERIFY_NOTE, REPORT_NOTE]}
    if kind == "delivery_text":
        fee = money(rng, 1, 4)
        link = f"https://{slug(courier)}-redelivery-{rng.randint(10, 99)}.example/pay"
        d.update(frame="text", sender=phone(rng, f"+1 {rng.choice(('305', '646', '213', '512'))}")[3:],
                 words=f"a text message that pretends to be from a delivery company ({courier})",
                 lines=[f"{courier}: Your package {rng.randint(1000000, 9999999)} is on hold due to an unpaid "
                        f"delivery fee of {fee}.", f"Pay within 24 hours or it will be returned: {link}"],
                 verdict="scam",
                 signs=["it came out of the blue about a package", f"it asks for a small fee ({fee}) to release "
                        "it", "it gives a 24-hour deadline", f"the link ({link}) is not the delivery company's own "
                        "web address", "it comes from an ordinary phone number, not the company"],
                 steps=["Do not tap the link or reply.", "If you are expecting a parcel, track it on the delivery "
                        "company's own app or website."])
    elif kind == "bank_text":
        link = f"http://{slug(bank)[:10]}-verify.example"
        d.update(frame="text", sender=phone(rng, "+1 202")[3:],
                 words=f"a text message that pretends to be from a bank ({bank})",
                 lines=[f"ALERT: Your {bank} account has been LOCKED due to suspicious activity.",
                        f"Verify your identity now at {link} or your account will be closed."],
                 verdict="scam",
                 signs=["it tries to scare you (account locked, account closed)", "it asks you to \"verify your "
                        "identity\" through a link", f"the link ({link}) is not the bank's own web address and "
                        "starts with http, not https", "it is urgent (\"now\")"],
                 steps=["Do not tap the link.", "Call the bank on the number on the back of your card, or open its "
                        "own app, to check your account."])
    elif kind == "toll_text":
        toll, amount = rng.choice(TOLLS), money(rng, 3, 12)
        link = f"https://tollpay-{rng.randint(100, 999)}.example"
        d.update(frame="text", sender=phone(rng, "+1 415")[3:],
                 words=f"a text message about an unpaid road toll that pretends to be from \"{toll}\"",
                 lines=[f"{toll}: You have an unpaid toll balance of {amount}.",
                        f"To avoid a late fee of $50 and loss of your licence, pay today: {link}"],
                 verdict="scam",
                 signs=[f"it asks you to pay a small toll ({amount}) through a link", "it threatens a late fee and "
                        "the loss of your licence", "it says to pay today", f"the link ({link}) is not a toll "
                        "agency's own web address"],
                 steps=["Do not tap the link.", "Check your toll account on the toll agency's own website or "
                        "phone number."])
    elif kind == "wrong_number_text":
        stranger = f"{rng.choice(FIRST)}"
        d.update(frame="chat", sender=phone(rng, "+1 917")[3:],
                 words="a text message from a stranger that looks like a wrong number",
                 lines=[f"Hi {rng.choice(FIRST)}, is this still your number? It's {stranger} from the yoga class :)",
                        "Oh sorry, wrong number! You seem nice though. Where are you from?"],
                 verdict="scam",
                 signs=["a stranger texts a name that is not yours", "after \"wrong number\" they keep chatting to "
                        "make friends", "this is how many romance and investment (cryptocurrency) scams start"],
                 steps=["Do not reply; block the number and delete the message.", "Never send money or invest "
                        "because someone you met by text or online tells you to."])
    elif kind == "code_request_text":
        d.update(frame="chat", sender=phone(rng, "+1 718")[3:],
                 words="a text message asking you to send back a verification code",
                 lines=["Hi! Sorry, I accidentally put your number in when I signed up. You'll get a 6-digit code "
                        "in a minute.", "Can you send it back to me? It's really urgent, thanks!!"],
                 verdict="scam",
                 signs=["a stranger asks you to send them a verification code", "a code sent to your phone is for "
                        "your own account, and whoever gets it can take the account over", "they say it is urgent"],
                 steps=["Do not send the code to anyone.", "If you get a code you did not ask for, ignore it; if "
                        "it keeps happening, change that account's password."],
                 notes=[CODE_NOTE, REPORT_NOTE])
    elif kind == "new_number_text":
        relative = rng.choice(("Mom", "Dad", "Grandma", "Auntie"))
        d.update(frame="chat", sender=phone(rng, "+1 312")[3:],
                 words="a text message from someone claiming to be a family member with a new number",
                 lines=[f"Hi {relative}, it's me. I dropped my phone in water so this is my new number.",
                        f"Can you do me a favour? I need to pay a bill of {money(rng, 400, 1800)} today and my bank "
                        "app isn't working. I'll pay you back tomorrow."],
                 verdict="scam",
                 signs=["a \"new number\" with no name, claiming to be family", "a request for money the same day",
                        "an excuse why they cannot pay themselves"],
                 steps=["Do not send money.", "Call the family member on the number you already have for them, or "
                        "ask a question only they would know."],
                 notes=[VOICE_NOTE, VERIFY_NOTE, REPORT_NOTE])
    elif kind == "grandparent_text":
        kid = rng.choice(GRANDKIDS)
        d.update(frame="chat", sender=phone(rng, "+1 602")[3:],
                 words="a text message that claims to be a grandchild in trouble (a grandparent scam)",
                 lines=[f"Grandma it's {kid}. I'm in trouble, I was in a car accident and I'm in jail. Please "
                        "don't tell Mom and Dad.", f"I need {money(rng, 2, 9, False)},000 for bail. My lawyer will "
                        "call you. He says you can pay with gift cards or give cash to a courier."],
                 verdict="scam",
                 signs=["an emergency that needs money at once", "it asks you to keep it secret from the family",
                        "it asks for gift cards or cash handed to a courier", "it comes from a number you do not "
                        "know"],
                 steps=["Do not send money, gift cards or cash.", "Hang up or stop replying, then call your "
                        "grandchild or their parents on a number you know."],
                 notes=[GIFT_NOTE, VOICE_NOTE, ELDER_NOTE, REPORT_NOTE])
    elif kind == "crypto_chat":
        platform = rng.choice(CRYPTO)
        link = f"https://{slug(platform)}-invest.example"
        d.update(frame="chat", sender=f"{rng.choice(FIRST)} (met on a dating app)",
                 words=f"a chat message from an online friend pushing a cryptocurrency investment ({platform})",
                 lines=["I made 40% last month on this crypto trading site, it's guaranteed!",
                        f"Let me help you start, just deposit $500 at {link} and I'll show you."],
                 verdict="scam",
                 signs=["someone you met online is pushing an investment", "it promises big, \"guaranteed\" "
                        "returns", f"it sends you to an unknown trading site ({link})"],
                 steps=["Do not deposit money or send cryptocurrency.", "Stop chatting with anyone who asks you to "
                        "invest."],
                 notes=[GIFT_NOTE, VERIFY_NOTE, REPORT_NOTE])
    elif kind == "prize_email":
        link = f"https://claim-{slug(store)}-reward.example"
        d.update(frame="email", sender=f"{store} Rewards <winner@{slug(store)}-prizes.example>",
                 subject="Congratulations!!! You have WON",
                 words=f"an email that says you have won a prize from a shop ({store})",
                 lines=["Dear Customer,", f"You have been selected to receive a $1,000 {store} gift card!",
                        f"Claim it now - you pay only {money(rng, 3, 9)} shipping: {link}",
                        "This offer expires in 2 hours."],
                 verdict="scam",
                 signs=["you won a prize you never entered", "you must pay to get the prize", "the greeting is "
                        "\"Dear Customer\", not your name", "it expires in 2 hours", f"the link ({link}) is not the "
                        "shop's own address"],
                 steps=["Do not click the link or pay anything.", "Delete the email or mark it as spam."])
    elif kind == "password_email":
        org = f"{rng.choice(('Greenfield', 'Westbrook', 'Oakridge', 'Pinecrest'))} {rng.choice(('School', 'Library', 'Office', 'Council'))}"
        d.update(frame="email", sender=f"IT Helpdesk <support@mail-{rng.randint(100, 999)}.example>",
                 subject="Your mailbox password expires today",
                 words="an email that pretends to be from an IT helpdesk about a password",
                 lines=["Dear user,", f"Your {org} mailbox password will expire today and you will not recieve "
                        "new messages.", "To keep your current password, click here and sign in: "
                        f"https://{slug(org)}-mail-login.example", "IT Helpdesk"],
                 verdict="scam",
                 signs=["it says your password expires today (pressure)", "it asks you to sign in through a link",
                        "the sender's address is not your organisation's", "the greeting is \"Dear user\"",
                        "it has a spelling mistake (\"recieve\")"],
                 steps=["Do not click the link or type your password.", "Ask your organisation's IT helpdesk "
                        "directly, using the contact details you already have."])
    elif kind == "renewal_email":
        product, amount, number = rng.choice(SOFTWARE), money(rng, 299, 499), phone(rng, "1-888")
        d.update(frame="email", sender=f"Billing <billing@{slug(product)[:8]}-invoice.example>",
                 subject=f"Order confirmed: {product} renewal",
                 words=f"an email about a subscription renewal that pretends to be from \"{product}\"",
                 lines=[f"Thank you! Your {product} subscription has renewed for {amount}.",
                        f"If you did not authorise this payment, call our refund desk at {number} within 24 hours.",
                        f"Invoice number {rng.randint(100000, 999999)}"],
                 verdict="scam",
                 signs=[f"an unexpected charge for a large amount ({amount})", "it pushes you to call the number "
                        "in the email", "it gives a 24-hour deadline"],
                 steps=["Do not call the number in the email.", "Check your bank or card statement yourself; if "
                        "there is a charge you do not know, call the number on your card."],
                 notes=[POPUP_NOTE, VERIFY_NOTE, REPORT_NOTE])
    elif kind == "boss_email":
        boss = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        d.update(frame="email", sender=f"{boss} <{slug(boss)}.office@freemail.example>",
                 subject="Quick favour - are you at your desk?",
                 words="an email that pretends to be from your boss, asking for gift cards",
                 lines=[f"Hi {first},", f"I'm in a meeting and need you to buy 5 {store} gift cards of $200 each "
                        "for a client.", "Scratch off the backs and send me photos of the codes. Keep this between "
                        f"us for now.", f"Thanks, {boss}"],
                 verdict="scam",
                 signs=["it asks for gift cards and photos of their codes", "it asks you to keep it secret",
                        "it comes from a free email address, not a work address", "the sender says they cannot "
                        "talk (\"in a meeting\")"],
                 steps=["Do not buy gift cards or send codes.", "Speak to your boss in person or call them on a "
                        "number you know."],
                 notes=[GIFT_NOTE, VERIFY_NOTE, REPORT_NOTE])
    elif kind == "agency_letter":
        agency, number = rng.choice(AGENCIES), phone(rng, "1-202")
        d.update(frame="letter", sender=agency,
                 subject="FINAL NOTICE",
                 words=f"a letter that pretends to be from a government office (\"{agency}\", a made-up name)",
                 lines=[f"Dear {first} {last},", "Your benefits will be SUSPENDED due to suspicious activity on "
                        "your account.", f"Call {number} immediately to avoid arrest.",
                        "A reinstatement fee of $250 must be paid today by gift card or cryptocurrency."],
                 verdict="scam",
                 signs=["it threatens to suspend your benefits and to arrest you", "it demands a fee by gift card "
                        "or cryptocurrency", "it says \"immediately\" and \"today\"", "it gives its own number to "
                        "call"],
                 steps=["Do not call the number or pay.", "Contact the real government office using the number "
                        "on its official website or on letters you know are real."],
                 notes=[GIFT_NOTE, VERIFY_NOTE, ELDER_NOTE, REPORT_NOTE])
    elif kind == "tech_popup":
        number = phone(rng, "1-844")
        brand = rng.choice(("System Security Center", "Device Protection Alert", "Windows Safety Check"))
        d.update(frame="popup", sender=brand, subject="WARNING! VIRUS DETECTED",
                 words=f"a fake virus warning (pop-up) on a web page, calling itself \"{brand}\"",
                 lines=[f"Your computer is infected with {rng.randint(3, 9)} viruses!", "Your files, photos and "
                        "passwords are at risk.", "DO NOT CLOSE THIS WINDOW OR RESTART YOUR COMPUTER.",
                        f"Call Support now: {number}"],
                 verdict="scam",
                 signs=["a web page says your computer is infected", "it tells you to call a phone number",
                        "it tells you not to close the window or restart", "it uses capital letters and alarm to "
                        "scare you"],
                 steps=["Do not call the number and do not let anyone connect to your computer.", "Close the "
                        "browser; if it will not close, restart the computer."],
                 notes=[POPUP_NOTE, REPORT_NOTE])
    elif kind == "fake_login":
        link = f"https://{slug(bank)[:12]}-secure-login.example/signin"
        d.update(frame="browser", sender=link, subject=f"{bank} - Online Banking",
                 words=f"a fake bank sign-in page (it pretends to be {bank}) with a padlock in the address bar",
                 lines=["Sign in to Online Banking", "Username", "Password", "Card PIN", "Full Social Security "
                        "number", "Sign in"],
                 verdict="scam",
                 signs=[f"the web address ({link}) is not the bank's own", "it asks for your card PIN and full "
                        "Social Security number, which a sign-in page never needs", "the padlock does not make it "
                        "safe"],
                 steps=["Do not type anything into this page.", "Type the bank's address yourself, or use its own "
                        "app."],
                 notes=[PADLOCK_NOTE, VERIFY_NOTE, REPORT_NOTE])
    elif kind == "qr_sticker":
        link = f"pay-parking-{rng.randint(10, 99)}.example"
        d.update(frame="sign", sender="Parking", subject="PAY HERE",
                 words="a parking sign with a QR-code sticker stuck on it",
                 lines=["PAY FOR PARKING", "Scan to pay", f"Sticker: QR code - {link}", "Zone 4021"],
                 verdict="scam",
                 signs=["the QR code is a sticker stuck over the sign", f"the address printed with it ({link}) is "
                        "not a city or parking company website"],
                 steps=["Do not scan the sticker.", "Pay at the meter or with the parking company's own app."])
    elif kind == "overpay_message":
        item = rng.choice(("sofa", "bicycle", "dining table", "lawn mower"))
        d.update(frame="chat", sender=f"Buyer {rng.choice(FIRST)} (marketplace)",
                 words=f"a marketplace message from a buyer who wants to overpay for a {item}",
                 lines=[f"I'll take the {item}! I'm sending a cheque for $1,500 instead of $500 because my mover "
                        "needs the rest.", "When it arrives please wire the extra $1,000 to my "
                        "mover. Thanks!"],
                 verdict="scam",
                 signs=["the buyer sends more than the price", "they ask you to send the extra money back by wire",
                        "the cheque can bounce days later, after you have sent real money"],
                 steps=["Do not accept the overpayment or send money back.", "Sell only for the exact price, paid "
                        "in a way you trust."],
                 notes=[GIFT_NOTE, REPORT_NOTE])
    elif kind == "job_text":
        d.update(frame="text", sender=phone(rng, "+1 469")[3:],
                 words="a text message offering a work-from-home job",
                 lines=["Hi, we saw your resume! Remote job: $900/week for 1 hour a day, reshipping packages.",
                        f"Pay {money(rng, 49, 99)} for your starter kit to begin: https://jobs-{rng.randint(10, 99)}.example"],
                 verdict="scam",
                 signs=["a job offer you did not apply for", "high pay for little work", "you must pay to start",
                        "reshipping packages can make you part of a crime"],
                 steps=["Do not pay or reply.", "Look for jobs only through employers and job sites you trust."])
    # ---- safe and genuine examples
    elif kind == "safe_code_text":
        code = f"{rng.randint(100000, 999999)}"
        d.update(frame="text", sender=f"{bank}", words=f"a verification-code text message from {bank}",
                 lines=[f"{bank}: Your verification code is {code}. It expires in 10 minutes.",
                        f"{bank} will never call or text to ask for this code. Do not share it."],
                 verdict="safe",
                 signs=["it has no link to tap", "it does not ask you to call anyone", "it says never to share the "
                        "code"],
                 caution="use the code only if you just asked for it yourself, and only type it into the bank's "
                         "own app or website; never read it to anyone who calls",
                 steps=["If you just signed in, type the code into the bank's own app or site.", "If you did not "
                        "ask for a code, ignore it and do not share it."],
                 notes=[CODE_NOTE])
    elif kind == "safe_appointment":
        clinic = rng.choice(CLINICS)
        d.update(frame="text", sender=clinic, words=f"an appointment reminder text from {clinic}",
                 lines=[f"{clinic}: Reminder of your appointment on {rng.choice(('Tue', 'Wed', 'Thu', 'Fri'))} "
                        f"{rng.randint(2, 27)} {rng.choice(('March', 'April', 'May', 'June'))} at "
                        f"{rng.randint(8, 16)}:{rng.choice(('00', '15', '30', '45'))}.",
                        "Reply C to confirm. Questions? Call the number on your clinic card."],
                 verdict="safe",
                 signs=["it has no link", "it asks for no money or personal details", "it tells you to use the "
                        "number you already have"],
                 caution="if a reminder ever asks for payment, card numbers or a link to \"confirm\", treat it "
                         "with suspicion",
                 steps=["If the appointment is yours, you can reply C or call the clinic on the number you "
                        "already have."], notes=[VERIFY_NOTE])
    elif kind == "safe_signin_alert":
        d.update(frame="email", sender=f"{bank} <alerts@{slug(bank)}.example>", subject="New sign-in to your account",
                 words=f"an email alert about a new sign-in, from {bank}",
                 lines=[f"Hello {first},", "We noticed a sign-in to your account from a new device.",
                        "If this was you, you don't need to do anything.", f"If not, open the {bank} app or type "
                        f"{slug(bank)}.example yourself to change your password.", "We will never ask for your "
                        "password, PIN or codes by email."],
                 verdict="safe",
                 signs=["it uses your name", "it has no link or button to click", "it tells you to open the app or "
                        "type the address yourself", "it asks for nothing"],
                 caution="check the sender's address too, and if you are unsure, open the bank's app yourself "
                         "rather than replying",
                 steps=["If the sign-in was not you, open the bank's own app or type its address yourself and "
                        "change your password."], notes=[VERIFY_NOTE])
    elif kind == "browser_warning":
        site = f"{rng.choice(('mail', 'shop', 'news', 'portal'))}.{slug(store)}.example"
        d.update(frame="warning", sender="Web browser", subject="Your connection is not private",
                 words="the web browser's own security warning (\"Your connection is not private\")",
                 lines=["Your connection is not private", f"Attackers might be trying to steal your information "
                        f"from {site} (for example, passwords, messages or credit cards).",
                        "NET::ERR_CERT_DATE_INVALID", "Advanced", "Back to safety"],
                 verdict="warning",
                 signs=["the browser could not check the site's security certificate, so the connection may not "
                        "be private"],
                 caution="press \"Back to safety\"; do not type passwords or card numbers on that site",
                 steps=["Press \"Back to safety\".", "Do not enter passwords or card details on that site; try "
                        "again later, or check that your computer's date and time are right."], notes=[PADLOCK_NOTE])
    elif kind == "authenticator":
        code = f"{rng.randint(100, 999)} {rng.randint(100, 999)}"
        d.update(frame="app", sender="Example Authenticator",
                 words="an authenticator app showing a sign-in code",
                 lines=[f"{bank}", f"{first.lower()}.{last.lower()}@mail.example", code,
                        f"Refreshes in {rng.randint(3, 29)} seconds"],
                 verdict="safe",
                 signs=["it is an app on your own phone, not a message from someone else", "the code changes every "
                        "30 seconds"],
                 caution="type the code only into the site or app you are signing in to yourself; never read it "
                         "to anyone who calls or texts",
                 steps=["Use the code only when you are signing in yourself."], notes=[CODE_NOTE])
    elif kind == "update_notice":
        d.update(frame="notice", sender="Settings - Software update",
                 words="a software update notice from the computer's own settings",
                 lines=["Updates are available", "Security update for your device (version "
                        f"{rng.randint(10, 15)}.{rng.randint(0, 9)}.{rng.randint(1, 9)})",
                        "Restart now", "Schedule the restart"],
                 verdict="safe",
                 signs=["it is in the device's own settings, not a web page", "it asks for no money, phone call or "
                        "personal details"],
                 caution="install updates from the device's own settings; an \"update\" offered by a pop-up on a "
                         "web page is not safe",
                 steps=["Save your work and restart to install the update; updates fix security holes."],
                 notes=[])
    else:
        raise ValueError(kind)
    return d


SCAM_KINDS = ("delivery_text", "bank_text", "toll_text", "wrong_number_text", "code_request_text", "new_number_text",
              "grandparent_text", "crypto_chat", "prize_email", "password_email", "renewal_email", "boss_email",
              "agency_letter", "tech_popup", "fake_login", "qr_sticker", "overpay_message", "job_text")
SAFE_KINDS = ("safe_code_text", "safe_appointment", "safe_signin_alert", "browser_warning", "authenticator",
              "update_notice")
KINDS = SCAM_KINDS + SAFE_KINDS


def details(n, seed=SEED):
    """The made-up facts of the n-th example: about two in three are scams, the rest safe or genuine warnings."""
    rng = random.Random(f"{seed}-{n}")
    kinds = SCAM_KINDS if n % 3 else SAFE_KINDS
    d = template(rng, kinds[(n // 3) % len(kinds)] if rng.random() < 0.5 else rng.choice(kinds))
    d["rng"] = rng
    return d


# ----------------------------------------------------------------- drawing

def wrap(draw, text, fnt, width):
    """text cut into lines that fit width pixels."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit(draw, text, size, bold, kind, width):
    """The font of size (or smaller, down to 14 pixels) in which text fits width pixels: nothing is cut off."""
    while size > 14 and draw.textlength(text, font=font(size, bold, kind)) > width:
        size -= 1
    return font(size, bold, kind)


def banner(draw, width):
    """The EXAMPLE banner across the top of every picture, its words always whole."""
    draw.rectangle([0, 0, width, 54], fill=(255, 214, 0))
    draw.text((20, 12), BANNER, font=fit(draw, BANNER, 28, True, 0, width - 40), fill=(0, 0, 0))


def draw_example(d):
    """The picture of an example's facts (a PIL image)."""
    from PIL import Image, ImageDraw
    rng = d["rng"]
    dark = rng.random() < 0.25
    paper, ink = ((24, 24, 28), (235, 235, 235)) if dark else ((255, 255, 255), (20, 20, 20))
    frame = d["frame"]
    kind_font = rng.randrange(6)
    body, bold, small = font(30, False, kind_font), font(32, True, kind_font), font(24, False, kind_font)
    if frame in ("text", "chat", "app"):                           # a phone screen
        width, height = 760, 1400
        page = Image.new("RGB", (width, height), paper)
        draw = ImageDraw.Draw(page)
        banner(draw, width)
        draw.text((30, 70), f"{rng.randint(1, 12)}:{rng.randint(0, 59):02d}", font=small, fill=ink)
        if frame == "app":
            draw.text((30, 130), d["sender"], font=bold, fill=ink)
            draw.rectangle([30, 200, width - 30, 520], outline=(120, 120, 120), width=3)
            draw.text((60, 230), d["lines"][0], font=fit(draw, d["lines"][0], 32, True, kind_font, width - 150),
                      fill=ink)
            draw.text((60, 280), d["lines"][1], font=small, fill=ink)
            draw.text((60, 330), d["lines"][2], font=fit(draw, d["lines"][2], 84, True, kind_font, width - 150),
                      fill=(30, 110, 220))
            draw.text((60, 460), d["lines"][3], font=small, fill=ink)
            return page
        draw.text((30, 130), d["sender"], font=bold, fill=ink)
        draw.text((30, 175), "Text Message" if frame == "text" else "Chat", font=small, fill=(130, 130, 130))
        y = 240
        bubble = (60, 60, 66) if dark else (229, 229, 234)
        for line in d["lines"]:
            rows = wrap(draw, line, body, width - 140)
            h = len(rows) * 40 + 30
            draw.rounded_rectangle([30, y, width - 70, y + h], radius=26, fill=bubble)
            for i, row in enumerate(rows):
                draw.text((55, y + 15 + i * 40), row, font=body, fill=ink)
            y += h + 24
        draw.rounded_rectangle([30, height - 110, width - 30, height - 40], radius=30, outline=(150, 150, 150),
                               width=2)
        draw.text((60, height - 92), "Text Message", font=small, fill=(150, 150, 150))
        return page
    if frame in ("email", "letter"):
        width, height = 1240, 1000 if frame == "email" else 1500
        page = Image.new("RGB", (width, height), paper if frame == "email" else (252, 250, 244))
        draw = ImageDraw.Draw(page)
        ink = ink if frame == "email" else (20, 20, 20)
        banner(draw, width)
        y = 90
        if frame == "email":
            draw.text((40, y), f"From: {d['sender']}", font=small, fill=ink)
            draw.text((40, y + 40), f"Subject: {d['subject']}", font=bold, fill=ink)
            draw.line([(40, y + 95), (width - 40, y + 95)], fill=(160, 160, 160), width=2)
            y += 130
        else:
            draw.text((60, y + 20), d["sender"].upper(), font=fit(draw, d["sender"].upper(), 44, True, kind_font,
                                                                  width - 120), fill=(20, 40, 110))
            draw.text((60, y + 100), d["subject"], font=font(40, True, kind_font), fill=(180, 0, 0))
            y += 190
        for line in d["lines"]:
            for row in wrap(draw, line, body, width - 120):
                draw.text((60, y), row, font=body, fill=ink)
                y += 42
            y += 18
        return page
    if frame in ("popup", "browser", "warning", "notice"):
        width, height = 1280, 860
        page = Image.new("RGB", (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(page)
        banner(draw, width)
        draw.rectangle([0, 54, width, 130], fill=(222, 222, 226))
        address = d["sender"] if frame == "browser" else (
            f"https://{rng.choice(('free-movies', 'best-deals', 'news-today'))}{rng.randint(1, 99)}.example"
            if frame == "popup" else "")
        if address:
            draw.rounded_rectangle([110, 70, width - 40, 116], radius=20, fill=(255, 255, 255))
            if frame == "browser":                         # the padlock the answer speaks of
                draw.rectangle([128, 92, 146, 108], fill=(80, 80, 80))
                draw.arc([130, 78, 144, 98], 180, 360, fill=(80, 80, 80), width=3)
            draw.text((160, 78), address, font=small, fill=(20, 20, 20))
        if frame == "popup":
            draw.rectangle([140, 170, width - 140, height - 60], fill=(190, 0, 0))
            draw.text((180, 200), d["subject"], font=fit(draw, d["subject"], 52, True, kind_font, width - 380),
                      fill=(255, 255, 255))
            draw.text((180, 270), d["sender"], font=small, fill=(255, 230, 230))
            y = 330
            for line in d["lines"]:
                for row in wrap(draw, line, bold, width - 380):
                    draw.text((180, y), row, font=bold, fill=(255, 255, 255))
                    y += 46
                y += 14
        elif frame == "browser":
            draw.text((width // 2 - 260, 170), d["subject"], font=fit(draw, d["subject"], 40, True, kind_font, 760),
                      fill=(20, 60, 140))
            y = 250
            for label in d["lines"][1:-1]:
                draw.text((width // 2 - 260, y), label, font=small, fill=(20, 20, 20))
                draw.rectangle([width // 2 - 260, y + 32, width // 2 + 260, y + 80], outline=(120, 120, 120),
                               width=2, fill=(255, 255, 255))
                y += 110
            draw.rectangle([width // 2 - 260, y, width // 2 + 260, y + 56], fill=(20, 60, 140))
            draw.text((width // 2 - 40, y + 12), d["lines"][-1], font=bold, fill=(255, 255, 255))
        elif frame == "warning":
            draw.rectangle([0, 130, width, height], fill=(255, 255, 255) if not dark else (32, 33, 36))
            text_ink = (32, 33, 36) if not dark else (232, 234, 237)
            draw.text((160, 200), "!", font=font(90, True, kind_font), fill=(200, 40, 30))
            draw.text((160, 320), d["lines"][0], font=fit(draw, d["lines"][0], 44, True, kind_font, width - 320),
                      fill=text_ink)
            y = 400
            for row in wrap(draw, d["lines"][1], body, width - 320):
                draw.text((160, y), row, font=body, fill=text_ink)
                y += 42
            draw.text((160, y + 20), d["lines"][2], font=small, fill=(120, 120, 120))
            draw.text((160, y + 110), d["lines"][3], font=bold, fill=(26, 115, 232))
            button = draw.textlength(d["lines"][4], font=bold) + 50
            draw.rounded_rectangle([width - 160 - button, y + 95, width - 160, y + 155], radius=8, fill=(26, 115, 232))
            draw.text((width - 135 - button, y + 108), d["lines"][4], font=bold, fill=(255, 255, 255))
        else:                                              # the device's own update notice
            draw.rectangle([0, 130, width, height], fill=(250, 250, 250))
            draw.text((80, 170), d["sender"], font=small, fill=(90, 90, 90))
            draw.text((80, 230), d["lines"][0], font=font(44, True, kind_font), fill=(20, 20, 20))
            draw.text((80, 310), d["lines"][1], font=fit(draw, d["lines"][1], 30, False, kind_font, width - 160),
                      fill=(20, 20, 20))
            draw.rounded_rectangle([80, 400, 380, 460], radius=8, fill=(0, 103, 192))
            draw.text((110, 412), d["lines"][2], font=bold, fill=(255, 255, 255))
            draw.text((420, 412), d["lines"][3], font=bold, fill=(0, 103, 192))
        return page
    # a sign with a sticker (the QR code is drawn as a pattern of squares: it holds no address)
    width, height = 900, 1300
    page = Image.new("RGB", (width, height), (16, 80, 160))
    draw = ImageDraw.Draw(page)
    banner(draw, width)
    draw.text((80, 120), d["lines"][0], font=fit(draw, d["lines"][0], 64, True, kind_font, width - 160),
              fill=(255, 255, 255))
    draw.text((80, 230), d["lines"][1], font=font(48, True, kind_font), fill=(255, 255, 255))
    draw.rectangle([180, 380, 720, 980], fill=(255, 255, 255))
    for i in range(12):
        for j in range(12):
            if rng.random() < 0.5 or (i < 3 and j < 3) or (i < 3 and j > 8) or (i > 8 and j < 3):
                draw.rectangle([220 + i * 38, 420 + j * 38, 256 + i * 38, 456 + j * 38], fill=(0, 0, 0))
    draw.text((200, 900), d["lines"][2].split(" - ", 1)[1], font=small, fill=(0, 0, 0))
    draw.text((80, 1080), d["lines"][3], font=font(40, False, kind_font), fill=(255, 255, 255))
    return page


# ----------------------------------------------------------------- the rows

def joined(items):
    """ "a, b and c"."""
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def example_rows(d):
    """The question-and-answer rows of one example, from its own made-up facts."""
    shown = [BANNER]
    if d["frame"] in ("text", "chat"):
        shown.append(f"From: {d['sender']}.")
    elif d["frame"] == "email":
        shown += [f"From: {d['sender']}.", f"Subject: {d['subject']}."]
    elif d["frame"] in ("letter", "popup"):
        shown += [d["sender"] + ".", d["subject"] + "."]
    elif d["frame"] == "browser":
        shown += [f"Address bar: {d['sender']} (with a padlock).", d["subject"] + "."]
    elif d["frame"] == "app":
        shown.append(d["sender"] + ".")
    elif d["frame"] == "notice":
        shown.append(d["sender"] + ".")
    shown += [line if line.endswith((".", "!", "?", ":", ",")) else line + "." for line in d["lines"]]
    read = " ".join(shown)
    if d["verdict"] == "scam":
        judge = f"Yes, this made-up example shows the warning signs of a scam: {joined(d['signs'])}."
    elif d["verdict"] == "safe":
        judge = (f"This made-up example shows none of the usual warning signs: {joined(d['signs'])}. Still, "
                 f"{d['caution']}.")
    else:
        judge = (f"No, this is not a scam: it is a made-up example of a real kind of warning, {d['words']}. It "
                 f"means {joined(d['signs'])}. {d['caution'][0].upper()}{d['caution'][1:]}.")
    steps = " ".join(d["steps"] + d["notes"])
    rows = [{"question": KIND_Q, "answer": f"This is a made-up example of {d['words']}, marked EXAMPLE."},
            {"question": READ_Q, "answer": f"It says: {read}"},
            {"question": SCAM_Q, "answer": judge},
            {"question": DO_Q, "answer": steps}]
    return [dict(r, credit=CREDIT, synthetic=True, example=True, verdict=d["verdict"]) for r in rows]


def make_example(n, seed=SEED):
    """The n-th example as (file name, JPEG bytes, rows): a flat screenshot or a phone photo of a screen or paper."""
    d = details(n, seed)
    page = draw_example(d)
    strength = 0.0 if d["rng"].random() < 0.4 else d["rng"].uniform(0.3, 1.0)
    data = phone_photo(page, d["rng"], strength=strength)
    return f"example-{d['kind'].replace('_', '-')}-{n:05d}.jpg", data, example_rows(d)


def build_synthetic_scam_examples(limit):
    """The synthetic_scam_examples pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_example(n) for n in range(limit)])


# ----------------------------------------------------------------- the packs

SYNTHETIC_SCAMS_PACKS = {
    "synthetic_scam_examples": (build_synthetic_scam_examples,
                                "Computer-made (synthetic) examples of scam and safe messages (texts, emails, pop-ups, "
                                "sign-in pages, letters and a QR sticker) drawn with Pillow by "
                                "packs/synthetic_scams_packs.py from a fixed seed: made-up names, companies, .example "
                                "web addresses and 555-01xx phone numbers, each marked EXAMPLE. CC0."),
}
SYNTHETIC_SCAMS_LIMITS = {
    "synthetic_scam_examples": 3000,
}
SYNTHETIC_SCAMS_COMMONS_KEYS = ()


def main(argv=None):
    """Make a few examples and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the synthetic scam examples pack builder.")
    parser.add_argument("key", choices=sorted(SYNTHETIC_SCAMS_PACKS))
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = build_synthetic_scam_examples(args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:300])
        if data and args.save:
            os.makedirs(args.save, exist_ok=True)
            with open(os.path.join(args.save, name), "wb") as f:
                f.write(data)
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
