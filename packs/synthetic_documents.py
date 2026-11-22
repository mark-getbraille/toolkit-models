"""Shared helpers for the COMPUTER-MADE (SYNTHETIC) document packs of the money and work, travel and civics
collections (packs/money_work_packs.py, packs/travel_packs.py, packs/civics_packs.py), in the same way as
packs/synthetic_bills_packs.py: every page is drawn here with Pillow from a fixed seed, with MADE-UP people,
companies and numbers, and photographed by phone_photo.py. Nothing is read, copied or downloaded.

The rule for these documents (the owner's): they must never be usable as real ones. So every page:
  - carries the word SPECIMEN (or SAMPLE for a sample ballot) large across it, at the top and in a corner
    (specimen_marks), and its rows say so ("Is this a real document?" -> "No ...");
  - uses only made-up names (the name lists of synthetic_bills_packs), made-up towns, web addresses under the
    reserved ".example" domain and phone numbers in the 555-01xx range set aside for fiction;
  - uses impossible numbers: Social Security numbers beginning 000 (never issued), employer numbers beginning 00
    (never issued), passports of "Utopia" (code UTO, the made-up country of the ICAO's own specimen passports) with
    a number containing letters no real one has.
The answers say only what the generator drew.
"""

import random

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from synthetic_bills_packs import FIRST, LAST, STREETS, TOWNS

SPECIMEN = "SPECIMEN"
NOT_REAL_Q = "Is this a real document?"


def made_up_person(rng):
    """(first name, last name) from the made-up name lists."""
    return rng.choice(FIRST), rng.choice(LAST)


def made_up_address(rng):
    """[street line, town line] of a made-up address."""
    town, region, code = rng.choice(TOWNS)
    return [f"{rng.randint(12, 9890)} {rng.choice(STREETS)}", f"{town}, {region} {code}"]


def impossible_ssn(rng):
    """A Social Security number that can never be real: the area number 000 is never issued."""
    return f"000-{rng.randint(10, 99):02d}-{rng.randint(1000, 9999)}"


def impossible_ein(rng):
    """An employer identification number that can never be real: the prefix 00 is never issued."""
    return f"00-{rng.randint(1000000, 9999999)}"


def fiction_phone(rng):
    """A phone number in the range set aside for fiction (555-0100 to 555-0199)."""
    return f"(555) 555-01{rng.randint(0, 99):02d}"


def specimen_marks(page, word=SPECIMEN, kind_font=0):
    """Draw word large and see-through across the page (diagonally), and again at its top right, so the page can
    never pass for a real document. Returns the page (an RGB PIL image)."""
    from PIL import Image, ImageDraw
    from phone_photo import font
    width, height = page.size
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    size = max(40, int(min(width, height) / 5))
    big = font(size, True, kind_font)
    text_w = draw.textlength(word, font=big)
    stamp = Image.new("RGBA", (int(text_w) + 40, size + 40), (0, 0, 0, 0))
    ImageDraw.Draw(stamp).text((20, 10), word, font=big, fill=(200, 0, 0, 110))
    stamp = stamp.rotate(28, expand=True)
    layer.paste(stamp, ((width - stamp.width) // 2, (height - stamp.height) // 2), stamp)
    small = font(max(18, size // 4), True, kind_font)
    label = f"{word} - NOT A REAL DOCUMENT"
    label_w = draw.textlength(label, font=small)
    draw.rectangle([width - label_w - 30, 4, width - 10, 18 + small.size], fill=(255, 255, 255, 235))
    draw.text((width - label_w - 20, 8), label, font=small, fill=(200, 0, 0, 255))
    out = Image.alpha_composite(page.convert("RGBA"), layer)
    return out.convert("RGB")


def wrap_lines(draw, text, font_, width):
    """text broken into lines that fit width pixels in font_ (a long line is never cut off)."""
    lines, line = [], ""
    for word in text.split():
        if line and draw.textlength(f"{line} {word}", font=font_) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + ([line] if line else [])


def not_real_row(words, credit):
    """The row every synthetic document has: it is not real, it is marked, and what it shows."""
    return {"question": NOT_REAL_Q, "answer": f"No. It is marked {SPECIMEN}: a computer-made example of {words} with "
                                              f"made-up details, not a real document.", "credit": credit,
            "synthetic": True}


def seeded(seed, n):
    """The random generator of the n-th document of a pack (the same n and seed give the same document)."""
    return random.Random(f"{seed}-{n}")
