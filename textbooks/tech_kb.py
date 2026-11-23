"""Computer help and technology documentation for the reference library, in the group "techdocs" ("Reference,
computer help and technology"), the owner's request of 2026-11-22. Keys: techdocs (every book here), tech:microsoft
and tech:apple (one company's books), tech:<name> (one book).

What this module builds, in plain words: documentation that its publisher puts under an open licence in a public git
repository, IN FULL (every article of the folders named), one book per product, read by one shallow git clone of
only those folders (GitHub allows cloning public repositories; its robots.txt shuts programs out of its web pages and
downloads, which are not used).

  Microsoft Learn documentation from the MicrosoftDocs repositories on GitHub. Each repository's LICENSE (checked at
    every build) puts the documentation under Creative Commons Attribution 4.0 (CC BY 4.0) and its LICENSE-CODE puts
    the code samples under the MIT licence. Built: PowerShell (the conceptual documentation, the current long-term
    support version's cmdlet reference, and Windows PowerShell 5.1's reference, the one built into Windows);
    Microsoft's troubleshooting and support articles (the SupportArticles-docs repository behind
    learn.microsoft.com/troubleshoot) for Windows, Windows Server, Outlook, Office, Microsoft 365, Exchange,
    SharePoint and OneDrive, Teams and Microsoft Edge; the Microsoft 365 admin documentation; and the accessibility
    guidance for Windows apps (the developer guides to Narrator, keyboard access, screen readers and high contrast);
    the Windows commands reference (every command of the command prompt) and the Windows Terminal documentation.
  Apple's open-source Swift documentation: "The Swift Programming Language" (the swift-book repository) and the
    Swift.org documentation (API design guidelines, getting started, package manager, server, C++ interoperability),
    both under the Apache License 2.0 with the Runtime Library Exception, whose text is a page of each book.

Not included, with the reason and an index or sitemap address for the owner's Program Downloader (NOT_INCLUDED):
support.microsoft.com and support.apple.com articles and user guides (the Narrator and VoiceOver guides among them),
Apple's Human Interface Guidelines and developer documentation (all copyrighted), and Microsoft Learn pages whose
source repositories are private (Windows client, Teams, the Learn accessibility hub).

Each article is converted from its Markdown (Microsoft's DocFX flavour or Apple's DocC flavour) by md_page(): code
blocks kept as they are, notes and warnings as quotations, pictures as their descriptions, includes inlined, links
between articles of the book pointed at its pages. Every book has its licence and notice, "published" (the newest
article date, or the commit date), "version" (the repository's commit), the key and fingerprint for the weekly update
check (sign(): the repository's newest commit), and "originals" (the repository and its licence files).

refs_common.REGISTRY sends the tech: keys here. Run from the repository's folder:
  python3 textbooks/tech_kb.py tech:swift_book --out build/textbooks
  python3 textbooks/tech_kb.py tech:ms_windows_support --out build/textbooks --limit 20     (a small test)
  python3 textbooks/tech_kb.py --list techdocs
"""

import argparse
import datetime
import html
import os
import posixpath
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_common as R  # noqa: E402

GROUP = "techdocs"
GROUPS = {GROUP: "Reference, computer help and technology"}
WORDS = ("techdocs", f"group:{GROUP}", "tech:microsoft", "tech:apple")

CC_BY = "CC BY 4.0"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"
APACHE = "Apache License 2.0"
APACHE_URL = "https://www.apache.org/licenses/LICENSE-2.0"
MS_CC_TEXT = r"Attribution 4\.0 International"
APACHE_TEXT = r"Apache License\s+Version 2\.0"
MS = "Microsoft Corporation (Microsoft Learn documentation)"
MS_NOTICE = ("© Microsoft Corporation. The documentation is licensed under the Creative Commons Attribution 4.0 "
             "International licence (https://creativecommons.org/licenses/by/4.0/) and its code samples under the "
             "MIT licence, as the repository's LICENSE and LICENSE-CODE files say. Changed: the Markdown articles "
             "converted to pages for reading offline (pictures replaced by their descriptions). Microsoft, Windows, "
             "Office, Outlook, Teams, PowerShell and the other names are trademarks of the Microsoft group of "
             "companies; this book is not made or endorsed by Microsoft. Check learn.microsoft.com for the current "
             "article.")
SWIFT_NOTICE = ("Copyright (c) 2014 - 2026 Apple Inc. and the Swift project authors. Licensed under the Apache "
                "License v2.0 with Runtime Library Exception (the full text is the last page of this book). Changed: "
                "the DocC or Markdown articles converted to pages for reading offline (pictures replaced by their "
                "descriptions). Swift and the Swift logo are trademarks of Apple Inc.")

# The books. repo: the GitHub repository; branch: its default branch (whose LICENSE is checked); folders: the folders
# read (every .md article in them); includes: more folders their [!INCLUDE] files come from; source: the published
# address; kind: "docfx" (Microsoft) or "docc"/"jekyll" (Swift). "{lts}" in a folder is the current long-term-support
# PowerShell version (lts_version()).
MS_BOOKS = [
    dict(name="ms_powershell", repo="MicrosoftDocs/PowerShell-Docs", branch="main", licence_file="LICENSE.md",
         folders=["reference/docs-conceptual"], includes=["reference/includes"],
         title="PowerShell documentation: install, learn, script and manage with PowerShell",
         subject="PowerShell (command line and scripting)", source="https://learn.microsoft.com/powershell/scripting/",
         description="Microsoft's PowerShell documentation, every article: what PowerShell is, installing it on "
                     "Windows, macOS and Linux, learning it (the PowerShell 101 guide, deep dives), scripting, "
                     "remoting, security, the PowerShell Gallery, writing modules and the developer guide, the "
                     "integrated scripting environment and what is new in each version."),
    dict(name="ms_powershell_reference", repo="MicrosoftDocs/PowerShell-Docs", branch="main", licence_file="LICENSE.md",
         folders=["reference/{lts}"], includes=["reference/includes"],
         title="PowerShell {lts} cmdlet reference (long-term support version)",
         subject="PowerShell (command line and scripting)", source="https://learn.microsoft.com/powershell/module/",
         description="The reference of every cmdlet in PowerShell's own modules for the current long-term support "
                     "version ({lts}), with its syntax, description, parameters and examples, and the about_ topics "
                     "(the language: variables, operators, loops, functions, error handling, remoting and more)."),
    dict(name="ms_windows_powershell_51_reference", repo="MicrosoftDocs/PowerShell-Docs", branch="main",
         licence_file="LICENSE.md", folders=["reference/5.1"], includes=["reference/includes"],
         title="Windows PowerShell 5.1 cmdlet reference (the PowerShell built into Windows)",
         subject="PowerShell (command line and scripting)", source="https://learn.microsoft.com/powershell/module/"
         "?view=powershell-5.1",
         description="The reference of every cmdlet in Windows PowerShell 5.1's own modules, the version built into "
                     "Windows 10 and 11, with syntax, parameters and examples, and its about_ topics."),
    dict(name="ms_windows_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main",
         folders=["support/windows-client"], includes=["support/includes"],
         title="Windows troubleshooting and support articles (Microsoft Learn)", subject="Windows (help and "
         "troubleshooting)", source="https://learn.microsoft.com/troubleshoot/windows-client/",
         description="Microsoft's troubleshooting articles for Windows 10 and Windows 11, every one: installing and "
                     "updating, startup and performance, networking, printing, devices and drivers, user profiles "
                     "and sign-in, security, shell and desktop, applications, backup and recovery."),
    dict(name="ms_windows_server_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main",
         folders=["support/windows-server"], includes=["support/includes"],
         title="Windows Server troubleshooting and support articles (Microsoft Learn)",
         subject="Windows Server (help and troubleshooting)",
         source="https://learn.microsoft.com/troubleshoot/windows-server/",
         description="Microsoft's troubleshooting articles for Windows Server, every one: Active Directory, "
                     "networking, remote desktop, storage, Group Policy, Hyper-V, deployment, performance, printing "
                     "and security."),
    dict(name="ms_outlook_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main", folders=["Outlook"],
         includes=["Outlook/includes", "support/includes"], title="Outlook troubleshooting and support articles "
         "(Microsoft Learn)", subject="Outlook (email; help and troubleshooting)",
         source="https://learn.microsoft.com/troubleshoot/outlook/",
         description="Microsoft's troubleshooting articles for classic Outlook for Windows, the new Outlook for "
                     "Windows and Outlook for Mac, every one: accounts and profiles, sending and receiving, "
                     "calendars, data files, performance, add-ins, search and printing."),
    dict(name="ms_office_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main", folders=["Office"],
         includes=["Office/includes", "support/includes"], title="Microsoft Office troubleshooting and support "
         "articles (Word, Excel, PowerPoint, Access; Microsoft Learn)", subject="Microsoft Office (help and "
         "troubleshooting)", source="https://learn.microsoft.com/troubleshoot/office/",
         description="Microsoft's troubleshooting articles for the Office apps (Word, Excel, PowerPoint, Access, "
                     "OneNote, Project, Visio, Publisher), installation and activation, every one."),
    dict(name="ms_microsoft365_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main",
         folders=["Microsoft365"], includes=["Microsoft365/includes", "support/includes"],
         title="Microsoft 365 troubleshooting and support articles (Microsoft Learn)",
         subject="Microsoft 365 (help and troubleshooting)", source="https://learn.microsoft.com/troubleshoot/"
         "microsoft-365/", description="Microsoft's troubleshooting articles for Microsoft 365: the admin center, "
         "accounts and licences, Purview compliance and other services, every one."),
    dict(name="ms_exchange_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main", folders=["Exchange"],
         includes=["Exchange/includes", "support/includes"], title="Exchange troubleshooting and support articles "
         "(Microsoft Learn)", subject="Exchange (email servers; help and troubleshooting)",
         source="https://learn.microsoft.com/troubleshoot/exchange/",
         description="Microsoft's troubleshooting articles for Exchange Online, Exchange Server and hybrid "
                     "Exchange, every one: mail flow, mailboxes, clients, migration, administration."),
    dict(name="ms_sharepoint_onedrive_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main",
         folders=["SharePoint"], includes=["SharePoint/includes", "support/includes"],
         title="SharePoint and OneDrive troubleshooting and support articles (Microsoft Learn)",
         subject="SharePoint and OneDrive (help and troubleshooting)",
         source="https://learn.microsoft.com/troubleshoot/sharepoint/",
         description="Microsoft's troubleshooting articles for SharePoint Online, SharePoint Server and OneDrive, "
                     "every one: sync, sharing and permissions, sites, search and administration."),
    dict(name="ms_teams_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main", folders=["Teams"],
         includes=["Teams/includes", "support/includes"], title="Microsoft Teams troubleshooting and support "
         "articles (Microsoft Learn)", subject="Microsoft Teams (help and troubleshooting)",
         source="https://learn.microsoft.com/troubleshoot/microsoftteams/",
         description="Microsoft's troubleshooting articles for Teams, every one: signing in, meetings and "
                     "conferencing, calls and phone system, chat and presence, files, Teams Rooms and devices, and "
                     "administration."),
    dict(name="ms_edge_support", repo="MicrosoftDocs/SupportArticles-docs", branch="main",
         folders=["support/microsoft-edge"], includes=["support/includes"],
         title="Microsoft Edge troubleshooting and support articles (Microsoft Learn)",
         subject="Microsoft Edge (web browser; help and troubleshooting)",
         source="https://learn.microsoft.com/troubleshoot/microsoft-edge/",
         description="Microsoft's troubleshooting articles for the Microsoft Edge browser, every one."),
    dict(name="ms_microsoft365_admin", repo="MicrosoftDocs/microsoft-365-docs", branch="public",
         folders=["microsoft-365/admin"], includes=["microsoft-365/includes", "microsoft-365/admin/includes"],
         title="Microsoft 365 admin documentation (Microsoft Learn)", subject="Microsoft 365 (administration)",
         source="https://learn.microsoft.com/microsoft-365/admin/",
         description="Microsoft's documentation for running Microsoft 365 for a business or organization, every "
                     "article: setting up, adding users and assigning licences, domains, email, security, billing, "
                     "the admin center's accessibility and keyboard shortcuts, reports and support."),
    dict(name="ms_windows_app_accessibility", repo="MicrosoftDocs/windows-dev-docs", branch="docs",
         folders=["hub/apps/design/accessibility"], includes=["hub/apps/includes"],
         title="Accessibility in Windows apps: Narrator, screen readers, keyboard and high contrast (Microsoft "
               "Learn)", subject="Windows accessibility (for app makers)",
         source="https://learn.microsoft.com/windows/apps/design/accessibility/accessibility",
         description="Microsoft's guide to making Windows apps accessible, every article: accessibility overview, "
                     "designing for screen readers and Narrator, keyboard accessibility, high contrast and colour, "
                     "text scaling, accessible text requirements, custom automation peers, testing with Narrator "
                     "and Accessibility Insights, and the accessibility checklist."),
    # added 2026-11-23 for the computers collection (computers_more.py, comp:index): the command prompt and the
    # Windows Terminal, both CC BY 4.0 by their repositories' LICENSE (checked at every build)
    dict(name="ms_windows_commands", repo="MicrosoftDocs/windowsserverdocs", branch="main",
         folders=["WindowsServerDocs/administration/windows-commands"], includes=[],
         title="Windows commands: the command prompt reference (cmd, Microsoft Learn)",
         subject="Windows (command prompt)", source="https://learn.microsoft.com/windows-server/administration/"
         "windows-commands/windows-commands",
         description="Microsoft's reference of every command of the Windows command prompt (cmd.exe), one article "
                     "per command, with its syntax, parameters and examples: dir, cd, copy, xcopy, robocopy, del, "
                     "move, ren, md, attrib, type, more, find, findstr, sort, ipconfig, ping, tracert, netstat, "
                     "nslookup, chkdsk, sfc, diskpart, format, shutdown, tasklist, taskkill, systeminfo, set, "
                     "setx, where, wmic, net, sc, schtasks, bcdedit, and the rest, with the command-line syntax "
                     "key. Most commands work the same in Windows 10 and 11 as in Windows Server."),
    dict(name="ms_windows_terminal", repo="MicrosoftDocs/terminal", branch="main", folders=["TerminalDocs"],
         includes=[], title="Windows Terminal documentation (Microsoft Learn)",
         subject="Windows (Windows Terminal)", source="https://learn.microsoft.com/windows/terminal/",
         description="Microsoft's documentation for Windows Terminal, every article: installing it, the command "
                     "palette, panes and tabs, profiles for Command Prompt, PowerShell and WSL Linux, settings, "
                     "actions and keyboard shortcuts, search and selection, command-line arguments, tips and "
                     "troubleshooting, and the Cascadia Code font."),
]
APPLE_BOOKS = [
    dict(name="swift_book", repo="swiftlang/swift-book", branch="main", licence_file="LICENSE.txt",
         folders=["TSPL.docc"], kind="docc", title="The Swift Programming Language", subject="Swift (programming "
         "language)", source="https://docs.swift.org/swift-book/",
         publisher="Apple Inc. and the Swift project authors (swift.org)",
         description="The official book on Swift, Apple's open-source programming language, in full: the guided "
                     "tour, the language guide (the basics, operators, strings, collections, control flow, "
                     "functions, closures, enumerations, structures and classes, properties, methods, inheritance, "
                     "initialization, optional chaining, error handling, concurrency, macros, type casting, "
                     "protocols, generics, opaque types, memory and access control) and the language reference."),
    dict(name="swift_org_docs", repo="swiftlang/swift-org-website", branch="main", licence_file="LICENSE.txt",
         folders=["documentation"], kind="jekyll", title="Swift.org documentation: API design guidelines, getting "
         "started, packages, servers and C++ interoperability", subject="Swift (programming language)",
         source="https://www.swift.org/documentation/", publisher="Apple Inc. and the Swift project authors "
         "(swift.org)", description="The documentation articles of swift.org, every one: the API design "
                                    "guidelines, getting started with Swift in editors and on Linux, Android and "
                                    "WebAssembly, the package manager, Swift on the server, C++ interoperability, "
                                    "concurrency, the core libraries, LLDB and continuous integration."),
]
BOOKS = MS_BOOKS + APPLE_BOOKS
BOOKS_BY_NAME = {b["name"]: b for b in BOOKS}


# ====================================================================== Markdown (DocFX, DocC, Jekyll) to HTML

FENCE = re.compile(r"^(\s*)(```+|~~~+)\s*([\w+#.-]*)[^\n]*\n(.*?)^\1\2\s*$", re.S | re.M)
INTERNAL = "https://book.invalid/"


def front_matter(text):
    """({field: value}, rest) of an article: the simple "name: value" lines of its front matter."""
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fields = {}
    for line in m.group(1).splitlines():
        f = re.match(r"^([A-Za-z_.]+):\s*(.*)$", line)
        if f and f.group(2).strip() not in ("", ">-", "|", ">"):
            fields[f.group(1)] = f.group(2).strip().strip("'\"")
    return fields, text[m.end():]


def ms_date(text):
    """"11/04/2025" or "2025-11-04" -> "2025-11-04" ("" when it is not a date)."""
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", (text or "").strip())
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", (text or "").strip())
    return m.group(0) if m else ""


def inline_includes(text, here, root, depth=0):
    """The text with DocFX includes ([!INCLUDE [x](path)]) and Jekyll include_relative tags replaced by the files'
    text (front matter removed), one level deep; a file that is not there is left out."""
    def load(rel):
        path = os.path.normpath(os.path.join(os.path.dirname(here), rel))
        if not path.startswith(os.path.normpath(root)) or not os.path.isfile(path) or depth > 1:
            return ""
        with open(path, encoding="utf-8", errors="replace") as f:
            return inline_includes(front_matter(f.read())[1], path, root, depth + 1)
    text = re.sub(r"\[!INCLUDE\s*\[[^\]]*\]\(([^)]+)\)\s*\]", lambda m: "\n" + load(m.group(1).strip()) + "\n", text,
                  flags=re.I)
    return re.sub(r"\{%\s*include_relative\s+([^\s%]+)\s*%\}", lambda m: "\n" + load(m.group(1)) + "\n", text)


def md_page(text, here, root, links, kind="docfx"):
    """(title, HTML) of one Markdown article at path here (inside root): its first heading (or front matter title)
    is the title, the rest becomes HTML. links: {absolute article path: page path} of the book."""
    import writing_business as W
    fields, body = front_matter(text)
    body = inline_includes(body.replace("\r", ""), here, root)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    codes = []

    def keep_code(m):
        codes.append(m.group(4).rstrip("\n"))
        return f"\n\x02{len(codes) - 1}\x03\n"
    body = FENCE.sub(keep_code, body)
    if kind == "docc":
        body = re.sub(r"^@\w+(?:\([^)]*\))?\s*\{.*?^\}\s*$", "", body, flags=re.S | re.M)   # @Metadata { } and such
        body = re.sub(r"``([^`]+)``", r"`\1`", body)
    title = fields.get("title", "")
    m = re.search(r"^#\s+(.+?)\s*#*\s*$", body, re.M)
    if m:
        title = title or m.group(1)
        body = body[:m.start()] + body[m.end():]
    title = re.sub(r"[`*]", "", html.unescape(title)).strip()

    def picture(m):
        alt = re.search(r'alt-text="([^"]*)"', m.group(0))
        return f"(Picture: {alt.group(1)})" if alt and alt.group(1).strip() else ""
    body = re.sub(r":::image\b.*?:::(?:\s*:::image-end:::)?", picture, body, flags=re.S)
    body = re.sub(r"^\s*:::.*$|^\s*>\s*\[!div[^\]]*\]\s*$", "", body, flags=re.M)        # zones, rows, monikers
    body = re.sub(r"^(\s*>\s*)\[!(NOTE|TIP|IMPORTANT|CAUTION|WARNING)\]\s*$",
                  lambda m: f"{m.group(1)}**{m.group(2).capitalize()}:**", body, flags=re.M)

    def target(m):
        label, href = m.group(1), m.group(2).strip()
        if kind == "docc" and href.startswith("doc:"):          # a DocC link names an article, wherever it is
            name, _, frag = href[4:].partition("#")
            page = links.get("doc:" + name)
            return f"[{label}]({INTERNAL}{page}{'#' + frag if frag else ''})" if page else label
        if re.match(r"^[a-z]+:", href) or href.startswith("#"):
            return m.group(0)
        if href.startswith("/"):
            site = {"docfx": "https://learn.microsoft.com", "jekyll": "https://www.swift.org"}.get(kind)
            return f"[{label}]({site}{href})" if site else label
        path, _, frag = href.partition("#")
        path = path.split("?")[0]
        absolute = os.path.normpath(os.path.join(os.path.dirname(here), path)) if path else here
        page = links.get(absolute) or links.get(absolute + ".md")
        return f"[{label}]({INTERNAL}{page}{'#' + frag if frag else ''})" if page else label
    body = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", target, body)
    if kind == "docc":
        def doc_link(m):
            words = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", m.group(1))        # "TheBasics" -> "The Basics"
            fake = re.match(r"\[(.*)\]\((.*)\)", f"[{words}](doc:{m.group(1)}{'#' + m.group(2) if m.group(2) else ''})")
            return target(fake)
        body = re.sub(r"<doc:([\w-]+)(?:#([\w-]+))?>", doc_link, body)
    out = W.md_html(body)
    out = out.replace(f'href="{INTERNAL}', 'href="')

    def code_html(m):
        return f"<pre><code>{html.escape(codes[int(m.group(1))])}</code></pre>"
    out = re.sub(r"<p>\s*\x02(\d+)\x03\s*</p>", code_html, out)
    out = re.sub(r"\x02(\d+)\x03", code_html, out)
    return title, out


# ====================================================================== the books

def lts_version(clone):
    """The current long-term-support PowerShell version ("7.6") from the repository's support-lifecycle article,
    else the newest numbered reference folder but one (the newest is the preview)."""
    article = os.path.join(clone, "reference", "docs-conceptual", "install", "PowerShell-Support-Lifecycle.md")
    if os.path.isfile(article):
        with open(article, encoding="utf-8", errors="replace") as f:
            m = re.search(r"current LTS release is PowerShell (\d+\.\d+)", f.read())
        if m and os.path.isdir(os.path.join(clone, "reference", m.group(1))):
            return m.group(1)
    versions = sorted((d for d in os.listdir(os.path.join(clone, "reference")) if re.fullmatch(r"\d+\.\d+", d)),
                      key=lambda v: tuple(int(x) for x in v.split(".")))
    return versions[-2] if len(versions) > 1 else versions[-1]


def articles(clone, folders, kind):
    """[(unit, absolute path)] of the Markdown articles in folders, in order: DocC by the book's own topic list,
    others by folder and name (index or overview articles first in their folder), partials ("_x.md") and
    include folders left out."""
    if kind == "docc":
        root = os.path.join(clone, folders[0])
        main = [f for f in os.listdir(root) if f.endswith(".md")]
        order, unit, out = [], "", []
        if main:
            with open(os.path.join(root, main[0]), encoding="utf-8") as f:
                for line in f:
                    h = re.match(r"^###\s+(.+)$", line)
                    if h:
                        unit = h.group(1).strip()
                    for name in re.findall(r"<doc:([\w-]+)>", line):
                        order.append((unit, name))
        found = {}
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                if f.endswith(".md"):
                    found.setdefault(f[:-3], os.path.join(dirpath, f))
        out = [(u, found[n]) for u, n in order if n in found]
        listed = {p for _u, p in out}
        out += [("More", p) for n, p in sorted(found.items()) if p not in listed and n != main[0][:-3]]
        return out
    out = []
    for folder in folders:
        root = os.path.join(clone, folder)
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = sorted(d for d in dirs if d not in ("includes", "media", "images", "breadcrumb", "bread"))
            rel = os.path.relpath(dirpath, root)
            unit_word = rel.split(os.sep)[0] if rel != "." else ""
            unit = re.sub(r"[-_]+", " ", unit_word).strip().capitalize() if unit_word else "Overview"
            names = sorted((f for f in files if f.endswith(".md") and not f.startswith("_") and
                            f.lower() not in ("readme.md", "toc.md", "contributing.md")),
                           key=lambda f: (f.lower() not in ("index.md", "overview.md"), f.lower()))
            out += [(unit, os.path.join(dirpath, f)) for f in names]
    return out


def doc_book(spec, work, cache=None, left_out=None, limit=None):
    """The Book of one spec of MS_BOOKS or APPLE_BOOKS: the repository's licence file checked (raw.githubusercontent
    .com), a shallow clone of its folders, every article a page."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    repo_url = f"https://github.com/{spec['repo']}"
    apple = spec in APPLE_BOOKS
    licence_url = f"https://raw.githubusercontent.com/{spec['repo']}/{spec['branch']}/" \
                  f"{spec.get('licence_file', 'LICENSE')}"
    try:
        licence_text = B.fetch(licence_url, cache) if R.readable(licence_url, cache) else ""
    except (urllib.error.URLError, OSError):
        licence_text = ""
    if not re.search(APACHE_TEXT if apple else MS_CC_TEXT, licence_text):
        left_out.append({"title": spec["title"], "reason": f"Its repository's licence file ({licence_url}) could not "
                         "be read or no longer states the licence that was checked."})
        return None
    kind = spec.get("kind", "docfx")
    patterns = []
    folders = list(spec["folders"])
    if any("{lts}" in f for f in folders):
        patterns.append("/reference/docs-conceptual/install/PowerShell-Support-Lifecycle.md")
        patterns += [f"/reference/{v}/**/*.md" for v in ("5.1", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9")]
    for folder in folders + spec.get("includes", []):
        if "{lts}" not in folder:
            patterns.append(f"/{folder}/**/*.md")
    clone = R.shallow_clone(repo_url, work, patterns, ref=spec["branch"])
    commit, commit_date = R.git_facts(clone)
    lts = lts_version(clone) if any("{lts}" in f for f in folders) else ""
    folders = [f.replace("{lts}", lts) for f in folders]
    title = spec["title"].replace("{lts}", lts)
    plan = articles(clone, folders, kind)
    if limit:
        plan = plan[:limit]
    paths, links = set(), {}
    for _unit, path in plan:
        rel = os.path.relpath(path, clone)
        page = B.slug(re.sub(r"\.md$", "", rel.replace(os.sep, "-")), 90)
        while page in paths:
            page += "-2"
        paths.add(page)
        links[os.path.normpath(path)] = page
        links[os.path.normpath(path)[:-3]] = page
        links["doc:" + os.path.basename(path)[:-3]] = page        # DocC's <doc:Name> links
    book = B.Book(name=spec["name"], title=title, subject=spec["subject"], level="reference", group=GROUP,
                  publisher=spec.get("publisher", MS), country="International", licence=APACHE if apple else CC_BY,
                  licence_url=APACHE_URL if apple else CC_BY_URL, source=spec["source"],
                  description=spec["description"].replace("{lts}", lts), notice=SWIFT_NOTICE if apple else MS_NOTICE)
    book.changes = "the Markdown articles converted to pages (pictures replaced by their descriptions)"
    units, dates = {}, []
    for unit, path in plan:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        fields, _ = front_matter(text)
        if fields.get("redirect_url") or fields.get("redirect_document_id"):
            continue
        ptitle, body = md_page(text, path, clone, links, "docc" if kind == "docc" else
                               ("jekyll" if kind == "jekyll" else "docfx"))
        if not R.page_text(body):
            continue
        n = units.setdefault(unit, len(units) + 1)
        date = ms_date(fields.get("ms.date", "") or fields.get("date", ""))
        dates.append(date)
        rel = os.path.relpath(path, clone).replace(os.sep, "/")
        head = f"<p>{'Updated ' + date + '. ' if date else ''}Source: {B.esc(spec['repo'])}, {B.esc(rel)}.</p>"
        book.pages.append(B.Page(links[os.path.normpath(path)], ptitle or os.path.basename(path)[:-3], head + body, n,
                                 unit))
    if apple:
        book.pages.append(B.Page("licence", "Licence: Apache License 2.0 with Runtime Library Exception",
                                 f"<pre>{B.esc(licence_text)}</pre>", len(units) + 1, "Licence"))
    today = datetime.date.today().isoformat()
    book.published = B.newest_date([d for d in dates if d and d <= today]) or commit_date
    book.version = f"{spec['repo']} commit {commit[:12]} of {commit_date}" + (f", PowerShell {lts}" if lts else "")
    book.originals = [{"url": repo_url, "kind": "html"}, {"url": licence_url, "kind": "txt"}]
    if not apple:
        book.originals.append({"url": f"https://raw.githubusercontent.com/{spec['repo']}/{spec['branch']}/"
                                      "LICENSE-CODE", "kind": "txt"})
    return book


# ====================================================================== keys, signs, the build

def all_keys():
    """Every build key of this module."""
    return [f"tech:{b['name']}" for b in BOOKS]


def knows(word):
    """True when word is one of this module's request words or keys."""
    return word in WORDS or word.startswith("tech:")


def expand_keys(words):
    """The keys the words stand for: "techdocs" or "group:techdocs" (every book), "tech:microsoft", "tech:apple", or
    one key (kept as it is)."""
    keys = []
    for w in words:
        if w in ("techdocs", f"group:{GROUP}"):
            keys += all_keys()
        elif w == "tech:microsoft":
            keys += [f"tech:{b['name']}" for b in MS_BOOKS]
        elif w == "tech:apple":
            keys += [f"tech:{b['name']}" for b in APPLE_BOOKS]
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change: the repository's newest commit ("" when it cannot be asked)."""
    import updates
    spec = BOOKS_BY_NAME.get(key.split(":", 1)[1] if ":" in key else "")
    return updates.git_head(f"https://github.com/{spec['repo']}") if spec else ""


def books_for(key, work, cache=None, left_out=None, limit=None):
    """The Books of one key (one book), or [] (the reason in left_out)."""
    left_out = left_out if left_out is not None else []
    spec = BOOKS_BY_NAME.get(key.split(":", 1)[1] if ":" in key else "")
    if spec is None:
        left_out.append({"title": key, "reason": "Unknown key."})
        return []
    book = doc_book(spec, work, cache, left_out, limit)
    return [book] if book is not None else []


def build(keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys into out_dir with one manifest per key (refs_common.build_keys)."""
    return R.build_keys(R._module("tech_kb"), keys, out_dir, cache, date, limit)  # (also when run as a script)


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "microsoftdocs_repositories": "github.com/MicrosoftDocs/PowerShell-Docs (LICENSE.md), SupportArticles-docs, "
                                  "microsoft-365-docs and windows-dev-docs (LICENSE), read 2026-11-22 and checked "
                                  "again at every build: \"Attribution 4.0 International\" (CC BY 4.0) for the "
                                  "documentation; LICENSE-CODE: the MIT licence for code samples. Read by shallow git "
                                  "clone; raw.githubusercontent.com has no robots rules.",
    "swift_repositories": "github.com/swiftlang/swift-book and swiftlang/swift-org-website LICENSE.txt (read "
                          "2026-11-22, checked at every build): Apache License, Version 2.0, with the Runtime "
                          "Library Exception; its text is a page of each book (section 4(a)).",
}

NOT_INCLUDED = [
    ("Microsoft Support articles (support.microsoft.com): the Complete Guide to Narrator, Windows and Office help, "
     "Microsoft accessibility support and the rest", "Copyrighted by Microsoft (its terms of use allow personal, "
     "non-commercial viewing only; there is no open licence and no public repository). For personal use, the "
     "owner's Program Downloader can read them. Index: https://support.microsoft.com/_sitemaps/sitemapindex.xml (the "
     "Narrator guide: https://support.microsoft.com/en-us/windows/complete-guide-to-narrator-e4397a0d-ef4f-b386-"
     "d8ae-c172f109bdb1; accessibility: https://support.microsoft.com/en-us/accessibility)"),
    ("Microsoft Learn pages whose source repositories are private: Windows client documentation for IT pros "
     "(windows-docs-pr), Microsoft Teams administration (OfficeDocs-SkypeForBusiness-pr) and the Learn accessibility "
     "hub", "Their pages name private repositories (checked 2026-11-22: \"original_content_git_url\" points at "
     "MicrosoftDocs/windows-docs-pr and OfficeDocs-SkypeForBusiness-pr, which cannot be read; the accessibility hub "
     "names none), so no open licence can be checked. Index for the Program Downloader: "
     "https://learn.microsoft.com/_sitemaps/sitemapindex.xml (https://learn.microsoft.com/windows/, "
     "https://learn.microsoft.com/microsoftteams/, https://learn.microsoft.com/accessibility/)"),
    ("Other MicrosoftDocs repositories (Azure, Dynamics 365, Power Platform, SQL Server, Intune, Visual Studio, "
     "Windows PowerShell modules for Windows Server, VBA, Edge developer docs)", "Open (CC BY 4.0) but left out for "
     "now as less useful to the owner than the books built; they can be added as more MS_BOOKS entries."),
    ("Apple Support articles and user guides (support.apple.com): the VoiceOver user guides for Mac, iPhone and iPad, "
     "the iPhone, iPad, Mac, Apple Watch and Apple TV user guides and the support articles", "Copyrighted by Apple "
     "(\"All rights reserved\"; no open licence). For personal use, the owner's Program Downloader can read them. "
     "Index: https://support.apple.com/en-us/sitemaps/sitemap-index-en-us.xml (the VoiceOver guide for Mac: "
     "https://support.apple.com/guide/voiceover/welcome/mac; the iPhone user guide: "
     "https://support.apple.com/guide/iphone/welcome/ios). Its robots.txt disallows /docs/product/ and the "
     "manuals' PDFs."),
    ("Apple Human Interface Guidelines and Apple Developer documentation (developer.apple.com)", "Copyrighted by "
     "Apple (developer.apple.com's terms; no open licence). Index: "
     "https://developer.apple.com/design/human-interface-guidelines and https://developer.apple.com/documentation/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["techdocs"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many articles")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
