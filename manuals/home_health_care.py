"""The home health care collections of the manual library (the owner's life-skills requests of 2026-11-22):
categories.py adds CATEGORIES to its own. Home medical and mobility equipment (wheelchairs, oxygen concentrators,
CPAP) is the category home_medical, and home test kits home_health_tests: not repeated.

The categories, each an INDEX of facts and links only (each document belongs to its maker):
  first_aid_home_care  AEDs (automated external defibrillators), epinephrine auto-injector trainers and patient
                       instructions, first aid kits, thermometers, blood pressure monitors, pulse oximeters,
                       nebulisers, peak flow meters and spacers, insulin pens, pill organisers and medication
                       reminders, TENS units and heating pads;
  dental_care_devices  electric toothbrushes, water flossers, denture cleaners, night guards and retainer cases;
  eye_care_optics      optical magnifiers (handheld, stand, dome), reading glasses, contact lens cases and cleaners,
                       eye drop guides, and the US Navy Opticalman manuals;
  birth_postpartum     breast pumps (makers and device records; their Internet Archive manuals are baby_gear's), baby
                       thermometers, baby scales, fetal dopplers and nasal aspirators.
Each lists the Internet Archive's manuals (searched by its IA words), the FDA's device identifiers of over-the-counter
devices (udi: brand, model, maker and barcode numbers from AccessGUDID, public domain), the makers' own instructions
as LINKS (the owner's rule: nothing is read from their sites), public-domain US military manuals where one exists
(public_guides: kept only when its own front text says "Approved for public release" and shows no restricted marking,
build_manuals.public_guide_entries), and the official guidance pages (links). Each says its notice first.
"""

EMERGENCY = ("In an emergency, call 911 (or your local emergency number). Use a device only as its own instructions "
             "say; this is general information, not medical training or a diagnosis: ask a doctor, nurse or "
             "pharmacist.")
DENTAL = ("Follow the device's own instructions. For a knocked-out tooth, a swollen face or a bad toothache, see a "
          "dentist today. This is general information, not a diagnosis: ask your dentist.")
EYE = ("Never rinse or store contact lenses in tap water or saliva. Sudden loss of vision, a chemical splash or an "
       "eye injury is an emergency: call 911. This is general information, not a diagnosis: ask your eye doctor.")
BIRTH = ("A fever in a baby under 3 months is urgent: call the doctor at once; in an emergency call 911. Follow each "
         "device's own instructions. This is general information, not medical advice: ask your midwife, nurse or "
         "doctor.")

RULE = ("by the owner's rule the maker's own instructions and manuals are link-only: nothing is read from its site; "
        "its page is listed for the person to open")


def _makers(category, prefix, makers):
    """The link-only makers of one category, with the shared fields."""
    return [dict(dict(category=category, prefix=prefix, documents="instructions and manuals", access="link",
                      reason=RULE, types=[]), **m) for m in makers]


def _guide(ia, title, by, year, military=True):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military manual (whose front text must say it is approved for public release)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


FIRST_AID_MAKERS = _makers("first_aid_home_care", "fa", [
    dict(key="philips-heartstart", maker="Philips HeartStart (AEDs)", type="AED",
         library="https://www.usa.philips.com/healthcare/solutions/emergency-care-resuscitation", site="philips.com"),
    dict(key="zoll-aed", maker="ZOLL (AED Plus, AED 3)", type="AED", library="https://www.zoll.com/support",
         site="zoll.com"),
    dict(key="cardiac-science", maker="Cardiac Science Powerheart (Zoll)", type="AED",
         library="https://www.zoll.com/support", site="zoll.com"),
    dict(key="physio-control", maker="Stryker LIFEPAK (Physio-Control)", type="AED",
         library="https://www.stryker.com/us/en/emergency-care.html", site="stryker.com"),
    dict(key="defibtech", maker="Defibtech", type="AED", library="https://www.defibtech.com/", site="defibtech.com"),
    dict(key="epipen", maker="EpiPen (Viatris)", type="epinephrine auto-injector (patient instructions)",
         library="https://www.epipen.com/", site="epipen.com"),
    dict(key="auvi-q", maker="Auvi-Q (Kaléo)", type="epinephrine auto-injector (patient instructions)",
         library="https://www.auvi-q.com/", site="auvi-q.com"),
    dict(key="omron", maker="Omron Healthcare", type="blood pressure monitors and nebulisers",
         library="https://omronhealthcare.com/support", site="omronhealthcare.com"),
    dict(key="braun-thermometers", maker="Braun (Kaz) thermometers", type="thermometers",
         library="https://www.braunhealthcare.com/us_en/support", site="braunhealthcare.com"),
    dict(key="welch-allyn", maker="Welch Allyn (Hillrom)", type="thermometers and blood pressure",
         library="https://www.hillrom.com/en/support/", site="hillrom.com"),
])
DENTAL_MAKERS = _makers("dental_care_devices", "dc", [
    dict(key="oral-b", maker="Oral-B", type="electric toothbrushes", library="https://oralb.com/en-us/support",
         site="oralb.com"),
    dict(key="philips-sonicare", maker="Philips Sonicare", type="electric toothbrushes",
         library="https://www.usa.philips.com/c-m-pe/electric-toothbrushes", site="philips.com"),
    dict(key="waterpik", maker="Waterpik", type="water flossers", library="https://www.waterpik.com/support/",
         site="waterpik.com"),
    dict(key="polident", maker="Polident (Haleon)", type="denture cleaners", library="https://www.polident.com/",
         site="polident.com"),
])
EYE_MAKERS = _makers("eye_care_optics", "ey", [
    dict(key="eschenbach", maker="Eschenbach Optik", type="optical magnifiers",
         library="https://www.eschenbach.com/", site="eschenbach.com"),
    dict(key="schweizer", maker="Schweizer Optik", type="optical magnifiers", library="https://www.schweizer-optik.de/",
         site="schweizer-optik.de"),
    dict(key="carson", maker="Carson Optical", type="magnifiers and monoculars", library="https://carson.com/support/",
         site="carson.com"),
    dict(key="bausch-lomb", maker="Bausch + Lomb", type="contact lens solutions and eye drops",
         library="https://www.bausch.com/", site="bausch.com"),
    dict(key="alcon", maker="Alcon", type="contact lenses and solutions", library="https://www.alcon.com/",
         site="alcon.com"),
    dict(key="autodrop", maker="Owen Mumford Autodrop", type="eye drop guide", library="https://www.owenmumford.com/",
         site="owenmumford.com"),
])
BIRTH_MAKERS = _makers("birth_postpartum", "bp", [
    dict(key="medela", maker="Medela", type="breast pumps", library="https://www.medela.us/support",
         site="medela.us"),
    dict(key="spectra", maker="Spectra Baby USA", type="breast pumps", library="https://www.spectrababyusa.com/",
         site="spectrababyusa.com"),
    dict(key="lansinoh", maker="Lansinoh", type="breast pumps and postpartum care", library="https://lansinoh.com/",
         site="lansinoh.com"),
    dict(key="frida", maker="Frida (Fridababy, Frida Mom)", type="nasal aspirators and postpartum care",
         library="https://frida.com/", site="frida.com"),
])

CATEGORIES = {
    "first_aid_home_care": dict(
        name="First aid and home care devices (instructions)",
        description="AEDs, epinephrine auto-injectors (patient instructions and trainers), first aid kits, "
                    "thermometers, blood pressure monitors, pulse oximeters, nebulisers, peak flow meters and spacers, "
                    "insulin pens, pill organisers and medication reminders, TENS units and heating pads: manuals at "
                    "the Internet Archive, the FDA's device records with barcode numbers, the makers' instructions "
                    "(links), the US Navy Hospital Corpsman manual, and CDC's and the NHS's guidance (links).",
        kind="manuals", licence="CC0 (facts and links); FDA device records and US Navy manuals are public domain; "
                                "each other document belongs to its maker",
        ia=["aed", "defibrillator", "heartstart", "epinephrine", "auto-injector", "first aid kit", "thermometer",
            "blood pressure monitor", "pulse oximeter", "nebulizer", "peak flow meter", "inhaler spacer",
            "insulin pen", "pill organizer", "medication reminder", "tens unit", "heating pad"],
        udi=['"defibrillator"', '"thermometer"', '"sphygmomanometer"', '"oximeter"', '"nebulizer"',
             '"peak flow"', '"first aid kit"', '"heating pad"'],
        makers=FIRST_AID_MAKERS, notice=EMERGENCY,
        public_guides=[_guide("Hospital_Corpsman_NAVEDTRA_14295", "Hospital Corpsman (NAVEDTRA 14295)",
                              "the US Navy", None)],
        guidance=[dict(title="CPR and AED: what to do (CDC heart disease pages; in the reference library: "
                             "firstaid:cdc_stroke_heart)", url="https://www.cdc.gov/heart-disease/index.html",
                       by="the US Centers for Disease Control and Prevention"),
                  dict(title="Anaphylaxis and adrenaline auto-injectors (NHS; in the reference library: "
                             "firstaid:nhs_emergency_first_aid)", url="https://www.nhs.uk/conditions/anaphylaxis/",
                       by="the NHS (Open Government Licence v3.0)")]),
    "dental_care_devices": dict(
        name="Dental care devices (instructions)",
        description="Electric toothbrushes, water flossers, denture cleaners, night guards and retainer cases: "
                    "manuals at the Internet Archive, the FDA's device records with barcode numbers, the makers' "
                    "instructions (links), the US Navy's dental assistant course, and NIDCR's guidance (links).",
        kind="manuals", licence="CC0 (facts and links); FDA device records and US Navy courses are public domain; "
                                "each other document belongs to its maker",
        ia=["electric toothbrush", "sonic toothbrush", "water flosser", "oral irrigator", "denture cleaner",
            "night guard", "retainer case"],
        udi=['"toothbrush"', '"oral irrigator"', '"denture"'], makers=DENTAL_MAKERS, notice=DENTAL,
        public_guides=[_guide("DTIC_ADA218590", "Dental Assistant, Advanced (US Navy course, revision 1989)",
                              "the US Navy", 1989)],
        guidance=[dict(title="Oral hygiene (NIDCR; in the reference library: dental:nidcr_health_info)",
                       url="https://www.nidcr.nih.gov/health-info/oral-hygiene",
                       by="the National Institute of Dental and Craniofacial Research")]),
    "eye_care_optics": dict(
        name="Eye care and optical aids (instructions)",
        description="Optical magnifiers (handheld, stand and dome magnifiers, magnifying glasses, reading lenses), "
                    "monoculars and telescopes for distance, reading glasses, contact lens cases and cleaners, and "
                    "eye drop guides: manuals at the Internet Archive, the FDA's device records with barcode "
                    "numbers, the makers' instructions (links), the US Navy Opticalman manuals, and the FDA's and "
                    "NEI's guidance (links). Electronic video magnifiers are the electronics collections'.",
        kind="manuals", licence="CC0 (facts and links); FDA device records and US Navy manuals are public domain; "
                                "each other document belongs to its maker",
        ia=["magnifier", "magnifying glass", "dome magnifier", "stand magnifier", "loupe", "monocular",
            "reading glasses", "contact lens case", "lens cleaner", "eye drop guide"],
        udi=['"magnifier"', '"contact lens"', '"spectacle"'], makers=EYE_MAKERS, notice=EYE,
        public_guides=[_guide("opticalman32nave015103mbp", "Opticalman 3 & 2 (NAVEDTRA 10215, 1989)", "the US Navy",
                              1989),
                       _guide("opticalman1cdepa004061mbp", "Opticalman 1 & C (US Navy, 1991)", "the US Navy", 1991)],
        guidance=[dict(title="Contact lenses (FDA; in the reference library: eyes:fda_contact_lenses)",
                       url="https://www.fda.gov/medical-devices/consumer-products/contact-lenses",
                       by="the US Food and Drug Administration"),
                  dict(title="How to put in eye drops (National Eye Institute)",
                       url="https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/glaucoma/"
                           "glaucoma-medicines/how-put-eye-drops", by="the National Eye Institute")]),
    "birth_postpartum": dict(
        name="Birth, breastfeeding and newborn care devices (instructions)",
        description="Breast pumps, baby thermometers, baby scales, fetal dopplers and nasal aspirators: manuals "
                    "at the Internet Archive (breast pump manuals are searched by the category baby_gear), the FDA's "
                    "device records with barcode "
                    "numbers, the makers' instructions (links), and CDC's and the FDA's guidance (links).",
        kind="manuals", licence="CC0 (facts and links); FDA device records are public domain; each other document "
                                "belongs to its maker",
        ia=["baby thermometer", "baby scale", "fetal doppler", "nasal aspirator"],
        udi=['"breast pump"', '"fetal"'], makers=BIRTH_MAKERS, notice=BIRTH,
        guidance=[dict(title="Breast pumps (FDA)", url="https://www.fda.gov/medical-devices/consumer-products/"
                                                      "breast-pumps", by="the US Food and Drug Administration"),
                  dict(title="Hear Her: urgent maternal warning signs (CDC; in the reference library: "
                             "birth:cdc_hear_her)", url="https://www.cdc.gov/hearher/",
                       by="the US Centers for Disease Control and Prevention")]),
}
