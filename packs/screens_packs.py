"""Picture pack of COMPUTER AND PHONE SCREENS, computer-made (the owner's request of 2026-11-22: pictures for the
picture describer). Used by build_packs.py in the same way as its own PACKS: build_<key>(limit) returns
[(file name, JPEG bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as
(None, None, row) rows naming the same picture (food_packs.with_twins). The limit counts pictures.

Why: the owner is blind. Screen readers cannot read every screen: a picture sent by a friend, a screenshot in an
email, a kiosk, a frozen computer photographed with a phone, a CAPTCHA, or an app that is not accessible. The
describer must read a screen IN ORDER (the title, the text, the fields, then the buttons), say which button is the
default (drawn highlighted) and which has keyboard focus (the dotted outline), and say what each button does.

The pack (SCREENS_PACKS):
  synthetic_screens  Screens drawn here with Pillow from a fixed seed (SEED), in four GENERIC looks: "a Windows-like
                     computer", "a Mac-like computer", "an Android-like phone" and "an iPhone-like phone". Nothing is
                     copied: no company's logo, icon, typeface or trademarked design is drawn (no window-button
                     colours, no app-store or system icons; plain shapes and the build machine's free fonts), every
                     app, company and person is made up, web addresses are under the reserved ".example" domain and
                     phone numbers in the 555-01xx range set aside for fiction. The kinds (KINDS): OK/Cancel
                     questions, "save changes?", permission prompts (camera, microphone, location, notifications,
                     contacts), error messages, update notices, settings pages with switches, sign-in screens,
                     two-factor code screens, file pickers, printer dialogs, CAPTCHAs (with the accessible way round
                     each one), cookie banners, app store pages, phone lock screens with notifications, and single
                     notification banners. About one picture in four is "photographed" off the screen with a phone
                     (phone_photo.py), the rest are clean screenshots.

Every answer is exact: the generator drew the screen, so it says what is on it and nothing else.
  "What does this screen say?"         everything in reading order, ending with the buttons, the default and focus;
  "What do the buttons do?"            each button and what pressing it does (the generator's own meaning);
  "Which button is selected?"          the default button and the focused one (where the look shows them);
  and questions of the kind ("Which settings are turned on?", "How do I get past this CAPTCHA?", "What is the
  code for?", "What happens if I reject the cookies?" ...).
Safety notes (the same words as synthetic_scams_packs.py, imported, never re-written): CODE_NOTE on two-factor
screens and PADLOCK_NOTE on sign-in screens. Scam screens (fake virus pop-ups, fake sign-in pages, fake update
notices) are NOT drawn again here: they are the synthetic_scam_examples pack (packs/synthetic_scams_packs.py), which
teaches the warning signs; these are ordinary, honest screens.

Real screenshots elsewhere: commons_screens (packs/everyday_extras_packs.py: Commons error messages, dialog boxes,
login and lock screens, CAPTCHAs; only CC0, public domain, CC BY, MIT or Apache files), and the kit's research
entries rico_screens, rico_widgets and screenqa_rico (Android app screens from Rico; personal use). This pack extends
them with what they lack: the order to read in, the default and focused button, and what each button does.
Never used for picture-making (a model must never learn to draw convincing system screens): the kit puts the key in
NOT_FOR_PICTURE_MAKING.

    python packs/screens_packs.py synthetic_screens --limit 12 --save some-folder      (a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo
from synthetic_documents import seeded
from synthetic_scams_packs import CODE_NOTE, PADLOCK_NOTE

SEED = 6421
READ_Q = "What does this screen say?"
BUTTONS_Q = "What do the buttons do?"
SELECTED_Q = "Which button is selected?"
KIND_Q = "What kind of screen is this?"
CREDIT = ("A computer-made screen drawn with Pillow by packs/screens_packs.py (synthetic: generic look, made-up apps, "
          "companies and people, web addresses under .example, 555-01xx phone numbers; not a real program), CC0")
STYLES = ("windows", "mac", "android", "iphone")
STYLE_WORDS = {"windows": "a Windows-like computer", "mac": "a Mac-like computer", "android": "an Android-like phone",
               "iphone": "an iPhone-like phone"}
PHONES = ("android", "iphone")
CAPTCHA_NOTE = ("CAPTCHAs are a known barrier for blind people (W3C, \"Inaccessibility of CAPTCHA\"): look for an "
                "audio challenge or another way to prove you are a person; if there is none, contact the website's "
                "support and ask for another way in.")

# ----------------------------------------------------------------- made-up names

APPS = ("Notewell", "PixelPal Photos", "Brightline Mail", "TaskTide", "Harbor Maps", "Cloudberry Drive",
        "Sunfield Weather", "Quillpad Writer", "Meadow Music", "Lumen Reader", "Chatterbox Messenger",
        "Pocket Ledger", "Riverstone Bank App", "FitTrail", "Orchard Recipes", "Beacon Video Calls")
SITES = ("mapleleafnews.example", "greenmarket.example", "harborview-bank.example", "riverbendlibrary.example",
         "townhall-services.example", "brightwaystores.example", "sunfieldweather.example", "pinecrestclinic.example")
FIRST = ("Maria", "James", "Aisha", "Wei", "Daniel", "Priya", "Robert", "Fatima", "Carlos", "Linda", "Kwame", "Sofia")
LAST = ("Alvarez", "Brennan", "Okafor", "Lindqvist", "Marchetti", "Haddad", "Novak", "Pereira", "Tanaka", "Whitlow")
DOCS = ("Budget 2026", "Letter to landlord", "Meeting notes", "Recipe ideas", "Holiday plans", "Chapter 3 draft",
        "Shopping list", "Club newsletter")
PRINTERS = ("Office Printer (LaserJet-like)", "Kitchen Inkjet", "Library Printer 2", "Save as PDF")
FOLDERS = ("Documents", "Downloads", "Pictures", "Desktop", "Music")
FILES = ("Budget 2026.xlsx", "Letter to landlord.docx", "Holiday photo 01.jpg", "Recipe ideas.txt",
         "Bank statement March.pdf", "Club newsletter.docx", "Scan 0042.pdf", "Garden plan.png", "Song demo.mp3",
         "Tax notes.txt", "Invitation.pdf", "Resume 2026.docx")
PERMISSIONS = {
    "camera": ("take pictures and record video", "The app can use the camera."),
    "microphone": ("record audio", "The app can use the microphone."),
    "location": ("use your location", "The app can see where you are."),
    "notifications": ("send you notifications", "The app can show alerts, sounds and badges."),
    "contacts": ("see your contacts", "The app can read the names and numbers in your contacts."),
}
SETTINGS = ("Wi-Fi", "Bluetooth", "Airplane mode", "Dark theme", "Location services", "Auto-update apps",
            "Screen reader", "Large text", "Notifications sound", "Battery saver", "Mobile data", "Auto-brightness")


def fiction_phone(rng):
    """A made-up phone number in the 555-01xx range set aside for fiction."""
    return f"(555) 555-01{rng.randint(0, 99):02d}"


def b(label, does):
    """One button: its label and what pressing it does."""
    return {"label": label, "does": does}


# ----------------------------------------------------------------- the screens' facts

def details(kind, style, rng):
    """The made-up facts of one screen: a dict with "kind", "style", "title", "app", "parts" (the body in reading
    order: ("text", words), ("field", label, value), ("secret", label, dots), ("switch", label, on), ("list", items,
    chosen index), ("code", digits shown, how many boxes), ("captcha", letters), ("rating", stars, reviews)), "buttons"
    (b() dicts in the order drawn), "default" and "focus" (button indexes or None), "extra" (kind-specific rows)."""
    app = rng.choice(APPS)
    doc = rng.choice(DOCS)
    d = {"kind": kind, "style": style, "app": app, "title": app, "parts": [], "buttons": [], "default": None,
         "focus": None, "extra": []}
    phone = style in PHONES
    if kind == "confirm":
        what = rng.choice((f"Delete \"{doc}\"?", "Empty the Recycle Bin?" if style == "windows" else "Empty the Trash?",
                           "Sign out of all devices?", "Remove this printer?", "Restart now to finish installing?"))
        d.update(title=app if not phone else what)
        d["parts"] = [("text", what)] if not phone else []
        d["parts"].append(("text", rng.choice(("This cannot be undone.", "You can change this later in Settings.",
                                               "Unsaved work in open apps may be lost."))))
        d["buttons"] = [b("OK", "goes ahead and does it"), b("Cancel", "closes this message and changes nothing")]
        d["default"] = rng.choice((0, 1))
    elif kind == "save":
        d.update(title=app)
        d["parts"] = [("text", f"Do you want to save the changes you made to \"{doc}\"?"),
                      ("text", "Your changes will be lost if you don't save them.")]
        d["buttons"] = [b("Save", "saves your changes and closes the document"),
                        b("Don't Save", "closes the document and throws away the changes"),
                        b("Cancel", "goes back to the document without closing it")]
        d["default"] = 0
    elif kind == "permission":
        what = rng.choice(sorted(PERMISSIONS))
        verb, meaning = PERMISSIONS[what]
        d.update(title=f"Allow {app} to {verb}?")
        d["parts"] = [("text", rng.choice((f"{app} needs this so you can use all its features.",
                                           "You can change this at any time in Settings.")))]
        if what == "location" and phone:
            d["buttons"] = [b("While using the app", f"{meaning} Only while you are using it."),
                            b("Only this time", f"{meaning} Just this once; it asks again next time."),
                            b("Don't allow", "The app is not given this permission.")]
        else:
            d["buttons"] = [b("Allow", meaning), b("Don't allow", "The app is not given this permission; some "
                                                                  "features may not work.")]
        d["extra"].append(("What is this app asking for?", f"{app} (a made-up app) is asking for permission to "
                           f"{verb}. Only allow it if you trust the app and the feature needs it."))
    elif kind == "error":
        code = f"0x{rng.randint(0x1000, 0xFFFF):04X}"
        msg = rng.choice((f"The file \"{rng.choice(FILES)}\" could not be opened because it is damaged.",
                          "Cannot connect to the server. Check your internet connection and try again.",
                          "The printer is out of paper.", "There is not enough space on the disk.",
                          f"{app} has stopped responding.", "Your password is incorrect. You have 2 tries left."))
        d.update(title=f"{app} - Error" if not phone else "Error")
        d["parts"] = [("text", msg), ("text", f"Error code: {code}")]
        d["buttons"] = [b("OK", "closes the message")] if rng.random() < 0.5 else \
            [b("Try Again", "tries the same thing again"), b("Close", "closes the message")]
        d["default"] = 0
    elif kind == "update":
        version = f"{rng.randint(2, 19)}.{rng.randint(0, 9)}.{rng.randint(0, 9)}"
        d.update(title="Update available")
        d["parts"] = [("text", f"{app} version {version} is ready to install."),
                      ("text", rng.choice(("This update fixes security problems and improves stability.",
                                           "Your device will restart to finish the update.",
                                           f"Download size: {rng.randint(12, 950)} MB.")))]
        d["buttons"] = [b("Update now", "downloads and installs the update now"),
                        b("Later", "closes this notice; it will remind you again"),
                        b("Remind me tomorrow", "asks again tomorrow")][:rng.choice((2, 3))]
        d["default"] = 0
        d["extra"].append(("Is it safe to update?", "Updates from the device's own settings or the app's own store "
                           "are the safe way to update. Be wary of an update notice that appears on a web page or "
                           "asks you to call a number: that is a common scam."))
    elif kind == "settings":
        chosen = rng.sample(SETTINGS, rng.randint(4, 6))
        d.update(title="Settings")
        d["parts"] = [("switch", name, rng.random() < 0.5) for name in chosen]
        d["buttons"] = [] if phone else [b("Close", "closes the settings window")]
        on = [p[1] for p in d["parts"] if p[2]]
        off = [p[1] for p in d["parts"] if not p[2]]
        d["extra"].append(("Which settings are turned on?",
                           (f"Turned on: {', '.join(on)}." if on else "None of them is turned on.") +
                           (f" Turned off: {', '.join(off)}." if off else "")))
    elif kind == "sign_in":
        site = rng.choice(SITES)
        email = f"{rng.choice(FIRST).lower()}.{rng.choice(LAST).lower()}@{rng.choice(SITES)}"
        d.update(title=f"Sign in to {site}")
        d["parts"] = [("field", "Email address", email if rng.random() < 0.6 else ""),
                      ("secret", "Password", rng.randint(0, 12)), ("text", "Forgot password?")]
        d["buttons"] = [b("Sign in", "sends the email address and password to sign in"),
                        b("Create account", "opens the form to make a new account")]
        d["default"] = 0
        d["extra"].append(("Is it safe to sign in here?", f"The screen says it is the sign-in page of {site} (a "
                           f"made-up site). {PADLOCK_NOTE}"))
    elif kind == "two_factor":
        digits = rng.choice((4, 6, 6, 8))
        typed = "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(0, digits)))
        number = fiction_phone(rng)
        d.update(title="Two-step verification")
        d["parts"] = [("text", f"Enter the {digits}-digit code we sent to {number[:-4]}**{number[-2:]}."),
                      ("code", typed, digits), ("text", "Didn't get a code? Resend code")]
        d["buttons"] = [b("Verify", "checks the code and finishes signing in"),
                        b("Cancel", "stops signing in")]
        d["default"] = 0
        d["extra"].append(("What is the code for?", "It is a one-time code that proves it is really you signing in. "
                           f"Type it only into the screen where you asked to sign in. {CODE_NOTE}"))
    elif kind == "file_picker":
        folder = rng.choice(FOLDERS)
        items = rng.sample(FILES, rng.randint(4, 6))
        chosen = rng.randrange(len(items))
        verb = rng.choice(("Open", "Save"))
        d.update(title=f"{verb} file - {app}" if verb == "Open" else f"Save As - {app}")
        d["parts"] = [("text", f"Look in: {folder}"), ("list", items, chosen),
                      ("field", "File name", items[chosen] if verb == "Open" else doc)]
        d["buttons"] = [b(verb, "opens the chosen file" if verb == "Open" else "saves the file in this folder with "
                                                                              "this name"),
                        b("Cancel", "closes the window without opening or saving anything")]
        d["default"] = 0
    elif kind == "printer":
        printer = rng.choice(PRINTERS)
        copies = rng.choice((1, 1, 2, 3))
        pages = rng.choice(("All", "Current page", f"1-{rng.randint(2, 9)}"))
        colour = rng.choice(("Colour", "Black and white"))
        d.update(title="Print")
        d["parts"] = [("field", "Printer", printer), ("field", "Copies", str(copies)), ("field", "Pages", pages),
                      ("field", "Colour", colour)]
        d["buttons"] = [b("Print", "sends the document to the printer"),
                        b("Cancel", "closes the window without printing")]
        d["default"] = 0
    elif kind == "captcha":
        letters = "".join(rng.choice("ABCDEFGHJKLMNPRSTUVWXYZ23456789") for _ in range(rng.randint(5, 7)))
        audio = rng.random() < 0.6
        d.update(title="Please confirm you are not a robot")
        d["parts"] = [("text", "Type the characters you see in the picture."), ("captcha", letters),
                      ("field", "Characters", "")]
        d["buttons"] = [b("Submit", "sends what you typed"), b("New picture", "shows different characters")]
        if audio:
            d["buttons"].append(b("Audio challenge", "plays the characters as sound, so you can type what you hear"))
        d["default"] = 0
        d["extra"].append(("How do I get past this CAPTCHA?",
                           f"The picture shows the characters {' '.join(letters)}. " +
                           ("This one has an Audio challenge button: it plays characters to type instead. "
                            if audio else "This one shows no audio choice. ") + CAPTCHA_NOTE))
    elif kind == "cookie":
        site = rng.choice(SITES)
        d.update(title=f"{site} uses cookies")
        d["parts"] = [("text", "We use cookies to make this site work, to remember your choices and, if you agree, "
                               "to measure visits and show advertising.")]
        d["buttons"] = [b("Accept all", "allows all cookies, including advertising and measuring cookies"),
                        b("Reject all", "allows only the cookies the site needs to work"),
                        b("Manage choices", "opens a list where you choose each kind of cookie")]
        rng.shuffle(d["buttons"])
        d["extra"].append(("What happens if I reject the cookies?", "Rejecting keeps only the cookies the site "
                           "needs to work; the site should still work, without advertising or measuring cookies."))
    elif kind == "app_store":
        stars = rng.choice(("4.8", "4.5", "4.1", "3.6", "2.9"))
        reviews = rng.choice((f"{rng.randint(12, 999)}", f"{rng.randint(1, 9)},{rng.randint(0, 999):03d}",
                              f"{rng.randint(11, 950)}K"))
        price = rng.choice(("Free", "Free", "$2.99", "$0.99"))
        age = rng.choice(("Everyone", "Ages 4+", "Teen", "Ages 12+"))
        maker = f"{rng.choice(LAST)} Software"
        d.update(title=app)
        d["parts"] = [("text", f"By {maker}"), ("rating", stars, reviews),
                      ("text", f"Price: {price}"), ("text", f"Rated: {age}"),
                      ("text", f"Size: {rng.randint(8, 400)} MB"),
                      ("text", rng.choice(("Keep notes, lists and reminders in one place.",
                                           "Edit and share your photos.", "Track your walks and runs.",
                                           "Read books and listen to audiobooks.")))]
        label = "Install" if price == "Free" else f"Buy {price}"
        d["buttons"] = [b(label, "downloads the app" + ("" if price == "Free" else f" and charges {price}"))]
        d["default"] = 0
        d["extra"].append(("Is this app free?", "Yes: the price shown is Free." if price == "Free" else
                           f"No: it costs {price}."))
        d["extra"].append(("What is the app's rating?", f"{stars} out of 5 stars, from {reviews} ratings."))
    elif kind == "lock":
        hour, minute = rng.randint(1, 12), rng.randint(0, 59)
        day = rng.choice(("Monday, March 9", "Tuesday, June 16", "Friday, October 2", "Sunday, December 20",
                          "Wednesday, April 22"))
        notes = []
        for _ in range(rng.randint(1, 3)):
            who = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            notes.append(rng.choice((f"Messages: {who}: Running 10 minutes late, sorry!",
                                     f"Missed call: {who}", f"Calendar: Dentist at {rng.randint(1, 5)}:30 PM",
                                     f"{rng.choice(APPS)}: Your weekly summary is ready",
                                     f"Email: {who}: Photos from Saturday",
                                     "Battery: 15% battery remaining")))
        d.update(title=f"{hour}:{minute:02d}")
        d["parts"] = [("text", day)] + [("text", n) for n in notes] + [("text", "Swipe up to unlock")]
        d["extra"].append(("What notifications are on the lock screen?",
                           f"{len(notes)}: " + "; ".join(notes) + "."))
        d["extra"].append(("What time is it?", f"The lock screen shows {hour}:{minute:02d}, {day}."))
    else:   # notification banner
        who = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        text = rng.choice((f"{who}: Are we still on for lunch?", "Your package was delivered.",
                           f"Reminder: {rng.choice(DOCS)} is due today.", "Backup complete."))
        d.update(title=app)
        d["parts"] = [("text", text), ("text", "Received now")]
        d["buttons"] = [b("Reply", "opens a box to answer"), b("Mark as read", "clears the notification")] \
            if ":" in text else [b("Open", "opens the app"), b("Dismiss", "clears the notification")]
    if d["buttons"] and d["default"] is not None and style in ("windows", "mac") and rng.random() < 0.6:
        d["focus"] = rng.randrange(len(d["buttons"]))
    return d


KINDS = ("confirm", "save", "permission", "error", "update", "settings", "sign_in", "two_factor", "file_picker",
         "printer", "captcha", "cookie", "app_store", "lock", "notification")
KIND_WORDS = {"confirm": "a question asking you to confirm (OK or Cancel)", "save": "a \"save changes\" question",
              "permission": "a permission prompt", "error": "an error message", "update": "an update notice",
              "settings": "a settings page", "sign_in": "a sign-in screen", "two_factor": "a two-step verification "
              "(two-factor) code screen", "file_picker": "a file picker", "printer": "a print dialog",
              "captcha": "a CAPTCHA (a test to show you are a person)", "cookie": "a cookie banner",
              "app_store": "an app store page", "lock": "a phone lock screen", "notification": "a notification"}
# The kinds that only make sense on a phone or only on a computer.
PHONE_ONLY = ("lock", "app_store")
COMPUTER_ONLY = ("file_picker", "printer", "save")


def style_for(kind, rng):
    """A look that fits the kind of screen."""
    if kind in PHONE_ONLY:
        return rng.choice(PHONES)
    if kind in COMPUTER_ONLY:
        return rng.choice(("windows", "mac"))
    return rng.choice(STYLES)


# ----------------------------------------------------------------- the answers

def part_words(part):
    """One body part in words, as a screen reader would say it."""
    kind = part[0]
    if kind == "text":
        return part[1]
    if kind == "field":
        return f"{part[1]} box: " + (part[2] if part[2] else "empty")
    if kind == "secret":
        return f"{part[1]} box: " + (f"{part[2]} characters typed, hidden as dots" if part[2] else "empty")
    if kind == "switch":
        return f"{part[1]}: switch {'on' if part[2] else 'off'}"
    if kind == "list":
        return "List of files: " + ", ".join(part[1]) + f" ({part[1][part[2]]} is selected)"
    if kind == "code":
        return f"Code boxes: {part[2]} boxes, " + (f"filled in so far: {part[1]}" if part[1] else "all empty")
    if kind == "captcha":
        return "A picture of stretched, wavy characters"
    if kind == "rating":
        return f"Rating: {part[1]} out of 5 stars ({part[2]} ratings)"
    return ""


def button_words(d):
    """ "Buttons: Save (default, has focus), Don't Save, Cancel." or "" when there are no buttons."""
    if not d["buttons"]:
        return ""
    out = []
    for i, button in enumerate(d["buttons"]):
        marks = [w for w, on in (("default", i == d["default"]), ("has keyboard focus", i == d["focus"])) if on]
        out.append(button["label"] + (f" ({', '.join(marks)})" if marks else ""))
    return f"Button{'s' if len(out) > 1 else ''}: " + ", ".join(out) + "."


def screen_rows(d):
    """The rows of one screen, from its own made-up facts (see the module docstring)."""
    look = STYLE_WORDS[d["style"]]
    label = {"lock": "Time", "notification": "Notification from", "app_store": "App"}.get(d["kind"], "Title")
    read = [f"{label}: {d['title']}."] + [w.rstrip(".") + "." for w in (part_words(p) for p in d["parts"]) if w]
    if button_words(d):
        read.append(button_words(d))
    rows = [{"question": KIND_Q, "answer": f"It is {KIND_WORDS[d['kind']]} on {look} screen, from "
             f"{'the made-up app ' + d['app'] if d['kind'] not in ('lock',) else 'the phone itself'}."},
            {"question": READ_Q, "answer": " ".join(read)}]
    if d["buttons"]:
        rows.append({"question": BUTTONS_Q, "answer": " ".join(f"{x['label']}: {x['does'].rstrip('.')}."
                                                             for x in d["buttons"])})
        if d["default"] is not None:
            default = d["buttons"][d["default"]]["label"]
            drawn = "drawn in bold" if d["style"] == "iphone" else "drawn filled in colour"
            said = f"The default button, {drawn}, is {default}: pressing Enter would choose it."
            if d["focus"] is not None:
                focus = d["buttons"][d["focus"]]["label"]
                said += (f" Keyboard focus (the dotted outline) is on {focus}" +
                         (", so Space would press it too." if focus == default else
                          f", so Space would press {focus} while Enter still presses {default}."))
        else:
            said = "No button is highlighted as the default."
        rows.append({"question": SELECTED_Q, "answer": said})
    rows += [{"question": q, "answer": a} for q, a in d["extra"]]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows]


# ----------------------------------------------------------------- drawing

def wrap(draw, text, fnt, width):
    """text broken into lines that fit width pixels."""
    lines, line = [], ""
    for word in text.split():
        if line and draw.textlength(f"{line} {word}", font=fnt) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + ([line] if line else [])


def palette(style, rng):
    """The colours of a look: a dark or light theme for phones, light for computers."""
    dark = style in PHONES and rng.random() < 0.35
    accent = rng.choice([(40, 100, 200), (30, 120, 90), (120, 70, 170), (200, 90, 30), (20, 110, 150)])
    if dark:
        return {"bg": (28, 28, 30), "panel": (48, 48, 52), "ink": (240, 240, 240), "dim": (170, 170, 175),
                "line": (90, 90, 95), "accent": accent, "field": (36, 36, 40), "back": (12, 12, 14)}
    return {"bg": (246, 246, 248), "panel": (255, 255, 255), "ink": (20, 20, 22), "dim": (100, 100, 105),
            "line": (190, 190, 196), "accent": accent, "field": (255, 255, 255),
            "back": rng.choice([(70, 110, 150), (120, 140, 120), (150, 120, 160), (210, 200, 180), (90, 90, 100)])}


def draw_part(draw, part, x, y, width, colours, k, fonts, canvas=None):
    """Draw one body part at (x, y) within width pixels (a CAPTCHA picture is pasted onto canvas, the image draw
    draws on); returns the y below it."""
    body, small, bold = fonts
    kind = part[0]
    ink, dim, line = colours["ink"], colours["dim"], colours["line"]
    if kind == "text":
        link = part[1].startswith(("Forgot", "Didn't get", "Swipe"))
        for text in wrap(draw, part[1], body, width):
            draw.text((x, y), text, font=body, fill=colours["accent"] if link else ink)
            y += body.size + 8
        return y + 6
    if kind in ("field", "secret"):
        draw.text((x, y), part[1], font=small, fill=dim)
        y += small.size + 6
        draw.rectangle([x, y, x + width, y + body.size + 22], outline=line, width=2, fill=colours["field"])
        shown = part[2] if kind == "field" else "•" * part[2]
        draw.text((x + 12, y + 10), shown, font=body, fill=ink)
        return y + body.size + 36
    if kind == "switch":
        draw.text((x, y + 6), part[1], font=body, fill=ink)
        sx = x + width - 90
        on = part[2]
        draw.rounded_rectangle([sx, y, sx + 80, y + 40], radius=20, fill=colours["accent"] if on else line)
        knob = sx + 44 if on else sx + 4
        draw.ellipse([knob, y + 4, knob + 32, y + 36], fill=(255, 255, 255))
        draw.text((sx - 50, y + 8), "On" if on else "Off", font=small, fill=dim)
        draw.line([x, y + 56, x + width, y + 56], fill=line, width=1)
        return y + 70
    if kind == "list":
        for i, item in enumerate(part[1]):
            if i == part[2]:
                draw.rectangle([x, y - 4, x + width, y + body.size + 8], fill=colours["accent"])
            draw.rectangle([x + 8, y + 4, x + 26, y + 24], outline=ink if i != part[2] else (255, 255, 255), width=2)
            draw.text((x + 40, y), item, font=body, fill=(255, 255, 255) if i == part[2] else ink)
            y += body.size + 16
        return y + 8
    if kind == "code":
        box = min(70, (width - 10 * part[2]) // part[2])
        for i in range(part[2]):
            bx = x + i * (box + 10)
            draw.rectangle([bx, y, bx + box, y + box + 10], outline=line if i >= len(part[1]) else colours["accent"],
                           width=3, fill=colours["field"])
            if i < len(part[1]):
                draw.text((bx + box // 3, y + 14), part[1][i], font=bold, fill=ink)
        return y + box + 30
    if kind == "captcha":
        import random
        from PIL import Image, ImageDraw
        tile = Image.new("RGB", (min(width, 420), 110), (225, 228, 220))
        tdraw = ImageDraw.Draw(tile)
        jitter = random.Random(part[1])
        for _ in range(14):
            tdraw.line([jitter.randint(0, tile.width), jitter.randint(0, 110), jitter.randint(0, tile.width),
                        jitter.randint(0, 110)], fill=(140, 140, 150), width=2)
        cx = 20
        for ch in part[1]:
            glyph = Image.new("RGBA", (70, 90), (0, 0, 0, 0))
            ImageDraw.Draw(glyph).text((10, 5), ch, font=font(60, True, k), fill=(40, 40, 90, 255))
            glyph = glyph.rotate(jitter.randint(-28, 28), expand=False)
            tile.paste(glyph, (cx, jitter.randint(0, 20)), glyph)
            cx += 52
        if canvas is not None:
            canvas.paste(tile, (x, y))
        return y + 130
    if kind == "rating":
        draw.text((x, y), f"{part[1]} stars   ({part[2]} ratings)", font=body, fill=ink)
        return y + body.size + 14
    return y


def draw_buttons(draw, d, x0, x1, y, colours, fonts, phone):
    """Draw the buttons in a row (right-aligned on computers, full width on phones); returns the y below them."""
    body = fonts[0]
    if not d["buttons"]:
        return y
    labels = [x["label"] for x in d["buttons"]]
    if phone and d["style"] == "iphone":
        # Stacked full-width buttons divided by lines, as many phone alerts are.
        for i, label in enumerate(labels):
            draw.line([x0, y, x1, y], fill=colours["line"], width=1)
            weight = fonts[2] if i == d["default"] else body
            w = draw.textlength(label, font=weight)
            draw.text(((x0 + x1 - w) / 2, y + 18), label, font=weight, fill=colours["accent"])
            y += body.size + 40
        return y
    widths = [int(draw.textlength(label, font=body)) + 48 for label in labels]
    total = sum(widths) + 16 * (len(widths) - 1)
    if total > x1 - x0:                                  # too wide for one row: one button a row
        rows = [[i] for i in range(len(labels))]
    else:
        rows = [list(range(len(labels)))]
    for row in rows:
        width_row = sum(widths[i] for i in row) + 16 * (len(row) - 1)
        bx = x1 - width_row
        for i in row:
            box = [bx, y, bx + widths[i], y + body.size + 24]
            if i == d["default"]:
                draw.rounded_rectangle(box, radius=8 if d["style"] != "windows" else 2, fill=colours["accent"])
                fill = (255, 255, 255)
            elif d["style"] == "android":
                fill = colours["accent"]                      # text buttons
            else:
                draw.rounded_rectangle(box, radius=8 if d["style"] != "windows" else 2, outline=colours["line"],
                                       width=2, fill=colours["panel"])
                fill = colours["ink"]
            draw.text((bx + 24, y + 12), labels[i], font=body, fill=fill)
            if i == d["focus"]:
                for dx in range(box[0] - 5, box[2] + 5, 8):
                    draw.line([dx, box[1] - 5, dx + 4, box[1] - 5], fill=colours["ink"], width=2)
                    draw.line([dx, box[3] + 5, dx + 4, box[3] + 5], fill=colours["ink"], width=2)
                for dy in range(box[1] - 5, box[3] + 5, 8):
                    draw.line([box[0] - 5, dy, box[0] - 5, dy + 4], fill=colours["ink"], width=2)
                    draw.line([box[2] + 5, dy, box[2] + 5, dy + 4], fill=colours["ink"], width=2)
            bx += widths[i] + 16
        y += body.size + 40
    return y


def draw_screen(d, rng):
    """One screen as a PIL image (see the module docstring)."""
    from PIL import Image, ImageDraw
    phone = d["style"] in PHONES
    k = rng.randrange(8)
    colours = palette(d["style"], rng)
    size = (750, 1334) if phone else (1280, 800)
    page = Image.new("RGB", size, colours["back"])
    draw = ImageDraw.Draw(page)
    fonts = (font(30 if phone else 22, False, k), font(24 if phone else 18, False, k),
             font(32 if phone else 24, True, k))
    full = d["kind"] in ("settings", "lock", "app_store", "sign_in", "two_factor", "captcha") and phone
    if phone:                                             # the phone's status bar
        draw.rectangle([0, 0, size[0], 50], fill=colours["back"] if not full else colours["bg"])
        status_ink = (255, 255, 255) if not full or colours["bg"][0] < 100 else (20, 20, 20)
        draw.text((30, 12), f"{rng.randint(1, 12)}:{rng.randint(0, 59):02d}", font=fonts[1], fill=status_ink)
        draw.text((size[0] - 130, 12), f"{rng.randint(20, 99)}%", font=fonts[1], fill=status_ink)
    if d["kind"] == "lock":                               # the lock screen fills the phone
        draw.rectangle([0, 50, size[0], size[1]], fill=colours["back"])
        big = font(140, False, k)
        w = draw.textlength(d["title"], font=big)
        draw.text(((size[0] - w) / 2, 140), d["title"], font=big, fill=(255, 255, 255))
        y = 320
        for i, part in enumerate(d["parts"]):
            text = part[1]
            if i == 0 or text.startswith("Swipe"):
                w = draw.textlength(text, font=fonts[0])
                draw.text(((size[0] - w) / 2, y if i == 0 else size[1] - 120), text, font=fonts[0],
                          fill=(255, 255, 255))
                y += 80 if i == 0 else 0
                continue
            lines = wrap(draw, text, fonts[0], size[0] - 120)
            height = 30 + (fonts[0].size + 8) * len(lines)
            draw.rounded_rectangle([40, y, size[0] - 40, y + height], radius=24, fill=(240, 240, 244))
            ty = y + 15
            for line in lines:
                draw.text((60, ty), line, font=fonts[0], fill=(20, 20, 22))
                ty += fonts[0].size + 8
            y += height + 20
        return page
    if not phone:                                         # a plain window behind the dialog, on a desktop
        draw.rectangle([60, 40, size[0] - 60, size[1] - 80], fill=(236, 236, 238), outline=(150, 150, 155))
        draw.rectangle([0, size[1] - 48, size[0], size[1]], fill=(40, 44, 52) if d["style"] == "windows"
                       else (225, 225, 230))
    width = (size[0] - 80) if phone else rng.choice((640, 720, 800))
    if full:
        x0, top = 0, 50
        width = size[0]
    elif d["kind"] == "notification":
        x0, top = (20, 70) if phone else (size[0] - 520, 20)
        width = (size[0] - 40) if phone else 500
    elif d["kind"] == "cookie":
        x0, top, width = 0, (size[1] - 420) if phone else (size[1] - 300), size[0]
    else:
        x0 = (size[0] - width) // 2
        top = 260 if phone else rng.randint(110, 180)
    pad = 36 if phone else 28
    inner = width - 2 * pad
    # Measure, then draw: a scratch pass finds the height.
    scratch = Image.new("RGB", (width, 3000))
    sdraw = ImageDraw.Draw(scratch)
    title_lines = wrap(sdraw, d["title"], fonts[2], inner)
    has_bar = d["style"] in ("windows", "mac") and d["kind"] not in ("notification", "cookie")
    y = (44 + 16 if has_bar else 20) + (fonts[2].size + 10) * len(title_lines) + 20
    for part in d["parts"]:
        y = draw_part(sdraw, part, pad, y, inner, colours, k, fonts)
    y = draw_buttons(sdraw, d, pad, width - pad, y + 10, colours, fonts, phone)
    height = size[1] - top if full else y + 20
    radius = 0 if full or d["style"] == "windows" else 22
    draw.rounded_rectangle([x0, top, x0 + width, top + height], radius=radius, fill=colours["panel"],
                           outline=colours["line"], width=1 if not full else 0)
    y = top + 20
    if has_bar:
        bar = 44
        draw.rectangle([x0 + 1, top + 1, x0 + width - 1, top + bar], fill=colours["bg"])
        if d["style"] == "windows":
            draw.text((x0 + 16, top + 10), d["app"], font=fonts[1], fill=colours["dim"])
            draw.text((x0 + width - 40, top + 8), "X", font=fonts[1], fill=colours["dim"])
        else:                                             # three plain grey circles, centred title
            for i in range(3):
                draw.ellipse([x0 + 16 + i * 26, top + 14, x0 + 32 + i * 26, top + 30], fill=(180, 180, 186))
            w = draw.textlength(d["app"], font=fonts[1])
            draw.text((x0 + (width - w) / 2, top + 10), d["app"], font=fonts[1], fill=colours["dim"])
        y = top + bar + 16
    for line in title_lines:
        if d["style"] == "iphone" and not full:
            w = draw.textlength(line, font=fonts[2])
            draw.text((x0 + (width - w) / 2, y), line, font=fonts[2], fill=colours["ink"])
        else:
            draw.text((x0 + pad, y), line, font=fonts[2], fill=colours["ink"])
        y += fonts[2].size + 10
    y += 20
    for part in d["parts"]:
        y = draw_part(draw, part, x0 + pad, y, inner, colours, k, fonts, page)
    draw_buttons(draw, d, x0 + (0 if d["style"] == "iphone" else pad), x0 + width - (0 if d["style"] == "iphone"
                                                                                     else pad), y + 10, colours,
                 fonts, phone)
    return page


def make_screen(n, seed=SEED):
    """The n-th screen (the kinds in turn) as (file name, JPEG bytes, rows): a clean screenshot, or about one in
    four photographed off the screen with a phone."""
    import io
    rng = seeded(seed, n)
    kind = KINDS[n % len(KINDS)]
    d = details(kind, style_for(kind, rng), rng)
    page = draw_screen(d, rng)
    if rng.random() < 0.25:
        data = phone_photo(page, rng, background=(20, 20, 22), strength=rng.uniform(0.3, 0.9))
    else:
        buffer = io.BytesIO()
        page.save(buffer, "JPEG", quality=90)
        data = buffer.getvalue()
    return f"screen-{kind}-{d['style']}-{n:05d}.jpg", data, screen_rows(d)


def build_synthetic_screens(limit):
    """The synthetic_screens pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_screen(n) for n in range(limit)])


SCREENS_PACKS = {
    "synthetic_screens": (build_synthetic_screens,
                          "Computer-made (synthetic) computer and phone screens drawn with Pillow by "
                          "packs/screens_packs.py from a fixed seed, in generic Windows-like, Mac-like, Android-like "
                          "and iPhone-like looks (no company's logos, icons or trademarked designs): dialog boxes, "
                          "error messages, permission prompts, update notices, settings, sign-in and two-step "
                          "verification screens, file pickers, print dialogs, CAPTCHAs, cookie banners, app store "
                          "pages, lock screens and notifications; made-up apps and people, .example addresses, "
                          "555-01xx numbers. CC0."),
}
SCREENS_LIMITS = {"synthetic_screens": 3000}
SCREENS_COMMONS_KEYS = ()


def main(argv=None):
    """Make a few screens and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the synthetic screens pack builder.")
    parser.add_argument("key", choices=sorted(SCREENS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = SCREENS_PACKS[args.key][0](args.limit)
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
