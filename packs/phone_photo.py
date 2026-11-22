"""Shared helpers for the COMPUTER-MADE (synthetic) picture packs (care_label_packs.py, synthetic_bills_packs.py):
fonts found on the build machine, and "phone photo" effects that make a clean drawing look like a photo a blind person
took with a phone: a background around it, a slight turn and tilt (perspective), uneven light, a little blur, noise and
JPEG compression. Everything is drawn here with Pillow from a fixed random seed, so the same pack comes out the same
every time; nothing is downloaded.

    python packs/phone_photo.py      (writes a sample picture to phone-photo-sample.jpg in the current folder)
"""

import glob
import io
import os

FONT_FOLDERS = ("/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
                "C:/Windows/Fonts", "/Library/Fonts", "/System/Library/Fonts")
# Families that look like the type on real bills and labels (sans, serif and monospaced), when they are installed.
FONT_NAMES = ("DejaVuSans", "DejaVuSerif", "DejaVuSansMono", "LiberationSans", "LiberationSerif", "LiberationMono",
              "FreeSans", "FreeSerif", "FreeMono", "NotoSans-", "NotoSerif-", "arial", "times", "cour", "verdana")
_FONTS = {}


def font_files():
    """The regular and bold TrueType fonts of FONT_NAMES found on this machine (sorted, so the choice is the same on
    every run of one machine), or [] when none is installed (the helpers then use Pillow's own font)."""
    if "files" not in _FONTS:
        found = []
        for folder in FONT_FOLDERS:
            found += glob.glob(os.path.join(folder, "**", "*.ttf"), recursive=True)
        keep = [f for f in found if any(os.path.basename(f).startswith(n) for n in FONT_NAMES)
                and not any(w in os.path.basename(f) for w in ("Oblique", "Italic", "Condensed", "ExtraLight",
                                                                "Light", "Thin"))]
        _FONTS["files"] = sorted(set(keep))
    return _FONTS["files"]


def font(size, bold=False, kind=0):
    """A font of the given pixel size: the kind-th installed font (bold ones when bold), else Pillow's own."""
    from PIL import ImageFont
    files = [f for f in font_files() if ("Bold" in f or "bd" in os.path.basename(f).lower()) == bold] or font_files()
    if files:
        path = files[kind % len(files)]
        key = (path, size)
        if key not in _FONTS:
            _FONTS[key] = ImageFont.truetype(path, size)
        return _FONTS[key]
    return ImageFont.load_default(size)


def phone_photo(picture, rng, background=None, strength=1.0):
    """The picture (a PIL image) as if photographed with a phone: on a background (a colour or a table-like
    surface), turned up to 6 degrees, tilted in perspective, with uneven light, a little blur and noise; returns JPEG
    bytes. strength 0 gives a flat scan-like copy; 1 the usual amount."""
    from PIL import Image, ImageDraw, ImageFilter
    import random
    rng = rng or random.Random(0)
    w, h = picture.size
    margin = int(max(w, h) * (0.06 + 0.10 * rng.random() * strength))
    bg = background or rng.choice([(120, 98, 74), (200, 196, 188), (66, 70, 78), (230, 226, 214), (150, 130, 110),
                                   (34, 40, 48), (180, 160, 140)])
    canvas = Image.new("RGB", (w + 2 * margin, h + 2 * margin), bg)
    grain = ImageDraw.Draw(canvas)
    for _ in range(int((w + h) * 0.4)):                 # a little texture in the table or cloth
        x, y = rng.randrange(canvas.width), rng.randrange(canvas.height)
        shade = tuple(max(0, min(255, c + rng.randint(-14, 14))) for c in bg)
        grain.line([(x, y), (x + rng.randint(-30, 30), y + rng.randint(-3, 3))], fill=shade)
    canvas.paste(picture.convert("RGB"), (margin, margin))
    # A slight turn, then a perspective tilt (the phone not held flat).
    canvas = canvas.rotate(rng.uniform(-6, 6) * strength, resample=Image.BICUBIC, expand=False, fillcolor=bg)
    cw, ch = canvas.size
    d = 0.05 * strength
    quad = [(cw * rng.uniform(0, d), ch * rng.uniform(0, d)), (cw * rng.uniform(0, d), ch * (1 - rng.uniform(0, d))),
            (cw * (1 - rng.uniform(0, d)), ch * (1 - rng.uniform(0, d))), (cw * (1 - rng.uniform(0, d)),
                                                                           ch * rng.uniform(0, d))]
    canvas = canvas.transform((cw, ch), Image.QUAD, [c for p in quad for c in p], resample=Image.BICUBIC,
                              fillcolor=bg)
    # Uneven light: a soft gradient from one side, sometimes a shadow band.
    light = Image.new("L", (cw, ch), 0)
    draw = ImageDraw.Draw(light)
    side, top = rng.random() < 0.5, rng.randint(0, 70)
    for i in range(cw if side else ch):
        v = int(top * i / max(1, (cw if side else ch)) * strength)
        draw.line([(i, 0), (i, ch)] if side else [(0, i), (cw, i)], fill=v)
    if rng.random() < 0.3 * strength:
        x = rng.randrange(cw)
        draw.rectangle([x, 0, x + cw // 5, ch], fill=90)
    canvas = Image.composite(Image.new("RGB", (cw, ch), (0, 0, 0)), canvas, light.filter(ImageFilter.GaussianBlur(40)))
    if strength:
        canvas = canvas.filter(ImageFilter.GaussianBlur(rng.uniform(0.2, 1.3) * strength))
        tile = Image.frombytes("RGB", (96, 96), rng.randbytes(96 * 96 * 3))   # seeded, so the picture repeats
        noise = Image.new("RGB", (cw, ch))
        for nx in range(0, cw, 96):
            for ny in range(0, ch, 96):
                noise.paste(tile, (nx, ny))
        canvas = Image.blend(canvas, noise, 0.03 * strength)
    if max(canvas.size) > 1280:
        canvas.thumbnail((1280, 1280))
    out = io.BytesIO()
    canvas.save(out, "JPEG", quality=rng.randint(70, 90))
    return out.getvalue()


if __name__ == "__main__":
    import random
    from PIL import Image, ImageDraw
    sample = Image.new("RGB", (600, 400), "white")
    ImageDraw.Draw(sample).text((40, 40), "Amount due: $84.17", font=font(36, True), fill="black")
    with open("phone-photo-sample.jpg", "wb") as f:
        f.write(phone_photo(sample, random.Random(1)))
    print(f"{len(font_files())} fonts found; wrote phone-photo-sample.jpg")
