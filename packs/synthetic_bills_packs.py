"""Pack builder for BILLS AND STATEMENTS, COMPUTER-MADE (SYNTHETIC) ONLY: electricity, gas and water bills, phone
bills, bank statements, credit-card statements, pharmacy receipts and medical bills, drawn here with Pillow from a
fixed seed with MADE-UP people, companies, addresses and amounts, and photographed by phone_photo.py (turned, tilted,
uneven light, blur). Never a real person's document: no real bill is read, copied or downloaded, nothing is fetched at
all. Used by build_packs.py in the same way as its own PACKS: build_synthetic_bills(limit) returns [(file name, JPEG
bytes or None, row)], every row marked "synthetic": true. A picture with more than one question comes once with its
JPEG and then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit
counts pictures.

Why: bills and statements come on paper, and a blind person has to find the amount due, the due date, whose bill it is
and how to pay, without a sighted helper reading their private papers.

Because the generator wrote each page, every answer is exact: "How much do I owe?" (the amount due, or for a bank
statement the closing balance and for a receipt the total paid), "When is it due?", "Whose bill is this?" (the
account holder or patient), "How can I pay?" (the ways printed on the page), "What kind of document is this?", and
"Where on the page is the amount due?" (the part of the page where it was drawn). Made-up details are kept
unmistakably made up: company and town names invented here, web addresses under the reserved ".example" domain, phone
numbers in the 555-01xx range set aside for fiction, account and card numbers masked to their last four digits.

Layouts vary (a colour band or a plain header, the summary box on the left or right, a payment stub at the foot or
none, one of several fonts and sizes, black or coloured ink), so a model learns to find the parts, not one design.

Never used for picture-making (a model must never learn to draw convincing bills): the kit puts the key in
NOT_FOR_PICTURE_MAKING. The generator is this file; with the same seed (SEED) it makes the same pages.

    python packs/synthetic_bills_packs.py synthetic_bills --limit 6 --save some-folder      (a quick check)
"""

import datetime
import random
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo

SEED = 9305
AMOUNT_Q = "How much do I owe?"
DUE_Q = "When is it due?"
HOLDER_Q = "Whose bill is this?"
PAY_Q = "How can I pay?"
KIND_Q = "What kind of document is this?"
WHERE_Q = "Where on the page is the amount due?"
CREDIT = ("A computer-made document drawn with Pillow by packs/synthetic_bills_packs.py (synthetic: made-up names, "
          "companies, addresses and amounts; not a real person's document), CC0")

FIRST = ("Maria", "James", "Aisha", "Wei", "Daniel", "Priya", "Robert", "Fatima", "Carlos", "Linda", "Kwame", "Sofia",
         "Thomas", "Mei", "Olivia", "Ahmed", "Grace", "Luis", "Hannah", "Samuel", "Nadia", "George", "Yuki", "Ruth")
LAST = ("Alvarez", "Brennan", "Okafor", "Lindqvist", "Marchetti", "Haddad", "Novak", "Pereira", "Tanaka", "Whitlow",
        "Osei", "Kowalski", "Delacroix", "Fenwick", "Iqbal", "Moreau", "Castellano", "Ashby", "Nakamura", "Quinlan")
STREETS = ("Juniper Lane", "Harrow Road", "Willowmere Drive", "Copperleaf Court", "Bramble Street", "Stonebridge Way",
           "Larkspur Avenue", "Fairhaven Road", "Thistle Close", "Morningside Terrace")
TOWNS = (("Maple Falls", "ON", "K0A 1B0"), ("Cedar Hollow", "OH", "45999"), ("Brookhaven Springs", "OR", "97999"),
         ("Port Ellery", "NS", "B0J 2C0"), ("Westmarch", "TX", "75999"), ("Silverlake Junction", "MN", "55999"))
# (kind, the words for it, made-up companies)
KINDS = [
    ("electricity", "an electricity bill", ("Riverbend Power & Light", "Northstar Electric Co-op")),
    ("gas", "a gas bill", ("Bluefield Gas Company", "Prairie Natural Gas")),
    ("water", "a water bill", ("Northgate Water Authority", "Clearbrook Water & Sewer")),
    ("phone", "a mobile phone bill", ("Brightline Mobile", "Signalwave Wireless")),
    ("bank", "a bank statement", ("Harborview Community Bank", "Lakeshore Savings Union")),
    ("card", "a credit-card statement", ("Summit Card Services", "Evergreen Rewards Card")),
    ("pharmacy", "a pharmacy receipt", ("Oakleaf Pharmacy", "Greenway Drug Store")),
    ("medical", "a medical bill", ("Lakeside Family Clinic", "St. Brigid Community Hospital")),
]
MEDICINES = ("Amoxicillin 500 mg capsules", "Lisinopril 10 mg tablets", "Metformin 500 mg tablets",
             "Atorvastatin 20 mg tablets", "Omeprazole 20 mg capsules", "Sertraline 50 mg tablets",
             "Levothyroxine 50 mcg tablets", "Albuterol inhaler 90 mcg")
PARTS = {("top", "left"): "near the top left", ("top", "right"): "near the top right",
         ("middle", "left"): "in the middle on the left", ("middle", "right"): "in the middle on the right",
         ("bottom", "left"): "at the bottom left", ("bottom", "right"): "at the bottom right",
         ("top", "middle"): "near the top, in the middle", ("middle", "middle"): "in the middle of the page",
         ("bottom", "middle"): "at the bottom, in the middle"}


def money(cents):
    """ "$1,284.07" from cents."""
    return f"${cents // 100:,}.{cents % 100:02d}"


def long_date(d):
    """ "12 December 2026"."""
    return f"{d.day} {d.strftime('%B')} {d.year}"


def page_part(x, y, width, height):
    """Where (x, y) lies on a width-by-height page, in words ("near the top right")."""
    row = "top" if y < height / 3 else "middle" if y < height * 2 / 3 else "bottom"
    col = "left" if x < width * 0.4 else "right" if x > width * 0.6 else "middle"
    return PARTS[(row, col)]


def details(n, seed=SEED):
    """The made-up facts of the n-th document (a dict): its kind, company, holder, address, dates, amounts, lines and
    ways to pay. The same n and seed give the same facts."""
    rng = random.Random(f"{seed}-{n}")
    kind, words, companies = KINDS[n % len(KINDS)] if rng.random() < 0.5 else rng.choice(KINDS)
    company = rng.choice(companies)
    holder = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    town, region, code = rng.choice(TOWNS)
    address = [f"{rng.randint(12, 9890)} {rng.choice(STREETS)}", f"{town}, {region} {code}"]
    issued = datetime.date(2026, 1, 1) + datetime.timedelta(days=rng.randint(0, 330))
    due = issued + datetime.timedelta(days=rng.choice((14, 21, 25, 28, 30)))
    slug = "".join(c for c in company.lower() if c.isalnum())
    stub = kind not in ("bank", "pharmacy") and rng.random() < 0.7
    phone = f"1-800-555-01{rng.randint(0, 99):02d}"
    account = f"****{rng.randint(1000, 9999)}"
    lines, amount = [], 0
    if kind in ("electricity", "gas", "water"):
        use = rng.randint(80, 1400)
        unit = {"electricity": "kWh", "gas": "therms", "water": "gallons x 100"}[kind]
        charge = use * rng.randint(9, 22)
        lines = [(f"Usage: {use} {unit}", charge), ("Delivery charge", rng.randint(900, 3500)),
                 ("Taxes and fees", rng.randint(150, 1200))]
    elif kind == "phone":
        lines = [("Monthly plan", rng.choice((3500, 4500, 6000, 7500))),
                 ("Device payment", rng.choice((0, 2083, 3333))),
                 ("Taxes and fees", rng.randint(300, 1100))]
    elif kind == "card":
        lines = [("Previous balance", rng.randint(0, 250000)), ("Purchases", rng.randint(2000, 180000)),
                 ("Payments and credits", -rng.randint(0, 150000)), ("Interest charged", rng.randint(0, 4000))]
    elif kind == "bank":
        lines = [("Opening balance", rng.randint(10000, 900000)), ("Deposits", rng.randint(0, 600000)),
                 ("Withdrawals and payments", -rng.randint(0, 500000))]
    elif kind == "pharmacy":
        lines = [(f"Rx {rng.randint(1000000, 9999999)} {rng.choice(MEDICINES)}", rng.randint(400, 4500))
                 for _ in range(rng.randint(1, 3))]
    else:
        lines = [("Office visit", rng.randint(9000, 30000)), ("Laboratory tests", rng.randint(2000, 15000)),
                 ("Insurance payment", -rng.randint(5000, 25000)), ("Insurance adjustment", -rng.randint(0, 6000))]
    if sum(c for _, c in lines) < 500:                       # the lines always add up to the amount shown
        lines.append(("Balance carried forward", 500 - sum(c for _, c in lines) + rng.randint(0, 3000)))
    amount = sum(c for _, c in lines)
    minimum = min(amount, max(2500, amount // 30)) if kind == "card" else 0
    ways = []
    if kind == "pharmacy":
        ways = ["Paid by card at the counter."]
    elif kind != "bank":
        ways = [f"online at www.{slug}.example/pay", f"by phone at {phone}"]
        if stub:
            ways.append(f"by cheque payable to {company}, sent with the stub at the bottom of the page")
        if rng.random() < 0.4:
            ways.append("by automatic payment from your bank account (sign up online)")
    return {"kind": kind, "words": words, "company": company, "holder": holder, "address": address,
            "issued": issued, "due": due, "account": account, "lines": lines, "amount": amount,
            "minimum": minimum, "ways": ways, "stub": stub, "phone": phone, "slug": slug, "rng": rng}


def draw_document(d):
    """The page of a document's details as a PIL image, and where its amount was drawn (x, y)."""
    from PIL import Image, ImageDraw
    rng = d["rng"]
    width, height = 1240, rng.choice((1650, 1754))
    paper = rng.choice([(255, 255, 255), (252, 250, 244), (246, 248, 252)])
    accent = rng.choice([(20, 70, 140), (0, 110, 90), (150, 30, 40), (90, 60, 140), (30, 30, 30), (200, 100, 0)])
    ink = (25, 25, 25)
    kind_font = rng.randrange(8)
    big, mid, small = font(40, True, kind_font), font(30, False, kind_font), font(24, False, kind_font)
    bold = font(30, True, kind_font)
    page = Image.new("RGB", (width, height), paper)
    draw = ImageDraw.Draw(page)
    y = 60
    if rng.random() < 0.6:                                   # a colour band with the company's name
        draw.rectangle([0, 0, width, 140], fill=accent)
        draw.text((60, 45), d["company"], font=big, fill=(255, 255, 255))
        y = 180
    else:
        draw.text((60, y), d["company"], font=big, fill=accent)
        draw.line([(60, y + 60), (width - 60, y + 60)], fill=accent, width=4)
        y += 90
    title = {"electricity": "ELECTRICITY BILL", "gas": "GAS BILL", "water": "WATER AND SEWER BILL",
             "phone": "WIRELESS STATEMENT", "bank": "ACCOUNT STATEMENT", "card": "CREDIT CARD STATEMENT",
             "pharmacy": "RECEIPT", "medical": "PATIENT STATEMENT"}[d["kind"]]
    draw.text((60, y), title, font=bold, fill=ink)
    draw.text((60, y + 50), f"Statement date: {d['issued'].strftime('%B %d, %Y')}", font=small, fill=ink)
    who = "Patient" if d["kind"] in ("medical", "pharmacy") else "Account holder"
    draw.text((60, y + 90), f"{who}: {d['holder']}", font=mid, fill=ink)
    for i, line in enumerate(d["address"]):
        draw.text((60, y + 135 + i * 36), line, font=small, fill=ink)
    draw.text((60, y + 215), f"Account number: {d['account']}", font=small, fill=ink)
    # The summary box, on the right or the left.
    box_left = rng.random() < 0.3
    bx = 60 if box_left else width - 560
    by = y + 270 if box_left else y
    draw.rectangle([bx, by, bx + 500, by + 250], outline=accent, width=4)
    label = {"bank": "Closing balance", "pharmacy": "Total paid", "card": "New balance"}.get(d["kind"], "Amount due")
    draw.text((bx + 25, by + 20), label, font=mid, fill=ink)
    amount_at = (bx + 250, by + 95)                         # the middle of the amount
    draw.text((bx + 25, by + 65), money(d["amount"]), font=font(54, True, kind_font),
              fill=accent if rng.random() < 0.5 else ink)
    if d["kind"] not in ("bank", "pharmacy"):
        draw.text((bx + 25, by + 145), f"Due by: {d['due'].strftime(rng.choice(('%B %d, %Y', '%m/%d/%Y')))}",
                  font=bold, fill=ink)
    if d["minimum"]:
        draw.text((bx + 25, by + 195), f"Minimum payment: {money(d['minimum'])}", font=small, fill=ink)
    # The lines.
    ty = max(y + 300, by + 290)
    draw.text((60, ty), "Details", font=bold, fill=accent)
    ty += 50
    for text, cents in d["lines"]:
        draw.text((80, ty), text, font=small, fill=ink)
        value = money(abs(cents))
        value = f"-{value}" if cents < 0 else value
        draw.text((width - 80 - draw.textlength(value, font=small), ty), value, font=small, fill=ink)
        ty += 40
    draw.line([(80, ty + 5), (width - 80, ty + 5)], fill=ink, width=2)
    # How to pay, and the stub.
    ty += 40
    if d["ways"]:
        draw.text((60, ty), "Ways to pay" if d["kind"] != "pharmacy" else "Payment", font=bold, fill=accent)
        for i, way in enumerate(d["ways"]):
            text = ("- Pay " + way) if d["kind"] != "pharmacy" else way
            size = 24
            while size > 14 and draw.textlength(text, font=font(size, False, kind_font)) > width - 140:
                size -= 1                                    # a long line is printed smaller, never cut off
            draw.text((80, ty + 50 + i * 38), text, font=font(size, False, kind_font), fill=ink)
        ty += 60 + len(d["ways"]) * 38
    draw.text((60, ty + 10), f"Questions? Call {d['phone']}", font=small, fill=ink)
    if d["stub"]:
        sy = height - 300
        for x in range(40, width - 40, 24):
            draw.line([(x, sy), (x + 12, sy)], fill=ink, width=2)
        draw.text((60, sy + 25), "Please return this portion with your payment", font=small, fill=ink)
        draw.text((60, sy + 75), d["holder"], font=mid, fill=ink)
        draw.text((60, sy + 115), f"Account {d['account']}", font=small, fill=ink)
        draw.text((width - 520, sy + 75), f"Amount due: {money(d['amount'])}", font=bold, fill=ink)
        draw.text((width - 520, sy + 125), f"Due: {d['due'].strftime('%m/%d/%Y')}", font=small, fill=ink)
    return page, amount_at, (width, height)


def document_rows(d, amount_at, size):
    """The question-and-answer rows of a document, from its own made-up facts."""
    rows = [{"question": KIND_Q, "answer": f"This is {d['words']} from {d['company']} (a made-up company)."}]
    if d["kind"] == "bank":
        rows.append({"question": "What is the balance?", "answer": f"The closing balance is {money(d['amount'])}."})
    elif d["kind"] == "pharmacy":
        rows.append({"question": "How much was paid?", "answer": f"The total paid was {money(d['amount'])}, by card."})
    else:
        text = f"The amount due is {money(d['amount'])}."
        if d["kind"] == "card":
            text = f"The new balance is {money(d['amount'])}; the minimum payment is {money(d['minimum'])}."
        rows.append({"question": AMOUNT_Q, "answer": text})
        rows.append({"question": DUE_Q, "answer": f"It is due by {long_date(d['due'])}."})
        rows.append({"question": WHERE_Q, "answer": f"It is in the box {page_part(*amount_at, *size)}, under "
                                                    f"\"{'New balance' if d['kind'] == 'card' else 'Amount due'}\"."})
    who = "The patient is" if d["kind"] in ("medical", "pharmacy") else "It is addressed to"
    rows.append({"question": HOLDER_Q if d["kind"] not in ("bank", "pharmacy") else "Whose name is on this?",
                 "answer": f"{who} {d['holder']}."})
    if d["kind"] not in ("bank", "pharmacy"):
        ways = d["ways"]
        rows.append({"question": PAY_Q, "answer": "The page says you can pay " + (", ".join(ways[:-1]) + ", or "
                                                                                 + ways[-1] if len(ways) > 1 else
                                                                                 ways[0]) + "."})
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows]


def make_document(n, seed=SEED):
    """The n-th document as (file name, JPEG bytes, rows)."""
    d = details(n, seed)
    page, amount_at, size = draw_document(d)
    data = phone_photo(page, d["rng"], strength=d["rng"].uniform(0.3, 1.0))
    return f"bill-{d['kind']}-{n:05d}.jpg", data, document_rows(d, amount_at, size)


def build_synthetic_bills(limit):
    """The synthetic_bills pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_document(n) for n in range(limit)])


# ----------------------------------------------------------------- the packs

SYNTHETIC_BILLS_PACKS = {
    "synthetic_bills": (build_synthetic_bills,
                        "Computer-made (synthetic) bills, statements and receipts drawn with Pillow by "
                        "packs/synthetic_bills_packs.py from a fixed seed: made-up people, companies, addresses and "
                        "amounts, not anyone's real documents. CC0."),
}
SYNTHETIC_BILLS_LIMITS = {
    "synthetic_bills": 4000,
}
SYNTHETIC_BILLS_COMMONS_KEYS = ()


def main(argv=None):
    """Make a few documents and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the synthetic bills pack builder.")
    parser.add_argument("key", choices=sorted(SYNTHETIC_BILLS_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = build_synthetic_bills(args.limit)
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
