"""Picture collections of NON-PROFIT ORGANISATIONS (NGOs, charities, foundations) for the Picture Model Training
Kit that cannot be ready-made packs: what was looked at, what is already in the kit, what is left out and why, and
which organisations to ask for permission. The open ones are packs: packs/ngo_packs.py (Our World in Data charts)
and packs/field_manual_packs.py (drawings from US military field manuals with Distribution Statement A; US
government works, not an NGO, but built in the same survey).

As in the other *_sources.py files, nothing here is re-shared by the kit's makers, and nothing here downloads
anything: NGO_SOURCES is the place for a collection the kit downloads on the user's own computer when it is not open
(share-alike, non-commercial, research); none was found that is both usable and not already in the kit, so it is
empty for now. The categories are those of packs/SOURCE-RULES.md.

Rules kept (packs/SOURCE-RULES.md): no sexual content; children only in everyday scenes and marked "child"; no
children-focused charity imagery (appeal photos of children in need are left out, whatever their licence); people
are never learnt from for picture-making; licences checked at the source; robots.txt and terms obeyed; keys only
from environment variables.

    NGO_SOURCES               [] (Source entries; see sources.Source)
    NGO_PICTURE_MAKING_OK     the keys of NGO_SOURCES a picture-making model may learn from (none)
    NGO_ALREADY_IN_KIT        NGO collections that are already packs or kit entries, and where
    NGO_NOT_INCLUDED          {collection: why it is left out}
    NGO_PERMISSION_CANDIDATES {organisation: what it has, its terms, whom to ask}
"""

NGO_SOURCES = []
NGO_PICTURE_MAKING_OK = ()

NGO_ALREADY_IN_KIT = {
    "Gapminder Dollar Street": "packs/world_life_packs.py and packs/people_activity_packs.py (CC BY 4.0).",
    "iNaturalist (California Academy of Sciences and National Geographic Society)": "build_packs.build_inaturalist "
                                                                                   "(CC0 and CC BY photos).",
    "Wikimedia Commons (Wikimedia Foundation)": "many packs; share-alike files in the kit's share-alike entries.",
    "Smithsonian Open Access": "build_packs.build_smithsonian (CC0).",
    "Europeana": "the europeana packs (each item's own licence).",
    "Zooniverse camera-trap projects (Snapshot Serengeti and others, via LILA BC)": "packs/everyday_packs.py "
                                                                                    "(Community Data License "
                                                                                    "Agreement, permissive).",
    "Disabled And Here (Affecting Change Collective)": "packs/disability_packs.py (its Commons files, CC BY).",
    "Mapillary street photos (StreetSurfaceVis)": "training-kit/kit/extra_sources.py (CC BY-SA 4.0, share-alike).",
}

NGO_NOT_INCLUDED = {
    "Free Music Archive, Mozilla Common Voice": "sound and speech, not pictures.",
    "Our World in Data articles' photos": "only its charts are used (owid_charts): the photos in its articles are "
                                          "other people's, under their own licences.",
    "Gender Spectrum Collection (Vice)": "CC BY-NC-ND with editorial-use terms: no derivatives (a description is a "
                                        "change), and it shows people.",
    "Save the Children, UNICEF, CARE and other child-focused charities' photo libraries": "copyright, and appeal "
                                                                                         "photos of children in "
                                                                                         "need are never used (the "
                                                                                         "owner's rule), whatever "
                                                                                         "their licence.",
    "UN Photo": "copyright of the United Nations; its terms were not readable from this machine (the terms page "
                "answered 404). Not used without the UN's written permission.",
    "WWF and The Nature Conservancy photo libraries": "copyright of each organisation and its photographers; for "
                                                      "press use only.",
    "American Red Cross photo library": "its media pages refuse automated requests (403); photos are for news use "
                                        "under its terms (not checked from this machine).",
    "Habitat for Humanity, Feeding America, Goodwill": "no open photo collection found; their photos are their "
                                                       "own (terms pages not checked from this machine).",
    "Humanitarian OpenStreetMap Team (HOT)": "map data (ODbL), not photos; its drone imagery is on OpenAerialMap "
                                             "under each uploader's licence, mostly CC BY 4.0 but without words "
                                             "describing the pictures.",
    "Internet Archive picture collections": "rights differ item by item; used only where an item is a US government "
                                            "work with Distribution Statement A (packs/field_manual_packs.py).",
    "Canadian Armed Forces manuals": "Crown copyright, non-commercial reproduction only (canada.ca terms): personal "
                                     "use at most, and not checked item by item; left out.",
}

NGO_PERMISSION_CANDIDATES = {
    "Hesperian Health Guides (Where There Is No Doctor and other books)":
        "Has: thousands of clear line drawings of first aid, health care and daily life, each with a caption, made "
        "for people with little schooling. Terms: its books let anyone copy and adapt them to be given away free "
        "or at cost, not for profit, and ask to be told first. Ask (for training a picture describer for blind "
        "people, credited, not sold as pictures): the contact page of hesperian.org.",
    "UN Photo (United Nations Department of Global Communications)":
        "Has: decades of captioned photos of humanitarian work, schools, clinics and daily life. Ask: the UN Photo "
        "Library's permissions desk (address on media.un.org).",
    "American Red Cross and the IFRC":
        "Have: captioned photos of disaster response, shelters, blood drives and first-aid training, and the IFRC's "
        "first-aid guideline drawings. Ask: their media relations offices.",
    "Perkins School for the Blind (Paths to Literacy) and the American Printing House for the Blind":
        "Have: photos of braille, tactile graphics and assistive devices with descriptions written for blind "
        "readers. Ask: their communications offices (both are all rights reserved).",
}
