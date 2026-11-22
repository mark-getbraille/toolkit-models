"""The collection "Blind and low-vision living: braille writers, braille displays, magnifiers and talking devices
(manuals)" (category key vision_devices): the owner's request of 2026-11-22 for a blind and low-vision living
section, with its own heading in the manual library, and the braille writer care and repair part he asked for the
same day. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (braillers and
            braillewriters, slates and styluses, embossers, reading machines, Kurzweil and Optacon, DAISY players,
            money and colour identifiers, talking scales and thermometers, video magnifiers, notetakers ...). The
            words the collection "accessibility" already searches (talking, braille, magnifier, daisy player, victor
            reader, screen reader, notetaker, refreshable, low vision ...) are not repeated here;
  makers    braille writer makers and repairers (Perkins Solutions for the Perkins Brailler, Next Generation and
            SMART Brailler; APH; the Mountbatten and Tatrapoint makers), screen reader and magnifier software makers
            (Freedom Scientific for JAWS, ZoomText and Fusion; Dolphin; NV Access), braille display, notetaker and
            embosser makers not already in assistive_tech_repair, talking-label and money-reader makers, cane makers,
            and the describer apps: by the owner's rule their own manuals and guides are LINK-ONLY, for the person
            (or the personal assistant) to open in a browser or fetch with Program Downloader; nothing is read from
            their sites;
  documents the braille writer care documents found, each with its access decision (the Perkins Brailler
            maintenance guide on the Internet Archive has no licence: link-only);
  guidance  the government pages the reference library builds in full (textbooks/vision_living.py: NLS, BEP's
            currency reader programme, the Access Board's accessible prescription labels) and the repair
            programmes (NLS, VA, state Assistive Technology Act programmes).

The makers already in the collection assistive_tech_repair (HumanWare, Vispero hardware, Eschenbach, ZEISS,
Enhanced Vision, Orbit Research, APH's devices, Index Braille, ViewPlus, HIMS, Zoomax, PLEXTALK, Envision, Sunu,
WeWALK) and NLS's player manuals (there and in the reference library: elec:nls_players, elec:nls_dtbm_service_manual)
are not listed again; the reference library's index (vision:index) links both collections.

The care notice is said first (NOTICE).
"""

NOTICE = ("Braille writers and devices: follow the maker's care guide. If a braille writer's key sticks, the "
          "embossing head jams or the paper will not feed, do not force it or take it apart: ask the maker or a "
          "braille writer repair service. NLS players are repaired or replaced free through your network library "
          "(1-888-657-7323); veterans can ask their VIST coordinator; state Assistive Technology Act programmes lend, "
          "reuse and help repair devices. Use only the maker's battery and charger.")

IA_WORDS = ["brailler", "braillewriter", "braille writer", "slate and stylus", "embosser", "reading machine",
            "kurzweil", "optacon", "money identifier", "bill reader", "color identifier", "colour identifier",
            "talking scale", "talking thermometer", "talking watch", "video magnifier", "electronic magnifier",
            "speech synthesizer", "dectalk", "book reader", "large print"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="vision_devices", prefix="vl", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    # braille writers and their repair
    dict(key="perkins-solutions", maker="Perkins Solutions (Perkins Brailler, Next Generation Perkins Brailler, "
                                        "SMART Brailler; sales, parts and repair)",
         type="braille writer", library="https://brailler.perkins.org/", site="brailler.perkins.org",
         reason=RULE + "; www.perkins.org refuses programs (403, checked 2026-11-22)"),
    dict(key="aph-braille-writers", maker="American Printing House for the Blind (braille writers, slates, "
                                          "styluses and teaching tools)",
         type="braille writer, slate and stylus", library="https://www.aph.org/", site="aph.org"),
    dict(key="mountbatten", maker="Mountbatten Brailler (electronic braille writer)", type="braille writer",
         library="https://www.mountbattenbrailler.com/", site="mountbattenbrailler.com"),
    # screen reader and magnification software
    dict(key="freedom-scientific", maker="Freedom Scientific (JAWS, ZoomText, Fusion; training and documentation)",
         type="screen reader and screen magnifier", library="https://www.freedomscientific.com/",
         site="freedomscientific.com"),
    dict(key="dolphin", maker="Dolphin Computer Access (SuperNova, Guide)", type="screen reader and screen "
                                                                                "magnifier",
         library="https://yourdolphin.com/", site="yourdolphin.com"),
    dict(key="nv-access", maker="NV Access (NVDA; its guides are built in full in the reference library: "
                                "atdoc:nvda_user_guide)", type="screen reader", library="https://www.nvaccess.org/",
         site="nvaccess.org"),
    # braille displays, notetakers and embossers not in assistive_tech_repair
    dict(key="dot-inc", maker="Dot Incorporation (Dot Pad, Dot Watch)", type="tactile display and braille watch",
         library="https://www.dotincorp.com/", site="dotincorp.com"),
    dict(key="american-thermoform", maker="American Thermoform (Swell Form, tactile graphics machines)",
         type="tactile graphics machine", library="https://americanthermoform.com/", site="americanthermoform.com"),
    # talking labels, money readers and daily living
    dict(key="envision-america", maker="En-Vision America (ScripTalk talking prescription labels, i.d. mate)",
         type="talking label reader", library="https://www.envisionamerica.com/", site="envisionamerica.com"),
    dict(key="orcam", maker="OrCam (OrCam MyEye, OrCam Read)", type="reading device",
         library="https://www.orcam.com/", site="orcam.com"),
    # canes
    dict(key="ambutech", maker="Ambutech (white canes and tips)", type="white cane",
         library="https://ambutech.com/", site="ambutech.com"),
    # describer apps
    dict(key="be-my-eyes", maker="Be My Eyes (describer app)", type="describer app",
         library="https://www.bemyeyes.com/", site="bemyeyes.com"),
    dict(key="aira", maker="Aira (visual interpreting service)", type="describer service",
         library="https://aira.io/", site="aira.io"),
]]

US_GOV = "a US government work (public domain)"
DOCUMENTS = [
    dict(key="perkins-maintenance-guide-ia", by="Perkins (uploaded to the Internet Archive by APH)",
         product="Perkins Brailler", title="Perkins Brailler Written Guide, Level 1: General Maintenance Guide",
         url="https://archive.org/details/written-guide-level-1-general-maintenance-guide-english",
         type="braille writer", document="maintenance guide", access="link",
         rights="no licence given (Perkins' copyright)",
         reason="link only: the item carries no licence, so it is for the owner's own use (Program Downloader)"),
    dict(key="perkins-maintenance-video-ia", by="Perkins (uploaded to the Internet Archive by APH)",
         product="Perkins Brailler", title="Perkins Brailler Video, Level 1: General Maintenance Guide",
         url="https://archive.org/details/video-level-1-general-maintenance-guide-english",
         type="braille writer", document="maintenance video", access="link",
         rights="no licence given (Perkins' copyright)",
         reason="link only: the item carries no licence, so it is for the owner's own use"),
    dict(key="nls-currency-reader", by="National Library Service for the Blind and Print Disabled (NLS)",
         product="US currency reader", title="US Currency Reader Program (NLS)",
         url="https://www.loc.gov/nls/services-and-resources/us-currency-reader-program/", type="money identifier",
         document="guide", access="full", rights=US_GOV,
         reason="a US government work; robots.txt allows /nls/ (in the reference library: vision:nls_services)"),
    dict(key="bep-currency-reader", by="Bureau of Engraving and Printing", product="US currency reader (iBill)",
         title="U.S. Currency Reader Program and its questions and answers (BEP)",
         url="https://www.bep.gov/services/currency-accessibility/us-currency-reader-program/",
         type="money identifier", document="guide", access="full", rights=US_GOV,
         reason="a US government work; robots.txt allows the pages (in the reference library: "
                "vision:bep_currency_access)"),
]

GUIDANCE = [
    dict(title="Accessible prescription drug container labels (US Access Board; in the reference library: "
               "vision:access_board_rx_labels)", url="https://www.access-board.gov/rx.html",
         by="the US Access Board"),
    dict(title="State Assistive Technology Act programmes: device loans, reuse and repair (ACL; in the reference "
               "library: elec:acl_assistive_technology)",
         url="https://acl.gov/programs/assistive-technology/assistive-technology",
         by="the Administration for Community Living"),
    dict(title="VA Blind Rehabilitation Service (VIST coordinators arrange devices and their repair)",
         url="https://www.prosthetics.va.gov/blindrehab/index.asp", by="the US Department of Veterans Affairs"),
    dict(title="NLS equipment for NLS materials (players, repair and replacement through your network library)",
         url="https://www.loc.gov/nls/services-and-resources/equipment-for-nls-materials/",
         by="the National Library Service for the Blind and Print Disabled"),
]

CATEGORY = dict(
    name="Blind and low-vision living: braille writers, braille displays, magnifiers and talking devices (manuals)",
    description="Braille writers (the Perkins Brailler, Next Generation and SMART Brailler, Mountbatten and others) "
                "with their care and repair, slates and styluses, braille embossers and tactile graphics machines, "
                "screen reader and magnifier software (JAWS, ZoomText, Fusion, SuperNova, NVDA), reading machines, "
                "talking label and money readers, canes and describer apps: the Internet Archive's manuals, the "
                "makers' pages (links) and the government's programmes. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, documents=DOCUMENTS, guidance=GUIDANCE, notice=NOTICE)
