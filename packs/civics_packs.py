"""Picture packs for CITIZENSHIP AND CIVICS (the owner's request of 2026-11-22). Used by build_packs.py in the same way
as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture
with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The
limit counts pictures.

Why: a sample ballot comes in the mail before an election and a jury summons comes from the court; a blind voter or
juror needs to know what is on them (the contests and choices, how to mark a choice, when and where to report)
without a sighted helper.

The pack (CIVICS_PACKS):
  synthetic_civic_documents  COMPUTER-MADE sample ballots and jury summonses, drawn here with Pillow from a fixed seed
                             and photographed by phone_photo.py, the same way as synthetic_bills_packs.py (helpers in
                             synthetic_documents.py). NEVER usable as real ones: SPECIMEN across every page and at its
                             top, made-up places ("Example County"), made-up candidates and measures, made-up courts,
                             phone numbers in the 555-01xx range set aside for fiction and web addresses under
                             ".example". Every answer is exact (the generator drew it): the election and its date, the
                             contests and their choices, how many to vote for, how to mark the ballot; the summons'
                             court, date, time and place to report, juror number, and how to ask to be excused. Every
                             row is marked synthetic; never for picture-making. Legal answers end with NOT_ADVICE.

    python packs/civics_packs.py synthetic_civic_documents --limit 4 --save some-folder      (a quick check)
"""

import datetime
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from phone_photo import font, phone_photo
from synthetic_bills_packs import long_date
from synthetic_documents import (fiction_phone, made_up_address, made_up_person, not_real_row, seeded, specimen_marks,
                                 wrap_lines)

SEED = 9413
NOT_ADVICE = "General information, not tax or legal advice; check the current rules or ask a professional."
CREDIT = ("A computer-made SPECIMEN document drawn with Pillow by packs/civics_packs.py (synthetic: made-up places, "
          "candidates, measures and courts; not a real ballot or summons), CC0")
KIND_Q = "What kind of document is this?"
COUNTIES = ("Example County", "Specimen County", "Sample Valley County", "Fictional Lake County")
OFFICES = ("Mayor of Port Ellery", "City Council, District 3", "County Commissioner", "School Board Member",
           "County Clerk", "Sheriff of Example County", "Library Board Trustee", "Water District Director")
MEASURES = ("Measure A: shall the town build a new public library, paid for by a bond of $4,000,000?",
            "Measure B: shall the county add a quarter-cent sales tax for road repair for ten years?",
            "Measure C: shall the city keep parks open one hour later in summer?",
            "Measure D: shall the school district renew its existing parcel tax for arts programmes?")
COURTS = ("Superior Court of Example County", "District Court of Specimen County", "Circuit Court of Sample Valley")


def ballot_details(rng):
    """The made-up facts of a sample ballot: the election, its date, the contests (with how many to vote for) and
    the measures."""
    county = rng.choice(COUNTIES)
    day = datetime.date(2026, 11, 3) if rng.random() < 0.5 else datetime.date(2027, rng.choice((3, 4, 6)),
                                                                                rng.randint(1, 28))
    contests = []
    for office in rng.sample(OFFICES, rng.randint(2, 3)):
        people = [" ".join(made_up_person(rng)) for _ in range(rng.randint(2, 4))]
        contests.append((office, rng.choice((1, 1, 1, 2)) if office.startswith(("City Council", "School")) else 1,
                         list(dict.fromkeys(people))))
    measures = rng.sample(MEASURES, rng.randint(1, 2))
    return {"kind": "ballot", "county": county, "day": day, "contests": contests, "measures": measures,
            "mark": rng.choice(("Fill in the oval completely next to your choice", "Connect the arrow pointing to "
                                                                                      "your choice"))}


def summons_details(rng):
    """The made-up facts of a jury summons: the court, the juror, the date, time and place to report."""
    first, last = made_up_person(rng)
    day = datetime.date(2026, 1, 5) + datetime.timedelta(days=7 * rng.randint(0, 50))
    return {"kind": "summons", "first": first, "last": last, "court": rng.choice(COURTS), "day": day,
            "time": rng.choice(("8:00 AM", "8:30 AM", "9:00 AM")), "juror": f"{rng.randint(100000, 999999)}",
            "place": f"{rng.randint(100, 999)} Courthouse Plaza, Room {rng.randint(101, 420)}",
            "address": made_up_address(rng), "phone": fiction_phone(rng),
            "web": f"jury.{rng.choice(('examplecounty', 'specimencourt', 'samplevalley'))}.example"}


def draw_ballot(d, rng):
    """A sample ballot as a PIL image: the heading, the marking instruction, each contest with its ovals."""
    from PIL import Image, ImageDraw
    width, height, k = 1240, 1700, rng.randrange(8)
    page = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    ink = (20, 20, 20)
    draw.text((50, 110), f"SAMPLE BALLOT - {d['county'].upper()}", font=font(38, True, k), fill=ink)
    draw.text((50, 165), f"Election of {d['day']:%B %d, %Y}", font=font(28, False, k), fill=ink)
    draw.rectangle([50, 215, width - 50, 275], outline=ink, width=3)
    draw.text((65, 230), f"INSTRUCTIONS: {d['mark']}. Use a black pen.", font=font(24, True, k), fill=ink)
    y = 310
    for office, many, people in d["contests"]:
        draw.rectangle([50, y, width - 50, y + 52], fill=(225, 225, 225))
        draw.text((65, y + 10), f"{office}  (Vote for {many})", font=font(27, True, k), fill=ink)
        y += 65
        for person in people:
            draw.ellipse([80, y + 4, 120, y + 30], outline=ink, width=3)
            draw.text((140, y), person, font=font(27, False, k), fill=ink)
            y += 48
        y += 20
    for measure in d["measures"]:
        draw.rectangle([50, y, width - 50, y + 52], fill=(225, 225, 225))
        title, question = measure.split(": ", 1)
        draw.text((65, y + 10), title, font=font(27, True, k), fill=ink)
        y += 65
        for line in wrap_lines(draw, question, font(24, False, k), width - 160):
            draw.text((80, y), line, font=font(24, False, k), fill=ink)
            y += 34
        y += 12
        for choice in ("YES", "NO"):
            draw.ellipse([80, y + 4, 120, y + 30], outline=ink, width=3)
            draw.text((140, y), choice, font=font(27, False, k), fill=ink)
            y += 48
        y += 20
    return specimen_marks(page, kind_font=k)


def draw_summons(d, rng):
    """A jury summons as a PIL image: the court, the juror, when and where to report, and how to ask to be
    excused."""
    from PIL import Image, ImageDraw
    width, height, k = 1240, 1500, rng.randrange(8)
    page = Image.new("RGB", (width, height), (252, 251, 246))
    draw = ImageDraw.Draw(page)
    ink = (20, 20, 20)
    lines = [(d["court"].upper(), 34, True), ("SUMMONS FOR JURY SERVICE", 34, True), ("", 20, False),
             (f"{d['first']} {d['last']}", 28, True), (d["address"][0], 26, False), (d["address"][1], 26, False),
             ("", 20, False), (f"Juror number: {d['juror']}", 28, True),
             (f"Report on: {d['day']:%A, %B %d, %Y} at {d['time']}", 28, True), (f"Report to: {d['place']}", 26, False),
             ("", 20, False), (f"Before your date, call the juror line after 5 PM the evening before, or check the "
                               f"website, to learn whether you must report: {d['phone']}, {d['web']}", 24, False),
             ("", 20, False), ("To ask to be excused or to postpone your service, return the enclosed form or reply "
                               "online within 10 days. Tell the court if you need an accommodation for a disability.",
                               24, False)]
    y = 130
    for text, size, bold in lines:
        for line in wrap_lines(draw, text, font(size, bold, k), width - 120) or [""]:
            draw.text((60, y), line, font=font(size, bold, k), fill=ink)
            y += size + 14
    return specimen_marks(page, kind_font=k)


def ballot_rows(d):
    """The rows of a sample ballot, from its own made-up facts."""
    contests = "; ".join(f"{o} (vote for {m}): {', '.join(p)}" for o, m, p in d["contests"])
    rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN sample ballot for {d['county']} (a made-up county), "
                                          f"for the election of {long_date(d['day'])}."},
            {"question": "What is on this ballot?", "answer": f"The contests are: {contests}. The measures are: "
             f"{' '.join(d['measures'])} Each measure is answered yes or no. (Made-up candidates and measures.)"},
            {"question": "How do I mark my choices?", "answer": f"The instructions say: {d['mark']}, with a black pen. "
             f"Voters who are blind can ask for an accessible voting machine at the polling place."}]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row("a sample ballot", CREDIT)]


def summons_rows(d):
    """The rows of a jury summons, from its own made-up facts."""
    rows = [{"question": KIND_Q, "answer": f"This is a SPECIMEN jury summons from the {d['court']} (a made-up court) "
                                          f"for {d['first']} {d['last']} (a made-up person)."},
            {"question": "When and where do I report?", "answer": f"On {long_date(d['day'])} at {d['time']}, at "
                                                                 f"{d['place']}. {NOT_ADVICE}"},
            {"question": "What is my juror number?", "answer": f"Juror number {d['juror']}."},
            {"question": "How do I find out whether I must go, or ask to be excused?", "answer": f"It says to call "
             f"{d['phone']} or check {d['web']} the evening before, and to return the enclosed form or reply online "
             f"within 10 days to ask to be excused or postponed; it asks you to tell the court if you need an accommodation "
             f"for a disability. {NOT_ADVICE}"}]
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows] + [not_real_row("a jury summons", CREDIT)]


def make_document(n, seed=SEED):
    """The n-th document (ballots and summonses in turn) as (file name, JPEG bytes, rows)."""
    rng = seeded(seed, n)
    if n % 2 == 0:
        d = ballot_details(rng)
        page, rows = draw_ballot(d, rng), ballot_rows(d)
    else:
        d = summons_details(rng)
        page, rows = draw_summons(d, rng), summons_rows(d)
    data = phone_photo(page, rng, strength=rng.uniform(0.3, 1.0))
    return f"civic-{d['kind']}-{n:05d}.jpg", data, rows


def build_synthetic_civic_documents(limit):
    """The synthetic_civic_documents pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_document(n) for n in range(limit)])


CIVICS_PACKS = {
    "synthetic_civic_documents": (build_synthetic_civic_documents,
                                  "Computer-made (synthetic) SPECIMEN sample ballots and jury summonses drawn with "
                                  "Pillow by packs/civics_packs.py from a fixed seed: made-up places, candidates, "
                                  "measures and courts, never usable as real documents. CC0."),
}
CIVICS_LIMITS = {"synthetic_civic_documents": 1500}
CIVICS_COMMONS_KEYS = ()


def main(argv=None):
    """Make a few documents and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try the synthetic civic documents pack builder.")
    parser.add_argument("key", choices=sorted(CIVICS_PACKS))
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = CIVICS_PACKS[args.key][0](args.limit)
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
