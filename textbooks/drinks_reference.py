"""Drinks: the hand-written guide "How to describe a drink" and the TTB's wine manual, for the textbooks release.

Why: the owner's request of 2026-11-21 added wine, beer, spirits and every other drink to the offline library: how to
taste and describe them, how they are labelled, and how they are made, at home too. Most of the material is built by
the usual readers from sources.py (group "drinks": the TTB's standards of identity and home-production rules in the
Code of Federal Regulations, 26 U.S.C. chapter 51, the FDA's juice and labelling rules and guides, the TTB's
guidance pages and its spirits and beer manuals, Wikibooks' Brewing, Wine and Bartending, and old public-domain books
on brewing, winemaking, distilling, bars and soft drinks). This module adds two books the usual readers cannot make:

  drinks:guide          "How to describe a drink": a short guide written for this library, in plain words, for the
                        toolkit's Assistant and for a blind person tasting or being told about a drink. Every fact in
                        it comes from the public-domain US sources above (the legal definitions in 27 CFR parts 4, 5
                        and 7, the health warning of 27 CFR part 16, the home-production limits of 27 CFR 24.75 and
                        25.205, 26 U.S.C. 5601, the juice percentage rule of 21 CFR 101.30, and the FDA's caffeine
                        and Nutrition Facts guides); its own words are CC0. The legal and safety notes come first.
  drinks:ttb_wine_bam   The TTB's Beverage Alcohol Manual for wine, whole: the TTB publishes it one PDF per chapter,
                        so each chapter is read by build_textbooks.pdfdoc_book and the chapters are joined into one
                        book (the spirits and beer manuals are single PDFs, in sources.PDF_DOCS).

Run from the repository's folder:
    python3 textbooks/build_textbooks.py drinks:guide --out build/textbooks
"""

import build_textbooks as B
import sources

DISTILLING_WARNING = sources.DISTILLING_NOTE.strip()
ALCOHOL_NOTE = "Contains alcohol. Not for people under the legal drinking age, during pregnancy, or before driving."
CAFFEINE_NOTE = ("High in caffeine; not recommended for children, during pregnancy, or for people sensitive to "
                 "caffeine.")
GUIDE_SOURCES = ("27 CFR parts 4, 5, 7, 16, 24 and 25 (Alcohol and Tobacco Tax and Trade Bureau); 26 U.S.C. sections "
                 "5042, 5053 and 5601; 21 CFR 101.30 and part 146 (Food and Drug Administration); the FDA's guides "
                 "\"How to Understand and Use the Nutrition Facts Label\" and \"Spilling the Beans: How Much Caffeine "
                 "is Too Much?\"; the TTB's labelling guidance. All are works of the US government, in the public "
                 "domain.")
LICENCE_LINE = ("How to describe a drink: written for the toolkit's library in November 2026 from public-domain US "
                "government sources only (" + GUIDE_SOURCES + "). Its own words are CC0 (no rights reserved).")
NOT_INCLUDED = []                # what was looked at and left out is in sources.DRINKS_NOT_INCLUDED

# The TTB wine manual's chapters (https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/
# beverage-alcohol-manual/), checked on 2026-11-21.
WINE_BAM_PAGE = "https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/beverage-alcohol-manual/"
WINE_BAM_FILES = "https://www.ttb.gov/system/files/images/pdfs/wine_bam/"
WINE_BAM_CHAPTERS = [
    ("c1-mandatory-label-information.pdf", "Chapter 1: Mandatory label information"),
    ("c2-type-size-and-legibility-requirements.pdf", "Chapter 2: Type size and legibility requirements"),
    ("c3-format-type-size-legibility-heath-warning-statement.pdf", "Chapter 3: The health warning statement"),
    ("c4-geographic-brand-names.pdf", "Chapter 4: Geographic brand names"),
    ("c5-class-and-type-designation.pdf", "Chapter 5: Class and type designation"),
    ("c6-name-and-address.pdf", "Chapter 6: Name and address"),
    ("c7-standards-of-fill-and-net-contents.pdf", "Chapter 7: Standards of fill and net contents"),
    ("c8-cellar-treatment-for-natural-wine.pdf", "Chapter 8: Cellar treatment of natural wine"),
    ("c9-appellation-of-origin-and-vintage-date.pdf", "Chapter 9: Appellation of origin and vintage date"),
    ("c10-sample-wine-labels.pdf", "Chapter 10: Sample wine labels"),
]

# The guide's pages: (path, title, [paragraphs or ("list", [items]) or ("h2", heading)]).
GUIDE = [
    ("safety-and-the-law-first", "Safety and the law first", [
        "Alcoholic drinks: " + ALCOHOL_NOTE + " Every US alcoholic drink label carries the government warning of "
        "27 CFR part 16: \"GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic "
        "beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages "
        "impairs your ability to drive a car or operate machinery, and may cause health problems.\"",
        "Energy drinks and other high-caffeine drinks: " + CAFFEINE_NOTE + " Say the amount of caffeine only when "
        "the label or record states it. The FDA's guide says 400 milligrams a day is an amount not generally "
        "associated with negative effects for healthy adults, and that it has not set a level for children.",
        ("h2", "Making drinks at home (United States)"),
        "Beer: federal law lets an adult brew beer at home for personal or family use, not for sale: up to 100 "
        "gallons a calendar year, or 200 gallons for a household of two or more adults (26 U.S.C. 5053 and 27 CFR "
        "25.205 and 25.206).",
        "Wine: the same limits apply to wine made at home for personal or family use (26 U.S.C. 5042 and 27 CFR "
        "24.75).",
        "Spirits: " + DISTILLING_WARNING,
        "State and local laws can be stricter than federal law, and the laws of other countries differ.",
    ]),
    ("how-to-describe-a-drink", "How to describe a drink", [
        "A good description goes from what can be read or seen to what can be smelled and tasted. When describing "
        "a picture, say only what the picture, the label or the record shows; never guess an alcohol content, a "
        "vintage or a caffeine amount that is not printed.",
        ("list", [
            "What it is: the kind of drink (wine, beer, spirit, cider, juice, soft drink, water, coffee, tea), and, "
            "as the label states them, the brand, the class or type (\"Bourbon Whisky\", \"India Pale Ale\", "
            "\"Cabernet Sauvignon\"), the style, the region or appellation, the vintage and the alcohol content "
            "(\"13.5% alc/vol\", or the proof for spirits: proof is twice the percentage of alcohol by volume).",
            "The container: bottle (its colour, shape and closure: cork, screw cap, crown cap, swing top), can, box "
            "(bag-in-box wine), carton, pouch, keg, cask or tap; its size as printed (750 mL, 12 fl oz).",
            "Appearance in the glass: the colour and how deep it is, clear or hazy, still or sparkling (fine or large "
            "bubbles), and for beer the head (its colour, thickness and how long it lasts).",
            "Aroma (the smell): fruity, floral, herbal or grassy, spicy, earthy, woody or oaky, toasty, nutty, "
            "caramel or chocolate, smoky, yeasty or bready, and for beer malty or hoppy.",
            "Palate (the taste in the mouth): sweet to dry, acidity (fresh, crisp, tart), bitterness, tannin (the "
            "drying grip of red wine and strong tea), body (light, medium, full), the warmth of the alcohol, and the "
            "fizz.",
            "Finish: how long the taste lasts after swallowing (short, medium, long) and what it leaves (bitter, "
            "sweet, smoky, fruity).",
            "How it is served: the glass, the temperature (chilled, room temperature, hot), ice, garnish.",
        ]),
        "A short example in this order: \"A bottle of red wine. The label says Cabernet Sauvignon, Napa Valley, 2019, "
        "14.5% alcohol by volume. In the glass it is deep ruby and clear.\" Then, if the drink is being tasted: "
        "\"It smells of blackcurrant and oak; it is dry and full-bodied with firm tannin and a long finish.\" For an "
        "alcoholic drink, end with: " + ALCOHOL_NOTE,
    ]),
    ("wine", "Wine", [
        "The colour words: white wine runs from pale straw and green-gold to deep gold and amber; rosé from pale pink "
        "and salmon to deep pink; red wine from purple and ruby to garnet and brick (older reds turn brown at the "
        "rim). Sparkling wine has bubbles: the finer and longer-lasting, the more it is praised.",
        "What US law calls wine (27 CFR part 4, standards of identity): grape wine (from grapes), with types such as "
        "table wine (not over 14 percent alcohol), dessert wine (over 14 and not over 24 percent), sparkling wine "
        "made effervescent by a second fermentation in a closed container, champagne-style wines, carbonated wine, "
        "citrus wine, fruit wine (from fruit other than grapes), wine from other agricultural products (such as "
        "mead from honey) and aperitif wine. The part itself, whole, is in this library.",
        "A varietal label names the grape (Chardonnay, Pinot Noir); US rules say most of the wine must come from "
        "that grape (at least 75 percent for most varieties). An appellation of origin names where the grapes grew "
        "(a country, state, county or an American viticultural area such as Napa Valley); a vintage date is the "
        "year the grapes were harvested.",
    ]),
    ("beer", "Beer", [
        "The colour words: pale straw, gold, amber, copper, brown, and black; clear, slightly hazy or cloudy (wheat "
        "beers and many modern IPAs are hazy). The head is the foam on top: white, off-white or tan; thin or thick; "
        "quick to fade or lasting, leaving lace on the glass.",
        "The two big families are ales (top-fermenting yeast, often fruity) and lagers (bottom-fermenting yeast, "
        "cooler and cleaner). US labelling rules (27 CFR part 7) list class and type names such as beer, ale, "
        "porter, stout, lager and malt liquor; a style name such as India Pale Ale is said as the label prints it.",
        "Beer is made from malted grain (usually barley), hops (for bitterness and aroma), yeast and water: the grain "
        "is mashed in hot water to make a sweet liquid (wort), which is boiled with hops, cooled, fermented by the "
        "yeast, then conditioned and packaged. The Wikibooks book Brewing and the old brewing manuals in this "
        "library give whole recipes, with their grain bills and hop schedules in the units their authors used.",
    ]),
    ("spirits", "Spirits", [
        "Spirits are distilled: a fermented liquid is heated in a still and the alcohol vapour is collected. The "
        "standards of identity in 27 CFR part 5 (section 5.143 and its tables, whole in this library) say what "
        "each name means in the US, for example:",
        ("list", [
            "Vodka: neutral spirits (distilled to a very high proof), sometimes filtered or treated; flavoured "
            "vodka is a type of its own.",
            "Whisky: distilled from a fermented mash of grain. Bourbon whisky is made from a mash of at least 51 "
            "percent corn and stored in charred new oak containers; rye whisky at least 51 percent rye; malt whisky "
            "at least 51 percent malted barley; wheat whisky at least 51 percent wheat; corn whisky at least 80 "
            "percent corn. \"Straight\" whisky has been stored at least two years.",
            "Gin: gets its main flavour from juniper berries.",
            "Brandy: distilled from fermented fruit juice or mash (grape brandy unless another fruit is named).",
            "Rum: distilled from fermented sugar cane products (juice, syrup, molasses).",
            "Agave spirits, including tequila (from the blue agave, made in Mexico) and mezcal.",
            "Liqueurs and cordials: spirits flavoured and sweetened (at least 2.5 percent sugar by weight).",
        ]),
        "Colour words for spirits: water-clear, pale straw, gold, amber, copper, mahogany. Wood-aged spirits take "
        "colour and vanilla, caramel and spice aromas from the barrel.",
        DISTILLING_WARNING,
    ]),
    ("soft-drinks-juices-and-waters", "Soft drinks, juices, coffee, tea and waters", [
        "Juice or juice drink: under 21 CFR 101.30 a drink that says it contains juice must state how much on the "
        "label, as \"Contains __ percent juice\" (or the words \"100 percent juice\"), near the top of the "
        "information panel; a drink with less juice is often called a juice drink, beverage or cocktail. Nectars "
        "are diluted, sweetened fruit purees (21 CFR part 146 defines canned fruit nectars and the kinds of orange "
        "juice). Read the percentage as printed; never estimate it.",
        "Soft drinks: carbonated (sodas, colas, ginger ale, root beer, tonic and sparkling waters) or still "
        "(lemonade, iced tea, sports drinks); say regular, diet or zero sugar only as the label says. Energy drinks: "
        + CAFFEINE_NOTE + " Kombucha is fermented tea; plant milks are made from oats, almonds, soy, rice or "
        "coconut; drink mixes and syrups are diluted before drinking.",
        "The Nutrition Facts label (FDA): first the serving size and servings per container, then calories, then "
        "the nutrients with their percent Daily Value (5 percent or less is low, 20 percent or more is high), "
        "including total sugars and added sugars. Caffeine is listed only when the maker chooses to state it.",
        "Mocktails are mixed drinks without alcohol; describe them like cocktails (glass, colour, garnish).",
    ]),
    ("reading-an-alcohol-label", "Reading an alcohol label", [
        "The TTB's rules (27 CFR parts 4, 5 and 7, and its Beverage Alcohol Manuals in this library) name what a US "
        "label must say. The items to read out, in this order, are:",
        ("list", ["The brand name.", "The class or type (\"Red Wine\", \"Kentucky Straight Bourbon Whisky\", "
                  "\"Lager\").", "The alcohol content, as printed (wine and spirits must show it; for most beer it "
                  "is optional under federal rules).", "The net contents (750 mL, 12 FL OZ).",
                  "The name and address of the bottler or importer, and the country of origin for imports.",
                  "Declarations such as \"Contains sulfites\", and colour additives such as FD&C Yellow No. 5.",
                  "The government health warning."]),
        "A vintage date, a grape variety, an appellation or an age statement is read only when it is printed.",
    ]),
    ("where-to-read-more", "Where to read more in this library", [
        ("list", [
            "The laws, whole: 27 CFR parts 4 (wine), 5 (spirits), 7 (malt beverages), 16 (health warning), 19 "
            "(distilled spirits plants), 24 (wine, including home winemaking) and 25 (beer, including home "
            "brewing); 21 CFR parts 101 (food labeling), 120 (juice safety) and 146 (fruit juices); 26 U.S.C. "
            "chapter 51.",
            "The TTB's Beverage Alcohol Manuals (wine, spirits, beer) and its guidance pages.",
            "The FDA's guides to the Nutrition Facts label, caffeine and juice safety.",
            "Wikibooks: Brewing, Wine and Bartending (share-alike).",
            "Old public-domain books (before 1931): brewing (Wahl and Henius, Pitt, Cobbett, Booth), wine and cider "
            "(Haraszthy, Roos, Wright, Brannt, Alwood, Crampton), distilling (with the legal and safety notes "
            "first), bartending (Jerry Thomas, Haywood) and soft drinks and juices (Sulz, Saxe, Wiley, Dearing, "
            "Cruess, Moore). Their methods, safety advice and laws are out of date; their units are as written.",
        ]),
    ]),
]


def guide_body(blocks):
    """The HTML of one guide page from its blocks: paragraphs, ("h2", heading) and ("list", [items])."""
    out = []
    for block in blocks:
        if isinstance(block, tuple) and block[0] == "h2":
            out.append(f"<h2>{B.esc(block[1])}</h2>")
        elif isinstance(block, tuple) and block[0] == "list":
            out.append("<ul>" + "".join(f"<li>{B.esc(item)}</li>" for item in block[1]) + "</ul>")
        else:
            out.append(f"<p>{B.esc(block)}</p>")
    return "\n".join(out)


def guide_book():
    """The book "How to describe a drink" (nothing is downloaded: its words are in GUIDE)."""
    book = B.Book(name="how_to_describe_a_drink", title="How to describe a drink: wine, beer, spirits and soft drinks",
                  subject="Drinks (tasting and describing)", level="reference", group="drinks",
                  publisher="Digital Accessibility Toolkit (written from US government sources)",
                  country="United States", licence="CC0", licence_url="https://creativecommons.org/publicdomain/zero/"
                  "1.0/", source="https://www.ttb.gov/regulated-commodities/beverage-alcohol",
                  description="A plain guide to describing a drink: the legal and safety notes first, then what to "
                              "say and in what order (label, container, appearance, aroma, palate, finish), the "
                              "words for wine, beer, spirits, soft drinks, juices and waters, and how to read an "
                              "alcohol label and the Nutrition Facts label. Built only from public-domain US sources.",
                  changes="written for this library from public-domain US government sources", published="2026-11-21")
    about = (f"<p>{B.esc(LICENCE_LINE)}</p><p>Sources: {B.esc(GUIDE_SOURCES)}</p>")
    book.pages = [B.Page("about-this-book", "About this book", about)] + \
        [B.Page(path, title, guide_body(blocks), i) for i, (path, title, blocks) in enumerate(GUIDE, 1)]
    return book


def wine_bam_book(work, cache=None, left_out=None):
    """The TTB wine manual, whole: each chapter's PDF read by pdfdoc_book (its licence line checked on the TTB's
    policy page), the chapters joined in order. None when no chapter could be read (said in left_out)."""
    left_out = left_out if left_out is not None else []
    base = dict(sources.TTB_PDF, name="ttb_bam_wine", title="The Beverage Alcohol Manual: Wine (TTB)",
                subject="Wine (labels)", page=WINE_BAM_PAGE,
                description="The TTB's practical guide to wine labels, whole: mandatory information, type size, the "
                            "health warning, geographic brand names, class and type, name and address, standards of "
                            "fill, cellar treatment of natural wine, appellation of origin and vintage date, and "
                            "sample labels.")
    book = None
    for number, (file_name, chapter) in enumerate(WINE_BAM_CHAPTERS, 1):
        part = B.pdfdoc_book(dict(base, name=f"ttb_bam_wine_c{number}", pdf=WINE_BAM_FILES + file_name), work, cache,
                             left_out)
        if part is None:
            continue
        chapter_pages = list(part.pages)
        if book is None:
            book = part
            book.name, book.pages = "ttb_bam_wine", []
            book.original_pdf = {}
        for i, page in enumerate(chapter_pages, 1):
            book.pages.append(B.Page(f"c{number}-{i}-{B.slug(page.title, 40)}", page.title, page.body, number,
                                     chapter))
    return book


def drinks_book(piece, work, cache=None, left_out=None):
    """The book of one drinks key piece ("guide" or "ttb_wine_bam"), or None."""
    if piece == "guide":
        return guide_book()
    if piece == "ttb_wine_bam":
        return wine_bam_book(work, cache, left_out)
    if left_out is not None:
        left_out.append({"title": f"drinks:{piece}", "reason": "Unknown drinks book."})
    return None
