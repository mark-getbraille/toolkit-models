"""Finding the pictures on the scanned pages of old civil defence booklets, and checking film stills: the shared
method of the civil defence picture packs (packs/civil_defense_packs.py, built on GitHub) and the kit's own civil
defence collections (kit/civil_defense_sources.py, downloaded on the user's computer). It needs only numpy and Pillow
(and pypdfium2 for the PDF pages), so both can use it; nothing here downloads anything.

WHY A METHOD OF ITS OWN. The booklets of the 1950s to 1980s (the US Federal Civil Defense Administration and Office of
Civil Defense, the UK Home Office, Canada's Emergency Measures Organization) were printed on paper and scanned page by
page: each PDF page is one photograph of the paper, with the words the Internet Archive read from it (OCR) laid over
it invisibly. So a drawing cannot be found from the PDF's own drawing commands (as packs/field_manual_packs.py does for
modern manuals). Instead, on each page:
  1. The page is drawn at PAGE_DPI dots per inch in shades of grey.
  2. The OCR words are joined into lines (text_lines). A line of running text (at least 5 words that look like real
     words, and wider than 38 percent of the page: body_line) is blanked out; short lines are kept, because the
     labels inside a drawing ("concrete block", "6 in.") are short.
  3. What is left that is dark (ink) is looked at in small squares; neighbouring inked squares are joined into
     pieces (find_regions), and a piece big enough (at least 18 percent of the page across and 12 percent down, and
     at least 4 percent of its area) is a picture. A dark scanning edge along the side of the page is not.
  4. Its caption (caption_for) is a line just under the picture or just over it: "Figure 5. Basement shelter",
     "Fig. 9.-Double-wall shelter", or a short separate line of real words close to the picture (not running
     text). Nothing is guessed: a picture with no such line has no caption, and the builders set it aside for a
     person to describe.
  5. Whether it is a drawing or a photograph (picture_kind): printed photographs are made of many grey dots
     (halftone), drawings are black lines on white paper. When it is not clear, it is called a picture.

FILM STILLS (still_problem). A still is not used when it is nearly all one shade (black, white or blank), too dark,
too blurred, or a title card (a plain background with lettering: almost the whole picture one shade with sharp
marks on it). The same tests the kit's video_frames.py uses for brightness, sharpness and repeats are used, with the
same numbers.

    python kit/civil_defense_figures.py BOOKLET.pdf OUT_FOLDER      (a quick check: saves the pictures it finds)
"""

import io
import re

PAGE_DPI = 150              # pages are drawn at this many dots per inch
INK = 150                   # a grey shade (0 black to 255 white) darker than this is ink
CELL = 8                    # pages are looked at in squares of this many pixels
CELL_INK = 0.03             # a square with more than this share of ink is inked
JOIN = 3                    # inked squares this many squares apart (or nearer) belong to the same piece
LEAST_WIDE, LEAST_HIGH, LEAST_AREA = 0.18, 0.12, 0.04     # a picture's smallest size, in shares of the page
MOST_FILLED = 0.92          # a piece whose box is more inked than this is a black block or scanning edge
BODY_WIDE = 0.38            # running text: a line at least this share of the page wide ...
BODY_WORDS = 5              # ... with at least this many words that look like words
CAPTION_NEAR = 0.045        # a caption is at most this share of the page height from its picture
CAPTION_MOST_WORDS = 40
CAPTION_LINES = 3
PLAIN_CAPTION_WORDS = 15    # a caption without "Figure" has at most this many words
# Page headings that sit under or over a drawing but are not its caption.
HEADING = re.compile(r"^(general information|technical summary|contents|introduction|appendix|notes?|section [a-z0-9]"
                     r"+|page \d+)$", re.I)
MOST_WORDS = 0.22           # a "picture" whose box is more covered than this by lines of real words is printed words

# A caption that names the figure: "Figure 5", "Fig. 9.-Double-wall shelter", "FIGURE 12 Shelter plan".
FIGURE = re.compile(r"^\s*(?:fig(?:ure)?|plate|illustration|diagram)\s*\.?\s*([0-9]{1,3}[a-z]?|[IVX]{1,5})\b"
                    r"\s*[.:,;\-–—]*\s*(.*)$", re.I)
def figure_match(text):
    """FIGURE matched on a line, with OCR's stray hyphens inside words taken out first ("Figur-e 3")."""
    return FIGURE.match(re.sub(r"^(\s*[Ff]i-?g-?u-?r-?e)", lambda m: m.group(1).replace("-", ""), text))


WORD = re.compile(r"^[\"'(]?[A-Za-z][a-z]*(?:['’-][A-Za-z]+)*[.,;:!?)\"']{0,2}$|^[A-Z][A-Z-]+[.,:]?$|"
                  r"^\d+(?:[./-]\d+)*(?:\s?(?:in|ft|cm|mm)\.?)?[.,]?$")


# ----------------------------------------------------------------- the shared words

# Words that make a picture's row graphic (the kit's graphic choice: war, attack, injuries and death), medical, or a
# child's; and words that keep a picture, booklet or film out altogether (births, nudity and sex, the dead).
GRAPHIC = re.compile(r"\b(blasts?|explo\w*|fireballs?|mushroom|detonat\w*|bomb\w*|ground zero|destroy\w*|destruction|"
                     r"damage\w*|ruins?|rubble|wreck\w*|casualt\w*|injur\w*|wound\w*|burns?|burned|burning|bleed\w*|"
                     r"dead|death|deaths|killed|dying|bodies|corpses?|victims?|fire ?storms?|atomic attack|nuclear "
                     r"attack|under attack|enemy attack|h-bomb|a-bomb|hydrogen bomb|warfare|gas attack|war)\b", re.I)
MEDICAL = re.compile(r"\b(first aid|bandag\w*|splint\w*|artificial respiration|resuscitat\w*|tourniquet|nursing|"
                     r"medical|medicine|health care|patients?|stretchers?|fractur\w*|pulse|sick\w*|ill|illness)\b",
                     re.I)
CHILD = re.compile(r"\b(child\w*|kids?|boys?|girls?|bab(y|ies)|infants?|toddlers?|teen\w*|youngsters?|youth|4-H|"
                   r"pupils?|schoolchild\w*|schools?|students?|classrooms?|kindergarten\w*|sons?|daughters?)\b", re.I)
# Never used: births (the birth rules need a person's check), nudity and sex, and films about the dead and injured.
LEAVE_OUT = re.compile(r"\b(child ?birth|obstetric\w*|maternity|deliver(y|ing) (a |the )?bab\w*|nud\w*|naked|"
                       r"sex\w*|hiroshima|nagasaki|victims|corpses?|dead bodies)\b", re.I)


# ----------------------------------------------------------------- words on the page

def word_share(text):
    """The share of the tokens of text that look like ordinary words or numbers (OCR of a drawing gives "/s/ f/oar")."""
    tokens = [t.strip("._") for t in text.split()]
    tokens = [t for t in tokens if re.search(r"[A-Za-z0-9]", t)]           # dot leaders and dashes are not words
    if not tokens:
        return 0.0
    return sum(1 for t in tokens if WORD.match(t)) / len(tokens)


def text_lines(textpage, page_height):
    """The OCR words of a pypdfium2 text page joined into lines: [{"box": (left, top, right, bottom) in points from
    the top left, "text"}], top to bottom. Words whose middles are at the same height (within half a word's height)
    form a band; a band is cut where two words are more than three word-heights apart (two columns)."""
    rects = []
    for i in range(textpage.count_rects()):
        left, bottom, right, top = textpage.get_rect(i)
        if right - left < 0.5 or top - bottom < 0.5:
            continue
        rects.append((left, page_height - top, right, page_height - bottom))
    if not rects:
        return []
    heights = sorted(r[3] - r[1] for r in rects)
    usual = heights[len(heights) // 2]
    rects.sort(key=lambda r: (r[1] + r[3]) / 2)
    bands, middle = [], None
    for r in rects:
        centre = (r[1] + r[3]) / 2
        if bands and abs(centre - middle) <= 0.5 * usual:
            bands[-1].append(r)
            middle = sum((b[1] + b[3]) / 2 for b in bands[-1]) / len(bands[-1])
        else:
            bands.append([r])
            middle = centre
    boxes = []
    for band in bands:
        band.sort(key=lambda r: r[0])
        piece = [band[0]]
        for r in band[1:]:
            if r[0] - max(p[2] for p in piece) > 3 * usual:
                boxes.append(piece)
                piece = []
            piece.append(r)
        boxes.append(piece)
    out = []
    for piece in boxes:
        left, top = min(r[0] for r in piece), min(r[1] for r in piece)
        right, bottom = max(r[2] for r in piece), max(r[3] for r in piece)
        words = textpage.get_text_bounded(left=left - 0.5, bottom=page_height - bottom - 0.5, right=right + 0.5,
                                          top=page_height - top + 0.5)
        words = " ".join(words.split())
        if words:
            out.append({"box": (left, top, right, bottom), "text": words})
    out.sort(key=lambda ln: (ln["box"][1], ln["box"][0]))
    return out


def body_line(line, page_width):
    """True for a line of running text (see the module docstring), which is not part of any picture."""
    left, _, right, _ = line["box"]
    tokens = line["text"].split()
    return right - left >= BODY_WIDE * page_width and len(tokens) >= BODY_WORDS and word_share(line["text"]) >= 0.6


def paragraph_lines(lines):
    """Mark as running text ("body": True) the short lines of a paragraph too (its first and last lines, "from
    fallout."): a line of real words right above or below a line of running text, overlapping it sideways. lines are
    in pixels or points, top to bottom; changed in place."""
    for _ in range(3):
        changed = False
        for i, ln in enumerate(lines):
            if ln["body"] or word_share(ln["text"]) < 0.75:
                continue
            left, top, right, bottom = ln["box"]
            height = bottom - top
            for other in lines[max(0, i - 3):i + 4]:
                if other is ln or not other["body"]:
                    continue
                o_left, o_top, o_right, o_bottom = other["box"]
                close = min(abs(o_top - bottom), abs(top - o_bottom)) <= 0.9 * height
                if close and o_left < right and left < o_right:
                    ln["body"] = changed = True
                    break
        if not changed:
            break


# ----------------------------------------------------------------- the pictures on a page

def find_regions(gray, blanked=()):
    """The boxes (x0, y0, x1, y1, in pixels) of the pictures on a page drawn in grey (a 2-D numpy array), with the
    boxes in blanked (pixels; the running text) not counted as ink. Biggest first."""
    import numpy as np
    height, width = gray.shape
    ink = gray < INK
    for x0, y0, x1, y1 in blanked:
        ink[max(0, int(y0) - 2):int(y1) + 3, max(0, int(x0) - 2):int(x1) + 3] = False
    rows, cols = height // CELL, width // CELL
    if rows < 4 or cols < 4:
        return []
    cells = ink[:rows * CELL, :cols * CELL].reshape(rows, CELL, cols, CELL).mean(axis=(1, 3)) > CELL_INK
    seen = np.zeros_like(cells, dtype=bool)
    found = []
    for r0, c0 in zip(*np.nonzero(cells)):
        if seen[r0, c0]:
            continue
        stack, members = [(r0, c0)], []
        seen[r0, c0] = True
        while stack:
            r, c = stack.pop()
            members.append((r, c))
            for rr in range(max(0, r - JOIN), min(rows, r + JOIN + 1)):
                for cc in range(max(0, c - JOIN), min(cols, c + JOIN + 1)):
                    if cells[rr, cc] and not seen[rr, cc]:
                        seen[rr, cc] = True
                        stack.append((rr, cc))
        rs = [m[0] for m in members]
        cs = [m[1] for m in members]
        box = (min(cs) * CELL, min(rs) * CELL, (max(cs) + 1) * CELL, (max(rs) + 1) * CELL)
        found.append((box, len(members)))
    out = []
    for (x0, y0, x1, y1), count in found:
        w, h = x1 - x0, y1 - y0
        if w < LEAST_WIDE * width or h < LEAST_HIGH * height or w * h < LEAST_AREA * width * height:
            continue
        if count * CELL * CELL > MOST_FILLED * w * h and (w < 0.05 * width or h < 0.05 * height or w * h > 0.5 *
                                                           width * height):
            continue                                     # a solid black bar or the dark edge of the scan
        if (x0 <= CELL or x1 >= width - CELL) and w < 0.08 * width:
            continue                                     # a thin dark edge along the side of the page
        out.append((x0, y0, x1, y1))
    out.sort(key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    return out


def picture_kind(gray):
    """"photograph", "drawing" or "picture" for a picture cut from a page (grey numpy array): a printed photograph has
    many middle greys (its halftone dots, blurred by the scan), a drawing hardly any."""
    import numpy as np
    total = gray.size or 1
    middle = float(np.count_nonzero((gray > 70) & (gray < 190))) / total
    dark = float(np.count_nonzero(gray <= 70)) / total
    if middle > 0.35 and dark + middle > 0.5:
        return "photograph"
    if middle < 0.12:
        return "drawing"
    return "picture"


def caption_for(box, lines, page_height):
    """(label, caption words) for a picture box (pixels) from the page's lines (pixels, as text_lines but scaled):
    a "Figure N" line or a short separate line of words just under or over the picture; ("", "") when there is none.
    label is the figure's number ("5") when the caption names one."""
    x0, y0, x1, y1 = box
    near = CAPTION_NEAR * page_height
    lines = [ln for ln in lines if not ln.get("body") or figure_match(ln["text"])]
    below = [ln for ln in lines if y1 - 4 <= ln["box"][1] <= y1 + near and ln["box"][2] > x0 and ln["box"][0] < x1]
    above = [ln for ln in reversed(lines) if y0 - near <= ln["box"][3] <= y0 + 4 and ln["box"][2] > x0
             and ln["box"][0] < x1]
    inside = [ln for ln in lines if ln["box"][1] >= y0 - 2 and ln["box"][3] <= y1 + 2]
    for ln in inside + below + above:                      # a line naming the figure wins, wherever it is
        m = figure_match(ln["text"])
        if m:
            rest = m.group(2)
            if ln in below or ln in inside:                   # a caption can go on to the next line
                more = block_after(ln, lines)
                rest = " ".join([rest] + [b["text"] for b in more]).strip()
            return m.group(1), tidy_caption(rest)
    if below:                       # a short separate line under the picture, within its width
        block = [below[0]] + block_after(below[0], lines)[:1]
        words = " ".join(b["text"] for b in block)
        after = lines.index(block[-1]) + 1
        separate = after >= len(lines) or lines[after]["box"][1] - block[-1]["box"][3] > \
            0.9 * (block[-1]["box"][3] - block[-1]["box"][1])
        margin = 0.05 * (x1 - x0)
        within = all(b["box"][0] >= x0 - margin and b["box"][2] <= x1 + margin for b in block)
        if separate and within and len(words.split()) <= PLAIN_CAPTION_WORDS and caption_ok(words, strict=True):
            return "", tidy_caption(words)
    return "", ""


def block_after(line, lines):
    """The lines that follow line closely (a caption that goes on), at most CAPTION_LINES - 1 of them."""
    out, last = [], line
    for ln in lines[lines.index(line) + 1:]:
        height = last["box"][3] - last["box"][1]
        if ln["box"][1] - last["box"][3] > 1.0 * height or len(out) >= CAPTION_LINES - 1:
            break
        out.append(ln)
        last = ln
    return out


def tidy_caption(text):
    """A caption without its leading dashes and dots, broken words joined ("con- crete" -> "concrete"), and with
    its own full stop taken off (the answer adds one)."""
    text = re.sub(r"(\w)- (\w)", r"\1\2", " ".join(str(text or "").split()))
    text = re.sub(r"^[\s.:;,\-–—]+", "", text).rstrip(" .;:,-")
    if text.isupper():                       # "ABOVEGROUND DOUBLE-WALL SHELTER" -> "Aboveground double-wall shelter"
        text = text[:1] + text[1:].lower()
    return text


def caption_ok(text, strict=False):
    """True when a caption has at least two words of three letters or more and is mostly real words (not OCR noise
    such as "E L E V A T o N" or "BILL OF MATIIRIAiS"). strict (a caption without "Figure"): nearly all real words,
    starting with a letter, and not a page heading ("General information")."""
    long_words = [t for t in text.split() if len(re.sub(r"[^A-Za-z]", "", t)) >= 3]
    if re.match(r"^([IVX]+|[A-Z]|\d+)\.\s", text):
        return False                                # a section heading ("II. The Shelters"), not a caption
    if strict and (not re.match(r"^[\"'(]?[A-Za-z]", text) or word_share(text) < 0.9 or re.search(r"[!|{}<>\\]", text)
                   or HEADING.match(text.strip())):
        return False
    return len(long_words) >= 2 and word_share(text) >= 0.8


def centred_in(line_box, box):
    """True when the middle of a line's box is inside a picture's box."""
    middle_x, middle_y = (line_box[0] + line_box[2]) / 2, (line_box[1] + line_box[3]) / 2
    return box[0] <= middle_x <= box[2] and box[1] <= middle_y <= box[3]


def words_cover(box, lines):
    """The share of a picture box covered by lines of real words (at least two words, most of them real): high for a
    list, a table of contents or a block of small print that was taken for a picture, low for a drawing with labels."""
    x0, y0, x1, y1 = box
    area = 0.0
    for ln in lines:
        left, top, right, bottom = ln["box"]
        if centred_in(ln["box"], box) and len(ln["text"].split()) >= 2 and word_share(ln["text"]) >= 0.6:
            area += (min(right, x1) - max(left, x0)) * (min(bottom, y1) - max(top, y0))
    return area / max(1.0, float((x1 - x0) * (y1 - y0)))


def labels_inside(box, lines):
    """The words printed inside a picture (its labels, "concrete block"), as read by the OCR: kept only as hints for
    the people who describe the pictures that have no caption."""
    x0, y0, x1, y1 = box
    words = [ln["text"] for ln in lines if centred_in(ln["box"], box) and word_share(ln["text"]) >= 0.75]
    return "; ".join(words)[:300]


def page_figures(page, dpi=PAGE_DPI):
    """The pictures on one scanned page (a pypdfium2 page): [{"jpeg", "box" (pixels), "label", "caption",
    "labels", "kind", "share" (of the page)}], biggest first."""
    import numpy as np
    width_pt, height_pt = page.get_size()
    scale = dpi / 72
    image = page.render(scale=scale).to_pil().convert("L")
    gray = np.asarray(image)
    height, width = gray.shape
    textpage = page.get_textpage()
    lines = []
    for ln in text_lines(textpage, height_pt):
        left, top, right, bottom = ln["box"]
        lines.append({"box": (left * scale, top * scale, right * scale, bottom * scale), "text": ln["text"],
                      "body": body_line(ln, width_pt)})
    paragraph_lines(lines)
    blanked = [ln["box"] for ln in lines if ln["body"] or figure_match(ln["text"])]
    out = []
    for box in find_regions(gray, blanked):
        x0, y0, x1, y1 = box
        if words_cover(box, lines) > MOST_WORDS:
            continue                    # a list, a table of contents or small print: words, not a picture
        pad = 6
        crop = image.crop((max(0, x0 - pad), max(0, y0 - pad), min(width, x1 + pad), min(height, y1 + pad)))
        label, caption = caption_for(box, lines, height)
        buffer = io.BytesIO()
        crop.convert("RGB").save(buffer, "JPEG", quality=90)
        out.append({"jpeg": buffer.getvalue(), "box": box, "label": label, "caption": caption,
                    "labels": labels_inside(box, lines), "kind": picture_kind(np.asarray(crop)),
                    "share": (x1 - x0) * (y1 - y0) / float(width * height)})
    return out


# ----------------------------------------------------------------- film stills

DARK = 40                   # as video_frames.DARK: a still whose mean brightness is below this is too dark
BRIGHT = 235                # ... and above this, a white or washed-out frame
FLAT = 14.0                 # a still whose shades vary less than this (standard deviation) is blank
SHARP_LEAST = 12.0          # as video_frames.SHARP_LEAST: sharpness below this is always too blurred
CARD_SHARE = 0.50           # a title card: at least this share of the picture (made smaller, so film grain is
CARD_SPREAD = 20            # smoothed) within CARD_SPREAD shades of its commonest shade, its shades varying less
CARD_STD = 32.0             # than CARD_STD in all (a plain background), and sharp marks (lettering) on at least
CARD_EDGES = 0.004          # CARD_EDGES of it
EDGE_BAND = 0.15            # burned-in marks and frame lines are looked for this far in from each edge ...
MARK_LINE = 0.08            # ... in lines (rows or columns) where at least this share stays sharp and still, or
FRAME_LINE = 0.35           # where an edge runs along the line in at least this share of the stills (frame lines)


def sharpness(gray):
    """How sharp a grey picture (2-D numpy array) is: the variance of its Laplacian, as video_frames.sharpness."""
    import numpy as np
    g = gray.astype(np.float32)
    lap = g[1:-1, :-2] + g[1:-1, 2:] + g[:-2, 1:-1] + g[2:, 1:-1] - 4 * g[1:-1, 1:-1]
    return float(lap.var())


def fingerprint(gray):
    """A 64-bit picture fingerprint (pHash, as video_frames.fingerprint): pictures that look alike are close."""
    import numpy as np
    from PIL import Image
    small = np.asarray(Image.fromarray(gray).resize((32, 32), Image.BILINEAR), dtype=np.float32)
    n = np.arange(32)
    dct = np.cos(np.pi * (2 * n[None, :] + 1) * n[:, None] / 64).astype(np.float32)
    low = (dct @ small @ dct.T)[:8, :8].flatten()
    bits = low > np.median(low[1:])
    return int("".join("1" if b else "0" for b in bits), 2)


def distance(a, b):
    """How many of the 64 bits of two fingerprints differ."""
    return bin(a ^ b).count("1")


def still_problem(gray, sharp_floor=SHARP_LEAST):
    """Why a film still (grey numpy array, about 320 to 640 pixels wide) is not used, or "" when it may be:
    "too dark", "a white frame", "a blank frame", "blurred", "a title card"."""
    import numpy as np
    mean, spread = float(gray.mean()), float(gray.std())
    if mean < DARK:
        return "too dark"
    if mean > BRIGHT:
        return "a white frame"
    if spread < FLAT:
        return "a blank frame"
    if sharpness(gray) < sharp_floor:
        return "blurred"
    from PIL import Image
    smooth = np.asarray(Image.fromarray(gray).resize((160, max(2, 160 * gray.shape[0] // gray.shape[1])),
                                                     Image.BILINEAR))
    counts = np.bincount(smooth.ravel(), minlength=256)
    mode = int(counts.argmax())
    plain = counts[max(0, mode - CARD_SPREAD):mode + CARD_SPREAD + 1].sum() / float(smooth.size)
    edges = float((np.abs(np.diff(gray.astype(np.int16), axis=1)) > 50).mean())
    if plain >= CARD_SHARE and spread < CARD_STD and edges >= CARD_EDGES:
        return "a title card"
    return ""


def black_borders(grays):
    """(top, bottom, left, right) rows and columns of black bars (letterbox) that every still of a film has: the
    lines whose mean shade over all the stills is under 18. grays: grey numpy arrays of the same size."""
    import numpy as np
    stack = np.stack(grays).astype(np.float32)
    rows, cols = stack.mean(axis=(0, 2)), stack.mean(axis=(0, 1))

    def run(values):
        """How many lines from the start are black."""
        n = 0
        while n < len(values) // 4 and values[n] < 18:
            n += 1
        return n
    return run(rows), run(rows[::-1]), run(cols), run(cols[::-1])


def fixed_marks(grays):
    """Where a film keeps sharp marks near its edges while the rest of the picture changes (a burned-in logo, a time
    code, or the frame lines and sprocket edges of a full-frame film scan), from grey numpy arrays of its stills (all
    the same size; 128 pixels wide is enough): the shares of the picture to cut off at the (top, bottom, left, right)
    to leave them out, each at most EDGE_BAND. (0, 0, 0, 0) when there are none, the film is too short to tell (fewer
    than 12 stills) or the picture hardly changes."""
    import numpy as np
    if len(grays) < 12:
        return 0.0, 0.0, 0.0, 0.0
    stack = np.stack(grays).astype(np.float32)
    moving = stack.std(axis=0)
    if float((moving > 14).mean()) < 0.6:
        return 0.0, 0.0, 0.0, 0.0
    across = (np.abs(np.diff(stack, axis=2)) > 24).mean(axis=0)              # how often each spot is an edge
    down = (np.abs(np.diff(stack, axis=1)) > 24).mean(axis=0)
    marks = np.zeros(moving.shape, dtype=bool)                                # still marks: logos, time codes
    marks[:, 1:] |= across > 0.6
    marks[1:, :] |= down > 0.6
    marks &= moving < 9
    height, width = marks.shape
    band_y, band_x = max(1, int(height * EDGE_BAND)), max(1, int(width * EDGE_BAND))
    row_lines = np.zeros(height, dtype=bool)                                  # frame lines: a line across the
    row_lines[1:] = down.mean(axis=1) >= FRAME_LINE                           # picture in most stills, even when
    col_lines = np.zeros(width, dtype=bool)                                   # it shakes a little
    col_lines[1:] = across.mean(axis=0) >= FRAME_LINE

    def depth(rows, lines):
        """How deep (in lines from the edge) the marks or frame lines reach within the band: rows is the band and
        lines its frame-line flags, edge first."""
        hits = [i for i, row in enumerate(rows) if row.mean() >= MARK_LINE or lines[i]]
        return (max(hits) + 2) if hits else 0
    top = depth(marks[:band_y], row_lines[:band_y])
    bottom = depth(marks[::-1][:band_y], row_lines[::-1][:band_y])
    left = depth(marks[:, :band_x].T, col_lines[:band_x])
    right = depth(marks[:, ::-1][:, :band_x].T, col_lines[::-1][:band_x])
    return top / height, bottom / height, left / width, right / width


def main(argv=None):
    """Save the pictures found in one PDF booklet into a folder, with their captions (a quick check)."""
    import os
    import sys
    import pypdfium2 as pdfium
    argv = argv if argv is not None else sys.argv[1:]
    path, out = argv[0], argv[1]
    os.makedirs(out, exist_ok=True)
    doc = pdfium.PdfDocument(path)
    for n in range(len(doc)):
        for i, fig in enumerate(page_figures(doc[n])):
            name = f"p{n + 1:03d}-{i}.jpg"
            with open(os.path.join(out, name), "wb") as f:
                f.write(fig["jpeg"])
            print(name, fig["kind"], f"{fig['share']:.2f}", repr(fig["label"]), repr(fig["caption"]),
                  "| labels:", fig["labels"][:80])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
