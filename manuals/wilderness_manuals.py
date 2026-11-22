"""The collection "Wilderness first aid kits, splints and avalanche gear (manuals)" (category key
wilderness_first_aid): the owner's request of 2026-11-22 (wilderness and remote first aid). categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (avalanche transceivers and
            beacons, trauma kits, SAM splints and emergency bivvies); no word another
            collection already searches (personal locator beacons and satellite messengers are radio_mesh_satellite's
            (the radio section), first aid kits first_aid_home_care's);
  makers    the big makers, LINK-ONLY by the owner's rule: their own manuals and guides are for the person (or the
            personal assistant) to open in a browser or fetch with Program Downloader; nothing is read from their
            sites (their terms keep all rights);
  guidance  the US government pages the reference library builds in full (textbooks/wilderness_first_aid.py: NOAA
            SARSAT's beacon pages, the Park Service's and Forest Service's safety pages), as links.

The notice is said first (NOTICE): call 911 or use the SOS of a messenger or PLB; not training; take a course.
"""

NOTICE = ("General information, not training, medical advice or a diagnosis. In an emergency call 911, or use the SOS "
          "of a satellite messenger or a personal locator beacon (PLB) where there is no phone signal. Take a "
          "wilderness first aid course before you go, and practise with an avalanche transceiver before you need it.")

IA_WORDS = ["avalanche transceiver", "avalanche beacon", "trauma kit", "sam splint", "emergency bivy"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="wilderness_first_aid", prefix="wf", documents="manuals and instructions",
               access="link", reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="adventure-medical-kits",
         maker="Adventure Medical Kits",
         type="wilderness first aid kit",
         library="https://www.adventuremedicalkits.com/",
         site="adventuremedicalkits.com"),
    dict(key="sam-medical",
         maker="SAM Medical (SAM Splint)",
         type="splint",
         library="https://www.sammedical.com/",
         site="sammedical.com"),
    dict(key="mymedic",
         maker="MyMedic",
         type="first aid and trauma kit",
         library="https://mymedic.com/",
         site="mymedic.com"),
    dict(key="bca",
         maker="Backcountry Access (BCA)",
         type="avalanche transceiver",
         library="https://backcountryaccess.com/",
         site="backcountryaccess.com"),
    dict(key="mammut-barryvox",
         maker="Mammut (Barryvox)",
         type="avalanche transceiver",
         library="https://www.mammut.com/",
         site="mammut.com"),
    dict(key="ortovox",
         maker="Ortovox",
         type="avalanche transceiver",
         library="https://www.ortovox.com/",
         site="ortovox.com"),
]]

GUIDANCE = [
               dict(title=("406 MHz distress beacons and registering one (NOAA SARSAT; in the reference library: "
                          "wild:noaa_sarsat_beacons; beacon and messenger manuals: the radio collection "
                          "radio_mesh_satellite)"),
                    url="https://www.sarsat.noaa.gov/emergency-406-beacons/",
                    by="NOAA"),
               dict(title=("Hike Smart and the ten essentials (National Park Service; in the reference library: "
                          "wild:nps_hiking_backcountry_safety)"),
                    url="https://www.nps.gov/articles/10essentials.htm",
                    by="the National Park Service"),
               dict(title="Avalanches (US Forest Service; in the reference library: wild:usfs_backcountry_safety)",
                    url="https://www.fs.usda.gov/visit/know-before-you-go/avalanches",
                    by="the US Forest Service"),
           ]

CATEGORY = dict(
    name="Wilderness first aid kits, splints and avalanche gear (manuals)",
    description=("Wilderness and trauma first aid kits, SAM splints, emergency bivvies and avalanche transceivers: the"
                 " Internet Archive's manuals, the makers' manual pages (links) and the Park Service's, Forest "
                 "Service's and NOAA's guidance. Beacons and messengers are the radio collection's. Links only."),
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
