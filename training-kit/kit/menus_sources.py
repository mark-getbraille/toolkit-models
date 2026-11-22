"""RESTAURANT MENUS for the Picture Model Training Kit (the owner's request of 2026-11-22: pictures for the picture
describer). This file lists the ready-made packs built in packs/menus_packs.py (group "permissive"; the kit downloads
them with prepare_pack) and what was looked at and left out, with the reason (MENUS_NOT_INCLUDED):
  nypl_menus       pages of historical menus from the New York Public Library's "What's on the Menu?" collection
                   with the dishes and prices volunteers transcribed (data CC0 from NYPL; pictures of menus published
                   before 1931, public domain in the United States, or marked "No Known U.S. Copyright Restrictions"
                   or CC0 by NYPL when the pack builder had an NYPL_API_TOKEN);
  synthetic_menus  computer-made modern menus (made-up restaurants, .example web sites, 555-01xx numbers) in common
                   layouts: one and two columns, drawn pictures of dishes, price boards and specials boards.

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer, from the kit's own release, only when the user ticks it. Answers say only what the library's
records or the generator say; allergy answers end "if you have a food allergy, ask the staff before you order".
Topics: food (Food and packaged goods) and documents (Documents, maps and signs). Picture-making
(MENUS_PICTURE_MAKING_OK): synthetic_menus only (made-up menus, no people); the NYPL menus are old printed works with
illustrations by named and unnamed artists, so they are not used for picture-making.

    python -c "import sources, menus_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

MENUS_SOURCES = [
    Source("nypl_menus", "Historical restaurant menus with their dishes and prices as transcribed, and the restaurant, "
                         "event and date (New York Public Library, What's on the Menu?, ready-made pack)",
           "Menu data CC0 (NYPL); pictures public domain in the United States (published before 1931, or marked No "
           "Known U.S. Copyright Restrictions or CC0 by NYPL)",
           "From The New York Public Library, What's on the Menu?, https://www.nypl.org/research/support/"
           "whats-on-the-menu (each page in CREDITS.txt)", "permissive", 3000, 30, prepare_pack, "about 900 MB"),
    Source("synthetic_menus", "Modern restaurant menus read in order: dishes, prices, vegetarian and gluten-free marks, "
                              "specials boards and the restaurant's details (computer-made, synthetic, ready-made pack)",
           "CC0 (drawn by packs/menus_packs.py from a fixed seed; made-up restaurants)",
           "Computer-made by the kit's makers (packs/menus_packs.py)", "permissive", 2000, 25, prepare_pack,
           "about 350 MB"),
]

MENUS_PICTURE_MAKING_OK = {"synthetic_menus"}

MENUS_NOT_INCLUDED = {
    "menus.nypl.org (the project's own site)": "retired (it now forwards to the library's research page); the data "
        "comes from the library's published data dump on Amazon S3 instead, and the pictures from images.nypl.org.",
    "NYPL menus dated 1931 or later, or with no date": "left out unless the library's Digital Collections API (with "
        "the free NYPL_API_TOKEN, kept outside this repository) says No Known U.S. Copyright Restrictions or CC0: "
        "later menus may still be in copyright.",
    "Restaurant menu photos from review and delivery sites": "the restaurants' and photographers' copyright, and the "
        "sites' terms forbid copying; not used.",
    "Open Images 'Menu' label": "already asked by open_images_cards_documents (which says only that it is a menu).",
}
