"""Math as readable text, for the textbooks' ZIM files.

The Digital Accessibility Toolkit's article reader (app/toolkit/library/zim.py, html_to_text) leaves <math> elements
out, and its Send to braille, DAISY and TTS hand-overs take the article's plain text. So every formula is written
into the page as linear text that a screen reader speaks and liblouis translates: "x^2 + 3x − 4 = 0",
"v = (d)/(t)", "sqrt(2)", "Δd = d_f − d_0". The same words are the element's aria-label, so the Kiwix apps' readers
speak them too.

  mathml_text(element)   an ElementTree MathML element (OpenStax CNXML: m:math) -> text
  latex_text(source)     a LaTeX formula (Siyavula's \\( ... \\) and \\[ ... \\]) -> text
"""

import re

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε", "zeta": "ζ",
    "eta": "η", "theta": "θ", "vartheta": "θ", "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν",
    "xi": "ξ", "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ", "varphi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
SYMBOLS = {
    "times": "×", "div": "÷", "cdot": "·", "pm": "±", "mp": "∓", "ne": "≠", "neq": "≠", "le": "≤", "leq": "≤",
    "ge": "≥", "geq": "≥", "lt": "<", "gt": ">", "approx": "≈", "equiv": "≡", "sim": "~", "propto": "∝",
    "infty": "∞", "degree": "°", "circ": "°", "therefore": "∴", "because": "∵", "in": "∈", "notin": "∉",
    "subset": "⊂", "subseteq": "⊆", "cup": "∪", "cap": "∩", "emptyset": "∅", "varnothing": "∅", "forall": "∀",
    "exists": "∃", "rightarrow": "→", "to": "→", "leftarrow": "←", "Rightarrow": "⇒", "Leftrightarrow": "⇔",
    "leftrightarrow": "↔", "angle": "∠", "triangle": "△", "parallel": "∥", "perp": "⊥", "ldots": "...",
    "cdots": "...", "dots": "...", "prime": "′", "partial": "∂", "nabla": "∇", "sum": "Σ", "prod": "Π",
    "int": "∫", "%": "%", "$": "$", "{": "{", "}": "}", "_": "_", "&": "&", "#": "#", "|": "‖",
    "langle": "⟨", "rangle": "⟩", "lbrace": "{", "rbrace": "}", "mid": "|", "colon": ":", "neg": "¬",
    "land": "∧", "lor": "∨", "hbar": "ℏ", "ell": "ℓ", "Re": "ℜ", "Im": "ℑ", "star": "*", "ast": "*",
    "bullet": "•", "checkmark": "✓",
}
FUNCTIONS = {"sin", "cos", "tan", "cot", "sec", "csc", "cosec", "log", "ln", "exp", "lim", "max", "min", "det",
             "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh"}
BLACKBOARD = {"N": "ℕ", "Z": "ℤ", "Q": "ℚ", "R": "ℝ", "C": "ℂ"}
SPACES = {",", ";", ":", "!", "quad", "qquad", " ", "enspace", "thinspace", "medspace", "thickspace"}
ACCENTS = {"bar": "bar", "overline": "bar", "hat": "hat", "vec": "vector", "dot": "dot", "ddot": "double dot",
           "tilde": "tilde", "overrightarrow": "vector", "widehat": "hat", "underline": "underlined"}


def _simple(text):
    """True when text needs no brackets around it as a numerator, denominator, power or root ("2", "x", "10")."""
    return bool(re.fullmatch(r"[\w.,′°]+", text or "")) or len(text or "") <= 1


def _wrap(text):
    """text in brackets unless it is simple."""
    text = (text or "").strip()
    return text if _simple(text) else f"({text})"


def _tidy(text):
    """Single spaces, none before closing punctuation."""
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+([,.;)\]])", r"\1", text)


# ---------------------------------------------------------------------- MathML

def _local(tag):
    """A tag without its namespace ("{http://www.w3.org/1998/Math/MathML}mi" -> "mi")."""
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _children(el):
    """The element children of el (comments left out)."""
    return [c for c in el if isinstance(c.tag, str)]


def _mml(el):
    """The text of one MathML element."""
    tag = _local(el.tag)
    kids = _children(el)
    if tag in ("mi", "mn", "mtext", "ms"):
        return (el.text or "").strip() if tag != "mtext" else " ".join((el.text or "").split())
    if tag == "mo":
        op = (el.text or "").strip()
        if op in ("=", "+", "−", "-", "×", "÷", "<", ">", "≤", "≥", "≠", "≈", "±", "→", "⇒", "·"):
            return f" {op} "
        if op == ",":
            return ", "
        return op
    if tag == "mspace":
        return " "
    if tag in ("mfrac",) and len(kids) == 2:
        return f"{_wrap(_mml(kids[0]))}/{_wrap(_mml(kids[1]))}"
    if tag == "msqrt":
        return f"sqrt({_tidy(''.join(_mml(k) for k in kids))})"
    if tag == "mroot" and len(kids) == 2:
        return f"root {_tidy(_mml(kids[1]))} of ({_tidy(_mml(kids[0]))})"
    if tag == "msup" and len(kids) == 2:
        return f"{_tidy(_mml(kids[0]))}^{_wrap(_tidy(_mml(kids[1])))}"
    if tag == "msub" and len(kids) == 2:
        return f"{_tidy(_mml(kids[0]))}_{_wrap(_tidy(_mml(kids[1])))}"
    if tag == "msubsup" and len(kids) == 3:
        return f"{_tidy(_mml(kids[0]))}_{_wrap(_tidy(_mml(kids[1])))}^{_wrap(_tidy(_mml(kids[2])))}"
    if tag in ("mover", "munder", "munderover") and kids:
        base = _tidy(_mml(kids[0]))
        marks = [_tidy(_mml(k)) for k in kids[1:]]
        accent = {"¯": "bar", "‾": "bar", "^": "hat", "→": "vector", "⇀": "vector", "˙": "dot", "~": "tilde",
                  "˜": "tilde", "_": "underlined"}
        if len(marks) == 1 and marks[0] in accent:
            return f"{base} {accent[marks[0]]} " if accent[marks[0]] != "vector" else f"vector {base} "
        if tag == "munder":
            return f"{base}_{_wrap(marks[0])}" if marks else base
        if tag == "mover":
            return f"{base}^{_wrap(marks[0])}" if marks else base
        return f"{base}_{_wrap(marks[0])}^{_wrap(marks[1])}" if len(marks) == 2 else base
    if tag == "mfenced":
        open_, close = el.get("open", "("), el.get("close", ")")
        sep = el.get("separators", ",")
        return open_ + (sep[:1] + " ").join(_tidy(_mml(k)) for k in kids) + close
    if tag == "mtable":
        rows = []
        for row in kids:
            cells = [_tidy(_mml(c)) for c in _children(row)] if _local(row.tag) in ("mtr", "mlabeledtr") \
                else [_tidy(_mml(row))]
            rows.append(", ".join(c for c in cells if c))
        return "; ".join(r for r in rows if r)
    if tag == "semantics":
        return _mml(kids[0]) if kids else ""
    if tag in ("annotation", "annotation-xml", "none", "mprescripts", "malignmark", "maligngroup"):
        return ""
    if tag == "menclose":
        return f"({_tidy(''.join(_mml(k) for k in kids))})"
    # math, mrow, mstyle, mpadded, mphantom, mtd, merror ... : their children in order
    return "".join(_mml(k) for k in kids) + ("" if kids else (el.text or ""))


def mathml_text(element):
    """Readable linear text of a MathML element (see the module docstring)."""
    try:
        return _tidy(_mml(element))
    except RecursionError:
        return ""


# ---------------------------------------------------------------------- LaTeX

def _tokens(src):
    """The tokens of a LaTeX formula: commands ("\\frac"), braces, ^ _ and single characters."""
    out, i = [], 0
    while i < len(src):
        ch = src[i]
        if ch == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", src[i:])
            out.append("\\" + m.group(1))
            i += len(m.group(0))
            if m.group(1).isalpha():
                while i < len(src) and src[i] == " ":
                    i += 1
            continue
        out.append(ch)
        i += 1
    return out


class _Latex:
    """A small reader of LaTeX formulas: a recursive walk over the tokens, giving linear text."""

    def __init__(self, src):
        """src: the formula without its \\( \\) marks."""
        self.t = _tokens(src)
        self.i = 0

    def group(self):
        """The text of the next argument: a {...} group or a single token."""
        while self.i < len(self.t) and self.t[self.i] == " ":
            self.i += 1
        if self.i >= len(self.t):
            return ""
        if self.t[self.i] == "{":
            self.i += 1
            return self.seq("}")
        return self.atom()

    def optional(self):
        """The text of an optional [...] argument, or None."""
        if self.i < len(self.t) and self.t[self.i] == "[":
            self.i += 1
            return self.seq("]")
        return None

    def seq(self, end=None):
        """Tokens up to end (consumed) as text."""
        parts = []
        while self.i < len(self.t):
            if end is not None and self.t[self.i] == end:
                self.i += 1
                break
            if end is None and self.t[self.i] == "}":
                self.i += 1
                continue
            parts.append(self.atom())
        return "".join(parts)

    def atom(self):
        """The text of one item: a command with its arguments, a group, a power or index, a character."""
        tok = self.t[self.i]
        self.i += 1
        if tok == "{":
            return self.seq("}")
        if tok == "^":
            return "^" + _wrap(_tidy(self.group()))
        if tok == "_":
            return "_" + _wrap(_tidy(self.group()))
        if tok in ("=", "+", "<", ">"):
            return f" {tok} "
        if tok == "-":
            return " − "
        if tok == "&":
            return " "
        if tok == "~":
            return " "
        if not tok.startswith("\\"):
            return tok
        name = tok[1:]
        if name in ("frac", "dfrac", "tfrac"):
            a, b = _tidy(self.group()), _tidy(self.group())
            return f"{_wrap(a)}/{_wrap(b)}"
        if name == "sqrt":
            n = self.optional()
            body = _tidy(self.group())
            return f"root {_tidy(n)} of ({body})" if n else f"sqrt({body})"
        if name in ("text", "textrm", "mathrm", "textit", "textbf", "mathbf", "mathit", "operatorname",
                    "mbox", "boldsymbol", "mathsf", "texttt"):
            return self.group()
        if name == "mathbb":
            inner = self.group()
            return BLACKBOARD.get(inner, inner)
        if name in ACCENTS:
            inner = _tidy(self.group())
            word = ACCENTS[name]
            if word == "vector":
                return f"vector {inner} "
            if name in ("dot", "overline") and re.fullmatch(r"\d+", inner):
                return f"{inner} recurring "
            return f"{inner} {word} "
        if name in ("left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr"):
            if self.i < len(self.t):
                nxt = self.t[self.i]
                self.i += 1
                return "" if nxt == "." else SYMBOLS.get(nxt[1:], nxt[1:]) if nxt.startswith("\\") else nxt
            return ""
        if name in ("begin", "end"):
            self.group()
            return " "
        if name == "\\":
            return "; "
        if name in SPACES:
            return " "
        if name in GREEK:
            return GREEK[name]
        if name in SYMBOLS:
            sym = SYMBOLS[name]
            return f" {sym} " if sym in ("×", "÷", "±", "≠", "≤", "≥", "≈", "≡", "→", "⇒", "⇔", "∈", "∴") else sym
        if name in FUNCTIONS:
            return f"{name} "
        if name in ("displaystyle", "textstyle", "scriptstyle", "limits", "nolimits", "hline", "label", "tag"):
            if name in ("label", "tag"):
                self.group()
            return ""
        return name


def latex_text(source):
    """Readable linear text of a LaTeX formula (see the module docstring)."""
    try:
        return _tidy(_Latex(source.strip()).seq())
    except (IndexError, RecursionError):
        return " ".join(source.split())
