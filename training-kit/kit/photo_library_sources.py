"""LARGE PUBLIC-DOMAIN US GOVERNMENT PHOTO LIBRARIES for the Picture Model Training Kit (the owner's request of
2026-11-22). This file lists:
  - the ready-made packs built in packs/nasa_library_packs.py (the NASA Image and Video Library by theme) and
    packs/nps_library_packs.py (the National Park Service's NPGallery by theme), group "permissive"; the kit
    downloads them with prepare_pack;
  - the libraries looked at and left out, with the reason (PHOTO_LIBRARY_NOT_INCLUDED), and those that need a free
    sign-up the kit cannot do for the user (PHOTO_LIBRARY_SIGN_UP).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit
on the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence
was checked at its source in November 2026: NASA's own pictures and the Park Service staff's photos are US
government works, not under copyright; the packs keep only records credited to NASA (with its centres, JPL-Caltech,
STScI or the USGS) or to the Park Service, with no copyright, courtesy or licence words.

Answers are each record's own words (NASA's caption, trimmed to the plain description; the park's accessibility alt
text and description), never a guess. People in the pictures are described as the captions describe them (names
included, never recognised from a face); children only as the libraries show them, in everyday clothed scenes.

Picture-making (PHOTO_LIBRARY_PICTURE_MAKING_OK): only the planets, Earth-from-space, wildlife and landscape packs;
sources.py puts every other key in NOT_FOR_PICTURE_MAKING, and the packs that are mostly people (astronauts, NASA
people at work, launch crews, visitors using accessibility features and facilities) are PHOTO_LIBRARY_BODILY_KEYS,
added to sources.PEOPLE_AND_BODILY_PACK_KEYS.
Topics (topics.py): aircraft and rockets in "transport"; Earth from space, planets and telescopes, wildlife and
landscapes in "nature"; visitor facilities and signs in "documents" and "places"; accessibility features in "vision";
people at work in "people"; historic buildings in "places"; the astronaut pack in no topic.

    python -c "import sources, photo_library_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

NASA_LICENCE = ("Not under copyright: NASA images (nasa.gov/nasa-brand-center/images-and-media); only records "
                "credited to NASA, its centres, JPL-Caltech, STScI or the USGS, with no copyright or courtesy words")
NASA_CREDIT = "NASA Image and Video Library, https://images.nasa.gov (each picture's credit in CREDITS.txt)"
NPS_LICENCE = ("Public domain (U.S. National Park Service staff photos); only records marked 'Public domain' and "
               "credited to the Park Service")
NPS_CREDIT = "U.S. National Park Service, NPGallery, https://npgallery.nps.gov (each photo's credit in CREDITS.txt)"

PHOTO_LIBRARY_SOURCES = [
    Source("nasa_space_astronauts", "Astronauts and spaceflight: spacewalks, the space station, the shuttle, Apollo, "
                                    "Skylab and crew training, with NASA's captions (NASA Image and Video Library, "
                                    "ready-made pack)",
           NASA_LICENCE, NASA_CREDIT, "permissive", 3000, 20, prepare_pack, "about 900 MB"),
    Source("nasa_aircraft", "NASA research aircraft: X-planes, the ER-2, SOFIA, the DC-8, helicopters, drones and "
                            "wind-tunnel models, with NASA's captions (NASA Image and Video Library, ready-made pack)",
           NASA_LICENCE, NASA_CREDIT, "permissive", 2500, 15, prepare_pack, "about 750 MB"),
    Source("nasa_earth_from_space", "The Earth from space: storms, coasts, cities at night and auroras photographed "
                                    "from orbit, with NASA's captions (NASA Image and Video Library, ready-made pack)",
           NASA_LICENCE, NASA_CREDIT, "permissive", 3000, 20, prepare_pack, "about 900 MB"),
    Source("nasa_planets_telescopes", "Planets, moons, the Sun, comets, galaxies and nebulas from NASA missions and "
                                      "telescopes, with NASA's captions (NASA Image and Video Library, ready-made "
                                      "pack)",
           NASA_LICENCE, NASA_CREDIT, "permissive", 3000, 20, prepare_pack, "about 800 MB"),
    Source("nasa_rockets_launch", "Rockets, launches and launch sites: pads, the Vehicle Assembly Building, "
                                  "crawler-transporters, rollouts and engine tests, with NASA's captions (NASA Image "
                                  "and Video Library, ready-made pack)",
           NASA_LICENCE, NASA_CREDIT, "permissive", 3000, 20, prepare_pack, "about 900 MB"),
    Source("nasa_people_at_work", "NASA people at work: engineers, technicians and scientists in labs, clean rooms "
                                  "and mission control, with NASA's captions (NASA Image and Video Library, "
                                  "ready-made pack)",
           NASA_LICENCE, NASA_CREDIT, "permissive", 2500, 15, prepare_pack, "about 750 MB"),
    Source("npgallery_accessibility", "Accessibility in the national parks: accessible trails, ramps, lifts, tactile "
                                      "exhibits, braille and audio-described signs, accessible campsites and "
                                      "restrooms, with the parks' alt text (NPGallery, ready-made pack)",
           NPS_LICENCE, NPS_CREDIT, "permissive", 1500, 10, prepare_pack, "about 600 MB"),
    Source("npgallery_facilities", "National park visitor facilities and signs: visitor centres, entrance signs, "
                                   "wayside exhibits, trailheads, campgrounds, picnic areas and boardwalks, with the "
                                   "parks' alt text (NPGallery, ready-made pack)",
           NPS_LICENCE, NPS_CREDIT, "permissive", 3000, 20, prepare_pack, "about 1.2 GB"),
    Source("npgallery_historic_buildings", "Historic buildings in the national parks: cabins, houses, barns, mills, "
                                           "churches, missions, pueblos and cliff dwellings, with the parks' alt "
                                           "text (NPGallery, ready-made pack)",
           NPS_LICENCE, NPS_CREDIT, "permissive", 3000, 20, prepare_pack, "about 1.2 GB"),
    Source("npgallery_wildlife_more", "More national park wildlife: deer, moose, wolves, foxes, sheep and goats, "
                                      "seals, whales, reptiles, frogs, fish, butterflies and birds of prey, with the "
                                      "parks' alt text (NPGallery, ready-made pack)",
           NPS_LICENCE, NPS_CREDIT, "permissive", 3000, 20, prepare_pack, "about 1.2 GB"),
    Source("npgallery_landscapes_more", "More national park landscapes: arches, hoodoos, dunes, prairies, meadows, "
                                        "wetlands, islands, cliffs, hot springs, tide pools and redwoods, with the "
                                        "parks' alt text (NPGallery, ready-made pack)",
           NPS_LICENCE, NPS_CREDIT, "permissive", 3000, 20, prepare_pack, "about 1.2 GB"),
]

# The collections a picture-making model may learn from: things and places, not people.
PHOTO_LIBRARY_PICTURE_MAKING_OK = {"nasa_earth_from_space", "nasa_planets_telescopes", "npgallery_wildlife_more",
                                   "npgallery_landscapes_more"}
# The packs that are mostly people: describing only (added to sources.PEOPLE_AND_BODILY_PACK_KEYS).
PHOTO_LIBRARY_BODILY_KEYS = ("nasa_space_astronauts", "nasa_people_at_work", "nasa_rockets_launch",
                             "npgallery_accessibility", "npgallery_facilities")

PHOTO_LIBRARY_SIGN_UP = {
    "NPS Data API (developer.nps.gov), its multimedia galleries and photos":
        "https://www.nps.gov/subjects/developer/get-started.htm (a free API key, by e-mail sign-up)",
    "NOAA Photo Library and US Forest Service, BLM and USDA photos on Flickr":
        "https://www.flickr.com/services/apps/create/ (a free Flickr API key)",
}

PHOTO_LIBRARY_NOT_INCLUDED = {
    "NASA Image and Video Library items by others": "pictures credited to companies (SpaceX, Rocket Lab, Boeing), to "
        "other space agencies and their astronauts (ESA, CSA, JAXA), to universities, amateurs or 'courtesy of' "
        "anyone, or marked copyright, are left out of the NASA packs: only NASA's own pictures are public domain.",
    "NASA artist's concepts, illustrations, logos, patches and posters": "graphics, not photos; left out.",
    "NPGallery records not credited to the Park Service": "volunteers', partners' and other photographers' photos, "
        "even when marked public domain, are left out: the owner asked for NPS staff photos only.",
    "NPS Multimedia Search on www.nps.gov": "its pages are under /search/, which www.nps.gov's robots.txt "
        "disallows; the NPS Data API needs a key (PHOTO_LIBRARY_SIGN_UP).",
    "US Fish and Wildlife Service National Digital Library": "public domain, but its old site forwards to "
        "fws.gov/search/images, and fws.gov's robots.txt disallows /search (checked 22 November 2026).",
    "NOAA Photo Library": "public domain, but photolib.noaa.gov forwards to www.noaa.gov/noaa-collections, which "
        "refused this machine (405, 22 November 2026); its Flickr copy needs a Flickr API key.",
    "Already in the kit": "the USGS multimedia gallery (usgs), the Library of Congress FSA/OWI photographs "
        "(loc_fsa), Highsmith (loc_highsmith), HABS and HAER (loc_habs_houses, loc_haer), NPGallery's general pack "
        "(npgallery), NASA Earth Observatory (earth_observatory) and the small live NASA collection (nasa): not "
        "repeated.",
    "USDA, FEMA and Smithsonian photo pages": "usda.gov and si.edu refused this machine (403); FEMA's library "
        "refused it before (see graphic_sources.py); not all Smithsonian pictures are public domain.",
}
