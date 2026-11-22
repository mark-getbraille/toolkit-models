"""The collection "Medical alert systems, hearing amplifiers and other aging-in-place devices (manuals)" (category
key aging_in_place): the owner's request of 2026-11-22 (aging and end-of-life planning). categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (medical alert and personal
            emergency response systems, hearing amplifiers and over-the-counter hearing aids, automatic pill
            dispensers, bath lifts); no word another
            collection already searches (lift chairs, bed rails, stair lifts and walkers are home_medical's;
            amplified and large-button phones accessibility's);
  makers    the big makers, LINK-ONLY by the owner's rule: their own manuals and guides are for the person (or the
            personal assistant) to open in a browser or fetch with Program Downloader; nothing is read from their
            sites (their terms keep all rights);
  guidance  the US government pages the reference library builds in full (textbooks/aging_end_of_life.py: NIDCD's
            hearing pages, ACL's long-term care guide, the VA's geriatrics pages), as links.

The notice is said first (NOTICE): test a medical alert regularly; it does not replace 911; ask a doctor, audiologist
or occupational therapist; 911 and 988.
"""

NOTICE = ("Test a medical alert button regularly as its instructions say; in an emergency call 911 if you can. Use "
          "each device as its own instructions say. General information, not medical advice or a diagnosis: ask your "
          "doctor, audiologist or occupational therapist which device fits. In a mental health crisis call or text "
          "988.")

IA_WORDS = ["medical alert", "personal emergency response", "hearing amplifier", "personal sound amplifier",
            "pill dispenser", "bath lift"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="aging_in_place", prefix="ag", documents="manuals and instructions", access="link", reason=RULE,
               types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="lifeline",
         maker="Lifeline (Philips Lifeline, now Connect America)",
         type="medical alert system",
         library="https://www.lifeline.com/",
         site="lifeline.com"),
    dict(key="medical-guardian",
         maker="Medical Guardian",
         type="medical alert system",
         library="https://www.medicalguardian.com/",
         site="medicalguardian.com"),
    dict(key="bay-alarm",
         maker="Bay Alarm Medical",
         type="medical alert system",
         library="https://www.bayalarmmedical.com/",
         site="bayalarmmedical.com"),
    dict(key="hero",
         maker="Hero Health",
         type="automatic pill dispenser",
         library="https://herohealth.com/",
         site="herohealth.com"),
    dict(key="medminder",
         maker="MedMinder",
         type="automatic pill dispenser",
         library="https://www.medminder.com/",
         site="medminder.com"),
    dict(key="jabra-enhance",
         maker="Jabra Enhance",
         type="over-the-counter hearing aid",
         library="https://www.jabraenhance.com/",
         site="jabraenhance.com"),
    dict(key="lexie",
         maker="Lexie Hearing (hearX)",
         type="over-the-counter hearing aid",
         library="https://lexiehearing.com/",
         site="lexiehearing.com"),
]]

GUIDANCE = [
               dict(title="Over-the-counter hearing aids (NIDCD; in the reference library: aging:nidcd_hearing)",
                    url="https://www.nidcd.nih.gov/health/over-counter-hearing-aids",
                    by="the National Institute on Deafness and Other Communication Disorders"),
               dict(title="Hearing aids (FDA)",
                    url="https://www.fda.gov/medical-devices/consumer-products/hearing-aids",
                    by="the US Food and Drug Administration"),
               dict(title=("Long-term care and staying in your home (ACL; in the reference library: "
                          "aging:acl_long_term_care)"),
                    url="https://acl.gov/ltc/housing/staying-in-your-home",
                    by="the Administration for Community Living"),
           ]

CATEGORY = dict(
    name="Medical alert systems, hearing amplifiers and other aging-in-place devices (manuals)",
    description=("Medical alert and personal emergency response systems, hearing amplifiers and over-the-counter "
                 "hearing aids, automatic pill dispensers and bath lifts: the Internet Archive's manuals, the makers' "
                 "manual pages (links) and NIDCD's, FDA's and ACL's guidance. Links only."),
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
