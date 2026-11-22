"""READING PICTURES for the Picture Model Training Kit: handwriting, charts and diagrams, date codes on packaging,
sign language and weather maps. The open collections are ready-made packs (packs/handwriting_packs.py,
chart_packs.py, date_code_packs.py, sign_language_packs.py, weather_map_packs.py, listed in sources.py); this file
holds the collections that cannot be packs because of their licence, and every source that was looked at and left
out, with the reason (the owner's request of 2026-11-21).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: a collection is downloaded by the kit on the
user's own computer, straight from its maker, only when the user ticks its personal-use box. Every licence was
checked at its source in November 2026.

The collections (PICTURE_READING_SOURCES):
  noncommercial
    tqa_diagrams  TQA, Textbook Question Answering (Kembhavi et al., 2017, Allen Institute for AI; CC BY-NC 3.0, from
                  CK-12's open science books): the instructional diagrams with the paragraph that explains each
                  ("Explain this diagram.") and the lesson figures with their captions ("What does this figure
                  show?"). The 1.76 GB zip is downloaded once.

Left out, each with its reason: HANDWRITING_NOT_INCLUDED, CHART_NOT_INCLUDED, DATE_NOT_INCLUDED,
SIGN_NOT_INCLUDED and WEATHER_NOT_INCLUDED (all together in PICTURE_READING_NOT_INCLUDED).

    python kit/picture_reading_sources.py tqa_diagrams --cap 8      (from the kit folder: a quick check)
"""

import json
import os
import random
import zipfile

from sources import Source, clean, save_picture, say
from more_sources import download_to

TQA_URL = "https://ai2-public-datasets.s3.amazonaws.com/tqa/tqa_train_val_test.zip"
TQA_PAGE = "https://allenai.org/data/tqa"
EXPLAIN = "Explain this diagram."
FIGURE_SHOWS = "What does this figure show?"


def sentence(text):
    """Text as a sentence: a capital letter first and a full stop at the end."""
    text = clean(text)
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".!?" else text + "."


def tqa_rows(lessons, part):
    """[(path in the zip, row)] for one part of TQA: each instructional diagram with its explanation (at least 12
    words), and each lesson figure with its caption (at least 6 words)."""
    out = []
    for lesson in lessons:
        for diagram in (lesson.get("instructionalDiagrams") or {}).values():
            text = clean(diagram.get("processedText"))
            if len(text.split()) >= 12 and diagram.get("imagePath"):
                out.append((f"tqa_train_val_test/{part}/{diagram['imagePath']}",
                            {"question": EXPLAIN, "answer": sentence(text), "split": ""}))
        for topic in (lesson.get("topics") or {}).values():
            for figure in ((topic.get("content") or {}).get("figures") or []):
                caption = clean(figure.get("caption"))
                if len(caption.split()) >= 6 and figure.get("imagePath"):
                    out.append((f"tqa_train_val_test/{part}/{figure['imagePath']}",
                                {"question": FIGURE_SHOWS, "answer": sentence(caption), "split": ""}))
    return out


def prepare_tqa_diagrams(source, data_dir, work, cap):
    """TQA's diagrams and figures (see the module docstring), in a fixed random order, at most cap of them."""
    archive = download_to(work, TQA_URL, "tqa_train_val_test.zip")
    folder = os.path.join(data_dir, source.key)
    rows = []
    with zipfile.ZipFile(archive) as z:
        chosen = []
        for part, name in (("train", "tqa_v1_train.json"), ("val", "tqa_v1_val.json"), ("test", "tqa_v2_test.json")):
            path = f"tqa_train_val_test/{part}/{name}"
            if path in z.namelist():
                chosen += tqa_rows(json.loads(z.read(path)), part)
        random.Random(317).shuffle(chosen)
        seen = set()
        for member, row in chosen:
            if len(rows) >= cap + source.test:
                break
            if (member, row["question"]) in seen:
                continue
            seen.add((member, row["question"]))
            try:
                data = z.read(member)
            except KeyError:
                continue
            picture = save_picture("tqa-" + member.split("/", 2)[-1].replace("/", "-").rsplit(".", 1)[0], data, folder)
            if picture:
                rows.append(dict(row, picture=picture))
    say(f"  TQA: {len(rows)} diagrams and figures.")
    return rows


PICTURE_READING_SOURCES = [
    Source("tqa_diagrams", "TQA: school science diagrams explained, and textbook figures with their captions "
                           "(non-commercial; personal use)",
           "CC BY-NC 3.0 (README.md in the TQA zip; text from CK-12's open science books)",
           "TQA, Textbook Question Answering (Kembhavi et al., 2017), Allen Institute for AI, CC BY-NC 3.0, "
           f"{TQA_PAGE}; lessons from CK-12 (www.ck12.org)", "noncommercial", 2000, 20, prepare_tqa_diagrams,
           "1.76 GB, once", terms="https://creativecommons.org/licenses/by-nc/3.0/",
           terms_summary="Non-commercial use with credit (CC BY-NC 3.0)."),
]

# The collections a picture-making model may learn from: the diagrams (drawings, no people).
PICTURE_READING_PICTURE_MAKING_OK = {"tqa_diagrams"}

HANDWRITING_NOT_INCLUDED = {
    "GNHK, GoodNotes Handwriting Kollection (CC BY 4.0)":
        "its download page (goodnotes.com/gnhk) now sends visitors to GoodNotes' home page, and the GitHub "
        "repository (GoodNotes/GNHK-dataset) holds only the README, which links to that page (checked 2026-11-21). "
        "Copies on Hugging Face are other people's uploads, not the makers' own download, so they are not used. "
        "Worth adding as soon as GoodNotes puts the files back.",
    "IAM Handwriting Database (University of Bern)":
        "needs a sign-up on fki.tic.heia-fr.ch and is for non-commercial research only; a personal-use, sign-up "
        "entry (the owner downloads it with his own account and puts the files in the sign-up folder) could be "
        "added to signup_sources.py.",
    "RIMES (French handwritten letters and forms)":
        "the makers (A2iA and Teklia) give it only after a request form and an agreement, research only; it could "
        "be a sign-up entry. French, so an answer would be a French transcription.",
    "CVL Database (TU Wien, Zenodo 1492267, CC BY-NC 4.0)":
        "its cropped pages carry no transcription in the files (the writers copied seven known texts; the word "
        "boxes are in UTF-16 XML of the 4.2 GB full set), so an answer could not be taken from the dataset "
        "without matching each page to its text by hand. Left for a later pass (non-commercial).",
    "HKR, Handwritten Kazakh and Russian (Nurseitov et al.)":
        "Cyrillic forms in Kazakh and Russian; no licence is written in its GitHub repository, and its files are on "
        "Google Drive, whose download server (drive.usercontent.google.com) disallows every robot in robots.txt.",
    "ImageCLEF 2016 Bentham Handwritten Retrieval (Zenodo 52994, CC BY-NC-SA 4.0)":
        "7.9 GB of the same Bentham Papers; the CC BY 4.0 ICDAR 2015 set (bentham_pages) is used instead.",
    "Library of Congress By the People":
        "already in the kit as loc_letters (text_packs.py: CC0 transcriptions of handwritten letters and diaries).",
}

CHART_NOT_INCLUDED = {
    "AI2 Diagrams (AI2D)": "already in the kit as ai2d (personal_sources.py, research terms from license.txt in the "
                           "zip).",
    "ChartQA": "already in the kit as chartqa (personal_sources.py, GPL-3.0, treated as personal use).",
    "SciCap (Penn State with Adobe, CC BY-NC-SA 4.0)":
        "figures from arXiv papers with their authors' captions; looked at again: the makers' own copy "
        "(CrowdAILab/scicap on Hugging Face, not gated) keeps its pictures in one zip split into eleven 2 GB parts "
        "(23 GB in all), so no picture can be taken out without downloading the whole set. bigtech_sources.py also "
        "notes that PlotQA, ChartQA, AI2D, TQA and the case-report figures already cover scientific figures. Could "
        "be a non-commercial entry for a computer with room for it.",
    "OpenStax books as they are now (CC BY-NC-SA 4.0 since March to April 2026)":
        "OpenStax changed the licence of its books to CC BY-NC-SA in 2026, and openstax.org's robots.txt "
        "disallows /apps/archive, /contents and /resources and keeps GPTBot out of /books/. The openstax_figures "
        "pack therefore reads the books' own GitHub repositories (github.com/openstax) at the last version before "
        "each book's licence change, which OpenStax published under CC BY 4.0 (a CC licence cannot be taken back "
        "for a version already published).",
    "OpenStax American Government, Psychology, Microbiology, US History and the other books":
        "not in openstax_figures: Psychology and Microbiology hold medical and people photos, and the history and "
        "government books mostly photographs of people; the economics, statistics, biology, chemistry, physics and "
        "astronomy books are used.",
    "Our World in Data": "already in the kit as owid_charts (ngo_packs.py).",
    "PlotQA": "already in the kit as plotqa (text_packs.py).",
}

DATE_NOT_INCLUDED = {
    "ExpDate (Seker and Ahn, 2022, CC BY 4.0)":
        "real and synthetic product photos with every date read and marked (felizang.github.io/expdate), CC BY 4.0, "
        "but its only download is a Google Drive folder: drive.google.com's robots.txt allows the folder page, "
        "and the file server (drive.usercontent.google.com) disallows every robot, so a program may not fetch the "
        "zips. The owner can download Products-Real.zip by hand and use the own-pictures folder; worth a sign-up "
        "style local-files entry later.",
    "Open Food Facts (photos and the expiration_date field)":
        "the kit reads Open Food Facts only through its bulk-reuse routes (off_dump.py). A product's "
        "expiration_date was typed for one pack, but no photo is marked as the one that shows the date, so an "
        "answer could not say the date of the pack in a given photo; the only per-photo text is machine OCR, "
        "never used as an answer. Not built.",
    "Food Packaging OCR (Mendeley Data 3cpx2fmn3r, CC BY 4.0)":
        "already in the kit as food_packaging (big_sources.py: 'What is the use-by date on this package?').",
    "Commons 'Expiration dates'":
        "also asked by food_packs.py's Commons food pack ('It shows an expiry date'); commons_date_codes adds the "
        "date itself where the file's own words state it.",
}

SIGN_NOT_INCLUDED = {
    "ASL Citizen (Microsoft Research and Boston University)":
        "Microsoft Research License Terms: non-commercial research only, and the signers' videos are personal data "
        "that must be kept confidential and destroyed after the research; 42.8 GB of videos. Not built.",
    "WLASL and MS-ASL":
        "only lists of YouTube links (C-UDA and research terms); the videos would have to be taken from YouTube "
        "(as extra_sources.py already notes).",
    "ASL alphabet sets on Kaggle (for example 'ASL Alphabet' by grassknoted)":
        "Kaggle needs the owner's own account and key, and the sets' licences vary (several say GPL-2 or give "
        "none); a sign-up entry could be added to signup_sources.py.",
    "How2Sign": "already in the kit as how2sign (extra_sources.py, CC BY-NC 4.0, personal use).",
    "HaGRID hand gestures": "already in the kit as hagrid (share-alike).",
    "Commons gestures (thumbs up, OK, V sign, waving)":
        "already in commons_expressions (expression_packs.py), which leaves sign alphabets out; "
        "commons_sign_language takes the sign alphabets and sign language.",
}

WEATHER_NOT_INCLUDED = {
    "Storm Prediction Center (spc.noaa.gov) outlooks, watches and mesoscale discussions":
        "public domain, but spc.noaa.gov's robots.txt says 'User-agent: * Disallow: /' (checked 2026-11-21).",
    "NWS radar (radar.weather.gov) and NEXRAD Level II/III on AWS Open Data":
        "radar.weather.gov gives only the current loop, no archive; the AWS buckets hold raw radar volumes, not "
        "pictures, and drawing them would make a picture the program invented. WPC's archived analysis and radar "
        "composite (radsfcus_exp) is used instead.",
    "Iowa Environmental Mesonet radar composites":
        "made by Iowa State University, not NOAA, and its robots.txt disallows /archive/nexrad/; not used.",
    "Commons weather radar images":
        "a small category; the NOAA and NWS products are taken from their own archives instead.",
}

PICTURE_READING_NOT_INCLUDED = {**HANDWRITING_NOT_INCLUDED, **CHART_NOT_INCLUDED, **DATE_NOT_INCLUDED,
                                **SIGN_NOT_INCLUDED, **WEATHER_NOT_INCLUDED}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try a picture-reading collection.")
    parser.add_argument("key", choices=[s.key for s in PICTURE_READING_SOURCES])
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PICTURE_READING_SOURCES if s.key == args.key)
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="reading-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
