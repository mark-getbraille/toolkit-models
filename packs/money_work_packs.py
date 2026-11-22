"""Picture packs for MONEY, WORK AND BUSINESS (the owner's request of 2026-11-22). Used by build_packs.py in the same
way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture
with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The
limit counts pictures.

Why: pay stubs and the yearly wage and tax statement (a W-2) come on paper or as a printed PDF, and a blind worker
has to find the gross and net pay, the hours, the deductions and the year's totals without a sighted helper reading
private papers.

The pack (MONEY_WORK_PACKS):
  synthetic_pay_documents  COMPUTER-MADE pay stubs and wage and tax statements laid out like a W-2, drawn here with
                           Pillow from a fixed seed and photographed by phone_photo.py, the same way as
                           synthetic_bills_packs.py (helpers in synthetic_documents.py). NEVER usable as real ones:
                           SPECIMEN across every page and at its top, made-up people and employers, Social Security
                           numbers beginning 000 and employer numbers beginning 00 (never issued). Every answer is
                           exact (the generator drew it): the gross and net pay, the pay period and pay date, the hours
                           and rate, each deduction, the year-to-date totals, and the W-2's boxes 1 to 6. Every row is
                           marked synthetic; never for picture-making.
  Tax answers end with NOT_ADVICE ("General information, not tax or legal advice; check the current rules or ask a
  professional."), the same words as the reference books (textbooks/money_work.py).

Not repeated here: bills, bank and card statements and pharmacy and medical receipts (synthetic_bills), banknotes and
coins (the currency and money packs), cheques and receipts of the document collections.

    python packs/money_work_packs.py synthetic_pay_documents --limit 6 --save some-folder      (a quick check)
"""

import datetime
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo
from synthetic_bills_packs import long_date, money
from synthetic_documents import (impossible_ein, impossible_ssn, made_up_address, made_up_person, not_real_row,
                                 seeded, specimen_marks)

SEED = 9412
NOT_ADVICE = "General information, not tax or legal advice; check the current rules or ask a professional."
CREDIT = ("A computer-made SPECIMEN document drawn with Pillow by packs/money_work_packs.py (synthetic: made-up people, "
          "employers and amounts, impossible SSN and EIN; not a real document), CC0")
EMPLOYERS = ("Riverbend Hardware Co.", "Summit Valley Clinic", "Bluefield Logistics LLC", "Harborview Grocers",
             "Copperleaf Call Center", "Larkspur Public Library", "Northgate Manufacturing", "Evergreen Home Care")
KIND_Q = "What kind of document is this?"


def stub_details(rng):
    """The made-up facts of a pay stub: hours, rate, deductions and the year's totals (they always add up)."""
    first, last = made_up_person(rng)
    rate = rng.randint(1500, 4800)                      # cents an hour
    hours = rng.choice((32, 36, 40, 40, 40, 80))
    overtime = rng.choice((0, 0, 0, 2, 4, 6)) if hours in (40, 80) else 0
    gross = rate * hours + rate * 3 // 2 * overtime
    federal, ss, medicare = gross * rng.randint(6, 14) // 100, gross * 62 // 1000, gross * 145 // 10000
    state = gross * rng.randint(0, 6) // 100
    health = rng.choice((0, 0, 4250, 6875, 9120))
    retire = gross * rng.choice((0, 0, 3, 5)) // 100
    deductions = [("Federal income tax", federal), ("Social Security tax", ss), ("Medicare tax", medicare)]
    if state:
        deductions.append(("State income tax", state))
    if health:
        deductions.append(("Health insurance", health))
    if retire:
        deductions.append(("401(k) retirement", retire))
    net = gross - sum(c for _, c in deductions)
    end = datetime.date(2026, 1, 9) + datetime.timedelta(days=14 * rng.randint(0, 24))
    start = end - datetime.timedelta(days=13 if hours == 80 else 6)
    paid = end + datetime.timedelta(days=rng.choice((3, 5, 6)))
    periods = rng.randint(1, 24)
    return {"kind": "stub", "first": first, "last": last, "employer": rng.choice(EMPLOYERS), "rate": rate,
            "hours": hours, "overtime": overtime, "gross": gross, "deductions": deductions, "net": net,
            "start": start, "end": end, "paid": paid, "ytd_gross": gross * periods, "ytd_net": net * periods,
            "address": made_up_address(rng), "id": f"E{rng.randint(1000, 9999)}"}


def w2_details(rng):
    """The made-up facts of a wage and tax statement laid out like a W-2 (boxes 1 to 6)."""
    first, last = made_up_person(rng)
    wages = rng.randint(1800000, 9500000)
    retire = wages * rng.choice((0, 3, 6)) // 100
    return {"kind": "w2", "first": first, "last": last, "employer": rng.choice(EMPLOYERS), "year": 2025,
            "ssn": impossible_ssn(rng), "ein": impossible_ein(rng), "box1": wages - retire,
            "box2": (wages - retire) * rng.randint(7, 15) // 100, "box3": wages, "box4": wages * 62 // 1000,
            "box5": wages, "box6": wages * 145 // 10000, "address": made_up_address(rng)}


def draw_stub(d, rng):
    """A pay stub as a PIL image: the employer and employee, the pay period, earnings, deductions and net pay."""
    from PIL import Image, ImageDraw
    width, height, k = 1240, 1100, rng.randrange(8)
    page = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    ink, accent = (25, 25, 25), rng.choice([(20, 70, 140), (0, 110, 90), (120, 40, 60), (40, 40, 40)])
    draw.text((50, 70), d["employer"], font=font(40, True, k), fill=accent)
    draw.text((50, 125), "EARNINGS STATEMENT (PAY STUB)", font=font(30, True, k), fill=ink)
    draw.text((50, 180), f"Employee: {d['first']} {d['last']}   ID {d['id']}", font=font(26, False, k), fill=ink)
    draw.text((50, 220), f"Pay period: {d['start']:%m/%d/%Y} to {d['end']:%m/%d/%Y}", font=font(26, False, k),
              fill=ink)
    draw.text((50, 260), f"Pay date: {d['paid']:%m/%d/%Y}", font=font(26, True, k), fill=ink)
    y = 330
    draw.text((50, y), "Earnings", font=font(28, True, k), fill=accent)
    lines = [(f"Regular {d['hours']} hours at {money(d['rate'])}", d["rate"] * d["hours"])]
    if d["overtime"]:
        lines.append((f"Overtime {d['overtime']} hours at {money(d['rate'] * 3 // 2)}", d["rate"] * 3 // 2 *
                      d["overtime"]))
    lines.append(("Gross pay", d["gross"]))
    for text, cents in lines:
        y += 42
        draw.text((80, y), text, font=font(25, text == "Gross pay", k), fill=ink)
        draw.text((width - 300, y), money(cents), font=font(25, text == "Gross pay", k), fill=ink)
    y += 70
    draw.text((50, y), "Deductions", font=font(28, True, k), fill=accent)
    for text, cents in d["deductions"]:
        y += 42
        draw.text((80, y), text, font=font(25, False, k), fill=ink)
        draw.text((width - 300, y), f"-{money(cents)}", font=font(25, False, k), fill=ink)
    y += 70
    draw.rectangle([50, y, width - 50, y + 80], outline=accent, width=4)
    draw.text((80, y + 20), "NET PAY", font=font(34, True, k), fill=ink)
    draw.text((width - 330, y + 20), money(d["net"]), font=font(34, True, k), fill=ink)
    y += 120
    draw.text((80, y), f"Year to date: gross {money(d['ytd_gross'])}, net {money(d['ytd_net'])}",
              font=font(24, False, k), fill=ink)
    return specimen_marks(page, kind_font=k)


def draw_w2(d, rng):
    """A wage and tax statement laid out like a W-2 (boxes a to f and 1 to 6) as a PIL image."""
    from PIL import Image, ImageDraw
    width, height, k = 1400, 900, rng.randrange(8)
    page = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    ink, red = (20, 20, 20), (170, 30, 30)
    draw.text((40, 70), f"Form W-2 Wage and Tax Statement {d['year']} (SPECIMEN, not an IRS form)",
              font=font(30, True, k), fill=red)

    def box(x, y, w, h, label, value):
        """One labelled box."""
        draw.rectangle([x, y, x + w, y + h], outline=red, width=2)
        draw.text((x + 8, y + 6), label, font=font(15, False, k), fill=red)
        draw.text((x + 8, y + 34), value, font=font(26, True, k), fill=ink)
    box(40, 130, 620, 90, "a  Employee's social security number", d["ssn"])
    box(40, 220, 620, 90, "b  Employer identification number (EIN)", d["ein"])
    box(40, 310, 620, 150, "c  Employer's name and address", d["employer"])
    box(40, 460, 620, 180, "e/f  Employee's name and address", f"{d['first']} {d['last']}")
    draw.text((48, 540), "\n".join(d["address"]), font=font(22, False, k), fill=ink)
    labels = [("1  Wages, tips, other compensation", d["box1"]), ("2  Federal income tax withheld", d["box2"]),
              ("3  Social security wages", d["box3"]), ("4  Social security tax withheld", d["box4"]),
              ("5  Medicare wages and tips", d["box5"]), ("6  Medicare tax withheld", d["box6"])]
    for i, (label, cents) in enumerate(labels):
        box(680 + (i % 2) * 340, 130 + (i // 2) * 110, 330, 110, label, money(cents))
    return specimen_marks(page, kind_font=k)


def stub_rows(d):
    """The rows of a pay stub, from its own made-up facts."""
    deduction_words = "; ".join(f"{t} {money(c)}" for t, c in d["deductions"])
    rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN pay stub (earnings statement) from {d['employer']} "
                                          f"(a made-up employer) for {d['first']} {d['last']} (a made-up person)."},
            {"question": "How much was I paid?", "answer": f"Net pay (take-home pay) is {money(d['net'])}; gross pay "
                                                          f"before deductions is {money(d['gross'])}."},
            {"question": "What pay period and pay date does it show?", "answer": f"The pay period is "
             f"{long_date(d['start'])} to {long_date(d['end'])}, paid on {long_date(d['paid'])}."},
            {"question": "How many hours, at what rate?", "answer": f"{d['hours']} regular hours at "
             f"{money(d['rate'])} an hour" + (f", and {d['overtime']} overtime hours at {money(d['rate'] * 3 // 2)}"
                                              if d["overtime"] else "") + "."},
            {"question": "What was taken out?", "answer": f"The deductions are: {deduction_words}. {NOT_ADVICE}"},
            {"question": "What are the year-to-date totals?", "answer": f"Year to date: gross {money(d['ytd_gross'])}, "
                                                                       f"net {money(d['ytd_net'])}."}]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row("a pay stub", CREDIT)]


def w2_rows(d):
    """The rows of a W-2-like statement, from its own made-up facts."""
    rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN wage and tax statement laid out like a Form W-2 for "
                                          f"{d['year']}, from {d['employer']} (a made-up employer) to {d['first']} "
                                          f"{d['last']} (a made-up person). {NOT_ADVICE}"},
            {"question": "What are my wages for the year?", "answer": f"Box 1, wages, tips and other compensation: "
             f"{money(d['box1'])}. Box 3, Social Security wages: {money(d['box3'])}. Box 5, Medicare wages: "
             f"{money(d['box5'])}. {NOT_ADVICE}"},
            {"question": "How much federal tax was withheld?", "answer": f"Box 2, federal income tax withheld: "
             f"{money(d['box2'])}. Box 4, Social Security tax: {money(d['box4'])}. Box 6, Medicare tax: "
             f"{money(d['box6'])}. {NOT_ADVICE}"},
            {"question": "What Social Security number is printed?", "answer": f"Box a shows {d['ssn']}: a made-up "
             f"number beginning 000, which is never issued."}]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row("a W-2 wage and tax statement",
                                                                                  CREDIT)]


def make_document(n, seed=SEED):
    """The n-th document (two pay stubs to every W-2) as (file name, JPEG bytes, rows)."""
    rng = seeded(seed, n)
    if n % 3 == 2:
        d = w2_details(rng)
        page, rows = draw_w2(d, rng), w2_rows(d)
    else:
        d = stub_details(rng)
        page, rows = draw_stub(d, rng), stub_rows(d)
    data = phone_photo(page, rng, strength=rng.uniform(0.3, 1.0))
    return f"pay-{d['kind']}-{n:05d}.jpg", data, rows


def build_synthetic_pay_documents(limit):
    """The synthetic_pay_documents pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_document(n) for n in range(limit)])


MONEY_WORK_PACKS = {
    "synthetic_pay_documents": (build_synthetic_pay_documents,
                                "Computer-made (synthetic) SPECIMEN pay stubs and W-2-like wage and tax statements "
                                "drawn with Pillow by packs/money_work_packs.py from a fixed seed: made-up people, "
                                "employers and amounts, impossible SSN and EIN, never usable as real documents. CC0."),
}
MONEY_WORK_LIMITS = {"synthetic_pay_documents": 2500}
MONEY_WORK_COMMONS_KEYS = ()


def main(argv=None):
    """Make a few documents and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the synthetic pay documents pack builder.")
    parser.add_argument("key", choices=sorted(MONEY_WORK_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = MONEY_WORK_PACKS[args.key][0](args.limit)
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
