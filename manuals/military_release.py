"""The release rule for US military publications, shared by every builder in this repository.

THE SAME FILE is kept in four places, because each part of the repository runs on its own (the pack builders, the
textbooks, the manuals and the training kit, which runs from a copy on the owner's computer):
    packs/military_release.py, textbooks/military_release.py, manuals/military_release.py and
    training-kit/kit/military_release.py
packs/test_military_release.py checks that the four copies are the same, word for word. Change one, copy it to the
other three.

THE OWNER'S DECISION (22 November 2026): "Remove the cleared-for-public-release restrictions for military
publications if posted by a government entity or a museum or archive.org. I consider them safe to include."

So a US military publication is judged like this (release_rule):
  1. Classified: its front pages print CONFIDENTIAL, SECRET or TOP SECRET (in capitals, as markings are printed;
     "UNCLASSIFIED" is not a classified marking) or "Classified by:". The owner's refinement (22 November 2026):
     "Classified, Secret or Confidential is OK if published openly." So an old classification marking is accepted,
     verdict "public", with the notice "Originally classified <level>; declassified and released by <who> (<the
     declassification marking or the address>)", when there is evidence that the government declassified and
     released it:
       a. a US government entity publishes it openly on its own public site (.gov or .mil: the CIA's FOIA reading
          room, the National Archives, presidential libraries, DTIC's public area, agency FOIA libraries), read
          from that address at build time, or a separate government address checked to answer without a login; or
       b. a copy from the Internet Archive or a museum that clearly is a declassified government release: a
          declassification marking in its text (DECLASSIFIED, "Declassified by", "Authority NND ...", "Approved for
          Release", "Sanitized Copy Approved for Release", a FOIA release stamp, an E.O. 13526 (or 12958, 12356)
          declassification line), or its record names the releasing agency or NARA (released_by). Overstruck
          markings cannot be seen in a text layer, so they count only through a. or a written marking.
     Without such evidence (live markings), and always from a leak site (LEAK_HOSTS: WikiLeaks and the like) or any
     other third-party host, it is LEFT OUT entirely: verdict "out". The builders' weapons, explosives, demolition,
     sabotage, interrogation and tactics exclusions apply to declassified documents as to any other.
  2. Restricted: its front pages print a restricted marking (Distribution Statement B to F, "distribution authorized
     to ...", "distribution is limited to ...", FOUO, CUI, NOFORN, "not releasable to", ITAR or another
     export-control warning such as "WARNING: this document contains technical data whose export is restricted").
     The owner's refinement (22 November 2026): "If stamped restricted etc. but published openly by a government
     entity, it is safe." So:
       a. When a US government entity itself publishes it openly on its own public website (a .gov or .mil address
          anyone can reach without a login: armypubs.army.mil's public pages, an agency library, govinfo, the
          Library of Congress, DTIC's public area), it goes into the open collections like any other government
          work, verdict "public", with the notice "A work of the US armed forces (public domain under 17 U.S.C.
          105). Its front pages print '<the marking>', but <the agency> publishes it openly at <address>." The
          builder must have read the copy from that government address at build time (which shows it still
          answers without a login), or checked a separate government address with answers_without_login; when
          the address no longer answers openly, point b applies.
       b. A copy found only on archive.org, a museum or another host that is not the government's: it is NEVER put
          into a public, open collection (those collections are published as public GitHub releases, and
          export-controlled technical data must not be republished without the government publishing it itself).
          From archive.org or a museum the verdict is "personal": the builder puts it on its personal-use route
          marked PERSONAL USE ONLY (the training kit's personal-use collections, the textbooks' personal-use books,
          or a link-only entry the owner fetches himself with Program Downloader). From any other host it is left
          out, as before. Verdict "personal" or "out".
  3. No marking, from an open host: a copy from a government website (.gov, .mil: a US government agency or
     library such as the Library of Congress, DTIC, the Army Publishing Directorate or GPO), a museum, or the
     Internet Archive (archive.org). A missing Distribution Statement A no longer leaves it out. Verdict "public",
     with a truthful release line: when the statement is printed, it says so; when it is not, it says the
     publication is a work of the US armed forces (public domain under 17 U.S.C. 105) published openly by that
     host, and that its front pages print no distribution statement. It never claims "approved for public release"
     for a copy that does not print it.
  4. No marking, from any other host (a third-party website): the old rule. Kept only when Distribution Statement A
     is printed.

A copy whose front pages have no readable text (a scan without a text layer) is left out: its markings cannot be
checked. Every other check (the weapons and explosives safety rules, licences of works that are not the government's,
robots.txt and terms of use, the text-layer checks) stays in the builders, unchanged.

Some Army PDFs print their cover in a font whose letters come out moved by 29 places (",675,%87,21" for
"DISTRIBUTION"); every check also reads that form (unshifted), so a marking is found in either form.
"""

import re
import urllib.parse
from collections import namedtuple

# Distribution Statement A, in the forms the publications print it.
DISTRIBUTION_A = re.compile(r"approved\s*for\s*public\s*release\s*[;:,.]?\s*(?:and\s*)?distribution\s*(?:is\s*)?"
                            r"unlimited|distribution\s*(?:is\s*)?unlimited\s*[;:,.]?\s*approved\s*for\s*public\s*"
                            r"release|distribution\s+statement\s+a\s*[:.]\s*approved", re.I)

# Restricted (but unclassified) markings: never republished, personal use at most.
RESTRICTED = re.compile(r"distribution\s*(?:statement\s*)?[B-F]\s*[:.\-–—]|distribution\s+(?:statement\s+)?[B-F]\b|"
                        r"distribution\s*authori[sz]ed\s*to|distribution\s+(?:is\s+)?(?:limited|restricted)\s+to|"
                        r"authorized\s+to\s+U\.?\s?S\.?\s+Government\s+agencies|for\s*official\s*use\s*only|"
                        r"\bFOUO\b|controlled\s*unclassified|\bCUI\b|\bNOFORN\b|export[- ]?controlled|\bITAR\b|"
                        r"not\s+releasable\s+to|warning:?\s+this\s+document\s+contains\s+technical\s+data\s+whose\s+"
                        r"export", re.I)

# Classified markings, printed in capitals ("SECRET", "TOP SECRET", "CONFIDENTIAL"), and "Classified by:". Matched
# with the case as printed, so "UNCLASSIFIED", "Secretary" or "keep it confidential" are not taken for one.
CLASSIFIED = re.compile(r"\b(?:TOP\s+SECRET|SECRET|CONFIDENTIAL)\b(?!\s+(?:SERVICE|SANTA))|"
                        r"(?i:\bclassified\s+by\s*:)")

# Evidence that a classified document was declassified and released (point 1 b of the module docstring).
DECLASSIFIED = re.compile(r"\bdeclassified\b|\bdeclassified\s+by\b|authority\s*:?\s*NND\s*-?\s*\d+|"
                          r"(?<!public\s)approved\s+for\s+release|sanitized\s+copy\s+approved|"
                          r"FOIA\s*(?:release|case|request|\(b\))|released\s+under\s+(?:the\s+)?(?:FOIA|freedom\s+of\s+"
                          r"information)|E\.?\s?O\.?\s*(?:13526|12958|12356|12065)", re.I)
# The classification levels, highest first.
LEVELS = (("TOP SECRET", re.compile(r"\bTOP\s+SECRET\b")),
          ("SECRET", re.compile(r"\bSECRET\b(?!\s+(?:SERVICE|SANTA))")),
          ("CONFIDENTIAL", re.compile(r"\bCONFIDENTIAL\b")))
# Sites that post leaked documents: never a release, whatever the document shows.
LEAK_HOSTS = ("wikileaks.org", "wikileaks.ch", "wikileaks.de", "cryptome.org", "ddosecrets.com",
              "distributeddenialofsecrets.com", "pastebin.com", "t.me", "telegram.me", "4chan.org", "discord.com",
              "discordapp.com", "reddit.com", "x.com", "twitter.com")

# Open hosts by the end of their address: (host ending, the words for it in a release line).
NAMED_HOSTS = [
    ("archive.org", "the Internet Archive (archive.org)"),
    ("dtic.mil", "the Defense Technical Information Center (DTIC)"),
    ("armypubs.army.mil", "the Army Publishing Directorate (armypubs.army.mil)"),
    ("loc.gov", "the Library of Congress (loc.gov)"),
    ("govinfo.gov", "the US Government Publishing Office (govinfo.gov)"),
    ("gpo.gov", "the US Government Publishing Office (gpo.gov)"),
    ("si.edu", "the Smithsonian Institution (si.edu)"),
    ("cia.gov", "the CIA's FOIA Electronic Reading Room (cia.gov)"),
    ("archives.gov", "the National Archives (archives.gov)"),
]
# Museums that are not under .gov, .mil or si.edu (add a museum's own host here when one is used).
MUSEUM_HOSTS = ("nationalww2museum.org", "theworldwar.org", "metmuseum.org", "navalunderseamuseum.org")

# Fewer words than this on the front pages: a scan without a text layer, whose markings cannot be read, so it is
# left out (a missing statement may only be accepted when the program could see there is no marking).
MIN_WORDS = 1

Release = namedtuple("Release", "verdict release reason statement host")
# verdict    "public" (may go into the open collections), "personal" (personal use only, never republished) or
#            "out" (left out)
# release    the truthful release line to show with the publication ("" when it is left out)
# reason     why it is personal use or left out ("" when public)
# statement  True when Distribution Statement A is printed
# host       the words for where the copy comes from ("" for a host that is not open)


def unshifted(text):
    """The text with every character moved 29 places on: some Army PDFs print the cover in a font whose letters come
    out 29 places early (",675,%87,21" is "DISTRIBUTION"). Only used for the release checks."""
    return "".join(chr(ord(c) + 29) if 3 < ord(c) < 94 and c not in " \t\n\r" else c for c in text)


def host_of(source):
    """The host of an address ("https://archive.org/details/x" -> "archive.org"); a bare host is returned as it is,
    in small letters."""
    source = str(source or "").strip().lower()
    if "//" in source:
        source = urllib.parse.urlsplit(source).hostname or ""
    return source.split("/")[0].split(":")[0]


def is_government(source):
    """True when the address or host is a US government website (.gov or .mil: an agency, DTIC, the Army
    Publishing Directorate, the Library of Congress, GPO). Museums and archive.org are open hosts but not the
    government's."""
    host = host_of(source)
    return bool(host) and (host.endswith((".gov", ".mil")) or host in ("gov", "mil"))


# Words in an address that mean a login stands in the way (a common access card, single sign-on ...).
LOGIN = re.compile(r"\b(?:log\s*in|login|sign\s*in|signin|sso|cac|common\s+access\s+card|authenticat\w*|"
                   r"password|auth)\b", re.I)


def answers_without_login(status, final_url="", content_type="", first_text=""):
    """True when a government address answered openly: HTTP status 200, not sent on to a login page, and not an
    HTML page asking for a password. The builder makes the request and passes what it got: the status, the address
    it ended at (after redirects), the content type and the first few thousand characters."""
    if int(status or 0) != 200:
        return False
    parts = urllib.parse.urlsplit(str(final_url or ""))
    words = re.sub(r"[/\-_.?=&]+", " ", f"{parts.hostname or ''} {parts.path} {parts.query}")
    if LOGIN.search(words):
        return False
    if "html" in str(content_type or "").lower() and re.search(r"<input[^>]+type=[\"']?password", str(first_text
                                                                                                   or ""), re.I):
        return False
    return True


def open_host(source):
    """The words for an open host (point 3 of the module docstring), or "" for any other host. source: an address or
    a host."""
    host = host_of(source)
    if not host:
        return ""
    for ending, words in NAMED_HOSTS:
        if host == ending or host.endswith("." + ending):
            return words
    if host.endswith((".gov", ".mil")) or host in ("gov", "mil"):
        return f"the US government site {host}"
    if host.endswith(".museum") or any(host == m or host.endswith("." + m) for m in MUSEUM_HOSTS):
        return f"the museum site {host}"
    return ""


def _search(pattern, text):
    """The first match of pattern in text or in its unshifted form, or None."""
    for form in (text, unshifted(text)):
        found = pattern.search(form)
        if found:
            return found
    return None


def marking(front_text):
    """("classified" or "restricted", the marking's words) found in the front pages, or ("", "")."""
    text = " ".join(str(front_text or "").split())
    bad = _search(CLASSIFIED, text)
    if bad:
        return "classified", " ".join(bad.group(0).split())
    bad = _search(RESTRICTED, text)
    if bad:
        return "restricted", " ".join(bad.group(0).split()).rstrip(":.-–— ")
    return "", ""


def has_statement_a(front_text):
    """True when the front pages print Distribution Statement A."""
    return bool(_search(DISTRIBUTION_A, " ".join(str(front_text or "").split())))


def level_of(front_text):
    """The highest classification level printed in the front pages ("TOP SECRET", "SECRET", "CONFIDENTIAL"), else
    "classified" (only "Classified by:" was found)."""
    text = " ".join(str(front_text or "").split())
    for name, pattern in LEVELS:
        if _search(pattern, text):
            return name
    return "classified"


def declassification(front_text):
    """The words of a declassification marking in the front pages (point 1 b), or ""."""
    found = _search(DECLASSIFIED, " ".join(str(front_text or "").split()))
    return " ".join(found.group(0).split()) if found else ""


def leak_host(source):
    """True when the address or host is a site that posts leaked documents (LEAK_HOSTS)."""
    host = host_of(source)
    return any(host == h or host.endswith("." + h) for h in LEAK_HOSTS)


def _gov_release(source, gov_address, gov_answers):
    """The government address that publishes the copy openly (the source itself when it is a government site and
    answered; else gov_address when it is a government site checked to answer), or ""."""
    if is_government(source) and gov_answers is not False:
        return source if "//" in str(source) else f"https://{host_of(source)}/"
    if gov_address and is_government(gov_address) and gov_answers is True:
        return gov_address
    return ""


def release_rule(front_text, source, work="a work of the US armed forces", gov_address="", gov_answers=None,
                 released_by=""):
    """Judge one US military publication by the words of its front pages and where its copy comes from, as the
    module docstring says. Returns a Release.
      source       the address (or host) the copy was read from
      work         how the publication is named in the release line ("a work of the US Navy")
      gov_address  for a restricted-marked copy: a US government address where the government itself publishes it
                   (when the copy was read from such an address, source is used and this may stay empty)
      gov_answers  whether that government address answered without a login when it was checked at build time
                   (answers_without_login). A copy read from a government source answered (the builder just read
                   it) unless False is passed; a separate gov_address counts only when this is True.
      released_by  for a classified-marked copy from the Internet Archive or a museum: the releasing agency or NARA
                   as its own record names it (point 1 b)"""
    host = open_host(source)
    words_seen = max(len(re.findall(r"[A-Za-z]{2,}", form)) for form in (str(front_text or ""),
                                                                         unshifted(str(front_text or ""))))
    if words_seen < MIN_WORDS:
        return Release("out", "", "its front pages have no readable text (a scan without a text layer), so its "
                       "markings cannot be checked", False, host)
    kind, words = marking(front_text)
    statement = has_statement_a(front_text)
    if kind == "classified":
        level = level_of(front_text)
        declassified = declassification(front_text)
        address = "" if leak_host(source) else _gov_release(source, gov_address, gov_answers)
        start = f"{work[0].upper()}{work[1:]} (public domain under 17 U.S.C. 105). Originally classified {level}"
        if address:
            evidence = f"{declassified}; " if declassified else ""
            line = f"{start}; declassified and released by {open_host(address)} ({evidence}{address})."
            return Release("public", line, "", statement, open_host(address))
        if host and not leak_host(source) and (declassified or released_by):
            who = released_by or "the US government"
            evidence = f"marked '{declassified}'" if declassified else "as its record says"
            line = f"{start}; declassified and released by {who} ({evidence}); copy from {host}."
            return Release("public", line, "", statement, host)
        return Release("out", "", f"prints a classified marking ({level}) with no declassification or government "
                       "release shown: never included", statement, host)
    if kind == "restricted":
        address = _gov_release(source, gov_address, gov_answers)
        if address:
            agency = open_host(address)
            line = (f"{work[0].upper()}{work[1:]} (public domain under 17 U.S.C. 105). Its front pages print "
                    f"'{words}', but {agency} publishes it openly at {address}.")
            return Release("public", line, "", statement, open_host(address))
        if host:
            line = (f"PERSONAL USE ONLY: {work} (public domain under 17 U.S.C. 105) whose front pages print a "
                    f"restricted marking ({words}), and no open copy on a government site was found; not "
                    f"republished. Fetch it yourself from {host}.")
            return Release("personal", line, f"prints a restricted marking ({words}): personal use only, fetch it "
                           "yourself", statement, host)
        return Release("out", "", f"prints a restricted marking ({words})", statement, host)
    if statement:
        return Release("public", "Distribution Statement A: approved for public release; distribution is unlimited",
                       "", True, host)
    if host:
        line = (f"{work[0].upper()}{work[1:]} (public domain under 17 U.S.C. 105), published openly by {host}; its "
                "front pages print no distribution statement.")
        return Release("public", line, "", False, host)
    return Release("out", "", "no Distribution Statement A on its front pages, and its copy is not from a "
                   "government, museum or Internet Archive site", False, host)
