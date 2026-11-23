"""Learning music for the reference library: music theory, learning to play, braille music and music history (the
owner's request of 2026-11-23), in its own group "Reference, music: theory, playing and history". Keys:
musiclearn:<name> (the prefix "music:" already belongs to the sheet music collection, sheet_music.py). Request words
(each well under 256 jobs):
  music-theory           the two open music theory textbooks and the old theory, harmony and form books
  music-methods          old method books for piano, voice, guitar, harmonica, ukulele, accordion, violin,
                         banjo, saxophone, clarinet and flute, drums and fife, and the US Army's band manuals
  music-braille-history  old braille music guides, music histories and appreciation courses
  music-learning         every book of this module, with the index

What this module builds, in plain words, each IN FULL:
  - two openly licensed music theory textbooks, every page, each kept apart under its own share-alike licence:
      Open Music Theory (the first edition, openmusictheory.github.io, Gotham, Brown, Shaffer and Wells, Hybrid
      Pedagogy Publishing, CC BY-SA 4.0) and Music Theory for the 21st-Century Classroom (Robert Hutchinson, GNU Free
      Documentation License 1.2 or later; its own colophon says so, so it is not the "no licence" the games module
      noted earlier);
  - old public-domain books from the Internet Archive (published before 1931; the builder reads each item's own
    record at every build and refuses a later one), each marked as an old book:
      theory: Jadassohn's Manual of Harmony, Stainer's Harmony, Prout's Counterpoint, Fugue and Musical Form,
      Goetschius's Tone-Relations, Lessons in Music Form and Elementary Counterpoint, Elson's Theory of Music and his
      Music Dictionary (1905), Ham's Rudiments of Music and Simpson's 400 Questions on the Rudiments;
      learning to play: Hofmann's Piano Playing, Cooke's Great Pianists on Piano Playing, Burrowes' Piano Primer,
      Czerny's Pianoforte School (volume 1), Lilli Lehmann's How to Sing, Shakespeare's The Art of Singing, Caruso and
      the Art of Singing, Guilbert's How to Sing a Song, Carcassi's guitar method, harmonica courses (Cole 1926,
      Minevitch 1923), ukulele methods (Kamiki 1921, Guckert's chords 1917, Peterson 1924), Jewett's accordion
      teacher (1850), Auer's Violin Playing as I Teach It, Martens's Violin Mastery, Schroeder's Handbook of Violin
      Playing, Foden's Home Study Lessons for Banjo, Converse's Analytical Banjo Method, de Ville's
      Universal Method for the Saxophone, Klosé's clarinet method, Soussmann's flute method, Strube's Drum and Fife
      Instructor (1870, the US Army's own drum book), Nevins's Army Regulations for Drum, Fife and Bugle (1864) and
      McGeary's Yankee Doodle Method (1920);
      braille music: the Key to the Braille Music Notation of 1922 (1925), Robyn's Thorough Description of the
      Braille System for the Reading and Writing of Music (1867) and Watson's Braille Music and Its Problems (1925);
      history and appreciation: Pratt's History of Music, Hamilton's Outlines of Music History and his Music
      Appreciation, Elson's History of American Music, Arthur Elson's Book of Musical Knowledge, Faulkner's What We
      Hear in Music and Baltzell's Dictionary of Musicians;
  - the US Army's band manuals from the Internet Archive (works of the US government; the builder reads each one's
    front pages and follows the shared distribution rule): FM 12-50 The Band (1946), The Marching Band (1957) and
    The Military Band (1969);
  - musiclearn:index, "Learning music: a guide to the library" (facts and links, CC0): every music book here and
    elsewhere in the library by key (sheet music, instrument care, the old instrument and band books, the music
    histories in literature, radio and audio books), the textbook catalogues that hold more music theory, and the
    link-only sources with the reason.
  Every method and theory book says plainly that its music examples and exercises are printed notation, pictures the
  scanner cannot read: only the words are in the book, so the books were chosen for their explanations. The braille
  music books say their code is out of date (the current code is the Music Braille Code 2015, BANA).

Already in the library and not repeated: Prout's Harmony and Goetschius's Exercises in Melody-Writing (games:),
Stanford and Forsyth's History of Music and Krehbiel's How to Listen to Music (lit:), the old guitar, banjo and band
books (olife:), Braille Music Notation 1930 (pdf:braille_music_notation_1930), Louis Braille's 1829 book with music
(lopen:braille_procede_1829), Krolick's Dictionary of Braille Music Signs (blind:nls_dictionary_braille_music_signs_1979),
the NLS braille music catalogues (music:nls_braille_music), piano tuning and violin making
(instr:, olife:), and the textbook catalogues (LibreTexts, the Open Textbook Library) with their music theory books.

Not built (NOT_INCLUDED, link-only): the Music Braille Code 2015 (BANA copyright), De Garmo's Introduction to Braille
Music Transcription (1970: published by the Library of Congress, but it quotes copyrighted music by permission), Open
Music Theory's second edition (its Pressbooks host refuses programs), and the Library of Congress music division's
research guides (loc.gov's guides pages are not a government work in full: they quote other owners' material).

Licences: Open Music Theory's footer "CC BY-SA 4.0" and Music Theory for the 21st-Century Classroom's colophon "GNU Free
Documentation License, Version 1.2 or any later version" are checked at every build; the old books by the pre-1931
year check; the Army manuals are works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page).

Run from the repository's folder:
  python3 textbooks/music_learning.py musiclearn:index --out build/textbooks
  python3 textbooks/music_learning.py musiclearn:hofmann_piano_playing_1920 --out build/textbooks --limit 3
  python3 textbooks/music_learning.py --list music-learning
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

PREFIX = "musiclearn"
GROUP = "musiclearn"
GROUPS = {GROUP: "Reference, music: theory, playing and history"}

# The note every theory and method book carries: its music is printed notation, which the scanner cannot read.
NOTATION = ("Its music examples and exercises are printed notation (pictures): only the words around them are read "
            "into this book, so play or transcribe from a score, not from this text.")
OLD = "Published in {year}: an old book; some of its terms and teaching habits are of its time."
BRAILLE_OLD = ("Published in {year}: an old book, OUT OF DATE as a braille code: braille music signs have been revised "
               "since (the current code in the US and Canada is the Music Braille Code 2015, BANA), so check every "
               "sign against the current code. Its braille examples may be pictures the scanner cannot read.")
HISTORY_OLD = ("Published in {year}: an old book; its history stops at its own date and some of its judgements of "
               "composers and of music outside Europe are of its time.")


def book(name, title, subject, publisher, archive, year, description, note=OLD, notation=True,
         country="United States"):
    """One old music book of the Internet Archive (published before 1931); notation=True adds the note that its
    music examples are printed notation."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=NOTATION if notation else "", country=country)


# ====================================================================== open music theory textbooks (share-alike)

OMT = "https://openmusictheory.github.io/"
MT21C = "https://musictheory.pugetsound.edu/mt21c/"
GUIDES = [
    dict(K.WEB, group=GROUP, name="open_music_theory", title="Open Music Theory (first edition, CC BY-SA)",
         subject="Music theory", publisher="Kris Shaffer, Bryn Hughes, Brian Moseley and Robin Wharton (Hybrid "
         "Pedagogy Publishing)", country="International", licence="CC BY-SA 4.0",
         licence_url="https://creativecommons.org/licenses/by-sa/4.0/", licence_page=OMT + "contents.html",
         licence_text=r"CC BY.{1,3}SA 4\.0", source=OMT + "contents.html", crawl=[(OMT + "contents.html", 1)],
         pages=r"^https://openmusictheory\.github\.io/[A-Za-z0-9_-]+\.html$",
         content=(r'<article class="wrap post">', r"</article>"), limit=160,
         title_from=r"<title>\s*(.*?)\s*(?:&#8211;|–) Open Music Theory\s*</title>",
         unit_rules=[(r"/(basicNotation|beams|clefs|pitch|intervals|triads|seventh|keySig|scales|meter|rhythm|"
                      r"[a-z]*[Nn]otation)", "Fundamentals"),
                     (r"/(firstSpecies|secondSpecies|thirdSpecies|fourthSpecies|cantusFirmus|species)", "Counterpoint"),
                     (r"/(SATB|voiceLeading|harmonicFunctions|cadence|embellishing|predominant|appliedChords|"
                      r"Modulation|mixture|neapolitan|augmentedSixth|alteredSubdominants|RNfromFB|bassoContinuo)",
                      "Harmony and voice leading"),
                     (r"/(phrase|period|sentence|compound|classical|SonataTheory|rondo|fivePartRondo|sevenPart|"
                      r"binary|ternary|externalExpansions|KBVL)", "Form"),
                     (r"/(atonal|set|complements|commonTones|twelveTone|serial|row)", "Post-tonal theory"),
                     (r".", "Other chapters")],
         description="The first edition of Open Music Theory, an open college music theory textbook, every page: "
                     "notation and fundamentals (pitch, rhythm, meter, intervals, scales, keys, triads and seventh "
                     "chords), species counterpoint, harmony and voice leading (cadences, embellishing tones, applied "
                     "chords, modulation, mixture, augmented sixth chords, figured bass), form (phrases, periods, "
                     "sentences, sonata and rondo forms) and post-tonal theory (set classes, twelve-tone rows). "
                     + NOTATION,
         notice="Open Music Theory, by Kris Shaffer, Bryn Hughes, Brian Moseley and Robin Wharton (and its "
                "contributors), (c) Hybrid Pedagogy Publishing, licensed CC BY-SA 4.0: share-alike, so anything made "
                "from it keeps the same licence; kept apart from the public-domain books. Its interactive examples "
                "and pictures of notation are left out.",
         changes="its pages made into web pages, with the site's menus, interactive examples and pictures left out"),
    dict(K.WEB, group=GROUP, name="music_theory_21st_century_classroom", title="Music Theory for the 21st-Century "
         "Classroom (Robert Hutchinson, GFDL)", subject="Music theory", publisher="Robert Hutchinson (University of "
         "Puget Sound)", country="United States", licence="GFDL 1.2 or later",
         licence_url="https://www.gnu.org/licenses/old-licenses/fdl-1.2.html", licence_page=MT21C + "frontmatter-3.html",
         licence_text=r"GNU Free Documentation License, Version 1\.2 or any later version",
         source=MT21C + "MusicTheory.html", crawl=[(MT21C + "MusicTheory.html", 1)],
         pages=r"^https://musictheory\.pugetsound\.edu/mt21c/[A-Za-z0-9_-]+\.html$",
         content=(r'<main class="ptx-main"[^>]*>', r"</main>"), limit=400, title_from=r"<title>([^<]+)</title>",
         unit_rules=[(r"/(BasicConcepts|Pitch|Notation|Octave|Accidentals|Enharmonic|Major|Minor|Scale|"
                      r"BasicsOfRhythm|TimeSignature|Durational|Dots|meter|Intervals?|Triads?)", "Fundamentals"),
                     (r"/(Roman|Cadence|Seventh|Harmonic|NonChord|Melodic|Phrase|Period|Sentence|Voice|Part)",
                      "Diatonic harmony and form"),
                     (r"/(Applied|Secondary|Modulation|Mixture|Neapolitan|Augmented|Altered|Chromatic)",
                      "Chromatic harmony"),
                     (r"/(Blues|Pop|Jazz|Chord|Lead|Swing|Guitar|Song)", "Popular music and jazz"),
                     (r"/(Twelve|Serial|Set|Post|Minimal|Additive|Phase|Modes|Impression)", "Twentieth-century music"),
                     (r".", "Other chapters")],
         description="Music Theory for the 21st-Century Classroom, an open college music theory textbook, every page: "
                     "basic concepts and notation, scales, keys and rhythm, intervals, triads and seventh chords, "
                     "Roman numerals and cadences, harmonic progression, non-chord tones, melody and phrase, "
                     "part-writing, chromatic harmony (applied chords, modulation, mixture, the Neapolitan and "
                     "augmented sixth chords), form, popular music (blues, chord symbols, lead sheets) and "
                     "twentieth-century music (modes, set theory, serialism and minimalism), with practice exercises "
                     "and their answers. " + NOTATION,
         notice="Music Theory for the 21st-Century Classroom, (c) 2017 Robert Hutchinson: \"Permission is granted to "
                "copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, "
                "Version 1.2 or any later version ... with no Invariant Sections, no Front-Cover Texts, and no "
                "Back-Cover Texts\" (share-alike); kept apart from the public-domain books. Its pictures of notation "
                "and its audio examples are left out.",
         changes="its pages made into web pages, with the site's menus, pictures of notation and audio left out"),
]
ALLOWED = {"GFDL 1.2 or later": "share-alike"}

# ====================================================================== theory (old books)

THEORY_PDFS = [
    book("jadassohn_manual_of_harmony_1893", "A Manual of Harmony (Salomon Jadassohn, 1893)", "Music theory: harmony",
         "Salomon Jadassohn, translated by Paul Torek and H. B. Pasmore (G. Schirmer)", "cu31924022485548", 1893,
         "The Leipzig Conservatory's harmony course in English: scales and intervals, triads and their connection, "
         "chords of the seventh and ninth, inversions, suspensions and passing notes, modulation and the chorale, "
         "with exercises."),
    book("stainer_harmony_1893", "Harmony, with one hundred graduated exercises (John Stainer, 1893)",
         "Music theory: harmony", "John Stainer (Novello, Ewer and Co.)", "cu31924022354421", 1893,
         "Novello's primer of harmony: chords and their progressions, part-writing, cadences, inversions, discords "
         "and their resolution, modulation, with a hundred graded exercises.", country="United Kingdom"),
    book("prout_counterpoint_strict_free_1890", "Counterpoint: Strict and Free (Ebenezer Prout, 1890)",
         "Music theory: counterpoint", "Ebenezer Prout (Augener)", "counterpointstri00prouuoft", 1890,
         "Counterpoint in two, three and four parts in the five species, then free counterpoint, with exercises.",
         country="United Kingdom"),
    book("prout_fugue_1891", "Fugue (Ebenezer Prout, 1891)", "Music theory: fugue", "Ebenezer Prout (Augener)",
         "fuguepro00prouuoft", 1891,
         "How a fugue is built: the subject, answer and countersubject, the exposition, episodes, stretto and pedal, "
         "with analyses of fugues by Bach and others.", country="United Kingdom"),
    book("prout_musical_form_1893", "Musical Form (Ebenezer Prout, 1893)", "Music theory: form",
         "Ebenezer Prout (Augener)", "15emusicalform00prouuoft", 1893,
         "The building blocks of musical form: motives, phrases and sentences, cadences, simple binary and ternary "
         "forms, with examples from the classics.", country="United Kingdom"),
    book("goetschius_tone_relations_1917", "The Theory and Practice of Tone-Relations (Percy Goetschius, 1900; "
         "1917 printing)", "Music theory: harmony", "Percy Goetschius (G. Schirmer)", "theorypracticeof00goetuoft", 1900,
         "A condensed course of harmony on a natural system: scales and keys, chords and their relations, "
         "progressions, part-writing, chromatic chords and modulation, with exercises."),
    book("goetschius_lessons_in_music_form_1904", "Lessons in Music Form (Percy Goetschius, 1904)",
         "Music theory: form", "Percy Goetschius (Oliver Ditson)", "lessonsinmusicfo00goetuoft", 1904,
         "A manual of musical analysis: the figure, motive, phrase and period, the song forms, rondos and the sonata "
         "allegro, explained for students and listeners."),
    book("goetschius_elementary_counterpoint_1910", "Exercises in Elementary Counterpoint (Percy Goetschius, 1910)",
         "Music theory: counterpoint", "Percy Goetschius (G. Schirmer)", "exercisesineleme00goetuoft", 1910,
         "A graded course in counterpoint, from writing one line against another to free invention in several "
         "parts, with exercises."),
    book("elson_theory_of_music_1890", "The Theory of Music (Louis C. Elson, 1890)", "Music theory: rudiments",
         "Louis C. Elson (New England Conservatory)", "cu31924021758226", 1890,
         "The theory of music as applied to teaching voice and instruments: notation, scales, intervals, chords, "
         "rhythm and the ornaments, in plain words for students."),
    book("elson_music_dictionary_1905", "Elson's Music Dictionary (Louis C. Elson, 1905)", "Music dictionary",
         "Louis C. Elson (Oliver Ditson)", "cu31924021631340", 1905,
         "A dictionary of the terms and signs used in music, with the pronunciation of each Italian, French and "
         "German word, a list of musical abbreviations and a short English-to-foreign dictionary of musical terms.",
         notation=False),
    book("ham_rudiments_of_music_1900", "The Rudiments of Music and Elementary Harmony (Albert Ham, 1900)",
         "Music theory: rudiments", "Albert Ham", "rudimentsofmusic00hama", 1900,
         "The rudiments of music (notation, time, scales, intervals, keys and terms) and the first steps in harmony, "
         "with test papers."),
    book("simpson_400_questions_rudiments_1900", "400 Questions on the Rudiments of Music (James Simpson, 1900)",
         "Music theory: rudiments", "James Simpson", "400questionsonru00simp", 1900,
         "Four hundred questions with their answers on the rudiments of music: notes, rests, clefs, time, scales, "
         "intervals, keys and the musical terms, for self-testing.", country="United Kingdom"),
]

# ====================================================================== learning to play (old method books)

METHOD_PDFS = [
    book("hofmann_piano_playing_1920", "Piano Playing, with Piano Questions Answered (Josef Hofmann, 1920 edition)",
         "Learning to play: piano", "Josef Hofmann (Theodore Presser)", "pianoplayingwith00hofmuoft", 1920,
         "The great pianist's two books in one: plain advice on practising, touch, technique, the pedal, playing "
         "from memory and interpretation, and his answers to hundreds of piano students' questions."),
    book("cooke_great_pianists_on_piano_playing_1917", "Great Pianists on Piano Playing (James Francis Cooke, 1917)",
         "Learning to play: piano", "James Francis Cooke (Theodore Presser)", "greatpianistsonp00cook", 1917,
         "Study talks with the great pianists of the time (Paderewski, Rachmaninoff, Hofmann, Godowsky, Bauer and "
         "others) on practice, technique, tone, rhythm and interpretation."),
    book("burrowes_piano_primer_1905", "Burrowes' Piano Primer (J. F. Burrowes, 1905 printing)",
         "Learning to play: piano", "J. F. Burrowes", "burrowespianopri00burriala", 1905,
         "The classic beginner's primer in questions and answers: the keyboard, notes and rests, time, scales, "
         "fingering and the musical terms, for lessons or self-teaching."),
    book("czerny_pianoforte_school_vol1_1839", "Complete Theoretical and Practical Piano Forte School, volume 1 (Carl "
         "Czerny, 1839)", "Learning to play: piano", "Carl Czerny (R. Cocks and Co.)", "completetheoreti01czer",
         1839,
         "Czerny's great piano method, volume 1: from the first rudiments of playing (sitting, the hand, the "
         "keyboard, notes and time) to scales and fingering, with his explanations of each exercise.",
         country="United Kingdom"),
    book("lehmann_how_to_sing_1915", "How to Sing (Lilli Lehmann, 1915 edition)", "Learning to play: voice and "
         "singing", "Lilli Lehmann, translated by Richard Aldrich (Macmillan)", "howtosingmeinege00lehmuoft", 1915,
         "The great soprano's book on singing: breathing, the voice's registers, resonance, vowels and consonants, "
         "exercises for the voice, and the care of the voice."),
    book("shakespeare_art_of_singing_1909", "The Art of Singing (William Shakespeare, 1909)", "Learning to play: "
         "voice and singing", "William Shakespeare (the singer and teacher; Oliver Ditson)", "artofsinging00shakuoft",
         1909,
         "A singing teacher's course based on the old Italian method: breath control, the attack, quality of tone, "
         "registers, agility and words, with exercises.", country="United Kingdom"),
    book("fucito_caruso_art_of_singing_1922", "Caruso and the Art of Singing (Salvatore Fucito, 1922)",
         "Learning to play: voice and singing", "Salvatore Fucito and Barnet J. Beyer (Frederick A. Stokes)",
         "cu31924022205318", 1922,
         "Caruso's accompanist on how Caruso sang and practised: breathing, tone, the vowels, his daily vocal "
         "exercises and his advice to students."),
    book("guilbert_how_to_sing_a_song_1919", "How to Sing a Song (Yvette Guilbert, 1919)", "Learning to play: voice "
         "and singing", "Yvette Guilbert (Macmillan)", "howtosingsongart00guiluoft", 1919,
         "The French singer on the art of interpreting a song: expression, the colour of the voice, gesture, and "
         "how to bring out the words and feeling of a lyric.", notation=False),
    book("carcassi_guitar_method_1853", "New and Improved Method for the Guitar (Matteo Carcassi, 1853 edition)",
         "Learning to play: guitar", "Matteo Carcassi (Oliver Ditson)", "newimprovedmetho00carc", 1853,
         "Carcassi's classic guitar method: holding the guitar, the strings and the fingerboard, the rudiments of "
         "music, scales and chords in every key, and graded lessons."),
    book("cole_five_minute_harmonica_course_1926", "5 Minute Harmonica Course (M. M. Cole, 1926)",
         "Learning to play: harmonica", "M. M. Cole Publishing Company", "5-minute-harmonica-course-m.-m.-cole", 1926,
         "A short course for the beginner on the harmonica (mouth organ): holding it, single notes, breathing in and "
         "out, the tongue for chords, and simple tunes by numbers."),
    book("minevitch_harmonica_at_sight_1923", "How to Play the Harmonica at Sight (Borrah Minevitch, 1923)",
         "Learning to play: harmonica", "Borrah Minevitch", "how-to-play-the-harmonica-at-sight-borrah-minevitch",
         1923,
         "The harmonica virtuoso's self-instructor: the instrument, single notes, the numbered system for reading "
         "tunes, tonguing, chords and effects."),
    book("kamiki_ukulele_method_1921", "The Kamiki Ukulele Method (1921)", "Learning to play: ukulele",
         "Wm. J. Smith Music Co.", "kamikiukulelemet00newy", 1921,
         "A ukulele method: tuning, holding the instrument, the strokes of the right hand, chords and their "
         "diagrams, and accompaniments for songs."),
    book("guckert_ukulele_chords_1917", "The Original Guckert's Chords for the Ukulele (E. N. Guckert, 1917)",
         "Learning to play: ukulele", "E. N. Guckert", "originalguckerts00guck", 1917,
         "Ukulele chords at sight without notes or teacher: tuning, the strokes and every common chord, described "
         "by string and fret."),
    book("peterson_ukulele_method_1924", "Peterson Ukulele Method (J. Kalani Peterson, 1924)",
         "Learning to play: ukulele", "J. Kalani Peterson", "petersonukulelem00pete", 1924,
         "A Hawaiian player's ukulele method: tuning, strokes and strums, chords in the common keys, and pieces."),
    book("jewett_flutina_accordion_teacher_1850", "Jewett's National Flutina and Accordion Teacher (1850)",
         "Learning to play: accordion", "John P. Jewett", "jewettsnationalf00jewe", 1850,
         "An early instruction book for the accordion and flutina: the instrument, the bellows and the keys, the "
         "rudiments of music, and tunes. The accordions of 1850 were simpler than today's.",
         note="Published in {year}: an old book about early button accordions; today's piano and chromatic "
              "accordions have more keys and basses."),
    book("auer_violin_playing_1921", "Violin Playing as I Teach It (Leopold Auer, 1921)", "Learning to play: violin "
         "and fiddle", "Leopold Auer (Frederick A. Stokes)", "violinplayingasi00auer", 1921,
         "The great violin teacher's own book: holding the violin and bow, the bow arm, tone, practising, the left "
         "hand, double stops, vibrato, ornaments, and how to interpret the violin repertoire."),
    book("martens_violin_mastery_1919", "Violin Mastery: Talks with Master Violinists and Teachers (Frederick H. "
         "Martens, 1919)", "Learning to play: violin and fiddle", "Frederick H. Martens (Frederick A. Stokes)",
         "violinmastery00mart", 1919,
         "Interviews with Ysaÿe, Kreisler, Elman, Heifetz, Auer and other violinists and teachers on technique, "
         "practice, tone and interpretation."),
    book("schroeder_handbook_violin_playing_1900", "Handbook of Violin Playing (Carl Schroeder, about 1900)",
         "Learning to play: violin and fiddle", "Carl Schroeder (Augener)", "handbookofviolin00schruoft", 1900,
         "A handbook for violin students: the instrument and bow, holding them, the positions, bowing, practising, "
         "and a guide to the studies and pieces to learn in order.", country="United Kingdom"),
    book("foden_home_study_lessons_banjo_1921", "Home Study Lessons for Banjo (William Foden, U.S. School of Music, "
         "1921)", "Learning to play: banjo", "William Foden (U.S. School of Music)",
         "home-study-lessons-for-banjo-us-school-of-music-foden", 1921,
         "A correspondence course for the banjo: tuning, holding the banjo, the right-hand strokes, the fingerboard, "
         "chords and graded lessons, each explained for a student working alone."),
    book("converse_analytical_banjo_method_1887", "Frank B. Converse's Analytical Banjo Method (1887)",
         "Learning to play: banjo", "Frank B. Converse (S. S. Stewart)", "FrankB.ConversesAnalyticalBanjoMethod",
         1887,
         "A method for the five-string banjo by its best-known teacher of the time: holding the banjo, the right-hand "
         "strokes, the fingerboard, chords and graded exercises."),
    book("deville_universal_method_saxophone_1908", "Universal Method for the Saxophone (Paul de Ville, 1908)",
         "Learning to play: woodwinds", "Paul de Ville (Carl Fischer)", "universalmethodf0000paul", 1908,
         "A complete saxophone method: the instrument and its family, the mouthpiece and reed, breathing and "
         "embouchure, fingering charts, tonguing, scales and studies."),
    book("klose_clarinet_method_1898", "Celebrated Method for the Clarinet (Hyacinthe Klosé, 1898 edition)",
         "Learning to play: woodwinds", "Hyacinthe Klosé (Carl Fischer)", "celebratedmethod00klos", 1898,
         "Klosé's clarinet method: the instrument, reed and mouthpiece, fingering, tone, articulation, scales and "
         "studies."),
    book("soussmann_flute_method_1906", "Complete Method for the Flute, part 1 (H. Soussmann, 1906 edition)",
         "Learning to play: woodwinds", "H. Soussmann (Carl Fischer)", "completemethodfo01sous", 1906,
         "A flute method: holding the flute, the embouchure, fingering, tonguing, scales and daily exercises."),
    book("strube_drum_fife_instructor_1870", "Strube's Drum and Fife Instructor (Gardiner A. Strube, 1870)",
         "Learning to play: drums", "Gardiner A. Strube", "strubesdrumfifei00stru", 1870,
         "The drum book adopted by the US Army in 1869: holding the sticks, the rudiments of drumbeating (rolls, "
         "flams, drags and ruffs), the camp duty and the fife calls."),
    book("nevins_army_regulations_drum_fife_bugle_1864", "Army Regulations for Drum, Fife, and Bugle (William "
         "Nevins, 1864)", "Learning to play: drums and bugle", "William Nevins", "armyregulationsf00nevi", 1864,
         "A Civil War manual for the drum, fife and bugle: the rudiments of each instrument, the beats and calls of "
         "camp and field duty, and how they were played.",
         note="Published in {year}: an old book; a historical record of the army's field music of its time."),
    book("mcgeary_yankee_doodle_method_1920", "The Yankee Doodle Method for Drum, Fife and Bugle (Robert E. McGeary, "
         "1920)", "Learning to play: drums and bugle", "Robert E. McGeary", "yankeedoodlemeth00mcge", 1920,
         "A simplified self-instructor for drum, fife and bugle: holding the instruments, the drum rudiments, the "
         "fife's fingering and the bugle calls."),
]

# The US Army's band manuals (works of the US government; the builder reads each one's front pages).
ARMY_NOTICE = "A work of the US Army (public domain); the builder says what its own front pages print about distribution."
ARMY_PDFS = [
    K.us_pdf(GROUP, name=f"army_fm_12_50_{year}", title=f"{title} (FM 12-50, {year})", subject="Learning to play: "
             "bands", publisher=publisher, archive=archive, distribution_a=True, published=published,
             version=f"FM 12-50, {year} (Internet Archive item {archive})",
             description=description + " " + NOTATION, notice=ARMY_NOTICE)
    for year, title, publisher, archive, published, description in [
        (1946, "The Band", "War Department", "FM12-501946", "1946-07",
         "The Army's band manual after the Second World War: organising and leading a band, rehearsals, the "
         "instruments and their players, concert and marching music, ceremonies and the care of instruments."),
        (1957, "The Marching Band", "Headquarters, Department of the Army", "FM12-501957", "1957-01",
         "The Army's manual for the marching band: formations, the drum major's signals, marching and playing, "
         "ceremonies and parades, and rehearsal."),
        (1969, "The Military Band", "Headquarters, Department of the Army", "FM12-501969", "1969-12",
         "The Army's band manual of 1969: the band's mission and organisation, the bandmaster and drum major, "
         "rehearsing, concert and ceremonial music, marching, and the instruments."),
    ]]

# ====================================================================== braille music, history and appreciation

BRAILLE_PDFS = [
    book("key_braille_music_notation_1922", "Key to the Braille Music Notation, 1922, with Synopsis and Index "
         "(1925)", "Braille music", "Braille Music Notation Committee (National Institute for the Blind)",
         "keytobraillemusi00brai", 1925,
         "The key to the braille music code agreed in 1922: the signs for notes, rests, octaves, intervals and "
         "chords, accidentals, time and key signatures, fingering, slurs, repeats and the formats for keyboard, "
         "vocal and instrumental music, with a synopsis and index.", note=BRAILLE_OLD, notation=False,
         country="United Kingdom"),
    book("robyn_braille_system_music_1867", "Thorough Description of the Braille System for the Reading and Writing "
         "of Music (Henry Robyn, 1867)", "Braille music", "Henry Robyn", "thoroughdescript00roby", 1867,
         "The first American description of braille music, by a teacher at the Missouri School for the Blind: the "
         "braille signs for notes, rests, octaves and the other parts of music, with how to read and write them.",
         note=BRAILLE_OLD, notation=False),
    book("watson_braille_music_problems_1925", "Braille Music and Its Problems (Edward Watson, 1925)",
         "Braille music", "Edward Watson (National Institute for the Blind)", "braillemusicitsp00edwa", 1925,
         "How the National Institute for the Blind tackled braille music in the 1920s: the code, transcribing and "
         "printing music in braille, and the problems that remained.", note=BRAILLE_OLD, notation=False,
         country="United Kingdom"),
]
HISTORY_PDFS = [
    book("pratt_history_of_music_1907", "The History of Music: a handbook and guide for students (Waldo Selden Pratt, "
         "1907)", "Music history", "Waldo Selden Pratt (G. Schirmer)", "historyofmusicha00pratuoft", 1907,
         "A one-volume history of music from ancient and folk music through the Middle Ages, the Renaissance and the "
         "classical and Romantic composers to the early twentieth century, with lists for further reading.",
         note=HISTORY_OLD, notation=False),
    book("baltzell_dictionary_of_musicians_1911", "Baltzell's Dictionary of Musicians (W. J. Baltzell, 1911)",
         "Music reference: musicians", "W. J. Baltzell (Oliver Ditson)", "cu31924022206464", 1911,
         "Short life stories of musicians of every period and country (composers, performers, teachers and writers "
         "on music), with how to pronounce their names.", note=HISTORY_OLD, notation=False),
    book("hamilton_outlines_music_history_1908", "Outlines of Music History (Clarence G. Hamilton, 1908)",
         "Music history", "Clarence G. Hamilton (Oliver Ditson)", "outlinesofmusich00hamiuoft", 1908,
         "A short history of music for students in outline form: periods, forms and composers, with suggested "
         "listening and questions.", note=HISTORY_OLD, notation=False),
    book("elson_history_of_american_music_1915", "The History of American Music (Louis C. Elson, 1915 edition)",
         "Music history: America", "Louis C. Elson (Macmillan)", "historyofamerica00elso", 1915,
         "Music in the United States from the Puritans' psalm-singing to the early twentieth century: hymns and "
         "folk songs, opera, orchestras, American composers, bands, patriotic songs and music teaching.",
         note=HISTORY_OLD, notation=False),
    book("arthur_elson_book_of_musical_knowledge_1915", "The Book of Musical Knowledge (Arthur Elson, 1915)",
         "Music history and appreciation", "Arthur Elson (Houghton Mifflin)", "cu31924022267441", 1915,
         "The history, technique and appreciation of music in one book, with the lives of the composers, the "
         "instruments of the orchestra and how music is built.", note=HISTORY_OLD, notation=False),
    book("hamilton_music_appreciation_1920", "Music Appreciation, based upon methods of literary criticism "
         "(Clarence G. Hamilton, 1920)", "Music appreciation", "Clarence G. Hamilton (Oliver Ditson)",
         "musicappreciatio00hamiuoft", 1920,
         "A course for listeners that treats music as literature is treated: melody, rhythm, harmony and form, the "
         "kinds of music (folk song, dance, song, the sonata, the symphony, opera) and how to judge a piece.",
         note=HISTORY_OLD, notation=False),
    book("faulkner_what_we_hear_in_music_1917", "What We Hear in Music (Anne Shaw Faulkner, 1917 edition)",
         "Music appreciation", "Anne Shaw Faulkner (Victor Talking Machine Company)", "whatwehearinmusi00ober_0",
         1917,
         "A laboratory course in music history and appreciation built around records: folk music, the orchestra "
         "and its instruments, musical form, opera and the great composers, with listening lists.",
         note=HISTORY_OLD + " Its record numbers are those of the Victor catalogue of its time.", notation=False),
]

PDFS = THEORY_PDFS + METHOD_PDFS + ARMY_PDFS + BRAILLE_PDFS + HISTORY_PDFS


def keys_of(entries):
    """The build keys of some entries of this module."""
    return [f"{PREFIX}:{e['name']}" for e in entries]


# ====================================================================== the index

LINK_ONLY = [
    ("link", "Music Braille Code 2015 (Braille Authority of North America)",
     "https://www.brailleauthority.org/music-braille-code-2015", "BANA's copyright: the current braille music code "
     "in the US and Canada; link-only, fetch it yourself."),
    ("link", "Introduction to Braille Music Transcription (Mary Turner De Garmo, Library of Congress, 1970)",
     "https://archive.org/details/introductiontobr00mary", "Written by a volunteer outside the government and "
     "quoting copyrighted music by permission of its publishers; link-only."),
    ("link", "Open Music Theory, second edition (Pressbooks)", "https://viva.pressbooks.pub/openmusictheory/",
     "CC BY-SA, but its host refuses programs; the first edition is built (musiclearn:open_music_theory)."),
    ("link", "Library of Congress Music Division research guides", "https://guides.loc.gov/music",
     "The guides quote and link other owners' material and are not wholly a government work; open them in a browser."),
    ("link", "IMSLP, the Petrucci Music Library (method books and scores)", "https://imslp.org/wiki/Category:Methods",
     "Its robots.txt disallows the files and listings (see the sheet music collection); link-only."),
]

INDEX_SECTIONS = [
    ("Music theory", "Textbooks of music theory: two open ones (share-alike) and old public-domain books on "
     "harmony, counterpoint, form and the rudiments. Music examples are printed notation, so these books give the "
     "explanations in words.",
     [("key", k, e["title"]) for k, e in zip(keys_of(GUIDES), GUIDES)] +
     [("key", k, e["title"]) for k, e in zip(keys_of(THEORY_PDFS), THEORY_PDFS)] +
     [("key", "games:prout_harmony_1889", "Prout's Harmony: its Theory and Practice (1889)"),
      ("key", "games:goetschius_melody_writing_1900", "Goetschius's Exercises in Melody-Writing (1900)"),
      ("word", "course:libretexts", "LibreTexts' open textbooks, among them its music theory and music appreciation "
                                    "books (the Humanities library)"),
      ("word", "cat:otl", "the Open Textbook Library's books, among them Understanding Basic Music Theory "
                          "(Schmidt-Jones, CC BY)")]),
    ("Learning to play", "Old method books for each instrument and voice, chosen for their explanations, and the US "
     "Army's band manuals. The exercises themselves are printed notation.",
     [("key", k, e["title"]) for k, e in zip(keys_of(METHOD_PDFS + ARMY_PDFS), METHOD_PDFS + ARMY_PDFS)] +
     [("word", "oldbooks-life-instruments", "the old instrument books of the life-skills collection: guitar "
                                            "(Holland, Foden), banjo (Converse, Grimshaw), band instruments "
                                            "(Clappé, Goldman, Gallo), piano and violin making"),
      ("manuals", "musical_instruments", "makers' manuals for keyboards, guitars, amplifiers and pro audio"),
      ("manuals", "instrument_care", "care and repair guides for instruments")]),
    ("Braille music", "Old braille music guides (out of date as a code: check against the Music Braille Code 2015) "
     "and the National Library Service's braille music catalogues.",
     [("key", k, e["title"]) for k, e in zip(keys_of(BRAILLE_PDFS), BRAILLE_PDFS)] +
     [("key", "pdf:braille_music_notation_1930", "Braille Music Notation (American Braille Press, 1930)"),
      ("key", "lopen:braille_procede_1829", "Louis Braille's own book of 1829, with his music signs (in French)"),
      ("key", "blind:nls_dictionary_braille_music_signs_1979", "Krolick's Dictionary of Braille Music Signs (NLS, "
                                                                "1979)"),
      ("key", "music:nls_braille_music", "the NLS braille music catalogues and the Music Section's guides"),
      ("key", "vision:nls_services", "the National Library Service: who can enrol, talking books and braille")] +
     LINK_ONLY[:2]),
    ("Music history and appreciation", "Old histories of music and listening courses.",
     [("key", k, e["title"]) for k, e in zip(keys_of(HISTORY_PDFS), HISTORY_PDFS)] +
     [("key", "lit:stanford_forsyth_history_of_music", "Stanford and Forsyth's A History of Music"),
      ("key", "lit:krehbiel_how_to_listen", "Krehbiel's How to Listen to Music"),
      ("word", "old-radio", "old-time radio scripts, with music programmes of their time")]),
    ("Sheet music, instruments and recording", "Scores, instrument care and recording, elsewhere in the library.",
     [("word", "sheet-music", "the sheet music collection: Mutopia scores (LilyPond text and PDF) and its own "
                              "guide (music:index)"),
      ("word", "instrument-care", "piano tuning and violin making (instr:)"),
      ("word", "audio-media", "recording and editing audio: the Audacity Manual, OSARA and media guides"),
      ("manuals", "audio_gear", "audio recorders, microphones and recording gear")] + LINK_ONLY[2:]),
]

INDEX_BOOK, INDEX_SIGN = X.index_maker(
    PREFIX, GROUP, "Learning music: a guide to the library", "Music: theory, playing, braille music and history",
    "A guide to the music books of the library: music theory, learning to play an instrument or sing, braille music "
    "and music history, with the key of each book, the sheet music and instrument collections, and the sources that "
    "are links only.", INDEX_SECTIONS)

WORDS = {
    "music-theory": lambda: keys_of(GUIDES + THEORY_PDFS),
    "music-methods": lambda: keys_of(METHOD_PDFS + ARMY_PDFS),
    "music-braille-history": lambda: keys_of(BRAILLE_PDFS + HISTORY_PDFS),
    "music-learning": lambda: [f"{PREFIX}:index"] + keys_of(GUIDES + PDFS),
}
COLLECTION = K.Collection(PREFIX, GROUP, guides=GUIDES, pdfs=PDFS, makers={"index": (INDEX_BOOK, INDEX_SIGN)},
                          words=WORDS)

LICENCE_LINES = {
    "musiclearn_open_textbooks": "openmusictheory.github.io: every page's footer \"(c) 2022 Hybrid Pedagogy Publishing. "
                                 "CC BY-SA 4.0.\" (checked at every build on its contents page); robots.txt "
                                 "\"User-agent: * Disallow:\" (all allowed). musictheory.pugetsound.edu/mt21c: its "
                                 "colophon \"Permission is granted to copy, distribute and/or modify this document "
                                 "under the terms of the GNU Free Documentation License, Version 1.2 or any later "
                                 "version\" (checked at every build); no robots.txt (none answers), no AI rules "
                                 "(checked 2026-11-23). Both share-alike, kept apart.",
    "musiclearn_old_books": "archive.org (its robots.txt allows the files): books published before 1931 are in the US "
                            "public domain; the builder checks each item's year on the Internet Archive's record at "
                            "every build. Lending-library-only copies are not used.",
    "musiclearn_army": "FM 12-50 (1946, 1957, 1969): works of the US Army, read from the Internet Archive; the builder "
                       "reads each one's front pages and follows the shared distribution rule (military_release.py).",
    "musiclearn_index": "The index (musiclearn:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("Music Braille Code 2015 (BANA)", "Copyright of the Braille Authority of North America; link-only (also in "
     "vision_living.py and sheet_music.py). Index: https://www.brailleauthority.org/music-braille-code-2015"),
    ("Introduction to Braille Music Transcription (Mary Turner De Garmo, Library of Congress, 1970)", "Written by a "
     "volunteer outside the government; it quotes copyrighted music (Sam Fox 1939, Summy-Birchard 1959 and others) by "
     "permission, which does not pass to copies. Link-only. Index: https://archive.org/details/introductiontobr00mary"),
    ("Open Music Theory, second edition (viva.pressbooks.pub)", "CC BY-SA 4.0, but its host answers programs "
     "\"403\" (checked again 2026-11-23); the first edition is built (musiclearn:open_music_theory). Index: "
     "https://viva.pressbooks.pub/openmusictheory/"),
    ("Library of Congress Music Division research guides (guides.loc.gov/music)", "The guides list and quote "
     "other owners' material; not built as a government work. Index: https://guides.loc.gov/music"),
    ("Starting-out method books full of exercises only (Arban's cornet method, most band and drum books)", "Their "
     "pages are almost all notation, which the scanner cannot read, so the builder would find no words; books with "
     "explanations were chosen instead. Index: https://archive.org/search?query=subject%3A%22instruction+and+study%22"),
    ("Lilli Lehmann's How to Sing (1924 printing) and other lending-library copies", "Lending-library only on the "
     "Internet Archive; the 1915 edition is built. Index: https://archive.org/details/howtosing0000lill"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
