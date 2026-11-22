"""The collection "Musical instrument care and repair (guides and manuals)" (category key instrument_care), the
owner's life-skills request of 2026-11-22. categories.py adds it to CATEGORIES. Electronic instruments and pro audio
are the category musical_instruments (and their repair the electronics collections).

What it lists, in plain words (an INDEX of facts and links only):
  ia      the Internet Archive's manual collections, searched by IA_WORDS (acoustic instruments' care and setup,
          tuners, metronomes, humidifiers, string winders, piano care);
  makers  instrument, string, drumhead and care-product makers: link-only by the owner's rule (nothing is read);
  guidance the old public-domain books of the reference library (piano tuning, violin making).
"""

INSTRUMENT_SAFETY = ("Unplug electric instruments and amplifiers before working on them; amplifiers hold dangerous "
                     "voltages inside even when unplugged, so leave their repair to a technician. Loosen strings "
                     "slowly and wear eye protection when cutting them.")

IA_WORDS = ["guitar care", "guitar setup", "violin care", "string instrument care", "instrument care", "chromatic tuner",
            "clip-on tuner", "instrument humidifier", "guitar humidifier", "piano care", "piano tuning",
            "band instrument", "woodwind care", "brass care", "drum tuning"]

RULE = ("by the owner's rule the maker's own care guides and manuals are link-only: nothing is read from its site; "
        "its page is listed for the person to open")
_COMMON = dict(category="instrument_care", prefix="ic", documents="care guides and manuals", access="link",
               reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="yamaha-music", maker="Yamaha (pianos, band and orchestral instruments)", type="instrument care",
         library="https://usa.yamaha.com/support/", site="yamaha.com"),
    dict(key="steinway", maker="Steinway & Sons", type="piano care", library="https://www.steinway.com/",
         site="steinway.com"),
    dict(key="fender", maker="Fender", type="guitar setup and care", library="https://support.fender.com/",
         site="fender.com"),
    dict(key="martin", maker="C. F. Martin & Co.", type="guitar care", library="https://www.martinguitar.com/",
         site="martinguitar.com"),
    dict(key="taylor", maker="Taylor Guitars", type="guitar care", library="https://www.taylorguitars.com/support",
         site="taylorguitars.com"),
    dict(key="daddario", maker="D'Addario", type="strings, reeds, drumheads and humidifiers",
         library="https://www.daddario.com/", site="daddario.com"),
    dict(key="conn-selmer", maker="Conn-Selmer", type="band instrument care", library="https://www.conn-selmer.com/",
         site="conn-selmer.com"),
    dict(key="remo", maker="Remo", type="drumheads", library="https://remo.com/", site="remo.com"),
    dict(key="korg-tuners", maker="Korg (tuners and metronomes)", type="tuners and metronomes",
         library="https://www.korg.com/us/support/", site="korg.com"),
]]

GUIDANCE = [
    dict(title="Modern Piano Tuning and Allied Arts (1917; in the reference library: instr:white_piano_tuning_1917)",
         url="https://archive.org/details/modernpianotunin00whit", by="William Braid White (public domain)"),
    dict(title="Violin-Making, As It Was and Is (1885; in the reference library: "
               "instr:heron_allen_violin_making_1885)", url="https://archive.org/details/cu31924022320216",
         by="Edward Heron-Allen (public domain)"),
]

CATEGORY = dict(
    name="Musical instrument care and repair (guides and manuals)",
    description="Caring for acoustic instruments: guitars and violins (strings, setup, humidity), pianos (tuning "
                "and care), band instruments (woodwinds and brass), drums (heads and tuning), tuners and humidifiers: the Internet Archive's manuals, the makers' care guides (links) and the old "
                "public-domain books of the reference library.",
    kind="manuals", licence="CC0 (facts and links); each document belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=INSTRUMENT_SAFETY)
