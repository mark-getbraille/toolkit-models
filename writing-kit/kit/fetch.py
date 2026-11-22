"""Polite downloading for the Writing Kit: every request goes through here.

What it does, in plain words:
  - reads each site's robots.txt once and obeys it: a page that robots.txt closes to programs is never fetched;
  - refuses a whole site for this kit when its robots.txt says it does not want AI training: a "Content-Signal" line
    with "ai-train=no", or a block on the general AI-training crawlers (GPTBot, ClaudeBot, CCBot, Google-Extended
    and the like) for the address we want. A block on only some companies' crawlers (for example Meta's or
    ByteDance's) is not a refusal by itself, but it is written down as a warning in the build report, so the owner
    can decide;
  - waits between requests to the same site: the robots.txt "Crawl-delay" when it gives one, otherwise
    DEFAULT_DELAY seconds;
  - tries a few times on a network error, waiting longer each time;
  - sends a plain name for the kit (USER_AGENT), never any personal details.

Nothing here keeps cookies, logs in, or uses keys. Only official addresses are ever used (each reader decides which).
"""

import hashlib
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

USER_AGENT = "WritingKit/1 (https://github.com/mark-getbraille/toolkit-models)"
DEFAULT_DELAY = 3.0          # seconds between two requests to the same site when its robots.txt names no delay

# The crawlers that AI companies use to collect training text in general. A site that closes the address we want to
# any of these is taken to say "no AI training", and the kit leaves it out.
AI_TRAINING_AGENTS = ["GPTBot", "ClaudeBot", "anthropic-ai", "Claude-Web", "CCBot", "Google-Extended",
                      "Applebot-Extended", "cohere-ai", "cohere-training-data-crawler", "MistralAI-Training",
                      "AI2Bot", "Omgilibot", "PerplexityBot"]
# Crawlers of single companies: a block on these alone is only a warning (sites often block them for heavy crawling).
COMPANY_AI_AGENTS = ["meta-externalagent", "FacebookBot", "Bytespider", "Amazonbot", "Diffbot", "ImagesiftBot"]


class RobotsRefusal(Exception):
    """Raised when robots.txt (or its AI-training signals) does not allow the kit to use an address."""


def parse_content_signals(text):
    """The "Content-Signal" values of a robots.txt that apply to every crawler ("User-agent: *"), as a dict such as
    {"search": "yes", "ai-train": "no"}. Lines in other User-agent groups are ignored."""
    signals, agents, in_rules = {}, [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            if in_rules:                       # a new group starts after rules
                agents, in_rules = [], False
            agents.append(value)
        else:
            in_rules = True
            if field == "content-signal" and ("*" in agents or not agents):
                for pair in value.split(","):
                    if "=" in pair:
                        key, val = (p.strip().lower() for p in pair.split("=", 1))
                        signals[key] = val
    return signals


def group_rules(text, agent):
    """[(allow, pattern)] of the robots.txt group that applies to agent (its own group if it has one, otherwise the
    "*" group)."""
    groups, agents, rules, in_rules = [], [], [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            if in_rules:
                groups.append((agents, rules))
                agents, rules, in_rules = [], [], False
            agents.append(value.lower())
        elif field in ("allow", "disallow"):
            in_rules = True
            if value or field == "allow":
                rules.append((field == "allow", value))
    if agents:
        groups.append((agents, rules))
    name = agent.split("/")[0].lower()
    mine = [r for a, r in groups if any(x != "*" and x in agent.lower() for x in a) or name in a]
    if mine:
        return [rule for r in mine for rule in r]
    return [rule for a, r in groups if "*" in a for rule in r]


def wildcard_allowed(rules, path):
    """RFC 9309 matching with "*" and "$": the longest matching rule wins; Allow wins a tie; no match allows."""
    best = None
    for allow, pattern in rules:
        regex = "^" + re.escape(pattern).replace(r"\*", ".*")
        regex = regex[:-2] + "$" if regex.endswith(r"\$") else regex
        if re.match(regex, path):
            key = (len(pattern), allow)
            if best is None or key > best:
                best = key
    return True if best is None else best[1]


class Robots:
    """One site's robots.txt: whether an address may be fetched, the wait between requests, and the AI signals."""

    def __init__(self, site, text):
        self.site = site
        self.text = text or ""
        self.parser = urllib.robotparser.RobotFileParser()
        self.parser.parse(self.text.splitlines())
        self.signals = parse_content_signals(self.text)
        delay = self.parser.crawl_delay(USER_AGENT) or self.parser.crawl_delay("*")
        self.delay = float(delay) if delay else DEFAULT_DELAY

    def check(self, url):
        """(allowed, reason, warnings) for url. allowed is False when robots.txt closes url to the kit, says
        ai-train=no, or closes url to a general AI-training crawler. warnings lists company-crawler blocks."""
        if self.signals.get("ai-train") == "no":
            return False, f"{self.site}/robots.txt says 'Content-Signal: ai-train=no'", []
        parts = urllib.parse.urlsplit(url)
        path = (parts.path or "/") + ("?" + parts.query if parts.query else "")
        if not self.parser.can_fetch(USER_AGENT, url) or \
                not wildcard_allowed(group_rules(self.text, USER_AGENT), path):
            return False, f"{self.site}/robots.txt does not allow programs to read {url}", []
        blocked = [a for a in AI_TRAINING_AGENTS if not self.parser.can_fetch(a, url)]
        if blocked:
            return False, f"{self.site}/robots.txt blocks AI-training crawlers ({', '.join(blocked)})", []
        warnings = [a for a in COMPANY_AI_AGENTS if not self.parser.can_fetch(a, url)]
        if warnings:
            warnings = [f"{self.site}/robots.txt blocks some single companies' AI crawlers ({', '.join(warnings)}); "
                        "it does not block AI-training crawlers in general or this kit"]
        return True, "", warnings


class Fetcher:
    """Fetches addresses politely (see the module notes). One Fetcher is used for a whole build, so each robots.txt
    is read once and the waits are kept per site. say(text) receives progress lines."""

    def __init__(self, say=print, opener=None, cache_dir=None):
        self.say = say
        self.cache_dir = cache_dir
        self.robots = {}
        self.last = {}
        self.warnings = []
        self.extra_headers = {}          # for example EDGAR's declared user agent, from the computer's settings
        self.opener = opener or urllib.request.build_opener()

    def _site(self, url):
        parts = urllib.parse.urlsplit(url)
        return f"{parts.scheme}://{parts.netloc}"

    def robots_for(self, url):
        """The Robots of url's site, reading robots.txt the first time. As RFC 9309 says, a robots.txt that answers
        with a 4xx error (not found, forbidden) sets no rules; one that cannot be reached, or answers with a server
        error, closes the site."""
        site = self._site(url)
        if site not in self.robots:
            try:
                text = self._get(site + "/robots.txt", site, check=False).decode("utf-8", "replace")
            except urllib.error.HTTPError as err:
                # RFC 9309: a robots.txt that is "unavailable" (4xx) means no rules; an unreachable one (5xx)
                # means stay away.
                text = "" if 400 <= err.code < 500 else "User-agent: *\nDisallow: /\n"
            except (urllib.error.URLError, OSError):
                text = "User-agent: *\nDisallow: /\n"
            self.robots[site] = Robots(site, text)
        return self.robots[site]

    def check(self, url):
        """Raise RobotsRefusal when url may not be used; remember any warning."""
        allowed, reason, warnings = self.robots_for(url).check(url)
        if not allowed:
            raise RobotsRefusal(reason)
        for w in warnings:
            if w not in self.warnings:
                self.warnings.append(w)
                self.say("Note: " + w)

    def _wait(self, site, delay):
        gap = time.time() - self.last.get(site, 0)
        if gap < delay:
            time.sleep(delay - gap)
        self.last[site] = time.time()

    def _get(self, url, site, check=True, stream=False, tries=3):
        delay = self.robots[site].delay if site in self.robots else DEFAULT_DELAY
        for attempt in range(tries):
            self._wait(site, delay)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **self.extra_headers})
                resp = self.opener.open(req, timeout=60)
                return resp if stream else resp.read()
            except urllib.error.HTTPError as err:
                if err.code in (404, 410, 403, 401) or attempt == tries - 1:
                    raise
            except (urllib.error.URLError, OSError):
                if attempt == tries - 1:
                    raise
            time.sleep(10 * (attempt + 1))

    def get(self, url):
        """The bytes at url, after the robots.txt checks and the wait. With a cache folder, a page fetched before is
        read from there instead (robots.txt is still checked), so a rebuild does not ask the site again."""
        self.check(url)
        path = None
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            path = os.path.join(self.cache_dir, hashlib.sha1(url.encode("utf-8")).hexdigest())
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read()
        data = self._get(url, self._site(url))
        if path:
            with open(path + ".part", "wb") as f:
                f.write(data)
            os.replace(path + ".part", path)
        return data

    def open_stream(self, url):
        """An open response for url (for large official files read as they arrive), after the same checks."""
        self.check(url)
        return self._get(url, self._site(url), stream=True)

    def download(self, url, dest, size=None, sha256=None, say=None, chunk=1 << 20, tries=6,
                 report_every=250_000_000, sleep=time.sleep):
        """Save the file at url as dest, resuming where an earlier try stopped. Returns "already" when dest is
        already complete, otherwise "downloaded".

        How it works, in plain words: the bytes go into dest + ".part". If that file is already there (a download
        that was stopped or cut off), the kit asks the site only for the rest (an HTTP "Range" request) and adds it
        to the end; a site that sends the whole file again instead is written from the start. When size is given
        the download is complete only at exactly that many bytes; when sha256 is given the finished file must also
        have that checksum, or it is deleted and an error raised. Only then is ".part" renamed to dest. A line goes
        to say every report_every bytes. Network errors are retried (tries times, waiting longer each time); robots.txt
        is obeyed as for every other request."""
        say = say or self.say
        if os.path.exists(dest) and (size is None or os.path.getsize(dest) == size):
            return "already"
        self.check(url)
        part, site = dest + ".part", self._site(url)
        delay = self.robots[site].delay if site in self.robots else DEFAULT_DELAY
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        for attempt in range(tries):
            have = os.path.getsize(part) if os.path.exists(part) else 0
            if size is not None and have > size:          # longer than the file can be: start again
                os.remove(part)
                have = 0
            if size is not None and have == size:
                break
            headers = {"User-Agent": USER_AGENT, **self.extra_headers}
            if have:
                headers["Range"] = f"bytes={have}-"
            self._wait(site, delay)
            try:
                resp = self.opener.open(urllib.request.Request(url, headers=headers), timeout=60)
                status = getattr(resp, "status", None) or resp.getcode()
                if have and status != 206:                # the site ignored the Range request: start again
                    have = 0
                if have:
                    say(f"  resuming at {have / 1e9:.2f} GB")
                next_report = (have // report_every + 1) * report_every
                with open(part, "ab" if have else "wb") as f:
                    while True:
                        block = resp.read(chunk)
                        if not block:
                            break
                        f.write(block)
                        have += len(block)
                        if have >= next_report:
                            total = f" of {size / 1e9:.2f} GB ({100 * have // size}%)" if size else " GB"
                            say(f"  {have / 1e9:.2f}{total}")
                            next_report += report_every
                resp.close()
                if size is None or have >= size:
                    break
            except urllib.error.HTTPError as err:
                if err.code == 416 and size is not None and have == size:
                    break
                if err.code == 416:                       # the part file does not fit the file any more
                    os.remove(part)
                elif err.code in (404, 410, 403, 401) or attempt == tries - 1:
                    raise
            except (urllib.error.URLError, OSError):
                if attempt == tries - 1:
                    raise
            if attempt < tries - 1:
                sleep(10 * (attempt + 1))
        got = os.path.getsize(part) if os.path.exists(part) else 0
        if size is not None and got != size:
            raise OSError(f"{url}: only {got} of {size} bytes arrived; run again to resume")
        if sha256:
            digest = hashlib.sha256()
            with open(part, "rb") as f:
                for block in iter(lambda: f.read(1 << 20), b""):
                    digest.update(block)
            if digest.hexdigest() != sha256.lower():
                os.remove(part)
                raise ValueError(f"{url}: the downloaded file's checksum does not match; it was deleted, run again")
        os.replace(part, dest)
        return "downloaded"
