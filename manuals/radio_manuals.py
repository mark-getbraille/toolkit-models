"""Manual collections for RADIO COMMUNICATIONS, with their own heading (the owner's request of 2026-11-22: radio as its
own section, separate from preparedness). categories.py adds them to CATEGORIES, under names that start "Radio
communications:" so they appear together, on their own, in the manuals list:
  radio_two_way          GMRS, FRS, MURS and business two-way radios;
  radio_weather_alert    NOAA weather alert radios and emergency (hand-crank, solar) radios, including alert radios
                         for deaf and hard of hearing people;
  radio_ham_makers       amateur radio transceivers, handhelds, antennas and analysers by maker (Yaesu, Icom,
                         Kenwood, Baofeng, Alinco, Elecraft, AnyTone, Xiegu), digital voice (DMR, D-STAR, System
                         Fusion) and programming software;
  radio_mesh_satellite   off-grid mesh and data radio (Meshtastic and LoRa boards, goTenna, Beartooth), satellite
                         messengers (Garmin inReach, ZOLEO, SPOT) and personal locator beacons;
  radio_military_manuals US military radio and antenna manuals from the Internet Archive (public domain).

What each lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker): the Internet
Archive's manuals found with each category's words (words the existing ham_radio, marine_electronics and
personal_electronics categories already use are not repeated); the makers' own manual libraries, LINK-ONLY by the
owner's rule (nothing is read from their sites; the person opens them or fetches them with Program Downloader:
none of these makers' terms allow redistributing their manuals); public-domain military manuals (public_guides);
and guidance pages, with the reference library's key where the page is already a book (radio:).

Already elsewhere and not repeated: "Amateur radio, scanners and CB (manuals)" (ham_radio in more_categories.py: the
Digital Library of Amateur Radio and Communications, Kenwood's and Radio Shack's libraries, Uniden, Cobra, Midland and
Motorola collections), marine VHF radios (marine_electronics) and walkie-talkies as personal electronics.

The military manuals (radio_military_manuals): by the owner's rule of 2026-11-22 a military publication found openly on
archive.org is kept whether or not it prints Distribution Statement A, with a truthful notice; one printing a
restricted marking goes to personal use or link-only (this index is links only); classified markings only when
declassified or released. The shared check that reads each manual's front text (build_manuals.public_guide_entries) is
being changed to this rule on another branch; until it is merged it keeps only the manuals that print Distribution
Statement A or date from before 1964.

Every category's notice is RADIO_SAFETY (the same words as packs/radio_packs.py), said first.
"""

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is listed "
        "for the person to open or fetch with Program Downloader")
LICENCE = "CC0 (facts and links); each manual belongs to its maker; the military manuals are US government works"

RADIO_SAFETY = ("Radio safety: keep every antenna, mast and feed line far from power lines, more than the length of "
                "the antenna and mast from the nearest line (contact can kill). Never climb a tower without training "
                "and fall protection. Ground your station, and disconnect antennas when lightning is near. Follow the "
                "FCC's RF exposure limits and keep transmitting antennas away from people. Transmit only where you "
                "are licensed or the service allows it; encryption is not allowed on amateur frequencies; in an "
                "emergency, call 911 first.")
PLB_NOTE = ("Register a personal locator beacon with NOAA (free, beaconregistration.noaa.gov) and use it only in grave "
            "danger; a satellite messenger needs an active subscription to send an SOS.")

TWO_WAY_WORDS = ["gmrs", "frs radio", "family radio service", "two-way radio", "two way radio", "murs", "talkabout",
                 "business radio", "walkie-talkie"]
WEATHER_WORDS = ["weather radio", "weather alert radio", "noaa weather", "emergency radio", "crank radio",
                 "hand crank radio", "solar radio", "all hazards radio", "same weather radio"]
HAM_WORDS = ["yaesu", "icom", "baofeng", "alinco", "elecraft", "anytone", "xiegu", "dmr radio", "d-star",
             "system fusion", "antenna analyzer", "nanovna", "mobile transceiver", "dual band radio"]
MESH_WORDS = ["meshtastic", "lora", "gotenna", "beartooth", "satellite messenger", "inreach", "zoleo",
              "spot messenger", "personal locator beacon", "plb", "epirb"]
MILITARY_WORDS = ["radio set an/prc", "an/prc", "an/grc", "an/vrc", "sincgars", "tm 11-5820", "radio set",
                  "field radio"]


def _makers(category, prefix, documents, makers):
    """The makers of one category (all link-only), with the shared fields."""
    return [dict(category=category, prefix=prefix, types=[], documents=documents, access="link", reason=RULE, **m)
            for m in makers]


TWO_WAY_MAKERS = _makers("radio_two_way", "r2", "user manuals", [
    dict(key="midland", maker="Midland (GMRS and FRS radios)", type="GMRS and FRS radio",
         library="https://midlandusa.com/pages/manuals", site="midlandusa.com"),
    dict(key="motorola-talkabout", maker="Motorola Solutions (Talkabout and business radios)", type="two-way radio",
         library="https://www.motorolasolutions.com/en_us/support.html", site="motorolasolutions.com"),
    dict(key="cobra", maker="Cobra Electronics (two-way and CB radios)", type="two-way radio",
         library="https://www.cobra.com/", site="cobra.com"),
    dict(key="wouxun", maker="Wouxun", type="GMRS radio", library="https://wouxun.us/", site="wouxun.us"),
    dict(key="btech", maker="BTECH (BaoFeng Tech, GMRS radios)", type="GMRS radio", library="https://baofengtech.com/",
         site="baofengtech.com"),
    dict(key="rocky-talkie", maker="Rocky Talkie", type="FRS and GMRS radio", library="https://rockytalkie.com/",
         site="rockytalkie.com"),
    dict(key="retevis", maker="Retevis", type="two-way radio", library="https://www.retevis.com/", site="retevis.com"),
])
WEATHER_MAKERS = _makers("radio_weather_alert", "rw", "user manuals", [
    dict(key="midland-weather", maker="Midland (weather alert radios)", type="weather alert radio",
         library="https://midlandusa.com/pages/manuals", site="midlandusa.com"),
    dict(key="sangean", maker="Sangean", type="weather alert radio", library="https://www.sangean.com/",
         site="sangean.com"),
    dict(key="eton", maker="Eton (emergency and hand-crank radios)", type="emergency radio",
         library="https://etoncorp.com/", site="etoncorp.com"),
    dict(key="kaito", maker="Kaito Electronics", type="emergency radio", library="https://www.kaito-usa.com/",
         site="kaito-usa.com"),
    dict(key="reecom", maker="Reecom (weather alert radios with text displays)", type="weather alert radio",
         library="https://www.reecomradio.com/", site="reecomradio.com"),
])
HAM_MAKERS = _makers("radio_ham_makers", "rh", "operating and instruction manuals", [
    dict(key="yaesu", maker="Yaesu", type="amateur radio", library="https://www.yaesu.com/", site="yaesu.com"),
    dict(key="icom", maker="Icom America", type="amateur radio", library="https://www.icomamerica.com/",
         site="icomamerica.com"),
    dict(key="kenwood", maker="Kenwood (amateur radio; its older manuals are in ham_radio)", type="amateur radio",
         library="https://www.kenwood.com/usa/com/amateur/", site="kenwood.com"),
    dict(key="baofeng", maker="Baofeng", type="handheld radio", library="https://www.baofengradio.com/",
         site="baofengradio.com"),
    dict(key="alinco", maker="Alinco", type="amateur radio", library="https://www.alinco.com/", site="alinco.com"),
    dict(key="elecraft", maker="Elecraft", type="amateur radio", library="https://elecraft.com/", site="elecraft.com"),
    dict(key="anytone", maker="AnyTone (DMR radios)", type="DMR radio", library="https://www.anytone.net/",
         site="anytone.net"),
    dict(key="xiegu", maker="Xiegu", type="amateur radio", library="https://www.cqxiegu.com/", site="cqxiegu.com"),
    dict(key="rigexpert", maker="RigExpert (antenna analysers)", type="antenna analyser",
         library="https://rigexpert.com/", site="rigexpert.com"),
    dict(key="chirp", maker="CHIRP (radio programming software; free, GPL)", type="programming software",
         library="https://chirpmyradio.com/projects/chirp/wiki/Home", site="chirpmyradio.com"),
])
MESH_MAKERS = _makers("radio_mesh_satellite", "rm", "manuals and guides", [
    dict(key="meshtastic", maker="Meshtastic (documentation; in the reference library: radio:meshtastic_docs)",
         type="mesh radio firmware", library="https://meshtastic.org/docs/", site="meshtastic.org"),
    dict(key="lilygo", maker="LILYGO (T-Beam, T-Echo, T-Deck)", type="LoRa board", library="https://lilygo.cc/",
         site="lilygo.cc"),
    dict(key="heltec", maker="Heltec Automation", type="LoRa board", library="https://heltec.org/", site="heltec.org"),
    dict(key="rakwireless", maker="RAKwireless (WisBlock)", type="LoRa board", library="https://docs.rakwireless.com/",
         site="rakwireless.com"),
    dict(key="seeed", maker="Seeed Studio (SenseCAP trackers)", type="LoRa device", library="https://wiki.seeedstudio.com/",
         site="seeedstudio.com"),
    dict(key="gotenna", maker="goTenna", type="mesh device", library="https://gotenna.com/", site="gotenna.com"),
    dict(key="beartooth", maker="Beartooth", type="mesh device", library="https://beartooth.com/", site="beartooth.com"),
    dict(key="garmin-inreach", maker="Garmin (inReach satellite communicators)", type="satellite messenger",
         library="https://support.garmin.com/", site="garmin.com"),
    dict(key="zoleo", maker="ZOLEO", type="satellite messenger", library="https://www.zoleo.com/", site="zoleo.com"),
    dict(key="spot", maker="SPOT (Globalstar)", type="satellite messenger", library="https://www.findmespot.com/",
         site="findmespot.com"),
    dict(key="acr", maker="ACR Electronics (personal locator beacons)", type="personal locator beacon",
         library="https://www.acrartex.com/", site="acrartex.com"),
])


def _guide(ia, title, year, by="the US Army"):
    """One military radio or antenna manual: its Internet Archive item, title and year (military: its front text is
    read by the shared check)."""
    return dict(ia=ia, title=title, by=by, year=year, military=True)


MILITARY_GUIDES = [
    _guide("TC9-64", "Communications-Electronics Fundamentals: Wave Propagation, Transmission Lines, and Antennas "
           "(TC 9-64, 2004)", 2004),
    _guide("MCRP3-403C", "Antenna Handbook (MCRP 3-40.3C, 1999)", 1999, "the US Marine Corps"),
    _guide("TM11-2651", "Antenna Groups AN/GRA-4 and AN/GRA-12 (TM 11-2651, 1961)", 1961),
    _guide("TM11-2630", "Antenna Equipment RC-219A and Antenna AN-78-A (TM 11-2630, 1944)", 1944),
    _guide("TM11-2608", "Antenna System AS-81/GR (TM 11-2608, 1944)", 1944),
    _guide("TM11-2631", "Antenna Equipment RC-154-A (TM 11-2631, 1944)", 1944),
]

GUIDANCE = [
    dict(title="Amateur Radio Service rules (47 CFR Part 97; in the reference library: radio:cfr_47_97_amateur)",
         url="https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97",
         by="the Federal Communications Commission"),
    dict(title="Personal Radio Services rules: GMRS, FRS, MURS, CB (47 CFR Part 95; in the reference library: "
               "radio:cfr_47_95_personal_radio)", url="https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-95",
         by="the Federal Communications Commission"),
    dict(title="NCVEC question pools for the amateur licence exams (in the reference library: radio:ncvec_*)",
         url="https://www.ncvec.org/index.php/amateur-question-pools", by="the NCVEC Question Pool Committee"),
]
WEATHER_GUIDANCE = [
    dict(title="NOAA Weather Radio: how it works and SAME codes (in the reference library: prep:nwr_guide)",
         url="https://www.weather.gov/nwr/", by="the National Weather Service"),
    dict(title="NOAA Weather Radio stations and SAME codes by county (in the reference library: prep:nwr_stations)",
         url="https://www.weather.gov/nwr/counties", by="the National Weather Service"),
    dict(title="NOAA Weather Radio for people who are deaf or hard of hearing",
         url="https://www.weather.gov/nwr/special_needs", by="the National Weather Service"),
]
MESH_GUIDANCE = [
    dict(title="Meshtastic documentation (in the reference library: radio:meshtastic_docs)",
         url="https://meshtastic.org/docs/", by="the Meshtastic project (GPL-3.0)"),
    dict(title="Register a personal locator beacon (NOAA SARSAT)", url="https://beaconregistration.noaa.gov/",
         by="the National Oceanic and Atmospheric Administration"),
]

CATEGORIES = {
    "radio_two_way": dict(
        name="Radio communications: GMRS, FRS, MURS and business two-way radios (manuals)",
        description="Two-way radios for families, groups and businesses: GMRS (an FCC licence covers a family), FRS "
                    "and MURS (no licence) and business radios: the Internet Archive's manuals and the makers' manual "
                    "pages as links, with the FCC's rules in the reference library.",
        kind="manuals", licence=LICENCE, any_year=True, ia=TWO_WAY_WORDS, makers=TWO_WAY_MAKERS,
        notice=RADIO_SAFETY, guidance=GUIDANCE, ia_exclude=r"\b(sega|video game|game manual|toy|lucas ?arts)\b"),
    "radio_weather_alert": dict(
        name="Radio communications: weather alert and emergency radios (manuals)",
        description="NOAA weather alert radios (with SAME county codes), alert radios for deaf and hard of hearing "
                    "people, and emergency radios with hand cranks, solar panels and USB charging: the Internet "
                    "Archive's manuals, the makers' pages as links, and the National Weather Service's guidance.",
        kind="manuals", licence=LICENCE, any_year=True, ia=WEATHER_WORDS, makers=WEATHER_MAKERS,
        notice=RADIO_SAFETY + " Program your county's SAME code (the reference library's station list has every "
                              "county's code) so the radio alarms only for your area.",
        guidance=WEATHER_GUIDANCE, ia_exclude=r"\b(sega|video game|game manual|lucas ?arts)\b"),
    "radio_ham_makers": dict(
        name="Radio communications: amateur radio makers, digital voice and programming (manuals)",
        description="Amateur radio transceivers, handhelds, mobiles, antennas and analysers by maker (Yaesu, Icom, "
                    "Kenwood, Baofeng, Alinco, Elecraft, AnyTone, Xiegu, RigExpert), digital voice (DMR, D-STAR, "
                    "System Fusion) and CHIRP programming: the Internet Archive's manuals and the makers' pages as "
                    "links (older manuals are in Amateur radio, scanners and CB).",
        kind="manuals", licence=LICENCE, any_year=True, ia=HAM_WORDS, makers=HAM_MAKERS, notice=RADIO_SAFETY,
        guidance=GUIDANCE, ia_exclude=r"\b(sega|video game|game manual|lucas ?arts|catalog(?:ue)?s?)\b"),
    "radio_mesh_satellite": dict(
        name="Radio communications: mesh, LoRa and satellite messengers (manuals)",
        description="Off-grid mesh and data radio (Meshtastic and LoRa boards from LILYGO, Heltec, RAKwireless and "
                    "Seeed; goTenna; Beartooth), satellite messengers (Garmin inReach, ZOLEO, SPOT) and personal "
                    "locator beacons: the Internet Archive's manuals and the makers' pages as links, with Meshtastic's "
                    "documentation in the reference library.",
        kind="manuals", licence=LICENCE, any_year=True, ia=MESH_WORDS, makers=MESH_MAKERS,
        notice=RADIO_SAFETY + " " + PLB_NOTE, guidance=MESH_GUIDANCE,
        ia_exclude=r"\b(sega|video game|game manual|lucas ?arts|lorazepam|loratadine)\b"),
    "radio_military_manuals": dict(
        name="Radio communications: military radio and antenna manuals (public domain)",
        description="US military radio and antenna manuals: wave propagation, transmission lines and antennas (TC "
                    "9-64), the Marine Corps antenna handbook, antenna equipment manuals of the 1940s to 1960s, and "
                    "the Internet Archive's radio set manuals (index links). Military equipment and frequencies; the "
                    "physics is the same as for amateur radio.",
        kind="manuals", licence=LICENCE, any_year=True, ia=MILITARY_WORDS, public_guides=MILITARY_GUIDES,
        notice=RADIO_SAFETY + " These are military manuals: their frequencies and equipment are military ones; "
                              "transmit only where you are licensed.",
        ia_exclude=r"\b(weapons?|ammunition|missile|fire control|explosive|demolition)\b"),
}
