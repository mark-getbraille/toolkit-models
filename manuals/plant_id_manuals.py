"""The collection "Plant identification: field guides, hand lenses, plant presses and identification apps (manuals)"
(category key plant_id): the owner's request of 2026-11-22 for plant identification. categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (plant identification, field
            guides, hand lenses, plant presses, herbaria, wildflower, tree and mushroom guides, foraging). "Loupe" and
            "moisture meter" are already searched by other collections, so they are not repeated here;
  makers    the plant identification apps and the hand lens makers: LINK-ONLY by the owner's rule (the apps' help
            pages are links for the person to open; nothing is read from them, and the inaturalist.org site is never
            read by the toolkit, only its open data through GBIF);
  guidance  the reference library's plant books (textbooks/plant_id.py) and the poison help line.

The safety notice is said first (NOTICE): never eat a wild plant or mushroom unless an expert has identified it in
person; an app or a picture is never enough.
"""

NOTICE = ("Read this first: never eat, taste or use a wild plant or mushroom because an app, a book or a picture "
          "named it; only an expert who sees it in person can confirm it, and deadly lookalikes exist. Poison "
          "Control: 1-800-222-1222 (US); call 911 if someone is very ill.")

IA_WORDS = ["plant identification", "field guide", "hand lens", "plant press", "herbarium", "wildflower",
            "tree identification", "mushroom", "foraging", "botany"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="plant_id", prefix="pi", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="seek-inaturalist", maker="Seek by iNaturalist", type="plant and animal identification app",
         library="https://www.inaturalist.org/pages/seek_app", site="inaturalist.org"),
    dict(key="plantnet-app", maker="Pl@ntNet", type="plant identification app", library="https://plantnet.org/en/",
         site="plantnet.org"),
    dict(key="picturethis", maker="PictureThis", type="plant identification app", library="https://www.picturethisai.com/",
         site="picturethisai.com"),
    dict(key="belomo", maker="BelOMO", type="hand lenses and magnifiers", library="https://belomo.com/", site="belomo.com"),
]]

GUIDANCE = [
    dict(title="Plant identification books (in the reference library: request word plant-id)",
         url="https://www.fs.usda.gov/wildflowers", by="the US Forest Service and others"),
    dict(title="Poison Control (open it in a browser, or call 1-800-222-1222)", url="https://www.poison.org/",
         by="America's Poison Centers and the National Capital Poison Center"),
    dict(title="Toxic and non-toxic plants for pets (ASPCA; copyright, open it in a browser)",
         url="https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants", by="the ASPCA"),
]

CATEGORY = dict(
    name="Plant identification: field guides, hand lenses, plant presses and identification apps (manuals)",
    description="Field guides, hand lenses, plant presses and herbarium supplies, wildflower, tree and mushroom guides, "
                "and plant identification apps: the Internet Archive's manuals, the makers' and apps' help pages "
                "(links), and the reference library's plant books. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
