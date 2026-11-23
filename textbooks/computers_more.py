"""Computers, phones and programming for the reference library: Linux and free-software manuals, programming books,
Windows command-line help, home networking, and a guide to everything the library has on computers and phones (the
owner's request of 2026-11-23). The books are in the group "Reference, computer help and technology" (techdocs, the
group of tech_kb.py). Keys: comp:<name>; request words (each at most 256 jobs):
  comp-linux             Linux and free software: the command line, Debian, FreeBSD, the GNU manuals
  comp-programming       programming: Python, JavaScript, Git, SQLite, Rust, Go
  comp-windows-basics    Windows and general PC skills (the Microsoft books of tech_kb.py and the pcb: books)
  comp-repair-network    home networking and routers (OpenWrt), electronics repair (elec:)
  comp-phones            phones: the guide's phone part and the privacy books on phones
  computers              every book above and the computer and phone basics, with the guide comp:index

What this module builds, in plain words, each IN FULL (every page of the guide, every node of the manual or the
whole PDF), with the licence each one states, checked again at every build:
  Open (permissive: the toolkit may share them freely, with credit):
    - Machtelt Garrels' Bash Guide for Beginners and Introduction to Linux (The Linux Documentation Project; a
      BSD-style licence, "Redistribution and use in source and binary forms, with or without modification, are
      permitted"), and Mendel Cooper's Advanced Bash-Scripting Guide ("granted to the Public Domain");
    - the FreeBSD Handbook (the FreeBSD Documentation License, a BSD-style licence);
    - the official Python documentation: the tutorial, the library reference, and the language reference, how-to
      guides, FAQs and "using Python" pages ("Python software and documentation are licensed under the Python
      Software Foundation License Version 2");
    - SQLite's documentation (its authors dedicated it to the public domain);
    - The Rust Programming Language (MIT or Apache 2.0, the book repository's two licence files);
    - the Go documentation: tutorials, Effective Go, the FAQ, modules, databases and the language specification
      (go.dev: "licensed under the Creative Commons Attribution 4.0 License").
  Share-alike (a book made from them keeps the licence; kept separate from the open books):
    - The Debian Administrator's Handbook (Raphael Hertzog and Roland Mas; offered under CC BY-SA 3.0 or the GNU GPL
      version 2 or later: the CC BY-SA choice is used);
    - the Debian Installation Guide for 64-bit PCs and Debian Reference (Osamu Aoki), both under the GNU GPL;
    - the GNU manuals of Bash, Coreutils, grep, sed and tar (the GNU Free Documentation License 1.3 or later), read
      from the Info files inside each program's official source package on ftp.gnu.org (www.gnu.org did not answer
      this build machine; ftp.gnu.org asks for 60 seconds between requests, which this module keeps);
    - the OpenWrt user guide (the router software's wiki; CC BY-SA 4.0).
  Personal use only (non-commercial licences; each marked so in its notice and in the catalogue):
    - The Linux Command Line by William Shotts (CC BY-NC-ND: whole and unchanged, the PDF read as it is, from its
      Internet Archive copy, since SourceForge's download page asks for a browser check);
    - Think Python, 2nd edition (Allen B. Downey, CC BY-NC 3.0), Automate the Boring Stuff with Python, 3rd edition
      (Al Sweigart, CC BY-NC-SA 3.0), Eloquent JavaScript, 4th edition (Marijn Haverbeke, CC BY-NC 3.0) and Pro Git,
      2nd edition (Scott Chacon and Ben Straub, CC BY-NC-SA 3.0).
  The guide comp:index (the toolkit's own facts and links, CC0): by theme, every book of the library on computers
  and phones, the Kiwix library's Stack Exchange and Wikibooks entries, and the sources that are links only.
Every book's notice ends with TECH_SAFETY and COMMAND_SAFETY (read a command before you run it as administrator).

Also added for this collection, in tech_kb.py (Microsoft's CC BY 4.0 repositories): tech:ms_windows_commands (every
command of the Windows command prompt) and tech:ms_windows_terminal.

Already in the library and not repeated: the LibreOffice guides, GNOME help and Library of Congress archiving
(pcb:, olife:), Microsoft's and Apple's open documentation (tech:), the GnuPG manual and the security guides
(privacy:), the ArchWiki's accessibility pages (a11yc:), W3C's accessibility tutorials (nonprofit:w3c_wai_tutorials),
electronics repair (elec:), the Open Textbook Library and LibreTexts' computing books (cat:otl, course:libretexts),
MDN Web Docs, Stack Exchange and Wikibooks (whole in the Kiwix library). Not built, with the reason and an address
(NOT_INCLUDED): Ubuntu's documentation, the Raspberry Pi documentation, The Linux Documentation Project's HOWTOs and
older guides, the Emacs manual, Microsoft's and Apple's and Google's own help sites, GCFGlobal, Cisco and CompTIA
courses, the FCC's consumer guides and Australia's Be Connected.

Run from the repository's folder:
  python3 textbooks/computers_more.py comp:python_tutorial --out build/textbooks --limit 3
  python3 textbooks/computers_more.py comp:gnu_sed_manual --out build/textbooks --limit 5
  python3 textbooks/computers_more.py --list computers
"""

import html
import io
import os
import re
import sys
import tarfile
import time
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import computer_basics as CB  # noqa: E402 - the computer safety note and the pcb: books
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "techdocs"
GROUPS = {GROUP: "Reference, computer help and technology"}

TECH_SAFETY = CB.TECH_SAFETY
COMMAND_SAFETY = ("Command line safety: a command run as administrator (sudo, su, or an elevated Command Prompt or "
                  "PowerShell) can delete files or change the whole system; read every command before you run it, "
                  "never paste one from a stranger, and keep a backup.")
SAFETY = f"{TECH_SAFETY} {COMMAND_SAFETY}"

# Licence names (the ones not already in sources.ALLOWED are added by ALLOWED below).
CC_BY = "CC BY 4.0"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"
CC_BY_SA_3 = "CC BY-SA 3.0"
CC_BY_SA_3_URL = "https://creativecommons.org/licenses/by-sa/3.0/"
CC_BY_SA_4 = "CC BY-SA 4.0"
CC_BY_SA_4_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
CC_BY_NC_3 = "CC BY-NC 3.0"
CC_BY_NC_3_URL = "https://creativecommons.org/licenses/by-nc/3.0/"
CC_BY_NC_SA_3 = "CC BY-NC-SA 3.0"
CC_BY_NC_SA_3_URL = "https://creativecommons.org/licenses/by-nc-sa/3.0/"
CC_BY_NC_ND_3 = "CC BY-NC-ND 3.0"
CC_BY_NC_ND_3_URL = "https://creativecommons.org/licenses/by-nc-nd/3.0/us/"
BSD3 = "BSD-3-Clause"
BSD3_URL = "https://opensource.org/license/bsd-3-clause"
PD_AUTHOR = "Public domain (dedicated by its authors)"
PSF = "PSF-2.0"
PSF_URL = "https://docs.python.org/3/license.html"
MIT_APACHE = "MIT OR Apache-2.0"
FREEBSD_DOC = "FreeBSD Documentation License"
FREEBSD_DOC_URL = "https://www.freebsd.org/copyright/freebsd-doc-license/"
GPL2 = "GPL-2.0"                          # the name at_docs.py adds to sources.ALLOWED (share-alike)
GPL2_URL = "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html"
GPL_DFSG = "GPL (any version compliant with the Debian Free Software Guidelines)"
GFDL = "GFDL-1.3-or-later"                # the name a11y_community.py adds to sources.ALLOWED (share-alike)
GFDL_URL = "https://www.gnu.org/licenses/fdl-1.3.html"
ALLOWED = {BSD3: "open", PD_AUTHOR: "open", PSF: "open", MIT_APACHE: "open", FREEBSD_DOC: "open",
           GPL_DFSG: "share-alike"}

PERSONAL = "Personal use only (a non-commercial licence)."
DOCBOOK = (r"(?si)<div\s+class=\"?navheader\"?\s*>.*?</div\s*>", r"(?i)<div\s+class=\"?navfooter\"?")
# DocBook pages (tldp.org, debian.org): the title from <title>, and the page's own first heading (in capitals on
# tldp.org, which the builder's lower-case rule misses) left out, as the page gets its own.
DOCBOOK_MORE = dict(content=DOCBOOK, title_from=r"(?i)<title\s*>(.*?)</title", drop=K.DROP + [r"(?i)<h1\b.*?</h1\s*>"])


def guide(name, title, subject, publisher, licence, licence_url, licence_page, licence_text, start, pages,
          description, notice, depth=1, follow=None, units=(), limit=300, urls=None, **more):
    """A web guide under an open, share-alike or non-commercial licence, read by crawling from start (or from the
    fixed list urls), its licence line checked on licence_page at every build; the notice ends with SAFETY."""
    starts = [start] if isinstance(start, str) else list(start)
    entry = dict(K.WEB, group=GROUP, name=name, title=title, subject=subject, publisher=publisher,
                 country="International", licence=licence, licence_url=licence_url, licence_page=licence_page,
                 licence_text=licence_text, source=starts[0], description=description, notice=f"{notice} {SAFETY}",
                 crawl=[(s, depth) for s in starts], follow=follow, pages=pages, unit_rules=list(units), limit=limit,
                 **more)
    if urls:
        entry["urls"] = list(urls)
    return entry


# ====================================================================== Linux and free software

TLDP = "https://tldp.org/LDP/"
GARRELS_TEXT = (r"Copyright \(c\) 2002-2007, Machtelt Garrels \* All rights reserved\. \* Redistribution and use in "
                r"source and binary forms, with or without \* modification, are permitted")
GARRELS_NOTICE = ("Copyright (c) 2002-2007, Machtelt Garrels. All rights reserved. Redistribution and use in source and "
                  "binary forms, with or without modification, are permitted under the BSD-style licence printed in "
                  "the guide's Copyright information page (kept in this book), provided this notice, the conditions "
                  "and the disclaimer are kept; the guide is offered \"as is\", without warranty. Converted to an "
                  "accessible format from The Linux Documentation Project's copy (tldp.org). Written in 2008: some "
                  "commands and programs have changed since; check your system's own manual pages (man).")

LINUX = [
    guide("tldp_bash_beginners", "Bash Guide for Beginners (Machtelt Garrels)", "The Bash shell (command line)",
          "Machtelt Garrels (The Linux Documentation Project)", BSD3, BSD3_URL,
          TLDP + "Bash-Beginners-Guide/html/intro_07.html", GARRELS_TEXT,
          TLDP + "Bash-Beginners-Guide/html/index.html",
          r"^https://tldp\.org/LDP/Bash-Beginners-Guide/html/[a-z0-9_]+\.html$",
          "A gentle course in the Bash shell and shell scripts, every page: Bash and its features, writing and "
          "debugging scripts, the Bash environment and variables, regular expressions, grep, sed and awk, "
          "conditional statements, interactive scripts, loops, variables and arrays, functions and signals, with "
          "exercises at the end of each chapter.", GARRELS_NOTICE, **DOCBOOK_MORE,
          units=[(r"/chap_0?[1-4]|/sect_0?[1-4]_", "Bash and scripts"), (r"/chap_0?[5-8]|/sect_0?[5-8]_",
                                                                         "Tools and decisions"),
                 (r"/chap_|/sect_", "Loops, functions and signals"), (r".", "About this guide")], limit=120),
    guide("tldp_intro_linux", "Introduction to Linux: a hands-on guide (Machtelt Garrels)", "Linux (beginners)",
          "Machtelt Garrels (The Linux Documentation Project)", BSD3, BSD3_URL,
          TLDP + "intro-linux/html/intro_07.html", GARRELS_TEXT, TLDP + "intro-linux/html/index.html",
          r"^https://tldp\.org/LDP/intro-linux/html/[a-z0-9_]+\.html$",
          "A hands-on introduction to Linux for new users, every page: what Linux is, logging in and quick start "
          "commands, files and the file system, permissions, processes, the boot process, I/O redirection, text "
          "editors (vi), the Bash environment, printers, fundamental backup techniques, networking, sound and video, "
          "X Window, and the glossary.", GARRELS_NOTICE, **DOCBOOK_MORE, limit=200),
    guide("tldp_advanced_bash_scripting", "Advanced Bash-Scripting Guide (Mendel Cooper)",
          "The Bash shell (scripting)", "Mendel Cooper (The Linux Documentation Project)", PD_AUTHOR,
          TLDP + "abs/html/index.html", TLDP + "abs/html/index.html",
          r"This document is herewith granted to the Public Domain\. No copyright!", TLDP + "abs/html/index.html",
          r"^https://tldp\.org/LDP/abs/html/[a-z0-9-]+\.html$",
          "The classic in-depth course on shell scripting, every page: special characters, variables and "
          "parameters, quoting, exit status, tests, operations, loops and branches, command substitution, "
          "arithmetic expansion, I/O redirection, here documents, subshells, functions, aliases, lists, arrays, "
          "regular expressions, the commands scripts use (external filters and utilities), debugging, options, "
          "gotchas, scripting with style, and hundreds of example scripts.",
          "By Mendel Cooper, from The Linux Documentation Project (tldp.org): \"This document is herewith granted "
          "to the Public Domain. No copyright!\" Converted to an accessible format. Version 10 (2014): some "
          "commands have changed since; check your system's own manual pages (man).", **DOCBOOK_MORE,
          units=[(r"/part1|/why-shell|/sha-bang", "Introduction"), (r".", "Chapters")], limit=420),
    guide("freebsd_handbook", "The FreeBSD Handbook", "FreeBSD (operating system)",
          "The FreeBSD Documentation Project", FREEBSD_DOC, FREEBSD_DOC_URL, FREEBSD_DOC_URL,
          r"Redistribution and use in source \(AsciiDoc\) and .compiled. forms \(HTML, PDF, EPUB and so forth\) with "
          r"or without modification, are permitted",
          "https://docs.freebsd.org/en/books/handbook/", r"^https://docs\.freebsd\.org/en/books/handbook/[a-z-]+/$",
          "The FreeBSD Project's own manual, every chapter: installing FreeBSD, UNIX basics, installing programs "
          "(packages and ports), the X Window System and Wayland, networking, desktop programs, multimedia, "
          "configuring the kernel, printing, Linux binary compatibility, WINE, configuration and tuning, booting, "
          "security, jails and containers, storage, GEOM, ZFS, other file systems, virtualization, updating "
          "FreeBSD, serial communications, PPP, email, network servers, firewalls, advanced networking, and the "
          "glossary.",
          "Copyright 1995-2026 The FreeBSD Documentation Project, under the FreeBSD Documentation License "
          "(https://www.freebsd.org/copyright/freebsd-doc-license/): redistribution with or without modification "
          "is permitted provided the copyright notice, conditions and disclaimer are kept; the documentation is "
          "provided \"as is\", without warranty. FreeBSD is a registered trademark of the FreeBSD Foundation; this "
          "copy is not endorsed by it.", depth=0,
          urls=[f"https://docs.freebsd.org/en/books/handbook/{c}/" for c in (
              "preface", "introduction", "bsdinstall", "basics", "ports", "wayland", "network", "desktop",
              "multimedia", "kernelconfig", "printing", "linuxemu", "wine", "config", "boot", "security", "jails",
              "containers", "mac", "audit", "disks", "geom", "zfs", "filesystems", "virtualization", "cutting-edge",
              "dtrace", "usb-device-mode", "serialcomms", "ppp-and-slip", "mail", "network-servers", "firewalls",
              "advanced-networking", "mirrors", "bibliography", "eresources", "glossary")],
          units=[(r"/(preface|introduction|bsdinstall|basics|ports|wayland|network)/", "Getting started"),
                 (r"/(desktop|multimedia|kernelconfig|printing|linuxemu|wine)/", "Common tasks"),
                 (r"/(config|boot|security|jails|containers|mac|audit|disks|geom|zfs|filesystems|virtualization|"
                  r"cutting-edge|dtrace|usb-device-mode)/", "System administration"),
                 (r"/(serialcomms|ppp-and-slip|mail|network-servers|firewalls|advanced-networking)/",
                  "Network communication"), (r".", "Appendices")], limit=45),
]

# The Debian books (share-alike).
DEBIAN_HANDBOOK = "https://debian-handbook.info/browse/stable/"
LINUX += [
    guide("debian_administrators_handbook", "The Debian Administrator's Handbook (Raphael Hertzog and Roland Mas)",
          "Debian Linux (running a system)", "Raphael Hertzog and Roland Mas (Freexian SARL)", CC_BY_SA_3,
          CC_BY_SA_3_URL, DEBIAN_HANDBOOK,
          r"This book is licensed under a Creative Commons Attribution-ShareAlike 3\.0 Unported License",
          DEBIAN_HANDBOOK, r"^https://debian-handbook\.info/browse/stable/[a-z0-9.-]+\.html$",
          "The full handbook for running a Debian system, every page of its online \"stable\" edition (written for "
          "Debian 11 \"Bullseye\" when checked on 2026-11-23; most of it applies to later Debian versions): the Debian project, a case study, installing "
          "Debian, after the first boot, the packaging system (dpkg) and APT, getting help, basic configuration "
          "(network, accounts, printing, the bootloader), Unix services, administration, network infrastructure "
          "and services (email, web, file sharing), workstations, security, advanced administration, "
          "virtualization, creating a Debian package, Kali Linux and other derivatives.",
          "The Debian Administrator's Handbook by Raphael Hertzog and Roland Mas (Copyright Freexian SARL), offered "
          "under two licences; this copy uses the Creative Commons Attribution-ShareAlike 3.0 Unported License "
          "(https://creativecommons.org/licenses/by-sa/3.0/): a book made from it keeps that licence. Converted to "
          "an accessible format.", content=(r"<div xml:lang=\"[A-Za-z-]+\" class=\"[a-z]+\" lang=\"[A-Za-z-]+\">", r"<ul class=\"docnav\">"),
          units=[(r"/(index|preface|foreword|sect\.who|sect\.selected|sect\.book|sect\.contrib|sect\.ackn)", "Preface"),
                 (r".", "Chapters")], limit=200),
    guide("debian_installation_guide", "Debian GNU/Linux Installation Guide (64-bit PC, amd64)",
          "Debian Linux (installing)", "The Debian Installer team", GPL2, GPL2_URL,
          "https://www.debian.org/releases/stable/amd64/index.en.html",
          r"This manual is free software; you may redistribute it and/or modify it under the terms of the GNU "
          r"General Public License",
          "https://www.debian.org/releases/stable/amd64/index.en.html",
          r"^https://www\.debian\.org/releases/stable/amd64/[a-z0-9]+\.en\.html$",
          "The official guide to installing the current stable Debian on a 64-bit PC, every page: welcome to Debian, "
          "system requirements, before installing, getting the installation media (USB sticks, network boot), "
          "booting the installer (including the speech-synthesized and braille installation for blind users), "
          "using the installer, booting into your new system, next steps, and the installation HOWTO, partitioning "
          "and preseeding appendices.",
          "The Debian GNU/Linux Installation Guide by the Debian Installer team: free software under the GNU General "
          "Public License (version 2, its Appendix F, kept in this book): a book made from it keeps that licence. "
          "Converted to an accessible format. Debian is a registered trademark of Software in the Public Interest, "
          "Inc.", **DOCBOOK_MORE,
          units=[(r"/index\.", "Contents"), (r"/pr\d", "Preface"), (r"/ch0?[1-3]", "Before installing"),
                 (r"/ch0?[4-6]", "Installing"), (r"/ch", "After installing"), (r".", "Appendices")], limit=120),
    guide("debian_reference", "Debian Reference (Osamu Aoki)", "Debian Linux (after installing)", "Osamu Aoki",
          GPL_DFSG, "https://www.debian.org/social_contract#guidelines",
          "https://www.debian.org/doc/manuals/debian-reference/index.en.html",
          r"This book is free; you may redistribute it and/or modify it under the terms of the GNU General Public "
          r"License of any version compliant to the Debian Free Software Guidelines",
          "https://www.debian.org/doc/manuals/debian-reference/index.en.html",
          r"^https://www\.debian\.org/doc/manuals/debian-reference/(pr|ch|ap)[0-9a-z]*\.en\.html$",
          "A broad overview of using and looking after a Debian system after installing, through shell commands, "
          "every chapter: GNU/Linux tutorials (the console, files, the shell, text processing), Debian package "
          "management, system initialization, authentication and access controls, network setup, network "
          "applications, the GUI system, I18N and L10N, system tips, data management (backup, encryption, "
          "storage), data conversion, programming, and the appendix.",
          "Debian Reference by Osamu Aoki (Copyright 2013-2024 Osamu Aoki): free under the GNU General Public "
          "License of any version compliant with the Debian Free Software Guidelines: a book made from it keeps "
          "that licence. Converted to an accessible format.", **DOCBOOK_MORE,
          units=[(r"/pr", "Preface"), (r"/ap", "Appendix"), (r".", "Chapters")], limit=20),
]

# ====================================================================== programming (open)

PY = "https://docs.python.org/3/"
PY_TEXT = r"Python software and documentation are licensed under the Python Software Foundation License Version 2"
PY_NOTICE = ("Copyright 2001 Python Software Foundation; all rights reserved. Python software and documentation are "
             "licensed under the Python Software Foundation License Version 2 (https://docs.python.org/3/license.html); "
             "the examples, recipes and other code in the documentation are also under the Zero-Clause BSD licence. "
             "Converted to an accessible format from docs.python.org (the current Python 3 version). \"Python\" is a "
             "registered trademark of the Python Software Foundation.")
PY_CONTENT = (r"<div class=\"body\" role=\"main\">", r"<div class=\"sphinxsidebar\"|<footer")
PY_DROP = K.DROP + [r"<a class=\"headerlink\".*?</a>"]


def python_book(name, title, subject, folders, description, limit):
    """One book of the Python documentation: the contents pages of folders (tutorial, library ...) and every page
    they list."""
    alt = "|".join(folders)
    return guide(name, title, subject, "Python Software Foundation", PSF, PSF_URL, PY + "license.html", PY_TEXT,
                 [f"{PY}{f}/index.html" for f in folders], rf"^https://docs\.python\.org/3/({alt})/[a-z0-9._-]+\.html$",
                 description, PY_NOTICE, content=PY_CONTENT, drop=PY_DROP,
                 title_from=r"<h1>(.*?)<a class=\"headerlink\"",
                 units=[(rf"/{f}/", f.capitalize()) for f in folders], limit=limit)


GO_TEXT = r"the contents of this site are licensed under the Creative Commons Attribution 4\.0 License"
PROGRAMMING = [
    python_book("python_tutorial", "The Python Tutorial (official Python documentation)", "Python (learning)",
                ["tutorial"], "The official Python tutorial, every page: whetting your appetite, using the "
                "interpreter, an informal introduction (numbers, text, lists), control flow, data structures, "
                "modules, input and output, errors and exceptions, classes, a tour of the standard library, virtual "
                "environments and packages, and floating-point arithmetic.", 30),
    python_book("python_library", "The Python Standard Library (official Python documentation)",
                "Python (reference)", ["library"], "The reference of Python's standard library, every page: "
                "built-in functions, types and exceptions, text processing, data types, numbers and maths, "
                "functional programming, files and directories, data persistence, compression, file formats, "
                "cryptography, the operating system, concurrency, networking, internet data, markup, internet "
                "protocols, multimedia, internationalization, graphical interfaces (tkinter), developer tools, "
                "debugging and profiling, packaging and the Python runtime.", 450),
    python_book("python_language_howto", "Python language reference, how-to guides, FAQs and setup (official "
                "Python documentation)", "Python (reference)", ["reference", "howto", "faq", "using"],
                "The rest of the official Python documentation for readers: the language reference (lexical "
                "analysis, the data model, execution, imports, expressions, statements), the HOWTO guides (sorting, "
                "logging, regular expressions, Unicode, sockets, argparse, descriptors and more), the FAQs (general, "
                "programming, design, library, extending, Windows, graphical interfaces) and Python setup and usage "
                "(the command line, Unix, Windows, macOS and editors).", 120),
    guide("sqlite_docs", "SQLite documentation: the SQL language, the command-line shell and the database",
          "SQLite (databases)", "The SQLite developers (D. Richard Hipp and others)", PD_AUTHOR,
          "https://www.sqlite.org/copyright.html", "https://www.sqlite.org/copyright.html",
          r"All of the code and documentation in SQLite has been dedicated to the public domain by the authors",
          "https://www.sqlite.org/lang.html",
          r"^https://www\.sqlite\.org/(lang[a-z_]*|quickstart|cli|datatype3|faq|about|features|whentouse|pragma|"
          r"json1|windowfunctions|foreignkeys|autoinc|nulls|quirks|different|rescode|limits|backup|wal|fts5|"
          r"csv|uri|stricttables|gencol|withoutrowid|rowvalue|partialindex|expridx|datatypes|lockingv3|"
          r"atomiccommit|howtocorrupt|isolation|optoverview|queryplanner|eqp|sqlanalyze|sqldiff)\.html$",
          "SQLite's own documentation of the small database built into phones, browsers and many programs, the "
          "pages for users: about SQLite, when to use it, the quick start, the command-line shell (sqlite3), the "
          "whole SQL language (every statement, expression and function, date and time, aggregate, window and "
          "maths functions, JSON), data types, PRAGMA statements, foreign keys, full-text search, write-ahead "
          "logging, backups, limits, result codes, how the query planner works, how transactions are made safe, "
          "the quirks and the FAQ.",
          "SQLite's code and documentation are in the public domain: \"All of the code and documentation in SQLite "
          "has been dedicated to the public domain by the authors\" (https://www.sqlite.org/copyright.html). "
          "Converted to an accessible format.", depth=1,
          urls=["https://www.sqlite.org/about.html", "https://www.sqlite.org/whentouse.html",
                "https://www.sqlite.org/quickstart.html", "https://www.sqlite.org/cli.html",
                "https://www.sqlite.org/datatype3.html", "https://www.sqlite.org/faq.html"],
          content=(r"<div class=\"fancy_title\">|<h1[^>]*>", r"</body>"),
          drop=K.DROP + [r"<div class=\"menu[^\"]*\".*?</div>", r"<div class=\"tagline[^\"]*\".*?</div>"],
          units=[(r"/lang", "The SQL language"), (r"/(cli|quickstart|about|whentouse|faq|features|different|quirks)\.",
                                                  "Getting started"), (r".", "Using the database")], limit=320),
    guide("rust_book", "The Rust Programming Language (the Rust Book)", "Rust (programming language)",
          "Steve Klabnik, Carol Nichols and Chris Krycho, with the Rust community", MIT_APACHE,
          "https://github.com/rust-lang/book", "https://raw.githubusercontent.com/rust-lang/book/main/LICENSE-MIT",
          r"Permission is hereby granted, free of charge, to any person obtaining a copy",
          "https://doc.rust-lang.org/book/toc.html", r"^https://doc\.rust-lang\.org/book/(?!toc\.|print\.)[a-z0-9-]+\.html$",
          "The official book on the Rust programming language, every chapter: getting started with Cargo, a "
          "guessing game, common programming concepts, ownership, structs, enums and pattern matching, packages "
          "and modules, collections, error handling, generics, traits and lifetimes, testing, a command-line "
          "program, closures and iterators, smart pointers, concurrency, async, object-oriented features, "
          "patterns, advanced features, a web server project, and the appendices.",
          "The Rust Programming Language by Steve Klabnik, Carol Nichols and Chris Krycho with contributions from "
          "the Rust community, under the MIT licence or the Apache License 2.0, at your option (the book "
          "repository's LICENSE-MIT and LICENSE-APACHE: \"Copyright (c) 2010 The Rust Project Developers\"). "
          "Converted to an accessible format. Rust is a trademark of the Rust Foundation.",
          title_from=r"<main>\s*<h[12][^>]*>(.*?)</h[12]>",
          units=[(r"/(title-page|foreword|ch00)", "Introduction"), (r"/appendix", "Appendices"),
                 (r".", "Chapters")], limit=130),
    guide("go_docs", "Go documentation: tutorials, Effective Go, the FAQ and the language specification",
          "Go (programming language)", "The Go Authors (go.dev)", CC_BY, CC_BY_URL, "https://go.dev/copyright", GO_TEXT,
          "https://go.dev/doc",          # without its last "/", so the crawler does not add one to every link
          r"^https://go\.dev/(doc/(install|tutorial/[a-z-]+(\.html)?|effective_go|code\.html|faq|cmd|comment|"
          r"editors\.html|diagnostics\.html|gc-guide|modules/[a-z-]+|database/[a-z-]+|articles/wiki/)|"
          r"ref/(spec|mod|mem))$",
          "The Go project's documentation for learning and using Go, every page listed: installing Go, the "
          "tutorials (getting started, creating a module, workspaces, a web service, generics, fuzzing, database "
          "access), How to Write Go Code, Effective Go, the FAQ, the go command, doc comments, editors, "
          "diagnostics and the garbage collector guide, modules (managing dependencies, developing and publishing, "
          "the go.mod reference), accessing databases, and the language specification and memory model.",
          "From go.dev, by the Go Authors: \"Except as noted, the contents of this site are licensed under the "
          "Creative Commons Attribution 4.0 License, and code is licensed under a BSD license\". Converted to an "
          "accessible format. Go and the Go gopher are trademarks of Google LLC.",
          units=[(r"/tutorial/|/install|/code\.html|/articles/", "Tutorials"), (r"/ref/", "Reference"),
                 (r"/modules/", "Modules"), (r"/database/", "Databases"), (r".", "Guides")], limit=80),
]

# ====================================================================== programming (personal use)

PROGRAMMING += [
    guide("think_python_2e", "Think Python, 2nd edition: How to Think Like a Computer Scientist (Allen B. Downey)",
          "Python (learning)", "Allen B. Downey (Green Tea Press)", CC_BY_NC_3, CC_BY_NC_3_URL,
          "https://greenteapress.com/wp/think-python-2e/",
          r"It is available under the Creative Commons Attribution-NonCommercial 3\.0 Unported License",
          "https://greenteapress.com/thinkpython2/html/index.html",
          r"^https://greenteapress\.com/thinkpython2/html/thinkpython20\d\d\.html$",
          "A beginner's introduction to programming with Python 3, every chapter: the way of the program, "
          "variables and expressions, functions, a turtle case study, conditionals and recursion, fruitful "
          "functions, iteration, strings, word play, lists, dictionaries, tuples, data structure selection, files, "
          "classes and objects, functions and methods, inheritance, the goodies, debugging and the analysis of "
          "algorithms.", f"{PERSONAL} Think Python, 2nd edition, by Allen B. Downey (Green Tea Press), under the "
          "Creative Commons Attribution-NonCommercial 3.0 Unported License (https://creativecommons.org/licenses/"
          "by-nc/3.0/): not for commercial use. Converted to an accessible format.",
          content=(r"Buy this book at Amazon\.com</a>", r"<div id=\"ea-slot\"|<hr>\s*<a href=\"thinkpython2\d+\.html\""),
          units=[(r"thinkpython200[01]\.", "Preface"), (r"thinkpython20(0[2-9]|1\d)\.", "Chapters"),
                 (r".", "Appendices and index")],
          personal_use=True, limit=30),
    guide("automate_boring_stuff_3e", "Automate the Boring Stuff with Python, 3rd edition (Al Sweigart)",
          "Python (practical tasks)", "Al Sweigart", CC_BY_NC_SA_3, CC_BY_NC_SA_3_URL,
          "https://automatetheboringstuff.com/", r"Free to read under a Creative Commons license",
          "https://automatetheboringstuff.com/", r"^https://automatetheboringstuff\.com/3e/(chapter\d+|appendix[a-z])"
                                                r"\.html$",
          "Practical programming for total beginners, every chapter: Python basics, flow control, loops, "
          "functions, debugging, lists, dictionaries, strings, text pattern matching with regular expressions, "
          "reading and writing files, organizing files, designing and deploying command-line programs, web "
          "scraping, Excel, Google Sheets, SQLite databases, PDF and Word documents, CSV, JSON and XML, keeping "
          "time and scheduling tasks, sending email and texts, images, recognizing text in images, controlling "
          "the keyboard and mouse, text-to-speech and speech recognition, with the appendices on installing "
          "packages and running programs.",
          f"{PERSONAL} Automate the Boring Stuff with Python, 3rd edition, by Al Sweigart, free to read under a "
          "Creative Commons licence (the site's link: Attribution-NonCommercial-ShareAlike 3.0, https://"
          "creativecommons.org/licenses/by-nc-sa/3.0/): not for commercial use, and a book made from it keeps that "
          "licence. Converted to an accessible format; the site's notices of the printed book left out.",
          content=(r"<div type=\"frontmatter\"[^>]*>|<div type=\"bodymatter\"[^>]*>", r"</body>"),
          title_from=r"<title>(.*?)(?:, Automate the Boring Stuff with Python, 3rd Ed)?</title>",
          units=[(r"/chapter(\d|1[0-2])\.", "Part I: Programming basics"), (r"/chapter\d+\.",
                                                                          "Part II: Automating tasks"),
                 (r".", "Appendices")],
          drop=K.DROP + [r"<div style=\"border: 1px solid black; padding: 5px;\" id=\"closeable_ad_bar2?\">.*?</div>"],
          personal_use=True, limit=30),
    guide("eloquent_javascript_4e", "Eloquent JavaScript, 4th edition (Marijn Haverbeke)", "JavaScript (learning)",
          "Marijn Haverbeke", CC_BY_NC_3, CC_BY_NC_3_URL, "https://eloquentjavascript.net/",
          r"Licensed under a Creative Commons attribution-noncommercial license",
          "https://eloquentjavascript.net/", r"^https://eloquentjavascript\.net/\d\d_[a-z_]+\.html$",
          "A book about JavaScript, programming and the web, every chapter: values, types and operators, program "
          "structure, functions, data structures, higher-order functions, objects, a robot project, bugs and "
          "errors, regular expressions, modules, asynchronous programming, a programming language project, "
          "JavaScript and the browser, the document object model, handling events, a platform game, drawing on "
          "canvas, HTTP and forms, a pixel art editor, Node.js and a skill-sharing website.",
          f"{PERSONAL} Eloquent JavaScript, 4th edition (2024), by Marijn Haverbeke, licensed under a Creative "
          "Commons Attribution-NonCommercial license (https://creativecommons.org/licenses/by-nc/3.0/): not for "
          "commercial use; the code in the book may also be used under the MIT licence. Converted to an accessible "
          "format; the illustrations, by other artists, are described only by their captions.",
          content=(r"<article>", r"</article>"), personal_use=True,
          units=[(r"/0\d_|/1[0-2]_", "Language"), (r"/1[3-9]_", "Browser"), (r"/2\d_", "Node")], limit=30),
    guide("pro_git_2e", "Pro Git, 2nd edition (Scott Chacon and Ben Straub)", "Git (version control)",
          "Scott Chacon and Ben Straub (Apress), with contributors", CC_BY_NC_SA_3, CC_BY_NC_SA_3_URL,
          "https://git-scm.com/book/en/v2",
          r"All content is licensed under the Creative Commons Attribution Non Commercial Share Alike 3\.0 license",
          "https://git-scm.com/book/en/v2", r"^https://git-scm\.com/book/en/v2/[A-Z][A-Za-z0-9%-]+$",
          "The whole book on Git, the version control system: getting started and installing, Git basics "
          "(recording changes, history, undoing, remotes, tags), branching and merging, Git on the server, "
          "distributed workflows, GitHub, Git tools (stashing, searching, rewriting history, submodules), "
          "customizing Git, Git and other systems, Git internals, and the appendices on Git in other environments, "
          "embedding Git and the Git commands.",
          f"{PERSONAL} Pro Git, 2nd edition, by Scott Chacon and Ben Straub (Apress), the version on git-scm.com "
          "with its contributors' corrections, licensed under the Creative Commons Attribution Non Commercial "
          "Share Alike 3.0 license (https://creativecommons.org/licenses/by-nc-sa/3.0/): not for commercial use, "
          "and a book made from it keeps that licence. Converted to an accessible format.",
          content=(r"<div id=\"main\"[^>]*>", r"<div id=\"nav\">"), personal_use=True,
          units=[(r"/v2/Getting-Started", "Getting started"), (r"/v2/Git-Basics", "Git basics"),
                 (r"/v2/Git-Branching", "Branching"), (r"/v2/Git-on-the-Server", "Git on the server"),
                 (r"/v2/Distributed-Git", "Distributed Git"), (r"/v2/GitHub", "GitHub"),
                 (r"/v2/Git-Tools", "Git tools"), (r"/v2/Customizing-Git", "Customizing Git"),
                 (r"/v2/Git-and-Other", "Git and other systems"), (r"/v2/Git-Internals", "Git internals"),
                 (r".", "Appendices")], limit=120),
]

# The Linux Command Line: a whole PDF under a no-derivatives licence, kept whole and unchanged (personal use).
LINUX_PDFS = [
    dict(group=GROUP, name="linux_command_line", title="The Linux Command Line, Seventh Internet Edition "
         "(William Shotts)", subject="The Linux command line (beginners)", publisher="William E. Shotts, Jr. "
         "(LinuxCommand.org)", archive="the-linux-command-line-7th-internet-edition", country="International",
         licence=CC_BY_NC_ND_3, licence_url=CC_BY_NC_ND_3_URL, unchanged=True, personal_use=True,
         licence_page="https://linuxcommand.org/tlcl.php",
         licence_text=r"Released under a BY-NC-ND Creative Commons license",
         pdf_licence_text=r"(?i)licensed under the Creative Commons Attribution.?\s*Non\s*-?\s*commercial-No Derivative "
                          r"Works 3\.0 United States License",
         level="reference", version="Seventh Internet Edition, release 25.12A", published="2026-07-18",
         description="The complete beginner's book on the Linux command line and shell scripting, whole: what the "
                     "shell is, navigating the file system, exploring the system, manipulating files and "
                     "directories, working with commands, redirection, seeing the world as the shell sees it, "
                     "keyboard tricks, permissions, processes, the environment, the vi editor, customizing the "
                     "prompt, package management, storage media, networking, searching for files, archiving and "
                     "backup, regular expressions, text processing, formatting output, printing, compiling "
                     "programs, and writing shell scripts from the first one to arrays and exotica.",
         notice=f"{PERSONAL} The Linux Command Line by William E. Shotts, Jr., released under the Creative Commons "
                "Attribution-Noncommercial-No Derivative Works 3.0 United States License (https://creativecommons.org/"
                "licenses/by-nc-nd/3.0/us/, as the book's copyright page says; linuxcommand.org/tlcl.php: \"BY-NC-ND\"): not for commercial use and no "
                "changes allowed, so the PDF is kept whole and its text unchanged; only its format is converted. "
                "Read from the Internet Archive's copy of the author's PDF (release 25.12A), because SourceForge's "
                "download page asks for a browser check. " + SAFETY,
         changes="its text made into web pages, one per chapter, the text unchanged"),
]

# ====================================================================== GNU manuals (Info files from ftp.gnu.org)

GNU_FTP = "https://ftp.gnu.org/gnu/"
GNU_WAIT = 61.0                         # ftp.gnu.org/robots.txt: "Crawl-delay: 60"
GNU_LICENCE_TEXT = (r"Permission is granted to copy, distribute and/or modify this document under the terms of the "
                    r"GNU Free Documentation License, Version 1\.3 or any later version")
GNU_NOTICE = ("Copyright Free Software Foundation, Inc. \"Permission is granted to copy, distribute and/or modify this "
              "document under the terms of the GNU Free Documentation License, Version 1.3 or any later version "
              "published by the Free Software Foundation\" (with the manual's own invariant sections and cover "
              "texts, if any, as its first page says); the licence's full text is the book's page \"GNU Free "
              "Documentation License\". A book made from it keeps that licence. Converted from the Info file in the "
              "program's official source package on ftp.gnu.org to web pages, one per Info node; the text is "
              "otherwise unchanged.")
# (name, package, info file inside the package, title, subject, description)
GNU_MANUALS = [
    ("gnu_bash_manual", "bash", "bashref.info", "The GNU Bash Reference Manual", "The Bash shell (reference)",
     "The official manual of Bash, the shell of most Linux systems and of macOS's Terminal before zsh, every "
     "section: shell syntax, quoting, commands, functions, parameters and expansions, redirections, executing "
     "commands, shell scripts, the builtin commands, shell variables, Bash features (startup files, interactive "
     "shells, conditional expressions, arithmetic, aliases, arrays, the prompt), job control, command line "
     "editing (Readline) and history."),
    ("gnu_coreutils_manual", "coreutils", "coreutils.info", "GNU Coreutils: the core file, text and shell utilities",
     "Linux commands (reference)",
     "The manual of the core commands every Linux system has, every section: ls, cp, mv, rm, mkdir, ln, chmod, "
     "chown, touch, cat, head, tail, sort, uniq, wc, cut, tr, split, df, du, date, echo, printf, test, sleep, "
     "env, md5sum and sha256sum, and the rest, with the common options and how file permissions and dates are "
     "written."),
    ("gnu_grep_manual", "grep", "grep.info", "GNU grep: searching text with patterns", "Linux commands (searching)",
     "The manual of grep, the command that finds lines matching a pattern, every section: invoking grep, its "
     "options, environment variables, exit status, regular expressions (basic and extended), usage examples "
     "and performance."),
    ("gnu_sed_manual", "sed", "sed.info", "GNU sed: a stream editor", "Linux commands (editing text)",
     "The manual of sed, the command that edits text as it streams past, every section: running sed, sed "
     "scripts and commands, regular expressions, advanced sed (cycles and buffers), sample scripts and reporting "
     "bugs."),
    ("gnu_tar_manual", "tar", "tar.info", "GNU tar: an archiver tool", "Linux commands (archives and backups)",
     "The manual of tar, the command that packs files into one archive and unpacks them, every section: a "
     "tutorial, invoking tar, the operations, choosing files and names, compressing (gzip, bzip2, xz), backups "
     "and incremental dumps, archive formats, tapes and media, and reliability and security."),
]


def gnu_entry(name):
    """The GNU_MANUALS row of a key's name, as a dict."""
    for row in GNU_MANUALS:
        if row[0] == name:
            return dict(zip(("name", "package", "info", "title", "subject", "description"), row))
    raise KeyError(name)


_gnu_last = [0.0]


def gnu_wait():
    """Wait until GNU_WAIT seconds have passed since the last request to ftp.gnu.org (its robots.txt asks for a
    crawl delay of 60 seconds)."""
    wait = GNU_WAIT - (time.monotonic() - _gnu_last[0])
    if _gnu_last[0] and wait > 0:
        time.sleep(wait)
    _gnu_last[0] = time.monotonic()


def newest_tarball(listing, package):
    """The file name of the newest source package of package in an ftp.gnu.org folder listing ("" when none):
    the highest version, .tar.xz preferred to .tar.gz."""
    found = set(re.findall(rf'href="({re.escape(package)}-(\d+(?:\.\d+)*)\.tar\.(?:xz|gz))"', listing))
    if not found:
        return ""

    def order(item):
        """(version numbers, xz before gz) of one file."""
        return tuple(int(x) for x in item[1].split(".")), item[0].endswith(".xz")
    return max(found, key=order)[0]


def gnu_listing(package):
    """The ftp.gnu.org folder listing of package (fresh, paced)."""
    import build_textbooks as B
    gnu_wait()
    return B.fetch(f"{GNU_FTP}{package}/", None)


def info_files(tar_path, info):
    """The text of the Info manual info inside a source package (its doc/ folder), its split parts (info-1,
    info-2 ...) joined in order; "" when the package has none."""
    parts = {}
    with tarfile.open(tar_path) as tf:
        for member in tf.getmembers():
            m = re.search(rf"/doc/{re.escape(info)}(?:-(\d+))?$", member.name)
            if m and member.isfile():
                parts[int(m.group(1) or 0)] = tf.extractfile(member).read().decode("utf-8", "replace")
    return "".join(parts[k] for k in sorted(parts))


NODE_HEAD = re.compile(r"^\s*File: [^,]+,\s+Node: ([^,\n]+)(?:,[^\n]*?\bUp: ([^,\n]+))?[^\n]*\n")


def info_nodes(text):
    """[(node name, up node name, body text)] of an Info manual's text, in order; the tag table, the indirect
    table and the index nodes (which list page numbers of the printed manual) are left out."""
    nodes = []
    for chunk in text.split("\x1f"):
        m = NODE_HEAD.match(chunk)
        if not m:
            continue
        body = chunk[m.end():]
        if "\x00\x08[index\x00\x08]" in body:
            continue
        nodes.append((m.group(1).strip(), (m.group(2) or "").strip(), body))
    return nodes


def node_slug(name):
    """The page name of an Info node ("Shell Syntax" -> "node-shell-syntax")."""
    import build_textbooks as B
    return "node-" + B.slug(name, 70)


UNDERLINE = re.compile(r"^([*=\-.])\1{2,}\s*$")


def info_html(body, names):
    """HTML of one Info node's text: underlined lines become headings, menus become lists of links to their nodes,
    "*Note X::" cross references become links, indented blocks (examples) stay preformatted, the rest are
    paragraphs. names: the node names of the manual (links only to these)."""
    import build_textbooks as B

    def link(name, words=None):
        """A link to a node of this manual (or the words alone when it is not one)."""
        name = " ".join(name.split())
        words = " ".join((words or name).split())
        return f'<a href="{node_slug(name)}">{B.esc(words)}</a>' if name in names else B.esc(words)

    def inline(text):
        """Paragraph text with its cross references made into links."""
        out, last = [], 0
        for m in re.finditer(r"\*[Nn]ote\s+([^:]+?)::|\*[Nn]ote\s+([^:]+?):\s*([^.,]+?)[.,]", text):
            out.append(B.esc(text[last:m.start()]))
            out.append("see " + (link(m.group(1)) if m.group(1) else link(m.group(3), m.group(2))))
            last = m.end()
        out.append(B.esc(text[last:]))
        return "".join(out)

    lines = body.replace("\r", "").split("\n")
    blocks, cur = [], []
    for line in lines:
        if line.strip():
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    out = []
    for block in blocks:
        if len(block) == 2 and UNDERLINE.match(block[1]):
            level = {"*": 2, "=": 2, "-": 3, ".": 4}[block[1].strip()[0]]
            out.append(f"<h{level}>{B.esc(block[0].strip())}</h{level}>")
            continue
        if block[0].startswith("* Menu:") or (block[0].startswith("* ") and re.match(r"^\* [^:]+::", block[0])):
            items = []                           # [[link HTML, description words]]
            for line in block:
                if line.startswith("* Menu:"):
                    continue
                short = re.match(r"^\* ([^:]+)::\s*(.*)$", line)           # "* Node::  what it is"
                named = re.match(r"^\* ([^:]+):\s*([^.,\t]+)[.,\t]\s*(.*)$", line)   # "* Words: Node.  what"
                if short:
                    items.append([link(short.group(1)), short.group(2)])
                elif named:
                    items.append([link(named.group(2), named.group(1)), named.group(3)])
                elif items and line[:1].isspace():
                    items[-1][1] += " " + line.strip()
                elif line.strip():
                    items.append(["", line.strip()])             # a heading line inside the menu
            if items:
                out.append("<ul>" + "".join(f"<li>{a}{' ' if a and d.strip() else ''}{B.esc(' '.join(d.split()))}"
                                            "</li>" for a, d in items) + "</ul>")
            continue
        if all(x.startswith("     ") or x.startswith("\t") for x in block):
            pad = min(len(x) - len(x.lstrip(" ")) for x in block if not x.startswith("\t"))
            pad = pad if any(not x.startswith("\t") for x in block) else 0
            out.append("<pre>" + B.esc("\n".join(x[pad:] if x.startswith(" " * pad) else x for x in block)) +
                       "</pre>")
            continue
        out.append("<p>" + inline(" ".join(x.strip() for x in block)) + "</p>")
    return "".join(out)


def gnu_book(name, work, cache=None, left_out=None, limit=None):
    """comp:gnu_<program>_manual: the newest source package of the program from ftp.gnu.org (60 seconds between
    requests), the Info manual inside it, its licence line checked in its own front matter, one page per node
    (grouped by chapter, the nodes directly under Top)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    e = gnu_entry(name)
    folder = f"{GNU_FTP}{e['package']}/"
    if not K.readable(folder, cache):
        left_out.append({"title": e["title"], "reason": "ftp.gnu.org's robots.txt does not allow reading it now."})
        return None
    tarball = newest_tarball(gnu_listing(e["package"]), e["package"])
    if not tarball:
        left_out.append({"title": e["title"], "reason": f"No source package was found in {folder}."})
        return None
    gnu_wait()
    path = K.download_file(folder + tarball, cache, name=tarball)
    text = info_files(path, e["info"])
    front = " ".join(text.split("\x1f", 1)[0].split())
    if not text or not re.search(GNU_LICENCE_TEXT, front):
        left_out.append({"title": e["title"], "reason": f"The Info manual of {tarball} no longer states the licence "
                         "that was checked (GNU Free Documentation License 1.3 or later)."})
        return None
    version = re.sub(r"\.tar\.(xz|gz)$", "", tarball)
    book = K.new_book(f"comp_{name}", e["title"], e["subject"], GROUP, "Free Software Foundation (the GNU Project)",
                      GFDL, GFDL_URL, folder, e["description"], f"{GNU_NOTICE} {SAFETY}", country="International",
                      changes="the Info manual's nodes made into web pages; menus and cross references made into "
                              "links; the text otherwise unchanged")
    nodes = info_nodes(text)
    names = {n for n, _up, _b in nodes}
    ups = {n: up for n, up, _b in nodes}

    def chapter(node):
        """The chapter of a node: its ancestor directly under Top."""
        seen = set()
        while ups.get(node) and ups[node] not in ("Top", "(dir)") and node not in seen:
            seen.add(node)
            node = ups[node]
        return "Introduction" if node == "Top" else node
    units = {}
    book.pages.append(B.Page("licence-of-this-manual", "About this manual and its licence",
                             K.text_html(text.split("\x1f", 1)[0].split("INFO-DIR-SECTION")[0]), 0, "About"))
    for node, _up, body in nodes:
        if limit and len(book.pages) >= limit:
            break
        unit = chapter(node)
        n = units.setdefault(unit, len(units) + 1)
        book.pages.append(B.Page(node_slug(node), node, info_html(body, names), n, unit))
    book.version = f"{version} (the Info manual of the source package)"
    book.published = K.last_modified(folder + tarball) if not limit else ""
    book.originals = [{"url": folder + tarball, "kind": "gz" if tarball.endswith(".gz") else "html"}]
    return book


def gnu_sign(name):
    """The weekly sign of a GNU manual: the name of the program's newest source package."""
    return newest_tarball(gnu_listing(gnu_entry(name)["package"]), gnu_entry(name)["package"])


# ====================================================================== networking (share-alike)

OPENWRT = "https://openwrt.org/"
NETWORK = [
    guide("openwrt_user_guide", "OpenWrt user guide: free router software", "Home networking and routers (OpenWrt)",
          "The OpenWrt Project and its wiki contributors", CC_BY_SA_4, CC_BY_SA_4_URL, OPENWRT + "license",
          r"Except where otherwise noted, content on this wiki is licensed under the following license: CC "
          r"Attribution-Share Alike 4\.0 International",
          [OPENWRT + "docs/guide-quick-start/start", OPENWRT + "docs/guide-user/start"],
          r"^https://openwrt\.org/docs/(guide-quick-start|guide-user)/[a-z0-9_.:/-]+$",
          "The OpenWrt wiki's quick start and user guide pages linked from its contents: what OpenWrt is, "
          "checking your router is supported, installing and upgrading OpenWrt, the first login and the LuCI web "
          "interface, the basic configuration of the network, Wi-Fi, firewall and DHCP, adding packages, "
          "storage and USB, network services (DNS, VPN, file sharing), troubleshooting and recovering a router "
          "that does not start (failsafe mode).",
          "From the OpenWrt wiki (openwrt.org), by its contributors: \"Except where otherwise noted, content on this "
          "wiki is licensed under the following license: CC Attribution-Share Alike 4.0 International\" "
          "(https://creativecommons.org/licenses/by-sa/4.0/): a book made from it keeps that licence. Converted to "
          "an accessible format. Installing other software on a router can break it if done wrongly: follow the "
          "page for your exact model.",
          content=(r"<div class=\"dw-content\">", r"<nav id=\"dw__pagetools\"|<footer|</article>"),
          drop=K.DROP + [r"<div class=\"dw-page-icons[^\"]*\".*?</div>"],
          units=[(r"/guide-quick-start/", "Quick start"), (r"/installation", "Installing and upgrading"),
                 (r"/troubleshooting", "Troubleshooting"), (r".", "Using OpenWrt")], limit=250),
]

GUIDES = LINUX + PROGRAMMING + NETWORK
PDFS = LINUX_PDFS

# ====================================================================== the guide (comp:index)

KIWIX = "https://library.kiwix.org/"
SECTIONS = [
    ("Linux and the command line", "Learning Linux, the shell (Bash) and the commands every Linux system has.", [
        ("key", "comp:linux_command_line", "The Linux Command Line (William Shotts), whole; personal use only"),
        ("key", "comp:tldp_intro_linux", "Introduction to Linux (Machtelt Garrels)"),
        ("key", "comp:tldp_bash_beginners", "Bash Guide for Beginners (Machtelt Garrels)"),
        ("key", "comp:tldp_advanced_bash_scripting", "Advanced Bash-Scripting Guide (Mendel Cooper)"),
        ("key", "comp:gnu_bash_manual", "The GNU Bash Reference Manual (share-alike)"),
        ("key", "comp:gnu_coreutils_manual", "GNU Coreutils: ls, cp, mv, sort and the other core commands"),
        ("key", "comp:gnu_grep_manual", "GNU grep: searching text"),
        ("key", "comp:gnu_sed_manual", "GNU sed: editing text"),
        ("key", "comp:gnu_tar_manual", "GNU tar: archives and backups"),
        ("key", "olife:gnome_desktop_help", "GNOME desktop help (the desktop of Ubuntu and Fedora)"),
        ("key", "a11yc:arch_wiki_accessibility", "ArchWiki: accessibility and speech on Linux"),
        ("word", "vision-living", "Orca, BRLTTY and the other screen readers are in the vision collection"),
        ("link", "ArchWiki, whole (Kiwix library: archlinux_en_all)", KIWIX + "#lang=eng&q=archlinux",
         "GNU FDL; already a ready-made Kiwix book, so not rebuilt here"),
        ("link", "The Linux Documentation Project HOWTOs", "https://tldp.org/HOWTO/HOWTO-INDEX/index.html",
         "each HOWTO has its own licence and most are old; open them in a browser"),
        ("link", "Ubuntu documentation (desktop help and Ubuntu Server)", "https://help.ubuntu.com/",
         "no licence is stated on the documentation pages; open it in a browser"),
        ("link", "GNU Emacs manual", "https://www.gnu.org/software/emacs/manual/",
         "GNU FDL, but www.gnu.org did not answer this build machine and the Emacs package is very large")]),
    ("Debian and FreeBSD: installing and running a system", "Installing and looking after a Linux or BSD computer.", [
        ("key", "comp:debian_installation_guide", "Debian Installation Guide (64-bit PC), with the speech and "
                                                  "braille installer"),
        ("key", "comp:debian_administrators_handbook", "The Debian Administrator's Handbook (share-alike)"),
        ("key", "comp:debian_reference", "Debian Reference (share-alike)"),
        ("key", "comp:freebsd_handbook", "The FreeBSD Handbook")]),
    ("Programming", "Learning to program, and the references programmers use.", [
        ("key", "comp:python_tutorial", "The Python Tutorial (official)"),
        ("key", "comp:python_library", "The Python Standard Library (official reference)"),
        ("key", "comp:python_language_howto", "Python language reference, how-to guides and FAQs (official)"),
        ("key", "comp:think_python_2e", "Think Python, 2nd edition; personal use only"),
        ("key", "comp:automate_boring_stuff_3e", "Automate the Boring Stuff with Python, 3rd edition; personal use "
                                                 "only"),
        ("key", "comp:eloquent_javascript_4e", "Eloquent JavaScript, 4th edition; personal use only"),
        ("key", "comp:pro_git_2e", "Pro Git, 2nd edition; personal use only"),
        ("key", "comp:sqlite_docs", "SQLite documentation"),
        ("key", "comp:rust_book", "The Rust Programming Language"),
        ("key", "comp:go_docs", "Go documentation"),
        ("key", "tech:swift_book", "The Swift Programming Language (Apple, open source)"),
        ("key", "tech:ms_powershell", "PowerShell documentation (Microsoft)"),
        ("key", "nonprofit:w3c_wai_tutorials", "Web Accessibility Tutorials (W3C WAI): accessible menus, forms, "
                                               "tables and images"),
        ("key", "privacy:owasp_cheat_sheets", "OWASP Cheat Sheets: safe sign-in and passwords for website builders"),
        ("link", "MDN Web Docs: HTML, CSS and JavaScript (Kiwix library: developer.mozilla.org_en_all)",
         KIWIX + "#lang=eng&q=mozilla", "CC BY-SA; already a ready-made Kiwix book, so not rebuilt here"),
        ("link", "DevDocs programming references (Kiwix library: devdocs_en_*)", KIWIX + "#lang=eng&q=devdocs",
         "each with its own open licence; ready-made Kiwix books"),
        ("link", "Stack Overflow (Kiwix library, 107 GB; reading only)", "https://download.kiwix.org/zim/"
                                                                         "stack_exchange/",
         "CC BY-SA; Stack Exchange forbids AI training, so it is reference only and too big to rebuild")]),
    ("Windows and everyday PC skills", "Using Windows, the command prompt, Office programs and files.", [
        ("key", "pcb:index", "Computer and phone basics: the beginner's guide to the library"),
        ("key", "tech:ms_windows_support", "Windows troubleshooting and support articles (Microsoft)"),
        ("key", "tech:ms_windows_commands", "Windows commands: every command of the command prompt (Microsoft)"),
        ("key", "tech:ms_windows_terminal", "Windows Terminal documentation (Microsoft)"),
        ("key", "tech:ms_windows_powershell_51_reference", "Windows PowerShell 5.1 commands (Microsoft)"),
        ("key", "tech:ms_office_support", "Microsoft Office troubleshooting articles"),
        ("key", "tech:ms_outlook_support", "Outlook troubleshooting articles"),
        ("key", "tech:ms_edge_support", "Microsoft Edge troubleshooting articles"),
        ("key", "pcb:libreoffice_getting_started", "LibreOffice Getting Started Guide"),
        ("key", "pcb:loc_personal_digital_archiving", "Keeping files safe: folders, names and backups (Library of "
                                                     "Congress)"),
        ("word", "typing", "Touch typing courses and the keyboard skills index"),
        ("link", "Microsoft Support: Windows help and the keyboard shortcuts", "https://support.microsoft.com/"
                                                                                "windows",
         "Microsoft's copyright; open it in a browser"),
        ("link", "GCFGlobal free computer lessons", "https://edu.gcfglobal.org/en/topics/tech/",
         "Goodwill Community Foundation's copyright; open it in a browser")]),
    ("Repair, hardware and home networking", "Fixing and building computers, and running a home network.", [
        ("key", "comp:openwrt_user_guide", "OpenWrt user guide: free router software (share-alike)"),
        ("key", "elec:wikibooks_assemble_desktop_pc", "How to Assemble a Desktop PC (Wikibooks)"),
        ("word", "electronics", "Electronics and repair books (Kuphaldt, Navy NEETS, NLS player manuals)"),
        ("word", "cat:otl", "The Open Textbook Library, whose computing and networking textbooks are built whole"),
        ("word", "course:libretexts", "LibreTexts, whose Workforce library has the computer and network courses"),
        ("manuals", "computers", "Computer and router manuals, as links"),
        ("link", "Raspberry Pi documentation", "https://www.raspberrypi.com/documentation/",
         "CC BY-SA 4.0, but its site refuses programs (403); open it in a browser"),
        ("link", "Cisco Networking Academy", "https://www.netacad.com/",
         "Cisco's copyright and a sign-in; open it in a browser"),
        ("link", "CompTIA A+ and Network+ exam objectives", "https://www.comptia.org/certifications",
         "CompTIA's copyright; open it in a browser")]),
    ("Phones and tablets", "Smartphones, tablets, their accessibility and staying safe on them.", [
        ("key", "privacy:security_in_a_box", "Security in a Box: protecting Android phones and iPhones"),
        ("key", "privacy:privacy_guides", "Privacy Guides: Android and iOS privacy"),
        ("key", "privacy:ncsc_individuals_families", "UK NCSC: securing your phone and accounts"),
        ("manuals", "personal_electronics", "Phone and tablet manuals, as links"),
        ("link", "iPhone User Guide and its accessibility chapter (VoiceOver)", "https://support.apple.com/guide/"
                                                                                 "iphone/welcome/ios",
         "Apple's copyright; open it in a browser"),
        ("link", "Android Accessibility Help (TalkBack)", "https://support.google.com/accessibility/android/",
         "Google's copyright; open it in a browser"),
        ("link", "FCC consumer guides: phones, robocalls, wireless emergency alerts and hearing aid compatibility",
         "https://www.fcc.gov/consumers/guides", "public domain, but fcc.gov refuses programs; open it in a "
                                                 "browser"),
        ("link", "Be Connected (Australian Government): beginner phone and computer courses",
         "https://beconnected.esafety.gov.au/", "no licence is stated and its courses are in a sign-in learning "
                                                "system; open it in a browser")]),
    ("Questions and answers, and Wikibooks, in the Kiwix library", "Ready-made Kiwix books: pick them in the "
     "Kiwix catalogue; nothing is rebuilt.", [
        ("key", "se:index", "Stack Exchange how-to sites: Super User, Ask Ubuntu, Unix and Linux, Ask Different, "
                            "Android Enthusiasts and more (reading only, never training)"),
        ("link", "Wikibooks, whole (Kiwix library: wikibooks_en_all)", KIWIX + "#lang=eng&q=wikibooks",
         "CC BY-SA; its computing shelf has Computers for Beginners, Bash Shell Scripting, Python Programming, "
         "Linux Guide and many more"),
        ("link", "Wikipedia's computing articles (Kiwix library: wikipedia_en_computer)", KIWIX + "#lang=eng&q="
                                                                                                "computer",
         "CC BY-SA; a ready-made Kiwix book")]),
]
INDEX = X.index_maker("comp", GROUP, "Computers, phones and programming: a guide to the library",
                      "Computers, phones and programming",
                      "A guide to everything in the library on computers and phones, by theme: Linux and the "
                      "command line, installing and running Debian and FreeBSD, programming, Windows and everyday PC "
                      "skills, repair and home networking, phones and tablets, and the question-and-answer sites "
                      "and Wikibooks of the Kiwix library.", SECTIONS, country="International")
MAKERS = {"index": INDEX}
MAKERS.update({row[0]: (gnu_book, gnu_sign) for row in GNU_MANUALS})


def theme_keys(section_numbers, own):
    """The keys of a request word: comp:index, the module's own keys named in own, and every library key the
    guide's sections (by number, from 1) list."""
    keys = ["comp:index"] + [f"comp:{n}" for n in own]
    for number in section_numbers:
        keys += [what for kind, what, *_ in SECTIONS[number - 1][2] if kind == "key"]
    return list(dict.fromkeys(keys))


LINUX_NAMES = [g["name"] for g in LINUX] + [p["name"] for p in LINUX_PDFS] + [r[0] for r in GNU_MANUALS]
PROGRAMMING_NAMES = [g["name"] for g in PROGRAMMING]
NETWORK_NAMES = [g["name"] for g in NETWORK]
WORDS = {
    "comp-linux": lambda: theme_keys((1, 2), LINUX_NAMES),
    "comp-programming": lambda: theme_keys((3,), PROGRAMMING_NAMES),
    "comp-windows-basics": lambda: theme_keys((4,), []),
    "comp-repair-network": lambda: theme_keys((5,), NETWORK_NAMES),
    "comp-phones": lambda: theme_keys((6,), []),
    "computers": lambda: list(dict.fromkeys(theme_keys((1, 2, 3, 4, 5, 6, 7), LINUX_NAMES + PROGRAMMING_NAMES +
                                                       NETWORK_NAMES) + [f"pcb:{g['name']}" for g in CB.GUIDES])),
}
COLLECTION = K.Collection("comp", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "comp_tldp": "tldp.org (checked at every build): Machtelt Garrels' guides' \"Copyright information\" pages: "
                 "\"Copyright (c) 2002-2007, Machtelt Garrels. All rights reserved. Redistribution and use in source "
                 "and binary forms, with or without modification, are permitted provided that ...\" (BSD-3-Clause); "
                 "the Advanced Bash-Scripting Guide's front page: \"This document is herewith granted to the Public "
                 "Domain. No copyright!\". robots.txt allows our reader; no AI rules (checked 2026-11-23).",
    "comp_freebsd": "www.freebsd.org/copyright/freebsd-doc-license/ (checked at every build): \"Redistribution and "
                    "use in source (AsciiDoc) and 'compiled' forms (HTML, PDF, EPUB and so forth) with or without "
                    "modification, are permitted provided that ...\". docs.freebsd.org's robots.txt allows our reader "
                    "(2026-11-23).",
    "comp_debian": "debian-handbook.info (\"This book is licensed under a Creative Commons Attribution-ShareAlike 3.0 "
                   "Unported License\", or the GNU GPL version 2 or later; CC BY-SA is used); the Debian "
                   "Installation Guide (\"This manual is free software; you may redistribute it and/or modify it "
                   "under the terms of the GNU General Public License\", its Appendix F) and Debian Reference (\"under "
                   "the terms of the GNU General Public License of any version compliant to the Debian Free Software "
                   "Guidelines\"), checked at every build; share-alike. robots.txt allows our reader (2026-11-23).",
    "comp_gnu": "The Info manuals inside the GNU source packages on ftp.gnu.org (bash, coreutils, grep, sed, tar), "
                "each one's front matter checked at every build: \"Permission is granted to copy, distribute and/or "
                "modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later "
                "version\" (share-alike). ftp.gnu.org's robots.txt allows everything with \"Crawl-delay: 60\", which "
                "the module keeps (61 seconds between requests). www.gnu.org reset this build machine's connections "
                "(2026-11-23), so its web pages are not read.",
    "comp_python": "docs.python.org/3/license.html (checked at every build): \"Python software and documentation are "
                   "licensed under the Python Software Foundation License Version 2\"; code in the documentation is "
                   "also Zero-Clause BSD. robots.txt allows our reader (2026-11-23).",
    "comp_sqlite_rust_go": "www.sqlite.org/copyright.html: \"All of the code and documentation in SQLite has been "
                           "dedicated to the public domain by the authors\"; the Rust Book's repository: LICENSE-MIT "
                           "and LICENSE-APACHE (MIT or Apache 2.0); go.dev/copyright: \"Except as noted, the contents of "
                           "this site are licensed under the Creative Commons Attribution 4.0 License\". All checked "
                           "at every build; robots.txt allows our reader (2026-11-23).",
    "comp_personal_use": "Personal use only: The Linux Command Line (linuxcommand.org/tlcl.php: \"Released under a "
                         "BY-NC-ND Creative Commons license\"; the PDF's own copyright page is checked too; kept whole "
                         "and unchanged; read from the Internet Archive item the-linux-command-line-7th-internet-"
                         "edition because SourceForge's download page asks for a browser check); Think Python 2e "
                         "(\"Creative Commons Attribution-NonCommercial 3.0 Unported License\"); Automate the Boring "
                         "Stuff (\"Free to read under a Creative Commons license\", linking CC BY-NC-SA 3.0); Eloquent "
                         "JavaScript (\"Licensed under a Creative Commons attribution-noncommercial license\", linking "
                         "CC BY-NC 3.0); Pro Git (\"Creative Commons Attribution Non Commercial Share Alike 3.0 "
                         "license\"). robots.txt of each site allows our reader (2026-11-23).",
    "comp_openwrt": "openwrt.org/license (checked at every build): \"Except where otherwise noted, content on this "
                    "wiki is licensed under the following license: CC Attribution-Share Alike 4.0 International\". "
                    "robots.txt allows our reader (2026-11-23).",
    "comp_index": "The guide (comp:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Ubuntu documentation (help.ubuntu.com, documentation.ubuntu.com/server)", "No licence is stated on the "
     "documentation pages or in the Ubuntu Server documentation repository's files that could be read (2026-11-23). "
     "Link-only (comp:index); Ask Ubuntu is in the Kiwix library (se:index). Index: https://help.ubuntu.com/"),
    ("Raspberry Pi documentation", "CC BY-SA 4.0 (its repository's LICENSE.md), but www.raspberrypi.com refuses "
     "programs (403, 2026-11-23) and the repository holds only AsciiDoc sources. Link-only. Index: "
     "https://www.raspberrypi.com/documentation/"),
    ("The Linux Documentation Project's HOWTOs, the Linux System Administrator's Guide and the Network "
     "Administrator's Guide", "Each HOWTO has its own licence and most were last updated 2000-2010; the two guides "
     "(GNU FDL) date from 2004 and 2000 (SLIP and UUCP). Link-only. Index: https://tldp.org/guides.html"),
    ("The GNU manuals from www.gnu.org and the GNU Emacs manual", "www.gnu.org reset this build machine's "
     "connections (2026-11-23); the Bash, Coreutils, grep, sed and tar manuals are read from their source packages "
     "on ftp.gnu.org instead. The Emacs package is very large and Emacs is little used with screen readers "
     "(Emacspeak is its own project). Index: https://www.gnu.org/manual/"),
    ("ArchWiki (whole), MDN Web Docs, Wikibooks and Stack Overflow", "Already ready-made books in the Kiwix library "
     "(archlinux_en_all, developer.mozilla.org_en_all, wikibooks_en_all, stackoverflow.com_en_all); not rebuilt. "
     "Index: https://library.kiwix.org/"),
    ("Apple's iPhone, iPad and Mac guides, Google's Android and TalkBack help, and Microsoft Support's Windows "
     "pages", "The makers' copyright: link-only (comp:index). Microsoft's CC BY 4.0 documentation is built "
     "(tech:). Index: https://support.apple.com/guide/ and https://support.google.com/accessibility/android/"),
    ("Cisco Networking Academy and CompTIA courses", "Copyright, and Cisco's courses need a sign-in. Link-only. "
     "Index: https://www.netacad.com/"),
    ("Be Connected (Australian Government eSafety Commissioner)", "No licence is stated on its pages and its "
     "courses are in a sign-in learning system; esafety.gov.au did not answer (2026-11-23). Link-only. Index: "
     "https://beconnected.esafety.gov.au/"),
    ("Open Textbook Library and LibreTexts computing and networking textbooks", "Already built whole by the open "
     "catalogues (cat:otl) and courses (course:libretexts) modules; not repeated. Index: "
     "https://open.umn.edu/opentextbooks/subjects/computer-science-information-systems"),
    ("Think Python, 3rd edition", "CC BY-NC-SA 4.0 and published as Jupyter notebooks; the 2nd edition (HTML) is "
     "built. Index: https://allendowney.github.io/ThinkPython/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
