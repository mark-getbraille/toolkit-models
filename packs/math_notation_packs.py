"""Picture packs of MATHS AND SCIENCE NOTATION (the owner's request of 2026-11-22: pictures for the picture describer).
Used by build_packs.py in the same way as its own PACKS: build_<key>(limit) returns [(file name, JPEG bytes or None,
row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the
same picture (food_packs.with_twins). The limit counts pictures.

Why: the owner is a blind braille transcriber. A formula in a picture (a photo of a worksheet, a scanned textbook
page, a screenshot) is unreadable to a screen reader. The describer must give the formula EXACTLY as LaTeX, so that
it can be turned into Nemeth Code or UEB technical braille downstream, and say it aloud in plain spoken maths
("x squared plus 2 x plus 1"). Every row of these packs also carries the LaTeX in its own "latex" field (and, for
structures, "smiles"), untouched, for that conversion.

The packs (MATH_PACKS):
  synthetic_formulas  Formulas typeset here with matplotlib's mathtext (matplotlib's own renderer: no LaTeX program
                      is needed) from a fixed seed (SEED), in five type styles (Computer Modern, STIX, STIX sans,
                      DejaVu sans and serif), on plain paper, lined notebook paper, graph paper, a whiteboard or a
                      textbook page, about a third "photographed" by phone_photo.py. The formulas are
                      (1) NAMED_FORMULAS: well-known formulas of school and college maths, physics and chemistry
                      (quadratic formula, Pythagoras, areas and volumes, E = mc^2, Ohm's law, the ideal gas law, Euler's
                      identity, derivatives and integrals ...), written out here; mathematical formulas are facts,
                      not anyone's expression, and none is copied from a book; and (2) formulas made up from a small
                      grammar (polynomials, equations, fractions, roots, powers, trigonometry, logarithms, sums,
                      integrals, derivatives, limits, inequalities, chemical equations). Each formula is built as a
                      tree, so its LaTeX and its spoken reading come from the same tree and always agree.
                      Answers: "What does this formula say?" (the spoken reading, then the LaTeX), "What is the LaTeX
                      for this?" (the LaTeX alone, exactly as typeset) and, for a named formula, "What formula is
                      this?".
  chem_structures     Chemical structure drawings (skeletal formulas) drawn here with RDKit (BSD licence) from each
                      compound's SMILES as recorded in Wikidata (CC0), for the common compounds of CHEMICALS (drugs,
                      vitamins, sugars, amino acids, hormones, solvents, household and food chemicals). The molecular
                      formula, the counts of atoms and rings, and the canonical SMILES are worked out by RDKit from
                      the SMILES, so nothing is guessed. Answers: "What chemical is this?" (its Wikidata name and
                      item), "What is its molecular formula?", "Describe this structure." (counts only: atoms by
                      element, rings, aromatic rings) and "What is the SMILES for this?". PubChem's own drawings are
                      not used: PubChem's robots.txt disallows /rest/pug/ (checked 2026-11-22).
Notes: both packs are made by this repository from a fixed seed, so they are CC0; Wikidata's data is CC0. Never used
for picture-making? They may be: a model that draws formulas and structures harms nobody, and no person is shown
(the kit's MATH_PICTURE_MAKING_OK lists both).

Handwritten maths (CROHME: CC BY-NC-SA, personal use), im2latex-100k and the other formula sets are kit entries:
training-kit/kit/math_notation_sources.py.

Needs: matplotlib (synthetic_formulas) and rdkit (chem_structures): "python -m pip install matplotlib rdkit".

    python packs/math_notation_packs.py synthetic_formulas --limit 12 --save some-folder      (a quick check)
"""

import io
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import say, session
from phone_photo import font, phone_photo
from synthetic_documents import seeded

SEED = 3142
SAY_Q = "What does this formula say?"
LATEX_Q = "What is the LaTeX for this?"
NAME_Q = "What formula is this?"
CREDIT = ("A computer-made formula typeset with matplotlib's mathtext by packs/math_notation_packs.py (synthetic, "
          "from a fixed seed), CC0")

# ----------------------------------------------------------------- formula trees
#
# A formula is a small tree of tuples; latex() and spoken() walk the same tree:
#   ("n", "2")  a number      ("v", "x")  a letter (Greek by name: ("v", "theta"))
#   ("+", a, b) ("-", a, b)   ("*", a, b) written side by side (2x) or with a dot when both are numbers
#   ("x", a, b) times sign    ("/", a, b) a fraction       ("^", a, b) a power      ("_", a, b) a subscript
#   ("sqrt", a) ("root", n, a) ("()", a) brackets          ("f", "sin", a) a function
#   ("=", a, b) and the other relations "<", ">", "<=", ">=", "!=", "approx", "->"
#   ("neg", a) minus a        ("pm", a, b) a plus or minus b
#   ("sum", i, lo, hi, a)     ("int", lo, hi, a, var)      ("lim", var, to, a)       ("d", var, a) d/dvar of a
#   ("chem", "H_2O")          a chemical formula in upright letters

GREEK = {"alpha", "beta", "gamma", "delta", "theta", "lambda", "mu", "pi", "sigma", "omega", "phi", "rho", "Delta",
         "Sigma", "Omega", "epsilon", "tau"}
RELATIONS = {"=": ("=", "equals"), "<": ("<", "is less than"), ">": (">", "is greater than"),
             "<=": (r"\leq", "is less than or equal to"), ">=": (r"\geq", "is greater than or equal to"),
             "!=": (r"\neq", "is not equal to"), "approx": (r"\approx", "is approximately equal to"),
             "->": (r"\rightarrow", "gives")}
ORDINAL = {2: "squared", 3: "cubed"}
NUMBER_WORDS = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six",
                "7": "seven", "8": "eight", "9": "nine", "10": "ten"}
# Number fractions said the everyday way ("one half b h", not "1 over 2 b h", which could be heard as 1 over 2bh).
COMMON_FRACTIONS = {("1", "2"): "one half", ("1", "3"): "one third", ("2", "3"): "two thirds",
                    ("1", "4"): "one quarter", ("3", "4"): "three quarters", ("4", "3"): "four thirds"}
NTH = {"3": "cube", "4": "fourth", "5": "fifth", "6": "sixth", "n": "n-th"}


def simple(node):
    """True for a node said as one word or number (no "end" needed after it)."""
    return node[0] in ("n", "v") or (node[0] == "_" and simple(node[1]) and simple(node[2]))


def latex(node):
    """The LaTeX of a formula tree (as typeset, and as given in the answers)."""
    kind = node[0]
    if kind == "n":
        return node[1]
    if kind == "v":
        return "\\" + node[1] if node[1] in GREEK else node[1]
    if kind in ("+", "-"):
        return f"{latex(node[1])} {kind} {latex(node[2])}"
    if kind == "*":
        a, b = latex(node[1]), latex(node[2])
        return f"{a} \\cdot {b}" if node[2][0] == "n" or (node[1][0] == "n" and b[:1].isdigit()) else f"{a}{b}"
    if kind == "x":
        return f"{latex(node[1])} \\times {latex(node[2])}"
    if kind == "/":
        return f"\\frac{{{latex(node[1])}}}{{{latex(node[2])}}}"
    if kind == "^":
        return f"{latex(node[1])}^{{{latex(node[2])}}}"
    if kind == "_":
        return f"{latex(node[1])}_{{{latex(node[2])}}}"
    if kind == "sqrt":
        return f"\\sqrt{{{latex(node[1])}}}"
    if kind == "root":
        return f"\\sqrt[{latex(node[1])}]{{{latex(node[2])}}}"
    if kind == "()":
        return f"\\left({latex(node[1])}\\right)"
    if kind == "f":
        inner = node[2]
        arg = latex(inner) if simple(inner) or inner[0] == "()" else f"\\left({latex(inner)}\\right)"
        return f"\\{node[1]} {arg}" if simple(inner) else f"\\{node[1]}{arg}"
    if kind in RELATIONS:
        return f"{latex(node[1])} {RELATIONS[kind][0]} {latex(node[2])}"
    if kind == "neg":
        return f"-{latex(node[1])}"
    if kind == "pm":
        return f"{latex(node[1])} \\pm {latex(node[2])}"
    if kind == "sum":
        return f"\\sum_{{{latex(node[1])}={latex(node[2])}}}^{{{latex(node[3])}}} {latex(node[4])}"
    if kind == "int":
        bounds = f"_{{{latex(node[1])}}}^{{{latex(node[2])}}}" if node[1] else ""
        return f"\\int{bounds} {latex(node[3])} \\, d{latex(node[4])}"
    if kind == "lim":
        return f"\\lim_{{{latex(node[1])} \\to {latex(node[2])}}} {latex(node[3])}"
    if kind == "d":
        inner = latex(node[2]) if simple(node[2]) else f"\\left({latex(node[2])}\\right)"
        return f"\\frac{{d}}{{d{latex(node[1])}}} {inner}"
    if kind == "chem":
        return "\\mathrm{" + node[1] + "}"
    raise ValueError(kind)


def number_words(text):
    """A number as it is read: "2" stays "2" (a screen reader says it), "-3" is "minus 3", "infinity"."""
    if text == "\\infty":
        return "infinity"
    return text.replace("-", "minus ") if text.startswith("-") else text


def letter(name):
    """A letter as said: Greek by name, capitals as "capital A"."""
    if name in GREEK:
        return ("capital " + name.lower()) if name[0].isupper() else name
    return f"capital {name}" if len(name) == 1 and name.isupper() else name


def spoken(node):
    """The spoken reading of a formula tree, in the plain words a teacher would say aloud ("x squared plus 2 x plus
    1", "the fraction a over b", "the square root of 2")."""
    kind = node[0]
    if kind == "n":
        return number_words(node[1])
    if kind == "v":
        return letter(node[1])
    if kind == "+":
        return f"{spoken(node[1])} plus {spoken(node[2])}"
    if kind == "-":
        return f"{spoken(node[1])} minus {spoken(node[2])}"
    if kind == "*":
        joiner = " times " if node[2][0] == "n" else " "
        return f"{spoken(node[1])}{joiner}{spoken(node[2])}"
    if kind == "x":
        return f"{spoken(node[1])} times {spoken(node[2])}"
    if kind == "/":
        if (node[1][1], node[2][1]) in COMMON_FRACTIONS and node[1][0] == node[2][0] == "n":
            return COMMON_FRACTIONS[(node[1][1], node[2][1])]
        if simple(node[1]) and simple(node[2]):
            return f"{spoken(node[1])} over {spoken(node[2])}"
        return f"the fraction {spoken(node[1])} over {spoken(node[2])}, end fraction"
    if kind == "^":
        base = spoken(node[1]) if simple(node[1]) or node[1][0] == "f" else f"open bracket {spoken(node[1])} " \
                                                                             f"close bracket"
        exp = node[2]
        if exp[0] == "n" and exp[1].isdigit() and int(exp[1]) in ORDINAL:
            return f"{base} {ORDINAL[int(exp[1])]}"
        if simple(exp):
            return f"{base} to the power of {spoken(exp)}"
        return f"{base} to the power of {spoken(exp)}, end power"
    if kind == "_":
        return f"{spoken(node[1])} sub {spoken(node[2])}"
    if kind == "sqrt":
        return f"the square root of {spoken(node[1])}" + ("" if simple(node[1]) else ", end root")
    if kind == "root":
        nth = NTH.get(node[1][1], spoken(node[1]) + "-th")
        return f"the {nth} root of {spoken(node[2])}" + ("" if simple(node[2]) else ", end root")
    if kind == "()":
        return f"open bracket {spoken(node[1])} close bracket"
    if kind == "f":
        names = {"sin": "sine", "cos": "cosine", "tan": "tangent", "ln": "natural log", "log": "log",
                 "exp": "the exponential of"}
        inner = node[2]
        arg = spoken(inner) if simple(inner) or inner[0] == "()" else f"open bracket {spoken(inner)} close bracket"
        return f"{names.get(node[1], node[1])} {'of ' if node[1] in ('ln', 'log') else ''}{arg}"
    if kind in RELATIONS:
        return f"{spoken(node[1])} {RELATIONS[kind][1]} {spoken(node[2])}"
    if kind == "neg":
        return f"minus {spoken(node[1])}"
    if kind == "pm":
        return f"{spoken(node[1])} plus or minus {spoken(node[2])}"
    if kind == "sum":
        return (f"the sum from {spoken(node[1])} equals {spoken(node[2])} to {spoken(node[3])} of "
                f"{spoken(node[4])}")
    if kind == "int":
        bounds = f" from {spoken(node[1])} to {spoken(node[2])}" if node[1] else ""
        return f"the integral{bounds} of {spoken(node[3])} d {spoken(node[4])}"
    if kind == "lim":
        return f"the limit as {spoken(node[1])} approaches {spoken(node[2])} of {spoken(node[3])}"
    if kind == "d":
        inner = spoken(node[2]) if simple(node[2]) else f"open bracket {spoken(node[2])} close bracket"
        return f"the derivative with respect to {spoken(node[1])} of {inner}"
    if kind == "chem":
        return chem_spoken(node[1])
    raise ValueError(kind)


def chem_spoken(text):
    """ "2H_2 + O_2 \\rightarrow 2H_2O" read aloud: "2 H 2 plus O 2 gives 2 H 2 O" (each element said as its
    symbol's letters, subscripts as plain numbers)."""
    text = text.replace("\\rightarrow", " gives ").replace("+", " plus ").replace("_", " ")
    out = []
    for word in text.split():
        if word in ("gives", "plus"):
            out.append(word)
            continue
        parts = re.findall(r"\d+|[A-Z][a-z]?|\(|\)", word)
        out.append(" ".join({"(": "open bracket", ")": "close bracket"}.get(p, p) for p in parts))
    return " ".join(out)


# ----------------------------------------------------------------- well-known formulas

def N(x):
    """A number node."""
    return ("n", str(x))


def V(x):
    """A letter node."""
    return ("v", x)


def P(a, b):
    """a to the power b (b a number or a node)."""
    return ("^", a, N(b) if isinstance(b, int) else b)


x, y, a, b, c, r, h, m, t, n = (V(s) for s in "xyabcrhmtn")
NAMED_FORMULAS = [
    ("the quadratic formula", ("=", x, ("/", ("pm", ("neg", b), ("sqrt", ("-", P(b, 2), ("*", ("*", N(4), a), c)))),
                                        ("*", N(2), a)))),
    ("the Pythagorean theorem", ("=", ("+", P(a, 2), P(b, 2)), P(c, 2))),
    ("the area of a circle", ("=", V("A"), ("*", V("pi"), P(r, 2)))),
    ("the circumference of a circle", ("=", V("C"), ("*", ("*", N(2), V("pi")), r))),
    ("the volume of a sphere", ("=", V("V"), ("*", ("*", ("/", N(4), N(3)), V("pi")), P(r, 3)))),
    ("the volume of a cylinder", ("=", V("V"), ("*", ("*", V("pi"), P(r, 2)), h))),
    ("the area of a triangle", ("=", V("A"), ("*", ("/", N(1), N(2)), ("*", b, h)))),
    ("Einstein's mass-energy equation", ("=", V("E"), ("*", m, P(c, 2)))),
    ("Newton's second law", ("=", V("F"), ("*", m, a))),
    ("Ohm's law", ("=", V("V"), ("*", V("I"), V("R")))),
    ("the ideal gas law", ("=", ("*", V("P"), V("V")), ("*", ("*", n, V("R")), V("T")))),
    ("the formula for kinetic energy", ("=", ("_", V("E"), V("k")), ("*", ("/", N(1), N(2)), ("*", m, P(V("v"), 2))))),
    ("the formula for speed", ("=", V("v"), ("/", V("d"), t))),
    ("the slope-intercept form of a line", ("=", y, ("+", ("*", m, x), b))),
    ("the slope of a line through two points", ("=", m, ("/", ("-", ("_", y, N(2)), ("_", y, N(1))),
                                                           ("-", ("_", x, N(2)), ("_", x, N(1)))))),
    ("the distance formula", ("=", V("d"), ("sqrt", ("+", P(("()", ("-", ("_", x, N(2)), ("_", x, N(1)))), 2),
                                                     P(("()", ("-", ("_", y, N(2)), ("_", y, N(1)))), 2))))),
    ("the difference of two squares", ("=", ("-", P(a, 2), P(b, 2)), ("*", ("()", ("+", a, b)), ("()", ("-", a, b))))),
    ("the square of a sum", ("=", P(("()", ("+", a, b)), 2), ("+", ("+", P(a, 2), ("*", ("*", N(2), a), b)), P(b, 2)))),
    ("the Pythagorean identity", ("=", ("+", P(("f", "sin", V("theta")), 2), P(("f", "cos", V("theta")), 2)), N(1))),
    ("Euler's identity", ("=", ("+", P(V("e"), ("*", V("i"), V("pi"))), N(1)), N(0))),
    ("the sum of the first n whole numbers", ("=", ("sum", V("i"), N(1), n, V("i")), ("/", ("*", n, ("()", ("+", n, N(1)))),
                                                                                    N(2)))),
    ("the power rule for derivatives", ("=", ("d", x, P(x, n)), ("*", n, P(x, ("-", n, N(1)))))),
    ("the integral of x to the n", ("=", ("int", None, None, P(x, n), x),
                                    ("+", ("/", P(x, ("+", n, N(1))), ("+", n, N(1))), V("C")))),
    ("the definition of e as a limit", ("=", ("lim", n, ("n", "\\infty"), P(("()", ("+", N(1), ("/", N(1), n))), n)),
                                        V("e"))),
    ("compound interest", ("=", V("A"), ("*", V("P"), P(("()", ("+", N(1), ("/", r, n))), ("*", n, t))))),
    ("the density formula", ("=", V("rho"), ("/", m, V("V")))),
    ("the formula for power in a circuit", ("=", V("P"), ("*", V("I"), V("V")))),
    ("the law of universal gravitation", ("=", V("F"), ("/", ("*", ("*", V("G"), ("_", m, N(1))), ("_", m, N(2))),
                                                         P(r, 2)))),
    ("the formula for work", ("=", V("W"), ("*", V("F"), V("d")))),
    ("the photosynthesis equation", ("->", ("chem", "6CO_2 + 6H_2O"), ("chem", "C_6H_{12}O_6 + 6O_2"))),
    ("the burning of hydrogen", ("->", ("chem", "2H_2 + O_2"), ("chem", "2H_2O"))),
    ("the burning of methane", ("->", ("chem", "CH_4 + 2O_2"), ("chem", "CO_2 + 2H_2O"))),
    ("the logarithm of a product", ("=", ("f", "log", ("()", ("*", a, b))), ("+", ("f", "log", a), ("f", "log", b)))),
    ("the mean of n numbers", ("=", V("mu"), ("*", ("/", N(1), n), ("sum", V("i"), N(1), n, ("_", x, V("i")))))),
    ("the change in a quantity", ("=", ("*", V("Delta"), x), ("-", ("_", x, N(2)), ("_", x, N(1))))),
]

# ----------------------------------------------------------------- made-up formulas

LETTERS = ("x", "y", "t", "a", "b", "n", "z", "u")


def coefficient_term(rng, var, power):
    """A term such as 3x^2, x, 5 (a coefficient that is 1 is not written)."""
    k = rng.randint(1, 9)
    base = var if power == 1 else P(var, power)
    if power == 0:
        return N(k)
    return base if k == 1 else ("*", N(k), base)


def polynomial(rng, var, degree):
    """A polynomial in var of the given degree, terms joined by plus or minus."""
    out = coefficient_term(rng, var, degree)
    for power in range(degree - 1, -1, -1):
        if rng.random() < 0.75:
            out = (rng.choice("+-"), out, coefficient_term(rng, var, power))
    return out


def made_up(rng):
    """One made-up formula tree from the grammar (see the module docstring)."""
    var = V(rng.choice(LETTERS))
    k, j = rng.randint(2, 12), rng.randint(2, 9)
    choice = rng.randrange(14)
    if choice == 0:
        return ("=", polynomial(rng, var, 2), N(0))
    if choice == 1:
        return ("=", polynomial(rng, var, 1), N(rng.randint(-20, 40)))
    if choice == 2:
        return ("=", ("+", ("/", var, N(k)), ("/", N(j), N(k + 1))), N(rng.randint(1, 9)))
    if choice == 3:
        return ("=", ("sqrt", ("+", P(var, 2), N(k))), N(j))
    if choice == 4:
        inside = (rng.choice("+-"), coefficient_term(rng, var, 1), N(rng.randint(1, 9)))
        return ("=", ("*", N(k), ("()", inside)), polynomial(rng, var, 1))
    if choice == 5:
        return ("=", ("f", rng.choice(("sin", "cos", "tan")), ("*", N(2), V("theta"))),
                ("/", N(1), N(2)))
    if choice == 6:
        return ("=", ("f", rng.choice(("log", "ln")), var), N(k))
    if choice == 7:
        return ("sum", V("k"), N(1), N(k), P(V("k"), rng.choice((2, 3))))
    if choice == 8:
        return ("int", N(0), N(j), polynomial(rng, var, 2), var)
    if choice == 9:
        return ("d", var, polynomial(rng, var, 3))
    if choice == 10:
        return (rng.choice(("<", ">", "<=", ">=")), polynomial(rng, var, 1), N(rng.randint(0, 30)))
    if choice == 11:
        return ("=", ("/", polynomial(rng, var, 2), ("-", var, N(j))), ("+", var, N(k)))
    if choice == 12:
        return ("=", ("root", N(rng.choice((3, 4))), var), N(j))
    return ("=", P(var, ("/", N(1), N(j))), N(k))


# ----------------------------------------------------------------- typesetting

FONTSETS = ("cm", "stix", "stixsans", "dejavusans", "dejavuserif")
BACKGROUNDS = ("paper", "notebook", "graph", "whiteboard", "textbook")


def typeset(tex, fontset, size, colour):
    """The formula $tex$ typeset by matplotlib's mathtext, as a cropped RGBA PIL image (transparent around the ink),
    or None when mathtext cannot typeset it."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    with matplotlib.rc_context({"mathtext.fontset": fontset}):
        fig = plt.figure(figsize=(0.01, 0.01))
        try:
            fig.text(0, 0, f"${tex}$", fontsize=size, color=colour)
            buffer = io.BytesIO()
            fig.savefig(buffer, dpi=150, transparent=True, bbox_inches="tight", pad_inches=0.08, format="png")
        except Exception:  # noqa: BLE001 - mathtext could not typeset it: the formula is not used
            return None
        finally:
            plt.close(fig)
    return Image.open(io.BytesIO(buffer.getvalue())).convert("RGBA")


def page_for(ink, kind, rng, caption=""):
    """The typeset formula placed on a background of kind (see BACKGROUNDS), as an RGB image."""
    from PIL import Image, ImageDraw
    w, h = ink.size
    pad_x, pad_y = rng.randint(60, 200), rng.randint(60, 160)
    width, height = w + 2 * pad_x, h + 2 * pad_y + (50 if caption else 0)
    colour = {"paper": (252, 251, 247), "notebook": (250, 250, 244), "graph": (250, 252, 250),
              "whiteboard": (244, 246, 248), "textbook": (248, 246, 240)}[kind]
    page = Image.new("RGB", (width, height), colour)
    draw = ImageDraw.Draw(page)
    if kind == "notebook":
        for yy in range(30, height, 34):
            draw.line([0, yy, width, yy], fill=(170, 200, 230), width=1)
        draw.line([50, 0, 50, height], fill=(230, 150, 150), width=2)
    elif kind == "graph":
        for v in range(0, max(width, height), 24):
            draw.line([v, 0, v, height], fill=(200, 225, 205), width=1)
            draw.line([0, v, width, v], fill=(200, 225, 205), width=1)
    elif kind == "whiteboard":
        draw.rectangle([0, 0, width - 1, height - 1], outline=(150, 150, 155), width=8)
    page.paste(ink, (pad_x, pad_y), ink)
    if caption:
        draw.text((pad_x, height - 60), caption, font=font(22, False, rng.randrange(4)), fill=(60, 60, 60))
    return page


def formula_rows(tree, name="", number=""):
    """The rows of one formula (see the module docstring); every row carries "latex". number: the equation number
    printed beside it on a textbook page ("(3.26)"), said after the formula."""
    tex = latex(tree)
    words = spoken(tree) + (f". It is numbered {number}" if number else "")
    rows = []
    if name:
        rows.append({"question": NAME_Q, "answer": f"It is {name}: {words}."})
    rows += [{"question": SAY_Q, "answer": f"It says: {words}. In LaTeX: {tex}"},
             {"question": LATEX_Q, "answer": tex}]
    return [dict(r, latex=tex, credit=CREDIT, synthetic=True) for r in rows]


def make_formula(n, seed=SEED):
    """The n-th formula as (file name, JPEG bytes, rows), or None when it cannot be typeset. Every third picture is
    a named formula; the others are made up."""
    rng = seeded(seed, n)
    if n % 3 == 0:
        name, tree = NAMED_FORMULAS[(n // 3) % len(NAMED_FORMULAS)]
    else:
        name, tree = "", made_up(rng)
    colour = rng.choice(("#111111", "#111111", "#1a2a6c", "#0b3d0b"))
    ink = typeset(latex(tree), rng.choice(FONTSETS), rng.randint(20, 34), colour)
    if ink is None:
        return None
    kind = rng.choice(BACKGROUNDS)
    caption = f"({rng.randint(1, 12)}.{rng.randint(1, 30)})" if kind == "textbook" else ""
    page = page_for(ink, kind, rng, caption)
    if rng.random() < 0.35:
        data = phone_photo(page, rng, strength=rng.uniform(0.2, 0.8))
    else:
        buffer = io.BytesIO()
        page.save(buffer, "JPEG", quality=92)
        data = buffer.getvalue()
    return f"formula-{n:05d}.jpg", data, formula_rows(tree, name, caption)


def build_synthetic_formulas(limit):
    """The synthetic_formulas pack (see the module docstring)."""
    from food_packs import with_twins
    out, n = [], 0
    while len(out) < limit and n < limit * 2:
        made = make_formula(n)
        n += 1
        if made:
            out.append(made)
    return with_twins(out)


# ----------------------------------------------------------------- chemical structures (RDKit, Wikidata SMILES)

# English Wikipedia titles of common compounds; Wikidata gives each one's item, English name and SMILES.
CHEMICALS = (
    "Water", "Hydrogen peroxide", "Ammonia", "Methane", "Ethane", "Propane", "Butane", "Octane", "Ethylene",
    "Acetylene", "Benzene", "Toluene", "Naphthalene", "Phenol", "Methanol", "Ethanol", "Isopropyl alcohol", "Glycerol",
    "Ethylene glycol", "Acetone", "Formaldehyde", "Acetaldehyde", "Acetic acid", "Formic acid", "Citric acid",
    "Lactic acid", "Oxalic acid", "Tartaric acid", "Malic acid", "Ascorbic acid", "Benzoic acid", "Salicylic acid",
    "Aspirin", "Paracetamol", "Ibuprofen", "Naproxen", "Caffeine", "Theobromine", "Nicotine", "Glucose", "Fructose",
    "Sucrose", "Lactose", "Maltose", "Ribose", "Glycine", "Alanine", "Valine", "Leucine", "Isoleucine", "Proline",
    "Phenylalanine", "Tryptophan", "Methionine", "Serine", "Threonine", "Cysteine", "Tyrosine", "Asparagine",
    "Glutamine", "Aspartic acid", "Glutamic acid", "Lysine", "Arginine", "Histidine", "Urea", "Uric acid", "Creatine",
    "Cholesterol", "Testosterone", "Estradiol", "Progesterone", "Cortisol", "Adrenaline", "Norepinephrine",
    "Dopamine", "Serotonin", "Melatonin", "Histamine", "Acetylcholine", "Adenine", "Guanine", "Cytosine", "Thymine",
    "Uracil", "Adenosine triphosphate", "Nicotinamide", "Riboflavin", "Thiamine", "Pyridoxine", "Folic acid",
    "Biotin", "Retinol", "Beta-Carotene", "Capsaicin", "Menthol", "Vanillin", "Cinnamaldehyde", "Limonene",
    "Eugenol", "Camphor", "Carvone", "Linalool", "Geraniol", "Thymol", "Ethyl acetate", "Diethyl ether",
    "Chloroform", "Dichloromethane", "Carbon tetrachloride", "Hexane", "Cyclohexane", "Styrene", "Aniline",
    "Pyridine", "Furan", "Thiophene", "Pyrrole", "Indole", "Imidazole", "Morphine", "Codeine", "Quinine",
    "Benzylpenicillin", "Amoxicillin", "Metformin", "Atorvastatin", "Omeprazole", "Lisinopril", "Amlodipine",
    "Levothyroxine", "Sertraline", "Fluoxetine", "Diazepam", "Warfarin", "Sildenafil", "Loratadine", "Cetirizine",
    "Diphenhydramine", "Pseudoephedrine", "Dextromethorphan", "Lidocaine", "Benzocaine", "Saccharin", "Aspartame",
    "Sucralose", "Monosodium glutamate", "Sodium bicarbonate", "Sulfuric acid", "Nitric acid", "Phosphoric acid",
    "Carbon dioxide", "Nitrous oxide", "Ozone", "Sulfur dioxide", "Hydrogen sulfide", "Coumarin", "Resveratrol",
    "Quercetin", "Curcumin", "Piperine", "Allicin", "Salicin", "Oleic acid", "Linoleic acid", "Palmitic acid",
    "Stearic acid", "Butyric acid", "Propionic acid", "Succinic acid", "Fumaric acid", "Pyruvic acid", "Glutathione",
    "Taurine", "Carnitine", "Choline", "Inositol", "Xylitol", "Sorbitol", "Mannitol", "Erythritol", "Trehalose",
    "Galactose", "Mannose", "Deoxyribose", "Glucosamine", "Dimethyl sulfoxide", "Tetrahydrofuran", "Acetonitrile",
    "Nitrobenzene", "Bisphenol A", "Ethylenediaminetetraacetic acid", "Sodium dodecyl sulfate", "Triclosan",
    "Methylparaben", "Hydroquinone", "Benzoyl peroxide", "Tretinoin", "Minoxidil", "Oxybenzone", "Avobenzone",
    "DEET", "Permethrin", "Glyphosate", "Bilirubin", "Heme", "Cinnamic acid", "Gallic acid", "Tannic acid",
)
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
CHEM_CREDIT = ("A structure drawn with RDKit by packs/math_notation_packs.py from the SMILES in Wikidata item {qid} "
               "(https://www.wikidata.org/wiki/{qid}; Wikidata CC0), CC0")
CHEM_NAME_Q = "What chemical is this?"
CHEM_FORMULA_Q = "What is its molecular formula?"
CHEM_DESCRIBE_Q = "Describe this structure."
CHEM_SMILES_Q = "What is the SMILES for this?"
ELEMENT_NAMES = {"C": "carbon", "H": "hydrogen", "O": "oxygen", "N": "nitrogen", "S": "sulfur", "P": "phosphorus",
                 "Cl": "chlorine", "Br": "bromine", "I": "iodine", "F": "fluorine", "Na": "sodium", "K": "potassium",
                 "Fe": "iron", "Ca": "calcium", "Mg": "magnesium", "B": "boron", "Si": "silicon"}


def wikidata_compounds(titles=CHEMICALS):
    """[(name, Wikidata item, SMILES)] for the English Wikipedia titles, from Wikidata's own API (isomeric SMILES
    when recorded, else canonical; deprecated statements skipped), 25 titles a request, patiently (Wikimedia asks for
    slow, serial requests)."""
    s, out = session(), []
    for start in range(0, len(titles), 25):
        batch = titles[start:start + 25]
        data = {}
        for attempt in range(6):
            try:
                r = s.get(WIKIDATA_API, timeout=60, params={
                    "action": "wbgetentities", "sites": "enwiki", "titles": "|".join(batch), "normalize": 1,
                    "props": "labels|claims", "languages": "en", "format": "json", "maxlag": 5})
                if r.status_code == 200:
                    data = r.json()
                    break
            except Exception:  # noqa: BLE001 - wait longer each time
                pass
            time.sleep(15 * (attempt + 1))
        for qid, entity in sorted((data.get("entities") or {}).items()):
            if not qid.startswith("Q"):
                continue
            claims = entity.get("claims") or {}

            def values(prop):
                """The non-deprecated string values of a property."""
                return [c["mainsnak"]["datavalue"]["value"] for c in claims.get(prop, [])
                        if c.get("rank") != "deprecated" and (c.get("mainsnak") or {}).get("datavalue")]
            smiles = (values("P2017") or values("P233") or [""])[0]
            name = ((entity.get("labels") or {}).get("en") or {}).get("value", "")
            if smiles and name:
                out.append((name, qid, smiles))
        time.sleep(2)
    say(f"Wikidata: SMILES for {len(out)} of {len(titles)} compounds")
    return out


def structure_facts(smiles):
    """What RDKit works out from a SMILES: {"formula", "atoms" ([(element, count)] heavy atoms, carbon first),
    "rings", "aromatic", "canonical"}, or None when RDKit cannot read it."""
    from rdkit import Chem
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    counts = {}
    for atom in mol.GetAtoms():
        counts[atom.GetSymbol()] = counts.get(atom.GetSymbol(), 0) + 1
    order = sorted(counts, key=lambda e: (e != "C", e != "H", e))
    info = mol.GetRingInfo()
    aromatic = sum(1 for ring in info.AtomRings() if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring))
    return {"formula": CalcMolFormula(mol), "atoms": [(e, counts[e]) for e in order], "rings": info.NumRings(),
            "aromatic": aromatic, "canonical": Chem.MolToSmiles(mol)}


def formula_words(formula):
    """ "C8H10N4O2" said as "C 8 H 10 N 4 O 2" (a charge sign as "plus" or "minus")."""
    parts = re.findall(r"[A-Z][a-z]?|\d+|[+-]", formula)
    return " ".join({"+": "plus", "-": "minus"}.get(p, p) for p in parts)


def chem_rows(name, qid, smiles, facts):
    """The rows of one structure (see the module docstring); every row carries "smiles"."""
    atoms = ", ".join(f"{k} {ELEMENT_NAMES.get(e, e)}" for e, k in facts["atoms"])
    rings = ("no rings" if not facts["rings"] else f"{facts['rings']} ring{'s' if facts['rings'] > 1 else ''}"
             + ((", which is aromatic" if facts["rings"] == 1 else f", {facts['aromatic']} of them aromatic")
                if facts["aromatic"] else (", not aromatic" if facts["rings"] == 1 else ", none aromatic")))
    credit = CHEM_CREDIT.format(qid=qid)
    rows = [{"question": CHEM_NAME_Q, "answer": f"It is the structure of {name} (Wikidata {qid}), molecular formula "
             f"{facts['formula']}."},
            {"question": CHEM_FORMULA_Q, "answer": f"{facts['formula']}, said {formula_words(facts['formula'])}."},
            {"question": CHEM_DESCRIBE_Q, "answer": f"A skeletal structure of {name}. Its atoms other than hydrogen: "
             f"{atoms}; it has {rings}."},
            {"question": CHEM_SMILES_Q, "answer": facts["canonical"]}]
    return [dict(r, smiles=facts["canonical"], credit=credit, synthetic=True) for r in rows]


def draw_structure(smiles, rng):
    """A skeletal drawing of the SMILES by RDKit, as an RGB PIL image (size, line width, atom colours and rotation
    vary)."""
    from PIL import Image
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D
    mol = Chem.MolFromSmiles(smiles)
    size = rng.choice((500, 600, 700))
    drawer = rdMolDraw2D.MolDraw2DCairo(size, size)
    options = drawer.drawOptions()
    options.bondLineWidth = rng.choice((1, 2, 2, 3))
    options.rotate = rng.choice((0, 0, 30, 90, 180, 270))
    if rng.random() < 0.4:
        options.useBWAtomPalette()
    options.addStereoAnnotation = False
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return Image.open(io.BytesIO(drawer.GetDrawingText())).convert("RGB")


def build_chem_structures(limit, compounds=None):
    """The chem_structures pack (see the module docstring): each compound drawn a few times in different styles,
    until limit pictures. compounds: [(name, item, SMILES)] (else read from Wikidata)."""
    from food_packs import with_twins
    compounds = compounds if compounds is not None else wikidata_compounds()
    usable = []
    for name, qid, smiles in compounds:
        facts = structure_facts(smiles)
        if facts and facts["atoms"]:
            usable.append((name, qid, smiles, facts))
    out, n = [], 0
    while usable and len(out) < limit:
        name, qid, smiles, facts = usable[n % len(usable)]
        rng = seeded(SEED + 1, n)
        page = draw_structure(smiles, rng)
        if rng.random() < 0.3:
            data = phone_photo(page, rng, strength=rng.uniform(0.2, 0.7))
        else:
            buffer = io.BytesIO()
            page.save(buffer, "JPEG", quality=92)
            data = buffer.getvalue()
        out.append((f"chem-{qid}-{n // max(1, len(usable))}.jpg", data, chem_rows(name, qid, smiles, facts)))
        n += 1
        if n >= len(usable) * 4:                   # at most four drawings of each compound
            break
    return with_twins(out)


MATH_PACKS = {
    "synthetic_formulas": (build_synthetic_formulas,
                           "Computer-made (synthetic) formulas typeset with matplotlib's mathtext by "
                           "packs/math_notation_packs.py from a fixed seed: well-known formulas of maths, physics and "
                           "chemistry and made-up ones, each with its exact LaTeX and a spoken reading. CC0."),
    "chem_structures": (build_chem_structures,
                        "Chemical structures drawn with RDKit (BSD) by packs/math_notation_packs.py from the SMILES "
                        "recorded in Wikidata (CC0, https://www.wikidata.org), with formulas and counts worked out by "
                        "RDKit. CC0."),
}
MATH_LIMITS = {"synthetic_formulas": 3000, "chem_structures": 800}
# chem_structures reads Wikidata (Wikimedia's servers), so it goes in the Commons lane with its slow, serial requests.
MATH_COMMONS_KEYS = ("chem_structures",)


def main(argv=None):
    """Make a few pictures and print their rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Try a maths and science notation pack builder.")
    parser.add_argument("key", choices=sorted(MATH_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = MATH_PACKS[args.key][0](args.limit)
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
