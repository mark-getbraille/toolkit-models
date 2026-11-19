"""Self-tests of two things that keep pack builds from failing on other people's servers (nothing is downloaded):

  - The Commons lane. The workflow (.github/workflows/packs.yml) builds the packs that read the Wikimedia Commons API
    in their own lane, two at a time, because Commons refused requests for hours when ten packs read it together.
    These tests check that build_packs.COMMONS_KEYS names every such pack (every key named commons_..., and every
    builder that calls one of the Commons helpers, found by following the functions it calls), that pack_lanes splits
    keys with their "+" and "?" marks correctly, and that the plan step's own Python in packs.yml prints the two lanes.
  - Dropped connections. A request through build_packs.session() that fails with a dropped connection (an SSL error,
    a reset, a cut-off download, a timeout) is made again, also when the drop happens on the server a download was
    redirected to (as archive.org does), and fetch_all keeps a picture whose first try was dropped.

Run it from the repository's folder:   python3 -m pytest packs/test_lanes.py
"""

import io
import json
import os
import re
import subprocess
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_packs  # noqa: E402

import requests  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")
# The names that show a builder reads the Commons API.
COMMONS_HELPERS = {"commons_get", "commons_members", "commons_entries", "mech_entries", "us_commons", "COMMONS_API"}


# ----------------------------------------------------------------- the Commons lane

def code_objects(code):
    """A function's code and the code of every function or lambda written inside it."""
    yield code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from code_objects(const)


def reads_commons(fn, seen=None):
    """True when the function, or any function of the pack files it calls (followed through their names), uses one
    of the COMMONS_HELPERS."""
    seen = set() if seen is None else seen
    if id(fn) in seen:
        return False
    seen.add(id(fn))
    names = fn.__globals__
    for code in code_objects(fn.__code__):
        for name in code.co_names:
            if name in COMMONS_HELPERS:
                return True
            called = names.get(name)
            if isinstance(called, types.FunctionType) and called.__code__.co_filename.startswith(
                    os.path.dirname(build_packs.__file__)) and reads_commons(called, seen):
                return True
    return False


def test_commons_keys_are_packs():
    """Every key in COMMONS_KEYS is a pack (no misspelt or removed key)."""
    assert build_packs.COMMONS_KEYS <= set(build_packs.PACKS), build_packs.COMMONS_KEYS - set(build_packs.PACKS)


def test_every_commons_named_pack_is_in_the_lane():
    """Every pack named commons_..., or work_/farm_/mech_/med_/vet_commons_..., is in COMMONS_KEYS."""
    named = {k for k in build_packs.PACKS if k.startswith("commons_") or "_commons_" in k}
    assert named <= build_packs.COMMONS_KEYS, sorted(named - build_packs.COMMONS_KEYS)


def test_every_builder_that_reads_commons_is_in_the_lane():
    """Every pack whose builder calls a Commons helper is in COMMONS_KEYS (a new Commons pack must be added there)."""
    found = {k for k, (builder, *_) in build_packs.PACKS.items()
             if isinstance(builder, types.FunctionType) and reads_commons(builder)}
    assert found, "the scan found no Commons packs at all: it is broken"
    assert found <= build_packs.COMMONS_KEYS, sorted(found - build_packs.COMMONS_KEYS)
    # Packs known to read Commons through helpers named differently are in the lane too.
    for key in ("us_road_signs", "ca_road_signs", "wikidata_devices", "commons", "commons_valued",
                "commons_college_streams", "commons_university_archives", "commons_state_roads", "farm_usda_nrcs"):
        assert key in build_packs.COMMONS_KEYS, key


def test_pack_lanes_keeps_marks_and_order():
    """Top-up ("+") and needs-only ("?") keys go to the lane of their pack, with their mark, in the order given."""
    commons, other = build_packs.pack_lanes(
        ["loc_fsa", "commons_disasters", "us_road_signs+", "field_manual_figures?", "commons_war?", "owid_charts+",
         "wikidata_devices"])
    assert commons == ["commons_disasters", "us_road_signs+", "commons_war?", "wikidata_devices"]
    assert other == ["loc_fsa", "field_manual_figures?", "owid_charts+"]
    assert build_packs.pack_lanes([]) == ([], [])


def plan_python():
    """The Python of packs.yml's plan step (the text between <<'PY' and PY), as the runner gives it to python3."""
    import yaml
    with open(os.path.join(WORKFLOWS, "packs.yml"), encoding="utf-8") as f:
        workflow = yaml.safe_load(f)
    run = next(step["run"] for step in workflow["jobs"]["plan"]["steps"] if step.get("id") == "keys")
    return re.search(r"<<'PY'\n(.*?)\nPY\b", run, re.S).group(1)


def run_plan(keys):
    """The plan step's GITHUB_OUTPUT lines for the keys text, as {name: JSON value}."""
    done = subprocess.run([sys.executable, "-", keys], input=plan_python(), capture_output=True, text=True,
                          cwd=REPO, check=True)
    out = {}
    for line in done.stdout.splitlines():
        name, _, value = line.partition("=")
        out[name] = json.loads(value)
    return out


def test_plan_step_prints_the_two_lanes():
    """The plan step prints keys, commons and other, and nothing else, so GITHUB_OUTPUT gets exactly three lines."""
    out = run_plan("commons_disasters,loc_fsa+,commons_us_eating_out?,field_manual_figures,not_a_pack")
    assert set(out) == {"keys", "commons", "other"}
    assert out["keys"] == ["commons_disasters", "loc_fsa+", "commons_us_eating_out?", "field_manual_figures"]
    assert out["commons"] == ["commons_disasters", "commons_us_eating_out?"]
    assert out["other"] == ["loc_fsa+", "field_manual_figures"]
    everything = run_plan("all")
    assert sorted(everything["commons"] + everything["other"]) == sorted(everything["keys"])
    assert set(k for k in everything["keys"] if k.startswith("commons_")) <= set(everything["commons"])


def test_the_workflows_call_the_lanes():
    """packs.yml calls pack-build.yml twice (eight at a time and the Commons lane two at a time), and the manifest
    jobs wait for both, whatever happened to them."""
    import yaml
    with open(os.path.join(WORKFLOWS, "packs.yml"), encoding="utf-8") as f:
        packs = yaml.safe_load(f)
    with open(os.path.join(WORKFLOWS, "pack-build.yml"), encoding="utf-8") as f:
        lane = yaml.safe_load(f)
    jobs = packs["jobs"]
    assert jobs["build"]["uses"] == jobs["build-commons"]["uses"] == "./.github/workflows/pack-build.yml"
    assert jobs["build"]["with"] == {"keys": "${{ needs.plan.outputs.other }}", "parallel": 8}
    assert jobs["build-commons"]["with"] == {"keys": "${{ needs.plan.outputs.commons }}", "parallel": 2}
    assert jobs["build"]["secrets"] == jobs["build-commons"]["secrets"] == "inherit"
    for name in ("manifest", "needs-manifest"):
        assert jobs[name]["needs"] == ["build", "build-commons"] and jobs[name]["if"] == "always()"
    assert packs["concurrency"] == {"group": "training-packs", "cancel-in-progress": False}
    # (PyYAML reads the key "on" as True.)
    assert set(lane[True]["workflow_call"]["inputs"]) == {"keys", "parallel"}
    build = lane["jobs"]["build"]
    assert build["strategy"]["max-parallel"] == "${{ inputs.parallel }}"
    assert build["env"]["EUROPEANA_KEY"] == "${{ secrets.EUROPEANA_KEY }}"
    assert build["env"]["DPLA_API_KEY"] == "${{ secrets.DPLA_API_KEY }}"
    assert [s.get("name") for s in build["steps"]][-1] == "Upload the pictures that need a description"


# ----------------------------------------------------------------- dropped connections

class FlakyAdapter(requests.adapters.HTTPAdapter):
    """A made-up web: START redirects to FILE (as archive.org sends a download on to a file server); the first
    `drops` requests for FILE fail with the given error, later ones answer the picture."""

    START, FILE = "https://archive.example/download/manual.pdf", "https://dn1.archive.example/manual.pdf"

    def __init__(self, drops, error, body=b"%PDF-1.4 made up"):
        super().__init__()
        self.drops, self.error, self.body, self.asked = drops, error, body, []

    def send(self, request, **kwargs):
        """Answer one request from the made-up web."""
        self.asked.append(request.url)
        r = requests.Response()
        r.request, r.url, r.raw = request, request.url, io.BytesIO(b"")
        if request.url == self.START:
            r.status_code, r.headers["Location"], r._content = 302, self.FILE, b""
        elif self.drops > 0:
            self.drops -= 1
            raise self.error("EOF occurred in violation of protocol (_ssl.c:2427)")
        else:
            r.status_code, r._content = 200, self.body
        return r


def no_waiting(monkeypatch):
    """Make the retry pauses instant for the test, and return the list of pauses asked for."""
    waits = []
    monkeypatch.setattr(build_packs.time, "sleep", waits.append)
    return waits


def test_session_tries_a_dropped_redirect_again(monkeypatch):
    """An SSL drop on the server the download was redirected to is tried again, from the start, and comes."""
    waits = no_waiting(monkeypatch)
    s = build_packs.session()
    web = FlakyAdapter(2, requests.exceptions.SSLError)
    s.mount("https://", web)
    r = s.get(web.START, timeout=5)
    assert r.status_code == 200 and r.content == web.body
    assert web.asked == [web.START, web.FILE] * 3
    assert waits == list(build_packs.TRANSIENT_WAITS[:2])


def test_session_gives_up_after_its_tries(monkeypatch):
    """A connection that keeps dropping fails after the session's tries (the caller decides what to do)."""
    no_waiting(monkeypatch)
    s = build_packs.session(transient_tries=3)
    web = FlakyAdapter(10, requests.exceptions.ChunkedEncodingError)
    s.mount("https://", web)
    try:
        s.get(web.FILE, timeout=5)
    except requests.exceptions.ChunkedEncodingError:
        pass
    else:
        raise AssertionError("the third drop should have failed the request")
    assert web.asked == [web.FILE] * 3


def test_session_does_not_retry_other_errors(monkeypatch):
    """An error that is not a dropped connection (here a bad address) is not tried again."""
    no_waiting(monkeypatch)
    s = build_packs.session()
    web = FlakyAdapter(1, requests.exceptions.InvalidURL)
    s.mount("https://", web)
    try:
        s.get(web.FILE, timeout=5)
    except requests.exceptions.InvalidURL:
        pass
    assert web.asked == [web.FILE]


def test_fetch_all_survives_one_dropped_connection(monkeypatch):
    """fetch_all keeps a picture whose first download was dropped (ReadTimeout on the redirected server)."""
    from PIL import Image
    no_waiting(monkeypatch)
    picture = io.BytesIO()
    Image.new("RGB", (80, 80), (200, 30, 30)).save(picture, "JPEG")
    web = FlakyAdapter(1, requests.exceptions.ReadTimeout, body=picture.getvalue())
    made = build_packs.session

    def session_with_the_made_up_web(*args, **kwargs):
        """build_packs.session, talking to the made-up web."""
        s = made(*args, **kwargs)
        s.mount("https://", web)
        return s

    monkeypatch.setattr(build_packs, "session", session_with_the_made_up_web)
    got = build_packs.fetch_all([("one.jpg", web.START, {"question": "q", "answer": "a"})], workers=1)
    assert [name for name, _, _ in got] == ["one.jpg"]


def test_commons_pace_spaces_requests(monkeypatch):
    """Two Commons requests in a row are at least COMMONS_PAUSE seconds apart."""
    waits = no_waiting(monkeypatch)
    now = [1000.0]
    monkeypatch.setattr(build_packs.time, "time", lambda: now[0])
    build_packs._COMMONS_LAST[0] = 0.0
    build_packs.commons_pace()               # the first request of the build: no wait
    now[0] += 0.25
    build_packs.commons_pace()               # a quarter of a second later: waits the rest of the pause
    assert waits == [build_packs.COMMONS_PAUSE - 0.25]
