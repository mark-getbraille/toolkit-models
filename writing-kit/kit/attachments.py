"""Attachments for the Writing Kit: saving the files that come with a message beside it, and reading the text of the
ones that are written documents (memos, letters, notes) so they can be used as more training text.

  save_message(folder, message_text, files)  writes message.txt and each attachment into one folder per message
  extract_text(name, data)                   the plain text of an attachment, or "" when it is not a text document

Text is read from: plain text (.txt, .text, .asc, text/plain), web pages (.htm, .html), Word documents in the newer
format (.docx, read with Python's own zip and XML reading), RTF (.rtf, the control words removed), and PDF (.pdf,
with the free pdftotext program when it is on the computer; Windows users can get it with Xpdf or Poppler; without
it the PDF is still saved, only not read). Old-format Word files (.doc) are saved but not read: reading them needs a
separate program. Pictures, spreadsheets, programs and archives are saved only.
"""

import html
import io
import os
import re
import shutil
import subprocess
import tempfile
import zipfile

TEXT_TYPES = (".txt", ".text", ".asc", ".me", ".msg")


def safe_name(name, default="attachment"):
    """A file name that is safe to write on Windows and Linux (no folders, no odd characters)."""
    name = os.path.basename((name or "").replace("\\", "/")).strip()
    name = re.sub(r"[^\w.\- ()]+", "_", name)[:120].strip(" .")
    return name or default


def save_message(folder, message_text, files):
    """Write message_text to folder/message.txt and each (name, bytes) of files beside it. Returns the saved names."""
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "message.txt"), "w", encoding="utf-8") as f:
        f.write(message_text)
    saved = []
    for name, data in files:
        name = safe_name(name)
        base, ext = os.path.splitext(name)
        n = 1
        while name in saved or name == "message.txt":
            n += 1
            name = f"{base} ({n}){ext}"
        with open(os.path.join(folder, name), "wb") as f:
            f.write(data)
        saved.append(name)
    return saved


def _docx_text(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", "\t", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def _rtf_text(data):
    text = data.decode("latin-1", "replace")
    text = re.sub(r"\\par[d]?", "\n", text)
    text = re.sub(r"\{\\\*[^{}]*\}", "", text)
    text = re.sub(r"\\'[0-9a-f]{2}", "", text)
    text = re.sub(r"\\[a-z]+-?\d* ?", "", text)
    return text.replace("{", "").replace("}", "")


def _pdf_text(data):
    tool = shutil.which("pdftotext")
    if not tool:
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "in.pdf")
        with open(src, "wb") as f:
            f.write(data)
        try:
            out = subprocess.run([tool, "-q", "-enc", "UTF-8", src, "-"], capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return out.stdout.decode("utf-8", "replace")


def extract_text(name, data, content_type=""):
    """The plain text of an attachment (see the module notes), tidied; "" when it is not a text document or cannot
    be read."""
    ext = os.path.splitext((name or "").lower())[1]
    ctype = (content_type or "").lower()
    try:
        if ext in TEXT_TYPES or ctype == "text/plain":
            text = data.decode("utf-8") if _is_utf8(data) else data.decode("latin-1")
        elif ext in (".htm", ".html") or ctype == "text/html":
            raw = data.decode("utf-8", "replace")
            raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
            text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?i)<br\s*/?>|</p>", "\n", raw)))
        elif ext == ".docx":
            text = _docx_text(data)
        elif ext == ".rtf" or ctype in ("application/rtf", "text/rtf"):
            text = _rtf_text(data)
        elif ext == ".pdf" or ctype == "application/pdf":
            text = _pdf_text(data)
        else:
            return ""
    except (ValueError, KeyError, zipfile.BadZipFile, UnicodeDecodeError):
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def _is_utf8(data):
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False
