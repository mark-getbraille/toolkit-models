"""A guard: Stack Exchange content is NEVER used for training.

Why: Stack Exchange restricts using its content to train AI (its robots.txt says "Content-signal: search=no,
ai-train=no" and "Disallow: /" to every program, checked 2026-11-22). The reference library lists Stack Exchange's
how-to sites only as Kiwix books for reading (textbooks/stack_exchange.py: every entry reference_only=True, with the
notice "For reading and looking things up only; not for AI training (Stack Exchange's terms)."). No picture pack,
training-kit collection, topic add-on or training script may use them.

It checks that:
  - no Python file of the packs, the kit, tools or scripts (outside textbooks/, where the reference-only list lives)
    has a Stack Exchange address or the name of one of the Kiwix Stack Exchange books in its code (comments and
    docstrings may name them, to explain why they are not used); test files hold made-up records and are not looked
    at;
  - no workflow, Windows command or shell script that builds packs or the kit names them;
  - none of the kit's collections (sources.SOURCES, and every *_sources.py table) has a Stack Exchange address in its
    fields;
  - the reference library still marks every Stack Exchange Kiwix book reference only, with the notice.

Run it from the training-kit folder:   xvfb-run -a python3 -m pytest -q tests/test_no_stack_exchange.py
"""

import ast
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit")
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, KIT)

# Every host of the Stack Exchange network, and the Kiwix book names made from them ("diy.stackexchange.com_en_all").
HOSTS = r"(?:[a-z0-9-]+\.)*(?:stackexchange\.com|stackoverflow\.com|superuser\.com|serverfault\.com|askubuntu\.com|" \
        r"mathoverflow\.net|stackapps\.com)"
ADDRESS = re.compile(HOSTS, re.I)
SKIP_DIRS = {".git", "__pycache__", "node_modules", "textbooks"}


def python_files():
    """Every Python file of the repository outside textbooks/, except tests (test_*.py) and skipped folders."""
    for top, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py") and not f.startswith("test_"):
                yield os.path.join(top, f)


def code_strings(path):
    """[(line, text)] of the string constants in a Python file's code, leaving out docstrings."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body \
                and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            docs.add(id(node.body[0].value))
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs]


def test_the_rule_itself():
    """Addresses and Kiwix names are caught; ordinary words are not."""
    for text in ("https://diy.stackexchange.com/questions/1", "cooking.stackexchange.com_en_all", "askubuntu.com",
                 "https://superuser.com/a/2", "stackoverflow.com_en_all_2026-07.zim"):
        assert ADDRESS.search(text), text
    for text in ("stack of exchange papers", "a super user", "ask ubuntu users"):
        assert not ADDRESS.search(text), text


def test_no_pack_or_kit_code_names_stack_exchange():
    """No Stack Exchange address or Kiwix book name in the code of the packs, the kit, tools or scripts."""
    problems = [f"{os.path.relpath(path, REPO)}:{line}: {text[:80]}"
                for path in python_files() for line, text in code_strings(path) if ADDRESS.search(text)]
    assert not problems, "Code that could use Stack Exchange content:\n" + "\n".join(problems)


def test_no_script_names_stack_exchange():
    """No workflow, Windows command or shell script of the packs or the kit names Stack Exchange."""
    problems = []
    for top, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith((".yml", ".yaml", ".cmd", ".bat", ".sh", ".ps1")) or f == "request.txt":
                path = os.path.join(top, f)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    if ADDRESS.search(fh.read()):
                        problems.append(os.path.relpath(path, REPO))
    assert not problems, problems


def test_no_kit_collection_uses_stack_exchange():
    """No field of any of the kit's collections (sources.SOURCES and the *_sources.py tables) is a Stack Exchange
    address."""
    import sources
    tables = list(sources.SOURCES)
    for f in sorted(os.listdir(KIT)):
        if f.endswith("_sources.py"):
            try:
                module = importlib.import_module(f[:-3])
            except Exception:  # noqa: BLE001 - a table that needs optional packages is checked by the code scan
                continue
            for value in vars(module).values():
                if isinstance(value, (list, tuple)):
                    tables += list(value)
    bad = [repr(item)[:100] for item in tables if ADDRESS.search(repr(vars(item)) if hasattr(item, "__dict__")
                                                                 else repr(item))]
    assert not bad, bad


def test_reference_library_marks_them_reference_only():
    """textbooks/stack_exchange.py marks every Stack Exchange Kiwix book reference only, with the notice."""
    sys.path.insert(0, os.path.join(REPO, "textbooks"))
    import stack_exchange
    notice = "For reading and looking things up only; not for AI training (Stack Exchange's terms)."
    assert stack_exchange.REFERENCE_ONLY_NOTICE == notice
    assert stack_exchange.SITES and all(s["reference_only"] for s in stack_exchange.SITES)
    assert set(stack_exchange.KIWIX_REFERENCE_ONLY) == {s["kiwix"] for s in stack_exchange.SITES}
    assert all(notice in label for label in stack_exchange.KIWIX_LABELS.values())
