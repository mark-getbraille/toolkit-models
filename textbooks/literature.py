"""Literature and culture for the reference library, in the group "Reference, literature and culture" (the owner's
request of 2026-11-22). Keys: lit:<name>; request words, by genre (each well under 256 jobs):
  literature-novels     classic novels
  literature-stories    short stories
  literature-poetry     poetry
  literature-plays      plays
  literature-world      world literature and epics in public-domain English translations
  mythology-folklore    mythology, folklore and fairy tales (Greek, Norse, Celtic, African, Asian, Native American)
  literature-essays     essays, speeches, historic documents and history narratives
  literature-reference  art and music history, and literary reference (phrase and fable, the classical dictionary)
  literature            all of them, with the gathering index

What this module builds, in plain words: every book is an old public-domain book read IN FULL from its Internet
Archive scan, published before 1931 (the builder reads each item's own record at every build and refuses a later
reprint, so a book still in copyright in the US is never built). Works first published in 1925 to 1930 (The Great
Gatsby, Mrs Dalloway, A Farewell to Arms, The Sound and the Fury) entered the US public domain in 2021 to 2026. Each
book's description says what it is in a neutral line; myths and folk tales are presented respectfully, as the
collections tell them, and old books whose words or ideas are out of date or offensive today say so in their notice.

The gathering index (lit:index) is one small book made here, without downloading anything: for each genre, the books
of this collection with their keys, and where to find more in the libraries the toolkit already offers (Project
Gutenberg and Wikisource whole in the Kiwix library, the read-aloud fairy tales, the sacred and philosophical texts).

Already in the library and not repeated: Grimm, Andersen, Jacobs's English Fairy Tales and Lang's Blue Fairy Book
(readaloud:nursery_rhymes), the sacred texts and classic philosophy (sacred:), the Internet Archive's history books by
subject (open_catalogues.py's "history" topic), Project Gutenberg and Wikisource (Kiwix), and the writing kit's
LibriVox audiobooks (a separate collection).

Not built (NOT_INCLUDED): anything published in 1931 or later (copyright in the US), Project Gutenberg's site
(refuses programs at times; Kiwix holds it), Smarthistory and other art-history sites (non-commercial), and the
translations of the Shahnameh, the Masnavi, Gilgamesh and Hausa folklore for which no pre-1931 scan with a text layer
was found.

Run from the repository's folder:
  python3 textbooks/literature.py lit:index --out build/textbooks
  python3 textbooks/literature.py --list literature-poetry
"""

import datetime
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book, OLD_LICENCE, OLD_URL  # noqa: E402

GROUP = "literature"
GROUPS = {GROUP: "Reference, literature and culture"}

OLD_WORDS = ("Published in {year}. An old book: some of its words and ideas are of their time and may be out of date "
             "or offensive today.")

# (genre word, subject, [(name, title, author or translator and publisher, Internet Archive item, year, description,
# country)]). Each item is the most read copy with a text layer found with the Internet Archive's advanced search
# (2026-11-22); its year is checked again at every build.
NOVELS = [
    ("austen_pride_prejudice", "Pride and Prejudice (Jane Austen)", "Jane Austen (George Allen)", "prideprejudice00aust", 1894, "Elizabeth Bennet, Mr Darcy and the Bennet family.", "United Kingdom"),
    ("austen_emma", "Emma (Jane Austen)", "Jane Austen", "emmaausten00austrich", 1896, "Emma Woodhouse's matchmaking in the village of Highbury.", "United Kingdom"),
    ("austen_sense_sensibility", "Sense and Sensibility (Jane Austen)", "Jane Austen", "sensesensibility00austrich", 1896, "The Dashwood sisters, Elinor and Marianne.", "United Kingdom"),
    ("bronte_jane_eyre", "Jane Eyre (Charlotte Brontë)", "Charlotte Brontë", "janeeyre00broniala", 1899, "An orphan governess and Mr Rochester of Thornfield Hall.", "United Kingdom"),
    ("bronte_wuthering_heights", "Wuthering Heights (Emily Brontë)", "Emily Brontë (Thomas Cautley Newby)", "wutheringheights01bron", 1847, "Heathcliff and Catherine on the Yorkshire moors.", "United Kingdom"),
    ("dickens_great_expectations", "Great Expectations (Charles Dickens)", "Charles Dickens (J. M. Dent)", "greatexpectation0000dick_c1y6", 1907, "The orphan Pip and his unknown benefactor.", "United Kingdom"),
    ("dickens_tale_two_cities", "A Tale of Two Cities (Charles Dickens)", "Charles Dickens", "taleoftwocities00dickrich", 1906, "London and Paris in the French Revolution.", "United Kingdom"),
    ("dickens_oliver_twist", "Oliver Twist (Charles Dickens)", "Charles Dickens", "olivertwist01dick", 1861, "An orphan in the workhouse and the London underworld.", "United Kingdom"),
    ("dickens_david_copperfield", "David Copperfield (Charles Dickens)", "Charles Dickens", "davidcopperfield01dicke", 1850, "David Copperfield's life told by himself.", "United Kingdom"),
    ("dickens_christmas_carol", "A Christmas Carol (Charles Dickens)", "Charles Dickens", "christmascar00dick", 1915, "Ebenezer Scrooge and the three spirits.", "United Kingdom"),
    ("twain_huckleberry_finn", "Adventures of Huckleberry Finn (Mark Twain)", "Mark Twain (Charles L. Webster)", "adventureshuckle00twaiiala", 1885, "Huck and Jim on the Mississippi River.", "United States"),
    ("twain_tom_sawyer", "The Adventures of Tom Sawyer (Mark Twain)", "Mark Twain (American Publishing Company)", "adventuresoftoms00twaiiala", 1876, "A boyhood on the Mississippi.", "United States"),
    ("melville_moby_dick", "Moby-Dick; or, The Whale (Herman Melville)", "Herman Melville", "mobydickorwhale01melvuoft", 1922, "Captain Ahab's hunt for the white whale.", "United States"),
    ("hawthorne_scarlet_letter", "The Scarlet Letter (Nathaniel Hawthorne)", "Nathaniel Hawthorne", "scarletletter00hawt", 1878, "Hester Prynne in Puritan Boston.", "United States"),
    ("eliot_middlemarch", "Middlemarch (George Eliot)", "George Eliot", "middlemarchstudy12elio_0", 1908, "Life in a provincial English town.", "United Kingdom"),
    ("hardy_tess", "Tess of the d'Urbervilles (Thomas Hardy)", "Thomas Hardy (Modern Library)", "tessofdurbervill0000unse_k5d6", 1919, "A country girl's life in Wessex.", "United Kingdom"),
    ("tolstoy_war_and_peace", "War and Peace (Leo Tolstoy)", "Leo Tolstoy", "warpeace01tols_0", 1900, "Russian families in the Napoleonic wars.", "Russia"),
    ("tolstoy_anna_karenina", "Anna Karenina (Leo Tolstoy)", "Leo Tolstoy", "annakareninatols00tolsiala", 1899, "Anna Karenina and Russian society.", "Russia"),
    ("dostoevsky_crime_punishment", "Crime and Punishment (Fyodor Dostoevsky, Constance Garnett)", "Constance Garnett (Heinemann)", "crimepunishment00dostuoft", 1917, "Raskolnikov's crime and conscience.", "Russia"),
    ("dostoevsky_brothers_karamazov", "The Brothers Karamazov (Fyodor Dostoevsky)", "Fyodor Dostoevsky", "brotherskaramaz00dost", 1900, "A father, his sons and a murder.", "Russia"),
    ("hugo_les_miserables", "Les Misérables (Victor Hugo)", "Victor Hugo", "lesmiserablesnov01hugoiala", 1909, "Jean Valjean's life in nineteenth-century France.", "France"),
    ("dumas_monte_cristo", "The Count of Monte Cristo (Alexandre Dumas)", "Alexandre Dumas", "countofmontecris01duma", 1888, "Edmond Dantès's imprisonment, escape and revenge.", "France"),
    ("dumas_three_musketeers", "The Three Musketeers and Twenty Years After (Alexandre Dumas)", "Alexandre Dumas", "worksalexdumas02dumauoft", 1893, "D'Artagnan and the musketeers.", "France"),
    ("cervantes_don_quixote", "Don Quixote (Miguel de Cervantes)", "Miguel de Cervantes", "adventuresofdo00cerv", 1800, "The knight of La Mancha and Sancho Panza.", "Spain"),
    ("shelley_frankenstein", "Frankenstein (Mary Shelley, 1818 text)", "Mary Shelley", "Frankenstein1818Edition", 1818, "Victor Frankenstein and the creature he makes.", "United Kingdom"),
    ("stoker_dracula", "Dracula (Bram Stoker)", "Bram Stoker (Archibald Constable)", "draculabr00stokuoft", 1897, "Count Dracula, told in letters and diaries.", "United Kingdom"),
    ("stevenson_treasure_island", "Treasure Island (Robert Louis Stevenson)", "Robert Louis Stevenson", "islandtreasure00stevrich", 1883, "Jim Hawkins, Long John Silver and buried treasure.", "United Kingdom"),
    ("stevenson_jekyll_hyde", "Strange Case of Dr Jekyll and Mr Hyde (Robert Louis Stevenson)", "Robert Louis Stevenson", "strangecaseofdrj00stevrich", 1886, "A doctor and his other self.", "United Kingdom"),
    ("wells_time_machine", "The Time Machine (H. G. Wells)", "H. G. Wells", "timemachineinven00well", 1895, "A traveller to the far future.", "United Kingdom"),
    ("wells_war_of_the_worlds", "The War of the Worlds (H. G. Wells)", "H. G. Wells", "warofworlds00welluoft", 1898, "Martians invade England.", "United Kingdom"),
    ("verne_twenty_thousand_leagues", "Twenty Thousand Leagues under the Sea (Jules Verne)", "Jules Verne (Charles Scribner's Sons)", "twentythousandle0000vern_l0i3", 1925, "Captain Nemo and the Nautilus.", "France"),
    ("doyle_adventures_sherlock_holmes", "The Adventures of Sherlock Holmes (Arthur Conan Doyle)", "Arthur Conan Doyle", "adventuresofsher00doylrich", 1892, "Twelve cases of the detective and Dr Watson.", "United Kingdom"),
    ("alcott_little_women", "Little Women (Louisa May Alcott)", "Louisa May Alcott (J. M. Dent)", "littlewomen0000alco_t3z5", 1908, "The four March sisters growing up.", "United States"),
    ("carroll_alice", "Alice's Adventures in Wonderland (Lewis Carroll)", "Lewis Carroll", "AlicesAdventuresInWonderland", 1865, "Alice down the rabbit hole.", "United Kingdom"),
    ("fitzgerald_great_gatsby", "The Great Gatsby (F. Scott Fitzgerald, first edition, 1925)", "F. Scott Fitzgerald (Charles Scribner's Sons)", "the-great-gatsby-1st-ed-1925", 1925, "Jay Gatsby and Daisy Buchanan on Long Island.", "United States"),
    ("wharton_age_of_innocence", "The Age of Innocence (Edith Wharton)", "Edith Wharton (D. Appleton)", "ageofinnocence00wharuoft", 1920, "New York society in the 1870s.", "United States"),
    ("cather_my_antonia", "My Ántonia (Willa Cather)", "Willa Cather (Houghton Mifflin)", "myantonia00cathrich", 1918, "Immigrant life on the Nebraska prairie.", "United States"),
    ("london_call_of_the_wild", "The Call of the Wild (Jack London)", "Jack London", "callofthewild00lond", 1917, "Buck, a dog in the Klondike gold rush.", "United States"),
    ("conrad_heart_of_darkness", "Youth, Heart of Darkness, The End of the Tether (Joseph Conrad)", "Joseph Conrad", "YouthHeartOfDarknessTheEndOrTheTether", 1902, "Three tales, including Marlow's journey up the Congo.", "United Kingdom"),
    ("woolf_mrs_dalloway", "Mrs Dalloway (Virginia Woolf, 1925)", "Virginia Woolf", "mrsdalloway00wool", 1925, "One June day in London.", "United Kingdom"),
    ("joyce_ulysses", "Ulysses (James Joyce, 1922)", "James Joyce (Shakespeare and Company)", "ulysses00joyc_1", 1922, "One day in Dublin, 16 June 1904.", "France"),
    ("hemingway_farewell_to_arms", "A Farewell to Arms (Ernest Hemingway, 1929)", "Ernest Hemingway (Charles Scribner's Sons)", "farewelltoarms0000erne_r7q3", 1929, "An American ambulance driver in Italy in the First World War.", "United States"),
    ("faulkner_sound_fury", "The Sound and the Fury (William Faulkner, 1929), with As I Lay Dying", "William Faulkner (Modern Library)", "soundandthefurya013056mbp", 1929, "The Compson family of Mississippi. (As I Lay Dying, 1930, is in the same volume.)", "United States"),
]
STORIES = [
    ("poe_tales_mystery_imagination", "Tales of Mystery and Imagination (Edgar Allan Poe)", "Edgar Allan Poe", "talesofmysteryim01poee", 1923, "Poe's tales of terror and detection.", "United States"),
    ("ohenry_four_million", "The Four Million (O. Henry)", "O. Henry (McClure, Phillips)", "fourmillionstori00henr", 1906, "New York stories, including The Gift of the Magi.", "United States"),
    ("chekhov_tales_3", "The Tales of Chekhov, volume 3 (Constance Garnett)", "Constance Garnett (Chatto and Windus)", "talesofchekhov03chek", 1916, "Short stories of Anton Chekhov.", "Russia"),
    ("maupassant_short_stories", "The Complete Short Stories of Guy de Maupassant", "Guy de Maupassant", "completeshortsto1903maup", 1903, "Maupassant's short stories in ten volumes in one.", "France"),
    ("kipling_jungle_book", "The Jungle Book (Rudyard Kipling)", "Rudyard Kipling (Macmillan)", "junglebook00kipl2", 1894, "Mowgli and the animals of the Indian jungle.", "United Kingdom"),
    ("hawthorne_twice_told_tales", "Twice-Told Tales (Nathaniel Hawthorne)", "Nathaniel Hawthorne", "twicetoldtales00hawt", 1837, "Hawthorne's early tales and sketches.", "United States"),
    ("joyce_dubliners", "Dubliners (James Joyce)", "James Joyce (Grant Richards)", "dubliners00joycrich", 1914, "Fifteen stories of Dublin life.", "United Kingdom"),
]
POETRY = [
    ("whitman_leaves_of_grass", "Leaves of Grass (Walt Whitman)", "Walt Whitman", "leavesofgrassrhys00whitrich", 1886, "Whitman's poems, including Song of Myself.", "United States"),
    ("dickinson_poems", "Poems by Emily Dickinson", "Emily Dickinson (Roberts Brothers)", "poemsbyemilydick00dickrich", 1896, "The early editions of Emily Dickinson's poems.", "United States"),
    ("frost_north_of_boston", "North of Boston (Robert Frost)", "Robert Frost (Henry Holt)", "northofboston00frosrish", 1915, "Frost's New England poems, including Mending Wall.", "United States"),
    ("frost_new_hampshire", "New Hampshire (Robert Frost, 1923)", "Robert Frost (Henry Holt)", "NewHampshireRobertFrost1923", 1923, "Including Stopping by Woods on a Snowy Evening.", "United States"),
    ("keats_poetical_works", "The Complete Poetical Works of John Keats", "John Keats", "completepoetical01keat", 1900, "Keats's poems and odes.", "United Kingdom"),
    ("shelley_poetical_works", "The Complete Poetical Works of Percy Bysshe Shelley", "Percy Bysshe Shelley", "completepoeticalshel", 1914, "Shelley's poems.", "United Kingdom"),
    ("coleridge_poetical_works", "The Complete Poetical Works of Samuel Taylor Coleridge", "Samuel Taylor Coleridge (Clarendon Press)", "cu31924102776576", 1912, "Coleridge's poems, including The Rime of the Ancient Mariner.", "United Kingdom"),
    ("tennyson_poetical_works", "The Complete Poetical Works of Tennyson", "Alfred, Lord Tennyson", "completepoetical00tenn", 1898, "Tennyson's poems.", "United Kingdom"),
    ("longfellow_poetical_works", "The Complete Poetical Works of Henry Wadsworth Longfellow", "Henry Wadsworth Longfellow (Houghton Mifflin)", "completepoeti00long", 1893, "Longfellow's poems, including Hiawatha and Evangeline.", "United States"),
    ("burns_poetical_works", "The Complete Poetical Works of Robert Burns", "Robert Burns", "burnsworks00burnrich", 1872, "Burns's poems and songs in Scots and English.", "United Kingdom"),
    ("blake_poetical_works", "The Poetical Works of William Blake", "William Blake (Clarendon Press)", "poeticalworksofw00blakuoft", 1905, "Blake's poems, including Songs of Innocence and of Experience.", "United Kingdom"),
    ("yeats_wind_among_the_reeds", "The Wind Among the Reeds (W. B. Yeats)", "W. B. Yeats", "wind00yeatamongreedsrich", 1903, "Yeats's early poems.", "Ireland"),
    ("eliot_waste_land", "The Waste Land (T. S. Eliot, 1922)", "T. S. Eliot (Boni and Liveright)", "wasteland01elio", 1922, "Eliot's long poem.", "United States"),
    ("dunbar_complete_poems", "The Complete Poems of Paul Laurence Dunbar", "Paul Laurence Dunbar (Dodd, Mead)", "completepoemsofp00dunbrich", 1913, "Dunbar's poems in standard English and dialect.", "United States"),
    ("palgrave_golden_treasury", "The Golden Treasury (Francis Turner Palgrave)", "Francis Turner Palgrave", "goldentreasuryo00palg", 1916, "An anthology of the best songs and lyric poems in English.", "United Kingdom"),
    ("oxford_book_english_verse", "The Oxford Book of English Verse, 1250-1900", "Arthur Quiller-Couch (Clarendon Press)", "cu31924011997909", 1912, "An anthology of English poetry from the Middle Ages to 1900.", "United Kingdom"),
    ("milton_paradise_lost", "Paradise Lost (John Milton)", "John Milton", "miltonsparadisel00miltuoft", 1860, "Milton's epic of the Fall.", "United Kingdom"),
    ("chaucer_canterbury_tales", "The Canterbury Tales (Geoffrey Chaucer)", "Geoffrey Chaucer", "canterburytaleso00chauuoft", 1914, "The pilgrims' tales on the road to Canterbury.", "United Kingdom"),
]
PLAYS = [
    ("shakespeare_complete_works", "The Complete Works of William Shakespeare", "William Shakespeare", "completeworksofw00shakrich", 1900, "Shakespeare's plays and poems.", "United Kingdom"),
    ("ibsen_dolls_house", "A Doll's House (Henrik Ibsen)", "Henrik Ibsen", "dollshouseplayin00ibseuoft", 1900, "Nora Helmer's marriage.", "Norway"),
    ("chekhov_seagull_cherry_orchard", "Two Plays by Tchekhof: The Seagull, The Cherry Orchard", "Anton Chekhov (Charles Scribner's Sons)", "twoplaysbytchekh00chekiala", 1912, "Two of Chekhov's plays.", "Russia"),
    ("shaw_pygmalion", "Pygmalion (Bernard Shaw)", "Bernard Shaw", "pygmalionplayinf00shawrich", 1914, "Professor Higgins and Eliza Doolittle.", "United Kingdom"),
    ("wilde_importance_of_being_earnest", "The Importance of Being Earnest (Oscar Wilde)", "Oscar Wilde", "importanceofbein1920wild", 1920, "Wilde's comedy of manners.", "United Kingdom"),
    ("sophocles_seven_plays", "Sophocles: the text of the seven plays (R. C. Jebb)", "R. C. Jebb (Cambridge University Press)", "sophoclestextof00sophiala", 1906, "The seven surviving plays of Sophocles, including Oedipus the King and Antigone.", "United Kingdom"),
    ("aeschylus_oresteia", "The Oresteia of Aeschylus", "Aeschylus", "oresteiaofaeschy00aesciala", 1900, "Agamemnon, The Libation Bearers and The Eumenides.", "United Kingdom"),
    ("euripides_bacchae", "The Bacchae of Euripides (Gilbert Murray)", "Gilbert Murray (George Allen)", "bacchaeofeuripid015559mbp", 1920, "Euripides's tragedy of Dionysus at Thebes.", "United Kingdom"),
    ("moliere_dramatic_works", "The Dramatic Works of Molière (Henri Van Laun)", "Henri Van Laun", "dramaticworksofm02moliiala", 1800, "Molière's comedies in English.", "France"),
    ("marlowe_works", "The Works of Christopher Marlowe", "Christopher Marlowe", "worksmarlowe02bulluoft", 1885, "Marlowe's plays, including Doctor Faustus.", "United Kingdom"),
    ("oneill_emperor_jones", "The Emperor Jones (Eugene O'Neill)", "Eugene O'Neill (Stewart Kidd)", "emperorjones00onei", 1921, "O'Neill's expressionist play.", "United States"),
    ("goethe_faust", "Faust, parts I and II (Goethe)", "Johann Wolfgang von Goethe", "faustpartsiii00goetuoft", 1908, "Faust's bargain with Mephistopheles.", "Germany"),
]
WORLD = [
    ("homer_iliad_pope", "The Iliad of Homer (Alexander Pope)", "Alexander Pope", "iliadofhomertran00homeuoft", 1909, "The war at Troy and the wrath of Achilles.", "Greece"),
    ("homer_odyssey_palmer", "The Odyssey of Homer (George Herbert Palmer)", "George Herbert Palmer (Houghton Mifflin)", "odysseyofhomertr01homeuoft", 1894, "Odysseus's journey home from Troy.", "Greece"),
    ("virgil_dryden", "The Works of Virgil: Pastorals, Georgics and Aeneid (John Dryden)", "John Dryden", "workscontainingh00virguoft", 1780, "Virgil's poems, including the Aeneid.", "Italy"),
    ("dante_divine_comedy_longfellow", "The Divine Comedy of Dante Alighieri (Henry Wadsworth Longfellow)", "Henry Wadsworth Longfellow", "divinecomedyofda00dantiala", 1867, "Dante's journey through Hell, Purgatory and Paradise.", "Italy"),
    ("arabian_nights_lang", "The Arabian Nights Entertainments (Andrew Lang)", "Andrew Lang (Longmans, Green)", "arabiannightsent00lang", 1898, "Tales of the Thousand and One Nights.", "United Kingdom"),
    ("beowulf_gummere", "The Oldest English Epic: Beowulf and other poems (Francis B. Gummere)", "Francis B. Gummere (Macmillan)", "oldestenglishepi00gummuoft", 1922, "Beowulf, Finnsburg, Waldere, Deor, Widsith and the Hildebrand lay.", "United States"),
    ("kalevala_crawford", "The Kalevala, the epic poem of Finland (John Martin Crawford)", "John Martin Crawford", "kalevalaepicpoem01crawuoft", 1904, "The Finnish national epic.", "Finland"),
    ("mahabharata_dutt", "Mahabharata: the epic of ancient India (Romesh C. Dutt)", "Romesh C. Dutt (J. M. Dent)", "cu31924023015542", 1899, "The Mahabharata condensed into English verse.", "India"),
    ("song_of_roland", "The Song of Roland (Leonard Bacon)", "Leonard Bacon (Yale University Press)", "songofrolandtran00bacouoft", 1914, "The French epic of Roland at Roncevaux.", "France"),
    ("nibelungenlied", "The Lay of the Nibelungs (Alice Horton)", "Alice Horton (George Bell)", "nibelungslay00hortrich", 1901, "The German epic of Siegfried and Kriemhild.", "Germany"),
    ("omar_khayyam_rubaiyat", "Rubaiyat of Omar Khayyam (Edward FitzGerald)", "Edward FitzGerald", "rubaiyatfitzgera00omar", 1905, "FitzGerald's English version of the Persian quatrains.", "Iran"),
    ("tagore_gitanjali", "Gitanjali: Song Offerings (Rabindranath Tagore)", "Rabindranath Tagore (Macmillan)", "gitanjalisongoff00tagouoft", 1913, "Tagore's own prose translations of his Bengali poems.", "India"),
    ("li_po_obata", "The Works of Li Po, the Chinese Poet (Shigeyoshi Obata)", "Shigeyoshi Obata (E. P. Dutton)", "worksoflipochine00libauoft", 1923, "Poems of Li Bai in English verse.", "China"),
    ("genji_wreath_of_cloud", "A Wreath of Cloud: the third part of The Tale of Genji (Arthur Waley, 1927)", "Arthur Waley (George Allen and Unwin)", "AWreathOfCloud", 1927, "Part of Murasaki Shikibu's Tale of Genji.", "Japan"),
]
MYTH = [
    ("bulfinch_mythology", "Bulfinch's Mythology: The Age of Fable, The Age of Chivalry, Legends of Charlemagne", "Thomas Bulfinch", "bulfinchsmytholo1913bulf", 1913, "Greek, Roman and Norse myths and the legends of King Arthur and Charlemagne.", "United States"),
    ("gayley_classic_myths", "The Classic Myths in English Literature (Charles Mills Gayley)", "Charles Mills Gayley (Ginn)", "theclassicmythsi00gayluoft", 1894, "The Greek and Roman myths and where English poets use them.", "United States"),
    ("colum_children_of_odin", "The Children of Odin (Padraic Colum)", "Padraic Colum (Macmillan)", "cu31924058637574", 1920, "The Norse myths retold.", "United States"),
    ("bellows_poetic_edda", "The Poetic Edda (Henry Adams Bellows)", "Henry Adams Bellows (American-Scandinavian Foundation)", "poeticedda00belluoft", 1923, "The Old Norse poems of the gods and heroes.", "United States"),
    ("brodeur_prose_edda", "The Prose Edda (Arthur Gilchrist Brodeur)", "Arthur Gilchrist Brodeur (American-Scandinavian Foundation)", "proseedda00snor", 1916, "Snorri Sturluson's book of Norse mythology.", "United States"),
    ("gregory_gods_fighting_men", "Gods and Fighting Men (Lady Gregory)", "Lady Gregory (John Murray)", "godsfightingmens00gregrich", 1904, "The Irish stories of the Tuatha Dé Danann and the Fianna.", "Ireland"),
    ("gregory_cuchulain", "Cuchulain of Muirthemne (Lady Gregory)", "Lady Gregory (John Murray)", "ofmuirtcuchulain00gregrich", 1911, "The Ulster cycle of Cú Chulainn.", "Ireland"),
    ("jacobs_celtic_fairy_tales", "Celtic Fairy Tales (Joseph Jacobs)", "Joseph Jacobs (David Nutt)", "celticfairytale00jacorich", 1892, "Irish, Scottish, Welsh and Cornish folk tales.", "United Kingdom"),
    ("guest_mabinogion", "The Mabinogion (Lady Charlotte Guest)", "Lady Charlotte Guest", "TheMabinogionGuest1877", 1910, "The medieval Welsh tales.", "United Kingdom"),
    ("dayrell_southern_nigeria", "Folk Stories from Southern Nigeria (Elphinstone Dayrell)", "Elphinstone Dayrell (Longmans, Green)", "folkstoriesfroms00dayrrich", 1910, "Efik and Ibibio folk stories as collected in 1910.", "Nigeria"),
    ("ozaki_japanese_fairy_tales", "Japanese Fairy Tales (Yei Theodora Ozaki)", "Yei Theodora Ozaki (A. L. Burt)", "japanesefairytal00ozak", 1903, "Momotaro, Urashima Taro and other Japanese tales.", "Japan"),
    ("jacobs_indian_fairy_tales", "Indian Fairy Tales (Joseph Jacobs)", "Joseph Jacobs (David Nutt)", "indiantales00jacorich", 1892, "Folk tales of India.", "United Kingdom"),
    ("mclaughlin_sioux", "Myths and Legends of the Sioux (Marie L. McLaughlin)", "Marie L. McLaughlin (Bismarck Tribune)", "mythslegsioux00mclarich", 1916, "Lakota and Dakota stories told by a writer of Dakota descent.", "United States"),
    ("linderman_indian_why_stories", "Indian Why Stories (Frank B. Linderman)", "Frank B. Linderman (Charles Scribner's Sons)", "indianwhystories00lind", 1915, "Blackfeet, Chippewa and Cree stories as told to Linderman.", "United States"),
    ("cushing_zuni_folk_tales", "Zuñi Folk Tales (Frank Hamilton Cushing)", "Frank Hamilton Cushing (G. P. Putnam's Sons)", "zuifolktales00cushrich", 1901, "Zuni stories as recorded by Cushing.", "United States"),
    ("aesop_caxton", "The Fables of Aesop (Joseph Jacobs, from Caxton's 1484 printing)", "Joseph Jacobs (David Nutt)", "fablesofaesopasf01aesouoft", 1889, "Aesop's fables.", "United Kingdom"),
    ("lang_red_fairy_book", "The Red Fairy Book (Andrew Lang)", "Andrew Lang (Longmans, Green)", "redfairybook00langiala", 1890, "Fairy tales from many countries.", "United Kingdom"),
    ("lang_green_fairy_book", "The Green Fairy Book (Andrew Lang)", "Andrew Lang (Longmans, Green)", "greenfairybook00lang", 1906, "Fairy tales from many countries.", "United Kingdom"),
    ("lang_yellow_fairy_book", "The Yellow Fairy Book (Andrew Lang)", "Andrew Lang (Longmans, Green)", "yellowfairybook00lang02", 1906, "Fairy tales from many countries.", "United Kingdom"),
    ("perrault_fairy_tales", "The Fairy Tales of Charles Perrault", "Charles Perrault", "fairytalesofchar00perr", 1922, "Cinderella, Puss in Boots, Sleeping Beauty and the other tales.", "France"),
]
ESSAYS = [
    ("emerson_essays", "Emerson's Essays", "Ralph Waldo Emerson", "emersonselected00emerrich", 1920, "Self-Reliance, Nature and other essays.", "United States"),
    ("thoreau_walden", "Walden; or, Life in the Woods (Henry David Thoreau)", "Henry David Thoreau", "cu31924021445741", 1899, "Two years in a cabin by Walden Pond.", "United States"),
    ("montaigne_works", "The Works of Michel de Montaigne: Essays, Journey into Italy, Letters", "Michel de Montaigne", "workscomprising01montuoft", 1864, "Montaigne's essays in English.", "France"),
    ("bacon_essays", "The Essays of Francis Bacon", "Francis Bacon", "baconsadvancemen00bacouoft", 1883, "Bacon's essays, counsels civil and moral.", "United Kingdom"),
    ("lincoln_speeches_letters", "Speeches and Letters of Abraham Lincoln, 1832-1865", "Abraham Lincoln (J. M. Dent)", "speechesletterso00linciala", 1907, "Lincoln's speeches, including the Gettysburg Address and the inaugural addresses.", "United States"),
    ("douglass_narrative", "Narrative of the Life of Frederick Douglass, an American Slave", "Frederick Douglass", "douglasfred00dougrich", 1847, "Douglass's own account of his life in slavery and escape.", "United States"),
    ("federalist", "The Federalist on the New Constitution (Hamilton, Madison and Jay)", "Alexander Hamilton, James Madison and John Jay", "federalistoncon00hami", 1831, "The Federalist Papers.", "United States"),
    ("paine_common_sense", "Common Sense (Thomas Paine)", "Thomas Paine", "commonsense00painrich", 1920, "Paine's 1776 case for American independence.", "United States"),
    ("washington_up_from_slavery", "Up from Slavery (Booker T. Washington)", "Booker T. Washington (Doubleday, Page)", "upfromslaveryaut00washuoft", 1901, "Washington's autobiography.", "United States"),
    ("dubois_souls_of_black_folk", "The Souls of Black Folk (W. E. B. Du Bois)", "W. E. B. Du Bois (A. C. McClurg)", "cu31924024920492", 1903, "Du Bois's essays and sketches.", "United States"),
    ("gibbon_decline_fall", "The History of the Decline and Fall of the Roman Empire (Edward Gibbon), with his autobiography", "Edward Gibbon", "TheDeclineTheFallOfTheRomanEmpireVindicationAutobiiography", 1925, "Gibbon's history of Rome's decline.", "United Kingdom"),
    ("herodotus_history_1", "The History of Herodotus, volume 1 (George Rawlinson)", "George Rawlinson (J. M. Dent)", "herodotus00herouoft", 1910, "The Greek historian's account of the Persian Wars.", "Greece"),
    ("thucydides_jowett", "Thucydides (Benjamin Jowett)", "Benjamin Jowett (Clarendon Press)", "a609583001thucuoft", 1881, "The history of the Peloponnesian War.", "Greece"),
    ("plutarch_lives_1", "Plutarch's Lives, volume 1 (Bernadotte Perrin)", "Bernadotte Perrin (Loeb Classical Library)", "plutarchslives01plut2", 1914, "Plutarch's paired lives of Greeks and Romans.", "Greece"),
    ("parkman_oregon_trail", "The Oregon Trail (Francis Parkman)", "Francis Parkman (Little, Brown)", "oregontrailsketc07park", 1892, "Parkman's 1846 journey on the prairies and in the Rocky Mountains.", "United States"),
    ("prescott_conquest_mexico", "History of the Conquest of Mexico (William H. Prescott)", "William H. Prescott", "conquestofmexico01presrich", 1873, "The Spanish conquest of the Aztec empire, from the sources of its time.", "United States"),
    ("wells_outline_of_history", "The Outline of History (H. G. Wells)", "H. G. Wells (Macmillan)", "outlineofhistory00wellrich", 1921, "A history of life and mankind from the beginning to 1920.", "United Kingdom"),
]
REFERENCE = [
    ("reinach_apollo_history_of_art", "Apollo: an illustrated manual of the history of art throughout the ages (Salomon Reinach)", "Salomon Reinach (Charles Scribner's Sons)", "apolloillustrate00rein", 1910, "A short history of art from prehistory to the nineteenth century; pictures are described by their captions only.", "France"),
    ("stanford_forsyth_history_of_music", "A History of Music (Charles Villiers Stanford and Cecil Forsyth)", "Stanford and Forsyth (Macmillan)", "cu31924022441871", 1920, "Western music from ancient times to the early twentieth century.", "United Kingdom"),
    ("krehbiel_how_to_listen", "How to Listen to Music (Henry Edward Krehbiel)", "Henry Edward Krehbiel (Charles Scribner's Sons)", "howtolistentomus00krehuoft", 1912, "A guide to listening: the orchestra, musical forms and what to listen for.", "United States"),
    ("brewer_phrase_and_fable", "Dictionary of Phrase and Fable (E. Cobham Brewer)", "E. Cobham Brewer (Cassell)", "dictionaryofphra02brew", 1895, "The origins of phrases, allusions and words with a tale to tell.", "United Kingdom"),
    ("smith_classical_dictionary", "A New Classical Dictionary of Greek and Roman Biography, Mythology and Geography (Charles Anthon, after William Smith)", "Charles Anthon (Harper)", "newclassicaldict00anthiala", 1860, "Who was who in Greek and Roman history and myth.", "United States"),
]

GENRES = [
    ("literature-novels", "Classic novels", NOVELS),
    ("literature-stories", "Short stories", STORIES),
    ("literature-poetry", "Poetry", POETRY),
    ("literature-plays", "Plays", PLAYS),
    ("literature-world", "World literature and epics", WORLD),
    ("mythology-folklore", "Mythology, folklore and fairy tales", MYTH),
    ("literature-essays", "Essays, speeches and history", ESSAYS),
    ("literature-reference", "Art and music history and literary reference", REFERENCE),
]

PDFS = []
for _word, _subject, _rows in GENRES:
    for _name, _title, _by, _archive, _year, _desc, _country in _rows:
        PDFS.append(old_book(GROUP, _name, _title, f"Literature: {_subject}", _by, _archive, _year, _desc,
                             note=OLD_WORDS, country=_country))


# ====================================================================== the gathering index (made here)

ELSEWHERE = [
    ("Project Gutenberg (Kiwix library)", "Tens of thousands of public-domain books: open the Project Gutenberg "
     "library in the Offline libraries window and search by author or title."),
    ("Wikisource (Kiwix library: wikisource_en_all)", "Public-domain texts transcribed and checked by volunteers: "
     "poems, speeches, historic documents, plays and translations."),
    ("Read-aloud fairy tales (readaloud:nursery_rhymes)", "Grimm, Andersen, Jacobs's English Fairy Tales, Lang's Blue "
     "Fairy Book and Mother Goose."),
    ("Sacred and philosophical texts (sacred-texts)", "The Bible, the Tanakh, the Quran, the Bhagavad Gita, the "
     "Buddhist and Chinese classics and classic philosophy."),
    ("History books by subject (the Internet Archive's history topic)", "Old public-domain books on United States and "
     "world history."),
]


def index_book(name, work, cache=None, left_out=None, limit=None):
    """The gathering index: one page per genre listing this collection's books (title, year and key), and a page of
    where to find more; made from this module's own lists, nothing downloaded."""
    import build_textbooks as B
    book = K.new_book("lit_index", "Literature and culture: the gathering index", "Literature: index", GROUP,
                      "Digital Accessibility Toolkit (GetBraille.com)", "CC0 1.0",
                      "https://creativecommons.org/publicdomain/zero/1.0/", "https://archive.org/",
                      "A guide to the literature and culture books: every book of this collection by genre with its "
                      "year, and where to find more in the libraries the toolkit already offers.",
                      "Made from the collection's own list (facts and titles only), CC0.")
    for chapter, (word, subject, rows) in enumerate(GENRES, 1):
        items = "".join(f"<li>{html.escape(title)}, {year} (key lit:{n})</li>"
                        for n, title, _by, _a, year, _d, _c in rows)
        body = f"<p>{len(rows)} books; ask for them all with the request word {word}.</p><ul>{items}</ul>"
        book.pages.append(B.Page(f"{chapter:02d}-{B.slug(subject)}", subject, body, chapter, "Books by genre"))
    more = "".join(f"<li><strong>{html.escape(t)}</strong>: {html.escape(d)}</li>" for t, d in ELSEWHERE)
    book.pages.append(B.Page("99-more", "Where to find more", f"<ul>{more}</ul>", len(GENRES) + 1, "More"))
    book.published = datetime.date.today().isoformat()
    book.version = f"index of {len(PDFS)} books, made {book.published}"
    return book


COLLECTION = K.Collection(
    "lit", GROUP, pdfs=PDFS, makers={"index": (index_book, lambda name: K.sha([p["name"] for p in PDFS]))},
    words=dict({w: (lambda rows=rows: [f"lit:{r[0]}" for r in rows]) for w, _s, rows in GENRES},
               literature=lambda: ["lit:index"] + [f"lit:{p['name']}" for p in PDFS]))

LICENCE_LINES = {
    "literature_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, "
                            "so a later reprint is refused); archive.org's robots.txt allows the files; no AI rules "
                            "(checked 2026-11-22). The index is the toolkit's own list of facts, CC0.",
}
NOT_INCLUDED = [
    ("Books first published in 1931 or later (Steinbeck, Orwell, later Hemingway, Faulkner and Woolf, Langston "
     "Hughes's later poems, Achebe and others)", "In copyright in the US; link-only. Works of 1930 entered the public "
     "domain on 1 January 2026, those of 1931 follow on 1 January 2027. Index: "
     "https://www.copyright.gov/help/faq/faq-duration.html"),
    ("Langston Hughes's The Weary Blues (1926)", "Public domain in the US since 2022, but no Internet Archive scan "
     "dated before 1931 with a text layer was found (2026-11-22). Index: https://archive.org/search?query=weary+blues"),
    ("The Shahnameh (Warner), the Masnavi (Nicholson, Whinfield), Gilgamesh (Thompson, 1928), Rattray's Hausa "
     "Folk-Lore, a Ramayana and Waley's first Genji volume", "No pre-1931 Internet Archive copy with a text layer was "
     "found (2026-11-22); some are in the Kiwix library's Project Gutenberg. Index: "
     "https://archive.org/search?query=shahnama"),
    ("Project Gutenberg and Wikisource", "Already whole in the Kiwix library; gutenberg.org answered this build "
     "machine \"503\" (2026-11-22). Index: https://www.gutenberg.org/ and https://en.wikisource.org/"),
    ("Smarthistory, Khan Academy art history and other art and music history sites", "CC BY-NC-SA (non-commercial) "
     "or the site's own terms; link-only. Index: https://smarthistory.org/"),
    ("Bartlett's Familiar Quotations", "The pre-1931 Internet Archive copies found have no text layer (Google scans "
     "without words); left out. Index: https://archive.org/search?query=bartlett+familiar+quotations"),
    ("Author portraits, theatre and folk art pictures", "Not made into a picture pack: the art packs already read the "
     "museums' open collections (the Met, Cleveland, Smithsonian, Art Institute), and a pack that names real people "
     "from their faces would identify people, which the picture describer does not do. Index: "
     "https://commons.wikimedia.org/wiki/Category:Portraits_of_writers"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
