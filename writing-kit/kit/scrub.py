"""Privacy scrubbing and choosing good examples for the Writing Kit. Every message from every source goes through
clean_message() before it can become a training example. SCRUBBING.txt (in the kit's main folder) explains the same
rules in plain words for the owner.

The steps, in order:
  1. Keep only the writer's own words: quoted earlier messages ("> ...", "-----Original Message-----", "On ...
     wrote:", forwarded blocks) and footers ("Sent from my iPhone", disclaimers) are cut off (own_words()).
  2. Drop the whole message if it touches a sensitive subject (sensitive_reason()): health and medical matters,
     family and personal life, money trouble, HR, jobs and disciplinary matters, anything sexual, anything about
     children, passwords and confidential or legal matters, crime and police.
  3. Replace personal details with placeholders (scrub_text()): email addresses, web addresses, phone numbers,
     Social Security and other ID numbers, card and account numbers, dates of birth, street addresses and postcodes,
     IP addresses and long numbers.
  4. Replace people's names with placeholders: [Name], [Name 2] ... for people named in the message, and [Your name]
     for the writer's own sign-off. Names are found from the message's own headers (From, To, Cc), from greetings
     ("Hi Pat,"), from titles ("Ms. Lopez"), from sign-offs and from a list of common first names (names.py). Public
     officials are not treated differently: everyone gets a placeholder.
  5. Keep only short, workaday messages that read well (quality_reason()): about 12 to 200 words, ordinary English
     sentences, not a table or a list of numbers, not an automatic message or newsletter, and not so full of
     placeholders that it no longer reads as a message.

Attachments are never read: the readers pass only the message's own text here.
"""

import re

from names import (AMBIGUOUS, COMMON_WORDS, EXTRA_PUBLIC, FIRST_NAMES, MONTHLIKE, PUBLIC_NAMES, SURNAMES,
                   TITLES)

# ----------------------------------------------------------------- 1. the writer's own words

QUOTE_MARKERS = [
    r"^-{2,}\s*Original Message\s*-{2,}",
    r"^-{2,}\s*Forwarded by",
    r"^-{3,}\s*Forwarded message",
    r"^Begin forwarded message",
    r"^On .{4,200}wrote:\s*$",
    r"^On .{4,120}$\n^.{0,120}wrote:\s*$",
    r"^.{1,80} wrote:\s*$",
    r"^From:\s.*$\n^(Sent|Date|To):",
    r"^\s*From:\s.*\n\s*To:",
    r"^_{8,}\s*$",
    r"^\s*To:\s.*\n\s*cc:",
    r"^-{5,}\s*$",
    r"\bFrom:\s.{0,80}<[^>\n]*@",            # a quoted header in the middle of a line
    r"^.{0,60}\bFrom:\s.*\n.*\b(To|Sent|Date|cc):",
]
FOOTER_MARKERS = [
    r"^Sent from my \w+", r"^Get Outlook for", r"^Please consider the environment",
    r"^This (e-?mail|message)( and any attachments)? (is|are|may be) (confidential|intended)",
    r"^\*{5,}", r"^={5,}", r"^-- ?$",
    r"^.{0,40}Enron Capital & Trade Resources",       # left over from Enron's quoted headers
]


def own_words(body):
    """The writer's own part of body: everything before the first quoted message, forwarded block or footer, with
    lines starting ">" removed and spacing tidied."""
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    cut = len(text)
    for pattern in QUOTE_MARKERS + FOOTER_MARKERS:
        if pattern.startswith("^"):
            pattern = "^[ \t]*" + pattern[1:]          # the marker may be indented
        m = re.search(pattern, text, re.M | re.I)
        if m and m.start() < cut:
            cut = m.start()
    text = text[:cut]
    lines = [ln.strip() for ln in text.split("\n") if not ln.lstrip().startswith(">")]
    lines = [ln for ln in lines if not DATE_LINE.match(ln)]
    text = unwrap("\n".join(lines))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# A line that is only a date or time stamp left over from a mail program ("05/28/2001 05:30 PM").
DATE_LINE = re.compile(r"^(?=.*\d)\s*(\d{1,2}/\d{1,2}/\d{2,4})?\s*(\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM)?)?\s*$", re.I)


def unwrap(text):
    """Join lines that a mail program broke at about 70 to 80 characters back into paragraphs. A line is joined to
    the next when it is long (45 characters or more) and the next line is not empty, a list item or a sign-off."""
    lines = text.split("\n")
    out = []
    for line in lines:
        if out and len(out[-1]) >= 45 and line and not re.match(r"([-*\u2022]|\d+[.)])\s", line) \
                and not SIGN_OFF.match(line) and not re.match(r"\[Your name\]", line) \
                and not re.fullmatch(r"[A-Z][A-Za-z'.\-]*( [A-Z][A-Za-z'.\-]*){0,2}", line):
            out[-1] = out[-1] + " " + line
        else:
            out.append(line)
    return "\n".join(out)


# ----------------------------------------------------------------- 2. sensitive subjects (the message is dropped)

def _words(*items):
    return re.compile(r"\b(" + "|".join(items) + r")\b", re.I)


SENSITIVE = {
    "health or medical": _words(
        r"doctors?", r"hospital\w*", r"surgery", r"surgeon", r"cancer", r"tumou?r", r"chemo\w*", r"diagnos\w*",
        r"illness", r"sick(ness)?", r"flu", r"medications?", r"medicines?", r"prescriptions?", r"therap(y|ist|ies)",
        r"pregnan\w*", r"miscarriage", r"injur(y|ies|ed)", r"diseases?", r"diabet\w*", r"HIV", r"mental health",
        r"depress(ion|ed)", r"anxiety", r"rehab", r"clinic", r"symptoms?", r"MRI", r"blood", r"health (issue|problem|"
        r"condition|scare)s?", r"medical", r"dentist", r"ER visit", r"recover(y|ing)", r"my (disability|condition)",
        r"covid", r"virus", r"infection", r"allerg\w*", r"heart attack", r"stroke", r"sinus\w*", r"ill",
        r"physician", r"nurse", r"pharmac\w*", r"vaccin\w*", r"appointment with (the|my|a) (doc|dr)\w*"),
    "family or personal life": _words(
        r"divorc\w*", r"custody", r"funeral", r"passed away", r"died", r"death", r"wedding", r"marri(age|ed)",
        r"my (wife|husband|son|daughter|kids?|children|mother|father|mom|mum|dad|parents|brother|sister|family|"
        r"girlfriend|boyfriend|fianc\w*|partner|grandmother|grandfather|baby)", r"family emergency", r"girlfriend",
        r"boyfriend", r"fianc\w*", r"honeymoon", r"in-laws?", r"memorial", r"condolences?", r"sympathy",
        r"(mom|dad|mum|mommy|daddy|grandpa|grandma|granny|aunt|uncle|cousin|nephew|niece|stepson|stepdaughter)s?",
        r"adopt\w*", r"home ?study", r"hubby", r"wife", r"husband", r"spouse", r"pregnan\w*", r"birth",
        r"miss you", r"love you", r"xoxo", r"hugs", r"sweetheart", r"honey", r"darling", r"babe", r"dating",
        r"date night", r"cute", r"in love", r"crush", r"chicks?", r"girls", r"partying", r"partied", r"shenanigans",
        r"hook(ed)? up", r"exes", r"my ex"),
    "money trouble": _words(
        r"debts?", r"bankrupt\w*", r"foreclos\w*", r"loans?", r"mortgage", r"evict\w*", r"can'?t afford",
        r"cannot afford", r"unemploy\w*", r"salary", r"salaries", r"paychecks?", r"payroll", r"garnish\w*",
        r"credit score", r"overdue", r"broke", r"in the red", r"collections? agency", r"owes?", r"owed"),
    "HR, jobs or discipline": _words(
        r"performance review", r"PRC", r"fired", r"firing", r"terminat\w*", r"lay-?offs?", r"laid off",
        r"resign\w*", r"disciplin\w*", r"harass\w*", r"grievance", r"misconduct", r"investigat\w*", r"lawsuits?",
        r"sue", r"suing", r"attorneys?", r"lawyers?", r"severance", r"probation", r"HR", r"human resources",
        r"bonus(es)?", r"compensation", r"offer letter", r"interview\w*", r"resume", r"résumé",
        r"job (offer|search|application)", r"hiring", r"promotion", r"demot\w*", r"reprimand\w*", r"written warning",
        r"separation agreement", r"retention", r"pension", r"401\(?k\)?", r"benefits enrollment", r"candidates?",
        r"job (openings?|opportunit\w*)", r"recruit\w*", r"headhunter", r"job references?", r"as a reference", r"separations?",
        r"waivers?", r"pay ?stubs?", r"visas?", r"immigration", r"green card", r"background check"),
    "sexual content": _words(
        r"sex\w*", r"nude\w*", r"naked", r"porn\w*", r"erotic\w*", r"condoms?", r"intimate", r"affair",
        r"lingerie", r"strip club", r"breasts?", r"orgasm\w*", r"horny", r"xxx", r"escort", r"hooker", r"kiss(es|ing)?"),
    "children": _words(
        r"child", r"children", r"kids?", r"teens?", r"teenagers?", r"juvenile", r"minors", r"daughters?", r"sons?",
        r"babies", r"baby", r"infants?", r"toddlers?", r"daycare", r"pre-?school", r"kindergarten", r"school",
        r"homework", r"playdate", r"babysit\w*"),
    "passwords, confidential or legal": _words(
        r"passwords?", r"passcodes?", r"PIN", r"SSN", r"social security", r"privileged", r"confidential",
        r"attorney-client", r"do not forward", r"log-?in details", r"usernames?", r"subpoena\w*", r"litigation",
        r"settlement", r"deposition", r"indict\w*", r"testimony", r"court ?house", r"courts?", r"mediation",
        r"TRO", r"sub ?poena\w*", r"complaint against", r"filed a complaint", r"plaintiff", r"defendant",
        r"jury", r"filing a complaint", r"violen\w*", r"threats?", r"threaten\w*"),
    "crime or police": _words(
        r"police", r"arrest\w*", r"jail", r"prison", r"crime", r"criminal", r"drugs?", r"stolen", r"theft",
        r"assault\w*", r"DUI", r"court date", r"fraud\w*", r"weapons?", r"guns?", r"shotguns?", r"rifles?",
        r"pistols?", r"firearms?", r"ammo", r"ammunition"),
    "gambling, drinking or partying": _words(
        r"gambl\w*", r"bets?", r"betting", r"wager\w*", r"bookie", r"casino", r"poker", r"drunk", r"hangover",
        r"wasted", r"booze", r"shots", r"bar tab", r"keg"),
    "swearing or insults": _words(
        r"fuck\w*", r"shit\w*", r"bitch\w*", r"ass", r"asses", r"asshole\w*", r"bastard\w*", r"damn\w*", r"crap",
        r"piss\w*", r"dick", r"cock", r"suck(s|ed)?", r"stupid", r"idiots?", r"moron\w*", r"hell", r"stinks?",
        r"psycho", r"retard\w*", r"screw(ed)?", r"whore\w*", r"slut\w*", r"coon"),
    "personal banking": _words(
        r"checking account", r"savings account", r"bank account", r"credit cards?", r"direct deposit",
        r"debit card", r"wire transfer", r"401k", r"ira account", r"tax return", r"taxes"),
}


def sensitive_reason(text):
    """The name of the first sensitive subject text touches ("health or medical" ...), or "" when none."""
    for name, pattern in SENSITIVE.items():
        if pattern.search(text):
            return name
    return ""


# ----------------------------------------------------------------- 3. personal details -> placeholders

STREET_WORDS = (r"Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl|Parkway|Pkwy|"
                r"Circle|Cir|Highway|Hwy|Terrace|Trail|Square|Sq|Loop|Freeway|Fwy")

DETAIL_PATTERNS = [
    # (placeholder, pattern). Order matters: the more specific ones first.
    ("[email address]", re.compile(r"[\w.+\-']+@[\w\-]+(\.[\w\-]+)+")),
    ("[email address]", re.compile(r"\b[\w .\-]{2,40}/(?:[A-Z]{2,}/)*[A-Z]{2,}@[A-Za-z]{2,}\b")),   # Lotus Notes
    ("[link]", re.compile(r"(https?://|ftp://|www\.)[^\s<>\"')\]]+", re.I)),
    ("[date of birth]", re.compile(
        r"\b(DOB|D\.O\.B\.?|date of birth|birth ?date|born on|born)\b[:\s]*"
        r"(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|[A-Z][a-z]+\.? \d{1,2},? \d{4}|\d{1,2} [A-Z][a-z]+ \d{4}|\d{4})", re.I)),
    ("[ID number]", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("[card number]", re.compile(r"\b(?:\d{4}[ -]){3}\d{1,7}\b")),
    ("[account number]", re.compile(
        r"(?<=\b)(?:account|acct|a/c|policy|member|customer|routing|employee|badge|licen[cs]e|passport|"
        r"confirmation|order|invoice|ticket|case|reference|ref|tag|deal)\s*(?:no\.?|number|num\.?|#)?(?:\s+is)?\s*[:#]?\s*"
        r"(?=[A-Z0-9\-]*\d)[A-Z0-9][A-Z0-9\-]{3,}", re.I)),
    ("[phone number]", re.compile(r"\+\d{1,3}[\s.\-]?\(?\d{1,4}\)?(?:[\s.\-]?\d{2,4}){2,4}\b")),
    ("[phone number]", re.compile(
        r"(?:\b1[\s.\-])?(?:\(\d{3}\)\s?|\b\d{3}[\s.\-])\d{3}[\s.\-]\d{4}\b(?:\s*(?:x|ext\.?|extension)\s*\d{1,6})?",
        re.I)),
    ("[phone number]", re.compile(r"\b(?:x|ext\.?|extension)\s*\d{3,6}\b", re.I)),
    ("[phone number]", re.compile(r"\b\d{3}-\d{4}\b")),
    ("[phone number]", re.compile(r"(?<![\d.\-/])\b\d-\d{4}\b(?![\-/]\d)")),        # internal extensions: 3-6731
    ("[street address]", re.compile(
        r"\b\d{1,6}\s+(?:[NSEW]\.?\s+)?(?:[A-Z][A-Za-z]+\.?\s+){1,4}(?:" + STREET_WORDS + r")\b\.?"
        r"(?:,?\s*(?:Suite|Ste|Apt|Unit|Floor|Fl|#)\.?\s*\w+)?")),
    ("[street address]", re.compile(r"\bP\.?\s?O\.?\s+Box\s+\d+\b", re.I)),
    ("[postcode]", re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b")),
    ("[postcode]", re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s+\d[A-Z]{2}\b")),
    ("[IP address]", re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")),
    ("[number]", re.compile(r"\b\d{6,}\b")),
]


def scrub_details(text):
    """text with every personal detail of DETAIL_PATTERNS replaced by its placeholder."""
    for placeholder, pattern in DETAIL_PATTERNS:
        text = pattern.sub(placeholder, text)
    return text


# ----------------------------------------------------------------- 4. names -> placeholders

HEADER_STOPWORDS = set("""
enron enronxgate ect hou corp com net org inc ltd llc co cc bcc na group team desk support mail email list lists
info admin office the and of for to all new houston london w3c www ees ena ene ews na-ent hotmail yahoo gmail aol
public lists archives dept department staff services service committee board members member re fw fwd notes user
""".split())
NOT_SURNAMES = set("""
monday tuesday wednesday thursday friday saturday sunday january february march april june july august september
october november december i i'm i'll i've i'd the and thanks thank please enron houston texas london we you
""".split())

GREETING = re.compile(r"^(?P<g>(?:hi|hello|hey|dear|good (?:morning|afternoon|evening)|morning|greetings|thanks|"
                      r"thank you|ok|okay)[ ,]+)(?P<n>[A-Za-z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)?)(?=\s*[,!.:\-\n]|$)",
                      re.I | re.M)
SIGN_OFF = re.compile(r"^\s*(thanks|thank you|thanks again|many thanks|thx|regards|best regards|kind regards|warm "
                      r"regards|best|best wishes|all the best|cheers|sincerely|yours|yours truly|take care|talk soon|"
                      r"see you|later|respectfully|with thanks|ciao)\b[ ,!.\-]*$", re.I)
TITLE_RE = r"(?:%s)\.?" % "|".join(TITLES)
# Words that are never names on their own (titles and forms of address).
NEVER_NAMES = {t.lower() for t in TITLES} | {"sir", "madam", "madame", "team", "all", "everyone", "hello", "hi",
                                            "dear", "folks", "guys", "colleagues", "friends", "whom"}
# "My name is ...", "I am ...", "This is ...": the capitalised words after it are a name when they are not ordinary
# words (this also catches short names such as "Bo" or "Ni").
INTRO = re.compile(r"\b(?i:my name is|i am|i'm|this is|myself|it's)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)")
# Words after which an ambiguous word at the start of a sentence ("Dawn has ...", "Bill said ...") is a name.
PERSON_VERBS = (r"\s+(has|had|is|was|will|would|said|says|wants|wanted|called|asked|told|thinks|thought|and|can|"
                r"could|should|needs|needed|mentioned|sent|just|also|wrote|agreed|knows)\b")
TOKEN = re.compile(r"\b(?:" + TITLE_RE + r"\s+)?[A-Z][A-Za-z'\-]+\b(?:\s+[A-Z]\.)?")


def names_from_headers(*values):
    """The set of lower-case name words found in header values (From, To, Cc ...) and in email addresses there
    ("pat.lopez@example.com" gives pat and lopez)."""
    found = set()
    for value in values:
        if not value:
            continue
        for local in re.findall(r"([\w.\-]+)@", value):
            for part in re.split(r"[._\-\d]+", local):
                if len(part) >= 3 and part.lower() not in HEADER_STOPWORDS:
                    found.add(part.lower())
        plain = re.sub(r"[\w.+\-]+@[\w.\-]+", " ", value)
        for part in re.findall(r"[A-Za-z][A-Za-z'\-]+", plain):
            if len(part) >= 2 and part.lower() not in HEADER_STOPWORDS:
                found.add(part.lower())
    return found


class NameScrubber:
    """Replaces the names in one message with [Name], [Name 2] ... (the same person keeps the same placeholder in
    the subject and the body) and the writer's sign-off with [Your name]."""

    def __init__(self, known=(), writer=()):
        self.known = {k.lower() for k in known}
        self.writer = {w.lower() for w in writer}
        self.mapping = {}

    def _placeholder(self, words):
        for w in words:
            if w in self.mapping:
                ph = self.mapping[w]
                break
        else:
            if words and all(w in self.writer for w in words) and self.writer:
                ph = "[Your name]"
            else:
                n = len({v for v in self.mapping.values() if v != "[Your name]"}) + 1
                ph = "[Name]" if n == 1 else f"[Name {n}]"
        for w in words:
            self.mapping.setdefault(w, ph)
        return ph

    def _is_name(self, word, initial=False, after=""):
        """True when word (a capitalised word) is taken to be a person's name. initial is True when it starts a
        sentence or a line, where ordinary words are capitalised too; after is the text that follows it."""
        if "-" in word.strip("-"):                    # "Zenger-Miller": a name if any part is one
            return any(self._is_name(part, initial, after) for part in word.split("-") if len(part) > 1)
        next_char = after[:1]
        base = re.sub(r"'s$", "", word.strip("'.")).strip("'")
        w = base.lower()
        if not w or w.startswith("i'") or w in NEVER_NAMES:
            return False
        if w in self.known or w in self.writer or w in self.mapping or w in FIRST_NAMES:
            return True
        if base in EXTRA_PUBLIC:
            return False
        if w in SURNAMES:
            return not (initial and w in COMMON_WORDS)
        if w in AMBIGUOUS:
            return w not in MONTHLIKE and (not initial or (next_char != "" and next_char in ",:")
                                           or re.match(PERSON_VERBS, after) is not None)
        if re.fullmatch(r"[A-Z][a-z]{2,}", base) and COMMON_WORDS:
            return w not in COMMON_WORDS and base not in PUBLIC_NAMES
        return False

    @staticmethod
    def _initial(text, start):
        """True when position start begins a sentence or a line."""
        return re.search(r"(^|[.!?:;]\s+|\n\s*|[\"(]\s*)$", text[max(0, start - 10):start] if start >= 10
                         else text[:start]) is not None

    def replace_names(self, text):
        """text with each run of name words replaced by its placeholder."""
        out, pos = [], 0
        tokens = list(TOKEN.finditer(text))
        i = 0
        while i < len(tokens):
            m = tokens[i]
            raw = m.group(0)
            titled = re.match(TITLE_RE + r"\s+", raw) is not None
            word = re.sub("^" + TITLE_RE + r"\s+", "", raw).split()[0]
            is_name = titled or self._is_name(word, self._initial(text, m.start()), text[m.end():m.end() + 30])
            if not is_name and word.lower() in AMBIGUOUS and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if text[m.end():nxt.start()].strip() == "" and self._is_name(nxt.group(0).split()[0]):
                    is_name = True
            if not is_name:
                i += 1
                continue
            run = [m]
            while i + len(run) < len(tokens):           # surnames and middle names right after it
                nxt = tokens[i + len(run)]
                if text[run[-1].end():nxt.start()] not in (" ", " -", "-") or \
                        re.match(TITLE_RE + r"\s", nxt.group(0)):
                    break
                nword = nxt.group(0).split()[0].lower()
                if nword in HEADER_STOPWORDS or nword in NOT_SURNAMES:
                    break
                run.append(nxt)
            words = []
            for r in run:
                words += [x.lower().strip(".") for x in re.sub("^" + TITLE_RE + r"\s+", "", r.group(0)).split()
                          if len(x.strip(".")) > 1]
            out.append(text[pos:run[0].start()])
            out.append(self._placeholder(words))
            pos = run[-1].end()
            i += len(run)
        out.append(text[pos:])
        return "".join(out)

    def introductions(self, text):
        """The name in "My name is ...", "I am ..." or "This is ..." becomes a placeholder (see INTRO)."""
        def fix(m):
            words = m.group(1).split()
            if words[0].lower() in COMMON_WORDS and len(words[0]) > 3 and not self._is_name(words[0]):
                return m.group(0)
            return m.group(0)[:m.start(1) - m.start(0)] + self._placeholder([w.lower() for w in words])
        return INTRO.sub(fix, text)

    def greetings(self, text):
        """The name after a greeting at the start of a line ("Hi Pat," "Dear Ms Lopez,") becomes a placeholder,
        even when it is not a known name or is written in small letters."""
        def fix(m):
            name = m.group("n")
            first = name.split()[0].lower()
            if first in ("all", "everyone", "team", "folks", "guys", "there", "again", "so", "much", "you", "for",
                         "both", "y'all", "everybody", "sir", "madam", "colleagues", "friends", "group", "to"):
                return m.group(0)
            if re.fullmatch(TITLE_RE, name.split()[0]):
                name_words = name.split()[1:]
            else:
                name_words = name.split()
            return m.group("g") + self._placeholder([w.lower() for w in name_words] or [first])
        return GREETING.sub(fix, text)

    def signature(self, text):
        """After a sign-off line ("Thanks," "Regards,"), a short name line becomes [Your name] and anything after it
        (job title, company, phone) is cut. A lone name on the last line becomes [Your name] too."""
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            if SIGN_OFF.match(line):
                rest = [ln for ln in lines[idx + 1:] if ln.strip()]
                if rest and len(rest[0].split()) <= 4:
                    return "\n".join(lines[:idx + 1] + ["[Your name]"])
                if not rest:
                    return "\n".join(lines[:idx + 1])
        # a signature block at the very end: up to five short lines without full stops (name, job title,
        # company, phone), at least one of them a name. The whole block becomes [Your name].
        while lines and not lines[-1].strip():
            lines.pop()
        block = 0
        while block < min(5, len(lines) - 1) and self._signature_line(lines[-1 - block]):
            block += 1
        if block:
            tail = lines[len(lines) - block:]
            if any(self._name_line(t) for t in tail):
                lines = lines[:len(lines) - block] + ["[Your name]"]
            elif all(re.fullmatch(r"\s*(\[[a-zA-Z ]+\]\s*)+", t) for t in tail):
                lines = lines[:len(lines) - block]          # only contact details left: drop them
        return "\n".join(lines)

    @staticmethod
    def _signature_line(line):
        """True for a short line that could belong to a signature block (no sentence end, six words at most)."""
        words = line.strip(" -").split()
        return 1 <= len(words) <= 6 and not re.search(r"[.!?:,]\s*$", line.strip()) or \
            re.fullmatch(r"\s*(\[[a-zA-Z ]+\]\s*)+", line) is not None

    def _name_line(self, line):
        """True for a line that is a name: one to three capitalised words or initials, or a name placeholder."""
        words = line.strip(" -").split()
        if not 1 <= len(words) <= 3:
            return False
        if any(w.startswith("[Name") or w == "[Your" for w in words):
            return True
        return all(re.fullmatch(r"[A-Z][A-Za-z'\-]*\.?", w) for w in words) and \
            (any(self._is_name(w.strip(".")) for w in words) or all(len(w) <= 3 for w in words))

    def scrub(self, text, signature=True):
        """All three name steps on text."""
        if signature:
            text = self.signature(text)
        text = self.greetings(text)
        text = self.introductions(text)
        text = self.replace_names(text)
        # "[Your name]" from the signature step may be followed by a name the step above replaced: tidy up
        text = re.sub(r"\[Your name\](\s*\[Name(?: \d+)?\])+", "[Your name]", text)
        return text


# ----------------------------------------------------------------- 5. quality

AUTOMATED = _words(r"unsubscribe", r"click here", r"view (this|it) in your browser", r"this message was sent",
                   r"newsletter", r"do not reply", r"no-?reply", r"auto-?reply", r"out of (the )?office",
                   r"automatically generated", r"mailing list", r"subscribe", r"you are receiving", r"privacy policy",
                   r"original message", r"forwarded message", r"forwarded by", r"lottery", r"winner", r"viagra")
COMMON = set("the a an and to of you i is for in it that on be will we this with have are me can my your at as "
             "if so not do please thanks let know would could just get about all".split())


def quality_reason(text, min_words=12, max_words=200):
    """Why text is not a good writing example ("too short" ...), or "" when it is fine."""
    words = re.findall(r"[A-Za-z']+|\[[^\]]+\]", text)
    if len(words) < min_words:
        return "too short"
    if len(words) > max_words:
        return "too long"
    if AUTOMATED.search(text):
        return "automatic message or newsletter"
    letters = sum(c.isalpha() for c in text)
    digits = sum(c.isdigit() for c in text)
    if letters == 0 or digits / (letters + digits) > 0.08:
        return "mostly numbers"
    upper = sum(c.isupper() for c in text)
    if upper / letters > 0.25:
        return "mostly capital letters"
    if sum(ord(c) < 128 for c in text) / len(text) < 0.98:
        return "not plain English text"
    plain = [w.lower() for w in words if not w.startswith("[")]
    if not plain or sum(w in COMMON for w in plain) / len(plain) < 0.18:
        return "not ordinary English sentences"
    placeholders = len(re.findall(r"\[[^\]]+\]", text.replace("[Your name]", "")))
    if placeholders / len(words) > 0.12 or placeholders > 8:
        return "too many removed details"
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if sum(1 for ln in lines if re.search(r"\t|\s{3,}|\|", ln)) > 1:
        return "looks like a table"
    if sum(1 for ln in lines if re.match(r"\s*([-*•]|\d+[.)])\s", ln)) > 4:
        return "mostly a list"
    starts = [s.lstrip("\"'([") for s in re.split(r"(?<=[.!?])\s+|\n+", text) if re.match(r"\W*[A-Za-z]", s)]
    if len(starts) >= 2 and sum(1 for s in starts if s[:1].isupper() or s.startswith("[")) / len(starts) < 0.6:
        return "careless capital letters"
    if not re.search(r"[.!?]", text):
        return "no full sentences"
    if re.search(r"\b(attached|attachment)\b", text, re.I) and len(words) < 25:
        return "only sends an attachment"
    return ""


# ----------------------------------------------------------------- the whole pipeline

def clean_message(subject, body, known_names=(), writer_names=(), min_words=12, max_words=200):
    """(cleaned, reason). cleaned is {"subject", "body"} with personal details and names replaced, or None with the
    reason the message was dropped ("sensitive: health or medical", "quality: too short" ...)."""
    own = own_words(body or "")
    subject = re.sub(r"\s+", " ", subject or "")
    subject = re.sub(r"^\s*((re|fw|fwd|aw)\s*:\s*|\[[^\]]{1,40}\]\s*)+", "", subject, flags=re.I).strip()
    for part in (subject, own):
        why = sensitive_reason(part)
        if why:
            return None, "sensitive: " + why
    names = NameScrubber(known_names, writer_names)
    text = scrub_details(own)
    text = names.scrub(text)
    subj = names.scrub(scrub_details(subject), signature=False)
    text = re.sub(r"\[(?:Name(?: \d+)?|Your name)\]@[A-Za-z.]+", "[email address]", text)
    text = re.sub(r"(\n\[Your name\])(\n.*)*\n\[Your name\]\s*$", r"\1", text)   # one sign-off is enough
    text = re.sub(r"[ \t]+\n", "\n", text).strip()
    why = quality_reason(text, min_words, max_words)
    if why:
        return None, "quality: " + why
    return {"subject": subj, "body": text}, ""
