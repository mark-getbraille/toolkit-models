"""The collection "RVs, trailers and towing, and motorcycle gear (manuals)" (category key motorcycles_rvs): the
owner's request of 2026-11-22 for motorcycles, RVs and trailers. practical_manuals.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (travel trailers, campers,
            motorhomes, fifth wheels, trailer hitches and brake controllers, RV refrigerators, furnaces and water
            heaters, motorcycle helmets and intercoms; RV generators are the power collection's). The plain words
            motorcycle, scooter, moped, ATV and snowmobile are already searched by the powersports collection, which has the motorcycle owner's
            manuals, so they are not repeated here;
  makers    the motorcycle, RV, trailer, hitch and RV appliance makers (Harley-Davidson, Honda, Airstream, Winnebago,
            Thor, Forest River, Jayco, Dometic, Norcold, Suburban, Lippert, Curt, B&W, Equal-i-zer): by the owner's
            rule LINK-ONLY, for the person (or the personal assistant) to open in a browser or fetch with Program
            Downloader; nothing is read from their sites;
  guidance  the guides the reference library builds in full (the Army's trailer and driver manuals, the Park
            Service's campground pages) and the federal pages that refuse programs (NHTSA), as links.

The safety notice is said first (NOTICE): towing, RV propane and carbon monoxide, and motorcycle helmets.
"""

NOTICE = ("Match the hitch, ball and coupler ratings to the loaded trailer's weight, keep the tongue weight at about "
          "10 to 15 percent, cross the safety chains and check the lights and breakaway brake before every trip. In "
          "an RV, keep smoke, carbon monoxide and propane alarms working and turn the propane off while driving. On "
          "a motorcycle, wear a DOT-approved helmet and protective gear.")

IA_WORDS = ["travel trailer", "camper", "pop-up camper", "motorhome", "motor home", "fifth wheel", "trailer hitch",
            "brake controller", "rv refrigerator", "rv furnace", "rv water heater", "airstream",
            "winnebago", "motorcycle helmet", "motorcycle intercom"]

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is "
        "listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="motorcycles_rvs", prefix="mr", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="harley-davidson", maker="Harley-Davidson", type="motorcycle owner's manual",
         library="https://www.harley-davidson.com/us/en/owners/", site="harley-davidson.com"),
    dict(key="honda-powersports", maker="Honda Powersports", type="motorcycle and scooter owner's manual",
         library="https://powersports.honda.com/", site="powersports.honda.com"),
    dict(key="airstream", maker="Airstream", type="travel trailer and touring coach owner's manual",
         library="https://www.airstream.com/owners/", site="airstream.com"),
    dict(key="winnebago", maker="Winnebago", type="motorhome and travel trailer owner's manual",
         library="https://www.winnebago.com/owners", site="winnebago.com"),
    dict(key="thor", maker="Thor Industries", type="RV owner's manual", library="https://www.thorindustries.com/",
         site="thorindustries.com"),
    dict(key="forest-river", maker="Forest River", type="RV and trailer owner's manual",
         library="https://forestriverinc.com/", site="forestriverinc.com"),
    dict(key="jayco", maker="Jayco", type="travel trailer and motorhome owner's manual",
         library="https://www.jayco.com/owners/", site="jayco.com"),
    dict(key="dometic", maker="Dometic", type="RV refrigerator, air conditioner, awning and toilet",
         library="https://www.dometic.com/", site="dometic.com"),
    dict(key="norcold", maker="Norcold (Thetford)", type="RV refrigerator", library="https://www.thetford.com/",
         site="thetford.com"),
    dict(key="suburban", maker="Suburban (Airxcel)", type="RV furnace and water heater",
         library="https://www.airxcel.com/", site="airxcel.com"),
    dict(key="lippert", maker="Lippert", type="RV leveling, slide-outs, axles and hitches",
         library="https://www.lippert.com/", site="lippert.com"),
    dict(key="curt", maker="CURT", type="trailer hitch, wiring and brake controller",
         library="https://www.curtmfg.com/",
         site="curtmfg.com"),
    dict(key="b-and-w", maker="B&W Trailer Hitches", type="gooseneck, fifth wheel and receiver hitch",
         library="https://www.bwtrailerhitches.com/", site="bwtrailerhitches.com"),
    dict(key="equalizer", maker="Equal-i-zer (Progress Mfg.)", type="weight distribution and sway control hitch",
         library="https://www.equalizerhitch.com/", site="equalizerhitch.com"),
]]

GUIDANCE = [
    dict(title="Operator's and Maintenance Manual, M1101 and M1102 trailers (Army TM 9-2330-392-13&P; built in full "
               "in the reference library: rvs:army_tm_m1101_trailer)",
         url="https://archive.org/details/trl-m-1101-m-1102-tm-9-2330-392-13-p-ltt", by="the US Army"),
    dict(title="Manual for the Wheeled Vehicle Operator: coupling and towing (Army TC 21-305-20; in the reference "
               "library: drive:army_tc_21_305_20)",
         url="https://archive.org/details/tc-21-305-20-manual-for-the-wheeled-vehicle-operator-2016", by="the US Army"),
    dict(title="Campgrounds and accessibility (National Park Service; in the reference library: "
               "rvs:nps_campgrounds_accessibility)", url="https://www.nps.gov/subjects/camping/campground.htm",
         by="the National Park Service"),
    dict(title="Motorcycle safety (NHTSA; open it in a browser: it refuses programs)",
         url="https://www.nhtsa.gov/road-safety/motorcycle-safety", by="the National Highway Traffic Safety "
                                                                      "Administration"),
    dict(title="Every state's motorcycle operator manual (links in the manual collection driving_handbooks)",
         url="https://www.usa.gov/state-motor-vehicle-services", by="USA.gov"),
]

CATEGORY = dict(
    name="RVs, trailers and towing, and motorcycle gear (manuals)",
    description="Travel trailers, campers, motorhomes and fifth wheels, trailer hitches and brake controllers, RV "
                "refrigerators, furnaces, water heaters, and motorcycle helmets and intercoms: the "
                "Internet Archive's manuals, the makers' manual pages (links) and the government's trailer, towing, "
                "campground and motorcycle safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
