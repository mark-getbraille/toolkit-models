"""Eye care, glasses, contact lenses and low vision for the reference library, in the group "Reference, home health
care and first aid" (the owner's request of 2026-11-22). Keys: eye-care (every book), eyes:<name>. The eye care
products book (eye medicines by use, contact lens care products, device records) is eyecare_products.py.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the National Eye Institute's eye health information (NIH): eye conditions and diseases (cataracts, glaucoma,
    macular degeneration, diabetic retinopathy, retinitis pigmentosa, dry eye, pink eye, floaters, retinal
    detachment and the rest), healthy vision (eye exams, eye safety and protective eyewear), low vision and vision
    rehabilitation, children's vision, and how to put in eye drops, every page;
  - CDC's Vision Health pages (common eye problems, keeping eyes healthy, eye safety, children's vision), kept whole;
  - the FDA's contact lens pages (types of lenses, everyday eye care, the risks, solutions and products, hydrogen
    peroxide solutions and their neutralising step, buying lenses and the prescription, decorative lenses);
  - the NHS's eye pages (cataracts, glaucoma, macular degeneration, diabetic retinopathy, dry eyes, floaters and
    flashes, vision loss), with the non-US note;
  - the VA Blind Rehabilitation Service's pages (what blind and low vision rehabilitation is, the Blind
    Rehabilitation Centers, VIST coordinators, its fact sheets).
  (The NLS informational publications are guide:nls_informational_publications; MedlinePlus's summaries are
  mlp:health_topics: not repeated.)

Every book starts with the eye note: sudden vision loss, flashes with a curtain or shadow over your sight, a
chemical in the eye or an eye injury is an emergency (for a chemical, rinse the eye with clean running water for at
least 15 minutes and call 911); general information, not a diagnosis; ask your eye doctor.

Not built (NOT_INCLUDED): the American Academy of Ophthalmology, AFB, APH, Perkins, NFB and Prevent Blindness
(copyright: link-only), Wikibooks (in Kiwix already).

Licences: US government works (NEI, FDA's website policies "in the public domain and may be republished", VA); CDC's
terms; the NHS's Open Government Licence v3.0.

Run from the repository's folder:
  python3 textbooks/eye_care.py eyes:nei_eye_health --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import first_aid as F  # noqa: E402 - the helpers of the home health modules

GROUP = F.GROUP
NOTE = ("Sudden loss of vision, flashes with a curtain or shadow over your sight, a chemical in the eye or an eye "
        "injury is an emergency: for a chemical, rinse the eye with clean running water for at least 15 minutes, "
        "and call 911 (or your local emergency number) or go to an emergency room. This is general information, "
        "not a diagnosis: ask your eye doctor.")
FDA_POLICY = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished, reprinted and otherwise used freely"

GUIDES = [
    K.guide(GROUP, "nei_eye_health", "Eye health information (National Eye Institute)", "Eye care",
            "National Eye Institute (NEI), National Institutes of Health",
            "https://www.nei.nih.gov/eye-health-information",
            r"^https://www\.nei\.nih\.gov/eye-health-information(/[a-z0-9-]+){1,4}$",
            "The National Eye Institute's pages for the public, every page: eye conditions and diseases (cataracts, "
            "glaucoma, age-related macular degeneration, diabetic retinopathy, retinitis pigmentosa, dry eye, pink "
            "eye, floaters, retinal detachment, refractive errors, colour blindness and more: symptoms, causes, "
            "treatment), healthy vision (eye exams, eye safety and protective eyewear, sunglasses, contact lens "
            "safety), low vision and vision rehabilitation, children's vision, and how to use eye drops.",
            NOTE + " A work of the National Institutes of Health (public domain).", depth=3,
            follow=r"^https://www\.nei\.nih\.gov/eye-health-information(/[a-z0-9-]+){1,3}$",
            units=[(r"/eye-conditions-and-diseases", "Eye conditions and diseases"),
                   (r"/healthy-vision", "Healthy vision and eye safety"), (r"/low-vision", "Low vision"),
                   (r".", "More about eye health")], limit=400),
    F.cdc_book(GROUP, "cdc_vision_health", "Vision Health (CDC)", "Eye care", ["vision-health"],
               "CDC's Vision Health pages, every page: common eye disorders and diseases, keeping your eyes healthy, "
               "eye safety at home, at work and in sport, children's vision, and vision loss.",
               units=[(r".", "Vision health")], note=NOTE),
    dict(K.guide(GROUP, "fda_contact_lenses", "Contact lenses: types, care, solutions and risks (FDA)", "Eye care",
                 "US Food and Drug Administration (FDA)",
                 "https://www.fda.gov/medical-devices/consumer-products/contact-lenses",
                 r"^https://www\.fda\.gov/medical-devices/(consumer-products/contact-lenses|contact-lenses/"
                 r"[a-z0-9-]+)$",
                 "The FDA's contact lens pages, every page: types of contact lenses, everyday eye care (never rinse "
                 "or store lenses in tap water or saliva, replace the case), the risks and the warning signs of an "
                 "eye infection, contact lens solutions and products (multipurpose solutions, hydrogen peroxide "
                 "solutions and their neutralising step, saline, rewetting drops), buying lenses and the "
                 "prescription, decorative lenses, and how to report a problem.",
                 NOTE + " A work of the US Food and Drug Administration (public domain).", depth=1, limit=30),
         licence_page=FDA_POLICY, licence_text=FDA_TEXT),
    F.nhs_book(GROUP, "nhs_eyes", "Cataracts, glaucoma, macular degeneration and other eye conditions (NHS)",
               "Eye care (UK)",
               ["conditions/cataracts", "conditions/glaucoma", "conditions/age-related-macular-degeneration-amd",
                "conditions/diabetic-retinopathy", "symptoms/dry-eyes", "symptoms/floaters-and-flashes-in-the-eyes",
                "conditions/vision-loss"],
               "The NHS's eye pages, each whole: cataracts, glaucoma, age-related macular degeneration, diabetic "
               "retinopathy, dry eyes, floaters and flashes (and when they are an emergency), and vision loss "
               "(sight tests, registering as sight impaired, help and support).", note=NOTE),
    K.guide(GROUP, "va_blind_rehabilitation", "Blind Rehabilitation Service (VA)", "Low vision and blindness",
            "Blind Rehabilitation Service, US Department of Veterans Affairs", "https://www.rehab.va.gov/blindrehab/",
            r"^https://www\.rehab\.va\.gov/PROSTHETICS/blindrehab/[A-Za-z0-9_-]+\.asp$",
            "The VA Blind Rehabilitation Service's pages, every page: what blind and low vision rehabilitation is "
            "(orientation and mobility, living skills, low vision therapy, assistive technology), the Blind "
            "Rehabilitation Centers and outpatient services, the Visual Impairment Services Team (VIST) "
            "coordinators, and how veterans are referred.",
            NOTE + " A work of the US Department of Veterans Affairs (public domain).", depth=1, limit=40),
]

COLLECTION = K.Collection("eyes", GROUP, guides=GUIDES,
                          words={"eye-care": lambda: [f"eyes:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "eyes_nei_va": "www.nei.nih.gov and www.rehab.va.gov: works of the US government (17 U.S.C. 105, checked on "
                   "govinfo.gov's policies page at every build); robots.txt allows the pages; no AI rules (checked "
                   "2026-11-22).",
    "eyes_fda": "www.fda.gov/about-fda/about-website/website-policies (checked at every build): FDA's pages \"are in "
                "the public domain and may be republished, reprinted and otherwise used freely\"; robots.txt allows "
                "/medical-devices/; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("American Academy of Ophthalmology (EyeSmart), Prevent Blindness, AFB, APH, Perkins and NFB eye and low vision "
     "guides", "Copyright of each organisation (checked 2026-11-22); not openly licensed. Link-only. Index: "
     "https://www.aao.org/eye-health , https://preventblindness.org/ , https://www.afb.org/ , "
     "https://www.aph.org/ , https://www.perkins.org/resources/ and https://nfb.org/"),
    ("White cane care and orientation and mobility guides", "No openly licensed or US government guide to cane care "
     "and repair was found beyond the VA's rehabilitation pages built here (the cane makers' and NFB's guides are "
     "copyright, checked 2026-11-22). Link-only. Index: https://nfb.org/programs-services/free-white-cane-program"),
    ("Glasses repair (tightening hinges, replacing nose pads and screws)", "No open guide was found; the opticians' "
     "and makers' pages are copyright and iFixit's guides are linked from the manual library (its terms keep API "
     "answers 24 hours only). Index: https://www.ifixit.com/Device/Eyeglasses"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
