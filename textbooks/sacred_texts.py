"""Sacred and philosophical texts for the reference library, in the group "Reference, sacred and philosophical texts"
(the owner's request of 2026-11-22). Keys: sacred-texts (every book), sacred:<name>.

What this module builds, in plain words. Every translation is in the public domain in the US: published before 1931
(the builder reads each Internet Archive item's own record at every build and refuses a later reprint), or released
into the public domain by its publisher (the World English Bible). Each text is presented as its tradition presents
it: the book's own words, a neutral one-line description, and no commentary added by the toolkit. Grouped by
tradition (each book's subject names it):
  - Christianity: the King James Version (Authorized Version, Pure Cambridge Edition), the American Standard Version
    (1901) and the World English Bible (a modern-English translation dedicated to the public domain, from eBible.org);
  - Judaism: the Hebrew Bible (Tanakh) in the Jewish Publication Society's translation of 1917;
  - Islam: the Quran in Marmaduke Pickthall's "The Meaning of the Glorious Koran" (1930) and E. H. Palmer's
    translation (Sacred Books of the East, 1880);
  - the Latter Day Saint movement: the Book of Mormon (1920 edition, with chapters and verses);
  - Hinduism: the Bhagavad Gita (Edwin Arnold's "The Song Celestial", and K. T. Telang's prose translation of 1882)
    and the Upanishads (Max Müller, 1879 and 1884; R. E. Hume's Thirteen Principal Upanishads, 1921);
  - Buddhism: the Dhammapada (Max Müller, 1881) and Henry Clarke Warren's Buddhism in Translations;
  - Taoism: the Tao Te Ching (Paul Carus, 1898; James Legge's Texts of Taoism, 1891);
  - Confucianism: the Analects, the Great Learning, the Doctrine of the Mean and Mencius (James Legge, The Four Books);
  - Sikhism: Max Arthur Macauliffe's The Sikh Religion (1909), the English translation of much of the Guru Granth
    Sahib with the lives of the Gurus as he tells them (no complete public-domain translation exists);
  - the Bahá'í Faith: 'Abdu'l-Bahá's Some Answered Questions (Laura Clifford Barney's translation, 1908);
  - Zoroastrianism: the Zend-Avesta (James Darmesteter, Sacred Books of the East, 1880);
  - classic philosophy: Plato (Jowett), Aristotle's Ethics and Politics, Lucretius, Marcus Aurelius and Epictetus
    (George Long), Boethius, Augustine's Confessions, Descartes, Hobbes, Spinoza, Locke, Hume, Kant (Meiklejohn),
    Mill, Schopenhauer, Nietzsche and William James;
  - a short neutral introduction to each text and tradition: the lead section (only the opening, before the first
    heading) of the English Wikipedia article on each text, CC BY-SA 4.0, as a separate SHARE-ALIKE book.

Already in the library and not repeated: Project Gutenberg and Wikisource whole in the Kiwix library (they hold most
of these texts too; the books here are the chosen editions, each with its year checked).

Not built (NOT_INCLUDED): modern copyrighted translations (NIV, ESV, NRSV, the new JPS, Sahih International, Yusuf
Ali's 1934 Quran (still protected in the US until 2030: restored foreign work), Easwaran, Feng and English and
others), the Bahá'í Reference Library (its own terms), sacred-texts.com (its own copyright on the edition), and Project
Gutenberg's site (refuses programs at times; Kiwix holds it).

Licences: "Public domain (published before 1931)" for the old books; "Public domain (dedicated by its publisher)" for
the World English Bible (eBible.org's page says so, checked at every build); CC BY-SA 4.0 for the Wikipedia
introductions (Wikipedia's copyright page checked at every build).

Run from the repository's folder:
  python3 textbooks/sacred_texts.py sacred:wikipedia_introductions --out build/textbooks --limit 3
  python3 textbooks/sacred_texts.py --list sacred-texts
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "sacred"
GROUPS = {GROUP: "Reference, sacred and philosophical texts"}

# The respectful presentation every book carries in its notice.
RESPECT = ("Presented as its tradition presents it: the text's own words, with no commentary added by the toolkit.")
OLD_WORDS = ("{year} translation: its English is of its time (\"thee\" and \"thou\" in places), and the "
             "translator's own introduction and notes are kept as printed.")


def text(name, title, tradition, publisher, archive, year, description, note=OLD_WORDS, country="United States"):
    """One sacred or philosophical text (an old Internet Archive book) under its tradition's subject."""
    return old_book(GROUP, name, title, tradition, publisher, archive, year, description, note=note, notice=RESPECT,
                    country=country)


CHRISTIAN = "Sacred texts: Christianity (the Bible)"
JEWISH = "Sacred texts: Judaism (the Hebrew Bible)"
ISLAM = "Sacred texts: Islam (the Quran)"
LDS = "Sacred texts: the Latter Day Saint movement"
HINDU = "Sacred texts: Hinduism"
BUDDHIST = "Sacred texts: Buddhism"
TAOIST = "Sacred texts: Taoism"
CONFUCIAN = "Sacred texts: Confucianism"
SIKH = "Sacred texts: Sikhism"
BAHAI = "Sacred texts: the Bahá'í Faith"
ZOROASTRIAN = "Sacred texts: Zoroastrianism"
PHILOSOPHY = "Philosophy: classic works"

PDFS = [
    # ---------------------------------------------------------------- Christianity
    text("kjv_bible", "The Holy Bible: King James Version (Authorized Version, Pure Cambridge Edition)", CHRISTIAN,
         "Cambridge University Press", "TheHolyBibleAuthorizedKingJamesVersionPureCambridgeEdition", 1900,
         "The Bible in the King James Version of 1611 (the Authorized Version), in the Pure Cambridge Edition's text: "
         "the Old and New Testaments.", note="In the US the King James Version is in the public domain (in the "
         "United Kingdom the Crown's rights apply)."),
    text("asv_bible_1901", "The Holy Bible: American Standard Version (1901)", CHRISTIAN,
         "Thomas Nelson and Sons (American Revision Committee)", "holybible00newy", 1901,
         "The Bible in the American Standard Version of 1901: the Old and New Testaments, newly edited by the "
         "American Revision Committee."),
    # ---------------------------------------------------------------- Judaism
    text("jps_tanakh_1917", "The Holy Scriptures according to the Masoretic Text (Jewish Publication Society, 1917)",
         JEWISH, "Jewish Publication Society of America", "holyscripturesac028077mbp", 1917,
         "The Hebrew Bible (Tanakh) in the Jewish Publication Society's English translation of 1917: the Torah, the "
         "Prophets (Nevi'im) and the Writings (Ketuvim), in the Jewish order of the books."),
    # ---------------------------------------------------------------- Islam
    text("pickthall_quran_1930", "The Meaning of the Glorious Koran (Marmaduke Pickthall, 1930)", ISLAM,
         "Marmaduke Pickthall (Alfred A. Knopf)", "MN40248ucmf_9", 1930,
         "The Quran in Marmaduke Pickthall's English translation of 1930, the first by an English Muslim, surah by "
         "surah. As Pickthall's foreword says, Muslims hold that the Quran is the Arabic text itself, so an English "
         "version is an attempt to give its meaning.", note="Published in 1930: in the US public domain since 2026.",
         country="United Kingdom"),
    text("palmer_quran_1880", "The Qur'an (E. H. Palmer, Sacred Books of the East, 1880)", ISLAM,
         "E. H. Palmer (Clarendon Press, Oxford)", "thequraan09unknuoft", 1880,
         "The Quran in E. H. Palmer's English translation for the Sacred Books of the East series, surah by surah.",
         country="United Kingdom"),
    # ---------------------------------------------------------------- the Latter Day Saint movement
    text("book_of_mormon_1920", "The Book of Mormon (1920 edition)", LDS,
         "The Church of Jesus Christ of Latter-day Saints", "bookofmormonacco00bookuoft", 1920,
         "The Book of Mormon in its 1920 edition, divided into chapters and verses, with its introductory pages and "
         "the testimonies of witnesses as printed."),
    # ---------------------------------------------------------------- Hinduism
    text("arnold_bhagavad_gita", "The Song Celestial, or Bhagavad-Gita (Edwin Arnold)", HINDU,
         "Edwin Arnold (Truslove, Hanson and Comba)", "songcelestialorb00edwi", 1906,
         "The Bhagavad Gita, from the Mahabharata, in Edwin Arnold's English verse translation: the dialogue between "
         "Arjuna and Krishna in eighteen chapters.", country="United Kingdom"),
    text("telang_bhagavad_gita_1882", "The Bhagavadgita (K. T. Telang, Sacred Books of the East, 1882)", HINDU,
         "Kashinath Trimbak Telang (Clarendon Press, Oxford)", "wg908", 1882,
         "The Bhagavad Gita in K. T. Telang's close prose translation, with the Sanatsugatiya and the Anugita, for the "
         "Sacred Books of the East series.", country="United Kingdom"),
    text("muller_upanishads_1", "The Upanishads, part 1 (Max Müller, Sacred Books of the East, 1879)", HINDU,
         "F. Max Müller (Clarendon Press, Oxford)", "upanishads01ml", 1879,
         "The Upanishads in Max Müller's translation, part 1: the Chandogya, Talavakara (Kena), Aitareya, Kaushitaki "
         "and Vajasaneyi (Isha) Upanishads.", country="United Kingdom"),
    text("muller_upanishads_2", "The Upanishads, part 2 (Max Müller, Sacred Books of the East, 1884)", HINDU,
         "F. Max Müller (Clarendon Press, Oxford)", "upanishads02ml", 1879,
         "The Upanishads in Max Müller's translation, part 2: the Katha, Mundaka, Taittiriya, Brihadaranyaka, "
         "Svetasvatara, Prasna and Maitrayana Upanishads.", country="United Kingdom"),
    text("hume_thirteen_upanishads_1921", "The Thirteen Principal Upanishads (Robert Ernest Hume, 1921)", HINDU,
         "Robert Ernest Hume (Oxford University Press)", "thirteenprincipa00hume", 1921,
         "The thirteen principal Upanishads in R. E. Hume's English translation, with his outline of their "
         "philosophy and an annotated bibliography."),
    # ---------------------------------------------------------------- Buddhism
    text("muller_dhammapada_1881", "The Dhammapada (Max Müller) and the Sutta-Nipata (Fausböll), Sacred Books of the "
         "East (1881)", BUDDHIST, "F. Max Müller and V. Fausböll (Clarendon Press, Oxford)",
         "dhammapadacollection01ml", 1881,
         "The Dhammapada, the collection of verses of the Pali canon, in Max Müller's translation, with V. "
         "Fausböll's translation of the Sutta-Nipata.", country="United Kingdom"),
    text("warren_buddhism_in_translations", "Buddhism in Translations (Henry Clarke Warren)", BUDDHIST,
         "Henry Clarke Warren (Harvard University, Harvard Oriental Series)", "buddhismintransl00warruoft", 1922,
         "Passages from the Pali Buddhist scriptures translated by Henry Clarke Warren: the Buddha's life, the "
         "sentient being, karma and rebirth, meditation and Nirvana, and the monastic order."),
    # ---------------------------------------------------------------- Taoism and Confucianism
    text("carus_tao_te_ching_1898", "Lao-Tze's Tao-Teh-King (Paul Carus, 1898)", TAOIST,
         "Paul Carus (Open Court Publishing)", "laotzestaotehkin00laoz", 1898,
         "The Tao Te Ching of Laozi in Chinese and English, with Paul Carus's transliteration and translation, chapter "
         "by chapter."),
    text("legge_texts_of_taoism_1891", "The Texts of Taoism (James Legge, Sacred Books of the East, 1891)", TAOIST,
         "James Legge (Clarendon Press, Oxford)", "sacredbooksofchi00laozuoft", 1891,
         "The Tao Te Ching and the writings of Zhuangzi (Kwang-tze) in James Legge's translation.",
         country="United Kingdom"),
    text("legge_four_books", "The Four Books: the Confucian Analects, the Great Learning, the Doctrine of the Mean and "
         "the Works of Mencius (James Legge)", CONFUCIAN, "James Legge", "fourbooksconfuci00leggiala", 1900,
         "The Four Books of Confucianism in James Legge's English translation: the Analects of Confucius, the Great "
         "Learning, the Doctrine of the Mean and the works of Mencius.", country="China"),
    # ---------------------------------------------------------------- Sikhism
    text("macauliffe_sikh_religion_1", "The Sikh Religion: its Gurus, Sacred Writings and Authors, volume 1 (Max Arthur "
         "Macauliffe, 1909)", SIKH, "Max Arthur Macauliffe (Clarendon Press, Oxford)", "thesikhreligion01macauoft",
         1909, "Volume 1 of Macauliffe's six volumes: Guru Nanak's life as Macauliffe tells it and his hymns from the "
         "Guru Granth Sahib in English, including the Japji.", country="United Kingdom"),
    text("macauliffe_sikh_religion_2", "The Sikh Religion, volume 2 (Max Arthur Macauliffe, 1909)", SIKH,
         "Max Arthur Macauliffe (Clarendon Press, Oxford)", "TheSikhReligionVolII", 1909,
         "Volume 2: Guru Angad, Guru Amar Das and Guru Ram Das, with their hymns from the Guru Granth Sahib in "
         "English.", country="United Kingdom"),
    text("macauliffe_sikh_religion_3", "The Sikh Religion, volume 3 (Max Arthur Macauliffe, 1909)", SIKH,
         "Max Arthur Macauliffe (Clarendon Press, Oxford)", "TheSikhReligionItsGurusSacredWritingsAndAuthorsVolIII",
         1909, "Volume 3: Guru Arjan and the compiling of the Granth Sahib, with his hymns in English, including the "
         "Sukhmani.", country="United Kingdom"),
    text("macauliffe_sikh_religion_5", "The Sikh Religion, volume 5 (Max Arthur Macauliffe, 1909)", SIKH,
         "Max Arthur Macauliffe (Clarendon Press, Oxford)", "thesikhreligioni05macauoft", 1909,
         "Volume 5: Guru Tegh Bahadur and Guru Gobind Singh, with their compositions in English.",
         country="United Kingdom"),
    text("macauliffe_sikh_religion_6", "The Sikh Religion, volume 6 (Max Arthur Macauliffe, 1909)", SIKH,
         "Max Arthur Macauliffe (Clarendon Press, Oxford)", "thesikhreligioni06macauoft", 1909,
         "Volume 6: the Bhagats (saints) whose hymns are in the Guru Granth Sahib (Kabir, Namdev, Ravidas, Farid and "
         "others), in English.", country="United Kingdom"),
    # ---------------------------------------------------------------- the Bahá'í Faith and Zoroastrianism
    text("abdul_baha_some_answered_questions_1908", "Some Answered Questions ('Abdu'l-Bahá, translated by Laura "
         "Clifford Barney, 1908)", BAHAI, "Laura Clifford Barney (Kegan Paul)", "someansweredques00abdurich", 1908,
         "Talks of 'Abdu'l-Bahá collected and translated from the Persian by Laura Clifford Barney (the 1908 "
         "translation; the Bahá'í World Centre published a revised one in 2014, which is not used here).",
         country="United Kingdom"),
    text("darmesteter_zend_avesta", "The Zend-Avesta, part 2 (James Darmesteter, Sacred Books of the East)",
         ZOROASTRIAN, "James Darmesteter (Clarendon Press, Oxford)", "zendavesta02darm", 1880,
         "The Avesta of Zoroastrianism in James Darmesteter's translation for the Sacred Books of the East: the "
         "Sirozahs, Yasts and Nyayis.", country="United Kingdom"),
]

PHILO = [
    ("jowett_plato_dialogues_2", "The Dialogues of Plato, volume 2 (Benjamin Jowett, 1892)", "Benjamin Jowett "
     "(Clarendon Press, Oxford)", "dialoguesofplato18922plat", 1892, "Plato's dialogues in Benjamin Jowett's "
     "translation, volume 2 of the third edition.", "United Kingdom"),
    ("jowett_plato_republic", "The Republic of Plato (Benjamin Jowett)", "Benjamin Jowett (Clarendon Press, Oxford)",
     "a604578400platuoft", 1888, "Plato's Republic in Benjamin Jowett's translation: justice, the ideal city and the "
     "allegory of the cave.", "United Kingdom"),
    ("jowett_plato_socratic", "The Four Socratic Dialogues of Plato: Euthyphro, Apology, Crito, Phaedo (Benjamin "
     "Jowett, 1903)", "Benjamin Jowett (Clarendon Press, Oxford)", "foursocraticdial00platuoft", 1903,
     "Plato's four dialogues on the trial and death of Socrates, in Jowett's translation.", "United Kingdom"),
    ("aristotle_nicomachean_ethics", "The Nicomachean Ethics of Aristotle (F. H. Peters)", "F. H. Peters (Kegan Paul, "
     "Trench)", "petersethics00arisrich", 1886, "Aristotle's Nicomachean Ethics: happiness, virtue, friendship and "
     "the good life.", "United Kingdom"),
    ("aristotle_politics", "Aristotle's Politics (Benjamin Jowett, 1905)", "Benjamin Jowett (Clarendon Press, "
     "Oxford)", "aristotlespoliti00arisuoft", 1905, "Aristotle's Politics in Jowett's translation: the household, "
     "citizenship, constitutions and the best state.", "United Kingdom"),
    ("lucretius_nature_of_things", "Lucretius, On the Nature of Things (H. A. J. Munro)", "H. A. J. Munro (Deighton, "
     "Bell)", "lucretiusonnatu00lucr", 1872, "Lucretius's poem on Epicurean philosophy: atoms, the soul, the world "
     "and the fear of death, in Munro's prose translation.", "United Kingdom"),
    ("long_marcus_aurelius", "The Meditations of the Emperor Marcus Aurelius Antoninus (George Long)",
     "George Long", "meditationsofemp00marcuoft", 1890, "Marcus Aurelius's Meditations, the Stoic emperor's notes to "
     "himself, in George Long's translation.", "United Kingdom"),
    ("long_epictetus_discourses", "The Discourses of Epictetus, with the Encheiridion and Fragments (George Long)",
     "George Long (George Bell)", "discoursesofepic033057mbp", 1890, "The Stoic teaching of Epictetus as written down "
     "by Arrian, with the Encheiridion (handbook), in George Long's translation.", "United Kingdom"),
    ("boethius_consolation", "The Consolation of Philosophy of Boethius (H. R. James)", "H. R. James (Elliot Stock)",
     "theconsolationof00boetuoft", 1900, "Boethius's dialogue with Philosophy, written in prison, in H. R. James's "
     "translation.", "United Kingdom"),
    ("augustine_confessions", "The Confessions of St. Augustine (E. B. Pusey)", "E. B. Pusey (J. M. Dent)",
     "confessionsofsta00auguuoft", 1909, "Augustine of Hippo's Confessions in E. B. Pusey's translation.",
     "United Kingdom"),
    ("descartes_discourse_method", "A Discourse on Method; Meditations on the First Philosophy; Principles of "
     "Philosophy (Descartes, John Veitch)", "John Veitch (J. M. Dent, Everyman's Library)",
     "discourseonmetho1912desc", 1912, "René Descartes's Discourse on Method, Meditations and Principles of "
     "Philosophy in John Veitch's translation.", "United Kingdom"),
    ("hobbes_leviathan", "Hobbes's Leviathan (reprinted from the edition of 1651)", "Thomas Hobbes (Clarendon Press, "
     "Oxford)", "hobbessleviathan00hobbuoft", 1909, "Thomas Hobbes's Leviathan: human nature, the social contract and "
     "the sovereign state.", "United Kingdom"),
    ("spinoza_ethics", "Improvement of the Understanding, Ethics and Correspondence of Benedict de Spinoza (R. H. M. "
     "Elwes)", "R. H. M. Elwes (M. Walter Dunne)", "improvementofund00spinuoft", 1901, "Spinoza's Ethics, his "
     "Treatise on the Improvement of the Understanding and his letters, in Elwes's translation.", "United States"),
    ("locke_human_understanding", "An Essay Concerning Human Understanding (John Locke)", "John Locke",
     "humanunderstandi00lockuoft", 1825, "John Locke's Essay on where our ideas and knowledge come from.",
     "United Kingdom"),
    ("hume_enquiry", "An Enquiry Concerning Human Understanding, and Selections from A Treatise of Human Nature (David "
     "Hume)", "David Hume (Open Court Publishing)", "enquiryconcernin00humeuoft", 1907, "David Hume's Enquiry on "
     "experience, cause and effect, miracles and scepticism.", "United States"),
    ("kant_critique_pure_reason", "Critique of Pure Reason (Immanuel Kant, J. M. D. Meiklejohn)",
     "J. M. D. Meiklejohn (George Bell)", "critiqueofpurere00kant", 1882, "Immanuel Kant's Critique of Pure Reason in "
     "Meiklejohn's translation.", "United Kingdom"),
    ("mill_on_liberty", "On Liberty (John Stuart Mill)", "John Stuart Mill (Longman)", "onliberty00inmill", 1864,
     "John Stuart Mill's essay on the limits of society's power over the individual: freedom of thought, speech and "
     "action.", "United Kingdom"),
    ("mill_utilitarianism", "Utilitarianism (John Stuart Mill)", "John Stuart Mill (Parker, Son and Bourn)",
     "a592840000milluoft", 1863, "John Stuart Mill's Utilitarianism: the greatest happiness principle and its "
     "defence.", "United Kingdom"),
    ("schopenhauer_world_will", "The World as Will and Idea, volume 1 (Arthur Schopenhauer, Haldane and Kemp)",
     "R. B. Haldane and J. Kemp (Kegan Paul)", "theworldaswillan01schouoft", 1910, "Volume 1 of Schopenhauer's main "
     "work in Haldane and Kemp's translation.", "United Kingdom"),
    ("nietzsche_zarathustra", "Thus Spake Zarathustra (Friedrich Nietzsche, Thomas Common)", "Thomas Common (Modern "
     "Library)", "thusspakezarathu00niet", 1917, "Friedrich Nietzsche's Thus Spake Zarathustra in Thomas Common's "
     "translation.", "United States"),
    ("james_varieties_religious_experience", "The Varieties of Religious Experience (William James, 1902)",
     "William James (Longmans, Green)", "varietiesofrelig00jameuoft", 1902, "William James's Gifford Lectures on the "
     "psychology of religious experience.", "United States"),
]
PDFS += [text(name, title, PHILOSOPHY, publisher, archive, year, description, country=country)
         for name, title, publisher, archive, year, description, country in PHILO]

# ====================================================================== the World English Bible (eBible.org)

WEB_PAGE = "https://ebible.org/find/details.php?id=engwebp"
PDFS.append(dict(
    group=GROUP, name="world_english_bible", title="The Holy Bible: World English Bible", subject=CHRISTIAN,
    publisher="eBible.org (Michael Paul Johnson and volunteers)", country="United States",
    licence="Public domain (dedicated by its publisher)", licence_url=WEB_PAGE, licence_page=WEB_PAGE,
    licence_text=r"The World English Bible is a Public Domain translation", level="reference",
    pdf="https://ebible.org/pdf/eng-web/eng-web_all.pdf", page=WEB_PAGE,
    version="The World English Bible as eBible.org publishes it (with the Deuterocanon/Apocrypha), read at build time",
    description="The World English Bible, a modern-English update of the American Standard Version that its makers "
                "dedicated to the public domain: the Old Testament, the Deuterocanonical books (Apocrypha) and the New "
                "Testament.",
    notice="From eBible.org: \"The World English Bible is a Public Domain translation of the Holy Bible into modern "
           "English.\" " + RESPECT))

# ====================================================================== short introductions (Wikipedia, CC BY-SA)

WIKI = "https://en.wikipedia.org/wiki/"
WIKI_LICENCE_PAGE = WIKI + "Wikipedia:Copyrights"
# (article, tradition): the lead section of each is read.
INTRO_ARTICLES = [
    ("Bible", "Christianity"), ("King_James_Version", "Christianity"), ("American_Standard_Version", "Christianity"),
    ("World_English_Bible", "Christianity"), ("Hebrew_Bible", "Judaism"), ("Torah", "Judaism"),
    ("Quran", "Islam"), ("The_Meaning_of_the_Glorious_Koran", "Islam"), ("Book_of_Mormon", "Latter Day Saint movement"),
    ("Bhagavad_Gita", "Hinduism"), ("Upanishads", "Hinduism"), ("Dhammapada", "Buddhism"), ("Pali_Canon", "Buddhism"),
    ("Tao_Te_Ching", "Taoism"), ("Analects", "Confucianism"), ("Mencius_(book)", "Confucianism"),
    ("Guru_Granth_Sahib", "Sikhism"), ("Some_Answered_Questions", "Bahai Faith"), ("Avesta", "Zoroastrianism"),
    ("Republic_(Plato)", "Philosophy"), ("Nicomachean_Ethics", "Philosophy"), ("Meditations", "Philosophy"),
    ("Discourses_of_Epictetus", "Philosophy"), ("The_Consolation_of_Philosophy", "Philosophy"),
    ("Critique_of_Pure_Reason", "Philosophy"), ("On_Liberty", "Philosophy"), ("Thus_Spoke_Zarathustra", "Philosophy"),
]
INTRO_URLS = [WIKI + a for a, _t in INTRO_ARTICLES]
# The lead section only: from the article's own text to its contents list or first second-level heading; infoboxes,
# notes, footnote marks, pictures and hidden parts are left out (first the pages' data-mw attributes, whose JSON
# holds ">" signs that would confuse the other patterns).
LEAD_START = r'<div class="mw-content-ltr mw-parser-output"[^>]*>'
LEAD_END = r'<meta property="mw:PageProp/toc"|<div class="mw-heading mw-heading2"'
LEAD_DROP = [r"\sdata-mw='[^']*'", r'\sdata-mw="[^"]*"'] + K.DROP + [r'<table class="infobox.*?</table>\s*(?=<p\b)', r"<table\b.*?</table>", r"<sup\b.*?</sup>",
                      r'<div[^>]*role="note".*?</div>', r"<figure\b.*?</figure>", r'<div class="shortdescription.*?</div>',
                      r"<link\b[^>]*>"]


def tradition_rules():
    """[(address pattern, part)]: each introduction under its tradition's part."""
    return [(r"/" + re.escape(a) + "$", t) for a, t in INTRO_ARTICLES]


GUIDES = [dict(
    K.WEB, group=GROUP, name="wikipedia_introductions", title="Introductions to the sacred and philosophical texts "
    "(Wikipedia excerpts)", subject="Sacred texts and philosophy: introductions",
    publisher="Wikipedia contributors (Wikimedia Foundation)", country="United States",
    licence="CC BY-SA 4.0", licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    licence_page=WIKI_LICENCE_PAGE, licence_text=r"Creative Commons Attribution-ShareAlike 4\.0",
    source=INTRO_URLS[0], crawl=[(INTRO_URLS[0], 0)], urls=list(INTRO_URLS),
    pages=r"^https://en\.wikipedia\.org/wiki/[A-Za-z0-9_(),%.'-]+$", content=(LEAD_START, LEAD_END), drop=LEAD_DROP,
    unit_rules=tradition_rules(), limit=len(INTRO_URLS) + 5,
    description="A short, neutral introduction to each text and tradition in this collection: the opening section "
                "(before the first heading) of the English Wikipedia article on each: the Bible and its English "
                "versions, the Hebrew Bible and the Torah, the Quran, the Book of Mormon, the Bhagavad Gita and the "
                "Upanishads, the Dhammapada and the Pali Canon, the Tao Te Ching, the Analects and Mencius, the Guru "
                "Granth Sahib, Some Answered Questions, the Avesta, and the classic works of philosophy.",
    notice="From Wikipedia, the free encyclopedia (en.wikipedia.org), by its contributors; each page names its article. "
           "Licensed CC BY-SA 4.0: share-alike, so anything made from this book keeps the same licence. Only each "
           "article's opening section is kept; footnotes, infoboxes and pictures are left out.")]

COLLECTION = K.Collection("sacred", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"sacred-texts": lambda: [f"sacred:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "sacred_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                        "a later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                        "2026-11-22). Pickthall's Quran (1930) entered the US public domain on 1 January 2026.",
    "sacred_web": "ebible.org/find/details.php?id=engwebp (checked at every build): \"The World English Bible is a "
                  "Public Domain translation of the Holy Bible into modern English\"; robots.txt allows the PDF.",
    "sacred_wikipedia": "en.wikipedia.org/wiki/Wikipedia:Copyrights (checked at every build): text under CC BY-SA 4.0; "
                        "robots.txt allows /wiki/ pages to ordinary readers and the builder is not an AI company's "
                        "reader (its /api/ is refused, so the pages themselves are read, one at a time).",
}
NOT_INCLUDED = [
    ("Modern copyrighted Bible translations (NIV, ESV, NRSV, NKJV, NASB, the Catholic NABRE, the JPS 1985 Tanakh)",
     "Copyright of their publishers; link-only. The public-domain KJV, ASV, WEB and JPS 1917 are built. Index: "
     "https://www.biblegateway.com/versions/ and https://www.sefaria.org/texts/Tanakh"),
    ("The Quran translated by Abdullah Yusuf Ali (1934), Sahih International, M. A. S. Abdel Haleem and other modern "
     "translations", "Yusuf Ali's 1934 translation was first published in Lahore; as a foreign work its US copyright "
     "was restored (95 years from publication: protected until the end of 2029). The modern ones are copyright. "
     "Link-only; Pickthall (1930) and Palmer (1880) are built. Index: https://quran.com/"),
    ("Modern translations of the Bhagavad Gita, the Upanishads, the Dhammapada, the Tao Te Ching and the Analects "
     "(Easwaran, Feng and English, Mitchell, Ames and Rosemont, Bhikkhu Bodhi and others)", "Copyright of their "
     "translators and publishers; link-only. Index: https://www.accesstoinsight.org/ (its own free-distribution "
     "terms, not checked as an open licence)"),
    ("A complete English Guru Granth Sahib (Sant Singh Khalsa, Manmohan Singh)", "No complete public-domain English "
     "translation exists; the modern ones are copyright. Macauliffe's six volumes (1909) are built (volume 4's scan "
     "with a text layer was not found). Index: https://www.srigranth.org/"),
    ("The Bahá'í Reference Library (bahai.org/library)", "Its texts are offered under the Bahá'í International "
     "Community's own terms of use, not an open licence; link-only. The 1908 Some Answered Questions is built. "
     "Index: https://www.bahai.org/library/"),
    ("sacred-texts.com (Internet Sacred Text Archive)", "Most of its texts are public domain, but the site claims "
     "copyright on its own editions and asks that they not be mirrored; the same old translations are read from the "
     "Internet Archive's scans instead. Index: https://sacred-texts.com/"),
    ("Project Gutenberg and Wikisource copies of these texts", "Already whole in the Kiwix library (Project Gutenberg "
     "and wikisource_en_all); gutenberg.org also answered this build machine \"503\" (2026-11-22). Index: "
     "https://www.gutenberg.org/ebooks/bookshelf/ and https://en.wikisource.org/wiki/Portal:Religion"),
    ("Pascal's Pensées and Seneca's Moral Letters", "The Internet Archive copies found were a modern Penguin edition "
     "wrongly dated, or no pre-1931 copy with a text layer; left out. Index: "
     "https://archive.org/search?query=pascal+pensees"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
