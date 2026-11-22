"""Real questions: a test set of questions that blind people really asked about their own photos, to measure whether a
topic add-on (or any trained describer) really helps them. It is a test only: nothing here is ever trained on, and
train.py leaves these pictures out of every training (leave_out).

Where the questions come from (all CC BY 4.0, credited in every report):
  - VizWiz VQA, its "test" part (Gurari et al., 2018; vizwiz.org): photos blind people took with their phones, each
    with the question they asked and the answers of ten sighted people. Its answers were published later
    (VizWiz_all_answers/VQA_test.json), and the kit never trains on this part (it learns from VizWiz's "train"
    questions and the "val" captions), so the pictures are new to every model the kit makes.
  - VizWiz's masked photos (VizWiz_train_00023431 to 00023958): photos with private information (bills, cards,
    mail, prescription labels, screens) that VizWiz released with the private parts already covered over (the
    ImageNet mean colour), with their questions and ten answers. Only these released, masked copies are used, never
    an unmasked original; the questions are sorted into topics like the others (documents, medicines and so on).
  - Home health tests (the group "home_tests", not a topic add-on): every VizWiz question about reading a home
    test's result lines (pregnancy tests; VizWiz has no COVID-19 or ovulation tests, which came later, and no other
    open set of blind people's questions has them yet), from its test, train and val parts. They are tested with the
    medicines topic and in every full test.
  - ORBIT (Massiceti et al., 2021; City, University of London and Microsoft): frames of videos that blind and
    low-vision people filmed of their own things, from ORBIT's "train" part (the kit's ORBIT pack uses its
    validation and test parts first). The question is "What is this?" and the answer is the thing's name as the
    person called it (several accepted wordings).
  The VizWiz photos from its train and val parts, and the ORBIT frames, are left out of every training by leave_out.
  Left out on purpose: a VizWiz question that VizWiz-Priv (CC BY 4.0) asked about a private photo, unless the photo is
  one of the masked ones, so an unmasked private photo is never used; and questions or answers about things that
  identify someone or are intimate: passwords and identity numbers, faces and looks, tattoos, number plates, nudity or
  sex, e-mail addresses, and answers holding a long number such as a phone or card number (private_reason). The
  nudity and sexual content topics stay empty: no open set of blind people's questions has them. Firearms is empty
  too (no question in VizWiz is about a gun).

How the questions were sorted: by simple word rules on the question and on the answers at least two people agreed on
(classify_topic, classify_kind), checked by hand on 40 questions of each group: about 9 in 10 were in the right group
(medicines 40 of 40, drugs 21 of 22, machines 38 of 40, documents 37 of 40, art 32 of 35, nature 33 of 40, where
pictures printed on shirts and scent names slip in). Each topic has up to 50 questions with a mix of kinds and at most
a quarter that cannot be answered; everyday questions fill up to 600.

The list (real_questions.jsonl beside this file, about 600 rows, made by tools/build_real_questions.py in the
repository) holds, for each question: "id", "source" (vizwiz or orbit), "image" (the file name at its source),
"question", "answers" (VizWiz: the ten people's answers; ORBIT: the accepted names), "answerable" (0 when most of
VizWiz's ten people said it cannot be answered from the photo), "topic" (a topics.py id, "home_tests" or
"everyday"), "kind" (the type of question: reading text, expiry date, amount, colour, which button, on or off, money, medicine, what is
this, yes or no, other) and "licence". ORBIT rows also say where the frame is in ORBIT's published zip ("zip",
"offset", "size", "method"), so one frame is read without downloading the 50 GB zip.

The pictures are downloaded on this computer the first time (fetch_pictures), into <library or work>\\real-questions:
VizWiz photos one by one from VizWiz's own server (vizwiz.cs.colorado.edu, which has no robots.txt limits), ORBIT
frames with byte-range reads of ORBIT's zip on figshare (City, University of London's repository, which allows it).
About 600 photos, 200 MB.

How an answer is scored (score_row):
  - accuracy: VizWiz's standard VQA accuracy. The model's answer and the ten people's answers are tidied the official
    way (normalise: lower case, punctuation, number words to digits, "a", "an" and "the" dropped, contractions
    mended); the answer scores min(1, how many of the other nine people gave it / 3), averaged over the ten ways of
    leaving one person out. So an answer three or more people gave scores 1. An answer that says the photo does not
    show enough ("I can't tell", "unanswerable") counts as "unanswerable". ORBIT rows: 1 when the answer names the
    thing (any accepted wording), else 0.
  - contains: a kinder check for answers in whole sentences: 1 when the answer contains, as whole words, an answer
    at least two of the ten people gave.
  - unanswerable: for a question most people could not answer, whether the model said so too ("said unanswerable
    when it should"), and for the others, whether it wrongly gave up.
The model is asked the person's question with ASK_SHORT after it (the usual VizWiz instruction: answer in a word or
phrase, and say Unanswerable when the photo does not show enough).

Run it with kit\\run.cmd --evaluate 4b (the model itself), --evaluate <an add-on folder or result zip>, and
--topic ID to test only that topic's questions and the everyday ones (train.py hands --evaluate to run_evaluation).
The wizard's Topic add-ons window has "Test on real questions" (Alt+Q). A topic add-on's training runs it by itself,
before and after, on that topic's real questions and the everyday ones, and its report says how it did
(compare_lines). The report of a test alone is report-real-questions-<name>.txt in the kit folder (report_lines).
"""

import json
import os
import random
import re
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SET_FILE = os.path.join(HERE, "real_questions.jsonl")
FOLDER_NAME = "real-questions"

VIZWIZ_PICTURES = "https://vizwiz.cs.colorado.edu/VizWiz_visualization_img/"
ORBIT_ZIPS = {"train": "https://ndownloader.figshare.com/files/27189155"}      # ORBIT's train part, 50 GB
USER_AGENT = "PictureModelTrainingKit/2"

VIZWIZ_CREDIT = ("VizWiz VQA (Danna Gurari, Qing Li, Abigale J. Stangl, Anhong Guo, Chi Lin, Kristen Grauman, Jiebo "
                 "Luo and Jeffrey P. Bigham, CVPR 2018), CC BY 4.0, https://vizwiz.org/tasks-and-datasets/vqa/ "
                 "(test part, with its published answers); private photos left out with VizWiz-Priv (Gurari et al., "
                 "CVPR 2019), CC BY 4.0.")
ORBIT_CREDIT = ("ORBIT dataset (Daniela Massiceti, Luisa Zintgraf, John Bronskill, Lida Theodorou, Matthew Tobias "
                "Harris, Edward Cutrell, Cecily Morrison, Katja Hofmann and Simone Stumpf, ICCV 2021), City, "
                "University of London and Microsoft, CC BY 4.0, https://doi.org/10.25383/city.14294597")
LICENCE = "CC BY 4.0"

# The instruction added after each question (the usual one for VizWiz), so answers are short and comparable.
ASK_SHORT = ("Answer the question using a single word or phrase. When the picture does not show enough to answer, "
             "answer Unanswerable.")
ANSWER_TOKENS = 40
EVERYDAY = "everyday"
# A group of its own, not a topic add-on: home health tests (pregnancy, COVID-19 and other rapid tests, ovulation
# tests), whose result lines blind people ask about. It is tested with the medicines and health topics (both hold the
# home health test packs) and with every test.
HOME_TESTS = "home_tests"
HOME_TEST_TOPICS = ("medicines", "health")
HOME_TEST_WORDS = re.compile(r"(?<![a-z0-9])(pregnan\w*|ovulat\w*|covid|coronavirus|rapid test|antigen|lateral flow|"
                             r"test strips?|home test|flu test|strep test|positive or negative|negative or positive)"
                             r"(?![a-z0-9])")
# Result lines alone ("one line or two?") count only with a test's other words, and never about a screen.
TEST_LINES = re.compile(r"(?<![a-z0-9])((one|two|1|2|pink|red|blue) lines?|result (window|lines?)|control line)"
                        r"(?![a-z0-9])")
TEST_HINTS = re.compile(r"test|pregnan|positive|negative|plus|minus|window|device")

# ----------------------------------------------------------------- VizWiz's official answer tidying
# From the VQA and VizWiz evaluation code (vqaEval.py, BSD licence): the same lists and steps.

CONTRACTIONS = {
    "aint": "ain't", "arent": "aren't", "cant": "can't", "couldve": "could've", "couldnt": "couldn't",
    "couldn'tve": "couldn't've", "couldnt've": "couldn't've", "didnt": "didn't", "doesnt": "doesn't",
    "dont": "don't", "hadnt": "hadn't", "hadnt've": "hadn't've", "hadn'tve": "hadn't've", "hasnt": "hasn't",
    "havent": "haven't", "hed": "he'd", "hed've": "he'd've", "he'dve": "he'd've", "hes": "he's", "howd": "how'd",
    "howll": "how'll", "hows": "how's", "Id've": "I'd've", "I'dve": "I'd've", "Im": "I'm", "Ive": "I've",
    "isnt": "isn't", "itd": "it'd", "itd've": "it'd've", "it'dve": "it'd've", "itll": "it'll", "let's": "let's",
    "maam": "ma'am", "mightnt": "mightn't", "mightnt've": "mightn't've", "mightn'tve": "mightn't've",
    "mightve": "might've", "mustnt": "mustn't", "mustve": "must've", "neednt": "needn't", "notve": "not've",
    "oclock": "o'clock", "oughtnt": "oughtn't", "ow's'at": "'ow's'at", "'ows'at": "'ow's'at", "'ow'sat": "'ow's'at",
    "shant": "shan't", "shed've": "she'd've", "she'dve": "she'd've", "she's": "she's", "shouldve": "should've",
    "shouldnt": "shouldn't", "shouldnt've": "shouldn't've", "shouldn'tve": "shouldn't've", "somebody'd": "somebodyd",
    "somebodyd've": "somebody'd've", "somebody'dve": "somebody'd've", "somebodyll": "somebody'll",
    "somebodys": "somebody's", "someoned": "someone'd", "someoned've": "someone'd've", "someone'dve": "someone'd've",
    "someonell": "someone'll", "someones": "someone's", "somethingd": "something'd",
    "somethingd've": "something'd've", "something'dve": "something'd've", "somethingll": "something'll",
    "thats": "that's", "thered": "there'd", "thered've": "there'd've", "there'dve": "there'd've",
    "therere": "there're", "theres": "there's", "theyd": "they'd", "theyd've": "they'd've", "they'dve": "they'd've",
    "theyll": "they'll", "theyre": "they're", "theyve": "they've", "twas": "'twas", "wasnt": "wasn't",
    "wed've": "we'd've", "we'dve": "we'd've", "weve": "we've", "werent": "weren't", "whatll": "what'll",
    "whatre": "what're", "whats": "what's", "whatve": "what've", "whens": "when's", "whered": "where'd",
    "wheres": "where's", "whereve": "where've", "whod": "who'd", "whod've": "who'd've", "who'dve": "who'd've",
    "wholl": "who'll", "whos": "who's", "whove": "who've", "whyll": "why'll", "whyre": "why're", "whys": "why's",
    "wont": "won't", "wouldve": "would've", "wouldnt": "wouldn't", "wouldnt've": "wouldn't've",
    "wouldn'tve": "wouldn't've", "yall": "y'all", "yall'll": "y'all'll", "y'allll": "y'all'll",
    "yall'd've": "y'all'd've", "y'alld've": "y'all'd've", "y'all'dve": "y'all'd've", "youd": "you'd",
    "youd've": "you'd've", "you'dve": "you'd've", "youll": "you'll", "youre": "you're", "youve": "you've"}
NUMBER_WORDS = {"none": "0", "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
                "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
ARTICLES = {"a", "an", "the"}
PERIOD_STRIP = re.compile(r"(?!<=\d)(\.)(?!\d)")
COMMA_STRIP = re.compile(r"(\d)(,)(\d)")
PUNCTUATION = [";", r"/", "[", "]", '"', "{", "}", "(", ")", "=", "+", "\\", "_", "-", ">", "<", "@", "`", ",", "?",
               "!"]


def _punctuation(text):
    """The official punctuation step: a mark next to a space (or in a text with a number like 1,000) is dropped,
    others become a space; full stops not inside a number are dropped."""
    out = text
    for mark in PUNCTUATION:
        if (mark + " " in text or " " + mark in text) or COMMA_STRIP.search(text) is not None:
            out = out.replace(mark, "")
        else:
            out = out.replace(mark, " ")
    return PERIOD_STRIP.sub("", out)


def _digits_and_articles(text):
    """The official word step: lower case, number words to digits, articles dropped, contractions mended."""
    words = [NUMBER_WORDS.get(w, w) for w in text.lower().split()]
    words = [w for w in words if w not in ARTICLES]
    return " ".join(CONTRACTIONS.get(w, w) for w in words)


def normalise(text):
    """An answer tidied the official VizWiz way ("Two Cans." -> "2 cans")."""
    text = str(text or "").replace("\n", " ").replace("\t", " ").strip()
    return _digits_and_articles(_punctuation(text))


# ----------------------------------------------------------------- scoring one answer

UNANSWERABLE_WORDS = ("unanswerable", "unsuitable", "unsuitable image")
GAVE_UP = re.compile(
    r"\b(unanswerable|unsuitable|(can ?not|can't|cant|unable to|not able to|impossible to|hard to|difficult to) "
    r"(tell|see|read|determine|answer|identify|make out|be determined|be read|be seen)|"
    r"(is|are) not (visible|readable|legible|clear|shown)|too (blurry|blurred|dark|bright|out of focus)|"
    r"i don't know|i do not know|not enough (information|detail))\b")


def said_unanswerable(text):
    """True when an answer says the photo does not show enough to answer ("Unanswerable", "I can't tell from this
    picture.", "The text is too blurry to read.")."""
    words = str(text or "").lower().replace("’", "'")
    return normalise(words) in UNANSWERABLE_WORDS or bool(GAVE_UP.search(words))


def vizwiz_accuracy(answer, people):
    """VizWiz's standard accuracy (0 to 1) of answer against the people's answers (normally ten): for each way of
    leaving one person out, min(1, how many of the others gave the same answer / 3), averaged."""
    people = [normalise(p) for p in people if str(p or "").strip()]
    if not people:
        return 0.0
    mine = normalise(answer)
    total = 0.0
    for i in range(len(people)):
        others = people[:i] + people[i + 1:]
        total += min(1.0, sum(1 for p in others if p == mine) / 3.0)
    return total / len(people)


def _has_words(text, phrase):
    """True when phrase appears in text as whole words (both already normalised)."""
    return bool(phrase) and re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None


def agreed_answers(people, least=2):
    """The answers (normalised) that at least least people gave, without "unanswerable"."""
    counts = {}
    for p in people:
        n = normalise(p)
        if n:
            counts[n] = counts.get(n, 0) + 1
    return [a for a, c in counts.items() if c >= least and a not in UNANSWERABLE_WORDS]


def score_row(row, answer):
    """The scores of the model's answer to one real question: {"accuracy", "contains", "should_give_up",
    "gave_up"} (see the module docstring)."""
    gave_up = said_unanswerable(answer)
    should = not row.get("answerable", 1)
    if row.get("source") == "orbit":           # the accepted names of the person's own thing
        text = normalise(answer)
        named = 0.0 if gave_up else float(any(_has_words(text, normalise(n)) for n in row["answers"]))
        return {"accuracy": named, "contains": named, "should_give_up": False, "gave_up": gave_up}
    scored = "unanswerable" if gave_up else answer
    accuracy = vizwiz_accuracy(scored, row["answers"])
    text = normalise(answer)
    contains = 0.0 if gave_up else float(any(_has_words(text, a) for a in agreed_answers(row["answers"])))
    if should and gave_up:
        contains = 1.0
    return {"accuracy": accuracy, "contains": float(max(contains, accuracy >= 1.0)), "should_give_up": should,
            "gave_up": gave_up}


# ----------------------------------------------------------------- sorting questions into topics (simple rules)

def _words(*phrases):
    """One regular expression matching any of the phrases as whole words."""
    return re.compile(r"(?<![a-z0-9])(" + "|".join(phrases) + r")(?![a-z0-9])")


# Each topic: words in the question, and words in the answers people agreed on. The topic with the most matches
# wins (question words count double); documents (reading) only when no other topic matched; else everyday.
TOPIC_WORDS = {
    "medicines": _words(
        r"medicines?", r"medications?", r"meds", r"pills?", r"capsules?", r"prescriptions?", r"pharmacy",
        r"dosage", r"doses?", r"vitamins?", r"multivitamins?", r"supplements?",
        r"inhalers?", r"insulin", r"syringes?", r"eye ?drops", r"ointment", r"bandages?", r"band ?aids?",
        r"thermometer", r"glucose", r"blood (pressure|sugar)", r"ibuprofen", r"tylenol", r"advil", r"aspirin",
        r"acetaminophen", r"motrin", r"aleve", r"naproxen", r"claritin", r"loratadine", r"benadryl", r"zyrtec",
        r"cetirizine", r"mucinex", r"nyquil", r"dayquil", r"robitussin", r"sudafed", r"pepto", r"tums",
        r"antacid", r"laxative", r"omeprazole", r"prilosec", r"metformin", r"lisinopril", r"prednisone",
        r"amoxicillin", r"neosporin", r"hydrocortisone", r"cough (syrup|drops|medicine)",
        r"antibiotics?", r"drug store", r"rx", r"nasal spray", r"allergy (medicine|relief|pills|tablets)",
        r"melatonin", r"fish oil", r"probiotics?",
        r"pain reliever", r"cold medicine", r"tablets? (of|for)", r"first aid", r"hearing aids?", r"vicks",
        r"excedrin", r"gauze", r"saline", r"contact lens(es)? solution", r"rubbing alcohol", r"peroxide"),
    "drugs": _words(
        r"marijuana", r"cannabis", r"thc", r"cbd", r"bongs?", r"vapes?", r"vaping", r"e ?cigarettes?",
        r"cigarettes?", r"cigars?", r"tobacco", r"nicotine", r"rolling papers?", r"newport", r"marlboro",
        r"camel (cigarettes|filters|lights)", r"cocaine", r"heroin", r"joint"),
    "firearms": _words(
        r"guns?", r"rifles?", r"pistols?", r"handguns?", r"shotguns?", r"revolvers?", r"ammo", r"ammunition",
        r"bullets?", r"holsters?", r"caliber", r"calibre", r"firearms?"),
    "food": _words(
        r"food", r"eat", r"eating", r"cook", r"cooking", r"bake", r"baking", r"recipe", r"cereal", r"soups?",
        r"canned", r"beans", r"rice", r"pasta", r"noodles?", r"ramen", r"sauce", r"spices?", r"seasoning",
        r"salt", r"sugar", r"flour", r"bread", r"cake", r"cookies?", r"candy", r"chocolate", r"chips", r"snacks?",
        r"cheese", r"meat", r"chicken", r"beef", r"pork", r"tuna", r"eggs?", r"fruit", r"bananas?",
        r"vegetables?", r"tomato(es)?", r"potato(es)?", r"corn", r"peas", r"frozen", r"nutrition", r"calories",
        r"ingredients", r"flavou?rs?", r"pizza", r"burger", r"sandwich", r"dinner", r"lunch", r"breakfast",
        r"oatmeal", r"popcorn", r"peanuts?", r"peanut butter", r"jelly", r"jam", r"honey", r"syrup", r"ketchup",
        r"mustard", r"mayo(nnaise)?", r"salad dressing", r"yogh?urt", r"ice cream", r"grocer(y|ies)",
        r"brownies?", r"muffins?", r"crackers?", r"gravy", r"macaroni", r"spaghetti", r"pancakes?",
        r"dog food", r"cat food", r"pet food", r"cooking (instructions|directions)", r"campbell'?s?", r"kraft",
        r"heinz", r"kellogg'?s?", r"nabisco", r"pringles", r"doritos", r"betty crocker", r"pillsbury",
        r"hamburger helper", r"cream of (mushroom|chicken)", r"quaker", r"cheerios", r"hormel", r"del monte",
        r"green giant", r"progresso", r"lays", r"oreos?", r"cinnamon", r"oregano", r"basil", r"paprika",
        r"vinegar", r"olive oil", r"cooking oil", r"butter", r"margarine", r"tortillas?", r"oats", r"granola",
        r"cupcakes?", r"pie", r"soup mix", r"stuffing", r"broth", r"stock cubes?", r"bouillon", r"chili",
        r"salsa", r"pudding", r"jello", r"gum", r"mints?", r"nuts", r"almonds?", r"raisins", r"apples?",
        r"oranges", r"grapes", r"lemons?", r"onions?", r"carrots?", r"lettuce", r"mushrooms? (soup)", r"steak",
        r"sausages?", r"bacon", r"ham", r"turkey", r"shrimp", r"salmon", r"sardines", r"pepperoni", r"lasagna",
        r"burrito", r"tacos?", r"nachos", r"cornbread", r"biscuits?", r"waffles?", r"bagels?", r"cheesecake",
        r"spinach", r"broccoli", r"green beans", r"baked beans", r"best before", r"use by", r"sell by",
        r"expir(y|ation|es|ed)", r"best by"),
    "drinks": _words(
        r"drinks?", r"beverages?", r"soda", r"pop", r"colas?", r"coke", r"coca ?cola", r"pepsi", r"sprite",
        r"fanta", r"juice", r"bottled water", r"water bottle", r"sparkling water", r"tea", r"teas", r"tea bags?",
        r"coffee", r"k ?cups?", r"keurig pods?", r"espresso", r"milk", r"almond milk", r"soy milk", r"lemonade",
        r"gatorade", r"powerade", r"energy drinks?", r"red bull", r"monster energy", r"dr pepper",
        r"mountain dew", r"ginger ale", r"root beer", r"iced tea", r"hot chocolate", r"cocoa", r"smoothie",
        r"kool ?aid", r"crystal light", r"creamer", r"seltzer", r"tonic water", r"snapple", r"lipton",
        r"folgers", r"maxwell house", r"starbucks", r"nescafe", r"decaf", r"latte", r"cappuccino"),
    "alcohol": _words(
        r"beers?", r"wines?", r"vodka", r"whiske?y", r"rum", r"gin", r"tequila", r"bourbon", r"liquor",
        r"alcohol(ic)?", r"champagne", r"prosecco", r"hard cider", r"ale", r"lager", r"ipa", r"stout", r"merlot",
        r"chardonnay", r"cabernet", r"pinot", r"riesling", r"moscato", r"sauvignon", r"zinfandel", r"sangria",
        r"margarita", r"cocktails?", r"brandy", r"scotch", r"schnapps", r"liqueur", r"budweiser", r"coors",
        r"corona", r"heineken", r"bud light", r"miller lite", r"jack daniel'?s?", r"smirnoff", r"bacardi",
        r"guinness", r"sake", r"vermouth", r"kahlua", r"baileys", r"rose wine", r"red wine", r"white wine"),
    "machines": _words(
        r"buttons?", r"settings?", r"dials?", r"knobs?", r"switch(es)?", r"remote( control)?", r"tv",
        r"television", r"ovens?", r"stoves?", r"microwaves?", r"washer", r"washing machine", r"dryer",
        r"dishwasher", r"thermostat", r"air condition(er|ing)", r"fan", r"heater", r"on or off", r"turned on",
        r"turned off", r"plugged in", r"computers?", r"laptops?", r"keyboards?", r"mouse", r"printers?",
        r"cameras?", r"cars?", r"vehicles?", r"bikes?", r"bicycles?", r"batter(y|ies)", r"chargers?", r"cables?",
        r"plugs?", r"outlets?", r"light ?bulbs?", r"lamps?", r"appliances?", r"clocks?", r"watch", r"timer",
        r"coffee maker", r"toaster", r"blender", r"vacuum", r"dvd player", r"cd player", r"radio",
        r"speakers?", r"headphones", r"earbuds", r"controllers?", r"xbox", r"playstation", r"nintendo",
        r"wii", r"ipod", r"iphone", r"ipad", r"tablet", r"kindle", r"phone", r"cell ?phone", r"modem", r"router",
        r"usb", r"hdmi", r"tools?", r"screwdriver", r"drill", r"hammer", r"wrench", r"calculator", r"scale",
        r"fridge", r"refrigerator", r"freezer", r"thermometer reading", r"temperature", r"lights? (is |are )?on",
        r"lights? off", r"power button", r"volume", r"channel", r"display", r"led", r"cooker", r"kettle", r"iron",
        r"sewing machine", r"crock ?pot", r"slow cooker", r"air fryer", r"instant pot", r"mixer", r"engine",
        r"tire", r"tyre", r"dashboard"),
    "art": _words(
        r"paintings?", r"drawings?", r"artwork", r"art", r"sculptures?", r"statues?", r"figurines?",
        r"portraits?", r"canvas", r"guitars?", r"pianos?", r"violins?", r"ukuleles?", r"drums?", r"flutes?",
        r"harmonica", r"musical instruments?", r"instrument", r"vases?", r"ornaments?", r"museum", r"mural",
        r"mosaic", r"pottery", r"ceramic", r"tapestry", r"carving", r"sketch", r"cartoon", r"illustration",
        r"framed (picture|print|photo)", r"picture frame", r"print of"),
    "documents": _words(
        r"read", r"reads", r"reading", r"say", r"says", r"saying", r"text", r"written", r"writing", r"words?",
        r"letters?", r"mail", r"envelopes?", r"papers?", r"documents?", r"forms?", r"receipts?", r"pages?",
        r"books?", r"title", r"author", r"magazines?", r"newspapers?", r"signs?", r"screen", r"monitor",
        r"maps?", r"charts?", r"graphs?", r"table of contents", r"calendars?", r"instructions", r"directions", r"menu",
        r"sheet music", r"posters?", r"tickets?", r"labels?", r"printed", r"brochure", r"flyer", r"coupons?",
        r"notes?", r"message", r"error", r"spell(ed)?", r"language", r"barcode", r"date", r"bills? (say|for)",
        r"cards?", r"greeting cards?", r"birthday cards?", r"handwriting", r"braille"),
    "nature": _words(
        r"plants?", r"flowers?", r"trees?", r"leaf", r"leaves", r"grass", r"garden", r"birds?", r"dogs?",
        r"cats?", r"animals?", r"insects?", r"bugs?", r"spiders?", r"butterfl(y|ies)", r"bees?", r"squirrels?",
        r"deer", r"horses?", r"cows?", r"sky", r"clouds?", r"cloudy", r"weather", r"sunny", r"raining", r"snow",
        r"sunset", r"sunrise", r"lake", r"ocean", r"beach", r"mountains?", r"rocks?", r"mushrooms?",
        r"weeds?", r"seeds?", r"soil", r"puppy", r"kitten", r"breed", r"fish tank", r"aquarium", r"moon",
        r"stars", r"outside", r"yard", r"lawn", r"roses?", r"tulips?", r"daisy", r"cactus", r"succulent",
        r"fern", r"ivy", r"moss", r"pine", r"oak", r"maple", r"frog", r"snake", r"lizard", r"turtle", r"rabbit",
        r"bunny", r"mouse droppings", r"ants?", r"moth", r"wasp", r"caterpillar", r"worm", r"beetle", r"cricket",
        r"cockroach", r"roach", r"sea shells?", r"shells?", r"park", r"field", r"woods", r"forest"),
}
# Words that stop a match (a "cartridge" of ink is not ammunition; an "apple" phone is not fruit).
NOT_TOPIC = {
    "food": _words(r"apple (tv|watch|phone|computer|ipad|iphone|laptop)", r"orange (color|colour|shirt)",
                   r"color", r"colour"),
    "machines": _words(r"(eye|reading) ?glasses"),
    "nature": _words(r"hot dogs?", r"cat food", r"dog food", r"pet food", r"corn dog"),
    "firearms": _words(r"glue gun", r"nail gun", r"staple gun", r"heat gun", r"water gun", r"toy gun"),
    "drinks": _words(r"pop ?corn", r"pop tarts?", r"k ?pop"),
    "art": _words(r"what is this (a )?picture of", r"in this picture", r"of this picture"),
}
# A question about a book, album or other printed title is about reading it, whatever the title says ("cats"), unless
# the question itself names a subject.
TITLES = _words(r"books?", r"audio ?books?", r"titles?", r"pamphlets?", r"magazines?", r"newspapers?", r"albums?",
                r"cds?", r"dvds?", r"movies?", r"novels?", r"author")
# Topics that need a word in the question itself (an answer alone is too unsure: "glue gun").
QUESTION_ONLY = {"firearms"}
# The order a tie is broken in: the specific subjects first, reading last.
TOPIC_ORDER = ["medicines", "drugs", "firearms", "alcohol", "drinks", "food", "art", "nature", "machines",
               "documents"]


def _match_count(pattern, text):
    """How many different words of pattern are in text."""
    return len({m.group(1) for m in pattern.finditer(text)})


def classify_topic(question, people=()):
    """The topic id of a real question from its words and the answers at least two people agreed on, "home_tests"
    for a home health test (pregnancy, COVID-19, ovulation: reading the result lines), or "everyday". Question words
    count double; documents (reading text) only when no subject topic matched."""
    q = " " + str(question or "").lower().replace("’", "'") + " "
    a = " ".join(agreed_answers(people)) if people else ""
    if HOME_TEST_WORDS.search(q) or (TEST_LINES.search(q) and TEST_HINTS.search(q + " " + a) and
                                     "screen" not in q):
        return HOME_TESTS
    best, best_score = EVERYDAY, 0
    for topic in TOPIC_ORDER:
        if topic == "documents":
            continue
        blocked = NOT_TOPIC.get(topic)
        q_text = blocked.sub(" ", q) if blocked else q
        a_text = blocked.sub(" ", a) if blocked else a
        score = 2 * _match_count(TOPIC_WORDS[topic], q_text) + _match_count(TOPIC_WORDS[topic], a_text)
        in_question = _match_count(TOPIC_WORDS[topic], q_text)
        if not in_question and (topic in QUESTION_ONLY or TITLES.search(q)):
            score = 0
        if score > best_score:
            best, best_score = topic, score
    if best == EVERYDAY and (_match_count(TOPIC_WORDS["documents"], q) or
                             _match_count(TOPIC_WORDS["documents"], a)):
        best = "documents"
    return best


KINDS = [   # (kind, what it is in plain words, pattern on the question); the first that fits is used
    ("expiry", "an expiry or use-by date", _words(r"expir\w*", r"best by", r"best before", r"use by", r"sell by",
                                                  r"good until", r"still good", r"date on")),
    ("money", "money: which note or coin", _words(r"dollars?", r"bills?", r"money", r"currency", r"coins?",
                                                  r"cash", r"cents?", r"denomination", r"euros?", r"pounds? note")),
    ("on_off", "is it on or off", _words(r"on or off", r"off or on", r"turned (on|off)", r"switched (on|off)",
                                         r"is (it|this|that|the \w+) (turned |switched )?(on|off)(?= ?\??\s*$)",
                                         r"lights? (is |are )?on\??\s*$",
                                         r"plugged in")),
    ("button", "which button or setting", _words(r"buttons?", r"settings?", r"dials?", r"knobs?", r"switch",
                                                 r"set to", r"which (one|key)", r"keys? (is|on)")),
    ("colour", "a colour", _words(r"colou?rs?", r"colou?red")),
    ("amount", "an amount, number or time", _words(r"how (much|many|long|old)", r"price", r"cost", r"amount",
                                                   r"weight", r"weigh", r"calories", r"temperature", r"what time",
                                                   r"number", r"total", r"balance", r"percent", r"degrees",
                                                   r"ounces?", r"oz", r"servings?")),
    ("read", "reading text", _words(r"read", r"say", r"says", r"text", r"written", r"writing", r"words?",
                                    r"title", r"label", r"letters?", r"screen", r"spell", r"name of")),
    ("what", "what is this (naming a thing)", _words(r"what('s| is| are)( this| that| these| it| in)",
                                                     r"what kind", r"what type", r"what brand", r"which brand",
                                                     r"what flavou?r", r"identify", r"what can", r"what am i")),
]
KIND_WORDS = {k: words for k, words, _p in KINDS} | {"medicine": "which medicine it is", "yes_no": "a yes or no",
                                                     "other": "another kind of question"}


def classify_kind(question, topic="", answer_type=""):
    """The type of a real question (KIND_WORDS): an expiry date, money, on or off, which button, a colour, an
    amount, reading text, a medicine's name (a "what" or reading question about medicines), what is this, a yes or
    no, or other."""
    q = " " + str(question or "").lower().replace("’", "'") + " "
    for kind, _words_, pattern in KINDS:
        if pattern.search(q):
            if kind in ("what", "read") and topic == "medicines":
                return "medicine"
            return kind
    if answer_type == "yes/no":
        return "yes_no"
    return "other"


# ----------------------------------------------------------------- leaving private things out

PRIVATE = _words(
    r"social security", r"ssn", r"passwords?", r"passports?", r"licen[cs]e plate", r"pin number",
    r"how do i look", r"my face", r"selfie", r"tattoos?", r"nude", r"naked", r"sex", r"sexy", r"sexual",
    r"condoms?", r"porn\w*", r"lingerie", r"underwear", r"bra", r"breasts?", r"penis", r"vagina", r"genitals?",
    r"\w+@\w+\.\w+")


def private_reason(question, people=()):
    """Why a VizWiz question must be left out ("" when it may be used): it asks about, or its answers show, things
    that identify someone or are intimate (passwords, identity numbers, faces and looks, tattoos, number plates,
    nudity or sex, an e-mail address), or an answer holds a long number (a phone, card or account number). Questions
    about bills, cards, mail, prescription labels and screens are kept: they are what blind people ask most."""
    q = " " + str(question or "").lower() + " "
    answers = " ".join(str(p or "").lower() for p in people)
    found = PRIVATE.search(q) or PRIVATE.search(" " + answers + " ")
    if found:
        return f"private: {found.group(1)}"
    if re.search(r"\d[\d \-]{6,}\d", answers.replace(",", "")) and not re.search(r"\d+\.\d\d", answers):
        return "private: a long number"
    return ""


def question_key(text):
    """A question reduced to its letters and digits, to match the same question in two VizWiz files."""
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


# ----------------------------------------------------------------- choosing a balanced set

def pick_mix(rows, want, unanswerable_share=0.25, seed=2026):
    """Up to want of rows (one topic's questions), taking the kinds of question in turn so the topic has a mix, with
    at most unanswerable_share of questions that cannot be answered, and a question asked again about another photo
    only when the others run out. The same rows each time (seed)."""
    pool = sorted(rows, key=lambda r: r["id"])
    random.Random(seed).shuffle(pool)
    seen, first, again = set(), [], []
    for r in pool:                     # the same question asked again (another photo) only when others run out
        key = question_key(r["question"])
        (again if key in seen else first).append(r)
        seen.add(key)
    pool = again[::-1] + first[::-1]   # taken from the end: first-time questions first
    most_unanswerable = int(want * unanswerable_share)
    kinds = {}
    for r in pool:
        kinds.setdefault(r["kind"], []).append(r)
    taken, unanswerable = [], 0
    while len(taken) < want and any(kinds.values()):
        for kind in sorted(kinds):
            while kinds[kind] and len(taken) < want:
                r = kinds[kind].pop()
                if not r.get("answerable", 1):
                    if unanswerable >= most_unanswerable:
                        continue
                    unanswerable += 1
                taken.append(r)
                break
    return taken


# ----------------------------------------------------------------- the list

def load_set(path=SET_FILE):
    """The real questions (the rows of real_questions.jsonl)."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def for_topic(rows, topic_id=""):
    """The rows to test for a topic: its own questions and the everyday ones, and for medicines and health the home
    health tests too (all rows when no topic is given)."""
    if not topic_id:
        return list(rows)
    wanted = {topic_id, EVERYDAY} | ({HOME_TESTS} if topic_id in HOME_TEST_TOPICS else set())
    return [r for r in rows if r["topic"] in wanted]


def counts(rows):
    """{topic: how many questions} for rows, in the topics' order, everyday last."""
    out = {}
    for r in rows:
        out[r["topic"]] = out.get(r["topic"], 0) + 1
    return out


def picture_name(row):
    """The file name of a real question's picture on this computer."""
    return row["image"] if row["source"] == "vizwiz" else "orbit-" + row["image"]


def _stem(path):
    """A picture's file name without its folder, extension and the kit's prefixes ("orbit-", "vizwizq-")."""
    name = os.path.splitext(os.path.basename(str(path or "")))[0]
    for prefix in ("orbit-", "vizwizq-", "vizwiz-", "realq-"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def leave_out(rows, real_rows=None):
    """(training rows without the real questions' pictures, how many were left out): a picture of the real
    questions is never trained on, whichever collection brings it (the ORBIT pack, a VizWiz collection)."""
    try:
        real_rows = load_set() if real_rows is None else real_rows
    except OSError:
        return list(rows), 0
    stems = {os.path.splitext(r["image"])[0] for r in real_rows}
    kept = [r for r in rows if _stem(r.get("picture")) not in stems]
    return kept, len(rows) - len(kept)


# ----------------------------------------------------------------- downloading the pictures

def _session():
    """A requests session with the kit's plain user agent."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def _orbit_frame(session, row, cache):
    """One ORBIT frame's bytes, read from ORBIT's zip with a byte range (its place is in the row). figshare sends
    the zip from a signed address that expires within seconds, so the address is looked up again when refused."""
    url = ORBIT_ZIPS[row["zip"]]
    start, size = int(row["offset"]), int(row["size"])
    for _attempt in range(4):
        if url not in cache:
            first = session.get(url, headers={"Range": "bytes=0-0"}, timeout=120, allow_redirects=True)
            first.raise_for_status()
            cache[url] = first.url
        answer = session.get(cache[url], headers={"Range": f"bytes={start}-{start + 30 + 1024 + size}"},
                             timeout=300)
        if answer.status_code == 206:
            data = answer.content
            name_length, extra_length = int.from_bytes(data[26:28], "little"), int.from_bytes(data[28:30], "little")
            name = data[30:30 + name_length].decode("utf-8", "replace")
            if data[:4] != b"PK\x03\x04" or not name.endswith(row["image"]):
                raise RuntimeError(f"ORBIT's zip did not have {row['image']} where expected")
            body = data[30 + name_length + extra_length:30 + name_length + extra_length + size]
            return zlib.decompress(body, -15) if int(row.get("method", 8)) == 8 else body
        cache.pop(url, None)
    raise RuntimeError(f"ORBIT's zip could not be read for {row['image']}")


def fetch_pictures(rows, folder, say=print):
    """Download the pictures of rows that are not in folder yet (VizWiz photos from VizWiz's server, ORBIT frames
    from ORBIT's zip); returns (rows whose picture is here, each with "picture" set, how many could not be had).
    Already downloaded pictures are never fetched again."""
    os.makedirs(folder, exist_ok=True)
    missing = [r for r in rows if not os.path.exists(os.path.join(folder, picture_name(r)))]
    if missing:
        say(f"  Downloading {len(missing)} photos of the real questions (once; about "
            f"{max(1, len(missing) * 250 // 1000)} MB).")
        session, cache, failed = _session(), {}, 0
        for number, row in enumerate(missing, 1):
            path = os.path.join(folder, picture_name(row))
            try:
                if row["source"] == "vizwiz":
                    answer = session.get(VIZWIZ_PICTURES + row["image"], timeout=120)
                    answer.raise_for_status()
                    data = answer.content
                else:
                    data = _orbit_frame(session, row, cache)
                with open(path + ".part", "wb") as f:
                    f.write(data)
                os.replace(path + ".part", path)
            except Exception:  # noqa: BLE001 - counted and said; the test goes on with the others
                failed += 1
            if number % 50 == 0 or number == len(missing):
                say(f"    {number} of {len(missing)} photos downloaded")
        if failed:
            say(f"  {failed} photos could not be downloaded; they are left out of this test.")
    here = [dict(r, picture=os.path.join(folder, picture_name(r))) for r in rows
            if os.path.exists(os.path.join(folder, picture_name(r)))]
    return here, len(rows) - len(here)


# ----------------------------------------------------------------- summing up

def summarise(results):
    """{group: {"questions", "accuracy", "contains", "should", "gave_up_right", "answerable", "gave_up_wrong"}} for
    results (rows with their scores), for each topic and "all"."""
    out = {}
    for r in results:
        for group in (r["topic"], "all"):
            s = out.setdefault(group, {"questions": 0, "accuracy": 0.0, "contains": 0.0, "should": 0,
                                       "gave_up_right": 0, "answerable": 0, "gave_up_wrong": 0})
            s["questions"] += 1
            s["accuracy"] += r["accuracy"]
            s["contains"] += r["contains"]
            if r["should_give_up"]:
                s["should"] += 1
                s["gave_up_right"] += int(r["gave_up"])
            else:
                s["answerable"] += 1
                s["gave_up_wrong"] += int(r["gave_up"])
    for s in out.values():
        s["accuracy"] /= s["questions"]
        s["contains"] /= s["questions"]
    return out


def _percent(part, whole):
    """A share in whole percent ("40 percent"), or "none" when whole is 0."""
    return f"{round(100 * part / whole)} percent" if whole else "none"


def _topic_title(topic_id):
    """A topic's name for people ("Food and packaged goods"), or "Everyday questions"."""
    if topic_id == EVERYDAY:
        return "Everyday questions"
    if topic_id == HOME_TESTS:
        return "Home health tests (pregnancy, COVID-19, ovulation)"
    if topic_id == "all":
        return "All questions"
    try:
        import topics
        found = topics.find(topic_id)
        return found.title if found else topic_id
    except ImportError:
        return topic_id


def _verdict(accuracy):
    """Plain words for an accuracy."""
    if accuracy >= 0.6:
        return "good: most answers match what people said"
    if accuracy >= 0.4:
        return "fair: about half the answers match"
    if accuracy >= 0.2:
        return "weak: few answers match"
    return "poor: hardly any answers match"


def group_lines(group, s):
    """The plain lines for one topic's scores (s from summarise)."""
    lines = [f"{_topic_title(group)} ({s['questions']} questions): accuracy {s['accuracy']:.2f}, "
             f"{_verdict(s['accuracy'])}. The answer held what people said in "
             f"{_percent(s['contains'] * s['questions'], s['questions'])}."]
    if s["should"]:
        lines.append(f"  Of {s['should']} questions the photo could not answer, it said so for "
                     f"{s['gave_up_right']} ({_percent(s['gave_up_right'], s['should'])}).")
    if s["answerable"] and s["gave_up_wrong"]:
        lines.append(f"  It gave up on {s['gave_up_wrong']} of {s['answerable']} questions that people could answer.")
    return lines


def _ordered(groups):
    """Topic groups in the topics' order, everyday and all last."""
    try:
        import topics
        order = [t.id for t in topics.TOPICS]
    except ImportError:
        order = []
    return sorted((g for g in groups if g not in ("all", EVERYDAY, HOME_TESTS)),
                  key=lambda g: order.index(g) if g in order else 99) + \
        [g for g in (HOME_TESTS, EVERYDAY, "all") if g in groups]


EXPLAIN = ["How it is scored: accuracy is VizWiz's standard score, from 0 to 1: an answer three or more of the ten "
           "sighted people also gave scores 1, one that two gave scores about 0.6, one that one gave about 0.3. ORBIT "
           "questions (\"What is this?\" about a blind person's own thing) score 1 when the answer names the thing.",
           "\"Held what people said\" is kinder to long answers: the answer contains an answer at least two people "
           "gave. A question the photo could not answer (most people said so) should be answered \"Unanswerable\" "
           "or \"I can't tell\"."]


def credit_lines(rows):
    """The credits of the sources the rows come from."""
    sources = {r["source"] for r in rows}
    return ["Credits (" + LICENCE + "):"] + [f"  {c}" for s, c in (("vizwiz", VIZWIZ_CREDIT),
                                                                  ("orbit", ORBIT_CREDIT)) if s in sources]


def report_lines(name, results, missing=0, topic_id=""):
    """The report of a real-questions test alone: what was tested, the scores for each topic in plain words, how it
    is scored, a few examples, and the credits."""
    summary = summarise(results)
    lines = [f"Real questions test: {name}", "",
             f"{len(results)} questions that blind people asked about their own photos"
             + (f" ({_topic_title(topic_id)} and everyday questions)" if topic_id else "") + "."
             + (f" {missing} photos could not be downloaded and were left out." if missing else ""), ""]
    if not results:
        return lines + ["No question could be tested."]
    for group in _ordered(summary):
        lines += group_lines(group, summary[group])
    lines += ["", *EXPLAIN, "", "Examples (the question, what people said, the model's answer, its score):", ""]
    seen = set()
    for r in results:
        if r["topic"] in seen:
            continue
        seen.add(r["topic"])
        people = ", ".join(agreed_answers(r["answers"], 2)[:3]) or ("unanswerable" if not r.get("answerable", 1)
                                                                    else ", ".join(r["answers"][:3]))
        lines += [f"{_topic_title(r['topic'])}: {r['question']}", f"  People: {people}",
                  f"  Model: {r['model_answer']}  (score {r['accuracy']:.2f})", ""]
    return lines + credit_lines(results)


def compare_lines(topic, before, after):
    """The topic add-on report's lines on the real questions: before and after on the topic's own real questions and
    the everyday ones (and the home health tests for medicines and health), in plain words. before and after:
    scored rows from answer_all, or their summarise() already made."""
    lines = ["  On blind people's real questions (VizWiz and ORBIT photos, never trained on):"]
    b = before if isinstance(before, dict) else summarise(before)
    a = after if isinstance(after, dict) else summarise(after)
    shown = False
    groups = [(topic.id, "this topic")] + ([(HOME_TESTS, "home health tests")] if topic.id in HOME_TEST_TOPICS else [])
    for group, name in groups + [(EVERYDAY, "everyday questions")]:
        if group not in b or group not in a:
            if group == topic.id:
                lines.append("    This topic has no real questions yet (no open set of blind people's questions "
                             "covers it), so it could not be tested this way.")
            continue
        shown = True
        gain = a[group]["accuracy"] - b[group]["accuracy"]
        words = ("better" if gain >= 0.02 else "worse" if gain <= -0.02 else "about the same")
        line = (f"    On {name} ({b[group]['questions']} questions): accuracy before {b[group]['accuracy']:.2f}, "
                f"after {a[group]['accuracy']:.2f}: {words}.")
        if b[group]["should"]:
            line += (f" Said \"unanswerable\" when it should: before {b[group]['gave_up_right']}, after "
                     f"{a[group]['gave_up_right']} of {b[group]['should']}.")
        lines.append(line)
    if shown:
        lines.append("    (Accuracy is VizWiz's standard score, 0 to 1: how well the short answer matches what ten "
                     "sighted people said.)")
    return lines


# ----------------------------------------------------------------- running the test (needs the graphics card)

def messages(row, system):
    """The conversation for one real question: the toolkit's system words, the photo, the question and ASK_SHORT."""
    from PIL import Image
    return [{"role": "system", "content": [{"type": "text", "text": system}]},
            {"role": "user", "content": [{"type": "image", "image": Image.open(row["picture"]).convert("RGB")},
                                         {"type": "text", "text": f"{row['question']}\n{ASK_SHORT}"}]}]


def answer_one(model, processor, row, device, system):
    """The model's short answer to one real question (greedy)."""
    import torch
    inputs = processor.apply_chat_template(messages(row, system), tokenize=True, return_dict=True,
                                           add_generation_prompt=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=ANSWER_TOKENS, do_sample=False)
    return processor.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def answer_all(answer, rows, out_path, say=print, label="real questions"):
    """Answer every row with answer(row) -> text, score it, and write out_path (.jsonl); answers already written
    are kept (a stopped test carries on). Returns the scored rows."""
    done = []
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            done = [json.loads(line) for line in f if line.strip()]
    finished = {r["id"] for r in done}
    todo = [r for r in rows if r["id"] not in finished]
    with open(out_path, "a", encoding="utf-8") as f:
        for number, row in enumerate(todo, len(done) + 1):
            text = answer(row)
            result = dict(row, model_answer=text, **score_row(row, text))
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
            f.flush()
            done.append(result)
            if number % 25 == 0 or number == len(rows):
                say(f"    {label}: {number} of {len(rows)} questions answered")
    wanted = {r["id"] for r in rows}
    return [r for r in done if r["id"] in wanted]


def find_addon(work, topic_id="", model="4b"):
    """The newest finished add-on in the kit's work folder (adapter-<run>/final), of a topic when topic_id is given;
    None when there is none."""
    if not os.path.isdir(work):
        return None
    found = []
    for name in os.listdir(work):
        final = os.path.join(work, name, "final")
        if not (name.startswith(f"adapter-{model}") and os.path.isdir(final)):
            continue
        if topic_id and f"-topic-{topic_id}" not in name:
            continue
        found.append((os.path.getmtime(final), final))
    return max(found)[1] if found else None


def resolve_target(target, work):
    """(what to test, said in words; the add-on folder or None for the model itself; the model key or None) for the
    --evaluate value: "4b" or "8b" (the model itself), an add-on folder (with adapter_config.json, or its "final"
    folder), or a result zip (its add-on is unpacked into work). Raises ValueError in plain words."""
    value = str(target or "").strip().strip('"')
    if value.lower() in ("4b", "8b"):
        return f"the {value.upper()} model itself", None, value.lower()
    if value.lower() == "base":
        return "the model itself", None, None
    if os.path.isdir(value):
        for folder in (value, os.path.join(value, "final")):
            if os.path.exists(os.path.join(folder, "adapter_config.json")):
                return f"the add-on {folder}", folder, _model_of(folder)
        raise ValueError(f"No add-on was found in {value} (it has no adapter_config.json).")
    if value.lower().endswith(".zip") and os.path.exists(value):
        import zipfile
        out = os.path.join(work, "real-questions-addons", os.path.splitext(os.path.basename(value))[0])
        with zipfile.ZipFile(value) as z:
            names = [n for n in z.namelist() if n.endswith("adapter_config.json") and not n.startswith("toolkit/")]
            if not names:
                raise ValueError(f"The zip {value} has no add-on in it.")
            prefix = names[0][:-len("adapter_config.json")]
            for n in z.namelist():
                if n.startswith(prefix) and not n.endswith("/"):
                    path = os.path.join(out, n[len(prefix):])
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with z.open(n) as src, open(path, "wb") as dst:
                        dst.write(src.read())
        return f"the add-on in {os.path.basename(value)}", out, _model_of(out)
    raise ValueError(f"{value} is not 4b, 8b, an add-on folder or a result zip.")


def _model_of(folder):
    """"4b" or "8b" from an add-on's label or settings, or None when they do not say."""
    for name in ("addon-label.json", "adapter_config.json"):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    text = json.dumps(json.load(f)).lower()
            except (OSError, ValueError):
                continue
            for key in ("8b", "4b"):
                if f"-{key}-" in text:
                    return key
    return None


def run_evaluation(train, target, topic_id="", model_key="4b", library=""):
    """kit\\run.cmd --evaluate TARGET [--topic ID]: test TARGET (see resolve_target) on the real questions (of the
    topic and the everyday ones when topic_id is given), on this computer's graphics card, and write
    report-real-questions-<name>.txt in the kit folder. train is the kit's train.py (its say, stop, model loading
    and folders). Returns 0."""
    say = train.say
    work = os.path.join(train.HERE, "work")
    os.makedirs(work, exist_ok=True)
    if topic_id:
        import topics
        topic = topics.find(topic_id)
        if topic is None:
            train.stop(f"There is no topic called {topic_id}. The topics are:\n" + topics.topic_list_text())
        topic_id = topic.id
    try:
        what, adapter, wanted = resolve_target(target, work)
    except ValueError as e:
        train.stop(str(e))
    model_key = wanted or model_key
    rows = for_topic(load_set(), topic_id)
    say("")
    say(f"Real questions test: {what}, on {len(rows)} questions blind people asked about their own photos"
        + (f" ({topic_id} and everyday)." if topic_id else "."))
    if topic_id and not any(r["topic"] == topic_id for r in rows):
        say(f"  The topic {topic_id} has no real questions yet (no open set of blind people's questions covers it); "
            "only the everyday questions are tested.")
    say("Step 1 of 3: checking the graphics card and getting the model (carries on if stopped).")
    train.check_computer(model_key, work, free_needed=25)
    folder = train.download_model(model_key, work)
    say("Step 2 of 3: downloading the photos of the real questions.")
    pictures = os.path.join(library, FOLDER_NAME) if library else os.path.join(work, FOLDER_NAME)
    rows, missing = fetch_pictures(rows, pictures, say)
    if not rows:
        train.stop("None of the photos of the real questions could be downloaded. Check the internet connection and "
                   "start again.")
    name = re.sub(r"[^A-Za-z0-9.-]+", "-", os.path.basename(os.path.dirname(adapter)) if adapter and
                  os.path.basename(adapter) == "final" else os.path.basename(adapter or model_key)).strip("-")
    name += f"-{topic_id}" if topic_id else ""
    say(f"Step 3 of 3: the model answers {len(rows)} questions (a few minutes).")
    model, processor = train.load_model(folder, adapter=adapter)
    model.eval()
    out = os.path.join(work, f"real-questions-{name}.jsonl")
    results = answer_all(lambda row: answer_one(model, processor, row, "cuda", train.SYSTEM), rows, out, say)
    report = os.path.join(train.HERE, f"report-real-questions-{name}.txt")
    with open(report, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines(what, results, missing, topic_id)) + "\n")
    overall = summarise(results).get("all", {"accuracy": 0.0})
    say("")
    say(f"FINISHED. Real questions test of {what}: accuracy {overall['accuracy']:.2f} on {len(results)} questions.")
    say(f"The report is {report}")
    return 0


def run_for_topic(train, topic, folder, final, results_dir, state, run, library=""):
    """For a topic add-on's training: the real questions of its topic and the everyday ones, answered by the model
    before training and by the add-on after, kept in results_dir (a stopped test carries on). Returns (before,
    after) scored rows, or ([], []) when the photos cannot be had: the training never stops for this test."""
    say = train.say
    rows = for_topic(load_set(), topic.id)
    pictures = os.path.join(library, FOLDER_NAME) if library else os.path.join(train.HERE, "work", FOLDER_NAME)
    try:
        rows, _missing = fetch_pictures(rows, pictures, say)
    except Exception as e:  # noqa: BLE001 - said in plain words; the training goes on
        say(f"  The real questions could not be downloaded ({e}); the report leaves them out.")
        return [], []
    if not rows:
        say("  The real questions' photos could not be downloaded; the report leaves them out.")
        return [], []
    scored = {}
    for part, adapter in (("before", None), ("after", final)):
        out = os.path.join(results_dir, f"real-questions-{part}.jsonl")
        if not state.done(f"realq-{part}-{run}"):
            say(f"  Real questions ({part} training): {len(rows)} questions blind people asked.")
            model, processor = train.load_model(folder, adapter=adapter)
            model.eval()
            answer_all(lambda row: answer_one(model, processor, row, "cuda", train.SYSTEM), rows, out, say,
                       f"real questions, {part} training")
            del model, processor
            train.free()
            state.mark(f"realq-{part}-{run}")
        with open(out, encoding="utf-8") as f:
            scored[part] = [json.loads(line) for line in f if line.strip()]
    return scored["before"], scored["after"]
