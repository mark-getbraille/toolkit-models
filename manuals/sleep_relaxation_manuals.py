"""The collection "Light therapy lamps, sound machines and wake-up lights (manuals)" (category key sleep_relaxation):
the owner's request of 2026-11-22 (mental health and wellbeing). categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (light therapy lamps, SAD
            lamps, white noise and sound machines, sunrise alarms and wake-up lights); no word another
            collection already searches (CPAP machines are home_medical's);
  makers    the big makers, LINK-ONLY by the owner's rule: their own manuals and guides are for the person (or the
            personal assistant) to open in a browser or fetch with Program Downloader; nothing is read from their
            sites (their terms keep all rights);
  guidance  the US government pages the reference library builds in full (textbooks/mental_health.py and
            fitness_nutrition.py: NIMH's topics, CDC's and NHLBI's sleep pages), as links.

The notice is said first (NOTICE): not medical advice; 911 and 988.
"""

NOTICE = ("Use each device as its own instructions say. General information, not medical advice or a diagnosis: ask "
          "your doctor about light therapy, especially with eye conditions or bipolar disorder. In an emergency call "
          "911; in a mental health crisis call or text 988.")

IA_WORDS = ["light therapy", "sad lamp", "light box", "white noise", "sound machine", "sunrise alarm",
            "wake-up light", "sleep sound"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="sleep_relaxation", prefix="sr", documents="manuals and instructions",
               access="link", reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="philips-wake-up-light",
         maker="Philips (wake-up lights)",
         type="wake-up light",
         library="https://www.usa.philips.com/c-m-li/light-therapy",
         site="usa.philips.com"),
    dict(key="hatch",
         maker="Hatch (Restore, Rest)",
         type="sunrise alarm and sound machine",
         library="https://www.hatch.co/",
         site="hatch.co"),
    dict(key="verilux",
         maker="Verilux (HappyLight)",
         type="light therapy lamp",
         library="https://verilux.com/",
         site="verilux.com"),
    dict(key="carex",
         maker="Carex (Day-Light)",
         type="light therapy lamp",
         library="https://carex.com/",
         site="carex.com"),
    dict(key="yogasleep",
         maker="Yogasleep (Marpac, Dohm)",
         type="white noise machine",
         library="https://www.yogasleep.com/",
         site="yogasleep.com"),
    dict(key="lectrofan",
         maker="LectroFan (Adaptive Sound Technologies)",
         type="white noise machine",
         library="https://www.lectrofan.com/",
         site="lectrofan.com"),
]]

GUIDANCE = [
               dict(title="Seasonal affective disorder (NIMH; in the reference library: mind:nimh_health_topics)",
                    url="https://www.nimh.nih.gov/health/publications/seasonal-affective-disorder",
                    by="the National Institute of Mental Health"),
               dict(title="Sleep (CDC; in the reference library: fit:cdc_sleep)",
                    url="https://www.cdc.gov/sleep/index.html",
                    by="the US Centers for Disease Control and Prevention"),
           ]

CATEGORY = dict(
    name="Light therapy lamps, sound machines and wake-up lights (manuals)",
    description=("Light therapy lamps and light boxes, white noise and sound machines, sunrise alarms and wake-up "
                 "lights: the Internet Archive's manuals, the makers' manual pages (links) and the government's sleep "
                 "and seasonal depression guidance. Links only."),
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
