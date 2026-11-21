"""Reading scanned pages for the Writing Kit (OCR, optical character recognition), all on this computer.

Why this engine: RapidOCR (the "rapidocr" package, Apache License 2.0) is installed with one pip command, needs no
separate program, and carries its small text-reading models inside the package, so nothing is downloaded when it
runs and nothing is sent anywhere. It runs on the computer's processor with ONNX Runtime (MIT licence); no graphics
card is needed. It is a text reader only, not an AI vision model that describes pictures. Tesseract was the other
choice, but on Windows it needs its own installer besides Python. PDF pages are drawn as pictures with pypdfium2
(Apache 2.0 or BSD), which also reads the text of pages that already have real text.

  available()                  (True, "") when the engine can be used, otherwise (False, what to install)
  read_pdf(data, ...)          yields one Page per PDF page: its text, confidence score and picture
  fix_header_line(line)        a header line with common OCR mistakes corrected ("Frorn:" becomes "From:")
  mask_page_image(page, mask)  the page picture with identity, card and bank numbers and passwords blacked out

Confidence: the engine gives each line of text a score from 0 to 1. A page's score is the average over its lines,
weighted by their length. Pages under MIN_PAGE_CONFIDENCE (or with almost no text) are left out, and the reason is
written to the log the build saves (scanned-pages-left-out.txt). Lines under MIN_LINE_CONFIDENCE are dropped.
"""

import io
import os
import re
from dataclasses import dataclass, field

ENGINE_NAME = "RapidOCR 3.10 (Apache 2.0) with ONNX Runtime, run on this computer"
INSTALL_HINT = "pip install -r kit\\requirements-ocr.txt"
RENDER_DPI = 200                  # how sharply each PDF page is drawn before it is read
MIN_PAGE_CONFIDENCE = 0.80        # pages scoring below this are left out
MIN_LINE_CONFIDENCE = 0.50        # single lines scoring below this are dropped
MIN_PAGE_WORDS = 8                # pages with fewer words than this are left out (blank, cover or stamp pages)

_engine = None


@dataclass
class Page:
    """One PDF page as read: number (from 1), text, confidence (0 to 1), method ("ocr" or "text layer"), kept (True
    when it is good enough), reason (why it was left out), png (the page picture), lines ([(text, score, box)])."""
    number: int
    text: str = ""
    confidence: float = 0.0
    method: str = "ocr"
    kept: bool = False
    reason: str = ""
    png: bytes = b""
    lines: list = field(default_factory=list)
    size: tuple = (0, 0)


class OcrUnavailable(Exception):
    """Raised when the OCR engine or the PDF reader is not installed."""


def available():
    """(True, "") when RapidOCR, ONNX Runtime and pypdfium2 are installed with RapidOCR's own models; otherwise
    (False, a plain sentence saying what to install)."""
    try:
        import pypdfium2  # noqa: F401
        import onnxruntime  # noqa: F401
        import rapidocr
    except ImportError as err:
        return False, f"the OCR reader is not installed ({err.name} is missing); type: {INSTALL_HINT}"
    models = os.path.join(os.path.dirname(rapidocr.__file__), "models")
    if not os.path.isdir(models) or not [n for n in os.listdir(models) if n.endswith(".onnx")]:
        # without its bundled models RapidOCR would try to download them; the kit never lets it
        return False, "RapidOCR's own models are missing; reinstall it with: " + INSTALL_HINT
    return True, ""


def engine():
    """The one RapidOCR engine of this run (made the first time it is needed, which takes a second or two)."""
    global _engine
    if _engine is None:
        ok, why = available()
        if not ok:
            raise OcrUnavailable(why)
        import logging
        from rapidocr import RapidOCR
        _engine = RapidOCR(params={"Global.log_level": "error"})
        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
    return _engine


def lines_to_text(lines):
    """The text of a page from its OCR lines [(text, score, box)], in reading order: pieces at the same height are
    joined left to right, and a larger gap between lines starts a new paragraph (a blank line)."""
    items = []
    for text, score, box in lines:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        items.append((min(ys), max(ys), min(xs), text))
    items.sort()
    rows = []                                   # [[top, bottom, [(x, text)]]]
    for top, bottom, x, text in items:
        if rows:
            r = rows[-1]
            overlap = min(bottom, r[1]) - max(top, r[0])
            if overlap > 0.5 * min(bottom - top, r[1] - r[0]):
                r[2].append((x, text))
                r[0], r[1] = min(r[0], top), max(r[1], bottom)
                continue
        rows.append([top, bottom, [(x, text)]])
    if not rows:
        return ""
    heights = sorted(r[1] - r[0] for r in rows)
    line_h = max(1.0, heights[len(heights) // 2])
    out, last_bottom = [], None
    for top, bottom, parts in rows:
        if last_bottom is not None and top - last_bottom > 0.9 * line_h:
            out.append("")
        out.append(" ".join(t for _, t in sorted(parts)))
        last_bottom = bottom
    return "\n".join(out)


# Common OCR mistakes in email header words: each pattern matches a misread header word at the start of a line.
HEADER_FIXES = [
    ("From", r"(?:F|P|E)\s?(?:r|n)\s?(?:o|0|a|c)\s?(?:m|rn|n|nn|in)"),
    ("Sent", r"(?:S|5)\s?(?:e|c|o)\s?(?:n|r|m)\s?(?:t|l|f|1)"),
    ("To", r"(?:T|I)\s?(?:o|0|c)"),
    ("Cc", r"(?:C|c)\s?(?:c|C|e)"),
    ("Bcc", r"(?:B|8)\s?cc"),
    ("Subject", r"(?:S|5)\s?(?:u|n)\s?(?:b|h)\s?(?:j|i|l|f)\s?(?:e|c|o)\s?(?:c|e|o)\s?(?:t|l|f|1)"),
    ("Date", r"(?:D|O)\s?(?:a|o)\s?(?:t|l|f)\s?(?:e|c)"),
    ("Attachments", r"Attach\s?(?:m|rn)\s?(?:e|c)\s?(?:n|r)\s?(?:t|l)\s?(?:s|5)?"),
    ("Importance", r"Importance"),
]
_FIX_RES = [(word, re.compile(r"^(\s*)" + pattern + r"\s*([:;.,])\s*")) for word, pattern in HEADER_FIXES]
LOOSE_STOP = {"From", "Sent", "Subject"}    # header words OCR often ends with "." or "," instead of ":"


def fix_header_line(line):
    """line with its header word corrected when it starts with a misread one ("Frorn;" or "Sen t." become "From:"
    and "Sent:"). Other lines come back unchanged. "Attachment:" stays singular when it was written so."""
    for word, regex in _FIX_RES:
        m = regex.match(line)
        if m:
            if m.group(2) in ".," and word not in LOOSE_STOP:
                return line              # "To." or "Date," at a line start is too often an ordinary sentence
            if word == "Attachments" and not re.search(r"[s5]\s*[:;.,]", m.group(0)):
                word = "Attachment"
            return m.group(1) + word + ": " + line[m.end():]
    return line


def _page_image(page, dpi):
    """The PIL picture of a pypdfium2 page drawn at dpi, in grey."""
    return page.render(scale=dpi / 72.0, grayscale=True).to_pil()


def _has_images(page):
    import pypdfium2.raw as pdfium_c
    return any(True for _ in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE], max_depth=2))


def read_pdf(data, first=1, last=None, dpi=RENDER_DPI, keep_images=True, only_image_pages=False,
             min_confidence=MIN_PAGE_CONFIDENCE):
    """Yield a Page for each page of the PDF in data (bytes), from page first to page last (counted from 1). A page
    with real text and no pictures is read as text (confidence 1); every other page is drawn and read with OCR.
    only_image_pages skips the pages with no pictures at all (used for hearing records, whose own text is read
    elsewhere). The page picture (PNG) is kept when keep_images is True."""
    try:
        import pypdfium2 as pdfium
    except ImportError as err:
        raise OcrUnavailable(f"pypdfium2 is missing; type: {INSTALL_HINT}") from err
    pdf = pdfium.PdfDocument(data)
    try:
        count = len(pdf)
        for index in range(first - 1, min(count, last or count)):
            page = pdf[index]
            result = Page(number=index + 1)
            try:
                images = _has_images(page)
                text_layer = page.get_textpage().get_text_bounded() if not images else ""
                if only_image_pages and not images:
                    result.reason = "no scanned picture on this page"
                    yield result
                    continue
                if not images and len(text_layer.split()) >= MIN_PAGE_WORDS:
                    result.text, result.confidence, result.method = text_layer.replace("\r\n", "\n"), 1.0, \
                        "text layer"
                    picture = _page_image(page, 100) if keep_images else None
                else:
                    picture = _page_image(page, dpi)
                    import numpy
                    out = engine()(numpy.array(picture.convert("RGB")))
                    raw = list(zip(out.txts or (), out.scores or (), out.boxes if out.boxes is not None else ()))
                    lines = [(t, float(s), [tuple(map(float, p)) for p in b]) for t, s, b in raw
                             if float(s) >= MIN_LINE_CONFIDENCE and t.strip()]
                    result.lines = lines
                    chars = sum(len(t) for t, _, _ in lines)
                    result.confidence = sum(s * len(t) for t, s, _ in lines) / chars if chars else 0.0
                    result.text = lines_to_text(lines)
                result.size = picture.size if picture is not None else (0, 0)
                if picture is not None and keep_images:
                    buf = io.BytesIO()
                    picture.save(buf, "PNG", optimize=True)
                    result.png = buf.getvalue()
                words = len(result.text.split())
                if words < MIN_PAGE_WORDS:
                    result.reason = f"almost no text ({words} words)"
                elif result.confidence < min_confidence:
                    result.reason = f"confidence {result.confidence:.2f} is under {min_confidence:.2f}"
                else:
                    result.kept = True
                result.text = "\n".join(fix_header_line(x) for x in result.text.split("\n"))
            finally:
                page.close()
            yield result
    finally:
        pdf.close()


def page_count(data):
    """How many pages the PDF in data has."""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(data)
    try:
        return len(pdf)
    finally:
        pdf.close()


def mask_page_image(page, mask):
    """The page's PNG with a black box over every OCR line whose text mask (the privacy rule) would change: identity,
    card and bank numbers and passwords. The picture is drawn at RENDER_DPI, the same scale as the line boxes."""
    hits = [box for text, _, box in page.lines if mask(text) != text]
    if not hits or not page.png:
        return page.png
    from PIL import Image, ImageDraw
    picture = Image.open(io.BytesIO(page.png)).convert("L")
    draw = ImageDraw.Draw(picture)
    for box in hits:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        draw.rectangle([min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2], fill=0)
    buf = io.BytesIO()
    picture.save(buf, "PNG", optimize=True)
    return buf.getvalue()
