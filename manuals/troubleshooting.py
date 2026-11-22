"""Two collections added on 2026-11-21: appliance error codes and troubleshooting by brand, and the release notes of
firmware and software of common devices (routers, phones, smart speakers, computers and screen readers).
categories.py adds both; build_manuals.py builds them.

  appliance_troubleshooting   washers, dryers, dishwashers, ovens and ranges, refrigerators, furnaces, heat pumps
      and water heaters. Three kinds of source:
        1. the Internet Archive's service manuals, technical sheets ("tech sheets", the wiring and fault-code sheet
           taped inside many appliances), repair and troubleshooting manuals (ia_any: ONE search of the Manual
           Library, which holds every maker's collection, manuals_whirlpool, manuals_maytag and the rest, for a
           kind of appliance AND a kind of service paper in the title; the copies of manual-copying sites are left
           out as everywhere). Each item keeps the rights its uploader gave. Checked on 2026-11-21: none of the
           appliance service manuals there carries an open licence (a search for appliance service, repair or
           troubleshooting titles with a Creative Commons or public-domain licence found 0), so they are indexed as
           links like every manual.
        2. the makers' own error-code and support pages: LINK ONLY (APPLIANCE_MAKERS, access "link"): the error
           code tables are the makers' copyright; nothing is read; the address is listed for the person to open
           in a browser for their own use.
        3. hand-entered pages (DOCUMENTS): iFixit's community troubleshooting pages for each kind of appliance,
           LINK ONLY (see IFIXIT_REASON), and two US government pages (public domain: ENERGY STAR's heating and
           cooling maintenance checklist, the CPSC recalls search).
  release_notes   firmware and software release notes (RELEASE_NOTES). "full" where the text is openly licensed and
      the site's robots.txt allows programs: the index marks it may_download, so the owner's Program Downloader
      copies the whole text (NVDA's "What's New", GPL; Orca's NEWS, LGPL; BRLTTY's ChangeLog, LGPL; the Android
      and Pixel security bulletins, CC BY 4.0; OpenWrt's release notes, CC BY-SA 4.0). "link" for everything
      that is the maker's copyright (JAWS, Narrator, VoiceOver, Windows, macOS, iOS, router, phone and speaker
      makers): the address only, never downloaded by a program. Where a version can be read (NVDA's newest
      release from its own What's New page; Orca's newest stable release from GNOME's download list), the
      index records it ("version"), so a rebuild after a new release is a new version of the index
      (build_manuals.merge_catalogue keeps the old ones).

Checked by a program on 2026-11-21 with the builder's User-Agent:
  - iFixit (www.ifixit.com): its pages are CC BY-NC-SA 3.0 (personal, non-commercial use is allowed); robots.txt
    allows the Device pages and the API but says "ai-train=no"; its Terms of Use say API answers may be kept for
    24 hours only and must not go into "indexes" or "datasets", and that content is for your own personal use.
    So nothing of iFixit is read or kept: its pages are listed by hand, and build_manuals.NO_AUTOMATED_DOWNLOAD
    keeps the Program Downloader from copying them. The owner opens them in a browser.
  - energy.gov's Energy Saver pages (furnaces, heat pumps, water heating) answer "not found" (HTTP 404) now; not
    used. www.energystar.gov's robots.txt allows this builder (it shuts out ClaudeBot by name only).
  - gitlab.gnome.org's robots.txt disallows its "raw" files, so Orca's NEWS is taken from download.gnome.org
    (no robots.txt), the file published with each release.
  - JAWS's What's New (support.freedomscientific.com) refuses programs (HTTP 403) and is Freedom Scientific's
    copyright: link only.
  - Microsoft's Windows release health and Apple's update pages: their sites' terms keep the text theirs (no open
    licence on the pages): link only.
  - Sonos's and Dolphin's release-notes addresses answered "not found" (HTTP 404): their support home pages are
    linked instead.
Not used: the error-code "lookup" websites that copy makers' tables (they are copies of copyrighted tables; the
same rule as manual-copying sites, build_manuals.NEVER_SITES).
"""

INDEX_LICENCE = "CC0 (facts and links); each manual and page belongs to its maker or author"

# What an Internet Archive item is, from its title: (regular expression, kind). The first that matches is kept.
APPLIANCE_KINDS = [
    (r"dish ?washers?", "dishwasher"), (r"washing machines?|\bwashers?\b|laundry", "washer"),
    (r"\bdryers?\b", "dryer"), (r"refrigerators?|fridges?|freezers?|ice makers?", "refrigerator"),
    (r"heat pumps?", "heat pump"), (r"furnaces?|boilers?", "furnace"), (r"water heaters?", "water heater"),
    (r"\bovens?\b|\branges?\b|cooktops?|stoves?", "oven or range"),
]
_KINDS = ["washer", "washing machine", "dryer", "dishwasher", "oven", "electric range", "gas range", "cooktop",
          "refrigerator", "freezer", "furnace", "heat pump", "water heater"]
_DOCUMENTS = ["service", "repair", "troubleshooting", "error codes", "fault codes", "tech sheet", "technical sheet",
              "diagnostic", "wiring diagram"]
# The single Internet Archive search: a title with one of the kinds AND one of the kinds of service paper ("washer"
# ... "service", "furnace" ... "tech sheet"); a phrase is matched as a phrase (build_manuals.ia_any_clause).
IA_WORDS = {"kinds": _KINDS, "documents": _DOCUMENTS}
# Not home appliances (a hair dryer, a pressure washer, a tractor's range, laboratory plate washers, washer
# disinfectors and ultra-low freezers), and sales papers and parts lists.
IA_EXCLUDE = (r"hair ?dryer|pressure washer|parts washer|\block ?washer|tractor|loader|baler|rover|rifle|scope|"
              r"elisa|(?:strip|plate|microplate|cage|rack) washer|disinfector|ultra[- ]low|laborator|"
              r"rangefinder|catalog(?:ue)?s?\b|price ?list|brochure|flyer|parts? (?:list|catalog|book)")

# The makers' own error-code and support pages: LINK ONLY. Addresses opened on 2026-11-21 (the error-code page where
# one was confirmed, else the support or home page, as said in each reason).
_LINK = "the maker's error-code tables and support pages are its copyright, so nothing is read; "
_COMMON = dict(prefix="ts", types=[], documents="error codes and troubleshooting pages",
               category="appliance_troubleshooting")


def _makers(makers):
    """The appliance makers with the shared fields."""
    return [dict(_COMMON, access="link", **m) for m in makers]


APPLIANCE_MAKERS = _makers([
    dict(key="whirlpool", maker="Whirlpool (with Maytag, KitchenAid, Amana and JennAir)", type="home appliance",
         library="https://www.whirlpool.com/owners.html",
         reason=_LINK + "the site does not answer programs, so the owners' page address is not confirmed"),
    dict(key="maytag", maker="Maytag", type="home appliance", library="https://www.maytag.com/owners.html",
         reason=_LINK + "the site does not answer programs, so the owners' page address is not confirmed"),
    dict(key="kitchenaid", maker="KitchenAid", type="home appliance", library="https://www.kitchenaid.com/owners.html",
         reason=_LINK + "the site does not answer programs, so the owners' page address is not confirmed"),
    dict(key="ge", maker="GE Appliances (with Hotpoint, Café, Monogram and Haier)", type="home appliance",
         library="https://www.geappliances.com/ge/service-and-support/", reason=_LINK + "its support page is linked"),
    dict(key="lg", maker="LG", type="home appliance", library="https://www.lg.com/us/support/help-library",
         reason=_LINK + "its help library (error codes by product) is linked"),
    dict(key="samsung", maker="Samsung", type="home appliance", library="https://www.samsung.com/us/support/",
         reason=_LINK + "its support page is linked"),
    dict(key="bosch", maker="Bosch (with Thermador and Gaggenau)", type="home appliance",
         library="https://www.bosch-home.com/us/en/services", reason=_LINK + "its service page is linked"),
    dict(key="frigidaire", maker="Frigidaire and Electrolux", type="home appliance",
         library="https://www.frigidaire.com/",
         reason=_LINK + "the site does not answer programs, so its home page is linked"),
    dict(key="kenmore", maker="Kenmore", type="home appliance", library="https://www.kenmore.com/",
         reason=_LINK + "its home page is linked (Kenmore appliances were made by Whirlpool, LG, Frigidaire and "
                        "others: the model number's first three digits say which)"),
    dict(key="speed-queen", maker="Speed Queen", type="washer or dryer", library="https://speedqueen.com/support/",
         reason=_LINK + "its support page is linked"),
    dict(key="miele", maker="Miele", type="home appliance", library="https://www.mieleusa.com/c/service-1823.htm",
         reason=_LINK + "the site refuses programs (HTTP 403)"),
    dict(key="carrier", maker="Carrier (with Bryant and Payne)", type="furnace or heat pump",
         library="https://www.carrier.com/us/en/residential/", reason=_LINK + "its home page is linked"),
    dict(key="trane", maker="Trane and American Standard", type="furnace or heat pump",
         library="https://www.trane.com/residential/", reason=_LINK + "its home page is linked"),
    dict(key="lennox", maker="Lennox", type="furnace or heat pump",
         library="https://www.lennox.com/residential/owners/",
         reason=_LINK + "its owners' page is linked"),
    dict(key="goodman", maker="Goodman (with Amana heating and Daikin)", type="furnace or heat pump",
         library="https://www.goodmanmfg.com/support", reason=_LINK + "its support page is linked"),
    dict(key="rheem", maker="Rheem and Ruud", type="water heater, furnace or heat pump",
         library="https://www.rheem.com/",
         reason=_LINK + "its home page is linked"),
    dict(key="ao-smith", maker="A. O. Smith", type="water heater", library="https://www.hotwater.com/",
         reason=_LINK + "its home page is linked"),
    dict(key="bradford-white", maker="Bradford White", type="water heater", library="https://www.bradfordwhite.com/",
         reason=_LINK + "its home page is linked"),
    dict(key="rinnai", maker="Rinnai", type="tankless water heater", library="https://www.rinnai.us/support/contact",
         reason=_LINK + "its support page is linked"),
    dict(key="navien", maker="Navien", type="tankless water heater or boiler", library="https://www.navieninc.com/",
         reason=_LINK + "its home page is linked"),
])

IFIXIT_RIGHTS = "CC BY-NC-SA 3.0 (iFixit and its authors): personal, non-commercial use"
IFIXIT_REASON = ("iFixit's Terms of Use (read 2026-11-21) allow programs only through its API, keep API answers 24 "
                 "hours at most and forbid putting them in indexes or datasets; its robots.txt says ai-train=no. So "
                 "nothing is read: its page is listed by hand for the owner to open in a browser (personal use, "
                 "as its CC BY-NC-SA licence allows).")


def _ifixit(kind, page):
    """The hand-entered record of one iFixit troubleshooting page (link only)."""
    return dict(key=f"ifixit-{page.lower()}", by="iFixit (community repair wiki)", product=kind,
                title=f"iFixit: {kind} repair and troubleshooting (community pages)",
                url=f"https://www.ifixit.com/Device/{page}", type=kind, document="troubleshooting",
                access="link", rights=IFIXIT_RIGHTS, reason=IFIXIT_REASON)


APPLIANCE_DOCUMENTS = [
    _ifixit("washer", "Washing_Machine"), _ifixit("dryer", "Dryer"), _ifixit("dishwasher", "Dishwasher"),
    _ifixit("oven or range", "Stove"), _ifixit("wall oven", "Wall_Oven"), _ifixit("cooktop", "Cooktop"),
    _ifixit("refrigerator", "Refrigerator"), _ifixit("furnace", "Furnace"), _ifixit("heat pump", "Heat_Pump"),
    _ifixit("water heater", "Water_Heater"),
    dict(key="energystar-maintenance", by="ENERGY STAR (US EPA)", product="furnace, heat pump and air conditioner",
         title="Heating and cooling maintenance checklist (ENERGY STAR)",
         url="https://www.energystar.gov/saveathome/heating-cooling/maintenance-checklist", type="furnace or heat pump",
         document="guide", access="full", rights="a US government work (public domain)",
         reason="a US government work; robots.txt allows this builder"),
    dict(key="cpsc-recalls", by="US Consumer Product Safety Commission", product="every appliance",
         title="Recalls search (CPSC): check an appliance for a safety recall", url="https://www.cpsc.gov/Recalls",
         type="home appliance", document="guide", access="full", rights="a US government work (public domain)",
         reason="a US government work; robots.txt allows the page"),
]

APPLIANCE_NOTICE = ("Unplug the appliance, or switch off its breaker, before opening any panel; turn off the gas and "
                    "water first where there are any. Gas, refrigerant and the burner, flue and controls of a "
                    "furnace or gas water heater are work for a licensed technician. If you smell gas, leave the "
                    "house and call the gas company from outside. Error codes differ between models: check the "
                    "model number on the appliance's rating plate.")

# ------------------------------------------------------------------------------------------- release notes
_COPY = "the maker's copyright (no open licence on the page), so it is link only: the owner opens it in a browser"


def _note(key, by, product, title, url, type_, access, rights, reason, **more):
    """One release-notes record."""
    return dict(key=key, by=by, product=product, title=title, url=url, type=type_, document="release notes",
                access=access, rights=rights, reason=reason, **more)


RELEASE_NOTES = [
    # Screen readers and braille.
    _note("nvda", "NV Access", "NVDA", "NVDA: What's New (every release's changes)",
          "https://download.nvaccess.org/documentation/changes.html", "screen reader", "full",
          "GNU GPL version 2 or later (NV Access)",
          "NVDA and its documentation are under the GNU GPL; download.nvaccess.org has no robots.txt (all allowed)",
          version_from="heading", version_pattern=r"<h2[^>]*>\s*(\d{4}\.\d+(?:\.\d+)?)\s*<"),
    _note("orca", "GNOME (Orca team)", "Orca", "Orca screen reader: NEWS of the newest release",
          "https://download.gnome.org/sources/orca/", "screen reader", "full",
          "GNU LGPL version 2.1 or later (the Orca authors)",
          "Orca is under the GNU LGPL; download.gnome.org has no robots.txt (gitlab.gnome.org's robots.txt "
          "disallows its raw files, so it is not used)", version_from="gnome", project="orca"),
    _note("brltty", "The BRLTTY team", "BRLTTY", "BRLTTY (braille display driver): ChangeLog",
          "https://brltty.app/doc/ChangeLog.txt", "braille software", "full",
          "GNU LGPL version 2.1 or later (the BRLTTY team)",
          "BRLTTY is under the GNU LGPL; brltty.app has no robots.txt (all allowed)"),
    _note("jaws", "Freedom Scientific (Vispero)", "JAWS", "JAWS: What's New",
          "https://support.freedomscientific.com/Downloads/JAWS/JAWSWhatsNew", "screen reader", "link",
          "copyrighted (Freedom Scientific)", _COPY + "; the site also refuses programs (HTTP 403)"),
    _note("narrator", "Microsoft", "Narrator", "Narrator: the complete guide (its What's New chapter)",
          "https://support.microsoft.com/en-us/accessibility/windows/narrator/complete-guide-to-narrator",
          "screen reader", "link", "copyrighted (Microsoft)", _COPY),
    _note("voiceover", "Apple", "VoiceOver", "Apple accessibility features (VoiceOver)",
          "https://www.apple.com/accessibility/features/?vision", "screen reader", "link", "copyrighted (Apple)",
          _COPY + "; VoiceOver changes are listed in each macOS and iOS update's notes below"),
    _note("dolphin", "Dolphin Computer Access", "SuperNova", "Dolphin SuperNova: support and release notes",
          "https://yourdolphin.com/Product-Support", "screen reader", "link", "copyrighted (Dolphin Computer Access)",
          _COPY + "; its release-notes address answered HTTP 404, so the support page is linked"),
    # Computers.
    _note("windows", "Microsoft", "Windows", "Windows release health (Windows 11 and 10 release information)",
          "https://learn.microsoft.com/en-us/windows/release-health/", "operating system", "link",
          "copyrighted (Microsoft)", _COPY),
    _note("macos", "Apple", "macOS", "What's new in the updates for macOS Sequoia",
          "https://support.apple.com/en-us/120283", "operating system", "link", "copyrighted (Apple)", _COPY),
    _note("apple-security", "Apple", "macOS, iOS, iPadOS, watchOS, tvOS", "Apple security releases",
          "https://support.apple.com/en-us/100100", "operating system", "link", "copyrighted (Apple)", _COPY),
    # Phones.
    _note("ios", "Apple", "iOS", "About iOS 17 updates", "https://support.apple.com/en-us/118723", "phone", "link",
          "copyrighted (Apple)", _COPY),
    _note("android-security", "Android Open Source Project (Google)", "Android",
          "Android security bulletins", "https://source.android.com/docs/security/bulletin", "phone", "full",
          "CC BY 4.0 (Android Open Source Project)",
          "source.android.com's pages are under CC BY 4.0 (its Content License); robots.txt allows them"),
    _note("pixel-security", "Android Open Source Project (Google)", "Google Pixel",
          "Pixel update bulletins", "https://source.android.com/docs/security/bulletin/pixel", "phone", "full",
          "CC BY 4.0 (Android Open Source Project)",
          "source.android.com's pages are under CC BY 4.0 (its Content License); robots.txt allows them"),
    _note("samsung-security", "Samsung", "Samsung Galaxy phones", "Samsung mobile security updates",
          "https://security.samsungmobile.com/securityUpdate.smsb", "phone", "link", "copyrighted (Samsung)", _COPY),
    # Routers.
    _note("openwrt", "The OpenWrt project", "OpenWrt", "OpenWrt releases and release notes",
          "https://openwrt.org/releases/start", "router", "full", "CC BY-SA 4.0 (OpenWrt wiki authors)",
          "the OpenWrt wiki is under CC BY-SA 4.0; robots.txt allows the page"),
    _note("netgear", "NETGEAR", "NETGEAR routers", "NETGEAR support (firmware and release notes by model)",
          "https://www.netgear.com/support/", "router", "link", "copyrighted (NETGEAR)", _COPY),
    _note("tp-link", "TP-Link", "TP-Link routers", "TP-Link download center (firmware and release notes by model)",
          "https://www.tp-link.com/us/support/download/", "router", "link", "copyrighted (TP-Link)", _COPY),
    _note("asus", "ASUS", "ASUS routers", "ASUS download center (firmware and release notes by model)",
          "https://www.asus.com/support/download-center/", "router", "link", "copyrighted (ASUS)", _COPY),
    _note("linksys", "Linksys", "Linksys routers", "Linksys support (firmware and release notes by model)",
          "https://support.linksys.com/home/", "router", "link", "copyrighted (Linksys)", _COPY),
    _note("eero", "eero (Amazon)", "eero", "eero support (software release notes)", "https://eero.com/support",
          "router", "link", "copyrighted (eero)", _COPY),
    _note("ubiquiti", "Ubiquiti", "UniFi and AmpliFi", "Ubiquiti releases", "https://community.ui.com/releases",
          "router", "link", "copyrighted (Ubiquiti)", _COPY),
    # Smart speakers.
    _note("google-nest", "Google", "Google Nest and Home speakers and displays",
          "Google smart speaker and display firmware versions and release notes",
          "https://support.google.com/googlehome/answer/7365257", "smart speaker", "link", "copyrighted (Google)",
          _COPY),
    _note("echo", "Amazon", "Amazon Echo", "Alexa-enabled device software versions",
          "https://www.amazon.com/gp/help/customer/display.html?nodeId=GMB5FVUB6REAVTXY", "smart speaker", "link",
          "copyrighted (Amazon)", _COPY + "; Amazon's conditions of use also forbid robots"),
    _note("sonos", "Sonos", "Sonos speakers", "Sonos support (software release notes)",
          "https://support.sonos.com/en/home", "smart speaker", "link", "copyrighted (Sonos)",
          _COPY + "; its release-notes address answered HTTP 404, so the support page is linked"),
]

CATEGORIES = {
    "appliance_troubleshooting": dict(
        name="Appliance error codes and troubleshooting (service manuals and makers' pages)",
        description="Error codes, fault codes, technical sheets, service and troubleshooting manuals of washers, "
                    "dryers, dishwashers, ovens and ranges, refrigerators, furnaces, heat pumps and water heaters: "
                    "the Internet Archive's service manuals, the makers' own error-code pages (links), iFixit's "
                    "community pages (links) and US government maintenance and recall pages.",
        kind="manuals", licence=INDEX_LICENCE,
        ia_any=IA_WORDS, ia_kinds=APPLIANCE_KINDS, ia_exclude=IA_EXCLUDE,
        makers=APPLIANCE_MAKERS, documents=APPLIANCE_DOCUMENTS, notice=APPLIANCE_NOTICE),
    "release_notes": dict(
        name="Firmware and software release notes (routers, phones, speakers, computers, screen readers)",
        description="What changed in each update of NVDA, JAWS, Narrator, VoiceOver, Orca and BRLTTY; Windows, "
                    "macOS and iOS; Android and Pixel phones; routers (OpenWrt, NETGEAR, TP-Link, ASUS, Linksys, "
                    "eero, Ubiquiti); and smart speakers (Google Nest, Amazon Echo, Sonos). The openly licensed "
                    "ones may be copied whole; the rest are links.",
        kind="manuals", licence=INDEX_LICENCE, documents=RELEASE_NOTES),
}
