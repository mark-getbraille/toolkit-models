"""Style labels for the Writing Kit. Every example gets one style from the fixed list below and a register (formal,
neutral or casual), so the owner can train on one style at a time. build_dataset.py writes one folder per style
(out/<style>/train.jsonl and validation.jsonl) besides the combined files, and --styles builds only chosen ones.

  label(row, source_key, record)   (style, register) for one example
"""

import re

STYLES = {
    # everyday messages
    "email_business": "work email: requests, replies, updates, scheduling, follow-ups between colleagues or companies",
    "email_personal": "personal email to friends, family, neighbours or landlords",
    "text_message": "text messages (SMS) and very short notes",
    "chat": "live chat: IRC channels, customer service chats, assistant conversations",
    "forum_post": "posts on Usenet groups, mailing-list style forums and web forums",
    "comment_public": "public comments: comments to government agencies, Wikipedia talk-page comments",
    "review": "product and service reviews",
    "social_post": "short social media posts and announcements",
    # formal and workplace documents
    "letter_formal": "formal letters: to agencies, the SEC, shareholders, fundraising letters",
    "letter_personal": "personal letters, mostly old public-domain letters",
    "memo": "memos and documents attached to work email",
    "press_release": "press releases from companies and agencies",
    "report": "reports from agencies and organisations",
    "minutes": "minutes of meetings",
    "transcript_meeting": "transcripts of hearings, parliament and public meetings",
    "transcript_court": "transcripts of court proceedings (US Supreme Court oral arguments)",
    "transcript_conversation": "transcripts of everyday spoken conversations (telephone, face to face)",
    "speech": "speeches, remarks and addresses",
    "plain_language_gov": "plain-language government writing: public notices and statements",
    "legal": "legal writing: opinions, filings",
    "technical": "technical and how-to writing, guides",
    "academic": "academic and textbook writing, grant summaries",
    "news": "news reports and magazine articles",
    "blog": "blog posts",
    # creative
    "fiction_prose": "novels and short stories",
    "fan_fiction": "fan fiction released under an open licence",
    "poetry": "poems",
    "screenplay_drama": "plays and screenplays",
    "dialogue": "made-up dialogues between characters",
    "children_story": "stories for children",
    "humour": "humorous writing",
}
REGISTERS = ("formal", "neutral", "casual")

FORMAL_STYLES = {"letter_formal", "press_release", "report", "minutes", "transcript_court", "speech",
                 "plain_language_gov", "legal", "technical", "academic", "memo"}
CASUAL_STYLES = {"text_message", "chat", "forum_post", "social_post", "review", "transcript_conversation",
                 "dialogue", "humour", "email_personal", "fan_fiction"}

BY_SOURCE = {
    "enron": "email_business", "idl": "email_business", "doj_google": "email_business", "w3c": "email_business",
    "debian": "forum_post", "usenet": "forum_post", "irc": "chat", "sms": "text_message", "taskmaster": "chat",
    "sgd": "chat", "multiwoz": "chat", "topical": "chat", "abcd": "chat", "wikitalk": "comment_public",
    "gutenberg": "letter_personal", "sbcsae": "transcript_conversation", "regulations": "comment_public",
    "scotus": "transcript_court", "hearings": "transcript_meeting", "hansard": "transcript_meeting",
    "fedreg": "plain_language_gov", "openstax_business": "academic", "wikinews": "news", "nsf": "academic",
    "blogs": "blog", "scanned_federal": "email_business", "scanned_state": "email_business",
    "govinfo_exhibits": "email_business", "scanned_folder": "email_business",
}
PERSONAL_WORDS = re.compile(r"(?i)\b(friend|mom|dad|mother|father|sister|brother|grandpa|grandma|neighbou?r|"
                            r"landlord|cousin|aunt|uncle|wife|husband|boyfriend|girlfriend|birthday|teacher)\b")


def _register(style, tone=""):
    if style in FORMAL_STYLES:
        return "formal"
    if style in CASUAL_STYLES:
        return "casual"
    tone = (tone or "").lower()
    if "casual" in tone or "conversational" in tone:
        return "casual"
    if "formal" in tone and "informal" not in tone:
        return "formal"
    return "neutral"


def label(row, source_key, record=None):
    """(style, register) for one example row (with its kind, form and tone) from source_key."""
    record = record or {}
    kind, form, tone = row.get("kind", ""), row.get("form", ""), row.get("tone", "")
    style = record.get("style_label")
    if not style:
        if kind == "attachment":
            style = "memo"
        elif source_key in ("oasst2", "dolly"):
            text = row.get("instruction", "")
            if form == "text message" or re.search(r"(?i)\btext\b|\bsms\b|\btweet", text):
                style = "social_post" if re.search(r"(?i)tweet|post", text) else "text_message"
            elif re.search(r"(?i)\bletter\b", text):
                style = "letter_formal" if not PERSONAL_WORDS.search(text) else "letter_personal"
            elif re.search(r"(?i)\bmemo\b", text):
                style = "memo"
            else:
                style = "email_personal" if PERSONAL_WORDS.search(text) else "email_business"
        elif source_key == "edgar":
            style = "press_release" if kind == "press release" else "letter_formal"
        elif source_key == "oanc":
            style = {"fundraising letter": "letter_formal", "slate": "news", "government": "report",
                     "travel": "technical"}.get(kind) or ("transcript_conversation" if form == "chat message"
                                                          else "news")
        elif source_key == "presidential":
            style = {"letter": "letter_formal", "statement": "plain_language_gov"}.get(kind, "speech")
        elif source_key == "fineweb":
            style = "review" if kind == "review" else "forum_post"
        else:
            style = BY_SOURCE.get(source_key, "email_business")
        if style == "email_business" and source_key in ("enron", "idl", "usenet") and \
                row.get("audience") in ("an outside contact",) and tone == "friendly and casual" and \
                PERSONAL_WORDS.search(row.get("response", "")[:400]):
            style = "email_personal"
    assert style in STYLES, style
    return style, _register(style, tone)
