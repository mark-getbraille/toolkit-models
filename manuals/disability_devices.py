"""Two collections of the manual library for disabilities other than blindness (the owner's request of 2026-11-22):
categories.py adds CATEGORIES to its own.

  hearing_communication_devices  hearing aids, cochlear implants and bone-anchored implants, assistive listening
                                 (FM and loop systems, pocket amplifiers), captioned and amplified telephones,
                                 alerting devices (flashing doorbells, bed shakers, vibrating alarm clocks) and AAC
                                 devices (speech-generating devices and communication apps);
  wheelchairs_mobility_vehicles  the wheelchair, power chair, scooter and patient lift makers, and the vehicle
                                 adaptations (wheelchair-accessible vans, lifts, hand controls, transfer seats).

Each is an INDEX of facts and links only (each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by words no other collection searches: "hearing aid",
            "tty" and "amplified phone" are the accessibility collection's, and "wheelchair", "power chair",
            "mobility scooter", "walker", "patient lift" and the rest are the home_medical collection's (with the
            FDA's device records), so they are not repeated here;
  makers    by the owner's rule every maker's own manuals and guides are LINK-ONLY (their terms keep all rights):
            nothing is read from their sites; each page is listed for the person to open or fetch with Program
            Downloader;
  documents the US government's guides IN FULL ("full": works of the US government, read where robots.txt allows):
            the FDA's hearing aid, over-the-counter hearing aid and cochlear implant pages, NIDCD's assistive devices
            and AAC pages, and the VA's prosthetics pages; the FCC's relay and hearing aid compatibility pages and
            NHTSA's adapted vehicle pages are links only (both sites refuse programs).

The notice is said first: an audiologist fits and programmes hearing aids and implants; a speech-language
pathologist sets up AAC; a wheelchair is fitted by a seating specialist; check weight limits, and have vehicle
adaptations installed and inspected by a qualified mobility dealer.
"""

INDEX_LICENCE = "CC0 (facts and links); each manual belongs to its maker; the government guides are public domain"
US_GOV = "a US government work (public domain)"

HEARING_NOTICE = ("Hearing aids, cochlear implants and AAC devices are fitted and programmed by professionals: an "
                  "audiologist or hearing aid specialist for hearing devices, a speech-language pathologist for AAC. "
                  "Keep batteries, especially button batteries, away from children and pets: swallowing one is an "
                  "emergency (call 911 or Poison Control, 1-800-222-1222). Follow each device's own instructions.")
MOBILITY_NOTICE = ("A wheelchair, power chair or scooter is fitted by a seating and mobility specialist; check the "
                   "weight limit of every chair, lift and ramp, and charge batteries as the maker says. Vehicle "
                   "lifts, ramps and hand controls are installed and inspected by a qualified mobility equipment "
                   "dealer, and driving with hand controls needs training (a driver rehabilitation specialist).")

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")


def _makers(category, prefix, makers):
    """The link-only makers of one collection, with the shared fields."""
    return [dict(dict(category=category, prefix=prefix, documents="manuals and user guides", access="link",
                      reason=RULE, types=[]), **m) for m in makers]


# ------------------------------------------------------------------------------ hearing and communication devices

HEARING_IA = ["cochlear implant", "sound processor", "bone anchored", "assistive listening", "fm system",
              "pocket talker", "loop system", "captioned telephone", "captel", "bed shaker", "vibrating alarm",
              "alerting system", "speech generating", "augmentative communication", "communication device"]

HEARING_MAKERS = _makers("hearing_communication_devices", "hcd", [
    dict(key="phonak", maker="Phonak (Sonova)", type="hearing aid", library="https://www.phonak.com/"),
    dict(key="oticon", maker="Oticon (Demant)", type="hearing aid", library="https://www.oticon.com/"),
    dict(key="signia", maker="Signia (WS Audiology)", type="hearing aid", library="https://www.signia.net/"),
    dict(key="resound", maker="ReSound (GN Hearing)", type="hearing aid", library="https://www.resound.com/"),
    dict(key="starkey", maker="Starkey", type="hearing aid", library="https://www.starkey.com/"),
    dict(key="widex", maker="Widex (WS Audiology)", type="hearing aid", library="https://www.widex.com/"),
    dict(key="unitron", maker="Unitron (Sonova)", type="hearing aid", library="https://www.unitron.com/"),
    dict(key="jabra-enhance", maker="Jabra Enhance (GN, over-the-counter hearing aids)", type="OTC hearing aid",
         library="https://www.jabra.com/"),
    dict(key="cochlear", maker="Cochlear Ltd (Nucleus implants, Baha and Osia bone conduction)",
         type="cochlear implant and bone conduction implant", library="https://www.cochlear.com/"),
    dict(key="advanced-bionics", maker="Advanced Bionics (Sonova)", type="cochlear implant",
         library="https://www.advancedbionics.com/"),
    dict(key="med-el", maker="MED-EL", type="cochlear and middle ear implant", library="https://www.medel.com/"),
    dict(key="tobii-dynavox", maker="Tobii Dynavox", type="speech-generating device and eye gaze AAC",
         library="https://us.tobiidynavox.com/"),
    dict(key="prc-saltillo", maker="PRC-Saltillo", type="speech-generating device", library="https://www.prc-saltillo.com/"),
    dict(key="ablenet", maker="AbleNet", type="switches and simple communication devices",
         library="https://www.ablenetinc.com/"),
    dict(key="lingraphica", maker="Lingraphica", type="speech-generating device", library="https://www.aphasia.com/"),
    dict(key="captel", maker="CapTel (Ultratec)", type="captioned telephone", library="https://www.captel.com/"),
    dict(key="clarity", maker="Clarity (amplified phones)", type="amplified telephone", library="https://www.clarityproducts.com/"),
    dict(key="sonic-alert", maker="Sonic Alert", type="alerting device and vibrating alarm clock",
         library="https://www.sonicalert.com/"),
    dict(key="williams-av", maker="Williams AV", type="assistive listening system", library="https://williamsav.com/"),
    dict(key="listen-technologies", maker="Listen Technologies", type="assistive listening system",
         library="https://www.listentech.com/"),
])

FDA_HEARING = "https://www.fda.gov/medical-devices/hearing-aids/"
HEARING_DOCUMENTS = [
    dict(key="fda-hearing-aids", by="US Food and Drug Administration", product="hearing aids",
         title="Hearing aids: types, over-the-counter hearing aids, how to get them (FDA; in the reference library: "
               "dis:fda_hearing_aids)",
         url="https://www.fda.gov/medical-devices/consumer-products/hearing-aids", type="hearing aid",
         document="guide", access="full", rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="fda-otc-hearing-aids", by="US Food and Drug Administration", product="over-the-counter hearing aids",
         title="OTC hearing aids: what you should know (FDA)", url=FDA_HEARING + "otc-hearing-aids-what-you-should-know",
         type="OTC hearing aid", document="guide", access="full", rights=US_GOV,
         reason="a US government work; robots.txt allows the page"),
    dict(key="fda-other-hearing-devices", by="US Food and Drug Administration", product="sound amplifiers (PSAPs)",
         title="Other hearing devices and products: personal sound amplification products (FDA)",
         url=FDA_HEARING + "other-hearing-devices-and-products", type="hearing device", document="guide",
         access="full", rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="fda-cochlear-implants", by="US Food and Drug Administration", product="cochlear implants",
         title="Cochlear implants (FDA)", url="https://www.fda.gov/medical-devices/implants-and-prosthetics/cochlear-implants",
         type="cochlear implant", document="guide", access="full", rights=US_GOV,
         reason="a US government work; robots.txt allows the page"),
    dict(key="nidcd-assistive-devices", by="National Institute on Deafness and Other Communication Disorders (NIH)",
         product="assistive listening, alerting and AAC devices",
         title="Assistive devices for people with hearing, voice, speech or language disorders (NIDCD; in the "
               "reference library: dir:nidcd_health)",
         url="https://www.nidcd.nih.gov/health/assistive-devices-people-hearing-voice-speech-or-language-disorders",
         type="assistive listening and AAC device", document="guide", access="full", rights=US_GOV,
         reason="a US government work; robots.txt allows the page"),
    dict(key="nidcd-cochlear-implants", by="National Institute on Deafness and Other Communication Disorders (NIH)",
         product="cochlear implants", title="Cochlear implants (NIDCD)",
         url="https://www.nidcd.nih.gov/health/cochlear-implants", type="cochlear implant", document="guide",
         access="full", rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="fcc-hearing-aid-compatibility", by="Federal Communications Commission",
         product="hearing aid compatible phones", title="Hearing aid compatibility for wireless telephones (FCC)",
         url="https://www.fcc.gov/consumers/guides/hearing-aid-compatibility-wireless-telephones",
         type="telephone", document="guide", access="link", rights=US_GOV,
         reason="link only: fcc.gov refuses programs (HTTP 403), so the page is not read"),
    dict(key="fcc-relay-services", by="Federal Communications Commission", product="relay services and captioned "
                                                                                  "telephones",
         title="Telecommunications relay services, video relay and IP captioned telephone service (FCC)",
         url="https://www.fcc.gov/consumers/guides/telecommunications-relay-service-trs", type="telephone",
         document="guide", access="link", rights=US_GOV,
         reason="link only: fcc.gov refuses programs (HTTP 403), so the page is not read"),
]

# ------------------------------------------------------------------------------ wheelchairs, mobility and vehicles

MOBILITY_IA = ["wheelchair accessible van", "vehicle lift", "scooter lift", "hand controls", "transfer seat",
               "wheelchair securement", "tie-down", "ceiling lift"]

MOBILITY_MAKERS = _makers("wheelchairs_mobility_vehicles", "wmv", [
    dict(key="invacare", maker="Invacare", type="wheelchair, power chair, bed and patient lift",
         library="https://www.invacare.com/"),
    dict(key="permobil", maker="Permobil (with TiLite and ROHO cushions)", type="power chair, manual wheelchair and "
                                                                               "cushion",
         library="https://www.permobil.com/"),
    dict(key="sunrise-medical", maker="Sunrise Medical (Quickie, Zippie, JAY cushions)",
         type="manual and power wheelchair and seating", library="https://www.sunrisemedical.com/"),
    dict(key="pride-mobility", maker="Pride Mobility (Jazzy, Go-Go, Quantum)", type="power chair, scooter and lift "
                                                                                    "chair",
         library="https://www.pridemobility.com/"),
    dict(key="drive-medical", maker="Drive DeVilbiss Healthcare", type="wheelchair, rollator, scooter and bath "
                                                                       "safety",
         library="https://www.drivemedical.com/"),
    dict(key="golden-technologies", maker="Golden Technologies", type="scooter, power chair and lift chair",
         library="https://www.goldentech.com/"),
    dict(key="ki-mobility", maker="Ki Mobility", type="manual wheelchair", library="https://www.kimobility.com/"),
    dict(key="whill", maker="WHILL", type="power chair", library="https://whill.inc/"),
    dict(key="hoyer", maker="Hoyer (Joerns Healthcare)", type="patient lift", library="https://www.joerns.com/"),
    dict(key="braunability", maker="BraunAbility", type="wheelchair-accessible van and vehicle lift",
         library="https://www.braunability.com/"),
    dict(key="vantage-mobility", maker="Vantage Mobility International (VMI)", type="wheelchair-accessible van",
         library="https://www.vantagemobility.com/"),
    dict(key="harmar", maker="Harmar", type="vehicle lift, stairlift and ramp", library="https://www.harmar.com/"),
    dict(key="bruno-vehicle", maker="Bruno (vehicle lifts and turning seats)", type="vehicle lift and transfer seat",
         library="https://www.bruno.com/"),
    dict(key="q-straint", maker="Q'Straint", type="wheelchair securement", library="https://www.qstraint.com/"),
])

MOBILITY_DOCUMENTS = [
    dict(key="va-prosthetics", by="US Department of Veterans Affairs", product="wheelchairs, scooters and other "
                                                                             "prosthetic and sensory aids",
         title="VA Prosthetic and Sensory Aids Service: how veterans get wheelchairs and mobility aids",
         url="https://www.prosthetics.va.gov/psas/", type="mobility aid services", document="guide", access="full",
         rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="access-board-vehicles", by="US Access Board", product="accessible buses, vans and rail cars",
         title="ADA Accessibility Guidelines for Transportation Vehicles (Access Board; in the reference library: "
               "travel:access_board_vehicles)",
         url="https://www.access-board.gov/ada/vehicles/", type="accessible vehicle", document="guide",
         access="full", rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="nhtsa-adapted-vehicles", by="National Highway Traffic Safety Administration",
         product="adapted vehicles", title="Adapted vehicles for drivers and passengers with disabilities (NHTSA)",
         url="https://www.nhtsa.gov/road-safety/adapted-vehicles", type="adapted vehicle", document="guide",
         access="link", rights=US_GOV,
         reason="link only: nhtsa.gov refuses programs (HTTP 403), so the page is not read"),
]

CATEGORIES = {
    "hearing_communication_devices": dict(
        name="Hearing aids, cochlear implants, assistive listening, captioned phones and AAC devices (manuals)",
        description="Hearing aids (prescription and over the counter), cochlear and bone conduction implants and "
                    "their sound processors, assistive listening systems (FM, loop, pocket amplifiers), captioned "
                    "and amplified telephones, alerting devices (flashing doorbells, bed shakers, vibrating alarm "
                    "clocks) and AAC devices (speech-generating devices, switches and eye gaze): the Internet "
                    "Archive's manuals, the makers' support pages (links), and the FDA's and NIDCD's guides.",
        kind="manuals", licence=INDEX_LICENCE, ia=HEARING_IA, makers=HEARING_MAKERS, documents=HEARING_DOCUMENTS,
        notice=HEARING_NOTICE),
    "wheelchairs_mobility_vehicles": dict(
        name="Wheelchairs, power chairs, scooters, patient lifts and accessible vehicles (makers and guides)",
        description="The makers of manual and power wheelchairs, scooters, seating and cushions, patient lifts, "
                    "wheelchair-accessible vans, vehicle lifts, turning seats and securement systems (links), the "
                    "Internet Archive's manuals of vehicle adaptations, and the VA's and Access Board's guides. "
                    "Wheelchair, walker and scooter manuals with the FDA's device records are in the home medical "
                    "equipment collection.",
        kind="manuals", licence=INDEX_LICENCE, ia=MOBILITY_IA, makers=MOBILITY_MAKERS, documents=MOBILITY_DOCUMENTS,
        notice=MOBILITY_NOTICE),
}
