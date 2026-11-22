"""The collection "Fitness equipment and activity trackers (manuals)" (category key fitness_equipment): the owner's
request of 2026-11-22 (fitness and nutrition). categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (rowing machines, home gyms,
            weight benches, stair climbers, vibration plates, fitness trackers, heart rate monitors and pedometers);
            no word another
            collection already searches (treadmills, exercise bikes and ellipticals are home_appliances');
  makers    the big makers, LINK-ONLY by the owner's rule: their own manuals and guides are for the person (or the
            personal assistant) to open in a browser or fetch with Program Downloader; nothing is read from their
            sites (their terms keep all rights);
  guidance  the US government pages the reference library builds in full (textbooks/fitness_nutrition.py: the
            Physical Activity Guidelines and Move Your Way), as links.

The notice is said first (NOTICE): read the safety section, use the safety key or clip, keep children away from
moving machines, ask a doctor if you have a health condition; 911.
"""

NOTICE = ("Read the safety section first: use the treadmill's safety key or clip, keep children and pets away from "
          "moving machines, and check that the machine is assembled and anchored as its manual says. General "
          "information, not medical advice or a diagnosis: if you have a health condition, ask your doctor before you "
          "start a new exercise plan. In an emergency call 911; in a mental health crisis call or text 988.")

IA_WORDS = ["rowing machine", "rower", "home gym", "weight bench", "exercise machine", "stair climber", "stepper",
            "vibration plate", "fitness tracker", "heart rate monitor", "pedometer", "bowflex", "nordictrack",
            "concept2"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="fitness_equipment", prefix="fx", documents="manuals and instructions",
               access="link", reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="peloton",
         maker="Peloton",
         type="exercise bike, treadmill and rower",
         library="https://support.onepeloton.com/",
         site="support.onepeloton.com"),
    dict(key="nordictrack",
         maker="NordicTrack (iFIT)",
         type="treadmill, bike, elliptical and rower",
         library="https://www.nordictrack.com/",
         site="nordictrack.com"),
    dict(key="bowflex",
         maker="Bowflex (Johnson Health Tech)",
         type="home gym and adjustable weights",
         library="https://www.bowflex.com/",
         site="bowflex.com"),
    dict(key="concept2",
         maker="Concept2",
         type="rower, ski erg and bike erg",
         library="https://www.concept2.com/support",
         site="concept2.com"),
    dict(key="schwinn-fitness",
         maker="Schwinn Fitness",
         type="exercise bike",
         library="https://www.bowflex.com/schwinn-fitness",
         site="bowflex.com"),
    dict(key="garmin-fitness",
         maker="Garmin (fitness watches and heart rate monitors)",
         type="fitness tracker",
         library="https://support.garmin.com/",
         site="support.garmin.com"),
    dict(key="fitbit",
         maker="Fitbit (Google)",
         type="fitness tracker",
         library="https://support.google.com/fitbit",
         site="support.google.com"),
    dict(key="polar",
         maker="Polar",
         type="heart rate monitor and sports watch",
         library="https://support.polar.com/",
         site="support.polar.com"),
]]

GUIDANCE = [
               dict(title=("Physical Activity Guidelines for Americans (HHS; in the reference library: "
                          "fit:physical_activity_guidelines)"),
                    url="https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines",
                    by="the US Department of Health and Human Services"),
               dict(title="Move Your Way (HHS; in the reference library: fit:odphp_move_your_way)",
                    url="https://odphp.health.gov/moveyourway",
                    by="the US Department of Health and Human Services"),
           ]

CATEGORY = dict(
    name="Fitness equipment and activity trackers (manuals)",
    description=("Rowing machines, home gyms, weight benches, stair climbers, vibration plates, fitness trackers, "
                 "heart rate monitors and pedometers: the Internet Archive's manuals, the makers' manual pages (links)"
                 " and the government's physical activity guidance. Links only."),
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
