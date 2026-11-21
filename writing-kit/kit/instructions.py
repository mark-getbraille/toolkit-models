"""Turning a cleaned message into a writing instruction, by simple rules (no AI, nothing online).

For each message the kit works out, from the message's own words:
  kind      what the message does: reply, thank-you note, request, scheduling, follow-up, declining, apology,
            complaint, announcement, confirmation, introduction, invitation or update (classify_kind());
  form      email, text message (very short, no greeting or sign-off) or memo (an announcement to a group);
  tone      friendly and casual, polite and professional, or firm (guess_tone());
  audience  a colleague, a team or group, an outside contact, or a public mailing list (from the source's details);
  length    very short, short or a few short paragraphs (from the word count).
It then fills a sentence template such as "Write a short, friendly reply to a colleague declining the meeting
politely." and adds the main point when a simple rule can find it in the message (what is asked for, what the thanks
is for) and the subject line when it says something useful. The same message always gets the same wording (the
template is chosen from a hash of the text), so a rebuild gives the same files.
"""

import hashlib
import re

KIND_RULES = [
    # (kind, pattern); the first that matches wins, so the more particular kinds come first.
    ("declining", r"\b(unfortunately|(won'?t|will not|can'?t|cannot|can not) (be able to )?(make|attend|join|come|do)|"
                  r"have to (decline|pass)|unable to (attend|make|join)|regrets\b|send(ing)? my regrets|"
                  r"not be able to (make|attend|join))"),
    ("apology", r"\b(sorry|apologi[sz]e|apologies|my mistake|my fault)\b"),
    ("complaint", r"\b(disappointed|not happy|unacceptable|frustrat\w*|still (haven't|have not|hasn't|not)|"
                  r"complain\w*|problem with your|poor service|this is the (second|third) time)\b"),
    ("thank-you note", r"^\W*(thanks|thank you|many thanks|thanks so much|thank you so much)\b(?! in advance)"),
    ("follow-up", r"\b(following up|follow(ing)? up on|just checking|checking in|any (update|news|word)|"
                  r"(friendly )?reminder|haven't heard|did you (get|have a chance)|circling back)\b"),
    ("introduction", r"\b(i'?d like to introduce|let me introduce|meet \[name|introducing|i am the new|i'm the new)\b"),
    ("invitation", r"\b(you are invited|you're invited|would (you )?like to (join|come)|join us|invite you|"
                   r"we'?d love (for you|to have you))\b"),
    ("scheduling", r"\b((set up|schedule|arrange|book|move|push) (a |the |our )?(meeting|call|time|lunch)|meeting|"
                   r"conference call|lunch|availability|are you (available|free)|schedul\w*|reschedul\w*|calendar|"
                   r"free (on|at|for)|does .{1,20} work for you|works for me|what time)\b"),
    ("announcement", r"\b(please (note|be advised)|announc\w*|effective (immediately|today|monday|tomorrow)|"
                     r"will be (closed|down|out|unavailable)|fyi|welcome (to|aboard)|we are pleased|"
                     r"i am pleased|happy to (announce|share)|starting (today|tomorrow|next))\b"),
    ("request", r"(\b(could|can|would|will) you\b|\bplease (send|let|call|review|forward|check|confirm|give|"
                r"get|provide|update|fax|add|take|look|make|do|see)\b|\bi need\b|\bcan i get\b|\bwould it be possible)"),
    ("confirmation", r"\b(confirm\w*|sounds good|will do|got it|that works|ok(ay)?,? (thanks|great)|"
                     r"no problem|all set|done\b)"),
]

TEMPLATES = {
    # Each kind has a few sentence patterns. {length} {tone} {form} {audience} {point} are filled in.
    "reply": ["Write a {length}, {tone} reply to {audience}{point}.",
              "Reply to {audience} in a {length}, {tone} {form}{point}.",
              "Draft a {length} {form} replying to {audience}{point}. Keep the tone {tone}."],
    "thank-you note": ["Write a {length}, {tone} thank-you {form} to {audience}{point}.",
                       "Thank {audience} in a {length}, {tone} {form}{point}."],
    "request": ["Write a {length}, {tone} {form} to {audience}{point}.",
                "Draft a {length} {form} to {audience}{point}. Keep it {tone}."],
    "scheduling": ["Write a {length}, {tone} {form} to {audience} about arranging a time{point}.",
                   "Draft a {length} {form} to {audience} to sort out a meeting or call{point}. Keep it {tone}."],
    "follow-up": ["Write a {length}, {tone} follow-up {form} to {audience}{point}.",
                  "Draft a {length} {form} following up with {audience}{point}. Keep it {tone}."],
    "declining": ["Write a {length}, {tone} {form} to {audience} politely saying no{point}.",
                  "Draft a {length} {form} to {audience} declining politely{point}. Keep it {tone}."],
    "apology": ["Write a {length}, {tone} {form} to {audience} apologising{point}.",
                "Draft a {length} apology {form} to {audience}{point}. Keep it {tone}."],
    "complaint": ["Write a {length}, {tone} {form} to {audience} raising a complaint{point}.",
                  "Draft a {length} complaint {form} to {audience}{point}. Keep it {tone}."],
    "announcement": ["Write a {length}, {tone} {form} announcing something to {audience}{point}.",
                     "Draft a {length} announcement {form} for {audience}{point}. Keep it {tone}."],
    "confirmation": ["Write a {length}, {tone} {form} to {audience} confirming{point}.",
                     "Draft a {length} {form} to {audience} to confirm{point}. Keep it {tone}."],
    "introduction": ["Write a {length}, {tone} {form} introducing yourself or someone to {audience}{point}."],
    "invitation": ["Write a {length}, {tone} {form} inviting {audience}{point}.",
                   "Draft a {length} invitation {form} to {audience}{point}. Keep it {tone}."],
    "update": ["Write a {length}, {tone} {form} to {audience} with a quick update{point}.",
               "Draft a {length} {form} to {audience} sharing information{point}. Keep it {tone}."],
}

GENERIC_SUBJECTS = {"", "hi", "hello", "hey", "question", "questions", "update", "fyi", "info", "thanks", "thank you",
                    "no subject", "(no subject)", "follow up", "follow-up", "meeting", "request", "test", "re", "help"}

SWAP = {"me": "you", "my": "your", "mine": "yours", "myself": "yourself", "i": "you", "i'm": "you're",
        "i'll": "you'll", "i've": "you've", "i'd": "you'd", "we": "you", "us": "you", "our": "your",
        "you": "them", "your": "their", "yours": "theirs", "yourself": "themselves", "you're": "they're",
        "you'll": "they'll", "you've": "they've", "am": "are"}


SUBJECT_VERBS = (r"know|can|have|are|will|would|need|want|get|think|see|could|should|may|might|do|did|were|had|"
                 r"find|like|hear|send|make")


def swap_person(clause):
    """A clause turned from the writer's point of view to the instruction's: "send me your notes" becomes "send you
    their notes" (I and me become you; you and your become them and their; "you" before a verb becomes "they")."""
    clause = re.sub(r"\byou (?=(" + SUBJECT_VERBS + r")\b)", "they ", clause, flags=re.I)
    def one(m):
        word = m.group(0)
        new = SWAP.get(word.lower(), word)
        return new
    return re.sub(r"[A-Za-z']+", one, clause)


def _sentences(text):
    body = re.sub(r"^\s*(hi|hello|hey|dear|good morning)[^\n]{0,40}\n", "", text, flags=re.I)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", body) if s.strip()]


def asking(clause):
    """" asking them to ..." for a request clause, with the small fixes plain English needs ("do not" becomes
    "not to", "wanna go" becomes "whether they would like to go")."""
    clause = swap_person(clause.strip())
    m = re.match(r"(?:wanna|want to|like to) (.+)", clause, re.I)
    if m:
        return " asking whether they would like to " + m.group(1)
    m = re.match(r"(?:do not|don't|dont) (.+)", clause, re.I)
    if m:
        return " asking them not to " + m.group(1)
    return " asking them to " + clause


def main_point(kind, text):
    """A few words saying what the message is for, from its own sentences ("asking them to send the updated
    figures"), or "" when no simple rule finds it."""
    for s in _sentences(text):
        low = s.rstrip(" .!?")
        m = re.search(r"\b(?:could|can|would|will) you (?:please )?(.{6,90})$", low, re.I)
        if m and kind in ("request", "reply", "follow-up", "scheduling", "invitation"):
            return asking(m.group(1))
        m = re.match(r"(?:please) (.{6,90})$", low, re.I)
        if m and kind in ("request", "reply", "follow-up", "announcement"):
            return asking(m.group(1))
        m = re.match(r"(?:thanks|thank you)(?: so much| very much| again)? for (.{4,90})$", low, re.I)
        if m and kind in ("thank-you note", "reply"):
            return " thanking them for " + swap_person(m.group(1))
        m = re.search(r"\b(?:won't|will not|can't|cannot) (?:be able to )?(make|attend|join) (.{3,60})$", low, re.I)
        if m and kind == "declining":
            return f" saying you can't {m.group(1).lower()} {swap_person(m.group(2))}"
    return ""


def classify_kind(subject, text, is_reply=False):
    """The kind of message (see KIND_RULES), "reply" when it answers someone and no other rule fits, else
    "update"."""
    first = " ".join(_sentences(text)[:3])
    for kind, pattern in KIND_RULES:
        flags = re.I | (re.M if pattern.startswith("^") else 0)
        if re.search(pattern, first if kind == "thank-you note" else text, flags):
            return kind
    if re.search(KIND_RULES[3][1], text, re.I) and len(text.split()) < 40:
        return "thank-you note"
    return "reply" if is_reply else "update"


def guess_tone(text, kind):
    """"friendly and casual", "polite and professional" or "firm but polite"."""
    if kind == "complaint":
        return "firm but polite"
    casual = len(re.findall(r"\b(hi|hey|cheers|great|cool|awesome|guys|folks|gonna|yeah|ok|okay|lol|dude|"
                            r"wanna|kinda|btw|thx)\b|!|"
                            r"\b\w+'(ll|re|ve|s|t|d)\b", text, re.I))
    formal = len(re.findall(r"\b(dear|regards|sincerely|kindly|please find|i would like|we would like|"
                            r"furthermore|however|therefore|respectfully|appreciate)\b", text, re.I))
    return "friendly and casual" if casual > formal else "polite and professional"


def guess_form(text, kind, audience):
    """"text message", "memo", "note" or "email"."""
    words = len(text.split())
    has_greeting = re.match(r"\s*(hi|hello|hey|dear|good|morning|all|team|everyone)\b", text, re.I)
    has_signoff = "[Your name]" in text
    if words <= 30 and not has_greeting and not has_signoff:
        return "text message"
    if kind == "announcement" and audience in ("the team", "everyone in the group"):
        return "memo"
    if kind == "thank-you note" and words <= 40:
        return "note"
    return "email"


def length_word(text):
    """"very short", "short" or "fairly short" from the word count."""
    words = len(text.split())
    if words <= 35:
        return "very short"
    if words <= 90:
        return "short"
    return "fairly short"


def subject_hint(subject):
    """' The subject line is "..."' when the subject says something useful, otherwise ""."""
    subj = (subject or "").strip().strip(".")
    if subj.lower() in GENERIC_SUBJECTS or len(subj) < 4 or len(subj.split()) > 12:
        return ""
    if subj.count("[") > 1 or re.fullmatch(r"[\W\d_]+", subj):
        return ""
    if len(re.sub(r"\[[^\]]*\]", " ", subj).split()) < 2:        # mostly a placeholder
        return ""
    return f' The subject is "{subj}".'


def make_instruction(subject, text, audience="a colleague", is_reply=False):
    """(instruction, details) for a cleaned message. details = {"kind", "form", "tone", "audience", "length"}."""
    kind = classify_kind(subject, text, is_reply)
    tone = guess_tone(text, kind)
    form = guess_form(text, kind, audience)
    length = length_word(text)
    point = main_point(kind, text)
    templates = TEMPLATES.get(kind, TEMPLATES["update"])
    pick = int(hashlib.sha1(text.encode("utf-8")).hexdigest(), 16) % len(templates)
    sentence = templates[pick].format(length=length, tone=tone, form=form, audience=audience, point=point)
    sentence = re.sub(r"\s+", " ", sentence).replace(" .", ".").replace("..", ".")
    if is_reply and kind != "reply":
        sentence += " It answers a message they sent."
    instruction = sentence + subject_hint(subject)
    return instruction, {"kind": kind, "form": form, "tone": tone, "audience": audience, "length": length}


# ----------------------------------------------------------------- chats, texts, letters and public comments

CHAT_TEMPLATES = [
    "Here is part of {setting}. Write {speaker}'s next message, in the same casual style.\n\n{context}",
    "Continue this conversation ({setting}). Reply as {speaker}, briefly and naturally.\n\n{context}",
    "Read the conversation below ({setting}) and write what {speaker} says next.\n\n{context}",
]
TALK_TEMPLATES = [
    "Here is a discussion on {setting}. Write {speaker}'s reply, as a comment on the talk page.\n\n{context}",
    "Reply to the last comment in this discussion ({setting}) as {speaker}.\n\n{context}",
]


def pick(templates, text):
    """One of templates, always the same one for the same text."""
    return templates[int(hashlib.sha1(text.encode("utf-8")).hexdigest(), 16) % len(templates)]


def make_chat_instruction(setting, context, speaker, reply, style=""):
    """(instruction, details) for "write the next message" in a conversation. context is [(speaker, text)]."""
    lines = "\n".join(f"{who}: {text}" for who, text in context)
    templates = TALK_TEMPLATES if style == "talk" else CHAT_TEMPLATES
    instruction = pick(templates, reply).format(setting=setting, speaker=speaker, context=lines)
    kind = classify_kind("", reply, is_reply=True)
    return instruction, {"kind": kind, "form": "chat message" if style != "talk" else "comment",
                         "tone": guess_tone(reply, kind), "audience": setting, "length": length_word(reply)}


SMS_TEMPLATES = [
    "Write a {length} text message to a friend{point}. Keep it {tone}, the way people really text.",
    "Text a friend{point}. Make it {length} and {tone}.",
    "Send a {length}, {tone} text message{point}.",
]


def make_sms_instruction(text):
    """(instruction, details) for a real text message (SMS)."""
    kind = classify_kind("", text)
    point = main_point(kind, text)
    tone = guess_tone(text, kind)
    if not point:
        point = {"thank-you note": " to say thanks", "apology": " to say sorry", "declining": " to say you can't make "
                 "it", "scheduling": " to sort out when to meet", "request": " asking for something",
                 "follow-up": " to check in", "confirmation": " to confirm", "invitation": " inviting them"}.get(kind, "")
    instruction = pick(SMS_TEMPLATES, text).format(length=length_word(text), tone=tone, point=point)
    return re.sub(r"\s+", " ", instruction), {"kind": kind, "form": "text message", "tone": tone,
                                              "audience": "a friend", "length": length_word(text)}


def make_letter_instruction(text, title):
    """(instruction, details) for a public-domain personal letter (written before about 1930)."""
    kind = classify_kind("", text)
    tone = "warm and old-fashioned"
    to = "a friend or relative"
    m = re.match(r"\s*(?:my )?(?:dear|dearest)\s+([^,\n:]{1,30})", text, re.I)
    if m and re.match(r"(?i)(mother|father|sister|brother|aunt|uncle|son|daughter|wife|husband)", m.group(1)):
        to = "your " + m.group(1).split()[0].lower()
    what = {"thank-you note": "thanking them", "apology": "apologising", "invitation": "with an invitation",
            "declining": "declining something", "request": "asking a favour"}.get(kind, "with your news")
    instruction = (f"Write a personal letter to {to} {what}, in the style of a letter written before 1930 "
                   f"(from \"{title.strip()}\").")
    return instruction, {"kind": kind, "form": "letter", "tone": tone, "audience": to, "length": length_word(text)}


def make_comment_instruction(text, agency, title):
    """(instruction, details) for a public comment sent to a US federal agency."""
    kind = "complaint" if re.search(r"\b(oppose|against|disagree|unfair|terrible|outrage\w*)\b", text, re.I) \
        else "public comment"
    tone = guess_tone(text, "update")
    about = f' about "{title.strip()}"' if title else ""
    instruction = (f"Write a public comment to the US agency {agency or 'in charge'}{about}, in your own words, as "
                   f"an ordinary member of the public. Make it {length_word(text)} and {tone}.")
    return instruction, {"kind": kind, "form": "public comment", "tone": tone, "audience": agency,
                         "length": length_word(text)}
