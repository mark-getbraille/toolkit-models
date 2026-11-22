"""MATHS AND SCIENCE NOTATION for the Picture Model Training Kit (the owner's request of 2026-11-22: pictures for the
picture describer; the owner is a braille transcriber, so formulas are given EXACTLY as LaTeX, for Nemeth Code or UEB
technical braille downstream, with a spoken reading). This file lists:
  - the ready-made packs built in packs/math_notation_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): synthetic_formulas (formulas typeset with matplotlib's mathtext, with their LaTeX and a spoken
    reading such as "x squared plus 2 x plus 1") and chem_structures (chemical structures drawn with RDKit from
    Wikidata's SMILES, with the name, molecular formula, atom and ring counts and SMILES);
  - im2latex_formulas (group "research", personal use): im2latex-100k (Genthial and Sauvestre's prebuilt set on
    Zenodo, record 56198, from Deng and others' "Image-to-Markup Generation", arXiv:1609.04938): about 100,000
    printed formulas with their LaTeX. Zenodo lists the record as CC0, but its formulas were taken from arXiv papers
    whose authors keep their own licences, so the kit treats it as personal use. Its formula pictures are read
    straight from the 290 MB archive until enough are taken (prepare_im2latex); the answer is the LaTeX exactly as
    the set gives it (tokens separated by spaces);
  - the sources looked at and left out, with the reason (MATH_NOT_INCLUDED), handwritten maths (CROHME) among them.

Topic: documents (Documents, maps and signs). Picture-making (MATH_PICTURE_MAKING_OK): the two packs (formulas and
structures, no people); im2latex_formulas is personal use, never for picture-making.

    python -c "import sources, math_notation_sources"      (from the kit folder: checks the file loads)
"""

import os

from extra_sources import get_bytes, save, say, stream_tar, zenodo
from sources import Source, prepare_pack

LATEX_Q = "What is the LaTeX for this?"
IM2LATEX_RECORD = "56198"
IM2LATEX_TERMS = "https://zenodo.org/records/56198"
IM2LATEX_CREDIT = ("im2latex-100k (Anssi Kanervisto, Zenodo record 56198, https://zenodo.org/records/56198, from Yuntian "
                   "Deng and others, Image-to-Markup Generation, arXiv:1609.04938); formulas from arXiv papers")


def im2latex_formulas(text):
    """The formula list (one formula a line, the line number its index) as a list of strings."""
    return [line.strip() for line in text.split("\n")]


def im2latex_lists(lists, formulas):
    """{picture name: (split, LaTeX)} from the set's train/validate/test lists ("<index> <name> <render>" lines);
    test-list pictures are the kit's test pictures, the others training ones."""
    out = {}
    for split, text in lists:
        for line in text.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit() and int(parts[0]) < len(formulas):
                formula = formulas[int(parts[0])]
                if formula:
                    out[parts[1]] = (split, formula)
    return out


def on_white(data):
    """A formula picture (black ink on a see-through background) as JPEG-ready RGB bytes on white."""
    import io

    from PIL import Image
    picture = Image.open(io.BytesIO(data)).convert("RGBA")
    white = Image.new("RGBA", picture.size, (255, 255, 255, 255))
    out = io.BytesIO()
    Image.alpha_composite(white, picture).convert("RGB").save(out, "PNG")
    return out.getvalue()


def prepare_im2latex(source, data_dir, work, cap):
    """im2latex-100k: the formula list and the split lists are read, then the picture archive is read from the web
    only until cap training and source.test test pictures are taken. Each row asks for the LaTeX."""
    formulas = im2latex_formulas(get_bytes(zenodo(IM2LATEX_RECORD, "im2latex_formulas.lst")).decode("latin-1"))
    lists = [(split, get_bytes(zenodo(IM2LATEX_RECORD, name)).decode("latin-1"))
             for split, name in (("train", "im2latex_train.lst"), ("train", "im2latex_validate.lst"),
                                 ("test", "im2latex_test.lst"))]
    wanted = im2latex_lists(lists, formulas)
    say(f"  im2latex-100k: {len(wanted)} formulas with pictures.")
    folder = os.path.join(data_dir, source.key)
    rows, counts = [], {"train": 0, "test": 0}
    room = {"train": cap, "test": source.test}

    def take(member, tar):
        """Keep a listed formula picture while its split has room; True when both are full."""
        name = os.path.basename(member.name)
        stem = name[:-4] if name.endswith(".png") else name
        found = wanted.get(stem) or wanted.get(name)
        if found and counts[found[0]] < room[found[0]]:
            path = save(f"im2latex-{stem}", on_white(tar.extractfile(member).read()), folder)
            if path:
                counts[found[0]] += 1
                rows.append({"picture": path, "question": LATEX_Q, "answer": found[1], "latex": found[1],
                             "split": found[0], "credit": IM2LATEX_CREDIT})
        return counts["train"] >= room["train"] and counts["test"] >= room["test"]

    stream_tar(zenodo(IM2LATEX_RECORD, "formula_images.tar.gz"), take, "the im2latex-100k formula pictures (290 MB)")
    return rows


MATH_SOURCES = [
    Source("synthetic_formulas", "Printed maths, physics and chemistry formulas with their exact LaTeX and a spoken "
                                 "reading (computer-made, synthetic, ready-made pack)",
           "CC0 (typeset by packs/math_notation_packs.py from a fixed seed)",
           "Computer-made by the kit's makers (packs/math_notation_packs.py, matplotlib mathtext)", "permissive",
           3000, 30, prepare_pack, "about 250 MB"),
    Source("chem_structures", "Chemical structure drawings with the compound's name, molecular formula, atom and ring "
                              "counts and SMILES (drawn with RDKit from Wikidata, ready-made pack)",
           "CC0 (drawn by packs/math_notation_packs.py; Wikidata data CC0)",
           "Computer-made by the kit's makers with RDKit (BSD) from Wikidata (CC0), https://www.wikidata.org",
           "permissive", 800, 15, prepare_pack, "about 60 MB"),
    Source("im2latex_formulas", "im2latex-100k: printed formulas from scientific papers with their LaTeX (personal use)",
           "Listed CC0 on Zenodo; the formulas come from arXiv papers under their authors' own licences, so personal, "
           "non-commercial use only", IM2LATEX_CREDIT, "research", 6000, 40, prepare_im2latex,
           "up to 290 MB, read once", terms=IM2LATEX_TERMS,
           terms_summary="Zenodo lists CC0; formulas taken from arXiv papers. Personal, non-commercial use only."),
]

MATH_PICTURE_MAKING_OK = {"synthetic_formulas", "chem_structures"}

MATH_NOT_INCLUDED = {
    "CROHME handwritten maths (ICDAR competitions, TC-11)": "CC BY-NC-SA 3.0 (personal use) and given as ink "
        "strokes (InkML), not pictures; the owner can fetch it from https://tc11.cvc.uab.es/datasets/ and use it "
        "through Your own pictures once drawn. Not downloaded by the kit.",
    "HME100K (TAL Education)": "released for research only through a request form with no stated licence for the "
                               "pictures; not used.",
    "PubChem structure drawings and data": "PubChem's robots.txt (checked 2026-11-22) disallows /rest/pug/ for every "
        "program; the structures are drawn with RDKit from Wikidata's SMILES instead.",
    "Formulas typeset by a LaTeX program": "matplotlib's own mathtext typesets them, so no TeX installation is needed "
                                          "on the build machines; the LaTeX given is the same either way.",
    "Mathpix, Im2Latex-230k and other commercial or unlicensed formula sets": "no open licence for the pictures.",
}
