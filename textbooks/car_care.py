"""Car care for the reference library, in the group "Reference, car care and driving" (the owner's request of
2026-11-22). Keys: car-care (every book), car:<name>.

What could be built, in plain words: the official US guides to car care are on sites that refuse programs or carry no
licence statement (NHTSA, FuelEconomy.gov, the Alternative Fuels Data Center: NOT_INCLUDED, link-only for the owner's
personal assistant), and makers' owner's manuals are copyright (the manual library links them). So this module
builds the old public-domain car care books, each whole from the Internet Archive's scan with its text layer, only
when the Internet Archive's record shows it was published before 1931 (checked at every build); each says plainly
that it is out of date (cars, fluids and safety rules have changed), and is kept for the basics of how an engine,
battery, tyres and brakes work:
  - The Automobile Book: A Practical Treatise on the Construction, Operation and Care of Motor Cars (1915);
  - The Automobile Storage Battery, Its Care and Repair (1918);
  - Automobile Troubles and Repairs (1916).
NHTSA's vehicle recalls are already in the library (textbooks/recalls.py), and the US Army's automotive manuals are
in the manual library's car_care category (public guides).

Every book starts with the safety note: never work under a car held up only by a jack (jack stands on firm, level
ground); let a hot engine cool before opening the radiator or coolant cap; battery acid burns and batteries give off
explosive gas; if you break down, get off the road, turn on the hazard lights and call for help (911 in an
emergency).

Run from the repository's folder:
  python3 textbooks/car_care.py car:automobile_book_1915 --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "carcare"
GROUPS = {GROUP: "Reference, car care and driving"}
SAFETY = ("Safety first: never work under a car held up only by a jack (use jack stands on firm, level ground); let "
          "a hot engine cool before opening the radiator or coolant cap; battery acid burns and batteries give off "
          "explosive gas; if you break down, get off the road, turn on the hazard lights and call for help (911 in "
          "an emergency).")
OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"


def old_book(group, name, title, subject, archive, year, description, safety):
    """An old public-domain book read whole from its Internet Archive item (build_textbooks.pdfdoc_book checks the
    item's year is before 1931 at every build), with the safety note and the out-of-date note."""
    return dict(name=name, title=title, subject=subject, group=group, country="United States",
                publisher=f"published {year}", licence=OLD_LICENCE, licence_url=OLD_URL, archive=archive,
                old_public_domain=True, published=str(year), level="reference",
                version=f"Internet Archive item {archive}", description=description,
                notice=f"{safety} Published in {year}: an old book, out of date; read it for the basics, and follow "
                       f"today's guides and your own manual for anything you do.")


PDFS = [
    old_book(GROUP, "automobile_book_1915", "The Automobile Book: A Practical Treatise on the Construction, "
             "Operation and Care of Motor Cars (1915)", "Car care (old book)", "automobilebooka00homagoog", 1915,
             "A 1915 handbook on how a motor car is built and works (engine, ignition, carburettor, cooling, "
             "lubrication, transmission, brakes, tyres) and how to drive and look after it.", SAFETY),
    old_book(GROUP, "storage_battery_1918", "The Automobile Storage Battery: Its Care and Repair (1918)",
             "Car batteries (old book)", "automobilestora00chicgoog", 1918,
             "A 1918 book on the lead-acid car battery: how it works, charging, testing with a hydrometer, keeping "
             "it filled and clean, and its troubles and repair.", SAFETY),
    old_book(GROUP, "automobile_troubles_1916", "Automobile Troubles and Repairs (1916)",
             "Car repair (old book)", "automobiletroub00cravgoog", 1916,
             "A 1916 guide to finding and fixing a car's troubles: starting, ignition, fuel, overheating, noises, "
             "tyres and punctures, with welding and vulcanising.", SAFETY),
]

COLLECTION = K.Collection("car", GROUP, pdfs=PDFS, words={"car-care": lambda: [f"car:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "car_old_books": "archive.org (its robots.txt allows the files): books published before 1931 are in the US "
                     "public domain; the builder checks each item's year on the Internet Archive's record at every "
                     "build.",
}
NOT_INCLUDED = [
    ("NHTSA consumer guides (tyre safety, vehicle maintenance, car seats, safety ratings)", "Public domain, but "
     "www.nhtsa.gov answers programs \"403 Forbidden\", robots.txt included (checked 2026-11-22). Its recalls are "
     "built from its API (textbooks/recalls.py). Link-only. Index: https://www.nhtsa.gov/equipment/tires and "
     "https://www.nhtsa.gov/road-safety"),
    ("FuelEconomy.gov (DOE and EPA): gas mileage tips and keeping your car in shape", "Its robots.txt does not allow "
     "this builder's reader on /feg/ (checked 2026-11-22). Link-only. Index: https://www.fueleconomy.gov/feg/"
     "maintain.jsp"),
    ("Alternative Fuels Data Center: electric vehicle charging guides (afdc.energy.gov)", "Run by the National "
     "Renewable Energy Laboratory for DOE; its disclaimer page states no public-domain or open licence (checked "
     "2026-11-22), so its text is not copied. Link-only. Index: https://afdc.energy.gov/fuels/electricity"),
    ("FMCSA (fmcsa.dot.gov)", "Refuses programs (\"403\", checked 2026-11-22); written for commercial drivers. "
     "Index: https://www.fmcsa.dot.gov/"),
    ("Car makers' owner's manuals and maintenance schedules", "Copyright of each maker; the manual library's cars "
     "category links them. Index: https://www.nhtsa.gov/recalls"),
    ("EPA Green Vehicle Guide", "The EPA's copyright statement allows non-commercial use only (see pets_home.py); "
     "its pages are about buying cleaner vehicles, not care. Link-only. Index: https://www.epa.gov/greenvehicles"),
    ("YouTube car care videos, Instructables, Reddit and car forums", 
     "Not read (the owner's rule: their terms forbid scraping, or the "
     "pictures and text are their users' own). Index: https://www.youtube.com/results?search_query=car+maintenance"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
