"""Picture pack of FILLED-IN GOVERNMENT FORMS, computer-made (the owner's request of 2026-11-22: government forms with
their instructions; the reference books are textbooks/gov_forms.py). Used by build_packs.py in the same way as its
own PACKS: build_<key>(limit) returns [(file name, JPEG bytes or None, row)]; a picture with more than one question
comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

Why: a blind person who gets a filled-in tax or benefits form back (from an employer, a bank or a helper) wants to
check what was written in each box without reading private papers to someone else.

The pack (GOV_FORMS_PACKS):
  synthetic_gov_forms  COMPUTER-MADE filled-in forms laid out like the IRS Form W-4 (withholding certificate), Form
                       W-9 (taxpayer identification number request), Form 1099-NEC (nonemployee compensation) and the
                       SSA's Form SS-5 (application for a Social Security card), drawn here with Pillow from a fixed
                       seed and photographed by phone_photo.py, the same way as money_work_packs.py (helpers in
                       synthetic_documents.py). NEVER usable as real ones: SPECIMEN across every page and at its top,
                       the title says "SPECIMEN, not an IRS form" (or SSA form), made-up people, businesses and
                       towns, Social Security numbers beginning 000 and employer numbers beginning 00 (never issued).
                       Every answer is exact (the generator drew it). Every row is marked synthetic; never for
                       picture-making.
  Tax answers end with NOT_ADVICE (the same words as money_work_packs.py).

The blank official forms themselves are the us_federal_forms pack (packs/us_modern_packs.py) and the form books.

    python packs/gov_forms_packs.py synthetic_gov_forms --limit 8 --save some-folder      (a quick check)
"""

import datetime
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo
from synthetic_bills_packs import long_date, money
from synthetic_documents import (impossible_ein, impossible_ssn, made_up_address, made_up_person, not_real_row,
                                 seeded, specimen_marks)

SEED = 7731
NOT_ADVICE = "General information, not tax or legal advice; check the current rules or ask a professional."
CREDIT = ("A computer-made SPECIMEN form drawn with Pillow by packs/gov_forms_packs.py (synthetic: made-up people, "
          "businesses and amounts, impossible SSN and EIN; not a real form), CC0")
KIND_Q = "What kind of form is this?"
KINDS = ("w4", "w9", "nec", "ss5")
FILING = ("Single or Married filing separately", "Married filing jointly", "Head of household")
TAX_CLASS = ("Individual/sole proprietor", "C corporation", "S corporation", "Partnership",
             "Limited liability company (S)")
BUSINESSES = ("Maple Row Bakery", "Tidewater Tutoring LLC", "Northfield Lawn Care", "Crescent Web Studio",
              "Pinecone Cleaning Co.", "Brightwater Music Lessons")
CITIES = (("Clearwater Falls", "Ohio"), ("Dunmore Springs", "Kansas"), ("Lake Elsin", "Oregon"),
          ("Port Ambry", "Maine"), ("Redstone Hollow", "Utah"))


def details(kind, rng):
    """The made-up facts of one filled-in form of kind ("w4", "w9", "nec" or "ss5")."""
    first, last = made_up_person(rng)
    d = {"kind": kind, "first": first, "last": last, "ssn": impossible_ssn(rng), "address": made_up_address(rng),
         "signed": datetime.date(2026, 1, 5) + datetime.timedelta(days=rng.randint(0, 300))}
    if kind == "w4":
        children, others = rng.choice((0, 0, 1, 2, 3)), rng.choice((0, 0, 1))
        d.update(year=2026, filing=rng.choice(FILING), children=children, others=others,
                 dependents=children * 220000 + others * 50000, extra=rng.choice((0, 0, 2500, 5000, 10000)),
                 employer=rng.choice(BUSINESSES), ein=impossible_ein(rng))
    elif kind == "w9":
        d.update(business=rng.choice(BUSINESSES + ("",)), tax_class=rng.choice(TAX_CLASS),
                 requester=rng.choice(("Harbor Credit Union", "Oakline Property Management", "Summit Payroll Inc.")))
        if d["tax_class"] != "Individual/sole proprietor":
            d["ein"] = impossible_ein(rng)
    elif kind == "nec":
        comp = rng.randint(60000, 4800000)
        d.update(year=2025, payer=rng.choice(BUSINESSES), payer_ein=impossible_ein(rng), box1=comp,
                 box4=comp * rng.choice((0, 0, 0, 24)) // 100, account=f"{rng.randint(100, 999)}-{rng.randint(10, 99)}")
    else:
        city, state = rng.choice(CITIES)
        d.update(birth=datetime.date(rng.randint(1950, 2008), rng.randint(1, 12), rng.randint(1, 28)),
                 birthplace=f"{city}, {state}", citizenship="U.S. Citizen", sex=rng.choice(("Female", "Male")),
                 phone=f"(555) 555-01{rng.randint(0, 99):02d}")
    return d


TITLES = {"w4": "Form W-4 Employee's Withholding Certificate {year} (SPECIMEN, not an IRS form)",
          "w9": "Form W-9 Request for Taxpayer Identification Number and Certification (SPECIMEN, not an IRS form)",
          "nec": "Form 1099-NEC Nonemployee Compensation {year} (SPECIMEN, not an IRS form)",
          "ss5": "Form SS-5 Application for a Social Security Card (SPECIMEN, not an SSA form)"}


def field_list(d):
    """[(box label, value)] of the form's filled-in boxes, in the order they are drawn."""
    name = f"{d['first']} {d['last']}"
    street, town = d["address"]
    if d["kind"] == "w4":
        return [("Step 1(a) First name and last name", name), ("Address", street), ("City, state, ZIP", town),
                ("Step 1(b) Social security number", d["ssn"]), ("Step 1(c) Filing status", d["filing"]),
                ("Step 3 Claim dependents: total", money(d["dependents"])),
                ("Step 4(c) Extra withholding each pay period", money(d["extra"])),
                ("Employee's signature and date", f"{name}   {d['signed']:%m/%d/%Y}"),
                ("Employer's name and EIN", f"{d['employer']}   {d['ein']}")]
    if d["kind"] == "w9":
        rows = [("1 Name (as shown on your income tax return)", name),
                ("2 Business name, if different", d["business"] or "(left blank)"),
                ("3a Federal tax classification", d["tax_class"]), ("5 Address", street), ("6 City, state, ZIP", town),
                ("Part I Social security number", d["ssn"])]
        if d.get("ein"):
            rows.append(("Part I Employer identification number", d["ein"]))
        return rows + [("Requester's name", d["requester"]), ("Signature and date", f"{name}   {d['signed']:%m/%d/%Y}")]
    if d["kind"] == "nec":
        return [("PAYER'S name", d["payer"]), ("PAYER'S TIN", d["payer_ein"]), ("RECIPIENT'S TIN", d["ssn"]),
                ("RECIPIENT'S name", name), ("Street address", street), ("City, state, ZIP", town),
                ("Account number", d["account"]), ("1 Nonemployee compensation", money(d["box1"])),
                ("4 Federal income tax withheld", money(d["box4"]))]
    return [("1 Name to be shown on card", name), ("2 Place of birth", d["birthplace"]),
            ("3 Citizenship", d["citizenship"]), ("4 Sex", d["sex"]), ("6 Date of birth", f"{d['birth']:%m/%d/%Y}"),
            ("Social security number (if any)", d["ssn"]), ("Mailing address", f"{street}, {town}"),
            ("Phone number", d["phone"]), ("Signature and date", f"{name}   {d['signed']:%m/%d/%Y}")]


def draw_form(d, rng):
    """A filled-in form as a PIL image: its SPECIMEN title, then each labelled box with its typed value."""
    from PIL import Image, ImageDraw
    width, k = 1400, rng.randrange(8)
    fields = field_list(d)
    height = 260 + 104 * len(fields)
    page = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    ink, line = (20, 20, 20), rng.choice([(20, 20, 20), (170, 30, 30), (20, 60, 130)])
    draw.text((40, 80), TITLES[d["kind"]].format(year=d.get("year", "")), font=font(28, True, k), fill=line)
    y = 150
    for label, value in fields:
        draw.rectangle([40, y, width - 40, y + 96], outline=line, width=2)
        draw.text((52, y + 8), label, font=font(17, False, k), fill=line)
        draw.text((52, y + 42), value, font=font(30, True, k), fill=ink)
        y += 104
    return specimen_marks(page, kind_font=k)


def form_rows(d):
    """The rows of one filled-in form, from its own made-up facts."""
    name = f"{d['first']} {d['last']} (a made-up person)"
    kind = d["kind"]
    if kind == "w4":
        rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN filled-in form laid out like the IRS Form W-4, "
                 f"Employee's Withholding Certificate, for {d['year']}, filled in by {name}. {NOT_ADVICE}"},
                {"question": "What filing status is checked?", "answer": f"Step 1(c): {d['filing']}."},
                {"question": "How much is claimed for dependents?", "answer": f"Step 3 shows {money(d['dependents'])}"
                 f" ({d['children']} qualifying children and {d['others']} other dependents). {NOT_ADVICE}"},
                {"question": "Is extra tax withheld?", "answer": (f"Yes: Step 4(c) asks for {money(d['extra'])} extra "
                 "each pay period." if d["extra"] else "No: Step 4(c) shows $0.00.") + f" {NOT_ADVICE}"}]
    elif kind == "w9":
        rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN filled-in form laid out like the IRS Form W-9, "
                 f"Request for Taxpayer Identification Number and Certification, filled in by {name} for "
                 f"{d['requester']} (a made-up requester). {NOT_ADVICE}"},
                {"question": "What tax classification is checked?", "answer": f"Line 3a: {d['tax_class']}."},
                {"question": "What business name is written?", "answer": f"Line 2: {d['business']}." if d["business"]
                 else "Line 2 (business name) is left blank."}]
    elif kind == "nec":
        rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN form laid out like the IRS Form 1099-NEC, "
                 f"Nonemployee Compensation, for {d['year']}, from {d['payer']} (a made-up payer) to {name}. "
                 f"{NOT_ADVICE}"},
                {"question": "How much was I paid?", "answer": f"Box 1, nonemployee compensation: "
                 f"{money(d['box1'])}. {NOT_ADVICE}"},
                {"question": "Was any federal income tax withheld?", "answer": f"Box 4, federal income tax withheld: "
                 f"{money(d['box4'])}. {NOT_ADVICE}"}]
    else:
        rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN filled-in form laid out like the Social Security "
                 f"Administration's Form SS-5, Application for a Social Security Card, filled in for {name}."},
                {"question": "What date of birth is written?", "answer": f"Box 6: {long_date(d['birth'])}."},
                {"question": "What place of birth is written?", "answer": f"Box 2: {d['birthplace']} (a made-up "
                 f"town)."}]
    rows.append({"question": "What Social Security number is written?", "answer": f"{d['ssn']}: a made-up number "
                 "beginning 000, which is never issued."})
    words = {"w4": "a W-4 withholding certificate", "w9": "a W-9 form", "nec": "a 1099-NEC form",
             "ss5": "an SS-5 Social Security card application"}[kind]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row(words, CREDIT)]


def make_form(n, seed=SEED):
    """The n-th form (the four kinds in turn) as (file name, JPEG bytes, rows)."""
    rng = seeded(seed, n)
    d = details(KINDS[n % len(KINDS)], rng)
    data = phone_photo(draw_form(d, rng), rng, strength=rng.uniform(0.3, 1.0))
    return f"govform-{d['kind']}-{n:05d}.jpg", data, form_rows(d)


def build_synthetic_gov_forms(limit):
    """The synthetic_gov_forms pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_form(n) for n in range(limit)])


GOV_FORMS_PACKS = {
    "synthetic_gov_forms": (build_synthetic_gov_forms,
                            "Computer-made (synthetic) SPECIMEN filled-in forms laid out like the IRS W-4, W-9 and "
                            "1099-NEC and the SSA's SS-5, drawn with Pillow by packs/gov_forms_packs.py from a fixed "
                            "seed: made-up people, businesses and amounts, impossible SSN and EIN, never usable as "
                            "real forms. CC0."),
}
GOV_FORMS_LIMITS = {"synthetic_gov_forms": 2000}
GOV_FORMS_COMMONS_KEYS = ()


def main(argv=None):
    """Make a few forms and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the synthetic government forms pack builder.")
    parser.add_argument("key", choices=sorted(GOV_FORMS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = GOV_FORMS_PACKS[args.key][0](args.limit)
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
