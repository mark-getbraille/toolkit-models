"""Picture packs for TRAVEL (the owner's request of 2026-11-22). Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more
than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit
counts pictures.

Why: a blind traveller is handed a boarding pass at the desk and carries a passport, and in an airport or station
needs to know what a sign means. The packs teach the picture describer to read those.

The packs (TRAVEL_PACKS):
  synthetic_travel_documents  COMPUTER-MADE passport data pages and boarding passes, drawn here with Pillow from a
                              fixed seed and photographed by phone_photo.py, the same way as synthetic_bills_packs.py
                              (helpers in synthetic_documents.py). NEVER usable as real documents: SPECIMEN across
                              every page and at its top, made-up names, passports of "Utopia" (code UTO, the made-up
                              country of the ICAO's own specimen passports) with numbers containing "SPC" that no
                              real passport has, made-up airlines and flight numbers starting "ZZ". Every row is
                              marked synthetic and every answer is exact (the generator drew it): whose document it
                              is, the passport's expiry date, the flight, the destination, the gate, the boarding
                              time, the seat and the boarding group. Never for picture-making (a model must never
                              learn to draw convincing travel documents).
  commons_travel_signs        Wikimedia Commons (CC0, public domain or CC BY files only): the US Department of
                              Transportation's passenger symbol signs (the AIGA pictograms, public domain), each named
                              from its own file name (baggage claim, customs, immigration, taxi, currency exchange
                              ...), airport signs, passport control, baggage carousels, jet bridges, taxi signs and
                              currency exchange offices.

Not repeated here: airport gates, departure boards, departure and arrival halls, airport escalators and the inside of
airports (indoor_packs), US airport terminals and airport security (us_modern_packs), Canadian airports
(canada_packs), toilet and exit signs (indoor_packs, events_safety_packs). Real passports and boarding passes are
never used: they carry real people's details.

    python packs/travel_packs.py synthetic_travel_documents --limit 6 --save some-folder      (a quick check)
"""

import datetime
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo
from synthetic_bills_packs import long_date
from synthetic_documents import (SPECIMEN, made_up_person, not_real_row, seeded, specimen_marks)

SEED = 9411
CREDIT = ("A computer-made SPECIMEN document drawn with Pillow by packs/travel_packs.py (synthetic: made-up names, "
          "country, airline and numbers; not a real document and never usable as one), CC0")
KIND_Q = "What kind of document is this?"
WHOSE_Q = "Whose document is this?"

# Made-up airlines (their codes begin ZZ, which no real airline's flight numbers use here) and real airport codes.
AIRLINES = (("Aldoria Air", "ZZ"), ("Westmarch Airways", "ZY"), ("Norvale Express", "ZX"))
AIRPORTS = (("ATL", "Atlanta"), ("BOS", "Boston"), ("ORD", "Chicago O'Hare"), ("DFW", "Dallas/Fort Worth"),
            ("DEN", "Denver"), ("LAX", "Los Angeles"), ("MIA", "Miami"), ("JFK", "New York JFK"),
            ("SFO", "San Francisco"), ("SEA", "Seattle"), ("YYZ", "Toronto Pearson"), ("MEX", "Mexico City"),
            ("LHR", "London Heathrow"), ("MSP", "Minneapolis-Saint Paul"), ("PHX", "Phoenix"))
GROUPS = ("1", "2", "3", "4", "5", "A", "B", "C", "PRE", "Priority")


def passport_details(n, rng):
    """The made-up facts of the n-th passport data page."""
    first, last = made_up_person(rng)
    born = datetime.date(1940, 1, 1) + datetime.timedelta(days=rng.randint(0, 25000))
    issued = datetime.date(2017, 1, 1) + datetime.timedelta(days=rng.randint(0, 3200))
    expires = issued.replace(year=issued.year + 10) - datetime.timedelta(days=1)
    number = f"SPC{rng.randint(100000, 999999)}"
    return {"kind": "passport", "first": first, "last": last, "born": born, "issued": issued, "expires": expires,
            "number": number, "sex": rng.choice("FMX"), "place": rng.choice(("Utopia City", "Port Ellery",
                                                                              "Maple Falls", "Westmarch"))}


def boarding_details(n, rng):
    """The made-up facts of the n-th boarding pass."""
    first, last = made_up_person(rng)
    airline, code = rng.choice(AIRLINES)
    origin, dest = rng.sample(AIRPORTS, 2)
    day = datetime.date(2026, 1, 1) + datetime.timedelta(days=rng.randint(0, 360))
    depart = datetime.time(rng.randint(5, 22), rng.choice((0, 5, 15, 20, 30, 35, 45, 50)))
    board = (datetime.datetime.combine(day, depart) - datetime.timedelta(minutes=rng.choice((30, 35, 40, 45)))).time()
    return {"kind": "boarding", "first": first, "last": last, "airline": airline, "flight": f"{code} {rng.randint(100, 9999)}",
            "origin": origin, "dest": dest, "day": day, "depart": depart, "board": board,
            "gate": f"{rng.choice('ABCDE')}{rng.randint(1, 48)}", "seat": f"{rng.randint(1, 38)}{rng.choice('ABCDEF')}",
            "group": rng.choice(GROUPS), "cabin": rng.choice(("Economy", "Economy", "Main Cabin", "Business"))}


def clock(t):
    """ "7:45 PM" from a time."""
    return t.strftime("%I:%M %p").lstrip("0")


def draw_passport(d, rng):
    """A passport data page as a PIL image (a card shape with a photo box, the fields and two MRZ-like lines)."""
    from PIL import Image, ImageDraw
    width, height = 1250, 880
    k = rng.randrange(8)
    page = Image.new("RGB", (width, height), rng.choice([(236, 241, 247), (243, 238, 228), (234, 244, 236)]))
    draw = ImageDraw.Draw(page)
    ink, accent = (25, 25, 40), rng.choice([(20, 50, 120), (110, 30, 50), (20, 90, 70)])
    draw.text((40, 60), "UTOPIA  PASSPORT  (SPECIMEN)", font=font(40, True, k), fill=accent)
    draw.rectangle([40, 120, 360, 520], outline=accent, width=4)
    draw.text((95, 300), "NO PHOTO", font=font(34, True, k), fill=accent)
    fields = [("Type / Type", "P"), ("Code / Code", "UTO"), ("Passport No. / No du passeport", d["number"]),
              ("Surname / Nom", d["last"].upper()), ("Given names / Prénoms", d["first"].upper()),
              ("Nationality / Nationalité", "UTOPIAN (SPECIMEN)"),
              ("Date of birth / Date de naissance", d["born"].strftime("%d %b %Y").upper()),
              ("Sex / Sexe", d["sex"]), ("Place of birth / Lieu de naissance", d["place"].upper()),
              ("Date of issue / Date de délivrance", d["issued"].strftime("%d %b %Y").upper()),
              ("Date of expiration / Date d'expiration", d["expires"].strftime("%d %b %Y").upper()),
              ("Authority / Autorité", "MINISTRY OF SPECIMENS")]
    for i, (label, value) in enumerate(fields):           # two columns of six fields
        x, y = (400 if i < 6 else 830), 130 + (i % 6) * 64
        draw.text((x, y), label, font=font(19, False, k), fill=ink)
        draw.text((x, y + 22), value, font=font(28, True, k), fill=ink)
    names = f"{d['last'].upper()}<<{d['first'].upper()}".replace(" ", "<")
    line1 = f"P<UTO{names}".ljust(44, "<")[:44]
    line2 = f"{d['number']}<0UTO{d['born']:%y%m%d}0{d['sex']}{d['expires']:%y%m%d}0SPECIMEN".ljust(44, "<")[:44]
    for i, line in enumerate((line1, line2)):
        draw.text((40, height - 130 + i * 50), line, font=font(34, False, k), fill=ink)
    return specimen_marks(page, kind_font=k), k


def draw_boarding(d, rng):
    """A boarding pass as a PIL image (the airline's band, the fields in boxes, a tear-off stub)."""
    from PIL import Image, ImageDraw
    width, height = 1500, 720
    k = rng.randrange(8)
    page = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    ink, accent = (20, 20, 20), rng.choice([(0, 70, 140), (180, 30, 40), (0, 110, 90), (90, 40, 140)])
    draw.rectangle([0, 0, width, 100], fill=accent)
    draw.text((30, 28), f"{d['airline']}   BOARDING PASS", font=font(40, True, k), fill=(255, 255, 255))
    boxes = [("PASSENGER", f"{d['last'].upper()}/{d['first'].upper()}"), ("FLIGHT", d["flight"]),
             ("DATE", d["day"].strftime("%d%b%y").upper()),
             ("FROM", f"{d['origin'][0]} {d['origin'][1]}"), ("TO", f"{d['dest'][0]} {d['dest'][1]}"),
             ("DEPARTS", clock(d["depart"])), ("BOARDING", clock(d["board"])), ("GATE", d["gate"]),
             ("SEAT", d["seat"]), ("GROUP", d["group"]), ("CLASS", d["cabin"])]
    x, y = 30, 130
    for label, value in boxes:
        w = 520 if label in ("PASSENGER", "FROM", "TO") else 240
        if x + w > 1080:
            x, y = 30, y + 120
        draw.rectangle([x, y, x + w - 15, y + 105], outline=accent, width=3)
        draw.text((x + 12, y + 8), label, font=font(20, True, k), fill=accent)
        size = 34
        while size > 16 and draw.textlength(value, font=font(size, True, k)) > w - 40:
            size -= 1
        draw.text((x + 12, y + 45), value, font=font(size, True, k), fill=ink)
        x += w
    for yy in range(110, height, 22):
        draw.line([(1110, yy), (1110, yy + 11)], fill=ink, width=2)
    stub = [d["flight"], f"{d['origin'][0]} to {d['dest'][0]}", f"Gate {d['gate']}", f"Seat {d['seat']}",
            f"Group {d['group']}", f"{d['last'].upper()}/{d['first'].upper()}"]
    for i, line in enumerate(stub):
        draw.text((1135, 140 + i * 62), line, font=font(30, True, k), fill=ink)
    draw.rectangle([30, height - 80, 1080, height - 25], outline=ink, width=2)
    draw.text((45, height - 70), "NO BARCODE - SPECIMEN ONLY", font=font(28, True, k), fill=ink)
    return specimen_marks(page, kind_font=k), k


def passport_rows(d):
    """The rows of a passport data page, from its own made-up facts."""
    name = f"{d['first']} {d['last']}"
    rows = [{"question": KIND_Q, "answer": "This is a SPECIMEN passport data page (the page with the photo and "
                                          "details) of the made-up country Utopia."},
            {"question": WHOSE_Q, "answer": f"It is made out to {name} (a made-up person)."},
            {"question": "When does this passport expire?", "answer": f"The date of expiration printed is "
                                                                     f"{long_date(d['expires'])}."},
            {"question": "What is the passport number?", "answer": f"The number printed is {d['number']}, a "
                                                                  f"specimen number no real passport has."},
            {"question": "What are the two lines of letters at the bottom?", "answer": "They are the "
             "machine-readable zone: the same details coded for a passport reader, with < filling the gaps."}]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row("a passport data page", CREDIT)]


def boarding_rows(d):
    """The rows of a boarding pass, from its own made-up facts."""
    name = f"{d['first']} {d['last']}"
    rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN boarding pass from {d['airline']} (a made-up "
                                          f"airline)."},
            {"question": WHOSE_Q, "answer": f"It is for {name} (a made-up person)."},
            {"question": "What flight is this, and where is it going?", "answer": f"Flight {d['flight']} from "
             f"{d['origin'][1]} ({d['origin'][0]}) to {d['dest'][1]} ({d['dest'][0]}), on {long_date(d['day'])}."},
            {"question": "What gate do I go to?", "answer": f"Gate {d['gate']}."},
            {"question": "When does boarding start?", "answer": f"Boarding is at {clock(d['board'])}; the flight "
                                                               f"departs at {clock(d['depart'])}."},
            {"question": "What is my seat?", "answer": f"Seat {d['seat']}, in {d['cabin']}, boarding group "
                                                      f"{d['group']}."}]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row("a boarding pass", CREDIT)]


def make_document(n, seed=SEED):
    """The n-th document (passports and boarding passes in turn) as (file name, JPEG bytes, rows)."""
    rng = seeded(seed, n)
    if n % 2 == 0:
        d = passport_details(n, rng)
        page, _k = draw_passport(d, rng)
        rows = passport_rows(d)
    else:
        d = boarding_details(n, rng)
        page, _k = draw_boarding(d, rng)
        rows = boarding_rows(d)
    data = phone_photo(page, rng, strength=rng.uniform(0.3, 1.0))
    return f"travel-{d['kind']}-{n:05d}.jpg", data, rows


def build_synthetic_travel_documents(limit):
    """The synthetic_travel_documents pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_document(n) for n in range(limit)])


# ----------------------------------------------------------------- Commons travel signs

SIGN_Q = "What does this sign tell me?"
PLACE_Q = "What kind of place is this?"
WHAT_Q = "What is this?"
AIGA = "AIGA symbol signs"
AIGA_NOTE = ("It is one of the passenger symbol signs the US Department of Transportation had designed with the AIGA "
             "for airports, stations and other transport buildings.")
# (pattern of the file's own name, what the sign means): only files whose name says which sign they are.
AIGA_SIGNS = [
    (r"baggage ?check ?in", "baggage check-in: where you hand in your bags"),
    (r"baggage ?lockers", "baggage lockers: lockers for leaving bags"),
    (r"arriving ?flights", "arriving flights (arrivals)"), (r"departing ?flights", "departing flights (departures)"),
    (r"immigration", "immigration: passport and immigration control"), (r"customs", "customs"),
    (r"currency ?exchange", "currency exchange: where you can change money"), (r"taxi", "taxis"),
    (r"ground ?transportation", "ground transportation: buses, shuttles and taxis from the airport"),
    (r"car ?rental", "car rental"), (r"rail ?transportation", "trains (rail transportation)"),
    (r"\bbus\b", "buses"), (r"water ?transportation", "boats and ferries"), (r"heliport", "a heliport"),
    (r"ticket ?purchase", "tickets: where to buy them"), (r"lost ?and ?found", "lost and found"),
    (r"information", "information: where you can ask for help"), (r"hotel ?information", "hotel information"),
    (r"waiting ?room", "a waiting room"), (r"elevator", "a lift (elevator)"), (r"escalator", "an escalator"),
    (r"stairs", "stairs"), (r"first ?aid", "first aid"), (r"drinking ?fountain", "a drinking fountain"),
    (r"telephone", "a telephone"), (r"\bmail\b", "mail (post)"), (r"coffee ?shop", "a coffee shop"),
    (r"restaurant", "a restaurant"), (r"\bbar\b", "a bar"), (r"shops", "shops"), (r"cashier", "a cashier"),
    (r"coat ?check", "a coat check"), (r"nursery", "a nursery (baby changing)"),
    (r"litter ?disposal", "a litter bin"), (r"no[ -]?smoking", "no smoking"), (r"no[ -]?parking", "no parking"),
    (r"no[ -]?entry", "no entry"), (r"no[ -]?dogs", "no dogs (service animals are allowed in US public places under the "
                                             "ADA)"), (r"\bparking", "parking"), (r"\bexit", "the exit"),
]


def aiga_specs():
    """One Commons spec per AIGA sign: the category's files whose own name, just after "Aiga", starts with the
    sign's words (so "Aiga hotelinformation" is hotel information, never plain information)."""
    specs = []
    for pattern, meaning in AIGA_SIGNS:
        specs.append((AIGA, False, [(SIGN_Q, f"It is the symbol sign for {meaning}. {AIGA_NOTE}")],
                      re.compile(rf"^File:(Aiga|AIGA)[ _-]*{pattern}", re.I)))
    return specs


TRAVEL_SPECS = [
    ("Internal airport signs", True, [(SIGN_Q, "It is a sign inside an airport.")]),
    ("Airport signs in the United States", True, [(SIGN_Q, "It is an airport sign in the USA.")]),
    ("Passport control", False, [(PLACE_Q, "This is passport control, where officers check travellers' passports "
                                           "and visas.")]),
    ("Baggage carousels", True, [(WHAT_Q, "This is a baggage carousel (baggage claim belt), where checked bags come "
                                          "out after a flight.")]),
    ("Jet bridges", True, [(WHAT_Q, "This is a jet bridge (air bridge): the covered walkway from the gate to the "
                                    "plane's door.")]),
    ("Taxi signs", True, [(SIGN_Q, "It is a taxi sign: taxis stop or wait here.")]),
    ("Bureaux de change", True, [(PLACE_Q, "This is a bureau de change (currency exchange), where you can change "
                                           "money.")]),
]


def build_commons_travel_signs(limit):
    """The commons_travel_signs pack (see the module docstring)."""
    from home_packs import build_commons_topic
    specs = aiga_specs() + TRAVEL_SPECS
    return build_commons_topic(specs, limit, "travelsign")


# ----------------------------------------------------------------- the packs

TRAVEL_PACKS = {
    "synthetic_travel_documents": (build_synthetic_travel_documents,
                                   "Computer-made (synthetic) SPECIMEN passport data pages and boarding passes drawn "
                                   "with Pillow by packs/travel_packs.py from a fixed seed: made-up people, country, "
                                   "airlines and numbers, marked SPECIMEN, never usable as real documents. CC0."),
    "commons_travel_signs": (build_commons_travel_signs,
                             "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY "
                             "(credited below) of the AIGA passenger symbol signs, airport signs, passport control, "
                             "baggage carousel, jet bridge, taxi sign and currency exchange categories."),
}
TRAVEL_LIMITS = {
    "synthetic_travel_documents": 3000,
    "commons_travel_signs": 600,
}
TRAVEL_COMMONS_KEYS = ("commons_travel_signs",)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try a travel pack builder.")
    parser.add_argument("key", choices=sorted(TRAVEL_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = TRAVEL_PACKS[args.key][0](args.limit)
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
