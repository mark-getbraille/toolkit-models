"""Creative writing readers for the Writing Kit (added at the owner's request), each labelled by style:
fiction_prose, children_story, poetry, screenplay_drama and humour.

  read_gutenberg_creative  public-domain novels, short stories, children's books, poetry, plays and humour from
                           Project Gutenberg's official mirror, found in Gutenberg's own catalogue by subject
  read_doctorow            Cory Doctorow's novels that he releases under Creative Commons (non-commercial, so personal
                           use only), from his own site's download pages

Pairs are made by simple rules: "Continue this story/scene in the same style" (the passage before is given and the
next passage is the answer), "Write a poem in the style of ...", and "Write the opening of a short story ...".
Fan fiction sites (Archive of Our Own, FanFiction.Net, Wattpad) and Reddit's WritingPrompts are excluded: see
sources-not-used.txt.
"""

import csv
import io
import re

import readers_more

CREATIVE_SUBJECTS = [
    # (style, subject words in Gutenberg's catalogue, how many books)
    ("fiction_prose", r"short stories", 4),
    ("fiction_prose", r"fiction", 4),
    ("children_story", r"juvenile fiction|fairy tales|children's stories", 4),
    ("poetry", r"poetry|poems", 5),
    ("screenplay_drama", r"drama|comedies|tragedies|plays", 4),
    ("humour", r"humor|wit and humor|humorous stories", 4),
]
DOCTOROW_BOOKS = ["littlebrother", "homeland", "makers", "down", "est", "overclocked", "context", "content"]
WHAT = {"fiction_prose": "story", "children_story": "children's story", "screenplay_drama": "scene from the play",
        "humour": "humorous piece"}


def paragraphs(text):
    """The paragraphs of a plain-text book (lines joined, blank lines between paragraphs)."""
    out = []
    for block in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s*\n\s*", " ", block).strip()
        if para:
            out.append(para)
    return out


def continuation_pairs(text, title, author, style, max_pairs=12, chunk=300, context=150):
    """[(instruction, answer)]: passages of about chunk words, each with the about context words before it."""
    paras = [p for p in paragraphs(text) if not re.fullmatch(r"[\W\dIVXLC]*(CHAPTER|Chapter|ACT|Act|SCENE|Scene)?"
                                                          r"[\W\dIVXLC.]*", p)]
    pieces, current = [], []
    for p in paras:
        current.append(p)
        if sum(len(x.split()) for x in current) >= chunk:
            pieces.append("\n\n".join(current))
            current = []
    if len(pieces) < 3:
        return []
    pieces = pieces[1:-1]                                     # skip front matter and the very end
    step = max(1, len(pieces) // (max_pairs + 1))
    out = []
    what = WHAT.get(style, "story")
    by = f" by {author}" if author else ""
    for i in range(1, len(pieces), step):
        before = " ".join(pieces[i - 1].split()[-context:])
        if style == "screenplay_drama":
            instruction = f'Continue this {what} "{title}"{by}, in the same style and layout:\n\n{before}'
        else:
            instruction = f'Continue this {what} in the same style ("{title}"{by}):\n\n{before}'
        out.append((instruction, pieces[i]))
        if len(out) >= max_pairs:
            break
    return out


def poems(text, max_poems=15):
    """[(title, poem)]: blocks of 4 to 60 lines separated by two or more blank lines, with a short title line."""
    out = []
    for block in re.split(r"\n\s*\n\s*\n+", text):
        lines = [ln.rstrip() for ln in block.strip("\n").split("\n")]
        if not 4 <= len(lines) <= 60:
            continue
        title = ""
        if len(lines[0].split()) <= 8 and (lines[0].isupper() or not lines[0].rstrip().endswith((",", ";"))):
            title, lines = lines[0].strip(), lines[1:]
        body = "\n".join(lines).strip()
        if re.match(r"(?i)(contents|index|preface|introduction|notes?|illustrations)\b", title) or \
                sum(1 for ln in lines if re.match(r"\s*([IVXLC]+\.|\d+\.?)\s", ln)) > len(lines) / 3:
            continue
        avg = sum(len(ln) for ln in lines) / max(1, len(lines))
        if avg < 70 and len(body.split()) >= 20:                   # short lines: verse, not prose
            out.append((title, body))
        if len(out) >= max_poems:
            break
    return out


def read_gutenberg_creative(fetcher, say=print, **_):
    say("  Gutenberg creative writing: reading the catalogue from the official mirror.")
    catalogue = fetcher.get(readers_more.GUTENBERG_MIRROR + "cache/epub/feeds/pg_catalog.csv").decode("utf-8",
                                                                                                    "replace")
    rows = [r for r in csv.DictReader(io.StringIO(catalogue)) if r.get("Language") == "en" and r.get("Type") == "Text"]
    used = set()
    for style, subjects, count in CREATIVE_SUBJECTS:
        books = [r for r in rows if re.search(subjects, (r.get("Subjects") or "").lower()) and r["Text#"] not in used
                 and "letters" not in (r.get("Title") or "").lower()][:count]
        for row in books:
            used.add(row["Text#"])
            number, title = row["Text#"], re.sub(r"\s+", " ", row.get("Title", "")).strip()
            author = re.sub(r",\s*\d.*$", "", (row.get("Authors") or "").split(";")[0]).strip()
            if "," in author:
                last, first = author.split(",", 1)
                author = f"{first.strip()} {last.strip()}"
            try:
                text = fetcher.get(f"{readers_more.GUTENBERG_MIRROR}cache/epub/{number}/pg{number}.txt") \
                    .decode("utf-8", "replace")
            except Exception as err:
                if "robots" in str(err):
                    raise
                continue
            if re.search(r"(?i)copyrighted project gutenberg|copyright \(c\)|\u00a9", text[:6000]):
                continue                                 # a modern book shared with permission, not public domain
            body = readers_more.gutenberg_body(text)
            if style == "poetry":
                for poem_title, poem in poems(body):
                    about = f' titled "{poem_title.title()}"' if poem_title else ""
                    yield {"type": "text", "group": f"gutenberg-{number}", "kind": "poem", "form": "poem",
                           "tone": "literary", "audience": "readers", "style_label": "poetry",
                           "instruction": f"Write a poem{about} in the style of {author or 'a classic poet'}.",
                           "response": poem}
            else:
                for instruction, answer in continuation_pairs(body, title, author, style):
                    yield {"type": "text", "group": f"gutenberg-{number}", "kind": style, "form": WHAT.get(style),
                           "tone": "literary", "audience": "readers", "style_label": style,
                           "instruction": instruction, "response": answer}


def read_doctorow(fetcher, say=print, books=None, **_):
    """Text records from Cory Doctorow's Creative Commons novels (the plain-text editions on craphound.com)."""
    for slug in books or DOCTOROW_BOOKS:
        page = fetcher.get(f"https://craphound.com/{slug}/download/").decode("utf-8", "replace")
        links = re.findall(r'href="((?:https?://craphound\.com)?[^"]*\.txt)"', page)
        if not links:
            continue
        link = links[0] if links[0].startswith("http") else f"https://craphound.com/{slug}/" + links[0].lstrip("./")
        text = fetcher.get(link.replace("http://", "https://")).decode("utf-8", "replace")
        if not re.search(r"(?i)creative commons|creativecommons\.org", text[:20000]):
            say(f"  Doctorow: {slug} does not state a Creative Commons licence in the file; skipped.")
            continue
        title = slug.replace("littlebrother", "Little Brother").title() if slug != "littlebrother" else "Little Brother"
        for instruction, answer in continuation_pairs(text, title, "Cory Doctorow", "fiction_prose", max_pairs=20):
            yield {"type": "text", "group": slug, "kind": "novel", "form": "story", "tone": "modern and casual",
                   "audience": "readers", "style_label": "fiction_prose", "instruction": instruction,
                   "response": answer}
